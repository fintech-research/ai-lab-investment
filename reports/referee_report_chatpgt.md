# Referee Report on “Investing in Artificial General Intelligence”

### Recommendation (for a top general-interest finance journal)

**Reject (encourage substantial reworking and resubmission elsewhere first).**

The paper is ambitious, creative, and timely. It combines real options, strategic investment, regime switching, default, and an AI-specific training/inference allocation mechanism in one framework. That is a real strength. The paper also has strong instincts about what is economically distinctive in frontier AI infrastructure competition, especially the training-vs-inference trade-off and the idea of recovering implied beliefs from observed investment choices. The paper clearly states these intended contributions in the introduction and related literature sections.

That said, for a top finance journal, the paper currently falls short on three fronts:

1. **The theoretical contribution is over-claimed relative to what is rigorously established.**
2. **Several key propositions/proofs are not fully general as stated (and in places rely on baseline-specific or additional conditions).**
3. **The empirical/calibration/revealed-beliefs section is interesting but too fragile for the claims made, especially given the paper’s own sensitivity results.**

The paper could become a strong theory-plus-calibration piece (or a first step toward a stronger structural/empirical paper), but it needs a sharper objective and more discipline in theorem statements, assumptions, and identification claims.

---

## Summary of contribution (what works)

The paper’s core idea is to model AI-lab compute investment as a joint choice of:

* **when to invest**
* **how much capacity to build**
* **what fraction of capacity to allocate to training vs inference**

with regime switching from a low-demand to high-demand “AGI” regime, and with the regime arrival rate potentially endogenous to industry training investment. This is a novel and economically meaningful mechanism. The introduction presents this well, and the “faith-based survival” intuition is memorable and potentially publishable if cleanly established.

The related literature section is broad and mostly appropriate in terms of categories: real options, strategic timing/capacity, structural credit/default, and some economics of AI/scaling laws.

The paper also appropriately tempers some claims in Section 5 by calling the inversion “illustrative” and stressing sensitivity/ordinal rather than cardinal inference. That self-awareness is a plus.

---

## Main concerns

### 1) The paper tries to do too much, and the strongest parts get diluted

Right now this is simultaneously:

* a new strategic real-options theory paper,
* a structural credit/default paper,
* an AI economics paper,
* a calibration paper,
* a revealed-beliefs inversion paper,
* and a policy paper.

For JoF-level standards, that breadth is only an advantage if each piece is airtight. Here, it creates the opposite problem: the model is rich, but many results are only partially established (baseline-specific, heuristic, or numerical), while the calibration/inversion is too fragile to carry the empirical ambition.

You need to decide what the paper is.

**My view:** the strongest paper is either:

* a **theory paper** centered on the training–inference allocation under strategic investment and regime switching, with a disciplined set of propositions and clean comparative statics, or
* a **theory + calibration note** with much humbler revealed-beliefs claims.

As written, the manuscript reads like it wants top-journal breadth, but the proof architecture and identification arguments are not yet at that level.

---

### 2) Theoretical statements are stronger than the proofs support

This is the biggest issue for a theory-heavy submission.

#### 2.1 Proposition 1 is not stated at the right level of generality

Proposition 1 presents broad statements about interiority, uniqueness, and comparative statics of the optimal training fraction. But Appendix A explicitly says the proof applies in the **baseline regime where the simplified low-regime option value** (F_L(X)=C X^{\beta_H}) is valid (i.e., a parameter region in which there is no interior L-regime trigger).

That is a materially narrower claim than the proposition language suggests. If the proposition is intended to be general, the proof is incomplete. If it is baseline-specific, the proposition should be rewritten to say so.

This matters because the economics of the training decision is precisely where the paper claims novelty. A top referee will push hard on whether the result survives beyond the calibration region.

#### 2.2 There is a clear sign error in the Appendix A uniqueness argument

In the proof of Proposition 1, the uniqueness argument states (paraphrasing): because (\alpha\in(0,1)), one gets (\alpha(\alpha-1)>0), while bracketed terms are positive, which implies strict concavity. This sign is wrong: for (\alpha\in(0,1)), **(\alpha(\alpha-1)<0)**. The conclusion (strict concavity) may still be correct, but the written argument contains a mathematical sign mistake. (This is exactly the kind of thing that hurts credibility in a top-journal theory submission.) The extracted appendix text shows this explicitly.  (and the underlying proof text around the uniqueness step)

This is fixable, but it signals insufficient theorem-proof polishing.

#### 2.3 Proposition 2 (“default boundary decreasing in (\tilde\lambda)”) appears to require an additional condition that is not emphasized in the proposition statement

The proposition states that the default boundary decreases in (\tilde\lambda) because H-regime continuation value raises (A_{\text{eff},i}).

However, the proof sketch differentiates (A_{\text{eff},i}) w.r.t. (\tilde\lambda) and the sign depends on a difference term (effectively (R_H-R_L)); the derivative is not globally positive without a condition. The appendix itself appears to rely on this condition for the leverage-training substitution discussion (“when (R_H>R_L)”).

So either:

* add a maintained condition (e.g., H-regime continuation sufficiently valuable relative to L-regime revenues), or
* weaken the proposition to a conditional statement.

As currently written, the proposition overstates the proof.

#### 2.4 Proposition 3 (preemption equilibrium) relies on a heuristic extension of a known result without enough verification

The appendix says the proof follows Huisman and Kort (2015), and claims continuity/monotonicity/single-crossing hold in the “enriched” model with training allocation, endogenous (\tilde\lambda), and default risk.

But the single-crossing argument is justified using a simplified comparison (“leader value grows linearly in (X) while follower value grows as (X^{\beta_H})”), which is too loose in this enriched environment because:

* leader value includes regime-switch continuation and default considerations,
* allocation choices differ by leader/follower,
* and default boundaries can create kinks/nonlinearities.

This may still be true, but you need a real proof or a clearly labeled conjecture + numerical verification. For top-journal theory standards, “the enriched model satisfies the same conditions” is not enough unless the conditions are checked carefully and explicitly.

---

### 3) The model’s economics are interesting, but some mechanisms are partly imposed rather than derived

The paper’s central mechanism is compelling, but several choices are highly stylized:

* fixed training fraction after investment,
* fixed installed capacity (no staged expansion),
* absorbing H regime,
* Tullock contest in both regimes,
* reduced-form mapping from training compute to arrival intensity.

You do acknowledge some of these limitations, which is good.

But a top finance referee will ask: does the result hinge on these choices?

For example, the “faith-based survival” effect is striking, but it may be driven heavily by the modeling choice that training both:

1. directly improves H-regime revenues, and
2. increases the arrival rate of the favorable regime.

That double channel is economically plausible, but it also stacks the deck. You need sharper separation of what is robust to:

* exogenous (\lambda),
* alternative contest/market-share structures,
* dynamic reallocation of training/inference post-investment,
* staged capacity expansion,
* debt covenants/rollover constraints (especially if CoreWeave-style firms are a calibration target).

Without that, the paper risks being read as a rich but fragile parable.

---

### 4) The literature review is broad and competent, but not yet disciplined enough for JoF positioning

The literature review is generally appropriate and cites the expected foundations (McDonald-Siegel, Grenadier, Huisman-Kort, Leland, etc.), plus AI scaling and macro-AI references.

The problem is not coverage. The problem is positioning.

At times the review reads like a comprehensive map of adjacent literatures rather than a sharp argument for why this paper belongs in a top finance journal. The paper should distinguish more clearly between:

* **what is genuinely finance** (investment timing/capacity under uncertainty, strategic preemption, financing/default interactions),
* **what is AI-specific economics seasoning**, and
* **what is calibration context rather than contribution**.

Right now the review’s breadth may backfire by inviting specialists to ask why each omitted paper or mechanism is not included.

A stronger JoF-style framing would be:

* one core finance question,
* one core theoretical innovation,
* one disciplined set of testable/model-implied comparative statics,
* optional AI application.

---

### 5) The revealed-beliefs inversion is interesting but currently too fragile to support strong claims

Section 5 is conceptually appealing: use investment intensity and training fraction as two moments to infer an implied AGI arrival-rate belief.

The paper is right that the training fraction can break degeneracies that CapEx/Revenue alone cannot. The CoreWeave-vs-Anthropic contrast is a good illustration of the mechanism.

However, the identification is much weaker than the prose sometimes suggests:

* the inversion is conditional on many calibrated parameters and on the model structure itself,
* several “observable” inputs are in practice noisy or difficult to map cleanly (especially training fraction),
* and your own sensitivity results show extreme instability in cardinal (\hat\lambda), especially to (\sigma_H). For example, the Anthropic-like (\hat\lambda) spanning roughly ([0.003, 0.90]) under a ±25% volatility perturbation is not a minor sensitivity; it is near-total lack of cardinal identification.

You acknowledge this and emphasize ordinal rankings, which is the right instinct.  But then the inversion should be reframed more aggressively as:

* **a structural interpretation device**
* **not an estimate**
* **not a revealed probability**
* and not even a tight “implied belief” absent much stronger measurement/validation.

For a top finance journal, this section would need either:

1. a much more credible empirical measurement strategy for training allocation and firm-level model primitives, or
2. a tighter theorem/identification proposition about what is and is not identified under observable sufficient statistics.

---

## Comments on derivations and proofs (specific technical points)

These are the issues I would expect an editor/referee to flag.

### A. Proposition 1 proof should be revised for correctness and scope

* **Scope mismatch**: Appendix A states the proof is for the baseline parameter region where the simplified (F_L) solution applies; proposition language sounds broader.
* **Sign error** in concavity/uniqueness argument ((\alpha(\alpha-1)>0) should be (<0)); conclusion may remain valid but the written proof is incorrect as stated.
* Comparative statics rely on an implicit function argument over (A_{\text{eff}}), but if (\tilde\lambda) itself depends on training choices (through Equation 2 in the duopoly/endogenous-arrival setting), then you need to be explicit about whether the proposition is proved under:

  * exogenous (\tilde\lambda),
  * partial equilibrium in (\tilde\lambda),
  * or fixed-point equilibrium.

### B. Proposition 2 likely needs conditional wording

* The sign of (\partial A_{\text{eff}}/\partial \tilde\lambda) is not obviously always positive; the appendix derivation itself suggests dependence on relative magnitudes of L- and H-regime payoffs.
* The leverage-training substitution statement in part (iii) is economically interesting, but it seems to rely on the same condition (H continuation sufficiently valuable). This should be stated cleanly.

### C. Proposition 3 proof is too heuristic for a central equilibrium claim

* If preemption equilibrium existence/uniqueness is a main result, the extension from Huisman-Kort should be formalized.
* At minimum, provide:

  * exact conditions,
  * a lemma showing monotonicity and single crossing in the enriched model,
  * and numerical verification across the parameter region used in calibration (not just baseline).

### D. Baseline-specific simplifications should be surfaced earlier

The statement that the L-regime option can reduce to a particular solution because no interior L-trigger exists under baseline parameters is important for understanding what is analytical vs numerical in the paper. This currently appears as a technical discussion after the derivation.

Bring this up more explicitly in the roadmap and theorem statements.

---

## What would make this paper much stronger (practical roadmap)

### Path A (best chance for top theory/finance outlet): Narrow and harden the theory

1. **Center the paper on one main theoretical contribution**
   Training–inference allocation under strategic real options with regime switching (and possibly default as an extension).
2. **Rewrite propositions with exact domains/conditions**
   No overbroad “always” statements.
3. **Turn Proposition 3 into a real theorem (or demote it)**
   If proof is not ready, label as proposition supported numerically.
4. **Separate exogenous-(\lambda) and endogenous-(\lambda) results clearly**
5. **Move revealed-beliefs calibration to a shorter section or appendix**
   Present as illustration, not inference.

### Path B (application-oriented): Keep breadth, lower claims, and target field journal

1. Emphasize the paper as a **structural framework + scenario tool**
2. Reframe Section 5 as **interpretive inversion under maintained assumptions**
3. Add extensive robustness/alternative specifications
4. Drop/soften strong wording around “revealed beliefs” and policy implications

---

## Minor comments (but worth fixing)

1. **Claim discipline / wording**
   Phrases like “delivering analytical investment triggers and capacity in a duopoly” read stronger than what is actually closed-form vs semi-analytical/numerical in the text. Tighten this.

2. **Literature positioning**
   The related literature is long and competent, but you should shorten and sharpen the “closest paper” comparisons. The current version invites debates over completeness rather than persuading the reader of contribution.

3. **Notation clarity**
   The use of (\lambda), (\tilde\lambda), and different parameterizations across sections/propositions should be standardized more aggressively. This is especially important once (\tilde\lambda) becomes endogenous to strategic choices.

4. **Empirical observability of training fraction**
   Section 5 treats training fraction as observable or calibratable; in practice this is noisy, inferred, and potentially strategic/unobservable. You should discuss measurement error explicitly and show how inference degrades under noise.

5. **Sensitivity presentation**
   The paper is commendably honest about sensitivity, but the implication should be stronger: when (\hat\lambda) spans almost the entire parameter space under plausible perturbations, cardinal claims are not “noisy”; they are essentially non-identified in practice.

---

## Bottom line

This is a smart and original paper with a genuinely interesting mechanism. The author has good taste in the economic problem and has assembled an ambitious framework. But at the current stage, it reads more like a promising working paper than a JoF-ready submission.

The main issue is not the idea. It is the gap between:

* what is claimed,
* what is proved,
* and what is identified.

If the paper is narrowed and the theory/proofs are made precise (especially Proposition 1 scope, Proposition 2 conditions, and Proposition 3 proof), it could become a strong contribution. As it stands, I would not recommend publication at a top general-interest finance journal.
