"""Shared visual style for the paper videos (3Blue1Brown-inspired).

Semantic colors map model objects to a consistent palette across all
scenes: demand is yellow, the pre-AGI (L) regime is blue, the post-AGI
(H) regime is teal, training is purple, inference is blue, costs and
default are red tones.
"""

from __future__ import annotations

from manim import (
    BLUE_C,
    DOWN,
    GOLD_C,
    GREY_A,
    GREY_B,
    LEFT,
    MAROON_C,
    PURPLE_A,
    RED_C,
    RIGHT,
    TEAL_C,
    UP,
    YELLOW_C,
    Axes,
    FadeIn,
    FadeOut,
    Line,
    MathTex,
    Mobject,
    Scene,
    SurroundingRectangle,
    Tex,
    Text,
    VGroup,
)

# Semantic palette
C_DEMAND = YELLOW_C  # demand process X_t
C_L = BLUE_C  # low / pre-AGI regime
C_H = TEAL_C  # high / post-AGI regime
C_TRAIN = PURPLE_A  # training compute (phi K)
C_INFER = BLUE_C  # inference compute ((1-phi) K)
C_COST = RED_C  # investment / operating costs
C_DEFAULT = MAROON_C  # default boundary, credit risk
C_OPTION = GOLD_C  # option value, triggers
C_TEXT = GREY_A
C_FAINT = GREY_B

BG_COLOR = "#101418"

TITLE_SCALE = 1.1
BODY_SCALE = 0.7


def title_text(s: str, **kwargs) -> Text:
    return Text(s, weight="BOLD", font_size=44, **kwargs)


def body_tex(*parts: str, **kwargs) -> Tex:
    kwargs.setdefault("font_size", 34)
    return Tex(*parts, **kwargs)


def section_label(index: str, name: str) -> VGroup:
    """Small persistent corner label, e.g. '2.1  Single-firm benchmark'."""
    label = Text(f"{index}  {name}", font_size=20, color=C_FAINT)
    label.to_corner(UP + LEFT, buff=0.3)
    return VGroup(label)


def underline(mobj: Mobject, color=C_OPTION, buff: float = 0.12) -> Line:
    line = Line(LEFT, RIGHT, color=color, stroke_width=3)
    line.set_width(mobj.get_width() + 0.2)
    line.next_to(mobj, DOWN, buff=buff)
    return line


def highlight(
    mobj: Mobject, color=C_OPTION, buff: float = 0.12
) -> SurroundingRectangle:
    return SurroundingRectangle(mobj, color=color, buff=buff, stroke_width=2.5)


def clean_axes(
    x_range, y_range, width: float = 9.0, height: float = 5.0, **kwargs
) -> Axes:
    """Axes with the muted look used across all scenes."""
    kwargs.setdefault("tips", False)
    kwargs.setdefault(
        "axis_config",
        {"color": C_FAINT, "stroke_width": 2, "include_ticks": False},
    )
    ax = Axes(
        x_range=x_range, y_range=y_range, x_length=width, y_length=height, **kwargs
    )
    return ax


def fade_replace(scene: Scene, old: Mobject, new: Mobject, run_time: float = 0.8):
    scene.play(FadeOut(old, run_time=run_time / 2))
    scene.play(FadeIn(new, run_time=run_time / 2))


def eq(latex: str, color=None, font_size: int = 40, **kwargs) -> MathTex:
    m = MathTex(latex, font_size=font_size, **kwargs)
    if color is not None:
        m.set_color(color)
    return m


# Baseline calibration constants used across scenes (paper Table: baseline)
BASELINE = {
    "r": 0.12,
    "mu_L": 0.01,
    "mu_H": 0.06,
    "sigma": 0.25,
    "lambda": 0.10,
    "alpha": 0.40,
    "gamma": 1.50,
    "delta": 0.03,
    "c": 1.0,
    "beta_H": 1.55,
    "beta_L_plus": 3.01,
    "phi_star": 0.70,
    "K_star": 0.0067,
    "X_star": 0.0047,
    "X_P": 0.0027,
    "phi_underbar": 0.18,
    "phi_tilde": 0.32,
}
