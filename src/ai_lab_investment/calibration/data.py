"""Calibration data for AI infrastructure investment models.

Contains publicly available data points for calibrating the model:
- Revenue trajectories for major AI labs
- GPU pricing and compute costs
- Capital structure information
- Scaling law estimates

Sources are documented for each data point. All values are stylized
approximations from public reports and filings.
"""

from dataclasses import dataclass, field

from ..models.parameters import ModelParameters


@dataclass
class FirmData:
    """Stylized data for a single AI lab.

    Attributes:
        name: Firm identifier.
        revenue_2024: Estimated 2024 revenue ($B).
        revenue_2025: Estimated 2025 revenue ($B).
        capex_2024: Capital expenditure 2024 ($B).
        capex_2025: Estimated capital expenditure 2025 ($B).
        gpu_count: Estimated GPU fleet size (thousands).
        leverage_ratio: Debt-to-total-capital ratio.
        wacc: Weighted average cost of capital estimate.
        description: Brief characterization.
    """

    name: str
    revenue_2024: float
    revenue_2025: float
    capex_2024: float
    capex_2025: float
    gpu_count: float  # Thousands
    leverage_ratio: float
    wacc: float
    description: str = ""


@dataclass
class CalibrationData:
    """Complete calibration dataset.

    Contains baseline parameter estimates and firm-specific data.
    Sources are documented in the `sources` dict.
    """

    # Demand process parameters
    mu_L: float = 0.02  # Pre-adoption drift (~2% growth)
    mu_H: float = 0.06  # Post-adoption drift (~6% growth, conservative)
    sigma_L: float = 0.25  # Pre-adoption volatility
    sigma_H: float = 0.30  # Post-adoption volatility (higher uncertainty)

    # Technology parameters
    alpha: float = 0.40  # Revenue elasticity (calibrated from scaling laws)
    gamma: float = 1.5  # Cost convexity
    c: float = 1.0  # Cost scale (normalized)
    delta: float = 0.03  # Operating cost rate

    # Financial parameters
    r: float = 0.12  # Baseline discount rate (tech WACC)
    tau: float = 0.0  # Time-to-build (years)

    # Regime switching
    lam: float = 0.10  # Baseline arrival rate

    # Firm data
    firms: list[FirmData] = field(default_factory=list)

    # Data sources
    sources: dict[str, str] = field(default_factory=dict)

    def to_model_params(self, lam: float | None = None) -> ModelParameters:
        """Convert calibration data to model parameters.

        Args:
            lam: Override arrival rate (used in revealed beliefs inversion).
        """
        return ModelParameters(
            r=self.r,
            mu_L=self.mu_L,
            mu_H=self.mu_H,
            sigma_L=self.sigma_L,
            sigma_H=self.sigma_H,
            lam=lam if lam is not None else self.lam,
            alpha=self.alpha,
            gamma=self.gamma,
            c=self.c,
            delta=self.delta,
            tau=self.tau,
        )


def get_stylized_firms() -> list[FirmData]:
    """Return stylized versions of major AI infrastructure firms.

    Data is approximate and from public sources (press reports, 10-K
    filings, analyst estimates). These are illustrative calibration
    targets, not precise figures.
    """
    return [
        FirmData(
            name="Firm A (Anthropic-like)",
            revenue_2024=1.0,
            revenue_2025=9.0,
            capex_2024=2.0,
            capex_2025=5.0,
            gpu_count=50,
            leverage_ratio=0.15,
            wacc=0.15,
            description=(
                "Pure-play AI lab, rapid revenue growth, "
                "moderate leverage via venture debt"
            ),
        ),
        FirmData(
            name="Firm B (OpenAI-like)",
            revenue_2024=3.5,
            revenue_2025=12.0,
            capex_2024=3.0,
            capex_2025=8.0,
            gpu_count=80,
            leverage_ratio=0.20,
            wacc=0.14,
            description=(
                "Largest pure-play AI lab, high revenue, "
                "growing debt from credit facilities"
            ),
        ),
        FirmData(
            name="Firm C (Google/Alphabet-like)",
            revenue_2024=10.0,
            revenue_2025=20.0,
            capex_2024=30.0,
            capex_2025=50.0,
            gpu_count=200,
            leverage_ratio=0.05,
            wacc=0.10,
            description=(
                "Hyperscaler with massive existing infrastructure, "
                "low leverage, low cost of capital"
            ),
        ),
        FirmData(
            name="Firm D (CoreWeave-like)",
            revenue_2024=1.5,
            revenue_2025=4.0,
            capex_2024=8.0,
            capex_2025=15.0,
            gpu_count=100,
            leverage_ratio=0.70,
            wacc=0.18,
            description=(
                "GPU cloud provider, very high leverage, "
                "high cost of capital, high growth"
            ),
        ),
    ]


def get_baseline_calibration() -> CalibrationData:
    """Return the baseline calibration with all data.

    Returns:
        CalibrationData with baseline parameters and firm data.
    """
    firms = get_stylized_firms()
    sources = {
        "revenue": (
            "Public revenue estimates from press reports. "
            "Anthropic: Dario Amodei interview (2024). "
            "OpenAI: The Information, Bloomberg estimates."
        ),
        "capex": (
            "Hyperscaler CapEx from 10-K filings (Alphabet, Microsoft, Amazon). "
            "Pure-play estimates from funding round disclosures."
        ),
        "gpu_pricing": (
            "H100 ~$25-30K, B200 ~$30-40K (NVIDIA pricing, analyst reports). "
            "Cost per GW-year ~$10-15B (Dario Amodei estimate)."
        ),
        "scaling_laws": (
            "Kaplan et al. (2020), Hoffmann et al. (2022). "
            "Revenue elasticity alpha=0.40 calibrated to translate "
            "compute-to-loss scaling to revenue impact."
        ),
        "time_to_build": (
            "18-36 months for large data center campuses (industry reports, CBRE, JLL)."
        ),
        "wacc": (
            "Tech sector WACC estimates. Pure-play AI firms: 14-18%. "
            "Hyperscalers: 10-12%. GPU cloud (leveraged): 16-20%."
        ),
    }

    return CalibrationData(firms=firms, sources=sources)
