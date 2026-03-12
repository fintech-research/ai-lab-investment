"""Valuation analysis for AI infrastructure firms.

Decomposes firm value into:
1. Assets-in-place: value of existing capacity at current demand
2. Expansion option: value of the option to invest in new capacity
3. Regime switch option: additional value from potential L->H transition

Computes credit risk metrics (default probability, credit spread) and
quantifies the "Dario dilemma" — the cost of belief mismatches between
a firm's true lambda and its investment strategy.
"""

import numpy as np

from .base_model import SingleFirmModel
from .duopoly import DuopolyModel
from .parameters import ModelParameters


class ValuationAnalysis:
    """Comprehensive valuation analysis for AI infrastructure firms.

    Brings together the single-firm, duopoly, and calibration models
    to produce firm valuations, growth option decompositions, credit
    risk metrics, and scenario analyses.
    """

    def __init__(self, params: ModelParameters):
        self.params = params
        self._cache: dict = {}

    # ------------------------------------------------------------------
    # Growth option decomposition
    # ------------------------------------------------------------------

    def growth_option_decomposition(
        self,
        X: float,
        K_installed: float,
        regime: str = "H",
    ) -> dict[str, float]:
        """Decompose firm value into components.

        Args:
            X: Current demand level.
            K_installed: Currently installed capacity (0 if pre-investment).
            regime: Current demand regime.

        Returns:
            Dict with:
            - total_value: Total firm value
            - assets_in_place: Value of installed capacity
            - expansion_option: Value of option to expand
            - regime_switch_value: Additional value from regime switching
        """
        model = SingleFirmModel(self.params)

        # Assets-in-place
        if K_installed > 0:
            assets = model.installed_value(X, K_installed, regime)
        else:
            assets = 0.0

        # Total option value (includes expansion option)
        option_val = model.option_value(X, regime)

        # Regime switch value: difference between L and H option values
        if regime == "L":
            F_L = model.option_value_L(X)
            # Value in L without switching (pure L parameters)
            params_no_switch = self.params.with_param(lam=1e-10)
            model_no_switch = SingleFirmModel(params_no_switch)
            try:
                F_L_no_switch = model_no_switch.option_value(X, "L")
            except (ValueError, RuntimeError):
                F_L_no_switch = 0.0
            regime_switch = F_L - F_L_no_switch
        else:
            regime_switch = 0.0

        expansion_option = option_val - assets if option_val > assets else 0.0
        total = assets + expansion_option + regime_switch

        return {
            "total_value": total,
            "assets_in_place": assets,
            "expansion_option": expansion_option,
            "regime_switch_value": regime_switch,
            "assets_fraction": assets / total if total > 0 else 0.0,
            "growth_fraction": (expansion_option + regime_switch) / total
            if total > 0
            else 0.0,
        }

    # ------------------------------------------------------------------
    # Credit risk
    # ------------------------------------------------------------------

    def credit_spread(
        self,
        leverage: float,
        K: float = 1.0,
        phi: float = 0.5,
        regime: str = "H",
        risk_free_rate: float | None = None,
    ) -> float:
        """Compute credit spread for a levered firm.

        Credit spread = yield on risky debt - risk-free rate.
        yield = coupon / debt_value.

        Args:
            leverage: Debt-to-investment ratio.
            K: Capacity level.
            phi: Training fraction (default 0.5).
            regime: Demand regime.
            risk_free_rate: Risk-free rate (defaults to r - 0.03).

        Returns:
            Credit spread in absolute terms (e.g., 0.02 = 200 bps).
        """
        if leverage <= 0:
            return 0.0

        if risk_free_rate is None:
            risk_free_rate = max(self.params.r - 0.03, 0.01)

        duo = DuopolyModel(
            self.params,
            leverage=leverage,
            coupon_rate=0.05,
            bankruptcy_cost=0.30,
        )

        # Compute at a demand level above the default boundary
        X_D = duo.default_boundary(phi, K, 0.0, 0.0)
        X = max(X_D * 3, 0.1)

        coupon = duo.coupon_payment(K)
        D = duo.debt_value(X, phi, K, 0.0, 0.0)

        if D <= 0 or coupon <= 0:
            return 0.0

        yield_risky = coupon / D
        spread = yield_risky - risk_free_rate
        return max(spread, 0.0)

    def default_probability(
        self,
        X_current: float,
        K: float,
        leverage: float,
        phi: float = 0.5,
        regime: str = "H",
        horizon: float = 5.0,
    ) -> float:
        """Approximate probability of default within horizon.

        Uses the probability that GBM hits the default boundary
        within the given time horizon.

        P(default in T) approx= N(-d2) where d2 is from Black-Scholes.

        Args:
            X_current: Current demand level.
            K: Capacity.
            leverage: Debt-to-investment ratio.
            phi: Training fraction (default 0.5).
            regime: Demand regime.
            horizon: Time horizon in years.

        Returns:
            Probability of default [0, 1].
        """
        if leverage <= 0:
            return 0.0

        duo = DuopolyModel(
            self.params,
            leverage=leverage,
            coupon_rate=0.05,
            bankruptcy_cost=0.30,
        )
        X_D = duo.default_boundary(phi, K, 0.0, 0.0)
        if X_D <= 0 or X_current <= X_D:
            return 1.0 if X_D > 0 else 0.0

        if horizon <= 0:
            return 0.0

        p = self.params
        mu = p.mu_H if regime == "H" else p.mu_L
        sigma = p.sigma

        # First-passage (barrier) probability for GBM hitting X_D
        # P(min_{0<=t<=T} X_t <= X_D) = N(-d1) + (X_D/X)^{2nu/sigma^2} N(-d2)
        # where nu = mu - sigma^2/2, d1 = [ln(X/X_D) + nu*T]/(sigma*sqrt(T)),
        # d2 = [ln(X/X_D) - nu*T]/(sigma*sqrt(T))
        from scipy.stats import norm

        nu = mu - 0.5 * sigma**2
        sqrt_T = sigma * np.sqrt(horizon)
        log_ratio = np.log(X_current / X_D)

        d1 = (log_ratio + nu * horizon) / sqrt_T
        d2 = (log_ratio - nu * horizon) / sqrt_T

        prob = norm.cdf(-d1)
        if sigma > 0:
            prob += (X_D / X_current) ** (2 * nu / sigma**2) * norm.cdf(-d2)

        return float(np.clip(prob, 0.0, 1.0))

    def credit_spread_curve(
        self,
        leverage_values: np.ndarray,
        regime: str = "H",
    ) -> dict[str, np.ndarray]:
        """Compute credit spreads across leverage levels.

        Default probability is evaluated at the same demand level used
        for credit spread computation (3x the default boundary at each
        leverage level). This produces leverage-varying default risk.
        """
        n = len(leverage_values)
        spreads = np.full(n, np.nan)
        default_probs = np.full(n, np.nan)

        for i, lev in enumerate(leverage_values):
            try:
                spreads[i] = self.credit_spread(lev, regime=regime)
                # Use the same X evaluation as credit_spread (3x X_D)
                duo = DuopolyModel(
                    self.params,
                    leverage=lev,
                    coupon_rate=0.05,
                    bankruptcy_cost=0.30,
                )
                X_D = duo.default_boundary(0.5, 1.0, 0.0, 0.0)
                X_current = max(X_D * 3, 0.1)
                default_probs[i] = self.default_probability(
                    X_current=X_current, K=1.0, leverage=lev, regime=regime
                )
            except (ValueError, RuntimeError):
                continue

        return {
            "leverage": leverage_values,
            "credit_spread": spreads,
            "default_probability": default_probs,
        }

    # ------------------------------------------------------------------
    # Dario dilemma
    # ------------------------------------------------------------------

    def dario_dilemma(
        self,
        lambda_true: float,
        lambda_invest: float,
    ) -> dict[str, float]:
        """Quantify the cost of belief mismatches.

        Uses the phi-aware model where lambda enters through A_eff,
        so the optimal (X*, K*, phi*) all depend on lambda.

        If a firm's true lambda (private belief) differs from the lambda
        it uses for investment decisions, what is the cost?

        - Conservative (lambda_invest < lambda_true): invests too late,
          misses revenue during the boom
        - Aggressive (lambda_invest > lambda_true): invests too early
          and too much, risk of default in bad states

        Args:
            lambda_true: True arrival rate (private belief).
            lambda_invest: Arrival rate used for investment decisions.

        Returns:
            Dict with value under each scenario.
        """
        # Optimal investment under true lambda
        p_true = self.params.with_param(lam=lambda_true)
        model_true = SingleFirmModel(p_true)
        try:
            X_true, K_true, phi_true = model_true.optimal_trigger_capacity_phi()
            V_optimal = model_true.installed_value_with_phi(
                X_true, phi_true, K_true, "L"
            )
            I_optimal = model_true.investment_cost(K_true)
            npv_optimal = V_optimal - I_optimal
        except (ValueError, RuntimeError):
            return {"error": "No solution at true lambda"}

        # Investment under mismatched lambda
        p_invest = self.params.with_param(lam=lambda_invest)
        model_invest = SingleFirmModel(p_invest)
        try:
            X_invest, K_invest, phi_invest = model_invest.optimal_trigger_capacity_phi()
            # Evaluate this investment under the TRUE demand process
            # (true A_eff) but with the mismatched (K, phi) policy.
            V_mismatch = model_true.installed_value_with_phi(
                X_invest, phi_invest, K_invest, "L"
            )
            I_mismatch = model_true.investment_cost(K_invest)
            npv_mismatch = V_mismatch - I_mismatch
        except (ValueError, RuntimeError):
            return {"error": "No solution at invest lambda"}

        # Include timing discount: the option value at a common reference
        # demand X_0 is NPV(X*) * (X_0 / X*)^beta_H. This accounts for
        # the different waiting times (higher trigger = longer wait).
        beta = p_true.beta_H
        # Use a reference X_0 below both triggers
        X_0 = min(X_true, X_invest) * 0.5
        if X_0 <= 0:
            X_0 = 1e-6

        ev_optimal = npv_optimal * (X_0 / X_true) ** beta if npv_optimal > 0 else 0
        ev_mismatch = npv_mismatch * (X_0 / X_invest) ** beta if npv_mismatch > 0 else 0
        value_loss = ev_optimal - ev_mismatch
        value_loss_pct = value_loss / abs(ev_optimal) if ev_optimal != 0 else 0

        return {
            "lambda_true": lambda_true,
            "lambda_invest": lambda_invest,
            "X_optimal": X_true,
            "K_optimal": K_true,
            "phi_optimal": phi_true,
            "npv_optimal": npv_optimal,
            "X_mismatch": X_invest,
            "K_mismatch": K_invest,
            "phi_mismatch": phi_invest,
            "npv_mismatch": npv_mismatch,
            "ev_optimal": ev_optimal,
            "ev_mismatch": ev_mismatch,
            "value_loss": value_loss,
            "value_loss_pct": value_loss_pct,
            "is_conservative": lambda_invest < lambda_true,
        }

    def dario_dilemma_leveraged(
        self,
        lambda_true: float,
        lambda_invest: float,
        leverage: float = 0.40,
    ) -> dict[str, float]:
        """Quantify belief-mismatch cost with leverage (default risk).

        Uses total firm value (E + D) from the Leland structural model,
        so deadweight bankruptcy costs (b * V(X_D)) are captured. This
        shows how leverage amplifies the cost of overinvestment through
        endogenous default risk.
        """
        # Optimal policy under true lambda
        p_true = self.params.with_param(lam=lambda_true)
        model_true = SingleFirmModel(p_true)
        duo_true = DuopolyModel(
            p_true, leverage=leverage, coupon_rate=0.05, bankruptcy_cost=0.30
        )
        try:
            X_true, K_true, phi_true = model_true.optimal_trigger_capacity_phi()
            eq_opt = duo_true.equity_value(X_true, phi_true, K_true, 0.0, 0.0, leverage)
            debt_opt = duo_true.debt_value(X_true, phi_true, K_true, 0.0, 0.0, leverage)
            I_opt = duo_true.investment_cost(K_true)
            # Total NPV = E + D - lev*I = (V - (1-lev)*I - BC) + D - lev*I
            npv_optimal = eq_opt + debt_opt - leverage * I_opt
        except (ValueError, RuntimeError):
            return {"error": "No solution at true lambda"}

        # Investment under mismatched lambda
        p_invest = self.params.with_param(lam=lambda_invest)
        model_invest = SingleFirmModel(p_invest)
        try:
            X_invest, K_invest, phi_invest = model_invest.optimal_trigger_capacity_phi()
            eq_mis = duo_true.equity_value(
                X_invest, phi_invest, K_invest, 0.0, 0.0, leverage
            )
            debt_mis = duo_true.debt_value(
                X_invest, phi_invest, K_invest, 0.0, 0.0, leverage
            )
            I_mis = duo_true.investment_cost(K_invest)
            npv_mismatch = eq_mis + debt_mis - leverage * I_mis
        except (ValueError, RuntimeError):
            return {"error": "No solution at invest lambda"}

        # Timing discount
        beta = p_true.beta_H
        X_0 = min(X_true, X_invest) * 0.5
        if X_0 <= 0:
            X_0 = 1e-6

        ev_optimal = npv_optimal * (X_0 / X_true) ** beta if npv_optimal > 0 else 0
        ev_mismatch = npv_mismatch * (X_0 / X_invest) ** beta if npv_mismatch > 0 else 0
        value_loss = ev_optimal - ev_mismatch
        value_loss_pct = value_loss / abs(ev_optimal) if ev_optimal != 0 else 0

        # Conditional default probabilities under true dynamics
        from scipy.stats import norm as _norm

        def _default_prob(X_entry, K, phi, horizon=5.0):
            X_D = duo_true.default_boundary(phi, K, 0.0, 0.0)
            if X_D <= 0 or X_entry <= X_D:
                return 1.0 if X_D > 0 else 0.0
            d2 = (
                np.log(X_entry / X_D) + (p_true.mu_L - 0.5 * p_true.sigma**2) * horizon
            ) / (p_true.sigma * np.sqrt(horizon))
            return float(_norm.cdf(-d2))

        dp_optimal = _default_prob(X_true, K_true, phi_true)
        dp_mismatch = _default_prob(X_invest, K_invest, phi_invest)

        return {
            "lambda_true": lambda_true,
            "lambda_invest": lambda_invest,
            "leverage": leverage,
            "ev_optimal": ev_optimal,
            "ev_mismatch": ev_mismatch,
            "value_loss": value_loss,
            "value_loss_pct": value_loss_pct,
            "default_prob_optimal": dp_optimal,
            "default_prob_mismatch": dp_mismatch,
            "is_conservative": lambda_invest < lambda_true,
        }

    def dario_dilemma_surface(
        self,
        lambda_true_range: np.ndarray,
        lambda_invest_range: np.ndarray,
    ) -> dict[str, np.ndarray]:
        """Compute value loss for a grid of (true, invest) lambda pairs."""
        n_t = len(lambda_true_range)
        n_i = len(lambda_invest_range)
        value_loss = np.full((n_t, n_i), np.nan)

        for i, lt in enumerate(lambda_true_range):
            for j, li in enumerate(lambda_invest_range):
                result = self.dario_dilemma(lt, li)
                if "value_loss_pct" in result:
                    value_loss[i, j] = result["value_loss_pct"]

        return {
            "lambda_true": lambda_true_range,
            "lambda_invest": lambda_invest_range,
            "value_loss_pct": value_loss,
        }

    # ------------------------------------------------------------------
    # Equity valuation vs lambda
    # ------------------------------------------------------------------

    def equity_value_vs_lambda(
        self,
        lambda_values: np.ndarray,
        X: float = 1.0,
        regime: str = "H",
    ) -> dict[str, np.ndarray]:
        """Compute equity value across lambda values.

        Shows sensitivity of valuation to AI timeline beliefs.
        """
        n = len(lambda_values)
        option_values = np.full(n, np.nan)
        triggers = np.full(n, np.nan)
        capacities = np.full(n, np.nan)

        for i, lam in enumerate(lambda_values):
            try:
                p = self.params.with_param(lam=lam)
                model = SingleFirmModel(p)
                option_values[i] = model.option_value(X, regime)
                X_star, K_star = model.optimal_trigger_and_capacity(regime)
                triggers[i] = X_star
                capacities[i] = K_star
            except (ValueError, RuntimeError):
                continue

        return {
            "lambda_values": lambda_values,
            "option_values": option_values,
            "triggers": triggers,
            "capacities": capacities,
        }

    # ------------------------------------------------------------------
    # Phi-aware valuation
    # ------------------------------------------------------------------

    def growth_option_decomposition_with_phi(
        self,
        X: float,
        K_installed: float = 0.0,
        phi: float = 0.5,
    ) -> dict[str, float]:
        """Decompose firm value using the phi-aware model.

        Uses the combined L+H revenue structure where phi determines
        the split between inference revenue and training value.

        Args:
            X: Current demand level.
            K_installed: Currently installed capacity (0 if pre-investment).
            phi: Training fraction.

        Returns:
            Dict with value components.
        """
        model = SingleFirmModel(self.params)

        # Assets-in-place with phi
        if K_installed > 0:
            assets = model.installed_value_with_phi(X, phi, K_installed, "L")
        else:
            assets = 0.0

        # Option value with phi optimization
        option_val = model.option_value_with_phi(X)

        # Decompose: option includes optimal (K*, phi*)
        X_star, K_star, phi_star = model.optimal_trigger_capacity_phi()

        expansion_option = option_val - assets if option_val > assets else 0.0
        total = assets + expansion_option

        return {
            "total_value": total,
            "assets_in_place": assets,
            "expansion_option": expansion_option,
            "assets_fraction": assets / total if total > 0 else 0.0,
            "growth_fraction": expansion_option / total if total > 0 else 0.0,
            "phi_installed": phi,
            "phi_optimal": phi_star,
            "K_optimal": K_star,
            "X_trigger": X_star,
        }

    def equity_value_vs_lambda_with_phi(
        self,
        lambda_values: np.ndarray,
        X: float = 1.0,
    ) -> dict[str, np.ndarray]:
        """Equity value and optimal phi across lambda values.

        Shows how both valuation and training allocation respond to
        different beliefs about AI timelines.
        """
        n = len(lambda_values)
        option_values = np.full(n, np.nan)
        triggers = np.full(n, np.nan)
        capacities = np.full(n, np.nan)
        phis = np.full(n, np.nan)

        for i, lam in enumerate(lambda_values):
            try:
                p = self.params.with_param(lam=lam)
                model = SingleFirmModel(p)
                option_values[i] = model.option_value_with_phi(X)
                X_star, K_star, phi_star = model.optimal_trigger_capacity_phi()
                triggers[i] = X_star
                capacities[i] = K_star
                phis[i] = phi_star
            except (ValueError, RuntimeError):
                continue

        return {
            "lambda_values": lambda_values,
            "option_values": option_values,
            "triggers": triggers,
            "capacities": capacities,
            "phis": phis,
        }

    # ------------------------------------------------------------------
    # Summary
    # ------------------------------------------------------------------

    def summary(self, X: float = 1.0, regime: str = "H") -> dict:
        """Comprehensive valuation summary."""
        result = {}

        # Growth option decomposition
        result["decomposition"] = self.growth_option_decomposition(
            X, K_installed=0.0, regime=regime
        )

        # Credit risk at different leverage levels
        leverages = [0.0, 0.2, 0.4, 0.6]
        result["credit"] = {}
        for lev in leverages:
            spread = self.credit_spread(lev, regime=regime)
            prob = self.default_probability(X, 1.0, lev, regime=regime)
            result["credit"][f"leverage_{lev}"] = {
                "spread_bps": spread * 10000,
                "default_prob_5yr": prob,
            }

        # Dario dilemma example
        result["dario_dilemma"] = self.dario_dilemma(lambda_true=0.3, lambda_invest=0.1)

        return result
