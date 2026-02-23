Referee Report on “Investing in Artificial General Intelligence”

Recommendation: Reject (encourage resubmission elsewhere after substantial revision)

This paper develops a dynamic investment model for frontier AI labs that combines irreversible investment, strategic competition, endogenous default, regime switching, and a training-versus-inference allocation choice. The paper is ambitious and timely. The central idea is interesting: firms invest in compute capacity, choose how much to allocate to current revenue (inference) versus capability-building (training), and this allocation affects both current cash flows and the arrival rate of a high-demand “AGI” regime. The paper also proposes a “revealed beliefs” inversion to infer firms’ implied AGI timeline beliefs from observed investment and allocation choices.

The topic is important, and the paper is creative. The draft is also unusually broad for a first pass: it integrates multiple literatures and tries to deliver both theory and an applied calibration. The framing is compelling and the paper is clearly written in many places.

That said, in its current form, the paper is not ready for a top finance journal. My main concerns are (i) the theoretical derivations/proofs are not yet at the level implied by the claims, (ii) several key results are asserted with sketch proofs or numerical verification only, (iii) there are internal inconsistencies in the derivation and proof logic, and (iv) the calibration/revealed-beliefs exercise is too illustrative and under-identified for the strength of the empirical claims. I would encourage the author to continue developing this project, but it needs a substantial tightening of scope and a more rigorous theoretical core before it can be evaluated as a top-field theory contribution.

## 1) Contribution and overall assessment

The paper’s strongest contribution is conceptual: putting the training/inference allocation at the center of irreversible investment under strategic competition and default risk. That is a genuinely interesting mechanism, and the “faith-based survival” idea (training investment raises continuation value and can lower the default boundary) is novel and potentially important.

The paper also does a good job motivating why standard real-options capacity models miss something essential in this setting (the same hardware supports both current revenue and future capability competition). The high-level economic story is strong.

However, the current contribution is overstated relative to what is actually established. The paper repeatedly emphasizes “closed-form” solutions and formal propositions, but many of the key results are either:

* only partially derived,
* dependent on unproven assertions,
* established numerically rather than analytically,
* or internally inconsistent with the stated model equations.

For a Journal of Finance-style theory paper, the theoretical foundation has to be much tighter than this.

## 2) Major technical concerns (model derivation and proofs)

### A. The low-regime option value derivation appears internally inconsistent

The paper states in the low regime that the option value takes the form (F(X)=B X^{\beta_H}) and explicitly says “the option value uses (\beta_H) as the characteristic exponent” because the option value is driven by H-regime expectations (Section 2.3.3). It then uses this to derive the low-regime trigger formula by directly replacing the revenue coefficient with (A_{\text{eff}}). This is a central step in the paper.

I do not think this is justified as written. In a regime-switching stopping problem with Poisson transitions, the low-regime value typically solves a coupled ODE (or HJB) involving the L-regime differential operator and a switching term into the H-regime value. One generally obtains:

* a homogeneous solution with exponents driven by L-regime parameters (and (r+\lambda)-type terms), and
* a particular solution tied to the H-regime continuation.

The text itself hints at this by later referencing a “particular-solution coefficient (C)” in Figure 4 discussion, but the displayed low-regime option-value formula omits such a term and proceeds as if the H-regime exponent alone is sufficient. That is a red flag.

This is not a minor notation issue. It affects:

* the low-regime trigger formula,
* comparative statics with respect to (\tilde\lambda),
* the entire logic of the revealed-beliefs inversion if low-regime policies are built on the wrong option structure.

At minimum, the author needs to derive the coupled L/H stopping problem explicitly and show under what special assumptions the reduced form in Section 2.3.3 is valid.

### B. The proofs are mostly proof sketches, not proofs

The appendix proofs (especially Propositions 3–5) are not at top-journal standard.

* Proposition 3 (preemption equilibrium): existence/uniqueness is delegated to Huisman and Kort “applied to enriched payoff functions,” with conditions said to be “verified numerically.” That is not sufficient if the proposition is stated as a theorem-level claim under the new model. The enrichment here is not cosmetic; the payoff functions now include endogenous (\tilde\lambda), training allocation, and default risk. Those changes can alter monotonicity, single crossing, and regularity conditions.

* Proposition 4 (N-firm equilibrium): again mostly intuitive arguments plus numerical verification. The section itself acknowledges some statements are “numerical observations.” Those should be labeled as such, not stated as formal proposition claims.

* Proposition 5 (asymmetric investment dilemma): the proof is essentially an intuition/Taylor expansion argument plus “verified numerically” when leverage is present. That may be fine as a conjecture or calibrated result, but not as a formal proposition unless the theorem is weakened.

In short: either prove the propositions rigorously (with full assumptions and lemmas), or reframe them as numerical findings.

### C. Proposition 3 proof contains an economically and mathematically problematic statement

In the appendix proof of Proposition 3, the argument for the leader having higher training fraction includes the claim that during monopoly phase the leader “earns (X \cdot K_L^\alpha) regardless of (\phi).” That is inconsistent with the model’s low-regime revenue specification, where revenue depends on inference capacity ((1-\phi)K). In the low regime, (\phi) should matter directly for revenue. This undermines the proof intuition as written.

That is a serious issue because Proposition 3(ii) is one of the paper’s distinctive strategic predictions.

### D. Proposition 2 proof and statements need tightening

The default-boundary proposition is one of the paper’s more attractive results, but the proof is loose and contains at least one confusing/inaccurate statement.

Examples:

* In the leverage-training substitution discussion, the wording suggests both leverage and training “increase (A_{\text{eff}}),” but leverage should primarily affect the numerator (coupon/debt service burden), not (A_{\text{eff}}).
* The sign claim for (\partial A_{\text{eff}}/\partial \tilde\lambda) is asserted under broad conditions that may not be sufficient once contest shares and the L-regime inference term are included.
* Comparative statics depend on whether (\phi) and (K) are held fixed or optimized jointly (the text shifts between partial and equilibrium effects).

These can be fixed, but they need precise statements and notation.

### E. Proposition 1 proof (interior (\phi^*)) is too informal and has sign/asymptotic issues

The proof of interiority for the training fraction relies on boundary arguments that are sketched informally. The asymptotic logic near (\phi \to 0) and (\phi \to 1) is plausible under (\alpha\in(0,1)), but the proof needs explicit derivatives and limits. As written, the sign discussion is muddled and easy to misread. Since the interior allocation is central to the economics, this should be a formal lemma, not a narrative argument.

## 3) Literature review: strong breadth, but uneven weighting and some missing anchors

The literature review is broad and, in many places, well informed. The paper does a good job covering the core finance building blocks (real options, strategic investment, structural credit risk, regime-switching valuation), and the positioning relative to Huisman & Kort is sensible.

That said, the review has three problems in its current form:

1. Overstatement of novelty
   The paper repeatedly claims no existing model combines all features. That may be true in a literal sense, but top journals care more about whether the new combination yields a sharp, robust, and testable insight. The review should spend less space on “feature stacking” and more on identifying the one or two genuinely new mechanisms.

2. Missing/underweighted adjacent theory literatures
   Given the focus on endogenous technological arrival and strategic allocation to future capability, the paper should engage more directly with:

   * strategic R&D races / patent race / innovation timing models,
   * innovation tournaments and dynamic competition in technology races,
   * endogenous technology arrival in IO/macro settings,
   * possibly learning and belief heterogeneity in real options games (if the paper wants to emphasize revealed beliefs).

   The current review has related pieces, but the core “technology race with strategic capability-building” ancestry is not fully developed.

3. Heavy reliance on executive quotes and industry narratives in the academic positioning
   The motivation is effective, but some citations and claims read more like a policy essay than a top finance theory paper. The paper can keep the executive quotes, but the literature review should more cleanly separate:

   * formal theory contribution,
   * institutional motivation,
   * illustrative sector application.

## 4) Calibration and revealed-beliefs inversion: promising idea, but too weakly identified for current claims

The inversion from observed CapEx and training allocation to implied (\lambda) is a clever idea. The paper is upfront that the exercise is illustrative, and that is appropriate.

But the current draft still draws stronger inferences than the empirical setup can support.

Main concerns:

* Many parameters are not directly observable and are jointly influential (e.g., cost convexity, operating cost, discount rate, revenue elasticities, contest structure, leverage assumptions).
* “Training fraction” is not directly observed in a clean way for the firms used in calibration; any proxy is likely noisy and model-dependent.
* The mapping from firm-level CapEx to “frontier training compute” versus broader infrastructure (including cloud, power, networking, redundancy, etc.) is extremely imperfect.
* Endogeneity is severe: observed investment reflects beliefs, financing constraints, contracting frictions, strategic signaling, customer commitments, and ecosystem complementarities.

As a result, the “revealed beliefs” section is better viewed as:

* a structural thought experiment,
* a sensitivity analysis,
* or a partial-identification exercise (set-valued implied beliefs under parameter uncertainty),

rather than a point-inference method.

If the author wants this to be a serious empirical contribution, the paper needs a much more disciplined identification strategy (or a narrower claim).

## 5) Scope and positioning problem

The paper is trying to do too much at once:

* new theory model,
* closed-form results,
* duopoly preemption game,
* N-firm extension,
* endogenous default,
* calibration,
* revealed-beliefs inversion,
* policy implications.

This breadth is impressive, but it dilutes the paper and makes the weakest parts too visible. For a top-journal submission, I would strongly recommend narrowing the scope.

A more credible path would be one of:

Option A (theory-first paper)

* Focus on the core model and one or two robust propositions:

  * training/inference allocation under regime-switching demand,
  * endogenous default boundary and “faith-based survival.”
* Provide rigorous derivations and proofs.
* Keep calibration minimal and illustrative.

Option B (quantitative/modeling paper)

* Be explicit that many results are numerical.
* Recast some propositions as “numerical findings.”
* Build a transparent sensitivity/identification analysis around the inversion exercise.

Right now the draft wants theorem-level authority and calibrated relevance at the same time, but the theory is not yet airtight and the quantitative exercise is not yet disciplined enough.

## 6) Specific comments and suggestions for revision

1. Re-derive Section 2.3.3 from the correct coupled regime-switching stopping problem.
   This is the highest-priority issue. If the current low-regime trigger is only an approximation, say so clearly and test its accuracy.

2. Downgrade several propositions to numerical propositions/observations unless formal proofs are added.
   In particular Propositions 3–5.

3. Clean up notation and distinguish clearly:

   * exogenous (\lambda_0),
   * endogenous (\tilde\lambda),
   * partial vs equilibrium comparative statics,
   * fixed-((K,\phi)) vs optimized comparative statics.

4. Tighten the default-risk section:

   * define exactly what is held fixed in Proposition 2,
   * clean up the leverage-training substitution wording,
   * prove (or appropriately qualify) monotonicity conditions.

5. Revisit Proposition 3(ii) proof intuition.
   The current monopoly-phase argument appears inconsistent with the model’s own revenue function.

6. Clarify the equilibrium concept in the N-firm section.
   The text alternates between “sequential equilibrium” language and iterative fixed-point best responses. Those are not the same object. State precisely what equilibrium is being computed.

7. Rebalance the literature review.
   Less emphasis on “this paper combines X+Y+Z” and more on the single novel mechanism and where it sits relative to strategic R&D / technology race models.

8. Soften empirical claims in the revealed-beliefs section or provide a partial-identification framework.
   The current claims about inferred beliefs are interesting, but too brittle for strong interpretation.

9. Consider a shorter paper with a cleaner theorem set.
   The model is interesting enough to stand on a tighter core.

## 7) Bottom line

This is a creative, timely, and potentially important project. The economic intuition is strong, and the training/inference allocation mechanism is genuinely novel in this context. But the paper is not yet ready for a top finance journal because the mathematical derivations and proofs do not currently support the strength of the claims, and the calibration/inversion section is too illustrative for the inferences drawn.

I would encourage the author to continue with the project, but with a sharper focus and substantially stronger theory.
