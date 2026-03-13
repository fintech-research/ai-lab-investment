# Referee Report on “AI Lab Investment under AGI Uncertainty”

## Recommendation

**Recommendation: Reject in current form for a top general-interest finance journal; encourage resubmission elsewhere after substantial revision**

## Summary

This paper studies irreversible AI infrastructure investment under uncertainty about the arrival of a transformative “AGI” regime. Firms choose when to invest, how much capacity to build, and how to split installed capacity between inference and training. The model combines real options, regime switching, duopoly preemption, and endogenous default. The headline mechanism is that training raises the continuation value associated with the post-AGI regime and can therefore lower the default boundary, a channel the author calls “faith-based survival.” The paper also develops a quantitative illustration of “Dario’s dilemma,” namely the cost of investing on the basis of beliefs about AGI timing that differ from the truth.

The paper has real strengths. The topic is timely without being purely journalistic. More importantly, the central economic tension is not artificial: capacity allocated to training improves future competitive position but weakens current cash flow, so the growth option and distress risk are linked through the same control variable. That is a clean idea, and it is the best part of the paper. The literature review is broad and mostly well organized around real options, strategic investment, R&D races, and structural credit risk. The paper also does a decent job stating its intended marginal contribution relative to the closest building blocks.

That said, I do not think the paper clears the bar for a top finance journal in its current form. My main concern is not the topic, but the analytical discipline. The paper repeatedly presents results as analytical or semi-analytical when, on close reading, several of the most important claims are either approximation-based, partial-equilibrium comparative statics, or numerical regularities. This is acceptable in a specialized theory-plus-quantitative paper if framed honestly, but here the exposition oversells what has been established.

## Main Comments

### 1. The paper’s analytical claims are too strong relative to what is actually proved

My biggest substantive concern is the treatment of the low-regime option value. The paper starts from the general solution

\[
F_L(X) = A_1 X^{\beta_L^+} + C X^{\beta_H},
\]

then argues that under condition (A3) the homogeneous term disappears, i.e. \(A_1 = 0\), because “there is no L-regime exercise boundary to pin it down.” I do not find that convincing as written. There is still an overall investment boundary in the problem once the H-regime prospect is included through \(A_{\mathrm{eff}}\). So the statement that the homogeneous term vanishes is not a theorem; it is at best an approximation whose accuracy appears to be checked numerically at the baseline. That is too loose for a paper whose contribution is supposed to rest on analytical characterization. At minimum, this needs to be reframed explicitly as an approximation result with a proposition stating the approximation domain and error bound, not as a clean closed-form solution.

### 2. There is an internal inconsistency around optimal capacity \(K^*\)

A second serious issue is internal consistency on capacity choice. Proposition 1 states that \(K^*\) is independent of \(\phi\) because \(A_{\mathrm{eff}} = g(\phi)K^\alpha\), so the \(\phi\)-dependent term drops out of the first-order condition. The same logic implies that, in the single-firm benchmark, \(K^*\) should not move with \(\lambda\) except through channels the paper would need to specify separately.

Yet the paper later reports a positive elasticity of \(K^*\) with respect to \(\lambda\), and the discussion says that higher \(\lambda\) leads to “earlier, larger, and more training-intensive investment.” Elsewhere, the appendix discussion of Dario’s dilemma says the capacity channel contributes zero asymmetry because \(K^*\) is independent of \(\phi\) and \(\lambda\), but then the leveraged case says overinvestment raises \(K^*\). These statements cannot all be true without a very careful distinction between the single-firm benchmark, duopoly equilibrium, and endogenous leverage. As written, the notation and economic claims slide across those environments without warning. A top referee will not forgive that.

### 3. The comparative statics for the default boundary are overstated

The default-boundary comparative statics have a similar problem. The proof of “faith-based survival” differentiates \(A_{\mathrm{eff}}\) with respect to \(\lambda\) while holding capacities and training fractions fixed. That is a perfectly legitimate mechanical result. But the paper often writes as if the equilibrium default boundary necessarily falls with optimism about AGI timelines. The appendix itself acknowledges an offsetting \(\beta\)-channel and decomposes the full derivative into opposing terms. So what is analytically established is weaker than what the prose implies. The paper needs to distinguish clearly between fixed-policy comparative statics and equilibrium comparative statics with endogenous \((K, \phi, \ell)\). Right now it blurs them.

### 4. The competition structure may be doing too much work

I am also not persuaded by the Tullock specification as used here. The paper openly notes that under asymmetry total industry revenue can rise because of the contest form, i.e. asymmetry can effectively create rents rather than merely redistribute them. That is not a minor technical detail; it is potentially central to the strategic results. If larger capacity asymmetry mechanically expands total revenue, then part of the incentive to preempt or overtrain may be a property of the contest function rather than a robust feature of the underlying economics.

The paper says the main findings survive under Cournot, but the robustness discussion is too thin. For a top journal, this is not enough. The alternative competition structure needs either a proper appendix derivation with analogous figures and tables or much more modest claims in the main text.

### 5. The quantitative section is useful but should not be oversold

The quantitative section is another weak point. The author is admirably candid that the calibration is stylized, that training fractions are inferred with substantial uncertainty, and that the firm archetypes are illustrative composites rather than structural estimates. The paper also admits that the CapEx concept is not comparable across archetypes because for some firms it refers to cloud commitments while for others it refers to owned infrastructure.

Those admissions are appropriate. But then the paper goes on to make stronger interpretive claims, for example that observed aggressive investment patterns are rational and are consistent with genuinely optimistic beliefs about AI timelines. I think that goes too far relative to the calibration. The exercise is useful as disciplined illustration; it is not strong enough to support revealed-belief rhetoric.

### 6. The discussion of “Dario’s dilemma” is not fully coherent

In the expected-value analysis, the paper says underinvestment is more costly than overinvestment for equal-sized belief errors. In the tail-risk analysis, overinvestment produces much higher default risk. Those two statements can coexist. But the prose in the conclusion and discussion sometimes collapses them into a broader claim that the downside of overinvestment exceeds the opportunity cost of underinvestment. That is not the same result. The paper needs to separate expected-loss asymmetry from tail-risk asymmetry very sharply. Right now the rhetoric moves back and forth depending on which result sounds more compelling.

### 7. The value decomposition is not yet conceptually tight enough

A smaller but still important issue is the value decomposition. The “capacity gap value” is defined as a rebalancing gain from moving from current installed capacity to optimal capacity, and the paper explicitly says it is not a forward-looking option value. Yet that object is then used to make asset-pricing statements about why frontier AI lab equities should behave like growth stocks. I do not think that section is conceptually tight enough for a top finance journal. Either the decomposition should be rewritten in more standard finance terms, or the section should be greatly reduced. As it stands, it feels like an intuitive graphic in search of a theorem.

## Literature Review

On the literature review: it is mostly competent and better than average for a first draft. Still, it could be sharper. The paper would benefit from spending less space cataloguing adjacent literatures and more space drawing very explicit contrasts with the closest papers. In particular, the comparison with work on timing and capacity choice, investment/default interactions, and classic R&D race models should be tighter and less encyclopedic. Right now the review is broad, but the truly incremental part of the paper is harder to isolate than it should be.

## Additional Specific Comments

### 1. Separate the environments more cleanly

The paper should be much more explicit about which claims are single-firm results, which are duopoly results, and which additionally rely on endogenous leverage. Too many statements about “the model” pool together objects from different environments. This is what produces the confusion on whether \(K^*\) does or does not respond to \(\lambda\).

### 2. Stop overselling the strategic equilibrium characterization

The paper should stop calling Proposition 3 an analytical equilibrium characterization. The existence argument is analytical in a weak sense, but uniqueness and the leader-follower training ranking are computational. I would not object to that if the paper were frank about it. I do object to the current framing, which invites the reader to think the strategic equilibrium is much more tightly pinned down than it is.

### 3. Tighten the introduction

The empirical motivation in the introduction is effective but overdone. There are too many executive quotes and recent examples relative to the amount of formal theory the paper can actually sustain. A top referee may see that as packaging rather than substance. The introduction would improve if it cut some journalistic detail and got to the model’s key wedge faster.

### 4. Move the training-share limitation earlier

The fixed training share is probably the most consequential economic simplification in the paper. The paper does acknowledge this, and it also notes that the boundary between training and inference is blurring because inference-time scaling can itself generate capability improvements. But given how central \(\phi\) is to all the results, that limitation belongs much earlier and more prominently. Otherwise the reader is left wondering whether the paper’s central control variable is already becoming obsolete as a clean conceptual distinction.

### 5. Make the testable predictions more concrete

The testable predictions section is directionally sensible, but several “predictions” are too close to restatements of the model’s own assumptions or calibration choices. It would help to translate them into cleaner empirical objects and say more honestly where real data are currently inadequate.

## Bottom Line

If I were wearing a strict *Journal of Finance* referee hat, I would recommend rejection. Not because the paper lacks merit, but because the current draft mixes a good idea with too much analytical overclaiming.

The fastest route forward is probably not to keep piling on features. It is to simplify, clean the logic, and make the theory airtight about what is actually proved and what is only shown numerically. That would leave a smaller paper, but a much stronger one.

## Summary of Required Revisions

1. Resolve the internal inconsistency around \(K^*\) and its comparative statics.
2. Either prove the low-regime solution properly or reframe it explicitly as an approximation.
3. Separate analytical results from numerical regularities throughout.
4. Provide a much stronger robustness treatment for the competition structure.
5. Tone down the inferential claims drawn from the calibration.
