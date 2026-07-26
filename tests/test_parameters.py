"""Tests for model parameters."""

import pytest

from ai_lab_investment.models.parameters import ModelParameters, _positive_root


class TestPositiveRoot:
    def test_known_case(self):
        beta = _positive_root(0.2, 0.05, 0.10)
        assert beta > 1.0
        residual = 0.5 * 0.2**2 * beta * (beta - 1) + 0.05 * beta - 0.10
        assert abs(residual) < 1e-12

    def test_positive(self):
        beta = _positive_root(0.25, 0.02, 0.05)
        assert beta > 1.0

    def test_higher_vol_lower_root(self):
        beta_low = _positive_root(0.15, 0.02, 0.05)
        beta_high = _positive_root(0.30, 0.02, 0.05)
        assert beta_low > beta_high


class TestModelParameters:
    def test_defaults_valid(self):
        p = ModelParameters()
        assert p.r == 0.12
        assert p.beta_H > 1.0
        assert p.beta_L > 1.0
        assert p.A_H > 0
        assert p.A_L > 0

    def test_A_H_formula(self):
        p = ModelParameters()
        assert abs(p.A_H - 1.0 / (p.r - p.mu_H)) < 1e-12

    def test_A_L_with_lambda(self):
        p = ModelParameters(lam=0.1)
        expected = (p.r - p.mu_H + p.lam) / ((p.r - p.mu_H) * (p.r - p.mu_L + p.lam))
        assert abs(p.A_L - expected) < 1e-12

    def test_A_L_without_regime_switching(self):
        p = ModelParameters(lam=1e-10)
        expected = 1.0 / (p.r - p.mu_L)
        assert abs(p.A_L - expected) < 1e-6

    def test_invalid_r_below_mu_H(self):
        with pytest.raises(ValueError, match="exceed high-regime drift"):
            ModelParameters(r=0.05, mu_H=0.10)

    def test_invalid_alpha(self):
        with pytest.raises(ValueError, match="alpha"):
            ModelParameters(alpha=1.5)

    def test_invalid_gamma(self):
        with pytest.raises(ValueError, match="gamma"):
            ModelParameters(gamma=0.5)

    def test_with_param(self):
        p = ModelParameters(lam=0.1)
        p2 = p.with_param(lam=0.3)
        assert p2.lam == 0.3
        assert p.lam == 0.1
        assert p2.A_L != p.A_L

    def test_A_L_increases_with_lambda(self):
        p1 = ModelParameters(lam=0.05)
        p2 = ModelParameters(lam=0.30)
        assert p2.A_L > p1.A_L


class TestValidationGuards:
    """Inadmissible primitives must fail loudly at construction."""

    def test_zero_volatility_raises(self):
        with pytest.raises(ValueError, match="Volatility"):
            ModelParameters(sigma=0.0)

    def test_negative_volatility_raises(self):
        with pytest.raises(ValueError, match="Volatility"):
            ModelParameters(sigma=-0.25)

    def test_mu_H_below_mu_L_raises(self):
        """(A1): the switch to H is a growth acceleration, mu_H > mu_L."""
        with pytest.raises(ValueError, match="must exceed low-regime"):
            ModelParameters(mu_L=0.06, mu_H=0.01)

    def test_mu_H_equal_mu_L_raises(self):
        with pytest.raises(ValueError, match="must exceed low-regime"):
            ModelParameters(mu_L=0.05, mu_H=0.05)

    def test_negative_delta_raises(self):
        with pytest.raises(ValueError, match="delta"):
            ModelParameters(delta=-0.01)

    def test_zero_delta_allowed(self):
        assert ModelParameters(delta=0.0).delta == 0.0

    def test_negative_lambda_raises(self):
        with pytest.raises(ValueError, match="lambda"):
            ModelParameters(lam=-0.01)

    def test_with_param_revalidates(self):
        """with_param goes through __post_init__, so guards still bite."""
        p = ModelParameters()
        with pytest.raises(ValueError, match="Volatility"):
            p.with_param(sigma=0.0)


class TestLambdaEdgeCases:
    """The lam = 0 branch and the large-lambda limit."""

    def test_exact_zero_lambda_A_L(self):
        """At lam = 0 exactly, A_L collapses to the pure-L perpetuity."""
        p = ModelParameters(lam=0.0)
        assert abs(p.A_L - 1.0 / (p.r - p.mu_L)) < 1e-15

    def test_exact_zero_lambda_beta_L(self):
        """At lam = 0, beta_L solves the L equation discounted at r."""
        p = ModelParameters(lam=0.0)
        beta = p.beta_L
        residual = 0.5 * p.sigma**2 * beta * (beta - 1.0) + p.mu_L * beta - p.r
        assert abs(residual) < 1e-12

    def test_zero_lambda_is_limit_of_small_lambda(self):
        p0 = ModelParameters(lam=0.0)
        p_eps = ModelParameters(lam=1e-9)
        assert abs(p0.A_L - p_eps.A_L) < 1e-7
        assert abs(p0.beta_L - p_eps.beta_L) < 1e-7

    def test_large_lambda_A_L_approaches_A_H(self):
        """As lambda -> infinity the firm is effectively already in H."""
        p = ModelParameters(lam=1e6)
        assert abs(p.A_L - p.A_H) / p.A_H < 1e-5

    def test_large_lambda_beta_L_grows(self):
        """beta_L is increasing in the effective discount rate r + lambda."""
        p_small = ModelParameters(lam=0.10)
        p_large = ModelParameters(lam=100.0)
        assert p_large.beta_L > p_small.beta_L
        beta = p_large.beta_L
        residual = (
            0.5 * p_large.sigma**2 * beta * (beta - 1.0)
            + p_large.mu_L * beta
            - (p_large.r + p_large.lam)
        )
        assert abs(residual) < 1e-6
