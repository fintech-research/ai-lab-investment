"""Publication-quality figures for Phase 5: valuation analysis.

Generates figures showing growth option decomposition, credit risk,
the Dario dilemma, and equity value sensitivity to AI timeline beliefs.
"""

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

from ..models import ModelParameters, ValuationAnalysis


def plot_growth_option_decomposition(
    output_dir: Path | None = None,
) -> plt.Figure:
    """Decompose firm value as a function of installed capacity.

    Exploratory version of the paper's fig-growth-decomposition: delegates
    to `ValuationAnalysis.capacity_gap_decomposition` at the
    precommitted-scale policy of the model of record (issue #184), so the
    x-axis is K_installed / K*.
    """
    va = ValuationAnalysis(ModelParameters())
    K_ratios = np.linspace(0.01, 1.5, 40)
    decomp = va.capacity_gap_decomposition(K_ratios, demand_multiple=1.5)
    assets = decomp["assets_in_place"]
    counterfactual = decomp["capacity_gap"]

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(11, 4.5))

    ax1.stackplot(
        K_ratios,
        assets,
        counterfactual,
        labels=["Assets-in-place", "Capacity gap"],
        colors=["#2196F3", "#FF9800"],
        alpha=0.8,
    )
    ax1.axvline(1.0, color="gray", linestyle=":", alpha=0.6, linewidth=1)
    ax1.set_xlabel(r"Installed capacity $K / K^*$")
    ax1.set_ylabel("Normalized value")
    ax1.set_title("(A) Value Decomposition")
    ax1.legend(loc="upper left")

    ax2.plot(K_ratios, decomp["gap_fraction"], "b-", linewidth=2)
    ax2.axvline(1.0, color="gray", linestyle=":", alpha=0.6, linewidth=1)
    ax2.set_xlabel(r"Installed capacity $K / K^*$")
    ax2.set_ylabel("Scale-gap index (%)")
    ax2.set_title("(B) Scale-Gap Index")
    ax2.set_ylim(0, 100)

    fig.suptitle("Normalized Scale-Gap Diagnostic", fontsize=14)
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

    At the model's own policies (issue #184, the exhibit of issue #179):
    delegates to `ValuationAnalysis.on_policy_credit`, debt issued at the
    single firm's precommitted-scale entry, the duopoly leader's first
    investment and the follower's post-switch entry, both debt conventions.
    """
    va = ValuationAnalysis(ModelParameters())
    leverages = tuple(float(x) for x in np.linspace(0.0, 0.7, 15))
    rows = va.on_policy_credit(leverages=leverages)

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(11, 4.5))
    colours = {"single_firm": "k", "leader": "b", "follower": "0.5"}
    styles = {"par": "-", "fair": "--"}
    for role, colour in colours.items():
        for debt, style in styles.items():
            sel = [r for r in rows if r["role"] == role and r["debt"] == debt]
            lev = [r["leverage"] for r in sel]
            label = f"{role.replace('_', ' ')}, {debt}"
            ax1.plot(
                lev,
                [1e4 * r["spread"] for r in sel],
                color=colour,
                linestyle=style,
                linewidth=2,
                label=label,
            )
            ax2.plot(
                lev,
                [100 * r["default_probability"] for r in sel],
                color=colour,
                linestyle=style,
                linewidth=2,
            )
    ax1.set_xlabel("Leverage (debt/investment)")
    ax1.set_ylabel("Credit spread at entry (bps)")
    ax1.set_title("(A) Credit Spread at the Model's Policies")
    ax1.legend(loc="upper left", fontsize="small")
    ax2.set_xlabel("Leverage (debt/investment)")
    ax2.set_ylabel("5-year default probability, no switch (%)")
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

    Value loss against lambda_invest at lambda_true = 0.10, for the single
    firm of the model of record with precommitted post-switch scale
    (issue #184, the exhibit of issue #180): unlevered claims
    (`ValuationAnalysis.dario_dilemma`) and the levered claims at
    ell = 0.40 under fairly priced debt (`dario_dilemma_leveraged`).
    """
    va = ValuationAnalysis(ModelParameters())

    fixed_true = 0.10
    lam_range = np.geomspace(0.02, 0.50, 25)
    losses_unlev = [
        100 * va.dario_dilemma(fixed_true, float(li))["value_loss_pct"]
        for li in lam_range
    ]
    losses_lev = [
        100
        * va.dario_dilemma_leveraged(fixed_true, float(li), leverage=0.40)[
            "value_loss_pct"
        ]
        for li in lam_range
    ]

    fig, ax = plt.subplots(figsize=(7, 5))

    ax.plot(lam_range, losses_unlev, "b-", linewidth=2, label=r"$\ell = 0$")
    ax.plot(
        lam_range, losses_lev, "r--", linewidth=2, label=r"$\ell = 0.40$, fair debt"
    )

    ax.axvline(fixed_true, color="gray", linestyle=":", alpha=0.6, linewidth=1)
    ax.axhline(0, color="gray", alpha=0.3, linewidth=0.5)

    ax.set_xscale("log")
    ax.set_xlabel(r"Investment belief $\lambda_{\mathrm{invest}}$ (log scale)")
    ax.set_ylabel(r"Value loss $\Delta V / V^*$ (\%)")
    ax.set_title(
        rf"Dario's Dilemma, precommitted scale ($\lambda_{{true}} = {fixed_true}$)"
    )
    ax.legend(loc="upper center")
    ax.set_ylim(bottom=-2)

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

    Uses the phi-aware model where lambda enters through A_eff, under the
    pure-power approximation (`equity_value_vs_lambda_with_phi`); the
    paper's exact counterpart is `figures.paper.lambda_option_value_curve`.
    """
    params = ModelParameters()
    va = ValuationAnalysis(params)

    lam_vals = np.linspace(0.02, 1.0, 50)
    result = va.equity_value_vs_lambda_with_phi(lam_vals)
    valid = ~np.isnan(result["option_values"])

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(11, 4.5))

    if valid.sum() > 0:
        ax1.plot(
            result["lambda_values"][valid],
            result["option_values"][valid],
            "b-",
            linewidth=2,
        )
    ax1.set_xlabel(r"Arrival rate $\tilde{\lambda}$ (yr$^{-1}$)")
    ax1.set_ylabel("Option value $F(X)$")
    ax1.set_title(r"(A) Equity Value vs. $\tilde{\lambda}$")

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
            result["phis"][valid],
            "g--",
            linewidth=2,
            label=r"Training $\phi^*$",
        )
        ax2_twin.set_ylabel(r"Optimal $\phi^*$", color="g")
        ax2_twin.set_ylim(0, 1)
    ax2.set_xlabel(r"Arrival rate $\tilde{\lambda}$ (yr$^{-1}$)")
    ax2.set_ylabel("Investment trigger $X^*$", color="r")
    ax2.set_title(r"(B) Investment Policy vs. $\tilde{\lambda}$")

    lines1, labels1 = ax2.get_legend_handles_labels()
    lines2, labels2 = ax2_twin.get_legend_handles_labels()
    ax2.legend(lines1 + lines2, labels1 + labels2, loc="best")

    fig.suptitle(
        r"Equity Valuation Sensitivity to AI Timeline Beliefs ($\tilde{\lambda}$)",
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
