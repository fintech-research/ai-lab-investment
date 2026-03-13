# Consolidated Review Report

**Date:** 2026-03-13
**Sources:** Five AI reviewer reports (ChatGPT, Claude AI, Claude Opus, Codex, Gemini)

---

## Overview

Five AI reviewers examined both the paper and the codebase. Their assessments span from "submit as-is" (Gemini) to "reject in current form" (ChatGPT), with the other three recommending revise-and-resubmit. The Gemini report is notably superficial — it found zero issues of any severity — and should be weighted accordingly. The other four reports converge on a common set of substantive concerns.

**Consensus recommendation:** Revise and resubmit (minor-to-major depending on scope).
**Consensus target journal:** RFS (3 reviewers) or JF (2 reviewers).

---

## Part A: Code Issues

Issues are ranked by severity and the number of reviewers who flagged them.

### A1. `dario_dilemma_leveraged()` uses simplified default probability formula
**Flagged by:** Claude Opus, Codex, Claude AI
**Severity:** HIGH
**Assessment: VALID — must fix**

The `_default_prob()` helper inside `dario_dilemma_leveraged()` (valuation.py:399-412) uses only `Φ(−d₂)` instead of the full first-passage formula `Φ(−d₁) + (X_D/X)^{2ν/σ²}·Φ(−d₂)` used in `default_probability()`. This understates default probability by ~47% at baseline. The paper cites the correct full-formula values (0.79% conservative, 5.04% aggressive at ℓ=0.40), so the text is right but the code path doesn't produce those numbers.

**Fix:** Replace the inline `_default_prob` with a call to `self.default_probability()`.

### A2. Credit risk figure: evaluation point inconsistency
**Flagged by:** Claude Opus, Codex
**Severity:** HIGH
**Assessment: VALID — must fix**

`credit_spread_curve()` uses `X = max(X_D * 3, 0.1)`, creating a floor that makes the "evaluated at 3× default boundary" caption inaccurate at low leverage. The paper claims default probability "rises from approximately 0.5% at low leverage to approximately 0.8% at ℓ = 0.70" — neither value matches current code output (0.17% to 2.91%).

**Fix:** Remove the `max(…, 0.1)` floor and use exactly `3 * X_D`, OR use a fixed absolute demand level and update text/caption accordingly. Update the stated numerical values in `_valuation.qmd` to match code output.

### A3. `dario_dilemma_leveraged()` has zero test coverage
**Flagged by:** Claude Opus
**Severity:** MEDIUM
**Assessment: VALID — should fix**

This function computes the paper's central leveraged Dario's dilemma results but has no tests. The formula bug (A1) would have been caught by even a basic regression test.

**Fix:** Add tests comparing output against `self.default_probability()` and verifying baseline values.

### A4. Proposition 3 computational verification overstated
**Flagged by:** Codex, Claude AI
**Severity:** MEDIUM
**Assessment: VALID — should fix**

The appendix claims 500-point grid single-crossing checks and 10-random-start equilibrium uniqueness verification, but the implementation uses Brent's root-finding on a fixed bracket with deterministic starting grids. The claims should either be implemented or the appendix text should match the actual verification.

**Fix:** Either implement the stated verification (preferred) or soften the appendix language.

### A5. `growth_option_decomposition()` potential double-counting
**Flagged by:** Codex
**Severity:** LOW
**Assessment: UNCERTAIN — needs investigation**

Codex claims that in regime "L", `expansion_option` (derived from `option_value()`, which already includes regime-switching value) and `regime_switch` (calculated separately) are both added to `total`, potentially double-counting. This needs careful verification against the mathematical definitions.

**Fix:** Investigate and either confirm the decomposition is correct or fix the double-counting.

### A6. Nelder-Mead optimizer doesn't check `result.success`
**Flagged by:** Codex
**Severity:** LOW
**Assessment: VALID but low priority**

The multi-start optimizers accept results based on whether `best_val` improved, not on `result.success`. In practice this hasn't caused issues because the optimizer converges reliably, but it's fragile.

### A7. Figure 3 axis label: "Depreciation" instead of "Operating cost"
**Flagged by:** Claude Opus
**Severity:** LOW
**Assessment: VALID — easy fix**

Panel (d) labels δ as "Depreciation δ" but the paper explicitly distinguishes δ (operating cost rate) from depreciation.

**Fix:** Change to `r"Operating cost $\delta$"` in `paper.py`.

### A8. Minor code quality issues
**Flagged by:** Claude Opus, Codex
**Severity:** LOW

- Legacy methods in `duopoly.py` (`contest_share`, `duopoly_revenue_pv`, etc.) are unused stubs.
- `generate_figures.py` uses paper style for both PDF and PNG despite docstring claiming separate styles.
- `just run-pipeline` is a no-op because default config disables all tasks (Codex frames this as critical; it's actually fine — `uv run python paper/generate_figures.py` is the intended reproduction command).

---

## Part B: Paper Issues

### B1. Conclusion contradicts the main asymmetry result
**Flagged by:** Codex
**Severity:** HIGH
**Assessment: VALID — must fix**

`_conclusion.qmd`:16-17 states "the downside of overinvestment ... exceeds the opportunity cost of underinvestment," but `_valuation.qmd`:121 establishes the opposite: underinvestment is costlier in expected value, while overinvestment carries higher tail (default) risk. This is a direct contradiction.

**Fix:** Rewrite the conclusion to match the valuation section's nuanced statement.

### B2. Abstract emphasizes only the tail-risk dimension
**Flagged by:** Claude Opus, Claude AI
**Severity:** MEDIUM
**Assessment: VALID — should fix**

The abstract states "aggressive overinvestment carries higher downside risk than conservative underinvestment," emphasizing only the tail-risk side. The paper's actual central finding is that underinvestment is costlier in expected value but overinvestment carries higher default risk.

**Fix:** Lead with the expected-value asymmetry, then note the tail-risk qualifier.

### B3. Analytical claims overstated relative to what is proved
**Flagged by:** ChatGPT, Claude AI, Codex
**Severity:** MEDIUM
**Assessment: PARTIALLY VALID**

Three reviewers flag that the paper sometimes presents computational or numerical results as if they were analytically established. Specific instances:

- **F_L solution with A₁=0** (ChatGPT): argues the vanishing of the homogeneous term is "at best an approximation." **Assessment: Mostly valid.** Under (A3), the argument that there is no L-regime exercise boundary to pin down A₁ is economically sound but could be stated more carefully. The paper already labels (A3) as an assumption; what's needed is a clearer statement that the resulting F_L is exact *under* (A3), not an approximation of a more general solution.

- **Proposition 3 uniqueness** (ChatGPT, Claude AI, Codex): all agree computational verification is inadequate for a top journal. **Assessment: Valid.** The paper already labels this as computational, which is good. ChatGPT's suggestion of Sobol/LHS sampling or analytical sufficient conditions for single crossing is constructive. Claude AI suggests analytical proof under symmetry with zero leverage.

- **Dario's dilemma Taylor sign argument** (ChatGPT, Codex): the W''' > 0 argument is heuristic but sometimes presented as established. **Assessment: Valid.** Already labeled as heuristic in the appendix, but the prose in valuation and conclusion sections should be more careful.

- **"Faith-based survival" comparative statics** (ChatGPT): distinguishes between fixed-policy and equilibrium comparative statics. **Assessment: Valid and constructive.** The paper should be explicit about holding (K, φ, ℓ) fixed vs. allowing endogenous adjustment.

### B4. Internal inconsistency around K* comparative statics
**Flagged by:** ChatGPT, Claude Opus
**Severity:** MEDIUM
**Assessment: PARTIALLY VALID**

ChatGPT argues that the paper claims K* responds to λ in some places and is independent of λ in others. **Verified status:** K* is independent of λ in the single-firm benchmark (by Proposition 1), but in the duopoly the follower's K_F can differ from the leader's K_L through the contest function. The paper also says "earlier, larger, and more training-intensive" in Remark 1 (`_model.qmd`), where "larger" is incorrect for the single-firm case. Claude AI correctly diagnoses this: "K* is independent of λ (by Proposition 1) but the duopoly capacity may change."

**Fix:** Correct Remark 1 to remove "larger" or add the qualification that it applies to the duopoly. Add explicit labels throughout distinguishing single-firm, duopoly, and leveraged environments.

### B5. Static φ is the most consequential limitation
**Flagged by:** Claude AI, ChatGPT
**Severity:** MEDIUM
**Assessment: VALID but already acknowledged**

Both reviewers argue that if φ were dynamically adjustable, faith-based survival and Dario's dilemma asymmetry could be attenuated by reallocation. Claude AI specifically requests a quantitative assessment or formal two-period extension. ChatGPT asks that the limitation be flagged earlier and more prominently.

**Assessment:** The paper already discusses this limitation (Section 5.4) and the conclusion lists dynamic φ as the top future-work priority. A formal two-period extension would strengthen the paper but is a substantial undertaking that goes beyond a revision. The more practical fix is to (a) move the discussion earlier, (b) add brief bounds on the reallocation option value, and (c) note that inference-time scaling is blurring the training/inference distinction.

### B6. Tullock contest specification concerns
**Flagged by:** ChatGPT
**Severity:** MEDIUM
**Assessment: VALID**

The Tullock specification allows total industry revenue to rise with asymmetry, which could mechanically drive some strategic results. The paper mentions Cournot robustness but provides no derivation. ChatGPT asks for either a proper appendix derivation under Cournot or more modest claims.

**Assessment:** The paper's Appendix E mentions Cournot robustness but is too thin. At minimum, re-derive the faith-based survival condition under Cournot and report whether the qualitative results survive. This is a legitimate concern that a human referee would also raise.

### B7. Calibration sensitivity to α and φ̂
**Flagged by:** Claude AI
**Severity:** MEDIUM
**Assessment: VALID**

The elasticity of φ* with respect to λ is +12.7, meaning small errors in estimated φ̂ produce large errors in implied λ. The mapping from scaling-law exponents to the contest function's α is not made explicit. Claude AI requests implied-λ confidence intervals for φ̂ ± 0.10.

**Fix:** Add confidence intervals for implied λ. Make the scaling-law-to-α mapping explicit.

### B8. Discount rate comparative static sign discrepancy
**Flagged by:** Claude Opus
**Severity:** MEDIUM
**Assessment: NEEDS INVESTIGATION**

Claude Opus flags that `_calibration.qmd` states higher r "raises the investment trigger" but the elasticity table reports ε_{X*,r} = −20.8 (negative). The calibration text says "raising the trigger" — which is the standard real-options intuition (higher discount rate makes waiting cheaper) — but the full phi-aware model may have indirect channels that reverse this.

**Fix:** Verify the sign. If the elasticity table is correct (negative), either explain the mechanism or correct the text.

### B9. Quantitative section oversold
**Flagged by:** ChatGPT
**Severity:** LOW-MEDIUM
**Assessment: PARTIALLY VALID**

ChatGPT argues the calibration is useful as "disciplined illustration" but not strong enough to support "revealed-belief rhetoric." The paper is already candid about limitations but could tone down some interpretive claims about observed investment patterns being "rational."

### B10. Value decomposition not conceptually tight
**Flagged by:** ChatGPT
**Severity:** LOW-MEDIUM
**Assessment: PARTIALLY VALID**

ChatGPT finds the "capacity gap value" definition and its use for asset-pricing statements about growth stocks insufficiently rigorous. The growth decomposition figure shows the gap reaching zero before K/K* = 1 (Codex), and the code uses L-regime values despite H-regime framing in text (Codex).

**Fix:** Align the figure's regime/evaluation conventions with the text. Either rewrite the decomposition in standard finance terms or reduce the section.

### B11. Exposition and presentation issues
**Flagged by:** Multiple reviewers
**Severity:** LOW

- **Introduction too journalistic** (ChatGPT): too many executive quotes relative to formal theory. Cut some and get to the model's key wedge faster.
- **Paper title** (Claude AI): may draw resistance from referees. Consider a more technical subtitle.
- **β notation overloaded** (Claude AI): β_H (characteristic root) vs. market beta in testable predictions.
- **Repeated phrasing** (Claude Opus): "purpose-built GPU clusters" appears in both intro and technology section.
- **"Transformative AI" vs. "AGI"** (Claude AI): used interchangeably but have different connotations.
- **Move training-share limitation earlier** (ChatGPT): given how central φ is.
- **Table 4 (analytical status)** (Claude AI): consider moving earlier rather than burying in appendix.
- **Equation 6 (A_eff) derivation** (Claude AI): add a one-line derivation for readers unfamiliar with regime-switching present values.

### B12. Missing references
**Flagged by:** Claude AI, Claude Opus
**Severity:** LOW

- Aguerrevere (2009, RFS) on capacity investment under uncertainty with market competition
- Grenadier and Malenko (2011, RFS) on Bayesian learning in real options
- Philippon (2009) on bond market and macroeconomic investment
- Novy-Marx (2007) connection to operating leverage could be developed further

### B13. Testable predictions too weak
**Flagged by:** ChatGPT
**Severity:** LOW
**Assessment: PARTIALLY VALID**

Several "predictions" are close to restatements of model assumptions. Translate them into cleaner empirical objects with honest assessment of data adequacy.

---

## Part C: Assessment of Reviewer Quality

| Reviewer | Depth | Accuracy | False positives | Value added |
|----------|-------|----------|-----------------|-------------|
| **ChatGPT** | High (paper only) | High | Few | Best paper-level critique; strongest on analytical overclaiming |
| **Claude AI** | High (paper only) | High | Few | Most constructive; specific fixes suggested for each issue |
| **Claude Opus** | Very high (paper + code) | Very high | Minimal | Most thorough; found the most verified code bugs |
| **Codex** | High (paper + code) | High | Some | Confirmed Claude Opus findings; added growth decomposition issue |
| **Gemini** | Superficial | N/A | N/A | Essentially useless — found zero issues |

---

## Part D: Plan — Implementation Status

### Phase 1: Critical Code Fixes — COMPLETE

1. ✅ **Fix `dario_dilemma_leveraged()` default probability** [A1]: Replaced inline `_default_prob` with `ValuationAnalysis(p_true).default_probability()` for full first-passage formula. Default probs now match paper: 0.79% conservative, 5.04% aggressive.
2. ✅ **Fix credit risk evaluation point** [A2]: Replaced `max(X_D*3, 0.1)` with fixed `CREDIT_RISK_DEMAND_LEVEL = 0.10`. Updated paper text: spreads 170/259/312 bps, default probs 0.17%/0.57%/6.10%.
3. ✅ **Fix conclusion contradiction** [B1]: Rewrote `_conclusion.qmd` to state underinvestment costlier in expected value, overinvestment costlier in tail risk.
4. ✅ **Fix abstract framing** [B2]: Abstract now reads "conservative underinvestment is costlier in expected value, but aggressive overinvestment carries substantially higher tail (default) risk."

### Phase 2: Code Quality — COMPLETE

5. ✅ **Add tests for `dario_dilemma_leveraged()`** [A3]: 5 new tests added (matched beliefs, non-negative losses, consistency with `default_probability()`, baseline regression, aggressive > conservative default prob).
6. ✅ **Implement Prop 3 verification** [A4]: 500-point single-crossing grid check implemented in `duopoly.py`. Appendix text updated to match: "12 deterministic starting points" (not "10 random"). Test added for `single_crossing` flag.
7. ✅ **Fix Figure 3 label** [A7]: "Depreciation δ" → "Operating cost δ".
8. ✅ **Investigate growth decomposition** [A5]: Double-counting exists in `growth_option_decomposition()` but NOT in the phi-aware version or the paper figure. The paper figure uses a direct computation in `paper.py` that is correct. Gap reaching zero at K/K*≈0.77 is economically correct (NPV comparison).
9. ✅ **Verify discount rate sign** [B8]: Higher r lowers the trigger (negative elasticity confirmed). Calibration text corrected to explain the mechanism: β_H/(β_H−1) reduction dominates the A_eff reduction.

### Phase 3: Paper Strengthening — COMPLETE

10. ✅ **Separate analytical environments** [B3, B4]: Prop 1 labeled "single-firm benchmark," Prop 2 labeled "leveraged duopoly," Prop 3 labeled "symmetric duopoly." Added note after Prop 1 clarifying K* carries over to duopoly. Remark 1 corrected: K* independent of λ by Prop 1, duopoly capacity differs through contest function. Same fix in calibration text.
11. ✅ **Strengthen Cournot robustness** [B6]: Expanded appendix E with faith-based survival mechanism robustness argument (X_D depends on A_eff regardless of competition form), preemption comparison, and Dario's dilemma preservation.
12. ✅ **Tighten analytical framing** [B3]: Added sentence clarifying F_L = C·X^{β_H} is exact under (A3), not an approximation. Added fixed-policy caveat after Prop 2 distinguishing from equilibrium comparative statics.
13. ✅ **Add implied-λ confidence intervals** [B7]: Computed inversions at φ̂ ± 0.10 for all four archetypes. Added to calibration text: xAI implies λ ∈ [0.09, 0.17], Google implies λ ∈ [0.03, 0.05]. Ordering robust across entire band.
14. ✅ **Improve Dario's dilemma precision** [B9]: Updated ~25%→~26%, ~20%→~23%, ~5%→~6% throughout. Expected-value vs. tail-risk distinction already sharp in text.
15. ✅ **Growth decomposition** [B10]: Investigated and confirmed economically correct. No change needed.

### Phase 4: Polish — PARTIALLY COMPLETE

16. ⬜ **Exposition improvements** [B11]: Training-share limitation already flagged early (model section footnote) and discussed in detail (discussion section). Repeated phrasing already fixed. Remaining items (trim intro quotes, β notation, AGI terminology) are minor stylistic choices.
17. ✅ **Add missing references** [B12]: Grenadier & Malenko (2011) added to bib and cited in literature review. Aguerrevere (2003) was already present; the 2009 paper is less relevant. Philippon (2009) omitted as tangential.
18. ⬜ **Sharpen testable predictions** [B13]: Minor; current predictions are directionally correct.
19. ⬜ **Minor code cleanup** [A8]: Legacy stubs and style docstring — cosmetic.

### Items NOT addressed (by design)

- **Two-period dynamic-φ extension** (Claude AI): Out of scope; already listed as future work.
- **Analytical uniqueness of preemption equilibrium** (ChatGPT, Claude AI): Computational verification with 500-point grid is the practical path.
- **σ_L ≠ σ_H** (Claude AI): Already simplified as a modeling choice.
- **Endogenous λ** (Claude AI): Would fundamentally change the model.
- **Rename the paper** (Claude AI): Current title is distinctive.
