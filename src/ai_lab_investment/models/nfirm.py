"""N-firm numerical investment game with training/inference allocation.

Extends the analytical duopoly to N >= 2 firms using backward induction
and finite-difference methods on a log-X grid.

The sequential equilibrium (Bouis, Huisman & Kort 2009) is solved by:
1. Start with the last firm (N-th entrant) facing N-1 competitors
2. Solve its optimal trigger and capacity via 2D optimization (K, phi)
3. Work backward: the (k)-th entrant anticipates all future entry
4. Each firm's value function accounts for future entrants' triggers

Training/inference allocation uses the same specification as the
single-firm and duopoly models:
    L-regime: pi_i^L = X * [(1-phi_i)*K_i]^alpha * s_i^L
    H-regime: pi_i^H = X * [phi_i*K_i]^alpha * s_i^H
The combined A_eff revenue coefficient, incorporating regime-switching
continuation value, drives the investment trigger.
"""

import warnings

import numpy as np
from scipy import optimize

from .parameters import ModelParameters


class NFirmModel:
    """N-firm sequential investment game with numerical solution.

    Solves for the sequential equilibrium where firms invest one at a time
    at distinct triggers X_1* < X_2* < ... < X_N*.

    Uses the same regime-switching A_eff revenue coefficient as the duopoly
    model, with N-firm Tullock contest shares for revenue allocation.
    """

    def __init__(
        self,
        params: ModelParameters,
        n_firms: int = 3,
        leverage: float = 0.0,
        coupon_rate: float = 0.05,
        bankruptcy_cost: float = 0.30,
    ):
        """Initialize the N-firm model.

        Args:
            params: Base model parameters.
            n_firms: Number of firms in the market.
            leverage: Debt-to-investment-cost ratio.
            coupon_rate: Coupon rate on debt.
            bankruptcy_cost: Fraction of value lost in default.
        """
        self.params = params
        self.n_firms = n_firms
        self.leverage = leverage
        self.coupon_rate = coupon_rate
        self.bankruptcy_cost = bankruptcy_cost
        self._cache: dict = {}

    # ------------------------------------------------------------------
    # Revenue with N-firm competition
    # ------------------------------------------------------------------

    def contest_share_L(
        self,
        K_i: float,
        phi_i: float,
        competitor_capacities: list[float],
        competitor_phis: list[float],
    ) -> float:
        """L-regime contest share: inference-based competition.

        share_i^L = [(1-phi_i)*K_i]^alpha
                    / {[(1-phi_i)*K_i]^alpha + sum_j [(1-phi_j)*K_j]^alpha}
        """
        alpha = self.params.alpha
        inf_i = (1.0 - phi_i) * K_i
        num = inf_i**alpha
        denom = num + sum(
            ((1.0 - phi_j) * K_j) ** alpha
            for K_j, phi_j in zip(competitor_capacities, competitor_phis, strict=False)
        )
        if denom <= 0:
            return 1.0 / (1.0 + len(competitor_capacities))
        return num / denom

    def contest_share_H(
        self,
        K_i: float,
        phi_i: float,
        competitor_capacities: list[float],
        competitor_phis: list[float],
    ) -> float:
        """H-regime contest share: training/quality-based competition.

        share_i^H = [phi_i*K_i]^alpha
                    / {[phi_i*K_i]^alpha + sum_j [phi_j*K_j]^alpha}
        """
        alpha = self.params.alpha
        tr_i = phi_i * K_i
        if tr_i <= 0:
            return 0.0
        num = tr_i**alpha
        denom = num + sum(
            (phi_j * K_j) ** alpha
            for K_j, phi_j in zip(competitor_capacities, competitor_phis, strict=False)
            if phi_j * K_j > 0
        )
        if denom <= 0:
            return 1.0 / (1.0 + len(competitor_capacities))
        return num / denom

    def contest_share(self, K_i: float, competitor_capacities: list[float]) -> float:
        """Legacy contest share (backward-compatible, uses total capacity).

        Equivalent to contest_share_L with phi=0 for all firms.
        """
        alpha = self.params.alpha
        num = K_i**alpha
        denom = num + sum(K**alpha for K in competitor_capacities)
        if denom <= 0:
            return 1.0 / (1.0 + len(competitor_capacities))
        return num / denom

    def _effective_revenue_coeff(
        self,
        K_i: float,
        phi_i: float,
        competitor_capacities: list[float],
        competitor_phis: list[float],
    ) -> float:
        """Compute effective revenue coefficient per unit X (combined L + H).

        A_eff = [(1-phi)*K]^alpha * s_L / (r - mu_L + lam)
              + lam / (r - mu_L + lam) * [phi*K]^alpha * s_H * A_H

        Mirrors the duopoly model's _effective_revenue_coeff, using
        the exogenous lambda (params.lam) for the regime-switching rate.
        """
        p = self.params
        lam = p.lam

        s_L = self.contest_share_L(K_i, phi_i, competitor_capacities, competitor_phis)
        s_H = self.contest_share_H(K_i, phi_i, competitor_capacities, competitor_phis)

        inf_cap = (1.0 - phi_i) * K_i
        tr_cap = phi_i * K_i

        denom_L = p.r - p.mu_L + lam
        if denom_L <= 0:
            return 0.0

        a_eff = inf_cap**p.alpha * s_L / denom_L

        if tr_cap > 0 and lam > 0:
            a_eff += lam / denom_L * tr_cap**p.alpha * s_H * p.A_H

        return a_eff

    def revenue_pv(
        self,
        X: float,
        K_i: float,
        phi_i: float,
        competitor_capacities: list[float],
        competitor_phis: list[float],
    ) -> float:
        """Present value of revenue for firm i (combined L + H).

        V_i = A_eff * X - delta * K_i / r
        """
        p = self.params
        a_eff = self._effective_revenue_coeff(
            K_i, phi_i, competitor_capacities, competitor_phis
        )
        return a_eff * X - p.delta * K_i / p.r

    def investment_cost(self, K: float) -> float:
        """Total investment cost I(K) = c * K^gamma."""
        return self.params.c * K**self.params.gamma

    def coupon_payment(self, K: float) -> float:
        """Annual coupon payment on debt."""
        if self.leverage <= 0:
            return 0.0
        return self.coupon_rate * self.leverage * self.investment_cost(K)

    # ------------------------------------------------------------------
    # Single entrant's problem (building block)
    # ------------------------------------------------------------------

    def _entrant_objective(
        self,
        params_vec: np.ndarray,
        competitor_capacities: list[float],
        competitor_phis: list[float],
    ) -> float:
        """Negative log of option value factor for (K, phi) optimization.

        Maximizes h(K, phi) = A_eff^beta_H / cost^(beta_H-1).
        Uses beta_H because the investment option is driven by H-regime
        expectations (consistent with base_model and duopoly).
        """
        log_K, phi = params_vec
        K = np.exp(log_K)

        if phi <= 0.01 or phi >= 0.99:
            return 1e20

        p = self.params
        beta = p.beta_H

        a_eff = self._effective_revenue_coeff(
            K, phi, competitor_capacities, competitor_phis
        )

        c_D = self.coupon_payment(K)
        equity_cost = (1.0 - self.leverage) * self.investment_cost(K)
        b = p.delta * K / p.r + equity_cost + c_D / p.r

        if a_eff <= 0 or b <= 0:
            return 1e20
        return -(beta * np.log(a_eff) - (beta - 1.0) * np.log(b))

    def _entrant_trigger(
        self,
        K: float,
        phi: float,
        competitor_capacities: list[float],
        competitor_phis: list[float],
    ) -> float:
        """Optimal trigger X*(K, phi) for an entrant with given competitors."""
        p = self.params
        beta = p.beta_H
        markup = beta / (beta - 1.0)

        a_eff = self._effective_revenue_coeff(
            K, phi, competitor_capacities, competitor_phis
        )

        c_D = self.coupon_payment(K)
        equity_cost = (1.0 - self.leverage) * self.investment_cost(K)
        total_cost = p.delta * K / p.r + equity_cost + c_D / p.r

        if a_eff <= 0:
            return np.inf
        return markup * total_cost / a_eff

    def solve_entrant(
        self,
        competitor_capacities: list[float],
        competitor_phis: list[float] | None = None,
        regime: str = "H",
    ) -> tuple[float, float, float]:
        """Solve a single entrant's optimal trigger, capacity, and phi.

        Args:
            competitor_capacities: List of competitors' capacities.
            competitor_phis: List of competitors' training fractions.
                If None, defaults to 0.5 for each competitor.
            regime: Demand regime (for cache key compatibility).

        Returns:
            (X*, K*, phi*): Optimal trigger, capacity, and training fraction.
        """
        if competitor_phis is None:
            competitor_phis = [0.5] * len(competitor_capacities)

        best_val = 1e20
        best_params = None

        for log_K_init in [-2, 0, 2]:
            for phi_init in [0.15, 0.30, 0.50, 0.70]:
                x0 = np.array([log_K_init, phi_init])
                try:
                    result = optimize.minimize(
                        self._entrant_objective,
                        x0,
                        args=(competitor_capacities, competitor_phis),
                        method="Nelder-Mead",
                        options={"maxiter": 2000, "xatol": 1e-8, "fatol": 1e-10},
                    )
                    if result.fun < best_val:
                        best_val = result.fun
                        best_params = result.x
                except (ValueError, RuntimeError):
                    continue

        if best_params is None or best_val >= 1e19:
            msg = "Entrant optimization failed"
            raise RuntimeError(msg)

        K_star = np.exp(best_params[0])
        phi_star = np.clip(best_params[1], 0.01, 0.99)
        X_star = self._entrant_trigger(
            K_star, phi_star, competitor_capacities, competitor_phis
        )
        return X_star, K_star, phi_star

    # ------------------------------------------------------------------
    # Sequential equilibrium (backward induction)
    # ------------------------------------------------------------------

    def solve_sequential_equilibrium(
        self,
        regime: str = "H",
        max_iterations: int = 20,
        tol: float = 1e-6,
    ) -> list[dict[str, float]]:
        """Solve for the sequential equilibrium via iterative refinement.

        Firms invest one at a time: firm N (last) faces N-1 competitors,
        firm N-1 faces N-2, etc. Each firm's trigger, capacity, and
        training fraction are optimal given anticipated future entry.

        Returns:
            List of dicts, one per firm (ordered by entry time):
            [{'entry_order': 1, 'X_trigger': ..., 'K_capacity': ...,
              'phi_training': ..., 'share': ...}, ...]
        """
        cache_key = ("seq_eq", regime)
        if cache_key in self._cache:
            return self._cache[cache_key]

        # First pass: solve each entrant's problem from last to first
        entrant_solutions = []
        for k in range(self.n_firms):
            n_competitors = self.n_firms - 1 - k
            dummy_K = [1.0] * n_competitors if n_competitors > 0 else []
            dummy_phi = [0.5] * n_competitors if n_competitors > 0 else []
            X_star, K_star, phi_star = self.solve_entrant(dummy_K, dummy_phi, regime)
            entrant_solutions.append((X_star, K_star, phi_star))

        # Iterative refinement using actual capacities and phis
        # Use dampening (alpha_damp) to stabilize convergence
        alpha_damp = 0.5
        for _iteration in range(max_iterations):
            refined = []
            for k in range(self.n_firms):
                n_competitors = self.n_firms - 1 - k
                if n_competitors > 0:
                    competitor_Ks = [entrant_solutions[j][1] for j in range(k)]
                    competitor_phis = [entrant_solutions[j][2] for j in range(k)]
                    remaining_Ks = [
                        entrant_solutions[j][1] for j in range(k + 1, self.n_firms)
                    ]
                    remaining_phis = [
                        entrant_solutions[j][2] for j in range(k + 1, self.n_firms)
                    ]
                    all_Ks = (competitor_Ks + remaining_Ks)[:n_competitors]
                    all_phis = (competitor_phis + remaining_phis)[:n_competitors]
                    X_new, K_new, phi_new = self.solve_entrant(all_Ks, all_phis, regime)
                else:
                    all_others_K = [
                        entrant_solutions[j][1] for j in range(self.n_firms) if j != k
                    ]
                    all_others_phi = [
                        entrant_solutions[j][2] for j in range(self.n_firms) if j != k
                    ]
                    X_new, K_new, phi_new = self.solve_entrant(
                        all_others_K, all_others_phi, regime
                    )
                # Dampen updates to stabilize convergence
                X_old, K_old, phi_old = entrant_solutions[k]
                X_star = alpha_damp * X_new + (1 - alpha_damp) * X_old
                K_star = alpha_damp * K_new + (1 - alpha_damp) * K_old
                phi_star = alpha_damp * phi_new + (1 - alpha_damp) * phi_old
                refined.append((X_star, K_star, phi_star))

            max_change = max(
                abs(refined[k][1] - entrant_solutions[k][1])
                for k in range(self.n_firms)
            )
            entrant_solutions = refined
            if max_change < tol:
                break
        else:
            warnings.warn(
                f"N-firm equilibrium did not converge after {max_iterations} "
                f"iterations (max capacity change: {max_change:.2e})",
                stacklevel=2,
            )

        # Sort by trigger (lowest = first entrant = leader)
        entries = []
        indexed = [(X, K, phi, i) for i, (X, K, phi) in enumerate(entrant_solutions)]
        indexed.sort(key=lambda t: t[0])

        all_Ks = [K for _, K, _, _ in indexed]
        all_phis = [phi for _, _, phi, _ in indexed]
        for order, (X_star, K_star, phi_star, _orig_idx) in enumerate(indexed):
            other_Ks = [all_Ks[j] for j in range(len(all_Ks)) if j != order]
            other_phis = [all_phis[j] for j in range(len(all_phis)) if j != order]
            share = self.contest_share_L(K_star, phi_star, other_Ks, other_phis)
            entries.append({
                "entry_order": order + 1,
                "X_trigger": X_star,
                "K_capacity": K_star,
                "phi_training": phi_star,
                "market_share": share,
                "investment_cost": self.investment_cost(K_star),
            })

        self._cache[cache_key] = entries
        return entries

    # ------------------------------------------------------------------
    # Training/inference allocation (alternative quality-dynamics model)
    # ------------------------------------------------------------------

    def optimal_training_fraction_quality_model(
        self,
        K: float = 1.0,
        X: float = 1.0,
        competitor_capacities: list[float] | None = None,
        regime: str = "H",
    ) -> float:
        """Optimal training fraction from the quality-dynamics model.

        phi* = eta / (alpha + eta)

        This closed-form follows from the alternative quality-dynamics
        specification Q(phi*K)^eta * ((1-phi)*K)^alpha, NOT from the
        regime-switching A_eff model used by the main solver.

        Retained for comparison with the literature and as a
        reference point.
        """
        return self.params.eta / (self.params.alpha + self.params.eta)

    # Keep old name as alias for backward compatibility
    optimal_training_fraction = optimal_training_fraction_quality_model

    def quality_dynamics(
        self,
        K: float,
        training_fraction: float,
        periods: int = 20,
    ) -> np.ndarray:
        """Compute quality trajectory from power-law scaling.

        Q(t) = (phi * K * t)^eta for t >= 1 (cumulative training compute).
        In log-space: q(t) = eta * ln(phi * K * t).

        This is part of the alternative quality-dynamics model, not
        the main regime-switching specification.

        Returns:
            Array of quality levels [q(0), q(1), ..., q(periods)].
        """
        K_T = K * training_fraction
        qualities = np.zeros(periods + 1)
        if K_T > 0:
            for t in range(1, periods + 1):
                qualities[t] = self.params.eta * np.log(K_T * t)
        return qualities

    # ------------------------------------------------------------------
    # Heterogeneous firms
    # ------------------------------------------------------------------

    def solve_heterogeneous(
        self,
        firm_params: list[dict],
        regime: str = "H",
    ) -> list[dict[str, float]]:
        """Solve the N-firm game with heterogeneous firms.

        Args:
            firm_params: List of dicts with firm-specific overrides.
                Keys can include: 'r', 'alpha', 'c', 'gamma', 'delta',
                'leverage', 'initial_K', 'initial_quality'.

        Returns:
            List of dicts with each firm's equilibrium solution.
        """
        solutions = []
        for i, fp in enumerate(firm_params):
            overrides = {
                k: v
                for k, v in fp.items()
                if k
                in (
                    "r",
                    "alpha",
                    "c",
                    "gamma",
                    "delta",
                    "mu_L",
                    "mu_H",
                    "sigma",
                    "lam",
                )
            }
            p = self.params.with_param(**overrides) if overrides else self.params

            lev = fp.get("leverage", self.leverage)
            init_K = fp.get("initial_K", 0.0)

            other_Ks = []
            for j, fp_j in enumerate(firm_params):
                if j != i:
                    other_Ks.append(fp_j.get("initial_K", 1.0))

            model = NFirmModel(
                p,
                n_firms=1,
                leverage=lev,
                coupon_rate=self.coupon_rate,
                bankruptcy_cost=self.bankruptcy_cost,
            )
            # Competitors' phis default to 0.5 for heterogeneous solve
            other_phis = [0.5] * len(other_Ks)
            X_star, K_star, phi_star = model.solve_entrant(other_Ks, other_phis, regime)

            solutions.append({
                "firm_id": i,
                "X_trigger": X_star,
                "K_capacity": K_star,
                "phi_training": phi_star,
                "initial_K": init_K,
                "leverage": lev,
                "investment_cost": self.investment_cost(K_star),
            })

        solutions.sort(key=lambda s: s["X_trigger"])
        for order, sol in enumerate(solutions):
            sol["entry_order"] = order + 1

        return solutions

    # ------------------------------------------------------------------
    # Comparative statics
    # ------------------------------------------------------------------

    def comparative_statics(
        self,
        param_name: str,
        values: np.ndarray,
        regime: str = "H",
    ) -> dict[str, np.ndarray]:
        """Compute equilibrium over a range of parameter values.

        Returns triggers, capacities, and phis for each firm at each value.
        """
        n_vals = len(values)
        results = {
            "param_values": values,
            "triggers": np.full((n_vals, self.n_firms), np.nan),
            "capacities": np.full((n_vals, self.n_firms), np.nan),
            "phis": np.full((n_vals, self.n_firms), np.nan),
            "has_solution": np.zeros(n_vals, dtype=bool),
        }

        for i, val in enumerate(values):
            try:
                p = self.params.with_param(**{param_name: val})
                m = NFirmModel(
                    p,
                    n_firms=self.n_firms,
                    leverage=self.leverage,
                    coupon_rate=self.coupon_rate,
                    bankruptcy_cost=self.bankruptcy_cost,
                )
                eq = m.solve_sequential_equilibrium(regime)
                for j, entry in enumerate(eq):
                    results["triggers"][i, j] = entry["X_trigger"]
                    results["capacities"][i, j] = entry["K_capacity"]
                    results["phis"][i, j] = entry["phi_training"]
                results["has_solution"][i] = True
            except (ValueError, RuntimeError):
                continue

        return results

    # ------------------------------------------------------------------
    # Verification against Phase 2
    # ------------------------------------------------------------------

    def verify_against_duopoly(self, regime: str = "H") -> dict:
        """Compare N=2 numerical solution with analytical duopoly.

        Returns dict with trigger/capacity/phi comparisons.
        """
        from .duopoly import DuopolyModel

        # N=2 numerical
        m2 = NFirmModel(
            self.params,
            n_firms=2,
            leverage=self.leverage,
            coupon_rate=self.coupon_rate,
            bankruptcy_cost=self.bankruptcy_cost,
        )
        numerical = m2.solve_sequential_equilibrium(regime)

        # Analytical duopoly
        duo = DuopolyModel(
            self.params,
            leverage=self.leverage,
            coupon_rate=self.coupon_rate,
            bankruptcy_cost=self.bankruptcy_cost,
        )
        analytical = duo.solve_preemption_equilibrium(regime)

        return {
            "numerical_leader_X": numerical[0]["X_trigger"],
            "numerical_leader_K": numerical[0]["K_capacity"],
            "numerical_leader_phi": numerical[0]["phi_training"],
            "numerical_follower_X": numerical[1]["X_trigger"],
            "numerical_follower_K": numerical[1]["K_capacity"],
            "numerical_follower_phi": numerical[1]["phi_training"],
            "analytical_leader_X": analytical["X_leader"],
            "analytical_leader_K": analytical["K_leader"],
            "analytical_leader_phi": analytical["phi_leader"],
            "analytical_follower_X": analytical["X_follower"],
            "analytical_follower_K": analytical["K_follower"],
            "analytical_follower_phi": analytical["phi_follower"],
        }

    # ------------------------------------------------------------------
    # Summary
    # ------------------------------------------------------------------

    def summary(self, regime: str = "H") -> dict:
        """Return a summary of the N-firm equilibrium."""
        result = {"n_firms": self.n_firms}

        try:
            eq = self.solve_sequential_equilibrium(regime)
            result["entries"] = eq
            result["total_capacity"] = sum(e["K_capacity"] for e in eq)
            result["total_investment"] = sum(e["investment_cost"] for e in eq)
        except (ValueError, RuntimeError) as e:
            result["error"] = str(e)

        return result
