"""Derivation walkthrough, Part 3: the pre-AGI option (~15-20 min).

Covers the L-regime HJB equation with regime switching, the
non-homogeneous Euler ODE and its general solution, the exact A_1 = 0
argument (Proof of Proposition 1, Step 5b), the interior optimal
training fraction (Step 5 lemma), comparative statics (Step 6), and
Remark 1 on the role of lambda.

Render: uv run python video/render.py walkthrough_part3
Draft a single scene:
    cd video && uv run manim render -ql walkthrough_part3.py P3S01Title
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
    MathTex,
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
    C_L,
    C_OPTION,
    C_TEXT,
    C_TRAIN,
    clean_axes,
    eq,
    highlight,
)

SCENES = [
    "P3S01Title",
    "P3S02Recap",
    "P3S03HJB",
    "P3S04EulerODE",
    "P3S05Homogeneous",
    "P3S06Particular",
    "P3S07SimplifiedForm",
    "P3S08RuleOutPositive",
    "P3S09RuleOutNegative",
    "P3S10TriggerConsistency",
    "P3S11PhiLemma",
    "P3S12ComparativeStatics",
    "P3S13LambdaChannels",
    "P3S14Close",
]


def _q_parabola_axes(width: float = 8.6, height: float = 4.0):
    """Axes sized for plotting the characteristic quadratics Q(beta)."""
    return clean_axes(
        x_range=[-3.6, 4.4], y_range=[-0.32, 0.34], width=width, height=height
    )


def _Q_L(beta: float) -> float:
    p = BASELINE
    return (
        0.5 * p["sigma"] ** 2 * beta * (beta - 1)
        + p["mu_L"] * beta
        - (p["r"] + p["lambda"])
    )


def _Q_H(beta: float) -> float:
    p = BASELINE
    return 0.5 * p["sigma"] ** 2 * beta * (beta - 1) + p["mu_H"] * beta - p["r"]


class P3S01Title(PaperScene):
    def construct(self):
        kicker = Text(
            "DERIVATION WALKTHROUGH - PART 3", font_size=24, color=C_FAINT
        ).shift(UP * 1.6)
        title = Text("The Pre-AGI Option", font_size=52, weight="BOLD")
        sub = Text(
            "The L-regime ODE and the optimal training fraction",
            font_size=28,
            color=C_TEXT,
        ).next_to(title, DOWN, buff=0.45)

        with self.voiceover(
            "Welcome back to the derivation walkthrough. This is part three:"
            " the pre-AGI option."
        ):
            self.play(FadeIn(kicker), run_time=0.8)
            self.play(Write(title), run_time=1.6)

        with self.voiceover(
            "We derive the low-regime option value from its differential"
            " equation, prove that the homogeneous coefficient is exactly"
            " zero, and characterize the interior optimal training fraction."
        ):
            self.play(FadeIn(sub), run_time=1.2)
        self.pause(0.6)
        self.play(FadeOut(kicker), FadeOut(title), FadeOut(sub), run_time=0.7)


class P3S02Recap(PaperScene):
    def construct(self):
        self.set_header("Where we left off", kicker="RECAP")

        opt_h = eq(
            r"F_H(X) = B_H X^{\beta_H},\qquad B_H \approx 37.6,"
            r"\quad \beta_H \approx 1.55",
            font_size=38,
        ).shift(UP * 1.6)
        opt_h[0][0:5].set_color(C_H)
        with self.voiceover(
            "In part two we solved the post-AGI problem. The H-regime option"
            " value is B H times X to the beta H, with beta H about one point"
            " five five at the baseline."
        ):
            self.play(Write(opt_h), run_time=1.6)

        steps = eq(
            r"X^*(K,\phi) = \frac{\beta_H}{\beta_H - 1}\cdot"
            r"\frac{\delta K/r + cK^{\gamma}}{A_{\text{eff}}(\phi, K)},"
            r"\qquad F(X_0) \propto \frac{A_{\text{eff}}^{\beta_H}}"
            r"{b^{\beta_H - 1}}",
            font_size=36,
        ).next_to(opt_h, DOWN, buff=0.7)
        with self.voiceover(
            "Steps one through four of the proof of proposition one gave the"
            " trigger formula, the net present value at the trigger, and the"
            " reduced objective: A effective to the beta H over total cost to"
            " the beta H minus one, which delivered the closed-form capacity"
            " K star."
        ):
            self.play(Write(steps), run_time=2.0)

        agenda = VGroup(
            MathTex(
                r"\text{1.  The $L$-regime ODE that justifies the option value}",
                font_size=30,
            ),
            MathTex(
                r"\text{2.  Why } A_1 = 0 \text{ exactly, not approximately}",
                font_size=30,
            ),
            MathTex(
                r"\text{3.  The interior optimal } \phi"
                r"\text{ and its comparative statics}",
                font_size=30,
            ),
        ).arrange(DOWN, buff=0.35, aligned_edge=LEFT)
        agenda.next_to(steps, DOWN, buff=0.8)
        with self.voiceover(
            "All of that took the option-value exponent beta H as given, even"
            " though the firm starts in the low regime. Today we close that"
            " gap with three pieces of unfinished business."
        ):
            self.play(FadeIn(agenda[0], shift=RIGHT * 0.3), run_time=0.9)
        with self.voiceover(
            "First, the low-regime differential equation. Second, the"
            " subtlest argument in the paper: why the homogeneous coefficient"
            " A one is exactly zero. And third, the full proof that the"
            " optimal training fraction is interior and unique."
        ):
            self.play(FadeIn(agenda[1], shift=RIGHT * 0.3), run_time=0.9)
            self.play(FadeIn(agenda[2], shift=RIGHT * 0.3), run_time=0.9)
        self.pause(0.5)
        self.clear_body()


class P3S03HJB(PaperScene):
    def construct(self):
        self.set_header("The L-regime HJB equation", kicker="OPTION VALUE IN L")

        setup = eq(
            r"\text{In regime } L:\quad \text{option value } F_L(X),\qquad"
            r" dX = \mu_L X\,dt + \sigma X\,dW",
            font_size=36,
        ).shift(UP * 2.2)
        setup[0][22:27].set_color(C_L)
        with self.voiceover(
            "The firm sits in the low regime, holding the unexercised"
            " investment option, worth F L of X. Demand follows a geometric"
            " Brownian motion with drift mu L."
        ):
            self.play(Write(setup), run_time=1.6)

        bellman = eq(
            r"r\,F_L(X)\,dt = \mathbb{E}\bigl[dF_L\bigr]",
            font_size=40,
        ).next_to(setup, DOWN, buff=0.6)
        with self.voiceover(
            "Over a short interval d t, the option must earn the required"
            " return: r times F L times d t equals the expected change in the"
            " option's value. We now compute that expected change from first"
            " principles."
        ):
            self.play(Write(bellman), run_time=1.4)

        branch1 = VGroup(
            MathTex(
                r"\text{with prob. } \lambda\,dt\text{:  regime switches to } H",
                font_size=26,
            ),
            eq(r"F_L(X) \;\longrightarrow\; F_H(X)", font_size=34, color=C_H),
        ).arrange(DOWN, buff=0.2, aligned_edge=LEFT)
        branch2 = VGroup(
            MathTex(
                r"\text{with prob. } 1 - \lambda\,dt\text{:  stay in } L"
                r"\text{, } X \text{ diffuses}",
                font_size=26,
            ),
            eq(
                r"\mathbb{E}[dF_L \mid \text{no switch}] = \Bigl(\mu_L X F_L'"
                r" + \tfrac{1}{2}\sigma^2 X^2 F_L''\Bigr)dt",
                font_size=34,
                color=C_L,
            ),
        ).arrange(DOWN, buff=0.2, aligned_edge=LEFT)
        branches = VGroup(branch1, branch2).arrange(DOWN, buff=0.45, aligned_edge=LEFT)
        branches.next_to(bellman, DOWN, buff=0.55)

        with self.voiceover(
            "Two things can happen. With probability lambda d t, the Poisson"
            " switch arrives: the regime jumps to H, and the firm's option is"
            " suddenly worth F H of X instead of F L of X. Demand itself does"
            " not jump; only the regime does."
        ):
            self.play(FadeIn(branch1), run_time=1.4)
        with self.voiceover(
            "With the remaining probability, the regime stays low and only"
            " demand moves. Ito's lemma gives the usual drift term: mu L X"
            " times the first derivative, plus one half sigma squared X"
            " squared times the second derivative, all times d t."
        ):
            self.play(FadeIn(branch2), run_time=1.4)

        self.clear_body(setup, bellman)

        total = MathTex(
            r"\mathbb{E}[dF_L] = \Bigl(\mu_L X F_L' + \tfrac{1}{2}\sigma^2"
            r" X^2 F_L''\Bigr)dt",
            r"\;+\;\lambda\,dt\,\bigl[F_H(X) - F_L(X)\bigr]",
            r"\;+\;o(dt)",
            font_size=34,
        ).next_to(bellman, DOWN, buff=0.6)
        total[1].set_color(C_DEMAND)
        with self.voiceover(
            "Adding the two branches, the expected change is the Ito drift"
            " plus a compensated jump term: lambda d t times the gain F H"
            " minus F L. Cross terms like the switch probability times the"
            " diffusion increment are of smaller order than d t and are"
            " absorbed in the little-o term."
        ):
            self.play(Write(total), run_time=2.0)

        hjb = MathTex(
            r"\tfrac{1}{2}\sigma^2 X^2 F_L''",
            r"+\mu_L X F_L'",
            r"+\lambda\bigl[F_H(X) - F_L(X)\bigr]",
            r"-r F_L",
            r"=0",
            font_size=38,
        ).next_to(total, DOWN, buff=0.7)
        hjb[2].set_color(C_DEMAND)
        with self.voiceover(
            "Substituting into the required-return condition, dividing by d"
            " t, and letting d t go to zero gives the Hamilton Jacobi Bellman"
            " equation for the low-regime option."
        ):
            self.play(Write(hjb), run_time=1.8)

        box = highlight(hjb[2], color=C_DEMAND)
        with self.voiceover(
            "The lambda term is the regime-switching coupling: at rate"
            " lambda, the firm swaps its low-regime option for the H-regime"
            " one. This is the only place the two regimes talk to each"
            " other."
        ):
            self.play(Create(box), run_time=0.9)

        note = eq(
            r"F_H(X) = B_H X^{\beta_H}\ \text{(H-regime \emph{option}"
            r" value, } X < X_H^*\text{)},\quad\text{not } V_H",
            font_size=32,
            color=C_H,
        ).next_to(hjb, DOWN, buff=0.6)
        with self.voiceover(
            "One crucial reading note: F H here is the H-regime option value"
            " B H X to the beta H from part two, the value of holding the"
            " unexercised option in regime H. It is not the installed value V"
            " H. The firm switches regimes before investing, so it inherits"
            " the option, not the project."
        ):
            self.play(Write(note), run_time=1.8)
        self.pause(0.5)
        self.clear_body()


class P3S04EulerODE(PaperScene):
    def construct(self):
        self.set_header("A non-homogeneous Euler ODE", kicker="OPTION VALUE IN L")

        hjb = MathTex(
            r"\tfrac{1}{2}\sigma^2 X^2 F_L'' + \mu_L X F_L'",
            r"+\lambda F_H(X)",
            r"-\lambda F_L",
            r"-r F_L",
            r"=0",
            font_size=38,
        ).shift(UP * 1.8)
        with self.voiceover(
            "Take the HJB equation and expand the coupling bracket into its"
            " two pieces: plus lambda F H, and minus lambda F L."
        ):
            self.play(Write(hjb), run_time=1.6)

        with self.voiceover(
            "Now substitute the known H-regime option, B H X to the beta H,"
            " for F H, and group the two F L terms into a single discount"
            " term."
        ):
            self.play(
                Indicate(hjb[1], color=C_H),
                run_time=1.0,
            )
            self.play(
                Indicate(hjb[2], color=C_OPTION),
                Indicate(hjb[3], color=C_OPTION),
                run_time=1.0,
            )

        ode = MathTex(
            r"\tfrac{1}{2}\sigma^2 X^2 F_L'' + \mu_L X F_L'",
            r"-(r+\lambda)F_L",
            r"+\lambda B_H X^{\beta_H}",
            r"=0",
            font_size=40,
        ).next_to(hjb, DOWN, buff=0.9)
        ode[1].set_color(C_OPTION)
        ode[2].set_color(C_H)
        with self.voiceover(
            "The result is a linear second-order Euler equation with a"
            " power-function forcing term."
        ):
            self.play(FadeIn(ode, shift=DOWN * 0.3), run_time=1.2)

        b1 = highlight(ode[1], color=C_OPTION)
        n1 = (
            MathTex(
                r"\text{effective discount } r + \lambda = 0.12 + 0.10 = 0.22",
                font_size=26,
                color=C_OPTION,
            )
            .next_to(ode, DOWN, buff=0.65)
            .shift(LEFT * 2.2)
        )
        with self.voiceover(
            "Two features matter. First, the discount rate on the low-regime"
            " option is r plus lambda, twenty-two percent at the baseline:"
            " the regime switch acts like an extra depreciation of the"
            " low-regime state, because at rate lambda this value is replaced"
            " by the H-regime one."
        ):
            self.play(Create(b1), FadeIn(n1), run_time=1.2)

        b2 = highlight(ode[2], color=C_H)
        n2 = MathTex(
            r"\text{forcing term: arrival of the $H$-regime option}",
            font_size=26,
            color=C_H,
        ).next_to(n1, DOWN, buff=0.35, aligned_edge=LEFT)
        with self.voiceover(
            "Second, the equation is non-homogeneous: the forcing term"
            " lambda B H X to the beta H is the expected inflow of H-regime"
            " option value. The general solution is a homogeneous part plus"
            " one particular solution, and we build both next."
        ):
            self.play(Create(b2), FadeIn(n2), run_time=1.2)
        self.pause(0.5)
        self.clear_body()


class P3S05Homogeneous(PaperScene):
    def construct(self):
        self.set_header("Homogeneous solution", kicker="GENERAL SOLUTION, 1 OF 2")

        guess = eq(
            r"\text{try } F(X) = X^{\beta}:\qquad F' = \beta X^{\beta-1},"
            r"\qquad F'' = \beta(\beta-1)X^{\beta-2}",
            font_size=36,
        ).shift(UP * 2.2)
        with self.voiceover(
            "Drop the forcing term and solve the homogeneous equation. Euler"
            " equations admit power solutions, so try F equals X to the"
            " beta, with these derivatives."
        ):
            self.play(Write(guess), run_time=1.6)

        sub = eq(
            r"\Bigl[\tfrac{1}{2}\sigma^2\beta(\beta-1) + \mu_L\beta"
            r" - (r+\lambda)\Bigr]X^{\beta} = 0",
            font_size=38,
        ).next_to(guess, DOWN, buff=0.6)
        with self.voiceover(
            "Each term of the equation contributes the same power X to the"
            " beta: the second-derivative term gives one half sigma squared"
            " beta times beta minus one, the drift term gives mu L beta, and"
            " the discount gives minus r plus lambda."
        ):
            self.play(Write(sub), run_time=1.8)

        qdef = eq(
            r"Q_L(\beta) \equiv \tfrac{1}{2}\sigma^2\beta(\beta-1)"
            r" + \mu_L\beta - (r+\lambda) = 0",
            font_size=38,
            color=C_L,
        ).next_to(sub, DOWN, buff=0.55)
        with self.voiceover(
            "The bracket must vanish: this is the characteristic quadratic Q"
            " L of beta, the low-regime counterpart of the quadratic that"
            " defined beta H in part two, but with drift mu L and the"
            " effective discount r plus lambda."
        ):
            self.play(Write(qdef), run_time=1.6)

        self.clear_body(qdef)
        self.play(qdef.animate.scale(0.85).to_edge(UP, buff=1.45).shift(RIGHT * 1.5))

        ax = _q_parabola_axes().shift(DOWN * 1.1)
        curve = ax.plot(_Q_L, x_range=[-3.45, 4.3], color=C_L, stroke_width=3)
        x_lab = MathTex(r"\beta", font_size=30, color=C_FAINT).next_to(
            ax.coords_to_point(4.4, 0), RIGHT, buff=0.1
        )
        with self.voiceover(
            "Plot Q L against beta at the baseline parameters. It is an"
            " upward parabola, and at beta equal to zero it takes the value"
            " minus r minus lambda, which is negative, so there is exactly"
            " one negative root and one positive root."
        ):
            self.play(Create(ax), FadeIn(x_lab), run_time=1.0)
            self.play(Create(curve), run_time=1.8)

        bl_plus = BASELINE["beta_L_plus"]
        bl_minus = -2.33
        dot_p = Dot(ax.coords_to_point(bl_plus, 0), color=C_OPTION)
        dot_m = Dot(ax.coords_to_point(bl_minus, 0), color=C_FAINT)
        lab_p = MathTex(
            r"\beta_L^+ \approx 3.01", font_size=32, color=C_OPTION
        ).next_to(dot_p, UP + RIGHT, buff=0.1)
        lab_m = MathTex(
            r"\beta_L^- \approx -2.33", font_size=32, color=C_FAINT
        ).next_to(dot_m, UP + LEFT, buff=0.1)
        with self.voiceover(
            "At the baseline, the positive root is beta L plus, about three"
            " point zero one, and the negative root is about minus two point"
            " three three."
        ):
            self.play(FadeIn(dot_p, scale=2), Write(lab_p), run_time=1.0)
            self.play(FadeIn(dot_m, scale=2), Write(lab_m), run_time=1.0)

        bh = BASELINE["beta_H"]
        dot_h = Dot(ax.coords_to_point(bh, 0), color=C_H)
        drop = DashedLine(
            ax.coords_to_point(bh, 0),
            ax.coords_to_point(bh, _Q_L(bh)),
            color=C_H,
        )
        lab_h = MathTex(r"\beta_H \approx 1.55", font_size=32, color=C_H).next_to(
            dot_h, UP, buff=0.15
        )
        lab_q = MathTex(r"Q_L(\beta_H) < 0", font_size=32, color=C_H).next_to(
            ax.coords_to_point(bh, _Q_L(bh)), DOWN, buff=0.15
        )
        with self.voiceover(
            "Mark one more point for later: beta H, about one point five"
            " five, lies strictly between the two roots, where the parabola"
            " dips below zero. So Q L evaluated at beta H is negative. Keep"
            " that in mind."
        ):
            self.play(FadeIn(dot_h, scale=2), Write(lab_h), run_time=1.0)
            self.play(Create(drop), Write(lab_q), run_time=1.2)

        hom = eq(
            r"F_{\text{hom}}(X) = A_1 X^{\beta_L^+} + A_2 X^{\beta_L^-}",
            font_size=36,
        ).to_edge(DOWN, buff=0.4)
        with self.voiceover(
            "The homogeneous solution is therefore a combination of the two"
            " powers: A one times X to the beta L plus, and A two times X to"
            " the beta L minus."
        ):
            self.play(Write(hom), run_time=1.4)
        self.pause(0.5)
        self.clear_body()


class P3S06Particular(PaperScene):
    def construct(self):
        self.set_header("Particular solution", kicker="GENERAL SOLUTION, 2 OF 2")

        ode = eq(
            r"\tfrac{1}{2}\sigma^2 X^2 F'' + \mu_L X F' - (r+\lambda)F"
            r" + \lambda B_H X^{\beta_H} = 0",
            font_size=36,
        ).shift(UP * 2.45)
        guess = eq(
            r"\text{guess: } F_p(X) = C\,X^{\beta_H}\quad\text{(same power"
            r" as the forcing)}",
            font_size=36,
            color=C_H,
        ).next_to(ode, DOWN, buff=0.45)
        with self.voiceover(
            "Now the particular solution. The forcing term is a pure power"
            " of X, and beta H is not a root of Q L, so guess a particular"
            " solution proportional to the same power: C times X to the beta"
            " H."
        ):
            self.play(Write(ode), run_time=1.4)
            self.play(Write(guess), run_time=1.2)

        plug = MathTex(
            r"\Bigl[\tfrac{1}{2}\sigma^2\beta_H(\beta_H-1) + \mu_L\beta_H"
            r" - (r+\lambda)\Bigr]C\,X^{\beta_H}",
            r"+\lambda B_H X^{\beta_H}",
            r"= 0",
            font_size=34,
        ).next_to(guess, DOWN, buff=0.5)
        plug[1].set_color(C_H)
        with self.voiceover(
            "Substituting the guess, every term again carries X to the beta"
            " H: the diffusion term contributes one half sigma squared beta"
            " H beta H minus one times C, the drift contributes mu L beta H"
            " times C, and the discount minus r plus lambda times C."
        ):
            self.play(Write(plug), run_time=2.0)

        collect = eq(
            r"\bigl[\,Q_L(\beta_H)\,C + \lambda B_H\,\bigr]X^{\beta_H} = 0",
            font_size=36,
        ).next_to(plug, DOWN, buff=0.45)
        with self.voiceover(
            "The bracket is exactly the characteristic quadratic evaluated"
            " at beta H. For the equation to hold for every X, the bracket"
            " must vanish."
        ):
            self.play(Write(collect), run_time=1.4)

        c_eq = eq(
            r"C = \frac{-\lambda B_H}{Q_L(\beta_H)}",
            font_size=42,
            color=C_OPTION,
        ).next_to(collect, DOWN, buff=0.5)
        with self.voiceover(
            "Solving for C gives the particular-solution coefficient: minus"
            " lambda B H over Q L of beta H. This is the paper's equation"
            " for C, and it is fully pinned down by the O D E. No boundary"
            " condition is involved."
        ):
            self.play(Write(c_eq), run_time=1.4)

        self.clear_body(c_eq)
        self.play(c_eq.animate.scale(0.85).to_edge(UP, buff=1.4).shift(LEFT * 3.6))

        sign1 = eq(
            r"Q_H(\beta_H) \equiv \tfrac{1}{2}\sigma^2\beta_H(\beta_H-1)"
            r" + \mu_H\beta_H - r = 0\quad\text{(definition of }\beta_H)",
            font_size=33,
        ).shift(UP * 0.95)
        with self.voiceover(
            "Why is C positive? Recall from part two that beta H is by"
            " definition the positive root of the H-regime quadratic Q H, so"
            " Q H at beta H is zero."
        ):
            self.play(Write(sign1), run_time=1.6)

        sign2 = MathTex(
            r"Q_L(\beta_H) = Q_H(\beta_H) + (\mu_L - \mu_H)\beta_H - \lambda",
            r"= -(\mu_H - \mu_L)\beta_H - \lambda",
            font_size=34,
        ).next_to(sign1, DOWN, buff=0.45)
        with self.voiceover(
            "Subtract the two quadratics: they differ only in the drift and"
            " discount terms. So Q L at beta H equals mu L minus mu H times"
            " beta H, minus lambda. Both pieces are negative."
        ):
            self.play(Write(sign2), run_time=1.8)

        sign3 = eq(
            r"Q_L(\beta_H) = -(0.06 - 0.01)\times 1.55 - 0.10"
            r" \approx -0.178 < 0",
            font_size=34,
            color=C_L,
        ).next_to(sign2, DOWN, buff=0.45)
        with self.voiceover(
            "Numerically, minus five percent of drift gap times one point"
            " five five, minus the arrival rate of zero point one zero,"
            " gives about minus zero point one seven eight. This is the"
            " algebraic version of the picture from the last scene: beta H"
            " lies between the two roots of Q L, where the parabola is"
            " negative."
        ):
            self.play(Write(sign3), run_time=1.6)

        c_num = eq(
            r"C = \frac{-\,0.10 \times 37.6}{-\,0.178} \approx 21.1 > 0",
            font_size=36,
            color=C_OPTION,
        ).next_to(sign3, DOWN, buff=0.5)
        with self.voiceover(
            "A negative denominator against the negative numerator makes C"
            " positive: about twenty-one point one at the baseline. The"
            " switching prospect adds value, as it should."
        ):
            self.play(Write(c_num), run_time=1.4)

        self.clear_body()
        gen = MathTex(
            r"F_L(X) = A_1 X^{\beta_L^+} + A_2 X^{\beta_L^-}",
            r"+\,C X^{\beta_H}",
            font_size=38,
        ).shift(UP * 1.2)
        gen[1].set_color(C_OPTION)
        with self.voiceover(
            "Putting the pieces together, the general solution is the two"
            " homogeneous powers plus the particular term C X to the beta"
            " H."
        ):
            self.play(Write(gen), run_time=1.4)

        bc = eq(
            r"X \to 0^+:\quad X^{\beta_L^-} = X^{-2.33} \to \infty"
            r"\quad\Rightarrow\quad A_2 = 0",
            font_size=36,
        ).next_to(gen, DOWN, buff=0.55)
        with self.voiceover(
            "The boundary condition at zero kills one of them. If demand"
            " hits zero it stays there, and an option on worthless demand is"
            " worthless: F L of zero must be zero. The negative power blows"
            " up as X goes to zero, so A two must be zero."
        ):
            self.play(Write(bc), run_time=1.6)

        final = eq(
            r"F_L(X) = A_1 X^{\beta_L^+} + C\,X^{\beta_H},\qquad X < X^*",
            font_size=40,
        ).next_to(bc, DOWN, buff=0.6)
        box = highlight(final)
        with self.voiceover(
            "We are left with the paper's general form: A one times X to the"
            " beta L plus, plus C times X to the beta H, valid below the"
            " investment trigger. C is known. The entire next stretch of the"
            " video is about the one remaining unknown, A one."
        ):
            self.play(Write(final), run_time=1.4)
            self.play(Create(box), run_time=0.8)
        self.pause(0.5)
        self.clear_body()


class P3S07SimplifiedForm(PaperScene):
    def construct(self):
        self.set_header("When does the simple form apply?", kicker="THE A1 QUESTION")

        gen = MathTex(
            r"F_L(X) =",
            r"A_1 X^{\beta_L^+}",
            r"+",
            r"C\,X^{\beta_H}",
            font_size=40,
        ).shift(UP * 2.0)
        gen[1].set_color(C_COST)
        gen[3].set_color(C_OPTION)
        with self.voiceover(
            "Here is the situation. The coefficient C is already determined"
            " by the differential equation's forcing structure. A one is"
            " not."
        ):
            self.play(Write(gen), run_time=1.4)

        roles = VGroup(
            MathTex(
                r"C X^{\beta_H}\text{: value of the expected regime switch}",
                font_size=28,
                color=C_OPTION,
            ),
            MathTex(
                r"A_1 X^{\beta_L^+}\text{: the autonomous $L$-regime"
                r" investment option}",
                font_size=28,
                color=C_COST,
            ),
        ).arrange(DOWN, buff=0.3, aligned_edge=LEFT)
        roles.next_to(gen, DOWN, buff=0.55)
        with self.voiceover(
            "The two terms have sharply different economics. The particular"
            " term is the value of the coming regime switch. The homogeneous"
            " term solves the equation with no switching at all: it is the"
            " value of an option to invest on the strength of low-regime"
            " inference revenue alone."
        ):
            self.play(FadeIn(roles[0]), run_time=1.0)
            self.play(FadeIn(roles[1]), run_time=1.0)

        a3 = eq(
            r"\text{(A3):}\qquad \Phi_L \equiv \frac{1 - 1/\beta_L^+}{\alpha}"
            r" \;\geq\; 1",
            font_size=40,
        ).next_to(roles, DOWN, buff=0.6)
        with self.voiceover(
            "Whether that standalone option ever gets exercised is governed"
            " by the option premium ratio Phi L: one minus one over beta L"
            " plus, divided by alpha. Assumption A three states that Phi L"
            " is at least one: the markup-adjusted marginal value of"
            " capacity, alpha, is too small for low-regime revenue alone to"
            " justify irreversible investment."
        ):
            self.play(Write(a3), run_time=1.6)

        a3num = eq(
            r"\text{baseline: } \Phi_L = \frac{1 - 1/3.01}{0.40}"
            r" \approx 1.67 \;\gg\; 1",
            font_size=36,
            color=C_L,
        ).next_to(a3, DOWN, buff=0.5)
        with self.voiceover(
            "At the baseline calibration, with beta L plus around three"
            " point zero one and alpha at zero point four, Phi L is about"
            " one point six seven, so the condition holds with a wide"
            " margin."
        ):
            self.play(Write(a3num), run_time=1.4)

        claim = MathTex(
            r"\text{Claim: under (A3), } A_1 = 0"
            r"\text{ exactly --- proof in two steps}",
            font_size=30,
            color=C_TEXT,
        ).next_to(a3num, DOWN, buff=0.55)
        with self.voiceover(
            "The claim is that under A three, A one equals zero exactly, not"
            " as an approximation: an option that is never exercised has"
            " zero value. We now prove it by ruling out a positive A one,"
            " then a negative one."
        ):
            self.play(FadeIn(claim), run_time=1.2)
        self.pause(0.5)
        self.clear_body()


class P3S08RuleOutPositive(PaperScene):
    def construct(self):
        self.set_header("Step 5b: ruling out A1 > 0", kicker="PROP 1, PROOF")

        pure = eq(
            r"\text{no-switching $L$-world: }\;"
            r"X_L^{\text{pure}} = \frac{\beta_L^+}{\beta_L^+ - 1}\cdot"
            r"\frac{\delta K/r + I(K)}{A_L K^{\alpha}},"
            r"\qquad A_L = \frac{1}{r - \mu_L}",
            font_size=33,
        ).shift(UP * 2.05)
        with self.voiceover(
            "First, a hypothetical. Shut off regime switching entirely and"
            " let the firm invest on low-regime revenue alone. The candidate"
            " trigger would have the familiar markup form, with beta L plus"
            " in the premium and the pure low-regime perpetuity coefficient,"
            " one over r minus mu L, in the denominator."
        ):
            self.play(Write(pure), run_time=2.0)

        cond = eq(
            r"\text{interior standalone optimum requires }\;\Phi_L < 1,"
            r"\qquad\text{(A3): }\Phi_L \geq 1",
            font_size=35,
        ).next_to(pure, DOWN, buff=0.5)
        with self.voiceover(
            "Exactly as in the H-regime analysis of part two, an interior"
            " standalone optimum exists only when the option premium ratio"
            " Phi L is below one. Assumption A three imposes the opposite."
        ):
            self.play(Write(cond), run_time=1.6)

        concl1 = MathTex(
            r"\Rightarrow\;\text{at every } K\text{, $L$-revenue falls"
            r" short: no finite exercise boundary in } L",
            font_size=28,
            color=C_L,
        ).next_to(cond, DOWN, buff=0.4)
        with self.voiceover(
            "So at every capacity level, markup-adjusted low-regime revenue"
            " falls short of what exercise requires. The standalone problem"
            " has no finite trigger: the pure low-regime firm waits forever."
        ):
            self.play(FadeIn(concl1), run_time=1.2)

        self.clear_body()

        sup = eq(r"\text{Suppose } A_1 > 0.", font_size=38, color=C_COST).shift(
            UP * 2.4 + LEFT * 3.6
        )
        with self.voiceover("Now suppose A one were strictly positive."):
            self.play(Write(sup), run_time=1.0)

        claim = eq(
            r"\text{Claim: }\beta_L^+ > \beta_H\qquad(3.01 > 1.55)",
            font_size=36,
        ).next_to(sup, DOWN, buff=0.4, aligned_edge=LEFT)
        mono = eq(
            r"Q(\beta;\mu,\rho) = \tfrac{1}{2}\sigma^2\beta(\beta-1)"
            r" + \mu\beta - \rho:\qquad"
            r"\frac{\partial Q}{\partial \rho} = -1,\quad"
            r"\frac{\partial Q}{\partial \mu} = \beta > 0",
            font_size=32,
        ).next_to(claim, DOWN, buff=0.4, aligned_edge=LEFT)
        with self.voiceover(
            "The key fact is that beta L plus exceeds beta H. Look at the"
            " characteristic quadratic as a function of its drift and"
            " discount. Raising the discount shifts the whole parabola down."
            " Lowering the drift also shifts it down wherever beta is"
            " positive."
        ):
            self.play(Write(claim), run_time=1.2)
            self.play(Write(mono), run_time=1.6)

        ax = _q_parabola_axes(width=8.0, height=3.1).shift(DOWN * 1.85)
        cur_h = ax.plot(_Q_H, x_range=[-3.2, 4.0], color=C_H, stroke_width=3)
        cur_l = ax.plot(_Q_L, x_range=[-3.45, 4.3], color=C_L, stroke_width=3)
        lab_qh = MathTex(r"Q_H", font_size=30, color=C_H).next_to(
            ax.coords_to_point(3.3, _Q_H(3.3)), LEFT, buff=0.15
        )
        lab_ql = MathTex(r"Q_L", font_size=30, color=C_L).next_to(
            ax.coords_to_point(4.2, _Q_L(4.2)), RIGHT, buff=0.08
        )
        bh = BASELINE["beta_H"]
        bl = BASELINE["beta_L_plus"]
        dot_h = Dot(ax.coords_to_point(bh, 0), color=C_H, radius=0.06)
        dot_l = Dot(ax.coords_to_point(bl, 0), color=C_L, radius=0.06)
        arr = Arrow(
            ax.coords_to_point(bh, 0.10),
            ax.coords_to_point(bl, 0.10),
            color=C_OPTION,
            buff=0.05,
            stroke_width=4,
            max_tip_length_to_length_ratio=0.12,
        )
        with self.voiceover(
            "Moving from the H-regime quadratic to the low-regime one does"
            " both at once: the discount rises from r to r plus lambda, and"
            " the drift falls from mu H to mu L. The parabola drops, so its"
            " positive root slides to the right: beta L plus is three point"
            " zero one, beta H only one point five five."
        ):
            self.play(Create(ax), run_time=0.8)
            self.play(Create(cur_h), FadeIn(lab_qh), FadeIn(dot_h), run_time=1.2)
            self.play(Create(cur_l), FadeIn(lab_ql), FadeIn(dot_l), run_time=1.2)
            self.play(Create(arr), run_time=0.8)

        self.clear_body(sup)
        dom = eq(
            r"X \to \infty:\quad A_1 X^{\beta_L^+} \gg C X^{\beta_H}"
            r"\quad\Rightarrow\quad F_L(X) \sim A_1 X^{\beta_L^+}",
            font_size=36,
        ).shift(UP * 1.1)
        with self.voiceover(
            "Because beta L plus is the larger exponent, a positive A one"
            " means the homogeneous term eventually dominates: for large X"
            " the option value grows like X to the three point zero one."
        ):
            self.play(Write(dom), run_time=1.6)

        npv = eq(
            r"\text{any payoff: } V - I = A_{\text{eff}}X - b"
            r" \;\;\text{grows linearly in } X",
            font_size=34,
        ).next_to(dom, DOWN, buff=0.5)
        with self.voiceover(
            "But every payoff the firm can actually collect grows only"
            " linearly in demand. A value function that outgrows every"
            " attainable payoff can only be sustained if exercise truncates"
            " it: there would have to be a finite low-regime exercise"
            " boundary where value matching cuts the explosive branch off."
        ):
            self.play(Write(npv), run_time=1.6)

        contra = eq(
            r"\Rightarrow\;\text{finite $L$-exercise boundary exists}"
            r"\;\;\bot\;\;\text{(A3)}\qquad\Rightarrow\qquad A_1 \leq 0",
            font_size=36,
            color=C_COST,
        ).next_to(npv, DOWN, buff=0.6)
        with self.voiceover(
            "And that is precisely what assumption A three rules out: under"
            " A three, no finite low-regime boundary exists. Contradiction."
            " So A one cannot be positive."
        ):
            self.play(Write(contra), run_time=1.4)
        self.pause(0.5)
        self.clear_body()


class P3S09RuleOutNegative(PaperScene):
    def construct(self):
        self.set_header("Step 5b: ruling out A1 < 0", kicker="PROP 1, PROOF")

        sup = eq(
            r"\text{Suppose } A_1 < 0:\qquad F_L(X) = A_1 X^{\beta_L^+}"
            r" + C X^{\beta_H} \;<\; C X^{\beta_H}\;\;\forall X > 0",
            font_size=34,
        ).shift(UP * 2.2)
        with self.voiceover(
            "Now the other direction. If A one were negative, the option"
            " value would lie strictly below C X to the beta H for every"
            " positive demand level."
        ):
            self.play(Write(sup), run_time=1.6)

        strat = VGroup(
            Text("The pure switching strategy:", font_size=28, color=C_OPTION),
            Text("1. never invest while in regime L", font_size=25),
            Text(
                "2. when the switch arrives, hold the H-option,"
                " invest at the H-trigger",
                font_size=25,
            ),
        ).arrange(DOWN, buff=0.25, aligned_edge=LEFT)
        strat.next_to(sup, DOWN, buff=0.5)
        with self.voiceover(
            "To see why that is impossible, consider one specific,"
            " perfectly feasible strategy: do nothing in the low regime,"
            " wait for the Poisson switch, and then run the optimal"
            " H-regime policy from part two, investing at the H trigger."
        ):
            self.play(FadeIn(strat), run_time=1.6)

        wode = eq(
            r"\tfrac{1}{2}\sigma^2 X^2 W'' + \mu_L X W' - (r+\lambda)W"
            r" + \lambda B_H X^{\beta_H} = 0",
            font_size=35,
        ).next_to(strat, DOWN, buff=0.5)
        with self.voiceover(
            "Call its value W of X. The same expected-return computation as"
            " before applies, with the same switch payoff B H X to the beta"
            " H, so W solves exactly the same forced differential equation."
        ):
            self.play(Write(wode), run_time=1.6)

        self.clear_body(wode)
        self.play(wode.animate.to_edge(UP, buff=1.45))

        pins = VGroup(
            eq(
                r"W = a_1 X^{\beta_L^+} + a_2 X^{\beta_L^-} + C X^{\beta_H}",
                font_size=34,
            ),
            eq(
                r"W(0) = 0 \;\Rightarrow\; a_2 = 0",
                font_size=34,
            ),
            eq(
                r"\text{no $L$-exercise boundary + no-bubble growth}"
                r"\;\Rightarrow\; a_1 = 0",
                font_size=34,
            ),
            eq(
                r"\Rightarrow\quad W(X) = C\,X^{\beta_H}\;\;\text{exactly}",
                font_size=38,
                color=C_OPTION,
            ),
        ).arrange(DOWN, buff=0.42)
        pins.next_to(wode, DOWN, buff=0.6)
        with self.voiceover(
            "So W has the same general form, with its own coefficients a"
            " one and a two on the homogeneous powers."
        ):
            self.play(Write(pins[0]), run_time=1.2)
        with self.voiceover(
            "The boundary condition at zero kills the negative power, just as before."
        ):
            self.play(Write(pins[1]), run_time=1.0)
        with self.voiceover(
            "And this strategy never exercises in the low regime by"
            " construction, so there is no boundary to support an explosive"
            " branch; the no-bubble growth condition, that the value of a"
            " strategy cannot outgrow the payoffs it delivers, kills the"
            " positive power too."
        ):
            self.play(Write(pins[2]), run_time=1.4)
        with self.voiceover(
            "What remains is exactly the particular solution: the pure"
            " switching strategy is worth precisely C times X to the beta"
            " H."
        ):
            self.play(Write(pins[3]), run_time=1.2)

        self.clear_body()
        opt = eq(
            r"F_L(X) \;\geq\; W(X) = C X^{\beta_H}"
            r"\qquad\text{(optimum dominates any feasible strategy)}",
            font_size=36,
        ).shift(UP * 1.3)
        with self.voiceover(
            "But F L is the value of the optimal policy, and the pure"
            " switching strategy is feasible, so F L must be at least W."
            " That directly contradicts F L lying strictly below C X to the"
            " beta H."
        ):
            self.play(Write(opt), run_time=1.6)

        concl = eq(
            r"A_1 = 0\quad\text{exactly:}\qquad "
            r"F_L(X) = C\,X^{\beta_H},\quad X < X^*",
            font_size=42,
            color=C_OPTION,
        ).next_to(opt, DOWN, buff=0.7)
        box = highlight(concl)
        with self.voiceover(
            "A one can be neither positive nor negative, so it is exactly"
            " zero. Under assumption A three, the simplified option value C"
            " X to the beta H is not an approximation; it is the exact"
            " solution, and the option value derives entirely from the"
            " expected regime switch."
        ):
            self.play(Write(concl), run_time=1.4)
            self.play(Create(box), run_time=0.8)
        self.pause(0.5)
        self.clear_body()


class P3S10TriggerConsistency(PaperScene):
    def construct(self):
        self.set_header("Two conditions, one unknown", kicker="PROP 1, PROOF")

        bdef = eq(
            r"b \equiv \delta K/r + cK^{\gamma}\qquad\text{(total cost)}",
            font_size=34,
            color=C_COST,
        ).shift(UP * 2.35)
        vm = MathTex(
            r"\text{value matching:}\quad",
            r"C\,(X^*)^{\beta_H} = A_{\text{eff}}\,X^* - b",
            font_size=36,
        ).next_to(bdef, DOWN, buff=0.5)
        sp = MathTex(
            r"\text{smooth pasting:}\quad",
            r"\beta_H\, C\,(X^*)^{\beta_H - 1} = A_{\text{eff}}",
            font_size=36,
        ).next_to(vm, DOWN, buff=0.4)
        vm[1].set_color(C_TEXT)
        sp[1].set_color(C_TEXT)
        with self.voiceover(
            "There is a loose end. At the investment trigger, the option"
            " value must satisfy two boundary conditions: value matching,"
            " where the option equals the investment payoff, and smooth"
            " pasting, where their slopes agree."
        ):
            self.play(Write(bdef), run_time=1.0)
            self.play(Write(vm), run_time=1.2)
            self.play(Write(sp), run_time=1.2)

        worry = MathTex(
            r"\text{$C$ is already pinned by the ODE: two equations,"
            r" ONE unknown } X^*\text{.  Overdetermined?}",
            font_size=28,
            color=C_DEMAND,
        ).next_to(sp, DOWN, buff=0.45)
        with self.voiceover(
            "Normally these two conditions determine two unknowns: the"
            " option coefficient and the trigger. But here C is already"
            " fixed by the differential equation, so we have two equations"
            " in the single unknown X star. Is the system overdetermined?"
        ):
            self.play(FadeIn(worry), run_time=1.2)

        div = eq(
            r"\frac{C(X^*)^{\beta_H}}{\beta_H C (X^*)^{\beta_H-1}}"
            r" = \frac{A_{\text{eff}}X^* - b}{A_{\text{eff}}}"
            r"\quad\Longrightarrow\quad"
            r"\frac{X^*}{\beta_H} = X^* - \frac{b}{A_{\text{eff}}}",
            font_size=34,
        ).next_to(worry, DOWN, buff=0.5)
        with self.voiceover(
            "Divide value matching by smooth pasting. On the left, C and"
            " the powers of X star cancel, leaving X star over beta H. On"
            " the right, A effective divides through."
        ):
            self.play(Write(div), run_time=1.8)

        self.clear_body(div)
        self.play(div.animate.to_edge(UP, buff=1.5))

        solve = eq(
            r"X^*\Bigl(1 - \frac{1}{\beta_H}\Bigr) = \frac{b}{A_{\text{eff}}}"
            r"\quad\Longrightarrow\quad"
            r" X^* = \frac{\beta_H}{\beta_H - 1}\cdot"
            r"\frac{\delta K^*/r + c(K^*)^{\gamma}}"
            r"{A_{\text{eff}}(\phi^*, K^*)}",
            font_size=35,
        ).next_to(div, DOWN, buff=0.55)
        with self.voiceover(
            "Collecting X star on the left and rearranging delivers the"
            " trigger equation used throughout the paper: the option markup"
            " beta H over beta H minus one, times total cost over A"
            " effective."
        ):
            self.play(Write(solve), run_time=1.8)

        nums = eq(
            r"\frac{\beta_H}{\beta_H - 1} \approx 2.81,\qquad "
            r"X^* \approx 0.0047",
            font_size=34,
            color=C_OPTION,
        ).next_to(solve, DOWN, buff=0.45)
        with self.voiceover(
            "At the baseline, the markup is about two point eight one and"
            " the trigger is about zero point zero zero four seven, jointly"
            " determined with K star and phi star since A effective depends"
            " on both."
        ):
            self.play(Write(nums), run_time=1.2)

        foc = eq(
            r"F(X) = \max_{\hat X}\;\bigl(A_{\text{eff}}\hat{X} - b\bigr)"
            r"\Bigl(\tfrac{X}{\hat X}\Bigr)^{\beta_H}:"
            r"\qquad \frac{dF}{d\hat X} = 0 \;\Leftrightarrow\;"
            r"\hat{X} = \frac{\beta_H}{\beta_H - 1}\cdot\frac{b}{A_{\text{eff}}}",
            font_size=32,
        ).next_to(nums, DOWN, buff=0.55)
        with self.voiceover(
            "Why is the pair of conditions consistent rather than"
            " overdetermined? Because they are jointly the first-order"
            " conditions of the underlying stopping problem. Choosing the"
            " threshold to maximize the discounted exercise payoff, value"
            " matching defines the payoff being maximized, and smooth"
            " pasting is exactly its first-order condition; differentiating"
            " reproduces the same trigger."
        ):
            self.play(Write(foc), run_time=2.0)
        with self.voiceover(
            "So with C predetermined and K star and phi star at their"
            " optima, the two boundary conditions collapse into one"
            " equation for one unknown. Nothing is overdetermined."
        ):
            self.play(Indicate(solve, color=C_OPTION), run_time=1.2)
        self.pause(0.5)
        self.clear_body()


class P3S11PhiLemma(PaperScene):
    def construct(self):
        self.set_header("The interior training fraction", kicker="STEP 5 LEMMA")

        aeff = eq(
            r"A_{\text{eff}}(\phi) = w_L\bigl[(1-\phi)K\bigr]^{\alpha}"
            r" + w_H(\phi K)^{\alpha},\qquad "
            r"w_L = \frac{1}{r - \mu_L + \lambda},\quad "
            r"w_H = \frac{\lambda A_H}{r - \mu_L + \lambda}",
            font_size=31,
        ).shift(UP * 2.3)
        with self.voiceover(
            "Now the training fraction. Write A effective as a weighted sum"
            " of the two capacity terms: weight w L on inference and weight"
            " w H on training, where w H carries the arrival rate lambda"
            " and the H-regime perpetuity coefficient A H."
        ):
            self.play(Write(aeff), run_time=2.0)

        why = eq(
            r"b(K)\ \text{independent of}\ \phi\;\Rightarrow\;"
            r"\max_{\phi} \frac{A_{\text{eff}}^{\beta_H}}{b^{\beta_H-1}}"
            r"\;\Leftrightarrow\;\max_{\phi} A_{\text{eff}}(\phi)",
            font_size=33,
        ).next_to(aeff, DOWN, buff=0.45)
        with self.voiceover(
            "Costs depend only on total capacity, not on the split, so"
            " maximizing the option-value factor over phi is the same as"
            " maximizing A effective itself."
        ):
            self.play(Write(why), run_time=1.6)

        d1 = eq(
            r"\frac{\partial A_{\text{eff}}}{\partial \phi}"
            r" = \alpha K^{\alpha}\bigl[-w_L(1-\phi)^{\alpha-1}"
            r" + w_H\,\phi^{\alpha-1}\bigr]",
            font_size=35,
        ).next_to(why, DOWN, buff=0.5)
        with self.voiceover(
            "Differentiate with respect to phi. The inference term loses"
            " capacity, contributing minus w L times one minus phi to the"
            " alpha minus one; the training term gains, contributing plus w"
            " H times phi to the alpha minus one."
        ):
            self.play(Write(d1), run_time=1.6)

        inada = eq(
            r"\phi \to 0^+:\ \phi^{\alpha-1}\to+\infty\;\Rightarrow\;"
            r"\frac{\partial A_{\text{eff}}}{\partial\phi}\to+\infty,"
            r"\qquad"
            r"\phi \to 1^-:\ (1-\phi)^{\alpha-1}\to+\infty\;\Rightarrow\;"
            r"\frac{\partial A_{\text{eff}}}{\partial\phi}\to-\infty",
            font_size=29,
        ).next_to(d1, DOWN, buff=0.5)
        with self.voiceover(
            "Since alpha is between zero and one, the exponent alpha minus"
            " one is negative, and both ends explode. As phi goes to zero,"
            " phi to the alpha minus one diverges while the other power"
            " tends to one, so the derivative goes to plus infinity: the"
            " first unit of training has infinite marginal value."
        ):
            self.play(Write(inada), run_time=2.0)
        with self.voiceover(
            "Symmetrically, as phi approaches one the derivative goes to"
            " minus infinity: the last unit of inference has infinite"
            " marginal value. These are Inada conditions at both ends."
        ):
            self.play(Indicate(inada, color=C_TRAIN), run_time=1.2)

        ivt = MathTex(
            r"\text{derivative continuous on } (0,1)\text{, } +\infty"
            r"\text{ at } 0\text{, } -\infty\text{ at } 1"
            r"\;\;\Rightarrow\;\;\text{IVT: } \phi^*\text{ exists in } (0,1)",
            font_size=27,
            color=C_TEXT,
        ).next_to(inada, DOWN, buff=0.45)
        with self.voiceover(
            "The derivative is continuous on the open interval, positive"
            " near zero and negative near one, so by the intermediate value"
            " theorem it crosses zero at some interior phi star. Existence"
            " is done."
        ):
            self.play(FadeIn(ivt), run_time=1.2)

        self.clear_body()
        d2 = eq(
            r"\frac{\partial^2 A_{\text{eff}}}{\partial \phi^2}"
            r" = \alpha(\alpha-1)K^{\alpha}\bigl[w_L(1-\phi)^{\alpha-2}"
            r" + w_H\,\phi^{\alpha-2}\bigr] \;<\; 0",
            font_size=36,
        ).shift(UP * 1.9)
        with self.voiceover(
            "For uniqueness, differentiate once more. The prefactor alpha"
            " times alpha minus one is negative, and the bracket is a sum"
            " of two strictly positive powers, so the second derivative is"
            " strictly negative everywhere: A effective is strictly concave"
            " in phi, and the interior critical point is unique."
        ):
            self.play(Write(d2), run_time=1.8)

        foc1 = eq(
            r"w_H\,\phi^{\alpha-1} = w_L(1-\phi)^{\alpha-1}"
            r"\quad\Longrightarrow\quad"
            r"\frac{w_H}{w_L} = \Bigl(\frac{1-\phi^*}{\phi^*}\Bigr)^{\alpha-1}"
            r" = \Bigl(\frac{\phi^*}{1-\phi^*}\Bigr)^{1-\alpha}",
            font_size=33,
        ).next_to(d2, DOWN, buff=0.5)
        with self.voiceover(
            "Setting the first derivative to zero gives the first-order"
            " condition: the weighted marginal products are equalized."
            " Rearranged, the weight ratio w H over w L equals the training"
            " odds ratio phi star over one minus phi star, raised to the"
            " power one minus alpha."
        ):
            self.play(Write(foc1), run_time=1.8)

        foc2 = eq(
            r"\frac{w_H}{w_L} = \lambda A_H = \frac{\lambda}{r-\mu_H}"
            r"\quad\Longrightarrow\quad"
            r"\Bigl(\frac{\phi^*}{1-\phi^*}\Bigr)^{1-\alpha}"
            r" = \frac{\lambda}{r - \mu_H}",
            font_size=35,
        ).next_to(foc1, DOWN, buff=0.5)
        foc2[0][-22:].set_color(C_TRAIN)
        with self.voiceover(
            "And the weight ratio simplifies beautifully: the common"
            " denominator r minus mu L plus lambda cancels, leaving lambda"
            " times A H, which is lambda over r minus mu H. The training"
            " odds depend on beliefs and the post-AGI prize, nothing else."
        ):
            self.play(Write(foc2), run_time=1.8)

        self.clear_body(foc2)
        self.play(foc2.animate.scale(0.85).to_edge(UP, buff=1.4))

        from ai_lab_investment.models.base_model import SingleFirmModel
        from ai_lab_investment.models.parameters import ModelParameters

        params = ModelParameters()
        model = SingleFirmModel(params)
        _, _, phi_model = model.optimal_trigger_capacity_phi()

        alpha, r, mu_H = params.alpha, params.r, params.mu_H

        def phi_star(lam: float) -> float:
            ratio = (lam / (r - mu_H)) ** (1.0 / (1.0 - alpha))
            return ratio / (1.0 + ratio)

        lams = np.linspace(0.005, 0.5, 140)
        phis = np.array([phi_star(la) for la in lams])
        ax = clean_axes(
            x_range=[0, 0.5], y_range=[0, 1.0], width=8.4, height=3.6
        ).shift(DOWN * 1.5)
        curve = ax.plot_line_graph(
            lams, phis, line_color=C_TRAIN, add_vertex_dots=False
        )
        x_lab = MathTex(r"\lambda", font_size=32, color=C_DEMAND).next_to(
            ax.x_axis, RIGHT, buff=0.15
        )
        y_lab = MathTex(r"\phi^*", font_size=32, color=C_TRAIN).next_to(
            ax.y_axis, UP, buff=0.15
        )
        with self.voiceover(
            "Inverting the first-order condition gives phi star in closed"
            " form as a function of lambda. Plotting it: the optimal"
            " training share rises steeply at low arrival rates and"
            " flattens as training saturates."
        ):
            self.play(Create(ax), FadeIn(x_lab), FadeIn(y_lab), run_time=1.0)
            self.play(Create(curve), run_time=1.8)

        lam0 = params.lam
        dot = Dot(ax.coords_to_point(lam0, phi_model), color=C_DEMAND)
        note = eq(
            r"\lambda = 0.10:\;\;\phi^* \approx 0.70",
            font_size=34,
            color=C_DEMAND,
        ).next_to(dot, DOWN + RIGHT, buff=0.3)
        with self.voiceover(
            "At the baseline arrival rate of zero point one zero, the model"
            " solver and the closed form agree: phi star is about zero"
            " point seven zero. Seventy percent of capacity goes to"
            " training."
        ):
            self.play(FadeIn(dot, scale=2), Write(note), run_time=1.4)
        self.pause(0.5)
        self.clear_body()


class P3S12ComparativeStatics(PaperScene):
    def construct(self):
        self.set_header("Comparative statics of phi*", kicker="STEP 6")

        foc = eq(
            r"G(\phi^*) \equiv \Bigl(\frac{\phi^*}{1-\phi^*}\Bigr)^{1-\alpha}"
            r" = \frac{w_H}{w_L},\qquad G'(\phi) > 0",
            font_size=38,
        ).shift(UP * 2.1)
        with self.voiceover(
            "Comparative statics follow from the implicit function theorem"
            " applied to the first-order condition. The left side is a"
            " strictly increasing function of phi star, so phi star moves"
            " in the same direction as the weight ratio w H over w L. The"
            " strictly negative second derivative from the lemma guarantees"
            " the implicit function theorem applies."
        ):
            self.play(Write(foc), run_time=1.8)

        s1 = eq(
            r"\text{(i)}\quad \frac{w_H}{w_L} = \lambda A_H"
            r"\ \text{increasing in }\lambda"
            r"\quad\Rightarrow\quad \frac{\partial \phi^*}{\partial \lambda} > 0",
            font_size=35,
        ).next_to(foc, DOWN, buff=0.6)
        with self.voiceover(
            "First, lambda. The ratio is lambda times A H, which is"
            " directly increasing in lambda, so the optimal training"
            " fraction rises with the arrival rate. More optimistic"
            " timelines mean more training compute."
        ):
            self.play(Write(s1), run_time=1.6)

        s2 = eq(
            r"\text{(ii)}\quad \frac{w_H}{w_L} = \frac{\lambda}{r - \mu_H}"
            r"\ \text{increasing in }\mu_H"
            r"\quad\Rightarrow\quad \frac{\partial \phi^*}{\partial \mu_H} > 0",
            font_size=35,
        ).next_to(s1, DOWN, buff=0.5)
        with self.voiceover(
            "Second, mu H. A higher post-AGI growth rate shrinks r minus mu"
            " H, raising the ratio, so phi star rises: a bigger prize after"
            " the switch tilts the same hardware toward training."
        ):
            self.play(Write(s2), run_time=1.6)

        s3 = MathTex(
            r"\text{(iii)}\quad \frac{w_H}{w_L} = ",
            r"\frac{\lambda A_H/(r - \mu_L + \lambda)}{1/(r - \mu_L + \lambda)}",
            r"= \lambda A_H\quad\text{(no $\mu_L$)}",
            font_size=35,
        ).next_to(s2, DOWN, buff=0.5)
        with self.voiceover(
            "Third, and most surprising: phi star is completely independent"
            " of the low-regime growth rate. Write the ratio out: both"
            " weights carry the same factor, one over r minus mu L plus"
            " lambda."
        ):
            self.play(Write(s3), run_time=1.6)

        box = highlight(s3[1], color=C_L)
        with self.voiceover(
            "The common factor cancels top and bottom, and mu L disappears."
            " Economically, the low-regime drift raises the value of"
            " inference revenue and the value of the switching continuation"
            " in exactly the same proportion, so it cannot tilt the split."
        ):
            self.play(Create(box), run_time=0.9)

        concl = MathTex(
            r"\text{Training intensity reveals beliefs } (\lambda, \mu_H)"
            r"\text{, not current conditions } (\mu_L)\text{.}",
            font_size=29,
            color=C_TRAIN,
        ).next_to(s3, DOWN, buff=0.6)
        with self.voiceover(
            "That is the testable content of the lemma: training intensity"
            " reveals a lab's beliefs about timelines and the post-AGI"
            " market, not the conditions of today's market."
        ):
            self.play(FadeIn(concl), run_time=1.2)
        self.pause(0.5)
        self.clear_body()


class P3S13LambdaChannels(PaperScene):
    def construct(self):
        self.set_header("The role of lambda", kicker="REMARK 1")

        ch1 = eq(
            r"\text{trigger channel:}\quad \lambda\uparrow\;\Rightarrow\;"
            r"A_{\text{eff}}\uparrow\;\Rightarrow\;"
            r"X^* = \frac{\beta_H}{\beta_H-1}\cdot\frac{b}{A_{\text{eff}}}"
            r"\downarrow",
            font_size=34,
        ).shift(UP * 1.9)
        ch2 = eq(
            r"\text{allocation channel:}\quad \lambda\uparrow\;\Rightarrow\;"
            r"\frac{w_H}{w_L}\uparrow\;\Rightarrow\;\phi^*\uparrow"
            r"\qquad(K^*\ \text{unchanged})",
            font_size=34,
        ).next_to(ch1, DOWN, buff=0.5)
        with self.voiceover(
            "Remark one collects the two ways the arrival rate moves the"
            " solution. The trigger channel: higher lambda raises A"
            " effective, which lowers the investment trigger, so optimistic"
            " firms invest sooner."
        ):
            self.play(Write(ch1), run_time=1.6)
        with self.voiceover(
            "And the allocation channel: higher lambda raises the weight"
            " ratio, pushing the training fraction up. Capacity K star, by"
            " contrast, is untouched, since it depends only on cost and"
            " technology parameters."
        ):
            self.play(Write(ch2), run_time=1.6)

        self.clear_body()

        from ai_lab_investment.models.base_model import SingleFirmModel
        from ai_lab_investment.models.parameters import ModelParameters

        lam_vals = np.linspace(0.01, 0.80, 48)
        X_ref = 0.01
        f_l = np.full_like(lam_vals, np.nan)
        c_vals = np.full_like(lam_vals, np.nan)
        f_h_ref = SingleFirmModel(ModelParameters()).option_value_H(X_ref)
        for i, lam in enumerate(lam_vals):
            try:
                m = SingleFirmModel(ModelParameters(lam=float(lam)))
                f_l[i] = m.option_value_L(X_ref)
                c_vals[i] = m.particular_solution_coeff()
            except (ValueError, RuntimeError):
                continue

        ax1 = clean_axes(
            x_range=[0, 0.82], y_range=[0, 0.030], width=5.4, height=3.6
        ).shift(LEFT * 3.4 + DOWN * 0.9)
        ax2 = clean_axes(
            x_range=[0, 0.82], y_range=[0, 38], width=5.4, height=3.6
        ).shift(RIGHT * 3.4 + DOWN * 0.9)
        t1 = MathTex(r"F_L(X = 0.01)", font_size=26, color=C_L).next_to(
            ax1, UP, buff=0.25
        )
        t2 = Text("coefficient C", font_size=24, color=C_OPTION).next_to(
            ax2, UP, buff=0.25
        )
        xl1 = MathTex(r"\lambda", font_size=28, color=C_DEMAND).next_to(
            ax1.x_axis, DOWN, buff=0.15
        )
        xl2 = MathTex(r"\lambda", font_size=28, color=C_DEMAND).next_to(
            ax2.x_axis, DOWN, buff=0.15
        )
        with self.voiceover(
            "The paper's figure quantifies the option-value side of this,"
            " and we recompute it here directly from the model code,"
            " evaluating the pre-adoption option at a reference demand of"
            " zero point zero one across a grid of arrival rates."
        ):
            self.play(
                Create(ax1),
                Create(ax2),
                FadeIn(t1),
                FadeIn(t2),
                FadeIn(xl1),
                FadeIn(xl2),
                run_time=1.4,
            )

        fl_curve = ax1.plot_line_graph(
            lam_vals, f_l, line_color=C_L, add_vertex_dots=False
        )
        fh_line = DashedLine(
            ax1.coords_to_point(0, f_h_ref),
            ax1.coords_to_point(0.82, f_h_ref),
            color=C_H,
        )
        fh_lab = MathTex(r"F_H", font_size=28, color=C_H).next_to(
            fh_line.get_end(), UP + LEFT, buff=0.1
        )
        with self.voiceover(
            "On the left, F L rises steeply at first and then concavely in"
            " lambda, climbing toward the post-adoption benchmark F H shown"
            " as the dashed line: as the expected switch time shrinks, the"
            " pre-AGI option converges to the post-AGI one."
        ):
            self.play(Create(fl_curve), run_time=1.8)
            self.play(Create(fh_line), FadeIn(fh_lab), run_time=1.0)

        c_curve = ax2.plot_line_graph(
            lam_vals, c_vals, line_color=C_OPTION, add_vertex_dots=False
        )
        with self.voiceover(
            "On the right, the particular-solution coefficient C increases"
            " monotonically in lambda, from near zero toward B H of about"
            " thirty-seven point six: the mechanism operates entirely"
            " through the continuation-value channel we derived."
        ):
            self.play(Create(c_curve), run_time=1.8)

        lam0 = 0.10
        m0 = SingleFirmModel(ModelParameters(lam=lam0))
        dot1 = Dot(ax1.coords_to_point(lam0, m0.option_value_L(X_ref)), color=C_DEMAND)
        dot2 = Dot(
            ax2.coords_to_point(lam0, m0.particular_solution_coeff()), color=C_DEMAND
        )
        with self.voiceover(
            "The baseline belief sits here: lambda of zero point one zero"
            " gives C of about twenty-one point one, the number we computed"
            " analytically earlier. Note also the concavity: around the"
            " policy range, good news about timelines moves the option"
            " value less than bad news of the same size."
        ):
            self.play(FadeIn(dot1, scale=2), FadeIn(dot2, scale=2), run_time=1.0)
        self.pause(0.5)
        self.clear_body()


class P3S14Close(PaperScene):
    def construct(self):
        self.set_header("What we proved today", kicker="PART 3 RECAP")

        items = VGroup(
            MathTex(
                r"\text{1.  HJB in } L \;\to\; \text{forced Euler ODE"
                r" with discount } r + \lambda",
                font_size=30,
            ),
            MathTex(
                r"\text{2.  } C = -\lambda B_H / Q_L(\beta_H) > 0"
                r"\text{, pinned by the ODE alone}",
                font_size=30,
            ),
            MathTex(
                r"\text{3.  Under (A3), } A_1 = 0\text{ exactly: }"
                r" F_L = C X^{\beta_H}",
                font_size=30,
            ),
            MathTex(
                r"\text{4.  VM + SP consistent: one unknown } X^*"
                r"\text{, the trigger formula}",
                font_size=30,
            ),
            MathTex(
                r"\text{5.  } \phi^*\text{ interior, unique, increasing in }"
                r" \lambda\text{ and } \mu_H\text{, independent of } \mu_L",
                font_size=30,
            ),
        ).arrange(DOWN, buff=0.42, aligned_edge=LEFT)
        items.shift(DOWN * 0.2)

        narrations = [
            "To recap: the low-regime Bellman equation became a forced"
            " Euler equation, with the regime switch acting as an extra"
            " discount and as a forcing term.",
            "The forcing coefficient C came straight out of the equation,"
            " positive because beta H sits between the roots of the"
            " low-regime quadratic.",
            "Under assumption A three we ruled out both signs of A one, so"
            " the simplified option value is exact, not an approximation.",
            "With C predetermined, value matching and smooth pasting"
            " jointly pin down the single trigger, reproducing the formula"
            " from part two with A effective in place of the H-regime"
            " coefficient.",
            "And the training fraction is interior and unique, pinned by"
            " beliefs and the post-AGI prize, and provably independent of"
            " today's growth rate.",
        ]
        for item, narration in zip(items, narrations, strict=True):
            with self.voiceover(narration):
                self.play(FadeIn(item, shift=RIGHT * 0.3), run_time=0.9)

        self.pause(0.4)
        nxt = VGroup(
            Text("Next: Part 4", font_size=34, weight="BOLD", color=C_OPTION),
            Text(
                "Duopoly, debt, default -- and the faith-based survival proof",
                font_size=26,
                color=C_TEXT,
            ),
        ).arrange(DOWN, buff=0.3)
        with self.voiceover(
            "Next time, part four: two firms race for the same prize, we"
            " add leverage and endogenous default, and we prove the"
            " faith-based survival result. See you there."
        ):
            self.clear_body()
            self.play(FadeIn(nxt), run_time=1.2)
        self.pause(0.8)
        self.play(FadeOut(nxt), FadeOut(self.header), run_time=0.8)
        self.header = None
