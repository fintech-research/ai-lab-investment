# Referee Report on “Investing in Artificial General Intelligence”

**Recommendation:** Reject in current form, with encouragement to continue developing the paper.

This is an ambitious and imaginative paper. The central idea is genuinely interesting: installed compute serves two competing purposes, current inference revenue and future training capability, so the same allocation choice affects both growth-option value and financial fragility. That is a real finance problem, not just an AI story, and the paper’s “training-survival channel” is the right place to look for novelty.

That said, I do not think the paper is currently at the standard of the *Journal of Finance*. My concern is not that the idea is weak. The concern is that the paper overstates the analytical strength of its results relative to what is actually proved, leans heavily on approximations in the part of the model that is supposed to be most novel, and uses a calibration that is too stylized to support some of the paper’s stronger economic interpretations. The paper itself partly acknowledges this: the appendix classifies several key results as computational regularities or numerical findings rather than analytical theorems.

## Summary of the paper

The paper studies irreversible capacity investment by frontier AI labs under demand uncertainty, a Poisson regime switch from a low-demand to a high-demand state, duopoly preemption, leverage, and endogenous default. Firms choose when to invest, how much capacity to install, and what share to allocate to training versus inference. The main claims are:

1. optimal training rises with optimism about the arrival of the high regime,
2. training can lower the default boundary by increasing continuation value (“faith-based survival”), and
3. mistaken pessimism is more costly in expected value than mistaken optimism, although optimism creates more tail default risk (“Dario’s dilemma”).

## Overall assessment

The paper has a publishable core idea, but it is not yet a publishable paper at the top-finance-journal level.

What works:

- The core economic trade-off is sharp and novel enough to be worth modeling.
- The single-firm problem is the strongest part of the paper.
- The paper is well written and unusually clear for a theory/calibration paper.
- The author is admirably transparent about which results are analytical and which are computational.

What does not yet work:

- The paper presents itself as more analytical than it really is.
- The default result, which is arguably the headline contribution, is built on an approximation to the true regime-switching credit problem.
- The duopoly/preemption part is only partially proved, and the strongest comparative-static claims there are numerical.
- The calibration is too loose and too media-driven to support some of the paper’s stronger substantive claims about observed AI investment behavior.
- The model is motivated by heterogeneous beliefs, but the strategic game is mostly solved in a symmetric common-belief environment; heterogeneity enters mainly through comparative statics across archetypes, not through equilibrium interaction among firms with different priors.

## Major comments

### 1. The paper overclaims theorem status

This is the biggest issue. The introduction, abstract, and conclusion give the impression that the main economic results are analytically established. That is not really true. The appendix’s own classification says that uniqueness of the preemption trigger is based on computational verification, the leader-vs-follower training ranking is a computational regularity, and the comparative statics of the preemption equilibrium are numerical. “Dario’s dilemma” is explicitly numerical.

That is not fatal by itself. Plenty of good theory papers mix analytical structure with numerical characterization. But then the paper has to be framed honestly as a semi-analytical structural model with illustrative quantitative implications, not as a theory paper that has fully characterized its equilibrium. Right now the exposition repeatedly blurs that distinction.

At a minimum, I would require the author to:

- downgrade the language in the abstract, introduction, and conclusion;
- separate clean theorems from computational regularities;
- move some of the most speculative interpretation out of the main theoretical contribution and into a discussion section.

### 2. The “faith-based survival” result rests on an approximation, not on the full regime-switching default problem

This is the second major issue. The paper’s most distinctive claim is that more training can lower the default boundary by raising the continuation value in the high regime. But the default boundary is derived using an “unconditional” effective revenue coefficient, and the paper explicitly acknowledges that a fully coupled regime-switching default model would instead have state-dependent boundaries and that the unconditional approximation likely overstates continuation value in the low regime, implying the true low-regime default boundary may be higher.

That matters a lot. It means Proposition 2 is not really a theorem about the original economic environment; it is a theorem about an approximation to that environment. For a side result that would be fine. For the flagship mechanism, it is not.

This is where I think the paper has to make a hard choice:

- either solve the true coupled regime-switching default problem; or
- explicitly reposition the result as an approximation-based mechanism and stop presenting it as a clean structural theorem.

In the current draft, the paper wants the rhetorical benefits of the stronger claim while quietly admitting the weaker one in a footnote. That will not survive a top-journal review.

### 3. The proof of the low-regime option simplification is not convincing as written

The paper claims that when the standalone low-regime investment trigger does not exist, the homogeneous coefficient in the low-regime option solution is exactly zero, and it says this is “not an approximation but an exact consequence” of the relevant assumption.

I do not think the argument is rigorous as written. “There is no standalone low-regime exercise boundary to pin down the coefficient” does not by itself imply that the coefficient vanishes. Lack of a boundary condition is not a proof that the coefficient is zero. One still needs an admissibility argument, transversality argument, or some alternative restriction that rules out the homogeneous component. Maybe such an argument exists, but it is not given here.

This matters because Proposition 1 and the clean separation result for optimal capacity are built on that simplification. I did not find an obvious algebraic contradiction in the single-firm derivation conditional on that structure, but the logical step that gets you to the simplified low-regime value function is currently too quick for publication.

### 4. The paper is motivated by heterogeneous beliefs, but the strategic model does not really deliver a heterogeneous-beliefs equilibrium

The motivating narrative is that firms disagree sharply about AGI timelines, and those belief differences drive investment behavior. That is plausible and interesting. But the actual strategic model is largely a symmetric duopoly. Heterogeneity mostly shows up later as comparative statics across calibrated archetypes, or as a mismatch between the firm’s investment belief and the true regime-switching intensity in the Dario’s dilemma exercise. That is not the same thing as solving a game between firms with genuinely different beliefs.

This gap shows up in several places:

- the paper talks about cross-sectional heterogeneity in beliefs as if it were structurally modeled;
- the calibration maps observed firm behavior into implied beliefs, but the paper itself admits that this mapping is illustrative rather than identified;
- the leader-follower asymmetry is derived mainly from market structure, not from disagreement.

For a top journal, I would want one of two things:

- either a cleaner statement that this is a common-belief model with comparative statics in beliefs, not a heterogeneous-beliefs game;
- or an actual extension in which firms hold different priors and strategic interaction occurs under disagreement.

Right now the paper repeatedly slides between those two interpretations.

### 5. The calibration is too stylized to support strong economic claims

The paper is admirably candid that the calibration is “stylized,” not structurally estimated, and that training fractions are inferred from incomplete data with substantial uncertainty.

That honesty is good. But then the paper often goes further than the calibration can bear. In particular, the conclusion that observed extreme capital commitments are “consistent with genuinely optimistic beliefs” and are “too costly for strategic posturing or agency problems alone to explain” feels too strong given the calibration inputs. The same section later admits the inference is illustrative and fragile to calibration assumptions.

The problem is not merely parameter uncertainty. It is deeper:

- several key parameters are chosen for plausibility rather than pinned down;
- the inferred training fractions are noisy;
- the model abstracts from dynamic reallocation, learning, alternative financing structures, and other margins that could materially affect the inversion from observed policy to implied beliefs;
- the archetypes are composites rather than mapped firms.

So the paper should not use the calibration to argue that observed behavior is evidence against agency, signaling, or strategic posturing. That is not identified here. The calibration can illustrate mechanisms. It cannot do that heavier interpretive work.

### 6. The static treatment of training versus inference is too strong for the paper’s ambitions

The author openly notes that the training fraction is fixed at investment time and that dynamic reallocation would create a richer optimization problem.

That is a fair simplification for a first pass. But it is also the simplification most likely to drive the main result. In the model, training is both a current sacrifice and a future capability stock, and this fixed choice is what mechanically links survival and long-run upside. In practice, firms can and do reallocate compute, change training intensity, defer training runs, or substitute inference-time scaling for pretraining. Once that margin is introduced, the severity of the “undertrain now and lose everything later” mechanism may weaken substantially.

I do not think the paper must fully solve the dynamic training-share problem to be publishable. But it does need a sharper argument for why the static-share approximation preserves the sign and magnitude of the main results, rather than merely their qualitative existence.

## Comments on the literature review

The literature review is competent and broadly appropriate. The paper clearly knows the real options, strategic investment, structural credit, and R&D race literatures, and the basic map of closest papers is right. The framing around McDonald-Siegel, Grenadier/Huisman-Kort, and Leland is sensible.

Still, I have three concerns.

First, the review is too expansive and not selective enough. For a top theory paper, I want a tighter confrontation with the 3–5 closest papers and a cleaner explanation of exactly what object is new. Right now the review sometimes reads like a catalog.

Second, the paper needs to distinguish more sharply between “closest finance mechanism” and “AI motivation.” The current introduction leans heavily on executive quotes, contemporary examples, and sector anecdotes. That is fine for motivation, but it should not crowd out the cleaner theoretical positioning.

Third, the paper should be more explicit about what is borrowed from the industrial organization and R&D race literature and what is genuinely new relative to that literature. The dual-use capacity margin is the main novelty. That should be stated even more plainly and repeatedly.

So my view is: the review is appropriate, but not yet disciplined enough for a top journal.

## Comments on derivations and proofs

My reading of the math is as follows.

The strongest part is Proposition 1. Conditional on the separability of effective revenue into a training-share component and a capacity component, and on the simplified low-regime option form, the closed-form characterization of optimal capacity, interiority of the training choice, and the comparative statics in the regime-switch intensity and high-state drift look broadly coherent. I did not spot an obvious sign error or algebraic contradiction there. But this is conditional on the step that sets the homogeneous low-regime coefficient to zero, and that step needs a more rigorous justification.

Proposition 2 is economically appealing but mathematically weaker than the draft suggests, because it is built on the unconditional effective-revenue approximation. The fixed-policy comparative statics are fine as mechanical statements, but they should not be sold as fully structural predictions of the original regime-switching credit problem.

Proposition 3 is not at theorem standard. Existence via continuity and boundary conditions is okay. Uniqueness is computational. The leader-training dominance result is computational. The comparative statics are numerical. Again, that is not disqualifying, but the paper has to stop pretending otherwise.

The Dario’s dilemma section is useful intuition, but it is not a proof. It is a numerical result with a heuristic decomposition. That is how it should be described.

So my bottom line on the model derivations is this: the paper is internally coherent enough to be worth revising, but the proof package is not yet at publishable top-journal standard.

## Minor comments

1. The paper should be much more conservative in the abstract and conclusion. “Analytical” should be replaced in several places by “semi-analytical,” “computational,” or “numerically characterized.”
2. The normalization and units need more work. The jump from the single-firm optimal-capacity scale to the duopoly scale may be explainable, but it looks jarring and undermines confidence unless explained earlier and more clearly.
3. The claim that higher operating cost raises optimal capacity is counterintuitive on first read. Even if correct under this structure, it needs a much more careful explanation.
4. The introduction is too long and too tied to current AI-sector narratives. Some of that should move to a shorter institutional background section or an appendix. The paper should age better.
5. The paper should put the “analytical status of results” table, or a reduced version of it, in the main text rather than burying it in the appendix. It is important to understanding what has and has not been shown.
6. The empirical predictions section should be scaled back. Many of the listed predictions are comparative-static implications under fixed policies or stylized calibration, not clean empirical hypotheses ready for testing.
7. The revealed-beliefs interpretation should be presented much more cautiously. The paper’s own discussion already admits fragility there; the rest of the paper should match that caution.

## Recommendation

My recommendation is rejection in current form.

That said, I do not think this is a dead end. I think there is a good paper here if the author is willing to narrow the ambition and harden the core.

The path I would recommend is:

- make the paper more honestly a theory-plus-illustrative-quantification paper;
- either solve the coupled regime-switching default problem or explicitly downgrade the “faith-based survival” result to an approximation-based mechanism;
- strengthen the logical step behind the low-regime option simplification;
- sharply separate proven results from computational regularities;
- tone down the calibration-based interpretation about actual firms’ beliefs.

If the author does those things, the paper could become a strong field-journal theory paper, and maybe more with another major modeling pass. In its current form, though, it is not ready for the *Journal of Finance*.

---

My own blunt summary: good idea, good instincts, decent structure, but too much of the paper’s punch sits on approximations, numerical regularities, and topical calibration. That is not enough yet for a top-five finance journal.
