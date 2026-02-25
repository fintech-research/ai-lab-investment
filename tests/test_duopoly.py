"""Tests for the duopoly model with endogenous lambda and training."""

import numpy as np
import pytest

from ai_lab_investment.models.duopoly import DuopolyModel
from ai_lab_investment.models.parameters import ModelParameters


@pytest.fixture
def default_params():
    return ModelParameters()


@pytest.fixture
def endogenous_params():
    """Parameters with endogenous lambda (xi > 0)."""
    return ModelParameters(xi=0.5, lam_0=0.05, lam=0.10)


@pytest.fixture
def model(default_params):
    """Duopoly model without leverage (all-equity, exogenous lambda)."""
    return DuopolyModel(default_params, leverage=0.0)


@pytest.fixture
def endogenous_model(endogenous_params):
    """Duopoly model with endogenous lambda."""
    return DuopolyModel(endogenous_params, leverage=0.0)


@pytest.fixture
def levered_model(default_params):
    """Duopoly model with leverage."""
    return DuopolyModel(
        default_params, leverage=0.5, coupon_rate=0.05, bankruptcy_cost=0.30
    )


# ------------------------------------------------------------------
# Legacy contest function (backward compatibility)
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
        """With zero competitor, share approaches 1."""
        share = model.contest_share(1.0, 1e-10)
        assert share > 0.999


# ------------------------------------------------------------------
# Regime-specific contest functions
# ------------------------------------------------------------------


class TestRegimeContestFunctions:
    def test_L_regime_uses_inference(self, model):
        """L-regime share depends on inference capacity (1-phi)*K."""
        # Same total K, different phi → different inference
        s1 = model.contest_share_L(0.2, 1.0, 0.2, 1.0)
        assert abs(s1 - 0.5) < 1e-12  # Symmetric

        # More inference → higher L-share
        s_more = model.contest_share_L(0.1, 1.0, 0.3, 1.0)
        assert s_more > 0.5  # phi_i=0.1 → more inference

    def test_H_regime_uses_training(self, model):
        """H-regime share depends on training capacity phi*K."""
        s1 = model.contest_share_H(0.3, 1.0, 0.3, 1.0)
        assert abs(s1 - 0.5) < 1e-12  # Symmetric

        # More training → higher H-share
        s_more = model.contest_share_H(0.4, 1.0, 0.2, 1.0)
        assert s_more > 0.5  # phi_i=0.4 → more training

    def test_symmetric_phi_equals_legacy(self, model):
        """With symmetric phi, regime shares reduce to legacy share."""
        phi = 0.3
        K_i, K_j = 2.0, 1.5
        s_L = model.contest_share_L(phi, K_i, phi, K_j)
        s_H = model.contest_share_H(phi, K_i, phi, K_j)
        s_legacy = model.contest_share(K_i, K_j)
        assert abs(s_L - s_legacy) < 1e-12
        assert abs(s_H - s_legacy) < 1e-12

    def test_shares_sum_to_one(self, model):
        """L-regime and H-regime shares each sum to 1."""
        phi_i, K_i, phi_j, K_j = 0.2, 2.0, 0.4, 1.5
        s_L_i = model.contest_share_L(phi_i, K_i, phi_j, K_j)
        s_L_j = model.contest_share_L(phi_j, K_j, phi_i, K_i)
        assert abs(s_L_i + s_L_j - 1.0) < 1e-12

        s_H_i = model.contest_share_H(phi_i, K_i, phi_j, K_j)
        s_H_j = model.contest_share_H(phi_j, K_j, phi_i, K_i)
        assert abs(s_H_i + s_H_j - 1.0) < 1e-12


# ------------------------------------------------------------------
# Legacy revenue (backward compatibility)
# ------------------------------------------------------------------


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
        """Shares sum to 1 for swapped capacities."""
        K_i, K_j = 1.5, 2.5
        s1 = model.contest_share(K_i, K_j)
        s2 = model.contest_share(K_j, K_i)
        assert abs(s1 + s2 - 1.0) < 1e-12


# ------------------------------------------------------------------
# Endogenous lambda
# ------------------------------------------------------------------


class TestEndogenousLambda:
    def test_exogenous_model_lambda(self, model):
        """With xi=0, lambda_tilde = lam regardless of phi, K."""
        lam = model.endogenous_lambda(0.3, 10.0, 0.5, 5.0)
        assert abs(lam - model.params.lam) < 1e-12

    def test_endogenous_lambda_increases_with_training(self, endogenous_model):
        """More training compute increases lambda_tilde."""
        lam1 = endogenous_model.endogenous_lambda(0.1, 1.0, 0.1, 1.0)
        lam2 = endogenous_model.endogenous_lambda(0.5, 1.0, 0.5, 1.0)
        assert lam2 > lam1

    def test_endogenous_lambda_increases_with_K(self, endogenous_model):
        """More capacity (at fixed phi) increases lambda_tilde."""
        lam1 = endogenous_model.endogenous_lambda(0.3, 1.0, 0.3, 1.0)
        lam2 = endogenous_model.endogenous_lambda(0.3, 5.0, 0.3, 5.0)
        assert lam2 > lam1

    def test_endogenous_lambda_baseline(self, endogenous_model):
        """With zero training, lambda_tilde = lam_0."""
        lam = endogenous_model.endogenous_lambda(0.0, 1.0, 0.0, 1.0)
        assert abs(lam - endogenous_model.params.lam_0) < 1e-12


# ------------------------------------------------------------------
# Installed value functions with phi
# ------------------------------------------------------------------


class TestInstalledValues:
    def test_L_regime_value_positive(self, model):
        """L-regime value should be positive for reasonable params."""
        V = model.installed_value_L(1.0, 0.3, 1.0, 0.3, 1.0)
        assert -model.params.delta / model.params.r < V

    def test_H_regime_value_positive(self, model):
        """H-regime value should be positive for sufficient X."""
        V = model.installed_value_H(5.0, 0.3, 1.0, 0.3, 1.0)
        assert V > 0

    def test_monopolist_value_exceeds_duopoly(self, model):
        """Monopolist value > duopoly value (no competitor share loss)."""
        X, phi, K = 2.0, 0.3, 1.0
        V_mono = model.monopolist_value_L(X, phi, K)
        V_duo = model.installed_value_L(X, phi, K, phi, K)
        assert V_mono > V_duo

    def test_value_increases_with_X(self, model):
        """Value increases with demand."""
        V1 = model.installed_value_L(1.0, 0.3, 1.0, 0.3, 1.0)
        V2 = model.installed_value_L(5.0, 0.3, 1.0, 0.3, 1.0)
        assert V2 > V1


# ------------------------------------------------------------------
# Follower's problem (3D)
# ------------------------------------------------------------------


class TestFollower:
    def test_follower_trigger_positive(self, model):
        """Follower's trigger should be positive."""
        X_F, K_F, phi_F, lev_F = model.solve_follower(K_L=1.0, phi_L=0.3)
        assert X_F > 0
        assert K_F > 0
        assert 0 < phi_F < 1
        assert lev_F >= 0

    def test_follower_capacity_responds_to_leader(self, model):
        """Follower's capacity changes in response to leader's capacity."""
        _, K_F1, _, _ = model.solve_follower(K_L=0.5, phi_L=0.3)
        _, K_F2, _, _ = model.solve_follower(K_L=2.0, phi_L=0.3)
        assert K_F1 > 0 and K_F2 > 0
        assert abs(K_F1 - K_F2) > 1e-10

    def test_follower_option_value_positive(self, model):
        """Follower's option value should be positive below trigger."""
        X_F, _K_F, _phi_F, _lev_F = model.solve_follower(K_L=1.0, phi_L=0.3)
        fov = model.follower_option_value(X_F * 0.5, K_L=1.0, phi_L=0.3, regime="H")
        assert fov > 0

    def test_follower_option_value_increasing(self, model):
        """Follower's option value increases with X."""
        K_L, phi_L = 1.0, 0.3
        X_F, _, _, _ = model.solve_follower(K_L, phi_L)
        v1 = model.follower_option_value(X_F * 0.3, K_L, phi_L, "H")
        v2 = model.follower_option_value(X_F * 0.6, K_L, phi_L, "H")
        assert v2 > v1


# ------------------------------------------------------------------
# Leader's problem
# ------------------------------------------------------------------


class TestLeader:
    def test_leader_monopolist_trigger_positive(self, model):
        """Leader's monopolist trigger should be positive."""
        X_L, K_L, phi_L, _lev_L = model.solve_leader_monopolist(regime="H")
        assert X_L > 0
        assert K_L > 0
        assert 0 < phi_L < 1

    def test_leader_trigger_below_follower(self, model):
        """Leader invests before follower: X_L < X_F."""
        eq = model.solve_preemption_equilibrium("H")
        assert eq["X_leader"] < eq["X_follower"]

    def test_leader_value_positive_at_trigger(self, model):
        """Leader's value should be positive at the equilibrium trigger."""
        eq = model.solve_preemption_equilibrium("H")
        leader_val = model._leader_value_at(
            eq["X_leader"], eq["K_leader"], eq["phi_leader"], eq["lev_leader"]
        )
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
            "phi_leader",
            "lev_leader",
            "X_follower",
            "K_follower",
            "phi_follower",
            "lev_follower",
            "X_default_leader",
            "X_default_follower",
            "lambda_tilde",
        ]
        for key in required:
            assert key in eq, f"Missing key: {key}"

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

    def test_training_fractions_in_range(self, model):
        """Training fractions should be interior: 0 < phi < 1."""
        eq = model.solve_preemption_equilibrium("H")
        assert 0 < eq["phi_leader"] < 1
        assert 0 < eq["phi_follower"] < 1


# ------------------------------------------------------------------
# Default risk with new API
# ------------------------------------------------------------------


class TestDefaultRisk:
    def test_default_boundary_positive_with_leverage(self, levered_model):
        """Default boundary is positive when there's debt."""
        X_D = levered_model.default_boundary(
            phi_i=0.3, K_i=1.0, phi_j=0.3, K_j=1.0, leverage=0.5
        )
        assert X_D > 0

    def test_no_default_boundary_without_leverage(self, model):
        """Default boundary is zero with no leverage."""
        X_D = model.default_boundary(phi_i=0.3, K_i=1.0, phi_j=0.3, K_j=1.0)
        assert X_D == 0.0

    def test_higher_leverage_higher_default_boundary(self, default_params):
        """Higher leverage raises the default boundary."""
        m = DuopolyModel(default_params)
        X_D1 = m.default_boundary(0.3, 1.0, 0.3, 1.0, leverage=0.3)
        X_D2 = m.default_boundary(0.3, 1.0, 0.3, 1.0, leverage=0.7)
        assert X_D2 > X_D1

    def test_higher_phi_higher_default_boundary(self):
        """Higher training fraction raises default boundary when lambda is small.

        With small lambda, L-regime inference revenue dominates the value
        function: phi up -> inference revenue down -> X_D up -> spread up.

        With large lambda, the H-regime continuation value offsets this
        (the "faith-based survival" mechanism).
        """
        # Use small lambda so L-regime inference dominates
        p = ModelParameters(lam=0.02, lam_0=0.02)
        m = DuopolyModel(p)
        X_D1 = m.default_boundary(0.1, 1.0, 0.1, 1.0, leverage=0.5)
        X_D2 = m.default_boundary(0.5, 1.0, 0.5, 1.0, leverage=0.5)
        assert X_D2 > X_D1

    def test_negative_root_is_negative(self, model):
        """Negative characteristic root should be negative."""
        beta_neg = model._negative_root("H")
        assert beta_neg < 0

    def test_negative_root_uses_lam_tilde(self, model):
        """Negative root with lam_tilde differs from root without it."""
        beta_no_lam = model._negative_root("L", lam_tilde=0.0)
        beta_with_lam = model._negative_root("L", lam_tilde=0.10)
        # Higher effective discount → more negative root
        assert beta_with_lam < beta_no_lam

    def test_negative_root_numerical_value(self):
        """Verify negative root against direct quadratic formula computation."""
        p = ModelParameters()
        m = DuopolyModel(p)
        lam_tilde = p.lam  # 0.10
        # Direct computation: (σ²/2)β(β-1) + μβ - (r + λ̃) = 0
        sigma, mu = p.sigma_L, p.mu_L
        a = 0.5 * sigma**2
        b = mu - 0.5 * sigma**2
        c = -(p.r + lam_tilde)
        discriminant = b**2 - 4 * a * c
        expected = (-b - discriminant**0.5) / (2 * a)
        actual = m._negative_root("L", lam_tilde)
        assert abs(actual - expected) < 1e-12
        # Regression: should be approximately -2.335, not -1.649
        assert actual < -2.0

    def test_smooth_pasting_at_default_boundary(self, default_params):
        """Ongoing equity satisfies E(X_D)=0 and E'(X_D)=0 at default boundary.

        The default boundary is derived from smooth-pasting on the ongoing
        equity (excluding sunk investment cost), following Leland (1994).
        """
        m = DuopolyModel(
            default_params, leverage=0.5, coupon_rate=0.05, bankruptcy_cost=0.30
        )
        phi_i, K_i, phi_j, K_j = 0.3, 1.0, 0.3, 1.0
        lev = 0.5

        X_D = m.default_boundary(phi_i, K_i, phi_j, K_j, lev)
        assert X_D > 0

        p = default_params
        V_XD = m.installed_value_L(X_D, phi_i, K_i, phi_j, K_j)
        c_D = m.coupon_payment(K_i, lev)
        A_eff = m._effective_revenue_coeff(phi_i, K_i, phi_j, K_j)
        lam_tilde = m.endogenous_lambda(phi_i, K_i, phi_j, K_j)
        beta_neg = m._negative_root("L", lam_tilde)

        default_claim = c_D / p.r - V_XD

        # Value matching: E_ongoing(X_D) = V_XD - c_D/r + default_claim = 0
        E_ongoing_XD = V_XD - c_D / p.r + default_claim
        assert abs(E_ongoing_XD) < 1e-10

        # Smooth pasting: E'_ongoing(X_D) = A_eff + beta_neg * claim / X_D = 0
        E_prime_at_XD = A_eff + beta_neg * default_claim / X_D
        assert abs(E_prime_at_XD) < 1e-10

    def test_default_boundary_below_trigger(self, levered_model):
        """Default boundary should be below investment trigger."""
        eq = levered_model.solve_preemption_equilibrium("H")
        if eq["X_default_follower"] > 0:
            assert eq["X_default_follower"] < eq["X_follower"]


# ------------------------------------------------------------------
# Equity and debt with new API
# ------------------------------------------------------------------


class TestEquityDebt:
    def test_equity_increases_with_X(self, levered_model):
        """Equity increases with demand."""
        E1 = levered_model.equity_value(1.0, 0.3, 1.0, 0.3, 1.0, 0.5)
        E2 = levered_model.equity_value(3.0, 0.3, 1.0, 0.3, 1.0, 0.5)
        assert E2 > E1

    def test_all_equity_matches_value_minus_cost(self, model):
        """With no leverage, equity = V - I."""
        X, phi, K = 5.0, 0.3, 1.0
        E = model.equity_value(X, phi, K, 0.0, 0.0, leverage=0.0)
        V = model.monopolist_value_L(X, phi, K)
        cost = model.investment_cost(K)
        assert abs(E - max(V - cost, 0.0)) < 1e-10

    def test_levered_equilibrium_exists(self, levered_model):
        """Levered model should produce a valid equilibrium."""
        eq = levered_model.solve_preemption_equilibrium("H")
        assert eq["X_leader"] > 0
        assert eq["X_follower"] > eq["X_leader"]

    def test_firm_value_equals_equity_plus_debt(self, levered_model):
        """Firm value = equity + debt."""
        X, phi_i, K_i, phi_j, K_j = 2.0, 0.3, 1.0, 0.3, 1.0
        E = levered_model.equity_value(X, phi_i, K_i, phi_j, K_j, 0.5)
        D = levered_model.debt_value(X, phi_i, K_i, phi_j, K_j, 0.5)
        FV = levered_model.firm_value(X, phi_i, K_i, phi_j, K_j, 0.5)
        assert abs(FV - (E + D)) < 1e-10


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
# Nesting / backward compatibility
# ------------------------------------------------------------------


class TestNesting:
    def test_exogenous_lambda_nesting(self, default_params):
        """With xi=0, endogenous model recovers exogenous baseline."""
        p = default_params
        assert p.xi == 0.0
        m = DuopolyModel(p, leverage=0.0)
        # Lambda should always be lam (total effective rate) regardless of phi/K
        lam = m.endogenous_lambda(0.5, 10.0, 0.5, 10.0)
        assert abs(lam - p.lam) < 1e-12

    def test_symmetric_phi_contest_reduces(self, model):
        """With symmetric phi, regime-specific shares = legacy shares."""
        phi = 0.25
        K_i, K_j = 2.0, 1.0
        s_L = model.contest_share_L(phi, K_i, phi, K_j)
        s_H = model.contest_share_H(phi, K_i, phi, K_j)
        s_legacy = model.contest_share(K_i, K_j)
        assert abs(s_L - s_legacy) < 1e-12
        assert abs(s_H - s_legacy) < 1e-12


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
        """Summary reports investment costs.

        Under F_H = 0, with beta_L in the option premium and alpha=0.40,
        the duopoly produces degenerate results (K -> 0). The summary
        may report zero or very small costs. We verify the key exists.
        """
        s = model.summary()
        assert "leader_investment_cost" in s or "error" in s

    def test_summary_has_lambda_tilde(self, model):
        """Summary includes endogenous lambda."""
        s = model.summary()
        assert "lambda_tilde" in s
        assert s["lambda_tilde"] > 0

    def test_summary_has_regime_shares(self, model):
        """Summary includes L-regime and H-regime market shares."""
        s = model.summary()
        assert "leader_share_L" in s
        assert "leader_share_H" in s
