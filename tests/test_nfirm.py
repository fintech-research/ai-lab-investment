"""Tests for the N-firm numerical investment model."""

import numpy as np
import pytest

from ai_lab_investment.models.nfirm import NFirmModel
from ai_lab_investment.models.parameters import ModelParameters


@pytest.fixture
def default_params():
    return ModelParameters()


@pytest.fixture
def model3(default_params):
    """3-firm model without leverage."""
    return NFirmModel(default_params, n_firms=3, leverage=0.0)


@pytest.fixture
def model4(default_params):
    """4-firm model without leverage."""
    return NFirmModel(default_params, n_firms=4, leverage=0.0)


@pytest.fixture
def model2(default_params):
    """2-firm model for comparison with duopoly."""
    return NFirmModel(default_params, n_firms=2, leverage=0.0)


# ------------------------------------------------------------------
# Contest function
# ------------------------------------------------------------------


class TestContestFunction:
    def test_no_competitors(self, model3):
        """With no competitors, share = 1."""
        share = model3.contest_share(1.0, [])
        assert abs(share - 1.0) < 1e-12

    def test_symmetric_3firms(self, model3):
        """Three equal firms get 1/3 each."""
        share = model3.contest_share(1.0, [1.0, 1.0])
        assert abs(share - 1.0 / 3.0) < 1e-6

    def test_symmetric_4firms(self, model4):
        """Four equal firms get 1/4 each."""
        share = model4.contest_share(1.0, [1.0, 1.0, 1.0])
        assert abs(share - 0.25) < 1e-6

    def test_larger_K_higher_share(self, model3):
        """Larger capacity gives higher share."""
        share = model3.contest_share(2.0, [1.0, 1.0])
        assert share > 1.0 / 3.0


# ------------------------------------------------------------------
# Regime-specific contest functions
# ------------------------------------------------------------------


class TestRegimeContestFunctions:
    def test_L_regime_uses_inference(self, model3):
        """L-regime share depends on inference capacity (1-phi)*K."""
        # Symmetric: equal share
        s = model3.contest_share_L(1.0, 0.3, [1.0, 1.0], [0.3, 0.3])
        assert abs(s - 1.0 / 3.0) < 1e-6

        # More inference → higher L-share
        s_more = model3.contest_share_L(1.0, 0.1, [1.0, 1.0], [0.3, 0.3])
        assert s_more > 1.0 / 3.0

    def test_H_regime_uses_training(self, model3):
        """H-regime share depends on training capacity phi*K."""
        s = model3.contest_share_H(1.0, 0.3, [1.0, 1.0], [0.3, 0.3])
        assert abs(s - 1.0 / 3.0) < 1e-6

        # More training → higher H-share
        s_more = model3.contest_share_H(1.0, 0.5, [1.0, 1.0], [0.3, 0.3])
        assert s_more > 1.0 / 3.0

    def test_shares_sum_to_one(self, model3):
        """Contest shares should sum to 1 for both regimes."""
        K = [1.0, 2.0, 1.5]
        phi = [0.3, 0.4, 0.2]
        s_L = sum(
            model3.contest_share_L(
                K[i],
                phi[i],
                [K[j] for j in range(3) if j != i],
                [phi[j] for j in range(3) if j != i],
            )
            for i in range(3)
        )
        assert abs(s_L - 1.0) < 1e-6

        s_H = sum(
            model3.contest_share_H(
                K[i],
                phi[i],
                [K[j] for j in range(3) if j != i],
                [phi[j] for j in range(3) if j != i],
            )
            for i in range(3)
        )
        assert abs(s_H - 1.0) < 1e-6


# ------------------------------------------------------------------
# Single entrant
# ------------------------------------------------------------------


class TestSingleEntrant:
    def test_entrant_trigger_positive(self, model3):
        """Entrant's trigger should be positive."""
        X, K, phi = model3.solve_entrant([1.0, 1.0], [0.5, 0.5])
        assert X > 0
        assert K > 0
        assert 0 < phi < 1

    def test_more_competitors_higher_trigger(self, default_params):
        """More competitors raise the trigger."""
        m2 = NFirmModel(default_params, n_firms=2)
        m4 = NFirmModel(default_params, n_firms=4)
        X2, _, _ = m2.solve_entrant([1.0], [0.5])
        X4, _, _ = m4.solve_entrant([1.0, 1.0, 1.0], [0.5, 0.5, 0.5])
        assert X4 > X2

    def test_entrant_capacity_positive(self, model3):
        """Entrant should choose positive capacity."""
        _, K, _ = model3.solve_entrant([0.5, 0.5], [0.5, 0.5])
        assert K > 0

    def test_entrant_phi_interior(self, model3):
        """Entrant's optimal phi should be interior (0 < phi < 1)."""
        _, _, phi = model3.solve_entrant([1.0, 1.0], [0.5, 0.5])
        assert 0.01 < phi < 0.99


# ------------------------------------------------------------------
# Effective revenue coefficient
# ------------------------------------------------------------------


class TestEffectiveRevenueCoeff:
    def test_a_eff_positive(self, model3):
        """A_eff should be positive for reasonable inputs."""
        a_eff = model3._effective_revenue_coeff(1.0, 0.5, [1.0], [0.5])
        assert a_eff > 0

    def test_a_eff_increases_with_K(self, model3):
        """A_eff should increase with K (more capacity → more revenue)."""
        a1 = model3._effective_revenue_coeff(0.5, 0.5, [1.0], [0.5])
        a2 = model3._effective_revenue_coeff(2.0, 0.5, [1.0], [0.5])
        assert a2 > a1

    def test_monopolist_a_eff_higher(self, model3):
        """Monopolist A_eff > duopoly A_eff (no share loss)."""
        a_mono = model3._effective_revenue_coeff(1.0, 0.5, [], [])
        a_duo = model3._effective_revenue_coeff(1.0, 0.5, [1.0], [0.5])
        assert a_mono > a_duo


# ------------------------------------------------------------------
# Sequential equilibrium
# ------------------------------------------------------------------


class TestSequentialEquilibrium:
    def test_returns_correct_count(self, model3):
        """Should return one entry per firm."""
        eq = model3.solve_sequential_equilibrium("H")
        assert len(eq) == 3

    def test_triggers_ordered(self, model3):
        """Triggers should be in ascending order (leader < follower)."""
        eq = model3.solve_sequential_equilibrium("H")
        triggers = [e["X_trigger"] for e in eq]
        assert triggers == sorted(triggers)

    def test_all_positive(self, model3):
        """All triggers, capacities, and phis should be positive."""
        eq = model3.solve_sequential_equilibrium("H")
        for entry in eq:
            assert entry["X_trigger"] > 0
            assert entry["K_capacity"] > 0
            assert 0 < entry["phi_training"] < 1

    def test_entry_orders(self, model3):
        """Entry orders should be 1, 2, 3."""
        eq = model3.solve_sequential_equilibrium("H")
        orders = [e["entry_order"] for e in eq]
        assert orders == [1, 2, 3]

    def test_shares_sum_to_one(self, model3):
        """Market shares should sum to 1."""
        eq = model3.solve_sequential_equilibrium("H")
        total_share = sum(e["market_share"] for e in eq)
        assert abs(total_share - 1.0) < 1e-6

    def test_4firm_equilibrium(self, model4):
        """4-firm equilibrium should produce valid results."""
        eq = model4.solve_sequential_equilibrium("H")
        assert len(eq) == 4
        triggers = [e["X_trigger"] for e in eq]
        assert triggers == sorted(triggers)

    def test_has_investment_cost(self, model3):
        """Each entry should report investment cost."""
        eq = model3.solve_sequential_equilibrium("H")
        for entry in eq:
            assert "investment_cost" in entry
            assert entry["investment_cost"] > 0

    def test_has_phi_training(self, model3):
        """Each entry should report training fraction."""
        eq = model3.solve_sequential_equilibrium("H")
        for entry in eq:
            assert "phi_training" in entry
            assert 0 < entry["phi_training"] < 1


# ------------------------------------------------------------------
# Training/inference allocation (alternative quality-dynamics model)
# ------------------------------------------------------------------


class TestTrainingAllocation:
    def test_quality_model_closed_form(self, default_params):
        """Quality-dynamics phi* = eta/(alpha+eta) (alternative model)."""
        m = NFirmModel(default_params, n_firms=3)
        theta = m.optimal_training_fraction_quality_model()
        expected = default_params.eta / (default_params.alpha + default_params.eta)
        assert abs(theta - expected) < 1e-10

    def test_quality_model_independent_of_X_K(self, default_params):
        """Quality-dynamics closed-form is independent of demand/capacity."""
        m = NFirmModel(default_params, n_firms=3)
        t1 = m.optimal_training_fraction_quality_model(K=1.0, X=0.5)
        t2 = m.optimal_training_fraction_quality_model(K=10.0, X=5.0)
        assert abs(t1 - t2) < 1e-10

    def test_backward_compat_alias(self, default_params):
        """optimal_training_fraction is an alias for the quality model."""
        m = NFirmModel(default_params, n_firms=3)
        assert (
            m.optimal_training_fraction() == m.optimal_training_fraction_quality_model()
        )

    def test_quality_dynamics_increasing(self, default_params):
        """Quality should increase with training (power-law model)."""
        m = NFirmModel(default_params, n_firms=3)
        q = m.quality_dynamics(K=5.0, training_fraction=0.3, periods=10)
        assert len(q) == 11
        assert q[0] == 0.0
        assert q[-1] > q[0]
        assert all(q[i + 1] >= q[i] for i in range(len(q) - 1))

    def test_zero_training_zero_quality(self, default_params):
        """Zero training gives zero quality change."""
        m = NFirmModel(default_params, n_firms=3)
        q = m.quality_dynamics(K=2.0, training_fraction=0.0, periods=10)
        assert np.all(q == 0.0)


# ------------------------------------------------------------------
# Heterogeneous firms
# ------------------------------------------------------------------


class TestHeterogeneousFirms:
    def test_heterogeneous_solution(self, default_params):
        """Heterogeneous firms should produce valid solutions."""
        m = NFirmModel(default_params, n_firms=3)
        firm_params = [
            {"initial_K": 2.0, "leverage": 0.0},
            {"initial_K": 1.0, "leverage": 0.3},
            {"initial_K": 0.5, "leverage": 0.0},
        ]
        solutions = m.solve_heterogeneous(firm_params, regime="H")
        assert len(solutions) == 3
        for sol in solutions:
            assert sol["X_trigger"] > 0
            assert sol["K_capacity"] > 0

    def test_heterogeneous_ordered(self, default_params):
        """Solutions should be ordered by trigger."""
        m = NFirmModel(default_params, n_firms=2)
        firm_params = [
            {"initial_K": 1.0},
            {"initial_K": 1.0},
        ]
        solutions = m.solve_heterogeneous(firm_params, regime="H")
        triggers = [s["X_trigger"] for s in solutions]
        assert triggers == sorted(triggers)


# ------------------------------------------------------------------
# Verification against Phase 2
# ------------------------------------------------------------------


class TestVerification:
    def test_n2_produces_two_entries(self, model2):
        """N=2 numerical should give 2 entries."""
        eq = model2.solve_sequential_equilibrium("H")
        assert len(eq) == 2

    def test_n2_symmetric_triggers(self, model2):
        """N=2 symmetric firms should converge to equal triggers."""
        eq = model2.solve_sequential_equilibrium("H")
        assert eq[0]["X_trigger"] <= eq[1]["X_trigger"]

    def test_verification_dict_has_keys(self, model2):
        """Verification comparison should have required keys."""
        result = model2.verify_against_duopoly("H")
        assert "numerical_leader_X" in result
        assert "analytical_leader_X" in result
        assert "numerical_follower_X" in result
        assert "analytical_follower_X" in result
        assert "numerical_leader_phi" in result
        assert "analytical_leader_phi" in result


# ------------------------------------------------------------------
# Comparative statics
# ------------------------------------------------------------------


class TestComparativeStatics:
    def test_sigma_statics(self, model3):
        """Comparative statics over sigma should produce results."""
        stats = model3.comparative_statics(
            "sigma_H", np.linspace(0.25, 0.45, 5), regime="H"
        )
        assert stats["has_solution"].sum() >= 2
        assert stats["triggers"].shape == (5, 3)
        assert stats["phis"].shape == (5, 3)

    def test_more_firms_higher_triggers(self, default_params):
        """With more firms, later entrants have higher triggers."""
        m = NFirmModel(default_params, n_firms=4)
        eq = m.solve_sequential_equilibrium("H")
        for i in range(len(eq) - 1):
            assert eq[i]["X_trigger"] <= eq[i + 1]["X_trigger"]


# ------------------------------------------------------------------
# Summary
# ------------------------------------------------------------------


class TestSummary:
    def test_summary_has_entries(self, model3):
        """Summary should contain equilibrium entries."""
        s = model3.summary()
        assert "entries" in s
        assert s["n_firms"] == 3

    def test_summary_total_capacity(self, model3):
        """Summary should report total capacity."""
        s = model3.summary()
        assert "total_capacity" in s
        assert s["total_capacity"] > 0

    def test_summary_total_investment(self, model3):
        """Summary should report total investment."""
        s = model3.summary()
        assert "total_investment" in s
        assert s["total_investment"] > 0
