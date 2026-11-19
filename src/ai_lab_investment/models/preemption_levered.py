"""Preemption game in the exact primitives with shutdown, default and debt.

Model of record for the duopoly (issues #178 and #200). `preemption_exact` solves the
L-regime preemption game in the exact primitives for firms that operate
forever. This module adds the credit primitives of issue #177 to the same
game: every installed firm may stop operating (the unlevered firm at a
shutdown boundary, the levered firm at a default boundary), debt is priced
with the recovery rule of `DuopolyModel.recovery_value`, and the coupon is
either the par coupon r_c * l * I(K) or the fair coupon at which the debt
is worth its proceeds l * I(K) at issuance.

Formulation
-----------
Everything in the module docstring of `preemption_exact` carries over (roles,
the follower's absorbing-H entry problem, the two post-switch scale
assumptions, the leader's four phases, rent equalization). What changes is
the claim each firm holds once installed. With fixed claims q = delta K + C_D:

Absorbing regime H, both firms installed. Leland's closed form with the
H-regime negative root: E^H(X) = a X - q/r + (q/r - a X_D^H) (X / X_D^H)^{b_H^-}
above X_D^H = [b_H^- / (b_H^- - 1)] (q/r) / a and zero below, with a the
firm's H-regime revenue coefficient. Debt is (C_D/r) [1 - (X / X_D^H)^{b_H^-}]
plus the recovery term.

Absorbing regime H, leader installed, follower waiting. The leader's equity
is R X - q/r + g_1 X^{b_H} + g_2 X^{b_H^-} between its boundary and the
follower's trigger X_F^H: value matching and smooth pasting at the boundary
and value matching to the duopoly equity at X_F^H pin (g_1, g_2, boundary).

Regime L. Each claim solves the L-regime ODE with forcing equal to its flow
plus lambda times its H-regime value, which is zero below the H-regime
boundary. The forcing is piecewise a sum of powers (plus a table when the
follower's scale is chosen at the switch), so the bounded particular
solution P is in closed form (`SegmentClaim`) and

    E(X) = P(X) + C X^{b_L^-} + h X^{b_L^+},

with h = 0 unless the follower enters before the switch. The boundary X_D
solves b_L^- P(X_D) = X_D P'(X_D) (value matching and smooth pasting), which
is the coupled regime-switching boundary and not the single-boundary formula
eq-default-boundary. Debt solves the same ODE with forcing C_D + lambda D^H
and the Dirichlet condition D(X_D) = R(X_D).

Entry payoffs. A firm entering at X with capacity K receives E(X) - (1 - l)
I(K), with E evaluated at the par coupon or at the fair coupon for issuance
at X. Under fair pricing this is firm value less I(K), so leverage enters
the entry decision only through the difference between the default boundary
and the shutdown boundary; under par debt at r_c < r it also carries the
financing subsidy.

Conventions
-----------
1. A firm values its claim as if the rival's capacity stayed in the contest
   forever. What happens to a rival's capacity after its default or shutdown
   is not modelled, as in the reduced model.
2. Recovery in regime L is eq-recovery with the exact unlevered asset value:
   (1 - b) times the inference business net of its perpetual operating cost,
   valued with the option to shut it down at its own boundary (the default
   rule "net_with_shutdown", issue #179; "net" omits that option), at most
   the unlevered asset value and the default-free claim. The inference
   business is valued in the single-boundary form of `DuopolyModel`
   (`liquidation_value`), on the flow the leader earns before the follower
   enters. In regime H the inference business has no revenue, so the same
   rule gives zero recovery.
3. The coupon is fixed at issuance. The follower's fair coupon is set at the
   demand at which it enters.
4. The follower's pre-switch entry candidate is located on the claim without
   the default option (a grid search) and polished on the exact claim.
5. The post-switch exercise region of the follower is taken to be an upper
   set, as in `preemption_exact`.

First investment (issue #200)
-----------------------------
Rent equalization gives X_P, the lowest demand at which leading is as good
as following. The benchmark date of first investment is X_L, the trigger of
the leader in the equilibrium with assigned roles: one firm invests at X_L,
the other follows. `assigned_leader_equilibrium` states the strategies and
checks the no-deviation conditions numerically; the leader's and follower's
credit objects, the hitting statistics and every other object of
`equilibrium_record` without the ``rent_eq_`` prefix are evaluated at X_L.
The value of mutual waiting that enters X_L (`mutual_waiting_claim`) prices
the post-switch game on the claims of this module, with the option to stop
and with debt.

None of these uses the beta_H discount factor or the unconditional A_eff
coefficient in regime L. `ExactPreemptionGame` is the nested game in which
firms operate forever and carry no debt.
"""

from bisect import bisect_right
from dataclasses import dataclass
from itertools import pairwise
from math import inf, isfinite
from typing import NamedTuple, cast

import numpy as np
from scipy import interpolate, linalg, optimize

from .parameters import ModelParameters
from .preemption_exact import (
    ExactPreemptionGame,
    ForcedClaim,
    LeaderSubgame,
    PostSwitchEntry,
    PreSwitchEntry,
    contest_revenue,
)

DEBT_CONVENTIONS: tuple[str, ...] = ("par", "fair")

#: Recovery rules of the exact game (see `DuopolyModel.recovery_value`).
RECOVERY_RULES: tuple[str, ...] = ("net_with_shutdown", "net")

Terms = tuple[tuple[float, float], ...]


class PiecewisePowers:
    """A function equal to a sum of powers sum_j c_j X^{q_j} on each segment.

    ``breaks`` are the increasing breakpoints and ``terms[k]`` the (c, q)
    pairs on the k-th segment, the first starting at zero and the last
    unbounded. An empty tuple of terms is the zero function.
    """

    def __init__(
        self, breaks: tuple[float, ...] = (), terms: tuple[Terms, ...] = ((),)
    ):
        if len(terms) != len(breaks) + 1:
            msg = "terms must have one more entry than breaks"
            raise ValueError(msg)
        if any(b1 <= b0 for b0, b1 in pairwise(breaks)):
            msg = f"breaks must be increasing, got {breaks}"
            raise ValueError(msg)
        self.breaks = tuple(float(b) for b in breaks)
        self.terms = tuple(tuple(t) for t in terms)

    @classmethod
    def everywhere(cls, *terms: tuple[float, float]) -> "PiecewisePowers":
        return cls((), (tuple(terms),))

    def _segment(self, x: float) -> int:
        return bisect_right(self.breaks, x)

    def scaled(self, k: float) -> "PiecewisePowers":
        return PiecewisePowers(
            self.breaks,
            tuple(tuple((k * c, q) for c, q in seg) for seg in self.terms),
        )

    def __add__(self, other: "PiecewisePowers") -> "PiecewisePowers":
        breaks = tuple(sorted(set(self.breaks) | set(other.breaks)))
        terms = []
        for i in range(len(breaks) + 1):
            if not breaks:
                rep = 1.0
            elif i == 0:
                rep = 0.5 * breaks[0]
            elif i == len(breaks):
                rep = 2.0 * breaks[-1]
            else:
                rep = float(np.sqrt(breaks[i - 1] * breaks[i]))
            terms.append(
                self.terms[self._segment(rep)] + other.terms[other._segment(rep)]
            )
        return PiecewisePowers(breaks, tuple(terms))

    def splice(self, x: float, upper: "PiecewisePowers") -> "PiecewisePowers":
        """This function below x and ``upper`` at and above it."""
        low = tuple(b for b in self.breaks if b < x)
        high = tuple(b for b in upper.breaks if b > x)
        terms = (
            self.terms[: len(low) + 1] + upper.terms[len(upper.breaks) - len(high) :]
        )
        return PiecewisePowers((*low, float(x), *high), terms)

    def __call__(self, X: np.ndarray | float) -> np.ndarray:
        X_arr = np.atleast_1d(np.asarray(X, dtype=float))
        seg = np.searchsorted(np.asarray(self.breaks), X_arr, side="right")
        out = np.zeros_like(X_arr)
        for k in np.unique(seg):
            mask = seg == k
            for c, q in self.terms[k]:
                out[mask] += c * X_arr[mask] ** q
        return out


class SegmentClaim:
    """Bounded particular solution of the L-regime ODE, piecewise-power forcing.

    P(X) = kappa [X^{b-} int_0^X f y^{-b- - 1} dy + X^{b+} int_X^inf f y^{-b+ - 1} dy],
    the same Green's-function solution as `ForcedClaim`, with f a
    `PiecewisePowers` so that both integrals are in closed form on every
    segment. Also returns X P'(X), which the smooth-pasting conditions need.
    """

    def __init__(self, bn: float, bp: float, kappa: float, forcing: PiecewisePowers):
        self.bn, self.bp, self.kappa = bn, bp, kappa
        self.breaks = np.asarray(forcing.breaks, dtype=float)
        self.terms = forcing.terms
        n = len(self.breaks)
        if any(q <= bn for _, q in self.terms[0]):
            msg = "Forcing is not integrable at the origin"
            raise ValueError(msg)
        if any(q >= bp for _, q in self.terms[-1]):
            msg = "Forcing is not integrable at infinity"
            raise ValueError(msg)
        self.lo = [0.0, *forcing.breaks]
        self.hi = [*forcing.breaks, inf]
        minus = [
            self._integral(self.terms[k], self.lo[k], self.hi[k], bn) for k in range(n)
        ]
        plus = [
            self._integral(self.terms[k], self.lo[k], self.hi[k], bp)
            for k in range(1, n + 1)
        ]
        self.minus_below = np.concatenate([[0.0], np.cumsum(minus)])
        self.plus_above = np.concatenate([np.cumsum(plus[::-1])[::-1], [0.0]])

    @staticmethod
    def _power(x: float, e: float) -> float:
        if x == 0.0:
            if e <= 0.0:
                msg = "Forcing is not integrable at the origin"
                raise ValueError(msg)
            return 0.0
        if not isfinite(x):
            if e >= 0.0:
                msg = "Forcing is not integrable at infinity"
                raise ValueError(msg)
            return 0.0
        return x**e

    def _integral(self, terms: Terms, a: float, b: float, root: float) -> float:
        total = 0.0
        for c, q in terms:
            e = q - root
            total += c * (self._power(b, e) - self._power(a, e)) / e
        return total

    def value_slope(self, X: np.ndarray | float) -> tuple[np.ndarray, np.ndarray]:
        """(P(X), X P'(X))."""
        X_arr = np.atleast_1d(np.asarray(X, dtype=float))
        seg = np.searchsorted(self.breaks, X_arr, side="right")
        low = self.minus_below[seg].copy()
        high = self.plus_above[seg].copy()
        for k in np.unique(seg):
            mask = seg == k
            x = X_arr[mask]
            a, b = self.lo[k], self.hi[k]
            for c, q in self.terms[k]:
                e = q - self.bn
                low[mask] += c * (x**e - (a**e if a > 0.0 else 0.0)) / e
                e = q - self.bp
                high[mask] += c * ((b**e if isfinite(b) else 0.0) - x**e) / e
        lower = X_arr**self.bn * low
        upper = X_arr**self.bp * high
        return (
            self.kappa * (lower + upper),
            self.kappa * (self.bn * lower + self.bp * upper),
        )


class Particular:
    """Particular solution: a closed-form part plus an optional tabulated part.

    The tabulated part is a `ForcedClaim` whose forcing vanishes below its
    breakpoint, where it is a multiple of X^{b+}. Slopes are available below
    that breakpoint only, which is where every boundary of the game lies.
    """

    def __init__(self, closed: SegmentClaim, table: ForcedClaim | None = None):
        self.closed = closed
        self.table = table
        self.slope_limit = inf if table is None else table.X_b

    def value(self, X: np.ndarray | float) -> np.ndarray:
        out = self.closed.value_slope(X)[0]
        if self.table is not None:
            out = out + self.table(X)
        return out

    def value_slope(self, X: np.ndarray | float) -> tuple[np.ndarray, np.ndarray]:
        P, XdP = self.closed.value_slope(X)
        if self.table is not None:
            X_arr = np.atleast_1d(np.asarray(X, dtype=float))
            if np.any(X_arr >= self.table.X_b):
                msg = "Slope requested above the tabulated breakpoint"
                raise ValueError(msg)
            tail = self.table.u * X_arr**self.table.bp
            P, XdP = P + tail, XdP + self.table.bp * tail
        return P, XdP


@dataclass(frozen=True)
class InstalledClaims:
    """Equity and debt of an installed firm in regime L.

    E(X) = P_E(X) + C_E X^{b-} + h_E X^{b+} above ``X_D`` and zero at or
    below it; D(X) likewise above ``X_D`` and ``recovery`` at or below it.
    ``X_top`` is the demand at which the claim ends because the follower
    enters before the switch (inf otherwise).
    """

    coupon: float
    X_D: float
    recovery: float
    X_top: float
    bn: float
    bp: float
    equity_particular: Particular
    equity_coefs: tuple[float, float]
    debt_particular: Particular | None
    debt_coefs: tuple[float, float]

    def _evaluate(
        self,
        X: np.ndarray | float,
        particular: Particular,
        coefs: tuple[float, float],
        floor: float,
    ) -> np.ndarray:
        X_arr = np.atleast_1d(np.asarray(X, dtype=float))
        out = np.full_like(X_arr, floor)
        alive = X_arr > self.X_D
        if alive.any():
            x = X_arr[alive]
            out[alive] = (
                particular.value(x) + coefs[0] * x**self.bn + coefs[1] * x**self.bp
            )
        return out

    def equity(self, X: np.ndarray | float) -> np.ndarray:
        """Going-concern equity value (before the sunk contribution)."""
        return self._evaluate(X, self.equity_particular, self.equity_coefs, 0.0)

    def debt(self, X: np.ndarray | float) -> np.ndarray:
        """Debt value; zero when there is no coupon."""
        if self.debt_particular is None:
            return np.zeros_like(np.atleast_1d(np.asarray(X, dtype=float)))
        return self._evaluate(X, self.debt_particular, self.debt_coefs, self.recovery)


class LeveredSubgame(LeaderSubgame):
    """Exact values after a leader installs (K_L, phi_L) in regime L.

    Counterpart of `preemption_exact.LeaderSubgame` with the option to stop
    operating and, under leverage, debt. The follower's policies do not
    depend on the leader's coupon (convention 1 of the module docstring).
    """

    def __init__(self, game: "LeveredPreemptionGame", K_L: float, phi_L: float):
        # The base constructor is not called: it would build the claims
        # without credit, none of which is used here.
        self.game: LeveredPreemptionGame = game
        self.K_L = float(K_L)
        self.phi_L = float(phi_L)
        self.T_L = self.phi_L * self.K_L
        self.N_L = (1.0 - self.phi_L) * self.K_L
        self.sunk = (1.0 - game.leverage) * game.investment_cost(self.K_L)
        self.post_switch = game.follower_post_switch_entry(self.T_L)
        self.table = game.follower_table(self.post_switch)
        self.follower_claim = game.follower_waiting_claim(self.post_switch, self.table)
        self.pre_switch = game.follower_pre_switch_entry(
            self.follower_claim, self.N_L, self.T_L
        )
        self._claims: dict[float, InstalledClaims] = {}
        self._fair: dict[float, float] = {}

    # -- domain -----------------------------------------------------------

    def _check_domain(self, X: np.ndarray) -> None:
        if np.any(self.pre_switch.X_entry <= X):
            msg = (
                "Values are defined below the follower's pre-switch entry "
                f"trigger X_F^L = {self.pre_switch.X_entry:.6g}"
            )
            raise ValueError(msg)

    # -- follower ---------------------------------------------------------

    def follower_value(self, X: np.ndarray | float) -> np.ndarray:
        """Follower's value F(X), for X below its pre-switch trigger."""
        X_arr = np.atleast_1d(np.asarray(X, dtype=float))
        self._check_domain(X_arr)
        return (
            self.follower_claim(X_arr) + self.pre_switch.premium * X_arr**self.game.bp
        )

    # -- leader -----------------------------------------------------------

    def leader_claims(self, coupon: float) -> InstalledClaims:
        """Leader's equity and debt before follower entry at a given coupon."""
        key = float(coupon)
        if key not in self._claims:
            if len(self._claims) > 64:
                self._claims = {k: v for k, v in self._claims.items() if k == 0.0}
            self._claims[key] = self.game.leader_waiting_claims(self, key)
        return self._claims[key]

    def leader_coupon(self, X: float) -> float:
        """Coupon in force for a leader entering at X."""
        game = self.game
        proceeds = game.leverage * game.investment_cost(self.K_L)
        if proceeds <= 0.0:
            return 0.0
        if game.debt == "par":
            return game.coupon_rate * proceeds
        key = float(X)
        if key not in self._fair:
            self._fair[key] = game.solve_fair_coupon(self.leader_claims, key, proceeds)
        return self._fair[key]

    def leader_value(self, X: np.ndarray | float) -> np.ndarray:
        """Leader's entry NPV L(X) = E_L(X) - (1 - l) I(K_L)."""
        X_arr = np.atleast_1d(np.asarray(X, dtype=float))
        self._check_domain(X_arr)
        if self.game.debt == "par" or self.game.leverage <= 0.0:
            claims = self.leader_claims(self.leader_coupon(float(X_arr[0])))
            return claims.equity(X_arr) - self.sunk
        out = np.empty_like(X_arr)
        for i, x in enumerate(X_arr):
            try:
                claims = self.leader_claims(self.leader_coupon(float(x)))
                out[i] = claims.equity(x)[0] - self.sunk
            except ValueError:
                # No fair coupon: the proceeds exceed the debt capacity at x.
                out[i] = -self.game.investment_cost(self.K_L)
        return out

    def gap(self, X: np.ndarray | float) -> np.ndarray:
        """Leader-minus-follower gap L(X) - F(X)."""
        return self.leader_value(X) - self.follower_value(X)

    def leader_credit(self, X: float) -> dict[str, float]:
        """Leader's credit objects for entry at demand X.

        Returns the coupon, the default (or shutdown) boundary, equity and
        debt values, recovery, the spread C_D / D - r and the distance to
        default X / X_D. Without debt the spread is nan.
        """
        game = self.game
        coupon = self.leader_coupon(X)
        claims = self.leader_claims(coupon)
        debt = float(claims.debt(X)[0])
        proceeds = game.leverage * game.investment_cost(self.K_L)
        return {
            "coupon": coupon,
            "coupon_rate": coupon / proceeds if proceeds > 0.0 else float("nan"),
            "X_default": claims.X_D,
            "distance_to_default": X / claims.X_D,
            "equity": float(claims.equity(X)[0]),
            "debt": debt,
            "proceeds": proceeds,
            "recovery": claims.recovery,
            "spread": coupon / debt - game.params.r if debt > 0.0 else float("nan"),
        }


class LeveredPreemptionGame(ExactPreemptionGame):
    """L-regime preemption game in the exact primitives with credit.

    Args:
        params: Model parameters.
        scale: Post-switch scale assumption, ``"precommitted"`` or
            ``"envelope"`` (scale chosen at the switch).
        leverage: Debt proceeds as a fraction of I(K), common to both firms.
        coupon_rate: Par coupon rate r_c.
        bankruptcy_cost: Fraction b of the liquidation value lost in default.
        debt: ``"par"`` (coupon r_c * l * I) or ``"fair"`` (coupon at which
            debt is worth l * I at issuance).
        table_density: Points per decade of the quadrature tables.
        recovery_rule: ``"net_with_shutdown"`` (default) or ``"net"``; see
            convention 2 of the module docstring.
        contest: ``"tullock"`` (the model of record) or ``"arithmetic_mean"``
            (`preemption_exact.contest_revenue`).
    """

    def __init__(
        self,
        params: ModelParameters,
        scale: str = "envelope",
        leverage: float = 0.0,
        coupon_rate: float = 0.05,
        bankruptcy_cost: float = 0.30,
        debt: str = "par",
        table_density: int = 150,
        recovery_rule: str = "net_with_shutdown",
        contest: str = "tullock",
    ):
        super().__init__(params, scale, table_density, contest)
        if debt not in DEBT_CONVENTIONS:
            msg = f"debt must be one of {DEBT_CONVENTIONS}, got {debt!r}"
            raise ValueError(msg)
        if recovery_rule not in RECOVERY_RULES:
            msg = (
                f"recovery_rule must be one of {RECOVERY_RULES}, got {recovery_rule!r}"
            )
            raise ValueError(msg)
        self.recovery_rule = recovery_rule
        if not 0.0 <= leverage < 1.0:
            msg = f"Leverage must be in [0, 1), got {leverage}"
            raise ValueError(msg)
        p = params
        self.leverage = float(leverage)
        self.coupon_rate = float(coupon_rate)
        self.bankruptcy_cost = float(bankruptcy_cost)
        self.debt = debt
        self.bn_H = self._root(p.mu_H, p.r, -1.0)
        self.m_H = self.bn_H / (self.bn_H - 1.0)
        self.m_L = self.bn / (self.bn - 1.0)
        self.kappa = 2.0 / (p.sigma**2 * (self.bp - self.bn))
        # Claim without the default option: under par debt the subsidy scales
        # the capital cost by 1 - l (1 - r_c / r); under fair debt it is the
        # unlevered claim. Used to start the searches only.
        scale_c = 1.0
        if debt == "par":
            scale_c = 1.0 - self.leverage * (1.0 - self.coupon_rate / p.r)
        self.proxy = ExactPreemptionGame(
            p.with_param(c=p.c * scale_c), scale, table_density, contest
        )
        self._boundary_grid = np.geomspace(1e-7 * self.X_ref, 1e5 * self.X_ref, 480)
        self._fair_rate: float | None = None
        self._response: interpolate.CubicSpline | None = None

    def _root(self, mu: float, discount: float, sign: float) -> float:
        s2 = self.params.sigma**2
        b = mu - 0.5 * s2
        return (-b + sign * np.sqrt(b * b + 2.0 * s2 * discount)) / s2

    def _build_subgame(self, K_L: float, phi_L: float) -> LeveredSubgame:
        return LeveredSubgame(self, K_L, phi_L)

    def subgame(self, K_L: float, phi_L: float) -> LeveredSubgame:
        """Exact values, with credit, after a leader installs (K_L, phi_L)."""
        return cast("LeveredSubgame", self._subgame(float(K_L), float(phi_L)))

    def investment_cost(self, K: np.ndarray | float) -> np.ndarray | float:
        return self.params.c * K**self.params.gamma

    def mutual_waiting_claim(self, leader: str = "reoptimized") -> ForcedClaim:
        """Value to each firm when neither invests before the switch.

        ``"reoptimized"`` prices the post-switch game on the claims of this
        module: the firm that enters first after the switch chooses its
        scale at its entry demand, both firms may stop operating, debt is
        par or fair as in the rest of the game, and each firm is worth the
        follower's value (rent equalization, see
        `ExactPreemptionGame._post_switch_game_claim`). ``"no_stop"`` is the
        same game without the option to stop and with debt reduced to its
        par subsidy (the value used before issue #200, kept to report the
        difference), and ``"paper"`` holds the post-switch leader at the
        single-firm scale K_H*, also without the option.
        """
        if leader == "paper":
            return self.proxy.mutual_waiting_claim("paper")
        if leader == "no_stop":
            return self.proxy.mutual_waiting_claim("reoptimized")
        return super().mutual_waiting_claim(leader)

    # ------------------------------------------------------------------
    # Post-switch game between two firms that have not installed
    # ------------------------------------------------------------------

    def _follower_response(self, T: float) -> tuple[float, float, float]:
        """Follower's (X_F^H, K_F^H, B_F) against H-regime leader capacity T.

        `follower_post_switch_entry` tabulated on a log grid of T and
        interpolated by cubic splines, because the post-switch game needs it
        at every candidate capacity of the leader. The interpolation error
        is below 1e-6 in relative terms (`tests/test_duopoly_exact.py`).
        """
        if self._response is None:
            log_T = np.log(self.K_ref) + np.linspace(-15.0, 23.0, 153)
            entries = [self.follower_post_switch_entry(float(t)) for t in np.exp(log_T)]
            table = np.log([[e.X_F, e.K_F, e.B_F] for e in entries])
            self._response = interpolate.CubicSpline(log_T, table)
        X_F, K_F, B_F = np.exp(self._response(np.log(T)))
        return float(X_F), float(K_F), float(B_F)

    def _envelope_capacity(self, X: np.ndarray, T: float) -> np.ndarray:
        """Capacity maximizing the follower's levered H-regime entry NPV at X.

        Golden-section search in log K, one decade either side of the
        optimum without the default option.
        """
        log_K = np.log(self.proxy.post_switch_capacity(X, T))
        lo, hi = log_K - 1.0, log_K + 1.0
        ratio = 0.5 * (np.sqrt(5.0) - 1.0)
        x1, x2 = hi - ratio * (hi - lo), lo + ratio * (hi - lo)
        f1 = self.follower_h_payoff(X, np.exp(x1), T)
        f2 = self.follower_h_payoff(X, np.exp(x2), T)
        for _ in range(60):
            left = f1 > f2
            hi = np.where(left, x2, hi)
            lo = np.where(left, lo, x1)
            x1_new = hi - ratio * (hi - lo)
            x2_new = lo + ratio * (hi - lo)
            f1_new = self.follower_h_payoff(X, np.exp(x1_new), T)
            f2_new = self.follower_h_payoff(X, np.exp(x2_new), T)
            x1, x2, f1, f2 = x1_new, x2_new, f1_new, f2_new
        return np.exp(0.5 * (lo + hi))

    def _post_switch_follow_value(self, X: np.ndarray, K: float) -> np.ndarray:
        """Levered value after the switch of the firm facing an installed K."""
        X_arr = np.atleast_1d(np.asarray(X, dtype=float))
        X_F, K_F, B_F = self._follower_response(K)
        out = B_F * X_arr**self.params.beta_H
        hi = X_arr >= X_F
        if hi.any():
            x = X_arr[hi]
            if self.scale == "precommitted":
                capacity = np.full_like(x, K_F)
            else:
                capacity = self._envelope_capacity(x, K)
            out[hi] = self.follower_h_payoff(x, capacity, K)
        return out

    def _post_switch_leader_npv(self, X: float, K: float) -> float:
        """Levered NPV of entering first at X after the switch with K.

        All capacity is in training. Below the follower's trigger the claim
        is that of `_h_leader_waiting`; at or above it the follower enters
        at once and the claim is Leland's duopoly form. The coupon is the
        par coupon or the fair coupon for issuance at X; -inf when the claim
        does not exist or the debt cannot be placed.
        """
        p = self.params
        outlay = float(self.investment_cost(K))
        proceeds = self.leverage * outlay
        R = p.A_H * K**p.alpha
        X_F, K_F, _ = self._follower_response(K)
        if X >= X_F and self.scale != "precommitted":
            K_F = float(self._envelope_capacity(np.array([X]), K)[0])
        a_duo = p.A_H * float(contest_revenue(K, K_F, p.alpha, self.contest))

        def claims(coupon: float) -> tuple[float, PiecewisePowers, PiecewisePowers]:
            q = p.delta * K + coupon
            duopoly = self._h_installed(a_duo, q, coupon)
            if X >= X_F:
                return duopoly
            return self._h_leader_waiting(R, q, coupon, X_F, duopoly[1:], duopoly[1:])

        try:
            if proceeds <= 0.0:
                coupon = 0.0
            elif self.debt == "par":
                coupon = self.coupon_rate * proceeds
            else:
                coupon = p.r * proceeds
                for _ in range(200):
                    X_D, _, debt = claims(coupon)
                    value = float(debt(X)[0]) if X_D < X else 0.0
                    if value <= 0.0:
                        return -inf
                    if abs(value - proceeds) <= 1e-12 * proceeds:
                        break
                    coupon *= proceeds / value
                else:
                    return -inf
            equity = float(claims(coupon)[1](X)[0])
        except ValueError:
            return -inf
        return equity - (1.0 - self.leverage) * outlay

    # ------------------------------------------------------------------
    # Absorbing regime H
    # ------------------------------------------------------------------

    def _h_installed(
        self, a: float, q: float, coupon: float
    ) -> tuple[float, PiecewisePowers, PiecewisePowers]:
        """H-regime boundary, equity and debt of a firm with coefficient a."""
        r = self.params.r
        if a <= 0.0:
            # No H-regime revenue: the firm stops at the switch.
            return inf, PiecewisePowers(), PiecewisePowers()
        X_D = self.m_H * (q / r) / a
        option = (q / r - a * X_D) * X_D ** (-self.bn_H)
        equity = PiecewisePowers(
            (X_D,), ((), ((a, 1.0), (-q / r, 0.0), (option, self.bn_H)))
        )
        if coupon <= 0.0:
            return X_D, equity, PiecewisePowers()
        debt = PiecewisePowers(
            (X_D,),
            ((), ((coupon / r, 0.0), (-coupon / r * X_D ** (-self.bn_H), self.bn_H))),
        )
        return X_D, equity, debt

    def _h_leader_waiting(
        self,
        R: float,
        q: float,
        coupon: float,
        X_F: float,
        duopoly: tuple[PiecewisePowers, PiecewisePowers],
        top: tuple[PiecewisePowers, PiecewisePowers],
    ) -> tuple[float, PiecewisePowers, PiecewisePowers]:
        """H-regime claims of a leader whose follower has not installed.

        ``duopoly`` holds the leader's claims once the follower has entered
        at its trigger (the matching values at X_F) and ``top`` the claims
        to splice in at and above X_F.
        """
        r = self.params.r
        beta, bn = self.params.beta_H, self.bn_H
        if R <= 0.0:
            msg = "Leader without training capacity has no H-regime claim"
            raise ValueError(msg)
        e_F = float(duopoly[0](X_F)[0])
        d_F = float(duopoly[1](X_F)[0])

        def coefficients(X_D: float) -> tuple[float, float]:
            a0 = q / r - R * X_D
            b0 = -R * X_D
            g1 = (b0 - bn * a0) / (beta - bn) / X_D**beta
            g2 = (beta * a0 - b0) / (beta - bn) / X_D**bn
            return g1, g2

        def residual(X_D: float) -> float:
            g1, g2 = coefficients(X_D)
            return R * X_F - q / r + g1 * X_F**beta + g2 * X_F**bn - e_F

        X_mono = self.m_H * (q / r) / R
        if X_mono >= X_F:
            msg = "Leader's H-regime boundary lies above the follower's trigger"
            raise ValueError(msg)
        grid = np.geomspace(X_mono, X_F * (1.0 - 1e-10), 40)
        vals = np.array([residual(x) for x in grid])
        idx = np.flatnonzero((vals[:-1] > 0.0) & (vals[1:] <= 0.0))
        if idx.size == 0:
            msg = "No H-regime boundary for the leader before follower entry"
            raise ValueError(msg)
        i = int(idx[0])
        X_D = float(optimize.brentq(residual, grid[i], grid[i + 1], xtol=1e-18))
        g1, g2 = coefficients(X_D)
        equity = PiecewisePowers(
            (X_D,), ((), ((R, 1.0), (-q / r, 0.0), (g1, beta), (g2, bn)))
        ).splice(X_F, top[0])
        if coupon <= 0.0:
            return X_D, equity, PiecewisePowers()
        # D(X_D) = 0 (no H-regime recovery) and D(X_F) = duopoly debt.
        lhs = np.array([[X_D**beta, X_D**bn], [X_F**beta, X_F**bn]])
        d1, d2 = np.linalg.solve(lhs, np.array([-coupon / r, d_F - coupon / r]))
        debt = PiecewisePowers(
            (X_D,), ((), ((coupon / r, 0.0), (float(d1), beta), (float(d2), bn)))
        ).splice(X_F, top[1])
        return X_D, equity, debt

    # ------------------------------------------------------------------
    # Regime L: boundaries and claims
    # ------------------------------------------------------------------

    def _particular(
        self, forcing: PiecewisePowers, table: ForcedClaim | None = None
    ) -> Particular:
        return Particular(SegmentClaim(self.bn, self.bp, self.kappa, forcing), table)

    def _table_claim(self, y: np.ndarray, f: np.ndarray) -> ForcedClaim | None:
        if not np.any(f > 0.0):
            return None
        return ForcedClaim(self.params, float(y[0]), (), table=(y, np.maximum(f, 0.0)))

    def _free_boundary(
        self,
        part: Particular,
        match: tuple[float, float] | None = None,
        guess: float | None = None,
    ) -> tuple[float, float, float]:
        """Boundary and homogeneous coefficients of an equity claim.

        Without ``match`` the claim is P + C X^{b-} and X_D is the first root
        of b- P(X) - X P'(X) from below, which maximizes the option to stop.
        With ``match = (X_M, v_M)`` the claim also carries h X^{b+} and is
        matched to v_M at X_M. ``guess`` is a first estimate of X_D.

        Returns:
            (X_D, C, h).
        """
        bn = self.bn
        limit = part.slope_limit if match is None else min(part.slope_limit, match[0])

        def condition(x: float) -> float:
            p_x, xdp_x = part.value_slope(x)
            return float(bn * p_x[0] - xdp_x[0])

        def first_root(grid: np.ndarray) -> float | None:
            grid = grid[grid < limit * (1.0 - 1e-9)]
            if grid.size < 2:
                return None
            P, XdP = part.value_slope(grid)
            S = bn * P - XdP
            idx = np.flatnonzero((S[:-1] > 0.0) & (S[1:] <= 0.0))
            if idx.size == 0 or S[0] <= 0.0:
                return None
            i = int(idx[0])
            return float(
                optimize.brentq(condition, grid[i], grid[i + 1], xtol=1e-20, rtol=1e-13)
            )

        # Look near the single-boundary estimate first; the full scan is the
        # fallback and the definition (first root from below).
        X_0 = None
        if guess is not None and guess > 0.0:
            X_0 = first_root(np.geomspace(0.2 * guess, 3.0 * guess, 28))
        if X_0 is None:
            X_0 = first_root(self._boundary_grid)
        if X_0 is None:
            msg = "No default boundary below the follower's entry"
            raise ValueError(msg)
        C_0 = -float(part.value(X_0)[0]) * X_0 ** (-bn)
        if match is None:
            return X_0, C_0, 0.0
        return self._matched_boundary(part, match, X_0, C_0, limit)

    def _matched_boundary(
        self,
        part: Particular,
        match: tuple[float, float],
        X_0: float,
        C_0: float,
        limit: float,
    ) -> tuple[float, float, float]:
        """Boundary of a claim that ends at X_M with value v_M.

        Value matching and smooth pasting at X_D give the loadings on the
        two homogeneous terms as functions of X_D; the value at X_M closes
        the system.
        """
        bn, bp = self.bn, self.bp
        X_M, v_M = match
        P_M = float(part.value(X_M)[0])

        def loadings(x: float) -> tuple[float, float]:
            p_x, xdp_x = part.value_slope(x)
            w = float(bn * p_x[0] - xdp_x[0]) / (bp - bn)
            return -float(p_x[0]) - w, w

        def residual(x: float) -> float:
            u, w = loadings(x)
            return P_M + u * (X_M / x) ** bn + w * (X_M / x) ** bp - v_M

        hi = limit * (1.0 - 1e-9)
        if residual(X_0) <= 0.0 or residual(hi) >= 0.0:
            # Entry does not lower the claim: keep the boundary and match.
            return X_0, C_0, (v_M - P_M - C_0 * X_M**bn) / X_M**bp
        X_D = float(optimize.brentq(residual, X_0, hi, xtol=1e-20, rtol=1e-13))
        u, w = loadings(X_D)
        return X_D, u * X_D ** (-bn), w * X_D ** (-bp)

    def _debt_coefs(
        self,
        part: Particular,
        X_D: float,
        recovery: float,
        match: tuple[float, float] | None,
    ) -> tuple[float, float]:
        bn, bp = self.bn, self.bp
        gap_D = recovery - float(part.value(X_D)[0])
        if match is None:
            return gap_D * X_D ** (-bn), 0.0
        X_M, d_M = match
        lhs = np.array([[X_D**bn, X_D**bp], [X_M**bn, X_M**bp]])
        C, h = np.linalg.solve(lhs, np.array([gap_D, d_M - float(part.value(X_M)[0])]))
        return float(C), float(h)

    def _recovery(
        self, flow: float, N_i: float, X_D: float, coupon: float, unlevered
    ) -> float:
        """eq-recovery at X_D; ``unlevered`` returns the unlevered claims."""
        p = self.params
        if coupon <= 0.0:
            return 0.0
        liquidation = self.liquidation_value(flow, N_i, X_D)
        if liquidation <= 0.0:
            return 0.0
        asset = float(unlevered().equity(X_D)[0])
        return min((1.0 - self.bankruptcy_cost) * min(liquidation, asset), coupon / p.r)

    def liquidation_value(self, flow: float, N_i: float, X: float) -> float:
        """Inference business at X under the game's recovery rule.

        ``flow`` is the inference revenue per unit of demand and ``N_i`` the
        inference capacity. Under "net" the business is a X - c with
        a = flow / (r - mu_L + lambda) and c = delta N_i / r (it can be
        negative); under "net_with_shutdown" its owner may stop at
        X_I = m_L c / a, which adds (c - a X_I) (X / X_I)^{b_L^-} above X_I
        and makes it zero at or below X_I.
        """
        p = self.params
        a = flow * self.w_L
        c = p.delta * N_i / p.r
        if self.recovery_rule == "net" or c <= 0.0:
            return a * X - c
        if a <= 0.0:
            return 0.0
        X_I = self.m_L * c / a
        if X <= X_I:
            return 0.0
        return a * X - c + (c - a * X_I) * (X / X_I) ** self.bn

    def installed_claims(
        self,
        K: float,
        phi: float,
        N_rival: float,
        T_rival: float,
        coupon: float,
    ) -> InstalledClaims:
        """Equity and debt in regime L when both firms are installed.

        With no rival capacity (N_rival = T_rival = 0) this is the installed
        monopolist, whose boundary is the coupled regime-switching boundary.
        """
        p = self.params
        N_i, T_i = (1.0 - phi) * K, phi * K
        flow = float(contest_revenue(N_i, N_rival, p.alpha, self.contest))
        a = p.A_H * float(contest_revenue(T_i, T_rival, p.alpha, self.contest))
        q = p.delta * K + coupon
        _, equity_H, debt_H = self._h_installed(a, q, coupon)
        forcing = PiecewisePowers.everywhere((flow, 1.0), (-q, 0.0)) + equity_H.scaled(
            p.lam
        )
        part_E = self._particular(forcing)
        guess = self.m_L * (q / p.r) / (self.w_L * flow + self.w_H * a / p.A_H)
        X_D, C, _ = self._free_boundary(part_E, guess=guess)
        if coupon <= 0.0:
            return InstalledClaims(
                0.0, X_D, 0.0, inf, self.bn, self.bp, part_E, (C, 0.0), None, (0.0, 0.0)
            )
        recovery = self._recovery(
            flow,
            N_i,
            X_D,
            coupon,
            lambda: self.installed_claims(K, phi, N_rival, T_rival, 0.0),
        )
        part_D = self._particular(
            PiecewisePowers.everywhere((coupon, 0.0)) + debt_H.scaled(p.lam)
        )
        return InstalledClaims(
            coupon,
            X_D,
            recovery,
            inf,
            self.bn,
            self.bp,
            part_E,
            (C, 0.0),
            part_D,
            self._debt_coefs(part_D, X_D, recovery, None),
        )

    def installed_credit(self, K: float, phi: float, X: float) -> dict[str, float]:
        """Credit objects of an installed monopolist that issues debt at X.

        The single firm of the model of record once it has invested: the
        claims of `installed_claims` without a rival (coupled boundary,
        default possible after the switch), under the game's leverage, debt
        convention and recovery rule. Keys as in `LeveredSubgame.leader_credit`.
        """
        proceeds = self.leverage * float(self.investment_cost(K))

        def claims_at(coupon: float) -> InstalledClaims:
            return self.installed_claims(K, phi, 0.0, 0.0, coupon)

        if proceeds <= 0.0:
            coupon = 0.0
        elif self.debt == "par":
            coupon = self.coupon_rate * proceeds
        else:
            coupon = self.solve_fair_coupon(claims_at, X, proceeds)
        claims = claims_at(coupon)
        debt = float(claims.debt(X)[0])
        return {
            "coupon": coupon,
            "coupon_rate": coupon / proceeds if proceeds > 0.0 else float("nan"),
            "X_default": claims.X_D,
            "distance_to_default": X / claims.X_D,
            "equity": float(claims.equity(X)[0]),
            "debt": debt,
            "proceeds": proceeds,
            "recovery": claims.recovery,
            "spread": coupon / debt - self.params.r if debt > 0.0 else float("nan"),
        }

    def _leader_h_duopoly(
        self, y: np.ndarray, T_L: float, K_F: np.ndarray, q: float, coupon: float
    ) -> tuple[np.ndarray, np.ndarray]:
        """Leader's H-regime equity and debt against follower capacity K_F(y)."""
        p = self.params
        a = p.A_H * contest_revenue(T_L, K_F, p.alpha, self.contest)
        X_D = self.m_H * (q / p.r) / a
        alive = y > X_D
        ratio = np.where(alive, y / X_D, 1.0) ** self.bn_H
        equity = np.where(alive, a * y - q / p.r + (q / p.r - a * X_D) * ratio, 0.0)
        debt = np.where(alive, coupon / p.r * (1.0 - ratio), 0.0)
        return equity, debt

    def leader_waiting_claims(
        self, sub: LeveredSubgame, coupon: float
    ) -> InstalledClaims:
        """Leader's equity and debt in regime L while the follower waits."""
        p = self.params
        K_L, phi_L, T_L, N_L = sub.K_L, sub.phi_L, sub.T_L, sub.N_L
        entry = sub.post_switch
        flow = N_L**p.alpha
        R = p.A_H * T_L**p.alpha
        q = p.delta * K_L + coupon
        a_duo = p.A_H * float(contest_revenue(T_L, entry.K_F, p.alpha, self.contest))
        _, eq_duo, debt_duo = self._h_installed(a_duo, q, coupon)
        tables: tuple[ForcedClaim | None, ForcedClaim | None] = (None, None)
        if self.scale == "precommitted":
            top = (eq_duo, debt_duo)
        else:
            top = (PiecewisePowers(), PiecewisePowers())
            if sub.table is None:
                msg = "The envelope scale needs the follower's capacity table"
                raise ValueError(msg)
            y, K_env = sub.table["y"], sub.table["K"]
            eq_y, debt_y = self._leader_h_duopoly(y, T_L, K_env, q, coupon)
            tables = (
                self._table_claim(y, p.lam * eq_y),
                self._table_claim(y, p.lam * debt_y) if coupon > 0.0 else None,
            )
        _, equity_H, debt_H = self._h_leader_waiting(
            R, q, coupon, entry.X_F, (eq_duo, debt_duo), top
        )
        part_E = self._particular(
            PiecewisePowers.everywhere((flow, 1.0), (-q, 0.0)) + equity_H.scaled(p.lam),
            tables[0],
        )
        pre = sub.pre_switch
        X_top = pre.X_entry
        match_E = match_D = None
        if pre.enters:
            duo = self.installed_claims(
                K_L, phi_L, (1.0 - pre.phi) * pre.K, pre.phi * pre.K, coupon
            )
            match_E = (X_top, float(duo.equity(X_top)[0]))
            match_D = (X_top, float(duo.debt(X_top)[0]))
        guess = self.m_L * (q / p.r) / (self.w_L * flow + self.w_H * R / p.A_H)
        X_D, C, h = self._free_boundary(part_E, match_E, guess)
        if coupon <= 0.0:
            return InstalledClaims(
                0.0, X_D, 0.0, X_top, self.bn, self.bp, part_E, (C, h), None, (0.0, 0.0)
            )
        recovery = self._recovery(
            flow, N_L, X_D, coupon, lambda: sub.leader_claims(0.0)
        )
        part_D = self._particular(
            PiecewisePowers.everywhere((coupon, 0.0)) + debt_H.scaled(p.lam),
            tables[1],
        )
        return InstalledClaims(
            coupon,
            X_D,
            recovery,
            X_top,
            self.bn,
            self.bp,
            part_E,
            (C, h),
            part_D,
            self._debt_coefs(part_D, X_D, recovery, match_D),
        )

    def solve_fair_coupon(
        self, claims_at, X: float, proceeds: float, rate: float | None = None
    ) -> float:
        """Smallest coupon at which debt issued at X is worth ``proceeds``.

        ``claims_at(coupon)`` returns the `InstalledClaims` at that coupon.
        Debt value per unit of coupon falls as the coupon rises (the boundary
        rises with it), so the map C -> C * proceeds / D(X; C) is increasing
        and, iterated from the riskless coupon r * proceeds, where risky debt
        is worth less than its proceeds, climbs to the smallest root.
        ``rate`` is an optional starting coupon rate from a nearby solve; the
        iteration then approaches the same root from whichever side it starts
        on, and falls back to the riskless start if it leaves the feasible
        range.

        Raises:
            ValueError: If the proceeds exceed the debt capacity at X.
        """
        starts = [self.params.r] if rate is None else [rate, self.params.r]
        for start in starts:
            coupon = start * proceeds
            for _ in range(200):
                claims = claims_at(coupon)
                value = float(claims.debt(X)[0]) if claims.X_D < X else 0.0
                if value <= 0.0:
                    break
                if abs(value - proceeds) <= 1e-13 * proceeds:
                    self._fair_rate = coupon / proceeds
                    return coupon
                coupon *= proceeds / value
        msg = (
            f"No fair coupon: proceeds {proceeds:.6g} exceed the debt capacity "
            f"at X = {X:.6g}"
        )
        raise ValueError(msg)

    # ------------------------------------------------------------------
    # Follower: absorbing-H entry
    # ------------------------------------------------------------------

    def _fair_coupon_H(
        self, X: np.ndarray, K: np.ndarray, a: np.ndarray, proceeds: np.ndarray
    ) -> np.ndarray:
        """Fair coupon of absorbing-H debt issued at X (nan when infeasible).

        (C/r) [1 - z(C)] = proceeds with z = (X_D(C) / X)^{-b_H^-}, iterated
        as C <- r proceeds / (1 - z(C)) from the riskless coupon, which
        increases to the smallest root.
        """
        p = self.params
        theta = -self.bn_H
        riskless = p.r * proceeds
        coupon = riskless.copy()
        for _ in range(200):
            z = (self.m_H * (p.delta * K + coupon) / (p.r * a * X)) ** theta
            z = np.minimum(z, 1.0 - 1e-12)
            updated = riskless / (1.0 - z)
            if np.all(np.abs(updated - coupon) <= 1e-14 * coupon):
                coupon = updated
                break
            coupon = updated
        z = (self.m_H * (p.delta * K + coupon) / (p.r * a * X)) ** theta
        return np.where(z < 0.99, coupon, np.nan)

    def follower_h_payoff(
        self, X: np.ndarray | float, K: np.ndarray | float, T_L: float
    ) -> np.ndarray:
        """Follower's entry NPV in the absorbing regime, E^H(X) - (1 - l) I(K).

        All capacity is devoted to training. The coupon is the par coupon or
        the fair coupon for issuance at X; an infeasible fair issue returns
        -inf.
        """
        p = self.params
        X_arr, K_arr = np.broadcast_arrays(
            np.atleast_1d(np.asarray(X, dtype=float)),
            np.atleast_1d(np.asarray(K, dtype=float)),
        )
        a = p.A_H * contest_revenue(K_arr, T_L, p.alpha, self.contest)
        outlay = p.c * K_arr**p.gamma
        proceeds = self.leverage * outlay
        if self.leverage <= 0.0:
            coupon = np.zeros_like(K_arr)
        elif self.debt == "par":
            coupon = self.coupon_rate * proceeds
        else:
            coupon = self._fair_coupon_H(X_arr, K_arr, a, proceeds)
        feasible = np.isfinite(coupon)
        coupon = np.where(feasible, coupon, 0.0)
        q = p.delta * K_arr + coupon
        X_D = self.m_H * (q / p.r) / a
        alive = X_arr > X_D
        ratio = np.where(alive, X_arr / X_D, 1.0) ** self.bn_H
        equity = np.where(alive, a * X_arr - q / p.r + (q / p.r - a * X_D) * ratio, 0.0)
        return np.where(feasible, equity - (1.0 - self.leverage) * outlay, -np.inf)

    def follower_post_switch_entry(self, T_L: float) -> PostSwitchEntry:
        """Follower's absorbing-H trigger and capacity on the levered claim.

        Maximizes the option coefficient [E^H(X) - (1 - l) I(K)] X^{-beta_H}
        over (X, K), started at the solution without the default option.
        """
        beta = self.params.beta_H
        start = self.proxy.post_switch_entry(T_L)
        norm = start.B_F

        def neg(v: np.ndarray) -> float:
            x, k = float(np.exp(v[0])), float(np.exp(v[1]))
            payoff = float(self.follower_h_payoff(x, k, T_L)[0])
            if not np.isfinite(payoff):
                return 1e20
            return -payoff * x ** (-beta) / norm

        res = optimize.minimize(
            neg,
            np.log([start.X_F, start.K_F]),
            method="Nelder-Mead",
            options={
                "maxiter": 2000,
                "xatol": 1e-10,
                "fatol": 1e-13,
                "initial_simplex": np.log([start.X_F, start.K_F])
                + np.array([[0.0, 0.0], [0.02, 0.0], [0.0, 0.02]]),
            },
        )
        return PostSwitchEntry(
            X_F=float(np.exp(res.x[0])),
            K_F=float(np.exp(res.x[1])),
            B_F=float(-res.fun * norm),
            T_L=float(T_L),
        )

    def follower_table(self, entry: PostSwitchEntry) -> dict[str, np.ndarray] | None:
        """Follower's capacity and payoff when it enters at the switch.

        Tabulated on the quadrature grid above X_F^H: the capacity that
        maximizes the levered entry NPV at each demand level (``"envelope"``)
        or K_F^H (``"precommitted"``). Not needed, and None, for the
        precommitted scale without a demand-dependent coupon.
        """
        fair = self.debt == "fair" and self.leverage > 0.0
        if self.scale == "precommitted" and not fair:
            return None
        y = self._table_grid(entry.X_F)
        if self.scale == "precommitted":
            K = np.full_like(y, entry.K_F)
        else:
            n = max(int(14 * np.log10(y[-1] / y[0])), 24)
            coarse = np.geomspace(y[0], y[-1], n)
            best = np.log(self._envelope_capacity(coarse, entry.T_L))
            # The jointly optimal capacity is the envelope capacity at X_F^H.
            best[0] = np.log(entry.K_F)
            K = np.exp(interpolate.CubicSpline(np.log(coarse), best)(np.log(y)))
        payoff = self.follower_h_payoff(y, K, entry.T_L)
        if not np.all(np.isfinite(payoff)) or np.any(payoff <= 0.0):
            msg = "Follower's entry payoff at the switch is not positive"
            raise ValueError(msg)
        return {"y": y, "K": K, "payoff": payoff}

    def follower_waiting_claim(
        self, entry: PostSwitchEntry, table: dict[str, np.ndarray] | None
    ) -> ForcedClaim:
        """P_F: value of waiting for the switch and then holding F^H."""
        p = self.params
        low = ((p.lam * entry.B_F, p.beta_H),)
        if table is not None:
            return ForcedClaim(
                p, entry.X_F, low, table=(table["y"], p.lam * table["payoff"])
            )
        # Precommitted scale, coupon independent of demand: closed form.
        a = p.A_H * float(contest_revenue(entry.K_F, entry.T_L, p.alpha, self.contest))
        outlay = float(self.investment_cost(entry.K_F))
        coupon = self.coupon_rate * self.leverage * outlay
        q = p.delta * entry.K_F + coupon
        X_D = self.m_H * (q / p.r) / a
        option = (q / p.r - a * X_D) * X_D ** (-self.bn_H)
        high = (
            (p.lam * a, 1.0),
            (-p.lam * (q / p.r + (1.0 - self.leverage) * outlay), 0.0),
            (p.lam * option, self.bn_H),
        )
        return ForcedClaim(p, entry.X_F, low, high)

    def follower_entry_credit(self, entry: PostSwitchEntry) -> dict[str, float]:
        """Follower's boundary and spread at its post-switch entry.

        The follower enters in the absorbing regime at X_F^H with K_F^H, all
        capacity in training, so its claims are Leland's closed forms with
        zero recovery.
        """
        p = self.params
        X_F, K_F = entry.X_F, entry.K_F
        a = p.A_H * float(contest_revenue(K_F, entry.T_L, p.alpha, self.contest))
        proceeds = self.leverage * float(self.investment_cost(K_F))
        coupon = 0.0
        if proceeds > 0.0 and self.debt == "par":
            coupon = self.coupon_rate * proceeds
        elif proceeds > 0.0:
            coupon = float(
                self._fair_coupon_H(
                    np.array([X_F]),
                    np.array([K_F]),
                    np.array([a]),
                    np.array([proceeds]),
                )[0]
            )
        X_D = self.m_H * ((p.delta * K_F + coupon) / p.r) / a
        debt = coupon / p.r * (1.0 - (X_F / X_D) ** self.bn_H)
        return {
            "X_D_follower": X_D,
            "follower_distance_to_default": X_F / X_D,
            "follower_spread": coupon / debt - p.r if debt > 0.0 else float("nan"),
        }

    # ------------------------------------------------------------------
    # Follower: pre-switch entry
    # ------------------------------------------------------------------

    def follower_l_payoff(
        self, X: float, K: float, phi: float, N_L: float, T_L: float
    ) -> float:
        """Follower's NPV of entering at X in regime L with (K, phi)."""
        proceeds = self.leverage * float(self.investment_cost(K))

        def claims_at(coupon: float) -> InstalledClaims:
            return self.installed_claims(K, phi, N_L, T_L, coupon)

        if proceeds <= 0.0:
            coupon = 0.0
        elif self.debt == "par":
            coupon = self.coupon_rate * proceeds
        else:
            coupon = self.solve_fair_coupon(claims_at, X, proceeds, self._fair_rate)
        equity = float(claims_at(coupon).equity(X)[0])
        return equity - (1.0 - self.leverage) * float(self.investment_cost(K))

    def follower_pre_switch_entry(
        self, claim: ForcedClaim, N_L: float, T_L: float
    ) -> PreSwitchEntry:
        """Follower's best pre-switch entry on the levered claim.

        The candidate comes from the grid search of `preemption_exact` on the
        claim without the default option; whenever that candidate is worth at
        least 97% of waiting it is polished on the exact claim, which decides
        whether the follower enters before the switch.
        """

        def payoff(x: float, k: float, phi: float) -> float:
            try:
                return self.follower_l_payoff(x, k, phi, N_L, T_L)
            except ValueError:
                return -np.inf

        return self.pre_switch_entry(
            claim, N_L, T_L, cost=self.proxy.cost, payoff=payoff, slack=0.97
        )


# ----------------------------------------------------------------------
# Hitting probabilities and times
# ----------------------------------------------------------------------


def hitting_statistics(
    params: ModelParameters, X_from: float, X_to: float
) -> dict[str, float]:
    """First-passage statistics of demand from X_from to the level X_to.

    Demand follows the L-regime GBM until the switch, which arrives at rate
    lambda, and the H-regime GBM afterwards.

    Returns:
        Dict with ``before_switch``, the probability of reaching X_to before
        the switch, (X_to / X_from)^theta with theta the root of
        (sigma^2/2) theta (theta - 1) + mu_L theta - lambda = 0 of the sign
        that makes it a probability; ``no_switch``, the probability of ever
        reaching X_to if the switch never arrived; ``after_switch``, the
        probability of ever reaching X_to from X_from under the H-regime
        dynamics; and ``expected_time_after_switch``, the expected first
        passage time from X_from under the H-regime dynamics (inf when the
        level is reached with probability below one, zero when X_to has
        already been passed in the direction of travel).
    """
    p = params
    s2 = p.sigma**2
    d = float(np.log(X_to / X_from))
    up = d > 0.0
    nu_L = p.mu_L - 0.5 * s2
    nu_H = p.mu_H - 0.5 * s2
    root = np.sqrt(nu_L**2 + 2.0 * s2 * p.lam)
    theta = (-nu_L + (root if up else -root)) / s2

    def ever(nu: float) -> float:
        toward = nu if up else -nu
        return 1.0 if toward >= 0.0 else float(np.exp(-2.0 * abs(nu) * abs(d) / s2))

    toward_H = nu_H if up else -nu_H
    return {
        "before_switch": float(np.exp(-theta * d)),
        "no_switch": ever(nu_L),
        "after_switch": ever(nu_H),
        "expected_time_after_switch": abs(d) / toward_H if toward_H > 0.0 else inf,
    }


def expected_entry_time(params: ModelParameters, X_from: float, X_to: float) -> float:
    """Expected time until demand first exceeds X_to > X_from after the switch.

    The time to the switch plus the expected H-regime passage time from the
    demand level at the switch, when the level X_to matters only after the
    switch (a follower that enters only in regime H). With Y the log demand
    change by the switch, which is two-sided exponential,

        E[tau] = 1/lambda + E[(d - Y)^+] / nu_H,   d = log(X_to / X_from),
        E[(d - Y)^+] = d - nu_L/lambda + w exp(-theta_+ d) / theta_+,

    with theta_+ > 0 > theta_- the roots of (sigma^2/2) theta^2 + nu_L theta
    - lambda = 0 and w = |theta_-| / (theta_+ + |theta_-|). Requires a
    positive H-regime log drift.
    """
    p = params
    s2 = p.sigma**2
    nu_L = p.mu_L - 0.5 * s2
    nu_H = p.mu_H - 0.5 * s2
    if nu_H <= 0.0:
        return inf
    d = float(np.log(X_to / X_from))
    root = np.sqrt(nu_L**2 + 2.0 * s2 * p.lam)
    theta_p = (-nu_L + root) / s2
    theta_n = (nu_L + root) / s2
    w = theta_n / (theta_p + theta_n)
    shortfall = d - nu_L / p.lam + w * np.exp(-theta_p * d) / theta_p
    return float(1.0 / p.lam + shortfall / nu_H)


# ----------------------------------------------------------------------
# First investment: the equilibrium with assigned roles
# ----------------------------------------------------------------------

#: Tolerance of the no-deviation checks, relative to the value compared.
#: A Nelder-Mead solve of the leader's policy is reproducible to about 1e-6
#: in its value.
DEVIATION_TOLERANCE = 1e-5


class EntryScan(NamedTuple):
    """Demand scan behind X_L.

    By default the scan is anchored at two objects that exist at every
    admissible parameterization, the single firm's post-switch trigger
    X_H* and its precommitted-scale pre-switch trigger X*: it runs from
    ``span[0]`` times the lower of the two to ``span[1]`` times the higher,
    with ``points`` points per decade, and is extended by a decade at a time
    (at most `ENTRY_SCAN_EXTENSION` at each end) while the quantity that
    decides the answer peaks at an end. With ``fixed`` the scan is instead
    ``points`` points over ``span`` in units of X_H*, with no extension.
    ``xatol`` is the tolerance on log X_L of the refinement.
    """

    points: float
    span: tuple[float, float]
    xatol: float
    fixed: bool = False


#: Decades by which the scan behind X_L may be extended at each end.
ENTRY_SCAN_EXTENSION = 3


def entry_scan_anchors(game: ExactPreemptionGame) -> tuple[float, float]:
    """(X_H*, X*): the single firm's post-switch and precommitted triggers.

    X* is replaced by X_H* where the precommitted-scale problem has no
    solution on its capacity grid.
    """
    try:
        X_star = float(game.single.precommitted_optimum().X_star)
    except (RuntimeError, ValueError):
        X_star = float("nan")
    if not (isfinite(X_star) and X_star > 0.0):
        X_star = game.X_ref
    return game.X_ref, X_star


def entry_scan_grid(game: ExactPreemptionGame, scan: EntryScan) -> np.ndarray:
    """Initial demand grid of the scan behind X_L (see `EntryScan`)."""
    if scan.fixed:
        low, high = scan.span
        return game.X_ref * np.geomspace(low, high, int(scan.points))
    anchors = entry_scan_anchors(game)
    low, high = scan.span[0] * min(anchors), scan.span[1] * max(anchors)
    n = int(np.ceil(scan.points * np.log10(high / low))) + 1
    return np.geomspace(low, high, n)


def _leader_row(
    game: ExactPreemptionGame, X: float, start: tuple[float, float] | None
) -> tuple[float, float, float, float]:
    K, phi, lead = game.leader_best_policy(X, start)
    follow = float(game.subgame(K, phi).follower_value(X)[0])
    return K, phi, lead, follow


def _scan_leader(
    game: ExactPreemptionGame,
    grid: np.ndarray,
    pivot: int,
    start: tuple[float, float] | None = None,
) -> tuple[np.ndarray, np.ndarray, bool, bool]:
    """Leader's best policy and both roles' values along a demand grid.

    The optimizer starts at ``grid[pivot]`` (from ``start`` when given,
    otherwise cold) and is warm-started outward in both directions. The
    grid is truncated where no leader policy keeps the follower out.

    Returns:
        (grid, table, complete_low, complete_high), with rows (K_L, phi_L,
        L*, F) of the table, and whether the scan reached each end of the
        grid.
    """
    rows: dict[int, tuple[float, float, float, float]] = {}
    for indices in (range(pivot, -1, -1), range(pivot + 1, len(grid))):
        if pivot in indices:
            policy = start
        elif pivot in rows:
            policy = rows[pivot][:2]
        else:
            break
        for i in indices:
            try:
                row = _leader_row(game, float(grid[i]), policy)
            except RuntimeError:
                break
            policy = row[:2]
            rows[i] = row
    kept = sorted(rows)
    if len(kept) < 5 or kept != list(range(kept[0], kept[-1] + 1)):
        msg = "Leader re-optimization failed on the entry scan"
        raise RuntimeError(msg)
    table = np.array([rows[i] for i in kept])
    return grid[kept], table, kept[0] == 0, kept[-1] == len(grid) - 1


def _extend_scan(
    game: ExactPreemptionGame,
    grid: np.ndarray,
    table: np.ndarray,
    points: np.ndarray,
    upward: bool,
) -> tuple[np.ndarray, np.ndarray, bool]:
    """Continue the scan over ``points``, outward from one end of ``grid``.

    Returns the extended grid and table and whether every point was solved
    (the scan stops where no leader policy keeps the follower out).
    """
    edge = -1 if upward else 0
    policy = (float(table[edge, 0]), float(table[edge, 1]))
    rows = []
    for X in points:
        try:
            row = _leader_row(game, float(X), policy)
        except RuntimeError:
            break
        policy = row[:2]
        rows.append(row)
    complete = len(rows) == len(points)
    if not rows:
        return grid, table, complete
    new_grid, new_rows = points[: len(rows)], np.array(rows)
    if upward:
        return np.concatenate([grid, new_grid]), np.vstack([table, new_rows]), complete
    return (
        np.concatenate([new_grid[::-1], grid]),
        np.vstack([new_rows[::-1], table]),
        complete,
    )


def _extend_entry_scan(
    game: ExactPreemptionGame,
    scan: EntryScan,
    grid: np.ndarray,
    table: np.ndarray,
    open_low: bool,
    open_high: bool,
) -> tuple[np.ndarray, np.ndarray, int]:
    """Extend the scan by a decade at an end while the answer peaks there.

    The decisive quantity is h = [L* - W] X^{-beta_L^+} where leading beats
    waiting somewhere on the scan, and L* / W otherwise. An end is extended
    only if the scan reached it, at most `ENTRY_SCAN_EXTENSION` times.

    Returns:
        (grid, table, decades added).
    """
    if scan.fixed:
        return grid, table, 0
    wait = game.mutual_waiting_claim("reoptimized")
    step = float(grid[1] / grid[0])
    n_new = int(np.ceil(scan.points))
    added = {"low": 0, "high": 0}
    while True:
        h = (table[:, 2] - wait(grid)) * grid ** (-game.bp)
        score = h if np.max(h) > 0.0 else table[:, 2] / wait(grid)
        i = int(np.argmax(score))
        if i == 0 and open_low and added["low"] < ENTRY_SCAN_EXTENSION:
            points = grid[0] * step ** -np.arange(1, n_new + 1)
            grid, table, open_low = _extend_scan(game, grid, table, points, False)
            added["low"] += 1
        elif i == len(grid) - 1 and open_high and added["high"] < ENTRY_SCAN_EXTENSION:
            points = grid[-1] * step ** np.arange(1, n_new + 1)
            grid, table, open_high = _extend_scan(game, grid, table, points, True)
            added["high"] += 1
        else:
            return grid, table, added["low"] + added["high"]


def _stopping_check(
    game: ExactPreemptionGame, X: np.ndarray, h: np.ndarray, n_grid: int = 4001
) -> tuple[float, float, np.ndarray]:
    """The leader's stopping problem without an assumption on its shape.

    Given that the rival never invests first, the leader's value less the
    mutual-waiting value, u = V - W, solves the homogeneous L-regime ODE
    where the leader waits and equals g(X) = L*(X) - W(X) where it invests.
    The linear complementarity problem min{-A u, u - g} = 0, with A the
    L-regime operator, is solved on a log grid over the scanned range by
    policy iteration (Howard's algorithm, which converges monotonically
    for the M-matrix that central differences give here), with g
    interpolated from the scan (a cubic spline of g X^{-beta_L^+} in log
    demand). At the bottom of the grid u is proportional to X^{beta_L^+};
    at the top the leader invests if g is positive there and u decays with
    the negative root otherwise.

    Returns:
        (lowest demand of the exercise set, inf when it is empty; 1.0 when
        the exercise set is an upper set of the scanned range; the
        coefficient u X^{-beta_L^+} on the grid points below the exercise
        set).
    """
    p = game.params
    fine = np.geomspace(X[0], X[-1], n_grid)
    y = np.log(fine)
    dy = y[1] - y[0]
    obstacle = interpolate.CubicSpline(np.log(X), h)(y) * fine**game.bp
    half_var = 0.5 * p.sigma**2
    drift = p.mu_L - half_var
    sub = -(half_var / dy**2 - drift / (2.0 * dy))
    diag = 2.0 * half_var / dy**2 + p.r + p.lam
    sup = -(half_var / dy**2 + drift / (2.0 * dy))
    if sub > 0.0 or sup > 0.0:
        msg = "Grid too coarse for a monotone scheme"
        raise ValueError(msg)
    w_lo = float(np.exp(-game.bp * dy))
    w_hi = float(np.exp(game.bn * dy))
    top_stops = obstacle[-1] > 0.0

    def solve(active: np.ndarray) -> np.ndarray:
        ab = np.zeros((3, n_grid))
        ab[0, 1:] = np.where(active[:-1], 0.0, sup)
        ab[1] = np.where(active, 1.0, diag)
        ab[2, :-1] = np.where(active[1:], 0.0, sub)
        rhs = np.where(active, obstacle, 0.0)
        ab[1, 0], ab[0, 1], rhs[0] = 1.0, -w_lo, 0.0
        if not active[-1]:
            ab[1, -1], ab[2, -2], rhs[-1] = 1.0, -w_hi, 0.0
        return linalg.solve_banded((1, 1), ab, rhs)

    active = np.zeros(n_grid, dtype=bool)
    active[-1] = top_stops
    # The boundary can move by one grid point per step, so allow n_grid steps.
    for _ in range(2 * n_grid):
        value = solve(active)
        residual = np.zeros(n_grid)
        residual[1:-1] = sub * value[:-2] + diag * value[1:-1] + sup * value[2:]
        updated = value - obstacle < residual
        updated[0], updated[-1] = False, top_stops
        if np.array_equal(updated, active):
            break
        active = updated
    else:
        msg = "Policy iteration did not converge"
        raise RuntimeError(msg)
    if not active.any():
        return inf, 1.0, value * fine ** (-game.bp)
    first = int(np.argmax(active))
    return (
        float(fine[first]),
        float(np.all(active[first:])),
        value[:first] * fine[:first] ** (-game.bp),
    )


def _spline_peak(X: np.ndarray, h: np.ndarray) -> tuple[float, float]:
    """Maximizer and maximum of a cubic spline of h in log demand."""
    fine = np.geomspace(X[0], X[-1], 20001)
    values = interpolate.CubicSpline(np.log(X), h)(np.log(fine))
    i = int(np.argmax(values))
    return float(fine[i]), float(values[i])


#: Keys of `assigned_leader_equilibrium` evaluated at X_L (nan, or inf for
#: the triggers, when no firm invests before the switch on the scan).
_ENTRY_KEYS: tuple[str, ...] = (
    "X_L",
    "K_L",
    "phi_L",
    "leader_value",
    "follower_value",
    "waiting_value",
    "lead_over_wait",
    "follower_over_leader",
    "X_L_over_X_P",
    "coefficient_ratio",
    "leader_best_other_trigger",
    "coefficient_single_peaked",
    "lcp_trigger",
    "lcp_upper_set",
    "lcp_coefficient_error",
    "follower_margin",
    "follower_margin_to_X_P",
    "follower_margin_if_leading_after_switch",
    "X_L_no_stop",
    "X_L_roles_kept",
    "wait_no_stop_ratio",
)


def assigned_leader_equilibrium(
    game: ExactPreemptionGame,
    X_P: float = float("nan"),
    scan: EntryScan | None = None,
    lead_at_X_P: float = float("nan"),
    start: tuple[float, float] | None = None,
) -> dict[str, float]:
    """First investment when one firm leads and the other follows.

    The equilibrium
    ---------------
    Two symmetric firms, neither installed, demand X in regime L. One firm
    is the designated leader, the other the designated follower.

    - Leader: invest the first time demand is at or above X_L before the
      switch, with the capacity and training fraction that maximize its
      entry value at that demand, L*(X) = max_{K, phi} L(X; K, phi).
    - Follower: do not invest before the leader has; once the leader is
      installed, play the best response of `LeveredSubgame` (enter before
      the switch at X_F^L if that pays, otherwise wait for the switch and
      enter at X_F^H, or at once if demand is already above it).
    - If the switch arrives while neither firm is installed, the firms play
      the post-switch game, in which each is worth the follower's value
      (`mutual_waiting_claim`): the claim on that outcome is W(X).
    - If the designated follower deviates and invests first, the other firm
      plays the follower's best response against it.

    Before the leader invests, with b = beta_L^+ and X below X_L,

        V_lead(X)   = W(X) + [L*(X_L) - W(X_L)] (X / X_L)^b,
        V_follow(X) = W(X) + [F(X_L)  - W(X_L)] (X / X_L)^b,

    with F(X_L) the follower's value against the policy the leader installs
    at X_L. Note that the follower's value before the leader invests is
    V_follow, the value of waiting for the leader's entry or for the switch,
    and not F(X).

    Locating X_L
    ------------
    X_L maximizes h(X) = [L*(X) - W(X)] X^{-b}. It is searched for on the
    demand scan of `EntryScan`, anchored at the single firm's triggers X_H*
    and X* and not at the rent-equalization trigger X_P, so that it is
    located wherever it exists, including where the game has no X_P
    (following beats leading at every scanned demand). The scan point that
    maximizes h is refined by a bounded search between its neighbors. When
    L* <= W at every scanned demand no firm invests before the switch on
    the scan: ``first_investment`` is 0.0, X_L is inf, and
    ``waiting_equilibrium`` says whether mutual waiting is then an
    equilibrium on the scan (no firm gains by investing first, since
    leading pays L* < W, and the post-switch game is a race).

    No-deviation conditions, all checked numerically on the scan
    ------------------------------------------------------------
    1. Leader, among triggers. ``leader_best_other_trigger`` is the largest
       h(X) / h(X_L) over the other scan points, and
       ``coefficient_single_peaked`` says that h rises up to X_L and falls
       above it on the scan.
    2. Leader, among all stopping rules. The linear complementarity problem
       of `_stopping_check` makes no assumption on the shape of the
       investment region: ``lcp_trigger`` is the lowest demand at which it
       invests and ``lcp_upper_set`` says that it invests at every scanned
       demand above it.
    3. Follower, before the leader's entry. Investing first at X pays at
       most L*(X) (the rival then follows), so the condition is V_follow(X)
       >= L*(X) for X <= X_L: ``follower_margin`` is the smallest
       [V_follow(X) - L*(X)] / V_follow(X) on the scan. Because V_follow -
       V_lead = [F(X_L) - L*(X_L)] (X / X_L)^b and V_lead >= L* by condition
       1, it holds whenever the follower is the better-off role at X_L
       (``follower_over_leader`` >= 1), that is, whenever X_L <= X_P, and in
       particular wherever the game has no X_P (F >= L* at every scanned
       demand).
    4. Follower, off the path. If the leader has failed to invest at a
       demand between X_L and X_P, the follower still prefers that the
       leader invest: ``follower_margin_to_X_P`` is the smallest [F(X) -
       L*(X)] / F(X) over the scan points in that range (over every scan
       point above X_L where there is no X_P). Above X_P both firms want to
       lead and the profile is not an equilibrium of those subgames; they
       are reached only if the game starts there.
    5. Follower, after the leader's entry: its policy is the best response
       by construction (checked against a linear complementarity solve in
       the tests).
    6. After a switch with neither firm installed, the post-switch game is
       a race (``post_switch_race``): the trigger an H-regime leader would
       choose if its rival never led lies above the post-switch
       rent-equalization trigger, so valuing each firm at the follower's
       value there is the symmetric outcome of a preemption game.

    ``equilibrium`` is 1.0 when all of them hold on the scan and X_L is
    interior to it. When X_L would lie above X_P the follower prefers to
    preempt and the first investment is at X_P instead.

    What this does not establish: that the conditions hold between scan
    points or outside the scanned range; uniqueness among asymmetric
    equilibria; the symmetric mixed-strategy equilibrium, in which both
    firms would delay between X_L and X_P; how the firms coordinate on
    roles; and the continuation after the switch, which is a selection
    (``X_L_roles_kept`` is the trigger if the leader also led after the
    switch, inf when it would then wait for the switch). Simultaneous
    investment is not priced.

    Args:
        game: The game.
        X_P: Rent-equalization trigger, nan when the game has none. It is
            used only for the checks and ratios that refer to it, never to
            place the scan.
        scan: The scan (`ENTRY_SCAN` by default).
        lead_at_X_P: L*(X_P), for ``coefficient_ratio``; nan if unknown.
        start: Leader's policy (K_L, phi_L) to start the optimizer at the
            scan point nearest X_H*; by default it starts cold.

    Returns:
        Dict with ``first_investment``, ``X_L``, the leader's policy ``K_L``
        and ``phi_L`` there, ``leader_value``, ``follower_value`` and
        ``waiting_value`` at X_L, ``lead_over_wait`` and
        ``follower_over_leader``, ``X_L_over_X_P``, ``coefficient_ratio``
        (h(X_L) / h(X_P)), the checks listed above, ``X_L_no_stop`` and
        ``X_L_roles_kept`` (the trigger under the mutual-waiting value
        without the option to stop, and with the leader's role kept through
        the switch; both located on a spline of the scan),
        ``wait_no_stop_ratio`` (that waiting value over W at X_L, less
        one), ``follower_margin_if_leading_after_switch`` (condition 3 for
        a follower that would be the firm to lead after the switch, whose
        waiting value is `post_switch_leading_claim`),
        ``entry_max_lead_over_wait`` (the largest L* / W on the scan) and
        the scan (``entry_scan_points``, ``entry_scan_low`` and
        ``entry_scan_high`` in units of X_H*, the last two being where the
        scan stopped, and ``entry_scan_extensions``, the decades added).
        Without a first investment the keys evaluated at X_L are nan.
    """
    scan = ENTRY_SCAN if scan is None else scan
    bp = game.bp
    nan = float("nan")
    wait = game.mutual_waiting_claim("reoptimized")
    grid = entry_scan_grid(game, scan)
    pivot = int(np.argmin(np.abs(np.log(grid / game.X_ref))))
    grid, table, open_low, open_high = _scan_leader(game, grid, pivot, start)

    grid, table, extensions = _extend_entry_scan(
        game, scan, grid, table, open_low, open_high
    )
    h = (table[:, 2] - wait(grid)) * grid ** (-bp)
    lead = table[:, 2]
    wait_all = wait(grid)
    race = (
        game.post_switch_assigned_trigger > game.post_switch_trigger
        and game.post_switch_single_crossing
    )
    common = {
        "entry_max_lead_over_wait": float(np.max(lead / wait_all)),
        "post_switch_race": float(race),
        "post_switch_trigger": game.post_switch_trigger,
        "post_switch_assigned_trigger": game.post_switch_assigned_trigger,
        "entry_scan_points": float(len(grid)),
        "entry_scan_low": float(grid[0] / game.X_ref),
        "entry_scan_high": float(grid[-1] / game.X_ref),
        "entry_scan_extensions": float(extensions),
    }
    i = int(np.argmax(h))
    if h[i] <= 0.0:
        # No firm invests before the switch on the scan. Leading pays L* < W
        # at every scanned demand, so (given a race after the switch) no firm
        # gains by investing first, and the follower's condition is moot.
        out = dict.fromkeys(_ENTRY_KEYS, nan) | {"X_L": inf, "X_L_roles_kept": inf}
        return (
            out
            | common
            | {
                "first_investment": 0.0,
                "equilibrium": 0.0,
                "waiting_equilibrium": float(race),
            }
        )
    interior = 0 < i < len(grid) - 1
    policy = {"start": (float(table[i, 0]), float(table[i, 1]))}

    def coefficient(X: float) -> tuple[float, tuple[float, float, float, float]]:
        row = _leader_row(game, X, policy["start"])
        policy["start"] = row[:2]
        return (row[2] - float(wait(X)[0])) * X ** (-bp), row

    if interior:
        res = optimize.minimize_scalar(
            lambda z: -coefficient(float(np.exp(z)))[0] / h[i],
            bounds=(np.log(grid[i - 1]), np.log(grid[i + 1])),
            method="bounded",
            options={"xatol": scan.xatol},
        )
        X_new = float(np.exp(res.x))
        h_new, row = coefficient(X_new)
        if h_new > h[i] and not np.any(np.isclose(grid, X_new, rtol=1e-9)):
            j = int(np.searchsorted(grid, X_new))
            grid = np.insert(grid, j, X_new)
            table = np.insert(table, j, row, axis=0)
            h = np.insert(h, j, h_new)
            i = j
    X_L = float(grid[i])
    K_L, phi_L, lead_L, follow_L = (float(v) for v in table[i])
    lead = table[:, 2]
    wait_all = wait(grid)
    wait_L = float(wait_all[i])
    h_L = float(h[i])

    # 1. The leader among triggers.
    others = np.delete(h, i)
    single_peaked = bool(np.all(np.diff(h[: i + 1]) > 0) and np.all(np.diff(h[i:]) < 0))
    # 2. The leader among all stopping rules.
    lcp_trigger, lcp_upper_set, lcp_coefficient = _stopping_check(game, grid, h)
    lcp_error = (
        float(np.max(np.abs(lcp_coefficient / h_L - 1.0)))
        if lcp_coefficient.size
        else float("nan")
    )
    # 3. The follower before the leader's entry.
    below = grid <= X_L
    v_follow = wait_all[below] + (follow_L - wait_L) * (grid[below] / X_L) ** bp
    follower_margin = float(np.min((v_follow - lead[below]) / v_follow))
    # 4. The follower between X_L and X_P (above X_L where there is no X_P),
    # off the path.
    upper = X_P * (1.0 - 1e-6) if isfinite(X_P) else inf
    between = (grid > X_L) & (grid < upper)
    margin_to_X_P = (
        float(np.min(1.0 - lead[between] / table[between, 3]))
        if between.any()
        else float("nan")
    )
    # 3b. The same if the follower were the firm that leads after the switch.
    leading = game.post_switch_leading_claim()(grid)
    v_alt = leading[below] + (follow_L - leading[i]) * (grid[below] / X_L) ** bp
    follower_margin_alt = float(np.min((v_alt - lead[below]) / v_alt))
    tol = DEVIATION_TOLERANCE
    holds = (
        interior
        and float(np.max(others)) <= h_L * (1.0 + tol)
        and lcp_upper_set == 1.0
        and abs(lcp_trigger / X_L - 1.0) < 0.02
        and follower_margin >= -tol
        and not margin_to_X_P < -tol
        and follow_L >= lead_L * (1.0 - tol)
        and race
    )

    # Sensitivity of the trigger to the mutual-waiting value.
    def other_trigger(claim: ForcedClaim) -> float:
        X_alt, h_alt = _spline_peak(grid, (lead - claim(grid)) * grid ** (-bp))
        return X_alt if h_alt > 0.0 else inf

    h_P = (lead_at_X_P - float(wait(X_P)[0])) * X_P ** (-bp) if isfinite(X_P) else nan
    out = {
        "first_investment": 1.0,
        "X_L": X_L,
        "K_L": K_L,
        "phi_L": phi_L,
        "leader_value": lead_L,
        "follower_value": follow_L,
        "waiting_value": wait_L,
        "lead_over_wait": lead_L / wait_L,
        "follower_over_leader": follow_L / lead_L,
        "X_L_over_X_P": X_L / X_P if isfinite(X_P) else nan,
        "coefficient_ratio": h_L / h_P,
        "equilibrium": float(holds),
        "waiting_equilibrium": 0.0,
        "leader_best_other_trigger": float(np.max(others)) / h_L,
        "coefficient_single_peaked": float(single_peaked),
        "lcp_trigger": lcp_trigger,
        "lcp_upper_set": lcp_upper_set,
        "lcp_coefficient_error": lcp_error,
        "follower_margin": follower_margin,
        "follower_margin_to_X_P": margin_to_X_P,
        "follower_margin_if_leading_after_switch": follower_margin_alt,
    } | common
    if isinstance(game, LeveredPreemptionGame):
        no_stop = game.mutual_waiting_claim("no_stop")
        out["X_L_no_stop"] = other_trigger(no_stop)
        out["wait_no_stop_ratio"] = float(no_stop(X_L)[0]) / wait_L - 1.0
    out["X_L_roles_kept"] = other_trigger(game.post_switch_leading_claim())
    return out


# ----------------------------------------------------------------------
# Equilibrium records
# ----------------------------------------------------------------------

#: Prefix of the record keys evaluated at the rent-equalization trigger.
RENT_EQUALIZATION_PREFIX = "rent_eq_"


def _entry_objects(
    game: LeveredPreemptionGame, sub: LeveredSubgame, X: float
) -> dict[str, float]:
    """Policies, values, credit objects and hitting statistics for entry at X."""
    params = game.params
    credit = sub.leader_credit(X)
    X_F = sub.post_switch.X_F
    out = {
        "K_L": sub.K_L,
        "phi_L": sub.phi_L,
        "X_F": X_F,
        "K_F": sub.post_switch.K_F,
        "X_F_pre_switch": sub.pre_switch.X_entry,
        "leader_value": float(sub.leader_value(X)[0]),
        "follower_value": float(sub.follower_value(X)[0]),
        "leader_investment": float(game.investment_cost(sub.K_L)),
        "X_D_leader": credit["X_default"],
        "distance_to_default": credit["distance_to_default"],
        "coupon_rate": credit["coupon_rate"],
        "debt_value": credit["debt"],
        "debt_proceeds": credit["proceeds"],
        "recovery": credit["recovery"],
        "spread": credit["spread"],
    }
    out.update(game.follower_entry_credit(sub.post_switch))
    follower = hitting_statistics(params, X, X_F)
    leader = hitting_statistics(params, X, credit["X_default"])
    out.update({
        "follower_before_switch": follower["before_switch"],
        "follower_no_switch": follower["no_switch"],
        "follower_time_after_switch": follower["expected_time_after_switch"],
        "follower_expected_entry_time": expected_entry_time(params, X, X_F),
        "leader_default_before_switch": leader["before_switch"],
        "leader_default_no_switch": leader["no_switch"],
    })
    return out


def equilibrium_record(
    params: ModelParameters,
    scale: str = "envelope",
    leverage: float = 0.0,
    debt: str = "par",
    coupon_rate: float = 0.05,
    bankruptcy_cost: float = 0.30,
    n_scan: int = 25,
    x_range: tuple[float, float] = (0.03, 300.0),
    entry_scan: EntryScan | None = None,
    rent_equalization: dict | None = None,
    recovery_rule: str = "net_with_shutdown",
    contest: str = "tullock",
) -> dict[str, float | str]:
    """Duopoly equilibrium with a re-optimizing leader, as a flat record.

    The benchmark is the equilibrium with assigned roles
    (`assigned_leader_equilibrium`): one firm invests first at X_L, the
    trigger it prefers given that its rival follows, and the keys without
    a prefix are evaluated there: ``X_L``, the leader's policy ``K_L`` and
    ``phi_L``, the follower's post-switch trigger and capacity ``X_F`` and
    ``K_F`` against that policy, the values, the leader's credit objects at
    entry, the follower's boundary at its post-switch entry, the
    first-passage statistics of the follower's trigger and of the leader's
    boundary from X_L, and the no-deviation checks.

    The rent-equalization trigger ``X_P``, the lowest demand at which
    leading is as good as following (L*(X_P) = F(X_P), first up-crossing on
    the scan ``x_range``, in units of X_H*), is an upper bound on the date
    of first investment. The same objects evaluated there carry the prefix
    ``rent_eq_``; ``exists``, ``n_sign_changes`` and the scan
    (``scan_points``, ``scan_low``, ``scan_high``) describe that solve.

    X_L is located without reference to X_P (`assigned_leader_equilibrium`
    and `EntryScan`), so it is reported wherever it exists, also where
    there is no rent-equalization trigger on the scan (``exists`` 0.0; the
    record then has no ``rent_eq_`` keys and keeps ``max_gap_over_follower``
    and the ``scan_peak*`` keys of that scan). Where L* <= W at every
    scanned demand, ``first_investment`` is 0.0, X_L is inf and the objects
    at X_L are absent.

    Args:
        entry_scan: The scan behind X_L (`ENTRY_SCAN` by default).
        rent_equalization: A record of an earlier solve of the same cell.
            Its ``X_P``, the leader's policy there and the description of
            its scan are then reused instead of re-solved (the X_P solve
            does not depend on the mutual-waiting value); everything else
            is recomputed. Reuse it across recovery rules only under par
            debt, where the equilibrium does not depend on recovery.
        recovery_rule: Recovery rule of the game (`RECOVERY_RULES`).
        contest: Contest of the game; a record of the arithmetic-mean
            benchmark carries the key ``contest``.

    Missing objects are nan.
    """
    game = LeveredPreemptionGame(
        params,
        scale,
        leverage,
        coupon_rate,
        bankruptcy_cost,
        debt,
        recovery_rule=recovery_rule,
        contest=contest,
    )
    prefix = RENT_EQUALIZATION_PREFIX
    if rent_equalization is None:
        sol = game.rent_equalization_reoptimized(n_scan, x_range)
        scan = (float(n_scan), float(x_range[0]), float(x_range[1]))
    else:
        old = rent_equalization
        sol = {
            "exists": old["exists"],
            "n_sign_changes": old["n_sign_changes"],
            "X_P": old["X_P"],
            "K_L": old.get(prefix + "K_L", old.get("K_L")),
            "phi_L": old.get(prefix + "phi_L", old.get("phi_L")),
        }
        sol |= {
            key: value
            for key, value in old.items()
            if key.startswith("scan_peak")
            or key in ("max_gap_over_follower", "max_lead_over_wait")
        }
        scan = (old["scan_points"], old["scan_low"], old["scan_high"])
    out: dict[str, float | str] = {
        "lam": params.lam,
        "scale": scale,
        "leverage": leverage,
        "debt": debt,
        "recovery_rule": recovery_rule,
        "X_H": game.X_ref,
        "phi_star": game.phi_star,
        "scan_points": scan[0],
        "scan_low": scan[1],
        "scan_high": scan[2],
        "exists": sol["exists"],
        "n_sign_changes": sol["n_sign_changes"],
        "X_P": sol["X_P"],
    }
    if contest != "tullock":
        out["contest"] = contest
    rent: dict[str, float] | None = None
    X_P = float("nan")
    if sol["exists"]:
        X_P = float(sol["X_P"])
        at_X_P = game.subgame(float(sol["K_L"]), float(sol["phi_L"]))
        wait = game.mutual_waiting_claim("reoptimized")
        rent = _entry_objects(game, at_X_P, X_P)
        rent["lead_over_wait"] = rent["leader_value"] / float(wait(X_P)[0])
    else:
        # Why there is no trigger: the largest (L* - F) / F on the scan is
        # negative when following is better at every scanned demand level.
        # The scan point that maximizes [L* - W] X^{-beta_L^+} on that scan
        # is kept for comparison with the located X_L.
        for key, value in sol.items():
            if key.startswith("scan_peak") or key in (
                "max_gap_over_follower",
                "max_lead_over_wait",
            ):
                out[key] = value
    entry = assigned_leader_equilibrium(
        game,
        X_P,
        ENTRY_SCAN if entry_scan is None else entry_scan,
        float("nan") if rent is None else rent["leader_value"],
    )
    out.update(entry)
    if entry["first_investment"]:
        at_X_L = game.subgame(entry["K_L"], entry["phi_L"])
        out.update(_entry_objects(game, at_X_L, entry["X_L"]))
    if rent is not None:
        out.update({prefix + key: value for key, value in rent.items()})
    return out


# ----------------------------------------------------------------------
# Cached equilibria behind the paper's duopoly numbers
# ----------------------------------------------------------------------

#: Arrival rates of the spread-at-entry table (issue #178, comment C23).
GRID_LAMBDAS: tuple[float, ...] = (0.05, 0.10, 0.15, 0.20, 0.25, 0.30, 0.40, 0.50)
#: Leverage levels of that table.
GRID_LEVERAGES: tuple[float, ...] = (0.40, 0.65)


def grid_cells() -> list[tuple[float, str, float, str]]:
    """(lambda, scale, leverage, debt) cells stored in the cache.

    Zero leverage on the arrival rates of `GRID_LAMBDAS` plus 0.03 and
    0.075 (for `fig-competition-effect`); the precommitted-scale variant at
    baseline; leverage 0.20 at baseline; and the spread-at-entry grid under
    both debt conventions.
    """
    cells = [
        (lam, "envelope", 0.0, "par") for lam in sorted({0.03, 0.075, *GRID_LAMBDAS})
    ]
    cells.append((0.10, "precommitted", 0.0, "par"))
    cells += [(0.10, "envelope", 0.20, debt) for debt in DEBT_CONVENTIONS]
    cells += [
        (lam, "envelope", leverage, debt)
        for leverage in GRID_LEVERAGES
        for debt in DEBT_CONVENTIONS
        for lam in GRID_LAMBDAS
    ]
    return cells


#: Cells solved on a narrower demand scan than the default 25 points over
#: [0.03, 300] X_H*. Under fair debt at lambda = 0.05 the follower also
#: enters before the switch, each subgame then needs a fair coupon inside
#: the follower's search, and the full scan would take about five hours per
#: cell. The narrow scan brackets the crossing found at zero leverage
#: (X_P = 0.59 X_H*); it does not show that this crossing is the first one
#: over the wider range.
SCAN_OVERRIDES: dict[tuple[float, str, float, str], tuple[int, tuple[float, float]]] = {
    (0.05, "envelope", leverage, "fair"): (5, (0.3, 1.5)) for leverage in GRID_LEVERAGES
}


#: Default scan behind X_L: ten points per decade from 0.03 times the lower
#: of X_H* and X* to ten times the higher, extended while X_L is at an end,
#: and the tolerance on log X_L of the refinement (`EntryScan`).
ENTRY_SCAN = EntryScan(10, (0.03, 10.0), 1e-4)

#: Cells whose X_L is located on a narrower, fixed scan, for the reason given
#: at `SCAN_OVERRIDES` (one evaluation of the leader's best policy takes
#: several minutes there): seven points from 0.118 to 0.944 X_H*, the range
#: of 0.2 to 1.6 times the X_P found at zero leverage, which brackets X_L
#: there (0.31 X_H*); the no-deviation checks then cover that range only.
ENTRY_SCAN_OVERRIDES: dict[tuple[float, str, float, str], EntryScan] = {
    (0.05, "envelope", leverage, "fair"): EntryScan(7, (0.118, 0.944), 1e-3, True)
    for leverage in GRID_LEVERAGES
}


def _solve_cell(
    cell: tuple[float, str, float, str], previous: dict | None = None
) -> dict[str, float | str]:
    lam, scale, leverage, debt = cell
    n_scan, x_range = SCAN_OVERRIDES.get(cell, (25, (0.03, 300.0)))
    return equilibrium_record(
        ModelParameters().with_param(lam=lam),
        scale,
        leverage,
        debt,
        n_scan=n_scan,
        x_range=x_range,
        entry_scan=ENTRY_SCAN_OVERRIDES.get(cell, ENTRY_SCAN),
        rent_equalization=previous,
    )


def _cell_of(record: dict) -> tuple[float, str, float, str]:
    return (record["lam"], record["scale"], record["leverage"], record["debt"])


def write_equilibrium_grid(
    path: str,
    workers: int = 8,
    fresh: bool = False,
    cells: list[tuple[float, str, float, str]] | None = None,
) -> list[dict]:
    """Solve every cell of `grid_cells` at baseline and write the cache.

    Unless ``fresh``, a cell already in the file at ``path`` keeps its
    rent-equalization trigger and the leader's policy there (the expensive
    demand scan, which does not depend on anything computed afterwards) and
    everything else in the record is recomputed. With ``fresh`` every cell
    is solved from scratch. ``cells`` restricts the solve to some cells (the
    file then holds those only).
    """
    import json
    import os
    from concurrent.futures import ProcessPoolExecutor

    previous: dict[tuple[float, str, float, str], dict] = {}
    if not fresh and os.path.exists(path):
        with open(path) as handle:
            previous = {_cell_of(r): r for r in map(decode_record, json.load(handle))}
    if cells is None:
        cells = grid_cells()
    with ProcessPoolExecutor(max_workers=workers) as pool:
        records = list(
            pool.map(_solve_cell, cells, [previous.get(cell) for cell in cells])
        )
    with open(path, "w") as handle:
        json.dump([encode_record(r) for r in records], handle, indent=2)
        handle.write("\n")
    return records


def encode_record(record: dict) -> dict:
    """Record with non-finite floats as strings, so the cache is strict JSON."""
    return {
        key: repr(value)
        if isinstance(value, float) and not np.isfinite(value)
        else value
        for key, value in record.items()
    }


def decode_record(record: dict) -> dict:
    """Inverse of `encode_record`."""
    tokens = {"inf": inf, "-inf": -inf, "nan": float("nan")}
    return {
        key: tokens.get(value, value) if isinstance(value, str) else value
        for key, value in record.items()
    }


def format_spread_table(records: list[dict]) -> str:
    """Markdown table of the leader's credit objects at its entry X_L (C23)."""
    header = (
        "| leverage | debt | lambda | X_L | X_L / X_P | K_L | X_L / X_D "
        "| spread (bps) | coupon rate | K_F | X_F | equilibrium |"
    )
    lines = [header, "|" + "---|" * 12]
    for rec in sorted(
        records, key=lambda r: (r["scale"], r["leverage"], r["debt"], r["lam"])
    ):
        if rec["scale"] != "envelope":
            continue
        spread = rec.get("spread", float("nan"))
        lines.append(
            f"| {rec['leverage']:.2f} | {rec['debt']} | {rec['lam']:.3f} "
            f"| {rec['X_L']:.6f} | {rec['X_L_over_X_P']:.3f} | {rec['K_L']:.6f} "
            f"| {rec['distance_to_default']:.3f} | {1e4 * spread:.1f} "
            f"| {rec.get('coupon_rate', float('nan')):.4f} "
            f"| {rec['K_F']:.4f} | {rec['X_F']:.5f} | {rec['equilibrium']:.0f} |"
        )
    return "\n".join(lines)


if __name__ == "__main__":  # pragma: no cover
    import sys

    from .duopoly import EQUILIBRIUM_GRID_PATH

    grid = write_equilibrium_grid(
        str(EQUILIBRIUM_GRID_PATH), fresh="fresh" in sys.argv[1:]
    )
    print(format_spread_table(grid))
