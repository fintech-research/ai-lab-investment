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
# Single entrant
# ------------------------------------------------------------------


class TestSingleEntrant:
    def test_entrant_trigger_positive(self, model3):
        """Entrant's trigger should be positive."""
        X, K = model3.solve_entrant([1.0, 1.0], regime="H")
        assert X > 0
        assert K > 0

    def test_more_competitors_higher_trigger(self, default_params):
        """More competitors raise the trigger."""
        m2 = NFirmModel(default_params, n_firms=2)
        m4 = NFirmModel(default_params, n_firms=4)
        X2, _ = m2.solve_entrant([1.0], regime="H")
        X4, _ = m4.solve_entrant([1.0, 1.0, 1.0], regime="H")
        assert X4 > X2

    def test_entrant_capacity_positive(self, model3):
        """Entrant should choose positive capacity."""
        _, K = model3.solve_entrant([0.5, 0.5], regime="H")
        assert K > 0


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
        """All triggers and capacities should be positive."""
        eq = model3.solve_sequential_equilibrium("H")
        for entry in eq:
            assert entry["X_trigger"] > 0
            assert entry["K_capacity"] > 0

    def test_entry_orders(self, model3):
        """Entry orders should be 1, 2, 3."""
        eq = model3.solve_sequential_equilibrium("H")
        orders = [e["entry_order"] for e in eq]
        assert orders == [1, 2, 3]

    def test_shares_sum_to_one(self, model3):
        """Market shares should approximately sum to 1."""
        eq = model3.solve_sequential_equilibrium("H")
        total_share = sum(e["market_share"] for e in eq)
        assert abs(total_share - 1.0) < 0.1  # Approximate due to different K

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


# ------------------------------------------------------------------
# Training/inference allocation
# ------------------------------------------------------------------


class TestTrainingAllocation:
    def test_zero_training_default(self, model3):
        """Default model has zero training fraction."""
        assert model3.training_fraction == 0.0

    def test_optimal_training_in_bounds(self, default_params):
        """Optimal training fraction should be in [0, 1)."""
        m = NFirmModel(
            default_params, n_firms=3, training_fraction=0.0, scaling_beta=0.1
        )
        theta = m.optimal_training_fraction(
            K=1.0, X=1.0, competitor_capacities=[1.0, 1.0], regime="H"
        )
        assert 0.0 <= theta < 1.0

    def test_quality_dynamics_increasing(self, default_params):
        """Quality should increase with training."""
        m = NFirmModel(default_params, n_firms=3, scaling_beta=0.1)
        q = m.quality_dynamics(K=2.0, training_fraction=0.3, periods=10)
        assert len(q) == 11
        assert q[0] == 0.0
        # Quality should increase (K_T = 0.6 > 1 would give positive dq)
        # Actually K_T = 0.6, log(0.6) < 0, so quality decreases
        # Use larger K so K_T > 1
        q2 = m.quality_dynamics(K=5.0, training_fraction=0.3, periods=10)
        assert q2[-1] > q2[0]  # K_T = 1.5, log(1.5) > 0

    def test_zero_training_zero_quality(self, default_params):
        """Zero training gives zero quality change."""
        m = NFirmModel(default_params, n_firms=3, scaling_beta=0.1)
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

    def test_n2_leader_before_follower(self, model2):
        """N=2 leader should invest before follower."""
        eq = model2.solve_sequential_equilibrium("H")
        assert eq[0]["X_trigger"] < eq[1]["X_trigger"]

    def test_verification_dict_has_keys(self, model2):
        """Verification comparison should have required keys."""
        result = model2.verify_against_duopoly("H")
        assert "numerical_leader_X" in result
        assert "analytical_leader_X" in result
        assert "numerical_follower_X" in result
        assert "analytical_follower_X" in result


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

    def test_summary_with_training(self, default_params):
        """Summary with training should include quality trajectory."""
        m = NFirmModel(
            default_params,
            n_firms=3,
            training_fraction=0.2,
            scaling_beta=0.1,
        )
        s = m.summary()
        assert "training_fraction" in s
        assert "leader_quality_trajectory" in s
