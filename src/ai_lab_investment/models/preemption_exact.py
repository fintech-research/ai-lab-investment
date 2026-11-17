"""L-regime preemption game in the exact primitives, at zero leverage.

Diagnostic for the question raised by the 2026-11 review (comment C1, action
4; issue #173). The single firm of Internet Appendix B prefers to wait for
the regime switch rather than invest before it. In a duopoly both firms
cannot wait, so does the threat of preemption restore a finite pre-switch
trigger once the pure-power (unconditional-A_eff) convention is dropped?
Verification module: not wired into the pipeline, and it changes no number
in the paper.

Formulation
-----------
Primitives are the paper's. Demand X follows a GBM with drift mu_L before and
mu_H after a switch that arrives at rate lambda and is absorbing. A firm with
capacity K and training fraction phi earns the flow X [(1-phi)K]^alpha s^L
before the switch and X (phi K)^alpha s^H after it, with s the Tullock shares
of sec-duopoly (equal to one while the rival has not installed), pays the
operating cost delta K forever, and sinks I(K) = c K^gamma in one
irreversible lump with phi committed at installation. There is no debt.
Nothing is priced with the beta_H convention. Every L-regime claim V solves

    (sigma^2/2) X^2 V'' + mu_L X V' - (r + lambda) V + f(X) = 0,

with f its revenue flow plus lambda times its value at a switch, and the
bounded solution is written with the Green's function of that operator
(`ForcedClaim`). Roles are those of the paper's game: one firm (the leader)
installs (K_L, phi_L) at demand X in regime L and the other (the follower)
best-responds.

Follower, after the switch. A follower that has not installed holds an
absorbing-H option against the installed leader. It devotes all capacity to
training (inference earns nothing in H), so entering at X with K pays
A_H X K^{2 alpha} / (K^alpha + (phi_L K_L)^alpha) - delta K / r - I(K). The
jointly optimal (X_F^H, K_F^H) and the option coefficient B_F^H come from a
scalar first-order condition (`post_switch_entry`). Its value F^H(X) is
B_F^H X^{beta_H} below X_F^H and the exercised payoff above it, under the two
scale assumptions of Internet Appendix B:

- ``"precommitted"``: capacity fixed at K_F^H (affine payoff above X_F^H);
- ``"envelope"``: capacity chosen at the switch (the exercise envelope).

Follower, before the switch. Its exact value solves the stopping problem
with forcing lambda F^H(X) and obstacle Psi(X) = max_{K, phi} [A_eff,F(phi,
K) X - delta K / r - I(K)], where A_eff,F is the duopoly coefficient of
eq-a-eff-duopoly (exact, because once both firms are installed no decision
remains). The follower may therefore enter before the switch, or wait for it
and enter in H, whichever is worth more. Below its pre-switch entry trigger
X_F^L,

    F(X) = P_F(X) + h_F X^{beta_L^+},
    h_F = max{0, sup_X [Psi(X) - P_F(X)] X^{-beta_L^+}},

with P_F the pure switching value (never enter before the switch). h_F = 0
means that the follower waits for the switch at every demand level.

Leader. Its revenue claim M solves the same ODE, with four phases:

- before the switch, follower not installed: the monopoly flow
  X [(1-phi_L) K_L]^alpha;
- before the switch, follower installed (only if h_F > 0): M is matched at
  X_F^L to the leader's duopoly value A_eff,L X, which adds h_M X^{beta_L^+};
- after the switch, follower not installed and X < X_F^H: the monopoly claim
  A_H (phi_L K_L)^alpha X less the dilution at the follower's entry,
  Delta (X / X_F^H)^{beta_H} (exact: H is absorbing, so beta_H is the right
  root there);
- after the switch, X >= X_F^H: the follower enters at the switch, at K_F^H
  or at the envelope capacity, and the leader keeps its H-regime share.

The leader's entry NPV is L(X) = M(X) - delta K_L / r - I(K_L).

Rent equalization. The gap L(X) - F(X) is negative at the origin (the sunk
outlay). The preemption trigger X_P is its first up-crossing on the region in
which the follower has not entered.

Conventions kept and dropped
----------------------------
Kept: zero leverage; symmetric firms and beliefs; phi committed at
installation; a single lump; the Tullock contests; the role structure of the
paper's game (one leader, one follower). The leader-scale convention is
reported both ways. ``paper`` holds (K_L, phi_L) at the reduced-form monopoly
optimum (K*, phi*) of Proposition 1, so the comparison with the reduced-model
X_P isolates the valuation. ``reoptimized`` lets the leader choose (K_L,
phi_L) to maximize its own entry NPV at the entry demand, the follower
best-responding, and solves the fixed point L*(X_P) = F(X_P; K_L(X_P),
phi_L(X_P)), as in the leader-scale sensitivity of Internet Appendix B. Only
the second is a best response in the exact game: K* is an object of the
reduced model. Dropped: every use of the beta_H discount factor and of the
pure-power option form in the L-regime.

Simplifications
---------------
1. The follower's post-switch value assumes that it enters at once above
   X_F^H (an upper-set exercise region). The tests check this with an
   H-regime linear complementarity problem; it is not proved.
2. "Precommitted" fixes the follower's *post-switch* scale at K_F^H, the
   analogue of the single firm's K_H*. Its pre-switch scale is always chosen
   at entry.
3. Uniqueness of the envelope capacity uses 2 alpha < 1 (marginal contest
   revenue decreasing in own capacity); the constructor rejects alpha >= 1/2.
4. Outcomes with simultaneous installation are ignored: the leader's
   re-optimization excludes policies that make the follower enter at once,
   and no coordination-failure term is priced.
5. `mutual_waiting_claim` prices the candidate outcome in which neither firm
   invests before the switch. It assumes rent equalization in the post-switch
   game, so each firm is worth the value of a follower facing an H-regime
   leader, whose scale follows the same convention as the L-regime leader's
   (K_H*, or re-optimized at its entry demand). It is a supplementary check
   on whether leading at X_P beats mutual waiting, not a full solution of
   the post-switch game.
6. Existence of X_P is established on a finite demand grid and the first
   up-crossing is reported. No uniqueness or equilibrium-selection argument
   is made.

Verification
------------
`finite_difference_subgame` re-solves both claims on a log-demand grid: the
follower by a linear complementarity problem with the obstacle Psi
(primal-dual active set, no assumption on the shape of the exercise region)
and the leader by the linear system with a Dirichlet condition on the
follower's exercise set. It shares the post-switch sub-problem with the
Green's-function solution and nothing else. With the rival's capacity set to
zero the follower's problem is the single-firm problem of `piecewise_option`,
whose closed forms and envelope results the tests reproduce.

Run ``uv run python -m ai_lab_investment.models.preemption_exact`` for the
table over the grid of the issue (about ten minutes).
"""

from dataclasses import dataclass
from functools import lru_cache

import numpy as np
from scipy import integrate, interpolate, linalg, optimize

from .parameters import ModelParameters
from .piecewise_option import (
    PiecewiseOptionModel,
    _negative_root,
    reduced_form_reference,
)

SCALES: tuple[str, ...] = ("precommitted", "envelope")

_PENALTY = 1e20


def contest_revenue(
    own: np.ndarray | float, rival: np.ndarray | float, alpha: float
) -> np.ndarray:
    """Tullock revenue per unit demand, own^{2 alpha} / (own^alpha + rival^alpha).

    Equals own^alpha when the rival has no capacity, and zero when own = 0.
    """
    own_arr = np.asarray(own, dtype=float)
    rival_arr = np.asarray(rival, dtype=float)
    with np.errstate(divide="ignore", invalid="ignore"):
        share = 1.0 / (1.0 + (rival_arr / own_arr) ** alpha)
        out = own_arr**alpha * share
    return np.where(own_arr > 0.0, out, 0.0)


class ForcedClaim:
    """Bounded solution of the L-regime ODE for a given forcing f.

    Solves (sigma^2/2) X^2 P'' + mu_L X P' - (r + lambda) P + f(X) = 0 with
    P bounded at the origin and free of the explosive root at infinity:

        P(X) = kappa [ X^{b-} int_0^X f(y) y^{-b- - 1} dy
                     + X^{b+} int_X^inf f(y) y^{-b+ - 1} dy ],

    b+ and b- the roots of the L-regime characteristic equation and
    kappa = 2 / (sigma^2 (b+ - b-)). The forcing is a sum of powers
    sum_j c_j X^{p_j} below a breakpoint X_b and, above it, either another sum
    of powers (closed form) or a table on a log grid (cumulative Simpson
    quadrature with a power-law tail). Below X_b the solution is

        P(X) = sum_j c_j X^{p_j} / (-Q_L(p_j)) + u X^{b+},

    so the whole forcing above X_b enters through the single number u.
    """

    def __init__(
        self,
        params: ModelParameters,
        X_b: float,
        low: tuple[tuple[float, float], ...],
        high: tuple[tuple[float, float], ...] = (),
        table: tuple[np.ndarray, np.ndarray] | None = None,
    ):
        p = params
        self.bp = p.beta_L
        self.bn = _negative_root(p.sigma, p.mu_L, p.r + p.lam)
        self.kappa = 2.0 / (p.sigma**2 * (self.bp - self.bn))
        self._half_var = 0.5 * p.sigma**2
        self._mu = p.mu_L
        self._discount = p.r + p.lam
        self.X_b = float(X_b)
        self.low = low
        self.high = high
        self.top = float("inf")
        self._spline: interpolate.CubicSpline | None = None

        self._I_b = sum(c * self.X_b ** (q - self.bn) / (q - self.bn) for c, q in low)
        if table is None:
            J = sum(d * self.X_b ** (q - self.bp) / (self.bp - q) for d, q in high)
        else:
            J = self._build_table(*table)
        self.u = self.kappa * (
            J + sum(c * self.X_b ** (q - self.bp) / (q - self.bp) for c, q in low)
        )

    def _Q(self, q: float) -> float:
        return self._half_var * q * (q - 1.0) + self._mu * q - self._discount

    def _build_table(self, y: np.ndarray, f: np.ndarray) -> float:
        """Tabulate P above X_b; returns int_{X_b}^inf f(y) y^{-b+ - 1} dy."""
        z = np.log(y)
        lower = integrate.cumulative_simpson(f * np.exp(-self.bn * z), x=z, initial=0.0)
        # Integrate the decaying integrand from the top down: differencing a
        # cumulative integral taken from X_b loses the far tail to
        # cancellation.
        upper = integrate.cumulative_simpson(
            (f * np.exp(-self.bp * z))[::-1], x=-z[::-1], initial=0.0
        )[::-1]
        elasticity = np.log(f[-1] / f[-9]) / (z[-1] - z[-9])
        tail = f[-1] * y[-1] ** (-self.bp) / (self.bp - elasticity)
        above = tail + upper
        P = self.kappa * (y**self.bn * (self._I_b + lower) + y**self.bp * above)
        if np.any(P <= 0.0):
            msg = "Tabulated claim must be positive for log interpolation"
            raise ValueError(msg)
        self.top = float(y[-1])
        self._spline = interpolate.CubicSpline(z, np.log(P))
        return float(above[0])

    def _above(self, X: np.ndarray) -> np.ndarray:
        if self._spline is not None:
            if np.any(self.top < X):
                msg = f"Demand above the tabulated range (top = {self.top:.4g})"
                raise ValueError(msg)
            return np.exp(self._spline(np.log(X)))
        inner = np.full_like(X, self._I_b)
        outer = np.zeros_like(X)
        for d, q in self.high:
            e = q - self.bn
            inner += d * (X**e - self.X_b**e) / e
            outer += d * X**q / (self.bp - q)
        return self.kappa * (X**self.bn * inner + outer)

    def __call__(self, X: np.ndarray | float) -> np.ndarray:
        X_arr = np.atleast_1d(np.asarray(X, dtype=float))
        out = np.empty_like(X_arr)
        lo = X_arr < self.X_b
        x = X_arr[lo]
        below = self.u * x**self.bp
        for c, q in self.low:
            below += c * x**q / (-self._Q(q))
        out[lo] = below
        if (~lo).any():
            out[~lo] = self._above(X_arr[~lo])
        return out


@dataclass(frozen=True)
class PostSwitchEntry:
    """Follower's absorbing-H entry against a leader with training capacity T_L.

    Attributes:
        X_F: Entry trigger X_F^H.
        K_F: Capacity optimal for entry at X_F^H (all devoted to training).
        B_F: Option coefficient, F^H(X) = B_F X^{beta_H} below X_F^H.
        T_L: Leader's training capacity phi_L K_L (zero: no rival).
    """

    X_F: float
    K_F: float
    B_F: float
    T_L: float


@dataclass(frozen=True)
class PreSwitchEntry:
    """Follower's best pre-switch (L-regime) entry policy.

    Attributes:
        premium: Coefficient h_F >= 0 on X^{beta_L^+}; zero when the follower
            waits for the switch at every demand level.
        X_entry: Pre-switch entry trigger (inf when premium = 0).
        K: Capacity installed at X_entry (nan when premium = 0).
        phi: Training fraction installed at X_entry (nan when premium = 0).
        best_ratio: sup_X Psi(X) / P_F(X) on the search grid, the best
            immediate-exercise value relative to waiting for the switch; it
            is below one exactly when no pre-switch entry pays.
    """

    premium: float
    X_entry: float
    K: float
    phi: float
    best_ratio: float

    @property
    def enters(self) -> bool:
        return self.premium > 0.0


class LeaderSubgame:
    """Exact values after a leader installs (K_L, phi_L) in regime L.

    Attributes:
        post_switch: The follower's absorbing-H entry problem.
        pre_switch: The follower's best pre-switch entry policy.
        follower_claim: P_F, the follower's pure switching value.
        leader_claim: The leader's revenue claim absent pre-switch entry.
    """

    def __init__(self, game: "ExactPreemptionGame", K_L: float, phi_L: float):
        self.game = game
        self.K_L = float(K_L)
        self.phi_L = float(phi_L)
        self.T_L = self.phi_L * self.K_L
        self.N_L = (1.0 - self.phi_L) * self.K_L
        self.post_switch = game.post_switch_entry(self.T_L)
        self.follower_claim = game.follower_claim(self.post_switch)
        self.leader_claim = game.leader_claim(self.K_L, self.phi_L, self.post_switch)
        self.pre_switch = game.pre_switch_entry(self.follower_claim, self.N_L, self.T_L)
        self.leader_premium = 0.0
        if self.pre_switch.enters:
            e = self.pre_switch
            duopoly = game.revenue_coeff(self.phi_L, self.K_L, e.phi, e.K) * e.X_entry
            claim = float(self.leader_claim(e.X_entry)[0])
            self.leader_premium = (duopoly - claim) / e.X_entry**game.bp
        self.sunk = game.cost(self.K_L)

    def _check_domain(self, X: np.ndarray) -> None:
        if np.any(self.pre_switch.X_entry <= X):
            msg = (
                "Values are defined below the follower's pre-switch entry "
                f"trigger X_F^L = {self.pre_switch.X_entry:.6g}"
            )
            raise ValueError(msg)

    def follower_value(self, X: np.ndarray | float) -> np.ndarray:
        """Follower's exact value F(X), for X below its pre-switch trigger."""
        X_arr = np.atleast_1d(np.asarray(X, dtype=float))
        self._check_domain(X_arr)
        return (
            self.follower_claim(X_arr) + self.pre_switch.premium * X_arr**self.game.bp
        )

    def leader_value(self, X: np.ndarray | float) -> np.ndarray:
        """Leader's entry NPV L(X), for X below the follower's pre-switch trigger."""
        X_arr = np.atleast_1d(np.asarray(X, dtype=float))
        self._check_domain(X_arr)
        revenue = self.leader_claim(X_arr) + self.leader_premium * X_arr**self.game.bp
        return revenue - self.sunk

    def gap(self, X: np.ndarray | float) -> np.ndarray:
        """Leader-minus-follower gap L(X) - F(X)."""
        return self.leader_value(X) - self.follower_value(X)


class ExactPreemptionGame:
    """Zero-leverage L-regime preemption game in the exact primitives.

    Args:
        params: Model parameters.
        scale: Post-switch scale assumption for a firm that has not installed
            when the switch arrives: ``"precommitted"`` or ``"envelope"``.
        table_density: Points per decade of the quadrature table used for the
            envelope forcing.
    """

    def __init__(
        self,
        params: ModelParameters,
        scale: str = "precommitted",
        table_density: int = 150,
    ):
        if scale not in SCALES:
            msg = f"scale must be one of {SCALES}, got {scale!r}"
            raise ValueError(msg)
        if params.alpha >= 0.5:
            msg = (
                "The exact preemption diagnostic requires alpha < 1/2 "
                f"(unique envelope capacity), got {params.alpha}"
            )
            raise ValueError(msg)
        p = params
        self.params = params
        self.scale = scale
        self.table_density = table_density
        self.single = PiecewiseOptionModel(params)
        self.X_ref = self.single.X_H
        self.K_ref = self.single.K_H
        self.bp = p.beta_L
        self.bn = _negative_root(p.sigma, p.mu_L, p.r + p.lam)
        self.w_L = 1.0 / (p.r - p.mu_L + p.lam)
        self.w_H = p.lam * p.A_H * self.w_L
        self.phi_star = self.single.base.closed_form_phi_star()
        self.x_search = (1e-4 * self.X_ref, 1e6 * self.X_ref)
        self._subgame = lru_cache(maxsize=256)(self._build_subgame)
        self._waiting: dict[str, ForcedClaim] = {}
        self.post_switch_trigger = float("nan")
        self.post_switch_leader_capacity = float("nan")
        self.post_switch_single_crossing = True

    # ------------------------------------------------------------------
    # Primitives
    # ------------------------------------------------------------------

    def cost(self, K: np.ndarray | float) -> np.ndarray:
        """Operating-cost perpetuity plus investment cost, delta K / r + I(K)."""
        p = self.params
        K_arr = np.asarray(K, dtype=float)
        return p.delta * K_arr / p.r + p.c * K_arr**p.gamma

    def revenue_coeff(
        self,
        phi: np.ndarray | float,
        K: np.ndarray | float,
        phi_rival: float,
        K_rival: float,
    ) -> np.ndarray:
        """Installed L-regime revenue coefficient against an installed rival.

        A_eff of eq-a-eff-duopoly (eq-a-eff when the rival has no capacity).
        Exact once both firms are installed, since no decision remains.
        """
        alpha = self.params.alpha
        phi_arr = np.asarray(phi, dtype=float)
        K_arr = np.asarray(K, dtype=float)
        inference = contest_revenue(
            (1.0 - phi_arr) * K_arr, (1.0 - phi_rival) * K_rival, alpha
        )
        training = contest_revenue(phi_arr * K_arr, phi_rival * K_rival, alpha)
        return self.w_L * inference + self.w_H * training

    # ------------------------------------------------------------------
    # Post-switch (absorbing-H) sub-problem of the follower
    # ------------------------------------------------------------------

    def _share(self, K: np.ndarray | float, T_L: float) -> np.ndarray:
        """Follower's H-regime contest share against training capacity T_L."""
        K_arr = np.asarray(K, dtype=float)
        if T_L <= 0.0:
            return np.ones_like(K_arr)
        return 1.0 / (1.0 + (T_L / K_arr) ** self.params.alpha)

    def post_switch_entry(self, T_L: float) -> PostSwitchEntry:
        """Follower's jointly optimal absorbing-H trigger and capacity.

        Maximizing a(K)^{beta_H} / b(K)^{beta_H - 1}, with a(K) = A_H K^{2
        alpha} / (K^alpha + T_L^alpha) and b(K) = delta K / r + I(K), gives
        alpha beta_H (2 - s(K)) b(K) = (beta_H - 1) K b'(K), whose left side
        less right side is strictly decreasing in K. With T_L = 0 this is the
        single-firm H-regime problem.
        """
        p = self.params
        beta = p.beta_H

        def bracket(log_K: float) -> float:
            K = np.exp(log_K)
            s = float(self._share(K, T_L))
            b = p.delta * K / p.r + p.c * K**p.gamma
            Kb_prime = p.delta * K / p.r + p.gamma * p.c * K**p.gamma
            return p.alpha * beta * (2.0 - s) - (beta - 1.0) * Kb_prime / b

        K_F = float(np.exp(optimize.brentq(bracket, -60.0, 40.0, xtol=1e-13)))
        a = p.A_H * float(contest_revenue(K_F, T_L, p.alpha))
        b = float(self.cost(K_F))
        X_F = beta / (beta - 1.0) * b / a
        B_F = (a * X_F - b) / X_F**beta
        return PostSwitchEntry(X_F=X_F, K_F=K_F, B_F=B_F, T_L=float(T_L))

    def post_switch_capacity(self, X: np.ndarray, T_L: float) -> np.ndarray:
        """Capacity maximizing the follower's immediate absorbing-H NPV at X.

        Solves A_H X alpha K^{alpha-1} s (2 - s) = delta / r + c gamma
        K^{gamma-1} by bisection in log K; the left side over the right is
        decreasing in K because 2 alpha < 1.
        """
        p = self.params
        X_arr = np.atleast_1d(np.asarray(X, dtype=float))
        lo = np.full_like(X_arr, -80.0)
        hi = np.full_like(X_arr, 40.0)
        for _ in range(64):
            mid = 0.5 * (lo + hi)
            K = np.exp(mid)
            s = self._share(K, T_L)
            revenue = p.A_H * X_arr * p.alpha * K ** (p.alpha - 1.0) * s * (2.0 - s)
            marginal_cost = p.delta / p.r + p.c * p.gamma * K ** (p.gamma - 1.0)
            up = revenue > marginal_cost
            lo = np.where(up, mid, lo)
            hi = np.where(up, hi, mid)
        return np.exp(0.5 * (lo + hi))

    def _exercised_capacity(self, X: np.ndarray, entry: PostSwitchEntry) -> np.ndarray:
        """Follower's capacity when it enters at the switch, X >= X_F^H."""
        if self.scale == "precommitted":
            return np.full_like(X, entry.K_F)
        return self.post_switch_capacity(X, entry.T_L)

    def post_switch_value(self, X: np.ndarray, entry: PostSwitchEntry) -> np.ndarray:
        """Follower's absorbing-H value F^H(X) against the installed leader."""
        p = self.params
        X_arr = np.atleast_1d(np.asarray(X, dtype=float))
        out = entry.B_F * X_arr**p.beta_H
        hi = X_arr >= entry.X_F
        if hi.any():
            x = X_arr[hi]
            K = self._exercised_capacity(x, entry)
            a = p.A_H * contest_revenue(K, entry.T_L, p.alpha)
            out[hi] = a * x - self.cost(K)
        return out

    def leader_post_switch_revenue(
        self, X: np.ndarray, K_L: float, phi_L: float, entry: PostSwitchEntry
    ) -> np.ndarray:
        """Leader's H-regime revenue claim when the follower has not installed.

        Monopoly revenue A_H (phi_L K_L)^alpha X less the dilution at the
        follower's entry below X_F^H; the shared duopoly revenue above it,
        where the follower enters at the switch.
        """
        p = self.params
        X_arr = np.atleast_1d(np.asarray(X, dtype=float))
        T_L = phi_L * K_L
        R_H = p.A_H * T_L**p.alpha
        share_at_entry = 1.0 - float(self._share(entry.K_F, T_L)) if T_L > 0 else 0.0
        drop = R_H * entry.X_F * (1.0 - share_at_entry)
        out = R_H * X_arr - drop * (X_arr / entry.X_F) ** p.beta_H
        hi = X_arr >= entry.X_F
        if hi.any() and T_L > 0:
            x = X_arr[hi]
            K_F = self._exercised_capacity(x, entry)
            out[hi] = R_H * (1.0 - self._share(K_F, T_L)) * x
        return out

    # ------------------------------------------------------------------
    # L-regime claims
    # ------------------------------------------------------------------

    def _table_grid(self, X_b: float) -> np.ndarray:
        top = max(1e2 * X_b, 1e2 * self.x_search[1])
        n = int(self.table_density * np.log10(top / X_b)) + 1
        return np.geomspace(X_b, top, n)

    def follower_claim(self, entry: PostSwitchEntry) -> ForcedClaim:
        """P_F: value of waiting for the switch and then holding F^H."""
        p = self.params
        low = ((p.lam * entry.B_F, p.beta_H),)
        if self.scale == "precommitted":
            a = p.A_H * float(contest_revenue(entry.K_F, entry.T_L, p.alpha))
            b = float(self.cost(entry.K_F))
            return ForcedClaim(p, entry.X_F, low, ((p.lam * a, 1.0), (-p.lam * b, 0.0)))
        y = self._table_grid(entry.X_F)
        return ForcedClaim(
            p, entry.X_F, low, table=(y, p.lam * self.post_switch_value(y, entry))
        )

    def leader_claim(
        self, K_L: float, phi_L: float, entry: PostSwitchEntry
    ) -> ForcedClaim:
        """Leader's revenue claim while the follower has not installed.

        Flow X [(1-phi_L) K_L]^alpha plus lambda times
        `leader_post_switch_revenue`; operating costs are netted out
        separately because they are paid in every state.
        """
        p = self.params
        T_L = phi_L * K_L
        flow = ((1.0 - phi_L) * K_L) ** p.alpha
        R_H = p.A_H * T_L**p.alpha
        share = 1.0 - float(self._share(entry.K_F, T_L)) if T_L > 0 else 0.0
        drop = R_H * entry.X_F * (1.0 - share)
        low = (
            (flow + p.lam * R_H, 1.0),
            (-p.lam * drop * entry.X_F ** (-p.beta_H), p.beta_H),
        )
        if self.scale == "precommitted":
            return ForcedClaim(p, entry.X_F, low, ((flow + p.lam * R_H * share, 1.0),))
        y = self._table_grid(entry.X_F)
        forcing = flow * y + p.lam * self.leader_post_switch_revenue(
            y, K_L, phi_L, entry
        )
        return ForcedClaim(p, entry.X_F, low, table=(y, forcing))

    # ------------------------------------------------------------------
    # Follower's pre-switch entry
    # ------------------------------------------------------------------

    def _best_allocation(
        self, K: np.ndarray, N_L: float, T_L: float
    ) -> tuple[np.ndarray, np.ndarray]:
        """Revenue coefficient maximized over phi on a grid, at each capacity."""
        phis = np.linspace(0.005, 0.995, 100)
        alpha = self.params.alpha
        inference = contest_revenue(np.outer(K, 1.0 - phis), N_L, alpha)
        training = contest_revenue(np.outer(K, phis), T_L, alpha)
        coeff = self.w_L * inference + self.w_H * training
        j = np.argmax(coeff, axis=1)
        return coeff[np.arange(len(K)), j], phis[j]

    def pre_switch_entry(
        self, claim: ForcedClaim, N_L: float, T_L: float
    ) -> PreSwitchEntry:
        """Follower's best pre-switch entry against inference/training rival.

        Maximizes the exercise premium [A_eff,F(phi, K) X - b(K) - P_F(X)]
        X^{-beta_L^+} over (X, K, phi): a coarse grid search followed by a
        Nelder-Mead polish. A non-positive supremum means that waiting for
        the switch dominates entry at every demand level and scale searched
        (demand up to 1e6 X_H*); a trigger above that range is reported as no
        entry.
        """
        X = np.geomspace(self.x_search[0], self.x_search[1], 480)
        K = np.exp(
            np.linspace(np.log(self.K_ref) - 16.0, np.log(self.K_ref) + 26.0, 480)
        )
        coeff, phis = self._best_allocation(K, N_L, T_L)
        wait = claim(X)
        obstacle = np.outer(X, coeff) - self.cost(K)[None, :]
        best_ratio = float(np.max(obstacle.max(axis=1) / wait))
        premium = (obstacle - wait[:, None]) * X[:, None] ** (-self.bp)
        i, j = np.unravel_index(int(np.argmax(premium)), premium.shape)
        # A supremum at the top of the demand grid is not an interior trigger.
        if premium[i, j] <= 0.0 or i == len(X) - 1:
            return PreSwitchEntry(
                0.0, float("inf"), float("nan"), float("nan"), best_ratio
            )

        norm = float(premium[i, j])
        rival_K = N_L + T_L
        rival_phi = T_L / rival_K if rival_K > 0 else 0.0

        def neg(v: np.ndarray) -> float:
            log_X, log_K, phi = v
            x = np.exp(log_X)
            if not (self.x_search[0] < x < self.x_search[1]):
                return _PENALTY
            if abs(log_K) > 60.0 or not (1e-4 < phi < 1.0 - 1e-4):
                return _PENALTY
            k = np.exp(log_K)
            a = float(self.revenue_coeff(phi, k, rival_phi, rival_K))
            payoff = a * x - float(self.cost(k)) - float(claim(x)[0])
            return -payoff * x ** (-self.bp) / norm

        start = np.array([np.log(X[i]), np.log(K[j]), phis[j]])
        res = optimize.minimize(
            neg,
            start,
            method="Nelder-Mead",
            options={"maxiter": 4000, "xatol": 1e-10, "fatol": 1e-13},
        )
        log_X, log_K, phi = res.x
        return PreSwitchEntry(
            premium=float(-res.fun * norm),
            X_entry=float(np.exp(log_X)),
            K=float(np.exp(log_K)),
            phi=float(phi),
            best_ratio=best_ratio,
        )

    # ------------------------------------------------------------------
    # Subgames, the single-firm benchmark, and mutual waiting
    # ------------------------------------------------------------------

    def _build_subgame(self, K_L: float, phi_L: float) -> LeaderSubgame:
        return LeaderSubgame(self, K_L, phi_L)

    def subgame(self, K_L: float, phi_L: float) -> LeaderSubgame:
        """Exact values after a leader installs (K_L, phi_L) in regime L."""
        return self._subgame(float(K_L), float(phi_L))

    def single_firm(self) -> PreSwitchEntry:
        """Single-firm benchmark: the follower's problem with no rival.

        Its `enters` flag says whether the monopolist of Internet Appendix B
        has a finite pre-switch trigger under this scale assumption.
        """
        entry = self.post_switch_entry(0.0)
        return self.pre_switch_entry(self.follower_claim(entry), 0.0, 0.0)

    # ------------------------------------------------------------------
    # Post-switch game and the value of mutual waiting
    # ------------------------------------------------------------------

    def post_switch_leader_policy(self, X: float) -> tuple[float, float, float]:
        """H-regime leader's capacity maximizing its own entry NPV at X.

        If neither firm has installed when the switch arrives, the game
        continues in the absorbing regime: a leader entering at X with K (all
        training) earns `leader_post_switch_revenue` less its costs and the
        rival holds `post_switch_value` against it.

        Returns:
            (K, leader NPV, follower value) at the leader's best capacity.
        """
        x = np.array([X])

        def neg(log_K: float) -> float:
            K = float(np.exp(log_K))
            entry = self.post_switch_entry(K)
            revenue = self.leader_post_switch_revenue(x, K, 1.0, entry)[0]
            return -(float(revenue) - float(self.cost(K)))

        coarse = np.log(self.K_ref) + np.linspace(-14.0, 22.0, 73)
        vals = np.array([neg(v) for v in coarse])
        i = int(np.argmin(vals))
        res = optimize.minimize_scalar(
            neg,
            bounds=(coarse[max(i - 1, 0)], coarse[min(i + 1, len(coarse) - 1)]),
            method="bounded",
            options={"xatol": 1e-10},
        )
        K = float(np.exp(res.x))
        follow = float(self.post_switch_value(x, self.post_switch_entry(K))[0])
        return K, float(-res.fun), follow

    def _post_switch_game_claim(self) -> ForcedClaim:
        """Mutual-waiting claim when the H-regime leader re-optimizes scale.

        Rent equalization in the post-switch game: at a switch below the
        H-regime preemption trigger X_P^H each firm is worth the follower's
        option against the leader that enters at X_P^H; at a switch above it
        each is worth the follower's value against a leader entering at once.
        """
        p = self.params
        grid = np.geomspace(1e-3 * self.X_ref, 1e5 * self.X_ref, 97)
        policies = [self.post_switch_leader_policy(float(x)) for x in grid]
        gaps = np.array([lead - follow for _, lead, follow in policies])
        up = np.flatnonzero((gaps[:-1] < 0.0) & (gaps[1:] >= 0.0))
        if gaps[0] >= 0.0 or up.size == 0:
            msg = "No preemption trigger in the post-switch game"
            raise RuntimeError(msg)
        i = int(up[0])
        self.post_switch_single_crossing = bool(np.all(gaps[i + 1 :] >= 0.0))

        def gap(X: float) -> float:
            _, lead, follow = self.post_switch_leader_policy(X)
            return lead - follow

        X_PH = float(optimize.brentq(gap, grid[i], grid[i + 1], rtol=1e-10))
        K_P, _, follow_P = self.post_switch_leader_policy(X_PH)
        self.post_switch_trigger = X_PH
        self.post_switch_leader_capacity = K_P

        y = self._table_grid(X_PH)
        log_K = np.log(np.array([k for k, _, _ in policies]))
        log_grid = np.log(grid)
        slope = (log_K[-1] - log_K[-2]) / (log_grid[-1] - log_grid[-2])
        log_y = np.log(y)
        K_y = np.exp(
            np.where(
                log_y <= log_grid[-1],
                np.interp(log_y, log_grid, log_K),
                log_K[-1] + slope * (log_y - log_grid[-1]),
            )
        )
        values = np.array([
            self.post_switch_value(np.array([x]), self.post_switch_entry(float(k)))[0]
            for x, k in zip(y, K_y, strict=True)
        ])
        low = ((p.lam * follow_P / X_PH**p.beta_H, p.beta_H),)
        return ForcedClaim(p, X_PH, low, table=(y, p.lam * values))

    def mutual_waiting_claim(self, leader: str = "paper") -> ForcedClaim:
        """Value to each firm when neither invests before the switch.

        Priced under rent equalization in the post-switch game, with the
        H-regime leader's scale following the same convention as the
        L-regime leader's: ``"paper"`` holds it at the single-firm scale K_H*
        (each firm is then worth the value of a follower facing that leader
        at every demand level), ``"reoptimized"`` lets the H-regime leader
        choose scale at its entry demand. See simplification 4 of the module
        docstring.
        """
        if leader not in self._waiting:
            if leader == "paper":
                entry = self.post_switch_entry(self.K_ref)
                self._waiting[leader] = self.follower_claim(entry)
            elif leader == "reoptimized":
                self._waiting[leader] = self._post_switch_game_claim()
            else:
                msg = f"leader must be 'paper' or 'reoptimized', got {leader!r}"
                raise ValueError(msg)
        return self._waiting[leader]

    # ------------------------------------------------------------------
    # Rent equalization
    # ------------------------------------------------------------------

    def paper_policy(self) -> tuple[float, float]:
        """Reduced-form monopoly optimum (K*, phi*) of Proposition 1."""
        rf = reduced_form_reference(self.params)
        return rf["K_star"], rf["phi_star"]

    def exact_monopoly_policy(self) -> tuple[float, float]:
        """Exact single-firm optimum (K, phi) with precommitted post-switch scale.

        The paper's leader-scale convention (leader at the monopoly-phase
        optimum) transplanted to the exact problem. The precommitted class is
        used in both scale variants because the unrestricted single firm
        need not invest before the switch at all.
        """
        game = self
        if self.scale != "precommitted":
            game = ExactPreemptionGame(self.params, "precommitted")
        entry = game.single_firm()
        return entry.K, entry.phi

    def _scan_grid(self, sub: LeaderSubgame, n_scan: int) -> np.ndarray:
        top = min(sub.pre_switch.X_entry * (1.0 - 1e-9), 1e4 * self.X_ref)
        return np.geomspace(1e-3 * self.X_ref, top, n_scan)

    def rent_equalization(
        self, K_L: float, phi_L: float, n_scan: int = 600
    ) -> dict[str, float]:
        """First up-crossing of L(X) - F(X) for a fixed leader policy.

        The gap is scanned on a log grid from 1e-3 X_H* up to the follower's
        pre-switch entry trigger (or 1e4 X_H* when it never enters before the
        switch) and the first negative-to-positive sign change is refined
        with Brent's method.

        Returns:
            Dict with ``exists`` (1.0 / 0.0); ``X_P`` (nan when no crossing);
            the number of sign changes on the grid; ``max_gap_over_follower``
            and ``max_lead_over_wait``, the largest (L - F) / F and L / W on
            the grid, W the mutual-waiting value under the ``"paper"``
            convention; the follower's policies; and ``lead_over_wait_at_X_P``
            (nan when no crossing).
        """
        sub = self.subgame(K_L, phi_L)
        grid = self._scan_grid(sub, n_scan)
        gaps = sub.gap(grid)
        wait = self.mutual_waiting_claim("paper")
        changes = np.flatnonzero(np.diff(np.sign(gaps)) != 0)
        up = [int(i) for i in changes if gaps[i] < 0.0 <= gaps[i + 1]]
        out = {
            "K_L": sub.K_L,
            "phi_L": sub.phi_L,
            "exists": 0.0,
            "X_P": float("nan"),
            "n_sign_changes": float(len(changes)),
            "max_gap_over_follower": float(np.max(gaps / sub.follower_value(grid))),
            "max_lead_over_wait": float(np.max(sub.leader_value(grid) / wait(grid))),
            "lead_over_wait_at_X_P": float("nan"),
            "X_F_post_switch": sub.post_switch.X_F,
            "K_F_post_switch": sub.post_switch.K_F,
            "X_F_pre_switch": sub.pre_switch.X_entry,
            "K_F_pre_switch": sub.pre_switch.K,
        }
        if gaps[0] >= 0.0 or not up:
            return out
        i = up[0]
        X_P = float(
            optimize.brentq(
                lambda x: float(sub.gap(x)[0]), grid[i], grid[i + 1], xtol=1e-16
            )
        )
        lead = float(sub.leader_value(X_P)[0])
        out.update({
            "exists": 1.0,
            "X_P": X_P,
            "lead_over_wait_at_X_P": lead / float(wait(X_P)[0]),
        })
        return out

    # ------------------------------------------------------------------
    # Re-optimized leader
    # ------------------------------------------------------------------

    def leader_best_policy(
        self, X: float, start: tuple[float, float] | None = None
    ) -> tuple[float, float, float]:
        """Leader's (K, phi) maximizing its own entry NPV at demand X.

        The follower best-responds to each candidate. Nelder-Mead over
        (log K, phi), warm-started from `start` when given and otherwise run
        from four scales around the reduced-form policy. Policies that make
        the follower enter at once (X at or above its pre-switch trigger) are
        excluded, in keeping with the leader-follower role structure.

        Returns:
            (K_L, phi_L, L(X; K_L, phi_L)).
        """
        norm = float(self.single.pure_switching_value(X))

        def neg(v: np.ndarray) -> float:
            log_K, phi = v
            if abs(log_K) > 30.0 or not (0.01 < phi < 0.99):
                return _PENALTY
            try:
                value = float(self.subgame(np.exp(log_K), phi).leader_value(X)[0])
            except ValueError:
                return _PENALTY
            return -value / norm

        K_0, phi_0 = self.paper_policy()
        cold = [(np.log(K_0) + d, phi_0) for d in (-4.0, -2.0, 0.0, 2.0)]
        warm = [] if start is None else [(np.log(start[0]), start[1])]
        best_val, best_x = _PENALTY, None
        for starts in (warm, cold):
            for s in starts:
                res = optimize.minimize(
                    neg,
                    np.array(s),
                    method="Nelder-Mead",
                    options={"maxiter": 600, "xatol": 1e-7, "fatol": 1e-10},
                )
                if res.fun < best_val:
                    best_val, best_x = float(res.fun), res.x
            if best_x is not None:
                break
        if best_x is None:
            msg = f"Leader re-optimization failed at X = {X:.6g}"
            raise RuntimeError(msg)
        return float(np.exp(best_x[0])), float(best_x[1]), -best_val * norm

    def reoptimized_gap(
        self, X: float, start: tuple[float, float] | None = None
    ) -> tuple[float, float, float, float]:
        """Leader-minus-follower gap at X when the leader re-optimizes scale.

        Returns:
            (gap, K_L, phi_L, L*), with gap = L*(X) - F(X; K_L, phi_L).
        """
        K_L, phi_L, lead = self.leader_best_policy(X, start)
        follow = float(self.subgame(K_L, phi_L).follower_value(X)[0])
        return lead - follow, K_L, phi_L, lead

    def _scan_reoptimized(
        self, grid: np.ndarray
    ) -> tuple[np.ndarray, np.ndarray, np.ndarray, list[tuple[float, float]]]:
        """Re-optimized gap and leader value along a demand grid, warm-started.

        The scan stops at the first demand level at which no leader policy
        keeps the follower out (every candidate triggers its immediate
        entry); the grid is truncated there.
        """
        gaps: list[float] = []
        leads: list[float] = []
        policies: list[tuple[float, float]] = []
        start: tuple[float, float] | None = None
        for X in grid:
            try:
                gap, K_L, phi_L, lead = self.reoptimized_gap(float(X), start)
            except RuntimeError:
                break
            start = (K_L, phi_L)
            gaps.append(gap)
            leads.append(lead)
            policies.append(start)
        n = len(gaps)
        if n < 2:
            msg = "Leader re-optimization failed at the bottom of the scan"
            raise RuntimeError(msg)
        return grid[:n], np.array(gaps), np.array(leads), policies

    def rent_equalization_reoptimized(
        self, n_scan: int = 25, x_range: tuple[float, float] = (0.03, 300.0)
    ) -> dict[str, float]:
        """Rent equalization when the leader chooses scale at the entry demand.

        Solves L*(X_P) = F(X_P; K_L(X_P), phi_L(X_P)) with L*(X) = max_{K,
        phi} L(X; K, phi), scanning a log grid over x_range (in units of the
        single-firm H-regime trigger X_H*) with the leader's optimizer
        warm-started along it, then refining the first up-crossing with
        Brent's method. The mutual-waiting comparison uses the
        ``"reoptimized"`` convention of `mutual_waiting_claim`.
        ``max_gap_over_follower`` is the largest (L* - F) / F on the scan
        grid, a measure of how much leading is preferred where it is.
        """
        grid = np.geomspace(x_range[0] * self.X_ref, x_range[1] * self.X_ref, n_scan)
        wait = self.mutual_waiting_claim("reoptimized")
        grid, gaps, leads, policies = self._scan_reoptimized(grid)
        changes = np.flatnonzero(np.diff(np.sign(gaps)) != 0)
        up = [int(i) for i in changes if gaps[i] < 0.0 <= gaps[i + 1]]
        nan = float("nan")
        out = {
            "exists": 0.0,
            "X_P": nan,
            "K_L": nan,
            "phi_L": nan,
            "n_sign_changes": float(len(changes)),
            "max_gap_over_follower": float(np.max(gaps / (leads - gaps))),
            "max_lead_over_wait": float(np.max(leads / wait(grid))),
            "lead_over_wait_at_X_P": nan,
            "X_F_post_switch": nan,
            "K_F_post_switch": nan,
            "X_F_pre_switch": nan,
        }
        if gaps[0] >= 0.0 or not up:
            return out
        i = up[0]
        warm = {"start": policies[i]}

        def gap(X: float) -> float:
            value, K_L, phi_L, _ = self.reoptimized_gap(X, warm["start"])
            warm["start"] = (K_L, phi_L)
            return value

        X_P = float(optimize.brentq(gap, grid[i], grid[i + 1], rtol=1e-8))
        K_L, phi_L, lead = self.leader_best_policy(X_P, warm["start"])
        sub = self.subgame(K_L, phi_L)
        out.update({
            "exists": 1.0,
            "X_P": X_P,
            "K_L": K_L,
            "phi_L": phi_L,
            "lead_over_wait_at_X_P": lead / float(wait(X_P)[0]),
            "X_F_post_switch": sub.post_switch.X_F,
            "K_F_post_switch": sub.post_switch.K_F,
            "X_F_pre_switch": sub.pre_switch.X_entry,
        })
        return out

    # ------------------------------------------------------------------
    # Independent finite-difference verification
    # ------------------------------------------------------------------

    def _obstacle_on_grid(
        self, X: np.ndarray, N_L: float, T_L: float
    ) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
        """Pre-switch exercise envelope Psi(X) and its maximizers on a grid."""
        K = np.exp(
            np.linspace(np.log(self.K_ref) - 20.0, np.log(self.K_ref) + 30.0, 2000)
        )
        coeff, phis = self._best_allocation(K, N_L, T_L)
        cost = self.cost(K)
        psi = np.empty_like(X)
        K_best = np.empty_like(X)
        phi_best = np.empty_like(X)
        for lo in range(0, len(X), 512):
            chunk = np.outer(X[lo : lo + 512], coeff) - cost[None, :]
            j = np.argmax(chunk, axis=1)
            psi[lo : lo + 512] = chunk[np.arange(len(j)), j]
            K_best[lo : lo + 512] = K[j]
            phi_best[lo : lo + 512] = phis[j]
        return psi, K_best, phi_best

    def finite_difference_subgame(
        self,
        K_L: float,
        phi_L: float,
        n_grid: int = 8001,
        x_range: tuple[float, float] = (1e-5, 1e7),
    ) -> dict[str, np.ndarray | float]:
        """Leader and follower values by finite differences on a log grid.

        The follower's stopping problem is solved as a linear complementarity
        problem with the exercise envelope as obstacle; the leader's claim is
        the linear system with its duopoly value imposed wherever the
        follower exercises. x_range is in units of X_H*.

        Returns:
            Dict with the grid ``X``, the ``leader`` and ``follower`` values,
            the ``gap``, the follower's pre-switch exercise ``boundary`` (inf
            when the exercise set is empty) and the first up-crossing
            ``X_P`` of the gap below that boundary (nan when there is none).
        """
        p = self.params
        T_L = phi_L * K_L
        N_L = (1.0 - phi_L) * K_L
        entry = self.post_switch_entry(T_L)
        X = np.geomspace(x_range[0] * self.X_ref, x_range[1] * self.X_ref, n_grid)

        psi, K_F, phi_F = self._obstacle_on_grid(X, N_L, T_L)
        follower, active = solve_forced_ode(
            X,
            p.lam * self.post_switch_value(X, entry),
            p.sigma,
            p.mu_L,
            p.r + p.lam,
            obstacle=psi,
        )
        leader_forcing = N_L**p.alpha * X + p.lam * self.leader_post_switch_revenue(
            X, K_L, phi_L, entry
        )
        duopoly = np.zeros_like(X)
        if active.any():
            duopoly[active] = (
                self.revenue_coeff(phi_L, K_L, phi_F[active], K_F[active]) * X[active]
            )
        revenue, _ = solve_forced_ode(
            X,
            leader_forcing,
            p.sigma,
            p.mu_L,
            p.r + p.lam,
            fixed=(active, duopoly),
        )
        leader = revenue - float(self.cost(K_L))
        gap = leader - follower
        boundary = float(X[np.argmax(active)]) if active.any() else float("inf")
        below = np.less(X, boundary)
        up = np.flatnonzero((gap[:-1] < 0.0) & (gap[1:] >= 0.0) & below[1:])
        X_P = float("nan")
        if up.size and gap[0] < 0.0:
            i = int(up[0])
            w = -gap[i] / (gap[i + 1] - gap[i])
            X_P = float(np.exp(np.log(X[i]) + w * np.log(X[i + 1] / X[i])))
        return {
            "X": X,
            "leader": leader,
            "follower": follower,
            "gap": gap,
            "boundary": boundary,
            "X_P": X_P,
        }


def _end_condition(
    y: np.ndarray,
    forcing: np.ndarray,
    i: int,
    j: int,
    root: float,
    operator: tuple[float, float, float],
) -> tuple[float, float, float]:
    """End-point row V_i - w V_j = rhs of `solve_forced_ode`.

    The solution near an end is the local power-law particular solution
    forcing / (-Q(elasticity)) plus the homogeneous mode X^root, which the
    row eliminates.

    Returns:
        (w, rhs, particular value at i).
    """
    half_var, mu, discount = operator
    w = float(np.exp(root * (y[i] - y[j])))
    if forcing[i] <= 0.0 or forcing[j] <= 0.0:
        return w, 0.0, 0.0
    e = np.log(forcing[j] / forcing[i]) / (y[j] - y[i])
    q = -(half_var * e * (e - 1.0) + mu * e - discount)
    return w, float((forcing[i] - w * forcing[j]) / q), float(forcing[i] / q)


def solve_forced_ode(
    X: np.ndarray,
    forcing: np.ndarray,
    sigma: float,
    mu: float,
    discount: float,
    obstacle: np.ndarray | None = None,
    fixed: tuple[np.ndarray, np.ndarray] | None = None,
) -> tuple[np.ndarray, np.ndarray]:
    """Finite-difference solve of a forced GBM valuation ODE on a log grid.

    Solves (sigma^2/2) X^2 V'' + mu X V' - discount V + forcing = 0 with
    central differences in log X. With an obstacle the problem is the linear
    complementarity problem min{-(LV + forcing), V - obstacle} = 0, solved by
    the primal-dual active-set iteration, which makes no assumption on the
    shape of the exercise region. Rows flagged in ``fixed`` are Dirichlet
    rows. At the two ends the solution is the local power-law particular
    solution plus the admissible homogeneous mode only (the positive root at
    the bottom, the negative root at the top), so neither the singular mode
    at the origin nor the explosive one at infinity enters; when the obstacle
    exceeds the particular solution at the top, the top row is an exercise
    row.

    Returns:
        (values, active) with ``active`` the exercise set (all False without
        an obstacle).
    """
    n = len(X)
    y = np.log(X)
    dy = y[1] - y[0]
    half_var = 0.5 * sigma**2
    drift = mu - half_var
    sub = -(half_var / dy**2 - drift / (2.0 * dy))
    diag = 2.0 * half_var / dy**2 + discount
    sup = -(half_var / dy**2 + drift / (2.0 * dy))
    spread = np.sqrt(drift**2 + 4.0 * half_var * discount)
    operator = (half_var, mu, discount)
    w_lo, rhs_lo, _ = _end_condition(
        y, forcing, 0, 1, (-drift + spread) / sigma**2, operator
    )
    w_hi, rhs_hi, particular_hi = _end_condition(
        y, forcing, n - 1, n - 2, (-drift - spread) / sigma**2, operator
    )

    pinned = np.zeros(n, dtype=bool)
    target = np.zeros(n)
    if fixed is not None:
        pinned |= fixed[0]
        target[fixed[0]] = fixed[1][fixed[0]]
    if obstacle is not None and obstacle[-1] >= particular_hi:
        pinned[-1], target[-1] = True, obstacle[-1]
    ends = np.zeros(n, dtype=bool)
    ends[0], ends[-1] = not pinned[0], not pinned[-1]
    threshold = np.full(n, -np.inf) if obstacle is None else obstacle

    def solve(active: np.ndarray) -> np.ndarray:
        rows = pinned | active | ends
        ab = np.zeros((3, n))
        ab[0, 1:] = np.where(rows[:-1], 0.0, sup)
        ab[1] = np.where(rows, 1.0, diag)
        ab[2, :-1] = np.where(rows[1:], 0.0, sub)
        rhs = np.where(active, threshold, np.where(pinned, target, forcing))
        if ends[0]:
            ab[0, 1], rhs[0] = -w_lo, rhs_lo
        if ends[-1]:
            ab[2, -2], rhs[-1] = -w_hi, rhs_hi
        return linalg.solve_banded((1, 1), ab, rhs)

    active = np.zeros(n, dtype=bool)
    V = solve(active)
    for _ in range(200):
        residual = np.zeros(n)
        residual[1:-1] = sub * V[:-2] + diag * V[1:-1] + sup * V[2:] - forcing[1:-1]
        updated = np.where(active, residual > 0.0, threshold > V) & ~pinned & ~ends
        if np.array_equal(updated, active):
            return V, active | (pinned & (threshold >= V))
        active = updated
        V = solve(active)
    msg = "Active-set iteration did not converge"
    raise RuntimeError(msg)


# ----------------------------------------------------------------------
# Diagnostic report
# ----------------------------------------------------------------------

#: Grid of the issue: arrival rates and cost convexities.
DIAGNOSTIC_LAMBDAS: tuple[float, ...] = (0.03, 0.05, 0.10, 0.20, 0.50)
DIAGNOSTIC_GAMMAS: tuple[float, ...] = (1.5, 1.9)


def reduced_model_trigger(params: ModelParameters, reoptimized: bool = False) -> float:
    """Preemption trigger of the paper's reduced (pure-power) model.

    Zero leverage. ``reoptimized`` selects the leader-scale sensitivity of
    Internet Appendix B instead of the paper's convention.
    """
    from .duopoly import DuopolyModel

    model = DuopolyModel(params)
    if reoptimized:
        return float(model.solve_preemption_reoptimized_leader()["X_leader"])
    return float(model.solve_preemption_equilibrium()["X_leader"])


def preemption_diagnostic(
    params: ModelParameters | None = None,
    scale: str = "envelope",
    reoptimize: bool = True,
) -> dict[str, float]:
    """Does preemption restore a pre-switch trigger at one calibration?

    Reports the single-firm benchmark and the rent-equalization trigger
    under three leader-scale conventions: the leader at the paper's
    reduced-form (K*, phi*); at the exact monopoly optimum of
    `exact_monopoly_policy`; and (when `reoptimize`) with scale chosen at the
    entry demand, the only one of the three that is a best response in the
    exact game. Each comes with a mutual-waiting comparison.

    Returns:
        Flat dict; keys prefixed ``single_``, ``paper_``, ``mono_`` and
        ``reopt_``. Flags are 1.0 / 0.0 and missing objects are nan.
    """
    if params is None:
        params = ModelParameters()
    game = ExactPreemptionGame(params, scale)
    single = game.single_firm()
    K_star, phi_star = game.paper_policy()
    out: dict[str, float] = {
        "lam": params.lam,
        "gamma": params.gamma,
        "X_H": game.X_ref,
        "phi_star": game.phi_star,
        "single_invests": float(single.enters),
        "single_X": single.X_entry,
        "single_K": single.K,
        "single_best_ratio": single.best_ratio,
        "reduced_X_P": reduced_model_trigger(params),
    }
    paper = game.rent_equalization(K_star, phi_star)
    out.update({f"paper_{key}": value for key, value in paper.items()})
    mono = game.rent_equalization(*game.exact_monopoly_policy())
    out.update({f"mono_{key}": value for key, value in mono.items()})
    if reoptimize:
        reopt = game.rent_equalization_reoptimized()
        out.update({f"reopt_{key}": value for key, value in reopt.items()})
        out["post_switch_trigger"] = game.post_switch_trigger
        out["post_switch_single_crossing"] = float(game.post_switch_single_crossing)
    return out


def diagnostic_grid(
    lambdas: tuple[float, ...] = DIAGNOSTIC_LAMBDAS,
    gammas: tuple[float, ...] = DIAGNOSTIC_GAMMAS,
    scales: tuple[str, ...] = SCALES,
    base_params: ModelParameters | None = None,
    reoptimize: bool = True,
) -> list[dict[str, float | str]]:
    """`preemption_diagnostic` over the grid of the issue."""
    if base_params is None:
        base_params = ModelParameters()
    rows: list[dict[str, float | str]] = []
    for gamma in gammas:
        for lam in lambdas:
            params = base_params.with_param(lam=lam, gamma=gamma)
            for scale in scales:
                row: dict[str, float | str] = {"scale": scale}
                row.update(preemption_diagnostic(params, scale, reoptimize))
                rows.append(row)
    return rows


def _fmt(value: float | str, spec: str = ".5f") -> str:
    if isinstance(value, str):
        return value
    if np.isnan(value):
        return "none"
    if np.isinf(value):
        return "never"
    return format(value, spec)


def format_diagnostic_table(rows: list[dict[str, float | str]]) -> str:
    """Markdown table of `diagnostic_grid` rows."""
    header = (
        "| gamma | lambda | scale | single-firm X* | X_P, leader at (K*, phi*) "
        "| max (L-F)/F | X_P, leader at exact monopoly scale "
        "| X_P, leader re-optimized | K_L | phi_L | phi* "
        "| max (L*-F)/F | L/W at X_P | reduced X_P |"
    )
    lines = [header, "|" + "---|" * 14]
    for row in rows:
        cells = [
            _fmt(row["gamma"], ".1f"),
            _fmt(row["lam"], ".2f"),
            _fmt(row["scale"]),
            _fmt(row["single_X"]),
            _fmt(row["paper_X_P"]),
            _fmt(row["paper_max_gap_over_follower"], "+.3f"),
            _fmt(row["mono_X_P"]),
            _fmt(row.get("reopt_X_P", float("nan"))),
            _fmt(row.get("reopt_K_L", float("nan"))),
            _fmt(row.get("reopt_phi_L", float("nan")), ".4f"),
            _fmt(row["phi_star"], ".4f"),
            _fmt(row.get("reopt_max_gap_over_follower", float("nan")), "+.3f"),
            _fmt(row.get("reopt_lead_over_wait_at_X_P", float("nan")), ".3f"),
            _fmt(row["reduced_X_P"]),
        ]
        lines.append("| " + " | ".join(cells) + " |")
    return "\n".join(lines)


if __name__ == "__main__":  # pragma: no cover
    print(format_diagnostic_table(diagnostic_grid()))
