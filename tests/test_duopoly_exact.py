"""Tests for the duopoly model of record (issue #178).

The preemption game in the exact primitives with the credit primitives of
issue #177 (`preemption_levered`), the entry points `DuopolyModel` owns, and
the cached equilibria behind the paper's duopoly numbers. Solving one
equilibrium takes one to two minutes, so the default suite checks the cached
records against the solver's own conditions (rent equalization, optimality
of the leader's policy) and the re-solves are marked ``slow``.
"""

import numpy as np
import pytest

from ai_lab_investment.models.duopoly import (
    DuopolyModel,
    DuopolySolution,
    cached_equilibrium,
    load_equilibrium_grid,
)
from ai_lab_investment.models.parameters import ModelParameters
from ai_lab_investment.models.preemption_exact import (
    ExactPreemptionGame,
    ForcedClaim,
    contest_revenue,
    solve_forced_ode,
)
from ai_lab_investment.models.preemption_levered import (
    GRID_LAMBDAS,
    LeveredPreemptionGame,
    PiecewisePowers,
    SegmentClaim,
    equilibrium_record,
    expected_entry_time,
    hitting_statistics,
)

P = ModelParameters()
# Benchmark leader policy at baseline (zero leverage, scale chosen at the switch).
K_L, PHI_L = 0.0140868, 0.6878514


@pytest.fixture(scope="module")
def games() -> dict[tuple[str, float, str], LeveredPreemptionGame]:
    out = {}
    for scale in ("envelope", "precommitted"):
        out[(scale, 0.0, "par")] = LeveredPreemptionGame(P, scale)
        out[(scale, 0.4, "par")] = LeveredPreemptionGame(P, scale, leverage=0.4)
    out[("envelope", 0.4, "fair")] = LeveredPreemptionGame(
        P, "envelope", leverage=0.4, debt="fair"
    )
    return out


def _ode_residual(value, forcing, x, sigma, mu, discount, h=1e-4):
    v0, up, dn = value(x), value(x * (1 + h)), value(x * (1 - h))
    d1 = (up - dn) / (2 * h * x)
    d2 = (up - 2 * v0 + dn) / (h * x) ** 2
    return 0.5 * sigma**2 * x**2 * d2 + mu * x * d1 - discount * v0 + forcing(x)


class TestPiecewisePowers:
    def test_add_and_evaluate(self):
        a = PiecewisePowers((1.0,), (((2.0, 1.0),), ((3.0, 0.0),)))
        b = PiecewisePowers((2.0,), ((), ((1.0, 2.0),)))
        total = a + b
        assert total.breaks == (1.0, 2.0)
        x = np.array([0.5, 1.5, 3.0])
        assert total(x) == pytest.approx([1.0, 3.0, 12.0])
        assert total.scaled(2.0)(x) == pytest.approx([2.0, 6.0, 24.0])

    def test_splice(self):
        low = PiecewisePowers((1.0, 4.0), ((), ((1.0, 1.0),), ((9.0, 0.0),)))
        high = PiecewisePowers((0.5, 3.0), ((), ((2.0, 0.0),), ((1.0, 2.0),)))
        spliced = low.splice(2.0, high)
        assert spliced.breaks == (1.0, 2.0, 3.0)
        assert spliced(np.array([0.5, 1.5, 2.5, 5.0])) == pytest.approx([
            0.0,
            1.5,
            2.0,
            25.0,
        ])

    def test_rejects_bad_input(self):
        with pytest.raises(ValueError, match="one more entry"):
            PiecewisePowers((1.0,), ((),))
        with pytest.raises(ValueError, match="increasing"):
            PiecewisePowers((2.0, 1.0), ((), (), ()))


class TestSegmentClaim:
    def test_matches_forced_claim(self, games):
        g = games[("envelope", 0.0, "par")]
        low, high = ((0.3, P.beta_H),), ((2.0, 1.0), (-0.01, 0.0))
        X_b = 0.02
        reference = ForcedClaim(P, X_b, low, high)
        claim = SegmentClaim(g.bn, g.bp, g.kappa, PiecewisePowers((X_b,), (low, high)))
        x = np.geomspace(1e-4, 10.0, 60)
        assert claim.value_slope(x)[0] == pytest.approx(reference(x), rel=1e-11)

    def test_solves_the_ode_and_reports_its_slope(self, games):
        g = games[("envelope", 0.0, "par")]
        forcing = PiecewisePowers(
            (0.01, 0.1),
            (((1.0, 1.0), (-0.02, 0.0)), ((1.4, 1.0), (0.5, P.beta_H)), ((3.0, 1.0),)),
        )
        claim = SegmentClaim(g.bn, g.bp, g.kappa, forcing)
        x = np.array([0.002, 0.03, 0.05, 0.4, 2.0])
        res = _ode_residual(
            lambda z: claim.value_slope(z)[0], forcing, x, P.sigma, P.mu_L, P.r + P.lam
        )
        assert np.max(np.abs(res) / np.abs(forcing(x))) < 1e-5
        h = 1e-6
        numeric = (
            claim.value_slope(x * (1 + h))[0] - claim.value_slope(x * (1 - h))[0]
        ) / (2 * h)
        assert claim.value_slope(x)[1] == pytest.approx(numeric, rel=1e-7)

    def test_rejects_non_integrable_forcing(self, games):
        g = games[("envelope", 0.0, "par")]
        with pytest.raises(ValueError, match="origin"):
            SegmentClaim(
                g.bn, g.bp, g.kappa, PiecewisePowers.everywhere((1.0, g.bn - 1.0))
            )
        with pytest.raises(ValueError, match="infinity"):
            SegmentClaim(
                g.bn, g.bp, g.kappa, PiecewisePowers.everywhere((1.0, g.bp + 1.0))
            )


class TestInstalledClaims:
    """Equity and debt of an installed firm: the coupled boundary, exactly."""

    @pytest.mark.parametrize("leverage", [0.0, 0.4])
    @pytest.mark.parametrize("K", [0.006727, 0.015784])
    def test_monopoly_boundary_is_the_coupled_boundary(self, games, leverage, K):
        g = games[("envelope", leverage, "par")]
        duo = DuopolyModel(P, leverage=leverage)
        phi = g.phi_star
        claims = g.installed_claims(K, phi, 0.0, 0.0, duo.coupon_payment(K))
        coupled = duo.default_boundary_coupled(phi, K, 0.0, 0.0)
        assert pytest.approx(coupled, rel=1e-10) == claims.X_D
        # ... and about 3% below the single-boundary formula.
        single = duo.default_boundary(phi, K, 0.0, 0.0)
        assert 0.025 < 1.0 - claims.X_D / single < 0.04

    def test_small_firm_boundary_below_its_post_switch_boundary(self, games):
        """A small firm facing a large rival survives in L only on hope.

        Its L-regime boundary lies below its H-regime boundary, the case the
        scalar reduction of `default_boundary_coupled` does not cover (it
        assumes the H-regime claim is alive at the L-regime boundary).
        """
        g = games[("envelope", 0.0, "par")]
        claims = g.installed_claims(0.0145, 0.689, 0.003, 0.297, 0.0)
        a = P.A_H * float(contest_revenue(0.689 * 0.0145, 0.297, P.alpha))
        X_D_H = g.m_H * (P.delta * 0.0145 / P.r) / a
        assert claims.X_D < X_D_H
        coupled = DuopolyModel(P).default_boundary_coupled(0.689, 0.0145, 0.99, 0.3)
        assert pytest.approx(coupled, rel=5e-3) == claims.X_D
        assert pytest.approx(coupled, rel=1e-4) != claims.X_D

    @pytest.mark.parametrize("leverage", [0.0, 0.4])
    def test_value_matching_and_smooth_pasting(self, games, leverage):
        g = games[("envelope", leverage, "par")]
        coupon = 0.05 * leverage * P.c * 0.0158**P.gamma
        claims = g.installed_claims(0.0158, 0.70, 0.004, 0.2, coupon)
        x = claims.X_D
        scale = float(claims.equity(10 * x)[0])
        assert float(claims.equity(x * (1 + 1e-9))[0]) / scale < 1e-8
        slope = (claims.equity(x * (1 + 1e-5))[0] - 0.0) / (x * 1e-5)
        assert abs(slope) * x / scale < 1e-4
        assert np.all(np.diff(claims.equity(np.geomspace(x, 100 * x, 200))) > 0)

    def test_equity_solves_the_coupled_system(self, games):
        g = games[("envelope", 0.4, "par")]
        K, phi = 0.0158, 0.70
        coupon = 0.05 * 0.4 * P.c * K**P.gamma
        claims = g.installed_claims(K, phi, 0.0, 0.0, coupon)
        q = P.delta * K + coupon
        a = P.A_H * (phi * K) ** P.alpha
        _, equity_H, debt_H = g._h_installed(a, q, coupon)
        flow = ((1 - phi) * K) ** P.alpha
        x = np.geomspace(1.3 * claims.X_D, 0.5, 40)
        res = _ode_residual(
            claims.equity,
            lambda z: flow * z - q + P.lam * equity_H(z),
            x,
            P.sigma,
            P.mu_L,
            P.r + P.lam,
        )
        assert np.max(np.abs(res)) / q < 1e-5
        res = _ode_residual(
            claims.debt,
            lambda z: coupon + P.lam * debt_H(z),
            x,
            P.sigma,
            P.mu_L,
            P.r + P.lam,
        )
        assert np.max(np.abs(res)) / coupon < 1e-5
        assert float(claims.debt(claims.X_D * (1 + 1e-10))[0]) == pytest.approx(
            claims.recovery, abs=1e-9 * coupon / P.r
        )

    def test_debt_bounded_by_riskless_claim_and_recovery_rule(self, games):
        g = games[("envelope", 0.4, "par")]
        K, phi = 0.0158, 0.30
        coupon = 2.0 * P.delta * K
        claims = g.installed_claims(K, phi, 0.0, 0.0, coupon)
        x = np.geomspace(claims.X_D, 1.0, 100)
        assert np.all(claims.debt(x) <= coupon / P.r + 1e-15)
        # eq-recovery: (1 - b) min{Lambda+, U}, capped at the default-free claim.
        flow = ((1 - phi) * K) ** P.alpha
        liquidation = flow * claims.X_D * g.w_L - P.delta * (1 - phi) * K / P.r
        unlevered = g.installed_claims(K, phi, 0.0, 0.0, 0.0)
        asset = float(unlevered.equity(claims.X_D)[0])
        assert liquidation > 0
        assert claims.recovery == pytest.approx(
            min(0.7 * min(liquidation, asset), coupon / P.r)
        )
        assert claims.recovery <= asset

    def test_recovery_is_zero_at_the_optimal_allocation(self, games):
        g = games[("envelope", 0.4, "par")]
        K = 0.0158
        claims = g.installed_claims(
            K, g.phi_star, 0.0, 0.0, 0.05 * 0.4 * P.c * K**P.gamma
        )
        assert claims.recovery == 0.0


class TestLeaderClaims:
    """Leader's claims while the follower waits, against independent solves."""

    @pytest.mark.parametrize("leverage", [0.0, 0.4])
    def test_h_regime_claim_boundary_conditions(self, games, leverage):
        g = games[("precommitted", leverage, "par")]
        sub = g.subgame(K_L, PHI_L)
        coupon = sub.leader_coupon(0.0086)
        q = P.delta * K_L + coupon
        T = PHI_L * K_L
        X_F = sub.post_switch.X_F
        a_duo = P.A_H * float(contest_revenue(T, sub.post_switch.K_F, P.alpha))
        _, eq_duo, debt_duo = g._h_installed(a_duo, q, coupon)
        X_D, equity, debt = g._h_leader_waiting(
            P.A_H * T**P.alpha, q, coupon, X_F, (eq_duo, debt_duo), (eq_duo, debt_duo)
        )
        # The anticipated dilution raises the boundary above the monopoly one.
        assert g.m_H * (q / P.r) / (P.A_H * T**P.alpha) < X_D < X_F
        scale = float(equity(X_F)[0])
        assert abs(float(equity(X_D * (1 + 1e-9))[0])) / scale < 1e-7
        slope = float(equity(X_D * (1 + 1e-5))[0]) / (X_D * 1e-5)
        assert abs(slope) * X_D / scale < 1e-3
        assert float(equity(X_F * (1 - 1e-12))[0]) == pytest.approx(
            float(eq_duo(X_F)[0]), rel=1e-9
        )
        if coupon > 0:
            assert float(debt(X_F * (1 - 1e-12))[0]) == pytest.approx(
                float(debt_duo(X_F)[0]), rel=1e-9
            )
            assert abs(float(debt(X_D * (1 + 1e-12))[0])) < 1e-9 * coupon / P.r

    @pytest.mark.parametrize("scale", ["precommitted", "envelope"])
    @pytest.mark.parametrize("leverage", [0.0, 0.4])
    def test_equity_matches_the_linear_complementarity_solution(
        self, games, scale, leverage
    ):
        """Finite-difference solves share only the follower's policy.

        The H-regime claim is the stopping problem with the duopoly equity
        imposed above the follower's trigger; the L-regime claim the stopping
        problem forced by it. Neither assumes a boundary.
        """
        g = games[(scale, leverage, "par")]
        sub = g.subgame(K_L, PHI_L)
        coupon = sub.leader_coupon(0.0086)
        claims = sub.leader_claims(coupon)
        q = P.delta * K_L + coupon
        T, N = PHI_L * K_L, (1 - PHI_L) * K_L
        X_F = sub.post_switch.X_F
        X = np.geomspace(1e-5 * g.X_ref, 1e7 * g.X_ref, 8001)
        if scale == "precommitted":
            K_F = np.full_like(X, sub.post_switch.K_F)
        else:
            K_F = np.interp(np.log(X), np.log(sub.table["y"]), sub.table["K"])
        duopoly, _ = g._leader_h_duopoly(X, T, K_F, q, coupon)
        equity_H, _ = solve_forced_ode(
            X,
            T**P.alpha * X - q,
            P.sigma,
            P.mu_H,
            P.r,
            obstacle=np.zeros_like(X),
            fixed=(X >= X_F, duopoly),
        )
        equity_L, stopped = solve_forced_ode(
            X,
            N**P.alpha * X - q + P.lam * np.maximum(equity_H, 0.0),
            P.sigma,
            P.mu_L,
            P.r + P.lam,
            obstacle=np.zeros_like(X),
        )
        boundary = X[np.flatnonzero(stopped)[-1]]
        assert pytest.approx(boundary, rel=5e-3) == claims.X_D
        region = (X > 1.1 * claims.X_D) & (0.01 * min(sub.pre_switch.X_entry, 1e3) > X)
        assert claims.equity(X[region]) == pytest.approx(equity_L[region], rel=5e-3)

    def test_leader_boundary_above_monopoly_boundary(self, games):
        g = games[("envelope", 0.4, "par")]
        sub = g.subgame(K_L, PHI_L)
        coupon = sub.leader_coupon(0.0086)
        alone = g.installed_claims(K_L, PHI_L, 0.0, 0.0, coupon)
        assert sub.leader_claims(coupon).X_D > alone.X_D

    def test_entry_npv_is_minus_the_contribution_below_the_boundary(self, games):
        g = games[("envelope", 0.4, "par")]
        sub = g.subgame(K_L, PHI_L)
        X_D = sub.leader_claims(sub.leader_coupon(0.0086)).X_D
        outlay = P.c * K_L**P.gamma
        assert sub.leader_value(0.5 * X_D)[0] == pytest.approx(-0.6 * outlay)

    def test_precommitted_follower_entry_matches_duopoly_claim(self, games):
        """With precommitted scale the follower also enters before the switch."""
        g = games[("precommitted", 0.4, "par")]
        sub = g.subgame(K_L, PHI_L)
        pre = sub.pre_switch
        assert pre.enters
        coupon = sub.leader_coupon(0.0086)
        claims = sub.leader_claims(coupon)
        duo = g.installed_claims(
            K_L, PHI_L, (1 - pre.phi) * pre.K, pre.phi * pre.K, coupon
        )
        x = pre.X_entry * (1 - 1e-12)
        assert claims.equity(x)[0] == pytest.approx(duo.equity(x)[0], rel=1e-8)
        assert claims.debt(x)[0] == pytest.approx(duo.debt(x)[0], rel=1e-8)
        with pytest.raises(ValueError, match="pre-switch entry"):
            sub.leader_value(pre.X_entry * 1.01)


class TestFairDebt:
    def test_fair_coupon_prices_debt_at_par(self, games):
        g = games[("envelope", 0.4, "fair")]
        sub = g.subgame(K_L, PHI_L)
        credit = sub.leader_credit(0.0086)
        assert credit["debt"] == pytest.approx(credit["proceeds"], rel=1e-9)
        assert credit["coupon_rate"] > P.r
        assert credit["spread"] == pytest.approx(credit["coupon_rate"] - P.r)

    def test_par_debt_is_worth_less_than_its_proceeds(self, games):
        credit = (
            games[("envelope", 0.4, "par")].subgame(K_L, PHI_L).leader_credit(0.0086)
        )
        assert credit["coupon_rate"] == pytest.approx(0.05)
        assert 0.35 < credit["debt"] / credit["proceeds"] < 0.45

    def test_fair_debt_leaves_entry_values_almost_unchanged(self, games):
        """Under fair pricing leverage enters only through the boundary shift."""
        x = np.array([0.006, 0.0086, 0.02])
        plain = games[("envelope", 0.0, "par")].subgame(K_L, PHI_L)
        fair = games[("envelope", 0.4, "fair")].subgame(K_L, PHI_L)
        par = games[("envelope", 0.4, "par")].subgame(K_L, PHI_L)
        base_L, base_F = plain.leader_value(x), plain.follower_value(x)
        assert fair.leader_value(x) == pytest.approx(base_L, rel=2e-3)
        assert np.all(fair.follower_value(x) <= base_F)
        assert fair.follower_value(x) == pytest.approx(base_F, rel=2e-3)
        # Par debt at r_c < r transfers value to both, mostly to the follower.
        assert np.all(par.leader_value(x) > 1.01 * base_L)
        assert np.all(par.follower_value(x) > 1.09 * base_F)

    def test_follower_fair_coupon_in_the_absorbing_regime(self, games):
        g = games[("envelope", 0.4, "fair")]
        X, K = np.array([0.09, 0.5]), np.array([0.33, 0.9])
        a = P.A_H * contest_revenue(K, PHI_L * K_L, P.alpha)
        proceeds = 0.4 * P.c * K**P.gamma
        coupon = g._fair_coupon_H(X, K, a, proceeds)
        X_D = g.m_H * (P.delta * K + coupon) / (P.r * a)
        debt = coupon / P.r * (1 - (X / X_D) ** g.bn_H)
        assert debt == pytest.approx(proceeds, rel=1e-10)
        assert np.all(coupon > P.r * proceeds)
        # Proceeds beyond the debt capacity have no fair coupon.
        assert np.isnan(g._fair_coupon_H(X_D * 1.02, K, a, proceeds)).all()
        assert g.follower_h_payoff(X_D * 1.02, K, PHI_L * K_L)[0] == -np.inf

    def test_no_fair_coupon_near_the_boundary(self, games):
        g = games[("envelope", 0.4, "fair")]
        sub = g.subgame(K_L, PHI_L)
        X_D = sub.leader_claims(0.0).X_D
        with pytest.raises(ValueError, match="debt capacity"):
            sub.leader_coupon(1.05 * X_D)
        # The entry NPV there is the loss of the outlay, not an error.
        assert sub.leader_value(1.05 * X_D)[0] == pytest.approx(-P.c * K_L**P.gamma)


class TestNestedGames:
    def test_zero_leverage_adds_only_the_shutdown_option(self, games):
        plain = ExactPreemptionGame(P, "envelope").subgame(K_L, PHI_L)
        option = games[("envelope", 0.0, "par")].subgame(K_L, PHI_L)
        x = np.array([0.004, 0.0086, 0.02, 0.05])
        gain = option.leader_value(x) - plain.leader_value(x)
        # The option is worth most near the boundary; at high demand the
        # follower's own option (it enters slightly earlier) outweighs it.
        assert gain[0] > gain[1] > 0
        assert np.all(np.abs(gain[1:]) / plain.leader_value(x)[1:] < 0.004)
        assert option.follower_value(x) == pytest.approx(
            plain.follower_value(x), rel=1e-3
        )
        assert pytest.approx(plain.post_switch.X_F, rel=3e-3) == option.post_switch.X_F

    def test_continuous_at_zero_leverage(self):
        x = 0.0086
        base = LeveredPreemptionGame(P, "envelope").subgame(K_L, PHI_L)
        for debt in ("par", "fair"):
            gaps = []
            for lev in (1e-3, 1e-5):
                sub = LeveredPreemptionGame(
                    P, "envelope", leverage=lev, debt=debt
                ).subgame(K_L, PHI_L)
                credit = sub.leader_credit(x)
                gaps.append([
                    credit["X_default"] / base.leader_credit(x)["X_default"] - 1.0,
                    abs(sub.leader_value(x)[0] / base.leader_value(x)[0] - 1.0),
                    abs(sub.follower_value(x)[0] / base.follower_value(x)[0] - 1.0),
                ])
            gaps = np.array(gaps)
            assert np.all(gaps[0, 0] > 0)
            assert np.all(gaps[0] < 2e-3)
            assert np.all(gaps[1] < 2e-5)
            assert gaps[0, 0] / gaps[1, 0] == pytest.approx(100.0, rel=0.1)

    def test_rejects_bad_arguments(self):
        with pytest.raises(ValueError, match="debt must be"):
            LeveredPreemptionGame(P, debt="subsidized")
        with pytest.raises(ValueError, match="Leverage"):
            LeveredPreemptionGame(P, leverage=1.0)


class TestFixedScaleLeader:
    """The leader-scale variants reported beside the benchmark."""

    @pytest.mark.parametrize("scale", ["envelope", "precommitted"])
    def test_no_trigger_at_the_pure_power_scale(self, games, scale):
        g = games[(scale, 0.0, "par")]
        out = g.rent_equalization(*g.paper_policy())
        assert not out["exists"]
        assert out["max_gap_over_follower"] == pytest.approx(-0.053, abs=0.002)

    def test_bare_trigger_at_the_monopoly_scale(self, games):
        g = games[("envelope", 0.0, "par")]
        out = g.rent_equalization(*g.exact_monopoly_policy())
        assert out["exists"]
        assert out["X_P"] == pytest.approx(0.007683, rel=2e-3)
        assert out["max_gap_over_follower"] == pytest.approx(0.0125, abs=0.001)
        # Not unique on the scan: the gap comes back down.
        assert out["n_sign_changes"] == 2
        assert out["lead_over_wait_at_X_P"] < 1.0


class TestHittingStatistics:
    """C24: the follower's trigger is remote in probability and in time."""

    def test_reviewer_numbers_at_the_pure_power_ratio(self):
        out = hitting_statistics(P, 1.0, 44.0)
        assert out["no_switch"] == pytest.approx(0.076, abs=0.001)
        assert out["before_switch"] == pytest.approx(0.0003, abs=0.00005)
        assert out["expected_time_after_switch"] == pytest.approx(131.6, abs=0.1)
        assert out["after_switch"] == 1.0

    def test_probabilities_against_closed_forms(self):
        s2 = P.sigma**2
        nu = P.mu_L - 0.5 * s2
        d = np.log(10.0)
        out = hitting_statistics(P, 1.0, 10.0)
        assert out["no_switch"] == pytest.approx(np.exp(2 * nu * d / s2))
        theta = (-nu + np.sqrt(nu**2 + 2 * s2 * P.lam)) / s2
        assert out["before_switch"] == pytest.approx(10.0**-theta)
        # theta is a root of the L-regime operator with killing at lambda.
        assert 0.5 * s2 * theta * (theta - 1) + P.mu_L * theta - P.lam == pytest.approx(
            0.0, abs=1e-12
        )

    def test_downward_passage(self):
        out = hitting_statistics(P, 1.0, 0.2)
        # Negative L-regime log drift: reached for sure without a switch.
        assert out["no_switch"] == 1.0
        assert 0.0 < out["before_switch"] < 1.0
        nu_H = P.mu_H - 0.5 * P.sigma**2
        assert out["after_switch"] == pytest.approx(0.2 ** (2 * nu_H / P.sigma**2))
        assert out["expected_time_after_switch"] == np.inf

    def test_expected_entry_time_by_simulation(self):
        rng = np.random.default_rng(0)
        d, n = np.log(4.0), 400_000
        tau = rng.exponential(1.0 / P.lam, n)
        nu_L = P.mu_L - 0.5 * P.sigma**2
        nu_H = P.mu_H - 0.5 * P.sigma**2
        y = nu_L * tau + P.sigma * np.sqrt(tau) * rng.standard_normal(n)
        simulated = np.mean(tau + np.maximum(d - y, 0.0) / nu_H)
        assert expected_entry_time(P, 1.0, 4.0) == pytest.approx(simulated, rel=0.01)
        assert expected_entry_time(P.with_param(mu_H=0.02), 1.0, 4.0) == np.inf


# ----------------------------------------------------------------------
# Cached equilibria: the numbers the paper quotes
# ----------------------------------------------------------------------

GRID = load_equilibrium_grid()


def _record(lam=0.10, leverage=0.0, debt="par", scale="envelope"):
    return cached_equilibrium(lam, scale, leverage, debt)


def _game(record) -> LeveredPreemptionGame:
    return LeveredPreemptionGame(
        P.with_param(lam=record["lam"]),
        record["scale"],
        leverage=record["leverage"],
        debt=record["debt"],
    )


# Cells cheap enough to re-check in the default suite (no pre-switch entry of
# the follower under fair debt, which makes each subgame slow).
FAST_CELLS = [
    r
    for r in GRID
    if r["leverage"] == 0.0
    or r["lam"] in (0.10, 0.30)
    or (r["debt"] == "par" and r["lam"] != 0.05)
]


class TestCachedEquilibria:
    """The cache is checked against the conditions that define an equilibrium."""

    def test_cache_covers_the_grid(self):
        from ai_lab_investment.models.preemption_levered import grid_cells

        cells = {(r["lam"], r["scale"], r["leverage"], r["debt"]) for r in GRID}
        assert cells == set(grid_cells())
        assert all(r["exists"] == 1.0 for r in GRID)
        # Every cell shows one sign change of the gap on its scan.
        assert all(r["n_sign_changes"] == 1.0 for r in GRID)

    def test_records_carry_their_scan(self):
        from ai_lab_investment.models.preemption_levered import SCAN_OVERRIDES

        assert set(SCAN_OVERRIDES) == {
            (0.05, "envelope", 0.40, "fair"),
            (0.05, "envelope", 0.65, "fair"),
        }
        for r in GRID:
            cell = (r["lam"], r["scale"], r["leverage"], r["debt"])
            points, (low, high) = SCAN_OVERRIDES.get(cell, (25, (0.03, 300.0)))
            assert (r["scan_points"], r["scan_low"], r["scan_high"]) == (
                points,
                low,
                high,
            )
            # The trigger lies strictly inside the scanned range.
            assert low * r["X_H"] < r["X_P"] < high * r["X_H"]

    def test_lookup(self):
        assert _record()["X_P"] == pytest.approx(0.008570, rel=1e-3)
        with pytest.raises(KeyError, match="No cached equilibrium"):
            cached_equilibrium(lam=0.123)

    @pytest.mark.parametrize(
        "record",
        FAST_CELLS,
        ids=lambda r: f"{r['scale'][:3]}-lam{r['lam']}-lev{r['leverage']}-{r['debt']}",
    )
    def test_rent_equalization_and_leader_optimality(self, record):
        game = _game(record)
        X_P, K, phi = record["X_P"], record["K_L"], record["phi_L"]
        sub = game.subgame(K, phi)
        lead = float(sub.leader_value(X_P)[0])
        follow = float(sub.follower_value(X_P)[0])
        assert lead == pytest.approx(record["leader_value"], rel=1e-6)
        assert abs(lead - follow) / follow < 5e-5
        # No nearby policy gives the leader more.
        for dk, dphi in ((0.03, 0.0), (-0.03, 0.0), (0.0, 0.01), (0.0, -0.01)):
            other = game.subgame(K * np.exp(dk), phi + dphi)
            assert float(other.leader_value(X_P)[0]) < lead
        assert record["X_F"] == pytest.approx(sub.post_switch.X_F, rel=1e-6)
        assert record["X_F"] > X_P
        assert record["X_F_pre_switch"] > X_P

    def test_brute_force_leader_policy_at_baseline(self, games):
        record = _record()
        game = games[("envelope", 0.0, "par")]
        K_grid = record["K_L"] * np.geomspace(1 / 6, 6, 25)
        phi_grid = np.linspace(0.3, 0.95, 27)
        values = np.array([
            [float(game.subgame(k, f).leader_value(record["X_P"])[0]) for f in phi_grid]
            for k in K_grid
        ])
        i, j = np.unravel_index(int(np.argmax(values)), values.shape)
        assert K_grid[i] == pytest.approx(record["K_L"], rel=0.2)
        assert phi_grid[j] == pytest.approx(record["phi_L"], abs=0.03)
        assert values.max() <= record["leader_value"] * (1 + 1e-9)

    @pytest.mark.slow
    @pytest.mark.parametrize(
        ("leverage", "debt"), [(0.0, "par"), (0.40, "par"), (0.40, "fair")]
    )
    def test_resolve_baseline(self, leverage, debt):
        cached = _record(leverage=leverage, debt=debt)
        fresh = equilibrium_record(P, "envelope", leverage, debt)
        for key in ("X_P", "K_L", "phi_L", "X_F", "K_F", "X_D_leader", "spread"):
            if np.isnan(cached[key]):
                continue
            # Nelder-Mead tolerances make a solve reproducible to about 1e-4.
            assert fresh[key] == pytest.approx(cached[key], rel=5e-4), key

    @pytest.mark.slow
    def test_model_solve_reports_the_variants(self):
        solution = DuopolyModel(P).solve()
        assert isinstance(solution, DuopolySolution)
        assert pytest.approx(_record()["X_P"], rel=1e-4) == solution.X_P
        assert not solution.single_firm["invests_before_switch"]
        assert not solution.fixed_scale["pure_power"]["exists"]
        assert solution.fixed_scale["monopoly"]["exists"]
        assert solution.pure_power["X_leader"] == pytest.approx(0.002621, rel=1e-3)
        assert solution.preemption_ratio == pytest.approx(0.926, abs=0.002)


class TestBenchmarkEquilibrium:
    """Baseline numbers quoted in Section 2.5 and Internet Appendix B."""

    def test_baseline_policies(self):
        r = _record()
        assert r["X_P"] == pytest.approx(0.008570, rel=1e-3)
        assert r["K_L"] == pytest.approx(0.014087, rel=1e-3)
        assert r["phi_L"] == pytest.approx(0.68785, abs=1e-4)
        assert r["phi_star"] == pytest.approx(0.70086, abs=1e-5)
        assert r["X_F"] == pytest.approx(0.085886, rel=1e-3)
        assert r["K_F"] == pytest.approx(0.31746, rel=1e-3)
        assert np.isinf(r["X_F_pre_switch"])
        assert r["lead_over_wait"] == pytest.approx(1.223, abs=0.002)
        assert r["n_sign_changes"] == 1.0
        assert r["X_D_leader"] == pytest.approx(0.0014558, rel=1e-3)
        assert r["distance_to_default"] == pytest.approx(5.887, abs=0.005)

    def test_solution_object(self):
        solution = DuopolySolution(_record(), {"X_star": 0.009258})
        assert solution.exists
        assert solution.allocation_gap == pytest.approx(-0.0186, abs=2e-4)
        assert solution.scale_ratio == pytest.approx(22.5, abs=0.1)
        assert solution.trigger_ratio == pytest.approx(10.02, abs=0.02)
        assert solution.preemption_ratio == pytest.approx(0.926, abs=0.001)
        assert np.isnan(DuopolySolution(_record()).preemption_ratio)
        with pytest.raises(AttributeError):
            _ = solution.no_such_field

    def test_shutdown_option_lowers_the_trigger(self):
        """Against the game without the option (tests/test_preemption_exact.py)."""
        r = _record()
        assert r["X_P"] / 0.00896 - 1.0 == pytest.approx(-0.043, abs=0.003)
        assert r["K_L"] / 0.01471 - 1.0 == pytest.approx(-0.042, abs=0.003)

    def test_precommitted_scale_variant(self):
        pre = _record(scale="precommitted")
        assert pre["X_P"] == pytest.approx(0.008395, rel=1e-3)
        assert pre["K_L"] == pytest.approx(0.01375, rel=3e-3)
        # The follower would also enter before the switch, far above X_P.
        assert pre["X_F_pre_switch"] == pytest.approx(0.314, abs=0.002)
        # The order of moves does not depend on the scale assumption.
        assert pre["assigned_X_L"] == pytest.approx(0.003396, rel=5e-3)
        assert pre["assigned_follower_over_leader"] == pytest.approx(1.101, abs=0.003)

    def test_distance_from_the_nested_approximation(self):
        r = _record()
        pp = DuopolyModel(P).pure_power_preemption_equilibrium()
        solution = DuopolySolution(
            r, pure_power={k: float(v) for k, v in pp.items() if k[0] in "XK"}
        )
        error = solution.pure_power_error()
        assert error["X_P"] == pytest.approx(-0.694, abs=0.002)
        assert error["K_L"] == pytest.approx(-0.522, abs=0.002)
        assert error["X_F"] == pytest.approx(0.383, abs=0.002)
        assert error["K_F"] == pytest.approx(-0.185, abs=0.002)

    def test_leader_boundary_above_installed_monopolist(self, games):
        r = _record()
        alone = games[("envelope", 0.0, "par")].installed_claims(
            r["K_L"], r["phi_L"], 0.0, 0.0, 0.0
        )
        assert r["X_D_leader"] / alone.X_D - 1.0 == pytest.approx(0.089, abs=0.003)

    def test_follower_option_to_stop_moves_its_policy_little(self, games):
        r = _record()
        option = games[("envelope", 0.0, "par")].subgame(r["K_L"], r["phi_L"])
        plain = ExactPreemptionGame(P, "envelope").subgame(r["K_L"], r["phi_L"])
        assert 0 < 1 - option.post_switch.X_F / plain.post_switch.X_F < 0.002
        assert 0 < 1 - option.post_switch.K_F / plain.post_switch.K_F < 0.002

    def test_follower_capacity_condition_of_proposition_3(self):
        """Without the option to stop, K_F solves the scalar condition."""
        r = _record()
        plain = ExactPreemptionGame(P, "envelope")
        entry = plain.post_switch_entry(r["phi_L"] * r["K_L"])
        K, T = entry.K_F, entry.T_L
        s_F = K**P.alpha / (K**P.alpha + T**P.alpha)
        theta = P.delta * K / P.r + P.c * K**P.gamma
        K_theta_prime = P.delta * K / P.r + P.gamma * P.c * K**P.gamma
        b = P.beta_H
        assert P.alpha * b * (2 - s_F) * theta == pytest.approx(
            (b - 1) * K_theta_prime, rel=1e-9
        )
        assert (
            pytest.approx(b / (b - 1) * theta / (P.A_H * K**P.alpha * s_F), rel=1e-12)
            == entry.X_F
        )
        assert (b - 1) / (2 * P.alpha * b) < 1 < P.gamma * (b - 1) / (P.alpha * b)


class TestBeliefs:
    """Proposition 3(ii), (iv), (v) across arrival rates (C20 for the duopoly)."""

    LAMS = (0.03, 0.05, 0.075, 0.10, 0.15, 0.20, 0.25, 0.30, 0.40, 0.50)

    def _column(self, key):
        return np.array([_record(lam)[key] for lam in self.LAMS])

    def test_trigger_exists_where_the_single_firm_waits(self):
        from ai_lab_investment.models.base_model import SingleFirmModel

        for lam in self.LAMS:
            single = SingleFirmModel(P.with_param(lam=lam)).solve()
            assert single.invests_before_switch == (lam < 0.0729)
            assert _record(lam)["exists"] == 1.0
            assert _record(lam)["n_sign_changes"] == 1.0

    def test_trigger_and_capacity_hump_shaped(self):
        for key in ("X_P", "K_L"):
            values = self._column(key)
            peak = int(np.argmax(values))
            assert self.LAMS[peak] == 0.10
            assert np.all(np.diff(values[: peak + 1]) > 0)
            assert np.all(np.diff(values[peak:]) < 0)
        assert _record(0.03)["X_P"] == pytest.approx(0.0001354, rel=2e-3)
        assert _record(0.50)["X_P"] == pytest.approx(0.0014439, rel=2e-3)
        assert _record(0.03)["K_L"] == pytest.approx(2.81e-5, rel=0.01)
        assert _record(0.50)["K_L"] == pytest.approx(0.002082, rel=2e-3)

    def test_leader_allocation_below_phi_star_and_converging(self):
        gap = 1.0 - self._column("phi_L") / self._column("phi_star")
        assert np.all(gap > 0)
        assert np.all(np.diff(gap) < 0)
        assert gap[0] == pytest.approx(0.186, abs=0.003)
        assert gap[3] == pytest.approx(0.0186, abs=0.0003)
        assert gap[-1] == pytest.approx(0.0022, abs=0.0002)

    def test_distance_to_boundary_hump_shaped(self):
        distance = self._column("distance_to_default")
        assert self.LAMS[int(np.argmax(distance))] == 0.10
        assert np.all(np.diff(distance[3:]) < 0)
        assert distance[-1] == pytest.approx(4.13, abs=0.01)

    def test_leading_beats_mutual_waiting(self):
        ratio = self._column("lead_over_wait")
        assert ratio.min() == pytest.approx(1.05, abs=0.01)
        assert ratio.max() == pytest.approx(1.28, abs=0.01)


class TestOrderOfMoves:
    """X_P is where both firms want to lead, not the date of first investment.

    The trigger of a firm that knows it will lead (`leader_assigned_entry`)
    lies below the rent-equalization trigger at every arrival rate, so the
    game has a second-mover advantage between the two.
    """

    def test_assigned_leader_enters_below_rent_equalization(self):
        ratios, advantage = [], []
        for lam in TestBeliefs.LAMS:
            r = _record(lam)
            assert r["assigned_below_rent_equalization"] == 1.0
            assert r["assigned_coefficient_ratio"] > 1.0
            assert r["assigned_follower_over_leader"] > 1.0
            ratios.append(r["assigned_X_L"] / r["X_P"])
            advantage.append(r["assigned_follower_over_leader"])
        # The two triggers converge as the switch is believed to be nearer.
        assert np.all(np.diff(ratios[3:]) > 0)
        assert ratios[-1] == pytest.approx(0.988, abs=0.004)
        assert np.all(np.diff(advantage[3:]) < 0)

    def test_baseline(self):
        r = _record()
        assert r["assigned_X_L"] == pytest.approx(0.003394, rel=5e-3)
        assert r["assigned_X_L"] / r["X_P"] == pytest.approx(0.396, abs=0.003)
        assert r["assigned_K_L"] == pytest.approx(0.004213, rel=0.01)
        assert r["assigned_follower_over_leader"] == pytest.approx(1.103, abs=0.003)
        assert r["assigned_coefficient_ratio"] == pytest.approx(1.858, abs=0.01)
        solution = DuopolySolution(r)
        assert solution.second_mover_advantage
        assert not DuopolySolution(
            _record(leverage=0.40, debt="par")
        ).second_mover_advantage

    def test_leading_below_x_p_beats_waiting_for_it(self, games):
        """Direct check at 0.8 X_P: h(X) = [L*(X) - W(X)] X^{-beta_L^+}."""
        r = _record()
        game = games[("envelope", 0.0, "par")]
        wait = game.mutual_waiting_claim("reoptimized")
        start = (r["K_L"], r["phi_L"])

        def coefficient(X):
            _, _, lead = game.leader_best_policy(X, start)
            return (lead - float(wait(X)[0])) * X ** (-game.bp), lead

        h_P, lead_P = coefficient(r["X_P"])
        assert lead_P == pytest.approx(r["leader_value"], rel=1e-6)
        X = 0.8 * r["X_P"]
        h, lead = coefficient(X)
        # Investing at X is worth more than waiting for X_P ...
        waiting_for_X_P = float(wait(X)[0]) + h_P * X**game.bp
        assert lead > 1.01 * waiting_for_X_P
        assert h / h_P == pytest.approx(1.245, abs=0.01)
        # ... although following is the better role there.
        K, phi, _ = game.leader_best_policy(X, start)
        assert float(game.subgame(K, phi).follower_value(X)[0]) > 1.01 * lead

    def test_post_switch_game_is_a_race(self):
        """After the switch the order is the standard one.

        The mutual-waiting value prices the post-switch game by rent
        equalization. There the trigger of an assigned leader, which
        maximizes L*(X) X^{-beta_H}, lies above the rent-equalization trigger
        and leading is the better role between the two, so that game is a
        preemption race and the value used for it is the right one.
        """
        game = ExactPreemptionGame(P, "envelope")
        game.mutual_waiting_claim("reoptimized")
        X_PH = game.post_switch_trigger
        assert pytest.approx(0.000387, rel=5e-3) == X_PH
        multiples = np.array([0.5, 1.0, 2.0, 3.0, 5.0, 8.0, 12.0])
        coefficient, advantage = [], []
        for m in multiples:
            _, lead, follow = game.post_switch_leader_policy(float(m * X_PH))
            coefficient.append(lead * (m * X_PH) ** (-P.beta_H))
            advantage.append(lead / follow)
        peak = int(np.argmax(coefficient))
        assert multiples[peak] in (3.0, 5.0)
        assert np.all(np.diff(coefficient[: peak + 1]) > 0)
        assert advantage[1] == pytest.approx(1.0, abs=1e-6)
        assert np.all(np.array(advantage[2:]) > 1.1)

    @pytest.mark.slow
    def test_resolve_assigned_trigger(self, games):
        from ai_lab_investment.models.preemption_levered import leader_assigned_entry

        r = _record()
        out = leader_assigned_entry(
            games[("envelope", 0.0, "par")], r["X_P"], (r["K_L"], r["phi_L"])
        )
        assert out["X_L"] == pytest.approx(r["assigned_X_L"], rel=2e-3)
        assert out["follower_over_leader"] == pytest.approx(
            r["assigned_follower_over_leader"], abs=1e-3
        )


class TestSpreadAtEntry:
    """C23: the leader's spread and distance to default at X_P across lambda."""

    @pytest.mark.parametrize("leverage", [0.40, 0.65])
    @pytest.mark.parametrize("debt", ["par", "fair"])
    def test_shape(self, leverage, debt):
        records = [_record(lam, leverage, debt) for lam in GRID_LAMBDAS]
        spread = np.array([1e4 * r["spread"] for r in records])
        distance = np.array([r["distance_to_default"] for r in records])
        # Risky from the first unit: recovery is zero in every cell.
        assert np.all(spread > 20)
        assert all(r["recovery"] == 0.0 for r in records)
        # Not weakly increasing in lambda: U-shaped, minimum in the interior.
        low = int(np.argmin(spread))
        assert 0 < low < len(spread) - 1
        assert GRID_LAMBDAS[low] in (0.15, 0.20, 0.25, 0.30)
        assert np.all(np.diff(spread[: low + 1]) < 0)
        assert np.all(np.diff(spread[low:]) > 0)
        # The distance to default falls with lambda from 0.10 on.
        assert np.all(np.diff(distance[1:]) < 0)

    def test_levels(self):
        def spreads(leverage, debt):
            return [
                round(1e4 * _record(lam, leverage, debt)["spread"], 1)
                for lam in (0.10, 0.20, 0.50)
            ]

        assert spreads(0.40, "par") == pytest.approx([35.2, 28.7, 33.8], abs=0.15)
        assert spreads(0.40, "fair") == pytest.approx([41.9, 33.7, 36.7], abs=0.15)
        assert spreads(0.65, "par") == pytest.approx([44.3, 35.2, 37.7], abs=0.15)
        assert _record(0.10, 0.40, "par")["distance_to_default"] == pytest.approx(
            5.28, abs=0.01
        )
        assert _record(0.10, 0.40, "fair")["distance_to_default"] == pytest.approx(
            4.88, abs=0.01
        )

    def test_conventions(self):
        for lam in GRID_LAMBDAS:
            for leverage in (0.40, 0.65):
                par = _record(lam, leverage, "par")
                fair = _record(lam, leverage, "fair")
                assert par["coupon_rate"] == pytest.approx(0.05)
                assert par["debt_value"] < 0.45 * par["debt_proceeds"]
                assert fair["debt_value"] == pytest.approx(
                    fair["debt_proceeds"], rel=1e-9
                )
                assert fair["spread"] == pytest.approx(fair["coupon_rate"] - P.r)
                assert fair["spread"] > par["spread"]
                assert fair["distance_to_default"] < par["distance_to_default"]


class TestLeverageEffects:
    """C15: which effects of leverage survive fairly priced debt (Remark 4)."""

    LEVERAGES = (0.0, 0.20, 0.40, 0.65)

    def _path(self, debt, key):
        return np.array([
            _record(leverage=lev, debt=debt)[key] for lev in self.LEVERAGES
        ])

    def test_par_debt_raises_scale_triggers_and_boundary(self):
        for key in ("K_L", "K_F", "X_P", "X_F", "X_D_leader"):
            assert np.all(np.diff(self._path("par", key)) > 0), key
        change = {
            key: self._path("par", key)[2] / self._path("par", key)[0] - 1
            for key in ("K_L", "K_F", "X_P", "X_F", "X_D_leader")
        }
        assert change["K_L"] == pytest.approx(0.68, abs=0.01)
        assert change["K_F"] == pytest.approx(0.69, abs=0.01)
        assert change["X_P"] == pytest.approx(0.36, abs=0.01)
        assert change["X_F"] == pytest.approx(0.36, abs=0.01)
        assert change["X_D_leader"] == pytest.approx(0.52, abs=0.01)

    def test_fair_debt_leaves_scale_and_triggers_almost_unchanged(self):
        for key in ("K_L", "K_F", "X_P", "X_F"):
            path = self._path("fair", key)
            change = path / path[0] - 1.0
            # Lower, not higher, and by little. At leverage 0.20 the change
            # is within the precision of a solve (about 1e-4).
            assert abs(change[1]) < 1.5e-3, key
            assert -0.008 < change[2] < 0.0, key
            assert -0.03 < change[3] < change[2], key
        x_p = self._path("fair", "X_P")
        assert x_p[2] / x_p[0] - 1 == pytest.approx(-0.003, abs=0.001)

    def test_boundary_and_distance_survive_fair_pricing(self):
        boundary = self._path("fair", "X_D_leader")
        assert np.all(np.diff(boundary) > 0)
        assert boundary[2] / boundary[0] - 1 == pytest.approx(0.20, abs=0.01)
        for debt in ("par", "fair"):
            assert np.all(np.diff(self._path(debt, "distance_to_default")) < 0)
            assert np.all(np.diff(self._path(debt, "follower_distance_to_default")) < 0)
        assert self._path("fair", "distance_to_default")[2] == pytest.approx(
            4.88, abs=0.01
        )


class TestFollowerHittingTimes:
    """C24 in the equilibrium of record."""

    def test_baseline(self):
        r = _record()
        out = hitting_statistics(P, r["X_P"], r["X_F"])
        assert out["before_switch"] == pytest.approx(r["follower_before_switch"])
        assert r["follower_before_switch"] == pytest.approx(0.0069, abs=0.0002)
        assert r["follower_no_switch"] == pytest.approx(0.209, abs=0.002)
        assert r["follower_time_after_switch"] == pytest.approx(80.2, abs=0.3)
        assert r["follower_expected_entry_time"] == pytest.approx(97.6, abs=0.3)
        assert r["follower_expected_entry_time"] == pytest.approx(
            expected_entry_time(P, r["X_P"], r["X_F"])
        )

    def test_leader_boundary(self):
        r = _record()
        assert r["leader_default_before_switch"] == pytest.approx(0.0724, abs=0.001)
        assert r["leader_default_no_switch"] == 1.0
        par = _record(leverage=0.40, debt="par")
        assert par["leader_default_before_switch"] == pytest.approx(0.085, abs=0.001)

    def test_follower_entry_is_remote_at_every_belief(self):
        times = [
            _record(lam)["follower_expected_entry_time"] for lam in TestBeliefs.LAMS
        ]
        assert min(times) == pytest.approx(97.6, abs=0.3)
        assert max(times) == pytest.approx(186.3, abs=0.5)


class TestDuopolyModelEntryPoints:
    def test_exact_game_carries_the_model_settings(self):
        game = DuopolyModel(P, leverage=0.4, coupon_rate=0.06).exact_game(debt="fair")
        assert isinstance(game, LeveredPreemptionGame)
        assert (game.leverage, game.coupon_rate, game.debt) == (0.4, 0.06, "fair")
        assert game.scale == "envelope"

    def test_unsupported_specifications_raise(self):
        with pytest.raises(ValueError, match="exogenous arrival rate"):
            DuopolyModel(P.with_param(xi=0.1, lam_0=0.05)).exact_game()
        with pytest.raises(ValueError, match="Tullock contest"):
            DuopolyModel(P, contest="fixed_pie").exact_game()
        with pytest.raises(ValueError, match="recovery rule"):
            DuopolyModel(P, recovery_rule="gross").exact_game()

    def test_hitting_statistics_wrapper(self):
        assert DuopolyModel(P).hitting_statistics(1.0, 44.0) == hitting_statistics(
            P, 1.0, 44.0
        )
