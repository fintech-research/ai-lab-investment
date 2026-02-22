# Implementation Plan for Consolidated Review v2 Findings

**Date:** 2026-02-22
**Based on:** `reports/consolidated_review_v2.md`

## Overview

The v2 reviews converge on three categories of work:
1. **Foundational model fixes** (revealed beliefs, lambda-dependence, discount rate)
2. **Paper-code alignment** (proofs, notation, bibliography, figures)
3. **Code quality** (bugs, guards, tests)

This plan is ordered by dependency: later items depend on earlier ones.

---

## Phase 1: Fix Core Model Issues (Blocking — Must Complete First)

### 1.1 Fix Revealed Beliefs Methodology (P0, 3/3 consensus)

**Problem:** The revealed beliefs inversion is fundamentally broken in its current form:
- In H-regime, `X*`, `K*`, and `I/V` are all **lambda-independent** (verified: I/V = 0.187 constant across all lambda values)
- The gap function never changes sign, so `brentq` returns `None` for all firms
- Additionally, `I(K)/V(X,K)` (dimensionless) is compared to CapEx/Revenue (flow/flow), which is a units mismatch if V is a PV

**Root cause:** Lambda only enters through the L-regime characteristic equation. The H-regime trigger and capacity depend solely on `A_H = 1/(r - mu_H)` and `beta_H`, neither of which involves lambda.

**Fix (choose one approach):**
- **Option A (Recommended): L-regime inversion.** Compute investment value in regime L (where lambda matters through `A_L`, `beta_L`, and the particular solution coefficient `C`). The firm's option value in L embeds lambda through the switching continuation value. Define intensity as `I(K*) / F_L(X_current)` where `F_L` is the L-regime option value (which depends on lambda). This aligns with the narrative that firms invest *before* transformative AI arrives (i.e., in regime L).
- **Option B: Flow-consistent intensity.** Change model intensity to `I(K) / (X · K^alpha)` (investment cost / annualized flow revenue at trigger), and observed intensity to CapEx/Revenue (annual flow / annual flow). Then vary lambda to change K* and X* in L-regime.
- **Option C: Present-value-consistent.** Change observed intensity to CapEx / PV(Revenue) where PV is estimated as Revenue/(r-mu). Then use L-regime model values.

**Files to modify:**
- `src/ai_lab_investment/calibration/revealed_beliefs.py` — rewrite `infer_lambda_from_capex` and `_model_*_at_lambda` to use L-regime values
- `paper/_valuation.qmd` — update methodology description
- `paper/_appendix.qmd` — update derivation

**Verification:**
- After fix, `compute_all_revealed_beliefs()` should return non-None lambda values for all 4 firms
- Lambda values should be economically plausible (0.05-2.0 range)
- Different firms should get different lambdas (Anthropic > Google)

### 1.2 Resolve Lambda-Duopoly Dependence (P0, Codex critical)

**Problem:** Paper Proposition 3(ii) claims "preemption trigger decreases with lambda" but H-regime equilibrium is lambda-independent.

**Fix:** This is actually correct *when computed in L-regime*. The preemption equilibrium in L includes the switching continuation value which depends on lambda. Two options:
- **Option A:** Revise Proposition 3(ii) to clarify it applies to the L-regime equilibrium, not H-regime
- **Option B:** Add a comparative statics method that varies lambda, recomputes parameters, and solves the L-regime preemption equilibrium

**Files to modify:**
- `paper/_model.qmd` — revise Proposition 3(ii) statement
- `src/ai_lab_investment/figures/phase2.py` — fix or remove `plot_lambda_duopoly` if it plots flat lines
- `slides/long-form/_model.qmd` — update claim about preemption and lambda

### 1.3 Clarify Discount Rate Convention (P0, 3/3 consensus)

**Problem:** Paper says "r is the risk-free rate" but code uses r = 0.12 (WACC-level).

**Fix:** Add a footnote/remark in the model section clarifying the pricing convention. The standard real options approach (Dixit & Pindyck 1994) uses risk-adjusted discounting where r is the appropriate discount rate for the project's risk class (WACC), and mu is the risk-neutral drift (physical drift minus risk premium). This is well-established.

**Files to modify:**
- `paper/_model.qmd` — change "risk-free rate" to "risk-adjusted discount rate" or "WACC"; add footnote explaining the pricing convention
- `src/ai_lab_investment/models/parameters.py` — update docstring to match paper terminology (currently says "WACC")

---

## Phase 2: Regenerate Outputs (Depends on Phase 1)

### 2.1 Regenerate All Figures (P0, 2/3 consensus)

**Problem:** Figure 8 (`fig_firm_comparison.png`) may show values from a previous calibration. After Phase 1 fixes, all figures need regeneration.

**Action:**
```bash
uv run python paper/generate_figures.py
```

**Verification:**
- Figure 8 bar chart values should match `data.py` ratios (2.00, 1.25, 1.09, 2.00)
- All 10 figures should render without errors
- Copy updated figures to `slides/long-form/figures/` if needed

### 2.2 Update Slide Numerical Claims (P0, 2/3 consensus)

**Problem:** Multiple slide claims are stale:
- "X* ~ 0.49" — actual is 0.016 (30x off)
- "K* ~ 0.55" — actual is 0.055 (10x off)
- "Follower X_F ~ 0.66" — actual is ~1.0
- "Preemption cuts trigger to ~50%" — actually correct (53.6%)
- "Growth options >60% at K/K* < 0.3" — needs verification

**Files to modify:**
- `slides/long-form/_calibration.qmd` — update X*, K*, X_F, K_F values
- `slides/long-form/_results.qmd` — verify growth decomposition claim
- `slides/long-form/_model.qmd` — the "~50%" claim is actually correct, keep it

---

## Phase 3: Paper Revisions (Can Parallel with Phase 2)

### 3.1 Complete Proofs (P1, 2/3 consensus)

**Proposition 1 (K* derivation):**
- Replace "dominant balance" argument with explicit statement: "The optimal capacity K* is the unique solution to the FOC [equation], which we solve numerically via bounded scalar optimization. The existence of an interior solution requires [condition]."
- Alternatively, provide the full FOC for general delta > 0.

**Proposition 3 (uniqueness):**
- Fix the claim "leader value grows linearly in X" — it grows as X^beta_s (superlinear). Correct the argument.

**Proposition 4(iii) (total capacity increases with N):**
- Either prove the bound f^alpha > 1 - 1/N or weaken to "we verify numerically that..."

**Proposition 6 (Dario dilemma asymmetry):**
- Add Taylor expansion of value loss around lambda_true showing the asymmetry formally.

**Files:** `paper/_appendix.qmd`

### 3.2 Standardize Notation (P1, 2/3 consensus)

- Rename option value constant $D_L$ to $G_L$ to avoid collision with debt notation $D_0$, $D(X)$
- Define coupon notation clearly: use $d$ for coupon payment throughout, $c_d$ for coupon rate
- Add $A_s$ consistently (don't write $1/(r-\mu_s)$ inline where $A_s$ is defined)
- Consider adding a notation table

**Files:** `paper/_model.qmd`, `paper/_appendix.qmd`

### 3.3 Clean Bibliography (P1, 2/3 consensus)

- Identify which of the 10 orphaned entries should be cited vs removed
- Cite where relevant:
  - Pawlina & Kort (2006) in the duopoly section
  - Epoch AI (2024) / Sevilla (2022) in calibration
  - Korinek (2024) in revealed beliefs discussion
  - Leland (1996) in default model section
- Remove truly irrelevant entries

**Files:** `paper/references.bib`, various `.qmd` files

### 3.4 Soften Abstract Language (P1, 2/3 consensus)

- Change "analytical characterization" to "semi-analytical characterization" for the duopoly
- Ensure claims about revealed beliefs match actual numerical results (after Phase 1 fix)

**Files:** `paper/index.qmd`

### 3.5 Fix "We" to "I" (P2, Claude only)

- Single author uses "We" throughout
- Global search-and-replace in paper `.qmd` files

**Files:** All `paper/*.qmd` files

### 3.6 Update Placeholder Acknowledgments (P2, Codex only)

**Files:** `paper/index.qmd` (lines 22-25)

---

## Phase 4: Code Fixes (Can Parallel with Phase 3)

### 4.1 Fix Debt Recovery Formula (P1, Claude only)

**Problem:** Paper says recovery = $(1-b) \cdot V_s(X_D, K)$ (net of operating costs). Code adds back `delta*K/r` (gross asset value).

**Action:** Verify which is economically correct (Leland 1994 uses liquidation value of assets, which is typically gross). If gross is correct, update the paper formula. If net is correct, update the code.

**Files:** `src/ai_lab_investment/models/duopoly.py:270` or `paper/_model.qmd`

### 4.2 Fix Dario Dilemma Timing Discount (P1, Claude only)

**Problem:** Code evaluates `V(X*, K*) - I(K*)` without the timing discount $(X_0/X^*)^{\beta(\lambda_\text{true})}$.

**Action:** Either add the timing discount factor or document this as a deliberate simplification (comparing values at the trigger, not at current demand level).

**Files:** `src/ai_lab_investment/models/valuation.py:228-290` or `paper/_appendix.qmd`

### 4.3 Fix N-Firm Contest Share (P1, Claude only)

**Problem:** Own capacity adjusted for training fraction but competitors aren't.

**Fix:** Apply `(1 - training_fraction)` to competitor capacities in `contest_share`, or require callers to pass inference-only capacities.

**Files:** `src/ai_lab_investment/models/nfirm.py:73-84`

### 4.4 Verify Growth Decomposition Additivity (P2, Claude only)

**Problem:** Potential double-counting of regime switch value.

**Action:** Add a test verifying `assets + expansion_option + regime_switch == total_option_value` numerically. If it fails, adjust the decomposition.

**Files:** `src/ai_lab_investment/models/valuation.py:66-83`, `tests/test_valuation.py`

### 4.5 Add horizon=0 Guard (P2, Claude only)

**Files:** `src/ai_lab_investment/models/valuation.py:190-192`

```python
if horizon <= 0:
    return 0.0
```

### 4.6 Fix Soft Assertions in Tests (P2, Claude only)

- Replace `if condition: assert ...` with unconditional assertions or `pytest.skip()`
- Fix tautological `test_symmetric_duopoly_revenue` (swap K_i, K_j arguments)
- Tighten `test_shares_sum_to_one` tolerance from 0.1 to 1e-6

**Files:** `tests/test_base_model.py`, `tests/test_duopoly.py`, `tests/test_nfirm.py`

---

## Phase 5: Sensitivity Analysis (Depends on Phase 1)

### 5.1 Add Revealed Beliefs Sensitivity Table (P2, Claude only)

After Phase 1 fixes the revealed beliefs methodology:
- Compute $\partial\hat{\lambda}/\partial r$, $\partial\hat{\lambda}/\partial\alpha$, $\partial\hat{\lambda}/\partial\gamma$, etc.
- Present as a table showing which firm-specific parameters matter
- This addresses the identification concern (3/3 consensus)

**Files:** New content in `paper/_valuation.qmd` or `paper/_appendix.qmd`, potentially new figure

### 5.2 Add Parameter Sensitivity Table (P2, Claude only)

- Table of elasticities: $\Delta X^*/\Delta\theta$, $\Delta K^*/\Delta\theta$, $\Delta\hat{\lambda}/\Delta\theta$
- Complements the comparative statics figures with precise numbers

**Files:** `paper/_calibration.qmd` or `paper/_appendix.qmd`

---

## Dependency Graph

```
Phase 1 (Model Fixes)
  ├── 1.1 Revealed Beliefs ──────────────────────────┐
  ├── 1.2 Lambda-Duopoly ───────────────────┐        │
  └── 1.3 Discount Rate Convention          │        │
                                            ▼        ▼
Phase 2 (Regenerate)                   Phase 5 (Sensitivity)
  ├── 2.1 Regenerate Figures                5.1 Beliefs Sensitivity
  └── 2.2 Update Slide Numbers             5.2 Parameter Sensitivity

Phase 3 (Paper Revisions) ─── can run in parallel ─── Phase 4 (Code Fixes)
  ├── 3.1 Complete Proofs                              ├── 4.1 Debt Recovery
  ├── 3.2 Notation                                     ├── 4.2 Dario Timing
  ├── 3.3 Bibliography                                 ├── 4.3 Contest Share
  ├── 3.4 Abstract                                     ├── 4.4 Decomposition
  ├── 3.5 We → I                                       ├── 4.5 horizon Guard
  └── 3.6 Acknowledgments                              └── 4.6 Test Fixes
```

---

## Estimated Scope

| Phase | Items | Priority | Complexity |
|-------|-------|----------|------------|
| Phase 1 | 3 items | P0 (blocking) | High — requires model redesign for 1.1 |
| Phase 2 | 2 items | P0 | Low — scripted regeneration |
| Phase 3 | 6 items | P1-P2 | Medium — paper writing |
| Phase 4 | 6 items | P1-P2 | Low-Medium — targeted code fixes |
| Phase 5 | 2 items | P2 | Medium — new analysis |

**Critical path:** Phase 1.1 (revealed beliefs fix) is the most complex item and blocks Phase 2 and Phase 5. Start here.
