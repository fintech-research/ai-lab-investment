"""Parameter-perturbation robustness sweep for the Internet Appendix.

Perturbs each calibrated parameter one at a time by +/- 25% from the
baseline and re-computes the paper's headline objects:

- Dario's dilemma asymmetry (conservative loss vs aggressive loss, the
  sign of the W''' > 0 claim),
- the capacity-gap fraction at K/K* = 0.1 and 0.3,
- the faith-based survival thresholds (phi_underbar, phi_tilde) and the
  optimal training fraction phi*,
- the preemption discount X_P / X_L^mono.

Draws that violate an admissibility condition -- the parameter-domain
restrictions of Assumption 1 or the interior-capacity condition (A2) --
are *reported* with the failing condition rather than silently dropped,
so the boundary behavior of the calibration is visible.

Run with ``just run-sweep`` (or ``uv run python -m
ai_lab_investment.robustness``); also available as the Hydra pipeline
task ``tasks.robustness_sweep``.
"""

import csv
import logging
from dataclasses import asdict, dataclass, fields
from pathlib import Path

import numpy as np

from .exceptions import MissingEnvVarError
from .models import DuopolyModel, ModelParameters, SingleFirmModel, ValuationAnalysis
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
"""Calibrated parameters perturbed by the sweep (Internet Appendix C)."""

PERTURBATION = 0.25
"""Relative perturbation applied in each direction."""

GAP_K_FRACS: tuple[float, float] = (0.1, 0.3)
"""Installed-capacity fractions at which the capacity gap is evaluated."""

DILEMMA_MISMATCH = (0.2, 2.0)
"""Conservative / aggressive belief multiples relative to lambda_true."""


@dataclass
class Headline:
    """The paper's headline robustness objects at one parameterization."""

    loss_conservative: float
    loss_aggressive: float
    dilemma_asymmetry: float
    gap_fraction_low: float
    gap_fraction_high: float
    phi_star: float
    phi_underbar: float
    phi_tilde: float
    preemption_discount: float

    def sign_checks(self) -> "SignChecks":
        """Evaluate the qualitative claims the appendix asserts are robust."""
        return SignChecks(
            dilemma_asymmetry=self.loss_conservative > self.loss_aggressive,
            gap_positive=self.gap_fraction_high > 0.0,
            faith=0.0 < self.phi_underbar < self.phi_tilde < self.phi_star,
            preemption=0.0 < self.preemption_discount < 1.0,
        )


@dataclass
class SignChecks:
    """Boolean sign claims evaluated at one parameterization."""

    dilemma_asymmetry: bool
    gap_positive: bool
    faith: bool
    preemption: bool


@dataclass
class SweepRow:
    """One perturbation draw and the headline objects it implies."""

    param: str
    direction: str
    value: float
    admissible: bool
    failure: str | None = None
    loss_conservative: float | None = None
    loss_aggressive: float | None = None
    dilemma_asymmetry: float | None = None
    gap_fraction_low: float | None = None
    gap_fraction_high: float | None = None
    phi_star: float | None = None
    phi_underbar: float | None = None
    phi_tilde: float | None = None
    preemption_discount: float | None = None
    sign_dilemma_asymmetry: bool | None = None
    sign_gap_positive: bool | None = None
    sign_faith: bool | None = None
    sign_preemption: bool | None = None


SIGN_FIELDS: tuple[str, ...] = (
    "sign_dilemma_asymmetry",
    "sign_gap_positive",
    "sign_faith",
    "sign_preemption",
)

SIGN_LABELS = {
    "sign_dilemma_asymmetry": "conservative loss > aggressive loss",
    "sign_gap_positive": "capacity-gap fraction > 0 at K/K* = 0.3",
    "sign_faith": "0 < phi_underbar < phi_tilde < phi* (faith mechanism operative)",
    "sign_preemption": "0 < X_P / X_L^mono < 1",
}


def admissibility_failure(params: ModelParameters) -> str | None:
    """Return the failing admissibility condition, or None if admissible.

    Parameter-domain violations (Assumption 1: r > mu_H, alpha in (0,1),
    gamma > 1, ...) are caught at construction time by
    ``ModelParameters``; the interior-capacity condition (A2),
    1/gamma < (beta_H - 1)/(alpha * beta_H) < 1, is checked here.
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


def _headline_objects(params: ModelParameters) -> Headline:
    """Compute the paper's headline robustness objects at ``params``."""
    model = SingleFirmModel(params)
    valuation = ValuationAnalysis(params)
    duopoly = DuopolyModel(params, leverage=0.0)

    lam_true = params.lam
    conservative = valuation.dario_dilemma(lam_true, DILEMMA_MISMATCH[0] * lam_true)
    aggressive = valuation.dario_dilemma(lam_true, DILEMMA_MISMATCH[1] * lam_true)
    loss_conservative = float(conservative["value_loss_pct"])
    loss_aggressive = float(aggressive["value_loss_pct"])

    gap = valuation.capacity_gap_decomposition(np.array(GAP_K_FRACS))
    gap_low, gap_high = (float(x) for x in gap["gap_fraction"])

    _, _, phi_star = model.optimal_trigger_capacity_phi()
    equilibrium = duopoly.solve_preemption_equilibrium()
    discount = equilibrium["X_leader"] / equilibrium["X_leader_monopolist"]

    return Headline(
        loss_conservative=loss_conservative,
        loss_aggressive=loss_aggressive,
        dilemma_asymmetry=(
            loss_conservative / loss_aggressive
            if loss_aggressive != 0
            else float("nan")
        ),
        gap_fraction_low=gap_low,
        gap_fraction_high=gap_high,
        phi_star=float(phi_star),
        phi_underbar=float(duopoly.faith_threshold()),
        phi_tilde=float(duopoly.faith_threshold_exact()),
        preemption_discount=float(discount),
    )


def evaluate_draw(
    base: ModelParameters,
    param: str,
    direction: str,
    perturbation: float = PERTURBATION,
) -> SweepRow:
    """Evaluate a single perturbation draw.

    Args:
        base: Baseline calibration.
        param: Name of the parameter to perturb.
        direction: ``"-"``, ``"+"``, or ``"0"`` (baseline, no perturbation).
        perturbation: Relative size of the perturbation.

    Returns:
        A :class:`SweepRow`; ``admissible`` is False and ``failure``
        names the violated condition when the draw leaves the admissible
        region, in which case the headline fields are None.
    """
    scale = {"-": 1.0 - perturbation, "+": 1.0 + perturbation, "0": 1.0}[direction]
    value = getattr(base, param) * scale

    try:
        params = base.with_param(**{param: value})
    except ValueError as exc:
        return SweepRow(
            param=param,
            direction=direction,
            value=value,
            admissible=False,
            failure=f"(A1) parameter domain: {exc}",
        )

    failure = admissibility_failure(params)
    if failure is not None:
        return SweepRow(
            param=param,
            direction=direction,
            value=value,
            admissible=False,
            failure=failure,
        )

    try:
        headline = _headline_objects(params)
    except (ValueError, RuntimeError) as exc:
        return SweepRow(
            param=param,
            direction=direction,
            value=value,
            admissible=False,
            failure=f"solver failure: {exc}",
        )

    signs = headline.sign_checks()
    return SweepRow(
        param=param,
        direction=direction,
        value=value,
        admissible=True,
        loss_conservative=headline.loss_conservative,
        loss_aggressive=headline.loss_aggressive,
        dilemma_asymmetry=headline.dilemma_asymmetry,
        gap_fraction_low=headline.gap_fraction_low,
        gap_fraction_high=headline.gap_fraction_high,
        phi_star=headline.phi_star,
        phi_underbar=headline.phi_underbar,
        phi_tilde=headline.phi_tilde,
        preemption_discount=headline.preemption_discount,
        sign_dilemma_asymmetry=signs.dilemma_asymmetry,
        sign_gap_positive=signs.gap_positive,
        sign_faith=signs.faith,
        sign_preemption=signs.preemption,
    )


def run_sweep(
    base: ModelParameters | None = None,
    parameters: tuple[str, ...] = SWEEP_PARAMETERS,
    perturbation: float = PERTURBATION,
) -> list[SweepRow]:
    """Run the +/- ``perturbation`` sweep over ``parameters``.

    The first row is the unperturbed baseline; the remaining rows are the
    two perturbations of each parameter, in the order given.
    """
    base = ModelParameters() if base is None else base
    rows = [evaluate_draw(base, parameters[0], "0", perturbation)]
    rows[0].param = "baseline"
    for param in parameters:
        for direction in ("-", "+"):
            rows.append(evaluate_draw(base, param, direction, perturbation))
    return rows


VALUE_FIELDS: tuple[str, ...] = (
    "loss_conservative",
    "loss_aggressive",
    "dilemma_asymmetry",
    "gap_fraction_low",
    "gap_fraction_high",
    "phi_star",
    "phi_underbar",
    "phi_tilde",
    "preemption_discount",
)


@dataclass
class SweepSummary:
    """Aggregate of a sweep: counts, sign survival, and value ranges."""

    n_perturbations: int
    n_admissible: int
    n_failed: int
    failures: list[tuple[str, str, float, str]]
    sign_survival: dict[str, bool]
    sign_violations: dict[str, list[tuple[str, str]]]
    ranges: dict[str, tuple[float, float]]


def summarize_sweep(rows: list[SweepRow]) -> SweepSummary:
    """Aggregate a sweep into counts, sign survival, and value ranges."""
    perturbations = [row for row in rows if row.param != "baseline"]
    admissible = [row for row in perturbations if row.admissible]
    failed = [row for row in perturbations if not row.admissible]

    ranges: dict[str, tuple[float, float]] = {}
    for name in VALUE_FIELDS:
        values = [
            value
            for row in admissible
            if (value := getattr(row, name)) is not None and np.isfinite(value)
        ]
        if values:
            ranges[name] = (min(values), max(values))

    return SweepSummary(
        n_perturbations=len(perturbations),
        n_admissible=len(admissible),
        n_failed=len(failed),
        failures=[
            (row.param, row.direction, row.value, row.failure or "") for row in failed
        ],
        sign_survival={
            name: all(getattr(row, name) for row in admissible) for name in SIGN_FIELDS
        },
        sign_violations={
            name: [
                (row.param, row.direction)
                for row in admissible
                if not getattr(row, name)
            ]
            for name in SIGN_FIELDS
        },
        ranges=ranges,
    )


def _format_value(value: float | bool | str | None) -> str:
    if value is None:
        return "--"
    if isinstance(value, bool):
        return "yes" if value else "NO"
    if isinstance(value, float):
        return f"{value:.4g}"
    return str(value)


def format_sweep_table(rows: list[SweepRow]) -> str:
    """Render the sweep as a fixed-width text table."""
    columns = (
        ("param", "param"),
        ("direction", "dir"),
        ("value", "value"),
        ("admissible", "adm"),
        ("loss_conservative", "loss_cons"),
        ("loss_aggressive", "loss_aggr"),
        ("dilemma_asymmetry", "asym"),
        ("gap_fraction_low", "gap@0.1"),
        ("gap_fraction_high", "gap@0.3"),
        ("phi_star", "phi*"),
        ("phi_underbar", "phi_lo"),
        ("preemption_discount", "X_P/X_L"),
    )
    header = [label for _, label in columns]
    body = [[_format_value(getattr(row, name)) for name, _ in columns] for row in rows]
    widths = [
        max(len(header[i]), *(len(line[i]) for line in body))
        for i in range(len(columns))
    ]
    sep = "  "
    lines = [sep.join(h.ljust(w) for h, w in zip(header, widths, strict=True))]
    lines.append(sep.join("-" * w for w in widths))
    lines.extend(
        sep.join(cell.ljust(w) for cell, w in zip(line, widths, strict=True))
        for line in body
    )
    return "\n".join(lines)


def format_sweep_report(rows: list[SweepRow]) -> str:
    """Render the sweep table plus the failure log and sign summary."""
    summary = summarize_sweep(rows)
    parts = [
        "Parameter-perturbation robustness sweep "
        f"(+/-{PERTURBATION:.0%}, {summary.n_perturbations} perturbations)",
        "",
        format_sweep_table(rows),
        "",
        f"Admissible: {summary.n_admissible} / {summary.n_perturbations}; "
        f"inadmissible: {summary.n_failed}",
    ]

    if summary.failures:
        parts.append("")
        parts.append("Inadmissible draws (reported, not dropped):")
        parts.extend(
            f"  {param} {direction}{PERTURBATION:.0%} -> {value:.4g}: {failure}"
            for param, direction, value, failure in summary.failures
        )

    parts.append("")
    parts.append("Qualitative claims across admissible draws:")
    for name in SIGN_FIELDS:
        survived = summary.sign_survival[name]
        line = f"  {SIGN_LABELS[name]}: {'holds' if survived else 'FAILS'}"
        if not survived:
            offenders = ", ".join(
                f"{param}{direction}"
                for param, direction in summary.sign_violations[name]
            )
            line += f" at {offenders}"
        parts.append(line)

    parts.append("")
    parts.append("Ranges across admissible draws:")
    parts.extend(
        f"  {name}: [{low:.4g}, {high:.4g}]"
        for name, (low, high) in summary.ranges.items()
    )
    return "\n".join(parts)


def write_sweep_csv(rows: list[SweepRow], directory: Path) -> Path:
    """Write the sweep to a timestamped CSV in ``directory``."""
    directory.mkdir(parents=True, exist_ok=True)
    path = timestamp_file(directory / "robustness_sweep.csv")
    field_names = [f.name for f in fields(SweepRow)]
    with path.open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=field_names)
        writer.writeheader()
        writer.writerows(asdict(row) for row in rows)
    return path


def main() -> None:
    """Run the sweep, print the report, and write the CSV to RESULTS_DIR."""
    logging.getLogger().setLevel(logging.INFO)
    rows = run_sweep()
    print(format_sweep_report(rows))

    try:
        directory = get_results_directories().tables
    except MissingEnvVarError:
        logging.warning("RESULTS_DIR is not set; skipping CSV output")
        return
    path = write_sweep_csv(rows, directory)
    logging.info("Sweep written to %s", path)


if __name__ == "__main__":
    main()
