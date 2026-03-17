# REFEREE REPORT

---

**Manuscript:** *Investing in Artificial General Intelligence*

**Submitted to:** *The Journal of Finance*

**Date:** March 2026

---

## 1. Summary and Recommendation

This paper develops a continuous-time real-options model of irreversible capacity investment by frontier AI laboratories. The model features regime-switching demand (pre- and post-AGI), a training-inference allocation decision, duopoly preemption, and endogenous default risk. The central contribution is the identification of a *training-survival channel*: because the same GPU capacity serves both current inference revenue and future training capability, the allocation decision links the firm's growth-option value to its default boundary. Three main results emerge: (i) analytical characterization of optimal capacity, training fraction, and investment triggers; (ii) a "faith-based survival" mechanism whereby training investment lowers the default boundary through the expected post-AGI continuation value; and (iii) an asymmetric "Dario's dilemma" in which conservative underinvestment is costlier in expected value than aggressive overinvestment, though overinvestment carries higher tail risk.

**Recommendation: Revise and resubmit (major revision).** The paper addresses a first-order question in the most consequential capital allocation episode of this decade, and does so with a model that is both technically competent and economically interesting. The training-inference allocation margin is genuinely novel—no existing real-options, R&D-race, or structural-credit model generates this trade-off—and the results on faith-based survival and the asymmetry of belief costs are potentially important for both the academic literature and practitioners. However, several substantive issues need to be addressed before publication. These concern (a) the economic content of key modeling assumptions, (b) the analytical versus numerical status of central results, (c) calibration credibility, and (d) the scope of the contribution relative to the paper's length. I organize my comments into major issues that must be resolved and minor suggestions.


## 2. Major Issues

### 2.1 The Static Training Fraction: Not Just a Limitation but a Structural Problem

The author acknowledges (Section 5.4) that the assumption of a fixed training fraction ϕ chosen at investment time is the most-flagged limitation, and provides a useful two-period heuristic for the direction of bias (static ϕ* is biased upward). I want to push harder on this. The static-ϕ assumption is not merely a simplification—it is in tension with the economic environment the paper seeks to model. Frontier AI labs reallocate GPUs between training and inference on timescales of weeks, sometimes days. The paper's entire economic mechanism—that ϕ simultaneously determines current revenue, future competitive position, and default risk—is operative only to the extent that ϕ is meaningfully constrained. If firms can costlessly reallocate, the training-survival channel disappears: a struggling firm shifts to inference, a thriving firm shifts to training, and the knife-edge dynamics that make the model interesting evaporate.

I recognize that dynamic ϕ is technically demanding (it would require treating ϕ as a continuous control in the HJB equation), but the paper needs to do more than acknowledge the issue and sign the bias. Two concrete requests:

> (a) The paper should provide a quantitative bound on the bias. The two-period heuristic in Section 5.4 is qualitative. Can the author solve a simple two-period discrete version and show the magnitude of the bias? If the static ϕ* is, say, 0.70 while the dynamic optimum implies an initial ϕ of 0.45, that materially changes the calibration and the implied-λ inversions in Section 4.

> (b) Reallocation costs. A natural middle ground is to introduce a convex adjustment cost for changing ϕ, which would preserve the static model as a special case (infinite adjustment cost) and the frictionless benchmark as the other extreme. Even a rough calibration of adjustment costs would discipline how much of the training-survival channel survives.

### 2.2 Extreme Regime-Specific Revenue Structure

The regime-specific revenue structure—pure inference revenue in L, pure training revenue in H—is deliberately extreme, as the author acknowledges. But it drives the quantitative magnitudes of every result in the paper. In reality, post-AGI demand for inference is likely to be enormous (as the author concedes), and pre-AGI training quality already matters for revenue (better models attract more users). The current specification overstates the training-inference trade-off by construction. Consider: at the baseline calibration, ϕ* ≈ 0.70 (70% of capacity to training). This is already above the highest observed training fraction in Table 1 (ϕ̂ = 0.75 for the xAI-like archetype, which is an outlier). If inference mattered in H and training mattered in L, the optimal ϕ* would be interior for different reasons and likely lower.

I suggest the author develop a "mixed" specification where revenue in regime s depends on both inference and training capacity, with regime-dependent weights—for example, π_i^s(X) = X · [w_s · ((1−ϕ_i)K_i)^α + (1−w_s) · (ϕ_i K_i)^α] with w_L > w_H. This nests the current model (w_L = 1, w_H = 0) and allows the author to assess sensitivity of the headline results to the degree of regime specificity. If faith-based survival and Dario's dilemma survive at, say, w_L = 0.8 and w_H = 0.2, the contribution is substantially more robust.

### 2.3 Analytical vs. Numerical Status of Results

For a paper submitted to a top theory-oriented finance journal, the analytical status of the main results is a concern. The author is commendably transparent about this (Table 4), but the reality is:

> Proposition 1 (single firm) is fully analytical—clean and well-proved. This is a genuine strength.

> Proposition 2 (faith-based survival) is analytical in the comparative statics but relies on the unconditional A_eff approximation rather than state-dependent default boundaries. The author notes this is "conservative" but the direction is unclear: it overstates L-regime continuation value, which means the true L-regime default boundary may be higher. This weakens the faith-based survival result—the very mechanism the paper is built around.

> Proposition 3 (preemption equilibrium) is the least analytical of the three. Uniqueness is computational. The leader training advantage ϕ*_L ≥ ϕ*_F is a "computational regularity." Parts (iii)–(v) are "numerical findings." For what is presented as a theoretical contribution to the Journal of Finance, this is a gap.

There are two paths forward. First, the author could attempt to prove uniqueness of X_P analytically by establishing sufficient conditions for single crossing (e.g., restrictions on the curvature of L(X) that ensure it crosses the convex F(X) exactly once). The analytical motivation in the proof is nearly there—the default kink and regime-switching terms are what complicate things—and a targeted sufficient condition (e.g., a restriction on λ or ℓ relative to σ) might suffice. Second, if this proves intractable, the paper should more explicitly frame the duopoly analysis as a "semi-analytical" contribution and shift emphasis toward Propositions 1–2, which are fully proved.

### 2.4 Calibration: Confidence Intervals and Robustness to Joint Perturbation

The calibration is stylized by design, and the author is forthright about this. Nevertheless, several choices are weakly disciplined and bear directly on the headline results.

**Revenue elasticity α = 0.40.** This parameter drives both the degree of diminishing returns and the sensitivity of the Tullock contest. The stated justification—"GPU utilization rates, diminishing marginal compute value"—is vague. A more rigorous approach would calibrate α directly from the scaling laws literature (Kaplan et al. 2020, Hoffmann et al. 2022), where the exponent on compute in the loss-function power law is approximately 0.05–0.08. The mapping from loss-function exponents to revenue elasticity is nontrivial and model-dependent, but the paper should at least discuss the connection and bound α accordingly. Given that α has the second-highest elasticity for the trigger (ε = +19.7) and capacity (ε = +24.2), this matters quantitatively.

**Demand drifts μ_L = 0.01, μ_H = 0.06.** The low-regime drift of 1% is described as "baseline growth in cloud computing revenue," but cloud computing revenue has been growing at 20–40% annually (the paper's own data shows Google Cloud at +37–39%). Even risk-adjusted, a 1% drift is very low. The gap μ_H − μ_L = 0.05 is what drives the magnitude of the regime-switch value; a wider gap amplifies faith-based survival and Dario's dilemma. The author should explore sensitivity to the drift gap explicitly, not just through one-at-a-time elasticities.

**Joint perturbation.** Table 7 reports one-at-a-time elasticities, which miss interaction effects. Given the high elasticities to r and α, a joint perturbation (e.g., α = 0.30, r = 0.15, μ_H = 0.04) could substantially change the quantitative magnitudes. I would like to see a table showing the headline results (X*, K*, ϕ*, Dario's dilemma asymmetry) under at least four or five jointly varied parameter configurations spanning the plausible range.

### 2.5 Leland Framework Fit to AI Labs

The author acknowledges that the Leland (1994) structural default framework fits public-debt issuers better than VC-backed labs, and notes the trend toward debt financing (OpenAI's revolving credit facility, xAI's secured notes). This is fair. But the model's quantitative predictions on credit spreads (Figure 9) and default probabilities are presented with a degree of precision that the underlying framework does not warrant for the two most interesting archetypes (Anthropic-like and xAI-like), both of which are privately held with complex capital structures involving SAFEs, convertible instruments, and multi-class equity. The paper states that the qualitative predictions "apply across financing structures," but the faith-based survival threshold ϕ̲ = 0.18 (Equation 19) is a quantitative object derived from the Leland machinery. Would the threshold be similar under a VC-distress model where the binding constraint is a failed funding round rather than a missed coupon?

I suggest the author either (a) develop a brief alternative distress model (even a simple cash-burn model where the firm defaults when cumulative operating losses exhaust a finite cash reserve) and verify that the faith-based survival mechanism and ϕ̲ survive, or (b) restrict the credit-risk analysis (Section 4.2) to the archetypes for which the Leland framework is more appropriate (Google-like hyperscaler, and arguably OpenAI-like as it matures) and clearly caveat the application to VC-backed labs.

### 2.6 Dario's Dilemma: Partial Equilibrium Concern

Numerical Finding 2 (Dario's dilemma) is presented in a single-firm setting: one firm mismatches its beliefs and suffers a value loss. The paper acknowledges (Section 4.3.3) that a duopoly extension would amplify the underinvestment cost through the strategic channel. But the single-firm formulation misses a crucial force on the overinvestment side as well: if both firms over-invest because both hold aggressive beliefs, they enter earlier, build larger, and over-allocate to training—squeezing each other's contest shares and amplifying default risk. The "cost of being bold" in duopoly may be substantially higher than in the single-firm benchmark because both firms are bold simultaneously.

This is not a future extension—it is central to the paper's narrative. The paper motivates itself as a model of AI lab competition, yet the marquee result (Dario's dilemma) is proved in a non-competitive setting. I urge the author to compute the duopoly version of Figure 10, even if the results are numerical. Specifically: what is the value loss when both firms simultaneously hold beliefs λ_invest ≠ λ_true? Does the asymmetry survive? If overinvestment costs are amplified in duopoly (as I suspect), the paper's policy implications change: the observed investment behavior may be less "rational" than the single-firm analysis suggests.


## 3. Contribution and Literature Review

The literature review is thorough and well-organized. The four-pillar structure (real options, strategic investment, structural credit, AI economics) is appropriate, and the marginal contribution statement is clear. I have several comments on positioning and completeness.

**Marginal contribution.** The claimed contribution—the training-inference allocation under regime-specific competition with endogenous default—is compelling and, to my knowledge, genuinely new. No existing model generates the faith-based survival condition or the specific form of the Dario's dilemma asymmetry. The paper is right that the interaction of all three building blocks (regime-specific allocation, strategic competition, endogenous default) is what produces the new results. The concern is quantitative robustness: the mechanisms are established analytically, but their magnitudes depend on calibration choices that are hard to discipline. The paper should make this distinction more explicit—frame the contribution as the identification of qualitative mechanisms, with the calibration serving as illustration, not as a test.

**Missing literature connections.** Several relevant strands are underrepresented:

> (i) The technology adoption and general-purpose technology (GPT) literature beyond Jovanovic and Rousseau (2005): Bresnahan and Trajtenberg (1995) on GPTs, Helpman and Trajtenberg (1998) on GPT adoption cycles, and Goldfarb, Taska, and Teodoridis (2023) on AI adoption specifically. These papers study adoption timing under uncertainty about transformative technologies—closely related to the regime-switching framework here.

> (ii) The literature on investment under disagreement: Scheinkman and Xiong (2003) on speculative bubbles driven by belief heterogeneity, and Harrison and Kreps (1978) on speculative dynamics. Given that the paper emphasizes heterogeneous λ beliefs as the key driver of cross-sectional variation, connecting to the disagreement-and-overvaluation literature would strengthen the finance positioning.

> (iii) Agrawal, Gans, and Goldfarb (2019) on the economics of AI, which is now a standard reference for economists engaging with AI. Their framework for AI as a prediction technology is relevant to the inference-revenue specification.

> (iv) The network effects and platform competition literature (Rochet and Tirole, 2003; Parker and Van Alstyne, 2005) is relevant because AI models exhibit strong indirect network effects—more users generate more data, which improves models, which attracts more users. The Tullock contest abstracts entirely from this dynamic.


## 4. Detailed Assessment of Model and Proofs

### 4.1 Proposition 1 (Single-Firm Benchmark)

The proof is clean and correct. The separability result—that K* is independent of ϕ because A_eff factors as g(ϕ) · K^α—is elegant and economically intuitive: the scale of capacity is determined by cost-technology parameters, while the allocation between training and inference is determined by the regime-value weights. The Inada conditions for interiority of ϕ* are properly established (Step 5), and the uniqueness argument via strict concavity of A_eff in ϕ is correct (the second derivative is negative because α(α − 1) < 0 for α ∈ (0,1)). The comparative statics follow cleanly from implicit differentiation.

One minor technical note: the independence of ϕ* from μ_L (because w_H/w_L = λ/(r − μ_H) does not depend on μ_L) is a nice observation that deserves more emphasis. It means that the optimal training allocation depends only on the post-AGI growth premium and the arrival rate, not on current market conditions—a sharp and testable prediction.

### 4.2 Proposition 2 (Faith-Based Survival)

Parts (i) and (iv) are mechanical and straightforward. Part (ii) is the key result. The derivation of the faith-based survival condition (Equation 21) is correct. The closed-form threshold ϕ̲ in the symmetric case is correctly derived. However, I have two concerns:

> (a) The full derivative ∂X_D/∂λ decomposes into the β-channel (positive) and the A_eff-channel (negative). The paper claims the A_eff-channel dominates "whenever μ_H − μ_L is sufficiently large." This is verified numerically but not bounded analytically. A sufficient condition in terms of primitives (e.g., μ_H − μ_L > f(σ, r, α) for some explicit function f) would strengthen the result. At the baseline calibration, the β-channel is 52% of the A_eff-channel in absolute magnitude—not trivially small. If the calibration changed to, say, μ_H = 0.03 (a smaller regime gap), would the sign flip?

> (b) The unconditional A_eff framework for the default boundary (rather than state-dependent boundaries X_D^L and X_D^H) is a meaningful approximation. The paper says it is "conservative" in the sense of overstating L-regime continuation value. But overstating continuation value means understating the default boundary in L—i.e., the firm looks safer than it truly is. This biases the faith-based survival result upward: it makes training investment appear more effective at lowering default risk than it actually is. The paper should be more careful about the direction of this bias and ideally provide a bound on its magnitude.

Part (iii), the leverage-training substitution along the iso-X_D locus, is a mechanical relationship and is correctly characterized as such. The empirical prediction (highly levered firms should exhibit higher training fractions) is interesting but the author rightly notes it is a joint determination, not a causal claim.

### 4.3 Proposition 3 (Preemption Equilibrium)

The existence proof via IVT is standard and correct. The boundary conditions—L(0) < F(0) and L(X*_F) > F(X*_F)—are verified. The claim that L(X*_F) > F(X*_F) because the leader earns monopoly rents is economically clear but implicitly assumes that the leader's optimal policy at X*_F dominates the follower's—this should be stated more precisely in the proof.

The computational verification of uniqueness (500-point grid, Brent's method) is reasonable for a numerical exercise but insufficient to claim robustness. With 500 points, the grid spacing is (X*_F − X_D)/500, and a second crossing in a narrow interval could be missed. I suggest increasing the grid density to 5,000 points, or better yet, proving that L(X) − F(X) has at most one zero on the relevant interval by establishing sign restrictions on its derivative at the crossing.

The training advantage regularity ϕ*_L ≥ ϕ*_F is well-motivated economically (the monopoly-phase argument is clear), but calling it a "computational regularity" rather than a conjecture understates the gap. The paper should either prove it under simplifying assumptions (e.g., show it analytically in the limiting case λ → 0 or λ → ∞, or for the case of zero leverage) or explicitly state it as a conjecture with supporting numerical evidence.

### 4.4 Numerical Finding 2 (Dario's Dilemma)

The Taylor expansion argument identifying the source of asymmetry (W‴(λ_true) ≠ 0 through the nonlinear λ ↦ ϕ*(λ) mapping and the composition of the H-regime dominance in A_eff) is heuristically correct. The decomposition into capacity, timing, and training-allocation channels is useful. I have one substantive concern: the training-allocation channel is identified as "dominant," but this dominance depends on the baseline calibration where the H-regime term accounts for approximately 70% of A_eff. Under a mixed-revenue specification (my suggestion in Section 2.2 above), the H-regime term would be smaller, potentially reducing the asymmetry. The author should verify that the qualitative asymmetry is not an artifact of the extreme regime structure.


## 5. Minor Issues and Suggestions

**1. Tullock vs. Cournot: more than a footnote.** The paper uses Tullock contests and relegates Cournot to Appendix E. The revenue-expansion property of asymmetric Tullock contests (Section 2.4.1) is non-standard: total industry revenue increases with asymmetry, which means the leader gains partly through pie expansion, not just share theft. This amplifies preemption incentives beyond what a fixed-pie setting would deliver. The paper acknowledges this but does not quantify it. I would like to see a comparison of the leader-follower value gap under Tullock versus Cournot, even in the Appendix, to assess whether the quantitative results on preemption timing are driven by the contest form.

**2. Operating cost δ = 0.03 is very low.** The paper acknowledges that this is conservative. But given that accounting depreciation implies 20–33% per year and algorithmic obsolescence (the DeepSeek example) can devalue infrastructure further, an effective δ including economic depreciation could be 0.15–0.25. Table 7 shows low elasticity (+2.2 for trigger, +2.0 for capacity), but this elasticity is evaluated at δ = 0.03. The sensitivity at δ = 0.15 could be quite different given the nonlinear interaction with the default boundary.

**3. The absorbing H-regime.** The model does not allow for "AI winters." An extension with a small probability of reverting to L (or to a third, lower regime) would test whether faith-based survival is robust to the possibility that AGI expectations are wrong. The paper mentions this in Section 5.5 but does not explore it. Even a back-of-the-envelope calculation of how faith-based survival changes with a 5% annual probability of reversal would be informative.

**4. Normalization of demand X.** The demand process is abstract: X does not have dollar units, and the triggers (X* ≈ 0.0047) are unitless. While the comparative statics are valid regardless of normalization, the calibration section would benefit from mapping X to an observable quantity (e.g., total AI-related compute demand in dollar terms) so that readers can assess whether the optimal triggers correspond to plausible market states.

**5. Figure quality.** The figures are clear and informative. Figure 10 (Dario's dilemma) is the paper's best visualization. I would suggest adding a panel to Figure 10 showing the 5-year default probability alongside the value loss, to make the two-sided nature of the dilemma visually immediate.

**6. N > 2 competition.** Footnote 3 mentions the Bouis, Huisman, and Kort (2009) N-firm extension. Given that the frontier AI market includes at least four major labs (Anthropic, OpenAI, Google DeepMind, xAI) plus Meta and Mistral, the duopoly assumption is limiting. Even without solving the N-firm game, the paper could discuss how the key mechanisms scale with N. Does faith-based survival weaken or strengthen with more competitors? Does the preemption trigger fall further with N > 2?

**7. Endogenous λ.** The paper treats λ as exogenous and homogeneous (within each firm). But if training investment collectively accelerates the regime switch (as noted in Section 5.1), then λ is endogenous—and the firms face a coordination/free-rider problem. This is a substantial extension, but the current model's welfare implications (Section 5.1) should be more cautious given the abstraction.

**8. Length.** At 68 pages including appendices, the paper is long. The proofs are thorough but could be tightened. For example, the full boundary analysis in Appendix B (verification of Assumptions A2–A3 at archetype-specific WACCs) could be condensed to a single summary table with the details in an online appendix. The calibration details (Appendix C) and sensitivity analysis (Appendix D) are useful but could also be shortened. I estimate the paper could be reduced to 50–55 pages without losing substance.

**9. Inference-time scaling.** The paper mentions (Section 3.3, footnote) that inference-time scaling (chain-of-thought, search-augmented generation) blurs the training-inference boundary. This is not just a caveat—it is a structural change in the production technology. The DeepSeek R1 and OpenAI o-series models demonstrate that inference compute can substitute for training compute in producing capability improvements. The model's clean separation of ϕ into "training" and "inference" is increasingly at odds with the technology. The discussion should engage more seriously with how inference-time compute affects the training-survival channel.

**10. Testable predictions.** Section 5.2 lists four cross-sectional predictions, but acknowledges the tiny cross-section of frontier AI labs. I would suggest the author reframe the predictions to also encompass the broader universe of AI-adjacent firms (cloud providers, GPU manufacturers, AI-enabled SaaS companies) where the training-inference trade-off manifests at a different level of the value chain. This would increase the eventual testability of the model's implications.


## 6. Summary Assessment

This paper makes a substantive theoretical contribution to the intersection of corporate finance, real options, and the economics of AI. The training-inference allocation problem is a genuine economic novelty, and the mechanisms the paper identifies—faith-based survival, the asymmetric costs of belief mismatches, the leader-follower training divergence—are both economically interesting and policy-relevant. The model is technically competent, the proofs of the fully analytical results are correct, and the calibration, while stylized, is disciplined by real data.

The main weaknesses are: (i) the static training fraction, which is in tension with the economic environment; (ii) the extreme regime-specific revenue structure, which overstates the magnitudes of the headline results; (iii) the partially numerical character of the duopoly results; and (iv) the single-firm setting of Dario's dilemma, which omits the competitive amplification of belief mismatches. Addressing these issues—particularly the first two, which require model extensions—would significantly strengthen the paper.

I recommend a major revision, with the expectation that a revised version addressing the issues above would be suitable for the Journal of Finance. The topic is timely and important, the framework is well-suited to the problem, and the core economic mechanisms are sound. The revision should focus on robustness of the quantitative results rather than further model extensions; the current scope is already ambitious.
