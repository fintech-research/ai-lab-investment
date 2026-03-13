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
3. **Calibration:** Parameters calibrated to publicly available data on four stylized AI lab archetypes (hyperscaler, frontier lab, compute racer, lean lab).
4. **Valuation and Dario's dilemma:** Value decomposition, credit risk analysis, and an asymmetric belief-mismatch cost analysis showing that underinvestment is costlier in expected value than overinvestment, while overinvestment carries higher tail (default) risk.

**Key model features:**
- Training-inference allocation (φ): firms split capacity between inference (L-regime revenue) and training (H-regime competitive position)
- K* is independent of φ (separable FOCs); φ* is interior and determined by maximizing A_eff
- Faith-based survival: training raises A_eff through the H-regime continuation value, lowering the default boundary
- First-passage (barrier) default probability, consistent with Leland-style default mechanism
- Dario's dilemma: asymmetric cost of belief mismatch about λ (W''' > 0 → underinvestment costlier)

**Target journals:** JF, RFS, or Econometrica.

---

## Repository Structure

```
ai-lab-investment/
├── src/ai_lab_investment/       # Core source code
│   ├── __main__.py              # Entry point
│   ├── pipeline.py              # Hydra-decorated pipeline orchestrator
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
│   │   ├── phi_allocation.py    # Training/inference allocation figures
│   │   ├── phase1.py            # Exploratory base model figures
│   │   ├── phase2.py            # Exploratory duopoly figures
│   │   ├── phase4.py            # Exploratory calibration figures
│   │   └── phase5.py            # Exploratory valuation figures
│   └── utils/
│       ├── directories.py       # Directory path resolution
│       └── files.py             # Timestamped file naming
├── tests/                       # 190 tests across 6 test files
│   ├── test_base_model.py
│   ├── test_calibration.py
│   ├── test_duopoly.py
│   ├── test_parameters.py
│   ├── test_symbolic_duopoly.py
│   └── test_valuation.py
├── paper/                       # Research paper (Quarto -> PDF)
│   ├── index.qmd                # Main file; includes all sections
│   ├── _introduction.qmd        # Motivation, contribution, literature review
│   ├── _model.qmd               # Model: demand, technology, single-firm, duopoly
│   ├── _calibration.qmd         # Calibration to four AI lab archetypes
│   ├── _valuation.qmd           # Value decomposition, credit risk, Dario's dilemma
│   ├── _discussion.qmd          # Policy implications, testable predictions, limitations
│   ├── _conclusion.qmd
│   ├── _literature.qmd          # Literature review (included within introduction)
│   ├── _appendix.qmd            # Proofs (Propositions 1-3), numerical methods, calibration details
│   ├── generate_figures.py      # Thin wrapper: applies styles and saves output
│   ├── references.bib           # BibTeX references
│   └── figures/                 # Generated figures (*.pdf, *.png; 11 figures)
├── notebooks/
│   └── model_derivation.ipynb   # SymPy derivation notebook (8 sections + audit)
├── conf/config.yaml             # Hydra pipeline configuration
├── CLAUDE.md                    # Project instructions and conventions
├── AGENTS.md                    # Detailed agent instructions
├── justfile                     # Task runner (just check, just test, etc.)
└── pyproject.toml               # Python project metadata
```

---

## Review Scope

Your review covers two areas, weighted roughly equally.

### Part 1: Code Validation

Verify that the implementation is correct, the tests are meaningful, and the code faithfully implements the mathematics described in the paper.

### Part 2: Paper Review

Evaluate the paper as a referee would for a top finance or economics journal (JF, RFS, Econometrica).

---

## Detailed Review Checklist

Work through every section below. For each item, state whether it **passes**, **has issues** (describe them), or **could not be verified** (explain why). Be specific: cite file paths, line numbers, equation numbers, proposition numbers, and test names.

### 1. Mathematical Correctness

- [ ] **Propositions vs. code**: For each proposition in the paper (`_model.qmd`, `_appendix.qmd`), locate the corresponding implementation in the source code. The paper has three propositions: Proposition 1 (optimal K*, φ*), Proposition 2 (default boundary properties, faith-based survival), and Proposition 3 (preemption equilibrium). Verify that the formulas in code match the formulas in the paper exactly. Flag any discrepancies, even notational ones.
- [ ] **Proofs**: Read the proofs in `_appendix.qmd`. Check logical completeness — are all steps justified? Are boundary/edge cases handled? Pay particular attention to: (a) the separability of K* and φ* in Proposition 1, (b) the two-channel derivative ∂X_D/∂λ in Proposition 2(ii), and (c) the Dario's dilemma Taylor expansion sign argument.
- [ ] **Two model modes**: The code has two modes — *simple* (no φ: `installed_value()`, `optimal_trigger_and_capacity()`) and *full* (with φ: `optimal_trigger_capacity_phi()`, `installed_value_with_phi()`). Verify both are internally consistent and that the paper uses the full mode for all reported results.
- [ ] **Numerical methods**: In `calibration/revealed_beliefs.py` and the optimization routines in `base_model.py` and `duopoly.py`, verify that numerical algorithms (root-finding, Nelder-Mead optimization, Brent's method) are correctly implemented. Check convergence criteria and tolerances.
- [ ] **Parameter consistency**: Verify that default parameter values in `models/parameters.py` match the calibration values stated in `_calibration.qmd` and the baseline results table in `_appendix.qmd`. Check units and scaling.
- [ ] **Regime switching**: Verify the regime-switching demand process implementation in `models/base_model.py` matches the specification in `_model.qmd`. Check transition intensities, drift, volatility, and the absorbing-state assumption for regime H.
- [ ] **Default probability**: Verify that the first-passage (barrier hitting) probability in `valuation.py` is correctly implemented and matches the formula in `_valuation.qmd`.

### 2. Code Quality and Testing

- [ ] **Test coverage**: Run `just test` (or `uv run pytest --cov`) and report coverage. Identify any untested functions or branches in the models.
- [ ] **Test meaningfulness**: Read through the 6 test files. Are the tests checking economically meaningful properties (e.g., option values are positive, triggers decrease with volatility, default boundary lies below investment trigger, K* is independent of φ)? Or are they trivial/tautological?
- [ ] **Edge cases**: Are boundary conditions tested? (e.g., zero volatility, lambda = 0 or very large lambda, leverage = 0, φ at boundaries)
- [ ] **Numerical stability**: Check for potential numerical issues: division by zero guards, overflow in exponentials, convergence failures in optimization.
- [ ] **Code organization**: Is the code well-structured? Are responsibilities cleanly separated between modules? Any code smells or unnecessary complexity?
- [ ] **Reproducibility**: Can results be reproduced by running `just run-pipeline`? Are random seeds set where needed?

### 3. Paper Content Review

Review the paper as a referee for a top journal. Address each sub-item.

#### 3a. Structure and Argument

- [ ] **Motivation**: Is the introduction compelling? Does it clearly articulate the core economic question (timing, sizing, and allocating irreversible capacity under regime uncertainty), the gap in existing theory, and the key insight (training-survival channel)?
- [ ] **Literature positioning**: Does the paper adequately situate itself relative to the real options literature (Dixit & Pindyck, McDonald & Siegel), strategic investment games (Grenadier, Huisman & Kort), R&D race models (Loury, Reinganum), structural credit risk (Leland, Merton), and AI economics literature? Are there important omissions?
- [ ] **Model building**: Does the progression from single-firm to duopoly feel natural and well-motivated? Is the duopoly focus (rather than N-firm) adequately justified?
- [ ] **Key assumptions**: Are the maintained assumptions (A1–A4) clearly stated and their economic content explained? Is the simplified L-regime option value (A3) convincingly justified?
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

- [ ] **Paper figures**: Review all 11 figures in `paper/figures/`, generated by `paper/generate_figures.py` (which delegates all computation to `src/ai_lab_investment/figures/paper.py`). For each figure, verify: (a) it accurately represents the underlying model output, (b) axes labels and legends are correct, (c) it is publication-quality (fonts, resolution, layout). List any issues.
- [ ] **Code-figure consistency**: Spot-check at least 3 figures by tracing the data from model code through `figures/paper.py` to the final plot. Verify the pipeline is correct.

### 5. Calibration and Results

- [ ] **Parameter values**: Are calibrated parameter values reasonable and well-sourced? Check against the references cited in `_calibration.qmd` and the data sources table in `_appendix.qmd`.
- [ ] **Sensitivity**: Does the paper adequately explore sensitivity to key parameters (volatility, arrival rate, revenue elasticity, cost convexity, cost of capital)?
- [ ] **Comparative statics**: Verify that reported comparative statics (how triggers/values change with parameters) are consistent with economic intuition and the model's predictions.
- [ ] **Dario's dilemma results**: Are the value loss percentages and default probabilities under belief mismatches correctly computed and internally consistent? Does the Taylor expansion sign argument match the numerical results?
- [ ] **Growth decomposition**: Is the decomposition of firm value into installed capacity value and growth option value correctly computed and reported?

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
