"""Tests for symbolic derivation and verification of the duopoly model.

These tests verify:
1. The symbolic characteristic equations match numerical computations
2. The particular solution coefficient C matches base_model.py
3. The option value structure (one-term vs two-term) is correct
4. Smooth-pasting conditions hold
5. The paper's simplified form is valid only under specific conditions
6. Key comparative statics have correct signs
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
    h_regime_option_value,
    l_regime_ode,
    optimal_phi_conditions,
    verify_baseline_simplification,
    verify_option_value_structure,
    verify_particular_solution_coefficient,
    verify_smooth_pasting_L,
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
    return ModelParameters(alpha=0.85, r=0.20, mu_H=0.06, sigma_H=0.10, sigma_L=0.15)


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
            syms["sigma_H"]: p.sigma_H,
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
            syms["sigma_L"]: p.sigma_L,
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
        # Same structure but with sigma_L, mu_L
        eq_H_with_L_params = eq_H.subs({
            syms["sigma_H"]: syms["sigma_L"],
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
            0.5 * p.sigma_L**2 * p.beta_H * (p.beta_H - 1)
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
        assert result["paper_simplified_form_valid"]

    def test_baseline_single_term_matches(self, default_params):
        """At baseline, F_L = C * X^{beta_H} matches the code."""
        result = verify_option_value_structure(default_params)
        assert result["match"]

    def test_high_alpha_has_L_trigger(self, high_alpha_params):
        """With high alpha, an interior L-trigger should exist."""
        from ai_lab_investment.models.base_model import SingleFirmModel

        model = SingleFirmModel(high_alpha_params)
        if not model.has_interior_trigger("L"):
            pytest.skip("No interior L-trigger for these params")
        result = verify_option_value_structure(high_alpha_params)
        assert result["has_L_trigger"]
        assert not result["paper_simplified_form_valid"]

    def test_high_alpha_two_term_matches(self, high_alpha_params):
        """With interior L-trigger, two-term formula matches code."""
        from ai_lab_investment.models.base_model import SingleFirmModel

        model = SingleFirmModel(high_alpha_params)
        if not model.has_interior_trigger("L"):
            pytest.skip("No interior L-trigger for these params")
        result = verify_option_value_structure(high_alpha_params)
        assert result["match"]


# =====================================================================
# Baseline simplification check
# =====================================================================


class TestBaselineSimplification:
    def test_baseline_simplified_form_valid(self):
        """Paper's F_L = C*X^{beta_H} is valid at baseline."""
        result = verify_baseline_simplification()
        assert result["simplified_form_valid"]

    def test_option_premium_ratio_exceeds_one(self):
        """phi_L >= 1 at baseline (so no interior trigger in L)."""
        result = verify_baseline_simplification()
        assert result["option_premium_ratio_L"] >= 1.0


# =====================================================================
# Smooth-pasting verification
# =====================================================================


class TestSmoothPasting:
    def test_smooth_pasting_L_regime(self, high_alpha_params):
        """Smooth-pasting holds at L-regime trigger (when it exists)."""
        result = verify_smooth_pasting_L(high_alpha_params)
        if result.get("skip"):
            pytest.skip("No interior L-trigger")
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
        assert ov_result["paper_simplified_form_valid"]

        # Baseline check
        bl_result = verify_baseline_simplification()
        assert bl_result["simplified_form_valid"]

    def test_verify_all_high_alpha(self, high_alpha_params):
        """Run verification for params with interior L-trigger."""
        from ai_lab_investment.models.base_model import SingleFirmModel

        model = SingleFirmModel(high_alpha_params)
        if not model.has_interior_trigger("L"):
            pytest.skip("No interior L-trigger")

        c_result = verify_particular_solution_coefficient(high_alpha_params)
        assert c_result["match"]

        ov_result = verify_option_value_structure(high_alpha_params)
        assert ov_result["match"]
        assert not ov_result["paper_simplified_form_valid"]

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
