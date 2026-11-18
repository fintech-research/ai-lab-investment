"""Tests for the robustness sweeps of Internet Appendix E (issue #182)."""

import csv
import json
from math import inf, isfinite

import numpy as np
import pytest

from ai_lab_investment.models import ModelParameters
from ai_lab_investment.robustness import (
    DUOPOLY_GRID_PATH,
    DUOPOLY_JOINT_DRAWS,
    DUOPOLY_SIGN_LABELS,
    JOINT_DRAWS,
    JOINT_GRID_PATH,
    JOINT_SEED,
    SIGN_LABELS,
    SINGLE_FIRM_FIELDS,
    SWEEP_PARAMETERS,
    admissibility_failure,
    admissibility_window,
    capability_corner,
    capability_extension,
    duopoly_cells,
    duopoly_objects,
    evaluate_draw,
    format_joint_report,
    format_sweep_report,
    game_admissibility_failure,
    joint_scales,
    load_duopoly_grid,
    load_joint_grid,
    policy_elasticities,
    run_joint_sweep,
    run_sweep,
    single_firm_objects,
    summarize_sweep,
    write_sweep_csv,
)


@pytest.fixture
def params():
    return ModelParameters()


@pytest.fixture(scope="module")
def duopoly():
    return load_duopoly_grid()


class TestAdmissibility:
    def test_baseline_is_admissible(self, params):
        assert admissibility_failure(params) is None
        assert game_admissibility_failure(params) is None

    def test_alpha_minus_25_violates_a2(self, params):
        """alpha = 0.30 falls below the (A2) window (0.36, 0.53)."""
        failure = admissibility_failure(params.with_param(alpha=0.30))
        assert failure is not None
        assert "(A2) upper" in failure

    def test_r_plus_25_violates_a2(self, params):
        """r = 0.15 lies above the admissible window (0.097, 0.135)."""
        failure = admissibility_failure(params.with_param(r=0.15))
        assert failure is not None
        assert "(A2) upper" in failure

    def test_r_minus_25_violates_the_lower_bound(self, params):
        failure = admissibility_failure(params.with_param(r=0.09))
        assert failure is not None
        assert "(A2) lower" in failure

    def test_entry_game_needs_alpha_below_one_half(self, params):
        high = params.with_param(alpha=0.5)
        assert admissibility_failure(high) is None
        failure = game_admissibility_failure(high)
        assert failure is not None
        assert "alpha" in failure

    def test_window_of_the_model_of_record(self, params):
        """The window quoted in the calibration section and in Internet
        Appendix E: the one (A2) implies, because the post-switch scale
        problem is unchanged in the model of record. mu_L, lambda, delta and
        c do not enter (A2); the upper end for mu_L is the domain bound
        mu_L < mu_H."""
        window = admissibility_window(params)
        assert window["r"] == pytest.approx((0.0973, 0.1347), abs=5e-5)
        assert window["alpha"] == pytest.approx((0.3560, 0.5340), abs=5e-5)
        assert window["sigma"] == pytest.approx((0.1897, 0.3924), abs=5e-5)
        assert window["mu_H"] == pytest.approx((0.0512, 0.0766), abs=5e-5)
        assert window["gamma"][0] == pytest.approx(1.1235, abs=5e-5)
        assert window["gamma"][1] == inf
        for name in ("lam", "delta", "c"):
            assert window[name] == (0.0, inf)
        assert window["mu_L"][0] == 0.0
        assert window["mu_L"][1] == pytest.approx(params.mu_H, abs=1e-9)

    def test_window_edges_are_the_a2_bounds(self, params):
        """Just inside each edge (A2) holds and just outside it fails."""
        window = admissibility_window(params)
        for name, (low, high) in window.items():
            for edge, inward in ((low, 1.0), (high, -1.0)):
                if edge in (0.0, inf) or name == "mu_L":
                    continue
                inside = params.with_param(**{name: edge * (1.0 + 1e-6 * inward)})
                outside = params.with_param(**{name: edge * (1.0 - 1e-6 * inward)})
                assert admissibility_failure(inside) is None
                assert admissibility_failure(outside) is not None


class TestSingleFirmObjects:
    """The objects of one draw against the pins of the model of record."""

    @pytest.fixture(scope="class")
    def baseline(self):
        return single_firm_objects(ModelParameters())

    def test_policy(self, baseline):
        assert baseline["phi_star"] == pytest.approx(0.7009, abs=1e-4)
        assert baseline["phi_underbar"] == pytest.approx(0.1801, abs=1e-4)
        assert baseline["phi_tilde"] == pytest.approx(0.3219, abs=1e-4)
        assert baseline["X_star"] == pytest.approx(0.009258, rel=1e-3)
        assert baseline["K_star"] == pytest.approx(0.015784, rel=1e-3)
        assert baseline["waiting_margin"] == pytest.approx(1.0773, abs=1e-4)
        assert baseline["invests_before_switch"] == 0.0
        assert baseline["X_unrestricted"] == inf

    def test_dilemma_matches_the_paper_pairs(self, baseline):
        """tbl-dilemma-pairs: 32.5% against 1.3%, 13.3%, and the pairs
        (0.056, 0.18) and (0.069, 0.18); ratios 25, 2.4, 3.3 and 0.8."""
        assert baseline["pre_loss_low_levels"] == pytest.approx(0.3246, abs=1e-4)
        assert baseline["pre_loss_high_levels"] == pytest.approx(0.0132, abs=1e-4)
        assert baseline["pre_loss_high_log_far"] == pytest.approx(0.1325, abs=1e-4)
        assert baseline["pre_ratio_levels"] == pytest.approx(24.58, abs=0.01)
        assert baseline["pre_ratio_log_far"] == pytest.approx(2.450, abs=0.001)
        assert baseline["pre_ratio_log_near"] == pytest.approx(3.282, abs=0.001)
        assert baseline["pre_ratio_horizon"] == pytest.approx(0.776, abs=0.001)

    def test_unrestricted_version(self, baseline):
        """Scale chosen at the switch: the optimist waits and loses nothing."""
        assert baseline["unr_loss_low_levels"] == pytest.approx(0.4059, abs=1e-4)
        assert baseline["unr_loss_high_levels"] == 0.0
        assert baseline["unr_ratio_levels"] == inf

    def test_fields_are_complete(self, baseline):
        assert set(baseline) == set(SINGLE_FIRM_FIELDS)


class TestEvaluateDraw:
    @pytest.mark.parametrize("direction", ["-", "+"])
    def test_lambda_draws_are_admissible(self, params, direction):
        row = evaluate_draw(params, "lam", direction)
        assert row["admissible"]
        assert row["failure"] is None
        assert row["value"] == pytest.approx(
            params.lam * (0.75 if direction == "-" else 1.25)
        )
        assert row["pre_loss_low_levels"] > row["pre_loss_high_levels"]
        assert row["sign_faith"]
        assert row["sign_pre_levels"]

    def test_horizon_ranking_reverses_at_the_lower_arrival_rate(self, params):
        """At lambda = 0.075 the pessimist loses more in expected years too,
        the one sign reversal of the one-at-a-time sweep."""
        low = evaluate_draw(params, "lam", "-")
        high = evaluate_draw(params, "lam", "+")
        assert not low["sign_pre_horizon"]
        assert low["pre_ratio_horizon"] == pytest.approx(1.58, abs=0.01)
        assert high["sign_pre_horizon"]

    def test_inadmissible_draw_is_reported_not_dropped(self, params):
        """(A2) failures carry the failing condition, not silent truncation."""
        row = evaluate_draw(params, "alpha", "-")
        assert not row["admissible"]
        assert "(A2)" in row["failure"]
        assert "pre_loss_low_levels" not in row

    def test_parameter_domain_failure_is_reported(self, params):
        """mu_H above r violates Assumption 1 at construction time."""
        row = evaluate_draw(params, "mu_H", "+", perturbation=2.0)
        assert not row["admissible"]
        assert "(A1)" in row["failure"]

    def test_solver_failure_inside_the_window_is_reported(self, params):
        """gamma = 1.125 clears the lower bound of (A2) by 0.001 and the
        capacity optimum leaves the range searched."""
        row = evaluate_draw(params, "gamma", "-")
        assert not row["admissible"]
        assert row["failure"].startswith("solver failure")


class TestRunSweep:
    @pytest.fixture(scope="class")
    def rows(self):
        return run_sweep(parameters=("lam",))

    def test_row_layout(self, rows):
        assert [row["param"] for row in rows] == ["baseline", "lam", "lam"]
        assert [row["direction"] for row in rows] == ["0", "-", "+"]

    def test_summary_counts(self, rows):
        summary = summarize_sweep(rows)
        assert summary.n_draws == 2
        assert summary.n_admissible == 2
        assert summary.n_failed == 0
        assert summary.sign_counts["sign_pre_levels"] == 2
        assert summary.sign_violations["sign_pre_horizon"] == ["lam-"]
        assert summary.range("pre_ratio_levels")[0] > 1.0

    def test_report(self, rows):
        report = format_sweep_report(rows)
        assert "Qualitative statements across admissible draws" in report
        assert "fails at lam-" in report

    def test_csv_roundtrip(self, rows, tmp_path):
        path = write_sweep_csv(rows, tmp_path)
        assert path.parent == tmp_path
        assert "_UTC" in path.stem
        with path.open() as handle:
            records = list(csv.DictReader(handle))
        assert len(records) == len(rows)
        assert records[0]["param"] == "baseline"

    def test_default_parameter_set_covers_the_calibration(self):
        assert set(SWEEP_PARAMETERS) == {
            "r",
            "mu_L",
            "mu_H",
            "sigma",
            "lam",
            "alpha",
            "gamma",
            "delta",
            "c",
        }


class TestPaperNumbers:
    """Pin the one-at-a-time results quoted in Internet Appendix E."""

    @pytest.fixture(scope="class")
    def summary(self, duopoly):
        return summarize_sweep(run_sweep(duopoly=duopoly))

    def test_counts(self, summary):
        assert summary.n_draws == 18
        assert summary.n_admissible == 12
        assert summary.n_outside_window == 5
        assert summary.n_solver_failures == 1

    def test_failing_draws(self, summary):
        reasons = dict(summary.failures)
        assert set(reasons) == {"r-", "r+", "mu_H-", "sigma-", "alpha-", "gamma-"}
        assert "(A2) lower" in reasons["r-"]
        for name in ("r+", "mu_H-", "sigma-", "alpha-"):
            assert "(A2) upper" in reasons[name]
        assert reasons["gamma-"].startswith("solver failure")

    def test_sign_statements(self, summary):
        """Two reversals: at gamma = 1.875 the firm that chooses its scale
        at the switch invests before it, and at lambda = 0.075 the horizon
        ranking of the dilemma flips."""
        violations = {k: v for k, v in summary.sign_violations.items() if v}
        assert violations == {
            "sign_monopolist_waits": ["gamma+"],
            "sign_pre_horizon": ["lam-"],
        }

    def test_reported_ranges(self, summary):
        assert summary.range("phi_star") == pytest.approx((0.592, 0.791), abs=1e-3)
        assert summary.range("phi_underbar") == pytest.approx((0.097, 0.229), abs=1e-3)
        assert summary.range("phi_tilde") == pytest.approx((0.188, 0.369), abs=1e-3)
        assert summary.range("waiting_margin") == pytest.approx(
            (0.9965, 1.331), abs=1e-3
        )
        assert summary.range("pre_ratio_levels") == pytest.approx(
            (18.7, 27.5), abs=0.05
        )
        assert summary.range("pre_ratio_log_far") == pytest.approx(
            (1.77, 2.77), abs=0.01
        )
        assert summary.range("pre_ratio_log_near") == pytest.approx(
            (1.65, 7.22), abs=0.01
        )
        assert summary.range("pre_ratio_horizon") == pytest.approx(
            (0.46, 1.58), abs=0.01
        )
        assert summary.range("pre_loss_low_levels") == pytest.approx(
            (0.292, 0.416), abs=1e-3
        )
        assert summary.range("unr_loss_low_levels") == pytest.approx(
            (0.360, 0.531), abs=1e-3
        )

    def test_scale_parameters_leave_the_ratios_unchanged(self, duopoly):
        """delta and c only set the cost scale: every ratio and share is
        the baseline's, while the trigger and capacity move."""
        base = ModelParameters()
        reference = evaluate_draw(base, "lam", "0")
        for name in ("delta", "c"):
            for direction in ("-", "+"):
                row = evaluate_draw(base, name, direction, duopoly=duopoly)
                for key in ("phi_star", "waiting_margin", "pre_ratio_levels"):
                    assert row[key] == pytest.approx(reference[key], rel=1e-6)
                assert row["K_star"] != pytest.approx(reference["K_star"], rel=0.05)


class TestJointSweep:
    """The joint sweep: deterministic draws, the cache, the paper numbers."""

    @pytest.fixture(scope="class")
    def rows(self, duopoly):
        return load_joint_grid(duopoly)

    @pytest.fixture(scope="class")
    def summary(self, rows):
        return summarize_sweep(rows)

    def test_draws_are_deterministic(self):
        first, second = joint_scales(4), joint_scales(4)
        assert np.array_equal(first, second)
        assert first.shape == (16, len(SWEEP_PARAMETERS))
        assert first.min() >= 0.75
        assert first.max() <= 1.25
        # A shorter sequence is a prefix of a longer one.
        assert np.array_equal(joint_scales(6)[:16], first)

    def test_cache_metadata(self, rows):
        assert JOINT_SEED == 182
        assert JOINT_DRAWS == 4096
        assert JOINT_GRID_PATH.suffix == ".csv"
        assert len(rows) == JOINT_DRAWS

    def test_cache_holds_the_draws_of_the_sequence(self, rows):
        base = ModelParameters()
        scales = joint_scales()
        assert [row["draw"] for row in rows] == list(range(JOINT_DRAWS))
        for row in rows[:: JOINT_DRAWS // 64]:
            for name, scale in zip(SWEEP_PARAMETERS, scales[row["draw"]], strict=True):
                assert row[name] == pytest.approx(getattr(base, name) * scale, rel=1e-8)

    def test_cache_reproduces_on_a_prefix(self, rows):
        """The first 48 draws are re-solved and compared with the cache."""
        fresh = run_joint_sweep(n_draws=48, workers=1)
        for new, old in zip(fresh, rows[:48], strict=True):
            assert new["admissible"] == old["admissible"]
            if not new["admissible"]:
                assert new["failure"] == old["failure"]
                continue
            for key in SINGLE_FIRM_FIELDS:
                if isfinite(new[key]):
                    assert old[key] == pytest.approx(new[key], rel=1e-6, abs=1e-12)
                else:
                    assert str(old[key]) == str(new[key])
            for key in SIGN_LABELS:
                assert new[key] == old[key]

    @pytest.mark.slow
    def test_cache_reproduces_in_full(self, rows):
        fresh = run_joint_sweep(workers=8)
        for new, old in zip(fresh, rows, strict=True):
            assert new["admissible"] == old["admissible"]
            if new["admissible"]:
                for key in ("X_star", "K_star", "pre_ratio_levels", "waiting_margin"):
                    assert old[key] == pytest.approx(new[key], rel=1e-6)

    def test_counts(self, summary):
        """4,096 draws: 2,179 outside the window (53.2%), 7 inside it with a
        solver failure, 1,910 solved."""
        assert summary.n_draws == 4096
        assert summary.n_outside_window == 2179
        assert summary.failure_counts["(A2) upper"] == 1286
        assert summary.failure_counts["(A2) lower"] == 893
        assert summary.n_solver_failures == 7
        assert summary.n_admissible == 1910
        assert summary.inadmissible_share == pytest.approx(0.532, abs=5e-4)

    def test_sign_counts(self, summary):
        assert summary.sign_counts == {
            "sign_faith": 1894,
            "sign_monopolist_waits": 1645,
            "sign_pre_levels": 1910,
            "sign_pre_log_far": 1910,
            "sign_pre_log_near": 1829,
            "sign_pre_horizon": 1373,
            "sign_unr_levels": 1910,
        }

    def test_quantiles(self, summary):
        """5%, 50% and 95% quantiles quoted in tbl-joint-sweep."""
        expected = {
            "phi_star": (0.531, 0.713, 0.850),
            "phi_underbar": (0.062, 0.185, 0.296),
            "phi_tilde": (0.154, 0.323, 0.458),
            "waiting_margin": (0.945, 1.106, 1.291),
            "pre_loss_low_levels": (0.221, 0.328, 0.434),
            "pre_loss_high_levels": (0.00686, 0.01417, 0.02384),
            "pre_loss_high_log_far": (0.070, 0.142, 0.224),
            "unr_loss_low_levels": (0.273, 0.413, 0.538),
            "pre_ratio_levels": (14.4, 23.3, 36.8),
            "pre_ratio_log_far": (1.74, 2.36, 3.34),
            "pre_ratio_log_near": (1.07, 3.04, 7.55),
            "pre_ratio_horizon": (0.33, 0.73, 1.69),
            "pure_power_trigger_pct": (-60.0, -50.2, -37.8),
            "pure_power_capacity_pct": (-67.4, -55.3, -42.7),
        }
        for name, values in expected.items():
            table = summary.quantiles[name]
            got = (table["q5"], table["q50"], table["q95"])
            assert got == pytest.approx(values, rel=0.005), name

    def test_ranges(self, summary):
        assert summary.range("pre_ratio_levels") == pytest.approx((9.2, 54.1), abs=0.05)
        assert summary.range("pre_ratio_log_far") == pytest.approx(
            (1.13, 4.42), abs=0.01
        )
        assert summary.range("pre_ratio_log_near") == pytest.approx(
            (0.50, 17.81), abs=0.01
        )
        assert summary.range("pre_ratio_horizon") == pytest.approx(
            (0.21, 7.83), abs=0.01
        )

    def test_capacity_levels_span_many_orders_of_magnitude(self, summary):
        """The near-degeneracy of comment C16 in the model of record."""
        table = summary.quantiles["K_star"]
        assert table["q95"] / table["q5"] > 1e5
        assert table["q100"] / table["q0"] > 1e12

    def test_reversals_line_up_with_the_arrival_rate(self, rows):
        """Where the rankings of the dilemma reverse (Internet Appendix E)."""
        solved = [row for row in rows if row["admissible"]]
        low = [row for row in solved if row["lam"] < 0.10]
        high = [row for row in solved if row["lam"] >= 0.10]
        assert (len(low), len(high)) == (961, 949)
        assert sum(not row["sign_pre_horizon"] for row in low) == 499
        assert sum(not row["sign_pre_horizon"] for row in high) == 38
        assert sum(not row["sign_pre_log_near"] for row in low) == 1
        assert sum(not row["sign_pre_log_near"] for row in high) == 80
        invests = [row for row in solved if row["invests_before_switch"]]
        assert len(invests) == 265
        assert sum(row["gamma"] >= 1.5 for row in invests) == 242
        assert sum(row["lam"] < 0.10 for row in invests) == 218

    def test_report(self, rows):
        report = format_joint_report(rows)
        assert "4096 Sobol draws, seed 182" in report
        assert "outside the window: 2179 (53.2%)" in report


class TestCapabilityExtension:
    """Pre-positioned capability (Internet Appendix E, comment C2)."""

    @pytest.fixture(scope="class")
    def rows(self):
        return capability_extension()

    def test_first_row_is_the_model_of_record(self, rows):
        record = rows[0]
        assert np.isnan(record["kappa"])
        assert record["invests_before_switch"] == 0.0
        assert record["phi_star"] == pytest.approx(0.7009, abs=1e-4)
        assert record["value_over_record"] == pytest.approx(1.0, rel=1e-9)

    def test_every_kappa_has_a_finite_trigger(self, rows):
        for row in rows[1:]:
            assert row["invests_before_switch"] == 1.0
            assert 0.0 < row["X_star"] < inf
            assert row["X_star_over_late_trigger"] < 1.0

    def test_table(self, rows):
        """tbl-capability: kappa -> (X*, K*, phi*, phi_underbar, phi_tilde,
        value relative to the model of record)."""
        expected = {
            0.05: (1.084e-9, 1.139e-13, 0.6775, 0.1451, 0.2981, 0.8135),
            0.10: (4.317e-8, 5.354e-11, 0.6510, 0.1069, 0.2726, 0.8221),
            0.20: (1.521e-6, 2.075e-8, 0.5860, 0.0194, 0.2155, 0.8417),
            0.30: (1.070e-5, 5.498e-7, 0.4982, 0.0, 0.1487, 0.8659),
            0.50: (8.548e-5, 1.843e-5, 0.1922, 0.0, 0.0, 0.9368),
            0.75: (2.241e-4, 1.009e-4, 0.0, 0.0, 0.0, 1.0755),
            1.00: (4.160e-4, 2.976e-4, 0.0, 0.0, 0.0, 1.1989),
        }
        by_kappa = {row["kappa"]: row for row in rows[1:]}
        assert set(by_kappa) == set(expected)
        for kappa, (X, K, phi, lower, net, value) in expected.items():
            row = by_kappa[kappa]
            assert row["X_star"] == pytest.approx(X, rel=2e-3)
            assert row["K_star"] == pytest.approx(K, rel=2e-3)
            assert row["phi_star"] == pytest.approx(phi, abs=1e-4)
            assert row["phi_underbar"] == pytest.approx(lower, abs=1e-4)
            assert row["phi_tilde"] == pytest.approx(net, abs=1e-4)
            assert row["value_over_record"] == pytest.approx(value, abs=1e-4)

    def test_dilemma(self, rows):
        """Losses at beliefs 0.02 / 0.18 / 0.50 against a truth of 0.10."""
        by_kappa = {row["kappa"]: row for row in rows[1:]}
        expected = {
            0.10: (0.296, 0.027, 0.287),
            0.20: (0.208, 0.022, 0.288),
            0.50: (0.040, 0.013, 0.181),
            1.00: (0.045, 0.008, 0.015),
        }
        for kappa, losses in expected.items():
            row = by_kappa[kappa]
            got = (row["loss_low"], row["loss_high"], row["loss_far_high"])
            assert got == pytest.approx(losses, abs=1e-3)
        # Equal errors in lambda: the pessimist loses more at every kappa.
        assert all(row["ratio_levels"] > 3.0 for row in rows[1:])
        # Equal errors in logs: the ranking depends on kappa.
        assert by_kappa[0.20]["ratio_log_far"] < 1.0 < by_kappa[1.00]["ratio_log_far"]

    def test_corner(self, params, rows):
        """Nothing is trained before the switch for kappa above 0.571."""
        corner = capability_corner(params)
        assert corner == pytest.approx(0.5712, abs=1e-4)
        for row in rows[1:]:
            assert (row["phi_star"] > 0.0) == (row["kappa"] < corner)


class TestElasticities:
    def test_table(self):
        """tbl-elasticities: (X*, K*, phi*) of the precommitted-scale policy."""
        expected = {
            "r": (-21.6, -28.2, -1.0),
            "alpha": (20.4, 24.0, 0.2),
            "mu_H": (15.3, 19.7, 0.5),
            "sigma": (9.6, 11.8, 0.0),
            "gamma": (3.1, 6.6, 0.0),
            "delta": (2.2, 2.0, 0.0),
            "lam": (0.2, 0.5, 0.5),
        }
        rows = {row["param"]: row for row in policy_elasticities()}
        assert list(rows) == list(expected)
        for name, values in expected.items():
            row = rows[name]
            got = (row["X_star"], row["K_star"], row["phi_star"])
            assert got == pytest.approx(values, abs=0.05), name

    def test_post_switch_capacity_does_not_respond_to_beliefs(self):
        row = {r["param"]: r for r in policy_elasticities(parameters=("lam",))}["lam"]
        assert row["K_H"] == pytest.approx(0.0, abs=1e-9)
        assert row["X_H"] == pytest.approx(0.0, abs=1e-9)
        assert row["K_star"] > 0.5


class TestDuopolyCells:
    """The duopoly subsample: its definition and its cache."""

    def test_cells(self):
        cells = duopoly_cells()
        names = [cell["cell"] for cell in cells]
        assert len(names) == len(set(names))
        one_at_a_time = [name for name in names if name.startswith("oat:")]
        assert one_at_a_time == [
            "oat:mu_L-",
            "oat:mu_L+",
            "oat:mu_H+",
            "oat:sigma+",
            "oat:lam-",
            "oat:lam+",
            "oat:gamma-",
            "oat:gamma+",
            "oat:delta-",
            "oat:delta+",
            "oat:c-",
            "oat:c+",
        ]
        assert "fragile" in names
        joint = [name for name in names if name.startswith("joint:")]
        assert len(joint) == DUOPOLY_JOINT_DRAWS == 64
        assert joint[:4] == ["joint:3", "joint:4", "joint:6", "joint:7"]
        for cell in cells:
            params = ModelParameters().with_param(**cell["values"])
            assert game_admissibility_failure(params) is None

    def test_cache_covers_every_cell(self, duopoly):
        with DUOPOLY_GRID_PATH.open() as handle:
            stored = [cell["cell"] for cell in json.load(handle)]
        assert stored == [cell["cell"] for cell in duopoly_cells()]
        for cell in duopoly_cells():
            cached = duopoly[cell["cell"]]
            assert cached["values"] == pytest.approx(cell["values"], rel=1e-12)
            assert ("failure" in cached) or cached["record"]["exists"] == 1.0

    def test_baseline_comes_from_the_equilibrium_cache(self, duopoly):
        record = duopoly["baseline"]["record"]
        objects = duopoly_objects(record, single_firm_objects(ModelParameters()))
        assert objects["X_L_over_X_star"] == pytest.approx(0.3634, abs=1e-4)
        assert objects["X_L_over_X_P"] == pytest.approx(0.3926, abs=1e-4)
        assert objects["K_L_over_K_star"] == pytest.approx(0.2637, abs=1e-4)
        assert objects["phi_L_over_phi_star"] == pytest.approx(0.9689, abs=1e-4)
        assert objects["X_F_over_X_L"] == pytest.approx(13.16, abs=0.01)
        assert objects["equilibrium_verified"] == 1.0

    def test_sign_labels_cover_the_computed_signs(self, duopoly):
        rows = run_sweep(parameters=("lam",), duopoly=duopoly)
        for row in rows:
            for name in DUOPOLY_SIGN_LABELS:
                assert name in row


class TestDuopolySubsample:
    """Pin the duopoly objects of the sweeps (Internet Appendix E), read
    from the cache; `test_cell_reproduces` re-solves one cell."""

    @pytest.fixture(scope="class")
    def one_at_a_time(self, duopoly):
        return summarize_sweep(run_sweep(duopoly=duopoly))

    @pytest.fixture(scope="class")
    def joint_rows(self, duopoly):
        return load_joint_grid(duopoly)

    @pytest.fixture(scope="class")
    def joint(self, joint_rows):
        return summarize_sweep(joint_rows)

    def test_one_at_a_time_counts(self, one_at_a_time):
        """Twelve solved single-firm draws; alpha = 0.5 is outside the
        game, mu_H = 0.075 has no rent-equalization trigger, ten solve."""
        summary = one_at_a_time
        assert summary.n_duopoly == 11
        assert summary.n_duopoly_failed == 1
        assert summary.n_no_rent_equalization == 1
        ((label, reason),) = summary.duopoly_failures
        assert label == "mu_H+"
        assert reason.startswith("no rent-equalization trigger")
        solved = summary.n_duopoly - summary.n_duopoly_failed
        assert all(count == solved for count in summary.duopoly_sign_counts.values())

    def test_no_entry_at_the_higher_post_switch_drift(self, duopoly):
        """mu_H = 0.075: following beats leading at every scanned demand
        (by at least 4%) and leading never beats mutual waiting."""
        record = duopoly["oat:mu_H+"]["record"]
        assert record["n_sign_changes"] == 0.0
        assert record["max_gap_over_follower"] == pytest.approx(-0.041, abs=1e-3)
        assert record["max_lead_over_wait"] == pytest.approx(0.979, abs=1e-3)
        assert record["scan_peak"] == inf

    def test_one_at_a_time_ranges(self, one_at_a_time):
        expected = {
            "X_L_over_X_star": (0.273, 0.403),
            "X_L_over_X_P": (0.260, 0.581),
            "K_L_over_K_star": (0.174, 0.306),
            "phi_L_over_phi_star": (0.930, 0.990),
            "X_F_over_X_L": (5.65, 42.2),
            "lead_over_wait": (1.080, 1.125),
            "follower_over_leader": (1.047, 1.169),
        }
        for name, values in expected.items():
            assert one_at_a_time.range(name) == pytest.approx(values, rel=3e-3), name

    def test_scale_parameters_leave_the_equilibrium_ratios_unchanged(self, duopoly):
        base = ModelParameters()
        reference = evaluate_draw(base, "lam", "0", duopoly=duopoly)
        for name in ("delta", "c"):
            for direction in ("-", "+"):
                row = evaluate_draw(base, name, direction, duopoly=duopoly)
                for key in ("X_L_over_X_star", "K_L_over_K_star", "X_F_over_X_L"):
                    assert row[key] == pytest.approx(reference[key], rel=1e-3)

    def test_fragile_cell(self, duopoly):
        """gamma = 1.9: the equilibrium is verified, L* - F changes sign
        twice on the scan and the follower also has a pre-switch trigger."""
        cell = duopoly["fragile"]
        assert cell["values"] == {"gamma": 1.9}
        assert "failure" not in cell
        record = cell["record"]
        single = single_firm_objects(ModelParameters().with_param(gamma=1.9))
        objects = duopoly_objects(record, single)
        assert single["waiting_margin"] == pytest.approx(0.9928, abs=1e-4)
        assert single["invests_before_switch"] == 1.0
        assert single["X_unrestricted"] / single["X_star"] == pytest.approx(299, abs=1)
        assert objects["X_L_over_X_star"] == pytest.approx(0.325, abs=1e-3)
        assert objects["X_L_over_X_P"] == pytest.approx(0.240, abs=1e-3)
        assert objects["K_L_over_K_star"] == pytest.approx(0.237, abs=1e-3)
        assert objects["phi_L_over_phi_star"] == pytest.approx(0.928, abs=1e-3)
        assert objects["X_F_over_X_L"] == pytest.approx(5.45, abs=0.01)
        assert objects["equilibrium_verified"] == 1.0
        assert objects["single_crossing"] == 0.0
        assert record["n_sign_changes"] == 2.0
        # The follower's pre-switch trigger exists but at a demand several
        # hundred thousand times X_L.
        assert objects["follower_waits_for_switch"] == 0.0
        assert record["X_F_pre_switch"] / record["X_L"] > 5e5

    def test_joint_counts(self, joint):
        """64 draws: 47 solved, 15 without a rent-equalization trigger on
        the scan, 2 where the follower's capacity leaves the range."""
        assert joint.n_duopoly == 64
        assert joint.n_duopoly_failed == 17
        assert joint.n_no_rent_equalization == 15
        other = [r for _, r in joint.duopoly_failures if not r.startswith("no rent")]
        assert len(other) == 2
        assert all(reason.startswith("solver failure") for reason in other)

    def test_joint_sign_counts(self, joint):
        assert joint.duopoly_sign_counts == {
            "sign_entry_before_single": 42,
            "sign_entry_before_rent_eq": 44,
            "sign_leader_smaller": 42,
            "sign_leader_trains_less": 42,
            "sign_follower_later": 47,
            "sign_second_mover": 44,
            "sign_equilibrium": 39,
        }

    def test_joint_quantiles(self, joint):
        """5%, 50%, 95% quantiles of tbl-duopoly-sweep."""
        expected = {
            "X_L_over_X_star": (0.160, 0.342, 2.455),
            "X_L_over_X_P": (0.0712, 0.377, 0.999),
            "K_L_over_K_star": (0.115, 0.299, 3.381),
            "phi_L_over_phi_star": (0.905, 0.981, 1.002),
            "X_F_over_X_L": (5.88, 20.4, 377.1),
            "K_F_over_K_L": (12.7, 55.7, 467.3),
            "lead_over_wait": (1.022, 1.076, 1.133),
            "follower_over_leader": (1.000, 1.077, 1.190),
        }
        for name, values in expected.items():
            table = joint.duopoly_quantiles[name]
            got = (table["q5"], table["q50"], table["q95"])
            assert got == pytest.approx(values, rel=3e-3), name
        assert joint.range("X_L_over_X_star") == pytest.approx((0.1324, 5.16), rel=3e-3)
        assert joint.range("X_L_over_X_P") == pytest.approx((0.0468, 1.074), rel=3e-3)

    def test_why_the_equilibrium_checks_fail(self, joint_rows, duopoly):
        """Eight of the 47 solved draws: in three X_L lies above X_P (the
        follower would rather lead), in five the post-switch game is not a
        race. The follower waits for the switch in 40 draws."""
        solved = [row for row in joint_rows if "X_L_over_X_star" in row]
        assert len(solved) == 47
        failing = [row for row in solved if not row["sign_equilibrium"]]
        above = [row for row in failing if row["X_L_over_X_P"] > 1.0]
        no_race = [
            row
            for row in failing
            if duopoly[f"joint:{row['draw']}"]["record"]["post_switch_race"] == 0.0
        ]
        assert (len(failing), len(above), len(no_race)) == (8, 3, 5)
        assert not {row["draw"] for row in above} & {row["draw"] for row in no_race}
        assert max(row["X_L_over_X_P"] for row in above) == pytest.approx(
            1.074, abs=1e-3
        )
        assert sum(row["follower_waits_for_switch"] for row in solved) == 40
        assert sum(row["single_crossing"] for row in solved) == 40

    def test_draws_without_a_rent_equalization_trigger(self, joint_rows):
        """Following beats leading at every scanned demand; in eleven of
        the fifteen a leader whose rival follows would still enter on the
        scan, in four leading never beats mutual waiting."""
        rows = [row for row in joint_rows if "scan_peak_over_X_H" in row]
        assert len(rows) == 15
        gaps = [row["scan_max_gap_over_follower"] for row in rows]
        assert max(gaps) < 0.0
        assert min(gaps) == pytest.approx(-0.210, abs=1e-3)
        enters = [row for row in rows if row["scan_max_lead_over_wait"] > 1.0]
        assert len(enters) == 11
        assert all(isfinite(row["scan_peak_over_X_H"]) for row in enters)
        assert sum(not isfinite(row["scan_peak_over_X_H"]) for row in rows) == 4
        peaks = sorted(row["scan_peak_over_X_H"] for row in enters)
        assert peaks[0] == pytest.approx(1.39, abs=0.01)
        assert peaks[len(peaks) // 2] == pytest.approx(2.04, abs=0.01)
        assert peaks[-1] == pytest.approx(300.0, rel=1e-6)

    def test_cached_records_are_internally_consistent(self, duopoly):
        """Without re-solving: rent equalization at X_P and the definition
        of the reported ratios hold in every solved cell."""
        for name, cell in duopoly.items():
            if cell.get("failure") or name == "baseline":
                continue
            record = cell["record"]
            assert record["rent_eq_leader_value"] == pytest.approx(
                record["rent_eq_follower_value"], rel=1e-4
            ), name
            assert record["X_L_over_X_P"] == pytest.approx(
                record["X_L"] / record["X_P"], rel=1e-9
            )
            assert record["lead_over_wait"] == pytest.approx(
                record["leader_value"] / record["waiting_value"], rel=1e-9
            )
            assert record["leverage"] == 0.0
            assert record["scale"] == "envelope"

    @pytest.mark.slow
    def test_cell_reproduces(self, duopoly):
        """Re-solve one joint cell (about four minutes)."""
        from ai_lab_investment.models.preemption_levered import equilibrium_record

        cell = next(c for c in duopoly_cells() if c["cell"] == "joint:4")
        fresh = equilibrium_record(ModelParameters().with_param(**cell["values"]))
        cached = duopoly["joint:4"]["record"]
        for key in ("X_P", "X_L", "K_L", "phi_L", "X_F", "K_F"):
            assert fresh[key] == pytest.approx(cached[key], rel=3e-3), key
        assert fresh["equilibrium"] == cached["equilibrium"]
