"""Duopoly investment model with default risk and regime switching.

Solves for the Markov-perfect equilibrium of a preemption game between two
symmetric firms under:
- Regime-switching GBM demand (as in the base model)
- Contest-function revenue sharing: pi_i = X * K_i^alpha / (K_i^alpha + K_j^alpha)
- Endogenous default boundary (Leland 1994)
- Preemption equilibrium (Huisman & Kort 2015)

The three-way interaction (competition x leverage x default) is the paper's
main mechanism:
1. Competition pushes investment earlier (preemption effect)
2. Limited liability pushes capacity larger (risk-shifting effect)
3. Default risk creates a countervailing force (bankruptcy cost)

Solution approach:
1. Solve follower's problem (single-firm with competitor present)
2. Solve leader's problem given follower's best response
3. Find preemption equilibrium where value of leading = value of following
"""

import numpy as np
from scipy import optimize

from .parameters import ModelParameters


class DuopolyModel:
    """Duopoly investment game with default risk and regime switching.

    Two symmetric firms hold options to invest irreversibly in capacity.
    Revenue is shared via a contest function. Each firm finances with
    equity and debt, with endogenous default.

    The equilibrium features a leader (invests first) and follower
    (invests second), with the leader's trigger pinned by preemption.
    """

    def __init__(
        self,
        params: ModelParameters,
        leverage: float = 0.0,
        coupon_rate: float = 0.05,
        bankruptcy_cost: float = 0.30,
    ):
        """Initialize the duopoly model.

        Args:
            params: Base model parameters.
            leverage: Debt-to-investment-cost ratio D/I(K). 0 = all equity.
            coupon_rate: Coupon rate on debt as fraction of face value.
            bankruptcy_cost: Fraction of firm value lost in default (alpha_bc).
        """
        self.params = params
        self.leverage = leverage
        self.coupon_rate = coupon_rate
        self.bankruptcy_cost = bankruptcy_cost
        self._cache: dict = {}

    # ------------------------------------------------------------------
    # Revenue with competition
    # ------------------------------------------------------------------

    def contest_share(self, K_i: float, K_j: float) -> float:
        """Contest function market share for firm i.

        share_i = K_i^alpha / (K_i^alpha + K_j^alpha)
        """
        alpha = self.params.alpha
        num = K_i**alpha
        denom = K_i**alpha + K_j**alpha
        if denom <= 0:
            return 0.5
        return num / denom

    def duopoly_revenue_pv(
        self, X: float, K_i: float, K_j: float, regime: str
    ) -> float:
        """Present value of flow revenue for firm i in the duopoly.

        V_i = A_s * X * K_i^alpha / (K_i^alpha + K_j^alpha) - delta * K_i / r

        Args:
            X: Current demand level.
            K_i: Own capacity.
            K_j: Competitor's capacity.
            regime: 'L' or 'H'.

        Returns:
            Present value of installed capacity in the duopoly.
        """
        p = self.params
        A = p.A_H if regime == "H" else p.A_L
        share = self.contest_share(K_i, K_j)
        return A * X * K_i**p.alpha * share - p.delta * K_i / p.r

    def monopolist_revenue_pv(self, X: float, K: float, regime: str) -> float:
        """Present value when the firm is the only investor (leader pre-follower).

        V_monopolist = A_s * X * K^alpha - delta * K / r
        Same as single-firm since share = 1 when no competitor.
        """
        p = self.params
        A = p.A_H if regime == "H" else p.A_L
        return A * X * K**p.alpha - p.delta * K / p.r

    def investment_cost(self, K: float) -> float:
        """Total investment cost I(K) = c * K^gamma."""
        return self.params.c * K**self.params.gamma

    # ------------------------------------------------------------------
    # Default boundary (Leland 1994)
    # ------------------------------------------------------------------

    def coupon_payment(self, K: float) -> float:
        """Annual coupon payment on debt.

        Debt face value = leverage * I(K).
        Coupon = coupon_rate * face_value.
        """
        if self.leverage <= 0:
            return 0.0
        face_value = self.leverage * self.investment_cost(K)
        return self.coupon_rate * face_value

    def default_boundary(self, K_i: float, K_j: float, regime: str) -> float:
        """Endogenous default boundary X_D (Leland 1994).

        Equity holders default when equity value = 0. The optimal default
        boundary equates the marginal cost of continuing (coupon - revenue)
        to the marginal benefit (option value of recovery).

        X_D = [beta_neg / (beta_neg - 1)] * [coupon / r] / [A * share * K^alpha]

        where beta_neg is the negative characteristic root, representing
        the elasticity of the put-like default option.

        Returns 0 if no debt (leverage = 0).
        """
        if self.leverage <= 0:
            return 0.0

        p = self.params
        c_D = self.coupon_payment(K_i)
        if c_D <= 0:
            return 0.0

        A = p.A_H if regime == "H" else p.A_L
        share = self.contest_share(K_i, K_j)
        revenue_coeff = A * K_i**p.alpha * share

        if revenue_coeff <= 0:
            return 0.0

        # Negative root of the characteristic equation
        beta_neg = self._negative_root(regime)

        # Leland default boundary
        X_D = (beta_neg / (beta_neg - 1.0)) * (c_D / p.r) / revenue_coeff

        return max(X_D, 0.0)

    def _negative_root(self, regime: str) -> float:
        """Negative root of the characteristic equation.

        Solves: (sigma^2/2) * beta * (beta - 1) + mu * beta - r = 0
        Returns the negative root (beta < 0).
        """
        p = self.params
        sigma = p.sigma_H if regime == "H" else p.sigma_L
        mu = p.mu_H if regime == "H" else p.mu_L
        a = 0.5 * sigma**2
        b = mu - 0.5 * sigma**2
        c = -p.r
        discriminant = b**2 - 4 * a * c
        return (-b - discriminant**0.5) / (2 * a)

    # ------------------------------------------------------------------
    # Equity and debt valuation with default
    # ------------------------------------------------------------------

    def equity_value(
        self,
        X: float,
        K_i: float,
        K_j: float,
        regime: str,
    ) -> float:
        """Equity value of firm i after investment, accounting for default.

        E(X) = V(X, K_i, K_j) - I(K_i) * (1 - leverage) - coupon/r
               + [coupon/r - V(X_D, K_i, K_j) + I(K_i)*(1-leverage)]
                 * (X/X_D)^beta_neg

        For X >= X_D. At X = X_D, equity = 0 by construction.
        Without debt, equity = V(X) - I(K).
        """
        p = self.params
        K_j_eff = K_j if K_j > 0 else 0.0

        if self.leverage <= 0:
            if K_j_eff > 0:
                return self.duopoly_revenue_pv(
                    X, K_i, K_j_eff, regime
                ) - self.investment_cost(K_i)
            return self.monopolist_revenue_pv(X, K_i, regime) - self.investment_cost(
                K_i
            )

        c_D = self.coupon_payment(K_i)
        I_K = self.investment_cost(K_i)
        equity_contribution = I_K * (1.0 - self.leverage)

        if K_j_eff > 0:
            V_X = self.duopoly_revenue_pv(X, K_i, K_j_eff, regime)
        else:
            V_X = self.monopolist_revenue_pv(X, K_i, regime)

        X_D = self.default_boundary(K_i, K_j_eff, regime)

        if X_D <= 0 or X <= X_D:
            # No default boundary or already in default
            return max(V_X - equity_contribution - c_D / p.r, 0.0)

        beta_neg = self._negative_root(regime)

        if K_j_eff > 0:
            V_XD = self.duopoly_revenue_pv(X_D, K_i, K_j_eff, regime)
        else:
            V_XD = self.monopolist_revenue_pv(X_D, K_i, regime)

        # Default option value (put-like)
        default_claim = c_D / p.r - V_XD + equity_contribution
        default_option = default_claim * (X / X_D) ** beta_neg

        equity = V_X - equity_contribution - c_D / p.r + default_option
        return max(equity, 0.0)

    def debt_value(
        self,
        X: float,
        K_i: float,
        K_j: float,
        regime: str,
    ) -> float:
        """Debt value accounting for default risk.

        D(X) = coupon/r - [coupon/r - (1 - alpha_bc) * V(X_D)] * (X/X_D)^beta_neg

        Without debt, returns 0.
        """
        if self.leverage <= 0:
            return 0.0

        p = self.params
        c_D = self.coupon_payment(K_i)
        K_j_eff = K_j if K_j > 0 else 0.0
        X_D = self.default_boundary(K_i, K_j_eff, regime)

        if X_D <= 0:
            return c_D / p.r

        beta_neg = self._negative_root(regime)

        if K_j_eff > 0:
            V_XD = self.duopoly_revenue_pv(X_D, K_i, K_j_eff, regime)
        else:
            V_XD = self.monopolist_revenue_pv(X_D, K_i, regime)

        recovery = (1.0 - self.bankruptcy_cost) * (V_XD + p.delta * K_i / p.r)
        default_loss = c_D / p.r - recovery
        debt = c_D / p.r - default_loss * (X / X_D) ** beta_neg
        return max(debt, 0.0)

    def firm_value(
        self,
        X: float,
        K_i: float,
        K_j: float,
        regime: str,
    ) -> float:
        """Total firm value = equity + debt."""
        return self.equity_value(X, K_i, K_j, regime) + self.debt_value(
            X, K_i, K_j, regime
        )

    # ------------------------------------------------------------------
    # Follower's problem
    # ------------------------------------------------------------------

    def _follower_npv(self, K_F: float, K_L: float, X: float, regime: str) -> float:
        """NPV of follower investing at demand X with capacity K_F.

        Given leader has already invested K_L.
        """
        return self.equity_value(X, K_F, K_L, regime)

    def _follower_objective(self, log_K: float, K_L: float, regime: str) -> float:
        """Negative log of follower's option value factor for K optimization.

        Maximizes h(K) = a(K)^beta / b(K)^(beta-1) where:
        - a(K) = A * K^alpha * share(K, K_L)
        - b(K) = delta*K/r + (1-leverage)*c*K^gamma + coupon/r
        """
        K_F = np.exp(log_K)
        p = self.params
        A = p.A_H if regime == "H" else p.A_L
        beta = p.beta_H if regime == "H" else p.beta_L

        share = self.contest_share(K_F, K_L)
        a = A * K_F**p.alpha * share

        c_D = self.coupon_payment(K_F)
        equity_cost = (1.0 - self.leverage) * self.investment_cost(K_F)
        b = p.delta * K_F / p.r + equity_cost + c_D / p.r

        if a <= 0 or b <= 0:
            return 1e20
        return -(beta * np.log(a) - (beta - 1.0) * np.log(b))

    def _follower_trigger(self, K_F: float, K_L: float, regime: str) -> float:
        """Optimal trigger X_F*(K) for given follower capacity.

        X_F* = [beta/(beta-1)] * [total cost] / [A * K^alpha * share]
        """
        p = self.params
        A = p.A_H if regime == "H" else p.A_L
        beta = p.beta_H if regime == "H" else p.beta_L

        share = self.contest_share(K_F, K_L)
        markup = beta / (beta - 1.0)

        c_D = self.coupon_payment(K_F)
        equity_cost = (1.0 - self.leverage) * self.investment_cost(K_F)
        total_cost = p.delta * K_F / p.r + equity_cost + c_D / p.r

        revenue_coeff = A * K_F**p.alpha * share
        if revenue_coeff <= 0:
            return np.inf

        return markup * total_cost / revenue_coeff

    def solve_follower(self, K_L: float, regime: str = "H") -> tuple[float, float]:
        """Solve follower's optimal investment problem.

        Given leader capacity K_L, find follower's optimal trigger and capacity.

        Args:
            K_L: Leader's installed capacity.
            regime: Demand regime.

        Returns:
            (X_F*, K_F*): Follower's optimal trigger and capacity.
        """
        cache_key = ("follower", K_L, regime)
        if cache_key in self._cache:
            return self._cache[cache_key]

        result = optimize.minimize_scalar(
            self._follower_objective,
            bounds=(-15, 15),
            method="bounded",
            args=(K_L, regime),
        )
        if result.fun >= 1e19:
            msg = f"Follower optimization failed for K_L={K_L:.4f}, regime={regime}"
            raise RuntimeError(msg)
        K_F = np.exp(result.x)
        X_F = self._follower_trigger(K_F, K_L, regime)

        self._cache[cache_key] = (X_F, K_F)
        return X_F, K_F

    # ------------------------------------------------------------------
    # Leader's problem
    # ------------------------------------------------------------------

    def _leader_value_at(self, X: float, K_L: float, regime: str) -> float:
        """Leader's equity value at demand X with capacity K_L.

        Before follower enters: leader is monopolist.
        After follower enters (X >= X_F*): duopoly revenue.

        The leader's value accounts for the follower's future entry:
        V_leader(X) = V_monopolist(X) - [V_monopolist(X_F) - V_duopoly(X_F)]
                      * (X/X_F)^beta

        This subtracts the expected present value of the revenue loss
        when the follower enters.
        """
        p = self.params
        X_F, K_F = self.solve_follower(K_L, regime)

        # Current value as monopolist
        V_mono = self.monopolist_revenue_pv(X, K_L, regime)

        if X >= X_F:
            # Follower has already entered — use duopoly revenue directly
            V_duo = self.duopoly_revenue_pv(X, K_L, K_F, regime)
            equity_cost = (1.0 - self.leverage) * self.investment_cost(K_L)
            c_D = self.coupon_payment(K_L)
            return max(V_duo - equity_cost - c_D / p.r, 0.0)

        # Follower hasn't entered yet. Leader is monopolist but anticipates entry.
        beta = p.beta_H if regime == "H" else p.beta_L

        V_mono_at_XF = self.monopolist_revenue_pv(X_F, K_L, regime)
        V_duo_at_XF = self.duopoly_revenue_pv(X_F, K_L, K_F, regime)

        # Revenue drop when follower enters
        revenue_drop = V_mono_at_XF - V_duo_at_XF

        # Expected PV of revenue loss (scaled by probability of reaching X_F)
        entry_factor = (X / X_F) ** beta if X_F > 0 and X < X_F else 1.0

        V_leader = V_mono - revenue_drop * entry_factor

        equity_cost = (1.0 - self.leverage) * self.investment_cost(K_L)
        c_D = self.coupon_payment(K_L)
        return max(V_leader - equity_cost - c_D / p.r, 0.0)

    def _leader_objective(self, log_K: float, regime: str) -> float:
        """Negative of leader's option value factor for K optimization.

        The leader's problem: choose K_L to maximize the option value,
        accounting for the follower's future entry.

        Uses a modified approach: optimize over K, where the trigger
        is computed from the leader's value function.
        """
        K_L = np.exp(log_K)
        p = self.params
        A = p.A_H if regime == "H" else p.A_L
        beta = p.beta_H if regime == "H" else p.beta_L

        # Revenue coefficient as monopolist
        a = A * K_L**p.alpha

        c_D = self.coupon_payment(K_L)
        equity_cost = (1.0 - self.leverage) * self.investment_cost(K_L)
        b = p.delta * K_L / p.r + equity_cost + c_D / p.r

        if a <= 0 or b <= 0:
            return 1e20
        return -(beta * np.log(a) - (beta - 1.0) * np.log(b))

    def _leader_trigger_monopolist(self, K_L: float, regime: str) -> float:
        """Leader's trigger assuming monopolist revenue (upper bound).

        X_L* = [beta/(beta-1)] * total_cost / [A * K^alpha]
        """
        p = self.params
        A = p.A_H if regime == "H" else p.A_L
        beta = p.beta_H if regime == "H" else p.beta_L

        markup = beta / (beta - 1.0)
        c_D = self.coupon_payment(K_L)
        equity_cost = (1.0 - self.leverage) * self.investment_cost(K_L)
        total_cost = p.delta * K_L / p.r + equity_cost + c_D / p.r

        revenue_coeff = A * K_L**p.alpha
        if revenue_coeff <= 0:
            return np.inf
        return markup * total_cost / revenue_coeff

    def solve_leader_monopolist(self, regime: str = "H") -> tuple[float, float]:
        """Solve leader's problem ignoring preemption (monopolist trigger).

        This gives the trigger the leader would choose if there were no
        threat of preemption. The actual leader's trigger is lower due
        to preemption pressure.

        Returns:
            (X_L_mono*, K_L*): Leader's monopolist trigger and capacity.
        """
        cache_key = ("leader_mono", regime)
        if cache_key in self._cache:
            return self._cache[cache_key]

        result = optimize.minimize_scalar(
            self._leader_objective,
            bounds=(-15, 15),
            method="bounded",
            args=(regime,),
        )
        if result.fun >= 1e19:
            msg = f"Leader optimization failed for regime={regime}"
            raise RuntimeError(msg)
        K_L = np.exp(result.x)
        X_L = self._leader_trigger_monopolist(K_L, regime)

        self._cache[cache_key] = (X_L, K_L)
        return X_L, K_L

    # ------------------------------------------------------------------
    # Preemption equilibrium
    # ------------------------------------------------------------------

    def follower_option_value(self, X: float, K_L: float, regime: str) -> float:
        """Value of the follower's option at demand X.

        F_follower(X) = B_F * X^beta   for X < X_F*
        F_follower(X) = NPV            for X >= X_F*
        """
        p = self.params
        X_F, K_F = self.solve_follower(K_L, regime)
        beta = p.beta_H if regime == "H" else p.beta_L

        if X >= X_F:
            return self._follower_npv(K_F, K_L, X, regime)

        # Compute B_F from value-matching at X_F
        npv_at_trigger = self._follower_npv(K_F, K_L, X_F, regime)
        if X_F <= 0:
            return 0.0
        B_F = npv_at_trigger / X_F**beta
        return B_F * X**beta

    def _preemption_gap(self, X: float, regime: str) -> float:
        """Gap between leader's value and follower's option value at X.

        At the preemption trigger X_P, the value of leading = value of
        waiting (follower's option). The leader invests at X_P where
        this gap first becomes non-negative from below.

        L(X) - F(X) where:
        - L(X) = leader's equity value from investing at X with optimal K
        - F(X) = follower's option value (waiting)
        """
        _, K_L = self.solve_leader_monopolist(regime)
        leader_val = self._leader_value_at(X, K_L, regime)
        follower_opt = self.follower_option_value(X, K_L, regime)
        return leader_val - follower_opt

    def solve_preemption_equilibrium(self, regime: str = "H") -> dict[str, float]:
        """Solve for the preemption equilibrium.

        Finds the leader's preemption trigger X_P where the value of
        leading first equals the value of following.

        Returns dict with:
            X_leader: Leader's investment trigger
            K_leader: Leader's capacity
            X_follower: Follower's investment trigger
            K_follower: Follower's capacity
            X_default_leader: Leader's default boundary (0 if no debt)
            X_default_follower: Follower's default boundary (0 if no debt)
        """
        cache_key = ("preemption", regime)
        if cache_key in self._cache:
            return self._cache[cache_key]

        X_L_mono, K_L = self.solve_leader_monopolist(regime)
        X_F, K_F = self.solve_follower(K_L, regime)

        # The preemption trigger is where L(X) = F(X) for the first time.
        # Search in [epsilon, X_L_mono] since preemption forces earlier entry.
        # At very low X, L(X) < 0 < F(X). At X_L_mono, L(X) > 0.

        # Find the preemption point by bisection
        X_low = X_L_mono * 0.001
        X_high = X_L_mono

        # Check if preemption actually occurs
        gap_low = self._preemption_gap(X_low, regime)
        gap_high = self._preemption_gap(X_high, regime)

        if gap_low >= 0:
            # Leader value exceeds follower even at very low X (edge case)
            X_P = X_low
        elif gap_high <= 0:
            # No preemption — leader invests at monopolist trigger
            X_P = X_L_mono
        else:
            # Find the crossing point
            try:
                result = optimize.brentq(
                    self._preemption_gap,
                    X_low,
                    X_high,
                    args=(regime,),
                    xtol=1e-10,
                )
                X_P = result
            except ValueError:
                # If Brent's method fails, use monopolist trigger
                X_P = X_L_mono

        # Compute default boundaries
        X_D_L = self.default_boundary(K_L, 0.0, regime)  # Leader pre-follower
        X_D_F = self.default_boundary(K_F, K_L, regime)

        result = {
            "X_leader": X_P,
            "K_leader": K_L,
            "X_follower": X_F,
            "K_follower": K_F,
            "X_default_leader": X_D_L,
            "X_default_follower": X_D_F,
            "X_leader_monopolist": X_L_mono,
        }
        self._cache[cache_key] = result
        return result

    # ------------------------------------------------------------------
    # Special cases for verification
    # ------------------------------------------------------------------

    def solve_no_competition(self, regime: str = "H") -> tuple[float, float]:
        """Solve the single-firm problem (no competitor).

        Used for verification: should match Phase 1 SingleFirmModel.
        """
        from .base_model import SingleFirmModel

        model = SingleFirmModel(self.params)
        return model.optimal_trigger_and_capacity(regime)

    # ------------------------------------------------------------------
    # Comparative statics
    # ------------------------------------------------------------------

    def comparative_statics(
        self,
        param_name: str,
        values: np.ndarray,
        regime: str = "H",
    ) -> dict[str, np.ndarray]:
        """Compute equilibrium outcomes over a range of parameter values.

        Returns dict with arrays for leader/follower triggers, capacities,
        and default boundaries.
        """
        n = len(values)
        results = {
            "param_values": values,
            "X_leader": np.full(n, np.nan),
            "K_leader": np.full(n, np.nan),
            "X_follower": np.full(n, np.nan),
            "K_follower": np.full(n, np.nan),
            "X_default_leader": np.full(n, np.nan),
            "X_default_follower": np.full(n, np.nan),
            "has_solution": np.zeros(n, dtype=bool),
        }

        for i, val in enumerate(values):
            try:
                p = self.params.with_param(**{param_name: val})
                m = DuopolyModel(
                    p,
                    leverage=self.leverage,
                    coupon_rate=self.coupon_rate,
                    bankruptcy_cost=self.bankruptcy_cost,
                )
                eq = m.solve_preemption_equilibrium(regime)
                results["X_leader"][i] = eq["X_leader"]
                results["K_leader"][i] = eq["K_leader"]
                results["X_follower"][i] = eq["X_follower"]
                results["K_follower"][i] = eq["K_follower"]
                results["X_default_leader"][i] = eq["X_default_leader"]
                results["X_default_follower"][i] = eq["X_default_follower"]
                results["has_solution"][i] = True
            except (ValueError, RuntimeError):
                continue

        return results

    def leverage_comparative_statics(
        self,
        leverage_values: np.ndarray,
        regime: str = "H",
    ) -> dict[str, np.ndarray]:
        """Compute equilibrium outcomes over a range of leverage levels."""
        n = len(leverage_values)
        results = {
            "leverage": leverage_values,
            "X_leader": np.full(n, np.nan),
            "K_leader": np.full(n, np.nan),
            "X_follower": np.full(n, np.nan),
            "K_follower": np.full(n, np.nan),
            "X_default_leader": np.full(n, np.nan),
            "X_default_follower": np.full(n, np.nan),
            "has_solution": np.zeros(n, dtype=bool),
        }

        for i, lev in enumerate(leverage_values):
            try:
                m = DuopolyModel(
                    self.params,
                    leverage=lev,
                    coupon_rate=self.coupon_rate,
                    bankruptcy_cost=self.bankruptcy_cost,
                )
                eq = m.solve_preemption_equilibrium(regime)
                results["X_leader"][i] = eq["X_leader"]
                results["K_leader"][i] = eq["K_leader"]
                results["X_follower"][i] = eq["X_follower"]
                results["K_follower"][i] = eq["K_follower"]
                results["X_default_leader"][i] = eq["X_default_leader"]
                results["X_default_follower"][i] = eq["X_default_follower"]
                results["has_solution"][i] = True
            except (ValueError, RuntimeError):
                continue

        return results

    # ------------------------------------------------------------------
    # Summary
    # ------------------------------------------------------------------

    def summary(self, regime: str = "H") -> dict:
        """Return a summary of the equilibrium solution."""
        result = {}

        try:
            eq = self.solve_preemption_equilibrium(regime)
            result["equilibrium"] = eq

            # Add NPV information
            result["leader_npv"] = self._leader_value_at(
                eq["X_leader"], eq["K_leader"], regime
            )
            result["follower_npv"] = self._follower_npv(
                eq["K_follower"], eq["K_leader"], eq["X_follower"], regime
            )

            # Add investment costs
            result["leader_investment_cost"] = self.investment_cost(eq["K_leader"])
            result["follower_investment_cost"] = self.investment_cost(eq["K_follower"])

            # Market shares at follower entry
            if eq["K_follower"] > 0 and eq["K_leader"] > 0:
                result["leader_share_at_follower_entry"] = self.contest_share(
                    eq["K_leader"], eq["K_follower"]
                )
            result["leverage"] = self.leverage
            result["bankruptcy_cost"] = self.bankruptcy_cost
        except (ValueError, RuntimeError) as e:
            result["error"] = str(e)

        return result
