# Consolidated Referee Report and Revision Plan

**Paper:** "Investing in Artificial General Intelligence"
**Date:** 2026-02-23
**Sources:** Referee Report A (Claude), Referee Report B (ChatGPT)

---

## I. Executive Summary

Both referees find the paper ambitious, genuinely original, and well-written. The training-inference allocation under regime switching is recognized as a novel mechanism, and the faith-based survival channel is singled out as the paper's most compelling result. Both recommend major revision; Report B is somewhat harsher on the gap between claims and proofs.

The concerns cluster around five themes:

1. **Proof rigor** — Proposition 3 (preemption) is under-proved relative to its claims; Proposition 1 has a scope inconsistency.
2. **Over-claiming** — Prose sometimes reads stronger than what the analysis establishes, especially around calibration and "faith-based survival."
3. **Calibration grounding** — The scaling-law exponent eta is mislabeled as "directly observed"; training fractions lack sourcing; the paper straddles labs vs. infrastructure providers.
4. **Literature positioning** — Broad but not sharp enough on the exact marginal contribution; missing key predecessors.
5. **Presentation** — Length, notation inconsistencies, and mixing of analytical/numerical/narrative claims.

---

## II. Merged Major Comments

### 1. Proposition 3 (Preemption Equilibrium): Single-Crossing and Proof Rigor

**Both referees' #1 concern.** The single-crossing property is asserted via heuristic shape arguments ("approximately affine," "convex and eventually dominates") and verified numerically, but not proved. Report A asks for either analytical sufficient conditions or a clear demotion to "numerical finding." Report B is more emphatic: the enriched payoff environment (capacity choice, training allocation, leverage, regime-switching) makes the standard heuristics insufficient.

Additionally, Proposition 3(ii) (leader trains more than follower) is "good conjecture with strong numerics" (Report B) but lacks formal comparative-static derivation.

**Action required:**
- Downgrade Proposition 3(i) uniqueness to a computational result under stated shape assumptions, or provide formal sufficient conditions.
- Reframe Proposition 3(ii) as a numerical regularity unless a monotone comparative-static argument can be derived.
- More precisely: separate what is theorem vs. computational proposition vs. numerical finding. Table 2 already attempts this — make the proposition statements match it exactly.

### 2. Proposition 1: Scope Inconsistency and Presentation

Both referees note that Proposition 1 mixes exogenous lambda-tilde (xi = 0) scope with a comparative static in xi (endogenous arrival). Report A additionally notes the capacity formula is conditional on phi, not the joint optimum, which is "slightly misleading."

**Action required:**
- Cleanly separate Proposition 1 (exogenous lambda-tilde) from Corollary 1 (endogenous lambda-tilde / xi).
- Do not state d(phi*)/d(xi) inside the exogenous-lambda proof.
- Acknowledge that K* as stated is conditional on phi, not the joint optimum (or substitute phi* into K* for the reduced form).

### 3. Calibration: eta, Training Fractions, and Firm Identity

**eta = 0.07 ("directly observed").** Both referees flag this. Report A: "The mapping from scaling law exponents to arrival rate of AGI is not straightforward and involves substantial assumptions." The Kaplan/Hoffmann papers report loss-vs-compute exponents, not arrival-rate elasticities. Calling eta "directly observed" overstates empirical grounding.

**Training fractions.** Report A: phi-hat values in Table 4 are "described as estimated from industry reports but no specific sources are cited." These are crucial identification moments.

**Firm identity.** Report B raises the sharpest version: is this paper about frontier labs, infrastructure providers, or the joint ecosystem? The Leland default framework fits public-debt issuers better than VC-backed labs. The paper currently reads as all three.

**Action required:**
- Reclassify eta as "inferred" and add a substantive paragraph on the mapping from neural scaling law loss exponents to regime-switch arrival rates.
- Cite specific sources for training fraction estimates and discuss their uncertainty.
- Commit to a primary economic object. Report B recommends infrastructure providers as the cleanest finance fit. At minimum, be explicit about which archetype the Leland framework best fits and caveat the others.

### 4. Over-Claiming Relative to Analytical Status

Both referees identify a pattern: the prose (abstract, introduction, conclusion) reads stronger than the proofs support. Specific instances:

- "Optimism literally keeps the firm alive" — Report B: this is a conditional comparative static for the structural default boundary, not a general empirical claim about solvency.
- Calibration language sometimes sounds like structural identification (e.g., "rationalizing extreme commitments only under genuinely optimistic beliefs") when the exercise is illustrative.
- The "four contributions" framing (analytical, strategic, financing, quantitative) undersells the unified framework (Report A) while simultaneously over-claiming the individual parts.

**Action required:**
- Tone down rhetoric in abstract/introduction/conclusion. The mechanisms are strong enough without amplification.
- Reframe the calibration section as "disciplining magnitudes and illustrating mechanisms" (Report B), not explaining specific firms.
- Lead with the unified framework as the primary contribution; propositions flow from it.

### 5. Assumption (A3) Boundary Violation in Sensitivity Analysis

Report A identifies a concrete technical problem: the no-investment-in-L condition (A3) — (1 - 1/beta_L+) / alpha >= 1 — may be violated when alpha is pushed to 0.60 in the sensitivity analysis. At alpha = 0.60, the ratio is approximately 0.64 < 1. If violated, the simplified one-term option value is incorrect and the two-term solution is needed.

**Action required:**
- Check all sensitivity-analysis parameter combinations against (A3).
- Either restrict the sensitivity range to (A3)-admissible values, or derive and implement the two-term solution for the violating region.
- Verify Assumptions (A1)-(A3) hold at all four archetype-specific WACCs.

### 6. Literature Gaps

Report A identifies specific missing references:
- **Lambrecht and Perraudin (2003)** — real options in duopoly with incomplete information; relevant to heterogeneous beliefs.
- **Decamps, Mariotti, and Villeneuve (2006)** — irreversible investment with regime switching; structurally closest predecessor.
- **Nishihara and Ohyama (2021)** — multi-stage investment under regime switching.

Report B asks for:
- Sharper "delta" against the closest hybrid models (real options + competition + default).
- Explicit bridge to empirical corporate finance / IO implications: "What does this model let us measure or test that existing models do not?"

**Action required:**
- Add the three missing references with substantive discussion.
- Restructure the literature review: compact theory map in main text, institutional AI motivation in a separate subsection or appendix.
- Add a "testable implications" paragraph or subsection.

### 7. Faith-Based Survival: Explicit Threshold and Interpretation

Report A requests a closed-form expression for the minimum training fraction phi-underbar that ensures faith-based survival (at least for the symmetric duopoly case). Report B asks for tighter tying of the interpretation to the threshold condition and fixed-capacity assumptions.

Additionally, Report A questions Part (iii) on leverage-training substitution: is there an economic story for movement along the iso-X_D locus, or is it merely an accounting identity?

**Action required:**
- Provide the closed-form phi-underbar for the symmetric case.
- Develop the economic story for leverage-training substitution or downgrade the claim.
- Narrow the interpretation of faith-based survival to the model's conditional comparative static.

### 8. Tullock Contest Specification

Report A notes that the L-regime revenue uses [(1-phi_i)K_i]^{2alpha} in the numerator, creating a property where total industry revenue increases under asymmetric capacity. Is this desirable for the AI setting?

**Action required:**
- Add a brief discussion of the Tullock specification's properties under asymmetry and why this is (or isn't) appropriate for AI markets.

---

## III. Merged Minor Comments

1. **Notation consistency.** Both referees: lambda vs. lambda-tilde used interchangeably in places. Do a full consistency pass.
2. **Length.** Report A: 58 pages is long; Appendix C (N-firm) and Appendix F (robustness) can be condensed.
3. **Duplicate text.** "Purpose-built GPU clusters..." appears nearly verbatim twice (p. 2 and p. 7).
4. **Figure 1** adds limited content; consider moving to appendix or combining with Figure 2.
5. **Table 1** "Derived" label is overloaded (simple functions vs. endogenous-choice-dependent quantities).
6. **Equation (14)** trigger formula is implicit, not closed-form; note this.
7. **Section 4.2.1** introduces r_f (risk-free rate) not defined elsewhere; state relationship to r (WACC).
8. **Anthropic revenue** figures are hard to verify (private company); add caveat.
9. **SciPy version** should be specified for reproducibility.
10. **Section 4** mixes growth option decomposition, credit risk analysis, and AI investment dilemma; restructure into clearly motivated subsections.
11. **"Revealed beliefs"** is described as future work in conclusion but Section 4.3 essentially does it; reconcile.
12. **Equation (2)** notation lists firm-level arguments for lambda-tilde even when xi = 0; write the exogenous case separately.
13. **Assumption 1(A2)** condition needs a one-sentence economic interpretation.
14. **HJB equation (11)** should note explicitly that F_H(X) is the option value, not the installed value.
15. **Move limitations caveats forward** so they constrain interpretation of calibration results (Report B).

---

## IV. Revision Plan

### Phase 1: Theory Tightening (Highest Priority)

| # | Task | Section(s) | Effort |
|---|------|-----------|--------|
| 1.1 | Rewrite Proposition 3: separate theorem from computational proposition from numerical finding. Provide sufficient conditions for single crossing or demote uniqueness. | Sec 3, App A | High |
| 1.2 | Reframe Prop 3(ii) as numerical regularity or derive monotone comparative-static argument. | Sec 3, App A | Medium |
| 1.3 | Fix Proposition 1 scope: separate exogenous-lambda result from endogenous-lambda corollary. Remove xi comparative static from exogenous proof. | Sec 2, App A | Medium |
| 1.4 | Clarify K* is conditional on phi (or provide reduced-form after phi* substitution). | Sec 2 | Low |
| 1.5 | Check (A3) boundary across full sensitivity-analysis parameter space. Implement two-term solution or restrict parameter ranges. | App B, code | High |
| 1.6 | Verify (A1)-(A3) at all four archetype WACCs. | Sec 4, App | Low |
| 1.7 | Derive closed-form phi-underbar for symmetric faith-based survival. | Sec 3, App A | Medium |
| 1.8 | Develop economic story for leverage-training substitution or downgrade Prop 2(iii). | Sec 3 | Low |

### Phase 2: Calibration and Positioning (Second Priority)

| # | Task | Section(s) | Effort |
|---|------|-----------|--------|
| 2.1 | Reclassify eta as "inferred." Write paragraph on mapping from scaling-law loss exponents to arrival rates. | Sec 4, Table 3 | Medium |
| 2.2 | Source and cite training fraction estimates. Discuss uncertainty. | Sec 4, Table 4 | Medium |
| 2.3 | Commit to primary economic object (infrastructure providers recommended). Caveat archetype-specific Leland applicability. | Sec 1, 4, 5 | Medium |
| 2.4 | Recast calibration language as illustrative, not structural. | Sec 4 | Low |
| 2.5 | Discuss Tullock specification properties under asymmetry. | Sec 3 | Low |

### Phase 3: Literature and Framing (Third Priority)

| # | Task | Section(s) | Effort |
|---|------|-----------|--------|
| 3.1 | Add Lambrecht & Perraudin (2003), Decamps et al. (2006), Nishihara & Ohyama (2021) with substantive discussion. | Sec 1.1 / Lit review | Medium |
| 3.2 | Restructure literature review: compact theory map + separate institutional subsection. | Sec 1.1 | Medium |
| 3.3 | Lead introduction with unified framework as primary contribution; propositions as results that flow from it. | Sec 1 | Medium |
| 3.4 | Add "testable implications" paragraph connecting to empirical corporate finance / IO. | Sec 5 or new 4.x | Medium |
| 3.5 | Bridge to AI economics GE literature (Acemoglu 2024, Jones 2024): how does PE model relate? | Sec 1.1 | Low |

### Phase 4: Presentation and Polish (Final Priority)

| # | Task | Section(s) | Effort |
|---|------|-----------|--------|
| 4.1 | Full notation consistency pass (lambda/lambda-tilde, c_D/d, X_F/X_F*, r_f/r). | All | Medium |
| 4.2 | Tone down rhetoric in abstract/introduction/conclusion. | Sec 1, abstract, Sec 5 | Low |
| 4.3 | Condense Appendix C (N-firm) and Appendix F (robustness). | App C, F | Medium |
| 4.4 | Restructure Section 4 into clearly motivated subsections. | Sec 4 | Medium |
| 4.5 | Move Figure 1 to appendix or combine with Figure 2. | Sec 2 | Low |
| 4.6 | Reconcile "revealed beliefs" discussion (conclusion vs. Section 4.3). | Sec 4, 5 | Low |
| 4.7 | Fix duplicate text, minor notation issues, table classifications (see minor comments). | Various | Low |
| 4.8 | Move key limitations caveats earlier (before calibration results). | Sec 4, 5 | Low |
| 4.9 | Specify SciPy version; add Anthropic revenue caveat. | App B, Sec 4 | Low |
