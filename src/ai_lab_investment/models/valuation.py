"""Valuation analysis for AI infrastructure firms.

Decomposes firm value into:
1. Assets-in-place: value of existing capacity at current demand
2. Expansion option: value of the option to invest in new capacity
3. Regime switch option: additional value from potential L->H transition

Computes credit risk metrics (default probability, credit spread) and
quantifies Dario's dilemma, the cost of investing on a belief about lambda
that differs from the true rate (`belief_mismatch`, issue #180).
"""

from typing import Any

import numpy as np

from .base_model import SingleFirmModel
from .belief_mismatch import (
    DuopolyMismatch,
    SingleFirmMismatch,
    cached_dilemma_cell,
    matched_pairs,
)
from .duopoly import DEFAULT_RECOVERY_RULE, DuopolyModel, cached_equilibrium
from .parameters import ModelParameters

# Interim pins (issue #176). At the model of record: the credit exhibits
# since issue #179 (`on_policy_credit`) and Dario's dilemma since issue #180
# (`dario_dilemma`, `dario_dilemma_leveraged`, `dario_dilemma_duopoly`, exact
# values in `belief_mismatch`). Still at the pure-power approximation
# (`pure_power_*`): `two_period_dynamic_phi` and `fixed_pie_robustness`
# (#182; the latter quotes the pure-power dilemma ratio, as does the sweep in
# `robustness.py`), and the growth-option and capacity-gap decompositions
# behind Internet Appendix G (named by no sub-issue; #183 or #184). The
# `pure_power_dilemma*` methods are kept as the nested approximation, so that
# the earlier draft's dilemma numbers reproduce and their error can be
# stated; they feed no main-text number.

ON_POLICY_LEVERAGES: tuple[float, ...] = (0.0, 0.01, 0.05, 0.10, 0.15, 0.20, 0.40, 0.70)
"""Leverage grid of the on-policy credit table (issue #179)."""

CREDIT_COUPON_RATE = 0.05
"""Coupon rate on debt used throughout the credit-risk analysis."""

CREDIT_BANKRUPTCY_COST = 0.30
"""Fraction of firm value lost in default (alpha_bc) in the analysis."""


def _two_period_state_prices(
    p: ModelParameters, lam: float, dt: float
) -> tuple[float, float, float, float]:
    """State prices of the two-period training-reallocation decomposition.

    See ValuationAnalysis.two_period_dynamic_phi for the decomposition.
    Returns (w_L, w_pre, w_sw, w_ns): the weights on, respectively, the
    L-regime flow over [0, dt], the H-regime flow earned at the
    pre-switch allocation between an in-period switch and the revision
    date, the H perpetuity at the readjusted post-switch allocation, and
    the no-switch continuation at dt.
    """
    rho = p.r - p.mu_L + lam
    rho_H = p.r - p.mu_H
    w_ns = np.exp(-rho * dt)
    w_L = (1.0 - w_ns) / rho
    w_total = lam / rho * (1.0 - w_ns)
    gap = rho - rho_H
    if abs(gap) < 1e-12:
        w_sw = lam * np.exp(-rho_H * dt) * dt
    else:
        w_sw = lam * np.exp(-rho_H * dt) * (1.0 - np.exp(-gap * dt)) / gap
    return w_L, w_total - w_sw, w_sw, w_ns


class ValuationAnalysis:
    """Comprehensive valuation analysis for AI infrastructure firms.

    Brings together the single-firm, duopoly, and calibration models
    to produce firm valuations, growth option decompositions, credit
    risk metrics, and scenario analyses.
    """

    def __init__(
        self, params: ModelParameters, recovery_rule: str = DEFAULT_RECOVERY_RULE
    ):
        """Initialize the analysis.

        Args:
            params: Model parameters.
            recovery_rule: Recovery rule of the credit block (see
                `DuopolyModel.recovery_value`); "net" is the rule of issue
                #177, without the liquidator's option to shut the inference
                business down, and "gross" reproduces the credit numbers of
                the draft that preceded #177.
        """
        self.params = params
        self.recovery_rule = recovery_rule

    # ------------------------------------------------------------------
    # Growth option decomposition
    # ------------------------------------------------------------------

    def growth_option_decomposition(
        self,
        X: float,
        K_installed: float,
        regime: str = "H",
    ) -> dict[str, Any]:
        """Decompose firm value into components.

        Args:
            X: Current demand level.
            K_installed: Currently installed capacity (0 if pre-investment).
            regime: Current demand regime.

        Returns:
            Dict with:
            - total_value: Total firm value
            - assets_in_place: Value of installed capacity
            - expansion_option: Value of option to expand
            - regime_switch_value: Additional value from regime switching
        """
        model = SingleFirmModel(self.params)

        # Assets-in-place
        if K_installed > 0:
            assets = model.installed_value(X, K_installed, regime)
        else:
            assets = 0.0

        # Total option value (includes expansion option)
        option_val = model.option_value(X, regime)

        # Regime switch value: difference between L and H option values
        if regime == "L":
            F_L = model.option_value_L(X)
            # Value in L without switching (pure L parameters)
            params_no_switch = self.params.with_param(lam=1e-10)
            model_no_switch = SingleFirmModel(params_no_switch)
            try:
                F_L_no_switch = model_no_switch.option_value(X, "L")
            except (ValueError, RuntimeError):
                F_L_no_switch = 0.0
            regime_switch = F_L - F_L_no_switch
        else:
            regime_switch = 0.0

        # The option value already embeds the regime-switch component, so
        # the expansion option is the residual after both assets-in-place
        # and the regime-switch value (avoids double counting in the total).
        expansion_option = max(option_val - assets - regime_switch, 0.0)
        total = assets + expansion_option + regime_switch

        return {
            "total_value": total,
            "assets_in_place": assets,
            "expansion_option": expansion_option,
            "regime_switch_value": regime_switch,
            "assets_fraction": assets / total if total > 0 else 0.0,
            "growth_fraction": (expansion_option + regime_switch) / total
            if total > 0
            else 0.0,
        }

    # ------------------------------------------------------------------
    # Credit risk
    # ------------------------------------------------------------------

    # Fixed demand level for credit risk evaluation.
    # Using a fixed level (rather than a multiple of X_D) ensures consistent
    # distance-to-default comparisons across leverage levels.
    CREDIT_RISK_DEMAND_LEVEL = 0.10

    # Leverage at which the zero-leverage limit of a debt quantity is
    # evaluated (the spread on an infinitesimal issue).
    ZERO_LEVERAGE_LIMIT = 1e-6

    def _credit_model(self, leverage: float) -> DuopolyModel:
        return DuopolyModel(
            self.params,
            leverage=leverage,
            coupon_rate=CREDIT_COUPON_RATE,
            bankruptcy_cost=CREDIT_BANKRUPTCY_COST,
            recovery_rule=self.recovery_rule,
        )

    def _issuance_coupon(
        self,
        duo: DuopolyModel,
        X: float,
        K: float,
        phi: float,
        debt_convention: str,
    ) -> float:
        """Coupon under the chosen debt convention, for debt issued at X."""
        if debt_convention == "par":
            return duo.coupon_payment(K)
        if debt_convention == "fair":
            return duo.fair_coupon(X, phi, K)
        msg = f"Unknown debt convention: {debt_convention!r}"
        raise ValueError(msg)

    def credit_metrics(
        self,
        leverage: float,
        X: float,
        K: float,
        phi: float,
        debt_convention: str = "par",
        horizon: float = 5.0,
    ) -> dict[str, float]:
        """Credit primitives of a single firm with policy (K, phi) at X.

        Debt is issued at X. Under "par" the coupon is CREDIT_COUPON_RATE
        times the face value leverage * I(K) (the paper's convention);
        under "fair" it is the coupon at which the debt is worth
        leverage * I(K) at issuance (`DuopolyModel.fair_coupon`).

        At leverage = 0 there is no debt: X_D is the shutdown boundary
        and the default probability is the probability of reaching it;
        the recovery rate, spread and coupon-to-proceeds ratio are the
        limits as leverage goes to zero, evaluated at
        ZERO_LEVERAGE_LIMIT.

        Returns:
            Dict with "coupon", "X_D", "distance" (X / X_D), "debt_value",
            "recovery_rate" (fraction of the default-free claim c_D/r),
            "spread" (c_D / D - r, absolute), "coupon_rate" (c_D over the
            proceeds leverage * I(K)) and "default_probability".
        """
        if not 0.0 <= leverage <= 1.0:
            msg = f"Leverage must be in [0, 1], got {leverage}"
            raise ValueError(msg)
        p = self.params
        priced_lev = max(leverage, self.ZERO_LEVERAGE_LIMIT)
        priced = self._credit_model(priced_lev)
        priced_coupon = self._issuance_coupon(priced, X, K, phi, debt_convention)
        D = priced.debt_value(X, phi, K, 0.0, 0.0, coupon=priced_coupon)
        spread = max(priced_coupon / D - p.r, 0.0) if D > 0 else float("nan")

        coupon = priced_coupon if leverage > 0 else 0.0
        duo = self._credit_model(leverage)
        X_D = duo.default_boundary(phi, K, 0.0, 0.0, coupon=coupon)
        return {
            "coupon": coupon,
            "X_D": X_D,
            "distance": X / X_D if X_D > 0 else float("inf"),
            "debt_value": D if leverage > 0 else 0.0,
            "recovery_rate": priced.recovery_rate(
                phi, K, 0.0, 0.0, coupon=priced_coupon
            ),
            "spread": spread,
            "coupon_rate": priced_coupon / (priced_lev * priced.investment_cost(K)),
            "default_probability": self._first_passage_probability(
                X, X_D, "L", horizon
            ),
        }

    def credit_table(
        self,
        X: float,
        K: float,
        phi: float,
        leverages: tuple[float, ...] = (0.0, 0.01, 0.05, 0.20, 0.40, 0.70),
    ) -> list[dict[str, float]]:
        """`credit_metrics` under both debt conventions across leverage.

        One row per leverage, with keys "leverage" and, for each
        convention c in ("par", "fair"), "c_X_D", "c_recovery_rate",
        "c_spread", "c_coupon_rate" and "c_default_probability". A fair
        coupon that does not exist (proceeds above the debt capacity)
        gives nan entries.
        """
        rows = []
        for lev in leverages:
            row: dict[str, float] = {"leverage": lev}
            for convention in ("par", "fair"):
                try:
                    metrics = self.credit_metrics(lev, X, K, phi, convention)
                except ValueError:
                    metrics = {}
                for key in (
                    "X_D",
                    "recovery_rate",
                    "spread",
                    "coupon_rate",
                    "default_probability",
                ):
                    row[f"{convention}_{key}"] = metrics.get(key, float("nan"))
            rows.append(row)
        return rows

    def credit_spread(
        self,
        leverage: float,
        K: float = 1.0,
        phi: float = 0.5,
        regime: str = "L",
        risk_free_rate: float | None = None,
        X: float | None = None,
        debt_convention: str = "par",
    ) -> float:
        """Compute credit spread for a levered firm.

        Credit spread = yield on risky debt - benchmark yield.
        yield = coupon / debt_value.

        The benchmark is the model's discount rate r: all claims are
        valued by discounting at r, so a default-free perpetuity with
        coupon c_D is worth c_D / r and yields exactly r. The spread is
        therefore zero when default risk is absent and measures only the
        default-risk component.

        At leverage = 0 the returned value is the limit as leverage goes
        to zero (the spread on an infinitesimal issue). It is positive
        whenever the shutdown boundary can be reached, because the
        unlevered firm also stops operating there.

        Args:
            leverage: Debt-to-investment ratio.
            K: Capacity level.
            phi: Training fraction (default 0.5).
            regime: Demand regime (unused; debt is an L-regime claim).
            risk_free_rate: Benchmark rate (defaults to the model's r).
            X: Demand at which the debt is issued and priced (defaults
                to CREDIT_RISK_DEMAND_LEVEL).
            debt_convention: "par" (coupon rate CREDIT_COUPON_RATE on the
                face value) or "fair" (debt worth its proceeds at X).

        Returns:
            Credit spread in absolute terms (e.g., 0.02 = 200 bps).
        """
        if X is None:
            X = self.CREDIT_RISK_DEMAND_LEVEL
        metrics = self.credit_metrics(leverage, X, K, phi, debt_convention)
        spread = metrics["spread"]
        if risk_free_rate is not None:
            spread += self.params.r - risk_free_rate
        return max(spread, 0.0) if np.isfinite(spread) else 0.0

    def _first_passage_probability(
        self, X_current: float, X_D: float, regime: str, horizon: float
    ) -> float:
        """Probability that GBM started at X_current reaches X_D by horizon."""
        if X_D <= 0:
            return 0.0
        if X_current <= X_D:
            return 1.0
        if horizon <= 0:
            return 0.0

        p = self.params
        mu = p.mu_H if regime == "H" else p.mu_L
        sigma = p.sigma

        # First-passage (barrier) probability for GBM hitting X_D
        # P(min_{0<=t<=T} X_t <= X_D) = N(-d1) + (X_D/X)^{2nu/sigma^2} N(-d2)
        # where nu = mu - sigma^2/2, d1 = [ln(X/X_D) + nu*T]/(sigma*sqrt(T)),
        # d2 = [ln(X/X_D) - nu*T]/(sigma*sqrt(T))
        from scipy.stats import norm

        nu = mu - 0.5 * sigma**2
        sqrt_T = sigma * np.sqrt(horizon)
        log_ratio = np.log(X_current / X_D)

        d1 = (log_ratio + nu * horizon) / sqrt_T
        d2 = (log_ratio - nu * horizon) / sqrt_T

        prob = norm.cdf(-d1)
        if sigma > 0:
            prob += (X_D / X_current) ** (2 * nu / sigma**2) * norm.cdf(-d2)

        return float(np.clip(prob, 0.0, 1.0))

    def default_probability(
        self,
        X_current: float,
        K: float,
        leverage: float,
        phi: float = 0.5,
        regime: str = "L",
        horizon: float = 5.0,
        debt_convention: str = "par",
    ) -> float:
        """Approximate probability of default within horizon.

        Uses the first-passage probability that GBM hits the default
        boundary within the given time horizon. The default boundary
        X_D is an L-regime object (the firm defaults pre-switch), so the
        L-regime drift mu_L is the consistent choice and the default.
        The calculation abstracts from the regime switch itself: a
        switch to H before hitting X_D would effectively remove default
        risk, so the figure is an upper bound on the pre-switch hazard.

        Without debt the boundary is the shutdown boundary of the
        unlevered firm (the zero-coupon case of the same formula), so
        the probability is continuous as leverage goes to zero and is
        the probability that the firm stops operating.

        Args:
            X_current: Current demand level.
            K: Capacity.
            leverage: Debt-to-investment ratio.
            phi: Training fraction (default 0.5).
            regime: Demand regime governing the drift (default "L").
            horizon: Time horizon in years.
            debt_convention: "par" or "fair" (debt issued at X_current
                and worth its proceeds there).

        Returns:
            Probability of default [0, 1].
        """
        duo = self._credit_model(leverage)
        coupon = (
            self._issuance_coupon(duo, X_current, K, phi, debt_convention)
            if leverage > 0
            else 0.0
        )
        X_D = duo.default_boundary(phi, K, 0.0, 0.0, coupon=coupon)
        return self._first_passage_probability(X_current, X_D, regime, horizon)

    def credit_spread_curve(
        self,
        leverage_values: np.ndarray,
        regime: str = "L",
    ) -> dict[str, np.ndarray]:
        """Compute credit spreads across leverage levels.

        Both spread and default probability are evaluated at a fixed
        demand level (CREDIT_RISK_DEMAND_LEVEL), ensuring consistent
        distance-to-default comparisons across leverage levels.
        """
        n = len(leverage_values)
        spreads = np.full(n, np.nan)
        default_probs = np.full(n, np.nan)

        for i, lev in enumerate(leverage_values):
            try:
                spreads[i] = self.credit_spread(lev, regime=regime)
                default_probs[i] = self.default_probability(
                    X_current=self.CREDIT_RISK_DEMAND_LEVEL,
                    K=1.0,
                    leverage=lev,
                    regime=regime,
                )
            except (ValueError, RuntimeError):
                continue

        return {
            "leverage": leverage_values,
            "credit_spread": spreads,
            "default_probability": default_probs,
        }

    # ------------------------------------------------------------------
    # Credit at the model's own policies (issue #179)
    # ------------------------------------------------------------------

    def single_firm_policy(self) -> tuple[float, float, float]:
        """(X*, K*, phi*) of the single firm, precommitted post-switch scale.

        The model of record (`SingleFirmModel.optimal_trigger_capacity_phi`).
        With scale chosen at the switch the single firm waits at baseline,
        so this is the only pre-switch policy of the single firm at which
        debt can be issued there.
        """
        return SingleFirmModel(self.params).optimal_trigger_capacity_phi()

    def on_policy_credit(
        self,
        leverages: tuple[float, ...] = ON_POLICY_LEVERAGES,
        horizon: float = 5.0,
        conventions: tuple[str, ...] = ("par", "fair"),
        roles: tuple[str, ...] = ("single_firm", "leader", "follower"),
    ) -> list[dict[str, Any]]:
        """Credit objects at the model's own policies, across leverage.

        One row per (role, debt convention, leverage), with debt issued at
        the role's entry demand and priced with the exact claims of the
        model of record (`LeveredPreemptionGame`: coupled regime-switching
        boundary, default possible after the switch, the recovery rule of
        this analysis):

        - ``"single_firm"``: the precommitted-scale policy (X*, K*, phi*)
          of `single_firm_policy`, an installed monopolist
          (`LeveredPreemptionGame.installed_credit`).
        - ``"leader"``: the duopoly's first investment, the leader's
          (X_L, K_L, phi_L) of the cached unlevered equilibrium
          (`duopoly.cached_equilibrium`) held fixed across leverage; the
          follower best-responds at each leverage.
        - ``"follower"``: the follower's post-switch entry (X_F, K_F, all
          capacity in training) against that leader, re-optimized at each
          leverage, with the absorbing-regime claims (zero recovery after
          the switch).
        - ``"single_firm_closed_form"`` (not in the default roles): the
          single firm priced with the single-boundary closed forms of
          `DuopolyModel` (`credit_metrics`), the objects of Proposition 2.

        At zero leverage the boundary is the shutdown boundary and the
        spread, recovery rate and coupon rate are the limits as leverage
        goes to zero (evaluated at ZERO_LEVERAGE_LIMIT). The default
        probability is the first passage to the boundary within ``horizon``
        years under the drift of the regime in which the firm enters (mu_L
        for the single firm and the leader, mu_H for the follower), with
        the regime switch omitted: an upper bound on the pre-switch
        probability for the first two.

        Returns:
            Rows with keys ``role``, ``debt``, ``leverage``, ``X`` (entry
            demand), ``K``, ``phi``, ``X_D``, ``distance`` (X / X_D),
            ``recovery_rate`` (recovery over the default-free claim
            c_D / r), ``spread`` (c_D / D - r), ``coupon_rate`` (c_D over the
            proceeds) and ``default_probability``.
        """
        from .preemption_levered import LeveredPreemptionGame

        p = self.params
        rows: list[dict[str, Any]] = []
        X_s, K_s, phi_s = self.single_firm_policy()
        if any(role in roles for role in ("leader", "follower")):
            record = cached_equilibrium(lam=p.lam)
            X_L, K_L, phi_L = record["X_L"], record["K_L"], record["phi_L"]

        def row(role, debt, lev, X, K, phi, X_D, recovery_rate, spread, rate, regime):
            return {
                "role": role,
                "debt": debt,
                "leverage": lev,
                "X": X,
                "K": K,
                "phi": phi,
                "X_D": X_D,
                "distance": X / X_D,
                "recovery_rate": recovery_rate,
                "spread": spread,
                "coupon_rate": rate,
                "default_probability": self._first_passage_probability(
                    X, X_D, regime, horizon
                ),
            }

        for debt in conventions:
            for lev in leverages:
                if "single_firm_closed_form" in roles:
                    m = self.credit_metrics(lev, X_s, K_s, phi_s, debt, horizon)
                    rows.append(
                        row(
                            "single_firm_closed_form",
                            debt,
                            lev,
                            X_s,
                            K_s,
                            phi_s,
                            m["X_D"],
                            m["recovery_rate"],
                            m["spread"],
                            m["coupon_rate"],
                            "L",
                        )
                    )
                priced = max(lev, self.ZERO_LEVERAGE_LIMIT)
                game = LeveredPreemptionGame(
                    p,
                    "envelope",
                    priced,
                    CREDIT_COUPON_RATE,
                    CREDIT_BANKRUPTCY_COST,
                    debt,
                    recovery_rule=self.recovery_rule,
                )
                # At zero leverage the boundary is the shutdown boundary of
                # the unlevered claims.
                bare = (
                    game
                    if lev > 0
                    else LeveredPreemptionGame(
                        p,
                        "envelope",
                        0.0,
                        CREDIT_COUPON_RATE,
                        CREDIT_BANKRUPTCY_COST,
                        debt,
                        recovery_rule=self.recovery_rule,
                    )
                )
                if "single_firm" in roles:
                    c = game.installed_credit(K_s, phi_s, X_s)
                    rows.append(
                        row(
                            "single_firm",
                            debt,
                            lev,
                            X_s,
                            K_s,
                            phi_s,
                            bare.installed_credit(K_s, phi_s, X_s)["X_default"],
                            c["recovery"] / (c["coupon"] / p.r),
                            c["spread"],
                            c["coupon_rate"],
                            "L",
                        )
                    )
                if "leader" not in roles and "follower" not in roles:
                    continue
                sub, bare_sub = game.subgame(K_L, phi_L), bare.subgame(K_L, phi_L)
                if "leader" in roles:
                    c = sub.leader_credit(X_L)
                    rows.append(
                        row(
                            "leader",
                            debt,
                            lev,
                            X_L,
                            K_L,
                            phi_L,
                            bare_sub.leader_credit(X_L)["X_default"],
                            c["recovery"] / (c["coupon"] / p.r),
                            c["spread"],
                            c["coupon_rate"],
                            "L",
                        )
                    )
                if "follower" in roles:
                    entry = bare_sub.post_switch
                    f = game.follower_entry_credit(sub.post_switch)
                    spread = f["follower_spread"]
                    rows.append(
                        row(
                            "follower",
                            debt,
                            lev,
                            entry.X_F,
                            entry.K_F,
                            1.0,
                            bare.follower_entry_credit(entry)["X_D_follower"],
                            0.0,
                            spread,
                            CREDIT_COUPON_RATE if debt == "par" else p.r + spread,
                            "H",
                        )
                    )
        return rows

    def credit_phi_profile(
        self,
        phis: np.ndarray,
        leverage: float = 0.40,
        debt: str = "par",
        roles: tuple[str, ...] = ("single_firm", "leader"),
    ) -> dict[str, dict[str, np.ndarray]]:
        """Recovery rate, spread and boundary against the training fraction.

        Each role keeps its entry demand and capacity from `on_policy_credit`
        (the single firm's (X*, K*), the leader's (X_L, K_L)) and only phi
        varies, so the profile is a comparative static at a fixed scale and
        not a sequence of optimal policies. Exact claims, debt issued at the
        entry demand.

        Returns:
            For each role, arrays ``phi``, ``recovery_rate`` (fraction of the
            default-free claim), ``spread`` and ``X_D``, plus the scalar
            ``phi_policy`` (phi* or phi_L) under that key.
        """
        from .preemption_levered import LeveredPreemptionGame

        p = self.params
        game = LeveredPreemptionGame(
            p,
            "envelope",
            leverage,
            CREDIT_COUPON_RATE,
            CREDIT_BANKRUPTCY_COST,
            debt,
            recovery_rule=self.recovery_rule,
        )
        X_s, K_s, phi_s = self.single_firm_policy()
        record = cached_equilibrium(lam=p.lam)
        policies = {
            "single_firm": (X_s, K_s, phi_s),
            "leader": (record["X_L"], record["K_L"], record["phi_L"]),
        }
        out: dict[str, dict[str, np.ndarray]] = {}
        for role in roles:
            X, K, phi_policy = policies[role]
            rec, spread, X_D = (np.full(len(phis), np.nan) for _ in range(3))
            for i, phi in enumerate(phis):
                if role == "single_firm":
                    c = game.installed_credit(K, float(phi), X)
                else:
                    c = game.subgame(K, float(phi)).leader_credit(X)
                rec[i] = c["recovery"] / (c["coupon"] / p.r)
                spread[i] = c["spread"]
                X_D[i] = c["X_default"]
            out[role] = {
                "phi": np.asarray(phis, dtype=float),
                "recovery_rate": rec,
                "spread": spread,
                "X_D": X_D,
                "phi_policy": np.asarray(phi_policy),
            }
        return out

    # ------------------------------------------------------------------
    # Dario's dilemma in the model of record (issue #180)
    # ------------------------------------------------------------------

    def _single_firm_mismatch(
        self, lambda_true: float, version: str, X_0: float | None
    ) -> SingleFirmMismatch:
        cache = self.__dict__.setdefault("_mismatch", {})
        key = (float(lambda_true), version, X_0)
        if key not in cache:
            cache[key] = SingleFirmMismatch(
                self.params,
                lambda_true,
                version,
                X_0=X_0,
                recovery_rule=self.recovery_rule,
            )
        return cache[key]

    def dario_dilemma(
        self,
        lambda_true: float,
        lambda_invest: float,
        version: str = "precommitted",
        X_0: float | None = None,
    ) -> dict[str, Any]:
        """Cost of investing on the belief ``lambda_invest``, single firm.

        The mistaken firm follows the policy that is optimal under its
        belief in the exact problem (trigger, capacity, training fraction,
        or waiting for the switch) and that policy is valued exactly under
        ``lambda_true``, at the reference demand ``X_0`` (default: half the
        precommitted-scale trigger at the true rate). See
        `belief_mismatch.SingleFirmMismatch.loss` for the keys, which
        include the timing, capacity and allocation components.

        Args:
            version: ``"precommitted"`` (post-switch scale precommitted, the
                problem of Proposition 1(iii) and the main-text version) or
                ``"unrestricted"`` (scale chosen at the switch, in which a
                firm may wait for the switch).
        """
        return self._single_firm_mismatch(lambda_true, version, X_0).loss(lambda_invest)

    def dario_dilemma_matched(
        self,
        lambda_true: float = 0.10,
        additive: float = 0.08,
        version: str = "precommitted",
        X_0: float | None = None,
    ) -> dict[str, dict[str, float]]:
        """Losses at the matched pairs of `belief_mismatch.matched_pairs`.

        One entry per error metric (additive, the two proportional pairs,
        horizon), each with the two beliefs, their losses and the ratio of
        the pessimistic to the optimistic loss.
        """
        model = self._single_firm_mismatch(lambda_true, version, X_0)
        return {
            name: model.matched(low, high)
            for name, (low, high) in matched_pairs(lambda_true, additive).items()
        }

    def dario_dilemma_leveraged(
        self,
        lambda_true: float,
        lambda_invest: float,
        leverage: float = 0.40,
        version: str = "precommitted",
        debt: str = "fair",
        X_0: float | None = None,
    ) -> dict[str, Any]:
        """The single firm's dilemma on the levered claims.

        The policies are the unlevered ones at each belief; the claims are
        the exact claims of the credit block (option to stop operating,
        coupled boundary, debt under the recovery rule), and the value is
        the shareholders' entry value, which under fairly priced debt is
        firm value less the outlay. Also returns, for each policy, the
        distance to the boundary at entry and the five-year first-passage
        probability (`belief_mismatch.SingleFirmMismatch.levered`). At
        zero leverage the boundary is the shutdown boundary, so the loss
        differs slightly from `dario_dilemma`, whose claims carry no option
        to stop.
        """
        model = self._single_firm_mismatch(lambda_true, version, X_0)
        return model.levered(lambda_invest, leverage, debt)

    def dario_dilemma_surface(
        self,
        lambda_true_range: np.ndarray,
        lambda_invest_range: np.ndarray,
        version: str = "precommitted",
    ) -> dict[str, np.ndarray]:
        """Value loss on a grid of (true, invest) arrival rates."""
        value_loss = np.full((len(lambda_true_range), len(lambda_invest_range)), np.nan)
        for i, lt in enumerate(lambda_true_range):
            for j, li in enumerate(lambda_invest_range):
                value_loss[i, j] = self.dario_dilemma(lt, li, version)["value_loss_pct"]
        return {
            "lambda_true": lambda_true_range,
            "lambda_invest": lambda_invest_range,
            "value_loss_pct": value_loss,
        }

    def dilemma_third_derivative(
        self,
        lambda_true: float,
        step: float,
        version: str = "precommitted",
        X_0: float | None = None,
    ) -> float:
        """Third derivative in the belief of the exact value of the belief's
        policy, at ``lambda_true`` and a fixed reference demand, in units of
        the optimal value. Positive when small equal additive errors cost
        more on the pessimistic side."""
        model = self._single_firm_mismatch(lambda_true, version, X_0)
        return model.third_derivative(step)

    def dario_dilemma_duopoly(
        self,
        lambda_true: float,
        lambda_invest: float,
        role: str = "leader",
        leverage: float = 0.0,
        debt: str = "fair",
        solve: bool = False,
    ) -> dict[str, Any]:
        """The dilemma inside the entry equilibrium of the model of record.

        The benchmark is the equilibrium in which one firm leads at X_L and
        the other follows; the mistaken firm is the leader or the follower
        (``role``) and its rival, at the true rate, best-responds
        (`belief_mismatch.DuopolyMismatch`). Read from the cache
        `duopoly_dilemma.json` at the baseline calibration; with ``solve``
        the cell is computed (a few minutes).
        """
        if not solve:
            if self.params != ModelParameters().with_param(lam=self.params.lam):
                msg = "The cached duopoly dilemma is at the baseline calibration"
                raise KeyError(msg)
            if abs(lambda_true - 0.10) > 1e-12:
                msg = "The cached duopoly dilemma has lambda_true = 0.10"
                raise KeyError(msg)
            return cached_dilemma_cell(lambda_invest, role, leverage, debt)
        model = DuopolyMismatch(
            self.params, lambda_true, recovery_rule=self.recovery_rule
        )
        return model.cell(lambda_invest, role, leverage, debt)

    # ------------------------------------------------------------------
    # Dario's dilemma under the pure-power approximation (earlier draft)
    # ------------------------------------------------------------------

    def pure_power_dilemma(
        self,
        lambda_true: float,
        lambda_invest: float,
    ) -> dict[str, Any]:
        """Belief-mismatch cost under the pure-power approximation.

        The nested approximation of the earlier draft, kept so that its
        numbers reproduce and their error against `dario_dilemma` can be
        stated. Both policies are the pure-power ones and both are priced
        with the timing factor (X_0 / X*)^beta_H, which makes the
        percentage loss independent of X_0.

        Uses the phi-aware model where lambda enters through A_eff, so
        the trigger X* and allocation phi* depend on lambda. The pure-power
        capacity does *not*: it is independent of both lambda and phi, so
        in this approximation belief mismatches distort timing and
        allocation only, never scale (and hence never the coupon, which is
        proportional to I(K*)). In the exact problem capacity responds to
        the belief.

        If a firm's true lambda (private belief) differs from the lambda
        it uses for investment decisions, what is the cost?

        - Conservative (lambda_invest < lambda_true): invests too late
          and under-allocates to training, forgoing H-regime upside
        - Aggressive (lambda_invest > lambda_true): invests too early
          and over-allocates to training, sacrificing L-regime revenue
          and raising default risk in bad states

        Args:
            lambda_true: True arrival rate (private belief).
            lambda_invest: Arrival rate used for investment decisions.

        Returns:
            Dict with value under each scenario.
        """
        # Optimal investment under true lambda
        p_true = self.params.with_param(lam=lambda_true)
        model_true = SingleFirmModel(p_true)
        try:
            X_true, K_true, phi_true = model_true.pure_power_trigger_capacity_phi()
            V_optimal = model_true.installed_value_with_phi(
                X_true, phi_true, K_true, "L"
            )
            I_optimal = model_true.investment_cost(K_true)
            npv_optimal = V_optimal - I_optimal
        except (ValueError, RuntimeError):
            return {"error": "No solution at true lambda"}

        # Investment under mismatched lambda
        p_invest = self.params.with_param(lam=lambda_invest)
        model_invest = SingleFirmModel(p_invest)
        try:
            X_invest, K_invest, phi_invest = (
                model_invest.pure_power_trigger_capacity_phi()
            )
            # Evaluate this investment under the TRUE demand process
            # (true A_eff) but with the mismatched (K, phi) policy.
            V_mismatch = model_true.installed_value_with_phi(
                X_invest, phi_invest, K_invest, "L"
            )
            I_mismatch = model_true.investment_cost(K_invest)
            npv_mismatch = V_mismatch - I_mismatch
        except (ValueError, RuntimeError):
            return {"error": "No solution at invest lambda"}

        # Include timing discount: the option value at a common reference
        # demand X_0 is NPV(X*) * (X_0 / X*)^beta_H. This accounts for
        # the different waiting times (higher trigger = longer wait).
        beta = p_true.beta_H
        # Use a reference X_0 below both triggers
        X_0 = min(X_true, X_invest) * 0.5
        if X_0 <= 0:
            X_0 = 1e-6

        ev_optimal = npv_optimal * (X_0 / X_true) ** beta if npv_optimal > 0 else 0
        ev_mismatch = npv_mismatch * (X_0 / X_invest) ** beta if npv_mismatch > 0 else 0
        value_loss = ev_optimal - ev_mismatch
        value_loss_pct = value_loss / abs(ev_optimal) if ev_optimal != 0 else 0

        return {
            "lambda_true": lambda_true,
            "lambda_invest": lambda_invest,
            "X_optimal": X_true,
            "K_optimal": K_true,
            "phi_optimal": phi_true,
            "npv_optimal": npv_optimal,
            "X_mismatch": X_invest,
            "K_mismatch": K_invest,
            "phi_mismatch": phi_invest,
            "npv_mismatch": npv_mismatch,
            "ev_optimal": ev_optimal,
            "ev_mismatch": ev_mismatch,
            "value_loss": value_loss,
            "value_loss_pct": value_loss_pct,
            "is_conservative": lambda_invest < lambda_true,
        }

    def pure_power_dilemma_policy_value(
        self,
        lambda_true: float,
        lambda_invest: float,
        X_0: float,
    ) -> float:
        """W(lambda_invest) = NPV(lambda_true, lambda_invest) at a fixed X_0.

        The unlevered value, at demand X_0, of following the policy optimal
        under lambda_invest when the true arrival rate is lambda_true:
        NPV(X*) (X_0 / X*)^beta_H with the reduced-form timing factor. X_0
        must lie below the policy's trigger. Unlike `pure_power_dilemma`, which
        picks X_0 per pair (harmless for percentage losses because the
        common power cancels), this evaluator holds X_0 fixed so that W
        can be differentiated in lambda_invest.
        """
        p_true = self.params.with_param(lam=lambda_true)
        model_true = SingleFirmModel(p_true)
        model_invest = SingleFirmModel(self.params.with_param(lam=lambda_invest))
        X_inv, K_inv, phi_inv = model_invest.pure_power_trigger_capacity_phi()
        if X_inv <= X_0:
            msg = f"X_0 = {X_0:.4g} must lie below the policy trigger {X_inv:.4g}"
            raise ValueError(msg)
        npv = model_true.installed_value_with_phi(
            X_inv, phi_inv, K_inv, "L"
        ) - model_true.investment_cost(K_inv)
        return float(npv * (X_0 / X_inv) ** p_true.beta_H)

    def pure_power_dilemma_third_derivative(
        self,
        lambda_true: float,
        step: float,
        X_0: float | None = None,
    ) -> float:
        """Central finite-difference W'''(lambda_true) at a fixed X_0.

        Uses the five-point stencil (W(l+2h) - 2W(l+h) + 2W(l-h) - W(l-2h))
        / (2h^3). Callers should compare two step sizes; the sign is what
        the appendix's asymmetry argument uses. X_0 defaults to half the
        true-belief trigger, which lies below every trigger on the
        stencil for the calibrations considered.
        """
        if X_0 is None:
            X_true, _, _ = SingleFirmModel(
                self.params.with_param(lam=lambda_true)
            ).pure_power_trigger_capacity_phi()
            X_0 = 0.5 * X_true
        W = [
            self.pure_power_dilemma_policy_value(
                lambda_true, lambda_true + k * step, X_0
            )
            for k in (-2, -1, 1, 2)
        ]
        return float((W[3] - 2.0 * W[2] + 2.0 * W[1] - W[0]) / (2.0 * step**3))

    def pure_power_dilemma_leveraged(
        self,
        lambda_true: float,
        lambda_invest: float,
        leverage: float = 0.40,
    ) -> dict[str, Any]:
        """Belief-mismatch cost with leverage, pure-power approximation.

        Nested approximation of the earlier draft (see `pure_power_dilemma`);
        the model of record is `dario_dilemma_leveraged`.

        Uses total firm value (E + D) from the Leland structural model,
        so deadweight bankruptcy costs (b * V(X_D)) are captured. In the
        total-claim metric the shareholders' default option is worth
        *more* to the overinvesting firm (it enters closer to its default
        boundary), so the levered percentage loss from overinvestment is
        slightly *smaller* than the unlevered one at baseline (Internet
        Appendix A); what leverage raises is default risk, not the
        expected-value loss.

        Important: both the benchmark and the mismatched operating
        policies (X*, K*, phi*) come from the *unleveraged*
        SingleFirmModel at the respective lambda; the levered claims
        E + D - leverage * I are then valued under those policies. That
        is the intended experiment, not an oversight: leverage is
        exogenous in this model, so the firm sizes and times its
        investment on NPV grounds and debt is layered on top of the
        resulting policy.

        Consequence for the appendix argument: unlike the unleveraged
        pure_power_dilemma(), the objective returned here is NOT maximized at
        lambda_invest == lambda_true by construction, because the policy
        is not re-optimized against the levered objective. Numerically
        the gap is negligible -- at baseline with leverage 0.40 the
        levered objective peaks at lambda_invest ~ 0.101 and the value
        shortfall at lambda_true is ~1.3e-5 in relative terms -- so the
        second-order expansion in Internet Appendix A is stated exactly
        for the unleveraged case and used as an approximation here.
        """
        # Optimal policy under true lambda
        p_true = self.params.with_param(lam=lambda_true)
        model_true = SingleFirmModel(p_true)
        duo_true = DuopolyModel(
            p_true,
            leverage=leverage,
            coupon_rate=CREDIT_COUPON_RATE,
            bankruptcy_cost=CREDIT_BANKRUPTCY_COST,
            recovery_rule=self.recovery_rule,
        )
        try:
            X_true, K_true, phi_true = model_true.pure_power_trigger_capacity_phi()
            eq_opt = duo_true.equity_value(X_true, phi_true, K_true, 0.0, 0.0, leverage)
            debt_opt = duo_true.debt_value(X_true, phi_true, K_true, 0.0, 0.0, leverage)
            I_opt = duo_true.investment_cost(K_true)
            # Total NPV = E + D - lev*I = (V - (1-lev)*I - BC) + D - lev*I
            npv_optimal = eq_opt + debt_opt - leverage * I_opt
        except (ValueError, RuntimeError):
            return {"error": "No solution at true lambda"}

        # Investment under mismatched lambda
        p_invest = self.params.with_param(lam=lambda_invest)
        model_invest = SingleFirmModel(p_invest)
        try:
            X_invest, K_invest, phi_invest = (
                model_invest.pure_power_trigger_capacity_phi()
            )
            eq_mis = duo_true.equity_value(
                X_invest, phi_invest, K_invest, 0.0, 0.0, leverage
            )
            debt_mis = duo_true.debt_value(
                X_invest, phi_invest, K_invest, 0.0, 0.0, leverage
            )
            I_mis = duo_true.investment_cost(K_invest)
            npv_mismatch = eq_mis + debt_mis - leverage * I_mis
        except (ValueError, RuntimeError):
            return {"error": "No solution at invest lambda"}

        # Timing discount
        beta = p_true.beta_H
        X_0 = min(X_true, X_invest) * 0.5
        if X_0 <= 0:
            X_0 = 1e-6

        ev_optimal = npv_optimal * (X_0 / X_true) ** beta if npv_optimal > 0 else 0
        ev_mismatch = npv_mismatch * (X_0 / X_invest) ** beta if npv_mismatch > 0 else 0
        value_loss = ev_optimal - ev_mismatch
        value_loss_pct = value_loss / abs(ev_optimal) if ev_optimal != 0 else 0

        # Conditional default probabilities under true dynamics
        # Use the full first-passage formula (consistent with default_probability())
        va_true = ValuationAnalysis(p_true, self.recovery_rule)
        dp_optimal = va_true.default_probability(
            X_current=X_true,
            K=K_true,
            leverage=leverage,
            phi=phi_true,
            regime="L",
            horizon=5.0,
        )
        dp_mismatch = va_true.default_probability(
            X_current=X_invest,
            K=K_invest,
            leverage=leverage,
            phi=phi_invest,
            regime="L",
            horizon=5.0,
        )

        return {
            "lambda_true": lambda_true,
            "lambda_invest": lambda_invest,
            "leverage": leverage,
            "ev_optimal": ev_optimal,
            "ev_mismatch": ev_mismatch,
            "value_loss": value_loss,
            "value_loss_pct": value_loss_pct,
            "default_prob_optimal": dp_optimal,
            "default_prob_mismatch": dp_mismatch,
            "is_conservative": lambda_invest < lambda_true,
        }

    def pure_power_dilemma_surface(
        self,
        lambda_true_range: np.ndarray,
        lambda_invest_range: np.ndarray,
    ) -> dict[str, np.ndarray]:
        """`pure_power_dilemma` on a grid of (true, invest) lambda pairs."""
        n_t = len(lambda_true_range)
        n_i = len(lambda_invest_range)
        value_loss = np.full((n_t, n_i), np.nan)

        for i, lt in enumerate(lambda_true_range):
            for j, li in enumerate(lambda_invest_range):
                result = self.pure_power_dilemma(lt, li)
                if "value_loss_pct" in result:
                    value_loss[i, j] = result["value_loss_pct"]

        return {
            "lambda_true": lambda_true_range,
            "lambda_invest": lambda_invest_range,
            "value_loss_pct": value_loss,
        }

    # ------------------------------------------------------------------
    # Equity valuation vs lambda
    # ------------------------------------------------------------------

    def equity_value_vs_lambda(
        self,
        lambda_values: np.ndarray,
        X: float = 1.0,
        regime: str = "H",
    ) -> dict[str, np.ndarray]:
        """Compute equity value across lambda values.

        Shows sensitivity of valuation to AI timeline beliefs.
        """
        n = len(lambda_values)
        option_values = np.full(n, np.nan)
        triggers = np.full(n, np.nan)
        capacities = np.full(n, np.nan)

        for i, lam in enumerate(lambda_values):
            try:
                p = self.params.with_param(lam=lam)
                model = SingleFirmModel(p)
                option_values[i] = model.option_value(X, regime)
                X_star, K_star = model.optimal_trigger_and_capacity(regime)
                triggers[i] = X_star
                capacities[i] = K_star
            except (ValueError, RuntimeError):
                continue

        return {
            "lambda_values": lambda_values,
            "option_values": option_values,
            "triggers": triggers,
            "capacities": capacities,
        }

    # ------------------------------------------------------------------
    # Phi-aware valuation
    # ------------------------------------------------------------------

    def growth_option_decomposition_with_phi(
        self,
        X: float,
        K_installed: float = 0.0,
        phi: float = 0.5,
    ) -> dict[str, Any]:
        """Decompose firm value using the phi-aware model.

        Uses the combined L+H revenue structure where phi determines
        the split between inference revenue and training value.

        Args:
            X: Current demand level.
            K_installed: Currently installed capacity (0 if pre-investment).
            phi: Training fraction.

        Returns:
            Dict with value components.
        """
        model = SingleFirmModel(self.params)

        # Assets-in-place with phi
        if K_installed > 0:
            assets = model.installed_value_with_phi(X, phi, K_installed, "L")
        else:
            assets = 0.0

        # Option value with phi optimization
        option_val = model.pure_power_option_value(X)

        # Decompose: option includes optimal (K*, phi*)
        X_star, K_star, phi_star = model.pure_power_trigger_capacity_phi()

        expansion_option = option_val - assets if option_val > assets else 0.0
        total = assets + expansion_option

        return {
            "total_value": total,
            "assets_in_place": assets,
            "expansion_option": expansion_option,
            "assets_fraction": assets / total if total > 0 else 0.0,
            "growth_fraction": expansion_option / total if total > 0 else 0.0,
            "phi_installed": phi,
            "phi_optimal": phi_star,
            "K_optimal": K_star,
            "X_trigger": X_star,
        }

    def capacity_gap_decomposition(
        self,
        K_fracs: np.ndarray,
        demand_multiple: float = 1.5,
    ) -> dict[str, Any]:
        """Capacity-gap decomposition across installed-capacity levels.

        For each installed capacity K = frac * K*, computes assets-in-place
        (gross installed value at the optimal training fraction phi*) and
        the capacity gap value, defined as the shortfall of assets-in-place
        relative to the *net* value of the optimally sized greenfield
        project, NPV(K*, phi*) = V(X, phi*, K*) - I(K*), floored at zero.
        Because the benchmark nets out the full investment cost I(K*) while
        assets-in-place are gross of sunk costs, the gap reaches zero
        before K reaches K*. This is the comparative-statics measure of
        distance to optimal scale reported in the paper, not the NPV of
        incremental expansion from the installed base. Because the two
        components are measured against different benchmarks, their sum
        is a normalization device rather than firm value, and
        'gap_fraction' is a unit-free index in [0, 100], not a share of
        firm value.

        Args:
            K_fracs: Installed capacity as fractions of optimal K*.
            demand_multiple: Demand evaluation point as a multiple of the
                optimal trigger X*.

        Returns:
            Dict with 'K_fracs', 'assets_in_place', 'capacity_gap',
            'gap_fraction' (percent), and scalars 'X_eval', 'K_star',
            'phi_star', 'npv_optimal'.
        """
        model = SingleFirmModel(self.params)
        X_star, K_star, phi_star = model.pure_power_trigger_capacity_phi()
        X_eval = demand_multiple * X_star

        npv_optimal = model.installed_value_with_phi(
            X_eval, phi_star, K_star, "L"
        ) - model.investment_cost(K_star)

        assets = np.full_like(K_fracs, np.nan, dtype=float)
        gap = np.full_like(K_fracs, np.nan, dtype=float)
        for i, frac in enumerate(K_fracs):
            assets[i] = model.installed_value_with_phi(
                X_eval, phi_star, frac * K_star, "L"
            )
            gap[i] = max(npv_optimal - assets[i], 0.0)

        total = assets + gap
        gap_fraction = np.where(total > 0, gap / total * 100.0, 0.0)

        return {
            "K_fracs": K_fracs,
            "assets_in_place": assets,
            "capacity_gap": gap,
            "gap_fraction": gap_fraction,
            "X_eval": X_eval,
            "K_star": K_star,
            "phi_star": phi_star,
            "npv_optimal": npv_optimal,
        }

    def equity_value_vs_lambda_with_phi(
        self,
        lambda_values: np.ndarray,
        X: float = 1.0,
    ) -> dict[str, np.ndarray]:
        """Equity value and optimal phi across lambda values.

        Shows how both valuation and training allocation respond to
        different beliefs about AI timelines.
        """
        n = len(lambda_values)
        option_values = np.full(n, np.nan)
        triggers = np.full(n, np.nan)
        capacities = np.full(n, np.nan)
        phis = np.full(n, np.nan)

        for i, lam in enumerate(lambda_values):
            try:
                p = self.params.with_param(lam=lam)
                model = SingleFirmModel(p)
                option_values[i] = model.pure_power_option_value(X)
                X_star, K_star, phi_star = model.pure_power_trigger_capacity_phi()
                triggers[i] = X_star
                capacities[i] = K_star
                phis[i] = phi_star
            except (ValueError, RuntimeError):
                continue

        return {
            "lambda_values": lambda_values,
            "option_values": option_values,
            "triggers": triggers,
            "capacities": capacities,
            "phis": phis,
        }

    # ------------------------------------------------------------------
    # Non-equilibrium duopoly comparison of the earlier draft (OF-6)
    # ------------------------------------------------------------------

    def pure_power_dilemma_duopoly(
        self,
        lambda_true: float,
        lambda_invest: float,
        leverage: float = 0.0,
    ) -> dict[str, Any]:
        """Non-equilibrium duopoly comparison of the earlier draft.

        Not the model of record (`dario_dilemma_duopoly` computes the
        mismatch inside the entry equilibrium). Kept as the labelled
        comparison of Internet Appendix E: pure-power policies, a rival
        that does not best-respond, and a benchmark of symmetric
        simultaneous entry that is not an equilibrium of the game.

        A well-calibrated rival follows its *single-firm* optimal policy
        (trigger, capacity, training fraction) under lambda_true; it does
        not re-optimize against the focal firm, so this is a tractable
        benchmark rather than the full preemption equilibrium. The focal
        firm plays the optimal single-firm strategy under lambda_invest,
        and the firm with the lower trigger leads. This captures the
        strategic penalty of wrong beliefs: a conservative firm cedes the
        leader position and the monopoly-phase rents.

        Returns dict with value losses for single-firm and duopoly
        benchmarks.
        """

        # --- rational rival's optimal policy under true lambda ---
        p_true = self.params.with_param(lam=lambda_true)
        model_true = SingleFirmModel(p_true)
        duo_true = DuopolyModel(
            p_true,
            leverage=leverage,
            coupon_rate=CREDIT_COUPON_RATE,
            bankruptcy_cost=CREDIT_BANKRUPTCY_COST,
            recovery_rule=self.recovery_rule,
        )

        try:
            X_true, K_true, phi_true = model_true.pure_power_trigger_capacity_phi()
        except (ValueError, RuntimeError):
            return {"error": "No solution at true lambda"}

        # --- focal firm's policy under mistaken belief ---
        p_invest = self.params.with_param(lam=lambda_invest)
        model_invest = SingleFirmModel(p_invest)
        try:
            X_inv, K_inv, phi_inv = model_invest.pure_power_trigger_capacity_phi()
        except (ValueError, RuntimeError):
            return {"error": "No solution at invest lambda"}

        # --- single-firm benchmark (reuse existing method) ---
        sf = self.pure_power_dilemma(lambda_true, lambda_invest)

        # --- duopoly evaluation ---
        # Determine who leads. The firm with the lower trigger enters first.
        beta = p_true.beta_H

        if X_inv <= X_true:
            # Focal firm leads (invests first), rival follows
            # Leader value: monopoly until rival enters, then duopoly
            V_mono = duo_true.monopolist_value_L(X_inv, phi_inv, K_inv)
            if X_true > X_inv:
                # Rival enters at X_true; PV of revenue drop
                V_mono_XF = duo_true.monopolist_value_L(X_true, phi_inv, K_inv)
                V_duo_XF = duo_true.installed_value_L(
                    X_true, phi_inv, K_inv, phi_true, K_true
                )
                drop = V_mono_XF - V_duo_XF
                entry_factor = (X_inv / X_true) ** beta
                npv_focal = V_mono - drop * entry_factor
            else:
                # Simultaneous entry: immediate duopoly
                npv_focal = duo_true.installed_value_L(
                    X_inv, phi_inv, K_inv, phi_true, K_true
                )
            npv_focal -= duo_true.investment_cost(K_inv)
        else:
            # Rival leads, focal firm follows
            # Focal firm enters at X_inv into duopoly directly
            V_duo = duo_true.installed_value_L(X_inv, phi_inv, K_inv, phi_true, K_true)
            npv_focal = V_duo - duo_true.investment_cost(K_inv)

        # Optimal duopoly case: focal firm also plays correctly
        # Symmetric: both invest at the same trigger, immediate duopoly
        V_opt_duo = duo_true.installed_value_L(
            X_true, phi_true, K_true, phi_true, K_true
        )
        npv_optimal = V_opt_duo - duo_true.investment_cost(K_true)

        # Timing discount to common X_0
        X_0 = min(X_true, X_inv) * 0.5
        if X_0 <= 0:
            X_0 = 1e-6

        ev_opt = npv_optimal * (X_0 / X_true) ** beta if npv_optimal > 0 else 0
        ev_focal = npv_focal * (X_0 / X_inv) ** beta if npv_focal > 0 else 0
        loss_duo = ev_opt - ev_focal
        loss_duo_pct = loss_duo / abs(ev_opt) if ev_opt != 0 else 0

        return {
            "lambda_true": lambda_true,
            "lambda_invest": lambda_invest,
            "value_loss_pct_single": sf.get("value_loss_pct", np.nan),
            "value_loss_pct_duopoly": loss_duo_pct,
            "ev_optimal_duopoly": ev_opt,
            "ev_mismatch_duopoly": ev_focal,
            "focal_leads": bool(X_inv <= X_true),
            "X_focal": X_inv,
            "X_rival": X_true,
            "phi_focal": phi_inv,
            "phi_rival": phi_true,
        }

    # ------------------------------------------------------------------
    # Two-period dynamic phi illustration (OF-3)
    # ------------------------------------------------------------------

    def two_period_dynamic_phi(
        self,
        lambda_val: float | None = None,
        dt: float = 1.0,
        adjustment_cost: float = 0.0,
    ) -> dict[str, Any]:
        """Two-period illustration of dynamic training reallocation.

        The firm commits to phi_1 at investment and may revise the
        allocation once, at the period boundary dt, conditioning on
        whether the regime switch has occurred: to phi_H if it has, to
        phi_L2 if it has not. After the boundary the allocation is fixed
        forever, so each branch continues with the corresponding
        perpetuity. Capacity is held at the static optimum K_s, which
        isolates the allocation margin.

        Value decomposition (per unit of X_0, capacity K_s, with
        rho = r - mu_L + lam the L-regime discount rate inclusive of the
        switch hazard and rho_H = r - mu_H, A_H = 1/rho_H):

            V = w_L * [(1-phi_1) K]^alpha                       (i)
              + w_pre * A_H * [phi_1 K]^alpha                   (ii)
              + w_sw  * (A_H * [phi_H K]^alpha - kappa (phi_H - phi_1)^2)
              + w_ns  * (A_eff(phi_L2, K)      - kappa (phi_L2 - phi_1)^2)

            w_L   = (1 - e^{-rho dt}) / rho
                    survival-adjusted L-regime flow over [0, dt];
            w_sw  = int_0^dt lam e^{-rho t} e^{-rho_H (dt-t)} dt
                    state price of one unit of X_dt in the switched
                    state, i.e. the weight on the post-boundary
                    (readjusted) H allocation;
            w_tot = (lam / rho) (1 - e^{-rho dt})
                    total state price of the switch arriving in [0, dt];
            w_pre = w_tot - w_sw
                    residual weight on the *pre-switch* allocation: the
                    H flows earned between the switch and the boundary,
                    before the firm can reallocate;
            w_ns  = e^{-rho dt}
                    no-switch continuation at dt.

        The H prize therefore enters exactly once, split between the
        pre-boundary allocation (w_pre) and the post-boundary one
        (w_sw). The decomposition is exact rather than approximate: at
        phi_1 = phi_H = phi_L2 = phi it collapses to the perpetual
        A_eff(phi, K) of eq-a-eff, because w_L + w_ns / rho = 1 / rho on
        the inference term and w_pre + w_sw + w_ns * lam / rho = lam / rho
        on the H term. That identity is the test of the decomposition
        (test_two_period_decomposition_collapses_to_a_eff) and it makes
        the static benchmark behind the reported value gain literally the
        static model's revenue coefficient.

        Adjustment costs are charged inside the branch in which the
        reallocation happens and carry that branch's state price, so
        kappa is denominated in the same per-unit-of-X units as the
        revenue coefficients.

        Args:
            lambda_val: Arrival rate (defaults to params.lam).
            dt: Length of the commitment period in years.
            adjustment_cost: Quadratic reallocation cost kappa.

        Returns:
            Dict comparing static and dynamic allocations.
        """
        from scipy import optimize as sp_opt

        p = self.params
        lam = lambda_val if lambda_val is not None else p.lam

        # Probability of switch in period 1 (physical, reported only)
        p_switch = 1.0 - np.exp(-lam * dt)

        # Static benchmark
        p_lam = p.with_param(lam=lam)
        model_static = SingleFirmModel(p_lam)
        _, K_s, phi_s = model_static.pure_power_trigger_capacity_phi()

        kappa = adjustment_cost

        w_L, w_pre, w_sw, w_ns = _two_period_state_prices(p, lam, dt)

        def _period_value(phi_1: float, phi_H: float, phi_L2: float) -> float:
            """Expected PV of two-period revenue (per unit X, at K_s)."""
            K = K_s

            # (i) L-regime inference flow at phi_1 over [0, dt]
            value = w_L * ((1.0 - phi_1) * K) ** p.alpha

            # (ii) H flows between an in-period switch and the boundary,
            # still at the pre-switch allocation phi_1
            value += w_pre * p.A_H * (phi_1 * K) ** p.alpha

            # (iii) switched state at dt: H perpetuity at the readjusted
            # allocation, net of the reallocation cost
            value += w_sw * (
                p.A_H * (phi_H * K) ** p.alpha - kappa * (phi_H - phi_1) ** 2
            )

            # (iv) no-switch state at dt: L-regime perpetuity (eq-a-eff)
            # at the readjusted allocation, net of the reallocation cost
            value += w_ns * (
                model_static._effective_revenue_coeff_single(phi_L2, K)
                - kappa * (phi_L2 - phi_1) ** 2
            )

            return value

        def _neg_value(params_vec: np.ndarray) -> float:
            phi_1, phi_H, phi_L2 = params_vec
            if (
                phi_1 <= 0.01
                or phi_1 >= 0.99
                or phi_H <= 0.01
                or phi_H >= 0.99
                or phi_L2 <= 0.01
                or phi_L2 >= 0.99
            ):
                return 1e20
            return -_period_value(phi_1, phi_H, phi_L2)

        # Optimize
        best_val = 1e20
        best_params = None
        for p1 in [0.05, 0.3, 0.5, 0.7]:
            for pH in [0.5, 0.7, 0.9]:
                for pL in [0.2, 0.4, 0.6]:
                    x0 = np.array([p1, pH, pL])
                    try:
                        result = sp_opt.minimize(
                            _neg_value,
                            x0,
                            method="Nelder-Mead",
                            options={"maxiter": 2000, "xatol": 1e-8},
                        )
                        if result.fun < best_val:
                            best_val = result.fun
                            best_params = result.x
                    except (ValueError, RuntimeError):
                        continue

        if best_params is None:
            return {"error": "Dynamic phi optimization failed"}

        phi_1_opt = np.clip(best_params[0], 0.01, 0.99)
        phi_H_opt = np.clip(best_params[1], 0.01, 0.99)
        phi_L2_opt = np.clip(best_params[2], 0.01, 0.99)

        # The static benchmark is the collapsed decomposition, i.e.
        # A_eff(phi_s, K_s) exactly (see the docstring identity).
        val_dynamic = _period_value(phi_1_opt, phi_H_opt, phi_L2_opt)
        val_static = _period_value(phi_s, phi_s, phi_s)

        # The static faith-based survival threshold (eq-phi-underbar). It
        # is a function of the parameters only and is reported for
        # reference; this routine solves allocation and value, not the
        # default problem, so it says nothing about the threshold under
        # dynamic phi.
        R = ((p.r - p.mu_H) / (p.r - p.mu_L)) ** (1.0 / p.alpha)
        phi_underbar_static = R / (1.0 + R)

        return {
            "phi_static": phi_s,
            "phi_1_dynamic": phi_1_opt,
            "phi_H_dynamic": phi_H_opt,
            "phi_L2_dynamic": phi_L2_opt,
            "phi_underbar_static": phi_underbar_static,
            "value_dynamic": val_dynamic,
            "value_static": val_static,
            "value_gain_pct": (val_dynamic - val_static) / abs(val_static) * 100
            if val_static != 0
            else 0,
            "p_switch": p_switch,
            "adjustment_cost": kappa,
            "phi_1_below_static": phi_1_opt < phi_s,
        }

    # ------------------------------------------------------------------
    # Fixed-pie contest robustness (OF-4)
    # ------------------------------------------------------------------

    def fixed_pie_robustness(
        self,
        leverage: float = 0.0,
    ) -> dict[str, Any]:
        """Compare Tullock vs fixed-pie contest equilibrium objects.

        Solves the duopoly under both the standard Tullock contest and
        the fixed-pie variant (no revenue expansion), and reports key
        equilibrium quantities for comparison.
        """
        p = self.params

        # --- Standard Tullock ---
        duo_tullock = DuopolyModel(
            p,
            leverage=leverage,
            coupon_rate=CREDIT_COUPON_RATE,
            bankruptcy_cost=CREDIT_BANKRUPTCY_COST,
            recovery_rule=self.recovery_rule,
        )
        try:
            eq_tullock = duo_tullock.pure_power_preemption_equilibrium()
        except (ValueError, RuntimeError):
            return {"error": "Tullock equilibrium failed"}

        # Faith-based survival threshold (A_eff-channel, eq-phi-underbar)
        phi_underbar = duo_tullock.faith_threshold()

        # Dario dilemma asymmetry ratio under Tullock
        dd_cons = self.pure_power_dilemma(0.10, 0.02)
        dd_aggr = self.pure_power_dilemma(0.10, 0.20)
        loss_cons = dd_cons.get("value_loss_pct", np.nan)
        loss_aggr = dd_aggr.get("value_loss_pct", np.nan)
        asym_tullock = abs(loss_cons / loss_aggr) if loss_aggr != 0 else np.nan

        # --- Fixed-pie contest ---
        duo_fp = DuopolyModel(
            p,
            leverage=leverage,
            coupon_rate=CREDIT_COUPON_RATE,
            bankruptcy_cost=CREDIT_BANKRUPTCY_COST,
            contest="fixed_pie",
            recovery_rule=self.recovery_rule,
        )

        try:
            eq_fp = duo_fp.pure_power_preemption_equilibrium()
        except (ValueError, RuntimeError):
            eq_fp = None

        # Dario's dilemma under fixed-pie is computed using single-firm
        # (contest spec doesn't affect the single-firm dilemma, so the
        # asymmetry ratio is the same)

        result = {
            # Tullock results
            "tullock_phi_F": eq_tullock["phi_follower"],
            "tullock_X_F": eq_tullock["X_follower"],
            "tullock_K_F": eq_tullock["K_follower"],
            "tullock_X_P": eq_tullock["X_leader"],
            "tullock_phi_underbar": phi_underbar,
            "tullock_asym_ratio": asym_tullock,
            "tullock_preemption_discount": (
                eq_tullock["X_leader"] / eq_tullock["X_leader_monopolist"]
            ),
        }

        if eq_fp is not None:
            result.update({
                "fixedpie_phi_F": eq_fp["phi_follower"],
                "fixedpie_X_F": eq_fp["X_follower"],
                "fixedpie_K_F": eq_fp["K_follower"],
                "fixedpie_X_P": eq_fp["X_leader"],
                "fixedpie_preemption_discount": (
                    eq_fp["X_leader"] / eq_fp["X_leader_monopolist"]
                ),
            })
        else:
            result["fixedpie_error"] = "Fixed-pie equilibrium failed"

        return result

    # ------------------------------------------------------------------
    # Summary
    # ------------------------------------------------------------------

    def summary(self, X: float = 1.0, regime: str = "H") -> dict:
        """Comprehensive valuation summary."""
        result = {}

        # Growth option decomposition
        result["decomposition"] = self.growth_option_decomposition(
            X, K_installed=0.0, regime=regime
        )

        # Credit risk at different leverage levels
        leverages = [0.0, 0.2, 0.4, 0.6]
        result["credit"] = {}
        for lev in leverages:
            # Credit metrics are L-regime objects regardless of the
            # regime used for the value decomposition above.
            spread = self.credit_spread(lev, regime="L")
            prob = self.default_probability(X, 1.0, lev, regime="L")
            result["credit"][f"leverage_{lev}"] = {
                "spread_bps": spread * 10000,
                "default_prob_5yr": prob,
            }

        # Dario dilemma example
        result["dario_dilemma"] = self.dario_dilemma(lambda_true=0.3, lambda_invest=0.1)

        return result
