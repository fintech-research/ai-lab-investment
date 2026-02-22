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
