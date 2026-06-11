"""Short explainer video (~12-15 min): paper overview at conference depth.

Render: just render-explainer
Draft a single scene: cd video && uv run manim render -ql explainer.py E01Hook
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
    Indicate,
    LaggedStart,
    Line,
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
)

SCENES = [
    "E01Hook",
    "E02Problem",
    "E03Demand",
    "E04Technology",
    "E05OptionValue",
    "E06TrainingFraction",
    "E07Duopoly",
    "E08FaithBasedSurvival",
    "E09Archetypes",
    "E10DariosDilemma",
    "E11Takeaways",
]


class E01Hook(PaperScene):
    def construct(self):
        big = Text("$660,000,000,000", font_size=72, color=C_DEMAND, weight="BOLD")
        with self.voiceover(
            "Six hundred and sixty billion dollars. That is roughly what the"
            " leading AI laboratories and their compute partners are projected"
            " to spend on infrastructure in twenty twenty-six alone."
        ):
            self.play(Write(big), run_time=2.5)

        sub = Text("projected AI capex, 2026", font_size=28, color=C_FAINT).next_to(
            big, DOWN, buff=0.4
        )
        with self.voiceover(
            "Data centers, GPU clusters, power plants. Almost all of it is"
            " irreversible: once the capital is committed, there is no taking"
            " it back."
        ):
            self.play(FadeIn(sub), run_time=1.0)

        quote = Text(
            '"I could buy $1 trillion of compute that starts at the end of 2027.\n'
            "If my revenue is not $1 trillion... there's no force on Earth,\n"
            "there's no hedge on Earth that could stop me from going bankrupt.\"",
            font_size=26,
            color=C_TEXT,
            line_spacing=1.1,
        ).move_to(UP * 0.5)
        attrib = Text(
            "— Dario Amodei, CEO of Anthropic", font_size=24, color=C_FAINT
        ).next_to(quote, DOWN, buff=0.5)
        with self.voiceover(
            "And the people writing the checks know exactly what is at stake."
            " Here is Dario Amodei, the CEO of Anthropic."
        ):
            self.play(FadeOut(big), FadeOut(sub), run_time=0.8)
            self.play(FadeIn(quote), run_time=1.5)
            self.play(FadeIn(attrib), run_time=0.8)
        self.pause(1.0)

        title = Text(
            "Investing in Artificial General Intelligence",
            font_size=44,
            weight="BOLD",
        )
        author = Text(
            "Vincent Grégoire — HEC Montréal", font_size=26, color=C_FAINT
        ).next_to(title, DOWN, buff=0.4)
        with self.voiceover(
            "This is a video about a paper that turns that dilemma into"
            " mathematics: a model of how an AI lab should time, size, and"
            " allocate an irreversible bet on artificial general intelligence."
        ):
            self.play(FadeOut(quote), FadeOut(attrib), run_time=0.8)
            self.play(Write(title), run_time=2.0)
            self.play(FadeIn(author), run_time=0.8)
        self.pause(0.8)
        self.play(FadeOut(title), FadeOut(author), run_time=0.7)


class E02Problem(PaperScene):
    def construct(self):
        self.set_header("Three decisions, one bet", kicker="THE PROBLEM")

        q1 = Text("When to invest?", font_size=34, color=C_OPTION)
        q2 = Text("How much capacity?", font_size=34, color=C_COST)
        q3 = Text("Training or inference?", font_size=34, color=C_TRAIN)
        qs = VGroup(q1, q2, q3).arrange(DOWN, buff=0.7, aligned_edge=LEFT)
        qs.shift(LEFT * 3 + DOWN * 0.3)

        s1 = MathTex(r"X^*", font_size=44, color=C_OPTION).next_to(q1, RIGHT, buff=1.0)
        s2 = MathTex(r"K", font_size=44, color=C_COST).next_to(q2, RIGHT, buff=1.0)
        s3 = MathTex(r"\phi", font_size=44, color=C_TRAIN).next_to(q3, RIGHT, buff=1.0)

        with self.voiceover(
            "A frontier AI lab faces three intertwined decisions. First, when"
            " to pull the trigger on a massive, irreversible build-out."
        ):
            self.play(FadeIn(q1), Write(s1), run_time=1.2)
        with self.voiceover(
            "Second, how much compute capacity to install, knowing that"
            " marginal costs rise steeply with scale."
        ):
            self.play(FadeIn(q2), Write(s2), run_time=1.2)
        with self.voiceover(
            "And third, the decision this paper puts at center stage: what"
            " fraction phi of that capacity to devote to training new models,"
            " versus running inference for paying customers."
        ):
            self.play(FadeIn(q3), Write(s3), run_time=1.2)

        self.pause(0.3)
        tension = Text(
            "Training builds the future.  Inference pays for the present.",
            font_size=30,
            color=C_TEXT,
        ).to_edge(DOWN, buff=0.9)
        with self.voiceover(
            "The tension is brutal. Training builds the capability you need if"
            " transformative AI arrives. Inference generates the revenue you"
            " need to survive until it does. And both consume the same scarce"
            " GPUs."
        ):
            self.play(FadeIn(tension), run_time=1.5)
        self.pause(0.5)
        self.clear_body()


class E03Demand(PaperScene):
    def construct(self):
        self.set_header("Regime-switching demand", kicker="THE MODEL")

        gbm = MathTex(
            r"dX_t = \mu_s X_t\,dt + \sigma X_t\,dW_t,",
            r"\quad s \in \{L, H\}",
            font_size=40,
        ).to_edge(UP, buff=1.4)
        with self.voiceover(
            "Everything is driven by one stochastic process: the demand for"
            " AI compute, X. It follows a geometric Brownian motion whose"
            " drift depends on the regime the economy is in."
        ):
            self.play(Write(gbm), run_time=2.0)

        ax = clean_axes(x_range=[0, 12], y_range=[0, 4.2], width=9.5, height=4.0).shift(
            DOWN * 1.1
        )

        p = BASELINE
        rng = np.random.default_rng(11)
        t_switch = 7.0
        dt = 0.01
        t = np.arange(0, 12 + dt, dt)
        x = np.zeros_like(t)
        x[0] = 1.0
        for i in range(1, len(t)):
            mu = p["mu_L"] if t[i] < t_switch else p["mu_H"] + 0.10
            sig = 0.18
            x[i] = x[i - 1] * np.exp(
                (mu - 0.5 * sig**2) * dt + sig * np.sqrt(dt) * rng.normal()
            )
        mask_L = t <= t_switch
        line_L = ax.plot_line_graph(
            t[mask_L], x[mask_L], line_color=C_L, add_vertex_dots=False
        )
        line_H = ax.plot_line_graph(
            t[~mask_L], x[~mask_L], line_color=C_H, add_vertex_dots=False
        )

        lab_L = MathTex(r"\mu_L", font_size=36, color=C_L).move_to(
            ax.coords_to_point(3.2, 1.9)
        )
        with self.voiceover(
            "The economy starts in the low regime: today's world, where AI"
            " demand grows at a moderate rate mu L."
        ):
            self.play(Create(ax), run_time=1.0)
            self.play(Create(line_L), FadeIn(lab_L), run_time=2.2)

        flash = DashedLine(
            ax.coords_to_point(t_switch, 0),
            ax.coords_to_point(t_switch, 4.0),
            color=C_DEMAND,
        )
        agi = Text("AGI arrives", font_size=26, color=C_DEMAND).next_to(
            flash, UP, buff=0.1
        )
        with self.voiceover(
            "At some random time, a breakthrough arrives: a step change in AI"
            " capability that permanently shifts demand to a higher growth"
            " trajectory. That is the switch to the high regime."
        ):
            self.play(Create(flash), FadeIn(agi), run_time=1.2)

        lab_H = MathTex(r"\mu_H > \mu_L", font_size=36, color=C_H).move_to(
            ax.coords_to_point(10.2, 3.4)
        )
        with self.voiceover(
            "After the switch, growth is faster, and the switch is absorbing:"
            " capabilities, once demonstrated, do not disappear."
        ):
            self.play(Create(line_H), FadeIn(lab_H), run_time=2.0)

        pois = MathTex(
            r"\Pr(\text{switch in } dt) = \lambda\, dt", font_size=36, color=C_DEMAND
        ).to_edge(DOWN, buff=0.4)
        with self.voiceover(
            "The arrival is a Poisson event with rate lambda. Lambda is the"
            " single most important parameter in this model: it encodes a"
            " firm's beliefs about AI timelines."
        ):
            self.play(Write(pois), run_time=1.5)

        with self.voiceover(
            "At the baseline value of zero point one, the expected waiting"
            " time is ten years. Sam Altman, Dario Amodei, and Yann LeCun"
            " plainly disagree about this number, and that disagreement is"
            " exactly what the model exploits."
        ):
            self.play(Indicate(pois, color=C_DEMAND), run_time=1.5)
        self.pause(0.5)
        self.clear_body()


class E04Technology(PaperScene):
    def construct(self):
        self.set_header("One stock of GPUs, two uses", kicker="THE MODEL")

        cost = MathTex(
            r"I(K) = c\,K^{\gamma},\quad \gamma > 1", font_size=40, color=C_COST
        ).to_edge(UP, buff=1.4)
        with self.voiceover(
            "Installing capacity K costs c times K to the power gamma, with"
            " gamma greater than one: power constraints, GPU supply"
            " bottlenecks, and construction make marginal costs rise with"
            " scale. And once built, the capacity is sunk."
        ):
            self.play(Write(cost), run_time=1.8)

        bar_h, bar_w = 3.4, 1.5
        phi = 0.7
        infer = Rectangle(
            width=bar_w,
            height=bar_h * (1 - phi),
            fill_color=C_INFER,
            fill_opacity=0.85,
            stroke_color=C_TEXT,
        )
        train = Rectangle(
            width=bar_w,
            height=bar_h * phi,
            fill_color=C_TRAIN,
            fill_opacity=0.85,
            stroke_color=C_TEXT,
        )
        VGroup(train, infer).arrange(DOWN, buff=0).shift(LEFT * 4 + DOWN * 0.8)
        lab_train = MathTex(r"\phi K", font_size=38, color=C_TRAIN).next_to(
            train, LEFT, buff=0.3
        )
        lab_infer = MathTex(r"(1-\phi)K", font_size=38, color=C_INFER).next_to(
            infer, LEFT, buff=0.3
        )
        t_train = Text("training", font_size=26, color=C_TRAIN).next_to(
            train, RIGHT, buff=0.3
        )
        t_infer = Text("inference", font_size=26, color=C_INFER).next_to(
            infer, RIGHT, buff=0.3
        )

        with self.voiceover(
            "The firm splits its capacity. A fraction phi goes to training,"
            " shown in purple; the rest serves inference, in blue. This split"
            " is chosen at investment time."
        ):
            self.play(
                LaggedStart(
                    GrowFromEdge(infer, DOWN), GrowFromEdge(train, DOWN), lag_ratio=0.4
                ),
                run_time=1.6,
            )
            self.play(
                FadeIn(lab_train),
                FadeIn(lab_infer),
                FadeIn(t_train),
                FadeIn(t_infer),
                run_time=1.2,
            )

        rev_L = MathTex(
            r"\pi^L = X \cdot \left[(1-\phi)K\right]^{\alpha}",
            font_size=40,
        ).shift(RIGHT * 2.4 + UP * 0.1)
        rev_L[0][0:2].set_color(C_L)
        rev_H = MathTex(
            r"\pi^H = X \cdot (\phi K)^{\alpha}",
            font_size=40,
        ).next_to(rev_L, DOWN, buff=0.8, aligned_edge=LEFT)
        rev_H[0][0:2].set_color(C_H)

        with self.voiceover(
            "Revenue depends on the regime. Before the breakthrough, in the"
            " low regime, revenue comes from inference: you earn by serving"
            " today's demand."
        ):
            self.play(Write(rev_L), run_time=1.5)
        with self.voiceover(
            "After the breakthrough, revenue depends on training quality: in"
            " a post AGI world, the best models capture the market. A firm"
            " that never trained earns nothing there."
        ):
            self.play(Write(rev_H), run_time=1.5)

        alpha_note = MathTex(
            r"\alpha = 0.4:\ \text{doubling compute} \Rightarrow"
            r" \text{only } 2^{0.4} \approx 1.32\times\ \text{revenue}",
            font_size=32,
            color=C_FAINT,
        ).to_edge(DOWN, buff=0.5)
        with self.voiceover(
            "The exponent alpha, calibrated to AI scaling laws, is about zero"
            " point four. Doubling compute raises revenue by only about"
            " thirty-two percent: capability scales as a power law, with"
            " sharply diminishing returns."
        ):
            self.play(Write(alpha_note), run_time=1.5)
        self.pause(0.5)
        self.clear_body()


class E05OptionValue(PaperScene):
    def construct(self):
        self.set_header("Waiting has value", kicker="SINGLE FIRM")

        a_eff = MathTex(
            r"A_{\text{eff}}",
            r"=",
            r"\underbrace{\frac{[(1-\phi)K]^{\alpha}}{r-\mu_L+\lambda}}"
            r"_{\text{inference today}}",
            r"+",
            r"\underbrace{\frac{\lambda}{r-\mu_L+\lambda}\cdot"
            r"\frac{(\phi K)^{\alpha}}{r-\mu_H}}_{\text{AGI prize}}",
            font_size=38,
        ).to_edge(UP, buff=1.2)
        a_eff[2].set_color(C_INFER)
        a_eff[4].set_color(C_H)
        a_eff[0].set_color(C_TEXT)

        with self.voiceover(
            "Putting demand and technology together, the value of an"
            " installed firm is one number, A effective, times demand."
        ):
            self.play(Write(a_eff[0:2]), run_time=1.0)
        with self.voiceover(
            "A effective has two parts. The first capitalizes inference"
            " revenue earned while the economy stays in the low regime."
        ):
            self.play(Write(a_eff[2]), run_time=1.5)
        with self.voiceover(
            "The second is the AGI prize: the post-breakthrough training"
            " payoff, weighted by the probability rate lambda of getting"
            " there. Every result in this paper flows through this object."
        ):
            self.play(Write(a_eff[3:]), run_time=1.5)
        self.pause(0.4)

        from ai_lab_investment.models.base_model import SingleFirmModel
        from ai_lab_investment.models.parameters import ModelParameters

        model = SingleFirmModel(ModelParameters())
        X_star, K_star = model.optimal_trigger_and_capacity("H")
        X_vals = np.linspace(0.001 * X_star, 2.2 * X_star, 160)
        F = np.array([model.option_value_H(x) for x in X_vals])
        npv = np.array([
            model.installed_value(x, K_star, "H") - model.investment_cost(K_star)
            for x in X_vals
        ])

        y_max = float(F.max()) * 1.1
        y_min = float(npv.min()) * 1.1
        ax = clean_axes(
            x_range=[0, X_vals[-1]], y_range=[y_min, y_max], width=9.0, height=4.2
        ).shift(DOWN * 1.3)
        x_lab = MathTex(r"X", font_size=30, color=C_FAINT).next_to(
            ax.x_axis, RIGHT, buff=0.2
        )

        npv_line = ax.plot_line_graph(
            X_vals, npv, line_color=C_FAINT, add_vertex_dots=False
        )
        f_line = ax.plot_line_graph(
            X_vals, F, line_color=C_OPTION, add_vertex_dots=False
        )
        npv_lab = Text("NPV of investing now", font_size=24, color=C_FAINT).move_to(
            ax.coords_to_point(X_vals[-1] * 0.62, y_min * 0.75)
        )
        f_lab = Text("option value F(X)", font_size=24, color=C_OPTION).move_to(
            ax.coords_to_point(X_vals[-1] * 0.35, y_max * 0.55)
        )

        with self.voiceover(
            "Now, when should the firm invest? The dashed gray curve is the"
            " net present value of investing immediately, as a function of"
            " demand."
        ):
            self.play(Create(ax), FadeIn(x_lab), run_time=0.8)
            self.play(Create(npv_line), FadeIn(npv_lab), run_time=1.6)
        with self.voiceover(
            "The gold curve is the value of the investment option, computed"
            " from the model. It lies everywhere above the NPV: because the"
            " investment is irreversible and demand is volatile, waiting for"
            " more information has value."
        ):
            self.play(Create(f_line), FadeIn(f_lab), run_time=1.8)

        trig = DashedLine(
            ax.coords_to_point(X_star, y_min),
            ax.coords_to_point(X_star, y_max),
            color=C_OPTION,
        )
        trig_lab = MathTex(r"X^*", font_size=36, color=C_OPTION).next_to(
            trig, UP, buff=0.1
        )
        with self.voiceover(
            "The firm invests only when demand reaches the trigger X star,"
            " where the two curves meet tangentially."
        ):
            self.play(Create(trig), FadeIn(trig_lab), run_time=1.2)

        trigger_eq = MathTex(
            r"X^* = \underbrace{\frac{\beta_H}{\beta_H - 1}}_{\approx\,2.8}"
            r"\cdot \frac{\delta K/r + cK^{\gamma}}{A_{\text{eff}}}",
            font_size=36,
        ).move_to(a_eff)
        with self.voiceover(
            "And the trigger has a closed form: total costs over A effective,"
            " scaled up by an option premium. At baseline, that premium means"
            " the firm waits for demand nearly three times the break-even"
            " level. Optimism enters through A effective: a higher lambda"
            " raises it, and pulls the trigger down."
        ):
            self.play(FadeOut(a_eff), run_time=0.5)
            self.play(Write(trigger_eq), run_time=2.0)
        self.pause(0.5)
        self.clear_body()


class E06TrainingFraction(PaperScene):
    def construct(self):
        self.set_header("Beliefs pin the split", kicker="RESULT 1")

        foc = MathTex(
            r"\left(\frac{\phi^*}{1-\phi^*}\right)^{1-\alpha}",
            r"=",
            r"\frac{\lambda}{r - \mu_H}",
            font_size=44,
        ).to_edge(UP, buff=1.3)
        foc[0].set_color(C_TRAIN)
        foc[2].set_color(C_DEMAND)

        with self.voiceover(
            "Proposition one. Maximizing A effective over phi gives a"
            " first-order condition with a remarkably clean form: the odds"
            " ratio of training, raised to one minus alpha, equals lambda"
            " over r minus mu H."
        ):
            self.play(Write(foc), run_time=2.0)

        with self.voiceover(
            "Everything about the optimal split is in that ratio. Beliefs"
            " about AI timelines, the post AGI growth rate, and the discount"
            " rate. Capacity K cancels out entirely, and so does the"
            " low-regime growth rate."
        ):
            self.play(Indicate(foc[2], color=C_DEMAND), run_time=1.5)

        alpha, r, mu_H = BASELINE["alpha"], BASELINE["r"], BASELINE["mu_H"]

        def phi_star(lam: float) -> float:
            ratio = (lam / (r - mu_H)) ** (1 / (1 - alpha))
            return ratio / (1 + ratio)

        lams = np.linspace(0.01, 0.5, 120)
        phis = np.array([phi_star(la) for la in lams])
        ax = clean_axes(x_range=[0, 0.5], y_range=[0, 1], width=8.5, height=3.8).shift(
            DOWN * 1.4
        )
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
            "Plotting the optimal training fraction against lambda: more"
            " optimistic firms allocate more of their compute to training."
        ):
            self.play(Create(ax), FadeIn(x_lab), FadeIn(y_lab), run_time=1.0)
            self.play(Create(curve), run_time=1.8)

        lam0 = BASELINE["lambda"]
        dot = Dot(ax.coords_to_point(lam0, phi_star(lam0)), color=C_DEMAND)
        note = (
            MathTex(
                r"\lambda = 0.10 \;\Rightarrow\; \phi^* \approx 0.70",
                font_size=36,
            )
            .next_to(dot, DOWN, buff=0.4)
            .shift(RIGHT * 1.6)
        )
        with self.voiceover(
            "At the baseline belief, an expected ten years to AGI, the firm"
            " optimally devotes seventy percent of its capacity to training."
            " Sacrificing most of today's revenue for tomorrow's prize is not"
            " recklessness; it is the optimum."
        ):
            self.play(FadeIn(dot, scale=2), Write(note), run_time=1.5)
        self.pause(0.5)
        self.clear_body()


class E07Duopoly(PaperScene):
    def construct(self):
        self.set_header("Competition compresses timing", kicker="RESULT 2")

        contest = MathTex(
            r"\pi_i^L = X\cdot\frac{[(1-\phi_i)K_i]^{2\alpha}}"
            r"{[(1-\phi_i)K_i]^{\alpha} + [(1-\phi_j)K_j]^{\alpha}}",
            font_size=38,
        ).to_edge(UP, buff=1.3)
        with self.voiceover(
            "Frontier AI is not a monopoly; it is a race between a handful of"
            " labs. The paper models two firms whose revenues are shares of a"
            " contest: what matters is relative capacity. Inference capacity"
            " decides market share today; training quality decides it after"
            " AGI."
        ):
            self.play(Write(contest), run_time=2.2)

        nl = Line(LEFT * 5, RIGHT * 5, color=C_FAINT).shift(DOWN * 0.6)
        x_mono = 3.5
        x_p = -2.5
        tick_m = Line(UP * 0.15, DOWN * 0.15, color=C_TEXT).move_to(
            nl.get_center() + RIGHT * x_mono
        )
        tick_p = Line(UP * 0.15, DOWN * 0.15, color=C_OPTION).move_to(
            nl.get_center() + RIGHT * x_p
        )
        lab_m = (
            VGroup(
                MathTex(r"X^{\text{mono}}", font_size=34, color=C_TEXT),
                Text("monopolist waits", font_size=22, color=C_FAINT),
            )
            .arrange(DOWN, buff=0.15)
            .next_to(tick_m, DOWN, buff=0.25)
        )
        lab_p = (
            VGroup(
                MathTex(r"X_P", font_size=34, color=C_OPTION),
                Text("leader preempts", font_size=22, color=C_FAINT),
            )
            .arrange(DOWN, buff=0.15)
            .next_to(tick_p, DOWN, buff=0.25)
        )

        with self.voiceover(
            "A monopolist would wait for the comfortable trigger we just derived."
        ):
            self.play(Create(nl), run_time=0.8)
            self.play(Create(tick_m), FadeIn(lab_m), run_time=1.0)
        arrow = (
            MathTex(r"\;\approx 43\%\ \text{lower}\;", font_size=34, color=C_OPTION)
            .next_to(nl, UP, buff=0.5)
            .shift(LEFT * 0)
        )
        with self.voiceover(
            "But under the threat of being preempted, each firm shaves its"
            " trigger to stay ahead, until the rents from leading are fully"
            " dissipated. In equilibrium the leader invests at a trigger"
            " roughly forty-three percent below the monopoly benchmark."
        ):
            self.play(Create(tick_p), FadeIn(lab_p), run_time=1.2)
            self.play(Write(arrow), run_time=1.0)

        inv = MathTex(
            r"\phi_L^* \;=\; \phi_F^* \;=\; \phi^{*}_{\text{mono}}",
            font_size=42,
            color=C_TRAIN,
        ).to_edge(DOWN, buff=0.8)
        with self.voiceover(
            "But here is the striking part, proposition three: competition"
            " changes when firms invest, yet it does not change the"
            " training-inference split at all. Leader, follower, and"
            " monopolist all choose exactly the same phi."
        ):
            self.play(Write(inv), run_time=1.8)
        with self.voiceover(
            "The reason is a clean cancellation: when both firms choose the"
            " same split, their relative capacities are identical in both"
            " regimes, so the contest terms drop out of the allocation"
            " condition. Training intensity reveals a lab's beliefs about"
            " timelines, not its competitive position. That is a sharp,"
            " testable prediction."
        ):
            self.play(Indicate(inv, color=C_TRAIN), run_time=1.5)
        self.pause(0.5)
        self.clear_body()


class E08FaithBasedSurvival(PaperScene):
    def construct(self):
        self.set_header("Faith-based survival", kicker="RESULT 3")

        xd = MathTex(
            r"X_D",
            r"=",
            r"\frac{\beta^-}{\beta^- - 1}",
            r"\cdot\frac{c_D/r + \delta K/r}{A_{\text{eff}}}",
            font_size=44,
        ).to_edge(UP, buff=1.3)
        xd[0].set_color(C_DEFAULT)

        with self.voiceover(
            "Now add debt. Following Leland, equity holders walk away when"
            " demand falls to an endogenous default boundary, X D: coupon and"
            " operating obligations on top, and A effective on the bottom."
        ):
            self.play(Write(xd), run_time=2.0)

        with self.voiceover(
            "And that denominator is the punchline. Training raises the AGI"
            " component of A effective. A higher A effective pushes the"
            " default boundary down. Belief in AGI, backed by training"
            " compute, literally keeps the firm alive longer."
        ):
            self.play(Indicate(xd[3], color=C_H), run_time=1.5)

        thresh = MathTex(
            r"\frac{\partial X_D}{\partial \lambda} < 0"
            r"\iff \phi > \tilde{\phi} \approx 0.32",
            font_size=40,
        ).shift(UP * 0.1)
        with self.voiceover(
            "This is not automatic: diverting compute to training also"
            " sacrifices the inference cash flow that services the debt. The"
            " paper derives the exact threshold: optimism lowers the default"
            " boundary only when the training fraction exceeds about a third."
            " The optimal seventy percent clears it comfortably."
        ):
            self.play(Write(thresh), run_time=1.8)

        cred = (
            VGroup(
                Text(
                    "fewer defaults: continuation value floors equity",
                    font_size=28,
                    color=C_H,
                ),
                Text(
                    "but creditors recover less: faith dies in bankruptcy",
                    font_size=28,
                    color=C_DEFAULT,
                ),
            )
            .arrange(DOWN, buff=0.35)
            .to_edge(DOWN, buff=0.8)
        )
        with self.voiceover(
            "For credit markets this cuts both ways. Training lowers the"
            " probability of default, but the hoped-for AGI payoff is"
            " worthless to creditors in bankruptcy: only the inference"
            " business can be liquidated. Training-heavy labs should default"
            " less often, but recover less when they do."
        ):
            self.play(FadeIn(cred[0]), run_time=1.0)
            self.play(FadeIn(cred[1]), run_time=1.0)
        self.pause(0.5)
        self.clear_body()


class E09Archetypes(PaperScene):
    def construct(self):
        self.set_header("Who believes what", kicker="CALIBRATION")

        names = ["Google-like", "Anthropic-like", "OpenAI-like", "xAI-like"]
        phis = [0.35, 0.55, 0.60, 0.75]
        colors = [C_INFER, C_TEXT, C_OPTION, C_TRAIN]
        bar_w, bar_h = 1.1, 3.0
        cols = VGroup()
        for name, ph, col in zip(names, phis, colors, strict=True):
            frame = Rectangle(
                width=bar_w, height=bar_h, stroke_color=C_FAINT, stroke_width=2
            )
            fill = Rectangle(
                width=bar_w,
                height=bar_h * ph,
                fill_color=C_TRAIN,
                fill_opacity=0.85,
                stroke_width=0,
            ).align_to(frame, DOWN)
            val = MathTex(rf"\hat\phi = {ph:.2f}", font_size=28, color=col).next_to(
                frame, UP, buff=0.18
            )
            lab = Text(name, font_size=22, color=col).next_to(frame, DOWN, buff=0.18)
            cols.add(VGroup(frame, fill, val, lab))
        cols.arrange(RIGHT, buff=1.0, aligned_edge=DOWN).shift(DOWN * 0.5)

        with self.voiceover(
            "Do real labs behave like the model says? The paper builds four"
            " stylized archetypes from public data, and their estimated"
            " training fractions span a factor of two."
        ):
            self.play(FadeIn(cols[0]), FadeIn(cols[1]), run_time=1.2)
            self.play(FadeIn(cols[2]), FadeIn(cols[3]), run_time=1.2)

        with self.voiceover(
            "A hyperscaler that must serve billions of users keeps training"
            " near thirty-five percent. A compute racer building giant"
            " clusters before monetizing pushes it to seventy-five percent,"
            " while spending twenty times its revenue on capex."
        ):
            self.play(
                Indicate(cols[0][3], color=C_INFER),
                run_time=1.2,
            )
            self.play(Indicate(cols[3][3], color=C_TRAIN), run_time=1.2)

        inv = MathTex(
            r"\lambda = \left(\tfrac{\hat\phi}{1-\hat\phi}\right)^{1-\alpha}"
            r"(r - \mu_H)",
            font_size=38,
            color=C_DEMAND,
        ).to_edge(DOWN, buff=0.55)
        with self.voiceover(
            "Because the optimal split is pinned by beliefs, you can run the"
            " formula backwards: each observed training fraction implies a"
            " belief about AI timelines. The compute racer is investing as if"
            " AGI were six to eleven years away; the hyperscaler, as if it"
            " were twenty to thirty years out. The capital commitments we"
            " observe are consistent with genuinely optimistic beliefs."
        ):
            self.play(Write(inv), run_time=1.8)
        self.pause(0.5)
        self.clear_body()


class E10DariosDilemma(PaperScene):
    def construct(self):
        self.set_header("Dario's dilemma", kicker="RESULT 4")

        setup = MathTex(
            r"\Delta V = \text{NPV}(\lambda_{\text{true}}, \lambda_{\text{true}})"
            r" - \text{NPV}(\lambda_{\text{true}}, \lambda_{\text{invest}})",
            font_size=38,
        ).to_edge(UP, buff=1.3)
        with self.voiceover(
            "Finally: what does it cost to be wrong about AGI timing? Suppose"
            " the truth is lambda equals zero point one, but the firm invests"
            " as if it believed something else: a different trigger, a"
            " different scale, and crucially a different training fraction."
        ):
            self.play(Write(setup), run_time=2.0)

        ax = clean_axes(
            x_range=[0.0, 0.52], y_range=[0, 30], width=8.6, height=3.6
        ).shift(DOWN * 1.2)
        x_lab = MathTex(
            r"\lambda_{\text{invest}}", font_size=30, color=C_FAINT
        ).next_to(ax.x_axis, RIGHT, buff=0.15)
        y_lab = Text("value lost (%)", font_size=22, color=C_FAINT).next_to(
            ax.y_axis, UP, buff=0.15
        )

        from ai_lab_investment.models.parameters import ModelParameters
        from ai_lab_investment.models.valuation import ValuationAnalysis

        va = ValuationAnalysis(ModelParameters())
        lam_grid = np.array([
            0.02,
            0.04,
            0.06,
            0.08,
            0.10,
            0.14,
            0.20,
            0.30,
            0.40,
            0.50,
        ])
        losses = np.array([
            100 * va.dario_dilemma(0.10, float(la))["value_loss_pct"] for la in lam_grid
        ])
        curve = ax.plot_line_graph(
            lam_grid, losses, line_color=C_COST, add_vertex_dots=False
        )
        truth = DashedLine(
            ax.coords_to_point(0.10, 0),
            ax.coords_to_point(0.10, 28),
            color=C_DEMAND,
        )
        truth_lab = MathTex(
            r"\lambda_{\text{true}}", font_size=30, color=C_DEMAND
        ).next_to(truth, UP, buff=0.1)

        with self.voiceover(
            "Plotting the value loss against the invested-upon belief shows"
            " the dilemma's signature shape: zero at the truth, rising on"
            " both sides, but much steeper on the pessimistic side."
        ):
            self.play(Create(ax), FadeIn(x_lab), FadeIn(y_lab), run_time=1.0)
            self.play(Create(truth), FadeIn(truth_lab), run_time=0.8)
            self.play(Create(curve), run_time=2.0)

        nums = VGroup(
            Text("too conservative: -26%", font_size=30, color=C_COST),
            Text("too aggressive: -6%", font_size=30, color=C_H),
        ).arrange(DOWN, buff=0.25, aligned_edge=LEFT)
        nums.move_to(ax.coords_to_point(0.36, 22)).shift(UP * 0.8)
        with self.voiceover(
            "A firm that invests as if AGI were nearly impossible loses about"
            " twenty-six percent of its value, mostly because it barely"
            " trains, and the AGI prize is where most of the value lives. A"
            " comparably aggressive mistake loses only about six percent."
        ):
            self.play(FadeIn(nums), run_time=1.5)

        tail = Text(
            "but with leverage, the aggressive firm's 5-year default risk is ~8x"
            " higher",
            font_size=28,
            color=C_DEFAULT,
        ).to_edge(DOWN, buff=0.5)
        with self.voiceover(
            "So timidity is the bigger expected-value mistake, and observed"
            " mega-investments are consistent with rational optimism. But the"
            " dilemma is genuinely two-sided: with leverage, the aggressive"
            " firm enters earlier, bigger, and more indebted, and its"
            " five-year default probability is nearly eight times higher."
            " Underinvestment costs expected value; overinvestment buys tail"
            " risk. That is Dario's dilemma."
        ):
            self.play(Write(tail), run_time=1.8)
        self.pause(0.5)
        self.clear_body()


class E11Takeaways(PaperScene):
    def construct(self):
        self.set_header("What to remember", kicker="TAKEAWAYS")

        items = VGroup(
            Text(
                "1.  One allocation links growth and survival:\n"
                "     the same GPUs fund the future or pay for the present.",
                font_size=28,
                line_spacing=0.9,
            ),
            Text(
                "2.  Beliefs, not competition, set the training share\n"
                "     (φ* ≈ 0.70 at λ = 0.10).",
                font_size=28,
                line_spacing=0.9,
            ),
            Text(
                "3.  Competition compresses timing: leaders invest ~43% early.",
                font_size=28,
            ),
            Text(
                "4.  Faith-based survival: training lowers the default\n"
                "     boundary — but is worthless to creditors.",
                font_size=28,
                line_spacing=0.9,
            ),
            Text(
                "5.  Dario's dilemma: timidity costs value;"
                " aggression costs tail risk.",
                font_size=28,
            ),
        ).arrange(DOWN, buff=0.38, aligned_edge=LEFT)
        if items.width > 12.4:
            items.scale_to_fit_width(12.4)
        items.move_to(DOWN * 0.35)

        narrations = [
            "If you remember one thing: in this industry, the option to grow"
            " and the risk of failure are mechanically linked, because they"
            " compete for the same hardware.",
            "The training share is pinned down by beliefs about AI timelines"
            " and technology, not by market position.",
            "Competition shows up in timing: preemption pulls investment"
            " forward by almost half.",
            "Optimism backed by training extends survival, even though that"
            " optimism is worthless in bankruptcy.",
            "And the cost of mistaken beliefs is asymmetric: underinvesting"
            " destroys expected value, overinvesting concentrates default"
            " risk.",
        ]
        for item, narration in zip(items, narrations, strict=True):
            with self.voiceover(narration):
                self.play(FadeIn(item, shift=RIGHT * 0.3), run_time=1.0)

        self.pause(0.5)
        outro = VGroup(
            Text(
                "Investing in Artificial General Intelligence",
                font_size=34,
                weight="BOLD",
            ),
            Text("Vincent Grégoire — HEC Montréal", font_size=26, color=C_FAINT),
            Text(
                "github.com/fintech-research/ai-lab-investment",
                font_size=22,
                color=C_FAINT,
            ),
        ).arrange(DOWN, buff=0.35)
        with self.voiceover(
            "The full model, with all derivations, proofs, and code, is in"
            " the paper. Thanks for watching."
        ):
            self.clear_body()
            self.play(FadeOut(self.header), run_time=0.5)
            self.header = None
            self.play(FadeIn(outro), run_time=1.5)
        self.pause(1.0)
        self.play(FadeOut(outro), run_time=1.0)
