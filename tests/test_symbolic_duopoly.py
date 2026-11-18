"""Tests for symbolic derivation and verification of the duopoly model.

These tests verify:
1. The symbolic characteristic equations match numerical computations
2. The particular solution coefficient C matches base_model.py
3. The option value structure (one-term vs two-term) is correct
4. Smooth-pasting conditions hold
5. The pure-power form is an approximation of the model of record
6. Key comparative statics have correct signs
7. The identities behind Propositions 1 to 3, the piecewise L-regime
   solution and the recovery rule (residuals that simplify to zero), with
   numerical cross-checks against the model code
"""

import pytest
import sympy as sp

from ai_lab_investment.models.parameters import ModelParameters
from ai_lab_investment.models.symbolic_duopoly import (
    characteristic_equation_H,
    characteristic_equation_L,
    default_boundary_derivation,
    define_symbols,
    effective_revenue_coefficient,
    exact_faith_threshold,
    follower_capacity_condition,
    green_function_residual,
    h_regime_option_value,
    installed_value_in_lambda,
    l_regime_ode,
    l_regime_upper_particular,
    markup_channel,
    optimal_phi_conditions,
    phi_star_closed_form,
    post_switch_capacity_closed_form,
    premium_representation,
    pure_power_smooth_fit,
    recovery_split,
    tullock_factorization,
    two_region_conditions,
    verify_option_value_structure,
    verify_particular_solution_coefficient,
    verify_pure_power_approximation,
    verify_smooth_pasting_L,
    waiting_margin_asymptotic,
)


@pytest.fixture
def syms():
    return define_symbols()


@pytest.fixture
def default_params():
    return ModelParameters()


@pytest.fixture
def high_alpha_params():
    """Parameters where L-regime has an interior trigger."""
    return ModelParameters(alpha=0.85, r=0.20, mu_H=0.06, sigma=0.12)


_NO_L_TRIGGER = (
    "The high-alpha fixture must produce an interior L-trigger: it is the "
    "only parameterization exercising the two-term F_L branch. If parameter "
    "drift removes the trigger, that branch goes untested -- fail here "
    "rather than skip silently."
)


# =====================================================================
# Characteristic equations
# =====================================================================


class TestCharacteristicEquations:
    def test_H_regime_has_two_roots(self, syms):
        result = characteristic_equation_H(syms)
        assert len(result["roots"]) == 2

    def test_L_regime_has_two_roots(self, syms):
        result = characteristic_equation_L(syms)
        assert len(result["roots"]) == 2

    def test_H_regime_positive_root_matches_numerical(self, syms, default_params):
        """Symbolic positive root matches ModelParameters.beta_H."""
        result = characteristic_equation_H(syms)
        p = default_params

        # Evaluate symbolic root at numerical parameter values
        subs = {
            syms["sigma"]: p.sigma,
            syms["mu_H"]: p.mu_H,
            syms["r"]: p.r,
        }
        beta_H_symbolic = float(result["positive_root_expr"].subs(subs))
        assert abs(beta_H_symbolic - p.beta_H) < 1e-10

    def test_L_regime_positive_root_matches_numerical(self, syms, default_params):
        """Symbolic positive root matches ModelParameters.beta_L."""
        result = characteristic_equation_L(syms)
        p = default_params

        subs = {
            syms["sigma"]: p.sigma,
            syms["mu_L"]: p.mu_L,
            syms["r"]: p.r,
            syms["lam"]: p.lam,
        }
        beta_L_symbolic = float(result["positive_root_expr"].subs(subs))
        assert abs(beta_L_symbolic - p.beta_L) < 1e-10

    def test_L_regime_uses_r_plus_lambda(self, syms):
        """L-regime characteristic equation uses (r + lambda) as discount."""
        result = characteristic_equation_L(syms)
        eq = result["equation"]
        # The equation should contain (r + lambda) as the discount term
        # Verify by checking that setting lambda=0 gives the standard equation
        eq_no_lambda = eq.subs(syms["lam"], 0)
        eq_H = characteristic_equation_H(syms)["equation"]
        # Same structure but with mu_L (sigma is shared)
        eq_H_with_L_params = eq_H.subs({
            syms["mu_H"]: syms["mu_L"],
        })
        assert sp.simplify(eq_no_lambda - eq_H_with_L_params) == 0


# =====================================================================
# H-regime option value
# =====================================================================


class TestHRegimeOptionValue:
    def test_trigger_formula(self, syms):
        """H-regime trigger has the standard real options form."""
        result = h_regime_option_value(syms)
        trigger = result["trigger"]
        # Should be beta_H/(beta_H-1) * cost / revenue_coeff
        beta_H = syms["beta_H"]
        expected_markup = beta_H / (beta_H - 1)
        ratio = sp.simplify(trigger * result["revenue_coeff"] / result["total_cost"])
        assert sp.simplify(ratio - expected_markup) == 0


# =====================================================================
# L-regime ODE (the critical derivation)
# =====================================================================


class TestLRegimeODE:
    def test_particular_solution_coefficient_formula(self, syms):
        """C = -lambda * B_H / Q_L(beta_H)."""
        result = l_regime_ode(syms)
        C = result["C"]
        # Verify structure
        assert C.has(syms["lam"])
        assert C.has(syms["B_H"])

    def test_Q_L_at_beta_H_is_nonzero_numerically(self, default_params):
        """Q_L(beta_H) should be nonzero for default parameters."""
        p = default_params
        Q_L = (
            0.5 * p.sigma**2 * p.beta_H * (p.beta_H - 1)
            + p.mu_L * p.beta_H
            - (p.r + p.lam)
        )
        assert abs(Q_L) > 1e-10

    def test_C_positive_for_default_params(self, default_params):
        """C should be positive (switching adds option value)."""
        result = verify_particular_solution_coefficient(default_params)
        assert result["C_from_code"] > 0
        assert result["C_from_formula"] > 0

    def test_C_matches_code(self, default_params):
        """Symbolic C formula matches base_model.py computation."""
        result = verify_particular_solution_coefficient(default_params)
        assert result["match"]


# =====================================================================
# Option value structure verification
# =====================================================================


class TestOptionValueStructure:
    def test_baseline_has_no_L_trigger(self, default_params):
        """At baseline, no interior L-trigger exists."""
        result = verify_option_value_structure(default_params)
        assert not result["has_L_trigger"]
        assert result["single_power_branch"]

    def test_baseline_single_term_matches(self, default_params):
        """At baseline, F_L = C * X^{beta_H} matches the code."""
        result = verify_option_value_structure(default_params)
        assert result["match"]

    def test_high_alpha_has_L_trigger(self, high_alpha_params):
        """With high alpha, an interior L-trigger should exist."""
        from ai_lab_investment.models.base_model import SingleFirmModel

        model = SingleFirmModel(high_alpha_params)
        assert model.has_interior_trigger("L"), _NO_L_TRIGGER
        result = verify_option_value_structure(high_alpha_params)
        assert result["has_L_trigger"]
        assert not result["single_power_branch"]

    def test_high_alpha_two_term_matches(self, high_alpha_params):
        """With interior L-trigger, two-term formula matches code."""
        from ai_lab_investment.models.base_model import SingleFirmModel

        model = SingleFirmModel(high_alpha_params)
        assert model.has_interior_trigger("L"), _NO_L_TRIGGER
        result = verify_option_value_structure(high_alpha_params)
        assert result["match"]


# =====================================================================
# Baseline simplification check
# =====================================================================


class TestPurePowerApproximation:
    """The pure-power form is an approximation of the model of record.

    Issue #176 stopped the check from asserting that the form is valid at
    baseline; issue #185 renamed it and added the smooth-fit comparison.
    """

    def test_pure_power_form_is_not_exact_at_baseline(self):
        """The exact solution carries A_1 != 0 on X^{beta_L^+}."""
        result = verify_pure_power_approximation()
        assert not result["pure_power_form_exact"]
        assert result["A_1_exact"] < 0.0

    def test_paper_coefficients(self):
        """Internet Appendix A: A_w, A_1 at both capacities, 16.5 vs 21.1."""
        result = verify_pure_power_approximation()
        assert result["A_w"] == pytest.approx(-1.18e4, rel=5e-3)
        assert result["A_1_exact"] == pytest.approx(-0.85e4, rel=5e-3)
        assert result["A_1_at_K_H"] == pytest.approx(-1.01e4, rel=5e-3)
        assert result["A_w"] < result["A_1_exact"]
        assert result["smooth_fit_coeff"] == pytest.approx(16.5, abs=0.05)
        assert result["Gamma"] == pytest.approx(21.1, abs=0.05)

    def test_option_premium_ratio_exceeds_one(self):
        """The standalone L-regime scale problem has no interior optimum;
        that is a description, not a licence for the pure-power form."""
        result = verify_pure_power_approximation()
        assert result["option_premium_ratio_L"] >= 1.0
        assert not result["has_interior_L_trigger"]


# =====================================================================
# Smooth-pasting verification
# =====================================================================


class TestSmoothPasting:
    def test_smooth_pasting_L_regime(self, high_alpha_params):
        """Smooth-pasting holds at L-regime trigger (when it exists)."""
        result = verify_smooth_pasting_L(high_alpha_params)
        assert not result.get("skip"), _NO_L_TRIGGER
        assert result["match"]


# =====================================================================
# A_eff and comparative statics
# =====================================================================


class TestEffectiveRevenueCoeff:
    def test_A_eff_positive_numerically(self, default_params):
        """A_eff is positive for reasonable parameters."""
        from ai_lab_investment.models.base_model import SingleFirmModel

        model = SingleFirmModel(default_params)
        a_eff = model._effective_revenue_coeff_single(0.5, 1.0)
        assert a_eff > 0

    def test_dA_eff_dphi_is_zero_at_interior(self, syms):
        """dA_eff/dphi has interior zero (Proposition 1)."""
        result = optimal_phi_conditions(syms)
        foc = result["foc"]
        # The FOC should be a non-trivial expression in phi
        assert foc != 0  # Not identically zero

    def test_dA_eff_dlam_positive(self, syms):
        """dA_eff/dlambda is positive when H-revenue exceeds L-revenue."""
        result = effective_revenue_coefficient(syms)
        dA_dlam = result["dA_dlam"]
        # Substitute typical values where H-regime dominates
        subs = {
            syms["r"]: sp.Rational(12, 100),
            syms["mu_L"]: sp.Rational(1, 100),
            syms["mu_H"]: sp.Rational(6, 100),
            syms["lam"]: sp.Rational(1, 10),
            syms["alpha"]: sp.Rational(2, 5),
            syms["K"]: 1,
            syms["phi"]: sp.Rational(1, 2),
        }
        val = float(dA_dlam.subs(subs))
        assert val > 0, f"dA_eff/dlambda should be positive, got {val}"


# =====================================================================
# Default boundary
# =====================================================================


class TestDefaultBoundary:
    def test_dXD_dA_eff_negative(self, syms):
        """Higher A_eff lowers default boundary."""
        result = default_boundary_derivation(syms)
        # dX_D/dA_eff should be negative (symbolically)
        A_eff = sp.Symbol("A_eff", positive=True)
        expr = result["dXD_dA_eff"]
        # Substitute positive values to check sign
        subs = {
            sp.Symbol("beta_neg", negative=True): sp.Rational(-3, 1),
            sp.Symbol("c_D", positive=True): sp.Rational(1, 10),
            syms["delta"]: sp.Rational(3, 100),
            syms["K"]: 1,
            syms["r"]: sp.Rational(12, 100),
            A_eff: 1,
        }
        val = float(expr.subs(subs))
        assert val < 0

    def test_dXD_dcD_positive(self, syms):
        """Higher coupon raises default boundary."""
        result = default_boundary_derivation(syms)
        c_D = sp.Symbol("c_D", positive=True)
        A_eff = sp.Symbol("A_eff", positive=True)
        subs = {
            sp.Symbol("beta_neg", negative=True): sp.Rational(-3, 1),
            c_D: sp.Rational(1, 10),
            syms["delta"]: sp.Rational(3, 100),
            syms["K"]: 1,
            syms["r"]: sp.Rational(12, 100),
            A_eff: 1,
        }
        val = float(result["dXD_dcD"].subs(subs))
        assert val > 0


# =====================================================================
# Integration test: full pipeline
# =====================================================================


class TestFullPipeline:
    def test_verify_all_baseline(self, default_params):
        """Run all verification checks at baseline parameters."""
        # C coefficient
        c_result = verify_particular_solution_coefficient(default_params)
        assert c_result["match"]

        # Option value structure
        ov_result = verify_option_value_structure(default_params)
        assert ov_result["match"]
        assert ov_result["single_power_branch"]

        # Baseline check
        bl_result = verify_pure_power_approximation(default_params)
        assert not bl_result["pure_power_form_exact"]

    def test_verify_all_high_alpha(self, high_alpha_params):
        """Run verification for params with interior L-trigger."""
        from ai_lab_investment.models.base_model import SingleFirmModel

        model = SingleFirmModel(high_alpha_params)
        assert model.has_interior_trigger("L"), _NO_L_TRIGGER

        c_result = verify_particular_solution_coefficient(high_alpha_params)
        assert c_result["match"]

        ov_result = verify_option_value_structure(high_alpha_params)
        assert ov_result["match"]
        assert not ov_result["single_power_branch"]

        sp_result = verify_smooth_pasting_L(high_alpha_params)
        assert sp_result["match"]

    def test_multiple_lambda_values(self):
        """Verify C and option value across a range of lambda values."""
        for lam_val in [0.01, 0.05, 0.10, 0.20, 0.50, 1.0]:
            p = ModelParameters(lam=lam_val, lam_0=lam_val)
            result = verify_particular_solution_coefficient(p)
            assert result["match"], f"C mismatch at lambda={lam_val}"

            ov = verify_option_value_structure(p)
            assert ov["match"], f"Option value mismatch at lambda={lam_val}"


# =====================================================================
# Identities of the model of record (issue #185): residuals are zero
# =====================================================================


def _residuals(result, *keys):
    return {key: result[key] for key in keys}


class TestModelOfRecordIdentities:
    """Each symbolic identity the notebook displays simplifies to zero."""

    @pytest.mark.parametrize(
        ("function", "keys"),
        [
            (post_switch_capacity_closed_form, ("foc_residual_at_K_H",)),
            (l_regime_ode, ("ode_residual", "Q_L_reduction_residual")),
            (l_regime_upper_particular, ("residual",)),
            (
                premium_representation,
                ("homogeneous_residual", "smooth_pasting_minus_foc"),
            ),
            (pure_power_smooth_fit, ("factorization_residual",)),
            (
                waiting_margin_asymptotic,
                (
                    "envelope_foc_residual",
                    "envelope_value_residual",
                    "growth_residual",
                    "margin_residual",
                ),
            ),
            (effective_revenue_coefficient, ("dA_dlam_residual",)),
            (
                installed_value_in_lambda,
                (
                    "d1_residual",
                    "d2_residual",
                    "asymmetry_residual",
                    "dG_dphi_residual",
                    "semi_elasticity_residual",
                    "semi_elasticity_rho_residual",
                ),
            ),
            (
                phi_star_closed_form,
                (
                    "foc_residual",
                    "second_derivative_residual",
                    "inference_share_residual",
                ),
            ),
            (markup_channel, ("root_residual", "dM_dlam_residual", "m_residual")),
            (
                exact_faith_threshold,
                (
                    "dlnA_dlam_residual",
                    "linear_in_odds_residual",
                    "odds_residual",
                    "net_at_phi_tilde",
                    "a_eff_channel_at_phi_underbar",
                    "limit_m_to_zero_residual",
                ),
            ),
            (recovery_split, ("split_residual", "sign_residual")),
            (
                tullock_factorization,
                (
                    "derivative_residual",
                    "scale_invariance_residual",
                    "common_allocation_residual",
                ),
            ),
            (follower_capacity_condition, ("elasticity_a_residual", "foc_residual")),
            (green_function_residual, ("residual",)),
        ],
    )
    def test_residual_is_zero(self, syms, function, keys):
        residuals = _residuals(function(syms), *keys)
        assert all(value == 0 for value in residuals.values()), residuals

    def test_phi_underbar_comparative_statics(self, syms):
        """Derivatives of ln Omega match their signed forms (Prop. 2(ii))."""
        residuals = exact_faith_threshold(syms)["dlnOmega_residuals"]
        assert all(value == 0 for value in residuals.values()), residuals

    def test_capacity_coefficient_drops_out(self, syms):
        """eq-foc-K does not involve the revenue coefficient a (Step 4)."""
        assert post_switch_capacity_closed_form(syms)["a_drops_out"]

    def test_pure_power_residual_vanishes_only_at_gamma(self, syms):
        """B X^{beta_H} solves the HJB below X_H* iff B equals Gamma."""
        result = pure_power_smooth_fit(syms)
        Gamma = -syms["lam"] * syms["B_H"] / l_regime_ode(syms)["Q_L_at_beta_H"]
        assert sp.simplify(result["hjb_residual"].subs(result["B"], Gamma)) == 0

    def test_two_region_system_is_linear_in_coefficients(self, syms):
        """Three of the four conditions pin (A_1, G_1, G_2) given X*."""
        result = two_region_conditions(syms)
        names = result["symbols"]
        assert set(result["coefficients"]) == {names["A1"], names["G1"], names["G2"]}
        for key in ("A1", "G1", "G2"):
            assert not result["coefficients"][names[key]].has(
                names["A1"], names["G1"], names["G2"]
            )
        assert not result["scalar_equation_in_X_star"].has(
            names["A1"], names["G1"], names["G2"]
        )

    def test_follower_elasticity_limits(self, syms):
        """K Theta'/Theta rises from 1 to gamma (here gamma = 3/2)."""
        lo, hi = follower_capacity_condition(syms)[
            "theta_elasticity_limits_at_gamma_3_2"
        ]
        assert lo == 1
        assert hi == sp.Rational(3, 2)


# =====================================================================
# Numerical cross-checks of the identities against the model code
# =====================================================================


class TestModelOfRecordNumerics:
    """The closed forms evaluated at baseline agree with the model code."""

    @staticmethod
    def _baseline_subs(syms, p):
        return {
            syms["r"]: p.r,
            syms["mu_L"]: p.mu_L,
            syms["mu_H"]: p.mu_H,
            syms["sigma"]: p.sigma,
            syms["lam"]: p.lam,
            syms["alpha"]: p.alpha,
            syms["gamma"]: p.gamma,
            syms["c"]: p.c,
            syms["delta"]: p.delta,
            syms["beta_H"]: p.beta_H,
        }

    def test_post_switch_capacity(self, syms, default_params):
        from ai_lab_investment.models.piecewise_option import PiecewiseOptionModel
        from ai_lab_investment.models.preemption_exact import ExactPreemptionGame

        p = default_params
        K_H = post_switch_capacity_closed_form(syms)["K_H"]
        value = float(K_H.subs(self._baseline_subs(syms, p)))
        # `_solve_regime_H` maximizes numerically (agrees to about 1e-6);
        # the exact game's root-finder reproduces the closed form.
        assert value == pytest.approx(PiecewiseOptionModel(p).K_H, rel=1e-5)
        entry = ExactPreemptionGame(p, scale="envelope").post_switch_entry(0.0)
        assert value == pytest.approx(entry.K_F, rel=1e-10)

    def test_faith_thresholds_match_code(self, syms, default_params):
        from ai_lab_investment.models.duopoly import DuopolyModel

        p = default_params
        subs = self._baseline_subs(syms, p)
        mc = markup_channel(syms)
        m_val = float(mc["m"].subs(subs))
        assert m_val == pytest.approx(0.77, abs=0.005)
        ft = exact_faith_threshold(syms)
        phi_t = float(ft["phi_tilde"].subs(ft["m"], m_val).subs(subs))
        phi_u = float(ft["phi_underbar"].subs(subs))
        duo = DuopolyModel(p)
        assert phi_t == pytest.approx(duo.faith_threshold_exact(), rel=1e-10)
        assert phi_u == pytest.approx(duo.faith_threshold(), rel=1e-10)
        assert phi_u < phi_t

    def test_waiting_margin_matches_code(self, syms, default_params):
        from ai_lab_investment.models.base_model import SingleFirmModel

        p = default_params
        result = waiting_margin_asymptotic(syms)
        phi = SingleFirmModel(p).closed_form_phi_star()
        g_val = ((1 - phi) ** p.alpha + p.lam * p.A_H * phi**p.alpha) / (
            p.r - p.mu_L + p.lam
        )
        subs = self._baseline_subs(syms, p)
        subs.update({
            sp.Symbol("A_H", positive=True): p.A_H,
            sp.Symbol("g", positive=True): g_val,
        })
        margin = float(result["margin"].subs(subs))
        assert margin == pytest.approx(SingleFirmModel(p).solve().waiting_margin, 1e-6)

    @pytest.mark.parametrize("T_L", [0.0, 1e-3, 1e-2])
    def test_follower_capacity_root_matches_game(self, syms, default_params, T_L):
        import numpy as np
        from scipy import optimize

        from ai_lab_investment.models.preemption_exact import ExactPreemptionGame

        p = default_params
        result = follower_capacity_condition(syms)
        subs = self._baseline_subs(syms, p)
        subs[result["T_L"]] = T_L
        subs[result["A_H"]] = p.A_H
        log_derivative = sp.lambdify(syms["K"], result["log_derivative"].subs(subs))
        K_F = float(
            np.exp(optimize.brentq(lambda t: log_derivative(np.exp(t)), -30.0, 10.0))
        )
        entry = ExactPreemptionGame(p, scale="envelope").post_switch_entry(T_L)
        assert pytest.approx(entry.K_F, rel=1e-8) == K_F
        X_F = float(result["trigger"].subs(subs).subs(syms["K"], K_F))
        assert pytest.approx(entry.X_F, rel=1e-8) == X_F

    def test_green_function_reproduces_pure_switching_value(self, default_params):
        """eq-green with the piecewise forcing is the value of waiting S."""
        from ai_lab_investment.models.piecewise_option import PiecewiseOptionModel
        from ai_lab_investment.models.preemption_exact import ForcedClaim

        p = default_params
        model = PiecewiseOptionModel(p)
        claim = ForcedClaim(
            p,
            model.X_H,
            low=((p.lam * model.B_H, p.beta_H),),
            high=((p.lam * model.a_H, 1.0), (-p.lam * model.b_H, 0.0)),
        )
        for ratio in (0.2, 0.9, 1.5, 5.0, 50.0):
            x = ratio * model.X_H
            assert float(claim(x)[0]) == pytest.approx(
                model.pure_switching_value(x), rel=1e-9
            )

    def test_two_region_conditions_hold_at_code_optimum(self, default_params):
        """The precommitted-scale optimum satisfies the four conditions and
        the scale condition eq-scale-foc."""
        from ai_lab_investment.models.piecewise_option import PiecewiseOptionModel

        p = default_params
        model = PiecewiseOptionModel(p)
        sol = model.precommitted_optimum()
        bp, bn, h, X_H, X_s = (
            sol.beta_L_pos,
            sol.beta_L_neg,
            sol.beta_H,
            sol.X_H,
            sol.X_star,
        )

        def upper(x):
            return sol.D_1 * x**bp + sol.D_2 * x**bn + sol.g * x + sol.k

        def upper_slope(x):
            return bp * sol.D_1 * x ** (bp - 1) + bn * sol.D_2 * x ** (bn - 1) + sol.g

        lower = sol.A_1 * X_H**bp + sol.C * X_H**h
        lower_slope = bp * sol.A_1 * X_H ** (bp - 1) + h * sol.C * X_H ** (h - 1)
        scale = sol.a_L * X_s
        assert abs(lower - upper(X_H)) < 1e-9 * scale
        assert abs(lower_slope - upper_slope(X_H)) < 1e-7 * sol.a_L
        assert abs(upper(X_s) - (sol.a_L * X_s - sol.b_L)) < 1e-9 * scale
        assert abs(upper_slope(X_s) - sol.a_L) < 1e-7 * sol.a_L
        # eq-scale-foc: alpha A_eff X* = K (delta/r + c gamma K^{gamma-1})
        K = sol.K
        lhs = p.alpha * sol.a_L * X_s
        rhs = K * (p.delta / p.r + p.c * p.gamma * K ** (p.gamma - 1))
        assert lhs == pytest.approx(rhs, rel=1e-4)
        # Step 7: A_1 = A_w + [P - S](X*) X*^{-beta_L^+}, G_2 = G_w
        A_w, G_w = model.pure_switching_coeffs()
        premium = sol.a_L * X_s - sol.b_L - model.pure_switching_value(X_s)
        assert pytest.approx(A_w + premium * X_s ** (-bp), rel=1e-6) == sol.A_1
        assert pytest.approx(premium * X_s ** (-bp), rel=1e-6) == sol.D_1
        assert pytest.approx(G_w, rel=1e-4) == sol.D_2

    def test_lambda_bar(self, default_params):
        """phi*(lambda) crosses phi_tilde(lambda) near 0.034 (Prop. 2)."""
        from scipy import optimize

        from ai_lab_investment.models.base_model import SingleFirmModel
        from ai_lab_investment.models.duopoly import DuopolyModel

        def gap(lam):
            q = default_params.with_param(lam=lam, lam_0=lam)
            return (
                SingleFirmModel(q).closed_form_phi_star()
                - DuopolyModel(q).faith_threshold_exact()
            )

        assert optimize.brentq(gap, 0.005, 0.10) == pytest.approx(0.034, abs=5e-4)

    def test_pure_switching_below_gamma_power(self, default_params):
        """S lies 10% below Gamma X^{beta_H} at X_H* (Internet Appendix A)."""
        from ai_lab_investment.models.piecewise_option import PiecewiseOptionModel

        model = PiecewiseOptionModel(default_params)
        x = model.X_H
        ratio = model.pure_switching_value(x) / (model.C * x**default_params.beta_H)
        assert ratio - 1.0 == pytest.approx(-0.10, abs=0.005)

    def test_recovery_coupon_bound(self, default_params):
        """Lambda(X_D) < 0 iff C_D < delta K (1 - M)/M; about 0.43 at baseline."""
        from ai_lab_investment.models.duopoly import DuopolyModel

        p = default_params
        duo = DuopolyModel(p)
        beta_neg = duo._negative_root("L", p.lam)
        M = beta_neg / (beta_neg - 1.0)
        assert pytest.approx(0.70, abs=0.005) == M
        assert pytest.approx(0.43, abs=0.005) == (1 - M) / M
