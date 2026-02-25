# Investing in Artificial General Intelligence

**Date**: 2026-02-25, 4:13:16 p.m.
**Domain**: social_sciences/economics
**Taxonomy**: academic/research_paper
**Filter**: Active comments

---

## Overall Feedback

Here are some overall reactions to the document.

**Reconciling the valuation measure**

An observant reader working through the valuation logic may struggle to reconcile the different measures used across the debt and equity components. The paper currently introduces $r$ as a "risk-adjusted WACC" and $\mu_s$ as a "risk-adjusted growth rate" (Sections 2.1 and 3.1), with a note that "all valuation uses this reduced-form framework throughout." However, the credit risk section (Section 4.2.1) computes spreads relative to an explicitly risk-free rate $r_f$, and the default probability (Section 4.2.2) relies on a Merton-style formula that typically requires a specific measure change.

This creates an ambiguity regarding which discount rate applies to which claim and under which measure the state variable $X_t$ evolves. Since investment triggers and default boundaries are highly sensitive to drift and discounting, it would be beneficial to clarify whether the model operates in a physical or risk-neutral world. If $r$ includes an equity risk premium, treating it as the discount rate for debt or using it to derive risk-neutral default probabilities may introduce inconsistencies.

**Revenue specification and contest dynamics**

The specification of the production technology and the competitive contest raises a few questions regarding the underlying economic primitives. In the high regime ($H$), revenue is modeled as dependent entirely on training compute, $\phi K$ (Section 2.2.1 and Equation 15). This implies that a firm with zero inference capacity ($\phi=1$) captures maximal revenue, whereas a firm with $\phi=0$ receives nothing. While "training quality determines competitive position" is a compelling narrative, this mapping seems somewhat extreme; one might ask why post-switch value capture is purely training-limited rather than inference-limited, especially given the "AI factory" narrative.

Furthermore, the specific functional form of the Tullock contest in Sections 2.4.1 and 5.5 (Equation 14) appears to double-count capacity. By multiplying the "own capacity term" by a Tullock share that itself depends on own capacity, the model may be generating artificial scale effects where total industry revenue mechanically exceeds the symmetric benchmark solely due to asymmetry. Readers might worry that the leader/follower allocation incentives and the resulting $A_{\text{eff},i}$ (Eq. 17) are being driven by this "capacity enters twice" structure rather than the intended strategic preemption logic.

**Consistency of the pre-switch investment logic**

There appears to be a structural tension between the stated assumptions and the subsequent analysis of the low regime ($L$). Assumption 1(A3) is strictly labeled a "no-investment-in-$L$" condition, arguing that firms wait for the regime switch (Section 2.3.3). However, the paper immediately proceeds to define an $L$-regime investment trigger $X^*$ (Eq. 13) and analyze "single-firm model with training-inference allocation" behavior in Section 3.4.

Since the core economic trade-off involves sacrificing $L$-regime inference revenue to build an $H$-regime training position, this trade-off is difficult to evaluate if the region of validity implies "never invest in $L$." If the analysis is meant to apply to pre-switch behavior, Assumption A3 may need to be relaxed or the narrative adjusted so that the extensive characterization of pre-AGI allocation follows from a consistent region of the parameter space.

**The structural default boundary and the nature of the dilemma**

The derivation of the default boundary and the quantitative support for "Dario's dilemma" could be tightened to better align with the narrative. Proposition 2 attributes "faith-based survival" to training investment lowering $X_D$ by raising $A_{\text{eff},i}$. However, utilizing a standard Leland boundary with an unconditional continuation value in a regime-switching context is technically tricky; typically, the distress problem in such a setting is a coupled system where default depends on the probability of switching *before* hitting the boundary. The current shortcut also implies that the "liquidation value" in Equation 22 inherits the continuation structure, which may not be the intent.

Finally, while the introduction frames the dilemma as an asymmetry in downside/bankruptcy risk, the quantitative metric $\Delta V$ in Section 4.3.2 measures expected value loss (NPV). Numerical Finding 2 indicates that the value loss from conservative underinvestment exceeds that of aggressive overinvestment, which seems to conceptually flip the "bankruptcy risk" framing of the Amodei quote. To support the "downside risk" narrative, it would be helpful to present the asymmetry conditional on an explicit tail-risk or default probability metric rather than expected enterprise value.

**Status**: [Pending]

---

## Detailed Comments (4)

### 1. Conflation of training value slope with survival condition

**Status**: [Pending]

**Quote**:
> Write the default boundary as $X_{D}=N(\ell) / A_{\text {eff }, i}\left(\phi_{i}\right)$, where $N(\ell)=\left[\beta_{s}^{-} /\left(\beta_{s}^{-}-1\right)\right] \cdot\left(c_{d} \ell I(K) / r+\delta K / r\right)$ is strictly increasing in leverage, and $A_{\text {eff }, i}\left(\phi_{i}\right)$ is increasing in $\phi_{i}$ when the faith-based survival condition (Equation 21) holds (from part ii). A firm can therefore maintain a given default boundary $X_{D}$ while increasing leverage $\ell$ (raising the numerator) by simultaneously increasing training allocation $\phi_{i}$ (raising $A_{\text {eff }, i}$ in the denominator through the H -regime term).

**Feedback**:
The concern arises in the leverage–training substitution discussion, where it is stated that $A_{\text{eff},i}(\phi_i)$ is increasing in $\phi_i$ whenever the “faith-based survival” condition (Equation 21) holds, and this is then used to argue that a firm can keep $X_D$ fixed while raising leverage by simultaneously increasing $\phi_i$ (which is claimed to raise $A_{\text{eff},i}$).

However, Equation 21 governs the sign of $\partial A_{\text{eff},i}/\partial \lambda$ (the effect of the arrival rate on the effective revenue coefficient), not the sign of $\partial A_{\text{eff},i}/\partial \phi_i$. In earlier parts of the paper, $A_{\text{eff}}(\phi)$ is shown to be strictly concave in $\phi$ with an interior maximizer $\phi^*$ in the single-firm case, and in the symmetric-duopoly specialization preceding Equation 21 the same two-term structure carries over (up to a scale factor). In that benchmark, $A_{\text{eff},i}(\phi_i)$ therefore increases on $(0,\phi^*)$ and decreases on $(\phi^*,1)$, regardless of whether the faith-based survival condition $\phi_i>\underline{\phi}$ holds.

As a result, the statement that “$A_{\text{eff},i}(\phi_i)$ is increasing in $\phi_i$ when the faith-based survival condition holds” is not justified by the derivation in part (ii), and the inference that higher leverage can always be offset by higher $\phi_i$ along an iso–$X_D$ curve only applies locally where $A_{\text{eff},i}$ is actually increasing in $\phi_i$. It would be helpful to (i) decouple the faith-based survival condition from monotonicity in $\phi_i$, and (ii) qualify the leverage–training substitution in Proposition 2(iii) to apply on the range of $\phi_i$ over which $A_{\text{eff},i}$ is locally increasing, noting that beyond the peak of $A_{\text{eff},i}(\phi_i)$ higher training would instead raise the default boundary.

---

### 2. Logical error in boundary condition at X_F*

**Status**: [Pending]

**Quote**:
> At $X=X_{F}^{*}$ : the leader has accumulated monopoly rents over the interval since entry while the follower has just triggered, so $L\left(X_{F}^{*}\right)>F\left(X_{F}^{*}\right)$. This holds because the leader's cumulative monopoly-phase profits (earned with contest share $s_{L}=1$ ) exceed the follower's option value at the point of indifference.

**Feedback**:
At first the boundary condition “At $X=X_F^*$: the leader has accumulated monopoly rents over the interval since entry while the follower has just triggered, so $L(X_F^*)>F(X_F^*)$” made me think that $L(X)$ was being interpreted as the payoff from *investing at $X$*, in which case symmetric simultaneous investment at $X_F^*$ would give $L(X_F^*)=F(X_F^*)$. Then I understood that, in the surrounding discussion, $L(X)$ is better read as the **continuation value of an incumbent leader** as a function of the current state, given that the leader entered earlier at some $X_P<X_F^*$, while $F(X)$ is the follower’s option value prior to its own entry. Under that continuation‑value definition, $L(X_F^*)>F(X_F^*)$ is natural, because $L(X_F^*)$ includes accumulated monopoly rents over $[X_P,X_F^*]$ and $F(X_F^*)$ does not.

Because you then use $L(X)-F(X)$ on $(0,X_F^*)$ in an intermediate‑value‑theorem argument, it would be very helpful to spell out explicitly which object $L(X)$ denotes in that proof (continuation value under a fixed leader trigger $X_P$, rather than the payoff from choosing $X$ as a trigger) and to make clear that $L(X_F^*)$ is the leader’s value at the time the follower’s trigger is reached, not the value of investing for the first time at $X_F^*$. This clarification would avoid the impression that the boundary condition is inconsistent with the symmetric structure of the model.

---

### 3. Contradictory definitions of Leader Value L(X)

**Status**: [Pending]

**Quote**:
> Default risk implies $L\left(X_{D}\right)=0$; for $X>X_{D}$ the value is smooth and increasing. ... At $X=0: L(0)<0$ (the leader has incurred sunk cost $I\left(K_{L}\right)$ )

**Feedback**:
Statement “Default risk implies $L(X_D)=0$; for $X>X_D$ the value is smooth and increasing. ... At $X=0: L(0)<0$ (the leader has incurred sunk cost $I(K_L)$)” seems to mix two notions of the leader’s value. Earlier in Section 2.4.5, you define $E(X)$ as the net present value of equity at the moment of investment, net of the sunk cost, which equals $-(1-\ell)I(K)$ at $X_D$ and can be negative for small $X$, whereas the limited‑liability equity payoff is $\max\{E(X),0\}$ and is zero at $X\le X_D$.

In the proof of Proposition 3, $L(X)$ appears to stand for the limited‑liability equity value when you write $L(X_D)=0$, but for the NPV including the sunk cost when you write $L(0)<0$. It would help to clarify explicitly which object $L(X)$ denotes in this argument (NPV vs. payoff after limited liability), and, if $L$ is meant to be the NPV, to adjust the default‑boundary sentence accordingly (e.g. by noting that the underlying NPV at $X_D$ is negative while the equity payoff is zero). That would make the sign conditions used for the intermediate value theorem completely transparent.

---

### 4. Incorrect NPV condition

**Status**: [Pending]

**Quote**:
> the follower at $X_{F}^{*}$ is indifferent between investing and waiting (its NPV is zero at the trigger)

**Feedback**:
The parenthetical remark “the follower at $X_F^*$ is indifferent between investing and waiting (its NPV is zero at the trigger)” is misleading given your earlier real‑options setup. In the Dixit–Pindyck framework you adopt, the optimal trigger satisfies value‑matching and smooth‑pasting conditions, so at $X_F^*$ the installed project’s NPV relative to the investment cost, $V_{\text{follower}}(X_F^*)-I$, is strictly positive and equals the value of the option $F(X_F^*)>0$. A zero‑NPV condition $V-I=0$ would describe the Marshallian investment rule, which you explicitly distinguish from the option trigger in Section 2.3.2.

What is zero at the trigger is the *net advantage of deviating* (the follower is indifferent between exercising and waiting), not the project’s NPV. It would be clearer to rephrase this sentence accordingly, so as not to suggest that you are using a Marshallian “NPV=0” rule for the follower’s trigger.

---
