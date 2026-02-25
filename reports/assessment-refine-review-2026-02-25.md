# Assessment of Refine.ink Review — Investing in Artificial General Intelligence

**Date**: 2026-02-25
**Review source**: `reports/feedback-investing-in-artificial-general-intelligence-2026-02-25.md`
**Assessed by**: Claude (automated)

---

## Executive Summary

The review raises four overall concerns and four detailed comments. Three detailed comments identify genuine errors in the appendix proofs (Propositions 2 and 3). The fourth is a valid technical correction. Among the overall comments, the measure/discount-rate concern and the dilemma-framing concern are substantive and warrant revision; the other two are partially valid or arise from ambiguous exposition.

**Bottom line**: No result in the paper is invalidated, but the proofs of Propositions 2(iii) and 3(i) contain errors that must be corrected. Several expositional changes are needed to preempt misreadings.

---

## Comment-by-Comment Assessment

### Overall Comment 1 — Reconciling the valuation measure

> The paper introduces $r$ as a "risk-adjusted WACC" … but the credit risk section computes spreads relative to $r_f$, and the default probability relies on a Merton-style formula that typically requires a specific measure change.

**Verdict: Valid.**

The paper uses a reduced-form "certainty equivalent" device (McDonald & Siegel 1986) where $r$ and $\mu_s$ are risk-adjusted, but never explicitly says so. The credit risk section then introduces $r_f = 0.04$ for spread computation and a Merton default probability formula whose drift parameter has an ambiguous measure interpretation. The single sentence in the discussion ("All valuation uses a reduced-form risk-adjusted framework…") is too terse to resolve the ambiguity.

**Recommendation**: Add a short paragraph at the start of the model (Section 2.1) explicitly stating the reduced-form framework, the interpretation of $r$ and $\mu_s$, and how $r_f$ relates to $r$ in the credit risk section. Expand the discussion limitation to 2–3 sentences. No model changes needed — this is purely expositional.

**Effort**: Minor.

---

### Overall Comment 2 — Revenue specification and contest dynamics

> (a) H-regime revenue depends entirely on training compute … why is post-switch value capture purely training-limited?
> (b) The Tullock contest … appears to double-count capacity.

**Verdict: Partially valid, but already addressed in the paper.**

**(a)** The pure-training H-regime is a deliberate modeling choice. The paper could add one sentence acknowledging that post-AGI monetization also requires inference, but the binding constraint is modeled as training quality. Minor addition.

**(b)** The reviewer correctly identifies that total industry revenue can exceed the symmetric benchmark under asymmetry. The paper already discusses this (`_model.qmd` lines 229–233) and shows results hold under Cournot (Appendix E). No substantive fix needed. At most, make the forward reference to Appendix E more prominent.

**Recommendation**: One sentence on (a); strengthen the Appendix E cross-reference on (b).

**Effort**: Trivial.

---

### Overall Comment 3 — Consistency of the pre-switch investment logic

> Assumption 1(A3) is labeled "no-investment-in-$L$" … but the paper immediately defines an L-regime trigger $X^*$ and analyzes pre-switch behavior.

**Verdict: Based on a misreading of (A3), but the paper's label invites the confusion.**

(A3) means that L-regime revenue *alone* would never justify investment. The firm still invests while in regime L — driven by the combined $A_{\text{eff}}$ that includes the H-regime prospect. The trigger $X^*$ in eq-trigger-phi is for the combined problem, not a pure L-regime trigger. The label "no-investment-in-$L$" is technically correct (the L-regime homogeneous term drops out) but reads as "never invest while in L," which is wrong.

**Recommendation**: Relabel (A3) to "L-regime insufficient" or "option dominance in $L$." Add a clarifying sentence after Assumption 1: "Condition (A3) ensures that L-regime revenue alone would not justify investment; the firm invests while in regime L only because the combined revenue coefficient $A_{\text{eff}}$ — which includes the H-regime prospect — makes the investment worthwhile."

**Effort**: Minor.

---

### Overall Comment 4 — Default boundary and the nature of the dilemma

> (a) The Leland boundary with unconditional continuation value in a regime-switching context is technically tricky.
> (b) The quantitative metric $\Delta V$ measures expected value loss, which flips the "bankruptcy risk" framing.

**Verdict: Valid on both sub-points.**

**(a)** The paper uses $A_{\text{eff}}$ (an unconditional expectation over the regime switch) in the Leland default boundary. A fully coupled regime-switching default model would have state-dependent boundaries. The paper's approach is a reasonable tractability device but should be acknowledged as an approximation.

**(b)** This is the most important framing issue. The introduction frames Dario's dilemma as *downside/bankruptcy risk*, but Numerical Finding 2 shows that *underinvestment* is costlier in expected value (~25% vs ~5%). The NPV metric $\Delta V$ actually supports aggressive investment. To support the downside-risk narrative, the paper needs a conditional tail-risk metric (e.g., default probability under overinvestment vs. underinvestment). The Amodei quote about bankruptcy risk is currently in tension with the quantitative finding.

**Recommendation**:
- (a) Add a footnote or remark after Proposition 2 acknowledging the unconditional approximation.
- (b) Compute conditional default probabilities under belief mismatch and present alongside $\Delta V$. Reframe: "underinvestment costs more in expectation, but overinvestment carries higher tail risk" — making the dilemma genuinely two-sided.

**Effort**: Medium (requires small code addition for conditional default probabilities).

---

### Detailed Comment 1 — Conflation of training value slope with survival condition

> $A_{\text{eff},i}(\phi_i)$ is increasing in $\phi_i$ when the faith-based survival condition holds — but the condition governs $\partial A_{\text{eff},i}/\partial \lambda$, not $\partial A_{\text{eff},i}/\partial \phi_i$.

**Verdict: Completely valid. This is a genuine error in the proof.**

The proof of Proposition 2(iii) (`_appendix.qmd` ~line 139) claims $A_{\text{eff},i}(\phi_i)$ is increasing in $\phi_i$ "when the faith-based survival condition holds (from part ii)." Part (ii) established $\partial A_{\text{eff},i}/\partial \lambda > 0$ under that condition — the derivative is with respect to $\lambda$, not $\phi_i$. These are different conditions.

Since $A_{\text{eff},i}(\phi)$ is strictly concave in $\phi$ (with $\alpha < 1$, both $(1-\phi)^\alpha$ and $\phi^\alpha$ are concave), it has an interior maximizer $\phi^*$. The leverage-training substitution holds only for $\phi_i < \phi^*$, regardless of whether the faith-based condition is satisfied.

**Recommendation**:
1. In the proof of Proposition 2(iii): replace the incorrect back-reference to part (ii). State the correct condition: $A_{\text{eff},i}$ is increasing in $\phi_i$ for $\phi_i$ below the interior maximizer of $A_{\text{eff},i}(\cdot)$.
2. Qualify the substitution: it applies locally on $(0, \phi^*)$; beyond $\phi^*$, further training *raises* the default boundary.
3. Note that the economically relevant range (baseline $\phi^* \approx 0.70$) is within the increasing region.
4. In the Proposition 2(iii) statement: add "locally, for $\phi_i$ below the interior maximizer of $A_{\text{eff},i}$."

**Effort**: Medium.

---

### Detailed Comment 2 — Logical error in boundary condition at $X_F^*$

> It would be helpful to spell out which object $L(X)$ denotes: continuation value under a fixed leader trigger $X_P$, rather than the payoff from choosing $X$ as a trigger.

**Verdict: Valid (clarity issue).**

The reviewer initially misread $L(X)$ as the payoff from investing at $X$ (which would give $L(X_F^*) = F(X_F^*)$ under symmetry), then understood it as the continuation value of an incumbent leader. The proof never states this definition explicitly.

**Recommendation**: Add one sentence at the start of the proof defining $L(X)$ as the leader's NPV given entry at some earlier trigger $X_P$, evaluated at current state $X$. Subsumed by the fix for Detailed Comment 3.

**Effort**: Minor (combined with Comment 3).

---

### Detailed Comment 3 — Contradictory definitions of Leader Value $L(X)$

> "$L(X_D) = 0$" but "$L(0) < 0$ (the leader has incurred sunk cost $I(K_L)$)" — these mix limited-liability equity value with NPV including sunk cost.

**Verdict: Completely valid. This is a genuine inconsistency in the proof.**

The two claims require different definitions of $L$:
- $L(X_D) = 0$ requires $L$ = limited-liability equity value (equity is worthless at default).
- $L(0) < 0$ requires $L$ = NPV net of sunk cost.

If $L$ is the equity value with limited liability, then $L(X) = 0$ for all $X \leq X_D$, so $L(0) = 0$ — contradicting $L(0) < 0$. If $L$ is the NPV, then $L(X_D) = -(1-\ell)I(K) < 0$ — contradicting $L(X_D) = 0$.

The IVT argument needs $L(0) < F(0) = 0$ and $L(X_F^*) > F(X_F^*)$. The correct object is the NPV: $L(X) = E_L(X) - (1-\ell)I(K_L)$. Then:
- $L(0) = 0 - (1-\ell)I(K_L) < 0$ ✓
- $L(X_D) = 0 - (1-\ell)I(K_L) < 0$ (not zero)
- The statement "$L(X_D) = 0$" must be removed or corrected.

**Recommendation**: Rewrite the proof:
1. Define $L(X)$ explicitly as the leader's NPV: $L(X) = E_L(X) - (1-\ell)I(K_L)$, where $E_L$ is the equity value with $E_L(X_D) = 0$ under limited liability.
2. State: "For $X \leq X_D$, default has occurred and $E_L = 0$, so $L(X) = -(1-\ell)I(K_L) < 0$."
3. Remove the sentence "$L(X_D) = 0$."
4. Verify the upper boundary condition $L(X_F^*) > F(X_F^*)$ still follows.

**Effort**: Medium.

---

### Detailed Comment 4 — Incorrect NPV condition

> "its NPV is zero at the trigger" is misleading — in the Dixit–Pindyck framework, NPV at the optimal trigger is strictly positive.

**Verdict: Completely valid.**

At the real-options trigger, value-matching gives $V(X_F^*) - I = F(X_F^*) > 0$: the project NPV is strictly positive and equals the option value. What is zero is the *net advantage of exercising now versus waiting*, not the NPV. The paper itself distinguishes the Marshallian "NPV = 0" rule from the option trigger in Section 2.3.2, making this an internal inconsistency.

**Recommendation**: Replace "(its NPV is zero at the trigger)" with "(the net value of exercising now versus continuing to hold the option is zero at the trigger)."

**Effort**: Trivial.

---

## Implementation Plan

| # | Fix | Files | Priority | Effort |
|---|-----|-------|----------|--------|
| 1 | Correct Prop 2(iii) proof: decouple faith-based condition from $\phi$-monotonicity | `_appendix.qmd`, `_model.qmd` | **High** | Medium |
| 2 | Fix Prop 3(i) proof: resolve $L(X)$ definition contradiction, clarify notation | `_appendix.qmd` | **High** | Medium |
| 3 | Correct NPV parenthetical in Prop 3(i) proof | `_appendix.qmd` | **High** | Trivial |
| 4 | Add tail-risk metric to Dario's dilemma | `_valuation.qmd`, `_appendix.qmd`, code | **Medium** | Medium |
| 5 | Clarify measure/discount-rate framework | `_model.qmd`, `_valuation.qmd`, `_discussion.qmd` | **Medium** | Minor |
| 6 | Relabel (A3) and add clarifying sentence | `_model.qmd` | **Medium** | Minor |
| 7 | Acknowledge default-boundary approximation | `_model.qmd` or footnote | **Low** | Minor |
| 8 | Minor additions on H-regime revenue and Appendix E reference | `_model.qmd` | **Low** | Trivial |

Fixes 1–3 correct demonstrable errors and should be done first. Fix 4 addresses the most substantive framing concern. Fixes 5–8 are expositional improvements.
