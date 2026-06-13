# How these videos were made

A writeup of the approach used to produce the explainer and the six-part
derivation/proof walkthrough for *Investing in Artificial General
Intelligence*, detailed enough to turn into one or more reusable skills.
It covers the toolchain, the architecture, the conventions that matter,
the bugs that bit (so you can pre-empt them), and the multi-agent
workflow that scaled the production.

---

## 1. Goal and shape of the deliverable

Two distinct products from one paper:

1. **Short explainer** (~11 min) — 3Blue1Brown-style overview at the depth
   of a good conference talk. Audience: anyone curious about the paper.
2. **Derivation/proof walkthrough** (6 videos, ~2h10m) — section by
   section, every derivation and *every appendix proof* worked on screen.
   Audience: the paper's own author, reviewing the model before
   submission (and other researchers who want the full argument).

The non-obvious design decision that shaped everything: **proofs are
presented inline with the section they belong to, not collected at the
end.** That decision came from the issue and should be treated as a hard
requirement for this kind of "review companion" video.

---

## 2. Toolchain

- **Manim Community Edition** (`manim>=0.20`) for animation. Python 3.13.
- **Kokoro TTS via `kokoro-onnx`** for local, offline voiceover (voice
  `af_bella`). No cloud TTS, no per-character billing, deterministic.
- **`soundfile`** to write WAV.
- **ffmpeg** to concatenate per-scene clips into a per-video file.
- **uv** for dependency management (an optional `video` dependency group,
  so the heavy deps don't burden the main project); **just** for task
  recipes; **ruff** for lint/format; **ty** for typecheck (the `video/`
  dir is excluded because the group isn't installed in the default env).

Why not `manim-voiceover`? It's effectively unmaintained and pulls in a
pile of stale transitive deps. We wrote a ~150-line voiceover layer from
scratch (`kokoro_voiceover.py`) instead. The MIT-licensed
`xposed73/kokoro-manim-voiceover` repo was read for API inspiration only,
not imported.

Model files (`kokoro-v1.0.onnx`, `voices-v1.0.bin`, ~340 MB) are
downloaded once into `video/models/` (gitignored) by a `just` recipe.

---

## 3. Architecture

```
video/
  kokoro_voiceover.py   # KokoroTTS (synthesis + cache) + VoiceoverScene
  theme.py              # semantic palette, helpers, BASELINE constants
  scene_base.py         # PaperScene: header, clear_body helpers
  explainer.py          # SCENES = [...] ; one class per scene
  walkthrough_part1..6.py
  render.py             # reads SCENES via AST, renders each, stitches
  manim.cfg             # media_dir, background color
  models/               # Kokoro model files (gitignored)
  media/                # render artifacts (gitignored)
  output/               # stitched per-video mp4s (gitignored)
  AGENTS.md             # conventions (the rules below live here)
```

Key structural choices:

- **One scene class per logical beat.** Scenes are short (30–180 s). This
  is what makes the whole thing tractable: you render, inspect, and fix
  one scene at a time, and chapter markers fall out of scene boundaries.
- **Every module exposes `SCENES = [...]`**, an ordered list of class
  names. `render.py` reads it *with `ast`, without importing the module*
  (importing would trigger Manim setup), renders each scene, then
  concatenates in that order. This is the single source of truth for
  ordering and for the stitch.
- **`VoiceoverScene` context manager** paces animation to narration:

  ```python
  with self.voiceover("Demand follows a geometric Brownian motion."):
      self.play(Create(axes))
  ```

  On entering, the narration WAV is synthesized (or fetched from cache)
  and scheduled; on exit, the scene waits out any narration that outlasts
  the animations in the block. Keep each block to **one or two
  sentences** — long blocks drift out of sync with the visuals.
- **Audio caching by content hash.** Each narration segment is keyed by
  `(voice, speed, lang, text)`; the WAV and a small JSON of metadata
  (incl. duration) are cached in `media/voiceovers/`. Editing one line
  re-synthesizes only that line. This makes re-renders cheap and is what
  makes iterating on visuals (the slow part) practical.
- **Model-derived curves come from the real model code**, imported inside
  `construct()` (e.g. `SingleFirmModel`, `DuopolyModel`,
  `ValuationAnalysis` from `ai_lab_investment.models`). Never re-implement
  the economics in a scene file — the videos stay correct as the model
  evolves, and the figures match the paper exactly.
- **A shared semantic palette** (`theme.py`): demand = yellow, pre-AGI
  (L) regime = blue, post-AGI (H) = teal, training = purple, inference =
  blue, costs = red, default/credit = maroon, option/triggers = gold.
  Every scene uses these names, never raw colors, so the visual language
  is consistent across two hours of video. `theme.BASELINE` holds the
  calibration constants so on-screen numbers can't drift from the paper.

---

## 4. The conventions that actually matter

These are the rules that, if violated, produce wrong or broken videos.
They live in `video/AGENTS.md` and should be the spine of any skill.

### 4.1 Narration is spoken English; on-screen math is LaTeX

Two separate registers, and they must not be mixed:

- **Narration strings** (the argument to `voiceover(...)`) are *spoken* by
  the TTS. Write them as plain English: "phi", "lambda", "beta H", "A
  effective", "X star", "phi greater than phi bar". Never put LaTeX or
  unicode math in narration — the TTS will mangle it.
- **On-screen math must be `MathTex`, never `Text`.** This is the single
  most important rule and the one that caused the worst bug (see §6).
  `Text()` is rendered by Pango (a plain font renderer), so `X_D`,
  `K^alpha`, `phi`, `lambda`, `A_eff`, `->` show up *literally* —
  underscores, carets, spelled-out Greek. Anything with a subscript,
  superscript, Greek letter, symbol name, or comparison/arrow goes in
  `MathTex`, with prose wrapped in `\text{...}`:

  ```python
  MathTex(r"\text{training raises } A_{\text{eff}} \Rightarrow \text{lower } X_D")
  ```

  Use `\to` for "->", `\Rightarrow` for "=>", `\infty`, `\pm`, `\approx`,
  and escape `%` as `\%`. `MathTex` glyphs run a bit smaller than `Text`
  at equal `font_size`, so bump size ~2pt or drop ~10–15% on wide lines
  when converting.

### 4.2 ASCII-only in `Text()`

The ruff config flags ambiguous unicode (RUF001: `−`, `×`, curly quotes).
Keep `Text()` strings ASCII. This rule interacts dangerously with 4.1: an
over-literal reading ("ASCII only") is what pushed math into `Text` in the
first place. State both rules together and resolve the tension explicitly:
*math goes in MathTex (where unicode is irrelevant); the ASCII rule is
only about the prose that remains in Text.*

### 4.3 Numbers match the paper

Every quoted figure must match the paper's baseline (`theme.BASELINE` and
the appendix tables) or be computed live from model code. Cross-check.

### 4.4 Layout discipline

- A persistent header (`PaperScene.set_header(title, kicker)`) anchors
  each scene; `clear_body()` fades everything except the header between
  beats.
- Derivations are shown as *successive equation lines* (a `VGroup`
  arranged `DOWN`, or `TransformMatchingTex`), with the term being
  manipulated highlighted. For a review video, never skip an algebraic
  step you'd want a referee to check.
- When you replace one equation with another in the same spot, fade the
  old one out first — don't stack them (a real bug we hit: the trigger
  formula overlapping the chart it was meant to sit above).
- Multi-line `Text` blocks that might overflow: wrap manually and clamp
  with `scale_to_fit_width(frame_width)` as a safety net.

---

## 5. The render/verify loop

Per scene, the loop that catches problems:

1. `cd video && uv run manim render -ql [--media_dir media/build_pN] <file> <Scene>`
   (`-ql` = 480p15 draft; isolated `--media_dir` avoids Tex-cache races
   when several agents render in parallel).
2. Fix LaTeX errors until it renders. (LaTeX failures are the most common
   error: unescaped `%`, stray `&`, bad `\text{}` nesting.)
3. Extract a frame near the dense content and *look at it*:
   `ffmpeg -y -sseof -3 -i <scene>.mp4 -frames:v 1 frame.png` (or `-ss T`
   for a specific time), then view it. This is the only way to catch
   overlap/offscreen text — the render "succeeding" tells you nothing
   about layout. The `-s` flag on `manim` also dumps the last frame.
4. For audio, scan for dropped narration with silence detection:
   `ffmpeg -i <scene>.mp4 -af silencedetect=n=-40dB:d=4 -f null -`
   and check there's no `silence_start: 0` (leading silence ⇒ a muted
   segment).

Quality grades map to manim flags: `l`=480p15, `m`=720p30, `h`=1080p60,
`k`=2160p60. Draft everything at `l`; render `h`/`k` only for the final.
Audio is cached, so the final HQ pass only re-renders frames.

Verification gates before shipping: `just check` (ruff + ty), `just test`,
a repo-wide AST scan for math-in-`Text` (see §6), a full draft re-render +
stitch, and a silence scan over every scene.

---

## 6. Bugs that bit (pre-empt these)

Three real bugs, each worth a guard in a skill:

1. **espeak-ng truncates its data path to 160 chars.** Kokoro phonemizes
   via espeak-ng, whose `N_PATH_HOME` buffer silently truncates a long
   data-dir path (a deep venv inside a worktree blew past it), crashing
   the tokenizer with a confusing "phontab not found". Fix: symlink the
   espeak data dir to a short path under the temp dir and point espeak
   there. Implemented in `KokoroTTS._espeak_config()`. Keep it.

2. **Manim drops `add_sound` after a cached animation.** On a re-render,
   when an animation is found in the partial-movie cache, Manim sets
   `renderer.skip_animations = True` and only resets it at the *next*
   `play()`. `Scene.add_sound` silently no-ops while that flag is set —
   so narration started right after a cached animation goes missing. The
   first render is fine; re-renders lose audio. Fix: reset
   `renderer.skip_animations` (to `_original_skipping_status`) at the top
   of `voiceover()`, mirroring what `play()` does. Without this, audio
   silently disappears on exactly the re-renders you do most.

3. **Math rendered in `Text` instead of `MathTex`** (see §4.1). This was
   systematic — 97 sites across six files — because the scene-writing
   instruction said "ASCII only in Text()" without the countervailing
   "math goes in MathTex." The detector that should ship with the skill:

   ```python
   import ast, re
   from pathlib import Path
   pat = re.compile(r"(_[A-Za-z0-9]|\^|\b(alpha|beta|gamma|delta|lambda|"
                    r"sigma|phi|mu|ell)\b|>=|<=|->|=>|\bA_eff\b|\bX\*|\bK\*)")
   for f in Path("video").glob("*.py"):
       for node in ast.walk(ast.parse(f.read_text())):
           if isinstance(node, ast.Call) and getattr(node.func,"id","")=="Text":
               for a in node.args:
                   if isinstance(a, ast.Constant) and isinstance(a.value,str) \
                      and pat.search(a.value):
                       print(f, node.lineno, repr(a.value[:80]))
   ```

   Run it as an acceptance gate; the target is zero hits. (Note it can't
   catch arrow chains hidden in f-strings or concatenations, so a human
   frame-check is still required.)

---

## 7. The multi-agent production workflow

This is how the work scaled, and the part most worth turning into an
orchestration skill.

- **The orchestrator does the infrastructure first**, end to end, and
  proves it with a smoke test: deps, the voiceover layer, the theme, the
  render driver, and one trivial narrated scene rendered and inspected.
  Don't fan out until the pipeline demonstrably works — otherwise N agents
  reproduce the same setup bug N times.
- **One agent per video** (or per file) for the bulk authoring. Each got a
  detailed brief: which paper sections/appendix proofs to cover, the exact
  derivation steps to show on screen, the shared conventions (with the
  MathTex rule stated explicitly — see §4.1), the baseline numbers, and
  the model-code entry points to compute curves from. Each agent was
  required to self-verify: lint clean, every scene renders, and frames of
  the dense scenes inspected.
- **Agents render into isolated `--media_dir`s** (`media/build_pN`) to
  avoid clobbering each other's Tex cache and partial-movie files.
- **The orchestrator integrates, doesn't trust blindly.** For each agent
  result: re-run the lint and the AST scanner, spot-check 2–3 of the
  densest frames yourself, then commit. Several layout issues and the
  entire math-in-`Text` class of bugs were caught at integration, not by
  the authoring agents.
- **Briefs carry the hard-won rules.** When a systematic bug is found,
  the fix isn't just "patch the files" — it's (a) record the rule in
  `AGENTS.md` and project memory, and (b) put the rule *and a detector*
  into every agent brief so it can't recur. The math-in-`Text` fix was
  itself fanned out: one agent per file, each with the offender list and
  the scanner, acceptance = scanner-zero.
- **Watch for session limits.** A batch of fix-agents died mid-task at a
  usage-limit reset; because each had made partial, valid edits and the
  acceptance criterion was a re-runnable scanner, recovery was just
  "re-launch on the remainder." Design agent tasks to be *resumable*:
  idempotent edits + a machine-checkable done condition.

A reasonable skill decomposition:

- **`manim-paper-video` skill** — the single-video workflow: scaffold (or
  reuse) the voiceover/theme/render infra, author scenes under the §4
  conventions, run the §5 verify loop, ship. Bundles the §6 bug guards
  and the AST scanner.
- **`paper-walkthrough-series` skill** (orchestration) — fan out one
  authoring agent per section with the brief template, integrate with the
  verify-and-commit loop, build chapter markers from scene durations,
  produce the stitched videos and the YouTube descriptions.

---

## 8. Producing the YouTube metadata

Chapters are derived mechanically: read each module's `SCENES` order,
take each scene clip's duration via `ffprobe`, accumulate to get the
start timestamp, and pull the human-readable chapter title from the
scene's `set_header(...)` first argument (with hand-written titles for the
title/cold-open scenes that have no header). The descriptions cross-link
the explainer and all six parts, and append a fixed footer (paper link,
blog, socials). See `youtube_descriptions.md` for the output and the
exact script that computed the timestamps lives in the session history.
