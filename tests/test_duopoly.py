"""Tests for the duopoly investment model with default risk."""

import numpy as np
import pytest

from ai_lab_investment.models.duopoly import DuopolyModel
from ai_lab_investment.models.parameters import ModelParameters


@pytest.fixture
def default_params():
    return ModelParameters()


@pytest.fixture
def model(default_params):
    """Duopoly model without leverage (all-equity)."""
    return DuopolyModel(default_params, leverage=0.0)


@pytest.fixture
def levered_model(default_params):
    """Duopoly model with leverage."""
    return DuopolyModel(
        default_params, leverage=0.5, coupon_rate=0.05, bankruptcy_cost=0.30
    )


# ------------------------------------------------------------------
# Contest function and revenue
# ------------------------------------------------------------------


class TestContestFunction:
    def test_symmetric_equal_share(self, model):
        """Equal capacity gives 50/50 split."""
        assert abs(model.contest_share(1.0, 1.0) - 0.5) < 1e-12

    def test_larger_K_higher_share(self, model):
        """Larger capacity gives higher share."""
        share = model.contest_share(2.0, 1.0)
        assert share > 0.5

    def test_share_sums_to_one(self, model):
        """Shares sum to 1."""
        s1 = model.contest_share(3.0, 2.0)
        s2 = model.contest_share(2.0, 3.0)
        assert abs(s1 + s2 - 1.0) < 1e-12

    def test_monopolist_share(self, model):
        """With zero competitor, share approaches 1 (handled by revenue)."""
        share = model.contest_share(1.0, 1e-10)
        assert share > 0.999


class TestDuopolyRevenue:
    def test_duopoly_less_than_monopoly(self, model):
        """Duopoly revenue < monopoly revenue for same capacity."""
        X, K = 1.0, 1.0
        V_mono = model.monopolist_revenue_pv(X, K, "H")
        V_duo = model.duopoly_revenue_pv(X, K, K, "H")
        assert V_duo < V_mono

    def test_revenue_increases_with_X(self, model):
        """Revenue increases with demand."""
        K = 1.0
        V1 = model.duopoly_revenue_pv(1.0, K, K, "H")
        V2 = model.duopoly_revenue_pv(2.0, K, K, "H")
        assert V2 > V1

    def test_symmetric_duopoly_revenue(self, model):
        """Symmetric firms get same revenue (swap K_i and K_j)."""
        X, K_i, K_j = 2.0, 1.5, 2.5
        V1 = model.duopoly_revenue_pv(X, K_i, K_j, "H")
        V2 = model.duopoly_revenue_pv(X, K_j, K_i, "H")
        # Swapping roles gives symmetric structure (same total, different shares)
        assert V1 != V2  # different capacities should give different values
        # But shares should sum to 1
        s1 = model.contest_share(K_i, K_j)
        s2 = model.contest_share(K_j, K_i)
        assert abs(s1 + s2 - 1.0) < 1e-12


# ------------------------------------------------------------------
# Follower's problem
# ------------------------------------------------------------------


class TestFollower:
    def test_follower_trigger_positive(self, model):
        """Follower's trigger should be positive."""
        X_F, K_F = model.solve_follower(K_L=1.0, regime="H")
        assert X_F > 0
        assert K_F > 0

    def test_follower_trigger_higher_with_larger_leader(self, model):
        """Larger leader capacity raises follower's trigger (less attractive)."""
        X_F1, _ = model.solve_follower(K_L=0.5, regime="H")
        X_F2, _ = model.solve_follower(K_L=2.0, regime="H")
        assert X_F2 > X_F1

    def test_follower_capacity_responds_to_leader(self, model):
        """Follower's capacity changes in response to leader's capacity."""
        _, K_F1 = model.solve_follower(K_L=0.5, regime="H")
        _, K_F2 = model.solve_follower(K_L=2.0, regime="H")
        assert K_F1 > 0 and K_F2 > 0
        assert abs(K_F1 - K_F2) > 1e-10, "Follower capacity should respond to leader"

    def test_follower_option_value_positive(self, model):
        """Follower's option value should be positive below trigger."""
        X_F, _K_F = model.solve_follower(K_L=1.0, regime="H")
        fov = model.follower_option_value(X_F * 0.5, K_L=1.0, regime="H")
        assert fov > 0

    def test_follower_option_value_increasing(self, model):
        """Follower's option value increases with X."""
        K_L = 1.0
        X_F, _ = model.solve_follower(K_L, regime="H")
        v1 = model.follower_option_value(X_F * 0.3, K_L, "H")
        v2 = model.follower_option_value(X_F * 0.6, K_L, "H")
        assert v2 > v1


# ------------------------------------------------------------------
# Leader's problem
# ------------------------------------------------------------------


class TestLeader:
    def test_leader_monopolist_trigger_positive(self, model):
        """Leader's monopolist trigger should be positive."""
        X_L, K_L = model.solve_leader_monopolist(regime="H")
        assert X_L > 0
        assert K_L > 0

    def test_leader_trigger_below_follower(self, model):
        """Leader invests before follower: X_L < X_F."""
        eq = model.solve_preemption_equilibrium("H")
        assert eq["X_leader"] < eq["X_follower"]

    def test_leader_value_positive_at_trigger(self, model):
        """Leader's value should be positive at the equilibrium trigger."""
        eq = model.solve_preemption_equilibrium("H")
        leader_val = model._leader_value_at(eq["X_leader"], eq["K_leader"], "H")
        assert leader_val >= 0


# ------------------------------------------------------------------
# Preemption equilibrium
# ------------------------------------------------------------------


class TestPreemptionEquilibrium:
    def test_equilibrium_has_required_keys(self, model):
        """Equilibrium result has all required keys."""
        eq = model.solve_preemption_equilibrium("H")
        required = [
            "X_leader",
            "K_leader",
            "X_follower",
            "K_follower",
            "X_default_leader",
            "X_default_follower",
        ]
        for key in required:
            assert key in eq

    def test_leader_before_follower(self, model):
        """Leader's trigger < follower's trigger."""
        eq = model.solve_preemption_equilibrium("H")
        assert eq["X_leader"] < eq["X_follower"]

    def test_all_equity_no_default(self, model):
        """With no leverage, default boundaries are zero."""
        eq = model.solve_preemption_equilibrium("H")
        assert eq["X_default_leader"] == 0.0
        assert eq["X_default_follower"] == 0.0

    def test_preemption_lowers_trigger(self, model):
        """Preemption trigger < monopolist trigger."""
        eq = model.solve_preemption_equilibrium("H")
        assert eq["X_leader"] <= eq["X_leader_monopolist"]


# ------------------------------------------------------------------
# Default risk
# ------------------------------------------------------------------


class TestDefaultRisk:
    def test_default_boundary_positive_with_leverage(self, levered_model):
        """Default boundary is positive when there's debt."""
        X_D = levered_model.default_boundary(K_i=1.0, K_j=1.0, regime="H")
        assert X_D > 0

    def test_no_default_boundary_without_leverage(self, model):
        """Default boundary is zero with no leverage."""
        X_D = model.default_boundary(K_i=1.0, K_j=1.0, regime="H")
        assert X_D == 0.0

    def test_default_boundary_below_trigger(self, levered_model):
        """Default boundary should be below investment trigger for reasonable params."""
        eq = levered_model.solve_preemption_equilibrium("H")
        if eq["X_default_follower"] > 0:
            assert eq["X_default_follower"] < eq["X_follower"]

    def test_higher_leverage_higher_default_boundary(self, default_params):
        """Higher leverage raises the default boundary."""
        m1 = DuopolyModel(default_params, leverage=0.3)
        m2 = DuopolyModel(default_params, leverage=0.7)
        X_D1 = m1.default_boundary(1.0, 1.0, "H")
        X_D2 = m2.default_boundary(1.0, 1.0, "H")
        assert X_D2 > X_D1

    def test_negative_root_is_negative(self, model):
        """Negative characteristic root should be negative."""
        beta_neg = model._negative_root("H")
        assert beta_neg < 0

    def test_equity_value_positive_above_default(self, levered_model):
        """Equity value should be positive well above default boundary."""
        # Use equilibrium values where the firm has optimally invested
        eq = levered_model.solve_preemption_equilibrium("H")
        X_F = eq["X_follower"]
        K_F = eq["K_follower"]
        K_L = eq["K_leader"]
        E = levered_model.equity_value(X_F * 2, K_F, K_L, "H")
        assert E > 0

    def test_debt_value_positive(self, levered_model):
        """Debt value should be positive."""
        D = levered_model.debt_value(1.0, 1.0, 1.0, "H")
        assert D > 0

    def test_firm_value_equals_equity_plus_debt(self, levered_model):
        """Firm value = equity + debt."""
        X, K_i, K_j = 2.0, 1.0, 1.0
        E = levered_model.equity_value(X, K_i, K_j, "H")
        D = levered_model.debt_value(X, K_i, K_j, "H")
        FV = levered_model.firm_value(X, K_i, K_j, "H")
        assert abs(FV - (E + D)) < 1e-10


# ------------------------------------------------------------------
# Equity and debt with leverage
# ------------------------------------------------------------------


class TestEquityDebt:
    def test_equity_increases_with_X(self, levered_model):
        """Equity increases with demand."""
        E1 = levered_model.equity_value(1.0, 1.0, 1.0, "H")
        E2 = levered_model.equity_value(3.0, 1.0, 1.0, "H")
        assert E2 > E1

    def test_all_equity_matches_no_debt(self, model):
        """With no leverage, equity = V - I."""
        X, K = 5.0, 1.0
        E = model.equity_value(X, K, 0.0, "H")
        V = model.monopolist_revenue_pv(X, K, "H")
        cost = model.investment_cost(K)
        assert abs(E - (V - cost)) < 1e-10

    def test_levered_equilibrium_exists(self, levered_model):
        """Levered model should produce a valid equilibrium."""
        eq = levered_model.solve_preemption_equilibrium("H")
        assert eq["X_leader"] > 0
        assert eq["X_follower"] > eq["X_leader"]


# ------------------------------------------------------------------
# Comparative statics
# ------------------------------------------------------------------


class TestComparativeStatics:
    def test_sigma_statics_has_solutions(self, model):
        """Comparative statics over sigma should produce solutions."""
        stats = model.comparative_statics("sigma_H", np.linspace(0.25, 0.45, 5))
        assert stats["has_solution"].sum() >= 2

    def test_leverage_statics_has_solutions(self, default_params):
        """Leverage comparative statics should produce solutions."""
        m = DuopolyModel(default_params, leverage=0.3)
        stats = m.leverage_comparative_statics(np.linspace(0.0, 0.6, 5))
        assert stats["has_solution"].sum() >= 2

    def test_leader_always_before_follower_in_statics(self, model):
        """In all valid solutions, leader trigger < follower trigger."""
        stats = model.comparative_statics("sigma_H", np.linspace(0.25, 0.45, 5))
        valid = stats["has_solution"]
        if valid.sum() > 0:
            assert np.all(stats["X_leader"][valid] <= stats["X_follower"][valid])


# ------------------------------------------------------------------
# Summary
# ------------------------------------------------------------------


class TestSummary:
    def test_summary_has_equilibrium(self, model):
        """Summary should contain equilibrium info."""
        s = model.summary()
        assert "equilibrium" in s
        assert "leader_npv" in s

    def test_summary_levered(self, levered_model):
        """Levered model summary should include leverage info."""
        s = levered_model.summary()
        assert s["leverage"] == 0.5

    def test_summary_reports_costs(self, model):
        """Summary reports investment costs."""
        s = model.summary()
        assert "leader_investment_cost" in s
        assert s["leader_investment_cost"] > 0
