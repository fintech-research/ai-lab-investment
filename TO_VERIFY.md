# TO_VERIFY

Items from the prose-review pass (`reports/prose_review_claude.md`, branch
`prose-review-fixes`) that need a human check. Each was raised by an editing
agent that could not resolve it without recomputing a number, opening an
exhibit, or consulting a source. Delete an entry once verified.

## Sources and citations

- [ ] **\$121B 2025 hyperscaler bond issuance** (`_calibration.qmd`, opening
  paragraph). No source exists anywhere in the repo; Internet Appendix C covers
  only the xAI and OpenAI debt. Currently attributed as "Press reports place
  ...". Needs a footnote or removal.
- [ ] **Hassabis timeline range** (`_calibration.qmd`, Demand Process). The
  $\lambda \approx 0.10$–$0.15$ range attributed to Hassabis is still uncited
  while Amodei is cited. Find the source in Zotero or drop the comparison.
- [ ] **Microsoft CFO and Jensen Huang statements** and the ">40% of AI revenue
  is inference by late 2025" figure (`_appendix.qmd`, Internet Appendix C,
  $\hat{\phi}$ evidence block). Now marked as trade-press reports rather than
  filings, but still lack a source, date, and venue. "AI revenue" is also
  undefined (whose, measured how).
- [ ] **xAI CapEx row in `@tbl-sources`**. Labelled "press reports", but the
  body says CapEx is not separately disclosed for that archetype. Reconcile.
- [ ] **Four cite keys dropped from the bibliography.** The literature review's
  catalogue footnotes were cut, so `@bloom2009impact`, `@jovanovic2005general`,
  `@katz1986technology`, and `@farrell1986installed` are no longer cited
  anywhere and have dropped out of the reference list. The entries remain in
  `references.bib`. Confirm you are happy to lose them. (`@bloom2020ideas` is a
  different key and is still cited.)

## Numbers that need an exhibit check

- [ ] **Cooperative/cartel benchmark** (`_discussion.qmd`, Welfare and
  Overinvestment). The claim that industry capacity may exceed the cooperative
  level has no exhibit; grep finds "cartel"/"cooperative" only in that section.
  It is now written as an open question. If a cartel-capacity computation
  exists in the code but is unexhibited, replace the sentence with the actual
  comparison.
- [ ] **`@tbl-duopoly-dilemma` leverage level.** The added note does not state
  $\ell$, because the text never does. If the exercise is the $\ell = 0$ case,
  add it.
- [ ] **26.2% / 5.6% versus 26% / 6%.** Both roundings are now in use:
  `_valuation.qmd` quotes 26.2/5.6 where the 4.7 loss ratio needs that
  precision, and 26/6 elsewhere. Consistent, but confirm both trace to the same
  exhibit.
- [ ] **Rounding of 2.64% to 2.6%** (`_appendix.qmd`, Internet Appendix B) and
  the 97.4%/2.6% pair in the same sentence. Confirm the exported numbers
  support one decimal.
- [ ] **Cost-scale invariance justification** (`_appendix.qmd`, Internet
  Appendix E). The claim that the four sweep objects are invariant to $\delta$
  and $c$ is now attributed to homogeneity of the value functions in the cost
  scale. Confirm this is the mechanism in `robustness.py`.
- [ ] **`@tbl-elasticities` "$\approx 0$" rule.** The new note says those
  entries round to zero at the displayed precision. Confirm that is what the
  generator does.
- [ ] **`fig_growth_decomposition` band order.** The new non-colour cue asserts
  assets-in-place is the lower band and the capacity gap the upper band.
  Confirm against the figure.
- [ ] **Caption procedural numbers in `_model.qmd`** (60-point $\lambda$ grid on
  $[0.01, 0.80]$; 40 leverage levels on $[0.05, 0.65]$; 30 $\sigma$ points).
  Read from `figures/paper.py` and will drift if the generators change.

## Editorial calls to confirm

- [ ] **43% preemption discount in the introduction.** Now qualified as "at
  baseline volatility, and conditional on the convention that the leader
  installs the monopoly-phase optimal scale". The alternative is to drop the
  number from the introduction and keep only the sign.
- [ ] **`fig-growth-decomposition` label versus prose.** The prose now
  standardizes on "the scale-gap index $g$", and Internet Appendix G insists the
  exhibit is *not* a growth-option decomposition, but the Quarto label and the
  generated file are still `fig_growth_decomposition`. Renaming needs a
  `paper.py` edit plus a figure regeneration.
- [ ] **Internet Appendix A cross-reference to the conventions.** It says the
  four solution conventions "are also collected immediately before the
  statement of Proposition 3". That location is now a one-sentence pointer
  naming the four rather than a full restatement. Still accurate, but a
  co-author may want it softened.

## Codex review round (2026-09-07), umbrella #135

Author-only checks raised while verifying `reports/review_report_codex_20260907.md`. Each is also referenced from the sub-issue in parentheses.

- [ ] **\$660--690B 2026 spending aggregate** (`_introduction.qmd`, opening paragraph). The footnote cites only Amazon, Alphabet, and Microsoft guidance, which cannot sum to a "laboratories and their compute partners" total. State the aggregation or cite the source that made it. (#144)
- [ ] **Executive quotations in the introduction**: Pichai (Alphabet Q2 2024 call), Huang (GTC 2025, "easily 100x"), Musk (the x.com status ID `2025124840806514916` looks implausible for a 2025 post), LeCun/PYMNTS wording, Amodei/Dwarkesh wording and ellipsis, Stargate figures. Check exact wording and add URLs where missing. (#144)
- [ ] **OpenAI \$3.7B/\$12.5B revenue** (`_appendix.qmd`, Internet Appendix C). The cited openai.com post gives ARR of \$2B/\$6B/\$20B+, not these figures. Supply the press source or switch to the ARR series. (#144)
- [ ] **Epoch AI quotation** (`_appendix.qmd`, Internet Appendix C). The sentence in quotation marks paraphrases Epoch's wording; Epoch's \$2B research figure rests on an assumed two-year amortization of press reports. (#144)
- [ ] **Management Science reviewer count.** `submission/README.md` says five suggested reviewers; web summaries of the current guidelines say six and three AEs. INFORMS pages returned 403 to automated fetches; confirm on the portal. (#148)
- [ ] **Decision: C2 envelope re-solve.** A preliminary re-solve of the piecewise benchmark with the optimized post-switch scale finds no finite pre-switch trigger at baseline and a 6.9% policy loss instead of 2.6%. Needs independent reproduction and a decision on relabel vs re-solve before the appendix numbers are rewritten. (#136)
- [ ] **Decision: cover letter** L24 verification claim, L26 AI-upload invitation, drafting-speed paragraph. Flagged again by Codex after the July decision to keep them. (#148)
