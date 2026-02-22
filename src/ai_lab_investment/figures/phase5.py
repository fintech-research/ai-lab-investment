"""Publication-quality figures for Phase 5: valuation analysis.

Generates figures showing growth option decomposition, credit risk,
the Dario dilemma, and equity value sensitivity to AI timeline beliefs.
"""

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

from ..models import ModelParameters, ValuationAnalysis

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


def plot_growth_option_decomposition(
    output_dir: Path | None = None,
) -> plt.Figure:
    """Decompose firm value into assets-in-place and growth options.

    Key figure: shows how the value composition shifts as demand grows.
    """
    params = ModelParameters()
    va = ValuationAnalysis(params)

    X_vals = np.linspace(0.1, 3.0, 40)
    assets = np.full_like(X_vals, np.nan)
    expansion = np.full_like(X_vals, np.nan)
    switch_val = np.full_like(X_vals, np.nan)

    for i, X in enumerate(X_vals):
        result = va.growth_option_decomposition(X, K_installed=1.0)
        assets[i] = result["assets_in_place"]
        expansion[i] = result["expansion_option"]
        switch_val[i] = result["regime_switch_value"]

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(11, 4.5))

    ax1.stackplot(
        X_vals,
        assets,
        expansion,
        labels=["Assets-in-place", "Expansion option"],
        colors=["#2196F3", "#FF9800"],
        alpha=0.8,
    )
    ax1.set_xlabel("Demand level $X$")
    ax1.set_ylabel("Firm value")
    ax1.set_title("(A) Value Decomposition (H regime)")
    ax1.legend(loc="upper left")

    # Growth fraction
    total = assets + expansion
    growth_frac = np.where(total > 0, expansion / total, 0)
    ax2.plot(X_vals, growth_frac * 100, "b-", linewidth=2)
    ax2.set_xlabel("Demand level $X$")
    ax2.set_ylabel("Growth option fraction (%)")
    ax2.set_title("(B) Growth Option Share of Total Value")
    ax2.set_ylim(0, 100)

    fig.suptitle(
        "Growth Option Decomposition: Assets vs. Expansion Value",
        fontsize=14,
    )
    plt.tight_layout()

    if output_dir is not None:
        output_dir.mkdir(parents=True, exist_ok=True)
        fig.savefig(output_dir / "phase5_growth_decomposition.pdf")
        fig.savefig(output_dir / "phase5_growth_decomposition.png")

    return fig


def plot_credit_risk(
    output_dir: Path | None = None,
) -> plt.Figure:
    """Show credit spreads and default probability vs leverage.

    Key figure: maps from capital structure to credit risk.
    """
    params = ModelParameters()
    va = ValuationAnalysis(params)

    leverages = np.linspace(0.05, 0.7, 30)
    result = va.credit_spread_curve(leverages)

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(11, 4.5))

    valid = ~np.isnan(result["credit_spread"])
    if valid.sum() > 0:
        ax1.plot(
            result["leverage"][valid],
            result["credit_spread"][valid] * 10000,
            "b-",
            linewidth=2,
        )
    ax1.set_xlabel("Leverage (debt/investment)")
    ax1.set_ylabel("Credit spread (bps)")
    ax1.set_title("(A) Credit Spread Curve")

    valid_dp = ~np.isnan(result["default_probability"])
    if valid_dp.sum() > 0:
        ax2.plot(
            result["leverage"][valid_dp],
            result["default_probability"][valid_dp] * 100,
            "r-",
            linewidth=2,
        )
    ax2.set_xlabel("Leverage (debt/investment)")
    ax2.set_ylabel("5-year default probability (%)")
    ax2.set_title("(B) Default Probability")

    fig.suptitle(
        "Credit Risk in AI Infrastructure Firms",
        fontsize=14,
    )
    plt.tight_layout()

    if output_dir is not None:
        output_dir.mkdir(parents=True, exist_ok=True)
        fig.savefig(output_dir / "phase5_credit_risk.pdf")
        fig.savefig(output_dir / "phase5_credit_risk.png")

    return fig


def plot_dario_dilemma(
    output_dir: Path | None = None,
) -> plt.Figure:
    """Visualize the cost of belief mismatches.

    Key figure: heatmap showing value loss when a firm's investment
    strategy doesn't match its true beliefs about AI timelines.
    """
    params = ModelParameters()
    va = ValuationAnalysis(params)

    lt_range = np.linspace(0.05, 0.60, 15)
    li_range = np.linspace(0.05, 0.60, 15)
    surface = va.dario_dilemma_surface(lt_range, li_range)

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(11, 4.5))

    # Heatmap
    im = ax1.imshow(
        surface["value_loss_pct"] * 100,
        extent=[li_range[0], li_range[-1], lt_range[-1], lt_range[0]],
        aspect="auto",
        cmap="RdYlGn_r",
        vmin=0,
    )
    ax1.set_xlabel(r"Investment $\lambda$ (strategy)")
    ax1.set_ylabel(r"True $\lambda$ (belief)")
    ax1.set_title("(A) Value Loss from Mismatch (%)")
    ax1.plot(
        [li_range[0], li_range[-1]],
        [lt_range[0], lt_range[-1]],
        "k--",
        linewidth=1,
        label="Matched beliefs",
    )
    ax1.legend(loc="upper left", fontsize=9)
    fig.colorbar(im, ax=ax1, label="Value loss (%)")

    # Cross-section: fix true lambda, vary investment lambda
    fixed_true = 0.30
    results_conservative = []
    results_aggressive = []
    lam_range = np.linspace(0.05, 0.60, 20)
    for li in lam_range:
        r = va.dario_dilemma(fixed_true, li)
        if "value_loss_pct" in r:
            if li < fixed_true:
                results_conservative.append((li, r["value_loss_pct"]))
            else:
                results_aggressive.append((li, r["value_loss_pct"]))

    if results_conservative:
        x_c, y_c = zip(*results_conservative, strict=True)
        ax2.plot(x_c, np.array(y_c) * 100, "b-", linewidth=2, label="Conservative")
    if results_aggressive:
        x_a, y_a = zip(*results_aggressive, strict=True)
        ax2.plot(x_a, np.array(y_a) * 100, "r-", linewidth=2, label="Aggressive")
    ax2.axvline(fixed_true, color="gray", linestyle="--", alpha=0.5)
    ax2.set_xlabel(r"Investment $\lambda$")
    ax2.set_ylabel("Value loss (%)")
    ax2.set_title(rf"(B) Cost of Mismatch ($\lambda_{{true}}={fixed_true}$)")
    ax2.legend()

    fig.suptitle(
        r"The Dario Dilemma: Cost of Belief Mismatches",
        fontsize=14,
    )
    plt.tight_layout()

    if output_dir is not None:
        output_dir.mkdir(parents=True, exist_ok=True)
        fig.savefig(output_dir / "phase5_dario_dilemma.pdf")
        fig.savefig(output_dir / "phase5_dario_dilemma.png")

    return fig


def plot_equity_vs_lambda(
    output_dir: Path | None = None,
) -> plt.Figure:
    """Show how equity valuation depends on AI timeline beliefs.

    Key figure: demonstrates that firms with different lambda beliefs
    should have dramatically different valuations.
    """
    params = ModelParameters()
    va = ValuationAnalysis(params)

    lam_vals = np.linspace(0.02, 1.0, 50)
    result = va.equity_value_vs_lambda(lam_vals)
    valid = ~np.isnan(result["option_values"])

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(11, 4.5))

    if valid.sum() > 0:
        ax1.plot(
            result["lambda_values"][valid],
            result["option_values"][valid],
            "b-",
            linewidth=2,
        )
    ax1.set_xlabel(r"Arrival rate $\lambda$ (yr$^{-1}$)")
    ax1.set_ylabel("Option value $F(X)$")
    ax1.set_title("(A) Equity Value vs. AI Timeline Belief")

    if valid.sum() > 0:
        ax2.plot(
            result["lambda_values"][valid],
            result["triggers"][valid],
            "r-",
            linewidth=2,
            label="Trigger $X^*$",
        )
        ax2_twin = ax2.twinx()
        ax2_twin.plot(
            result["lambda_values"][valid],
            result["capacities"][valid],
            "g--",
            linewidth=2,
            label="Capacity $K^*$",
        )
        ax2_twin.set_ylabel("Optimal capacity $K^*$", color="g")
    ax2.set_xlabel(r"Arrival rate $\lambda$ (yr$^{-1}$)")
    ax2.set_ylabel("Investment trigger $X^*$", color="r")
    ax2.set_title("(B) Investment Policy vs. Belief")

    lines1, labels1 = ax2.get_legend_handles_labels()
    lines2, labels2 = ax2_twin.get_legend_handles_labels()
    ax2.legend(lines1 + lines2, labels1 + labels2, loc="best")

    fig.suptitle(
        r"Equity Valuation Sensitivity to AI Timeline Beliefs ($\lambda$)",
        fontsize=14,
    )
    plt.tight_layout()

    if output_dir is not None:
        output_dir.mkdir(parents=True, exist_ok=True)
        fig.savefig(output_dir / "phase5_equity_vs_lambda.pdf")
        fig.savefig(output_dir / "phase5_equity_vs_lambda.png")

    return fig


def generate_all_phase5_figures(
    output_dir: Path | None = None,
) -> list[plt.Figure]:
    """Generate all Phase 5 figures."""
    figs = [
        plot_growth_option_decomposition(output_dir),
        plot_credit_risk(output_dir),
        plot_dario_dilemma(output_dir),
        plot_equity_vs_lambda(output_dir),
    ]
    plt.close("all")
    return figs
