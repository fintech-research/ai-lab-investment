"""Exact piecewise free-boundary solution of the L-regime stopping problem.

Verification counterpart to the reduced-form option value used in the paper.
The paper prices the pre-investment L-regime option with the pure power form
F_L(X) = B * X^{beta_H} on the whole continuation region (the
"unconditional-A_eff / smooth-fit" convention, A_1 = 0). That convention is
exact only if the forcing term in the L-regime HJB equals lambda * B_H
X^{beta_H} everywhere. It does not: the H-regime option is exercised above the
H-regime trigger X_H*, so the true forcing is

    lambda * F_H(X) = lambda * B_H * X^{beta_H}                  X < X_H*
                    = lambda * [V_H(X, K_H*) - I(K_H*)]          X > X_H*

and the second branch is affine in X. At the baseline calibration the firm's
own trigger X* ~ 0.0047 lies above X_H* ~ 0.0028, so the exact continuation
problem is genuinely piecewise:

    region 1, 0 < X < X_H*:
        F(X) = A_1 X^{beta_L^+} + C X^{beta_H},  C = -lambda B_H / Q_L(beta_H)
    region 2, X_H* < X < X*:
        F(X) = D_1 X^{beta_L^+} + D_2 X^{beta_L^-} + g X + k
        g = lambda a_H / (r + lambda - mu_L),  k = -lambda b_H / (r + lambda)

with value and slope matched at X_H*, and value matching plus smooth pasting
at the free boundary X*. The negative root is absent from region 1 because
F(0) = 0. Everything is solved at the paper's *full* model (training-inference
allocation phi), so the exercise payoff is A_eff(phi, K) X - delta K / r - I(K)
exactly as in `SingleFirmModel.installed_value_with_phi`.

The module also provides:

- `threshold_value`, the exact value of an arbitrary threshold policy (no
  smooth pasting), which prices the paper's own policy inside the exact model;
- `pure_switching_value`, the value of never exercising in the low regime,
  which is the correct replication lower bound (it is *not* C X^{beta_H}: that
  expression ignores the same exercised-H forcing and overstates the bound);
- `finite_difference_value`, an independent Brennan--Schwartz solve of the
  linear complementarity problem, used to verify the closed-form solution.
"""

from dataclasses import dataclass

import numpy as np
from scipy import optimize

from .base_model import SingleFirmModel
from .parameters import ModelParameters

_BRACKET_EPS = 1e-9


@dataclass(frozen=True)
class PiecewiseSolution:
    """Solution of the exact L-regime free-boundary problem at fixed (K, phi).

    Attributes:
        X_star: Exact investment trigger.
        A_1: Coefficient on X^{beta_L^+} below X_H* (relative to C X^{beta_H}).
        D_1: Coefficient on X^{beta_L^+} above X_H* (0 in the one-region case).
        D_2: Coefficient on X^{beta_L^-} above X_H* (0 in the one-region case).
        K: Capacity the solution is conditioned on.
        phi: Training fraction the solution is conditioned on.
        a_L, b_L: Exercise payoff coefficients, payoff = a_L X - b_L.
        X_H: H-regime trigger separating the two regions.
        C: Particular-solution coefficient below X_H* (eq-particular-C).
        g, k: Particular-solution coefficients above X_H*.
        beta_L_pos, beta_L_neg: Roots of the L-regime characteristic equation.
        beta_H: Positive root of the H-regime characteristic equation.
    """

    X_star: float
    A_1: float
    D_1: float
    D_2: float
    K: float
    phi: float
    a_L: float
    b_L: float
    X_H: float
    C: float
    g: float
    k: float
    beta_L_pos: float
    beta_L_neg: float
    beta_H: float

    @property
    def two_region(self) -> bool:
        """True when the free boundary lies above the H-regime trigger."""
        return self.X_star > self.X_H

    def value(self, X: float) -> float:
        """Option value at demand X."""
        if self.X_star <= X:
            return self.a_L * X - self.b_L
        if X < self.X_H:
            return self.A_1 * X**self.beta_L_pos + self.C * X**self.beta_H
        return (
            self.D_1 * X**self.beta_L_pos
            + self.D_2 * X**self.beta_L_neg
            + self.g * X
            + self.k
        )

    def npv_at_trigger(self) -> float:
        """Net present value of investing at the exact trigger."""
        return self.a_L * self.X_star - self.b_L


class PiecewiseOptionModel:
    """Exact piecewise solution of the low-regime investment option.

    The H-regime sub-problem is the paper's own: after a switch the firm has
    not yet invested, so it solves the absorbing-H problem and installs
    K_H* with all capacity devoted to training (phi_H* = 1, the H-regime
    optimum since inference capacity earns nothing once the switch occurs).
    This is exactly `SingleFirmModel._solve_regime_H`, which also supplies the
    B_H entering the particular-solution coefficient C.
    """

    def __init__(self, params: ModelParameters):
        self.params = params
        self.base = SingleFirmModel(params)
        p = params

        self.X_H, self.K_H, self.B_H = self.base._solve_regime_H()
        self.C = self.base.particular_solution_coeff()
        self.beta_H = p.beta_H
        self.beta_L_pos = p.beta_L
        self.beta_L_neg = _negative_root(p.sigma, p.mu_L, p.r + p.lam)

        # H-regime exercised payoff, affine in X: a_H X - b_H
        self.a_H = p.A_H * self.K_H**p.alpha
        self.b_H = p.delta * self.K_H / p.r + self.base.investment_cost(self.K_H)

        # Particular solution for the affine forcing on (X_H*, X*)
        self.g = p.lam * self.a_H / (p.r + p.lam - p.mu_L)
        self.k = -p.lam * self.b_H / (p.r + p.lam)

    # ------------------------------------------------------------------
    # Payoffs
    # ------------------------------------------------------------------

    def regime_H_option_value(self, X: float) -> float:
        """H-regime option value F_H(X), the L-regime HJB forcing term / lam.

        Equals B_H X^{beta_H} below the H-regime trigger and the exercised
        value a_H X - b_H above it. The paper's reduced form extends the
        first branch to the whole continuation region.
        """
        if X < self.X_H:
            return self.B_H * X**self.beta_H
        return self.a_H * X - self.b_H

    def exercise_payoff_coeffs(self, K: float, phi: float) -> tuple[float, float]:
        """Coefficients (a_L, b_L) of the L-regime exercise payoff a_L X - b_L.

        a_L is the unconditional effective revenue coefficient A_eff(phi, K)
        of eq-a-eff and b_L is the operating-cost perpetuity plus I(K), so the
        payoff coincides with `installed_value_with_phi(X, phi, K, "L")` net
        of the investment cost.
        """
        p = self.params
        a_L = self.base._effective_revenue_coeff_single(phi, K)
        b_L = p.delta * K / p.r + self.base.investment_cost(K)
        return a_L, b_L

    # ------------------------------------------------------------------
    # Free-boundary solution
    # ------------------------------------------------------------------

    def solve(self, K: float, phi: float) -> PiecewiseSolution | None:
        """Solve the exact free-boundary problem at fixed (K, phi).

        Tries the one-region case (free boundary below X_H*, where the pure
        power forcing is exact) first; falls back to the two-region case with
        C^1 matching at X_H*.

        Returns:
            The solution, or None when no finite trigger exists (the firm
            never exercises before the regime switch).
        """
        one = self._solve_one_region(K, phi)
        if one is not None:
            return one
        return self._solve_two_region(K, phi)

    def _solve_one_region(self, K: float, phi: float) -> PiecewiseSolution | None:
        """Free boundary strictly below X_H*, where F = A_1 X^p + C X^h."""
        a_L, b_L = self.exercise_payoff_coeffs(K, phi)
        p_pos, h, C = self.beta_L_pos, self.beta_H, self.C

        def gap(X: float) -> float:
            # Smooth pasting eliminates A_1; what remains is value matching.
            return -a_L * X * (1.0 - 1.0 / p_pos) + C * X**h * (1.0 - h / p_pos) + b_L

        grid = np.geomspace(self.X_H * 1e-6, self.X_H * (1.0 - _BRACKET_EPS), 400)
        vals = np.array([gap(x) for x in grid])
        sign_change = np.where(np.sign(vals[:-1]) != np.sign(vals[1:]))[0]
        if len(sign_change) == 0:
            return None
        i = int(sign_change[0])
        X_star = float(optimize.brentq(gap, grid[i], grid[i + 1], xtol=1e-18))
        A_1 = (a_L * X_star - h * C * X_star**h) / (p_pos * X_star**p_pos)
        return self._make_solution(K, phi, X_star, A_1, 0.0, 0.0, a_L, b_L)

    def _solve_two_region(self, K: float, phi: float) -> PiecewiseSolution | None:
        """Free boundary above X_H*, with C^1 matching at X_H*."""
        a_L, b_L = self.exercise_payoff_coeffs(K, phi)

        def residual(X: float) -> float:
            return self._slope_mismatch(X, a_L, b_L)

        lo = self.X_H * (1.0 + _BRACKET_EPS)
        hi = self.X_H * 1e5
        if residual(lo) * residual(hi) > 0:
            return None
        X_star = float(optimize.brentq(residual, lo, hi, xtol=1e-18, rtol=8.9e-16))
        A_1, D_1, D_2 = self._upper_coeffs(X_star, a_L, b_L)
        return self._make_solution(K, phi, X_star, A_1, D_1, D_2, a_L, b_L)

    def _upper_coeffs(
        self, X_star: float, a_L: float, b_L: float
    ) -> tuple[float, float, float]:
        """Coefficients (A_1, D_1, D_2) implied by a candidate boundary X*.

        Value matching and smooth pasting at X* give a 2x2 linear system in
        (D_1, D_2); value matching at X_H* then gives A_1. The remaining
        condition, slope matching at X_H*, is the residual root-searched on.
        """
        p_pos, n, h = self.beta_L_pos, self.beta_L_neg, self.beta_H
        M = np.array([
            [X_star**p_pos, X_star**n],
            [p_pos * X_star ** (p_pos - 1.0), n * X_star ** (n - 1.0)],
        ])
        rhs = np.array([a_L * X_star - b_L - self.g * X_star - self.k, a_L - self.g])
        D_1, D_2 = np.linalg.solve(M, rhs)
        X_H = self.X_H
        A_1 = (
            D_1 * X_H**p_pos + D_2 * X_H**n + self.g * X_H + self.k - self.C * X_H**h
        ) / X_H**p_pos
        return float(A_1), float(D_1), float(D_2)

    def _slope_mismatch(self, X_star: float, a_L: float, b_L: float) -> float:
        """Slope mismatch at X_H* for a candidate free boundary X*."""
        p_pos, n, h = self.beta_L_pos, self.beta_L_neg, self.beta_H
        A_1, D_1, D_2 = self._upper_coeffs(X_star, a_L, b_L)
        X_H = self.X_H
        lower = p_pos * A_1 * X_H ** (p_pos - 1.0) + h * self.C * X_H ** (h - 1.0)
        upper = p_pos * D_1 * X_H ** (p_pos - 1.0) + n * D_2 * X_H ** (n - 1.0) + self.g
        return lower - upper

    def _make_solution(
        self,
        K: float,
        phi: float,
        X_star: float,
        A_1: float,
        D_1: float,
        D_2: float,
        a_L: float,
        b_L: float,
    ) -> PiecewiseSolution:
        return PiecewiseSolution(
            X_star=X_star,
            A_1=A_1,
            D_1=D_1,
            D_2=D_2,
            K=K,
            phi=phi,
            a_L=a_L,
            b_L=b_L,
            X_H=self.X_H,
            C=self.C,
            g=self.g,
            k=self.k,
            beta_L_pos=self.beta_L_pos,
            beta_L_neg=self.beta_L_neg,
            beta_H=self.beta_H,
        )

    # ------------------------------------------------------------------
    # Sub-optimal threshold policies and the replication bound
    # ------------------------------------------------------------------

    def threshold_value(self, K: float, phi: float, X_stop: float, X: float) -> float:
        """Exact value of the policy "invest at X_stop with (K, phi)".

        Same ODEs as `solve`, but only value matching is imposed at X_stop
        (smooth pasting holds only at the optimal boundary). This prices the
        paper's own reduced-form policy inside the exact model.
        """
        a_L, b_L = self.exercise_payoff_coeffs(K, phi)
        if X_stop <= X:
            return a_L * X - b_L

        p_pos, n, h = self.beta_L_pos, self.beta_L_neg, self.beta_H
        X_H = self.X_H
        if X_stop <= X_H:
            A_1 = (a_L * X_stop - b_L - self.C * X_stop**h) / X_stop**p_pos
            return A_1 * X**p_pos + self.C * X**h

        M = np.array([
            [X_H**p_pos, -(X_H**p_pos), -(X_H**n)],
            [
                p_pos * X_H ** (p_pos - 1.0),
                -p_pos * X_H ** (p_pos - 1.0),
                -n * X_H ** (n - 1.0),
            ],
            [0.0, X_stop**p_pos, X_stop**n],
        ])
        rhs = np.array([
            self.g * X_H + self.k - self.C * X_H**h,
            self.g - h * self.C * X_H ** (h - 1.0),
            a_L * X_stop - b_L - self.g * X_stop - self.k,
        ])
        A_1, D_1, D_2 = np.linalg.solve(M, rhs)
        if X < X_H:
            return float(A_1 * X**p_pos + self.C * X**h)
        return float(D_1 * X**p_pos + D_2 * X**n + self.g * X + self.k)

    def pure_switching_value(self, X: float) -> float:
        """Value of never exercising in the low regime (replication bound).

        The firm waits for the regime switch and then holds the H-regime
        option. The value solves the same piecewise ODE with no L-regime
        exercise boundary; the no-bubble condition kills X^{beta_L^+} above
        X_H*, and value and slope matching at X_H* pin the remaining two
        coefficients. This is the correct lower bound for F_L. It lies
        strictly *below* C X^{beta_H}, because the exercised H-regime payoff
        is below the extrapolated option power B_H X^{beta_H} above X_H*.
        """
        A_w, D_w = self.pure_switching_coeffs()
        p_pos, n, h = self.beta_L_pos, self.beta_L_neg, self.beta_H
        if X < self.X_H:
            return A_w * X**p_pos + self.C * X**h
        return D_w * X**n + self.g * X + self.k

    def pure_switching_coeffs(self) -> tuple[float, float]:
        """Coefficients (A_w, D_w) of the pure-switching value function."""
        p_pos, n, h, X_H = self.beta_L_pos, self.beta_L_neg, self.beta_H, self.X_H
        M = np.array([
            [X_H**p_pos, -(X_H**n)],
            [p_pos * X_H ** (p_pos - 1.0), -n * X_H ** (n - 1.0)],
        ])
        rhs = np.array([
            self.g * X_H + self.k - self.C * X_H**h,
            self.g - h * self.C * X_H ** (h - 1.0),
        ])
        A_w, D_w = np.linalg.solve(M, rhs)
        return float(A_w), float(D_w)

    # ------------------------------------------------------------------
    # Re-optimization of (K, phi) inside the exact model
    # ------------------------------------------------------------------

    def optimal_policy(self, X_0: float) -> PiecewiseSolution | None:
        """Re-optimize (K, phi) for the exact problem at demand X_0.

        Maximizes the exact option value at X_0 with the same multi-start
        Nelder-Mead pattern as `SingleFirmModel.optimal_trigger_capacity_phi`.
        Unlike the reduced form, the exact problem is not scale-free — X_H*
        fixes a scale — so the optimal policy is stated at a demand level.
        Within the region below X_H* the exact value is
        A_1 X^{beta_L^+} + C X^{beta_H} with C independent of (K, phi), so
        the ranking of policies whose triggers exceed X_0 is the ranking of
        the exercise premium A_1 and is the same for every such X_0;
        maximizing A_1 itself is not well posed, because A_1 diverges along
        sequences whose trigger collapses below X_0.
        """
        try:
            _, K_ref, phi_ref = self.base.optimal_trigger_capacity_phi()
            log_K_ref = float(np.log(K_ref))
        except (ValueError, RuntimeError):
            log_K_ref, phi_ref = -5.0, 0.50

        best_val = 1e20
        best: tuple[float, float] | None = None
        starts = [log_K_ref + d for d in (-3.0, -1.5, 0.0, 1.5)]
        for log_K_init in starts:
            for phi_init in [0.15, 0.40, float(phi_ref)]:
                result = optimize.minimize(
                    self._neg_value,
                    np.array([log_K_init, phi_init]),
                    method="Nelder-Mead",
                    args=(X_0,),
                    options={"maxiter": 3000, "xatol": 1e-12, "fatol": 1e-18},
                )
                if result.fun < best_val:
                    best_val = result.fun
                    best = (float(result.x[0]), float(result.x[1]))
        if best is None or best_val >= 1e19:
            return None
        K = float(np.exp(best[0]))
        phi = float(np.clip(best[1], 0.01, 0.99))
        return self.solve(K, phi)

    def _neg_value(self, params_vec: np.ndarray, X_0: float) -> float:
        """Negative exact option value at X_0 for a candidate (K, phi)."""
        log_K, phi = params_vec
        if log_K < -15.0 or log_K > 15.0 or phi <= 0.01 or phi >= 0.99:
            return 1e20
        sol = self.solve(float(np.exp(log_K)), float(phi))
        if sol is None:
            return 1e20
        return -sol.value(X_0)

    # ------------------------------------------------------------------
    # Independent numerical verification
    # ------------------------------------------------------------------

    def finite_difference_value(
        self,
        K: float,
        phi: float,
        n_grid: int = 20001,
        x_min: float = 1e-7,
        x_max: float = 5.0,
    ) -> tuple[np.ndarray, np.ndarray, float]:
        """Brennan--Schwartz solve of the same stopping problem.

        Discretizes the L-regime HJB in log demand and solves the linear
        complementarity problem exactly (the exercise region is the upper set
        [X*, inf), so the projected back-substitution is exact). Independent
        of the closed-form algebra above and used to verify it.

        Returns:
            (X grid, option values, estimated free boundary).
        """
        p = self.params
        a_L, b_L = self.exercise_payoff_coeffs(K, phi)
        y = np.linspace(np.log(x_min), np.log(x_max), n_grid)
        dy = y[1] - y[0]
        X = np.exp(y)

        s2 = 0.5 * p.sigma**2
        sub = -(s2 / dy**2 - (p.mu_L - s2) / (2.0 * dy))
        diag = 2.0 * s2 / dy**2 + (p.r + p.lam)
        sup = -(s2 / dy**2 + (p.mu_L - s2) / (2.0 * dy))

        payoff = a_L * X - b_L
        forcing = p.lam * np.where(
            X < self.X_H, self.B_H * X**self.beta_H, self.a_H * X - self.b_H
        )  # vectorized regime_H_option_value

        A = np.full(n_grid, sub)
        B = np.full(n_grid, diag)
        Cc = np.full(n_grid, sup)
        D = forcing.copy()
        B[0], Cc[0], D[0] = 1.0, 0.0, 0.0
        B[-1], A[-1], D[-1] = 1.0, 0.0, payoff[-1]

        c_prime = np.empty(n_grid)
        d_prime = np.empty(n_grid)
        c_prime[0] = Cc[0] / B[0]
        d_prime[0] = D[0] / B[0]
        for i in range(1, n_grid):
            den = B[i] - A[i] * c_prime[i - 1]
            c_prime[i] = Cc[i] / den
            d_prime[i] = (D[i] - A[i] * d_prime[i - 1]) / den

        F = np.empty(n_grid)
        F[-1] = max(d_prime[-1], payoff[-1])
        for i in range(n_grid - 2, -1, -1):
            F[i] = max(d_prime[i] - c_prime[i] * F[i + 1], payoff[i])

        exercised = (payoff + 1e-18 >= F) & (payoff > 0.0)
        boundary = float(X[np.argmax(exercised)]) if exercised.any() else float("inf")
        return X, F, boundary


def _negative_root(sigma: float, mu: float, discount: float) -> float:
    """Negative root of (sigma^2/2) b (b-1) + mu b - discount = 0."""
    a = 0.5 * sigma**2
    b = mu - 0.5 * sigma**2
    return (-b - (b**2 + 4.0 * a * discount) ** 0.5) / (2.0 * a)


# ----------------------------------------------------------------------
# Reduced-form reference and bias measurement
# ----------------------------------------------------------------------


def reduced_form_reference(params: ModelParameters) -> dict[str, float]:
    """Reduced-form (paper) solution: trigger, policy, and smooth-fit level.

    The smooth-fit coefficient is B = [V(X*, K*, phi*) - I(K*)] / (X*)^{beta_H},
    the level the paper prices the pre-investment option with. It differs from
    the forced-ODE particular coefficient C of eq-particular-C.
    """
    model = SingleFirmModel(params)
    X_star, K_star, phi_star = model.optimal_trigger_capacity_phi()
    a_L = model._effective_revenue_coeff_single(phi_star, K_star)
    b_L = params.delta * K_star / params.r + model.investment_cost(K_star)
    npv = a_L * X_star - b_L
    return {
        "X_star": X_star,
        "K_star": K_star,
        "phi_star": phi_star,
        "a_L": a_L,
        "b_L": b_L,
        "npv_at_trigger": npv,
        "smooth_fit_coeff": npv / X_star**params.beta_H,
        "C": model.particular_solution_coeff(),
    }


def smooth_fit_trigger(params: ModelParameters, K: float, phi: float) -> float:
    """Reduced-form trigger from the pure-power boundary conditions.

    Solves value matching and smooth pasting at fixed (K, phi) with the
    continuation value B X^{beta_H}, B free and A_1 = 0 — the paper's
    convention. Root-found rather than substituted in closed form so that the
    boundary-condition algebra is exercised; the answer must reproduce
    eq-trigger-phi, beta_H/(beta_H - 1) * b(K) / A_eff(phi, K).
    """
    model = SingleFirmModel(params)
    a_L = model._effective_revenue_coeff_single(phi, K)
    b_L = params.delta * K / params.r + model.investment_cost(K)
    h = params.beta_H

    def gap(X: float) -> float:
        # B eliminated with smooth pasting; what remains is value matching.
        return a_L * X * (1.0 / h - 1.0) + b_L

    lo = b_L / a_L * 1e-6
    hi = b_L / a_L * 1e6
    return float(optimize.brentq(gap, lo, hi, xtol=1e-18))


def piecewise_bias(
    params: ModelParameters | None = None,
    x0_ratio: float = 0.5,
    reoptimize: bool = True,
) -> dict[str, float]:
    """Compare the reduced-form and exact solutions at one calibration.

    Args:
        params: Model parameters (baseline calibration when None).
        x0_ratio: Evaluation demand as a fraction of the reduced-form
            trigger. The default 0.5 matches the reference level used by
            `ValuationAnalysis.dario_dilemma`.
        reoptimize: Also re-optimize (K, phi) inside the exact model.

    Returns:
        Dict of triggers, values, and relative biases. Percentage keys are
        relative deviations of the exact solution from the reduced form
        (positive = the reduced form is too low).
    """
    if params is None:
        params = ModelParameters()

    rf = reduced_form_reference(params)
    pw = PiecewiseOptionModel(params)
    X_0 = x0_ratio * rf["X_star"]

    fixed = pw.solve(rf["K_star"], rf["phi_star"])
    if fixed is None:
        msg = "No exact trigger at fixed reduced-form policy"
        raise RuntimeError(msg)

    value_rf = rf["smooth_fit_coeff"] * X_0**params.beta_H
    value_fixed = fixed.value(X_0)
    value_rf_policy = pw.threshold_value(
        rf["K_star"], rf["phi_star"], rf["X_star"], X_0
    )

    out = {
        "X_H": pw.X_H,
        "X_0": X_0,
        "C": pw.C,
        "smooth_fit_coeff": rf["smooth_fit_coeff"],
        "X_star_reduced": rf["X_star"],
        "K_reduced": rf["K_star"],
        "phi_reduced": rf["phi_star"],
        "X_star_piecewise_fixed": fixed.X_star,
        "trigger_bias_fixed_pct": 100.0 * (fixed.X_star / rf["X_star"] - 1.0),
        "A_1": fixed.A_1,
        "A_1_pure_switching": pw.pure_switching_coeffs()[0],
        "value_reduced": value_rf,
        "value_piecewise_fixed": value_fixed,
        "value_bias_fixed_pct": 100.0 * (value_fixed / value_rf - 1.0),
        "value_reduced_policy_exact": value_rf_policy,
        "reported_value_bias_pct": 100.0 * (value_rf / value_rf_policy - 1.0),
    }

    if reoptimize:
        opt = pw.optimal_policy(X_0)
        if opt is not None:
            value_opt = opt.value(X_0)
            out.update({
                "X_star_piecewise_opt": opt.X_star,
                "K_piecewise_opt": opt.K,
                "phi_piecewise_opt": opt.phi,
                "trigger_bias_opt_pct": 100.0 * (opt.X_star / rf["X_star"] - 1.0),
                "K_bias_opt_pct": 100.0 * (opt.K / rf["K_star"] - 1.0),
                "phi_bias_opt_pct": 100.0 * (opt.phi / rf["phi_star"] - 1.0),
                "value_piecewise_opt": value_opt,
                "value_bias_opt_pct": 100.0 * (value_opt / value_rf - 1.0),
                "policy_loss_pct": 100.0 * (1.0 - value_rf_policy / value_opt),
            })
    return out


def bias_sweep(
    param_name: str,
    values: np.ndarray,
    base_params: ModelParameters | None = None,
    x0_ratio: float = 0.5,
    reoptimize: bool = True,
) -> dict[str, np.ndarray]:
    """Piecewise-vs-reduced-form bias across a parameter range.

    Parameterizations where either model has no interior solution are
    silently skipped (NaN entries), matching `comparative_statics`.
    """
    if base_params is None:
        base_params = ModelParameters()

    keys = [
        "trigger_bias_fixed_pct",
        "value_bias_fixed_pct",
        "reported_value_bias_pct",
        "trigger_bias_opt_pct",
        "value_bias_opt_pct",
        "policy_loss_pct",
        "X_star_reduced",
        "X_H",
    ]
    out: dict[str, np.ndarray] = {k: np.full(len(values), np.nan) for k in keys}
    out["param_values"] = np.asarray(values, dtype=float)

    for i, val in enumerate(values):
        try:
            params = base_params.with_param(**{param_name: float(val)})
            res = piecewise_bias(params, x0_ratio=x0_ratio, reoptimize=reoptimize)
        except (ValueError, RuntimeError, np.linalg.LinAlgError):
            continue
        for key in keys:
            if key in res:
                out[key][i] = res[key]
    return out


def dilemma_bias(
    params: ModelParameters | None = None,
    lambda_true: float = 0.10,
    lambda_invest_values: tuple[float, ...] = (0.02, 0.05, 0.20, 0.35, 0.50),
    x0_ratio: float = 0.5,
) -> dict[str, list[float]]:
    """Recompute Dario's dilemma with exact piecewise valuation.

    The paper's evaluator discounts the mismatched policy's NPV with the
    reduced-form timing factor (X_0/X*)^{beta_H}. Here each belief's policy is
    obtained by solving the exact problem under that belief, and both policies
    are then valued exactly under the *true* arrival rate with
    `threshold_value`. The reference demand is the paper's own,
    X_0 = x0_ratio * min(X*, X*_mis) with reduced-form triggers (the paper
    uses x0_ratio = 0.5), so that both columns are evaluated at the same
    demand level.
    """
    if params is None:
        params = ModelParameters()

    from .valuation import ValuationAnalysis

    va = ValuationAnalysis(params)
    p_true = params.with_param(lam=lambda_true)
    pw_true = PiecewiseOptionModel(p_true)
    rf_true = reduced_form_reference(p_true)

    out: dict[str, list[float]] = {
        "lambda_invest": [],
        "loss_reduced_pct": [],
        "loss_piecewise_pct": [],
        "phi_reduced": [],
        "phi_piecewise": [],
    }
    for lam_i in lambda_invest_values:
        rf = va.dario_dilemma(lambda_true, lam_i)
        p_i = params.with_param(lam=lam_i)
        X_0 = x0_ratio * min(rf_true["X_star"], reduced_form_reference(p_i)["X_star"])
        opt_true = pw_true.optimal_policy(X_0)
        opt_i = PiecewiseOptionModel(p_i).optimal_policy(X_0)
        if opt_true is None or opt_i is None:
            continue
        v_opt = pw_true.threshold_value(opt_true.K, opt_true.phi, opt_true.X_star, X_0)
        v_mis = pw_true.threshold_value(opt_i.K, opt_i.phi, opt_i.X_star, X_0)
        out["lambda_invest"].append(lam_i)
        out["loss_reduced_pct"].append(100.0 * rf["value_loss_pct"])
        out["loss_piecewise_pct"].append(100.0 * (v_opt - v_mis) / v_opt)
        out["phi_reduced"].append(rf["phi_mismatch"])
        out["phi_piecewise"].append(opt_i.phi)
    return out


def format_bias_report(params: ModelParameters | None = None) -> str:
    """Human-readable report of the piecewise-vs-reduced-form comparison."""
    if params is None:
        params = ModelParameters()
    b = piecewise_bias(params)
    nan = float("nan")
    opt = {
        key: b.get(key, nan)
        for key in (
            "trigger_bias_opt_pct",
            "K_bias_opt_pct",
            "phi_bias_opt_pct",
            "value_bias_opt_pct",
            "policy_loss_pct",
        )
    }
    lines = [
        "Piecewise stopping bias vs. reduced-form model",
        "=" * 62,
        f"X_H* (H-regime trigger)      {b['X_H']:.6f}",
        f"X_0 (evaluation demand)      {b['X_0']:.6f}",
        f"C (forced-ODE coefficient)   {b['C']:.4f}",
        f"smooth-fit coefficient       {b['smooth_fit_coeff']:.4f}",
        "",
        "Fixed reduced-form policy (K*, phi*)",
        f"  trigger reduced / exact    {b['X_star_reduced']:.6f} / "
        f"{b['X_star_piecewise_fixed']:.6f}",
        f"  trigger bias               {b['trigger_bias_fixed_pct']:+.2f}%",
        f"  option value reduced/exact {b['value_reduced']:.6e} / "
        f"{b['value_piecewise_fixed']:.6e}",
        f"  value bias                 {b['value_bias_fixed_pct']:+.2f}%",
        f"  exact value of the paper's own policy "
        f"{b['value_reduced_policy_exact']:.6e}",
        f"  reduced-form formula error {b['reported_value_bias_pct']:+.2f}%",
        "",
        "Re-optimized inside the exact model",
        f"  trigger bias               {opt['trigger_bias_opt_pct']:+.2f}%",
        f"  capacity bias              {opt['K_bias_opt_pct']:+.2f}%",
        f"  training fraction bias     {opt['phi_bias_opt_pct']:+.4f}%",
        f"  value bias                 {opt['value_bias_opt_pct']:+.2f}%",
        f"  value loss of the paper's policy {opt['policy_loss_pct']:.2f}%",
    ]
    return "\n".join(lines)


#: Robustness ranges of Internet Appendix B (the (A2)-admissible ranges).
APPENDIX_B_RANGES: dict[str, tuple[float, float]] = {
    "sigma": (0.20, 0.38),
    "alpha": (0.37, 0.53),
    "gamma": (1.15, 2.00),
    "lam": (0.01, 0.50),
    "r": (0.10, 0.13),
}


def format_sweep_report(
    ranges: dict[str, tuple[float, float]] | None = None,
    n_points: int = 9,
) -> str:
    """Min/max bias over the Internet Appendix B robustness ranges."""
    if ranges is None:
        ranges = APPENDIX_B_RANGES
    keys = [
        ("trigger_bias_fixed_pct", "trigger bias, fixed policy"),
        ("value_bias_fixed_pct", "value bias, fixed policy"),
        ("reported_value_bias_pct", "reduced-form formula error"),
        ("trigger_bias_opt_pct", "trigger bias, re-optimized"),
        ("policy_loss_pct", "value loss of the paper's policy"),
    ]
    lines = ["Bias across the Internet Appendix B ranges", "=" * 62]
    for name, (lo, hi) in ranges.items():
        sweep = bias_sweep(name, np.linspace(lo, hi, n_points))
        lines.append(f"{name} in [{lo}, {hi}]")
        for key, label in keys:
            vals = sweep[key][~np.isnan(sweep[key])]
            if len(vals) == 0:
                continue
            lines.append(f"  {label:34s} {vals.min():+8.2f}% .. {vals.max():+8.2f}%")
    return "\n".join(lines)


if __name__ == "__main__":  # pragma: no cover
    import sys

    print(format_bias_report())
    if "sweep" in sys.argv[1:]:
        print()
        print(format_sweep_report())
