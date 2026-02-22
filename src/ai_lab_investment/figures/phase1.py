"""Publication-quality figures for Phase 1: single-firm base model.

Generates comparative statics plots showing how optimal investment
triggers and capacity respond to key model parameters.
"""

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

from ..models.base_model import SingleFirmModel
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


def plot_comparative_statics_H(
    params: ModelParameters | None = None,
    output_dir: Path | None = None,
) -> plt.Figure:
    """4-panel comparative statics for regime H.

    Shows how trigger and capacity respond to sigma_H, alpha, gamma, and delta.
    """
    if params is None:
        params = ModelParameters()

    model = SingleFirmModel(params)
    fig, axes = plt.subplots(2, 2, figsize=(10, 8))
    fig.suptitle(
        "Comparative Statics: Investment Trigger and Capacity (Regime H)",
        fontsize=14,
    )

    panels = [
        ("sigma_H", np.linspace(0.20, 0.50, 30), r"Volatility $\sigma_H$", "(A)"),
        ("alpha", np.linspace(0.33, 0.47, 30), r"Revenue elasticity $\alpha$", "(B)"),
        ("gamma", np.linspace(1.2, 2.5, 30), r"Cost convexity $\gamma$", "(C)"),
        ("delta", np.linspace(0.01, 0.10, 30), r"Operating cost $\delta$", "(D)"),
    ]

    for idx, (param_name, values, xlabel, panel_label) in enumerate(panels):
        ax = axes[idx // 2, idx % 2]
        stats = model.comparative_statics(param_name, values, regime="H")
        valid = stats["has_trigger"]

        ax.plot(
            stats["param_values"][valid],
            stats["triggers"][valid],
            "b-",
            linewidth=2,
        )
        ax.set_xlabel(xlabel)
        ax.set_ylabel(r"Trigger $X^*_H$", color="b")
        ax.tick_params(axis="y", labelcolor="b")

        ax2 = ax.twinx()
        ax2.plot(
            stats["param_values"][valid],
            stats["capacities"][valid],
            "r--",
            linewidth=2,
        )
        ax2.set_ylabel(r"Capacity $K^*_H$", color="r")
        ax2.tick_params(axis="y", labelcolor="r")
        ax.set_title(f"{panel_label} Effect of {xlabel.split('$')[1].split('$')[0]}")

    plt.tight_layout()

    if output_dir is not None:
        output_dir.mkdir(parents=True, exist_ok=True)
        fig.savefig(output_dir / "phase1_comparative_statics_H.pdf")
        fig.savefig(output_dir / "phase1_comparative_statics_H.png")

    return fig


def plot_option_value_H(
    params: ModelParameters | None = None,
    output_dir: Path | None = None,
) -> plt.Figure:
    """Plot option value and NPV vs demand X for regime H."""
    if params is None:
        params = ModelParameters()

    model = SingleFirmModel(params)
    X_star, K_star = model.optimal_trigger_and_capacity("H")

    X_max = X_star * 3.0
    X_grid = np.linspace(X_star * 0.01, X_max, 300)

    option_vals = model.value_function_numerical(X_grid, "H")
    npv_vals = np.array([
        model.installed_value(x, K_star, "H") - model.investment_cost(K_star)
        for x in X_grid
    ])

    fig, ax = plt.subplots(figsize=(8, 5))

    ax.plot(X_grid, option_vals, "b-", linewidth=2, label="Option value $F_H(X)$")
    ax.plot(X_grid, npv_vals, "r--", linewidth=1.5, label="NPV of investing now")
    ax.axvline(
        X_star,
        color="gray",
        linestyle=":",
        alpha=0.7,
        label=f"Trigger $X^*_H = {X_star:.4f}$",
    )
    ax.axhline(0, color="black", linewidth=0.5, alpha=0.3)
    ax.set_xlabel("Demand level $X$")
    ax.set_ylabel("Value")
    ax.set_title("Option Value vs. NPV of Immediate Investment (Regime H)")
    ax.legend(loc="upper left")
    ax.set_xlim(0, X_max)

    plt.tight_layout()

    if output_dir is not None:
        output_dir.mkdir(parents=True, exist_ok=True)
        fig.savefig(output_dir / "phase1_option_value_H.pdf")
        fig.savefig(output_dir / "phase1_option_value_H.png")

    return fig


def plot_option_value_comparison(
    params: ModelParameters | None = None,
    output_dir: Path | None = None,
) -> plt.Figure:
    """Compare option values in regimes L and H.

    Shows that the regime-L option value (from switching possibility)
    is entirely driven by the H-regime option through coefficient C.
    """
    if params is None:
        params = ModelParameters()

    model = SingleFirmModel(params)
    X_star_H, _ = model.optimal_trigger_and_capacity("H")

    X_grid = np.linspace(X_star_H * 0.01, X_star_H * 3.0, 300)
    F_H = model.value_function_numerical(X_grid, "H")
    F_L = model.value_function_numerical(X_grid, "L")

    fig, ax = plt.subplots(figsize=(8, 5))

    ax.plot(X_grid, F_H, "b-", linewidth=2, label="$F_H(X)$ (post-adoption)")
    ax.plot(X_grid, F_L, "r--", linewidth=2, label="$F_L(X)$ (pre-adoption)")
    ax.axvline(
        X_star_H,
        color="gray",
        linestyle=":",
        alpha=0.7,
        label=f"$X^*_H = {X_star_H:.4f}$",
    )
    ax.set_xlabel("Demand level $X$")
    ax.set_ylabel("Option value")
    ax.set_title("Option Values by Regime")
    ax.legend()
    ax.set_xlim(0, X_star_H * 3)

    plt.tight_layout()

    if output_dir is not None:
        output_dir.mkdir(parents=True, exist_ok=True)
        fig.savefig(output_dir / "phase1_option_comparison.pdf")
        fig.savefig(output_dir / "phase1_option_comparison.png")

    return fig


def plot_lambda_sensitivity(
    params: ModelParameters | None = None,
    output_dir: Path | None = None,
) -> plt.Figure:
    """Show how lambda affects option values and the H-regime trigger.

    This is a key figure for the paper: it shows how the expected
    arrival rate of transformative AI affects investment decisions.
    """
    if params is None:
        params = ModelParameters()

    lam_vals = np.linspace(0.01, 0.50, 30)
    triggers_H = np.full_like(lam_vals, np.nan)
    capacities_H = np.full_like(lam_vals, np.nan)
    C_vals = np.full_like(lam_vals, np.nan)

    for i, lam in enumerate(lam_vals):
        try:
            p = params.with_param(lam=lam)
            m = SingleFirmModel(p)
            X_H, K_H = m.optimal_trigger_and_capacity("H")
            triggers_H[i] = X_H
            capacities_H[i] = K_H
            C_vals[i] = m._particular_solution_coeff()
        except (ValueError, RuntimeError):
            continue

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(11, 4.5))

    valid = ~np.isnan(triggers_H)
    ax1.plot(lam_vals[valid], triggers_H[valid], "b-", linewidth=2)
    ax1.set_xlabel(r"Regime-switch arrival rate $\lambda$")
    ax1.set_ylabel(r"Investment trigger $X^*_H$")
    ax1.set_title("H-Regime Trigger vs. Arrival Rate")

    ax2.plot(lam_vals[valid], C_vals[valid], "r-", linewidth=2)
    ax2.set_xlabel(r"Regime-switch arrival rate $\lambda$")
    ax2.set_ylabel("$C$ (switching value coefficient)")
    ax2.set_title("L-Regime Option Value from Switching")

    plt.tight_layout()

    if output_dir is not None:
        output_dir.mkdir(parents=True, exist_ok=True)
        fig.savefig(output_dir / "phase1_lambda_sensitivity.pdf")
        fig.savefig(output_dir / "phase1_lambda_sensitivity.png")

    return fig


def plot_sample_paths(
    params: ModelParameters | None = None,
    output_dir: Path | None = None,
    n_paths: int = 5,
    T: float = 20.0,
    seed: int = 42,
) -> plt.Figure:
    """Plot sample demand paths with regime H trigger overlaid."""
    if params is None:
        params = ModelParameters()

    model = SingleFirmModel(params)
    rng = np.random.default_rng(seed)
    X_star_H, _ = model.optimal_trigger_and_capacity("H")

    fig, ax = plt.subplots(figsize=(10, 5))

    X0 = X_star_H * 0.3
    colors = plt.cm.Set2(np.linspace(0, 0.8, n_paths))

    for i in range(n_paths):
        path = model.simulate_demand(X0, T, dt=0.01, rng=rng)
        time = path["time"]
        X = path["X"]
        regime = path["regime"]

        # Find regime switch point
        switch_idx = np.argmax(regime == 1) if np.any(regime == 1) else len(regime)

        # Pre-switch (regime L)
        ax.plot(
            time[:switch_idx],
            X[:switch_idx],
            color=colors[i],
            alpha=0.7,
            linewidth=0.8,
        )
        # Post-switch (regime H)
        if switch_idx < len(regime):
            ax.plot(
                time[switch_idx:],
                X[switch_idx:],
                color=colors[i],
                alpha=0.9,
                linewidth=1.2,
                linestyle="-",
            )
            ax.plot(
                time[switch_idx],
                X[switch_idx],
                "o",
                color=colors[i],
                markersize=4,
            )

    ax.axhline(
        X_star_H,
        color="red",
        linestyle="--",
        linewidth=1.5,
        label=f"$X^*_H = {X_star_H:.4f}$",
    )
    ax.set_xlabel("Time (years)")
    ax.set_ylabel("Demand level $X_t$")
    ax.set_title("Sample Demand Paths with Regime Switching")
    ax.legend()
    ax.set_yscale("log")

    plt.tight_layout()

    if output_dir is not None:
        output_dir.mkdir(parents=True, exist_ok=True)
        fig.savefig(output_dir / "phase1_sample_paths.pdf")
        fig.savefig(output_dir / "phase1_sample_paths.png")

    return fig


def generate_all_phase1_figures(
    params: ModelParameters | None = None,
    output_dir: Path | None = None,
) -> list[plt.Figure]:
    """Generate all Phase 1 figures."""
    figs = [
        plot_comparative_statics_H(params, output_dir),
        plot_option_value_H(params, output_dir),
        plot_option_value_comparison(params, output_dir),
        plot_lambda_sensitivity(params, output_dir),
        plot_sample_paths(params, output_dir),
    ]
    plt.close("all")
    return figs
