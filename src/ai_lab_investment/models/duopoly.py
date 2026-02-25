"""Duopoly model: endogenous lambda, training allocation, default risk.

Solves for the Markov-perfect equilibrium of a preemption game between two
firms under:
- Regime-switching GBM demand with endogenous arrival rate
- Training-inference allocation (phi) as a strategic variable
- Regime-specific contest functions:
    L-regime: share over inference capacity [(1-phi)*K]^alpha
    H-regime: share over training compute [phi*K]^alpha
- Endogenous default boundary (Leland 1994)
- Preemption equilibrium (Huisman & Kort 2015)

The endogenous arrival rate:
    lambda_tilde = lam_0 + xi * [(phi_i*K_i)^eta + (phi_j*K_j)^eta]

creates a positive externality: rival training helps bring AGI closer,
benefiting both firms. The strategic interaction is in the H-regime share,
not in the speed of arrival.

When xi = 0, the model reduces to the exogenous-lambda baseline.

Investment trigger methodology:
    The investment trigger uses beta_H (the H-regime characteristic root)
    because the investment option value is driven by H-regime expectations.
    The installed value includes both L-regime inference revenue and
    H-regime training revenue (via regime-switch continuation value),
    providing a combined effective revenue coefficient A_eff for the trigger.
"""

import numpy as np
from scipy import optimize

from .parameters import ModelParameters


class DuopolyModel:
    """Duopoly investment game with endogenous lambda and training allocation.

    Two firms hold options to invest irreversibly in capacity. Each firm
    chooses capacity K, training fraction phi, and leverage ell. Revenue
    is shared via regime-specific contest functions:
        L-regime: inference-based competition over [(1-phi)*K]^alpha
        H-regime: training/quality-based competition over [phi*K]^alpha

    The endogenous lambda_tilde depends on both firms' training compute.

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
            params: Base model parameters (includes xi, lam_0, eta).
            leverage: Default debt-to-investment-cost ratio D/I(K). 0 = all equity.
            coupon_rate: Coupon rate on debt as fraction of face value.
            bankruptcy_cost: Fraction of firm value lost in default (alpha_bc).
        """
        self.params = params
        self.leverage = leverage
        self.coupon_rate = coupon_rate
        self.bankruptcy_cost = bankruptcy_cost
        self._cache: dict = {}

    # ------------------------------------------------------------------
    # Endogenous arrival rate
    # ------------------------------------------------------------------

    def endogenous_lambda(
        self,
        phi_i: float,
        K_i: float,
        phi_j: float = 0.0,
        K_j: float = 0.0,
    ) -> float:
        """Compute endogenous arrival rate lambda_tilde.

        When xi = 0, returns self.params.lam (exact recovery of baseline).
        When xi > 0, returns lam_0 + xi * training_contribution.
        """
        return self.params.lambda_tilde(phi_i, K_i, phi_j, K_j)

    # ------------------------------------------------------------------
    # Revenue with regime-specific competition
    # ------------------------------------------------------------------

    def contest_share_L(
        self, phi_i: float, K_i: float, phi_j: float, K_j: float
    ) -> float:
        """L-regime contest share: inference-based competition.

        share_i^L = [(1-phi_i)*K_i]^alpha
                    / {[(1-phi_i)*K_i]^alpha + [(1-phi_j)*K_j]^alpha}
        """
        alpha = self.params.alpha
        inf_i = (1.0 - phi_i) * K_i
        inf_j = (1.0 - phi_j) * K_j
        num = inf_i**alpha
        denom = num + inf_j**alpha
        if denom <= 0:
            return 0.5
        return num / denom

    def contest_share_H(
        self, phi_i: float, K_i: float, phi_j: float, K_j: float
    ) -> float:
        """H-regime contest share: training/quality-based competition.

        share_i^H = [phi_i*K_i]^alpha
                    / {[phi_i*K_i]^alpha + [phi_j*K_j]^alpha}
        """
        alpha = self.params.alpha
        tr_i = phi_i * K_i
        tr_j = phi_j * K_j
        if tr_i <= 0 and tr_j <= 0:
            return 0.5
        num = tr_i**alpha if tr_i > 0 else 0.0
        denom = num + (tr_j**alpha if tr_j > 0 else 0.0)
        if denom <= 0:
            return 0.5
        return num / denom

    def contest_share(self, K_i: float, K_j: float) -> float:
        """Legacy contest share (no phi, uses total capacity).

        Preserved for backward compatibility. Equivalent to the old model
        where phi is symmetric or absent.
        """
        alpha = self.params.alpha
        num = K_i**alpha
        denom = K_i**alpha + K_j**alpha
        if denom <= 0:
            return 0.5
        return num / denom

    # ------------------------------------------------------------------
    # Effective revenue coefficient (combined L + H)
    # ------------------------------------------------------------------

    def _effective_revenue_coeff(
        self,
        phi_i: float,
        K_i: float,
        phi_j: float,
        K_j: float,
        monopolist: bool = False,
    ) -> float:
        """Compute effective revenue coefficient per unit X.

        A_eff = [(1-phi)*K]^alpha * s_L / (r - mu_L + lam_tilde)
              + lam_tilde / (r - mu_L + lam_tilde) * [phi*K]^alpha * s_H * A_H

        This is V(X, K, phi) / X + delta*K/r (i.e., the revenue part only).

        Args:
            phi_i, K_i: Firm i's training fraction and capacity.
            phi_j, K_j: Firm j's training fraction and capacity.
            monopolist: If True, firm i is the only investor (shares = 1).

        Returns:
            Effective revenue coefficient A_eff.
        """
        p = self.params
        lam_tilde = self.endogenous_lambda(phi_i, K_i, phi_j, K_j)

        inf_cap = (1.0 - phi_i) * K_i
        tr_cap = phi_i * K_i

        if monopolist:
            s_L = 1.0
            s_H = 1.0
        else:
            s_L = self.contest_share_L(phi_i, K_i, phi_j, K_j)
            s_H = self.contest_share_H(phi_i, K_i, phi_j, K_j)

        denom_L = p.r - p.mu_L + lam_tilde
        if denom_L <= 0:
            return 0.0

        # L-regime inference revenue coefficient
        a_eff = inf_cap**p.alpha * s_L / denom_L

        # H-regime continuation value coefficient
        if tr_cap > 0 and lam_tilde > 0:
            a_eff += lam_tilde / denom_L * tr_cap**p.alpha * s_H * p.A_H

        return a_eff

    # ------------------------------------------------------------------
    # Present value functions with training-inference split
    # ------------------------------------------------------------------

    def installed_value_L(
        self,
        X: float,
        phi_i: float,
        K_i: float,
        phi_j: float,
        K_j: float,
    ) -> float:
        """L-regime installed value for firm i (post-investment, pre-switch).

        V_i^L(X) = A_eff * X - delta * K_i / r
        """
        p = self.params
        a_eff = self._effective_revenue_coeff(phi_i, K_i, phi_j, K_j)
        return a_eff * X - p.delta * K_i / p.r

    def installed_value_H(
        self,
        X: float,
        phi_i: float,
        K_i: float,
        phi_j: float,
        K_j: float,
    ) -> float:
        """H-regime installed value for firm i (absorbing state).

        V_i^H(X) = X * (phi_i*K_i)^alpha * s_i^H / (r - mu_H) - delta * K_i / r
        """
        p = self.params
        s_H = self.contest_share_H(phi_i, K_i, phi_j, K_j)
        tr_cap = phi_i * K_i
        if tr_cap <= 0:
            return -p.delta * K_i / p.r
        return p.A_H * X * tr_cap**p.alpha * s_H - p.delta * K_i / p.r

    def monopolist_value_L(
        self,
        X: float,
        phi_i: float,
        K_i: float,
    ) -> float:
        """L-regime value when firm i is the only investor (share = 1)."""
        p = self.params
        a_eff = self._effective_revenue_coeff(phi_i, K_i, 0.0, 0.0, monopolist=True)
        return a_eff * X - p.delta * K_i / p.r

    def monopolist_value_H(
        self,
        X: float,
        phi_i: float,
        K_i: float,
    ) -> float:
        """H-regime monopolist value (share = 1).

        V_i^H(X) = X * (phi_i*K_i)^alpha / (r - mu_H) - delta * K_i / r
        """
        p = self.params
        tr_cap = phi_i * K_i
        if tr_cap <= 0:
            return -p.delta * K_i / p.r
        return p.A_H * X * tr_cap**p.alpha - p.delta * K_i / p.r

    def duopoly_revenue_pv(
        self, X: float, K_i: float, K_j: float, regime: str
    ) -> float:
        """Legacy PV of flow revenue (no phi, backward-compatible).

        V_i = A_s * X * K_i^alpha / (K_i^alpha + K_j^alpha) - delta * K_i / r
        """
        p = self.params
        A = p.A_H if regime == "H" else p.A_L
        share = self.contest_share(K_i, K_j)
        return A * X * K_i**p.alpha * share - p.delta * K_i / p.r

    def monopolist_revenue_pv(self, X: float, K: float, regime: str) -> float:
        """Legacy PV when the firm is the only investor (no phi).

        V_monopolist = A_s * X * K^alpha - delta * K / r
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

    def coupon_payment(self, K: float, leverage: float | None = None) -> float:
        """Annual coupon payment on debt.

        Debt face value = leverage * I(K).
        Coupon = coupon_rate * face_value.
        """
        lev = leverage if leverage is not None else self.leverage
        if lev <= 0:
            return 0.0
        face_value = lev * self.investment_cost(K)
        return self.coupon_rate * face_value

    def default_boundary(
        self,
        phi_i: float,
        K_i: float,
        phi_j: float,
        K_j: float,
        leverage: float | None = None,
    ) -> float:
        """Endogenous default boundary X_D (Leland 1994).

        Default is driven by L-regime total revenue (inference + H-continuation).
        Higher phi reduces inference revenue but increases H-regime continuation
        (the "faith-based survival" mechanism).

        X_D = [beta_neg / (beta_neg - 1)] * [c_D/r + delta*K/r] / A_eff

        Derived from smooth-pasting on the ongoing equity value (excluding
        the sunk equity contribution, which is irrelevant for the default
        decision).

        Returns 0 if no debt (leverage = 0).
        """
        lev = leverage if leverage is not None else self.leverage
        if lev <= 0:
            return 0.0

        p = self.params
        c_D = self.coupon_payment(K_i, lev)
        if c_D <= 0:
            return 0.0

        is_monopolist = K_j <= 0
        revenue_coeff = self._effective_revenue_coeff(
            phi_i, K_i, phi_j, K_j, monopolist=is_monopolist
        )

        if revenue_coeff <= 0:
            return np.inf

        # Negative root of the characteristic equation in L-regime
        lam_tilde = self.endogenous_lambda(phi_i, K_i, phi_j, K_j)
        beta_neg = self._negative_root("L", lam_tilde)

        X_D = (
            (beta_neg / (beta_neg - 1.0))
            * (c_D / p.r + p.delta * K_i / p.r)
            / revenue_coeff
        )
        return max(X_D, 0.0)

    def _negative_root(self, regime: str, lam_tilde: float = 0.0) -> float:
        """Negative root of the characteristic equation.

        Solves: (sigma^2/2) * beta * (beta - 1) + mu * beta - (r + lam_tilde) = 0
        Returns the negative root (beta < 0).

        For the L-regime default boundary, the effective discount rate is
        r + lam_tilde, incorporating the regime-switching term. This parallels
        the positive root computation in parameters.py which uses discount = r + lam.
        """
        p = self.params
        sigma = p.sigma
        mu = p.mu_H if regime == "H" else p.mu_L
        a = 0.5 * sigma**2
        b = mu - 0.5 * sigma**2
        c = -(p.r + lam_tilde)
        discriminant = b**2 - 4 * a * c
        return (-b - discriminant**0.5) / (2 * a)

    # ------------------------------------------------------------------
    # Equity and debt valuation with default
    # ------------------------------------------------------------------

    def equity_value(
        self,
        X: float,
        phi_i: float,
        K_i: float,
        phi_j: float,
        K_j: float,
        leverage: float | None = None,
    ) -> float:
        """Equity value of firm i after investment, accounting for default.

        E(X) = V(X) - equity_contribution - coupon/r
               + [coupon/r - V(X_D)] * (X/X_D)^beta_neg

        The ongoing equity (excluding sunk cost) satisfies E_ongoing(X_D) = 0.
        The net equity at X_D equals -equity_contribution, clamped to 0 by
        limited liability.
        Without debt, equity = V(X) - I(K).
        """
        p = self.params
        lev = leverage if leverage is not None else self.leverage

        if K_j > 0:
            V_X = self.installed_value_L(X, phi_i, K_i, phi_j, K_j)
        else:
            V_X = self.monopolist_value_L(X, phi_i, K_i)

        if lev <= 0:
            return max(V_X - self.investment_cost(K_i), 0.0)

        c_D = self.coupon_payment(K_i, lev)
        I_K = self.investment_cost(K_i)
        equity_contribution = I_K * (1.0 - lev)

        X_D = self.default_boundary(phi_i, K_i, phi_j, K_j, lev)

        if X_D <= 0 or X <= X_D:
            return max(V_X - equity_contribution - c_D / p.r, 0.0)

        lam_tilde = self.endogenous_lambda(phi_i, K_i, phi_j, K_j)
        beta_neg = self._negative_root("L", lam_tilde)

        if K_j > 0:
            V_XD = self.installed_value_L(X_D, phi_i, K_i, phi_j, K_j)
        else:
            V_XD = self.monopolist_value_L(X_D, phi_i, K_i)

        # Default option value (put-like: value of walking away)
        # Ongoing equity at X_D: V(X_D) - c_D/r + default_claim = 0
        # Since V_XD = A_eff*X_D - delta*K/r already includes operating costs:
        default_claim = c_D / p.r - V_XD
        default_option = default_claim * (X / X_D) ** beta_neg

        equity = V_X - equity_contribution - c_D / p.r + default_option
        return max(equity, 0.0)

    def debt_value(
        self,
        X: float,
        phi_i: float,
        K_i: float,
        phi_j: float,
        K_j: float,
        leverage: float | None = None,
    ) -> float:
        """Debt value accounting for default risk.

        D(X) = coupon/r - [coupon/r - (1 - alpha_bc) * V(X_D)] * (X/X_D)^beta_neg
        """
        lev = leverage if leverage is not None else self.leverage
        if lev <= 0:
            return 0.0

        p = self.params
        c_D = self.coupon_payment(K_i, lev)
        X_D = self.default_boundary(phi_i, K_i, phi_j, K_j, lev)

        if X_D <= 0:
            return c_D / p.r

        lam_tilde = self.endogenous_lambda(phi_i, K_i, phi_j, K_j)
        beta_neg = self._negative_root("L", lam_tilde)

        if K_j > 0:
            V_XD = self.installed_value_L(X_D, phi_i, K_i, phi_j, K_j)
        else:
            V_XD = self.monopolist_value_L(X_D, phi_i, K_i)

        recovery = (1.0 - self.bankruptcy_cost) * (V_XD + p.delta * K_i / p.r)
        default_loss = c_D / p.r - recovery
        debt = c_D / p.r - default_loss * (X / X_D) ** beta_neg
        return max(debt, 0.0)

    def firm_value(
        self,
        X: float,
        phi_i: float,
        K_i: float,
        phi_j: float,
        K_j: float,
        leverage: float | None = None,
    ) -> float:
        """Total firm value = equity + debt."""
        return self.equity_value(X, phi_i, K_i, phi_j, K_j, leverage) + self.debt_value(
            X, phi_i, K_i, phi_j, K_j, leverage
        )

    # ------------------------------------------------------------------
    # Follower's problem (3D: K, phi, leverage)
    # ------------------------------------------------------------------

    def _follower_value(
        self,
        X: float,
        K_F: float,
        phi_F: float,
        K_L: float,
        phi_L: float,
        lev_F: float,
    ) -> float:
        """Follower's equity value from investing at demand X."""
        return self.equity_value(X, phi_F, K_F, phi_L, K_L, lev_F)

    def _follower_trigger(
        self,
        K_F: float,
        phi_F: float,
        K_L: float,
        phi_L: float,
        lev_F: float,
    ) -> float:
        """Follower's optimal trigger X_F* for given (K_F, phi_F, lev_F).

        X_F* = [beta_H/(beta_H-1)] * total_cost / A_eff

        Uses beta_H because the investment option value is driven by
        H-regime expectations. A_eff includes both L and H revenues.
        """
        p = self.params
        beta = p.beta_H

        a_eff = self._effective_revenue_coeff(phi_F, K_F, phi_L, K_L)
        if a_eff <= 0:
            return np.inf

        markup = beta / (beta - 1.0)
        c_D = self.coupon_payment(K_F, lev_F)
        equity_cost = (1.0 - lev_F) * self.investment_cost(K_F)
        total_cost = p.delta * K_F / p.r + equity_cost + c_D / p.r

        return markup * total_cost / a_eff

    def _follower_objective_3d(
        self,
        params_vec: np.ndarray,
        K_L: float,
        phi_L: float,
    ) -> float:
        """Negative of follower's option value factor for 3D optimization.

        params_vec = [log_K, phi, leverage]
        Maximizes h(K, phi, lev) = a_eff^beta_H / cost^(beta_H-1).
        """
        log_K, phi_F, lev_F = params_vec
        K_F = np.exp(log_K)

        # Bound checks
        if phi_F <= 0.01 or phi_F >= 0.99 or lev_F < 0 or lev_F > 0.95:
            return 1e20

        p = self.params
        beta = p.beta_H

        a_eff = self._effective_revenue_coeff(phi_F, K_F, phi_L, K_L)

        c_D = self.coupon_payment(K_F, lev_F)
        equity_cost = (1.0 - lev_F) * self.investment_cost(K_F)
        b = p.delta * K_F / p.r + equity_cost + c_D / p.r

        if a_eff <= 0 or b <= 0:
            return 1e20
        return -(beta * np.log(a_eff) - (beta - 1.0) * np.log(b))

    def solve_follower(
        self,
        K_L: float,
        phi_L: float,
        regime: str = "H",
    ) -> tuple[float, float, float, float]:
        """Solve follower's optimal investment problem (3D).

        Given leader's (K_L, phi_L), find follower's optimal
        trigger, capacity, training fraction, and leverage.

        Args:
            K_L: Leader's installed capacity.
            phi_L: Leader's training fraction.
            regime: Regime label (for cache key compatibility).

        Returns:
            (X_F*, K_F*, phi_F*, lev_F*): Follower's optimal choices.
        """
        cache_key = ("follower_3d", K_L, phi_L, regime)
        if cache_key in self._cache:
            return self._cache[cache_key]

        # 3D optimization with multiple starting points
        # When leverage=0 (all-equity), fix leverage at 0
        max_lev = min(self.leverage * 1.5 + 0.1, 0.95) if self.leverage > 0 else 0.0
        best_val = 1e20
        best_params = None

        lev_starts = [0.0] if max_lev == 0 else [0.0, self.leverage, max_lev * 0.7]

        for log_K_init in [-2, 0, 2]:
            for phi_init in [0.15, 0.30, 0.50]:
                for lev_init in lev_starts:
                    x0 = np.array([log_K_init, phi_init, lev_init])
                    try:
                        result = optimize.minimize(
                            self._follower_objective_3d,
                            x0,
                            args=(K_L, phi_L),
                            method="Nelder-Mead",
                            options={"maxiter": 2000, "xatol": 1e-8, "fatol": 1e-10},
                        )
                        if result.fun < best_val:
                            best_val = result.fun
                            best_params = result.x
                    except (ValueError, RuntimeError):
                        continue

        if best_params is None or best_val >= 1e19:
            msg = f"Follower optimization failed for K_L={K_L:.4f}, phi_L={phi_L:.3f}"
            raise RuntimeError(msg)

        K_F = np.exp(best_params[0])
        phi_F = np.clip(best_params[1], 0.01, 0.99)
        lev_F = np.clip(best_params[2], 0.0, max_lev)
        X_F = self._follower_trigger(K_F, phi_F, K_L, phi_L, lev_F)

        self._cache[cache_key] = (X_F, K_F, phi_F, lev_F)
        return X_F, K_F, phi_F, lev_F

    # ------------------------------------------------------------------
    # Leader's problem
    # ------------------------------------------------------------------

    def _leader_value_at(
        self,
        X: float,
        K_L: float,
        phi_L: float,
        lev_L: float,
    ) -> float:
        """Leader's equity value at demand X.

        Three phases:
        1. Pre-follower-entry, L-regime: monopoly revenues
        2. Post-follower-entry, L-regime: duopoly revenues
        3. H-regime (after switch): duopoly quality-based revenue

        Accounts for follower's entry changing lambda_tilde.
        """
        p = self.params

        # Follower's best response
        X_F, K_F, phi_F, lev_F = self.solve_follower(K_L, phi_L)

        # Leader's costs
        c_D_L = self.coupon_payment(K_L, lev_L)
        I_L = self.investment_cost(K_L)
        equity_cost_L = (1.0 - lev_L) * I_L

        if X >= X_F:
            # Follower already entered — duopoly
            V_duo = self.installed_value_L(X, phi_L, K_L, phi_F, K_F)
            return max(V_duo - equity_cost_L - c_D_L / p.r, 0.0)

        # Phase 1: Monopolist (before follower enters)
        V_mono = self.monopolist_value_L(X, phi_L, K_L)

        # Phase 2: Revenue drop when follower enters
        V_mono_at_XF = self.monopolist_value_L(X_F, phi_L, K_L)
        V_duo_at_XF = self.installed_value_L(X_F, phi_L, K_L, phi_F, K_F)
        revenue_drop = V_mono_at_XF - V_duo_at_XF

        # Probability-weighted PV of revenue loss
        beta = p.beta_H
        entry_factor = (X / X_F) ** beta if X_F > 0 else 1.0

        V_leader = V_mono - revenue_drop * entry_factor

        return max(V_leader - equity_cost_L - c_D_L / p.r, 0.0)

    def _leader_objective_3d(
        self,
        params_vec: np.ndarray,
    ) -> float:
        """Negative of leader's option value factor for 3D optimization.

        params_vec = [log_K, phi, leverage]
        Uses beta_H and A_eff (combined L+H revenue coefficient).
        """
        log_K, phi_L, lev_L = params_vec
        K_L = np.exp(log_K)

        if phi_L <= 0.01 or phi_L >= 0.99 or lev_L < 0 or lev_L > 0.95:
            return 1e20

        p = self.params
        beta = p.beta_H

        # Revenue coefficient as monopolist
        a_eff = self._effective_revenue_coeff(phi_L, K_L, 0.0, 0.0, monopolist=True)

        c_D = self.coupon_payment(K_L, lev_L)
        equity_cost = (1.0 - lev_L) * self.investment_cost(K_L)
        b = p.delta * K_L / p.r + equity_cost + c_D / p.r

        if a_eff <= 0 or b <= 0:
            return 1e20
        return -(beta * np.log(a_eff) - (beta - 1.0) * np.log(b))

    def solve_leader_monopolist(
        self,
        regime: str = "H",
    ) -> tuple[float, float, float, float]:
        """Solve leader's problem ignoring preemption (monopolist trigger).

        Returns:
            (X_L_mono*, K_L*, phi_L*, lev_L*): Leader's monopolist solution.
        """
        cache_key = ("leader_mono_3d", regime)
        if cache_key in self._cache:
            return self._cache[cache_key]

        # When leverage=0 (all-equity), fix leverage at 0
        max_lev = min(self.leverage * 1.5 + 0.1, 0.95) if self.leverage > 0 else 0.0
        best_val = 1e20
        best_params = None

        lev_starts = [0.0] if max_lev == 0 else [0.0, self.leverage, max_lev * 0.7]

        for log_K_init in [-2, 0, 2]:
            for phi_init in [0.15, 0.30, 0.50]:
                for lev_init in lev_starts:
                    x0 = np.array([log_K_init, phi_init, lev_init])
                    try:
                        result = optimize.minimize(
                            self._leader_objective_3d,
                            x0,
                            method="Nelder-Mead",
                            options={"maxiter": 2000, "xatol": 1e-8, "fatol": 1e-10},
                        )
                        if result.fun < best_val:
                            best_val = result.fun
                            best_params = result.x
                    except (ValueError, RuntimeError):
                        continue

        if best_params is None or best_val >= 1e19:
            msg = f"Leader optimization failed for regime={regime}"
            raise RuntimeError(msg)

        K_L = np.exp(best_params[0])
        phi_L = np.clip(best_params[1], 0.01, 0.99)
        lev_L = np.clip(best_params[2], 0.0, max_lev)

        # Compute trigger using beta_H and A_eff
        p = self.params
        beta = p.beta_H
        a_eff = self._effective_revenue_coeff(phi_L, K_L, 0.0, 0.0, monopolist=True)

        markup = beta / (beta - 1.0)
        c_D = self.coupon_payment(K_L, lev_L)
        equity_cost = (1.0 - lev_L) * self.investment_cost(K_L)
        total_cost = p.delta * K_L / p.r + equity_cost + c_D / p.r

        X_L = markup * total_cost / a_eff if a_eff > 0 else np.inf

        self._cache[cache_key] = (X_L, K_L, phi_L, lev_L)
        return X_L, K_L, phi_L, lev_L

    # ------------------------------------------------------------------
    # Preemption equilibrium
    # ------------------------------------------------------------------

    def follower_option_value(
        self, X: float, K_L: float, phi_L: float, regime: str
    ) -> float:
        """Value of the follower's option at demand X.

        F_follower(X) = B_F * X^beta_H   for X < X_F*
        F_follower(X) = NPV              for X >= X_F*
        """
        X_F, K_F, phi_F, lev_F = self.solve_follower(K_L, phi_L, regime)
        p = self.params
        beta = p.beta_H

        if X >= X_F:
            return self._follower_value(X, K_F, phi_F, K_L, phi_L, lev_F)

        npv_at_trigger = self._follower_value(X_F, K_F, phi_F, K_L, phi_L, lev_F)
        if X_F <= 0 or npv_at_trigger <= 0:
            return 0.0
        B_F = npv_at_trigger / X_F**beta
        return B_F * X**beta

    def _preemption_gap(self, X: float, regime: str) -> float:
        """Gap between leader's value and follower's option value at X.

        L(X) - F(X)
        """
        _, K_L, phi_L, lev_L = self.solve_leader_monopolist(regime)
        leader_val = self._leader_value_at(X, K_L, phi_L, lev_L)
        follower_opt = self.follower_option_value(X, K_L, phi_L, regime)
        return leader_val - follower_opt

    def solve_preemption_equilibrium(self, regime: str = "H") -> dict:
        """Solve for the preemption equilibrium.

        Finds X_P where the value of leading first equals the value
        of following.

        Returns dict with equilibrium quantities for leader and follower.
        """
        cache_key = ("preemption_3d", regime)
        if cache_key in self._cache:
            return self._cache[cache_key]

        X_L_mono, K_L, phi_L, lev_L = self.solve_leader_monopolist(regime)
        X_F, K_F, phi_F, lev_F = self.solve_follower(K_L, phi_L, regime)

        # Find the preemption point by bisection
        X_low = X_L_mono * 0.001
        X_high = X_L_mono

        gap_low = self._preemption_gap(X_low, regime)
        gap_high = self._preemption_gap(X_high, regime)

        if gap_low >= 0:
            X_P = X_low
        elif gap_high <= 0:
            X_P = X_L_mono
        else:
            try:
                X_P = optimize.brentq(
                    self._preemption_gap,
                    X_low,
                    X_high,
                    args=(regime,),
                    xtol=1e-10,
                )
            except ValueError:
                X_P = X_L_mono

        # Compute default boundaries
        X_D_L = self.default_boundary(phi_L, K_L, 0.0, 0.0, lev_L)
        X_D_F = self.default_boundary(phi_F, K_F, phi_L, K_L, lev_F)

        # Endogenous lambda with both firms invested
        lam_tilde = self.endogenous_lambda(phi_L, K_L, phi_F, K_F)

        result = {
            "X_leader": X_P,
            "K_leader": K_L,
            "phi_leader": phi_L,
            "lev_leader": lev_L,
            "X_follower": X_F,
            "K_follower": K_F,
            "phi_follower": phi_F,
            "lev_follower": lev_F,
            "X_default_leader": X_D_L,
            "X_default_follower": X_D_F,
            "X_leader_monopolist": X_L_mono,
            "lambda_tilde": lam_tilde,
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
        """Compute equilibrium outcomes over a range of parameter values."""
        n = len(values)
        results = {
            "param_values": values,
            "X_leader": np.full(n, np.nan),
            "K_leader": np.full(n, np.nan),
            "phi_leader": np.full(n, np.nan),
            "lev_leader": np.full(n, np.nan),
            "X_follower": np.full(n, np.nan),
            "K_follower": np.full(n, np.nan),
            "phi_follower": np.full(n, np.nan),
            "lev_follower": np.full(n, np.nan),
            "X_default_leader": np.full(n, np.nan),
            "X_default_follower": np.full(n, np.nan),
            "lambda_tilde": np.full(n, np.nan),
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
                for key in [
                    "X_leader",
                    "K_leader",
                    "phi_leader",
                    "lev_leader",
                    "X_follower",
                    "K_follower",
                    "phi_follower",
                    "lev_follower",
                    "X_default_leader",
                    "X_default_follower",
                    "lambda_tilde",
                ]:
                    results[key][i] = eq[key]
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
            "phi_leader": np.full(n, np.nan),
            "X_follower": np.full(n, np.nan),
            "K_follower": np.full(n, np.nan),
            "phi_follower": np.full(n, np.nan),
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
                for key in [
                    "X_leader",
                    "K_leader",
                    "phi_leader",
                    "X_follower",
                    "K_follower",
                    "phi_follower",
                    "X_default_leader",
                    "X_default_follower",
                ]:
                    results[key][i] = eq[key]
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

            result["leader_npv"] = self._leader_value_at(
                eq["X_leader"], eq["K_leader"], eq["phi_leader"], eq["lev_leader"]
            )
            result["follower_npv"] = self._follower_value(
                eq["X_follower"],
                eq["K_follower"],
                eq["phi_follower"],
                eq["K_leader"],
                eq["phi_leader"],
                eq["lev_follower"],
            )

            result["leader_investment_cost"] = self.investment_cost(eq["K_leader"])
            result["follower_investment_cost"] = self.investment_cost(eq["K_follower"])

            result["leader_share_L"] = self.contest_share_L(
                eq["phi_leader"],
                eq["K_leader"],
                eq["phi_follower"],
                eq["K_follower"],
            )
            result["leader_share_H"] = self.contest_share_H(
                eq["phi_leader"],
                eq["K_leader"],
                eq["phi_follower"],
                eq["K_follower"],
            )
            result["leverage"] = self.leverage
            result["bankruptcy_cost"] = self.bankruptcy_cost
            result["lambda_tilde"] = eq["lambda_tilde"]
        except (ValueError, RuntimeError) as e:
            result["error"] = str(e)

        return result
