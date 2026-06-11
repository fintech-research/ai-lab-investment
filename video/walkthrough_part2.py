"""Derivation walkthrough, Part 2 (~15-20 min): the single-firm benchmark.

Covers the paper's Single-Firm Benchmark section: installed values in both
regimes (the A_eff derivation in full), the H-regime option value and
trigger, the live option-value figure, and Steps 1-4 of the proof of
Proposition 1. Steps 5, 5b, and 6 are covered in Part 3.

Render: uv run python video/render.py walkthrough_part2
Draft one scene: cd video && uv run manim render -ql walkthrough_part2.py P2S01Title
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
    MathTex,
    Polygon,
    Text,
    VGroup,
    Write,
)
from scene_base import PaperScene
from theme import (
    C_COST,
    C_DEMAND,
    C_FAINT,
    C_H,
    C_INFER,
    C_OPTION,
    C_TEXT,
    C_TRAIN,
    clean_axes,
    highlight,
)

SCENES = [
    "P2S01Title",
    "P2S02Recap",
    "P2S03InstalledH",
    "P2S04InstalledLSetup",
    "P2S05AEff",
    "P2S06Nesting",
    "P2S07OptionH",
    "P2S08TriggerH",
    "P2S09OptionFigure",
    "P2S10ProofSteps12",
    "P2S11ProofStep3",
    "P2S12ProofStep4",
    "P2S13CompStatics",
    "P2S14Next",
]


def _stack(*lines, buff: float = 0.42) -> VGroup:
    """Arrange equation lines top-down, left-aligned."""
    return VGroup(*lines).arrange(DOWN, buff=buff, aligned_edge=LEFT)


class P2S01Title(PaperScene):
    def construct(self):
        kicker = Text("DERIVATION WALKTHROUGH", font_size=24, color=C_FAINT)
        title = Text("Part 2: The Single-Firm Benchmark", font_size=46, weight="BOLD")
        sub = Text(
            "Installed values and the H-regime option",
            font_size=28,
            color=C_FAINT,
        )
        group = VGroup(kicker, title, sub).arrange(DOWN, buff=0.45)

        with self.voiceover(
            "Welcome to part two of the derivation walkthrough. We build the"
            " single-firm benchmark from the ground up."
        ):
            self.play(FadeIn(kicker), run_time=0.8)
            self.play(Write(title), run_time=1.8)
            self.play(FadeIn(sub), run_time=0.8)

        agenda = (
            VGroup(
                Text(
                    "1. Installed values V_H and V_L, and A effective",
                    font_size=26,
                    color=C_TEXT,
                ),
                Text(
                    "2. The H-regime option, trigger, and figure",
                    font_size=26,
                    color=C_TEXT,
                ),
                Text(
                    "3. Proof of Proposition 1, Steps 1 through 4",
                    font_size=26,
                    color=C_TEXT,
                ),
            )
            .arrange(DOWN, buff=0.3, aligned_edge=LEFT)
            .next_to(group, DOWN, buff=0.8)
        )
        with self.voiceover(
            "Three blocks: the installed values in each regime, including the"
            " A effective derivation the paper states without proof; the"
            " option value and trigger in the high regime; and steps one"
            " through four of the proof of Proposition one."
        ):
            self.play(FadeIn(agenda, shift=UP * 0.2), run_time=1.5)

        with self.voiceover(
            "The purpose is review before submission, so every algebraic step"
            " appears on screen. If something in the paper is wrong, it"
            " should be visible here."
        ):
            self.pause(0.5)
        self.play(FadeOut(group), FadeOut(agenda), run_time=0.7)


class P2S02Recap(PaperScene):
    def construct(self):
        self.set_header("The toolkit from Part 1", kicker="RECAP")

        perp = MathTex(
            r"\mathbb{E}\!\left[\int_0^\infty e^{-rt}X_t\,dt\;\middle|\;"
            r"X_0=X\right] = \frac{X}{r-\mu}",
            font_size=36,
        )
        perp_note = Text(
            "growing perpetuity (GBM with drift mu, requires r > mu)",
            font_size=22,
            color=C_FAINT,
        )
        with self.voiceover(
            "Two tools from part one do all the work today. First, the"
            " growing perpetuity: the expected discounted integral of a"
            " geometric Brownian motion with drift mu is X over r minus mu."
        ):
            block = _stack(perp, perp_note).to_edge(UP, buff=1.5).shift(LEFT * 0.5)
            self.play(Write(perp), run_time=1.5)
            self.play(FadeIn(perp_note), run_time=0.8)

        char = MathTex(
            r"Q(\beta) = \tfrac{1}{2}\sigma^2\beta(\beta-1)+\mu\beta-r=0",
            font_size=36,
        )
        roots = MathTex(
            r"\beta^+ > 1 > 0 > \beta^-,\qquad \beta_H \approx 1.553",
            font_size=34,
            color=C_OPTION,
        )
        char_block = _stack(char, roots).next_to(
            block, DOWN, buff=0.6, aligned_edge=LEFT
        )
        with self.voiceover(
            "Second, the characteristic equation: power functions X to the"
            " beta solve the pricing O D E exactly when beta is a root of"
            " this quadratic."
        ):
            self.play(Write(char), run_time=1.5)
        with self.voiceover(
            "There is one root above one and one negative root. With the"
            " high-regime drift, the positive root beta H is about one point"
            " five five at baseline."
        ):
            self.play(FadeIn(roots), run_time=1.0)

        choices = VGroup(
            VGroup(
                MathTex(r"X^*", font_size=40, color=C_OPTION),
                Text("when", font_size=24, color=C_FAINT),
            ).arrange(DOWN, buff=0.15),
            VGroup(
                MathTex(r"K", font_size=40, color=C_COST),
                Text("how much", font_size=24, color=C_FAINT),
            ).arrange(DOWN, buff=0.15),
            VGroup(
                MathTex(r"\phi", font_size=40, color=C_TRAIN),
                Text("training share", font_size=24, color=C_FAINT),
            ).arrange(DOWN, buff=0.15),
        ).arrange(RIGHT, buff=1.4)
        choices.next_to(char_block, DOWN, buff=0.8)
        with self.voiceover(
            "And the firm has three choice variables: the trigger X star, the"
            " capacity K, and the training fraction phi. Today we pin down"
            " the trigger and the capacity; phi's interior optimum is part"
            " three."
        ):
            self.play(FadeIn(choices, shift=UP * 0.2), run_time=1.5)
        self.pause(0.5)
        self.clear_body()


class P2S03InstalledH(PaperScene):
    def construct(self):
        self.set_header("Installed value in regime H", kicker="EQ. installed-value-H")

        flow = MathTex(
            r"\pi^H_t = X_t\,(\phi K)^{\alpha}",
            font_size=36,
        )
        flow[0][5:9].set_color(C_TRAIN)
        with self.voiceover(
            "Start in the absorbing high regime, with capacity K and training"
            " fraction phi already installed. The revenue flow is demand"
            " times training compute to the alpha."
        ):
            flow.to_edge(UP, buff=1.4).shift(LEFT * 3.0)
            self.play(Write(flow), run_time=1.2)

        ex = MathTex(
            r"\mathbb{E}[X_t \mid X_0 = X] = X e^{\mu_H t}",
            font_size=34,
        )
        rev1 = MathTex(
            r"\mathbb{E}\!\left[\int_0^\infty e^{-rt}X_t(\phi K)^\alpha\,dt\right]"
            r"= (\phi K)^\alpha \int_0^\infty X e^{-(r-\mu_H)t}\,dt",
            font_size=34,
        )
        rev2 = MathTex(
            r"= \frac{X(\phi K)^\alpha}{r-\mu_H}",
            font_size=34,
            color=C_H,
        )
        body = _stack(ex, rev1, rev2).next_to(flow, DOWN, buff=0.55, aligned_edge=LEFT)
        with self.voiceover(
            "The expected level of demand grows at rate mu H, so the expected"
            " discounted revenue is a growing perpetuity."
        ):
            self.play(Write(ex), run_time=1.2)
        with self.voiceover(
            "Pull the constant capacity term out of the integral; what is"
            " left is X times e to the minus r minus mu H times t."
        ):
            self.play(Write(rev1), run_time=1.6)
        with self.voiceover(
            "Integrating gives X times phi K to the alpha, over r minus mu H."
            " Discounting at twelve percent against six percent growth, the"
            " net rate is six percent."
        ):
            self.play(Write(rev2), run_time=1.0)

        cost = MathTex(
            r"\int_0^\infty e^{-rt}\,\delta K\,dt = \frac{\delta K}{r}",
            font_size=34,
            color=C_COST,
        ).next_to(body, DOWN, buff=0.5, aligned_edge=LEFT)
        with self.voiceover(
            "Operating costs are a constant flow delta K, so they are a level"
            " perpetuity: delta K over r. No drift, no uncertainty."
        ):
            self.play(Write(cost), run_time=1.2)

        self.clear_body()
        vh = MathTex(
            r"V_H(X,K,\phi)",
            r"=",
            r"\frac{X(\phi K)^\alpha}{r-\mu_H}",
            r"-",
            r"\frac{\delta K}{r}",
            r"= A_H\,X(\phi K)^\alpha - \frac{\delta K}{r}",
            font_size=38,
        ).shift(UP * 0.8)
        vh[2].set_color(C_H)
        vh[4].set_color(C_COST)
        a_h = MathTex(
            r"A_H \equiv \frac{1}{r-\mu_H} = \frac{1}{0.12-0.06} \approx 16.7",
            font_size=34,
        ).next_to(vh, DOWN, buff=0.55)
        with self.voiceover(
            "Putting the two pieces together gives the installed value in"
            " regime H: revenue perpetuity minus cost perpetuity. This is"
            " equation installed-value-H in the paper."
        ):
            self.play(Write(vh), run_time=1.8)
            self.play(Create(highlight(vh[:5])), run_time=0.7)
        with self.voiceover(
            "A H is shorthand for one over r minus mu H, about sixteen point"
            " seven at baseline: each unit of revenue flow is worth almost"
            " seventeen units of value."
        ):
            self.play(Write(a_h), run_time=1.2)

        zero = MathTex(
            r"\phi = 0 \;\Rightarrow\; V_H = -\frac{\delta K}{r} \;<\; 0",
            font_size=34,
            color=C_COST,
        ).next_to(a_h, DOWN, buff=0.55)
        with self.voiceover(
            "Note the role of phi: a firm that allocated everything to"
            " inference earns zero H-regime revenue, yet still pays the"
            " operating costs. In the post A G I world, only trained models"
            " capture value."
        ):
            self.play(Write(zero), run_time=1.2)
        self.pause(0.5)
        self.clear_body()


class P2S04InstalledLSetup(PaperScene):
    def construct(self):
        self.set_header("Installed value in regime L", kicker="KEY DERIVATION")

        with self.voiceover(
            "Now the low regime. The paper states the L-regime installed"
            " value without proof, so this is the derivation to check most"
            " carefully."
        ):
            self.pause(0.2)

        tau = MathTex(
            r"\tau \sim \text{Exp}(\lambda),\quad \tau \perp W",
            font_size=36,
            color=C_DEMAND,
        )
        with self.voiceover(
            "Let tau be the regime-switch time: exponential with rate lambda,"
            " independent of the Brownian motion driving demand."
        ):
            tau.to_edge(UP, buff=1.4).shift(LEFT * 3.2)
            self.play(Write(tau), run_time=1.2)

        vl = MathTex(
            r"V_L(X) = \mathbb{E}\!\left[\int_0^{\tau} e^{-rt}"
            r"\bigl(\pi^L_t - \delta K\bigr)\,dt"
            r" + e^{-r\tau}\,V_H(X_\tau)\right]",
            font_size=36,
        )
        pil = MathTex(
            r"\pi^L_t = X_t\,[(1-\phi)K]^\alpha",
            font_size=32,
            color=C_INFER,
        )
        block = _stack(vl, pil).next_to(tau, DOWN, buff=0.55, aligned_edge=LEFT)
        with self.voiceover(
            "Before tau, the firm earns the inference revenue flow net of"
            " operating costs. At tau the regime switches, and the firm's"
            " continuation value is the H-regime installed value we just"
            " derived, discounted back."
        ):
            self.play(Write(vl), run_time=1.8)
        with self.voiceover(
            "In regime L, revenue comes from the inference share: X times one"
            " minus phi times K, all to the alpha."
        ):
            self.play(Write(pil), run_time=1.0)

        with self.voiceover(
            "First, a bookkeeping step for the costs, because V H carries its"
            " own cost perpetuity inside."
        ):
            self.pause(0.2)

        ck1 = MathTex(
            r"\int_0^\tau e^{-rt}\,dt = \frac{1-e^{-r\tau}}{r}",
            font_size=32,
        )
        ck2 = MathTex(
            r"\Rightarrow\;\int_0^\tau e^{-rt}\delta K\,dt"
            r" + e^{-r\tau}\frac{\delta K}{r}"
            r" = \frac{\delta K}{r}\quad\text{(pathwise)}",
            font_size=32,
            color=C_COST,
        )
        _stack(ck1, ck2).next_to(block, DOWN, buff=0.55, aligned_edge=LEFT)
        with self.voiceover(
            "The cost flow delta K runs in both regimes. Path by path, the"
            " discounted cost up to tau is one minus e to the minus r tau,"
            " over r, times delta K."
        ):
            self.play(Write(ck1), run_time=1.2)
        with self.voiceover(
            "Adding the discounted post-switch cost perpetuity from inside"
            " V H, the e to the minus r tau terms cancel exactly, leaving a"
            " single perpetuity delta K over r. No expectation needed."
        ):
            self.play(Write(ck2), run_time=1.4)
            self.play(Indicate(ck2, color=C_COST), run_time=1.0)

        self.clear_body(tau)
        remain = MathTex(
            r"V_L(X) =",
            r"[(1-\phi)K]^\alpha\,"
            r"\mathbb{E}\!\left[\int_0^\tau e^{-rt}X_t\,dt\right]",
            r"+ A_H(\phi K)^\alpha\,\mathbb{E}\!\left[e^{-r\tau}X_\tau\right]",
            r"- \frac{\delta K}{r}",
            font_size=34,
        ).shift(UP * 0.4)
        remain[1].set_color(C_INFER)
        remain[2].set_color(C_H)
        remain[3].set_color(C_COST)
        with self.voiceover(
            "What remains are the two revenue pieces: the inference stream"
            " cut off at tau, and the switch term carrying the H-regime"
            " revenue coefficient A H times phi K to the alpha."
        ):
            self.play(Write(remain), run_time=2.0)

        todo = Text(
            "two expectations to compute",
            font_size=26,
            color=C_OPTION,
        ).next_to(remain, DOWN, buff=0.7)
        with self.voiceover(
            "So everything reduces to two expectations: the demand integral"
            " stopped at tau, and discounted demand sampled at tau. We"
            " compute both next."
        ):
            self.play(FadeIn(todo), run_time=0.8)
        self.pause(0.5)
        self.clear_body()


class P2S05AEff(PaperScene):
    def construct(self):
        self.set_header("Deriving A effective", kicker="KEY DERIVATION")

        t1_title = Text(
            "Term 1: inference stream up to tau", font_size=24, color=C_INFER
        )
        t1a = MathTex(
            r"\mathbb{E}\!\left[\int_0^\tau e^{-rt}X_t\,dt\right]"
            r"= \mathbb{E}\!\left[\int_0^\infty e^{-rt}X_t\,"
            r"\mathbf{1}_{\{t<\tau\}}\,dt\right]",
            font_size=34,
        )
        t1b = MathTex(
            r"= \int_0^\infty e^{-rt}\,\mathbb{E}[X_t]\,\Pr(\tau>t)\,dt"
            r"\qquad\text{(Fubini, $\tau\perp W$)}",
            font_size=34,
        )
        t1c = MathTex(
            r"= \int_0^\infty e^{-rt}\,X e^{\mu_L t}\,e^{-\lambda t}\,dt"
            r"= X\int_0^\infty e^{-(r-\mu_L+\lambda)t}\,dt",
            font_size=34,
        )
        t1d = MathTex(
            r"= \frac{X}{r-\mu_L+\lambda}",
            font_size=36,
            color=C_INFER,
        )
        block1 = _stack(t1_title, t1a, t1b, t1c, t1d, buff=0.38)
        block1.to_edge(UP, buff=1.35).shift(LEFT * 0.3)

        with self.voiceover(
            "Term one. Rewrite the random upper limit as an indicator inside"
            " an infinite integral: the integrand is alive only while t is"
            " less than tau."
        ):
            self.play(FadeIn(t1_title), run_time=0.6)
            self.play(Write(t1a), run_time=1.6)
        with self.voiceover(
            "Swap expectation and integral by Fubini. Because tau is"
            " independent of the Brownian motion, the expectation factors"
            " into the mean of X t times the survival probability of tau."
        ):
            self.play(Write(t1b), run_time=1.6)
        with self.voiceover(
            "The mean grows at mu L, and the survival probability decays at"
            " lambda. The exponents combine into a single decay rate: r"
            " minus mu L plus lambda."
        ):
            self.play(Write(t1c), run_time=1.6)
        with self.voiceover(
            "Integrating gives X over r minus mu L plus lambda. At baseline"
            " that effective discount rate is twelve minus one plus ten,"
            " twenty-one percent."
        ):
            self.play(Write(t1d), run_time=1.0)
            self.play(Create(highlight(t1d)), run_time=0.6)

        self.clear_body()
        t2_title = Text(
            "Term 2: discounted demand at the switch", font_size=24, color=C_H
        )
        t2a = MathTex(
            r"\mathbb{E}\!\left[e^{-r\tau}X_\tau\right]"
            r"= \int_0^\infty \lambda e^{-\lambda t}\,e^{-rt}\,"
            r"\mathbb{E}[X_t]\,dt",
            font_size=34,
        )
        t2b = MathTex(
            r"= \int_0^\infty \lambda e^{-\lambda t}\,X e^{(\mu_L-r)t}\,dt"
            r"= \lambda X\int_0^\infty e^{-(r-\mu_L+\lambda)t}\,dt",
            font_size=34,
        )
        t2c = MathTex(
            r"= \frac{\lambda X}{r-\mu_L+\lambda}",
            font_size=36,
            color=C_H,
        )
        block2 = _stack(t2_title, t2a, t2b, t2c, buff=0.38)
        block2.to_edge(UP, buff=1.35).shift(LEFT * 0.3)
        with self.voiceover(
            "Term two. Condition on the switch time: tau has density lambda e"
            " to the minus lambda t, and given tau equals t, the expectation"
            " of discounted demand is X times e to the mu L minus r times t."
        ):
            self.play(FadeIn(t2_title), run_time=0.6)
            self.play(Write(t2a), run_time=1.6)
        with self.voiceover(
            "Again all three exponentials merge into the same rate, r minus"
            " mu L plus lambda, now multiplied by lambda from the density."
        ):
            self.play(Write(t2b), run_time=1.6)
        with self.voiceover(
            "So discounted demand at the switch is lambda X over r minus mu L"
            " plus lambda. Same denominator as term one; the lambda upstairs"
            " is the only difference."
        ):
            self.play(Write(t2c), run_time=1.0)
            self.play(Create(highlight(t2c, color=C_H)), run_time=0.6)

        self.clear_body()
        asm = MathTex(
            r"V_L(X) =",
            r"\frac{[(1-\phi)K]^\alpha}{r-\mu_L+\lambda}\,X",
            r"+ \frac{\lambda\,A_H(\phi K)^\alpha}{r-\mu_L+\lambda}\,X",
            r"- \frac{\delta K}{r}",
            font_size=36,
        ).shift(UP * 1.5)
        asm[1].set_color(C_INFER)
        asm[2].set_color(C_H)
        asm[3].set_color(C_COST)
        with self.voiceover(
            "Substituting both expectations back, the L-regime installed"
            " value is linear in demand, with two revenue coefficients and"
            " the cost perpetuity."
        ):
            self.play(Write(asm), run_time=1.8)

        aeff = MathTex(
            r"A_{\text{eff}}(\phi,K)",
            r"=",
            r"\frac{[(1-\phi)K]^\alpha}{r-\mu_L+\lambda}",
            r"+",
            r"\frac{\lambda}{r-\mu_L+\lambda}\cdot\frac{(\phi K)^\alpha}{r-\mu_H}",
            font_size=38,
        ).next_to(asm, DOWN, buff=0.6)
        aeff[2].set_color(C_INFER)
        aeff[4].set_color(C_H)
        vl_final = MathTex(
            r"V_L(X,K,\phi) = A_{\text{eff}}(\phi,K)\,X - \frac{\delta K}{r}",
            font_size=36,
        ).next_to(aeff, DOWN, buff=0.55)
        with self.voiceover(
            "Collecting the coefficient on X and expanding A H gives exactly"
            " equation a-eff in the paper: A effective. The derivation"
            " checks out."
        ):
            self.play(Write(aeff), run_time=1.8)
            self.play(Create(highlight(aeff)), run_time=0.7)
        with self.voiceover(
            "And the installed value is A effective times X minus delta K"
            " over r, which is equation installed-value-L."
        ):
            self.play(Write(vl_final), run_time=1.2)

        with self.voiceover(
            "Read the two pieces. The first capitalizes inference revenue at"
            " the effective rate r minus mu L plus lambda: discounting plus"
            " the risk that the L regime ends."
        ):
            self.play(Indicate(aeff[2], color=C_INFER), run_time=1.2)
        with self.voiceover(
            "The second is the H-regime prize, A H times phi K to the alpha,"
            " weighted by lambda over r minus mu L plus lambda. At baseline"
            " that weight is point one over point two one, about forty-eight"
            " percent."
        ):
            self.play(Indicate(aeff[4], color=C_H), run_time=1.2)
        self.pause(0.5)
        self.clear_body()


class P2S06Nesting(PaperScene):
    def construct(self):
        self.set_header("Sanity checks: nested special cases", kicker="REMARK")

        n1 = MathTex(
            r"\phi = 1:\quad A_{\text{eff}}"
            r" = \frac{\lambda}{r-\mu_L+\lambda}\cdot\frac{K^\alpha}{r-\mu_H}",
            font_size=36,
        )
        n1[0][0:3].set_color(C_TRAIN)
        n2 = MathTex(
            r"\phi = 0:\quad A_{\text{eff}} = \frac{K^\alpha}{r-\mu_L+\lambda}",
            font_size=36,
        )
        n2[0][0:3].set_color(C_INFER)
        n3 = MathTex(
            r"\lambda = 0:\quad A_{\text{eff}}"
            r" = \frac{[(1-\phi)K]^\alpha}{r-\mu_L}",
            font_size=36,
        )
        n3[0][0:3].set_color(C_DEMAND)
        block = _stack(n1, n2, n3, buff=0.65).shift(UP * 0.3)

        with self.voiceover(
            "Three special cases verify the formula. With phi equal to one,"
            " all training, the inference term vanishes and value derives"
            " entirely from the regime switch."
        ):
            self.play(Write(n1), run_time=1.5)
        with self.voiceover(
            "With phi equal to zero, all inference, the prize term vanishes:"
            " a standard L-regime present value with no upside, still"
            " discounted at the higher rate because the regime can end."
        ):
            self.play(Write(n2), run_time=1.5)
        with self.voiceover(
            "And with lambda equal to zero, no switching ever, A effective"
            " collapses to the textbook perpetuity coefficient, one over r"
            " minus mu L, on the inference share alone."
        ):
            self.play(Write(n3), run_time=1.5)

        note = Text(
            "all three limits match the paper's Remark (Nesting)",
            font_size=24,
            color=C_FAINT,
        ).next_to(block, DOWN, buff=0.7)
        with self.voiceover(
            "All three limits agree with the nesting remark in the paper, so"
            " the formula degrades gracefully at the boundary."
        ):
            self.play(FadeIn(note), run_time=0.8)
        self.pause(0.5)
        self.clear_body()


class P2S07OptionH(PaperScene):
    def construct(self):
        self.set_header("Option value in regime H", kicker="EQ. option-H")

        hjb = MathTex(
            r"\tfrac{1}{2}\sigma^2X^2F_H'' + \mu_H X F_H' - rF_H = 0,"
            r"\qquad X < X_H^*",
            font_size=36,
        )
        with self.voiceover(
            "Now the option. Before investing, the firm holds no capacity, so"
            " in the continuation region the option value F H satisfies the"
            " homogeneous H J B equation: no cash flows, just drift,"
            " volatility, and discounting."
        ):
            hjb.to_edge(UP, buff=1.4)
            self.play(Write(hjb), run_time=1.6)

        guess = MathTex(
            r"F_H = X^\beta\;\Rightarrow\;"
            r"\tfrac{1}{2}\sigma^2\beta(\beta-1)+\mu_H\beta-r = 0",
            font_size=34,
        )
        gen = MathTex(
            r"F_H(X) = A\,X^{\beta_H} + B\,X^{\beta_H^-},"
            r"\qquad \beta_H \approx 1.553,\;\; \beta_H^- < 0",
            font_size=34,
        )
        bdry = MathTex(
            r"F_H(0) = 0\;\;\text{and}\;\;X^{\beta_H^-}\to\infty"
            r"\text{ as }X\to 0\;\Rightarrow\; B = 0",
            font_size=34,
            color=C_OPTION,
        )
        _stack(guess, gen, bdry).next_to(hjb, DOWN, buff=0.55, aligned_edge=LEFT)
        with self.voiceover(
            "Try a power solution. X to the beta works exactly when beta"
            " solves the H-regime characteristic equation from the recap."
        ):
            self.play(Write(guess), run_time=1.4)
        with self.voiceover(
            "The general solution is a combination of the two roots: beta H,"
            " about one point five five, and the negative root."
        ):
            self.play(Write(gen), run_time=1.4)
        with self.voiceover(
            "The boundary condition at zero kills the negative root. If"
            " demand hits zero it stays there, the option is worthless, but"
            " X to a negative power blows up. So B must be zero."
        ):
            self.play(Write(bdry), run_time=1.4)

        self.clear_body()
        vm = MathTex(
            r"\text{value matching:}\quad",
            r"A\,(X^*)^{\beta_H} = V_H(X^*,K,\phi) - I(K)",
            font_size=36,
        ).shift(UP * 0.9)
        sp = MathTex(
            r"\text{smooth pasting:}\quad",
            r"A\,\beta_H (X^*)^{\beta_H-1} = \frac{\partial V_H}{\partial X}"
            r" = A_H(\phi K)^\alpha",
            font_size=36,
        ).next_to(vm, DOWN, buff=0.6, aligned_edge=LEFT)
        vm[0].set_color(C_FAINT)
        sp[0].set_color(C_FAINT)
        with self.voiceover(
            "Two conditions pin down the two unknowns, the constant A and the"
            " trigger X star. Value matching: at the trigger, the option is"
            " worth exactly the installed value net of the investment cost."
        ):
            self.play(Write(vm), run_time=1.6)
        with self.voiceover(
            "And smooth pasting: the derivatives must also meet, otherwise"
            " the kink could be exploited by waiting slightly longer or"
            " investing slightly earlier. The slope of V H in X is A H times"
            " phi K to the alpha."
        ):
            self.play(Write(sp), run_time=1.6)

        note = Text(
            "next: divide the two conditions to solve for X*",
            font_size=24,
            color=C_OPTION,
        ).next_to(sp, DOWN, buff=0.8)
        with self.voiceover(
            "Dividing the first condition by the second eliminates A and"
            " hands us the trigger in closed form. That is the next scene."
        ):
            self.play(FadeIn(note), run_time=0.8)
        self.pause(0.4)
        self.clear_body()


class P2S08TriggerH(PaperScene):
    def construct(self):
        self.set_header("Deriving the H-regime trigger", kicker="EQ. trigger-H")

        bdef = MathTex(
            r"b(K) \equiv cK^\gamma + \frac{\delta K}{r}"
            r"\qquad\text{(total cost: investment + capitalized operating)}",
            font_size=34,
            color=C_COST,
        )
        with self.voiceover(
            "Bundle the costs into one symbol: b of K is the investment cost"
            " plus the capitalized operating cost. It returns throughout the"
            " proof."
        ):
            bdef.to_edge(UP, buff=1.35)
            self.play(Write(bdef), run_time=1.4)

        vm = MathTex(
            r"A\,(X^*)^{\beta_H} = A_H(\phi K)^\alpha X^* - b(K)",
            font_size=34,
        )
        sp = MathTex(
            r"A\,\beta_H(X^*)^{\beta_H-1} = A_H(\phi K)^\alpha",
            font_size=34,
        )
        div = MathTex(
            r"\frac{A\,(X^*)^{\beta_H}}{A\,\beta_H(X^*)^{\beta_H-1}}",
            r"=",
            r"\frac{A_H(\phi K)^\alpha X^* - b(K)}{A_H(\phi K)^\alpha}",
            font_size=34,
        )
        simp = MathTex(
            r"\frac{X^*}{\beta_H} = X^* - \frac{b(K)}{A_H(\phi K)^\alpha}",
            font_size=34,
        )
        _stack(vm, sp, div, simp, buff=0.4).next_to(
            bdef, DOWN, buff=0.5, aligned_edge=LEFT
        )
        with self.voiceover(
            "Write value matching with V H expanded: A H phi K to the alpha"
            " times X star, minus b of K."
        ):
            self.play(Write(vm), run_time=1.3)
        with self.voiceover(
            "And smooth pasting as before. Two equations, two unknowns."
        ):
            self.play(Write(sp), run_time=1.1)
        with self.voiceover(
            "Divide the first by the second. On the left, A cancels, and X"
            " star to the beta H over X star to the beta H minus one leaves"
            " just X star over beta H."
        ):
            self.play(Write(div), run_time=1.6)
        with self.voiceover(
            "On the right, A H phi K to the alpha divides through: X star"
            " minus b of K over A H phi K to the alpha."
        ):
            self.play(Write(simp), run_time=1.3)

        self.clear_body()
        re1 = MathTex(
            r"\left(1 - \frac{1}{\beta_H}\right)X^*"
            r" = \frac{b(K)}{A_H(\phi K)^\alpha}",
            font_size=36,
        ).shift(UP * 1.3)
        trig = MathTex(
            r"X_H^*",
            r"=",
            r"\frac{\beta_H}{\beta_H-1}",
            r"\cdot\frac{r-\mu_H}{(\phi K)^\alpha}"
            r"\left(cK^\gamma + \frac{\delta K}{r}\right)",
            font_size=40,
        ).next_to(re1, DOWN, buff=0.6)
        trig[2].set_color(C_OPTION)
        with self.voiceover(
            "Collect the X star terms: one minus one over beta H, times X"
            " star, equals cost over the revenue slope."
        ):
            self.play(Write(re1), run_time=1.4)
        with self.voiceover(
            "Multiply through by beta H over beta H minus one and substitute"
            " A H. This is equation trigger-H in the paper, exactly."
        ):
            self.play(Write(trig), run_time=1.6)
            self.play(Create(highlight(trig)), run_time=0.7)

        marsh = MathTex(
            r"\text{Marshallian level } X_M:\;"
            r" A_H(\phi K)^\alpha X_M = b(K)"
            r"\;\Rightarrow\; X_H^* = \frac{\beta_H}{\beta_H-1}\,X_M"
            r" \approx 2.81\,X_M",
            font_size=32,
        ).next_to(trig, DOWN, buff=0.65)
        with self.voiceover(
            "Compare with the Marshallian rule, invest when N P V is zero:"
            " that level is just cost over revenue slope, without the"
            " multiplier."
        ):
            self.play(Write(marsh), run_time=1.6)
        with self.voiceover(
            "So beta H over beta H minus one is the option premium. At"
            " baseline it is about two point eight: irreversibility plus"
            " volatility makes the firm wait for demand nearly three times"
            " the break-even level."
        ):
            self.play(Indicate(trig[2], color=C_OPTION), run_time=1.2)
        self.pause(0.5)
        self.clear_body()


class P2S09OptionFigure(PaperScene):
    def construct(self):
        self.set_header("The option-value figure, live", kicker="FIG. option-value")

        from ai_lab_investment.models.base_model import SingleFirmModel
        from ai_lab_investment.models.parameters import ModelParameters

        model = SingleFirmModel(ModelParameters())
        X_star, K_star = model.optimal_trigger_and_capacity("H")
        X_vals = np.linspace(0.001 * X_star, 2.2 * X_star, 200)
        F = np.array([model.option_value_H(x) for x in X_vals])
        npv = np.array([
            model.installed_value(x, K_star, "H") - model.investment_cost(K_star)
            for x in X_vals
        ])

        y_max = float(F.max()) * 1.1
        y_min = float(npv.min()) * 1.15
        ax = clean_axes(
            x_range=[0, X_vals[-1]], y_range=[y_min, y_max], width=9.0, height=4.4
        ).shift(DOWN * 1.0)
        x_lab = MathTex(r"X", font_size=30, color=C_FAINT).next_to(
            ax.x_axis, RIGHT, buff=0.2
        )

        sub = Text(
            "H-regime sub-problem (phi = 1), model code, baseline parameters",
            font_size=22,
            color=C_FAINT,
        ).to_edge(UP, buff=1.25)
        with self.voiceover(
            "Let us reproduce the paper's option-value figure directly from"
            " the model code, using the H-regime sub-problem at baseline"
            " parameters."
        ):
            self.play(FadeIn(sub), run_time=0.8)
            self.play(Create(ax), FadeIn(x_lab), run_time=1.0)

        npv_line = ax.plot_line_graph(
            X_vals, npv, line_color=C_FAINT, add_vertex_dots=False
        )
        npv_lab = Text("NPV of investing now", font_size=22, color=C_FAINT).move_to(
            ax.coords_to_point(X_vals[-1] * 0.66, y_min * 0.35)
        )
        with self.voiceover(
            "The gray line is the net present value of investing immediately"
            " at the optimal scale: A H times X times K star to the alpha,"
            " minus all costs. It is negative for low demand."
        ):
            self.play(Create(npv_line), FadeIn(npv_lab), run_time=1.8)

        f_line = ax.plot_line_graph(
            X_vals, F, line_color=C_OPTION, add_vertex_dots=False
        )
        f_lab = MathTex(
            r"F_H(X) = B_H X^{\beta_H}", font_size=30, color=C_OPTION
        ).move_to(ax.coords_to_point(X_vals[-1] * 0.17, y_max * 0.72))
        with self.voiceover(
            "The gold curve is the option value, B H times X to the beta H,"
            " computed from the same model class the paper figures use."
        ):
            self.play(Create(f_line), FadeIn(f_lab), run_time=1.8)

        mask = X_vals <= X_star
        upper = [
            ax.coords_to_point(x, f) for x, f in zip(X_vals[mask], F[mask], strict=True)
        ]
        lower = [
            ax.coords_to_point(x, v)
            for x, v in zip(X_vals[mask][::-1], npv[mask][::-1], strict=True)
        ]
        wait_region = Polygon(
            *upper, *lower, fill_color=C_OPTION, fill_opacity=0.18, stroke_width=0
        )
        wait_lab = Text("value of waiting", font_size=22, color=C_OPTION).move_to(
            ax.coords_to_point(X_star * 0.42, y_max * 0.34)
        )
        with self.voiceover(
            "The shaded gap between the curves is the value of waiting. It is"
            " everywhere positive below the trigger, and at low demand the"
            " option is worth several times the N P V."
        ):
            self.play(FadeIn(wait_region), FadeIn(wait_lab), run_time=1.5)

        trig_line = DashedLine(
            ax.coords_to_point(X_star, y_min),
            ax.coords_to_point(X_star, y_max),
            color=C_OPTION,
        )
        trig_lab = MathTex(
            r"X_H^* \approx 0.0028", font_size=30, color=C_OPTION
        ).next_to(trig_line, UP, buff=0.1)
        tangency = Dot(
            ax.coords_to_point(X_star, float(model.option_value_H(X_star))),
            color=C_OPTION,
        )
        with self.voiceover(
            "At the trigger, about zero point zero zero two eight with"
            " capacity zero point zero zero six seven, the curves meet"
            " tangentially: same value and same slope. That is value matching"
            " and smooth pasting, visible on screen."
        ):
            self.play(Create(trig_line), FadeIn(trig_lab), run_time=1.2)
            self.play(FadeIn(tangency, scale=2.5), run_time=0.8)
        with self.voiceover(
            "Past the trigger the firm invests immediately, so the option"
            " value coincides with the N P V. The rendered curve matches"
            " figure option-value in the paper."
        ):
            self.play(Indicate(tangency, color=C_OPTION), run_time=1.0)
        self.pause(0.5)
        self.clear_body()


class P2S10ProofSteps12(PaperScene):
    def construct(self):
        self.set_header("Proof of Proposition 1", kicker="STEPS 1-2")

        setup = MathTex(
            r"F(X_0) = \bigl(V(X^*,K,\phi) - I(K)\bigr)"
            r"\left(\frac{X_0}{X^*}\right)^{\beta_H}",
            font_size=36,
        )
        with self.voiceover(
            "Now the proof of Proposition one, step by step. The firm"
            " maximizes the option value over the trigger, the capacity, and"
            " the training fraction jointly."
        ):
            setup.to_edge(UP, buff=1.35)
            self.play(Write(setup), run_time=1.6)

        cav = Text(
            "uses F_L = C X^(beta_H) under (A3); exactness proved in Part 3",
            font_size=22,
            color=C_FAINT,
        ).next_to(setup, DOWN, buff=0.35)
        with self.voiceover(
            "One caveat up front: this form uses the simplified L-regime"
            " option value, C times X to the beta H, valid under assumption"
            " A three. Part three proves that simplification is exact."
        ):
            self.play(FadeIn(cav), run_time=0.8)

        s1a = MathTex(
            r"\text{VM:}\;\; A(X^*)^{\beta_H} = A_{\text{eff}}\,X^* - b(K)"
            r"\qquad\text{SP:}\;\; A\beta_H(X^*)^{\beta_H-1} = A_{\text{eff}}",
            font_size=32,
        )
        s1b = MathTex(
            r"X^*(K,\phi)",
            r"=",
            r"\frac{\beta_H}{\beta_H-1}\cdot"
            r"\frac{\delta K/r + cK^\gamma}{A_{\text{eff}}(\phi,K)}",
            font_size=38,
        )
        _stack(s1a, s1b, buff=0.5).next_to(cav, DOWN, buff=0.5)
        with self.voiceover(
            "Step one: the trigger given K and phi. Value matching and"
            " smooth pasting are word for word the H-regime argument, with A"
            " effective in place of A H times phi K to the alpha."
        ):
            self.play(Write(s1a), run_time=1.6)
        with self.voiceover(
            "Dividing the two conditions exactly as before gives the trigger:"
            " the option premium times total cost over A effective. With phi"
            " and K at their optima, this evaluates to about zero point zero"
            " zero four seven at baseline."
        ):
            self.play(Write(s1b), run_time=1.4)
            self.play(Create(highlight(s1b)), run_time=0.6)

        self.clear_body()
        s2a = MathTex(
            r"\text{Step 2: rearrange the trigger:}\quad"
            r" A_{\text{eff}}\,X^* = \frac{\beta_H}{\beta_H-1}\,b(K)",
            font_size=34,
        ).shift(UP * 1.5)
        s2b = MathTex(
            r"V - I",
            r"= A_{\text{eff}}\,X^* - b(K)",
            r"= \left(\frac{\beta_H}{\beta_H-1} - 1\right)b(K)",
            font_size=34,
        ).next_to(s2a, DOWN, buff=0.55)
        s2c = MathTex(
            r"\frac{\beta_H}{\beta_H-1} - 1"
            r" = \frac{\beta_H - (\beta_H - 1)}{\beta_H-1}"
            r" = \frac{1}{\beta_H-1}",
            font_size=34,
        ).next_to(s2b, DOWN, buff=0.5)
        s2d = MathTex(
            r"V - I = \frac{b(K)}{\beta_H-1}",
            font_size=38,
            color=C_OPTION,
        ).next_to(s2c, DOWN, buff=0.55)
        with self.voiceover(
            "Step two: the N P V at the trigger. Multiply the trigger"
            " equation through by A effective: revenue value at exercise is"
            " beta H over beta H minus one, times total cost."
        ):
            self.play(Write(s2a), run_time=1.5)
        with self.voiceover("Subtract the cost b of K to get the N P V at exercise."):
            self.play(Write(s2b), run_time=1.4)
        with self.voiceover(
            "The bracket simplifies: beta H minus beta H minus one is just"
            " one, over beta H minus one."
        ):
            self.play(Write(s2c), run_time=1.3)
        with self.voiceover(
            "So at the moment of investing, the surplus equals total cost"
            " divided by beta H minus one. At baseline, with b of K star"
            " about zero point zero zero two two, the N P V is about zero"
            " point zero zero four."
        ):
            self.play(Write(s2d), run_time=1.0)
            self.play(Create(highlight(s2d)), run_time=0.6)
        self.pause(0.5)
        self.clear_body()


class P2S11ProofStep3(PaperScene):
    def construct(self):
        self.set_header("Proof of Proposition 1", kicker="STEP 3")

        s3a = MathTex(
            r"F(X_0)",
            r"= (V-I)\left(\frac{X_0}{X^*}\right)^{\beta_H}",
            r"= \frac{b(K)}{\beta_H-1}\,X_0^{\beta_H}\,(X^*)^{-\beta_H}",
            font_size=36,
        )
        with self.voiceover(
            "Step three: substitute the trigger and the N P V back into the"
            " option value, to see what the firm is actually maximizing over"
            " K and phi."
        ):
            s3a.to_edge(UP, buff=1.4)
            self.play(Write(s3a), run_time=1.8)

        s3b = MathTex(
            r"(X^*)^{-\beta_H}"
            r" = \left(\frac{\beta_H}{\beta_H-1}\cdot"
            r"\frac{b(K)}{A_{\text{eff}}}\right)^{-\beta_H}"
            r" = \left(\frac{\beta_H-1}{\beta_H}\right)^{\beta_H}"
            r"\frac{A_{\text{eff}}^{\beta_H}}{b(K)^{\beta_H}}",
            font_size=34,
        ).next_to(s3a, DOWN, buff=0.55, aligned_edge=LEFT)
        with self.voiceover(
            "Raise the step-one trigger to the power minus beta H: the"
            " fraction flips, giving A effective to the beta H over b to the"
            " beta H."
        ):
            self.play(Write(s3b), run_time=1.8)

        s3c = MathTex(
            r"F(X_0)",
            r"= \frac{1}{\beta_H-1}"
            r"\left(\frac{(\beta_H-1)X_0}{\beta_H}\right)^{\beta_H}",
            r"\cdot\,\frac{A_{\text{eff}}^{\beta_H}}{b(K)^{\beta_H-1}}",
            font_size=36,
        ).next_to(s3b, DOWN, buff=0.55, aligned_edge=LEFT)
        s3c[2].set_color(C_OPTION)
        with self.voiceover(
            "Multiply the pieces. The single b of K upstairs meets b to the"
            " beta H downstairs, leaving beta H minus one powers of b in the"
            " denominator. The X naught and beta H factors collect into one"
            " constant."
        ):
            self.play(Write(s3c), run_time=1.8)

        s3d = MathTex(
            r"F(X_0) = \mathcal{C}\cdot h(K,\phi),\qquad"
            r" h = \frac{A_{\text{eff}}(\phi,K)^{\beta_H}}{b(K)^{\beta_H-1}},"
            r"\qquad \mathcal{C}"
            r" = \frac{1}{\beta_H-1}\left(\frac{(\beta_H-1)X_0}"
            r"{\beta_H}\right)^{\beta_H}",
            font_size=28,
        ).next_to(s3c, DOWN, buff=0.6)
        s3d.set_x(0)
        with self.voiceover(
            "So the option value factors as a constant script C, which"
            " depends only on X naught and beta H, times the objective h:"
            " A effective to the beta H, over cost to the beta H minus one."
        ):
            self.play(Write(s3d), run_time=1.8)
            self.play(Create(highlight(s3d)), run_time=0.7)

        with self.voiceover(
            "Everything the firm controls lives in h. Maximizing the option"
            " is now a static problem: trade revenue coefficient against"
            " cost, with exponents beta H and beta H minus one."
        ):
            self.play(Indicate(s3d, color=C_OPTION), run_time=1.2)
        self.pause(0.5)
        self.clear_body()


class P2S12ProofStep4(PaperScene):
    def construct(self):
        self.set_header("Proof of Proposition 1", kicker="STEP 4: OPTIMAL K")

        f1 = MathTex(
            r"\ln h = \beta_H\ln A_{\text{eff}} - (\beta_H-1)\ln b(K)",
            font_size=34,
        )
        f2 = MathTex(
            r"\frac{\partial \ln h}{\partial K} = 0:\qquad"
            r"\frac{\beta_H}{A_{\text{eff}}}"
            r"\frac{\partial A_{\text{eff}}}{\partial K}"
            r" = (\beta_H-1)\,\frac{b'(K)}{b(K)}",
            font_size=34,
        )
        f3 = MathTex(
            r"A_{\text{eff}} = g(\phi)\,K^\alpha"
            r"\;\Rightarrow\;"
            r"\frac{1}{A_{\text{eff}}}\frac{\partial A_{\text{eff}}}"
            r"{\partial K} = \frac{\alpha}{K}"
            r"\qquad\text{($g(\phi)$ cancels!)}",
            font_size=34,
        )
        f4 = MathTex(
            r"\frac{\alpha\beta_H}{K}"
            r" = \frac{(\beta_H-1)\bigl(c\gamma K^{\gamma-1}+\delta/r\bigr)}"
            r"{cK^\gamma + \delta K/r}",
            font_size=34,
        )
        _stack(f1, f2, f3, f4, buff=0.45).to_edge(UP, buff=1.35).shift(LEFT * 0.2)
        with self.voiceover(
            "Step four: the first-order condition for capacity. Take logs of"
            " h: beta H times log A effective, minus beta H minus one times"
            " log cost."
        ):
            self.play(Write(f1), run_time=1.4)
        with self.voiceover(
            "Differentiate in K and set to zero: the weighted growth rate of"
            " revenue must equal the weighted growth rate of cost."
        ):
            self.play(Write(f2), run_time=1.6)
        with self.voiceover(
            "Here is the key structural fact. A effective separates as g of"
            " phi times K to the alpha, because both terms scale with K to"
            " the alpha. Its log-derivative in K is alpha over K, and every"
            " trace of phi cancels."
        ):
            self.play(Write(f3), run_time=1.6)
            self.play(Indicate(f3, color=C_TRAIN), run_time=1.0)
        with self.voiceover(
            "The condition becomes alpha beta H over K on the left, and the"
            " cost side on the right, with b prime equal to c gamma K to the"
            " gamma minus one, plus delta over r."
        ):
            self.play(Write(f4), run_time=1.6)

        self.clear_body()
        g1 = MathTex(
            r"\alpha\beta_H\left(cK^\gamma + \frac{\delta K}{r}\right)"
            r" = (\beta_H-1)\left(c\gamma K^\gamma + \frac{\delta K}{r}\right)",
            font_size=34,
        ).shift(UP * 1.8)
        g2 = MathTex(
            r"cK^\gamma\bigl[\alpha\beta_H - \gamma(\beta_H-1)\bigr]"
            r" = \frac{\delta K}{r}\bigl[\beta_H - 1 - \alpha\beta_H\bigr]",
            font_size=34,
        ).next_to(g1, DOWN, buff=0.5)
        g3 = MathTex(
            r"cK^{\gamma-1}\bigl[\gamma(\beta_H-1) - \alpha\beta_H\bigr]"
            r" = \frac{\delta}{r}\bigl[\alpha\beta_H - \beta_H + 1\bigr]",
            font_size=34,
        ).next_to(g2, DOWN, buff=0.5)
        g4 = MathTex(
            r"K^* = \left[\frac{\delta\,(\alpha\beta_H-\beta_H+1)}"
            r"{r\,c\,\bigl(\gamma(\beta_H-1)-\alpha\beta_H\bigr)}\right]"
            r"^{\frac{1}{\gamma-1}}",
            font_size=38,
            color=C_OPTION,
        ).next_to(g3, DOWN, buff=0.55)
        with self.voiceover(
            "Cross-multiply by K times b of K. On the right, K times b prime"
            " gives c gamma K to the gamma, plus delta K over r."
        ):
            self.play(Write(g1), run_time=1.6)
        with self.voiceover(
            "Collect the K to the gamma terms on the left and the linear"
            " terms on the right."
        ):
            self.play(Write(g2), run_time=1.5)
        with self.voiceover(
            "Both brackets are negative under assumption A two, so flip the"
            " signs of both, and divide by K."
        ):
            self.play(Write(g3), run_time=1.5)
        with self.voiceover(
            "Solving for K gives the closed form in Proposition one: K star"
            " to the power one over gamma minus one of delta times alpha beta"
            " H minus beta H plus one, over r c times gamma beta H minus one,"
            " minus alpha beta H."
        ):
            self.play(Write(g4), run_time=1.6)
            self.play(Create(highlight(g4)), run_time=0.7)

        self.clear_body()
        a2 = MathTex(
            r"\text{(A2):}\quad \frac{1}{\gamma}"
            r" < \frac{\beta_H-1}{\alpha\beta_H} < 1",
            font_size=34,
        ).to_edge(UP, buff=1.15)
        a2a = MathTex(
            r"\frac{\beta_H-1}{\alpha\beta_H} < 1"
            r" \iff \alpha\beta_H - \beta_H + 1 > 0\quad\text{(numerator)}",
            font_size=32,
        ).next_to(a2, DOWN, buff=0.35)
        a2b = MathTex(
            r"\frac{1}{\gamma} < \frac{\beta_H-1}{\alpha\beta_H}"
            r" \iff \gamma(\beta_H-1) - \alpha\beta_H > 0\quad"
            r"\text{(denominator)}",
            font_size=32,
        ).next_to(a2a, DOWN, buff=0.35)
        num = MathTex(
            r"K^* = \left[\frac{0.03\times 0.0683}"
            r"{0.12\times 0.2081}\right]^{2} \approx 0.0067",
            font_size=34,
            color=C_OPTION,
        ).next_to(a2b, DOWN, buff=0.4)
        with self.voiceover(
            "Where is assumption A two needed? Exactly here, for the bracket"
            " signs. The right inequality of A two is equivalent to a"
            " positive numerator."
        ):
            self.play(Write(a2), run_time=1.2)
            self.play(Write(a2a), run_time=1.4)
        with self.voiceover(
            "And the left inequality is equivalent to a positive denominator."
            " Together they make K star positive and finite, which is the"
            " interior capacity solution."
        ):
            self.play(Write(a2b), run_time=1.4)
        with self.voiceover(
            "Plugging in the baseline numbers, with gamma minus one equal to"
            " one half so the outer exponent is two, gives K star of about"
            " zero point zero zero six seven, matching the paper's table."
        ):
            self.play(Write(num), run_time=1.4)

        indep = Text(
            "K* contains no phi and no lambda:\n"
            "g(phi) cancelled, and beta_H solves the H-regime equation only",
            font_size=24,
            color=C_TRAIN,
            line_spacing=1.1,
        ).next_to(num, DOWN, buff=0.4)
        with self.voiceover(
            "And note what is absent: K star contains no phi, because g of"
            " phi cancelled, and no lambda, because beta H solves the"
            " H-regime characteristic equation, which never sees the arrival"
            " rate. Scale is set by cost and technology; beliefs set the"
            " split and the timing."
        ):
            self.play(FadeIn(indep), run_time=1.2)
        self.pause(0.5)
        self.clear_body()


class P2S13CompStatics(PaperScene):
    def construct(self):
        self.set_header(
            "Comparative statics in regime H", kicker="FIG. comparative-statics"
        )

        from ai_lab_investment.models.base_model import SingleFirmModel
        from ai_lab_investment.models.parameters import ModelParameters

        model = SingleFirmModel(ModelParameters())
        sigmas = np.linspace(0.21, 0.33, 13)
        cs = model.comparative_statics("sigma", sigmas, "H")
        log_trig = np.log10(cs["triggers"])
        log_cap = np.log10(cs["capacities"])

        y_min = float(min(log_trig.min(), log_cap.min())) - 0.3
        y_max = float(max(log_trig.max(), log_cap.max())) + 0.3
        ax = clean_axes(
            x_range=[0.20, 0.34], y_range=[y_min, y_max], width=8.6, height=3.9
        ).shift(DOWN * 1.2 + LEFT * 0.4)
        x_lab = MathTex(r"\sigma", font_size=30, color=C_FAINT).next_to(
            ax.x_axis, RIGHT, buff=0.2
        )
        y_lab = Text("log10 scale", font_size=20, color=C_FAINT).next_to(
            ax.y_axis, UP, buff=0.15
        )

        with self.voiceover(
            "Last, the comparative statics behind the paper's four-panel"
            " figure. Here is the volatility panel recomputed live from the"
            " model's comparative statics routine, on a log scale."
        ):
            self.play(Create(ax), FadeIn(x_lab), FadeIn(y_lab), run_time=1.0)

        trig_line = ax.plot_line_graph(
            sigmas, log_trig, line_color=C_OPTION, add_vertex_dots=False
        )
        cap_line = ax.plot_line_graph(
            sigmas, log_cap, line_color=C_COST, add_vertex_dots=False
        )
        trig_lab = MathTex(r"X_H^*", font_size=30, color=C_OPTION).next_to(
            ax.coords_to_point(0.33, log_trig[-1]), RIGHT, buff=0.2
        )
        cap_lab = MathTex(r"K_H^*", font_size=30, color=C_COST).next_to(
            ax.coords_to_point(0.33, log_cap[-1]), RIGHT, buff=0.2
        )
        with self.voiceover(
            "Higher sigma raises the trigger: more uncertainty makes waiting"
            " more valuable, so the option premium grows."
        ):
            self.play(Create(trig_line), FadeIn(trig_lab), run_time=1.6)
        with self.voiceover(
            "And it raises capacity too: when the firm finally does invest,"
            " it invests at a higher demand level and builds bigger. Both"
            " curves climb steeply, which is why the panel needs a log scale."
        ):
            self.play(Create(cap_line), FadeIn(cap_lab), run_time=1.6)

        self.clear_body()
        rows = VGroup(
            Text(
                "alpha up   ->  trigger up, capacity up (less diminishing returns)",
                font_size=26,
                color=C_TEXT,
            ),
            Text(
                "gamma up   ->  trigger non-monotone, capacity down (convex costs)",
                font_size=26,
                color=C_TEXT,
            ),
            Text(
                "delta up   ->  trigger up, capacity up (via the K* formula)",
                font_size=26,
                color=C_TEXT,
            ),
        ).arrange(DOWN, buff=0.45, aligned_edge=LEFT)
        rows.shift(DOWN * 0.2)
        with self.voiceover(
            "The other three panels read straight off the closed forms."
            " Higher alpha raises both trigger and capacity: marginal"
            " capacity is worth more."
        ):
            self.play(FadeIn(rows[0], shift=RIGHT * 0.3), run_time=1.0)
        with self.voiceover(
            "Higher gamma sharply cuts capacity through the one over gamma"
            " minus one exponent, while the trigger moves non-monotonically."
        ):
            self.play(FadeIn(rows[1], shift=RIGHT * 0.3), run_time=1.0)
        with self.voiceover(
            "And higher delta raises both: the linear cost floor is what"
            " creates the interior optimum in the first place, and shifting"
            " it favors larger scale. All four panels match figure"
            " comparative-statics in the paper."
        ):
            self.play(FadeIn(rows[2], shift=RIGHT * 0.3), run_time=1.0)
        self.pause(0.5)
        self.clear_body()


class P2S14Next(PaperScene):
    def construct(self):
        self.set_header("Where we are", kicker="NEXT")

        done = VGroup(
            Text("done: V_H, V_L, A_eff derived in full", font_size=28, color=C_H),
            Text(
                "done: H-regime option, trigger, option premium",
                font_size=28,
                color=C_H,
            ),
            Text(
                "done: Proposition 1, Steps 1-4: closed-form K*",
                font_size=28,
                color=C_H,
            ),
        ).arrange(DOWN, buff=0.35, aligned_edge=LEFT)
        done.shift(UP * 0.9)
        with self.voiceover(
            "That closes the first half of the single-firm benchmark: both"
            " installed values from first principles, the H-regime option"
            " and trigger, and the closed-form capacity from steps one to"
            " four of the proof."
        ):
            self.play(FadeIn(done, shift=RIGHT * 0.3), run_time=1.5)

        nxt = VGroup(
            Text("Part 3: the L-regime option value ODE", font_size=28, color=C_OPTION),
            Text(
                "exactness of A_1 = 0 under (A3)  (Step 5b)",
                font_size=28,
                color=C_OPTION,
            ),
            Text(
                "interior phi* and its comparative statics  (Steps 5-6)",
                font_size=28,
                color=C_OPTION,
            ),
        ).arrange(DOWN, buff=0.35, aligned_edge=LEFT)
        nxt.next_to(done, DOWN, buff=0.8, aligned_edge=LEFT)
        with self.voiceover(
            "Part three takes on the harder half: the L-regime option value,"
            " which solves an O D E with a regime-switching forcing term."
        ):
            self.play(FadeIn(nxt[0], shift=RIGHT * 0.3), run_time=1.0)
        with self.voiceover(
            "There we prove that the homogeneous coefficient A one is exactly"
            " zero under assumption A three, which justifies the simplified"
            " option value used today."
        ):
            self.play(FadeIn(nxt[1], shift=RIGHT * 0.3), run_time=1.0)
        with self.voiceover(
            "And we derive the interior training fraction phi star, about"
            " seventy percent at baseline, with its comparative statics in"
            " lambda and mu H. See you there."
        ):
            self.play(FadeIn(nxt[2], shift=RIGHT * 0.3), run_time=1.0)
        self.pause(0.8)
        self.clear_body()
        self.play(FadeOut(self.header), run_time=0.6)
        self.header = None
