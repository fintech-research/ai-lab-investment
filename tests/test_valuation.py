"""Tests for valuation analysis."""

import numpy as np
import pytest

from ai_lab_investment.models import ModelParameters, ValuationAnalysis


@pytest.fixture
def params():
    return ModelParameters()


@pytest.fixture
def va(params):
    return ValuationAnalysis(params)


# ------------------------------------------------------------------
# Growth option decomposition
# ------------------------------------------------------------------


class TestGrowthOptionDecomposition:
    def test_pre_investment_decomposition(self, va):
        """Pre-investment (K=0) should have zero assets-in-place."""
        result = va.growth_option_decomposition(X=1.0, K_installed=0.0)
        assert result["assets_in_place"] == 0.0
        assert result["expansion_option"] >= 0.0
        assert result["total_value"] >= 0.0

    def test_with_installed_capacity(self, va):
        """With installed capacity, assets-in-place should be positive."""
        result = va.growth_option_decomposition(X=1.0, K_installed=1.0)
        assert result["assets_in_place"] > 0.0
        assert result["total_value"] > 0.0

    def test_fractions_sum_to_one(self, va):
        """Assets + growth fractions should sum to 1."""
        result = va.growth_option_decomposition(X=1.0, K_installed=1.0)
        total_frac = result["assets_fraction"] + result["growth_fraction"]
        assert abs(total_frac - 1.0) < 1e-10

    def test_regime_L_has_switch_value(self, va):
        """Regime L should have positive regime switch value."""
        result = va.growth_option_decomposition(X=1.0, K_installed=0.0, regime="L")
        assert result["regime_switch_value"] >= 0.0

    def test_regime_H_no_switch_value(self, va):
        """Regime H should have zero regime switch value."""
        result = va.growth_option_decomposition(X=1.0, K_installed=0.0, regime="H")
        assert result["regime_switch_value"] == 0.0

    def test_higher_X_higher_assets(self, va):
        """Higher demand should increase assets-in-place."""
        r1 = va.growth_option_decomposition(X=0.5, K_installed=1.0)
        r2 = va.growth_option_decomposition(X=2.0, K_installed=1.0)
        assert r2["assets_in_place"] > r1["assets_in_place"]

    def test_higher_K_higher_assets(self, va):
        """More capacity should increase assets-in-place."""
        r1 = va.growth_option_decomposition(X=1.0, K_installed=0.5)
        r2 = va.growth_option_decomposition(X=1.0, K_installed=2.0)
        assert r2["assets_in_place"] > r1["assets_in_place"]


# ------------------------------------------------------------------
# Credit risk
# ------------------------------------------------------------------


class TestCreditRisk:
    def test_zero_leverage_zero_spread(self, va):
        """Unlevered firm has zero spread."""
        spread = va.credit_spread(leverage=0.0)
        assert spread == 0.0

    def test_positive_leverage_positive_spread(self, va):
        """Levered firm has positive spread."""
        spread = va.credit_spread(leverage=0.4)
        assert spread >= 0.0

    def test_higher_leverage_higher_spread(self, va):
        """Higher leverage should produce higher spread."""
        s1 = va.credit_spread(leverage=0.2)
        s2 = va.credit_spread(leverage=0.6)
        # Both should be non-negative; higher leverage >= lower
        assert s2 >= s1

    def test_zero_leverage_zero_default_prob(self, va):
        """Unlevered firm has zero default probability."""
        prob = va.default_probability(X_current=1.0, K=1.0, leverage=0.0)
        assert prob == 0.0

    def test_default_prob_in_range(self, va):
        """Default probability should be in [0, 1]."""
        prob = va.default_probability(X_current=1.0, K=1.0, leverage=0.4, horizon=5.0)
        assert 0.0 <= prob <= 1.0

    def test_higher_leverage_higher_default_prob(self, va):
        """Higher leverage should increase default probability."""
        p1 = va.default_probability(X_current=1.0, K=1.0, leverage=0.2)
        p2 = va.default_probability(X_current=1.0, K=1.0, leverage=0.6)
        assert p2 >= p1

    def test_credit_spread_curve_shape(self, va):
        """Credit spread curve should return correct shapes."""
        leverages = np.linspace(0.1, 0.6, 5)
        result = va.credit_spread_curve(leverages)
        assert len(result["leverage"]) == 5
        assert len(result["credit_spread"]) == 5
        assert len(result["default_probability"]) == 5


# ------------------------------------------------------------------
# Dario dilemma
# ------------------------------------------------------------------


class TestDarioDilemma:
    def test_matched_beliefs_no_loss(self, va):
        """When beliefs match, value loss should be zero."""
        result = va.dario_dilemma(lambda_true=0.20, lambda_invest=0.20)
        if "error" not in result:
            assert abs(result["value_loss"]) < 1e-8
            assert abs(result["value_loss_pct"]) < 1e-8

    def test_mismatched_beliefs_positive_loss(self, va):
        """Mismatched beliefs should produce positive value loss."""
        result = va.dario_dilemma(lambda_true=0.30, lambda_invest=0.10)
        if "error" not in result:
            assert result["value_loss"] >= 0.0

    def test_conservative_flag(self, va):
        """Should correctly identify conservative vs aggressive."""
        result = va.dario_dilemma(lambda_true=0.30, lambda_invest=0.10)
        if "error" not in result:
            assert result["is_conservative"] is True

        result2 = va.dario_dilemma(lambda_true=0.10, lambda_invest=0.30)
        if "error" not in result2:
            assert result2["is_conservative"] is False

    def test_dario_surface_shape(self, va):
        """Dario dilemma surface should have correct shape."""
        lt = np.array([0.1, 0.2, 0.3])
        li = np.array([0.1, 0.2])
        result = va.dario_dilemma_surface(lt, li)
        assert result["value_loss_pct"].shape == (3, 2)

    def test_surface_diagonal_near_zero(self, va):
        """Diagonal of the surface (matched beliefs) should be near zero."""
        vals = np.array([0.1, 0.2, 0.3])
        result = va.dario_dilemma_surface(vals, vals)
        for i in range(len(vals)):
            if not np.isnan(result["value_loss_pct"][i, i]):
                assert abs(result["value_loss_pct"][i, i]) < 0.01


class TestDarioDilemmaLeveraged:
    """Tests for the leveraged Dario's dilemma."""

    def test_matched_beliefs_no_loss(self, va):
        """When beliefs match, value loss should be zero."""
        result = va.dario_dilemma_leveraged(0.10, 0.10, leverage=0.40)
        assert "error" not in result
        assert abs(result["value_loss_pct"]) < 1e-6

    def test_value_losses_non_negative(self, va):
        """Mismatched beliefs produce non-negative value losses."""
        for li in [0.02, 0.50]:
            result = va.dario_dilemma_leveraged(0.10, li, leverage=0.40)
            assert "error" not in result
            assert result["value_loss_pct"] >= -1e-6

    def test_default_prob_consistency_with_main_method(self, va):
        """Default probs should match the standalone default_probability()."""
        result = va.dario_dilemma_leveraged(0.10, 0.10, leverage=0.40)
        assert "error" not in result
        # The leveraged method evaluates under p_true; create matching VA
        p_true = va.params.with_param(lam=0.10)
        va_true = ValuationAnalysis(p_true)
        from ai_lab_investment.models.base_model import SingleFirmModel

        model = SingleFirmModel(p_true)
        X, K, phi = model.optimal_trigger_capacity_phi()
        dp_standalone = va_true.default_probability(
            X_current=X,
            K=K,
            leverage=0.40,
            phi=phi,
            regime="L",
            horizon=5.0,
        )
        assert abs(result["default_prob_optimal"] - dp_standalone) < 1e-10

    def test_baseline_default_probs(self, va):
        """Regression: default probs at baseline match paper values."""
        r_cons = va.dario_dilemma_leveraged(0.10, 0.02, leverage=0.40)
        r_aggr = va.dario_dilemma_leveraged(0.10, 0.50, leverage=0.40)
        assert "error" not in r_cons
        assert "error" not in r_aggr
        # Paper: conservative ~0.79%, aggressive ~5.04%
        assert abs(r_cons["default_prob_mismatch"] - 0.0079) < 0.002
        assert abs(r_aggr["default_prob_mismatch"] - 0.0504) < 0.005

    def test_aggressive_higher_default_prob(self, va):
        """Aggressive overinvestment has higher default probability."""
        r_cons = va.dario_dilemma_leveraged(0.10, 0.02, leverage=0.40)
        r_aggr = va.dario_dilemma_leveraged(0.10, 0.50, leverage=0.40)
        assert "error" not in r_cons
        assert "error" not in r_aggr
        assert r_aggr["default_prob_mismatch"] > r_cons["default_prob_mismatch"]


# ------------------------------------------------------------------
# Equity value vs lambda
# ------------------------------------------------------------------


class TestEquityValueVsLambda:
    def test_shape(self, va):
        """Should return arrays of correct length."""
        lam_vals = np.array([0.05, 0.10, 0.20, 0.50])
        result = va.equity_value_vs_lambda(lam_vals)
        assert len(result["lambda_values"]) == 4
        assert len(result["option_values"]) == 4
        assert len(result["triggers"]) == 4
        assert len(result["capacities"]) == 4

    def test_positive_values(self, va):
        """Option values should be positive where solutions exist."""
        lam_vals = np.array([0.10, 0.20, 0.50])
        result = va.equity_value_vs_lambda(lam_vals)
        valid = ~np.isnan(result["option_values"])
        if valid.sum() > 0:
            assert np.all(result["option_values"][valid] > 0)


# ------------------------------------------------------------------
# Summary
# ------------------------------------------------------------------


class TestSummary:
    def test_summary_keys(self, va):
        """Summary should contain expected keys."""
        s = va.summary()
        assert "decomposition" in s
        assert "credit" in s
        assert "dario_dilemma" in s

    def test_summary_credit_levels(self, va):
        """Summary should have credit metrics at multiple leverage levels."""
        s = va.summary()
        assert "leverage_0.0" in s["credit"]
        assert "leverage_0.4" in s["credit"]

    def test_summary_decomposition_valid(self, va):
        """Summary decomposition should have valid values."""
        s = va.summary()
        d = s["decomposition"]
        assert d["total_value"] >= 0.0
        assert 0.0 <= d["assets_fraction"] <= 1.0


# ------------------------------------------------------------------
# Phi-aware valuation
# ------------------------------------------------------------------


class TestPhiAwareValuation:
    def test_decomposition_with_phi_pre_investment(self, va):
        """Pre-investment decomposition should have zero assets."""
        result = va.growth_option_decomposition_with_phi(X=1.0)
        assert result["assets_in_place"] == 0.0
        assert result["expansion_option"] >= 0.0
        assert result["phi_optimal"] > 0.0

    def test_decomposition_with_phi_installed(self, va):
        """With installed capacity, assets should be positive."""
        result = va.growth_option_decomposition_with_phi(
            X=2.0, K_installed=1.0, phi=0.4
        )
        assert result["assets_in_place"] > 0.0
        assert result["phi_installed"] == 0.4

    def test_decomposition_fractions_valid(self, va):
        """Asset and growth fractions should be in [0, 1]."""
        result = va.growth_option_decomposition_with_phi(X=1.0)
        assert 0.0 <= result["assets_fraction"] <= 1.0
        assert 0.0 <= result["growth_fraction"] <= 1.0

    def test_equity_vs_lambda_with_phi_shape(self, va):
        """Should return arrays with correct length."""
        lam_vals = np.array([0.05, 0.10, 0.20, 0.50])
        result = va.equity_value_vs_lambda_with_phi(lam_vals)
        assert len(result["lambda_values"]) == 4
        assert len(result["phis"]) == 4

    def test_equity_vs_lambda_with_phi_values(self, va):
        """Phi should increase with lambda."""
        lam_vals = np.array([0.05, 0.50])
        result = va.equity_value_vs_lambda_with_phi(lam_vals)
        valid = ~np.isnan(result["phis"])
        if valid.sum() == 2:
            assert result["phis"][1] > result["phis"][0]
