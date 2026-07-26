"""Tests for the exact piecewise L-regime stopping problem."""

import numpy as np
import pytest

from ai_lab_investment.models.parameters import ModelParameters
from ai_lab_investment.models.piecewise_option import (
    PiecewiseOptionModel,
    dilemma_bias,
    piecewise_bias,
    reduced_form_reference,
    smooth_fit_trigger,
)


@pytest.fixture
def default_params():
    return ModelParameters()


@pytest.fixture
def model(default_params):
    return PiecewiseOptionModel(default_params)


@pytest.fixture
def reduced(default_params):
    return reduced_form_reference(default_params)


@pytest.fixture
def fixed_policy_solution(model, reduced):
    return model.solve(reduced["K_star"], reduced["phi_star"])


@pytest.fixture(scope="module")
def baseline_bias():
    return piecewise_bias(ModelParameters())


@pytest.fixture(scope="module")
def baseline_dilemma():
    return dilemma_bias(ModelParameters(), lambda_invest_values=(0.02, 0.20))


class TestSetup:
    def test_baseline_trigger_ordering(self, model, reduced):
        """The paper's trigger lies above the H-regime trigger, so the exact
        continuation problem is genuinely two-region."""
        assert pytest.approx(0.002783, abs=1e-5) == model.X_H
        assert reduced["X_star"] == pytest.approx(0.004722, abs=1e-5)
        assert reduced["X_star"] > model.X_H

    def test_coefficient_gap(self, model, reduced):
        """Forced-ODE coefficient C ~ 21.14 vs smooth-fit level ~ 16.52."""
        assert pytest.approx(21.14, abs=0.01) == model.C
        assert reduced["smooth_fit_coeff"] == pytest.approx(16.52, abs=0.01)

    def test_h_regime_payoff_matches_option_at_trigger(self, model):
        """Value matching of the H-regime problem: a_H X_H - b_H = B_H X_H^h."""
        exercised = model.a_H * model.X_H - model.b_H
        option = model.B_H * model.X_H**model.beta_H
        assert exercised == pytest.approx(option, rel=1e-12)


class TestReducedFormConsistency:
    def test_pure_power_boundary_conditions_reproduce_eq_trigger_phi(
        self, default_params, reduced
    ):
        """With the pure-power continuation value and A_1 = 0, value matching
        and smooth pasting return the paper's closed-form trigger."""
        X = smooth_fit_trigger(default_params, reduced["K_star"], reduced["phi_star"])
        assert pytest.approx(reduced["X_star"], rel=1e-12) == X

    def test_smooth_fit_level_prices_the_paper_policy(self, reduced, default_params):
        npv = reduced["a_L"] * reduced["X_star"] - reduced["b_L"]
        level = npv / reduced["X_star"] ** default_params.beta_H
        assert level == pytest.approx(reduced["smooth_fit_coeff"], rel=1e-12)


class TestPiecewiseSolution:
    def test_boundary_conditions_hold(self, fixed_policy_solution):
        """Value matching and smooth pasting at X*, C^1 matching at X_H*."""
        sol = fixed_policy_solution
        eps = sol.X_star * 1e-7
        assert sol.value(sol.X_star) == pytest.approx(
            sol.a_L * sol.X_star - sol.b_L, rel=1e-12
        )
        slope = (sol.value(sol.X_star) - sol.value(sol.X_star - eps)) / eps
        assert slope == pytest.approx(sol.a_L, rel=1e-5)

        X_H, p_pos, n, h = sol.X_H, sol.beta_L_pos, sol.beta_L_neg, sol.beta_H
        lower = sol.A_1 * X_H**p_pos + sol.C * X_H**h
        upper = sol.D_1 * X_H**p_pos + sol.D_2 * X_H**n + sol.g * X_H + sol.k
        assert lower == pytest.approx(upper, rel=1e-10)
        slope_lo = p_pos * sol.A_1 * X_H ** (p_pos - 1) + h * sol.C * X_H ** (h - 1)
        slope_hi = (
            p_pos * sol.D_1 * X_H ** (p_pos - 1) + n * sol.D_2 * X_H ** (n - 1) + sol.g
        )
        assert slope_lo == pytest.approx(slope_hi, rel=1e-10)

    def test_ode_residual_is_zero_in_each_region(
        self, model, fixed_policy_solution, default_params
    ):
        """The closed form solves the forced Euler ODE on both intervals."""
        sol = fixed_policy_solution
        p = default_params
        for X in [0.5 * sol.X_H, 0.9 * sol.X_H, 1.2 * sol.X_H, 0.9 * sol.X_star]:
            step = X * 1e-5
            f0 = sol.value(X)
            f1 = (sol.value(X + step) - sol.value(X - step)) / (2 * step)
            f2 = (sol.value(X + step) - 2 * f0 + sol.value(X - step)) / step**2
            resid = (
                0.5 * p.sigma**2 * X**2 * f2
                + p.mu_L * X * f1
                - (p.r + p.lam) * f0
                + p.lam * model.regime_H_option_value(X)
            )
            assert abs(resid) < 1e-6 * abs(f0)

    def test_dominates_payoff_and_is_increasing(self, fixed_policy_solution):
        sol = fixed_policy_solution
        grid = np.geomspace(1e-5, sol.X_star * 1.5, 2000)
        vals = np.array([sol.value(x) for x in grid])
        assert np.all(np.diff(vals) > 0)
        assert np.all(vals >= sol.a_L * grid - sol.b_L - 1e-15)

    def test_dominates_pure_switching_and_reduced_form(
        self, model, fixed_policy_solution, reduced, default_params
    ):
        """The exact value dominates both the replication bound (never
        exercise in L) and the reduced-form smooth-fit level."""
        sol = fixed_policy_solution
        grid = np.geomspace(1e-5, sol.X_star, 1000)
        vals = np.array([sol.value(x) for x in grid])
        switching = np.array([model.pure_switching_value(x) for x in grid])
        reduced_vals = np.where(
            grid < reduced["X_star"],
            reduced["smooth_fit_coeff"] * grid**default_params.beta_H,
            sol.a_L * grid - sol.b_L,
        )
        assert np.all(vals >= switching - 1e-14)
        assert np.all(vals >= reduced_vals - 1e-14)

    def test_pure_switching_bound_is_below_C_power(self, model, default_params):
        """C X^{beta_H} is *not* the replication bound: above X_H* the
        H-regime option is exercised, so the true forcing is smaller and the
        pure-switching value lies strictly below C X^{beta_H}."""
        grid = np.geomspace(1e-4, model.X_H * 0.99, 200)
        switching = np.array([model.pure_switching_value(x) for x in grid])
        power = model.C * grid**default_params.beta_H
        assert np.all(switching < power)
        assert model.pure_switching_coeffs()[0] < 0.0

    def test_exercise_premium_exceeds_the_replication_bound(
        self, model, fixed_policy_solution
    ):
        """A_1 is not signed relative to zero, but it must exceed the
        pure-switching coefficient: exercising in L is worth something."""
        assert model.pure_switching_coeffs()[0] < fixed_policy_solution.A_1
        assert fixed_policy_solution.A_1 < 0.0

    def test_smooth_pasting_maximizes_threshold_value(
        self, model, fixed_policy_solution, reduced
    ):
        """The free boundary is the value-maximizing threshold policy."""
        sol = fixed_policy_solution
        X_0 = 0.5 * reduced["X_star"]
        thresholds = np.linspace(sol.X_star * 0.6, sol.X_star * 1.5, 200)
        values = np.array([
            model.threshold_value(reduced["K_star"], reduced["phi_star"], b, X_0)
            for b in thresholds
        ])
        assert thresholds[np.argmax(values)] == pytest.approx(sol.X_star, rel=0.02)
        assert values.max() == pytest.approx(sol.value(X_0), rel=1e-6)


class TestFiniteDifferenceVerification:
    def test_matches_brennan_schwartz_solution(
        self, model, fixed_policy_solution, reduced
    ):
        """Independent LCP solve reproduces the closed-form value and free
        boundary."""
        sol = fixed_policy_solution
        X, F, boundary = model.finite_difference_value(
            reduced["K_star"], reduced["phi_star"], n_grid=40001
        )
        assert boundary == pytest.approx(sol.X_star, rel=1e-3)
        for X_0 in [0.25 * sol.X_star, 0.5 * sol.X_star, 1.2 * model.X_H]:
            i = int(np.argmin(np.abs(X - X_0)))
            assert F[i] == pytest.approx(sol.value(X[i]), rel=1e-6)


class TestBaselineBias:
    """Pins the headline bias numbers of the piecewise-vs-reduced comparison.

    Mirrors TestCoupledDefaultBoundary in test_duopoly.py: if a model change
    moves these numbers, the appendix text quoting them must move too.
    """

    def test_trigger_and_value_bias(self, baseline_bias):
        b = baseline_bias
        assert b["X_star_piecewise_fixed"] == pytest.approx(0.007220, abs=1e-5)
        assert b["trigger_bias_fixed_pct"] == pytest.approx(52.9, abs=0.5)
        assert b["value_bias_fixed_pct"] == pytest.approx(19.1, abs=0.5)
        assert b["reported_value_bias_pct"] == pytest.approx(-14.8, abs=0.5)

    def test_reoptimized_policy(self, baseline_bias):
        b = baseline_bias
        assert b["trigger_bias_opt_pct"] == pytest.approx(96.1, abs=1.0)
        assert b["K_bias_opt_pct"] == pytest.approx(134.6, abs=2.0)
        # The training fraction is untouched by the convention: phi* maximizes
        # A_eff at fixed K in both the reduced and the exact problem.
        assert b["phi_piecewise_opt"] == pytest.approx(b["phi_reduced"], rel=1e-5)
        assert b["policy_loss_pct"] == pytest.approx(2.64, abs=0.15)


class TestLowLambdaBranch:
    def test_one_region_solution_at_low_lambda(self, default_params):
        """When the exact trigger falls below X_H* the problem collapses to
        the single-region case, where the pure-power forcing is exact."""
        params = default_params.with_param(lam=0.02)
        pw = PiecewiseOptionModel(params)
        sol = pw.optimal_policy(0.5 * reduced_form_reference(params)["X_star"])
        assert sol is not None
        assert not sol.two_region
        assert sol.D_1 == 0.0 and sol.D_2 == 0.0

    def test_convention_overstates_value_at_low_lambda(self, default_params):
        """At low arrival rates the beta_H discounting convention is too
        generous: the reduced form overstates its own policy's value."""
        b = piecewise_bias(default_params.with_param(lam=0.02))
        assert b["reported_value_bias_pct"] > 10.0
        assert b["trigger_bias_fixed_pct"] < 0.0


class TestDilemmaRecheck:
    def test_asymmetry_survives_exact_valuation(self, baseline_dilemma):
        d = baseline_dilemma
        i_low = d["lambda_invest"].index(0.02)
        i_high = d["lambda_invest"].index(0.20)
        # Conservative beliefs remain far costlier than aggressive ones, and
        # the asymmetry is larger than in the reduced form.
        assert d["loss_piecewise_pct"][i_low] > d["loss_piecewise_pct"][i_high]
        ratio_exact = d["loss_piecewise_pct"][i_low] / d["loss_piecewise_pct"][i_high]
        ratio_reduced = d["loss_reduced_pct"][i_low] / d["loss_reduced_pct"][i_high]
        assert ratio_exact > ratio_reduced
        assert d["loss_piecewise_pct"][i_low] == pytest.approx(39.8, abs=2.0)

    def test_training_fraction_unchanged(self, baseline_dilemma):
        d = baseline_dilemma
        for rf_phi, pw_phi in zip(d["phi_reduced"], d["phi_piecewise"], strict=True):
            assert pw_phi == pytest.approx(rf_phi, rel=1e-5)
