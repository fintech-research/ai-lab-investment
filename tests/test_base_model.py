"""Tests for the single-firm base model.

Under the F_H = 0 assumption:
- option_value_H() returns 0 for all X.
- The L-regime option value uses homogeneous solution F_L = A_1 * X^{beta_L^+}.
- The joint (K, phi) optimization uses beta_L in the option premium.
- Interior capacity requires alpha > 1 - 1/beta_L (~ 0.668 at baseline).
- At baseline alpha=0.40, no interior L-regime solution exists.
"""

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


@pytest.fixture
def interior_L_params():
    """Parameters where L-regime has an interior trigger under F_H = 0."""
    return ModelParameters(alpha=0.70)


@pytest.fixture
def interior_L_model(interior_L_params):
    return SingleFirmModel(interior_L_params)


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
        """With default alpha=0.40, alpha < 1-1/beta_L ~ 0.668."""
        assert not model.has_interior_trigger("L")

    def test_has_interior_trigger_L_high_alpha(self, interior_L_model):
        """With alpha=0.70 > 0.668, L-regime has interior trigger."""
        assert interior_L_model.has_interior_trigger("L")


class TestRegimeH:
    """H-regime standalone problem (retained for reference)."""

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

    def test_option_value_H_is_zero(self, model):
        """Under F_H = 0, option value in H is 0 for all X."""
        assert model.option_value_H(0.5) == 0.0
        assert model.option_value_H(1.0) == 0.0
        assert model.option_value_H(100.0) == 0.0


class TestRegimeL:
    """L-regime tests under F_H = 0."""

    def test_no_trigger_at_baseline_raises(self, model):
        """At baseline alpha=0.40, optimal_trigger_and_capacity raises."""
        with pytest.raises(RuntimeError, match="No interior capacity"):
            model.optimal_trigger_and_capacity("L")

    def test_option_value_L_zero_at_baseline(self, model):
        """Under F_H = 0 with alpha=0.40, option value is 0."""
        assert model.option_value_L(0.01) == 0.0
        assert model.option_value_L(1.0) == 0.0

    def test_option_value_L_positive_high_alpha(self, interior_L_model):
        """With alpha=0.70, L-regime option value is positive."""
        assert interior_L_model.option_value_L(0.001) > 0

    def test_option_value_L_increasing_high_alpha(self, interior_L_model):
        """L-regime option value increases with demand."""
        assert interior_L_model.option_value_L(0.002) > interior_L_model.option_value_L(
            0.001
        )

    def test_trigger_and_capacity_high_alpha(self, interior_L_model):
        """With alpha=0.70, trigger and capacity are well-defined."""
        X_star, K_star = interior_L_model.optimal_trigger_and_capacity("L")
        assert X_star > 0
        assert K_star > 0

    def test_smooth_pasting_high_alpha(self, interior_L_model):
        """Smooth-pasting at L-regime trigger: dF/dX = A_eff."""
        p = interior_L_model.params
        X_star, K_star, A_1 = interior_L_model._solve_regime_L()
        _, _, phi_star = interior_L_model.optimal_trigger_capacity_phi()

        dF = A_1 * p.beta_L * X_star ** (p.beta_L - 1)
        dV = interior_L_model._effective_revenue_coeff_single(phi_star, K_star)
        assert abs(dF - dV) / max(abs(dV), 1e-10) < 1e-4

    def test_value_matching_high_alpha(self, interior_L_model):
        """Value-matching at L-regime trigger: F(X*) = V(X*) - I(K*)."""
        p = interior_L_model.params
        X_star, K_star, A_1 = interior_L_model._solve_regime_L()
        _, _, phi_star = interior_L_model.optimal_trigger_capacity_phi()

        option_val = A_1 * X_star**p.beta_L
        npv = interior_L_model.installed_value_with_phi(
            X_star, phi_star, K_star, "L"
        ) - interior_L_model.investment_cost(K_star)
        assert abs(option_val - npv) / max(abs(npv), 1e-10) < 1e-4


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
        assert valid.sum() >= 2
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

    def test_L_reports_error_at_baseline(self, model):
        """At baseline alpha=0.40, L-regime reports error."""
        s = model.summary()
        assert "error" in s["L"]

    def test_L_has_trigger_high_alpha(self, interior_L_model):
        s = interior_L_model.summary()
        assert "X_star" in s["L"]
        assert "K_star" in s["L"]
        assert "phi_star" in s["L"]


# ------------------------------------------------------------------
# Training-inference allocation (phi) extensions
# ------------------------------------------------------------------


class TestEffectiveRevenueCoeff:
    def test_positive(self, model):
        a_eff = model._effective_revenue_coeff_single(0.5, 1.0)
        assert a_eff > 0

    def test_phi_zero_only_inference(self, model):
        a_eff_low = model._effective_revenue_coeff_single(0.01, 1.0)
        a_eff_high = model._effective_revenue_coeff_single(0.99, 1.0)
        assert a_eff_low > 0
        assert a_eff_high > 0

    def test_no_switching_only_inference(self):
        p = ModelParameters(lam=1e-10, lam_0=0.0)
        m = SingleFirmModel(p)
        K, phi = 1.0, 0.3
        a_eff = m._effective_revenue_coeff_single(phi, K)
        expected = ((1.0 - phi) * K) ** p.alpha / (p.r - p.mu_L)
        assert abs(a_eff - expected) / expected < 0.01

    def test_increases_with_K(self, model):
        a1 = model._effective_revenue_coeff_single(0.5, 0.5)
        a2 = model._effective_revenue_coeff_single(0.5, 2.0)
        assert a2 > a1


class TestInstalledValueWithPhi:
    def test_H_regime_training_only(self, model):
        p = model.params
        X, phi, K = 1.0, 0.5, 2.0
        V = model.installed_value_with_phi(X, phi, K, "H")
        expected = p.A_H * X * (phi * K) ** p.alpha - p.delta * K / p.r
        assert abs(V - expected) < 1e-12

    def test_H_regime_higher_phi_higher_value(self, model):
        V1 = model.installed_value_with_phi(1.0, 0.3, 1.0, "H")
        V2 = model.installed_value_with_phi(1.0, 0.7, 1.0, "H")
        assert V2 > V1

    def test_L_regime_positive(self, model):
        V = model.installed_value_with_phi(2.0, 0.5, 1.0, "L")
        assert V > 0

    def test_L_regime_increases_with_X(self, model):
        V1 = model.installed_value_with_phi(0.5, 0.5, 1.0, "L")
        V2 = model.installed_value_with_phi(2.0, 0.5, 1.0, "L")
        assert V2 > V1


class TestOptimalTriggerCapacityPhi:
    """Joint (K, phi) optimization tests.

    Under F_H = 0, these require alpha > 1 - 1/beta_L for interior K*.
    """

    def test_no_solution_at_baseline(self, model):
        """At baseline alpha=0.40, optimization fails."""
        with pytest.raises(RuntimeError, match="No interior capacity"):
            model.optimal_trigger_capacity_phi()

    def test_solution_exists_high_alpha(self, interior_L_model):
        X_star, K_star, phi_star = interior_L_model.optimal_trigger_capacity_phi()
        assert X_star > 0
        assert K_star > 0
        assert 0.01 <= phi_star <= 0.99

    def test_trigger_positive_high_alpha(self, interior_L_model):
        X_star, _, _ = interior_L_model.optimal_trigger_capacity_phi()
        assert X_star > 0

    def test_phi_interior_high_alpha(self, interior_L_model):
        _, _, phi_star = interior_L_model.optimal_trigger_capacity_phi()
        assert 0.05 < phi_star < 0.95

    def test_phi_depends_on_lambda(self):
        """Higher lambda should shift phi toward training.

        Use moderate lambda values to stay within the interior condition
        alpha > 1 - 1/beta_L (higher lambda raises beta_L, tightening
        the constraint).
        """
        p_low = ModelParameters(lam=0.05, alpha=0.70)
        p_high = ModelParameters(lam=0.12, alpha=0.70)
        m_low = SingleFirmModel(p_low)
        m_high = SingleFirmModel(p_high)
        _, _, phi_low = m_low.optimal_trigger_capacity_phi()
        _, _, phi_high = m_high.optimal_trigger_capacity_phi()
        assert phi_high > phi_low

    def test_npv_positive_at_trigger_high_alpha(self, interior_L_model):
        X_star, K_star, phi_star = interior_L_model.optimal_trigger_capacity_phi()
        V = interior_L_model.installed_value_with_phi(X_star, phi_star, K_star, "L")
        cost = interior_L_model.investment_cost(K_star)
        assert V - cost > 0

    def test_trigger_formula_consistency(self, interior_L_model):
        """Verify trigger = markup * cost / A_eff."""
        p = interior_L_model.params
        X_star, K_star, phi_star = interior_L_model.optimal_trigger_capacity_phi()
        a_eff = interior_L_model._effective_revenue_coeff_single(phi_star, K_star)
        markup = p.beta_L / (p.beta_L - 1.0)
        total_cost = p.delta * K_star / p.r + p.c * K_star**p.gamma
        X_formula = markup * total_cost / a_eff
        assert abs(X_star - X_formula) / X_star < 1e-4


class TestOptionValueWithPhi:
    """Option value with phi optimization.

    Under F_H = 0, requires alpha > 1 - 1/beta_L.
    """

    def test_zero_at_baseline(self, model):
        """At baseline, option value is 0 (no interior solution)."""
        with pytest.raises(RuntimeError, match="No interior capacity"):
            model.option_value_with_phi(0.5)

    def test_positive_high_alpha(self, interior_L_model):
        assert interior_L_model.option_value_with_phi(0.001) > 0

    def test_increasing_in_X_high_alpha(self, interior_L_model):
        V1 = interior_L_model.option_value_with_phi(0.001)
        V2 = interior_L_model.option_value_with_phi(0.003)
        assert V2 > V1

    def test_exceeds_npv_before_trigger_high_alpha(self, interior_L_model):
        X_star, K_star, phi_star = interior_L_model.optimal_trigger_capacity_phi()
        X = X_star * 0.5
        option = interior_L_model.option_value_with_phi(X)
        npv = interior_L_model.installed_value_with_phi(
            X, phi_star, K_star, "L"
        ) - interior_L_model.investment_cost(K_star)
        assert option >= npv - 1e-10
