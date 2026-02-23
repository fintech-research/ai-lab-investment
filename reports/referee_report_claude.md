# REFEREE REPORT

**Manuscript:** "Investing in Artificial General Intelligence"

**Recommendation:** Revise and Resubmit (Major Revision)

---

## 1. Summary

This paper develops a real options model of irreversible capacity investment by frontier AI laboratories racing to develop Artificial General Intelligence. The key innovation is embedding a training-inference compute allocation decision within a regime-switching framework: firms choose how to split GPU capacity between model training (which builds capabilities and endogenously accelerates the arrival of a high-demand regime) and inference serving (which generates current revenue). The model combines real options theory, Markov regime switching, Tullock oligopoly competition, endogenous default risk, and diminishing returns calibrated to neural scaling laws. It delivers closed-form investment triggers for a duopoly with default risk and a revealed beliefs methodology that inverts the structural model to extract implied AI timeline beliefs from observable investment decisions.

The paper is ambitious and timely. The AI infrastructure investment boom is arguably the most consequential capital allocation episode since the dot-com era, and there is a genuine need for rigorous analytical frameworks to understand the decision-making of frontier labs. The training-inference allocation is a genuinely novel modeling contribution, the faith-based survival mechanism is economically interesting, and the revealed beliefs exercise is creative. However, the paper has several significant issues—mathematical, conceptual, and empirical—that must be addressed before it is suitable for a top finance journal.

## 2. Assessment of Contribution

The paper claims four main contributions: (i) the training-inference allocation with endogenous regime switching, (ii) closed-form triggers with a faith-based survival mechanism, (iii) a revealed beliefs methodology using two identifying moments, and (iv) calibration to the AI infrastructure sector. I assess each in turn.

**Training-inference allocation.** This is the strongest and most novel aspect of the paper. The idea that frontier labs face a genuine intertemporal trade-off between inference (current revenue) and training (future competitive position) is well-motivated empirically and has not been formalized in the real options or corporate finance literatures. The regime-specific competition structure—Tullock contests over inference capacity today and training quality tomorrow—is a clean way to capture the arms-race dynamics that executives describe. The connection to the endogenous arrival rate (firms' training accelerates AGI) is a creative externality mechanism. This contribution alone makes the paper interesting.

**Closed-form results.** The claim of closed-form investment triggers is somewhat overstated. The triggers are closed-form conditional on the optimal capacity and training fraction, which are themselves determined by first-order conditions that do not have closed-form solutions in the general (L-regime with regime switching) case. More importantly, as I detail below, the derivation of the L-regime option value contains a mathematical error that calls into question the closed-form expressions. The faith-based survival mechanism—where optimism about AGI lowers the default boundary—is economically compelling and clearly articulated, though the underlying comparative static (higher λ raises A_eff, which lowers X_D) is relatively straightforward once the model is set up correctly.

**Revealed beliefs.** The idea of inverting a structural model to extract private beliefs from observable investment decisions is appealing in principle. However, the execution raises serious identification concerns. The sensitivity analysis (Table 5) reveals that the implied λ for the Anthropic-like archetype ranges from 0.003 to 0.90 under ±25% variation in σ_H alone—essentially spanning the entire parameter space. This means the cardinal estimates are uninformative. The paper acknowledges this and retreats to ordinal rankings, but even the ordinal claim is fragile: it depends entirely on the maintained assumption that all firms face identical demand-side parameters, which is implausible given the very different business models of the four archetypes. The two-moment approach using ϕ̂ is a step in the right direction but is not implemented as a joint estimation—ϕ is used only as a diagnostic, not as a binding moment condition.

**Calibration.** The stylized firm exercise is useful for illustration but should be framed more cautiously. The paper uses approximate composites from public filings, but the mapping from these composites to model parameters involves substantial judgment. For example, what counts as "revenue" for Google/Alphabet (the paper uses Google Cloud revenue, not Alphabet total) is a consequential choice that directly affects the CapEx/Revenue ratio and hence the implied λ. The revenue and CapEx figures in Table 1 are already somewhat dated relative to February 2026 and should be updated or at least explicitly time-stamped.

## 3. Major Concerns

### 3.1. Mathematical Error in L-Regime Option Value

This is the most serious technical issue. Section 2.3.3 claims that the option value in the low regime takes the form F(X) = B · X^{β_H}, using the H-regime characteristic exponent. The justification offered is that "the investment option value is driven by H-regime expectations." This is incorrect.

In a regime-switching model, the option value in regime L satisfies the Hamilton-Jacobi-Bellman equation:

> ½σ²_L X² F_L'' + μ_L X F_L' + λ̃[F_H(X) − F_L(X)] − r F_L = 0

where F_H(X) = B_H X^{β_H} is the known H-regime option value. Substituting and rearranging:

> ½σ²_L X² F_L'' + μ_L X F_L' − (r + λ̃) F_L + λ̃ B_H X^{β_H} = 0

The homogeneous part of this ODE has characteristic equation ½σ²_L β(β−1) + μ_L β − (r+λ̃) = 0, which yields roots β⁺_L and β⁻_L that depend on σ_L, μ_L, r, and λ̃—**not** on any H-regime parameters. The non-homogeneous term λ̃ B_H X^{β_H} produces a particular solution of the form C X^{β_H}. The general solution is therefore:

> F_L(X) = A₁ X^{β⁺_L} + C X^{β_H}

where I have set the coefficient on β⁻_L to zero (boundary condition as X → 0). The paper's claimed solution F_L = B X^{β_H} amounts to setting A₁ = 0, which is not generically true. The homogeneous solution A₁ X^{β⁺_L} captures the "pure" option to invest in the L-regime with L-regime demand dynamics, while the particular solution C X^{β_H} captures the value arising from the possibility of a regime switch. Dropping the homogeneous term is a non-trivial restriction on the solution that would require β⁺_L = β_H (i.e., identical characteristic roots across regimes) or a specific limiting argument (e.g., λ̃ → ∞). Neither is established.

This error propagates to the investment trigger (Equation 11), the smooth-pasting conditions, the comparative statics in Proposition 1, and potentially the duopoly equilibrium. The correct approach is to follow Guo, Miao, and Morellec (2005) and solve the coupled system of ODEs for F_L and F_H jointly, applying value-matching and smooth-pasting at the respective triggers in each regime. The resulting solution will have *two* trigger conditions (one for potential L-regime investment, one for H-regime investment) and the option value in L will be a sum of power terms with different exponents. This is a standard result in the regime-switching real options literature, and the paper's departure from it needs rigorous justification or correction.

**Required action:** Rederive the L-regime option value using the correct coupled ODE system. Verify that Equation 11, Propositions 1–3, and the comparative statics survive (possibly with modified expressions). If closed-form solutions are no longer available, provide the correct system of equations and solve numerically, which is already the approach for the N-firm game.

### 3.2. Identification of Revealed Beliefs

The revealed beliefs methodology is the paper's most policy-relevant contribution, but the identification is substantially weaker than presented. Several issues compound:

**(a) Extreme sensitivity to σ_H.** Table 5 shows that a ±25% perturbation in H-regime volatility moves the Anthropic-like implied λ from 0.003 to 0.90, a 300-fold range. Since σ_H is not directly observable (it describes a counterfactual regime that has not yet been realized), any point estimate of implied beliefs is effectively meaningless. The paper should report full confidence sets rather than point estimates, and should discuss what external information would discipline σ_H.

**(b) Heterogeneous demand parameters.** The inversion assumes all firms face identical demand-side parameters (μ_L, μ_H, σ_L, σ_H) and differ only in λ. But the four archetypes have fundamentally different business models: Google earns diversified cloud revenue, CoreWeave is a pure-play GPU lessor, Anthropic is a frontier lab selling API access, and OpenAI has a consumer product. These firms plausibly face different demand processes. Cross-sectional variation in μ_H or σ_H would be absorbed into the implied λ, contaminating the belief estimates. The paper needs either a formal argument for why demand-side homogeneity is a reasonable maintained assumption, or an extension that allows for heterogeneous demand parameters.

**(c) Training fraction is a diagnostic, not an identifying moment.** The paper claims two identifying moments (CapEx/Revenue and ϕ̂), but the inversion algorithm (Section 5.1.1, Step 3) only uses CapEx/Revenue to invert for λ; ϕ̂ is then compared to the model's predicted ϕ*(λ̂) as a specification check. This is a one-moment inversion with a diagnostic, not a two-moment estimation. To genuinely use both moments, the paper should set up a minimum-distance or simulated method of moments estimator that jointly matches investment intensity and training fraction, with a formal overidentification test. The discrepancy for CoreWeave (ϕ̂ = 0.20 vs. ϕ*_model = 0.52) is interpreted as revealing that CoreWeave is a debt-funded infrastructure play rather than a belief-driven investor, but this interpretation is post hoc—the model has no mechanism for debt-funded infrastructure plays to produce a low ϕ. This suggests the model is misspecified for CoreWeave, which undermines the claim that ϕ provides independent identification.

**(d) Timing of commitments.** The paper acknowledges (Section 5.1.2) that observed 2025 CapEx reflects commitments made 12–24 months earlier. This means the revealed λ is a lagged indicator. But the paper does not explore the magnitude of this lag or its implications for interpretation. Given that the AI landscape changed dramatically between late 2023 and early 2026 (GPT-4, Claude 3, DeepSeek R1, inference-time scaling), the beliefs embedded in 2025 CapEx may be substantially different from current beliefs.

**Required action:** (i) Report confidence sets over σ_H, γ, and α jointly rather than one-at-a-time sensitivities. (ii) Implement a proper two-moment estimator using CapEx/Revenue and ϕ̂ jointly. (iii) Discuss or model demand-side heterogeneity. (iv) Acknowledge that the exercise is closer to a calibration illustration than a structural estimation, and adjust the framing accordingly (the paper partially does this but inconsistently).

### 3.3. Static Training Fraction

The assumption that the training fraction ϕ is chosen at investment time and fixed thereafter is a significant limitation that is not adequately addressed. In practice, firms dynamically reallocate compute between training and inference on a daily basis. The emergence of inference-time scaling (test-time compute, chain-of-thought reasoning) has blurred the boundary between training and inference, making the binary split increasingly unrealistic. Moreover, the static ϕ assumption drives several of the paper's key results: the faith-based survival mechanism requires that ϕ be committed ex ante (so that it enters A_eff at the time of investment), and the revealed beliefs diagnostic requires that observed ϕ̂ can be meaningfully compared to the model's static ϕ*. If ϕ is dynamic, the observed *average* training fraction reflects the firm's optimal rebalancing policy, which depends on the current state (X_t, regime), not just on λ.

**Required action:** At minimum, the paper should provide an argument for why the static ϕ approximation captures the first-order effects. Ideally, the paper would present a simplified dynamic extension (even if solved numerically) to verify that the static model's predictions are qualitatively robust. The paper could also model ϕ as a slow-moving state variable (since large training runs take weeks to months) to motivate the static assumption as a time-scale approximation.

### 3.4. Tullock Contest Specification

The choice of the Tullock contest success function for revenue sharing is consequential but not well-motivated. The paper uses the same functional form in both regimes, with the regime-specific capacity measure substituted in. Several concerns arise.

First, the Tullock contest implies that revenue depends on *relative* capacity, which makes sense for a zero-sum market share game but is less appropriate if the market is growing and firms can expand the pie. In the current AI market, aggregate demand for inference is growing rapidly and firms are not obviously competing for a fixed pool of revenue. A Cournot specification (where each firm's revenue depends on its own capacity and total industry output affects price) might be more appropriate and would give different comparative statics.

Second, the revenue function in Equations 12–13 has the firm earning X · [(1−ϕ_i)K_i]^{2α} / {[(1−ϕ_i)K_i]^α + [(1−ϕ_j)K_j]^α}. When both firms are symmetric, this simplifies to X · K^α/2, which is half the single-firm revenue. The transition from the single-firm revenue (Equation 3) to the duopoly revenue (Equation 12) is not continuous as K_j → 0: with any positive K_j, the functional form changes. The paper should verify that the equilibrium is robust to alternative contest specifications, particularly Cournot, as suggested in the robustness discussion but not actually implemented.

**Required action:** Provide economic justification for the Tullock specification in the AI compute market. Implement and report the Cournot alternative (Appendix F mentions it but provides no results). Discuss whether the qualitative results—especially the asymmetry of the investment dilemma—survive alternative competitive structures.

## 4. Minor Concerns

### 4.1. Literature Positioning

The literature review is comprehensive and mostly well-executed, though several gaps should be addressed:

The connection to the *technology adoption* literature is underdeveloped. The regime switch from L to H is functionally a technology adoption event, and there is a substantial literature on adoption timing under uncertainty and network effects (e.g., Katz and Shapiro, 1986; Farrell and Saloner, 1986) that is not cited. The endogenous λ mechanism, where firms' training investment accelerates adoption, is a form of adoption externality that maps naturally to this literature.

The paper cites Akcigit and Kerr (2018) as the closest analog for the exploitation-exploration trade-off, but the more direct precedent in the real options literature is the choice between R&D investment (creating future options) and production capacity (exploiting current opportunities), as in Dixit and Pindyck (1994, Chapter 11). The training-inference split maps almost exactly to this framework.

The paper does not engage with the growing empirical literature on AI investment. Babina et al. (2024) study how AI investments affect firm value; Eisfeldt et al. (2024) examine the labor market effects of generative AI adoption. These papers provide empirical context for the theoretical mechanisms.

Finally, there is no discussion of the venture capital and startup finance literature (e.g., Gompers and Lerner, 2004; Kerr, Nanda, and Rhodes-Kropf, 2014), despite the fact that two of the four stylized firms (Anthropic and OpenAI) are venture-backed. The implications of VC governance for investment decisions differ substantially from the standard Leland framework.

### 4.2. Endogenous λ Calibration

The endogenous arrival rate mechanism is interesting but the calibration is ad hoc. The paper sets ξ so that modeled firms contribute "approximately half" of the total arrival rate. What is the basis for this? If the four modeled firms collectively represent, say, 60–70% of global frontier training compute (a defensible estimate), then the implied ξ could be derived from this share rather than set by fiat. The paper should also discuss how sensitive the results are to the scaling exponent η = 0.07, which is borrowed from the neural scaling laws literature but applied to a very different concept (the probability of achieving AGI, not model loss on a benchmark). The mapping from "loss on next-token prediction" to "probability of transformative AI" is highly non-trivial and deserves explicit discussion.

### 4.3. Default Mechanism and Venture Funding

The Leland (1994) default framework assumes that firms issue perpetual debt with a continuous coupon and default when equity value reaches zero. This is a reasonable approximation for mature firms with traded debt, but it fits poorly for Anthropic and OpenAI, which are funded primarily by equity (venture capital and strategic investments from Amazon and Microsoft, respectively). For these firms, the relevant "default" is not a failure to service debt but a failure to raise the next round of funding—a liquidity event that depends on investor sentiment, competitive positioning, and milestone achievement, not on the Leland smooth-pasting condition. The paper should either restrict the default analysis to the two archetypes where debt is relevant (Google-like and CoreWeave-like) or develop an alternative "funding failure" boundary for venture-backed firms (e.g., a cash-flow covenant that triggers when revenue falls below operating costs for a sustained period).

### 4.4. Absorbing H-Regime

The assumption that the H-regime is absorbing (once capabilities are demonstrated, they never disappear) is stated as capturing the "irreversibility of AI progress." While AI capabilities have historically been monotonically increasing, the absorbing assumption is stronger than necessary and has consequences for the model. It means that the H-regime growth rate μ_H applies in perpetuity, which may be unrealistic if the post-AGI economy eventually reaches a steady state. A more flexible specification would allow for a subsequent transition from H to a mature regime with lower growth, which would reduce the H-regime option value and affect the investment trigger. The paper should at least discuss the quantitative importance of the perpetual high-growth assumption.

### 4.5. Proposition 3, Part (ii): Leader's Training Fraction

The claim that ϕ*_L ≥ ϕ*_F is stated as part of Proposition 3 but the proof (Appendix A) only says "The result is verified numerically across the full parameter space." This is not a proof. For a claim elevated to a proposition, either provide an analytical proof or downgrade it to a numerical finding with appropriate caveats. The intuition given (the leader has monopoly-phase inference revenue, so can afford more training) is plausible but does not constitute a proof, especially since the follower's problem involves a different contest structure.

### 4.6. AI Investment Dilemma

Proposition 5 (asymmetric investment dilemma) is interesting but the proof relies on showing that W'''(λ_true) < 0, where W is the value function of the mismatched firm. The proof sketch identifies three channels (capacity, timing, training) each contributing W''' < 0, but does not show this formally—it argues each channel "contributes" without computing or bounding the third derivative. Moreover, the result depends on the specific functional forms (γ > 1, α < 1) and may not hold for all parameter values. The paper should provide conditions under which the asymmetry holds, not just assert it.

### 4.7. Missing Empirical Validation

The paper is purely theoretical with an illustrative calibration. For a top finance journal, some form of empirical validation would strengthen the paper substantially. Possible approaches include: (i) testing the model's prediction that more optimistic firms allocate more to training, using cross-sectional variation in observable training intensity and proxy variables for beliefs (e.g., executive statements, prediction market data on AGI timelines); (ii) examining whether the model's predicted credit spreads match observed spreads for AI infrastructure debt (e.g., CoreWeave's traded bonds); (iii) testing whether equity valuations covary with AI timeline news in the direction and magnitude predicted by the model.

## 5. Specific Comments

**Page 1, Abstract.** The abstract claims "closed-form investment triggers and capacity in a duopoly with default risk." This should be qualified: the triggers are closed-form given the optimal capacity and training fraction, which require numerical solution in the general case.

**Page 2.** The statement that "a $10 billion training cluster cannot be easily repurposed" is debatable. Training clusters can be (and are) repurposed for inference; the irreversibility is in the total compute capacity, not the training/inference split. This actually strengthens the case for a dynamic ϕ model.

**Equation 2.** The endogenous arrival rate λ̃ sums the training compute of only two firms. But in the N-firm extension (Section 3.1), it sums over all N. The notation should be unified from the start, or Equation 2 should be stated for the general N-firm case.

**Equation 7.** The effective revenue coefficient A_eff(ϕ, K) has λ̃ in both the denominator of the first term and the numerator/denominator of the second term. Since λ̃ depends on (ϕ, K) through Equation 2, A_eff is implicitly a fixed-point equation. The paper should state explicitly whether the λ̃ in A_eff is evaluated at the firm's own chosen (ϕ, K) or at some equilibrium value.

**Table 1.** The training fractions are "estimated from industry reports on compute allocation" but no specific reports are cited. Given that ϕ̂ is one of the two key moments for the revealed beliefs exercise, the data sources should be more transparent. Are these estimates based on GPU counts, power consumption, or reported training run durations?

**Figure 1.** The log-scale y-axis compresses the visual impact of the regime switch. Consider showing one panel in log scale and one in linear scale to help the reader appreciate the economic magnitude.

**Section 4.1.** The paper sets r = 0.12 as the "risk-adjusted WACC for a representative AI infrastructure firm" but Table 1 shows firm-specific WACCs ranging from 0.10 to 0.18. Which WACC is used in the revealed beliefs inversion? The text says "I use the common baseline" but using a common r when true WACCs differ by up to 80% (0.10 vs. 0.18) introduces substantial bias. The paper should either use firm-specific WACCs in the inversion or demonstrate that the ordinal ranking of implied λ is robust to WACC heterogeneity.

**Section 5.3.2.** The default probability formula uses the Merton (1974) approximation, which does not account for the regime switch. In the L-regime, default probability should account for the possibility that a switch to H would move the firm further from the default boundary. This is likely to make the Merton approximation conservative (overstating default probability), which should be noted.

**Section 6.4, Limitations.** The paper omits any discussion of the recent shift toward inference-time scaling (test-time compute), which fundamentally changes the training-inference trade-off. Models like OpenAI's o1/o3 and DeepSeek R1 generate revenue from inference that also serves as a form of training (reinforcement learning from deployment). This trend undermines the sharp binary split that is central to the model. Even a brief discussion of how inference-time scaling would affect the model's predictions would be valuable.

**Appendix A, Step 5.** The argument for existence of interior ϕ* claims that ∂h/∂ϕ → +∞ as ϕ → 0 because "the H-regime term's marginal value diverges." But (ϕK)^α → 0 as ϕ → 0, and ∂[(ϕK)^α]/∂ϕ = αK^α ϕ^{α−1}, which diverges because α < 1. The argument is correct but the text should state the mechanism more precisely: it is the concavity of (ϕK)^α (Inada condition) that drives the divergence, not the "marginal value" generically.

**Appendix A, Proof of Proposition 3.** The existence proof for the preemption trigger invokes the intermediate value theorem by claiming L(0) < 0 (sunk cost) and L(X*_F) > F(X*_F). The first claim is not obvious: at X = 0, the leader has invested and earns zero revenue in perpetuity, so its value is −I(K_L) − δK_L/r + λ̃ · (H-regime continuation value), which could be positive if the H-regime value is large enough. The proof should be more careful about the boundary conditions.

## 6. Overall Assessment

This paper tackles an important and timely topic with an ambitious modeling framework. The training-inference allocation is a genuine contribution to the real options literature, the faith-based survival mechanism is economically insightful, and the revealed beliefs exercise is creative. However, the mathematical error in the L-regime option value derivation is a first-order concern that must be resolved before the analytical results can be trusted. The identification of revealed beliefs is substantially weaker than presented and needs to be reframed or strengthened with a proper multi-moment estimator. The static training fraction assumption is a limitation that deserves more careful treatment.

If the mathematical issues are resolved and the identification discussion is appropriately nuanced, the paper could make a meaningful contribution to the intersection of real options, corporate finance, and the economics of AI. I recommend a major revision addressing the concerns above, with particular attention to Sections 3.1 (L-regime derivation), 3.2 (identification), and 3.3 (static ϕ).
