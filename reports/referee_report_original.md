# Investing in Artificial General Intelligence

**Date**: 2026-03-14, 10:44:20 a.m.
**Domain**: social_sciences/economics
**Taxonomy**: academic/research_paper
**Filter**: Active comments

---

## Overall Feedback

Here are some overall reactions to the document.

**Solving the real options boundary conditions in Section 2.3.3**

A central element of Section 2.3.3 is the specification of boundary conditions to solve the differential equation. The text asserts that under Assumption 1(A3), the homogeneous coefficient in $F_L(X)=A_1 X^{\beta_L^+}+C X^{\beta_H}$ satisfies "$A_1=0$ exactly" because "there is no L-regime exercise boundary to pin it down." The text then uses this simplified form to derive the trigger in Eq. (13).

However, the text also defines the particular-solution coefficient as $C=-\lambda B_H/Q_L(\beta_H)$, which is already pinned down by the underlying ODE. At the endogenous trigger $X^*$, value matching and smooth pasting are two conditions that generically determine the pair $(X^*,A_1)$, rather than determining $C$ alone. Clarifying exactly how the boundary logic leads to Eq. (13) and confirms the exactness of the simplification will be vital, as the paper states that "all analytical results are contained in this section" and relies heavily on this closed-form trigger for subsequent comparative statics and calibrations.


**The dimensionality of the default boundary in Proposition 2**

Proposition 2 and Eq. (18)–(19) derive the default boundary by taking a two-regime credit problem and applying a Leland-style smooth-pasting boundary as if it were a single-regime environment. This is accomplished by folding the $L\to H$ regime-switching environment into a unified $A_{\mathrm{eff},i}$ (Eq. 17) and an effective discount rate via $r+\lambda$ in the characteristic root.

In regime-switching structural credit settings, equity and debt values are usually governed by coupled systems across regimes, meaning the default policy itself is often regime-contingent. Readers will look for a formal demonstration that the optimal boundary here can be perfectly represented by a single-regime expression with an adjusted cash-flow coefficient. This structural step carries immense weight for the paper's headline "faith-based survival" mechanism. The sign and magnitude of $\partial X_D/\partial \lambda$, the interpretation of survival, and the properties of the training threshold $\underline\phi$ depend natively on this mapping. As an immediate focal point, readers will likely question how the closed-form $\underline\phi$ in Eq. (19) is completely independent of $\lambda$, given that Eq. (17) uses an explicit $\lambda/(r-\mu_L+\lambda)$ weighting.


**Rigidity in the training-inference allocation margin**

The model’s conceptual distinction relies heavily on the allocation $\phi$ linking current cash flow to future competitiveness, as outlined in Section 2.2.1 and formalized in Eq. 2–3 and Eq. 6. The current implementation handles this through specific structural constraints: $\phi$ is chosen once and fixed permanently, pre-switch training essentially has zero current value, post-switch inference is entirely worthless, and no capacity accumulates over time.

This formulation mechanically amplifies the "faith-based survival" channel, as $A_{\mathrm{eff}}$ can be elevated by shifting weight into the $H$ term. It also acts as a primary driver for the high calibrated optimum of $\phi^* \approx 0.70$ reported in Section 3.4. Given that the text acknowledges the existence of dynamic reallocation in practice in Section 3.3 and Section 5, there is a risk that the optimal default and training interactions might appear as artifacts of an imposed inability to reallocate compute near distress. Demonstrating how the core comparative statics and the "survival via training" logic behave if inference retains even minimal value post-switch, if training creates a persistent stock, or if firms can pay an adjustment cost to reset $\phi$, would anchor the economic discipline of the main results.


**Total industry revenue expansion in the contest specification**

Section 2.4.1 explicitly models competition using a Tullock specification and transparently notes that total industry revenue $\sum_i \pi_i$ "can exceed the symmetric benchmark" when firm capacities are asymmetric.

Because the strongest conclusions in the paper depend directly on leader-follower value gaps and slopes (Proposition 3's preemption logic) and the integration of $A_{\mathrm{eff},i}$ into the default boundary denominator in Eq. (18), this feature warrants deeper exploration. Both mechanisms are highly sensitive to whether winning a contest expands the total size of the pie or merely shifts shares. The document currently cites Appendix E regarding robustness to a Cournot specification, but the importance of this mechanic to the core narrative suggests doing more in the main text. Replicating the training responses, preemption gap, and faith-based survival region under a specification that holds total revenue $\sum_i \pi_i$ fixed, or detailing why the mechanisms inherently rely on generic share properties rather than absolute pie-expansion, would preempt structural concerns.


**Scale and normalization across model environments**

Section 3.4 reports baseline single-firm outcomes of $X^* \approx 0.0047$ and $K^* \approx 0.0067$, whereas the duopoly equilibrium yields $X_F \approx 0.57$ and $K_F \approx 1.30$. These figures occur under the same normalization $c=1$ and the same abstract demand shifter $X$.

The quantitative sections of the paper rely on levels to make economic points—such as the implied $\lambda$ derived from $\hat\phi$, the credit spread and default probability levels, and the actual magnitudes involved in "Dario's dilemma." Without a transparent mapping from the theoretical primitives to observable metrics indicating what one unit of $K$ or $X$ represents, these large raw scale jumps across the single-firm, duopoly, and levered blocks might read as normalization artifacts. A clear bridge keeping units interpretable and stable across all analytical environments is necessary to support the calibration-based claims.


**The strategic environment for Dario's Dilemma**

Section 4.3 formalizes the cost of belief mismatch entirely within the single-firm benchmark. However, the motivating narrative and the paper’s catalog of mechanisms heavily emphasize competitive preemption (Proposition 3) as the forcing function that pushes labs into aggressive capital commitments.

In a standalone environment, a firm manages timeline mismatch without facing the strategic penalty of being second. In the duopoly environment, an optimistic timeline mismatch interacts with the stopping problem, the race to secure leader identity, and the distribution of default risk. Evaluating the primary "dilemma" object outside the competitive environment that provides its essential economic tension softens the theoretical contribution of the paper. Shifting this formalization into the duopoly model would fully integrate the tail-risk claims with the strategic engine designed earlier in the paper.

**Status**: [Pending]

---

## Detailed Comments (33)

### 1. Incorrect determination of the particular solution coefficient C

**Status**: [Pending]

**Quote**:
> When does the simplified form $F_L = C \cdot X^{\beta_H}$ apply? The homogeneous coefficient $A_1$ is determined by value-matching and smooth-pasting at the L-regime investment trigger. When no interior trigger exists in the L-regime alone-specifically, when the option premium ratio $(1-1/\beta_L^+)/\alpha \ge 1$, so that L-regime revenue by itself is insufficient to justify investment-the general solution $F_L(X) = A_1 X^{\beta_L^+} + C X^{\beta_H}$ has $A_1 = 0$ because there is no L-regime exercise boundary to pin it down: the only boundary conditions are the smooth-pasting conditions at the investment trigger driven by $A_{\text{eff}}$ (which includes the H-regime prospect), and these determine $C$ alone.

**Feedback**:
There is an apparent inconsistency in the identification of coefficients in the L-regime ODE solution. Earlier, the text derives the particular-solution coefficient as $C=-\\lambda B_H/Q_L(\\beta_H)$, which (given an absorbing $H$ and a “known” $F_H$) pins down $C$ from the ODE’s forcing term. The quoted passage then states that under (A3) setting $A_1=0$ leaves smooth-pasting/value-matching at the L-regime trigger to “determine $C$ alone.” As written, these two statements conflict: if $C$ is re-identified from the trigger conditions it will generally differ from $-\\lambda B_H/Q_L(\\beta_H)$, and $F_L$ would not satisfy the stated HJB/ODE. This section would benefit from clarifying whether (i) $F_L=C X^{\\beta_H}$ with $A_1=0$ is intended as an approximation justified by the numerical smallness of the $A_1 X^{\\beta_L^+}$ term, or (ii) there is an additional consistency argument showing that the trigger conditions imply the same $C$ as the ODE-implied value in the maintained parameter region.

---

### 2. Contradiction regarding the leader's optimal capacity

**Status**: [Pending]

**Quote**:
> At baseline ( $\sigma=0.25$ ), preemption cuts the leader's trigger roughly in half relative to the monopolist. Competition primarily affects timing rather than scale: the leader's optimal capacity is identical to the monopolist's across all volatility levels.

**Feedback**:
The claim that “the leader's optimal capacity is identical to the monopolist's across all volatility levels” seems inconsistent with the duopoly payoff structure and with other statements later (e.g., Section 3.4’s remark that strategic interaction reduces per-firm capacity relative to the monopolist benchmark). Given the Tullock contest specification, contest shares $s_i^L,s_i^H$ depend on own capacity, so it is not obvious that the Proposition 1 homogeneity argument for $K^*$ (which uses $A_{\mathrm{eff}}=g(\phi)K^\alpha$) carries over unchanged to the leader in the preemption game. Please clarify (and, if this is a numerical regularity, document it) why $K_L(\sigma)$ coincides with the monopolist’s $K^{\text{mono}}(\sigma)$, and reconcile this with the paper’s other reported capacity comparisons.

---

### 3. Incorrect elasticities in Table 7

**Status**: [Pending]

**Quote**:
> The discount rate $r$ and revenue elasticity $\alpha$ are the most influential parameters for trigger and capacity, consistent with their central roles in real options theory (the cost of waiting) and the production technology (the value of capacity). The training fraction $\phi^*$ is most sensitive to the arrival rate $\lambda (\varepsilon=+12.7)$ and H -regime drift $\mu_{H}(\varepsilon=+8.3)$, confirming that beliefs about the regime switch are the primary driver of training allocation decisions.

**Feedback**:
Table 7’s reported sensitivities appear inconsistent with the paper’s own analytical characterization of the baseline optimum. In particular, Proposition 1 / Appendix A imply $K^*$ does not depend on $\lambda$ in the single-firm benchmark (the closed-form $K^*$ expression contains no $\lambda$), yet Table 7 reports a sizable $\varepsilon_{K^*}$ with respect to $\lambda$ (+4.8). Likewise, the implicit solution for $\phi^*$ from the FOC suggests a moderate local elasticity with respect to $\lambda$ at baseline (order-of-magnitude $\approx 0.5$ for the stated calibration), and the sign of $\partial \phi^*/\partial \alpha$ at baseline seems difficult to square with the negative elasticity reported. This looks like either a definition mismatch (e.g., transformed variables vs levels, arc vs point elasticities) or a numerical differentiation/implementation issue; it would help to reconcile Table 7 explicitly with Proposition 1 by clarifying what derivative is being computed and re-checking the routine.

---

### 4. Contradictions in baseline results comparison

**Status**: [Pending]

**Quote**:
> Under the baseline calibration, the single-firm model with training-inference allocation produces an investment trigger $X^{*} \approx 0.0047$, capacity $K^{*} \approx 0.0067$, and training fraction $\phi^{*} \approx 0.70$, where the effective revenue coefficient $A_{\text{eff}}$ (Equation 6) combines L-regime inference value and H -regime training value. The duopoly equilibrium with zero leverage produces
a follower policy of $X_{F} \approx 0.57, K_{F} \approx 1.30$, and $\phi_{F} \approx 0.70$, with the leader preempting at $X_{P} \approx 0.0082$ and the monopolist trigger at $X_{H}^{\text{mono}} \approx 0.0163$.

Strategic interaction accelerates investment (the preemption trigger $X_{P} \approx 0.0082 < X_{H}^{*} \approx 0.0163$ ) but reduces capacity per firm relative to the monopolist benchmark.

**Feedback**:
The baseline-results paragraph mixes several trigger/capacity objects (e.g., $X^{*}$, $X_P$, and a “monopolist trigger” denoted $X_H^{\\text{mono}}$ / $X_H^{*}$) without clearly distinguishing which regime/problem each comes from. As written, a reader could reasonably interpret the single-firm $X^{*}\\approx 0.0047$ as the monopolist benchmark, in which case the stated acceleration claim is difficult to reconcile with $X_P\\approx 0.0082$. Relatedly, the statement that competition “reduces capacity per firm relative to the monopolist benchmark” is not transparent given the reported $K^{*}\\approx 0.0067$ versus $K_F\\approx 1.30$ (unless a different capacity benchmark/regime or a same-state comparison is intended). Clarifying (i) what “monopolist trigger” is being used for the timing comparison and (ii) what capacity benchmark (and at what state) underlies the capacity comparison would make the interpretation of these numbers much clearer.

---

### 5. Contradiction regarding capacity optimization in duopoly

**Status**: [Pending]

**Quote**:
> The optimization is over two continuous variables ( $K_{F}, \phi_{F}$ )-or three $\left(K_{F}, \phi_{F}, \ell_{F}\right)$ when leverage is endogenous-with the trigger determined by smooth pasting at each evaluation.

**Feedback**:
The paper states after Proposition 1 that “The capacity formula in Proposition 1 carries over to the duopoly … [and contest] shares … do not enter the first-order condition for $K$.” However, in the duopoly specification (Section 2.4.1–2.4.2) the contest share $s_i^L,s_i^H$ depends on own capacity, so $A_{\mathrm{eff},i}$ is not obviously of the separable form $g(\phi_i)K_i^{\alpha}$ needed for the Proposition 1 capacity argument. Please reconcile this analytical claim with the duopoly payoff mapping (and with the later description of jointly optimizing over $(K_F,\phi_F)$): either provide the derivation/conditions under which the FOC for $K$ is unaffected by $s_i$, or qualify the “carry over” statement (e.g., as applying only to the monopoly/nesting case).

---

### 6. Contradictions regarding convexity and capacity independence

**Status**: [Pending]

**Quote**:
> The results show that equity value is increasing and convex in $\lambda$ : higher $\lambda$ implies earlier and larger investment with more training, generating more value from the growth option, and the marginal effect of higher $\lambda$ is itself increasing, so the valuation gap between optimistic and pessimistic firms widens as beliefs become more extreme. The steepest part of the valuation curve lies around $\lambda \in[0.1,0.5]$, precisely the range of disagreement among market participants. This convexity implies that a portfolio of frontier AI labs should exhibit positive convexity to AI timeline news: good news about AI capabilities should increase valuations more than bad news decreases them, because the option value is convex in the underlying arrival rate.

**Feedback**:
The paragraph asserts that “equity value is increasing and convex in $\lambda$” and uses this to motivate asymmetric responses to AI-timeline news. Earlier, Section 2.3.3 states that $F_L(X)$ “increases concavely in $\lambda$” and that $F_L$ approaches the $\lambda$-independent $F_H$ as $\lambda$ grows. If the Section 4.4 object is likewise bounded above as $\lambda\to\infty$, then global convexity in $\lambda$ cannot hold; at most, the value function could be locally convex over some intermediate range (e.g., the stated $\lambda\in[0.1,0.5]$). It would help to reconcile the curvature claim in Section 4.4 with the concavity/asymptote discussion in Section 2.3.3, especially because the asymmetric-news prediction in Section 5.2 relies on this curvature.

Separately, “higher $\lambda$ implies earlier and larger investment” is potentially confusing given the earlier single-firm result that $K^*$ is independent of $\lambda$ (Proposition 1 / Remark 1). If “larger” here refers to equilibrium capacity in the duopoly computation, it would be useful to make that distinction explicit; if instead it refers to “more aggressive” investment (timing and training intensity), the wording currently reads like a capacity comparative static.

---

### 7. Misspecification of the leader's H-regime continuation value

**Status**: [Pending]

**Quote**:
> Before the follower invests $\left(X<X_{F}\right)$, the leader earns monopoly revenue contest share $s_{L}=1$ in both regimes-and the effective revenue coefficient reflects the full monopoly value.

**Feedback**:
The statement “Before the follower invests $(X<X_F)$, the leader earns monopoly … in both regimes—and the effective revenue coefficient reflects the full monopoly value” is potentially misleading in the regime-switching setting. If the economy switches to regime $H$ while the follower is still out, the follower’s optimal entry threshold in $H$ need not equal the $L$-regime trigger, so the leader’s $H$-regime continuation value during the “pre-follower” phase is generally not a perpetual monopoly value. Please clarify whether $X_F$ is meant to be regime-contingent (e.g., $(X_F^L,X_F^H)$ or an overall entry policy) and how the leader’s pre-entry value accounts for follower entry following an $L\to H$ switch.

---

### 8. Confusion in the boundary condition for preemption existence

**Status**: [Pending]

**Quote**:
> A preemption trigger $X_{P} \in\left(0, X_{F}^{*}\right)$ exists such that $L\left(X_{P}\right)=F\left(X_{P}\right)$, where $L(X)=E_{L}(X)-(1-\ell) I\left(K_{L}\right)$ is the leader's NPV of entering at state $X$ and $F(X)$ is the follower's option value. Existence follows from continuity and the boundary conditions $L(0)<F(0)$ and $L\left(X_{F}^{*}\right)>F\left(X_{F}^{*}\right)$ (Appendix $A$ ).

**Feedback**:
The existence argument for $X_P$ uses the endpoint inequality $L(X_F^*)>F(X_F^*)$, but Appendix A’s justification (“the leader has accumulated monopoly rents over the interval since entry”) appears to rely on interpreting $L(X_F^*)$ as the leader’s continuation value at the moment the follower triggers after the leader entered earlier, rather than the “NPV of entering at state $X$” stated in Proposition 3(i). As written, the definition of $L(X)$ and the boundary-condition argument are not fully aligned, so it is unclear that $L(X_F^*)>F(X_F^*)$ is the correct endpoint condition for applying the IVT on $(0,X_F^*)$. Please clarify the precise definition/conditioning of $L(X)$ (invest-now payoff vs. post-entry continuation value) and adjust the endpoint argument accordingly.

---

### 9. Misunderstanding of Assumption (A2) and numerical optimization

**Status**: [Pending]

**Quote**:
> Assumption (A2) at archetype-specific WACCs. The option premium condition (A2), $1/\gamma<\left(\beta_{H}-1\right) /\left(\alpha \beta_{H}\right)<1$, depends on $r$ through $\beta_{H}$. At the baseline $r=0.12$, (A2) holds. At extreme archetype WACCs, (A2) may fail: the hyperscaler ( $r=0.10$ ) violates the lower bound; the compute racer ( $r=0.18$ ) violates the upper bound. All archetype-specific results use full numerical optimization that does not require (A2).

**Feedback**:
The discussion of Assumption (A2) and the archetype-WACC boundary check seems to need clarification/correction. With the baseline primitives used elsewhere in the paper, lowering $r$ to 0.10 appears unlikely to violate the *lower* bound in (A2), so the statement about the hyperscaler may be a numerical slip (or it may rely on additional archetype-specific parameter changes that are not stated here). More importantly, “full numerical optimization … does not require (A2)” is potentially misleading: (A2) is introduced as ensuring an interior capacity optimum, so if it fails the scale-choice problem may become a corner solution (or otherwise poorly behaved) unless the numerical implementation imposes explicit feasible bounds/regularization on $K$. It would help to be explicit about how the optimizer behaves and how reported archetype results should be interpreted in parameter regions where (A2) is violated.

---

### 10. Mismatched segment revenue and corporate CapEx

**Status**: [Pending]

**Quote**:
> For the Google-like archetype, revenue is Google Cloud revenue (\$43.2B in 2024, growing 37-39% to \$59-60B in 2025 per the Alphabet SEC filing), not Alphabet-wide revenue (\$403B); CapEx is total Alphabet capital expenditure (\$91.4B in 2025), approximately 60% to servers and 40% to data centers and networking.

**Feedback**:
The Google-like archetype pairs segment revenue (Google Cloud) with consolidated Alphabet CapEx, which makes the reported CapEx/Revenue ratio difficult to interpret and likely inflates the “1.5x” investment-intensity narrative. The text elsewhere notes that the CapEx concept differs across archetypes, but it would help to clarify whether the hyperscaler ratio is meant as a firm-wide AI-infrastructure proxy (hence consolidated CapEx is intentional) or as a segment-level investment-intensity measure (in which case some alignment of numerator/denominator is needed for comparability).

---

### 11. Incorrect elasticity value and backwards logic on uncertainty propagation

**Status**: [Pending]

**Quote**:
> The high elasticity of $\phi^{*}$ with respect to $\lambda$ ( $\varepsilon=+12.7$ at baseline) means that this uncertainty propagates substantially into implied beliefs: inverting $\phi^{*}(\lambda)=\hat{\phi}$ for each archetype at $\hat{\phi} \pm 0.10$ yields implied arrival rates that span roughly a factor of two

**Feedback**:
The reported “high elasticity” $\varepsilon=+12.7$ for $\phi^*$ with respect to $\lambda$ appears inconsistent with the model’s own single-firm FOC in Appendix A (Proof of Proposition 1, Step 5), which implies $\varepsilon_{\phi^*,\lambda}=(1-\phi^*)/(1-\alpha)$ and hence $\varepsilon\approx 0.50$ at the baseline values $\phi^*\approx 0.70$, $\alpha=0.40$. This also better matches the inversion examples reported in the same paragraph (e.g., $\hat\phi=0.75\pm 0.10 \Rightarrow \lambda\in[0.09,0.17]$). In addition, the intuition about uncertainty “propagating” into implied beliefs seems reversed: a high forward elasticity of $\phi^*$ in $\lambda$ would imply a low (attenuating) local elasticity of the inverse mapping $\lambda(\phi^*)$, whereas substantial amplification of $\hat\phi$ uncertainty into $\lambda$ corresponds to a low forward elasticity (high inverse elasticity). Please check both the elasticity calculation/definition being referenced here and the direction of the uncertainty-propagation argument.

---

### 12. Asset pricing terminology contradiction

**Status**: [Pending]

**Quote**:
> The baseline discount rate is $r=0.12$, the risk-adjusted WACC for a representative frontier AI lab. As discussed in Section 2, $r$ is the WACC and $\mu_{s}$ is the risk-adjusted (certaintyequivalent) growth rate; all valuation uses this reduced-form framework throughout.

**Feedback**:
The use of “risk-adjusted (certainty-equivalent) growth rate” $\mu_s$ alongside a WACC discount rate $r$ is potentially confusing, because “certainty-equivalent” language is often associated with discounting at $r_f$ rather than WACC. Footnote 12 in Section 2 does indicate a reduced-form convention in which $\mu_s$ is already adjusted by a risk premium so that discounting at $r$ is appropriate, but Section 3.1 would benefit from making that interpretation explicit and aligning it with the calibration discussion (analyst growth projections) and the later use of a separate $r_f$ in credit-spread calculations.

---

### 13. Incorrect comparative static for training fraction

**Status**: [Pending]

**Quote**:
> Step 6: Comparative statics. From the implicit function theorem applied to the FOC $\partial A_{\text {eff }} / \partial \phi=0$, with $\partial^{2} A_{\text {eff }} / \partial \phi^{2}<0$ :
(i) $\partial \phi^{*} / \partial \lambda>0$ : Higher $\lambda$ increases $w_{H} / w_{L}=\lambda A_{H}$. Since $\phi^{*}$ is increasing in $w_{H} / w_{L}$ (from the FOC ), the optimal training fraction rises.
(ii) $\partial \phi^{*} / \partial\left(r-\mu_{L}\right)^{-1}<0$ : A higher L-regime revenue premium $1 /\left(r-\mu_{L}\right)$ raises $w_{L}$ relative to $w_{H}$, decreasing $w_{H} / w_{L}$ and shifting the optimal allocation toward inference.

**Feedback**:
Step 6(ii) appears algebraically inconsistent with the preceding definitions of $w_L$ and $w_H$. Given $w_L=1/(r-\mu_L+\lambda)$ and $w_H=\lambda A_H/(r-\mu_L+\lambda)$ (with $A_H=1/(r-\mu_H)$), the ratio in the FOC simplifies to $w_H/w_L=\lambda A_H=\lambda/(r-\mu_H)$, which is independent of $\mu_L$. Under the model as written, this implies $\phi^*$ should not vary with $(r-\mu_L)^{-1}$ (the derivative should be zero), so the stated sign in (ii)—and the corresponding claim in Proposition 1 if repeated there—should be reconciled with the formulas (either by correcting the comparative static or clarifying a different notion of “L-regime revenue premium” that actually shifts $w_H/w_L$).

---

### 14. Misleading notation and definition for value loss ($\Delta V$)

**Status**: [Pending]

**Quote**:
> The value loss from mismatch is:

$$
\Delta V=\operatorname{NPV}\left(\lambda_{\text {true }}, \lambda_{\text {true }}\right)-\operatorname{NPV}\left(\lambda_{\text {true }}, \lambda_{\text {invest }}\right),
$$

where $\operatorname{NPV}\left(\lambda_{a}, \lambda_{b}\right)$ denotes the NPV of investing according to belief $\lambda_{b}-\operatorname{choosing}\left(X^{*}, K^{*}, \phi^{*}\right)$ optimal for $\lambda_{b}$-when the true parameter is $\lambda_{a}$.

**Feedback**:
The definition of $\Delta V$ is hard to parse because $\operatorname{NPV}(\lambda_a,\lambda_b)$ is not clearly pinned down as a time-0 (common-$X_0$) value of following the policy optimized under $\lambda_b$ when the true process is governed by $\lambda_a$. Given the paper’s earlier (standard) use of “NPV” as the exercise payoff, a reader can easily (mis)read this as an NPV evaluated at two different triggers/stopping states. It would help to clarify explicitly whether $\operatorname{NPV}(\lambda_a,\lambda_b)$ is an option-value/policy-value functional evaluated at a common initial state. Separately, $\Delta V$ is introduced in levels but then discussed as a percentage loss (e.g., “loses $26\%$ of value” and $\Delta V\approx 26\%$), and Figure 10 appears to use a normalized loss; the normalization underlying the reported percentages should be stated at the point where $\Delta V$ is defined.

---

### 15. Unlevered equity value ignores the abandonment option

**Status**: [Pending]

**Quote**:
> At $X=X_{D}, E\left(X_{D}\right)=-(1-\ell) I(K) \leq 0$: the equity holders' sunk contribution is lost, but limited liability prevents negative payoffs, so equity is worth $\max \{E(X), 0\}$. Without debt ( $\ell=0$ ), the expression simplifies to the NPV of the unlevered investment: $E(X)= A_{\mathrm{eff}, i} X-\delta K / r-I(K)$.

**Feedback**:
The statement that, when $\ell=0$, equity “simplifies to the NPV of the unlevered investment” is potentially inconsistent with the stopping-boundary structure when $\delta>0$. If operating costs can be avoided by shutdown/liquidation, an unlevered firm generally has an abandonment option and a positive abandonment threshold, so an option term would remain in the value (the levered formulas with $c_D=0$ would naturally suggest this). If instead abandonment/mothballing is ruled out in the model, it would help to clarify that $X_D$ and the option term are only meant to apply in the levered/default setting and that the $\ell=0$ case is solved as a pure perpetuity with no endogenous exit.

---

### 16. Mismatch between value decomposition formulas and Figure 8

**Status**: [Pending]

**Quote**:
> Figure 8 illustrates the value decomposition. Panel (a) decomposes total firm value into assets-in-place (blue) and capacity gap value (orange) as a function of installed capacity relative to the optimal level $K_{H}^{*}$. When the firm has little installed capacity ( $K / K_{H}^{*} \ll 1$ ), most of its value comes from the potential to reach optimal capacity, and assets-in-place are small.

**Feedback**:
The value-decomposition formulas in Section 4.1 are written in terms of $A_{\\mathrm{eff}}$ and $(K^{*},\\phi^{*})$, which reads like a pre-switch ($L$ with switching) valuation object. But the discussion of Figure 8 normalizes by $K_H^{*}$ and the caption notes “Parameters: regime $H$” (and demand at $1.5 X_H^{*}$), which makes it unclear whether the plotted decomposition is meant to be an $H$-regime illustration (potentially using an $H$-specialized version of the coefficient) or the $L$-regime decomposition defined just above. Clarifying which regime’s valuation object is used in Figure 8 (and how it relates to the $A_{\\mathrm{eff}}$ notation in the formulas) would help interpret the figure.

---

### 17. Incorrect comparative static for survival threshold

**Status**: [Pending]

**Quote**:
> Note that $\underline{\phi}$ is decreasing in $\alpha$ (lower diminishing returns make training more effective), decreasing in $\mu_{H}-\mu_{L}$ (a larger regime-switch growth premium amplifies the $H$-regime term), and increasing in $r$ (higher discounting reduces the present value of the continuation opportunity).

**Feedback**:
The stated comparative static of the closed-form threshold $\underline{\phi}=R/(1+R)$ with $R=((r-\mu_H)/(r-\mu_L))^{1/\alpha}$ seems to have the wrong sign in $\alpha$. With $r>\mu_H>\mu_L$, the base is in $(0,1)$, so $R$ (and hence $\underline{\phi}$) is increasing in $\alpha$, not decreasing. The accompanying intuition about “lower diminishing returns” should be made consistent with this sign.

---

### 18. Inaccurate claim about convexity of leader's value function

**Status**: [Pending]

**Quote**:
> The enriched payoff environment of this paper introduces additional features-capacity choice, training allocation, leverage with default, and regime switching-that modify the value function shapes beyond the standard framework. In particular: (a) the default kink at $X_{D}$ introduces a non-smooth point in $L(X)$; (b) the training allocation creates an additional channel through which the leader value depends on $X$; and (c) the regime-switching option adds a convex component to both $L(X)$ and $F(X)$.

**Feedback**:
The claim in (c) that regime switching “adds a convex component to both $L(X)$ and $F(X)$” is potentially ambiguous for the leader. While $F(X)$ is indeed convex (power-function option component), it is not obvious that regime switching contributes a positive convexity component to the leader value rather than (depending on coefficients) a concave loss term associated with post-switch competitive entry. It would help to clarify in what sense “convex component” is meant for $L(X)$ (e.g., the presence of additional option-like power terms versus a statement about the sign of $L''(X)$ over the relevant region).

---

### 19. Flawed intuition for marginal cost of training in Appendix A

**Status**: [Pending]

**Quote**:
> This double penalty makes training more expensive in the duopoly phase.

The follower, by contrast, enters directly into the duopoly phase and always faces the double penalty.

The monopoly-phase effect dominates because: (a) the monopoly phase occurs first, so its cash flows are discounted less; (b) the duration of the monopoly phase [ $X_{P}, X_{F}$ ] is endogenous and substantial... and (c) the H-regime benefit of training is independent of the competitive phase, so the leader's higher marginal benefit from uncontested H -regime positioning applies equally in both phases.

**Feedback**:
The “double penalty” intuition here seems potentially misleading given the paper’s own Tullock payoff. Holding the rival fixed, duopoly L-regime revenue $\pi_i^L=X\cdot y_i^2/(y_i+y_j)$ implies $\partial \pi_i^L/\partial y_i = X\,s_i(2-s_i)\le X$, so the absolute marginal loss from raising $\phi_i$ via reduced inference capacity (lower $y_i$) is scaled down relative to monopoly ($s_i=1$). If “more expensive” is meant in some other sense (e.g., proportional effect, or incorporating equilibrium follower responses / phase durations), it would help to clarify that precisely. Relatedly, claim (c) that the H-regime benefit of training is “independent of the competitive phase” appears too strong as written, since H-regime payoffs are contested after follower entry and therefore depend on whether the regime switch occurs during the monopoly interval versus during the duopoly interval.

---

### 20. Conflation of dynamic reallocation with learning about $\lambda$

**Status**: [Pending]

**Quote**:
> If the regime switch has not occurred after one period, the firm observes that it remains in regime $L$, which is (weakly) bad news about $\lambda_{\text{true}}$. The optimal response is to decrease $\phi$-shift from training to inference to bolster L-regime revenue.

**Feedback**:
The sentence frames “no switch after one period” as “bad news about $\\lambda_{\\text{true}}$,” but under the baseline specification where $\\lambda$ is known and the switch time is exponential (memoryless), non-arrival does not update beliefs about $\\lambda$ and would not by itself generate a time trend in the optimal $\\phi$ while still in regime $L$. If the intended intuition is instead (i) an incomplete-information extension with Bayesian learning about an unknown $\\lambda$, or (ii) a finite-horizon/two-period effect (less remaining time to benefit from training), that distinction should be made explicit; otherwise, the dynamic-$\\phi$ bias argument should be grounded purely in the option value of reallocating upon the realized regime switch (which the paragraph already articulates).

---

### 21. Incorrect mathematical explanation for Dario's dilemma asymmetry

**Status**: [Pending]

**Quote**:
> Because $A_{\text {eff }}$ is concave in $\phi$ with an interior maximizer near $\phi^{*} \approx 0.70$, and the H -regime term is large relative to the L -regime term, the value function is more steeply curved on the under-training
side. This channel contributes $W^{\prime \prime \prime}>0$ and is novel relative to standard real options models.

**Feedback**:
The heuristic explanation tying the asymmetry to $A_{\text{eff}}$ being “more steeply curved on the under-training side” seems questionable as stated. In the single-firm benchmark, $A_{\text{eff}}(\phi)$ is a weighted sum of $(1-\phi)^\alpha$ and $\phi^\alpha$, and (at the baseline calibration with an interior optimum near $\phi^*\approx 0.70$) the local third-derivative asymmetry of $A_{\text{eff}}$ around $\phi^*$ appears to go in the opposite direction (i.e., locally steeper curvature as $\phi$ increases). Since the relevant object is $W(\lambda_{\text{invest}})$, it would be helpful to separate the drivers more cleanly: the dominance of the H-regime component and the nonlinear/bounded mapping $\lambda_{\text{invest}}\mapsto \phi^*(\lambda_{\text{invest}})$ (and $\lambda_{\text{invest}}\mapsto X^*$) can generate asymmetry in $W$ even if $A_{\text{eff}}(\phi)$ is locally steeper on the over-training side.

---

### 22. Mix-up between cost convexity ($\gamma$) and revenue concavity ($\alpha$)

**Status**: [Pending]

**Quote**:
> A firm invests an irreversible lump sum $I(K)=c K^{\gamma}$ to install capacity $K>0$, where $\gamma>1$ captures diminishing returns (equivalently, convex investment costs). This specification nests the standard linear cost ($\gamma=1$, constant returns) and reflects the empirical regularity that AI scaling laws exhibit diminishing returns to compute (Kaplan, McCandlish, Henighan, Brown, Chess, et al., 2020; Hoffmann, Borgeaud, Mensch, Buchatskaya, Cai, et al., 2022): doubling compute does not double capability.

**Feedback**:
At first this paragraph made it sound like the scaling-laws evidence (“doubling compute does not double capability”) is being used to justify the convex installation cost $I(K)=cK^\gamma$ with $\gamma>1$. Given the model’s definitions, scaling laws seem to map more directly to concavity of payoffs in compute, which is already captured by the revenue exponent $\alpha\in(0,1)$ in $\pi_i^L$ and $\pi_i^H$. In contrast, $\gamma>1$ is naturally interpreted as increasing marginal cost of building additional physical capacity (power/siting/procurement constraints, etc.). It would help to separate these two economic mechanisms cleanly when introducing $\gamma$ versus $\alpha$.

---

### 23. Flawed mathematical justification for asymmetric revenue

**Status**: [Pending]

**Quote**:
> Total industry revenue $\sum_{i} \pi_{i}=X \cdot \sum_{i}\left[\left(1-\phi_{i}\right) K_{i}\right]^{2 \alpha} / \sum_{j}\left[\left(1-\phi_{j}\right) K_{j}\right]^{\alpha}$ can exceed the symmetric benchmark because the sum of $2 \alpha$-terms in the numerator exceeds the squared sum of $\alpha$-terms.

**Feedback**:
The explanation for why $\sum_i \pi_i$ can exceed the symmetric benchmark appears to rely on an incorrect inequality. With $y_i=[(1-\phi_i)K_i]^\alpha>0$, total revenue is $X\,(y_1^2+y_2^2)/(y_1+y_2)$, and it is not true that $y_1^2+y_2^2$ exceeds $(y_1+y_2)^2$. The intended comparison seems to be against the symmetric benchmark $X\,(y_1+y_2)/2$, in which case the correct inequality is $y_1^2+y_2^2 \ge (y_1+y_2)^2/2$ (strict under asymmetry), or equivalently that the expression is a share-weighted average that exceeds the simple average when capacities are dispersed.

---

### 24. Contradiction regarding hardware repurposing in Introduction

**Status**: [Pending]

**Quote**:
> Both activities consume the same scarce hardware, purpose-built GPU clusters housed in multi-billion-dollar data centers, creating an intertemporal allocation problem with no close parallel in traditional capital budgeting. ${ }^{2}$

These facilities take years to build, and purpose-built training clusters cannot be easily repurposed.

**Feedback**:
The Introduction’s juxtaposition of “Both activities consume the same scarce hardware” with “purpose-built training clusters cannot be easily repurposed” is likely to confuse readers about the intended degree of fungibility between training and inference compute. Later (e.g., Section 5.4) the paper notes that firms can reallocate GPUs between training and inference on week-scale horizons, which makes the “cannot be easily repurposed” wording feel too strong unless it is meant in a narrower sense (e.g., facility-level irreversibility, or substantial adjustment costs from cluster/network/software architecture rather than literal impossibility). It would help to clarify what repurposing friction is being asserted here and how it relates to the static-$\phi$ abstraction.

---

### 25. Inaccurate description of monopoly opportunity cost

**Status**: [Pending]

**Quote**:
> Duopoly preemption changes both timing and training incentives: the leader allocates more to training than the follower because the monopoly phase eliminates the opportunity cost of forgone inference revenue.

**Feedback**:
The mechanism in this sentence seems overstated. Even in the monopoly phase, increasing the training fraction $\phi_L$ still reduces inference capacity $(1-\phi_L)K_L$ and therefore lowers monopoly inference revenue, so the direct opportunity cost of foregone inference cash flow is not eliminated. What monopoly removes is the additional strategic/contest-share component of that cost (since $s_L^L=1$ is insensitive to $(1-\phi_L)K_L$ during monopoly), which makes training cheaper at the margin relative to the duopoly phase. Clarifying this distinction would better align the Introduction with the later discussion of Proposition 3.

---

### 26. Contradiction regarding fixed market size in Tullock contest

**Status**: [Pending]

**Quote**:
> Revenue depends on relative capacity, which fits a zero-sum share game but not a growing market; in particular, the Tullock form assumes a fixed total market size, which understates the market expansion effect of AI adoption and biases the model toward stronger competition effects relative to a setting where investment expands the pie.

**Feedback**:
Statement “the Tullock form assumes a fixed total market size” seems imprecise relative to the model’s own contest payoff in Section 2.4.1: with $\pi_i^L=X\,[(1-\phi_i)K_i]^{2\alpha}/(\cdot)$, aggregate industry revenue generally depends on $(K_i,K_j)$ and scales up if both firms’ capacities are scaled proportionally. If the intended limitation is instead that the contest share is zero-sum (pure business stealing) and that symmetric entry/duplication does not expand aggregate revenue (unlike, e.g., a Cournot specification with additive quantities), it would help to clarify that distinction here.

---

### 27. Inconsistent notation for the continuous coupon payment

**Status**: [Pending]

**Quote**:
> Debt pays a continuous coupon $d=c_{d} \cdot \ell \cdot I(K)$ where $c_{d}$ is the coupon rate. Following Leland (1994), equity holders choose to default endogenously when the equity value falls to zero.

**Feedback**:
The notation for the continuous coupon cash flow is inconsistent across Sections 2.4.3–2.4.5: it is introduced as $d=c_d\ell I(K)$, then the default boundary/equity formulas use $c_D$ as the coupon payment, and the debt value equation reverts to $d$. Even if $c_D\equiv d$ is intended, the switch (and the visual proximity of $c_D$ to the rate $c_d$) makes it easy to misread the cash-flow terms when tracking the default boundary and valuation equations.

---

### 28. Revenue increase from capacity doubling in contest

**Status**: [Pending]

**Quote**:
> The revenue elasticity $\alpha=0.40$ governs diminishing returns to capacity in revenue generation, entering both the L-regime inference contest (Equation 14) and the H-regime training contest (Equation 15). Doubling the relevant capacity measure increases revenue by approximately $2^{0.4} \approx 1.32$ times-a $32\%$ increase rather than $100\%$

**Feedback**:
The $2^{0.4}\approx 1.32$ calculation correctly describes the concavity of the underlying $C^\alpha$ term (and would be exact under monopoly/constant-share comparisons). However, because the sentence directly references the Tullock contests (Eq. 14–15), a reader might misread it as describing the effect of a unilateral capacity increase in a symmetric duopoly; in that experiment, revenue also rises via a higher contest share, so the total revenue gain would exceed $2^\alpha$. A brief clarification of which channel/comparison the “32%” figure refers to would remove this ambiguity.

---

### 29. Mismatch between heading and text in the third tension

**Status**: [Pending]

**Quote**:
> Third, waiting value versus preemption pressure: Dario's dilemma reveals an asymmetric cost of belief mismatches. Conservative underinvestment is costlier in expected value than aggressive overinvestment for the same magnitude of belief error, because under-allocating to training forfeits the H -regime option value that dominates firm worth.

**Feedback**:
At first the heading “waiting value versus preemption pressure” made me expect a summary tied directly to the duopoly preemption mechanism (leader investing below the single-firm trigger). The accompanying explanation instead focuses on Dario’s dilemma and the asymmetric expected-value costs of belief errors via under-allocation to training and lost H-regime continuation value. If Dario’s dilemma is meant to illustrate the same “wait vs. go early” margin (with preemption as one force that compresses waiting value), it would help to make that connection explicit here; otherwise the label of the third tension seems misaligned with the text that follows.

---

### 30. Incomplete expression for marginal cost of training

**Status**: [Pending]

**Quote**:
> Monopoly phase: The leader's L-regime revenue is $X \cdot\left[\left(1-\phi_{L}\right) K_{L}\right]^{\alpha}$ with $s_{L}^{L}=1$. Increasing $\phi_{L}$ reduces inference capacity but does not affect market share - the marginal cost is only the direct capacity effect $\alpha\left(1-\phi_{L}\right)^{\alpha-1}$.

**Feedback**:
At first, the phrase “the marginal cost is only the direct capacity effect $\alpha(1-\phi_L)^{\alpha-1}$” made it hard to reconcile the statement with the revenue expression $X[(1-\phi_L)K_L]^\alpha$, whose derivative in levels is $-X\alpha K_L^\alpha(1-\phi_L)^{\alpha-1}$. I understand the intent is to isolate the $\phi_L$-dependent part of the direct capacity channel (and to contrast it with the additional contest-share-loss channel in duopoly), but it would be clearer to indicate that the marginal revenue loss is proportional to $\alpha(1-\phi_L)^{\alpha-1}$ (or to specify the normalization) rather than presenting it as the full marginal cost.

---

### 31. Direction of markup factor limit

**Status**: [Pending]

**Quote**:
> The $\beta$-channel is positive because increasing $\lambda$ raises the effective discount rate ( $r+\lambda$ ), making $\beta_{s}^{-}$more negative and pushing the markup $M$ toward 1 from above $\left(d M / d \lambda=1 /\left[\left(\beta_{s}^{-}-1\right)^{2} D\right]>0\right.$, where $\left.D=\sqrt{\left(\mu_{L}-\sigma^{2} / 2\right)^{2}+2 \sigma^{2}(r+\lambda)}\right)$.

**Feedback**:
The statement that increasing $\lambda$ pushes the markup $M\equiv \beta_s^- /(\beta_s^- -1)$ “toward 1 from above” appears inconsistent with $\beta_s^-<0$. For $\beta_s^-<0$, $M\in(0,1)$, and as $\lambda$ increases (making $\beta_s^-$ more negative), $M$ increases toward 1 from below. The sign of $dM/d\lambda>0$ seems fine, but the “from above” direction is likely a slip (perhaps conflating with the usual investment-trigger markup $\beta^+/(\beta^+-1)>1$).

---

### 32. Notational slip in describing Huisman and Kort (2015)

**Status**: [Pending]

**Quote**:
> In the standard Huisman and Kort (2015) framework, uniqueness follows from single crossing: the leader value $L(X)$ crosses the follower value $F(X)$ exactly once on $\left(0, X_{F}^{*}\right)$. In their model, $L(X)$ is approximately affine in $X$ (installed revenue minus costs) while $F(X) \propto X^{\beta_{H}}$ is strictly convex with $F(0)=0>L(0)$, yielding at most one crossing.

**Feedback**:
I initially read the phrase $F(X)\propto X^{\beta_H}$ as asserting Huisman and Kort (2015) specifically use the paper’s H-regime characteristic root notation. However, the surrounding argument only needs “a positive root $\beta>1$ giving a strictly convex power function,” so this looks mainly like notation overloading. Still, since the sentence is explicitly describing “their model,” it would reduce confusion to denote the HK exponent generically (or explicitly note it is the positive characteristic root in the standard GBM benchmark), rather than $\beta_H$ which elsewhere denotes the high-regime root in this paper.

---

### 33. Notation overload for variable N

**Status**: [Pending]

**Quote**:
> (iii) Leverage-training substitution. Write the default boundary as $X_{D}=N(\ell) / A_{\text {eff }, i}\left(\phi_{i}\right)$, where $N(\ell)=\left[\beta_{s}^{-} /\left(\beta_{s}^{-}-1\right)\right] \cdot\left(c_{d} \ell I(K) / r+\delta K / r\right)$ is strictly increasing in leverage.

**Feedback**:
At first the use of $N$ here made it seem like the paper was redefining the same auxiliary quantity in two different ways across adjacent paragraphs (first $N=c_D/r+\delta K_i/r$ in the $\partial X_D/\partial\lambda$ decomposition, then $N(\ell)$ absorbing the markup factor as well). After reading closely, the intent is clear—(iii) is simply regrouping the default-boundary expression for leverage comparative statics and making the $\ell$ dependence explicit—but the reuse of the base symbol $N$ so close together creates a small risk of confusion, especially given the preceding discussion of $M(\beta_s^-)$ as $\lambda$-dependent.

---
