"""Archetype-level outputs and stated beliefs under the model of record (#183).

Two exhibits of the calibration section are computed here.

Archetypes (`archetype_outputs`). For each stylized firm of
`data.get_stylized_firms`, the assigned training fraction phi_hat is mapped
into an implied arrival rate by inverting the closed-form allocation rule of
Proposition 1, lambda = (phi / (1 - phi))^(1 - alpha) (r - mu_H), at phi_hat
and at phi_hat -/+ the uncertainty band. The rule is the same in the exact
problem and in the pure-power approximation, so the bands do not depend on
the solution method. At each of the three implied beliefs the single firm is
then solved in the exact piecewise problem (the model of record), holding
every other parameter, r included, at the baseline:

- the precommitted-scale policy (X*, K*) of Proposition 1(iii);
- whether a firm that chooses its scale at the switch invests before it, and
  at which trigger (it waits for the switch for beliefs at or above about
  0.073 at baseline);
- the credit objects at the archetype's own leverage, with debt issued at
  the precommitted-scale entry and priced with the exact claims
  (`ValuationAnalysis.on_policy_credit`, issue #179): the boundary at which
  the firm stops operating, the distance X* / X_D, and the five-year
  first-passage probability under the L-regime drift with the switch
  omitted, under par and fairly priced debt;
- Dario's dilemma if the implied belief is wrong and the truth is the
  baseline lambda (`belief_mismatch.SingleFirmMismatch`, issue #180), in the
  precommitted and the unrestricted versions, measured at the default
  reference demand (half the informed precommitted-scale trigger).

Credit is priced under the archetype's own belief; the dilemma values the
archetype's policy under the baseline belief. The duopoly is not re-solved:
`archetype_duopoly_cells` reports the cached equilibria of the entry game
(ell = 0, `duopoly_equilibria.json`) at the arrival rates of the cache that
fall inside each band. The archetype WACCs are checked against the window
in r on which (A2) holds (`robustness.admissibility_window`); the implied
band at the archetype's own WACC is reported for reference only, since the
capacity problem is not well-posed outside the window.

Stated beliefs (`stated_beliefs`). A statement that the switch arrives with
probability p within T years maps into a constant arrival rate by
P(tau <= T) = 1 - exp(-lambda T), so lambda = -ln(1 - p) / T
(`lambda_from_probability`). `STATED_BELIEFS` lists the statements; only
those with a cite key in `paper/references.bib` enter the paper, the others
(``cite_key=None``) wait for a source (TO_VERIFY.md).

The phi_hat are assigned by judgment (calibration section), so neither
exhibit is evidence that beliefs explain observed differences across firms.
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Any

from ..models.belief_mismatch import SingleFirmMismatch
from ..models.duopoly import load_equilibrium_grid
from ..models.parameters import ModelParameters
from ..models.piecewise_option import solve_single_firm
from ..models.valuation import ValuationAnalysis
from .data import CalibrationData, FirmData, get_baseline_calibration
from .revealed_beliefs import RevealedBeliefs

#: Points of the implied-lambda band, in the order of the exhibit.
BAND_POINTS: tuple[str, ...] = ("lo", "mid", "hi")

#: Debt conventions of the archetype credit objects.
DEBT_CONVENTIONS: tuple[str, ...] = ("par", "fair")


def short_name(firm: FirmData) -> str:
    """'Anthropic-like' from 'Firm A (Anthropic-like)'."""
    name = firm.name
    if "(" in name:
        name = name.split("(", 1)[1].rstrip(")")
    return name.replace("Google/Alphabet-like", "Google-like")


def phi_star_closed_form(lam: float, r: float, mu_H: float, alpha: float) -> float:
    """phi* = rho / (1 + rho), rho = [lambda / (r - mu_H)]^(1 / (1 - alpha))."""
    rho = (lam / (r - mu_H)) ** (1.0 / (1.0 - alpha))
    return rho / (1.0 + rho)


def lambda_from_probability(p: float, horizon: float) -> float:
    """Constant arrival rate at which the switch arrives by ``horizon`` w.p. p.

    P(tau <= T) = 1 - exp(-lambda T), so lambda = -ln(1 - p) / T.
    """
    if not 0.0 < p < 1.0:
        msg = f"p must be in (0, 1), got {p}"
        raise ValueError(msg)
    if horizon <= 0.0:
        msg = f"horizon must be positive, got {horizon}"
        raise ValueError(msg)
    return -math.log1p(-p) / horizon


def r_window(params: ModelParameters | None = None) -> tuple[float, float]:
    """Interval of r on which (A2) holds, other parameters at baseline."""
    from ..robustness import admissibility_window

    return admissibility_window(params, ("r",))["r"]


# ----------------------------------------------------------------------
# Archetypes
# ----------------------------------------------------------------------


def _single_firm_point(
    params: ModelParameters,
    lam: float,
    leverage: float,
    truth: dict[str, SingleFirmMismatch],
) -> dict[str, Any]:
    """Model-of-record objects at one implied belief."""
    p = params.with_param(lam=lam)
    sol = solve_single_firm(p)
    row: dict[str, Any] = {
        "lam": lam,
        "phi_star": sol.phi_star,
        "X_star": sol.precommitted.X_star,
        "K_star": sol.precommitted.K,
        "invests_before_switch": bool(sol.invests_before_switch),
        "X_unrestricted": sol.X_star,
        "K_unrestricted": sol.K_star,
        "waiting_margin": sol.waiting_margin,
    }
    credit = ValuationAnalysis(p).on_policy_credit(
        leverages=(leverage,), conventions=DEBT_CONVENTIONS, roles=("single_firm",)
    )
    for c in credit:
        debt = c["debt"]
        row[f"X_D_{debt}"] = c["X_D"]
        row[f"distance_{debt}"] = c["distance"]
        row[f"pd5_{debt}"] = c["default_probability"]
        row[f"spread_{debt}"] = c["spread"]
    for version, model in truth.items():
        loss = model.loss(lam)
        row[f"loss_{version}"] = loss["value_loss_pct"]
        row[f"waits_{version}"] = loss["waits"]
        row[f"immediate_{version}"] = loss["immediate"]
    return row


def archetype_outputs(
    calibration: CalibrationData | None = None,
    phi_uncertainty: float = 0.10,
) -> list[dict[str, Any]]:
    """One record per archetype: implied-lambda band and the outputs above.

    Every point holds r and the other parameters at the calibration
    baseline; the truth of the dilemma is the baseline lambda.

    Returns:
        Records with ``archetype``, ``phi_hat``, ``leverage``, ``wacc``,
        ``wacc_in_window`` (WACC inside the (A2) window in r),
        ``r_window``, ``band`` (lambda at ``lo``/``mid``/``hi``),
        ``band_own_wacc`` (the same inversion at the archetype's WACC, for
        reference) and ``points`` (one dict per band point, keyed as in
        `BAND_POINTS`, with the single-firm, credit and dilemma objects).
    """
    calibration = calibration or get_baseline_calibration()
    params = calibration.to_model_params()
    rb = RevealedBeliefs(calibration)
    window = r_window(params)
    truth = {
        version: SingleFirmMismatch(params, calibration.lam, version)
        for version in ("precommitted", "unrestricted")
    }
    out = []
    for firm in calibration.firms:
        band = rb.phi_inversion_band(firm, phi_uncertainty)
        own = rb.phi_inversion_band(firm, phi_uncertainty, use_firm_wacc=True)
        lams: dict[str, float] = {}
        for key in BAND_POINTS:
            lam = band[f"lambda_{key}"]
            if lam is None:
                msg = f"{firm.name}: phi_hat {firm.training_fraction} not invertible"
                raise ValueError(msg)
            lams[key] = float(lam)
        points = {
            key: _single_firm_point(params, lam, firm.leverage_ratio, truth)
            for key, lam in lams.items()
        }
        out.append({
            "archetype": short_name(firm),
            "phi_hat": firm.training_fraction,
            "leverage": firm.leverage_ratio,
            "wacc": firm.wacc,
            "wacc_in_window": window[0] < firm.wacc < window[1],
            "r_window": window,
            "band": lams,
            "band_own_wacc": {
                "lo": own["lambda_lo"],
                "mid": own["lambda_mid"],
                "hi": own["lambda_hi"],
            },
            "points": points,
        })
    return out


def archetype_duopoly_cells(
    archetypes: list[dict[str, Any]],
) -> dict[str, list[dict[str, Any]]]:
    """Cached entry-game equilibria (ell = 0) at arrival rates in each band.

    Reads `duopoly_equilibria.json` only; no equilibrium is solved. The
    records carry the first investment X_L and the leader's (K_L, phi_L),
    the follower's post-switch (X_F, K_F) and the leader's distance to its
    boundary at X_L.
    """
    cells = sorted(
        (
            r
            for r in load_equilibrium_grid()
            if r["leverage"] == 0.0 and r["scale"] == "envelope"
        ),
        key=lambda r: r["lam"],
    )
    out: dict[str, list[dict[str, Any]]] = {}
    for arch in archetypes:
        lo, hi = arch["band"]["lo"], arch["band"]["hi"]
        out[arch["archetype"]] = [
            {
                "lam": r["lam"],
                "X_L": r["X_L"],
                "K_L": r["K_L"],
                "phi_L": r["phi_L"],
                "X_F": r["X_F"],
                "K_F": r["K_F"],
                "distance_to_default": r["distance_to_default"],
            }
            for r in cells
            if lo - 1e-9 <= r["lam"] <= hi + 1e-9
        ]
    return out


# ----------------------------------------------------------------------
# Stated beliefs
# ----------------------------------------------------------------------


@dataclass(frozen=True)
class StatedBelief:
    """A public statement of the probability p of the switch within T years.

    Attributes:
        speaker: Who made the statement.
        statement: Short paraphrase or quotation.
        p: Probability stated.
        horizon: Years from the statement.
        cite_key: Key in `paper/references.bib`; None when the statement
            has no source there yet (it then stays out of the paper).
        archetype: Archetype whose phi_hat the statement is compared with.
    """

    speaker: str
    statement: str
    p: float
    horizon: float
    cite_key: str | None
    archetype: str

    @property
    def lam(self) -> float:
        return lambda_from_probability(self.p, self.horizon)


#: Statements mapped into lambda. The Amodei statements are from the
#: transcript of `amodei2026dwarkesh` (references/interview_transcript.md):
#: "within ten years ... I'm at 90%"; "99%, 95%--that all this will happen in
#: 10 years"; and "a hunch--this is more like a 50/50 thing--that it's going to
#: be more like one to two, maybe more like one to three" years. The same
#: interview gives the "roughly 50/50" training-inference split. The Hassabis
#: statements have no source in the bibliography or the Zotero library
#: (checked 2026-11-18) and are kept for when one is added (TO_VERIFY.md).
STATED_BELIEFS: tuple[StatedBelief, ...] = (
    StatedBelief(
        "Amodei",
        'Ten-year timeline: "I\'m at 90%"',
        0.90,
        10.0,
        "amodei2026dwarkesh",
        "Anthropic-like",
    ),
    StatedBelief(
        "Amodei",
        '"Strong view" of ten years: 95%',
        0.95,
        10.0,
        "amodei2026dwarkesh",
        "Anthropic-like",
    ),
    StatedBelief(
        "Amodei",
        '"Strong view" of ten years: 99%',
        0.99,
        10.0,
        "amodei2026dwarkesh",
        "Anthropic-like",
    ),
    StatedBelief(
        "Amodei",
        '"Hunch", 50/50: one to three years',
        0.50,
        3.0,
        "amodei2026dwarkesh",
        "Anthropic-like",
    ),
    StatedBelief(
        "Amodei",
        '"Hunch", 50/50: one to two years',
        0.50,
        2.0,
        "amodei2026dwarkesh",
        "Anthropic-like",
    ),
    StatedBelief(
        "Hassabis",
        "about 50% by the end of the decade (Davos, January 2026)",
        0.50,
        4.0,
        None,
        "Google-like",
    ),
    StatedBelief(
        "Hassabis",
        "AGI in five to ten years, read as the median",
        0.50,
        10.0,
        None,
        "Google-like",
    ),
    StatedBelief(
        "Hassabis",
        "AGI in five to ten years, read as the median",
        0.50,
        5.0,
        None,
        "Google-like",
    ),
)

#: Training share reported in `amodei2026dwarkesh` ("roughly 50/50"), for a
#: long-run equilibrium in which the "country of geniuses" already exists.
REPORTED_TRAINING_SHARE = 0.50


def stated_beliefs(
    calibration: CalibrationData | None = None,
    beliefs: tuple[StatedBelief, ...] = STATED_BELIEFS,
    sourced_only: bool = True,
) -> list[dict[str, Any]]:
    """Each statement's lambda, the allocation phi*(lambda) it implies, and
    the comparison with the archetype's assigned phi_hat and implied lambda.

    phi* is the closed form of Proposition 1 at the baseline r (and at the
    archetype's WACC for reference). ``lambda_reported_share`` inverts the
    reported "roughly 50/50" split at the baseline r.
    """
    calibration = calibration or get_baseline_calibration()
    c = calibration
    rb = RevealedBeliefs(calibration)
    firms = {short_name(f): f for f in calibration.firms}
    rows = []
    for b in beliefs:
        if sourced_only and b.cite_key is None:
            continue
        firm = firms[b.archetype]
        lam = b.lam
        rows.append({
            "speaker": b.speaker,
            "statement": b.statement,
            "p": b.p,
            "horizon": b.horizon,
            "cite_key": b.cite_key,
            "lam": lam,
            "expected_years": 1.0 / lam,
            "phi_star": phi_star_closed_form(lam, c.r, c.mu_H, c.alpha),
            "phi_star_own_wacc": phi_star_closed_form(lam, firm.wacc, c.mu_H, c.alpha),
            "archetype": b.archetype,
            "phi_hat": firm.training_fraction,
            "lambda_phi_hat": rb.infer_lambda_from_phi(firm.training_fraction),
            "lambda_reported_share": rb.infer_lambda_from_phi(REPORTED_TRAINING_SHARE),
        })
    return rows


# ----------------------------------------------------------------------
# Units (review comment C6)
# ----------------------------------------------------------------------

#: Anthropic-like 2025 compute spending, $B (`tbl-firms-data`).
ANTHROPIC_COMPUTE_2025 = 7.33


def normalization_example(spend: float = ANTHROPIC_COMPUTE_2025) -> dict[str, float]:
    """Monetary unit m of the calibration section's dollar illustration.

    m is the dollar value of one unit of value in the normalized model
    (c = 1), chosen so that the leader's outlay at first investment,
    I(K_L) = K_L^gamma at the cached baseline equilibrium (ell = 0), equals
    ``spend``. It converts values without re-solving anything, unlike a
    change of the cost scale c, which moves K by 1/kappa and X by
    1/kappa^(1 - alpha), kappa = c^(1/(gamma - 1)), and scales every value
    by 1/kappa (`tests/test_calibration.py::TestUnits`).

    Returns:
        Dict with ``I_leader`` and ``I_follower`` (normalized outlays),
        ``m`` ($B per unit), ``follower_dollars`` ($B), and ``I_single`` and
        ``m_single`` for the precommitted-scale single firm instead.
    """
    from ..models.duopoly import cached_equilibrium

    params = ModelParameters()
    record = cached_equilibrium(lam=params.lam)
    I_L = params.c * record["K_L"] ** params.gamma
    I_F = params.c * record["K_F"] ** params.gamma
    K_s = solve_single_firm(params).precommitted.K
    I_s = params.c * K_s**params.gamma
    m = spend / I_L
    return {
        "I_leader": I_L,
        "I_follower": I_F,
        "m": m,
        "follower_dollars": m * I_F,
        "I_single": I_s,
        "m_single": spend / I_s,
    }


# ----------------------------------------------------------------------
# Exhibit
# ----------------------------------------------------------------------


def _pct(x: float, digits: int = 2) -> str:
    return f"{100.0 * x:.{digits}f}"


def _sig(x: float, digits: int = 2) -> str:
    """Fixed-point string with ``digits`` significant figures."""
    if x == 0.0 or not math.isfinite(x):
        return f"{x}"
    places = max(digits - 1 - math.floor(math.log10(abs(x))), 0)
    return f"{x:.{places}f}"


def _unrestricted_cell(point: dict[str, Any]) -> str:
    if not point["invests_before_switch"]:
        return "waits"
    return _sig(point["X_unrestricted"])


def format_archetype_table(archetypes: list[dict[str, Any]]) -> str:
    """Markdown body (header and rows) of `tbl-archetypes`.

    One row per band point: the training fraction phi_hat -/+ 0.10 and
    phi_hat, the implied lambda, the precommitted-scale (X*, K*), the
    trigger with scale chosen at the switch ("waits" when there is none),
    the distance X*/X_D under par debt at the archetype's leverage, the
    five-year default probability under par and fair debt, and the losses
    of the two versions of the dilemma against the baseline lambda.
    """
    lines = [
        "| Archetype, $\\phi$ | $\\lambda$ | $X^*$ | $K^*$ | $X^{\\text{u}}$ "
        "| $X^*/X_D$ | $\\text{PD}^{\\text{par}}$ (\\%) "
        "| $\\text{PD}^{\\text{fair}}$ (\\%) | $\\Delta V^{\\text{pre}}$ (\\%) "
        "| $\\Delta V^{\\text{u}}$ (\\%) |",
        "|:--|--:|--:|--:|--:|--:|--:|--:|--:|--:|",
    ]
    for arch in archetypes:
        lines.append(
            f"| *{arch['archetype']}, $\\ell = {arch['leverage']:.2f}$* "
            "| | | | | | | | | |"
        )
        for key in BAND_POINTS:
            pt = arch["points"][key]
            lines.append(
                f"| {pt['phi_star']:.2f} | {pt['lam']:.3f} "
                f"| {_sig(pt['X_star'])} | {_sig(pt['K_star'])} "
                f"| {_unrestricted_cell(pt)} | {pt['distance_par']:.2f} "
                f"| {_pct(pt['pd5_par'])} | {_pct(pt['pd5_fair'])} "
                f"| {_pct(pt['loss_precommitted'], 1)} "
                f"| {_pct(pt['loss_unrestricted'], 1)} |"
            )
    return "\n".join(lines)


def format_stated_table(rows: list[dict[str, Any]]) -> str:
    """Markdown body of `tbl-stated-beliefs` (sourced statements only)."""
    lines = [
        "| Statement | $p$ | $T$ (years) | $\\lambda$ | $1/\\lambda$ "
        "(years) | $\\phi^*(\\lambda)$, $r = 0.12$ | $\\phi^*(\\lambda)$, $r = 0.15$ |",
        "|:--|--:|--:|--:|--:|--:|--:|",
    ]
    for row in rows:
        lines.append(
            f"| {row['statement']} | {row['p']:.2f} | {row['horizon']:.0f} "
            f"| {row['lam']:.3f} | {row['expected_years']:.1f} "
            f"| {row['phi_star']:.3f} | {row['phi_star_own_wacc']:.3f} |"
        )
    return "\n".join(lines)


def main() -> None:  # pragma: no cover - console report
    archetypes = archetype_outputs()
    print(format_archetype_table(archetypes))
    print()
    print(format_stated_table(stated_beliefs()))
    print()
    print(normalization_example())
    print()
    for arch in archetypes:
        print(
            f"{arch['archetype']}: WACC {arch['wacc']:.2f} "
            f"{'inside' if arch['wacc_in_window'] else 'outside'} the (A2) "
            f"window ({arch['r_window'][0]:.3f}, {arch['r_window'][1]:.3f}); "
            "band at own WACC "
            + ", ".join(f"{arch['band_own_wacc'][k]:.3f}" for k in BAND_POINTS)
        )
        for key in BAND_POINTS:
            pt = arch["points"][key]
            print(
                f"  {key}: lam {pt['lam']:.4f} phi* {pt['phi_star']:.4f} "
                f"X* {pt['X_star']:.5g} K* {pt['K_star']:.5g} "
                f"unrestricted {pt['invests_before_switch']} "
                f"{pt['X_unrestricted']:.5g} margin {pt['waiting_margin']:.4f} "
                f"dist par/fair {pt['distance_par']:.3f}/{pt['distance_fair']:.3f} "
                f"pd5 {pt['pd5_par']:.5f}/{pt['pd5_fair']:.5f} "
                f"spread {1e4 * pt['spread_par']:.1f}/{1e4 * pt['spread_fair']:.1f} "
                f"loss {pt['loss_precommitted']:.4f}/{pt['loss_unrestricted']:.4f} "
                f"imm {pt['immediate_precommitted']}"
            )
    print()
    for name, cells in archetype_duopoly_cells(archetypes).items():
        for cell in cells:
            print(
                f"{name}: lam {cell['lam']} X_L {cell['X_L']:.5g} "
                f"K_L {cell['K_L']:.5g} phi_L {cell['phi_L']:.4f} "
                f"X_F {cell['X_F']:.4g} K_F {cell['K_F']:.4g} "
                f"X_L/X_D {cell['distance_to_default']:.2f}"
            )
    print()
    for row in stated_beliefs(sourced_only=False):
        print(
            f"{row['speaker']}: {row['statement']} -> lam {row['lam']:.4f} "
            f"({row['expected_years']:.1f} yrs), phi* {row['phi_star']:.4f} "
            f"(own WACC {row['phi_star_own_wacc']:.4f}); {row['archetype']} "
            f"phi_hat {row['phi_hat']} -> lam {row['lambda_phi_hat']:.4f}; "
            f"50/50 -> lam {row['lambda_reported_share']:.4f} "
            f"[{row['cite_key']}]"
        )


if __name__ == "__main__":  # pragma: no cover
    main()
