# Review Report: AI Lab Investment

**Reviewer:** codex
**Date:** 2026-02-22

## Executive Summary
The codebase is well-structured, heavily tested (145 tests; all pass), and implements the core real-options mechanisms described in the paper. The single-firm model correctly applies smooth pasting and value matching, the regime-L particular solution is implemented consistently with the inhomogeneous ODE, and the duopoly module captures preemption and default risk with a Leland-style boundary using the negative root. Figures are reproducible from `paper/generate_figures.py` and match the narrative.

Two documentation–implementation mismatches should be addressed before submission:
- Training vs. inference allocation: the paper derives a closed-form optimal training share (Proposition 5), but the code implements a different functional form (log-based incremental quality and finite-horizon PV), yielding a numerical solution rather than the stated analytic ratio. Recommend aligning text with the implemented model or adjusting code to match the stated model.
- Regime-L solution and default boundary formulas: the paper includes a typographical error in the regime-L particular solution statement and an oversimplified default-boundary expression that omits the negative-root factor used in the code. Recommend correcting both formulas in the paper for consistency and accuracy.

Overall: the code is correct and publication-ready; the paper is strong but should incorporate the above fixes and a few clarity edits. Recommended outlet: JF or RFS; Econometrica would likely require fuller proofs and tighter formalism.

## Part 1: Code Validation

### 1. Mathematical Correctness
- Single-firm installed value and smooth pasting
  - Installed value uses `V_s(X,K) = A_s X K^α − δK/r`, implemented in `src/ai_lab_investment/models/base_model.py:38`–`45` and consistent with Eq. (installed value) in the paper.
  - H-regime trigger given K: `X*(K) = [β/(β−1)]·[δK/r + cK^γ]/[A·K^α]` implemented in `src/ai_lab_investment/models/base_model.py:70`–`81`, matches paper Eq. for `X_H^*`.
  - Smooth pasting and value matching verified by tests `tests/test_base_model.py:63` (smooth pasting) and `tests/test_base_model.py:73` (value matching). Both pass.

- Regime L link to H and particular solution
  - The inhomogeneous ODE for `F_L` with switch term is consistent with `F_L(X) = D_L X^{β_L} + C X^{β_H}`, where `C = −λ B_H / Q_L(β_H)`; implemented via `_particular_solution_coeff` in `src/ai_lab_investment/models/base_model.py:135`–`152` and used in `option_value_L` at `src/ai_lab_investment/models/base_model.py:234`–`251`.
  - Tests confirm the “no-trigger in L” case reduces to `F_L(X)=C·X^{β_H}` (`tests/test_base_model.py:108`).

- Duopoly follower/leader structure and preemption
  - Contest share and revenue PV (`src/ai_lab_investment/models/duopoly.py:64`–`95`) match the paper’s Tullock share and PV definitions.
  - Follower optimization over K and trigger consistent with option-premium structure (`src/ai_lab_investment/models/duopoly.py:200`–`224`, `src/ai_lab_investment/models/duopoly.py:226`–`245`).
  - Leader value anticipates follower entry via a revenue-drop term scaled by `(X/X_F)^β` (`src/ai_lab_investment/models/duopoly.py:280`–`320`).
  - Preemption trigger solved where leader value equals follower option using Brent root (`src/ai_lab_investment/models/duopoly.py:513`–`576`). Tests verify `X_leader < X_follower` and `X_leader ≤ X_leader_monopolist` (e.g., `tests/test_duopoly.py:108`, `tests/test_duopoly.py:133`).

- Default boundary and credit pieces
  - Default boundary uses Leland-style formula with negative characteristic root: `X_D = [β⁻/(β⁻−1)]·(coupon/r)/(A·share·K^α)` (`src/ai_lab_investment/models/duopoly.py:126`–`161`), with `β⁻<0` from the quadratic (`src/ai_lab_investment/models/duopoly.py:163`–`176`).
  - Equity and debt values correctly incorporate the default option via `(X/X_D)^{β⁻}`; see `src/ai_lab_investment/models/duopoly.py:182`–`220` and `src/ai_lab_investment/models/duopoly.py:236`–`264`. Tests cover sign and monotonicity (`tests/test_duopoly.py:160`, `tests/test_duopoly.py:203`).

- N-firm sequential equilibrium and training/inference
  - Backward-induction sequential entry with iterative refinement implemented in `src/ai_lab_investment/models/nfirm.py:164`–`240`; verification against analytical duopoly at `src/ai_lab_investment/models/nfirm.py:440`–`480`.
  - Training/inference allocation uses a log-based incremental quality term and finite-horizon PV (`src/ai_lab_investment/models/nfirm.py:280`–`326`), which differs from the power-law model stated in the paper (see Paper Issues below).

### 2. Code Quality and Testing
- Structure and readability
  - Clear modular layout with `models/`, `calibration/`, and `figures/` subpackages; helpful docstrings and caching for solved components.
  - Parameter validation robust and informative (`src/ai_lab_investment/models/parameters.py:35`–`88`).

- Tests and coverage
  - 145 tests across models, calibration, duopoly, N-firm, and valuation; all pass locally using `.venv/bin/pytest` (145 passed in 0.55s).
  - Tests check economic identities (smooth pasting, value matching), comparative statics shapes, default sign properties, and summary integrity.

- Numerical stability
  - Use of bounded scalar minimization and Brent root finding; guardrails for invalid regions; caching of intermediate solutions reduces redundant solves.

## Part 2: Paper and Presentation Review

### 3. Paper Content Review

#### 3a. Substance
- Motivation
  - Strong and timely; stakes and irreversibility are clear. Nicely situates the model in the AI compute race context (`paper/_introduction.qmd`).

- Literature positioning
  - Core citations are present (Dixit & Pindyck; McDonald & Siegel; Guo–Miao–Morellec; Grenadier; Huisman & Kort; Leland). Consider adding recent empirical/finance angles on AI capex and credit conditions if aiming at JF/RFS.

- Model building
  - Phase progression is natural. The single-firm and duopoly pieces are clean and connect well to the N-firm implementation.

- Identification (revealed beliefs)
  - The inversion uses capex intensity, not the H-regime trigger (which is λ-invariant), and the text reflects that (`paper/_valuation.qmd: inversion Eq.`, `tests/test_calibration.py` comments). Clear and defensible, though a short “why intensity not triggers” aside would help.

- Conclusion
  - Balanced; avoids overclaiming while highlighting the asymmetric loss implications and belief dispersion.

#### 3b. Writing Quality
- Clarity and correctness
  - Regime-L particular solution statement has a typo: at `paper/_model.qmd:94` it currently reads `F_L(X) = A_L X^{β_L} + (λ/(r+λ−r)) F_H(X)`. Since `r+λ−r = λ`, this reduces to `F_L = A_L X^{β_L} + F_H`, which is not correct. It should state the standard particular solution proportional to `X^{β_H}`:
    - Suggested replacement: “`F_L(X) = D_L X^{β_L} + C X^{β_H}`, where `C = −λ B_H / Q_L(β_H)` and `Q_L(β) = ½ σ_L^2 β(β−1) + μ_L β − (r+λ)`.” This matches the implementation at `src/ai_lab_investment/models/base_model.py:135`–`152` and tests.

  - Default boundary expression is oversimplified in the paper (`paper/_model.qmd:138`), omitting the dependence on the negative root. Replace with the Leland-style boundary used in code:
    - Suggested replacement: `X_D = [β_s^−/(β_s^− − 1)] · (d/r) / [A_s · K^α · share(K,K_j)]`, where `β_s^− < 0` solves `½ σ_s^2 β(β−1)+ μ_s β − r=0` (see `src/ai_lab_investment/models/duopoly.py:126`–`176`).

- Notation consistency
  - Where possible, prefer `D_L` (free constant in L) and `C` (particular coefficient) to avoid confusion with `A_L` (PV multiplier in installed value). This matches code naming in `base_model.py`.

- Length/focus
  - Scope is appropriate for a finance journal. Appendix proofs are sketch-level; fine for JF/RFS, likely insufficient for Econometrica.

- Abstract
  - Strong; consider tempering “closed-form investment triggers” claim for the duopoly: trigger given K is analytic, but overall equilibrium uses numeric minimization/root-finding (accurate but not fully closed form).

#### 3c. Journal Fit
- Contribution significance: High; unifies real options, competition, and credit, plus an inversion method that is practically relevant.
- Methodological rigor: Strong for JF/RFS. For Econometrica, tighten formal statements and proofs (e.g., uniqueness/existence conditions for preemption with leverage).
- Formatting/conventions: Econometrica-like style already adopted in figures; notation tweaks as above.
- Which journal fits best: JF or RFS (finance emphasis, credit/default integration, investment policy). Econometrica possible with expanded formalism.

### 4. Figures
- Paper figures
  - All 10 figures are generated by `paper/generate_figures.py` and saved under `paper/figures/`. Axes and legends are labeled; consistent publication style.

- Code–figure consistency (spot checks)
  - Option value vs NPV: `fig_option_value` uses `SingleFirmModel.option_value_H` and `installed_value − investment_cost` computed from the same `K_H^*` (`paper/generate_figures.py: fig_option_value`), matching `base_model.py` logic.
  - Default boundaries: `fig_default_boundaries` computes `X_F`, `X_P`, and `X_D` using `DuopolyModel.solve_preemption_equilibrium` and `default_boundary` (`paper/generate_figures.py: fig_default_boundaries`), consistent with `src/ai_lab_investment/models/duopoly.py:126`–`161` and `513`–`576`.
  - Competition effect: `fig_competition_effect` compares monopolist `X^*` to duopoly leader `X_P` across `σ_H` using the same parameter set (`paper/generate_figures.py: fig_competition_effect`), consistent with single-firm and duopoly modules.

- Slides figures
  - `slides/long-form/figures/` mirror paper figures. The slide deck references the same PNGs (e.g., `slides/long-form/_results.qmd`), ensuring consistency.

### 5. Calibration and Results
- Parameter values
  - Baseline `r=0.12`, `μ_H=0.06`, `σ_H=0.30`, `α=0.40`, `γ=1.5`, `λ=0.10` are reasonable given references in `_calibration.qmd`. Stylized firm data are plausible composites with sources listed.

- Sensitivity
  - Comparative statics in Phase 1–2 and sensitivity plots in Phase 4 explore key parameters; shapes are sensible (e.g., triggers ↑ with σ, ↓ with α).

- Comparative statics logic
  - Trigger increases with uncertainty; capacity responds in intuitive directions. Defaults rise with leverage; leader enters before follower.

- Revealed beliefs results
  - The inversion uses capex intensity via `RevealedBeliefs.infer_lambda_from_capex` (`src/ai_lab_investment/calibration/revealed_beliefs.py:94`–`140`), robust to calibration changes via `sensitivity_analysis` (`src/ai_lab_investment/calibration/revealed_beliefs.py:153`–`200`). Tests cover shape and plausibility (`tests/test_calibration.py`).

- Growth decomposition
  - Implemented in `ValuationAnalysis.growth_option_decomposition` (`src/ai_lab_investment/models/valuation.py:20`–`84`); figures match the decomposition narrative.

### 6. Slides Review
- Completeness and clarity
  - Slides cover the intro, model, results, calibration, revealed beliefs, and conclusions. Math is simplified appropriately for talks.

- Consistency
  - Figures and claims match the paper. The same training/inference optimization claim (φ* = η/(α+η)) appears here; see issue below for alignment with code.

## Summary of Issues

### Critical Issues
- Training vs. inference allocation mismatch
  - Issue: The paper and slides state Proposition 5: `φ* = η/(α+η)` based on a power-law quality function `Q(φK) = A(φK)^η` (e.g., `paper/_extensions.qmd` and `paper/_appendix.qmd`). The code implements a different mechanism: a log-based incremental quality `dq = scaling_beta·log(K_T)` and finite-horizon PV added to current inference revenue (`src/ai_lab_investment/models/nfirm.py:280`–`326`). This will generally not yield the analytic φ* and is solved numerically.
  - Fix options:
    1) Align text to implementation: Replace Proposition 5 with a description of the implemented log-increment model, state that φ* is obtained numerically, and interpret comparative statics qualitatively.
    2) Align code to text: Modify `optimal_training_fraction` to implement the power-law quality multiplicatively in revenue (e.g., revenue ∝ `A(φK)^η ((1−φ)K)^α`), which will deliver the closed-form φ* and match the paper. This requires adopting the multiplicative quality term rather than logging and removing the finite-horizon PV approximation.
  - Recommendation: Option (1) is faster editorially; Option (2) is elegant academically and strengthens the contribution. Choose based on target journal; JF/RFS can accept (1) if clearly stated; Econometrica prefers (2).

### Major Issues
- Regime-L solution typo
  - Location: `paper/_model.qmd:94`.
  - Fix: Replace with “`F_L(X) = D_L X^{β_L} + C X^{β_H}`, where `C = −λ B_H / Q_L(β_H)` and `Q_L(β) = ½ σ_L^2 β(β−1) + μ_L β − (r+λ)`.”

- Default boundary expression
  - Location: `paper/_model.qmd:138`.
  - Fix: Replace with the Leland-style expression used in code: `X_D = [β_s^−/(β_s^−−1)]·(d/r)/(A_s·K^α·share)`, referencing the negative root `β_s^−<0` (see `src/ai_lab_investment/models/duopoly.py:126`–`176`).

### Minor Issues
- Abstract wording
  - Consider softening “analytical characterization” of duopoly triggers to reflect mixed analytic/numeric solution.

- Notation consistency
  - Prefer `D_L` (free constant) and `C` (particular coefficient) rather than `A_L` for regime-L option constants to avoid confusion with `A_s = 1/(r−μ_s)` used in installed value.

- Add a brief note that the H-regime trigger does not depend on λ, which is why inversion uses capex intensity instead of triggers (`tests/test_calibration.py` already remarks this in comments).

## Overall Recommendation
- Recommendation: Revise and resubmit.
- Rationale: Code is sound and fully tested; paper needs small but important formula corrections and a clear alignment between the stated training/inference result and the implemented model. These are tractable revisions.
- Target journal: Journal of Finance or Review of Financial Studies, given the finance focus (leverage, default, valuation). Econometrica possible with expanded proofs and tighter formal results.
