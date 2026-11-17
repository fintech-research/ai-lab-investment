"""Tests for the single-firm base model.

The full-model entry points (`solve`, `optimal_trigger_capacity_phi`,
`option_value_with_phi`) return the model of record, the exact piecewise
problem. Everything that pins the pure-power approximation, including the
numbers the sections not yet revised still quote, lives in
`TestPurePowerApproximation`.
"""

from itertools import pairwise

import numpy as np
import pytest

from ai_lab_investment.models.base_model import SingleFirmModel
from ai_lab_investment.models.parameters import ModelParameters
from ai_lab_investment.models.piecewise_option import (
    BELIEF_GRID,
    PiecewiseOptionModel,
    belief_comparative_statics,
    belief_trigger_ranges,
    piecewise_bias,
    reduced_form_reference,
    smooth_fit_trigger,
)


@pytest.fixture
def default_params():
    return ModelParameters()


@pytest.fixture
def model(default_params):
    return SingleFirmModel(default_params)


@pytest.fixture(scope="module")
def solution():
    """Baseline model-of-record solution."""
    return SingleFirmModel(ModelParameters()).solve()


@pytest.fixture(scope="module")
def belief_table():
    return belief_comparative_statics(ModelParameters())


@pytest.fixture(scope="module")
def belief_ranges():
    return belief_trigger_ranges(ModelParameters())


@pytest.fixture(scope="module")
def reduced():
    return reduced_form_reference(ModelParameters())


@pytest.fixture(scope="module")
def baseline_bias():
    return piecewise_bias(ModelParameters())


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
    """`optimal_trigger_capacity_phi` returns the precommitted-scale policy
    of the model of record (Proposition 1)."""

    def test_baseline_policy(self, model):
        """Pins the (X*, K*, phi*) quoted in Proposition 1, tbl-baseline-results
        and the AGENTS.md fact lists."""
        X_star, K_star, phi_star = model.optimal_trigger_capacity_phi()
        assert X_star == pytest.approx(0.009258, abs=1e-6)
        assert K_star == pytest.approx(0.015784, abs=1e-6)
        assert phi_star == pytest.approx(0.700856, abs=1e-6)

    def test_is_the_precommitted_solution(self, model, solution):
        X_star, K_star, phi_star = model.optimal_trigger_capacity_phi()
        assert X_star == solution.precommitted.X_star
        assert K_star == solution.precommitted.K
        assert phi_star == solution.phi_star

    def test_trigger_lies_above_the_post_switch_trigger(self, solution):
        """The baseline problem is two-region: X* > X_H*."""
        assert solution.precommitted.two_region
        assert pytest.approx(0.002783, abs=1e-6) == solution.X_H

    def test_phi_interior(self, model):
        _, _, phi_star = model.optimal_trigger_capacity_phi()
        assert 0.05 < phi_star < 0.95

    def test_phi_depends_on_lambda(self):
        """Higher lambda shifts phi toward training."""
        _, _, phi_low = SingleFirmModel(
            ModelParameters(lam=0.05)
        ).optimal_trigger_capacity_phi()
        _, _, phi_high = SingleFirmModel(
            ModelParameters(lam=0.50)
        ).optimal_trigger_capacity_phi()
        assert phi_high > phi_low

    def test_npv_positive_at_trigger(self, model):
        X_star, K_star, phi_star = model.optimal_trigger_capacity_phi()
        V = model.installed_value_with_phi(X_star, phi_star, K_star, "L")
        assert V - model.investment_cost(K_star) > 0

    def test_solution_is_cached(self, model):
        assert model.solve() is model.solve()


class TestSingleFirmSolution:
    """What the monopolist does in the exact problem (issue #176)."""

    def test_monopolist_waits_at_baseline(self, solution):
        """With scale chosen whenever the firm invests, no finite pre-switch
        trigger exists at baseline."""
        assert not solution.invests_before_switch
        assert np.isinf(solution.X_star)
        assert np.isnan(solution.K_star)
        assert solution.waiting_margin == pytest.approx(1.0773, abs=1e-3)

    def test_waiting_confirmed_by_the_complementarity_problem(self, solution):
        """Policy iteration on the exercise envelope returns an empty
        stopping region (no assumption on its shape)."""
        assert solution._unrestricted.joint_lcp()["kind"] == "never"

    def test_value_ranking_at_baseline(self, solution):
        """At X_0 = half the pure-power trigger: waiting with scale chosen at
        the switch (1.741e-3) beats the precommitted-scale optimum
        (1.659e-3), which beats waiting with precommitted scale (1.619e-3),
        which beats the pure-power policy (1.615e-3). The last comparison is
        the one Internet Appendix B reports; it concerns the pure-power
        policy, not the precommitted-scale optimum."""
        X_pp, K_pp, phi_pp = solution.pure_power
        X_0 = 0.5 * X_pp
        wait = solution.waiting_value(X_0)
        pre = solution.precommitted_value(X_0)
        wait_pre = solution.precommitted_waiting_value(X_0)
        pp = solution._piecewise.threshold_value(K_pp, phi_pp, X_pp, X_0)
        assert wait == pytest.approx(1.7414e-3, rel=1e-4)
        assert pre == pytest.approx(1.6589e-3, rel=1e-4)
        assert wait_pre == pytest.approx(1.6192e-3, rel=1e-4)
        assert pp == pytest.approx(1.6151e-3, rel=1e-4)
        assert wait > pre > wait_pre > pp
        assert solution.value(X_0) == wait

    def test_precommitted_trigger_against_brennan_schwartz(self, solution):
        """Independent LCP solve at the optimal (K*, phi*) reproduces the
        free boundary of the two-region system."""
        pre = solution.precommitted
        _, _, boundary = solution._piecewise.finite_difference_value(
            pre.K, pre.phi, n_grid=20001
        )
        assert boundary == pytest.approx(pre.X_star, rel=1e-3)

    def test_post_switch_policy_is_the_H_regime_problem(self, model, solution):
        X_H, K_H = model.optimal_trigger_and_capacity("H")
        assert solution.X_H == X_H
        assert solution.K_H == K_H

    def test_finite_trigger_at_a_low_arrival_rate(self):
        """Internet Appendix B: at lambda = 0.05 the unrestricted problem
        invests before the switch, at X* = 0.0173 with K* = 0.029."""
        sol = SingleFirmModel(ModelParameters(lam=0.05)).solve()
        assert sol.invests_before_switch
        assert sol.waiting_margin < 1.0
        assert sol.X_star == pytest.approx(0.01729, rel=1e-3)
        assert sol.K_star == pytest.approx(0.02890, rel=1e-3)
        X_0 = 0.002
        assert sol.value(X_0) > sol.waiting_value(X_0)

    def test_versions_coincide_below_the_post_switch_trigger(self):
        """When the trigger lies below X_H* the post-switch scale assumption
        is immaterial: the precommitted and unrestricted policies agree."""
        sol = SingleFirmModel(ModelParameters(lam=0.03)).solve()
        assert sol.precommitted.X_star < sol.X_H
        assert not sol.precommitted.two_region
        assert sol.X_star == pytest.approx(sol.precommitted.X_star, rel=1e-6)
        assert sol.K_star == pytest.approx(sol.precommitted.K, rel=1e-6)

    def test_waiting_result_across_the_admissible_ranges(self):
        """Internet Appendix B: over the (A2)-admissible ranges the firm
        invests before the switch only at the top of the gamma range."""
        base = ModelParameters()
        for name, value in [
            ("sigma", 0.20),
            ("sigma", 0.38),
            ("alpha", 0.37),
            ("alpha", 0.53),
            ("r", 0.10),
            ("r", 0.13),
            ("gamma", 1.15),
        ]:
            sol = SingleFirmModel(base.with_param(**{name: value})).solve()
            assert not sol.invests_before_switch, (name, value)
        for gamma in (1.9, 2.0):
            sol = SingleFirmModel(base.with_param(gamma=gamma)).solve()
            assert sol.invests_before_switch
        assert SingleFirmModel(base.with_param(gamma=1.9)).solve().waiting_margin == (
            pytest.approx(0.993, abs=2e-3)
        )

    def test_pure_power_error(self, solution):
        """Measured error of the nested approximation at baseline."""
        err = solution.pure_power_error()
        assert err["trigger_pct"] == pytest.approx(-49.0, abs=0.1)
        assert err["capacity_pct"] == pytest.approx(-57.4, abs=0.1)
        assert abs(err["phi_gap"]) < 1e-6
        assert err["value_loss_precommitted_pct"] == pytest.approx(2.64, abs=0.02)
        assert err["value_loss_unrestricted_pct"] == pytest.approx(6.89, abs=0.02)


class TestBeliefComparativeStatics:
    """K*(lambda), X*(lambda), phi*(lambda) in the model of record
    (review comments C5 and C20)."""

    def test_belief_table(self, belief_table):
        """Pins the belief table quoted after Remark 3."""
        t = belief_table
        assert (
            tuple(t["lam"])
            == BELIEF_GRID
            == (0.03, 0.05, 0.075, 0.10, 0.15, 0.20, 0.50)
        )
        np.testing.assert_allclose(
            t["phi_star"],
            [0.2395, 0.4246, 0.5919, 0.7009, 0.8216, 0.8815, 0.9716],
            atol=5e-5,
        )
        np.testing.assert_allclose(
            t["X_precommitted"],
            [0.0004393, 0.005516, 0.008262, 0.009258, 0.009404, 0.008905, 0.006552],
            rtol=1e-3,
        )
        np.testing.assert_allclose(
            t["K_precommitted"],
            [0.0001707, 0.007040, 0.012736, 0.015784, 0.018100, 0.018433, 0.015810],
            rtol=1e-3,
        )

    def test_finite_unrestricted_trigger_only_at_low_arrival_rates(self, belief_table):
        """On the grid a finite pre-switch trigger exists at 0.03 and 0.05
        and at no higher rate."""
        t = belief_table
        np.testing.assert_array_equal(
            t["invests_before_switch"], [1.0, 1.0, 0.0, 0.0, 0.0, 0.0, 0.0]
        )
        np.testing.assert_allclose(
            t["X_unrestricted"][:2], [0.0004393, 0.017292], rtol=1e-3
        )
        np.testing.assert_allclose(
            t["K_unrestricted"][:2], [0.0001707, 0.028899], rtol=1e-3
        )
        assert np.all(np.isinf(t["X_unrestricted"][2:]))

    def test_existence_bound(self, belief_ranges):
        """The unrestricted trigger exists for lambda < 0.0729."""
        lam_bar = belief_ranges["lam_bar"]
        assert lam_bar == pytest.approx(0.0729, abs=1e-4)
        below = SingleFirmModel(ModelParameters(lam=lam_bar - 1e-3)).solve()
        above = SingleFirmModel(ModelParameters(lam=lam_bar + 1e-3)).solve()
        assert below.invests_before_switch
        assert not above.invests_before_switch

    def test_no_trigger_reappears_at_high_arrival_rates(self):
        """The waiting margin peaks near lambda = 0.2 and declines toward
        one from above; it stays above one up to lambda = 20."""
        for lam in (0.5, 1.0, 3.0, 20.0):
            sol = SingleFirmModel(ModelParameters(lam=lam)).solve()
            assert sol.waiting_margin > 1.0
            assert not sol.invests_before_switch

    def test_unrestricted_trigger_rises_in_lambda_where_it_exists(self):
        """A monopolist expecting the switch sooner invests later."""
        lams = np.linspace(0.01, 0.072, 32)
        triggers = [
            SingleFirmModel(ModelParameters(lam=v)).solve().X_star for v in lams
        ]
        capacities = [
            SingleFirmModel(ModelParameters(lam=v)).solve().K_star for v in lams
        ]
        assert np.all(np.diff(triggers) > 0)
        assert np.all(np.diff(capacities) > 0)

    def test_precommitted_trigger_is_hump_shaped(self, belief_ranges):
        """C20: the precommitted-scale trigger rises in lambda up to about
        0.127 and falls beyond; capacity peaks near 0.192."""
        assert belief_ranges["precommitted_trigger_peak"] == pytest.approx(
            0.1273, abs=1e-3
        )
        assert belief_ranges["precommitted_capacity_peak"] == pytest.approx(
            0.1924, abs=1e-3
        )
        lams = np.linspace(0.02, 0.50, 49)
        X = np.array([
            PiecewiseOptionModel(ModelParameters(lam=v)).precommitted_optimum().X_star
            for v in lams
        ])
        rising = lams[1:] <= 0.127
        assert np.all(np.diff(X)[rising] > 0)
        assert np.all(np.diff(X)[lams[:-1] >= 0.128] < 0)

    def test_C20_table(self, belief_table, baseline_bias):
        """Reviewer's table: K* = 0.0158, 0.0184, 0.0158 at lambda = 0.10,
        0.20, 0.50 reproduce; the trigger peaks on the grid at 0.15."""
        t = belief_table
        K = dict(zip(t["lam"], t["K_precommitted"], strict=True))
        X = dict(zip(t["lam"], t["X_precommitted"], strict=True))
        assert K[0.10] == pytest.approx(0.0158, abs=5e-5)
        assert K[0.20] == pytest.approx(0.0184, abs=5e-5)
        assert K[0.50] == pytest.approx(0.0158, abs=5e-5)
        assert X[0.10] == pytest.approx(0.0093, abs=5e-5)
        assert X[0.15] == pytest.approx(0.0094, abs=5e-5)
        assert max(X, key=X.get) == 0.15
        # the reviewer's own route at baseline, through optimal_policy(X_0)
        assert baseline_bias["K_piecewise_opt"] == pytest.approx(K[0.10], rel=1e-4)

    def test_C20_entry_at_lambda_003_is_an_evaluation_demand_artifact(
        self, belief_table, reduced
    ):
        """The reviewer's K* = 0.0021 at lambda = 0.03 reproduces only as the
        best *immediate* investment at X_0 = X*(0.10)/2: the trigger of that
        belief (0.00044) lies below X_0. The demand-free optimum is
        K* = 0.00017."""
        X_0 = 0.5 * reduced["X_star"]
        pw = PiecewiseOptionModel(ModelParameters(lam=0.03))
        at_demand = pw.optimal_policy(X_0)
        assert pytest.approx(0.0021, abs=5e-5) == at_demand.K
        assert at_demand.X_star == pytest.approx(0.0021, abs=5e-5)
        assert at_demand.X_star < X_0
        free = pw.precommitted_optimum()
        assert free.X_star < X_0
        assert pytest.approx(belief_table["K_precommitted"][0], rel=1e-9) == free.K
        assert pytest.approx(0.000171, rel=1e-2) == free.K
        assert pw.exercise_premium(free.K, free.phi) > pw.exercise_premium(
            at_demand.K, at_demand.phi
        )

    def test_capacity_responds_to_beliefs(self, belief_table):
        """Capacity is not belief-invariant in the model of record: it varies
        by a factor of about 90 over the grid (2.6 over [0.05, 0.50])."""
        K = belief_table["K_precommitted"]
        assert K.max() / K.min() == pytest.approx(108.0, rel=0.02)
        assert K[1:].max() / K[1:].min() == pytest.approx(2.62, abs=0.02)
        assert np.ptp(belief_table["K_pure_power"]) < 1e-8


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
        assert m.closed_form_phi_star() > 0.95

    def test_policy_approaches_the_H_regime_policy(self):
        """Nesting: as lambda grows the exact precommitted-scale policy
        approaches the H-regime policy (X_H*, K_H*), monotonically."""
        gaps = []
        for lam in (0.5, 2.0, 20.0, 100.0):
            sol = PiecewiseOptionModel(ModelParameters(lam=lam))
            opt = sol.precommitted_optimum()
            gaps.append((opt.X_star / sol.X_H - 1.0, opt.K / sol.K_H - 1.0))
        assert all(a[0] > b[0] > 0 and a[1] > b[1] > 0 for a, b in pairwise(gaps))
        assert gaps[-1][0] < 0.07
        assert gaps[-1][1] < 0.09

    def test_simulation_switches_immediately(self):
        m = SingleFirmModel(ModelParameters(lam=500.0))
        sim = m.simulate_demand(X0=1.0, T=1.0, dt=0.001, rng=np.random.default_rng(1))
        assert sim["regime"][-1] == 1
        # 1 - exp(-0.5) ~ 39% per step: the switch happens in the first
        # handful of steps with overwhelming probability.
        assert int(np.argmax(sim["regime"] == 1)) < 50


class TestOptionValueWithPhi:
    """Exact value of the firm that has not invested."""

    def test_positive_and_increasing(self, model):
        values = [model.option_value_with_phi(x) for x in (0.001, 0.003, 0.3, 0.8)]
        assert values[0] > 0
        assert np.all(np.diff(values) > 0)

    def test_is_the_waiting_value_at_baseline(self, model, solution):
        for X in (0.001, 0.01, 0.5):
            assert model.option_value_with_phi(X) == solution.waiting_value(X)

    def test_dominates_every_pre_switch_investment(self, model, solution):
        """Waiting beats installing the precommitted-scale (K*, phi*) and
        the pure-power (K*, phi*) at once, at every demand level."""
        pre = solution.precommitted
        _, K_pp, phi_pp = solution.pure_power
        for X in np.geomspace(1e-3, 10.0, 25):
            wait = model.option_value_with_phi(X)
            for K, phi in ((pre.K, pre.phi), (K_pp, phi_pp)):
                npv = model.installed_value_with_phi(
                    X, phi, K, "L"
                ) - model.investment_cost(K)
                assert wait > npv

    def test_exceeds_the_pure_power_value(self, model):
        """The approximation understates the option value at baseline."""
        X = 0.002
        assert model.option_value_with_phi(X) > model.pure_power_option_value(X)


class TestProposition1ClosedForm:
    """Proposition 1 in the model of record: phi* in closed form, K_H* in
    closed form, (X*, K*) from the two-region system."""

    @staticmethod
    def _closed_form_K_H(p: ModelParameters) -> float:
        b = p.beta_H
        return (
            p.delta
            * (p.alpha * b - b + 1.0)
            / (p.r * p.c * (p.gamma * (b - 1.0) - p.alpha * b))
        ) ** (1.0 / (p.gamma - 1.0))

    def test_closed_form_phi_star(self, model, solution):
        assert model.closed_form_phi_star() == pytest.approx(0.700856, abs=1e-5)
        assert solution.phi_star == model.closed_form_phi_star()

    def test_phi_star_maximizes_the_exercise_premium_at_every_scale(self, solution):
        """The allocation enters only through A_eff, so phi* is optimal at
        any capacity, not only at K*."""
        pw = solution._piecewise
        for K in (0.2 * solution.precommitted.K, solution.precommitted.K, 0.05):
            for phi in (solution.phi_star - 0.05, solution.phi_star + 0.05):
                a_star, _ = pw.exercise_payoff_coeffs(K, solution.phi_star)
                a_off, _ = pw.exercise_payoff_coeffs(K, phi)
                assert a_star > a_off

    def test_closed_form_post_switch_capacity(self, model, solution):
        """K_H* = [delta (alpha beta_H - beta_H + 1)
        / (r c (gamma (beta_H - 1) - alpha beta_H))]^(1/(gamma-1))."""
        K_closed = self._closed_form_K_H(model.params)
        assert pytest.approx(K_closed, rel=1e-6) == solution.K_H
        assert K_closed == pytest.approx(0.006727, abs=1e-6)

    def test_two_region_system_holds_at_the_optimum(self, solution):
        """Value matching and smooth pasting at X*, value and slope matching
        at X_H*, and the capacity first-order condition."""
        sol = solution.precommitted
        eps = sol.X_star * 1e-7
        assert sol.value(sol.X_star) == pytest.approx(sol.npv_at_trigger(), rel=1e-12)
        slope = (sol.value(sol.X_star) - sol.value(sol.X_star - eps)) / eps
        assert slope == pytest.approx(sol.a_L, rel=1e-5)

        X_H, p_pos, n, h = sol.X_H, sol.beta_L_pos, sol.beta_L_neg, sol.beta_H
        lower = sol.A_1 * X_H**p_pos + sol.C * X_H**h
        upper = sol.D_1 * X_H**p_pos + sol.D_2 * X_H**n + sol.g * X_H + sol.k
        assert lower == pytest.approx(upper, rel=1e-9)
        slope_lo = p_pos * sol.A_1 * X_H ** (p_pos - 1) + h * sol.C * X_H ** (h - 1)
        slope_hi = (
            p_pos * sol.D_1 * X_H ** (p_pos - 1) + n * sol.D_2 * X_H ** (n - 1) + sol.g
        )
        assert slope_lo == pytest.approx(slope_hi, rel=1e-6)

        p = solution._piecewise.params
        marginal_cost = p.delta / p.r + p.c * p.gamma * sol.K ** (p.gamma - 1.0)
        assert p.alpha * sol.a_L * sol.X_star / sol.K == pytest.approx(
            marginal_cost, rel=1e-7
        )
        assert pytest.approx(-8528.5, rel=1e-4) == sol.A_1

    def test_fixed_capacity_free_boundary_agrees(self, solution):
        """At K* the fixed-(K, phi) free-boundary solver returns the same
        trigger: the envelope optimum is the fixed-scale optimum."""
        pre = solution.precommitted
        fixed = solution._piecewise.solve(pre.K, pre.phi)
        assert fixed.X_star == pytest.approx(pre.X_star, rel=1e-8)

    def test_raises_outside_A2_admissible_region(self):
        """When (A2)'s upper bound fails the post-switch scale problem has
        no interior optimum; every full-model entry point must refuse."""
        for kwargs in [{"r": 0.15}, {"sigma": 0.18}]:
            m = SingleFirmModel(ModelParameters(**kwargs))
            with pytest.raises(RuntimeError, match="A2"):
                m.optimal_trigger_capacity_phi()
            with pytest.raises(RuntimeError, match="A2"):
                m.solve()
            with pytest.raises(RuntimeError, match="A2"):
                m.pure_power_trigger_capacity_phi()

    def test_duopoly_leader_raises_outside_A2(self):
        """The duopoly leader-monopolist problem inherits the same
        interior-capacity condition."""
        from ai_lab_investment.models.duopoly import DuopolyModel

        duo = DuopolyModel(ModelParameters(r=0.15), leverage=0.0)
        with pytest.raises(RuntimeError, match="A2"):
            duo.solve_leader_monopolist()


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
            SingleFirmModel(ModelParameters(r=r)).pure_power_trigger_capacity_phi()
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
        *and* lowers the trigger. The direction holds in the model of
        record; the levels Section 4 still quotes are the pure-power ones,
        pinned in TestPurePowerApproximation until issue #183."""
        triggers, capacities = [], []
        for alpha in [0.38, 0.40, 0.45]:
            X, K, _ = SingleFirmModel(
                ModelParameters(alpha=alpha)
            ).optimal_trigger_capacity_phi()
            triggers.append(X)
            capacities.append(K)
        assert triggers[0] < triggers[1] < triggers[2]
        assert capacities[0] < capacities[1] < capacities[2]
        assert triggers[0] == pytest.approx(0.00276, abs=1e-5)
        assert triggers[2] == pytest.approx(0.0827, abs=1e-4)

    def test_delta_is_a_capacity_normalization(self):
        """Section 4's delta = 0.10 check: delta enters only through
        b(K) = delta*K/r + c*K^gamma, so raising it is exactly a rescaling
        of the capacity unit. That is a property of the primitives, so it
        holds in the model of record: levels move by the closed-form
        exponents, phi* and the waiting decision are unchanged."""
        base = ModelParameters()
        high = base.with_param(delta=0.10)
        s0 = SingleFirmModel(base).solve()
        s1 = SingleFirmModel(high).solve()
        X0, K0 = s0.precommitted.X_star, s0.precommitted.K
        X1, K1 = s1.precommitted.X_star, s1.precommitted.K

        assert s1.phi_star == s0.phi_star
        assert s1.invests_before_switch == s0.invests_before_switch
        assert s1.waiting_margin == pytest.approx(s0.waiting_margin, rel=1e-9)
        scale = high.delta / base.delta
        K_ratio = scale ** (1.0 / (base.gamma - 1.0))
        X_ratio = scale ** ((base.gamma - base.alpha) / (base.gamma - 1.0))
        assert pytest.approx(K_ratio, rel=1e-5) == K1 / K0
        assert pytest.approx(X_ratio, rel=1e-5) == X1 / X0
        assert pytest.approx(K_ratio, rel=1e-6) == s1.K_H / s0.K_H
        assert pytest.approx(0.1309, abs=1e-4) == X1
        assert pytest.approx(0.1754, abs=1e-4) == K1


class TestCapacityGlobalOptimum:
    """Proposition 1: the closed-form K_H* is the global maximum of the
    post-switch capacity objective, which vanishes at both ends for
    delta > 0, and the pre-switch capacity is the single peak of the
    exercise premium."""

    def test_exercise_premium_is_single_peaked_in_capacity(self, solution):
        pw = solution._piecewise
        grid = np.linspace(-40.0, 10.0, 1001)
        vals = np.array([
            pw.exercise_premium(float(np.exp(t)), solution.phi_star) for t in grid
        ])
        finite = np.isfinite(vals)
        peaks = [
            i
            for i in range(1, len(grid) - 1)
            if finite[i] and vals[i] > vals[i - 1] and vals[i] > vals[i + 1]
        ]
        assert len(peaks) == 1
        assert np.exp(grid[peaks[0]]) == pytest.approx(
            solution.precommitted.K, rel=0.06
        )

    def test_objective_vanishes_at_both_ends(self):
        model = SingleFirmModel(ModelParameters())
        _, K_star, _ = model._solve_regime_H()
        at_opt = -model._objective_K(np.log(K_star), "H")
        for log_K in (-14.0, -10.0, 8.0, 12.0):
            assert -model._objective_K(log_K, "H") < at_opt
        # log objective falls without bound in both directions
        assert -model._objective_K(-14.0, "H") < -model._objective_K(-10.0, "H")
        assert -model._objective_K(12.0, "H") < -model._objective_K(8.0, "H")

    def test_closed_form_scales_with_delta(self):
        """K* is proportional to delta^{1/(gamma-1)}."""
        base = ModelParameters()
        _, K1, _ = SingleFirmModel(base)._solve_regime_H()
        _, K2, _ = SingleFirmModel(
            base.with_param(delta=2.0 * base.delta)
        )._solve_regime_H()
        assert pytest.approx(2.0 ** (1.0 / (base.gamma - 1.0)), rel=1e-6) == K2 / K1


class TestOptionValueInLambda:
    """Remark 3 and fig-lambda-option-value: the exact value of the firm
    that has not invested is non-monotone in lambda, with its minimum where
    phi*(lambda) crosses the faith threshold phi_underbar."""

    def test_turning_point_at_faith_threshold(self, belief_ranges):
        from ai_lab_investment.figures.paper import lambda_option_value_curve

        lams = np.linspace(0.005, 0.10, 39)
        values, phis, phi_underbar = lambda_option_value_curve(lams, X_ref=0.002)
        i_min = int(np.argmin(values))
        assert 0 < i_min < len(lams) - 1
        assert lams[i_min] == pytest.approx(0.025, abs=0.005)
        lam_cross = float(np.interp(phi_underbar, phis, lams))
        assert lam_cross == pytest.approx(lams[i_min], abs=0.005)
        assert lam_cross == pytest.approx(
            belief_ranges["pure_power_trigger_peak"], abs=5e-4
        )
        # increasing and concave over the policy range
        hi = np.linspace(0.10, 0.50, 17)
        v, _, _ = lambda_option_value_curve(hi, X_ref=0.002)
        assert np.all(np.diff(v) > 0)
        assert np.all(np.diff(v, 2) < 0)

    def test_curvature_range(self):
        """Convex between about 0.01 and 0.05, concave from 0.05 on."""
        from ai_lab_investment.figures.paper import lambda_option_value_curve

        lams = np.linspace(0.005, 0.80, 80)
        v, _, _ = lambda_option_value_curve(lams, X_ref=0.002)
        convex = lams[1:-1][np.diff(v, 2) > 0]
        assert convex.min() == pytest.approx(0.015, abs=0.006)
        assert convex.max() == pytest.approx(0.045, abs=0.006)

    def test_reference_demand_is_above_the_trigger_at_low_rates(self):
        """At X = 0.002 the firm has already invested for lambda up to about
        0.037, and waits for the switch above the existence bound."""
        low = SingleFirmModel(ModelParameters(lam=0.03)).solve()
        mid = SingleFirmModel(ModelParameters(lam=0.045)).solve()
        assert low.X_star < 0.002 < mid.X_star
        high = SingleFirmModel(ModelParameters(lam=0.10)).solve()
        assert high.value(0.002) == high.waiting_value(0.002)


class TestGammaComparativeStatic:
    """Section 3 and Internet Appendix F: K_H* is U-shaped in gamma at fixed c."""

    def test_capacity_non_monotone_in_gamma(self):
        K = {}
        for g in (1.20, 1.35, 1.50, 2.00):
            _, K[g], _ = SingleFirmModel(ModelParameters(gamma=g))._solve_regime_H()
        assert K[1.20] == pytest.approx(0.01072, rel=1e-3)
        assert K[1.35] == pytest.approx(0.00337, rel=1e-3)
        assert K[1.50] == pytest.approx(0.00673, rel=1e-3)
        assert K[2.00] == pytest.approx(0.03523, rel=1e-3)
        assert K[1.35] < K[1.50] < K[1.20] < K[2.00]


class TestMultistartSelection:
    """multistart_minimize must never return an unconverged start as the
    incumbent, even when its objective is lower."""

    def test_mixed_success_picks_converged_start(self, monkeypatch):
        from types import SimpleNamespace

        from ai_lab_investment.models import base_model as bm

        results = iter([
            SimpleNamespace(success=True, fun=1.0, x=np.array([1.0])),
            SimpleNamespace(success=False, fun=0.0, x=np.array([0.0])),
        ])
        monkeypatch.setattr(bm.optimize, "minimize", lambda *a, **k: next(results))
        best_x, best_val, diag = bm.multistart_minimize(
            lambda x: 0.0, [np.array([1.0]), np.array([0.0])]
        )
        assert diag["n_converged"] == 1
        assert best_val == 1.0
        assert best_x is not None and best_x[0] == 1.0


class TestPurePowerApproximation:
    """The pure-power form, kept as a nested approximation of the model of
    record (`pure_power_*`). Pins its numbers, including those the sections
    not yet revised still quote, its nesting, and its measured error.
    Merges the former pure-power tests of this file with
    TestReducedFormConsistency and TestBaselineBias of
    tests/test_piecewise_option.py."""

    # -- the approximate policy and the numbers of the earlier draft --

    def test_baseline_policy(self, model):
        """X* = 0.0047, K* = 0.0067, phi* = 0.70 of the earlier draft."""
        X_star, K_star, phi_star = model.pure_power_trigger_capacity_phi()
        assert X_star == pytest.approx(0.004722, abs=1e-6)
        assert K_star == pytest.approx(0.006727, abs=1e-6)
        assert phi_star == pytest.approx(0.700856, abs=1e-5)
        assert 0.01 <= phi_star <= 0.99

    def test_trigger_formula(self, model):
        """eq-trigger-pure-power: beta_H/(beta_H-1) * b(K*) / A_eff."""
        p = model.params
        X_star, K_star, phi_star = model.pure_power_trigger_capacity_phi()
        a_eff = model._effective_revenue_coeff_single(phi_star, K_star)
        b = p.delta * K_star / p.r + model.investment_cost(K_star)
        assert X_star == pytest.approx(p.beta_H / (p.beta_H - 1.0) * b / a_eff)

    def test_closed_form_K_star_matches_optimizer(self, model):
        K_closed = TestProposition1ClosedForm._closed_form_K_H(model.params)
        _, K_num, _ = model.pure_power_trigger_capacity_phi()
        assert abs(K_num - K_closed) / K_closed < 1e-4

    def test_K_star_independent_of_phi(self, model):
        """In the approximation the optimal capacity is the same at any
        fixed training fraction (A_eff = g(phi) K^alpha cancels in the K
        first-order condition). The exact problem has no such separation."""
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

    def test_closed_form_phi_star_matches_solver(self, model):
        _, _, phi_star = model.pure_power_trigger_capacity_phi()
        assert model.closed_form_phi_star() == pytest.approx(phi_star, abs=1e-6)

    def test_npv_positive_at_trigger(self, model):
        X_star, K_star, phi_star = model.pure_power_trigger_capacity_phi()
        V = model.installed_value_with_phi(X_star, phi_star, K_star, "L")
        assert V - model.investment_cost(K_star) > 0

    def test_option_value(self, model):
        """Positive, increasing, and above the NPV of immediate investment
        below the trigger."""
        assert model.pure_power_option_value(0.5) > 0
        assert model.pure_power_option_value(0.8) > model.pure_power_option_value(0.3)
        X_star, K_star, phi_star = model.pure_power_trigger_capacity_phi()
        X = X_star * 0.5
        npv = model.installed_value_with_phi(
            X, phi_star, K_star, "L"
        ) - model.investment_cost(K_star)
        assert model.pure_power_option_value(X) >= npv - 1e-10

    def test_option_value_in_lambda(self):
        """The approximate value curve of the earlier draft: minimum where
        phi* crosses phi_underbar, concave from about 0.085."""
        from ai_lab_investment.figures.paper import lambda_option_value_curve

        lams = np.linspace(0.005, 0.10, 39)
        values, phis, phi_underbar = lambda_option_value_curve(
            lams, X_ref=0.002, pure_power=True
        )
        i_min = int(np.argmin(values))
        assert lams[i_min] == pytest.approx(0.025, abs=0.005)
        assert float(np.interp(phi_underbar, phis, lams)) == pytest.approx(
            lams[i_min], abs=0.005
        )
        hi = np.linspace(0.10, 0.50, 17)
        v, _, _ = lambda_option_value_curve(hi, X_ref=0.002, pure_power=True)
        assert np.all(np.diff(v) > 0)
        assert np.all(np.diff(v, 2) < 0)

    def test_calibration_section_levels(self):
        """Levels still quoted in @sec-calibration (issue #183 re-solves
        them): triggers 0.0015 and 0.038 at alpha = 0.38 and 0.45, and
        (X*, K*) = (0.0667, 0.0747) at delta = 0.10."""
        triggers = {
            alpha: SingleFirmModel(
                ModelParameters(alpha=alpha)
            ).pure_power_trigger_capacity_phi()[0]
            for alpha in (0.38, 0.45)
        }
        assert triggers[0.38] == pytest.approx(0.0015, abs=1e-4)
        assert triggers[0.45] == pytest.approx(0.038, abs=1e-3)
        X1, K1, _ = SingleFirmModel(
            ModelParameters(delta=0.10)
        ).pure_power_trigger_capacity_phi()
        assert abs(X1 - 0.0667) < 5e-4
        assert abs(K1 - 0.0747) < 5e-4

    # -- timing in lambda (review comment C5) --

    def test_C5_trigger_rises_in_lambda_below_the_faith_threshold(self, belief_ranges):
        """X* = 0.00528, 0.00540, 0.00552 at lambda = 0.005, 0.01, 0.02: the
        approximate trigger rises in lambda while phi* < phi_underbar
        (lambda < 0.0242) and falls above."""
        triggers = [
            SingleFirmModel(ModelParameters(lam=lam)).pure_power_trigger_capacity_phi()[
                0
            ]
            for lam in (0.005, 0.01, 0.02)
        ]
        np.testing.assert_allclose(triggers, [0.00528, 0.00540, 0.00552], atol=5e-6)
        peak = belief_ranges["pure_power_trigger_peak"]
        assert peak == pytest.approx(0.02417, abs=1e-5)
        lams = np.linspace(0.005, 0.50, 100)
        X = np.array([
            SingleFirmModel(ModelParameters(lam=v)).pure_power_trigger_capacity_phi()[0]
            for v in lams
        ])
        assert np.all(np.diff(X)[lams[1:] < peak] > 0)
        assert np.all(np.diff(X)[lams[:-1] > peak] < 0)

    # -- nesting in the model of record --

    def test_allocation_is_exact(self, solution):
        assert solution.pure_power[2] == pytest.approx(solution.phi_star, abs=1e-6)

    def test_capacity_is_the_post_switch_capacity(self, solution):
        """K* of the approximation is K_H* at every arrival rate."""
        assert solution.pure_power[1] == pytest.approx(solution.K_H, rel=1e-5)
        for lam in (0.03, 0.50):
            sol = SingleFirmModel(ModelParameters(lam=lam)).solve()
            assert sol.pure_power[1] == pytest.approx(sol.K_H, rel=1e-5)

    def test_trigger_is_the_post_switch_trigger_rescaled(self, model, solution):
        """X* = X_H* A_H / g(phi*): the H-regime policy with the revenue
        coefficient A_H replaced by the effective one."""
        p = model.params
        g = model._effective_revenue_coeff_single(solution.phi_star, 1.0)
        assert solution.pure_power[0] == pytest.approx(
            solution.X_H * p.A_H / g, rel=1e-5
        )

    def test_both_collapse_onto_the_H_regime_policy(self):
        """The documented special case: as lambda grows both the exact and
        the approximate policy reduce to (X_H*, K_H*, phi = 1)."""
        m = SingleFirmModel(ModelParameters(lam=1e4))
        X_pp, K_pp, _ = m.pure_power_trigger_capacity_phi()
        X_H, K_H = m.optimal_trigger_and_capacity("H")
        assert abs(K_pp - K_H) / K_H < 0.05
        assert abs(X_pp - X_H) / X_H < 0.05
        sol = SingleFirmModel(ModelParameters(lam=100.0)).solve()
        assert sol.precommitted.X_star == pytest.approx(sol.pure_power[0], rel=0.07)
        assert pytest.approx(sol.pure_power[1], rel=0.09) == sol.precommitted.K
        assert sol.phi_star > 0.9999

    # -- consistency of the pure-power boundary conditions
    #    (formerly TestReducedFormConsistency) --

    def test_pure_power_boundary_conditions_reproduce_the_trigger(
        self, default_params, reduced
    ):
        """With the pure-power continuation value and A_1 = 0, value matching
        and smooth pasting return the closed-form trigger."""
        X = smooth_fit_trigger(default_params, reduced["K_star"], reduced["phi_star"])
        assert pytest.approx(reduced["X_star"], rel=1e-12) == X

    def test_smooth_fit_level_prices_the_approximate_policy(
        self, reduced, default_params
    ):
        npv = reduced["a_L"] * reduced["X_star"] - reduced["b_L"]
        level = npv / reduced["X_star"] ** default_params.beta_H
        assert level == pytest.approx(reduced["smooth_fit_coeff"], rel=1e-12)

    # -- measured error at baseline (formerly TestBaselineBias); if a model
    #    change moves these numbers, Internet Appendix B must move too --

    def test_trigger_and_value_error_at_the_approximate_policy(self, baseline_bias):
        b = baseline_bias
        assert b["X_star_piecewise_fixed"] == pytest.approx(0.007220, abs=1e-5)
        assert b["trigger_bias_fixed_pct"] == pytest.approx(52.9, abs=0.5)
        assert b["value_bias_fixed_pct"] == pytest.approx(19.1, abs=0.5)
        assert b["reported_value_bias_pct"] == pytest.approx(-14.8, abs=0.5)

    def test_error_against_the_exact_policy(self, baseline_bias, solution):
        b = baseline_bias
        assert b["trigger_bias_opt_pct"] == pytest.approx(96.1, abs=1.0)
        assert b["K_bias_opt_pct"] == pytest.approx(134.6, abs=2.0)
        # The training fraction is untouched: phi* maximizes A_eff at fixed K
        # in both the approximation and the exact problem.
        assert b["phi_piecewise_opt"] == pytest.approx(b["phi_reduced"], rel=1e-5)
        assert b["policy_loss_pct"] == pytest.approx(2.64, abs=0.15)
        # the demand-stated and the demand-free optimum agree at baseline
        assert b["X_star_piecewise_opt"] == pytest.approx(
            solution.precommitted.X_star, rel=1e-4
        )

    # -- the multistart behind the approximate policy --

    def test_reports_multistart_convergence(self, model):
        """The multistart records how many starts actually converged."""
        model.pure_power_trigger_capacity_phi()
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
            model.pure_power_trigger_capacity_phi()

    def test_objective_rejects_out_of_bounds_log_K(self, model):
        """The bound guard fires before exp(log_K) is ever formed."""
        assert model._objective_K_phi(np.array([1e4, 0.5])) == 1e20
        assert model._objective_K_phi(np.array([-1e4, 0.5])) == 1e20
