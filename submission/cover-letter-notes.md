# Cover letter: editorial notes (not part of the submitted letter)

*Editorial notes from the consolidated pre-submission review (2026-07-25) — flagged for the author's consideration; the letter text below is intentionally left unchanged:*

- *The paragraph granting referees permission to upload the manuscript to ChatGPT/Claude sits in tension with Management Science's AI policy, which warns review-team members against uploading submitted manuscripts; an author-side invitation may put reviewers in conflict with journal procedure even though the paper is publicly posted.*
- *The Lean paragraph's "existence and uniqueness of the preemption trigger" and "no unproven assumptions" state more than the paper's own Internet Appendix scope paragraph: the preemption lemmas are generic IVT/concavity results whose model-specific hypotheses (endpoint sign, ℓ = 0 concavity) are supplied numerically, and "no unproven assumptions" conflates "no Lean placeholders" with "no economic hypotheses." A referee who diffs the letter against the appendix will notice.*
- *Leading with the "…in Four Days" blog title in the letter body may invite a desk-level prior of shallowness; the disclosure document and repository link could carry that reference instead.*
- *Management Science asks that the cover letter include the manuscript's abstract; it is not currently included.*

*Codex pre-submission review (2026-09-07, issue #148) raised the same points again and asked that the letter carry no claim the Internet Appendix qualifies, no placeholders, and the abstract. What changed in `cover-letter.md` on 2026-09-08:*

- *The Lean paragraph now describes the verification as the appendix does: conditional algebra and calculus, with the preemption lemmas' model-specific hypotheses supplied numerically; "no unproven assumptions" replaced by "no unproven placeholders".*
- *The abstract is included, as the journal requests.*
- *The editorial notes moved here.*

*Deliberately unchanged, pending the author's decision (see `TO_VERIFY.md`): the paragraph granting referees permission to upload the manuscript to AI services, and the paragraph on the project's AI-assisted genesis, both kept in July 2026 as intentional.*

*Submission materials for the revised paper (2026-11-19, issue #190, after the four-report review of 2026-11-01 and the revision in umbrella #171). What changed in `cover-letter.md`:*

- *The abstract is the one in `paper/index.qmd` (250 words); `tests/test_paper_metadata.py` now fails if the letter's quotation drifts from it.*
- *The contribution paragraph follows the revised introduction: the model is solved in its primitives; competition, not the single firm's own option, brings investment forward of the switch, with a second-mover advantage at the date of first investment and the three caveats on the equilibrium; the closed-form training fraction; faith-based survival with the shutdown boundary that exists without debt; Dario's dilemma in three metrics (32% against 1.3% in levels, 13% at the same proportion, about the same in expected years, and the five-year tail comparison); the calibration as a mapping of assigned allocations into implied beliefs, not evidence about firms. "Preemption", "semi-analytical", "stated pricing convention", and "conservative underinvestment / aggressive overinvestment" are gone, as in the paper. Every number is one the abstract or the introduction quotes.*
- *The proof paragraph was audited sentence by sentence against `lean/README.md` (consolidated comment C19i: "machine-checked" only next to a claim the Lean files cover). It now lists what the package covers as the README maps it, says "at most one root" for the follower's condition (`followerFoc_unique`), describes Corollary 1 as stated without the option to stop, says what is not formalized, and points to the cached numerical solutions shipped with the package. "The referee can therefore focus on the economics rather than the algebra" became "I hope this lets the referee spend less time on the algebra and more on the economics".*
- *Em-dashes removed (two in the fit paragraph, two in the SSRN paragraph); wording otherwise unchanged there and in the AI paragraphs, whose decision is still pending (see above and `TO_VERIFY.md`).*
