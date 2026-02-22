"""Revealed beliefs methodology for inferring AI timeline beliefs.

The core insight: a firm's observable investment decision (when it invests
and how much capacity it builds) is a deterministic function of model
parameters including lambda (the arrival rate of transformative AI).
All parameters except lambda are observable or can be calibrated from
public data. Therefore, we can invert the model to back out each firm's
implied lambda — its "revealed belief" about AI timelines.

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
        regime: str = "H",
        lam_bounds: tuple[float, float] = (0.001, 2.0),
    ) -> float | None:
        """Infer lambda from a firm's observed capex level.

        Uses the ratio of capex to revenue as a proxy for the
        investment intensity, which the model predicts as a function
        of lambda.

        Higher lambda (more confident in AI adoption) -> invest more
        aggressively relative to current revenue.

        Args:
            firm: Firm data with observed revenue and capex.
            regime: Demand regime.
            lam_bounds: Search bounds for lambda.

        Returns:
            Implied lambda, or None if no solution found.
        """
        if firm.revenue_2025 <= 0:
            return None

        # Investment intensity: capex / revenue
        observed_intensity = firm.capex_2025 / firm.revenue_2025

        def gap(lam: float) -> float:
            try:
                params = self.calibration.to_model_params(lam=lam)
                # Adjust discount rate for firm-specific WACC
                params = params.with_param(r=firm.wacc)
                model = SingleFirmModel(params)
                X_star, K_star = model.optimal_trigger_and_capacity(regime)
                # Model-predicted investment intensity
                I_K = model.investment_cost(K_star)
                V = model.installed_value(X_star, K_star, regime)
                if V <= 0:
                    return 1e10
                predicted_intensity = I_K / V
                return predicted_intensity - observed_intensity
            except (ValueError, RuntimeError):
                return 1e10

        try:
            g_lo = gap(lam_bounds[0])
            g_hi = gap(lam_bounds[1])
            if np.isinf(g_lo) or np.isinf(g_hi):
                return None
            if abs(g_lo) > 1e9 or abs(g_hi) > 1e9:
                return None
            if g_lo * g_hi > 0:
                return None
            return optimize.brentq(gap, lam_bounds[0], lam_bounds[1], xtol=1e-6)
        except (ValueError, RuntimeError):
            return None

    def sensitivity_analysis(
        self,
        observed_trigger: float,
        param_name: str,
        param_range: np.ndarray,
        regime: str = "H",
    ) -> dict[str, np.ndarray]:
        """Assess sensitivity of implied lambda to a parameter.

        For each value of the specified parameter, re-infer lambda.
        Shows how robust the revealed belief is to calibration assumptions.

        Args:
            observed_trigger: Observed investment trigger.
            param_name: Parameter to vary.
            param_range: Values to sweep.
            regime: Demand regime.

        Returns:
            Dict with 'param_values' and 'implied_lambda' arrays.
        """
        n = len(param_range)
        implied_lambdas = np.full(n, np.nan)

        for i, val in enumerate(param_range):
            # Create modified calibration
            calib = CalibrationData(
                mu_L=self.calibration.mu_L,
                mu_H=self.calibration.mu_H,
                sigma_L=self.calibration.sigma_L,
                sigma_H=self.calibration.sigma_H,
                alpha=self.calibration.alpha,
                gamma=self.calibration.gamma,
                c=self.calibration.c,
                delta=self.calibration.delta,
                r=self.calibration.r,
                tau=self.calibration.tau,
                lam=self.calibration.lam,
            )
            setattr(calib, param_name, val)
            rb = RevealedBeliefs(calib)
            result = rb.infer_lambda_from_trigger(observed_trigger, regime)
            if result is not None:
                implied_lambdas[i] = result

        return {
            "param_values": param_range,
            "implied_lambda": implied_lambdas,
        }

    def compute_all_revealed_beliefs(self, regime: str = "H") -> list[dict]:
        """Compute revealed beliefs for all firms in the calibration.

        Uses multiple methods to infer lambda for each firm.

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
            }

            # Method 1: From capex intensity
            lam_capex = self.infer_lambda_from_capex(firm, regime)
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
        predictions = self.investment_predictions(
            np.array([0.05, 0.10, 0.20, 0.50, 1.0])
        )

        return {
            "n_firms": len(self.calibration.firms),
            "revealed_beliefs": beliefs,
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
