"""Walkthrough Part 1: The Environment -- demand, technology, and the toolkit.

Derivation/proof walkthrough series (issue #98), Part 1. Covers the paper's
Environment and Technology subsections (paper/_model.qmd), the risk-adjustment
framework, the derivation toolkit (growing perpetuity, characteristic
equation, regime-switch HJB), Assumption 1, and the baseline calibration.

Render: just render-walkthrough
Draft a single scene:
    cd video && uv run manim render -ql walkthrough_part1.py P1S01Title
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
    GrowFromEdge,
    LaggedStart,
    MathTex,
    Rectangle,
    Text,
    VGroup,
    Write,
)
from scene_base import PaperScene
from theme import (
    BASELINE,
    C_COST,
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
    "P1S01Title",
    "P1S02Demand",
    "P1S03RiskAdjustment",
    "P1S04Technology",
    "P1S05Allocation",
    "P1S06Perpetuity",
    "P1S07Characteristic",
    "P1S08RegimeHJB",
    "P1S09Assumptions",
    "P1S10Recap",
]


class P1S01Title(PaperScene):
    def construct(self):
        series = Text(
            "Investing in AGI: the full derivation",
            font_size=48,
            weight="BOLD",
        )
        part = Text("Part 1 - The Environment", font_size=34, color=C_OPTION)
        sub = Text(
            "demand, technology, and the toolkit",
            font_size=26,
            color=C_FAINT,
        )
        VGroup(series, part, sub).arrange(DOWN, buff=0.4)

        with self.voiceover(
            "Welcome. This series walks through the paper Investing in"
            " Artificial General Intelligence, section by section, with every"
            " derivation and every proof worked out in full."
        ):
            self.play(Write(series), run_time=2.2)
        with self.voiceover(
            "Appendix proofs are not deferred to the end: each one appears"
            " inline, right where the result it supports is stated."
        ):
            self.play(FadeIn(part, shift=UP * 0.2), run_time=0.9)
        with self.voiceover(
            "This is part one: the model environment. We set up the demand"
            " process, the technology, and the training inference split, and"
            " then build the small mathematical toolkit that every later part"
            " leans on."
        ):
            self.play(FadeIn(sub), run_time=0.9)
        self.pause(0.4)

        agenda = VGroup(
            Text("1.  Regime-switching demand", font_size=28),
            MathTex(
                r"\text{2.\ \ Risk adjustment: what } r,\ \mu,\ \sigma \text{ mean}",
                font_size=28,
            ),
            Text("3.  Technology: convex costs, operating costs", font_size=28),
            Text("4.  Training versus inference", font_size=28),
            Text("5.  Toolkit: perpetuity, characteristic roots, HJB", font_size=28),
            Text("6.  Assumption 1 and the baseline numbers", font_size=28),
        ).arrange(DOWN, buff=0.38, aligned_edge=LEFT)
        with self.voiceover(
            "Here is the plan. Nothing in this part is hard on its own, but"
            " getting these pieces exactly right is what makes the later"
            " propositions fall out cleanly."
        ):
            self.play(FadeOut(series), FadeOut(part), FadeOut(sub), run_time=0.6)
            self.play(
                LaggedStart(
                    *[FadeIn(a, shift=RIGHT * 0.3) for a in agenda],
                    lag_ratio=0.15,
                ),
                run_time=2.5,
            )
        self.pause(0.5)
        self.play(FadeOut(agenda), run_time=0.7)


class P1S02Demand(PaperScene):
    def construct(self):
        self.set_header("Regime-switching demand", kicker="PART 1 - ENVIRONMENT")

        gbm = MathTex(
            r"dX_t = \mu_s X_t\,dt + \sigma X_t\,dW_t,",
            r"\quad s \in \{L, H\}",
            font_size=42,
        ).to_edge(UP, buff=1.5)
        gbm[0][4:6].set_color(C_DEMAND)
        with self.voiceover(
            "Everything in the model is driven by one state variable: X, the"
            " demand for AI compute. It follows a geometric Brownian motion:"
            " d X equals mu sub s, X d t, plus sigma X d W."
        ):
            self.play(Write(gbm[0]), run_time=1.8)
        with self.voiceover(
            "The drift mu sub s depends on the regime s, which is either L or"
            " H; the volatility sigma is common to both regimes, and W is a"
            " standard Brownian motion."
        ):
            self.play(Write(gbm[1]), run_time=1.0)

        # Sample path with a regime switch (visual drifts exaggerated).
        rng = np.random.default_rng(42)
        dt = 0.01
        horizon = 12.0
        t_switch = 6.5
        t = np.arange(0.0, horizon + dt, dt)
        x = np.empty_like(t)
        x[0] = 1.0
        sig_vis = 0.16
        for i in range(1, len(t)):
            mu_vis = 0.05 if t[i] < t_switch else 0.22
            x[i] = x[i - 1] * np.exp(
                (mu_vis - 0.5 * sig_vis**2) * dt + sig_vis * np.sqrt(dt) * rng.normal()
            )
        y_max = float(x.max()) * 1.2
        ax = clean_axes(
            x_range=[0, horizon], y_range=[0, y_max], width=9.2, height=3.9
        ).shift(DOWN * 1.15)
        note = Text(
            "(drifts exaggerated for visibility)", font_size=18, color=C_FAINT
        ).move_to(ax.coords_to_point(2.4, y_max * 0.9))

        mask = t <= t_switch
        line_l = ax.plot_line_graph(
            t[mask], x[mask], line_color=C_L, add_vertex_dots=False
        )
        line_h = ax.plot_line_graph(
            t[~mask], x[~mask], line_color=C_H, add_vertex_dots=False
        )
        lab_l = MathTex(r"\mu_L", font_size=34, color=C_L).move_to(
            ax.coords_to_point(3.0, float(x[mask].max()) * 1.35)
        )
        with self.voiceover(
            "The economy starts in regime L, the pre AGI world: demand grows"
            " at the moderate rate mu L, driven by today's AI products."
        ):
            self.play(Create(ax), FadeIn(note), run_time=0.9)
            self.play(Create(line_l), FadeIn(lab_l), run_time=2.0)

        flash = DashedLine(
            ax.coords_to_point(t_switch, 0),
            ax.coords_to_point(t_switch, y_max * 0.97),
            color=C_DEMAND,
        )
        agi = Text("AGI arrives", font_size=24, color=C_DEMAND).next_to(
            flash, UP, buff=0.1
        )
        lab_h = MathTex(r"\mu_H > \mu_L", font_size=34, color=C_H).move_to(
            ax.coords_to_point(9.3, y_max * 0.84)
        )
        with self.voiceover(
            "At a random time, a breakthrough arrives, transformative AI, and"
            " the economy jumps to regime H, where demand grows at the faster"
            " rate mu H."
        ):
            self.play(Create(flash), FadeIn(agi), run_time=1.0)
            self.play(Create(line_h), FadeIn(lab_h), run_time=2.0)

        pois = MathTex(
            r"\Pr(\text{switch in } [t, t+dt]) = \lambda\,dt",
            font_size=34,
            color=C_DEMAND,
        ).to_edge(DOWN, buff=0.35)
        with self.voiceover(
            "The arrival is a Poisson event with rate lambda: over any short"
            " interval d t, the switch happens with probability lambda d t,"
            " independently of the Brownian shocks."
        ):
            self.play(Write(pois), run_time=1.4)

        absorbing = Text("(absorbing)", font_size=24, color=C_H)
        absorbing.next_to(lab_h, DOWN, buff=0.18)
        with self.voiceover(
            "Crucially, the switch is absorbing: once the economy is in H, it"
            " stays there forever. That encodes the irreversibility of AI"
            " progress: capabilities, once demonstrated, do not disappear."
        ):
            self.play(FadeIn(absorbing), run_time=1.2)
        self.pause(0.4)

        self.clear_body()
        ineq1 = MathTex(r"\mu_H > \mu_L", font_size=48)
        ineq1[0][0:2].set_color(C_H)
        ineq1[0][3:5].set_color(C_L)
        ineq2 = MathTex(r"r \;>\; \mu_H \;>\; \mu_L", font_size=48)
        ineq2[0][2:4].set_color(C_H)
        ineq2[0][5:7].set_color(C_L)
        VGroup(ineq1, ineq2).arrange(DOWN, buff=0.7).shift(DOWN * 0.3)
        with self.voiceover(
            "Two parameter restrictions complete the environment. First, mu H"
            " is strictly greater than mu L: the breakthrough raises growth."
        ):
            self.play(Write(ineq1), run_time=1.2)
        with self.voiceover(
            "Second, the discount rate r exceeds mu H, which exceeds mu L."
            " r greater than mu H is the convergence requirement that keeps"
            " present values finite, and the toolkit will show exactly why."
        ):
            self.play(Write(ineq2), run_time=1.4)
        self.pause(0.4)
        self.clear_body()


class P1S03RiskAdjustment(PaperScene):
    def construct(self):
        self.set_header(
            "What r, mu, and sigma really are", kicker="PART 1 - ENVIRONMENT"
        )

        def row(math: MathTex, note_str: str) -> VGroup:
            note = Text(note_str, font_size=22, color=C_FAINT)
            return VGroup(math, note).arrange(DOWN, aligned_edge=LEFT, buff=0.12)

        r1 = row(
            MathTex(r"r = \text{WACC}", font_size=36),
            "embeds the equity risk premium and the cost of debt",
        )
        r2 = row(
            MathTex(
                r"\mu_s = \underbrace{\bar{\mu}_s}_{\text{physical drift}}"
                r" - \underbrace{\eta_s}_{\text{risk premium}}",
                font_size=36,
            ),
            "certainty-equivalent (risk-adjusted) growth rates",
        )
        r3 = row(
            MathTex(r"\sigma \text{ unchanged}", font_size=36),
            "Girsanov: a change of measure shifts drift, not volatility",
        )
        r4 = row(
            MathTex(
                r"\text{PV} = \mathbb{E}^{\mathbb{Q}}\!\left[\int_0^\infty"
                r" e^{-rt}\,\pi(X_t)\,dt\right],"
                r"\quad \mu_s^{\mathbb{Q}} = \mu_s",
                font_size=36,
            ),
            "equivalent reading: the model lives under a risk-neutral measure Q",
        )
        rows = VGroup(r1, r2, r3, r4).arrange(DOWN, aligned_edge=LEFT, buff=0.42)
        rows.to_edge(LEFT, buff=1.0).shift(DOWN * 0.45)

        with self.voiceover(
            "One footnote in the paper deserves its own scene, because every"
            " number later depends on it: what exactly are r, mu, and sigma?"
            " Following Dixit and Pindyck, the whole model lives in a single"
            " risk adjusted, certainty equivalent framework."
        ):
            self.pause(0.2)
        with self.voiceover(
            "The discount rate r is the firm's weighted average cost of"
            " capital. The compensation investors demand for bearing risk is"
            " already inside it."
        ):
            self.play(FadeIn(r1, shift=RIGHT * 0.2), run_time=1.0)
        with self.voiceover(
            "The growth rates mu L and mu H are not physical expected growth"
            " rates of demand. They are the physical rates minus an"
            " appropriate risk premium, so that discounting the expected cash"
            " flow at r yields the correct present value."
        ):
            self.play(FadeIn(r2, shift=RIGHT * 0.2), run_time=1.2)
        with self.voiceover(
            "The volatility sigma needs no adjustment at all. By Girsanov's"
            " theorem, changing the probability measure shifts the drift of a"
            " diffusion but leaves its volatility untouched, so sigma is the"
            " same under both measures."
        ):
            self.play(FadeIn(r3, shift=RIGHT * 0.2), run_time=1.0)
        with self.voiceover(
            "Equivalently, you can read every valuation in the paper as an"
            " expectation under a risk neutral measure Q, with drift mu s"
            " already risk adjusted and discount rate r."
        ):
            self.play(FadeIn(r4, shift=RIGHT * 0.2), run_time=1.2)

        takeaway = MathTex(
            r"\text{Risk is priced once: in the wedge } r - \mu"
            r"\text{, never in the cash flows.}",
            font_size=27,
            color=C_OPTION,
        ).to_edge(DOWN, buff=0.45)
        with self.voiceover(
            "The point of the construction is to avoid double counting. If we"
            " discounted physical drifts at the WACC, the risk premium would"
            " be charged twice: once in r and once in the drift."
        ):
            self.play(FadeIn(takeaway), run_time=1.2)
        with self.voiceover(
            "Risk is priced exactly once, in the wedge between r and mu. And"
            " the model never needs a full asset pricing engine: the reduced"
            " form is consistent with no arbitrage valuation throughout."
        ):
            self.play(Create(highlight(takeaway)), run_time=0.8)
        self.pause(0.4)
        self.clear_body()


class P1S04Technology(PaperScene):
    def construct(self):
        self.set_header("Technology", kicker="PART 1 - ENVIRONMENT")

        cost = MathTex(
            r"I(K) = c\,K^{\gamma},",
            r"\quad \gamma > 1",
            font_size=42,
        ).to_edge(UP, buff=1.4)
        cost.set_color(C_COST)
        with self.voiceover(
            "Now the technology. To enter, a firm pays an irreversible lump"
            " sum, I of K equals c times K to the power gamma, to install"
            " capacity K."
        ):
            self.play(Write(cost), run_time=1.6)

        gamma = BASELINE["gamma"]
        ax = clean_axes(
            x_range=[0, 1.25], y_range=[0, 1.55], width=5.2, height=3.4
        ).shift(LEFT * 3.4 + DOWN * 1.3)
        convex = ax.plot(lambda k: k**gamma, x_range=[0, 1.2], color=C_COST)
        linear = DashedLine(
            ax.coords_to_point(0, 0), ax.coords_to_point(1.2, 1.2), color=C_FAINT
        )
        lab_convex = MathTex(r"\gamma = 1.5", font_size=30, color=C_COST).next_to(
            ax.coords_to_point(1.1, 1.1**gamma), DOWN + RIGHT, buff=0.12
        )
        lab_linear = MathTex(r"\gamma = 1", font_size=28, color=C_FAINT).next_to(
            ax.coords_to_point(0.55, 0.55), UP + LEFT, buff=0.1
        )
        with self.voiceover(
            "Gamma strictly greater than one makes the cost convex. Here is"
            " the baseline gamma of one point five against the linear"
            " benchmark: marginal cost rises with scale, and gamma equal to"
            " one nests the standard constant returns case."
        ):
            self.play(Create(ax), run_time=0.8)
            self.play(Create(linear), FadeIn(lab_linear), run_time=0.9)
            self.play(Create(convex), FadeIn(lab_convex), run_time=1.2)

        bullets = VGroup(
            Text("power constraints", font_size=26),
            Text("GPU supply bottlenecks", font_size=26),
            Text("data center site preparation", font_size=26),
            Text("construction complexity", font_size=26),
        ).arrange(DOWN, buff=0.3, aligned_edge=LEFT)
        bullets.shift(RIGHT * 3.4 + DOWN * 1.0)
        with self.voiceover(
            "The convexity is grounded in how these facilities get built:"
            " power constraints, GPU supply bottlenecks, site preparation,"
            " and construction complexity all bind harder as the project"
            " grows."
        ):
            self.play(
                LaggedStart(
                    *[FadeIn(b, shift=RIGHT * 0.2) for b in bullets],
                    lag_ratio=0.25,
                ),
                run_time=2.0,
            )

        flags = Text(
            "fixed once installed  /  one irreversible shot (no staging)",
            font_size=24,
            color=C_FAINT,
        ).to_edge(DOWN, buff=0.4)
        with self.voiceover(
            "Two simplifications are flagged at the outset: capacity is fixed"
            " once installed, with no expansion and no mothballing, and the"
            " investment is a single irreversible shot rather than a staged"
            " sequence of options. Both are discussed as extensions later in"
            " the paper."
        ):
            self.play(FadeIn(flags), run_time=1.0)
        self.pause(0.3)
        self.clear_body()

        flow = MathTex(
            r"\text{operating flow cost} = \delta K,",
            r"\quad \delta = 0.03",
            font_size=42,
        ).shift(UP * 1.1)
        flow[0][-3:-1].set_color(C_COST)
        with self.voiceover(
            "Once installed, capacity also burns a continuous operating cost:"
            " delta per unit of capacity per unit of time, covering power,"
            " cooling, maintenance, and personnel. At baseline, delta is"
            " three percent."
        ):
            self.play(Write(flow), run_time=1.4)

        nodk = MathTex(
            r"dK_t = 0 \quad \text{after installation}", font_size=36
        ).next_to(flow, DOWN, buff=0.55)
        contrast = VGroup(
            MathTex(
                r"\delta K \text{ is a perpetual flow cost, not a decay rate}",
                font_size=26,
                color=C_COST,
            ),
            MathTex(
                r"\text{capacity } K \text{ never depreciates in the model}",
                font_size=26,
                color=C_TEXT,
            ),
        ).arrange(DOWN, buff=0.25)
        contrast.next_to(nodk, DOWN, buff=0.5)
        with self.voiceover(
            "The paper is explicit about what delta is not: it is not"
            " depreciation. Capacity K never decays once installed; delta K"
            " is a perpetual operating expense."
        ):
            self.play(Write(nodk), run_time=1.0)
            self.play(FadeIn(contrast[0]), run_time=0.8)
        with self.voiceover(
            "Hardware obsolescence, new GPU generations and algorithmic"
            " efficiency gains, is real, but it lives in the calibration"
            " discussion, not in the law of motion for K. Keep the two ideas"
            " separate when reading delta."
        ):
            self.play(FadeIn(contrast[1]), run_time=0.8)
        self.pause(0.4)
        self.clear_body()


class P1S05Allocation(PaperScene):
    def construct(self):
        self.set_header("Training versus inference", kicker="PART 1 - ENVIRONMENT")

        bar_h, bar_w = 3.2, 1.4
        phi_vis = 0.6
        train = Rectangle(
            width=bar_w,
            height=bar_h * phi_vis,
            fill_color=C_TRAIN,
            fill_opacity=0.85,
            stroke_color=C_TEXT,
        )
        infer = Rectangle(
            width=bar_w,
            height=bar_h * (1 - phi_vis),
            fill_color=C_INFER,
            fill_opacity=0.85,
            stroke_color=C_TEXT,
        )
        VGroup(train, infer).arrange(DOWN, buff=0).shift(LEFT * 4.4 + DOWN * 0.9)
        lab_train = MathTex(r"\phi K", font_size=36, color=C_TRAIN).next_to(
            train, LEFT, buff=0.3
        )
        lab_infer = MathTex(r"(1-\phi)K", font_size=36, color=C_INFER).next_to(
            infer, LEFT, buff=0.3
        )
        t_train = Text("training", font_size=24, color=C_TRAIN).next_to(
            train, RIGHT, buff=0.25
        )
        t_infer = Text("inference", font_size=24, color=C_INFER).next_to(
            infer, RIGHT, buff=0.25
        )
        with self.voiceover(
            "Here is the paper's distinctive ingredient. The firm splits its"
            " installed capacity: a fraction phi of K goes to training, and"
            " the remaining one minus phi serves inference. Both uses draw on"
            " the same scarce GPUs."
        ):
            self.play(
                LaggedStart(
                    GrowFromEdge(infer, DOWN),
                    GrowFromEdge(train, DOWN),
                    lag_ratio=0.4,
                ),
                run_time=1.5,
            )
            self.play(
                FadeIn(lab_train),
                FadeIn(lab_infer),
                FadeIn(t_train),
                FadeIn(t_infer),
                run_time=1.0,
            )

        rev_l = MathTex(
            r"\pi^L(X) = X \cdot \left[(1-\phi)K\right]^{\alpha}",
            font_size=40,
        ).shift(RIGHT * 1.9 + UP * 0.4)
        rev_l[0][0:2].set_color(C_L)
        tag_l = Text("eq. revenue-L", font_size=18, color=C_FAINT).next_to(
            rev_l, RIGHT, buff=0.4
        )
        with self.voiceover(
            "Revenue depends on the regime. In the low regime, equation"
            " revenue L: flow revenue is X times inference capacity, one"
            " minus phi times K, raised to the power alpha. Before AGI, you"
            " earn by serving today's demand."
        ):
            self.play(Write(rev_l), FadeIn(tag_l), run_time=1.5)

        rev_h = MathTex(
            r"\pi^H(X) = X \cdot (\phi K)^{\alpha}",
            font_size=40,
        ).next_to(rev_l, DOWN, buff=0.7, aligned_edge=LEFT)
        rev_h[0][0:2].set_color(C_H)
        tag_h = Text("eq. revenue-H", font_size=18, color=C_FAINT).next_to(
            rev_h, RIGHT, buff=0.4
        )
        with self.voiceover(
            "In the high regime, equation revenue H: flow revenue is X times"
            " training compute, phi K, to the same power alpha. After AGI,"
            " the quality of your models determines your position."
        ):
            self.play(Write(rev_h), FadeIn(tag_h), run_time=1.5)

        asym = MathTex(
            r"\phi = 0\text{: maximal revenue today, zero revenue in } H",
            font_size=25,
            color=C_TEXT,
        ).to_edge(DOWN, buff=0.45)
        with self.voiceover(
            "Notice the asymmetry: phi enters the two regimes with opposite"
            " signs. A firm at phi equal to zero earns the most today but"
            " exactly nothing after the switch; a firm at phi equal to one"
            " bets everything on the breakthrough."
        ):
            self.play(FadeIn(asym), run_time=1.2)
        self.pause(0.3)
        self.clear_body()

        alpha_eq = MathTex(
            r"\alpha \in (0,1),",
            r"\quad \alpha = 0.40 \text{ at baseline}",
            font_size=40,
        ).shift(UP * 1.4)
        scaling = Text(
            "scaling laws (Kaplan et al. 2020; Hoffmann et al. 2022):"
            " capability is a power law in compute",
            font_size=23,
            color=C_FAINT,
        ).next_to(alpha_eq, DOWN, buff=0.35)
        with self.voiceover(
            "The exponent alpha lies strictly between zero and one, and is"
            " calibrated to the scaling law literature, Kaplan and"
            " co-authors and Hoffmann and co-authors: capability is a power"
            " law in compute, so doubling compute does not double revenue."
            " At baseline, alpha is zero point four."
        ):
            self.play(Write(alpha_eq), run_time=1.2)
            self.play(FadeIn(scaling), run_time=0.8)

        distinct = VGroup(
            MathTex(
                r"\alpha: \text{ diminishing returns in revenue}",
                font_size=34,
                color=C_DEMAND,
            ),
            MathTex(
                r"\gamma: \text{ convexity in investment cost}",
                font_size=34,
                color=C_COST,
            ),
        ).arrange(DOWN, buff=0.3, aligned_edge=LEFT)
        distinct.next_to(scaling, DOWN, buff=0.6)
        with self.voiceover(
            "Keep alpha and gamma apart in your head: alpha is diminishing"
            " returns on the revenue side, gamma is convexity on the cost"
            " side. They are distinct parameters playing distinct roles, and"
            " they enter every later formula differently."
        ):
            self.play(FadeIn(distinct[0]), run_time=0.8)
            self.play(FadeIn(distinct[1]), run_time=0.8)

        fixed = MathTex(
            r"\phi \text{ is chosen at investment time and fixed thereafter}",
            font_size=24,
            color=C_FAINT,
        ).to_edge(DOWN, buff=0.5)
        with self.voiceover(
            "One last rule: phi is chosen once, at the moment of investment,"
            " and fixed thereafter. Letting it vary would turn phi into a"
            " second state variable in the HJB equation; the static choice"
            " already carries all the economics we need."
        ):
            self.play(FadeIn(fixed), run_time=1.0)
        self.pause(0.4)
        self.clear_body()


class P1S06Perpetuity(PaperScene):
    def construct(self):
        self.set_header("Toolkit 1: the growing perpetuity", kicker="TOOLKIT")

        l1 = MathTex(
            r"\text{PV}(X) = \mathbb{E}\!\left[\int_0^\infty e^{-rt}"
            r" X_t\,dt \,\middle|\, X_0 = X\right]",
            font_size=36,
        )
        l2 = MathTex(
            r"X_t = X \exp\!\left(\left(\mu - \tfrac{1}{2}\sigma^2\right)t"
            r" + \sigma W_t\right)",
            font_size=36,
        )
        l3 = MathTex(
            r"\mathbb{E}[X_t]"
            r" = X e^{(\mu - \frac{1}{2}\sigma^2)t}\,"
            r"\mathbb{E}\!\left[e^{\sigma W_t}\right]",
            r" = X e^{(\mu - \frac{1}{2}\sigma^2)t}\,"
            r"e^{\frac{1}{2}\sigma^2 t}",
            r" = X e^{\mu t}",
            font_size=36,
        )
        l4 = MathTex(
            r"\text{PV}(X) = \int_0^\infty e^{-rt}\, X e^{\mu t}\,dt",
            r" = X \int_0^\infty e^{-(r - \mu)t}\,dt",
            font_size=36,
        )
        l5 = MathTex(
            r"\text{PV}(X) = \frac{X}{r - \mu}",
            r"\qquad \text{provided } r > \mu",
            font_size=38,
        )
        lines = VGroup(l1, l2, l3, l4, l5).arrange(DOWN, buff=0.42)
        lines.to_edge(UP, buff=1.35)

        with self.voiceover(
            "Time for the toolkit: three small results we will use over and"
            " over. First, the growing perpetuity, the present value of the"
            " demand flow itself."
        ):
            self.pause(0.2)
        with self.voiceover(
            "We want the expected discounted integral of X from now to"
            " forever, starting from level X and discounting at rate r."
        ):
            self.play(Write(l1), run_time=1.5)
        with self.voiceover(
            "The geometric Brownian motion has an explicit solution: X t"
            " equals X times the exponential of mu minus one half sigma"
            " squared, times t, plus sigma W t."
        ):
            self.play(Write(l2), run_time=1.4)
        with self.voiceover(
            "Take expectations. W t is normal with variance t, so the"
            " expectation of e to the sigma W t is e to the one half sigma"
            " squared t, the lognormal mean."
        ):
            self.play(Write(l3[0]), run_time=1.2)
            self.play(Write(l3[1]), run_time=1.0)
        with self.voiceover(
            "The two sigma terms cancel exactly, leaving the expected level X"
            " e to the mu t. Volatility drops out of the expected path."
        ):
            self.play(Write(l3[2]), run_time=0.8)
            self.play(Create(highlight(l3[2])), run_time=0.6)
        with self.voiceover(
            "Now swap the expectation and the time integral, which Tonelli's"
            " theorem licenses because the integrand is positive. What"
            " remains is an elementary integral of e to the minus, r minus"
            " mu, times t."
        ):
            self.play(Write(l4), run_time=1.5)
        with self.voiceover(
            "If r is greater than mu, the integral converges to one over r"
            " minus mu, so the present value is X over r minus mu. If r were"
            " less than or equal to mu, it would diverge: that is exactly why"
            " the environment imposed r greater than mu H."
        ):
            self.play(Write(l5), run_time=1.4)
            self.play(Create(highlight(l5[0])), run_time=0.6)

        ah = MathTex(
            r"A_H \equiv \frac{1}{r - \mu_H}",
            font_size=36,
            color=C_H,
        ).to_edge(DOWN, buff=0.4)
        with self.voiceover(
            "In the paper this constant appears as A H, one over r minus mu"
            " H: the H regime perpetuity multiplier that converts a unit"
            " revenue flow into a stock of value."
        ):
            self.play(Write(ah), run_time=1.2)
        self.pause(0.4)
        self.clear_body()


class P1S07Characteristic(PaperScene):
    def construct(self):
        self.set_header("Toolkit 2: the characteristic equation", kicker="TOOLKIT")

        l1 = MathTex(
            r"\tfrac{1}{2}\sigma^2 X^2 F''(X) + \mu X F'(X) - \rho F(X) = 0",
            font_size=38,
        )
        l2 = MathTex(
            r"\text{guess } F(X) = X^{\beta}:",
            r"\quad F' = \beta X^{\beta - 1},",
            r"\quad F'' = \beta(\beta - 1) X^{\beta - 2}",
            font_size=36,
        )
        l3 = MathTex(
            r"\tfrac{1}{2}\sigma^2 \beta(\beta - 1) X^{\beta}"
            r" + \mu \beta X^{\beta} - \rho X^{\beta} = 0",
            font_size=38,
        )
        l4 = MathTex(
            r"Q(\beta) \equiv \tfrac{1}{2}\sigma^2 \beta(\beta - 1)"
            r" + \mu \beta - \rho = 0",
            font_size=40,
        )
        lines = VGroup(l1, l2, l3, l4).arrange(DOWN, buff=0.5)
        lines.to_edge(UP, buff=1.5)

        with self.voiceover(
            "Tool number two is the engine behind every option value in the"
            " paper. Whenever the firm is waiting, the value of waiting"
            " solves a homogeneous ODE of this form, where rho stands for"
            " whatever effective discount rate applies."
        ):
            self.play(Write(l1), run_time=1.6)
        with self.voiceover(
            "Try a power function: F of X equals X to the beta. Then F prime"
            " is beta X to the beta minus one, and F double prime is beta"
            " times beta minus one, times X to the beta minus two."
        ):
            self.play(Write(l2), run_time=1.6)
        with self.voiceover(
            "Substitute. Every term is proportional to X to the beta: the X"
            " squared in front of F double prime exactly restores the two"
            " powers lost by differentiating twice. That is why the guess"
            " works: this is an Euler equation."
        ):
            self.play(Write(l3), run_time=1.5)
        with self.voiceover(
            "Divide through by X to the beta, which is positive, and the"
            " differential equation collapses to algebra: the quadratic Q of"
            " beta equals zero. This is the characteristic equation."
        ):
            self.play(Write(l4), run_time=1.4)
            self.play(Create(highlight(l4)), run_time=0.6)
        self.pause(0.3)
        self.clear_body()

        # Parabola drawn with H-regime baseline numbers.
        from ai_lab_investment.models.parameters import ModelParameters

        p = ModelParameters()
        sig, mu_h, r = p.sigma, p.mu_H, p.r
        a_coef = 0.5 * sig**2

        def q_h(b: float) -> float:
            return a_coef * b * (b - 1) + mu_h * b - r

        beta_pos = p.beta_H
        beta_neg = -r / (a_coef * beta_pos)  # product of roots = -rho / a

        ax = clean_axes(
            x_range=[-3.6, 3.6], y_range=[-0.2, 0.36], width=6.4, height=4.2
        ).shift(LEFT * 3.1 + DOWN * 0.7)
        b_vals = np.linspace(-3.4, 3.3, 200)
        curve = ax.plot_line_graph(
            b_vals,
            np.array([q_h(b) for b in b_vals]),
            line_color=C_OPTION,
            add_vertex_dots=False,
        )
        b_axis_lab = MathTex(r"\beta", font_size=28, color=C_FAINT).next_to(
            ax.coords_to_point(3.6, 0), RIGHT, buff=0.15
        )
        with self.voiceover(
            "Look at the shape of Q, drawn here with the H regime baseline"
            " numbers. The leading coefficient, one half sigma squared, is"
            " positive, so the parabola opens upward."
        ):
            self.play(Create(ax), FadeIn(b_axis_lab), run_time=0.9)
            self.play(Create(curve), run_time=1.6)

        d0 = Dot(ax.coords_to_point(0, q_h(0)), color=C_COST)
        d0_lab = MathTex(r"Q(0) = -\rho < 0", font_size=28, color=C_COST).next_to(
            d0, DOWN + RIGHT, buff=0.18
        )
        dn = Dot(ax.coords_to_point(beta_neg, 0), color=C_TEXT)
        dn_lab = MathTex(r"\beta^- < 0", font_size=28).next_to(
            dn, UP + RIGHT, buff=0.15
        )
        dp = Dot(ax.coords_to_point(beta_pos, 0), color=C_OPTION)
        dp_lab = MathTex(r"\beta^+ > 1", font_size=28, color=C_OPTION).next_to(
            dp, UP + LEFT, buff=0.15
        )
        with self.voiceover(
            "At beta equal to zero, Q is minus rho, which is negative. An"
            " upward parabola that is negative at zero must cross the axis"
            " once on each side: one negative root and one positive root."
        ):
            self.play(FadeIn(d0, scale=2), FadeIn(d0_lab), run_time=0.9)
            self.play(
                FadeIn(dn, scale=2),
                FadeIn(dn_lab),
                FadeIn(dp, scale=2),
                FadeIn(dp_lab),
                run_time=1.0,
            )

        d1 = Dot(ax.coords_to_point(1, q_h(1)), color=C_DEMAND)
        d1_lab = MathTex(
            r"Q(1) = \mu - \rho < 0", font_size=28, color=C_DEMAND
        ).next_to(d1, RIGHT, buff=0.25)
        with self.voiceover(
            "Now evaluate at beta equal to one: Q of one is mu minus rho."
            " Whenever the discount rate exceeds the drift, this is still"
            " negative, so the positive root lies strictly to the right of"
            " one. That is what makes the option markup, beta over beta minus"
            " one, finite and greater than one."
        ):
            self.play(FadeIn(d1, scale=2), FadeIn(d1_lab), run_time=1.0)

        num_h = MathTex(
            r"\text{H: } \mu = \mu_H = 0.06,\ \rho = r = 0.12",
            r"\\ \Rightarrow\ \beta_H \approx 1.55",
            font_size=34,
        )
        num_h.set_color(C_H)
        num_l = MathTex(
            r"\text{L: } \mu = \mu_L = 0.01,\ \rho = r + \lambda = 0.22",
            r"\\ \Rightarrow\ \beta_L^+ \approx 3.01",
            font_size=34,
        )
        num_l.set_color(C_L)
        nums = VGroup(num_h, num_l).arrange(DOWN, buff=0.6, aligned_edge=LEFT)
        nums.shift(RIGHT * 3.5 + DOWN * 0.6)
        with self.voiceover(
            "Now the baseline numbers. In regime H we discount at r, twelve"
            " percent, with drift mu H of six percent and sigma of twenty"
            " five percent: the positive root is beta H, approximately one"
            " point five five."
        ):
            self.play(Write(num_h), run_time=1.4)
        with self.voiceover(
            "In regime L, the regime switch will add lambda to the effective"
            " discount, as the next tool shows. With drift mu L of one"
            " percent and effective discount r plus lambda of twenty two"
            " percent, the positive root is beta L plus, approximately three"
            " point zero one. Heavier discounting and lower drift both push"
            " the root up."
        ):
            self.play(Write(num_l), run_time=1.4)
        self.pause(0.4)
        self.clear_body()


class P1S08RegimeHJB(PaperScene):
    def construct(self):
        self.set_header("Toolkit 3: the regime-switch HJB", kicker="TOOLKIT")

        l1 = MathTex(
            r"r F_L\,dt = \mathbb{E}[dF_L]",
            font_size=38,
        )
        l2 = MathTex(
            r"\mathbb{E}[dF_L] = \left(\mu_L X F_L'"
            r" + \tfrac{1}{2}\sigma^2 X^2 F_L''\right)dt",
            r" + \lambda\,dt\,\bigl[F_H(X) - F_L(X)\bigr]",
            font_size=34,
        )
        l3 = MathTex(
            r"\tfrac{1}{2}\sigma^2 X^2 F_L'' + \mu_L X F_L'"
            r" + \lambda\bigl[F_H(X) - F_L(X)\bigr] - r F_L = 0",
            font_size=36,
        )
        l4 = MathTex(
            r"\tfrac{1}{2}\sigma^2 X^2 F_L'' + \mu_L X F_L'",
            r"\;-\;(r + \lambda) F_L",
            r"\;+\;\lambda F_H(X)",
            r"\;=\;0",
            font_size=38,
        )
        lines = VGroup(l1, l2, l3, l4).arrange(DOWN, buff=0.48)
        lines.to_edge(UP, buff=1.4)

        with self.voiceover(
            "Tool number three: what a Poisson regime switch does to a"
            " Bellman equation. Take any value function F L that lives in"
            " regime L, such as the value of the not yet exercised"
            " investment option."
        ):
            self.pause(0.2)
        with self.voiceover(
            "Over a short interval d t, the required return on holding the"
            " claim, r F L d t, must equal its expected change."
        ):
            self.play(Write(l1), run_time=1.2)
        with self.voiceover(
            "The expected change has two pieces. Ito's lemma gives the"
            " diffusion part: drift mu L X F L prime, plus one half sigma"
            " squared X squared F L double prime, times d t."
        ):
            self.play(Write(l2[0]), run_time=1.4)
        with self.voiceover(
            "And with probability lambda d t the regime switches, so the"
            " value jumps from F L of X to F H of X: an extra expected gain"
            " of lambda d t times the jump."
        ):
            self.play(Write(l2[1]), run_time=1.2)
        with self.voiceover(
            "Collect terms and divide by d t. This is the HJB equation in"
            " regime L, with the coupling term lambda times F H minus F L:"
            " equation HJB L in the paper."
        ):
            self.play(Write(l3), run_time=1.5)
        with self.voiceover(
            "Now regroup, and the structure becomes transparent: the lambda F"
            " L piece joins the discounting, while the lambda F H piece moves"
            " to the end as a forcing term."
        ):
            self.play(Write(l4), run_time=1.5)

        box_disc = highlight(l4[1], color=C_OPTION)
        note_disc = MathTex(
            r"\text{effective discount } r + \lambda"
            r"\text{: regime } L \text{ `ends' at rate } \lambda",
            font_size=24,
            color=C_OPTION,
        ).to_edge(DOWN, buff=1.05)
        with self.voiceover(
            "First consequence: the effective discount rate is r plus"
            " lambda. While you sit in regime L, that world ends at rate"
            " lambda, so claims on it carry extra mortality. This is exactly"
            " where the L regime characteristic root beta L plus, with rho"
            " equal to r plus lambda, came from."
        ):
            self.play(Create(box_disc), FadeIn(note_disc), run_time=1.2)

        box_force = highlight(l4[2], color=C_H)
        note_force = MathTex(
            r"\text{coupling } \lambda F_H"
            r"\text{: the switch pays the } H\text{-regime value}",
            font_size=24,
            color=C_H,
        ).next_to(note_disc, DOWN, buff=0.2)
        with self.voiceover(
            "Second consequence: ending is not losing. When the switch hits,"
            " you collect F H. Since F H is proportional to X to the beta H,"
            " this forcing term generates a particular solution proportional"
            " to X to the beta H, on top of the homogeneous powers."
        ):
            self.play(Create(box_force), FadeIn(note_force), run_time=1.2)

        with self.voiceover(
            "That is the whole recipe for the pre AGI option value: take the"
            " homogeneous roots from the characteristic equation at rho equal"
            " to r plus lambda, then add one particular term inherited from"
            " regime H. Parts two and three put this machine to work in"
            " full."
        ):
            self.pause(0.2)
        self.pause(0.4)
        self.clear_body()


class P1S09Assumptions(PaperScene):
    def construct(self):
        self.set_header("Assumption 1: admissibility", kicker="ASSUMPTIONS")

        def row(math_str: str, note_str: str, fs: int = 30) -> VGroup:
            math = MathTex(math_str, font_size=fs)
            note = Text(note_str, font_size=21, color=C_FAINT)
            return VGroup(math, note).arrange(DOWN, aligned_edge=LEFT, buff=0.1)

        a1 = row(
            r"\text{(A1)}\quad r > \mu_H > \mu_L \geq 0,\ \sigma > 0,"
            r"\ \alpha \in (0,1),\ \gamma > 1,\ c > 0,\ \delta \geq 0,"
            r"\ \lambda > 0",
            "housekeeping: convergence, diminishing returns, convex costs",
        )
        a2 = row(
            r"\text{(A2)}\quad \frac{1}{\gamma}"
            r" < \frac{\beta_H - 1}{\alpha\beta_H} < 1",
            "option premium condition: interior capacity K in regime H",
        )
        a3 = row(
            r"\text{(A3)}\quad \frac{1 - 1/\beta_L^+}{\alpha} \geq 1",
            "L-regime insufficiency: simplified option value F_L = C X^beta_H is exact",
        )
        a4 = row(
            r"\text{(A4)}\quad A_{\text{eff}}(\phi, K)"
            r" \text{ twice continuously differentiable in } \phi \in (0,1)",
            "smoothness: first-order conditions and concavity arguments valid",
        )
        rows = VGroup(a1, a2, a3, a4).arrange(DOWN, aligned_edge=LEFT, buff=0.34)
        rows.to_edge(LEFT, buff=0.85).shift(DOWN * 0.25)

        with self.voiceover(
            "The last piece of setup is Assumption one: four admissibility"
            " conditions maintained throughout the paper. Let us read them"
            " one at a time, because each has a specific job."
        ):
            self.pause(0.2)
        with self.voiceover(
            "A one is housekeeping: the drift ordering and convergence"
            " condition we already met, positive volatility, alpha strictly"
            " between zero and one, gamma above one, positive unit cost, non"
            " negative operating cost, and a positive arrival rate."
        ):
            self.play(FadeIn(a1, shift=RIGHT * 0.2), run_time=1.1)
        with self.voiceover(
            "A two is the option premium condition: the markup adjusted"
            " payout share, beta H minus one over alpha beta H, must sit"
            " strictly between one over gamma and one. The lower bound keeps"
            " optimal capacity finite, the upper bound keeps it positive:"
            " together they guarantee an interior K in regime H."
        ):
            self.play(FadeIn(a2, shift=RIGHT * 0.2), run_time=1.1)
        with self.voiceover(
            "A three is L regime insufficiency: one minus one over beta L"
            " plus, divided by alpha, is at least one. Economically,"
            " inference revenue in the pre AGI world is never, on its own,"
            " enough to justify the irreversible investment."
        ):
            self.play(FadeIn(a3, shift=RIGHT * 0.2), run_time=1.1)
        with self.voiceover(
            "Its payoff is mathematical: the autonomous L regime option is"
            " never exercised, so the homogeneous coefficient is exactly"
            " zero, and the option value collapses to C times X to the beta"
            " H. The firm can still invest in regime L, but only because A"
            " effective includes the H regime prospect. We prove the"
            " zero coefficient claim rigorously in part three."
        ):
            self.play(Create(highlight(a3, buff=0.1)), run_time=0.8)
        with self.voiceover(
            "A four is pure smoothness: A effective is twice continuously"
            " differentiable in phi, so first order conditions and second"
            " derivative arguments are legitimate."
        ):
            self.play(FadeIn(a4, shift=RIGHT * 0.2), run_time=1.1)

        check = MathTex(
            r"\text{baseline: } \frac{1}{\gamma} = 0.67"
            r" < \frac{\beta_H - 1}{\alpha\beta_H} \approx 0.89 < 1,",
            r"\qquad \frac{1 - 1/\beta_L^+}{\alpha} \approx 1.67 \geq 1",
            font_size=32,
            color=C_OPTION,
        ).to_edge(DOWN, buff=0.4)
        with self.voiceover(
            "All four hold at the baseline calibration, with room to spare:"
            " the A two ratio is about zero point eight nine, between zero"
            " point six seven and one, and the A three ratio is about one"
            " point six seven, comfortably above one. The paper verifies all"
            " four at every parameter value it uses."
        ):
            self.play(Write(check), run_time=1.6)
        self.pause(0.4)
        self.clear_body()


class P1S10Recap(PaperScene):
    def construct(self):
        self.set_header("Baseline calibration", kicker="RECAP")

        def col(title: str, color, *rows_tex: str) -> VGroup:
            head = Text(title, font_size=22, color=color)
            items = [MathTex(s, font_size=32) for s in rows_tex]
            return VGroup(head, *items).arrange(DOWN, buff=0.3, aligned_edge=LEFT)

        col_a = col(
            "growth and risk",
            C_L,
            r"\mu_L = 0.01",
            r"\mu_H = 0.06",
            r"\sigma = 0.25",
            r"r = 0.12 \text{ (WACC)}",
        )
        col_b = col(
            "beliefs and technology",
            C_TRAIN,
            r"\lambda = 0.10",
            r"\alpha = 0.40",
            r"\gamma = 1.50",
            r"\delta = 0.03",
            r"c = 1.00",
        )
        col_c = col(
            "derived roots",
            C_OPTION,
            r"\beta_H \approx 1.55",
            r"\beta_L^+ \approx 3.01",
        )
        table = VGroup(col_a, col_b, col_c).arrange(RIGHT, buff=1.1, aligned_edge=UP)
        table.shift(DOWN * 0.45)

        with self.voiceover(
            "Let us close with the numbers we will carry through the entire"
            " series: the baseline calibration."
        ):
            self.pause(0.2)
        with self.voiceover(
            "Growth and risk: pre AGI drift of one percent, post AGI drift of"
            " six percent, volatility of twenty five percent, and a weighted"
            " average cost of capital of twelve percent. Check the ordering:"
            " r greater than mu H greater than mu L holds."
        ):
            self.play(FadeIn(col_a, shift=UP * 0.2), run_time=1.2)
        with self.voiceover(
            "Beliefs and technology: lambda of zero point one, an expected"
            " ten years to the breakthrough; alpha of zero point four from"
            " the scaling laws; cost convexity gamma of one point five;"
            " operating cost delta of three percent; and unit cost c"
            " normalized to one."
        ):
            self.play(FadeIn(col_b, shift=UP * 0.2), run_time=1.2)
        with self.voiceover(
            "And the two roots we derived with the toolkit: beta H of about"
            " one point five five for the H regime, and beta L plus of about"
            " three point zero one for the L regime with switching."
        ):
            self.play(FadeIn(col_c, shift=UP * 0.2), run_time=1.2)
        self.pause(0.4)
        self.clear_body()

        nxt = Text(
            "Next - Part 2: The single-firm benchmark",
            font_size=34,
            color=C_OPTION,
            weight="BOLD",
        ).shift(UP * 1.0)
        bullets = VGroup(
            MathTex(
                r"\text{installed values } V_H \text{ and } V_L"
                r"\text{, and } A_{\text{eff}}",
                font_size=26,
            ),
            MathTex(
                r"\text{the } H\text{-regime option and smooth pasting}",
                font_size=26,
            ),
            MathTex(
                r"\text{Proposition 1: trigger } X^*\text{, capacity } K^*"
                r"\text{, training fraction } \phi^*",
                font_size=26,
            ),
        ).arrange(DOWN, buff=0.32, aligned_edge=LEFT)
        bullets.next_to(nxt, DOWN, buff=0.55)
        with self.voiceover(
            "That completes the environment and the toolkit. In part two we"
            " solve the single firm benchmark: the installed values in each"
            " regime, the H regime option with smooth pasting, and the joint"
            " choice of trigger, capacity, and training fraction."
        ):
            self.play(FadeIn(nxt), run_time=1.0)
            self.play(
                LaggedStart(
                    *[FadeIn(b, shift=RIGHT * 0.2) for b in bullets],
                    lag_ratio=0.25,
                ),
                run_time=1.6,
            )
        with self.voiceover(
            "That is Proposition one, and we will prove every line of it."
            " See you there."
        ):
            self.pause(0.2)
        self.pause(0.6)
        self.play(FadeOut(nxt), FadeOut(bullets), run_time=0.7)
