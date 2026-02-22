# Consolidated Review Report (v2)

**Based on:** Three independent reviews (Claude Opus 4.6, OpenAI Codex, Gemini 3 Pro Preview)
**Date:** 2026-02-22

## Executive Summary

Three independent reviewers examined both the codebase and the accompanying paper/slides after the first round of fixes (commit `431f783`). All three confirm that the core implementation is faithful to the paper's mathematical framework, the test suite is robust for model logic (80-100% coverage on core modules), and the research question is timely and compelling. All three recommend **Revise and Resubmit** before journal submission, with **Review of Financial Studies (RFS)** as the primary target (JF secondary; Econometrica a reach without substantially expanded proofs).

Compared to the v1 consolidated review, the critical bugs (revenue double-counting, firm data inconsistency, missing revealed beliefs results) appear resolved. The v2 reviews converge on a new set of issues centered on **paper-code alignment** (discount rate convention, lambda-duopoly dependence, revealed beliefs dimensionality), **incomplete proofs**, and **stale figures/slide text**.

---

## Issues Flagged by All Three Reviewers (Highest Confidence)

### 1. Discount Rate Convention Inconsistency

**Severity: Critical** | Claude: Major, Codex: Critical, Gemini: Implicit

The paper describes $r$ as the "risk-free rate" (`_model.qmd:18`), while the code documents $r$ as "WACC" (`parameters.py:15-20`), and the calibration uses $r = 0.12$ (a WACC-level rate, not risk-free). This ambiguity undermines the pricing framework: risk-neutral pricing requires risk-free $r$ with risk-adjusted drift, while WACC-based discounting implies a different valuation approach.

- **Claude:** Lists "risk neutrality" as a limitation in `_discussion.qmd` but model uses WACC
- **Codex:** Explicitly flags text says "risk-free" but code says "WACC"
- **Gemini:** Notes the calibrated $r = 0.12$ is clearly WACC-level

**Recommended fix:** Add a footnote or remark in Section 2 clarifying the pricing approach. Either (a) declare risk-neutral pricing with risk-free $r$ and specify risk-adjusted drifts, or (b) adopt the Dixit-Pindyck convention of WACC-based discounting with physical drifts and retitle $r$ accordingly throughout.

### 2. Revealed Beliefs Identification / Dimensionality Concern

**Severity: Critical** | Claude: Major, Codex: Critical, Gemini: Critical

All three reviewers independently flag problems with the revealed beliefs inversion, though from different angles:

- **Gemini:** The model computes $I(K)/V(X,K)$ (dimensionless: stock/stock) but compares it to CapEx/Revenue (flow/flow, or stock/flow depending on CapEx definition). If $V \approx \text{Rev}/(r-\mu)$, then $I/V \approx (I/\text{Rev}) \cdot (r-\mu)$. Directly equating $I/V$ to CapEx/Rev implicitly assumes $r - \mu \approx 1$, which is false ($0.12 - 0.06 = 0.06$).
- **Claude:** Anthropic-like and CoreWeave-like produce identical $\hat{\lambda} = 0.95$ despite very different WACCs, leverage, and business models -- both have CapEx/Revenue = 2.00, suggesting the inversion is primarily driven by a single sufficient statistic rather than the rich firm-level heterogeneity the paper claims to exploit.
- **Codex:** Code compares CapEx/Revenue (flow) to $I/V$ where $V$ is PV, creating a units mismatch.

**Recommended fix:** (1) Report partial sensitivities $\partial\hat{\lambda}/\partial r$, $\partial\hat{\lambda}/\partial\ell$, etc. to demonstrate firm-specific parameters matter. (2) Normalize the inversion consistently -- either use $I(K)/(X K^\alpha)$ as model intensity (flow-consistent) or redefine observed intensity as CapEx/PV(Value). (3) If $\hat{\lambda}$ is effectively a monotone function of CapEx/Revenue alone, be transparent about this limitation.

### 3. Appendix A Step 2: Incomplete K* Derivation

**Severity: Major** | Claude: Major, Codex: Major, Gemini: Minor

All three note that the proof of Proposition 1's optimal capacity uses an informal "dominant balance" / "$\delta$-small" asymptotic argument rather than a rigorous derivation.

- **Claude:** The transition from the $\delta = 0$ leading-order solution to the general FOC is abrupt; existence condition is asserted without proof.
- **Codex:** Recommends completing the full FOC algebra or explicitly stating K* is obtained by 1-D numerical optimization.
- **Gemini:** Notes the proof is logical but incomplete.

**Recommended fix:** Either provide the full FOC for general $\delta > 0$ or explicitly state that $X^*(K)$ is closed-form while $K^*$ is found by 1-D numerical optimization, preserving smooth-pasting. The abstract should correspondingly say "semi-analytical characterization" rather than implying fully closed-form solutions.

### 4. Target Journal: RFS

All three reviewers recommend **Review of Financial Studies** as the primary target. JF is secondary (would benefit from stronger empirical content). Econometrica requires substantially more rigorous proofs and formal identification theorems.

---

## Issues Flagged by Two Reviewers (High Confidence)

### 5. Lambda-Duopoly Dependence Mismatch

**Severity: Critical** | Codex: Critical, Claude: Related caveat

The paper claims $X_P$ decreases with $\lambda$ (Proposition 3(ii), `_model.qmd:205`), but the implemented H-regime duopoly equilibrium uses $A_H$ and $\beta_H$ only, which are independent of $\lambda$ (`duopoly.py:92-105`). The Phase 2 figure function `plot_lambda_duopoly` (`phase2.py:369-373`) asserts this "key insight" but would plot flat lines under the current formulation.

**Recommended fix:** Either (a) revise Proposition 3(ii) to clarify that preemption triggers are $\lambda$-independent within regime H, removing or reworking the figure, or (b) extend the equilibrium to incorporate $\lambda$ via L-regime continuation values in the leader-follower comparison.

### 6. Incomplete Proofs (Propositions 1, 3, 4(iii), 6)

**Severity: Major** | Claude: Major, Codex: Major

- **Proposition 1:** Capacity derivation uses physicist's asymptotic argument, not rigorous proof. Existence condition asserted without proof.
- **Proposition 3:** Uniqueness argument claims "leader value grows linearly in X" but leader value includes $X^{\beta_s}$ ($\beta_s > 1$), which is superlinear.
- **Proposition 4(iii):** Asserts total capacity increases with N without formal bound. Required condition $f^\alpha > 1 - 1/N$ not verified.
- **Proposition 6:** Entirely qualitative. Identifies channels but provides no formal magnitude comparison.

**Recommended fix:** For Prop 1, provide full FOC or state as fixed-point characterization. For Prop 4(iii), prove the bound or weaken to numerical finding. For Prop 6, add Taylor expansion around $\lambda_\text{true}$.

### 7. Figure 8 Data-Figure Mismatch / Stale Figures

**Severity: Critical** | Claude: Critical, Codex: Related

Claude identifies that `fig_firm_comparison.png` shows values inconsistent with current `data.py` (bars at ~0.55, 0.65, 2.5, 3.7 vs computed ratios of 2.00, 1.25, 1.09, 2.00), strongly suggesting figures were generated from a previous data version.

**Recommended fix:** Regenerate all figures by running `python paper/generate_figures.py`. Update slide figure copies accordingly.

### 8. Slide Numerical Claims Don't Match Model Outputs

**Severity: Major** | Claude: Critical (detailed), Codex: Related

Multiple numerical values in slide text are inconsistent with current model outputs:

| Claim | Location | Stated | Actual | Factor off |
|-------|----------|--------|--------|------------|
| $X^* \sim 0.49$ | `_calibration.qmd:42` | 0.49 | ~0.016 | ~30x |
| $X_F \sim 0.66$ | `_calibration.qmd:46` | 0.66 | ~1.0 | ~1.5x |
| Preemption cuts trigger to ~50% | `_model.qmd:106` | 50% | ~10-30% | ~2x |
| Growth options >60% at K/K*<0.3 | `_results.qmd:52` | K/K*<0.3 | K/K*~0.1 | ~3x |

**Recommended fix:** Recompute all numerical claims from current model code and update slide text.

### 9. Notation Overloading

**Severity: Moderate** | Claude: Major, Codex: Minor

- $D$ used for three meanings: option value constant $D_L$, face value of debt $D_0$, debt value function $D(X)$
- Coupon notation inconsistent: $c_d$ (rate), $c_D$ (payment), $d$ (payment)
- $A_s$ multiplier introduced but written inline in some equations
- $\beta$ used inconsistently ($\beta_H$, $\beta_s^-$, $\beta_s$, $\beta$ without subscript)

**Recommended fix:** Add notation table. Rename $D_L$ to $G_L$ or $\tilde{C}$. Define coupon notation clearly.

### 10. Orphaned Bibliography Entries

**Severity: Moderate** | Claude: Major, Codex: Minor

10 of 31 bibliography entries are never cited, including directly relevant ones:
- Pawlina & Kort (2006) on asymmetric duopolies
- Epoch AI (2024) and Sevilla et al. (2022) on AI compute trends
- Korinek (2024) on AGI scenarios
- Leland (1996) on optimal capital structure
- Black & Cox (1976) on bond valuation

**Recommended fix:** Cite relevant orphaned references where they naturally fit, remove truly irrelevant ones.

---

## Issues Flagged by One Reviewer (Investigate)

### 11. Debt Recovery Value Formula Discrepancy (Claude only)

**Severity: Major**

Paper defines recovery as $(1-b)V_s(X_D, K)$ where $V_s$ is net of operating costs. Code (`duopoly.py:270`) computes recovery using gross asset value (adding back $\delta K/r$). Difference is $(1-b)\delta K/r \approx 0.175$ per unit capacity -- material for credit spread calculations.

**Fix:** Align paper formula with code or vice versa.

### 12. Dario Dilemma Omits Timing Discount (Claude only)

**Severity: Major**

Paper's appendix includes a $(X_0/X^*)^{\beta(\lambda_\text{true})}$ discounting factor in NPV. Code (`valuation.py:228-290`) computes NPV at trigger without this factor, ignoring time value of reaching different triggers.

**Fix:** Multiply by `(X_0 / X_star) ** beta_true` or document as simplification.

### 13. N-Firm Contest Share Bug with Training Fraction (Claude only)

**Severity: Major (when training enabled)**

In `nfirm.py:79-81`, own capacity is adjusted for training fraction but competitor capacities use raw $K^\alpha$. Impact is zero at default `training_fraction=0.0` but produces incorrect results when training allocation is enabled.

**Fix:** Adjust competitor capacities by $(1 - \text{training\_fraction})$ in `contest_share`.

### 14. Growth Decomposition Double-Counting (Claude only)

**Severity: Moderate**

In `valuation.py:66-83`, `option_val` from `option_value_L` already embeds the switching option, but `regime_switch` is computed separately. Then `expansion_option = option_val - assets` already contains part of the switching value.

**Fix:** Verify decomposition is additive by construction or adjust `expansion_option` to subtract `regime_switch`.

### 15. Missing Guard for horizon=0 in default_probability (Claude only)

**Severity: Minor (code bug)**

`valuation.py:190-192`: `sigma * np.sqrt(horizon)` gives division by zero when `horizon=0`.

**Fix:** Add `if horizon <= 0: return 0.0` guard.

### 16. "We" with Single Author (Claude only)

**Severity: Minor**

"We" used throughout but only one author listed.

**Fix:** Change to "I" or add co-authors.

### 17. Training-Inference Allocation Disconnected (Claude only)

**Severity: Minor**

Section 3.2 (`_extensions.qmd`) produces Proposition 5 but is never used in calibration or revealed beliefs. Quality dynamics are underdeveloped.

**Fix:** Either integrate into revealed beliefs analysis or note explicitly as illustrative.

### 18. Missing Sensitivity Table (Claude only)

**Severity: Minor**

No formal table showing elasticities of key outputs ($X^*$, $K^*$, $\hat{\lambda}$) to each parameter. Only qualitative descriptions and comparative statics figures.

**Fix:** Add sensitivity table in calibration section or appendix.

### 19. Placeholder Acknowledgments (Codex only)

**Severity: Minor**

`paper/index.qmd:22-25` contains placeholder "We thank ... ~~".

**Fix:** Update or remove before submission.

### 20. Soft Assertions in Tests (Claude only)

**Severity: Minor**

Several tests use conditional assertions (`if condition: assert ...`) that silently pass. `test_symmetric_duopoly_revenue` is tautological. `test_shares_sum_to_one` uses 10% tolerance.

**Fix:** Replace soft assertions with unconditional ones or explicit `pytest.skip()`. Fix tautological test to swap arguments. Tighten tolerances.

---

## Reviewer Agreement Matrix

| Issue | Claude | Codex | Gemini | Consensus |
|-------|:------:|:-----:|:------:|:---------:|
| Discount rate convention | X | X | X | **3/3** |
| Revealed beliefs identification/dimensionality | X | X | X | **3/3** |
| Appendix A K* derivation incomplete | X | X | X | **3/3** |
| RFS as target journal | X | X | X | **3/3** |
| Revise and resubmit | X | X | X | **3/3** |
| Lambda-duopoly dependence mismatch | - | X | - | 1/3* |
| Incomplete proofs (Props 1, 3, 4, 6) | X | X | - | 2/3 |
| Figure 8 stale / data-figure mismatch | X | X | - | 2/3 |
| Slide numerical claims wrong | X | X | - | 2/3 |
| Notation overloading | X | X | - | 2/3 |
| Orphaned bibliography | X | X | - | 2/3 |
| Debt recovery formula discrepancy | X | - | - | 1/3 |
| Dario dilemma timing discount | X | - | - | 1/3 |
| N-firm contest share bug (training) | X | - | - | 1/3 |
| Growth decomposition double-counting | X | - | - | 1/3 |
| Missing default_probability guard | X | - | - | 1/3 |
| "We" with single author | X | - | - | 1/3 |
| Training-inference disconnected | X | - | - | 1/3 |
| Missing sensitivity table | X | - | - | 1/3 |
| Placeholder acknowledgments | - | X | - | 1/3 |
| Soft/tautological tests | X | - | - | 1/3 |

*Lambda-duopoly flagged as critical by Codex; Claude's analysis is consistent but categorizes it differently.

---

## Priority-Ordered Action Items

### P0 -- Must Fix Before Submission

1. **Clarify discount rate convention** -- unify "risk-free" (paper) vs "WACC" (code) throughout (3/3 consensus)
2. **Fix revealed beliefs dimensionality** -- normalize inversion consistently and report sensitivity to firm-specific parameters (3/3 consensus)
3. **Regenerate all figures** from current calibration data; verify Figure 8 matches `data.py` (2/3 consensus)
4. **Update slide numerical claims** to match current model outputs (2/3 consensus)
5. **Resolve lambda-duopoly dependence** -- either fix Proposition 3(ii) or extend the model (Codex critical)

### P1 -- Should Fix

6. **Complete proofs** for Propositions 1, 3, 4(iii), and 6 (2/3 consensus)
7. **Fix Appendix A Step 2** -- full FOC for K* or state explicitly as numerical (3/3 consensus)
8. **Standardize notation** -- $D$ overloading, coupon symbols, $\beta$ subscripts (2/3 consensus)
9. **Clean bibliography** -- cite or remove 10 orphaned entries (2/3 consensus)
10. **Fix debt recovery formula** discrepancy between paper and code (Claude only, material impact)
11. **Add Dario dilemma timing discount** or document simplification (Claude only)
12. **Fix N-firm contest share** for non-zero training fraction (Claude only)
13. **Soften abstract language** -- "semi-analytical" for duopoly; ensure claims match content (2/3 consensus)

### P2 -- Nice to Have

14. **Fix growth decomposition** potential double-counting (Claude only)
15. **Add sensitivity table** for key outputs (Claude only)
16. **Add horizon=0 guard** in `default_probability` (Claude only)
17. **Fix "We" to "I"** or add co-authors (Claude only)
18. **Integrate or demote** training-inference allocation section (Claude only)
19. **Fix soft assertions** and tautological tests (Claude only)
20. **Update placeholder acknowledgments** (Codex only)
