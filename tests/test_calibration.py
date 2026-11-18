"""Tests for calibration and revealed beliefs."""

from pathlib import Path

import numpy as np
import pytest

from ai_lab_investment.calibration.archetypes import (
    BAND_POINTS,
    STATED_BELIEFS,
    archetype_duopoly_cells,
    archetype_outputs,
    format_archetype_table,
    format_stated_table,
    lambda_from_probability,
    normalization_example,
    stated_beliefs,
)
from ai_lab_investment.calibration.data import (
    get_baseline_calibration,
    get_stylized_firms,
)
from ai_lab_investment.calibration.revealed_beliefs import RevealedBeliefs

PAPER_DIR = Path(__file__).resolve().parents[1] / "paper"

# ------------------------------------------------------------------
# Calibration data
# ------------------------------------------------------------------


class TestCalibrationData:
    def test_baseline_calibration_valid(self):
        """Baseline calibration should produce valid model parameters."""
        calib = get_baseline_calibration()
        params = calib.to_model_params()
        assert params.r > params.mu_H
        assert params.beta_H > 1.0

    def test_has_firms(self):
        """Baseline calibration should include firm data."""
        calib = get_baseline_calibration()
        assert len(calib.firms) >= 3

    def test_has_sources(self):
        """Calibration should document data sources."""
        calib = get_baseline_calibration()
        assert len(calib.sources) > 0

    def test_to_model_params_override_lambda(self):
        """Should be able to override lambda in model params."""
        calib = get_baseline_calibration()
        p1 = calib.to_model_params(lam=0.1)
        p2 = calib.to_model_params(lam=0.5)
        assert p1.lam == 0.1
        assert p2.lam == 0.5

    def test_stylized_firms_count(self):
        """Should have 4 stylized firms."""
        firms = get_stylized_firms()
        assert len(firms) == 4

    def test_firms_have_positive_revenue(self):
        """All firms should have positive revenue."""
        firms = get_stylized_firms()
        for firm in firms:
            assert firm.revenue_2025 > 0
            assert firm.capex_2025 > 0


# ------------------------------------------------------------------
# Revealed beliefs: the closed-form phi inversion and the exploratory
# capex-intensity moments (merged from TestRevealedBeliefs,
# TestPhiAwareBeliefs and TestPhiInversion, issue #183)
# ------------------------------------------------------------------


@pytest.fixture(scope="module")
def rb():
    return RevealedBeliefs(get_baseline_calibration())


class TestRevealedBeliefs:
    def test_round_trip_through_model(self, rb):
        """phi*(lambda) of the model of record, inverted, recovers lambda."""
        from ai_lab_investment.models.base_model import SingleFirmModel

        for lam_true in (0.03, 0.10, 0.30):
            params = rb.calibration.to_model_params(lam=lam_true)
            _, _, phi_star = SingleFirmModel(params).optimal_trigger_capacity_phi()
            lam_recovered = rb.infer_lambda_from_phi(phi_star)
            assert lam_recovered == pytest.approx(lam_true, rel=1e-6)

    def test_phi_is_the_same_in_the_approximation(self, rb):
        """The allocation rule, hence the bands, does not depend on the
        solution method: phi* is exact in the pure-power approximation."""
        from ai_lab_investment.models.base_model import SingleFirmModel

        model = SingleFirmModel(rb.calibration.to_model_params())
        exact = model.optimal_trigger_capacity_phi()[2]
        approx = model.pure_power_trigger_capacity_phi()[2]
        assert exact == pytest.approx(model.closed_form_phi_star(), rel=1e-9)
        assert approx == pytest.approx(exact, abs=1e-3)

    def test_band_matches_paper_ranges(self, rb):
        """@tbl-firms: [0.05, 0.09], [0.06, 0.10], [0.03, 0.05], [0.09, 0.17]."""
        expected = {
            "Anthropic": (0.0532, 0.0870),
            "OpenAI": (0.0600, 0.0998),
            "Google": (0.0310, 0.0532),
            "xAI": (0.0870, 0.1699),
        }
        for firm in rb.calibration.firms:
            key = next(k for k in expected if k in firm.name)
            band = rb.phi_inversion_band(firm)
            assert band["lambda_lo"] == pytest.approx(expected[key][0], abs=1e-4)
            assert band["lambda_hi"] == pytest.approx(expected[key][1], abs=1e-4)

    def test_band_at_own_wacc(self, rb):
        """Internet Appendix C: xAI-like [0.17, 0.34] at r = 0.18, Google-like
        [0.02, 0.04] at r = 0.10."""
        firms = {f.name: f for f in rb.calibration.firms}
        xai = next(f for n, f in firms.items() if "xAI" in n)
        google = next(f for n, f in firms.items() if "Google" in n)
        b_xai = rb.phi_inversion_band(xai, use_firm_wacc=True)
        b_goog = rb.phi_inversion_band(google, use_firm_wacc=True)
        assert (b_xai["lambda_lo"], b_xai["lambda_hi"]) == pytest.approx(
            (0.174, 0.340), abs=1e-3
        )
        assert (b_goog["lambda_lo"], b_goog["lambda_hi"]) == pytest.approx(
            (0.021, 0.035), abs=1e-3
        )

    def test_inadmissible_phi_returns_none(self, rb):
        assert rb.infer_lambda_from_phi(0.0) is None
        assert rb.infer_lambda_from_phi(1.0) is None

    def test_phi_intensity_at_model_of_record(self, rb):
        """The phi-aware intensity uses the precommitted-scale K* and the
        exact value; it is U-shaped in lambda with a minimum near 7.5."""
        intensity, phi = rb._model_phi_intensity_at_lambda(0.10)
        assert intensity == pytest.approx(7.76, abs=0.02)
        assert phi == pytest.approx(0.7009, abs=1e-4)
        lo, _ = rb._model_phi_intensity_at_lambda(0.05)
        hi, _ = rb._model_phi_intensity_at_lambda(0.50)
        assert lo > intensity
        assert hi > intensity
        _, phi_lo = rb._model_phi_intensity_at_lambda(0.05)
        _, phi_hi = rb._model_phi_intensity_at_lambda(0.50)
        assert phi_hi > phi_lo

    def test_compute_all_with_phi(self, rb):
        """Only the xAI-like intensity (14.1) lies above the minimum of the
        exact intensity curve, so it alone has a phi-aware solution."""
        beliefs = rb.compute_all_revealed_beliefs_with_phi()
        assert len(beliefs) == len(rb.calibration.firms)
        solved = {b["firm"]: b["lambda_implied"] for b in beliefs}
        for name, lam in solved.items():
            if "xAI" in name:
                assert lam == pytest.approx(0.0555, abs=1e-3)
            else:
                assert lam is None
        for b in beliefs:
            assert "lambda_from_capex_legacy" in b
            assert b["lambda_from_phi"] == rb.infer_lambda_from_phi(
                next(
                    f.training_fraction
                    for f in rb.calibration.firms
                    if f.name == b["firm"]
                )
            )

    def test_phi_observed_from_firm_data(self, rb):
        firm = rb.calibration.firms[0]
        result = rb.infer_lambda_with_phi(firm)
        assert result["phi_observed"] == firm.training_fraction

    def test_compute_all_revealed_beliefs(self, rb):
        """H-regime (simple mode) capex inversion: every firm solves."""
        beliefs = rb.compute_all_revealed_beliefs()
        assert len(beliefs) == len(rb.calibration.firms)
        assert all(b["lambda_from_capex"] > 0 for b in beliefs)

    def test_sensitivity_analysis_shape(self, rb):
        firm = rb.calibration.firms[0]
        result = rb.sensitivity_analysis(firm, "sigma", np.linspace(0.20, 0.35, 4))
        assert len(result["param_values"]) == 4
        assert len(result["implied_lambda"]) == 4

    def test_investment_predictions(self, rb):
        preds = rb.investment_predictions(np.array([0.05, 0.10, 0.50]))
        assert preds["has_solution"].all()
        assert np.all(preds["triggers"] > 0)
        assert rb._model_capacity_at_lambda(0.10) > 0

    def test_summary(self, rb):
        s = rb.summary()
        for key in (
            "n_firms",
            "revealed_beliefs",
            "revealed_beliefs_with_phi",
            "predictions_by_lambda",
            "sources",
        ):
            assert key in s

    def test_calibration_passes_endogenous_params(self):
        calib = get_baseline_calibration()
        params = calib.to_model_params(xi=0.05)
        assert params.lam_0 == calib.lam_0
        assert params.eta == calib.eta
        assert params.xi == 0.05


# ------------------------------------------------------------------
# Archetype outputs under the model of record (issue #183)
# ------------------------------------------------------------------


@pytest.fixture(scope="module")
def archetypes():
    return {a["archetype"]: a for a in archetype_outputs()}


class TestArchetypeOutputs:
    def test_bands_and_round_trip(self, archetypes):
        """phi*(lambda) at each band point returns phi_hat -/+ 0.10."""
        for arch in archetypes.values():
            for key, shift in zip(BAND_POINTS, (-0.10, 0.0, 0.10), strict=True):
                assert arch["points"][key]["phi_star"] == pytest.approx(
                    arch["phi_hat"] + shift, abs=1e-9
                )
                assert arch["points"][key]["lam"] == arch["band"][key]

    def test_wacc_window(self, archetypes):
        """(A2) admits r in (0.097, 0.135): only the Google-like WACC is in."""
        inside = {name for name, a in archetypes.items() if a["wacc_in_window"]}
        assert inside == {"Google-like"}
        lo, hi = archetypes["Google-like"]["r_window"]
        assert (lo, hi) == pytest.approx((0.0970, 0.1352), abs=5e-4)

    @pytest.mark.parametrize(
        ("name", "key", "X", "K"),
        [
            ("Anthropic-like", "mid", 0.007710, 0.011416),
            ("OpenAI-like", "mid", 0.008358, 0.012983),
            ("Google-like", "lo", 0.000540, 0.000236),
            ("Google-like", "mid", 0.003431, 0.003650),
            ("xAI-like", "mid", 0.009464, 0.016908),
            ("xAI-like", "hi", 0.009230, 0.018359),
        ],
    )
    def test_precommitted_policy(self, archetypes, name, key, X, K):
        pt = archetypes[name]["points"][key]
        assert pt["X_star"] == pytest.approx(X, rel=2e-3)
        assert pt["K_star"] == pytest.approx(K, rel=2e-3)

    def test_unrestricted_waits_above_the_threshold(self, archetypes):
        """Scale chosen at the switch: beliefs at or above 0.073 wait; below,
        the trigger lies far above the precommitted one, except at the
        Google-like beliefs."""
        for arch in archetypes.values():
            for pt in arch["points"].values():
                assert pt["invests_before_switch"] == (pt["lam"] < 0.0729)
        anth = archetypes["Anthropic-like"]["points"]
        assert anth["mid"]["X_unrestricted"] == pytest.approx(1.171, rel=5e-3)
        assert anth["lo"]["X_unrestricted"] == pytest.approx(0.0302, rel=5e-3)
        goog = archetypes["Google-like"]["points"]
        assert goog["mid"]["X_unrestricted"] == pytest.approx(0.00361, rel=5e-3)

    def test_credit_at_own_leverage(self, archetypes):
        """Distance X*/X_D under par debt and five-year default probability
        (par / fair) at the archetype's leverage."""
        anth = archetypes["Anthropic-like"]["points"]["mid"]
        assert anth["distance_par"] == pytest.approx(6.14, abs=0.01)
        assert anth["pd5_par"] == pytest.approx(0.00214, abs=2e-5)
        assert anth["pd5_fair"] == pytest.approx(0.00231, abs=2e-5)
        goog = archetypes["Google-like"]["points"]
        assert goog["lo"]["distance_par"] == pytest.approx(4.29, abs=0.01)
        assert goog["lo"]["pd5_par"] == pytest.approx(0.0148, abs=1e-4)
        assert goog["mid"]["pd5_par"] == pytest.approx(0.00531, abs=5e-5)
        xai = archetypes["xAI-like"]["points"]["mid"]
        assert xai["distance_par"] == pytest.approx(6.30, abs=0.01)
        assert xai["pd5_fair"] == pytest.approx(0.00238, abs=2e-5)

    def test_dilemma_loss_against_the_baseline(self, archetypes):
        """Loss if the implied belief is wrong and lambda = 0.10 is true."""
        pts = {
            (n, k): a["points"][k] for n, a in archetypes.items() for k in BAND_POINTS
        }
        assert pts["Google-like", "lo"]["loss_precommitted"] == pytest.approx(
            0.2285, abs=5e-4
        )
        assert pts["Google-like", "mid"]["loss_precommitted"] == pytest.approx(
            0.1715, abs=5e-4
        )
        assert pts["Google-like", "mid"]["loss_unrestricted"] == pytest.approx(
            0.2711, abs=5e-4
        )
        assert pts["Anthropic-like", "mid"]["loss_precommitted"] == pytest.approx(
            0.0121, abs=2e-4
        )
        assert pts["OpenAI-like", "hi"]["loss_precommitted"] < 1e-4
        assert pts["xAI-like", "hi"]["loss_precommitted"] == pytest.approx(
            0.0107, abs=2e-4
        )
        for (_, _), pt in pts.items():
            if pt["lam"] >= 0.0729:
                assert pt["loss_unrestricted"] == pytest.approx(0.0, abs=1e-9)

    def test_duopoly_cells_inside_the_bands(self, archetypes):
        cells = archetype_duopoly_cells(list(archetypes.values()))
        assert [c["lam"] for c in cells["Google-like"]] == [0.05]
        assert [c["lam"] for c in cells["Anthropic-like"]] == [0.075]
        assert [c["lam"] for c in cells["OpenAI-like"]] == [0.075]
        assert [c["lam"] for c in cells["xAI-like"]] == [0.10, 0.15]
        assert cells["Google-like"][0]["X_L"] == pytest.approx(0.000841, rel=1e-3)
        assert cells["Anthropic-like"][0]["X_L"] == pytest.approx(0.002253, rel=1e-3)
        assert cells["xAI-like"][1]["X_L"] == pytest.approx(0.003826, rel=1e-3)

    def test_paper_table_is_generated(self, archetypes):
        """The body of @tbl-archetypes in Internet Appendix C is the output
        of `format_archetype_table`."""
        table = format_archetype_table(list(archetypes.values()))
        appendix = (PAPER_DIR / "_appendix.qmd").read_text()
        assert table in appendix


# ------------------------------------------------------------------
# Stated beliefs (issue #183, review comments C9 and C19d)
# ------------------------------------------------------------------


class TestStatedBeliefs:
    def test_mapping(self):
        assert lambda_from_probability(0.5, 1.0) == pytest.approx(np.log(2.0))
        assert lambda_from_probability(0.9, 10.0) == pytest.approx(np.log(10.0) / 10)
        lam = lambda_from_probability(0.39, 5.0)
        assert 1.0 - np.exp(-5.0 * lam) == pytest.approx(0.39)
        with pytest.raises(ValueError):
            lambda_from_probability(1.0, 10.0)
        with pytest.raises(ValueError):
            lambda_from_probability(0.5, 0.0)

    def test_amodei_statements(self):
        """amodei2026dwarkesh: lambda 0.23 to 0.46 and phi* 0.90 to 0.97,
        against phi_hat = 0.55 (lambda 0.068) and the reported 50/50
        (lambda 0.060)."""
        rows = {r["statement"]: r for r in stated_beliefs()}
        assert set(rows) == {
            'Ten-year timeline: "I\'m at 90%"',
            '"Strong view" of ten years: 95%',
            '"Strong view" of ten years: 99%',
            '"Hunch", 50/50: one to three years',
            '"Hunch", 50/50: one to two years',
        }
        assert all(r["cite_key"] == "amodei2026dwarkesh" for r in rows.values())
        expected = {
            'Ten-year timeline: "I\'m at 90%"': (0.2303, 0.9039),
            '"Strong view" of ten years: 95%': (0.2996, 0.9358),
            '"Strong view" of ten years: 99%': (0.4605, 0.9676),
            '"Hunch", 50/50: one to three years': (0.2310, 0.9044),
            '"Hunch", 50/50: one to two years': (0.3466, 0.9490),
        }
        for statement, (lam, phi) in expected.items():
            assert rows[statement]["lam"] == pytest.approx(lam, abs=1e-4)
            assert rows[statement]["phi_star"] == pytest.approx(phi, abs=1e-4)
        row = rows['Ten-year timeline: "I\'m at 90%"']
        assert row["lambda_phi_hat"] == pytest.approx(0.0677, abs=1e-4)
        assert row["lambda_reported_share"] == pytest.approx(0.0600, abs=1e-9)
        lams = [r["lam"] for r in rows.values()]
        assert min(lams) / row["lambda_phi_hat"] == pytest.approx(3.40, abs=0.01)
        assert max(lams) / row["lambda_phi_hat"] == pytest.approx(6.80, abs=0.01)

    def test_unsourced_statements_stay_out(self):
        """The Hassabis statements have no cite key yet (TO_VERIFY.md)."""
        all_rows = stated_beliefs(sourced_only=False)
        assert {r["speaker"] for r in all_rows} == {"Amodei", "Hassabis"}
        assert all(r["speaker"] == "Amodei" for r in stated_beliefs())
        hassabis = [r for r in all_rows if r["speaker"] == "Hassabis"]
        assert [round(r["lam"], 3) for r in hassabis] == [0.173, 0.069, 0.139]

    def test_cite_keys_exist(self):
        bib = (PAPER_DIR / "references.bib").read_text()
        for b in STATED_BELIEFS:
            if b.cite_key is not None:
                assert "{" + b.cite_key + "," in bib


class TestStatedTable:
    def test_paper_table_is_generated(self):
        """The body of @tbl-stated-beliefs is `format_stated_table`."""
        table = format_stated_table(stated_beliefs())
        appendix = (PAPER_DIR / "_appendix.qmd").read_text()
        assert table in appendix


# ------------------------------------------------------------------
# Units: change of cost scale against a monetary unit (review comment C6)
# ------------------------------------------------------------------


class TestUnits:
    def test_cost_scale_is_a_homogeneity(self):
        """Re-solving at cost c moves K by 1/kappa and X by
        1/kappa^(1 - alpha), kappa = c^(1/(gamma - 1)); values scale by
        1/kappa (not kappa), in the model of record."""
        from ai_lab_investment.models.parameters import ModelParameters
        from ai_lab_investment.models.piecewise_option import solve_single_firm

        base = solve_single_firm(ModelParameters())
        scaled = solve_single_firm(ModelParameters(c=4.0))
        kappa = 4.0 ** (1.0 / (1.5 - 1.0))
        assert (
            pytest.approx(kappa, rel=1e-5)
            == base.precommitted.K / scaled.precommitted.K
        )
        assert base.precommitted.X_star / scaled.precommitted.X_star == pytest.approx(
            kappa**0.6, rel=1e-5
        )
        X = 0.004
        assert base.value(X) / scaled.value(X / kappa**0.6) == pytest.approx(
            kappa, rel=1e-6
        )
        assert scaled.invests_before_switch == base.invests_before_switch
        assert scaled.phi_star == base.phi_star

    def test_credit_is_invariant_to_the_cost_scale(self):
        """Distance to the boundary, default probability and spread at the
        model's own policy do not depend on c."""
        from ai_lab_investment.models.parameters import ModelParameters
        from ai_lab_investment.models.valuation import ValuationAnalysis

        rows = [
            ValuationAnalysis(ModelParameters(c=c)).on_policy_credit(
                leverages=(0.40,), conventions=("par",), roles=("single_firm",)
            )[0]
            for c in (1.0, 4.0)
        ]
        for key in ("distance", "default_probability", "spread"):
            assert rows[1][key] == pytest.approx(rows[0][key], rel=1e-6)

    def test_monetary_unit(self):
        """@sec-calibration: m = $27T maps I(K_L) = 0.00027 to $7.3B; the
        follower's outlay I(K_F) = 0.066 is then $1.8T."""
        ex = normalization_example()
        assert ex["I_leader"] == pytest.approx(0.000269, abs=1e-6)
        assert ex["I_follower"] == pytest.approx(0.0655, abs=1e-4)
        assert ex["m"] == pytest.approx(27_294, rel=1e-3)
        assert ex["follower_dollars"] == pytest.approx(1_789, rel=1e-3)
        assert ex["I_single"] == pytest.approx(0.00198, abs=1e-5)

    def test_delta_is_a_normalization(self):
        """Internet Appendix C: at delta = 0.10 the levels move (X* 0.0093 to
        0.131, K* 0.0158 to 0.175), phi* and the dilemma losses do not."""
        from ai_lab_investment.models.belief_mismatch import SingleFirmMismatch
        from ai_lab_investment.models.parameters import ModelParameters
        from ai_lab_investment.models.piecewise_option import solve_single_firm

        sol = solve_single_firm(ModelParameters(delta=0.10))
        assert sol.precommitted.X_star == pytest.approx(0.1309, abs=2e-4)
        assert pytest.approx(0.1754, abs=2e-4) == sol.precommitted.K
        assert sol.phi_star == pytest.approx(0.7009, abs=1e-4)
        models = [
            SingleFirmMismatch(ModelParameters(delta=d), 0.10) for d in (0.03, 0.10)
        ]
        for belief, level in ((0.02, 0.3247), (0.18, 0.0132), (0.50, 0.1325)):
            base, scaled = (m.loss(belief)["value_loss_pct"] for m in models)
            assert scaled == pytest.approx(base, rel=1e-6)
            assert base == pytest.approx(level, abs=5e-4)


class TestFirstBracket:
    def test_returns_lowest_sign_change(self):
        from ai_lab_investment.calibration.revealed_beliefs import _first_bracket

        # two roots at 0.05 and 0.3: endpoint bracketing (0.01, 0.5) would
        # see no sign change; the grid scan returns the lower one.
        gap = lambda lam: (lam - 0.05) * (lam - 0.3)  # noqa: E731
        bracket = _first_bracket(gap, (0.01, 0.5))
        assert bracket is not None
        lo, hi = bracket
        assert lo < 0.05 < hi
        assert hi < 0.3
        assert _first_bracket(lambda lam: 1.0, (0.01, 0.5)) is None
        assert _first_bracket(lambda lam: 1e12, (0.01, 0.5)) is None
