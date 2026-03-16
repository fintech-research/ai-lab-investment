"""Create functions for all paper figures (single source of truth).

Each ``create_*`` function builds and returns a
:class:`~matplotlib.figure.Figure`.  Styling (fonts, spines, grid) is
set by the caller via :func:`matplotlib.pyplot.style.context`; these
functions control only figure-specific layout (dimensions, colours,
annotations).

Pipeline figure modules (phase1-phase5) serve separate exploratory
purposes and should NOT be duplicated here.
"""

from __future__ import annotations

import matplotlib.pyplot as plt
import numpy as np

FULL_W = 6.5  # full-column width (inches)
HALF_W = 3.25  # half-column width (inches)


# ── Figure 1: Sample demand paths with regime switching ──────────


def create_sample_paths() -> plt.Figure:
    """Sample demand paths showing L→H regime switch."""
    from ..models.base_model import SingleFirmModel
    from ..models.parameters import ModelParameters

    p = ModelParameters()
    model = SingleFirmModel(p)
    X_star, _ = model.optimal_trigger_and_capacity("H")

    fig, ax = plt.subplots(figsize=(FULL_W, 3.2))
    rng = np.random.default_rng(42)
    colors = ["#1f77b4", "#d62728", "#2ca02c", "#9467bd", "#ff7f0e"]

    for i in range(5):
        sim = model.simulate_demand(X0=X_star * 0.3, T=20, dt=0.005, rng=rng)
        t, X, reg = sim["time"], sim["X"], sim["regime"]
        switch_idx = np.argmax(reg == 1) if (reg == 1).any() else len(reg)
        ax.plot(
            t[:switch_idx],
            X[:switch_idx],
            color=colors[i],
            alpha=0.5,
            linewidth=0.8,
        )
        if switch_idx < len(t):
            ax.plot(
                t[switch_idx - 1 :],
                X[switch_idx - 1 :],
                color=colors[i],
                alpha=0.9,
                linewidth=1.2,
            )
            ax.plot(
                t[switch_idx],
                X[switch_idx],
                "o",
                color=colors[i],
                markersize=3,
                zorder=5,
            )

    ax.axhline(
        X_star,
        color="black",
        linestyle="--",
        linewidth=1.0,
        label=rf"$X_H^* = {X_star:.4f}$",
    )
    ax.set_yscale("log")
    ax.set_xlabel("Time (years)")
    ax.set_ylabel(r"Demand level $X_t$")
    ax.legend(loc="upper left", framealpha=0.9)
    fig.tight_layout()
    return fig


# ── Figure 2: Option value vs NPV of immediate investment ───────


def create_option_value() -> plt.Figure:
    """Option value F_H(X) and NPV with value-of-waiting shading."""
    from ..models.base_model import SingleFirmModel
    from ..models.parameters import ModelParameters

    p = ModelParameters()
    model = SingleFirmModel(p)
    X_star, K_star = model.optimal_trigger_and_capacity("H")

    X_vals = np.linspace(0.001 * X_star, 3.0 * X_star, 300)
    F_H = np.array([model.option_value_H(x) for x in X_vals])
    NPV = np.array([
        model.installed_value(x, K_star, "H") - model.investment_cost(K_star)
        for x in X_vals
    ])

    fig, ax = plt.subplots(figsize=(FULL_W, 3.5))
    ax.plot(X_vals, F_H, "k-", linewidth=1.8, label=r"Option value $F_H(X)$")
    ax.plot(
        X_vals,
        NPV,
        "--",
        color="0.4",
        linewidth=1.3,
        label="NPV of immediate investment",
    )
    ax.axvline(X_star, color="0.6", linestyle=":", linewidth=0.8)
    ax.annotate(
        r"$X_H^*$",
        xy=(X_star, 0),
        xytext=(X_star * 1.08, max(F_H) * 0.15),
        fontsize="small",
        color="0.4",
    )

    mask = X_vals < X_star
    ax.fill_between(X_vals[mask], NPV[mask], F_H[mask], alpha=0.12, color="steelblue")
    ax.text(
        X_star * 0.3,
        max(F_H) * 0.12,
        "Value of\nwaiting",
        fontsize="x-small",
        color="steelblue",
        ha="center",
    )

    ax.set_xlabel(r"Demand level $X$")
    ax.set_ylabel("Value")
    ax.legend(loc="upper left", framealpha=0.9)
    ax.set_xlim(0, X_vals[-1])
    ax.set_ylim(bottom=min(0, NPV.min() * 1.1))
    fig.tight_layout()
    return fig


# ── Figure 3: Comparative statics (4 panels) ────────────────────


def create_comparative_statics() -> plt.Figure:
    """4-panel comparative statics for H-regime trigger and capacity."""
    from ..models.base_model import SingleFirmModel
    from ..models.parameters import ModelParameters

    p = ModelParameters()

    panels = [
        ("sigma", np.linspace(0.18, 0.32, 40), r"Volatility $\sigma$"),
        ("alpha", np.linspace(0.30, 0.45, 40), r"Revenue elasticity $\alpha$"),
        ("gamma", np.linspace(1.2, 2.0, 40), r"Cost convexity $\gamma$"),
        ("delta", np.linspace(0.01, 0.08, 40), r"Operating cost $\delta$"),
    ]

    fig, axes = plt.subplots(2, 2, figsize=(FULL_W, 4.5))
    labels = ["(a)", "(b)", "(c)", "(d)"]

    for idx, (param_name, values, xlabel) in enumerate(panels):
        ax = axes[idx // 2, idx % 2]
        model = SingleFirmModel(p)
        result = model.comparative_statics(param_name, values, "H")
        v = result["has_trigger"]

        ax.plot(
            result["param_values"][v],
            result["triggers"][v],
            "k-",
            linewidth=1.5,
            label=r"Trigger $X_H^*$",
        )
        ax2 = ax.twinx()
        ax2.spines["right"].set_visible(True)
        ax2.plot(
            result["param_values"][v],
            result["capacities"][v],
            "--",
            color="0.45",
            linewidth=1.3,
            label=r"Capacity $K_H^*$",
        )
        ax.set_xlabel(xlabel)
        if idx % 2 == 0:
            ax.set_ylabel(r"$X_H^*$")
        if idx % 2 == 1:
            ax2.set_ylabel(r"$K_H^*$", color="0.45")
        ax.set_title(labels[idx], loc="left", fontweight="bold")

        lines1, labs1 = ax.get_legend_handles_labels()
        lines2, labs2 = ax2.get_legend_handles_labels()
        if idx == 0:
            ax.legend(lines1 + lines2, labs1 + labs2, loc="upper left")
        ax2.spines["top"].set_visible(False)

    fig.tight_layout()
    return fig


# ── Figure 4: Regime switch value vs lambda ──────────────────────


def create_lambda_option_value() -> plt.Figure:
    """Two-panel: F_L vs lambda and switching coefficient C vs lambda."""
    from ..models.base_model import SingleFirmModel
    from ..models.parameters import ModelParameters

    lam_vals = np.linspace(0.01, 0.80, 60)
    X_ref = 0.01

    F_L_vals = np.full_like(lam_vals, np.nan)
    F_H_vals = np.full_like(lam_vals, np.nan)
    C_vals = np.full_like(lam_vals, np.nan)

    for i, lam in enumerate(lam_vals):
        try:
            p = ModelParameters(lam=lam)
            model = SingleFirmModel(p)
            F_L_vals[i] = model.option_value_L(X_ref)
            F_H_vals[i] = model.option_value_H(X_ref)
            C_vals[i] = model._particular_solution_coeff()
        except (ValueError, RuntimeError):
            continue

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(FULL_W, 3.2))

    valid = ~np.isnan(F_L_vals)
    ax1.plot(
        lam_vals[valid],
        F_L_vals[valid],
        "k-",
        linewidth=1.5,
        label=r"$F_L(X)$ (pre-adoption)",
    )
    ax1.axhline(
        F_H_vals[0],
        color="0.5",
        linestyle="--",
        linewidth=1.0,
        label=r"$F_H(X)$ (post-adoption)",
    )
    ax1.set_xlabel(r"Arrival rate $\lambda$ (yr$^{-1}$)")
    ax1.set_ylabel(f"Option value at $X={X_ref}$")
    ax1.legend()
    ax1.set_title("(a)", loc="left", fontweight="bold")

    valid_c = ~np.isnan(C_vals)
    ax2.plot(lam_vals[valid_c], C_vals[valid_c], "k-", linewidth=1.5)
    ax2.set_xlabel(r"Arrival rate $\lambda$ (yr$^{-1}$)")
    ax2.set_ylabel(r"Switching value coefficient $C$")
    ax2.set_title("(b)", loc="left", fontweight="bold")

    fig.tight_layout()
    return fig


# ── Figure 5: Investment and default boundaries ──────────────────


def create_default_boundaries() -> plt.Figure:
    """Follower trigger, leader trigger, and default boundary vs leverage."""
    from ..models.duopoly import DuopolyModel
    from ..models.parameters import ModelParameters

    p = ModelParameters()
    leverages = np.linspace(0.05, 0.65, 40)
    X_F = np.full_like(leverages, np.nan)
    X_L = np.full_like(leverages, np.nan)
    X_D = np.full_like(leverages, np.nan)

    for i, lev in enumerate(leverages):
        try:
            duo = DuopolyModel(p, leverage=lev, coupon_rate=0.05, bankruptcy_cost=0.30)
            eq = duo.solve_preemption_equilibrium("H")
            X_F[i] = eq["X_follower"]
            X_L[i] = eq["X_leader"]
            X_D[i] = eq["X_default_follower"]
        except (ValueError, RuntimeError):
            continue

    fig, ax = plt.subplots(figsize=(FULL_W, 3.8))
    valid = ~np.isnan(X_F)

    ax.fill_between(
        leverages[valid],
        X_D[valid],
        X_F[valid],
        alpha=0.15,
        color="steelblue",
        label="Operating region",
    )
    ax.plot(
        leverages[valid],
        X_F[valid],
        "k-",
        linewidth=1.5,
        label=r"Follower trigger $X_F^*$",
    )
    ax.plot(
        leverages[valid],
        X_D[valid],
        "k--",
        linewidth=1.3,
        label=r"Default boundary $X_D$",
    )
    ax.plot(
        leverages[valid],
        X_L[valid],
        "-",
        color="0.5",
        linewidth=1.0,
        label=r"Leader trigger $X_P$",
    )

    ax.set_xlabel("Leverage (D/I)")
    ax.set_ylabel(r"Demand level $X$")
    ax.legend(loc="center left", framealpha=0.9)
    fig.tight_layout()
    return fig


# ── Figure 6: Credit risk ────────────────────────────────────────


def create_credit_risk() -> plt.Figure:
    """Two-panel: credit spread and default probability vs leverage.

    Delegates to ValuationAnalysis.credit_spread_curve().
    """
    from ..models import ModelParameters, ValuationAnalysis

    p = ModelParameters()
    va = ValuationAnalysis(p)

    leverages = np.linspace(0.05, 0.70, 30)
    result = va.credit_spread_curve(leverages)

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(FULL_W, 3.2))

    valid_s = ~np.isnan(result["credit_spread"])
    if valid_s.sum() > 0:
        ax1.plot(
            result["leverage"][valid_s],
            result["credit_spread"][valid_s] * 10_000,
            "k-",
            linewidth=1.5,
        )
    ax1.set_xlabel("Leverage (D/I)")
    ax1.set_ylabel("Credit spread (bps)")
    ax1.set_title("(a)", loc="left", fontweight="bold")

    valid_d = ~np.isnan(result["default_probability"])
    if valid_d.sum() > 0:
        ax2.plot(
            result["leverage"][valid_d],
            result["default_probability"][valid_d] * 100,
            "k-",
            linewidth=1.5,
        )
    ax2.set_xlabel("Leverage (D/I)")
    ax2.set_ylabel("5-year default probability (%)")
    ax2.set_title("(b)", loc="left", fontweight="bold")

    fig.tight_layout()
    return fig


# ── Figure 7: Competition effect ─────────────────────────────────


def create_competition_effect() -> plt.Figure:
    """Single-panel: monopolist vs duopoly leader triggers over sigma."""
    from ..models.duopoly import DuopolyModel
    from ..models.parameters import ModelParameters

    p = ModelParameters()
    sigmas = np.linspace(0.18, 0.30, 30)

    mono_trig = np.full_like(sigmas, np.nan)
    leader_trig = np.full_like(sigmas, np.nan)

    for i, s in enumerate(sigmas):
        try:
            ps = p.with_param(sigma=s)
            duo = DuopolyModel(ps, leverage=0.0)
            eq = duo.solve_preemption_equilibrium("H")
            mono_trig[i] = eq["X_leader_monopolist"]
            leader_trig[i] = eq["X_leader"]
        except (ValueError, RuntimeError):
            pass

    fig, ax = plt.subplots(1, 1, figsize=(HALF_W, 3.2))

    v_m = ~np.isnan(mono_trig)
    v_l = ~np.isnan(leader_trig)
    ax.plot(sigmas[v_m], mono_trig[v_m], "k-", linewidth=1.5, label="Monopolist")
    ax.plot(
        sigmas[v_l],
        leader_trig[v_l],
        "--",
        color="0.35",
        linewidth=1.3,
        label="Duopoly leader",
    )
    ax.set_xlabel(r"Volatility $\sigma$")
    ax.set_ylabel(r"Investment trigger $X^*$")
    ax.legend()

    fig.tight_layout()
    return fig


# ── Figure 8: Firm comparison (calibration) ──────────────────────


def create_firm_comparison() -> plt.Figure:
    """Two-panel: CapEx intensity (broken y-axis) and growth-vs-leverage scatter."""
    from ..calibration.data import get_baseline_calibration

    calib = get_baseline_calibration()
    firms = calib.firms

    names = [f.name.split("(")[1].rstrip(")") for f in firms]
    capex_int = [f.capex_2025 / f.revenue_2025 for f in firms]
    rev_growth = [f.revenue_2025 / f.revenue_2024 for f in firms]
    leverages = [f.leverage_ratio for f in firms]

    colors = ["#1f77b4", "#ff7f0e", "#2ca02c", "#d62728"]
    x = np.arange(len(names))

    # Panel (a): broken y-axis bar chart for CapEx/Revenue
    # Upper segment shows the xAI outlier; lower segment shows the cluster
    fig = plt.figure(figsize=(FULL_W, 3.2))
    gs = fig.add_gridspec(2, 2, height_ratios=[1, 2.5], hspace=0.08, wspace=0.35)
    ax_top = fig.add_subplot(gs[0, 0])
    ax_bot = fig.add_subplot(gs[1, 0])
    ax2 = fig.add_subplot(gs[:, 1])

    for ax in (ax_top, ax_bot):
        ax.bar(x, capex_int, color=colors, edgecolor="0.3", width=0.55)
        ax.set_xticks(x)

    # Upper axis: show the outlier region
    ax_top.set_ylim(18, 22)
    ax_top.set_xticklabels([])
    ax_top.tick_params(bottom=False)
    ax_top.set_title("(a)", loc="left", fontweight="bold")

    # Lower axis: show the cluster
    ax_bot.set_ylim(0, 3)
    ax_bot.set_xticklabels(names, rotation=15, ha="right", fontsize="small")
    ax_bot.axhline(1.0, color="0.6", linestyle=":", linewidth=0.7)

    # Hide spines at the break
    ax_top.spines["bottom"].set_visible(False)
    ax_bot.spines["top"].set_visible(False)
    ax_top.tick_params(bottom=False)

    # Draw break marks
    d = 0.012
    kw = {"transform": ax_top.transAxes, "color": "k", "clip_on": False, "lw": 0.8}
    ax_top.plot((-d, +d), (-d, +d), **kw)
    ax_top.plot((1 - d, 1 + d), (-d, +d), **kw)
    kw = {"transform": ax_bot.transAxes, "color": "k", "clip_on": False, "lw": 0.8}
    ax_bot.plot((-d, +d), (1 - d, 1 + d), **kw)
    ax_bot.plot((1 - d, 1 + d), (1 - d, 1 + d), **kw)

    # Shared y-label
    fig.text(0.01, 0.5, "CapEx / Revenue (2025)", va="center", rotation="vertical")

    # Panel (b): scatter plot (unchanged)
    for i, name in enumerate(names):
        ax2.scatter(
            rev_growth[i],
            leverages[i],
            s=100,
            c=colors[i],
            edgecolors="0.3",
            zorder=5,
        )
        ax2.annotate(
            name,
            (rev_growth[i], leverages[i]),
            textcoords="offset points",
            xytext=(8, 4),
            fontsize="small",
        )
    ax2.set_xlabel("Revenue growth (2024-2025x)")
    ax2.set_ylabel("Leverage ratio")
    ax2.set_title("(b)", loc="left", fontweight="bold")

    return fig


# ── Figure 9: Lambda interpretation (timeline) ──────────────────


def create_lambda_timeline() -> plt.Figure:
    """Two-panel: expected years and 5-year switch probability vs lambda."""
    lam = np.linspace(0.05, 1.0, 100)
    expected_years = 1.0 / lam
    prob_5yr = (1 - np.exp(-lam * 5)) * 100

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(FULL_W, 3.2))

    ax1.plot(lam, expected_years, "k-", linewidth=1.5)
    ax1.set_xlabel(r"Arrival rate $\lambda$ (yr$^{-1}$)")
    ax1.set_ylabel("Expected years to regime switch")
    ax1.set_ylim(0, 22)
    ax1.set_title("(a)", loc="left", fontweight="bold")

    ax2.plot(lam, prob_5yr, "k-", linewidth=1.5)
    ax2.set_xlabel(r"Arrival rate $\lambda$ (yr$^{-1}$)")
    ax2.set_ylabel("Prob. of switch within 5 years (%)")
    ax2.set_title("(b)", loc="left", fontweight="bold")

    fig.tight_layout()
    return fig


# ── Figure 10: Value decomposition ────────────────────────────────


def create_growth_decomposition() -> plt.Figure:
    """Two-panel: value decomposition and capacity gap fraction.

    Uses the phi-aware model (optimal_trigger_capacity_phi,
    installed_value_with_phi) matching Phase 1 corrections.
    """
    from ..models.base_model import SingleFirmModel
    from ..models.parameters import ModelParameters

    p = ModelParameters()
    model = SingleFirmModel(p)
    X_star, K_star, phi_star = model.optimal_trigger_capacity_phi()

    K_fracs = np.linspace(0.01, 1.5, 40)
    assets = np.full_like(K_fracs, np.nan)
    counterfactual = np.full_like(K_fracs, np.nan)

    X_eval = 1.5 * X_star
    V_optimal = model.installed_value_with_phi(X_eval, phi_star, K_star, "L")
    I_optimal = model.investment_cost(K_star)
    npv_optimal = V_optimal - I_optimal

    for i, kr in enumerate(K_fracs):
        K_inst = kr * K_star
        assets[i] = model.installed_value_with_phi(X_eval, phi_star, K_inst, "L")
        counterfactual[i] = max(npv_optimal - assets[i], 0)

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(FULL_W, 3.2))

    ax1.fill_between(
        K_fracs, 0, assets, alpha=0.4, color="#1f77b4", label="Assets-in-place"
    )
    ax1.fill_between(
        K_fracs,
        assets,
        assets + counterfactual,
        alpha=0.4,
        color="#ff7f0e",
        label="Capacity gap value",
    )
    ax1.axvline(1.0, color="0.5", linestyle=":", linewidth=0.8)
    ax1.set_xlabel(r"Installed capacity ($K / K_H^*$)")
    ax1.set_ylabel("Value")
    ax1.legend(loc="lower right")
    ax1.set_title("(a)", loc="left", fontweight="bold")

    total = assets + counterfactual
    growth_frac = np.where(total > 0, counterfactual / total * 100, 0)
    ax2.plot(K_fracs, growth_frac, "k-", linewidth=1.5)
    ax2.set_xlabel(r"Installed capacity ($K / K_H^*$)")
    ax2.set_ylabel("Capacity gap fraction (%)")
    ax2.set_ylim(0, 105)
    ax2.set_title("(b)", loc="left", fontweight="bold")

    fig.tight_layout()
    return fig


# ── Figure 11: Dario's Dilemma ───────────────────────────────────


def create_investment_dilemma() -> plt.Figure:
    """Value loss from belief mismatch (unleveraged and leveraged).

    Delegates to ValuationAnalysis.dario_dilemma() and
    dario_dilemma_leveraged(), matching Phase 1 corrections.
    """
    from ..models import ModelParameters, ValuationAnalysis

    p = ModelParameters()
    va = ValuationAnalysis(p)

    fixed_true = 0.10
    lam_range = np.linspace(0.005, 0.50, 40)

    losses_unlev = []
    for li in lam_range:
        r = va.dario_dilemma(fixed_true, li)
        losses_unlev.append(r.get("value_loss_pct", np.nan) * 100)

    losses_lev = []
    for li in lam_range:
        r = va.dario_dilemma_leveraged(fixed_true, li, leverage=0.40)
        losses_lev.append(r.get("value_loss_pct", np.nan) * 100)

    fig, ax = plt.subplots(figsize=(FULL_W, 3.8))

    losses_unlev_arr = np.array(losses_unlev)
    losses_lev_arr = np.array(losses_lev)

    ax.plot(lam_range, losses_unlev_arr, "k-", linewidth=1.5, label=r"$\ell = 0$")
    ax.plot(lam_range, losses_lev_arr, "k--", linewidth=1.5, label=r"$\ell = 0.40$")

    ax.axvline(fixed_true, color="0.6", linestyle=":", linewidth=0.8)

    high_loss = losses_unlev_arr > 10
    if high_loss.any():
        ax.fill_between(
            lam_range,
            0,
            losses_unlev_arr,
            where=high_loss,
            alpha=0.10,
            color="red",
            label="Loss > 10%",
        )

    ax.set_xlabel(r"Investment belief $\lambda_{\mathrm{invest}}$")
    ax.set_ylabel(r"Value loss $\Delta V / V^*$ (%)")
    ax.legend(loc="upper center", framealpha=0.9)
    ax.set_xlim(0, 0.5)
    ax.set_ylim(0, 28)

    ax.annotate(
        "Underinvestment\n(conservative)",
        xy=(0.045, 16),
        fontsize="small",
        ha="left",
        color="navy",
    )
    ax.annotate(
        "Overinvestment\n(aggressive)",
        xy=(0.35, 8),
        fontsize="small",
        ha="center",
        color="darkred",
    )

    fig.tight_layout()
    return fig
