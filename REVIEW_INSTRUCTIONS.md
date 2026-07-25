# Review Instructions

You are reviewing a research project and its accompanying codebase. Your task is to produce a detailed review report covering both **code validation** and **paper quality**. Read these instructions fully before beginning.

---

## Project Overview

**Title:** "Investing in Artificial General Intelligence"

**Author:** Vincent Grégoire (HEC Montréal)

**Research question:** How should a frontier AI laboratory optimally time, size, and allocate an irreversible capacity investment between training (future capability) and inference (current revenue) under demand uncertainty, regime switching, duopoly competition, and endogenous default risk?

**Methodology:** The paper builds a unified real options model in several layers:

1. **Single-firm benchmark:** Analytical solution for optimal investment trigger, capacity, and training fraction with regime-switching demand (absorbing high state arriving with Poisson intensity λ) and diminishing returns calibrated to AI scaling laws.
2. **Duopoly with default risk:** Extends the benchmark to two-firm preemption competition with Tullock contest revenue, endogenous (Leland-style) default boundaries, and credit risk. The leader invests first and enjoys a monopoly phase until follower entry.
3. **Calibration:** Parameters calibrated to publicly available data on four stylized AI lab archetypes: frontier lab (Anthropic-like), platform (OpenAI-like), hyperscaler (Google-like), and compute racer (xAI-like).
4. **Valuation and Dario's dilemma:** Value decomposition, credit risk analysis, and an asymmetric belief-mismatch cost analysis showing that underinvestment is costlier in expected value than overinvestment, while overinvestment carries higher tail (default) risk.

**Key model features:**
- Training-inference allocation (φ): firms split capacity between inference (L-regime revenue) and training (H-regime competitive position)
- K* is independent of φ (separable FOCs); φ* is interior and determined by maximizing A_eff
- Faith-based survival: training raises A_eff through the H-regime continuation value, lowering the default boundary
- First-passage (barrier) default probability, consistent with Leland-style default mechanism
- Dario's dilemma: asymmetric cost of belief mismatch about λ (W''' > 0 → underinvestment costlier). Note this is labeled **Numerical Finding 1**, not a proposition — the paper deliberately separates analytical from numerical results (see `@tbl-result-taxonomy` in Internet Appendix A).

**Proof verification:** The closed-form algebra of Propositions 1–3 is machine-checked in Lean 4/Mathlib under `lean/`. Internet Appendix A opens with a paragraph stating the scope of that verification. Part of your job is to check that this claim is neither overstated nor understated (see checklist §1).

**Target journals:** The submission plan (`submission/README.md`, decided 2026-07-03) is a ladder headed by **Management Science**, then JFQA, Review of Finance, RCFS, Journal of Corporate Finance, JEDC, JIFMIM, IRFA. Earlier drafts targeted JF/RFS/Econometrica; that framing is obsolete. Review the paper against the standards of a strong general-interest management-science / finance journal, and say explicitly if you think the paper is under- or over-aimed relative to this ladder.

---

## Repository Structure

```
ai-lab-investment/
├── src/ai_lab_investment/       # Core source code
│   ├── __main__.py              # Entry point
│   ├── pipeline.py              # Hydra-decorated pipeline orchestrator
│   ├── exceptions.py            # Custom exceptions
│   ├── models/                  # Economic models
│   │   ├── base_model.py        # Single-firm benchmark (simple + full φ-aware modes)
│   │   ├── duopoly.py           # Duopoly with default risk and preemption
│   │   ├── parameters.py        # Parameter definitions and calibration
│   │   ├── symbolic_duopoly.py  # SymPy symbolic verification of duopoly ODEs
│   │   └── valuation.py         # Credit risk, Dario's dilemma, growth decomposition
│   ├── calibration/             # Calibration
│   │   ├── data.py              # Data loading and preprocessing
│   │   └── revealed_beliefs.py  # Revealed beliefs inference algorithm
│   ├── figures/                 # Figure generation
│   │   ├── paper.py             # All 11 paper figures (primary source of truth)
│   │   ├── phase1.py            # Exploratory base model figures (pipeline only)
│   │   ├── phase2.py            # Exploratory duopoly figures (pipeline only)
│   │   ├── phase4.py            # Exploratory calibration figures (pipeline only)
│   │   └── phase5.py            # Exploratory valuation figures (pipeline only)
│   └── utils/
│       ├── directories.py       # Directory path resolution
│       └── files.py             # Timestamped file naming
├── tests/                       # 229 tests across 6 test files
│   ├── test_base_model.py
│   ├── test_calibration.py
│   ├── test_duopoly.py
│   ├── test_parameters.py
│   ├── test_symbolic_duopoly.py
│   └── test_valuation.py
├── paper/                       # Research paper (Quarto -> PDF)
│   ├── index.qmd                # Main file; includes all sections
│   ├── _introduction.qmd        # Motivation, contribution; includes _literature.qmd
│   ├── _model.qmd               # Model: demand, technology, single-firm, duopoly
│   ├── _calibration.qmd         # Calibration to four AI lab archetypes
│   ├── _valuation.qmd           # Value decomposition, credit risk, Dario's dilemma, equity sensitivity
│   ├── _discussion.qmd          # Welfare, testable predictions, policy, static-φ bias, limitations
│   ├── _conclusion.qmd
│   ├── _literature.qmd          # Literature review (included within introduction)
│   ├── _appendix.qmd            # INTERNET APPENDIX. A: Proofs (Props 1-3 + Numerical Finding 1, result taxonomy), B: numerical verification methods, C: calibration details and data sources, D: parameter sensitivity, E: robustness (Cournot discussion, fixed-pie, dynamic φ, duopoly dilemma, 3-regime)
│   ├── generate_figures.py      # Thin wrapper: applies styles and saves output
│   ├── references.bib           # BibTeX references (57 entries)
│   ├── reference_corrections.md # Audit trail of bibliography corrections
│   └── figures/                 # Generated figures (*.pdf, *.png; 11 figures, 10 used in paper)
├── lean/                        # Lean 4 / Mathlib formalization of the closed forms
│   ├── README.md                # Theorem-to-paper-result map, scope and limitations
│   └── AILabProofs/             # Basic, EulerODE, CharacteristicRoots,
│                                #   Proposition1, Proposition1Phi, Proposition2, Duopoly
├── submission/                  # Journal submission materials
│   ├── README.md                # Target-journal ladder and pre-submission checklist
│   ├── cover-letter.md, ai-disclosure.md
│   └── replication/             # Referee-facing package (Lean + equation listing + Dockerfile)
├── notebooks/
│   └── model_derivation.ipynb   # SymPy derivation notebook (8 sections + summary + completeness audit)
├── references/                  # Lit review, data compendium, background notes (source material)
├── reports/                     # Review reports (yours goes here; do not read others)
├── slides/                      # Presentation slides (out of review scope)
├── video/                       # Manim explainer + walkthrough videos (out of review scope)
├── docs/                        # MkDocs documentation site (out of review scope)
├── conf/config.yaml             # Hydra pipeline configuration
├── CLAUDE.md                    # Project instructions (includes AGENTS.md)
├── AGENTS.md                    # Detailed agent instructions
├── justfile                     # Task runner (just check, just test, etc.)
└── pyproject.toml               # Python project metadata
```

---

## Review Scope

Your review covers two areas, weighted roughly equally.

### Part 1: Code Validation

Verify that the implementation is correct, the tests are meaningful, and the code faithfully implements the mathematics described in the paper. This includes the Lean formalization in `lean/`: whether it proves what the paper says it proves, and whether the paper's description of its scope is accurate.

### Part 2: Paper Review

Evaluate the paper as a referee would for a leading management-science or finance journal (Management Science, JFQA, Review of Finance — see the ladder above).

---

## Detailed Review Checklist

Work through every section below. For each item, state whether it **passes**, **has issues** (describe them), or **could not be verified** (explain why). Be specific: cite file paths, line numbers, equation numbers, proposition numbers, and test names.

### 1. Mathematical Correctness

- [ ] **Propositions vs. code**: For each proposition in the paper (`_model.qmd`, `_appendix.qmd`), locate the corresponding implementation in the source code. The paper has three propositions: Proposition 1 (optimal K*, φ*), Proposition 2 (default boundary properties, faith-based survival), and Proposition 3 (preemption equilibrium). Verify that the formulas in code match the formulas in the paper exactly. Flag any discrepancies, even notational ones.
- [ ] **Proofs**: Read the proofs in `_appendix.qmd`. Check logical completeness — are all steps justified? Are boundary/edge cases handled? Pay particular attention to: (a) the separability of K* and φ* in Proposition 1, (b) the two-channel derivative ∂X_D/∂λ in Proposition 2(ii) including the markup channel and the exact net threshold φ̃, and (c) the Dario's dilemma Taylor expansion sign argument in Numerical Finding 1.
- [ ] **Result taxonomy**: `@tbl-result-taxonomy` (Internet Appendix A) classifies each result as closed-form, implicit-function, analytical, computational, or numerical. Verify each classification is honest — in particular that nothing labeled "closed-form" or "analytical" actually rests on numerical verification, and that the analytical/computational split in Proposition 3(i)–(ii) matches what the proofs and code actually establish.
- [ ] **Lean verification**: The `lean/` project machine-checks the closed-form algebra. Build it (`cd lean && lake exe cache get && lake build`) or, if you cannot, say so. Then assess: (a) do the Lean theorems listed in `lean/README.md` actually correspond to the paper results they claim to (spot-check at least three against the paper's equations); (b) is the scope paragraph at the top of Internet Appendix A accurate — does it correctly disclaim the HJB derivation, the optimal-stopping verification theorem, the A₁ = 0 exactness argument, and the numerical results; (c) are any theorems vacuous or trivially weaker than the paper's claim (e.g. hypotheses so strong the statement is not the paper's result)? Confirm no `sorry` and only the three standard axioms.
- [ ] **Two model modes**: The code has two modes — *simple* (no φ: `installed_value()`, `optimal_trigger_and_capacity()`) and *full* (with φ: `optimal_trigger_capacity_phi()`, `installed_value_with_phi()`). Verify both are internally consistent and that the paper uses the full mode for all reported results.
- [ ] **Numerical methods**: In `calibration/revealed_beliefs.py` and the optimization routines in `base_model.py` and `duopoly.py`, verify that numerical algorithms (root-finding, Nelder-Mead optimization, Brent's method) are correctly implemented. Check convergence criteria and tolerances.
- [ ] **Parameter consistency**: Verify that default parameter values in `models/parameters.py` match the calibration values stated in `_calibration.qmd` and the baseline results table in `_appendix.qmd`. Check units and scaling.
- [ ] **Regime switching**: Verify the regime-switching demand process implementation in `models/base_model.py` matches the specification in `_model.qmd`. Check transition intensities, drift, volatility, and the absorbing-state assumption for regime H.
- [ ] **Default probability**: Verify that the first-passage (barrier hitting) probability in `valuation.py` is correctly implemented and matches the formula in `_valuation.qmd`.

### 2. Code Quality and Testing

- [ ] **Test coverage**: Run `just test` (or `uv run pytest --cov`) and report coverage. Identify any untested functions or branches in the models.
- [ ] **Test meaningfulness**: Read through the 6 test files. Are the tests checking economically meaningful properties (e.g., option values are positive, triggers decrease with volatility, default boundary lies below investment trigger, K* is independent of φ)? Or are they trivial/tautological?
- [ ] **Paper-number tests**: Several tests pin numbers reported in the paper (e.g. `TestAppendixERobustness::test_duopoly_dilemma_table` and `::test_dynamic_phi_table` in `test_valuation.py`). Verify the pinned values match the tables actually printed in `_appendix.qmd`, and that the tolerances are tight enough to catch a real regression.
- [ ] **Edge cases**: Are boundary conditions tested? (e.g., zero volatility, lambda = 0 or very large lambda, leverage = 0, φ at boundaries)
- [ ] **Numerical stability**: Check for potential numerical issues: division by zero guards, overflow in exponentials, convergence failures in optimization.
- [ ] **Code organization**: Is the code well-structured? Are responsibilities cleanly separated between modules? Any code smells or unnecessary complexity?
- [ ] **Reproducibility**: Can results be reproduced by running `just run-pipeline`? Are random seeds set where needed?

### 3. Paper Content Review

Review the paper as a referee for a leading management-science / finance journal (see the target ladder above). Address each sub-item.

#### 3a. Structure and Argument

- [ ] **Motivation**: Is the introduction compelling? Does it clearly articulate the core economic question (timing, sizing, and allocating irreversible capacity under regime uncertainty), the gap in existing theory, and the key insight (training-survival channel)?
- [ ] **Literature positioning**: Does the paper adequately situate itself relative to the real options literature (Dixit & Pindyck, McDonald & Siegel), strategic investment games (Grenadier, Huisman & Kort), R&D race models (Loury, Reinganum), structural credit risk (Leland, Merton), and AI economics literature? Are there important omissions?
- [ ] **Model building**: Does the progression from single-firm to duopoly feel natural and well-motivated? Is the duopoly focus (rather than N-firm) adequately justified?
- [ ] **Key assumptions**: Are the maintained assumptions of Assumption 1 (A1–A4) clearly stated and their economic content explained? Is the simplified L-regime option value (A3, the A₁ = 0 argument) convincingly justified?
- [ ] **Conclusion**: Does it summarize findings effectively without overclaiming?
- [ ] **Internet Appendix split**: A large amount of material sits in the Internet Appendix (all proofs, numerical methods, calibration details, all robustness). Is the split defensible for a referee — is anything load-bearing for the main argument buried there, and is anything in the main text that belongs in the appendix?

#### 3b. Writing Quality

- [ ] **Clarity**: Is the writing clear and precise throughout? Flag any passages that are confusing, vague, or poorly worded.
- [ ] **Notation**: Is mathematical notation consistent throughout the paper? Are all symbols defined before use?
- [ ] **Length and focus**: Is the paper appropriately scoped for its target journals? Any sections that feel padded or underdeveloped?
- [ ] **Abstract, keywords, JEL codes**: Does the abstract concisely convey the contribution, methodology, and key results? Are the keywords and JEL codes on the title page appropriate?

#### 3c. Journal Fit

- [ ] **Contribution significance**: Is the contribution substantial enough for Management Science (the top of the ladder)? If not, which rung of the ladder in `submission/README.md` is the realistic entry point?
- [ ] **Methodological rigor**: Does the paper meet the technical standards of these journals?
- [ ] **Formatting and conventions**: Does the paper follow the conventions of its target journals (currently rendered with an Econometrica bibliography style via Quarto/LuaLaTeX; appropriate formality, front matter, disclosure)?
- [ ] **AI-use disclosure**: The paper is openly AI-assisted (`thanks` footnote in `index.qmd`, `submission/ai-disclosure.md`, `ai_workflow.md`). Assess whether the disclosure is adequate and appropriately placed for the target journals, and whether it is likely to affect reception.
- [ ] **Which journal fits best**: Based on the paper's strengths, recommend the most appropriate target journal and explain why — agreeing or disagreeing with the existing ladder.

### 4. Figures

- [ ] **Paper figures**: Review the 11 figures in `paper/figures/` (one PDF + one PNG each), generated by `paper/generate_figures.py` (which delegates all computation to `src/ai_lab_investment/figures/paper.py`). Ten are referenced in the paper; `fig_sample_paths` is used in the slides only — confirm this and flag any other figure that is generated but never cited. For each figure, verify: (a) it accurately represents the underlying model output, (b) axes labels and legends are correct, (c) it is publication-quality (fonts, resolution, layout). List any issues.
- [ ] **Code-figure consistency**: Spot-check at least 3 figures by tracing the data from model code through `figures/paper.py` to the final plot. Verify the pipeline is correct.

### 5. Calibration and Results

- [ ] **Parameter values**: Are calibrated parameter values reasonable and well-sourced? Check against the sources cited in `_calibration.qmd` (now given as URL footnotes) and the parameter/data-source tables at the top of the Internet Appendix. Note that the archetype figures are as of Q4 2025–Q1 2026 and that the xAI-like archetype is calibrated standalone, pre-SpaceX acquisition — check that this framing is applied consistently.
- [ ] **Sensitivity and robustness**: Does the paper adequately explore sensitivity to key parameters (volatility, arrival rate, revenue elasticity, cost convexity, cost of capital; Internet Appendix D) and the robustness exercises in Internet Appendix E — ±25% parameter perturbations truncated to the admissible region, the qualitative Cournot discussion and the quantified fixed-pie contest, the two-period dynamic-φ extension, the one-sided duopoly Dario's dilemma, and the three-regime remark? Flag any robustness claim that is asserted rather than computed (the Cournot and three-regime discussions are explicitly qualitative — is that acceptable?).
- [ ] **Comparative statics**: Verify that reported comparative statics (how triggers/values change with parameters) are consistent with economic intuition and the model's predictions.
- [ ] **Dario's dilemma results**: Are the value loss percentages and default probabilities under belief mismatches correctly computed and internally consistent? Does the Taylor expansion sign argument (Numerical Finding 1) match the numerical results, single-firm and duopoly?
- [ ] **Growth decomposition**: Is the decomposition of firm value into installed capacity value and growth option value correctly computed and reported?
- [ ] **Normalization caveat**: The model is unit-free ($c = 1$), so levels of $X$ and $K$ are not interpretable and only ratios/percentages carry content. Check that the paper never draws an economic conclusion from a level, and that the illustrative mapping to CapEx in `_calibration.qmd` is presented as illustration only.

---

## Output Instructions

### Report Format

Write your review as a single Markdown file with the following structure:

```markdown
# Review Report: AI Lab Investment

**Reviewer:** [Your identifier]
**Date:** [YYYY-MM-DD]

## Executive Summary
[2-3 paragraph overview of findings. Overall assessment: is the code correct? Is the paper ready for submission?]

## Part 1: Code Validation
### 1. Mathematical Correctness
[Findings for each checklist item]

### 2. Code Quality and Testing
[Findings for each checklist item]

## Part 2: Paper Review
### 3. Paper Content Review
[Findings for each sub-section]

### 4. Figures
[Findings for each checklist item]

### 5. Calibration and Results
[Findings for each checklist item]

## Summary of Issues
### Critical Issues
[Issues that must be fixed before submission]

### Major Issues
[Significant concerns that should be addressed]

### Minor Issues
[Suggestions for improvement]

## Overall Recommendation
[Submit as-is / Revise and resubmit / Major revision needed]
[Recommended target journal with justification]
```

### Report Location

Save your report to the `reports/` directory at the repository root with the filename:

```
reports/review_report_[YOUR_IDENTIFIER].md
```

Replace `[YOUR_IDENTIFIER]` with a short, unique identifier for yourself (e.g., `claude`, `codex`, `gemini`). Use lowercase with underscores.

**Before writing your report**, list files in `reports/` to check existing filenames and avoid overwriting another reviewer's report. Do NOT read the contents of any existing reports — only check filenames to avoid collisions.

### Important Constraints

- **Do not read other reports.** You must form your own independent assessment. Only list filenames in `reports/` to avoid naming collisions.
- **Be specific.** Cite file paths, line numbers, equation numbers, proposition numbers, and test names. Vague criticism is not useful.
- **Be constructive.** For every issue identified, suggest a concrete fix or improvement where possible.
- **Be honest.** If something is beyond your ability to verify (e.g., you cannot run the code), say so explicitly rather than guessing.
