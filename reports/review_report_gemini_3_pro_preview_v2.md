# Review Report: AI Lab Investment

**Reviewer:** gemini_3_pro_preview_v2
**Date:** 2026-02-22

## Executive Summary

The paper "Investing in Intelligence: A Real Options Framework for AI Compute Infrastructure" presents a timely and sophisticated analysis of AI infrastructure investment. It successfully integrates real options theory, regime switching, oligopoly competition, and endogenous default risk into a unified framework calibrated to empirical scaling laws.

The codebase is generally well-structured, follows modern Python practices, and implements the mathematical models faithfully. The analytical solutions for the single-firm and duopoly cases match the derived propositions. The numerical methods for the N-firm equilibrium and revealed beliefs inversion are logically sound, though with a dimensionality concern in the latter.

Overall, the paper is strong and close to submission quality. The model provides clear economic mechanisms explaining the "race to scale" and the role of heterogeneous beliefs. I recommend a "Revise and Resubmit" to address the dimensionality issue in the revealed beliefs calibration and to strengthen the justification for the chosen method.

## Part 1: Code Validation

### 1. Mathematical Correctness
- [x] **Propositions vs. code**: The implementation in `models/base_model.py` and `models/duopoly.py` matches the propositions in the paper.
    - `SingleFirmModel` correctly implements the optimal trigger $X_H^*$ (Eq 62) and capacity $K_H^*$ (Eq 76).
    - `DuopolyModel` correctly implements the contest function (Eq 121) and default boundary $X_D$ (Eq 141).
- [x] **Proofs**: The proofs in `_appendix.qmd` are logical. The smooth-pasting conditions are correctly derived.
- [x] **Numerical methods**: The backward induction in `models/nfirm.py` correctly handles the sequential entry game. The fixed-point iteration for capacity refinement is appropriate.
- [x] **Parameter consistency**: `models/parameters.py` matches the values in `_calibration.qmd` exactly.
- [x] **Regime switching**: The GBM simulation and analytical option values in `models/base_model.py` correctly incorporate the Poisson arrival rate $\lambda$ and the transition from regime L to H.

### 2. Code Quality and Testing
- [x] **Test coverage**: `just test` passes with reasonable coverage for the models (~80-90%). `figures`, `pipeline`, and `utils` are untested, which is acceptable for research code but could be improved.
- [x] **Test meaningfulness**: Tests in `tests/` check economic properties (e.g., `test_higher_lambda_lower_trigger`, `test_competition_accelerates_investment`).
- [x] **Edge cases**: Tests cover boundary conditions like zero leverage and single-firm equivalence.
- [x] **Numerical stability**: The code uses log-transformed optimization for capacity (`_objective_K`) to improve stability.
- [x] **Code organization**: The project structure is clean, with clear separation between models, calibration, and presentation logic.
- [x] **Reproducibility**: Random seeds are set in `simulate_demand` and figure generation, ensuring reproducibility.

## Part 2: Paper and Presentation Review

### 3. Paper Content Review

#### 3a. Structure and Argument
- [x] **Motivation**: The introduction is compelling, clearly linking the theoretical framework to the current AI investment boom.
- [x] **Literature positioning**: The paper is well-situated, citing key real options (Dixit & Pindyck) and strategic investment (Grenadier, Huisman) literature.
- [x] **Model building**: The progression from single-firm to duopoly to N-firm is logical.
- [ ] **Identification**: The "revealed beliefs" methodology has a dimensional consistency issue. The code compares a dimensionless ratio (Investment/Value) with a dimensioned ratio (Capex/Revenue, units of years). This requires justification or normalization.
- [x] **Conclusion**: Effectively summarizes the findings.

#### 3b. Writing Quality
- [x] **Clarity**: The writing is precise and high-quality.
- [x] **Notation**: Consistent throughout.
- [x] **Length and focus**: Appropriate for a top finance/econ journal.
- [x] **Abstract**: Concise and informative.

#### 3c. Journal Fit
- [x] **Contribution**: Significant theoretical and empirical contribution.
- [x] **Methodological rigor**: High.
- [x] **Formatting**: Follows standard conventions.
- [x] **Recommendation**: **Journal of Finance (JF)** or **Review of Financial Studies (RFS)**. The focus on corporate investment, default risk, and market beliefs fits these journals well.

### 4. Figures
- [x] **Paper figures**: The 10 generated figures are publication-quality and accurately reflect the model.
- [x] **Code-figure consistency**: Verified `generate_figures.py` uses the model classes correctly.
- [x] **Slide figures**: Consistent with paper.

### 5. Calibration and Results
- [x] **Parameter values**: Reasonable and sourced.
- [x] **Sensitivity**: Comparative statics in Figure 3 cover key parameters.
- [x] **Comparative statics**: Results (e.g., competition accelerates investment) align with intuition.
- [ ] **Revealed beliefs results**: Plausible qualitatively (frontier labs are more optimistic), but the quantitative values depend on the dimensional assumption noted above.
- [x] **Growth decomposition**: Correctly implemented as PVGO.

### 6. Slides Review
- [x] **Completeness**: Covers all key sections.
- [x] **Clarity**: Well-designed for presentation.
- [x] **Consistency**: Matches the paper.

## Summary of Issues

### Critical Issues
- **Dimensionality in Revealed Beliefs**: In `calibration/revealed_beliefs.py`, the method `infer_lambda_from_capex` compares `model_intensity = I(K) / V(X,K)` (dimensionless) with `observed_intensity = Capex / Revenue` (dimension: years).
    - $I(K)$ is a stock (lump sum cost). $V(X,K)$ is a stock (PV of firm). Ratio is dimensionless.
    - Capex is a flow (annual). Revenue is a flow (annual). Ratio is dimensionless?
    - **Correction**: If "Capex" in the data refers to the *total cost of the cluster* (lump sum), then it matches $I(K)$. If "Revenue" is *annual* revenue, then Capex/Revenue has units of years. The model's $V(X,K)$ is roughly $Revenue / (r-\mu)$. So $I/V \approx I / (Rev/(r-\mu)) = (I/Rev) * (r-\mu)$.
    - The code equates $I/V$ directly to $Capex/Rev$. This implies an assumption that $r-\mu \approx 1$, which is false ($0.12 - 0.06 = 0.06$).
    - **Fix**: The observed intensity should likely be compared to $I(K) / (Revenue\_Flow)$. Or the model intensity should be defined as $I(K) / (X K^\alpha)$.

### Major Issues
- None beyond the dimensionality issue.

### Minor Issues
- **Growth Decomposition Definition**: In Figure 10, "Assets-in-place" is defined as the gross value $V(X, K_{installed})$. Standard corporate finance definitions (e.g., Myers 1977) often define firm value as $V_{assets} + PVGO$. If $V_{assets}$ is net of replacement cost, clarity is needed. The current "gross value" approach is acceptable but should be explicitly stated.

## Overall Recommendation
**Revise and Resubmit**

Target Journal: **Journal of Finance**

The paper is theoretically sound and empirically relevant. The critical issue regarding the dimensionality of the revealed beliefs calibration must be addressed. Once fixed, the paper will be a strong candidate for a top-tier finance journal.
