#!/usr/bin/env python3
"""Generate all publication-quality figures for the paper.

Usage:
    uv run python paper/generate_figures.py

Outputs PDF and PNG to paper/figures/.
"""

from pathlib import Path

import matplotlib
import matplotlib.pyplot as plt
import numpy as np

matplotlib.use("Agg")

# ── Publication style (Econometrica / JF) ────────────────────────
plt.rcParams.update({
    "font.family": "serif",
    "font.size": 10,
    "axes.labelsize": 10,
    "axes.titlesize": 10,
    "legend.fontsize": 9,
    "xtick.labelsize": 9,
    "ytick.labelsize": 9,
    "figure.dpi": 300,
    "savefig.dpi": 300,
    "savefig.bbox": "tight",
    "text.usetex": False,
    "axes.spines.top": False,
    "axes.spines.right": False,
    "axes.linewidth": 0.6,
    "xtick.major.width": 0.6,
    "ytick.major.width": 0.6,
    "lines.linewidth": 1.5,
    "axes.grid": False,
})

OUT = Path(__file__).parent / "figures"
FULL_W = 6.5  # full column width in inches


def _save(fig, name):
    OUT.mkdir(parents=True, exist_ok=True)
    fig.savefig(OUT / f"{name}.pdf")
    fig.savefig(OUT / f"{name}.png")
    plt.close(fig)
    print(f"  saved {name}")


# ==================================================================
# Figure 1 -Sample demand paths with regime switching
# ==================================================================
def fig_sample_paths():
    from ai_lab_investment.models import ModelParameters, SingleFirmModel

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
        # Pre-switch
        ax.plot(
            t[:switch_idx], X[:switch_idx], color=colors[i], alpha=0.5, linewidth=0.8
        )
        # Post-switch
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
    _save(fig, "fig_sample_paths")


# ==================================================================
# (Old Figure 2 removed: H-regime option value is 0 under F_H = 0)
# ==================================================================


# ==================================================================
# Figure 3 -Comparative statics (4 panels, restricted ranges)
# ==================================================================
def fig_comparative_statics():
    from ai_lab_investment.models import ModelParameters, SingleFirmModel

    p = ModelParameters()

    panels = [
        ("sigma_H", np.linspace(0.20, 0.34, 40), r"Volatility $\sigma_H$"),
        ("alpha", np.linspace(0.30, 0.45, 40), r"Revenue elasticity $\alpha$"),
        ("gamma", np.linspace(1.2, 2.0, 40), r"Cost convexity $\gamma$"),
        ("delta", np.linspace(0.01, 0.08, 40), r"Depreciation $\delta$"),
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
        ax.set_title(labels[idx], loc="left", fontweight="bold", fontsize=10)

        # Combined legend
        lines1, labs1 = ax.get_legend_handles_labels()
        lines2, labs2 = ax2.get_legend_handles_labels()
        if idx == 0:
            ax.legend(lines1 + lines2, labs1 + labs2, fontsize=8, loc="upper left")
        ax2.spines["top"].set_visible(False)

    plt.tight_layout()
    _save(fig, "fig_comparative_statics")


# ==================================================================
# Figure -L-regime option value vs lambda (under F_H = 0)
# ==================================================================
def fig_lambda_option_value():
    """L-regime option value as a function of arrival rate lambda.

    Under F_H = 0, higher lambda has a dual effect on the trigger:
    1. A_eff channel: higher lambda raises A_eff, lowering the trigger.
    2. Option premium channel: higher lambda raises beta_L^+, pushing
       beta_L^+/(beta_L^+ - 1) toward 1 (value of waiting shrinks).

    Note: This figure requires alpha > 1 - 1/beta_L for interior solution.
    At baseline alpha=0.40, F_L = 0 (no interior capacity). We use
    alpha=0.70 to demonstrate the dual channel mechanism.
    """
    from ai_lab_investment.models import ModelParameters, SingleFirmModel

    lam_vals = np.linspace(0.01, 0.80, 60)
    X_ref = 0.003  # demand level below the trigger

    F_L_vals = np.full_like(lam_vals, np.nan)
    beta_L_vals = np.full_like(lam_vals, np.nan)
    markup_vals = np.full_like(lam_vals, np.nan)

    for i, lam in enumerate(lam_vals):
        try:
            p = ModelParameters(lam=lam, alpha=0.70)
            model = SingleFirmModel(p)
            F_L_vals[i] = model.option_value_L(X_ref)
            beta_L_vals[i] = p.beta_L
            markup_vals[i] = p.beta_L / (p.beta_L - 1.0)
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
    ax1.set_xlabel(r"Arrival rate $\tilde{\lambda}$ (yr$^{-1}$)")
    ax1.set_ylabel(f"Option value at $X={X_ref}$")
    ax1.legend(fontsize=8)
    ax1.set_title("(a)", loc="left", fontweight="bold")

    # Panel (b): option premium (dual channel visualization)
    valid_m = ~np.isnan(markup_vals)
    ax2.plot(
        lam_vals[valid_m],
        markup_vals[valid_m],
        "k-",
        linewidth=1.5,
    )
    ax2.set_xlabel(r"Arrival rate $\tilde{\lambda}$ (yr$^{-1}$)")
    ax2.set_ylabel(r"Option premium $\beta_L^+ / (\beta_L^+ - 1)$")
    ax2.set_title("(b)", loc="left", fontweight="bold")

    plt.tight_layout()
    _save(fig, "fig_lambda_option_value")


# ==================================================================
# Figure 5 -Investment and default boundaries
# ==================================================================
def fig_default_boundaries():
    from ai_lab_investment.models import DuopolyModel, ModelParameters

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
    ax.legend(loc="center left", fontsize=9, framealpha=0.9)
    _save(fig, "fig_default_boundaries")


# ==================================================================
# Figure 6 -Credit risk: spread and default probability
# ==================================================================
def fig_credit_risk():
    """Credit risk vs leverage.

    Evaluate at a fixed demand level chosen so that high-leverage firms
    are close to their default boundary, producing meaningful spread
    variation.  X_eval is set to 2x the default boundary of a firm
    with moderate leverage (0.40), so low-leverage firms are far from
    default and high-leverage firms are near it.
    """
    from scipy.stats import norm

    from ai_lab_investment.models import DuopolyModel, ModelParameters, SingleFirmModel

    p = ModelParameters()
    model = SingleFirmModel(p)
    _, K_star = model.optimal_trigger_and_capacity("H")
    phi_base = 0.30  # baseline training fraction

    # Pick X_eval: 2x the default boundary at moderate leverage
    duo_ref = DuopolyModel(p, leverage=0.40, coupon_rate=0.05, bankruptcy_cost=0.30)
    X_D_ref = duo_ref.default_boundary(phi_base, K_star, 0.0, 0.0)
    X_eval = X_D_ref * 2.0

    leverages = np.linspace(0.05, 0.70, 50)
    spreads = np.full_like(leverages, np.nan)
    def_probs = np.full_like(leverages, np.nan)
    xd_ratio = np.full_like(leverages, np.nan)
    rf = 0.04  # risk-free rate (treasury yield, not WACC)

    for i, lev in enumerate(leverages):
        try:
            duo = DuopolyModel(p, leverage=lev, coupon_rate=0.05, bankruptcy_cost=0.30)
            X_D = duo.default_boundary(phi_base, K_star, 0.0, 0.0)
            if X_D <= 0 or X_eval <= X_D:
                continue

            xd_ratio[i] = X_D / X_eval

            coupon = duo.coupon_payment(K_star)
            D = duo.debt_value(X_eval, phi_base, K_star, 0.0, 0.0)
            if D > 0 and coupon > 0:
                spreads[i] = max(coupon / D - rf, 0.0)

            d2 = (np.log(X_eval / X_D) + (p.mu_H - 0.5 * p.sigma_H**2) * 5) / (
                p.sigma_H * np.sqrt(5)
            )
            def_probs[i] = float(norm.cdf(-d2))
        except (ValueError, RuntimeError):
            continue

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(FULL_W, 3.2))

    valid_s = ~np.isnan(spreads)
    ax1.plot(leverages[valid_s], spreads[valid_s] * 10_000, "k-", linewidth=1.5)
    ax1.set_xlabel("Leverage (D/I)")
    ax1.set_ylabel("Credit spread (bps)")
    ax1.set_title("(a)", loc="left", fontweight="bold")

    valid_d = ~np.isnan(def_probs)
    ax2.plot(leverages[valid_d], def_probs[valid_d] * 100, "k-", linewidth=1.5)
    ax2.set_xlabel("Leverage (D/I)")
    ax2.set_ylabel("5-year default probability (%)")
    ax2.set_title("(b)", loc="left", fontweight="bold")

    plt.tight_layout()
    _save(fig, "fig_credit_risk")


# ==================================================================
# Figure 7 -Competition effect: monopoly vs duopoly
# ==================================================================
def fig_competition_effect():
    """Show how competition (duopoly) accelerates investment and
    reduces capacity relative to the monopolist benchmark.

    Panel (a): trigger ratio (leader/monopolist) -- shows preemption
    Panel (b): capacity ratio (leader/monopolist) -- shows rent sharing
    Both as a function of volatility.
    """
    from ai_lab_investment.models import (
        DuopolyModel,
        ModelParameters,
        SingleFirmModel,
    )

    p = ModelParameters()
    sigmas = np.linspace(0.20, 0.30, 30)

    trig_ratio = np.full_like(sigmas, np.nan)
    cap_ratio = np.full_like(sigmas, np.nan)
    mono_trig = np.full_like(sigmas, np.nan)
    leader_trig = np.full_like(sigmas, np.nan)

    for i, s in enumerate(sigmas):
        try:
            ps = p.with_param(sigma_H=s)
            m = SingleFirmModel(ps)
            X_m, K_m = m.optimal_trigger_and_capacity("H")
            mono_trig[i] = X_m

            duo = DuopolyModel(ps, leverage=0.0)
            eq = duo.solve_preemption_equilibrium("H")
            leader_trig[i] = eq["X_leader"]

            if X_m > 0:
                trig_ratio[i] = eq["X_leader"] / X_m
            if K_m > 0:
                cap_ratio[i] = eq["K_leader"] / K_m
        except (ValueError, RuntimeError):
            pass

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(FULL_W, 3.2))

    # Panel (a): absolute triggers
    v_m = ~np.isnan(mono_trig)
    v_l = ~np.isnan(leader_trig)
    ax1.plot(sigmas[v_m], mono_trig[v_m], "k-", linewidth=1.5, label="Monopolist")
    ax1.plot(
        sigmas[v_l],
        leader_trig[v_l],
        "--",
        color="0.35",
        linewidth=1.3,
        label="Duopoly leader",
    )
    ax1.set_xlabel(r"Volatility $\sigma_H$")
    ax1.set_ylabel(r"Investment trigger $X^*$")
    ax1.legend(fontsize=8)
    ax1.set_title("(a)", loc="left", fontweight="bold")

    # Panel (b): ratios -- show preemption + capacity erosion
    v_t = ~np.isnan(trig_ratio)
    v_c = ~np.isnan(cap_ratio)
    ax2.plot(
        sigmas[v_t],
        trig_ratio[v_t],
        "k-",
        linewidth=1.5,
        label=r"Trigger: $X_P / X^*_{\mathrm{mono}}$",
    )
    ax2.plot(
        sigmas[v_c],
        cap_ratio[v_c],
        "--",
        color="0.35",
        linewidth=1.3,
        label=r"Capacity: $K_L / K^*_{\mathrm{mono}}$",
    )
    ax2.axhline(1.0, color="0.7", linestyle=":", linewidth=0.7)
    ax2.set_xlabel(r"Volatility $\sigma_H$")
    ax2.set_ylabel("Ratio (duopoly leader / monopolist)")
    ax2.legend(fontsize=8)
    ax2.set_title("(b)", loc="left", fontweight="bold")

    plt.tight_layout()
    _save(fig, "fig_competition_effect")


# ==================================================================
# Figure 8 -Firm comparison (calibration)
# ==================================================================
def fig_firm_comparison():
    from ai_lab_investment.calibration.data import get_baseline_calibration

    calib = get_baseline_calibration()
    firms = calib.firms

    names = [f.name.split("(")[1].rstrip(")") for f in firms]
    capex_int = [f.capex_2025 / f.revenue_2025 for f in firms]
    rev_growth = [f.revenue_2025 / f.revenue_2024 for f in firms]
    leverages = [f.leverage_ratio for f in firms]

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(FULL_W, 3.2))

    colors = ["#1f77b4", "#ff7f0e", "#2ca02c", "#d62728"]
    x = np.arange(len(names))

    ax1.bar(x, capex_int, color=colors, edgecolor="0.3", width=0.55)
    ax1.set_xticks(x)
    ax1.set_xticklabels(names, rotation=15, ha="right", fontsize=8)
    ax1.set_ylabel("CapEx / Revenue (2025)")
    ax1.axhline(1.0, color="0.6", linestyle=":", linewidth=0.7)
    ax1.set_title("(a)", loc="left", fontweight="bold")

    for i, name in enumerate(names):
        ax2.scatter(
            rev_growth[i], leverages[i], s=100, c=colors[i], edgecolors="0.3", zorder=5
        )
        offset = (8, 4)
        ax2.annotate(
            name,
            (rev_growth[i], leverages[i]),
            textcoords="offset points",
            xytext=offset,
            fontsize=8,
        )
    ax2.set_xlabel("Revenue growth (2024-2025x)")
    ax2.set_ylabel("Leverage ratio")
    ax2.set_title("(b)", loc="left", fontweight="bold")

    plt.tight_layout()
    _save(fig, "fig_firm_comparison")


# ==================================================================
# Figure 9 -Lambda interpretation (timeline)
# ==================================================================
def fig_lambda_timeline():
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

    plt.tight_layout()
    _save(fig, "fig_lambda_timeline")


# ==================================================================
# Figure -Installed value decomposition (L vs H regime components)
# ==================================================================
def fig_growth_decomposition():
    """Decompose installed value into L-regime and H-regime components.

    Under F_H = 0, there is no post-AGI expansion option. Instead, the
    installed firm's value decomposes into inference revenue (L-regime)
    and training premium (H-regime continuation via A_eff).

    Panel (a): L-regime inference vs H-regime training components.
    Panel (b): H-regime fraction of total value vs training fraction.
    """
    from ai_lab_investment.models import ModelParameters, SingleFirmModel

    p = ModelParameters()
    model = SingleFirmModel(p)
    _, K_star = model.optimal_trigger_and_capacity("H")

    X = model._trigger_for_K(K_star, "H") * 1.5  # above trigger

    phi_vals = np.linspace(0.05, 0.95, 60)
    v_inference = np.zeros_like(phi_vals)
    v_training = np.zeros_like(phi_vals)

    for i, phi in enumerate(phi_vals):
        inf_cap = (1.0 - phi) * K_star
        tr_cap = phi * K_star
        denom_L = p.r - p.mu_L + p.lam
        # L-regime inference component
        v_inference[i] = inf_cap**p.alpha / denom_L * X
        # H-regime training component (via lambda transition)
        if tr_cap > 0:
            v_training[i] = p.lam / denom_L * tr_cap**p.alpha * p.A_H * X

    total = v_inference + v_training

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(FULL_W, 3.2))

    ax1.fill_between(
        phi_vals, 0, v_inference, alpha=0.4, color="#1f77b4", label="Inference (L)"
    )
    ax1.fill_between(
        phi_vals,
        v_inference,
        total,
        alpha=0.4,
        color="#ff7f0e",
        label="Training (H)",
    )
    ax1.set_xlabel(r"Training fraction $\phi$")
    ax1.set_ylabel("Installed value components")
    ax1.legend(fontsize=8, loc="upper right")
    ax1.set_title("(a)", loc="left", fontweight="bold")

    h_frac = np.where(total > 0, v_training / total * 100, 0)
    ax2.plot(phi_vals, h_frac, "k-", linewidth=1.5)
    ax2.set_xlabel(r"Training fraction $\phi$")
    ax2.set_ylabel("H-regime fraction of value (%)")
    ax2.set_ylim(0, 105)
    ax2.set_title("(b)", loc="left", fontweight="bold")

    plt.tight_layout()
    _save(fig, "fig_growth_decomposition")


# ==================================================================
# Figure 11 -AI Investment Dilemma (belief mismatch asymmetry)
# ==================================================================
def fig_investment_dilemma():
    """Value loss from belief mismatch: unleveraged vs leveraged.

    Cross-section at lambda_true = 0.10, varying lambda_invest.

    The mechanism: firms with different lambda beliefs choose
    different capacity levels.  Higher lambda -> more capacity
    (expecting imminent H-regime demand).  The asymmetry arises
    from convex costs (gamma > 1) and concave revenue (alpha < 1):
    overcapacity incurs disproportionate costs while generating
    diminishing revenue.  Leverage amplifies through default risk.
    """
    from ai_lab_investment.models import ModelParameters, SingleFirmModel

    p = ModelParameters()
    m = SingleFirmModel(p)
    X_star, K_star = m.optimal_trigger_and_capacity("H")

    # Evaluate at a demand level above the trigger (firm has invested)
    X_eval = X_star * 1.5

    # NPV at optimal capacity
    npv_opt = m.installed_value(X_eval, K_star, "H") - m.investment_cost(K_star)

    # Capacity multiplier as a function of belief mismatch.
    # Firms believing in higher lambda build more (expecting imminent
    # H-regime demand); lower-lambda firms build less.
    fixed_true = 0.10
    lam_range = np.linspace(0.02, 0.50, 80)

    # Map lambda_invest to capacity ratio K/K*
    # Higher lambda -> invest more aggressively
    # Use a convex mapping: K(lambda) = K* * (lambda/lambda_true)^eta
    # where eta > 1 captures the option-value amplification
    eta_map = 1.3
    K_ratios = (lam_range / fixed_true) ** eta_map

    # Unleveraged loss
    loss_unlev = np.full_like(lam_range, np.nan)
    for i, kr in enumerate(K_ratios):
        K_mis = K_star * kr
        npv_mis = m.installed_value(X_eval, K_mis, "H") - m.investment_cost(K_mis)
        if npv_opt > 0:
            loss_unlev[i] = min(max((npv_opt - npv_mis) / npv_opt, 0.0), 1.0)

    # Leveraged loss: default risk amplifies overinvestment
    loss_lev = np.full_like(lam_range, np.nan)
    lev = 0.40
    for i, kr in enumerate(K_ratios):
        K_mis = K_star * kr
        npv_mis = m.installed_value(X_eval, K_mis, "H") - m.investment_cost(K_mis)
        if npv_opt > 0:
            base_loss = max((npv_opt - npv_mis) / npv_opt, 0.0)
            if lam_range[i] > fixed_true:
                # Overinvestment: leverage adds default risk on excess
                # debt (convex amplification)
                excess = kr - 1.0
                debt_penalty = lev * excess * m.investment_cost(K_mis)
                amp_loss = base_loss + debt_penalty / npv_opt
                loss_lev[i] = min(amp_loss, 1.0)
            else:
                # Underinvestment: leverage mildly increases
                # opportunity cost
                loss_lev[i] = base_loss * (1.0 + 0.3 * lev)

    fig, ax = plt.subplots(figsize=(FULL_W, 3.8))

    valid_u = ~np.isnan(loss_unlev)
    valid_l = ~np.isnan(loss_lev)

    ax.plot(
        lam_range[valid_u],
        loss_unlev[valid_u] * 100,
        "k-",
        linewidth=1.5,
        label=r"Unleveraged ($\ell = 0$)",
    )
    ax.plot(
        lam_range[valid_l],
        loss_lev[valid_l] * 100,
        "k--",
        linewidth=1.5,
        label=r"Leveraged ($\ell = 0.40$)",
    )

    # Shade danger zone (overinvestment side only, loss > 20%)
    if valid_l.any():
        danger_mask = valid_l & (loss_lev > 0.20) & (lam_range > fixed_true)
        if danger_mask.any():
            ax.fill_between(
                lam_range[danger_mask],
                0,
                loss_lev[danger_mask] * 100,
                alpha=0.12,
                color="red",
                label="Danger zone (loss > 20%)",
            )

    ax.axvline(fixed_true, color="0.6", linestyle=":", linewidth=0.8)
    # Place annotation after drawing to get correct y-axis limits
    ax.set_xlabel(r"Investment belief $\lambda_{\mathrm{invest}}$")
    ax.set_ylabel(r"Value loss $\Delta V$ (%)")
    ax.legend(loc="lower right", fontsize=9, framealpha=0.9)
    ax.set_xlim(lam_range[0], lam_range[-1])
    ax.set_ylim(bottom=0)
    y_top = ax.get_ylim()[1]
    ax.annotate(
        rf"$\lambda_{{\mathrm{{true}}}} = {fixed_true}$",
        xy=(fixed_true, y_top * 0.5),
        xytext=(fixed_true + 0.02, y_top * 0.5),
        fontsize=9,
        color="0.4",
    )

    _save(fig, "fig_investment_dilemma")


# ==================================================================
# Main
# ==================================================================
if __name__ == "__main__":
    print("Generating paper figures...")
    fig_sample_paths()
    fig_comparative_statics()
    fig_lambda_option_value()
    fig_default_boundaries()
    fig_credit_risk()
    fig_competition_effect()
    fig_firm_comparison()
    fig_lambda_timeline()
    fig_growth_decomposition()
    fig_investment_dilemma()
    print("Done.")
