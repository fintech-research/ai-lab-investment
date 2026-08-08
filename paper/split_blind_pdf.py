#!/usr/bin/env python3
"""Split the blind render into the two PDFs uploaded to the INFORMS portal.

Usage:
    uv run python paper/split_blind_pdf.py   # (or: just render-blind)

Management Science takes supplementary material as a separate *e-companion*, so
the double-anonymous submission is two files: the manuscript and the Internet
Appendix. Quarto resolves cross-references only inside a single render, and the
manuscript and the appendix reference each other heavily (``@tbl-parameters``
one way, ``@eq-hjb-L`` the other), so ``index-blind.qmd`` is rendered *whole* and
cut here instead of being rendered as two documents.

The cut point is read from the LaTeX ``.aux`` file: ``_appendix-cover.qmd``
carries a ``\\label{ia-cover}`` on the Internet Appendix cover page, whose
recorded page is the first page of the e-companion. Pages are copied losslessly
with ``pdfjam`` (the ``pdfpages`` LaTeX package), which is part of the TeX Live
installation the paper already requires.
"""

from __future__ import annotations

import re
import shutil
import subprocess
import sys
from pathlib import Path
from typing import NoReturn

HERE = Path(__file__).parent
AUX = HERE / "index-blind.aux"
FULL_PDF = HERE / "_output" / "ai_lab_investment_blind_full.pdf"
MANUSCRIPT_PDF = HERE / "_output" / "ai_lab_investment_blind.pdf"
ECOMPANION_PDF = HERE / "_output" / "ai_lab_investment_blind_ecompanion.pdf"

TITLE = "Capacity, Training, and Default in the Race to Artificial General Intelligence"
KEYWORDS = (
    "real options, irreversible capacity investment, artificial intelligence, "
    "duopoly preemption, default risk"
)

# \newlabel{ia-cover}{{<label>}{<page>}{<title>}{<anchor>}{}} under hyperref.
_LABEL_RE = re.compile(r"\\newlabel\{ia-cover\}\{\{.*?\}\{(\d+)\}")


def fail(message: str) -> NoReturn:
    """Report a build problem and stop."""
    print(f"❌ {message}", file=sys.stderr)
    raise SystemExit(1)


def appendix_start_page() -> int:
    """Return the physical page number of the Internet Appendix cover page."""
    if not AUX.exists():
        fail(f"missing {AUX}; run `just render-blind`")
    match = _LABEL_RE.search(AUX.read_text(encoding="utf-8", errors="replace"))
    if match is None:
        fail(f"no \\label{{ia-cover}} recorded in {AUX}; is the appendix included?")
    page = int(match.group(1))
    if page < 2:
        fail(f"implausible Internet Appendix start page {page}")
    return page


def extract(pdfjam: str, pages: str, out: Path, title: str) -> None:
    """Copy ``pages`` of the full blind PDF into ``out`` with blind metadata."""
    subprocess.run(  # noqa: S603 - fixed argument list, no shell
        [
            pdfjam,
            "--fitpaper",
            "true",
            "--rotateoversize",
            "false",
            "--pdftitle",
            title,
            "--pdfauthor",
            "",
            "--pdfsubject",
            "",
            "--pdfkeywords",
            KEYWORDS,
            "--outfile",
            str(out),
            "--",
            str(FULL_PDF),
            pages,
        ],
        check=True,
        capture_output=True,
    )


def main() -> int:
    pdfjam = shutil.which("pdfjam")
    if pdfjam is None:
        fail("pdfjam not found; it ships with TeX Live (pdfpages)")
    if not FULL_PDF.exists():
        fail(f"missing {FULL_PDF}; run `just render-blind`")

    start = appendix_start_page()
    extract(pdfjam, f"1-{start - 1}", MANUSCRIPT_PDF, TITLE)
    extract(pdfjam, f"{start}-", ECOMPANION_PDF, f"Internet Appendix for {TITLE}")
    FULL_PDF.unlink()

    print(f"✅ manuscript  : {MANUSCRIPT_PDF} (pages 1-{start - 1})")
    print(f"✅ e-companion : {ECOMPANION_PDF} (pages {start}-end)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
