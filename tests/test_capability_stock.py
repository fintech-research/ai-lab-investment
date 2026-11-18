"""Tests for the capability-stock and late-entry prototypes (issue #174)."""

import numpy as np
import pytest
from scipy import integrate, special

from ai_lab_investment.models.base_model import SingleFirmModel
from ai_lab_investment.models.capability_stock import (
    LAMBDA_GRID,
    CapabilityStockModel,
    StockSpec,
    accumulating_stock_premium,
    belief_mismatch,
    follower_allocation_slope,
    interior_window,
    pure_power_policy,
    revenue_coeff,
    revisable_stock_allocation,
    specification_table,
    stock_regime,
    training_fraction,
)
from ai_lab_investment.models.duopoly import DuopolyModel
from ai_lab_investment.models.parameters import ModelParameters
from ai_lab_investment.models.piecewise_option import (
    PiecewiseOptionModel,
    reduced_form_reference,
)

THETA_80 = StockSpec.late_entry_discount(0.80)
THETA_50 = StockSpec.late_entry_discount(0.50)
KAPPA_20 = StockSpec.pre_positioned(0.20)
KAPPA_50 = StockSpec.pre_positioned(0.50)
STOCK = StockSpec.accumulating_stock()
STRICT_F = StockSpec.late_entry_discount(0.0, fixed_cost=0.002)


@pytest.fixture(scope="module")
def params():
    return ModelParameters()


@pytest.fixture(scope="module")
def paper(params):
    return CapabilityStockModel(params)


@pytest.fixture(scope="module")
def piecewise(params):
    return PiecewiseOptionModel(params)


@pytest.fixture(scope="module")
def reduced(params):
    return reduced_form_reference(params)


def _solve(params, spec, **changes):
    return CapabilityStockModel(params.with_param(**changes), spec)


def _lcp_check(model):
    """Brennan--Schwartz boundary and value at the model's own policy."""
    pol = model.policy
    lo, hi = model.lcp._envelope_grid_range()
    grid, values, boundary = model.lcp.finite_difference_value(
        pol.K_star, pol.phi_star, 8001, lo, hi, scale="envelope"
    )
    X_0 = 0.5 * pol.X_star
    value = float(np.interp(np.log(X_0), np.log(grid), values))
    return boundary, value, model.value(X_0)


class TestNestsThePaper:
    """theta = 1 with no other change is the paper's exact problem."""

    def test_late_entry_problem_is_the_h_regime_problem(self, paper, piecewise):
        assert paper.late_trigger == pytest.approx(piecewise.X_H, rel=1e-6)
        assert paper.late_capacity == pytest.approx(piecewise.K_H, rel=1e-6)
        assert paper.late_coeff == pytest.approx(piecewise.B_H, rel=1e-6)

    def test_adapter_carries_the_parent_coefficients(self, paper, piecewise):
        for name in ("C", "g", "k", "a_H", "b_H", "X_H"):
            assert getattr(paper.lcp, name) == pytest.approx(
                getattr(piecewise, name), rel=1e-6
            )

    def test_adapter_reproduces_the_precommitted_solution(
        self, paper, piecewise, reduced
    ):
        K, phi = reduced["K_star"], reduced["phi_star"]
        ours, theirs = paper.lcp.solve(K, phi), piecewise.solve(K, phi)
        assert ours.X_star == pytest.approx(theirs.X_star, rel=1e-6)
        assert ours.X_star == pytest.approx(0.007220, abs=1e-6)
        X_0 = 0.5 * reduced["X_star"]
        assert paper.lcp.pure_switching_value(X_0) == pytest.approx(
            piecewise.pure_switching_value(X_0), rel=1e-6
        )
        assert paper.lcp.threshold_value(
            K, phi, reduced["X_star"], X_0
        ) == pytest.approx(1.615102e-3, rel=1e-5)

    def test_baseline_never_invests_before_the_switch(self, paper):
        assert paper.regime() == "never"
        assert not np.isfinite(paper.policy.X_star)
        assert paper.joint_lcp()["kind"] == "never"

    def test_waiting_value_matches_the_envelope_finite_differences(
        self, paper, piecewise, reduced
    ):
        """Quadrature against the finite-difference pure switching value."""
        K, phi = reduced["K_star"], reduced["phi_star"]
        X_0 = 0.5 * reduced["X_star"]
        fd = piecewise.envelope_threshold_value(K, phi, np.inf, X_0, n_grid=4001)
        assert paper.waiting_value(X_0) == pytest.approx(fd, rel=1e-4)
        assert paper.waiting_value(X_0) == pytest.approx(1.7414e-3, rel=1e-4)

    def test_paper_policy_value_matches_the_envelope_finite_differences(
        self, paper, piecewise, reduced
    ):
        K, phi, X_star = reduced["K_star"], reduced["phi_star"], reduced["X_star"]
        X_0 = 0.5 * X_star
        fd = piecewise.envelope_threshold_value(K, phi, X_star, X_0)
        assert paper.policy_value(K, phi, X_star, X_0) == pytest.approx(fd, rel=1e-4)
        assert fd == pytest.approx(1.6215e-3, rel=1e-4)

    def test_low_arrival_rate_trigger_of_the_appendix(self, params):
        """Internet Appendix B: at lam = 0.05, X* = 0.0173 with K = 0.029."""
        pol = _solve(params, StockSpec(), lam=0.05).policy
        assert pol.status == "interior"
        assert pol.X_star == pytest.approx(0.0173, abs=1e-4)
        assert pol.K_star == pytest.approx(0.029, abs=1e-3)
        assert not pol.algebraic

    def test_unrestricted_dilemma_of_the_appendix(self, params):
        """Internet Appendix B: 42.7% at belief 0.02, 1.0% at 0.05, 0 above."""
        out = belief_mismatch(params, StockSpec(), lambda_invest=(0.02, 0.05, 0.20))
        assert out["X_0"] == pytest.approx(0.5 * 0.004722, rel=1e-3)
        assert out["loss_pct"] == pytest.approx([42.66, 0.986, 0.0], abs=0.02)

    def test_pure_power_at_beta_h_is_the_reduced_model(self, params, reduced):
        X, K, phi = pure_power_policy(params, beta=params.beta_H)
        assert pytest.approx(reduced["X_star"], rel=1e-6) == X
        assert pytest.approx(reduced["K_star"], rel=1e-6) == K
        assert phi == pytest.approx(reduced["phi_star"], rel=1e-6)
        p, b = params, params.beta_H
        closed = (
            p.delta
            * (p.alpha * b - b + 1.0)
            / (p.r * p.c * (p.gamma * (b - 1.0) - p.alpha * b))
        ) ** (1.0 / (p.gamma - 1.0))
        assert pytest.approx(closed, rel=1e-9) == K

    def test_training_fraction_is_the_paper_closed_form(self, params, paper):
        expected = SingleFirmModel(params).closed_form_phi_star()
        assert paper.phi_star == pytest.approx(expected, rel=1e-12)
        assert paper.g_star == pytest.approx(
            SingleFirmModel(params)._effective_revenue_coeff_single(expected, 1.0),
            rel=1e-12,
        )

    def test_faith_thresholds_are_the_paper_thresholds(self, params, paper):
        duo = DuopolyModel(params)
        assert paper.faith_threshold() == pytest.approx(duo.faith_threshold(), abs=1e-6)
        assert paper.faith_threshold(exact=True) == pytest.approx(
            duo.faith_threshold_exact(), abs=1e-6
        )


class TestLateEntryDiscount:
    """Specification 2."""

    def test_cutoff_above_which_the_firm_never_invests_early(self, params):
        bounds = [
            _solve(params, StockSpec(), lam=lam).theta_bounds() for lam in LAMBDA_GRID
        ]
        assert [b[1] for b in bounds] == pytest.approx(
            [1.587, 1.162, 0.928, 0.887, 0.923], abs=1e-3
        )
        assert all(b[0] == 0.0 for b in bounds)
        assert stock_regime(params, StockSpec.late_entry_discount(0.92)) == "interior"
        assert stock_regime(params, StockSpec.late_entry_discount(0.93)) == "never"

    def test_no_late_entry_means_immediate_investment(self, params):
        """theta = 0 at baseline: no trigger and no interior scale, by (A3)."""
        model = _solve(params, StockSpec.late_entry_discount(0.0))
        assert model.regime() == "immediate"
        assert model.policy.X_star == 0.0
        assert model.joint_lcp()["kind"] == "all"
        with pytest.raises(RuntimeError, match="No interior capacity"):
            pure_power_policy(params)

    @pytest.mark.parametrize(
        ("spec", "X_star", "K_star", "algebraic"),
        [(THETA_80, 7.404e-3, 1.196e-2, False), (THETA_50, 3.448e-5, 3.535e-6, True)],
    )
    def test_baseline_policy(self, params, spec, X_star, K_star, algebraic):
        pol = _solve(params, spec).policy
        assert pol.status == "interior"
        assert pol.X_star == pytest.approx(X_star, rel=1e-3)
        assert pol.K_star == pytest.approx(K_star, rel=1e-3)
        assert pol.algebraic is algebraic
        assert pol.phi_star == pytest.approx(0.70086, abs=1e-5)

    @pytest.mark.parametrize("spec", [THETA_80, THETA_50])
    def test_stopping_region_by_two_independent_solvers(self, params, spec):
        model = _solve(params, spec)
        boundary, fd_value, value = _lcp_check(model)
        assert boundary == pytest.approx(model.policy.X_star, rel=3e-3)
        assert fd_value == pytest.approx(value, rel=1e-4)
        joint = model.joint_lcp()
        assert joint["kind"] == "upper"
        assert joint["boundary"] == pytest.approx(model.policy.X_star, rel=5e-3)
        assert joint["capacity"] == pytest.approx(model.policy.K_star, rel=1e-2)

    def test_capacity_by_search_over_brennan_schwartz_solves(self, params):
        """K* against the parent's search over capacity, one LCP per K."""
        model = _solve(params, THETA_80)
        pol = model.policy
        bounds = (np.log(pol.K_star) - 2.0, np.log(pol.K_star) + 2.0)
        K, boundary, value = model.lcp.envelope_optimal_capacity(
            pol.phi_star, 0.5 * pol.X_star, log_K_bounds=bounds
        )
        assert pytest.approx(pol.K_star, rel=1e-2) == K
        assert boundary == pytest.approx(pol.X_star, rel=1e-2)
        assert value == pytest.approx(model.value(0.5 * pol.X_star), rel=1e-4)

    def test_trigger_below_the_search_range_means_immediate_investment(self, params):
        """A trigger below the smallest capacity searched is reported as
        immediate investment (issue #182), not as an error: the firm is in
        its investment region at every demand level of interest."""
        model = _solve(params, StockSpec.late_entry_discount(0.005))
        assert model.regime() == "interior"
        policy = model.policy
        assert policy.status == "immediate"
        assert policy.X_star == 0.0
        assert np.isnan(policy.K_star)
        X = 0.01
        assert model.value(X) == pytest.approx(float(model.exercise_envelope(X)[0]))

    def test_trigger_and_capacity_are_hump_shaped_in_beliefs(self, params):
        rows = specification_table(THETA_80, params)
        X = [row["X_star"] for row in rows]
        K = [row["K_star"] for row in rows]
        assert X[0] < X[1] < X[2] > X[3] > X[4]
        assert K[0] < K[1] < K[2] > K[3] > K[4]
        assert max(K) / min(K) > 1000.0

    def test_levels_are_hypersensitive_to_theta(self, params):
        """d ln K / d ln theta = 1 / [1 - (1 - alpha) beta_H] below X_H."""
        low = _solve(params, StockSpec.late_entry_discount(0.50)).policy.K_star
        high = _solve(params, StockSpec.late_entry_discount(0.505)).policy.K_star
        elasticity = np.log(high / low) / np.log(1.01)
        exact = 1.0 / (1.0 - (1.0 - params.alpha) * params.beta_H)
        assert exact == pytest.approx(14.64, abs=0.01)
        assert elasticity == pytest.approx(exact, rel=0.01)

    def test_window_is_not_wider_than_a2(self, params):
        a2_r = interior_window("r", 0.05, 0.40, None, params)
        a2_alpha = interior_window("alpha", 0.05, 0.95, None, params)
        assert a2_r == pytest.approx((0.0973, 0.1347), abs=2e-4)
        assert a2_alpha == pytest.approx((0.3560, 0.5340), abs=2e-4)
        assert interior_window("r", 0.05, 0.40, THETA_50, params) == pytest.approx(
            a2_r, abs=2e-4
        )
        assert interior_window("alpha", 0.05, 0.95, THETA_50, params) == pytest.approx(
            a2_alpha, abs=2e-4
        )
        shifted = interior_window("r", 0.05, 0.40, THETA_80, params)
        assert shifted == pytest.approx((0.0973, 0.1409), abs=2e-4)
        narrower = interior_window("alpha", 0.05, 0.95, THETA_80, params)
        assert narrower == pytest.approx((0.3560, 0.4725), abs=2e-4)

    def test_above_the_a2_upper_bound_the_paper_problem_has_a_trigger(self, params):
        """At r = 0.15 the entrant invests at once and theta = 1 is interior."""
        model = _solve(params, StockSpec(), r=0.15)
        assert model.late_trigger == 0.0
        assert model.theta_bounds() == pytest.approx((0.849, 1.102), abs=1e-3)
        assert model.policy.X_star == pytest.approx(0.01905, rel=1e-3)
        joint = model.joint_lcp()
        assert joint["kind"] == "upper"
        assert joint["boundary"] == pytest.approx(model.policy.X_star, rel=5e-3)
        below = _solve(params, StockSpec.late_entry_discount(0.80), r=0.15)
        assert below.regime() == "immediate"
        assert below.joint_lcp()["kind"] == "all"

    def test_ill_posed_below_the_a2_lower_bound(self, params):
        with pytest.raises(RuntimeError, match="lower bound of"):
            _solve(params, THETA_50, r=0.09)
        assert stock_regime(params.with_param(r=0.09), THETA_50) == "ill-posed"

    def test_free_reallocation_still_empties_pre_switch_training(self, params):
        """theta leaves the incumbent's technology alone (comment C2)."""
        assert training_fraction(params, StockSpec(theta=0.5, redeploy=1.0)) == 0.0


class TestPrePositionedCapability:
    """Specification 1."""

    def test_training_fraction_closed_form(self, params):
        assert training_fraction(params, KAPPA_20) == pytest.approx(0.5860, abs=1e-4)
        assert training_fraction(params, KAPPA_50) == pytest.approx(0.1922, abs=1e-4)
        assert training_fraction(params, StockSpec.pre_positioned(0.60)) == 0.0
        assert training_fraction(params, StockSpec.pre_positioned(1.0)) == 0.0
        assert (
            training_fraction(
                params.with_param(lam=0.03), StockSpec.pre_positioned(0.25)
            )
            == 0.0
        )

    @pytest.mark.parametrize("spec", [StockSpec(), KAPPA_20, KAPPA_50, STOCK])
    def test_training_fraction_maximizes_the_revenue_coefficient(self, params, spec):
        grid = np.linspace(0.0, 0.999, 4000)
        best = grid[np.argmax([revenue_coeff(params, spec, x) for x in grid])]
        assert training_fraction(params, spec) == pytest.approx(best, abs=5e-4)

    def test_strict_stock_is_degenerate(self, params):
        assert stock_regime(params, StockSpec.pre_positioned(0.0)) == "immediate"

    @pytest.mark.parametrize("kappa", [0.2, 0.5, 1.0])
    def test_finite_trigger_at_every_belief(self, params, kappa):
        rows = specification_table(StockSpec.pre_positioned(kappa), params)
        assert all(row["status"] == "interior" for row in rows)
        assert all(row["algebraic"] for row in rows)

    def test_baseline_policy_and_stopping_region(self, params):
        model = _solve(params, KAPPA_20)
        pol = model.policy
        assert pol.X_star == pytest.approx(1.5207e-6, rel=1e-3)
        assert pol.K_star == pytest.approx(2.0754e-8, rel=1e-3)
        boundary, fd_value, value = _lcp_check(model)
        assert boundary == pytest.approx(pol.X_star, rel=3e-3)
        assert fd_value == pytest.approx(value, rel=1e-4)
        assert model.joint_lcp()["kind"] == "upper"

    def test_faith_threshold_closed_form(self, params):
        p = params
        omega = ((p.r - p.mu_H) / (p.r - p.mu_L)) ** (1.0 / p.alpha)
        model = _solve(params, KAPPA_20)
        assert model.faith_threshold() == pytest.approx(
            (omega - 0.2) / (omega + 0.8), abs=1e-5
        )
        assert model.faith_threshold(exact=True) == pytest.approx(0.216, abs=1e-3)
        assert _solve(params, KAPPA_50).faith_threshold() == 0.0

    @pytest.mark.parametrize("spec", [StockSpec(), KAPPA_20, KAPPA_50])
    def test_role_invariance_critical_point(self, params, spec):
        phi = training_fraction(params, spec)
        args = (0.26, phi, 0.0067)
        assert follower_allocation_slope(params, spec, phi, *args) == pytest.approx(
            0.0, abs=1e-12
        )
        assert follower_allocation_slope(params, spec, phi - 0.05, *args) > 0.0
        assert follower_allocation_slope(params, spec, phi + 0.05, *args) < 0.0

    def test_default_boundary_is_the_paper_formula(self, params, paper):
        K, phi = 0.0067, 0.70
        duo = DuopolyModel(params, leverage=0.40)
        coupon = duo.coupon_payment(K)
        expected = duo.default_boundary(phi, K, phi, 0.0)
        assert paper.default_boundary(K, phi, coupon) == pytest.approx(expected)
        lower = _solve(params, KAPPA_20).default_boundary(K, phi, coupon)
        assert lower < expected


class TestAccumulatingStock:
    """Specification 3."""

    def test_head_start_factor_against_direct_integration(self, params):
        p = params
        rho, eta = p.r - p.mu_L + p.lam, p.r - p.mu_H
        direct, _ = integrate.quad(
            lambda a: (
                np.exp(-(rho - eta) * a)
                * special.gammaincc(1.0 + p.alpha, eta * a)
                / eta
            ),
            0.0,
            400.0,
            epsabs=0.0,
            epsrel=1e-11,
            limit=400,
        )
        premium = accumulating_stock_premium(params)
        assert premium == pytest.approx(1.15766, abs=1e-5)
        assert premium == pytest.approx(direct * rho / p.A_H, rel=1e-8)

    def test_finite_trigger_at_every_belief_and_rising_in_it(self, params):
        rows = specification_table(STOCK, params)
        assert all(row["status"] == "interior" for row in rows)
        X = [row["X_star"] for row in rows]
        assert sorted(X) == X
        assert X[2] == pytest.approx(0.04026, rel=1e-3)
        assert X[2] / rows[2]["late_trigger"] == pytest.approx(14.5, abs=0.1)
        assert rows[2]["phi_star"] == pytest.approx(0.7494, abs=1e-4)

    def test_stopping_region(self, params):
        model = _solve(params, STOCK)
        boundary, fd_value, value = _lcp_check(model)
        assert boundary == pytest.approx(model.policy.X_star, rel=3e-3)
        assert fd_value == pytest.approx(value, rel=1e-4)
        assert model.joint_lcp()["kind"] == "upper"

    def test_not_robust_across_the_admissible_window(self, params):
        for change in ({"r": 0.10}, {"alpha": 0.45}, {"gamma": 1.15}, {"sigma": 0.38}):
            assert stock_regime(params.with_param(**change), STOCK) == "never"
        assert interior_window("r", 0.05, 0.40, STOCK, params) == pytest.approx(
            (0.1079, 0.1486), abs=2e-4
        )

    def test_revisable_allocation(self, params):
        out = {
            lam: revisable_stock_allocation(params.with_param(lam=lam))
            for lam in LAMBDA_GRID
        }
        assert out[0.10]["lam_min"] == pytest.approx(0.07333, abs=1e-5)
        assert out[0.03]["phi"] == 0.0
        assert out[0.05]["phi"] == 0.0
        assert out[0.10]["phi"] == pytest.approx(0.0154, abs=5e-4)
        assert out[0.20]["phi"] == pytest.approx(0.1677, abs=5e-4)
        assert out[0.50]["phi"] == pytest.approx(0.4101, abs=5e-4)
        assert out[0.10]["phi_frozen"] == pytest.approx(0.7494, abs=1e-4)

    def test_static_contest_does_not_apply(self, params):
        with pytest.raises(ValueError, match="static contest"):
            follower_allocation_slope(params, STOCK, 0.7, 1.0, 0.7, 1.0)


class TestFixedCost:
    """Specification 4."""

    def test_strict_stock_is_a_pure_power_problem(self, params):
        model = _solve(params, STRICT_F)
        pol = model.policy
        assert (pol.X_star, pol.K_star) == pytest.approx(
            (4.7838e-3, 6.8424e-3), rel=1e-4
        )
        b = model.beta_pos
        markup = b / (b - 1.0) * model.total_cost(pol.K_star)
        assert pol.X_star == pytest.approx(
            markup / (model.g_star * pol.K_star**params.alpha), rel=1e-9
        )
        assert pure_power_policy(params, fixed_cost=0.002) == pytest.approx(
            (pol.X_star, pol.K_star, pol.phi_star), rel=1e-9
        )
        assert model.waiting_value(1.0) == 0.0
        X_0 = 0.5 * pol.X_star
        npv = model.exercise_payoff(pol.K_star, pol.phi_star, pol.X_star)
        assert model.value(X_0) == pytest.approx(npv * 0.5**b, rel=1e-9)

    def test_stopping_region(self, params):
        model = _solve(params, STRICT_F)
        boundary, fd_value, value = _lcp_check(model)
        assert boundary == pytest.approx(model.policy.X_star, rel=3e-3)
        assert fd_value == pytest.approx(value, rel=1e-4)
        assert model.joint_lcp()["kind"] == "upper"

    def test_trigger_and_capacity_fall_in_beliefs(self, params):
        rows = specification_table(STRICT_F, params)
        X = [row["X_star"] for row in rows]
        K = [row["K_star"] for row in rows]
        assert sorted(X, reverse=True) == X
        assert sorted(K, reverse=True) == K
        assert K[0] / K[-1] == pytest.approx(1.57, abs=0.01)

    def test_fixed_cost_removes_the_hypersensitivity(self, params):
        def capacity(spec):
            return _solve(params, spec).policy.K_star

        in_f = np.log(
            capacity(StockSpec.late_entry_discount(0.0, 0.00202)) / capacity(STRICT_F)
        ) / np.log(1.01)
        in_theta = np.log(
            capacity(StockSpec.late_entry_discount(0.505, 0.002))
            / capacity(StockSpec.late_entry_discount(0.50, 0.002))
        ) / np.log(1.01)
        assert in_f == pytest.approx(0.82, abs=0.02)
        assert in_theta == pytest.approx(1.07, abs=0.05)

    def test_fixed_cost_is_large_at_the_optimum(self, params):
        model = _solve(params, STRICT_F)
        share = 0.002 / model.total_cost(model.policy.K_star)
        assert share == pytest.approx(0.47, abs=0.01)

    @pytest.mark.parametrize(
        "change", [{"r": 0.18}, {"alpha": 0.30}, {"r": 0.09}, {"alpha": 0.70}]
    )
    def test_interior_outside_a2(self, params, change):
        model = _solve(params, STRICT_F, **change)
        assert model.policy.status == "interior"
        joint = model.joint_lcp()
        assert joint["kind"] == "upper"
        assert joint["boundary"] == pytest.approx(model.policy.X_star, rel=5e-3)

    def test_window(self, params):
        assert interior_window("r", 0.07, 0.40, STRICT_F, params) == (0.07, 0.40)
        assert interior_window("alpha", 0.05, 0.95, STRICT_F, params) == (0.05, 0.95)
        with_entry = StockSpec.pre_positioned(0.20, 0.002)
        r_lo, r_hi = interior_window("r", 0.07, 0.40, with_entry, params)
        assert (r_lo, r_hi) == pytest.approx((0.0973, 0.40), abs=2e-4)


class TestBeliefMismatch:
    """Dario's dilemma at beliefs 0.02, 0.18, 0.20, 0.50 against a true 0.10."""

    @pytest.mark.parametrize(
        ("spec", "losses"),
        [
            (THETA_80, [27.27, 1.43, 3.01, 23.11]),
            (THETA_50, [29.77, 3.26, 5.54, 28.51]),
            (KAPPA_20, [20.83, 2.15, 3.47, 28.77]),
            (KAPPA_50, [4.03, 1.34, 1.70, 18.13]),
            (STOCK, [24.93, 0.46, 0.47, 0.49]),
            (STRICT_F, [46.06, 26.56, 38.88, 270.80]),
        ],
    )
    def test_losses(self, params, spec, losses):
        out = belief_mismatch(params, spec)
        assert out["loss_pct"] == pytest.approx(losses, abs=0.05)
        additive = out["loss_pct"][0] / out["loss_pct"][1]
        assert additive > 1.0

    def test_proportional_ranking_depends_on_the_specification(self, params):
        def ratio(spec):
            loss = belief_mismatch(params, spec)["loss_pct"]
            return loss[0] / loss[3]

        assert ratio(THETA_80) == pytest.approx(1.18, abs=0.01)
        assert ratio(KAPPA_20) < 1.0
        assert ratio(STRICT_F) < 0.2
        assert ratio(STOCK) > 40.0

    def test_strict_stock_losses_do_not_depend_on_the_reference_demand(self, params):
        base = belief_mismatch(params, STRICT_F)
        lower = belief_mismatch(params, STRICT_F, x0_ratio=0.25)
        assert lower["loss_pct"] == pytest.approx(base["loss_pct"], rel=1e-9)

    def test_true_policy_has_no_loss(self, params):
        out = belief_mismatch(params, THETA_80, lambda_invest=(0.10,))
        assert out["loss_pct"] == pytest.approx([0.0], abs=1e-9)


class TestValidation:
    @pytest.mark.parametrize(
        "kwargs",
        [
            {"theta": 1.2},
            {"late_training": -0.1},
            {"redeploy": 2.0},
            {"fixed_cost": -1.0},
        ],
    )
    def test_spec_rejects_out_of_range_primitives(self, kwargs):
        with pytest.raises(ValueError, match="must"):
            StockSpec(**kwargs)

    def test_window_reports_a_non_interior_baseline(self, params):
        window = interior_window("r", 0.05, 0.40, StockSpec(), params)
        assert np.isnan(window[0])
        assert np.isnan(window[1])

    def test_late_entry_value_is_continuous_at_the_trigger(self, params):
        model = _solve(params, THETA_80)
        x = model.late_trigger
        below, above = model.late_entry_value([x * (1 - 1e-9), x * (1 + 1e-9)])
        assert below == pytest.approx(above, rel=1e-7)
        assert model.late_entry_value(x)[0] == pytest.approx(
            0.8 * PiecewiseOptionModel(params).regime_H_option_value(x), rel=1e-6
        )
