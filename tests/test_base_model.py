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
        """With sufficiently high alpha, regime L has an interior trigger.

        This fixture exists precisely to exercise the two-term F_L branch;
        if parameter drift ever removes the interior trigger, the test must
        fail loudly rather than skip.
        """
        # Both regimes need phi in (1/gamma, 1). High alpha + low vol works.
        p = ModelParameters(alpha=0.85, r=0.20, mu_H=0.06, sigma=0.12)
        m = SingleFirmModel(p)
        assert m.has_interior_trigger("L"), (
            "High-alpha fixture must produce an interior L-trigger; "
            "the two-term F_L branch would otherwise go untested"
        )
        X_L, K_L = m.optimal_trigger_and_capacity("L")
        assert X_L > 0
        assert K_L > 0


class TestComparativeStatics:
    def test_higher_sigma_higher_trigger_H(self, model):
        """Higher volatility -> higher trigger (more option value)."""
        stats = model.comparative_statics("sigma", np.array([0.25, 0.35]), regime="H")
        valid = stats["has_trigger"]
        assert valid.sum() == 2, "Both sigma values should yield valid triggers"
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
        stats = model.comparative_statics("sigma", vals, regime="H")
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


# ------------------------------------------------------------------
# Training-inference allocation (phi) extensions
# ------------------------------------------------------------------


class TestEffectiveRevenueCoeff:
    def test_positive(self, model):
        """A_eff should be positive for reasonable phi and K."""
        a_eff = model._effective_revenue_coeff_single(0.5, 1.0)
        assert a_eff > 0

    def test_phi_limits_match_paper_nesting(self, model):
        """eq-a-eff nesting: phi -> 0 leaves only the inference term,
        phi -> 1 leaves only the lambda-weighted H-regime term."""
        p = model.params
        K = 1.0
        denom_L = p.r - p.mu_L + p.lam

        a_eff_phi0 = model._effective_revenue_coeff_single(0.0, K)
        assert abs(a_eff_phi0 - K**p.alpha / denom_L) < 1e-12

        a_eff_phi1 = model._effective_revenue_coeff_single(1.0, K)
        expected_phi1 = p.lam / denom_L * K**p.alpha * p.A_H
        assert abs(a_eff_phi1 - expected_phi1) < 1e-12

    def test_no_switching_only_inference(self):
        """With lam=0, A_eff reduces to inference-only L-regime value."""
        p = ModelParameters(lam=1e-10, lam_0=0.0)
        m = SingleFirmModel(p)
        K, phi = 1.0, 0.3
        a_eff = m._effective_revenue_coeff_single(phi, K)
        # Should be approximately [(1-phi)*K]^alpha / (r - mu_L)
        expected = ((1.0 - phi) * K) ** p.alpha / (p.r - p.mu_L)
        assert abs(a_eff - expected) / expected < 0.01

    def test_increases_with_K(self, model):
        """A_eff should increase with capacity."""
        a1 = model._effective_revenue_coeff_single(0.5, 0.5)
        a2 = model._effective_revenue_coeff_single(0.5, 2.0)
        assert a2 > a1


class TestInstalledValueWithPhi:
    def test_H_regime_training_only(self, model):
        """H-regime value depends on training capacity (phi*K)^alpha."""
        p = model.params
        X, phi, K = 1.0, 0.5, 2.0
        V = model.installed_value_with_phi(X, phi, K, "H")
        expected = p.A_H * X * (phi * K) ** p.alpha - p.delta * K / p.r
        assert abs(V - expected) < 1e-12

    def test_H_regime_higher_phi_higher_value(self, model):
        """In H-regime, higher phi means more training → higher value."""
        V1 = model.installed_value_with_phi(1.0, 0.3, 1.0, "H")
        V2 = model.installed_value_with_phi(1.0, 0.7, 1.0, "H")
        assert V2 > V1

    def test_L_regime_positive(self, model):
        """L-regime installed value should be positive for moderate X."""
        V = model.installed_value_with_phi(2.0, 0.5, 1.0, "L")
        assert V > 0

    def test_L_regime_increases_with_X(self, model):
        """Higher demand should increase L-regime value."""
        V1 = model.installed_value_with_phi(0.5, 0.5, 1.0, "L")
        V2 = model.installed_value_with_phi(2.0, 0.5, 1.0, "L")
        assert V2 > V1


class TestOptimalTriggerCapacityPhi:
    def test_solution_exists(self, model):
        """Joint (K, phi) optimization should find a solution."""
        X_star, K_star, phi_star = model.optimal_trigger_capacity_phi()
        assert X_star > 0
        assert K_star > 0
        assert 0.01 <= phi_star <= 0.99

    def test_trigger_positive(self, model):
        X_star, _, _ = model.optimal_trigger_capacity_phi()
        assert X_star > 0

    def test_phi_interior(self, model):
        """Optimal phi should be interior (not at boundary)."""
        _, _, phi_star = model.optimal_trigger_capacity_phi()
        assert 0.05 < phi_star < 0.95

    def test_phi_depends_on_lambda(self):
        """Higher lambda should shift phi toward training."""
        p_low = ModelParameters(lam=0.05)
        p_high = ModelParameters(lam=0.50)
        m_low = SingleFirmModel(p_low)
        m_high = SingleFirmModel(p_high)
        _, _, phi_low = m_low.optimal_trigger_capacity_phi()
        _, _, phi_high = m_high.optimal_trigger_capacity_phi()
        # Higher switching rate → more valuable to have training capacity
        assert phi_high > phi_low

    def test_npv_positive_at_trigger(self, model):
        """NPV at the optimal trigger should be positive."""
        X_star, K_star, phi_star = model.optimal_trigger_capacity_phi()
        V = model.installed_value_with_phi(X_star, phi_star, K_star, "L")
        cost = model.investment_cost(K_star)
        assert V - cost > 0

    def test_reports_multistart_convergence(self, model):
        """The multistart records how many starts actually converged."""
        model.optimal_trigger_capacity_phi()
        diag = model.solver_diagnostics["trigger_capacity_phi"]
        assert diag["n_starts"] == 16
        assert diag["n_converged"] >= 1
        assert diag["best_objective"] < 1e19

    def test_rejects_unconverged_multistart(self, model, monkeypatch):
        """A run where no start converges must raise, not return the best
        non-converged value."""
        from ai_lab_investment.models import base_model as bm

        def fake_multistart(objective, starts, **kwargs):
            starts = list(starts)
            return (
                np.array([-2.0, 0.5]),
                -1.0,
                {
                    "n_starts": len(starts),
                    "n_evaluated": len(starts),
                    "n_converged": 0,
                    "best_objective": -1.0,
                },
            )

        monkeypatch.setattr(bm, "multistart_minimize", fake_multistart)
        model._cache.clear()
        with pytest.raises(RuntimeError, match="did not converge"):
            model.optimal_trigger_capacity_phi()

    def test_objective_rejects_out_of_bounds_log_K(self, model):
        """The bound guard fires before exp(log_K) is ever formed."""
        assert model._objective_K_phi(np.array([1e4, 0.5])) == 1e20
        assert model._objective_K_phi(np.array([-1e4, 0.5])) == 1e20


class TestZeroLambda:
    """The dedicated lambda = 0 branch (no regime switch is ever expected)."""

    @pytest.fixture
    def zero_lam_model(self):
        return SingleFirmModel(ModelParameters(lam=0.0))

    def test_particular_coefficient_is_zero(self, zero_lam_model):
        """C = -lambda B_H / Q_L vanishes exactly at lambda = 0."""
        assert zero_lam_model.particular_solution_coeff() == 0.0

    def test_option_value_L_has_no_switching_component(self, zero_lam_model):
        """With no interior L-trigger and C = 0, F_L is identically zero."""
        assert not zero_lam_model.has_interior_trigger("L")
        for X in [0.01, 0.05, 0.5]:
            assert zero_lam_model.option_value_L(X) == 0.0

    def test_effective_coefficient_has_no_H_term(self, zero_lam_model):
        """A_eff reduces to the pure inference perpetuity at lambda = 0."""
        p = zero_lam_model.params
        a_eff = zero_lam_model._effective_revenue_coeff_single(0.5, 1.0)
        expected = (0.5 * 1.0) ** p.alpha / (p.r - p.mu_L)
        assert abs(a_eff - expected) < 1e-15

    def test_regime_H_solution_unaffected(self, zero_lam_model, model):
        """The H-regime problem does not involve lambda at all."""
        X0, K0 = zero_lam_model.optimal_trigger_and_capacity("H")
        X1, K1 = model.optimal_trigger_and_capacity("H")
        assert abs(X0 - X1) < 1e-12
        assert abs(K0 - K1) < 1e-12

    def test_simulation_never_switches(self, zero_lam_model):
        sim = zero_lam_model.simulate_demand(
            X0=1.0, T=50.0, dt=0.01, rng=np.random.default_rng(0)
        )
        assert np.all(sim["regime"] == 0)


class TestLargeLambda:
    """Very large lambda: the L regime is a vanishing instant before H."""

    def test_phi_approaches_all_training(self):
        """When the switch is imminent, essentially everything is training."""
        m = SingleFirmModel(ModelParameters(lam=50.0))
        _, _, phi_star = m.optimal_trigger_capacity_phi()
        assert phi_star > 0.95

    def test_trigger_approaches_H_regime_trigger(self):
        """With lambda huge, the (K, phi) solution collapses onto the
        H-regime problem of Proposition 1."""
        p = ModelParameters(lam=1e4)
        m = SingleFirmModel(p)
        X_phi, K_phi, _ = m.optimal_trigger_capacity_phi()
        X_H, K_H = m.optimal_trigger_and_capacity("H")
        assert abs(K_phi - K_H) / K_H < 0.05
        assert abs(X_phi - X_H) / X_H < 0.05

    def test_simulation_switches_immediately(self):
        m = SingleFirmModel(ModelParameters(lam=500.0))
        sim = m.simulate_demand(X0=1.0, T=1.0, dt=0.001, rng=np.random.default_rng(1))
        assert sim["regime"][-1] == 1
        # 1 - exp(-0.5) ~ 39% per step: the switch happens in the first
        # handful of steps with overwhelming probability.
        assert int(np.argmax(sim["regime"] == 1)) < 50


class TestOptionValueWithPhi:
    def test_positive(self, model):
        """Option value should be positive."""
        assert model.option_value_with_phi(0.5) > 0

    def test_increasing_in_X(self, model):
        """Option value should increase with demand."""
        V1 = model.option_value_with_phi(0.3)
        V2 = model.option_value_with_phi(0.8)
        assert V2 > V1

    def test_exceeds_npv_before_trigger(self, model):
        """Option value should exceed immediate NPV before the trigger."""
        X_star, K_star, phi_star = model.optimal_trigger_capacity_phi()
        X = X_star * 0.5
        option = model.option_value_with_phi(X)
        npv = model.installed_value_with_phi(
            X, phi_star, K_star, "L"
        ) - model.investment_cost(K_star)
        assert option >= npv - 1e-10


class TestProposition1ClosedForm:
    def test_closed_form_K_star_matches_optimizer(self, model):
        """Proposition 1's closed-form K* must match the numerical optimum.

        K* = [delta*(alpha*beta_H - beta_H + 1)
              / (r*c*(gamma*(beta_H - 1) - alpha*beta_H))]^(1/(gamma-1))
        """
        p = model.params
        b = p.beta_H
        K_closed = (
            p.delta
            * (p.alpha * b - b + 1.0)
            / (p.r * p.c * (p.gamma * (b - 1.0) - p.alpha * b))
        ) ** (1.0 / (p.gamma - 1.0))
        _, K_num, _ = model.optimal_trigger_capacity_phi()
        assert abs(K_num - K_closed) / K_closed < 1e-4

    def test_raises_outside_A2_admissible_region(self):
        """When (A2)'s upper bound fails (alpha*beta_H <= beta_H - 1), the
        option-value factor diverges as K -> 0 and there is no interior
        optimum; the solver must refuse rather than return a boundary
        artifact (regression: it previously returned K* ~ 1e-322)."""
        for kwargs in [{"r": 0.15}, {"sigma": 0.18}]:
            p = ModelParameters(**kwargs)
            m = SingleFirmModel(p)
            with pytest.raises(RuntimeError, match="A2"):
                m.optimal_trigger_capacity_phi()

    def test_duopoly_leader_raises_outside_A2(self):
        """The duopoly leader-monopolist problem inherits the same
        interior-capacity condition."""
        from ai_lab_investment.models.duopoly import DuopolyModel

        duo = DuopolyModel(ModelParameters(r=0.15), leverage=0.0)
        with pytest.raises(RuntimeError, match="A2"):
            duo.solve_leader_monopolist()

    def test_K_star_independent_of_phi(self, model):
        """The optimal capacity is the same at any fixed training fraction
        (separability: A_eff = g(phi) * K^alpha cancels in the K FOC)."""
        from scipy import optimize

        capacities = []
        for phi in [0.30, 0.50, 0.70]:
            result = optimize.minimize_scalar(
                lambda log_K, phi=phi: model._objective_K_phi(np.array([log_K, phi])),
                bounds=(-15, 15),
                method="bounded",
            )
            capacities.append(np.exp(result.x))
        assert abs(capacities[0] - capacities[1]) / capacities[1] < 1e-5
        assert abs(capacities[2] - capacities[1]) / capacities[1] < 1e-5


class TestCalibrationSectionClaims:
    """Pin the admissibility and comparative-static claims made in the
    paper's calibration section (@sec-calibration)."""

    @staticmethod
    def _premium_ratio(p: ModelParameters) -> float:
        return (p.beta_H - 1.0) / (p.alpha * p.beta_H)

    def test_A2_status_at_archetype_waccs(self):
        """Section 4 states that only the hyperscaler (r = 0.10) and the
        baseline (r = 0.12) satisfy (A2); the platform (0.14), frontier
        lab (0.15), and compute racer (0.18) violate its upper bound."""
        for r in [0.10, 0.12]:
            SingleFirmModel(ModelParameters(r=r)).optimal_trigger_capacity_phi()
        for r in [0.14, 0.15, 0.18]:
            m = SingleFirmModel(ModelParameters(r=r))
            with pytest.raises(RuntimeError, match="A2"):
                m.optimal_trigger_capacity_phi()

    def test_admissible_r_window(self):
        """The (A2) window for r quoted in Section 4 is (0.097, 0.135)."""
        assert self._premium_ratio(ModelParameters(r=0.098)) > 1.0 / 1.5
        assert self._premium_ratio(ModelParameters(r=0.097)) < 1.0 / 1.5
        assert self._premium_ratio(ModelParameters(r=0.134)) < 1.0
        assert self._premium_ratio(ModelParameters(r=0.135)) > 1.0

    def test_admissible_alpha_window(self):
        """The (A2) window for alpha quoted in Section 4 is (0.356, 0.534)."""
        assert self._premium_ratio(ModelParameters(alpha=0.357)) < 1.0
        assert self._premium_ratio(ModelParameters(alpha=0.355)) > 1.0
        assert self._premium_ratio(ModelParameters(alpha=0.533)) > 1.0 / 1.5
        assert self._premium_ratio(ModelParameters(alpha=0.535)) < 1.0 / 1.5

    def test_lower_alpha_lowers_trigger_and_capacity(self):
        """Section 4's sensitivity discussion: lower alpha reduces capacity
        *and* lowers the trigger (both elasticities are positive)."""
        triggers, capacities = [], []
        for alpha in [0.38, 0.40, 0.45]:
            X, K, _ = SingleFirmModel(
                ModelParameters(alpha=alpha)
            ).optimal_trigger_capacity_phi()
            triggers.append(X)
            capacities.append(K)
        assert triggers[0] < triggers[1] < triggers[2]
        assert capacities[0] < capacities[1] < capacities[2]
        assert triggers[0] == pytest.approx(0.0015, abs=1e-4)
        assert triggers[2] == pytest.approx(0.038, abs=1e-3)

    def test_delta_is_a_capacity_normalization(self):
        """Section 4's delta = 0.10 check: delta enters only through
        b(K) = delta*K/r + c*K^gamma, so raising it is exactly a rescaling
        of the capacity unit. Levels move by the closed-form exponents;
        phi* and every ratio are unchanged."""
        base = ModelParameters()
        X0, K0, phi0 = SingleFirmModel(base).optimal_trigger_capacity_phi()
        high = base.with_param(delta=0.10)
        X1, K1, phi1 = SingleFirmModel(high).optimal_trigger_capacity_phi()

        assert abs(phi1 - phi0) < 1e-6
        scale = high.delta / base.delta
        K_ratio = scale ** (1.0 / (base.gamma - 1.0))
        X_ratio = scale ** ((base.gamma - base.alpha) / (base.gamma - 1.0))
        assert abs(K1 / K0 - K_ratio) / K_ratio < 1e-4
        assert abs(X1 / X0 - X_ratio) / X_ratio < 1e-4
        assert abs(X1 - 0.0667) < 5e-4
        assert abs(K1 - 0.0747) < 5e-4
