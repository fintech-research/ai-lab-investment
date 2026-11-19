# Submission materials (issue #95)

Documents supporting journal submission of *Investing in Artificial General Intelligence*.

- `cover-letter.md` — letter to the editor, currently targeted at Management Science (addressed generically to "Dear Editor"), with the abstract included (`tests/test_paper_metadata.py` fails if it drifts from `paper/index.qmd`); swap the journal name and fit paragraph to retarget. `cover-letter-notes.md` holds the editorial notes and the record of what was changed or deliberately kept.
- `ai-disclosure.md` — declaration of generative AI use: a short-form Elsevier-style statement (to be inserted in the manuscript before the references for Elsevier targets) and a detailed long-form disclosure.
- `replication/` — referee-facing machine-checked proof package (issue #108): a README for referees, `extract_equations.py` (generates `equations.tex`, the complete labeled equation listing, from the paper sources), and `just build-replication-package` to assemble the zip (Lean project + README + equations listing + the four cached numerical solutions in `numerics/`: `duopoly_equilibria.json`, `duopoly_dilemma.json`, `robustness_duopoly.json`, `robustness_joint.csv`).

## Building the submission PDFs

`just render-blind` produces the **two artifacts** uploaded to the INFORMS portal, both
in `paper/_output/`:

| File | Contents |
|:--|:--|
| `ai_lab_investment_blind.pdf` | Anonymous manuscript (title, abstract, keywords, body, references) |
| `ai_lab_investment_blind_ecompanion.pdf` | Anonymous e-companion (the Internet Appendix) |

`just render-paper` is unaffected and still produces the identified single-PDF version
(`paper/_output/ai_lab_investment.pdf`) with the author block, acknowledgments footnote,
and the appendix bound in.

How it works (see `paper/index-blind.qmd` for the details): `index-blind.qmd` mirrors
`index.qmd` but drops `authors`, `affiliations`, and `thanks`, and sets `linestretch: 1.5`.
It is selected by the `blind` Quarto profile (`paper/_quarto-blind.yml`), which makes it
the project's only render target so it still inherits the shared format configuration in
`paper/_quarto.yaml` (11pt, 3 cm margins, natbib/econometrica, title and keyword
partials). Quarto resolves cross-references only within a single render, and the
manuscript and the appendix reference each other in both directions, so the blind
document is rendered *whole* and `paper/split_blind_pdf.py` then cuts the PDF at the
Internet Appendix cover page (located via a `\label` in the `.aux` file, pages copied
losslessly with `pdfjam`). Every cross-reference therefore resolves in both artifacts.

Verified against the Management Science author guidelines (fetched 2026-07-25):
double-anonymous with no title page, ≥ 1.5 line spacing, 11pt, 1-inch-plus margins,
3–5 keywords, abstract ≤ 250 words (250 as of 2026-11-19, at the cap, guarded by `tests/test_paper_metadata.py`), alphabetical author–year
references, supplementary material as a separate e-companion.

**Length.** The guidelines set no hard page limit for an initial submission but
allow rejection for excessive length, and cap *invited revisions* at 32 pages at
1.5 spacing (47 double-spaced), excluding the e-companion. The blind manuscript
was 67 pages (plus a 49-page e-companion) in the 2026-08-08 build and 47 pages
(plus a 70-page e-companion) after the #149 consolidation and the #150 prose pass
of 2026-09-10, then 45 pages (plus a 66-page e-companion) once Internet Appendix I
and the references only it cited were removed on 2026-10-04. The model-of-record revision of November 2026 (#171) and the #187 framing rewrite brought it back to 60 pages (plus a 111-page e-companion), measured on 2026-11-18. The author then set the target for the initial submission at about 40 pages (38 to 42), and the #188 cut of 2026-11-18 brought the manuscript to 42 pages (38 of text and 4 of references) with a 120-page e-companion; what moved to the Internet Appendix is listed in `../TO_VERIFY.md`. The final prose pass (#189, 2026-11-18) left both counts unchanged (42 and 120 pages), with about three lines of slack on the last page of text, and regenerated `replication/equations.tex` for the equation placement after #188. Re-measured for the submission materials (#190, 2026-11-19): blind manuscript 42 pages, e-companion 120 pages, identified single PDF 142 pages, with no unresolved reference or citation in any of them. The 32-page cap applies only to an invited revision. Re-measure
with `just render-blind` after every content change.

### Reference style decision (2026-07-25)

Both builds use `paper/econometrica.bst`. INFORMS house style is alphabetical
author–year, which `econometrica.bst` satisfies, but the two are not typographically
identical (INFORMS: `Bertsimas D, Sim M (2004) The price of robustness. Oper. Res.
52(1):35–53.`; econometrica: `Bertsimas, D., and M. Sim (2004): "The Price of
Robustness," Operations Research, 52, 35–53.`). No INFORMS `.bst` ships with TeX Live,
and INFORMS applies its house style in copyediting after acceptance. **Decision:** submit
with `econometrica.bst`; if the editorial office asks for the house style at submission,
drop `informs2014.bst` (from the INFORMS LaTeX author package) into `paper/` and change
`biblio-style` in `paper/_quarto.yaml`.

### Portal checklist (Management Science)

- [ ] Choose the department (Finance vs. Operations Management — see
      `../reports/review_report_consolidated.md`; the cover letter suggests Finance)
- [ ] Upload the two blind PDFs; **do not** upload a title page
- [ ] Suggested reviewers (the July guideline fetch said five; a September
      web summary said six — confirm the count on the portal)
- [ ] Three associate editor nominations
- [ ] Submitting author's ORCID
- [x] Abstract pasted into the cover letter (`cover-letter.md`; current as of 2026-11-19, kept in sync by `tests/test_paper_metadata.py`)
- [ ] Paste the abstract into the portal's abstract field (same text, 250 words)
- [ ] Attach the referee-facing proof package `replication/replication-package.zip`
      (`just build-replication-package`) as supplementary material, since the cover
      letter says the submission includes it; check the portal's accepted file types
- [ ] AI-use disclosure: the acknowledgments footnote (`paper/index.qmd:thanks`) is
      stripped from the blind manuscript, so the generative-AI statement in
      `ai-disclosure.md` must go into the cover letter / portal disclosure field instead
- [ ] Keywords (3–5, as printed on the manuscript title page): real options; irreversible
      capacity investment; artificial intelligence; duopoly entry timing; default risk
- [ ] JEL codes (from `paper/keywords.tex`): C73, D25, G31, G32, G33, L13, O33
      (C73 = stochastic and dynamic games, for the entry equilibrium; D25 =
      intertemporal firm choice: investment, capacity, financing)
- [ ] INFORMS subject classifications (proposed; confirm the exact wording against the
      portal's list at submission time):
      *Finance: capital budgeting* (primary);
      *Games/group decisions: noncooperative*;
      *Dynamic programming/optimal control: applications*;
      *Industries: computers/electronics*;
      secondary, if a fifth is allowed: *Finance: capital structure*

## Target journal ladder (decided 2026-07-03, confirmed 2026-11-19)

One or two shots at the top of the list before moving down:

1. Management Science
2. Journal of Financial and Quantitative Analysis (JFQA)
3. Review of Finance
4. Review of Corporate Finance Studies (RCFS)
5. Journal of Corporate Finance
6. Journal of Economic Dynamics and Control (JEDC)
7. Journal of International Financial Markets, Institutions and Money (JIFMIM)
8. International Review of Financial Analysis (IRFA)

**Confirmed 2026-11-19 (Vincent, issue #190).** The ladder is unchanged: Management Science, then JFQA, then Review of Finance, then the rest of the list above. The review of 2026-11-01 (consolidated comment C18) expected a reject or reject-and-resubmit at the first three in the paper's form at that time, because its first objection was to the model rather than the venue, and named JEDC as the fallback if the structure were kept. That objection was about the pre-revision model; the #175 revision addresses it (the exact model of record, with the duopoly's first investment at X_L). The JEDC fallback is therefore recorded only as a later option after the top of the ladder, where JEDC already sits, not as a reason to move it up.

## Remaining before submission (see issue #95)

- [ ] Final human review
- [ ] Insert AI disclosure into the manuscript per target journal's format
- [ ] Check the guide for authors of the target journal
- [ ] Adapt the cover letter to the target journal
- [ ] Work through the portal checklist above and run `just render-blind`
- [ ] Submit
