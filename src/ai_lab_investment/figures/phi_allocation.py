"""Publication-quality figures for training-inference allocation (phi).

Generates figures showing how the optimal training fraction phi*
varies with model parameters, and the effect of endogenous lambda.
"""

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

from ..models.base_model import SingleFirmModel
from ..models.duopoly import DuopolyModel
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


def plot_phi_vs_lambda(
    params: ModelParameters | None = None,
    output_dir: Path | None = None,
) -> plt.Figure:
    """Show how optimal training fraction responds to arrival rate.

    Key insight: higher lambda (stronger belief in AGI) shifts
    allocation toward training, since H-regime values training capacity.
    """
    if params is None:
        params = ModelParameters()

    lam_vals = np.linspace(0.02, 0.80, 30)
    n = len(lam_vals)

    phi_single = np.full(n, np.nan)
    phi_leader = np.full(n, np.nan)
    phi_follower = np.full(n, np.nan)
    valid_single = np.zeros(n, dtype=bool)
    valid_duo = np.zeros(n, dtype=bool)

    for i, lam in enumerate(lam_vals):
        try:
            p = params.with_param(lam=lam)
            model = SingleFirmModel(p)
            _, _, phi = model.optimal_trigger_capacity_phi()
            phi_single[i] = phi
            valid_single[i] = True
        except (ValueError, RuntimeError):
            pass

        try:
            p = params.with_param(lam=lam)
            dm = DuopolyModel(p, leverage=0.0)
            eq = dm.solve_preemption_equilibrium("H")
            phi_leader[i] = eq["phi_leader"]
            phi_follower[i] = eq["phi_follower"]
            valid_duo[i] = True
        except (ValueError, RuntimeError):
            pass

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(11, 4.5))

    # Panel A: Single firm
    ax1.plot(
        lam_vals[valid_single],
        phi_single[valid_single],
        "k-",
        linewidth=2,
        label=r"Single firm $\phi^*$",
    )
    ax1.set_xlabel(r"Arrival rate $\lambda$")
    ax1.set_ylabel(r"Training fraction $\phi^*$")
    ax1.set_title(r"(A) Single Firm: $\phi^*$ vs. $\lambda$")
    ax1.set_ylim(0, 1)
    ax1.legend()

    # Panel B: Duopoly
    ax2.plot(
        lam_vals[valid_duo],
        phi_leader[valid_duo],
        "b-",
        linewidth=2,
        label=r"Leader $\phi_L^*$",
    )
    ax2.plot(
        lam_vals[valid_duo],
        phi_follower[valid_duo],
        "r--",
        linewidth=2,
        label=r"Follower $\phi_F^*$",
    )
    ax2.set_xlabel(r"Arrival rate $\lambda$")
    ax2.set_ylabel(r"Training fraction $\phi^*$")
    ax2.set_title(r"(B) Duopoly: $\phi^*$ vs. $\lambda$")
    ax2.set_ylim(0, 1)
    ax2.legend()

    fig.suptitle(
        "Optimal Training Allocation vs. AI Timeline Beliefs",
        fontsize=14,
    )
    plt.tight_layout()

    if output_dir is not None:
        output_dir.mkdir(parents=True, exist_ok=True)
        fig.savefig(output_dir / "phi_vs_lambda.pdf")
        fig.savefig(output_dir / "phi_vs_lambda.png")

    return fig


def plot_duopoly_phi_equilibrium(
    params: ModelParameters | None = None,
    output_dir: Path | None = None,
) -> plt.Figure:
    """Show phi, triggers, and default boundaries in duopoly equilibrium.

    Four-panel figure showing how the equilibrium changes with lambda.
    """
    if params is None:
        params = ModelParameters()

    lam_vals = np.linspace(0.02, 0.60, 25)
    n = len(lam_vals)

    X_L = np.full(n, np.nan)
    X_F = np.full(n, np.nan)
    K_L = np.full(n, np.nan)
    K_F = np.full(n, np.nan)
    phi_L = np.full(n, np.nan)
    phi_F = np.full(n, np.nan)
    lam_tilde = np.full(n, np.nan)
    valid = np.zeros(n, dtype=bool)

    for i, lam in enumerate(lam_vals):
        try:
            p = params.with_param(lam=lam)
            dm = DuopolyModel(p, leverage=0.0)
            eq = dm.solve_preemption_equilibrium("H")
            X_L[i] = eq["X_leader"]
            X_F[i] = eq["X_follower"]
            K_L[i] = eq["K_leader"]
            K_F[i] = eq["K_follower"]
            phi_L[i] = eq["phi_leader"]
            phi_F[i] = eq["phi_follower"]
            lam_tilde[i] = eq["lambda_tilde"]
            valid[i] = True
        except (ValueError, RuntimeError):
            pass

    fig, axes = plt.subplots(2, 2, figsize=(11, 9))

    # Panel A: Triggers
    axes[0, 0].plot(lam_vals[valid], X_L[valid], "b-", linewidth=2, label="Leader")
    axes[0, 0].plot(lam_vals[valid], X_F[valid], "r--", linewidth=2, label="Follower")
    axes[0, 0].set_ylabel("Investment trigger")
    axes[0, 0].set_title(r"(A) Triggers vs. $\lambda$")
    axes[0, 0].legend()

    # Panel B: Capacities
    axes[0, 1].plot(lam_vals[valid], K_L[valid], "b-", linewidth=2, label="Leader")
    axes[0, 1].plot(lam_vals[valid], K_F[valid], "r--", linewidth=2, label="Follower")
    axes[0, 1].set_ylabel("Capacity $K^*$")
    axes[0, 1].set_title(r"(B) Capacities vs. $\lambda$")
    axes[0, 1].legend()

    # Panel C: Training fractions
    axes[1, 0].plot(lam_vals[valid], phi_L[valid], "b-", linewidth=2, label="Leader")
    axes[1, 0].plot(lam_vals[valid], phi_F[valid], "r--", linewidth=2, label="Follower")
    axes[1, 0].set_xlabel(r"Arrival rate $\lambda$")
    axes[1, 0].set_ylabel(r"Training fraction $\phi^*$")
    axes[1, 0].set_title(r"(C) Training Allocation vs. $\lambda$")
    axes[1, 0].set_ylim(0, 1)
    axes[1, 0].legend()

    # Panel D: Endogenous lambda
    axes[1, 1].plot(lam_vals[valid], lam_tilde[valid], "g-", linewidth=2)
    axes[1, 1].plot(lam_vals[valid], lam_vals[valid], "k:", linewidth=1, alpha=0.5)
    axes[1, 1].set_xlabel(r"Exogenous $\lambda$")
    axes[1, 1].set_ylabel(r"Endogenous $\tilde{\lambda}$")
    axes[1, 1].set_title(r"(D) Endogenous vs. Exogenous $\lambda$")

    fig.suptitle(
        "Duopoly Equilibrium with Training Allocation",
        fontsize=14,
    )
    plt.tight_layout()

    if output_dir is not None:
        output_dir.mkdir(parents=True, exist_ok=True)
        fig.savefig(output_dir / "duopoly_phi_equilibrium.pdf")
        fig.savefig(output_dir / "duopoly_phi_equilibrium.png")

    return fig


def generate_all_phi_figures(
    params: ModelParameters | None = None,
    output_dir: Path | None = None,
) -> list[plt.Figure]:
    """Generate all phi-related figures."""
    figs = [
        plot_phi_vs_lambda(params, output_dir),
        plot_duopoly_phi_equilibrium(params, output_dir),
    ]
    plt.close("all")
    return figs
