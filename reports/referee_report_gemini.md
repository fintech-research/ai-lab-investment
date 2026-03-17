# Referee Report

**Title:** Investing in Artificial General Intelligence
**Author:** Vincent Grégoire

## 1. Summary

The paper develops a continuous-time real-options model to analyze the investment and capacity allocation decisions of frontier Artificial Intelligence (AI) laboratories. Facing uncertain demand driven by a potential regime shift to Artificial General Intelligence (AGI), a firm must choose the optimal timing to invest, the capacity of irreversible compute to build, and critically, how to allocate that capacity between current revenue-generating inference and future capability-building training. The model incorporates regime-switching demand, duopoly preemption, endogenous default risk (à la Leland), and diminishing returns.

The author derives three main novel results: (1) an analytical characterization of the optimal capacity and training-inference split; (2) a "faith-based survival" mechanism where allocating capacity to training raises the post-AGI continuation value, thereby lowering the endogenous default boundary; and (3) an asymmetric "Dario's dilemma," showing that conservative underinvestment (under-allocating to training) is significantly costlier in expected value than aggressive overinvestment.

## 2. Overall Assessment

This is a highly ambitious, timely, and elegantly constructed paper. The author successfully integrates several complex strands of theoretical corporate finance—real options, dynamic duopoly games, and structural credit risk—into a single, unified framework. The core mechanism (the tension between dedicating capital to survive today versus dedicating capital to win tomorrow) is intuitively appealing and captures the central economic friction of the current AI infrastructure boom.

The paper's contribution to the real-options and strategic investment literature is clear and substantial. By making the _use_ of installed capacity (the training-inference allocation $\phi$) endogenous and linking it to a regime-dependent payoff, the paper breaks new ground. However, to meet the bar of a top finance journal, the author must address some restrictive modeling assumptions—particularly the static nature of the capacity allocation and the reliance on identical scaling elasticities for training and inference—which may be driving the core results.

Below are my major and minor comments for the author to consider.

## 3. Major Comments

**1. The Static Nature of the Allocation Parameter ($\phi$)**
The model assumes that the fraction of compute allocated to training ($\phi$) is chosen at the time of investment and remains fixed forever. While I appreciate the immense tractability this affords (avoiding $\phi$ as a continuous state variable in the HJB equation), it suppresses a critical margin of safety for the firm. In reality, compute is highly fungible. If a firm faces impending default because current L-regime cash flows are too low, it can dynamically reallocate GPUs from training to inference to boost short-term revenue.

- **Recommendation:** The author should either solve a simplified extension where one-time reallocation is allowed at a cost, or provide a much more rigorous discussion of how a dynamic $\phi$ would alter "Dario's dilemma." Intuitively, if a firm can reallocate to save itself, the extreme downside risk of over-allocating to training is heavily mitigated, potentially making the asymmetry in "Dario's dilemma" even stronger (i.e., making aggressive investment even safer).

**2. Separation of Capacity ($K$) and Allocation ($\phi$)**
In Proposition 1, the author demonstrates that the optimal capacity $K^*$ is independent of the training fraction $\phi^*$. This is a beautiful analytical result, but it appears to be entirely mechanically driven by the assumption that the elasticity of revenue with respect to capacity ($\alpha$) is identical for both inference (Equation 2) and training (Equation 3).

- **Recommendation:** Is there empirical or scaling-law justification for assuming that inference revenue scales at the exact same rate as training capability? If $\alpha_L \neq \alpha_H$, the separability of $K$ and $\phi$ breaks down, and the investment scale becomes a function of the allocation choice. The author should test the robustness of the model to $\alpha_L \neq \alpha_H$ (even if only numerically) to prove that the core economic insights survive when this mathematical convenience is relaxed.

**3. "Faith-Based Survival" vs. Standard Continuation Value**
The "faith-based survival" mechanism is framed as a major novel contribution. However, in any standard Leland (1994) or Hackbarth et al. (2014) model with a growth option, an increase in the expected continuation value mechanically lowers the default boundary.

- **Recommendation:** The author needs to better isolate what is _structurally new_ here. Is the novelty simply that $\phi$ is the control variable driving the continuation value? The author should explicitly contrast the comparative statics of this mechanism against a baseline structural credit model with a standard exogenous growth option to highlight the marginal contribution of the allocation channel.

**4. Literature Review and Capital Structure Framing**
The literature review is thorough regarding real options and R&D races. However, the application of a continuous-coupon Leland debt structure to frontier AI labs (which are heavily VC-backed, relying on SAFEs, convertible notes, and complex equity tranches) requires careful defense.

- **Recommendation:** While the author acknowledges this in Section 5 (and correctly notes recent debt issuances by OpenAI and xAI), the paper would benefit from engaging with the literature on staging and venture capital financing (e.g., _Gornall and Strebulaev, 2020_). The author should clarify that "default" in this model can also be broadly interpreted as a "down-round," a liquidity crisis, or the inability to raise the next tranche of capital, rather than strict bankruptcy on public bonds.

## 4. Minor Comments

1. **Calibration of $\lambda$:** The baseline calibration uses $\lambda = 0.10$ (10-year expected arrival). The implied belief inversions in Section 4 are very sensitive to this and the scaling parameter $\alpha$. The author should provide a contour plot showing the sensitivity of "Dario's Dilemma" (value loss) to joint variations in $\lambda$ and $\alpha$.
2. **Duopoly Assumptions:** In the duopoly setting, the model assumes a "Tullock contest" for market share. It would be helpful to briefly explain why a contest success function is preferred over standard Cournot or Bertrand competition in the pre-AGI regime. Does it better reflect the winner-take-all dynamics of AI benchmarks?
3. **Endogenous $\lambda$ (Welfare):** In Section 5.1, the author briefly notes that an endogenous $\lambda$ (where aggregate training accelerates AGI) would create a positive externality. This is a fascinating point. Given the paper's focus on AGI, even a stylized two-firm proof of this social vs. private investment gap would elevate the paper's policy relevance.

## 5. Conclusion

This is an excellent working paper that tackles one of the most important capital allocation problems of the current decade. The mathematical derivations are sound, and the theoretical architecture is highly sophisticated. By addressing the robustness of the static $\phi$ assumption and the identical $\alpha$ elasticities, the paper will represent a top-tier contribution to the corporate finance and real-options literature.
