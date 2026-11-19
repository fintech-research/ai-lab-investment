"""Capability-stock and late-entry prototypes of the pre-switch investment problem.

Research prototype for issue #174. It is not wired into the pipeline and no
number in the paper depends on it. The question is whether a minimal change
of primitives makes investment *before* the regime switch, and training before
the switch, optimal in the properly solved stopping problem, where the paper's
own exact benchmark (`piecewise_option.py`, unrestricted post-switch scale)
prefers to wait at the baseline calibration.

Common environment (unchanged from the paper)
---------------------------------------------
Demand X is a GBM with drift mu_L before the switch and mu_H after; the switch
arrives at rate lam and is absorbing; the discount rate is r. A firm installs
one irreversible lump K at cost c K^gamma (plus a fixed cost f, zero in the
paper), pays delta K forever, and fixes the training fraction phi at
installation. Before the switch an installed firm earns X [(1 - phi) K]^alpha.

State variables: X and the regime, plus (K, phi) once installed. Committed at
installation: K and phi. Revisable: only what a specification says below.

The family
----------
Four primitives are added; the paper's exact problem is the default of each.

``theta`` in [0, 1]
    A firm with no capacity when the switch arrives keeps the H-regime
    investment option with probability theta (it is shut out otherwise).
``late_training`` = kappa_E in [0, 1]
    Capability an entrant builds after the switch is worth kappa_E per unit
    of compute, so its H revenue is X (kappa_E K)^alpha = vartheta X K^alpha
    with vartheta = kappa_E^alpha.
``redeploy`` = kappa_I in [0, 1]
    An installed firm's post-switch capability is
    Z = phi K + kappa_I (1 - phi) K: training capacity in place at the switch
    counts in full, and inference capacity redeployed to training after the
    switch counts at the rate kappa_I. Its H revenue is X Z^alpha.
``fixed_cost`` = f >= 0
    Installation costs f + c K^gamma.
``accumulating``
    Capability is the stock Z_t = zeta * phi K * (time since installation),
    see Specification 3.

With F_H the paper's unrestricted absorbing-H option (scale chosen at
exercise, all capacity trains), the claim held at the switch by a firm that
has not installed is ``theta * F_H(vartheta X)``.

Specification 2 (late-entry discount; issue text): theta < 1, the rest as in
the paper. theta = 1 is the paper's exact problem.

Specification 1 (pre-positioned capability; Fable's version made complete):
kappa_E = kappa_I = kappa, theta = 1. One technology parameter says how much
capability built after the switch is worth relative to capability in place
when it arrives, for incumbents and entrants alike. The "remainder" (1 - phi) K
is re-optimized after the switch by redeploying it to training, where it
earns through the capability kappa (1 - phi) K. kappa = 0 is the strict stock
(the remainder earns nothing and a late entrant earns nothing); kappa = 1 with
free reallocation is the flow economy behind the 0.01 corner of
``tbl-dynamic-phi``.

Specification 3 (accumulating stock). H revenue is X Z_t^alpha with
Z_t = zeta phi K (t - t_install), accumulating in both regimes without
depreciation. With phi fixed at installation the extra state is the firm's
age, expected revenue stays linear in X, and the *investment* problem reduces
exactly to the paper's with one change: an incumbent's H weight is multiplied
by the head-start factor

    m = [1 - x^(1 + alpha)] / (1 - x),   x = (r - mu_H) / (r - mu_L + lam),

once zeta is normalized so that an entrant's installed value keeps the
paper's coefficient A_H (`accumulating_stock_premium`). No new free parameter
enters the investment problem under that normalization. What does not reduce:
the default decision (equity depends on age), the duopoly (contest shares
depend on relative ages at the switch), and a revisable allocation (a
deterministic one-state control problem; `revisable_stock_allocation` solves
its constant-allocation restriction).

Specification 4 (amendment proposed here): a fixed installation cost f > 0,
combined with any of the above. Its polar case, the strict stock with a fixed
cost, has the pure-power L-regime option with exponent beta_L^+.

The stopping problem
--------------------
At installation the firm chooses (K, phi) with knowledge of X, so the
exercise payoff is the envelope

    P(X) = max_K [ g* K^alpha X - Theta(K) - f ],
    g(phi) = { (1 - phi)^alpha
               + lam A_H m [kappa_I + (1 - kappa_I) phi]^alpha } / (r - mu_L + lam),

with Theta(K) = delta K / r + c K^gamma and g* = max_phi g. The allocation
maximizes g at every scale, so

    phi* = (1 - M kappa_I) / (1 + M (1 - kappa_I)),
    M = [lam A_H m (1 - kappa_I)]^(-1 / (1 - alpha)),

truncated at zero; kappa_I = 0, m = 1 gives the paper's rho / (1 + rho).

Before the switch the value F of a firm that has not installed solves the
variational inequality

    max{ (1/2) sigma^2 X^2 F'' + mu_L X F' - (r + lam) F
         + lam theta F_H(vartheta X),  P(X) - F } = 0,   F(0) = 0.

After the switch an entrant solves the absorbing-H problem with payoff
max_K [A_H K^alpha z - Theta(K) - f] in z = vartheta X: value B_H z^beta_H
below its trigger z_H and the payoff above it.

Solution. Let S(X) be the value of never investing before the switch (the
particular solution of the ODE that is bounded at both ends). Then
F = S + sup_x [P(x) - S(x)] (X / x)^beta_L^+, and smooth pasting at the
trigger X* collapses to one scalar equation,

    (beta_L^+ - 1) g* K^alpha X - beta_L^+ [Theta(K) + f]
        = (2 / sigma^2) X^beta_L^-  int_0^X s^(-beta_L^- - 1)
                                    lam theta F_H(vartheta s) ds,

in which X = Theta'(K) K^(1 - alpha) / (alpha g*) is the demand at which K is
the statically optimal scale. Below the entrant's trigger the integral is a
power of X and the equation is algebraic in K; above it the integrand is the
entrant's exercise envelope, an elementary function of the entrant's capacity
(a sum of incomplete-beta-type integrals), evaluated here by quadrature. In
every case (X*, K*) is one scalar root and phi* is in closed form.

When theta = 0 or kappa_E = 0 the forcing term vanishes, F is the pure power
A X^beta_L^+, and the trigger is the textbook markup
X* = beta_L^+ / (beta_L^+ - 1) * [Theta(K*) + f] / (g* K*^alpha). The paper's
reduced model is the same algebra with beta_H in place of beta_L^+ and f = 0
(`pure_power_policy`), which is the documented special case that recovers its
numbers.

Three regimes arise, and `CapabilityStockModel.regime` classifies them from
the growth rates of P and S:

- "never": the waiting value outgrows the exercise envelope at large demand
  (the paper's baseline);
- "immediate": the envelope dominates at every demand level, so the firm
  installs at once at the statically optimal scale and no trigger exists
  (the strict stock without a fixed cost under (A3));
- "interior": a finite positive trigger with interior capacity.

Verification. `CapabilityStockModel.lcp` is a `PiecewiseOptionModel` whose
forcing and payoff are those of the specification, so the Brennan--Schwartz
solver of `piecewise_option.py` checks the stopping region at fixed (K, phi).
`CapabilityStockModel.joint_lcp` solves the complementarity problem on the
exercise envelope by policy iteration, which does not presume the stopping
region is an upper set.
"""

from collections.abc import Callable
from dataclasses import dataclass
from functools import cached_property

import numpy as np
from scipy import integrate, optimize, special
from scipy.linalg import solve_banded

from .base_model import SingleFirmModel
from .parameters import ModelParameters
from .piecewise_option import PiecewiseOptionModel, _negative_root

#: Log-capacity range searched for the scalar roots.
_LOG_K_RANGE = (-70.0, 25.0)
#: e-folds beyond which a power-law integrand tail is dropped.
_TAIL = 40.0

LAMBDA_GRID = (0.03, 0.05, 0.10, 0.20, 0.50)
DILEMMA_BELIEFS = (0.02, 0.18, 0.20, 0.50)


@dataclass(frozen=True)
class StockSpec:
    """Primitives added to the paper's exact problem (see module docstring)."""

    theta: float = 1.0
    late_training: float = 1.0
    redeploy: float = 0.0
    fixed_cost: float = 0.0
    accumulating: bool = False

    def __post_init__(self) -> None:
        for name in ("theta", "late_training", "redeploy"):
            value = getattr(self, name)
            if not 0.0 <= value <= 1.0:
                msg = f"{name} must lie in [0, 1], got {value}"
                raise ValueError(msg)
        if self.fixed_cost < 0.0:
            msg = f"fixed_cost must be non-negative, got {self.fixed_cost}"
            raise ValueError(msg)

    @classmethod
    def late_entry_discount(cls, theta: float, fixed_cost: float = 0.0) -> "StockSpec":
        """Specification 2."""
        return cls(theta=theta, fixed_cost=fixed_cost)

    @classmethod
    def pre_positioned(cls, kappa: float, fixed_cost: float = 0.0) -> "StockSpec":
        """Specification 1: one late-training effectiveness for everyone."""
        return cls(late_training=kappa, redeploy=kappa, fixed_cost=fixed_cost)

    @classmethod
    def accumulating_stock(cls, fixed_cost: float = 0.0) -> "StockSpec":
        """Specification 3 with phi fixed at installation."""
        return cls(accumulating=True, fixed_cost=fixed_cost)

    @property
    def entrant_excluded(self) -> bool:
        """True when a firm without capacity at the switch gets nothing."""
        return self.theta == 0.0 or self.late_training == 0.0


@dataclass(frozen=True)
class StockPolicy:
    """Optimal pre-switch policy of a specification.

    Attributes:
        status: "interior", "immediate" or "never" (module docstring).
        X_star: Trigger; 0 when immediate, inf when never.
        K_star: Capacity installed at the trigger (nan unless interior).
        phi_star: Training fraction, in closed form.
        algebraic: True when the trigger lies at or below the entrant's
            trigger, so the scalar equation involves no quadrature.
    """

    status: str
    X_star: float
    K_star: float
    phi_star: float
    algebraic: bool


def accumulating_stock_premium(params: ModelParameters) -> float:
    """Head-start factor m of Specification 3.

    An incumbent of age a at the switch earns X (zeta phi K)^alpha (a + s)^alpha
    at time s after it. Integrating over the exponential age and the
    post-switch horizon gives lam Gamma(1 + alpha) [eta^(-1-alpha) -
    rho^(-1-alpha)] / (rho - eta) per unit of X (phi K)^alpha zeta^alpha, with
    eta = r - mu_H and rho = r - mu_L + lam, against Gamma(1 + alpha)
    eta^(-1-alpha) for an entrant of age zero. Normalizing zeta so that the
    entrant's coefficient is A_H = 1 / eta leaves the incumbent's H weight at
    m times the paper's lam A_H / rho.
    """
    p = params
    x = (p.r - p.mu_H) / (p.r - p.mu_L + p.lam)
    return float((1.0 - x ** (1.0 + p.alpha)) / (1.0 - x))


def _head_start(params: ModelParameters, spec: StockSpec) -> float:
    return accumulating_stock_premium(params) if spec.accumulating else 1.0


def revenue_coeff(params: ModelParameters, spec: StockSpec, phi: float) -> float:
    """g(phi): installed L-regime revenue coefficient per unit of K^alpha X."""
    p = params
    capability = spec.redeploy + (1.0 - spec.redeploy) * phi
    h_weight = p.lam * p.A_H * _head_start(p, spec)
    return ((1.0 - phi) ** p.alpha + h_weight * capability**p.alpha) / (
        p.r - p.mu_L + p.lam
    )


def training_fraction(params: ModelParameters, spec: StockSpec) -> float:
    """Closed-form pre-switch training fraction phi* (zero at the corner)."""
    p = params
    kappa = spec.redeploy
    h_weight = p.lam * p.A_H * _head_start(p, spec) * (1.0 - kappa)
    if h_weight <= 0.0:
        return 0.0
    ratio = h_weight ** (-1.0 / (1.0 - p.alpha))
    return float(max(0.0, (1.0 - ratio * kappa) / (1.0 + ratio * (1.0 - kappa))))


def _first_upcrossing(
    func: Callable[[float], float], lo: float, hi: float, step: float = 0.5
) -> tuple[float | None, float]:
    """First root where func turns from negative to non-negative on [lo, hi].

    Returns the root (None if there is none) and func(lo).
    """
    start = func(lo)
    x, prev = lo, start
    while x < hi:
        nxt = min(x + step, hi)
        val = func(nxt)
        if prev < 0.0 <= val:
            return float(optimize.brentq(func, x, nxt, xtol=1e-13)), start
        x, prev = nxt, val
    return None, start


class CapabilityStockModel:
    """Exact pre-switch stopping problem of one specification."""

    def __init__(self, params: ModelParameters, spec: StockSpec | None = None):
        self.params = params
        self.spec = spec if spec is not None else StockSpec()
        p = params
        self.beta_H = p.beta_H
        self.beta_pos = p.beta_L
        self.beta_neg = _negative_root(p.sigma, p.mu_L, p.r + p.lam)
        self.vartheta = self.spec.late_training**p.alpha
        self.head_start = _head_start(p, self.spec)
        self.phi_star = training_fraction(p, self.spec)
        self.g_star = revenue_coeff(p, self.spec, self.phi_star)
        if self.beta_pos <= p.gamma / (p.gamma - p.alpha):
            msg = (
                "Ill-posed: the exercise envelope grows at least as fast as "
                "X^beta_L^+, so the pre-switch option value is unbounded."
            )
            raise RuntimeError(msg)
        self._solve_late_entry()

    # ------------------------------------------------------------------
    # Costs and static scale
    # ------------------------------------------------------------------

    def total_cost(self, K: np.ndarray | float) -> np.ndarray | float:
        """Theta(K) + f: outlay plus the operating-cost perpetuity."""
        p = self.params
        return p.delta * K / p.r + p.c * K**p.gamma + self.spec.fixed_cost

    def _marginal_cost(self, K: np.ndarray | float) -> np.ndarray | float:
        p = self.params
        return p.delta / p.r + p.c * p.gamma * K ** (p.gamma - 1.0)

    def _scale_payoff(self, K: np.ndarray | float) -> np.ndarray | float:
        """Net payoff at the demand where K is the statically optimal scale."""
        return self._marginal_cost(K) * K / self.params.alpha - self.total_cost(K)

    def _scale_demand(self, K: np.ndarray | float, coeff: float) -> np.ndarray | float:
        """Demand at which K maximizes coeff K^alpha X - Theta(K)."""
        p = self.params
        return self._marginal_cost(K) * K ** (1.0 - p.alpha) / (p.alpha * coeff)

    def _static_capacity(self, coeff: float, X: np.ndarray) -> np.ndarray:
        """Capacity maximizing coeff K^alpha X - Theta(K), by bisection."""
        p = self.params
        target = np.log(p.alpha * coeff) + np.log(X)
        lo = np.full_like(X, -120.0)
        hi = np.full_like(X, 80.0)
        for _ in range(90):
            mid = 0.5 * (lo + hi)
            excess = (
                target
                - (1.0 - p.alpha) * mid
                - np.log(self._marginal_cost(np.exp(mid)))
            )
            lo = np.where(excess > 0.0, mid, lo)
            hi = np.where(excess > 0.0, hi, mid)
        return np.exp(0.5 * (lo + hi))

    def _envelope(self, coeff: float, X: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
        K = self._static_capacity(coeff, X)
        return coeff * K**self.params.alpha * X - self.total_cost(K), K

    def exercise_envelope(self, X: np.ndarray | float) -> np.ndarray:
        """P(X): payoff of installing now at the best scale and allocation."""
        return self._envelope(self.g_star, np.atleast_1d(np.asarray(X, float)))[0]

    def exercise_payoff(self, K: float, phi: float, X: float) -> float:
        """Payoff of installing (K, phi) at demand X."""
        coeff = revenue_coeff(self.params, self.spec, phi)
        return float(coeff * K**self.params.alpha * X - self.total_cost(K))

    def _power_gap(self, K: float, beta: float) -> float:
        """beta P - X P' at the demand where K is the static optimum."""
        scale = self._marginal_cost(K) * K / self.params.alpha
        return float((beta - 1.0) * scale - beta * self.total_cost(K))

    @cached_property
    def demand_scale(self) -> float:
        """Reference demand level for numerical grids."""
        if 0.0 < self.late_trigger < np.inf:
            return self.late_trigger
        return float(self._scale_demand(self._kink_capacity, self.g_star))

    @cached_property
    def _kink_capacity(self) -> float:
        """Capacity at which linear and convex marginal costs are equal."""
        p = self.params
        return float((p.delta / (p.r * p.c * p.gamma)) ** (1.0 / (p.gamma - 1.0)))

    # ------------------------------------------------------------------
    # Late entry
    # ------------------------------------------------------------------

    def _solve_late_entry(self) -> None:
        """Entrant's absorbing-H problem in effective demand z = vartheta X.

        Sets `late_capacity` (K_H), `late_trigger` (z_H / vartheta, in units
        of X; 0 when the entrant invests at once, inf when it is excluded)
        and `late_coeff`, the coefficient on X^beta_H of the claim held at
        the switch below `late_trigger`.
        """
        p = self.params
        self.late_capacity = float("nan")
        self.late_trigger = float("inf")
        self.late_coeff = 0.0
        self._z_H = float("inf")
        if self.spec.entrant_excluded:
            return
        if self.beta_H <= p.gamma / (p.gamma - p.alpha):
            msg = (
                "Ill-posed: the H-regime option of a late entrant is unbounded "
                "(the lower bound of (A2) fails)."
            )
            raise RuntimeError(msg)
        root, _ = _first_upcrossing(
            lambda t: self._power_gap(float(np.exp(t)), self.beta_H), *_LOG_K_RANGE
        )
        if root is None:
            # The envelope dominates X^beta_H everywhere: immediate entry.
            self.late_capacity, self._z_H, self.late_trigger = 0.0, 0.0, 0.0
            return
        K_H = float(np.exp(root))
        z_H = float(self._scale_demand(K_H, p.A_H))
        B_H = float(self._scale_payoff(K_H)) / z_H**self.beta_H
        self.late_capacity, self._z_H = K_H, z_H
        self.late_trigger = z_H / self.vartheta
        self.late_coeff = self.spec.theta * self.vartheta**self.beta_H * B_H

    def late_entry_value(self, X: np.ndarray | float) -> np.ndarray:
        """theta F_H(vartheta X): the claim held at the switch without capacity."""
        X_arr = np.atleast_1d(np.asarray(X, float))
        if self.spec.entrant_excluded:
            return np.zeros_like(X_arr)
        out = self.late_coeff * X_arr**self.beta_H
        z = self.vartheta * X_arr
        mask = z >= self._z_H
        if mask.any():
            out[mask] = self.spec.theta * self._envelope(self.params.A_H, z[mask])[0]
        return out

    def _entrant_integral(self, beta: float, t_lo: float, t_hi: float) -> float:
        """int z^(-beta-1) [entrant payoff] dz over log capacities [t_lo, t_hi]."""
        p = self.params

        def integrand(t: float) -> float:
            k = np.exp(t)
            marginal = self._marginal_cost(k)
            z = marginal * k ** (1.0 - p.alpha) / (p.alpha * p.A_H)
            elasticity = (1.0 - p.alpha) + (
                p.c * p.gamma * (p.gamma - 1.0) * k ** (p.gamma - 1.0) / marginal
            )
            return float(z ** (-beta) * self._scale_payoff(k) * elasticity)

        if t_hi <= t_lo:
            return 0.0
        value, _ = integrate.quad(
            integrand, t_lo, t_hi, epsabs=0.0, epsrel=1e-10, limit=400
        )
        return float(value)

    def _entrant_log_capacity(self, X: float) -> float:
        z = np.array([self.vartheta * X])
        return float(np.log(self._static_capacity(self.params.A_H, z)[0]))

    def _integral_minus(self, X: float) -> float:
        """int_0^X s^(-beta_L^- - 1) theta F_H(vartheta s) ds."""
        if self.spec.entrant_excluded:
            return 0.0
        p = self.params
        h, n = self.beta_H, self.beta_neg
        x_t = self.late_trigger
        if x_t >= X:
            return self.late_coeff * X ** (h - n) / (h - n)
        closed = self.late_coeff * x_t ** (h - n) / (h - n) if x_t > 0.0 else 0.0
        t_hi = self._entrant_log_capacity(X)
        if self.late_capacity > 0.0:
            t_lo = float(np.log(self.late_capacity))
        else:
            t_lo = min(t_hi, np.log(self._kink_capacity)) - _TAIL / (
                1.0 - n * (1.0 - p.alpha)
            )
        tail = self._entrant_integral(n, t_lo, t_hi)
        return closed + self.spec.theta * self.vartheta**n * tail

    def _integral_plus(self, X: float) -> float:
        """int_X^inf s^(-beta_L^+ - 1) theta F_H(vartheta s) ds."""
        if self.spec.entrant_excluded:
            return 0.0
        h, b = self.beta_H, self.beta_pos
        x_t = self.late_trigger
        if x_t > X:
            below = self.late_coeff * (x_t ** (h - b) - X ** (h - b)) / (h - b)
            return below + self._tail_plus
        return self._upper_integral(X)

    def _upper_integral(self, X: float) -> float:
        p = self.params
        b = self.beta_pos
        t_lo = self._entrant_log_capacity(X)
        t_hi = max(t_lo, np.log(self._kink_capacity)) + _TAIL / (
            b * (p.gamma - p.alpha) - p.gamma
        )
        return (
            self.spec.theta * self.vartheta**b * self._entrant_integral(b, t_lo, t_hi)
        )

    @cached_property
    def _tail_plus(self) -> float:
        return self._upper_integral(self.late_trigger)

    def waiting_value(self, X: float) -> float:
        """S(X): value of never investing before the switch."""
        if self.spec.entrant_excluded:
            return 0.0
        p = self.params
        b, n = self.beta_pos, self.beta_neg
        scale = 2.0 * p.lam / (p.sigma**2 * (b - n))
        return float(
            scale * (X**n * self._integral_minus(X) + X**b * self._integral_plus(X))
        )

    # ------------------------------------------------------------------
    # Regime classification
    # ------------------------------------------------------------------

    def asymptotic_ratio(self, exponent: float) -> float:
        """Waiting value over exercise envelope where both grow like X^exponent.

        The envelope behaves like X^(1 / (1 - alpha)) at low demand (linear
        cost) and like X^(gamma / (gamma - alpha)) at high demand (convex
        cost); on either branch the ratio is theta lam / |Q_L(e)| times
        (vartheta A_H / g*)^e.
        """
        if self.spec.entrant_excluded:
            return 0.0
        p = self.params
        q = (
            0.5 * p.sigma**2 * exponent * (exponent - 1.0)
            + p.mu_L * exponent
            - (p.r + p.lam)
        )
        ratio = (self.vartheta * p.A_H / self.g_star) ** exponent
        return float(self.spec.theta * p.lam / (-q) * ratio)

    def theta_bounds(self) -> tuple[float, float]:
        """Range of theta giving an interior trigger, other primitives fixed.

        The upper bound is where waiting stops being dominated at high
        demand. The lower bound is zero unless the entrant invests at once
        (the upper bound of (A2) fails with no fixed cost), in which case
        waiting must dominate at low demand.
        """
        p = self.params
        if self.spec.entrant_excluded:
            return 0.0, float("inf")
        per_theta_high = self.asymptotic_ratio(p.gamma / (p.gamma - p.alpha))
        upper = self.spec.theta / per_theta_high
        low_exponent = 1.0 / (1.0 - p.alpha)
        if self.spec.fixed_cost > 0.0 or self.beta_H < low_exponent:
            return 0.0, upper
        return self.spec.theta / self.asymptotic_ratio(low_exponent), upper

    def regime(self) -> str:
        """Classify the solution as "interior", "immediate" or "never"."""
        p = self.params
        if self.asymptotic_ratio(p.gamma / (p.gamma - p.alpha)) >= 1.0:
            return "never"
        if self.spec.fixed_cost > 0.0:
            return "interior"
        low_exponent = 1.0 / (1.0 - p.alpha)
        if self.spec.entrant_excluded:
            return "interior" if self.beta_pos < low_exponent else "immediate"
        if self.beta_H < low_exponent:
            return "interior"
        return "interior" if self.asymptotic_ratio(low_exponent) > 1.0 else "immediate"

    # ------------------------------------------------------------------
    # Solution
    # ------------------------------------------------------------------

    def _trigger_gap(self, log_K: float) -> float:
        """Smooth-pasting residual at capacity K, scaled by total cost."""
        p = self.params
        K = float(np.exp(log_K))
        X = float(self._scale_demand(K, self.g_star))
        forcing = 0.0
        if not self.spec.entrant_excluded:
            forcing = (
                2.0 * p.lam / p.sigma**2 * X**self.beta_neg * self._integral_minus(X)
            )
        return (self._power_gap(K, self.beta_pos) - forcing) / float(self.total_cost(K))

    @cached_property
    def policy(self) -> StockPolicy:
        """Optimal pre-switch policy."""
        regime = self.regime()
        if regime == "never":
            return StockPolicy(regime, float("inf"), float("nan"), self.phi_star, True)
        if regime == "immediate":
            return StockPolicy(regime, 0.0, float("nan"), self.phi_star, True)
        root, start = _first_upcrossing(self._trigger_gap, *_LOG_K_RANGE)
        if start >= 0.0:
            # The smooth-pasting residual is already non-negative at the
            # smallest capacity searched (e^-70): the trigger exists but at a
            # scale below it, which happens when beta_H is just under
            # 1 / (1 - alpha), next to the upper bound of (A2). At every
            # demand level of interest the firm is in its investment region.
            return StockPolicy("immediate", 0.0, float("nan"), self.phi_star, True)
        if root is None:
            msg = "Interior trigger lies outside the capacity range searched."
            raise RuntimeError(msg)
        K = float(np.exp(root))
        X = float(self._scale_demand(K, self.g_star))
        return StockPolicy(regime, X, K, self.phi_star, self.late_trigger >= X)

    def policy_value(self, K: float, phi: float, X_stop: float, X: float) -> float:
        """Value at X of "install (K, phi) at X_stop", under this model's lam.

        X_stop = inf prices never investing before the switch.
        """
        if X_stop <= X:
            return self.exercise_payoff(K, phi, X)
        wait = self.waiting_value(X)
        if not np.isfinite(X_stop):
            return wait
        premium = self.exercise_payoff(K, phi, X_stop) - self.waiting_value(X_stop)
        return wait + premium * (X / X_stop) ** self.beta_pos

    def value(self, X: float) -> float:
        """Optimal pre-switch value at demand X."""
        pol = self.policy
        if pol.status == "never":
            return self.waiting_value(X)
        if pol.status == "immediate" or pol.X_star <= X:
            return float(self.exercise_envelope(X)[0])
        return self.policy_value(pol.K_star, pol.phi_star, pol.X_star, X)

    # ------------------------------------------------------------------
    # Credit objects of an installed firm
    # ------------------------------------------------------------------

    def faith_threshold(self, exact: bool = False) -> float:
        """Training fraction above which a higher lam is good news.

        With ``exact=False`` this is the A_eff-channel threshold (the paper's
        phi_underbar): dA_eff/dlam > 0. With ``exact=True`` it is the net
        threshold phi_tilde, at which the default boundary falls in lam,
        which adds the markup channel d ln[beta^- / (beta^- - 1)] / dlam.
        Solved from a numerical lam-derivative of g so that it covers every
        specification (the head start of Specification 3 moves with lam);
        returns 0 when every allocation qualifies and 1 when none does.
        """
        p = self.params
        hurdle = 0.0
        if exact:
            disc = np.sqrt(
                (p.mu_L - 0.5 * p.sigma**2) ** 2 + 2.0 * p.sigma**2 * (p.r + p.lam)
            )
            hurdle = 1.0 / (self.beta_neg * (self.beta_neg - 1.0) * disc)
        step = 1e-6
        up, down = p.with_param(lam=p.lam + step), p.with_param(lam=p.lam - step)

        def slope(phi: float) -> float:
            rise = np.log(revenue_coeff(up, self.spec, phi)) - np.log(
                revenue_coeff(down, self.spec, phi)
            )
            return float(rise / (2.0 * step) - hurdle)

        lo, hi = 1e-9, 1.0 - 1e-9
        if slope(lo) >= 0.0:
            return 0.0
        if slope(hi) <= 0.0:
            return 1.0
        return float(optimize.brentq(slope, lo, hi, xtol=1e-12))

    def default_boundary(self, K: float, phi: float, coupon: float) -> float:
        """Single-boundary default trigger of an installed firm (paper form)."""
        p = self.params
        markup = self.beta_neg / (self.beta_neg - 1.0)
        coeff = revenue_coeff(p, self.spec, phi) * K**p.alpha
        return float(markup * (coupon + p.delta * K) / (p.r * coeff))

    # ------------------------------------------------------------------
    # Independent numerical verification
    # ------------------------------------------------------------------

    @cached_property
    def lcp(self) -> "_StockLCP":
        """`PiecewiseOptionModel` carrying this specification's primitives."""
        return _StockLCP(self)

    def joint_lcp(
        self,
        n_grid: int = 6001,
        x_min: float | None = None,
        x_max: float | None = None,
    ) -> dict:
        """Complementarity problem on the exercise envelope, by policy iteration.

        Unlike the Brennan--Schwartz pass in `piecewise_option.py`, Howard's
        algorithm makes no assumption on the shape of the stopping region,
        so it also certifies that the region is an upper set.

        Returns:
            Dict with the grid ``X``, values ``F``, the boolean ``stop``
            mask, ``kind`` ("upper", "never", "all" or "other"), and the
            ``boundary`` and ``capacity`` at the lowest stopping node.
        """
        p = self.params
        if x_min is None or x_max is None:
            x_min, x_max = self._grid_range()
        y = np.linspace(np.log(x_min), np.log(x_max), n_grid)
        dy = y[1] - y[0]
        X = np.exp(y)
        s2 = 0.5 * p.sigma**2
        sub = -(s2 / dy**2 - (p.mu_L - s2) / (2.0 * dy))
        diag = 2.0 * s2 / dy**2 + (p.r + p.lam)
        sup = -(s2 / dy**2 + (p.mu_L - s2) / (2.0 * dy))

        obstacle, capacity = self._envelope(self.g_star, X)
        forcing = p.lam * self.late_entry_value(X)
        top = p.gamma / (p.gamma - p.alpha)
        q_top = s2 * top * (top - 1.0) + p.mu_L * top - (p.r + p.lam)
        far_field = max(obstacle[-1], forcing[-1] / (-q_top))
        near_field = max(obstacle[0], 0.0)

        stop = np.zeros(n_grid, dtype=bool)
        F = np.zeros(n_grid)
        for _ in range(500):
            bands = np.zeros((3, n_grid))
            bands[0, 1:] = np.where(stop[:-1], 0.0, sup)
            bands[1, :] = np.where(stop, 1.0, diag)
            bands[2, :-1] = np.where(stop[1:], 0.0, sub)
            rhs = np.where(stop, obstacle, forcing)
            bands[1, 0], bands[0, 1], rhs[0] = 1.0, 0.0, near_field
            bands[1, -1], bands[2, -2], rhs[-1] = 1.0, 0.0, far_field
            F = solve_banded((1, 1), bands, rhs)
            residual = np.zeros(n_grid)
            residual[1:-1] = sub * F[:-2] + diag * F[1:-1] + sup * F[2:] - forcing[1:-1]
            new_stop = stop.copy()
            new_stop[1:-1] = np.where(
                stop[1:-1], residual[1:-1] >= 0.0, F[1:-1] < obstacle[1:-1]
            )
            if np.array_equal(new_stop, stop):
                break
            stop = new_stop

        interior = stop[1:-1]
        out = {"X": X, "F": F, "stop": stop, "boundary": float("inf")}
        out["capacity"] = float("nan")
        if not interior.any():
            out["kind"] = "never"
            return out
        first = 1 + int(np.argmax(interior))
        out["boundary"], out["capacity"] = float(X[first]), float(capacity[first])
        if not interior[first - 1 :].all():
            out["kind"] = "other"
        else:
            out["kind"] = "all" if first == 1 else "upper"
        return out

    def _grid_range(self) -> tuple[float, float]:
        ref = [self.demand_scale]
        if self.regime() == "interior":
            ref.append(self.policy.X_star)
        return 1e-5 * min(ref), 1e5 * max(ref)


class _StockLCP(PiecewiseOptionModel):
    """`PiecewiseOptionModel` with a specification's forcing and payoff.

    The attributes the parent's algebra reads (X_H, B_H, C, a_H, b_H, g, k)
    are set to their scaled counterparts, so the precommitted-scale closed
    forms and the Brennan--Schwartz solver apply unchanged. At the default
    specification every attribute equals the parent's.
    """

    def __init__(self, model: CapabilityStockModel):
        p = model.params
        self.model = model
        self.params = p
        self.base = SingleFirmModel(p)
        self.beta_H = model.beta_H
        self.beta_L_pos = model.beta_pos
        self.beta_L_neg = model.beta_neg
        self.X_H = model.late_trigger
        self.K_H = model.late_capacity
        self.B_H = model.late_coeff
        q = (
            0.5 * p.sigma**2 * self.beta_H * (self.beta_H - 1.0)
            + p.mu_L * self.beta_H
            - (p.r + p.lam)
        )
        self.C = -p.lam * self.B_H / q
        self.a_H = 0.0
        self.b_H = 0.0
        if model.late_capacity > 0.0:
            theta, K_H = model.spec.theta, model.late_capacity
            self.a_H = theta * model.vartheta * p.A_H * K_H**p.alpha
            self.b_H = theta * float(model.total_cost(K_H))
        self.g = p.lam * self.a_H / (p.r + p.lam - p.mu_L)
        self.k = -p.lam * self.b_H / (p.r + p.lam)

    def exercise_payoff_coeffs(self, K: float, phi: float) -> tuple[float, float]:
        coeff = revenue_coeff(self.params, self.model.spec, phi)
        return coeff * K**self.params.alpha, float(self.model.total_cost(K))

    def envelope_capacity(self, X: np.ndarray | float) -> np.ndarray:
        z = self.model.vartheta * np.atleast_1d(np.asarray(X, dtype=float))
        return self.model._static_capacity(self.params.A_H, z)

    def envelope_payoff(self, X: np.ndarray | float) -> np.ndarray:
        z = self.model.vartheta * np.atleast_1d(np.asarray(X, dtype=float))
        return self.model.spec.theta * self.model._envelope(self.params.A_H, z)[0]

    def _envelope_grid_range(self, X_stop: float | None = None) -> tuple[float, float]:
        refs = [self.model.demand_scale]
        if self.model.regime() == "interior":
            refs.append(self.model.policy.X_star)
        if X_stop is not None and np.isfinite(X_stop):
            refs.append(float(X_stop))
        return 1e-5 * min(refs), 1e4 * max(refs)


# ----------------------------------------------------------------------
# Pure-power special case (nests the paper's reduced model)
# ----------------------------------------------------------------------


def pure_power_policy(
    params: ModelParameters,
    beta: float | None = None,
    fixed_cost: float = 0.0,
    redeploy: float = 0.0,
) -> tuple[float, float, float]:
    """(X*, K*, phi*) when the continuation value is a pure power X^beta.

    With ``beta = beta_L^+`` (the default) this is the exact solution when a
    late entrant gets nothing. With ``beta = params.beta_H`` and no fixed
    cost it is the paper's reduced model: K* of Proposition 1 and the trigger
    eq-trigger-phi.

    Raises:
        RuntimeError: When no interior scale exists at this exponent.
    """
    spec = StockSpec(theta=0.0, fixed_cost=fixed_cost, redeploy=redeploy)
    model = CapabilityStockModel(params, spec)
    exponent = model.beta_pos if beta is None else beta
    root, _ = _first_upcrossing(
        lambda t: model._power_gap(float(np.exp(t)), exponent), *_LOG_K_RANGE
    )
    if root is None:
        msg = f"No interior capacity for a pure power with exponent {exponent:.4f}"
        raise RuntimeError(msg)
    K = float(np.exp(root))
    return float(model._scale_demand(K, model.g_star)), K, model.phi_star


# ----------------------------------------------------------------------
# Belief mismatch (Dario's dilemma) in the exact problem
# ----------------------------------------------------------------------


def belief_mismatch(
    params: ModelParameters,
    spec: StockSpec,
    lambda_true: float = 0.10,
    lambda_invest: tuple[float, ...] = DILEMMA_BELIEFS,
    x0_ratio: float = 0.5,
    X_0: float | None = None,
) -> dict:
    """Value lost by following the policy that is optimal under a wrong lam.

    Each belief's policy solves the exact problem under that belief and is
    then valued under ``lambda_true`` at one demand level X_0, held fixed
    across beliefs, as in `piecewise_option.envelope_dilemma`. A policy whose
    trigger lies at or below X_0 is in its stopping region there, so it
    installs at X_0 the scale that is statically optimal under its own
    belief; one that never invests before the switch is worth the waiting
    value. X_0 defaults to ``x0_ratio`` times the true-belief trigger
    when that is finite, and otherwise to ``x0_ratio`` times the reduced
    model's trigger. Losses are shares of total value at X_0 and, outside
    the pure-power case, are not invariant to X_0, because the late-entry
    claim is common to every policy.
    """
    p_true = params.with_param(lam=lambda_true)
    truth = CapabilityStockModel(p_true, spec)
    if X_0 is None:
        if truth.policy.status == "interior":
            X_0 = x0_ratio * truth.policy.X_star
        else:
            X_0 = x0_ratio * pure_power_policy(p_true, beta=p_true.beta_H)[0]

    def worth(model: CapabilityStockModel) -> float:
        pol = model.policy
        K = pol.K_star
        if pol.X_star <= X_0:
            K = float(model._static_capacity(model.g_star, np.array([X_0]))[0])
        return truth.policy_value(K, pol.phi_star, pol.X_star, X_0)

    beliefs = [
        CapabilityStockModel(params.with_param(lam=lam), spec) for lam in lambda_invest
    ]
    best = worth(truth)
    return {
        "lambda_invest": list(lambda_invest),
        "X_0": X_0,
        "X_star": [m.policy.X_star for m in beliefs],
        "K_star": [m.policy.K_star for m in beliefs],
        "phi_star": [m.policy.phi_star for m in beliefs],
        "loss_pct": [100.0 * (1.0 - worth(m) / best) for m in beliefs],
    }


# ----------------------------------------------------------------------
# Interior-capacity window
# ----------------------------------------------------------------------


def stock_regime(params: ModelParameters, spec: StockSpec) -> str:
    """Regime of a specification, or "ill-posed" when no solution exists."""
    try:
        return CapabilityStockModel(params, spec).regime()
    except RuntimeError:
        return "ill-posed"


def interior_window(
    param_name: str,
    lo: float,
    hi: float,
    spec: StockSpec | None = None,
    base_params: ModelParameters | None = None,
    n: int = 401,
) -> tuple[float, float]:
    """Range of one parameter, around the baseline, with an interior optimum.

    ``spec=None`` returns the window of the paper's reduced model, that is
    condition (A2). Otherwise the window is where the specification has a
    finite positive pre-switch trigger with interior capacity. The grid is
    scanned outward from the baseline value and each end is refined by
    bisection; (nan, nan) means the baseline itself is not interior, and an
    end equal to ``lo`` or ``hi`` means the window extends at least that far.
    """
    base = base_params if base_params is not None else ModelParameters()

    def interior(value: float) -> bool:
        try:
            params = base.with_param(**{param_name: float(value)})
        except ValueError:
            return False
        if spec is None:
            return SingleFirmModel(params).has_interior_trigger("H")
        return stock_regime(params, spec) == "interior"

    def refine(inside: float, outside: float) -> float:
        for _ in range(30):
            mid = 0.5 * (inside + outside)
            inside, outside = (mid, outside) if interior(mid) else (inside, mid)
        return inside

    grid = np.linspace(lo, hi, n)
    start = int(np.argmin(np.abs(grid - getattr(base, param_name))))
    if not interior(grid[start]):
        return float("nan"), float("nan")
    left = right = start
    while left > 0 and interior(grid[left - 1]):
        left -= 1
    while right < n - 1 and interior(grid[right + 1]):
        right += 1
    lower = refine(grid[left], grid[left - 1]) if left > 0 else lo
    upper = refine(grid[right], grid[right + 1]) if right < n - 1 else hi
    return float(lower), float(upper)


# ----------------------------------------------------------------------
# Duopoly allocation condition and the revisable accumulating stock
# ----------------------------------------------------------------------


def follower_allocation_slope(
    params: ModelParameters,
    spec: StockSpec,
    phi_F: float,
    K_F: float,
    phi_L: float,
    K_L: float,
) -> float:
    """dA_eff,F / dphi_F under the paper's Tullock contests.

    Inference capacities contest L-regime revenue and capabilities
    Z_i = K_i [kappa_I + (1 - kappa_I) phi_i] contest H-regime revenue. The
    derivative uses f'(u) = alpha u^(alpha - 1) s (2 - s) for
    f(u) = u^(2 alpha) / (u^alpha + c). At a common allocation the two
    shares coincide, the factor s (2 - s) cancels, and the condition is the
    single-firm one: role invariance (Proposition 3(ii)) at phi*. Not defined
    for the accumulating stock, whose H shares depend on ages at the switch.
    """
    if spec.accumulating:
        msg = "The static contest does not apply to the accumulating stock."
        raise ValueError(msg)
    p = params
    kappa = spec.redeploy

    def marginal(own: float, rival: float) -> float:
        share = own**p.alpha / (own**p.alpha + rival**p.alpha)
        return p.alpha * own ** (p.alpha - 1.0) * share * (2.0 - share)

    inference = marginal((1.0 - phi_F) * K_F, (1.0 - phi_L) * K_L)
    capability = marginal(
        K_F * (kappa + (1.0 - kappa) * phi_F), K_L * (kappa + (1.0 - kappa) * phi_L)
    )
    rho = p.r - p.mu_L + p.lam
    return float(K_F * (p.lam * p.A_H * (1.0 - kappa) * capability - inference) / rho)


def revisable_stock_allocation(params: ModelParameters) -> dict[str, float]:
    """Pre-switch training under the accumulating stock when phi is revisable.

    After the switch the firm moves all compute to training, so a firm of age
    a at the switch that trained a constant fraction phi before it holds
    Z = zeta K (phi a + s) at time s after it. Under the normalization of
    `accumulating_stock_premium`, the value per unit of K^alpha X is

        J(phi) = (1 - phi)^alpha / rho
                 + lam int_0^inf e^(-rho a) h(phi a) da,
        h(z) = e^(eta z) Q(1 + alpha, eta z) / eta,

    with Q the regularized upper incomplete gamma function. The allocation
    is restricted to be constant before the switch (the unrestricted problem
    is a deterministic one-state control problem, not solved here). J'(0) =
    lam / rho^2 - alpha / rho, so phi is interior if and only if
    lam > alpha (r - mu_L) / (1 - alpha).

    Returns:
        Dict with ``phi`` (the maximizer), ``phi_frozen`` (the closed form
        when the allocation cannot be revised) and ``lam_min`` (the arrival
        rate above which ``phi`` is interior).
    """
    p = params
    rho, eta = p.r - p.mu_L + p.lam, p.r - p.mu_H

    def continuation(z: float) -> float:
        return float(np.exp(eta * z) * special.gammaincc(1.0 + p.alpha, eta * z) / eta)

    def value(phi: float) -> float:
        flow, _ = integrate.quad(
            lambda a: np.exp(-rho * a) * continuation(phi * a),
            0.0,
            _TAIL / rho,
            epsabs=0.0,
            epsrel=1e-10,
            limit=200,
        )
        return (1.0 - phi) ** p.alpha / rho + p.lam * flow

    res = optimize.minimize_scalar(
        lambda phi: -value(phi),
        bounds=(0.0, 1.0),
        method="bounded",
        options={"xatol": 1e-10},
    )
    phi = float(res.x) if value(float(res.x)) > value(0.0) else 0.0
    return {
        "phi": phi,
        "phi_frozen": training_fraction(p, StockSpec.accumulating_stock()),
        "lam_min": p.alpha * (p.r - p.mu_L) / (1.0 - p.alpha),
    }


# ----------------------------------------------------------------------
# Reporting
# ----------------------------------------------------------------------


def specification_table(
    spec: StockSpec,
    params: ModelParameters | None = None,
    lambdas: tuple[float, ...] = LAMBDA_GRID,
) -> list[dict]:
    """One row per arrival rate: regime, policy and credit thresholds."""
    base = params if params is not None else ModelParameters()
    rows = []
    for lam in lambdas:
        model = CapabilityStockModel(base.with_param(lam=lam), spec)
        pol = model.policy
        rows.append({
            "lam": lam,
            "status": pol.status,
            "X_star": pol.X_star,
            "K_star": pol.K_star,
            "phi_star": pol.phi_star,
            "algebraic": pol.algebraic,
            "late_trigger": model.late_trigger,
            "theta_bounds": model.theta_bounds(),
            "phi_underbar": model.faith_threshold(),
            "phi_tilde": model.faith_threshold(exact=True),
        })
    return rows


#: Specifications reported in the issue comment.
REPORTED_SPECS: dict[str, StockSpec] = {
    "paper exact (theta=1)": StockSpec(),
    "S2 theta=0.80": StockSpec.late_entry_discount(0.80),
    "S2 theta=0.50": StockSpec.late_entry_discount(0.50),
    "S1 kappa=0.20": StockSpec.pre_positioned(0.20),
    "S1 kappa=0.50": StockSpec.pre_positioned(0.50),
    "S3 accumulating": StockSpec.accumulating_stock(),
    "S4 strict stock, f=0.002": StockSpec.late_entry_discount(0.0, 0.002),
    "S4 + S2 theta=0.50, f=0.002": StockSpec.late_entry_discount(0.50, 0.002),
    "S4 + S1 kappa=0.20, f=0.002": StockSpec.pre_positioned(0.20, 0.002),
    "S4 + S3 accumulating, f=0.002": StockSpec.accumulating_stock(0.002),
}


def format_report(params: ModelParameters | None = None) -> str:  # pragma: no cover
    """Plain-text tables behind the issue #174 results comment."""
    base = params if params is not None else ModelParameters()
    lines = []
    for name, spec in REPORTED_SPECS.items():
        lines.append(f"\n{name}")
        lines.append(
            "  lam    status     X*          K*          phi*   X*/X_late"
            "  theta-range      phi_ub  phi_tl"
        )
        for row in specification_table(spec, base):
            lo, hi = row["theta_bounds"]
            lines.append(
                f"  {row['lam']:.2f}  {row['status']:9s}  {row['X_star']:.4e}"
                f"  {row['K_star']:.4e}  {row['phi_star']:.3f}"
                f"  {row['X_star'] / row['late_trigger']:9.3g}"
                f"  ({lo:.3f}, {hi:.3f})  {row['phi_underbar']:.3f}"
                f"   {row['phi_tilde']:.3f}"
            )
        mis = belief_mismatch(base, spec)
        loss = "  ".join(
            f"{lam:.2f}: {a:6.2f}%"
            for lam, a in zip(mis["lambda_invest"], mis["loss_pct"], strict=True)
        )
        lines.append(f"  dilemma at X_0 = {mis['X_0']:.3e}: {loss}")
        for name_, lo, hi in (("r", 0.05, 0.40), ("alpha", 0.05, 0.95)):
            window = interior_window(name_, lo, hi, spec, base)
            lines.append(f"  window {name_}: ({window[0]:.4f}, {window[1]:.4f})")
    a2_r = interior_window("r", 0.05, 0.40, None, base)
    a2_alpha = interior_window("alpha", 0.05, 0.95, None, base)
    lines.append(
        f"\n(A2) window: r in ({a2_r[0]:.4f}, {a2_r[1]:.4f}), "
        f"alpha in ({a2_alpha[0]:.4f}, {a2_alpha[1]:.4f})"
    )
    return "\n".join(lines)


if __name__ == "__main__":  # pragma: no cover
    print(format_report())
