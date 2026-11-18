"""Robustness sweeps for Internet Appendix E, at the model of record (issue #182).

Two sweeps around the baseline calibration, both over the nine calibrated
parameters (r, mu_L, mu_H, sigma, lambda, alpha, gamma, delta, c):

- *One at a time*: each parameter moved by +/- 25%, eighteen draws
  (`run_sweep`).
- *Joint*: `JOINT_DRAWS` points of a scrambled Sobol sequence with a fixed
  seed in the box of +/- 25% around the baseline, all nine parameters moved
  together (`joint_scales`, `run_joint_sweep`). Nothing on this path uses an
  unseeded generator.

At each draw the single-firm objects of the model of record are re-solved
(`single_firm_objects`): the allocation phi* and the thresholds phi_underbar
and phi_tilde, the post-switch policy, the precommitted-scale (X*, K*),
whether the firm that chooses its scale at the switch invests before it (the
waiting margin), and Dario's dilemma in both single-firm versions at the
matched pairs of issue #180 (equal errors in lambda, in log lambda and in
expected years to the switch), with the draw's own arrival rate as the truth.

The duopoly objects are those of the entry game in the exact primitives at
zero leverage (`duopoly_objects`): the first investment X_L against the
precommitted-scale single-firm trigger and against the rent-equalization
trigger X_P, the leader's capacity and allocation against the single firm's,
the follower's post-switch trigger against X_L, and whether the no-deviation
checks of issue #200 hold. One solve takes minutes, so they are computed on a
subsample (`duopoly_cells`: the admissible one-at-a-time draws, the first
`DUOPOLY_JOINT_DRAWS` admissible joint draws and the cell gamma = 1.9) and
cached in ``models/robustness_duopoly.json`` (`write_duopoly_grid`, resumable,
each cell bounded in-process by `DUOPOLY_TIME_CAP`). The joint single-firm
rows are cached in ``models/robustness_joint.csv`` (`write_joint_grid`).

Admissibility. The capacity problem pits a pure-power revenue against a
linear-plus-power cost, delta K / r + c K^gamma. After the switch the scale
problem has an interior optimum if and only if (A2) holds,
1/gamma < (beta_H - 1)/(alpha beta_H) < 1: above the upper bound the linear
cost term is too weak to stop the firm shrinking toward zero scale, below
the lower bound the convex term is too weak to stop it growing without
bound. Every pre-switch object of the model of record is built on that
post-switch problem, so the window is the one (A2) implies and is not wider
(`admissibility_window`). The entry game adds alpha < 1/2 (unique capacity on
the exercise envelope). Draws outside the window, and admissible draws at
which a solver fails, are *reported* with the condition they violate, never
dropped silently.

The module also holds the pre-positioned-capability extension of Internet
Appendix E (`capability_extension`), which answers comment C2 and is not the
model of record.

Run with ``just run-sweep`` (both sweeps; CSVs to RESULTS_DIR), ``just
sweep-joint-grid`` (rewrites the joint cache, a few minutes) and ``just
sweep-duopoly-grid`` (solves the missing duopoly cells, hours); also the
Hydra pipeline task ``tasks.robustness_sweep``.
"""

import csv
import json
import logging
import signal
import sys
import time
from collections.abc import Iterable
from concurrent.futures import ProcessPoolExecutor, as_completed
from dataclasses import dataclass
from math import inf, isfinite, isnan
from pathlib import Path
from typing import Any

import numpy as np
from scipy.stats import qmc

from .exceptions import MissingEnvVarError
from .models import DuopolyModel, ModelParameters, SingleFirmModel, ValuationAnalysis
from .models.belief_mismatch import SingleFirmMismatch, matched_pairs
from .models.capability_stock import CapabilityStockModel, StockSpec
from .models.capability_stock import belief_mismatch as capability_mismatch
from .models.duopoly import cached_equilibrium
from .models.piecewise_option import solve_single_firm
from .utils.directories import get_results_directories
from .utils.files import timestamp_file

SWEEP_PARAMETERS: tuple[str, ...] = (
    "r",
    "mu_L",
    "mu_H",
    "sigma",
    "lam",
    "alpha",
    "gamma",
    "delta",
    "c",
)
"""Calibrated parameters perturbed by the sweeps (Internet Appendix C)."""

PERTURBATION = 0.25
"""Relative perturbation: each direction one at a time, the half-width of the
box in the joint sweep."""

JOINT_SEED = 182
"""Seed of the scrambled Sobol sequence of the joint sweep."""

JOINT_LOG2_DRAWS = 12
JOINT_DRAWS = 2**JOINT_LOG2_DRAWS
"""Number of joint draws (a power of two, as a Sobol sequence wants)."""

DUOPOLY_JOINT_DRAWS = 64
"""Joint draws on which the duopoly is solved: the first ones, in sequence
order, that are admissible for the entry game."""

FRAGILE_GAMMA = 1.9
"""Cost convexity of the cell flagged as fragile at the decision gate (#175)."""

DUOPOLY_TIME_CAP = 100 * 60
"""Seconds after which one duopoly solve is abandoned and reported."""

MISMATCH_SIZE = 0.8
"""Additive belief error of the dilemma pairs, as a multiple of the true rate
(0.02 and 0.18 around 0.10, the pair of `tbl-dilemma-pairs`)."""

GAP_K_FRACS: tuple[float, float] = (0.1, 0.3)
"""Installed-capacity fractions at which the scale-gap index of Internet
Appendix G is evaluated (an object of the pure-power policy)."""

ALPHA_GAME_BOUND = 0.5
"""The entry game needs alpha below this (unique envelope capacity)."""

_MODELS = Path(__file__).parent / "models"
JOINT_GRID_PATH = _MODELS / "robustness_joint.csv"
DUOPOLY_GRID_PATH = _MODELS / "robustness_duopoly.json"

DILEMMA_VERSIONS: dict[str, str] = {"pre": "precommitted", "unr": "unrestricted"}
"""Column prefix of each single-firm version of the dilemma."""

DILEMMA_PAIRS: dict[str, str] = {
    "levels": "additive",
    "log_far": "proportional_low",
    "log_near": "proportional_high",
    "horizon": "horizon",
}
"""Column suffix of each matched pair of `belief_mismatch.matched_pairs`:
equal errors in lambda, in log lambda (the pair containing the pessimistic
member and the one containing the optimistic member) and in expected years."""

SINGLE_FIRM_FIELDS: tuple[str, ...] = (
    "phi_star",
    "phi_underbar",
    "phi_tilde",
    "X_H",
    "K_H",
    "X_star",
    "K_star",
    "waiting_margin",
    "invests_before_switch",
    "X_unrestricted",
    "pure_power_trigger_pct",
    "pure_power_capacity_pct",
    "gap_fraction_low",
    "gap_fraction_high",
    *(
        f"{prefix}_{kind}_{pair}"
        for prefix in DILEMMA_VERSIONS
        for pair in DILEMMA_PAIRS
        for kind in ("loss_low", "loss_high", "ratio")
    ),
)

DUOPOLY_FIELDS: tuple[str, ...] = (
    "X_L_over_X_star",
    "X_L_over_X_P",
    "X_P_over_X_star",
    "K_L_over_K_star",
    "phi_L_over_phi_star",
    "X_F_over_X_L",
    "K_F_over_K_L",
    "lead_over_wait",
    "follower_over_leader",
    "follower_margin",
    "follower_waits_for_switch",
    "equilibrium_verified",
    "single_crossing",
    "has_rent_equalization",
)

DUOPOLY_SCAN_FIELDS: tuple[str, ...] = (
    "scan_max_gap_over_follower",
    "scan_max_lead_over_wait",
    "scan_peak_over_X_H",
    "scan_peak_over_X_star",
    "scan_peak_interior",
    "scan_peak_lead_over_wait",
    "scan_peak_follower_over_leader",
)
"""What is reported where the entry game has no rent-equalization trigger on
the demand scan of `ExactPreemptionGame.rent_equalization_reoptimized`: the
largest (L* - F) / F and L* / W on that scan, and its point at which a leader
whose rival follows would enter, relative to X_H* and to the precommitted-
scale trigger, with L* / W and F / L* there. Those scan points are 47% apart
and nothing about them is refined or checked; since issue #182 the first
investment X_L itself is located and checked in these draws too
(`preemption_levered.assigned_leader_equilibrium`), and this is kept for
comparison with it."""

SIGN_LABELS: dict[str, str] = {
    "sign_faith": "0 < phi_underbar < phi_tilde < phi*",
    "sign_monopolist_waits": (
        "the firm that chooses its scale at the switch waits for it"
    ),
    "sign_pre_levels": (
        "precommitted scale: pessimist loses more, equal errors in lambda"
    ),
    "sign_pre_log_far": (
        "precommitted scale: pessimist loses more, equal errors in log lambda (x5)"
    ),
    "sign_pre_log_near": (
        "precommitted scale: pessimist loses more, equal errors in log lambda (x1.8)"
    ),
    "sign_pre_horizon": (
        "precommitted scale: optimist loses more, equal errors in expected years"
    ),
    "sign_unr_levels": (
        "scale chosen at the switch: pessimist loses more, equal errors in lambda"
    ),
}

DUOPOLY_SIGN_LABELS: dict[str, str] = {
    "sign_entry_before_single": "X_L below the precommitted-scale trigger X*",
    "sign_entry_before_rent_eq": (
        "X_L below the rent-equalization trigger X_P (or no X_P on the scan)"
    ),
    "sign_leader_smaller": "K_L below the precommitted-scale K*",
    "sign_leader_trains_less": "phi_L below phi*",
    "sign_follower_later": "X_F* above X_L",
    "sign_second_mover": "following is worth more than leading at X_L",
    "sign_equilibrium": "the no-deviation checks of the X_L equilibrium hold",
}

QUANTILES: tuple[float, ...] = (0.0, 0.05, 0.25, 0.50, 0.75, 0.95, 1.0)


# ----------------------------------------------------------------------
# Admissibility
# ----------------------------------------------------------------------


def admissibility_failure(params: ModelParameters) -> str | None:
    """Return the failing admissibility condition, or None if admissible.

    Parameter-domain violations (Assumption 1: r > mu_H, alpha in (0, 1),
    gamma > 1, ...) are caught at construction time by ``ModelParameters``;
    the interior-capacity condition (A2), 1/gamma < (beta_H - 1)/(alpha
    beta_H) < 1, is checked here. It is the condition for the post-switch
    scale problem, on which the pre-switch objects of the model of record
    are built, so it is also the admissibility condition of the model of
    record.
    """
    model = SingleFirmModel(params)
    if not model.has_interior_trigger("H"):
        ratio = model._option_premium_ratio("H")
        bound = "upper" if ratio >= 1.0 else "lower"
        return (
            f"(A2) {bound} bound: (beta_H-1)/(alpha*beta_H) = {ratio:.3f}, "
            f"need {1.0 / params.gamma:.3f} < ratio < 1"
        )
    return None


def game_admissibility_failure(params: ModelParameters) -> str | None:
    """Admissibility for the entry game: (A2) and alpha < 1/2."""
    failure = admissibility_failure(params)
    if failure is None and params.alpha >= ALPHA_GAME_BOUND:
        return f"entry game: alpha = {params.alpha:.3f}, need alpha < 1/2"
    return failure


def _admissible_at(base: ModelParameters, param: str, value: float) -> bool:
    try:
        params = base.with_param(**{param: value})
    except ValueError:
        return False
    return admissibility_failure(params) is None


def admissibility_window(
    base: ModelParameters | None = None,
    parameters: tuple[str, ...] = SWEEP_PARAMETERS,
    span: float = 50.0,
) -> dict[str, tuple[float, float]]:
    """Interval of each parameter on which (A2) holds, others at baseline.

    Bisection outward from the baseline value, down to ``1 / span`` and up to
    ``span`` times it. A bound that is not reached is reported as 0 or inf:
    the parameter then does not enter (A2) at all (mu_L, lambda, delta, c) or
    only one side binds within the parameter domain.
    """
    base = ModelParameters() if base is None else base
    window: dict[str, tuple[float, float]] = {}
    for param in parameters:
        center = float(getattr(base, param))

        def edge(far: float, param: str = param, center: float = center) -> float:
            if _admissible_at(base, param, far):
                return 0.0 if far < center else inf
            inside, outside = center, far
            for _ in range(80):
                mid = 0.5 * (inside + outside)
                if _admissible_at(base, param, mid):
                    inside = mid
                else:
                    outside = mid
            return 0.5 * (inside + outside)

        window[param] = (edge(center / span), edge(center * span))
    return window


# ----------------------------------------------------------------------
# Objects at one parameterization
# ----------------------------------------------------------------------


def _ratio(low: float, high: float) -> float:
    if high > 0.0:
        return low / high
    return inf if low > 0.0 else float("nan")


def single_firm_objects(params: ModelParameters) -> dict[str, float]:
    """Single-firm objects of the model of record at ``params``.

    The dilemma takes ``params.lam`` as the true arrival rate and the four
    matched pairs of `belief_mismatch.matched_pairs` with an additive error
    of `MISMATCH_SIZE` times it; losses are fractions of the informed firm's
    value at half its precommitted-scale trigger, as in the paper.
    """
    solution = solve_single_firm(params)
    duopoly = DuopolyModel(params, leverage=0.0)
    error = solution.pure_power_error()
    out: dict[str, float] = {
        "phi_star": float(solution.phi_star),
        "phi_underbar": float(duopoly.faith_threshold()),
        "phi_tilde": float(duopoly.faith_threshold_exact()),
        "X_H": float(solution.X_H),
        "K_H": float(solution.K_H),
        "X_star": float(solution.precommitted.X_star),
        "K_star": float(solution.precommitted.K),
        "waiting_margin": float(solution.waiting_margin),
        "invests_before_switch": float(solution.invests_before_switch),
        "X_unrestricted": float(solution.X_star),
        "pure_power_trigger_pct": float(error["trigger_pct"]),
        "pure_power_capacity_pct": float(error["capacity_pct"]),
    }
    # Scale-gap index of Internet Appendix G, still defined at the pure-power
    # policy (in percent, at K / K^pp = GAP_K_FRACS).
    gap = ValuationAnalysis(params).capacity_gap_decomposition(np.array(GAP_K_FRACS))
    out["gap_fraction_low"], out["gap_fraction_high"] = (
        float(x) for x in gap["gap_fraction"]
    )
    lam = params.lam
    pairs = matched_pairs(lam, MISMATCH_SIZE * lam)
    shared: dict[float, Any] = {lam: solution}
    for prefix, version in DILEMMA_VERSIONS.items():
        mismatch = SingleFirmMismatch.__new__(SingleFirmMismatch)
        mismatch._solutions = shared
        _init_mismatch(mismatch, params, lam, version)
        for suffix, name in DILEMMA_PAIRS.items():
            low, high = pairs[name]
            loss_low = float(mismatch.loss(low)["value_loss_pct"])
            loss_high = float(mismatch.loss(high)["value_loss_pct"])
            out[f"{prefix}_loss_low_{suffix}"] = loss_low
            out[f"{prefix}_loss_high_{suffix}"] = loss_high
            out[f"{prefix}_ratio_{suffix}"] = _ratio(loss_low, loss_high)
    return out


def _init_mismatch(
    mismatch: SingleFirmMismatch, params: ModelParameters, lam: float, version: str
) -> None:
    """Finish constructing a `SingleFirmMismatch` whose solution cache is set.

    The two versions share every single-firm solve (the solutions do not
    depend on the version), which halves the cost of a draw.
    """
    solutions = mismatch._solutions
    SingleFirmMismatch.__init__(mismatch, params, lam, version)
    solutions.update(mismatch._solutions)
    mismatch._solutions = solutions


def single_firm_signs(objects: dict[str, float]) -> dict[str, bool]:
    """Qualitative statements of the paper evaluated at one draw.

    Each is True when the statement holds as it does at baseline, so a False
    is a sign reversal. The horizon statement is the reversed ranking the
    paper reports at baseline (the optimist loses slightly more).
    """
    o = objects
    return {
        "sign_faith": 0.0 < o["phi_underbar"] < o["phi_tilde"] < o["phi_star"],
        "sign_monopolist_waits": o["invests_before_switch"] == 0.0,
        "sign_pre_levels": o["pre_loss_low_levels"] > o["pre_loss_high_levels"],
        "sign_pre_log_far": o["pre_loss_low_log_far"] > o["pre_loss_high_log_far"],
        "sign_pre_log_near": o["pre_loss_low_log_near"] > o["pre_loss_high_log_near"],
        "sign_pre_horizon": o["pre_loss_low_horizon"] < o["pre_loss_high_horizon"],
        "sign_unr_levels": o["unr_loss_low_levels"] > o["unr_loss_high_levels"],
    }


def duopoly_objects(
    record: dict[str, Any], single: dict[str, float]
) -> dict[str, float]:
    """Duopoly objects of the sweep from one equilibrium record.

    ``record`` is a record of `preemption_levered.equilibrium_record` at
    zero leverage and ``single`` the `single_firm_objects` at the same
    parameters. Ratios are unit-free, so the homogeneity of the model in
    delta and c leaves them unchanged.
    """
    X_L, X_P = float(record["X_L"]), float(record["X_P"])
    has_X_P = bool(record["exists"])
    nan = float("nan")
    return {
        "X_L_over_X_star": X_L / single["X_star"],
        "X_L_over_X_P": X_L / X_P if has_X_P else nan,
        "X_P_over_X_star": X_P / single["X_star"] if has_X_P else nan,
        "K_L_over_K_star": float(record["K_L"]) / single["K_star"],
        "phi_L_over_phi_star": float(record["phi_L"]) / single["phi_star"],
        "X_F_over_X_L": float(record["X_F"]) / X_L,
        "K_F_over_K_L": float(record["K_F"]) / float(record["K_L"]),
        "lead_over_wait": float(record["lead_over_wait"]),
        "follower_over_leader": float(record["follower_over_leader"]),
        "follower_margin": float(record["follower_margin"]),
        "follower_waits_for_switch": float(
            not isfinite(float(record["X_F_pre_switch"]))
        ),
        "equilibrium_verified": float(record["equilibrium"]),
        "single_crossing": float(record["n_sign_changes"] == 1.0),
        "has_rent_equalization": float(has_X_P),
    }


def duopoly_signs(objects: dict[str, float]) -> dict[str, bool]:
    """Qualitative statements about the entry equilibrium at one draw."""
    o = objects
    return {
        "sign_entry_before_single": o["X_L_over_X_star"] < 1.0,
        # Without X_P on the scan, following beats leading at every scanned
        # demand, so the first investment is below any crossing there.
        "sign_entry_before_rent_eq": not o["X_L_over_X_P"] >= 1.0,
        "sign_leader_smaller": o["K_L_over_K_star"] < 1.0,
        "sign_leader_trains_less": o["phi_L_over_phi_star"] < 1.0,
        "sign_follower_later": o["X_F_over_X_L"] > 1.0,
        "sign_second_mover": o["follower_over_leader"] > 1.0,
        "sign_equilibrium": o["equilibrium_verified"] == 1.0,
    }


# ----------------------------------------------------------------------
# Local elasticities (Internet Appendix D)
# ----------------------------------------------------------------------

ELASTICITY_PARAMETERS: tuple[str, ...] = (
    "r",
    "alpha",
    "mu_H",
    "sigma",
    "gamma",
    "delta",
    "lam",
)
"""Rows of `tbl-elasticities`, in the order of the table."""

ELASTICITY_STEP = 1e-3
"""Relative step of the central differences."""


def policy_elasticities(
    params: ModelParameters | None = None,
    parameters: tuple[str, ...] = ELASTICITY_PARAMETERS,
    step: float = ELASTICITY_STEP,
) -> list[dict[str, float]]:
    """Elasticities of the single firm's policy to each parameter.

    Central differences in logs, d ln y / d ln theta, of the
    precommitted-scale trigger and capacity of the model of record
    (``X_star``, ``K_star``), of the post-switch policy (``X_H``, ``K_H``,
    which is also the capacity of the pure-power approximation) and of the
    training fraction (``phi_star``).
    """
    params = ModelParameters() if params is None else params

    def policy(p: ModelParameters) -> dict[str, float]:
        solution = solve_single_firm(p)
        return {
            "X_star": solution.precommitted.X_star,
            "K_star": solution.precommitted.K,
            "X_H": solution.X_H,
            "K_H": solution.K_H,
            "phi_star": solution.phi_star,
        }

    rows = []
    for name in parameters:
        value = float(getattr(params, name))
        up = policy(params.with_param(**{name: value * (1.0 + step)}))
        down = policy(params.with_param(**{name: value * (1.0 - step)}))
        width = np.log((1.0 + step) / (1.0 - step))
        rows.append(
            {"param": name, "value": value}
            | {key: float(np.log(up[key] / down[key]) / width) for key in up}
        )
    return rows


# ----------------------------------------------------------------------
# Draws
# ----------------------------------------------------------------------


def joint_scales(
    log2_draws: int = JOINT_LOG2_DRAWS,
    seed: int = JOINT_SEED,
    perturbation: float = PERTURBATION,
    dimension: int = len(SWEEP_PARAMETERS),
) -> np.ndarray:
    """Multiplicative factors of the joint draws, shape (2^log2_draws, d).

    A scrambled Sobol sequence with a fixed seed, mapped to
    [1 - perturbation, 1 + perturbation] in each coordinate. The first rows
    of a longer sequence are the rows of a shorter one, so a prefix can be
    recomputed on its own.
    """
    sampler = qmc.Sobol(d=dimension, scramble=True, seed=seed)
    unit = sampler.random_base2(log2_draws)
    return 1.0 - perturbation + 2.0 * perturbation * unit


def _draw_values(
    base: ModelParameters, scales: Iterable[float], parameters: tuple[str, ...]
) -> dict[str, float]:
    return {
        name: float(getattr(base, name) * scale)
        for name, scale in zip(parameters, scales, strict=True)
    }


def evaluate_values(base: ModelParameters, values: dict[str, float]) -> dict[str, Any]:
    """Single-firm objects and signs at ``base`` with ``values`` replaced.

    Returns a row with ``admissible`` and ``failure``; a draw outside
    Assumption 1 or (A2), or at which a solver fails, carries the reason and
    no objects.
    """
    row: dict[str, Any] = dict(values)
    try:
        params = base.with_param(**values)
    except ValueError as exc:
        return row | {"admissible": False, "failure": f"(A1) parameter domain: {exc}"}
    failure = admissibility_failure(params)
    if failure is not None:
        return row | {"admissible": False, "failure": failure}
    try:
        objects = single_firm_objects(params)
    except (ValueError, RuntimeError, ArithmeticError) as exc:
        return row | {"admissible": False, "failure": f"solver failure: {exc}"}
    signs = single_firm_signs(objects)
    return row | {"admissible": True, "failure": None} | objects | signs


def _attach_duopoly(row: dict[str, Any], cell: dict[str, Any] | None) -> None:
    """Add the cached duopoly objects of ``cell`` to an admissible row.

    A solver failure is recorded under ``duopoly_failure``; a solve in which
    no firm invests before the switch on the scan under ``duopoly_no_entry``
    (with ``duopoly_waiting_equilibrium``); otherwise the objects at X_L and
    their signs are added. Where the game has no rent-equalization trigger
    on its scan the `DUOPOLY_SCAN_FIELDS` are added as well.
    """
    if cell is None or not row["admissible"]:
        return
    if cell.get("failure"):
        row["duopoly_failure"] = cell["failure"]
        return
    record = cell["record"]
    if "scan_peak" in record:
        row.update({
            "scan_max_gap_over_follower": float(record["max_gap_over_follower"]),
            "scan_max_lead_over_wait": float(record["max_lead_over_wait"]),
            "scan_peak_over_X_H": float(record["scan_peak"]) / row["X_H"],
            "scan_peak_over_X_star": float(record["scan_peak"]) / row["X_star"],
            "scan_peak_interior": float(record["scan_peak_interior"]),
            "scan_peak_lead_over_wait": float(record["scan_peak_lead_over_wait"]),
            "scan_peak_follower_over_leader": float(
                record["scan_peak_follower_over_leader"]
            ),
        })
    if not record.get("first_investment", 1.0):
        row["duopoly_no_entry"] = True
        row["duopoly_waiting_equilibrium"] = float(record["waiting_equilibrium"])
        row["duopoly_entry_max_lead_over_wait"] = float(
            record["entry_max_lead_over_wait"]
        )
        return
    objects = duopoly_objects(record, row)
    row.update(objects)
    row.update(duopoly_signs(objects))


def evaluate_draw(
    base: ModelParameters,
    param: str,
    direction: str,
    perturbation: float = PERTURBATION,
    duopoly: dict[str, dict[str, Any]] | None = None,
) -> dict[str, Any]:
    """Evaluate one one-at-a-time draw.

    Args:
        base: Baseline calibration.
        param: Name of the parameter to perturb.
        direction: ``"-"``, ``"+"``, or ``"0"`` (baseline, no perturbation).
        perturbation: Relative size of the perturbation.
        duopoly: Cached duopoly cells by name (`load_duopoly_grid`); the
            duopoly objects are attached when the draw's cell is there.
    """
    scale = {"-": 1.0 - perturbation, "+": 1.0 + perturbation, "0": 1.0}[direction]
    value = float(getattr(base, param) * scale)
    row = evaluate_values(base, {param: value})
    row = {
        "param": "baseline" if direction == "0" else param,
        "direction": direction,
        "value": value,
    } | {k: v for k, v in row.items() if k != param}
    if duopoly is not None:
        name = "baseline" if direction == "0" else f"oat:{param}{direction}"
        _attach_duopoly(row, duopoly.get(name))
    return row


def run_sweep(
    base: ModelParameters | None = None,
    parameters: tuple[str, ...] = SWEEP_PARAMETERS,
    perturbation: float = PERTURBATION,
    duopoly: dict[str, dict[str, Any]] | None = None,
) -> list[dict[str, Any]]:
    """Run the one-at-a-time sweep of +/- ``perturbation`` over ``parameters``.

    The first row is the unperturbed baseline; the remaining rows are the
    two perturbations of each parameter, in the order given.
    """
    base = ModelParameters() if base is None else base
    rows = [evaluate_draw(base, parameters[0], "0", perturbation, duopoly)]
    for param in parameters:
        for direction in ("-", "+"):
            rows.append(evaluate_draw(base, param, direction, perturbation, duopoly))
    return rows


def _evaluate_joint(args: tuple[int, tuple[float, ...]]) -> dict[str, Any]:
    index, scales = args
    base = ModelParameters()
    row = evaluate_values(base, _draw_values(base, scales, SWEEP_PARAMETERS))
    return {"draw": index} | row


def run_joint_sweep(
    n_draws: int | None = None,
    workers: int = 8,
    duopoly: dict[str, dict[str, Any]] | None = None,
) -> list[dict[str, Any]]:
    """Run the joint sweep on the first ``n_draws`` draws of the sequence.

    The work is bounded by the number of draws (each takes a fraction of a
    second); ``workers`` processes share it, or none when ``workers`` is 1.
    """
    scales = joint_scales()
    if n_draws is not None:
        scales = scales[:n_draws]
    tasks = [(i, tuple(float(s) for s in row)) for i, row in enumerate(scales)]
    if workers <= 1:
        rows = [_evaluate_joint(task) for task in tasks]
    else:
        with ProcessPoolExecutor(max_workers=workers) as pool:
            rows = list(pool.map(_evaluate_joint, tasks, chunksize=32))
    if duopoly is not None:
        for row in rows:
            _attach_duopoly(row, duopoly.get(f"joint:{row['draw']}"))
    return rows


# ----------------------------------------------------------------------
# Summaries
# ----------------------------------------------------------------------


def _finite(rows: list[dict[str, Any]], name: str) -> np.ndarray:
    values = [
        float(row[name])
        for row in rows
        if row.get(name) is not None and not isinstance(row[name], str)
    ]
    array = np.array(values, dtype=float)
    return array[np.isfinite(array)]


def _failure_kind(failure: str) -> str:
    for kind in ("(A1)", "(A2) upper", "(A2) lower", "solver failure"):
        if failure.startswith(kind):
            return kind
    return "other"


@dataclass
class SweepSummary:
    """Aggregate of a sweep.

    Attributes:
        n_draws: Draws other than the baseline row.
        n_admissible, n_failed: Split of those draws: solved, and not (outside
            the window or, inside it, a solver failure).
        failures: (label, reason) of each failed draw.
        failure_counts: Failed draws by kind ((A1), (A2) upper, (A2) lower,
            solver failure).
        sign_counts: For each statement of `SIGN_LABELS`, the number of
            admissible draws at which it holds.
        sign_violations: Labels of the admissible draws at which it fails.
        quantiles: `QUANTILES` of each value field over the admissible draws
            at which it is finite, with the count of those draws under
            ``"n"``.
        n_duopoly, n_duopoly_failed: Admissible draws with a duopoly solve,
            and those among them at which the solve failed.
        duopoly_failures: (label, reason) of those.
        n_duopoly_no_entry: Solved draws at which no firm invests before the
            switch on the scan (L* <= W at every scanned demand).
        n_waiting_equilibrium: Those of them at which mutual waiting is an
            equilibrium on the scan (the post-switch game is a race).
        duopoly_sign_counts, duopoly_sign_violations, duopoly_quantiles: The
            same aggregates over the draws with a first investment before
            the switch (`n_first_investment`).
        n_no_rent_equalization: Solved draws at which the game has no
            rent-equalization trigger on the demand scan (with or without a
            first investment).
        scan_quantiles: Quantiles of `DUOPOLY_SCAN_FIELDS` over those draws.
    """

    n_draws: int
    n_admissible: int
    n_failed: int
    failures: list[tuple[str, str]]
    failure_counts: dict[str, int]
    sign_counts: dict[str, int]
    sign_violations: dict[str, list[str]]
    quantiles: dict[str, dict[str, float]]
    n_duopoly: int
    n_duopoly_failed: int
    duopoly_failures: list[tuple[str, str]]
    n_duopoly_no_entry: int
    n_waiting_equilibrium: int
    duopoly_sign_counts: dict[str, int]
    duopoly_sign_violations: dict[str, list[str]]
    duopoly_quantiles: dict[str, dict[str, float]]
    n_no_rent_equalization: int
    scan_quantiles: dict[str, dict[str, float]]

    @property
    def n_first_investment(self) -> int:
        """Draws with a duopoly solve and a first investment before the switch."""
        return self.n_duopoly - self.n_duopoly_failed - self.n_duopoly_no_entry

    @property
    def n_solver_failures(self) -> int:
        """Draws inside the window at which a solver failed."""
        return self.failure_counts.get("solver failure", 0)

    @property
    def n_outside_window(self) -> int:
        """Draws that violate Assumption 1 or (A2)."""
        return self.n_failed - self.n_solver_failures

    @property
    def inadmissible_share(self) -> float:
        """Share of the draws outside the window."""
        return self.n_outside_window / self.n_draws if self.n_draws else float("nan")

    @property
    def sign_survival(self) -> dict[str, bool]:
        return {
            name: count == self.n_admissible for name, count in self.sign_counts.items()
        }

    def range(self, name: str) -> tuple[float, float]:
        """Smallest and largest finite value of a field."""
        table = self.quantiles.get(name) or self.duopoly_quantiles[name]
        return table["q0"], table["q100"]


def _label(row: dict[str, Any]) -> str:
    if "draw" in row:
        return f"draw {row['draw']}"
    return f"{row['param']}{row['direction']}"


def _quantile_table(
    rows: list[dict[str, Any]], names: tuple[str, ...]
) -> dict[str, dict[str, float]]:
    table: dict[str, dict[str, float]] = {}
    for name in names:
        values = _finite(rows, name)
        if values.size == 0:
            continue
        table[name] = {"n": float(values.size)} | {
            f"q{round(100 * q)}": float(np.quantile(values, q)) for q in QUANTILES
        }
    return table


def summarize_sweep(rows: list[dict[str, Any]]) -> SweepSummary:
    """Aggregate a sweep (one at a time or joint)."""
    draws = [row for row in rows if row.get("param") != "baseline"]
    admissible = [row for row in draws if row["admissible"]]
    failed = [row for row in draws if not row["admissible"]]
    counts: dict[str, int] = {}
    for row in failed:
        kind = _failure_kind(row["failure"])
        counts[kind] = counts.get(kind, 0) + 1
    solved = [row for row in admissible if "X_L_over_X_star" in row]
    unsolved = [row for row in admissible if row.get("duopoly_failure")]
    no_entry = [row for row in admissible if row.get("duopoly_no_entry")]
    return SweepSummary(
        n_draws=len(draws),
        n_admissible=len(admissible),
        n_failed=len(failed),
        failures=[(_label(row), row["failure"]) for row in failed],
        failure_counts=counts,
        sign_counts={
            name: sum(bool(row[name]) for row in admissible) for name in SIGN_LABELS
        },
        sign_violations={
            name: [_label(row) for row in admissible if not row[name]]
            for name in SIGN_LABELS
        },
        quantiles=_quantile_table(admissible, SINGLE_FIRM_FIELDS),
        n_duopoly=len(solved) + len(no_entry) + len(unsolved),
        n_duopoly_failed=len(unsolved),
        duopoly_failures=[(_label(row), row["duopoly_failure"]) for row in unsolved],
        n_duopoly_no_entry=len(no_entry),
        n_waiting_equilibrium=sum(
            row["duopoly_waiting_equilibrium"] == 1.0 for row in no_entry
        ),
        duopoly_sign_counts={
            name: sum(bool(row[name]) for row in solved) for name in DUOPOLY_SIGN_LABELS
        },
        duopoly_sign_violations={
            name: [_label(row) for row in solved if not row[name]]
            for name in DUOPOLY_SIGN_LABELS
        },
        duopoly_quantiles=_quantile_table(solved, DUOPOLY_FIELDS),
        n_no_rent_equalization=sum("scan_peak_over_X_H" in row for row in admissible),
        scan_quantiles=_quantile_table(
            [row for row in admissible if "scan_peak_over_X_H" in row],
            DUOPOLY_SCAN_FIELDS,
        ),
    )


# ----------------------------------------------------------------------
# Caches
# ----------------------------------------------------------------------


def _cell_text(value: Any, digits: int = 9) -> str:
    if value is None:
        return ""
    if isinstance(value, float | np.floating):
        value = float(value)
        return f"{value:.{digits}g}" if isfinite(value) else repr(value)
    return str(value)


def write_joint_grid(path: Path = JOINT_GRID_PATH, workers: int = 8) -> list[dict]:
    """Run the joint single-firm sweep and write its cache.

    One CSV row per draw, in draw order: the parameters, the reason when
    the draw is outside the window or a solver fails, and otherwise the
    objects of `SINGLE_FIRM_FIELDS` to nine significant digits (the sign
    statements are recomputed on loading). The seed, the number of draws
    and the box are the module constants; the tests check the file against
    them.
    """
    rows = run_joint_sweep(workers=workers)
    columns = ["draw", *SWEEP_PARAMETERS, "failure", *SINGLE_FIRM_FIELDS]
    with path.open("w", newline="") as handle:
        writer = csv.writer(handle, lineterminator="\n")
        writer.writerow(columns)
        for row in rows:
            writer.writerow([_cell_text(row.get(column)) for column in columns])
    return rows


def load_joint_grid(
    duopoly: dict[str, dict[str, Any]] | None = None,
) -> list[dict[str, Any]]:
    """Cached rows of the joint single-firm sweep (`write_joint_grid`).

    In draw order, in the layout of `run_joint_sweep`. Pass the cached
    duopoly cells to attach the duopoly objects of the subsample.
    """
    rows = []
    with JOINT_GRID_PATH.open(newline="") as handle:
        for record in csv.DictReader(handle):
            row: dict[str, Any] = {"draw": int(record["draw"])}
            row |= {name: float(record[name]) for name in SWEEP_PARAMETERS}
            if record["failure"]:
                rows.append(row | {"admissible": False, "failure": record["failure"]})
                continue
            row |= {"admissible": True, "failure": None}
            row |= {name: float(record[name]) for name in SINGLE_FIRM_FIELDS}
            rows.append(row | single_firm_signs(row))
    if duopoly is not None:
        for row in rows:
            _attach_duopoly(row, duopoly.get(f"joint:{row['draw']}"))
    return rows


def duopoly_cells(base: ModelParameters | None = None) -> list[dict[str, Any]]:
    """Parameterizations at which the entry game is solved for the sweeps.

    The one-at-a-time draws admissible for the game, the cell gamma =
    `FRAGILE_GAMMA`, and the first `DUOPOLY_JOINT_DRAWS` joint draws
    admissible for the game. Each is {"cell": name, "values": {...}}. The
    baseline is not listed: it is read from ``duopoly_equilibria.json``.
    """
    base = ModelParameters() if base is None else base

    def admissible(values: dict[str, float]) -> bool:
        try:
            params = base.with_param(**values)
        except ValueError:
            return False
        return game_admissibility_failure(params) is None

    cells = []
    for param in SWEEP_PARAMETERS:
        for direction, scale in (("-", 1.0 - PERTURBATION), ("+", 1.0 + PERTURBATION)):
            values = {param: float(getattr(base, param) * scale)}
            if admissible(values):
                cells.append({"cell": f"oat:{param}{direction}", "values": values})
    cells.append({"cell": "fragile", "values": {"gamma": FRAGILE_GAMMA}})
    joint = 0
    for index, scales in enumerate(joint_scales()):
        if joint == DUOPOLY_JOINT_DRAWS:
            break
        values = _draw_values(base, scales, SWEEP_PARAMETERS)
        if admissible(values):
            cells.append({"cell": f"joint:{index}", "values": values})
            joint += 1
    return cells


class _TimeCapError(BaseException):
    """Raised by the alarm; not an Exception, so that the solvers' own
    handlers (which catch RuntimeError to truncate a scan) cannot swallow it."""


def _raise_time_cap(signum, frame):  # pragma: no cover - signal handler
    raise _TimeCapError


def _solve_duopoly_cell(cell: dict[str, Any]) -> dict[str, Any]:  # pragma: no cover
    """Solve one cell of `duopoly_cells`, bounded by `DUOPOLY_TIME_CAP`."""
    from .models.preemption_levered import encode_record, equilibrium_record

    start = time.time()
    out = {key: cell[key] for key in ("cell", "values", "contest") if key in cell}
    signal.signal(signal.SIGALRM, _raise_time_cap)
    signal.alarm(DUOPOLY_TIME_CAP)
    try:
        params = ModelParameters().with_param(**cell["values"])
        contest = cell.get("contest", "tullock")
        out["record"] = encode_record(equilibrium_record(params, contest=contest))
    except _TimeCapError:
        out["failure"] = f"time cap of {DUOPOLY_TIME_CAP // 60} minutes reached"
    except (ValueError, RuntimeError, ArithmeticError, KeyError) as exc:
        out["failure"] = f"solver failure: {type(exc).__name__}: {exc}"
    finally:
        signal.alarm(0)
    out["seconds"] = round(time.time() - start, 1)
    return out


def _read_duopoly_file(path: Path) -> dict[str, dict[str, Any]]:
    if not path.exists():
        return {}
    with path.open() as handle:
        return {cell["cell"]: cell for cell in json.load(handle)}


def write_duopoly_grid(  # pragma: no cover - hours of solves
    path: Path = DUOPOLY_GRID_PATH,
    workers: int = 8,
    fresh: bool = False,
    retry: bool = False,
) -> dict[str, dict[str, Any]]:
    """Solve the cells of `duopoly_cells` missing from the cache.

    Resumable: the file is rewritten after each cell, in the order of
    `duopoly_cells`, and a cell already in it is kept unless ``fresh``; with
    ``retry`` the cells recorded as failed are solved again, except those
    that reached the time cap.
    """
    cells = duopoly_cells()
    done = {} if fresh else _read_duopoly_file(path)
    if retry:
        done = {
            name: cell
            for name, cell in done.items()
            if not cell.get("failure") or cell["failure"].startswith("time cap")
        }
    order = [cell["cell"] for cell in cells]
    done = {name: cell for name, cell in done.items() if name in order}
    todo = [cell for cell in cells if cell["cell"] not in done]

    def dump() -> None:
        with path.open("w") as handle:
            json.dump([done[name] for name in order if name in done], handle, indent=2)
            handle.write("\n")

    with ProcessPoolExecutor(max_workers=workers) as pool:
        futures = [pool.submit(_solve_duopoly_cell, cell) for cell in todo]
        for future in as_completed(futures):
            result = future.result()
            done[result["cell"]] = result
            dump()
            logging.info(
                "%s: %s (%.0f s)",
                result["cell"],
                result.get("failure", "solved"),
                result["seconds"],
            )
    dump()
    return done


def load_duopoly_grid() -> dict[str, dict[str, Any]]:
    """Cached duopoly cells of the sweeps by name, records decoded.

    Adds the baseline from ``duopoly_equilibria.json`` under ``"baseline"``.
    """
    from .models.preemption_levered import decode_record

    cells = _read_duopoly_file(DUOPOLY_GRID_PATH)
    for cell in cells.values():
        if "record" in cell:
            cell["record"] = decode_record(cell["record"])
    cells["baseline"] = {
        "cell": "baseline",
        "values": {},
        "record": cached_equilibrium(ModelParameters().lam),
    }
    return cells


# ----------------------------------------------------------------------
# Pre-positioned capability (Internet Appendix E; comment C2)
# ----------------------------------------------------------------------

KAPPA_GRID: tuple[float, ...] = (0.05, 0.10, 0.20, 0.30, 0.50, 0.75, 1.0)
"""Late-training effectiveness on which the extension is reported."""

CAPABILITY_BELIEFS: tuple[float, ...] = (0.2, 1.8, 5.0)
"""Beliefs of the extension's dilemma, as multiples of the true rate."""


def capability_corner(params: ModelParameters) -> float:
    """Late-training effectiveness above which nothing is trained early.

    Under pre-positioned capability the pre-switch training fraction is
    interior if and only if kappa^(1 - alpha) < lam A_H (1 - kappa); this is
    the root of that condition.
    """
    from scipy import optimize

    p = params
    return float(
        optimize.brentq(
            lambda k: k ** (1.0 - p.alpha) - p.lam * p.A_H * (1.0 - k),
            1e-12,
            1.0,
            xtol=1e-14,
        )
    )


def _capability_row(
    params: ModelParameters, spec: StockSpec, label: float, X_0: float, scale: float
) -> dict[str, float]:
    model = CapabilityStockModel(params, spec)
    policy = model.policy
    interior = policy.status == "interior"
    row = {
        "kappa": label,
        "invests_before_switch": float(interior),
        "X_star": float(policy.X_star) if interior else inf,
        "K_star": float(policy.K_star) if interior else float("nan"),
        "X_star_over_late_trigger": (
            float(policy.X_star / model.late_trigger) if interior else inf
        ),
        "phi_star": float(policy.phi_star),
        "phi_underbar": float(model.faith_threshold()),
        "phi_tilde": float(model.faith_threshold(exact=True)),
        "value_over_record": float(model.value(X_0)) / scale,
    }
    if interior:
        beliefs = tuple(m * params.lam for m in CAPABILITY_BELIEFS)
        losses = capability_mismatch(params, spec, params.lam, beliefs)["loss_pct"]
        row.update({
            "loss_low": losses[0] / 100.0,
            "loss_high": losses[1] / 100.0,
            "loss_far_high": losses[2] / 100.0,
            "ratio_levels": _ratio(losses[0], losses[1]),
            "ratio_log_far": _ratio(losses[0], losses[2]),
        })
    return row


def capability_extension(
    params: ModelParameters | None = None,
    kappas: tuple[float, ...] = KAPPA_GRID,
    x0_ratio: float = 0.5,
) -> list[dict[str, float]]:
    """The single firm under pre-positioned capability, by kappa.

    An extension, not the model of record. Training capacity in place when
    the switch arrives counts in full in the post-switch market; capability
    built afterwards counts at the rate kappa, for a firm that enters after
    the switch and for the inference capacity an installed firm redeploys to
    training (`capability_stock.StockSpec.pre_positioned`). kappa = 0 is the
    strict stock and kappa = 1 the flow economy with free redeployment. The
    model of record is not a member of the family (its entrant has kappa =
    1 and its incumbent cannot redeploy); it is the first row, with kappa
    reported as nan.

    Each row reports whether the firm that chooses its scale whenever it
    invests has a finite pre-switch trigger, the trigger and capacity, the
    trigger relative to that of a firm entering after the switch, the
    training fraction and the faith thresholds, the firm's value at a common
    reference demand (``x0_ratio`` times the precommitted-scale trigger of
    the model of record) relative to the model of record's, and the dilemma
    losses of `capability_stock.belief_mismatch` at beliefs
    `CAPABILITY_BELIEFS` times the true rate, measured at half the firm's
    own trigger.
    """
    params = ModelParameters() if params is None else params
    record = solve_single_firm(params)
    X_0 = x0_ratio * record.precommitted.X_star
    scale = float(record.value(X_0))
    rows = [_capability_row(params, StockSpec(), float("nan"), X_0, scale)]
    rows.extend(
        _capability_row(params, StockSpec.pre_positioned(kappa), kappa, X_0, scale)
        for kappa in kappas
    )
    return rows


# ----------------------------------------------------------------------
# Reports and CSV output
# ----------------------------------------------------------------------


def _format_value(value: Any) -> str:
    if value is None:
        return "--"
    if isinstance(value, bool | np.bool_):
        return "yes" if value else "NO"
    if isinstance(value, float | np.floating):
        if isnan(value):
            return "nan"
        return f"{value:.4g}"
    return str(value)


_TABLE_COLUMNS: tuple[tuple[str, str], ...] = (
    ("param", "param"),
    ("direction", "dir"),
    ("value", "value"),
    ("admissible", "adm"),
    ("phi_star", "phi*"),
    ("phi_underbar", "phi_lo"),
    ("phi_tilde", "phi_ti"),
    ("X_star", "X*"),
    ("K_star", "K*"),
    ("waiting_margin", "wait"),
    ("pre_ratio_levels", "lev"),
    ("pre_ratio_log_far", "log5"),
    ("pre_ratio_log_near", "log1.8"),
    ("pre_ratio_horizon", "years"),
    ("X_L_over_X_star", "XL/X*"),
    ("X_L_over_X_P", "XL/XP"),
    ("K_L_over_K_star", "KL/K*"),
    ("phi_L_over_phi_star", "phiL/phi*"),
    ("X_F_over_X_L", "XF/XL"),
    ("equilibrium_verified", "eq"),
)


def format_sweep_table(rows: list[dict[str, Any]]) -> str:
    """Render the one-at-a-time sweep as a fixed-width text table."""
    header = [label for _, label in _TABLE_COLUMNS]
    body = [
        [_format_value(row.get(name)) for name, _ in _TABLE_COLUMNS] for row in rows
    ]
    widths = [
        max(len(header[i]), *(len(line[i]) for line in body))
        for i in range(len(_TABLE_COLUMNS))
    ]
    sep = "  "
    lines = [sep.join(h.ljust(w) for h, w in zip(header, widths, strict=True))]
    lines.append(sep.join("-" * w for w in widths))
    lines.extend(
        sep.join(cell.ljust(w) for cell, w in zip(line, widths, strict=True))
        for line in body
    )
    return "\n".join(lines)


def _format_summary(summary: SweepSummary, list_failures: bool) -> list[str]:
    parts = [
        f"Solved: {summary.n_admissible} / {summary.n_draws}; outside the "
        f"window: {summary.n_outside_window} ({summary.inadmissible_share:.1%}); "
        f"inside it with a solver failure: {summary.n_solver_failures}",
    ]
    parts.extend(
        f"  {kind}: {count}" for kind, count in sorted(summary.failure_counts.items())
    )
    if list_failures and summary.failures:
        parts.append("Inadmissible draws (reported, not dropped):")
        parts.extend(f"  {label}: {reason}" for label, reason in summary.failures)
    parts.append("")
    parts.append("Qualitative statements across admissible draws:")
    for name, label in SIGN_LABELS.items():
        count = summary.sign_counts[name]
        line = f"  {label}: {count} / {summary.n_admissible}"
        offenders = summary.sign_violations[name]
        if offenders and len(offenders) <= 12:
            line += " (fails at " + ", ".join(offenders) + ")"
        parts.append(line)
    parts.append("")
    parts.append("Quantiles across admissible draws (n, min, 5, 25, 50, 75, 95, max):")
    parts.extend(_format_quantiles(summary.quantiles))
    solved = summary.n_first_investment
    parts.append("")
    parts.append(
        f"Duopoly subsample: {summary.n_duopoly} draws, {solved} with a first "
        f"investment before the switch, {summary.n_duopoly_no_entry} without "
        f"({summary.n_waiting_equilibrium} with mutual waiting an equilibrium "
        f"on the scan), {summary.n_duopoly_failed} failed"
    )
    parts.extend(f"  {label}: {reason}" for label, reason in summary.duopoly_failures)
    for name, label in DUOPOLY_SIGN_LABELS.items():
        line = f"  {label}: {summary.duopoly_sign_counts[name]} / {solved}"
        offenders = summary.duopoly_sign_violations[name]
        if offenders and len(offenders) <= 12:
            line += " (fails at " + ", ".join(offenders) + ")"
        parts.append(line)
    parts.extend(_format_quantiles(summary.duopoly_quantiles))
    if summary.n_no_rent_equalization:
        parts.append(
            f"No rent-equalization trigger on the scan: "
            f"{summary.n_no_rent_equalization} draws (points of the X_P scan)"
        )
        parts.extend(_format_quantiles(summary.scan_quantiles))
    return parts


def _format_quantiles(table: dict[str, dict[str, float]]) -> list[str]:
    return [
        f"  {name}: n={stats['n']:.0f}  "
        + "  ".join(f"{stats[f'q{round(100 * q)}']:.4g}" for q in QUANTILES)
        for name, stats in table.items()
    ]


def format_sweep_report(rows: list[dict[str, Any]]) -> str:
    """Render the one-at-a-time table, failure log and summary."""
    summary = summarize_sweep(rows)
    parts = [
        f"One-at-a-time sweep (+/-{PERTURBATION:.0%}, {summary.n_draws} perturbations)",
        "",
        format_sweep_table(rows),
        "",
        *_format_summary(summary, list_failures=True),
    ]
    return "\n".join(parts)


def format_joint_report(rows: list[dict[str, Any]]) -> str:
    """Render the summary of the joint sweep."""
    summary = summarize_sweep(rows)
    parts = [
        f"Joint sweep ({summary.n_draws} Sobol draws, seed {JOINT_SEED}, "
        f"box of +/-{PERTURBATION:.0%} around the baseline)",
        "",
        *_format_summary(summary, list_failures=False),
    ]
    return "\n".join(parts)


def format_window_report(window: dict[str, tuple[float, float]]) -> str:
    """Render the (A2) window of each parameter."""
    lines = ["Interval of each parameter on which (A2) holds, others at baseline:"]
    for name, (low, high) in window.items():
        if low == 0.0 and high == inf:
            lines.append(f"  {name}: does not bind")
        else:
            lines.append(f"  {name}: ({low:.4g}, {high:.4g})")
    return "\n".join(lines)


def format_capability_report(rows: list[dict[str, float]]) -> str:
    """Render the pre-positioned-capability extension."""
    columns = (
        "kappa",
        "invests_before_switch",
        "X_star",
        "K_star",
        "X_star_over_late_trigger",
        "phi_star",
        "phi_underbar",
        "phi_tilde",
        "value_over_record",
        "loss_low",
        "loss_high",
        "loss_far_high",
    )
    lines = [
        "Pre-positioned capability (extension, not the model of record; "
        "first row: model of record):",
        "  " + "  ".join(columns),
    ]
    lines.extend(
        "  " + "  ".join(_format_value(row.get(name)) for name in columns)
        for row in rows
    )
    return "\n".join(lines)


def write_sweep_csv(
    rows: list[dict[str, Any]], directory: Path, name: str = "robustness_sweep"
) -> Path:
    """Write a sweep to a timestamped CSV in ``directory``."""
    directory.mkdir(parents=True, exist_ok=True)
    path = timestamp_file(directory / f"{name}.csv")
    field_names: list[str] = []
    for row in rows:
        field_names.extend(key for key in row if key not in field_names)
    with path.open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=field_names)
        writer.writeheader()
        writer.writerows(rows)
    return path


def run_all(workers: int = 8, recompute_joint: bool = True) -> dict[str, Any]:
    """Run both sweeps and the extension; return rows and the text report.

    The single-firm objects are recomputed (those of the joint sweep are
    read from its cache when ``recompute_joint`` is False); the duopoly
    objects are read from the cache.
    """
    duopoly = load_duopoly_grid()
    sweep = run_sweep(duopoly=duopoly)
    if recompute_joint:
        joint = run_joint_sweep(workers=workers, duopoly=duopoly)
    else:
        joint = load_joint_grid(duopoly)
    capability = capability_extension()
    elasticities = policy_elasticities()
    fragile = duopoly.get("fragile")
    report = [
        format_window_report(admissibility_window()),
        "",
        "Local elasticities of the single firm's policy (d ln y / d ln theta):",
        *(
            f"  {row['param']}: "
            + ", ".join(
                f"{k} {v:+.2f}" for k, v in row.items() if k not in ("param", "value")
            )
            for row in elasticities
        ),
        "",
        format_sweep_report(sweep),
        "",
        format_joint_report(joint),
        "",
        format_capability_report(capability),
    ]
    if fragile is not None and "record" in fragile and not fragile.get("failure"):
        params = ModelParameters().with_param(**fragile["values"])
        objects = duopoly_objects(fragile["record"], single_firm_objects(params))
        report += [
            "",
            f"Cell gamma = {FRAGILE_GAMMA}: "
            + ", ".join(f"{k} = {v:.4g}" for k, v in objects.items()),
        ]
    return {
        "sweep": sweep,
        "joint": joint,
        "capability": capability,
        "elasticities": elasticities,
        "report": "\n".join(report),
    }


def write_all_csv(results: dict[str, Any], directory: Path) -> list[Path]:
    """Write the CSVs of `run_all` to ``directory``."""
    return [
        write_sweep_csv(results["sweep"], directory),
        write_sweep_csv(results["joint"], directory, "robustness_joint_sweep"),
        write_sweep_csv(results["capability"], directory, "capability_extension"),
        write_sweep_csv(results["elasticities"], directory, "policy_elasticities"),
    ]


def main(argv: list[str] | None = None) -> None:
    """Run the sweeps and write the CSVs, or rewrite a cache.

    ``joint-grid`` rewrites ``models/robustness_joint.csv``;
    ``duopoly-grid [fresh|retry]`` solves the duopoly cells missing from
    ``models/robustness_duopoly.json`` (all of them, or also the failed ones).
    """
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(message)s")
    argv = sys.argv[1:] if argv is None else argv
    if "joint-grid" in argv:
        rows = write_joint_grid()
        print(format_joint_report(rows))
        return
    if "duopoly-grid" in argv:
        write_duopoly_grid(fresh="fresh" in argv, retry="retry" in argv)
        return
    results = run_all()
    print(results["report"])
    try:
        directory = get_results_directories().tables
    except MissingEnvVarError:
        logging.warning("RESULTS_DIR is not set; skipping CSV output")
        return
    for path in write_all_csv(results, directory):
        logging.info("Sweep written to %s", path)


if __name__ == "__main__":
    main()
