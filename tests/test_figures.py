"""Smoke tests for the paper figure generators.

`figures/paper.py` is the single source of truth for the manuscript's
figures, and `paper/generate_figures.py` is a thin wrapper around it, so
exercising every `create_*` function here covers the code path that
produces the paper. The tests assert that each figure builds, is
non-degenerate (has axes and drawn data), and that the wrapper stays in
sync with the module.

Runtime is under a minute for all eleven figures (most of it the dilemma
figure), so they run in the default suite rather than behind a marker.
"""

import inspect
import re
from pathlib import Path

import matplotlib
import numpy as np
import pytest

matplotlib.use("Agg")

import matplotlib.pyplot as plt

from ai_lab_investment.figures import paper as paper_figures

CREATE_FUNCTIONS = sorted(
    name
    for name, obj in inspect.getmembers(paper_figures, inspect.isfunction)
    if name.startswith("create_") and obj.__module__ == paper_figures.__name__
)

# The paper has eleven figures; AGENTS.md documents the count, so pin it.
EXPECTED_N_FIGURES = 11


# Number of points on each drawn curve, by figure ({points: curves}). A
# solver failure on a grid point must raise rather than thin a curve
# (C19j), so every curve is complete and finite. Helper lines of at most
# two points (reference lines, matched-pair markers, legend proxies) are
# not counted.
CURVE_POINTS = {
    "create_comparative_statics": {40: 8},
    "create_competition_effect": {30: 2, 10: 2},
    "create_credit_risk": {29: 12, 66: 8},
    "create_default_boundaries": {4: 8},
    "create_growth_decomposition": {40: 1},
    "create_investment_dilemma": {121: 3, 14: 2},
    "create_lambda_option_value": {80: 3},
    "create_lambda_timeline": {100: 2},
    "create_option_value": {300: 2},
}

# Curves that are partial by construction: the single firm that chooses its
# scale at the switch has a pre-switch trigger only below lambda = 0.0729,
# which is 7 of the 30 grid points of the competition figure.
PARTIAL_CURVES = {"Single firm, scale chosen at the switch": 7}


def assert_curves_complete(name: str, fig: plt.Figure) -> None:
    counts: dict[int, int] = {}
    for ax in fig.get_axes():
        for line in ax.lines:
            y = np.asarray(line.get_ydata(), dtype=float)
            if len(y) <= 2:
                continue
            counts[len(y)] = counts.get(len(y), 0) + 1
            expected_finite = PARTIAL_CURVES.get(line.get_label(), len(y))
            assert np.isfinite(y).sum() == expected_finite, (name, line.get_label())
    assert counts == CURVE_POINTS.get(name, {}), name


@pytest.fixture(autouse=True)
def _close_figures():
    yield
    plt.close("all")


def test_expected_number_of_figure_generators():
    assert len(CREATE_FUNCTIONS) == EXPECTED_N_FIGURES


@pytest.mark.parametrize("name", CREATE_FUNCTIONS)
def test_figure_builds_and_renders(name, tmp_path):
    """Each generator returns a non-degenerate Figure that the backend can
    render to disk, which is what `paper/generate_figures.py` does, and
    whose curves are complete (`CURVE_POINTS`)."""
    fig = getattr(paper_figures, name)()
    assert isinstance(fig, plt.Figure)
    axes = fig.get_axes()
    assert axes, f"{name} produced a figure with no axes"
    drawn = sum(
        len(ax.lines) + len(ax.patches) + len(ax.collections) + len(ax.images)
        for ax in axes
    )
    assert drawn > 0, f"{name} produced axes with no drawn data"
    # Each curve has the expected number of points (C19j).
    if name != "create_sample_paths":
        assert_curves_complete(name, fig)

    out = tmp_path / f"{name}.pdf"
    fig.savefig(out)
    assert out.stat().st_size > 0


def test_generate_figures_wrapper_covers_every_generator():
    """`paper/generate_figures.py` must not drift from `paper.py`."""
    script = Path(__file__).resolve().parents[1] / "paper" / "generate_figures.py"
    source = script.read_text()
    missing = [name for name in CREATE_FUNCTIONS if name not in source]
    assert not missing, f"generate_figures.py does not render: {missing}"
    entries = re.findall(r"\(create_[a-z_]+, \"fig_[a-z_]+\"\)", source)
    assert len(entries) == EXPECTED_N_FIGURES


def test_lambda_curve_raises_instead_of_skipping(monkeypatch):
    from ai_lab_investment.models.base_model import SingleFirmModel

    def fail(self, X):
        msg = "no solution"
        raise ValueError(msg)

    monkeypatch.setattr(SingleFirmModel, "option_value_with_phi", fail)
    with pytest.raises(RuntimeError, match="lambda_option_value_curve failed"):
        paper_figures.lambda_option_value_curve(np.array([0.05, 0.10]))


def test_comparative_statics_raises_on_an_unsolved_point(monkeypatch):
    from ai_lab_investment.models.base_model import SingleFirmModel

    original = SingleFirmModel.comparative_statics

    def thinned(self, param_name, values, regime="H"):
        result = original(self, param_name, values, regime)
        result["has_trigger"][0] = False
        return result

    monkeypatch.setattr(SingleFirmModel, "comparative_statics", thinned)
    with pytest.raises(RuntimeError, match="points unsolved"):
        paper_figures.create_comparative_statics()


def test_pure_power_dilemma_error_raises(monkeypatch):
    from ai_lab_investment.models.valuation import ValuationAnalysis

    monkeypatch.setattr(
        ValuationAnalysis,
        "pure_power_dilemma",
        lambda self, truth, belief: {"error": "No solution at invest lambda"},
    )
    with pytest.raises(RuntimeError, match="pure_power_dilemma failed"):
        paper_figures.create_investment_dilemma()
