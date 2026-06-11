"""Walkthrough Part 6: Calibration, Credit Risk, and Dario's Dilemma.

Section-by-section walkthrough of the paper's quantitative sections
(calibration, valuation, and the related appendix material), aimed at
the paper's own author reviewing the numbers. Target ~20-25 minutes.

Render: uv run python video/render.py walkthrough_part6 --quality l
Draft a single scene:
    cd video && uv run manim render -ql walkthrough_part6.py P6S01Title
"""

from __future__ import annotations

import numpy as np
from manim import (
    DOWN,
    LEFT,
    RIGHT,
    UP,
    Create,
    DashedLine,
    Dot,
    FadeIn,
    FadeOut,
    Indicate,
    Line,
    MathTex,
    Mobject,
    Polygon,
    Text,
    VGroup,
    Write,
)
from scene_base import PaperScene
from theme import (
    BASELINE,
    C_COST,
    C_DEFAULT,
    C_DEMAND,
    C_FAINT,
    C_H,
    C_INFER,
    C_L,
    C_OPTION,
    C_TEXT,
    C_TRAIN,
    clean_axes,
    highlight,
)

SCENES = [
    "P6S01Title",
    "P6S02Recap",
    "P6S03Calibration",
    "P6S04Archetypes",
    "P6S05ImpliedBeliefs",
    "P6S06Baseline",
    "P6S07LambdaTimeline",
    "P6S08ValueDecomposition",
    "P6S09CreditSpreads",
    "P6S10DefaultRisk",
    "P6S11DilemmaSetup",
    "P6S12DilemmaNumbers",
    "P6S13EquitySensitivity",
    "P6S14Robustness",
    "P6S15Predictions",
    "P6S16Close",
]


def grid_table(
    rows: list[list],
    col_x: list[float],
    row_h: float = 0.42,
    font_size: int = 22,
    left_cols: tuple[int, ...] = (),
) -> VGroup:
    """Lay out rows of cells on a fixed column grid.

    Each cell is a string (rendered as Text) or a ready-made Mobject.
    Returns a VGroup of row-VGroups so rows can be animated separately.
    """
    table = VGroup()
    for i, row in enumerate(rows):
        row_group = VGroup()
        for j, cell in enumerate(row):
            if cell is None:
                continue
            m = (
                cell
                if isinstance(cell, Mobject)
                else Text(str(cell), font_size=font_size)
            )
            target = RIGHT * col_x[j] + DOWN * (i * row_h)
            if j in left_cols:
                m.move_to(target, aligned_edge=LEFT)
            else:
                m.move_to(target)
            row_group.add(m)
        table.add(row_group)
    return table


def implied_lambda(phi: float) -> float:
    """Paper inversion: lambda = (phi/(1-phi))^(1-alpha) * (r - mu_H)."""
    p = BASELINE
    return (phi / (1.0 - phi)) ** (1.0 - p["alpha"]) * (p["r"] - p["mu_H"])


class P6S01Title(PaperScene):
    def construct(self):
        kicker = Text("DERIVATION WALKTHROUGH", font_size=24, color=C_FAINT)
        title = Text(
            "Part 6: Calibration, Credit Risk,",
            font_size=42,
            weight="BOLD",
        )
        title2 = Text("and Dario's Dilemma", font_size=42, weight="BOLD")
        group = VGroup(kicker, title, title2).arrange(DOWN, buff=0.35)
        with self.voiceover(
            "Welcome to part six, the last part of this walkthrough series."
            " The theory is done; today we put numbers on it."
        ):
            self.play(FadeIn(kicker), run_time=0.6)
            self.play(Write(title), Write(title2), run_time=1.8)

        sub = Text(
            "calibration  |  implied beliefs  |  credit risk  |  belief mismatch",
            font_size=24,
            color=C_FAINT,
        ).next_to(group, DOWN, buff=0.6)
        with self.voiceover(
            "We will walk through the calibration, the implied beliefs"
            " exercise, the credit risk numbers, and the quantitative"
            " anatomy of Dario's dilemma."
        ):
            self.play(FadeIn(sub), run_time=1.0)
        self.pause(0.6)
        self.play(FadeOut(group), FadeOut(sub), run_time=0.8)


class P6S02Recap(PaperScene):
    def construct(self):
        self.set_header("From theory to numbers", kicker="6.0  RECAP AND ROADMAP")

        items = VGroup(
            MathTex(
                r"X^* = \frac{\beta_H}{\beta_H - 1}\cdot"
                r"\frac{\delta K/r + cK^{\gamma}}{A_{\text{eff}}}",
                font_size=32,
                color=C_OPTION,
            ),
            MathTex(
                r"\left(\frac{\phi^*}{1-\phi^*}\right)^{1-\alpha}"
                r" = \frac{\lambda}{r-\mu_H}",
                font_size=32,
                color=C_TRAIN,
            ),
            MathTex(
                r"X_P:\ L(X_P)=F(X_P),\qquad \phi_L^*=\phi_F^*=\phi^*",
                font_size=32,
                color=C_H,
            ),
            MathTex(
                r"X_D = \frac{\beta^-}{\beta^- - 1}\cdot"
                r"\frac{c_D/r + \delta K/r}{A_{\text{eff}}}",
                font_size=32,
                color=C_DEFAULT,
            ),
        ).arrange(DOWN, buff=0.42, aligned_edge=LEFT)
        items.shift(DOWN * 0.5 + LEFT * 2.0)

        with self.voiceover(
            "A quick recap of where we stand. Parts two and three gave us"
            " the closed-form trigger and the allocation first-order"
            " condition that pins down phi star from beliefs alone."
        ):
            self.play(FadeIn(items[0], shift=RIGHT * 0.3), run_time=0.9)
            self.play(FadeIn(items[1], shift=RIGHT * 0.3), run_time=0.9)
        with self.voiceover(
            "Part four added the preemption trigger and the role-invariance"
            " of the training fraction; part five added the Leland default"
            " boundary and faith-based survival."
        ):
            self.play(FadeIn(items[2], shift=RIGHT * 0.3), run_time=0.9)
            self.play(FadeIn(items[3], shift=RIGHT * 0.3), run_time=0.9)
        self.pause(0.3)
        self.clear_body()

        steps = VGroup(
            Text("1. Calibrate the primitives", font_size=26),
            Text("2. Four firm archetypes and their training fractions", font_size=26),
            Text("3. Invert the FOC: implied AI-timeline beliefs", font_size=26),
            Text("4. Baseline magnitudes and what lambda means", font_size=26),
            Text("5. Value decomposition and credit risk", font_size=26),
            Text("6. Dario's dilemma, robustness, predictions", font_size=26),
        ).arrange(DOWN, buff=0.38, aligned_edge=LEFT)
        steps.shift(DOWN * 0.5 + LEFT * 1.5)
        with self.voiceover(
            "Today's plan: calibrate the primitives, build four firm"
            " archetypes, and invert the allocation condition to read"
            " beliefs out of observed training fractions."
        ):
            for s in steps[:3]:
                self.play(FadeIn(s, shift=RIGHT * 0.3), run_time=0.7)
        with self.voiceover(
            "Then the baseline magnitudes, the value decomposition and"
            " credit risk numbers, and finally the quantitative anatomy of"
            " Dario's dilemma, the robustness checks, and the testable"
            " predictions."
        ):
            for s in steps[3:]:
                self.play(FadeIn(s, shift=RIGHT * 0.3), run_time=0.7)
        self.pause(0.4)
        self.clear_body()


class P6S03Calibration(PaperScene):
    def construct(self):
        self.set_header("A stylized calibration", kicker="6.1  CALIBRATION")

        philosophy = VGroup(
            Text(
                "Goal: discipline magnitudes, not structural estimation.",
                font_size=27,
                color=C_TEXT,
            ),
            Text(
                "Caveat 1: Leland default fits public-debt issuers,",
                font_size=24,
                color=C_FAINT,
            ),
            Text(
                "  not VC-backed labs (qualitative predictions still apply).",
                font_size=24,
                color=C_FAINT,
            ),
            Text(
                "Caveat 2: training fractions phi-hat are uncertain, +/- 0.10.",
                font_size=24,
                color=C_FAINT,
            ),
        ).arrange(DOWN, buff=0.3, aligned_edge=LEFT)
        philosophy.shift(UP * 0.6 + LEFT * 0.8)

        with self.voiceover(
            "First, the philosophy. The calibration is deliberately"
            " stylized: it disciplines the model's quantitative magnitudes"
            " and illustrates cross-sectional heterogeneity, but it is not"
            " a structural estimation of firm-level primitives."
        ):
            self.play(FadeIn(philosophy[0]), run_time=1.0)
        with self.voiceover(
            "Two caveats up front. The Leland default framework fits"
            " public-debt issuers better than venture-backed labs, and the"
            " training fractions are inferred from incomplete data, with"
            " uncertainty of plus or minus zero point one zero."
        ):
            self.play(FadeIn(philosophy[1:]), run_time=1.2)
        self.pause(0.3)
        self.clear_body()

        def status(s: str) -> Text:
            color = {"Chosen": C_OPTION, "Inferred": C_H, "Standard": C_FAINT}[s]
            return Text(s, font_size=20, color=color)

        def sym(tex: str) -> MathTex:
            return MathTex(tex, font_size=30)

        rows = [
            [
                Text("Symbol", font_size=20, color=C_FAINT),
                Text("Value", font_size=20, color=C_FAINT),
                Text("Status", font_size=20, color=C_FAINT),
                Text("Anchor", font_size=20, color=C_FAINT),
            ],
            [sym(r"\mu_L"), "0.01", status("Chosen"), "cloud baseline growth"],
            [
                sym(r"\mu_H"),
                "0.06",
                status("Chosen"),
                "risk-adjusted AGI-regime growth",
            ],
            [sym(r"\sigma"), "0.25", status("Inferred"), "cloud revenue volatility"],
            [sym(r"r"), "0.12", status("Inferred"), "frontier-lab WACC"],
            [sym(r"\lambda"), "0.10", status("Chosen"), "10-year expected horizon"],
            [
                sym(r"\alpha"),
                "0.40",
                status("Inferred"),
                "scaling laws (near A2 bound 0.36)",
            ],
            [sym(r"\gamma"), "1.50", status("Chosen"), "power + supply bottlenecks"],
            [sym(r"\delta"), "0.03", status("Inferred"), "operating flow cost"],
            [sym(r"c_d"), "0.05", status("Inferred"), "cost of debt"],
            [sym(r"b"), "0.30", status("Standard"), "bankruptcy cost"],
        ]
        table = grid_table(
            rows,
            col_x=[-5.9, -4.6, -3.2, -1.7],
            row_h=0.44,
            font_size=21,
            left_cols=(3,),
        )
        table.move_to(DOWN * 0.55)

        with self.voiceover(
            "Here is the full parameter table, with each parameter tagged"
            " as inferred from observable proxies, chosen for discipline,"
            " or standard from the literature."
        ):
            self.play(FadeIn(table[0]), run_time=0.5)
            for row in table[1:]:
                self.play(FadeIn(row), run_time=0.22)

        box = highlight(VGroup(table[1], table[2]))
        with self.voiceover(
            "The drifts are mu L of one percent and mu H of six percent,"
            " and both are risk-adjusted, certainty-equivalent growth"
            " rates, not observed revenue growth."
        ):
            self.play(Create(box), run_time=0.8)
        with self.voiceover(
            "Observed cloud revenue growth of twenty-four to thirty-nine"
            " percent is consistent with mu H of only six percent once the"
            " large risk premium embedded in the discount rate is netted"
            " out, and convergence requires r greater than mu H, which"
            " bounds it from above. Since the risk adjustment cannot be"
            " measured directly, mu H is tagged as chosen, not inferred."
        ):
            self.play(Indicate(table[2], color=C_OPTION), run_time=1.2)

        with self.voiceover(
            "The discount rate of twelve percent is the WACC of a"
            " representative frontier lab. Damodaran's industry estimates"
            " run from seven point two percent for software to ten point"
            " eight for semiconductors, and CAPM with betas of one point"
            " five to two point five gives a cost of equity around ten and"
            " a half to fifteen percent."
        ):
            self.play(FadeOut(box), run_time=0.4)
            box = highlight(table[4])
            self.play(Create(box), run_time=0.8)

        with self.voiceover(
            "Lambda of zero point one means a ten-year expected horizon, a"
            " moderate marginal-investor prior. Amodei's statements map to"
            " roughly zero point three to zero point five; Hassabis to"
            " about zero point one to zero point one five."
        ):
            self.play(FadeOut(box), run_time=0.4)
            box = highlight(table[5])
            self.play(Create(box), run_time=0.8)

        with self.voiceover(
            "Alpha of zero point four is anchored on the concavity of the"
            " compute-to-loss scaling laws. One disclosure: the"
            " interior-capacity condition A two requires alpha above"
            " roughly zero point three six at baseline volatility, so zero"
            " point four sits fairly close to that bound."
        ):
            self.play(FadeOut(box), run_time=0.4)
            box = highlight(table[6])
            self.play(Create(box), run_time=0.8)
        with self.voiceover(
            "That proximity does not drive the results: the archetype"
            " analysis uses full numerical optimization that never invokes"
            " A two, and the sensitivity range for alpha spans both sides"
            " of the closed-form regime."
        ):
            self.play(Indicate(table[6], color=C_H), run_time=1.0)

        with self.voiceover(
            "Gamma of one point five captures convex installation costs"
            " from power and GPU supply bottlenecks. And delta of three"
            " percent is an operating flow cost, power, cooling, and"
            " maintenance, not depreciation: hardware capital cost lives"
            " in c K to the gamma."
        ):
            self.play(FadeOut(box), run_time=0.4)
            box = highlight(VGroup(table[7], table[8]))
            self.play(Create(box), run_time=0.8)
        with self.voiceover(
            "Technological obsolescence would justify a higher effective"
            " delta, so the baseline is conservative; and a higher delta"
            " would actually strengthen the dilemma asymmetry later on."
            " The coupon rate of five percent and bankruptcy cost of"
            " thirty percent close out the financial block."
        ):
            self.play(FadeOut(box), run_time=0.5)
        self.pause(0.4)
        self.clear_body()


class P6S04Archetypes(PaperScene):
    def construct(self):
        self.set_header("Four stylized archetypes", kicker="6.2  FIRM ARCHETYPES")

        def head(line1: str, line2: str) -> VGroup:
            return VGroup(
                Text(line1, font_size=20, weight="BOLD"),
                Text(line2, font_size=17, color=C_FAINT),
            ).arrange(DOWN, buff=0.08)

        phi_label = VGroup(
            Text("Training fraction ", font_size=21),
            MathTex(r"\hat{\phi}", font_size=28, color=C_TRAIN),
        ).arrange(RIGHT, buff=0.1)

        rows = [
            [
                None,
                head("Frontier Lab", "(Anthropic-like)"),
                head("Platform", "(OpenAI-like)"),
                head("Hyperscaler", "(Google-like)"),
                head("Compute Racer", "(xAI-like)"),
            ],
            [Text("Revenue 2025 ($B)", font_size=21), "4.5", "12.5", "60.0", "0.5"],
            [Text("CapEx 2025 ($B)", font_size=21), "3.0", "12.0", "91.0", "10.0"],
            [Text("CapEx / Revenue", font_size=21), "0.67", "0.96", "1.52", "20.0"],
            [Text("Leverage", font_size=21), "0.05", "0.05", "0.10", "0.15"],
            [Text("WACC", font_size=21), "0.15", "0.14", "0.10", "0.18"],
            [phi_label, "0.55", "0.60", "0.35", "0.75"],
        ]
        table = grid_table(
            rows,
            col_x=[-6.2, -1.9, 0.3, 2.4, 4.7],
            row_h=0.52,
            font_size=21,
            left_cols=(0,),
        )
        table.move_to(DOWN * 0.45)
        note = Text(
            "xAI figures are pre-SpaceX-acquisition (standalone lab, Q4 2025).",
            font_size=19,
            color=C_FAINT,
        ).to_edge(DOWN, buff=0.35)

        with self.voiceover(
            "The cross-section is summarized by four stylized archetypes:"
            " a frontier lab like Anthropic, a platform like OpenAI, a"
            " hyperscaler like Google, and a compute racer like x A I."
            " These are illustrative composites, not structural estimates."
        ):
            self.play(FadeIn(table[0]), run_time=1.0)
        with self.voiceover(
            "Revenue and capex come from filings, earnings guidance, and"
            " press reports. The ratios are the interesting part."
        ):
            self.play(FadeIn(table[1]), FadeIn(table[2]), run_time=1.0)

        with self.voiceover(
            "Capex to revenue runs from zero point six seven for the"
            " Anthropic-like lab, through roughly parity for the"
            " OpenAI-like platform, one point five for the hyperscaler,"
            " and a striking twenty times revenue for the compute racer,"
            " which builds massive training clusters before monetization."
        ):
            self.play(FadeIn(table[3]), run_time=0.8)
            self.play(Indicate(table[3][-1], color=C_COST), run_time=1.0)
        with self.voiceover(
            "Leverage is uniformly low, five to fifteen percent, and the"
            " WACCs range from ten percent for the hyperscaler to eighteen"
            " for the compute racer. Note the x A I figures predate the"
            " SpaceX acquisition; the archetype is the standalone lab."
        ):
            self.play(FadeIn(table[4]), FadeIn(table[5]), run_time=0.8)
            self.play(FadeIn(note), run_time=0.6)
        with self.voiceover(
            "And the key row: estimated training fractions of zero point"
            " five five, zero point six, zero point three five, and zero"
            " point seven five. A factor of two of cross-sectional"
            " variation, which is what the inversion exercise will exploit."
        ):
            self.play(FadeIn(table[6]), run_time=0.8)
            self.play(Indicate(table[6], color=C_TRAIN), run_time=1.0)
        self.pause(0.3)
        self.clear_body()

        src_title = Text(
            "Where do the phi-hats come from?", font_size=28, weight="BOLD"
        ).shift(UP * 1.9)
        sources = VGroup(
            Text(
                "1. Executive statements: Amodei models the long run at"
                ' "roughly 50/50".',
                font_size=23,
            ),
            Text(
                "2. Epoch AI, OpenAI 2024: ~$3B training, $2B research,"
                " $1.8B inference",
                font_size=23,
            ),
            Text("    -> combined R&D share ~71% of compute.", font_size=23),
            Text(
                "3. Deloitte trajectory: two-thirds training -> parity (2025)",
                font_size=23,
            ),
            Text("    -> two-thirds inference (2026).", font_size=23),
        ).arrange(DOWN, buff=0.32, aligned_edge=LEFT)
        sources.next_to(src_title, DOWN, buff=0.5).shift(LEFT * 0.4)

        with self.voiceover(
            "The training fractions are triangulated from three kinds of"
            " evidence. First, executive statements: Amodei has modeled"
            " the long-run equilibrium at roughly fifty fifty."
        ):
            self.play(FadeIn(src_title), run_time=0.6)
            self.play(FadeIn(sources[0]), run_time=0.8)
        with self.voiceover(
            "Second, the only firm-level decomposition with primary"
            " documentation: Epoch AI's analysis of OpenAI's twenty"
            " twenty-four compute. Roughly three billion on training, two"
            " billion on research and experimentation, and one point eight"
            " billion on inference, so combined R and D was about"
            " seventy-one percent. The model's phi-hat subsumes both"
            " training and research."
        ):
            self.play(FadeIn(sources[1]), FadeIn(sources[2]), run_time=1.0)
        with self.voiceover(
            "Third, the industry trajectory from Deloitte: roughly"
            " two-thirds training, shifting to parity in twenty"
            " twenty-five, and projected to reach two-thirds inference in"
            " twenty twenty-six."
        ):
            self.play(FadeIn(sources[3]), FadeIn(sources[4]), run_time=1.0)
        self.pause(0.4)
        self.clear_body()


class P6S05ImpliedBeliefs(PaperScene):
    def construct(self):
        self.set_header(
            "Reading beliefs from allocations", kicker="6.3  IMPLIED BELIEFS"
        )

        foc = MathTex(
            r"\left(\frac{\phi^*}{1-\phi^*}\right)^{1-\alpha}"
            r" = \frac{\lambda}{r-\mu_H}",
            font_size=36,
        ).shift(UP * 1.7)
        inv = MathTex(
            r"\lambda \;=\;"
            r" \left(\frac{\hat{\phi}}{1-\hat{\phi}}\right)^{1-\alpha}(r-\mu_H)",
            font_size=38,
            color=C_DEMAND,
        ).next_to(foc, DOWN, buff=0.55)

        with self.voiceover(
            "Now the inversion. The part three first-order condition links"
            " the training odds ratio to lambda over r minus mu H."
        ):
            self.play(Write(foc), run_time=1.2)
        with self.voiceover(
            "Solving for lambda: an observed training fraction phi-hat"
            " implies an arrival rate equal to the odds ratio raised to"
            " one minus alpha, times r minus mu H. Each archetype's"
            " allocation becomes a statement about its AI timeline."
        ):
            self.play(Write(inv), run_time=1.4)
        self.pause(0.3)

        d1 = MathTex(
            r"(1-\alpha)\,[\ln\phi^* - \ln(1-\phi^*)] = \ln\lambda - \ln(r-\mu_H)",
            font_size=32,
        ).shift(DOWN * 0.8)
        d2 = MathTex(
            r"(1-\alpha)\left[\frac{1}{\phi^*}+\frac{1}{1-\phi^*}\right]"
            r"\frac{d\phi^*}{d\ln\lambda} = 1",
            font_size=32,
        ).next_to(d1, DOWN, buff=0.35)
        d3 = MathTex(
            r"\varepsilon_{\phi^*\!,\lambda}"
            r" = \frac{d\ln\phi^*}{d\ln\lambda}"
            r" = \frac{1-\phi^*}{1-\alpha}"
            r" \approx \frac{0.30}{0.60} = 0.5",
            font_size=34,
            color=C_TRAIN,
        ).next_to(d2, DOWN, buff=0.35)

        with self.voiceover(
            "How sensitive is the map? Take logs of the first-order"
            " condition: one minus alpha times log odds equals log lambda"
            " minus log of r minus mu H."
        ):
            self.play(Write(d1), run_time=1.2)
        with self.voiceover(
            "Differentiate with respect to log lambda. The derivative of"
            " the log odds is one over phi plus one over one minus phi,"
            " times d phi."
        ):
            self.play(Write(d2), run_time=1.2)
        with self.voiceover(
            "Multiplying through by phi star gives the elasticity of phi"
            " star with respect to lambda: one minus phi star, over one"
            " minus alpha. At the baseline, zero point three over zero"
            " point six, which is one half."
        ):
            self.play(Write(d3), run_time=1.4)
        with self.voiceover(
            "A moderate elasticity of one half means phi star moves slowly"
            " in lambda. But that makes the inverse map steep: a plus or"
            " minus zero point one error in phi-hat spans roughly a factor"
            " of two in the implied lambda."
        ):
            self.play(Indicate(d3, color=C_TRAIN), run_time=1.2)
        self.pause(0.3)
        self.clear_body()

        ax = clean_axes(x_range=[0, 0.37], y_range=[0, 5], width=8.6, height=3.3)
        ax.shift(UP * 0.15 + RIGHT * 1.6)
        x_lab = MathTex(r"\lambda", font_size=30, color=C_DEMAND).next_to(
            ax.x_axis, RIGHT, buff=0.15
        )
        ticks = VGroup()
        for v in [0.0, 0.1, 0.2, 0.3]:
            t = Text(f"{v:.1f}", font_size=18, color=C_FAINT)
            t.next_to(ax.coords_to_point(v, 0), DOWN, buff=0.18)
            ticks.add(t)

        firms = [
            ("Google-like (0.35)", 0.35, 1.0, C_INFER),
            ("Anthropic-like (0.55)", 0.55, 2.0, C_H),
            ("OpenAI-like (0.60)", 0.60, 3.0, C_TEXT),
            ("xAI-like (0.75)", 0.75, 4.0, C_TRAIN),
        ]
        bands = VGroup()
        labels = VGroup()
        for name, phi_hat, y, color in firms:
            lo = implied_lambda(phi_hat - 0.10)
            hi = implied_lambda(phi_hat + 0.10)
            band = Line(
                ax.coords_to_point(lo, y),
                ax.coords_to_point(hi, y),
                color=color,
                stroke_width=9,
            )
            lab = Text(name, font_size=20, color=color)
            lab.next_to(ax.coords_to_point(0, y), LEFT, buff=0.25)
            bands.add(band)
            labels.add(lab)

        base = DashedLine(
            ax.coords_to_point(0.10, 0),
            ax.coords_to_point(0.10, 4.6),
            color=C_FAINT,
        )
        base_lab = Text("baseline 0.10", font_size=18, color=C_FAINT).next_to(
            base, UP, buff=0.1
        )

        with self.voiceover(
            "Here are the implied arrival-rate bands, at the common"
            " baseline discount rate of twelve percent, with phi-hat"
            " varied by plus or minus zero point one."
        ):
            self.play(Create(ax), FadeIn(x_lab), FadeIn(ticks), run_time=0.9)
            self.play(Create(base), FadeIn(base_lab), run_time=0.7)
        with self.voiceover(
            "The Google-like hyperscaler implies lambda between zero point"
            " zero three and zero point zero five, expected horizons of"
            " roughly nineteen to thirty-two years."
        ):
            self.play(Create(bands[0]), FadeIn(labels[0]), run_time=1.0)
        with self.voiceover(
            "The Anthropic-like and OpenAI-like archetypes sit in the"
            " middle, straddling the baseline belief."
        ):
            self.play(
                Create(bands[1]),
                FadeIn(labels[1]),
                Create(bands[2]),
                FadeIn(labels[2]),
                run_time=1.2,
            )
        with self.voiceover(
            "And the x A I-like racer implies lambda between zero point"
            " zero nine and zero point one seven, an expected horizon of"
            " six to eleven years."
        ):
            self.play(Create(bands[3]), FadeIn(labels[3]), run_time=1.0)

        quals = VGroup(
            Text(
                "Qual. 1: at archetype WACCs the dispersion widens",
                font_size=21,
                color=C_FAINT,
            ),
            Text(
                "  (xAI at r=0.18: [0.17, 0.34];  Google at r=0.10: [0.02, 0.04])",
                font_size=21,
                color=C_FAINT,
            ),
            Text(
                "Qual. 2: ordering robust to common shifts; adjacent bands overlap",
                font_size=21,
                color=C_FAINT,
            ),
        ).arrange(DOWN, buff=0.22, aligned_edge=LEFT)
        quals.to_edge(DOWN, buff=0.25).shift(LEFT * 0.6)

        with self.voiceover(
            "Two qualifications. First, the inversion holds r at the"
            " common baseline; because implied lambda scales with r minus"
            " mu H, using each archetype's own WACC shifts the levels."
            " The x A I-like firm at eighteen percent implies zero point"
            " one seven to zero point three four, while the Google-like"
            " firm at ten percent implies zero point zero two to zero"
            " point zero four, so the cross-sectional dispersion widens"
            " rather than narrows."
        ):
            self.play(FadeIn(quals[0]), FadeIn(quals[1]), run_time=1.2)
        with self.voiceover(
            "Second, the ordering is robust to common shifts of all the"
            " phi-hats, but the bands of adjacent archetypes overlap, so"
            " independent errors could reorder neighbors, though not the"
            " endpoints."
        ):
            self.play(FadeIn(quals[2]), run_time=1.0)
        self.pause(0.4)
        self.clear_body()


class P6S06Baseline(PaperScene):
    def construct(self):
        self.set_header("Baseline magnitudes", kicker="6.4  BASELINE RESULTS")

        single = VGroup(
            Text("Single firm (= unconstrained leader)", font_size=24, color=C_OPTION),
            MathTex(
                r"X^* \approx 0.0047,\quad K^* \approx 0.0067,"
                r"\quad \phi^* \approx 0.70",
                font_size=34,
            ),
        ).arrange(DOWN, buff=0.3, aligned_edge=LEFT)
        duo = VGroup(
            Text("Duopoly (zero leverage)", font_size=24, color=C_H),
            MathTex(
                r"X_P \approx 0.0027\ (\text{43\% below } X^*),\quad"
                r" X_F \approx 0.12,\quad K_F \approx 0.26",
                font_size=34,
            ),
        ).arrange(DOWN, buff=0.3, aligned_edge=LEFT)
        block = VGroup(single, duo).arrange(DOWN, buff=0.6, aligned_edge=LEFT)
        block.shift(UP * 0.7 + LEFT * 0.4)

        with self.voiceover(
            "Under the baseline calibration, the single firm invests at a"
            " trigger of about zero point zero zero four seven, installs"
            " capacity of about zero point zero zero six seven, and"
            " allocates seventy percent of it to training."
        ):
            self.play(FadeIn(single), run_time=1.2)
        with self.voiceover(
            "In the duopoly, preemption pulls the leader's trigger down to"
            " about zero point zero zero two seven, a forty-three percent"
            " discount to the monopoly benchmark, while the follower waits"
            " for demand around zero point one two and installs a much"
            " larger zero point two six."
        ):
            self.play(FadeIn(duo), run_time=1.2)
        with self.voiceover(
            "The follower's scale looks dramatic, but it follows from two"
            " reinforcing forces: its contest share rises with its own"
            " capacity, raising the effective revenue elasticity above"
            " alpha, and it enters at demand roughly forty-four times the"
            " preemption trigger, where the larger commitment pays."
        ):
            self.play(Indicate(duo[1], color=C_H), run_time=1.2)

        norm = VGroup(
            Text(
                "Normalization c = 1: levels of X and K are unit-free.",
                font_size=24,
                color=C_TEXT,
            ),
            Text(
                "Only ratios and percentages carry economic content.",
                font_size=24,
                color=C_COST,
            ),
        ).arrange(DOWN, buff=0.25, aligned_edge=LEFT)
        norm.next_to(block, DOWN, buff=0.6).align_to(block, LEFT)

        with self.voiceover(
            "A crucial reading instruction: the model is normalized by the"
            " unit cost c equals one, so the absolute levels of X and K"
            " are not interpretable. The quantitative content lives in"
            " ratios and percentages, like the preemption discount, the"
            " training fraction, and the value-loss asymmetry."
        ):
            self.play(FadeIn(norm), run_time=1.2)

        mapping = (
            MathTex(
                r"c \approx \$23\text{B}:\quad"
                r" I(K_F) = K_F^{1.5} \approx 0.13"
                r" \;\Rightarrow\; \approx \$3\text{B}",
                font_size=32,
                color=C_FAINT,
            )
            .next_to(norm, DOWN, buff=0.5)
            .align_to(norm, LEFT)
        )
        with self.voiceover(
            "To map back to dollars you pick c. For example, setting c to"
            " about twenty-three billion dollars makes the follower's"
            " investment cost of zero point one three model units equal"
            " roughly three billion dollars, the Anthropic-like"
            " archetype's annual capex. No ratio or spread in the paper"
            " changes under this rescaling."
        ):
            self.play(Write(mapping), run_time=1.2)
        self.pause(0.4)
        self.clear_body()


class P6S07LambdaTimeline(PaperScene):
    def construct(self):
        self.set_header("What a lambda means", kicker="6.5  INTERPRETING LAMBDA")

        lam = np.linspace(0.05, 1.0, 120)
        et = 1.0 / lam
        lam2 = np.linspace(0.0, 1.0, 120)
        p5 = 1.0 - np.exp(-5.0 * lam2)

        ax1 = clean_axes(x_range=[0, 1.05], y_range=[0, 21], width=5.4, height=3.6)
        ax1.shift(LEFT * 3.4 + DOWN * 0.7)
        ax2 = clean_axes(x_range=[0, 1.05], y_range=[0, 1.05], width=5.4, height=3.6)
        ax2.shift(RIGHT * 3.5 + DOWN * 0.7)
        t1 = MathTex(r"E[T] = 1/\lambda", font_size=30, color=C_DEMAND).next_to(
            ax1, UP, buff=0.2
        )
        t2 = MathTex(
            r"P(\text{switch} \le 5\text{y}) = 1 - e^{-5\lambda}",
            font_size=30,
            color=C_H,
        ).next_to(ax2, UP, buff=0.2)
        xl1 = MathTex(r"\lambda", font_size=26, color=C_FAINT).next_to(
            ax1.x_axis, RIGHT, buff=0.1
        )
        xl2 = MathTex(r"\lambda", font_size=26, color=C_FAINT).next_to(
            ax2.x_axis, RIGHT, buff=0.1
        )

        c1 = ax1.plot_line_graph(lam, et, line_color=C_DEMAND, add_vertex_dots=False)
        c2 = ax2.plot_line_graph(lam2, p5, line_color=C_H, add_vertex_dots=False)

        with self.voiceover(
            "Before the heavier results, a feel for what lambda means."
            " The expected time to the regime switch is one over lambda,"
            " and the probability of a switch within a five-year planning"
            " horizon is one minus e to the minus five lambda. Both are"
            " simple closed forms."
        ):
            self.play(Create(ax1), Create(ax2), FadeIn(t1), FadeIn(t2), run_time=1.2)
            self.play(FadeIn(xl1), FadeIn(xl2), run_time=0.4)
            self.play(Create(c1), Create(c2), run_time=1.8)

        band1 = Polygon(
            ax1.coords_to_point(0.05, 0),
            ax1.coords_to_point(0.50, 0),
            ax1.coords_to_point(0.50, 20),
            ax1.coords_to_point(0.05, 20),
            stroke_width=0,
            fill_color=C_OPTION,
            fill_opacity=0.13,
        )
        band2 = Polygon(
            ax2.coords_to_point(0.05, 0),
            ax2.coords_to_point(0.50, 0),
            ax2.coords_to_point(0.50, 1.0),
            ax2.coords_to_point(0.05, 1.0),
            stroke_width=0,
            fill_color=C_OPTION,
            fill_opacity=0.13,
        )
        d1 = Dot(
            ax2.coords_to_point(0.10, 1 - np.exp(-0.5)), color=C_DEMAND, radius=0.07
        )
        d2 = Dot(ax2.coords_to_point(0.50, 1 - np.exp(-2.5)), color=C_COST, radius=0.07)
        n1 = Text("0.10 -> 39%", font_size=21, color=C_DEMAND).next_to(
            d1, DOWN + RIGHT, buff=0.12
        )
        n2 = Text("0.50 -> 92%", font_size=21, color=C_COST).next_to(
            d2, DOWN + RIGHT, buff=0.12
        )

        with self.voiceover(
            "At the baseline of zero point one, a switch within five years"
            " has thirty-nine percent probability; at zero point five it"
            " is ninety-two percent."
        ):
            self.play(FadeIn(d1), FadeIn(n1), run_time=0.8)
            self.play(FadeIn(d2), FadeIn(n2), run_time=0.8)
        with self.voiceover(
            "The disagreement range among market participants, lambda from"
            " zero point zero five to zero point five, sits exactly on the"
            " steep part of both curves. That is why small differences in"
            " beliefs translate into large differences in investment"
            " behavior."
        ):
            self.play(FadeIn(band1), FadeIn(band2), run_time=1.0)
        self.pause(0.4)
        self.clear_body()


class P6S08ValueDecomposition(PaperScene):
    def construct(self):
        self.set_header("Where the value sits", kicker="6.6  VALUE DECOMPOSITION")

        aip = MathTex(
            r"V_{\text{AIP}} = A_{\text{eff}}(\phi, K_{\text{inst}})\,X"
            r" - \frac{\delta K_{\text{inst}}}{r}",
            font_size=34,
        ).shift(UP * 1.6)
        gap = MathTex(
            r"V_{\text{gap}} = \max\{\text{NPV}(K^*, \phi^*) - V_{\text{AIP}},\, 0\}",
            font_size=34,
            color=C_OPTION,
        ).next_to(aip, DOWN, buff=0.45)

        with self.voiceover(
            "Motivated by Berk, Green, and Naik, the paper decomposes firm"
            " value. Assets in place are the installed capacity valued"
            " through A effective, net of the operating cost perpetuity."
        ):
            self.play(Write(aip), run_time=1.3)
        with self.voiceover(
            "The capacity-gap value is the shortfall of assets in place"
            " relative to the net value of the optimally sized greenfield"
            " project, floored at zero."
        ):
            self.play(Write(gap), run_time=1.3)
        with self.voiceover(
            "Read this as comparative statics, distance to optimal scale,"
            " not as the NPV of incremental expansion. And because the"
            " benchmark nets out the entire investment cost while assets"
            " in place are gross of sunk costs, the gap hits zero before"
            " installed capacity reaches K star."
        ):
            self.play(Indicate(gap, color=C_OPTION), run_time=1.2)
        self.pause(0.3)
        self.clear_body()

        from ai_lab_investment.models.parameters import ModelParameters
        from ai_lab_investment.models.valuation import ValuationAnalysis

        va = ValuationAnalysis(ModelParameters())
        fracs = np.linspace(0.02, 1.1, 25)
        dec = va.capacity_gap_decomposition(fracs)

        ax = clean_axes(x_range=[0, 1.15], y_range=[0, 85], width=8.6, height=4.2)
        ax.shift(DOWN * 0.9 + RIGHT * 0.6)
        xl = MathTex(r"K_{\text{inst}}/K^*", font_size=28, color=C_FAINT).next_to(
            ax.x_axis, RIGHT, buff=0.15
        )
        yl = Text("gap share of value (%)", font_size=20, color=C_FAINT).next_to(
            ax.y_axis, UP, buff=0.15
        )
        curve = ax.plot_line_graph(
            dec["K_fracs"],
            dec["gap_fraction"],
            line_color=C_OPTION,
            add_vertex_dots=False,
        )
        band = Polygon(
            ax.coords_to_point(0.1, 0),
            ax.coords_to_point(0.3, 0),
            ax.coords_to_point(0.3, 80),
            ax.coords_to_point(0.1, 80),
            stroke_width=0,
            fill_color=C_H,
            fill_opacity=0.15,
        )
        band_lab = Text("typical lab: 30-60% of value", font_size=21, color=C_H)
        band_lab.move_to(ax.coords_to_point(0.62, 62))

        with self.voiceover(
            "Computing the gap fraction from the model, at the optimal phi"
            " star and demand at one and a half times the trigger: the"
            " share of value in the gap starts near eighty percent for a"
            " tiny installed base and declines as capacity approaches the"
            " optimum."
        ):
            self.play(Create(ax), FadeIn(xl), FadeIn(yl), run_time=0.9)
            self.play(Create(curve), run_time=1.8)
        with self.voiceover(
            "A typical frontier lab, with installed capacity at ten to"
            " thirty percent of the model's optimum, carries thirty to"
            " sixty percent of its value in the capacity gap."
        ):
            self.play(FadeIn(band), FadeIn(band_lab), run_time=1.0)
        with self.voiceover(
            "Notice the curve reaches zero before K over K star equals"
            " one, exactly because the benchmark is net of the full"
            " investment cost."
        ):
            self.play(Indicate(curve, color=C_OPTION, scale_factor=1.02), run_time=1.0)

        imp = Text(
            "Asset-pricing read: these equities should behave like growth stocks.",
            font_size=23,
            color=C_TEXT,
        ).to_edge(DOWN, buff=0.35)
        with self.voiceover(
            "The asset-pricing implication: frontier lab equities should"
            " behave like growth stocks, high beta, high volatility, high"
            " discount-rate sensitivity, because most of their value is"
            " distance to scale, not current operations."
        ):
            self.play(FadeIn(imp), run_time=1.0)
        self.pause(0.4)
        self.clear_body()


class P6S09CreditSpreads(PaperScene):
    def construct(self):
        self.set_header("Credit spreads", kicker="6.7  CREDIT RISK")

        spread_eq = MathTex(
            r"\text{spread} = \frac{\text{coupon}}{D(X)} - r",
            font_size=38,
            color=C_DEFAULT,
        ).shift(UP * 1.7)
        with self.voiceover(
            "On to credit risk. The spread is the coupon over the market"
            " value of debt, minus r."
        ):
            self.play(Write(spread_eq), run_time=1.2)
        with self.voiceover(
            "Why is r the benchmark? The model has a single discount rate:"
            " a default-free perpetuity with coupon c D is worth c D over"
            " r and yields exactly r. So the spread is zero absent default"
            " risk, and isolates the default-risk component, not term"
            " premia or risk premia."
        ):
            self.play(Indicate(spread_eq, color=C_DEFAULT), run_time=1.2)

        channels = VGroup(
            Text(
                "phi raises A_eff -> lower X_D -> lower default probability",
                font_size=23,
                color=C_H,
            ),
            Text(
                "phi shrinks the inference business -> higher loss given default",
                font_size=23,
                color=C_COST,
            ),
            Text(
                "At baseline the LGD channel mildly dominates:"
                " spreads mildly increase in phi.",
                font_size=23,
                color=C_TEXT,
            ),
        ).arrange(DOWN, buff=0.3, aligned_edge=LEFT)
        channels.next_to(spread_eq, DOWN, buff=0.55)

        with self.voiceover(
            "The training fraction enters through two opposing channels."
            " Faith-based survival: higher phi raises A effective, lowers"
            " the default boundary, and cuts the probability of default."
        ):
            self.play(FadeIn(channels[0]), run_time=0.9)
        with self.voiceover(
            "But higher phi also shrinks the inference business that"
            " creditors can liquidate, raising the loss given default."
            " The continuation value that keeps the firm alive is"
            " destroyed in bankruptcy."
        ):
            self.play(FadeIn(channels[1]), run_time=0.9)
        with self.voiceover(
            "At the baseline calibration the loss-given-default channel"
            " mildly dominates, so spreads mildly increase in phi even as"
            " default probabilities fall."
        ):
            self.play(FadeIn(channels[2]), run_time=0.9)
        self.pause(0.3)
        self.clear_body()

        from ai_lab_investment.models.parameters import ModelParameters
        from ai_lab_investment.models.valuation import ValuationAnalysis

        va = ValuationAnalysis(ModelParameters())
        levs = np.linspace(0.02, 0.72, 15)
        spreads = np.array([va.credit_spread(le) * 1e4 for le in levs])
        marks = [(0.05, 0), (0.20, 12), (0.40, 41), (0.70, 97)]

        ax = clean_axes(x_range=[0, 0.75], y_range=[0, 105], width=8.6, height=4.2)
        ax.shift(DOWN * 0.9 + RIGHT * 0.6)
        xl = Text("leverage", font_size=20, color=C_FAINT).next_to(
            ax.x_axis, RIGHT, buff=0.15
        )
        yl = Text("spread (bps)", font_size=20, color=C_FAINT).next_to(
            ax.y_axis, UP, buff=0.15
        )
        curve = ax.plot_line_graph(
            levs, spreads, line_color=C_DEFAULT, add_vertex_dots=False
        )

        with self.voiceover(
            "Here is the model's spread curve, evaluated at a fixed demand"
            " level of zero point one, capacity one, and a training"
            " fraction of one half."
        ):
            self.play(Create(ax), FadeIn(xl), FadeIn(yl), run_time=0.9)
            self.play(Create(curve), run_time=1.6)

        zero_note = VGroup(
            Text("over-collateralized:", font_size=20, color=C_FAINT),
            Text("spread = 0 until ~0.13", font_size=20, color=C_FAINT),
        ).arrange(DOWN, buff=0.12, aligned_edge=LEFT)
        zero_note.move_to(ax.coords_to_point(0.27, 72))
        zline = DashedLine(
            ax.coords_to_point(0.13, 0),
            ax.coords_to_point(0.13, 50),
            color=C_FAINT,
        )
        with self.voiceover(
            "At low leverage the spread is exactly zero: the small coupon"
            " claim is over-collateralized by the liquidation value of the"
            " inference business, even though the equity holders' default"
            " boundary is positive. The spread turns positive only once"
            " the claim outgrows that collateral, around leverage of zero"
            " point one three."
        ):
            self.play(Create(zline), FadeIn(zero_note), run_time=1.0)

        dots = VGroup()
        notes = VGroup()
        for lv, bps in marks:
            d = Dot(ax.coords_to_point(lv, bps), color=C_OPTION, radius=0.06)
            n = Text(f"{bps}", font_size=20, color=C_OPTION).next_to(
                d, UP + LEFT, buff=0.08
            )
            dots.add(d)
            notes.add(n)
        with self.voiceover(
            "The numbers: roughly zero basis points at five percent"
            " leverage, twelve at twenty percent, forty-one at forty"
            " percent, and ninety-seven at seventy percent leverage."
            " Moderate spreads, even at high leverage."
        ):
            self.play(FadeIn(dots), FadeIn(notes), run_time=1.2)
        self.pause(0.4)
        self.clear_body()


class P6S10DefaultRisk(PaperScene):
    def construct(self):
        self.set_header("Default probability", kicker="6.7  CREDIT RISK")

        formula = MathTex(
            r"P(\text{default} \le T) = \Phi(-d_1)"
            r" + \left(\frac{X_D}{X}\right)^{2\nu/\sigma^2}\Phi(-d_2)",
            font_size=36,
        ).shift(UP * 1.8)
        defs = MathTex(
            r"\nu = \mu_L - \tfrac{\sigma^2}{2},\qquad"
            r" d_{1,2} = \frac{\ln(X/X_D) \pm \nu T}{\sigma\sqrt{T}}",
            font_size=30,
            color=C_FAINT,
        ).next_to(formula, DOWN, buff=0.4)

        with self.voiceover(
            "Default probability is the first-passage probability that"
            " geometric Brownian motion hits the barrier X D within the"
            " horizon, under the L-regime drift, since the boundary is an"
            " L-regime object."
        ):
            self.play(Write(formula), run_time=1.5)
            self.play(FadeIn(defs), run_time=0.8)
        with self.voiceover(
            "Each piece has a meaning. Phi of minus d one is the"
            " probability that log demand simply ends the horizon below"
            " the barrier, the direct drift-and-diffusion paths."
        ):
            self.play(Indicate(formula[0][:14], color=C_L), run_time=1.2)
        with self.voiceover(
            "The second term counts paths that dip below the barrier and"
            " come back: by the reflection argument, each is weighted by"
            " the barrier-to-demand ratio raised to two nu over sigma"
            " squared, with nu the log drift mu L minus half sigma squared."
        ):
            self.play(Indicate(formula[0][14:], color=C_DEFAULT), run_time=1.2)

        caveats = VGroup(
            Text(
                "Upper bound: ignores the rescuing switch to H before hitting X_D.",
                font_size=22,
                color=C_FAINT,
            ),
            Text(
                "Risk-neutral: mu_L is risk-adjusted; physical default"
                " probability is lower.",
                font_size=22,
                color=C_FAINT,
            ),
        ).arrange(DOWN, buff=0.25, aligned_edge=LEFT)
        caveats.next_to(defs, DOWN, buff=0.5)
        with self.voiceover(
            "Two caveats. The calculation ignores the regime switch"
            " itself, and a switch to H would effectively remove default"
            " risk, so these are upper bounds on the pre-switch hazard."
            " And since mu L is the risk-adjusted drift, this is a"
            " risk-neutral probability, consistent with the spreads;"
            " physical probabilities would be lower."
        ):
            self.play(FadeIn(caveats), run_time=1.0)
        self.pause(0.3)
        self.clear_body()

        from ai_lab_investment.models.parameters import ModelParameters
        from ai_lab_investment.models.valuation import ValuationAnalysis

        va = ValuationAnalysis(ModelParameters())
        levs = np.linspace(0.02, 0.72, 15)
        probs = np.array([va.default_probability(0.10, 1.0, le) * 100 for le in levs])
        marks = [(0.05, 0.63), (0.20, 1.80), (0.40, 4.85), (0.70, 12.98)]

        ax = clean_axes(x_range=[0, 0.75], y_range=[0, 15], width=8.6, height=4.2)
        ax.shift(DOWN * 0.9 + RIGHT * 0.6)
        xl = Text("leverage", font_size=20, color=C_FAINT).next_to(
            ax.x_axis, RIGHT, buff=0.15
        )
        yl = Text("5-year default prob. (%)", font_size=20, color=C_FAINT).next_to(
            ax.y_axis, UP, buff=0.15
        )
        curve = ax.plot_line_graph(
            levs, probs, line_color=C_DEFAULT, add_vertex_dots=False
        )
        with self.voiceover(
            "Plotting the five-year default probability against leverage,"
            " at the same evaluation point: demand zero point one,"
            " capacity one, phi one half."
        ):
            self.play(Create(ax), FadeIn(xl), FadeIn(yl), run_time=0.9)
            self.play(Create(curve), run_time=1.6)

        dots = VGroup()
        notes = VGroup()
        for lv, pr in marks:
            d = Dot(ax.coords_to_point(lv, pr), color=C_OPTION, radius=0.06)
            n = Text(f"{pr:.2f}%", font_size=20, color=C_OPTION).next_to(
                d, UP + LEFT, buff=0.08
            )
            dots.add(d)
            notes.add(n)
        with self.voiceover(
            "Zero point six three percent at five percent leverage, one"
            " point eight at twenty, four point eight five at forty, and"
            " twelve point nine eight percent at seventy percent leverage."
            " Default is far from rare at high leverage."
        ):
            self.play(FadeIn(dots), FadeIn(notes), run_time=1.2)

        punch = Text(
            "Creditors: high-probability, modest-severity."
            "  Shareholders bear the catastrophe.",
            font_size=23,
            color=C_TEXT,
        ).to_edge(DOWN, buff=0.35)
        with self.voiceover(
            "Contrast the two panels: default probabilities are double"
            " digits while spreads stay under a hundred basis points,"
            " because creditor losses are bounded by the inference"
            " collateral. For creditors, an AI lab is a high-probability,"
            " modest-severity credit; the catastrophic component, the"
            " destruction of the faith-based continuation value, is borne"
            " by shareholders."
        ):
            self.play(FadeIn(punch), run_time=1.0)
        self.pause(0.4)
        self.clear_body()


class P6S11DilemmaSetup(PaperScene):
    def construct(self):
        self.set_header("The cost of wrong beliefs", kicker="6.8  DARIO'S DILEMMA")

        setup = MathTex(
            r"\lambda_{\text{true}} \neq \lambda_{\text{invest}}:"
            r"\quad \text{policy } \bigl(X^*(\lambda_{\text{inv}}),\,"
            r" K^*(\lambda_{\text{inv}}),\, \phi^*(\lambda_{\text{inv}})\bigr)",
            font_size=32,
        ).shift(UP * 1.9)
        sources = Text(
            "mismatch sources: agency frictions, strategic signaling,"
            " bounded rationality",
            font_size=21,
            color=C_FAINT,
        ).next_to(setup, DOWN, buff=0.3)

        with self.voiceover(
            "Now the centerpiece. A firm whose true belief is lambda true"
            " invests according to a different lambda: its trigger,"
            " capacity, and training fraction all come from the mistaken"
            " belief. The mismatch can come from agency frictions,"
            " strategic signaling, or bounded rationality."
        ):
            self.play(Write(setup), run_time=1.4)
            self.play(FadeIn(sources), run_time=0.7)

        dv = MathTex(
            r"\Delta V = \text{NPV}(\lambda_{\text{true}}, \lambda_{\text{true}})"
            r" - \text{NPV}(\lambda_{\text{true}}, \lambda_{\text{invest}}),"
            r"\quad \text{timing factor } (X_0/X^*)^{\beta_H}",
            font_size=30,
            color=C_COST,
        ).next_to(sources, DOWN, buff=0.5)
        with self.voiceover(
            "The value loss is the gap between the NPV of the correct"
            " policy and the NPV of the mismatched policy, both evaluated"
            " under the true demand process from a common starting demand"
            " X zero. The factor X zero over X star to the beta H adjusts"
            " for the different waiting times to the two triggers."
        ):
            self.play(Write(dv), run_time=1.5)
        self.pause(0.3)

        taylor = MathTex(
            r"W'(\lambda_{\text{true}}) = 0"
            r" \;\Rightarrow\; \Delta V \approx"
            r" -\tfrac{1}{2}W''\,(\Delta\lambda)^2"
            r" \;-\; \tfrac{1}{6}W'''\,(\Delta\lambda)^3,"
            r"\qquad W''' > 0",
            font_size=32,
        ).next_to(dv, DOWN, buff=0.55)
        with self.voiceover(
            "Why is the loss asymmetric at all? Define W as the value of"
            " investing under a given belief, with outcomes under the"
            " truth. By construction W is maximized at the truth, so its"
            " first derivative there is zero, and the second-order loss is"
            " symmetric."
        ):
            self.play(Write(taylor), run_time=1.5)
        with self.voiceover(
            "The asymmetry comes from the odd-order terms, principally a"
            " positive third derivative: with W triple prime positive,"
            " pessimistic mismatches lose more than optimistic ones of the"
            " same size."
        ):
            self.play(Indicate(taylor, color=C_COST), run_time=1.2)
        self.pause(0.3)
        self.clear_body()

        ch = VGroup(
            Text(
                "Capacity channel: ZERO asymmetry (K* independent of lambda, Prop. 1)",
                font_size=23,
                color=C_FAINT,
            ),
            Text(
                "Timing channel: (X0/X*)^beta approximately symmetric",
                font_size=23,
                color=C_FAINT,
            ),
            Text(
                "Training allocation channel: DOMINANT",
                font_size=25,
                color=C_TRAIN,
            ),
            Text(
                "  - H-term is ~70% of A_eff at baseline:"
                " under-training kills the main value source",
                font_size=22,
            ),
            Text(
                "  - phi*(lambda) is concave (elasticity < 1, decreasing):"
                " distortions amplify on the pessimistic side",
                font_size=22,
            ),
        ).arrange(DOWN, buff=0.35, aligned_edge=LEFT)
        ch.shift(DOWN * 0.5 + LEFT * 0.4)

        with self.voiceover(
            "The appendix decomposes the loss into three channels. The"
            " capacity channel contributes zero asymmetry, because K star"
            " is independent of lambda by Proposition one. The timing"
            " factor is approximately symmetric."
        ):
            self.play(FadeIn(ch[0]), run_time=0.8)
            self.play(FadeIn(ch[1]), run_time=0.8)
        with self.voiceover(
            "The training allocation channel dominates. At baseline the"
            " H-regime term accounts for about seventy percent of A"
            " effective, so a pessimist who barely trains destroys the"
            " dominant source of firm value, while an optimist only"
            " sacrifices the smaller inference revenue."
        ):
            self.play(FadeIn(ch[2]), FadeIn(ch[3]), run_time=1.0)
        with self.voiceover(
            "And the map from lambda to phi star is concave, with"
            " elasticity below one and decreasing, which amplifies policy"
            " distortions on the pessimistic side. Together these produce"
            " the positive third derivative."
        ):
            self.play(FadeIn(ch[4]), run_time=1.0)
        self.pause(0.4)
        self.clear_body()


class P6S12DilemmaNumbers(PaperScene):
    def construct(self):
        self.set_header("The dilemma, quantified", kicker="6.8  DARIO'S DILEMMA")

        from ai_lab_investment.models.parameters import ModelParameters
        from ai_lab_investment.models.valuation import ValuationAnalysis

        va = ValuationAnalysis(ModelParameters())
        grid = [0.02, 0.04, 0.06, 0.08, 0.10, 0.14, 0.20, 0.30, 0.40, 0.50]
        losses = np.array([
            100 * va.dario_dilemma(0.10, g)["value_loss_pct"] for g in grid
        ])
        lev_losses = np.array([
            100 * va.dario_dilemma_leveraged(0.10, g, 0.40)["value_loss_pct"]
            for g in grid
        ])

        ax = clean_axes(x_range=[0, 0.53], y_range=[0, 30], width=8.8, height=4.0)
        ax.shift(DOWN * 0.5 + RIGHT * 0.4)
        xl = MathTex(r"\lambda_{\text{invest}}", font_size=28, color=C_FAINT).next_to(
            ax.x_axis, RIGHT, buff=0.15
        )
        yl = Text("value lost (%)", font_size=20, color=C_FAINT).next_to(
            ax.y_axis, UP, buff=0.15
        )
        truth = DashedLine(
            ax.coords_to_point(0.10, 0), ax.coords_to_point(0.10, 24), color=C_DEMAND
        )
        truth_lab = MathTex(
            r"\lambda_{\text{true}} = 0.10", font_size=26, color=C_DEMAND
        ).next_to(truth, DOWN, buff=0.15)
        c_unlev = ax.plot_line_graph(
            grid, losses, line_color=C_COST, add_vertex_dots=False
        )
        c_lev = ax.plot_line_graph(
            grid, lev_losses, line_color=C_DEFAULT, add_vertex_dots=False
        )
        leg = VGroup(
            Text("unleveraged", font_size=19, color=C_COST),
            Text("leverage 0.40", font_size=19, color=C_DEFAULT),
        ).arrange(DOWN, buff=0.15, aligned_edge=LEFT)
        leg.move_to(ax.coords_to_point(0.43, 9))

        with self.voiceover(
            "Here is the loss curve, computed from the model over a grid"
            " of mistaken beliefs, with the truth at zero point one."
            " The red curve is the unleveraged firm; the maroon curve adds"
            " forty percent leverage."
        ):
            self.play(Create(ax), FadeIn(xl), FadeIn(yl), run_time=0.9)
            self.play(Create(truth), FadeIn(truth_lab), run_time=0.7)
            self.play(Create(c_unlev), run_time=1.5)
            self.play(Create(c_lev), FadeIn(leg), run_time=1.2)

        d_cons = Dot(ax.coords_to_point(0.02, losses[0]), color=C_COST, radius=0.07)
        n_cons = Text("-26%  (phi ~ 0.14)", font_size=21, color=C_COST).next_to(
            d_cons, UP + RIGHT, buff=0.1
        )
        d_aggr = Dot(ax.coords_to_point(0.20, losses[6]), color=C_H, radius=0.07)
        n_aggr = Text("-6%", font_size=21, color=C_H).next_to(
            d_aggr, UP + LEFT, buff=0.1
        )
        with self.voiceover(
            "A conservative firm investing as if lambda were zero point"
            " zero two loses about twenty-six percent of value; its"
            " training fraction collapses to about zero point one four."
            " A comparably aggressive firm at zero point two loses only"
            " about six percent."
        ):
            self.play(FadeIn(d_cons), FadeIn(n_cons), run_time=0.9)
            self.play(FadeIn(d_aggr), FadeIn(n_aggr), run_time=0.9)

        d_ext = Dot(ax.coords_to_point(0.50, losses[-1]), color=C_COST, radius=0.07)
        n_ext = Text("23% vs 21% levered", font_size=20, color=C_FAINT).next_to(
            d_ext, UP + LEFT, buff=0.1
        )
        with self.voiceover(
            "At the extreme optimist's zero point five, the unleveraged"
            " loss is about twenty-three percent, but the levered loss is"
            " slightly lower, twenty-one. Why? For an overbuilt,"
            " over-trained firm, default truncates the perpetual operating"
            " cost drain on the overscaled capacity: liquidation sheds the"
            " delta K obligation, and that shutdown option modestly"
            " offsets the allocation distortion."
        ):
            self.play(FadeIn(d_ext), FadeIn(n_ext), run_time=1.0)
        self.pause(0.3)
        self.clear_body()

        tail = VGroup(
            Text("5-year default probability at leverage 0.40:", font_size=25),
            Text(
                "conservative (0.02): 0.79%      baseline: 0.64%      "
                "aggressive (0.50): 5.04%  (~8x)",
                font_size=24,
                color=C_DEFAULT,
            ),
        ).arrange(DOWN, buff=0.35, aligned_edge=LEFT)
        tail.shift(UP * 1.3 + LEFT * 0.4)
        with self.voiceover(
            "But the expected-value metric tells only half the story. In"
            " the tail, the asymmetry flips: at forty percent leverage,"
            " the conservative firm's five-year default probability is"
            " zero point seven nine percent, barely above the zero point"
            " six four baseline, while the aggressive firm's is five point"
            " zero four percent, nearly eight times the baseline. It"
            " enters earlier, bigger, and with a higher coupon."
        ):
            self.play(FadeIn(tail), run_time=1.2)

        duo = VGroup(
            Text("Duopoly amplification (Appendix E):", font_size=25),
            Text(
                "conservative: 26% -> 38%      aggressive: 6% -> 17%",
                font_size=24,
                color=C_H,
            ),
            Text(
                "asymmetry preserved at roughly 2x",
                font_size=23,
                color=C_FAINT,
            ),
        ).arrange(DOWN, buff=0.3, aligned_edge=LEFT)
        duo.next_to(tail, DOWN, buff=0.7).align_to(tail, LEFT)
        with self.voiceover(
            "Competition makes everything worse. Against a well-calibrated"
            " rival, the conservative loss rises from twenty-six to"
            " thirty-eight percent, because the firm also cedes the leader"
            " position and its monopoly-phase rents; the aggressive loss"
            " rises from six to seventeen."
        ):
            self.play(FadeIn(duo[0]), FadeIn(duo[1]), run_time=1.0)
        with self.voiceover(
            "The asymmetry survives at roughly two to one. Underinvestment"
            " costs expected value; overinvestment buys tail risk. That is"
            " Dario's dilemma in numbers."
        ):
            self.play(FadeIn(duo[2]), run_time=0.8)
        self.pause(0.4)
        self.clear_body()


class P6S13EquitySensitivity(PaperScene):
    def construct(self):
        self.set_header(
            "Equity value and timeline news", kicker="6.9  EQUITY SENSITIVITY"
        )

        from ai_lab_investment.models.parameters import ModelParameters
        from ai_lab_investment.models.valuation import ValuationAnalysis

        va = ValuationAnalysis(ModelParameters())
        lams = np.array([
            0.02,
            0.05,
            0.08,
            0.10,
            0.15,
            0.20,
            0.25,
            0.30,
            0.35,
            0.40,
            0.45,
            0.50,
        ])
        ev = va.equity_value_vs_lambda_with_phi(lams, X=0.001)
        vals = ev["option_values"]
        index = vals / vals[3] * 100.0

        ax = clean_axes(x_range=[0, 0.53], y_range=[60, 185], width=8.8, height=3.6)
        ax.shift(DOWN * 0.5 + RIGHT * 0.4)
        xl = MathTex(r"\lambda", font_size=28, color=C_FAINT).next_to(
            ax.x_axis, RIGHT, buff=0.15
        )
        yl = Text("option value (baseline = 100)", font_size=20, color=C_FAINT).next_to(
            ax.y_axis, UP, buff=0.15
        )
        curve = ax.plot_line_graph(
            lams, index, line_color=C_OPTION, add_vertex_dots=False
        )
        infl = DashedLine(
            ax.coords_to_point(0.08, 60), ax.coords_to_point(0.08, 170), color=C_FAINT
        )
        infl_lab = Text("convex only below ~0.08", font_size=19, color=C_FAINT)
        infl_lab.next_to(infl, RIGHT, buff=0.15).shift(UP * 1.6)

        with self.voiceover(
            "Last quantitative block: how equity value responds to"
            " timeline beliefs. Computing the pre-investment option value"
            " across lambda, indexed to one hundred at the baseline, the"
            " value is increasing but concave over the policy-relevant"
            " range from zero point one to zero point five."
        ):
            self.play(Create(ax), FadeIn(xl), FadeIn(yl), run_time=0.9)
            self.play(Create(curve), run_time=1.8)
        with self.voiceover(
            "It is convex only at very low arrival rates, below about"
            " zero point zero eight, beneath the range of current market"
            " disagreement."
        ):
            self.play(Create(infl), FadeIn(infl_lab), run_time=0.9)

        why = MathTex(
            r"\lambda \to \infty:\ F \to F_H \text{ (saturation)};\qquad"
            r" F(X, \lambda) = C(\lambda)\,X^{\beta_H}",
            font_size=30,
            color=C_TEXT,
        ).to_edge(DOWN, buff=0.85)
        with self.voiceover(
            "Why concave? As lambda grows, the option value saturates"
            " toward the lambda-independent H-regime value F H from below,"
            " so each extra unit of optimism adds less. And because the"
            " option has the form C of lambda times X to the beta H, with"
            " beta H independent of lambda, the curvature in lambda is the"
            " same at every demand level."
        ):
            self.play(Write(why), run_time=1.3)

        pred = Text(
            "Prediction: asymmetric response to AI timeline news,"
            " biggest for pessimistically priced firms.",
            font_size=22,
            color=C_DEMAND,
        ).to_edge(DOWN, buff=0.35)
        with self.voiceover(
            "The prediction: bad timeline news should move valuations more"
            " than equally sized good news, with the largest sensitivity"
            " for firms priced under relatively pessimistic beliefs, where"
            " the value function is steepest."
        ):
            self.play(FadeIn(pred), run_time=1.0)
        self.pause(0.4)
        self.clear_body()


class P6S14Robustness(PaperScene):
    def construct(self):
        self.set_header("Robustness, rapid fire", kicker="6.10  ROBUSTNESS")

        rows = [
            [
                Text("Object", font_size=21, color=C_FAINT),
                Text("Tullock", font_size=21, color=C_FAINT),
                Text("Fixed-pie", font_size=21, color=C_FAINT),
            ],
            [MathTex(r"\phi_F^*", font_size=28), "0.70", "0.70"],
            [
                Text("preemption discount", font_size=21),
                "0.57",
                "0.63",
            ],
            [MathTex(r"\underline{\phi}", font_size=28), "0.18", "0.18"],
        ]
        fp = grid_table(
            rows, col_x=[-3.6, -0.6, 1.6], row_h=0.5, font_size=22, left_cols=(0,)
        )
        fp.move_to(UP * 0.9 + LEFT * 1.2)
        fp_title = (
            Text(
                "1. Fixed-pie contest (kills revenue expansion)",
                font_size=24,
                color=C_H,
            )
            .next_to(fp, UP, buff=0.4)
            .align_to(fp, LEFT)
        )

        with self.voiceover(
            "Three robustness checks, quickly. First, replace the Tullock"
            " contest with a fixed-pie version that removes the"
            " revenue-expansion property: shares stay Tullock, but the"
            " industry pie no longer grows with capacity asymmetry."
        ):
            self.play(FadeIn(fp_title), run_time=0.7)
            self.play(FadeIn(fp), run_time=1.0)
        with self.voiceover(
            "The training fraction and the faith threshold are exactly"
            " unchanged, because both live inside A effective. Only the"
            " preemption discount softens, from zero point five seven to"
            " zero point six three. So the revenue-expansion property"
            " matters for the timing race, and for nothing else."
        ):
            self.play(Indicate(fp[2], color=C_OPTION), run_time=1.0)
        self.pause(0.3)
        self.clear_body()

        dyn = VGroup(
            Text("2. Two-period dynamic phi", font_size=24, color=C_TRAIN),
            Text(
                "phi_1 ~ static phi* (0.70 -> 0.76 across adjustment costs)",
                font_size=22,
            ),
            Text("value gain of reallocation: 1.6% free -> 0.3% costly", font_size=22),
            Text(
                "threshold phi-underbar 0.18 unchanged;"
                " static model slightly overstates initial phi",
                font_size=22,
            ),
        ).arrange(DOWN, buff=0.32, aligned_edge=LEFT)
        dyn.shift(UP * 1.1 + LEFT * 0.6)
        with self.voiceover(
            "Second, the most-flagged limitation: static phi. In a"
            " two-period extension where the firm can reallocate after"
            " observing the regime, the initial allocation stays close to"
            " the static optimum, drifting from zero point seven zero up"
            " to zero point seven six as adjustment costs rise."
        ):
            self.play(FadeIn(dyn[0]), FadeIn(dyn[1]), run_time=1.0)
        with self.voiceover(
            "The value gain from the reallocation option is one point six"
            " percent when reallocation is free, and only zero point three"
            " percent when it is costly. The faith threshold is unchanged,"
            " and the trigger is unchanged; the static model slightly"
            " overstates the initial training fraction, as the discussion"
            " section predicted."
        ):
            self.play(FadeIn(dyn[2]), FadeIn(dyn[3]), run_time=1.0)

        three = (
            Text(
                "3. Three-regime extension (L -> M -> H): qualitatively unchanged.",
                font_size=23,
                color=C_FAINT,
            )
            .next_to(dyn, DOWN, buff=0.7)
            .align_to(dyn, LEFT)
        )
        with self.voiceover(
            "And third, a three-regime extension with an intermediate"
            " capability step leaves the results qualitatively unchanged:"
            " the binary uncertainty about transformative AI is the"
            " essential feature."
        ):
            self.play(FadeIn(three), run_time=0.8)
        self.pause(0.4)
        self.clear_body()


class P6S15Predictions(PaperScene):
    def construct(self):
        self.set_header("What the data could say", kicker="6.11  TESTABLE PREDICTIONS")

        preds = VGroup(
            Text(
                "1. Two faces of credit risk: high phi-hat -> fewer defaults,"
                " larger loss given default",
                font_size=23,
            ),
            Text(
                "2. Training-beta: high phi-hat -> higher equity beta"
                " (more growth-option value)",
                font_size=23,
            ),
            Text(
                "3. Asymmetric news response: bad timeline news moves"
                " valuations more than good",
                font_size=23,
            ),
            Text(
                "4. Role-invariant allocation: beliefs explain phi-hat;"
                " order of entry does not",
                font_size=23,
            ),
        ).arrange(DOWN, buff=0.4, aligned_edge=LEFT)
        preds.shift(UP * 0.8 + LEFT * 0.3)

        with self.voiceover(
            "The model leaves four directional predictions. First, the two"
            " faces of credit risk: conditional on leverage,"
            " training-intensive labs should default less often but"
            " recover less for creditors when they do. The decomposition"
            " is the sharp prediction; the net effect on spreads is"
            " ambiguous and mildly positive at baseline."
        ):
            self.play(FadeIn(preds[0]), run_time=0.9)
        with self.voiceover(
            "Second, a training-beta relationship: higher phi-hat means"
            " more of the value is growth option, hence higher equity"
            " beta."
        ):
            self.play(FadeIn(preds[1]), run_time=0.9)
        with self.voiceover(
            "Third, the asymmetric response to AI timeline news that"
            " follows from concavity. And fourth, role invariance:"
            " training fractions should be explained by beliefs and"
            " technology, not by competitive position; order of entry"
            " should predict timing and scale, but not the split."
        ):
            self.play(FadeIn(preds[2]), run_time=0.9)
            self.play(FadeIn(preds[3]), run_time=0.9)
        self.pause(0.3)

        lims = VGroup(
            Text("Limitations to keep in mind:", font_size=24, color=C_COST),
            Text(
                "static phi  |  extreme regime-revenue split  |  Tullock reduced form",
                font_size=22,
                color=C_FAINT,
            ),
            Text(
                "no AI-winter reversal  |  partial equilibrium",
                font_size=22,
                color=C_FAINT,
            ),
        ).arrange(DOWN, buff=0.28, aligned_edge=LEFT)
        lims.next_to(preds, DOWN, buff=0.65).align_to(preds, LEFT)
        with self.voiceover(
            "Balanced against the limitations: phi is fixed at investment"
            " time; the regime-revenue structure, inference in L and"
            " training in H, is deliberately extreme; the Tullock contest"
            " is a reduced form; the switch to H is absorbing, so there is"
            " no AI winter; and everything is partial equilibrium."
        ):
            self.play(FadeIn(lims), run_time=1.2)
        self.pause(0.4)
        self.clear_body()


class P6S16Close(PaperScene):
    def construct(self):
        self.set_header("What is proved vs computed", kicker="6.12  SERIES CLOSE")

        rows = [
            [
                Text("Result", font_size=20, color=C_FAINT),
                Text("Method", font_size=20, color=C_FAINT),
            ],
            [
                Text("Prop. 1: K*, phi*, comparative statics", font_size=21),
                Text("closed form / implicit function", font_size=21, color=C_H),
            ],
            [
                Text("Prop. 2(i)-(ii): X_D, faith thresholds", font_size=21),
                Text("closed form", font_size=21, color=C_H),
            ],
            [
                Text("Prop. 2(iii)-(iv): substitution effects", font_size=21),
                Text("analytical", font_size=21, color=C_H),
            ],
            [
                Text("Prop. 3(i): X_P exists / unique", font_size=21),
                Text(
                    "analytical; uniqueness comp. if levered",
                    font_size=21,
                    color=C_OPTION,
                ),
            ],
            [
                Text("Prop. 3(ii): role invariance of phi", font_size=21),
                Text(
                    "exact critical pt; global opt. comp.", font_size=21, color=C_OPTION
                ),
            ],
            [
                Text("Prop. 3(iii)-(v): preemption statics", font_size=21),
                Text("numerical", font_size=21, color=C_COST),
            ],
            [
                Text("Numerical Finding 1: Dario's dilemma", font_size=21),
                Text("numerical", font_size=21, color=C_COST),
            ],
        ]
        tax = grid_table(
            rows, col_x=[-6.3, 0.6], row_h=0.5, font_size=21, left_cols=(0, 1)
        )
        tax.move_to(DOWN * 0.3 + UP * 1.2)

        with self.voiceover(
            "To close the series, the result taxonomy: what is actually"
            " proved, and what is computed. The single-firm optimum and"
            " the default boundary with its faith thresholds are closed"
            " form."
        ):
            self.play(FadeIn(tax[0]), run_time=0.5)
            for row in tax[1:4]:
                self.play(FadeIn(row), run_time=0.5)
        with self.voiceover(
            "The preemption trigger's existence is analytical, with"
            " uniqueness analytical when unlevered and computational with"
            " leverage. Role invariance is an exact critical point, with"
            " global optimality verified computationally."
        ):
            for row in tax[4:6]:
                self.play(FadeIn(row), run_time=0.5)
        with self.voiceover(
            "The preemption comparative statics and Dario's dilemma are"
            " honest numerical findings, verified across all"
            " parameterizations tested. Knowing which claim carries which"
            " warranty is half the referee report."
        ):
            for row in tax[6:]:
                self.play(FadeIn(row), run_time=0.5)
        self.pause(0.4)
        self.clear_body()

        outro = VGroup(
            Text(
                "Investing in Artificial General Intelligence",
                font_size=34,
                weight="BOLD",
            ),
            Text(
                "Derivation walkthrough - end of Part 6 (of 6)",
                font_size=24,
                color=C_FAINT,
            ),
            Text(
                "github.com/fintech-research/ai-lab-investment",
                font_size=22,
                color=C_FAINT,
            ),
        ).arrange(DOWN, buff=0.35)
        with self.voiceover(
            "And that is the whole paper: one allocation linking growth"
            " and survival, a calibration that turns beliefs into numbers,"
            " and a dilemma that prices being wrong in both directions."
            " Thanks for following the full derivation."
        ):
            self.play(FadeOut(self.header), run_time=0.5)
            self.header = None
            self.play(FadeIn(outro), run_time=1.5)
        self.pause(1.0)
        self.play(FadeOut(outro), run_time=1.0)
