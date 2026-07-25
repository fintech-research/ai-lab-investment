"""Guard the identified/blind manuscript pair against metadata drift.

`paper/index-blind.qmd` is the double-anonymous copy of `paper/index.qmd` used
for the Management Science submission. Quarto has no per-document metadata
include, so the shared front matter (title, abstract, keywords) is physically
duplicated; these tests keep the two copies in sync and enforce the submission
constraints that live in the front matter.
"""

from pathlib import Path
from typing import Any

import yaml

PAPER = Path(__file__).resolve().parents[1] / "paper"
IDENTIFIED = PAPER / "index.qmd"
BLIND = PAPER / "index-blind.qmd"
KEYWORDS_TEX = PAPER / "keywords.tex"

SHARED_KEYS = ("title", "abstract", "keywords")
IDENTIFYING_KEYS = ("authors", "affiliations", "thanks")


def front_matter(path: Path) -> dict[str, Any]:
    """Return the YAML front matter of a Quarto document."""
    text = path.read_text(encoding="utf-8")
    _, _, rest = text.partition("---\n")
    block, _, _ = rest.partition("\n---\n")
    return yaml.safe_load(block)


def test_shared_front_matter_matches() -> None:
    identified = front_matter(IDENTIFIED)
    blind = front_matter(BLIND)
    for key in SHARED_KEYS:
        assert blind[key] == identified[key], (
            f"{key} differs between index.qmd and index-blind.qmd; "
            "both carry the same manuscript content"
        )


def test_blind_manuscript_is_anonymous() -> None:
    blind = front_matter(BLIND)
    for key in IDENTIFYING_KEYS:
        assert key not in blind, f"index-blind.qmd must not declare `{key}`"


def test_blind_manuscript_uses_one_and_a_half_spacing() -> None:
    """Management Science requires at least 1.5 line spacing."""
    blind = front_matter(BLIND)
    assert blind["format"]["pdf"]["linestretch"] >= 1.5


def test_keyword_count_within_informs_limit() -> None:
    """Management Science asks for three to five keywords."""
    keywords = front_matter(IDENTIFIED)["keywords"]
    assert 3 <= len(keywords) <= 5, keywords


def test_keywords_tex_mirrors_front_matter() -> None:
    """`keywords.tex` prints the list on the title page; keep it in sync."""
    line = next(
        line
        for line in KEYWORDS_TEX.read_text(encoding="utf-8").splitlines()
        if "\\textbf{Keywords:}" in line
    )
    printed = line.split("\\textbf{Keywords:}")[1].replace("\\par", "").strip()
    assert printed == "; ".join(front_matter(IDENTIFIED)["keywords"])
