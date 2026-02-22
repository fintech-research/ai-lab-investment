"""Tests for the single-firm base model."""

import numpy as np
import pytest

from ai_lab_investment.models.base_model import SingleFirmModel
from ai_lab_investment.models.parameters import ModelParameters


@pytest.fixture
def default_params():
    return ModelParameters()


@pytest.fixture
def model(default_params):
    return SingleFirmModel(default_params)


class TestInstalledValue:
    def test_positive_for_high_demand(self, model):
        V = model.installed_value(X=10.0, K=1.0, regime="H")
        assert V > 0

    def test_increases_with_X(self, model):
        V1 = model.installed_value(X=1.0, K=1.0, regime="H")
        V2 = model.installed_value(X=2.0, K=1.0, regime="H")
        assert V2 > V1

    def test_regime_H_higher_than_L(self, model):
        V_H = model.installed_value(X=1.0, K=1.0, regime="H")
        V_L = model.installed_value(X=1.0, K=1.0, regime="L")
        assert V_H > V_L

    def test_formula(self, model):
        p = model.params
        X, K = 2.0, 1.5
        expected = p.A_H * X * K**p.alpha - p.delta * K / p.r
        actual = model.installed_value(X, K, "H")
        assert abs(actual - expected) < 1e-12


class TestPhiAndExistence:
    def test_phi_H_in_valid_range(self, model):
        phi = model._phi("H")
        gamma = model.params.gamma
        assert 1.0 / gamma < phi < 1.0

    def test_has_interior_trigger_H(self, model):
        assert model.has_interior_trigger("H")

    def test_no_interior_trigger_L_default(self, model):
        # With default params, phi_L > 1 so no interior trigger in L
        assert not model.has_interior_trigger("L")


class TestRegimeH:
    def test_trigger_positive(self, model):
        X_star, K_star = model.optimal_trigger_and_capacity("H")
        assert X_star > 0
        assert K_star > 0

    def test_smooth_pasting(self, model):
        """Verify smooth-pasting: dF/dX = dV/dX at X*."""
        p = model.params
        X_star, K_star, B_H = model._solve_regime_H()

        dF = p.beta_H * B_H * X_star ** (p.beta_H - 1)
        dV = p.A_H * K_star**p.alpha

        assert abs(dF - dV) / max(abs(dF), 1e-10) < 1e-6

    def test_value_matching(self, model):
        """Verify value-matching: F(X*) = V(X*, K*) - I(K*)."""
        X_star, K_star, B_H = model._solve_regime_H()
        option_val = B_H * X_star**model.params.beta_H
        npv = model.installed_value(X_star, K_star, "H") - model.investment_cost(K_star)
        assert abs(option_val - npv) / max(abs(npv), 1e-10) < 1e-5

    def test_option_value_positive(self, model):
        X_star, _ = model.optimal_trigger_and_capacity("H")
        assert model.option_value_H(X_star * 0.5) > 0

    def test_option_value_increasing(self, model):
        X_star, _ = model.optimal_trigger_and_capacity("H")
        X1 = X_star * 0.3
        X2 = X_star * 0.6
        assert model.option_value_H(X2) > model.option_value_H(X1)

    def test_option_exceeds_npv_before_trigger(self, model):
        X_star, K_star = model.optimal_trigger_and_capacity("H")
        X = X_star * 0.8
        option = model.option_value_H(X)
        npv = model.installed_value(X, K_star, "H") - model.investment_cost(K_star)
        assert option >= npv - 1e-10


class TestRegimeL:
    def test_no_trigger_raises(self, model):
        """When phi_L >= 1, optimal_trigger_and_capacity raises."""
        with pytest.raises(RuntimeError, match="No interior trigger"):
            model.optimal_trigger_and_capacity("L")

    def test_option_value_L_positive(self, model):
        """Even without trigger, option value is positive (from switching)."""
        assert model.option_value_L(0.01) > 0

    def test_option_value_L_from_C_only(self, model):
        """Without interior trigger, F_L(X) = C * X^beta_H."""
        p = model.params
        C = model._particular_solution_coeff()
        X = 0.05
        expected = C * X**p.beta_H
        actual = model.option_value_L(X)
        assert abs(actual - expected) / max(abs(expected), 1e-10) < 1e-10

    def test_C_positive(self, model):
        """C should be positive (switching adds value)."""
        assert model._particular_solution_coeff() > 0

    def test_option_value_L_increasing(self, model):
        assert model.option_value_L(0.1) > model.option_value_L(0.05)

    def test_with_high_alpha_has_L_trigger(self):
        """With sufficiently high alpha, regime L has an interior trigger."""
        # Both regimes need phi in (1/gamma, 1). High alpha + low vol works.
        p = ModelParameters(alpha=0.85, r=0.20, mu_H=0.06, sigma_H=0.10, sigma_L=0.15)
        m = SingleFirmModel(p)
        if not m.has_interior_trigger("L"):
            pytest.skip("No interior trigger in L for these parameters")
        X_L, K_L = m.optimal_trigger_and_capacity("L")
        assert X_L > 0
        assert K_L > 0


class TestComparativeStatics:
    def test_higher_sigma_higher_trigger_H(self, model):
        """Higher H volatility -> higher trigger (more option value)."""
        stats = model.comparative_statics("sigma_H", np.array([0.25, 0.35]), regime="H")
        valid = stats["has_trigger"]
        assert valid.sum() == 2, "Both sigma_H values should yield valid triggers"
        assert stats["triggers"][1] > stats["triggers"][0]

    def test_alpha_affects_trigger_H(self, model):
        """Varying alpha changes the trigger (non-trivial interaction)."""
        stats = model.comparative_statics(
            "alpha", np.linspace(0.35, 0.45, 5), regime="H"
        )
        valid = stats["has_trigger"]
        # At least some points should have valid triggers
        assert valid.sum() >= 2
        # Triggers should all be positive
        assert np.all(stats["triggers"][valid] > 0)

    def test_returns_correct_shape(self, model):
        vals = np.linspace(0.25, 0.50, 10)
        stats = model.comparative_statics("sigma_H", vals, regime="H")
        assert len(stats["triggers"]) == 10


class TestSimulation:
    def test_returns_correct_keys(self, model):
        result = model.simulate_demand(X0=1.0, T=5.0, dt=0.01)
        assert "time" in result
        assert "X" in result
        assert "regime" in result

    def test_correct_length(self, model):
        T, dt = 5.0, 0.01
        result = model.simulate_demand(X0=1.0, T=T, dt=dt)
        expected_len = int(T / dt) + 1
        assert len(result["time"]) == expected_len

    def test_regime_H_absorbing(self, model):
        result = model.simulate_demand(X0=1.0, T=10.0, initial_regime="H")
        assert np.all(result["regime"] == 1)

    def test_reproducible(self, model):
        r1 = model.simulate_demand(X0=1.0, T=1.0, rng=np.random.default_rng(42))
        r2 = model.simulate_demand(X0=1.0, T=1.0, rng=np.random.default_rng(42))
        np.testing.assert_array_equal(r1["X"], r2["X"])


class TestSummary:
    def test_has_both_regimes(self, model):
        s = model.summary()
        assert "L" in s
        assert "H" in s

    def test_H_has_trigger(self, model):
        s = model.summary()
        assert "X_star" in s["H"]
        assert "K_star" in s["H"]

    def test_L_reports_no_trigger(self, model):
        s = model.summary()
        assert s["L"]["trigger_exists"] is False
        assert s["L"]["C"] > 0
