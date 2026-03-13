#!/usr/bin/env python3
"""Generate all publication-quality figures for the paper.

Usage:
    uv run python paper/generate_figures.py

Each figure is rendered twice:
  - PDF with ``seaborn-v0_8-paper`` style (print-optimised fonts)
  - PNG with ``seaborn-v0_8-talk`` style (presentation-optimised fonts)

All figure logic lives in :mod:`ai_lab_investment.figures.paper`.
This script is a thin wrapper that applies styles and saves output.
"""

from pathlib import Path

import matplotlib
import matplotlib.pyplot as plt

matplotlib.use("Agg")

from ai_lab_investment.figures.paper import (
    create_comparative_statics,
    create_competition_effect,
    create_credit_risk,
    create_default_boundaries,
    create_firm_comparison,
    create_growth_decomposition,
    create_investment_dilemma,
    create_lambda_option_value,
    create_lambda_timeline,
    create_option_value,
    create_sample_paths,
)

OUT = Path(__file__).parent / "figures"

# ── Style overrides applied on top of seaborn base styles ────────

_PAPER_OVERRIDES: dict[str, object] = {
    "font.family": "serif",
    "text.usetex": False,
    "axes.spines.top": False,
    "axes.spines.right": False,
    "axes.grid": False,
    "figure.dpi": 300,
    "savefig.dpi": 300,
    "savefig.bbox": "tight",
}

_TALK_OVERRIDES: dict[str, object] = {
    "font.family": "serif",
    "text.usetex": False,
    "axes.spines.top": False,
    "axes.spines.right": False,
    "axes.grid": False,
    "figure.dpi": 300,
    "savefig.dpi": 300,
    "savefig.bbox": "tight",
}

# ── Rendering ────────────────────────────────────────────────────


def _save(create_fn, name: str) -> None:
    """Render *create_fn* with paper style (PDF) and talk style (PNG)."""
    OUT.mkdir(parents=True, exist_ok=True)

    with plt.style.context(["seaborn-v0_8-paper", _PAPER_OVERRIDES]):
        fig = create_fn()
        fig.savefig(OUT / f"{name}.pdf")
        plt.close(fig)

    with plt.style.context(["seaborn-v0_8-talk", _TALK_OVERRIDES]):
        fig = create_fn()
        fig.savefig(OUT / f"{name}.png")
        plt.close(fig)

    print(f"  saved {name}")


# ── Figure list (order matches paper) ────────────────────────────

FIGURES: list[tuple] = [
    (create_sample_paths, "fig_sample_paths"),
    (create_option_value, "fig_option_value"),
    (create_comparative_statics, "fig_comparative_statics"),
    (create_lambda_option_value, "fig_lambda_option_value"),
    (create_default_boundaries, "fig_default_boundaries"),
    (create_credit_risk, "fig_credit_risk"),
    (create_competition_effect, "fig_competition_effect"),
    (create_firm_comparison, "fig_firm_comparison"),
    (create_lambda_timeline, "fig_lambda_timeline"),
    (create_growth_decomposition, "fig_growth_decomposition"),
    (create_investment_dilemma, "fig_investment_dilemma"),
]

if __name__ == "__main__":
    print("Generating paper figures...")
    for create_fn, name in FIGURES:
        _save(create_fn, name)
    print("Done.")
