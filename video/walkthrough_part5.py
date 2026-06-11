"""Walkthrough Part 5 (~20 min): the preemption equilibrium -- Proposition 3.

Covers the timing game, the follower's problem and its separable reduction
(Appendix B), the leader's problem and solution convention, the discounting
conventions, rent equalization, and the full proofs of Proposition 3(i)
(existence and uniqueness) and 3(ii) (role invariance), plus the numerical
findings (iii)-(v) and the competition-effect figure.

Render: just render-walkthrough
Draft a single scene:
    cd video && uv run manim render -ql walkthrough_part5.py P5S01Title
"""

from __future__ import annotations

import numpy as np
from manim import (
    DOWN,
    LEFT,
    RIGHT,
    UP,
    Arrow,
    Create,
    DashedLine,
    Dot,
    FadeIn,
    FadeOut,
    Indicate,
    Line,
    MathTex,
    RoundedRectangle,
    Text,
    VGroup,
    Write,
)
from scene_base import PaperScene
from theme import (
    C_COST,
    C_DEFAULT,
    C_DEMAND,
    C_FAINT,
    C_H,
    C_L,
    C_OPTION,
    C_TEXT,
    C_TRAIN,
    clean_axes,
    highlight,
)

SCENES = [
    "P5S01Title",
    "P5S02Game",
    "P5S03Follower",
    "P5S04Separable",
    "P5S05CapacityFOC",
    "P5S06Leader",
    "P5S07Discounting",
    "P5S08RentEqualization",
    "P5S09Existence",
    "P5S10Uniqueness",
    "P5S11RoleInvariance",
    "P5S12Numericals",
    "P5S13CompetitionEffect",
    "P5S14Close",
]


def _baseline_duopoly():
    """Zero-leverage baseline duopoly with the equilibrium objects used here."""
    from ai_lab_investment.models.duopoly import DuopolyModel
    from ai_lab_investment.models.parameters import ModelParameters

    params = ModelParameters()
    duo = DuopolyModel(params, leverage=0.0)
    return params, duo


class P5S01Title(PaperScene):
    def construct(self):
        kicker = Text("DERIVATION WALKTHROUGH", font_size=24, color=C_FAINT).shift(
            UP * 1.6
        )
        title = Text(
            "Part 5: The Preemption Equilibrium",
            font_size=44,
            weight="BOLD",
        ).shift(UP * 0.7)
        sub = Text("Proposition 3", font_size=30, color=C_OPTION).next_to(
            title, DOWN, buff=0.4
        )
        with self.voiceover(
            "Part five of the derivation walkthrough. This part covers the"
            " preemption equilibrium of the duopoly: Proposition three, its"
            " proofs, and the numerical findings that come with them."
        ):
            self.play(FadeIn(kicker), run_time=0.6)
            self.play(Write(title), run_time=1.6)
            self.play(FadeIn(sub), run_time=0.8)

        recap = VGroup(
            Text(
                "So far: single-firm trigger, capacity, and phi (Prop. 1);",
                font_size=26,
                color=C_TEXT,
            ),
            Text(
                "default boundary and faith-based survival (Prop. 2).",
                font_size=26,
                color=C_TEXT,
            ),
        ).arrange(DOWN, buff=0.2)
        recap.next_to(sub, DOWN, buff=0.8)
        with self.voiceover(
            "Earlier parts built the single-firm benchmark: trigger,"
            " capacity, and training fraction, then the default boundary and"
            " faith-based survival."
        ):
            self.play(FadeIn(recap), run_time=1.2)

        agenda = VGroup(
            Text("1. The timing game", font_size=24, color=C_FAINT),
            Text("2. Follower: separable reduction", font_size=24, color=C_FAINT),
            Text("3. Leader: convention and dilution", font_size=24, color=C_FAINT),
            Text("4. Rent equalization and the proofs", font_size=24, color=C_FAINT),
        ).arrange(DOWN, buff=0.18, aligned_edge=LEFT)
        agenda.next_to(recap, DOWN, buff=0.6)
        with self.voiceover(
            "Now we put two identical firms in the same market and let them"
            " race. The plan: the timing game, the follower, the leader, the"
            " preemption trigger, and then the proofs."
        ):
            self.play(FadeIn(agenda, shift=RIGHT * 0.3), run_time=1.2)
        self.pause(0.6)
        self.play(
            FadeOut(kicker),
            FadeOut(title),
            FadeOut(sub),
            FadeOut(recap),
            FadeOut(agenda),
            run_time=0.8,
        )


class P5S02Game(PaperScene):
    def construct(self):
        self.set_header("The timing game", kicker="5.1 SETUP")

        strat = MathTex(
            r"\text{firm } i\text{'s strategy:}\quad",
            r"\bigl(X_i^*,\; K_i,\; \phi_i\bigr)",
            font_size=40,
        ).shift(UP * 1.7)
        strat[1].set_color(C_OPTION)
        with self.voiceover(
            "We solve for a subgame perfect equilibrium of a timing game in"
            " continuous time. Each firm's strategy is a triple: an"
            " investment trigger, a capacity, and a training fraction."
        ):
            self.play(Write(strat), run_time=1.4)

        obs = Text(
            "investment is immediately and publicly observed (closed loop):",
            font_size=26,
            color=C_TEXT,
        ).next_to(strat, DOWN, buff=0.5)
        obs2 = MathTex(
            r"\text{the follower conditions on the leader's realized }",
            r"(K_L, \phi_L)",
            font_size=34,
        ).next_to(obs, DOWN, buff=0.25)
        obs2[1].set_color(C_L)
        with self.voiceover(
            "Investment is immediately and publicly observed. This"
            " closed-loop information structure lets the follower condition"
            " its best response on the leader's realized capacity and"
            " training fraction."
        ):
            self.play(FadeIn(obs), FadeIn(obs2), run_time=1.2)

        lineage = Text(
            "Fudenberg-Tirole (1985)  ->  Pawlina-Kort (2006), Huisman-Kort (2015)",
            font_size=24,
            color=C_FAINT,
        ).next_to(obs2, DOWN, buff=0.5)
        with self.voiceover(
            "The solution concept is the preemption construction of"
            " Fudenberg and Tirole, extended to asymmetric capacity choice"
            " by Pawlina and Kort and by Huisman and Kort."
        ):
            self.play(FadeIn(lineage), run_time=1.0)

        box1 = RoundedRectangle(corner_radius=0.15, width=4.6, height=1.1, color=C_H)
        t1 = Text(
            "1. follower best response\n(K_F, phi_F, X_F)",
            font_size=22,
            color=C_TEXT,
            line_spacing=0.9,
        ).move_to(box1)
        box2 = RoundedRectangle(
            corner_radius=0.15, width=4.6, height=1.1, color=C_OPTION
        )
        t2 = Text(
            "2. leader trigger from\nrent equalization L(X_P) = F(X_P)",
            font_size=22,
            color=C_TEXT,
            line_spacing=0.9,
        ).move_to(box2)
        g1 = VGroup(box1, t1)
        g2 = VGroup(box2, t2)
        VGroup(g1, g2).arrange(RIGHT, buff=1.2).to_edge(DOWN, buff=0.6)
        arr = Arrow(g1.get_right(), g2.get_left(), color=C_FAINT, buff=0.1)
        with self.voiceover(
            "The equilibrium is built by backward induction: first the"
            " follower's best response to any leader policy, then the"
            " leader's trigger from rent equalization."
        ):
            self.play(FadeIn(g1), run_time=0.9)
            self.play(Create(arr), FadeIn(g2), run_time=1.0)
        self.pause(0.3)
        self.clear_body()

        cond1 = MathTex(
            r"\text{(i)}\quad",
            r"L(X_P) \;\geq\; \text{value of investing simultaneously at } X_P",
            font_size=36,
        ).shift(UP * 1.0)
        with self.voiceover(
            "Two conditions from Huisman and Kort underwrite the"
            " construction. First, at the preemption trigger, leading is"
            " worth at least as much as investing simultaneously."
        ):
            self.play(Write(cond1), run_time=1.4)

        cond2 = MathTex(
            r"\text{(ii)}\quad",
            r"X_F^* \;>\; X_L",
            font_size=36,
        ).next_to(cond1, DOWN, buff=0.6)
        note = Text(
            "both verified numerically for every parameterization"
            " (incl. leverage and phi)",
            font_size=24,
            color=C_FAINT,
        ).next_to(cond2, DOWN, buff=0.5)
        with self.voiceover(
            "Second, the follower's optimal trigger lies strictly above the"
            " leader's, so the equilibrium really is sequential. Both"
            " conditions are verified numerically at every parameterization,"
            " including those with leverage and training allocation."
        ):
            self.play(Write(cond2), run_time=1.0)
            self.play(FadeIn(note), run_time=0.8)

        closing = Text(
            "richer strategy space -> richer payoffs, same preemption logic",
            font_size=26,
            color=C_TEXT,
        ).next_to(note, DOWN, buff=0.6)
        with self.voiceover(
            "The richer strategy space enriches the payoffs but preserves"
            " the sequential preemption logic."
        ):
            self.play(FadeIn(closing), run_time=1.0)
        self.pause(0.4)
        self.clear_body()


class P5S03Follower(PaperScene):
    def construct(self):
        self.set_header("The follower's problem", kicker="5.2 BACKWARD INDUCTION")

        setup = MathTex(
            r"\text{observes } (K_L, \phi_L)",
            r"\;\Rightarrow\;",
            r"\text{chooses } (K_F, \phi_F)",
            r"\text{ at exogenous } \ell",
            font_size=38,
        ).shift(UP * 1.9)
        setup[0].set_color(C_L)
        setup[2].set_color(C_H)
        with self.voiceover(
            "Start at the end of the game, with the follower. It observes"
            " the leader's capacity and training fraction, and chooses its"
            " own capacity and split, at the exogenous leverage ell."
        ):
            self.play(Write(setup), run_time=1.4)

        trig = MathTex(
            r"X_F^*(K_F, \phi_F)",
            r"=",
            r"\frac{\beta_H}{\beta_H - 1}",
            r"\cdot",
            r"\frac{\delta K_F/r + (1-\ell)\,cK_F^{\gamma} + c_D/r}"
            r"{A_{\mathrm{eff},F}(K_F, \phi_F)}",
            font_size=38,
        ).next_to(setup, DOWN, buff=0.6)
        trig[0].set_color(C_OPTION)
        with self.voiceover(
            "The trigger is not a separate choice variable: for every"
            " candidate capacity and split, smooth pasting pins it down as"
            " the familiar markup over cost to revenue, now with the duopoly"
            " revenue coefficient."
        ):
            self.play(Write(trig), run_time=1.8)
        self.pause(0.3)

        b1 = MathTex(
            r"b(K;\ell)",
            r"=",
            r"\frac{\delta K}{r} + (1-\ell)\,cK^{\gamma}"
            r" + \frac{c_d\,\ell\, cK^{\gamma}}{r}",
            font_size=36,
        ).next_to(trig, DOWN, buff=0.7)
        with self.voiceover(
            "Why is leverage held exogenous rather than optimized? Look at"
            " the cost side of the follower's objective: equity pays one"
            " minus ell of the investment cost, and the coupon obligation"
            " capitalizes to c d times ell times the cost, over r."
        ):
            self.play(Write(b1), run_time=1.6)

        b2 = MathTex(
            r"b(K;\ell)",
            r"=",
            r"\frac{\delta K}{r} + cK^{\gamma}",
            r"\Bigl[1 - \ell\Bigl(1 - \frac{c_d}{r}\Bigr)\Bigr]",
            font_size=36,
        ).move_to(b1)
        with self.voiceover(
            "Collect the K to the gamma terms: the bracket is one minus ell"
            " times one minus c d over r."
        ):
            self.play(FadeOut(b1), run_time=0.4)
            self.play(Write(b2), run_time=1.2)
            self.play(Create(highlight(b2[3])), run_time=0.7)

        db = MathTex(
            r"\frac{\partial b}{\partial \ell}",
            r"=",
            r"-\,cK^{\gamma}\Bigl(1 - \frac{c_d}{r}\Bigr)",
            r"\;<\; 0",
            r"\qquad (c_d < r)",
            font_size=36,
        ).next_to(b2, DOWN, buff=0.9)
        db[3].set_color(C_COST)
        with self.voiceover(
            "Differentiate with respect to ell. Because the coupon rate is"
            " below the discount rate, this derivative is strictly negative:"
            " par debt with a below-market coupon acts as a pure subsidy in"
            " this objective."
        ):
            self.play(Write(db), run_time=1.4)
        self.pause(0.3)
        self.clear_body()

        obj = MathTex(
            r"\text{objective:}\quad",
            r"h = \frac{A_{\mathrm{eff},F}^{\beta_H}}{b(K;\ell)^{\beta_H - 1}}",
            r"\quad\text{strictly increasing in } \ell",
            font_size=38,
        ).shift(UP * 0.8)
        with self.voiceover(
            "The option value factor is A effective to the beta H over cost"
            " to the beta H minus one, so a lower cost means a higher value:"
            " the objective is strictly increasing in leverage."
        ):
            self.play(Write(obj), run_time=1.6)

        corner = Text(
            "an unconstrained leverage choice would be a corner solution",
            font_size=28,
            color=C_COST,
        ).next_to(obj, DOWN, buff=0.6)
        fix = Text(
            "fix: fairly priced debt at issuance -- left for future work;"
            " leverage stays exogenous",
            font_size=24,
            color=C_FAINT,
        ).next_to(corner, DOWN, buff=0.35)
        with self.voiceover(
            "An unconstrained choice would run straight to the corner."
            " Endogenizing capital structure would require fairly priced"
            " debt at issuance, which the paper leaves for future work."
        ):
            self.play(FadeIn(corner), run_time=0.9)
            self.play(FadeIn(fix), run_time=0.8)
        self.pause(0.4)
        self.clear_body()


class P5S04Separable(PaperScene):
    def construct(self):
        self.set_header("Separable reduction of the follower", kicker="5.3 APPENDIX B")

        intro = Text(
            "evaluate the contest at a common training fraction phi_F = phi_L = phi",
            font_size=28,
            color=C_TEXT,
        ).shift(UP * 1.9)
        with self.voiceover(
            "The follower's two-dimensional problem hides an exact separable"
            " structure, derived in Appendix B. The key step is to evaluate"
            " the contest at a common training fraction."
        ):
            self.play(FadeIn(intro), run_time=1.0)

        eq1 = MathTex(
            r"\bigl[(1-\phi)K_F\bigr]^{\alpha} + \bigl[(1-\phi)K_L\bigr]^{\alpha}",
            r"=",
            r"(1-\phi)^{\alpha}",
            r"\bigl(K_F^{\alpha} + K_L^{\alpha}\bigr)",
            font_size=38,
        ).next_to(intro, DOWN, buff=0.55)
        eq1[2].set_color(C_TRAIN)
        with self.voiceover(
            "Take the L-regime Tullock denominator. If both firms run the"
            " same split phi, the common factor one minus phi to the alpha"
            " pulls out of both terms."
        ):
            self.play(Write(eq1), run_time=1.6)
            self.play(Create(highlight(eq1[2])), run_time=0.7)

        eq2 = MathTex(
            r"(\phi K_F)^{\alpha} + (\phi K_L)^{\alpha}",
            r"=",
            r"\phi^{\alpha}",
            r"\bigl(K_F^{\alpha} + K_L^{\alpha}\bigr)",
            font_size=38,
        ).next_to(eq1, DOWN, buff=0.45)
        eq2[2].set_color(C_TRAIN)
        with self.voiceover(
            "The same happens in the H regime with phi to the alpha: both"
            " contest denominators factor into an allocation part and a pure"
            " capacity part."
        ):
            self.play(Write(eq2), run_time=1.4)

        eq3 = MathTex(
            r"\frac{\bigl[(1-\phi)K_F\bigr]^{2\alpha}}"
            r"{\bigl[(1-\phi)K_F\bigr]^{\alpha} + \bigl[(1-\phi)K_L\bigr]^{\alpha}}",
            r"=",
            r"(1-\phi)^{\alpha}\,",
            r"\frac{K_F^{2\alpha}}{K_F^{\alpha} + K_L^{\alpha}}",
            font_size=38,
        ).next_to(eq2, DOWN, buff=0.55)
        eq3[3].set_color(C_H)
        with self.voiceover(
            "Each regime's contest revenue is the standalone revenue times"
            " the contest share: u to the two alpha over the sum of the"
            " alphas. Dividing the factored pieces, the follower's L-regime"
            " term reduces to one minus phi to the alpha, times a pure"
            " capacity contest."
        ):
            self.play(Write(eq3), run_time=1.8)
            self.play(Create(highlight(eq3[3], color=C_H)), run_time=0.7)
        self.pause(0.4)
        self.clear_body()

        aeff = MathTex(
            r"A_{\mathrm{eff},F}",
            r"=",
            r"\bigl[\,w_L (1-\phi)^{\alpha} + w_H\,\phi^{\alpha}\bigr]",
            r"\cdot",
            r"\frac{K_F^{2\alpha}}{K_F^{\alpha} + K_L^{\alpha}}",
            r"\;=\;",
            r"g(\phi)",
            r"\cdot",
            r"\frac{K_F^{2\alpha}}{K_F^{\alpha} + K_L^{\alpha}}",
            font_size=38,
        ).shift(UP * 1.2)
        aeff[2].set_color(C_TRAIN)
        aeff[6].set_color(C_TRAIN)
        aeff[4].set_color(C_H)
        aeff[8].set_color(C_H)
        wdefs = MathTex(
            r"w_L = \frac{1}{r - \mu_L + \lambda},\qquad"
            r" w_H = \frac{\lambda}{(r - \mu_L + \lambda)(r - \mu_H)}",
            font_size=30,
            color=C_FAINT,
        ).next_to(aeff, DOWN, buff=0.5)
        with self.voiceover(
            "Assemble the follower's effective revenue coefficient: the"
            " allocation factor and the capacity contest separate exactly."
            " It is g of phi times K F to the two alpha over the capacity"
            " denominator."
        ):
            self.play(Write(aeff), run_time=2.0)
        with self.voiceover(
            "This is the same g-times-capacity structure as Proposition one,"
            " with the single firm's K to the alpha replaced by the contest"
            " term. The weights w L and w H are the familiar regime"
            " capitalization factors."
        ):
            self.play(FadeIn(wdefs), run_time=1.0)
            self.play(Create(highlight(aeff[6:], color=C_OPTION)), run_time=0.8)

        foc = MathTex(
            r"\frac{\partial A_{\mathrm{eff},F}}{\partial \phi}",
            r"=",
            r"g'(\phi)\cdot \frac{K_F^{2\alpha}}{K_F^{\alpha} + K_L^{\alpha}}",
            r"= 0",
            r"\;\iff\;",
            r"g'(\phi) = 0",
            font_size=38,
        ).next_to(wdefs, DOWN, buff=0.6)
        foc[5].set_color(C_TRAIN)
        with self.voiceover(
            "Differentiate in phi: the capacity factor is a constant, so the"
            " allocation first-order condition is g prime of phi equals"
            " zero, exactly the single-firm condition of Proposition one."
        ):
            self.play(Write(foc), run_time=1.6)

        seed = Text(
            "the seed of role invariance -- full proof in Section 5.9",
            font_size=24,
            color=C_FAINT,
        ).next_to(foc, DOWN, buff=0.5)
        with self.voiceover(
            "That is the seed of role invariance, which we will prove in"
            " full generality later. Everything strategic now lives in one"
            " scalar object: the capacity contest term."
        ):
            self.play(FadeIn(seed), run_time=0.9)
        self.pause(0.4)
        self.clear_body()


class P5S05CapacityFOC(PaperScene):
    def construct(self):
        self.set_header(
            "Follower capacity: the elasticity wedge", kicker="5.4 APPENDIX B"
        )

        prob = MathTex(
            r"\max_{K_F}\; h(K_F)",
            r"=",
            r"\frac{A_{\mathrm{eff},F}(K_F)^{\beta_H}}{b(K_F)^{\beta_H - 1}}",
            font_size=38,
        ).shift(UP * 1.8)
        with self.voiceover(
            "Now the capacity choice. The follower maximizes the option"
            " value factor: A effective to the beta H over the cost to the"
            " beta H minus one."
        ):
            self.play(Write(prob), run_time=1.4)

        logfoc = MathTex(
            r"\beta_H\,",
            r"\frac{d\ln A_{\mathrm{eff},F}}{d\ln K_F}",
            r"=",
            r"(\beta_H - 1)\,\frac{K_F\, b'(K_F)}{b(K_F)}",
            font_size=38,
        ).next_to(prob, DOWN, buff=0.55)
        logfoc[1].set_color(C_H)
        with self.voiceover(
            "Take logs and set the derivative in log K to zero: beta H times"
            " the revenue elasticity equals beta H minus one times the cost"
            " elasticity, K b prime over b."
        ):
            self.play(Write(logfoc), run_time=1.6)

        lnA = MathTex(
            r"\ln \frac{K^{2\alpha}}{K^{\alpha} + K_L^{\alpha}}",
            r"=",
            r"2\alpha \ln K",
            r"-",
            r"\ln\bigl(K^{\alpha} + K_L^{\alpha}\bigr)",
            font_size=38,
        ).next_to(logfoc, DOWN, buff=0.55)
        with self.voiceover(
            "So we need the elasticity of the contest term. Write its log:"
            " two alpha log K, minus the log of the capacity denominator."
        ):
            self.play(Write(lnA), run_time=1.4)

        dln = MathTex(
            r"\frac{d}{d\ln K}\,\ln\bigl(K^{\alpha} + K_L^{\alpha}\bigr)",
            r"=",
            r"\frac{K \cdot \alpha K^{\alpha - 1}}{K^{\alpha} + K_L^{\alpha}}",
            r"=",
            r"\alpha\, s_F",
            font_size=38,
        ).next_to(lnA, DOWN, buff=0.5)
        dln[4].set_color(C_OPTION)
        with self.voiceover(
            "Differentiate the denominator term with respect to log K: the"
            " chain rule gives K times alpha K to the alpha minus one, over"
            " the denominator. That is exactly alpha times the follower's"
            " contest share s F."
        ):
            self.play(Write(dln), run_time=1.8)
            self.play(Create(highlight(dln[4])), run_time=0.6)

        elast = MathTex(
            r"\frac{d\ln A_{\mathrm{eff},F}}{d\ln K}",
            r"=",
            r"2\alpha - \alpha\, s_F",
            r"=",
            r"\alpha\,(2 - s_F)",
            font_size=40,
        ).next_to(dln, DOWN, buff=0.5)
        elast[4].set_color(C_H)
        with self.voiceover(
            "Subtract: the revenue elasticity is two alpha minus alpha s F,"
            " that is, alpha times two minus s F. This is the effective"
            " elasticity of the follower's contest revenue."
        ):
            self.play(Write(elast), run_time=1.4)
            self.play(Create(highlight(elast[4], color=C_H)), run_time=0.7)
        self.pause(0.4)
        self.clear_body()

        foc = MathTex(
            r"\alpha\,\beta_H\,\bigl(2 - s_F(K_F)\bigr)\, b(K_F)",
            r"=",
            r"(\beta_H - 1)\, K_F\, b'(K_F)",
            font_size=40,
        ).shift(UP * 1.8)
        bdef = MathTex(
            r"b(K) = \frac{\delta K}{r}"
            r" + c\Bigl[1 - \ell\Bigl(1 - \frac{c_d}{r}\Bigr)\Bigr] K^{\gamma},"
            r"\qquad s_F = \frac{K_F^{\alpha}}{K_F^{\alpha} + K_L^{\alpha}}",
            font_size=32,
            color=C_FAINT,
        ).next_to(foc, DOWN, buff=0.45)
        with self.voiceover(
            "Substituting the elasticity back gives the capacity first-order"
            " condition of Appendix B: alpha beta H times two minus s F"
            " times b, equals beta H minus one times K b prime, with the"
            " leverage-adjusted total cost b."
        ):
            self.play(Write(foc), run_time=1.6)
            self.play(FadeIn(bdef), run_time=1.0)

        bracket = MathTex(
            r"\Phi(K) \equiv \alpha\beta_H\,\bigl(2 - s_F(K)\bigr)"
            r" - (\beta_H - 1)\,\frac{K b'(K)}{b(K)}",
            r"\quad\text{strictly decreasing}",
            font_size=36,
        ).next_to(bdef, DOWN, buff=0.55)
        bracket[1].set_color(C_OPTION)
        mono = Text(
            "s_F increasing in K;  K b'/b rises from 1 (linear term)"
            " to gamma (convex term)",
            font_size=24,
            color=C_FAINT,
        ).next_to(bracket, DOWN, buff=0.35)
        with self.voiceover(
            "Uniqueness: collect everything in one bracket. The share s F is"
            " increasing in K, and the cost elasticity K b prime over b"
            " rises monotonically from one, when the linear term dominates,"
            " to gamma. So the bracket is strictly decreasing: at most one"
            " root."
        ):
            self.play(Write(bracket), run_time=1.8)
            self.play(FadeIn(mono), run_time=0.9)

        lim1 = MathTex(
            r"K \to 0:\quad \Phi \to 2\alpha\beta_H - (\beta_H - 1) > 0",
            r"\iff \frac{\beta_H - 1}{2\alpha\beta_H} < 1\;\;(\approx 0.45)",
            font_size=32,
        ).next_to(mono, DOWN, buff=0.45)
        with self.voiceover(
            "Well-posedness needs the bracket to start positive and end"
            " negative. As K goes to zero, the share vanishes and the"
            " elasticity is two alpha: the condition is beta H minus one"
            " over two alpha beta H less than one, about zero point four"
            " five at baseline."
        ):
            self.play(Write(lim1), run_time=1.6)

        lim2 = MathTex(
            r"K \to \infty:\quad \Phi \to \alpha\beta_H - (\beta_H - 1)\gamma < 0",
            r"\iff \frac{\beta_H - 1}{\alpha\beta_H} > \frac{1}{\gamma}"
            r"\;\;(0.89 > 0.67)",
            font_size=32,
        ).next_to(lim1, DOWN, buff=0.35)
        with self.voiceover(
            "As K grows, the share tends to one and the cost elasticity to"
            " gamma: the condition is beta H minus one over alpha beta H"
            " greater than one over gamma; zero point eight nine against"
            " zero point six seven at baseline. Both hold."
        ):
            self.play(Write(lim2), run_time=1.6)
        self.pause(0.4)
        self.clear_body()

        wedge = MathTex(
            r"\alpha\,(2 - s_F) \;>\; \alpha",
            r"\qquad\text{(small } K\text{: elasticity } \to 2\alpha)",
            font_size=42,
        ).shift(UP * 1.4)
        wedge[0].set_color(C_H)
        with self.voiceover(
            "And here is the economics. The effective elasticity alpha times"
            " two minus s F is strictly greater than alpha, and at small"
            " scale it approaches two alpha: every unit of capacity earns"
            " standalone revenue and steals contest share from the leader."
        ):
            self.play(Write(wedge), run_time=1.4)

        nums = MathTex(
            r"K_F \approx 0.26 \;\;\text{vs}\;\; K_L \approx 0.0067"
            r"\;\;(\approx 38\times)",
            r"\qquad X_F^* \approx 0.12 \approx 44\, X_P",
            font_size=36,
        ).next_to(wedge, DOWN, buff=0.7)
        nums[0].set_color(C_TEXT)
        nums[1].set_color(C_OPTION)
        with self.voiceover(
            "That wedge is why the follower dwarfs the leader: capacity"
            " around zero point two six against zero point zero zero six"
            " seven, roughly thirty-eight times larger, with entry at X F of"
            " about zero point one two, some forty-four times the preemption"
            " trigger."
        ):
            self.play(Write(nums), run_time=1.6)

        wellposed = Text(
            "the 2-alpha small-K elasticity keeps the follower's problem"
            " well posed\neven where the single-firm problem (A2) degenerates",
            font_size=24,
            color=C_FAINT,
            line_spacing=1.0,
        ).next_to(nums, DOWN, buff=0.6)
        with self.voiceover(
            "And because the small-K elasticity is doubled, this condition"
            " is weaker than A two's upper bound: the follower stays well"
            " posed where the single-firm problem degenerates."
        ):
            self.play(FadeIn(wellposed), run_time=1.0)
        self.pause(0.4)
        self.clear_body()


class P5S06Leader(PaperScene):
    def construct(self):
        self.set_header("The leader's problem", kicker="5.5 BACKWARD INDUCTION")

        nl = Line(LEFT * 5.5, RIGHT * 5.5, color=C_FAINT).shift(UP * 1.4)
        tick_p = Line(UP * 0.15, DOWN * 0.15, color=C_OPTION).move_to(
            nl.get_center() + LEFT * 3.5
        )
        tick_f = Line(UP * 0.15, DOWN * 0.15, color=C_H).move_to(
            nl.get_center() + RIGHT * 2.5
        )
        lab_p = MathTex(r"X_P", font_size=32, color=C_OPTION).next_to(
            tick_p, DOWN, buff=0.2
        )
        lab_f = MathTex(r"X_F", font_size=32, color=C_H).next_to(tick_f, DOWN, buff=0.2)
        mono_lab = MathTex(
            r"\text{monopoly: } s_L = 1", font_size=30, color=C_TEXT
        ).move_to(nl.get_center() + LEFT * 0.5 + UP * 0.5)
        duo_lab = MathTex(
            r"\text{duopoly: } s_L^L,\, s_L^H < 1", font_size=30, color=C_TEXT
        ).move_to(nl.get_center() + RIGHT * 4.3 + UP * 0.5)
        with self.voiceover(
            "Step two of the backward induction: the leader. Until the"
            " follower enters at X F, the leader is a monopolist, with both"
            " contest shares equal to one. After X F, revenue is shared"
            " through the regime-specific contests."
        ):
            self.play(Create(nl), run_time=0.7)
            self.play(
                Create(tick_p),
                FadeIn(lab_p),
                Create(tick_f),
                FadeIn(lab_f),
                run_time=1.0,
            )
            self.play(FadeIn(mono_lab), FadeIn(duo_lab), run_time=1.0)

        val = MathTex(
            r"E_L(X)",
            r"=",
            r"E^{\mathrm{mono}}(X)",
            r"-",
            r"\underbrace{\bigl[V^{\mathrm{mono}}(X_F)"
            r" - V^{\mathrm{duo}}(X_F)\bigr]}_{\text{revenue drop at entry}}",
            r"\;\underbrace{\left(\frac{X}{X_F}\right)^{\beta_H}}"
            r"_{\text{entry discount}}",
            font_size=38,
        ).shift(DOWN * 0.6)
        val[2].set_color(C_L)
        val[4].set_color(C_COST)
        val[5].set_color(C_OPTION)
        with self.voiceover(
            "The leader's value carries both phases: start from the"
            " monopoly-phase equity, and subtract the present value of the"
            " revenue drop at follower entry."
        ):
            self.play(Write(val[0:3]), run_time=1.2)
        with self.voiceover(
            "The drop is the monopoly value minus the duopoly value,"
            " evaluated at the follower's trigger, and it is brought back to"
            " today with the stochastic discount factor X over X F, raised"
            " to the beta H."
        ):
            self.play(Write(val[3:]), run_time=1.8)
        self.pause(0.4)
        self.clear_body()

        conv = MathTex(
            r"(K_L, \phi_L) \;=\; \text{monopoly-phase optimum}"
            r" \;=\; \text{single-firm optimum (Prop. 1)}",
            font_size=36,
        ).shift(UP * 1.3)
        with self.voiceover(
            "What about the leader's own capacity and split? By convention,"
            " they solve the monopoly-phase problem, in which the"
            " Proposition one separability holds exactly, so K L and phi L"
            " coincide with the single-firm optimum."
        ):
            self.play(Write(conv), run_time=1.6)

        caveat = VGroup(
            Text(
                "caveat: a solution convention, not a result",
                font_size=28,
                color=C_COST,
            ),
            Text(
                "re-optimizing scale for entry at X_P < X_L^mono would give"
                " smaller capacity",
                font_size=24,
                color=C_TEXT,
            ),
            Text(
                "(earlier entry warrants smaller scale)",
                font_size=24,
                color=C_FAINT,
            ),
        ).arrange(DOWN, buff=0.22)
        caveat.next_to(conv, DOWN, buff=0.55)
        with self.voiceover(
            "Be clear about the caveat: this is a solution convention, not a"
            " result. Re-optimizing scale for entry at the preemption"
            " trigger, which lies below the unconstrained trigger, would"
            " imply a somewhat smaller capacity, because earlier entry"
            " warrants smaller scale."
        ):
            self.play(FadeIn(caveat), run_time=1.4)

        why = Text(
            "keeps the leader comparable to Prop. 1; does not affect rent equalization",
            font_size=26,
            color=C_TEXT,
        ).next_to(caveat, DOWN, buff=0.5)
        with self.voiceover(
            "The convention keeps the leader's policy directly comparable to"
            " Proposition one, and it does not affect the rent-equalization"
            " logic that pins down the preemption trigger."
        ):
            self.play(FadeIn(why), run_time=1.0)

        uncond = Text(
            "X_F is computed in the unconditional A_eff framework"
            " (not regime-contingent)",
            font_size=24,
            color=C_FAINT,
        ).next_to(why, DOWN, buff=0.45)
        with self.voiceover(
            "One more modeling choice: the follower's entry trigger is"
            " computed in the unconditional A effective framework rather"
            " than regime by regime; a fully state-dependent version would"
            " carry separate L and H triggers linked by the switching"
            " intensity."
        ):
            self.play(FadeIn(uncond), run_time=1.0)
        self.pause(0.4)
        self.clear_body()


class P5S07Discounting(PaperScene):
    def construct(self):
        self.set_header("Discounting conventions", kicker="5.6 APPENDIX B")

        conv = MathTex(
            r"\text{follower's option: } B_F\, X^{\beta_H}",
            r"\qquad\text{leader's dilution: } \left(\frac{X}{X_F}\right)^{\beta_H}",
            font_size=36,
        ).shift(UP * 1.8)
        conv[0].set_color(C_OPTION)
        conv[1].set_color(C_L)
        with self.voiceover(
            "Appendix B makes the discounting convention explicit, and it is"
            " worth dwelling on. Every option-like term in the L regime is"
            " valued with the H-regime exponent beta H: the follower's"
            " option, and the leader's dilution factor."
        ):
            self.play(Write(conv), run_time=1.8)

        alt = MathTex(
            r"\text{alternative: first-passage factor }",
            r"\left(\frac{X}{X_F}\right)^{\beta_L^+}",
            r"\quad\text{(conditions on no switch before entry)}",
            font_size=34,
        ).next_to(conv, DOWN, buff=0.6)
        alt[1].set_color(C_COST)
        with self.voiceover(
            "The natural alternative would be a first-passage factor with"
            " exponent beta L plus: the value of one unit paid when X first"
            " reaches X F, conditional on no regime switch happening before"
            " entry."
        ):
            self.play(Write(alt), run_time=1.6)

        a3 = MathTex(
            r"\text{under (A3):}\quad F_L(X) = C\, X^{\beta_H}",
            r"\quad\text{(pure power form)}",
            font_size=38,
        ).next_to(alt, DOWN, buff=0.6)
        a3[0].set_color(C_H)
        with self.voiceover(
            "But under assumption A three, the model's own pre-switch option"
            " value has the pure power form C times X to the beta H: the"
            " homogeneous beta L plus component is exactly the piece the"
            " assumption removes."
        ):
            self.play(Write(a3), run_time=1.4)

        nums = MathTex(
            r"\beta_H \approx 1.55,\qquad \beta_L^+ \approx 3.01",
            font_size=34,
            color=C_FAINT,
        ).next_to(a3, DOWN, buff=0.45)
        with self.voiceover(
            "So valuing the follower's option and the leader's dilution with"
            " beta H prices state-contingent payoffs consistently with the"
            " model's own option valuation. And the exponents are far apart:"
            " about three against one point five five."
        ):
            self.play(FadeIn(nums), run_time=1.0)
        self.pause(0.4)
        self.clear_body()

        approx = MathTex(
            r"\text{follower trigger: smooth pasting on }",
            r"A_{\mathrm{eff}}\, X - [\text{total cost}]",
            font_size=36,
        ).shift(UP * 1.0)
        approx[1].set_color(C_TEXT)
        with self.voiceover(
            "A second, related approximation: the follower's trigger is"
            " obtained from smooth pasting on the linear entry payoff, A"
            " effective times X minus total cost, omitting the small"
            " default-option term in the levered entry payoff."
        ):
            self.play(Write(approx), run_time=1.4)

        bound = MathTex(
            r"\text{omitted term: }",
            r"\left(\frac{X_F}{X_D}\right)^{\beta_s^-} \approx 0.015"
            r"\ \text{ at } \ell = 0.65",
            r"\quad\text{(vanishes at } \ell = 0\text{)}",
            font_size=34,
        ).next_to(approx, DOWN, buff=0.6)
        bound[1].set_color(C_DEFAULT)
        with self.voiceover(
            "The omitted piece is tiny: even at the highest leverage"
            " considered, X F over X D to the beta s minus is about zero"
            " point zero one five, so at most about one and a half percent"
            " of the default claim, and it vanishes exactly at zero"
            " leverage."
        ):
            self.play(Write(bound), run_time=1.6)
        self.pause(0.4)
        self.clear_body()


class P5S08RentEqualization(PaperScene):
    def construct(self):
        self.set_header("Rent equalization", kicker="5.7 THE PREEMPTION TRIGGER")

        sym = Text(
            "common beliefs (same lambda), symmetric equilibrium: both want to lead",
            font_size=28,
            color=C_TEXT,
        ).shift(UP * 2.0)
        with self.voiceover(
            "Now the heart of the equilibrium. Both firms share the same"
            " lambda and the game is symmetric, so both would like to be the"
            " leader."
        ):
            self.play(FadeIn(sym), run_time=1.0)

        eqn = MathTex(r"L(X_P) = F(X_P)", font_size=44, color=C_OPTION).next_to(
            sym, DOWN, buff=0.4
        )
        with self.voiceover(
            "The preemption trigger X P is the demand level at which the"
            " leader's value equals the follower's option value: rent"
            " equalization."
        ):
            self.play(Write(eqn), run_time=1.2)

        with self.voiceover(
            "Below X P, leading is worth less than following, so nobody"
            " moves. Above it, leading is strictly better, so each firm"
            " would jump in just ahead of its rival: the rent from leading"
            " is competed away, all the way down to X P."
        ):
            self.play(Indicate(eqn, color=C_OPTION), run_time=1.4)

        _params, duo = _baseline_duopoly()
        X_mono, K_L, phi_L, lev_L = duo.solve_leader_monopolist("H")
        eq = duo.solve_preemption_equilibrium("H")
        X_P = eq["X_leader"]

        xs = np.linspace(1e-4, 0.008, 90)
        L_vals = np.array([duo._leader_value_at(x, K_L, phi_L, lev_L) for x in xs])
        F_vals = np.array([duo.follower_option_value(x, K_L, phi_L, "H") for x in xs])
        y_max = float(max(L_vals.max(), F_vals.max())) * 1.12

        ax = clean_axes(
            x_range=[0, xs[-1]], y_range=[0, y_max], width=9.2, height=3.6
        ).shift(DOWN * 1.15)
        x_lab = (
            MathTex(r"X", font_size=30, color=C_FAINT)
            .next_to(ax.x_axis, RIGHT, buff=0.2)
            .shift(UP * 0.3)
        )
        l_line = ax.plot_line_graph(xs, L_vals, line_color=C_L, add_vertex_dots=False)
        f_line = ax.plot_line_graph(
            xs, F_vals, line_color=C_OPTION, add_vertex_dots=False
        )
        i_l = int(np.argmin(np.abs(xs - 0.0066)))
        i_f = int(np.argmin(np.abs(xs - 0.0073)))
        l_lab = MathTex(r"L(X)", font_size=32, color=C_L).move_to(
            ax.coords_to_point(0.0066, float(L_vals[i_l])) + UP * 0.5
        )
        f_lab = MathTex(r"F(X)", font_size=32, color=C_OPTION).move_to(
            ax.coords_to_point(0.0073, float(F_vals[i_f])) + DOWN * 0.45
        )
        with self.voiceover(
            "Here are the two curves at the baseline, computed from the"
            " model code. Gold is the follower's option value, a pure power"
            " function of X; blue is the leader's net value of entering."
        ):
            self.play(FadeOut(sym), run_time=0.5)
            self.play(Create(ax), FadeIn(x_lab), run_time=0.8)
            self.play(Create(f_line), FadeIn(f_lab), run_time=1.4)
            self.play(Create(l_line), FadeIn(l_lab), run_time=1.4)

        xp_line = DashedLine(
            ax.coords_to_point(X_P, 0),
            ax.coords_to_point(X_P, y_max * 0.85),
            color=C_OPTION,
        )
        xp_lab = MathTex(r"X_P \approx 0.0027", font_size=28, color=C_OPTION).next_to(
            ax.coords_to_point(X_P, 0), DOWN, buff=0.22
        )
        xm_line = DashedLine(
            ax.coords_to_point(X_mono, 0),
            ax.coords_to_point(X_mono, y_max * 0.55),
            color=C_FAINT,
        )
        xm_lab = MathTex(
            r"X_L^{\mathrm{mono}} \approx 0.0047", font_size=26, color=C_FAINT
        ).next_to(ax.coords_to_point(X_mono, 0), DOWN, buff=0.24)
        dot = Dot(
            ax.coords_to_point(X_P, duo.follower_option_value(X_P, K_L, phi_L, "H")),
            color=C_OPTION,
        )
        with self.voiceover(
            "They cross at X P, about zero point zero zero two seven:"
            " roughly fifty-seven percent of the monopoly trigger of zero"
            " point zero zero four seven."
        ):
            self.play(
                Create(xp_line), FadeIn(xp_lab), FadeIn(dot, scale=2), run_time=1.2
            )
            self.play(Create(xm_line), FadeIn(xm_lab), run_time=1.0)

        note = Text(
            "cross-sectional variation = comparative statics in lambda,"
            " not equilibrium mixing",
            font_size=24,
            color=C_FAINT,
        ).to_edge(DOWN, buff=0.12)
        with self.voiceover(
            "A note on interpretation: cross-sectional differences in"
            " investment behavior come from comparative statics in lambda"
            " across firm archetypes, not from equilibrium mixing between"
            " optimists and pessimists inside the game."
        ):
            self.play(FadeIn(note), run_time=1.0)
        self.pause(0.4)
        self.clear_body()


class P5S09Existence(PaperScene):
    def construct(self):
        self.set_header("Proposition 3(i): existence", kicker="5.8 PROOF")

        intro = Text(
            "an intermediate value argument (Huisman-Kort Thm. 1, enriched payoffs)",
            font_size=26,
            color=C_TEXT,
        ).shift(UP * 2.0)
        with self.voiceover(
            "Proposition three part one, existence, is fully analytical. It"
            " is an intermediate value argument, following Huisman and"
            " Kort's theorem one, applied to the enriched payoff functions."
        ):
            self.play(FadeIn(intro), run_time=1.0)

        defs = MathTex(
            r"L(X) = E_L(X) - (1-\ell)\, I(K_L),",
            r"\qquad F(X) = B_F\, X^{\beta_H},\;\; F(0) = 0",
            font_size=36,
        ).next_to(intro, DOWN, buff=0.5)
        defs[0].set_color(C_L)
        defs[1].set_color(C_OPTION)
        with self.voiceover(
            "Define L of X as the leader's NPV of entering at X: the"
            " going-concern equity value minus the equity share of the"
            " investment cost. The follower's option value F is proportional"
            " to X to the beta H, so F of zero is zero."
        ):
            self.play(Write(defs), run_time=1.8)

        props = VGroup(
            Text(
                "L continuous; increasing for X > X_D"
                " (linear L-revenue + positive option term)",
                font_size=24,
                color=C_TEXT,
            ),
            Text(
                "for X <= X_D: default, E_L = 0, so L = -(1-l) I(K_L) < 0",
                font_size=24,
                color=C_TEXT,
            ),
            Text(
                "F continuous, increasing, convex (beta_H > 1)",
                font_size=24,
                color=C_TEXT,
            ),
        ).arrange(DOWN, buff=0.25, aligned_edge=LEFT)
        props.next_to(defs, DOWN, buff=0.5)
        with self.voiceover(
            "L is continuous, and above the default boundary it is"
            " increasing: L-regime revenue is linear in X and the H-regime"
            " transition adds a positive option component. At or below X D"
            " the firm has defaulted, equity is worthless, and L equals"
            " minus the sunk equity contribution."
        ):
            self.play(FadeIn(props[0]), run_time=0.8)
            self.play(FadeIn(props[1]), run_time=0.8)
        with self.voiceover(
            "The follower's option value is continuous, increasing, and"
            " convex, because beta H exceeds one."
        ):
            self.play(FadeIn(props[2]), run_time=0.8)
        self.pause(0.3)
        self.clear_body()

        b0 = MathTex(
            r"X = 0:\qquad",
            r"L(0) = -(1-\ell)\, I(K_L) \;<\; 0 \;=\; F(0)",
            font_size=38,
        ).shift(UP * 1.5)
        b0[1].set_color(C_TEXT)
        with self.voiceover(
            "Boundary one, the origin: L of zero is minus one minus ell"
            " times the investment cost, strictly negative, while F of zero"
            " is zero. So F sits above L."
        ):
            self.play(Write(b0), run_time=1.4)

        b1 = MathTex(
            r"X = X_L^{\mathrm{mono}}:\qquad",
            r"L\bigl(X_L^{\mathrm{mono}}\bigr) \;>\; F\bigl(X_L^{\mathrm{mono}}\bigr)",
            font_size=38,
        ).next_to(b0, DOWN, buff=0.55)
        b1[1].set_color(C_TEXT)
        why1 = MathTex(
            r"\text{full monopoly-phase rent: dilution factor }"
            r"\bigl(X_L^{\mathrm{mono}}/X_F\bigr)^{\beta_H} \approx 0.007",
            font_size=30,
            color=C_FAINT,
        ).next_to(b1, DOWN, buff=0.35)
        with self.voiceover(
            "Boundary two, the leader's own unconstrained trigger. Investing"
            " as leader there earns essentially the full monopoly-phase"
            " rent: the follower's entry lies far away, so the dilution"
            " factor X mono over X F to the beta H is tiny, about zero point"
            " zero zero seven at baseline."
        ):
            self.play(Write(b1), run_time=1.4)
            self.play(FadeIn(why1), run_time=1.0)

        why2 = Text(
            "while F reflects only a diluted duopoly payoff, discounted"
            " all the way from X_F",
            font_size=24,
            color=C_FAINT,
        ).next_to(why1, DOWN, buff=0.35)
        with self.voiceover(
            "The follower's option at the same point reflects only a diluted"
            " duopoly payoff, discounted all the way from X F. Numerically,"
            " L exceeds F there at every parameterization tested."
        ):
            self.play(FadeIn(why2), run_time=1.0)

        ivt = MathTex(
            r"\Rightarrow\;\;\exists\, X_P \in \bigl(0,\, X_L^{\mathrm{mono}}\bigr):"
            r"\quad L(X_P) = F(X_P)",
            font_size=40,
        ).next_to(why2, DOWN, buff=0.55)
        ivt.set_color(C_OPTION)
        box = highlight(ivt)
        with self.voiceover(
            "Continuity plus a sign change is all the intermediate value"
            " theorem needs: there exists a preemption trigger strictly"
            " between zero and the monopoly trigger where L equals F."
        ):
            self.play(Write(ivt), run_time=1.4)
            self.play(Create(box), run_time=0.7)
        self.pause(0.4)
        self.clear_body()


class P5S10Uniqueness(PaperScene):
    def construct(self):
        self.set_header("Proposition 3(i): uniqueness", kicker="5.8 PROOF")

        intro = Text(
            "Huisman-Kort: L roughly affine, F convex with F(0) > L(0)"
            " => at most one up-crossing",
            font_size=24,
            color=C_TEXT,
        ).shift(UP * 2.0)
        with self.voiceover(
            "Uniqueness is where it gets interesting. In Huisman and Kort,"
            " an affine leader value against a convex follower value gives"
            " at most one up-crossing; at zero leverage, that logic becomes"
            " an exact proof here."
        ):
            self.play(FadeIn(intro), run_time=1.0)

        gap = MathTex(
            r"L(X) - F(X)",
            r"=",
            r"A_{\mathrm{eff}}^{\mathrm{mono}}\, X",
            r"-",
            r"\Bigl[\frac{\delta K_L}{r} + I(K_L)\Bigr]",
            r"-",
            r"E\, X^{\beta_H}",
            r"\qquad\text{on } (0, X_F)",
            font_size=38,
        ).next_to(intro, DOWN, buff=0.5)
        gap[2].set_color(C_L)
        gap[4].set_color(C_COST)
        gap[6].set_color(C_OPTION)
        with self.voiceover(
            "On the interval up to the follower's trigger, the zero-leverage"
            " gap has a closed form: a linear revenue term, minus the"
            " leader's total entry cost, minus E times X to the beta H."
        ):
            self.play(Write(gap), run_time=2.0)

        edef = MathTex(
            r"E",
            r"=",
            r"\frac{V^{\mathrm{mono}}(X_F) - V^{\mathrm{duo}}(X_F)}{X_F^{\beta_H}}",
            r"+",
            r"B_F",
            r"\;>\; 0",
            font_size=38,
        ).next_to(gap, DOWN, buff=0.55)
        edef[2].set_color(C_COST)
        edef[4].set_color(C_OPTION)
        with self.voiceover(
            "The coefficient E collects two pieces: the dilution loss, the"
            " monopoly value minus the duopoly value at follower entry,"
            " scaled by X F to the beta H, plus the follower's option"
            " coefficient B F."
        ):
            self.play(Write(edef), run_time=1.6)
        with self.voiceover(
            "Both pieces are positive. The monopoly value exceeds the"
            " duopoly value at X F, because a contest share below one of the"
            " same revenue stream is worth strictly less; and B F is a"
            " positive option coefficient. So E is strictly positive."
        ):
            self.play(Create(highlight(edef[2], color=C_COST)), run_time=0.7)
            self.play(Create(highlight(edef[4], color=C_OPTION)), run_time=0.7)

        second = MathTex(
            r"\frac{d^2}{dX^2}\bigl[L(X) - F(X)\bigr]",
            r"=",
            r"-\,E\,\beta_H(\beta_H - 1)\, X^{\beta_H - 2}",
            r"\;<\; 0",
            font_size=38,
        ).next_to(edef, DOWN, buff=0.55)
        second[3].set_color(C_H)
        with self.voiceover(
            "Differentiate the gap twice: the linear part dies, and what"
            " remains is minus E beta H times beta H minus one, times X to"
            " the beta H minus two. Strictly negative, because beta H"
            " exceeds one and E is positive: the gap is strictly concave."
        ):
            self.play(Write(second), run_time=1.8)
        self.pause(0.4)
        self.clear_body()

        params, duo = _baseline_duopoly()
        p = params
        beta = p.beta_H
        _X_mono, K_L, phi_L, _lev_L = duo.solve_leader_monopolist("H")
        X_F, K_F, phi_F, _lev_F = duo.solve_follower(K_L, phi_L)
        A = duo._effective_revenue_coeff(phi_L, K_L, 0.0, 0.0, monopolist=True)
        N = p.delta * K_L / p.r + duo.investment_cost(K_L)
        B_F = duo._follower_value(X_F, K_F, phi_F, K_L, phi_L, 0.0) / X_F**beta
        E = (
            duo.monopolist_value_L(X_F, phi_L, K_L)
            - duo.installed_value_L(X_F, phi_L, K_L, phi_F, K_F)
        ) / X_F**beta + B_F

        xs = np.linspace(1e-5, 0.018, 240)
        gvals = A * xs - N - E * xs**beta
        y_min, y_max = float(gvals.min()) * 1.15, float(gvals.max()) * 1.5

        ax = clean_axes(
            x_range=[0, xs[-1]], y_range=[y_min, y_max], width=9.4, height=3.3
        ).shift(DOWN * 0.85)
        zero_line = DashedLine(
            ax.coords_to_point(0, 0),
            ax.coords_to_point(xs[-1], 0),
            color=C_FAINT,
            stroke_width=2,
        )
        curve = ax.plot_line_graph(xs, gvals, line_color=C_H, add_vertex_dots=False)
        g_lab = MathTex(r"L(X) - F(X)", font_size=32, color=C_H).move_to(
            ax.coords_to_point(0.0128, y_max * 0.82)
        )
        with self.voiceover(
            "Here is that closed-form gap at the baseline, computed from the"
            " model coefficients. It starts negative, at minus the entry"
            " cost, and bends down everywhere: strict concavity."
        ):
            self.play(Create(ax), Create(zero_line), run_time=0.9)
            self.play(Create(curve), FadeIn(g_lab), run_time=1.8)

        from scipy import optimize as sciopt

        X_P = float(sciopt.brentq(lambda x: A * x - N - E * x**beta, 1e-6, 0.01))
        X_dn = float(sciopt.brentq(lambda x: A * x - N - E * x**beta, 0.01, 0.018))
        up_dot = Dot(ax.coords_to_point(X_P, 0), color=C_OPTION)
        up_lab = MathTex(r"X_P", font_size=30, color=C_OPTION).next_to(
            up_dot, UP + LEFT, buff=0.12
        )
        with self.voiceover(
            "A strictly concave function that starts negative crosses zero"
            " from below at most once. Existence gave one up-crossing;"
            " concavity says it is the only one. That is the zero-leverage"
            " uniqueness proof, and the crossing is exactly the X P from the"
            " previous scene."
        ):
            self.play(FadeIn(up_dot, scale=2), FadeIn(up_lab), run_time=1.0)

        lev_note = MathTex(
            r"\ell > 0:\quad \text{default option } \propto X^{\beta_s^-}"
            r"\;\;(\beta_s^- < 0):\ \text{convex near } X_D,\ \text{kink at } X_D",
            font_size=30,
        ).to_edge(DOWN, buff=0.3)
        lev_note.set_color(C_DEFAULT)
        with self.voiceover(
            "With leverage the picture is messier: the default option adds a"
            " term proportional to X to the beta s minus, with a positive"
            " coefficient. That term is strictly convex and explodes near"
            " the default boundary, breaking global concavity, and the"
            " default kink at X D adds a non-smooth point."
        ):
            self.play(Write(lev_note), run_time=1.6)

        comp_note = Text(
            "ell > 0: 500-point grid on (X_D, X_L^mono); exactly one"
            " up-crossing, all parameterizations",
            font_size=24,
            color=C_FAINT,
        ).next_to(lev_note, UP, buff=0.25)
        with self.voiceover(
            "So for positive leverage, uniqueness is verified"
            " computationally: five hundred grid points between X D and the"
            " monopoly trigger, exactly one up-crossing, with no exception"
            " across all parameterizations tested."
        ):
            self.play(FadeIn(comp_note), run_time=1.0)

        dn_dot = Dot(ax.coords_to_point(X_dn, 0), color=C_COST)
        dn_lab = Text(
            "far-out down-crossing (moot)", font_size=22, color=C_COST
        ).next_to(dn_dot, UP + RIGHT, buff=0.15)
        with self.voiceover(
            "One loose end: far above the monopoly trigger the gap turns"
            " negative again, because the leader's policy is held at the"
            " monopoly-phase optimum, too small a scale for entry at very"
            " high demand."
        ):
            self.play(FadeIn(dn_dot, scale=2), FadeIn(dn_lab), run_time=1.0)
        with self.voiceover(
            "That second crossing is moot: for any X above X P, each firm"
            " strictly prefers leading, so investment happens at X P and the"
            " high-demand region is never reached without entry having"
            " occurred."
        ):
            self.play(Indicate(up_dot, color=C_OPTION, scale_factor=2.0), run_time=1.2)
        self.pause(0.4)
        self.clear_body()


class P5S11RoleInvariance(PaperScene):
    def construct(self):
        self.set_header("Proposition 3(ii): role invariance", kicker="5.9 PROOF")

        leader = MathTex(
            r"\text{leader: } s_L^L = s_L^H = 1",
            r"\;\Rightarrow\;",
            r"\text{allocation FOC} = \text{Prop. 1}",
            r"\;\Rightarrow\;",
            r"\phi_L^* = \phi^*",
            font_size=34,
        ).shift(UP * 1.9)
        leader[4].set_color(C_TRAIN)
        with self.voiceover(
            "Part two is the paper's slickest argument: the training"
            " fraction is invariant to competitive role. For the leader it"
            " is immediate from the convention: monopoly-phase shares equal"
            " one, the allocation condition is Proposition one's, so phi L"
            " equals phi star."
        ):
            self.play(Write(leader), run_time=1.8)

        fdef = MathTex(
            r"f(u)",
            r"=",
            r"\frac{u^{2\alpha}}{u^{\alpha} + \bar{u}^{\alpha}}",
            r"\qquad (\bar{u}\ \text{rival's measure, fixed})",
            font_size=40,
        ).next_to(leader, DOWN, buff=0.6)
        fdef[2].set_color(C_H)
        with self.voiceover(
            "The follower is the real content. Write the Tullock contest"
            " payoff over the regime-relevant capacity measure u, holding"
            " the rival's measure u bar fixed: u to the two alpha, over u to"
            " the alpha plus u bar to the alpha."
        ):
            self.play(Write(fdef), run_time=1.6)

        d1 = MathTex(
            r"f'(u)",
            r"=",
            r"\frac{2\alpha\, u^{2\alpha - 1}\,(u^{\alpha} + \bar{u}^{\alpha})"
            r" \;-\; u^{2\alpha}\cdot \alpha\, u^{\alpha - 1}}"
            r"{(u^{\alpha} + \bar{u}^{\alpha})^{2}}",
            font_size=38,
        ).next_to(fdef, DOWN, buff=0.6)
        with self.voiceover(
            "Differentiate with the quotient rule: derivative of the"
            " numerator times the denominator, minus the numerator times the"
            " derivative of the denominator, over the denominator squared."
        ):
            self.play(Write(d1), run_time=1.8)
        self.pause(0.3)

        d2 = MathTex(
            r"f'(u)",
            r"=",
            r"\alpha\, u^{\alpha - 1}\;",
            r"\frac{2u^{\alpha}(u^{\alpha} + \bar{u}^{\alpha}) - u^{2\alpha}}"
            r"{(u^{\alpha} + \bar{u}^{\alpha})^{2}}",
            font_size=38,
        ).move_to(d1)
        d2[2].set_color(C_OPTION)
        d2_box = highlight(d2[2])
        with self.voiceover(
            "Pull alpha u to the alpha minus one out of both terms of the"
            " numerator: what remains inside is two u to the alpha times the"
            " denominator, minus u to the two alpha."
        ):
            self.play(FadeOut(d1), run_time=0.4)
            self.play(Write(d2), run_time=1.6)
            self.play(Create(d2_box), run_time=0.6)
        self.pause(0.3)

        d3 = MathTex(
            r"f'(u)",
            r"=",
            r"\alpha\, u^{\alpha - 1}\;",
            r"\underbrace{\frac{u^{\alpha}}{u^{\alpha} + \bar{u}^{\alpha}}}_{s}",
            r"\;\underbrace{\frac{2(u^{\alpha} + \bar{u}^{\alpha})"
            r" - u^{\alpha}}{u^{\alpha} + \bar{u}^{\alpha}}}_{2 - s}",
            font_size=38,
        ).move_to(d2)
        d3[2].set_color(C_OPTION)
        d3[3].set_color(C_H)
        d3[4].set_color(C_H)
        with self.voiceover(
            "Now factor u to the alpha out of that bracket and split one"
            " denominator factor into each piece: the first ratio is the"
            " contest share s, and the second is two minus s."
        ):
            self.play(FadeOut(d2), FadeOut(d2_box), run_time=0.4)
            self.play(Write(d3), run_time=2.0)

        d4 = MathTex(
            r"f'(u)",
            r"=",
            r"\alpha\, u^{\alpha - 1}\, s\,(2 - s),",
            r"\qquad s = \frac{u^{\alpha}}{u^{\alpha} + \bar{u}^{\alpha}}",
            font_size=42,
        ).next_to(d3, DOWN, buff=0.55)
        d4[2].set_color(C_TEXT)
        box = highlight(d4[2])
        with self.voiceover(
            "So the marginal contest revenue is the standalone marginal"
            " revenue, alpha u to the alpha minus one, scaled by the common"
            " multiplier s times two minus s."
        ):
            self.play(Write(d4), run_time=1.4)
            self.play(Create(box), run_time=0.7)
        self.pause(0.4)
        self.clear_body()

        same_s = MathTex(
            r"\phi_F = \phi_L = \phi:\qquad",
            r"s^L = \frac{[(1-\phi)K_F]^{\alpha}}"
            r"{[(1-\phi)K_F]^{\alpha} + [(1-\phi)K_L]^{\alpha}}",
            r"=",
            r"\frac{K_F^{\alpha}}{K_F^{\alpha} + K_L^{\alpha}}",
            r"=",
            r"s^H",
            font_size=34,
        ).shift(UP * 1.6)
        same_s[3].set_color(C_H)
        with self.voiceover(
            "Here is the crucial observation. At a common training fraction,"
            " the regime-relevant capacity ratios coincide: in the L regime"
            " the one minus phi factors cancel, and in the H regime the phi"
            " factors cancel. Both shares reduce to the same pure capacity"
            " share s, for any capacity pair."
        ):
            self.play(Write(same_s), run_time=2.2)

        foc = MathTex(
            r"\frac{\partial A_{\mathrm{eff},F}}{\partial \phi_F}"
            r"\bigg|_{\phi_F = \phi_L = \phi}",
            r"=",
            r"\alpha K_F^{\alpha}\,",
            r"s\,(2 - s)\,",
            r"\bigl[-w_L (1-\phi)^{\alpha - 1} + w_H\, \phi^{\alpha - 1}\bigr]",
            font_size=36,
        ).next_to(same_s, DOWN, buff=0.6)
        foc[3].set_color(C_H)
        foc[4].set_color(C_TRAIN)
        with self.voiceover(
            "Now differentiate the follower's A effective in phi F at the"
            " common split. The chain rule brings in f prime of each"
            " regime's measure, times minus K F for inference and plus K F"
            " for training, and everything reorganizes into alpha K F to the"
            " alpha, times s two minus s, times the single-firm bracket."
        ):
            self.play(Write(foc), run_time=2.2)

        with self.voiceover(
            "Because s is the same in both regime terms, the multiplier s"
            " times two minus s is a common factor: it cancels from the"
            " first-order condition entirely."
        ):
            self.play(Indicate(foc[3], color=C_H), run_time=1.2)

        cond = MathTex(
            r"w_H\, \phi^{\alpha - 1} = w_L\,(1 - \phi)^{\alpha - 1}",
            r"\;\iff\;",
            r"\left(\frac{\phi}{1-\phi}\right)^{1-\alpha}"
            r" = \frac{\lambda}{r - \mu_H}",
            r"\;\Rightarrow\; \phi^*",
            font_size=36,
        ).next_to(foc, DOWN, buff=0.55)
        cond[2].set_color(C_TRAIN)
        cond[3].set_color(C_TRAIN)
        with self.voiceover(
            "What is left is literally Proposition one's condition: the odds"
            " ratio of training to the one minus alpha equals lambda over r"
            " minus mu H, whose unique zero is phi star."
        ):
            self.play(Write(cond), run_time=1.8)
        self.pause(0.4)
        self.clear_body()

        exact = VGroup(
            Text(
                "exact critical point for ANY (K_F, K_L) -- not just to first order",
                font_size=27,
                color=C_TEXT,
            ),
            Text(
                "global optimality: computational -- phi_F = phi_L = phi*"
                " to 4+ decimals",
                font_size=27,
                color=C_TEXT,
            ),
            Text(
                "across the full calibration sweep"
                " (sigma, mu_H, alpha, gamma, lambda, ell)",
                font_size=24,
                color=C_FAINT,
            ),
        ).arrange(DOWN, buff=0.3, aligned_edge=LEFT)
        exact.shift(UP * 1.0)
        with self.voiceover(
            "Note what the argument did not assume: nothing about the"
            " capacities. Phi star is an exact critical point of the"
            " follower's allocation problem for any capacity pair, not"
            " merely to first order."
        ):
            self.play(FadeIn(exact[0]), run_time=0.9)
        with self.voiceover(
            "What remains computational is global optimality: numerically,"
            " phi F equals phi L equals phi star to at least four decimal"
            " places across the full calibration sweep, with no"
            " parameterization showing an economically meaningful gap."
        ):
            self.play(FadeIn(exact[1]), FadeIn(exact[2]), run_time=1.0)

        punch = VGroup(
            Text(
                "allocation is pinned by beliefs and technology, not market position",
                font_size=29,
                color=C_TRAIN,
            ),
            MathTex(
                r"X_F^*/X_P \approx 44\text{--}46:"
                r"\ \text{a long monopoly phase, but it moves only the"
                r" timing margin}",
                font_size=30,
                color=C_TEXT,
            ),
        ).arrange(DOWN, buff=0.35)
        punch.next_to(exact, DOWN, buff=0.7)
        with self.voiceover(
            "The economic punchline: training allocation is pinned down by"
            " beliefs and technology, not by market position. The monopoly"
            " phase is long, X F over X P around forty-four to forty-six at"
            " baseline, but it operates entirely on the timing margin, never"
            " the allocation margin."
        ):
            self.play(FadeIn(punch[0]), run_time=1.0)
            self.play(Write(punch[1]), run_time=1.2)
        self.pause(0.4)
        self.clear_body()


class P5S12Numericals(PaperScene):
    def construct(self):
        self.set_header(
            "Parts (iii)-(v): numerical findings", kicker="5.10 COMPARATIVE STATICS"
        )

        r3 = MathTex(
            r"\text{(iii)}\quad",
            r"\lambda \uparrow",
            r"\;\Rightarrow\;",
            r"\phi^* \uparrow,\quad X_P \downarrow",
            font_size=38,
        ).shift(UP * 1.6)
        r3[1].set_color(C_DEMAND)
        r3[3].set_color(C_TRAIN)
        with self.voiceover(
            "Parts three to five of the proposition are numerical findings,"
            " verified across the full parameter space. Part three: higher"
            " lambda raises the training fraction for both firms, and lowers"
            " the preemption trigger."
        ):
            self.play(Write(r3), run_time=1.4)

        r4 = MathTex(
            r"\text{(iv)}\quad",
            r"\ell \uparrow",
            r"\;\Rightarrow\;",
            r"K_F \uparrow,\quad X_P,\, X_F^*,\, X_D \uparrow,"
            r"\quad X_F^*/X_D \downarrow",
            font_size=38,
        ).next_to(r3, DOWN, buff=0.6)
        r4[1].set_color(C_DEFAULT)
        r4[3].set_color(C_TEXT)
        with self.voiceover(
            "Part four: leverage. Par debt with a below-market coupon lowers"
            " the effective capital cost, so a more levered follower builds"
            " bigger."
        ):
            self.play(Write(r4), run_time=1.6)
        with self.voiceover(
            "Larger scale needs higher demand to justify, and the coupon"
            " obligation raises the default point: all three boundaries, X"
            " P, X F, and X D, rise with leverage, while the proportional"
            " margin of safety, X F over X D, falls."
        ):
            self.play(Indicate(r4[3], color=C_DEFAULT), run_time=1.4)

        r5 = MathTex(
            r"\text{(v)}\quad",
            r"\lambda \uparrow",
            r"\;\Rightarrow\;",
            r"\frac{X_P}{X_D} \downarrow:"
            r"\quad \approx 2.8\ (\lambda = 0.05)"
            r"\;\to\; \approx 2.6\ (\lambda = 0.20)\quad(\ell = 0.40)",
            font_size=36,
        ).next_to(r4, DOWN, buff=0.6)
        r5[1].set_color(C_DEMAND)
        r5[3].set_color(C_TEXT)
        with self.voiceover(
            "Part five ties timing to credit risk. Higher lambda lowers both"
            " the preemption trigger and the default boundary, but the"
            " trigger effect dominates: the distance to default at entry"
            " falls from about two point eight at lambda zero point zero"
            " five, to about two point six at zero point two, at forty"
            " percent leverage."
        ):
            self.play(Write(r5), run_time=2.0)

        spread = Text(
            "Leland spread is monotone in X_P/X_D  =>  entry spread weakly"
            " increasing in lambda",
            font_size=26,
            color=C_DEFAULT,
        ).next_to(r5, DOWN, buff=0.65)
        with self.voiceover(
            "So more optimistic leaders enter closer to their default"
            " boundary, and since the Leland spread is monotone in that"
            " distance, the credit spread at entry is weakly increasing in"
            " lambda."
        ):
            self.play(FadeIn(spread), run_time=1.2)
        self.pause(0.4)
        self.clear_body()


class P5S13CompetitionEffect(PaperScene):
    def construct(self):
        self.set_header("The competition effect", kicker="5.11 FIG. COMPETITION-EFFECT")

        from ai_lab_investment.models.duopoly import DuopolyModel
        from ai_lab_investment.models.parameters import ModelParameters

        base = ModelParameters()
        sigmas = np.linspace(0.20, 0.30, 11)
        mono = np.zeros_like(sigmas)
        lead = np.zeros_like(sigmas)
        for i, s in enumerate(sigmas):
            duo = DuopolyModel(base.with_param(sigma=s), leverage=0.0)
            eq = duo.solve_preemption_equilibrium("H")
            mono[i] = eq["X_leader_monopolist"]
            lead[i] = eq["X_leader"]
        ratio = lead / mono

        with self.voiceover(
            "Finally, the figure that quantifies the preemption effect:"
            " the monopolist's trigger against the duopoly leader's"
            " preemption trigger, as a function of volatility, recomputed"
            " here from the model code."
        ):
            self.pause(0.2)

        ax1 = clean_axes(
            x_range=[0.20, 0.30],
            y_range=[0, float(mono.max()) * 1.12],
            width=5.6,
            height=3.9,
        ).shift(LEFT * 3.4 + DOWN * 0.9)
        ax2 = clean_axes(
            x_range=[0.20, 0.30], y_range=[0.45, 0.70], width=5.6, height=3.9
        ).shift(RIGHT * 3.4 + DOWN * 0.9)
        x1_lab = MathTex(r"\sigma", font_size=28, color=C_FAINT).next_to(
            ax1.x_axis, RIGHT, buff=0.15
        )
        x2_lab = MathTex(r"\sigma", font_size=28, color=C_FAINT).next_to(
            ax2.x_axis, RIGHT, buff=0.15
        )
        t1 = Text("triggers", font_size=22, color=C_FAINT).next_to(ax1, UP, buff=0.15)
        t2 = Text("preemption discount", font_size=22, color=C_FAINT).next_to(
            ax2, UP, buff=0.15
        )

        mono_line = ax1.plot_line_graph(
            sigmas, mono, line_color=C_TEXT, add_vertex_dots=False
        )
        lead_line = ax1.plot_line_graph(
            sigmas, lead, line_color=C_OPTION, add_vertex_dots=False
        )
        mono_lab = MathTex(r"X_L^{\mathrm{mono}}", font_size=28, color=C_TEXT).move_to(
            ax1.coords_to_point(0.282, mono.max() * 0.88)
        )
        lead_lab = MathTex(r"X_P", font_size=28, color=C_OPTION).move_to(
            ax1.coords_to_point(0.292, lead.max() * 0.55)
        )
        with self.voiceover(
            "On the left, both triggers rise steeply with sigma: more"
            " uncertainty raises the option value of waiting for everyone,"
            " monopolist and racer alike."
        ):
            self.play(Create(ax1), FadeIn(x1_lab), FadeIn(t1), run_time=0.9)
            self.play(Create(mono_line), FadeIn(mono_lab), run_time=1.2)
            self.play(Create(lead_line), FadeIn(lead_lab), run_time=1.2)

        ratio_line = ax2.plot_line_graph(
            sigmas, ratio, line_color=C_H, add_vertex_dots=False
        )
        ratio_lab = MathTex(
            r"X_P / X_L^{\mathrm{mono}}", font_size=28, color=C_H
        ).move_to(ax2.coords_to_point(0.265, 0.65))
        with self.voiceover(
            "On the right, their ratio falls: the preemption discount drops"
            " from about zero point six four at sigma equal to zero point"
            " two, to zero point five four at zero point three. Competition"
            " eats a growing share of the option value of waiting."
        ):
            self.play(Create(ax2), FadeIn(x2_lab), FadeIn(t2), run_time=0.9)
            self.play(Create(ratio_line), FadeIn(ratio_lab), run_time=1.6)

        i_base = int(np.argmin(np.abs(sigmas - 0.25)))
        base_dot = Dot(ax2.coords_to_point(0.25, float(ratio[i_base])), color=C_DEMAND)
        base_lab = MathTex(r"\approx 0.57", font_size=28, color=C_DEMAND).next_to(
            base_dot, DOWN, buff=0.15
        )
        with self.voiceover(
            "At the baseline sigma of zero point two five, the discount is"
            " about zero point five seven: preemption cuts the leader's"
            " trigger by roughly forty-three percent relative to the"
            " monopolist."
        ):
            self.play(FadeIn(base_dot, scale=2), FadeIn(base_lab), run_time=1.0)

        a2_note = Text(
            "grid starts at sigma = 0.20: (A2) needs beta_H < 1/(1-alpha),"
            " binding at sigma ~ 0.19",
            font_size=23,
            color=C_FAINT,
        ).to_edge(DOWN, buff=0.25)
        with self.voiceover(
            "The grid starts at sigma equal to zero point two because"
            " assumption A two bounds volatility from below at about zero"
            " point one nine: beta H must stay below one over one minus"
            " alpha for the capacity problem to have an interior optimum."
        ):
            self.play(FadeIn(a2_note), run_time=1.0)

        with self.voiceover(
            "And remember the division of labor in this solution:"
            " competition moves timing, not scale or allocation. The"
            " leader's capacity is the monopoly-phase optimum by"
            " construction, and phi is role-invariant by Proposition three"
            " part two."
        ):
            self.play(Indicate(ratio_lab, color=C_H), run_time=1.2)
        self.pause(0.4)
        self.clear_body()


class P5S14Close(PaperScene):
    def construct(self):
        summary = VGroup(
            Text("Proposition 3, fully dissected:", font_size=32, weight="BOLD"),
            Text(
                "existence: analytical (IVT)   |   uniqueness: analytical"
                " at ell = 0, computational beyond",
                font_size=25,
                color=C_TEXT,
            ),
            Text(
                "role invariance: exact s(2-s) cancellation   |  "
                " (iii)-(v): numerical findings",
                font_size=25,
                color=C_TEXT,
            ),
        ).arrange(DOWN, buff=0.4)
        summary.shift(UP * 0.8)
        with self.voiceover(
            "That completes Proposition three: analytical existence,"
            " analytical uniqueness at zero leverage, an exact allocation"
            " fixed point through the s times two minus s cancellation, and"
            " computational verification of everything else."
        ):
            self.play(FadeIn(summary), run_time=1.6)

        nxt = Text(
            "Part 6: calibration, credit risk, Dario's dilemma, and robustness",
            font_size=28,
            color=C_OPTION,
        ).next_to(summary, DOWN, buff=0.9)
        with self.voiceover(
            "Next and last, part six: calibration to the real AI labs,"
            " credit risk, Dario's dilemma, and the robustness checks."
            " Thanks for watching."
        ):
            self.play(Write(nxt), run_time=1.4)
        self.pause(0.8)
        self.play(FadeOut(summary), FadeOut(nxt), run_time=0.8)
