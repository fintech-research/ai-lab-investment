"""Render driver: renders all scenes of a video module in order and stitches them.

Usage (from the repo root or video/):
    uv run python video/render.py explainer --quality l
    uv run python video/render.py walkthrough_part1 walkthrough_part2 --quality h

Each video module must define ``SCENES``, an ordered list of scene class
names. The driver renders each scene with manim (sequentially, reusing the
voiceover cache) and concatenates the results with ffmpeg into
``video/output/<module>_<quality>.mp4``.
"""

from __future__ import annotations

import argparse
import ast
import shutil
import subprocess
import sys
from pathlib import Path

VIDEO_DIR = Path(__file__).resolve().parent

QUALITY_DIRS = {
    "l": "480p15",
    "m": "720p30",
    "h": "1080p60",
    "k": "2160p60",
}


def scene_names(module_path: Path) -> list[str]:
    """Read the SCENES list from a module without importing it."""
    tree = ast.parse(module_path.read_text())
    for node in ast.walk(tree):
        if isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name) and target.id == "SCENES":
                    return ast.literal_eval(node.value)
    msg = f"{module_path} does not define a SCENES list"
    raise ValueError(msg)


def render_module(module: str, quality: str, scenes_filter: list[str] | None) -> Path:
    module_path = VIDEO_DIR / f"{module}.py"
    names = scene_names(module_path)
    if scenes_filter:
        names = [n for n in names if n in scenes_filter]

    for name in names:
        print(f"=== Rendering {module}.{name} (-q{quality}) ===", flush=True)
        subprocess.run(  # noqa: S603
            [
                sys.executable,
                "-m",
                "manim",
                "render",
                f"-q{quality}",
                module_path.name,
                name,
            ],
            cwd=VIDEO_DIR,
            check=True,
        )

    clips_dir = VIDEO_DIR / "media" / "videos" / module / QUALITY_DIRS[quality]
    clips = [clips_dir / f"{name}.mp4" for name in names]
    missing = [c for c in clips if not c.exists()]
    if missing:
        msg = f"Missing rendered clips: {missing}"
        raise FileNotFoundError(msg)

    out_dir = VIDEO_DIR / "output"
    out_dir.mkdir(exist_ok=True)
    out_path = out_dir / f"{module}_{quality}.mp4"
    concat_list = clips_dir / "concat.txt"
    concat_list.write_text("".join(f"file '{c.resolve()}'\n" for c in clips))
    print(f"=== Stitching {len(clips)} clips -> {out_path} ===", flush=True)
    ffmpeg = shutil.which("ffmpeg")
    if ffmpeg is None:
        msg = "ffmpeg not found on PATH"
        raise FileNotFoundError(msg)
    subprocess.run(  # noqa: S603
        [
            ffmpeg,
            "-y",
            "-f",
            "concat",
            "-safe",
            "0",
            "-i",
            str(concat_list),
            "-c",
            "copy",
            str(out_path),
        ],
        check=True,
        capture_output=True,
    )
    return out_path


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("modules", nargs="+", help="video module names (no .py)")
    parser.add_argument("--quality", "-q", default="h", choices=list(QUALITY_DIRS))
    parser.add_argument(
        "--scenes",
        nargs="*",
        default=None,
        help="render only these scenes (still stitched in SCENES order)",
    )
    args = parser.parse_args()
    outputs = [render_module(m, args.quality, args.scenes) for m in args.modules]
    for out in outputs:
        print(f"Done: {out}")


if __name__ == "__main__":
    main()
