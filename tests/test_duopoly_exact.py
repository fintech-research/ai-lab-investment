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
    DEVIATION_TOLERANCE,
    GRID_LAMBDAS,
    RENT_EQUALIZATION_PREFIX,
    LeveredPreemptionGame,
    PiecewisePowers,
    SegmentClaim,
    _stopping_check,
    assigned_leader_equilibrium,
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
        # eq-recovery: (1 - b) min{Lambda+, U}, capped at the default-free claim,
        # with Lambda the inference business and its owner's option to stop.
        flow = ((1 - phi) * K) ** P.alpha
        a, c = flow * g.w_L, P.delta * (1 - phi) * K / P.r
        X_I = g.m_L * c / a
        X_D = claims.X_D
        liquidation = a * X_D - c + (c - a * X_I) * (X_D / X_I) ** g.bn
        unlevered = g.installed_claims(K, phi, 0.0, 0.0, 0.0)
        asset = float(unlevered.equity(X_D)[0])
        assert liquidation > a * X_D - c > 0
        assert claims.recovery == pytest.approx(
            min(0.7 * min(liquidation, asset), coupon / P.r)
        )
        assert claims.recovery <= asset

    def test_net_rule_omits_the_option_to_stop(self):
        g = LeveredPreemptionGame(P, "envelope", 0.4, recovery_rule="net")
        K, phi = 0.0158, 0.30
        flow = ((1 - phi) * K) ** P.alpha
        X = 0.002
        assert g.liquidation_value(flow, (1 - phi) * K, X) == pytest.approx(
            flow * X * g.w_L - P.delta * (1 - phi) * K / P.r, rel=1e-12
        )
        with pytest.raises(ValueError, match="recovery_rule"):
            LeveredPreemptionGame(P, "envelope", 0.4, recovery_rule="gross")

    def test_recovery_at_the_optimal_allocation(self, games):
        """Zero under the #177 rule; under the default rule the liquidator
        can shut the inference business down and recovers a small positive
        amount once the coupon pushes X_D above that business's own
        shutdown boundary."""
        g = games[("envelope", 0.4, "par")]
        K = 0.0158
        coupon = 0.05 * 0.4 * P.c * K**P.gamma
        net = LeveredPreemptionGame(P, "envelope", 0.4, recovery_rule="net")
        assert net.installed_claims(K, g.phi_star, 0.0, 0.0, coupon).recovery == 0.0
        claims = g.installed_claims(K, g.phi_star, 0.0, 0.0, coupon)
        assert 0.0 < claims.recovery < 0.01 * coupon / P.r


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
    """Cached record: keys without a prefix are evaluated at X_L."""
    return cached_equilibrium(lam, scale, leverage, debt)


def _at_X_P(record):
    """The record's objects at the rent-equalization trigger, without prefix."""
    n = len(RENT_EQUALIZATION_PREFIX)
    out = {k: v for k, v in record.items() if not k.startswith("rent_eq_")}
    out.update({k[n:]: v for k, v in record.items() if k.startswith("rent_eq_")})
    return out


def _rent(lam=0.10, leverage=0.0, debt="par", scale="envelope"):
    return _at_X_P(_record(lam, leverage, debt, scale))


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
        assert _rent()["X_P"] == pytest.approx(0.008570, rel=1e-3)
        with pytest.raises(KeyError, match="No cached equilibrium"):
            cached_equilibrium(lam=0.123)

    @pytest.mark.parametrize(
        "record",
        FAST_CELLS,
        ids=lambda r: f"{r['scale'][:3]}-lam{r['lam']}-lev{r['leverage']}-{r['debt']}",
    )
    def test_rent_equalization_and_leader_optimality(self, record):
        game = _game(record)
        record = _at_X_P(record)
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
        record = _rent()
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
        keys = ("X_P", "X_L", "K_L", "phi_L", "X_F", "K_F", "X_D_leader", "spread")
        rent = ("K_L", "phi_L", "X_F", "K_F", "X_D_leader", "spread")
        for key in (*keys, *(RENT_EQUALIZATION_PREFIX + k for k in rent)):
            if np.isnan(cached[key]):
                continue
            # Nelder-Mead tolerances make a solve reproducible to about 1e-4
            # at X_P; X_L is the maximizer of a flat function and is
            # reproducible to about 1e-3.
            tolerance = 5e-4 if key.startswith(("X_P", "rent_eq_")) else 3e-3
            assert fresh[key] == pytest.approx(cached[key], rel=tolerance), key
        assert fresh["equilibrium"] == 1.0

    @pytest.mark.slow
    def test_reusing_the_rent_equalization_solve(self):
        """What `write_equilibrium_grid` does unless told to start afresh."""
        cached = _record()
        fresh = equilibrium_record(P, "envelope", rent_equalization=cached)
        assert fresh["X_P"] == cached["X_P"]
        assert fresh["scan_points"] == cached["scan_points"]
        for key in ("X_L", "K_L", "follower_margin", "lcp_trigger", "rent_eq_spread"):
            if np.isnan(cached[key]):
                continue
            assert fresh[key] == pytest.approx(cached[key], rel=3e-3), key

    @pytest.mark.slow
    def test_grid_writer_reuses_the_cache(self, tmp_path):
        """`just duopoly-grid` on one cell, written to a scratch file."""
        import shutil

        from ai_lab_investment.models.duopoly import EQUILIBRIUM_GRID_PATH
        from ai_lab_investment.models.preemption_levered import (
            write_equilibrium_grid,
        )

        path = tmp_path / "grid.json"
        shutil.copy(EQUILIBRIUM_GRID_PATH, path)
        cell = (0.10, "envelope", 0.0, "par")
        (fresh,) = write_equilibrium_grid(str(path), workers=1, cells=[cell])
        cached = _record()
        assert fresh["X_P"] == cached["X_P"]
        assert fresh["X_L"] == pytest.approx(cached["X_L"], rel=3e-3)
        assert fresh["equilibrium"] == 1.0

    @pytest.mark.slow
    def test_model_solve_reports_the_variants(self):
        solution = DuopolyModel(P).solve()
        assert isinstance(solution, DuopolySolution)
        assert pytest.approx(_record()["X_P"], rel=1e-4) == solution.X_P
        assert pytest.approx(_record()["X_L"], rel=3e-3) == solution.X_L
        assert solution.equilibrium_verified
        assert not solution.single_firm["invests_before_switch"]
        assert not solution.fixed_scale["pure_power"]["exists"]
        assert solution.fixed_scale["monopoly"]["exists"]
        assert solution.pure_power["X_leader"] == pytest.approx(0.002621, rel=1e-3)
        assert solution.rent_equalization_ratio == pytest.approx(0.926, abs=0.002)
        assert solution.entry_ratio == pytest.approx(0.363, abs=0.003)


class TestBenchmarkEquilibrium:
    """Baseline numbers at the rent-equalization trigger X_P (Internet Appendix B).

    X_P is the upper bound on the date of first investment; the benchmark
    numbers at X_L are in `TestFirstInvestment`.
    """

    def test_baseline_policies(self):
        r = _rent()
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

    def test_shutdown_option_lowers_the_trigger(self):
        """Against the game without the option (tests/test_preemption_exact.py)."""
        r = _rent()
        assert r["X_P"] / 0.00896 - 1.0 == pytest.approx(-0.043, abs=0.003)
        assert r["K_L"] / 0.01471 - 1.0 == pytest.approx(-0.042, abs=0.003)

    def test_precommitted_scale_variant(self):
        pre = _rent(scale="precommitted")
        assert pre["X_P"] == pytest.approx(0.008395, rel=1e-3)
        assert pre["K_L"] == pytest.approx(0.01375, rel=3e-3)
        # The follower would also enter before the switch, far above X_P.
        assert pre["X_F_pre_switch"] == pytest.approx(0.314, abs=0.002)
        # The first investment does not depend on the scale assumption.
        pre = _record(scale="precommitted")
        assert pre["X_L"] == pytest.approx(0.003366, rel=5e-3)
        assert pre["follower_over_leader"] == pytest.approx(1.102, abs=0.003)
        assert pre["equilibrium"] == 1.0

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
        r = _rent()
        alone = games[("envelope", 0.0, "par")].installed_claims(
            r["K_L"], r["phi_L"], 0.0, 0.0, 0.0
        )
        assert r["X_D_leader"] / alone.X_D - 1.0 == pytest.approx(0.089, abs=0.003)

    def test_follower_option_to_stop_moves_its_policy_little(self, games):
        r = _rent()
        option = games[("envelope", 0.0, "par")].subgame(r["K_L"], r["phi_L"])
        plain = ExactPreemptionGame(P, "envelope").subgame(r["K_L"], r["phi_L"])
        assert 0 < 1 - option.post_switch.X_F / plain.post_switch.X_F < 0.002
        assert 0 < 1 - option.post_switch.K_F / plain.post_switch.K_F < 0.002

    def test_follower_capacity_condition_of_proposition_3(self):
        """Without the option to stop, K_F solves the scalar condition."""
        r = _rent()
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
    """Rent equalization across arrival rates (C20 for the duopoly).

    The same shapes at the benchmark trigger X_L are in `TestFirstInvestment`.
    """

    LAMS = (0.03, 0.05, 0.075, 0.10, 0.15, 0.20, 0.25, 0.30, 0.40, 0.50)

    def _column(self, key):
        return np.array([_rent(lam)[key] for lam in self.LAMS])

    def test_trigger_exists_where_the_single_firm_waits(self):
        from ai_lab_investment.models.base_model import SingleFirmModel

        for lam in self.LAMS:
            single = SingleFirmModel(P.with_param(lam=lam)).solve()
            assert single.invests_before_switch == (lam < 0.0729)
            assert _rent(lam)["exists"] == 1.0
            assert _rent(lam)["n_sign_changes"] == 1.0

    def test_trigger_and_capacity_hump_shaped(self):
        for key in ("X_P", "K_L"):
            values = self._column(key)
            peak = int(np.argmax(values))
            assert self.LAMS[peak] == 0.10
            assert np.all(np.diff(values[: peak + 1]) > 0)
            assert np.all(np.diff(values[peak:]) < 0)
        assert _rent(0.03)["X_P"] == pytest.approx(0.0001354, rel=2e-3)
        assert _rent(0.50)["X_P"] == pytest.approx(0.0014439, rel=2e-3)
        assert _rent(0.03)["K_L"] == pytest.approx(2.81e-5, rel=0.01)
        assert _rent(0.50)["K_L"] == pytest.approx(0.002082, rel=2e-3)

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


class TestFirstInvestment:
    """The benchmark of issue #200: one firm leads at X_L, the other follows.

    X_L is the trigger a firm chooses when it knows that its rival will
    follow; the rent-equalization trigger X_P lies above it at every cell
    of the grid and is an upper bound on the date of first investment.
    """

    def test_baseline(self):
        r = _record()
        assert r["X_L"] == pytest.approx(0.003364, rel=3e-3)
        assert r["X_L_over_X_P"] == pytest.approx(0.393, abs=0.002)
        assert r["K_L"] == pytest.approx(0.004163, rel=5e-3)
        assert r["phi_L"] == pytest.approx(0.6791, abs=3e-4)
        assert r["X_F"] == pytest.approx(0.04429, rel=3e-3)
        assert r["K_F"] == pytest.approx(0.1626, rel=3e-3)
        assert np.isinf(r["X_F_pre_switch"])
        assert r["lead_over_wait"] == pytest.approx(1.091, abs=0.002)
        assert r["follower_over_leader"] == pytest.approx(1.104, abs=0.002)
        assert r["coefficient_ratio"] == pytest.approx(1.83, abs=0.02)
        assert r["X_D_leader"] == pytest.approx(0.000700, rel=3e-3)
        assert r["distance_to_default"] == pytest.approx(4.805, abs=0.01)

    def test_solution_object(self):
        solution = DuopolySolution(_record(), {"X_star": 0.009258})
        assert solution.exists
        assert solution.equilibrium_verified
        assert solution.second_mover_advantage
        assert pytest.approx(_record()["X_L"]) == solution.X_L
        assert pytest.approx(_record()["rent_eq_K_L"]) == solution.rent_eq_K_L
        assert solution.allocation_gap == pytest.approx(-0.0311, abs=5e-4)
        assert solution.scale_ratio == pytest.approx(39.05, abs=0.2)
        assert solution.trigger_ratio == pytest.approx(13.16, abs=0.05)
        assert solution.entry_ratio == pytest.approx(0.363, abs=0.002)
        assert solution.rent_equalization_ratio == pytest.approx(0.926, abs=0.001)
        assert np.isnan(DuopolySolution(_record()).entry_ratio)
        assert np.isnan(DuopolySolution(_record()).rent_equalization_ratio)
        with pytest.raises(AttributeError):
            _ = solution.no_such_field

    def test_below_rent_equalization_in_every_cell(self):
        for r in GRID:
            assert r["X_L"] < r["X_P"]
            assert r["follower_over_leader"] > 1.0
            assert r["lead_over_wait"] > 1.0
            assert r["coefficient_ratio"] > 1.0
            assert DuopolySolution(r).second_mover_advantage == (
                r["X_L_over_X_P"] < 0.999
            )
        # The two triggers converge as the switch is believed to be nearer.
        ratios = [_record(lam)["X_L_over_X_P"] for lam in TestBeliefs.LAMS]
        advantage = [_record(lam)["follower_over_leader"] for lam in TestBeliefs.LAMS]
        assert np.all(np.diff(ratios[3:]) > 0)
        assert ratios[-1] == pytest.approx(0.975, abs=0.004)
        assert np.all(np.diff(advantage[3:]) < 0)

    def test_records_carry_the_entry_scan(self):
        from ai_lab_investment.models.preemption_levered import (
            ENTRY_SCAN,
            ENTRY_SCAN_OVERRIDES,
            SCAN_OVERRIDES,
        )

        assert set(ENTRY_SCAN_OVERRIDES) == set(SCAN_OVERRIDES)
        for r in GRID:
            cell = (r["lam"], r["scale"], r["leverage"], r["debt"])
            points, (low, high), _ = ENTRY_SCAN_OVERRIDES.get(cell, ENTRY_SCAN)
            assert r["entry_scan_points"] == points
            assert r["entry_scan_low"] == pytest.approx(low)
            # The scan may stop early where no leader policy keeps the
            # follower out; X_L is interior to what was scanned.
            assert r["entry_scan_high"] <= high * (1 + 1e-9)
            assert r["entry_scan_low"] < r["X_L_over_X_P"] < r["entry_scan_high"]

    def test_trigger_and_capacity_hump_shaped(self):
        """Proposition 3(iv) at the benchmark: the peak is at lambda = 0.15."""
        lams = TestBeliefs.LAMS
        for key in ("X_L", "K_L"):
            values = np.array([_record(lam)[key] for lam in lams])
            peak = int(np.argmax(values))
            assert lams[peak] == 0.15
            assert np.all(np.diff(values[: peak + 1]) > 0)
            assert np.all(np.diff(values[peak:]) < 0)
        assert _record(0.15)["X_L"] == pytest.approx(0.003826, rel=3e-3)
        assert _record(0.50)["X_L"] == pytest.approx(0.001407, rel=3e-3)
        assert _record(0.15)["K_L"] == pytest.approx(0.005635, rel=5e-3)
        assert _record(0.50)["K_L"] == pytest.approx(0.002006, rel=5e-3)

    def test_leader_allocation_below_phi_star_and_converging(self):
        lams = TestBeliefs.LAMS
        gap = np.array([
            1.0 - _record(lam)["phi_L"] / _record(lam)["phi_star"] for lam in lams
        ])
        assert np.all(gap > 0)
        assert np.all(np.diff(gap) < 0)
        assert gap[3] == pytest.approx(0.0311, abs=0.0005)
        assert gap[-1] == pytest.approx(0.0022, abs=0.0003)
        assert gap[0] == pytest.approx(0.140, abs=0.003)
        # Further from phi* than at X_P at every belief but the lowest.
        at_X_P = np.array([
            1.0 - _rent(lam)["phi_L"] / _rent(lam)["phi_star"] for lam in lams
        ])
        assert np.all(gap[1:] > at_X_P[1:])
        assert gap[0] < at_X_P[0]

    def test_distance_to_boundary_hump_shaped(self):
        lams = TestBeliefs.LAMS
        distance = np.array([_record(lam)["distance_to_default"] for lam in lams])
        assert lams[int(np.argmax(distance))] == 0.15
        assert np.all(np.diff(distance[4:]) < 0)
        assert distance.max() == pytest.approx(4.88, abs=0.01)
        assert distance[-1] == pytest.approx(4.12, abs=0.01)


class TestNoDeviation:
    """No-deviation conditions of the equilibrium with assigned roles.

    The cached records carry the checks of `assigned_leader_equilibrium`
    for every cell; the tests below assert them, re-derive the main ones
    at baseline from the game, and test the tools they rely on.
    """

    def test_every_cell_passes(self):
        for r in GRID:
            cell = (r["lam"], r["scale"], r["leverage"], r["debt"])
            assert r["equilibrium"] == 1.0, cell
            # Leader: no other trigger on the scan does better, and the
            # coefficient has a single peak.
            assert r["leader_best_other_trigger"] <= 1.0 + DEVIATION_TOLERANCE, cell
            assert r["coefficient_single_peaked"] == 1.0, cell
            # Leader: the stopping problem solved without a shape
            # assumption invests exactly from X_L up.
            assert r["lcp_upper_set"] == 1.0, cell
            assert r["lcp_trigger"] == pytest.approx(r["X_L"], rel=3e-3), cell
            assert r["lcp_coefficient_error"] < 1e-3, cell
            # Follower: waiting for the leader's entry (or the switch)
            # beats investing first, below X_L and between X_L and X_P.
            assert r["follower_margin"] > 0.0, cell
            assert not r["follower_margin_to_X_P"] < 0.0, cell
            # The game after a switch with neither firm installed is a race.
            assert r["post_switch_race"] == 1.0, cell
            assert r["post_switch_assigned_trigger"] > 3 * r["post_switch_trigger"]

    def test_follower_margin_bounded_by_the_role_advantage(self):
        """V_follow - L* = [F(X_L) - L*(X_L)] (X / X_L)^b + (V_lead - L*).

        The follower's condition is implied by the leader's whenever the
        follower is the better-off role at X_L; relative to its value the
        margin on the scan is at most the role advantage 1 - L*/F there.
        """
        for r in GRID:
            advantage = 1.0 - 1.0 / r["follower_over_leader"]
            assert 0.0 < r["follower_margin"] <= advantage + 2e-6
        margins = [_record(lam)["follower_margin"] for lam in TestBeliefs.LAMS]
        assert _record()["follower_margin"] == pytest.approx(0.068, abs=0.002)
        assert min(margins) == pytest.approx(0.0037, abs=0.0005)

    def test_baseline_conditions_from_the_game(self, games):
        """Leader and follower checked directly, not read from the cache."""
        r = _record()
        game = games[("envelope", 0.0, "par")]
        wait = game.mutual_waiting_claim("reoptimized")
        X_L, bp = r["X_L"], game.bp
        policy = (r["K_L"], r["phi_L"])
        h = {}
        lead = {}
        for m in (0.6, 1.0, 1.4):
            X = m * X_L
            _, _, lead[m] = game.leader_best_policy(X, policy)
            h[m] = (lead[m] - float(wait(X)[0])) * X ** (-bp)
        assert lead[1.0] == pytest.approx(r["leader_value"], rel=1e-6)
        # Leader: X_L beats the lower and the higher trigger.
        assert h[1.0] > h[0.6]
        assert h[1.0] > h[1.4]
        follow_L = float(game.subgame(*policy).follower_value(X_L)[0])
        wait_L = float(wait(X_L)[0])
        assert follow_L == pytest.approx(r["follower_value"], rel=1e-6)
        assert follow_L > lead[1.0] > wait_L
        for m in (0.6, 1.0):
            X = m * X_L
            # The follower's value before the leader's entry is the value of
            # waiting for it or for the switch ...
            waiting = float(wait(X)[0]) + (follow_L - wait_L) * m**bp
            # ... the leader's is the same with L* in place of F ...
            leading = float(wait(X)[0]) + (lead[1.0] - wait_L) * m**bp
            # ... and neither is improved on by investing at once.
            assert waiting > leading >= lead[m]
            assert waiting > 1.05 * lead[m]

    def test_follower_policy_is_a_best_response_at_the_benchmark(self):
        """Linear complementarity solve of the follower's problem at X_L."""
        r = _record()
        game = ExactPreemptionGame(P, "envelope")
        fd = game.finite_difference_subgame(r["K_L"], r["phi_L"])
        # No shape assumed: the follower never enters before the switch.
        assert np.isinf(fd["boundary"])
        grid, follower = np.asarray(fd["X"]), np.asarray(fd["follower"])
        i = int(np.argmin(np.abs(grid - r["X_L"])))
        exact = float(game.subgame(r["K_L"], r["phi_L"]).follower_value(grid[i])[0])
        assert follower[i] == pytest.approx(exact, rel=1e-5)
        # The option to stop adds little to the follower's value.
        assert r["follower_value"] == pytest.approx(exact, rel=2e-3)

    def test_stopping_check_recovers_a_known_trigger(self, games):
        """Obstacle a X - c with no forcing: trigger [b/(b-1)] c/a."""
        game = games[("envelope", 0.0, "par")]
        bp = game.bp
        X = np.geomspace(0.2, 20.0, 30)
        trigger, upper_set, coefficient = _stopping_check(
            game, X, (X - 1.0) * X ** (-bp)
        )
        exact = bp / (bp - 1.0)
        assert trigger == pytest.approx(exact, rel=2e-3)
        assert upper_set == 1.0
        assert coefficient == pytest.approx((exact - 1.0) * exact ** (-bp), rel=1e-3)

    def test_stopping_check_detects_an_interval(self, games):
        """A two-humped obstacle: the investment region is not an upper set."""
        game = games[("envelope", 0.0, "par")]
        X = np.geomspace(0.1, 100.0, 60)
        y = np.log(X)
        h = np.exp(-((y + 1.0) ** 2) / 0.05) + 0.02 * np.exp(-((y - 3.0) ** 2) / 4.0)
        trigger, upper_set, _ = _stopping_check(game, X, h)
        assert trigger == pytest.approx(np.exp(-1.0), rel=0.05)
        assert upper_set == 0.0

    @pytest.mark.slow
    def test_narrow_scan_reproduces_the_trigger(self, games):
        """The scan of `ENTRY_SCAN_OVERRIDES`, applied where the answer is known."""
        from ai_lab_investment.models.preemption_levered import ENTRY_SCAN_OVERRIDES

        points, span, xatol = next(iter(ENTRY_SCAN_OVERRIDES.values()))
        r = _record()
        out = assigned_leader_equilibrium(
            games[("envelope", 0.0, "par")],
            r["X_P"],
            (r["rent_eq_K_L"], r["rent_eq_phi_L"]),
            points,
            span,
            xatol,
        )
        assert out["X_L"] == pytest.approx(r["X_L"], rel=2e-3)
        assert out["lcp_trigger"] == pytest.approx(out["X_L"], rel=5e-3)
        assert out["equilibrium"] == 1.0

    @pytest.mark.slow
    def test_rejected_when_the_follower_would_preempt(self):
        """With L* raised above F at X_L the profile is not an equilibrium."""
        r = _record()
        out = assigned_leader_equilibrium(
            _InflatedGame(P, "envelope"),
            r["X_P"],
            (r["K_L"], r["phi_L"]),
            5,
            (0.25, 1.0),
            5e-2,
        )
        assert out["follower_over_leader"] < 1.0
        assert out["follower_margin"] < 0.0
        assert out["equilibrium"] == 0.0


class _InflatedGame(LeveredPreemptionGame):
    """A game whose leader values are scaled up, to exercise a failed check."""

    def leader_best_policy(self, X, start=None):
        K, phi, lead = super().leader_best_policy(X, start)
        return K, phi, 1.2 * lead


class TestMutualWaiting:
    """The value of mutual waiting with the option to stop and with debt."""

    def test_follower_response_interpolation(self, games):
        for key in (("envelope", 0.0, "par"), ("envelope", 0.4, "fair")):
            game = games[key]
            for T in (1e-4, 3.3e-3, 0.07, 2.0):
                entry = game.follower_post_switch_entry(T)
                X_F, K_F, B_F = game._follower_response(T)
                assert pytest.approx(entry.X_F, rel=1e-6) == X_F
                assert pytest.approx(entry.K_F, rel=1e-6) == K_F
                assert pytest.approx(entry.B_F, rel=1e-7) == B_F

    def test_post_switch_game_with_the_option_to_stop(self, games):
        game = games[("envelope", 0.0, "par")]
        wait = game.mutual_waiting_claim("reoptimized")
        no_stop = game.mutual_waiting_claim("no_stop")
        # The option lowers the post-switch rent-equalization trigger ...
        assert game.post_switch_trigger == pytest.approx(0.0003664, rel=3e-3)
        assert game.proxy.post_switch_trigger == pytest.approx(0.0003874, rel=3e-3)
        # ... and that game is a race: an assigned leader would wait longer.
        assert game.post_switch_assigned_trigger > 3 * game.post_switch_trigger
        assert game.post_switch_single_crossing
        _, lead, follow = game.post_switch_leader_policy(game.post_switch_trigger)
        assert lead == pytest.approx(follow, rel=1e-6)
        for multiple in (2.0, 4.0, 8.0):
            _, lead, follow = game.post_switch_leader_policy(
                multiple * game.post_switch_trigger
            )
            assert lead > 1.1 * follow
        # Error of the value without the option: a few tenths of a percent.
        X = _record()["X_P"] * np.geomspace(0.03, 10.0, 12)
        error = no_stop(X) / wait(X) - 1.0
        assert np.max(np.abs(error)) < 2.5e-3
        assert float(no_stop(_record()["X_L"])[0]) / float(
            wait(_record()["X_L"])[0]
        ) - 1.0 == pytest.approx(_record()["wait_no_stop_ratio"], abs=1e-6)

    def test_post_switch_values_join_at_the_follower_trigger(self, games):
        for key in (("envelope", 0.0, "par"), ("envelope", 0.4, "par")):
            game = games[key]
            K = 0.01
            X_F, _, _ = game._follower_response(K)
            below, above = game._post_switch_follow_value(
                np.array([X_F * (1 - 1e-7), X_F * (1 + 1e-7)]), K
            )
            assert below == pytest.approx(above, rel=1e-5)
            # The leader's value is continuous there as well.
            lead = [
                game._post_switch_leader_npv(X_F * (1 + s), K) for s in (-1e-6, 1e-6)
            ]
            assert lead[0] == pytest.approx(lead[1], rel=1e-4)

    def test_fair_debt_is_priced_at_par_for_the_post_switch_leader(self, games):
        par = games[("envelope", 0.4, "par")]
        fair = games[("envelope", 0.4, "fair")]
        zero = games[("envelope", 0.0, "par")]
        X, K = 0.002, 0.004
        # Fair pricing removes the subsidy: close to the unlevered value,
        # and below the par-financed one.
        unlevered = zero._post_switch_leader_npv(X, K)
        assert fair._post_switch_leader_npv(X, K) == pytest.approx(unlevered, rel=0.02)
        assert par._post_switch_leader_npv(X, K) > 1.02 * unlevered
        # An issue that cannot be placed has no value.
        assert fair._post_switch_leader_npv(1e-6, 1.0) == -np.inf

    def test_effect_of_the_option_on_the_trigger_in_every_cell(self):
        shift = np.array([r["X_L_no_stop"] / r["X_L"] - 1.0 for r in GRID])
        error = np.array([r["wait_no_stop_ratio"] for r in GRID])
        # Without the option in W the trigger would be about 1% higher,
        # except at lambda = 0.03, where it would be lower.
        assert np.median(shift) == pytest.approx(0.011, abs=0.004)
        assert -0.05 < shift.min() < shift.max() < 0.03
        assert np.all(np.abs(error) < 5e-3)

    def test_leader_kept_through_the_switch_would_wait(self):
        """Selection of the continuation: see `assigned_leader_equilibrium`."""
        for lam in TestBeliefs.LAMS[2:]:
            r = _record(lam)
            assert np.isinf(r["X_L_roles_kept"])
            # The profile in which the pre-switch follower is the firm that
            # leads after the switch passes the follower's check as well.
            assert r["follower_margin_if_leading_after_switch"] > 0.0

    def test_arguments(self, games):
        game = games[("envelope", 0.0, "par")]
        with pytest.raises(ValueError, match="leader must be"):
            game.mutual_waiting_claim("other")
        assert game.mutual_waiting_claim("paper") is game.proxy.mutual_waiting_claim(
            "paper"
        )
        leading = game.post_switch_leading_claim()
        wait = game.mutual_waiting_claim("reoptimized")
        X = np.array([1e-4, 3e-3, 0.05])
        # Leading after the switch is worth more, except below X_P^H.
        assert leading(X)[0] == pytest.approx(wait(X)[0], rel=0.05)
        assert np.all(leading(X)[1:] > 1.05 * wait(X)[1:])


def _recovery_rate(record):
    """Recovery over the default-free claim C_D / r of a cached record."""
    claim = record["coupon_rate"] * record["debt_proceeds"] / P.r
    return record["recovery"] / claim


class TestSpreadAtEntry:
    """C23 at the rent-equalization trigger X_P (the values of issue #178)."""

    @pytest.mark.parametrize("leverage", [0.40, 0.65])
    @pytest.mark.parametrize("debt", ["par", "fair"])
    def test_shape(self, leverage, debt):
        records = [_rent(lam, leverage, debt) for lam in GRID_LAMBDAS]
        spread = np.array([1e4 * r["spread"] for r in records])
        distance = np.array([r["distance_to_default"] for r in records])
        # Risky from the first unit: recovery (issue #179 rule) is below 8% of
        # the default-free claim in every cell, and zero under the #177 rule.
        assert np.all(spread > 20)
        assert all(_recovery_rate(r) < 0.08 for r in records)
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
                round(1e4 * _rent(lam, leverage, debt)["spread"], 1)
                for lam in (0.10, 0.20, 0.50)
            ]

        # Issue #179 rule; under the #177 rule 35.2, 28.7, 33.8 / 41.9, 33.7,
        # 36.7 / 44.3, 35.2, 37.7.
        assert spreads(0.40, "par") == pytest.approx([34.1, 28.5, 33.8], abs=0.15)
        assert spreads(0.40, "fair") == pytest.approx([40.2, 33.3, 36.7], abs=0.15)
        assert spreads(0.65, "par") == pytest.approx([42.4, 34.9, 37.7], abs=0.15)
        assert _rent(0.10, 0.40, "par")["distance_to_default"] == pytest.approx(
            5.28, abs=0.01
        )
        assert _rent(0.10, 0.40, "fair")["distance_to_default"] == pytest.approx(
            4.88, abs=0.01
        )

    def test_conventions(self):
        for lam in GRID_LAMBDAS:
            for leverage in (0.40, 0.65):
                par = _rent(lam, leverage, "par")
                fair = _rent(lam, leverage, "fair")
                assert par["coupon_rate"] == pytest.approx(0.05)
                assert par["debt_value"] < 0.45 * par["debt_proceeds"]
                assert fair["debt_value"] == pytest.approx(
                    fair["debt_proceeds"], rel=1e-9
                )
                assert fair["spread"] == pytest.approx(fair["coupon_rate"] - P.r)
                assert fair["spread"] > par["spread"]
                assert fair["distance_to_default"] < par["distance_to_default"]


class TestLeverageEffects:
    """C15 at the rent-equalization trigger X_P (the values of issue #178)."""

    LEVERAGES = (0.0, 0.20, 0.40, 0.65)

    def _path(self, debt, key):
        return np.array([_rent(leverage=lev, debt=debt)[key] for lev in self.LEVERAGES])

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
            # Lower, not higher, and by little: at most 0.3% at leverage 0.20
            # (within the precision of a solve, about 1e-4, under the #177
            # rule; recovery adds the rest) and below 1.1% at 0.40.
            assert -4e-3 < change[1] < 1.5e-3, key
            assert -0.011 < change[2] < 0.0, key
            assert -0.04 < change[3] < change[2], key
        x_p = self._path("fair", "X_P")
        # -0.3% under the #177 rule; recovery raises the fairly priced
        # leader's value at X_P and lowers the trigger further.
        assert x_p[2] / x_p[0] - 1 == pytest.approx(-0.007, abs=0.001)

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
    """C24 from the rent-equalization trigger X_P (the values of issue #178)."""

    def test_baseline(self):
        r = _rent()
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
        r = _rent()
        assert r["leader_default_before_switch"] == pytest.approx(0.0724, abs=0.001)
        assert r["leader_default_no_switch"] == 1.0
        par = _rent(leverage=0.40, debt="par")
        assert par["leader_default_before_switch"] == pytest.approx(0.085, abs=0.001)

    def test_follower_entry_is_remote_at_every_belief(self):
        times = [_rent(lam)["follower_expected_entry_time"] for lam in TestBeliefs.LAMS]
        assert min(times) == pytest.approx(97.6, abs=0.3)
        assert max(times) == pytest.approx(186.3, abs=0.5)


class TestCreditAtFirstInvestment:
    """C23, C15 and C24 at the benchmark: a leader that enters at X_L."""

    LEVERAGES = (0.0, 0.20, 0.40, 0.65)

    def _path(self, debt, key):
        return np.array([
            _record(leverage=lev, debt=debt)[key] for lev in self.LEVERAGES
        ])

    @pytest.mark.parametrize("leverage", [0.40, 0.65])
    @pytest.mark.parametrize("debt", ["par", "fair"])
    def test_spread_is_u_shaped_in_lambda(self, leverage, debt):
        """C23: not weakly increasing at X_L either."""
        records = [_record(lam, leverage, debt) for lam in GRID_LAMBDAS]
        spread = np.array([1e4 * r["spread"] for r in records])
        distance = np.array([r["distance_to_default"] for r in records])
        assert np.all(spread > 30)
        assert all(_recovery_rate(r) < 0.05 for r in records)
        low = int(np.argmin(spread))
        assert GRID_LAMBDAS[low] in (0.30, 0.40)
        assert np.all(np.diff(spread[: low + 1]) < 0)
        assert np.all(np.diff(spread[low:]) > 0)
        # The distance to default peaks at 0.10 or 0.15 and falls from there.
        assert GRID_LAMBDAS[int(np.argmax(distance))] in (0.10, 0.15)
        assert np.all(np.diff(distance[2:]) < 0)
        # Closer to the boundary, and a higher spread, than at X_P.
        at_X_P = [_at_X_P(r) for r in records]
        assert all(
            r["distance_to_default"] < p["distance_to_default"]
            for r, p in zip(records, at_X_P, strict=True)
        )
        assert all(
            r["spread"] > p["spread"] for r, p in zip(records, at_X_P, strict=True)
        )

    def test_spread_levels(self):
        def spreads(leverage, debt):
            return [
                round(1e4 * _record(lam, leverage, debt)["spread"], 1)
                for lam in (0.10, 0.30, 0.50)
            ]

        # Issue #179 rule; under the #177 rule 50.2 and 55.6 at lambda = 0.10.
        assert spreads(0.40, "par") == pytest.approx([49.4, 32.4, 34.0], abs=0.2)
        assert spreads(0.40, "fair") == pytest.approx([54.2, 36.0, 37.0], abs=0.2)
        assert spreads(0.65, "par") == pytest.approx([56.2, 37.2, 37.9], abs=0.2)
        assert spreads(0.65, "fair") == pytest.approx([61.8, 41.7, 41.4], abs=0.2)
        low = 1e4 * _record(0.05, 0.40, "par")["spread"]
        assert low == pytest.approx(95.8, abs=0.3)
        distance = _record(0.10, 0.40, "par")["distance_to_default"]
        assert distance == pytest.approx(4.515, abs=0.01)
        distance = _record(0.10, 0.40, "fair")["distance_to_default"]
        assert distance == pytest.approx(4.316, abs=0.01)

    def test_debt_conventions(self):
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

    def test_par_debt_raises_scale_triggers_and_boundary(self):
        """C15, Remark 4: the subsidy."""
        keys = ("K_L", "K_F", "X_L", "X_F", "X_D_leader")
        for key in keys:
            assert np.all(np.diff(self._path("par", key)) > 0), key
        change = {
            key: self._path("par", key)[2] / self._path("par", key)[0] - 1
            for key in keys
        }
        assert change["K_L"] == pytest.approx(0.70, abs=0.01)
        assert change["K_F"] == pytest.approx(0.70, abs=0.01)
        assert change["X_L"] == pytest.approx(0.37, abs=0.01)
        assert change["X_F"] == pytest.approx(0.37, abs=0.01)
        assert change["X_D_leader"] == pytest.approx(0.46, abs=0.01)

    def test_fair_debt_leaves_scale_and_triggers_almost_unchanged(self):
        for key in ("K_L", "K_F", "X_L", "X_F"):
            path = self._path("fair", key)
            change = path / path[0] - 1.0
            # X_L is located to about 1e-3, so the change at leverage 0.20
            # is within the precision of a solve.
            assert abs(change[1]) < 3e-3, key
            assert -0.01 < change[2] < 0.0, key
            assert -0.04 < change[3] < change[2], key
        x_l = self._path("fair", "X_L")
        assert x_l[2] / x_l[0] - 1 == pytest.approx(-0.004, abs=0.002)

    def test_boundary_and_distance_survive_fair_pricing(self):
        boundary = self._path("fair", "X_D_leader")
        assert np.all(np.diff(boundary) > 0)
        assert boundary[2] / boundary[0] - 1 == pytest.approx(0.11, abs=0.01)
        for debt in ("par", "fair"):
            assert np.all(np.diff(self._path(debt, "distance_to_default")) < 0)
            assert np.all(np.diff(self._path(debt, "follower_distance_to_default")) < 0)
        assert self._path("par", "distance_to_default")[2] == pytest.approx(
            4.515, abs=0.01
        )

    def test_leverage_moves_both_triggers_together(self):
        for debt in ("par", "fair"):
            ratio = self._path(debt, "X_L_over_X_P")
            assert np.all((ratio > 0.39) & (ratio < 0.40))

    def test_follower_hitting_times_at_baseline(self):
        """C24: the follower's trigger is remote from X_L as well."""
        r = _record()
        out = hitting_statistics(P, r["X_L"], r["X_F"])
        assert out["before_switch"] == pytest.approx(r["follower_before_switch"])
        assert r["follower_before_switch"] == pytest.approx(0.0038, abs=0.0002)
        assert r["follower_no_switch"] == pytest.approx(0.173, abs=0.002)
        assert r["follower_time_after_switch"] == pytest.approx(89.7, abs=0.3)
        assert r["follower_expected_entry_time"] == pytest.approx(107.1, abs=0.3)
        assert r["follower_expected_entry_time"] == pytest.approx(
            expected_entry_time(P, r["X_L"], r["X_F"])
        )

    def test_leader_boundary_hitting_probability(self):
        r = _record()
        assert r["leader_default_before_switch"] == pytest.approx(0.098, abs=0.001)
        assert r["leader_default_no_switch"] == 1.0
        par = _record(leverage=0.40, debt="par")
        assert par["leader_default_before_switch"] == pytest.approx(0.107, abs=0.001)
        fair = _record(leverage=0.40, debt="fair")
        assert fair["leader_default_before_switch"] == pytest.approx(0.115, abs=0.001)

    def test_follower_entry_is_remote_at_every_belief(self):
        times = [
            _record(lam)["follower_expected_entry_time"] for lam in TestBeliefs.LAMS
        ]
        assert min(times) == pytest.approx(105.4, abs=0.5)
        assert max(times) == pytest.approx(216.3, abs=0.5)
        # Later than from X_P at every belief.
        for lam in TestBeliefs.LAMS:
            assert (
                _record(lam)["follower_expected_entry_time"]
                > _rent(lam)["follower_expected_entry_time"]
            )


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
