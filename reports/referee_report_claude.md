# Referee Report

## Manuscript: "Investing in Artificial General Intelligence"

**Recommendation: Revise and Resubmit (Major Revision)**

---

## 1. Summary

This paper develops a continuous-time model of irreversible capacity investment by frontier AI laboratories racing to develop Artificial General Intelligence. Firms choose when to invest, how much compute capacity to build, and how to allocate it between model training (which builds capabilities and endogenously accelerates a regime switch to high demand) and inference serving (which generates current revenue). The framework combines real options (McDonald and Siegel, 1986; Dixit and Pindyck, 1994), regime switching (Guo, Miao, and Morellec, 2005), oligopoly competition via Tullock contests (Grenadier, 2002; Huisman and Kort, 2015), endogenous default risk (Leland, 1994), and diminishing returns calibrated to neural scaling laws. The main results include: (i) closed-form and semi-analytical investment triggers in a duopoly with training allocation and default risk; (ii) a "faith-based survival" mechanism whereby optimism about AGI, backed by training investment, lowers the endogenous default boundary; (iii) an illustrative "revealed beliefs" methodology that inverts the model to extract implied AGI timeline beliefs from observable investment decisions using two moments (CapEx/Revenue and training fraction); and (iv) an asymmetric "AI investment dilemma" in which aggressive overinvestment carries higher downside risk than conservative underinvestment.

---

## 2. Assessment of the Contribution

### Strengths

The paper tackles an extraordinarily timely and economically significant topic. The amounts being deployed—over $200 billion per year by leading firms—make the AI infrastructure race arguably the most important capital allocation event of the decade, yet formal structural models of these investment decisions are essentially absent from the finance literature. The paper fills a genuine gap.

The central innovation—placing the training-inference allocation at the heart of the real options problem—is well motivated and economically compelling. This allocation has no close analog in the standard real options literature: training builds option value for a post-AGI regime while inference generates cash flows needed to survive, and the tension between these two uses of scarce compute is the defining operational challenge facing frontier labs. Embedding this within an endogenous regime-switching framework where aggregate training accelerates the arrival of transformative AI is a natural and elegant modeling choice.

The "faith-based survival" mechanism (Proposition 2) is the paper's most novel theoretical contribution. The idea that optimism about AGI, when backed by training investment, lowers the default boundary through the effective revenue coefficient $A_{\text{eff}}$ is both mechanically clean and economically insightful. It provides a structural explanation for why highly levered AI firms can sustain valuations that appear disconnected from current cash flows—an observation that has puzzled market commentators.

The revealed beliefs methodology, while appropriately labeled "illustrative," represents a creative application of revealed preference theory to a setting where stated beliefs are noisy and potentially strategic. The use of the training fraction as a second identifying moment beyond CapEx/Revenue is a good insight—as demonstrated by the Anthropic-like vs. CoreWeave-like comparison in Table 2, where identical investment intensity maps to very different implied beliefs once training allocation is considered.

The writing is clear and well-organized throughout. The paper does a commendable job of connecting the formal model to real-world executive statements (Amodei, Pichai, Huang), grounding the abstractions in observable behavior.

### Concerns About the Contribution

While the paper assembles an impressive number of ingredients—real options, regime switching, Tullock contests, Leland default, scaling laws, endogenous arrival rates—the integration is at times more additive than synergistic. Many of the individual results (the option premium $\beta_H/(\beta_H - 1)$, the preemption trigger lying below the monopolist trigger, the convexity of credit spreads in leverage) are standard in the constituent literatures. The paper should be more precise about which results are genuinely new versus which are known results applied to a new setting. For instance, the comparative statics in Figure 3 are standard real options results; what is new is the training-allocation dimension and the faith-based survival mechanism. I would recommend reorganizing Section 2 to move more quickly to the novel elements and relegate the standard results to remarks or brief discussion.

The gap between the theoretical model and the empirical application is a concern. The model is a stylized structural framework with many free parameters, and the "revealed beliefs" exercise is a calibration, not an estimation. The paper is admirably transparent about this (Section 5.1.2), but the distinction matters because the headline numbers in Table 2 (e.g., $\hat{\lambda} = 0.90$ for the Anthropic-like archetype) may be taken at face value by readers. The extreme sensitivity of $\hat{\lambda}$ to $\sigma_H$ shown in Table 5—ranging from 0.003 to 0.90 under $\pm 25\%$ variation—substantially undermines the quantitative content of the calibration. A 300-fold range in implied beliefs from a single parameter perturbation is not a confidence set; it is near-non-identification.

---

## 3. Literature Review

The literature review is comprehensive and well-organized, covering the relevant building blocks from real options, strategic investment, structural credit risk, technology adoption, and the economics of AI. I have several specific suggestions.

**Missing or underemphasized references:**

1. The paper should engage more with the literature on investment under learning and Bayesian updating. Décamps, Mariotti, and Villeneuve (2005, "Investment Timing under Incomplete Information," *Mathematics of Operations Research*) and Lambrecht and Perraudin (2003, "Real Options and Preemption under Incomplete Information," *JFQA*) study how firms update beliefs about demand in real time. These are directly relevant because in practice, AI labs continually update their beliefs about $\lambda$ as new capability demonstrations occur, and the static-beliefs assumption in the current model is among its strongest limitations.

2. The connection to the capacity investment under uncertainty literature beyond Pindyck (1988) could be strengthened. Dangl (1999, "Investment and Capacity Choice under Uncertain Demand," *European Journal of Operational Research*) and Huisman and Kort (2015) are cited, but Bar-Ilan and Strange (1998, "A Model of Sequential Investment," *Journal of Economic Dynamics and Control*) on incremental investment and Abel and Eberly (1996, "Optimal Investment with Costly Reversibility," *Review of Economic Studies*) on irreversibility deserve mention given the paper's emphasis on the lumpiness of AI investment.

3. On the AI economics side, the paper cites Acemoglu (2024) and Korinek (2024) but does not engage with Traina (2024, "Computers and the Decline in Manufacturing Investment," *JF*) on how computing capital differs from traditional capital goods, which is relevant to the $I(K) = cK^\gamma$ specification. Tambe, Hitt, Rock, and Brynjolfsson (2020) on complementary investments in AI would also strengthen the discussion of the operating cost parameter $\delta$.

4. The endogenous default literature has grown significantly since Leland (1994). The paper cites Hackbarth, Mathews, and Robinson (2014) and Kumar and Yerramilli (2018), but Morellec (2004, "Can Managerial Discretion Explain Observed Leverage Ratios?," *RFS*) on endogenous investment and capital structure and Strebulaev (2007, "Do Tests of Capital Structure Theory Mean What They Say?," *JF*) on dynamic capital structure would provide useful context for the leverage-training substitution result.

**Positioning relative to closest papers:**

The paper correctly identifies Huisman and Kort (2015) as the closest strategic investment model and Kumar and Yerramilli (2018) as the closest investment-default model. The paper should be more explicit about the formal extensions relative to each. A comparison table showing which features each paper includes (capacity choice, training allocation, regime switching, endogenous arrival, default risk, $N$-firm, contest competition) would be efficient and clarify the incremental contribution.

---

## 4. Model Review

### 4.1 Environment and Technology (Sections 2.1–2.2)

**The demand specification is standard and appropriate.** GBM with regime-dependent drift and volatility, plus absorbing Poisson regime switch, is well-suited to the binary uncertainty about transformative AI. The absorbing assumption (no "AI winter") is a limitation the paper acknowledges but should discuss more carefully. The possibility of reversal—a period of exuberance followed by disappointment, as occurred in prior technology cycles—would change the analysis significantly by reducing the value of training and increasing the default risk of highly levered firms. Even a brief formal extension showing how a non-absorbing $H$-regime (with reversion rate $\lambda'$ back to $L$) would affect the faith-based survival mechanism would strengthen the paper.

**The endogenous arrival rate (Equation 2) is novel but raises questions.**

First, the functional form $\tilde{\lambda} = \lambda_0 + \xi \cdot [(\phi_i K_i)^\eta + (\phi_j K_j)^\eta]$ assumes additivity across firms—training compute contributions are separable. In practice, there are strong complementarities (e.g., open-source model releases that enable others to build upon) and substitutabilities (duplicative training runs on similar data). The additive form is a natural starting point, but the paper should discuss how alternative aggregation (e.g., $[\sum (\phi_j K_j)]^\eta$ with industry-level diminishing returns versus firm-level diminishing returns) would change the externality and welfare results.

Second, with $\eta = 0.07$, the contribution of any individual firm's training to $\tilde{\lambda}$ is extremely flat. Doubling training compute raises the firm's contribution by only 5%. This means the endogenous channel is quantitatively weak for realistic parameter values, and the model effectively reduces to the exogenous-$\lambda$ case for most purposes. The paper should be upfront about this: is the endogenous channel meant to be a quantitatively important mechanism or a qualitative illustration of the externality?

**The training-inference allocation (Section 2.2.1) is the key innovation but the timing assumption warrants more discussion.** The paper assumes $\phi$ is chosen at investment time and fixed thereafter. The justification (18–24 month planning horizons, GPU architecture choices) is reasonable for the initial allocation but increasingly strained as the firm operates: in practice, firms dynamically reallocate GPUs between training and inference on timescales of weeks. The paper acknowledges this limitation in Section 6.4 but should provide intuition for the direction of bias. If dynamic reallocation were allowed, would the initial $\phi^*$ be higher or lower? I conjecture it would be lower (firms can start with more inference and shift to training as signals about the regime switch arrive), which would affect the revealed beliefs calibration.

**The revenue specification deserves scrutiny.** In the L-regime, revenue is $\pi^L_i = X \cdot [(1 - \phi_i)K_i]^\alpha$ (single firm) or the Tullock form (duopoly). In the H-regime, revenue is $\pi^H_i = X \cdot (\phi_i K_i)^\alpha$. This assumes a clean switch: today only inference matters, post-AGI only training quality matters. In reality, the transition is likely gradual, with the relative importance of training versus inference shifting smoothly. A mixing parameter $\theta(t) \in [0, 1]$ that transitions from L-type to H-type revenue over time (rather than a binary switch) would be more realistic and would modify the sharp knife-edge results about $\phi^*$.

### 4.2 Single-Firm Benchmark (Section 2.3)

**Proposition 1 (Optimal capacity and training fraction):** The proof in Appendix A is correct and well-structured. I have verified the key steps:

- Step 1 (optimal trigger given $(K, \phi)$): Standard value-matching and smooth-pasting. Correct.
- Step 2 (NPV at trigger): Uses the standard result that NPV at the optimal trigger is $b(K)/(\beta_H - 1)$. Correct.
- Step 3 (joint optimization): The proportionality $F(X_0) \propto A_{\text{eff}}(\phi, K)^{\beta_H} / b(K)^{\beta_H - 1}$ follows from substituting the trigger into the option value. Correct.
- Step 4 (FOC for $K$, Equation 23): I have verified the logarithmic differentiation. The existence condition $1/\gamma < (\beta_H - 1)/(\alpha \beta_H) < 1$ ensures the interior solution for capacity, balancing marginal cost convexity against marginal revenue concavity. Correct.
- Step 5 (interior $\phi^*$): The Inada-condition argument is clean. With $\alpha \in (0,1)$, both boundary derivatives diverge as claimed. Strict concavity of $A_{\text{eff}}$ in $\phi$ follows from $\alpha(\alpha - 1) < 0$ and both bracketed terms being positive. This is the most elegant piece of the proof.
- Step 6 (comparative statics): These follow directly from the implicit function theorem. The signs are correct.

**One issue in the H-regime capacity formula:** The expression $K^* = [\cdots]^{1/(\gamma-1)} \cdot \phi^{-\alpha/(\gamma-1)}$ shows that $K^* \to \infty$ as $\phi \to 0$. This is technically correct (if you allocate nothing to training, you need infinite capacity to generate H-regime revenue from training quality, which is zero regardless of $K$)—but the formula is meaningless at $\phi = 0$. The paper should note explicitly that this closed form applies only for $\phi > 0$ and that the joint optimization over $(K, \phi)$ ensures $\phi^* > 0$, preventing the degeneracy.

**The simplified option value $F_L = C \cdot X^{\beta_H}$ (Section 2.3.3):** The condition for this simplification—$(1 - 1/\beta^+_L)/\alpha \geq 1$—is verified for the baseline calibration. However, several of the comparative statics exercises in later sections vary parameters (particularly $\alpha$ and $\sigma_L$) over ranges where this condition may fail. The paper should either: (a) verify the condition holds for all parameter values used in the figures and tables, or (b) use the full two-term solution (Equation 13) throughout. As written, it is unclear whether Figures 3–4 and Tables 4–5 use the simplified or full solution, and whether results could change under the full solution.

### 4.3 Duopoly with Default Risk (Section 2.4)

**Proposition 2 (Endogenous default with faith-based survival):** The proof is largely correct, but Part (ii) requires a sufficient condition ($R_H > R_L$) that is not always satisfied. This is acknowledged in the proof text but deserves more prominence. Specifically:

- When $\phi$ is low (mostly inference), $R_H$ can be small relative to $R_L$, and $\partial A_{\text{eff}}/\partial \tilde{\lambda}$ could be negative—meaning higher $\tilde{\lambda}$ could *raise* the default boundary. This would reverse the faith-based survival mechanism for inference-heavy firms.
- The paper should state explicitly the parameter region where faith-based survival holds, ideally as a closed-form condition on $\phi$ (e.g., $\phi > \underline{\phi}(\mu_L, \mu_H, r, s^L, s^H)$). This is important for the CoreWeave-like archetype ($\hat{\phi} = 0.20$), which may or may not satisfy the condition.

**Part (iii), the leverage-training substitution, is an interesting comparative static** but the wording could create confusion. The result says a firm can maintain the same $X_D$ while increasing leverage by increasing $\phi$. But this does not mean the firm is *better off*: higher $\phi$ sacrifices L-regime revenue, and the net effect on equity value is ambiguous. The paper should clarify that this is a mechanical relationship, not an optimal strategy.

**Proposition 3 (Preemption equilibrium):** The existence and uniqueness argument (Part (i)) follows the Huisman and Kort (2015) construction. The intermediate value theorem application is correct: $L(0) < 0 < F(0)$ and $L(X^*_F) > F(X^*_F)$ by the monopoly-phase profit accumulation argument. The single-crossing claim requires that the leader value grows more slowly than $X^{\beta_H}$ for large $X$; since the leader value is eventually linear in $X$ (once both firms are invested), this is satisfied for $\beta_H > 1$.

**Part (ii), $\phi^*_L \geq \phi^*_F$:** The economic intuition is persuasive—the leader faces lower marginal cost of training during the monopoly phase because its L-regime contest share is 1 regardless of $\phi_L$. However, the formal argument has a gap. The paper states that the leader's L-regime revenue is "$X \cdot [(1 - \phi_L)K_L]^\alpha$ with no competition for market share"—but this is the *monopoly-phase* revenue. After the follower enters, the leader does face inference competition, and its allocation $\phi_L$ affects its duopoly contest share. The proof should account for both phases of the leader's payoff (monopoly and post-follower-entry) and show that the monopoly-phase effect dominates. The numerical verification is reassuring but a more rigorous argument would strengthen the result.

**Part (v), credit spread increasing in $\lambda_0$:** The claim that $X_P$ decreases faster than $X_D$ with $\lambda_0$ is stated but not proven—it is verified numerically. For a top journal, this should either be proved analytically (showing the elasticities satisfy $\varepsilon_{X_P, \lambda_0} < \varepsilon_{X_D, \lambda_0} < 0$) or clearly labeled as a numerical finding rather than part of the proposition.

### 4.4 Tullock Contest Specification

The choice of Tullock contests over Cournot is motivated by tractability, and Appendix F notes that the main results are preserved under Cournot. However, the Tullock specification has a conceptual issue in this context. In a standard Tullock contest, the total prize is fixed and firms compete for shares. Here, the "prize" is $X$ (total demand), which is the same regardless of total industry capacity. This means that if all firms double their capacity, individual revenues remain unchanged—total industry output is demand-determined, not supply-determined. This is a strong assumption that rules out the possibility that more compute availability grows the market (e.g., by enabling new applications or lowering prices). The Cournot alternative, where firms' capacity choices affect the equilibrium price, may be more appropriate for this setting. At minimum, the paper should discuss this limitation.

### 4.5 The Revealed Beliefs Methodology (Section 5.1)

The methodology is creative but has structural identification concerns beyond those the paper already acknowledges:

1. **The inversion uses one moment (CapEx/Revenue) to identify $\hat{\lambda}$, and checks the second moment ($\hat{\phi}$) as a diagnostic.** This is not a joint estimation. A proper two-moment approach would minimize a weighted distance between model-predicted and observed $(I/R, \phi)$ pairs, which could yield different $\hat{\lambda}$ values than the single-moment inversion. The paper should either implement the joint estimation or explain why the sequential approach is preferred.

2. **The mapping from $\lambda$ to investment intensity is non-monotonic in some regions of the parameter space.** Higher $\lambda$ increases the option value and encourages investment, but also shifts allocation toward training, which reduces L-regime revenue (the denominator of CapEx/Revenue). For extreme parameter values, these effects could partially offset. The paper should verify global monotonicity of the CapEx/Revenue-to-$\lambda$ mapping over the relevant range.

3. **Observable heterogeneity is not fully controlled.** The four archetypes differ in WACC, leverage, and training fraction, yet the inversion holds most parameters at common baseline values. Table 1 shows firm-specific WACCs ranging from 0.10 to 0.18—a range that, through the $r$-sensitivity in Table 4 ($\varepsilon_{X^*} = -20.8$), could easily account for the cross-sectional dispersion in investment intensity *without any heterogeneity in $\lambda$*. The paper should present a version of the inversion that uses firm-specific WACCs and show how this affects the implied $\hat{\lambda}$ ordering.

---

## 5. Detailed Technical Comments

### Mathematical Issues

1. **Equation (7), $A_{\text{eff}}$:** The first term should be $[(1-\phi)K]^\alpha / (r - \mu_L + \tilde{\lambda})$. In the single-firm case, there is no contest share, so this is correct. But the transition to the duopoly version (Equation 18) introduces contest shares multiplicatively. The paper should be more explicit about the nesting: Equation (7) is the single-firm case; Equation (18) is the duopoly generalization. Currently the reader encounters $A_{\text{eff}}$ in both forms and must infer the connection.

2. **Equation (10):** This is the H-regime trigger, but the LHS is labeled $X^*$ without a regime subscript. Later (Equation 14), $X^*$ appears again for the L-regime trigger. The notation should be consistent—use $X^*_H$ in Equation (10) and $X^*_L$ in Equation (14).

3. **The default boundary (Equation 19):** The characteristic root $\beta^-_s$ depends on regime-specific parameters $(\sigma_s, \mu_s)$. In the L-regime, the relevant characteristic equation should incorporate the regime-switching term ($r + \tilde{\lambda}$ instead of $r$), analogous to the option value ODE (Equation 11). The paper uses $\beta^-_s$ without specifying which regime's parameters enter. If the firm is in regime $L$ with the possibility of switching to $H$, the default boundary should be computed using the L-regime ODE with the $\tilde{\lambda}$ adjustment. Please clarify.

4. **Proof of Proposition 2, Part (ii):** The expression for $\partial A_{\text{eff},i}/\partial \tilde{\lambda}$ uses $R_L = [(1-\phi_i)K_i]^\alpha \cdot s^L_i / (r - \mu_L)$. But from Equation (18), the L-regime term in $A_{\text{eff},i}$ is $[(1-\phi_i)K_i]^\alpha \cdot s^L_i / (r - \mu_L + \tilde{\lambda})$, not divided by $(r - \mu_L)$. I believe the proof defines $R_L$ and $R_H$ as the *per unit $X$* revenue components extracted from $A_{\text{eff}}$—but the factoring should be shown more explicitly. As written, the derivative may have an error in the denominator. Specifically, writing $A_{\text{eff},i} = \frac{1}{r - \mu_L + \tilde{\lambda}}[R_L + \tilde{\lambda} R_H]$ where $R_L$ and $R_H$ are *independent of $\tilde{\lambda}$* requires:
   $$R_L = [(1-\phi_i)K_i]^\alpha \cdot s^L_i, \quad R_H = \frac{(\phi_i K_i)^\alpha \cdot s^H_i}{r - \mu_H}$$
   which differs from what is stated in the proof. Please verify and correct.

5. **Numerical Finding 2 (Asymmetric AI investment dilemma):** The paper claims the asymmetry arises from $W'''(\lambda_{\text{true}}) \neq 0$ but only provides a heuristic decomposition into capacity, timing, and training channels. The signs of each channel's contribution to $W'''$ are stated but not derived. For the capacity channel, the argument that $I(K) = cK^\gamma$ convex and revenue concave in $K$ implies $W''' < 0$ is not immediate—it depends on how $K^*(\lambda)$ maps through the NPV function. A formal derivation of $W'''$ (at least for the unlevered case) would strengthen this finding considerably.

### Calibration Issues

6. **Table 1, Training fractions:** These are described as "estimated from industry reports on compute allocation." The sources should be cited more specifically. If exact figures are unavailable (which is likely, as firms do not disclose $\phi$ directly), the paper should describe the methodology for estimating $\hat{\phi}$ from observable proxies (e.g., reported training run costs, GPU hours dedicated to training, inference API pricing). Without this, the training fraction is effectively a free parameter, which undermines its role as an identifying moment.

7. **The $\xi$ calibration (Section 4.3):** The paper calibrates $\xi$ so that industry training compute contributes "approximately half" of the total arrival rate. This is a consequential assumption—it determines the quantitative importance of the endogenous channel. Yet no justification is provided beyond the 50% figure. What is the basis for this split? If $\xi$ were calibrated to 25% or 75%, how would the results change?

8. **Revenue concepts (Table 1):** The paper correctly notes that Google's relevant revenue is Google Cloud revenue, not Alphabet total. But the same issue applies to other archetypes. OpenAI's $4B (2024) and $12B (2025) figures presumably include ChatGPT subscription revenue, API revenue, and potentially enterprise contracts—but some of this revenue comes from models trained by other firms (via API resale) or from non-compute activities. The revenue concept should be defined precisely and consistently across all archetypes.

### Exposition

9. The paper is 60 pages with appendices. For a journal submission, significant compression is needed. The comparative statics figures (Figures 3, 6) convey standard real options results and could be moved to an online appendix. The policy discussion (Section 6) is interesting but speculative; it could be shortened substantially. The literature review in Section 1.1 is thorough but long—moving some of it to footnotes would improve flow.

10. The paper introduces many parameters ($\mu_L, \mu_H, \sigma_L, \sigma_H, r, \alpha, \gamma, c, \delta, \lambda_0, \xi, \eta, \phi, \ell, c_d, b$). A consolidated parameter table early in the paper, with definitions, baseline values, and interpretations, would greatly aid readability.

11. The term "faith-based survival" is colorful and memorable but may be perceived as informal for a top finance journal. Consider a more neutral label (e.g., "optimism-driven solvency" or "belief-supported survival") and reserve the vivid language for the introduction.

---

## 6. Additional Suggestions

1. **Monte Carlo validation.** The paper uses analytical and semi-analytical solutions throughout. A Monte Carlo simulation that confirms the theoretical investment triggers and default boundaries by simulating demand paths, investment decisions, and default events would provide independent validation—especially for the preemption equilibrium, where the solution involves numerical optimization.

2. **Testable predictions.** The model generates several cross-sectional predictions: firms with higher $\hat{\phi}$ should have (i) lower credit spreads conditional on leverage (faith-based survival), (ii) higher equity betas (more growth option content), and (iii) higher implied $\lambda$ (more optimistic beliefs). These are in principle testable using the (admittedly small) cross-section of AI infrastructure firms. Even a preliminary empirical exercise matching these predictions to observable market data would substantially strengthen the paper.

3. **Welfare analysis.** Section 6.2 informally discusses the tension between overinvestment from preemption and underinvestment in training from the externality. This deserves formal treatment. Computing the socially optimal investment policy (maximizing total surplus, internalizing the $\tilde{\lambda}$ externality) and comparing it to the decentralized equilibrium would quantify the welfare losses and provide a foundation for the policy discussion.

4. **Dynamic $\phi$.** The paper repeatedly flags the static $\phi$ assumption as a limitation. Rather than a full dynamic extension, a two-period version (choose $\phi_1$ at investment, then update to $\phi_2$ after observing demand) would provide intuition for the direction of bias and could be solved analytically.

---

## 7. Minor Comments

- p. 2: "yielding a model whose quality scales as a power law of compute invested"—this elides the distinction between pre-training compute and fine-tuning compute, which have different scaling properties.
- p. 3: The Amodei (2026) quote about $1 trillion of compute appears before being formally contextualized by the AI investment dilemma framework. Consider moving it to Section 5.4 where it fits naturally.
- p. 7, Equation (2): The notation $\tilde{\lambda}(\phi_i, K_i, \phi_j, K_j)$ makes explicit the duopoly dependence but is cumbersome. Consider $\Lambda(\mathbf{K}, \boldsymbol{\phi})$ for the general case.
- p. 9, Equation (3): Revenue is $X \cdot [(1-\phi_i)K_i]^\alpha$ in the single-firm case but $X \cdot [(1-\phi_i)K_i]^{2\alpha} / \{[(1-\phi_i)K_i]^\alpha + [(1-\phi_j)K_j]^\alpha\}$ in the duopoly (Equation 15). The single-firm revenue therefore does *not* nest as $K_j = 0$ in the Tullock form (which gives $X \cdot [(1-\phi_i)K_i]^\alpha$, matching Equation (3))—it does nest, but only because $2\alpha / 1 = 2\alpha$ simplifies when the denominator is the firm's own capacity. This should be noted explicitly.
- p. 15, Figure 4(b): The $y$-axis label "Switching value coefficient $C$" should define $C$ in the caption for readers who skip to the figures.
- p. 18, Equation (19): The subscript $s$ on $\beta^-_s$ is ambiguous—does it refer to the current regime at the time of default? Presumably $s = L$ since the firm can default in either regime but the faith-based mechanism operates in $L$. Clarify.
- p. 22, Section 3.1: "iterative best-response (fixed-point iteration on the capacity and training fraction profiles), which is a numerical method distinct from the backward-induction solution concept of the duopoly"—this distinction should be emphasized more, since the $N$-firm equilibrium concept differs from the duopoly (Nash in strategies vs. subgame perfect with sequential entry).
- p. 33, Table 2: The Anthropic-like and CoreWeave-like archetypes both show $\hat{\lambda} = 0.90$. This is presented as a limitation of the single-moment inversion that the training fraction diagnostic resolves. But the paper never provides a corrected $\hat{\lambda}$ for CoreWeave using both moments jointly. What would a two-moment estimate for CoreWeave look like?
- p. 38, Section 5.4.2: The value loss function $\Delta V = \text{NPV}(\lambda_{\text{true}}, \lambda_{\text{true}}) - \text{NPV}(\lambda_{\text{true}}, \lambda_{\text{invest}})$ should be plotted as a function of $\lambda_{\text{invest}}$ for a fixed $\lambda_{\text{true}}$ to visualize the asymmetry—currently this key result has no figure.
- Throughout: References to "Numerical Finding 1" and "Numerical Finding 2" are appropriate labels for computationally verified results, but it should be clear in the main text that these are not theorems—perhaps label them "Computational Result" to avoid ambiguity.

---

## 8. Summary Assessment

This paper makes a meaningful contribution to the real options and strategic investment literatures by introducing the training-inference allocation as a novel dimension of the capacity investment problem, with regime-specific competition and an endogenous arrival rate for transformative AI. The faith-based survival mechanism is an original and economically important result. The revealed beliefs methodology is a creative application of structural modeling to extract private information from investment decisions.

However, the paper needs to address several issues before it is ready for publication at a top journal. The most important are: (1) strengthening the identification in the revealed beliefs exercise, particularly by using firm-specific WACCs and jointly estimating from both moments; (2) addressing the extreme sensitivity of implied $\hat{\lambda}$ to $\sigma_H$, which currently undermines the quantitative calibration; (3) tightening the proofs where they rely on numerical verification (Proposition 3, parts (ii) and (v)); (4) verifying and correcting the potential error in the $\partial A_{\text{eff}}/\partial \tilde{\lambda}$ derivation in the proof of Proposition 2; and (5) substantial compression for journal-length constraints. The paper would also benefit from a Monte Carlo validation, testable empirical predictions, and a formal welfare analysis.

Despite these issues, the paper addresses a first-order economic question with a sophisticated and well-motivated structural model. With significant revision, it has the potential to make an important contribution to the literature.
