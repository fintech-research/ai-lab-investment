# Referee Report (Top Finance Journal Style)

### Recommendation

**Reject (with encouragement to revise and resubmit elsewhere first, then re-aim after substantial tightening).**

This is an ambitious and interesting paper. The core idea is genuinely original: modeling AI infrastructure investment as a joint real-options / strategic preemption / structural credit problem with an endogenous training-vs-inference allocation margin. The paper also has a strong “why now” motivation and some appealing mechanisms (especially the “faith-based survival” channel through continuation value and the asymmetric cost of over- vs under-investment). The author clearly understands both the finance theory toolkit and the institutional context.

That said, in its current form the paper is not yet at a top-journal standard. The main issues are not lack of ideas, but (i) over-claiming relative to what is analytically established, (ii) several proof arguments that are suggestive rather than rigorous, (iii) a literature section that is broad but not yet sharply positioned around the exact marginal contribution, and (iv) a calibration/quantitative section that is insightful but still too stylized and too dependent on non-structural external assumptions for the paper’s strongest empirical-sounding claims.

---

## 1) Summary and contribution

The paper studies irreversible AI infrastructure investment under uncertainty, with regime switching (pre- and post-transformative AI), strategic duopoly preemption, endogenous default risk in a Leland-style framework, and a novel training/inference allocation choice. It derives analytical and semi-analytical results (Propositions 1–3) and supplements them with numerical analysis and stylized calibration to AI-firm archetypes. The paper explicitly positions itself at the intersection of real options, strategic investment, structural credit risk, and economics of AI.

The novel mechanism is indeed clear in the paper’s own positioning: the key addition is the training-inference allocation under regime-switching demand with strategic competition and default.  The paper also articulates the “faith-based survival” mechanism through the default boundary and H-regime continuation value.

I view this as a potentially publishable research agenda. But the current manuscript tries to do too much at once and occasionally blurs the line between:

* what is fully proved,
* what is semi-analytical,
* what is computationally verified,
* and what is motivated by narrative/industry facts.

To the paper’s credit, Table 2 does try to classify results by analytical status.  (and the table text itself in the manuscript does this more fully). But the prose and contribution claims still sometimes read stronger than the proof burden supports.

---

## 2) Main strengths

### (A) The mechanism is genuinely interesting and finance-relevant

The training/inference allocation as an intertemporal trade-off (cash flow today vs future competitive position) is a good modeling innovation. The connection to leverage and default risk is especially compelling.

### (B) The paper integrates literatures in a non-trivial way

The bridge from McDonald-Siegel/Pindyck/Grenadier/Huisman-Kort to Leland-type endogenous default is thoughtful and potentially important. The preemption setup is clearly described and grounded in standard references.

### (C) The paper is unusually transparent about scope and limitations

The manuscript explicitly discusses limitations (fixed training fraction, Leland applicability to VC-backed labs, reduced-form contest function, absorbing H regime, omitted geopolitical dynamics). That is a real strength and improves credibility.

---

## 3) Major concerns (substantive)

## 3.1 The paper over-claims analytical rigor for Proposition 3 (especially part (i))

The paper states Proposition 3(i) as an analytical existence/uniqueness result for the preemption trigger, with single crossing “verified numerically.”  The proof then invokes continuity, monotonicity, and a single-crossing argument, but the argument is not sufficiently rigorous for the enriched payoff environment (capacity choice, training allocation, leverage/default, regime-switching, and endogenous/semi-endogenous components).

The specific issue is that the proof uses heuristics (“approximately affine,” “convex and eventually dominates any linear function”) and then narrows the comparison to a bounded interval, but the logic does not formally establish single crossing on the relevant interval.  In particular:

* the follower value being convex is not enough,
* the leader value being “approximately affine” is not enough,
* and the enrichment of the state/payoff structure means the exact shape conditions need to be stated and proved (or the proposition should be relabeled as numerical/computational).

This is fixable, but the current proof is below top-journal standards.

### What to do

Either:

1. **Downgrade Proposition 3(i)** to a theorem under additional explicit shape assumptions + computational verification, or
2. **Provide a true theorem** with sufficient conditions ensuring single crossing in the enriched model.

Right now the paper sits uncomfortably between those two.

---

## 3.2 Proposition 3(ii) (“leader trains more than follower”) is economically plausible but not analytically established

The proposition states a semi-analytical inequality (leader training fraction exceeds follower’s) and describes it as analytically motivated + numerically verified.  That is a reasonable target, but the proof text is still mostly economic intuition rather than a formal dominance argument.

The argument relies on monopoly-phase lower marginal cost and longer expected horizon for the leader, which is intuitive. However, the proof does not pin down:

* exact objective derivatives for leader vs follower,
* the role of endogenous follower response,
* the impact of λ-tilde changing with follower entry,
* or sufficient conditions ensuring the sign of the difference in optimal φ.

In a top-journal referee report, I would call this “good conjecture with strong numerics,” not a semi-analytical proposition unless the derivation is tightened.

### What to do

* Reframe this as a **numerical regularity** unless you can derive a monotone comparative-static argument with explicit assumptions.
* Alternatively, provide a proposition of the form: “Under assumptions X, Y, Z, local leader FOC dominates follower FOC at symmetric benchmark.”

---

## 3.3 There is a scope/assumption inconsistency in the proof of Proposition 1

The proof of Proposition 1 explicitly states scope as exogenous λ̃ (ξ = 0), with extension to endogenous λ̃ deferred to a corollary.  But later in Step 6 it includes a comparative static with respect to ξ (∂φ*/∂ξ > 0), which is an endogenous-arrival parameter. This is conceptually inconsistent with the maintained assumptions as written. The proposition statement itself also mixes exogenous λ̃ and a comparative static in ξ.

This may be a drafting issue (very likely), but it matters because the proof’s scope is one of the places where the paper is trying to be careful.

### What to do

* Cleanly separate:

  * **Proposition 1 (exogenous λ̃)**: interiority and comparative statics in λ0, current revenue premium, etc.
  * **Corollary 1 (endogenous λ̃ / ξ)**: comparative static in ξ under fixed-point conditions.
* If ξ enters through λ̃ only via endogenous channel, don’t state ∂φ*/∂ξ in the exogenous proof.

---

## 3.4 The default boundary result is interesting, but the “faith-based survival” interpretation is stronger than what is proved

The default boundary equation and the comparative static in λ̃ are a highlight of the paper. The manuscript clearly lays out the condition under which higher λ̃ lowers the default boundary (Equation 21 / threshold φ).  The proof of Proposition 2 is also better than the Proposition 3 proof: the derivative of (A_{\mathrm{eff},i}) w.r.t. λ̃ is explicit and transparent. (This is one of the stronger proof sections.)

However, the paper’s language occasionally turns this into a broad empirical claim (“optimism literally keeps the firm alive longer”) that sounds stronger than the formal statement. The proof establishes a conditional comparative static for the structural default boundary in the model, not a general empirical proposition about actual solvency outcomes.

### What to do

Tone down the rhetoric slightly, especially in the abstract/introduction/conclusion, and tie the interpretation tightly to:

* the threshold condition,
* fixed capacities/allocations in the comparative static,
* and the reduced-form mapping from beliefs to λ̃.

This will make the paper more credible, not less.

---

## 3.5 The calibration section is useful but currently too stylized to support some of the strongest external claims

The paper is admirably explicit that calibration is stylized and not a structural estimation exercise. That transparency helps. But the manuscript then makes claims that sound close to structural inference (e.g., rationalizing observed extreme commitments only under genuinely optimistic beliefs), which outruns what the calibration can support.

The calibration uses a mix of chosen, inferred, and directly observed parameters, plus stylized firm archetypes and estimated training fractions. This is fine as an illustration, but the interpretation needs to stay in that lane. The paper itself acknowledges this in places, but the headline claims sometimes drift beyond it. (Your own Table 3 calibration-status framing is good; lean into it harder.)

### What to do

* Recast the quantitative section as **disciplining magnitudes and illustrating mechanisms**, not “explaining” specific firms.
* Separate “illustrative inversion” from “structural revealed-beliefs methodology” (which you correctly place as future work in the conclusion).
* Add more robustness around the most consequential judgments (training fractions, effective WACCs, leverage assumptions, and λ0 priors).

---

## 3.6 The paper mixes model domains (frontier labs vs infrastructure providers) in a way that complicates identification and interpretation

The limitations section correctly notes that the Leland framework fits public debt issuers better than VC-backed labs, and that frontier labs often have financing structures far from the Leland environment.  This is an important admission. The problem is that the main quantitative narrative still uses stylized entities spanning frontier labs and infrastructure providers, while the default mechanism is more natural for the latter.

This creates a recurring interpretation issue:

* Is the paper about **labs**?
* about **cloud/infrastructure providers**?
* or a joint ecosystem game where these are distinct agent types?

Right now it sometimes reads as all three at once.

### What to do

Pick one of these paths and commit:

1. **Infrastructure-provider paper** (cleanest finance fit; structural credit becomes central),
2. **Frontier-lab investment paper** (replace Leland default with financing-round hazard / fundraising constraint),
3. **Two-type ecosystem model** (labs + providers), which is harder but potentially strongest.

For this draft, I would strongly recommend (1) as the cleanest route.

---

## 4) Literature review assessment

The literature review is competent and broad, and it correctly identifies the core parent literatures (real options, strategic investment, structural credit, AI economics) and the closest strategic investment building blocks (Huisman & Kort, Grenadier, etc.).

That said, for a top finance journal the literature positioning needs to be sharper in three ways:

### (A) Sharpen the exact marginal contribution relative to the closest finance papers

The draft currently says the model extends strategic timing/capacity with default, training allocation, diminishing returns, and regime switching. That is plausible. But to convince a top referee, you need a tighter “delta” against the closest hybrids:

* real options + strategic competition + financing/default,
* capacity choice + leverage substitution,
* endogenous state transitions / technology uncertainty.

In other words: what is the one theorem/mechanism that the existing literature truly cannot generate?

### (B) Separate “motivation references” from “identification references”

There is a lot of AI-industry and commentary material motivating the setup. That is fine. But top-journal readers will want:

* a compact, rigorous theory literature map in the main text,
* and perhaps a separate subsection/appendix for institutional AI motivation and calibration sources.

### (C) Add a more explicit bridge to empirical corporate finance / industrial organization implications

The current paper hints at disclosure, competition policy, and credit-risk implications (interesting), but the literature review does not yet build a strong bridge to the empirical tests the model implies.

This matters because top finance outlets often ask: “What does this model let us measure or test that existing models do not?”

---

## 5) Model derivations and proofs: detailed comments

This is the part you asked for specifically. My take is: **mostly promising and often correct-looking, but uneven in rigor.**

## 5.1 Proposition 1 proof (generally the strongest proof section, with one important scope issue)

The interiority argument for φ* using Inada-type behavior and strict concavity is well done and clear. The structure is clean:

* define (A_{\mathrm{eff}}(\phi)),
* show derivative goes to +∞ at 0 and −∞ at 1,
* show strict concavity,
* conclude unique interior solution.
  This is exactly the right style and is one of the more convincing parts of the appendix.

The main issue is the scope inconsistency noted above (exogenous λ̃ proof includes ξ comparative statics).

Minor but important:

* tighten notation consistency for λ vs λ̃ throughout the proof,
* make explicit which variables are held fixed in each comparative static,
* and clearly state whether the FOC-based comparative statics are local (they appear to be).

## 5.2 Proposition 2 proof (solid core idea; interpretation should be narrowed)

The algebra behind the faith-based survival condition is clean and intuitive. The derivative of (A_{\mathrm{eff},i}) w.r.t. λ̃ is straightforward and gives a transparent sign condition (Equation 21 threshold logic), which is a strength. The iso-default-boundary leverage/training substitution is also nicely framed as a mechanical iso-locus rather than an optimality result (good discipline by the author). This distinction is explicitly made in the proof and should be preserved.

What I would still ask for:

* a bit more rigor on regularity/parameter restrictions ensuring the root and denominator terms are well-behaved in the comparative statics,
* and a compact lemma stating the dependence of (X_D) on (A_{\mathrm{eff},i}) under the admissible parameter region.

## 5.3 Proposition 3 proof (needs major tightening or relabeling)

As noted, this is the weakest proof relative to the ambition of the claim. The proof is candid that numerical verification is doing substantial work.  That is fine in principle, but then the proposition statement and text should reflect that more consistently.

Specific problems:

* “single crossing” is asserted with heuristic shape arguments rather than proved,
* follower value shape is oversimplified in the enriched model,
* leader value monotonicity/continuity with default kinks and strategic response should be formalized,
* and part (ii) is intuition plus numerics, not a proof.

My advice: don’t fight this. Reclassify parts of Proposition 3 as computational propositions and make the theorem smaller but watertight.

---

## 6) What would most improve this paper (practical roadmap)

If the goal is eventually a top finance submission, I’d suggest the following sequence.

### First priority: make the theory claims bulletproof

1. **Rewrite Proposition 3 and Appendix A**

   * separate theorem / proposition / numerical findings cleanly
   * formalize conditions for preemption trigger existence or weaken the claim
   * relabel leader-vs-follower training result if needed

2. **Fix proof scope inconsistencies in Proposition 1**

   * exogenous vs endogenous λ̃
   * ξ comparative statics placement
   * variable-fixing statements

3. **Standardize notation**

   * λ vs λ̃, (c_D) vs (d), (X_F) vs (X_F^*), etc.
   * this matters a lot in a proof-heavy paper

### Second priority: tighten the paper’s identity

4. **Choose the economic object**

   * infrastructure providers vs frontier labs vs ecosystem model
   * right now the model mechanism and calibration narratives point in multiple directions

5. **Reposition the calibration section**

   * more clearly illustrative
   * stronger robustness on key judgment calls
   * avoid language that sounds like structural identification

### Third priority: sharpen the finance contribution

6. **Rewrite the literature review around the exact incremental theorem/mechanism**

   * one paragraph on closest finance papers
   * one paragraph on what your model uniquely adds
   * one paragraph on empirical implications

7. **Add a short “testable implications / measurement” subsection**
   This would materially increase top-journal relevance:

   * training fraction and leverage interaction
   * predicted credit spread sensitivity to AI optimism proxies
   * entry timing and capacity mix under competitive threat

---

## 7) Minor comments (selected)

* The paper is unusually readable for a technical theory paper; keep that.
* Some rhetorical phrasing is strong (“literally keeps the firm alive”) and works for a working-paper audience, but should be toned down in the main theorem statements and abstract for top-journal submission. The mechanism is strong enough without rhetorical amplification.
* The “analytical status” table is excellent and should be moved earlier / emphasized more, because it helps manage expectations. (You already have it; use it to discipline the prose.)
* The limitations section is good and honest. It actually strengthens the paper. Keep it, but move some of those caveats forward so they constrain interpretation of the calibration results.
