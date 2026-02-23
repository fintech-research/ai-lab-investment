# Referee Report

**Paper:** "Investing in Artificial General Intelligence"

**Recommendation:** Revise and Resubmit (Major Revision)

---

## Summary

This paper develops a real-options model of irreversible capacity investment for frontier AI laboratories, incorporating regime switching (low to high demand), a training-inference compute allocation decision, duopoly competition via Tullock contests, and endogenous default risk à la Leland (1994). The key novelty is the training-inference allocation: firms choose how to split scarce GPU capacity between model training (building future capability) and inference serving (generating current revenue), with regime-specific competition structures in each use. The paper delivers three propositions (optimal allocation, faith-based survival, preemption equilibrium) and a numerical finding on the asymmetric "AI investment dilemma." A stylized calibration to four firm archetypes illustrates the mechanisms.

The paper tackles a genuinely important question—arguably the largest capital allocation event currently underway—and does so using a well-constructed theoretical framework that combines established tools in creative ways. The training-inference allocation is a novel and economically meaningful addition to the real options literature, and the faith-based survival mechanism is an elegant result. However, several issues in the model derivation, the analytical claims, and the calibration require attention before the paper is suitable for publication.

---

## 1. Contribution Assessment

### Strengths

The paper's main contribution—embedding a training-inference allocation in a regime-switching real options framework—is genuine and well-motivated. The economic setting is novel: no existing paper in the real options or strategic investment literatures models the intertemporal compute allocation problem facing AI labs. The regime-specific competition structure (inference matters today, training quality matters post-adoption) creates a meaningful strategic trade-off that does not reduce to a standard R&D investment problem. The closest analog is the exploration-exploitation allocation in Akcigit and Kerr (2018), but the compute allocation is sufficiently different (shared hardware, regime-dependent payoff structures, Tullock-style competition) that the paper carves out a distinct niche.

The faith-based survival mechanism (Proposition 2) is the paper's most striking result and is well-named. The idea that training investment raises the continuation value, which lowers the default boundary, which keeps the firm alive to benefit from the regime switch—this is a clean, economically intuitive channel that emerges naturally from the model structure. It connects real options theory to the "survival through belief" narrative that dominates AI industry discourse.

The AI investment dilemma (Numerical Finding 2) is a useful quantitative contribution. The asymmetry between overinvestment and underinvestment losses is not obvious ex ante (the standard real options result is that the option value of waiting penalizes premature investment, which would suggest overinvestment is worse—but the training channel and leverage amplification add texture). The connection to the Amodei quote about trillion-dollar commitments is effective.

### Weaknesses in Contribution Framing

The paper somewhat undersells the methodological contribution relative to the applied contribution. The combination of regime switching, Tullock competition, training allocation, and endogenous default in a single tractable framework is technically impressive—but the paper presents this as four separate "contributions" (analytical, strategic, financing, quantitative) rather than emphasizing the integrated framework. I would recommend restructuring the introduction to lead with the unified framework as the primary contribution, with the propositions as results that flow from it.

The paper claims the duopoly is a "deliberate scope choice, not a limitation" (p. 3–4). This is somewhat defensive. The justification that frontier AI training is highly concentrated is reasonable, but the paragraph then acknowledges that "broader oligopoly crowding, coalition effects, entry and exit" are important. A more forthright treatment would be to simply state that duopoly is the analytically tractable case, that the N-firm extension in Appendix C confirms robustness, and leave it at that.

---

## 2. Literature Review

The literature review is comprehensive and well-organized. The paper correctly identifies its core building blocks (McDonald and Siegel 1986, Grenadier 2002, Huisman and Kort 2015, Leland 1994, Guo et al. 2005) and articulates clearly how it extends each. A few gaps:

1. **Lambrecht and Perraudin (2003)** study real options in duopoly with incomplete information—relevant given that the paper's key mechanism involves heterogeneous beliefs about λ. The belief heterogeneity across firms is central to the AI investment dilemma but is not connected to the literature on investment under disagreement.

2. **Nishihara and Ohyama (2021)** and the broader literature on multi-stage investment under regime switching may be relevant, particularly given the discussion of staged investment strategies in Section 4.3.3.

3. **Décamps, Mariotti, and Villeneuve (2006)** on irreversible investment with regime switching is a closer predecessor than acknowledged. Their two-regime model with absorbing high state is structurally similar; the paper should discuss how the training-inference allocation and Tullock competition differentiate the present framework.

4. The paper cites the AI economics literature (Acemoglu 2024, Korinek 2024, Jones 2024) but does not engage substantively with it. How does this paper's partial equilibrium model relate to the general equilibrium growth implications? A brief discussion would strengthen the positioning.

5. The empirical AI literature (Babina et al. 2024, Eisfeldt et al. 2024) is cited but not leveraged for calibration or testable predictions. If these papers provide relevant estimates (e.g., AI firm betas, investment intensities), they could discipline the calibration.

---

## 3. Model Derivation and Proofs

### 3.1 Proposition 1 (Optimal capacity and training fraction)

The proof is generally correct but has a significant presentation issue. The proposition statement mixes the H-regime closed-form (which is the standard real options result with training allocation) and the L-regime joint optimization (which is the novel result). These should be more clearly separated, since the H-regime capacity formula is essentially a direct calculation while the L-regime optimization involves the effective revenue coefficient $A_{\text{eff}}$.

**Issue with the capacity formula.** The stated optimal capacity (p. 13) is:

$$K^* = \left[\frac{\delta(\alpha\beta_H - \beta_H + 1)}{r\,c\,(\gamma(\beta_H - 1) - \alpha\beta_H)}\right]^{1/(\gamma-1)} \cdot \phi^{-\alpha/(\gamma-1)}$$

This is derived from the H-regime FOC. The condition $1/\gamma < (\beta_H - 1)/(\alpha\beta_H) < 1$ ensures the denominator is positive and the capacity is finite. However, the dependence on $\phi$ through $\phi^{-\alpha/(\gamma-1)}$ means that this is not truly the "optimal capacity" but rather the optimal capacity *conditional on* a given $\phi$. The joint optimization over $(K, \phi)$ must solve the coupled system, and the paper does not provide the reduced-form expression for $K^*$ after substituting the optimal $\phi^*$. This is fine if acknowledged explicitly, but as stated, Proposition 1 is slightly misleading because it gives the impression of a closed-form solution for the joint optimum.

**The Inada conditions argument** (Step 5, Appendix A) is correct. The proof that $\partial A_{\text{eff}}/\partial\phi \to +\infty$ as $\phi \to 0^+$ and $\partial A_{\text{eff}}/\partial\phi \to -\infty$ as $\phi \to 1^-$ follows from $\alpha \in (0,1)$, and the strict concavity of $A_{\text{eff}}$ in $\phi$ (second derivative strictly negative) guarantees uniqueness. This is clean.

**Comparative statics.** The claims $\partial\phi^*/\partial\lambda_0 > 0$ and $\partial\phi^*/\partial(r-\mu_L)^{-1} < 0$ follow from the implicit function theorem applied to the FOC, using the signs of the cross-partial derivatives. The argument is correct. However, the comparative static $\partial\phi^*/\partial\xi > 0$ (Corollary 1) is stated as "established numerically" rather than analytically, which is appropriate given the endogenous feedback.

### 3.2 Proposition 2 (Faith-based survival)

This is the paper's cleanest analytical result and the proof is correct. A few observations:

**The faith-based survival condition** (Equation 21) is:

$$\frac{(\phi_i K_i)^\alpha \cdot s_i^H}{r - \mu_H} \cdot (r - \mu_L) > [(1 - \phi_i)K_i]^\alpha \cdot s_i^L$$

The paper states that this holds for $\phi_i \gtrsim 0.15$ at the baseline. This threshold depends on all model parameters, and the paper should provide the formula for $\underline{\phi}$ explicitly (it can be solved from the condition with $s_i^L = s_i^H = 1/2$ for the symmetric duopoly case). This would make the result more portable and allow readers to assess the condition for alternative calibrations.

**Part (iii) on leverage-training substitution** is described as a "mechanical relationship" rather than a statement about optimality. This is appropriately cautious, but the paper could go further: is there any reason to believe that firms would move along this iso-$X_D$ locus in practice? If not, the result is an accounting identity rather than an economic prediction. The paper should either develop an economic story for when this substitution operates or downgrade the claim.

**Part (iv)** is straightforward (rival capacity reduces contest shares, raises default boundary). No issues.

### 3.3 Proposition 3 (Preemption equilibrium)

This is the paper's most complex result and the proof has both strengths and gaps.

**Part (i): Existence and uniqueness of $X_P$.** The proof follows the Huisman and Kort (2015) construction, which is appropriate. The argument that $L(0) < 0 < F(0)$ and $L(X_F^*) > F(X_F^*)$ establishes existence by the intermediate value theorem. However:

- The claim $L(X_F^*) > F(X_F^*)$ is justified by the assertion that "the leader's cumulative monopoly-phase profits exceed the follower's option value at the point of indifference." This is intuitive but not formally proved. A formal argument should show that the monopoly-phase revenue integral exceeds the follower's option value increment over $[X_P, X_F^*]$. This is likely straightforward but needs to be done.

- **Single crossing** is verified numerically rather than analytically. The paper provides a heuristic argument (leader value approximately affine, follower value convex on $(0, X_F^*)$) but acknowledges this is not a proof. For a top finance journal, this is the most significant analytical gap. The paper should either (a) provide conditions under which single crossing holds analytically (perhaps restricting to certain parameter regions), or (b) state clearly that uniqueness is a numerical finding and adjust the proposition statement accordingly. Currently, part (i) says the preemption trigger "exists and is unique under the standard conditions"—but the uniqueness relies on numerics, not on those standard conditions alone.

**Part (ii): $\phi_L^* \geq \phi_F^*$.** The qualitative argument is sound: the leader's marginal cost of training is lower during the monopoly phase because the contest share is 1. The dual penalty for the follower (direct capacity reduction plus contest share loss) is a nice observation. However, the result is "semi-analytical"—the inequality is verified numerically across calibration parameterizations. This is acceptable for a top journal if the paper is transparent about the scope of numerical verification (which it is in Table 2), but the paper should note that it has not identified parameter configurations where the inequality fails (or proved that none exist).

**Parts (iii)–(v)** are purely numerical findings. Part (v), that credit spreads are increasing in $\lambda_0$ at the preemption trigger, is economically interesting: firms that invest earlier due to optimism face higher credit risk. The appendix provides a plausible explanation (the trigger falls faster than the default boundary), but the lack of an analytical proof means this result is more fragile than the others.

### 3.4 Numerical Finding 2 (Asymmetric AI investment dilemma)

The three-channel decomposition (capacity, timing, training allocation) is useful for intuition. The argument that all three channels contribute $W''' < 0$ is heuristic but convincing. The key insight—that over-training sacrifices L-regime inference revenue needed for survival during the longer-than-expected pre-switch period—is novel relative to standard real options.

However, the paper does not provide the conditions under which the asymmetry holds. Is it possible for parameter configurations to reverse the asymmetry? The paper says "across all parameterizations tested" but does not characterize the boundary of the result. A sufficient condition for $W''' < 0$—even an approximate one—would strengthen the finding considerably.

### 3.5 Technical Issues in the Model

1. **Equation (7), $A_{\text{eff}}$:** The effective revenue coefficient treats the L-regime inference revenue and H-regime training revenue as additively separable. This is correct under the model's assumption that the firm's capacity allocation $\phi$ is fixed. But the notation $A_{\text{eff}}(\phi, K)$ makes $K$ appear as an argument, while in the single-firm case, $K$ enters only through $[(1-\phi)K]^\alpha$ and $(\phi K)^\alpha$. In the duopoly, $K$ also enters through the contest shares. The paper should be more explicit about when $A_{\text{eff}}$ depends on the rival's choices (Equation 18) versus only on the firm's own choices (Equation 7).

2. **The HJB equation (Equation 11):** The substitution of $F_H(X) = B_H X^{\beta_H}$ into the regime-switching term is standard. However, the paper should note explicitly that this assumes the firm has not yet invested in either regime—$F_H(X)$ is the H-regime *option* value, not the installed value. If the firm invests before the regime switch, the post-switch value is $V_H$ (installed), not $F_H$ (option). The current notation is consistent but could confuse readers who are thinking about the installed case.

3. **Condition (A3):** The no-investment-in-$L$ condition $(1 - 1/\beta_L^+)/\alpha \geq 1$ is crucial for the simplified option value $F_L = C \cdot X^{\beta_H}$ to apply. The paper verifies this for the baseline calibration ($\beta_L^+ \approx 1.63$, ratio $\approx 2.42$). But the sensitivity analysis varies parameters over wide ranges (e.g., $\alpha \in [0.20, 0.60]$ in Appendix B). At $\alpha = 0.60$, the ratio becomes $(1 - 1/1.63)/0.60 \approx 0.64 < 1$, violating (A3). The paper acknowledges this possibility (p. 12–13) but does not provide results for the full two-term solution. If the sensitivity analysis pushes into the (A3)-violating region, the numerical results in those regions may be incorrect (or at least require the two-term solution). This should be checked and discussed.

4. **Tullock contest specification:** The L-regime revenue (Equation 15) uses $[(1-\phi_i)K_i]^{2\alpha}$ in the numerator, not $[(1-\phi_i)K_i]^{\alpha}$. This means firm $i$'s revenue is $X \cdot s_i^L \cdot [(1-\phi_i)K_i]^\alpha$, where $s_i^L$ itself depends on $[(1-\phi_i)K_i]^\alpha$. The total industry revenue is therefore:

$$\sum_i \pi_i^L = X \cdot \frac{\sum_i [(1-\phi_i)K_i]^{2\alpha}}{\sum_j [(1-\phi_j)K_j]^\alpha}$$

which in the symmetric case reduces to $X \cdot K^\alpha$—the standard single-firm revenue. This is consistent and correct, but the non-standard exponent $2\alpha$ (rather than the usual $\alpha$ in the numerator with $\alpha$ in the denominator) should be noted. In particular, the Tullock specification has the property that total industry revenue increases when capacity becomes more asymmetric (the large firm captures disproportionately more). Is this a desirable feature for the AI setting? A brief discussion would be helpful.

5. **Static $\phi$ assumption:** Section 5.4 provides a useful discussion of the direction of bias. The argument that the static model overstates $\phi^*$ (because the option to reallocate later means the firm can start with more inference) is correct and important. However, the claim that "implied $\lambda$ would therefore be higher under the dynamic model" is an implication for the revealed beliefs exercise, not for the model's predictions. The paper should separate these two statements more clearly.

---

## 4. Calibration

### Strengths

The calibration is appropriately described as "stylized" and the paper is transparent about which parameters are directly observed, inferred, or chosen for discipline (Table 3). The firm archetypes are plausible composites, and the paper correctly uses sector-specific revenue for Google (Google Cloud, not Alphabet total).

### Issues

1. **$\eta = 0.07$ as a "directly observed" scaling law exponent.** The Kaplan et al. (2020) and Hoffmann et al. (2022) papers report scaling exponents for model *loss* as a function of training compute—not for the arrival rate of AGI. The mapping from "doubling compute reduces loss by $X$%" to "doubling compute raises the probability of regime switch by $Y$%" is not straightforward and involves substantial assumptions about what constitutes a "regime switch." Calling this parameter "directly observed" overstates the empirical grounding. I would recommend reclassifying $\eta$ as "inferred" and discussing the mapping from scaling laws to arrival rates more carefully. This is probably the calibration's weakest link.

2. **$\alpha = 0.40$ and $\gamma = 1.50$** are both "inferred" or "chosen for discipline" but play central roles in the results (Table 7 shows them among the highest-elasticity parameters). The paper should provide more discussion of alternative values and how the results change. For example, $\alpha = 0.40$ implies substantial diminishing returns—but in a winner-take-most market (which the Tullock specification allows), higher $\alpha$ might be more appropriate.

3. **The baseline $\lambda_0 = 0.05$ with total $\lambda = 0.10$** implies an expected time to regime switch of 10 years—roughly 2035. This is a "moderate prior" as stated, but it is significantly more pessimistic than the beliefs attributed to Amodei ($\lambda \approx 0.30$–$0.50$) or Hassabis ($\lambda \approx 0.10$–$0.15$). The paper should discuss whether the baseline is meant to represent the marginal investor's belief, the median belief, or the author's belief.

4. **WACC variation** across archetypes (0.10–0.18) is appropriate given the firm heterogeneity. However, the paper uses $r = 0.12$ for all analytical results and figures in Section 2, then introduces firm-specific WACCs in Section 4. This creates an inconsistency: the propositions are proved at $r = 0.12$, but the quantitative implications use different discount rates. The paper should verify that Assumptions (A1)–(A3) hold at all four archetype WACCs.

5. **Training fractions** $\hat{\phi}$ in Table 4 are described as "estimated from industry reports" but no specific sources are cited. These are crucial inputs: they are the moments that a revealed-beliefs exercise would use for identification. The paper should provide more detail on how these estimates were constructed and discuss their uncertainty.

---

## 5. Presentation and Exposition

### Strengths

The paper is exceptionally well-written for a technical theory paper. The figures are clear and well-designed. The use of executive quotes to motivate model features is effective without being excessive. Table 2 (analytical status of results) is a model of transparency that more theory papers should emulate.

### Suggestions

1. **Length.** At 58 pages (including appendices), the paper is long. The N-firm extension (Appendix C) and several robustness discussions (Appendix F) could be shortened without loss. The proofs in Appendix A are thorough but could be condensed by referencing standard results more aggressively.

2. **Figure 1** is a nice illustration of the demand environment but adds limited economic content. It could be moved to the appendix or combined with Figure 2.

3. **Section 4 (Quantitative Implications)** mixes several distinct analyses. The growth option decomposition, credit risk analysis, and AI investment dilemma could each be separate subsections with clearer motivation. Currently, the section reads as a collection of numerical exercises rather than a unified quantitative story.

4. **The "revealed beliefs" methodology** is mentioned in the conclusion as future work but is essentially what Section 4.3 already does (inverting the model to understand what beliefs rationalize observed investment). The paper should either develop this formally or remove the suggestion that it is future work.

5. **Notation.** The paper uses $\tilde{\lambda}$ for the effective arrival rate and $\lambda_0$ for the exogenous component, but several places in the text just write $\lambda$ without the tilde. A consistency pass is needed.

---

## 6. Minor Issues

- p. 2: "purpose-built GPU clusters housed in multi-billion-dollar data centers" appears nearly verbatim twice (here and p. 7). Remove one instance.
- p. 6, Equation (2): The notation $\tilde{\lambda}(\phi_i, K_i, \phi_j, K_j)$ lists firm-level arguments, but when $\xi = 0$, these arguments are irrelevant. Consider writing the endogenous case separately.
- p. 9, Table 1: "Derived" is used for both $A_H$ (which is a simple function of parameters) and $s_i^L$ (which depends on endogenous choices). A finer classification would help.
- p. 12, Assumption 1(A2): The condition $1/\gamma < (\beta_H - 1)/(\alpha\beta_H) < 1$ should be connected to economic primitives. What does it mean for this to fail? The paper says it ensures an interior capacity solution, but a one-sentence economic interpretation would help.
- p. 15, Equation (14): The trigger formula uses $A_{\text{eff}}(\phi^*, K^*)$ which itself depends on the trigger through the optimal $(K^*, \phi^*)$. The paper should note that this is an implicit equation, not a closed-form expression.
- p. 28, Table 4: The "Revenue 2024" and "Revenue 2025" figures for the Anthropic-like archetype ($0.9B and $3.0B) are plausible but hard to verify given Anthropic is private. The paper should note this caveat.
- p. 34, Section 4.2.1: The credit spread formula uses $r_f$ (risk-free rate), which appears nowhere else in the paper. The relationship between $r_f$ and $r$ (WACC) should be stated.
- p. 50, Appendix B: "SciPy optimization routines in Python 3.13"—as of the paper's date, this is current, but specifying the SciPy version would aid reproducibility.

---

## 7. Requested Revisions (Summary)

### Major

1. **Resolve the (A3) boundary issue.** Verify that all numerical results in the sensitivity analysis respect condition (A3), or provide the two-term solution for parameter regions where (A3) fails. This is especially important for high-$\alpha$ cases.

2. **Strengthen the single-crossing argument** for Proposition 3(i). Either provide analytical conditions or clearly demote uniqueness to a numerical finding.

3. **Reclassify $\eta$ as "inferred"** and provide a substantive discussion of the mapping from neural scaling law exponents to the arrival rate of AGI. This is a novel mapping that deserves more than a sentence.

4. **Provide the explicit threshold $\underline{\phi}$** for the faith-based survival condition in closed form (at least for the symmetric duopoly case).

5. **Check the Tullock specification's implications** for total industry revenue under asymmetric capacity. Discuss whether the property that asymmetry increases total revenue is desirable.

### Minor

6. Consistency pass on $\lambda$ vs. $\tilde{\lambda}$ notation.
7. Clarify that the Proposition 1 capacity formula is conditional on $\phi$, not the joint optimum.
8. Discuss the training fraction estimates more thoroughly and cite specific sources.
9. Verify Assumptions (A1)–(A3) hold at all four archetype-specific WACCs.
10. Condense Appendices C and F.

---

## 8. Overall Assessment

This is a strong paper that addresses a first-order economic question with a well-constructed theoretical framework. The training-inference allocation is a genuine innovation in the real options literature, and the faith-based survival mechanism is both novel and economically compelling. The paper is unusually well-written and transparent about the analytical status of its results.

The main concerns are (a) several analytical gaps in the proofs that should be tightened for a top journal, (b) the calibration of the scaling law exponent $\eta$, which is the paper's most important empirical input but is less well-grounded than claimed, and (c) some parameter regions in the sensitivity analysis that may violate the maintained assumptions.

Conditional on addressing these issues, the paper makes a sufficient contribution for a top finance journal. The topic is timely, the model is novel, and the economic insights—particularly the faith-based survival mechanism and the asymmetric AI investment dilemma—will be of broad interest to the finance and economics communities.
