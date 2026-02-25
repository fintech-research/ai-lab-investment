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

    Uses the phi-aware model. X-axis is K_installed / K_H* (capacity
    relative to optimal), matching the paper's fig-growth-decomposition.
    """
    from ..models.base_model import SingleFirmModel

    params = ModelParameters()
    model = SingleFirmModel(params)
    X_star, K_star, phi_star = model.optimal_trigger_capacity_phi()

    # Vary installed capacity from near 0 to 1.5 * K_star
    K_ratios = np.linspace(0.01, 1.5, 40)
    assets = np.full_like(K_ratios, np.nan)
    counterfactual = np.full_like(K_ratios, np.nan)

    # Evaluate at demand above trigger (1.5 * X*)
    X_eval = 1.5 * X_star
    # Option value at optimal (K*, phi*)
    V_optimal = model.installed_value_with_phi(X_eval, phi_star, K_star, "L")
    I_optimal = model.investment_cost(K_star)
    npv_optimal = V_optimal - I_optimal

    for i, kr in enumerate(K_ratios):
        K_inst = kr * K_star
        # Assets-in-place: value of current capacity at current phi*
        assets[i] = model.installed_value_with_phi(X_eval, phi_star, K_inst, "L")
        # Counterfactual: additional value from reaching K*
        counterfactual[i] = max(npv_optimal - assets[i], 0)

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(11, 4.5))

    ax1.stackplot(
        K_ratios,
        assets,
        counterfactual,
        labels=["Assets-in-place", "Counterfactual capacity value"],
        colors=["#2196F3", "#FF9800"],
        alpha=0.8,
    )
    ax1.axvline(1.0, color="gray", linestyle=":", alpha=0.6, linewidth=1)
    ax1.set_xlabel(r"Installed capacity $K / K_H^*$")
    ax1.set_ylabel("Firm value")
    ax1.set_title("(A) Value Decomposition")
    ax1.legend(loc="upper left")

    # Growth fraction
    total = assets + counterfactual
    growth_frac = np.where(total > 0, counterfactual / total, 0)
    ax2.plot(K_ratios, growth_frac * 100, "b-", linewidth=2)
    ax2.axvline(1.0, color="gray", linestyle=":", alpha=0.6, linewidth=1)
    ax2.set_xlabel(r"Installed capacity $K / K_H^*$")
    ax2.set_ylabel("Growth option fraction (\\%)")
    ax2.set_title("(B) Growth Option Share of Total Value")
    ax2.set_ylim(0, 100)

    fig.suptitle(
        "Growth Option Decomposition",
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

    Single-panel figure showing value loss as a function of
    lambda_invest for a fixed lambda_true, matching the paper's
    fig-investment-dilemma description.
    """
    params = ModelParameters()
    va = ValuationAnalysis(params)

    fixed_true = 0.10
    lam_range = np.linspace(0.02, 0.50, 30)

    # Unleveraged curve
    losses_unlev = []
    for li in lam_range:
        r = va.dario_dilemma(fixed_true, li)
        losses_unlev.append(r.get("value_loss_pct", np.nan) * 100)

    # Leveraged curve (ell = 0.40)
    losses_lev = []
    for li in lam_range:
        r = va.dario_dilemma_leveraged(fixed_true, li, leverage=0.40)
        losses_lev.append(r.get("value_loss_pct", np.nan) * 100)

    fig, ax = plt.subplots(figsize=(7, 5))

    ax.plot(lam_range, losses_unlev, "b-", linewidth=2, label=r"$\ell = 0$")
    ax.plot(lam_range, losses_lev, "r--", linewidth=2, label=r"$\ell = 0.40$")

    ax.axvline(fixed_true, color="gray", linestyle=":", alpha=0.6, linewidth=1)
    ax.axhline(0, color="gray", alpha=0.3, linewidth=0.5)

    # Shade the high-loss region (>10% threshold)
    losses_arr = np.array(losses_unlev)
    high_loss = losses_arr > 10
    if high_loss.any():
        ax.fill_between(
            lam_range,
            0,
            losses_arr,
            where=high_loss,
            alpha=0.10,
            color="red",
            label=r"Loss $> 10\%$",
        )

    ax.set_xlabel(r"Investment $\tilde{\lambda}$")
    ax.set_ylabel(r"Value loss $\Delta V / V^*$ (\%)")
    ax.set_title(rf"Dario's Dilemma ($\tilde{{\lambda}}_{{true}} = {fixed_true}$)")
    ax.legend(loc="upper left")
    ax.set_ylim(bottom=-2)

    # Annotate the asymmetry
    ax.annotate(
        "Underinvestment\n(conservative)",
        xy=(0.04, 15),
        fontsize=9,
        ha="center",
        color="navy",
    )
    ax.annotate(
        "Overinvestment\n(aggressive)",
        xy=(0.35, 8),
        fontsize=9,
        ha="center",
        color="darkred",
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

    Uses the phi-aware model where lambda enters through A_eff,
    producing lambda-dependent triggers, phis, and option values.
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
