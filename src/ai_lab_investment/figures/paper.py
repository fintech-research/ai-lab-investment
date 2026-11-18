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
from matplotlib import transforms

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
    # Anchor the trigger label to the top of its own vertical line (x in data
    # coordinates, y in axes coordinates) so it reads as a label for the line
    # rather than floating in the middle of the panel.
    ax.text(
        X_star,
        0.02,
        r"$X_H^*$",
        transform=transforms.blended_transform_factory(ax.transData, ax.transAxes),
        fontsize="small",
        color="0.4",
        ha="left",
        va="bottom",
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

    # Grids are restricted to the (A2)-admissible windows at baseline
    # (sigma in ~(0.19, 0.39), alpha in ~(0.36, 0.53), gamma > ~1.13);
    # outside them no interior trigger/capacity exists.
    panels = [
        ("sigma", np.linspace(0.20, 0.32, 40), r"Volatility $\sigma$"),
        ("alpha", np.linspace(0.37, 0.45, 40), r"Revenue elasticity $\alpha$"),
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
        # Label both axes on every panel: the right-hand (capacity) axis of the
        # left-column panels (a) and (c) was previously unlabelled, leaving the
        # dashed series unidentified outside the panel-(a) legend.
        ax.set_ylabel(r"$X_H^*$")
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


def lambda_option_value_curve(
    lam_vals: np.ndarray, X_ref: float = 0.002, pure_power: bool = False
) -> tuple[np.ndarray, np.ndarray, float]:
    """Full-model value of the uninvested firm and allocation across lambda.

    For each lambda the single firm's problem is re-solved and its value is
    read at the common demand level X_ref. By default this is the exact
    value of the model of record (`SingleFirmModel.option_value_with_phi`):
    at low arrival rates X_ref lies above the pre-switch trigger and the
    value is that of investing at once, and above the rate at which the
    trigger ceases to exist it is the value of waiting for the switch.
    ``pure_power=True`` returns the pure-power approximation instead, for
    which X_ref lies below every trigger on the grid.

    Also returns the faith-based survival threshold phi_underbar, which is
    lambda-independent: for a firm that invests, the envelope theorem gives
    dF/dlambda the sign of dA_eff/dlambda at phi*, positive iff
    phi* > phi_underbar, so the value falls in lambda where the optimal
    allocation is too inference-heavy and rises beyond.
    """
    from ..models.base_model import SingleFirmModel
    from ..models.duopoly import DuopolyModel
    from ..models.parameters import ModelParameters

    values = np.full_like(lam_vals, np.nan)
    phis = np.full_like(lam_vals, np.nan)
    for i, lam in enumerate(lam_vals):
        try:
            model = SingleFirmModel(ModelParameters(lam=lam))
            if pure_power:
                values[i] = model.pure_power_option_value(X_ref)
            else:
                values[i] = model.option_value_with_phi(X_ref)
            phis[i] = model.closed_form_phi_star()
        except (ValueError, RuntimeError):
            continue
    phi_underbar = float(DuopolyModel(ModelParameters()).faith_threshold())
    return values, phis, phi_underbar


def create_lambda_option_value() -> plt.Figure:
    """Two-panel: full-model value of the uninvested firm and phi* against lambda.

    Unlike the H-regime illustrations, this figure uses the full model: the
    solid curve is the exact value of the model of record and the dashed
    curve the pure-power approximation. The vertical line marks the arrival
    rate at which phi*(lambda) crosses phi_underbar, the minimum of the
    value in lambda.
    """
    lam_vals = np.linspace(0.005, 0.80, 80)
    X_ref = 0.002
    values, phis, phi_underbar = lambda_option_value_curve(lam_vals, X_ref)
    approx, _, _ = lambda_option_value_curve(lam_vals, X_ref, pure_power=True)
    valid = ~np.isnan(values)
    lam_turn = float(np.interp(phi_underbar, phis[valid], lam_vals[valid]))

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(FULL_W, 3.2))

    ax1.plot(lam_vals[valid], values[valid], "k-", linewidth=1.5, label="Exact")
    ax1.plot(
        lam_vals[valid],
        approx[valid],
        color="0.4",
        linestyle="--",
        linewidth=1.0,
        label="Pure-power approximation",
    )
    ax1.axvline(lam_turn, color="0.5", linestyle=":", linewidth=1.0)
    ax1.set_xlabel(r"Arrival rate $\lambda$ (yr$^{-1}$)")
    ax1.set_ylabel(f"Value $F(X)$ at $X={X_ref}$")
    ax1.legend(loc="lower right", fontsize="x-small", frameon=False)
    ax1.set_title("(a)", loc="left", fontweight="bold")

    ax2.plot(
        lam_vals[valid], phis[valid], "k-", linewidth=1.5, label=r"$\phi^*(\lambda)$"
    )
    ax2.axhline(
        phi_underbar,
        color="0.5",
        linestyle="--",
        linewidth=1.0,
        label=r"faith threshold $\phi$ (Prop. 2)",
    )
    ax2.axvline(lam_turn, color="0.5", linestyle=":", linewidth=1.0)
    ax2.set_xlabel(r"Arrival rate $\lambda$ (yr$^{-1}$)")
    ax2.set_ylabel(r"Optimal training fraction $\phi^*$")
    ax2.set_ylim(0, 1)
    ax2.legend(loc="center right")
    ax2.set_title("(b)", loc="left", fontweight="bold")

    fig.tight_layout()
    return fig


# ── Figure 5: Investment and default boundaries ──────────────────


ROLE_STYLE = {
    "single_firm": ("Single firm", "k"),
    "leader": ("Duopoly leader", "steelblue"),
    "follower": ("Duopoly follower", "0.55"),
}
"""Label and colour of each role in the credit figures."""

DEBT_STYLE = {"par": "-", "fair": "--"}
"""Line style of each debt convention in the credit figures."""


def create_default_boundaries() -> plt.Figure:
    """Entry triggers and boundaries of both duopoly roles against leverage.

    Model of record: the cached equilibria of the exact game at baseline
    (`duopoly.load_equilibrium_grid`), at the leverage levels the cache
    holds, one panel per debt convention. The leader's entry is the first
    investment X_L; its boundary and the follower's are the coupled
    boundaries of the exact claims, at each firm's entry.
    """
    from ..models.duopoly import load_equilibrium_grid

    cells = [
        r
        for r in load_equilibrium_grid()
        if r["scale"] == "envelope" and abs(r["lam"] - 0.10) < 1e-12
    ]
    unlevered = [r for r in cells if r["leverage"] == 0.0]
    if len(unlevered) != 1:
        msg = "Expected one unlevered baseline cell in the equilibrium cache"
        raise RuntimeError(msg)

    fig, axes = plt.subplots(1, 2, figsize=(FULL_W, 3.6), sharey=True)
    for ax, debt, title in zip(
        axes, ("par", "fair"), ("(a) Par debt", "(b) Fairly priced debt"), strict=True
    ):
        rows = sorted(
            unlevered + [r for r in cells if r["leverage"] > 0 and r["debt"] == debt],
            key=lambda r: r["leverage"],
        )
        lev = np.array([r["leverage"] for r in rows])
        X_F = np.array([r["X_F"] for r in rows])
        X_DF = np.array([r["X_D_follower"] for r in rows])
        X_L = np.array([r["X_L"] for r in rows])
        X_DL = np.array([r["X_D_leader"] for r in rows])
        ax.fill_between(lev, X_DF, X_F, alpha=0.12, color="0.5", linewidth=0)
        ax.fill_between(lev, X_DL, X_L, alpha=0.15, color="steelblue", linewidth=0)
        ax.plot(
            lev,
            X_F,
            "k-o",
            linewidth=1.4,
            markersize=3,
            label=r"Follower's trigger $X_F^*$",
        )
        ax.plot(
            lev,
            X_DF,
            "k--o",
            linewidth=1.1,
            markersize=3,
            label=r"Follower's boundary $X_{D,F}$",
        )
        ax.plot(
            lev,
            X_L,
            "-s",
            color="steelblue",
            linewidth=1.4,
            markersize=3,
            label=r"First investment $X_L$",
        )
        ax.plot(
            lev,
            X_DL,
            "-.s",
            color="steelblue",
            linewidth=1.1,
            markersize=3,
            label=r"Leader's boundary $X_{D,L}$",
        )
        ax.set_yscale("log")
        ax.set_xlim(-0.02, 0.67)
        ax.set_xticks(lev)
        ax.set_xticklabels([f"{x:.2f}" for x in lev])
        ax.set_xlabel(r"Leverage $\ell$ (D/I)")
        ax.set_title(title, loc="left", fontweight="bold", fontsize="medium")
    axes[0].set_ylim(4e-4, 0.15)
    axes[0].set_ylabel(r"Demand level $X$ (log scale)")
    handles, labels = axes[0].get_legend_handles_labels()
    fig.legend(
        handles, labels, loc="lower center", ncol=4, fontsize="small", frameon=False
    )
    fig.tight_layout(rect=(0.0, 0.08, 1.0, 1.0))
    return fig


# ── Figure 6: Credit risk ────────────────────────────────────────


def create_credit_risk() -> plt.Figure:
    """Credit spread, default probability and recovery at the model's policies.

    Delegates to `ValuationAnalysis.on_policy_credit` (panels a and b: the
    single firm's precommitted-scale policy, the duopoly's first investment
    and the follower's post-switch entry, across leverage, under both debt
    conventions) and `ValuationAnalysis.credit_phi_profile` (panels c and
    d: the training fraction varied at the single firm's and the leader's
    scale and entry demand, at leverage 0.40).
    """
    from ..models import ModelParameters, ValuationAnalysis

    va = ValuationAnalysis(ModelParameters())
    leverages = tuple(float(x) for x in np.linspace(0.0, 0.70, 29))
    rows = va.on_policy_credit(leverages=leverages)
    phis = np.linspace(0.30, 0.95, 66)
    profiles = {
        debt: va.credit_phi_profile(phis, 0.40, debt) for debt in ("par", "fair")
    }

    fig, axes = plt.subplots(2, 2, figsize=(FULL_W, 5.6))
    (ax_s, ax_p), (ax_r, ax_q) = axes
    for role, (label, colour) in ROLE_STYLE.items():
        for debt, style in DEBT_STYLE.items():
            sel = [r for r in rows if r["role"] == role and r["debt"] == debt]
            lev = np.array([r["leverage"] for r in sel])
            kwargs = {"color": colour, "linestyle": style, "linewidth": 1.4}
            name = label if debt == "par" else None
            ax_s.plot(lev, [1e4 * r["spread"] for r in sel], **kwargs)
            ax_p.plot(
                lev, [100 * r["default_probability"] for r in sel], label=name, **kwargs
            )
    for role in ("single_firm", "leader"):
        label, colour = ROLE_STYLE[role]
        for debt, style in DEBT_STYLE.items():
            prof = profiles[debt][role]
            kwargs = {"color": colour, "linestyle": style, "linewidth": 1.4}
            ax_r.plot(prof["phi"], 100 * prof["recovery_rate"], **kwargs)
            ax_q.plot(prof["phi"], 1e4 * prof["spread"], **kwargs)
        policy = float(profiles["par"][role]["phi_policy"])
        for ax in (ax_r, ax_q):
            ax.axvline(policy, color=colour, linestyle=":", linewidth=0.9)
    ax_p.plot([], [], "k-", linewidth=1.4, label="Par debt")
    ax_p.plot([], [], "k--", linewidth=1.4, label="Fairly priced debt")
    ax_p.legend(loc="upper left", fontsize="x-small", framealpha=0.95)

    ax_s.set_xlabel(r"Leverage $\ell$ (D/I)")
    ax_s.set_ylabel("Spread at entry over $r$ (bps)")
    ax_s.set_ylim(bottom=0)
    ax_p.set_xlabel(r"Leverage $\ell$ (D/I)")
    ax_p.set_ylabel("5-yr default prob., no switch (%)")
    ax_p.set_ylim(bottom=0)
    ax_r.set_xlabel(r"Training fraction $\phi$ (scale fixed)")
    ax_r.set_ylabel(r"Recovery at $\ell = 0.40$ (% of claim)")
    ax_r.set_ylim(bottom=0)
    ax_q.set_xlabel(r"Training fraction $\phi$ (scale fixed)")
    ax_q.set_ylabel(r"Spread at $\ell = 0.40$ (bps)")
    for ax, tag in zip(axes.flat, ("(a)", "(b)", "(c)", "(d)"), strict=True):
        ax.set_title(tag, loc="left", fontweight="bold")
    fig.tight_layout()
    return fig


# ── Figure 7: Competition effect ─────────────────────────────────


def create_competition_effect() -> plt.Figure:
    """Single firm's and duopoly leader's pre-switch triggers over lambda.

    Model of record. The single firm's triggers are solved on the grid; the
    duopoly's first investment X_L (the equilibrium with assigned roles)
    and the rent-equalization trigger X_P above it are read from the cached
    equilibria of the exact game (`duopoly.load_equilibrium_grid`), which
    take a few minutes each to solve.
    """
    from ..models.base_model import SingleFirmModel
    from ..models.duopoly import load_equilibrium_grid
    from ..models.parameters import ModelParameters

    p = ModelParameters()
    lams = np.geomspace(0.03, 0.50, 30)
    unrestricted = np.full_like(lams, np.nan)
    precommitted = np.full_like(lams, np.nan)
    for i, lam in enumerate(lams):
        sol = SingleFirmModel(p.with_param(lam=float(lam))).solve()
        precommitted[i] = sol.precommitted.X_star
        if sol.invests_before_switch:
            unrestricted[i] = sol.X_star

    records = sorted(
        (
            r
            for r in load_equilibrium_grid()
            if r["scale"] == "envelope" and r["leverage"] == 0.0 and r["exists"]
        ),
        key=lambda r: r["lam"],
    )
    lam_duo = np.array([r["lam"] for r in records])
    X_P = np.array([r["X_P"] for r in records])
    X_L = np.array([r["X_L"] for r in records])

    fig, ax = plt.subplots(1, 1, figsize=(1.5 * HALF_W, 3.2))
    top = 0.05
    shown = np.where(unrestricted <= top, unrestricted, np.nan)
    ax.plot(lams, shown, "k-", linewidth=1.5, label="Single firm, scale chosen freely")
    ax.plot(
        lams,
        precommitted,
        ":",
        color="0.45",
        linewidth=1.3,
        label="Single firm, precommitted scale",
    )
    ax.fill_between(lam_duo, X_L, X_P, color="steelblue", alpha=0.12, linewidth=0)
    ax.plot(
        lam_duo,
        X_L,
        "-s",
        color="steelblue",
        linewidth=1.5,
        markersize=3.5,
        label=r"Duopoly, first investment $X_L$",
    )
    ax.plot(
        lam_duo,
        X_P,
        "--o",
        color="0.35",
        linewidth=1.0,
        markersize=2.5,
        label=r"Duopoly, rent equalization $X_P$ (upper bound)",
    )
    ax.axvspan(0.0729, lams[-1], color="0.92", zorder=0)
    ax.text(
        0.2,
        0.03,
        "single firm waits\nfor the switch",
        fontsize="small",
        ha="center",
        va="center",
        color="0.3",
    )
    ax.set_xscale("log")
    ax.set_yscale("log")
    ax.set_xlim(lams[0], lams[-1])
    ax.set_ylim(2e-5, top)
    ax.set_xticks([0.03, 0.05, 0.10, 0.20, 0.50])
    ax.set_xticklabels(["0.03", "0.05", "0.10", "0.20", "0.50"])
    ax.minorticks_off()
    ax.set_xlabel(r"Arrival rate $\lambda$ (yr$^{-1}$)")
    ax.set_ylabel("Pre-switch investment trigger")
    ax.legend(loc="lower center", fontsize="small", framealpha=0.95)

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
    gs = fig.add_gridspec(2, 2, height_ratios=[1, 2.5], hspace=0.08, wspace=0.45)
    ax_top = fig.add_subplot(gs[0, 0])
    ax_bot = fig.add_subplot(gs[1, 0])
    ax2 = fig.add_subplot(gs[:, 1])

    for ax in (ax_top, ax_bot):
        ax.bar(x, capex_int, color=colors, edgecolor="0.3", width=0.55)
        ax.set_xticks(x)

    # Upper axis: show the outlier region
    ax_top.set_ylim(18, 22)
    ax_top.set_yticks([18, 20, 22])
    ax_top.set_xticklabels([])
    ax_top.tick_params(bottom=False)
    ax_top.set_title("(a)", loc="left", fontweight="bold")

    # Lower axis: show the cluster
    ax_bot.set_ylim(0, 3)
    ax_bot.set_yticks([0, 1, 2])
    ax_bot.set_xticklabels(names, rotation=15, ha="right", fontsize="small")
    ax_bot.axhline(1.0, color="0.6", linestyle=":", linewidth=0.7)

    # Hide spines at the break
    ax_top.spines["bottom"].set_visible(False)
    ax_bot.spines["top"].set_visible(False)
    ax_top.tick_params(bottom=False)

    # Draw break marks
    d = 0.012
    for ax_break, ys in ((ax_top, (-d, +d)), (ax_bot, (1 - d, 1 + d))):
        for xs in ((-d, +d), (1 - d, 1 + d)):
            ax_break.plot(
                xs,
                ys,
                transform=ax_break.transAxes,
                color="k",
                clip_on=False,
                lw=0.8,
            )

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
    ax2.set_xlabel("Revenue multiple (2025/2024)")
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


# ── Figure 10: Normalized scale-gap diagnostic ────────────────────


def create_growth_decomposition() -> plt.Figure:
    """Two-panel normalized scale-gap diagnostic.

    Panel (a) stacks assets-in-place and the capacity gap; panel (b)
    plots the scale-gap index g = gap / (assets + gap). This is a
    comparative-statics normalization, not a growth-option
    decomposition: the two components use different benchmarks (gross
    vs. net of sunk cost), so their sum is not firm value.

    Delegates to ValuationAnalysis.capacity_gap_decomposition(), which
    uses the phi-aware model (pure_power_trigger_capacity_phi,
    installed_value_with_phi).
    """
    from ..models import ModelParameters, ValuationAnalysis

    va = ValuationAnalysis(ModelParameters())
    K_fracs = np.linspace(0.01, 1.5, 40)
    decomp = va.capacity_gap_decomposition(K_fracs, demand_multiple=1.5)
    assets = decomp["assets_in_place"]
    counterfactual = decomp["capacity_gap"]
    growth_frac = decomp["gap_fraction"]

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
        label="Capacity gap",
    )
    ax1.axvline(1.0, color="0.5", linestyle=":", linewidth=0.8)
    ax1.set_xlabel(r"Installed capacity ($K / K^*$)")
    ax1.set_ylabel("Normalized value")
    ax1.legend(loc="upper left", fontsize="small", framealpha=0.95)
    ax1.set_title("(a)", loc="left", fontweight="bold")

    ax2.plot(K_fracs, growth_frac, "k-", linewidth=1.5)
    ax2.set_xlabel(r"Installed capacity $K / K^*$")
    ax2.set_ylabel(r"Scale-gap index $g$ (%)")
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

    # Equal additive belief errors (-0.08 / +0.08 around lambda_true)
    matched = [fixed_true - 0.08, fixed_true + 0.08]
    matched_losses = [
        va.dario_dilemma(fixed_true, li)["value_loss_pct"] * 100 for li in matched
    ]
    ax.plot(
        matched,
        matched_losses,
        linestyle="none",
        marker="o",
        markerfacecolor="white",
        markeredgecolor="k",
        markeredgewidth=1.3,
        markersize=7,
        zorder=5,
        label=r"Equal errors $\pm 0.08$ ($\ell = 0$)",
    )

    high_loss = losses_unlev_arr > 10
    if high_loss.any():
        ax.fill_between(
            lam_range,
            0,
            losses_unlev_arr,
            where=high_loss.tolist(),
            alpha=0.10,
            color="red",
            label=r"Loss > 10% ($\ell = 0$ curve)",
        )

    ax.set_xlabel(r"Investment belief $\lambda_{\mathrm{invest}}$")
    ax.set_ylabel(r"Value loss $\Delta V / V^*$ (%)")
    ax.legend(loc="upper center", framealpha=0.9)
    ax.set_xlim(0, 0.5)
    # Dynamic upper limit so the steep underinvestment branch is not clipped
    y_max = np.nanmax([np.nanmax(losses_unlev_arr), np.nanmax(losses_lev_arr)])
    ax.set_ylim(0, 1.1 * y_max)

    ax.annotate(
        "Underinvestment (conservative):\nlater entry, less training",
        xy=(0.045, 16),
        fontsize="small",
        ha="left",
        color="navy",
    )
    ax.annotate(
        "Overinvestment (aggressive):\nearlier entry, more training",
        xy=(0.35, 8),
        fontsize="small",
        ha="center",
        color="darkred",
    )

    fig.tight_layout()
    return fig
