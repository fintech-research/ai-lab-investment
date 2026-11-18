"""Duopoly model: preemption game, training allocation, default risk.

Two layers live here.

Model of record (issues #178, #200). `DuopolyModel.solve()` returns the
equilibrium of the entry game in the exact piecewise primitives: demand is in
regime L until a switch at rate lambda and in regime H afterwards, each firm
may invest before or after the switch, the leader chooses its capacity and
training fraction at the demand at which it enters, and every installed
firm may stop operating (a shutdown boundary without debt, a default
boundary with it). The game is solved in `preemption_levered` on top of
`preemption_exact`; nothing in it is priced with the pure-power form or the
unconditional A_eff coefficient. The benchmark date of first investment is
X_L, the trigger of the leader in the equilibrium with assigned roles
(issue #200); the rent-equalization trigger X_P is reported as an upper
bound on it. `DuopolySolution` reports both together with the fixed-scale
leader variants and the nested approximation below. A solve takes a few
minutes, so the equilibria behind the paper are cached in
`duopoly_equilibria.json` (`load_equilibrium_grid`).

Nested approximation (the earlier draft's model). The `pure_power_*`
methods solve the reduced-form game: the follower's option and the
dilution of the leader's claim are valued with the H-regime exponent
beta_H and the unconditional coefficient A_eff, and the leader is held at
the monopoly-phase scale. They are kept so that every number of the
earlier draft stays reproducible and its distance from the model of record
can be reported. `valuation.py`, `robustness.py`, `calibration/` and most
paper figures still call them (issues #179 to #184).

Primitives shared by both layers:
- Regime-specific contest functions:
    L-regime: share over inference capacity [(1-phi)*K]^alpha
    H-regime: share over training compute [phi*K]^alpha
- Credit primitives (issue #177): recovery net of operating costs, a
  shutdown boundary for the unlevered firm, par debt at r_c or the fair
  coupon. The closed forms below (`default_boundary`, `equity_value`,
  `debt_value`) use the single-boundary reduction; the exact game uses the
  coupled regime-switching boundary.

An endogenous arrival rate extension is plumbed through but switched
off by default (xi = 0) and is NOT used in the paper:
    lambda_tilde = lam_0 + xi * [(phi_i*K_i)^eta + (phi_j*K_j)^eta]
"""

import json
import logging
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import numpy as np
from scipy import optimize

from .base_model import multistart_minimize
from .parameters import ModelParameters

_KPHI_STARTS: tuple[tuple[float, float], ...] = tuple(
    (log_K_init, phi_init)
    for log_K_init in (-6.0, -2.0, 0.0, 2.0)
    for phi_init in (0.15, 0.30, 0.50, 0.70)
)
"""Deterministic (log K, phi) multistart grid shared by both roles."""

RECOVERY_RULES: tuple[str, ...] = ("net", "net_until_switch", "gross")
"""Recovery rules accepted by DuopolyModel (see `recovery_value`)."""


EQUILIBRIUM_GRID_PATH = Path(__file__).with_name("duopoly_equilibria.json")
"""Cached equilibria of the model of record (see `load_equilibrium_grid`)."""


@dataclass(frozen=True)
class DuopolySolution:
    """Equilibrium of the duopoly model of record.

    The game is solved in the exact primitives with a leader that chooses
    (K_L, phi_L) at the demand at which it enters. Two demand levels are
    reported and must not be confused.

    ``X_L`` is the benchmark date of first investment (issue #200): the
    trigger of the firm that leads in the equilibrium with assigned roles,
    in which one firm invests at X_L and the other follows. It is the
    trigger a firm prefers when it knows that its rival will follow, and
    the no-deviation conditions of that profile are checked numerically
    (`equilibrium_verified`; see
    `preemption_levered.assigned_leader_equilibrium` for the statement and
    for what is not established). Every key of the record without a prefix
    is evaluated there.

    ``X_P`` is the rent-equalization trigger, the lowest demand at which
    leading is as good as following (first up-crossing of L*(X) - F(X) on
    a finite demand scan; no uniqueness claim). When X_L < X_P
    (`second_mover_advantage`) following is the better role between the
    two, X_P is an upper bound on the date of first investment, and the
    objects evaluated there carry the prefix ``rent_eq_``.

    Attributes:
        record: Flat record of `preemption_levered.equilibrium_record`. Its
            keys are also readable as attributes. At X_L: ``X_L``,
            ``K_L``, ``phi_L``, ``X_F`` and ``K_F`` (the follower's
            post-switch trigger and capacity against that leader),
            ``X_F_pre_switch`` (inf when the follower never enters before
            the switch), ``leader_value``, ``follower_value``,
            ``waiting_value``, ``lead_over_wait``,
            ``follower_over_leader``, the leader's credit objects at entry
            (``X_D_leader``, ``distance_to_default``, ``coupon_rate``,
            ``spread``, ``debt_value``, ``debt_proceeds``, ``recovery``),
            the follower's boundary at its entry, the first-passage
            statistics from X_L, and the no-deviation checks
            (``equilibrium``, ``leader_best_other_trigger``,
            ``lcp_trigger``, ``follower_margin``, ...). At X_P: ``X_P``
            and the same objects under ``rent_eq_`` (``rent_eq_K_L``,
            ``rent_eq_spread``, ...). ``phi_star`` is the single firm's
            training fraction.
        single_firm: The monopoly case: ``invests_before_switch`` (scale
            chosen whenever the firm invests) and the precommitted-scale
            policy ``X_star``, ``K_star``.
        fixed_scale: Rent equalization with the leader's policy held fixed,
            keyed ``"pure_power"`` (the pure-power (K, phi*), the earlier
            draft's convention) and ``"monopoly"`` (the precommitted-scale
            single-firm optimum).
        pure_power: Equilibrium of the nested approximation, a
            rent-equalization equilibrium.
    """

    record: dict[str, Any]
    single_firm: dict[str, Any] = field(default_factory=dict)
    fixed_scale: dict[str, dict[str, float]] = field(default_factory=dict)
    pure_power: dict[str, float] = field(default_factory=dict)

    def __getattr__(self, name: str) -> Any:
        record = object.__getattribute__(self, "record")
        if name in record:
            return record[name]
        raise AttributeError(name)

    @property
    def exists(self) -> bool:
        """True when a finite pre-switch rent-equalization trigger was found."""
        return bool(self.record["exists"])

    @property
    def equilibrium_verified(self) -> bool:
        """True when every no-deviation check of the X_L profile holds.

        The checks are numerical and cover the demand scan stored in the
        record (``entry_scan_low`` to ``entry_scan_high``, in units of X_P).
        """
        return bool(self.record.get("equilibrium", 0.0))

    @property
    def second_mover_advantage(self) -> bool:
        """True when the first investment X_L lies below X_P."""
        return bool(self.record["X_L"] < self.record["X_P"] * (1.0 - 1e-3))

    @property
    def allocation_gap(self) -> float:
        """phi_L / phi* - 1 at X_L: the leader's distance from role invariance."""
        return self.record["phi_L"] / self.record["phi_star"] - 1.0

    @property
    def scale_ratio(self) -> float:
        """K_F / K_L for a leader that enters at X_L."""
        return self.record["K_F"] / self.record["K_L"]

    @property
    def trigger_ratio(self) -> float:
        """X_F / X_L, the follower's post-switch trigger over the leader's."""
        return self.record["X_F"] / self.record["X_L"]

    @property
    def entry_ratio(self) -> float:
        """X_L over the precommitted-scale single-firm trigger (nan if unknown)."""
        if "X_star" not in self.single_firm:
            return float("nan")
        return self.record["X_L"] / self.single_firm["X_star"]

    @property
    def rent_equalization_ratio(self) -> float:
        """X_P over the precommitted-scale single-firm trigger (nan if unknown)."""
        if "X_star" not in self.single_firm:
            return float("nan")
        return self.record["X_P"] / self.single_firm["X_star"]

    def pure_power_error(self) -> dict[str, float]:
        """Relative error of the nested approximation, at rent equalization.

        The nested game is a rent-equalization equilibrium, so it is
        compared with the objects of the exact game at X_P.
        """
        pairs = {
            "X_P": ("X_P", "X_leader"),
            "K_L": ("rent_eq_K_L", "K_leader"),
            "X_F": ("rent_eq_X_F", "X_follower"),
            "K_F": ("rent_eq_K_F", "K_follower"),
        }
        return {
            key: self.pure_power[other] / self.record[own] - 1.0
            for key, (own, other) in pairs.items()
            if other in self.pure_power
        }


def load_equilibrium_grid() -> list[dict[str, Any]]:
    """Cached equilibria of the model of record at the baseline calibration.

    One record per (lambda, post-switch scale, leverage, debt convention),
    written by ``uv run python -m ai_lab_investment.models.preemption_levered``
    and checked against the solver in `tests/test_duopoly_exact.py`. The
    paper's duopoly numbers and `fig-competition-effect` read this file.
    """
    from .preemption_levered import decode_record

    with EQUILIBRIUM_GRID_PATH.open() as handle:
        return [decode_record(record) for record in json.load(handle)]


def cached_equilibrium(
    lam: float = 0.10,
    scale: str = "envelope",
    leverage: float = 0.0,
    debt: str = "par",
) -> dict[str, Any]:
    """One record of `load_equilibrium_grid`.

    Raises:
        KeyError: If the cell is not in the cache.
    """
    for record in load_equilibrium_grid():
        if (
            abs(record["lam"] - lam) < 1e-12
            and record["scale"] == scale
            and abs(record["leverage"] - leverage) < 1e-12
            and (record["debt"] == debt or leverage == 0.0)
        ):
            return record
    msg = f"No cached equilibrium for lam={lam}, {scale}, leverage={leverage}, {debt}"
    raise KeyError(msg)


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
        contest: str = "tullock",
        recovery_rule: str = "net",
    ):
        """Initialize the duopoly model.

        Args:
            params: Base model parameters (includes xi, lam_0, eta).
            leverage: Debt-to-investment-cost ratio D/I(K) for both firms
                (exogenous). 0 = all equity.
            coupon_rate: Coupon rate on debt as fraction of face value.
            bankruptcy_cost: Fraction of firm value lost in default (alpha_bc).
            contest: Revenue-sharing specification, "tullock" (default) or
                "fixed_pie" (same Tullock shares, no revenue expansion
                under asymmetry).
            recovery_rule: What creditors seize in default, before the
                bankruptcy cost and the caps (see `recovery_value`):
                "net" (default) is the inference business net of the
                operating cost of its capacity, floored at zero;
                "net_until_switch" nets that cost only until the regime
                switch; "gross" is the pre-#177 rule, inference revenue
                gross of operating costs, kept so the earlier draft's
                credit numbers stay reproducible.
        """
        if contest not in ("tullock", "fixed_pie"):
            msg = f"Unknown contest specification: {contest!r}"
            raise ValueError(msg)
        if recovery_rule not in RECOVERY_RULES:
            msg = f"Unknown recovery rule: {recovery_rule!r}"
            raise ValueError(msg)
        if not 0.0 <= leverage <= 1.0:
            msg = f"Leverage must be in [0, 1], got {leverage}"
            raise ValueError(msg)
        if coupon_rate <= 0.0:
            msg = f"Coupon rate must be positive, got {coupon_rate}"
            raise ValueError(msg)
        if not 0.0 <= bankruptcy_cost <= 1.0:
            msg = f"Bankruptcy cost must be in [0, 1], got {bankruptcy_cost}"
            raise ValueError(msg)
        self.params = params
        self.leverage = leverage
        self.coupon_rate = coupon_rate
        self.bankruptcy_cost = bankruptcy_cost
        self.contest = contest
        self.recovery_rule = recovery_rule
        self._cache: dict = {}
        #: Multistart convergence diagnostics, keyed by sub-problem.
        self.solver_diagnostics: dict[str, dict] = {}

    # ------------------------------------------------------------------
    # Model of record: the preemption game in the exact primitives
    # ------------------------------------------------------------------

    def exact_game(self, scale: str = "envelope", debt: str = "par"):
        """The exact preemption game at this model's leverage and coupon.

        Args:
            scale: ``"envelope"`` (a firm that has not invested when the
                switch arrives chooses its scale then; the model of record)
                or ``"precommitted"`` (its post-switch scale is fixed at the
                capacity optimal at its post-switch trigger).
            debt: ``"par"`` or ``"fair"``.

        Raises:
            ValueError: For specifications the exact game does not cover
                (endogenous arrival rate, the arithmetic-mean contest, a
                recovery rule other than "net").
        """
        from .preemption_levered import LeveredPreemptionGame

        if self.params.xi != 0.0:
            msg = "The exact game requires an exogenous arrival rate (xi = 0)"
            raise ValueError(msg)
        if self.contest != "tullock" or self.recovery_rule != "net":
            msg = (
                "The exact game is solved for the Tullock contest and the "
                '"net" recovery rule only'
            )
            raise ValueError(msg)
        return LeveredPreemptionGame(
            self.params,
            scale,
            self.leverage,
            self.coupon_rate,
            self.bankruptcy_cost,
            debt,
        )

    def solve(
        self,
        scale: str = "envelope",
        debt: str = "par",
        variants: bool = True,
    ) -> DuopolySolution:
        """Equilibrium of the model of record.

        The leader chooses capacity and training fraction at the demand at
        which it enters; the follower best-responds, before or after the
        switch. The solution reports the first investment X_L of the
        equilibrium with assigned roles and the rent-equalization trigger
        X_P above it (see `DuopolySolution`). With ``variants`` it also
        carries the fixed-scale leader variants, the single-firm benchmark
        and the equilibrium of the nested approximation
        (`pure_power_preemption_equilibrium`). Takes three to four minutes;
        `cached_equilibrium` returns the stored baseline records.
        """
        from .base_model import SingleFirmModel
        from .preemption_levered import equilibrium_record

        game = self.exact_game(scale, debt)
        record = equilibrium_record(
            self.params,
            scale,
            self.leverage,
            debt,
            self.coupon_rate,
            self.bankruptcy_cost,
        )
        if not variants:
            return DuopolySolution(record)
        single = SingleFirmModel(self.params).solve()
        single_firm = {
            "invests_before_switch": single.invests_before_switch,
            "waiting_margin": single.waiting_margin,
            "X_star": single.precommitted.X_star,
            "K_star": single.precommitted.K,
        }
        fixed_scale = {
            "pure_power": game.rent_equalization(*game.paper_policy()),
            "monopoly": game.rent_equalization(*game.exact_monopoly_policy()),
        }
        try:
            pure_power = {
                key: float(value)
                for key, value in self.pure_power_preemption_equilibrium().items()
                if isinstance(value, float | np.floating)
            }
        except RuntimeError:
            pure_power = {}
        return DuopolySolution(record, single_firm, fixed_scale, pure_power)

    def hitting_statistics(self, X_from: float, X_to: float) -> dict[str, float]:
        """First-passage statistics of demand from X_from to X_to.

        See `preemption_levered.hitting_statistics`: the probability of
        reaching X_to before the switch, if the switch never arrived, and
        after it, and the expected post-switch passage time.
        """
        from .preemption_levered import hitting_statistics

        return hitting_statistics(self.params, X_from, X_to)

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

    @staticmethod
    def _check_phi(*phis: float) -> None:
        """Reject training fractions outside [0, 1].

        phi is a share of installed capacity, so phi > 1 makes the
        inference capacity (1-phi)K negative and phi < 0 does the same to
        the training capacity. Raising a negative base to the fractional
        power alpha silently produces a nan rather than failing, so the
        public entry points check the domain instead.
        """
        for phi in phis:
            if not 0.0 <= phi <= 1.0:
                msg = f"Training fraction phi must be in [0, 1], got {phi}"
                raise ValueError(msg)

    def contest_share_L(
        self, phi_i: float, K_i: float, phi_j: float, K_j: float
    ) -> float:
        """L-regime contest share: inference-based competition.

        share_i^L = [(1-phi_i)*K_i]^alpha
                    / {[(1-phi_i)*K_i]^alpha + [(1-phi_j)*K_j]^alpha}
        """
        self._check_phi(phi_i, phi_j)
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
        self._check_phi(phi_i, phi_j)
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

    def _effective_revenue_coeff_fixed_pie(
        self,
        phi_i: float,
        K_i: float,
        phi_j: float,
        K_j: float,
    ) -> float:
        """A_eff under the arithmetic-mean industry-revenue benchmark.

        Called "fixed_pie" in the contest argument for backward
        compatibility; the paper (Internet Appendix E) calls it the
        arithmetic-mean industry-revenue benchmark, because the pie still
        moves with both capacities and is fixed only against
        share-stealing.

        The industry pie is the arithmetic mean of the firms' standalone
        revenues, X * (y_i + y_j) / 2 with y_i the regime-relevant
        capacity measure raised to alpha, and shares are Tullock
        (s_i = y_i / (y_i + y_j)). Firm i's revenue is therefore
        s_i * (y_i + y_j) / 2 = y_i / 2: half its standalone revenue.
        Under symmetry this equals the standard Tullock payoff; under
        asymmetry the quadratic-mean revenue expansion is removed (the
        total pie is invariant to share-stealing), and no firm can
        free-ride on the rival's capacity.
        """
        p = self.params
        lam_tilde = self.endogenous_lambda(phi_i, K_i, phi_j, K_j)

        inf_i = (1.0 - phi_i) * K_i
        tr_i = phi_i * K_i

        denom_L = p.r - p.mu_L + lam_tilde
        if denom_L <= 0:
            return 0.0

        a_eff = 0.5 * inf_i**p.alpha / denom_L

        if tr_i > 0 and lam_tilde > 0:
            a_eff += lam_tilde / denom_L * 0.5 * tr_i**p.alpha * p.A_H

        return a_eff

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
        if self.contest == "fixed_pie" and not monopolist:
            return self._effective_revenue_coeff_fixed_pie(phi_i, K_i, phi_j, K_j)

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
        self._check_phi(phi_i, phi_j)
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
        self._check_phi(phi_i, phi_j)
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
        self._check_phi(phi_i)
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
        self._check_phi(phi_i)
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
        """Annual coupon under the par-debt convention.

        Debt face value = leverage * I(K), coupon = coupon_rate * face
        value. The lender advances the face value, so with coupon_rate
        below r the debt is worth less than the proceeds (a financing
        subsidy). `fair_coupon` solves instead for the coupon at which
        the debt is worth its proceeds at issuance.
        """
        lev = leverage if leverage is not None else self.leverage
        if lev <= 0:
            return 0.0
        face_value = lev * self.investment_cost(K)
        return self.coupon_rate * face_value

    def _resolve_coupon(self, K: float, lev: float, coupon: float | None) -> float:
        """Coupon in force: an explicit one, else the par-debt coupon."""
        if coupon is None:
            return self.coupon_payment(K, lev)
        if coupon < 0:
            msg = f"Coupon must be non-negative, got {coupon}"
            raise ValueError(msg)
        return float(coupon)

    def default_boundary(
        self,
        phi_i: float,
        K_i: float,
        phi_j: float,
        K_j: float,
        leverage: float | None = None,
        coupon: float | None = None,
    ) -> float:
        """Endogenous default boundary X_D (Leland 1994).

        Default is driven by L-regime total revenue (inference + H-continuation).
        Higher phi reduces inference revenue but increases H-regime continuation
        (the "faith-based survival" mechanism).

        X_D = [beta_neg / (beta_neg - 1)] * [c_D/r + delta*K/r] / A_eff

        Derived from smooth-pasting on the ongoing equity value (excluding
        the sunk equity contribution, which is irrelevant for the default
        decision).

        The unlevered firm is the c_D = 0 case of the same formula: it
        stops operating at the shutdown boundary
        [beta_neg / (beta_neg - 1)] * (delta*K/r) / A_eff, so X_D is
        continuous as leverage goes to zero. With debt the object is a
        default boundary, without debt a shutdown (abandonment) boundary.

        Args:
            coupon: Explicit coupon flow; defaults to the par-debt coupon
                `coupon_payment(K_i, leverage)`.
        """
        self._check_phi(phi_i, phi_j)
        lev = leverage if leverage is not None else self.leverage

        p = self.params
        c_D = self._resolve_coupon(K_i, lev, coupon)
        fixed_claims = c_D / p.r + p.delta * K_i / p.r
        if fixed_claims <= 0:
            # Neither a coupon nor an operating cost: nothing to walk
            # away from.
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

        X_D = (beta_neg / (beta_neg - 1.0)) * fixed_claims / revenue_coeff
        return max(X_D, 0.0)

    def shutdown_boundary(
        self,
        phi_i: float,
        K_i: float,
        phi_j: float = 0.0,
        K_j: float = 0.0,
    ) -> float:
        """Shutdown boundary of the unlevered firm: X_D at a zero coupon."""
        return self.default_boundary(phi_i, K_i, phi_j, K_j, 0.0, coupon=0.0)

    def default_boundary_coupled(
        self,
        phi_i: float,
        K_i: float,
        phi_j: float,
        K_j: float,
        leverage: float | None = None,
    ) -> float:
        """L-regime default boundary from the coupled regime-switching system.

        Verification counterpart to default_boundary(). The H-regime equity
        has the closed Leland form E_H(X) = A' X - N + D_H X^{beta_H^-} with
        its own boundary X_D^H; the L-regime equity ODE is forced by
        lambda * E_H, giving particular terms A_eff X - N + C_2 X^{beta_H^-}
        plus the homogeneous A_neg X^{beta_L^-}. Value matching and smooth
        pasting at X_D pin (A_neg, X_D) jointly.

        Scalar reduction: the homogeneous coefficient enters both boundary
        conditions linearly, so the combination beta_L^- * E(X_D)
        - X_D * E'(X_D) = 0 eliminates A_neg exactly, leaving one equation

            Phi(X) = A_eff (beta_L^- - 1) X - beta_L^- N
                     + C_2 (beta_L^- - beta_H^-) X^{beta_H^-} = 0,

        solved by Brent's method. The single-boundary formula in
        default_boundary() is the C_2 = 0 root; since C_2 < 0 at
        calibration values, the coupled boundary lies below it (about 3%
        at baseline; see coupled_boundary_bias_linear for the closed-form
        first-order bias).
        """
        self._check_phi(phi_i, phi_j)
        lev = leverage if leverage is not None else self.leverage
        if self.coupon_payment(K_i, lev) + self.params.delta * K_i <= 0:
            return 0.0

        terms = self._coupled_boundary_terms(phi_i, K_i, phi_j, K_j, lev)
        if terms is None:
            # No H-regime revenue: the coupled system degenerates to the
            # single-boundary case.
            return self.default_boundary(phi_i, K_i, phi_j, K_j, lev)
        a_eff, N, C_2, beta_L_neg, beta_H_neg = terms
        if a_eff <= 0:
            return np.inf

        def gap(X: float) -> float:
            return (
                a_eff * (beta_L_neg - 1.0) * X
                - beta_L_neg * N
                + C_2 * (beta_L_neg - beta_H_neg) * X**beta_H_neg
            )

        X_D0 = self.default_boundary(phi_i, K_i, phi_j, K_j, lev)
        # Phi is hump-shaped (-> -inf at both 0 and infinity) with at most
        # two roots. The economically relevant boundary is the right root,
        # which converges to the single-boundary X_D0 as C_2 -> 0; the
        # left root is an artifact of the X^{beta_H^-} term near zero.
        # Bracket from the hump maximum (closed form from Phi'(X_m) = 0).
        hump_coef = beta_H_neg * C_2 * (beta_L_neg - beta_H_neg)
        if hump_coef == 0.0:
            return X_D0
        X_m = (-a_eff * (beta_L_neg - 1.0) / hump_coef) ** (1.0 / (beta_H_neg - 1.0))
        hi = max(100.0 * X_D0, 10.0 * X_m)
        if gap(X_m) <= 0 or gap(hi) >= 0:
            logging.warning(
                "Coupled default boundary bracket failed; "
                "returning single-boundary formula"
            )
            return X_D0
        return float(optimize.brentq(gap, X_m, hi, xtol=1e-14))

    def _coupled_boundary_terms(
        self,
        phi_i: float,
        K_i: float,
        phi_j: float,
        K_j: float,
        lev: float,
    ) -> tuple[float, float, float, float, float] | None:
        """Common ingredients of the coupled default-boundary system.

        Returns (a_eff, N, C_2, beta_L_neg, beta_H_neg), or None when the
        firm has no H-regime revenue (phi_i * K_i <= 0).
        """
        p = self.params
        c_D = self.coupon_payment(K_i, lev)
        is_monopolist = K_j <= 0
        s_H = 1.0 if is_monopolist else self.contest_share_H(phi_i, K_i, phi_j, K_j)
        a_eff = self._effective_revenue_coeff(
            phi_i, K_i, phi_j, K_j, monopolist=is_monopolist
        )

        N = (c_D + p.delta * K_i) / p.r
        tr_cap = phi_i * K_i
        if tr_cap <= 0:
            return None
        A_prime = p.A_H * tr_cap**p.alpha * s_H

        # H-regime Leland boundary and default-option coefficient
        beta_H_neg = self._negative_root("H", 0.0)
        X_D_H = beta_H_neg / (beta_H_neg - 1.0) * N / A_prime
        D_H = (N - A_prime * X_D_H) * X_D_H ** (-beta_H_neg)

        lam_tilde = self.endogenous_lambda(phi_i, K_i, phi_j, K_j)
        beta_L_neg = self._negative_root("L", lam_tilde)
        Q_L = (
            0.5 * p.sigma**2 * beta_H_neg * (beta_H_neg - 1.0)
            + p.mu_L * beta_H_neg
            - (p.r + lam_tilde)
        )
        C_2 = -lam_tilde * D_H / Q_L
        return a_eff, N, C_2, beta_L_neg, beta_H_neg

    def coupled_boundary_bias_linear(
        self,
        phi_i: float,
        K_i: float,
        phi_j: float,
        K_j: float,
        leverage: float | None = None,
    ) -> float:
        """Closed-form first-order relative bias of the single boundary.

        Expanding the scalar coupled-boundary equation around the
        single-boundary root X_D^0 in the small coefficient C_2 gives

            (X_D^0 - X_D) / X_D^0
            ~ kappa = C_2 (beta_L^- - beta_H^-) (X_D^0)^{beta_H^- - 1}
                      / [A_eff (beta_L^- - 1)],

        the analytical counterpart of the ~3% overstatement reported in
        the paper. Returns kappa (positive when the single-boundary
        formula overstates the coupled boundary). Returns 0.0 when the
        firm has no H-regime revenue or no fixed claim to walk away from.
        """
        self._check_phi(phi_i, phi_j)
        lev = leverage if leverage is not None else self.leverage
        if self.coupon_payment(K_i, lev) + self.params.delta * K_i <= 0:
            return 0.0
        terms = self._coupled_boundary_terms(phi_i, K_i, phi_j, K_j, lev)
        if terms is None:
            return 0.0
        a_eff, _N, C_2, beta_L_neg, beta_H_neg = terms
        if a_eff <= 0:
            return 0.0
        X_D0 = self.default_boundary(phi_i, K_i, phi_j, K_j, lev)
        return float(
            C_2
            * (beta_L_neg - beta_H_neg)
            * X_D0 ** (beta_H_neg - 1.0)
            / (a_eff * (beta_L_neg - 1.0))
        )

    def faith_threshold(self) -> float:
        """A_eff-channel threshold phi_underbar (paper eq-phi-underbar).

        In the symmetric-shares case, dA_eff/dlambda > 0 iff phi exceeds
        phi_underbar = R / (1 + R), R = ((r - mu_H)/(r - mu_L))^(1/alpha).
        Independent of lambda.
        """
        p = self.params
        R = ((p.r - p.mu_H) / (p.r - p.mu_L)) ** (1.0 / p.alpha)
        return R / (1.0 + R)

    def faith_threshold_exact(self, lam: float | None = None) -> float:
        """Exact faith-based survival threshold phi_tilde (both channels).

        The full derivative of the default boundary decomposes as
        d ln X_D / d lambda = M'/M - A_eff'/A_eff (markup channel minus
        revenue channel). Since A_eff'/A_eff = [b(r - mu_L) - a] /
        [(a + lambda b) Delta] is linear in the L-flow a and the
        H-continuation b, the net condition d X_D / d lambda < 0 solves in
        closed form for the symmetric-shares case:

            phi > phi_tilde = R~ / (1 + R~),
            R~ = [(r - mu_H)(1 + m Delta)
                  / ((r - mu_L) - m lambda Delta)]^(1/alpha),
            m  = M'/M = 1 / [beta_s^- (beta_s^- - 1) D],
            D  = sqrt((mu_L - sigma^2/2)^2 + 2 sigma^2 (r + lambda)),
            Delta = r - mu_L + lambda.

        Nests phi_underbar as the m -> 0 (no markup channel) limit, and
        phi_tilde > phi_underbar whenever m > 0. Unlike phi_underbar,
        phi_tilde depends on lambda. Requires the regularity condition
        (r - mu_L) > m * lambda * Delta (always satisfied at calibration
        values); if violated, X_D is increasing in lambda for every phi
        and the threshold does not exist (returns 1.0).
        """
        p = self.params
        lam_eff = p.lam if lam is None else lam
        b_ = p.mu_L - 0.5 * p.sigma**2
        D = np.sqrt(b_**2 + 2.0 * p.sigma**2 * (p.r + lam_eff))
        beta_neg = (-b_ - D) / p.sigma**2
        m = 1.0 / (beta_neg * (beta_neg - 1.0) * D)
        delta_eff = p.r - p.mu_L + lam_eff
        denom = (p.r - p.mu_L) - m * lam_eff * delta_eff
        if denom <= 0:
            return 1.0
        R_tilde = ((p.r - p.mu_H) * (1.0 + m * delta_eff) / denom) ** (1.0 / p.alpha)
        return R_tilde / (1.0 + R_tilde)

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

    def _installed_value(
        self, X: float, phi_i: float, K_i: float, phi_j: float, K_j: float
    ) -> float:
        """L-regime installed value, monopoly when the rival has no capacity."""
        if K_j > 0:
            return self.installed_value_L(X, phi_i, K_i, phi_j, K_j)
        return self.monopolist_value_L(X, phi_i, K_i)

    def _going_concern(
        self,
        X: float,
        phi_i: float,
        K_i: float,
        phi_j: float,
        K_j: float,
        c_D: float,
    ) -> float:
        """Going-concern equity claim at coupon c_D, floored at zero.

        V(X) - c_D/r + [c_D/r - V(X_D)] (X/X_D)^beta_neg above X_D and
        zero at or below it. At c_D = 0 this is the unlevered asset value
        including the option to shut down.
        """
        p = self.params
        V_X = self._installed_value(X, phi_i, K_i, phi_j, K_j)
        X_D = self.default_boundary(phi_i, K_i, phi_j, K_j, 0.0, coupon=c_D)
        if X_D <= 0:
            # No fixed claim to walk away from: a plain perpetuity.
            return V_X - c_D / p.r
        if X <= X_D:
            return 0.0
        lam_tilde = self.endogenous_lambda(phi_i, K_i, phi_j, K_j)
        beta_neg = self._negative_root("L", lam_tilde)
        V_XD = self._installed_value(X_D, phi_i, K_i, phi_j, K_j)
        # Put-like value of walking away: V(X_D) - c_D/r + claim = 0.
        default_option = (c_D / p.r - V_XD) * (X / X_D) ** beta_neg
        return max(V_X - c_D / p.r + default_option, 0.0)

    def unlevered_asset_value(
        self,
        X: float,
        phi_i: float,
        K_i: float,
        phi_j: float = 0.0,
        K_j: float = 0.0,
    ) -> float:
        """Value of the installed assets to an all-equity owner.

        V(X) plus the option to stop operating at the shutdown boundary
        (the c_D = 0 case of the going-concern claim); zero at or below
        that boundary. This is Leland's (1994) unlevered asset value for
        a firm whose assets carry an operating cost.
        """
        self._check_phi(phi_i, phi_j)
        return self._going_concern(X, phi_i, K_i, phi_j, K_j, 0.0)

    def equity_value(
        self,
        X: float,
        phi_i: float,
        K_i: float,
        phi_j: float,
        K_j: float,
        leverage: float | None = None,
        coupon: float | None = None,
    ) -> float:
        """Entry NPV of the equity claim: going concern minus contribution.

        The model's single equity convention (paper, "Equity and debt
        values"): the going-concern claim is

            E_gc(X) = V(X) - coupon/r
                      + [coupon/r - V(X_D)] * (X/X_D)^beta_neg,

        which limited liability floors at zero -- E_gc(X_D) = 0 by
        smooth pasting, so the floor is a numerical guard that never
        binds above X_D. This method returns the object the investment
        decision is made on,

            E_gc(X) - (1 - leverage) * I(K),

        i.e. net of the equity holders' sunk contribution. That
        contribution is *not* refunded on default, so the returned value
        is negative below the default boundary (it equals
        -(1 - leverage) I(K) there) and at X = 0. This is exactly the
        L(0) < 0 endpoint the existence argument for the preemption
        trigger uses; clamping the net object at zero would contradict
        it.

        Without debt the same formula applies at a zero coupon: the
        going concern is the unlevered asset value, which includes the
        option to shut down at the shutdown boundary, and the entry NPV
        is that value minus I(K). Equity is therefore continuous as
        leverage goes to zero.

        Args:
            coupon: Explicit coupon flow; defaults to the par-debt coupon.
        """
        self._check_phi(phi_i, phi_j)
        lev = leverage if leverage is not None else self.leverage
        c_D = self._resolve_coupon(K_i, lev, coupon)
        equity_contribution = self.investment_cost(K_i) * (1.0 - lev)
        going_concern = self._going_concern(X, phi_i, K_i, phi_j, K_j, c_D)
        return going_concern - equity_contribution

    def recovery_value(
        self,
        phi_i: float,
        K_i: float,
        phi_j: float,
        K_j: float,
        leverage: float | None = None,
        coupon: float | None = None,
    ) -> float:
        """What creditors receive at the default boundary.

        Bankruptcy destroys the H-regime continuation value embedded in
        A_eff (the speculative post-AGI payoff requires the going concern
        -- its researchers, models, and training program -- and does not
        survive liquidation), so creditors seize the inference business
        only. Under the default rule ("net") recovery is

            (1 - alpha_bc) * min{ max(Lambda_net(X_D), 0), U(X_D) },

        capped at the default-free value of the claim c_D/r, where
        Lambda_net is `liquidation_value`, the inference business net of
        the operating cost of its capacity, and U is
        `unlevered_asset_value`. The cap at U keeps recovery inside the
        value of the assets the creditors take over: inference capacity
        alone can be worth more than the whole firm when its revenue
        share exceeds its capacity share, and the firm of the model
        cannot shed training capacity either. "net_until_switch" differs
        only in `liquidation_value`. "gross" is the pre-#177 rule,
        (1 - alpha_bc) times inference revenue gross of operating costs,
        capped at c_D/r only.
        """
        self._check_phi(phi_i, phi_j)
        lev = leverage if leverage is not None else self.leverage
        p = self.params
        c_D = self._resolve_coupon(K_i, lev, coupon)
        if c_D <= 0:
            return 0.0
        X_D = self.default_boundary(phi_i, K_i, phi_j, K_j, lev, coupon=c_D)
        if not np.isfinite(X_D) or X_D <= 0:
            return 0.0
        liq = max(self.liquidation_value(X_D, phi_i, K_i, phi_j, K_j), 0.0)
        if self.recovery_rule != "gross":
            liq = min(liq, self.unlevered_asset_value(X_D, phi_i, K_i, phi_j, K_j))
        return min((1.0 - self.bankruptcy_cost) * liq, c_D / p.r)

    def recovery_rate(
        self,
        phi_i: float,
        K_i: float,
        phi_j: float,
        K_j: float,
        leverage: float | None = None,
        coupon: float | None = None,
    ) -> float:
        """Recovery as a fraction of the default-free claim c_D/r.

        Returns nan when there is no debt.
        """
        lev = leverage if leverage is not None else self.leverage
        c_D = self._resolve_coupon(K_i, lev, coupon)
        if c_D <= 0:
            return float("nan")
        recovery = self.recovery_value(phi_i, K_i, phi_j, K_j, lev, coupon=c_D)
        return recovery / (c_D / self.params.r)

    def debt_value(
        self,
        X: float,
        phi_i: float,
        K_i: float,
        phi_j: float,
        K_j: float,
        leverage: float | None = None,
        coupon: float | None = None,
    ) -> float:
        """Debt value accounting for default risk.

        D(X) = coupon/r - [coupon/r - recovery] * (X/X_D)^beta_neg   (X > X_D)
        D(X) = recovery                                               (X <= X_D)

        Recovery is `recovery_value`: (1 - alpha_bc) times the
        inference-only liquidation value net of operating costs, never
        more than the unlevered asset value at X_D, and capped at the
        riskless value of the coupon claim c_D/r (absolute priority:
        creditors cannot recover more than their claim is worth
        default-free).

        Args:
            coupon: Explicit coupon flow; defaults to the par-debt coupon.
        """
        self._check_phi(phi_i, phi_j)
        lev = leverage if leverage is not None else self.leverage
        p = self.params
        c_D = self._resolve_coupon(K_i, lev, coupon)
        if c_D <= 0:
            return 0.0

        X_D = self.default_boundary(phi_i, K_i, phi_j, K_j, lev, coupon=c_D)

        if X_D <= 0:
            return c_D / p.r

        lam_tilde = self.endogenous_lambda(phi_i, K_i, phi_j, K_j)
        beta_neg = self._negative_root("L", lam_tilde)

        recovery = self.recovery_value(phi_i, K_i, phi_j, K_j, lev, coupon=c_D)
        if X <= X_D:
            # Default has occurred: creditors hold the realized recovery
            # (the continuation formula below is not valid past the
            # boundary and would extrapolate to zero).
            return recovery
        default_loss = c_D / p.r - recovery
        debt = c_D / p.r - default_loss * (X / X_D) ** beta_neg
        return max(debt, 0.0)

    def liquidation_value(
        self,
        X: float,
        phi_i: float,
        K_i: float,
        phi_j: float,
        K_j: float,
    ) -> float:
        """Liquidation value of firm i's productive assets at demand X.

        Only the inference business survives liquidation: the buyer
        acquires the capacity serving current demand and earns the
        L-regime revenue stream until the regime switch, capitalized at
        the effective rate r - mu_L + lambda. The H-regime continuation
        value (the faith-based component of A_eff) is destroyed in
        bankruptcy.

        The value is net of the operating cost of the inference capacity
        (1 - phi) K, as an unlevered asset value is in Leland (1994),
        whose asset value V is the value of the firm's activities. Under
        "net" that cost is the same perpetual commitment the firm itself
        carries, delta (1 - phi) K / r, so the firm's installed value is
        exactly this object plus the training business. Under
        "net_until_switch" the buyer stops paying at the switch, when
        the inference stream ends: delta (1 - phi) K / (r + lambda).
        Under "gross" (the pre-#177 rule) no operating cost is netted.
        The value can be negative; `recovery_value` applies the floor.
        """
        self._check_phi(phi_i, phi_j)
        p = self.params
        lam_tilde = self.endogenous_lambda(phi_i, K_i, phi_j, K_j)
        denom_L = p.r - p.mu_L + lam_tilde
        if denom_L <= 0:
            return 0.0
        inf_cap = (1.0 - phi_i) * K_i
        s_L = 1.0 if K_j <= 0 else self.contest_share_L(phi_i, K_i, phi_j, K_j)
        revenue = inf_cap**p.alpha * s_L * X / denom_L
        if self.recovery_rule == "gross":
            return revenue
        horizon_rate = p.r if self.recovery_rule == "net" else p.r + lam_tilde
        return revenue - p.delta * inf_cap / horizon_rate

    def firm_value(
        self,
        X: float,
        phi_i: float,
        K_i: float,
        phi_j: float,
        K_j: float,
        leverage: float | None = None,
        coupon: float | None = None,
    ) -> float:
        """Total firm value = equity + debt."""
        return self.equity_value(
            X, phi_i, K_i, phi_j, K_j, leverage, coupon
        ) + self.debt_value(X, phi_i, K_i, phi_j, K_j, leverage, coupon)

    def fair_coupon(
        self,
        X: float,
        phi_i: float,
        K_i: float,
        phi_j: float = 0.0,
        K_j: float = 0.0,
        leverage: float | None = None,
    ) -> float:
        """Coupon at which debt issued at demand X is worth its proceeds.

        Solves D(X; c_D) = leverage * I(K) for c_D, with the default
        boundary and the recovery re-determined at each candidate coupon.
        This is the fairly priced counterpart of the par-debt convention
        of `coupon_payment`, in which the lender advances leverage * I(K)
        against a coupon of coupon_rate * leverage * I(K), worth less
        than the proceeds whenever coupon_rate < r.

        Debt value is not monotone in the coupon (a higher coupon raises
        the default boundary), so the smallest root is returned, found by
        scanning from the riskless coupon r * leverage * I(K) to the
        coupon at which the firm would default at issuance.

        Raises:
            ValueError: If the proceeds exceed the debt capacity at X,
                or the firm has no revenue.
        """
        self._check_phi(phi_i, phi_j)
        lev = leverage if leverage is not None else self.leverage
        if lev <= 0:
            return 0.0
        p = self.params
        proceeds = lev * self.investment_cost(K_i)

        def gap(c_D: float) -> float:
            return (
                self.debt_value(X, phi_i, K_i, phi_j, K_j, lev, coupon=c_D) - proceeds
            )

        riskless = p.r * proceeds
        if gap(riskless) >= 0:
            # Default-free at this coupon (possible under "gross").
            return riskless

        a_eff = self._effective_revenue_coeff(
            phi_i, K_i, phi_j, K_j, monopolist=K_j <= 0
        )
        if a_eff <= 0:
            msg = "No fair coupon: the firm has no revenue"
            raise ValueError(msg)
        beta_neg = self._negative_root(
            "L", self.endogenous_lambda(phi_i, K_i, phi_j, K_j)
        )
        # Coupon at which the default boundary reaches X.
        ceiling = p.r * ((beta_neg - 1.0) / beta_neg * a_eff * X) - p.delta * K_i
        if ceiling > riskless:
            grid = np.geomspace(riskless, ceiling, 400)
            gaps = np.array([gap(c) for c in grid])
            crossing = np.flatnonzero(gaps >= 0)
            if crossing.size:
                k = int(crossing[0])
                return float(
                    optimize.brentq(gap, grid[k - 1], grid[k], xtol=1e-16, rtol=1e-12)
                )
        msg = (
            f"No fair coupon: proceeds {proceeds:.6g} exceed the debt "
            f"capacity at X = {X:.6g} (leverage {lev:.3f})"
        )
        raise ValueError(msg)

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

    def _follower_objective(
        self,
        params_vec: np.ndarray,
        K_L: float,
        phi_L: float,
    ) -> float:
        """Negative of follower's option value factor for (K, phi) optimization.

        params_vec = [log_K, phi]; leverage is fixed at the model's
        exogenous self.leverage. Leverage must not be a free coordinate:
        debt is issued at face value with coupon rate c_d < r, so the
        cost term b is strictly decreasing in leverage and an optimizer
        would always run to the upper bound.
        Maximizes h(K, phi) = a_eff^beta_H / cost^(beta_H-1).
        """
        log_K, phi_F = params_vec

        # Bound checks first: exp(log_K) overflows outside the bounds
        # (log_K bounds match base_model's (-15, 15)).
        if log_K < -15 or log_K > 15:
            return 1e20
        if phi_F <= 0.01 or phi_F >= 0.99:
            return 1e20

        K_F = np.exp(log_K)
        p = self.params
        beta = p.beta_H
        lev_F = self.leverage

        a_eff = self._effective_revenue_coeff(phi_F, K_F, phi_L, K_L)

        c_D = self.coupon_payment(K_F, lev_F)
        equity_cost = (1.0 - lev_F) * self.investment_cost(K_F)
        b = p.delta * K_F / p.r + equity_cost + c_D / p.r

        if a_eff <= 0 or b <= 0:
            return 1e20
        return -(beta * np.log(a_eff) - (beta - 1.0) * np.log(b))

    def pure_power_follower(
        self,
        K_L: float,
        phi_L: float,
        regime: str = "H",
    ) -> tuple[float, float, float, float]:
        """Follower's problem of the nested pure-power game, over (K, phi).

        Given leader's (K_L, phi_L), find follower's optimal
        trigger, capacity, and training fraction. Leverage is the
        model's exogenous self.leverage.

        Args:
            K_L: Leader's installed capacity.
            phi_L: Leader's training fraction.
            regime: Regime label (for cache key compatibility).

        Returns:
            (X_F*, K_F*, phi_F*, lev_F): Follower's optimal choices;
            lev_F equals the exogenous leverage.
        """
        cache_key = ("follower", K_L, phi_L, regime)
        if cache_key in self._cache:
            return self._cache[cache_key]

        lev_F = self.leverage
        best_params, best_val, diagnostics = multistart_minimize(
            self._follower_objective, _KPHI_STARTS, args=(K_L, phi_L)
        )
        self.solver_diagnostics["follower"] = diagnostics

        if best_params is None or best_val >= 1e19:
            msg = f"Follower optimization failed for K_L={K_L:.4f}, phi_L={phi_L:.3f}"
            raise RuntimeError(msg)
        if diagnostics["n_converged"] == 0:
            msg = (
                f"Follower optimization did not converge from any of the "
                f"{diagnostics['n_starts']} starting points "
                f"(K_L={K_L:.4f}, phi_L={phi_L:.3f})"
            )
            raise RuntimeError(msg)

        K_F = np.exp(best_params[0])
        phi_F = np.clip(best_params[1], 0.01, 0.99)
        X_F = self._follower_trigger(K_F, phi_F, K_L, phi_L, lev_F)

        self._cache[cache_key] = (X_F, K_F, phi_F, lev_F)
        return X_F, K_F, phi_F, lev_F

    def pure_power_follower_scalar(
        self,
        K_L: float,
        phi_L: float,
    ) -> tuple[float, float, float, float]:
        """Follower solution via the separable scalar reduction.

        Verification counterpart to pure_power_follower(). At a common training
        fraction phi_F = phi_L = phi, the Tullock contest denominators
        factor: [(1-phi)K_F]^alpha + [(1-phi)K_L]^alpha
        = (1-phi)^alpha (K_F^alpha + K_L^alpha), and likewise for the
        H-regime, so

            A_eff,F = g(phi) * K_F^{2 alpha} / (K_F^alpha + K_L^alpha),

        the same g(phi)-times-capacity-term separability as Proposition 1.
        The allocation FOC is then exactly the single-firm condition
        (phi_F = phi*, role invariance), and the capacity FOC reduces to a
        single equation in K_F with effective revenue elasticity
        alpha * (2 - s_F(K_F)), where s_F = K_F^alpha/(K_F^alpha+K_L^alpha):

            alpha beta_H (2 - s_F(K)) b(K) = (beta_H - 1) K b'(K).

        The bracket alpha*beta_H*(2 - s_F) - (beta_H - 1) K b'/b is
        strictly decreasing in K (s_F increasing, K b'/b increasing from 1
        to gamma), so the interior optimum is unique whenever
        (beta_H - 1)/(2 alpha beta_H) < 1 (small-K interiority; weaker
        than (A2)'s upper bound because the small-K elasticity is
        2 alpha) and (beta_H - 1)/(alpha beta_H) > 1/gamma (large-K
        interiority, the same lower bound as (A2)).

        Only valid for the Tullock contest with phi_F = phi_L.

        Returns:
            (X_F*, K_F*, phi_F*, lev_F) with phi_F* = phi_L.
        """
        if self.contest != "tullock":
            msg = "Scalar follower reduction requires the Tullock contest"
            raise RuntimeError(msg)

        p = self.params
        beta = p.beta_H
        lev_F = self.leverage

        # Interiority conditions for the follower's scalar problem
        small_k = (beta - 1.0) / (2.0 * p.alpha * beta)
        large_k = (beta - 1.0) / (p.alpha * beta)
        if not (small_k < 1.0 and large_k > 1.0 / p.gamma):
            msg = (
                f"No interior follower optimum: need "
                f"(beta_H-1)/(2 alpha beta_H) = {small_k:.3f} < 1 and "
                f"(beta_H-1)/(alpha beta_H) = {large_k:.3f} > "
                f"1/gamma = {1 / p.gamma:.3f}"
            )
            raise RuntimeError(msg)

        # Leverage-adjusted capital cost has the same K-powers as b(K)
        c_tilde = p.c * (1.0 - lev_F * (1.0 - self.coupon_rate / p.r))

        def foc_bracket(log_K: float) -> float:
            K = np.exp(log_K)
            s_F = K**p.alpha / (K**p.alpha + K_L**p.alpha)
            b_val = p.delta * K / p.r + c_tilde * K**p.gamma
            Kb_prime = p.delta * K / p.r + p.gamma * c_tilde * K**p.gamma
            return p.alpha * beta * (2.0 - s_F) - (beta - 1.0) * Kb_prime / b_val

        # Strictly decreasing bracket: positive at small K, negative at
        # large K under the interiority conditions above.
        K_F = float(np.exp(optimize.brentq(foc_bracket, -15.0, 15.0, xtol=1e-12)))
        X_F = self._follower_trigger(K_F, phi_L, K_L, phi_L, lev_F)
        return X_F, K_F, phi_L, lev_F

    # ------------------------------------------------------------------
    # Leader's problem
    # ------------------------------------------------------------------

    def _leader_revenue_drop(
        self, K_L: float, phi_L: float, K_F: float, phi_F: float, X_F: float
    ) -> float:
        """Drop in the leader's installed value when the follower enters."""
        V_mono_at_XF = self.monopolist_value_L(X_F, phi_L, K_L)
        V_duo_at_XF = self.installed_value_L(X_F, phi_L, K_L, phi_F, K_F)
        return V_mono_at_XF - V_duo_at_XF

    def leader_default_boundary(
        self,
        K_L: float,
        phi_L: float,
        lev_L: float,
        K_F: float,
        phi_F: float,
        X_F: float,
    ) -> tuple[float, float]:
        """Default boundary of a leader that anticipates follower entry.

        Before follower entry the leader's going-concern equity is

            E_L(X) = A X - N - drop (X/X_F)^beta_H + C_1 X^beta_neg,

        with A the monopoly-phase A_eff, N = C_D/r + delta K_L/r, drop the
        installed-value loss at follower entry (discounted with the
        paper's beta_H convention) and C_1 X^beta_neg the default option.
        Value matching E_L(X_D) = 0 and smooth pasting E_L'(X_D) = 0
        determine (X_D, C_1) jointly. The monopoly boundary of
        `default_boundary` is the drop = 0 special case; because the
        dilution term lowers equity, the anticipating leader's boundary
        lies above it.

        Without debt (c_D = 0) the same system gives the leader's
        shutdown boundary.

        Returns:
            (X_D, C_1); (0, 0) when there is neither a coupon nor an
            operating cost.
        """
        cache_key = ("leader_default", K_L, phi_L, lev_L, K_F, phi_F, X_F)
        if cache_key in self._cache:
            return self._cache[cache_key]

        p = self.params
        c_D = self.coupon_payment(K_L, lev_L)
        N = c_D / p.r + p.delta * K_L / p.r
        if N <= 0:
            return 0.0, 0.0
        A = self._effective_revenue_coeff(phi_L, K_L, 0.0, 0.0, monopolist=True)
        drop = self._leader_revenue_drop(K_L, phi_L, K_F, phi_F, X_F)
        beta_H = p.beta_H
        beta_neg = self._negative_root("L", self.endogenous_lambda(phi_L, K_L, 0, 0))

        def coefficient(X_D: float) -> float:
            # Smooth pasting solved for C_1 at a candidate boundary.
            slope_ex_option = A - drop * beta_H * X_D ** (beta_H - 1.0) / X_F**beta_H
            return -slope_ex_option * X_D ** (1.0 - beta_neg) / beta_neg

        def value_matching(X_D: float) -> float:
            C_1 = coefficient(X_D)
            return A * X_D - N - drop * (X_D / X_F) ** beta_H + C_1 * X_D**beta_neg

        X_D_mono = self.default_boundary(phi_L, K_L, 0.0, 0.0, lev_L)
        lo, hi = X_D_mono * 0.5, min(X_F, X_D_mono * 4.0)
        if value_matching(lo) * value_matching(hi) > 0:
            grid = np.geomspace(X_D_mono * 1e-3, X_F * (1.0 - 1e-9), 400)
            vals = np.array([value_matching(x) for x in grid])
            idx = np.where(np.sign(vals[:-1]) != np.sign(vals[1:]))[0]
            if idx.size == 0:
                msg = "No default boundary for the anticipating leader"
                raise RuntimeError(msg)
            lo, hi = grid[idx[0]], grid[idx[0] + 1]
        X_D = float(optimize.brentq(value_matching, lo, hi, xtol=1e-14))
        out = (X_D, float(coefficient(X_D)))
        self._cache[cache_key] = out
        return out

    def _leader_pre_entry_value(
        self,
        X: float,
        K_L: float,
        phi_L: float,
        lev_L: float,
        K_F: float,
        phi_F: float,
        X_F: float,
    ) -> float:
        """Leader's entry NPV at X < X_F (monopoly phase, entry anticipated).

        The going-concern claim carries the default option of
        `leader_default_boundary` (the shutdown option when there is no
        debt), is floored at zero below that boundary, and the sunk
        equity contribution is subtracted, matching the equity convention
        of `equity_value`.
        """
        p = self.params
        drop = self._leader_revenue_drop(K_L, phi_L, K_F, phi_F, X_F)
        entry_factor = (X / X_F) ** p.beta_H if X_F > 0 else 1.0
        X_D, C_1 = self.leader_default_boundary(K_L, phi_L, lev_L, K_F, phi_F, X_F)
        equity_contribution = (1.0 - lev_L) * self.investment_cost(K_L)
        if X_D <= 0:
            eq_mono = self.equity_value(X, phi_L, K_L, 0.0, 0.0, lev_L)
            return eq_mono - drop * entry_factor
        if X <= X_D:
            return -equity_contribution
        c_D = self.coupon_payment(K_L, lev_L)
        N = c_D / p.r + p.delta * K_L / p.r
        A = self._effective_revenue_coeff(phi_L, K_L, 0.0, 0.0, monopolist=True)
        beta_neg = self._negative_root("L", self.endogenous_lambda(phi_L, K_L, 0, 0))
        going_concern = A * X - N - drop * entry_factor + C_1 * X**beta_neg
        return max(going_concern, 0.0) - equity_contribution

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

        Before follower entry the claim is priced by
        `_leader_pre_entry_value`, whose default boundary is that of a
        leader anticipating entry (`leader_default_boundary`); after entry
        it is the duopoly `equity_value`, so the Leland default option
        enters on the same terms as the follower's. The pre-entry claim is
        not matched to the post-entry claim at X_F: the two differ by the
        difference between the monopoly-phase and duopoly default-option
        terms there, a small jump reported in Internet Appendix B.

        Returns the leader's entry NPV L(X), net of the sunk equity
        contribution and therefore negative at low demand -- the L(0) < 0
        endpoint of the existence argument. No clamp is applied here; the
        only limited-liability floor is the one on the going-concern
        claim.
        """
        X_F, K_F, phi_F, _ = self.pure_power_follower(K_L, phi_L)
        if X >= X_F:
            return self.equity_value(X, phi_L, K_L, phi_F, K_F, lev_L)
        return self._leader_pre_entry_value(X, K_L, phi_L, lev_L, K_F, phi_F, X_F)

    def _leader_objective(
        self,
        params_vec: np.ndarray,
    ) -> float:
        """Negative of leader's option value factor for (K, phi) optimization.

        params_vec = [log_K, phi]; leverage is fixed at the model's
        exogenous self.leverage (see _follower_objective for why leverage
        cannot be a free coordinate).
        Uses beta_H and A_eff (combined L+H revenue coefficient).
        """
        log_K, phi_L = params_vec

        # Bound checks first: exp(log_K) overflows outside the bounds
        # (log_K bounds match base_model's (-15, 15)).
        if log_K < -15 or log_K > 15:
            return 1e20
        if phi_L <= 0.01 or phi_L >= 0.99:
            return 1e20

        K_L = np.exp(log_K)
        p = self.params
        beta = p.beta_H
        lev_L = self.leverage

        # Revenue coefficient as monopolist
        a_eff = self._effective_revenue_coeff(phi_L, K_L, 0.0, 0.0, monopolist=True)

        c_D = self.coupon_payment(K_L, lev_L)
        equity_cost = (1.0 - lev_L) * self.investment_cost(K_L)
        b = p.delta * K_L / p.r + equity_cost + c_D / p.r

        if a_eff <= 0 or b <= 0:
            return 1e20
        return -(beta * np.log(a_eff) - (beta - 1.0) * np.log(b))

    def pure_power_leader_monopolist(
        self,
        regime: str = "H",
    ) -> tuple[float, float, float, float]:
        """Solve leader's problem ignoring preemption (monopolist trigger).

        The leader's (K, phi) maximizes the monopoly-phase option value;
        with leverage = 0 this coincides with the pure-power approximation
        SingleFirmModel.pure_power_trigger_capacity_phi (identical objectives).
        This is the leader of the nested approximation; in the model of
        record (`solve`) the leader chooses its scale at entry.

        Returns:
            (X_L_mono*, K_L*, phi_L*, lev_L): Leader's monopolist solution;
            lev_L equals the exogenous leverage.
        """
        cache_key = ("leader_mono", regime)
        if cache_key in self._cache:
            return self._cache[cache_key]

        p = self.params
        # The monopolist's A_eff is proportional to K^alpha (shares = 1),
        # so the problem inherits the single-firm interior-capacity
        # condition (A2); the leverage-adjusted cost has the same K-powers.
        # Without it the objective diverges as K -> 0 and the optimizer
        # would return a boundary artifact.
        premium_ratio = (1.0 - 1.0 / p.beta_H) / p.alpha
        if not 1.0 / p.gamma < premium_ratio < 1.0:
            msg = (
                f"No interior leader-monopolist optimum: condition (A2) "
                f"fails ((beta_H - 1)/(alpha*beta_H) = {premium_ratio:.3f}, "
                f"need {1 / p.gamma:.3f} < ratio < 1)."
            )
            raise RuntimeError(msg)

        lev_L = self.leverage
        best_params, best_val, diagnostics = multistart_minimize(
            self._leader_objective, _KPHI_STARTS
        )
        self.solver_diagnostics["leader_monopolist"] = diagnostics

        if best_params is None or best_val >= 1e19:
            msg = f"Leader optimization failed for regime={regime}"
            raise RuntimeError(msg)
        if diagnostics["n_converged"] == 0:
            msg = (
                f"Leader optimization did not converge from any of the "
                f"{diagnostics['n_starts']} starting points (regime={regime})"
            )
            raise RuntimeError(msg)

        K_L = np.exp(best_params[0])
        phi_L = np.clip(best_params[1], 0.01, 0.99)

        # Compute trigger using beta_H and A_eff
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
        X_F, K_F, phi_F, lev_F = self.pure_power_follower(K_L, phi_L, regime)
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
        _, K_L, phi_L, lev_L = self.pure_power_leader_monopolist(regime)
        leader_val = self._leader_value_at(X, K_L, phi_L, lev_L)
        follower_opt = self.follower_option_value(X, K_L, phi_L, regime)
        return leader_val - follower_opt

    def pure_power_preemption_equilibrium(
        self, regime: str = "H", strict: bool = True
    ) -> dict:
        """Preemption equilibrium of the nested pure-power game.

        The reduced-form game of the earlier draft, not the model of record
        (`solve`): the follower's option and the dilution of the leader's
        claim are priced with beta_H and the unconditional A_eff, and the
        leader is held at the monopoly-phase scale. Finds X_P where the
        value of leading first equals the value of following.

        Args:
            regime: Regime label (cache key; the equilibrium objects are
                built from the L-regime entry values throughout).
            strict: When True (the default, and what every paper,
                figure, and pipeline path uses), a failure to bracket or
                refine the rent-equalization root raises RuntimeError, and
                so does a gap with more than one sign change on the
                500-point search grid (``single_crossing`` False). The
                grid check is evidence of a single up-crossing at the
                resolution used, not a uniqueness proof.
                When False, the routine falls back to the corresponding
                endpoint of the search interval and logs a warning; the
                returned dict then has ``bracket_failed = True``. The
                escape hatch exists only for exploratory sweeps that
                prefer a flagged number to an exception -- a fallback
                endpoint is *not* an equilibrium and must never reach a
                reported result.

        Returns:
            Dict with equilibrium quantities for leader and follower,
            plus the diagnostics ``single_crossing``, ``n_sign_changes``,
            ``bracket_failed``, and ``solver_diagnostics``.

        Raises:
            RuntimeError: In strict mode, when the preemption gap does
                not cross zero inside (X_D, X_L^mono) or Brent's method
                fails on the bracketing interval.
        """
        cache_key = ("preemption_3d", regime, strict)
        if cache_key in self._cache:
            return self._cache[cache_key]

        X_L_mono, K_L, phi_L, lev_L = self.pure_power_leader_monopolist(regime)
        X_F, K_F, phi_F, lev_F = self.pure_power_follower(K_L, phi_L, regime)

        # Default boundaries: the leader's is that of a firm anticipating
        # follower entry (above the monopoly boundary), the follower's the
        # duopoly boundary.
        X_D_L, _ = self.leader_default_boundary(K_L, phi_L, lev_L, K_F, phi_F, X_F)
        X_D_F = self.default_boundary(phi_F, K_F, phi_L, K_L, lev_F)

        # Find the preemption point on (X_D, X_L^mono). The preemption
        # trigger is the *first* up-crossing of L(X) - F(X) and must lie
        # below the leader's unconstrained trigger X_L^mono. The gap
        # eventually turns negative again at high demand because (K_L,
        # phi_L) is held at the leader-role optimum rather than
        # re-optimized for late entry; that second crossing lies outside
        # the equilibrium path and the verification domain.
        X_low = max(X_D_L, X_L_mono * 0.001)
        X_high = X_L_mono

        grid = np.linspace(X_low, X_high, 500)
        gaps = np.array([self._preemption_gap(x, regime) for x in grid])
        sign_changes = np.sum(np.diff(np.sign(gaps)) != 0)
        single_crossing = bool(sign_changes == 1)

        bracket_failed = False
        reason = ""
        if gaps[0] >= 0:
            X_P = X_low
            bracket_failed = True
            reason = (
                f"the gap is already non-negative at the lower endpoint "
                f"(L - F = {gaps[0]:.4g} at X = {X_low:.4g})"
            )
        elif sign_changes == 0:
            X_P = X_L_mono
            bracket_failed = True
            reason = "the gap has no sign change on the search interval"
        else:
            # Bracket the first sign change and refine with Brent's method
            idx = int(np.argmax(np.diff(np.sign(gaps)) != 0))
            try:
                X_P = optimize.brentq(
                    self._preemption_gap,
                    grid[idx],
                    grid[idx + 1],
                    args=(regime,),
                    xtol=1e-10,
                )
            except ValueError as exc:
                X_P = X_L_mono
                bracket_failed = True
                reason = f"Brent's method failed on the bracketing interval: {exc}"
        if not bracket_failed and not single_crossing:
            # The root exists but the gap changes sign more than once on
            # the search interval: the reported X_P is the first up-crossing
            # and is not the unique candidate the paper describes.
            msg = (
                f"Preemption gap changes sign {int(sign_changes)} times on "
                f"({X_low:.4g}, {X_high:.4g}); the first up-crossing "
                f"X_P={X_P:.4g} is not a certified unique equilibrium."
            )
            if strict:
                raise RuntimeError(msg + " Rerun with strict=False to accept it.")
            logging.warning("%s (strict=False)", msg)
        if bracket_failed:
            if strict:
                msg = (
                    f"No preemption equilibrium on ({X_low:.4g}, {X_high:.4g}): "
                    f"{reason}. Rerun with strict=False to accept the "
                    f"flagged endpoint fallback X_P={X_P:.4g}."
                )
                raise RuntimeError(msg)
            logging.warning(
                "Preemption bracket failed on (%.4g, %.4g) because %s; "
                "using fallback X_P=%.4g (strict=False)",
                X_low,
                X_high,
                reason,
                X_P,
            )

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
            "single_crossing": single_crossing,
            "n_sign_changes": int(sign_changes),
            "bracket_failed": bracket_failed,
            "solver_diagnostics": dict(self.solver_diagnostics),
        }
        self._cache[cache_key] = result
        return result

    # ------------------------------------------------------------------
    # Leader-convention sensitivity: re-optimized leader scale
    # ------------------------------------------------------------------

    def _pure_power_follower_warm(
        self,
        K_L: float,
        phi_L: float,
        x0: np.ndarray,
    ) -> tuple[float, float, float, float]:
        """Follower best response from a single warm-started Nelder-Mead.

        Identical objective to pure_power_follower(), but with one starting
        point instead of the 16-point deterministic multistart. Used only
        inside pure_power_preemption_reoptimized_leader(), where the follower
        problem is re-solved at every evaluation of the leader's
        objective and the 16-start global search dominates the run time.
        The follower objective is smooth and single-peaked in (log K,
        phi) at every (K_L, phi_L) reached along the search, and the
        equilibrium returned by the sensitivity routine is cross-checked
        against the 16-start pure_power_follower() at the fixed point.
        """
        lev_F = self.leverage
        result = optimize.minimize(
            self._follower_objective,
            x0,
            args=(K_L, phi_L),
            method="Nelder-Mead",
            options={"maxiter": 2000, "xatol": 1e-8, "fatol": 1e-10},
        )
        if not np.isfinite(result.fun) or result.fun >= 1e19:
            msg = f"Warm follower solve failed for K_L={K_L:.6g}, phi_L={phi_L:.4f}"
            raise RuntimeError(msg)
        K_F = float(np.exp(result.x[0]))
        phi_F = float(np.clip(result.x[1], 0.01, 0.99))
        X_F = self._follower_trigger(K_F, phi_F, K_L, phi_L, lev_F)
        return X_F, K_F, phi_F, lev_F

    def _leader_value_reoptimized_at(
        self,
        X: float,
        K_L: float,
        phi_L: float,
        follower_x0: np.ndarray,
    ) -> float:
        """Leader entry NPV at X for a candidate (K_L, phi_L).

        Same three-phase construction as _leader_value_at(), but with the
        follower solved from a warm start (see _pure_power_follower_warm).
        """
        lev_L = self.leverage
        X_F, K_F, phi_F, _ = self._pure_power_follower_warm(K_L, phi_L, follower_x0)
        if X >= X_F:
            return self.equity_value(X, phi_L, K_L, phi_F, K_F, lev_L)
        return self._leader_pre_entry_value(X, K_L, phi_L, lev_L, K_F, phi_F, X_F)

    def pure_power_reoptimized_leader_policy(
        self,
        X: float,
        x0: np.ndarray | None = None,
    ) -> tuple[float, float, float]:
        """Leader's (K, phi) maximizing its entry NPV at demand X.

        Returns (L_star, K_L, phi_L), where L_star is the maximized entry
        NPV L(X; K_L, phi_L) with the follower best-responding to the
        chosen (K_L, phi_L).

        This replaces the paper's leader convention -- (K_L, phi_L) held
        at the monopoly-phase optimum of Proposition 1 -- by scale and
        allocation chosen for entry at X itself. Passing x0 runs a single
        warm-started Nelder-Mead from that point; omitting it runs the
        six-point deterministic multistart.
        """
        follower_x0 = np.array([-1.0, 0.70])

        def objective(v: np.ndarray) -> float:
            log_K, phi_L = v
            if log_K < -15.0 or log_K > 15.0:
                return 1e20
            if phi_L <= 0.01 or phi_L >= 0.99:
                return 1e20
            try:
                value = self._leader_value_reoptimized_at(
                    X, float(np.exp(log_K)), float(phi_L), follower_x0
                )
            except (ValueError, RuntimeError, FloatingPointError):
                return 1e20
            return -value if np.isfinite(value) else 1e20

        if x0 is not None:
            starts = [np.asarray(x0, dtype=float)]
        else:
            starts = [
                np.array([log_K0, phi0])
                for log_K0 in (-8.0, -5.0, -2.0)
                for phi0 in (0.35, 0.70)
            ]

        best_x, best_val, diagnostics = multistart_minimize(
            objective, starts, xatol=1e-9, fatol=1e-12
        )
        if best_x is None and x0 is not None:
            # A warm start may stop at the iteration cap while already
            # sitting on the optimum (it begins there); multistart_minimize
            # accepts converged starts only, so fall back to the cold
            # six-point multistart rather than reuse the unconverged point.
            cold = [
                np.array([log_K0, phi0])
                for log_K0 in (-8.0, -5.0, -2.0)
                for phi0 in (0.35, 0.70)
            ]
            best_x, best_val, diagnostics = multistart_minimize(
                objective, cold, xatol=1e-9, fatol=1e-12
            )
            diagnostics["warm_start_fallback"] = True
        self.solver_diagnostics["leader_reoptimized"] = diagnostics

        if best_x is None or best_val >= 1e19:
            msg = f"Leader re-optimization failed at X={X:.6g}"
            raise RuntimeError(msg)
        # The fixed point reached from a warm start is cross-checked
        # against the 16-start pure_power_follower() at the end of the calling
        # routine.
        if x0 is None and diagnostics["n_converged"] == 0:
            msg = (
                f"Leader re-optimization did not converge from any of the "
                f"{diagnostics['n_starts']} starting points at X={X:.6g}"
            )
            raise RuntimeError(msg)

        return (
            -best_val,
            float(np.exp(best_x[0])),
            float(np.clip(best_x[1], 0.01, 0.99)),
        )

    def pure_power_preemption_reoptimized_leader(
        self,
        regime: str = "H",
        n_grid: int = 40,
        x_low_factor: float = 1e-3,
    ) -> dict:
        """Nested pure-power game with a leader that re-optimizes scale.

        Sensitivity counterpart to pure_power_preemption_equilibrium(), which
        holds the leader's (K_L, phi_L) at the monopoly-phase optimum
        (the leader-scale convention). Here the leader chooses (K_L,
        phi_L) to maximize its entry NPV at the entry point itself, and
        the follower best-responds to that choice, so the leader's value
        of entering at X is the upper envelope

            L*(X) = max_{K, phi} L(X; K, phi),

        and X_P solves the rent-equalization condition on that envelope,

            L*(X_P) = F(X_P; K_L*(X_P), phi_L*(X_P)).

        The envelope gap is scanned on a log grid over
        (x_low_factor * X_L^mono, X_L^mono) with the leader's optimizer
        warm-started along the grid, then the first up-crossing is
        refined with Brent's method.

        The benchmark trigger X_L^mono in the reported discount is the
        single-firm (Proposition 1) monopolist trigger, which is common
        to both solutions, so the discount 1 - X_P / X_L^mono is
        comparable across the two.
        """
        cache_key = ("preemption_reopt", regime, n_grid, x_low_factor)
        if cache_key in self._cache:
            return self._cache[cache_key]

        X_L_mono, K_mono, phi_mono, lev_L = self.pure_power_leader_monopolist(regime)
        baseline = self.pure_power_preemption_equilibrium(regime)

        warm: dict[str, np.ndarray | None] = {"x0": None}

        grid = np.geomspace(X_L_mono * x_low_factor, X_L_mono, n_grid)
        gaps = np.empty(n_grid)
        policies: list[tuple[float, float]] = []
        for i, X in enumerate(grid):
            L_star, K_L, phi_L = self.pure_power_reoptimized_leader_policy(
                X, x0=warm["x0"] if i else None
            )
            warm["x0"] = np.array([np.log(K_L), phi_L])
            policies.append((K_L, phi_L))
            gaps[i] = L_star - self.follower_option_value(X, K_L, phi_L, regime)

        crossings = np.flatnonzero(np.diff(np.sign(gaps)) != 0)
        if gaps[0] >= 0 or crossings.size == 0:
            msg = (
                "Re-optimized preemption gap does not cross zero on "
                f"({grid[0]:.4g}, {grid[-1]:.4g})"
            )
            raise RuntimeError(msg)

        idx = int(crossings[0])
        warm["x0"] = np.array([np.log(policies[idx][0]), policies[idx][1]])

        def gap(X: float) -> float:
            _, K_L, phi_L = self.pure_power_reoptimized_leader_policy(X, x0=warm["x0"])
            warm["x0"] = np.array([np.log(K_L), phi_L])
            L_star = self._leader_value_at(X, K_L, phi_L, lev_L)
            return L_star - self.follower_option_value(X, K_L, phi_L, regime)

        X_P = float(optimize.brentq(gap, grid[idx], grid[idx + 1], xtol=1e-14))

        _, K_L, phi_L = self.pure_power_reoptimized_leader_policy(X_P, x0=warm["x0"])
        # Cross-check the fixed point with the 16-start follower solver.
        X_F, K_F, phi_F, lev_F = self.pure_power_follower(K_L, phi_L, regime)

        result = {
            "X_leader": X_P,
            "K_leader": K_L,
            "phi_leader": phi_L,
            "lev_leader": lev_L,
            "X_follower": X_F,
            "K_follower": K_F,
            "phi_follower": phi_F,
            "lev_follower": lev_F,
            "X_leader_monopolist": X_L_mono,
            "K_leader_convention": float(K_mono),
            "phi_leader_convention": float(phi_mono),
            "X_leader_convention": float(baseline["X_leader"]),
            "K_follower_convention": float(baseline["K_follower"]),
            "preemption_discount": 1.0 - X_P / X_L_mono,
            "preemption_discount_convention": 1.0
            - float(baseline["X_leader"]) / X_L_mono,
            "single_crossing": bool(crossings.size == 1),
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
        """Nested pure-power equilibrium over a range of parameter values."""
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
                    contest=self.contest,
                    recovery_rule=self.recovery_rule,
                )
                eq = m.pure_power_preemption_equilibrium(regime)
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
        """Nested pure-power equilibrium over a range of leverage levels."""
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
                    contest=self.contest,
                    recovery_rule=self.recovery_rule,
                )
                eq = m.pure_power_preemption_equilibrium(regime)
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
        """Summary of the nested pure-power equilibrium (exploratory pipeline)."""
        result = {}

        try:
            eq = self.pure_power_preemption_equilibrium(regime)
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
