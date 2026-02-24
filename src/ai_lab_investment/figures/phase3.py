"""Publication-quality figures for Phase 3: N-firm numerical solution.

Generates figures showing sequential equilibrium, the effect of the
number of firms, training/inference allocation, and comparison with
the analytical duopoly.
"""

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

from ..models.nfirm import NFirmModel
from ..models.parameters import ModelParameters

# Publication style
plt.rcParams.update({
    "text.usetex": True,
    "font.family": "serif",
    "font.size": 11,
    "axes.labelsize": 12,
    "axes.titlesize": 13,
    "legend.fontsize": 10,
    "xtick.labelsize": 10,
    "ytick.labelsize": 10,
    "figure.dpi": 300,
    "savefig.dpi": 300,
})


def plot_sequential_equilibrium(
    params: ModelParameters | None = None,
    output_dir: Path | None = None,
) -> plt.Figure:
    """Show triggers and capacities for N=2,3,4 firms."""
    if params is None:
        params = ModelParameters()

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(11, 4.5))

    for n in [2, 3, 4]:
        m = NFirmModel(params, n_firms=n, leverage=0.0)
        eq = m.solve_sequential_equilibrium("H")

        orders = [e["entry_order"] for e in eq]
        triggers = [e["X_trigger"] for e in eq]
        capacities = [e["K_capacity"] for e in eq]

        ax1.plot(orders, triggers, "o-", linewidth=2, markersize=8, label=f"N={n}")
        ax2.plot(orders, capacities, "o-", linewidth=2, markersize=8, label=f"N={n}")

    ax1.set_xlabel("Entry order")
    ax1.set_ylabel("Investment trigger $X^*$")
    ax1.set_title("(A) Investment Triggers")
    ax1.legend()
    ax1.set_xticks(range(1, 5))

    ax2.set_xlabel("Entry order")
    ax2.set_ylabel("Optimal capacity $K^*$")
    ax2.set_title("(B) Capacities")
    ax2.legend()
    ax2.set_xticks(range(1, 5))

    fig.suptitle("Sequential Equilibrium by Number of Firms", fontsize=14)
    plt.tight_layout()

    if output_dir is not None:
        output_dir.mkdir(parents=True, exist_ok=True)
        fig.savefig(output_dir / "phase3_sequential_equilibrium.pdf")
        fig.savefig(output_dir / "phase3_sequential_equilibrium.png")

    return fig


def plot_nfirm_comparative_statics(
    params: ModelParameters | None = None,
    output_dir: Path | None = None,
) -> plt.Figure:
    """Comparative statics: leader trigger vs sigma for different N."""
    if params is None:
        params = ModelParameters()

    sigma_vals = np.linspace(0.20, 0.50, 20)

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(11, 4.5))

    for n in [2, 3, 4]:
        m = NFirmModel(params, n_firms=n, leverage=0.0)
        stats = m.comparative_statics("sigma_H", sigma_vals, regime="H")
        valid = stats["has_solution"]

        if valid.sum() > 0:
            # Leader (first entrant)
            ax1.plot(
                stats["param_values"][valid],
                stats["triggers"][valid, 0],
                linewidth=2,
                label=f"N={n} leader",
            )
            # Last entrant
            ax2.plot(
                stats["param_values"][valid],
                stats["triggers"][valid, -1],
                linewidth=2,
                label=f"N={n} last",
            )

    ax1.set_xlabel(r"Volatility $\sigma_H$")
    ax1.set_ylabel("Leader trigger $X_1^*$")
    ax1.set_title("(A) Leader Trigger vs. Volatility")
    ax1.legend()

    ax2.set_xlabel(r"Volatility $\sigma_H$")
    ax2.set_ylabel("Last entrant trigger")
    ax2.set_title("(B) Last Entrant Trigger vs. Volatility")
    ax2.legend()

    fig.suptitle("Effect of Competition on Investment Timing", fontsize=14)
    plt.tight_layout()

    if output_dir is not None:
        output_dir.mkdir(parents=True, exist_ok=True)
        fig.savefig(output_dir / "phase3_nfirm_statics.pdf")
        fig.savefig(output_dir / "phase3_nfirm_statics.png")

    return fig


def plot_training_inference(
    params: ModelParameters | None = None,
    output_dir: Path | None = None,
) -> plt.Figure:
    """Show quality dynamics and optimal training allocation."""
    if params is None:
        params = ModelParameters()

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(11, 4.5))

    # Panel A: Quality dynamics for different training fractions
    m = NFirmModel(params, n_firms=3)
    periods = 20
    for theta in [0.1, 0.2, 0.3, 0.4]:
        q = m.quality_dynamics(K=5.0, training_fraction=theta, periods=periods)
        ax1.plot(
            range(periods + 1),
            q,
            linewidth=2,
            label=f"$\\theta={theta}$",
        )

    ax1.set_xlabel("Period")
    ax1.set_ylabel("Quality level $q$")
    ax1.set_title("(A) Quality Dynamics")
    ax1.legend()

    # Panel B: Optimal training fraction vs capacity
    K_vals = np.linspace(1.0, 10.0, 20)
    opt_thetas = []
    for K in K_vals:
        theta = m.optimal_training_fraction(
            K=K, X=1.0, competitor_capacities=[1.0, 1.0], regime="H"
        )
        opt_thetas.append(theta)

    ax2.plot(K_vals, opt_thetas, "b-", linewidth=2)
    ax2.set_xlabel("Total capacity $K$")
    ax2.set_ylabel(r"Optimal training fraction $\theta^*$")
    ax2.set_title("(B) Optimal Training Allocation")

    fig.suptitle("Training vs. Inference Allocation", fontsize=14)
    plt.tight_layout()

    if output_dir is not None:
        output_dir.mkdir(parents=True, exist_ok=True)
        fig.savefig(output_dir / "phase3_training_inference.pdf")
        fig.savefig(output_dir / "phase3_training_inference.png")

    return fig


def plot_market_structure(
    params: ModelParameters | None = None,
    output_dir: Path | None = None,
) -> plt.Figure:
    """Show market shares and total capacity vs number of firms."""
    if params is None:
        params = ModelParameters()

    n_range = range(2, 6)
    total_caps = []
    total_investments = []
    leader_shares = []

    for n in n_range:
        m = NFirmModel(params, n_firms=n, leverage=0.0)
        eq = m.solve_sequential_equilibrium("H")
        total_caps.append(sum(e["K_capacity"] for e in eq))
        total_investments.append(sum(e["investment_cost"] for e in eq))
        leader_shares.append(eq[0]["market_share"])

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(11, 4.5))

    ax1.bar(list(n_range), total_caps, color="steelblue", alpha=0.8)
    ax1.set_xlabel("Number of firms")
    ax1.set_ylabel("Total industry capacity")
    ax1.set_title("(A) Total Capacity")

    ax2.plot(list(n_range), leader_shares, "bo-", linewidth=2, markersize=8)
    ax2.set_xlabel("Number of firms")
    ax2.set_ylabel("Leader market share")
    ax2.set_title("(B) Leader's Market Share")
    ax2.set_ylim(0, 1)

    fig.suptitle("Market Structure and Competition", fontsize=14)
    plt.tight_layout()

    if output_dir is not None:
        output_dir.mkdir(parents=True, exist_ok=True)
        fig.savefig(output_dir / "phase3_market_structure.pdf")
        fig.savefig(output_dir / "phase3_market_structure.png")

    return fig


def generate_all_phase3_figures(
    params: ModelParameters | None = None,
    output_dir: Path | None = None,
) -> list[plt.Figure]:
    """Generate all Phase 3 figures."""
    figs = [
        plot_sequential_equilibrium(params, output_dir),
        plot_nfirm_comparative_statics(params, output_dir),
        plot_training_inference(params, output_dir),
        plot_market_structure(params, output_dir),
    ]
    plt.close("all")
    return figs
