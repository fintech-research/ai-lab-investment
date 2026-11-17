"""Tests for the duopoly model with endogenous lambda and training."""

import numpy as np
import pytest

from ai_lab_investment.models.base_model import SingleFirmModel
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
        """L-regime value should be strictly positive for reasonable params."""
        V = model.installed_value_L(1.0, 0.3, 1.0, 0.3, 1.0)
        assert V > 0

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
# Cross-model consistency (duopoly vs single-firm)
# ------------------------------------------------------------------


class TestCrossModelConsistency:
    def test_zero_leverage_leader_matches_single_firm(self, model):
        """At zero leverage the leader-monopolist problem IS the single-firm
        problem: identical objectives must give identical (X*, K*, phi*).

        Regression test for the leverage-drift bug, where the optimizer let
        the leverage coordinate run to its bound before clipping, inflating
        K by a factor of ~5.
        """
        sf = SingleFirmModel(model.params)
        X_s, K_s, phi_s = sf.pure_power_trigger_capacity_phi()
        X_L, K_L, phi_L, lev_L = model.solve_leader_monopolist("H")
        assert lev_L == 0.0
        assert abs(X_L - X_s) / X_s < 1e-4
        assert abs(K_L - K_s) / K_s < 1e-4
        assert abs(phi_L - phi_s) < 1e-4

    def test_solve_no_competition_matches_single_firm(self, model):
        """The verification bridge method must agree with SingleFirmModel."""
        sf = SingleFirmModel(model.params)
        X_s, K_s = sf.optimal_trigger_and_capacity("H")
        X_d, K_d = model.solve_no_competition("H")
        assert abs(X_d - X_s) / X_s < 1e-10
        assert abs(K_d - K_s) / K_s < 1e-10

    def test_fixed_pie_symmetric_matches_tullock(self, default_params):
        """Under symmetry, fixed-pie A_eff equals Tullock A_eff exactly."""
        duo_t = DuopolyModel(default_params, contest="tullock")
        duo_fp = DuopolyModel(default_params, contest="fixed_pie")
        phi, K = 0.4, 1.3
        a_t = duo_t._effective_revenue_coeff(phi, K, phi, K)
        a_fp = duo_fp._effective_revenue_coeff(phi, K, phi, K)
        assert abs(a_t - a_fp) < 1e-12

    def test_fixed_pie_follower_not_degenerate(self, default_params):
        """Fixed-pie follower capacity equals the single-firm K* (the
        half-revenue problem has the same scale-invariant FOC for K)."""
        duo_fp = DuopolyModel(default_params, contest="fixed_pie")
        sf = SingleFirmModel(default_params)
        _, K_s, _ = sf.pure_power_trigger_capacity_phi()
        _, K_F, _, _ = duo_fp.solve_follower(K_L=K_s, phi_L=0.70)
        assert abs(K_F - K_s) / K_s < 1e-3


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

    def test_preemption_lowers_trigger(self, model):
        """Preemption trigger < monopolist trigger."""
        eq = model.solve_preemption_equilibrium("H")
        assert eq["X_leader"] <= eq["X_leader_monopolist"]

    def test_training_fractions_in_range(self, model):
        """Training fractions should be interior: 0 < phi < 1."""
        eq = model.solve_preemption_equilibrium("H")
        assert 0 < eq["phi_leader"] < 1

    def test_single_crossing_verified(self, model):
        """L(X) - F(X) should have exactly one sign change (single crossing)."""
        eq = model.solve_preemption_equilibrium("H")
        assert eq["single_crossing"]
        assert 0 < eq["phi_follower"] < 1

    def test_reports_solver_diagnostics(self, model):
        """The equilibrium dict carries the bracket and multistart
        diagnostics needed to tell a solved root from a fallback."""
        eq = model.solve_preemption_equilibrium("H")
        assert eq["bracket_failed"] is False
        assert eq["n_sign_changes"] == 1
        diag = eq["solver_diagnostics"]
        assert diag["leader_monopolist"]["n_converged"] >= 1
        assert diag["follower"]["n_converged"] >= 1


# ------------------------------------------------------------------
# Preemption failure paths: strict mode must raise
# ------------------------------------------------------------------


class TestPreemptionFailurePaths:
    """A failed bracket is not an equilibrium. Paper-generating paths run
    in strict mode and must raise; the strict=False escape hatch returns
    the endpoint fallback with bracket_failed set."""

    @staticmethod
    def _force_gap(model, gap_fn):
        model._preemption_gap = gap_fn

    def test_positive_gap_at_lower_endpoint_raises(self, model):
        """L - F already non-negative at X_low: no first up-crossing."""
        self._force_gap(model, lambda X, regime: 1.0)
        with pytest.raises(RuntimeError, match="No preemption equilibrium"):
            model.solve_preemption_equilibrium("H")

    def test_no_sign_change_raises(self, model):
        """L - F never turns positive on (X_D, X_L^mono)."""
        self._force_gap(model, lambda X, regime: -1.0)
        with pytest.raises(RuntimeError, match="no sign change"):
            model.solve_preemption_equilibrium("H")

    def test_brent_failure_raises(self, model):
        """A grid sign change that Brent cannot reproduce still raises."""
        X_mid = model.solve_leader_monopolist("H")[0] * 0.5
        calls = {"n": 0}

        def flaky_gap(X, regime):
            calls["n"] += 1
            if calls["n"] <= 500:  # the grid scan brackets a root
                return X - X_mid
            return 1.0  # ... which has vanished by the time Brent runs

        self._force_gap(model, flaky_gap)
        with pytest.raises(RuntimeError, match="Brent"):
            model.solve_preemption_equilibrium("H")

    def test_non_strict_returns_flagged_fallback(self, model):
        """strict=False keeps the old endpoint fallback, but flags it."""
        self._force_gap(model, lambda X, regime: -1.0)
        eq = model.solve_preemption_equilibrium("H", strict=False)
        assert eq["bracket_failed"] is True
        assert eq["X_leader"] == eq["X_leader_monopolist"]

    def test_non_strict_lower_endpoint_fallback(self, model):
        self._force_gap(model, lambda X, regime: 1.0)
        eq = model.solve_preemption_equilibrium("H", strict=False)
        assert eq["bracket_failed"] is True
        assert eq["X_leader"] < eq["X_leader_monopolist"]

    def test_strict_is_the_default(self, model):
        """Callers that do not opt out get the raising behaviour."""
        self._force_gap(model, lambda X, regime: -1.0)
        with pytest.raises(RuntimeError):
            model.solve_preemption_equilibrium()

    def test_strict_and_non_strict_cached_separately(self, model):
        """The escape hatch must not poison the strict cache entry."""
        eq_strict = model.solve_preemption_equilibrium("H")
        eq_loose = model.solve_preemption_equilibrium("H", strict=False)
        assert eq_loose["X_leader"] == eq_strict["X_leader"]
        assert eq_loose["bracket_failed"] is False


# ------------------------------------------------------------------
# Domain guards on public methods
# ------------------------------------------------------------------


class TestDomainGuards:
    """Invalid parameters and allocations fail loudly rather than
    silently producing nan through a negative fractional power."""

    def test_contest_share_L_rejects_phi_above_one(self, model):
        with pytest.raises(ValueError, match="phi must be in"):
            model.contest_share_L(1.2, 1.0, 0.5, 1.0)

    def test_contest_share_L_rejects_negative_rival_phi(self, model):
        with pytest.raises(ValueError, match="phi must be in"):
            model.contest_share_L(0.5, 1.0, -0.1, 1.0)

    def test_contest_share_H_rejects_phi_above_one(self, model):
        with pytest.raises(ValueError, match="phi must be in"):
            model.contest_share_H(1.2, 1.0, 0.5, 1.0)

    @pytest.mark.parametrize("phi", [-0.1, 1.2])
    def test_value_functions_reject_out_of_range_phi(self, model, phi):
        with pytest.raises(ValueError, match="phi must be in"):
            model.installed_value_L(0.1, phi, 1.0, 0.5, 1.0)
        with pytest.raises(ValueError, match="phi must be in"):
            model.installed_value_H(0.1, phi, 1.0, 0.5, 1.0)
        with pytest.raises(ValueError, match="phi must be in"):
            model.monopolist_value_L(0.1, phi, 1.0)
        with pytest.raises(ValueError, match="phi must be in"):
            model.monopolist_value_H(0.1, phi, 1.0)

    @pytest.mark.parametrize("phi", [-0.1, 1.2])
    def test_credit_objects_reject_out_of_range_phi(self, levered_model, phi):
        with pytest.raises(ValueError, match="phi must be in"):
            levered_model.default_boundary(phi, 1.0, 0.0, 0.0)
        with pytest.raises(ValueError, match="phi must be in"):
            levered_model.equity_value(0.1, phi, 1.0, 0.0, 0.0)
        with pytest.raises(ValueError, match="phi must be in"):
            levered_model.debt_value(0.1, phi, 1.0, 0.0, 0.0)
        with pytest.raises(ValueError, match="phi must be in"):
            levered_model.liquidation_value(0.1, phi, 1.0, 0.0, 0.0)
        with pytest.raises(ValueError, match="phi must be in"):
            levered_model.firm_value(0.1, phi, 1.0, 0.0, 0.0)

    def test_boundary_phi_values_allowed(self, model):
        """phi = 0 and phi = 1 are admissible corners, not errors."""
        assert model.contest_share_L(0.0, 1.0, 0.0, 1.0) == pytest.approx(0.5)
        assert model.contest_share_H(1.0, 1.0, 1.0, 1.0) == pytest.approx(0.5)

    @pytest.mark.parametrize("lev", [-0.1, 1.5])
    def test_leverage_out_of_range_raises(self, default_params, lev):
        with pytest.raises(ValueError, match="Leverage"):
            DuopolyModel(default_params, leverage=lev)

    def test_non_positive_coupon_rate_raises(self, default_params):
        with pytest.raises(ValueError, match="Coupon rate"):
            DuopolyModel(default_params, leverage=0.4, coupon_rate=0.0)

    @pytest.mark.parametrize("bc", [-0.1, 1.5])
    def test_bankruptcy_cost_out_of_range_raises(self, default_params, bc):
        with pytest.raises(ValueError, match="Bankruptcy cost"):
            DuopolyModel(default_params, leverage=0.4, bankruptcy_cost=bc)


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
        sigma, mu = p.sigma, p.mu_L
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

        # Smooth pasting: E'_ongoing(X_D) = A_eff + beta_neg * claim / X_D = 0
        E_prime_at_XD = A_eff + beta_neg * default_claim / X_D
        assert abs(E_prime_at_XD) < 1e-10

        # Optimality (Leland): the smooth-pasting boundary maximizes the
        # ongoing equity value over candidate boundaries. For a candidate
        # boundary B, value matching pins the option coefficient and
        # G(X; B) = A_eff*X - (delta*K + c_D)/r
        #           + [(delta*K + c_D)/r - A_eff*B] * (X/B)^beta_neg.
        # G(X; X_D) must dominate perturbed boundaries at any X > X_D.
        N = (p.delta * K_i + c_D) / p.r

        def ongoing_equity(X, B):
            return A_eff * X - N + (N - A_eff * B) * (X / B) ** beta_neg

        X_test = 2.0 * X_D
        g_opt = ongoing_equity(X_test, X_D)
        assert g_opt > ongoing_equity(X_test, 0.9 * X_D)
        assert g_opt > ongoing_equity(X_test, 1.1 * X_D)

    def test_debt_value_matching_at_default(self, default_params):
        """As X -> X_D, debt value converges to the capped recovery."""
        m = DuopolyModel(
            default_params, leverage=0.5, coupon_rate=0.05, bankruptcy_cost=0.30
        )
        phi_i, K_i, phi_j, K_j = 0.3, 1.0, 0.3, 1.0
        lev = 0.5
        p = default_params

        X_D = m.default_boundary(phi_i, K_i, phi_j, K_j, lev)
        c_D = m.coupon_payment(K_i, lev)
        recovery = m.recovery_value(phi_i, K_i, phi_j, K_j, lev)
        assert 0.0 <= recovery <= c_D / p.r

        D_at_boundary = m.debt_value(X_D * (1.0 + 1e-9), phi_i, K_i, phi_j, K_j, lev)
        assert abs(D_at_boundary - recovery) < 1e-6

    def test_debt_never_exceeds_riskless_value(self, default_params):
        """Absolute priority cap: D(X) <= c_D / r at every demand level."""
        m = DuopolyModel(
            default_params, leverage=0.3, coupon_rate=0.05, bankruptcy_cost=0.30
        )
        K_i = 1.0
        c_D = m.coupon_payment(K_i, 0.3)
        p = default_params
        for X in [0.05, 0.1, 0.5, 1.0, 5.0]:
            D = m.debt_value(X, 0.3, K_i, 0.3, 1.0, 0.3)
            assert c_D / p.r + 1e-12 >= D

    def test_default_boundary_below_trigger(self, levered_model):
        """Default boundary is positive under leverage and below the trigger."""
        eq = levered_model.solve_preemption_equilibrium("H")
        assert eq["X_default_follower"] > 0
        assert eq["X_default_follower"] < eq["X_follower"]

    def test_faith_based_survival_at_optimal_phi(self):
        """Proposition 2(ii): dX_D/dlambda < 0 at the optimal training
        fraction (phi* well above the threshold phi_underbar)."""
        from ai_lab_investment.models.base_model import SingleFirmModel

        p = ModelParameters()
        _, K_star, phi_star = SingleFirmModel(p).pure_power_trigger_capacity_phi()
        h = 1e-4

        def x_d(lam):
            m = DuopolyModel(p.with_param(lam=lam), leverage=0.40)
            return m.default_boundary(phi_star, K_star, 0.0, 0.0, 0.40)

        dXD_dlam = (x_d(p.lam + h) - x_d(p.lam - h)) / (2 * h)
        assert dXD_dlam < 0

    def test_default_boundary_increasing_in_lambda_below_threshold(self):
        """Below phi_underbar both channels push the same way: the
        A_eff-channel turns positive (inference dominates) and the
        beta-channel is always positive, so dX_D/dlambda > 0."""
        p = ModelParameters()
        phi_low = 0.05  # well below phi_underbar ~ 0.18
        h = 1e-4

        def x_d(lam):
            m = DuopolyModel(p.with_param(lam=lam), leverage=0.40)
            return m.default_boundary(phi_low, 1.0, 0.0, 0.0, 0.40)

        dXD_dlam = (x_d(p.lam + h) - x_d(p.lam - h)) / (2 * h)
        assert dXD_dlam > 0

    def test_exact_threshold_phi_tilde_flips_dXD_dlambda(self):
        """The closed-form exact threshold phi_tilde (both channels) is the
        precise sign-flip point of dX_D/dlambda; phi_tilde > phi_underbar."""
        p = ModelParameters()
        d = DuopolyModel(p, leverage=0.40)
        phi_tilde = d.faith_threshold_exact()
        assert d.faith_threshold() < phi_tilde
        assert abs(d.faith_threshold() - 0.180) < 0.005
        assert abs(phi_tilde - 0.322) < 0.005  # baseline value

        h = 1e-5

        def dXD(phi):
            def xd(lam):
                m = DuopolyModel(p.with_param(lam=lam), leverage=0.40)
                return m.default_boundary(phi, 1.0, 0.0, 0.0, 0.40)

            return (xd(p.lam + h) - xd(p.lam - h)) / (2 * h)

        assert dXD(phi_tilde - 0.002) > 0
        assert dXD(phi_tilde + 0.002) < 0

    def test_faith_based_survival_reverses_at_low_lambda(self):
        """At very pessimistic beliefs the optimal allocation falls below
        the exact threshold (phi*(lambda) < phi_tilde(lambda) for
        lambda < lambda_bar ~ 0.034 at baseline), so dX_D/dlambda > 0 at
        the optimum -- the refinement delivered by the closed form."""
        from ai_lab_investment.models.base_model import SingleFirmModel

        p0 = ModelParameters()
        h = 1e-5
        # dXD_sign > 0 (boundary rising in lambda) iff phi* < phi_tilde
        for lam, dXD_sign in [(0.02, 1), (0.05, -1)]:
            pl = p0.with_param(lam=lam)
            _, K, phi = SingleFirmModel(pl).pure_power_trigger_capacity_phi()
            d = DuopolyModel(pl, leverage=0.40)
            phi_tilde = d.faith_threshold_exact()
            assert np.sign(phi - phi_tilde) == -dXD_sign

            def xd(la, phi=phi, K=K):
                m = DuopolyModel(p0.with_param(lam=la), leverage=0.40)
                return m.default_boundary(phi, K, 0.0, 0.0, 0.40)

            dXD = (xd(lam + h) - xd(lam - h)) / (2 * h)
            assert np.sign(dXD) == dXD_sign

    def test_phi_underbar_closed_form_is_aeff_lambda_threshold(self):
        """Eq phi-underbar: at phi = phi_underbar (symmetric duopoly),
        dA_eff/dlambda = 0; above it positive, below it negative."""
        p = ModelParameters()
        R = ((p.r - p.mu_H) / (p.r - p.mu_L)) ** (1.0 / p.alpha)
        phi_underbar = R / (1.0 + R)
        assert abs(phi_underbar - 0.180) < 0.005  # paper value

        K = 1.0
        h = 1e-5

        def a_eff(phi, lam):
            m = DuopolyModel(p.with_param(lam=lam))
            # Symmetric duopoly: equal capacities and training fractions
            return m._effective_revenue_coeff(phi, K, phi, K)

        for phi, expected_sign in [
            (phi_underbar, 0),
            (phi_underbar + 0.05, 1),
            (phi_underbar - 0.05, -1),
        ]:
            dA = (a_eff(phi, p.lam + h) - a_eff(phi, p.lam - h)) / (2 * h)
            if expected_sign == 0:
                assert abs(dA) < 1e-6
            else:
                assert np.sign(dA) == expected_sign


# ------------------------------------------------------------------
# Equity and debt with new API
# ------------------------------------------------------------------


class TestEquityDebt:
    def test_equity_increases_with_X(self, levered_model):
        """Equity increases with demand."""
        E1 = levered_model.equity_value(1.0, 0.3, 1.0, 0.3, 1.0, 0.5)
        E2 = levered_model.equity_value(3.0, 0.3, 1.0, 0.3, 1.0, 0.5)
        assert E2 > E1

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
        stats = model.comparative_statics("sigma", np.linspace(0.25, 0.45, 5))
        assert stats["has_solution"].sum() >= 2

    def test_leverage_statics_has_solutions(self, default_params):
        """Leverage comparative statics should produce solutions."""
        m = DuopolyModel(default_params, leverage=0.3)
        stats = m.leverage_comparative_statics(np.linspace(0.0, 0.6, 5))
        assert stats["has_solution"].sum() >= 2

    def test_leader_always_before_follower_in_statics(self, model):
        """In all valid solutions, leader trigger < follower trigger."""
        stats = model.comparative_statics("sigma", np.linspace(0.25, 0.45, 5))
        valid = stats["has_solution"]
        assert valid.sum() > 0
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
        """Summary reports investment costs."""
        s = model.summary()
        assert "leader_investment_cost" in s
        assert s["leader_investment_cost"] > 0

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


class TestCoupledDefaultBoundary:
    def test_single_boundary_overstates_coupled(self, default_params):
        """The single-boundary formula omits the positive H-regime default
        option, so it weakly overstates the coupled boundary; the error is
        small (a few percent) at baseline."""
        m = DuopolyModel(
            default_params, leverage=0.4, coupon_rate=0.05, bankruptcy_cost=0.30
        )
        phi_i, K_i, phi_j, K_j = 0.70, 1.0, 0.70, 1.0
        X_D = m.default_boundary(phi_i, K_i, phi_j, K_j)
        X_D_c = m.default_boundary_coupled(phi_i, K_i, phi_j, K_j)
        assert X_D_c > 0
        assert X_D_c <= X_D
        assert (X_D - X_D_c) / X_D_c < 0.05

    def test_scalar_reduction_satisfies_both_boundary_conditions(self, default_params):
        """The Brent root of the scalar equation must satisfy value matching
        AND smooth pasting of the coupled system (the elimination of the
        homogeneous coefficient is exact)."""
        m = DuopolyModel(
            default_params, leverage=0.4, coupon_rate=0.05, bankruptcy_cost=0.30
        )
        phi_i, K_i, phi_j, K_j = 0.70, 1.0, 0.70, 1.0
        X_D = m.default_boundary_coupled(phi_i, K_i, phi_j, K_j)
        terms = m._coupled_boundary_terms(phi_i, K_i, phi_j, K_j, 0.4)
        assert terms is not None
        a_eff, N, C_2, b_L, b_H = terms
        # Recover the homogeneous coefficient from smooth pasting, then
        # check value matching holds.
        A_neg = -(a_eff + C_2 * b_H * X_D ** (b_H - 1.0)) * X_D ** (1.0 - b_L) / b_L
        E = a_eff * X_D - N + C_2 * X_D**b_H + A_neg * X_D**b_L
        E_prime = (
            a_eff + C_2 * b_H * X_D ** (b_H - 1.0) + A_neg * b_L * X_D ** (b_L - 1.0)
        )
        assert abs(E) < 1e-12
        assert abs(E_prime) < 1e-9

    def test_linear_bias_approximates_exact_bias(self, default_params):
        """The closed-form first-order kappa is within 0.5pp of the exact
        relative bias (X_D0 - X_D_coupled)/X_D0, both ~3% at baseline."""
        m = DuopolyModel(
            default_params, leverage=0.4, coupon_rate=0.05, bankruptcy_cost=0.30
        )
        phi_i, K_i, phi_j, K_j = 0.70, 1.0, 0.70, 1.0
        X_D0 = m.default_boundary(phi_i, K_i, phi_j, K_j)
        X_Dc = m.default_boundary_coupled(phi_i, K_i, phi_j, K_j)
        exact_bias = (X_D0 - X_Dc) / X_D0
        kappa = m.coupled_boundary_bias_linear(phi_i, K_i, phi_j, K_j)
        assert 0.02 < exact_bias < 0.05
        assert kappa > 0
        assert abs(kappa - exact_bias) < 0.005


class TestFollowerScalarReduction:
    """The follower's problem separates at a common training fraction:
    A_eff,F = g(phi) * K^{2 alpha}/(K^alpha + K_L^alpha), so K_F solves a
    scalar FOC with effective elasticity alpha*(2 - s_F)."""

    def test_matches_nelder_mead(self, default_params):
        """Scalar reduction agrees with the 2-D optimizer (both leverages)."""
        for lev in [0.0, 0.40]:
            m = DuopolyModel(
                default_params, leverage=lev, coupon_rate=0.05, bankruptcy_cost=0.30
            )
            _, K_L, phi_L, _ = m.solve_leader_monopolist()
            X_nm, K_nm, phi_nm, _ = m.solve_follower(K_L, phi_L)
            X_sc, K_sc, phi_sc, _ = m.solve_follower_scalar(K_L, phi_L)
            assert abs(K_sc / K_nm - 1.0) < 1e-6
            assert abs(X_sc / X_nm - 1.0) < 1e-6
            assert abs(phi_sc - phi_nm) < 1e-4

    def test_allocation_foc_exact_at_common_phi(self, default_params):
        """Role invariance is exact: at phi_F = phi_L = phi*, the follower's
        allocation FOC is zero even under asymmetric capacities, because
        the common factor s(2 - s) cancels across regimes."""
        from ai_lab_investment.models.base_model import SingleFirmModel

        _, K_L, phi_star = SingleFirmModel(
            default_params
        ).pure_power_trigger_capacity_phi()
        m = DuopolyModel(default_params, leverage=0.0)
        K_F = 40.0 * K_L  # strongly asymmetric capacities
        h = 1e-7
        dA = (
            m._effective_revenue_coeff(phi_star + h, K_F, phi_star, K_L)
            - m._effective_revenue_coeff(phi_star - h, K_F, phi_star, K_L)
        ) / (2 * h)
        A = m._effective_revenue_coeff(phi_star, K_F, phi_star, K_L)
        assert abs(dA / A) < 1e-5

    def test_requires_tullock(self, default_params):
        m = DuopolyModel(default_params, leverage=0.0, contest="fixed_pie")
        with pytest.raises(RuntimeError, match="Tullock"):
            m.solve_follower_scalar(0.01, 0.70)

    def test_single_crossing_at_zero_leverage(self, default_params):
        """Supporting check for the analytical uniqueness result: the
        preemption gap has exactly one up-crossing at ell = 0 across
        lambda values (gap is strictly concave there)."""
        for lam in [0.05, 0.10, 0.20]:
            m = DuopolyModel(default_params.with_param(lam=lam), leverage=0.0)
            eq = m.solve_preemption_equilibrium("H")
            assert eq["single_crossing"] is True


# ------------------------------------------------------------------
# Equity convention: going-concern claim floored, entry NPV not
# ------------------------------------------------------------------


class TestEquityConvention:
    """One equity convention across paper, proof, and code: limited
    liability floors the *going-concern* claim E, and the object the
    entry decision uses is E(X) - (1 - ell) I(K), which is negative near
    the origin. That negativity is the L(0) < 0 = F(0) endpoint of the
    Proposition 3(i) existence argument."""

    def test_levered_entry_npv_below_default_boundary(self, levered_model):
        """Below X_D the going concern is worthless and the sunk equity
        contribution is lost: entry NPV == -(1 - ell) I(K), exactly."""
        phi, K, lev = 0.70, 1.0, 0.5
        X_D = levered_model.default_boundary(phi, K, 0.0, 0.0, lev)
        assert X_D > 0
        expected = -(1.0 - lev) * levered_model.investment_cost(K)
        for X in [1e-9, X_D * 0.5, X_D]:
            npv = levered_model.equity_value(X, phi, K, 0.0, 0.0, lev)
            assert abs(npv - expected) < 1e-12

    def test_going_concern_continuous_and_zero_at_boundary(self, levered_model):
        """E(X_D) = 0 by smooth pasting, so the limited-liability floor on
        the going-concern claim is a guard that never binds above X_D."""
        phi, K, lev = 0.70, 1.0, 0.5
        X_D = levered_model.default_boundary(phi, K, 0.0, 0.0, lev)
        contribution = (1.0 - lev) * levered_model.investment_cost(K)
        for eps in [1e-8, 1e-6, 1e-4]:
            npv = levered_model.equity_value(X_D * (1 + eps), phi, K, 0.0, 0.0, lev)
            going_concern = npv + contribution
            assert going_concern >= 0.0
            assert going_concern < 1e-3 * contribution

    def test_leader_value_negative_at_low_demand(self, model):
        """L(X) < 0 = F(0) at low demand -- no clamp on the leader's NPV."""
        eq = model.solve_preemption_equilibrium("H")
        K_L, phi_L = eq["K_leader"], eq["phi_leader"]
        for frac in [1e-4, 1e-2, 0.1]:
            X = eq["X_leader_monopolist"] * frac
            assert model._leader_value_at(X, K_L, phi_L, 0.0) < 0.0

    def test_preemption_trigger_unaffected_by_convention(self, model):
        """The floor never binds in the reported region: the equilibrium
        trigger still sits where L and F are both strictly positive."""
        eq = model.solve_preemption_equilibrium("H")
        X_P = eq["X_leader"]
        L = model._leader_value_at(X_P, eq["K_leader"], eq["phi_leader"], 0.0)
        F = model.follower_option_value(X_P, eq["K_leader"], eq["phi_leader"], "H")
        assert L > 0
        assert abs(L - F) < 1e-10


# ------------------------------------------------------------------
# Leader-scale convention: sensitivity and scale asymmetry
# ------------------------------------------------------------------


class TestLeaderScaleConvention:
    """Paper-pinned numbers for the leader-scale convention (Internet
    Appendix B) and the leader-follower scale asymmetry (@sec-duopoly)."""

    def test_reoptimized_leader_preemption_discount(self, default_params):
        """Re-optimizing (K_L, phi_L) for entry roughly doubles the
        preemption discount: 86% against the convention's 43%."""
        m = DuopolyModel(default_params, leverage=0.0)
        res = m.solve_preemption_reoptimized_leader(n_grid=24, x_low_factor=1e-2)

        assert res["single_crossing"]
        # Re-pinned in issue #177: the unlevered claims now carry the
        # shutdown option (0.427, 0.861, 0.000657 and 0.056 before).
        assert abs(res["preemption_discount_convention"] - 0.445) < 0.005
        assert abs(res["preemption_discount"] - 0.871) < 0.005
        assert abs(res["X_leader"] - 0.000611) < 5e-6
        # Leader shrinks to about 5% of the monopoly-phase capacity.
        assert abs(res["K_leader"] / res["K_leader_convention"] - 0.053) < 0.003
        # Role invariance survives re-optimization.
        assert abs(res["phi_leader"] - res["phi_leader_convention"]) < 1e-3
        # The convention understates, never overstates, the discount.
        assert res["preemption_discount"] > res["preemption_discount_convention"]

    def test_scale_asymmetry_ratios(self, model):
        """K_F/K_L ~ 38, X_F/X_P ~ 45 at baseline (X_F/X_P was 43.95
        before the unlevered leader had a shutdown option, issue #177)."""
        eq = model.solve_preemption_equilibrium("H")
        assert abs(eq["K_follower"] / eq["K_leader"] - 38.48) < 0.05
        assert abs(eq["X_follower"] / eq["X_leader"] - 45.33) < 0.05

    def test_elasticity_wedge_reproduces_follower_capacity(self, model):
        """The asymmetry is the elasticity wedge: substituting
        alpha*(2 - s_F) for alpha in the Proposition 1 closed form for K*
        reproduces K_F."""
        p = model.params
        eq = model.solve_preemption_equilibrium("H")
        K_L, K_F, beta = eq["K_leader"], eq["K_follower"], p.beta_H
        s_F = K_F**p.alpha / (K_F**p.alpha + K_L**p.alpha)
        alpha_eff = p.alpha * (2.0 - s_F)
        assert abs(s_F - 0.8115) < 5e-4
        assert abs(alpha_eff - 0.4754) < 5e-4

        def k_star(a):
            num = p.delta * (a * beta - beta + 1.0)
            den = p.r * p.c * (p.gamma * (beta - 1.0) - a * beta)
            return (num / den) ** (1.0 / (p.gamma - 1.0))

        assert abs(k_star(p.alpha) / K_L - 1.0) < 1e-6
        assert abs(k_star(alpha_eff) / K_F - 1.0) < 1e-6


# ------------------------------------------------------------------
# Anticipating leader's default boundary
# ------------------------------------------------------------------


class TestLeaderDefaultBoundary:
    """The levered leader's pre-entry claim satisfies the boundary conditions
    the paper attributes to it (Internet Appendix A, Proposition 3(i))."""

    @pytest.fixture(scope="class", params=[0.20, 0.40, 0.70])
    def levered_eq(self, request):
        model = DuopolyModel(
            ModelParameters(),
            leverage=request.param,
            coupon_rate=0.05,
            bankruptcy_cost=0.30,
        )
        eq = model.solve_preemption_equilibrium("H")
        return model, eq

    @staticmethod
    def _going_concern(model, eq, X):
        contrib = (1.0 - eq["lev_leader"]) * model.investment_cost(eq["K_leader"])
        return (
            model._leader_value_at(
                X, eq["K_leader"], eq["phi_leader"], eq["lev_leader"]
            )
            + contrib
        )

    def test_value_matching_and_smooth_pasting(self, levered_eq):
        model, eq = levered_eq
        X_D = eq["X_default_leader"]
        assert X_D > 0
        assert self._going_concern(model, eq, X_D) == pytest.approx(0.0, abs=1e-12)
        h = 1e-6 * X_D
        slope = (
            self._going_concern(model, eq, X_D + h)
            - self._going_concern(model, eq, X_D)
        ) / h
        scale = self._going_concern(model, eq, 2.0 * X_D) / X_D
        assert abs(slope) < 1e-4 * scale

    def test_nonnegative_above_boundary_increasing_on_search_interval(self, levered_eq):
        """E_L >= 0 on (X_D, X_F); increasing on the interval (X_D, X_L^mono]
        where the crossing is sought. Nearer X_F the convex dilution term
        eventually dominates and the pre-entry claim turns down, well
        above the equilibrium trigger."""
        model, eq = levered_eq
        X_D, X_F = eq["X_default_leader"], eq["X_follower"]
        X_mono = eq["X_leader_monopolist"]
        grid = np.geomspace(X_D * (1 + 1e-9), X_F * (1 - 1e-9), 60)
        vals = np.array([self._going_concern(model, eq, x) for x in grid])
        assert np.all(vals >= 0.0)
        search = np.geomspace(X_D * (1 + 1e-9), X_mono, 40)
        vals = np.array([self._going_concern(model, eq, x) for x in search])
        assert np.all(np.diff(vals) > 0.0)

    def test_boundary_above_monopoly_boundary(self, levered_eq):
        """Anticipated dilution lowers equity, so the anticipating leader
        defaults earlier than a monopolist with the same policy."""
        model, eq = levered_eq
        mono = model.default_boundary(
            eq["phi_leader"], eq["K_leader"], 0.0, 0.0, eq["lev_leader"]
        )
        assert eq["X_default_leader"] > mono
        assert eq["X_default_leader"] / mono - 1.0 < 0.15

    def test_small_jump_at_follower_entry(self, levered_eq):
        """The pre-entry claim is not matched to the post-entry claim at
        X_F; the residual jump is the difference between the two
        default-option terms there and is negligible relative to L(X_F)."""
        model, eq = levered_eq
        X_F = eq["X_follower"]
        left = model._leader_value_at(
            X_F * (1 - 1e-9), eq["K_leader"], eq["phi_leader"], eq["lev_leader"]
        )
        right = model._leader_value_at(
            X_F, eq["K_leader"], eq["phi_leader"], eq["lev_leader"]
        )
        assert abs(right - left) < 1e-4 * abs(right)

    def test_distance_to_default_pinned(self):
        """Proposition 3(v) numbers at ell = 0.40: X_P / X_D falls in lambda."""
        ratios = {}
        for lam in (0.05, 0.10, 0.20):
            m = DuopolyModel(
                ModelParameters(lam=lam),
                leverage=0.40,
                coupon_rate=0.05,
                bankruptcy_cost=0.30,
            )
            eq = m.solve_preemption_equilibrium("H")
            ratios[lam] = eq["X_leader"] / eq["X_default_leader"]
        assert ratios[0.05] == pytest.approx(2.63, abs=0.02)
        assert ratios[0.10] == pytest.approx(2.55, abs=0.02)
        assert ratios[0.20] == pytest.approx(2.44, abs=0.02)
        assert ratios[0.05] > ratios[0.10] > ratios[0.20]


# ------------------------------------------------------------------
# Default boundary in the training fraction (Proposition 2 prose)
# ------------------------------------------------------------------


class TestDefaultBoundaryInPhi:
    """X_D = MN / A_eff is U-shaped in phi at fixed (K, ell, lambda), with
    its minimum at the allocation optimum; against an asymmetric rival the
    own-phi maximizer of A_eff moves with the rival's allocation."""

    def test_monopoly_boundary_minimized_at_phi_star(self):
        model = DuopolyModel(
            ModelParameters(), leverage=0.40, coupon_rate=0.05, bankruptcy_cost=0.30
        )
        _, _, phi_star = SingleFirmModel(
            ModelParameters()
        ).pure_power_trigger_capacity_phi()
        grid = np.linspace(0.05, 0.95, 181)
        X_D = np.array([
            model.default_boundary(phi, 1.0, 0.0, 0.0, 0.40) for phi in grid
        ])
        assert grid[np.argmin(X_D)] == pytest.approx(phi_star, abs=0.006)
        assert model.default_boundary(0.90, 1.0, 0.0, 0.0, 0.40) > (
            model.default_boundary(phi_star, 1.0, 0.0, 0.0, 0.40)
        )
        assert model.default_boundary(0.50, 1.0, 0.0, 0.0, 0.40) > (
            model.default_boundary(phi_star, 1.0, 0.0, 0.0, 0.40)
        )

    def test_duopoly_own_phi_maximizer_moves_with_rival(self):
        model = DuopolyModel(ModelParameters())
        grid = np.linspace(0.05, 0.95, 901)

        def argmax(phi_j):
            vals = [model._effective_revenue_coeff(p, 1.0, phi_j, 1.0) for p in grid]
            return grid[int(np.argmax(vals))]

        assert argmax(0.10) == pytest.approx(0.843, abs=0.005)
        assert argmax(0.95) == pytest.approx(0.605, abs=0.005)
        _, _, phi_star = SingleFirmModel(
            ModelParameters()
        ).pure_power_trigger_capacity_phi()
        assert argmax(phi_star) == pytest.approx(phi_star, abs=0.002)


class TestContestShareProperties:
    """Section 3 prose on the Tullock share at alpha = 0.4."""

    def test_share_below_capacity_fraction_and_concave(self):
        model = DuopolyModel(ModelParameters())
        s4 = model.contest_share(4.0, 1.0)
        assert s4 == pytest.approx(0.6352, abs=1e-3)
        assert s4 < 0.8
        rev_share = 4.0**0.8 / (1.0 + 4.0**0.8)
        assert rev_share == pytest.approx(0.7519, abs=1e-3)
        assert s4 < rev_share < 0.8
        z = np.linspace(0.2, 8.0, 200)
        s = np.array([model.contest_share(zi, 1.0) for zi in z])
        assert np.all(np.diff(s) > 0)
        assert np.all(np.diff(s, 2) < 0)


class TestDebtBelowDefault:
    def test_debt_equals_recovery_at_and_below_boundary(self):
        model = DuopolyModel(
            ModelParameters(), leverage=0.40, coupon_rate=0.05, bankruptcy_cost=0.30
        )
        # At leverage 0.90 the coupon is large enough for the inference
        # business to be worth something net of its operating cost.
        phi, K, lev = 0.5, 1.0, 0.90
        X_D = model.default_boundary(phi, K, 0.0, 0.0, lev)
        at = model.debt_value(X_D, phi, K, 0.0, 0.0, lev)
        below = model.debt_value(0.5 * X_D, phi, K, 0.0, 0.0, lev)
        assert at > 0.0
        assert at == pytest.approx(model.recovery_value(phi, K, 0.0, 0.0, lev))
        assert below == pytest.approx(at, rel=1e-12)
        above = model.debt_value(1.5 * X_D, phi, K, 0.0, 0.0, lev)
        assert above > at

    def test_zero_recovery_debt_is_worthless_at_the_boundary(self):
        """At leverage 0.40 the netted inference business is under water
        at X_D, so creditors recover nothing and debt is worth zero at
        and below the boundary."""
        model = DuopolyModel(
            ModelParameters(), leverage=0.40, coupon_rate=0.05, bankruptcy_cost=0.30
        )
        phi, K = 0.5, 1.0
        X_D = model.default_boundary(phi, K, 0.0, 0.0)
        assert model.recovery_value(phi, K, 0.0, 0.0) == 0.0
        assert model.debt_value(X_D, phi, K, 0.0, 0.0) == 0.0
        assert model.debt_value(0.5 * X_D, phi, K, 0.0, 0.0) == 0.0
        assert model.debt_value(1.5 * X_D, phi, K, 0.0, 0.0) > 0.0


class TestSingleCrossingEnforced:
    def test_strict_mode_raises_on_multiple_sign_changes(self, model, monkeypatch):
        """A gap with two sign changes on the grid is not reported as an
        equilibrium in strict mode."""
        X_mono, _, _, _ = model.solve_leader_monopolist("H")
        # The search interval starts at the leader's shutdown boundary.
        X_low = model.solve_preemption_equilibrium("H")["X_default_leader"]

        def wiggly_gap(X, regime="H"):
            # negative, then positive, then negative, then positive
            return np.sin(3.0 * np.pi * (X - X_low) / (X_mono - X_low)) - 0.2

        monkeypatch.setattr(model, "_preemption_gap", wiggly_gap)
        model._cache = {
            k: v for k, v in model._cache.items() if k[0] != "preemption_3d"
        }
        with pytest.raises(RuntimeError, match="changes sign"):
            model.solve_preemption_equilibrium("H", strict=True)
        eq = model.solve_preemption_equilibrium("H", strict=False)
        assert eq["single_crossing"] is False


# ------------------------------------------------------------------
# Credit primitives (issue #177): shutdown, recovery, fair coupon
# ------------------------------------------------------------------

# Single-firm policies (X, K, phi) the credit primitives are reported at:
# the precommitted-scale policy of the model of record and the pure-power
# approximation the duopoly and credit blocks are still pinned to.
RECORD_POLICY = (0.009258307, 0.015783642, 0.700855718)
PURE_POWER_POLICY = (0.004721756, 0.006726639, 0.700855709)


def credit_model(leverage=0.0, recovery_rule="net"):
    return DuopolyModel(
        ModelParameters(),
        leverage=leverage,
        coupon_rate=0.05,
        bankruptcy_cost=0.30,
        recovery_rule=recovery_rule,
    )


class TestUnleveredFirm:
    """Every zero-leverage special case in one place (issue #177, C21).

    The unlevered firm is the zero-coupon case of the levered formulas:
    it has a shutdown boundary, its claims carry the shutdown option, and
    X_D, equity and the default probability are continuous as leverage
    goes to zero. Before #177 these were early returns (X_D = 0, no
    option, zero probability) tested in five different classes.
    """

    def test_shutdown_boundary_is_zero_coupon_default_boundary(self, model):
        p = model.params
        phi, K = 0.3, 1.0
        X_A = model.default_boundary(phi, K, phi, K)
        a_eff = model._effective_revenue_coeff(phi, K, phi, K)
        beta_neg = model._negative_root("L", p.lam)
        expected = beta_neg / (beta_neg - 1.0) * (p.delta * K / p.r) / a_eff
        assert pytest.approx(expected, rel=1e-12) == X_A
        assert model.shutdown_boundary(phi, K, phi, K) == X_A
        # An explicit zero coupon gives the same boundary at any leverage.
        assert model.default_boundary(phi, K, phi, K, 0.5, coupon=0.0) == X_A

    def test_equity_is_value_minus_cost_plus_shutdown_option(self, model):
        p = model.params
        X, phi, K = 5.0, 0.3, 1.0
        E = model.equity_value(X, phi, K, 0.0, 0.0, leverage=0.0)
        V = model.monopolist_value_L(X, phi, K)
        cost = model.investment_cost(K)
        X_A = model.shutdown_boundary(phi, K)
        beta_neg = model._negative_root("L", p.lam)
        option = -model.monopolist_value_L(X_A, phi, K) * (X / X_A) ** beta_neg
        assert option > 0
        assert pytest.approx(V - cost + option, rel=1e-12) == E
        assert model.unlevered_asset_value(X, phi, K) == pytest.approx(E + cost)
        # Far above the boundary the option is a small part of the value.
        assert option / V < 1e-6

    def test_entry_npv_is_minus_cost_at_and_below_shutdown(self, model):
        """The L(0) < 0 endpoint of the Proposition 3 existence argument:
        the firm that has stopped operating has lost I(K), not
        delta K / r + I(K) as before the shutdown option."""
        phi, K = 0.70, 0.0067
        X_A = model.shutdown_boundary(phi, K)
        for X in [0.0, 1e-12, 0.5 * X_A, X_A]:
            npv = model.equity_value(X, phi, K, 0.0, 0.0, leverage=0.0)
            assert npv == pytest.approx(-model.investment_cost(K), rel=1e-12)
        assert model.unlevered_asset_value(X_A, phi, K) == 0.0

    def test_smooth_pasting_at_shutdown(self, model):
        phi, K = 0.70, 0.0067
        X_A = model.shutdown_boundary(phi, K)
        h = 1e-5
        U = [model.unlevered_asset_value(X_A * (1 + k * h), phi, K) for k in (1, 2)]
        # U(X_A) = U'(X_A) = 0, so U is second order in the distance.
        assert U[1] / U[0] == pytest.approx(4.0, rel=1e-3)

    def test_coupled_boundary_positive_and_below_single(self, model):
        X_D = model.default_boundary(0.7, 1.0, 0.7, 1.0)
        X_D_c = model.default_boundary_coupled(0.7, 1.0, 0.7, 1.0)
        assert 0.0 < X_D_c <= X_D
        assert (X_D - X_D_c) / X_D_c < 0.05

    def test_equilibrium_reports_shutdown_boundaries(self, model):
        eq = model.solve_preemption_equilibrium("H")
        assert 0.0 < eq["X_default_leader"] < eq["X_leader"]
        assert 0.0 < eq["X_default_follower"] < eq["X_follower"]
        assert eq["X_default_leader"] == pytest.approx(0.0009483, rel=1e-3)
        assert eq["X_leader"] / eq["X_default_leader"] == pytest.approx(2.764, abs=5e-3)
        # The anticipating leader's boundary lies above the monopoly one.
        X_A = model.shutdown_boundary(eq["phi_leader"], eq["K_leader"])
        assert eq["X_default_leader"] > X_A

    def test_unlevered_preemption_trigger_pinned(self, model):
        """X_P = 0.002621 (0.002703 before the shutdown option): a
        discount of 44.5% from the pure-power monopoly trigger."""
        eq = model.solve_preemption_equilibrium("H")
        assert eq["X_leader"] == pytest.approx(0.002621, rel=1e-3)
        discount = 1.0 - eq["X_leader"] / eq["X_leader_monopolist"]
        assert discount == pytest.approx(0.4449, abs=5e-4)

    @pytest.mark.parametrize("policy", [RECORD_POLICY, PURE_POWER_POLICY])
    def test_continuity_as_leverage_goes_to_zero(self, policy):
        """X_D, the going-concern equity claim and the default
        probability at leverage 1e-6 agree with their zero-leverage
        values to first order in leverage."""
        from ai_lab_investment.models.valuation import ValuationAnalysis

        X, K, phi = policy
        va = ValuationAnalysis(ModelParameters())
        base, I_K = credit_model(0.0), credit_model().investment_cost(K)
        X_D0 = base.default_boundary(phi, K, 0.0, 0.0)
        E0 = base.equity_value(X, phi, K, 0.0, 0.0) + I_K
        pd0 = va.default_probability(X, K, 0.0, phi)
        assert X_D0 > 0 and pd0 > 0
        gaps = []
        for lev in (1e-3, 1e-6):
            m = credit_model(lev)
            X_D = m.default_boundary(phi, K, 0.0, 0.0)
            # Total claim of the equity holders, contribution added back.
            E = m.equity_value(X, phi, K, 0.0, 0.0) + (1.0 - lev) * I_K
            pd = va.default_probability(X, K, lev, phi)
            assert X_D > X_D0 and pd > pd0
            gaps.append((X_D / X_D0 - 1.0, 1.0 - E / E0, pd / pd0 - 1.0))
        for small, tiny in zip(*gaps, strict=True):
            assert 0.0 < tiny < 1e-5
            assert small / tiny == pytest.approx(1e3, rel=0.02)

    def test_no_debt_claims_without_leverage(self, model):
        phi, K = 0.3, 1.0
        assert model.coupon_payment(K) == 0.0
        assert model.debt_value(2.0, phi, K, 0.0, 0.0) == 0.0
        assert model.recovery_value(phi, K, 0.0, 0.0) == 0.0
        assert np.isnan(model.recovery_rate(phi, K, 0.0, 0.0))
        assert model.fair_coupon(2.0, phi, K) == 0.0

    def test_spread_and_default_probability_at_zero_leverage(self):
        """The spread at zero leverage is the limit on an infinitesimal
        issue; it is positive because the unlevered firm also stops
        operating. Pinned at the figure's evaluation point."""
        from ai_lab_investment.models.valuation import ValuationAnalysis

        va = ValuationAnalysis(ModelParameters())
        assert va.credit_spread(leverage=0.0) * 1e4 == pytest.approx(22.86, abs=0.05)
        assert va.credit_spread(leverage=1e-4) * 1e4 == pytest.approx(22.86, abs=0.05)
        pd = va.default_probability(X_current=0.10, K=1.0, leverage=0.0)
        assert pd * 100 == pytest.approx(0.404, abs=0.005)
        # Far from the boundary the probability is negligible, not zero.
        assert 0.0 < va.default_probability(1.0, 1.0, 0.0) < 1e-9
        # Under the pre-#177 gross rule the limit is default-free debt.
        gross = ValuationAnalysis(ModelParameters(), recovery_rule="gross")
        assert gross.credit_spread(leverage=0.0) == 0.0


class TestRecoveryRule:
    """Recovery net of operating costs (issue #177, C22)."""

    def test_unknown_rule_raises(self):
        with pytest.raises(ValueError, match="recovery rule"):
            DuopolyModel(ModelParameters(), recovery_rule="book")

    def test_installed_value_is_inference_plus_training_business(self):
        """Under "net" the inference business bears the same perpetual
        operating cost as the firm, so V = Lambda_net + training
        business exactly."""
        m = credit_model()
        p = m.params
        X, phi, K = 0.02, 0.6, 0.5
        training = (
            p.lam / (p.r - p.mu_L + p.lam) * p.A_H * (phi * K) ** p.alpha * X
            - p.delta * phi * K / p.r
        )
        assert m.liquidation_value(X, phi, K, 0.0, 0.0) + training == pytest.approx(
            m.monopolist_value_L(X, phi, K), rel=1e-12
        )

    def test_rules_differ_by_the_operating_cost(self):
        p = ModelParameters()
        X, phi, K = 0.02, 0.6, 0.5
        gross = credit_model(recovery_rule="gross").liquidation_value(X, phi, K, 0, 0)
        net = credit_model().liquidation_value(X, phi, K, 0, 0)
        until = credit_model(recovery_rule="net_until_switch").liquidation_value(
            X, phi, K, 0, 0
        )
        cost = p.delta * (1.0 - phi) * K
        assert gross - net == pytest.approx(cost / p.r, rel=1e-12)
        assert gross - until == pytest.approx(cost / (p.r + p.lam), rel=1e-12)

    @pytest.mark.parametrize("rule", ["net", "net_until_switch"])
    def test_recovery_never_exceeds_unlevered_asset_value(self, rule):
        """Creditors cannot recover more than the assets they seize are
        worth to an unlevered owner, nor more than the default-free
        claim, at any allocation, leverage or rival."""
        binding = 0
        for lev in (0.01, 0.05, 0.20, 0.40, 0.70, 0.95):
            m = credit_model(lev, rule)
            for phi in (0.02, 0.2, 0.5, 0.7, 0.9, 0.98):
                for K, K_j in ((0.0067, 0.0), (1.0, 0.0), (1.0, 1.0), (0.2, 3.0)):
                    X_D = m.default_boundary(phi, K, 0.5, K_j)
                    U = m.unlevered_asset_value(X_D, phi, K, 0.5, K_j)
                    rec = m.recovery_value(phi, K, 0.5, K_j)
                    assert 0.0 <= rec <= (1.0 - m.bankruptcy_cost) * U + 1e-15
                    assert rec <= m.coupon_payment(K) / m.params.r + 1e-15
                    liq = m.liquidation_value(X_D, phi, K, 0.5, K_j)
                    binding += liq > U
        # The cap at the unlevered asset value is not vacuous.
        assert binding > 0

    def test_gross_rule_reproduces_the_binding_cap(self):
        """C22 as stated by the reviewer: under the pre-#177 gross rule
        (1 - b) Lambda(X_D) is 2.8 times the coupon claim at ell = 0.40
        and still above it at 0.95, at the pure-power (X*, K*, phi*), so
        debt is default-free at every leverage."""
        X, K, phi = PURE_POWER_POLICY
        for lev, multiple in ((0.40, 2.83), (0.95, 1.28)):
            m = credit_model(lev, "gross")
            X_D = m.default_boundary(phi, K, 0.0, 0.0)
            claim = m.coupon_payment(K) / m.params.r
            liq = m.liquidation_value(X_D, phi, K, 0.0, 0.0)
            assert 0.7 * liq / claim == pytest.approx(multiple, abs=0.01)
            assert m.recovery_rate(phi, K, 0.0, 0.0) == 1.0
            assert m.debt_value(X, phi, K, 0.0, 0.0) == pytest.approx(claim, rel=1e-12)

    def test_gross_cap_stops_binding_at_the_model_of_record(self):
        """At the model-of-record policy the gross cap binds up to
        ell = 0.70 but not at 0.95 (the reviewer's 'every leverage up to
        0.95' is a statement about the pure-power policy)."""
        _, K, phi = RECORD_POLICY
        assert credit_model(0.70, "gross").recovery_rate(phi, K, 0.0, 0.0) == 1.0
        rate = credit_model(0.95, "gross").recovery_rate(phi, K, 0.0, 0.0)
        assert rate == pytest.approx(0.884, abs=2e-3)

    @pytest.mark.parametrize("policy", [RECORD_POLICY, PURE_POWER_POLICY])
    def test_netted_recovery_is_zero_at_the_firms_own_policy(self, policy):
        """At phi* the inference business is under water at X_D at every
        leverage: creditors recover nothing and debt is risky."""
        X, K, phi = policy
        for lev in (0.01, 0.05, 0.20, 0.40, 0.70):
            m = credit_model(lev)
            assert m.recovery_value(phi, K, 0.0, 0.0) == 0.0
            claim = m.coupon_payment(K) / m.params.r
            assert m.debt_value(X, phi, K, 0.0, 0.0) < claim

    def test_until_switch_rule_is_capped_by_unlevered_asset_value(self):
        """Netting the cost only until the switch leaves the inference
        business worth more than the whole firm at X_D, so the cap at
        the unlevered asset value binds and recovery is second order in
        leverage (6.1% of the claim at ell = 0.40, model of record)."""
        _, K, phi = RECORD_POLICY
        m = credit_model(0.40, "net_until_switch")
        X_D = m.default_boundary(phi, K, 0.0, 0.0)
        U = m.unlevered_asset_value(X_D, phi, K)
        assert m.liquidation_value(X_D, phi, K, 0.0, 0.0) > U
        assert m.recovery_value(phi, K, 0.0, 0.0) == pytest.approx(0.7 * U)
        assert m.recovery_rate(phi, K, 0.0, 0.0) == pytest.approx(0.0610, abs=5e-4)


class TestFairCoupon:
    """Fairly priced debt: D = ell I(K) at issuance (issue #177, C15)."""

    @pytest.mark.parametrize("rule", ["net", "net_until_switch", "gross"])
    @pytest.mark.parametrize("policy", [RECORD_POLICY, PURE_POWER_POLICY])
    def test_fair_coupon_debt_prices_at_par(self, policy, rule):
        X, K, phi = policy
        for lev in (0.01, 0.05, 0.20, 0.40, 0.70):
            m = credit_model(lev, rule)
            coupon = m.fair_coupon(X, phi, K)
            proceeds = lev * m.investment_cost(K)
            D = m.debt_value(X, phi, K, 0.0, 0.0, coupon=coupon)
            assert pytest.approx(proceeds, rel=1e-9) == D
            # A fair coupon is at least the default-free coupon r ell I.
            assert coupon >= m.params.r * proceeds * (1.0 - 1e-12)

    def test_par_convention_debt_is_worth_less_than_proceeds(self):
        """The financing subsidy of the par convention at r_c = 5%:
        debt is worth 40.7% of its proceeds at ell = 0.40 (41.7%, the
        ratio r_c / r, if it were default-free), a transfer of 23.7% of
        I(K)."""
        X, K, phi = PURE_POWER_POLICY
        m = credit_model(0.40)
        proceeds = 0.40 * m.investment_cost(K)
        D = m.debt_value(X, phi, K, 0.0, 0.0)
        assert D / proceeds == pytest.approx(0.4072, abs=5e-4)
        assert (proceeds - D) / m.investment_cost(K) == pytest.approx(0.237, abs=1e-3)
        assert m.fair_coupon(X, phi, K) / m.coupon_payment(K) == pytest.approx(
            2.467, abs=5e-3
        )

    def test_fair_coupon_raises_the_default_boundary(self):
        X, K, phi = RECORD_POLICY
        m = credit_model(0.40)
        par = m.default_boundary(phi, K, 0.0, 0.0)
        fair = m.default_boundary(phi, K, 0.0, 0.0, coupon=m.fair_coupon(X, phi, K))
        assert par == pytest.approx(0.001602, rel=1e-3)
        assert fair == pytest.approx(0.001782, rel=1e-3)

    def test_fair_coupon_increasing_in_leverage(self):
        X, K, phi = RECORD_POLICY
        rates = []
        for lev in np.linspace(0.05, 0.95, 10):
            m = credit_model(lev)
            rates.append(m.fair_coupon(X, phi, K) / (lev * m.investment_cost(K)))
        assert np.all(np.diff(rates) > 0)
        assert rates[0] > m.params.r

    def test_duopoly_fair_coupon(self):
        m = credit_model(0.40)
        X, phi, K = 0.5, 0.6, 1.0
        coupon = m.fair_coupon(X, phi, K, 0.6, 1.0)
        D = m.debt_value(X, phi, K, 0.6, 1.0, coupon=coupon)
        assert pytest.approx(0.40 * m.investment_cost(K), rel=1e-9) == D

    def test_proceeds_above_debt_capacity_raise(self):
        """At the off-policy evaluation point of fig-credit-risk no
        coupon raises 70% of I(K): debt capacity is exhausted."""
        m = credit_model(0.70)
        with pytest.raises(ValueError, match="debt capacity"):
            m.fair_coupon(0.10, 0.5, 1.0)

    def test_explicit_coupon_enters_every_claim(self):
        m = credit_model(0.40)
        X, phi, K = 0.5, 0.6, 1.0
        par = m.coupon_payment(K)
        assert m.equity_value(X, phi, K, 0.0, 0.0, coupon=par) == m.equity_value(
            X, phi, K, 0.0, 0.0
        )
        high = 2.0 * par
        assert m.default_boundary(phi, K, 0.0, 0.0, coupon=high) > m.default_boundary(
            phi, K, 0.0, 0.0
        )
        assert m.equity_value(X, phi, K, 0.0, 0.0, coupon=high) < m.equity_value(
            X, phi, K, 0.0, 0.0
        )
        assert m.firm_value(X, phi, K, 0.0, 0.0, coupon=high) == pytest.approx(
            m.equity_value(X, phi, K, 0.0, 0.0, coupon=high)
            + m.debt_value(X, phi, K, 0.0, 0.0, coupon=high)
        )
        with pytest.raises(ValueError, match="non-negative"):
            m.debt_value(X, phi, K, 0.0, 0.0, coupon=-1.0)
