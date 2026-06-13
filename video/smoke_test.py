"""Minimal end-to-end check: Kokoro narration synced with a Manim animation.

Render with:
    cd video && uv run manim render -ql smoke_test.py SmokeTest
"""

from kokoro_voiceover import VoiceoverScene
from manim import UP, Create, MathTex, Write
from theme import C_DEMAND, clean_axes


class SmokeTest(VoiceoverScene):
    def construct(self):
        ax = clean_axes(x_range=[0, 10], y_range=[0, 3], width=8, height=4)
        curve = ax.plot(lambda t: 0.5 * 1.12**t, color=C_DEMAND)
        label = MathTex(r"dX_t = \mu_s X_t\,dt + \sigma X_t\,dW_t", font_size=40)
        label.to_edge(UP)

        with self.voiceover(
            "This is a smoke test. Demand follows a geometric Brownian motion"
            " with regime dependent drift."
        ):
            self.play(Create(ax), run_time=1.5)
            self.play(Create(curve), run_time=2)
            self.play(Write(label), run_time=1.5)
