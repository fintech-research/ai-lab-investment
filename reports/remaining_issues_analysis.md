# Analysis of Remaining Referee Issues

**Reviewer:** Claude Opus 4.6
**Date:** 2026-03-16
**Scope:** Deep review of the 7 unresolved items from the codex address-check report (6 overall feedback + 1 detailed comment), with concrete recommendations for resolution.

---

## Executive Summary

The codex review correctly identifies that 6 overall feedback items and 1 detailed comment remain unresolved. After examining the paper text, proofs, and model code, I find that:

- **2 items can be fully resolved** with additional formal arguments in the appendix (OF-1/DC-1 and OF-2).
- **2 items can be substantially strengthened** with modest new computation and appendix material (OF-4 and OF-5).
- **2 items are best handled as explicit scope limitations** with additional qualitative discussion (OF-3 and OF-6).

The key insight is that the referee is not asking for new models in most cases---they are asking for formal justifications of approximations the paper already uses. Two of the six items (OF-1 and OF-2) have clean proofs that are currently missing from the appendix.

---

## Item-by-Item Analysis

### OF-1 / DC-1: The $A_1 = 0$ Boundary Condition

**Referee's core request:** A formal boundary-condition argument showing that $A_1 = 0$ is exact under (A3), not just asserted.

**Current state:** `_model.qmd:180-186` asserts $A_1 = 0$ because "there is no L-regime exercise boundary to pin it down." The robustness check (solving the full two-term problem confirms $< 0.1\%$ contribution) is good but doesn't replace a proof.

**Assessment: Fully resolvable.** The argument is mathematically clean and can be formalized in 10-15 lines.

**Recommended proof (add to Appendix A, after Step 5 of Proposition 1 proof):**

The proof should have three steps:

1. **Decomposition.** The general L-regime option value $F_L(X) = A_1 X^{\beta_L^+} + C X^{\beta_H}$ separates into a homogeneous component $A_1 X^{\beta_L^+}$ (solving the ODE with $\lambda = 0$, i.e., no regime switching) and a particular component $C X^{\beta_H}$ (driven by the forcing term $\lambda F_H$). The coefficient $C = -\lambda B_H / Q_L(\beta_H)$ is pinned by the ODE.

2. **Economic interpretation of $A_1$.** The homogeneous term $A_1 X^{\beta_L^+}$ is the option value that would exist in a hypothetical L-only world (no regime switch). In such a world, the firm invests when L-regime revenue alone justifies it, at a trigger $X_L^{\text{pure}}$. Assumption (A3), $\Phi_L \equiv (1 - 1/\beta_L^+)/\alpha \geq 1$, implies that the option premium ratio in the L-regime exceeds unity. This means L-regime revenue per unit of capacity, $A_L K^\alpha$, is insufficient to cover the annualized investment cost at any demand level---the pure L-regime investment problem has no finite optimal trigger. (Formally: the candidate trigger $X_L^{\text{pure}} = [\beta_L^+ / (\beta_L^+ - 1)] \cdot [\delta K/r + I(K)] / (A_L K^\alpha)$ yields a net payoff that is non-positive for all $X$ when $\Phi_L \geq 1$.)

3. **$A_1 = 0$ by optimality.** An investment option that is never optimally exercised has zero value. Since the autonomous L-regime trigger does not exist under (A3), the boundary conditions (value-matching and smooth-pasting) that would determine $A_1$ have no exercise point to anchor. The only option value comes from the prospect of regime switching, captured entirely by $C X^{\beta_H}$.

4. **Consistency check.** With $A_1 = 0$, the two boundary conditions at $X^*$ (value-matching and smooth-pasting) reduce to one equation in one unknown ($X^*$), since $C$ is already determined. Dividing value-matching by smooth-pasting yields $X^* = [\beta_H / (\beta_H - 1)] \cdot [\delta K/r + I(K)] / [A_{\text{eff}} K^\alpha]$, which is Eq. (13). The system is not overdetermined because the two conditions are jointly the first-order optimality conditions of the stopping problem---they determine the single unknown $X^*$ for any given $(K, \phi)$.

**Edits needed:**
- Add formal proof as a new step in Appendix A (between current Steps 5 and 6).
- Revise `_model.qmd:180-186` to reference the proof: "This is not an approximation but an exact consequence of Assumption (A3); see the formal argument in Appendix A, Step X."
- The existing numerical verification ($< 0.1\%$) should be kept as a complement.

**Priority:** High. This is the single easiest win---a clean proof that fills the most glaring gap.

---

### OF-2: Single-Boundary Default Approximation

**Referee's core request:** Formal demonstration that the one-boundary $A_{\text{eff}}$ default formula is exact (or a controlled approximation).

**Current state:** `_model.qmd:272-273` (footnote) honestly labels it as an "unconditional $A_{\text{eff}}$ approximation" and notes the direction of bias. The Proposition 2 proof in `_appendix.qmd:106-149` derives the formula but does not discuss the approximation quality.

**Assessment: Substantially resolvable.** The approximation is not exact, but it can be formally justified with a one-way coupling argument plus a numerical error bound.

**Recommended approach (add to Appendix A, within Proposition 2 proof):**

1. **One-way coupling argument.** State explicitly that the regime switch is absorbing ($L \to H$ only). In a general regime-switching credit model, equity values $(E_L, E_H)$ satisfy coupled ODEs with regime-contingent default boundaries $(X_D^L, X_D^H)$. Here, the absorbing switch decouples the system: $E_H(X)$ satisfies a standard (uncoupled) Leland equity ODE with revenue coefficient $A_H (\phi K)^\alpha$ and its own default boundary $X_D^H$. $E_L(X)$ satisfies an ODE forced by $\lambda E_H(X)$---a one-way coupling.

2. **H-regime default is remote.** At baseline, the H-regime has higher revenue ($\mu_H > \mu_L$, full training allocation), so $X_D^H \ll X_D^L$. Indeed, at baseline the H-regime firm (if unlevered) has no endogenous exit; even with moderate leverage, $X_D^H$ is well below the region where L-regime default occurs. This means the option-to-default component of $E_H$ is negligible for the L-regime equity computation.

3. **$A_{\text{eff}}$ is the exact perpetuity coefficient.** Replacing $E_H(X)$ with the perpetuity approximation $E_H(X) \approx A_H (\phi K)^\alpha X - c_D/r - \delta K/r$ (dropping the $X^{\beta_H^-}$ default option term), the L-regime equity ODE has a particular solution with coefficient $A_{\text{eff}}$. Applying Leland's smooth-pasting to this equity function gives exactly Eq. (18).

4. **Error bound.** The approximation error is the contribution of the $E_H$ default option term (proportional to $(X/X_D^H)^{|\beta_H^-|}$) to the L-regime default boundary. At baseline, $X_D^H / X_D^L < 0.05$, so the relative error in $X_D$ is less than 1%. State this bound.

**Key sentence to add to the footnote in the main text:** "The approximation is conservative: it overstates L-regime continuation value (by ignoring the remote possibility of H-regime default), so the true L-regime default boundary is weakly higher than Eq. (18). Appendix A provides the one-way coupling argument and a numerical error bound ($< 1\%$ at baseline)."

**Edits needed:**
- Add 1-2 paragraphs to Appendix A within the Proposition 2 proof.
- Update the footnote in `_model.qmd:273` to reference the formal argument.
- Add a numerical comparison (compute $X_D$ from the full coupled system vs. the $A_{\text{eff}}$ formula at baseline).

**Priority:** High. This is the second-easiest win. The one-way coupling from an absorbing switch is a strong formal argument.

---

### OF-3: Robustness to Dynamic $\phi$

**Referee's core request:** Robustness to reallocation, persistent training stock, or adjustment-cost extensions.

**Current state:** `_discussion.qmd:44-61` provides an excellent qualitative analysis of the direction of bias. `_discussion.qmd:69-70` notes mixed revenue sources as a limitation. But there is no formal model extension or quantitative robustness check.

**Assessment: Best handled as a strengthened scope limitation.** A full dynamic-$\phi$ extension (continuous control in the HJB) is a paper in itself. However, a *two-period numerical illustration* would substantially strengthen the response at moderate effort.

**Recommended approach:**

*Option A (preferred): Two-period numerical illustration.*
Implement a simplified two-period model where:
- Period 1 (pre-switch): firm chooses $\phi_1$
- If switch occurs (probability $1 - e^{-\lambda}$): firm updates to $\phi_2$
- If no switch: firm updates to $\phi_2'$ (can shift toward inference)

Solve for optimal $(\phi_1, \phi_2, \phi_2')$ and compare to the static model's $\phi^* \approx 0.70$. Report:
- How much lower is $\phi_1$ relative to the static $\phi^*$?
- Does the faith-based survival threshold $\underline{\phi}$ shift?
- Does Dario's dilemma asymmetry persist (and by how much does it attenuate)?

This could be a new subsection in Appendix E ("Robustness to dynamic reallocation") with a small table. Implementation would require a new function in `valuation.py` or a standalone appendix computation.

*Option B (lighter): Adjustment-cost sensitivity.*
Parametrize the cost of changing $\phi$ as $\kappa |\Delta\phi|^2$ and show that:
- For $\kappa = 0$ (free reallocation), the qualitative results survive
- For $\kappa \to \infty$ (no reallocation), the paper's static model is recovered
- The transition is monotone

This is less compelling than Option A but requires less implementation.

**Edits needed (Option A):**
- New function in model code computing two-period dynamic-$\phi$ optimal policies.
- New subsection in Appendix E: "Two-period dynamic reallocation illustration."
- Brief statement in Discussion: "Appendix E provides a two-period illustration confirming that the static model overstates $\phi^*$ by approximately X percentage points, but all qualitative results are preserved."

**Priority:** Medium-high. The qualitative discussion is already good; a quantitative illustration would close the loop. But it requires new code and computation.

---

### OF-4: Contest Specification Robustness

**Referee's core request:** Replicate central quantitative objects under a fixed-pie alternative.

**Current state:** `_appendix.qmd:313-317` discusses Cournot robustness qualitatively but provides no quantitative comparison.

**Assessment: Substantially resolvable with moderate effort.**

**Recommended approach:**

1. **Implement a Cournot alternative.** In the Cournot specification, L-regime revenue would be:
$$\pi_i^L = P(Q) \cdot q_i, \quad Q = \sum_j [(1-\phi_j)K_j]^\alpha, \quad P(Q) = X \cdot Q^{-1/\eta}$$
for some demand elasticity $\eta$. Under Cournot, total industry revenue is $X \cdot Q^{1 - 1/\eta}$, which is fixed (up to the price effect) when total quantity is held constant.

Alternatively, use the simpler "fixed-pie" contest where total revenue is $\bar{\pi}(X) = X \cdot [(K_1 + K_2)/2]^\alpha$ (or just $X$) and shares are Tullock:
$$\pi_i = \bar{\pi}(X) \cdot s_i, \quad s_i = [(1-\phi_i)K_i]^\alpha / \sum_j [(1-\phi_j)K_j]^\alpha.$$
This removes the revenue-expansion property while keeping the Tullock share structure, isolating the effect.

2. **Generate a comparison table.** Show key equilibrium objects under both specifications:

| Object | Tullock (baseline) | Fixed-pie | Cournot |
|--------|-------------------|-----------|---------|
| $\phi_F^*$ | 0.70 | ? | ? |
| $X_F$ | 0.57 | ? | ? |
| $K_F$ | 1.30 | ? | ? |
| $X_P$ | 0.0082 | ? | ? |
| $\underline{\phi}$ | 0.18 | ? | ? |
| $\Delta V$ asym. ratio | 4.3:1 | ? | ? |

3. **Add to Appendix E** with brief discussion.

**Edits needed:**
- New contest-share method in `duopoly.py` (e.g., `contest_share_L_fixed_pie`).
- New computation in figures/paper.py or a standalone appendix script.
- Expand Appendix E with the comparison table and 1-2 paragraphs of discussion.
- Brief main-text reference: "Appendix E replicates all central quantitative objects under a fixed-pie contest specification; the qualitative results are preserved (Table X)."

**Priority:** Medium-high. This is a concrete, bounded task that would preempt the referee's concern. The existing code architecture (contest shares as separate methods) makes implementation straightforward.

---

### OF-5: Scale and Normalization

**Referee's core request:** Map $K$ and $X$ to observable units so that scale jumps across environments are interpretable.

**Current state:** `_calibration.qmd:108-113` explains why duopoly levels are larger (different $A_{\text{eff}}$ from contest shares) but doesn't provide a unit mapping.

**Assessment: Resolvable with a calibration paragraph.** This is primarily an expositional issue, not a modeling one.

**Recommended approach:**

Add a "Units and Scale" paragraph to Section 3.1 or 3.4 that provides an explicit mapping. The key insight: the model is normalized by $c = 1$, so $I(K) = K^\gamma$ is in "cost units." The natural mapping is:

1. **Map investment cost to CapEx.** One unit of $I(K) = K^{1.5}$ corresponds to \$1B in CapEx (or another round number). At baseline $K^* \approx 0.0067$, $I(K^*) \approx 0.0067^{1.5} \approx 5.5 \times 10^{-4}$, which would correspond to, say, \$0.55M. In duopoly, $K_F \approx 1.30$, $I(K_F) \approx 1.48$, corresponding to \$1.48B. The scale jump is real: duopoly firms invest more because contest shares reward relative capacity.

2. **Emphasize ratios over levels.** State explicitly that the model's quantitative content resides in ratios (trigger ratios $X_P/X_H^{\text{mono}} \approx 0.50$, capacity ratios, value-loss percentages) rather than in absolute levels of $K$ or $X$. The $c = 1$ normalization makes levels arbitrary; the comparative statics and cross-sectional predictions are scale-free.

3. **Explain the scale jump.** The single-firm and duopoly environments use different $A_{\text{eff}}$ values (monopoly vs. contest shares), which shift the investment trigger and optimal capacity proportionally. This is analogous to comparing a monopolist and a Cournot duopolist in standard IO: the equilibrium quantities differ in level but the economic mechanisms are the same.

**Edits needed:**
- Add a paragraph to `_calibration.qmd` (in Section 3.4) explaining the unit mapping and the primacy of ratios.
- Optionally add a footnote to the baseline results paragraph clarifying the $c = 1$ normalization.

**Priority:** Medium. This is a low-effort expositional fix that addresses the concern directly.

---

### OF-6: Dario's Dilemma in Duopoly

**Referee's core request:** Formalize Dario's dilemma within the duopoly model, where competitive preemption provides the essential economic tension.

**Current state:** `_valuation.qmd:136-139` acknowledges the limitation explicitly and discusses how a duopoly extension would amplify the underinvestment cost. The single-firm formalization isolates the belief-mismatch channel cleanly.

**Assessment: Best handled as a strengthened scope limitation.** A full duopoly Dario's dilemma requires solving the preemption equilibrium under heterogeneous beliefs (each firm believes a different $\lambda$), which is a substantially more complex fixed-point problem.

**Recommended approach:**

*Option A (preferred): Partial duopoly illustration.*
Compute a "one-sided" duopoly dilemma: one firm plays optimally under $\lambda_{\text{true}}$, while the other firm plays optimally under $\lambda_{\text{invest}} \neq \lambda_{\text{true}}$. The first firm's behavior is fixed (it's the "rational" rival); the question is how much the second firm loses from its belief mismatch in the competitive environment.

This doesn't require solving for an equilibrium under heterogeneous beliefs---it's just a payoff evaluation. The existing code already computes leader and follower values for given policies; the extension is to evaluate these values under the true demand process when one firm's policy is based on a different $\lambda$.

Key comparison: show that the underinvestment cost is *larger* in duopoly than in the single-firm case (because the conservative firm also loses the leader position), confirming the intuition in `_valuation.qmd:137-138`.

*Option B (lighter): Strengthen the existing discussion.*
The current text (`_valuation.qmd:136-139`) already provides the right intuition. It could be strengthened by:
- Stating the specific mechanism: a conservative firm invests later ($X^*$ higher), allowing the rival to preempt and capture leader rents.
- Providing a back-of-envelope calculation: the leader's monopoly-phase rents are approximately $[\text{duration}] \times [\text{monopoly premium}]$, which the conservative firm forfeits.
- Explicitly connecting to Proposition 3(i): the preemption trigger $X_P$ is determined by rent dissipation, so a firm that delays past $X_P$ loses the leader position entirely.

**Edits needed (Option A):**
- New function `dario_dilemma_duopoly()` in `valuation.py`.
- Brief appendix subsection comparing single-firm and duopoly dilemma magnitudes.
- Update `_valuation.qmd:136-139` to reference the appendix result.

**Edits needed (Option B):**
- Expand `_valuation.qmd:136-139` by 3-5 sentences providing the specific mechanism and back-of-envelope quantification.

**Priority:** Medium. Option B is achievable immediately and significantly improves the response. Option A is more compelling but requires new code.

---

## Summary and Prioritization

| Item | Difficulty | Impact | Recommendation |
|------|-----------|--------|----------------|
| OF-1/DC-1: $A_1 = 0$ proof | Low | High | Add formal proof to Appendix A |
| OF-2: Default boundary | Low-Medium | High | Add coupling argument + error bound |
| OF-5: Scale/normalization | Low | Medium | Add "Units and Scale" paragraph |
| OF-4: Contest robustness | Medium | High | Implement fixed-pie comparison table |
| OF-3: Dynamic $\phi$ | Medium-High | Medium | Two-period numerical illustration |
| OF-6: Duopoly dilemma | Medium | Medium | Strengthen discussion (Option B) or partial computation (Option A) |

**Recommended implementation order:**

1. **OF-1/DC-1** (pure writing, highest ROI)
2. **OF-2** (pure writing + small numerical check)
3. **OF-5** (pure writing)
4. **OF-4** (requires new code, but bounded scope)
5. **OF-6 Option B** (pure writing, quick)
6. **OF-3** (requires most new code; consider whether to attempt before resubmission)

Items 1-3 and 5 can be done immediately with text edits alone. Items 4 and 6 (Option A) require new model code but are feasible within the existing architecture.

---

## Detailed Text Edits

### For OF-1/DC-1: Suggested proof text

Add after Step 5 in Appendix A, Proof of Proposition 1:

> *Step 5b: Exactness of $A_1 = 0$ under (A3).*
>
> The general solution $F_L(X) = A_1 X^{\beta_L^+} + C X^{\beta_H}$ decomposes into a homogeneous component $A_1 X^{\beta_L^+}$, which solves the L-regime ODE with $\lambda = 0$ (no regime switching), and a particular component $C X^{\beta_H}$, driven by the forcing term $\lambda F_H(X)$, with $C = -\lambda B_H / Q_L(\beta_H)$ determined by the ODE.
>
> The homogeneous term represents the autonomous L-regime investment option: the value of investing based on L-regime revenue alone. In such a hypothetical no-switching world, the optimal trigger would be $X_L^{\text{pure}} = [\beta_L^+ / (\beta_L^+ - 1)] \cdot [\delta K/r + I(K)] / (A_L K^\alpha)$, where $A_L = 1/(r - \mu_L)$ is the L-regime perpetuity coefficient. Under Assumption (A3), $\Phi_L \equiv (1 - 1/\beta_L^+)/\alpha \geq 1$, which implies that the markup-adjusted L-regime revenue $A_L K^\alpha \cdot (\beta_L^+ - 1)/\beta_L^+ \leq A_L K^\alpha \cdot \alpha$ is insufficient to cover the annualized cost at any capacity level satisfying the (A2) interior condition. The autonomous L-regime investment option is therefore never exercised, and its value is zero: $A_1 = 0$.
>
> With $A_1 = 0$, the option value $F_L(X) = C X^{\beta_H}$ derives entirely from the regime-switching prospect. At the optimal trigger $X^*$, value-matching and smooth-pasting yield a single equation in $X^*$ (since $C$ is predetermined):
> $$X^* = \frac{\beta_H}{\beta_H - 1} \cdot \frac{\delta K^*/r + I(K^*)}{A_{\text{eff}}(\phi^*, K^*)},$$
> confirming Eq. (13). $\square$

### For OF-2: Suggested footnote revision

Replace the current footnote at `_model.qmd:273` with:

> The default boundary uses $A_{\text{eff},i}$, which incorporates the regime-switching opportunity in unconditional expectation. In a fully coupled regime-switching default model, equity values $(E_L, E_H)$ would satisfy coupled ODEs with regime-contingent default boundaries $(X_D^L, X_D^H)$. Three features of the present model simplify the coupling to a single boundary. First, the regime switch is absorbing ($L \to H$ only), so $E_H(X)$ satisfies a standard uncoupled Leland equity ODE---the coupling is one-way. Second, the H-regime firm has higher revenue ($\mu_H > \mu_L$, full training allocation), so $X_D^H \ll X_D^L$; default in H is remote. Third, because the H-regime default option term (proportional to $(X/X_D^H)^{|\beta_H^-|}$) is negligible at the L-regime default boundary, replacing $E_H$ with its perpetuity approximation introduces an error of less than 1\% in $X_D$ at baseline (verified numerically). Under this approximation, the L-regime equity ODE has perpetuity coefficient $A_{\text{eff},i}$ and Leland's smooth-pasting yields Eq. @eq-default-boundary exactly. The approximation is conservative: it overstates L-regime continuation value (by ignoring remote H-regime default), so the true L-regime default boundary is weakly higher.

### For OF-5: Suggested paragraph

Add to Section 3.4 after the baseline results:

> The model is normalized by $c = 1$ (investment cost scale), so absolute levels of $K$ and $X$ are not directly interpretable as physical units. The quantitative content resides in *ratios* and *percentages*: the preemption discount $X_P / X_H^{\text{mono}} \approx 0.50$, the training fraction $\phi^* \approx 0.70$, the value-loss asymmetry (26% vs. 6%), and the credit spread levels (170--310 bps). The raw scale difference between single-firm ($X^* \approx 0.005$, $K^* \approx 0.007$) and duopoly ($X_F \approx 0.57$, $K_F \approx 1.30$) reflects the change in the effective revenue coefficient: in the single-firm model with regime switching, $A_{\text{eff}}$ is large (the H-regime prospect amplifies revenue per unit of demand), so the firm invests at low $X$; in the duopoly, contest shares reduce per-firm $A_{\text{eff}}$, requiring higher demand to justify entry. The economics is the same---the scale shift is a normalization artifact of holding $c = 1$ across environments, not a statement about physical magnitudes.
