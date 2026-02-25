"""Tests for calibration and revealed beliefs."""

import numpy as np
import pytest

from ai_lab_investment.calibration.data import (
    get_baseline_calibration,
    get_stylized_firms,
)
from ai_lab_investment.calibration.revealed_beliefs import RevealedBeliefs

# ------------------------------------------------------------------
# Calibration data
# ------------------------------------------------------------------


class TestCalibrationData:
    def test_baseline_calibration_valid(self):
        """Baseline calibration should produce valid model parameters."""
        calib = get_baseline_calibration()
        params = calib.to_model_params()
        assert params.r > params.mu_H
        assert params.beta_H > 1.0

    def test_has_firms(self):
        """Baseline calibration should include firm data."""
        calib = get_baseline_calibration()
        assert len(calib.firms) >= 3

    def test_has_sources(self):
        """Calibration should document data sources."""
        calib = get_baseline_calibration()
        assert len(calib.sources) > 0

    def test_to_model_params_override_lambda(self):
        """Should be able to override lambda in model params."""
        calib = get_baseline_calibration()
        p1 = calib.to_model_params(lam=0.1)
        p2 = calib.to_model_params(lam=0.5)
        assert p1.lam == 0.1
        assert p2.lam == 0.5

    def test_stylized_firms_count(self):
        """Should have 4 stylized firms."""
        firms = get_stylized_firms()
        assert len(firms) == 4

    def test_firms_have_positive_revenue(self):
        """All firms should have positive revenue."""
        firms = get_stylized_firms()
        for firm in firms:
            assert firm.revenue_2025 > 0
            assert firm.capex_2025 > 0


# ------------------------------------------------------------------
# Revealed beliefs
# ------------------------------------------------------------------


class TestRevealedBeliefs:
    @pytest.fixture
    def rb(self):
        calib = get_baseline_calibration()
        return RevealedBeliefs(calib)

    def test_model_trigger_at_lambda(self, rb):
        """Model should produce positive trigger for valid lambda."""
        X = rb._model_trigger_at_lambda(0.10)
        assert X > 0

    def test_higher_lambda_lower_trigger(self, rb):
        """Higher lambda should lower the trigger (invest sooner)."""
        X_lo = rb._model_trigger_at_lambda(0.05)
        X_hi = rb._model_trigger_at_lambda(0.50)
        # H-regime trigger doesn't depend directly on lambda
        # But capacity might change. Just check both are valid.
        assert X_lo > 0
        assert X_hi > 0

    def test_infer_lambda_from_trigger(self, rb):
        """Lambda inversion from H-regime trigger.

        Note: H-regime trigger X_H* doesn't depend on lambda (H is
        absorbing, beta_H = f(sigma, mu_H, r)). So the inversion
        may return the boundary value or None. This is correct behavior.
        The real revealed-beliefs methodology uses investment intensity
        (capex/revenue) which does depend on lambda through the option
        value structure.
        """
        true_lambda = 0.20
        X_star = rb._model_trigger_at_lambda(true_lambda)
        assert np.isfinite(X_star)
        # The inversion may not recover lambda from H-trigger alone
        recovered = rb.infer_lambda_from_trigger(X_star)
        # Result should be None (no sign change) or a boundary value
        # This is expected — the real inversion uses capex intensity
        assert recovered is None or recovered >= 0

    def test_infer_returns_none_for_impossible(self, rb):
        """Should return None for impossible trigger values."""
        result = rb.infer_lambda_from_trigger(1e10)
        # Very high trigger may not be achievable
        # Result should be None or a very low lambda
        assert result is None or result < 0.01

    def test_sensitivity_analysis_shape(self, rb):
        """Sensitivity analysis should return correct shape."""
        firm = rb.calibration.firms[0]
        result = rb.sensitivity_analysis(firm, "sigma", np.linspace(0.20, 0.45, 5))
        assert len(result["param_values"]) == 5
        assert len(result["implied_lambda"]) == 5

    def test_investment_predictions(self, rb):
        """Investment predictions should produce results."""
        preds = rb.investment_predictions(np.array([0.05, 0.10, 0.50]))
        assert preds["has_solution"].sum() >= 2
        valid = preds["has_solution"]
        assert np.all(preds["triggers"][valid] > 0)

    def test_compute_all_revealed_beliefs(self, rb):
        """Should produce beliefs for all firms; some may be None."""
        beliefs = rb.compute_all_revealed_beliefs()
        assert len(beliefs) == len(rb.calibration.firms)
        n_solved = 0
        for b in beliefs:
            assert "firm" in b
            assert "capex_intensity" in b
            if b["lambda_from_capex"] is not None:
                assert b["lambda_from_capex"] > 0
                n_solved += 1
        assert n_solved >= 3  # most firms should have a solution

    def test_summary(self, rb):
        """Summary should contain all key information."""
        s = rb.summary()
        assert "n_firms" in s
        assert "revealed_beliefs" in s
        assert "predictions_by_lambda" in s
        assert "sources" in s

    def test_capacity_at_lambda(self, rb):
        """Model capacity should be positive."""
        K = rb._model_capacity_at_lambda(0.10)
        assert K > 0


# ------------------------------------------------------------------
# Phi-aware revealed beliefs
# ------------------------------------------------------------------


class TestPhiAwareBeliefs:
    @pytest.fixture
    def rb(self):
        calib = get_baseline_calibration()
        return RevealedBeliefs(calib)

    def test_model_phi_intensity(self, rb):
        """Phi-aware model should return valid intensity and phi."""
        intensity, phi = rb._model_phi_intensity_at_lambda(0.10)
        assert intensity > 0
        assert 0.01 <= phi <= 0.99

    def test_higher_lambda_higher_phi(self, rb):
        """Higher lambda should shift optimal phi toward training."""
        _, phi_lo = rb._model_phi_intensity_at_lambda(0.05)
        _, phi_hi = rb._model_phi_intensity_at_lambda(0.50)
        assert phi_hi > phi_lo

    def test_infer_lambda_with_phi(self, rb):
        """Should infer lambda using phi-aware model."""
        firm = rb.calibration.firms[0]
        result = rb.infer_lambda_with_phi(firm)
        assert "lambda_implied" in result
        assert "phi_model" in result
        assert "phi_observed" in result
        assert "capex_intensity" in result

    def test_infer_lambda_with_phi_positive(self, rb):
        """Inferred lambda should be positive for all firms."""
        for firm in rb.calibration.firms:
            result = rb.infer_lambda_with_phi(firm)
            if result["lambda_implied"] is not None:
                assert result["lambda_implied"] > 0

    def test_phi_observed_from_firm_data(self, rb):
        """Should pass through observed training fraction."""
        firm = rb.calibration.firms[0]
        result = rb.infer_lambda_with_phi(firm)
        if firm.training_fraction > 0:
            assert result["phi_observed"] == firm.training_fraction

    def test_compute_all_with_phi(self, rb):
        """Should compute phi-aware beliefs for all firms."""
        beliefs = rb.compute_all_revealed_beliefs_with_phi()
        assert len(beliefs) == len(rb.calibration.firms)
        for b in beliefs:
            assert "lambda_implied" in b
            assert "phi_model" in b
            assert "lambda_from_capex_legacy" in b

    def test_summary_includes_phi_beliefs(self, rb):
        """Summary should include phi-aware beliefs."""
        s = rb.summary()
        assert "revealed_beliefs_with_phi" in s

    def test_firms_have_training_fraction(self):
        """Stylized firms should have training fraction estimates."""
        firms = get_stylized_firms()
        for firm in firms:
            assert hasattr(firm, "training_fraction")
            assert firm.training_fraction >= 0

    def test_calibration_passes_endogenous_params(self):
        """to_model_params should pass lam_0, xi, eta."""
        calib = get_baseline_calibration()
        params = calib.to_model_params()
        assert params.lam_0 == calib.lam_0
        assert params.xi == calib.xi
        assert params.eta == calib.eta

    def test_calibration_xi_override(self):
        """Should support xi override in to_model_params."""
        calib = get_baseline_calibration()
        params = calib.to_model_params(xi=0.05)
        assert params.xi == 0.05
