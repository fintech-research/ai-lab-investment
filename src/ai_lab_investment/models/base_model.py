"""Single-firm optimal investment model with regime-switching demand.

Solves for the optimal investment trigger X* and capacity K* under:
- Regime-switching GBM demand (Guo, Miao & Morellec 2005)
- Diminishing returns to compute (scaling laws)
- Convex investment costs
- Training-inference allocation (phi) as a strategic variable

Key economic results:
- In regime H (post-adoption): well-defined interior trigger and capacity.
  The firm invests when demand reaches X_H* with capacity K_H*.
- In regime L (pre-adoption): the trigger may or may not exist.
  When phi_L = (1-1/beta_L)/alpha >= 1, the option to wait is so
  valuable that the firm never exercises in L — it waits for the
  regime switch to H. The option value in L derives entirely from
  the probability of switching regimes.

Training-inference allocation:
  The firm allocates fraction phi to training and (1-phi) to inference.
  Revenue depends on regime:
    L-regime: pi_i^L = X * [(1-phi)*K]^alpha  (inference-based)
    H-regime: pi_i^H = X * [phi*K]^alpha       (training/quality-based)
  The optimal phi balances L-regime inference value against H-regime
  training value, modulated by the arrival rate lambda.
"""

import numpy as np
from scipy import optimize

from .parameters import ModelParameters


class SingleFirmModel:
    """Analytical solution for the single-firm investment problem.

    The firm holds a perpetual option to invest irreversibly in capacity K
    at cost I(K) = c * K^gamma. Once installed, capacity generates flow
    revenue pi(K, X) = X * K^alpha with operating cost delta * K.

    Demand X follows a regime-switching GBM. Regime H is absorbing.
    """

    def __init__(self, params: ModelParameters):
        self.params = params
        self._cache: dict = {}

    def installed_value(self, X: float, K: float, regime: str) -> float:
        """Value of installed capacity V(X, K, s).

        V_s(X, K) = A_s * X * K^alpha - delta * K / r
        """
        p = self.params
        A = p.A_H if regime == "H" else p.A_L
        return A * X * K**p.alpha - p.delta * K / p.r

    def investment_cost(self, K: float) -> float:
        """Total investment cost I(K) = c * K^gamma."""
        return self.params.c * K**self.params.gamma

    def _option_premium_ratio(self, regime: str) -> float:
        """Option premium ratio Phi = (1 - 1/beta) / alpha.

        An interior solution exists when 1/gamma < Phi < 1.
        Named _option_premium_ratio to distinguish from training fraction phi.
        """
        p = self.params
        beta = p.beta_H if regime == "H" else p.beta_L
        return (1.0 - 1.0 / beta) / p.alpha

    # Legacy alias
    _phi = _option_premium_ratio

    def has_interior_trigger(self, regime: str) -> bool:
        """Check whether an interior investment trigger exists.

        The trigger exists when 1/gamma < Phi < 1, where
        Phi = (1-1/beta)/alpha. When Phi >= 1, the option to wait
        is too valuable and the firm never invests in this regime.
        """
        Phi = self._option_premium_ratio(regime)
        return 1.0 / self.params.gamma < Phi < 1.0

    def _trigger_for_K(self, K: float, regime: str) -> float:
        """Optimal trigger X*(K) for a given capacity K.

        X*(K) = [beta/(beta-1)] * [delta*K/r + c*K^gamma] / [A*K^alpha]
        """
        p = self.params
        A = p.A_H if regime == "H" else p.A_L
        beta = p.beta_H if regime == "H" else p.beta_L
        markup = beta / (beta - 1.0)
        b = p.delta * K / p.r + p.c * K**p.gamma
        a = A * K**p.alpha
        return markup * b / a

    def _objective_K(self, log_K: float, regime: str) -> float:
        """Negative log of option value factor for K optimization.

        Maximizes h(K) = a(K)^beta / b(K)^(beta-1) over K.
        """
        K = np.exp(log_K)
        p = self.params
        A = p.A_H if regime == "H" else p.A_L
        beta = p.beta_H if regime == "H" else p.beta_L
        a = A * K**p.alpha
        b = p.delta * K / p.r + p.c * K**p.gamma
        if a <= 0 or b <= 0:
            return 1e20
        return -(beta * np.log(a) - (beta - 1.0) * np.log(b))

    def _solve_regime_H(self) -> tuple[float, float, float]:
        """Solve for X_H*, K_H*, B_H in the absorbing high regime.

        Returns:
            (X_H*, K_H*, B_H)

        Raises:
            RuntimeError: If no interior solution exists.
        """
        if "H" in self._cache:
            return self._cache["H"]

        p = self.params
        if not self.has_interior_trigger("H"):
            phi = self._phi("H")
            msg = (
                f"No interior solution in regime H. phi={phi:.3f}. "
                f"Need {1 / p.gamma:.3f} < phi < 1. "
                f"Try increasing alpha or sigma_H."
            )
            raise RuntimeError(msg)

        result = optimize.minimize_scalar(
            self._objective_K,
            bounds=(-15, 15),
            method="bounded",
            args=("H",),
        )
        if result.fun >= 1e19:
            msg = "Regime H optimization failed: no valid interior solution found"
            raise RuntimeError(msg)
        K_star = np.exp(result.x)
        X_star = self._trigger_for_K(K_star, "H")

        # B_H from smooth-pasting
        B_H = p.A_H * K_star**p.alpha * X_star ** (1 - p.beta_H) / p.beta_H

        self._cache["H"] = (X_star, K_star, B_H)
        return X_star, K_star, B_H

    def _particular_solution_coeff(self) -> float:
        """Compute C, the particular solution coefficient for regime L.

        C = -lambda * B_H / Q_L(beta_H)
        """
        p = self.params
        if p.lam == 0:
            return 0.0

        _, _, B_H = self._solve_regime_H()
        Q_L = (
            0.5 * p.sigma_L**2 * p.beta_H * (p.beta_H - 1)
            + p.mu_L * p.beta_H
            - (p.r + p.lam)
        )
        if abs(Q_L) < 1e-15:
            return 0.0
        return -p.lam * B_H / Q_L

    def _solve_regime_L(self) -> tuple[float | None, float | None, float]:
        """Solve for the regime L option.

        When an interior trigger exists (phi_L < 1), returns (X_L*, K_L*, D_L).
        When no interior trigger exists (phi_L >= 1), the firm never invests
        in regime L. Returns (None, None, 0.0) and the option value is
        F_L(X) = C * X^beta_H (value from potential regime switch only).

        Returns:
            (X_L* or None, K_L* or None, D_L)
        """
        if "L" in self._cache:
            return self._cache["L"]

        p = self.params
        C = self._particular_solution_coeff()

        if self.has_interior_trigger("L"):
            # Interior solution exists in pure L
            result = optimize.minimize_scalar(
                self._objective_K,
                bounds=(-15, 15),
                method="bounded",
                args=("L",),
            )
            if result.fun >= 1e19:
                msg = "Regime L optimization failed: no valid interior solution found"
                raise RuntimeError(msg)
            K_star = np.exp(result.x)
            X_star = self._trigger_for_K(K_star, "L")

            # D_L from smooth-pasting
            D_L = (
                (p.A_L * K_star**p.alpha - p.beta_H * C * X_star ** (p.beta_H - 1))
                * X_star ** (1 - p.beta_L)
                / p.beta_L
            )
            self._cache["L"] = (X_star, K_star, D_L)
        else:
            # No interior trigger in regime L.
            # Option value comes entirely from regime-switching possibility:
            # F_L(X) = C * X^beta_H
            self._cache["L"] = (None, None, 0.0)

        return self._cache["L"]

    def optimal_trigger_and_capacity(self, regime: str) -> tuple[float, float]:
        """Solve for optimal trigger X* and capacity K*.

        Args:
            regime: 'L' or 'H'.

        Returns:
            Tuple (X*, K*).

        Raises:
            RuntimeError: If no interior solution exists for this regime.
        """
        if regime == "H":
            X_star, K_star, _ = self._solve_regime_H()
            return X_star, K_star
        else:
            X_star, K_star, _ = self._solve_regime_L()
            if X_star is None:
                msg = (
                    "No interior trigger in regime L. The firm waits for "
                    "the regime switch to H before investing. "
                    f"phi_L = {self._phi('L'):.3f} >= 1."
                )
                raise RuntimeError(msg)
            return X_star, K_star

    def option_value_H(self, X: float) -> float:
        """Option value in regime H (absorbing).

        F_H(X) = B_H * X^beta_H      for X < X_H*
        F_H(X) = V_H(X, K_H*) - I(K_H*)  for X >= X_H*
        """
        X_star, K_star, B_H = self._solve_regime_H()
        if X_star <= X:
            return self.installed_value(X, K_star, "H") - self.investment_cost(K_star)
        return B_H * X**self.params.beta_H

    def option_value_L(self, X: float) -> float:
        """Option value in regime L.

        If interior trigger exists:
          F_L(X) = D_L * X^beta_L + C * X^beta_H    for X < X_L*
          F_L(X) = V_L(X, K_L*) - I(K_L*)           for X >= X_L*

        If no trigger (phi_L >= 1):
          F_L(X) = C * X^beta_H     for all X
          (value from regime switching only)
        """
        X_star, K_star, D_L = self._solve_regime_L()
        p = self.params
        C = self._particular_solution_coeff()

        if X_star is not None and X_star <= X:
            return self.installed_value(X, K_star, "L") - self.investment_cost(K_star)
        return D_L * X**p.beta_L + C * X**p.beta_H

    def option_value(self, X: float, regime: str) -> float:
        """Option value in the specified regime."""
        if regime == "H":
            return self.option_value_H(X)
        return self.option_value_L(X)

    def npv_at_trigger(self, regime: str) -> float:
        """NPV of investment at the optimal trigger."""
        X_star, K_star = self.optimal_trigger_and_capacity(regime)
        return self.installed_value(X_star, K_star, regime) - self.investment_cost(
            K_star
        )

    def comparative_statics(
        self,
        param_name: str,
        values: np.ndarray,
        regime: str = "H",
    ) -> dict[str, np.ndarray]:
        """Compute optimal trigger and capacity over a range of parameter values.

        Args:
            param_name: Name of parameter to vary.
            values: Array of parameter values.
            regime: Regime to compute statics for.

        Returns:
            Dict with 'param_values', 'triggers', 'capacities', 'npvs',
            and 'has_trigger' (boolean array).
        """
        triggers = np.full_like(values, np.nan)
        capacities = np.full_like(values, np.nan)
        npvs = np.full_like(values, np.nan)
        has_trigger = np.zeros(len(values), dtype=bool)

        for i, val in enumerate(values):
            try:
                p = self.params.with_param(**{param_name: val})
                model = SingleFirmModel(p)
                X_star, K_star = model.optimal_trigger_and_capacity(regime)
                triggers[i] = X_star
                capacities[i] = K_star
                npvs[i] = model.npv_at_trigger(regime)
                has_trigger[i] = True
            except (ValueError, RuntimeError):
                continue

        return {
            "param_values": values,
            "triggers": triggers,
            "capacities": capacities,
            "npvs": npvs,
            "has_trigger": has_trigger,
        }

    def simulate_demand(
        self,
        X0: float,
        T: float,
        dt: float = 0.001,
        initial_regime: str = "L",
        rng: np.random.Generator | None = None,
    ) -> dict[str, np.ndarray]:
        """Simulate a regime-switching GBM path.

        Args:
            X0: Initial demand level.
            T: Time horizon.
            dt: Time step.
            initial_regime: Starting regime ('L' or 'H').
            rng: Random number generator.

        Returns:
            Dict with 'time', 'X', 'regime' arrays.
        """
        if rng is None:
            rng = np.random.default_rng()

        p = self.params
        n_steps = int(T / dt)
        time = np.linspace(0, T, n_steps + 1)
        X = np.zeros(n_steps + 1)
        regime = np.zeros(n_steps + 1, dtype=int)  # 0=L, 1=H

        X[0] = X0
        regime[0] = 0 if initial_regime == "L" else 1

        for t in range(n_steps):
            s = regime[t]
            mu = p.mu_H if s == 1 else p.mu_L
            sigma = p.sigma_H if s == 1 else p.sigma_L

            dW = rng.normal(0, dt**0.5)
            X[t + 1] = X[t] * np.exp((mu - 0.5 * sigma**2) * dt + sigma * dW)

            if s == 0 and rng.random() < p.lam * dt:
                regime[t + 1] = 1
            else:
                regime[t + 1] = s

        return {"time": time, "X": X, "regime": regime}

    def value_function_numerical(
        self,
        X_grid: np.ndarray,
        regime: str,
    ) -> np.ndarray:
        """Compute option value on a grid."""
        return np.array([self.option_value(x, regime) for x in X_grid])

    def summary(self) -> dict:
        """Return a summary of model solutions for both regimes."""
        results = {}

        # Regime H
        try:
            X_H, K_H, _B_H = self._solve_regime_H()
            results["H"] = {
                "X_star": X_H,
                "K_star": K_H,
                "investment_cost": self.investment_cost(K_H),
                "npv_at_trigger": self.npv_at_trigger("H"),
                "installed_value_at_trigger": self.installed_value(X_H, K_H, "H"),
                "phi": self._phi("H"),
            }
        except RuntimeError as e:
            results["H"] = {"error": str(e)}

        # Regime L
        X_L, K_L, D_L = self._solve_regime_L()
        C = self._particular_solution_coeff()
        if X_L is not None:
            results["L"] = {
                "X_star": X_L,
                "K_star": K_L,
                "investment_cost": self.investment_cost(K_L),
                "npv_at_trigger": self.installed_value(X_L, K_L, "L")
                - self.investment_cost(K_L),
                "phi": self._phi("L"),
                "D_L": D_L,
                "C": C,
            }
        else:
            results["L"] = {
                "trigger_exists": False,
                "description": (
                    "No interior trigger. Firm waits for regime switch to H."
                ),
                "phi": self._phi("L"),
                "C": C,
                "option_value_formula": "F_L(X) = C * X^beta_H",
            }

        return results

    # ------------------------------------------------------------------
    # Training-inference allocation (phi) extensions
    # ------------------------------------------------------------------

    def _effective_revenue_coeff_single(self, phi: float, K: float) -> float:
        """Compute effective revenue coefficient for a single firm (shares=1).

        A_eff = [(1-phi)*K]^alpha / (r - mu_L + lam)
              + lam / (r - mu_L + lam) * [phi*K]^alpha * A_H

        This combines L-regime inference revenue and H-regime continuation
        value (via regime switch) into a single X-multiplier.
        """
        p = self.params
        lam = p.lam
        inf_cap = (1.0 - phi) * K
        tr_cap = phi * K

        denom_L = p.r - p.mu_L + lam
        if denom_L <= 0:
            return 0.0

        a_eff = inf_cap**p.alpha / denom_L

        if tr_cap > 0 and lam > 0:
            a_eff += lam / denom_L * tr_cap**p.alpha * p.A_H

        return a_eff

    def installed_value_with_phi(
        self, X: float, phi: float, K: float, regime: str = "L"
    ) -> float:
        """Installed value with explicit training fraction.

        H-regime: V = A_H * X * (phi*K)^alpha - delta*K/r
        L-regime: V = A_eff(phi, K) * X - delta*K/r
        """
        p = self.params
        if regime == "H":
            tr_cap = phi * K
            if tr_cap <= 0:
                return -p.delta * K / p.r
            return p.A_H * X * tr_cap**p.alpha - p.delta * K / p.r
        else:
            a_eff = self._effective_revenue_coeff_single(phi, K)
            return a_eff * X - p.delta * K / p.r

    def _objective_K_phi(self, params_vec: np.ndarray) -> float:
        """Negative of option value factor for joint (K, phi) optimization.

        Maximizes h(K, phi) = A_eff^beta_H / cost^(beta_H-1).
        Uses beta_H because investment option value is driven by
        H-regime expectations (same as duopoly model).
        """
        log_K, phi = params_vec
        K = np.exp(log_K)

        if phi <= 0.01 or phi >= 0.99:
            return 1e20

        p = self.params
        beta = p.beta_H

        a_eff = self._effective_revenue_coeff_single(phi, K)
        b = p.delta * K / p.r + p.c * K**p.gamma

        if a_eff <= 0 or b <= 0:
            return 1e20
        return -(beta * np.log(a_eff) - (beta - 1.0) * np.log(b))

    def optimal_trigger_capacity_phi(self) -> tuple[float, float, float]:
        """Solve for optimal (X*, K*, phi*) with training-inference allocation.

        The firm jointly optimizes capacity K and training fraction phi.
        The investment trigger uses beta_H and the combined A_eff coefficient.

        Returns:
            (X*, K*, phi*): Optimal trigger, capacity, and training fraction.
        """
        cache_key = "phi_opt"
        if cache_key in self._cache:
            return self._cache[cache_key]

        p = self.params
        beta = p.beta_H
        best_val = 1e20
        best_params = None

        for log_K_init in [-2, 0, 2]:
            for phi_init in [0.15, 0.30, 0.50, 0.70]:
                x0 = np.array([log_K_init, phi_init])
                try:
                    result = optimize.minimize(
                        self._objective_K_phi,
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
            msg = "Joint (K, phi) optimization failed"
            raise RuntimeError(msg)

        K_star = np.exp(best_params[0])
        phi_star = np.clip(best_params[1], 0.01, 0.99)

        a_eff = self._effective_revenue_coeff_single(phi_star, K_star)
        markup = beta / (beta - 1.0)
        total_cost = p.delta * K_star / p.r + p.c * K_star**p.gamma
        X_star = markup * total_cost / a_eff if a_eff > 0 else np.inf

        self._cache[cache_key] = (X_star, K_star, phi_star)
        return X_star, K_star, phi_star

    def option_value_with_phi(self, X: float) -> float:
        """Option value when the firm optimizes over (K, phi).

        F(X) = B * X^beta_H      for X < X*
        F(X) = V(X, phi*, K*) - I(K*)  for X >= X*
        """
        X_star, K_star, phi_star = self.optimal_trigger_capacity_phi()
        p = self.params
        beta = p.beta_H

        if X_star <= X:
            return self.installed_value_with_phi(
                X, phi_star, K_star, "L"
            ) - self.investment_cost(K_star)

        npv_at_trigger = self.installed_value_with_phi(
            X_star, phi_star, K_star, "L"
        ) - self.investment_cost(K_star)
        if npv_at_trigger <= 0:
            return 0.0
        B = npv_at_trigger / X_star**beta
        return B * X**beta
