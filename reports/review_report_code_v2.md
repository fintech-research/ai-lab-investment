# Review Report: AI Lab Investment

**Reviewer:** openai_assistant
**Date:** 2026-02-22

## Executive Summary
The repository cleanly implements a layered real-options framework (single firm → duopoly with default risk → N‑firm numerical) with thoughtful calibration and a strong figure pipeline. The core Phase 1 math is implemented faithfully (smooth pasting, existence conditions, regime switching), the duopoly adds a consistent structural default block, and the N‑firm module follows the intended fixed‑point refinement. Code is modular, documented, and covered by a robust test suite targeting key properties and comparative statics.

Two substantive paper–code mismatches need attention before submission: (i) the duopoly preemption trigger is stated to decrease with λ (paper Proposition 3(ii), `paper/_model.qmd:205`), but the implemented H‑regime equilibrium in code does not depend on λ (H uses `A_H`, `β_H` only); and (ii) the revealed‑beliefs inversion equates CapEx/Revenue to I/V where V is a present value, creating a units/definition mismatch versus the narrative (CapEx/Revenue). These should be reconciled (revise claims and figures or extend the model/estimation to align).

With those fixed, the paper is well positioned for a finance journal (RFS/JF) given its strategic investment + credit risk angle. I recommend “Revise and resubmit”.

## Part 1: Code Validation
### 1. Mathematical Correctness
- Single‑firm option structure and smooth pasting
  - Installed value matches the paper’s `V_s(X,K) = A_s X K^α − δK/r` (code: `src/ai_lab_investment/models/base_model.py:19-28`; paper: `paper/_model.qmd:36-47`).
  - H‑regime option value and trigger are implemented per the characteristic root β_H (code smooth pasting: `base_model.py:98-118, 170-194`; paper eqs. `paper/_model.qmd:51-64`). Tests verify value‑matching and smooth‑pasting at X*_H (`tests/test_base_model.py:31-58`).
  - Existence condition uses ϕ = (1−1/β)/α with 1/γ < ϕ < 1 (code: `base_model.py:35-54, 56-67`), consistent with the stated condition.
- Regime switching and L‑regime option value
  - Particular solution coefficient C and L‑regime construction match the RS-GBM form (code: `base_model.py:120-145, 147-196`). Tests confirm C>0 and the “no interior trigger” case (`tests/test_base_model.py:87-113`).
- Duopoly with default (Leland structure)
  - Default boundary and negative root are implemented per Leland with GBM state X (code: `src/ai_lab_investment/models/duopoly.py:126-161, 163-176`). Paper gives the same form (Appendix: “Proposition 2”, `paper/_appendix.qmd` A/B sections).
  - Leader/follower problems are set up with the contest share; preemption uses root finding of L(X)−F(X) (code: `duopoly.py:291-338, 506-560`). Tests target preemption ordering and equilibrium existence (`tests/test_duopoly.py:78-122, 145-164`).
- N‑firm fixed‑point solution and training split
  - Backward induction + refinement loop converges under a tolerance (code: `src/ai_lab_investment/models/nfirm.py:136-214`). Tests cover ordering and convergence properties (`tests/test_nfirm.py:72-118`).
  - Proposition 5 (optimal training φ* = η/(α+η)) matches code and tests (`nfirm.py:216-244`, `tests/test_nfirm.py:140-162`).

Issues/clarifications:
- Paper—code mismatch on λ in duopoly: The paper claims X_P ↓ in λ (Proposition 3(ii), `paper/_model.qmd:205`), while the implemented H‑regime duopoly uses `A_H, β_H` and thus is independent of λ (see `duopoly.py:92-105, 148-156`). The figure function `plot_lambda_duopoly` asserts the “key insight” (`src/ai_lab_investment/figures/phase2.py:369-373`), but will plot flat lines. Fix either the claim (relabel as independent of λ under the current H‑regime formulation) or extend the model to explicitly link preemption to λ (e.g., compute the preemption boundary in L with switching continuation value).
- Appendix derivation for K*: The Appendix’s Step 2 mixes a “δ small” leading‑order argument without completing the full FOC algebra (see `paper/_appendix.qmd:23-57`). Either provide the full closed‑form FOC solution for K* (if obtainable) or clearly state it is found by 1‑D numerical optimization while preserving the closed‑form X*(K) and smooth pasting.
- Discounting convention: The paper says “r is the risk‑free rate” (`paper/_model.qmd:18`), but the parameter class documents “r is WACC” (`src/ai_lab_investment/models/parameters.py:15-20, 32-40`). Reconcile: either present risk‑neutral drifts μ with risk‑free r in text, or explicitly state you work under a risk‑adjusted measure with r=WACC and μ “risk‑neutral drifts net of risk premium”.

### 2. Code Quality and Testing
- Structure and clarity
  - Clear module decomposition by phase; descriptive docstrings; caching of intermediate results in models; small, testable methods.
  - Figures are isolated from models; paper figures have a dedicated generator (`paper/generate_figures.py`).
- Tests (145 across 6 files)
  - Cover existence, smooth pasting, comparative statics, default boundary behavior, preemption ordering, N‑firm convergence, training fraction, calibration plumbing, and valuation utilities.
  - I could not execute tests in this sandbox (uv cache forbidden by FS sandbox), but manual inspection shows good coverage and sensible assertions (e.g., `tests/test_duopoly.py:201-220`, `tests/test_valuation.py:69-117`).
- Style/tooling
  - `just check` includes pre‑commit and type checking; Hydra pipeline orchestrates phases (`src/ai_lab_investment/pipeline.py`).

Suggestions:
- Add a minimal deterministic unit test around `solve_preemption_equilibrium` at a pinned parameter set to snapshot the X_P/X_F pair, catching regressions in the bisection/brent path.
- Consider surfacing an explicit “regime‑L preemption” API if you choose to make X_P depend on λ (see Critical Issues below).

## Part 2: Paper and Presentation Review
### 3. Paper Content Review
#### 3a. Structure & Argumentation
- Motivation is timely and compelling; the 5‑phase roadmap is clear and tracked in code. The single‑firm → duopoly → N‑firm progression feels natural and justified.
- Strategic investment + default mechanism is well‑motivated; the “competition–leverage spiral” is a distinctive angle for finance outlets.
- Revealed‑beliefs section is novel and clearly positioned, but see identification notes below.

- Key alignment fixes:
  - Duopoly λ‑dependence: revise Proposition 3(ii) and any related text/figures to match the implemented model (H‑regime triggers independent of λ) or extend the model so preemption is explicitly λ‑sensitive (e.g., evaluate L(X) vs F(X) in L with switching continuation value F_L that depends on C(λ)).
  - Clarify discounting: unify the “risk‑free r” (text) vs “WACC r” (code docs) convention.

#### 3b. Writing Quality
- Clear, precise exposition; consistent notation for X, K, α, γ, r, μ, σ, λ. All symbols used in equations appear to be defined before use. Minor suggestions:
  - In Proposition 3 derivation, define `β_s`/`β_s^-` explicitly when first used in the duopoly section (a short sentence reminding they are the positive/negative roots in regime s), e.g., near `paper/_model.qmd:155-167`.
  - Appendix A Step 2: remove the “δ small” aside or present the full FOC for K*; otherwise explicitly state K* is obtained by 1‑D numerical optimization after closed‑form X*(K).
  - Abstract: consider replacing “closed‑form investment triggers” with “semi‑analytical characterization”; duopoly uses 1‑D optimization for K and root finding for preemption.

#### 3c. Journal Fit
- Contribution significance: Strong, especially the integration of strategic timing, leverage/default, and an inversion approach for beliefs.
- Methodological rigor: Solid for a finance audience; proofs are sketched where closed‑form exists and computation is transparent elsewhere; tighten Appendix A as noted.
- Best fit: RFS or JF. Econometrica would likely require deeper theory results or identification proofs beyond the current inversion approach.

### 4. Figures
- Paper figures (10 total) generated via `paper/generate_figures.py`:
  - Verified code→figure consistency for:
    - `fig_option_value` (H‑regime option vs NPV) computed from `SingleFirmModel.option_value_H` and `installed_value` at K*_H (code: `paper/generate_figures.py:66-115`). Axes/labels and smooth‑pasting annotation match the text figure description (paper: `paper/_model.qmd:66-71`).
    - `fig_default_boundaries` uses `DuopolyModel.default_boundary` and preemption outputs (code: `paper/generate_figures.py:282-334`). Labels and shaded operating region match the explanation (paper: `paper/_model.qmd:149-158`).
    - `fig_growth_decomposition` is computed from model components at fixed X>K*_H trigger (code: `paper/generate_figures.py:560-618`), consistent with the valuation section (paper: `paper/_valuation.qmd:90-98`).
  - Style: consistent serif fonts, good DPI, clear legends; publication‑ready.
- Code–figure inconsistency to fix:
  - Phase 2 “λ–duopoly” diagnostic (`src/ai_lab_investment/figures/phase2.py:365-423`) asserts that higher λ lowers triggers but, under the current H‑regime formulation, triggers will be flat in λ. Remove or rework this diagnostic (and adjust any slide/paper text making that claim) unless the model is extended.
- Slide figures: long‑form slides reference the same generated PNGs; descriptions align with paper figures (e.g., fig_growth_decomposition, fig_lambda_timeline, fig_credit_risk).

### 5. Calibration and Results
- Parameter values are reasonable and sourced (Appendix C table; code sources in `src/ai_lab_investment/calibration/data.py`). α=0.40 and η≈0.07 are consistent with scaling‑laws literature; r in 10–18% spans plausible WACCs.
- Sensitivity is covered in Phase 1/3/4 figure suites; tests ensure monotonicities where expected.
- Revealed beliefs results: methodology is promising, but the inversion currently compares CapEx/Revenue (flow) to I/V where V is a present value (`src/ai_lab_investment/calibration/revealed_beliefs.py:120-136`). See Critical Issues: adjust to a flow‑consistent denominator (e.g., π(X*,K*) or annualized PV) or revise the text to match I/Value.
- Growth decomposition: computations match the described components and behave sensibly over X and K.

### 6. Slides Review
- Completeness: Covers motivation, model, results, calibration, revealed beliefs, and policy. The “Dario dilemma” framing is clear.
- Clarity: Self‑contained for a conference talk; math is appropriately simplified.
- Consistency: Slide claims match the paper except for the λ→duopoly trigger statement (address per above).

## Summary of Issues
### Critical Issues
- Duopoly λ‑dependence mismatch
  - Paper claims X_P ↓ in λ (`paper/_model.qmd:205`), figures and docstrings imply the same, but code’s H‑regime equilibrium is λ‑independent (`duopoly.py:92-105, 148-156`).
  - Fix: either (a) revise Proposition 3(ii), captions, and remove the λ–duopoly figure (Phase 2) or (b) extend equilibrium to incorporate λ via L‑regime continuation values in L(X) vs F(X).
- Revealed‑beliefs inversion units/definition mismatch
  - Code compares CapEx/Revenue (flow) to I/V where V is PV (`src/ai_lab_investment/calibration/revealed_beliefs.py:120-136`; paper eq. `paper/_valuation.qmd:11-20` says I/V=CapEx/Revenue).
  - Fix options: (1) Use flow revenue at the trigger for the denominator: π(X*,K*) = X*·K*^α − δK*; or (2) annualize PV (divide V by A_s) so that I/(V/A_s) ≈ I/flow; or (3) change the paper to define intensity consistently as CapEx / PV(Value).
- Discount rate convention inconsistency
  - Paper: r is risk‑free (`paper/_model.qmd:18`); code/docs: r is WACC (`src/ai_lab_investment/models/parameters.py:15-20`).
  - Fix: declare the measure (risk‑neutral with r risk‑free, μ risk‑neutral) or adopt risk‑adjusted cash flows with r=WACC and retitle accordingly.

### Major Issues
- Appendix A Step 2 derivation for K*: complete or explicitly mark as solved numerically (`paper/_appendix.qmd:23-57`).
- Abstract and Section text: replace “closed‑form duopoly triggers” with “semi‑analytical characterization” (1‑D optimization + root finding).
- Define β_s, β_s^- inline in the duopoly section before use for reader clarity (`paper/_model.qmd:155-167`).

### Minor Issues
- Acknowledge section in front matter contains a placeholder (“We thank … ~~”): update before submission (`paper/index.qmd:22-25`).
- Unify figure style between Phase modules and paper generator (minor typography differences); current output is publication‑quality regardless.
- Consider exposing time‑to‑build τ≠0 in a robustness figure (τ is present in params but unused in current analytics).

## Overall Recommendation
Revise and resubmit. Best fit: RFS. The contributions are strong and the code is in good shape; aligning the λ‑dependence claims with the implemented model and fixing the inversion definition are necessary for submission‑readiness. Once these are addressed (along with minor notation/derivation clean‑ups), the package will be competitive at a top finance outlet.
