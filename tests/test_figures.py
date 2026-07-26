"""Smoke tests for the paper figure generators.

`figures/paper.py` is the single source of truth for the manuscript's
figures, and `paper/generate_figures.py` is a thin wrapper around it, so
exercising every `create_*` function here covers the code path that
produces the paper. The tests assert that each figure builds, is
non-degenerate (has axes and drawn data), and that the wrapper stays in
sync with the module.

Runtime is ~6s for all eleven figures, so they run in the default suite
rather than behind a marker.
"""

import inspect
import re
from pathlib import Path

import matplotlib
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


@pytest.fixture(autouse=True)
def _close_figures():
    yield
    plt.close("all")


def test_expected_number_of_figure_generators():
    assert len(CREATE_FUNCTIONS) == EXPECTED_N_FIGURES


@pytest.mark.parametrize("name", CREATE_FUNCTIONS)
def test_figure_builds_and_renders(name, tmp_path):
    """Each generator returns a non-degenerate Figure that the backend can
    render to disk, which is what `paper/generate_figures.py` does."""
    fig = getattr(paper_figures, name)()
    assert isinstance(fig, plt.Figure)
    axes = fig.get_axes()
    assert axes, f"{name} produced a figure with no axes"
    drawn = sum(
        len(ax.lines) + len(ax.patches) + len(ax.collections) + len(ax.images)
        for ax in axes
    )
    assert drawn > 0, f"{name} produced axes with no drawn data"

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
