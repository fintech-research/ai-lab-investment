"""Tests for valuation analysis."""

import itertools

import numpy as np
import pytest

from ai_lab_investment.models import ModelParameters, SingleFirmModel, ValuationAnalysis


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
        """Levered firm has strictly positive spread once the coupon claim
        outgrows the inference collateral (baseline: above ell ~ 0.13)."""
        spread = va.credit_spread(leverage=0.4)
        assert spread > 0.0

    def test_higher_leverage_higher_spread(self, va):
        """Higher leverage should produce strictly higher spread."""
        s1 = va.credit_spread(leverage=0.2)
        s2 = va.credit_spread(leverage=0.6)
        assert s2 > s1 > 0.0

    def test_zero_leverage_zero_default_prob(self, va):
        """Unlevered firm has zero default probability."""
        prob = va.default_probability(X_current=1.0, K=1.0, leverage=0.0)
        assert prob == 0.0

    def test_default_prob_in_range(self, va):
        """Default probability should be in [0, 1]."""
        prob = va.default_probability(X_current=1.0, K=1.0, leverage=0.4, horizon=5.0)
        assert 0.0 <= prob <= 1.0

    def test_higher_leverage_higher_default_prob(self, va):
        """Higher leverage should strictly increase default probability."""
        p1 = va.default_probability(X_current=0.10, K=1.0, leverage=0.2)
        p2 = va.default_probability(X_current=0.10, K=1.0, leverage=0.6)
        assert p2 > p1 > 0.0

    def test_credit_spread_curve_shape(self, va):
        """Credit spread curve should return correct shapes."""
        leverages = np.linspace(0.1, 0.6, 5)
        result = va.credit_spread_curve(leverages)
        assert len(result["leverage"]) == 5
        assert len(result["credit_spread"]) == 5
        assert len(result["default_probability"]) == 5

    def test_high_leverage_strictly_positive_spread(self, va):
        """Once the coupon claim outgrows the inference liquidation value,
        the spread must be strictly positive."""
        assert va.credit_spread(leverage=0.7) > 0.0

    def test_first_passage_probability_against_monte_carlo(self, va):
        """Verify the closed-form barrier-hitting probability by simulation.

        Simulates GBM paths under the L-regime drift with a Brownian-bridge
        crossing correction (so the discrete grid does not understate
        barrier hits) and compares the hit frequency to the formula.
        """
        from ai_lab_investment.models.duopoly import DuopolyModel

        leverage, K, phi, horizon = 0.4, 1.0, 0.5, 5.0
        X0 = va.CREDIT_RISK_DEMAND_LEVEL
        p = va.params

        duo = DuopolyModel(p, leverage=leverage, coupon_rate=0.05, bankruptcy_cost=0.30)
        X_D = duo.default_boundary(phi, K, 0.0, 0.0)
        p_formula = va.default_probability(
            X_current=X0,
            K=K,
            leverage=leverage,
            phi=phi,
            regime="L",
            horizon=horizon,
        )

        rng = np.random.default_rng(12345)
        n_paths, n_steps = 20_000, 500
        dt = horizon / n_steps
        nu = p.mu_L - 0.5 * p.sigma**2
        log_b = np.log(X_D)

        log_x = np.full(n_paths, np.log(X0))
        hit = np.zeros(n_paths, dtype=bool)
        for _ in range(n_steps):
            log_x_new = (
                log_x + nu * dt + p.sigma * np.sqrt(dt) * rng.standard_normal(n_paths)
            )
            hit |= log_x_new <= log_b
            # Brownian-bridge probability of crossing within the step
            alive = ~hit
            if alive.any():
                d1 = log_x[alive] - log_b
                d2 = log_x_new[alive] - log_b
                p_bridge = np.exp(-2.0 * d1 * d2 / (p.sigma**2 * dt))
                hit[np.flatnonzero(alive)[rng.random(alive.sum()) < p_bridge]] = True
            log_x = log_x_new

        p_mc = hit.mean()
        # MC standard error ~0.0015; allow 4 standard errors
        assert abs(p_mc - p_formula) < 0.006


# ------------------------------------------------------------------
# Dario dilemma
# ------------------------------------------------------------------


class TestDarioDilemma:
    def test_matched_beliefs_no_loss(self, va):
        """When beliefs match, value loss should be zero."""
        result = va.dario_dilemma(lambda_true=0.20, lambda_invest=0.20)
        assert "error" not in result
        assert abs(result["value_loss"]) < 1e-8
        assert abs(result["value_loss_pct"]) < 1e-8

    def test_mismatched_beliefs_positive_loss(self, va):
        """Mismatched beliefs should produce positive value loss."""
        result = va.dario_dilemma(lambda_true=0.30, lambda_invest=0.10)
        assert "error" not in result
        assert result["value_loss"] >= 0.0

    def test_conservative_flag(self, va):
        """Should correctly identify conservative vs aggressive."""
        result = va.dario_dilemma(lambda_true=0.30, lambda_invest=0.10)
        assert "error" not in result
        assert result["is_conservative"] is True

        result2 = va.dario_dilemma(lambda_true=0.10, lambda_invest=0.30)
        assert "error" not in result2
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
        diag = np.diagonal(result["value_loss_pct"])
        assert not np.any(np.isnan(diag))
        assert np.all(np.abs(diag) < 0.01)


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


class TestDilemmaAsymmetry:
    def test_underinvestment_costlier_for_equal_mismatch(self, va):
        """Numerical Finding 1: for the same |lambda_invest - lambda_true|,
        the conservative loss exceeds the aggressive loss."""
        for delta in [0.05, 0.08]:
            r_cons = va.dario_dilemma(0.10, 0.10 - delta)
            r_aggr = va.dario_dilemma(0.10, 0.10 + delta)
            assert "error" not in r_cons
            assert "error" not in r_aggr
            assert r_cons["value_loss_pct"] > r_aggr["value_loss_pct"]

    def test_baseline_loss_magnitudes(self, va):
        """Regression: paper values 26% (lambda=0.02) and 6% (lambda=0.20)."""
        r_cons = va.dario_dilemma(0.10, 0.02)
        r_aggr = va.dario_dilemma(0.10, 0.20)
        assert abs(r_cons["value_loss_pct"] - 0.262) < 0.01
        assert abs(r_aggr["value_loss_pct"] - 0.056) < 0.01

    def test_asymmetry_invariant_to_delta(self):
        """Section 4's delta = 0.10 robustness check: delta is a capacity
        normalization, so the dilemma percentages and the preemption
        discount are numerically unchanged."""
        from ai_lab_investment.models.duopoly import DuopolyModel

        losses, discounts = [], []
        for delta in [0.03, 0.10]:
            p = ModelParameters(delta=delta)
            v = ValuationAnalysis(p)
            losses.append((
                v.dario_dilemma(0.10, 0.02)["value_loss_pct"],
                v.dario_dilemma(0.10, 0.20)["value_loss_pct"],
            ))
            eq = DuopolyModel(p, leverage=0.0).solve_preemption_equilibrium("L")
            discounts.append(eq["X_leader"] / eq["X_leader_monopolist"])

        assert losses[1][0] == pytest.approx(losses[0][0], rel=1e-4)
        assert losses[1][1] == pytest.approx(losses[0][1], rel=1e-4)
        assert discounts[1] == pytest.approx(discounts[0], rel=1e-4)
        assert discounts[0] == pytest.approx(0.57, abs=0.01)


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
        """Option values should be positive at all baseline-range lambdas."""
        lam_vals = np.array([0.10, 0.20, 0.50])
        result = va.equity_value_vs_lambda(lam_vals)
        valid = ~np.isnan(result["option_values"])
        assert valid.sum() == len(lam_vals)
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
        assert valid.sum() == 2
        assert result["phis"][1] > result["phis"][0]


# ------------------------------------------------------------------
# Capacity gap decomposition (paper fig-growth-decomposition)
# ------------------------------------------------------------------


class TestCapacityGapDecomposition:
    def test_gap_declines_and_vanishes(self, va):
        """Gap fraction declines in installed capacity and reaches zero
        before K/K* = 1 (the benchmark nets out the full investment cost
        while assets-in-place are gross of sunk costs)."""
        K_fracs = np.linspace(0.05, 1.2, 24)
        d = va.capacity_gap_decomposition(K_fracs)
        gf = d["gap_fraction"]
        assert np.all(np.diff(gf) <= 1e-9)  # weakly declining
        assert gf[0] > 50.0  # large gap at low installed capacity
        assert gf[-1] == 0.0  # zero at and beyond optimal scale
        # Crossover strictly below K/K* = 1
        below_one = K_fracs < 1.0
        assert np.any(gf[below_one] == 0.0)

    def test_paper_range_30_to_60_pct(self, va):
        """Paper claim: gap fraction roughly 30-60% for K/K* in [0.1, 0.3]."""
        d = va.capacity_gap_decomposition(np.array([0.1, 0.3]))
        assert 40.0 < d["gap_fraction"][0] < 60.0
        assert 20.0 < d["gap_fraction"][1] < 35.0


# ------------------------------------------------------------------
# Appendix E robustness tables (regression pins)
# ------------------------------------------------------------------


class TestAppendixERobustness:
    """Regression pins for the Appendix E robustness tables.

    These functions generate tbl-fixedpie, tbl-duopoly-dilemma, and
    tbl-dynamic-phi in the paper; the pins keep the published numbers
    reproducible from the test suite.
    """

    def test_fixed_pie_table(self, va):
        """tbl-fixedpie: phi_F = 0.70 under both contests; preemption
        discount 0.57 (Tullock) vs 0.63 (fixed pie); phi_underbar 0.18."""
        result = va.fixed_pie_robustness(leverage=0.0)
        assert "error" not in result
        assert "fixedpie_error" not in result
        assert abs(result["tullock_phi_F"] - 0.70) < 0.01
        assert abs(result["fixedpie_phi_F"] - 0.70) < 0.01
        assert abs(result["tullock_preemption_discount"] - 0.573) < 0.01
        assert abs(result["fixedpie_preemption_discount"] - 0.628) < 0.01
        assert abs(result["tullock_phi_underbar"] - 0.180) < 0.005

    def test_duopoly_dilemma_table(self, va):
        """tbl-duopoly-dilemma: 26%->38% conservative, 6%->17% aggressive;
        competition amplifies both losses but preserves the asymmetry."""
        r_cons = va.dario_dilemma_duopoly(0.10, 0.02)
        r_aggr = va.dario_dilemma_duopoly(0.10, 0.20)
        assert "error" not in r_cons
        assert "error" not in r_aggr
        assert abs(r_cons["value_loss_pct_duopoly"] - 0.383) < 0.02
        assert abs(r_aggr["value_loss_pct_duopoly"] - 0.173) < 0.02
        assert r_cons["value_loss_pct_duopoly"] > r_cons["value_loss_pct_single"]
        assert r_aggr["value_loss_pct_duopoly"] > r_aggr["value_loss_pct_single"]
        assert r_cons["value_loss_pct_duopoly"] > r_aggr["value_loss_pct_duopoly"]
        assert r_cons["focal_leads"] is False  # conservative cedes the lead
        assert r_aggr["focal_leads"] is True

    def test_dynamic_phi_table(self, va):
        """tbl-dynamic-phi: phi_1 at or below the static optimum, rising
        back toward it as reallocation gets costlier; phi_H at the training
        corner when kappa = 0; value gains declining in the adjustment
        cost; phi_underbar unchanged."""
        # kappa -> (phi_1, phi_H, phi_L2, value gain %)
        expected = {
            0.0: (0.01, 0.99, 0.70, 5.06),
            0.5: (0.60, 0.99, 0.66, 1.90),
            2.0: (0.69, 0.92, 0.69, 0.86),
            10.0: (0.70, 0.75, 0.70, 0.20),
        }
        gains = []
        for kappa, (phi_1, phi_H, phi_L2, gain) in expected.items():
            r = va.two_period_dynamic_phi(adjustment_cost=kappa)
            assert "error" not in r
            assert abs(r["phi_1_dynamic"] - phi_1) < 0.02
            assert abs(r["phi_H_dynamic"] - phi_H) < 0.02
            assert abs(r["phi_L2_dynamic"] - phi_L2) < 0.02
            assert abs(r["value_gain_pct"] - gain) < 0.15
            assert abs(r["phi_underbar"] - 0.180) < 0.005
            # the reallocation option never raises the initial allocation
            assert r["phi_1_dynamic"] <= r["phi_static"] + 1e-3
            gains.append(r["value_gain_pct"])
        assert all(g1 >= g2 - 1e-9 for g1, g2 in itertools.pairwise(gains))

    def test_two_period_decomposition_collapses_to_a_eff(self, va):
        """The two-period value decomposition is exact: with the same
        allocation in every branch it reproduces the perpetual A_eff of
        eq-a-eff, so the static benchmark behind the tbl-dynamic-phi value
        gains is literally the static model's revenue coefficient."""
        model = SingleFirmModel(va.params)
        _, K_s, phi_s = model.optimal_trigger_capacity_phi()
        a_eff = model._effective_revenue_coeff_single(phi_s, K_s)
        for dt in [0.25, 1.0, 5.0]:
            r = va.two_period_dynamic_phi(dt=dt, adjustment_cost=1.0)
            assert "error" not in r
            assert r["value_static"] == pytest.approx(a_eff, rel=1e-10)


# ------------------------------------------------------------------
# Option value curvature in lambda (paper, Equity Valuation Sensitivity)
# ------------------------------------------------------------------


class TestOptionValueCurvatureInLambda:
    def test_increasing_and_concave_over_policy_range(self, va):
        """The option value is increasing and concave in lambda over the
        policy-relevant range [0.1, 0.5]. Curvature in lambda is
        independent of X (F = C(lambda) X^beta_H below the trigger), so a
        single evaluation point suffices."""
        from ai_lab_investment.models.base_model import SingleFirmModel

        lams = np.linspace(0.10, 0.50, 9)
        vals = []
        for lam in lams:
            m = SingleFirmModel(va.params.with_param(lam=lam))
            vals.append(m.option_value_with_phi(0.001))
        vals = np.array(vals)
        assert np.all(np.diff(vals) > 0)  # increasing in lambda
        assert np.all(np.diff(vals, 2) < 0)  # concave in lambda
