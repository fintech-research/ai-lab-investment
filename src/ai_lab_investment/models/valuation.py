"""Valuation analysis for AI infrastructure firms.

Decomposes firm value into:
1. Assets-in-place: value of existing capacity at current demand
2. Expansion option: value of the option to invest in new capacity
3. Regime switch option: additional value from potential L->H transition

Computes credit risk metrics (default probability, credit spread) and
quantifies the "Dario dilemma" — the cost of belief mismatches between
a firm's true lambda and its investment strategy.
"""

from typing import Any

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
    ) -> dict[str, Any]:
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

        # The option value already embeds the regime-switch component, so
        # the expansion option is the residual after both assets-in-place
        # and the regime-switch value (avoids double counting in the total).
        expansion_option = max(option_val - assets - regime_switch, 0.0)
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

    # Fixed demand level for credit risk evaluation.
    # Using a fixed level (rather than a multiple of X_D) ensures consistent
    # distance-to-default comparisons across leverage levels.
    CREDIT_RISK_DEMAND_LEVEL = 0.10

    def credit_spread(
        self,
        leverage: float,
        K: float = 1.0,
        phi: float = 0.5,
        regime: str = "L",
        risk_free_rate: float | None = None,
    ) -> float:
        """Compute credit spread for a levered firm.

        Credit spread = yield on risky debt - benchmark yield.
        yield = coupon / debt_value.

        The benchmark is the model's discount rate r: all claims are
        valued by discounting at r, so a default-free perpetuity with
        coupon c_D is worth c_D / r and yields exactly r. The spread is
        therefore zero when default risk is absent and measures only the
        default-risk component.

        Args:
            leverage: Debt-to-investment ratio.
            K: Capacity level.
            phi: Training fraction (default 0.5).
            regime: Demand regime (unused; debt is an L-regime claim).
            risk_free_rate: Benchmark rate (defaults to the model's r).

        Returns:
            Credit spread in absolute terms (e.g., 0.02 = 200 bps).
        """
        if leverage <= 0:
            return 0.0

        if risk_free_rate is None:
            risk_free_rate = self.params.r

        duo = DuopolyModel(
            self.params,
            leverage=leverage,
            coupon_rate=0.05,
            bankruptcy_cost=0.30,
        )

        X = self.CREDIT_RISK_DEMAND_LEVEL

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
        regime: str = "L",
        horizon: float = 5.0,
    ) -> float:
        """Approximate probability of default within horizon.

        Uses the first-passage probability that GBM hits the default
        boundary within the given time horizon. The default boundary
        X_D is an L-regime object (the firm defaults pre-switch), so the
        L-regime drift mu_L is the consistent choice and the default.
        The calculation abstracts from the regime switch itself: a
        switch to H before hitting X_D would effectively remove default
        risk, so the figure is an upper bound on the pre-switch hazard.

        Args:
            X_current: Current demand level.
            K: Capacity.
            leverage: Debt-to-investment ratio.
            phi: Training fraction (default 0.5).
            regime: Demand regime governing the drift (default "L").
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
        regime: str = "L",
    ) -> dict[str, np.ndarray]:
        """Compute credit spreads across leverage levels.

        Both spread and default probability are evaluated at a fixed
        demand level (CREDIT_RISK_DEMAND_LEVEL), ensuring consistent
        distance-to-default comparisons across leverage levels.
        """
        n = len(leverage_values)
        spreads = np.full(n, np.nan)
        default_probs = np.full(n, np.nan)

        for i, lev in enumerate(leverage_values):
            try:
                spreads[i] = self.credit_spread(lev, regime=regime)
                default_probs[i] = self.default_probability(
                    X_current=self.CREDIT_RISK_DEMAND_LEVEL,
                    K=1.0,
                    leverage=lev,
                    regime=regime,
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
    ) -> dict[str, Any]:
        """Quantify the cost of belief mismatches.

        Uses the phi-aware model where lambda enters through A_eff, so
        the optimal trigger X* and allocation phi* depend on lambda. The
        optimal capacity K* does *not*: by Proposition 1 it is
        independent of both lambda and phi, so belief mismatches distort
        timing and allocation only, never scale (and hence never the
        coupon, which is proportional to I(K*)).

        If a firm's true lambda (private belief) differs from the lambda
        it uses for investment decisions, what is the cost?

        - Conservative (lambda_invest < lambda_true): invests too late
          and under-allocates to training, forgoing H-regime upside
        - Aggressive (lambda_invest > lambda_true): invests too early
          and over-allocates to training, sacrificing L-regime revenue
          and raising default risk in bad states

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
    ) -> dict[str, Any]:
        """Quantify belief-mismatch cost with leverage (default risk).

        Uses total firm value (E + D) from the Leland structural model,
        so deadweight bankruptcy costs (b * V(X_D)) are captured. This
        shows how leverage amplifies the cost of overinvestment through
        endogenous default risk.

        Important: both the benchmark and the mismatched operating
        policies (X*, K*, phi*) come from the *unleveraged*
        SingleFirmModel at the respective lambda; the levered claims
        E + D - leverage * I are then valued under those policies. That
        is the intended experiment, not an oversight: leverage is
        exogenous in this model, so the firm sizes and times its
        investment on NPV grounds and debt is layered on top of the
        resulting policy.

        Consequence for the appendix argument: unlike the unleveraged
        dario_dilemma(), the objective returned here is NOT maximized at
        lambda_invest == lambda_true by construction, because the policy
        is not re-optimized against the levered objective. Numerically
        the gap is negligible -- at baseline with leverage 0.40 the
        levered objective peaks at lambda_invest ~ 0.101 and the value
        shortfall at lambda_true is ~1.3e-5 in relative terms -- so the
        second-order expansion in Internet Appendix A is stated exactly
        for the unleveraged case and used as an approximation here.
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
        # Use the full first-passage formula (consistent with default_probability())
        va_true = ValuationAnalysis(p_true)
        dp_optimal = va_true.default_probability(
            X_current=X_true,
            K=K_true,
            leverage=leverage,
            phi=phi_true,
            regime="L",
            horizon=5.0,
        )
        dp_mismatch = va_true.default_probability(
            X_current=X_invest,
            K=K_invest,
            leverage=leverage,
            phi=phi_invest,
            regime="L",
            horizon=5.0,
        )

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
    ) -> dict[str, Any]:
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

    def capacity_gap_decomposition(
        self,
        K_fracs: np.ndarray,
        demand_multiple: float = 1.5,
    ) -> dict[str, Any]:
        """Capacity-gap decomposition across installed-capacity levels.

        For each installed capacity K = frac * K*, computes assets-in-place
        (gross installed value at the optimal training fraction phi*) and
        the capacity gap value, defined as the shortfall of assets-in-place
        relative to the *net* value of the optimally sized greenfield
        project, NPV(K*, phi*) = V(X, phi*, K*) - I(K*), floored at zero.
        Because the benchmark nets out the full investment cost I(K*) while
        assets-in-place are gross of sunk costs, the gap reaches zero
        before K reaches K*. This is the comparative-statics measure of
        distance to optimal scale reported in the paper, not the NPV of
        incremental expansion from the installed base.

        Args:
            K_fracs: Installed capacity as fractions of optimal K*.
            demand_multiple: Demand evaluation point as a multiple of the
                optimal trigger X*.

        Returns:
            Dict with 'K_fracs', 'assets_in_place', 'capacity_gap',
            'gap_fraction' (percent), and scalars 'X_eval', 'K_star',
            'phi_star', 'npv_optimal'.
        """
        model = SingleFirmModel(self.params)
        X_star, K_star, phi_star = model.optimal_trigger_capacity_phi()
        X_eval = demand_multiple * X_star

        npv_optimal = model.installed_value_with_phi(
            X_eval, phi_star, K_star, "L"
        ) - model.investment_cost(K_star)

        assets = np.full_like(K_fracs, np.nan, dtype=float)
        gap = np.full_like(K_fracs, np.nan, dtype=float)
        for i, frac in enumerate(K_fracs):
            assets[i] = model.installed_value_with_phi(
                X_eval, phi_star, frac * K_star, "L"
            )
            gap[i] = max(npv_optimal - assets[i], 0.0)

        total = assets + gap
        gap_fraction = np.where(total > 0, gap / total * 100.0, 0.0)

        return {
            "K_fracs": K_fracs,
            "assets_in_place": assets,
            "capacity_gap": gap,
            "gap_fraction": gap_fraction,
            "X_eval": X_eval,
            "K_star": K_star,
            "phi_star": phi_star,
            "npv_optimal": npv_optimal,
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
    # Duopoly Dario dilemma (OF-6)
    # ------------------------------------------------------------------

    def dario_dilemma_duopoly(
        self,
        lambda_true: float,
        lambda_invest: float,
        leverage: float = 0.0,
    ) -> dict[str, Any]:
        """Dario's dilemma in a duopoly: one-sided belief mismatch.

        A well-calibrated rival follows its *single-firm* optimal policy
        (trigger, capacity, training fraction) under lambda_true; it does
        not re-optimize against the focal firm, so this is a tractable
        benchmark rather than the full preemption equilibrium. The focal
        firm plays the optimal single-firm strategy under lambda_invest,
        and the firm with the lower trigger leads. This captures the
        strategic penalty of wrong beliefs: a conservative firm cedes the
        leader position and the monopoly-phase rents.

        Returns dict with value losses for single-firm and duopoly
        benchmarks.
        """

        # --- rational rival's optimal policy under true lambda ---
        p_true = self.params.with_param(lam=lambda_true)
        model_true = SingleFirmModel(p_true)
        duo_true = DuopolyModel(
            p_true, leverage=leverage, coupon_rate=0.05, bankruptcy_cost=0.30
        )

        try:
            X_true, K_true, phi_true = model_true.optimal_trigger_capacity_phi()
        except (ValueError, RuntimeError):
            return {"error": "No solution at true lambda"}

        # --- focal firm's policy under mistaken belief ---
        p_invest = self.params.with_param(lam=lambda_invest)
        model_invest = SingleFirmModel(p_invest)
        try:
            X_inv, K_inv, phi_inv = model_invest.optimal_trigger_capacity_phi()
        except (ValueError, RuntimeError):
            return {"error": "No solution at invest lambda"}

        # --- single-firm benchmark (reuse existing method) ---
        sf = self.dario_dilemma(lambda_true, lambda_invest)

        # --- duopoly evaluation ---
        # Determine who leads. The firm with the lower trigger enters first.
        beta = p_true.beta_H

        if X_inv <= X_true:
            # Focal firm leads (invests first), rival follows
            # Leader value: monopoly until rival enters, then duopoly
            V_mono = duo_true.monopolist_value_L(X_inv, phi_inv, K_inv)
            if X_true > X_inv:
                # Rival enters at X_true; PV of revenue drop
                V_mono_XF = duo_true.monopolist_value_L(X_true, phi_inv, K_inv)
                V_duo_XF = duo_true.installed_value_L(
                    X_true, phi_inv, K_inv, phi_true, K_true
                )
                drop = V_mono_XF - V_duo_XF
                entry_factor = (X_inv / X_true) ** beta
                npv_focal = V_mono - drop * entry_factor
            else:
                # Simultaneous entry: immediate duopoly
                npv_focal = duo_true.installed_value_L(
                    X_inv, phi_inv, K_inv, phi_true, K_true
                )
            npv_focal -= duo_true.investment_cost(K_inv)
        else:
            # Rival leads, focal firm follows
            # Focal firm enters at X_inv into duopoly directly
            V_duo = duo_true.installed_value_L(X_inv, phi_inv, K_inv, phi_true, K_true)
            npv_focal = V_duo - duo_true.investment_cost(K_inv)

        # Optimal duopoly case: focal firm also plays correctly
        # Symmetric: both invest at the same trigger, immediate duopoly
        V_opt_duo = duo_true.installed_value_L(
            X_true, phi_true, K_true, phi_true, K_true
        )
        npv_optimal = V_opt_duo - duo_true.investment_cost(K_true)

        # Timing discount to common X_0
        X_0 = min(X_true, X_inv) * 0.5
        if X_0 <= 0:
            X_0 = 1e-6

        ev_opt = npv_optimal * (X_0 / X_true) ** beta if npv_optimal > 0 else 0
        ev_focal = npv_focal * (X_0 / X_inv) ** beta if npv_focal > 0 else 0
        loss_duo = ev_opt - ev_focal
        loss_duo_pct = loss_duo / abs(ev_opt) if ev_opt != 0 else 0

        return {
            "lambda_true": lambda_true,
            "lambda_invest": lambda_invest,
            "value_loss_pct_single": sf.get("value_loss_pct", np.nan),
            "value_loss_pct_duopoly": loss_duo_pct,
            "ev_optimal_duopoly": ev_opt,
            "ev_mismatch_duopoly": ev_focal,
            "focal_leads": bool(X_inv <= X_true),
            "X_focal": X_inv,
            "X_rival": X_true,
            "phi_focal": phi_inv,
            "phi_rival": phi_true,
        }

    # ------------------------------------------------------------------
    # Two-period dynamic phi illustration (OF-3)
    # ------------------------------------------------------------------

    def two_period_dynamic_phi(
        self,
        lambda_val: float | None = None,
        dt: float = 1.0,
        adjustment_cost: float = 0.0,
    ) -> dict[str, Any]:
        """Two-period illustration of dynamic training reallocation.

        Period 1: firm invests with phi_1.
        Period 2: if regime switched (prob p_switch), firm uses phi_H.
                  if no switch (prob 1 - p_switch), firm uses phi_L2.
        Reallocation costs kappa * (delta_phi)^2 per reallocation event.

        Args:
            lambda_val: Arrival rate (defaults to params.lam).
            dt: Period length in years.
            adjustment_cost: Quadratic reallocation cost kappa.

        Returns:
            Dict comparing static and dynamic allocations.
        """
        from scipy import optimize as sp_opt

        p = self.params
        lam = lambda_val if lambda_val is not None else p.lam

        # Probability of switch in period 1
        p_switch = 1.0 - np.exp(-lam * dt)
        disc_1 = np.exp(-p.r * dt)

        # Static benchmark
        p_lam = p.with_param(lam=lam)
        model_static = SingleFirmModel(p_lam)
        _, K_s, phi_s = model_static.optimal_trigger_capacity_phi()

        kappa = adjustment_cost

        def _period_value(phi_1: float, phi_H: float, phi_L2: float) -> float:
            """Expected PV of two-period revenue (per unit X, at K_s)."""
            K = K_s

            # Period 1: L-regime revenue (inference + H-option from training).
            # Reuses the model's effective revenue coefficient (eq-a-eff).
            a_eff_1 = model_static._effective_revenue_coeff_single(phi_1, K)

            # PV from period 1 flows: effective coefficient times the
            # fraction of the perpetuity earned over [0, dt]
            pv_1 = a_eff_1 * (1.0 - np.exp(-(p.r - p.mu_L + lam) * dt))

            # Period 2 outcomes:
            # If switch: H-regime revenue with phi_H
            rev_2_H = (phi_H * K) ** p.alpha * p.A_H

            # If no switch: L-regime with phi_L2
            rev_2_L = model_static._effective_revenue_coeff_single(phi_L2, K)

            pv_2 = disc_1 * (p_switch * rev_2_H + (1.0 - p_switch) * rev_2_L)

            # Adjustment costs (expected)
            adj = kappa * (
                p_switch * (phi_H - phi_1) ** 2
                + (1.0 - p_switch) * (phi_L2 - phi_1) ** 2
            )

            return pv_1 + pv_2 - adj

        def _neg_value(params_vec: np.ndarray) -> float:
            phi_1, phi_H, phi_L2 = params_vec
            if (
                phi_1 <= 0.01
                or phi_1 >= 0.99
                or phi_H <= 0.01
                or phi_H >= 0.99
                or phi_L2 <= 0.01
                or phi_L2 >= 0.99
            ):
                return 1e20
            return -_period_value(phi_1, phi_H, phi_L2)

        # Optimize
        best_val = 1e20
        best_params = None
        for p1 in [0.3, 0.5, 0.7]:
            for pH in [0.5, 0.7, 0.9]:
                for pL in [0.2, 0.4, 0.6]:
                    x0 = np.array([p1, pH, pL])
                    try:
                        result = sp_opt.minimize(
                            _neg_value,
                            x0,
                            method="Nelder-Mead",
                            options={"maxiter": 2000, "xatol": 1e-8},
                        )
                        if result.fun < best_val:
                            best_val = result.fun
                            best_params = result.x
                    except (ValueError, RuntimeError):
                        continue

        if best_params is None:
            return {"error": "Dynamic phi optimization failed"}

        phi_1_opt = np.clip(best_params[0], 0.01, 0.99)
        phi_H_opt = np.clip(best_params[1], 0.01, 0.99)
        phi_L2_opt = np.clip(best_params[2], 0.01, 0.99)

        # Compute effective A_eff for the dynamic allocation
        val_dynamic = _period_value(phi_1_opt, phi_H_opt, phi_L2_opt)
        val_static = _period_value(phi_s, phi_s, phi_s)

        # Faith-based survival threshold under dynamic phi
        R = ((p.r - p.mu_H) / (p.r - p.mu_L)) ** (1.0 / p.alpha)
        phi_underbar = R / (1.0 + R)

        return {
            "phi_static": phi_s,
            "phi_1_dynamic": phi_1_opt,
            "phi_H_dynamic": phi_H_opt,
            "phi_L2_dynamic": phi_L2_opt,
            "phi_underbar": phi_underbar,
            "value_dynamic": val_dynamic,
            "value_static": val_static,
            "value_gain_pct": (val_dynamic - val_static) / abs(val_static) * 100
            if val_static != 0
            else 0,
            "p_switch": p_switch,
            "adjustment_cost": kappa,
            "phi_1_below_static": phi_1_opt < phi_s,
        }

    # ------------------------------------------------------------------
    # Fixed-pie contest robustness (OF-4)
    # ------------------------------------------------------------------

    def fixed_pie_robustness(
        self,
        leverage: float = 0.0,
    ) -> dict[str, Any]:
        """Compare Tullock vs fixed-pie contest equilibrium objects.

        Solves the duopoly under both the standard Tullock contest and
        the fixed-pie variant (no revenue expansion), and reports key
        equilibrium quantities for comparison.
        """
        p = self.params

        # --- Standard Tullock ---
        duo_tullock = DuopolyModel(
            p, leverage=leverage, coupon_rate=0.05, bankruptcy_cost=0.30
        )
        try:
            eq_tullock = duo_tullock.solve_preemption_equilibrium()
        except (ValueError, RuntimeError):
            return {"error": "Tullock equilibrium failed"}

        # Faith-based survival threshold (A_eff-channel, eq-phi-underbar)
        phi_underbar = duo_tullock.faith_threshold()

        # Dario dilemma asymmetry ratio under Tullock
        dd_cons = self.dario_dilemma(0.10, 0.02)
        dd_aggr = self.dario_dilemma(0.10, 0.20)
        loss_cons = dd_cons.get("value_loss_pct", np.nan)
        loss_aggr = dd_aggr.get("value_loss_pct", np.nan)
        asym_tullock = abs(loss_cons / loss_aggr) if loss_aggr != 0 else np.nan

        # --- Fixed-pie contest ---
        duo_fp = DuopolyModel(
            p,
            leverage=leverage,
            coupon_rate=0.05,
            bankruptcy_cost=0.30,
            contest="fixed_pie",
        )

        try:
            eq_fp = duo_fp.solve_preemption_equilibrium()
        except (ValueError, RuntimeError):
            eq_fp = None

        # Dario's dilemma under fixed-pie is computed using single-firm
        # (contest spec doesn't affect the single-firm dilemma, so the
        # asymmetry ratio is the same)

        result = {
            # Tullock results
            "tullock_phi_F": eq_tullock["phi_follower"],
            "tullock_X_F": eq_tullock["X_follower"],
            "tullock_K_F": eq_tullock["K_follower"],
            "tullock_X_P": eq_tullock["X_leader"],
            "tullock_phi_underbar": phi_underbar,
            "tullock_asym_ratio": asym_tullock,
            "tullock_preemption_discount": (
                eq_tullock["X_leader"] / eq_tullock["X_leader_monopolist"]
            ),
        }

        if eq_fp is not None:
            result.update({
                "fixedpie_phi_F": eq_fp["phi_follower"],
                "fixedpie_X_F": eq_fp["X_follower"],
                "fixedpie_K_F": eq_fp["K_follower"],
                "fixedpie_X_P": eq_fp["X_leader"],
                "fixedpie_preemption_discount": (
                    eq_fp["X_leader"] / eq_fp["X_leader_monopolist"]
                ),
            })
        else:
            result["fixedpie_error"] = "Fixed-pie equilibrium failed"

        return result

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
            # Credit metrics are L-regime objects regardless of the
            # regime used for the value decomposition above.
            spread = self.credit_spread(lev, regime="L")
            prob = self.default_probability(X, 1.0, lev, regime="L")
            result["credit"][f"leverage_{lev}"] = {
                "spread_bps": spread * 10000,
                "default_prob_5yr": prob,
            }

        # Dario dilemma example
        result["dario_dilemma"] = self.dario_dilemma(lambda_true=0.3, lambda_invest=0.1)

        return result
