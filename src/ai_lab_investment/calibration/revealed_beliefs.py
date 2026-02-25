"""Revealed beliefs methodology for inferring AI timeline beliefs.

The core insight: a firm's observable investment decision (when it invests
and how much capacity it builds) is a deterministic function of model
parameters including lambda (the arrival rate of transformative AI).
All parameters except lambda are observable or can be calibrated from
public data. Therefore, we can invert the model to back out each firm's
implied lambda — its "revealed belief" about AI timelines.

Extended methodology with training-inference allocation:
  With phi (training fraction) as a new observable, we have two moments:
  1. CapEx/Revenue ratio → investment intensity
  2. Training fraction phi → allocation choice
  These jointly identify (lambda, phi) or, given observed phi, provide
  a tighter identification of lambda alone.

If firms have private information about AI progress (internal benchmarks,
scaling curves, emergent capabilities), the revealed lambda contains
information not available to outside observers.
"""

import numpy as np
from scipy import optimize

from ..models.base_model import SingleFirmModel
from .data import CalibrationData, FirmData


class RevealedBeliefs:
    """Inversion algorithm for revealed beliefs about AI arrival rate.

    Given a firm's observed investment behavior, infers the lambda
    (regime-switch arrival rate) that rationalizes its decisions.
    """

    def __init__(self, calibration: CalibrationData):
        self.calibration = calibration

    def _model_trigger_at_lambda(self, lam: float, regime: str = "H") -> float:
        """Compute the model's predicted trigger at a given lambda.

        Returns X* for regime H (the trigger that matters for investment
        timing decisions).
        """
        try:
            params = self.calibration.to_model_params(lam=lam)
            model = SingleFirmModel(params)
            X_star, _ = model.optimal_trigger_and_capacity(regime)
        except (ValueError, RuntimeError):
            return np.inf
        return X_star

    def _model_capacity_at_lambda(self, lam: float, regime: str = "H") -> float:
        """Compute the model's predicted capacity at a given lambda."""
        try:
            params = self.calibration.to_model_params(lam=lam)
            model = SingleFirmModel(params)
            _, K_star = model.optimal_trigger_and_capacity(regime)
        except (ValueError, RuntimeError):
            return np.inf
        return K_star

    def _model_intensity_at_lambda(self, lam: float, X_ref: float = 0.01) -> float:
        """Compute model-predicted investment intensity at a given lambda.

        Uses the L-regime option value (which IS lambda-dependent) relative
        to the H-regime investment cost. The ratio F_L(X_ref) / I(K*_H)
        is monotonically increasing in lambda and serves as the model's
        prediction for investment intensity (CapEx/Revenue).

        The H-regime optimal capacity K*_H and investment cost I(K*_H) are
        lambda-independent (they depend only on A_H, beta_H, and cost
        parameters), so only the numerator F_L varies with lambda.
        """
        try:
            params = self.calibration.to_model_params(lam=lam)
            model = SingleFirmModel(params)
            _, K_star_H = model.optimal_trigger_and_capacity("H")
            I_K = model.investment_cost(K_star_H)
            F_L = model.option_value_L(X_ref)
            if I_K <= 0:
                return np.inf
            return F_L / I_K
        except (ValueError, RuntimeError):
            return np.inf

    def infer_lambda_from_trigger(
        self,
        observed_trigger: float,
        regime: str = "H",
        lam_bounds: tuple[float, float] = (0.001, 2.0),
    ) -> float | None:
        """Infer lambda from an observed investment trigger.

        Finds the lambda such that the model's predicted X* matches
        the observed trigger.

        Args:
            observed_trigger: The demand level at which the firm invested.
            regime: Demand regime.
            lam_bounds: Search bounds for lambda.

        Returns:
            Implied lambda, or None if no solution found.
        """

        def gap(lam: float) -> float:
            predicted = self._model_trigger_at_lambda(lam, regime)
            return predicted - observed_trigger

        try:
            # Check that the gap changes sign across bounds
            g_lo = gap(lam_bounds[0])
            g_hi = gap(lam_bounds[1])

            if np.isinf(g_lo) or np.isinf(g_hi):
                return None
            if g_lo * g_hi > 0:
                return None

            return optimize.brentq(gap, lam_bounds[0], lam_bounds[1], xtol=1e-6)
        except (ValueError, RuntimeError):
            return None

    def infer_lambda_from_capex(
        self,
        firm: FirmData,
        X_ref: float = 0.01,
        lam_bounds: tuple[float, float] = (0.001, 2.0),
    ) -> float | None:
        """Infer lambda from a firm's observed capex-to-revenue ratio.

        Uses the L-regime option value F_L(X_ref) relative to the H-regime
        investment cost I(K*_H) as the model's prediction for investment
        intensity. This ratio is monotonically increasing in lambda because:

        - I(K*_H) is lambda-independent (H-regime quantities depend only on
          A_H = 1/(r - mu_H) and beta_H, neither involving lambda)
        - F_L(X_ref) = D_L * X^beta_L + C * X^beta_H where C = -lam * B_H / Q_L(beta_H)
          is increasing in lambda (the L-regime option value derives from
          the possibility of switching to H)

        The economic interpretation: a firm in regime L with higher lambda
        values the potential regime switch more, making its growth option
        (and hence willingness to invest) larger relative to current scale.

        Args:
            firm: Firm data with observed revenue and capex.
            X_ref: Reference demand level for evaluating F_L.
            lam_bounds: Search bounds for lambda.

        Returns:
            Implied lambda, or None if no solution found.
        """
        if firm.revenue_2025 <= 0:
            return None

        observed_intensity = firm.capex_2025 / firm.revenue_2025

        def gap(lam: float) -> float:
            predicted = self._model_intensity_at_lambda(lam, X_ref)
            if np.isinf(predicted):
                return 1e10
            return predicted - observed_intensity

        try:
            g_lo = gap(lam_bounds[0])
            g_hi = gap(lam_bounds[1])
            if abs(g_lo) > 1e9 or abs(g_hi) > 1e9:
                return None
            if g_lo * g_hi > 0:
                return None
            return optimize.brentq(gap, lam_bounds[0], lam_bounds[1], xtol=1e-6)
        except (ValueError, RuntimeError):
            return None

    # ------------------------------------------------------------------
    # Phi-aware inversion methods
    # ------------------------------------------------------------------

    def _model_phi_intensity_at_lambda(
        self, lam: float, X_ref: float = 0.01
    ) -> tuple[float, float]:
        """Model-predicted (intensity, phi*) at a given lambda.

        Uses the phi-aware single-firm model to jointly predict
        investment intensity and optimal training fraction.

        Returns:
            (intensity, phi*) tuple. intensity = F(X_ref) / I(K*).
        """
        try:
            params = self.calibration.to_model_params(lam=lam)
            model = SingleFirmModel(params)
            X_star, K_star, phi_star = model.optimal_trigger_capacity_phi()
            I_K = model.investment_cost(K_star)
            F = model.option_value_with_phi(X_ref)
            if I_K <= 0:
                return np.inf, phi_star
            return F / I_K, phi_star
        except (ValueError, RuntimeError):
            return np.inf, 0.5

    def infer_lambda_with_phi(
        self,
        firm: FirmData,
        X_ref: float = 0.01,
        lam_bounds: tuple[float, float] = (0.001, 2.0),
    ) -> dict[str, float | None]:
        """Infer lambda using the phi-aware model.

        Uses two moments when training_fraction is available:
        1. CapEx/Revenue → investment intensity (primary)
        2. Training fraction → model-predicted phi* (diagnostic)

        The inversion targets intensity (moment 1) and reports the
        model-predicted phi* as a consistency check against the
        observed training fraction.

        Args:
            firm: Firm data with observed revenue, capex, and
                optionally training_fraction.
            X_ref: Reference demand level.
            lam_bounds: Search bounds for lambda.

        Returns:
            Dict with lambda_implied, phi_model, phi_observed, etc.
        """
        if firm.revenue_2025 <= 0:
            return {"lambda_implied": None, "error": "zero revenue"}

        observed_intensity = firm.capex_2025 / firm.revenue_2025

        def gap(lam: float) -> float:
            intensity, _ = self._model_phi_intensity_at_lambda(lam, X_ref)
            if np.isinf(intensity):
                return 1e10
            return intensity - observed_intensity

        lambda_implied = None
        phi_model = None
        try:
            g_lo = gap(lam_bounds[0])
            g_hi = gap(lam_bounds[1])
            if abs(g_lo) <= 1e9 and abs(g_hi) <= 1e9 and g_lo * g_hi < 0:
                lambda_implied = optimize.brentq(
                    gap, lam_bounds[0], lam_bounds[1], xtol=1e-6
                )
                _, phi_model = self._model_phi_intensity_at_lambda(
                    lambda_implied, X_ref
                )
        except (ValueError, RuntimeError):
            pass

        return {
            "lambda_implied": lambda_implied,
            "phi_model": phi_model,
            "phi_observed": (
                firm.training_fraction if firm.training_fraction > 0 else None
            ),
            "capex_intensity": observed_intensity,
        }

    def compute_all_revealed_beliefs_with_phi(self, X_ref: float = 0.01) -> list[dict]:
        """Compute revealed beliefs using the phi-aware model.

        Returns:
            List of dicts with firm name, inferred lambda, model-predicted
            phi, observed phi, and diagnostic information.
        """
        results = []
        for firm in self.calibration.firms:
            result = {
                "firm": firm.name,
                "revenue_growth": (
                    firm.revenue_2025 / firm.revenue_2024
                    if firm.revenue_2024 > 0
                    else np.inf
                ),
                "leverage": firm.leverage_ratio,
                "wacc": firm.wacc,
            }

            belief = self.infer_lambda_with_phi(firm, X_ref=X_ref)
            result.update(belief)

            # Also compute legacy single-moment inversion
            lam_legacy = self.infer_lambda_from_capex(firm, X_ref=X_ref)
            result["lambda_from_capex_legacy"] = lam_legacy

            results.append(result)

        return results

    def sensitivity_analysis(
        self,
        firm: FirmData,
        param_name: str,
        param_range: np.ndarray,
        X_ref: float = 0.01,
    ) -> dict[str, np.ndarray]:
        """Assess sensitivity of implied lambda to a parameter.

        For each value of the specified parameter, re-infer lambda from
        the firm's observed CapEx/Revenue ratio.

        Args:
            firm: Firm data with observed revenue and capex.
            param_name: Parameter to vary.
            param_range: Values to sweep.
            X_ref: Reference demand level.

        Returns:
            Dict with 'param_values' and 'implied_lambda' arrays.
        """
        n = len(param_range)
        implied_lambdas = np.full(n, np.nan)

        for i, val in enumerate(param_range):
            calib = CalibrationData(
                mu_L=self.calibration.mu_L,
                mu_H=self.calibration.mu_H,
                sigma=self.calibration.sigma,
                alpha=self.calibration.alpha,
                gamma=self.calibration.gamma,
                c=self.calibration.c,
                delta=self.calibration.delta,
                r=self.calibration.r,
                tau=self.calibration.tau,
                lam=self.calibration.lam,
                firms=self.calibration.firms,
            )
            setattr(calib, param_name, val)
            rb = RevealedBeliefs(calib)
            result = rb.infer_lambda_from_capex(firm, X_ref=X_ref)
            if result is not None:
                implied_lambdas[i] = result

        return {
            "param_values": param_range,
            "implied_lambda": implied_lambdas,
        }

    def compute_all_revealed_beliefs(self, X_ref: float = 0.01) -> list[dict]:
        """Compute revealed beliefs for all firms in the calibration.

        Uses the L-regime option value inversion to infer lambda.

        Args:
            X_ref: Reference demand level for F_L evaluation.

        Returns:
            List of dicts with firm name, inferred lambdas, and metadata.
        """
        results = []
        for firm in self.calibration.firms:
            result = {
                "firm": firm.name,
                "revenue_growth": (
                    firm.revenue_2025 / firm.revenue_2024
                    if firm.revenue_2024 > 0
                    else np.inf
                ),
                "capex_intensity": (
                    firm.capex_2025 / firm.revenue_2025
                    if firm.revenue_2025 > 0
                    else np.inf
                ),
                "leverage": firm.leverage_ratio,
                "wacc": firm.wacc,
                "training_fraction": firm.training_fraction,
            }

            # Infer from capex intensity using L-regime option value
            lam_capex = self.infer_lambda_from_capex(firm, X_ref=X_ref)
            result["lambda_from_capex"] = lam_capex

            results.append(result)

        return results

    def investment_predictions(
        self,
        lambda_values: np.ndarray,
        regime: str = "H",
    ) -> dict[str, np.ndarray]:
        """Predict investment patterns for different lambda beliefs.

        Shows what investment levels are consistent with different
        beliefs about AI timelines.

        Args:
            lambda_values: Array of lambda values to evaluate.
            regime: Demand regime.

        Returns:
            Dict with triggers, capacities, and investment costs.
        """
        n = len(lambda_values)
        triggers = np.full(n, np.nan)
        capacities = np.full(n, np.nan)
        costs = np.full(n, np.nan)
        has_solution = np.zeros(n, dtype=bool)

        for i, lam in enumerate(lambda_values):
            try:
                params = self.calibration.to_model_params(lam=lam)
                model = SingleFirmModel(params)
                X_star, K_star = model.optimal_trigger_and_capacity(regime)
                triggers[i] = X_star
                capacities[i] = K_star
                costs[i] = model.investment_cost(K_star)
                has_solution[i] = True
            except (ValueError, RuntimeError):
                continue

        return {
            "lambda_values": lambda_values,
            "triggers": triggers,
            "capacities": capacities,
            "investment_costs": costs,
            "has_solution": has_solution,
        }

    def summary(self) -> dict:
        """Return a summary of revealed beliefs analysis."""
        beliefs = self.compute_all_revealed_beliefs()
        beliefs_phi = self.compute_all_revealed_beliefs_with_phi()
        predictions = self.investment_predictions(
            np.array([0.05, 0.10, 0.20, 0.50, 1.0])
        )

        return {
            "n_firms": len(self.calibration.firms),
            "revealed_beliefs": beliefs,
            "revealed_beliefs_with_phi": beliefs_phi,
            "predictions_by_lambda": {
                "lambda": predictions["lambda_values"].tolist(),
                "triggers": [
                    float(t) if not np.isnan(t) else None
                    for t in predictions["triggers"]
                ],
                "capacities": [
                    float(c) if not np.isnan(c) else None
                    for c in predictions["capacities"]
                ],
            },
            "sources": self.calibration.sources,
        }
