"""Symbolic derivation and verification of the regime-switching option value.

Uses sympy to derive the L-regime option value under the no-post-AGI-entry
assumption (F_H = 0) and verify the investment trigger formulas used in
the paper and numerical code.

This module serves two purposes:
1. **Verification**: Confirms that base_model.py and duopoly.py implement
   the correct solution to the regime-switching stopping problem.
2. **Documentation**: Provides a permanent, executable record of the
   mathematical derivations that can generate LaTeX for the paper.

Under F_H = 0, the L-regime HJB is a *homogeneous* Euler ODE:

    (1/2) sigma_L^2 X^2 F_L'' + mu_L X F_L' - (r + lambda) F_L = 0

The solution is a single-term power function:

    F_L(X) = A_1 * X^{beta_L^+}

where beta_L^+ is the positive root of the L-regime characteristic equation
with effective discount r + lambda.

References:
- Guo, Miao & Morellec (2005): "Irreversible Investment with Regime Shifts"
- Dixit & Pindyck (1994): Chapter 6 (regime-switching extensions)
"""

import sympy as sp

# =====================================================================
# Symbolic parameter definitions
# =====================================================================


def define_symbols():
    """Define all symbolic parameters used in the model.

    Returns a dict of sympy symbols for convenient access.
    """
    syms = {}

    # Demand process parameters
    syms["X"] = sp.Symbol("X", positive=True)
    syms["mu_L"] = sp.Symbol("mu_L", real=True)
    syms["mu_H"] = sp.Symbol("mu_H", real=True)
    syms["sigma_L"] = sp.Symbol("sigma_L", positive=True)
    syms["sigma_H"] = sp.Symbol("sigma_H", positive=True)
    syms["r"] = sp.Symbol("r", positive=True)
    syms["lam"] = sp.Symbol("lambda", positive=True)  # tilde{lambda}

    # Technology parameters
    syms["alpha"] = sp.Symbol("alpha", positive=True)
    syms["gamma"] = sp.Symbol("gamma", positive=True)
    syms["c"] = sp.Symbol("c", positive=True)
    syms["delta"] = sp.Symbol("delta", positive=True)
    syms["K"] = sp.Symbol("K", positive=True)
    syms["phi"] = sp.Symbol("phi", positive=True)

    # Characteristic exponents
    syms["beta"] = sp.Symbol("beta")
    syms["beta_H"] = sp.Symbol("beta_H", positive=True)
    syms["beta_L_plus"] = sp.Symbol("beta_L_plus", positive=True)
    syms["beta_L_minus"] = sp.Symbol("beta_L_minus", real=True)

    # Option value coefficients
    syms["A1"] = sp.Symbol("A_1")
    syms["B_H"] = sp.Symbol("B_H", positive=True)
    syms["C_coeff"] = sp.Symbol("C")

    # Trigger
    syms["X_star"] = sp.Symbol("X^*", positive=True)

    return syms


# =====================================================================
# 1. Characteristic equations
# =====================================================================


def characteristic_equation_H(syms):
    """Characteristic equation for the H-regime (absorbing).

    (sigma_H^2 / 2) * beta * (beta - 1) + mu_H * beta - r = 0

    Returns the equation (set equal to zero) and its positive root.
    """
    beta = syms["beta"]
    sigma_H = syms["sigma_H"]
    mu_H = syms["mu_H"]
    r = syms["r"]

    eq = sp.Rational(1, 2) * sigma_H**2 * beta * (beta - 1) + mu_H * beta - r
    roots = sp.solve(eq, beta)

    # Return the equation and the two roots
    return {
        "equation": eq,
        "roots": roots,
        "positive_root_expr": roots[1],  # The larger root (positive)
        "negative_root_expr": roots[0],
    }


def characteristic_equation_L(syms):
    """Characteristic equation for the L-regime with regime switching.

    The L-regime ODE (homogeneous under F_H = 0) uses effective
    discount (r + lambda):

    (sigma_L^2 / 2) * beta * (beta - 1) + mu_L * beta - (r + lambda) = 0

    The regime-switching term lambda * [F_H - F_L] with F_H = 0
    reduces to -lambda * F_L, adding lambda to the effective discount.
    """
    beta = syms["beta"]
    sigma_L = syms["sigma_L"]
    mu_L = syms["mu_L"]
    r = syms["r"]
    lam = syms["lam"]

    eq = sp.Rational(1, 2) * sigma_L**2 * beta * (beta - 1) + mu_L * beta - (r + lam)
    roots = sp.solve(eq, beta)

    return {
        "equation": eq,
        "roots": roots,
        "positive_root_expr": roots[1],
        "negative_root_expr": roots[0],
    }


# =====================================================================
# 2. H-regime option value (set to zero under F_H = 0)
# =====================================================================


def h_regime_option_value(syms):
    """Derive the H-regime option value (standard real options).

    Under the no-post-AGI-entry assumption, F_H(X) = 0. This function
    retains the standard derivation for reference and verification of
    the standalone H-regime problem.

    F_H(X) = B_H * X^{beta_H}  for X < X_H*

    Value-matching: B_H * (X*)^{beta_H} = V_H(X*) - I(K)
    Smooth-pasting: beta_H * B_H * (X*)^{beta_H - 1} = A_H * (phi*K)^alpha

    Returns dict with trigger formula and option value coefficient.
    """
    X = syms["X"]
    r = syms["r"]
    mu_H = syms["mu_H"]
    alpha = syms["alpha"]
    gamma_ = syms["gamma"]
    c = syms["c"]
    delta = syms["delta"]
    K = syms["K"]
    phi = syms["phi"]
    beta_H = syms["beta_H"]
    X_star = syms["X_star"]

    A_H = 1 / (r - mu_H)
    revenue_coeff = A_H * (phi * K) ** alpha
    total_cost = c * K**gamma_ + delta * K / r

    # Smooth-pasting gives B_H
    B_H_expr = revenue_coeff * X_star ** (1 - beta_H) / beta_H

    # Value-matching gives the trigger
    trigger = (beta_H / (beta_H - 1)) * total_cost / revenue_coeff

    return {
        "A_H": A_H,
        "revenue_coeff": revenue_coeff,
        "total_cost": total_cost,
        "B_H": B_H_expr,
        "trigger": trigger,
        "option_value": B_H_expr * X**beta_H,
        "installed_value": revenue_coeff * X - delta * K / r,
    }


# =====================================================================
# 3. L-regime option value (homogeneous under F_H = 0)
# =====================================================================


def l_regime_ode(syms):
    """Derive the L-regime option value from the homogeneous ODE.

    Under F_H = 0, the L-regime option value satisfies:

    (1/2) sigma_L^2 X^2 F_L'' + mu_L X F_L' - (r + lambda) F_L = 0

    This is a homogeneous Euler ODE. The characteristic equation is:
    Q_L(beta) = (1/2) sigma_L^2 beta(beta-1) + mu_L beta - (r + lambda) = 0

    with positive root beta_L^+.

    Solution: F_L(X) = A_1 * X^{beta_L^+}

    A_1 is determined by value-matching and smooth-pasting at the trigger.
    """
    sigma_L = syms["sigma_L"]
    mu_L = syms["mu_L"]
    r = syms["r"]
    lam = syms["lam"]
    beta_L_plus = syms["beta_L_plus"]

    # Characteristic equation
    Q_L = (
        sp.Rational(1, 2) * sigma_L**2 * beta_L_plus * (beta_L_plus - 1)
        + mu_L * beta_L_plus
        - (r + lam)
    )

    return {
        "Q_L": Q_L,
        "solution": "F_L(X) = A_1 * X^{beta_L^+}",
        "note": (
            "Under F_H = 0, the L-regime HJB is homogeneous. "
            "The solution is a single power function with exponent "
            "beta_L^+ from the characteristic equation with discount r + lambda."
        ),
    }


def l_regime_option_value_full(syms):
    """Full L-regime option value with value-matching and smooth-pasting.

    For a firm with installed value V_L(X) = A_eff * X - delta*K/r,
    the option value is:

    F_L(X) = A_1 * X^{beta_L^+},  X < X*

    Boundary conditions at the trigger X*:

    VALUE-MATCHING:
    A_1 * (X*)^{beta_L^+} = A_eff * X* - delta*K/r - I(K)

    SMOOTH-PASTING:
    A_1 * beta_L^+ * (X*)^{beta_L^+ - 1} = A_eff

    These yield:
    X* = [beta_L^+ / (beta_L^+ - 1)] * [delta*K/r + c*K^gamma] / A_eff
    A_1 = A_eff * (X*)^{1 - beta_L^+} / beta_L^+
    """
    X_star = syms["X_star"]
    beta_L_plus = syms["beta_L_plus"]
    delta = syms["delta"]
    K = syms["K"]
    r = syms["r"]
    gamma_ = syms["gamma"]
    c = syms["c"]

    # A_eff is a symbolic placeholder
    A_eff = sp.Symbol("A_eff", positive=True)

    total_cost = c * K**gamma_ + delta * K / r
    trigger = (beta_L_plus / (beta_L_plus - 1)) * total_cost / A_eff

    npv_at_trigger = A_eff * X_star - delta * K / r - c * K**gamma_

    # Value-matching
    A1 = syms["A1"]
    vm = sp.Eq(A1 * X_star**beta_L_plus, npv_at_trigger)

    # Smooth-pasting
    sp_cond = sp.Eq(A1 * beta_L_plus * X_star ** (beta_L_plus - 1), A_eff)

    # A_1 from smooth-pasting
    A1_from_sp = sp.solve(sp_cond, A1)[0]

    return {
        "A_eff_symbol": A_eff,
        "trigger": trigger,
        "value_matching": vm,
        "smooth_pasting": sp_cond,
        "A1_from_smooth_pasting": A1_from_sp,
    }


# =====================================================================
# 4. Effective revenue coefficient A_eff (with training fraction)
# =====================================================================


def effective_revenue_coefficient(syms):
    """Derive A_eff for the single-firm case with training fraction.

    A_eff(phi, K) = [(1-phi)*K]^alpha / (r - mu_L + lambda)
                  + lambda / (r - mu_L + lambda) * (phi*K)^alpha / (r - mu_H)

    This combines L-regime inference revenue and H-regime continuation value.
    Note: A_eff captures the installed value per unit X for a firm that HAS
    invested, not the option value (which is F_H = 0 for non-investors).
    """
    r = syms["r"]
    mu_L = syms["mu_L"]
    mu_H = syms["mu_H"]
    lam = syms["lam"]
    alpha = syms["alpha"]
    K = syms["K"]
    phi = syms["phi"]

    denom_L = r - mu_L + lam
    A_H = 1 / (r - mu_H)

    inf_cap = (1 - phi) * K
    tr_cap = phi * K

    A_eff = inf_cap**alpha / denom_L + lam / denom_L * tr_cap**alpha * A_H

    # Partial derivative w.r.t. phi (for interior optimality)
    dA_dphi = sp.diff(A_eff, phi)

    # Partial derivative w.r.t. lambda (for faith-based survival)
    dA_dlam = sp.diff(A_eff, lam)

    return {
        "A_eff": A_eff,
        "dA_dphi": sp.simplify(dA_dphi),
        "dA_dlam": sp.simplify(dA_dlam),
    }


# =====================================================================
# 5. Optimal training fraction (Proposition 1)
# =====================================================================


def optimal_phi_conditions(syms):
    """Derive the first-order condition for the optimal training fraction.

    The firm maximizes h(K, phi) = A_eff^{beta_L^+} / cost^{beta_L^+ - 1}.
    Taking d/dphi of ln(h):

    beta_L^+ * (1/A_eff) * dA_eff/dphi = 0

    Since cost does not depend on phi, the FOC reduces to dA_eff/dphi = 0.
    """
    r = syms["r"]
    mu_L = syms["mu_L"]
    mu_H = syms["mu_H"]
    lam = syms["lam"]
    alpha = syms["alpha"]
    K = syms["K"]
    phi = syms["phi"]

    denom_L = r - mu_L + lam
    A_H = 1 / (r - mu_H)

    inf_cap = (1 - phi) * K
    tr_cap = phi * K

    A_eff = inf_cap**alpha / denom_L + lam / denom_L * tr_cap**alpha * A_H

    # FOC: dA_eff/dphi = 0
    foc = sp.diff(A_eff, phi)
    foc_simplified = sp.simplify(foc)

    return {
        "foc": foc_simplified,
        "A_eff": A_eff,
        "boundary_phi_0": "dA_eff/dphi -> +inf (Inada from training: alpha < 1)",
        "boundary_phi_1": "dA_eff/dphi -> -inf (Inada from inference: alpha < 1)",
        "interior_conclusion": (
            "By continuity and the intermediate value theorem, "
            "an interior phi* in (0,1) exists where dA_eff/dphi = 0."
        ),
    }


# =====================================================================
# 6. Default boundary (Proposition 2)
# =====================================================================


def default_boundary_derivation(syms):
    """Derive the endogenous default boundary and its comparative statics.

    X_D = [beta_neg / (beta_neg - 1)] * [c_D/r + delta*K/r] / A_eff

    Key result (faith-based survival):
    dX_D/dlambda < 0 when dA_eff/dlambda > 0
    """
    r = syms["r"]
    delta = syms["delta"]
    K = syms["K"]

    beta_neg = sp.Symbol("beta_neg", negative=True)
    c_D = sp.Symbol("c_D", positive=True)
    A_eff = sp.Symbol("A_eff", positive=True)

    X_D = (beta_neg / (beta_neg - 1)) * (c_D / r + delta * K / r) / A_eff

    dXD_dA = sp.diff(X_D, A_eff)
    dXD_dcD = sp.diff(X_D, c_D)

    return {
        "X_D": X_D,
        "dXD_dA_eff": sp.simplify(dXD_dA),
        "dXD_dcD": sp.simplify(dXD_dcD),
        "sign_dXD_dA": "< 0 (higher revenue lowers default boundary)",
        "sign_dXD_dcD": "> 0 (higher coupon raises default boundary)",
        "faith_based_survival": (
            "Since dA_eff/dlambda > 0 (when H-regime value exceeds "
            "L-regime value) and dX_D/dA_eff < 0, we get "
            "dX_D/dlambda < 0: higher arrival rate lowers default boundary."
        ),
    }


# =====================================================================
# 7. Numerical verification against base_model.py
# =====================================================================


def verify_option_value_structure(params):
    """Verify the L-regime option value structure against the code.

    Under F_H = 0, the option value is F_L(X) = A_1 * X^{beta_L^+}.

    Args:
        params: ModelParameters instance.

    Returns:
        Dict with verification results.
    """
    import numpy as np

    from .base_model import SingleFirmModel

    model = SingleFirmModel(params)
    p = params

    has_L_trigger = model.has_interior_trigger("L")

    if not has_L_trigger:
        return {
            "has_L_trigger": False,
            "form": "No interior trigger in L",
            "match": False,
            "note": "Cannot verify option value without interior trigger",
        }

    X_L, _K_L, A_1 = model._solve_regime_L()

    test_X = X_L * 0.5  # Below the trigger
    F_L_code = model.option_value_L(test_X)
    F_L_formula = A_1 * test_X**p.beta_L

    return {
        "has_L_trigger": True,
        "form": "F_L(X) = A_1 * X^{beta_L^+} (homogeneous solution)",
        "X_L_star": X_L,
        "A_1": A_1,
        "F_L_code": F_L_code,
        "F_L_formula": F_L_formula,
        "match": bool(
            np.abs(F_L_code - F_L_formula) / max(abs(F_L_code), 1e-10) < 1e-8
        ),
    }


def verify_smooth_pasting_L(params):
    """Verify smooth-pasting for the L-regime option value.

    Under F_H = 0, smooth-pasting at the trigger gives:
    dF_L/dX |_{X=X*} = A_eff(phi*, K*)

    The derivative of the installed value w.r.t. X is A_eff, because
    V(X, phi, K) = A_eff(phi, K) * X - delta*K/r.

    Args:
        params: ModelParameters instance.

    Returns:
        Dict with smooth-pasting verification.
    """
    import numpy as np

    from .base_model import SingleFirmModel

    model = SingleFirmModel(params)
    p = params

    if not model.has_interior_trigger("L"):
        return {"has_L_trigger": False, "skip": True}

    X_L, K_L, A_1 = model._solve_regime_L()
    _, _, phi_star = model.optimal_trigger_capacity_phi()

    # dF_L/dX at X*: A_1 * beta_L * X^(beta_L - 1)
    dF = A_1 * p.beta_L * X_L ** (p.beta_L - 1)

    # dV/dX at X* = A_eff(phi*, K*)
    dV = model._effective_revenue_coeff_single(phi_star, K_L)

    return {
        "has_L_trigger": True,
        "X_L_star": X_L,
        "dF_dX": dF,
        "dV_dX": dV,
        "match": bool(np.abs(dF - dV) / max(abs(dV), 1e-10) < 1e-4),
    }


def verify_baseline_simplification():
    """Check baseline parameters for interior L-regime trigger under F_H = 0.

    Under F_H = 0, the capacity optimization uses beta_L^+ in the option
    premium. An interior K* requires alpha > 1 - 1/beta_L^+. This is
    more restrictive than the old model which used beta_H.
    """
    from .parameters import ModelParameters

    p = ModelParameters()

    # Minimum alpha for interior K* under F_H = 0
    alpha_min = 1.0 - 1.0 / p.beta_L
    has_interior = p.alpha > alpha_min

    # K-optimization exponent: must be > 0
    k_exponent = p.beta_L * (p.alpha - 1) + 1

    return {
        "beta_L_plus": p.beta_L,
        "beta_H": p.beta_H,
        "alpha": p.alpha,
        "alpha_min_for_interior_K": alpha_min,
        "k_optimization_exponent": k_exponent,
        "has_interior_L_trigger": has_interior,
        "conclusion": (
            f"alpha = {p.alpha:.2f}, alpha_min = {alpha_min:.4f}. "
            + (
                "Interior L-regime trigger exists under F_H = 0."
                if has_interior
                else f"No interior L-regime trigger under F_H = 0. "
                f"Need alpha > {alpha_min:.4f} "
                f"(K-optimization exponent = {k_exponent:.4f} < 0)."
            )
        ),
    }


# =====================================================================
# 8. Generate LaTeX for the paper
# =====================================================================


def generate_latex():
    """Generate LaTeX expressions for key results.

    Returns a dict of LaTeX strings that can be pasted into the paper.
    """
    syms = define_symbols()

    # Characteristic equation H
    ch_H = characteristic_equation_H(syms)
    # Characteristic equation L
    ch_L = characteristic_equation_L(syms)
    # L-regime ODE
    l_ode = l_regime_ode(syms)
    # Full option value
    l_full = l_regime_option_value_full(syms)
    # A_eff
    a_eff_result = effective_revenue_coefficient(syms)

    return {
        "char_eq_H": sp.latex(ch_H["equation"]),
        "char_eq_L": sp.latex(ch_L["equation"]),
        "Q_L": sp.latex(l_ode["Q_L"]),
        "trigger": sp.latex(l_full["trigger"]),
        "value_matching": sp.latex(l_full["value_matching"]),
        "smooth_pasting": sp.latex(l_full["smooth_pasting"]),
        "A1_expr": sp.latex(l_full["A1_from_smooth_pasting"]),
        "A_eff": sp.latex(a_eff_result["A_eff"]),
        "dA_eff_dphi": sp.latex(a_eff_result["dA_dphi"]),
        "dA_eff_dlam": sp.latex(a_eff_result["dA_dlam"]),
    }
