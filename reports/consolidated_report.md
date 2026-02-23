# Consolidated Referee Report and Revision Plan

## Manuscript: "Investing in Artificial General Intelligence"

**Based on reports from Referee A (Claude) and Referee B (ChatGPT)**

---

## I. Consolidated Assessment

Both referees find the paper ambitious, creative, and timely. The core idea---modeling AI-lab compute investment as a joint choice of timing, capacity, and training-inference allocation under regime switching---is novel and economically compelling. The "faith-based survival" mechanism is singled out by both as the paper's most distinctive theoretical contribution. The revealed beliefs methodology is praised as a creative application of structural modeling.

However, both referees converge on **three fundamental weaknesses** that must be addressed:

1. **The paper tries to do too much, diluting its strongest contributions.**
2. **Theoretical claims are stronger than the proofs support.**
3. **The revealed beliefs calibration is too fragile for the claims made.**

Referee A recommends **Major Revision**; Referee B recommends **Reject (with encouragement to rework and resubmit)**. The gap between these assessments reflects differing views on how far the paper is from publication-ready, not on the merits of the underlying idea.

---

## II. Merged Main Comments

### A. Scope and Focus (Both referees)

Both referees argue the paper simultaneously tries to be a theory paper, structural credit paper, calibration paper, revealed-beliefs paper, and policy paper. This breadth creates a problem: no single piece is airtight enough for a top journal.

- **Referee A:** "The integration is at times more additive than synergistic. Many individual results are standard in the constituent literatures." Recommends reorganizing to move quickly to novel elements and relegating standard results.
- **Referee B:** "You need to decide what the paper is." Proposes two paths: (i) a focused theory paper on training-inference allocation with clean propositions, or (ii) a theory + calibration note with humbler claims.

**Consensus recommendation:** Sharpen the paper around one core contribution (the training-inference allocation and faith-based survival), compress standard real-options results, substantially shorten the policy discussion, and remove the revealed beliefs section entirely (see Section E below).

### B. Proposition 1: Scope Mismatch and Proof Issues (Both referees)

- **Referee A:** The proof applies only in the baseline parameter region where the simplified $F_L = CX^{\beta_H}$ holds. It is unclear whether Figures 3-4 and Tables 4-5 use the simplified or full solution.
- **Referee B:** Identifies the same scope mismatch *and* a sign error in the concavity argument---$\alpha(\alpha - 1) > 0$ should be $< 0$ for $\alpha \in (0,1)$. The conclusion (strict concavity) likely still holds but the written proof is incorrect.
- **Referee B:** Comparative statics need to specify whether they hold under exogenous $\tilde{\lambda}$, partial equilibrium, or fixed-point equilibrium.

**Consensus recommendation:** Fix the sign error, restate the proposition with explicit domain conditions, and verify (or switch to) the full two-term solution throughout all figures and tables.

### C. Proposition 2: Missing Conditions for Faith-Based Survival (Both referees)

- **Referee A:** The sign of $\partial A_{\text{eff}}/\partial \tilde{\lambda}$ requires $R_H > R_L$, which may fail for inference-heavy firms. The paper should state a closed-form condition on $\phi$ for when faith-based survival holds. Also flags a potential error in the $\partial A_{\text{eff}}/\partial \tilde{\lambda}$ derivation (denominator terms).
- **Referee B:** Same concern---the derivative is not globally positive. The proposition overstates the proof.

**Consensus recommendation:** Add an explicit maintained condition (e.g., $\phi > \underline{\phi}$) to the proposition statement. Verify and correct the derivative. Clarify that the leverage-training substitution (Part iii) is a mechanical relationship, not an optimal strategy.

### D. Proposition 3: Proof Not Rigorous Enough (Both referees)

- **Referee A:** Part (ii) ($\phi^*_L \geq \phi^*_F$) has a formal gap---the proof only considers the monopoly phase but the leader also faces duopoly competition after follower entry. Part (v) (credit spread increasing in $\lambda_0$) is numerically verified, not proved.
- **Referee B:** The single-crossing argument is "too loose" for the enriched model with training allocation, endogenous $\tilde{\lambda}$, and default risk. Needs either a real proof or demotion to a numerical finding.

**Consensus recommendation:** Formalize the single-crossing argument with explicit conditions and a supporting lemma, or relabel parts (ii) and (v) as computational/numerical results. Add verification across the full parameter region, not just the baseline.

### E. Revealed Beliefs: Near Non-Identification (Both referees)

This is the sharpest area of agreement. Both referees point to the extreme sensitivity of $\hat{\lambda}$ to $\sigma_H$ (spanning a 300-fold range under $\pm 25\%$ perturbation) as fatal to any cardinal interpretation.

- **Referee A:** "A 300-fold range in implied beliefs from a single parameter perturbation is not a confidence set; it is near-non-identification." Recommends: (i) joint two-moment estimation instead of sequential inversion, (ii) firm-specific WACCs, (iii) verification of global monotonicity of the CapEx/Revenue-to-$\lambda$ mapping.
- **Referee B:** "Cardinal claims are not 'noisy'; they are essentially non-identified in practice." Recommends reframing as a structural interpretation device, not an estimate or revealed probability.

**Consensus recommendation:** ~~Reframe the entire section as an illustrative structural interpretation tool.~~ **Decision: Remove the revealed beliefs section entirely.** Both referees agree the cardinal identification is untenable, and removing the section addresses the overarching concern that the paper tries to do too much. The methodology could be developed into a separate companion paper once the identification issues are resolved. The AI investment dilemma result (asymmetric value loss) does not depend on the inversion and should be retained as a standalone quantitative finding.

### F. Endogenous Arrival Rate: Quantitatively Weak (Referee A, supported by B)

- **Referee A:** With $\eta = 0.07$, the endogenous channel is extremely flat---doubling training compute raises the contribution by only 5%. The model effectively reduces to exogenous $\lambda$ for most purposes. Also: the additive form across firms ignores complementarities and substitutabilities.
- **Referee B:** The double channel (training improves H-regime revenue *and* increases arrival rate) "stacks the deck." Needs clearer separation of what is robust to exogenous vs. endogenous $\lambda$.

**Consensus recommendation:** Be upfront that the endogenous channel is quantitatively small for realistic parameters. Separate exogenous-$\lambda$ and endogenous-$\lambda$ results throughout. Discuss alternative aggregation functions.

### G. Static Training Allocation (Both referees)

- **Referee A:** If dynamic reallocation were allowed, the initial $\phi^*$ would likely be lower (start with more inference, shift to training as signals arrive), which would affect the calibration. Suggests a two-period extension.
- **Referee B:** Lists this among the key modeling choices that need robustness checks.

**Consensus recommendation:** Add a two-period extension (choose $\phi_1$ at investment, update to $\phi_2$ after observing demand) to provide intuition for the direction of bias.

### H. Exposition and Length (Both referees)

- **Referee A:** At 60 pages, significant compression is needed. Move comparative statics figures (standard results) to appendix. Add a consolidated parameter table. Consider renaming "faith-based survival" for journal formality.
- **Referee B:** Compress the literature review into a sharper positioning argument. Distinguish between what is genuinely finance, what is AI-specific economics, and what is calibration context.

**Consensus recommendation:** Target 40-45 pages. Move standard real-options comparative statics to online appendix. Shorten literature review and policy discussion. Add early parameter table.

---

## III. Additional Technical Issues

| Issue | Source | Priority |
|---|---|---|
| Notation inconsistency: $X^*$ used without regime subscript (Eq 10 vs 14) | A | Medium |
| $A_{\text{eff}}$ notation: single-firm (Eq 7) vs duopoly (Eq 18) nesting not explicit | A | Medium |
| Default boundary $\beta^-_s$: which regime's parameters? | A | High |
| Tullock contest: total market is demand-determined, no market expansion from capacity | A | Medium |
| Revenue switch is binary (L: inference only, H: training only)---consider gradual mixing | A | Low |
| Absorbing H-regime: discuss implications of non-absorbing (AI winter) scenario | A | Low |
| Training fraction sources need specific citations and methodology | A | High |
| $\xi$ calibration: "approximately half" of arrival rate needs justification and robustness | A | High |
| Revenue concepts not consistently defined across archetypes | A | Medium |
| "Numerical Finding" labels should be "Computational Result" to avoid ambiguity | A | Low |

---

## IV. Revision Plan

### Phase 1: Strengthen the Theoretical Core (Highest Priority)

1. **Fix Proposition 1**
   - Correct the sign error ($\alpha(\alpha - 1) < 0$) in the concavity argument
   - Restate the proposition with explicit domain conditions (baseline parameter region where simplified $F_L$ applies)
   - Verify all figures/tables use consistent solution (simplified vs full)
   - Clarify whether comparative statics hold under exogenous $\tilde{\lambda}$ only

2. **Fix Proposition 2**
   - Verify and correct the $\partial A_{\text{eff}}/\partial \tilde{\lambda}$ derivation (check denominators)
   - Add explicit condition ($R_H > R_L$ or equivalent $\phi > \underline{\phi}$) to proposition statement
   - Verify the condition holds for all archetypes, flag CoreWeave-like case
   - Clarify that leverage-training substitution (Part iii) is mechanical, not optimal

3. **Strengthen Proposition 3**
   - Formalize single-crossing argument for the enriched model (training allocation + default)
   - For Part (ii) ($\phi^*_L \geq \phi^*_F$): account for both monopoly and post-entry phases in the proof
   - For Part (v): either derive the elasticity inequality analytically or relabel as "Computational Result"
   - Add numerical verification across the full parameter region used in calibration

4. **Clean separation of exogenous vs endogenous $\lambda$**
   - Present all core results first under exogenous $\lambda$
   - Then show which results extend (and how) when $\lambda$ is endogenous
   - Be explicit that the endogenous channel is quantitatively small for $\eta = 0.07$

### Phase 2: Remove the Revealed Beliefs Section

Both referees identified the revealed beliefs calibration as near non-identified ($\hat{\lambda}$ spans a 300-fold range under $\pm 25\%$ $\sigma_H$ perturbation). Rather than attempting to salvage a fragile exercise, removing it entirely sharpens the paper as a clean theory contribution---which is what both referees recommend as the strongest path forward.

5. **Remove Section 5 (Revealed Beliefs and Valuation) entirely**
   - Delete the inversion algorithm, archetype calibration (Table 2), sensitivity tables (Tables 4-5), and associated figures
   - Remove "revealed beliefs" from the abstract, introduction, and keywords
   - Remove the four firm archetypes (Anthropic-like, Google-like, etc.) and Table 1 if it exists solely for the inversion

6. **Retain and relocate the calibration parameters**
   - Keep the calibration of model primitives (Section 4) as it supports the comparative statics and numerical results
   - The AI investment dilemma (asymmetric value loss from over- vs under-investment) does not depend on the revealed beliefs inversion---retain it as a standalone numerical finding, either in the calibration section or a new short "Quantitative Implications" section
   - Keep the $\lambda$-timeline interpretation figure (@fig-lambda-timeline) if useful for intuition

7. **Adjust the introduction and conclusion**
   - Rewrite the contribution list to center on: (i) training-inference allocation theory, (ii) faith-based survival, (iii) duopoly preemption with default, (iv) AI investment dilemma
   - Remove the "revealed beliefs methodology" as a listed contribution
   - Strengthen the motivation for *why the theory matters* without leaning on the calibration as evidence

8. **Clean up references and notation**
   - Remove references that were cited only in the revealed beliefs section
   - Remove archetype-specific notation and parameters that no longer appear

### Phase 3: Refocus and Compress

With the revealed beliefs section removed, the paper should be significantly shorter. Target ~35-40 pages (from ~60).

9. **Reorganize the paper around the core contribution**
   - Lead with the training-inference allocation as the central innovation
   - Move standard real-options comparative statics (Figures 3, 6) to online appendix
   - Shorten the policy discussion (Section 6) substantially
   - Compress the literature review, sharpen "closest paper" comparisons
   - The paper structure becomes: Model -> Extensions (N-firm) -> Calibration -> Quantitative Implications (AI investment dilemma) -> Discussion -> Conclusion

10. **Improve exposition**
    - Add a consolidated parameter table with definitions, baseline values, and interpretations early in Section 2
    - Standardize notation: use regime subscripts consistently ($X^*_H$, $X^*_L$), clarify $\lambda$ vs $\tilde{\lambda}$
    - Make the $A_{\text{eff}}$ nesting explicit (single-firm to duopoly)
    - Define the $y$-axis labels in figure captions for standalone readability

11. **Strengthen calibration section**
    - Justify the $\xi$ calibration (50% endogenous share) and show robustness to 25%/75%
    - Provide specific citations for training fraction estimates
    - Since the calibration now serves the comparative statics rather than an inversion, it can be more concise

### Phase 4: Extensions That Would Strengthen the Paper

12. **Two-period $\phi$ extension**
    - Solve a simplified model where the firm can update $\phi$ after observing demand
    - Show the direction of bias from the static assumption
    - This directly addresses the most-flagged limitation

13. **Monte Carlo validation**
    - Simulate demand paths, investment decisions, and default events
    - Confirm theoretical triggers and default boundaries
    - Especially valuable for the preemption equilibrium

14. **Testable predictions**
    - State cross-sectional predictions formally: higher $\hat{\phi}$ firms should have lower credit spreads (conditional on leverage), higher equity betas
    - Even a preliminary match to observable market data would help
    - These predictions stand on their own from the theory, independent of the removed revealed beliefs exercise

15. **Add the asymmetry figure**
    - Plot $\Delta V(\lambda_{\text{invest}})$ for fixed $\lambda_{\text{true}}$ to visualize the AI investment dilemma
    - This is flagged as a missing figure for a key result

### Phase 5: Polish

16. **Terminology**
    - Consider whether "faith-based survival" needs a more formal alternative for the proposition statement (keep vivid language in introduction/discussion)

17. **Comparison table**
    - Add a feature comparison table (capacity choice, training allocation, regime switching, endogenous arrival, default risk, N-firm, contest competition) relative to Huisman-Kort (2015), Kumar-Yerramilli (2018), and other closest papers

18. **Additional references**
    - Engage with Bayesian updating/learning literature (Decamps-Mariotti-Villeneuve 2005, Lambrecht-Perraudin 2003)
    - Add Abel-Eberly (1996), Bar-Ilan-Strange (1998) on irreversibility/sequential investment
    - Add Morellec (2004), Strebulaev (2007) on dynamic capital structure

---

## V. Priority Order

The revision should proceed in the order above: **theory first, then remove revealed beliefs, then compress, then extensions**. Phases 1-3 are essential for any resubmission. Phase 4 would significantly strengthen the paper but is not strictly necessary for a first revision. Phase 5 is polish.

The single most impactful change is **Phase 1, items 1-3**: making the propositions match what the proofs actually establish. The second most impactful is **Phase 2, item 5**: removing the revealed beliefs section entirely. This simultaneously addresses both referees' core concern about fragile identification *and* their concern that the paper tries to do too much. Removing it lets the paper focus squarely on its strongest asset---the training-inference allocation theory and faith-based survival mechanism---which is the path both referees recommend.

The revealed beliefs methodology could be developed into a separate empirical companion paper once the identification issues (firm-specific parameters, joint estimation, better measurement of training fractions) are properly addressed.
