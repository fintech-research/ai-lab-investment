# Consolidated Review Report: Investing in Artificial General Intelligence

**Date:** 2026-02-24
**Reviewers:** Claude Code, Codex, OpenCode

---

## Executive Summary

Three independent AI reviewers examined the codebase, paper, figures, slides, and calibration for the project "Investing in Artificial General Intelligence." All three reviewers agree the paper addresses a first-order economic question with a well-constructed theoretical framework, clean code architecture, and publication-quality writing. All recommend revision before submission.

The reviews converge on several critical findings: (1) two code bugs in the duopoly default boundary computation that affect all leveraged results, (2) a model specification inconsistency between the single-firm/duopoly models and the N-firm extension regarding how training compute enters revenue, (3) stale baseline numbers in the paper text that do not match current code output, and (4) slides that are substantially out of date with the current paper. Additionally, the reviews surface notation inconsistencies, gaps in the calibration narrative, and opportunities to strengthen the test suite.

**Consensus recommendation:** Major revision needed. **Target journal:** RFS (two reviewers) or JF (one reviewer).

---

## Agreement Matrix

The table below summarizes where the three reviewers agree, partially agree, or provide unique findings.

| Finding | Claude Code | Codex | OpenCode | Consensus |
|:--------|:-----------:|:-----:|:--------:|:---------:|
| Paper well-written, important topic | Yes | Yes | Yes | Unanimous |
| Code structure clean, well-organized | Yes | Yes | Yes | Unanimous |
| Slides out of date with paper | Yes | Yes | Yes | Unanimous |
| Training allocation ($\phi$) inconsistency across model phases | Yes | Partial | Yes | Strong |
| Notation inconsistencies ($\lambda$, $\phi$, $c_D$) | Yes | Yes | -- | 2 of 3 |
| $\eta$ calibration weakly motivated | Yes | Yes | -- | 2 of 3 |
| `_negative_root` bug (wrong discount rate) | Yes | -- | -- | 1 of 3 |
| Equity value bracket bug | Yes | -- | -- | 1 of 3 |
| Paper baseline numbers stale | Yes | -- | -- | 1 of 3 |
| Broken test dependencies | -- | Partial | Yes | Environment-specific |
| Target journal: RFS | Yes | -- | Yes | 2 of 3 |
| Target journal: JF | -- | Yes | Yes | 2 of 3 |

---

## Critical Issues

These issues affect the correctness of core results and must be resolved before submission.

### C1. Default Boundary Code Bugs (Claude Code)

Two bugs in `src/ai_lab_investment/models/duopoly.py` affect all results involving leverage and default risk:

- **Wrong discount rate in `_negative_root`** (line 359): Uses `c = -p.r` instead of `c = -(p.r + lam_tilde)`. The negative characteristic root should incorporate the regime-switching term. At baseline parameters, the code computes $\beta^- = -1.649$ while the paper formula gives $\beta^- = -2.335$ -- an 11% error in the default boundary multiplier.

- **Equity value default option bracket** (lines 411--415): Double-counts the operating cost term (`2 * delta*K/r`) and omits the equity contribution $(1-\ell)I(K)$. The smooth-pasting condition $E(X_D) = 0$ is not analytically satisfied; a `max(equity, 0)` clamp masks the error at runtime.

**Affected results:** Proposition 2 quantitative magnitudes, Proposition 3 parts iv--v, credit spreads, AI investment dilemma with leverage, `fig_default_boundaries`, `fig_credit_risk`.

*Note:* Only Claude Code identified these bugs. Codex reviewed the default boundary code and found it "consistent with standard Leland structure" but did not numerically verify the discount rate. OpenCode confirmed the default boundary "matches Proposition 2 and 3" at a higher level. The specificity and numerical evidence from Claude Code's review are compelling -- these bugs should be verified and fixed.

### C2. Model Specification Inconsistency for $\phi$ (OpenCode, Claude Code)

The single-firm/duopoly models (Phases 1--2) and the N-firm extension (Phase 3) use fundamentally different revenue functions:

- **Phase 1/2** (`base_model.py`, `duopoly.py`, `_model.qmd`): H-regime revenue is $\pi = X(\phi K)^\alpha$, where training compute directly generates revenue. The optimal $\phi^*$ is numerical and depends on $\lambda$, $r$, etc. Current code gives $\phi^* \approx 0.701$.

- **Phase 3** (`nfirm.py`, slides): Revenue is $\pi = X \cdot e^{\text{quality}} \cdot ((1-\phi)K)^\alpha$, where quality comes from cumulative training. This yields the closed-form $\phi^* = \eta/(\alpha + \eta) \approx 15\%$.

The paper text describes the first approach; the slides present the second. This undermines the claim of a "unified" framework. A single specification must be chosen and applied consistently.

### C3. Stale Baseline Results in Paper Text (Claude Code)

The paper (`_calibration.qmd:131-132`) states $X^* \approx 0.49$, $K^* \approx 0.55$, $\phi^* \approx 0.30$, but the current code produces $X^* = 0.027$, $K^* = 0.055$, $\phi^* = 0.701$. Project memory confirms $\phi^* \approx 0.701$, indicating the paper text is from a previous model version. The slides report yet a third set of values ($X^* \approx 0.016$). All three sources disagree.

---

## Major Issues

### M1. Slides Require Complete Refresh (All Three Reviewers)

All reviewers flagged the slides as inconsistent with the current paper:

- The "Training-Inference Allocation" slide presents a completely different model specification and $\phi^* \approx 15\%$ (Claude Code).
- The "Duopoly: Default Risk" slide omits the $\beta_s^-/(\beta_s^- - 1)$ option-value factor (Claude Code).
- The slides reference "Proposition 5" and formulas not present in the paper (OpenCode).
- Baseline numerical values in the slides differ from both the paper and the code (Claude Code).
- Slides use bare $\lambda$ throughout while the paper distinguishes $\lambda_0$, $\tilde{\lambda}$, $\lambda_{\text{true}}$ (Claude Code, Codex).

### M2. Parameter Inconsistency: $\lambda_0$ vs. $\tilde{\lambda}$ (Claude Code, Codex)

The paper's Table 3 lists $\lambda_0 = 0.05$ with $\xi = 0$, which by Equation 2 implies $\tilde{\lambda} = 0.05$. But the text states "the total effective rate $\tilde{\lambda} = 0.10$ per year," and the code uses `lam = 0.10`. The table should either list $\lambda_0 = 0.10$ or explain the additional component.

### M3. Arrival-Rate Elasticity $\eta$ Poorly Motivated (Claude Code, Codex)

Both reviewers flagged that the mapping from neural scaling law exponents (Kaplan/Hoffmann) to the arrival-rate elasticity $\eta = 0.07$ lacks a clear derivation. The paper acknowledges this is the calibration's "weakest link." Recommendations:

- Explain how loss-vs-compute translates to arrival-rate responsiveness (Codex).
- Label $\eta$ clearly as "inferred" rather than "directly observed" (Codex). [Note: the current revision already does this.]
- Add a sensitivity table for implied $\lambda$ with respect to $\eta$ (Codex, Claude Code).

### M4. Notation Inconsistencies (Claude Code, Codex)

- **$\lambda$ vs. $\tilde{\lambda}$ vs. $\lambda_0$**: Three related symbols used inconsistently across paper, slides, and code.
- **$\phi$ vs. $\Phi$**: `base_model.py` has a legacy alias `_phi` for the option-premium ratio $\Phi$ (not training share). Rename to `_Phi_ratio` to avoid confusion (Codex).
- **$c_D$ vs. $c_d$ vs. $d$**: The coupon notation varies between the main text and appendix (Claude Code).
- **$\beta_s^-$**: Generic subscript $s$ is confusing when default only occurs in regime L. Use $\beta_L^-$ (Claude Code).

### M5. Overflow Warnings in Duopoly Comparative Statics (Claude Code)

Eight `RuntimeWarning`s for overflow in `duopoly.py` during sigma sensitivity analysis (lines 285, 511, 740, 778). These produce `inf`/`nan` that propagate silently. Add overflow guards.

### M6. Missing Literature (Claude Code)

Five references absent from the literature review despite direct relevance:

- **Dixit (1989)** -- canonical hysteresis paper (entry/exit under uncertainty)
- **Pastor and Veronesi (2009)** -- technological revolutions and regime switching
- **Trigeorgis (1996)** -- compound options and sequential investment
- **Grenadier and Malenko (2011)** -- real options signaling
- **Lambrecht and Perraudin (2003)** -- real options in duopoly with incomplete information

### M7. Weak $\alpha = 0.40$ Motivation (Claude Code)

The paper argues $\alpha = 0.40$ from "GPU utilization rates decline as capacity grows," but this is a utilization argument, not a revenue elasticity argument. The mapping is not explained. Sensitivity analysis shows $\alpha$ is among the highest-elasticity parameters.

---

## Minor Issues

### Testing and Code Quality

| # | Issue | Source |
|:--|:------|:-------|
| m1 | Vacuous tests: `test_valuation.py:121-142` passes even when computation fails; `test_calibration.py:72-78` checks positivity, not ordering | Claude Code |
| m2 | Missing edge case tests: $\lambda = 0$, $\sigma \to 0$, $N = 1$, high $\lambda$ | Claude Code |
| m3 | Parameter validation branches (`parameters.py`) untested (76% coverage) | Claude Code |
| m4 | Copy-pasted multi-start optimization loops appear 4 times -- extract shared helper | Claude Code |
| m5 | String-based regime dispatch (`"H"`/`"L"`) with no validation; typos fail silently | Claude Code |
| m6 | Magic number `1e20` used as sentinel in 6 places with inconsistent `1e19` threshold | Claude Code |
| m7 | `time_to_build` parameter `tau` present in `ModelParameters` but unused in analytics; note as future work | Codex |
| m8 | Tight denominator guard `abs(Q_L) < 1e-15` in `base_model.py:166`; widen to `1e-10` | Claude Code |
| m9 | NFirmModel returns non-converged results with no convergence flag for callers | Claude Code |
| m10 | Dependency version pins (`numpy>=2.4.2`, `scipy>=1.17.0`) may cause failures in some environments | OpenCode |

### Paper and Figures

| # | Issue | Source |
|:--|:------|:-------|
| m11 | `fig_comparative_statics` panel (d): label says "Depreciation $\delta$" -- should be "Operating cost rate $\delta$" | Claude Code |
| m12 | Sensitivity analysis could be expanded: two-way plots for $(r, \alpha)$, confidence regions for revealed beliefs | Claude Code |
| m13 | Abstract: "semi-analytical characterization" should be "analytical existence and numerical characterization" | Claude Code |
| m14 | Cahn (2024) "$600B gap" figure in conclusion may be outdated | Claude Code |
| m15 | Tullock revenue function (Eq. 5): brief note explaining $[(1-\phi_i)K_i]^{2\alpha}$ equals capacity $\times$ share would help clarity | Claude Code |
| m16 | Add precise citations for training fraction estimates and CapEx intensities in `CalibrationData` | Codex |
| m17 | Include brief appendix note on multi-start optimization strategy and sentinel-value rejection | Codex |
| m18 | `fig_firm_comparison`: "Revenue growth (2024-2025x)" suffix "x" is non-standard | Claude Code |
| m19 | Endogenous $\lambda$ fixed-point loop: explicit code not found in `base_model.py` (may be in pipeline) | OpenCode |
| m20 | Data sourcing: add exact report/filing links for calibration inputs | Codex |

---

## Reviewer Disagreements

### Journal Target

- **Claude Code:** RFS (strongest fit for theory-with-calibration in the Leland tradition; JF prefers sharper theory or stronger empirics; Econometrica requires methodological novelty).
- **Codex:** JF (topical fit with corporate investment, default, and real options; clean empirical hooks via revealed beliefs).
- **OpenCode:** RFS or JF (corporate finance mechanics and revealed beliefs angle suit both).

**Synthesis:** RFS is the safer target given the calibration-over-estimation approach. JF is viable if the empirical content (revealed beliefs) is strengthened.

### Severity of the $\phi$ Inconsistency

- **OpenCode** rates this as the most critical issue, describing it as invalidating the "unified framework" claim.
- **Claude Code** identifies it as part of the slides-paper mismatch but focuses more on the code bugs.
- **Codex** mentions $\phi$ overloading as a naming issue but does not flag the model specification conflict.

**Synthesis:** This is a critical issue that must be resolved. The paper and code should use a single, consistent revenue specification across all phases.

### Code Bug Severity

- **Claude Code** identified two specific code bugs with numerical evidence (11% error in default boundary).
- **Codex** reviewed the same code and found it "consistent" -- but was unable to run tests to verify numerically.
- **OpenCode** confirmed the code "matches Proposition 2 and 3" at a high level but also could not run tests.

**Synthesis:** Claude Code's findings include specific line numbers and numerical verification. These bugs should be investigated immediately. The other reviewers' inability to run the code may explain why they did not catch these issues.

---

## Prioritized Action Plan

### Phase 1: Critical Fixes (Before Any Submission)

1. **Fix the two default boundary bugs** in `duopoly.py` (C1). Verify the negative root uses $r + \tilde{\lambda}$ and the equity value bracket matches the paper's formula. Regenerate all leveraged results and figures.

2. **Resolve the $\phi$ model specification** (C2). Choose one revenue function and apply it consistently across `base_model.py`, `duopoly.py`, `nfirm.py`, paper, and slides.

3. **Update all stale baseline numbers** (C3). Run the current code and update `_calibration.qmd` and all result discussions to match.

4. **Verify text-figure consistency** throughout. Cross-check `fig_competition_effect`, `fig_credit_risk`, and `fig_default_boundaries` after code fixes.

### Phase 2: Major Revisions

5. **Refresh the slides** to match the current paper (M1).

6. **Perform a notation consistency pass** across paper, code, and slides (M2, M4).

7. **Strengthen the $\eta$ and $\alpha$ calibration narrative** (M3, M7). Add sensitivity tables.

8. **Add overflow guards** to duopoly comparative statics (M5).

9. **Add missing literature** (M6).

### Phase 3: Polish

10. **Strengthen weak tests** and add edge case coverage (m1--m3).

11. **Code cleanup**: extract multi-start helper, add regime validation, name sentinel constants (m4--m6).

12. **Figure label fixes** and minor paper edits (m11--m20).

---

## Overall Assessment

The paper makes a genuine and novel contribution: integrating training-inference allocation, regime switching, endogenous default, and oligopoly competition into a unified real options framework for AI investment. The "faith-based survival" mechanism and "AI investment dilemma" are original and economically compelling. The writing quality is excellent and the codebase is well-structured.

However, the critical issues -- code bugs in the default boundary, model specification inconsistency across phases, and stale baseline numbers -- must be resolved before the quantitative results can be trusted. The slides require a complete rewrite to match the current paper. After addressing these issues, the paper would be competitive at RFS or JF.
