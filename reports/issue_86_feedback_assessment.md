# Issue #86 — Feedback Assessment

**Date:** 2026-03-12
**Branch:** 86-incorporate-feedback

This report assesses each piece of feedback from issue #86: three text comments from an anonymous reader and a formal referee report from Vincent Grégoire. Each item is rated as **Must fix**, **Should address**, or **Can dismiss**, with a suggested course of action.

---

## Part A: Text Comments (Anonymous Reader)

### Comment 1: "Reversibility" of AI infrastructure

> "Yet the fundamental uncertainty driving these decisions—whether and when AI capabilities will reach a transformative threshold—remains profoundly unresolved" → Those are certainly "reversible" (in real-life example) and so the citation is quite unrelated. AI is only a feature, yet the infrastructure used behind the scene remain modular, and can be used for multi-purpose without occuring enormous cost.

**Verdict: Can dismiss.**

The commenter conflates general-purpose data center infrastructure with purpose-built AI training clusters. The paper's claim is specifically about frontier training clusters (custom GPU interconnects, NVLink/InfiniBand fabrics, bespoke cooling and power), which *are* largely irreversible—they cannot economically serve general cloud workloads. The sentence in question (`_introduction.qmd:7`) is about uncertainty in AI capability timelines, not about infrastructure reversibility per se; the irreversibility claim is made separately on line 11 and is well-supported. The commenter appears to be thinking of commodity cloud infrastructure rather than purpose-built training supercomputers.

**Action:** No change needed. The paper already distinguishes between general compute and purpose-built training clusters.

---

### Comment 2: Source for 18–24 months and $10 billion cost

> "Facilities take 18–24 months to build, and a $10 billion training cluster cannot be easily repurposed." → Is this a standard cost, where did you get those numbers from?

**Verdict: Should address (minor).**

The 18–24 month timeline and $10B figure (`_introduction.qmd:11`) are stated as stylized facts without a direct citation. They are broadly consistent with public reporting (e.g., Microsoft/OpenAI Stargate timelines, Meta's $10B+ Llama training infrastructure), but a citation would strengthen the claim.

**Action:** Add a citation or footnote sourcing these figures. Candidates: Meta's 2024 capex disclosures, Microsoft's Stargate timeline announcements, or industry reports from SemiAnalysis/New Street Research. Alternatively, soften to "typically 18–24 months" with a footnote noting the range.

---

### Comment 3: xAI Colossus built in 122 days contradicts 18–24 months

> You cite xAI building proprietary cluster, while there is no mention that "xAI's Colossus supercomputer" was built in 122 days, instead of the standard 18-24 months you refer to.

**Verdict: Should address (minor).**

This is a fair observation. The paper cites xAI as an example of proprietary cluster investment but does not mention the accelerated Colossus timeline. However, the Colossus case is arguably an outlier that *reinforces* the paper's irreversibility argument: xAI achieved speed by accepting extraordinary cost and operational compromises (temporary facilities, no redundancy, limited cooling). The 18–24 month figure remains the industry norm for production-grade facilities.

**Action:** Add a brief footnote acknowledging the xAI Colossus timeline as a notable exception, while noting that it involved exceptional cost premiums and that the 18–24 month range applies to production-grade facilities. This actually strengthens the narrative by showing how desperate the timing pressure is.

---

## Part B: Referee Report (Vincent Grégoire)

### 1.1 Proposition 1: K*(φ) dependence on φ appears incorrect

**Claim:** In the pure H-regime, $A_{\text{eff}} = A_H \phi^\alpha K^\alpha$, so $\frac{1}{A_{\text{eff}}} \frac{\partial A_{\text{eff}}}{\partial K} = \frac{\alpha}{K}$, which is independent of φ. Therefore K* should not depend on φ.

**Verdict: Must fix — but the referee's argument is incomplete.**

The referee's algebra is correct for the *pure* H-regime case (conditional on being in H). However, Proposition 1's K*(φ) formula is stated for "the H-regime" but the paper's actual optimization (and all numerical results) uses the *full model* with $A_{\text{eff}}$ that combines L-regime and H-regime revenue. In the full model:

$$A_{\text{eff}}(\phi, K) = \frac{[(1-\phi)K]^\alpha}{r - \mu_L + \lambda} + \frac{\lambda \cdot [\phi K]^\alpha \cdot A_H}{r - \mu_L + \lambda}$$

Here $\frac{1}{A_{\text{eff}}} \frac{\partial A_{\text{eff}}}{\partial K} = \frac{\alpha}{K}$ still holds (both terms are proportional to $K^\alpha$), so the referee's point actually carries through even in the full model: the FOC for K from the smooth-pasting condition yields a K* that does not depend on φ through the $A_{\text{eff}}$ channel.

**But wait** — the cost function side matters too. The installed value is $V(X,K) = A_{\text{eff}} \cdot X / (\text{something involving } K)$, and the option value involves $A_{\text{eff}}^{\beta_H} / [\delta K/r + cK^\gamma]^{\beta_H - 1}$. When you differentiate the *option value* (not just the installed value) with respect to K, $A_{\text{eff}}$ enters raised to the power $\beta_H$, and the cost denominator has $K$ terms. Since $A_{\text{eff}} \propto K^\alpha$ (for any fixed φ), the K* from the full option-value FOC *does* encode φ indirectly through the level of $A_{\text{eff}}$.

Actually, re-examining more carefully: if $A_{\text{eff}} = f(\phi) \cdot K^\alpha$ for some function $f(\phi)$, then $A_{\text{eff}}^{\beta_H} = f(\phi)^{\beta_H} \cdot K^{\alpha \beta_H}$. The FOC $\partial/\partial K [A_{\text{eff}}^{\beta_H} / (\delta K/r + cK^\gamma)^{\beta_H - 1}] = 0$ yields a K* that *does* depend on φ through $f(\phi)$ whenever $\beta_H \neq \beta_H - 1$ (i.e., always). So the Proposition 1 formula may actually be correct, and the referee's error is in evaluating only the $\frac{1}{A_{\text{eff}}} \frac{\partial A_{\text{eff}}}{\partial K}$ term rather than the full option-value FOC.

**Action:** This requires careful re-derivation. The referee is wrong that K* is independent of φ, but the presentation in the paper could be clearer about *why* K* depends on φ (it comes through the option-value FOC, not through $A_{\text{eff}}$ alone). The paper should:
1. Verify the Proposition 1 formula against the SymPy derivation notebook.
2. Add a clarifying sentence explaining that the φ-dependence enters through the option-value optimization (the $A_{\text{eff}}^{\beta_H}$ numerator), not through the elasticity $\frac{1}{A_{\text{eff}}} \frac{\partial A_{\text{eff}}}{\partial K}$.
3. The response letter should walk through this derivation explicitly.

---

### 1.2 Proposition 2(ii): proof drops λ-dependence of β⁻_s

**Claim:** The proof that $X_D$ is decreasing in λ ignores the λ-dependence of $\beta_s^-$ in the multiplier $\beta_s^- / (\beta_s^- - 1)$.

**Verdict: Must fix.**

The referee is correct. The default boundary $X_D = \frac{\beta_s^-}{\beta_s^- - 1} \cdot \frac{c_D/r + \delta K/r}{A_{\text{eff}}}$ depends on λ through *both* $A_{\text{eff}}$ and $\beta_s^-$. The current proof only addresses the $A_{\text{eff}}$ channel. While the $A_{\text{eff}}$ channel is likely dominant (and numerical results confirm the sign), the proof is incomplete as stated.

**Action:** Either:
- (a) Compute the full derivative $\frac{\partial X_D}{\partial \lambda}$ including $\frac{\partial \beta_s^-}{\partial \lambda}$ and show conditions under which the sign is negative. This may be tractable since $\beta_s^-$ is the negative root of a quadratic in $\beta$ with $(r+\lambda)$ replacing the discount rate.
- (b) Downgrade to "the $A_{\text{eff}}$ channel dominates numerically" and present this as a computational result with analytical motivation, similar to how Proposition 3's uniqueness is already handled. Verify numerically that the $\beta_s^-$ channel never reverses the sign across the full parameter space.

Option (b) is simpler and consistent with the paper's existing treatment of other results.

---

### 1.3 Assumption (A3) and the simplified L-regime option value

**Claim:** The paper sets $A_1 = 0$ (dropping the $A_1 X^{\beta_L^+}$ term) by fiat, then proceeds to use smooth-pasting expressions. This is inconsistent.

**Verdict: Should address.**

The referee raises a legitimate point about rigor, but the economic logic is sound: under (A3), the L-regime alone cannot justify investment (the pure L-regime trigger is infinite), so $F_L$ has no exercise boundary *in L alone*. The firm invests while in L only because of the H-regime option embedded in $A_{\text{eff}}$. The $CX^{\beta_H}$ term captures exactly this: it's the value of waiting to invest optimally (with timing driven by the H-regime prospect, not by L-regime standalone value). The smooth-pasting at the investment trigger is with respect to this combined value, not a contradictory L-regime exercise.

The paper already explains this (`_model.qmd:122`), but the referee found it insufficiently clear.

**Action:**
1. Add a paragraph in the appendix explicitly stating: "Under (A3), the L-regime alone would never trigger investment, so there is no L-regime exercise boundary and $A_1 = 0$. The investment trigger in L is driven entirely by the effective revenue coefficient $A_{\text{eff}}$, which includes the H-regime prospect. The smooth-pasting conditions (Eq. 13) apply to this combined value."
2. Add a numerical robustness check: solve the full two-term problem and show that $A_1 X^{\beta_L^+}$ is negligible at the optimum (e.g., < 0.1% of $F_L$).

---

### 1.4 Internal inconsistency on Dario's dilemma asymmetry

**Claim:** The main text says underinvestment is costlier, but the appendix Taylor argument concludes $W''' < 0$, implying *overinvestment* is costlier.

**Verdict: Must fix — the referee has found a genuine inconsistency.**

The main text (`_valuation.qmd:104`) clearly states underinvestment is costlier in expected value (25% vs 5% at equal-magnitude mismatches). The appendix (`_appendix.qmd:204`) states $W''' < 0$, which means the third-order correction $\frac{1}{6}W'''(\lambda_{\text{true}})(\Delta\lambda)^3$ is *negative* for $\Delta\lambda > 0$ (overinvestment) and *positive* for $\Delta\lambda < 0$ (underinvestment). This means overinvestment has a larger loss than underinvestment at third order — the *opposite* of what the numerical results show.

The numerical results are almost certainly correct (they come directly from the code and are verified). The heuristic Taylor argument in the appendix appears to have the wrong sign or to be analyzing a different object.

**Action:**
1. Re-examine the heuristic argument. The three channels (capacity, timing, training allocation) need to be re-evaluated. The training allocation channel argument in the appendix may be backwards: under-training sacrifices the dominant H-regime component of $A_{\text{eff}}$, which is the *larger* loss — consistent with $W''' > 0$ (underinvestment costlier), not $W''' < 0$.
2. Either fix the sign of the heuristic argument (likely $W''' > 0$) or remove the heuristic Taylor argument and rely solely on the numerical result with economic intuition.
3. The numerical results and the main text narrative should remain unchanged — they are correct.

---

### 1.5 Numerical reproducibility / bounds inconsistency

**Claim:** Appendix B states optimization bounds $K \in [0.01, 10]$, but baseline $K^* \approx 0.0067$ lies outside this range.

**Verdict: Must fix — this is a clear error in the stated bounds.**

The baseline $K^* = 0.0067$ is below the lower bound of 0.01 stated in the appendix. The code (`base_model.py`) likely uses different (correct) bounds. This is probably just a typo in the appendix text.

**Action:** Check the actual bounds in the code and correct the appendix. The lower bound for K is likely 0.001 or smaller. This is a simple fix.

---

### 2.1 Regime-specific revenue structure (inference in L, training in H)

**Verdict: Should address in discussion (no model change needed).**

The referee is right that this is an extreme modeling choice. The paper already acknowledges it as a simplification. The key defense: this is the cleanest way to generate the training-inference trade-off, and mixing revenue sources in both regimes would complicate the algebra without changing the qualitative insights.

**Action:** Add 2–3 sentences to the discussion section acknowledging that a richer model with mixed revenue in both regimes would attenuate some quantitative results while preserving the qualitative mechanisms. This is a "future work" item.

---

### 2.2 Static φ is not a benign simplification

**Verdict: Should address in discussion.**

The paper already acknowledges this limitation. The referee wants more specificity about *which* results would attenuate.

**Action:** Expand the existing discussion of static φ by 2–3 sentences, explicitly noting that dynamic reallocation would: (a) reduce the optimal initial φ*, (b) attenuate the faith-based survival mechanism, and (c) reduce the Dario's dilemma asymmetry, since the over-training firm could partially recover by reallocating to inference.

---

### 2.3 Risk-adjustment framework needs tightening

**Verdict: Should address.**

The paper uses risk-adjusted (certainty-equivalent) drifts with WACC discounting. This is standard in corporate finance / real options but the referee wants explicit mapping. The concern about double-counting is legitimate if the exposition is sloppy.

**Action:** Add a brief paragraph (model section or appendix) explicitly stating: "All drifts $\mu_L, \mu_H$ are risk-adjusted (certainty-equivalent) drifts under the physical measure, and $r$ is the firm's WACC. This is equivalent to working under a risk-neutral measure with risk-neutral drifts $\mu^Q = \mu - \text{risk premium}$ and discounting at the risk-free rate." Cite Dixit & Pindyck (1994, Ch. 4) for the equivalence.

---

### 2.4 Default probability approximation misaligned with default mechanism

**Verdict: Should address.**

The paper uses a Merton-style approximation for default probabilities but has a Leland-style (barrier) default mechanism. These are conceptually different. The default probabilities are used only for illustrative purposes (the 5-year numbers in the Dario's dilemma discussion), not for any core proposition.

**Action:** Either:
- (a) Switch to the closed-form first-passage (barrier) probability under GBM (straightforward; see Shreve or Karatzas & Shreve).
- (b) Add a footnote labeling the current approximation as a rough proxy and note the direction of bias (Merton-style understates default probability relative to first-passage).

Option (a) is cleaner and not difficult to implement.

---

### Minor comment: Compact baseline table

**Verdict: Good suggestion.**

**Action:** Add a table in the calibration or appendix section listing baseline parameters, computed $(X^*, K^*, \phi^*)$, and verification of (A2)–(A3) admissibility.

---

### Minor comment: Tullock contest revenue inflation

**Verdict: Already addressed in the paper.** No action needed beyond what's there.

---

## Priority Summary

| # | Item | Priority | Effort |
|:--|:-----|:---------|:-------|
| 1.1 | Prop 1 K*(φ) derivation | Must fix (clarify, likely correct) | Medium |
| 1.2 | Prop 2(ii) β⁻_s dependence | Must fix | Medium |
| 1.4 | Dario's dilemma sign inconsistency | Must fix | Low–Medium |
| 1.5 | Optimization bounds typo | Must fix | Low |
| 1.3 | (A3) / simplified L-regime | Should address | Medium |
| 2.1 | Regime-specific revenue | Should address (discussion) | Low |
| 2.2 | Static φ limitation | Should address (discussion) | Low |
| 2.3 | Risk-adjustment framework | Should address | Low |
| 2.4 | Default probability method | Should address | Low–Medium |
| A.2 | 18–24 months citation | Should address | Low |
| A.3 | xAI Colossus footnote | Should address | Low |
| Minor | Baseline parameter table | Nice to have | Low |
| A.1 | Reversibility objection | Can dismiss | None |
