# Review Report: AI Lab Investment

**Reviewer:** opencode
**Date:** 2026-02-24

## Executive Summary

The project "Investing in Intelligence" presents a timely and sophisticated real options framework for AI infrastructure investment. The codebase implements a multi-stage model progression: a single-firm benchmark, a duopoly with default risk, and an N-firm sequential equilibrium. The theoretical work is grounded in a calibration to current industry data and scaling laws.

Overall, the code is well-structured and faithfully implements the core mathematical models described in the paper. However, I identified a **critical inconsistency** in the model specification between the single-firm/duopoly models (Phase 1/2) and the N-firm extension (Phase 3), specifically regarding how training compute affects revenue. This leads to conflicting results for the optimal training fraction ($\phi^*$). Additionally, the test suite is currently failing due to dependency issues with `numpy` and `scipy` versions, which needs immediate attention.

The paper is well-written and fits the scope of a top finance journal, but the discrepancies between the text/code in Phase 1 and the slides/code in Phase 3 must be resolved before submission.

## Part 1: Code Validation

### 1. Mathematical Correctness

-   **Propositions vs. Code:**
    -   **Pass:** The core GBM, option value, and investment trigger formulas in `base_model.py` correctly implement Equations (149), (176), and (230) from `_model.qmd`.
    -   **Pass:** The duopoly preemption logic and default boundary in `duopoly.py` match Proposition 2 and 3.
    -   **Issue (Critical):** There is a fundamental model mismatch regarding the training-inference allocation ($\phi$).
        -   In `base_model.py` (and `_model.qmd`), H-regime revenue is $\pi = X (\phi K)^\alpha$, implying training *directly* generates revenue in the high regime. This leads to a numerical solution for $\phi^*$ dependent on $\lambda$, $r$, etc.
        -   In `nfirm.py` (and `slides/long-form/_results.qmd`), revenue is modeled as $\pi = X \cdot e^{quality} \cdot ((1-\phi)K)^\alpha$, where quality comes from cumulative training. This leads to the closed-form $\phi^* = \eta / (\alpha + \eta)$ (Proposition 5 in slides/code docstrings).
        -   The paper text in `_model.qmd` describes the first approach (numerical), but the slides present the second (closed-form). This inconsistency must be reconciled.

-   **Proofs:**
    -   **Pass:** The proofs in `_appendix.qmd` (checked via `base_model.py` implementation) follow standard real options logic (smooth pasting, value matching).

-   **Numerical Methods:**
    -   **Pass:** `base_model.py` uses `scipy.optimize.minimize_scalar` effectively for the 1D optimization. `revealed_beliefs.py` uses `brentq` for root finding, which is appropriate.
    -   **Pass:** `nfirm.py` implements the recursive backward induction correctly.

-   **Parameter Consistency:**
    -   **Pass:** `calibration/data.py` values ($\mu_L=0.01, \alpha=0.40$, etc.) match `_calibration.qmd` exactly.

### 2. Code Quality and Testing

-   **Test Coverage:**
    -   **Issue (Critical):** The test suite is currently **failing** due to `ModuleNotFoundError: No module named 'numpy.char'` and other import errors. This appears to be caused by `pyproject.toml` pinning future versions (`numpy>=2.4.2`, `scipy>=1.17.0`) which are likely incompatible with the installed environment or each other.
    -   **Pass:** Coverage is reported as high (~86%) for the model files, which is good (conditional on tests passing).

-   **Test Meaningfulness:**
    -   **Pass:** Tests in `test_base_model.py` check economic properties (e.g., trigger > Marshallian trigger, option value > NPV).

-   **Code Organization:**
    -   **Pass:** The separation into `models/`, `calibration/`, and `pipeline.py` is clean and follows standard engineering practices. Type hinting is used consistently.

## Part 2: Paper and Presentation Review

### 3. Paper Content Review

#### 3a. Structure and Argument
-   **Motivation:** **Pass.** The introduction effectively motivates the "AI investment dilemma" (overinvest vs. miss out).
-   **Literature Positioning:** **Pass.** Situates well within real options (Dixit/Pindyck) and recent AI economics.
-   **Model Building:** **Pass.** The progression from single firm to duopoly is logical. The "faith-based survival" mechanism in the duopoly section is a strong theoretical contribution.

#### 3b. Writing Quality
-   **Clarity:** **Pass.** The writing is precise and professional.
-   **Notation:** **Pass.** Consistent usage of $X, K, \phi, \lambda$.

#### 3c. Journal Fit
-   **Recommendation:** **Review of Financial Studies (RFS)** or **Journal of Finance (JF)**.
-   **Justification:** The paper's strong focus on corporate finance mechanics (leverage, default risk, WACC) and the "revealed beliefs" asset pricing angle makes it a perfect fit for top finance journals. Econometrica might require more general theoretical contributions beyond the specific application.

### 4. Figures
-   **Pass:** The figures in `paper/figures/` (viewed via generation code) cover the key comparative statics.
-   **Consistency:** The figure generation code `paper/generate_figures.py` imports directly from the model classes, ensuring consistency (assuming the model code is fixed).

### 5. Calibration and Results
-   **Pass:** The calibration to "Stylized Firms" (Anthropic-like, OpenAI-like, etc.) is creative and grounded in available public data.
-   **Pass:** The "Revealed Beliefs" methodology is a clever use of the inverse function theorem to map observables (CapEx) to unobservables (beliefs).

### 6. Slides Review
-   **Issue (Major):** The slides present "Proposition 5" and the closed-form $\phi^*$ formula, which contradicts the main paper draft `_model.qmd` (which discusses Proposition 1 and numerical $\phi^*$). The slides need to be updated to match the current paper version, or the paper updated if the N-firm specification is the intended one.

## Summary of Issues

### Critical Issues
1.  **Model Inconsistency:** Phase 1/2 (`base_model.py`, `duopoly.py`) and Phase 3 (`nfirm.py`) use different revenue functions regarding $\phi$. This leads to contradictory results for optimal training allocation.
2.  **Broken Tests:** The test suite fails to run due to dependency version issues (`numpy`/`scipy`).

### Major Issues
1.  **Slides vs. Paper:** The slides reference a "Proposition 5" and a formula that are not present in the reviewed paper text.

### Minor Issues
1.  **Endogenous Lambda Loop:** The loop for endogenous $\lambda$ (Equation 19) is mentioned in Corollary 1 but explicit fixed-point code was not found in `base_model.py` (though it might be handled in the calling pipeline or implicitly).

## Overall Recommendation

**Revise and Resubmit (Internal)**

The project has high potential and the core modeling of the duopoly/default interaction is excellent. However, the inconsistency between the model stages regarding the training allocation $\phi$ invalidates the claim of a "unified" framework.

**Action Plan:**
1.  **Decide on the $\phi$ model:** Choose either the flow-revenue model (Phase 1) or the quality-stock model (Phase 3) and apply it consistently across all phases.
2.  **Fix Dependencies:** Downgrade `numpy` and `scipy` in `pyproject.toml` to stable, compatible versions (e.g., `numpy>=1.26`, `scipy>=1.14`) to get tests passing.
3.  **Sync Slides:** Update slides to reflect the chosen model specification.
