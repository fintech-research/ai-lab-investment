"""Symbolic derivation and verification of the regime-switching option value.

Uses sympy to derive the coupled ODE system for F_L(X) and F_H(X),
solve for the general solution, apply boundary conditions, and verify
the investment trigger formulas used in the paper and numerical code.

This module serves two purposes:
1. **Verification**: Confirms that base_model.py and duopoly.py implement
   the correct solution to the regime-switching stopping problem.
2. **Documentation**: Provides a permanent, executable record of the
   mathematical derivations that can generate LaTeX for the paper.

The L-regime option value has TWO terms in general:

    F_L(X) = A1 * X^{beta_L_plus} + C * X^{beta_H}

where:
- A1 * X^{beta_L_plus} is the homogeneous solution (L-regime dynamics
  with effective discount r + lambda)
- C * X^{beta_H} is the particular solution from the regime-switching
  term lambda * F_H(X)

The simplified form F_L = C * X^{beta_H} (A1 = 0) applies when no
interior trigger exists in regime L, i.e., when the option premium ratio
(1 - 1/beta_L_plus)/alpha >= 1 (Assumption A3 in the paper). At the
baseline calibration, beta_L_plus ≈ 3.01 gives a ratio ≈ 1.67 > 1,
so the simplified form is valid. The paper derives and states this
condition explicitly (see eq-option-L-general and Assumption 1(A3)).

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
    syms["sigma"] = sp.Symbol("sigma", positive=True)
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

    (sigma^2 / 2) * beta * (beta - 1) + mu_H * beta - r = 0

    Returns the equation (set equal to zero) and its positive root.
    """
    beta = syms["beta"]
    sigma = syms["sigma"]
    mu_H = syms["mu_H"]
    r = syms["r"]

    eq = sp.Rational(1, 2) * sigma**2 * beta * (beta - 1) + mu_H * beta - r
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

    The homogeneous part of the L-regime ODE uses effective discount (r + lambda):

    (sigma^2 / 2) * beta * (beta - 1) + mu_L * beta - (r + lambda) = 0

    This is because the regime-switching term lambda * [F_H - F_L] acts
    as an additional "discount" on F_L.
    """
    beta = syms["beta"]
    sigma = syms["sigma"]
    mu_L = syms["mu_L"]
    r = syms["r"]
    lam = syms["lam"]

    eq = sp.Rational(1, 2) * sigma**2 * beta * (beta - 1) + mu_L * beta - (r + lam)
    roots = sp.solve(eq, beta)

    return {
        "equation": eq,
        "roots": roots,
        "positive_root_expr": roots[1],
        "negative_root_expr": roots[0],
    }


# =====================================================================
# 2. H-regime option value (standard, absorbing)
# =====================================================================


def h_regime_option_value(syms):
    """Derive the H-regime option value (standard real options).

    F_H(X) = B_H * X^{beta_H}  for X < X_H*

    The installed value in H is:
    V_H(X) = A_H * X * (phi*K)^alpha - delta*K/r

    where A_H = 1 / (r - mu_H).

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
    # B_H * X*^{beta_H} = A_H * X* * (phi*K)^alpha - delta*K/r - c*K^gamma
    # Substituting B_H from smooth-pasting:
    # revenue_coeff * X* / beta_H = revenue_coeff * X* - total_cost
    # revenue_coeff * X* * (1 - 1/beta_H) = total_cost
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
# 3. L-regime option value (coupled ODE — the critical derivation)
# =====================================================================


def l_regime_ode(syms):
    """Derive the L-regime option value from the coupled ODE system.

    The L-regime option value satisfies the HJB equation:

    (1/2) sigma^2 X^2 F_L'' + mu_L X F_L' + lambda[F_H(X) - F_L(X)] - r F_L = 0

    Rearranging:
    (1/2) sigma^2 X^2 F_L'' + mu_L X F_L' - (r + lambda) F_L + lambda F_H(X) = 0

    Since F_H(X) = B_H * X^{beta_H}, this is a second-order Euler ODE with
    a non-homogeneous term lambda * B_H * X^{beta_H}.

    GENERAL SOLUTION:
    F_L(X) = A1 * X^{beta_L_plus} + A2 * X^{beta_L_minus} + C * X^{beta_H}

    where:
    - beta_L_plus, beta_L_minus are roots of the L-regime characteristic
      equation with discount (r + lambda)
    - C is the particular solution coefficient
    - A2 = 0 (boundary condition: F_L(0) = 0 requires dropping the
      negative-exponent term since beta_L_minus < 0)
    - A1 is determined by value-matching/smooth-pasting at the trigger

    PARTICULAR SOLUTION COEFFICIENT:
    Substituting C * X^{beta_H} into the homogeneous operator:
    C * Q_L(beta_H) * X^{beta_H} + lambda * B_H * X^{beta_H} = 0

    where Q_L(beta) = (1/2) sigma^2 beta(beta-1) + mu_L beta - (r + lambda)

    So: C = -lambda * B_H / Q_L(beta_H)
    """
    sigma = syms["sigma"]
    mu_L = syms["mu_L"]
    r = syms["r"]
    lam = syms["lam"]
    beta_H = syms["beta_H"]
    B_H = syms["B_H"]

    # Q_L evaluated at beta_H
    Q_L_at_beta_H = (
        sp.Rational(1, 2) * sigma**2 * beta_H * (beta_H - 1) + mu_L * beta_H - (r + lam)
    )

    # Particular solution coefficient
    C_expr = -lam * B_H / Q_L_at_beta_H

    return {
        "Q_L_at_beta_H": Q_L_at_beta_H,
        "C": C_expr,
        "general_solution": "F_L(X) = A1 * X^{beta_L_plus} + C * X^{beta_H}",
        "note": (
            "The simplified F_L = C * X^{beta_H} sets A1 = 0, which applies "
            "when no interior trigger exists in L (option premium ratio >= 1). "
            "The paper derives this as Assumption A3 and uses the simplified "
            "form throughout the baseline analysis (see eq-option-L-general)."
        ),
    }


def l_regime_option_value_full(syms):
    """Full L-regime option value with value-matching and smooth-pasting.

    For a firm with installed value V_L(X) = A_eff * X - delta*K/r,
    the option value is:

    F_L(X) = A1 * X^{beta_L_plus} + C * X^{beta_H},  X < X*

    Boundary conditions at the trigger X*:

    VALUE-MATCHING:
    A1 * (X*)^{beta_L_plus} + C * (X*)^{beta_H} = A_eff * X* - delta*K/r - I(K)

    SMOOTH-PASTING:
    A1 * beta_L_plus * (X*)^{beta_L_plus - 1} + C * beta_H * (X*)^{beta_H - 1} = A_eff

    These two equations determine A1 and X* (given K, phi, and hence A_eff).
    """
    X_star = syms["X_star"]
    beta_H = syms["beta_H"]
    beta_L_plus = syms["beta_L_plus"]
    A1 = syms["A1"]
    C_coeff = syms["C_coeff"]
    delta = syms["delta"]
    K = syms["K"]
    r = syms["r"]
    gamma_ = syms["gamma"]
    c = syms["c"]

    # A_eff is a symbolic placeholder
    A_eff = sp.Symbol("A_eff", positive=True)

    npv_at_trigger = A_eff * X_star - delta * K / r - c * K**gamma_

    # Value-matching
    vm = sp.Eq(
        A1 * X_star**beta_L_plus + C_coeff * X_star**beta_H,
        npv_at_trigger,
    )

    # Smooth-pasting
    sp_cond = sp.Eq(
        A1 * beta_L_plus * X_star ** (beta_L_plus - 1)
        + C_coeff * beta_H * X_star ** (beta_H - 1),
        A_eff,
    )

    # Solve for A1 from smooth-pasting
    A1_from_sp = sp.solve(sp_cond, A1)[0]

    # Substitute into value-matching to get equation for X*
    vm_substituted = vm.subs(A1, A1_from_sp)

    # Solve for X* (this is the trigger equation)
    trigger_eq = sp.simplify(vm_substituted)

    return {
        "A_eff_symbol": A_eff,
        "value_matching": vm,
        "smooth_pasting": sp_cond,
        "A1_from_smooth_pasting": A1_from_sp,
        "trigger_equation": trigger_eq,
        "note_trigger": (
            "The trigger X* is determined implicitly by the substituted "
            "equation. In general this does not simplify to the paper's "
            "beta_H/(beta_H-1) * cost/A_eff formula, which is only valid "
            "for the single-exponent case (A1=0)."
        ),
    }


# =====================================================================
# 4. When is A1 = 0? (Justifying the paper's simplified form)
# =====================================================================


def when_is_A1_zero(syms):
    """Analyze when the homogeneous term A1 vanishes.

    A1 = 0 occurs when:
    1. There is no interior trigger in L (the firm never invests in L,
       only waits for the regime switch). In this case, there are no
       value-matching / smooth-pasting conditions to determine A1,
       and the option value is purely F_L(X) = C * X^{beta_H}.

    2. The condition (1 - 1/beta_L_plus)/alpha >= 1, i.e., the option
       premium ratio in L exceeds 1, meaning the option to wait is so
       valuable the firm never exercises in L.

    The code in base_model.py checks this via has_interior_trigger("L").
    When this returns False (common for baseline parameters), A1 = 0
    and F_L = C * X^{beta_H} is correct.

    When an interior L-trigger exists, the full two-term solution
    F_L = A1 * X^{beta_L_plus} + C * X^{beta_H} must be used.
    """
    beta_L_plus = syms["beta_L_plus"]
    alpha = syms["alpha"]
    gamma_ = syms["gamma"]

    # Option premium ratio in L
    phi_L = (1 - 1 / beta_L_plus) / alpha

    # Interior trigger exists when 1/gamma < phi_L < 1
    exists_condition = sp.And(1 / gamma_ < phi_L, phi_L < 1)

    return {
        "option_premium_ratio_L": phi_L,
        "interior_trigger_condition": exists_condition,
        "A1_zero_when": sp.Or(phi_L >= 1, phi_L <= 1 / gamma_),
        "note": (
            "For the paper's baseline parameters (sigma=0.25, mu_L=0.01, "
            "r=0.12, lambda=0.10), beta_L_plus ≈ 3.01 gives phi_L ≈ 1.67 > 1. "
            "So A1=0 and the simplified F_L = C * X^{beta_H} IS valid. "
            "The paper states this as Assumption 1(A3) and derives the "
            "boundary explicitly (see Appendix B for sensitivity analysis)."
        ),
    }


# =====================================================================
# 5. Effective revenue coefficient A_eff (with training fraction)
# =====================================================================


def effective_revenue_coefficient(syms):
    """Derive A_eff for the single-firm case with training fraction.

    A_eff(phi, K) = [(1-phi)*K]^alpha / (r - mu_L + lambda)
                  + lambda / (r - mu_L + lambda) * (phi*K)^alpha / (r - mu_H)

    This combines L-regime inference revenue and H-regime continuation value.
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
# 6. Optimal training fraction (Proposition 1)
# =====================================================================


def optimal_phi_conditions(syms):
    """Derive the first-order condition for the optimal training fraction.

    The firm maximizes h(K, phi) = A_eff^{beta_H} / cost^{beta_H - 1}.
    Taking d/dphi of ln(h):

    beta_H * (1/A_eff) * dA_eff/dphi = 0

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

    # Check boundary behavior
    # As phi -> 0+: d/dphi of [(1-phi)K]^alpha -> -alpha*K^alpha*(1-phi)^{alpha-1}*K
    # But d/dphi of [phi*K]^alpha -> alpha*K^alpha*phi^{alpha-1}*K -> +inf (alpha < 1)
    # So dA_eff/dphi -> +inf as phi -> 0+ (Inada condition from training term)

    # As phi -> 1-: d/dphi of [(1-phi)K]^alpha -> -inf
    # And d/dphi of [phi*K]^alpha -> alpha*K^alpha (finite)
    # So dA_eff/dphi -> -inf as phi -> 1- (Inada condition from inference term)

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
# 7. Default boundary (Proposition 2)
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

    # Since beta_neg < 0, beta_neg/(beta_neg - 1) is in (0, 1)
    # So X_D < (c_D + delta*K) / (r * A_eff) (the naive break-even)

    dXD_dA = sp.diff(X_D, A_eff)
    # dX_D/dA_eff < 0 (higher effective revenue lowers default boundary)

    dXD_dcD = sp.diff(X_D, c_D)
    # dX_D/dc_D > 0 (higher coupon raises default boundary)

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
# 8. Numerical verification against base_model.py
# =====================================================================


def verify_particular_solution_coefficient(params):
    """Verify C = -lambda * B_H / Q_L(beta_H) against base_model.py.

    Args:
        params: ModelParameters instance.

    Returns:
        Dict with symbolic and numerical values for comparison.
    """
    import numpy as np

    from .base_model import SingleFirmModel

    model = SingleFirmModel(params)
    p = params

    # Numerical values from the code
    C_code = model._particular_solution_coeff()
    _, _, B_H_code = model._solve_regime_H()

    # Symbolic verification
    Q_L = (
        0.5 * p.sigma**2 * p.beta_H * (p.beta_H - 1) + p.mu_L * p.beta_H - (p.r + p.lam)
    )
    C_formula = -p.lam * B_H_code / Q_L

    return {
        "C_from_code": C_code,
        "C_from_formula": C_formula,
        "B_H": B_H_code,
        "Q_L_at_beta_H": Q_L,
        "beta_H": p.beta_H,
        "beta_L": p.beta_L,
        "match": bool(np.abs(C_code - C_formula) < 1e-12),
    }


def verify_option_value_structure(params):
    """Verify the two-term structure of F_L against the code.

    Tests that F_L(X) = D_L * X^{beta_L} + C * X^{beta_H} when an
    interior L-trigger exists, and F_L(X) = C * X^{beta_H} otherwise.

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
    C = model._particular_solution_coeff()

    if not has_L_trigger:
        # F_L = C * X^{beta_H} (single-term, A1 = 0)
        test_X = 0.05
        F_L_code = model.option_value_L(test_X)
        F_L_formula = C * test_X**p.beta_H
        return {
            "has_L_trigger": False,
            "form": "F_L(X) = C * X^{beta_H} (single-term, A1=0)",
            "F_L_code": F_L_code,
            "F_L_formula": F_L_formula,
            "match": bool(np.abs(F_L_code - F_L_formula) < 1e-10),
            "C": C,
            "paper_simplified_form_valid": True,
        }
    else:
        # F_L = D_L * X^{beta_L} + C * X^{beta_H} (two-term)
        X_L, _K_L, D_L = model._solve_regime_L()
        if X_L is None:  # pragma: no cover
            msg = "Expected interior L-trigger but got None"
            raise RuntimeError(msg)
        test_X = X_L * 0.5  # Below the trigger
        F_L_code = model.option_value_L(test_X)
        F_L_formula = D_L * test_X**p.beta_L + C * test_X**p.beta_H
        return {
            "has_L_trigger": True,
            "form": "F_L(X) = D_L * X^{beta_L} + C * X^{beta_H} (two-term)",
            "X_L_star": X_L,
            "D_L": D_L,
            "C": C,
            "F_L_code": F_L_code,
            "F_L_formula": F_L_formula,
            "match": bool(
                np.abs(F_L_code - F_L_formula) / max(abs(F_L_code), 1e-10) < 1e-8
            ),
            "paper_simplified_form_valid": False,
        }


def verify_baseline_simplification():
    """Check whether the paper's simplified form is valid at baseline params.

    At the default baseline (sigma=0.25, mu_L=0.01, r=0.12, lam=0.10),
    check if the L-regime has no interior trigger, validating F_L = C*X^{beta_H}.
    """
    from .parameters import ModelParameters

    p = ModelParameters()

    # Compute the option premium ratio in L
    phi_L = (1.0 - 1.0 / p.beta_L) / p.alpha

    return {
        "beta_L_plus": p.beta_L,
        "option_premium_ratio_L": phi_L,
        "has_interior_L_trigger": 1.0 / p.gamma < phi_L < 1.0,
        "simplified_form_valid": phi_L >= 1.0,
        "conclusion": (
            f"phi_L = {phi_L:.4f}. "
            + (
                "phi_L >= 1, so no interior trigger in L. "
                "The simplified F_L = C * X^{beta_H} IS valid for "
                "the baseline parameters (Assumption A3 satisfied)."
                if phi_L >= 1.0
                else "phi_L < 1, so an interior trigger exists in L. "
                "The full two-term solution F_L = A1*X^{beta_L_plus} + C*X^{beta_H} "
                "must be used (Assumption A3 violated at these parameters)."
            )
        ),
    }


def verify_smooth_pasting_L(params):
    """Verify smooth-pasting for the L-regime option value.

    When an interior trigger exists:
    dF_L/dX |_{X=X*} = dV_L/dX |_{X=X*} = A_L * K^alpha

    Args:
        params: ModelParameters instance with alpha and r such that
                an interior L-trigger exists.

    Returns:
        Dict with smooth-pasting verification.
    """
    import numpy as np

    from .base_model import SingleFirmModel

    model = SingleFirmModel(params)
    p = params

    if not model.has_interior_trigger("L"):
        return {"has_L_trigger": False, "skip": True}

    X_L, K_L, D_L = model._solve_regime_L()
    C = model._particular_solution_coeff()

    # dF_L/dX at X*
    dF = D_L * p.beta_L * X_L ** (p.beta_L - 1) + C * p.beta_H * X_L ** (p.beta_H - 1)

    # dV_L/dX at X* = A_L * K_L^alpha
    dV = p.A_L * K_L**p.alpha

    return {
        "has_L_trigger": True,
        "X_L_star": X_L,
        "dF_dX": dF,
        "dV_dX": dV,
        "match": bool(np.abs(dF - dV) / max(abs(dV), 1e-10) < 1e-4),
    }


# =====================================================================
# 9. Generate LaTeX for the paper
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
        "Q_L_at_beta_H": sp.latex(l_ode["Q_L_at_beta_H"]),
        "C_coefficient": sp.latex(l_ode["C"]),
        "value_matching": sp.latex(l_full["value_matching"]),
        "smooth_pasting": sp.latex(l_full["smooth_pasting"]),
        "A1_expr": sp.latex(l_full["A1_from_smooth_pasting"]),
        "A_eff": sp.latex(a_eff_result["A_eff"]),
        "dA_eff_dphi": sp.latex(a_eff_result["dA_dphi"]),
        "dA_eff_dlam": sp.latex(a_eff_result["dA_dlam"]),
    }
