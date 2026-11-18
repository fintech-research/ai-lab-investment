"""Symbolic derivation and verification of the paper's closed-form algebra.

Uses sympy to verify the identities behind Propositions 1 to 3, the
L-regime ODE solutions of the model of record and the recovery rule, and
cross-checks a few of them against the numerical code. The symbolic
functions (sections 1 to 10) return the expressions they derive and, for
each identity stated in their docstrings, a residual that simplifies to
zero when the identity holds;
`notebooks/model_derivation.ipynb` displays them and
`tests/test_symbolic_duopoly.py` asserts the residuals. A zero residual
verifies that identity and nothing more: optimality of a candidate policy,
existence or uniqueness of a trigger, and every equilibrium level are
outside this module.

The model of record (issue #176) prices the L-regime option on a piecewise
forcing term. Below the post-switch trigger X_H* the forcing is lambda B_H
X^{beta_H} and

    F_L(X) = A1 * X^{beta_L_plus} + Gamma * X^{beta_H},

with Gamma = -lambda B_H / Q_L(beta_H) (eq-particular-C). Above X_H*, with
the post-switch scale precommitted, the forcing is affine and the solution
adds X^{beta_L_minus} and an affine particular solution (eq-option-L-upper).
The coefficients are pinned by matching at X_H* and at the trigger.

The single power F_L proportional to X^{beta_H} on the whole continuation
region (A1 = 0) is the *pure-power approximation*: a decision rule whose
smooth-fit coefficient (about 16.5 at baseline) differs from Gamma (about
21.1), so it solves the L-regime HJB on no interval. The L-regime
insufficiency condition (1 - 1/beta_L_plus)/alpha >= 1 (about 1.67 at
baseline, the former Assumption A3) says that the standalone L-regime scale
problem has no interior optimum; it does not make A1 vanish, and the exact
precommitted-scale solution has A1 < 0 at baseline
(`verify_pure_power_approximation`).

References:
- Guo, Miao & Morellec (2005): "Irreversible Investment with Regime Shifts"
- Dixit & Pindyck (1994): Chapter 6 (regime-switching extensions)
"""

from typing import Any, cast

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


def post_switch_capacity_closed_form(syms):
    """Closed-form post-switch capacity K_H*, eq-K-H (Proposition 1(ii)).

    Steps 1 to 4 of the Proof of Proposition 1: with payoff a K^alpha X -
    Theta(K), Theta(K) = c K^gamma + delta K / r, the option coefficient is
    proportional to h(K) = (a K^alpha)^{beta_H} / Theta(K)^{beta_H - 1}, and
    d ln h / dK = 0 is eq-foc-K, which does not involve a. Returns the
    first-order condition, its residual at the closed form (zero), and the
    small- and large-K exponents of h, whose signs are the two bounds of
    (A2).
    """
    alpha, gamma_, c, delta, r = (
        syms["alpha"],
        syms["gamma"],
        syms["c"],
        syms["delta"],
        syms["r"],
    )
    beta_H, K = syms["beta_H"], syms["K"]
    a = sp.Symbol("a", positive=True)
    Theta = c * K**gamma_ + delta * K / r
    log_h = beta_H * sp.log(a * K**alpha) - (beta_H - 1) * sp.log(Theta)
    foc = sp.simplify(sp.diff(log_h, K))
    K_H_base = (
        delta
        * (alpha * beta_H - beta_H + 1)
        / (r * c * (gamma_ * (beta_H - 1) - alpha * beta_H))
    )
    K_H = K_H_base ** (1 / (gamma_ - 1))
    # The numerator of the condition is linear in u = K^{gamma - 1}.
    u = sp.Symbol("u", positive=True)
    numerator = sp.expand(sp.numer(sp.together(foc)) / K)
    linear_in_u = sp.expand(sp.powsimp(numerator.subs(K**gamma_, K * u), force=True))
    linear_in_u = sp.expand(sp.simplify(linear_in_u.subs(K ** (gamma_ - 1), u)))
    u_solution = sp.solve(linear_in_u, u)
    # K_H^{gamma - 1} is K_H_base, positive under (A2).
    residual = sp.simplify(u_solution[0] - K_H_base) if u_solution else None
    return {
        "Theta": Theta,
        "foc": foc,
        "foc_numerator_in_u": linear_in_u,
        "u_solution": u_solution,
        "K_H": K_H,
        "K_H_power_gamma_minus_1": K_H_base,
        "foc_residual_at_K_H": residual,
        "a_drops_out": not foc.has(a),
        "exponent_small_K": alpha * beta_H - (beta_H - 1),
        "exponent_large_K": alpha * beta_H - gamma_ * (beta_H - 1),
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

    Below the post-switch trigger X_H*, F_H(X) = B_H * X^{beta_H}, so on
    that interval this is a second-order Euler ODE with a non-homogeneous
    term lambda * B_H * X^{beta_H}. Above X_H* the forcing is the exercised
    post-switch payoff (`l_regime_upper_particular`).

    GENERAL SOLUTION BELOW X_H*:
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

    # Residual of C * X^{beta_H} in the ODE below X_H*
    X = syms["X"]
    F_p = C_expr * X**beta_H
    residual = (
        sp.Rational(1, 2) * sigma**2 * X**2 * sp.diff(F_p, X, 2)
        + mu_L * X * sp.diff(F_p, X)
        - (r + lam) * F_p
        + lam * B_H * X**beta_H
    )

    # Q_L(beta_H) = (mu_L - mu_H) beta_H - lambda once Q_H(beta_H) = 0
    mu_H = syms["mu_H"]
    Q_H_at_beta_H = (
        sp.Rational(1, 2) * sigma**2 * beta_H * (beta_H - 1) + mu_H * beta_H - r
    )
    Q_L_reduced = (mu_L - mu_H) * beta_H - lam

    return {
        "Q_L_at_beta_H": Q_L_at_beta_H,
        "C": C_expr,
        "ode_residual": sp.simplify(residual),
        "Q_L_at_beta_H_reduced": Q_L_reduced,
        "Q_L_reduction_residual": sp.expand(
            Q_L_at_beta_H - Q_H_at_beta_H - Q_L_reduced
        ),
        "general_solution": (
            "F_L(X) = A1 * X^{beta_L_plus} + C * X^{beta_H} for X < X_H*"
        ),
        "note": (
            "Valid below the post-switch trigger X_H* only. Setting A1 = 0 "
            "and extending C * X^{beta_H}'s functional form to the whole "
            "continuation region is the pure-power approximation, not a "
            "solution of the HJB (see `pure_power_smooth_fit`)."
        ),
    }


def l_regime_upper_particular(syms):
    """Particular solution above X_H* with the post-switch scale precommitted.

    Above X_H* a switch is followed by immediate exercise at K_H*, so the
    forcing is lambda * (p_H X - q_H), with p_H = A_H K_H*^alpha and
    q_H = delta K_H*/r + I(K_H*). The affine particular solution is

        g X + k,  g = lambda p_H / (r + lambda - mu_L),
                  k = -lambda q_H / (r + lambda)

    (eq-option-L-upper), to which G_1 X^{beta_L+} + G_2 X^{beta_L-} is added.
    """
    X = syms["X"]
    sigma = syms["sigma"]
    mu_L = syms["mu_L"]
    r = syms["r"]
    lam = syms["lam"]
    p_H = sp.Symbol("p_H", positive=True)
    q_H = sp.Symbol("q_H", positive=True)

    g = lam * p_H / (r + lam - mu_L)
    k = -lam * q_H / (r + lam)
    F_p = g * X + k
    residual = (
        sp.Rational(1, 2) * sigma**2 * X**2 * sp.diff(F_p, X, 2)
        + mu_L * X * sp.diff(F_p, X)
        - (r + lam) * F_p
        + lam * (p_H * X - q_H)
    )
    return {"p_H": p_H, "q_H": q_H, "g": g, "k": k, "residual": sp.simplify(residual)}


def two_region_conditions(syms):
    """Matching conditions of the two-region system (Proposition 1(iii)).

    Lower branch A1 X^{b+} + Gamma X^{h} on (0, X_H*), upper branch
    G1 X^{b+} + G2 X^{b-} + g X + k on (X_H*, X*), exercise payoff
    a X - b. Value and slope matching at X_H* and value matching and
    smooth pasting at X* are four conditions, linear in (A1, G1, G2) given
    X*, so the system reduces to one scalar equation in X* at a given
    capacity. Returns the four conditions and the coefficients solved from
    three of them; the fourth is the scalar residual in X*.
    """
    X_H = sp.Symbol("X_H^*", positive=True)
    X_s = syms["X_star"]
    bp = syms["beta_L_plus"]
    bn = syms["beta_L_minus"]
    h = syms["beta_H"]
    Gamma = sp.Symbol("Gamma", positive=True)
    A1, G1, G2 = sp.symbols("A_1 G_1 G_2")
    g, k = sp.symbols("g k")
    a, b = sp.symbols("a b", positive=True)

    lower = A1 * X_H**bp + Gamma * X_H**h
    lower_slope = bp * A1 * X_H ** (bp - 1) + h * Gamma * X_H ** (h - 1)

    def upper(x):
        return G1 * x**bp + G2 * x**bn + g * x + k

    def upper_slope(x):
        return bp * G1 * x ** (bp - 1) + bn * G2 * x ** (bn - 1) + g

    conditions = {
        "value_matching_X_H": sp.Eq(lower, upper(X_H)),
        "slope_matching_X_H": sp.Eq(lower_slope, upper_slope(X_H)),
        "value_matching_X_star": sp.Eq(upper(X_s), a * X_s - b),
        "smooth_pasting_X_star": sp.Eq(upper_slope(X_s), a),
    }
    coeffs = sp.solve(
        [
            conditions["value_matching_X_star"],
            conditions["smooth_pasting_X_star"],
            conditions["value_matching_X_H"],
        ],
        [G1, G2, A1],
        dict=True,
    )[0]
    scalar = sp.simplify((lower_slope - upper_slope(X_H)).subs(coeffs))
    return {
        "conditions": conditions,
        "coefficients": coeffs,
        "scalar_equation_in_X_star": scalar,
        "symbols": {
            "X_H": X_H,
            "Gamma": Gamma,
            "A1": A1,
            "G1": G1,
            "G2": G2,
            "g": g,
            "k": k,
            "a": a,
            "b": b,
        },
    }


def premium_representation(syms):
    """Step 7 of the Proof of Proposition 1: the exercise premium.

    With S the value of never investing before the switch and P(X; K) the
    payoff, the policy "invest at X_bar" is worth

        F(X) = S(X) + [P(X_bar) - S(X_bar)] (X / X_bar)^{beta_L+},  X < X_bar

    (eq-premium). Its added term solves the homogeneous L-regime equation,
    and the first-order condition of the coefficient [P - S] X_bar^{-b+} in
    X_bar is smooth pasting of F against P. Returns both residuals: the
    homogeneous residual of the added term, and smooth pasting minus a
    multiple of the first-order condition, each zero.
    """
    X = syms["X"]
    bp = syms["beta_L_plus"]
    sigma, mu_L, r, lam = syms["sigma"], syms["mu_L"], syms["r"], syms["lam"]
    xb = sp.Symbol("Xbar", positive=True)
    P = cast(Any, sp.Function("P"))
    S = cast(Any, sp.Function("S"))

    coeff = (P(xb) - S(xb)) * xb ** (-bp)
    F = S(X) + coeff * X**bp

    added = coeff * X**bp
    homog = (
        sp.Rational(1, 2) * sigma**2 * X**2 * sp.diff(added, X, 2)
        + mu_L * X * sp.diff(added, X)
        - (r + lam) * added
    )
    Q_L_bp = sp.Rational(1, 2) * sigma**2 * bp * (bp - 1) + mu_L * bp - (r + lam)
    homog_residual = sp.simplify(homog - Q_L_bp * added)

    smooth_pasting = sp.diff(F, X).subs(X, xb).doit() - sp.diff(P(xb), xb)
    foc = sp.diff(coeff, xb)
    # Smooth pasting equals -X_bar^{b+} times the first-order condition.
    sp_residual = sp.simplify(smooth_pasting + xb**bp * foc)
    return {
        "coefficient": coeff,
        "value": F,
        "foc_in_Xbar": sp.simplify(foc),
        "smooth_pasting": sp.simplify(smooth_pasting),
        "homogeneous_residual": homog_residual,
        "smooth_pasting_minus_foc": sp_residual,
        "Q_L_at_beta_L_plus": Q_L_bp,
    }


def pure_power_smooth_fit(syms):
    """The pure-power approximation (eq-trigger-phi) and why it is one.

    With a single power B X^{h} on the whole continuation region against
    the payoff a X - b, smooth pasting and value matching give
    X^pp = h/(h-1) * b/a and B = (a X^pp - b) / (X^pp)^h. Substituted in
    the L-regime HJB below X_H*, B X^h leaves the residual
    Q_L(h) (B - Gamma) X^h, zero only if B equals Gamma of
    eq-particular-C; at baseline B is about 16.5 and Gamma about 21.1.
    """
    X = syms["X"]
    h = syms["beta_H"]
    sigma, mu_L, r, lam = syms["sigma"], syms["mu_L"], syms["r"], syms["lam"]
    B_H = syms["B_H"]
    X_s = syms["X_star"]
    a, b = sp.symbols("a b", positive=True)
    B = sp.Symbol("B", positive=True)

    vm = sp.Eq(B * X_s**h, a * X_s - b)
    sp_cond = sp.Eq(h * B * X_s ** (h - 1), a)
    B_from_sp = sp.solve(sp_cond, B)[0]
    trigger = sp.simplify(sp.solve(vm.subs(B, B_from_sp), X_s)[0])
    sol = {B: sp.simplify(B_from_sp.subs(X_s, trigger)), X_s: trigger}

    Q_L_h = sp.Rational(1, 2) * sigma**2 * h * (h - 1) + mu_L * h - (r + lam)
    Gamma = -lam * B_H / Q_L_h
    F = B * X**h
    residual = (
        sp.Rational(1, 2) * sigma**2 * X**2 * sp.diff(F, X, 2)
        + mu_L * X * sp.diff(F, X)
        - (r + lam) * F
        + lam * B_H * X**h
    )
    return {
        "trigger": trigger,
        "smooth_fit_coeff": sp.simplify(sol[B]),
        "hjb_residual": sp.simplify(residual),
        "hjb_residual_factored": Q_L_h * (B - Gamma) * X**h,
        "factorization_residual": sp.simplify(residual - Q_L_h * (B - Gamma) * X**h),
        "B": B,
        "a": a,
        "b": b,
    }


def _log_residual(lhs, rhs):
    """log(lhs) - log(rhs), expanded and simplified; zero iff lhs = rhs.

    For expressions that are positive under the symbols' assumptions, where
    sympy does not combine fractional powers of products on its own.
    """
    diff = sp.expand_log(sp.log(lhs), force=True) - sp.expand_log(
        sp.log(rhs), force=True
    )
    return sp.simplify(diff)


def waiting_margin_asymptotic(syms):
    """Leading-order growth of the two values behind eq-waiting-margin.

    With scale chosen at the switch, the post-switch payoff is the envelope
    max_K [A_H K^alpha X - delta K/r - c K^gamma], and the best pre-switch
    payoff is the same envelope with g(phi*) in place of A_H. Dropping the
    operating cost, which is of lower order in X, the maximizer of
    a X K^alpha - c K^gamma solves K^{gamma - alpha} = alpha a X/(c gamma),
    so the envelope is (1 - alpha/gamma) a X K^alpha = E(a) X^theta with
    theta = gamma/(gamma - alpha). The waiting value forced by
    lambda E(A_H) X^theta has the particular solution
    lambda E(A_H) X^theta / (-Q_L(theta)), and the ratio of the two leading
    coefficients is lambda / (-Q_L(theta)) (A_H / g)^theta, the waiting
    margin. This verifies the ratio of leading terms; it is not a proof of
    the criterion, which the paper labels as derived from growth rates and
    confirmed numerically.
    """
    X = syms["X"]
    alpha, gamma_, c = syms["alpha"], syms["gamma"], syms["c"]
    sigma, mu_L, r, lam = syms["sigma"], syms["mu_L"], syms["r"], syms["lam"]
    a = sp.Symbol("a", positive=True)
    A_H = sp.Symbol("A_H", positive=True)
    g = sp.Symbol("g", positive=True)
    K = syms["K"]
    theta = gamma_ / (gamma_ - alpha)

    payoff = a * X * K**alpha - c * K**gamma_
    # First-order condition, written as K^{gamma - alpha} = alpha a X/(c gamma)
    foc = sp.diff(payoff, K)
    foc_residual = sp.simplify(
        sp.expand(foc * K ** (1 - alpha) / (c * gamma_))
        - (alpha * a * X / (c * gamma_) - K ** (gamma_ - alpha))
    )
    # At the maximizer the payoff is (1 - alpha/gamma) a X K^alpha
    K_g = sp.Symbol("K_g", positive=True)  # stands for K^{gamma - alpha}
    value_residual = sp.simplify(
        (a * X * K**alpha - c * K**alpha * K_g).subs(K_g, alpha * a * X / (c * gamma_))
        - (1 - alpha / gamma_) * a * X * K**alpha
    )

    def E(coef):
        K_opt = (alpha * coef * X / (c * gamma_)) ** (1 / (gamma_ - alpha))
        return (1 - alpha / gamma_) * coef * X * K_opt**alpha / X**theta

    # E(a) does not depend on X
    E_a = E(a)
    growth_residual = sp.simplify(sp.diff(sp.expand_log(sp.log(E_a), force=True), X))
    Q_L_theta = (
        sp.Rational(1, 2) * sigma**2 * theta * (theta - 1) + mu_L * theta - (r + lam)
    )
    # Positive under Q_L(theta) < 0, which holds when theta < beta_L^+.
    neg_Q = sp.Symbol("negQ", positive=True)
    margin = lam * E(A_H) / neg_Q / E(g)
    target = lam / neg_Q * (A_H / g) ** theta
    return {
        "theta": theta,
        "envelope_coefficient": sp.simplify(E_a),
        "envelope_foc_residual": foc_residual,
        "envelope_value_residual": value_residual,
        "growth_residual": growth_residual,
        "margin": margin.subs(neg_Q, -Q_L_theta),
        "margin_residual": _log_residual(margin, target),
        "Q_L_theta": Q_L_theta,
    }


def l_regime_option_value_full(syms):
    """Full L-regime option value with value-matching and smooth-pasting.

    For a firm with installed value V_L(X) = A_eff * X - delta*K/r,
    the option value is:

    F_L(X) = A1 * X^{beta_L_plus} + C * X^{beta_H},  X < min(X_H*, X*)

    These are the conditions of the one-region case, in which the trigger
    lies below the post-switch trigger X_H*. At baseline X* > X_H* and the
    conditions are those of `two_region_conditions`.

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
            "equation, on the lower branch only (X* < X_H*). It does not "
            "simplify to beta_H/(beta_H-1) * cost/A_eff, which is the "
            "trigger of the pure-power approximation (A1 = 0). At baseline "
            "X* > X_H*, and the trigger solves `two_region_conditions`."
        ),
    }


# =====================================================================
# 4. L-regime insufficiency condition (descriptive; the former A3)
# =====================================================================


def l_regime_insufficiency(syms):
    """The L-regime insufficiency condition, eq-l-insufficiency.

    Phi_L = (1 - 1/beta_L_plus)/alpha >= 1 says that the standalone
    L-regime scale problem (no switch credited, discount r + lambda) has
    no interior optimal capacity: an interior optimum would need
    1/gamma < Phi_L < 1, the L-regime analogue of (A2). That is all it
    says. It does not imply A1 = 0 in eq-option-L-general and licenses no
    simplification of the option value; the exact precommitted-scale
    solution has A1 < 0 at baseline (`verify_pure_power_approximation`).
    Equivalently, the condition is alpha <= 1 - 1/beta_L_plus.
    """
    beta_L_plus = syms["beta_L_plus"]
    alpha = syms["alpha"]
    gamma_ = syms["gamma"]

    phi_L = (1 - 1 / beta_L_plus) / alpha

    return {
        "option_premium_ratio_L": phi_L,
        "insufficiency_condition": phi_L >= 1,
        "alpha_bound": 1 - 1 / beta_L_plus,
        "standalone_interior_scale_condition": sp.And(1 / gamma_ < phi_L, phi_L < 1),
        "note": (
            "Descriptive only: the standalone L-regime scale problem has no "
            "interior optimum when phi_L >= 1. Nothing about A1 follows."
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

    # Quotient-rule form of Proof of Proposition 2(ii)
    Pi_L = inf_cap**alpha
    Pi_H = tr_cap**alpha * A_H
    dA_dlam_form = (Pi_H * (r - mu_L) - Pi_L) / denom_L**2

    return {
        "A_eff": A_eff,
        "dA_dphi": sp.simplify(dA_dphi),
        "dA_dlam": sp.simplify(dA_dlam),
        "dA_dlam_quotient_form": dA_dlam_form,
        "dA_dlam_residual": sp.simplify(dA_dlam - dA_dlam_form),
    }


def installed_value_in_lambda(syms):
    """Shape in lambda of installed value at fixed (X, K, phi) (issue #181).

    V(lambda) = A_eff(lambda) X - delta K / r with A_eff = (a + lambda b) /
    (d + lambda), a = [(1-phi)K]^alpha, b = (phi K)^alpha / (r - mu_H),
    d = r - mu_L, G = b d - a. Identities (residuals zero):

    - dV/dlambda = X G / (d + lambda)^2;
    - d2V/dlambda2 = -2 X G / (d + lambda)^3, so V is increasing and
      strictly concave on lambda >= 0 iff G > 0, the faith condition of
      Proposition 2(ii), i.e. phi > phi_underbar with monopoly shares;
    - news asymmetry, for 0 < h < d + lambda: [V(lambda) - V(lambda - h)] -
      [V(lambda + h) - V(lambda)] = 2 h^2 X G / [(d+lambda)(d+lambda-h)
      (d+lambda+h)];
    - dG/dphi = alpha [b d / phi + a / (1 - phi)] > 0;
    - the semi-elasticity of A_eff in lambda is (rho d - 1) / [(1 + lambda
      rho)(d + lambda)] with rho = b / a, whose derivative in rho is
      1 / (1 + lambda rho)^2 > 0.
    """
    r, mu_L, mu_H = syms["r"], syms["mu_L"], syms["mu_H"]
    lam, alpha, K, phi, X = (
        syms["lam"],
        syms["alpha"],
        syms["K"],
        syms["phi"],
        syms["X"],
    )
    delta = syms["delta"]
    h = sp.Symbol("h", positive=True)
    rho = sp.Symbol("rho", positive=True)
    a = ((1 - phi) * K) ** alpha
    b = (phi * K) ** alpha / (r - mu_H)
    d = r - mu_L
    G = b * d - a
    V = (a + lam * b) / (d + lam) * X - delta * K / r
    asym = (V - V.subs(lam, lam - h)) - (V.subs(lam, lam + h) - V)
    semi = sp.diff(sp.log((a + lam * b) / (d + lam)), lam)
    semi_rho = (rho * d - 1) / ((1 + lam * rho) * (d + lam))
    return {
        "V": V,
        "G": G,
        "d1_residual": sp.simplify(sp.diff(V, lam) - X * G / (d + lam) ** 2),
        "d2_residual": sp.simplify(sp.diff(V, lam, 2) + 2 * X * G / (d + lam) ** 3),
        "asymmetry_residual": sp.simplify(
            asym - 2 * h**2 * X * G / ((d + lam) * (d + lam - h) * (d + lam + h))
        ),
        "dG_dphi_residual": sp.simplify(
            sp.diff(G, phi) - alpha * (b * d / phi + a / (1 - phi))
        ),
        "semi_elasticity_residual": sp.simplify(semi - semi_rho.subs(rho, b / a)),
        "semi_elasticity_rho_residual": sp.simplify(
            sp.diff(semi_rho, rho) - 1 / (1 + lam * rho) ** 2
        ),
    }


# =====================================================================
# 6. Optimal training fraction (Proposition 1(i))
# =====================================================================


def optimal_phi_conditions(syms):
    """Derive the first-order condition for the optimal training fraction.

    The pre-switch exercise payoff is A_eff(phi, K) X - delta K/r - I(K),
    and neither the cost nor the continuation value of a firm that has not
    invested depends on phi, so at every capacity and every trigger the
    allocation maximizes A_eff: the condition is dA_eff/dphi = 0.
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


def phi_star_closed_form(syms):
    """The closed form phi* = rho/(1 + rho), eq-phi-star, and two identities.

    With g(phi) = (1-phi)^alpha + lambda A_H phi^alpha (the common factor
    K^alpha/(r - mu_L + lambda) dropped) and rho = (lambda A_H)^{1/(1-alpha)}:

    1. dg/dphi vanishes at phi = rho/(1 + rho);
    2. d^2 g/dphi^2 < 0 on (0, 1), so the critical point is unique;
    3. at phi*, the inference term is the fraction 1 - phi* of g, which is
       why the inference business earns the fraction 1 - phi* of revenue at
       the optimal allocation (used for the recovery rule, section 8).
    """
    r, mu_H, lam, alpha = syms["r"], syms["mu_H"], syms["lam"], syms["alpha"]
    phi = syms["phi"]
    rho = sp.Symbol("rho", positive=True)

    A_H = 1 / (r - mu_H)
    g = (1 - phi) ** alpha + lam * A_H * phi**alpha
    rho_expr = (lam * A_H) ** (1 / (1 - alpha))
    phi_star = rho / (1 + rho)

    # Write lambda A_H = rho^{1 - alpha}, which is the definition of rho.
    lam_of_rho = rho ** (1 - alpha) * (r - mu_H)
    dg = sp.diff(g, phi).subs(lam, lam_of_rho)
    foc_residual = sp.simplify(sp.powsimp(dg.subs(phi, phi_star), force=True))

    share = (1 - phi) ** alpha / g
    share_residual = sp.simplify(
        sp.powsimp(
            (share - (1 - phi)).subs(lam, lam_of_rho).subs(phi, phi_star), force=True
        )
    )
    second = sp.diff(g, phi, 2)
    second_factored = (
        alpha
        * (alpha - 1)
        * ((1 - phi) ** (alpha - 2) + lam * A_H * phi ** (alpha - 2))
    )
    # phi = 1/(1 + z) with z > 0 parametrizes (0, 1) with 1 - phi > 0 known.
    z = sp.Symbol("z", positive=True)
    return {
        "g": g,
        "rho": rho_expr,
        "phi_star": phi_star.subs(rho, rho_expr),
        "foc_residual": foc_residual,
        "second_derivative": sp.simplify(second),
        "second_derivative_residual": sp.simplify(
            sp.powsimp(
                sp.expand_power_base(
                    (second - second_factored).subs(phi, 1 / (1 + z)), force=True
                ),
                force=True,
            )
        ),
        "inference_share_residual": share_residual,
        "dphi_drho": sp.simplify(sp.diff(phi_star, rho)),
        "drho_dlam": sp.simplify(sp.diff(rho_expr, lam)),
        "drho_dmu_H": sp.simplify(sp.diff(rho_expr, mu_H)),
        "drho_dmu_L": sp.diff(rho_expr, syms["mu_L"]),
    }


# =====================================================================
# 7. Default boundary (Proposition 2)
# =====================================================================


def default_boundary_derivation(syms):
    """Derive the endogenous default boundary and its comparative statics.

    X_D = [beta_neg / (beta_neg - 1)] * [c_D/r + delta*K/r] / A_eff

    This function treats the markup M = beta_neg/(beta_neg - 1) and A_eff
    as independent symbols, so it gives the partial effects of A_eff and of
    the coupon only. The effect of lambda runs through both, with opposite
    signs (`markup_channel`, `exact_faith_threshold`): dA_eff/dlambda > 0 is
    not sufficient for dX_D/dlambda < 0.
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
            "dX_D/dlambda combines the A_eff channel (negative when "
            "phi > phi_underbar) and the markup channel (positive): "
            "dX_D/dlambda < 0 iff phi > phi_tilde (eq-phi-tilde)."
        ),
    }


def markup_channel(syms):
    """The markup factor M = beta_L^-/(beta_L^- - 1) as a function of lambda.

    beta_L^- = (-(mu_L - sigma^2/2) - R)/sigma^2 with
    R = sqrt((mu_L - sigma^2/2)^2 + 2 sigma^2 (r + lambda)). Verifies
    dM/dlambda = 1/[(beta_L^- - 1)^2 R] and the semi-elasticity
    m = (dM/dlambda)/M = 1/[beta_L^- (beta_L^- - 1) R], both positive since
    beta_L^- < 0 (Proof of Proposition 2, markup channel).
    """
    sigma, mu_L, r, lam = syms["sigma"], syms["mu_L"], syms["r"], syms["lam"]
    b_ = mu_L - sigma**2 / 2
    R = sp.sqrt(b_**2 + 2 * sigma**2 * (r + lam))
    beta_neg = (-b_ - R) / sigma**2
    M = beta_neg / (beta_neg - 1)
    dM = sp.diff(M, lam)
    m = dM / M
    Q_L = sp.Rational(1, 2) * sigma**2 * beta_neg * (beta_neg - 1) + mu_L * beta_neg
    return {
        "beta_neg": beta_neg,
        "R": R,
        "M": M,
        "root_residual": sp.simplify(sp.expand(Q_L - (r + lam))),
        "dM_dlam": dM,
        "dM_dlam_residual": sp.simplify(dM - 1 / ((beta_neg - 1) ** 2 * R)),
        "m": m,
        "m_residual": sp.simplify(m - 1 / (beta_neg * (beta_neg - 1) * R)),
    }


def exact_faith_threshold(syms):
    """The thresholds phi_underbar (eq-phi-underbar) and phi_tilde (eq-phi-tilde).

    With symmetric shares, Pi_L = (1-phi)^alpha and Pi_H = phi^alpha/(r-mu_H)
    up to the common factor K^alpha s. Then

        d ln X_D / d lambda = m - d ln A_eff / d lambda,
        d ln A_eff / d lambda = [Pi_H (r - mu_L) - Pi_L] / [(Pi_L + lambda Pi_H) Delta],

    with Delta = r - mu_L + lambda. The net condition d X_D / d lambda < 0 is
    linear in (Pi_L, Pi_H) and holds iff Pi_H/Pi_L exceeds
    (1 + m Delta)/((r - mu_L) - m lambda Delta), i.e. iff phi > phi_tilde,
    given the regularity condition (r - mu_L) > m lambda Delta. Returns the
    residuals of: the log-derivative of A_eff; the reduction of both
    conditions to linear functions of the odds zeta = (phi/(1-phi))^alpha;
    the odds of phi = W^{1/alpha}/(1 + W^{1/alpha}), which is W; the net
    condition at the odds of phi_tilde and the A_eff-channel condition at
    the odds of phi_underbar (both zero); the m -> 0 limit of phi_tilde
    minus phi_underbar (zero); and the derivatives of ln Omega in alpha, r,
    mu_H and mu_L against their signed forms (zero): under (A1), with
    q = (r - mu_H)/(r - mu_L) < 1, phi_underbar is increasing in alpha and
    in r and decreasing in mu_H - mu_L (the last sentence of Proposition
    2(ii)).
    """
    r, mu_L, mu_H = syms["r"], syms["mu_L"], syms["mu_H"]
    lam, alpha, phi = syms["lam"], syms["alpha"], syms["phi"]
    m = sp.Symbol("m", positive=True)
    Delta = r - mu_L + lam

    Pi_L = (1 - phi) ** alpha
    Pi_H = phi**alpha / (r - mu_H)
    A = (Pi_L + lam * Pi_H) / Delta
    dlnA = sp.diff(sp.log(A), lam)
    dlnA_form = (Pi_H * (r - mu_L) - Pi_L) / ((Pi_L + lam * Pi_H) * Delta)

    Omega = ((r - mu_H) / (r - mu_L)) ** (1 / alpha)
    phi_under = Omega / (1 + Omega)
    T = (r - mu_H) * (1 + m * Delta) / ((r - mu_L) - m * lam * Delta)
    Omega_t = T ** (1 / alpha)
    phi_tilde = Omega_t / (1 + Omega_t)

    net = Pi_H * (r - mu_L) - Pi_L - m * (Pi_L + lam * Pi_H) * Delta

    # Both conditions divided by Pi_L are linear in the odds
    # zeta = (phi/(1-phi))^alpha, the only way phi enters.
    zeta = sp.Symbol("zeta", positive=True)
    odds = phi**alpha / (1 - phi) ** alpha
    net_z = (
        zeta * (r - mu_L) / (r - mu_H) - 1 - m * Delta * (1 + lam * zeta / (r - mu_H))
    )
    channel_z = zeta * (r - mu_L) / (r - mu_H) - 1
    linear_residual = sp.simplify(net / Pi_L - net_z.subs(zeta, odds))

    # Comparative statics of phi_underbar, which is increasing in Omega:
    # ln Omega = ln q / alpha with q = (r - mu_H)/(r - mu_L) < 1.
    log_Omega = sp.log((r - mu_H) / (r - mu_L)) / alpha
    dlnOmega = {
        "alpha": sp.diff(log_Omega, alpha),
        "r": sp.diff(log_Omega, r),
        "mu_H": sp.diff(log_Omega, mu_H),
        "mu_L": sp.diff(log_Omega, mu_L),
    }
    dlnOmega_form = {
        "alpha": -sp.log((r - mu_H) / (r - mu_L)) / alpha**2,
        "r": (mu_H - mu_L) / (alpha * (r - mu_H) * (r - mu_L)),
        "mu_H": -1 / (alpha * (r - mu_H)),
        "mu_L": 1 / (alpha * (r - mu_L)),
    }

    # phi = W^{1/alpha}/(1 + W^{1/alpha}) has odds^alpha = W (W > 0).
    W = sp.Symbol("W", positive=True)
    phi_of_W = W ** (1 / alpha) / (1 + W ** (1 / alpha))
    odds_residual = _log_residual(odds.subs(phi, phi_of_W), W)

    return {
        "Omega": Omega,
        "phi_underbar": phi_under,
        "Omega_tilde": Omega_t,
        "phi_tilde": phi_tilde,
        "m": m,
        "dlnA_dlam_residual": sp.simplify(dlnA - dlnA_form),
        "net_condition": net,
        "net_in_odds": net_z,
        "linear_in_odds_residual": linear_residual,
        "odds_residual": odds_residual,
        "net_at_phi_tilde": sp.simplify(net_z.subs(zeta, T)),
        "a_eff_channel_at_phi_underbar": sp.simplify(
            channel_z.subs(zeta, (r - mu_H) / (r - mu_L))
        ),
        "limit_m_to_zero_residual": sp.simplify(phi_tilde.subs(m, 0) - phi_under),
        "dlnOmega": dlnOmega,
        "dlnOmega_residuals": {
            key: sp.simplify(dlnOmega[key] - dlnOmega_form[key]) for key in dlnOmega
        },
        "regularity_condition": (r - mu_L) - m * lam * Delta > 0,
        "dlnXD_dphi_at_phi_star_note": (
            "X_D is proportional to 1/A_eff, so at phi* (where dA_eff/dphi = 0) "
            "a reallocation has no first-order effect on X_D."
        ),
    }


# =====================================================================
# 8. Recovery rule (eq-recovery)
# =====================================================================


def recovery_split(syms):
    """Installed value splits into the inference and training businesses.

    Lambda(X) = [(1-phi)K]^alpha X/Delta - delta (1-phi) K / r is the
    inference business net of the operating cost of its capacity (single
    firm or symmetric shares). Then:

    1. V_L = Lambda + training business, with training business
       lambda A_H (phi K)^alpha X/Delta - delta phi K / r (exact identity);
    2. at phi* the inference term is the fraction 1 - phi* of A_eff
       (`phi_star_closed_form`), so Lambda(X) = (1 - phi*) V_L(X);
    3. at the single-boundary default boundary A_eff X_D = M (C_D + delta K)/r,
       so Lambda(X_D) < 0 iff C_D < delta K (1 - M)/M.

    Returns residuals for 1 and 3 (zero) and the coupon bound of 3. The caps
    of eq-recovery (at U(X_D) and at C_D/r) are definitions, not identities,
    and are not checked here.
    """
    r, mu_L, mu_H = syms["r"], syms["mu_L"], syms["mu_H"]
    lam, alpha, phi, K, X = (
        syms["lam"],
        syms["alpha"],
        syms["phi"],
        syms["K"],
        syms["X"],
    )
    delta = syms["delta"]
    Delta = r - mu_L + lam
    A_H = 1 / (r - mu_H)
    M = sp.Symbol("M", positive=True)
    C_D = sp.Symbol("C_D", positive=True)

    A_eff = ((1 - phi) * K) ** alpha / Delta + lam * A_H * (phi * K) ** alpha / Delta
    V_L = A_eff * X - delta * K / r
    Lam = ((1 - phi) * K) ** alpha * X / Delta - delta * (1 - phi) * K / r
    training = lam * A_H * (phi * K) ** alpha * X / Delta - delta * phi * K / r

    # At phi*, Lambda = (1 - phi)(A_eff X - delta K / r); evaluate at X_D.
    A_eff_sym = sp.Symbol("A_eff", positive=True)
    X_D = M * (C_D + delta * K) / (r * A_eff_sym)
    Lam_at_XD = (1 - phi) * (A_eff_sym * X_D - delta * K / r)
    bound = delta * K * (1 - M) / M
    return {
        "Lambda": Lam,
        "training_business": training,
        "split_residual": sp.simplify(V_L - Lam - training),
        "Lambda_at_X_D": sp.simplify(Lam_at_XD),
        "coupon_bound": bound,
        "sign_residual": sp.simplify(Lam_at_XD - (1 - phi) * M / r * (C_D - bound)),
    }


# =====================================================================
# 9. Proposition 3: Tullock contest and the follower after the switch
# =====================================================================


def tullock_factorization(syms):
    """Contest derivative and the allocation condition at a common phi.

    f(u) = u^{2 alpha}/(u^alpha + ubar^alpha) has
    f'(u) = alpha u^{alpha-1} s (2 - s), s = u^alpha/(u^alpha + ubar^alpha),
    and s is invariant to scaling both capacities. At a common allocation
    phi the share is the same in both regimes, so

        d A_eff,i/d phi_i = alpha K_i^alpha s (2 - s) [-w_L (1-phi)^{alpha-1}
                                                       + w_H phi^{alpha-1}],

    the single firm's condition times a positive multiplier: phi is a
    critical point iff phi = phi* (Proposition 3(ii), first statement). It
    says nothing about the leader's allocation in the solved game, where
    the rival is not at the leader's allocation.
    """
    alpha, phi = syms["alpha"], syms["phi"]
    u, ub, t = sp.symbols("u ubar t", positive=True)
    Ki, Kj = sp.symbols("K_i K_j", positive=True)
    w_L, w_H = sp.symbols("w_L w_H", positive=True)
    phi_i = sp.Symbol("phi_i", positive=True)

    def f(own, rival):
        return own ** (2 * alpha) / (own**alpha + rival**alpha)

    def share(own, rival):
        return own**alpha / (own**alpha + rival**alpha)

    s = share(u, ub)
    f_u = sp.diff(f(u, ub), u)
    deriv_residual = sp.simplify(f_u - alpha * u ** (alpha - 1) * s * (2 - s))
    scale_residual = sp.simplify(
        sp.powsimp(
            sp.expand_power_base(share(t * u, t * ub) - s, force=True), force=True
        )
    )

    # Chain rule: d/dphi_i of w_L f((1-phi_i) K_i) + w_H f(phi_i K_i) is
    # -K_i w_L f'((1-phi_i) K_i) + K_i w_H f'(phi_i K_i). At a common phi
    # write psi = 1 - phi (both positive) and use the f' identity above.
    psi = sp.Symbol("psi", positive=True)

    def f_prime(own, rival):
        sh = share(own, rival)
        return alpha * own ** (alpha - 1) * sh * (2 - sh)

    dA = -Ki * w_L * f_prime(psi * Ki, psi * Kj) + Ki * w_H * f_prime(
        phi * Ki, phi * Kj
    )
    s_c = share(Ki, Kj)
    factored = (
        alpha
        * Ki**alpha
        * s_c
        * (2 - s_c)
        * (-w_L * psi ** (alpha - 1) + w_H * phi ** (alpha - 1))
    )
    common_residual = sp.simplify(
        sp.powsimp(sp.expand_power_base(dA - factored, force=True), force=True)
    )
    gp = cast(Any, sp.Function("f"))
    chain = sp.diff(w_L * gp((1 - phi_i) * Ki) + w_H * gp(phi_i * Ki), phi_i)
    return {
        "f_prime": sp.simplify(f_u),
        "derivative_residual": deriv_residual,
        "scale_invariance_residual": scale_residual,
        "chain_rule": chain,
        "common_allocation_derivative": factored,
        "common_allocation_residual": common_residual,
    }


def follower_capacity_condition(syms):
    """The follower's post-switch capacity condition, eq-follower-foc.

    After the switch the follower trains with all its capacity against a
    leader with training capacity T_L, with revenue coefficient
    a(K) = A_H K^{2 alpha}/(K^alpha + T_L^alpha) and cost
    Theta(K) = delta K / r + c K^gamma. For a given K the problem is Step 1
    of the Proof of Proposition 1, so the option coefficient is proportional
    to a^{beta_H}/Theta^{beta_H - 1} and its log-derivative in ln K is

        beta_H alpha (2 - s_F) - (beta_H - 1) K Theta'/Theta.

    Verifies d ln a/d ln K = alpha (2 - s_F) and the limits of
    K Theta'/Theta (1 as K -> 0, gamma as K -> oo). Setting the
    log-derivative to zero is eq-follower-foc.
    """
    alpha, gamma_, c, delta, r = (
        syms["alpha"],
        syms["gamma"],
        syms["c"],
        syms["delta"],
        syms["r"],
    )
    beta_H, K = syms["beta_H"], syms["K"]
    T_L = sp.Symbol("T_L", positive=True)
    A_H = sp.Symbol("A_H", positive=True)

    a = A_H * K ** (2 * alpha) / (K**alpha + T_L**alpha)
    s_F = K**alpha / (K**alpha + T_L**alpha)
    Theta = delta * K / r + c * K**gamma_
    elasticity_a = sp.simplify(K * sp.diff(a, K) / a)
    elasticity_theta = sp.simplify(K * sp.diff(Theta, K) / Theta)
    log_derivative = beta_H * elasticity_a - (beta_H - 1) * elasticity_theta
    foc = sp.Eq(
        alpha * beta_H * (2 - s_F) * Theta, (beta_H - 1) * K * sp.diff(Theta, K)
    )
    foc_residual = sp.simplify((foc.lhs - foc.rhs) / Theta - log_derivative)
    gamma_num = sp.Rational(3, 2)
    theta_lim0 = sp.limit(elasticity_theta.subs(gamma_, gamma_num), K, 0, "+")
    theta_lim_inf = sp.limit(elasticity_theta.subs(gamma_, gamma_num), K, sp.oo)
    return {
        "T_L": T_L,
        "A_H": A_H,
        "a": a,
        "s_F": s_F,
        "Theta": Theta,
        "elasticity_a_residual": sp.simplify(elasticity_a - alpha * (2 - s_F)),
        "elasticity_theta": elasticity_theta,
        "log_derivative": log_derivative,
        "foc": foc,
        "foc_residual": foc_residual,
        "theta_elasticity_limits_at_gamma_3_2": (theta_lim0, theta_lim_inf),
        "small_K_condition": 2 * alpha * beta_H > beta_H - 1,
        "large_K_condition": alpha * beta_H < gamma_ * (beta_H - 1),
        "trigger": beta_H / (beta_H - 1) * Theta / (A_H * K**alpha * s_F),
    }


# =====================================================================
# 10. Green's function of the L-regime operator (eq-green)
# =====================================================================


def green_function_residual(syms):
    """eq-green solves the L-regime ODE for a generic forcing f.

    P(X) = kappa [X^{b-} int_0^X f(y) y^{-b- - 1} dy
                  + X^{b+} int_X^oo f(y) y^{-b+ - 1} dy],
    kappa = 2/(sigma^2 (b+ - b-)), with b+ and b- the roots of
    Q_L(b) = sigma^2/2 b (b - 1) + mu_L b - (r + lambda). The residual of
    sigma^2/2 X^2 P'' + mu_L X P' - (r + lambda) P + f(X) is computed by
    Leibniz's rule and simplified after eliminating mu_L and r with
    Q_L(b+) = Q_L(b-) = 0. Convergence of the integrals (forcing growing
    more slowly than X^{b+} and vanishing faster than X^{b-} at the
    origin) is assumed, not checked.
    """
    X = syms["X"]
    sigma, mu_L, r, lam = syms["sigma"], syms["mu_L"], syms["r"], syms["lam"]
    y = sp.Symbol("y", positive=True)
    bp = sp.Symbol("b_p", positive=True)
    bn = sp.Symbol("b_n", negative=True)
    f = cast(Any, sp.Function("f"))
    kappa = 2 / (sigma**2 * (bp - bn))
    P = kappa * (
        X**bn * sp.Integral(f(y) * y ** (-bn - 1), (y, 0, X))
        + X**bp * sp.Integral(f(y) * y ** (-bp - 1), (y, X, sp.oo))
    )
    residual = (
        sp.Rational(1, 2) * sigma**2 * X**2 * sp.diff(P, X, 2)
        + mu_L * X * sp.diff(P, X)
        - (r + lam) * P
        + f(X)
    )

    def Q(b):
        return sp.Rational(1, 2) * sigma**2 * b * (b - 1) + mu_L * b - (r + lam)

    roots = sp.solve([Q(bp), Q(bn)], [mu_L, r], dict=True)[0]
    return {
        "P": P,
        "kappa": kappa,
        "root_substitution": roots,
        "residual": sp.simplify(sp.expand(residual).subs(roots)),
    }


# =====================================================================
# 11. Numerical verification against base_model.py
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
    """Check the simple-mode L-regime code path against its own formula.

    `SingleFirmModel.option_value_L` is the simple mode (no training
    fraction, no piecewise forcing). It returns D_L X^{beta_L} + C X^{beta_H}
    when the standalone L-regime scale problem has an interior optimum and
    C X^{beta_H} otherwise. This function checks that the code returns the
    formula of its branch. It does not check either formula against the
    model of record: neither solves the piecewise HJB above X_H*, and the
    single-power branch is not the exact value at baseline
    (`verify_pure_power_approximation`).

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
        # Simple-mode single-power branch: F_L = C * X^{beta_H}
        test_X = 0.05
        F_L_code = model.option_value_L(test_X)
        F_L_formula = C * test_X**p.beta_H
        return {
            "has_L_trigger": False,
            "form": "F_L(X) = C * X^{beta_H} (simple-mode single power)",
            "F_L_code": F_L_code,
            "F_L_formula": F_L_formula,
            "match": bool(np.abs(F_L_code - F_L_formula) < 1e-10),
            "C": C,
            "single_power_branch": True,
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
            "single_power_branch": False,
        }


def verify_pure_power_approximation(params=None):
    """The pure-power form against the model of record, at given parameters.

    Reports, without certifying the single power: the L-regime
    insufficiency ratio Phi_L (a description of the standalone L-regime
    scale problem); the coefficient A_w of X^{beta_L^+} in the value of
    never investing before the switch; the coefficient A_1 of the exact
    precommitted-scale solution at its optimal policy and at the capacity
    K_H* of the approximation; and the smooth-fit coefficient B of the
    approximation against Gamma of eq-particular-C. At baseline A_w, A_1 < 0
    and B < Gamma, so F_L = B X^{beta_H} is neither the exact value nor a
    solution of the L-regime HJB.

    Args:
        params: ModelParameters instance; the baseline when omitted.
    """
    from .parameters import ModelParameters
    from .piecewise_option import PiecewiseOptionModel, reduced_form_reference

    p = params if params is not None else ModelParameters()
    model = PiecewiseOptionModel(p)
    phi_L = (1.0 - 1.0 / p.beta_L) / p.alpha
    optimum = model.precommitted_optimum()
    at_K_H = model.solve(model.K_H, optimum.phi)
    A_w, _ = model.pure_switching_coeffs()
    ref = reduced_form_reference(p)
    B = float(ref["smooth_fit_coeff"])
    Gamma = float(ref["C"])

    return {
        "beta_L_plus": p.beta_L,
        "option_premium_ratio_L": phi_L,
        "has_interior_L_trigger": 1.0 / p.gamma < phi_L < 1.0,
        "A_w": A_w,
        "A_1_exact": float(optimum.A_1),
        "A_1_at_K_H": float(at_K_H.A_1) if at_K_H is not None else float("nan"),
        "smooth_fit_coeff": B,
        "Gamma": Gamma,
        "pure_power_form_exact": optimum.A_1 == 0.0 and Gamma == B,
        "conclusion": (
            f"Phi_L = {phi_L:.4f} describes the standalone L-regime scale "
            "problem and says nothing about A_1. The exact precommitted-scale "
            f"solution has A_1 = {optimum.A_1:.4g}, and the smooth-fit "
            f"coefficient {B:.4g} differs from Gamma = {Gamma:.4g}, so "
            "F_L = B X^{beta_H} is an approximation, with its error "
            "reported by piecewise_option.py."
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
# 12. Generate LaTeX for the paper
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
