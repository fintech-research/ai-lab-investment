"""Shared scene scaffolding for the paper videos."""

from __future__ import annotations

from kokoro_voiceover import VoiceoverScene
from manim import (
    DOWN,
    LEFT,
    UP,
    FadeIn,
    FadeOut,
    Mobject,
    Text,
    VGroup,
)
from theme import C_FAINT, C_TEXT, underline


class PaperScene(VoiceoverScene):
    """VoiceoverScene with a persistent header and convenience helpers."""

    header: VGroup | None = None

    def set_header(self, title: str, kicker: str | None = None) -> VGroup:
        """Display (or replace) a small persistent header at the top left."""
        parts = []
        if kicker:
            parts.append(Text(kicker, font_size=18, color=C_FAINT))
        parts.append(Text(title, font_size=28, color=C_TEXT, weight="BOLD"))
        group = VGroup(*parts).arrange(DOWN, aligned_edge=LEFT, buff=0.12)
        group.to_corner(UP + LEFT, buff=0.4)
        group.add(underline(group[-1]).set_stroke(width=2))
        if self.header is not None:
            self.play(FadeOut(self.header), FadeIn(group), run_time=0.6)
        else:
            self.play(FadeIn(group), run_time=0.6)
        self.header = group
        return group

    def clear_body(self, *keep: Mobject, run_time: float = 0.7) -> None:
        """Fade out everything except the header and ``keep`` mobjects."""
        protected = set(keep)
        if self.header is not None:
            protected.add(self.header)
        protected_families: set[Mobject] = set()
        for m in protected:
            protected_families.update(m.get_family())
        doomed = [
            m
            for m in self.mobjects
            if m not in protected and not (set(m.get_family()) & protected_families)
        ]
        if doomed:
            self.play(*[FadeOut(m) for m in doomed], run_time=run_time)
