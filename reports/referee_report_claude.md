# Referee Report

**Manuscript:** "Investing in Intelligence: A Real Options Framework for AI Compute Infrastructure"

**Recommendation:** Revise and Resubmit (Major Revision)

---

## Summary

This paper develops a real options model of irreversible capacity investment tailored to the AI infrastructure sector. It combines six ingredients: regime-switching demand (low → high, Poisson arrival), oligopoly competition via a Tullock contest, endogenous default risk à la Leland (1994), diminishing returns calibrated to neural scaling laws, a training-inference compute allocation, and a "revealed beliefs" methodology that inverts the model to extract firms' private beliefs about the arrival rate of transformative AI. The model is calibrated to stylized versions of Anthropic, OpenAI, Google DeepMind, and CoreWeave. The paper introduces the "Dario dilemma"—an asymmetry in the cost of belief mismatches whereby overinvestment is more costly than underinvestment of equal magnitude.

The paper addresses a timely and economically important question. The combination of building blocks is sensible for the application, and the revealed beliefs methodology is a creative contribution. However, several issues—ranging from errors in the proofs, to fragility of the identification strategy, to incomplete integration of the model's components—need to be addressed before the paper is suitable for publication at a top finance journal.

---

## Major Comments

### 1. Error in the Proof of Proposition 1

The proof of Proposition 1 (Appendix A) contains an algebraic error that propagates into the statement of the proposition itself.

The proof correctly derives that the NPV at the trigger is:

$$V_H(X^*, K) - I(K) = \frac{\beta_H}{\beta_H - 1}\left(cK^\gamma + \frac{\delta K}{r}\right) - \frac{\delta K}{r} - cK^\gamma.$$

Simplifying, this yields:

$$V - I = \frac{1}{\beta_H - 1}\left(cK^\gamma + \frac{\delta K}{r}\right).$$

However, the proof instead claims:

$$V - I = \frac{1}{\beta_H - 1}\left(cK^\gamma + \frac{\delta K}{r}\right) - \frac{\delta K}{r} = \frac{cK^\gamma}{\beta_H - 1} - \frac{(\beta_H - 2)\delta K}{r(\beta_H - 1)}.$$

The spurious $-\delta K / r$ term has no justification—it appears to double-count the maintenance cost. The correct simplification is simply $\frac{1}{\beta_H - 1}(cK^\gamma + \delta K/r)$.

More importantly, the optimization problem is not to maximize $V - I$ at the trigger, but to maximize the option value at the current demand level:

$$F_H(X_0) = (V - I) \cdot \left(\frac{X_0}{X^*(K)}\right)^{\beta_H},$$

where $X^*(K)$ is itself a function of $K$. The first-order condition for $K$ from this full problem is more complex than what is presented in the appendix. Specifically, maximizing $h(K) = K^{\alpha \beta_H} / (cK^\gamma + \delta K/r)^{\beta_H - 1}$ yields:

$$\alpha \beta_H (cK^\gamma + \delta K/r) = (\beta_H - 1)(c\gamma K^\gamma + \delta K/r),$$

which is an implicit equation in $K$. The expression in Proposition 1 also has $K$ appearing on both sides (the $K^{1-\gamma}$ term on the right-hand side), so it is an implicit characterization rather than a closed-form solution. While the proposition text says $K_H^*$ "satisfies" this equation, the presentation and the proof are misleading. The author should either (a) present the correct implicit first-order condition and solve it numerically, clearly stating so, or (b) derive the correct closed-form in the special case $\delta = 0$ and treat general $\delta > 0$ numerically.

The comparative statics stated in the proposition (e.g., $K_H^*$ increasing in $\mu_H$, decreasing in $c$, $\gamma$, and $\delta$) may well be correct, but since they are derived from the incorrect FOC, they need to be re-verified from the corrected expression.

### 2. Fragility of the Revealed Beliefs Identification

The revealed beliefs methodology is the paper's most novel contribution, but Table 5 reveals a fundamental identification problem. When $\sigma_H$ is varied by ±25% from its baseline of 0.30 (i.e., over the range [0.225, 0.375]), the implied $\hat{\lambda}$ for the Anthropic-like firm ranges from **0.003 to 0.90**—essentially spanning the entire economically meaningful parameter space. This means the headline result (Anthropic invests as if transformative AI arrives in ~1 year) is almost entirely determined by the calibration of $\sigma_H$, a parameter that is itself very difficult to pin down empirically.

This fragility undermines the paper's central claim that investment behavior reveals private beliefs about AI timelines. What it reveals, instead, is a joint function of beliefs and hard-to-observe demand volatility. The author should:

- Discuss this fragility prominently, not just in an appendix table. Currently the text says "reasonable variation in calibration parameters produces bounded changes in implied $\hat{\lambda}$," which is contradicted by the paper's own Table 5.
- Explore whether any observable moments (e.g., option-implied volatility of cloud computing firms, quarterly revenue variance) can discipline $\sigma_H$ more tightly.
- Consider presenting results as confidence sets for $\hat{\lambda}$ conditional on plausible ranges for $\sigma_H$, rather than point estimates.
- Acknowledge that the identification assumption—that cross-firm variation in investment intensity reflects variation in $\lambda$ rather than unobserved cost or technology heterogeneity—is strong and essentially untestable in the current framework.

### 3. Incomplete Integration of the Training-Inference Allocation

The training-inference allocation (Section 3.2) is presented as a distinctive feature of the model, but it is surprisingly disconnected from the rest of the analysis. Proposition 5 shows that the optimal training fraction $\phi^* = \eta / (\alpha + \eta)$ is a constant, independent of demand $X$, capacity $K$, and the regime. This means the allocation decision is completely separable from the investment timing and capacity choice problems—it simply rescales the revenue function by a constant multiplicative factor.

As a result, the training-inference allocation does not interact with any of the other model features (regime switching, competition, default risk). It does not affect investment triggers, it does not change with the state of the world, and it generates no interesting dynamics. The first-mover advantage through quality accumulation (Section 3.2.3) is mentioned but never analyzed formally or used in the calibration.

The author should either:

- Enrich the training-inference allocation so it genuinely interacts with the other model components (e.g., make $\eta$ or $A$ state-dependent, allow the allocation to shift between regimes, or model inference-time scaling as in Brown 2024), or
- Downgrade its prominence in the paper, acknowledging that it enters as a multiplicative constant and does not generate novel economic forces beyond those already present in the base model.

### 4. The Dario Dilemma: Proof and Economic Content

Proposition 6 claims an asymmetry in the cost of belief mismatches but the proof is qualitative rather than rigorous. The Taylor expansion argument asserts that $V''(\lambda) > 0$ for overinvestment and "smaller" for underinvestment, but provides no formal derivation. The statement "the aggressive case compounds two sources of loss (timing + capacity + default risk) while the conservative case involves only timing loss" is economic intuition, not a proof.

Several issues:

- The claim that underinvestment involves "only timing loss" is not obviously correct. A firm that builds too little capacity also suffers from suboptimal scale. The proof needs to formalize why the capacity distortion is larger for overinvestment than for underinvestment.
- The role of leverage in amplifying the asymmetry is asserted but not derived. A rigorous proof should show, for example, that $\partial^2 \Delta V / \partial \lambda_{\text{invest}}^2$ is larger for $\lambda_{\text{invest}} > \lambda_{\text{true}}$ than for $\lambda_{\text{invest}} < \lambda_{\text{true}}$.
- The proof should also clarify what is being held fixed. If a firm invests according to $\lambda_{\text{invest}}$, does it also choose leverage according to $\lambda_{\text{invest}}$? The interaction between belief errors and leverage choice is central to the dilemma but is not formalized.

I would suggest either providing a rigorous proof (even if only for a special case, e.g., $\delta = 0$, zero leverage) or relabeling the result as a numerical finding documented by simulation.

### 5. Stylized Calibration and Empirical Content

The calibration uses "stylized firms" with round-number parameters that are "composites designed to capture the key features of each firm category." While I appreciate the transparency, this approach limits the paper's empirical contribution. The revealed beliefs results (Table 2) are driven by the CapEx/Revenue ratio alone—a single moment per firm. With only one moment to match, the inversion is mechanically determined once the other parameters are fixed.

Several concerns:

- The CapEx/Revenue ratios for the Anthropic-like and CoreWeave-like firms are identical (2.00), yet these firms have very different financial structures (leverage 0.20 vs. 0.70) and cost of capital (0.15 vs. 0.18). The model produces identical $\hat{\lambda} = 0.90$ for both. This raises the question: does the model fail to distinguish between equity-financed optimism and debt-financed speculation? If so, this is a significant limitation for the "revealed beliefs" interpretation.
- The paper targets CapEx/Revenue but does not verify whether the model simultaneously matches other observable moments (e.g., market capitalization, credit spreads, revenue growth). A model that matches one ratio but misses others provides weak identification.
- Moving from "stylized" to actual firm data would substantially strengthen the paper. Even if exact calibration is difficult, using actual CapEx and revenue figures rather than round numbers would increase credibility.

### 6. Equity Value Formula (Section 2.4.3)

The equity value expression includes a term $-(1 - \ell)I(K)$ that subtracts the equity contribution at investment. This conflates two distinct objects: the going-concern equity value (used in the default boundary derivation) and the NPV of equity to an investor at the time of investment. The Leland (1994) framework values equity as the present value of cash flows to equity holders conditional on the firm being a going concern minus the default option transfer to debt holders. The initial equity contribution should not appear in the going-concern equity value—it is a sunk cost at the time of valuation.

Please clarify whether $E(X)$ represents the going-concern value or the NPV of equity investment, and ensure consistency with the default boundary derivation, which requires the going-concern formulation.

---

## Minor Comments

### Literature

1. The literature review is comprehensive—perhaps too comprehensive for a journal article. At nearly 4 pages, it reads more like a handbook chapter survey. I would suggest condensing it to roughly half its current length, focusing on the papers that are directly used as building blocks (Huisman and Kort 2015, Leland 1994, Guo, Miao, and Morellec 2005, Grenadier 2002, Bouis et al. 2009) and the closest competitors, with the remaining citations moved to footnotes or a brief "other related work" paragraph.

2. The scaling laws literature (Kaplan et al. 2020, Hoffmann et al. 2022) is well cited, but the paper would benefit from also citing the growing economics literature on AI specifically. For example, Korinek and Suh (2024, "Scenarios for the Transition to AGI") model scenarios for transformative AI in a macro framework. Traina (2024) studies the industrial organization of AI. Acemoglu (2024, "The Simple Macroeconomics of AI") provides a skeptical take on transformative AI that is directly relevant to the low-$\lambda$ interpretation. These papers offer alternative frameworks for thinking about the demand regime switch that is central to the model.

3. The connection to the "ideas getting harder to find" literature (Bloom et al. 2020) is well drawn. Consider also citing Jones (2024, "The AI Dilemma") which explicitly connects AI scaling laws to the semi-endogenous growth framework.

4. The reference to Novy-Marx (2011) on operating leverage and the cross-section of returns would strengthen the asset pricing discussion in Section 5.2, since the growth option decomposition has direct implications for systematic risk.

### Model and Proofs

5. **Proposition 3, part (iv):** The claim that "the credit spread at the preemption trigger is increasing in $\lambda$" is stated without proof. Since the preemption trigger itself depends on $\lambda$ in a complex way, this comparative static is not obvious and should be derived or verified numerically.

6. **Proposition 4, part (iii):** The proof acknowledges that total industry capacity increasing in $N$ is verified only numerically. For a proposition in a theory paper, this is unsatisfying. Consider either providing conditions under which the result holds analytically, or moving it to a "Numerical Result" or "Observation" to distinguish it from the proven claims.

7. **Equation (6):** The term $\lambda F_H(X)$ in the ODE for $F_L$ should be stated more carefully. For $X < X_H^*$, $F_H(X)$ is the option value (equation 3); for $X \geq X_H^*$, $F_H(X) = V_H(X, K_H^*) - I(K_H^*)$. The boundary between these cases matters for the solution and should be discussed.

8. **Remark 1** notes that the net effect of $\lambda$ on the trigger depends on parameters. It would be useful to provide conditions (or a numerical boundary in parameter space) under which each effect dominates, since this is central to the paper's economic message.

9. The $N$-firm model (Section 3.1) uses "iterative refinement" (fixed-point iteration) rather than the backward induction described in the text. These are different solution concepts. Backward induction solves the game by working from the last entrant backward and yields a subgame perfect equilibrium. Iterative refinement is a computational technique that may or may not converge to the equilibrium. The paper should clarify the relationship: is iterative refinement being used to solve the backward induction problem, or is it a different equilibrium concept?

### Calibration and Results

10. The discount rate $r = 0.12$ is described as a WACC, but the firm-specific WACCs in Table 1 range from 0.10 to 0.18. Are the analytical results in Sections 2–3 computed at $r = 0.12$ while the calibration uses firm-specific rates? If so, the analytical figures (e.g., $X_H^* \approx 0.49$) do not directly correspond to any firm in the calibration. Please clarify.

11. The depreciation rate $\delta = 0.03$ is described as "distinct from accounting depreciation of GPU hardware (which is faster)." Given that Nvidia releases new architectures every 18–24 months and the paper itself notes that "algorithmic breakthroughs can devalue installed capacity overnight," $\delta = 0.03$ seems low. A depreciation rate corresponding to a 5-year useful life would be $\delta \approx 0.20$. Even if $\delta$ represents only operating costs (power, cooling, personnel), 3% of capacity per year seems an underestimate for facilities that consume hundreds of megawatts of power. The sensitivity to $\delta$ should be explored more thoroughly.

12. Figure 7(b) shows Google/Alphabet-like as a low-leverage, moderate-growth firm. But Google's AI revenue growth has been driven primarily by its cloud division, which has been growing at 25-35% annually. The 1.375x revenue growth multiple (implying ~37.5% growth) may understate the growth of Google's AI-specific operations. Consider discussing whether the relevant "revenue" for the model is total company revenue or AI-specific revenue.

13. The $\hat{\lambda}$ values in Table 2 are derived from a static model, but the firms' investment decisions are sequential and dynamic. A firm that spent $6B in 2025 may have had a different $\hat{\lambda}$ in 2024 when it committed the capital. The paper should discuss the timing of information and commitment more carefully.

### Presentation

14. The abstract promises "semi-analytical characterization" but many of the key results (N-firm equilibrium, revealed beliefs inversion) are fully numerical. I would suggest toning down the "analytical" claims and being more precise about what is closed-form versus computed numerically.

15. Figure 1 uses a log scale for the y-axis, which makes the regime switch visually less dramatic than it actually is. Consider adding a linear-scale version, or at least noting that the visual impression understates the magnitude of the demand shift.

16. The term "Dario dilemma" is catchy but could be seen as pejorative or personal. Since the paper names a specific living executive, consider whether "AI investment dilemma" or "timeline belief dilemma" might be more appropriate for a journal publication. At minimum, ensure that Dario Amodei is comfortable with his name being attached to a "dilemma" that implies potential irrationality.

17. Several important limitations (Section 6.4) could be mentioned earlier. In particular, the absence of dynamic rebalancing and the fixed capacity assumption are strong restrictions that affect the interpretation of all results. Flagging these up front, rather than in a limitations section, would help readers evaluate the results as they encounter them.

18. The paper refers to a "Tullock contest for AI compute market share" in the abstract, but the Tullock function as specified (Equation 8) determines revenue sharing, not market share in the traditional sense. With $\alpha < 1$, the contest function $s_i = K_i^\alpha / (K_i^\alpha + K_j^\alpha)$ maps capacity ratios into revenue shares through a concave transformation. The language should be precise about what the contest governs.

---

## Summary Assessment

This paper tackles an important and timely question with a well-constructed theoretical framework. The core model—combining real options, regime switching, oligopoly, and default risk—is appropriate for the application and represents a genuine contribution to the real options literature. The revealed beliefs methodology is creative and, if the identification issues can be addressed, could become a useful tool for extracting private information from corporate investment decisions.

However, the paper currently falls short of the standards required for a top finance journal on several dimensions. The proof of Proposition 1 contains an error. The revealed beliefs identification is fragile to calibration assumptions in a way the text does not adequately acknowledge. The training-inference allocation, presented as a key feature, does not interact with the rest of the model. The Dario dilemma proof is informal. And the calibration, while transparent, is too stylized to deliver convincing quantitative conclusions.

A successful revision would: (i) correct the proofs, (ii) honestly assess the identification challenges and either tighten identification through additional moments or present results as conditional on calibration assumptions, (iii) either integrate the training-inference allocation into the investment game or reduce its prominence, and (iv) move toward actual firm data for the calibration. With these revisions, the paper has the potential to make a solid contribution.
