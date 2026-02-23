## Referee report (as for Journal of Finance)

**Manuscript:** *Investing in Intelligence: A Real Options Framework for AI Compute Infrastructure*
**Recommendation:** Reject as-is; potentially **revise-and-resubmit** only if the paper is re-scoped and the identification + modeling gaps below are fixed.

### 1) Summary and what the paper is trying to do

The paper builds a real-options model of irreversible “compute capacity” investment with (i) a Poisson regime switch from low to high demand, (ii) oligopoly competition via a Tullock contest share, (iii) endogenous default risk à la Leland, (iv) diminishing returns/convex costs “calibrated” to AI scaling laws, and (v) an extension where compute is allocated between training and inference.

The headline empirical/structural idea is a “revealed beliefs” inversion: because most parameters are taken as observable/calibrated, the firm’s observed investment intensity (CapEx/Revenue) is mapped into an implied Poisson arrival rate (\hat\lambda) for the high-demand regime.  The paper then interprets dispersion in (\hat\lambda) across “stylized” firms (Anthropic-like, OpenAI-like, Google-like, CoreWeave-like) as dispersion in private beliefs about “transformative AI,” and introduces a “Dario dilemma” asymmetry where being too aggressive is worse than being too conservative, especially with leverage.

### 2) Contribution: what is new, and is it enough for a top finance journal?

There are two potential contributions:

1. **A theoretical synthesis** (real options + regime switching + strategic investment + structural default) applied to AI infrastructure. This is an application-driven synthesis; the paper itself emphasizes “feature count” (combining multiple ingredients).  This can be useful, but JF typically needs either (a) a clean new mechanism with general implications, or (b) a compelling empirical test/measurement contribution with credible identification.

2. **The revealed-beliefs inversion**. This is the most promising angle because it aims to extract private information from observed investment behavior (Table 2).  If this were made credible, it could be genuinely interesting to finance readers (information aggregation, valuation sensitivity, etc.).

Right now, the contribution is not yet at “top journal” standard because the inversion is not convincingly identified (see Major Concern #1), and the model is not internally tight enough (Major Concern #2). The paper reads like a sophisticated memo with nice economics intuition, not like a publishable structural/real-options paper.

### 3) Literature review: appropriate, but it dodges the closest identification threats

The literature review is broad and mostly appropriate: classic real options; strategic exercise and preemption; regime switching; structural credit risk; investment/financing interaction; and some growth/scaling-law analogies.

But the review is weakest exactly where the paper’s *core claim* lives:

* **Structural inversion / identification with limited observables.** The paper frames this as “revealed preference” (Samuelson) , but it does not engage the structural IO/asset-pricing identification logic: when a single statistic (CapEx/Revenue) is mapped to a single belief parameter (\lambda), the mapping is fragile unless you can rule out confounds (cost heterogeneity, demand level normalization, accounting differences, contracting differences, cloud vs owned compute, off-balance-sheet commitments, etc.). The paper acknowledges an “identification assumption”  but does not do the heavy lifting.

* **Empirical measurement of “compute investment.”** CapEx is not compute, and revenue is not “compute demand.” The paper uses stylized firm inputs (Table 1)  but does not wrestle with the fact that the numerator/denominator are noisy proxies with firm-specific accounting and business-model content. This undermines the inversion.

If the paper wants to be a JF-style contribution, it should either (i) turn the inversion into a careful measurement paper with defensible data construction and validation, or (ii) de-emphasize inversion and contribute a clean theory mechanism with testable implications.

---

## Major concerns

### Major Concern 1: The “revealed beliefs” inversion is not identified (as implemented)

The inversion sets (\hat\lambda) to match a ratio of option value in regime (L) to the cost of optimal (H)-regime capacity, equating it to observed CapEx/Revenue.

This is too thin for credible inference:

* **One moment, many confounds.** CapEx/Revenue reflects (at least) scale, growth stage, depreciation accounting, leasing vs owning, supply contracts, and (critically) product mix (inference-serving vs infrastructure resale vs “platform” revenue). Treating cross-firm variation as belief heterogeneity is an extremely strong maintained assumption.

* **Demand level normalization is doing hidden work.** The inversion uses (F_L(X_{\text{ref}};\lambda)) at a “reference demand level” . If (X_{\text{ref}}) is not anchored to observables in a firm-specific way, (\hat\lambda) is effectively absorbing that normalization choice. Small changes in (X_{\text{ref}}) can mechanically produce large changes in (\hat\lambda), especially given the steep mapping from (\lambda) to “5-year switch probability.”

* **The implied numbers look implausibly extreme.** Table 2 implies (\hat\lambda \approx 0.90) (expected switch ~1.1 years) for both Anthropic-like and CoreWeave-like firms.  That is not “dispersion,” it is essentially “near certainty of imminent regime change,” which is a very strong claim to hang on a single proxy ratio, particularly for a leveraged infrastructure provider whose CapEx may be largely contracted/financed in ways not captured by the model.

What would fix this:

* Replace CapEx/Revenue with **compute-specific** measures (GPU-hours under management; contracted power capacity; committed GPU purchases; data center MW; capex broken out into AI infra; etc.), and show how results move.
* Use **multiple moments** per firm (time series of CapEx, revenue, and capacity proxies), estimate (\lambda) in a panel with firm fixed effects for cost heterogeneity, or do a Bayesian inversion with explicit priors on unobserved cost parameters.
* Provide a **validation exercise**: show that the inferred (\hat\lambda) predicts something out-of-sample (subsequent expansion pace, leverage changes, contract structure, credit spreads, or event reactions to AI capability news).

Without this, the inversion reads as an illustrative calibration, not an identified estimate of beliefs.

### Major Concern 2: Key modeling choices are not internally consistent (and this matters for the “proof” claims)

Several core equations are either under-derived or economically inconsistent:

1. **Installed value with depreciation/operating cost.** The installed value is stated as
   [
   V_s(X,K)=\frac{XK^\alpha}{r-\mu_s}-\frac{\delta K}{r}.
   ]

   This mixes (i) a growing cash flow proportional to (X_t) and constant (K^\alpha), with (ii) a *level* cost flow proportional to (K). If (\delta) is meant to represent physical/tech depreciation of capacity, a more standard treatment is (K_t=Ke^{-\delta t}) (or capacity replacement), which changes the PV of revenues as well. If (\delta) is meant to be a maintenance cost rate, then the text should stop calling it depreciation and clarify the units. Right now the model is halfway between “depreciating productive capital” and “operating expense,” and later results (triggers, comparative statics) depend on this.

2. **Contest revenue double-counting capacity.** Duopoly revenue is specified as
   [
   \pi_i = X \cdot K_i^\alpha \cdot \frac{K_i^\alpha}{K_i^\alpha+K_j^\alpha}.
   ]

   This implies (\pi_i = X \cdot \frac{K_i^{2\alpha}}{K_i^\alpha+K_j^\alpha}). That may be intended, but the interpretation becomes strange: capacity affects both “industry output” and “market share” through the same exponent. If the purpose is to capture winner-take-most via the contest share, then industry output should likely be (X\cdot(\sum K^\alpha)) or (X\cdot(\sum K)^\alpha) with shares determined separately. As written, the arms race is mechanically amplified, and the paper’s “capacity choice with diminishing returns” becomes hard to interpret.

3. **Proposition 1 is not actually proven, and the stated formula looks wrong as written.** The “proof” is a placeholder sentence . Moreover the displayed expression for (K_H^*) contains a stray (K^{1-\gamma}) term inside what should be a closed-form solution , suggesting an algebraic or typesetting error. This is not cosmetic: optimal scale is central for the inversion and comparative statics.

4. **Strategic equilibrium claims exceed what is shown.** Proposition 3 leans on existence/uniqueness from Huisman & Kort (2015) , but the model has been modified (default option, debt, altered payoff structure). It is not automatic that the same theorem applies without checking conditions. The proof sketch is not sufficient for top-journal standards.

Given how much of the paper is framed as “semi-analytical characterization” and “closed form triggers,”  you need real derivations in an appendix, not narrative proofs.

### Major Concern 3: The N-firm “equilibrium” is a computational fixed point with missing strategic content

The N-firm section uses iterative refinement/fixed-point iteration and claims ordered triggers, capacity decreasing in N, etc.

But the proof of Proposition 4 explicitly admits that a formal proof is not provided for part (iii) (total capacity increasing in N).  More importantly, it is unclear whether the algorithm is solving the correct strategic game (closed-loop vs open-loop; what is observed when; do firms commit to capacity; what are the strategy spaces). If the paper wants to retain N-firm results, it needs:

* a precise game form (timing, capacity commitment, observability, financing choice timing),
* a mapping from that game to the proposed algorithm, and
* robustness checks for multiple fixed points / dependence on initialization.

Right now, it reads as “we found a plausible fixed point.”

### Major Concern 4: Calibration is too stylized for the strength of the conclusions

The paper calibrates “stylized” firm archetypes using revenue and CapEx ratios and uses an external quote-based claim about future capex.  Table 1 provides numbers but without documentation of sources/definitions for each item.

For a JF audience, you need:

* a clean data appendix (definitions, what is included in CapEx, how revenue maps to “compute demand,” treatment of leases and purchase commitments),
* sensitivity to alternative measures (OpEx for compute, “cost of revenue” for cloud inference, power capacity), and
* a clear separation between “illustrative calibration” and “structural inference.”

---

## Model/proof checks (specific technical comments)

1. **Regime-switching option in L (Equation 6):** The ODE with ((r+\lambda)) and the (\lambda F_H(X)) source term is standard for a Poisson jump to an absorbing regime.  The proposed form (F_L(X)=G_L X^{\beta_L}+C X^{\beta_H}) is plausible given (F_H(X)\propto X^{\beta_H}).
   However, because the inversion depends on monotonicity of (F_L) in (\lambda), you should prove monotonicity (or provide conditions). Right now it is asserted.

2. **Default boundary (Equation 9):** The boundary is presented as a Leland-style smooth-pasting result scaled by contest share.  The comparative statics proof is fine as a sketch.
   But: you must state clearly what asset value process is assumed for the levered firm (is it (V(X)) with GBM in (X)?), and how regime switching affects default (separate (X_D) by regime is hinted at via (\beta_s^-)).

3. **Training fraction Proposition 5:** This is correctly derived for the specified multiplicative form; the appendix proof is fine.
   But economically, the assumption that training fraction is static and independent of (X) and (K) is doing a lot. If the paper wants to connect to the real “training vs inference” debate, you likely need either (i) a dynamic state variable for model quality with depreciation/obsolescence and discrete training runs, or (ii) at least show robustness when training generates an option-like payoff rather than a contemporaneous multiplicative factor.

4. **Dario dilemma Proposition 6:** The “proof” is again mostly intuition; it does not establish a formal asymmetry result.  If this is a key named mechanism, it needs a real statement and proof (even if local, e.g., second-order expansion around (\lambda_{\text{true}})).

---

## What I would recommend as a re-scope path (if you want this to have a shot)

### Path A: Make it a credible “revealed beliefs” measurement paper

* Build a dataset of **compute commitments/capacity proxies** (MW, GPU shipments, long-term supply contracts, capex guidance specific to AI, etc.).
* Estimate (\lambda) using **multiple moments** and allow for unobserved heterogeneity in costs/technology.
* Validate using market prices (equity reactions, credit spreads) and show information content beyond public forecasts.

### Path B: Make it a clean theory paper about competition + leverage under regime-switching demand

* Strip down: drop training/inference, drop the inversion, and focus on the interaction of **preemption and endogenous default** in capacity games.
* Prove equilibrium properly and deliver sharp comparative statics (when does leverage accelerate vs delay investment?).
* Then the AI application becomes a motivating example rather than the identification pillar.

Right now the paper tries to do both, and the weakest part (inversion) is also the most central to the headline claim.

---

## Minor comments (but worth fixing)

* Clarify whether (r) and (\mu_s) are risk-neutral parameters or a reduced-form “risk-adjusted” approach; this is mentioned but should be consistent throughout.
* If you keep Table 2, emphasize it as **illustrative** unless/until identification is strengthened; the current interpretation (“expected switch in ~1 year”) is too strong given the inputs.
* The policy section is sensible but speculative; it should flow from quantified model outputs (e.g., systemic risk via joint default probabilities, not just narrative).
* For N-firm results, don’t state propositions you can’t prove; at minimum, label them as numerical regularities.
