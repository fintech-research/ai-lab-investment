# Submission materials (issue #95)

Documents supporting journal submission of *Capacity, Training, and Default in the Race to Artificial General Intelligence*.

- `cover-letter.md` — letter to the editor, currently targeted at Management Science (addressed generically to "Dear Editor"); swap the journal name and fit paragraph to retarget.
- `ai-disclosure.md` — declaration of generative AI use: a short-form Elsevier-style statement (to be inserted in the manuscript before the references for Elsevier targets) and a detailed long-form disclosure.
- `replication/` — referee-facing machine-checked proof package (issue #108): a README for referees, `extract_equations.py` (generates `equations.tex`, the complete labeled equation listing, from the paper sources), and `just build-replication-package` to assemble the zip (Lean project + README + equations listing).

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
3–5 keywords, abstract ≤ 250 words (~178), alphabetical author–year references,
supplementary material as a separate e-companion.

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
      `../reports/review_report_consolidated.md`)
- [ ] Upload the two blind PDFs; **do not** upload a title page
- [ ] Five suggested reviewers
- [ ] Three associate editor nominations
- [ ] Submitting author's ORCID
- [ ] Abstract pasted into the cover letter (`cover-letter.md`)
- [ ] AI-use disclosure: the acknowledgments footnote (`paper/index.qmd:thanks`) is
      stripped from the blind manuscript, so the generative-AI statement in
      `ai-disclosure.md` must go into the cover letter / portal disclosure field instead
- [ ] Keywords (3–5, as printed on the manuscript title page): real options; irreversible
      capacity investment; artificial intelligence; duopoly preemption; default risk
- [ ] JEL codes (from `paper/keywords.tex`): C73, D25, G31, G32, G33, L13, O33
      (C73 = stochastic and dynamic games, for the preemption equilibrium; D25 =
      intertemporal firm choice: investment, capacity, financing)
- [ ] INFORMS subject classifications (proposed; confirm the exact wording against the
      portal's list at submission time):
      *Finance: capital budgeting* (primary);
      *Games/group decisions: noncooperative*;
      *Dynamic programming/optimal control: applications*;
      *Industries: computers/electronics*;
      secondary, if a fifth is allowed: *Finance: capital structure*

## Target journal ladder (decided 2026-07-03)

One or two shots at the top of the list before moving down:

1. Management Science
2. Journal of Financial and Quantitative Analysis (JFQA)
3. Review of Finance
4. Review of Corporate Finance Studies (RCFS)
5. Journal of Corporate Finance
6. Journal of Economic Dynamics and Control (JEDC)
7. Journal of International Financial Markets, Institutions and Money (JIFMIM)
8. International Review of Financial Analysis (IRFA)

## Remaining before submission (see issue #95)

- [ ] Final human review
- [ ] Insert AI disclosure into the manuscript per target journal's format
- [ ] Check the guide for authors of the target journal
- [ ] Adapt the cover letter to the target journal
- [ ] Work through the portal checklist above and run `just render-blind`
- [ ] Submit
