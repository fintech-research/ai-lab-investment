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
        training_fraction: Estimated fraction of compute allocated to
            training (vs inference). 0.0 = unknown/not estimated.
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
    training_fraction: float = 0.0
    description: str = ""


@dataclass
class CalibrationData:
    """Complete calibration dataset.

    Contains baseline parameter estimates and firm-specific data.
    Sources are documented in the `sources` dict.
    """

    # Demand process parameters
    mu_L: float = 0.01  # Pre-adoption drift (~1% growth, matches ModelParameters)
    mu_H: float = 0.06  # Post-adoption drift (~6% growth, conservative)
    sigma: float = 0.25  # Demand volatility (common across regimes)

    # Technology parameters
    alpha: float = 0.40  # Revenue elasticity (calibrated from scaling laws)
    gamma: float = 1.5  # Cost convexity
    c: float = 1.0  # Cost scale (normalized)
    delta: float = 0.03  # Operating cost rate

    # Financial parameters
    r: float = 0.12  # Baseline discount rate (tech WACC)
    tau: float = 0.0  # Time-to-build (years)

    # Regime switching
    lam: float = 0.10  # Baseline arrival rate (total effective)
    lam_0: float = 0.05  # Exogenous baseline arrival rate
    xi: float = 0.0  # Training scaling (0 = exogenous model)
    eta: float = 0.07  # Scaling law exponent (Kaplan et al. 2020)

    # Firm data
    firms: list[FirmData] = field(default_factory=list)

    # Data sources
    sources: dict[str, str] = field(default_factory=dict)

    def to_model_params(
        self,
        lam: float | None = None,
        xi: float | None = None,
    ) -> ModelParameters:
        """Convert calibration data to model parameters.

        Args:
            lam: Override arrival rate (used in revealed beliefs inversion).
            xi: Override training scaling parameter.
        """
        return ModelParameters(
            r=self.r,
            mu_L=self.mu_L,
            mu_H=self.mu_H,
            sigma=self.sigma,
            lam=lam if lam is not None else self.lam,
            lam_0=self.lam_0,
            xi=xi if xi is not None else self.xi,
            eta=self.eta,
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
            revenue_2024=0.9,
            revenue_2025=4.5,
            capex_2024=2.0,
            capex_2025=3.0,
            gpu_count=50,
            leverage_ratio=0.05,
            wacc=0.15,
            training_fraction=0.55,
            description=(
                "Pure-play AI lab, rapid revenue growth, nearly all-equity funded"
            ),
        ),
        FirmData(
            name="Firm B (OpenAI-like)",
            revenue_2024=3.7,
            revenue_2025=12.5,
            capex_2024=3.8,
            capex_2025=12.0,
            gpu_count=100,
            leverage_ratio=0.05,
            wacc=0.14,
            training_fraction=0.60,
            description=(
                "Largest pure-play AI lab, high revenue, revolving credit facility"
            ),
        ),
        FirmData(
            name="Firm C (Google/Alphabet-like)",
            revenue_2024=43.0,
            revenue_2025=60.0,
            capex_2024=52.5,
            capex_2025=91.0,
            gpu_count=250,
            leverage_ratio=0.10,
            wacc=0.10,
            training_fraction=0.35,
            description=(
                "Hyperscaler with massive existing infrastructure, "
                "low leverage, low cost of capital"
            ),
        ),
        FirmData(
            name="Firm D (xAI-like)",
            revenue_2024=0.2,
            revenue_2025=0.5,
            capex_2024=2.6,
            capex_2025=10.0,
            gpu_count=200,
            leverage_ratio=0.15,
            wacc=0.18,
            training_fraction=0.75,
            description=(
                "Compute-first frontier lab, extreme CapEx/Revenue, "
                "owned compute dedicated to training"
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
            "Anthropic: $0.9B collected 2024, $4-5B collected 2025 "
            "(SaaStr, Sacra). OpenAI: $3.7B 2024, $12-13B 2025 "
            "(CFO Sarah Friar, Jan 2026). Google Cloud: $43.2B "
            "2024, $59-60B 2025 (Alphabet SEC 10-K). xAI: ~$200M+ "
            "standalone 2025 (Bloomberg, Jan 2026)."
        ),
        "capex": (
            "Alphabet CapEx from SEC 10-K: $52.5B 2024, $91.4B 2025. "
            "Anthropic cloud spend: $2.66B through Sep 2025 (press). "
            "OpenAI Azure spend: $8.65B through Q3 2025 (The Information). "
            "xAI: ~$10B+ est. 2025 ($7.8B cash burn through Sep)."
        ),
        "gpu_pricing": (
            "H100 ~$25-40K, B200 ~$30-35K (NVIDIA pricing, analyst). "
            "Cloud rates fell 64-75% since early 2024. "
            "Cost per GW: $30-60B construction (Bernstein, AWS, McKinsey)."
        ),
        "scaling_laws": (
            "Kaplan et al. (2020), Hoffmann et al. (2022). "
            "Revenue elasticity alpha=0.40 calibrated from "
            "compute-to-loss power law exponents."
        ),
        "training_fraction": (
            "Amodei ~50/50 (Dwarkesh, Feb 2026). Epoch AI: OpenAI "
            "2024 71% R&D / 26% inference. Deloitte TMT 2026: "
            "industry shifting from 2/3 training to 2/3 inference. "
            "Range: 0.35-0.75 across archetypes."
        ),
        "time_to_build": (
            "12-24 months typical (hyperscaler); 2-4 years new builds. "
            "xAI Colossus: 122 days for 100K GPUs (exceptional)."
        ),
        "wacc": (
            "Damodaran Jan 2025: software 7.2%, semis 10.8%. "
            "Private AI labs: CAPM with beta 1.5-2.5 gives 10.5-15%. "
            "Hyperscalers: 9-10% (Alphabet beta ~1.02)."
        ),
    }

    return CalibrationData(firms=firms, sources=sources)
