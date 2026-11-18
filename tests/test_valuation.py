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
        zero = va.dario_dilemma_leveraged(0.10, 0.50, leverage=0.0)
        small = va.dario_dilemma_leveraged(0.10, 0.50, leverage=0.01)
        high = va.dario_dilemma_leveraged(0.10, 0.50, leverage=0.40)
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
        # The unlevered dilemma of `dario_dilemma` values the claim
        # without the shutdown option (22.58%); issue #180 reconciles it.
        plain = va.dario_dilemma(0.10, 0.50)["value_loss_pct"]
        assert plain * 100 == pytest.approx(22.578, abs=0.005)

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
        discount are numerically unchanged. The ratio X_P / X_L^mono is
        0.555 (0.573 before the unlevered claims carried the shutdown
        option, issue #177)."""
        from ai_lab_investment.models.duopoly import DuopolyModel

        losses, discounts = [], []
        for delta in [0.03, 0.10]:
            p = ModelParameters(delta=delta)
            v = ValuationAnalysis(p)
            losses.append((
                v.dario_dilemma(0.10, 0.02)["value_loss_pct"],
                v.dario_dilemma(0.10, 0.20)["value_loss_pct"],
            ))
            eq = DuopolyModel(p, leverage=0.0).pure_power_preemption_equilibrium("L")
            discounts.append(eq["X_leader"] / eq["X_leader_monopolist"])

        assert losses[1][0] == pytest.approx(losses[0][0], rel=1e-4)
        assert losses[1][1] == pytest.approx(losses[0][1], rel=1e-4)
        assert discounts[1] == pytest.approx(discounts[0], rel=1e-4)
        assert discounts[0] == pytest.approx(0.555, abs=0.005)


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
        """tbl-fixedpie: phi_F = 0.70 under both contests; X_P / X_L^mono
        0.555 (Tullock) vs 0.606 (fixed pie); phi_underbar 0.18. The two
        ratios were 0.573 and 0.628 before the unlevered claims carried
        the shutdown option (issue #177)."""
        result = va.fixed_pie_robustness(leverage=0.0)
        assert "error" not in result
        assert "fixedpie_error" not in result
        assert abs(result["tullock_phi_F"] - 0.70) < 0.01
        assert abs(result["fixedpie_phi_F"] - 0.70) < 0.01
        assert abs(result["tullock_preemption_discount"] - 0.555) < 0.005
        assert abs(result["fixedpie_preemption_discount"] - 0.606) < 0.005
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
        cost. The routine also returns the static threshold phi_underbar
        for reference; it does not solve the default problem.

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
            assert r["phi_underbar_static"] == pytest.approx(0.1801, abs=5e-4)
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
        _, K_s, phi_s = model.pure_power_trigger_capacity_phi()
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
            vals.append(m.pure_power_option_value(0.001))
        vals = np.array(vals)
        assert np.all(np.diff(vals) > 0)  # increasing in lambda
        assert np.all(np.diff(vals, 2) < 0)  # concave in lambda


class TestDilemmaMatchedErrorsAndCurvature:
    """Numerical Finding 1 at equal additive errors, and the W''' sign the
    appendix's Taylor argument rests on, at a fixed reference demand."""

    @pytest.fixture(scope="class")
    def va(self):
        return ValuationAnalysis(ModelParameters())

    def test_matched_pair_losses(self, va):
        cons = va.dario_dilemma(0.10, 0.02)["value_loss_pct"] * 100
        aggr = va.dario_dilemma(0.10, 0.18)["value_loss_pct"] * 100
        assert cons == pytest.approx(26.19, abs=0.2)
        assert aggr == pytest.approx(4.15, abs=0.2)
        assert cons / aggr == pytest.approx(6.3, abs=0.1)

    def test_third_derivative_positive_and_step_stable(self, va):
        w3 = {h: va.dilemma_third_derivative(0.10, h) for h in (0.005, 0.01, 0.02)}
        assert all(v > 0 for v in w3.values())
        assert w3[0.005] == pytest.approx(w3[0.01], rel=0.05)

    def test_local_expansion_matches_small_errors(self, va):
        """Delta V(-h) - Delta V(+h) ~ W''' h^3 / 3 for small h, in units of W."""
        h = 0.02
        X_true, _, _ = SingleFirmModel(
            ModelParameters()
        ).pure_power_trigger_capacity_phi()
        X_0 = 0.5 * X_true
        W0 = va.dilemma_policy_value(0.10, 0.10, X_0)
        gap = (
            va.dilemma_policy_value(0.10, 0.10 + h, X_0)
            - va.dilemma_policy_value(0.10, 0.10 - h, X_0)
        ) / W0
        cubic = va.dilemma_third_derivative(0.10, 0.01, X_0) * h**3 / 3.0 / W0
        assert gap == pytest.approx(cubic, rel=0.15)

    def test_policy_value_rejects_x0_above_trigger(self, va):
        with pytest.raises(ValueError, match="below the policy trigger"):
            va.dilemma_policy_value(0.10, 0.10, 1.0)
