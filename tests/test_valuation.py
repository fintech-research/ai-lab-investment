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


class TestPublishedCreditLevels:
    """Pin the credit levels printed in section 5.2 and fig-credit-risk.

    The formula itself is Monte-Carlo verified above; these pins guard the
    *published levels* against silent drift. Everything here is a
    deterministic closed-form evaluation at the figure's own conventions
    (X = CREDIT_RISK_DEMAND_LEVEL, K = 1, phi = 0.5), so the tolerances
    are tight enough to catch a one-digit change in the printed value.
    """

    def test_spread_levels_at_quoted_leverages(self, va):
        """Paper: 'approximately 40 bps at ell = 0.40 and 100 bps at
        ell = 0.70'."""
        assert va.credit_spread(leverage=0.40) * 1e4 == pytest.approx(41.34, abs=0.2)
        assert va.credit_spread(leverage=0.70) * 1e4 == pytest.approx(97.13, abs=0.5)

    def test_spread_turns_positive_near_leverage_013(self, va):
        """Paper: the spread turns positive 'around ell ~ 0.13'."""
        assert va.credit_spread(leverage=0.13) < 1e-9
        assert va.credit_spread(leverage=0.14) * 1e4 == pytest.approx(1.05, abs=0.1)
        assert va.credit_spread(leverage=0.15) * 1e4 == pytest.approx(3.07, abs=0.1)

    def test_default_probability_levels(self, va):
        """Paper: the 5-year default probability 'rises from approximately
        0.6% at low leverage to approximately 13% at ell = 0.70'. The
        figure's leverage grid starts at 0.05."""
        pd = va.default_probability
        X = va.CREDIT_RISK_DEMAND_LEVEL
        assert pd(X, 1.0, 0.05) * 100 == pytest.approx(0.627, abs=0.01)
        assert pd(X, 1.0, 0.40) * 100 == pytest.approx(4.847, abs=0.02)
        assert pd(X, 1.0, 0.70) * 100 == pytest.approx(12.979, abs=0.05)

    def test_figure_grid_endpoints(self, va):
        """fig-credit-risk plots credit_spread_curve() on
        linspace(0.05, 0.70, 30); pin both endpoints of both panels."""
        result = va.credit_spread_curve(np.linspace(0.05, 0.70, 30))
        spreads_bps = result["credit_spread"] * 1e4
        pds_pct = result["default_probability"] * 100
        assert spreads_bps[0] == pytest.approx(0.0, abs=1e-9)
        assert spreads_bps[-1] == pytest.approx(97.13, abs=0.5)
        assert pds_pct[0] == pytest.approx(0.627, abs=0.01)
        assert pds_pct[-1] == pytest.approx(12.979, abs=0.05)
        # Panel shapes: spread weakly increasing, default prob strictly so.
        assert np.all(np.diff(spreads_bps) >= -1e-12)
        assert np.all(np.diff(pds_pct) > 0)


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
        """Regression: default probs at baseline match paper values
        (section 5.2: 0.64% baseline, 0.79% conservative, 5.04%
        aggressive). Pinned to +/-0.01pp, i.e. one digit of the printed
        two-decimal percentage."""
        r_cons = va.dario_dilemma_leveraged(0.10, 0.02, leverage=0.40)
        r_aggr = va.dario_dilemma_leveraged(0.10, 0.50, leverage=0.40)
        assert "error" not in r_cons
        assert "error" not in r_aggr
        assert r_cons["default_prob_optimal"] * 100 == pytest.approx(0.64, abs=0.01)
        assert r_aggr["default_prob_optimal"] * 100 == pytest.approx(0.64, abs=0.01)
        assert r_cons["default_prob_mismatch"] * 100 == pytest.approx(0.79, abs=0.01)
        assert r_aggr["default_prob_mismatch"] * 100 == pytest.approx(5.04, abs=0.01)

    def test_baseline_triggers_allocations_and_distance_to_default(self, va):
        """Section 5.2 prose: the conservative firm enters at X* = 0.0055
        against 0.0047 at correct beliefs; the aggressive firm at 0.0033
        while over-training (phi* = 0.97 against 0.70). Distance to
        default X*/X_D falls from 5.1 to 4.9 (conservative) and 3.3
        (aggressive)."""
        from ai_lab_investment.models.duopoly import DuopolyModel

        duo = DuopolyModel(
            va.params, leverage=0.40, coupon_rate=0.05, bankruptcy_cost=0.30
        )
        expected = {
            # lambda_invest -> (X*, phi*, X*/X_D)
            0.02: (0.005515, 0.1381, 4.85),
            0.10: (0.004722, 0.7009, 5.05),
            0.50: (0.003337, 0.9716, 3.27),
        }
        for lam, (X_exp, phi_exp, dd_exp) in expected.items():
            model = SingleFirmModel(va.params.with_param(lam=lam))
            X, K, phi = model.optimal_trigger_capacity_phi()
            assert pytest.approx(X_exp, abs=5e-6) == X
            assert phi == pytest.approx(phi_exp, abs=5e-4)
            X_D = duo.default_boundary(phi, K, 0.0, 0.0)
            assert pytest.approx(dd_exp, abs=0.01) == X / X_D

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
        """Regression: paper values 26% (lambda=0.02) and 6% (lambda=0.20),
        and the asymmetry ratio 4.6 quoted in Internet Appendix E. Pinned
        to +/-0.2pp so a one-digit drift in the printed percentage fails."""
        r_cons = va.dario_dilemma(0.10, 0.02)
        r_aggr = va.dario_dilemma(0.10, 0.20)
        assert r_cons["value_loss_pct"] * 100 == pytest.approx(26.19, abs=0.2)
        assert r_aggr["value_loss_pct"] * 100 == pytest.approx(5.63, abs=0.2)
        ratio = r_cons["value_loss_pct"] / r_aggr["value_loss_pct"]
        assert ratio == pytest.approx(4.65, abs=0.05)

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

    def test_paper_range_25_to_50_pct(self, va):
        """Paper claim (_valuation.qmd): the scale-gap index runs at roughly
        25-50% for K/K* in [0.1, 0.3], equalling ~50% at 0.1 and ~26% at 0.3."""
        d = va.capacity_gap_decomposition(np.array([0.1, 0.3]))
        assert d["gap_fraction"][0] == pytest.approx(50.1, abs=0.5)
        assert d["gap_fraction"][1] == pytest.approx(26.0, abs=0.5)
        # Band quoted in the paper brackets both endpoints.
        assert 25.0 <= d["gap_fraction"][1] < d["gap_fraction"][0] <= 50.5

    def test_zero_crossover_near_077(self, va):
        """Paper claim: the index reaches zero at K/K* ~ 0.77."""
        K_fracs = np.linspace(0.5, 1.0, 501)
        gf = va.capacity_gap_decomposition(K_fracs)["gap_fraction"]
        crossover = K_fracs[np.argmax(gf <= 0.0)]
        assert crossover == pytest.approx(0.77, abs=0.02)


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
        competition amplifies both losses but preserves the asymmetry.
        Pinned to +/-0.2pp, one digit of the printed percentage."""
        r_cons = va.dario_dilemma_duopoly(0.10, 0.02)
        r_aggr = va.dario_dilemma_duopoly(0.10, 0.20)
        assert "error" not in r_cons
        assert "error" not in r_aggr
        assert r_cons["value_loss_pct_single"] * 100 == pytest.approx(26.19, abs=0.2)
        assert r_aggr["value_loss_pct_single"] * 100 == pytest.approx(5.63, abs=0.2)
        assert r_cons["value_loss_pct_duopoly"] * 100 == pytest.approx(38.31, abs=0.2)
        assert r_aggr["value_loss_pct_duopoly"] * 100 == pytest.approx(17.33, abs=0.2)
        assert r_cons["value_loss_pct_duopoly"] > r_cons["value_loss_pct_single"]
        assert r_aggr["value_loss_pct_duopoly"] > r_aggr["value_loss_pct_single"]
        assert r_cons["value_loss_pct_duopoly"] > r_aggr["value_loss_pct_duopoly"]
        assert r_cons["focal_leads"] is False  # conservative cedes the lead
        assert r_aggr["focal_leads"] is True

    def test_duopoly_dilemma_prose_numbers(self, va):
        """Internet Appendix E prose around tbl-duopoly-dilemma: the
        conservative firm invests at X* = 0.0055 against the rival's
        0.0047 and under-allocates to training (phi = 0.14 vs 0.70); the
        aggressive firm leads at X* = 0.0040 while over-allocating
        (phi = 0.88)."""
        r_cons = va.dario_dilemma_duopoly(0.10, 0.02)
        r_aggr = va.dario_dilemma_duopoly(0.10, 0.20)
        assert r_cons["X_focal"] == pytest.approx(0.005515, abs=5e-6)
        assert r_cons["X_rival"] == pytest.approx(0.004722, abs=5e-6)
        assert r_cons["phi_focal"] == pytest.approx(0.1381, abs=5e-4)
        assert r_cons["phi_rival"] == pytest.approx(0.7009, abs=5e-4)
        assert r_aggr["X_focal"] == pytest.approx(0.003999, abs=5e-6)
        assert r_aggr["X_rival"] == pytest.approx(0.004722, abs=5e-6)
        assert r_aggr["phi_focal"] == pytest.approx(0.8815, abs=5e-4)
        assert r_aggr["phi_rival"] == pytest.approx(0.7009, abs=5e-4)

    def test_dynamic_phi_table(self, va):
        """tbl-dynamic-phi: phi_1 at or below the static optimum, rising
        back toward it as reallocation gets costlier; phi_H at the training
        corner when kappa = 0; value gains declining in the adjustment
        cost; phi_underbar unchanged.

        The table prints phi to two decimals and value gains to one, so
        the tolerances (0.005 on phi, 0.03pp on gains) are set to fail on
        a one-digit change in any printed cell.
        """
        # kappa -> (phi_1, phi_H, phi_L2, value gain %)
        expected = {
            0.0: (0.010, 0.990, 0.7009, 5.056),
            0.5: (0.6017, 0.990, 0.6602, 1.896),
            2.0: (0.6871, 0.9235, 0.6908, 0.859),
            10.0: (0.6979, 0.7514, 0.6981, 0.196),
        }
        gains = []
        for kappa, (phi_1, phi_H, phi_L2, gain) in expected.items():
            r = va.two_period_dynamic_phi(adjustment_cost=kappa)
            assert "error" not in r
            assert r["phi_static"] == pytest.approx(0.7009, abs=5e-4)
            assert r["phi_1_dynamic"] == pytest.approx(phi_1, abs=0.005)
            assert r["phi_H_dynamic"] == pytest.approx(phi_H, abs=0.005)
            assert r["phi_L2_dynamic"] == pytest.approx(phi_L2, abs=0.005)
            assert r["value_gain_pct"] == pytest.approx(gain, abs=0.03)
            assert r["phi_underbar"] == pytest.approx(0.1801, abs=5e-4)
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
