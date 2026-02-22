"""N-firm numerical investment game with training/inference allocation.

Extends the analytical duopoly to N >= 2 firms using backward induction
and finite-difference methods on a log-X grid.

The sequential equilibrium (Bouis, Huisman & Kort 2009) is solved by:
1. Start with the last firm (N-th entrant) facing N-1 competitors
2. Solve its optimal trigger and capacity via 1D optimization
3. Work backward: the (k)-th entrant anticipates all future entry
4. Each firm's value function accounts for future entrants' triggers

Training/inference allocation:
- Post-investment, each firm splits capacity K into K_I (inference)
  and K_T (training): K = K_I + K_T
- Inference generates current revenue
- Training generates quality via power-law scaling: Q = (phi*K*t)^eta
- Quality multiplies demand: effective demand = X * exp(q)
"""

import warnings

import numpy as np
from scipy import optimize

from .parameters import ModelParameters


class NFirmModel:
    """N-firm sequential investment game with numerical solution.

    Solves for the sequential equilibrium where firms invest one at a time
    at distinct triggers X_1* < X_2* < ... < X_N*.

    Uses the same contest function as the duopoly model for revenue sharing.
    """

    def __init__(
        self,
        params: ModelParameters,
        n_firms: int = 3,
        leverage: float = 0.0,
        coupon_rate: float = 0.05,
        bankruptcy_cost: float = 0.30,
        training_fraction: float = 0.0,
        eta: float = 0.07,
    ):
        """Initialize the N-firm model.

        Args:
            params: Base model parameters.
            n_firms: Number of firms in the market.
            leverage: Debt-to-investment-cost ratio.
            coupon_rate: Coupon rate on debt.
            bankruptcy_cost: Fraction of value lost in default.
            training_fraction: Fraction of capacity allocated to training.
                0 = all inference (base case).
            eta: Scaling law exponent for training quality.
                Q = (phi*K*t)^eta per Kaplan et al. (2020).
        """
        self.params = params
        self.n_firms = n_firms
        self.leverage = leverage
        self.coupon_rate = coupon_rate
        self.bankruptcy_cost = bankruptcy_cost
        self.training_fraction = training_fraction
        self.eta = eta
        self._cache: dict = {}

    # ------------------------------------------------------------------
    # Revenue with N-firm competition
    # ------------------------------------------------------------------

    def contest_share(self, K_i: float, competitor_capacities: list[float]) -> float:
        """Contest function market share for firm i with N-1 competitors.

        share_i = K_i^alpha / (K_i^alpha + sum_j K_j^alpha)
        """
        alpha = self.params.alpha
        K_i_inf = K_i * (1.0 - self.training_fraction)
        num = K_i_inf**alpha
        denom = num + sum(
            (K * (1.0 - self.training_fraction)) ** alpha for K in competitor_capacities
        )
        if denom <= 0:
            return 1.0 / (1.0 + len(competitor_capacities))
        return num / denom

    def revenue_pv(
        self,
        X: float,
        K_i: float,
        competitor_capacities: list[float],
        regime: str,
        quality: float = 0.0,
    ) -> float:
        """Present value of revenue for firm i with N-1 competitors.

        V_i = A * X * exp(q) * K_I^alpha * share - delta * K / r
        """
        p = self.params
        A = p.A_H if regime == "H" else p.A_L
        K_I = K_i * (1.0 - self.training_fraction)
        share = self.contest_share(K_i, competitor_capacities)
        return A * X * np.exp(quality) * K_I**p.alpha * share - p.delta * K_i / p.r

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
        log_K: float,
        competitor_capacities: list[float],
        regime: str,
    ) -> float:
        """Negative log of option value factor for capacity optimization.

        Same approach as base model: maximize a(K)^beta / b(K)^(beta-1).
        """
        K = np.exp(log_K)
        p = self.params
        A = p.A_H if regime == "H" else p.A_L
        beta = p.beta_H if regime == "H" else p.beta_L

        K_I = K * (1.0 - self.training_fraction)
        share = self.contest_share(K, competitor_capacities)
        a = A * K_I**p.alpha * share

        c_D = self.coupon_payment(K)
        equity_cost = (1.0 - self.leverage) * self.investment_cost(K)
        b = p.delta * K / p.r + equity_cost + c_D / p.r

        if a <= 0 or b <= 0:
            return 1e20
        return -(beta * np.log(a) - (beta - 1.0) * np.log(b))

    def _entrant_trigger(
        self,
        K: float,
        competitor_capacities: list[float],
        regime: str,
    ) -> float:
        """Optimal trigger X*(K) for an entrant with given competitors."""
        p = self.params
        A = p.A_H if regime == "H" else p.A_L
        beta = p.beta_H if regime == "H" else p.beta_L

        K_I = K * (1.0 - self.training_fraction)
        share = self.contest_share(K, competitor_capacities)
        markup = beta / (beta - 1.0)

        c_D = self.coupon_payment(K)
        equity_cost = (1.0 - self.leverage) * self.investment_cost(K)
        total_cost = p.delta * K / p.r + equity_cost + c_D / p.r

        revenue_coeff = A * K_I**p.alpha * share
        if revenue_coeff <= 0:
            return np.inf
        return markup * total_cost / revenue_coeff

    def solve_entrant(
        self,
        competitor_capacities: list[float],
        regime: str = "H",
    ) -> tuple[float, float]:
        """Solve a single entrant's optimal trigger and capacity.

        Args:
            competitor_capacities: List of competitors' inference capacities.
            regime: Demand regime.

        Returns:
            (X*, K*): Optimal trigger and capacity.
        """
        result = optimize.minimize_scalar(
            self._entrant_objective,
            bounds=(-15, 15),
            method="bounded",
            args=(competitor_capacities, regime),
        )
        if result.fun >= 1e19:
            msg = f"Entrant optimization failed for regime={regime}"
            raise RuntimeError(msg)
        K_star = np.exp(result.x)
        X_star = self._entrant_trigger(K_star, competitor_capacities, regime)
        return X_star, K_star

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
        firm N-1 faces N-2, etc. Each firm's trigger and capacity are
        optimal given the anticipated future entry. The equilibrium is
        found by fixed-point iteration until capacity changes fall below tol.

        Returns:
            List of dicts, one per firm (ordered by entry time):
            [{'entry_order': 1, 'X_trigger': ..., 'K_capacity': ..., 'share': ...}, ...]
        """
        cache_key = ("seq_eq", regime)
        if cache_key in self._cache:
            return self._cache[cache_key]

        # First pass: solve each entrant's problem from last to first
        entrant_solutions = []
        for k in range(self.n_firms):
            n_competitors = self.n_firms - 1 - k
            # Approximate competitor capacities as copies of each other
            # Use a dummy capacity for initial solve
            dummy_competitors = [1.0] * n_competitors if n_competitors > 0 else []
            X_star, K_star = self.solve_entrant(dummy_competitors, regime)
            entrant_solutions.append((X_star, K_star))

        # Iterative refinement using actual capacities
        for _iteration in range(max_iterations):
            refined = []
            for k in range(self.n_firms):
                n_competitors = self.n_firms - 1 - k
                if n_competitors > 0:
                    # Use capacities from previous iteration
                    # Competitors who enter before this firm
                    competitor_Ks = [entrant_solutions[j][1] for j in range(k)]
                    # Add remaining competitors (enter after but in market view)
                    remaining = [
                        entrant_solutions[j][1] for j in range(k + 1, self.n_firms)
                    ]
                    all_competitors = competitor_Ks + remaining
                    # For the k-th entrant, use k competitors already in market
                    X_star, K_star = self.solve_entrant(
                        all_competitors[:n_competitors], regime
                    )
                else:
                    # Last entrant: monopolist-like (all others in market)
                    all_others = [
                        entrant_solutions[j][1] for j in range(self.n_firms) if j != k
                    ]
                    X_star, K_star = self.solve_entrant(all_others, regime)
                refined.append((X_star, K_star))

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
        indexed = [(X, K, i) for i, (X, K) in enumerate(entrant_solutions)]
        indexed.sort(key=lambda t: t[0])

        all_Ks = [K for _, K, _ in indexed]
        for order, (X_star, K_star, _orig_idx) in enumerate(indexed):
            other_Ks = [all_Ks[j] for j in range(len(all_Ks)) if j != order]
            share = self.contest_share(K_star, other_Ks)
            entries.append({
                "entry_order": order + 1,
                "X_trigger": X_star,
                "K_capacity": K_star,
                "market_share": share,
                "investment_cost": self.investment_cost(K_star),
            })

        self._cache[cache_key] = entries
        return entries

    # ------------------------------------------------------------------
    # Training/inference allocation
    # ------------------------------------------------------------------

    def optimal_training_fraction(
        self,
        K: float = 1.0,
        X: float = 1.0,
        competitor_capacities: list[float] | None = None,
        regime: str = "H",
    ) -> float:
        """Optimal training fraction from Proposition 5.

        phi* = eta / (alpha + eta)

        This closed-form follows from the power-law quality model
        Q(phi*K)^eta * ((1-phi)*K)^alpha. The FOC yields
        eta*(1-phi) = alpha*phi, independent of X, K, and competition.

        Returns:
            Optimal training fraction phi* in (0, 1).
        """
        return self.eta / (self.params.alpha + self.eta)

    def quality_dynamics(
        self,
        K: float,
        training_fraction: float,
        periods: int = 20,
    ) -> np.ndarray:
        """Compute quality trajectory from power-law scaling.

        Q(t) = (phi * K * t)^eta for t >= 1 (cumulative training compute).
        In log-space: q(t) = eta * ln(phi * K * t).

        Returns:
            Array of quality levels [q(0), q(1), ..., q(periods)].
        """
        K_T = K * training_fraction
        qualities = np.zeros(periods + 1)
        if K_T > 0:
            for t in range(1, periods + 1):
                qualities[t] = self.eta * np.log(K_T * t)
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
        # Solve each firm's problem independently with heterogeneous params
        for i, fp in enumerate(firm_params):
            # Create firm-specific parameters
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
                    "sigma_L",
                    "sigma_H",
                    "lam",
                )
            }
            p = self.params.with_param(**overrides) if overrides else self.params

            lev = fp.get("leverage", self.leverage)
            init_K = fp.get("initial_K", 0.0)

            # Other firms' capacities (use initial + solved capacities)
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
                training_fraction=self.training_fraction,
                eta=self.eta,
            )
            X_star, K_star = model.solve_entrant(other_Ks, regime)

            solutions.append({
                "firm_id": i,
                "X_trigger": X_star,
                "K_capacity": K_star,
                "initial_K": init_K,
                "leverage": lev,
                "investment_cost": self.investment_cost(K_star),
            })

        # Sort by trigger
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

        Returns triggers and capacities for each firm at each parameter value.
        """
        n_vals = len(values)
        results = {
            "param_values": values,
            "triggers": np.full((n_vals, self.n_firms), np.nan),
            "capacities": np.full((n_vals, self.n_firms), np.nan),
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
                    training_fraction=self.training_fraction,
                    eta=self.eta,
                )
                eq = m.solve_sequential_equilibrium(regime)
                for j, entry in enumerate(eq):
                    results["triggers"][i, j] = entry["X_trigger"]
                    results["capacities"][i, j] = entry["K_capacity"]
                results["has_solution"][i] = True
            except (ValueError, RuntimeError):
                continue

        return results

    # ------------------------------------------------------------------
    # Verification against Phase 2
    # ------------------------------------------------------------------

    def verify_against_duopoly(self, regime: str = "H") -> dict:
        """Compare N=2 numerical solution with analytical duopoly.

        Returns dict with trigger/capacity comparisons.
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
            "numerical_follower_X": numerical[1]["X_trigger"],
            "numerical_follower_K": numerical[1]["K_capacity"],
            "analytical_leader_X": analytical["X_leader"],
            "analytical_leader_K": analytical["K_leader"],
            "analytical_follower_X": analytical["X_follower"],
            "analytical_follower_K": analytical["K_follower"],
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

            if self.training_fraction > 0:
                result["training_fraction"] = self.training_fraction
                # Quality dynamics for the first entrant
                K1 = eq[0]["K_capacity"]
                qualities = self.quality_dynamics(K1, self.training_fraction)
                result["leader_quality_trajectory"] = qualities.tolist()

        except (ValueError, RuntimeError) as e:
            result["error"] = str(e)

        return result
