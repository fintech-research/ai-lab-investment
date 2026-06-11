# AGENTS.md — video/

3Blue1Brown-style explainer videos for the paper, built with Manim CE and
locally generated Kokoro voiceovers (issue #98). Global rules: `@../AGENTS.md`.

## Setup and rendering

- `just video-setup` — install the `video` dependency group and download the
  Kokoro ONNX model files (~340 MB, gitignored, into `video/models/`).
- `just render-explainer [quality]` / `just render-walkthrough [quality]` —
  render and stitch; quality is `l` (480p15, drafts), `m`, `h` (1080p60), `k`.
- Single scene while iterating:
  `cd video && uv run manim render -ql explainer.py SceneName`
- Stitched outputs land in `video/output/`; intermediate media in
  `video/media/` (both gitignored).

## Structure

- `kokoro_voiceover.py` — self-contained TTS layer (no manim-voiceover
  dependency): `KokoroTTS` (synthesis + content-hash cache) and
  `VoiceoverScene` (the `with self.voiceover("...")` context manager).
- `theme.py` — semantic palette and helpers. Demand = yellow, L-regime =
  blue, H-regime = teal, training = purple, inference = blue, costs = red,
  default/credit = maroon, option/triggers = gold. Use these, not raw colors.
- `explainer.py` — short (~10–15 min) conference-level video.
- `walkthrough_part1..6.py` — section-by-section derivation/proof series.
  Appendix proofs are presented inline with their sections, never separately.
- Each video module defines `SCENES`, the ordered list of scene class names;
  `render.py` reads it (without importing the module) to render and stitch.

## Conventions

- Every scene subclasses `VoiceoverScene` and paces animation inside
  `with self.voiceover("...")` blocks. Keep each block to one or two
  sentences; long narration in a single block drifts out of sync with the
  visuals.
- Narration is plain spoken English: write "phi", "lambda", "beta",
  "A effective", "X star" — never LaTeX or unicode math in narration text.
  Spell out comparisons ("phi greater than phi bar"). The voice is
  `af_bella` (do not change without updating cached audio).
- Voiceover audio is cached in `video/media/voiceovers/` keyed by
  (voice, speed, lang, text); editing narration text regenerates only the
  changed segments.
- All numbers quoted in narration must match the paper's baseline
  calibration (see `theme.BASELINE` and `paper/_appendix.qmd`
  Table tbl-baseline-results).
- Model-derived curves (option values, triggers, boundaries) must be
  computed with `ai_lab_investment` model code (importable in scenes), not
  re-implemented in scene files.

## Gotchas

- espeak-ng truncates its data path to 160 chars; `KokoroTTS` works around
  this with a short symlink in the temp dir (`_espeak_config`). Do not
  remove it.
- `video/` is excluded from `ty` type checking because the `video`
  dependency group is not installed in the default dev environment
  (`uv sync` removes it; re-run `uv sync --group video`).
- LaTeX in `MathTex` uses the system TeX installation; keep equations to
  amsmath-compatible constructs.
