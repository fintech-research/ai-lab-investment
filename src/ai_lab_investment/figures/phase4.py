"""Publication-quality figures for Phase 4: calibration and revealed beliefs.

Generates figures showing calibration results, revealed belief estimates,
sensitivity analysis, and investment predictions.
"""

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

from ..calibration.data import get_baseline_calibration
from ..calibration.revealed_beliefs import RevealedBeliefs

# Publication style
plt.rcParams.update({
    "font.family": "serif",
    "font.size": 11,
    "axes.labelsize": 12,
    "axes.titlesize": 13,
    "legend.fontsize": 10,
    "xtick.labelsize": 10,
    "ytick.labelsize": 10,
    "figure.dpi": 300,
    "savefig.dpi": 300,
    "text.usetex": False,
})


def plot_investment_predictions(
    output_dir: Path | None = None,
) -> plt.Figure:
    """Show predicted investment vs lambda.

    Key figure: what investment patterns are consistent with different
    beliefs about AI timeline arrival rates.
    """
    calib = get_baseline_calibration()
    rb = RevealedBeliefs(calib)
    lam_vals = np.linspace(0.01, 1.0, 50)
    preds = rb.investment_predictions(lam_vals, regime="H")

    valid = preds["has_solution"]

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(11, 4.5))

    ax1.plot(
        preds["lambda_values"][valid],
        preds["triggers"][valid],
        "b-",
        linewidth=2,
    )
    ax1.set_xlabel(r"Arrival rate $\lambda$ (yr$^{-1}$)")
    ax1.set_ylabel("Investment trigger $X^*$")
    ax1.set_title("(A) When to Invest")

    ax2.plot(
        preds["lambda_values"][valid],
        preds["capacities"][valid],
        "r-",
        linewidth=2,
    )
    ax2.set_xlabel(r"Arrival rate $\lambda$ (yr$^{-1}$)")
    ax2.set_ylabel("Optimal capacity $K^*$")
    ax2.set_title("(B) How Much to Invest")

    fig.suptitle(
        r"Investment Decisions as a Function of AI Timeline Beliefs ($\lambda$)",
        fontsize=14,
    )
    plt.tight_layout()

    if output_dir is not None:
        output_dir.mkdir(parents=True, exist_ok=True)
        fig.savefig(output_dir / "phase4_investment_predictions.pdf")
        fig.savefig(output_dir / "phase4_investment_predictions.png")

    return fig


def plot_sensitivity_analysis(
    output_dir: Path | None = None,
) -> plt.Figure:
    """Show sensitivity of implied lambda to key parameters.

    4-panel figure: how the inferred lambda changes when each
    calibrated parameter is varied.
    """
    calib = get_baseline_calibration()
    rb = RevealedBeliefs(calib)

    # Use the first firm as reference for sensitivity analysis
    firm = calib.firms[0]

    fig, axes = plt.subplots(2, 2, figsize=(10, 8))

    panels = [
        ("sigma_H", np.linspace(0.20, 0.50, 25), r"$\sigma_H$", "(A)"),
        ("alpha", np.linspace(0.30, 0.50, 25), r"$\alpha$", "(B)"),
        ("r", np.linspace(0.08, 0.20, 25), r"$r$", "(C)"),
        ("delta", np.linspace(0.01, 0.08, 25), r"$\delta$", "(D)"),
    ]

    for idx, (param_name, values, xlabel, panel_label) in enumerate(panels):
        ax = axes[idx // 2, idx % 2]
        result = rb.sensitivity_analysis(firm, param_name, values)
        valid = ~np.isnan(result["implied_lambda"])

        if valid.sum() > 0:
            ax.plot(
                result["param_values"][valid],
                result["implied_lambda"][valid],
                "b-",
                linewidth=2,
            )
        ax.set_xlabel(xlabel)
        ax.set_ylabel(r"Implied $\lambda$")
        ax.set_title(f"{panel_label} Sensitivity to {xlabel}")

    fig.suptitle(
        r"Sensitivity of Revealed $\lambda$ to Calibration Assumptions",
        fontsize=14,
    )
    plt.tight_layout()

    if output_dir is not None:
        output_dir.mkdir(parents=True, exist_ok=True)
        fig.savefig(output_dir / "phase4_sensitivity.pdf")
        fig.savefig(output_dir / "phase4_sensitivity.png")

    return fig


def plot_firm_comparison(
    output_dir: Path | None = None,
) -> plt.Figure:
    """Compare stylized firms' investment intensity and implied beliefs."""
    calib = get_baseline_calibration()
    firms = calib.firms

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(11, 4.5))

    names = [f.name.split("(")[1].rstrip(")") for f in firms]
    capex_intensity = [f.capex_2025 / f.revenue_2025 for f in firms]
    rev_growth = [f.revenue_2025 / f.revenue_2024 for f in firms]
    leverages = [f.leverage_ratio for f in firms]

    colors = ["#2196F3", "#FF9800", "#4CAF50", "#F44336"]
    x = np.arange(len(names))

    ax1.bar(x, capex_intensity, color=colors, alpha=0.8)
    ax1.set_xticks(x)
    ax1.set_xticklabels(names, rotation=15, ha="right")
    ax1.set_ylabel("CapEx / Revenue (2025)")
    ax1.set_title("(A) Investment Intensity")

    ax2.scatter(rev_growth, leverages, s=200, c=colors, alpha=0.8, edgecolors="black")
    for i, name in enumerate(names):
        ax2.annotate(
            name,
            (rev_growth[i], leverages[i]),
            textcoords="offset points",
            xytext=(10, 5),
            fontsize=9,
        )
    ax2.set_xlabel("Revenue Growth (2024-2025x)")
    ax2.set_ylabel("Leverage Ratio")
    ax2.set_title("(B) Growth vs. Leverage")

    fig.suptitle("AI Infrastructure Firms: Stylized Comparison", fontsize=14)
    plt.tight_layout()

    if output_dir is not None:
        output_dir.mkdir(parents=True, exist_ok=True)
        fig.savefig(output_dir / "phase4_firm_comparison.pdf")
        fig.savefig(output_dir / "phase4_firm_comparison.png")

    return fig


def plot_lambda_timeline(
    output_dir: Path | None = None,
) -> plt.Figure:
    """Show what different lambda values imply for AI timelines.

    Translates lambda into expected years until regime switch.
    """
    lam_vals = np.linspace(0.05, 1.0, 50)
    expected_years = 1.0 / lam_vals
    prob_5yr = 1 - np.exp(-lam_vals * 5)

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(11, 4.5))

    ax1.plot(lam_vals, expected_years, "b-", linewidth=2)
    ax1.set_xlabel(r"Arrival rate $\lambda$ (yr$^{-1}$)")
    ax1.set_ylabel("Expected years until regime switch")
    ax1.set_title("(A) Expected Timeline")
    ax1.set_ylim(0, 25)

    ax2.plot(lam_vals, prob_5yr * 100, "r-", linewidth=2)
    ax2.set_xlabel(r"Arrival rate $\lambda$ (yr$^{-1}$)")
    ax2.set_ylabel("Probability (%)")
    ax2.set_title("(B) Prob. of Switch Within 5 Years")

    fig.suptitle(
        r"Interpreting $\lambda$: AI Timeline Beliefs",
        fontsize=14,
    )
    plt.tight_layout()

    if output_dir is not None:
        output_dir.mkdir(parents=True, exist_ok=True)
        fig.savefig(output_dir / "phase4_lambda_timeline.pdf")
        fig.savefig(output_dir / "phase4_lambda_timeline.png")

    return fig


def generate_all_phase4_figures(
    output_dir: Path | None = None,
) -> list[plt.Figure]:
    """Generate all Phase 4 figures."""
    figs = [
        plot_investment_predictions(output_dir),
        plot_sensitivity_analysis(output_dir),
        plot_firm_comparison(output_dir),
        plot_lambda_timeline(output_dir),
    ]
    plt.close("all")
    return figs
