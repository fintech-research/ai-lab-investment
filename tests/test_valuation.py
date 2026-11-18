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
    # The zero-leverage cases live in
    # tests/test_duopoly.py::TestUnleveredFirm.

    def test_positive_leverage_positive_spread(self, va):
        """A levered firm has a strictly positive spread at every
        leverage: recovery is net of operating costs, so debt is never
        default-free."""
        for lev in (0.01, 0.13, 0.4):
            assert va.credit_spread(leverage=lev) > 0.0

    def test_higher_leverage_higher_spread(self, va):
        """Higher leverage should produce strictly higher spread."""
        s1 = va.credit_spread(leverage=0.2)
        s2 = va.credit_spread(leverage=0.6)
        assert s2 > s1 > 0.0

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
        """The spread is strictly positive at high leverage, under the
        netted rule and under the pre-#177 gross rule alike."""
        assert va.credit_spread(leverage=0.7) > 0.0
        gross = ValuationAnalysis(va.params, recovery_rule="gross")
        assert 0.0 < gross.credit_spread(leverage=0.7) < va.credit_spread(leverage=0.7)

    def test_unknown_debt_convention_raises(self, va):
        with pytest.raises(ValueError, match="debt convention"):
            va.credit_spread(leverage=0.4, debt_convention="market")

    def test_leverage_out_of_range_raises(self, va):
        with pytest.raises(ValueError, match="Leverage"):
            va.credit_metrics(1.2, 0.10, 1.0, 0.5)

    def test_spread_against_other_benchmark_rate(self, va):
        base = va.credit_spread(leverage=0.4)
        shifted = va.credit_spread(leverage=0.4, risk_free_rate=va.params.r - 0.01)
        assert shifted == pytest.approx(base + 0.01)

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


# (role, debt, leverage) -> (X_D, spread bps, 5-year default probability %,
# recovery % of the claim): the on-policy credit table of issue #179.
ON_POLICY_CREDIT = {
    ("single_firm", "par", 0.00): (0.0014323, 22.17, 0.1565, 0.000),
    ("leader", "par", 0.00): (0.0007002, 43.61, 0.8375, 0.000),
    ("follower", "par", 0.00): (0.0043010, 3.77, 0.0010, 0.000),
    ("single_firm", "par", 0.01): (0.0014353, 22.27, 0.1585, 0.000),
    ("leader", "par", 0.01): (0.0007009, 43.69, 0.8424, 0.082),
    ("follower", "par", 0.01): (0.0043431, 3.85, 0.0011, 0.000),
    ("single_firm", "par", 0.05): (0.0014473, 22.69, 0.1667, 0.000),
    ("leader", "par", 0.05): (0.0007040, 44.02, 0.8619, 0.407),
    ("follower", "par", 0.05): (0.0045163, 4.19, 0.0014, 0.000),
    ("single_firm", "par", 0.10): (0.0014623, 23.22, 0.1774, 0.000),
    ("leader", "par", 0.10): (0.0007079, 44.43, 0.8868, 0.808),
    ("follower", "par", 0.10): (0.0047445, 4.67, 0.0020, 0.000),
    ("single_firm", "par", 0.15): (0.0014773, 23.76, 0.1887, 0.000),
    ("leader", "par", 0.15): (0.0007117, 44.87, 0.9120, 1.127),
    ("follower", "par", 0.15): (0.0049869, 5.20, 0.0029, 0.000),
    ("single_firm", "par", 0.20): (0.0014923, 24.29, 0.2004, 0.051),
    ("leader", "par", 0.20): (0.0007156, 45.39, 0.9377, 1.221),
    ("follower", "par", 0.20): (0.0052449, 5.79, 0.0040, 0.000),
    ("single_firm", "par", 0.40): (0.0015523, 26.41, 0.2531, 0.679),
    ("leader", "par", 0.40): (0.0007308, 47.43, 1.0443, 1.667),
    ("follower", "par", 0.40): (0.0064723, 9.00, 0.0153, 0.000),
    ("single_firm", "par", 0.70): (0.0016423, 29.73, 0.3504, 1.763),
    ("leader", "par", 0.70): (0.0007529, 50.50, 1.2142, 2.304),
    ("follower", "par", 0.70): (0.0092545, 18.45, 0.1087, 0.000),
    ("single_firm", "fair", 0.00): (0.0014323, 22.17, 0.1565, 0.000),
    ("leader", "fair", 0.00): (0.0007002, 43.61, 0.8375, 0.000),
    ("follower", "fair", 0.00): (0.0043010, 3.77, 0.0010, 0.000),
    ("single_firm", "fair", 0.01): (0.0014397, 22.42, 0.1614, 0.000),
    ("leader", "fair", 0.01): (0.0007021, 43.82, 0.8499, 0.203),
    ("follower", "fair", 0.01): (0.0043706, 3.92, 0.0011, 0.000),
    ("single_firm", "fair", 0.05): (0.0014690, 23.46, 0.1824, 0.000),
    ("leader", "fair", 0.05): (0.0007100, 44.67, 0.9006, 1.003),
    ("follower", "fair", 0.05): (0.0046492, 4.57, 0.0019, 0.000),
    ("single_firm", "fair", 0.10): (0.0015058, 24.77, 0.2115, 0.159),
    ("leader", "fair", 0.10): (0.0007199, 45.95, 0.9672, 1.381),
    ("follower", "fair", 0.10): (0.0049978, 5.47, 0.0034, 0.000),
    ("single_firm", "fair", 0.15): (0.0015427, 26.07, 0.2440, 0.563),
    ("leader", "fair", 0.15): (0.0007298, 47.28, 1.0373, 1.694),
    ("follower", "fair", 0.15): (0.0053470, 6.47, 0.0057, 0.000),
    ("single_firm", "fair", 0.20): (0.0015796, 27.40, 0.2802, 1.012),
    ("leader", "fair", 0.20): (0.0007398, 48.63, 1.1110, 2.012),
    ("follower", "fair", 0.20): (0.0056967, 7.57, 0.0092, 0.000),
    ("single_firm", "fair", 0.40): (0.0017282, 33.10, 0.4666, 2.706),
    ("leader", "fair", 0.40): (0.0007799, 54.30, 1.4449, 3.216),
    ("follower", "fair", 0.40): (0.0070992, 13.06, 0.0437, 0.000),
    ("single_firm", "fair", 0.70): (0.0019543, 42.98, 0.9015, 4.700),
    ("leader", "fair", 0.70): (0.0008410, 63.67, 2.0745, 4.774),
    ("follower", "fair", 0.70): (0.0091914, 24.81, 0.2256, 0.000),
}


@pytest.fixture(scope="module")
def on_policy_rows():
    return ValuationAnalysis(ModelParameters()).on_policy_credit(
        roles=("single_firm", "single_firm_closed_form", "leader", "follower")
    )


def _select(rows, role, debt):
    return [r for r in rows if r["role"] == role and r["debt"] == debt]


class TestPublishedCreditLevels:
    """The on-policy credit table and fig-credit-risk (issue #179).

    Debt issued at each role's own entry: the single firm's
    precommitted-scale policy, the duopoly's first investment X_L (leader's
    policy held at the unlevered equilibrium) and the follower's
    post-switch entry; exact claims; default recovery rule
    ("net_with_shutdown"); leverage grid ON_POLICY_LEVERAGES; both debt
    conventions. `_valuation.qmd`, Credit Risk Analysis, and Internet
    Appendix H quote these numbers.
    """

    def test_grid(self, on_policy_rows):
        from ai_lab_investment.models.valuation import ON_POLICY_LEVERAGES

        assert ON_POLICY_LEVERAGES == (0.0, 0.01, 0.05, 0.10, 0.15, 0.20, 0.40, 0.70)
        for role in ("single_firm", "single_firm_closed_form", "leader", "follower"):
            for debt in ("par", "fair"):
                rows = _select(on_policy_rows, role, debt)
                assert [r["leverage"] for r in rows] == list(ON_POLICY_LEVERAGES)

    @pytest.mark.parametrize("key", sorted(ON_POLICY_CREDIT))
    def test_levels(self, on_policy_rows, key):
        role, debt, lev = key
        (row,) = [
            r for r in _select(on_policy_rows, role, debt) if r["leverage"] == lev
        ]
        X_D, spread, pd, recovery = ON_POLICY_CREDIT[key]
        assert row["X_D"] == pytest.approx(X_D, rel=2e-4)
        assert 1e4 * row["spread"] == pytest.approx(spread, abs=0.02)
        assert 100 * row["default_probability"] == pytest.approx(pd, abs=2e-4)
        assert 100 * row["recovery_rate"] == pytest.approx(recovery, abs=2e-3)

    def test_entry_policies(self, on_policy_rows):
        (sf,) = [
            r
            for r in _select(on_policy_rows, "single_firm", "par")
            if r["leverage"] == 0
        ]
        assert (sf["X"], sf["K"], sf["phi"]) == pytest.approx(
            (0.009258, 0.015784, 0.7009), rel=1e-3
        )
        (lead,) = [
            r for r in _select(on_policy_rows, "leader", "par") if r["leverage"] == 0
        ]
        assert (lead["X"], lead["K"], lead["phi"]) == pytest.approx(
            (0.003364, 0.004163, 0.6791), rel=1e-3
        )
        assert lead["distance"] == pytest.approx(4.805, abs=1e-3)
        (fol,) = [
            r for r in _select(on_policy_rows, "follower", "par") if r["leverage"] == 0
        ]
        assert fol["X"] == pytest.approx(0.04429, rel=1e-3)
        assert fol["distance"] == pytest.approx(10.30, abs=0.01)

    def test_spread_is_positive_without_debt_and_rises_with_leverage(
        self, on_policy_rows
    ):
        """Shutdown risk alone prices the debt: the spread on an
        infinitesimal issue is positive for every role, and leverage up to
        0.40 adds at most a quarter to it for the single firm and the leader."""
        for role in ("single_firm", "leader", "follower"):
            for debt in ("par", "fair"):
                rows = _select(on_policy_rows, role, debt)
                spreads = np.array([r["spread"] for r in rows])
                pds = np.array([r["default_probability"] for r in rows])
                assert spreads[0] > 0
                assert np.all(np.diff(spreads) > 0)
                assert np.all(np.diff(pds) > 0)
                if role != "follower":
                    at_040 = rows[6]["spread"]
                    assert at_040 / spreads[0] < 1.5

    def test_fair_debt_is_riskier_than_par_debt(self, on_policy_rows):
        for role in ("single_firm", "leader", "follower"):
            par = _select(on_policy_rows, role, "par")
            fair = _select(on_policy_rows, role, "fair")
            for a, b in zip(par[1:], fair[1:], strict=True):
                assert b["spread"] > a["spread"]
                # The follower re-optimizes, and the par subsidy raises its
                # capacity, so only the fixed policies compare boundaries.
                if role != "follower":
                    assert b["X_D"] > a["X_D"]
            assert fair[6]["coupon_rate"] == pytest.approx(0.12 + fair[6]["spread"])

    def test_closed_form_understates_the_single_firm_spread(self, on_policy_rows):
        """The single-boundary closed forms (Proposition 2) put X_D about 3%
        higher than the coupled boundary and omit default after the switch,
        so they understate the spread (17 against 22 bps without debt)."""
        exact = _select(on_policy_rows, "single_firm", "par")
        closed = _select(on_policy_rows, "single_firm_closed_form", "par")
        assert 1e4 * closed[0]["spread"] == pytest.approx(16.78, abs=0.02)
        assert 1e4 * closed[6]["spread"] == pytest.approx(19.93, abs=0.02)
        assert 1e4 * closed[7]["spread"] == pytest.approx(22.52, abs=0.02)
        for e, c in zip(exact, closed, strict=True):
            assert 1.02 < c["X_D"] / e["X_D"] < 1.04
            assert c["spread"] < e["spread"]

    def test_leader_policy_held_fixed_matches_the_cached_equilibria(
        self, on_policy_rows
    ):
        """Under fairly priced debt the re-solved equilibria at leverage 0.20
        and 0.40 change the leader's policy by less than 1%, so the table's
        fixed-policy rows are within a few tenths of a basis point of the
        equilibrium spread; under par debt the subsidy moves the policy."""
        from ai_lab_investment.models.duopoly import cached_equilibrium

        fair = {r["leverage"]: r for r in _select(on_policy_rows, "leader", "fair")}
        for lev in (0.20, 0.40):
            rec = cached_equilibrium(leverage=lev, debt="fair")
            assert rec["spread"] == pytest.approx(fair[lev]["spread"], abs=1e-4)
            assert rec["X_D_leader"] == pytest.approx(fair[lev]["X_D"], rel=0.01)
        par = cached_equilibrium(leverage=0.40, debt="par")
        assert par["X_L"] > 1.3 * fair[0.40]["X"]


class TestCreditPhiProfile:
    """fig-credit-risk panels (c) and (d): phi varied at a fixed scale."""

    @pytest.fixture(scope="class")
    def profiles(self):
        va = ValuationAnalysis(ModelParameters())
        phis = np.linspace(0.30, 0.95, 27)
        return {
            debt: va.credit_phi_profile(phis, 0.40, debt) for debt in ("par", "fair")
        }

    def test_recovery_weakly_increasing_in_phi_up_to_the_cap(self, profiles):
        for debt in ("par", "fair"):
            for role in ("single_firm", "leader"):
                prof = profiles[debt][role]
                rec = prof["recovery_rate"]
                assert np.all(np.diff(rec) >= -1e-9)
                assert np.all(rec[prof["phi"] <= 0.60] == 0.0)
                assert rec[-1] > 0.03

    def test_spread_falls_in_phi_through_the_policy(self, profiles):
        """Around the policies more training lowers the spread at a fixed
        scale: default risk and loss given default fall together."""
        for debt in ("par", "fair"):
            for role in ("single_firm", "leader"):
                prof = profiles[debt][role]
                phi, spread = prof["phi"], prof["spread"]
                band = (phi >= 0.30) & (phi <= 0.75)
                assert np.all(np.diff(spread[band]) < 0)

    def test_net_rule_has_zero_recovery_at_the_policies(self):
        va = ValuationAnalysis(ModelParameters(), recovery_rule="net")
        prof = va.credit_phi_profile(np.array([0.6791, 0.7009]), 0.40, "par")
        assert np.all(prof["single_firm"]["recovery_rate"] == 0.0)
        assert np.all(prof["leader"]["recovery_rate"] == 0.0)


class TestOffPolicyStressPoint:
    """The evaluation point of the earlier drafts' fig-credit-risk,
    (X, K, phi) = (0.10, 1, 0.5), kept so its numbers stay reproducible:
    no firm of the model is there (X is 11 times X*, K 63 times K*). The
    paper no longer quotes it (issue #179)."""

    def test_levels_under_the_177_rule(self, params):
        net = ValuationAnalysis(params, recovery_rule="net")
        assert net.credit_spread(leverage=0.05) * 1e4 == pytest.approx(27.66, abs=0.2)
        assert net.credit_spread(leverage=0.20) * 1e4 == pytest.approx(45.57, abs=0.2)
        assert net.credit_spread(leverage=0.40) * 1e4 == pytest.approx(78.78, abs=0.2)
        assert net.credit_spread(leverage=0.70) * 1e4 == pytest.approx(146.78, abs=0.5)

    def test_levels_under_the_default_rule(self, va):
        assert va.credit_spread(leverage=0.40) * 1e4 == pytest.approx(76.4, abs=0.2)
        assert va.credit_spread(leverage=0.70) * 1e4 == pytest.approx(141.8, abs=0.5)

    def test_earlier_draft_levels_under_gross_recovery(self, params):
        """The draft's 'approximately 40 bps at ell = 0.40 and 100 bps
        at ell = 0.70', with a spread that turns positive 'around
        ell ~ 0.13'."""
        gross = ValuationAnalysis(params, recovery_rule="gross")
        assert gross.credit_spread(leverage=0.40) * 1e4 == pytest.approx(41.34, abs=0.2)
        assert gross.credit_spread(leverage=0.70) * 1e4 == pytest.approx(97.13, abs=0.5)
        assert gross.credit_spread(leverage=0.13) < 1e-9
        assert gross.credit_spread(leverage=0.14) * 1e4 == pytest.approx(1.05, abs=0.1)
        assert gross.credit_spread(leverage=0.15) * 1e4 == pytest.approx(3.07, abs=0.1)

    def test_default_probability_levels(self, va):
        """Unchanged by the recovery rule: the boundary does not depend on it."""
        pd = va.default_probability
        X = va.CREDIT_RISK_DEMAND_LEVEL
        assert pd(X, 1.0, 0.05) * 100 == pytest.approx(0.627, abs=0.01)
        assert pd(X, 1.0, 0.40) * 100 == pytest.approx(4.847, abs=0.02)
        assert pd(X, 1.0, 0.70) * 100 == pytest.approx(12.979, abs=0.05)


CREDIT_TABLE_LEVERAGES = (0.0, 0.01, 0.05, 0.20, 0.40, 0.70)

# leverage -> (X_D par, spread par bps, X_D fair, spread fair bps,
# recovery rate par, recovery rate fair); closed forms, default rule.
CREDIT_TABLE_RECORD = {
    0.0: (0.001478, 16.78, 0.001478, 16.78, 0.0000, 0.0000),
    0.01: (0.001482, 16.86, 0.001486, 16.96, 0.0005, 0.0012),
    0.05: (0.001494, 17.16, 0.001516, 17.71, 0.0025, 0.0060),
    0.20: (0.001540, 18.31, 0.001630, 20.67, 0.0097, 0.0217),
    0.40: (0.001602, 19.93, 0.001782, 25.12, 0.0182, 0.0385),
    0.70: (0.001695, 22.52, 0.002013, 32.94, 0.0295, 0.0574),
}
CREDIT_TABLE_PURE_POWER = {
    0.0: (0.000886, 24.63, 0.000886, 24.63, 0.0000, 0.0000),
    0.01: (0.000887, 24.71, 0.000889, 24.81, 0.0003, 0.0008),
    0.05: (0.000892, 24.99, 0.000901, 25.52, 0.0017, 0.0040),
    0.20: (0.000910, 26.10, 0.000946, 28.33, 0.0064, 0.0150),
    0.40: (0.000935, 27.62, 0.001006, 32.39, 0.0124, 0.0275),
    0.70: (0.000971, 30.00, 0.001096, 39.21, 0.0205, 0.0429),
}
# Same, par spread (bps) under the #177 rule ("net"), which has zero recovery.
CREDIT_TABLE_RECORD_NET = {0.0: 16.78, 0.20: 18.50, 0.40: 20.31, 0.70: 23.22}


class TestCreditPrimitivesTable:
    """The table issue #177 reports: X_D, recovery rate and spread at
    entry for ell in {0, 0.01, 0.05, 0.20, 0.40, 0.70}, under par debt at
    r_c and under fairly priced debt, at two single-firm policies."""

    @pytest.mark.parametrize("which", ["record", "pure_power"])
    def test_table(self, va, params, which):
        model = SingleFirmModel(params)
        if which == "record":
            X, K, phi = model.optimal_trigger_capacity_phi()
            expected = CREDIT_TABLE_RECORD
        else:
            X, K, phi = model.pure_power_trigger_capacity_phi()
            expected = CREDIT_TABLE_PURE_POWER
        rows = va.credit_table(X, K, phi, CREDIT_TABLE_LEVERAGES)
        assert [row["leverage"] for row in rows] == list(CREDIT_TABLE_LEVERAGES)
        for row in rows:
            xd_par, s_par, xd_fair, s_fair, rec_par, rec_fair = expected[
                row["leverage"]
            ]
            assert row["par_X_D"] == pytest.approx(xd_par, abs=1e-6)
            assert row["fair_X_D"] == pytest.approx(xd_fair, abs=1e-6)
            assert row["par_spread"] * 1e4 == pytest.approx(s_par, abs=0.02)
            assert row["fair_spread"] * 1e4 == pytest.approx(s_fair, abs=0.02)
            # Recovery is a few percent of the claim at most, rising from
            # zero as leverage goes to zero.
            assert row["par_recovery_rate"] == pytest.approx(rec_par, abs=1e-4)
            assert row["fair_recovery_rate"] == pytest.approx(rec_fair, abs=1e-4)
            # Fairly priced debt pays r plus the spread on its proceeds.
            assert row["fair_coupon_rate"] == pytest.approx(
                params.r + row["fair_spread"], rel=1e-9
            )

    def test_net_rule_has_zero_recovery(self, params):
        X, K, phi = SingleFirmModel(params).optimal_trigger_capacity_phi()
        net = ValuationAnalysis(params, recovery_rule="net")
        rows = net.credit_table(X, K, phi, tuple(CREDIT_TABLE_RECORD_NET))
        for row in rows:
            assert row["par_recovery_rate"] == 0.0 or row["leverage"] == 0.0
            assert row["par_spread"] * 1e4 == pytest.approx(
                CREDIT_TABLE_RECORD_NET[row["leverage"]], abs=0.02
            )

    def test_table_columns_increase_in_leverage(self, va, params):
        X, K, phi = SingleFirmModel(params).optimal_trigger_capacity_phi()
        rows = va.credit_table(X, K, phi, CREDIT_TABLE_LEVERAGES)
        for key in ("par_X_D", "fair_X_D", "par_spread", "fair_spread"):
            assert np.all(np.diff([row[key] for row in rows]) > 0)
        # The fair coupon exceeds the par coupon, so its boundary is higher.
        for row in rows[1:]:
            assert row["fair_X_D"] > row["par_X_D"]
            assert row["fair_default_probability"] > row["par_default_probability"]

    def test_missing_fair_coupon_is_reported_as_nan(self, va):
        """At the figure's off-policy point no coupon raises 70% of I(K)."""
        (row,) = va.credit_table(0.10, 1.0, 0.5, (0.70,))
        assert np.isnan(row["fair_spread"])
        assert row["par_spread"] * 1e4 == pytest.approx(141.82, abs=0.5)
        assert row["par_recovery_rate"] == pytest.approx(0.0703, abs=5e-4)

    def test_fair_default_probability_matches_metrics(self, va, params):
        X, K, phi = SingleFirmModel(params).optimal_trigger_capacity_phi()
        metrics = va.credit_metrics(0.40, X, K, phi, "fair")
        pd = va.default_probability(X, K, 0.40, phi, debt_convention="fair")
        assert pd == pytest.approx(metrics["default_probability"], rel=1e-12)
        assert pd * 100 == pytest.approx(0.552, abs=0.005)
        assert metrics["distance"] == pytest.approx(X / metrics["X_D"])


# ------------------------------------------------------------------
# Dario's dilemma in the model of record (issue #180)
# ------------------------------------------------------------------


@pytest.fixture(scope="module")
def exact_va():
    """One analysis object for the exact dilemma (it caches the solves)."""
    return ValuationAnalysis(ModelParameters())


class TestDarioDilemma:
    """Single firm, exact values, both versions of the problem."""

    @pytest.mark.parametrize("version", ["precommitted", "unrestricted"])
    def test_matched_beliefs_no_loss(self, exact_va, version):
        result = exact_va.dario_dilemma(0.10, 0.10, version)
        assert result["value_loss_pct"] == 0.0
        assert result["timing_pct"] == pytest.approx(0.0, abs=1e-12)

    def test_reference_demand_is_half_the_true_trigger(self, exact_va):
        result = exact_va.dario_dilemma(0.10, 0.20)
        X_star, _, _ = SingleFirmModel(ModelParameters()).optimal_trigger_capacity_phi()
        assert result["X_0"] == pytest.approx(0.5 * X_star, rel=1e-12)
        assert result["X_optimal"] == pytest.approx(X_star, rel=1e-9)
        assert exact_va.dario_dilemma(0.10, 0.20, "unrestricted")[
            "X_0"
        ] == pytest.approx(result["X_0"], rel=1e-12)

    @pytest.mark.parametrize(
        ("belief", "loss"),
        [
            (0.02, 32.46),
            (0.03, 23.57),
            (0.05, 8.31),
            (0.10 / 1.8, 4.33),
            (9.0 / 130.0, 1.03),
            (0.18, 1.32),
            (0.20, 1.87),
            (0.50, 13.25),
        ],
    )
    def test_precommitted_losses(self, exact_va, belief, loss):
        """Numerical Finding 1, tbl-dilemma: losses in percent of the
        informed firm's value at X_0 = X*/2."""
        result = exact_va.dario_dilemma(0.10, belief)
        assert result["value_loss_pct"] * 100 == pytest.approx(loss, abs=0.02)
        assert result["is_conservative"] is (belief < 0.10)

    @pytest.mark.parametrize(
        ("belief", "loss"),
        [(0.02, 40.59), (0.05, 2.69), (0.10 / 1.8, 0.46), (0.075, 0.0), (0.50, 0.0)],
    )
    def test_unrestricted_losses(self, exact_va, belief, loss):
        """With scale chosen at the switch a belief at or above 0.073 says
        to wait, as the truth does, and costs nothing."""
        result = exact_va.dario_dilemma(0.10, belief, "unrestricted")
        assert result["value_loss_pct"] * 100 == pytest.approx(loss, abs=0.02)
        assert result["waits"] is (belief > 0.073)

    def test_policies_behind_the_losses(self, exact_va):
        """The pessimist's own trigger lies below X_0, so it installs at
        once at the scale it believes best there; the optimists wait for
        their own triggers, which lie below the informed firm's."""
        low = exact_va.dario_dilemma(0.10, 0.02)
        assert low["immediate"] is True
        assert low["trigger_mismatch"] == pytest.approx(3.115e-5, rel=1e-3)
        assert low["X_mismatch"] == pytest.approx(low["X_0"])
        assert low["K_mismatch"] == pytest.approx(0.00534, abs=1e-5)
        assert low["phi_mismatch"] == pytest.approx(0.1381, abs=1e-4)
        assert low["K_optimal"] == pytest.approx(0.01578, abs=1e-5)
        for belief, X, K, phi in [
            (0.18, 0.00913, 0.01842, 0.862),
            (0.50, 0.00655, 0.01581, 0.972),
        ]:
            high = exact_va.dario_dilemma(0.10, belief)
            assert high["immediate"] is False
            assert high["X_mismatch"] == pytest.approx(X, abs=1e-5)
            assert high["K_mismatch"] == pytest.approx(K, abs=1e-5)
            assert high["phi_mismatch"] == pytest.approx(phi, abs=1e-3)

    @pytest.mark.parametrize("version", ["precommitted", "unrestricted"])
    @pytest.mark.parametrize("belief", [0.02, 0.05, 0.18, 0.50])
    def test_components_sum_to_the_loss(self, exact_va, version, belief):
        r = exact_va.dario_dilemma(0.10, belief, version)
        total = r["timing_pct"] + r["capacity_pct"] + r["allocation_pct"]
        assert total == pytest.approx(r["value_loss_pct"], abs=1e-12)
        assert r["timing_pct"] >= -1e-12

    @pytest.mark.parametrize(
        ("belief", "timing", "capacity", "allocation"),
        [
            (0.02, 8.41, -0.17, 24.23),
            (0.05, 4.04, 0.26, 4.02),
            (0.18, 0.00, 0.31, 1.01),
            (0.50, 1.54, 3.88, 7.84),
        ],
    )
    def test_decomposition(self, exact_va, belief, timing, capacity, allocation):
        """tbl-dilemma: allocation is the largest component on both sides;
        timing matters for the pessimist, capacity for the far optimist."""
        r = exact_va.dario_dilemma(0.10, belief)
        got = [100 * r[k] for k in ("timing_pct", "capacity_pct", "allocation_pct")]
        assert got == pytest.approx([timing, capacity, allocation], abs=0.02)

    def test_unrestricted_loss_is_timing_and_allocation(self, exact_va):
        r = exact_va.dario_dilemma(0.10, 0.02, "unrestricted")
        got = [100 * r[k] for k in ("timing_pct", "capacity_pct", "allocation_pct")]
        assert got == pytest.approx([19.43, -0.15, 21.31], abs=0.02)

    def test_loss_is_the_exact_value_of_a_feasible_policy(self, exact_va):
        """The mismatched value is the exact value, under the true rate, of
        a threshold policy; it reproduces the threshold valuation of
        `piecewise_option` and never exceeds the optimum."""
        from ai_lab_investment.models.piecewise_option import PiecewiseOptionModel

        pw = PiecewiseOptionModel(ModelParameters())
        for belief in (0.05, 0.18, 0.50):
            r = exact_va.dario_dilemma(0.10, belief)
            direct = pw.threshold_value(
                r["K_mismatch"], r["phi_mismatch"], r["X_mismatch"], r["X_0"]
            )
            assert r["value_mismatch"] == pytest.approx(direct, rel=1e-10)
            assert r["value_mismatch"] < r["value_optimal"]

    def test_agrees_with_the_independent_rechecks(self):
        """At the reference demand of the earlier re-checks, X^pp / 2, the
        losses reproduce `piecewise_option.dilemma_bias` (Nelder-Mead on
        the exact value) and `capability_stock.belief_mismatch`."""
        from ai_lab_investment.models.capability_stock import (
            StockSpec,
            belief_mismatch,
        )
        from ai_lab_investment.models.piecewise_option import dilemma_bias

        p = ModelParameters()
        X_pp, _, _ = SingleFirmModel(p).pure_power_trigger_capacity_phi()
        va = ValuationAnalysis(p)
        beliefs = (0.05, 0.20, 0.50)
        old = dilemma_bias(p, lambda_invest_values=beliefs)
        for belief, loss in zip(beliefs, old["loss_piecewise_pct"], strict=True):
            new = va.dario_dilemma(0.10, belief, X_0=0.5 * X_pp)["value_loss_pct"]
            assert new * 100 == pytest.approx(loss, abs=0.02)
        stock = belief_mismatch(p, StockSpec(), lambda_invest=(0.02, 0.05, 0.20))
        for belief, loss in zip((0.02, 0.05, 0.20), stock["loss_pct"], strict=True):
            new = va.dario_dilemma(0.10, belief, "unrestricted", X_0=0.5 * X_pp)
            assert new["value_loss_pct"] * 100 == pytest.approx(loss, abs=0.02)

    def test_unknown_version_raises(self, exact_va):
        with pytest.raises(ValueError, match="version must be"):
            exact_va.dario_dilemma(0.10, 0.20, "nested")

    def test_surface(self, exact_va):
        vals = np.array([0.05, 0.10, 0.20])
        surface = exact_va.dario_dilemma_surface(vals, vals)
        assert surface["value_loss_pct"].shape == (3, 3)
        assert np.all(np.diagonal(surface["value_loss_pct"]) == 0.0)
        assert np.all(surface["value_loss_pct"] >= 0.0)


class TestDilemmaMatchedErrors:
    """The asymmetry in the three metrics in which errors can be matched:
    additive (lambda), proportional (log lambda) and horizon (1 / lambda)."""

    def test_pairs(self):
        from ai_lab_investment.models.belief_mismatch import (
            additive_pair,
            horizon_pair,
            matched_pairs,
            proportional_pair,
        )

        assert additive_pair(0.10, 0.08) == pytest.approx((0.02, 0.18))
        assert proportional_pair(0.10, 5.0) == pytest.approx((0.02, 0.50))
        low, high = horizon_pair(0.10, 10.0 - 1.0 / 0.18)
        assert (1 / low - 10.0, 10.0 - 1 / high) == pytest.approx(
            (4.444, 4.444), abs=1e-3
        )
        with pytest.raises(ValueError, match="exceeds the true horizon"):
            horizon_pair(0.10, 40.0)
        pairs = matched_pairs(0.10)
        assert pairs["additive"] == pytest.approx((0.02, 0.18))
        assert pairs["proportional_low"] == pytest.approx((0.02, 0.50))
        assert pairs["proportional_high"] == pytest.approx((0.10 / 1.8, 0.18))
        assert pairs["horizon"] == pytest.approx((9.0 / 130.0, 0.18))

    @pytest.mark.parametrize(
        ("metric", "low", "high", "ratio"),
        [
            ("additive", 32.46, 1.32, 24.6),
            ("proportional_low", 32.46, 13.25, 2.45),
            ("proportional_high", 4.33, 1.32, 3.28),
            ("horizon", 1.03, 1.32, 0.776),
        ],
    )
    def test_precommitted(self, exact_va, metric, low, high, ratio):
        """The pessimist loses more in levels of lambda and in logs; in
        expected years to the switch the optimist loses slightly more."""
        m = exact_va.dario_dilemma_matched(0.10)[metric]
        assert m["loss_low"] * 100 == pytest.approx(low, abs=0.02)
        assert m["loss_high"] * 100 == pytest.approx(high, abs=0.02)
        assert m["ratio"] == pytest.approx(ratio, rel=0.01)

    def test_unrestricted_is_one_sided(self, exact_va):
        """With scale chosen at the switch only the pessimist can lose."""
        matched = exact_va.dario_dilemma_matched(0.10, version="unrestricted")
        for m in matched.values():
            assert m["loss_high"] == 0.0
            assert m["loss_low"] >= 0.0
        assert matched["additive"]["loss_low"] * 100 == pytest.approx(40.59, abs=0.02)
        assert matched["horizon"]["loss_low"] * 100 == pytest.approx(0.0, abs=1e-3)

    def test_small_equal_additive_errors(self, exact_va):
        """Locally the pessimistic side is the steeper one: the third
        derivative of the policy value is positive at both step sizes, and
        the losses at 0.10 -/+ 0.01 are ordered accordingly."""
        w3 = [exact_va.dilemma_third_derivative(0.10, h) for h in (0.005, 0.01)]
        assert all(v > 0 for v in w3)
        assert w3 == pytest.approx([543.0, 628.0], rel=0.02)
        low = exact_va.dario_dilemma(0.10, 0.09)["value_loss_pct"]
        high = exact_va.dario_dilemma(0.10, 0.11)["value_loss_pct"]
        assert low > high > 0.0
        assert exact_va.dilemma_third_derivative(0.10, 0.005, "unrestricted") == 0.0

    def test_other_true_rates(self):
        """Internet Appendix A: at true rates 0.05 and 0.20 the rankings in
        levels and at a factor of five hold; at a factor of 1.8 and in
        expected time the sign depends on the true rate."""
        from ai_lab_investment.models.belief_mismatch import (
            SingleFirmMismatch,
            matched_pairs,
        )

        expected = {
            0.05: {"additive": 8.9, "proportional_low": 2.18,
                   "proportional_high": 3.12, "horizon": 2.25},
            0.20: {"additive": 31.2, "proportional_low": 2.97,
                   "proportional_high": 0.60, "horizon": 0.24},
        }  # fmt: skip
        for truth, ratios in expected.items():
            model = SingleFirmMismatch(ModelParameters(), truth)
            for name, (low, high) in matched_pairs(truth, 0.8 * truth).items():
                got = model.matched(low, high)["ratio"]
                assert got == pytest.approx(ratios[name], rel=0.02)

    def test_ranking_across_reference_demands(self):
        """The losses are not invariant to X_0. Across X_0 = X*/4, X*/2 and
        3X*/4 the additive and proportional rankings hold and the horizon
        pair stays close to even."""
        from ai_lab_investment.models.belief_mismatch import SingleFirmMismatch

        model = SingleFirmMismatch(ModelParameters(), 0.10)
        rows = model.reference_sensitivity(
            (0.02, 9.0 / 130.0, 0.18, 0.50), (0.25, 0.5, 0.75)
        )
        table = [
            [100 * row[f"loss_{b:g}"] for b in (0.02, 9.0 / 130.0, 0.18, 0.50)]
            for row in rows
        ]
        expected = [
            [39.97, 0.34, 0.43, 4.35],
            [32.46, 1.03, 1.32, 13.25],
            [27.44, 1.99, 2.57, 22.77],
        ]
        for got, want in zip(table, expected, strict=True):
            assert got == pytest.approx(want, abs=0.02)
            assert got[0] > got[3] > got[2] > got[1]


class TestDarioDilemmaLeveraged:
    """The single firm's dilemma on the levered claims and its tail risk."""

    LEVERAGES = (0.0, 0.01, 0.05, 0.15, 0.40)

    @pytest.fixture(scope="class")
    def rows(self, exact_va):
        return {
            (lev, belief): exact_va.dario_dilemma_leveraged(0.10, belief, lev)
            for lev in self.LEVERAGES
            for belief in (0.02, 0.10, 0.18, 0.50)
        }

    def test_matched_beliefs_no_loss(self, rows):
        for lev in self.LEVERAGES:
            assert rows[lev, 0.10]["value_loss_pct"] == 0.0

    def test_losses_do_not_move_with_fairly_priced_leverage(self, rows):
        """C21: under fairly priced debt leverage leaves the expected-value
        loss where the option to stop operating puts it."""
        for lev in self.LEVERAGES:
            got = [100 * rows[lev, b]["value_loss_pct"] for b in (0.02, 0.18, 0.50)]
            assert got == pytest.approx([31.76, 1.29, 12.74], abs=0.03)

    def test_continuous_at_zero_leverage(self, rows):
        for belief in (0.02, 0.18, 0.50):
            zero, small = rows[0.0, belief], rows[0.01, belief]
            assert small["value_loss_pct"] == pytest.approx(
                zero["value_loss_pct"], abs=1e-4
            )
            assert small["default_prob_mismatch"] == pytest.approx(
                zero["default_prob_mismatch"], rel=0.05
            )

    def test_option_to_stop_lowers_the_loss_slightly(self, exact_va, rows):
        plain = exact_va.dario_dilemma(0.10, 0.50)["value_loss_pct"]
        assert plain * 100 == pytest.approx(13.25, abs=0.02)
        assert rows[0.0, 0.50]["value_loss_pct"] < plain

    @pytest.mark.parametrize(
        ("leverage", "probabilities"),
        [
            (0.0, (0.156, 0.371, 0.345, 1.795)),
            (0.01, (0.161, 0.378, 0.356, 1.841)),
            (0.05, (0.182, 0.405, 0.403, 2.030)),
            (0.15, (0.244, 0.478, 0.540, 2.562)),
            (0.40, (0.467, 0.705, 1.028, 4.285)),
        ],
    )
    def test_default_probabilities(self, rows, leverage, probabilities):
        """tbl-dilemma-tail: five-year first passage to the boundary at
        which the firm stops operating, informed firm then beliefs 0.02,
        0.18 and 0.50, in percent, fairly priced debt."""
        got = [100 * rows[leverage, 0.02]["default_prob_optimal"]] + [
            100 * rows[leverage, b]["default_prob_mismatch"] for b in (0.02, 0.18, 0.50)
        ]
        assert got == pytest.approx(probabilities, abs=0.003)

    def test_informed_firm_matches_the_credit_table(self, rows):
        """The informed firm's rows are those of tbl-credit-pd."""
        assert rows[0.0, 0.18]["default_prob_optimal"] * 100 == pytest.approx(
            0.16, abs=0.005
        )
        assert rows[0.40, 0.18]["default_prob_optimal"] * 100 == pytest.approx(
            0.47, abs=0.005
        )
        assert rows[0.0, 0.18]["distance_optimal"] == pytest.approx(6.46, abs=0.01)

    def test_distance_to_the_boundary(self, rows):
        """Both mistaken firms enter closer to the boundary than the
        informed firm, the far optimist closest; the boundary exists
        without debt and leverage shifts it."""
        for lev, want in [
            (0.0, (6.46, 5.58, 5.65, 4.12)),
            (0.40, (5.36, 4.96, 4.62, 3.40)),
        ]:
            got = [rows[lev, 0.02]["distance_optimal"]] + [
                rows[lev, b]["distance_mismatch"] for b in (0.02, 0.18, 0.50)
            ]
            assert got == pytest.approx(want, abs=0.01)
            assert got[0] > got[1] > got[3]
            assert got[0] > got[2] > got[3]

    def test_par_debt_carries_the_subsidy(self, exact_va):
        """Under par debt at r_c < r the levered objective rewards scale,
        so the pessimist's loss rises with leverage and the optimists'
        falls."""
        par = [
            100
            * exact_va.dario_dilemma_leveraged(0.10, b, 0.40, debt="par")[
                "value_loss_pct"
            ]
            for b in (0.02, 0.18, 0.50)
        ]
        assert par == pytest.approx([35.36, 0.88, 12.35], abs=0.03)

    def test_unrestricted_firm_that_waits_has_no_boundary(self, exact_va):
        r = exact_va.dario_dilemma_leveraged(0.10, 0.50, 0.40, "unrestricted")
        assert r["value_loss_pct"] == 0.0
        assert r["default_prob_mismatch"] == 0.0
        low = exact_va.dario_dilemma_leveraged(0.10, 0.02, 0.40, "unrestricted")
        assert low["value_loss_pct"] * 100 == pytest.approx(40.25, abs=0.03)
        assert low["default_prob_mismatch"] * 100 == pytest.approx(0.705, abs=0.003)


class TestDuopolyDilemma:
    """The dilemma inside the entry equilibrium (C13), from the cache
    `duopoly_dilemma.json`; the slow tests re-solve cells of it."""

    BELIEFS = (0.02, 0.03, 0.05, 0.10 / 1.8, 9.0 / 130.0, 0.075, 0.15, 0.18, 0.20,
               0.25, 0.30, 0.40, 0.50)  # fmt: skip

    @pytest.fixture(scope="class")
    def grid(self):
        from ai_lab_investment.models.belief_mismatch import load_dilemma_grid

        return load_dilemma_grid()

    def test_grid(self, grid):
        from ai_lab_investment.models.duopoly import cached_equilibrium

        assert grid["lambda_true"] == 0.10
        assert grid["X_0"] == pytest.approx(0.5 * cached_equilibrium()["X_L"])
        assert [p["lambda_invest"] for p in grid["policies"]] == pytest.approx(
            self.BELIEFS
        )
        # Two roles, zero leverage plus four levels under two conventions.
        assert len(grid["cells"]) == len(self.BELIEFS) * 2 * 9

    @pytest.mark.parametrize(
        ("belief", "loss"),
        [
            (0.02, 47.81),
            (0.03, 24.81),
            (0.05, 11.68),
            (0.10 / 1.8, 9.62),
            (9.0 / 130.0, 4.09),
            (0.075, 1.87),
            (0.15, 0.83),
            (0.18, 1.75),
            (0.20, 2.62),
            (0.30, 10.71),
            (0.40, 24.96),
            (0.50, 31.75),
        ],
    )
    def test_mistaken_leader(self, exact_va, belief, loss):
        """tbl-duopoly-dilemma: the leader loses on both sides."""
        cell = exact_va.dario_dilemma_duopoly(0.10, belief, "leader")
        assert cell["leads"] == 1.0
        assert cell["value_loss_pct"] * 100 == pytest.approx(loss, abs=0.03)
        parts = cell["timing_pct"] + cell["capacity_pct"] + cell["allocation_pct"]
        assert parts == pytest.approx(cell["value_loss_pct"], abs=1e-10)

    def test_mistaken_follower_loses_only_by_taking_the_lead(self, exact_va):
        """A follower's post-switch policy does not involve lambda, so a
        mistaken follower that stays one loses nothing; for beliefs at or
        below 0.069 and at or above 0.40 it takes the lead and loses the
        leader's loss plus the follower's role."""
        for belief in self.BELIEFS:
            follow = exact_va.dario_dilemma_duopoly(0.10, belief, "follower")
            lead = exact_va.dario_dilemma_duopoly(0.10, belief, "leader")
            stays = 0.07 < belief < 0.35
            assert follow["leads"] == (0.0 if stays else 1.0)
            if stays:
                assert follow["value_loss_pct"] == 0.0
                assert not np.isfinite(follow["X_pre_switch"])
            else:
                assert follow["value_loss_pct"] > lead["value_loss_pct"]
                assert follow["X_entry"] == lead["X_entry"]
        losses = [
            100 * exact_va.dario_dilemma_duopoly(0.10, b, "follower")["value_loss_pct"]
            for b in (0.02, 9.0 / 130.0, 0.40, 0.50)
        ]
        assert losses == pytest.approx([49.62, 7.41, 27.56, 34.11], abs=0.03)

    @pytest.mark.parametrize(
        ("metric", "ratio"),
        [
            ("additive", 27.3),
            ("proportional_low", 1.51),
            ("proportional_high", 5.49),
            ("horizon", 2.33),
        ],
    )
    def test_matched_pairs(self, exact_va, metric, ratio):
        """The leader's pessimistic loss exceeds its optimistic loss in all
        three metrics, by a factor of 27 in levels and 1.5 at a factor of
        five in logs."""
        from ai_lab_investment.models.belief_mismatch import matched_pairs

        low, high = matched_pairs(0.10)[metric]
        got = (
            exact_va.dario_dilemma_duopoly(0.10, low)["value_loss_pct"]
            / exact_va.dario_dilemma_duopoly(0.10, high)["value_loss_pct"]
        )
        assert got == pytest.approx(ratio, rel=0.01)

    def test_policies(self, grid):
        """The pessimists' triggers lie below X_0, so they invest at once;
        the far optimist does too; the others wait for their triggers."""
        by_belief = {round(p["lambda_invest"], 6): p for p in grid["policies"]}
        for belief in self.BELIEFS:
            pol = by_belief[round(belief, 6)]
            assert pol["immediate"] == (1.0 if belief < 0.06 or belief == 0.50 else 0.0)
            assert pol["leads_before_switch"] == 1.0
        low, high = by_belief[0.02], by_belief[0.5]
        assert low["phi"] == pytest.approx(0.01, abs=1e-3)  # bound of the search
        assert (high["K"], high["phi"]) == pytest.approx((0.00258, 0.970), abs=1e-3)
        assert by_belief[0.18]["X_entry"] == pytest.approx(0.003547, rel=1e-3)

    def test_best_response_is_the_equilibrium_policy_when_followers_wait(self, grid):
        """For beliefs at which a follower waits for the switch (0.075 and
        above) the mistaken leader's best response to a rival that follows
        is the leader's policy of the equilibrium at that belief."""
        from ai_lab_investment.models.duopoly import cached_equilibrium

        for pol in grid["policies"]:
            belief = pol["lambda_invest"]
            if belief < 0.07 or pol["immediate"] or abs(belief - 0.18) < 1e-9:
                continue
            eq = cached_equilibrium(lam=belief)
            assert not np.isfinite(eq["X_F_pre_switch"])
            assert pol["X_entry"] == pytest.approx(eq["X_L"], rel=3e-3)
            assert pol["K"] == pytest.approx(eq["K_L"], rel=5e-3)
            assert pol["phi"] == pytest.approx(eq["phi_L"], abs=1e-3)
            assert pol["believed_entry_value"] == pytest.approx(
                eq["leader_value"], rel=1e-3
            )

    def test_rival_follows(self, grid):
        """Roles: in every cell in which the mistaken firm invests first,
        the informed rival prefers following to investing first, and waits
        for the switch once it follows."""
        cells = [c for c in grid["cells"] if c["leads"] == 1.0]
        assert all(not np.isfinite(c["rival_pre_switch_entry"]) for c in cells)
        margins = [c["rival_margin"] for c in cells if c["leverage"] == 0.0]
        assert len(margins) == len(self.BELIEFS) + 7
        assert min(margins) == pytest.approx(0.034, abs=0.002)

    def test_fairly_priced_leverage_leaves_the_losses(self, exact_va):
        for lev in (0.01, 0.05, 0.15, 0.40):
            got = [
                100
                * exact_va.dario_dilemma_duopoly(0.10, b, "leader", lev)[
                    "value_loss_pct"
                ]
                for b in (0.02, 0.18, 0.50)
            ]
            assert got == pytest.approx([47.81, 1.75, 31.75], abs=0.03)

    @pytest.mark.parametrize(
        ("leverage", "probabilities"),
        [
            (0.0, (0.84, 1.56, 1.64, 8.67)),
            (0.05, (0.90, 1.68, 1.78, 9.06)),
            (0.15, (1.04, 1.91, 2.06, 9.88)),
            (0.40, (1.44, 2.62, 2.92, 12.11)),
        ],
    )
    def test_leader_default_probabilities(self, exact_va, leverage, probabilities):
        """tbl-dilemma-tail: the informed leader, then beliefs 0.02, 0.18
        and 0.50, five-year first passage in percent, fairly priced debt.
        The informed leader's entries are those of tbl-credit-pd."""
        cells = [
            exact_va.dario_dilemma_duopoly(0.10, b, "leader", leverage)
            for b in (0.02, 0.18, 0.50)
        ]
        got = [100 * cells[0]["default_prob_optimal"]] + [
            100 * c["default_prob_mismatch"] for c in cells
        ]
        assert got == pytest.approx(probabilities, abs=0.01)
        distances = [cells[0]["distance_optimal"]] + [
            c["distance_mismatch"] for c in cells
        ]
        assert distances[0] > distances[1] > distances[3]

    def test_cached_cell_reproduces_from_its_policy(self, grid):
        """Valuation under the true rate, re-done from the cached policy."""
        from ai_lab_investment.models.belief_mismatch import DuopolyMismatch

        model = DuopolyMismatch(ModelParameters(), policies=grid["policies"])
        for role in ("leader", "follower"):
            fresh = model.cell(0.50, role, 0.05, "fair")
            cached = next(
                c
                for c in grid["cells"]
                if c["lambda_invest"] == 0.50
                and c["role"] == role
                and c["leverage"] == 0.05
                and c["debt"] == "fair"
            )
            for key in ("value_optimal", "value_mismatch", "default_prob_mismatch"):
                # Quadrature and root-finding differ in the last digits
                # between platforms (macOS cache, Linux CI).
                assert fresh[key] == pytest.approx(cached[key], rel=1e-7)

    def test_uncached_cell_raises(self, exact_va):
        with pytest.raises(KeyError, match="No cached duopoly dilemma"):
            exact_va.dario_dilemma_duopoly(0.10, 0.12)
        with pytest.raises(KeyError, match="lambda_true"):
            exact_va.dario_dilemma_duopoly(0.20, 0.30)

    @pytest.mark.slow
    @pytest.mark.parametrize("belief", [0.02, 0.18])
    def test_resolved_cells_match_the_cache(self, grid, belief):
        """Re-solves the mistaken firm's policy under its belief (one
        immediate investor, one that waits for its trigger) and both
        roles' losses, about two minutes each."""
        va = ValuationAnalysis(ModelParameters())
        cached = next(
            p for p in grid["policies"] if abs(p["lambda_invest"] - belief) < 1e-9
        )
        for role in ("leader", "follower"):
            fresh = va.dario_dilemma_duopoly(0.10, belief, role, solve=True)
            stored = va.dario_dilemma_duopoly(0.10, belief, role)
            assert fresh["leads"] == stored["leads"]
            assert fresh["value_loss_pct"] == pytest.approx(
                stored["value_loss_pct"], abs=2e-4
            )
            if role == "leader":
                assert fresh["X_entry"] == pytest.approx(cached["X_entry"], rel=2e-3)
                assert fresh["rival_margin"] == pytest.approx(
                    stored["rival_margin"], abs=2e-3
                )


# ------------------------------------------------------------------
# Dario's dilemma under the pure-power approximation (earlier draft)
# ------------------------------------------------------------------


class TestPurePowerDilemmaRecheck:
    """The pure-power losses against the exact ones at the reference demand
    of the earlier re-check, X^pp / 2 (moved from test_piecewise_option)."""

    @pytest.fixture(scope="class")
    def baseline_dilemma(self):
        from ai_lab_investment.models.piecewise_option import dilemma_bias

        return dilemma_bias(ModelParameters(), lambda_invest_values=(0.02, 0.20))

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
        # Fixed reference demand X_0 = X*(lambda_true)/2 for every belief.
        assert d["loss_piecewise_pct"][i_low] == pytest.approx(39.8, abs=2.0)
        assert d["loss_piecewise_pct"][i_high] == pytest.approx(0.63, abs=0.1)

    def test_training_fraction_unchanged(self, baseline_dilemma):
        d = baseline_dilemma
        for rf_phi, pw_phi in zip(d["phi_reduced"], d["phi_piecewise"], strict=True):
            assert pw_phi == pytest.approx(rf_phi, rel=1e-5)


class TestPurePowerDilemma:
    def test_matched_beliefs_no_loss(self, va):
        """When beliefs match, value loss should be zero."""
        result = va.pure_power_dilemma(lambda_true=0.20, lambda_invest=0.20)
        assert "error" not in result
        assert abs(result["value_loss"]) < 1e-8
        assert abs(result["value_loss_pct"]) < 1e-8

    def test_mismatched_beliefs_positive_loss(self, va):
        """Mismatched beliefs should produce positive value loss."""
        result = va.pure_power_dilemma(lambda_true=0.30, lambda_invest=0.10)
        assert "error" not in result
        assert result["value_loss"] >= 0.0

    def test_conservative_flag(self, va):
        """Should correctly identify conservative vs aggressive."""
        result = va.pure_power_dilemma(lambda_true=0.30, lambda_invest=0.10)
        assert "error" not in result
        assert result["is_conservative"] is True

        result2 = va.pure_power_dilemma(lambda_true=0.10, lambda_invest=0.30)
        assert "error" not in result2
        assert result2["is_conservative"] is False

    def test_dario_surface_shape(self, va):
        """Dario dilemma surface should have correct shape."""
        lt = np.array([0.1, 0.2, 0.3])
        li = np.array([0.1, 0.2])
        result = va.pure_power_dilemma_surface(lt, li)
        assert result["value_loss_pct"].shape == (3, 2)

    def test_surface_diagonal_near_zero(self, va):
        """Diagonal of the surface (matched beliefs) should be near zero."""
        vals = np.array([0.1, 0.2, 0.3])
        result = va.pure_power_dilemma_surface(vals, vals)
        diag = np.diagonal(result["value_loss_pct"])
        assert not np.any(np.isnan(diag))
        assert np.all(np.abs(diag) < 0.01)


class TestPurePowerDilemmaLeveraged:
    """Tests for the leveraged Dario's dilemma."""

    def test_matched_beliefs_no_loss(self, va):
        """When beliefs match, value loss should be zero."""
        result = va.pure_power_dilemma_leveraged(0.10, 0.10, leverage=0.40)
        assert "error" not in result
        assert abs(result["value_loss_pct"]) < 1e-6

    def test_value_losses_non_negative(self, va):
        """Mismatched beliefs produce non-negative value losses."""
        for li in [0.02, 0.50]:
            result = va.pure_power_dilemma_leveraged(0.10, li, leverage=0.40)
            assert "error" not in result
            assert result["value_loss_pct"] >= -1e-6

    def test_default_prob_consistency_with_main_method(self, va):
        """Default probs should match the standalone default_probability()."""
        result = va.pure_power_dilemma_leveraged(0.10, 0.10, leverage=0.40)
        assert "error" not in result
        # The leveraged method evaluates under p_true; create matching VA
        p_true = va.params.with_param(lam=0.10)
        va_true = ValuationAnalysis(p_true)
        from ai_lab_investment.models.base_model import SingleFirmModel

        model = SingleFirmModel(p_true)
        X, K, phi = model.pure_power_trigger_capacity_phi()
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
        r_cons = va.pure_power_dilemma_leveraged(0.10, 0.02, leverage=0.40)
        r_aggr = va.pure_power_dilemma_leveraged(0.10, 0.50, leverage=0.40)
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
            X, K, phi = model.pure_power_trigger_capacity_phi()
            assert pytest.approx(X_exp, abs=5e-6) == X
            assert phi == pytest.approx(phi_exp, abs=5e-4)
            X_D = duo.default_boundary(phi, K, 0.0, 0.0)
            assert pytest.approx(dd_exp, abs=0.01) == X / X_D

    def test_continuous_at_zero_leverage(self, va):
        """C21 (issue #177): the levered/unlevered wedge used to appear in
        full at ell = 0.01 (loss 21.58% against 22.58% unlevered, default
        probabilities 0.48% / 4.06% against zero). With the shutdown
        boundary at ell = 0 the loss and both probabilities are
        continuous, and the aggressive-to-correct ratio is 8.4 without
        any debt (7.8 at ell = 0.40)."""
        zero = va.pure_power_dilemma_leveraged(0.10, 0.50, leverage=0.0)
        small = va.pure_power_dilemma_leveraged(0.10, 0.50, leverage=0.01)
        high = va.pure_power_dilemma_leveraged(0.10, 0.50, leverage=0.40)
        assert zero["value_loss_pct"] * 100 == pytest.approx(21.585, abs=0.005)
        assert small["value_loss_pct"] == pytest.approx(
            zero["value_loss_pct"], abs=1e-6
        )
        assert high["value_loss_pct"] == pytest.approx(zero["value_loss_pct"], abs=1e-4)
        assert zero["default_prob_optimal"] * 100 == pytest.approx(0.481, abs=0.002)
        assert zero["default_prob_mismatch"] * 100 == pytest.approx(4.036, abs=0.005)
        assert small["default_prob_optimal"] * 100 == pytest.approx(0.485, abs=0.002)
        assert small["default_prob_mismatch"] * 100 == pytest.approx(4.059, abs=0.005)
        ratio = [
            d["default_prob_mismatch"] / d["default_prob_optimal"]
            for d in (zero, small, high)
        ]
        assert ratio == pytest.approx([8.39, 8.37, 7.84], abs=0.01)
        # The unlevered `pure_power_dilemma` values the claim without the
        # shutdown option (22.58%).
        plain = va.pure_power_dilemma(0.10, 0.50)["value_loss_pct"]
        assert plain * 100 == pytest.approx(22.578, abs=0.005)

    def test_aggressive_higher_default_prob(self, va):
        """Aggressive overinvestment has higher default probability."""
        r_cons = va.pure_power_dilemma_leveraged(0.10, 0.02, leverage=0.40)
        r_aggr = va.pure_power_dilemma_leveraged(0.10, 0.50, leverage=0.40)
        assert "error" not in r_cons
        assert "error" not in r_aggr
        assert r_aggr["default_prob_mismatch"] > r_cons["default_prob_mismatch"]


class TestPurePowerDilemmaAsymmetry:
    def test_underinvestment_costlier_for_equal_mismatch(self, va):
        """Numerical Finding 1: for the same |lambda_invest - lambda_true|,
        the conservative loss exceeds the aggressive loss."""
        for delta in [0.05, 0.08]:
            r_cons = va.pure_power_dilemma(0.10, 0.10 - delta)
            r_aggr = va.pure_power_dilemma(0.10, 0.10 + delta)
            assert "error" not in r_cons
            assert "error" not in r_aggr
            assert r_cons["value_loss_pct"] > r_aggr["value_loss_pct"]

    def test_baseline_loss_magnitudes(self, va):
        """Regression: paper values 26% (lambda=0.02) and 6% (lambda=0.20),
        and the asymmetry ratio 4.6 quoted in Internet Appendix E. Pinned
        to +/-0.2pp so a one-digit drift in the printed percentage fails."""
        r_cons = va.pure_power_dilemma(0.10, 0.02)
        r_aggr = va.pure_power_dilemma(0.10, 0.20)
        assert r_cons["value_loss_pct"] * 100 == pytest.approx(26.19, abs=0.2)
        assert r_aggr["value_loss_pct"] * 100 == pytest.approx(5.63, abs=0.2)
        ratio = r_cons["value_loss_pct"] / r_aggr["value_loss_pct"]
        assert ratio == pytest.approx(4.65, abs=0.05)

    def test_asymmetry_invariant_to_delta(self):
        """Section 4's delta = 0.10 robustness check: delta is a capacity
        normalization, so the dilemma percentages and the preemption
        discount are numerically unchanged. The ratio X_P / X_L^mono is
        0.555 (0.573 before the unlevered claims carried the shutdown
        option, issue #177)."""
        from ai_lab_investment.models.duopoly import DuopolyModel

        losses, discounts = [], []
        for delta in [0.03, 0.10]:
            p = ModelParameters(delta=delta)
            v = ValuationAnalysis(p)
            losses.append((
                v.pure_power_dilemma(0.10, 0.02)["value_loss_pct"],
                v.pure_power_dilemma(0.10, 0.20)["value_loss_pct"],
            ))
            eq = DuopolyModel(p, leverage=0.0).pure_power_preemption_equilibrium("L")
            discounts.append(eq["X_leader"] / eq["X_leader_monopolist"])

        assert losses[1][0] == pytest.approx(losses[0][0], rel=1e-4)
        assert losses[1][1] == pytest.approx(losses[0][1], rel=1e-4)
        assert discounts[1] == pytest.approx(discounts[0], rel=1e-4)
        assert discounts[0] == pytest.approx(0.555, abs=0.005)


# ------------------------------------------------------------------
# Value in lambda: the unexercised option and the installed firm
# (paper Remark 3, fig-lambda-option-value, Prediction 3, issue #181)
# ------------------------------------------------------------------


def _increasing_concave(values: np.ndarray) -> bool:
    return bool(np.all(np.diff(values) > 0) and np.all(np.diff(values, 2) < 0))


class TestValueInLambda:
    """Two objects, kept apart. The *option* of a firm that has not invested
    re-optimizes its policy at each lambda (fig-lambda-option-value). The
    *installed* firm holds (K, phi) and its coupon fixed: its going-concern
    value A_eff(lambda) X - (delta K + c_D)/r is increasing and concave in
    lambda iff phi > phi_underbar (Internet Appendix A), and its exact equity
    with the option to stop is checked on a grid."""

    POLICY_LAMBDAS = np.linspace(0.10, 0.50, 9)
    WIDE_LAMBDAS = np.linspace(0.02, 0.80, 33)

    @pytest.fixture(scope="class")
    def va(self):
        return ValuationAnalysis(ModelParameters())

    @pytest.fixture(scope="class")
    def single_policy(self, va):
        return va.single_firm_policy()

    @pytest.fixture(scope="class")
    def leader_policy(self):
        from ai_lab_investment.models.duopoly import cached_equilibrium

        record = cached_equilibrium(lam=0.10)
        return record["X_L"], record["K_L"], record["phi_L"]

    # -- the unexercised option ------------------------------------------

    def test_option_shape(self, va):
        lam_vals = np.array([0.05, 0.10, 0.20, 0.50])
        result = va.equity_value_vs_lambda(lam_vals)
        for key in ("lambda_values", "option_values", "triggers", "capacities"):
            assert len(result[key]) == 4

    def test_option_positive(self, va):
        lam_vals = np.array([0.10, 0.20, 0.50])
        result = va.equity_value_vs_lambda(lam_vals)
        assert np.all(np.isfinite(result["option_values"]))
        assert np.all(result["option_values"] > 0)

    def test_option_increasing_and_concave_over_policy_range(self, va):
        """Option of the uninvested firm under the pure-power approximation.
        Curvature in lambda is independent of X (F = C(lambda) X^beta_H below
        the trigger), so one evaluation point suffices."""
        vals = np.array([
            SingleFirmModel(va.params.with_param(lam=lam)).pure_power_option_value(
                0.001
            )
            for lam in self.POLICY_LAMBDAS
        ])
        assert _increasing_concave(vals)

    # -- installed firm, going concern (analytical) ----------------------

    def test_threshold_is_phi_underbar(self, va):
        r = va.installed_value_vs_lambda(np.array([0.1]), 0.01, 0.01, 0.5)
        assert r["phi_underbar"] == pytest.approx(0.1801, abs=1e-4)

    def test_closed_form_derivatives_match_finite_differences(self, va):
        lam, h = 0.10, 1e-4
        r = va.installed_value_vs_lambda(
            np.array([lam - h, lam, lam + h]), 0.009, 0.0158, 0.70
        )
        v = r["going_concern"]
        assert (v[2] - v[0]) / (2 * h) == pytest.approx(
            r["d_going_concern"][1], rel=1e-6
        )
        assert (v[2] - 2 * v[1] + v[0]) / h**2 == pytest.approx(
            r["d2_going_concern"][1], rel=1e-4
        )

    @pytest.mark.parametrize("phi", [0.20, 0.30, 0.50, 0.70, 0.95])
    def test_going_concern_increasing_concave_above_threshold(self, va, phi):
        lams = np.linspace(0.0, 2.0, 41)
        r = va.installed_value_vs_lambda(lams, 0.009, 0.0158, phi, coupon=1e-4)
        assert _increasing_concave(r["going_concern"])
        assert np.all(r["d_going_concern"] > 0)
        assert np.all(r["d2_going_concern"] < 0)

    @pytest.mark.parametrize("phi", [0.05, 0.10, 0.17])
    def test_going_concern_decreasing_convex_below_threshold(self, va, phi):
        lams = np.linspace(0.0, 2.0, 41)
        r = va.installed_value_vs_lambda(lams, 0.009, 0.0158, phi)
        assert np.all(np.diff(r["going_concern"]) < 0)
        assert np.all(np.diff(r["going_concern"], 2) > 0)

    def test_going_concern_flat_at_threshold(self, va):
        phi_u = va.installed_value_vs_lambda(np.array([0.1]), 1.0, 1.0, 0.5)[
            "phi_underbar"
        ]
        r = va.installed_value_vs_lambda(
            np.linspace(0.0, 1.0, 11), 0.009, 0.0158, phi_u
        )
        assert np.ptp(r["going_concern"]) < 1e-12

    def test_news_asymmetry_closed_form(self, va):
        """V(lam) - V(lam - h) - [V(lam + h) - V(lam)]
        = 2 h^2 X G / [(d + lam)(d + lam - h)(d + lam + h)]."""
        p = va.params
        X, K, phi, lam, h = 0.009, 0.0158, 0.70, 0.10, 0.05
        r = va.installed_value_vs_lambda(np.array([lam - h, lam, lam + h]), X, K, phi)
        v = r["going_concern"]
        d = p.r - p.mu_L
        G = (phi * K) ** p.alpha / (p.r - p.mu_H) * d - ((1 - phi) * K) ** p.alpha
        expected = 2 * h**2 * X * G / ((d + lam) * (d + lam - h) * (d + lam + h))
        assert (v[1] - v[0]) - (v[2] - v[1]) == pytest.approx(expected, rel=1e-10)
        assert expected > 0

    def test_exposure_increasing_in_phi_at_common_belief(self, va):
        """At a common lambda and (X, K), the slope, the curvature and the
        semi-elasticity of A_eff X in lambda all rise with phi."""
        phis = np.linspace(0.05, 0.99, 30)
        rows = [
            va.installed_value_vs_lambda(np.array([0.10]), 0.009, 0.0158, phi)
            for phi in phis
        ]
        slope = np.array([r["d_going_concern"][0] for r in rows])
        curv = np.array([r["d2_going_concern"][0] for r in rows])
        semi = slope / np.array([r["A_eff"][0] * 0.009 for r in rows])
        assert np.all(np.diff(slope) > 0)
        assert np.all(np.diff(curv) < 0)
        assert np.all(np.diff(semi) > 0)

    def test_exposure_hump_shaped_along_beliefs(self, va):
        """Across firms whose allocation is phi*(lambda), the semi-elasticity
        of A_eff in lambda is not monotone in phi*: it peaks near the
        baseline belief and falls among the most optimistic firms."""
        semi = {}
        for lam in (0.05, 0.10, 0.20, 0.50):
            phi = SingleFirmModel(va.params.with_param(lam=lam)).closed_form_phi_star()
            r = va.installed_value_vs_lambda(np.array([lam]), 1.0, 1.0, phi)
            semi[lam] = r["d_going_concern"][0] / r["A_eff"][0]
        assert semi[0.05] == pytest.approx(2.24, abs=0.01)
        assert semi[0.10] == pytest.approx(2.25, abs=0.01)
        assert semi[0.20] == pytest.approx(1.18, abs=0.01)
        assert semi[0.50] == pytest.approx(0.30, abs=0.01)

    # -- installed firm, exact equity with the option to stop (numerical) --

    def test_policy_values_include_the_option(self, va, single_policy):
        X, K, phi = single_policy
        r = va.installed_value_vs_lambda(self.WIDE_LAMBDAS, X, K, phi)
        assert np.all(r["equity"] > r["going_concern"])
        assert np.all(r["equity"] - r["going_concern"] < 0.01 * r["equity"])

    @pytest.mark.parametrize("leverage", [0.0, 0.40, 0.70])
    def test_single_firm_equity_at_policy(self, va, single_policy, leverage):
        """Installed monopolist at the precommitted-scale policy, par coupon."""
        X, K, phi = single_policy
        coupon = 0.05 * leverage * SingleFirmModel(va.params).investment_cost(K)
        r = va.installed_value_vs_lambda(self.WIDE_LAMBDAS, X, K, phi, coupon=coupon)
        assert np.all(np.isfinite(r["equity"]))
        assert _increasing_concave(r["equity"])

    def test_equity_depends_on_the_coupon_only_through_the_fixed_cost(self, va):
        """E(X; delta K + c) = s E(X/s; delta K) with s = (delta K + c)/(delta K):
        levered equity is unlevered equity at a rescaled demand, so its shape
        in lambda at a given distance to the boundary is the same."""
        p = va.params
        K, phi, X = 0.0158, 0.70, 0.009
        coupon = 0.4 * p.delta * K
        s = (p.delta * K + coupon) / (p.delta * K)
        lev = va.installed_value_vs_lambda(self.POLICY_LAMBDAS, X, K, phi, coupon)
        unl = va.installed_value_vs_lambda(self.POLICY_LAMBDAS, X / s, K, phi)
        np.testing.assert_allclose(lev["equity"], s * unl["equity"], rtol=1e-8)
        np.testing.assert_allclose(lev["X_default"], s * unl["X_default"], rtol=1e-8)

    @pytest.mark.parametrize("phi", [0.25, 0.30, 0.50, 0.70, 0.90, 0.99])
    def test_single_firm_equity_on_grid(self, va, phi):
        """Increasing and concave on lambda in [0.02, 0.80] at demand from 1.25
        to 20 times the highest boundary over that range (12 levels)."""
        K = 0.0158
        X_D = va.installed_value_vs_lambda(self.WIDE_LAMBDAS, 1.0, K, phi)["X_default"]
        for multiple in np.geomspace(1.25, 20.0, 12):
            r = va.installed_value_vs_lambda(
                self.WIDE_LAMBDAS, multiple * X_D.max(), K, phi
            )
            assert _increasing_concave(r["equity"]), multiple

    def test_option_overturns_the_sign_just_above_threshold(self, va):
        """At phi = 0.19 > phi_underbar the going-concern value rises in
        lambda, but with the shutdown option value falls at 1.5 times the
        boundary; it rises at three times it."""
        K, phi = 0.0158, 0.19
        X_D = va.installed_value_vs_lambda(self.WIDE_LAMBDAS, 1.0, K, phi)["X_default"]
        near = va.installed_value_vs_lambda(self.WIDE_LAMBDAS, 1.5 * X_D.max(), K, phi)
        far = va.installed_value_vs_lambda(self.WIDE_LAMBDAS, 3.0 * X_D.max(), K, phi)
        assert np.all(near["d_going_concern"] > 0)
        assert np.all(np.diff(near["equity"]) < 0)
        assert _increasing_concave(far["equity"])

    def test_concavity_fails_next_to_the_boundary(self, va):
        """The option to stop makes value convex in lambda close to the
        boundary: the result is not stated there."""
        K, phi = 0.0158, 0.70
        X_D = va.installed_value_vs_lambda(self.WIDE_LAMBDAS, 1.0, K, phi)["X_default"]
        r = va.installed_value_vs_lambda(self.WIDE_LAMBDAS, 1.01 * X_D.max(), K, phi)
        assert np.all(np.diff(r["equity"]) > 0)
        assert not np.all(np.diff(r["equity"], 2) < 0)

    @pytest.mark.parametrize("leverage", [0.0, 0.40])
    @pytest.mark.parametrize("multiple", [0.5, 1.0, 1.5])
    def test_leader_equity_at_policy(self, va, leader_policy, leverage, multiple):
        """Installed duopoly leader at (K_L, phi_L), follower dilution
        included, at multiples of the entry demand X_L."""
        X_L, K_L, phi_L = leader_policy
        coupon = 0.05 * leverage * SingleFirmModel(va.params).investment_cost(K_L)
        r = va.installed_value_vs_lambda(
            self.WIDE_LAMBDAS, multiple * X_L, K_L, phi_L, coupon, role="leader"
        )
        assert np.all(np.isfinite(r["equity"]))
        assert _increasing_concave(r["equity"])

    def test_leader_dilution_breaks_the_shape_at_low_phi(self, va, leader_policy):
        """At phi = 0.25 the follower's dilution, which arrives sooner when
        lambda is higher, makes the leader's value non-monotone in lambda,
        although the monopolist's going-concern value is increasing."""
        X_L, K_L, _ = leader_policy
        r = va.installed_value_vs_lambda(
            self.POLICY_LAMBDAS, X_L, K_L, 0.25, role="leader"
        )
        assert np.all(r["d_going_concern"] > 0)
        assert not np.all(np.diff(r["equity"]) > 0)

    def test_rejects_unknown_role(self, va):
        with pytest.raises(ValueError, match="role"):
            va.installed_value_vs_lambda(np.array([0.1]), 0.01, 0.01, 0.5, role="x")


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

    def test_decomposition_with_phi_is_at_the_model_of_record(self, va):
        """Issue #184: the policy and option value are the model of record's
        (precommitted-scale policy, exact value); pure_power=True gives the
        approximation."""
        X = 0.0046
        model = SingleFirmModel(va.params)
        exact = va.growth_option_decomposition_with_phi(X=X)
        assert exact["K_optimal"] == pytest.approx(0.015784, rel=1e-4)
        assert exact["X_trigger"] == pytest.approx(0.009258, rel=1e-4)
        assert exact["expansion_option"] == pytest.approx(
            model.option_value_with_phi(X), rel=1e-12
        )
        approx = va.growth_option_decomposition_with_phi(X=X, pure_power=True)
        assert approx["K_optimal"] == pytest.approx(0.006727, rel=1e-3)
        assert approx["expansion_option"] == pytest.approx(
            model.pure_power_option_value(X), rel=1e-12
        )

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
    """Internet Appendix G at the precommitted-scale policy of the model of
    record (issue #184); `TestCapacityGapPurePower` keeps the earlier
    draft's version."""

    def test_uses_the_precommitted_scale_policy(self, va):
        d = va.capacity_gap_decomposition(np.array([0.5]))
        assert d["K_star"] == pytest.approx(0.015784, rel=1e-4)
        assert d["X_eval"] == pytest.approx(1.5 * 0.009258, rel=1e-4)
        assert d["phi_star"] == pytest.approx(0.700856, abs=1e-6)

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

    def test_paper_values(self, va):
        """Internet Appendix G: about 80% at K/K* = 0.01, 50% at 0.1 and 26%
        at 0.3, so roughly 25-50% over [0.1, 0.3]."""
        d = va.capacity_gap_decomposition(np.array([0.01, 0.1, 0.3]))
        assert d["gap_fraction"][0] == pytest.approx(79.7, abs=0.5)
        assert d["gap_fraction"][1] == pytest.approx(50.4, abs=0.5)
        assert d["gap_fraction"][2] == pytest.approx(25.8, abs=0.5)
        assert 25.0 <= d["gap_fraction"][2] < d["gap_fraction"][1] <= 51.0

    def test_zero_crossover_near_073(self, va):
        """Internet Appendix G: the index reaches zero at K/K* ~ 0.73."""
        K_fracs = np.linspace(0.5, 1.0, 501)
        gf = va.capacity_gap_decomposition(K_fracs)["gap_fraction"]
        crossover = K_fracs[np.argmax(gf <= 0.0)]
        assert crossover == pytest.approx(0.73, abs=0.01)

    def test_policy_argument_reproduces_the_solve(self, va):
        model = SingleFirmModel(va.params)
        policy = model.optimal_trigger_capacity_phi()
        fracs = np.array([0.1, 0.3])
        solved = va.capacity_gap_decomposition(fracs)["gap_fraction"]
        given = va.capacity_gap_decomposition(fracs, policy=policy)["gap_fraction"]
        np.testing.assert_allclose(given, solved, rtol=1e-12)


class TestCapacityGapPurePower:
    """The earlier draft's diagnostic, at the pure-power policy."""

    def test_earlier_draft_values(self, va):
        d = va.capacity_gap_decomposition(np.array([0.1, 0.3]), pure_power=True)
        assert d["K_star"] == pytest.approx(0.006727, rel=1e-3)
        assert d["gap_fraction"][0] == pytest.approx(50.1, abs=0.5)
        assert d["gap_fraction"][1] == pytest.approx(26.0, abs=0.5)

    def test_zero_crossover_near_077(self, va):
        K_fracs = np.linspace(0.5, 1.0, 501)
        gf = va.capacity_gap_decomposition(K_fracs, pure_power=True)["gap_fraction"]
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
        """tbl-fixedpie (issue #182), two layers.

        Exact primitives: against the leader of the benchmark equilibrium
        the follower's capacity is 39 times the leader's under Tullock and
        1.6 times under the arithmetic-mean benchmark, its trigger 15.9
        against 1.9 times X_H*; the post-switch game is a race under
        Tullock (leading worth 0.71 to 1.82 times following on the scan) and
        not under the benchmark (1.00 to 2.24).

        Nested pure-power game: phi_F = 0.70 under both contests; X_P over
        the pure-power single-firm trigger 0.555 against 0.606."""
        result = va.fixed_pie_robustness(leverage=0.0)
        assert result["exact_K_L"] == pytest.approx(0.004163, rel=1e-3)
        assert result["exact_tullock_K_F_over_K_L"] == pytest.approx(39.05, abs=0.05)
        assert result["exact_mean_K_F_over_K_L"] == pytest.approx(1.561, abs=0.005)
        assert result["exact_tullock_X_F_over_X_H"] == pytest.approx(15.91, abs=0.02)
        assert result["exact_mean_X_F_over_X_H"] == pytest.approx(1.931, abs=0.005)
        assert result["exact_tullock_lead_over_follow_min"] == pytest.approx(
            0.711, abs=0.005
        )
        assert result["exact_tullock_lead_over_follow_max"] == pytest.approx(
            1.816, abs=0.005
        )
        assert result["exact_mean_lead_over_follow_min"] == pytest.approx(1.0, abs=1e-9)
        assert result["exact_mean_lead_over_follow_max"] == pytest.approx(
            2.238, abs=0.005
        )
        assert result["exact_tullock_race"] is True
        assert result["exact_mean_race"] is False
        assert "nested_tullock_error" not in result
        assert "nested_mean_error" not in result
        assert abs(result["nested_tullock_phi_F"] - 0.70) < 0.01
        assert abs(result["nested_mean_phi_F"] - 0.70) < 0.01
        assert abs(result["nested_tullock_trigger_ratio"] - 0.555) < 0.005
        assert abs(result["nested_mean_trigger_ratio"] - 0.606) < 0.005
        assert abs(result["phi_underbar"] - 0.180) < 0.005

    def test_benchmark_contest_has_no_post_switch_race(self):
        """Under the arithmetic-mean benchmark the entry game of the model
        of record has no mutual-waiting value: leading beats following at
        every demand level after the switch, so the solver reports that the
        post-switch game has no rent-equalization trigger."""
        from ai_lab_investment.models.preemption_levered import LeveredPreemptionGame

        game = LeveredPreemptionGame(ModelParameters(), contest="arithmetic_mean")
        entry = game.follower_post_switch_entry(0.003)
        other = game.follower_post_switch_entry(0.3)
        # The follower's problem does not involve the leader's capacity.
        assert pytest.approx(other.K_F, rel=1e-6) == entry.K_F
        assert pytest.approx(other.X_F, rel=1e-6) == entry.X_F
        with pytest.raises(RuntimeError, match="No preemption trigger"):
            game.mutual_waiting_claim("reoptimized")
        with pytest.raises(ValueError, match="contest must be one of"):
            LeveredPreemptionGame(ModelParameters(), contest="cournot")

    def test_duopoly_dilemma_table(self, va):
        """tbl-duopoly-dilemma: 26%->38% conservative, 6%->17% aggressive;
        competition amplifies both losses but preserves the asymmetry.
        Pinned to +/-0.2pp, one digit of the printed percentage."""
        r_cons = va.pure_power_dilemma_duopoly(0.10, 0.02)
        r_aggr = va.pure_power_dilemma_duopoly(0.10, 0.20)
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
        r_cons = va.pure_power_dilemma_duopoly(0.10, 0.02)
        r_aggr = va.pure_power_dilemma_duopoly(0.10, 0.20)
        assert r_cons["X_focal"] == pytest.approx(0.005515, abs=5e-6)
        assert r_cons["X_rival"] == pytest.approx(0.004722, abs=5e-6)
        assert r_cons["phi_focal"] == pytest.approx(0.1381, abs=5e-4)
        assert r_cons["phi_rival"] == pytest.approx(0.7009, abs=5e-4)
        assert r_aggr["X_focal"] == pytest.approx(0.003999, abs=5e-6)
        assert r_aggr["X_rival"] == pytest.approx(0.004722, abs=5e-6)
        assert r_aggr["phi_focal"] == pytest.approx(0.8815, abs=5e-4)
        assert r_aggr["phi_rival"] == pytest.approx(0.7009, abs=5e-4)

    def test_dynamic_phi_table(self, va):
        """tbl-dynamic-phi at the model of record (issue #182): capacity
        held at the precommitted-scale K* = 0.0158, static revenue value
        1.87 per unit of demand. phi_1 at or below the static optimum,
        rising back toward it as reallocation gets costlier; phi_H at the
        training corner when kappa is small; value gains declining in the
        adjustment cost. The routine also returns the static threshold
        phi_underbar for reference; it does not solve the default problem.

        The table prints phi to two decimals and value gains to one, so
        the tolerances (0.005 on phi, 0.03pp on gains) are set to fail on
        a one-digit change in any printed cell.
        """
        # kappa -> (phi_1, phi_H, phi_L2, value gain %)
        expected = {
            0.0: (0.010, 0.990, 0.7009, 5.056),
            0.5: (0.5683, 0.990, 0.6569, 2.098),
            2.0: (0.6801, 0.990, 0.6872, 1.144),
            10.0: (0.6967, 0.7708, 0.6971, 0.272),
        }
        gains = []
        for kappa, (phi_1, phi_H, phi_L2, gain) in expected.items():
            r = va.two_period_dynamic_phi(adjustment_cost=kappa)
            assert "error" not in r
            assert r["phi_static"] == pytest.approx(0.7009, abs=5e-4)
            assert r["K_static"] == pytest.approx(0.015784, rel=1e-3)
            assert r["value_static"] == pytest.approx(1.8687, abs=5e-4)
            assert r["phi_1_dynamic"] == pytest.approx(phi_1, abs=0.005)
            assert r["phi_H_dynamic"] == pytest.approx(phi_H, abs=0.005)
            assert r["phi_L2_dynamic"] == pytest.approx(phi_L2, abs=0.005)
            assert r["value_gain_pct"] == pytest.approx(gain, abs=0.03)
            assert r["phi_underbar_static"] == pytest.approx(0.1801, abs=5e-4)
            # the reallocation option never raises the initial allocation
            assert r["phi_1_dynamic"] <= r["phi_static"] + 1e-3
            gains.append(r["value_gain_pct"])
        assert all(g1 >= g2 - 1e-9 for g1, g2 in itertools.pairwise(gains))
        # Longer commitment period: phi_1 = 0.10 at kappa = 0 and dt = 5.
        longer = va.two_period_dynamic_phi(dt=5.0)
        assert longer["phi_1_dynamic"] == pytest.approx(0.098, abs=0.002)

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


class TestPurePowerDilemmaCurvature:
    """Numerical Finding 1 at equal additive errors, and the W''' sign the
    appendix's Taylor argument rests on, at a fixed reference demand."""

    @pytest.fixture(scope="class")
    def va(self):
        return ValuationAnalysis(ModelParameters())

    def test_matched_pair_losses(self, va):
        cons = va.pure_power_dilemma(0.10, 0.02)["value_loss_pct"] * 100
        aggr = va.pure_power_dilemma(0.10, 0.18)["value_loss_pct"] * 100
        assert cons == pytest.approx(26.19, abs=0.2)
        assert aggr == pytest.approx(4.15, abs=0.2)
        assert cons / aggr == pytest.approx(6.3, abs=0.1)

    def test_third_derivative_positive_and_step_stable(self, va):
        w3 = {
            h: va.pure_power_dilemma_third_derivative(0.10, h)
            for h in (0.005, 0.01, 0.02)
        }
        assert all(v > 0 for v in w3.values())
        assert w3[0.005] == pytest.approx(w3[0.01], rel=0.05)

    def test_local_expansion_matches_small_errors(self, va):
        """Delta V(-h) - Delta V(+h) ~ W''' h^3 / 3 for small h, in units of W."""
        h = 0.02
        X_true, _, _ = SingleFirmModel(
            ModelParameters()
        ).pure_power_trigger_capacity_phi()
        X_0 = 0.5 * X_true
        W0 = va.pure_power_dilemma_policy_value(0.10, 0.10, X_0)
        gap = (
            va.pure_power_dilemma_policy_value(0.10, 0.10 + h, X_0)
            - va.pure_power_dilemma_policy_value(0.10, 0.10 - h, X_0)
        ) / W0
        cubic = (
            va.pure_power_dilemma_third_derivative(0.10, 0.01, X_0) * h**3 / 3.0 / W0
        )
        assert gap == pytest.approx(cubic, rel=0.15)

    def test_policy_value_rejects_x0_above_trigger(self, va):
        with pytest.raises(ValueError, match="below the policy trigger"):
            va.pure_power_dilemma_policy_value(0.10, 0.10, 1.0)
