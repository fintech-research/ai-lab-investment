"""Belief mismatch (Dario's dilemma) in the model of record (issue #180).

A firm that invests on a belief ``lambda_invest`` about the arrival rate of
the switch, when the true rate is ``lambda_true``, follows the policy that is
optimal under its belief; this module values that policy exactly under the
true rate and reports the loss against the true optimum. Nothing here uses
the pure-power pricing of the earlier draft (the nested approximation stays
in `ValuationAnalysis.pure_power_dilemma`).

Definitions
-----------
Reference demand. Every value is measured at one demand level X_0, held
fixed across beliefs, at which no firm is installed. A firm whose belief puts
its trigger at or below X_0 is in its investment region there and installs at
once, at the scale and allocation it believes best at X_0; a firm whose
trigger lies above X_0 waits for it; a firm whose belief says to wait for the
switch waits. After a switch without capacity every firm follows the same
policy, because the post-switch problem does not involve the arrival rate.
Losses are shares of the value of the correctly informed firm at X_0. They
are not invariant to X_0: the claim on the post-switch option is common to
every policy and its weight in firm value falls as X_0 rises toward the
trigger. The default is half the correctly informed firm's trigger (the
precommitted-scale trigger X* for the single firm, the first investment X_L
for the duopoly), and `SingleFirmMismatch.reference_sensitivity` reports the
dependence.

Single firm, two versions (`SingleFirmMismatch`):

- ``"precommitted"``: post-switch scale precommitted to K_H*, the problem of
  Proposition 1(iii). Every belief has a finite pre-switch trigger.
- ``"unrestricted"``: scale chosen at the switch. A belief at or above about
  0.073 says to wait for the switch, and so does the truth at baseline; such
  a belief costs nothing. A belief below it invests before the switch.

Decomposition. With (X, K, phi) the entry demand, capacity and training
fraction the mistaken firm ends up with: *timing* is the loss of a firm that
invests at the mistaken firm's entry demand X but with the capacity and
allocation that are best there under the truth; the remainder is split
between *capacity* and *allocation* by averaging the two orders in which K
and phi can be moved to their mistaken values. The three sum to the loss.

Leverage (`SingleFirmMismatch.levered`). The operating policy is the
unlevered one at each belief and leverage is layered on it, as in the credit
exhibits of issue #179: the claims are those of
`preemption_levered.LeveredPreemptionGame` without a rival (option to stop
operating, coupled boundary, debt priced under the recovery rule), and the
value is the shareholders' entry value E - (1 - l) I, which under fairly
priced debt is firm value less the outlay. The tail risk is the distance of
the entry demand to the boundary at which the firm stops operating, and the
five-year first-passage probability of that boundary under the L-regime
drift with the switch omitted (the convention of `tbl-credit-pd`).

Duopoly (`DuopolyMismatch`). The benchmark is the equilibrium of the entry
game in which one firm leads at X_L and the other follows
(`preemption_levered.assigned_leader_equilibrium`), both at the true rate.
One firm holds the belief ``lambda_invest``; its rival holds the truth and
knows the mistaken firm's policy.

- Mistaken leader. It best-responds, under its belief, to what its rival
  does: the rival follows, and after the leader's entry waits for the switch
  (the follower's best response at the true rate in every cell computed;
  ``rival_pre_switch_entry`` records it). The mistaken leader therefore
  invests at the demand, capacity and allocation that maximize its believed
  value of leading over mutual waiting, or at once at X_0 when that demand
  lies at or below X_0. For a belief at which a follower would also wait for
  the switch (0.075 and above at baseline) this is the leader's policy of
  the equilibrium of the game at that belief, and the cached equilibria
  reproduce it; below, a rival sharing the belief would enter before the
  switch, which the informed rival does not do.
- Mistaken follower. After the leader's entry its post-switch policy does not
  involve the arrival rate, so a mistaken follower that stays a follower and
  waits for the switch loses nothing. Its belief matters in two ways only.
  It may enter before the switch (``X_pre_switch``), and it may take the
  lead: before the leader's entry it compares, under its belief, leading at
  the demand it likes best below X_L with waiting for the rival's entry at
  X_L, and invests first when leading is worth more. Roles then change: the
  rival, which prefers following to leading below the rent-equalization
  trigger, follows, the outcome is the mistaken leader's, and the loss is
  measured against the benchmark follower's value.

``rival_margin`` reports whether the rival indeed prefers to follow: the
smallest excess, over a demand scan between X_0 and the mistaken firm's
entry, of its value of waiting for that entry over its value of investing
first, as a fraction of the former. Under leverage the policies are the
unlevered ones (the leader's policy of the unlevered equilibrium, as in issue
#179) and only the claims change.

The policies and the losses are cached in `duopoly_dilemma.json`;
``python -m ai_lab_investment.models.belief_mismatch`` rewrites it.
"""

import json
from dataclasses import dataclass
from math import inf, isfinite
from pathlib import Path
from typing import Any

import numpy as np

from .duopoly import DEFAULT_RECOVERY_RULE, cached_equilibrium
from .parameters import ModelParameters
from .piecewise_option import SingleFirmSolution, solve_single_firm

VERSIONS: tuple[str, ...] = ("precommitted", "unrestricted")

#: Leverage levels of the levered dilemma (issue #180).
DILEMMA_LEVERAGES: tuple[float, ...] = (0.0, 0.01, 0.05, 0.15, 0.40)

#: Coupon rate and bankruptcy cost of the credit block (as in `valuation`).
COUPON_RATE = 0.05
BANKRUPTCY_COST = 0.30

DILEMMA_GRID_PATH = Path(__file__).with_name("duopoly_dilemma.json")


# ----------------------------------------------------------------------
# Error metrics
# ----------------------------------------------------------------------


def additive_pair(lambda_true: float, size: float) -> tuple[float, float]:
    """Beliefs ``size`` below and above the truth, in units of lambda."""
    return lambda_true - size, lambda_true + size


def proportional_pair(lambda_true: float, factor: float) -> tuple[float, float]:
    """Beliefs a factor ``factor`` below and above the truth (equal in logs)."""
    return lambda_true / factor, lambda_true * factor


def horizon_pair(lambda_true: float, years: float) -> tuple[float, float]:
    """Beliefs whose expected time to the switch, 1 / lambda, is ``years``
    longer and shorter than the truth's."""
    horizon = 1.0 / lambda_true
    if years >= horizon:
        msg = f"A horizon error of {years} years exceeds the true horizon {horizon}"
        raise ValueError(msg)
    return 1.0 / (horizon + years), 1.0 / (horizon - years)


def matched_pairs(
    lambda_true: float = 0.10, additive: float = 0.08
) -> dict[str, tuple[float, float]]:
    """The pairs of beliefs the paper quotes, around ``lambda_true``.

    ``"additive"`` is the pair ``additive`` below and above the truth. The
    other pairs are built from its two members: ``"proportional_low"`` and
    ``"proportional_high"`` are the pairs equal in logs that contain the
    pessimistic and the optimistic member, and ``"horizon"`` is the pair
    equal in expected years to the switch that contains the optimistic
    member (no optimistic belief matches the horizon error of the
    pessimistic member when that error exceeds the true horizon).
    """
    low, high = additive_pair(lambda_true, additive)
    years = 1.0 / lambda_true - 1.0 / high
    return {
        "additive": (low, high),
        "proportional_low": proportional_pair(lambda_true, lambda_true / low),
        "proportional_high": proportional_pair(lambda_true, high / lambda_true),
        "horizon": horizon_pair(lambda_true, years),
    }


def first_passage_probability(
    params: ModelParameters, X: float, X_D: float, horizon: float = 5.0
) -> float:
    """Probability of reaching X_D from X within ``horizon`` years in regime L
    (switch omitted), the convention of the on-policy credit table."""
    from .valuation import ValuationAnalysis

    return ValuationAnalysis(params)._first_passage_probability(X, X_D, "L", horizon)


# ----------------------------------------------------------------------
# Single firm
# ----------------------------------------------------------------------


@dataclass(frozen=True)
class BeliefPolicy:
    """What a firm with belief ``lam`` does from the reference demand.

    Attributes:
        lam: The belief.
        trigger, K_trigger: Its own pre-switch trigger and the capacity it
            would install there (inf and nan when it waits for the switch).
        phi: Its training fraction.
        X_entry: Demand at which it invests, starting from the reference
            demand: the larger of the two (inf when it waits).
        K: Capacity it installs there.
    """

    lam: float
    trigger: float
    K_trigger: float
    phi: float
    X_entry: float
    K: float

    @property
    def waits(self) -> bool:
        return not isfinite(self.X_entry)

    @property
    def immediate(self) -> bool:
        return isfinite(self.X_entry) and self.trigger <= self.X_entry * (1.0 - 1e-12)


class SingleFirmMismatch:
    """Dario's dilemma for the single firm in the exact problem.

    Args:
        params: Model parameters; ``params.lam`` is ignored.
        lambda_true: True arrival rate.
        version: ``"precommitted"`` or ``"unrestricted"`` (module docstring).
        X_0: Reference demand; by default ``x0_ratio`` times the
            precommitted-scale trigger at the true rate, in both versions, so
            that the two are compared at one demand level.
        x0_ratio: See ``X_0``.
        recovery_rule: Recovery rule of the levered claims.
    """

    def __init__(
        self,
        params: ModelParameters,
        lambda_true: float = 0.10,
        version: str = "precommitted",
        X_0: float | None = None,
        x0_ratio: float = 0.5,
        recovery_rule: str = DEFAULT_RECOVERY_RULE,
    ):
        if version not in VERSIONS:
            msg = f"version must be one of {VERSIONS}, got {version!r}"
            raise ValueError(msg)
        self.params = params
        self.lambda_true = float(lambda_true)
        self.version = version
        self.recovery_rule = recovery_rule
        self._solutions: dict[float, SingleFirmSolution] = {}
        self.truth = self._solution(self.lambda_true)
        self.X_ref = self.truth.precommitted.X_star
        self.X_0 = float(X_0) if X_0 is not None else x0_ratio * self.X_ref
        self.bp = params.with_param(lam=self.lambda_true).beta_L
        self._games: dict[tuple[float, str], Any] = {}
        self.optimum = self.policy(self.lambda_true)
        self.value_optimal = self.policy_value(self.optimum)

    # -- policies ---------------------------------------------------------

    def _solution(self, lam: float) -> SingleFirmSolution:
        key = float(lam)
        if key not in self._solutions:
            self._solutions[key] = solve_single_firm(self.params.with_param(lam=key))
        return self._solutions[key]

    def policy(self, lam: float) -> BeliefPolicy:
        """Policy of a firm with belief ``lam``, from the reference demand."""
        sol = self._solution(lam)
        if self.version == "precommitted":
            trigger, K = sol.precommitted.X_star, sol.precommitted.K
        else:
            trigger, K = sol.X_star, sol.K_star
        if not isfinite(trigger):
            return BeliefPolicy(float(lam), inf, float("nan"), sol.phi_star, inf, K)
        X_entry, K_entry = trigger, K
        if trigger <= self.X_0:
            model = sol._unrestricted
            X_entry = self.X_0
            K_entry = float(
                model._static_capacity(model.g_star, np.array([X_entry]))[0]
            )
        return BeliefPolicy(float(lam), trigger, K, sol.phi_star, X_entry, K_entry)

    def truth_scale(self, X: float) -> float:
        """Capacity that is statically optimal at X under the true rate."""
        model = self.truth._unrestricted
        return float(model._static_capacity(model.g_star, np.array([X]))[0])

    # -- exact values under the true rate ---------------------------------

    def payoff(self, K: float, phi: float, X: float) -> float:
        """Net payoff of installing (K, phi) at X under the true rate."""
        return float(self.truth._unrestricted.exercise_payoff(K, phi, X))

    def waiting_value(self, X: float) -> float:
        """Value of never investing before the switch under the true rate."""
        if self.version == "precommitted":
            return self.truth.precommitted_waiting_value(X)
        return self.truth.waiting_value(X)

    def value(self, X_entry: float, K: float, phi: float) -> float:
        """Value at X_0 of "install (K, phi) at X_entry" (inf: never)."""
        wait = self.waiting_value(self.X_0)
        if not isfinite(X_entry):
            return wait
        if X_entry <= self.X_0:
            return self.payoff(K, phi, self.X_0)
        premium = self.payoff(K, phi, X_entry) - self.waiting_value(X_entry)
        return wait + premium * (self.X_0 / X_entry) ** self.bp

    def policy_value(self, policy: BeliefPolicy) -> float:
        return self.value(policy.X_entry, policy.K, policy.phi)

    # -- the dilemma ------------------------------------------------------

    def decomposition(self, policy: BeliefPolicy) -> dict[str, float]:
        """Timing, capacity and allocation components of the value lost."""
        full = self.policy_value(policy)
        if policy.waits:
            return {
                "timing": self.value_optimal - full,
                "capacity": 0.0,
                "allocation": 0.0,
            }
        X, phi_true = policy.X_entry, self.truth.phi_star
        K_true = self.truth_scale(X)
        at_date = self.value(X, K_true, phi_true)
        only_K = self.value(X, policy.K, phi_true)
        only_phi = self.value(X, K_true, policy.phi)
        return {
            "timing": self.value_optimal - at_date,
            "capacity": 0.5 * ((at_date - only_K) + (only_phi - full)),
            "allocation": 0.5 * ((at_date - only_phi) + (only_K - full)),
        }

    def loss(self, lambda_invest: float) -> dict[str, Any]:
        """Loss of a firm that invests on the belief ``lambda_invest``.

        Returns:
            Dict with the two policies, ``value_optimal``,
            ``value_mismatch``, ``value_loss`` and ``value_loss_pct`` (a
            fraction of the optimal value at X_0), ``premium_loss_pct`` (the
            same loss as a fraction of what the option to invest before the
            switch is worth at X_0, nan when that is zero), and the three
            components of `decomposition` as fractions of the optimal value.
        """
        pol = self.policy(lambda_invest)
        value = self.policy_value(pol)
        best = self.value_optimal
        premium = best - self.waiting_value(self.X_0)
        parts = self.decomposition(pol)
        return {
            "lambda_true": self.lambda_true,
            "lambda_invest": float(lambda_invest),
            "version": self.version,
            "X_0": self.X_0,
            "X_optimal": self.optimum.X_entry,
            "K_optimal": self.optimum.K,
            "phi_optimal": self.optimum.phi,
            "trigger_mismatch": pol.trigger,
            "X_mismatch": pol.X_entry,
            "K_mismatch": pol.K,
            "phi_mismatch": pol.phi,
            "waits": pol.waits,
            "immediate": pol.immediate,
            "value_optimal": best,
            "value_mismatch": value,
            "value_loss": best - value,
            "value_loss_pct": (best - value) / best,
            "premium_loss_pct": (best - value) / premium
            if premium > 1e-12 * best
            else float("nan"),
            "timing_pct": parts["timing"] / best,
            "capacity_pct": parts["capacity"] / best,
            "allocation_pct": parts["allocation"] / best,
            "is_conservative": lambda_invest < self.lambda_true,
        }

    def matched(self, low: float, high: float) -> dict[str, float]:
        """Losses at a pair of beliefs and their ratio (low over high)."""
        loss_low = self.loss(low)["value_loss_pct"]
        loss_high = self.loss(high)["value_loss_pct"]
        return {
            "lambda_low": low,
            "lambda_high": high,
            "loss_low": loss_low,
            "loss_high": loss_high,
            "ratio": loss_low / loss_high if loss_high > 0.0 else inf,
        }

    def third_derivative(self, step: float) -> float:
        """Central finite-difference third derivative, in the belief, of the
        value of the belief's policy at the true rate (units of the optimal
        value). Its sign orders the losses from small equal additive errors."""
        w = [
            self.policy_value(self.policy(self.lambda_true + k * step))
            for k in (-2, -1, 1, 2)
        ]
        third = (w[3] - 2.0 * w[2] + 2.0 * w[1] - w[0]) / (2.0 * step**3)
        return float(third / self.value_optimal)

    def reference_sensitivity(
        self, beliefs: tuple[float, ...], ratios: tuple[float, ...]
    ) -> list[dict[str, float]]:
        """Losses at ``beliefs`` for reference demands ``ratios`` times X*."""
        rows = []
        for ratio in ratios:
            other = SingleFirmMismatch(
                self.params,
                self.lambda_true,
                self.version,
                X_0=ratio * self.X_ref,
                recovery_rule=self.recovery_rule,
            )
            row = {"x0_ratio": ratio, "X_0": other.X_0}
            for lam in beliefs:
                row[f"loss_{lam:g}"] = other.loss(lam)["value_loss_pct"]
            rows.append(row)
        return rows

    # -- leverage ---------------------------------------------------------

    def _levered_game(self, leverage: float, debt: str):
        from .preemption_levered import LeveredPreemptionGame

        key = (float(leverage), debt)
        if key not in self._games:
            scale = "precommitted" if self.version == "precommitted" else "envelope"
            game = LeveredPreemptionGame(
                self.params.with_param(lam=self.lambda_true),
                scale,
                leverage,
                COUPON_RATE,
                BANKRUPTCY_COST,
                debt,
                recovery_rule=self.recovery_rule,
            )
            entry = game.follower_post_switch_entry(0.0)
            wait = game.follower_waiting_claim(entry, game.follower_table(entry))
            self._games[key] = (game, wait)
        return self._games[key]

    def _levered_value(self, leverage: float, debt: str, pol: BeliefPolicy) -> float:
        game, wait = self._levered_game(leverage, debt)
        wait_0 = float(wait(self.X_0)[0])
        if pol.waits:
            return wait_0
        payoff = game.follower_l_payoff(pol.X_entry, pol.K, pol.phi, 0.0, 0.0)
        if pol.X_entry <= self.X_0:
            return payoff
        premium = payoff - float(wait(pol.X_entry)[0])
        return wait_0 + premium * (self.X_0 / pol.X_entry) ** self.bp

    def _tail(self, leverage: float, debt: str, pol: BeliefPolicy) -> dict[str, float]:
        if pol.waits:
            return {"X_D": float("nan"), "distance": inf, "default_probability": 0.0}
        game, _ = self._levered_game(leverage, debt)
        X_D = game.installed_credit(pol.K, pol.phi, pol.X_entry)["X_default"]
        p_true = self.params.with_param(lam=self.lambda_true)
        return {
            "X_D": X_D,
            "distance": pol.X_entry / X_D,
            "default_probability": first_passage_probability(p_true, pol.X_entry, X_D),
        }

    def levered(
        self, lambda_invest: float, leverage: float = 0.40, debt: str = "fair"
    ) -> dict[str, Any]:
        """The dilemma on the levered claims, policies held at the unlevered
        ones (module docstring).

        Returns:
            Dict with ``value_optimal``, ``value_mismatch`` and
            ``value_loss_pct`` on the shareholders' entry value, and for each
            policy the boundary at which the firm stops operating, the
            distance X / X_D at entry and the five-year first-passage
            probability (``X_D_*``, ``distance_*``, ``default_prob_*``). A
            firm that waits for the switch has no pre-switch boundary.
        """
        pol = self.policy(lambda_invest)
        best = self._levered_value(leverage, debt, self.optimum)
        value = self._levered_value(leverage, debt, pol)
        tail_opt = self._tail(leverage, debt, self.optimum)
        tail_mis = self._tail(leverage, debt, pol)
        return {
            "lambda_true": self.lambda_true,
            "lambda_invest": float(lambda_invest),
            "version": self.version,
            "leverage": leverage,
            "debt": debt,
            "X_0": self.X_0,
            "value_optimal": best,
            "value_mismatch": value,
            "value_loss": best - value,
            "value_loss_pct": (best - value) / best,
            "X_D_optimal": tail_opt["X_D"],
            "X_D_mismatch": tail_mis["X_D"],
            "distance_optimal": tail_opt["distance"],
            "distance_mismatch": tail_mis["distance"],
            "default_prob_optimal": tail_opt["default_probability"],
            "default_prob_mismatch": tail_mis["default_probability"],
            "is_conservative": lambda_invest < self.lambda_true,
        }


# ----------------------------------------------------------------------
# Duopoly
# ----------------------------------------------------------------------

#: Beliefs of the cached duopoly dilemma: the arrival rates of
#: `duopoly_equilibria.json` other than the truth, plus the members of
#: `matched_pairs` that are not among them.
DILEMMA_BELIEFS: tuple[float, ...] = (
    0.02,
    0.03,
    0.05,
    0.10 / 1.8,
    9.0 / 130.0,
    0.075,
    0.15,
    0.18,
    0.20,
    0.25,
    0.30,
    0.40,
    0.50,
)

#: Debt conventions of the cached cells at positive leverage.
DILEMMA_DEBTS: tuple[str, ...] = ("fair", "par")


def load_dilemma_grid() -> dict[str, Any]:
    """Cached duopoly dilemma at the baseline calibration.

    Keys: ``lambda_true``, ``X_0``, ``x0_ratio``; ``policies`` (one record
    per belief, `DuopolyMismatch.belief_policy`); ``cells`` (one record per
    belief, role, leverage and debt convention, `DuopolyMismatch.cell`).
    """
    from .preemption_levered import decode_record

    with DILEMMA_GRID_PATH.open() as handle:
        raw = json.load(handle)
    for key in ("policies", "cells"):
        raw[key] = [decode_record(record) for record in raw[key]]
    return raw


def cached_dilemma_cell(
    lambda_invest: float, role: str, leverage: float = 0.0, debt: str = "fair"
) -> dict[str, Any]:
    """One cell of `load_dilemma_grid`.

    Raises:
        KeyError: If the cell is not in the cache.
    """
    for cell in load_dilemma_grid()["cells"]:
        if (
            abs(cell["lambda_invest"] - lambda_invest) < 1e-9
            and cell["role"] == role
            and abs(cell["leverage"] - leverage) < 1e-12
            and (cell["debt"] == debt or leverage == 0.0)
        ):
            return cell
    msg = (
        f"No cached duopoly dilemma for belief {lambda_invest}, {role}, "
        f"leverage={leverage}, {debt}"
    )
    raise KeyError(msg)


def _rival_waits_game(params: ModelParameters, recovery_rule: str):
    """Unlevered entry game in which the rival, once it follows, never
    enters before the switch: what the mistaken firm faces when its rival
    holds the truth and the truth says to wait (checked in each cell)."""
    from .preemption_exact import PreSwitchEntry
    from .preemption_levered import LeveredPreemptionGame

    class RivalWaits(LeveredPreemptionGame):
        def follower_pre_switch_entry(self, claim, N_L, T_L) -> PreSwitchEntry:
            return PreSwitchEntry(0.0, inf, float("nan"), float("nan"), float("nan"))

    return RivalWaits(
        params,
        "envelope",
        0.0,
        COUPON_RATE,
        BANKRUPTCY_COST,
        "par",
        recovery_rule=recovery_rule,
    )


class DuopolyMismatch:
    """Dario's dilemma inside the entry equilibrium (module docstring).

    Args:
        params: Model parameters; ``params.lam`` is ignored.
        lambda_true: True arrival rate; its unlevered equilibrium must be in
            `duopoly_equilibria.json` or be passed as ``truth``.
        x0_ratio: Reference demand as a fraction of the true first
            investment X_L.
        truth: Unlevered equilibrium record at the true rate.
        policies: Belief policies already computed (records of
            `belief_policy`), reused instead of re-solved.
        recovery_rule: Recovery rule of the levered claims.
    """

    #: Demand scan behind the mistaken firm's trigger: points and upper end
    #: in units of the true first investment X_L (the scan starts at X_0).
    SCAN: tuple[int, float] = (15, 2.0)

    def __init__(
        self,
        params: ModelParameters,
        lambda_true: float = 0.10,
        x0_ratio: float = 0.5,
        truth: dict | None = None,
        policies: list[dict] | None = None,
        recovery_rule: str = DEFAULT_RECOVERY_RULE,
    ):
        self.params = params
        self.lambda_true = float(lambda_true)
        self.recovery_rule = recovery_rule
        if truth is None:
            truth = cached_equilibrium(lam=self.lambda_true)
        self.truth = truth
        self.X_L = float(truth["X_L"])
        self.K_L = float(truth["K_L"])
        self.phi_L = float(truth["phi_L"])
        self.X_0 = x0_ratio * self.X_L
        self.x0_ratio = x0_ratio
        self._games: dict[tuple[float, float, str], Any] = {}
        self._belief_games: dict[float, Any] = {}
        self._policies: dict[float, dict] = {
            float(r["lambda_invest"]): r for r in policies or []
        }
        self._scan: tuple[np.ndarray, np.ndarray] | None = None
        self.bp = self.game(self.lambda_true).bp

    # -- games --------------------------------------------------------------

    def game(self, lam: float, leverage: float = 0.0, debt: str = "par"):
        """The entry game at arrival rate ``lam`` (cached)."""
        from .preemption_levered import LeveredPreemptionGame

        key = (float(lam), float(leverage), debt if leverage > 0.0 else "par")
        if key not in self._games:
            self._games[key] = LeveredPreemptionGame(
                self.params.with_param(lam=lam),
                "envelope",
                leverage,
                COUPON_RATE,
                BANKRUPTCY_COST,
                key[2],
                recovery_rule=self.recovery_rule,
            )
        return self._games[key]

    def belief_game(self, lam: float):
        """The game a firm with belief ``lam`` leads in: its rival follows
        and waits for the switch (`_rival_waits_game`)."""
        key = float(lam)
        if key not in self._belief_games:
            self._belief_games[key] = _rival_waits_game(
                self.params.with_param(lam=key), self.recovery_rule
            )
        return self._belief_games[key]

    # -- the mistaken firm's policy (under its belief) ----------------------

    def _believed_trigger(self, game) -> tuple[float, float, float, float, float]:
        """First investment of a firm that leads under the belief of ``game``.

        Maximizes h(X) = [L*(X) - W(X)] X^{-beta_L^+}, the believed
        coefficient of leading at X over mutual waiting, on a demand scan
        from X_0 up, refined between the neighbours of the best scan point;
        a maximum at X_0 itself means that the believed trigger lies at or
        below X_0 (h is single-peaked in every cached equilibrium), so that
        the firm invests at once.

        Returns:
            (X, K, phi, believed entry value L*(X), h(X)).
        """
        from scipy import optimize

        wait = game.mutual_waiting_claim("reoptimized")
        points, top = self.SCAN
        grid = np.geomspace(self.X_0, top * self.X_L, points)

        def at(X: float, start) -> tuple[float, float, float, float]:
            K, phi, lead = game.leader_best_policy(X, start)
            return K, phi, lead, (lead - float(wait(X)[0])) * X ** (-game.bp)

        cold = game.leader_best_policy(float(grid[0]))
        rows = [at(float(grid[0]), cold[:2])]
        for X in grid[1:]:
            rows.append(at(float(X), rows[-1][:2]))
        h = np.array([row[3] for row in rows])
        i = int(np.argmax(h))
        if i == len(grid) - 1:
            msg = "The believed trigger lies above the demand scan"
            raise RuntimeError(msg)
        res = optimize.minimize_scalar(
            lambda z: -at(float(np.exp(z)), rows[i][:2])[3] / abs(h[i]),
            bounds=(np.log(grid[max(i - 1, 0)]), np.log(grid[i + 1])),
            method="bounded",
            options={"xatol": 1e-4},
        )
        X = float(np.exp(res.x))
        best = at(X, rows[i][:2])
        if best[3] <= h[i]:
            # No interior improvement: the scan point itself, which is X_0
            # when the believed trigger lies at or below it.
            X, best = float(grid[i]), rows[i]
        K, phi, lead, coefficient = best
        return X, K, phi, lead, coefficient

    def belief_policy(self, lambda_invest: float) -> dict:
        """What a firm with belief ``lambda_invest`` does in each role.

        Everything here is valued under the firm's belief, against a rival
        that behaves as it does at the true rate.

        Returns:
            Dict with ``X_entry``, ``K``, ``phi`` and ``immediate`` (its
            first investment as the leader: the demand, capacity and
            training fraction that maximize its believed value of leading,
            or investment at once at X_0 when its trigger lies at or below
            X_0); ``leads_before_switch`` (0.0 when it believes that waiting
            for the switch beats leading at every demand scanned);
            ``follower_takes_lead`` with the demand and policy at which it
            would (``X_lead``, ``K_lead``, ``phi_lead``) and the two
            believed values compared there (``believed_lead_value``,
            ``believed_follow_value``); and its pre-switch entry as a
            follower against the true leader (``X_pre_switch``, inf when it
            waits for the switch, ``K_pre_switch``, ``phi_pre_switch``).
        """
        key = float(lambda_invest)
        for cached, record in self._policies.items():
            if abs(cached - key) < 1e-9:
                return record
        leading = self.belief_game(key)
        wait = leading.mutual_waiting_claim("reoptimized")
        X_entry, K, phi, lead, h = self._believed_trigger(leading)
        immediate = X_entry <= self.X_0 * (1.0 + 1e-12)

        # As the designated follower: lead at the demand it likes best
        # below the rival's entry at X_L, or wait for that entry?
        X_lead, K_lead, phi_lead, lead_value = X_entry, K, phi, lead
        if X_entry >= self.X_L:
            X_lead = self.X_L
            K_lead, phi_lead, lead_value = leading.leader_best_policy(X_lead, (K, phi))
        against_truth = self.game(key).subgame(self.K_L, self.phi_L)
        follow_at_entry = float(against_truth.follower_value(self.X_L)[0])
        follow = (
            float(wait(X_lead)[0])
            + (follow_at_entry - float(wait(self.X_L)[0]))
            * (X_lead / self.X_L) ** leading.bp
        )
        pre = against_truth.pre_switch
        record = {
            "lambda_true": self.lambda_true,
            "lambda_invest": key,
            "X_0": self.X_0,
            "X_entry": X_entry,
            "K": K,
            "phi": phi,
            "immediate": float(immediate),
            "believed_entry_value": lead,
            "leads_before_switch": float(h > 0.0),
            "X_lead": X_lead,
            "K_lead": K_lead,
            "phi_lead": phi_lead,
            "believed_lead_value": lead_value,
            "believed_follow_value": follow,
            "follower_takes_lead": float(h > 0.0 and lead_value > follow),
            "X_pre_switch": float(pre.X_entry),
            "K_pre_switch": float(pre.K),
            "phi_pre_switch": float(pre.phi),
        }
        self._policies[key] = record
        return record

    # -- values under the true rate ----------------------------------------

    def _before_entry(self, game, value_at_entry: float, X_entry: float) -> float:
        """Value at X_0 of a claim worth ``value_at_entry`` when the first
        investment occurs at X_entry, and the mutual-waiting value if the
        switch comes first."""
        if X_entry <= self.X_0 * (1.0 + 1e-12):
            return value_at_entry
        wait = game.mutual_waiting_claim("reoptimized")
        premium = value_at_entry - float(wait(X_entry)[0])
        return float(wait(self.X_0)[0]) + premium * (self.X_0 / X_entry) ** self.bp

    def _outcome(self, game, X_entry: float, K: float, phi: float) -> dict[str, float]:
        """Both firms' values at X_0, and the leader's tail objects, when one
        firm leads at X_entry with (K, phi) and the other follows."""
        sub = game.subgame(K, phi)
        credit = sub.leader_credit(X_entry)
        p_true = self.params.with_param(lam=self.lambda_true)
        follow = float(sub.follower_value(X_entry)[0])
        return {
            "leader": self._before_entry(
                game, float(sub.leader_value(X_entry)[0]), X_entry
            ),
            "follower": self._before_entry(game, follow, X_entry),
            "follower_at_entry": follow,
            "X_D": credit["X_default"],
            "distance": X_entry / credit["X_default"],
            "default_probability": first_passage_probability(
                p_true, X_entry, credit["X_default"]
            ),
            "rival_pre_switch_entry": float(sub.pre_switch.X_entry),
        }

    def benchmark(self, leverage: float = 0.0, debt: str = "fair") -> dict[str, float]:
        """Values at X_0 in the equilibrium at the true rate (the leader's
        policy that of the unlevered equilibrium at every leverage)."""
        game = self.game(self.lambda_true, leverage, debt)
        return self._outcome(game, self.X_L, self.K_L, self.phi_L)

    def _leader_scan(self) -> tuple[np.ndarray, np.ndarray]:
        """L*(X) of the true unlevered game on the demand scan."""
        if self._scan is None:
            game = self.game(self.lambda_true)
            points, top = self.SCAN
            grid = np.geomspace(self.X_0, top * self.X_L, points)
            policy = (self.K_L, self.phi_L)
            values = []
            for X in grid:
                K, phi, lead = game.leader_best_policy(float(X), policy)
                policy = (K, phi)
                values.append(lead)
            self._scan = (grid, np.array(values))
        return self._scan

    def rival_margin(self, X_entry: float, follower_at_entry: float) -> float:
        """Whether the rival, at the true rate, prefers to follow.

        Smallest excess of its value of waiting for the mistaken firm's
        entry at X_entry (worth ``follower_at_entry`` to it then) over its
        value of investing first, L*(X), on the scan points between X_0 and
        X_entry and at X_entry, as a fraction of the former.
        """
        game = self.game(self.lambda_true)
        wait = game.mutual_waiting_claim("reoptimized")
        lead_at_entry = game.leader_best_policy(X_entry, (self.K_L, self.phi_L))[2]
        margin = (follower_at_entry - lead_at_entry) / follower_at_entry
        if X_entry <= self.X_0 * (1.0 + 1e-12):
            return margin
        grid, lead = self._leader_scan()
        keep = grid < X_entry
        stay = (
            wait(grid[keep])
            + (follower_at_entry - float(wait(X_entry)[0]))
            * (grid[keep] / X_entry) ** self.bp
        )
        return float(min(margin, np.min((stay - lead[keep]) / stay)))

    def _lead_decomposition(
        self, X_entry: float, K: float, phi: float, best: float
    ) -> dict[str, float]:
        """Timing, capacity and allocation components for a firm that leads
        at X_entry with (K, phi), against the value ``best`` (unlevered).

        Timing is the loss of leading at X_entry with the capacity and
        allocation that are best there at the true rate; when ``best`` is
        the benchmark follower's value it also carries the change of role.
        """
        game = self.game(self.lambda_true)
        K_true, phi_true, _ = game.leader_best_policy(X_entry, (self.K_L, self.phi_L))

        def worth(k: float, f: float) -> float:
            lead = float(game.subgame(k, f).leader_value(X_entry)[0])
            return self._before_entry(game, lead, X_entry)

        at_date, full = worth(K_true, phi_true), worth(K, phi)
        only_K, only_phi = worth(K, phi_true), worth(K_true, phi)
        return {
            "timing_pct": (best - at_date) / best,
            "capacity_pct": 0.5 * ((at_date - only_K) + (only_phi - full)) / best,
            "allocation_pct": 0.5 * ((at_date - only_phi) + (only_K - full)) / best,
        }

    def cell(
        self,
        lambda_invest: float,
        role: str,
        leverage: float = 0.0,
        debt: str = "fair",
    ) -> dict[str, Any]:
        """Loss of the mistaken firm in the role ``"leader"`` or ``"follower"``.

        Returns:
            Dict with ``value_optimal`` (the benchmark value of that role at
            X_0), ``value_mismatch``, ``value_loss_pct``; ``leads`` (whether
            the mistaken firm ends up investing first) and, when it does,
            its entry (``X_entry``, ``K``, ``phi``, ``immediate``), the
            leader's tail objects (``distance_mismatch``,
            ``default_prob_mismatch`` against ``distance_optimal``,
            ``default_prob_optimal`` for the benchmark leader), the rival's
            gain (``rival_gain_pct``, its value against the value of the
            role it would otherwise have had), ``rival_pre_switch_entry``
            (inf when the rival waits for the switch, as the policy
            assumes) and, at zero leverage, the decomposition and
            ``rival_margin``.
        """
        if role not in ("leader", "follower"):
            msg = f"role must be 'leader' or 'follower', got {role!r}"
            raise ValueError(msg)
        pol = self.belief_policy(lambda_invest)
        game = self.game(self.lambda_true, leverage, debt)
        bench = self.benchmark(leverage, debt)
        out: dict[str, Any] = {
            "lambda_true": self.lambda_true,
            "lambda_invest": float(lambda_invest),
            "role": role,
            "leverage": leverage,
            "debt": debt if leverage > 0.0 else "none",
            "X_0": self.X_0,
            "distance_optimal": bench["distance"],
            "default_prob_optimal": bench["default_probability"],
        }
        if role == "leader":
            leads = bool(pol["leads_before_switch"])
            entry = (pol["X_entry"], pol["K"], pol["phi"])
            best, rival_best = bench["leader"], bench["follower"]
        else:
            leads = bool(pol["follower_takes_lead"])
            entry = (pol["X_lead"], pol["K_lead"], pol["phi_lead"])
            best, rival_best = bench["follower"], bench["leader"]
        out.update({"value_optimal": best, "leads": float(leads)})
        if leads:
            X_entry, K, phi = entry
            result = self._outcome(game, X_entry, K, phi)
            value = result["leader"]
            out.update({
                "X_entry": X_entry,
                "K": K,
                "phi": phi,
                "immediate": float(X_entry <= self.X_0 * (1.0 + 1e-12)),
                "distance_mismatch": result["distance"],
                "default_prob_mismatch": result["default_probability"],
                "rival_gain_pct": result["follower"] / rival_best - 1.0,
                "rival_pre_switch_entry": result["rival_pre_switch_entry"],
            })
            if leverage == 0.0:
                out.update(self._lead_decomposition(X_entry, K, phi, best))
                out["rival_margin"] = self.rival_margin(
                    X_entry, result["follower_at_entry"]
                )
        elif role == "leader":
            # Neither firm invests before the switch.
            wait = game.mutual_waiting_claim("reoptimized")
            value = float(wait(self.X_0)[0])
            out["rival_gain_pct"] = value / rival_best - 1.0
        else:
            value = self._follower_value(game, pol, bench["follower"])
            out.update({"X_pre_switch": pol["X_pre_switch"], "rival_gain_pct": 0.0})
        out.update({
            "value_mismatch": value,
            "value_loss_pct": (best - value) / best,
        })
        return out

    def _follower_value(self, game, pol: dict, benchmark: float) -> float:
        """True value at X_0 of a mistaken firm that stays the follower."""
        X_pre = pol["X_pre_switch"]
        if not isfinite(X_pre):
            return benchmark
        sub = game.subgame(self.K_L, self.phi_L)
        X_in = max(X_pre, self.X_L)
        payoff = game.follower_l_payoff(
            X_in, pol["K_pre_switch"], pol["phi_pre_switch"], sub.N_L, sub.T_L
        )
        claim = sub.follower_claim
        premium = payoff - float(claim(X_in)[0])
        at_entry = float(claim(self.X_L)[0]) + premium * (self.X_L / X_in) ** self.bp
        return self._before_entry(game, at_entry, self.X_L)


# ----------------------------------------------------------------------
# Cache
# ----------------------------------------------------------------------


def _policy_and_cells(lam: float) -> tuple[dict, list[dict]]:
    model = DuopolyMismatch(ModelParameters())
    policy = model.belief_policy(lam)
    cells = []
    for role in ("leader", "follower"):
        cells.append(model.cell(lam, role))
        for leverage in DILEMMA_LEVERAGES[1:]:
            for debt in DILEMMA_DEBTS:
                cells.append(model.cell(lam, role, leverage, debt))
    return policy, cells


def write_dilemma_grid(
    path: str | Path = DILEMMA_GRID_PATH, workers: int = 8
) -> dict[str, Any]:
    """Solve the duopoly dilemma at baseline and write the cache (a few
    minutes per belief, one process per belief)."""
    from concurrent.futures import ProcessPoolExecutor

    from .preemption_levered import encode_record

    with ProcessPoolExecutor(max_workers=workers) as pool:
        results = list(pool.map(_policy_and_cells, DILEMMA_BELIEFS))
    reference = DuopolyMismatch(ModelParameters())
    out = {
        "lambda_true": reference.lambda_true,
        "x0_ratio": reference.x0_ratio,
        "X_0": reference.X_0,
        "policies": [encode_record(policy) for policy, _ in results],
        "cells": [encode_record(c) for _, cells in results for c in cells],
    }
    with Path(path).open("w") as handle:
        json.dump(out, handle, indent=2)
        handle.write("\n")
    return out


if __name__ == "__main__":  # pragma: no cover
    grid = write_dilemma_grid()
    print(f"{len(grid['cells'])} cells written to {DILEMMA_GRID_PATH}")
