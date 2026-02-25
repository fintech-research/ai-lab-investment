# Review Report: AI Lab Investment

**Reviewer:** gemini
**Date:** 2026-02-25

## Executive Summary

The project "Investing in Intelligence" presents a timely and ambitious real options framework for AI compute investment. The theoretical model is well-grounded in the literature, effectively combining regime-switching demand with strategic competition and capacity allocation.

However, the current codebase has **critical issues** regarding the $N$-firm equilibrium implementation. The paper claims to solve for a sequential equilibrium using backward induction, but the code implements a simultaneous-move iterative best-response algorithm. This method is not only theoretically inconsistent with the sequential entry description but is also numerically unstable, failing to converge in the test suite. Additionally, there are inconsistencies in the reported methodology for the $N$-firm extension.

The single-firm and duopoly models are better implemented and align well with the paper's propositions. The paper itself is well-written and positioned for a top finance journal, provided the numerical and methodological inconsistencies are resolved.

## Part 1: Code Validation

### 1. Mathematical Correctness

-   **Propositions vs. code**:
    -   **Single Firm**: The implementation in `base_model.py` (`optimal_trigger_capacity_phi`) correctly implements the formulas in `_model.qmd` (Proposition 1). The effective revenue coefficient $A_{\text{eff}}$ correctly combines L-regime and H-regime components.
    -   **Duopoly**: `duopoly.py` correctly implements the preemption equilibrium (Proposition 3) using backward induction (follower reaction first, then leader). The regime-specific contest functions match the paper.
    -   **N-Firm**: **CRITICAL ISSUE**. The paper (`_extensions.qmd`) states the $N$-firm model is solved via "backward induction" (lines 6, 61) but also mentions "iterative best-response" (line 32). The code (`nfirm.py`, `solve_sequential_equilibrium`) implements the latter: a fixed-point iteration where each firm optimizes against *all* others simultaneously. This is **not** a sequential backward induction solution. In a sequential game, Firm 1 should anticipate Firm 2's reaction, not treat Firm 2's decision as fixed.
-   **Regime Switching**: The GBM with regime switching is correctly implemented. The effective discount rates ($r - \mu_L + \lambda$) and the particular solution coefficient $C$ in `base_model.py` match the derivations.
-   **Parameter Consistency**: Default parameters in `parameters.py` ($r=0.12, \mu_L=0.01, \mu_H=0.06, \sigma=0.25, \dots$) match the calibration section.

### 2. Code Quality and Testing

-   **Test Coverage**: Overall coverage is 47%. The core models (`duopoly.py`, `base_model.py`, `nfirm.py`) have decent coverage (~86-89%), but the pipeline and figure generation are largely untested.
-   **Numerical Stability**: **FAIL**. The $N$-firm tests in `test_nfirm.py` produce `UserWarning: N-firm equilibrium did not converge` with max capacity changes reaching $10^{20}$. This indicates the fixed-point iteration is divergent.
-   **Overflow Errors**: `RuntimeWarning: overflow encountered in scalar power` occurs in `duopoly.py` and `nfirm.py`. This suggests parameter combinations or intermediate steps in the optimization loop are hitting numerical limits, likely due to the non-converging iterations blowing up capacity values.
-   **Test Meaningfulness**: The tests check for basic properties (triggers exist, values are positive), but the $N$-firm tests are currently failing or warning, meaning they are not effectively validating the equilibrium logic.

## Part 2: Paper Review

### 3. Paper Content Review

#### 3a. Structure and Argument
-   **Motivation**: Strong. The link between real options, AI scaling laws, and market structure is compelling.
-   **Model Building**: The progression from single-firm to duopoly is logical. The extension to $N$ firms is natural but, as noted, methodologically confused in the text.
-   **Literature**: Good positioning relative to Dixit/Pindyck and Grenadier. The "faith-based survival" mechanism is a nice theoretical contribution linking beliefs to credit risk.

#### 3b. Writing Quality
-   **Clarity**: generally excellent. The distinction between "training" and "inference" compute is well-explained.
-   **Contradiction**: `_extensions.qmd` contains a direct contradiction regarding the solution method (backward induction vs. iterative best response). This must be harmonized.

#### 3c. Journal Fit
-   **Recommendation**: **Review of Financial Studies (RFS)** or **Journal of Finance (JF)**.
-   **Justification**: The paper fits the "new finance" trend of modeling specific technological/industrial shocks. The focus on corporate investment, capital structure (default risk), and competition is core finance.

### 4. Figures
-   **Consistency**: `figures/paper.py` generally matches the model logic.
-   **Figure 10 (Growth Decomposition)**: The implementation in `create_growth_decomposition` is confusing. It calculates a "counterfactual" value that doesn't clearly map to standard "growth option" definitions (PV of future investment opportunities). It seems to compare optimal vs. sub-optimal capacity value, which is not the standard definition.

### 5. Calibration and Results
-   **Parameters**: The baseline values are reasonable and well-sourced in the text.
-   **Results**: The "faith-based survival" result (higher training $\phi$ lowers default boundary) is intriguing and appears consistent with the model mechanics (verified in `duopoly.py` default boundary logic).

## Summary of Issues

### Critical Issues
1.  **N-Firm Model Implementation**: The `nfirm.py` code does not implement the sequential backward induction described in parts of the paper. It implements a simultaneous-move fixed-point iteration.
2.  **N-Firm Numerical Divergence**: The $N$-firm solver fails to converge, producing massive capacity values and overflow warnings. This renders Phase 3 results unreliable.
3.  **Methodological Contradiction**: The paper (`_extensions.qmd`) explicitly claims two contradictory solution methods for the $N$-firm case.

### Major Issues
1.  **Growth Option Figure Logic**: Figure 10's calculation of "growth option value" is non-standard and likely incorrect or mislabeled.
2.  **Overflow Warnings**: `RuntimeWarning`s in `duopoly.py` need to be addressed, likely by bounding the optimization search space or using log-transformed variables more consistently to avoid $K^\gamma$ blowups.

### Minor Issues
1.  **Documentation**: `base_model.py` methods like `installed_value` (simple mode) don't take `phi`, while `installed_value_with_phi` (full mode) does. This distinction is clear in `AGENTS.md` but should be clarified in the code docstrings to avoid confusion.

## Overall Recommendation

**Revise and Resubmit**.

The core contribution (single firm and duopoly with default) is strong and well-executed. However, the $N$-firm extension is currently flawed in both implementation and description. The author should either:
1.  Fix the `nfirm.py` code to strictly implement backward induction (solve Firm $N$, then $N-1$, etc.), OR
2.  Downgrade the claim to a "simultaneous entry" or "open-loop" equilibrium and fix the numerical stability issues in the iterative solver.

**Target Journal**: Review of Financial Studies.
