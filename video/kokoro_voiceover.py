"""Local text-to-speech voiceovers for Manim using Kokoro (ONNX).

This is a self-contained replacement for ``manim-voiceover`` (which is
unmaintained and pulls in stale dependencies). It synthesizes narration
locally with `kokoro-onnx <https://github.com/thewh1teagle/kokoro-onnx>`_,
caches the generated audio by content hash, and synchronizes animations
with the narration through a ``voiceover`` context manager:

    class MyScene(VoiceoverScene):
        def construct(self):
            with self.voiceover("Demand follows a geometric Brownian motion."):
                self.play(Create(axes))

On exiting the ``with`` block, the scene waits for the remainder of the
narration before continuing, so each block of animation is paced by its
narration segment.

Model files (``kokoro-v1.0.onnx`` and ``voices-v1.0.bin``) must be present
in ``video/models/``; run ``just video-models`` to download them.

API inspired by manim-voiceover and the (MIT-licensed) implementation in
https://github.com/xposed73/kokoro-manim-voiceover, but written from
scratch against kokoro-onnx >= 0.5.
"""

from __future__ import annotations

import hashlib
import json
import os
import tempfile
from contextlib import contextmanager
from dataclasses import dataclass
from pathlib import Path
from typing import TYPE_CHECKING

import soundfile as sf
from manim import Scene, config, logger

if TYPE_CHECKING:
    from collections.abc import Generator

VIDEO_DIR = Path(__file__).resolve().parent
MODEL_DIR = Path(os.environ.get("KOKORO_MODEL_DIR", VIDEO_DIR / "models"))
CACHE_DIR = Path(os.environ.get("KOKORO_CACHE_DIR", VIDEO_DIR / "media" / "voiceovers"))

DEFAULT_VOICE = "af_bella"
DEFAULT_SPEED = 1.0
DEFAULT_LANG = "en-us"


class KokoroTTS:
    """Synthesizes speech with Kokoro and caches WAV files by content hash."""

    def __init__(
        self,
        voice: str = DEFAULT_VOICE,
        speed: float = DEFAULT_SPEED,
        lang: str = DEFAULT_LANG,
        model_dir: Path = MODEL_DIR,
        cache_dir: Path = CACHE_DIR,
    ) -> None:
        self.voice = voice
        self.speed = speed
        self.lang = lang
        self.model_path = model_dir / "kokoro-v1.0.onnx"
        self.voices_path = model_dir / "voices-v1.0.bin"
        self.cache_dir = cache_dir
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self._kokoro = None  # lazy: loading the ONNX model takes a few seconds

    @staticmethod
    def _espeak_config():
        """Espeak config that survives long project paths.

        espeak-ng stores its data path in a 160-character buffer
        (``N_PATH_HOME``); the espeak-ng-data directory inside a deeply
        nested virtualenv exceeds it and gets silently truncated, crashing
        the tokenizer. Mirror the data directory behind a short symlink in
        the temp directory and point espeak there instead.
        """
        import espeakng_loader
        from kokoro_onnx.config import EspeakConfig

        base = Path(tempfile.gettempdir()) / "espeak-kokoro"
        base.mkdir(parents=True, exist_ok=True)
        link = base / "espeak-ng-data"
        if not link.exists():
            link.symlink_to(
                Path(espeakng_loader.get_data_path()), target_is_directory=True
            )
        return EspeakConfig(
            lib_path=espeakng_loader.get_library_path(), data_path=str(base)
        )

    def _load(self):
        if self._kokoro is None:
            if not self.model_path.exists() or not self.voices_path.exists():
                msg = (
                    f"Kokoro model files not found in {self.model_path.parent}. "
                    "Run `just video-models` to download them."
                )
                raise FileNotFoundError(msg)
            from kokoro_onnx import Kokoro

            logger.info("Loading Kokoro ONNX model (first use only)...")
            self._kokoro = Kokoro(
                str(self.model_path),
                str(self.voices_path),
                espeak_config=self._espeak_config(),
            )
        return self._kokoro

    def _cache_key(self, text: str) -> str:
        payload = f"{self.voice}|{self.speed}|{self.lang}|{text}"
        return hashlib.sha256(payload.encode()).hexdigest()[:24]

    def synthesize(self, text: str) -> tuple[Path, float]:
        """Return (path to WAV, duration in seconds) for the given narration."""
        key = self._cache_key(text)
        wav_path = self.cache_dir / f"{key}.wav"
        meta_path = self.cache_dir / f"{key}.json"
        if wav_path.exists() and meta_path.exists():
            meta = json.loads(meta_path.read_text())
            return wav_path, meta["duration"]

        kokoro = self._load()
        samples, sample_rate = kokoro.create(
            text, voice=self.voice, speed=self.speed, lang=self.lang
        )
        sf.write(wav_path, samples, sample_rate)
        duration = len(samples) / sample_rate
        meta_path.write_text(
            json.dumps(
                {
                    "text": text,
                    "voice": self.voice,
                    "speed": self.speed,
                    "lang": self.lang,
                    "duration": duration,
                },
                indent=2,
            )
        )
        return wav_path, duration


@dataclass
class VoiceoverTracker:
    """Tracks the playback window of one narration segment."""

    scene: Scene
    duration: float
    start_time: float

    @property
    def remaining(self) -> float:
        elapsed = self.scene.renderer.time - self.start_time
        return max(self.duration - elapsed, 0.0)


class VoiceoverScene(Scene):
    """A Scene with Kokoro-narrated voiceover segments.

    Subclasses use :meth:`voiceover` as a context manager. Narration audio
    is generated (or fetched from cache) at render time and mixed into the
    scene's audio track; the scene waits out any narration that outlasts
    the animations inside the block.
    """

    tts: KokoroTTS | None = None

    def set_speech_service(self, tts: KokoroTTS) -> None:
        self.tts = tts

    def _ensure_tts(self) -> KokoroTTS:
        if self.tts is None:
            self.tts = KokoroTTS()
        return self.tts

    @contextmanager
    def voiceover(self, text: str) -> Generator[VoiceoverTracker]:
        """Play narration for ``text`` over the animations in the block."""
        text = " ".join(text.split())  # normalize whitespace from indented strings
        wav_path, duration = self._ensure_tts().synthesize(text)
        # After a cache-hit play(), manim leaves renderer.skip_animations True
        # until the next play() resets it, and Scene.add_sound silently drops
        # sounds while it is set — which would mute narration on re-renders.
        # Reset it here with the same semantics as play().
        self.renderer.skip_animations = getattr(
            self.renderer, "_original_skipping_status", False
        )
        self.add_sound(str(wav_path))
        tracker = VoiceoverTracker(
            scene=self, duration=duration, start_time=self.renderer.time
        )
        try:
            yield tracker
        finally:
            self.safe_wait(tracker.remaining)

    def safe_wait(self, duration: float) -> None:
        """Wait only if the duration exceeds one frame."""
        if duration > 1 / config.frame_rate:
            self.wait(duration)

    def pause(self, duration: float = 0.6) -> None:
        """A beat of silence between narration segments."""
        self.safe_wait(duration)
