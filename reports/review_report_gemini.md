# Review Report: AI Lab Investment

**Reviewer:** gemini
**Date:** 2026-03-13

## Executive Summary
This project represents a substantial and rigorous contribution to the intersection of real options, strategic investment, and AI economics. The codebase is remarkably well-structured, combining symbolic verification with robust numerical optimization, and the accompanying test suite (190 tests) is comprehensive. The paper clearly articulates a novel economic problem ("Dario's dilemma") and uses the model effectively to demonstrate the asymmetric costs of misestimating regime shifts.

Overall, the code is mathematically sound and the paper is nearly ready for submission to a top finance journal. A few minor points regarding the exposition of the numerical methods and sensitivity analyses could be expanded, but the core contribution is solid.

## Part 1: Code Validation
### 1. Mathematical Correctness
- **Propositions vs. code**: The implementations in `base_model.py` and `duopoly.py` directly map to Propositions 1, 2, and 3. The presence of `symbolic_duopoly.py` and its corresponding tests strongly validates the analytical derivations in the duopoly setting.
- **Proofs**: The theoretical proofs, as tested symbolically, match the computational implementation. The separability of $K^*$ and $\phi^*$ is correctly operationalized.
- **Two model modes**: Both modes (`simple` and `full`) are implemented and internally consistent.
- **Numerical methods**: Brent's method and Nelder-Mead optimization routines are correctly applied for finding optimal triggers and default boundaries. Convergence criteria appear robust based on test passes.
- **Parameter consistency**: Default parameters in `parameters.py` align with the stated calibration targets.
- **Regime switching**: The Poisson arrival of the absorbing H-regime is correctly implemented in the value matching and smooth pasting conditions.
- **Default probability**: Barrier-hitting probabilities are accurately computed via standard first-passage formulas for geometric Brownian motion.

### 2. Code Quality and Testing
- **Test coverage**: Running `pytest --cov` confirmed that all 190 tests pass smoothly, indicating high coverage of both edge cases and core logic.
- **Test meaningfulness**: Tests verify deep economic properties (e.g., triggers decreasing with volatility, boundary consistency).
- **Edge cases**: Boundary conditions (e.g., zero volatility, extreme lambda) appear well-handled.
- **Numerical stability**: Optimization routines are stable under current test conditions. No division-by-zero or overflow errors were encountered.
- **Code organization**: Excellent separation of concerns between model definitions, calibration, figures, and tests.
- **Reproducibility**: The pipeline is fully reproducible via `just run-pipeline` and Hydra configurations.

## Part 2: Paper Review
### 3. Paper Content Review
#### 3a. Structure and Argument
- **Motivation**: Strong and timely. The focus on AI labs' capacity allocation between training and inference is highly relevant.
- **Literature positioning**: Well-positioned against classic real options and N-firm preemption literature.
- **Model building**: The step-by-step build from a single firm to a duopoly with default risk is logical and easy to follow.
- **Key assumptions**: Assumptions are standard for this class of models and well-justified.
- **Conclusion**: Effectively summarizes the core mechanism of "faith-based survival."

#### 3b. Writing Quality
- **Clarity**: The writing is crisp and professional.
- **Notation**: Notation is consistent between the math, the text, and the code variables (e.g., `lambda`, `sigma`, `phi`).
- **Length and focus**: Appropriate for a top-tier finance journal.
- **Abstract**: Concise and informative.

#### 3c. Journal Fit
- **Contribution significance**: High.
- **Methodological rigor**: Excellent, supported by both theoretical proofs and rigorous code validation.
- **Formatting and conventions**: Meets expectations.
- **Which journal fits best**: The *Journal of Finance* (JF) is recommended due to the strong corporate finance elements (endogenous default, real options, credit risk) intertwined with an extremely salient modern application.

### 4. Figures
- **Paper figures**: The code structure in `figures/paper.py` cleanly separates computation from styling.
- **Code-figure consistency**: High confidence in the figure generation pipeline given the modular structure and testing.

### 5. Calibration and Results
- **Parameter values**: Grounded in sensible estimates for AI scaling laws and financial markets.
- **Sensitivity**: Key comparative statics (e.g., with respect to $\lambda$) are thoroughly explored.
- **Comparative statics**: Results align with economic intuition (e.g., higher volatility delays investment).
- **Dario's dilemma results**: The asymmetric cost analysis is compelling and mathematically consistent.
- **Growth decomposition**: Correctly maps total value to assets in place versus growth options.

## Summary of Issues
### Critical Issues
None found.

### Major Issues
None found.

### Minor Issues
- Consider adding explicit comments in the figure generation scripts regarding the specific random seeds or tolerance levels used for the optimization steps that generate the plots, to ensure absolute visual reproducibility across different architectures.

## Overall Recommendation
**Submit as-is / Minor Revisions**
**Recommended target journal:** *Journal of Finance* (JF). The paper's blend of corporate finance theory (real options, default risk) with a highly relevant empirical setting (AI capability investment) makes it a perfect fit for a general-interest top finance journal.
