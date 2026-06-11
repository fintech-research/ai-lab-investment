"""Walkthrough Part 4 (~20-25 min): Duopoly, Debt, and Default.

Derivation-level walkthrough of the paper's duopoly-with-default-risk
section (paper/_model.qmd) and the proof of Proposition 2
(paper/_appendix.qmd), including the coupled default-boundary analysis
of Appendix B. Audience: the paper's author, reviewing every step.

Render: uv run python video/render.py walkthrough_part4
Draft a single scene:
    cd video && uv run manim render -ql walkthrough_part4.py P4S01Title
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
    Polygon,
    Text,
    VGroup,
    Write,
)
from scene_base import PaperScene
from theme import (
    BASELINE,
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
    "P4S01Title",
    "P4S02Recap",
    "P4S03Contests",
    "P4S04ContestProperties",
    "P4S05EffectiveCoefficient",
    "P4S06CapitalStructure",
    "P4S07LelandBoundary",
    "P4S08OneWayCoupling",
    "P4S09LeverageStatics",
    "P4S10FaithCondition",
    "P4S11MarkupChannel",
    "P4S12ExactThreshold",
    "P4S13SignAtOptimum",
    "P4S14SubstitutionAndRival",
    "P4S15EquityDebt",
    "P4S16BoundariesFigure",
    "P4S17Close",
]


class P4S01Title(PaperScene):
    def construct(self):
        part = Text("WALKTHROUGH - PART 4", font_size=26, color=C_OPTION)
        title = Text("Duopoly, Debt, and Default", font_size=52, weight="BOLD")
        sub = Text("the faith-based survival proof", font_size=30, color=C_FAINT)
        group = VGroup(part, title, sub).arrange(DOWN, buff=0.45)

        with self.voiceover(
            "Part four. This is the densest part of the series: we take the"
            " single-firm machinery from the earlier parts and add the two"
            " ingredients that make the model speak to credit markets."
        ):
            self.play(FadeIn(part), run_time=0.8)
            self.play(Write(title), run_time=1.8)

        with self.voiceover(
            "A rival, and debt. By the end we will have proved Proposition two,"
            " faith-based survival, with every algebraic step on screen."
        ):
            self.play(FadeIn(sub), run_time=1.0)
        self.pause(0.8)
        self.play(FadeOut(group), run_time=0.7)


class P4S02Recap(PaperScene):
    def construct(self):
        self.set_header("Where we are", kicker="RECAP")

        rec1 = MathTex(
            r"dX_t = \mu_s X_t\,dt + \sigma X_t\,dW_t,"
            r"\qquad \Pr(L \to H \text{ in } dt) = \lambda\,dt",
            font_size=34,
        )
        rec2 = MathTex(
            r"A_{\text{eff}} = \frac{[(1-\phi)K]^{\alpha}}{r-\mu_L+\lambda}"
            r" + \frac{\lambda}{r-\mu_L+\lambda}\cdot"
            r"\frac{(\phi K)^{\alpha}}{r-\mu_H}",
            font_size=34,
        )
        rec3 = MathTex(
            r"X^* = \frac{\beta_H}{\beta_H-1}\cdot"
            r"\frac{\delta K^*/r + I(K^*)}{A_{\text{eff}}},"
            r"\qquad \left(\frac{\phi^*}{1-\phi^*}\right)^{1-\alpha}"
            r" = \frac{\lambda}{r-\mu_H}",
            font_size=34,
        )
        VGroup(rec1, rec2, rec3).arrange(DOWN, buff=0.55).shift(DOWN * 0.4)

        with self.voiceover(
            "A quick recap of what we already have. Demand follows a geometric"
            " Brownian motion, and an absorbing regime switch from L to H"
            " arrives at Poisson rate lambda."
        ):
            self.play(Write(rec1), run_time=1.6)
        with self.voiceover(
            "An installed firm is worth A effective times demand, where"
            " A effective capitalizes inference revenue today plus the"
            " lambda-weighted post-switch training payoff."
        ):
            self.play(Write(rec2), run_time=1.8)
        with self.voiceover(
            "And the single firm invests at a closed-form trigger, with the"
            " training fraction phi star pinned down by beliefs: about seventy"
            " percent at the baseline lambda of zero point one."
        ):
            self.play(Write(rec3), run_time=1.8)
        self.pause(0.4)
        self.clear_body()

        items = VGroup(
            Text("1.  Tullock contests, one per regime", font_size=27),
            Text("2.  The duopoly A effective", font_size=27),
            Text("3.  Debt issued at par below the discount rate", font_size=27),
            Text("4.  The Leland default boundary, derived in full", font_size=27),
            Text("5.  The one-way coupling and its 3 percent bias", font_size=27),
            Text("6.  Proposition 2, parts (i) through (iv)", font_size=27),
            Text("7.  Equity, debt, and recovery values", font_size=27),
            Text("8.  Leverage and the margin of safety", font_size=27),
        ).arrange(DOWN, buff=0.32, aligned_edge=LEFT)
        items.shift(DOWN * 0.4)

        with self.voiceover(
            "Here is the route for this part. We build the duopoly contest"
            " structure, fold it into A effective, and add a debt layer."
        ):
            self.play(
                FadeIn(items[0], shift=RIGHT * 0.3),
                FadeIn(items[1], shift=RIGHT * 0.3),
                FadeIn(items[2], shift=RIGHT * 0.3),
                run_time=1.5,
            )
        with self.voiceover(
            "Then we derive the default boundary the Leland way, check the"
            " approximation hiding inside it, and prove all four parts of"
            " Proposition two."
        ):
            self.play(
                FadeIn(items[3], shift=RIGHT * 0.3),
                FadeIn(items[4], shift=RIGHT * 0.3),
                FadeIn(items[5], shift=RIGHT * 0.3),
                run_time=1.5,
            )
        with self.voiceover(
            "We close with the equity and debt claims, the recovery"
            " specification, and the leverage figure from the paper."
        ):
            self.play(
                FadeIn(items[6], shift=RIGHT * 0.3),
                FadeIn(items[7], shift=RIGHT * 0.3),
                run_time=1.2,
            )
        self.pause(0.5)
        self.clear_body()


class P4S03Contests(PaperScene):
    def construct(self):
        self.set_header("Regime-specific Tullock contests", kicker="MODEL")

        eq_l = MathTex(
            r"\pi_i^L",
            r"=",
            r"X\cdot\frac{[(1-\phi_i)K_i]^{2\alpha}}"
            r"{[(1-\phi_i)K_i]^{\alpha}+[(1-\phi_j)K_j]^{\alpha}}",
            font_size=38,
        ).to_edge(UP, buff=1.5)
        eq_l[0].set_color(C_INFER)

        with self.voiceover(
            "Now add the rival. In the low regime, the two firms compete over"
            " inference capacity through a Tullock contest: revenue depends on"
            " relative capacity, not just your own."
        ):
            self.play(Write(eq_l), run_time=2.0)

        ydef = MathTex(
            r"y_i \equiv [(1-\phi_i)K_i]^{\alpha}",
            font_size=36,
            color=C_INFER,
        ).next_to(eq_l, DOWN, buff=0.55)
        with self.voiceover(
            "To see the structure, write y i for firm i's inference measure:"
            " inference capacity raised to the scaling exponent alpha."
        ):
            self.play(Write(ydef), run_time=1.2)

        rew = MathTex(
            r"\pi_i^L = X\,\frac{y_i^2}{y_i+y_j}",
            r"= X\, y_i \cdot s_i^L,",
            r"\qquad s_i^L \equiv \frac{y_i}{y_i+y_j}",
            font_size=38,
        ).next_to(ydef, DOWN, buff=0.55)
        rew[2].set_color(C_FAINT)
        with self.voiceover(
            "Then the contest payoff is X times y i squared over y i plus y j,"
            " which factors as standalone revenue times the contest share s i:"
            " your own y, scaled by your share of total y."
        ):
            self.play(Write(rew), run_time=2.0)

        eq_h = MathTex(
            r"\pi_i^H = X\cdot\frac{(\phi_i K_i)^{2\alpha}}"
            r"{(\phi_i K_i)^{\alpha}+(\phi_j K_j)^{\alpha}}"
            r" = X\,(\phi_i K_i)^{\alpha}\, s_i^H",
            font_size=36,
        ).next_to(rew, DOWN, buff=0.55)
        eq_h.set_color(C_H)
        with self.voiceover(
            "The high regime has the same form over training compute: after"
            " the switch, model quality decides market share, so the contest"
            " runs over phi K instead of one minus phi K."
        ):
            self.play(Write(eq_h), run_time=1.8)

        single = MathTex(
            r"K_j = 0\ \Rightarrow\ s_i^L = s_i^H = 1"
            r"\ \Rightarrow\ \text{single-firm revenue}",
            font_size=32,
            color=C_FAINT,
        ).to_edge(DOWN, buff=0.5)
        with self.voiceover(
            "Sanity check: with no rival, both shares equal one and we recover"
            " the single-firm revenue functions exactly."
        ):
            self.play(Write(single), run_time=1.2)
        self.pause(0.4)
        self.clear_body()

        from ai_lab_investment.models.duopoly import DuopolyModel
        from ai_lab_investment.models.parameters import ModelParameters

        ratios = np.linspace(0.01, 4.0, 200)
        ax = clean_axes([0, 4], [0, 1.08], width=8.8, height=4.2).shift(DOWN * 0.9)
        x_lab = MathTex(r"K_i / K_j", font_size=30, color=C_FAINT).next_to(
            ax.x_axis, RIGHT, buff=0.2
        )
        y_lab = MathTex(r"s_i", font_size=30, color=C_FAINT).next_to(
            ax.y_axis, UP, buff=0.15
        )
        with self.voiceover(
            "The exponent alpha controls how sensitive the share is to"
            " relative capacity. Let us plot firm one's share against the"
            " capacity ratio, using the model's own contest functions."
        ):
            self.play(Create(ax), FadeIn(x_lab), FadeIn(y_lab), run_time=1.0)

        specs = [
            (0.10, C_DEMAND, r"\alpha = 0.1"),
            (0.40, C_L, r"\alpha = 0.4"),
            (0.90, C_TRAIN, r"\alpha = 0.9"),
        ]
        narrs = [
            "At alpha near zero the curve is almost flat at one half: shares"
            " split fifty-fifty regardless of capacity.",
            "At the calibrated alpha of zero point four, the share responds"
            " smoothly, with diminishing returns to capacity dominance.",
            "As alpha grows toward one, the curve steepens around the symmetric point.",
        ]
        for (a, col, lab), narr in zip(specs, narrs, strict=True):
            duo = DuopolyModel(ModelParameters(alpha=a))
            s_vals = np.array([duo.contest_share(float(k), 1.0) for k in ratios])
            curve = ax.plot_line_graph(
                ratios, s_vals, line_color=col, add_vertex_dots=False
            )
            tag = MathTex(lab, font_size=28, color=col).next_to(
                ax.coords_to_point(4.0, float(s_vals[-1])), RIGHT, buff=0.12
            )
            with self.voiceover(narr):
                self.play(Create(curve), FadeIn(tag), run_time=1.6)

        step = VGroup(
            DashedLine(
                ax.coords_to_point(0, 0.0),
                ax.coords_to_point(1, 0.0),
                color=C_FAINT,
            ),
            DashedLine(
                ax.coords_to_point(1, 0.0),
                ax.coords_to_point(1, 1.0),
                color=C_FAINT,
            ),
            DashedLine(
                ax.coords_to_point(1, 1.0),
                ax.coords_to_point(4, 1.0),
                color=C_FAINT,
            ),
        )
        dot = Dot(ax.coords_to_point(1, 0.5), color=C_OPTION)
        lim_lab = MathTex(
            r"\alpha \to \infty:\ \text{winner take all}",
            font_size=28,
            color=C_FAINT,
        ).move_to(ax.coords_to_point(2.6, 0.18))
        with self.voiceover(
            "In the limit as alpha goes to infinity, the share becomes a step"
            " function at the symmetric point: the larger firm captures the"
            " entire market. Alpha indexes the whole range from equal split"
            " to winner-take-all."
        ):
            self.play(Create(step), FadeIn(dot, scale=2), FadeIn(lim_lab), run_time=1.8)
        self.pause(0.5)
        self.clear_body()


class P4S04ContestProperties(PaperScene):
    def construct(self):
        self.set_header("Three properties, with proofs", kicker="MODEL")

        lab_a = Text("(a)  symmetry", font_size=26, color=C_OPTION)
        lab_a.to_edge(LEFT, buff=0.8).shift(UP * 1.9)
        a1 = MathTex(
            r"y_1 = y_2 = y\ \Rightarrow\ s_i = \frac{y}{2y} = \tfrac{1}{2}",
            font_size=36,
        ).next_to(lab_a, DOWN, buff=0.4, aligned_edge=LEFT)
        a2 = MathTex(
            r"\pi_1 + \pi_2 = X\,\frac{y^2 + y^2}{2y} = X\,y"
            r" = X\,[(1-\phi)K]^{\alpha}",
            font_size=36,
        ).next_to(a1, DOWN, buff=0.4, aligned_edge=LEFT)

        with self.voiceover(
            "Property a: symmetry. With equal capacities and equal training"
            " fractions, each y is the same, so each share is y over two y,"
            " exactly one half."
        ):
            self.play(FadeIn(lab_a), Write(a1), run_time=1.6)
        with self.voiceover(
            "Total industry revenue is then X times two y squared over two y,"
            " which collapses to X times the regime-relevant capacity to the"
            " alpha: the standard single-firm benchmark, now split in two."
        ):
            self.play(Write(a2), run_time=1.8)
        self.pause(0.4)
        self.clear_body()

        lab_b = Text("(b)  winner-take-more", font_size=26, color=C_OPTION)
        lab_b.to_edge(LEFT, buff=0.8).shift(UP * 2.3)
        b1 = MathTex(
            r"\pi_1 + \pi_2 = X\,\frac{y_1^2 + y_2^2}{y_1 + y_2}",
            r"\ \geq\ X\,\frac{y_1 + y_2}{2}",
            font_size=36,
        ).next_to(lab_b, DOWN, buff=0.45, aligned_edge=LEFT)
        b2 = MathTex(
            r"\Longleftrightarrow\quad 2\,(y_1^2 + y_2^2)\ \geq\ (y_1 + y_2)^2",
            font_size=36,
        ).next_to(b1, DOWN, buff=0.42, aligned_edge=LEFT)
        b3 = MathTex(
            r"2\,(y_1^2 + y_2^2) - (y_1 + y_2)^2",
            r"= y_1^2 - 2y_1y_2 + y_2^2",
            r"= (y_1 - y_2)^2 \geq 0",
            font_size=36,
        ).next_to(b2, DOWN, buff=0.42, aligned_edge=LEFT)
        b4 = MathTex(
            r"\text{with equality iff } y_1 = y_2",
            font_size=32,
            color=C_FAINT,
        ).next_to(b3, DOWN, buff=0.42, aligned_edge=LEFT)

        with self.voiceover(
            "Property b: under asymmetry, the contest inflates total revenue."
            " The claim is that X times the sum of squares over the sum is at"
            " least the symmetric benchmark, X times the average of the y's."
        ):
            self.play(FadeIn(lab_b), Write(b1), run_time=1.8)
        with self.voiceover(
            "Multiply both sides by two times the sum: the claim is equivalent"
            " to two times the sum of squares exceeding the square of the sum."
        ):
            self.play(Write(b2), run_time=1.4)
        with self.voiceover(
            "Expand the square of the sum and subtract: the difference is y one"
            " squared minus two y one y two plus y two squared, which is"
            " exactly y one minus y two, squared. Non-negative, always."
        ):
            self.play(Write(b3), run_time=2.0)
        box = highlight(b3[2], color=C_OPTION)
        with self.voiceover(
            "So the whole inequality is just a perfect square rearranged, and"
            " it binds with equality only in the symmetric case."
        ):
            self.play(Create(box), FadeIn(b4), run_time=1.2)
        with self.voiceover(
            "Economically: the quadratic mean beats the arithmetic mean, so"
            " asymmetry expands the pie. A dominant firm gains partly by"
            " stealing share and partly by growing total revenue, which can"
            " amplify preemption incentives; Appendix E quantifies this with"
            " a fixed-pie variant."
        ):
            self.play(Indicate(b1[0], color=C_OPTION), run_time=1.4)
        self.pause(0.4)
        self.clear_body()

        lab_c = Text(
            "(c)  regularity when alpha < 1  (Skaperdas 1996)",
            font_size=26,
            color=C_OPTION,
        )
        lab_c.to_edge(LEFT, buff=0.8).shift(UP * 1.8)
        bullets = VGroup(
            Text("- the contest equilibrium is unique", font_size=28),
            Text("- no over-dissipation of rents", font_size=28),
            Text(
                "- shares rise in own capacity, at diminishing rates",
                font_size=28,
            ),
        ).arrange(DOWN, buff=0.35, aligned_edge=LEFT)
        bullets.next_to(lab_c, DOWN, buff=0.5, aligned_edge=LEFT)

        with self.voiceover(
            "Property c: with alpha below one, the contest is regular in the"
            " sense of Skaperdas: the equilibrium is unique and firms do not"
            " dissipate more than the rents at stake."
        ):
            self.play(
                FadeIn(lab_c), FadeIn(bullets[0]), FadeIn(bullets[1]), run_time=1.6
            )
        with self.voiceover(
            "And comparative statics are well behaved: a larger capacity"
            " always increases your share, but with diminishing marginal"
            " returns. This is the regularity we lean on throughout."
        ):
            self.play(FadeIn(bullets[2]), run_time=1.0)
        self.pause(0.5)
        self.clear_body()


class P4S05EffectiveCoefficient(PaperScene):
    def construct(self):
        self.set_header("The duopoly A effective", kicker="MODEL")

        aeff = MathTex(
            r"A_{\text{eff},i}",
            r"=",
            r"\frac{[(1-\phi_i)K_i]^{\alpha}\, s_i^L}{r-\mu_L+\lambda}",
            r"+",
            r"\frac{\lambda}{r-\mu_L+\lambda}\cdot"
            r"\frac{(\phi_i K_i)^{\alpha}\, s_i^H}{r-\mu_H}",
            font_size=38,
        ).to_edge(UP, buff=1.5)
        aeff[2].set_color(C_INFER)
        aeff[4].set_color(C_H)

        with self.voiceover(
            "Folding the contests into the valuation gives the duopoly"
            " effective revenue coefficient: the same two-term structure as"
            " the single firm, with each term scaled by its own contest share."
        ):
            self.play(Write(aeff), run_time=2.2)
        with self.voiceover(
            "The first term is inference revenue in the current regime, scaled"
            " by the L share; the second is the lambda-weighted post-switch"
            " training payoff, scaled by the H share."
        ):
            self.play(Indicate(aeff[2], color=C_INFER), run_time=1.0)
            self.play(Indicate(aeff[4], color=C_H), run_time=1.0)

        val = MathTex(
            r"V_i^L(X) = A_{\text{eff},i}\, X - \frac{\delta K_i}{r}",
            font_size=38,
        ).next_to(aeff, DOWN, buff=0.7)
        with self.voiceover(
            "The installed value in the low regime is again linear in demand:"
            " A effective times X, minus the capitalized operating cost."
        ):
            self.play(Write(val), run_time=1.4)

        red = MathTex(
            r"K_j = 0\ \Rightarrow\ s_i^L = s_i^H = 1"
            r"\ \Rightarrow\ A_{\text{eff},i} = A_{\text{eff}}^{\text{single}}",
            font_size=34,
            color=C_FAINT,
        ).next_to(val, DOWN, buff=0.6)
        with self.voiceover(
            "When the rival's capacity is zero, both shares equal one and this"
            " reduces exactly to the single-firm A effective from part two."
        ):
            self.play(Write(red), run_time=1.4)

        strat = MathTex(
            r"\phi_i \uparrow\ :\quad s_i^L \downarrow\ ,\quad s_i^H \uparrow",
            font_size=38,
        ).next_to(red, DOWN, buff=0.6)
        strat.set_color(C_TRAIN)
        with self.voiceover(
            "The training fraction is now a strategic variable: raising phi"
            " weakens your inference position today and strengthens your"
            " training position after the switch. Both shares move at once."
        ):
            self.play(Write(strat), run_time=1.5)
        self.pause(0.5)
        self.clear_body()


class P4S06CapitalStructure(PaperScene):
    def construct(self):
        self.set_header("Capital structure", kicker="MODEL")

        l1 = MathTex(
            r"\ell = \frac{D_0}{I(K)}",
            r"\qquad\text{(exogenous, common to both firms)}",
            font_size=38,
        ).to_edge(UP, buff=1.5)
        l1[1].set_color(C_FAINT)
        l2 = MathTex(
            r"c_D = c_d \cdot \ell \cdot I(K),\qquad c_d < r",
            font_size=38,
        ).next_to(l1, DOWN, buff=0.5)

        with self.voiceover(
            "Now the debt layer. Each firm finances its investment with a"
            " mix of equity and debt, parameterized by the leverage ratio ell:"
            " face value of debt over the investment cost."
        ):
            self.play(Write(l1), run_time=1.6)
        with self.voiceover(
            "Debt is issued at par and pays a perpetual coupon: coupon rate"
            " c d times the face value. Crucially, c d is below the discount"
            " rate r: relationship lenders extend below-market terms."
        ):
            self.play(Write(l2), run_time=1.6)

        s1 = MathTex(
            r"\text{equity contributes: } (1-\ell)\, I(K)",
            font_size=34,
        )
        s2 = MathTex(
            r"\text{debt contributes: } \ell\, I(K)\ \text{(par issuance)}",
            font_size=34,
        )
        s3 = MathTex(
            r"\text{coupon liability: } \frac{c_D}{r}"
            r" = \frac{c_d}{r}\,\ell\, I(K)\ <\ \ell\, I(K)",
            font_size=34,
        )
        srcs = VGroup(s1, s2, s3).arrange(DOWN, buff=0.38, aligned_edge=LEFT)
        srcs.next_to(l2, DOWN, buff=0.55)

        with self.voiceover(
            "Let us derive what this convention does to the cost of capital."
            " Equity holders put in one minus ell times the investment cost,"
            " and debt holders put in the remaining ell times I of K."
        ):
            self.play(Write(s1), run_time=1.0)
            self.play(Write(s2), run_time=1.0)
        with self.voiceover(
            "But the liability the firm takes on is the present value of the"
            " perpetual coupon: c D over r, which is c d over r times ell I."
            " Since c d is below r, that is strictly less than what the debt"
            " raised."
        ):
            self.play(Write(s3), run_time=1.6)
        box3 = highlight(s3, color=C_OPTION)
        self.play(Create(box3), run_time=0.6)

        d1 = MathTex(
            r"\text{effective capital cost}",
            r"= (1-\ell)\,I(K) + \frac{c_d}{r}\,\ell\, I(K)",
            font_size=34,
        )
        d2 = MathTex(
            r"= I(K)\left[1 - \ell + \frac{c_d}{r}\,\ell\right]",
            font_size=34,
        )
        d3 = MathTex(
            r"= I(K)\left[1 - \ell\left(1 - \frac{c_d}{r}\right)\right]",
            font_size=34,
        )
        deriv = VGroup(d1, d2, d3).arrange(DOWN, buff=0.32, aligned_edge=LEFT)
        deriv.to_edge(DOWN, buff=0.45)

        with self.voiceover(
            "So the capital the equity holders effectively pay for is their"
            " own contribution plus the value of the coupon liability."
        ):
            self.play(FadeOut(l1), FadeOut(l2), run_time=0.5)
            self.play(VGroup(srcs, box3).animate.to_edge(UP, buff=1.3), run_time=0.6)
            self.play(Write(d1), run_time=1.4)
        with self.voiceover(
            "Factor out the investment cost, then group the ell terms: the"
            " effective capital cost is I of K times one minus ell times one"
            " minus c d over r."
        ):
            self.play(Write(d2), run_time=1.0)
            self.play(Write(d3), run_time=1.0)
        box = highlight(d3, color=C_OPTION)
        with self.voiceover(
            "At the baseline coupon of five percent against a twelve percent"
            " discount rate, forty percent leverage cuts the effective capital"
            " cost by about twenty-three percent. That is the financing"
            " concession embedded in par issuance."
        ):
            self.play(Create(box), run_time=0.8)
        self.pause(0.3)
        with self.voiceover(
            "Two consequences to keep in mind: cheaper debt-financed capital"
            " pushes firms toward larger scale and later entry, while the"
            " coupon obligation will raise the default boundary we derive"
            " next."
        ):
            self.play(Indicate(d3, color=C_OPTION), run_time=1.2)
        self.pause(0.4)
        self.clear_body()


class P4S07LelandBoundary(PaperScene):
    def construct(self):
        self.set_header("The default boundary: Leland derivation", kicker="MODEL")

        hat_def = MathTex(
            r"\hat{E}(X) \equiv E(X) + (1-\ell)\,I(K)",
            r"\qquad\text{(going-concern equity)}",
            font_size=34,
        ).to_edge(UP, buff=1.4)
        hat_def[1].set_color(C_FAINT)
        with self.voiceover(
            "Equity holders default endogenously when it is optimal to stop"
            " servicing the debt. The object that decides this is the"
            " going-concern equity: the market value of the claim after the"
            " investment is sunk."
        ):
            self.play(Write(hat_def), run_time=1.6)

        ode = MathTex(
            r"\tfrac{1}{2}\sigma^2 X^2 \hat{E}'' + \mu_L X \hat{E}'",
            r"- (r+\lambda)\,\hat{E}",
            r"+ \pi_i^L(X) - \delta K_i - c_D",
            r"+ \lambda\, E_H(X)",
            r"= 0",
            font_size=34,
        ).next_to(hat_def, DOWN, buff=0.55)
        ode[1].set_color(C_DEMAND)
        ode[3].set_color(C_H)
        with self.voiceover(
            "Above the default boundary, the going-concern equity satisfies"
            " the L-regime ordinary differential equation: diffusion and drift"
            " terms, discounting at the effective rate r plus lambda, the net"
            " cash flow after operating costs and coupons, and the"
            " regime-switch pickup lambda times the H-regime equity."
        ):
            self.play(Write(ode), run_time=2.4)
        with self.voiceover(
            "Note the coupling is one way: E H solves its own problem and"
            " feeds into this equation as a forcing term, but the L-regime"
            " equity never feeds back, because the switch is absorbing."
        ):
            self.play(Indicate(ode[3], color=C_H), run_time=1.2)

        part = MathTex(
            r"\hat{E}_p(X) = A_{\text{eff},i}\,X - \frac{c_D + \delta K_i}{r}",
            r"\equiv A_{\text{eff},i}\,X - N",
            font_size=36,
        ).next_to(ode, DOWN, buff=0.55)
        with self.voiceover(
            "Replace E H by its perpetuity component for now; the next scene"
            " makes that step precise. Matching coefficients on the linear"
            " and constant terms gives the particular solution: A effective"
            " times X, minus the capitalized coupon and operating costs,"
            " which I will call N."
        ):
            self.play(Write(part), run_time=2.0)

        char = MathTex(
            r"\tfrac{1}{2}\sigma^2\beta(\beta-1) + \mu_L\beta - (r+\lambda) = 0",
            r"\quad\Rightarrow\quad \beta_s^+ > 1,\ \ \beta_s^- < 0",
            font_size=34,
        ).next_to(part, DOWN, buff=0.5)
        char[1].set_color(C_DEFAULT)
        with self.voiceover(
            "The homogeneous solutions are powers of X, with exponents solving"
            " the characteristic quadratic at the effective discount rate r"
            " plus lambda. It has one root above one and one negative root,"
            " beta s minus."
        ):
            self.play(Write(char), run_time=1.8)

        gen = MathTex(
            r"\hat{E}(X) = A_{\text{eff},i}\,X - N",
            r"+ A_+ X^{\beta_s^+}",
            r"+ A_- X^{\beta_s^-}",
            font_size=36,
        ).to_edge(DOWN, buff=0.5)
        gen[1].set_color(C_FAINT)
        gen[2].set_color(C_DEFAULT)
        with self.voiceover(
            "So the general solution is the particular part plus the two"
            " homogeneous powers. As demand grows large, equity must approach"
            " its perpetuity value, so the explosive positive-root term is"
            " ruled out: A plus equals zero."
        ):
            self.play(Write(gen), run_time=1.8)
        strike = Line(
            gen[1].get_corner(DOWN + LEFT),
            gen[1].get_corner(UP + RIGHT),
            color=C_DEFAULT,
            stroke_width=4,
        )
        with self.voiceover(
            "What survives is the negative-root term: the default option,"
            " which matters near the boundary and vanishes at high demand."
        ):
            self.play(Create(strike), run_time=0.8)
        self.pause(0.4)
        self.clear_body()

        sol = MathTex(
            r"\hat{E}(X) = A_{\text{eff},i}\,X - N + A_- X^{\beta},"
            r"\qquad \beta \equiv \beta_s^- < 0",
            font_size=36,
        ).to_edge(UP, buff=1.4)
        with self.voiceover(
            "Here is the surviving solution, writing beta for the negative"
            " root to keep the algebra light. Two unknowns remain: the"
            " option coefficient A minus, and the boundary X D itself."
        ):
            self.play(Write(sol), run_time=1.6)

        bc = MathTex(
            r"\hat{E}(X_D) = 0",
            r"\qquad\text{(value matching)}",
            r"\qquad \hat{E}'(X_D) = 0",
            r"\qquad\text{(smooth pasting)}",
            font_size=34,
        ).next_to(sol, DOWN, buff=0.5)
        bc[1].set_color(C_FAINT)
        bc[3].set_color(C_FAINT)
        with self.voiceover(
            "Limited liability supplies the two boundary conditions. At the"
            " default boundary the going-concern equity is worth exactly zero,"
            " and because equity holders choose the boundary optimally, the"
            " value function pastes smoothly: its slope is also zero there."
        ):
            self.play(Write(bc), run_time=2.0)

        vm = MathTex(
            r"\text{(VM)}\quad",
            r"A_{\text{eff},i}\,X_D - N + A_- X_D^{\beta} = 0",
            font_size=34,
        )
        sp = MathTex(
            r"\text{(SP)}\quad",
            r"A_{\text{eff},i} + \beta\, A_- X_D^{\beta-1} = 0",
            font_size=34,
        )
        st1 = MathTex(
            r"\text{(SP)}\times \tfrac{X_D}{\beta}:\quad",
            r"A_- X_D^{\beta} = -\frac{A_{\text{eff},i}\,X_D}{\beta}",
            font_size=34,
        )
        st2 = MathTex(
            r"\text{into (VM)}:\quad",
            r"A_{\text{eff},i}\,X_D - N - \frac{A_{\text{eff},i}\,X_D}{\beta} = 0",
            font_size=34,
        )
        st3 = MathTex(
            r"A_{\text{eff},i}\,X_D\left(1 - \tfrac{1}{\beta}\right) = N",
            r"\quad\Longleftrightarrow\quad",
            r"A_{\text{eff},i}\,X_D\,\frac{\beta - 1}{\beta} = N",
            font_size=34,
        )
        steps = VGroup(vm, sp, st1, st2, st3).arrange(
            DOWN, buff=0.32, aligned_edge=LEFT
        )
        steps.next_to(bc, DOWN, buff=0.45)

        with self.voiceover(
            "Write the two conditions out: value matching, and smooth pasting."
        ):
            self.play(Write(vm), run_time=1.0)
            self.play(Write(sp), run_time=1.0)
        box_st1 = highlight(st1[1], color=C_OPTION)
        with self.voiceover(
            "Multiply smooth pasting by X D over beta: this isolates the"
            " option term, A minus times X D to the beta, as minus A effective"
            " X D over beta."
        ):
            self.play(Write(st1), run_time=1.4)
            self.play(Create(box_st1), run_time=0.5)
        with self.voiceover(
            "Substitute that into value matching: the option coefficient is"
            " gone, leaving a single equation in X D alone."
        ):
            self.play(Write(st2), run_time=1.4)
        with self.voiceover(
            "Factor A effective X D: one minus one over beta is beta minus one"
            " over beta."
        ):
            self.play(Write(st3), run_time=1.4)

        final = MathTex(
            r"X_D",
            r"= \frac{\beta_s^-}{\beta_s^- - 1}\cdot"
            r"\frac{c_D/r + \delta K_i/r}{A_{\text{eff},i}}",
            font_size=40,
        ).move_to(DOWN * 1.6)
        final[0].set_color(C_DEFAULT)
        with self.voiceover(
            "Solve for X D: the default boundary is beta over beta minus one,"
            " times the capitalized coupon and operating costs, divided by A"
            " effective. This is equation default-boundary in the paper."
        ):
            self.play(
                FadeOut(vm),
                FadeOut(sp),
                FadeOut(st1),
                FadeOut(box_st1),
                FadeOut(st2),
                run_time=0.6,
            )
            self.play(st3.animate.next_to(bc, DOWN, buff=0.5), run_time=0.6)
            self.play(Write(final), run_time=1.8)
            self.play(Create(highlight(final, color=C_DEFAULT)), run_time=0.6)
        self.pause(0.4)
        self.clear_body(self.header)

        p = BASELINE
        b_coef = p["mu_L"] - 0.5 * p["sigma"] ** 2
        disc = np.sqrt(b_coef**2 + 2.0 * p["sigma"] ** 2 * (p["r"] + p["lambda"]))
        beta_neg = (-b_coef - disc) / p["sigma"] ** 2
        markup = beta_neg / (beta_neg - 1.0)

        m1 = MathTex(
            r"\beta_s^- < 0\ \Rightarrow\ M \equiv \frac{\beta_s^-}{\beta_s^- - 1}"
            r" \in (0, 1)",
            font_size=38,
        ).shift(UP * 1.2)
        m2 = MathTex(
            rf"\text{{baseline: }}\beta_s^- \approx {beta_neg:.2f},"
            rf"\qquad M \approx {markup:.2f}",
            font_size=36,
            color=C_FAINT,
        ).next_to(m1, DOWN, buff=0.5)
        m3 = MathTex(
            r"\text{naive break-even: } A_{\text{eff},i}\,X = N"
            r"\ \Rightarrow\ X_{\text{be}} = \frac{N}{A_{\text{eff},i}},"
            r"\qquad X_D = M\cdot X_{\text{be}} < X_{\text{be}}",
            font_size=34,
        ).next_to(m2, DOWN, buff=0.5)
        with self.voiceover(
            "One interpretation before we move on. Because beta is negative,"
            " the factor beta over beta minus one lies strictly between zero"
            " and one."
        ):
            self.play(Write(m1), run_time=1.4)
        with self.voiceover(
            f"At the baseline calibration, beta is about minus"
            f" {abs(beta_neg):.2f} rounded, so the factor is about zero point"
            f" seven."
        ):
            self.play(Write(m2), run_time=1.2)
        with self.voiceover(
            "A naive firm would default the moment revenue stops covering"
            " coupons and operating costs. The optimal boundary sits thirty"
            " percent below that break-even level: defaulting kills the"
            " option to wait for demand to recover, and that option has value."
        ):
            self.play(Write(m3), run_time=1.8)
        self.pause(0.5)
        self.clear_body()


class P4S08OneWayCoupling(PaperScene):
    def construct(self):
        self.set_header("The one-way coupling, made exact", kicker="APPENDIX B")

        from ai_lab_investment.models.duopoly import DuopolyModel
        from ai_lab_investment.models.parameters import ModelParameters

        p = ModelParameters()
        duo = DuopolyModel(p, leverage=0.40, coupon_rate=0.05, bankruptcy_cost=0.30)
        eq_d = duo.solve_preemption_equilibrium("H")
        args = (
            float(eq_d["phi_follower"]),
            float(eq_d["K_follower"]),
            float(eq_d["phi_leader"]),
            float(eq_d["K_leader"]),
        )
        x_d0 = duo.default_boundary(*args)
        x_dc = duo.default_boundary_coupled(*args)
        kappa = duo.coupled_boundary_bias_linear(*args)
        exact_bias = (x_d0 - x_dc) / x_d0

        q = Text(
            "We replaced E_H by its perpetuity component. What did we drop?",
            font_size=28,
            color=C_TEXT,
        ).to_edge(UP, buff=1.4)
        with self.voiceover(
            "The derivation replaced the H-regime equity by its perpetuity"
            " component. Time to check what that step dropped, and what it"
            " costs."
        ):
            self.play(FadeIn(q), run_time=1.2)

        eh = MathTex(
            r"E_H(X) =",
            r"A_H (\phi_i K_i)^{\alpha} s_i^H\, X - N",
            r"+ D_H X^{\beta_H^-}",
            r",\qquad D_H > 0",
            font_size=36,
        ).next_to(q, DOWN, buff=0.55)
        eh[1].set_color(C_H)
        eh[2].set_color(C_DEFAULT)
        with self.voiceover(
            "Because the switch is absorbing, E H satisfies a standard,"
            " uncoupled Leland equation with a closed-form solution: a"
            " perpetuity part, plus its own default option, D H times X to"
            " the negative H-root, with D H positive."
        ):
            self.play(Write(eh), run_time=2.0)

        f1 = MathTex(
            r"E_H \to \text{perpetuity only}"
            r"\ \Rightarrow\ \text{particular coefficient} = A_{\text{eff},i}"
            r"\ \Rightarrow\ \text{eq. default-boundary exactly}",
            font_size=32,
        ).next_to(eh, DOWN, buff=0.55)
        with self.voiceover(
            "Keeping only the perpetuity part, the forcing term capitalizes"
            " into a particular solution whose linear coefficient is exactly"
            " A effective: the single-boundary formula is not an"
            " approximation of the algebra, it is exact under that"
            " replacement."
        ):
            self.play(Write(f1), run_time=1.8)

        f2 = MathTex(
            r"\text{omitted } D_H X^{\beta_H^-} > 0"
            r"\ \Rightarrow\ E_H \text{ understated}"
            r"\ \Rightarrow\ X_D \text{ overstated}",
            font_size=34,
            color=C_DEFAULT,
        ).next_to(f1, DOWN, buff=0.5)
        with self.voiceover(
            "But the omitted term is positive: it is the H-regime default"
            " option. Dropping it understates the continuation value, so the"
            " closed-form boundary weakly overstates X D. The error runs"
            " against faith-based survival, which is the conservative"
            " direction."
        ):
            self.play(Write(f2), run_time=1.8)
        self.pause(0.4)
        self.clear_body()

        c2 = MathTex(
            r"\lambda D_H X^{\beta_H^-}\ \text{forces}\ C_2 X^{\beta_H^-},",
            r"\qquad C_2 = \frac{-\lambda D_H}{Q_L(\beta_H^-)},",
            r"\qquad Q_L(\beta) = \tfrac{1}{2}\sigma^2\beta(\beta-1)"
            r" + \mu_L\beta - (r+\lambda)",
            font_size=32,
        ).to_edge(UP, buff=1.4)
        with self.voiceover(
            "Now solve the coupled system exactly. The dropped term enters the"
            " L-regime equation as a forcing proportional to X to the beta H"
            " minus, so it adds a particular term C two times that same power,"
            " with C two equal to minus lambda D H over the L characteristic"
            " polynomial evaluated at beta H minus."
        ):
            self.play(Write(c2), run_time=2.2)
        with self.voiceover(
            "That division is legitimate because beta H minus is not a root of"
            " the L-regime polynomial, and at calibration values C two comes"
            " out negative."
        ):
            self.play(Indicate(c2[1], color=C_OPTION), run_time=1.2)

        full = MathTex(
            r"E(X) = A_{\text{eff},i}\,X - N",
            r"+ C_2 X^{\beta_H^-}",
            r"+ A_- X^{\beta_L^-}",
            font_size=36,
        ).next_to(c2, DOWN, buff=0.5)
        full[1].set_color(C_H)
        full[2].set_color(C_DEFAULT)
        with self.voiceover(
            "The exact L-regime equity therefore has three pieces: the"
            " perpetuity part, the new C two term, and the homogeneous"
            " default-option term with unknown coefficient A minus."
        ):
            self.play(Write(full), run_time=1.6)

        vm = MathTex(
            r"\text{(VM)}\ \ A_{\text{eff}}X_D - N + C_2 X_D^{\beta_H^-}"
            r" + A_- X_D^{\beta_L^-} = 0",
            font_size=32,
        )
        sp = MathTex(
            r"\text{(SP)}\times X_D\ \ A_{\text{eff}}X_D"
            r" + \beta_H^- C_2 X_D^{\beta_H^-}"
            r" + \beta_L^- A_- X_D^{\beta_L^-} = 0",
            font_size=32,
        )
        comb = MathTex(
            r"\beta_L^-\cdot\text{(VM)} - \text{(SP)}\times X_D:",
            font_size=32,
            color=C_OPTION,
        )
        res = MathTex(
            r"A_{\text{eff}}(\beta_L^- - 1)X_D - \beta_L^- N"
            r" + C_2(\beta_L^- - \beta_H^-)X_D^{\beta_H^-} = 0",
            font_size=34,
        )
        block = VGroup(vm, sp, comb, res).arrange(DOWN, buff=0.32, aligned_edge=LEFT)
        block.next_to(full, DOWN, buff=0.5)

        with self.voiceover(
            "Value matching and smooth pasting at the boundary now determine"
            " A minus and X D jointly. Here is smooth pasting already"
            " multiplied through by X D."
        ):
            self.play(Write(vm), run_time=1.2)
            self.play(Write(sp), run_time=1.2)
        with self.voiceover(
            "The key observation: A minus enters both equations linearly,"
            " through the same product A minus times X D to the beta L minus."
            " So take beta L minus times value matching, and subtract smooth"
            " pasting."
        ):
            self.play(Write(comb), run_time=1.2)
        with self.voiceover(
            "The homogeneous coefficient cancels exactly, leaving one scalar"
            " equation in X D alone: the linear and constant terms from"
            " before, plus a single C two correction."
        ):
            self.play(Write(res), run_time=1.6)
            self.play(Create(highlight(res, color=C_OPTION)), run_time=0.6)
        with self.voiceover(
            "Set C two to zero and you recover the single-boundary formula:"
            " A effective times beta minus one times X D equals beta times N."
            " The coupled boundary is the continuation of that root as C two"
            " switches on."
        ):
            self.play(Indicate(res, color=C_FAINT), run_time=1.2)
        self.pause(0.4)
        self.clear_body()

        kap = MathTex(
            r"\frac{X_D^0 - X_D}{X_D^0} \approx \kappa =",
            r"\frac{C_2\,(\beta_L^- - \beta_H^-)\,(X_D^0)^{\beta_H^- - 1}}"
            r"{A_{\text{eff}}\,(\beta_L^- - 1)}",
            r"> 0",
            font_size=36,
        ).shift(UP * 1.1)
        with self.voiceover(
            "A first-order expansion in the small coefficient C two around the"
            " single-boundary root X D zero gives a closed-form relative bias,"
            " kappa. The sign is analytical: C two is negative and the"
            " denominator is negative, so kappa is positive."
        ):
            self.play(Write(kap), run_time=2.0)

        nums = MathTex(
            rf"\text{{baseline (follower, }}\ell=0.40\text{{): }}"
            rf"\kappa \approx {kappa * 100:.1f}\%,"
            rf"\qquad \text{{exact bias}} \approx {exact_bias * 100:.1f}\%",
            font_size=36,
            color=C_FAINT,
        ).next_to(kap, DOWN, buff=0.6)
        with self.voiceover(
            f"Computing both from the model at the baseline equilibrium: the"
            f" first-order kappa is about {kappa * 100:.1f} percent, and the"
            f" exact coupled-system bias is about {exact_bias * 100:.1f}"
            f" percent, uniformly across leverage levels."
        ):
            self.play(Write(nums), run_time=1.6)

        concl = Text(
            "single-boundary formula overstates X_D by ~3%:"
            " conservative for faith-based survival",
            font_size=26,
            color=C_DEFAULT,
        ).next_to(nums, DOWN, buff=0.6)
        with self.voiceover(
            "So the working formula makes the levered firm look about three"
            " percent riskier than it is. Every credit-risk conclusion that"
            " follows is therefore conservative."
        ):
            self.play(FadeIn(concl), run_time=1.2)
        self.pause(0.5)
        self.clear_body()


class P4S09LeverageStatics(PaperScene):
    def construct(self):
        self.set_header("Proposition 2(i): leverage and the coupon", kicker="PROOF")

        xd = MathTex(
            r"X_D = \frac{\beta_s^-}{\beta_s^- - 1}\cdot",
            r"\frac{c_d\,\ell\,I(K) + \delta K}{r\,A_{\text{eff},i}}",
            font_size=40,
        ).to_edge(UP, buff=1.6)
        with self.voiceover(
            "Part one of Proposition two is immediate once the coupon is"
            " written out: c D equals c d times ell times I of K, so leverage"
            " and the coupon rate live only in the numerator."
        ):
            self.play(Write(xd), run_time=1.8)

        note = MathTex(
            r"A_{\text{eff},i}\ \text{does not depend on}\ \ell"
            r"\quad\text{(at fixed } K_i, \phi_i\text{)}",
            font_size=34,
            color=C_FAINT,
        ).next_to(xd, DOWN, buff=0.6)
        with self.voiceover(
            "A effective is a statement about revenues and beliefs; holding"
            " capacity and the training fraction fixed, it contains no"
            " leverage at all."
        ):
            self.play(Write(note), run_time=1.4)

        derivs = MathTex(
            r"\frac{\partial X_D}{\partial \ell}"
            r" = \frac{\beta_s^-}{\beta_s^- - 1}\cdot"
            r"\frac{c_d\,I(K)}{r\,A_{\text{eff},i}} > 0,",
            r"\qquad \frac{\partial X_D}{\partial c_d}"
            r" = \frac{\beta_s^-}{\beta_s^- - 1}\cdot"
            r"\frac{\ell\,I(K)}{r\,A_{\text{eff},i}} > 0",
            font_size=36,
        ).next_to(note, DOWN, buff=0.7)
        with self.voiceover(
            "Differentiate: both partial derivatives are positive constants"
            " times the markup factor. More debt, or a higher coupon rate,"
            " mechanically raises the demand level at which equity holders"
            " walk away. That is part one, done."
        ):
            self.play(Write(derivs), run_time=2.0)
            self.play(Create(highlight(derivs, color=C_OPTION)), run_time=0.6)
        self.pause(0.5)
        self.clear_body()


class P4S10FaithCondition(PaperScene):
    def construct(self):
        self.set_header("Proposition 2(ii): the faith condition", kicker="PROOF")

        adef = MathTex(
            r"a \equiv [(1-\phi_i)K_i]^{\alpha}\, s_i^L",
            r"\qquad\text{(L-regime flow)}",
            font_size=36,
        )
        adef[0].set_color(C_INFER)
        adef[1].set_color(C_FAINT)
        bdef = MathTex(
            r"b \equiv \frac{(\phi_i K_i)^{\alpha}\, s_i^H}{r - \mu_H}",
            r"\qquad\text{(H-continuation PV)}",
            font_size=36,
        )
        bdef[0].set_color(C_H)
        bdef[1].set_color(C_FAINT)
        aeff = MathTex(
            r"A_{\text{eff},i} = \frac{a + \lambda\, b}{r - \mu_L + \lambda}",
            font_size=40,
        )
        defs = VGroup(adef, bdef, aeff).arrange(DOWN, buff=0.45)
        defs.to_edge(UP, buff=1.4)

        with self.voiceover(
            "Now the core of the proposition: how the default boundary moves"
            " with optimism. Define a as the L-regime revenue flow, and b as"
            " the present value of the H-regime revenue per unit of demand."
        ):
            self.play(Write(adef), run_time=1.4)
            self.play(Write(bdef), run_time=1.4)
        with self.voiceover(
            "Then A effective is simply a plus lambda b, all over r minus mu L"
            " plus lambda. Lambda appears in both the numerator and the"
            " denominator, and that tension is the whole story."
        ):
            self.play(Write(aeff), run_time=1.4)

        q1 = MathTex(
            r"\frac{\partial A_{\text{eff},i}}{\partial \lambda} =",
            r"\frac{b\,(r-\mu_L+\lambda)\;-\;(a + \lambda b)}"
            r"{(r-\mu_L+\lambda)^2}",
            font_size=38,
        )
        q2 = MathTex(
            r"\text{numerator} = b(r-\mu_L)",
            r"+ \lambda b",
            r"- a",
            r"- \lambda b",
            font_size=38,
        )
        q3 = MathTex(
            r"\frac{\partial A_{\text{eff},i}}{\partial \lambda}"
            r" = \frac{b(r-\mu_L) - a}{(r-\mu_L+\lambda)^2}",
            font_size=38,
        )
        steps = VGroup(q1, q2, q3).arrange(DOWN, buff=0.42)
        steps.next_to(defs, DOWN, buff=0.55)

        with self.voiceover(
            "Differentiate with the quotient rule: derivative of the numerator"
            " is b, times the denominator, minus the numerator times the"
            " derivative of the denominator, which is one."
        ):
            self.play(Write(q1), run_time=1.8)
        with self.voiceover(
            "Expand the top: b times r minus mu L, plus lambda b, minus a,"
            " minus lambda b. The two lambda b terms cancel exactly."
        ):
            self.play(Write(q2), run_time=1.6)
            self.play(
                Indicate(q2[1], color=C_OPTION),
                Indicate(q2[3], color=C_OPTION),
                run_time=1.2,
            )
        with self.voiceover(
            "What remains is b times r minus mu L, minus a, over the square of"
            " the effective discount rate."
        ):
            self.play(Write(q3), run_time=1.4)

        cond = MathTex(
            r"\frac{\partial A_{\text{eff},i}}{\partial \lambda} > 0"
            r"\quad\Longleftrightarrow\quad",
            r"b\,(r - \mu_L) > a",
            font_size=40,
        ).to_edge(DOWN, buff=0.5)
        cond[1].set_color(C_OPTION)
        with self.voiceover(
            "So optimism raises A effective exactly when the H-continuation"
            " value, scaled by r minus mu L, exceeds the L-regime flow. That"
            " is the faith condition. And since mu H exceeds mu L, the"
            " scaling factor works in faith's favor."
        ):
            self.play(Write(cond), run_time=1.8)
            self.play(Create(highlight(cond[1], color=C_OPTION)), run_time=0.6)
        self.pause(0.4)
        self.clear_body()

        from ai_lab_investment.models.duopoly import DuopolyModel
        from ai_lab_investment.models.parameters import ModelParameters

        p = ModelParameters()
        duo = DuopolyModel(p)
        phi_under = duo.faith_threshold()
        r_val = ((p.r - p.mu_H) / (p.r - p.mu_L)) ** (1.0 / p.alpha)

        head = Text(
            "symmetric shares: s_L = s_H = s  (symmetric capacities, or monopoly)",
            font_size=26,
            color=C_FAINT,
        ).to_edge(UP, buff=1.4)
        c1 = MathTex(
            r"\frac{(\phi K)^{\alpha}\, s}{r-\mu_H}\,(r-\mu_L)"
            r" > (1-\phi)^{\alpha} K^{\alpha}\, s",
            font_size=36,
        )
        c2 = MathTex(
            r"\left(\frac{\phi}{1-\phi}\right)^{\alpha}"
            r" > \frac{r-\mu_H}{r-\mu_L}",
            font_size=36,
        )
        c3 = MathTex(
            r"\frac{\phi}{1-\phi} > R"
            r" \equiv \left(\frac{r-\mu_H}{r-\mu_L}\right)^{1/\alpha}",
            font_size=36,
        )
        c4 = MathTex(
            r"\phi > R\,(1-\phi)\quad\Rightarrow\quad \phi\,(1+R) > R",
            font_size=36,
        )
        c5 = MathTex(
            r"\phi > \underline{\phi} = \frac{R}{1+R}",
            font_size=40,
        )
        chain = VGroup(c1, c2, c3, c4, c5).arrange(DOWN, buff=0.36)
        chain.next_to(head, DOWN, buff=0.45)

        with self.voiceover(
            "With symmetric shares, the condition becomes fully explicit."
            " Substitute the definitions of a and b: the contest shares and"
            " the K to the alpha factors appear on both sides."
        ):
            self.play(FadeIn(head), Write(c1), run_time=1.8)
        with self.voiceover(
            "Cancel them and collect the phi terms: the odds ratio of training"
            " raised to alpha must exceed r minus mu H over r minus mu L."
        ):
            self.play(Write(c2), run_time=1.4)
        with self.voiceover(
            "Take both sides to the power one over alpha and call the"
            " right-hand side R."
        ):
            self.play(Write(c3), run_time=1.2)
        with self.voiceover(
            "Then multiply through by one minus phi and collect: phi times one"
            " plus R exceeds R."
        ):
            self.play(Write(c4), run_time=1.2)
        box5 = highlight(c5, color=C_OPTION)
        with self.voiceover(
            "So the A-effective channel is positive exactly when phi exceeds"
            " phi underbar, R over one plus R. This is equation"
            " phi-underbar in the paper."
        ):
            self.play(Write(c5), run_time=1.4)
            self.play(Create(box5), run_time=0.6)

        nums = MathTex(
            rf"R = \left(\tfrac{{0.06}}{{0.11}}\right)^{{2.5}}"
            rf" \approx {r_val:.2f},"
            rf"\qquad \underline{{\phi}} \approx {phi_under:.2f}"
            r"\qquad(\text{independent of }\lambda)",
            font_size=34,
            color=C_FAINT,
        ).to_edge(DOWN, buff=0.45)
        with self.voiceover(
            "At the baseline calibration, R is zero point zero six over zero"
            " point one one, raised to the two point five: about zero point"
            " two two. So phi underbar is about zero point one eight, and"
            " notice it does not involve lambda at all."
        ):
            self.play(FadeOut(head), FadeOut(c1), FadeOut(c2), run_time=0.5)
            self.play(VGroup(c3, c4, c5, box5).animate.shift(UP * 2.0), run_time=0.6)
            self.play(Write(nums), run_time=1.8)
        self.pause(0.5)
        self.clear_body()


class P4S11MarkupChannel(PaperScene):
    def construct(self):
        self.set_header("The opposing markup channel", kicker="PROOF")

        xd = MathTex(
            r"X_D = M(\beta_s^-)\cdot\frac{N}{A_{\text{eff},i}},",
            r"\qquad M(\beta) = \frac{\beta}{\beta-1},",
            r"\qquad N = \frac{c_D + \delta K_i}{r}",
            font_size=36,
        ).to_edge(UP, buff=1.4)
        with self.voiceover(
            "The faith condition is not the end of part two, because lambda"
            " attacks the boundary from a second direction: the markup factor"
            " M depends on beta, and beta depends on lambda through the"
            " effective discount rate."
        ):
            self.play(Write(xd), run_time=1.8)

        dec = MathTex(
            r"\frac{\partial X_D}{\partial \lambda} =",
            r"\underbrace{\frac{\partial M}{\partial\lambda}\cdot"
            r"\frac{N}{A_{\text{eff},i}}}_{>0\ (\beta\text{-channel})}",
            r"+",
            r"\underbrace{M\,N\cdot"
            r"\frac{\partial (1/A_{\text{eff},i})}{\partial\lambda}}"
            r"_{<0\ (A_{\text{eff}}\text{-channel, under faith})}",
            font_size=36,
        ).next_to(xd, DOWN, buff=0.6)
        dec[1].set_color(C_DEFAULT)
        dec[3].set_color(C_H)
        with self.voiceover(
            "The full derivative splits into two channels: a beta channel"
            " through the markup, and the A-effective channel we just signed."
            " The claim is that the beta channel is always positive."
        ):
            self.play(Write(dec), run_time=2.2)
        self.pause(0.3)

        m1 = MathTex(
            r"\beta_s^- = \frac{-(\mu_L - \sigma^2/2) - D}{\sigma^2},",
            r"\qquad D = \sqrt{(\mu_L - \sigma^2/2)^2 + 2\sigma^2(r+\lambda)}",
            font_size=32,
        )
        m2 = MathTex(
            r"2D\,\frac{dD}{d\lambda} = 2\sigma^2"
            r"\quad\Rightarrow\quad \frac{dD}{d\lambda} = \frac{\sigma^2}{D}",
            font_size=32,
        )
        m3 = MathTex(
            r"\frac{d\beta_s^-}{d\lambda} = -\frac{1}{\sigma^2}\cdot"
            r"\frac{dD}{d\lambda} = -\frac{1}{D}",
            font_size=32,
        )
        m4 = MathTex(
            r"\frac{dM}{d\beta} = \frac{(\beta-1) - \beta}{(\beta-1)^2}"
            r" = -\frac{1}{(\beta-1)^2}",
            font_size=32,
        )
        m5 = MathTex(
            r"\frac{dM}{d\lambda} = \frac{dM}{d\beta}\cdot"
            r"\frac{d\beta_s^-}{d\lambda}"
            r" = \frac{1}{(\beta_s^- - 1)^2\, D} > 0",
            font_size=34,
        )
        VGroup(m1, m2, m3).arrange(DOWN, buff=0.3).next_to(dec, DOWN, buff=0.45)
        anchor = m3.copy().next_to(dec, DOWN, buff=0.45)
        m4.next_to(anchor, DOWN, buff=0.32)
        m5.next_to(m4, DOWN, buff=0.32)

        with self.voiceover(
            "Write the negative root explicitly from the quadratic formula,"
            " with D the square root of the discriminant; lambda enters only"
            " inside D."
        ):
            self.play(Write(m1), run_time=1.6)
        with self.voiceover(
            "Differentiate D squared: two D D prime equals two sigma squared,"
            " so D prime is sigma squared over D."
        ):
            self.play(Write(m2), run_time=1.4)
        with self.voiceover(
            "Hence the root moves at rate minus one over D: a higher lambda"
            " makes beta more negative."
        ):
            self.play(Write(m3), run_time=1.2)
        with self.voiceover(
            "And the markup's slope in beta is minus one over beta minus one,"
            " squared, by the quotient rule."
        ):
            self.play(FadeOut(m1), FadeOut(m2), run_time=0.4)
            self.play(m3.animate.move_to(anchor), run_time=0.5)
            self.play(Write(m4), run_time=1.2)
        with self.voiceover(
            "Chain the two: the minus signs cancel, and d M d lambda is one"
            " over beta minus one squared times D. Strictly positive."
        ):
            self.play(Write(m5), run_time=1.4)
            self.play(Create(highlight(m5, color=C_DEFAULT)), run_time=0.6)

        p = BASELINE
        b_coef = p["mu_L"] - 0.5 * p["sigma"] ** 2
        disc = np.sqrt(b_coef**2 + 2.0 * p["sigma"] ** 2 * (p["r"] + p["lambda"]))
        beta_neg = (-b_coef - disc) / p["sigma"] ** 2
        with self.voiceover(
            "Since beta is negative, M sits below one and rises toward one as"
            " lambda grows: at baseline, beta is about minus two point three"
            " three and M is about zero point seven. So more optimism, taken"
            " alone through this channel, erodes the option-value discount"
            " and pushes the default boundary up."
        ):
            self.play(
                Indicate(dec[1], color=C_DEFAULT),
                run_time=1.5,
            )
        _ = beta_neg
        self.pause(0.5)
        self.clear_body()


class P4S12ExactThreshold(PaperScene):
    def construct(self):
        self.set_header("The exact net threshold", kicker="PROOF")

        t1 = MathTex(
            r"\ln X_D = \ln M + \ln N - \ln A_{\text{eff},i}",
            font_size=36,
        )
        t2 = MathTex(
            r"\frac{\partial \ln X_D}{\partial\lambda} = m"
            r" - \frac{\partial \ln A_{\text{eff},i}}{\partial\lambda},",
            r"\qquad m \equiv \frac{1}{M}\frac{dM}{d\lambda}"
            r" = \frac{1}{\beta_s^-(\beta_s^- - 1)\,D} > 0",
            font_size=34,
        )
        t3 = MathTex(
            r"\frac{\partial \ln A_{\text{eff},i}}{\partial\lambda}"
            r" = \frac{b(r-\mu_L) - a}{(a + \lambda b)\,\Delta},",
            r"\qquad \Delta \equiv r - \mu_L + \lambda",
            font_size=34,
        )
        top = VGroup(t1, t2, t3).arrange(DOWN, buff=0.4)
        top.to_edge(UP, buff=1.4)

        with self.voiceover(
            "The two channels combine cleanly in logs: log X D is log markup"
            " plus log costs minus log A effective, and N does not depend on"
            " lambda."
        ):
            self.play(Write(t1), run_time=1.4)
        with self.voiceover(
            "So the semi-elasticity of the boundary is m minus the"
            " semi-elasticity of A effective, where m is d M d lambda over M:"
            " one over beta times beta minus one times D, positive because"
            " beta times beta minus one is positive for negative beta."
        ):
            self.play(Write(t2), run_time=2.0)
        with self.voiceover(
            "Divide the quotient-rule derivative by A effective itself: the"
            " semi-elasticity of A effective is b r minus mu L minus a, over"
            " a plus lambda b times Delta, with Delta the effective discount"
            " rate."
        ):
            self.play(Write(t3), run_time=1.8)

        n1 = MathTex(
            r"\frac{\partial X_D}{\partial\lambda} < 0"
            r"\quad\Longleftrightarrow\quad",
            r"b(r-\mu_L) - a > m\,(a + \lambda b)\,\Delta",
            font_size=36,
        )
        n1[1].set_color(C_OPTION)
        n2 = MathTex(
            r"b(r-\mu_L) - m\lambda\Delta\, b\ >\ a + m\Delta\, a",
            font_size=36,
        )
        n3 = MathTex(
            r"b\left[(r-\mu_L) - m\lambda\Delta\right]\ >\ a\,(1 + m\Delta)",
            font_size=36,
        )
        n4 = MathTex(
            r"\frac{b}{a} > \frac{1 + m\Delta}{(r-\mu_L) - m\lambda\Delta}",
            r"\qquad\text{(requires } (r-\mu_L) > m\lambda\Delta\text{)}",
            font_size=36,
        )
        n4[1].set_color(C_FAINT)
        net = VGroup(n1, n2, n3, n4).arrange(DOWN, buff=0.3)
        net.to_edge(DOWN, buff=0.5)

        with self.voiceover(
            "The boundary falls with lambda when the A-effective"
            " semi-elasticity beats m. Multiply through by the positive"
            " denominator: the condition is b r minus mu L minus a, greater"
            " than m times a plus lambda b times Delta. Linear in a and b."
        ):
            self.play(FadeOut(t1), run_time=0.5)
            self.play(VGroup(t2, t3).animate.to_edge(UP, buff=1.2), run_time=0.6)
            self.play(Write(n1), run_time=2.0)
        with self.voiceover(
            "Move the lambda b piece of the right side to the left, and the a"
            " pieces to the right."
        ):
            self.play(Write(n2), run_time=1.4)
        with self.voiceover("Factor b on the left and a on the right."):
            self.play(Write(n3), run_time=1.2)
        with self.voiceover(
            "Divide: the condition is a floor on the ratio b over a. The"
            " division is valid under the mild regularity condition that r"
            " minus mu L exceeds m lambda Delta; if that ever failed, no"
            " allocation could make the boundary fall."
        ):
            self.play(Write(n4), run_time=1.6)
            self.play(Create(highlight(n4[0], color=C_OPTION)), run_time=0.6)
        self.pause(0.4)
        self.clear_body()

        from ai_lab_investment.models.duopoly import DuopolyModel
        from ai_lab_investment.models.parameters import ModelParameters

        p = ModelParameters()
        duo = DuopolyModel(p)
        phi_tilde = duo.faith_threshold_exact()
        phi_under = duo.faith_threshold()
        b_coef = p.mu_L - 0.5 * p.sigma**2
        disc = np.sqrt(b_coef**2 + 2.0 * p.sigma**2 * (p.r + p.lam))
        beta_neg = (-b_coef - disc) / p.sigma**2
        m_val = 1.0 / (beta_neg * (beta_neg - 1.0) * disc)

        s1 = MathTex(
            r"\text{symmetric shares: }\ \frac{b}{a}"
            r" = \frac{(\phi/(1-\phi))^{\alpha}}{r-\mu_H}",
            font_size=36,
        )
        s2 = MathTex(
            r"\tilde{\phi} = \frac{\tilde{R}}{1+\tilde{R}},",
            r"\qquad \tilde{R} = \left[\frac{(r-\mu_H)(1+m\Delta)}"
            r"{(r-\mu_L) - m\lambda\Delta}\right]^{1/\alpha}",
            font_size=38,
        )
        block = VGroup(s1, s2).arrange(DOWN, buff=0.5)
        block.to_edge(UP, buff=1.6)

        with self.voiceover(
            "With symmetric shares, b over a is the training odds ratio to the"
            " alpha, divided by r minus mu H: the shares and capacities cancel"
            " just as before."
        ):
            self.play(Write(s1), run_time=1.6)
        with self.voiceover(
            "Solving for phi by the same two steps as phi underbar gives the"
            " exact net threshold, phi tilde: identical in form, with the"
            " ratio R inflated by the markup channel. This is equation"
            " phi-tilde in the paper."
        ):
            self.play(Write(s2), run_time=1.8)
            self.play(Create(highlight(s2, color=C_OPTION)), run_time=0.6)

        nums = MathTex(
            rf"\text{{baseline: }} m \approx {m_val:.2f},"
            rf"\qquad \tilde{{\phi}} \approx {phi_tilde:.2f}"
            rf"\ >\ \underline{{\phi}} \approx {phi_under:.2f}",
            font_size=36,
            color=C_FAINT,
        ).next_to(block, DOWN, buff=0.6)
        with self.voiceover(
            "At baseline, m is about zero point seven seven, and phi tilde is"
            " about zero point three two, comfortably above phi underbar at"
            " zero point one eight."
        ):
            self.play(Write(nums), run_time=1.6)

        nest = MathTex(
            r"m \to 0\ \Rightarrow\ \tilde{R} \to R"
            r"\ \Rightarrow\ \tilde{\phi} \to \underline{\phi};"
            r"\qquad m > 0\ \Rightarrow\ \tilde{\phi} > \underline{\phi}",
            font_size=34,
        ).next_to(nums, DOWN, buff=0.6)
        with self.voiceover(
            "And the nesting is clean: switch the markup channel off by"
            " sending m to zero and phi tilde collapses to phi underbar;"
            " for any positive m it sits strictly above. Clearing the faith"
            " condition is necessary but not sufficient: you must beat the"
            " markup channel too."
        ):
            self.play(Write(nest), run_time=1.8)
        self.pause(0.5)
        self.clear_body()


class P4S13SignAtOptimum(PaperScene):
    def construct(self):
        self.set_header("Sign at the optimum", kicker="PROOF")

        from scipy import optimize

        from ai_lab_investment.models.duopoly import DuopolyModel
        from ai_lab_investment.models.parameters import ModelParameters

        p = ModelParameters()
        duo = DuopolyModel(p)

        def phi_star(lam: float) -> float:
            ratio = (lam / (p.r - p.mu_H)) ** (1.0 / (1.0 - p.alpha))
            return ratio / (1.0 + ratio)

        lams = np.linspace(0.005, 0.20, 80)
        phi_s = np.array([phi_star(la) for la in lams])
        phi_t = np.array([duo.faith_threshold_exact(float(la)) for la in lams])
        lam_bar = optimize.brentq(
            lambda la: phi_star(la) - duo.faith_threshold_exact(la), 0.01, 0.10
        )

        ax = clean_axes([0, 0.20], [0, 0.95], width=9.2, height=4.6).shift(DOWN * 0.6)
        x_lab = MathTex(r"\lambda", font_size=32, color=C_DEMAND).next_to(
            ax.x_axis, RIGHT, buff=0.15
        )
        y_lab = MathTex(r"\phi", font_size=32, color=C_TRAIN).next_to(
            ax.y_axis, UP, buff=0.15
        )
        with self.voiceover(
            "Phi tilde depends on lambda, and so does the optimal allocation"
            " phi star from Proposition one. So whether the firm actually"
            " enjoys faith-based survival at its own optimum is a horse race"
            " between two curves."
        ):
            self.play(Create(ax), FadeIn(x_lab), FadeIn(y_lab), run_time=1.2)

        c_star = ax.plot_line_graph(
            lams, phi_s, line_color=C_TRAIN, add_vertex_dots=False
        )
        l_star = MathTex(r"\phi^*(\lambda)", font_size=30, color=C_TRAIN).move_to(
            ax.coords_to_point(0.155, 0.93)
        )
        with self.voiceover(
            "The purple curve is the optimal training fraction, increasing in"
            " lambda: more optimistic firms train more."
        ):
            self.play(Create(c_star), FadeIn(l_star), run_time=1.6)

        c_til = ax.plot_line_graph(
            lams, phi_t, line_color=C_DEFAULT, add_vertex_dots=False
        )
        l_til = MathTex(
            r"\tilde{\phi}(\lambda)", font_size=30, color=C_DEFAULT
        ).move_to(ax.coords_to_point(0.165, 0.26))
        with self.voiceover(
            "The red curve is the exact threshold phi tilde, computed from the"
            " model's closed form. It drifts gently with lambda."
        ):
            self.play(Create(c_til), FadeIn(l_til), run_time=1.6)

        cross = DashedLine(
            ax.coords_to_point(lam_bar, 0),
            ax.coords_to_point(lam_bar, 0.9),
            color=C_OPTION,
        )
        cross_lab = MathTex(
            rf"\bar{{\lambda}} \approx {lam_bar:.3f}",
            font_size=30,
            color=C_OPTION,
        ).next_to(cross, UP, buff=0.1)
        with self.voiceover(
            "The curves cross at lambda bar, about zero point zero three four."
            " To the right of the crossing, including the baseline of zero"
            " point one, phi star exceeds phi tilde: the optimal allocation"
            " clears the threshold and the default boundary falls with"
            " optimism."
        ):
            self.play(Create(cross), FadeIn(cross_lab), run_time=1.4)

        lam_ex = 0.02
        d_star = Dot(ax.coords_to_point(lam_ex, phi_star(lam_ex)), color=C_TRAIN)
        d_til = Dot(
            ax.coords_to_point(lam_ex, duo.faith_threshold_exact(lam_ex)),
            color=C_DEFAULT,
        )
        ex_lab = MathTex(
            rf"\lambda = 0.02:\ \phi^* \approx {phi_star(lam_ex):.2f}"
            rf" < \tilde{{\phi}} \approx {duo.faith_threshold_exact(lam_ex):.2f}",
            font_size=30,
        ).move_to(ax.coords_to_point(0.115, 0.50))
        with self.voiceover(
            "To the left, the ordering flips. At lambda equal to zero point"
            " zero two, the optimal allocation is only about fourteen percent"
            " training, below the threshold of about twenty-seven percent."
        ):
            self.play(FadeIn(d_star, scale=2), FadeIn(d_til, scale=2), run_time=0.8)
            self.play(Write(ex_lab), run_time=1.2)

        with self.voiceover(
            "So for sufficiently pessimistic beliefs, the optimal allocation"
            " is too inference-heavy, and the default boundary is locally"
            " increasing in lambda at the optimum. The closed form makes this"
            " refinement visible, and finite differences confirm it."
        ):
            self.play(Indicate(ex_lab, color=C_OPTION), run_time=1.4)
        self.pause(0.5)
        self.clear_body()


class P4S14SubstitutionAndRival(PaperScene):
    def construct(self):
        self.set_header("Parts (iii) and (iv)", kicker="PROOF")

        x1 = MathTex(
            r"X_D = \frac{\Psi(\ell)}{A_{\text{eff},i}(\phi_i)},",
            r"\qquad \Psi(\ell) = \frac{\beta_s^-}{\beta_s^- - 1}\cdot"
            r"\frac{c_d\,\ell\,I(K) + \delta K}{r}"
            r"\ \ \text{increasing in } \ell",
            font_size=34,
        ).to_edge(UP, buff=1.4)
        with self.voiceover(
            "Part three: leverage-training substitution. Write the boundary as"
            " a leverage piece Psi over an allocation piece A effective; Psi"
            " strictly increases in ell."
        ):
            self.play(Write(x1), run_time=1.8)

        x2 = MathTex(
            r"A_{\text{eff},i}(\phi)\ \text{strictly concave, interior max at }"
            r"\phi^*:\quad \uparrow\ \text{on}\ (0,\phi^*),"
            r"\quad \downarrow\ \text{on}\ (\phi^*,1)",
            font_size=32,
        ).next_to(x1, DOWN, buff=0.45)
        with self.voiceover(
            "From the proof of Proposition one, A effective is strictly"
            " concave in phi with an interior maximizer: increasing below phi"
            " star, decreasing above."
        ):
            self.play(Write(x2), run_time=1.6)

        from scipy import optimize

        from ai_lab_investment.models.duopoly import DuopolyModel
        from ai_lab_investment.models.parameters import ModelParameters

        p = ModelParameters()
        duo = DuopolyModel(p, coupon_rate=0.05)
        cap = 1.0

        def boundary(phi: float, lev: float) -> float:
            return duo.default_boundary(phi, cap, 0.0, 0.0, leverage=lev)

        lev0, phi0 = 0.10, 0.10
        target = boundary(phi0, lev0)
        lev_grid = np.linspace(lev0, 0.32, 45)
        levs, phis = [], []
        for lev in lev_grid:
            f = lambda ph, lv=lev: boundary(ph, lv) - target  # noqa: E731
            if f(0.699) > 0:
                break
            levs.append(float(lev))
            phis.append(float(optimize.brentq(f, 0.02, 0.699)))

        ax = clean_axes([0.08, 0.34], [0, 0.85], width=7.6, height=3.6).shift(
            DOWN * 1.6
        )
        x_lab = MathTex(r"\ell", font_size=30, color=C_FAINT).next_to(
            ax.x_axis, RIGHT, buff=0.15
        )
        y_lab = MathTex(r"\phi", font_size=30, color=C_TRAIN).next_to(
            ax.y_axis, UP, buff=0.15
        )
        iso = ax.plot_line_graph(
            np.array(levs), np.array(phis), line_color=C_OPTION, add_vertex_dots=False
        )
        iso_lab = Text("iso-X_D locus", font_size=24, color=C_OPTION).move_to(
            ax.coords_to_point(0.155, 0.55)
        )
        ceil = DashedLine(
            ax.coords_to_point(0.08, 0.70),
            ax.coords_to_point(0.34, 0.70),
            color=C_TRAIN,
        )
        ceil_lab = (
            MathTex(r"\phi^* \approx 0.70", font_size=28, color=C_TRAIN)
            .next_to(ceil, UP, buff=0.08)
            .shift(RIGHT * 2.4)
        )
        with self.voiceover(
            "So below phi star there is a substitution along the iso-boundary"
            " locus, computed here from the model: each extra unit of"
            " leverage can be offset by extra training, holding X D fixed."
        ):
            self.play(Create(ax), FadeIn(x_lab), FadeIn(y_lab), run_time=1.0)
            self.play(Create(iso), FadeIn(iso_lab), run_time=1.6)
        with self.voiceover(
            "The locus climbs toward phi star and stops: above the maximizer,"
            " more training lowers A effective and raises the boundary, so no"
            " substitution is available there."
        ):
            self.play(Create(ceil), FadeIn(ceil_lab), run_time=1.2)
        with self.voiceover(
            "This is mechanical, not optimal: the allocation first-order"
            " condition contains no leverage, so any empirical comovement of"
            " leverage and training reflects joint determination by beliefs"
            " and financing capacity, not a causal link."
        ):
            self.play(Indicate(iso_lab, color=C_OPTION), run_time=1.4)
        self.pause(0.4)
        self.clear_body()

        r1 = MathTex(
            r"s_i = \frac{y_i}{y_i + y_j}:\qquad"
            r"\frac{\partial s_i}{\partial y_j}"
            r" = -\frac{y_i}{(y_i + y_j)^2} < 0",
            font_size=36,
        ).shift(UP * 1.3)
        r2 = MathTex(
            r"K_j \uparrow\ \Rightarrow\ s_i^L \downarrow,\ s_i^H \downarrow"
            r"\ \Rightarrow\ A_{\text{eff},i} \downarrow"
            r"\ \Rightarrow\ X_D \uparrow",
            font_size=38,
        ).next_to(r1, DOWN, buff=0.7)
        with self.voiceover(
            "Part four is one chain of inequalities. Differentiate the share"
            " in the rival's measure: it is strictly decreasing, in both"
            " regimes."
        ):
            self.play(Write(r1), run_time=1.6)
        with self.voiceover(
            "A bigger rival shrinks both contest shares, which lowers A"
            " effective, which raises the default boundary. Stronger"
            " competition pushes you toward default. That completes"
            " Proposition two."
        ):
            self.play(Write(r2), run_time=1.6)
            self.play(Create(highlight(r2, color=C_OPTION)), run_time=0.6)
        self.pause(0.5)
        self.clear_body()


class P4S15EquityDebt(PaperScene):
    def construct(self):
        self.set_header("Equity and debt values", kicker="MODEL")

        e_full = MathTex(
            r"E(X) =",
            r"A_{\text{eff},i}X - \frac{\delta K}{r}",
            r"- (1-\ell)I(K)",
            r"- \frac{c_D}{r}",
            r"+ \left[\frac{c_D}{r} + \frac{\delta K}{r}"
            r" - A_{\text{eff},i}X_D\right]"
            r"\left(\frac{X}{X_D}\right)^{\beta_s^-}",
            font_size=32,
        ).to_edge(UP, buff=1.4)
        e_full[1].set_color(C_TEXT)
        e_full[2].set_color(C_FAINT)
        e_full[3].set_color(C_DEFAULT)
        e_full[4].set_color(C_OPTION)
        with self.voiceover(
            "Here is the equity claim, in the paper's net-present-value"
            " convention: the going-concern value minus the equity holders'"
            " initial contribution, so the firm invests when E is"
            " non-negative."
        ):
            self.play(Write(e_full), run_time=2.4)
        with self.voiceover(
            "Read it piece by piece: the unlevered perpetuity value, minus the"
            " sunk equity contribution, minus the capitalized coupon, plus the"
            " default option."
        ):
            for idx in (1, 2, 3, 4):
                self.play(Indicate(e_full[idx]), run_time=0.7)
        with self.voiceover(
            "The bracket multiplying the option factor is the flow deficit at"
            " the boundary: coupons and operating costs in excess of revenue,"
            " which limited liability lets equity holders abandon. The factor"
            " X over X D to the beta is the price of a claim paying one at"
            " default, and it tends to one as X falls to the boundary."
        ):
            self.play(Indicate(e_full[4], color=C_OPTION), run_time=1.4)

        chk1 = MathTex(
            r"E(X_D) = A_{\text{eff}}X_D - \frac{\delta K}{r} - (1-\ell)I(K)"
            r" - \frac{c_D}{r}",
            r"+ \frac{c_D}{r} + \frac{\delta K}{r} - A_{\text{eff}}X_D",
            font_size=32,
        )
        chk2 = MathTex(
            r"E(X_D) = -(1-\ell)\,I(K)\ \leq\ 0",
            font_size=36,
        )
        checks = VGroup(chk1, chk2).arrange(DOWN, buff=0.4)
        checks.next_to(e_full, DOWN, buff=0.6)
        with self.voiceover(
            "Consistency check at the boundary: set X equal to X D, so the"
            " option factor is one, and add the bracket."
        ):
            self.play(Write(chk1), run_time=1.6)
        with self.voiceover(
            "Everything cancels in pairs except the sunk contribution: at"
            " default the equity holders lose exactly what they put in, and"
            " limited liability truncates the claim at zero from there. The"
            " smooth-pasting conditions that pinned X D are independent of"
            " this sunk constant."
        ):
            self.play(Write(chk2), run_time=1.4)
            self.play(Create(highlight(chk2, color=C_OPTION)), run_time=0.6)

        unlev = MathTex(
            r"\ell = 0:\quad E(X) = A_{\text{eff},i}X"
            r" - \frac{\delta K}{r} - I(K)",
            font_size=32,
            color=C_FAINT,
        ).next_to(checks, DOWN, buff=0.5)
        with self.voiceover(
            "And without debt the whole default apparatus disappears: equity"
            " is just the unlevered net present value."
        ):
            self.play(Write(unlev), run_time=1.2)
        self.pause(0.4)
        self.clear_body()

        d_eq = MathTex(
            r"D(X) =",
            r"\frac{c_D}{r}\left[1 - \left(\frac{X}{X_D}\right)^{\beta_s^-}"
            r"\right]",
            r"+ R(X_D)\left(\frac{X}{X_D}\right)^{\beta_s^-}",
            font_size=36,
        ).to_edge(UP, buff=1.4)
        d_eq[1].set_color(C_TEXT)
        d_eq[2].set_color(C_DEFAULT)
        with self.voiceover(
            "The debt claim mirrors it: the risk-free value of the coupon"
            " stream, minus the part lost if default arrives, plus the"
            " recovery, both priced with the same default claim factor."
        ):
            self.play(Write(d_eq), run_time=2.0)

        rec = MathTex(
            r"R(X_D) = \min\left\{(1-b)\,\Lambda(X_D),\ \frac{c_D}{r}\right\},",
            r"\qquad \Lambda(X_D) = \frac{[(1-\phi_i)K_i]^{\alpha} s_i^L}"
            r"{r - \mu_L + \lambda}\, X_D",
            font_size=34,
        ).next_to(d_eq, DOWN, buff=0.6)
        rec[1].set_color(C_INFER)
        with self.voiceover(
            "Recovery is the liquidation value Lambda, net of bankruptcy"
            " costs b, capped at the default-free value of the coupon claim."
        ):
            self.play(Write(rec), run_time=1.8)
        with self.voiceover(
            "Look closely at Lambda: it capitalizes only the inference"
            " business, the L-regime revenue stream. The H-regime"
            " continuation, the faith-based component of A effective, is"
            " absent: the post-AGI payoff needs the going concern, its"
            " researchers and its training program, and does not transfer to"
            " creditors. Faith dies in bankruptcy."
        ):
            self.play(Indicate(rec[1], color=C_INFER), run_time=1.6)
        with self.voiceover(
            "The cap enforces absolute priority: creditors cannot collect more"
            " in default than their claim is worth default-free. Without it,"
            " a lightly levered firm, whose boundary is driven by operating"
            " costs rather than coupons, would hand its creditors a windfall."
        ):
            self.play(Indicate(rec[0], color=C_OPTION), run_time=1.4)

        faces = VGroup(
            Text(
                "training raises A_eff  ->  lower X_D  ->  fewer defaults",
                font_size=27,
                color=C_H,
            ),
            Text(
                "training shrinks Lambda  ->  lower recovery  ->  higher LGD",
                font_size=27,
                color=C_DEFAULT,
            ),
        ).arrange(DOWN, buff=0.35)
        faces.to_edge(DOWN, buff=0.7)
        with self.voiceover(
            "So training has two faces for credit risk: above the faith"
            " threshold it lowers the probability of default, but it also"
            " shrinks the liquidation value, raising the loss given default."
            " Training-heavy labs should default less often, and recover less"
            " when they do."
        ):
            self.play(FadeIn(faces[0]), run_time=1.0)
            self.play(FadeIn(faces[1]), run_time=1.0)
        self.pause(0.5)
        self.clear_body()


class P4S16BoundariesFigure(PaperScene):
    def construct(self):
        self.set_header("Leverage and the margin of safety", kicker="FIGURE")

        from ai_lab_investment.models.duopoly import DuopolyModel
        from ai_lab_investment.models.parameters import ModelParameters

        p = ModelParameters()
        leverages = np.linspace(0.05, 0.65, 13)
        x_f = np.full_like(leverages, np.nan)
        x_p = np.full_like(leverages, np.nan)
        x_d = np.full_like(leverages, np.nan)
        for i, lev in enumerate(leverages):
            duo = DuopolyModel(
                p, leverage=float(lev), coupon_rate=0.05, bankruptcy_cost=0.30
            )
            eq_d = duo.solve_preemption_equilibrium("H")
            x_f[i] = eq_d["X_follower"]
            x_p[i] = eq_d["X_leader"]
            x_d[i] = eq_d["X_default_follower"]

        ax = clean_axes([0.0, 0.70], [0, 0.24], width=9.4, height=4.6).shift(DOWN * 0.7)
        x_lab = MathTex(r"\ell", font_size=30, color=C_FAINT).next_to(
            ax.x_axis, RIGHT, buff=0.15
        )
        y_lab = MathTex(r"X", font_size=30, color=C_FAINT).next_to(
            ax.y_axis, UP, buff=0.15
        )
        with self.voiceover(
            "Last stop: the paper's default-boundaries figure, recomputed live"
            " from the duopoly model over leverage from five to sixty-five"
            " percent, with a five percent coupon and thirty percent"
            " bankruptcy costs."
        ):
            self.play(Create(ax), FadeIn(x_lab), FadeIn(y_lab), run_time=1.2)

        pts_up = [
            ax.coords_to_point(le, xf) for le, xf in zip(leverages, x_f, strict=True)
        ]
        pts_dn = [
            ax.coords_to_point(le, xd)
            for le, xd in zip(leverages[::-1], x_d[::-1], strict=True)
        ]
        region = Polygon(
            *pts_up, *pts_dn, stroke_width=0, fill_color=C_L, fill_opacity=0.15
        )
        f_line = ax.plot_line_graph(
            leverages, x_f, line_color=C_TEXT, add_vertex_dots=False
        )
        f_lab = MathTex(r"X_F^*", font_size=30, color=C_TEXT).next_to(
            ax.coords_to_point(0.65, x_f[-1]), RIGHT, buff=0.15
        )
        with self.voiceover(
            "The top line is the follower's entry trigger. It rises from about"
            " zero point one two at five percent leverage to about zero point"
            " two one at sixty-five: cheap debt-financed capital pushes"
            " optimal scale up, and the larger commitment needs higher demand"
            " to justify."
        ):
            self.play(Create(f_line), FadeIn(f_lab), run_time=1.8)

        d_line = ax.plot_line_graph(
            leverages, x_d, line_color=C_DEFAULT, add_vertex_dots=False
        )
        d_lab = MathTex(r"X_D", font_size=30, color=C_DEFAULT).next_to(
            ax.coords_to_point(0.65, x_d[-1]), RIGHT, buff=0.15
        )
        with self.voiceover(
            "The bottom line is the default boundary, which roughly triples"
            " over the same range as coupon obligations grow."
        ):
            self.play(Create(d_line), FadeIn(d_lab), run_time=1.6)

        p_line = ax.plot_line_graph(
            leverages, x_p, line_color=C_OPTION, add_vertex_dots=False
        )
        p_lab = MathTex(r"X_P", font_size=30, color=C_OPTION).next_to(
            ax.coords_to_point(0.65, x_p[-1] + 0.008), RIGHT, buff=0.15
        )
        with self.voiceover(
            "The gold line near the axis is the leader's preemption trigger,"
            " far below the follower's: that is the competition-compressed"
            " timing we prove in part five."
        ):
            self.play(Create(p_line), FadeIn(p_lab), run_time=1.4)

        ratio_lo = x_f[0] / x_d[0]
        ratio_hi = x_f[-1] / x_d[-1]
        with self.voiceover(
            "The shaded band between entry and default is the operating"
            " region. It widens in absolute terms as leverage rises."
        ):
            self.play(FadeIn(region), run_time=1.2)

        margin = MathTex(
            rf"\frac{{X_F^*}}{{X_D}}:\quad {ratio_lo:.0f}\ \to\ {ratio_hi:.0f}",
            font_size=36,
        ).move_to(ax.coords_to_point(0.22, 0.19))
        with self.voiceover(
            "But the relative margin of safety contracts sharply: the ratio of"
            " entry trigger to default boundary falls from about twelve to"
            " about six. A levered entrant can tolerate only half the"
            " proportional demand decline before hitting the boundary."
        ):
            self.play(Write(margin), run_time=1.6)
            self.play(Create(highlight(margin, color=C_DEFAULT)), run_time=0.6)

        with self.voiceover(
            "This compressed margin is exactly the scenario Amodei describes:"
            " commit to trillion-dollar compute purchases, and a modest"
            " revenue shortfall is enough to reach the boundary, because"
            " there is no hedge on Earth that bridges the gap."
        ):
            self.play(Indicate(margin, color=C_DEFAULT), run_time=1.4)
        self.pause(0.5)
        self.clear_body()


class P4S17Close(PaperScene):
    def construct(self):
        self.set_header("What we proved", kicker="PART 4 - CLOSE")

        items = VGroup(
            Text(
                "(i)    X_D rises with leverage and the coupon rate",
                font_size=27,
            ),
            Text(
                "(ii)   faith-based survival: X_D falls with lambda"
                " iff phi > phi-tilde ~ 0.32",
                font_size=27,
            ),
            Text(
                "(iii)  leverage-training substitution below phi*"
                " (mechanical, not causal)",
                font_size=27,
            ),
            Text(
                "(iv)   stronger rivals raise X_D",
                font_size=27,
            ),
            Text(
                "+ the single-boundary formula overstates X_D by ~3%: conservative",
                font_size=27,
                color=C_FAINT,
            ),
        ).arrange(DOWN, buff=0.4, aligned_edge=LEFT)
        items.shift(DOWN * 0.3)

        with self.voiceover(
            "To summarize part four: leverage and coupons raise the default"
            " boundary, and optimism lowers it precisely when the training"
            " fraction clears the exact threshold phi tilde, which the"
            " optimal allocation does whenever lambda exceeds about zero"
            " point zero three four."
        ):
            self.play(FadeIn(items[0], shift=RIGHT * 0.3), run_time=0.9)
            self.play(FadeIn(items[1], shift=RIGHT * 0.3), run_time=0.9)
        with self.voiceover(
            "Below the optimal allocation, leverage and training trade off"
            " along an iso-boundary locus, stronger rivals push the boundary"
            " up, and the whole construction errs on the conservative side by"
            " about three percent."
        ):
            self.play(FadeIn(items[2], shift=RIGHT * 0.3), run_time=0.9)
            self.play(FadeIn(items[3], shift=RIGHT * 0.3), run_time=0.9)
            self.play(FadeIn(items[4], shift=RIGHT * 0.3), run_time=0.9)
        self.pause(0.4)

        teaser = VGroup(
            Text("Next: Part 5", font_size=34, weight="BOLD", color=C_OPTION),
            Text(
                "the preemption equilibrium and Proposition 3:"
                " existence and uniqueness of X_P,",
                font_size=26,
                color=C_TEXT,
            ),
            Text(
                "rent equalization, and why the training fraction"
                " is invariant to competition",
                font_size=26,
                color=C_TEXT,
            ),
        ).arrange(DOWN, buff=0.3)
        teaser.shift(DOWN * 0.3)
        with self.voiceover(
            "Next, part five: the preemption game. We prove existence and"
            " uniqueness of the preemption trigger, derive rent equalization,"
            " and show the striking cancellation that makes the training"
            " fraction invariant to competitive position. See you there."
        ):
            self.clear_body()
            self.play(FadeIn(teaser), run_time=1.5)
        self.pause(0.8)
        self.clear_body()
        if self.header is not None:
            self.play(FadeOut(self.header), run_time=0.6)
            self.header = None
