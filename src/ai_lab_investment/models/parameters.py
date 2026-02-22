"""Model parameters for AI compute investment under regime-switching uncertainty."""

from dataclasses import dataclass, field


@dataclass
class ModelParameters:
    """Parameters for the single-firm investment model with regime switching.

    The demand shifter X_t follows a GBM with regime-dependent drift and
    volatility. The firm invests irreversibly in capacity K at convex cost
    I(K) = c * K^gamma, earning flow revenue pi(K, X) = X * K^alpha with
    operating costs delta * K.

    The drift parameters represent risk-neutral drifts (net of risk premium).
    The discount rate r is the risk-adjusted rate (WACC).

    Attributes:
        r: Risk-adjusted discount rate (WACC).
        mu_L: Risk-neutral demand drift in regime L (pre-adoption).
        mu_H: Risk-neutral demand drift in regime H (post-adoption).
        sigma_L: Volatility of demand in regime L.
        sigma_H: Volatility of demand in regime H.
        lam: Poisson arrival rate of regime switch L -> H.
        alpha: Revenue elasticity to capacity (0 < alpha < 1).
        gamma: Cost convexity exponent (gamma > 1).
        c: Investment cost scale parameter.
        delta: Operating cost per unit of capacity per unit time.
        tau: Time-to-build lag (years). Set to 0 for base analytical case.
    """

    # Discount rate (WACC for AI infrastructure firms)
    r: float = 0.12
    # Risk-neutral demand drift in low regime (pre-adoption)
    mu_L: float = 0.01
    # Risk-neutral demand drift in high regime (post-adoption)
    mu_H: float = 0.06
    sigma_L: float = 0.25
    sigma_H: float = 0.30
    # Poisson arrival rate of regime switch L -> H
    lam: float = 0.10
    # Revenue elasticity to capacity; must satisfy alpha > 1 - 1/beta_H
    # for an interior solution. With sigma_H=0.30, beta_H ~ 1.47,
    # so alpha > 0.32 is needed. We use 0.40.
    alpha: float = 0.40
    # Cost convexity (must be > 1)
    gamma: float = 1.5
    c: float = 1.0
    delta: float = 0.03
    tau: float = 0.0

    # Derived quantities (computed in __post_init__)
    _beta_H: float = field(init=False, repr=False)
    _beta_L: float = field(init=False, repr=False)
    _A_H: float = field(init=False, repr=False)
    _A_L: float = field(init=False, repr=False)

    def __post_init__(self):
        self._validate()
        self._compute_derived()

    def _validate(self):
        if self.r <= 0:
            msg = f"Discount rate r must be positive, got {self.r}"
            raise ValueError(msg)
        if self.r <= self.mu_H:
            msg = (
                f"Discount rate r={self.r} must exceed high-regime drift "
                f"mu_H={self.mu_H} for convergence"
            )
            raise ValueError(msg)
        if self.r <= self.mu_L:
            msg = (
                f"Discount rate r={self.r} must exceed low-regime drift "
                f"mu_L={self.mu_L} for convergence"
            )
            raise ValueError(msg)
        if not 0 < self.alpha < 1:
            msg = f"Revenue elasticity alpha must be in (0,1), got {self.alpha}"
            raise ValueError(msg)
        if self.gamma <= 1:
            msg = (
                f"Cost convexity gamma must be > 1 for well-defined capacity, "
                f"got {self.gamma}"
            )
            raise ValueError(msg)
        if self.c <= 0:
            msg = f"Cost scale c must be positive, got {self.c}"
            raise ValueError(msg)
        if self.sigma_L <= 0 or self.sigma_H <= 0:
            msg = "Volatilities must be positive"
            raise ValueError(msg)
        if self.lam < 0:
            msg = f"Arrival rate lambda must be non-negative, got {self.lam}"
            raise ValueError(msg)
        if self.tau < 0:
            msg = f"Time-to-build tau must be non-negative, got {self.tau}"
            raise ValueError(msg)

    def _compute_derived(self):
        """Compute derived quantities from primitive parameters."""
        self._beta_H = _positive_root(self.sigma_H, self.mu_H, self.r)
        self._beta_L = _positive_root(self.sigma_L, self.mu_L, self.r + self.lam)
        self._A_H = 1.0 / (self.r - self.mu_H)
        if self.lam > 0:
            self._A_L = (self.r - self.mu_H + self.lam) / (
                (self.r - self.mu_H) * (self.r - self.mu_L + self.lam)
            )
        else:
            self._A_L = 1.0 / (self.r - self.mu_L)

    @property
    def beta_H(self) -> float:
        """Positive characteristic root in regime H."""
        return self._beta_H

    @property
    def beta_L(self) -> float:
        """Positive root for regime L (effective discount r+lambda)."""
        return self._beta_L

    @property
    def A_H(self) -> float:
        """Present-value multiplier for revenue in regime H."""
        return self._A_H

    @property
    def A_L(self) -> float:
        """Present-value multiplier for revenue in regime L with switching."""
        return self._A_L

    def with_param(self, **kwargs) -> "ModelParameters":
        """Return a new ModelParameters with specified parameters changed."""
        params = {
            "r": self.r,
            "mu_L": self.mu_L,
            "mu_H": self.mu_H,
            "sigma_L": self.sigma_L,
            "sigma_H": self.sigma_H,
            "lam": self.lam,
            "alpha": self.alpha,
            "gamma": self.gamma,
            "c": self.c,
            "delta": self.delta,
            "tau": self.tau,
        }
        params.update(kwargs)
        return ModelParameters(**params)


def _positive_root(sigma: float, mu: float, discount: float) -> float:
    """Compute the positive root of the characteristic equation.

    Solves: (sigma^2/2) * beta * (beta - 1) + mu * beta - discount = 0
    """
    a = 0.5 * sigma**2
    b = mu - 0.5 * sigma**2
    c = -discount
    discriminant = b**2 - 4 * a * c
    return (-b + discriminant**0.5) / (2 * a)
