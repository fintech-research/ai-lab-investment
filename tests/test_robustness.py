"""Smoke tests for the parameter-perturbation robustness sweep."""

import csv

import pytest

from ai_lab_investment.models import ModelParameters
from ai_lab_investment.robustness import (
    SIGN_FIELDS,
    SWEEP_PARAMETERS,
    admissibility_failure,
    evaluate_draw,
    format_sweep_report,
    run_sweep,
    summarize_sweep,
    write_sweep_csv,
)


@pytest.fixture
def params():
    return ModelParameters()


class TestAdmissibility:
    def test_baseline_is_admissible(self, params):
        assert admissibility_failure(params) is None

    def test_alpha_minus_25_violates_a2(self, params):
        """alpha = 0.30 falls below the (A2) window (0.36, 0.53)."""
        failure = admissibility_failure(params.with_param(alpha=0.30))
        assert failure is not None
        assert "(A2)" in failure

    def test_r_plus_25_violates_a2(self, params):
        """r = 0.15 lies above the admissible window (0.097, 0.135)."""
        failure = admissibility_failure(params.with_param(r=0.15))
        assert failure is not None
        assert "(A2)" in failure


class TestEvaluateDraw:
    @pytest.mark.parametrize("direction", ["-", "+"])
    def test_lambda_draws_are_admissible_and_signed(self, params, direction):
        row = evaluate_draw(params, "lam", direction)
        assert row.admissible
        assert row.failure is None
        assert row.value == pytest.approx(
            params.lam * (0.75 if direction == "-" else 1.25)
        )
        assert all(getattr(row, name) for name in SIGN_FIELDS)
        assert row.loss_conservative is not None
        assert row.loss_aggressive is not None
        assert row.preemption_discount is not None
        assert row.loss_conservative > row.loss_aggressive
        assert 0.0 < row.preemption_discount < 1.0

    def test_inadmissible_draw_is_reported_not_dropped(self, params):
        """(A2) failures carry the failing condition, not silent truncation."""
        row = evaluate_draw(params, "alpha", "-")
        assert not row.admissible
        assert row.failure is not None
        assert "(A2)" in row.failure
        assert row.loss_conservative is None

    def test_parameter_domain_failure_is_reported(self, params):
        """mu_H above r violates Assumption 1 at construction time."""
        row = evaluate_draw(params, "mu_H", "+", perturbation=2.0)
        assert not row.admissible
        assert row.failure is not None
        assert "(A1)" in row.failure


class TestRunSweep:
    @pytest.fixture(scope="class")
    def rows(self):
        return run_sweep(parameters=("lam",))

    def test_row_layout(self, rows):
        assert [row.param for row in rows] == ["baseline", "lam", "lam"]
        assert [row.direction for row in rows] == ["0", "-", "+"]

    def test_summary_counts_and_signs(self, rows):
        summary = summarize_sweep(rows)
        assert summary.n_perturbations == 2
        assert summary.n_admissible == 2
        assert summary.n_failed == 0
        assert all(summary.sign_survival.values())
        assert summary.ranges["dilemma_asymmetry"][0] > 1.0

    def test_report_lists_signs(self, rows):
        report = format_sweep_report(rows)
        assert "Qualitative claims across admissible draws" in report
        assert "FAILS" not in report

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
    """Pin the sweep results quoted in Internet Appendix E."""

    @pytest.fixture(scope="class")
    def summary(self):
        return summarize_sweep(run_sweep())

    def test_admissible_counts(self, summary):
        assert summary.n_perturbations == 18
        assert summary.n_admissible == 13
        assert summary.n_failed == 5

    def test_failing_draws(self, summary):
        failing = {(param, direction) for param, direction, _, _ in summary.failures}
        assert failing == {
            ("r", "-"),
            ("r", "+"),
            ("mu_H", "-"),
            ("sigma", "-"),
            ("alpha", "-"),
        }
        assert all("(A2)" in failure for _, _, _, failure in summary.failures)

    def test_all_headline_signs_survive(self, summary):
        assert all(summary.sign_survival.values())

    def test_reported_ranges(self, summary):
        low, high = summary.ranges["dilemma_asymmetry"]
        assert (low, high) == pytest.approx((3.6, 6.0), abs=0.1)
        assert summary.ranges["preemption_discount"] == pytest.approx(
            (0.53, 0.63), abs=0.01
        )
        assert summary.ranges["gap_fraction_low"] == pytest.approx(
            (47.9, 59.1), abs=0.5
        )
