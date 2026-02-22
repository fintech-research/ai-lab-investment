"""Publication-quality figures for Phase 2: duopoly with default risk.

Generates figures showing the preemption equilibrium, leader-follower
dynamics, default boundaries, and the competition-leverage spiral.
"""

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

from ..models.duopoly import DuopolyModel
from ..models.parameters import ModelParameters

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


def plot_leader_follower_triggers(
    params: ModelParameters | None = None,
    output_dir: Path | None = None,
) -> plt.Figure:
    """Compare leader and follower triggers across volatility.

    Shows that preemption pushes the leader to invest earlier,
    with the gap widening as volatility increases.
    """
    if params is None:
        params = ModelParameters()

    sigma_vals = np.linspace(0.20, 0.50, 25)
    model = DuopolyModel(params, leverage=0.0)
    stats = model.comparative_statics("sigma_H", sigma_vals, regime="H")
    valid = stats["has_solution"]

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(11, 4.5))

    # Panel A: Triggers
    ax1.plot(
        stats["param_values"][valid],
        stats["X_leader"][valid],
        "b-",
        linewidth=2,
        label="Leader $X_L^*$",
    )
    ax1.plot(
        stats["param_values"][valid],
        stats["X_follower"][valid],
        "r--",
        linewidth=2,
        label="Follower $X_F^*$",
    )
    ax1.set_xlabel(r"Volatility $\sigma_H$")
    ax1.set_ylabel("Investment trigger")
    ax1.set_title("(A) Investment Triggers")
    ax1.legend()

    # Panel B: Capacities
    ax2.plot(
        stats["param_values"][valid],
        stats["K_leader"][valid],
        "b-",
        linewidth=2,
        label="Leader $K_L^*$",
    )
    ax2.plot(
        stats["param_values"][valid],
        stats["K_follower"][valid],
        "r--",
        linewidth=2,
        label="Follower $K_F^*$",
    )
    ax2.set_xlabel(r"Volatility $\sigma_H$")
    ax2.set_ylabel("Optimal capacity")
    ax2.set_title("(B) Capacities")
    ax2.legend()

    fig.suptitle(
        "Leader vs. Follower: Preemption Equilibrium (All-Equity)",
        fontsize=14,
    )
    plt.tight_layout()

    if output_dir is not None:
        output_dir.mkdir(parents=True, exist_ok=True)
        fig.savefig(output_dir / "phase2_leader_follower_triggers.pdf")
        fig.savefig(output_dir / "phase2_leader_follower_triggers.png")

    return fig


def plot_leverage_effect(
    params: ModelParameters | None = None,
    output_dir: Path | None = None,
) -> plt.Figure:
    """Show how leverage affects equilibrium triggers and default boundaries.

    Key figure: demonstrates the competition-leverage spiral.
    """
    if params is None:
        params = ModelParameters()

    leverage_vals = np.linspace(0.0, 0.70, 25)
    n = len(leverage_vals)

    X_leader = np.full(n, np.nan)
    X_follower = np.full(n, np.nan)
    K_leader = np.full(n, np.nan)
    K_follower = np.full(n, np.nan)
    X_def_leader = np.full(n, np.nan)
    X_def_follower = np.full(n, np.nan)
    valid = np.zeros(n, dtype=bool)

    for i, lev in enumerate(leverage_vals):
        try:
            m = DuopolyModel(
                params, leverage=lev, coupon_rate=0.05, bankruptcy_cost=0.30
            )
            eq = m.solve_preemption_equilibrium("H")
            X_leader[i] = eq["X_leader"]
            X_follower[i] = eq["X_follower"]
            K_leader[i] = eq["K_leader"]
            K_follower[i] = eq["K_follower"]
            X_def_leader[i] = eq["X_default_leader"]
            X_def_follower[i] = eq["X_default_follower"]
            valid[i] = True
        except (ValueError, RuntimeError):
            continue

    fig, axes = plt.subplots(1, 3, figsize=(14, 4.5))

    # Panel A: Investment triggers
    axes[0].plot(
        leverage_vals[valid], X_leader[valid], "b-", linewidth=2, label="Leader $X_L^*$"
    )
    axes[0].plot(
        leverage_vals[valid],
        X_follower[valid],
        "r--",
        linewidth=2,
        label="Follower $X_F^*$",
    )
    axes[0].set_xlabel("Leverage (D/I)")
    axes[0].set_ylabel("Investment trigger")
    axes[0].set_title("(A) Investment Triggers")
    axes[0].legend()

    # Panel B: Capacities
    axes[1].plot(
        leverage_vals[valid], K_leader[valid], "b-", linewidth=2, label="Leader $K_L^*$"
    )
    axes[1].plot(
        leverage_vals[valid],
        K_follower[valid],
        "r--",
        linewidth=2,
        label="Follower $K_F^*$",
    )
    axes[1].set_xlabel("Leverage (D/I)")
    axes[1].set_ylabel("Optimal capacity")
    axes[1].set_title("(B) Capacities")
    axes[1].legend()

    # Panel C: Default boundaries
    has_default = valid & (X_def_follower > 0)
    if has_default.sum() > 0:
        axes[2].plot(
            leverage_vals[has_default],
            X_def_leader[has_default],
            "b-",
            linewidth=2,
            label="Leader $X_D^L$",
        )
        axes[2].plot(
            leverage_vals[has_default],
            X_def_follower[has_default],
            "r--",
            linewidth=2,
            label="Follower $X_D^F$",
        )
    axes[2].set_xlabel("Leverage (D/I)")
    axes[2].set_ylabel("Default boundary")
    axes[2].set_title("(C) Default Boundaries")
    axes[2].legend()

    fig.suptitle("The Competition-Leverage Spiral", fontsize=14)
    plt.tight_layout()

    if output_dir is not None:
        output_dir.mkdir(parents=True, exist_ok=True)
        fig.savefig(output_dir / "phase2_leverage_effect.pdf")
        fig.savefig(output_dir / "phase2_leverage_effect.png")

    return fig


def plot_competition_vs_monopoly(
    params: ModelParameters | None = None,
    output_dir: Path | None = None,
) -> plt.Figure:
    """Compare duopoly equilibrium to single-firm (monopoly) solution.

    Shows the preemption effect: competition lowers the leader's trigger
    relative to the single-firm benchmark.
    """
    if params is None:
        params = ModelParameters()

    from ..models.base_model import SingleFirmModel

    sigma_vals = np.linspace(0.20, 0.50, 25)
    n = len(sigma_vals)

    X_mono = np.full(n, np.nan)
    X_leader = np.full(n, np.nan)
    X_follower = np.full(n, np.nan)
    valid = np.zeros(n, dtype=bool)

    for i, sig in enumerate(sigma_vals):
        try:
            p = params.with_param(sigma_H=sig)
            sm = SingleFirmModel(p)
            X_m, _ = sm.optimal_trigger_and_capacity("H")
            X_mono[i] = X_m

            dm = DuopolyModel(p, leverage=0.0)
            eq = dm.solve_preemption_equilibrium("H")
            X_leader[i] = eq["X_leader"]
            X_follower[i] = eq["X_follower"]
            valid[i] = True
        except (ValueError, RuntimeError):
            continue

    fig, ax = plt.subplots(figsize=(8, 5))

    ax.plot(
        sigma_vals[valid],
        X_mono[valid],
        "k-",
        linewidth=2,
        label="Single firm $X^*$ (Phase 1)",
    )
    ax.plot(
        sigma_vals[valid],
        X_leader[valid],
        "b--",
        linewidth=2,
        label="Duopoly leader $X_L^*$",
    )
    ax.plot(
        sigma_vals[valid],
        X_follower[valid],
        "r:",
        linewidth=2,
        label="Duopoly follower $X_F^*$",
    )
    ax.set_xlabel(r"Volatility $\sigma_H$")
    ax.set_ylabel("Investment trigger")
    ax.set_title("Preemption Effect: Competition Lowers the Leader's Trigger")
    ax.legend()

    plt.tight_layout()

    if output_dir is not None:
        output_dir.mkdir(parents=True, exist_ok=True)
        fig.savefig(output_dir / "phase2_competition_vs_monopoly.pdf")
        fig.savefig(output_dir / "phase2_competition_vs_monopoly.png")

    return fig


def plot_default_and_investment(
    params: ModelParameters | None = None,
    output_dir: Path | None = None,
) -> plt.Figure:
    """Show investment triggers and default boundaries in (X, leverage) space.

    Illustrates the region where firms invest but then default if demand falls.
    """
    if params is None:
        params = ModelParameters()

    leverage_vals = np.linspace(0.05, 0.65, 20)
    n = len(leverage_vals)

    X_leader = np.full(n, np.nan)
    X_follower = np.full(n, np.nan)
    X_def_F = np.full(n, np.nan)
    valid = np.zeros(n, dtype=bool)

    for i, lev in enumerate(leverage_vals):
        try:
            m = DuopolyModel(
                params, leverage=lev, coupon_rate=0.05, bankruptcy_cost=0.30
            )
            eq = m.solve_preemption_equilibrium("H")
            X_leader[i] = eq["X_leader"]
            X_follower[i] = eq["X_follower"]
            X_def_F[i] = eq["X_default_follower"]
            valid[i] = True
        except (ValueError, RuntimeError):
            continue

    fig, ax = plt.subplots(figsize=(8, 5))

    ax.plot(
        leverage_vals[valid],
        X_follower[valid],
        "r-",
        linewidth=2,
        label="$X_F^*$ (invest)",
    )
    ax.plot(
        leverage_vals[valid],
        X_leader[valid],
        "b-",
        linewidth=2,
        label="$X_L^*$ (invest)",
    )
    has_def = valid & (X_def_F > 0)
    if has_def.sum() > 0:
        ax.plot(
            leverage_vals[has_def],
            X_def_F[has_def],
            "k--",
            linewidth=2,
            label="$X_D$ (default)",
        )
        # Shade the region between default and investment
        ax.fill_between(
            leverage_vals[has_def],
            X_def_F[has_def],
            X_follower[has_def],
            alpha=0.15,
            color="red",
            label="Operating region (follower)",
        )

    ax.set_xlabel("Leverage (D/I)")
    ax.set_ylabel("Demand level $X$")
    ax.set_title("Investment and Default Boundaries")
    ax.legend(loc="upper left")

    plt.tight_layout()

    if output_dir is not None:
        output_dir.mkdir(parents=True, exist_ok=True)
        fig.savefig(output_dir / "phase2_default_and_investment.pdf")
        fig.savefig(output_dir / "phase2_default_and_investment.png")

    return fig


def plot_lambda_duopoly(
    params: ModelParameters | None = None,
    output_dir: Path | None = None,
) -> plt.Figure:
    """Show how lambda affects the duopoly equilibrium.

    Key insight: higher lambda (more likely regime switch) lowers triggers
    and intensifies competition.
    """
    if params is None:
        params = ModelParameters()

    lam_vals = np.linspace(0.01, 0.50, 25)
    n = len(lam_vals)

    X_leader = np.full(n, np.nan)
    X_follower = np.full(n, np.nan)
    K_leader = np.full(n, np.nan)
    valid = np.zeros(n, dtype=bool)

    for i, lam in enumerate(lam_vals):
        try:
            p = params.with_param(lam=lam)
            m = DuopolyModel(p, leverage=0.0)
            eq = m.solve_preemption_equilibrium("H")
            X_leader[i] = eq["X_leader"]
            X_follower[i] = eq["X_follower"]
            K_leader[i] = eq["K_leader"]
            valid[i] = True
        except (ValueError, RuntimeError):
            continue

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(11, 4.5))

    ax1.plot(
        lam_vals[valid], X_leader[valid], "b-", linewidth=2, label="Leader $X_L^*$"
    )
    ax1.plot(
        lam_vals[valid], X_follower[valid], "r--", linewidth=2, label="Follower $X_F^*$"
    )
    ax1.set_xlabel(r"Regime-switch rate $\lambda$")
    ax1.set_ylabel("Investment trigger")
    ax1.set_title(r"(A) Triggers vs. $\lambda$")
    ax1.legend()

    ax2.plot(lam_vals[valid], K_leader[valid], "b-", linewidth=2)
    ax2.set_xlabel(r"Regime-switch rate $\lambda$")
    ax2.set_ylabel("Leader capacity $K_L^*$")
    ax2.set_title(r"(B) Leader Capacity vs. $\lambda$")

    fig.suptitle("Effect of AI Adoption Rate on Duopoly Equilibrium", fontsize=14)
    plt.tight_layout()

    if output_dir is not None:
        output_dir.mkdir(parents=True, exist_ok=True)
        fig.savefig(output_dir / "phase2_lambda_duopoly.pdf")
        fig.savefig(output_dir / "phase2_lambda_duopoly.png")

    return fig


def generate_all_phase2_figures(
    params: ModelParameters | None = None,
    output_dir: Path | None = None,
) -> list[plt.Figure]:
    """Generate all Phase 2 figures."""
    figs = [
        plot_leader_follower_triggers(params, output_dir),
        plot_leverage_effect(params, output_dir),
        plot_competition_vs_monopoly(params, output_dir),
        plot_default_and_investment(params, output_dir),
        plot_lambda_duopoly(params, output_dir),
    ]
    plt.close("all")
    return figs
