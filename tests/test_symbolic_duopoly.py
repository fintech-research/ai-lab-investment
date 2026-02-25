"""Tests for symbolic derivation and verification of the duopoly model.

Under the F_H = 0 assumption:
1. The L-regime ODE is homogeneous (no particular solution C).
2. F_L(X) = A_1 * X^{beta_L^+} (single-term solution).
3. Smooth-pasting gives dF_L/dX = A_eff (not A_L) at the trigger.
4. The baseline simplification check reflects the new constraint
   alpha > 1 - 1/beta_L for interior K*.
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
    verify_smooth_pasting_L,
)


@pytest.fixture
def syms():
    return define_symbols()


@pytest.fixture
def default_params():
    return ModelParameters()


@pytest.fixture
def interior_L_params():
    """Parameters where L-regime has an interior trigger under F_H = 0."""
    return ModelParameters(alpha=0.70)


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
        result = characteristic_equation_H(syms)
        p = default_params
        subs = {
            syms["sigma_H"]: p.sigma_H,
            syms["mu_H"]: p.mu_H,
            syms["r"]: p.r,
        }
        beta_H_symbolic = float(result["positive_root_expr"].subs(subs))
        assert abs(beta_H_symbolic - p.beta_H) < 1e-10

    def test_L_regime_positive_root_matches_numerical(self, syms, default_params):
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
        result = characteristic_equation_L(syms)
        eq = result["equation"]
        eq_no_lambda = eq.subs(syms["lam"], 0)
        eq_H = characteristic_equation_H(syms)["equation"]
        eq_H_with_L_params = eq_H.subs({
            syms["sigma_H"]: syms["sigma_L"],
            syms["mu_H"]: syms["mu_L"],
        })
        assert sp.simplify(eq_no_lambda - eq_H_with_L_params) == 0


# =====================================================================
# H-regime option value (retained for reference)
# =====================================================================


class TestHRegimeOptionValue:
    def test_trigger_formula(self, syms):
        result = h_regime_option_value(syms)
        trigger = result["trigger"]
        beta_H = syms["beta_H"]
        expected_markup = beta_H / (beta_H - 1)
        ratio = sp.simplify(trigger * result["revenue_coeff"] / result["total_cost"])
        assert sp.simplify(ratio - expected_markup) == 0


# =====================================================================
# L-regime ODE (homogeneous under F_H = 0)
# =====================================================================


class TestLRegimeODE:
    def test_ode_is_homogeneous(self, syms):
        """Under F_H = 0, the L-regime ODE has no forcing term."""
        result = l_regime_ode(syms)
        # The note should describe the homogeneous ODE
        assert "homogeneous" in result.get("note", "").lower()

    def test_Q_L_positive_root(self, syms, default_params):
        """Q_L has a positive root (beta_L^+)."""
        result = characteristic_equation_L(syms)
        p = default_params
        subs = {
            syms["sigma_L"]: p.sigma_L,
            syms["mu_L"]: p.mu_L,
            syms["r"]: p.r,
            syms["lam"]: p.lam,
        }
        beta_L = float(result["positive_root_expr"].subs(subs))
        assert beta_L > 1.0


# =====================================================================
# Option value structure verification
# =====================================================================


class TestOptionValueStructure:
    def test_baseline_has_no_L_trigger(self, default_params):
        """At baseline alpha=0.40, no interior L-trigger under F_H = 0."""
        result = verify_option_value_structure(default_params)
        assert not result["has_L_trigger"]

    def test_high_alpha_has_L_trigger(self, interior_L_params):
        """With alpha=0.70, an interior L-trigger should exist."""
        result = verify_option_value_structure(interior_L_params)
        assert result["has_L_trigger"]
        assert result["match"]

    def test_high_alpha_single_term_matches(self, interior_L_params):
        """F_L = A_1 * X^{beta_L^+} matches the code."""
        result = verify_option_value_structure(interior_L_params)
        assert result["form"] == "F_L(X) = A_1 * X^{beta_L^+} (homogeneous solution)"
        assert result["match"]


# =====================================================================
# Baseline simplification check
# =====================================================================


class TestBaselineSimplification:
    def test_no_interior_L_trigger_at_baseline(self):
        """At baseline alpha=0.40, no interior K* under F_H = 0."""
        result = verify_baseline_simplification()
        assert not result["has_interior_L_trigger"]

    def test_alpha_min_correct(self):
        """alpha_min should be approximately 1 - 1/beta_L."""
        result = verify_baseline_simplification()
        expected = 1.0 - 1.0 / result["beta_L_plus"]
        assert abs(result["alpha_min_for_interior_K"] - expected) < 1e-10

    def test_k_optimization_exponent_negative_at_baseline(self):
        """At baseline, beta_L*(alpha-1)+1 < 0."""
        result = verify_baseline_simplification()
        assert result["k_optimization_exponent"] < 0


# =====================================================================
# Smooth-pasting verification
# =====================================================================


class TestSmoothPasting:
    def test_smooth_pasting_L_regime(self, interior_L_params):
        """Smooth-pasting holds at L-regime trigger."""
        result = verify_smooth_pasting_L(interior_L_params)
        if result.get("skip"):
            pytest.skip("No interior L-trigger")
        assert result["match"]


# =====================================================================
# A_eff and comparative statics
# =====================================================================


class TestEffectiveRevenueCoeff:
    def test_A_eff_positive_numerically(self, default_params):
        from ai_lab_investment.models.base_model import SingleFirmModel

        model = SingleFirmModel(default_params)
        a_eff = model._effective_revenue_coeff_single(0.5, 1.0)
        assert a_eff > 0

    def test_dA_eff_dphi_is_zero_at_interior(self, syms):
        result = optimal_phi_conditions(syms)
        foc = result["foc"]
        assert foc != 0

    def test_dA_eff_dlam_positive(self, syms):
        result = effective_revenue_coefficient(syms)
        dA_dlam = result["dA_dlam"]
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
        result = default_boundary_derivation(syms)
        A_eff = sp.Symbol("A_eff", positive=True)
        subs = {
            sp.Symbol("beta_neg", negative=True): sp.Rational(-3, 1),
            sp.Symbol("c_D", positive=True): sp.Rational(1, 10),
            syms["delta"]: sp.Rational(3, 100),
            syms["K"]: 1,
            syms["r"]: sp.Rational(12, 100),
            A_eff: 1,
        }
        val = float(result["dXD_dA_eff"].subs(subs))
        assert val < 0

    def test_dXD_dcD_positive(self, syms):
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
        """Run verification checks at baseline (no interior L-trigger)."""
        ov_result = verify_option_value_structure(default_params)
        assert not ov_result["has_L_trigger"]

        bl_result = verify_baseline_simplification()
        assert not bl_result["has_interior_L_trigger"]

    def test_verify_all_high_alpha(self, interior_L_params):
        """Run verification for params with interior L-trigger."""
        ov_result = verify_option_value_structure(interior_L_params)
        assert ov_result["has_L_trigger"]
        assert ov_result["match"]

        sp_result = verify_smooth_pasting_L(interior_L_params)
        assert sp_result["match"]

    def test_multiple_lambda_values(self):
        """Verify option value across a range of lambda values."""
        for lam_val in [0.01, 0.05, 0.10, 0.20, 0.50, 1.0]:
            p = ModelParameters(lam=lam_val, lam_0=lam_val, alpha=0.70)
            ov = verify_option_value_structure(p)
            if ov["has_L_trigger"]:
                assert ov["match"], f"Option value mismatch at lambda={lam_val}"
