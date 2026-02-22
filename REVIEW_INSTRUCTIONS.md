# Review Instructions

You are reviewing a research project and its accompanying codebase. Your task is to produce a detailed review report covering both **code validation** and **paper quality**. Read these instructions fully before beginning.

---

## Project Overview

**Title:** "Investing in Intelligence: A Real Options Framework for AI Compute Infrastructure"

**Author:** Vincent Gregoire (HEC Montreal)

**Research question:** How should firms optimally invest in irreversible AI compute capacity under demand uncertainty, regime switching, strategic competition, and default risk — and what do observed investment decisions reveal about firms' private beliefs regarding transformative AI?

**Methodology:** The paper builds a unified real options model in several layers:

1. **Single-firm benchmark** (Phase 1): Analytical solution for optimal investment trigger and capacity with regime-switching demand and diminishing returns calibrated to AI scaling laws.
2. **Duopoly with default risk** (Phase 2): Extends the benchmark to two-firm competition with endogenous default boundaries and credit risk.
3. **N-firm sequential equilibrium** (Phase 3): Numerical backward-induction solution for N heterogeneous firms with dynamic training/inference allocation.
4. **Calibration** (Phase 4): Parameters calibrated to publicly available data on AI compute costs, scaling laws, and stylized firm characteristics.
5. **Revealed beliefs** (Phase 5): An inversion methodology that backs out firms' implied probability of transformative AI arrival from observable investment and market cap data.

**Target journals:** AER, JF, RFS, or Econometrica.

---

## Repository Structure

```
ai-lab-investment/
├── src/ai_lab_investment/       # Core source code
│   ├── __main__.py              # Entry point
│   ├── pipeline.py              # Hydra-decorated pipeline orchestrator
│   ├── models/                  # Economic models (Phases 1-3)
│   │   ├── base_model.py        # Single-firm benchmark
│   │   ├── duopoly.py           # Duopoly with default risk
│   │   ├── nfirm.py             # N-firm sequential equilibrium
│   │   ├── parameters.py        # Parameter definitions and calibration
│   │   └── valuation.py         # Revealed beliefs and growth decomposition
│   ├── calibration/             # Phase 4
│   │   ├── data.py              # Data loading and preprocessing
│   │   └── revealed_beliefs.py  # Revealed beliefs inference algorithm
│   ├── figures/                 # Figure generation by phase
│   │   ├── phase1.py            # Base model figures
│   │   ├── phase2.py            # Duopoly figures
│   │   ├── phase3.py            # N-firm figures
│   │   ├── phase4.py            # Calibration figures
│   │   └── phase5.py            # Valuation/revealed beliefs figures
│   └── utils/
│       ├── directories.py       # Directory path resolution
│       └── files.py             # Timestamped file naming
├── tests/                       # 145 tests across 6 test files
│   ├── test_base_model.py
│   ├── test_calibration.py
│   ├── test_duopoly.py
│   ├── test_nfirm.py
│   ├── test_parameters.py
│   └── test_valuation.py
├── paper/                       # Research paper (Quarto -> PDF)
│   ├── index.qmd                # Main file; includes all sections
│   ├── _introduction.qmd
│   ├── _model.qmd               # Environment, technology, single-firm benchmark
│   ├── _extensions.qmd          # N-firm equilibrium, training-inference allocation
│   ├── _calibration.qmd         # Calibration (demand, technology, stylized firms)
│   ├── _valuation.qmd           # Revealed beliefs methodology, growth decomposition
│   ├── _discussion.qmd          # Discussion and policy implications
│   ├── _conclusion.qmd
│   ├── _appendix.qmd            # Proofs (Propositions 1, 5)
│   ├── generate_figures.py      # Publication-quality figure generation (11 figures)
│   ├── references.bib           # BibTeX references
│   └── *.pdf / *.png            # Generated figures
├── slides/long-form/            # Conference slides (Quarto -> RevealJS)
│   ├── index.qmd
│   ├── _introduction.qmd
│   ├── _model.qmd
│   ├── _results.qmd
│   ├── _calibration.qmd
│   ├── _revealed_beliefs.qmd
│   └── _conclusion.qmd
├── conf/config.yaml             # Hydra pipeline configuration
├── plan.md                      # Detailed 5-phase research plan
├── CLAUDE.md                    # Project instructions and conventions
├── justfile                     # Task runner (just check, just test, etc.)
└── pyproject.toml               # Python project metadata
```

---

## Review Scope

Your review covers two areas, weighted roughly equally.

### Part 1: Code Validation

Verify that the implementation is correct, the tests are meaningful, and the code faithfully implements the mathematics described in the paper.

### Part 2: Paper and Presentation Review

Evaluate the paper as a referee would for a top finance or economics journal (AER, Econometrica, JF, RFS). Assess the slides for clarity and conference readiness.

---

## Detailed Review Checklist

Work through every section below. For each item, state whether it **passes**, **has issues** (describe them), or **could not be verified** (explain why). Be specific: cite file paths, line numbers, equation numbers, proposition numbers, and test names.

### 1. Mathematical Correctness

- [ ] **Propositions vs. code**: For each proposition in the paper (`_model.qmd`, `_extensions.qmd`, `_appendix.qmd`), locate the corresponding implementation in the source code. Verify that the formulas in code match the formulas in the paper exactly. Flag any discrepancies, even notational ones.
- [ ] **Proofs**: Read the proofs in `_appendix.qmd`. Check logical completeness — are all steps justified? Are boundary/edge cases handled?
- [ ] **Numerical methods**: In `models/nfirm.py` and `calibration/revealed_beliefs.py`, verify that numerical algorithms (root-finding, backward induction, fixed-point iteration) are correctly implemented. Check convergence criteria and tolerances.
- [ ] **Parameter consistency**: Verify that default parameter values in `models/parameters.py` match the calibration values stated in `_calibration.qmd`. Check units and scaling.
- [ ] **Regime switching**: Verify the regime-switching demand process implementation in `models/base_model.py` matches the specification in `_model.qmd`. Check transition intensities, drift, and volatility handling.

### 2. Code Quality and Testing

- [ ] **Test coverage**: Run `just test` (or `uv run pytest --cov`) and report coverage. Identify any untested functions or branches in the models.
- [ ] **Test meaningfulness**: Read through the 6 test files. Are the tests checking economically meaningful properties (e.g., option values are positive, triggers decrease with volatility, default boundary lies below investment trigger)? Or are they trivial/tautological?
- [ ] **Edge cases**: Are boundary conditions tested? (e.g., zero volatility, single firm in N-firm model, lambda = 0 or very large lambda)
- [ ] **Numerical stability**: Check for potential numerical issues: division by zero guards, overflow in exponentials, ill-conditioned matrices, convergence failures.
- [ ] **Code organization**: Is the code well-structured? Are responsibilities cleanly separated between modules? Any code smells or unnecessary complexity?
- [ ] **Reproducibility**: Can results be reproduced by running `just run-pipeline`? Are random seeds set where needed?

### 3. Paper Content Review

Review the paper as a referee for a top journal. Address each sub-item.

#### 3a. Structure and Argument

- [ ] **Motivation**: Is the introduction compelling? Does it clearly articulate why this problem matters and what gap the paper fills?
- [ ] **Literature positioning**: Does the paper adequately situate itself relative to the real options literature (Dixit & Pindyck, McDonald & Siegel), strategic investment games (Grenadier, Weeds), and AI economics literature? Are there important omissions?
- [ ] **Model building**: Does the progression from single-firm to duopoly to N-firm feel natural and well-motivated? Is each extension clearly justified?
- [ ] **Identification**: Is the revealed beliefs methodology convincingly identified? What assumptions drive the inversion, and are they clearly stated and reasonable?
- [ ] **Conclusion**: Does it summarize findings effectively without overclaiming?

#### 3b. Writing Quality

- [ ] **Clarity**: Is the writing clear and precise throughout? Flag any passages that are confusing, vague, or poorly worded.
- [ ] **Notation**: Is mathematical notation consistent throughout the paper? Are all symbols defined before use?
- [ ] **Length and focus**: Is the paper appropriately scoped for a top journal? Any sections that feel padded or underdeveloped?
- [ ] **Abstract**: Does the abstract concisely convey the contribution, methodology, and key results?

#### 3c. Journal Fit

- [ ] **Contribution significance**: Is the contribution substantial enough for JF, RFS, or Econometrica?
- [ ] **Methodological rigor**: Does the paper meet the technical standards of these journals?
- [ ] **Formatting and conventions**: Does the paper follow the conventions of its target journals (Econometrica style, appropriate formality)?
- [ ] **Which journal fits best**: Based on the paper's strengths, recommend the most appropriate target journal and explain why.

### 4. Figures

- [ ] **Paper figures**: Review all 10 figures generated by `paper/generate_figures.py`. For each figure, verify: (a) it accurately represents the underlying model output, (b) axes labels and legends are correct, (c) it is publication-quality (fonts, resolution, layout). List any issues.
- [ ] **Code-figure consistency**: Spot-check at least 3 figures by tracing the data from model code through the figure generation code to the final plot. Verify the pipeline is correct.
- [ ] **Slide figures**: Check that figures in `slides/long-form/figures/` are consistent with the paper figures.

### 5. Calibration and Results

- [ ] **Parameter values**: Are calibrated parameter values reasonable and well-sourced? Check against the references cited in `_calibration.qmd`.
- [ ] **Sensitivity**: Does the paper adequately explore sensitivity to key parameters (volatility, arrival rate, number of firms, cost of capital)?
- [ ] **Comparative statics**: Verify that reported comparative statics (how triggers/values change with parameters) are consistent with economic intuition and the model's predictions.
- [ ] **Revealed beliefs results**: Are the implied belief estimates for stylized firms plausible? Do they pass a basic sanity check?
- [ ] **Growth decomposition**: Is the decomposition of firm value into installed capacity value and growth option value correctly computed and reported?

### 6. Slides Review

- [ ] **Completeness**: Do the slides cover the key contributions, model, results, and policy implications?
- [ ] **Clarity**: Are the slides readable and self-contained for a conference audience? Is math appropriately simplified for presentation?
- [ ] **Consistency with paper**: Do results, figures, and claims in the slides match the paper exactly?

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

## Part 2: Paper and Presentation Review
### 3. Paper Content Review
[Findings for each sub-section]

### 4. Figures
[Findings for each checklist item]

### 5. Calibration and Results
[Findings for each checklist item]

### 6. Slides Review
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
