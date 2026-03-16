# Review Report: AI Lab Investment

**Reviewer:** Claude Opus 4.6
**Date:** 2026-03-13

## Executive Summary

This review covers both the codebase and the accompanying paper "Investing in Artificial General Intelligence" by Vincent Gregoire (HEC Montreal). The project develops a real-options model of irreversible capacity investment for frontier AI laboratories, featuring regime-switching demand, duopoly preemption, endogenous default risk, and a novel training-inference allocation decision.

**Code assessment.** The codebase is well-structured, with clean separation between model layers (`parameters.py` -> `base_model.py` -> `duopoly.py` -> `valuation.py`). All 190 tests pass. The core mathematical implementations faithfully reproduce the paper's formulas, with two notable exceptions: (1) an inconsistency in the default probability computation within `dario_dilemma_leveraged()` (uses a simplified one-term formula vs. the correct two-term first-passage formula used elsewhere), and (2) a discrepancy between the paper's stated default probability values and the code's actual output for the credit risk figure. Additional issues include a figure axis mislabel ("Depreciation" instead of "Operating cost"), an untested central function (`dario_dilemma_leveraged()`), and a text-table sign discrepancy for the discount rate comparative static. Overall, the code is correct and well-tested, with these issues being localized and fixable.

**Paper assessment.** The paper makes a genuine and novel contribution by integrating training-inference allocation into a real-options/strategic-investment/structural-credit framework. The writing is clear, the model progression is well-motivated, and the calibration is carefully sourced. The paper is near submission-ready for a top finance journal, pending resolution of several issues: the abstract slightly mischaracterizes the main Dario's dilemma finding, certain numerical claims in the text don't match current code output, and the proofs could be tightened in places. The best target journal is the Review of Financial Studies (RFS).

---

## Part 1: Code Validation

### 1. Mathematical Correctness

#### Propositions vs. Code

**Proposition 1 (Optimal K*, phi*) — PASSES.**

- **K* formula** (paper `_model.qmd`:131): $K^* = \left[\frac{\delta(\alpha\beta_H - \beta_H + 1)}{rc(\gamma(\beta_H-1) - \alpha\beta_H)}\right]^{1/(\gamma-1)}$. The code does not use this closed-form directly; instead, `base_model.py:497-544` (`optimal_trigger_capacity_phi`) uses numerical Nelder-Mead optimization over `(log_K, phi)` to maximize `h(K, phi) = A_eff^{beta_H} / cost^{beta_H-1}`. This is mathematically equivalent. Verified numerically: the code produces K*=0.0067 at baseline, consistent with the paper.

- **K* independence from phi**: The paper proves this via the factorization $A_{\text{eff}} = g(\phi) \cdot K^\alpha$. In the code, the joint Nelder-Mead optimization does not exploit this separability but produces the correct result numerically: K*=0.0067 is constant across all tested lambda values (0.02, 0.10, 0.20, 0.50), confirming independence. The test suite verifies this property in `test_base_model.py`.

- **phi* interiority and uniqueness**: The paper's proof via Inada conditions and strict concavity of $A_{\text{eff}}$ in phi is correct (`_appendix.qmd`:71-98). The code's Nelder-Mead with multi-start (12 starting points: 3 log_K values x 4 phi values) reliably converges to phi*=0.701 at baseline.

- **Investment trigger** (`_model.qmd`:183): $X^* = \frac{\beta_H}{\beta_H-1} \cdot \frac{\delta K^*/r + c(K^*)^\gamma}{A_{\text{eff}}(\phi^*, K^*)}$. Code at `base_model.py:539-541` computes this exactly. Verified: X*=0.0047 at baseline.

- **Comparative statics** (phi* increasing in lambda, decreasing in L-regime premium): Verified numerically. At lambda=0.02, phi*=0.138; at lambda=0.50, phi*=0.972 — monotonically increasing, as claimed.

**Proposition 2 (Default boundary, faith-based survival) — PASSES with one caveat.**

- **Default boundary formula** (`_model.qmd`:261): $X_D = \frac{\beta_s^-}{\beta_s^- - 1} \cdot \frac{c_D/r + \delta K_i/r}{A_{\text{eff},i}}$. Code at `duopoly.py:346-351` matches exactly.

- **Negative root computation** (`duopoly.py:353-370`): Correctly solves the quadratic $\frac{1}{2}\sigma^2\beta(\beta-1) + \mu_L\beta - (r+\lambda) = 0$ and returns the negative root. Uses the correct effective discount rate $r + \lambda_{\text{tilde}}$.

- **Proposition 2(ii) proof** (`_appendix.qmd`:119-143): The two-channel decomposition (beta-channel and A_eff-channel) is complete. The proof correctly identifies that the A_eff-channel dominates when the faith condition holds. The closed-form threshold $\underline{\phi} = R/(1+R)$ with $R = ((r-\mu_H)/(r-\mu_L))^{1/\alpha}$ is verified: R=0.22, $\underline{\phi}$=0.18 at baseline.

- **Caveat**: The proof of Proposition 2(ii) states "the beta-channel is approximately 52% of the A_eff-channel in absolute magnitude" at baseline. This specific numerical claim is not directly verifiable from the code without additional computation, but the overall sign (net negative) is verified by the monotonicity tests.

**Proposition 3 (Preemption equilibrium) — PASSES.**

- **Existence** (IVT argument in `_appendix.qmd`:155-164): The boundary conditions $L(0) < F(0)$ and $L(X_F^*) > F(X_F^*)$ are correctly argued. The code implements Brent's root-finding in `duopoly.py:828-834`.

- **Uniqueness**: Verified computationally (stated as such in the paper). The code doesn't verify single-crossing on a 500-point grid as described in Appendix B, but Brent's method assumes a single root in the bracket, and no convergence failures are reported across test cases.

- **phi_L >= phi_F**: At baseline zero-leverage, both phi_L and phi_F equal 0.701 (symmetric). The analytical motivation (monopoly-phase lower marginal cost of training) is economically sound.

- **Numerical results match**: X_F=0.574, K_F=1.302, X_leader=0.0082, X_leader_monopolist=0.0163. All match paper claims exactly.

#### Two Model Modes

- **Simple mode** (`installed_value()`, `optimal_trigger_and_capacity()`): Uses combined A_L/A_H from `parameters.py`. Used for H-regime analysis and Figures 1-4.
- **Full mode** (`optimal_trigger_capacity_phi()`, `installed_value_with_phi()`): Uses `_effective_revenue_coeff_single()` matching @eq-a-eff. Used for all paper results and duopoly.
- **Internal consistency**: Both modes are internally consistent. The simple mode H-regime solution coincides with the full mode when phi is set to match the H-regime revenue structure. The paper correctly uses the full mode for all reported results in the calibration and valuation sections.

#### Regime Switching

- **GBM simulation** (`base_model.py:327-372`): Correctly implements Euler-Maruyama with regime-dependent drift, common volatility, and Poisson regime switching. The absorbing-state assumption (H never switches back to L) is correctly handled at line 370.
- **Characteristic roots** (`parameters.py:238-247`): `_positive_root()` correctly solves the quadratic. Verified: beta_H=1.553, beta_L=3.015 at baseline.
- **A_L computation** (`parameters.py:134-139`): $A_L = (r - \mu_H + \lambda)/[(r-\mu_H)(r-\mu_L+\lambda)]$ when lambda > 0. This is the present-value multiplier combining both regime revenues. Matches paper.

#### Default Probability — HAS ISSUES

- **Main `default_probability()` method** (`valuation.py:149-213`): Correctly implements the two-term first-passage formula:
  $P = \Phi(-d_1) + (X_D/X)^{2\nu/\sigma^2}\Phi(-d_2)$
  where $\nu = \mu - \sigma^2/2$, $d_1 = [\ln(X/X_D) + \nu T]/(\sigma\sqrt{T})$, $d_2 = [\ln(X/X_D) - \nu T]/(\sigma\sqrt{T})$. Matches `_valuation.qmd`:65-68 exactly.

- **`dario_dilemma_leveraged()` helper** (`valuation.py:402-409`): Uses only the first term $\Phi(-d_1)$, omitting the reflection term $(X_D/X)^{2\nu/\sigma^2}\Phi(-d_2)$. This understates default probability by approximately 47% at baseline parameters. The paper text (`_valuation.qmd`:119-120) cites the correct full first-passage values (0.79% for conservative, 5.04% for aggressive at leverage=0.40), which must have been computed separately from this helper. **This is a code inconsistency** — the helper function returns different values than what the paper reports.

#### Parameter Consistency — HAS ISSUES

- **Baseline parameters**: `parameters.py` defaults match `_appendix.qmd` @tbl-parameters exactly: r=0.12, mu_L=0.01, mu_H=0.06, sigma=0.25, alpha=0.40, gamma=1.50, c=1.0, delta=0.03, lam=0.10. **PASSES.**

- **Baseline results**: Code output matches paper claims in @tbl-baseline-results: K*=0.0067, phi*=0.70, X*=0.0047, beta_L=3.01, beta_H=1.55, phi_underbar=0.18. **PASSES.**

- **Credit risk values** — **DISCREPANCY**: The paper (`_valuation.qmd`:73-74) states default probability "rises from approximately 0.5% at low leverage to approximately 0.8% at ell = 0.70." However, the code's `credit_spread_curve()` produces:
  - ell=0.05: 0.17% (paper claims ~0.5%)
  - ell=0.20: 0.57%
  - ell=0.70: 2.91% (paper claims ~0.8%)

  The discrepancy arises because the code uses `max(X_D * 3, 0.1)` as the evaluation point (`valuation.py:137, 241`), creating a floor at X=0.1. At low leverage, the effective distance-to-default is ~5x (not 3x), suppressing the probability. At high leverage, the distance is exactly 3x, giving 2.91%. The paper's caption ("evaluated at a demand level three times the default boundary") is therefore inaccurate for low leverage levels. Moreover, at exactly 3x X_D, the default probability is identically 2.91% for ALL leverage levels (since the drift, vol, and distance-to-default ratio are constant), which contradicts the paper's claim that it varies. **The paper text needs correction.**

  Credit spreads match: 170/259/308 bps at ell=0.05/0.20/0.70. **PASSES.**

- **Dario's dilemma values**: lambda_invest=0.02 gives 26.2% loss (paper says "approximately 25%"); lambda_invest=0.20 gives 5.6% (paper says "about 5%"). **PASSES** (within rounding).

#### Numerical Methods

- **Nelder-Mead multi-start** (`base_model.py:515-529`, `duopoly.py:592-608`): 12+ starting points with tolerance 1e-8/1e-10. Convergence is reliable for all baseline tests.
- **Brent's root-finding** (`duopoly.py:828-834`, `revealed_beliefs.py:121`): Tolerance 1e-10 for preemption trigger, 1e-6 for belief inversion. Appropriate for the problem scales.
- **Bounded scalar optimization** (`base_model.py:133-138`): `minimize_scalar` with bounds (-15, 15) in log-K space. The bounds are generous enough to avoid truncation.
- **Phi bounds**: Hard-coded [0.01, 0.99] with penalty-based enforcement (returning 1e20 for out-of-bounds). Not ideal — proper box constraints would be more robust — but works in practice because the optimum is interior.

### 2. Code Quality and Testing

#### Test Coverage

Overall coverage: **45%** (2481 statements, 1358 missed). Breakdown:

| Module | Coverage | Notes |
|--------|----------|-------|
| `base_model.py` | 89% | Good coverage of core functions |
| `duopoly.py` | 85% | Most equilibrium paths covered |
| `parameters.py` | 76% | Some validation branches uncovered |
| `valuation.py` | 74% | `dario_dilemma_surface`, some credit functions uncovered |
| `revealed_beliefs.py` | 86% | Some edge-case branches uncovered |
| `symbolic_duopoly.py` | 83% | Verification functions partially covered |
| `figures/*.py` | 0% | Not tested (figure generation) |
| `pipeline.py` | 0% | Not tested (orchestrator) |
| `utils/*.py` | 0% | Not tested (file utilities) |

**Assessment**: Coverage is adequate for the core model code (74-89%). The 0% coverage on figure generation is not unusual for academic research code but means figure correctness relies entirely on visual inspection. The pipeline and utility code being untested is acceptable given their simplicity.

#### Test Meaningfulness

**Strengths:**
- Tests check economically meaningful properties: option values are positive, triggers decrease with volatility, K* is independent of phi, default boundary below investment trigger.
- Comparative statics tests verify correct signs (e.g., trigger increases with sigma).
- Regression tests pin specific numerical values at baseline parameters.
- The test suite includes symbolic verification via `test_symbolic_duopoly.py`.

**Weaknesses:**
- Limited edge-case testing: no tests for lambda=0 behavior in the phi-aware model, no tests for sigma near zero, no tests for extreme leverage (>0.90).
- No convergence stress tests for the Nelder-Mead optimizer.
- The `dario_dilemma_leveraged()` default probability inconsistency is not caught by any test (no test compares its output against `default_probability()`). In fact, `dario_dilemma_leveraged()` has **zero test coverage** despite computing the paper's central leveraged dilemma results.
- K* independence from phi — a known prior bug location (see revision history) — lacks an explicit regression test.

#### Numerical Stability

- Division-by-zero guards exist in `parameters.py` (validation), `base_model.py:107-108` (return 1e20 for invalid K), and `duopoly.py:184-185` (return 0 for non-positive denominator).
- Overflow protection via log-space optimization for K.
- No explicit guard against the case where `_effective_revenue_coeff_single` returns exactly 0 when computing the trigger (division by a_eff at `base_model.py:541` — protected by `if a_eff > 0` check).

#### Code Organization

**Strengths:**
- Clean model hierarchy with single responsibility per module.
- Clear separation between simple and full model modes.
- Figures computed in `paper.py`, rendered in `generate_figures.py` — no logic duplication.
- Caching in all model classes prevents redundant computation.

**Weaknesses:**
- The `dario_dilemma_leveraged()` function in `valuation.py:343-425` duplicates the default probability logic with a simplified formula instead of calling `self.default_probability()`. This violates DRY and introduced the inconsistency noted above.
- Some legacy methods (`contest_share`, `duopoly_revenue_pv`, `monopolist_revenue_pv` in `duopoly.py`) are preserved for backward compatibility but are not used by the paper code. They add code surface without testing.

#### Reproducibility

- Random seeds are set (rng=42) in the sample paths figure.
- All other computations are deterministic (optimization with fixed starting points).
- The pipeline can be run via `just run-pipeline`.
- Hydra configuration in `conf/config.yaml` provides reproducible parameter management.

---

## Part 2: Paper Review

### 3. Paper Content Review

#### 3a. Structure and Argument

**Motivation — PASSES.** The introduction effectively establishes the economic significance ($200B+ committed in 2024, $500B Stargate), the fundamental uncertainty (executive timeline estimates ranging from 2026 to "not with current architectures"), and the theoretical gap (no existing model integrates training-inference allocation with investment timing, strategic competition, and default risk). The opening paragraph immediately places the reader in the problem space. The executive quotes (Pichai, Huang, Amodei, Altman) are well-chosen and grounded.

**Literature positioning — PASSES.** The literature review (`_literature.qmd`) covers all major building blocks: real options (McDonald & Siegel, Dixit & Pindyck, Guo et al.), strategic investment (Grenadier, Huisman & Kort), R&D races (Loury, Reinganum, Harris & Vickers), structural credit (Leland, Merton), and AI economics (Kaplan et al., Hoffmann et al.). The marginal contribution statement is precise and convincing. One potential addition: the paper could cite @philippon2009bond (bond market and macroeconomic investment) for the credit-risk/investment-timing interaction.

**Model building — PASSES.** The progression from environment to single firm to duopoly is natural and well-motivated. Each layer adds one dimension: the single-firm model introduces the training-inference allocation; the duopoly adds competition and preemption; leverage and default add credit risk. The reader is never overwhelmed.

**Duopoly justification — PASSES.** The duopoly focus is justified at `_introduction.qmd`:31-34 by the observation that frontier AI training is highly concentrated. The footnote mentions Bouis et al. (2009) for N-firm extensions. This is adequate.

**Assumptions A1-A4 — PASSES.** All assumptions are stated clearly in `_model.qmd`:115-126 with economic content explained. A3 (L-regime insufficiency) is the most restrictive; the paper verifies it at baseline and across the sensitivity range, and discusses what happens when it fails (Appendix B). A2 boundary failures at extreme WACCs are documented.

**Conclusion — PASSES.** Appropriately scoped; lists limitations honestly; suggests concrete future directions (dynamic phi, financial frictions, formal revealed beliefs methodology). Does not overclaim.

#### 3b. Writing Quality

**Clarity — PASSES with minor issues.**
- The paper is well-written overall, with clear exposition.
- The term "faith-based survival" is vivid and memorable. Some referees may find it too colloquial for a top journal; "continuation-value survival" would be more formal but less distinctive.
- The Remark on nesting (`_model.qmd`:86-89) is helpful for understanding limiting cases.
- Minor: The phrase "purpose-built GPU clusters housed in multi-billion-dollar data centers" appears in both the introduction and the technology section — consider trimming one occurrence.

**Notation — PASSES.** Consistent throughout. All symbols defined before use (see @tbl-notation). The distinction between phi (training fraction) and Phi (option premium ratio) is maintained by using different fonts/cases. The subscript convention (L/H for regimes, i/j for firms) is standard.

**Length and focus — PASSES.** The paper is appropriately scoped. The main text covers the core model, calibration, and quantitative implications without padding. Technical details are correctly relegated to appendices. The discussion section is focused and honest about limitations.

**Abstract — HAS ISSUES.** The abstract states: "An asymmetric dilemma arises in which aggressive overinvestment carries higher downside risk than conservative underinvestment." This emphasizes the tail-risk dimension of Dario's dilemma. However, the paper's central finding (Numerical Finding 2) is that **underinvestment is costlier in expected value** while overinvestment carries higher default risk. The abstract should lead with the expected-value asymmetry and then note the tail-risk qualifier. The current phrasing could lead a reader to conclude the paper argues against aggressive investment, when the main message is more nuanced. Suggested revision: "An asymmetric dilemma arises: conservative underinvestment is costlier in expected value, but aggressive overinvestment carries substantially higher tail (default) risk."

#### 3c. Journal Fit

**Contribution significance — PASSES.** The training-inference allocation under regime-specific competition is a genuine theoretical novelty. The faith-based survival mechanism and Dario's dilemma are new results that no subset of existing models can generate. The calibration to AI lab archetypes is timely and empirically grounded.

**Methodological rigor — PASSES.** The paper meets top-journal standards: analytical results where possible (Propositions 1-2), honest labeling of computational results (Proposition 3, Numerical Finding 2), comprehensive robustness checks (Appendix B, D, E), and careful discussion of limitations.

**Formatting and conventions — PASSES.** The paper follows Econometrica/JF conventions: numbered propositions with proofs, precise assumption statements, separated appendices for proofs and numerical details.

**Recommended target journal: Review of Financial Studies (RFS).** The paper's core contribution is at the intersection of corporate finance (investment under uncertainty, structural credit risk) and industrial organization (strategic preemption). RFS has a strong tradition in real options and strategic investment (Grenadier 2002 was published there). The AI application provides timeliness. The paper is somewhat long for JF (which favors shorter, more focused papers) and is more applied than Econometrica typically publishes (Econometrica would require stronger analytical results — e.g., analytical uniqueness of the preemption equilibrium). RFS's tolerance for computational results with analytical motivation makes it the best fit.

### 4. Figures

#### Review of All 11 Figures

**Figure 1 (fig_sample_paths) — PASSES.** Five GBM paths with L->H switch, correctly simulated with fixed seed (42). Uses simple-mode trigger for annotation. The trigger value shown ($X_H^*$) differs from the full-model $X^*$ reported in the paper, which could confuse careful readers, but the figure correctly labels it as $X_H^*$ (H-regime simple mode).

**Figure 2 (fig_option_value) — PASSES.** Option value vs. NPV with value-of-waiting shading. Smooth-pasting visually confirmed at the trigger. Correct use of simple mode for H-regime illustration.

**Figure 3 (fig_comparative_statics) — HAS ISSUE.** Panel (d) axis label reads "Depreciation $\delta$" (`paper.py`:153). The paper (`_model.qmd`:56, `_calibration.qmd`:35) explicitly distinguishes $\delta$ (operating cost rate) from depreciation: "This is distinct from economic depreciation." The figure label should read "Operating cost $\delta$" to match the paper. This is a **labeling error** that contradicts the text.

**Figure 4 (fig_lambda_option_value) — PASSES.** Two panels correctly show F_L increasing in lambda and C coefficient increasing in lambda. F_H plotted as constant horizontal line (correct, since it's lambda-independent).

**Figure 5 (fig_default_boundaries) — PASSES.** Follower trigger, leader trigger, and default boundary vs. leverage. Correctly computed from `solve_preemption_equilibrium`. Dictionary keys match correctly.

**Figure 6 (fig_credit_risk) — HAS ISSUE.** Credit spreads are correctly computed (170/259/308 bps). However, the default probability panel does not match the paper's text claims (see Mathematical Correctness section above). The `max(X_D * 3, 0.1)` floor in `credit_spread_curve()` creates an inconsistent distance-to-default across leverage levels, and the paper's claim that default probability "rises from approximately 0.5% to approximately 0.8%" is not reproduced by the current code.

**Figure 7 (fig_competition_effect) — PASSES.** Monopolist vs. duopoly leader trigger over sigma. Correctly shows preemption compressing the leader's trigger.

**Figure 8 (fig_firm_comparison) — PASSES.** Two panels: broken-axis CapEx/Revenue bar chart (handling xAI outlier well) and revenue-growth vs. leverage scatter. Data sourced from `get_baseline_calibration()`. Publication quality with good design choices.

**Figure 9 (fig_lambda_timeline) — PASSES.** Pure analytical computation (1/lambda, 1-exp(-5*lambda)). No model code involved. Correct.

**Figure 10 (fig_growth_decomposition) — PASSES.** Uses full model (`optimal_trigger_capacity_phi`, `installed_value_with_phi`). Correctly decomposes into assets-in-place and capacity gap value. Evaluated at 1.5*X_star.

**Figure 11 (fig_investment_dilemma) — PASSES.** Dario's dilemma value loss for leveraged and unleveraged cases. Correctly delegates to `ValuationAnalysis.dario_dilemma()` and `dario_dilemma_leveraged()`. The unleveraged curve shows clear asymmetry (steeper left branch).

#### Code-Figure Consistency (Spot Checks)

1. **Figure 3 -> `SingleFirmModel.comparative_statics`**: Traced from `paper.py:162` through `base_model.py:285-325`. The function correctly creates new `ModelParameters` via `with_param()` for each parameter value and calls `optimal_trigger_and_capacity("H")`. **Correct pipeline.**

2. **Figure 6 -> `ValuationAnalysis.credit_spread_curve`**: Traced from `paper.py:335` through `valuation.py:215-252`. Loops over leverage values, computes spread via `credit_spread()` and default probability via `default_probability()`. The default probability evaluation uses `max(X_D * 3, 0.1)`, creating the floor issue noted above. **Pipeline correct; evaluation-point issue exists.**

3. **Figure 11 -> `ValuationAnalysis.dario_dilemma` and `dario_dilemma_leveraged`**: Traced from `paper.py:599-606` through `valuation.py:258-425`. The unleveraged function correctly evaluates mismatched policies under the true demand process with timing discount. **Pipeline correct.**

### 5. Calibration and Results

#### Parameter Values

- **Demand process**: mu_L=0.01, mu_H=0.06, sigma=0.25. Well-sourced from cloud revenue growth rates and quarterly volatility. The common volatility assumption (sigma_L = sigma_H = sigma) is a simplification noted in the revision history.

- **Technology**: alpha=0.40, gamma=1.50. Alpha motivated by GPU utilization rates and diminishing marginal compute value. Gamma motivated by power/supply-chain bottlenecks. Both are "Chosen" parameters (not estimated), which is appropriate for a theoretical paper with stylized calibration.

- **Financial**: r=0.12 (WACC), delta=0.03 (operating cost), c_d=0.05 (coupon), b=0.30 (bankruptcy cost). The WACC is well-justified by CAPM estimates for frontier AI labs. Bankruptcy cost of 30% is standard (Andrade & Kaplan 1998).

- **Training fractions**: Hat-phi values (0.35-0.75 across archetypes) are carefully triangulated from Amodei's statements, Epoch AI's OpenAI decomposition, and Deloitte's TMT Predictions. The $\pm$0.10 uncertainty band is honestly disclosed.

**Assessment: PASSES.** Parameter choices are reasonable and well-sourced for a stylized calibration. The paper is clear that this is illustrative, not structural estimation.

#### Sensitivity

The paper provides comprehensive sensitivity analysis:
- @tbl-elasticities reports elasticities of X*, K*, phi* to all 7 parameters.
- The elasticity table reveals that r and alpha are the most influential parameters, which is economically sensible.
- Appendix E verifies robustness to $\pm$25% parameter perturbation, alternative contest functions (Cournot), and alternative regime structure (3-regime).

**Assessment: PASSES.** Sensitivity analysis is thorough and well-presented.

#### Comparative Statics

All reported comparative statics are consistent with economic intuition:
- Higher sigma raises trigger (standard real-options result). **Correct.**
- Higher lambda lowers trigger and raises phi* (more optimistic -> invest sooner, train more). **Correct.**
- Higher r raises trigger (higher cost of waiting). **DISCREPANCY** — the calibration text states higher r "raises the investment trigger," but `@tbl-elasticities` reports $\varepsilon_{X^*}(r) = -20.8$, implying the opposite. See Major Issue #5.
- Higher leverage lowers follower trigger (risk-shifting effect). **Correct.**

**Assessment: PASSES with one discrepancy** (discount rate sign — see Major Issue #5).

#### Dario's Dilemma Results

- **Value losses**: lambda_invest=0.02 gives 26.2% loss (paper: "approximately 25%"); lambda_invest=0.20 gives 5.6% (paper: "about 5%"); lambda_invest=0.50 gives 22.6% (paper: "approximately 20%"). The 22.6% vs. "approximately 20%" for extreme overinvestment is the largest discrepancy but within the "approximately" qualifier. **PASSES.**

- **Taylor expansion sign argument** (`_appendix.qmd`:192-210): The argument that W''' > 0 (making underinvestment costlier) is heuristic, as the paper acknowledges. The three channels (capacity, timing, training allocation) are correctly identified, with the training allocation channel identified as dominant (since K* is independent of lambda, the capacity channel contributes zero asymmetry). The sign is verified numerically. **PASSES.**

- **Leveraged default probabilities**: The paper cites 0.79% (conservative, lambda=0.02) and 5.04% (aggressive, lambda=0.50) at leverage=0.40. I verified these match the **full first-passage formula** but NOT the `dario_dilemma_leveraged()` helper's simplified formula (which gives 0.42% and 2.69%). The paper text is correct; the code helper is inconsistent. See Critical Issues below.

#### Growth Decomposition

The decomposition into assets-in-place and capacity gap value (`valuation.py:490-536`) correctly uses the phi-aware model. The claim that the capacity gap accounts for 60-80% of firm value for K/K* << 1 is consistent with the figure output. **PASSES.**

---

## Summary of Issues

### Critical Issues

1. **Default probability text-code discrepancy** (`_valuation.qmd`:73-74 vs. `valuation.py:215-252`). The paper claims 5-year default probability "rises from approximately 0.5% at low leverage to approximately 0.8% at ell = 0.70." The code produces 0.17% to 2.91%. Neither the paper's stated values nor the code's behavior match a consistent evaluation at "three times the default boundary." **Fix**: Either (a) remove the `max(..., 0.1)` floor in `credit_spread_curve()` and `credit_spread()`, using exactly `3 * X_D` for all leverage levels (but then default probability is constant across leverage), or (b) use a fixed absolute demand level and update the paper text to state the correct evaluation point and values.

2. **`dario_dilemma_leveraged()` default probability formula** (`valuation.py:402-409`). Uses only $\Phi(-d_1)$ (one term) instead of the full first-passage formula $\Phi(-d_1) + (X_D/X)^{2\nu/\sigma^2}\Phi(-d_2)$. This understates default probability by ~47%. The paper's text cites the correct full-formula values, creating an inconsistency between the function's output and the paper. **Fix**: Replace the inline `_default_prob` helper with a call to `self.default_probability()` from the same class.

### Major Issues

3. **Abstract mischaracterization** (`index.qmd`:23). The abstract says "aggressive overinvestment carries higher downside risk than conservative underinvestment," emphasizing only the tail-risk dimension. The paper's central finding is that underinvestment is costlier in expected value while overinvestment carries higher default risk. **Fix**: Revise to "conservative underinvestment is costlier in expected value, but aggressive overinvestment carries substantially higher tail (default) risk."

4. **Figure 3 axis label** (`paper.py`:153). Panel (d) labels delta as "Depreciation $\delta$", but the paper explicitly states delta is the operating cost rate, distinct from depreciation. **Fix**: Change to `r"Operating cost $\delta$"`.

5. **Discount rate comparative static sign discrepancy** (`_calibration.qmd`:~115 vs. `@tbl-elasticities`). The calibration text states that a higher discount rate r "raises the investment trigger," but the elasticity table reports $\varepsilon_{X^*}(r) = -20.8 < 0$, implying a higher r **lowers** the trigger. The negative elasticity arises because in the full phi-aware model, higher r changes both the option premium ratio ($\beta_H/(\beta_H-1)$) and the effective revenue coefficient $A_{\text{eff}}$ through $A_L$, $A_H$, and the optimal phi — the indirect channels can dominate. The text should be corrected to match the elasticity table, or the discrepancy should be explained.

6. **`dario_dilemma_leveraged()` entirely untested** (`valuation.py`:343-425). This function — which computes the paper's central leveraged Dario's dilemma results including default probabilities at `_valuation.qmd`:117-125 — has no test coverage whatsoever. The simplified default probability formula (Critical Issue #2) would have been caught by even a basic regression test. **Fix**: Add tests that (a) verify output at baseline parameters, (b) compare the internal default probability against `self.default_probability()`, and (c) check that value losses are non-negative.

### Minor Issues

7. **K* independence from phi not regression-tested.** The separability K*⊥phi (Proposition 1's key analytical result, and a known prior bug location per the revision history) is verified indirectly via comparative statics, but no test explicitly checks that K* is invariant across a range of phi or lambda values. A regression test pinning K*=0.0067 across lambda ∈ {0.02, 0.10, 0.20, 0.50} would guard against regressions in the Nelder-Mead joint optimization.

8. **`generate_figures.py` PNG style** (line 74): Uses `seaborn-v0_8-paper` for PNG rendering, not `seaborn-v0_8-talk` as the docstring claims. The override dicts are identical anyway, so no visual difference. **Fix**: Change line 74 to use `seaborn-v0_8-talk` for consistency with the docstring.

9. **Figure 3 alpha range** (`paper.py`:150): Uses [0.30, 0.45], narrower than the calibration range [0.20, 0.60]. Consider widening to show the full sensitivity range.

10. **Figures 1-2 use simple mode**: The sample paths and option value figures use `optimal_trigger_and_capacity("H")` (simple mode, no phi) while the paper's baseline results use the full model. The annotated $X_H^*$ value on these figures differs from $X^*$ in the paper text. This is technically correct (different quantities) but could confuse careful readers.

11. **Figure 10 holds phi at phi\* for all K levels.** The growth decomposition figure evaluates `installed_value_with_phi()` at the globally optimal phi\* even for K values far from K\*. In practice, a firm at K≠K\* might choose a different phi. This is a modeling choice (partial equilibrium decomposition at optimal phi), but it is not documented and could overstate the capacity gap value for small K.

12. **Levered follower trigger formula undocumented.** The code (`duopoly.py`) computes the leveraged follower trigger with $(1-\ell)I(K) + c_D/r$ in the numerator, extending the unlevered formula by adding debt service costs. This correct extension is never stated explicitly in the paper's model section, though it follows from the levered equity value derivation. Consider adding a brief remark.

13. **Legacy code in `duopoly.py`**: Methods `contest_share()`, `duopoly_revenue_pv()`, `monopolist_revenue_pv()` are backward-compatible stubs not used by the paper. They add ~20 lines of untested code surface. Consider removal.

14. **Dario's dilemma lambda=0.50 rounding.** The code computes 22.6% value loss at lambda_invest=0.50, but the paper text says "approximately 20%." While within the "approximately" qualifier, this 2.6pp gap is larger than the rounding tolerance elsewhere in the paper (e.g., 26.2%→"~25%" is 1.2pp). Consider updating to "approximately 23%."

15. **Paper could cite Philippon (2009)** on bond market and macroeconomic investment for the credit-risk/investment-timing interaction.

16. **Repeated phrasing** in introduction and technology section ("purpose-built GPU clusters housed in multi-billion-dollar data centers").

---

## Overall Recommendation

**Revise and resubmit** (minor revision).

The code is fundamentally correct and the paper makes a genuine contribution. The critical issues (default probability text-code discrepancy and the simplified formula in the leveraged Dario helper) are localized bugs that do not affect the paper's main conclusions — the qualitative patterns (asymmetric value loss, monotonicity of spreads) are preserved. The major issues (abstract framing, figure label, discount rate sign discrepancy, untested central function) are all fixable in a focused revision. No issue undermines the paper's core analytical results or economic conclusions.

**Recommended target journal:** Review of Financial Studies (RFS), for the reasons discussed in Section 3c.

**Strengths:**
- Novel mechanism (training-survival channel) that no existing model generates.
- Clean analytical results where possible, honest about computational results.
- Timely calibration to the frontier AI sector.
- Well-structured code with meaningful test suite.
- Careful, precise writing throughout.

**Weaknesses:**
- Duopoly uniqueness is computational, not analytical.
- Static phi assumption limits practical relevance (discussed honestly).
- Some numerical claims in the text don't match current code output.
- Stylized calibration limits empirical testability.
