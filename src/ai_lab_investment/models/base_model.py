"""Single-firm optimal investment model with regime-switching demand.

Solves for the optimal investment trigger X* and capacity K* under:
- Regime-switching GBM demand (Guo, Miao & Morellec 2005)
- Diminishing returns to compute (scaling laws)
- Convex investment costs
- Training-inference allocation (phi) as a strategic variable

No-post-AGI-entry assumption (F_H = 0):
  If the firm has not invested when the regime switch occurs, it is
  permanently locked out. This "winner-take-all" assumption captures
  the adoption race: a firm must have trained a model in place before
  transformative AI arrives, or it is years behind and excluded.

  Consequence: the L-regime option value satisfies a *homogeneous*
  Euler ODE with effective discount r + lambda_tilde, yielding the
  single-term solution F_L(X) = A_1 * X^{beta_L^+}.

  The arrival rate lambda_tilde enters the trigger through TWO channels:
    1. A_eff channel: higher lambda_tilde raises A_eff, lowering the trigger.
    2. Option premium channel: higher lambda_tilde raises beta_L^+,
       pushing beta_L^+/(beta_L^+ - 1) toward 1 --- the value of waiting
       shrinks because delay risks permanent exclusion.

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
    Under the no-post-AGI-entry assumption, F_H(X) = 0: a firm that has
    not invested when the regime switch occurs is permanently excluded.
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

        For regime H (standalone): exists when 1/gamma < Phi < 1, where
        Phi = (1-1/beta_H)/alpha.

        For regime L (under F_H = 0): exists when the K-optimization has
        an interior solution, requiring alpha > 1 - 1/beta_L. This replaces
        condition (A3) from the old model. When this fails, the option
        premium beta_L/(beta_L-1) is too low relative to the revenue
        elasticity alpha to support an interior capacity level.
        """
        p = self.params
        if regime == "L":
            # Under F_H = 0, the capacity optimization exponent is
            # beta_L*(alpha-1) + 1. Interior K* requires this > 0,
            # equivalently alpha > 1 - 1/beta_L.
            return p.alpha > 1.0 - 1.0 / p.beta_L
        Phi = self._option_premium_ratio(regime)
        return 1.0 / p.gamma < Phi < 1.0

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

    def _solve_regime_L(self) -> tuple[float, float, float]:
        """Solve for the L-regime investment option via joint (K, phi) optimization.

        Under F_H = 0, the L-regime HJB is homogeneous:
            (1/2) sigma_L^2 X^2 F_L'' + mu_L X F_L' - (r + lam) F_L = 0

        Solution: F_L(X) = A_1 * X^{beta_L^+}, where beta_L^+ is the
        positive root of the characteristic equation with discount r + lam.

        The firm jointly optimizes capacity K and training fraction phi,
        using A_eff(phi, K) as the revenue coefficient:
            X* = [beta_L^+/(beta_L^+ - 1)] * cost(K*) / A_eff(phi*, K*)

        Returns:
            (X_L*, K_L*, A_1): Trigger, capacity, and option value coefficient.

        Raises:
            RuntimeError: If optimization fails.
        """
        if "L" in self._cache:
            return self._cache["L"]

        X_star, K_star, phi_star = self.optimal_trigger_capacity_phi()

        # A_1 from value-matching: A_1 * X*^{beta_L} = V(X*, phi*, K*) - I(K*)
        p = self.params
        npv = self.installed_value_with_phi(
            X_star, phi_star, K_star, "L"
        ) - self.investment_cost(K_star)
        A_1 = npv / X_star**p.beta_L if X_star > 0 and npv > 0 else 0.0

        self._cache["L"] = (X_star, K_star, A_1)
        return X_star, K_star, A_1

    def optimal_trigger_and_capacity(self, regime: str) -> tuple[float, float]:
        """Solve for optimal trigger X* and capacity K*.

        Args:
            regime: 'L' or 'H'. Note: under F_H = 0, the H-regime
                standalone problem is still well-defined but is not
                used by the main model.

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
            return X_star, K_star

    def _solve_regime_H(self) -> tuple[float, float, float]:
        """Solve for X_H*, K_H*, B_H in the absorbing high regime.

        This computes the standalone H-regime investment problem.
        Under the no-post-AGI-entry assumption (F_H = 0), this solution
        is NOT used by the L-regime option value. It is retained for
        comparative statics and pedagogical figures.

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

    def option_value_H(self, X: float) -> float:
        """Option value in regime H (absorbing).

        Under the no-post-AGI-entry assumption, F_H(X) = 0: a firm
        that has not invested when the regime switch occurs is permanently
        excluded. This method returns 0 for all X.
        """
        return 0.0

    def option_value_L(self, X: float) -> float:
        """Option value in regime L with optimal (K, phi) allocation.

        Under F_H = 0, the L-regime option value is the single-term
        homogeneous solution with joint (K, phi) optimization:
            F_L(X) = A_1 * X^{beta_L^+}            for X < X*
            F_L(X) = V(X, phi*, K*) - I(K*)         for X >= X*

        Returns 0 if no interior capacity solution exists (alpha too low
        relative to beta_L).
        """
        if not self.has_interior_trigger("L"):
            return 0.0

        X_star, K_star, A_1 = self._solve_regime_L()
        _, _, phi_star = self.optimal_trigger_capacity_phi()
        p = self.params

        if X_star <= X:
            return self.installed_value_with_phi(
                X, phi_star, K_star, "L"
            ) - self.investment_cost(K_star)
        return A_1 * X**p.beta_L

    def option_value(self, X: float, regime: str) -> float:
        """Option value in the specified regime."""
        if regime == "H":
            return self.option_value_H(X)
        return self.option_value_L(X)

    def npv_at_trigger(self, regime: str) -> float:
        """NPV of investment at the optimal trigger."""
        if regime == "L":
            X_star, K_star, phi_star = self.optimal_trigger_capacity_phi()
            return self.installed_value_with_phi(
                X_star, phi_star, K_star, "L"
            ) - self.investment_cost(K_star)
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

        # Regime H (standalone, for reference)
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

        # Regime L (main model under F_H = 0, joint K and phi optimization)
        try:
            X_L, K_L, A_1 = self._solve_regime_L()
            _, _, phi_star = self.optimal_trigger_capacity_phi()
            results["L"] = {
                "X_star": X_L,
                "K_star": K_L,
                "phi_star": phi_star,
                "investment_cost": self.investment_cost(K_L),
                "npv_at_trigger": self.installed_value_with_phi(X_L, phi_star, K_L, "L")
                - self.investment_cost(K_L),
                "option_premium_ratio": self._option_premium_ratio("L"),
                "A_1": A_1,
                "option_value_formula": "F_L(X) = A_1 * X^beta_L",
            }
        except RuntimeError as e:
            results["L"] = {"error": str(e)}

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

        Maximizes h(K, phi) = A_eff^{beta_L} / cost^{beta_L - 1}.
        Uses beta_L (the L-regime characteristic root with discount r + lam)
        because under F_H = 0, the investment option value is governed by
        L-regime dynamics with the regime-switch hazard acting as
        additional discount.
        """
        log_K, phi = params_vec
        K = np.exp(log_K)

        if phi <= 0.01 or phi >= 0.99:
            return 1e20

        p = self.params
        beta = p.beta_L

        a_eff = self._effective_revenue_coeff_single(phi, K)
        b = p.delta * K / p.r + p.c * K**p.gamma

        if a_eff <= 0 or b <= 0:
            return 1e20
        return -(beta * np.log(a_eff) - (beta - 1.0) * np.log(b))

    def optimal_trigger_capacity_phi(self) -> tuple[float, float, float]:
        """Solve for optimal (X*, K*, phi*) with training-inference allocation.

        The firm jointly optimizes capacity K and training fraction phi.
        The investment trigger uses beta_L^+ and the combined A_eff coefficient.

        Returns:
            (X*, K*, phi*): Optimal trigger, capacity, and training fraction.

        Raises:
            RuntimeError: If no interior capacity solution exists.
                Under F_H = 0, requires alpha > 1 - 1/beta_L.
        """
        cache_key = "phi_opt"
        if cache_key in self._cache:
            return self._cache[cache_key]

        p = self.params
        if not self.has_interior_trigger("L"):
            threshold = 1.0 - 1.0 / p.beta_L
            msg = (
                f"No interior capacity solution under F_H = 0. "
                f"Need alpha > {threshold:.4f} (got alpha = {p.alpha:.2f}). "
                f"The K-optimization exponent beta_L*(alpha-1)+1 = "
                f"{p.beta_L * (p.alpha - 1) + 1:.4f} must be positive."
            )
            raise RuntimeError(msg)

        beta = p.beta_L
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

        F(X) = B * X^{beta_L}      for X < X*
        F(X) = V(X, phi*, K*) - I(K*)  for X >= X*
        """
        X_star, K_star, phi_star = self.optimal_trigger_capacity_phi()
        p = self.params
        beta = p.beta_L

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
