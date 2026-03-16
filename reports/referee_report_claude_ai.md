# REFEREE REPORT

*Investing in Artificial General Intelligence* by Vincent Grégoire

---

## 1. Summary and Recommendation

This paper develops a continuous-time real options model of irreversible capacity investment by frontier AI laboratories. The model's distinctive feature is a *training-inference allocation*: firms must split installed GPU capacity between inference (which generates current revenue) and training (which builds capabilities for a post-AGI regime). The paper combines regime switching (à la Guo, Miao, and Morellec, 2005), duopoly preemption (à la Huisman and Kort, 2015), endogenous default (Leland, 1994), and diminishing returns calibrated to AI scaling laws. Three headline results emerge: (i) analytical characterization of the optimal training fraction and investment trigger in the single-firm case; (ii) a "faith-based survival" mechanism whereby training investment lowers the default boundary through the continuation-value channel; and (iii) "Dario's dilemma," an asymmetric cost-of-error result showing that underinvestment in training is more costly in expected value than overinvestment of equal magnitude.

**Recommendation: Revise and resubmit.** The paper tackles an important and timely problem—one that genuinely matters for practitioners, policymakers, and academics—and the core economic mechanism (the training-inference allocation linking growth options to default risk) is novel and interesting. The calibration to real AI lab archetypes is ambitious and the paper is generally well-written. However, several issues need to be addressed before the paper is suitable for publication. The most important concerns relate to (a) the static nature of the training fraction, which the paper itself identifies as the key limitation but does not adequately bound; (b) the strength of some claims relative to the analytical results actually delivered; (c) the calibration's sensitivity to hard-to-pin-down parameters; and (d) some gaps in the proofs and model exposition. I elaborate below.

## 2. Assessment of Contribution

### 2.1 What the paper does well

The central contribution—the training-inference allocation channel—is genuinely novel and fills a real gap in the literature. No existing paper captures the mechanism by which a firm's choice of how to split compute between current revenue generation and future capability building simultaneously determines its growth-option value and its distance to default. The "faith-based survival" result (Proposition 2) is particularly compelling: it formalizes the intuition, widely held in the industry, that the prospect of transformative AI is itself a source of financial resilience. The closed-form threshold φ̄ (Equation 19) is a clean, interpretable result.

The paper also does a commendable job of engaging with the institutional reality of the AI sector. The stylized archetypes in Table 1 are carefully constructed from public filings and reports, and the discussion of how training fractions are estimated (executive statements, Epoch AI decompositions, Deloitte trajectories) is unusually transparent for a theory paper. The "Dario's dilemma" framework is memorable and provides a useful organizing device for thinking about the asymmetric risks of over- and under-investment.

### 2.2 Concerns about scope of contribution

My primary concern is that the paper's strongest claims rest on a modeling choice that the paper itself identifies as the most important limitation: the static training fraction. The assumption that φ is fixed at investment time is analytically convenient but creates a tension with the headline results. Consider:

**Faith-based survival.** Proposition 2 shows that higher φ lowers the default boundary through the continuation-value channel. But if φ is dynamically adjustable, a firm approaching distress would reallocate from training to inference, boosting L-regime cash flow and lowering the default boundary through a *different* channel. The static model conflates these two margins. The Section 5.4 discussion acknowledges this but does not bound the bias. At minimum, I would want to see a quantitative assessment: how large is the faith-based survival effect relative to the reallocation option value? Without this, it is difficult to know whether the mechanism survives in a richer model.

**Dario's dilemma asymmetry.** The asymmetry in Numerical Finding 2 is driven by the training allocation channel: a pessimistic firm under-allocates to training and forfeits the H-regime option value. With dynamic reallocation, a firm that initially under-trains could adjust upward upon receiving positive signals about λ, substantially attenuating the asymmetry. The paper notes this (Section 5.4) but again does not quantify the attenuation. The two-period intuition in Section 5.4 is helpful but informal; a formal two-period extension, even under simplifying assumptions, would significantly strengthen the paper.

**Leader-follower training gap.** Proposition 3(ii) is labeled a "computational regularity" rather than an analytical result. This is refreshingly honest, but it also means the paper's claims about the leader training more than the follower lack formal support. The analytical motivation provided (the monopoly-phase effect) is intuitive but not a proof. Given that this is one of three headline results, elevating it to at least a semi-analytical result (e.g., by proving it under symmetry with zero leverage) would be valuable.

## 3. Literature Review

The literature review is thorough and well-organized. The paper correctly identifies its position at the intersection of four literatures (real options, strategic investment, structural credit, AI economics) and makes a convincing case that no single existing paper generates the training-survival channel. A few specific comments:

**R&D race literature.** The connection to Loury (1979), Lee and Wilde (1980), and Reinganum (1981, 1982) is well-drawn. However, the paper could engage more with the distinction between *pure R&D races* (where expenditure buys probability of breakthrough) and the present setting (where training buys competitive position conditional on a regime switch the firm cannot accelerate). The paper briefly notes that endogenizing λ as a function of aggregate training compute would create a positive externality (Section 5.1), but this extension would literally turn the model into an R&D race in the Loury sense. A brief discussion of how the results would change under endogenous λ would sharpen the marginal contribution claim.

**Hackbarth, Mathews, and Robinson (2014).** This is correctly identified as the closest paper combining real options with endogenous default and product market competition. The paper should more clearly articulate what is structurally different versus what is a richer parameterization. The training-inference allocation is genuinely new, but the regime-switching demand and Tullock contest are modeling choices that could, in principle, be grafted onto the Hackbarth et al. framework.

**Missing references.** The paper should cite Aguerrevere (2009, RFS) on capacity investment under uncertainty with market competition—the paper's Tullock contest is closely related to capacity competition with endogenous output. Novy-Marx (2007) is cited but the connection to operating leverage could be developed further, given the paper's result that high-φ firms have higher equity betas (Section 5.2, prediction 2). Grenadier and Malenko (2011, RFS) on Bayesian learning in real options is relevant to the discussion of belief updating in Section 5 and the future research direction on dynamic learning.

## 4. Model Derivation and Proofs

### 4.1 Proposition 1 (Optimal capacity and training fraction)

The proof is clear and correct. The key insight—that K* is independent of φ because A_eff factors as g(φ)·K^α—is well-explained and the Inada conditions for interiority of φ* are properly verified. Two minor issues:

(a) The proof uses the simplified option value F_L = C·X^{β_H}, which requires Assumption 1(A3). The paper notes that A3 holds at baseline (α = 0.40, (1 − 1/β_L^+)/α ≈ 1.67) and throughout the sensitivity range α ∈ [0.20, 0.60]. But the archetype-specific WACCs change β_L^+ and could push (A3) to fail. The paper's Appendix B notes that the hyperscaler archetype (r = 0.10) violates (A2) and the compute racer (r = 0.18) violates the upper bound. The reader needs a clearer statement of which analytical results apply to which archetypes and which require full numerical optimization.

(b) The comparative static ∂φ*/∂λ > 0 in Proposition 1(i) follows cleanly from the implicit function theorem. However, the text in Remark 1 states that "higher λ raises the option value monotonically and encourages earlier, larger, and more training-intensive investment." The "larger" claim is not part of Proposition 1—K* is independent of λ. This should be clarified: K* is independent of λ (by Proposition 1) but the *duopoly* capacity may change through the contest function.

### 4.2 Proposition 2 (Faith-based survival)

This is the paper's most novel analytical result. The derivation is sound. The decomposition of ∂X_D/∂λ into the β-channel (positive) and the A_eff-channel (negative) in the proof is illuminating. A few points:

(a) The proof states that the β-channel is "approximately 52% of the A_eff-channel in absolute magnitude" at baseline. This is a numerical claim embedded in what is otherwise an analytical proof. It would be cleaner to state a sufficient condition for the A_eff-channel to dominate (e.g., a bound on μ_H − μ_L relative to σ) and verify it at all calibration points.

(b) The closed-form threshold φ̄ (Equation 19) is derived for the symmetric duopoly with s_i^L = s_i^H = 1/2. The paper should verify whether the asymmetric case (e.g., a leader with higher K and φ) changes the threshold quantitatively. Given the asymmetric calibration in Table 1, this is relevant.

(c) Part (iii) on leverage-training substitution is described as "mechanical" and "not a statement about optimality." This is the correct caveat, but the paper then uses it to generate a testable prediction: "highly levered AI firms should exhibit higher training fractions." The prediction requires an assumption about the *joint* determination of (ℓ, φ) that is not formally modeled—the paper takes leverage as exogenous. If leverage is endogenous (as suggested in the future work discussion), the co-movement could go either way. Soften this prediction or provide the endogenous leverage extension.

### 4.3 Proposition 3 (Preemption equilibrium)

This is the most complex result and the proof is appropriately careful about separating analytical existence from computational verification. Several concerns:

(a) **Existence.** The existence argument relies on showing L(0) < F(0) and L(X_F*) > F(X_F*). The first condition is immediate (L(0) = −(1 − ℓ)I(K_L) < 0 = F(0)). The second condition—that the leader's value at the follower's trigger exceeds the follower's option value—is asserted with an intuitive argument about accumulated monopoly rents but not formally proved. A brief sketch would help: the leader's value at X_F* includes the present value of monopoly-phase revenue over [X_P, X_F*], which is bounded below by a function of X_F* − X_P and the monopoly revenue rate; the follower's option value at X_F* equals the NPV at the trigger (by smooth pasting), which equals b(K_F)/(β_H − 1) from Step 2 of the Proposition 1 proof. Showing the former exceeds the latter would complete the argument.

(b) **Uniqueness.** Computational verification on a 500-point grid is adequate for a working paper but not for a top journal. The concern is not the grid resolution but the dimensionality: uniqueness is verified "across all parameterizations tested," but the parameter space is at least 6-dimensional (σ, α, γ, λ, ℓ, and the rival's strategy). How systematically is this space explored? A Sobol or Latin hypercube sampling scheme, with the number of configurations tested reported explicitly, would be more convincing. Alternatively, the paper could derive analytical sufficient conditions for single crossing—even if they require strong assumptions—as a complement to the numerical verification.

(c) **Part (v): Credit spread increasing in λ.** The stated mechanism is that "X_P decreases faster than X_D because the preemption incentive is amplified by the training channel." This is an important claim but lacks quantitative support in the proof. Reporting the elasticities ε_{X_P,λ} and ε_{X_D,λ} at baseline would help the reader verify that the trigger effect indeed dominates.

### 4.4 Numerical Finding 2 (Dario's dilemma)

The decomposition into timing, capacity, and training allocation channels is well done. The observation that K* is independent of λ (so the capacity channel contributes zero asymmetry) is a clean simplification that the paper should emphasize more. The key driver of the asymmetry—that A_eff is more steeply curved on the under-training side due to the concavity of A_eff in φ and the dominance of the H-regime term—is clearly explained.

However, the claim that "underinvestment is costlier in expected value" while "overinvestment carries substantially higher tail risk" is potentially confusing. The paper reports that a conservative firm (λ_invest = 0.02) loses ~25% of value while an aggressive firm (λ_invest = 0.20) loses only ~5%. But at λ_invest = 0.50, the loss is ~20%—not far from the conservative case. The asymmetry is therefore sensitive to the range of λ_invest considered. Figure 10 shows that for very high λ_invest (> 0.35), the overinvestment loss *exceeds* the underinvestment loss at the symmetric point. The paper should be more precise about the region in which the asymmetry holds and where it reverses.

## 5. Calibration

The calibration is ambitious and largely successful at grounding the model in observable data. Several concerns:

**Training fraction estimates.** The φ̂ values carry ±0.10 uncertainty by the paper's own admission, yet they enter the implied-belief inversion nonlinearly (Table 7 reports an elasticity of ε_{φ*,λ} = +12.7). This means small errors in φ̂ produce large errors in implied λ. The paper should report the implied-λ confidence intervals corresponding to φ̂ ± 0.10 for each archetype.

**Revenue elasticity α.** This parameter does substantial work: it governs diminishing returns in both the production function and the contest function, and the sensitivity analysis (Table 7) shows it is the second-most influential parameter (ε_{X*,α} = +17.9, ε_{K*,α} = +19.9). The calibration to α = 0.40 is described as reflecting "GPU utilization rates" and "diminishing marginal compute value," but these are only loosely linked to the contest function's α. The scaling laws literature (Kaplan et al., 2020; Hoffmann et al., 2022) provides power-law exponents for loss as a function of compute, not for revenue as a function of capacity in a Tullock contest. The mapping from scaling law exponents to α should be made explicit.

**Demand process.** The use of a common σ across regimes is a simplification. In practice, demand volatility is likely higher in the L-regime (where AI capabilities are uncertain) than in the H-regime (where transformation is realized). Allowing σ_L ≠ σ_H would change the characteristic roots and potentially affect the faith-based survival condition. This is a natural robustness check.

**WACC variation.** The archetype WACCs range from 0.10 (Google-like) to 0.18 (xAI-like), and the sensitivity analysis shows r has the highest elasticity for both trigger and capacity (ε_{X*,r} = −20.8, ε_{K*,r} = −25.1). This means the cross-sectional variation in investment behavior is driven as much by differences in the cost of capital as by differences in λ-beliefs. The paper should decompose the archetype variation into a λ-driven component and an r-driven component to clarify which channel matters more quantitatively.

## 6. Exposition and Presentation

The paper is generally well-written and the exposition is clear. Some suggestions:

(a) The paper is long (65 pages with appendices). For a Journal of Finance submission, the main text should be tightened. The institutional material in Sections 1 and 3 is engaging but could be condensed. The detailed discussion of each archetype's revenue and CapEx data (Section 3.3) is valuable but could be moved to an online appendix with a summary in the main text.

(b) Table 4 (analytical status of results) is an excellent addition and unusually transparent. Consider moving it earlier (e.g., after Proposition 3) rather than burying it in the Appendix.

(c) The notation is mostly clean but the use of β_H for the positive characteristic root of the H-regime ODE and β_s^− for the negative root of the regime-s ODE is potentially confusing given that β is also the standard symbol for market beta in the testable predictions discussion (Section 5.2). Distinguish these symbols.

(d) Figure 10 (Dario's dilemma) is the paper's key figure and should appear more prominently. The current figure only shows λ_true = 0.10; a panel showing multiple λ_true values (e.g., 0.05, 0.10, 0.30) would reveal how the asymmetry varies with the firm's true beliefs and strengthen the generality of the result.

(e) The paper title is attention-grabbing but may draw resistance from referees who find the AGI framing speculative. Consider a subtitle that signals the corporate finance contribution more clearly (e.g., "Real Options, Training Allocation, and Default Risk in AI Infrastructure Investment").

## 7. Minor Issues and Typos

(a) Equation 6: the derivation of A_eff is stated without proof. While it is straightforward (capitalize L-regime flow at rate r − μ_L + λ, then add the expected H-regime continuation), a one-line derivation would help readers unfamiliar with regime-switching present values.

(b) Section 2.4.1: the Tullock specification is said to produce total industry revenue that "can exceed the symmetric benchmark." The paper notes this is a potential concern for growing markets but does not quantify the overshoot. A numerical bound at the calibration would be useful.

(c) Section 3.4: the baseline duopoly results report X_F ≈ 0.57 and K_F ≈ 1.30, which differ from the single-firm results (X* ≈ 0.0047, K* ≈ 0.0067) by orders of magnitude. This is presumably due to the Tullock contest splitting revenue, but the jump is jarring and deserves brief comment.

(d) The paper uses both "transformative AI" and "AGI" interchangeably. These have different connotations in the AI safety literature. The paper should pick one or define the distinction.

(e) Footnote 12 (Section 2.1) on the risk-adjusted framework is dense and important. Consider elevating the key point—that μ_s is already risk-adjusted and r is the WACC—into the main text at first use.

(f) Section 4.2.2: the default probability formula uses the first-passage probability for standard GBM, but the demand process has regime switching. The paper states this uses the "risk-adjusted drift," yielding a risk-neutral default probability. This is correct under the A_eff approximation but should note that the regime switch introduces an additional source of approximation error: the actual first-passage time depends on which regime the process is in.

(g) Appendix E references robustness under Cournot competition but provides no details beyond the assertion that "main qualitative results are preserved." For a top journal, at least one key result (e.g., the faith-based survival condition) should be re-derived under Cournot in the appendix.

## 8. Overall Assessment

This is a strong paper that tackles an important and timely problem with a well-constructed model. The training-inference allocation mechanism is genuinely novel and economically significant. The calibration, while necessarily stylized, is carefully done and transparently presented. The main weaknesses are (i) the static φ assumption, whose quantitative implications for the headline results remain unbounded; (ii) the reliance on computational verification for key results (Proposition 3(ii), uniqueness of X_P) that a top journal will want at least partially elevated to analytical results; and (iii) the calibration's sensitivity to α and φ̂, which needs more thorough exploration. Addressing these issues—particularly through a formal two-period dynamic-φ extension and sharper analytical characterization of the duopoly equilibrium—would make this paper suitable for a top finance journal.
