# Review Report: AI Lab Investment

**Reviewer:** claude_opus
**Date:** 2026-02-25

## Executive Summary

This report reviews both the codebase and the research paper "Investing in Artificial General Intelligence: A Real Options Framework for AI Compute Infrastructure" by Vincent Gregoire (HEC Montreal). The project builds a unified real options model of irreversible AI compute investment with regime switching, duopoly competition, endogenous default risk, and diminishing returns calibrated to AI scaling laws.

**Overall assessment: The code is substantially correct and the paper is near submission-ready for a top finance journal.** All 227 tests pass. The core mathematical implementation (single-firm, duopoly, and valuation) faithfully reproduces the paper's propositions and equations. Every calibrated numerical result reported in the paper matches the code output. The paper is well-written, well-structured, and makes a significant contribution to the real options and AI economics literatures.

That said, the review identifies one substantive paper-code inconsistency (the equity value formula includes a sunk cost term inside the default option bracket that is inconsistent with the stated default boundary), a critical numerical stability issue (the N-firm sequential equilibrium diverges under iterative best-response), and several minor issues. None of these undermine the paper's core results, which rely on the single-firm and duopoly models (both correct), but they should be addressed before submission.

---

## Part 1: Code Validation

### 1. Mathematical Correctness

#### 1.1 Propositions vs. Code

**Proposition 1** (Optimal capacity and training fraction; `_model.qmd`:128-141 vs `base_model.py`):

- [x] **PASS.** The trigger formula in code (`base_model.py`:538-541) exactly matches eq-trigger-phi:
  ```python
  X_star = (beta / (beta - 1.0)) * total_cost / a_eff
  ```
  where `total_cost = delta*K/r + c*K^gamma` and `a_eff` is from `_effective_revenue_coeff_single()`.
- [x] **PASS.** The code uses numerical optimization of `h(K,phi) = A_eff^{beta_H} / cost^{beta_H-1}` (`base_model.py`:495) rather than the closed-form K*(phi). Verified numerically: code produces K*=0.006727, matching the analytical formula exactly.
- [x] **PASS.** Interior phi* verified: the FOC `dA_eff/dphi = 0` is satisfied at phi*=0.7009. Strict concavity confirmed across [0.05, 0.95].
- [x] **PASS.** Comparative statics direction (higher lambda -> higher phi*) matches Prop 1(iii).

**Proposition 2** (Default boundary and faith-based survival; `_model.qmd`:270-283 vs `duopoly.py`):

- [x] **PASS.** Default boundary (`duopoly.py`:346-349) exactly matches eq-default-boundary:
  ```python
  X_D = (beta_neg / (beta_neg - 1.0)) * (c_D / p.r + p.delta * K_i / p.r) / revenue_coeff
  ```
  Verified numerically: X_D = 0.04752 at baseline.
- [x] **PASS.** Faith-based survival threshold eq-phi-underbar: `phi_underbar = R/(1+R)` with `R = ((r-mu_H)/(r-mu_L))^{1/alpha}`. Verified R=0.2197, phi_underbar=0.1801 (paper states ~0.18).
- [x] **PASS.** Rival capacity effect (Prop 2(iv)): contest shares decrease with K_j, lowering A_eff_i, raising X_D. Mechanism correctly captured.
- [ ] **ISSUE** (see Critical Issues below). The equity value formula in the paper (`_model.qmd`:303) includes `(1-ell)I(K)` inside the default option bracket, which is inconsistent with eq-default-boundary. The code (`duopoly.py`:426) correctly excludes it.

**Proposition 3** (Preemption equilibrium; `_model.qmd`:349-361 vs `duopoly.py`):

- [x] **PASS.** Existence: code finds X_P via Brent's method on `_preemption_gap()` (`duopoly.py`:822-831). X_P=0.0082 at baseline.
- [x] **PASS.** X_P < X_F: 0.0082 < 0.5743. Confirmed.
- [x] **PASS.** phi_L >= phi_F (weak inequality): both equal 0.7009 at baseline (equality satisfies weak inequality). Paper correctly labels this as a "computational regularity."
- [x] **PASS.** Parts (iii)-(v) are numerical findings, verified across parameterizations in tests.

**Effective revenue coefficient** (eq-a-eff; `_model.qmd`:80 vs `base_model.py`:449-452):

- [x] **PASS.** Single-firm A_eff matches exactly. Duopoly version (`duopoly.py`:188-192) correctly adds contest shares. Verified numerically: code = 9.8232, manual = 9.8232. Monopolist limit (K_j=0) correctly recovers single-firm value.

**Particular solution coefficient** (eq-particular-C; `_model.qmd`:169 vs `base_model.py`:161-168):

- [x] **PASS.** `C = -lambda * B_H / Q_L(beta_H)` with `Q_L = (sigma^2/2)*beta_H*(beta_H-1) + mu_L*beta_H - (r+lambda)`. Exact match. C = 21.14 at baseline.

**Symbolic cross-validation** (`symbolic_duopoly.py`):

- [x] **PASS.** SymPy derivations independently verify all characteristic roots, the C coefficient, option value structure (both one-term and two-term forms), and comparative statics signs (dA_eff/dlambda > 0, dX_D/dA_eff < 0).

#### 1.2 Proofs

**Proof of Proposition 1** (`_appendix.qmd`:39-104): **PASS.** All 6 steps logically complete. Minor observation: Step 4 does not explicitly verify the second-order condition for K (that the FOC gives a maximum), but this is implicit from the bounded optimization over K > 0 and confirmed numerically.

**Proof of Proposition 2** (`_appendix.qmd`:106-145): **PASS.** Parts (i)-(iv) logically complete. Appropriate caveats about the mechanical leverage-training substitution (Part iii).

**Proof of Proposition 3** (`_appendix.qmd`:147-184): **PASS** with one caveat. Existence via IVT is correct. Uniqueness is honestly classified as computational. The X_F/X_P ratio range of "approximately 40-70" is verified (70.0 at zero leverage, 43.5 at ell=0.70).

#### 1.3 Numerical Methods

**Single-firm optimization** (`base_model.py`): **PASS.** `minimize_scalar` with bounded method on a unimodal objective. Bounds [-15, 15] in log-K space are generous. Joint (K, phi) optimization uses 12-point multi-start Nelder-Mead. Converges reliably.

**Duopoly** (`duopoly.py`): **PASS.** Follower uses 9-27 point multi-start Nelder-Mead (xatol=1e-8, fatol=1e-10). Preemption root-finding uses Brentq with proper sign checking and fallbacks. Default boundary formula is division-safe (revenue_coeff <= 0 returns inf). Negative root always has positive discriminant (proven algebraically).

**N-firm equilibrium** (`nfirm.py`): **ISSUE.** See Critical Issues. The iterative best-response algorithm diverges, producing capacity values up to 1.17e192 and 141,000+ overflow warnings. The dampening factor (0.5) is insufficient.

**Revealed beliefs** (`revealed_beliefs.py`): **PASS.** Brentq inversions on [0.001, 2.0] with proper sign checks and infinity guards. Tolerance xtol=1e-6 is appropriate.

#### 1.4 Parameter Consistency

- [x] **PASS.** All 11 default parameter values in `parameters.py` match `_appendix.qmd` tbl-parameters and `_calibration.qmd` exactly: r=0.12, mu_L=0.01, mu_H=0.06, sigma=0.25, lambda=0.10, alpha=0.40, gamma=1.50, c=1.00, delta=0.03, coupon_rate=0.05, bankruptcy_cost=0.30.
- [x] **PASS.** Calibration data in `data.py` (`get_stylized_firms()`) matches tbl-firms for all 4 firm archetypes (24 data points verified).

#### 1.5 Regime Switching

- [x] **PASS.** GBM demand process (`base_model.py`:365): `X[t+1] = X[t]*exp((mu - 0.5*sigma^2)*dt + sigma*dW)`. Matches eq-gbm.
- [x] **PASS.** Transition intensity lambda enters through the effective discount rate (r + lambda) in the L-regime characteristic equation (`parameters.py`:238-247). H-regime is absorbing (no back-transition). Consistent with `_model.qmd` specification.
- [x] **PASS.** A_L formula (`parameters.py`:135-137) correctly integrates the regime-switching PV: `A_L = (r - mu_H + lam) / [(r - mu_H)(r - mu_L + lam)]`.

---

### 2. Code Quality and Testing

#### 2.1 Test Coverage

227 tests across 7 files. All pass. Coverage by module:

| Module | Stmts | Coverage | Notes |
|--------|-------|----------|-------|
| `models/base_model.py` | 234 | 89% | Uncovered: some branch guards for edge cases |
| `models/duopoly.py` | 371 | 86% | Uncovered: some endogenous lambda paths, heterogeneous K_j branches |
| `models/nfirm.py` | 219 | 89% | Uncovered: some N-firm edge case paths |
| `models/parameters.py` | 110 | 76% | Uncovered: `lambda_tilde()` endogenous paths, some validation branches |
| `models/valuation.py` | 195 | 77% | Uncovered: `dario_dilemma_leveraged` (lines 348-390), some decomposition paths |
| `models/symbolic_duopoly.py` | 190 | 83% | Uncovered: `l_regime_option_value_full()` two-term derivation, LaTeX generation |
| `calibration/revealed_beliefs.py` | 152 | 86% | Uncovered: some edge case returns |
| `calibration/data.py` | 39 | 100% | Full coverage |
| `figures/paper.py` | 309 | **0%** | No tests for figure generation |
| `pipeline.py` | 103 | **0%** | No tests for pipeline orchestration |
| **Overall** | **2813** | **47%** | 47% is low, driven by untested figures/pipeline/utilities |

The 47% overall coverage is misleading: the core model code (where correctness matters most) has 76-89% coverage. The figures, pipeline, and utility modules are untested but are thin wrappers over the tested model code.

#### 2.2 Test Meaningfulness

The test suite is **strong and economically meaningful**. Standout tests include:

- **Smooth-pasting and value-matching** (`test_base_model.py`:63-78): Verifies the fundamental first-order conditions defining the optimal exercise boundary.
- **Symbolic-numerical cross-validation** (`test_symbolic_duopoly.py`): The strongest tests in the suite. SymPy derivations independently verify numerical implementations across multiple parameter sets and lambda values.
- **Leland default conditions** (`test_duopoly.py`:383-413): Verifies E(X_D)=0 and E'(X_D)=0 at the default boundary.
- **Firm value = equity + debt** (`test_duopoly.py`:448-454): Balance sheet identity.
- **Dario's dilemma self-consistency** (`test_valuation.py`:121-125): Matched beliefs produce zero loss.
- **Preemption ordering** (`test_duopoly.py`:301-304): Leader invests before follower.

A minority of tests are structural (checking dict keys, array shapes) rather than economic, but these serve as regression guards.

**One weakness:** `test_calibration.py`:73-79 (`test_higher_lambda_lower_trigger`) checks "both values are valid" rather than asserting the economic direction, making it partially tautological. The comment acknowledges the H-trigger is lambda-independent, which is correct, but the test name is misleading.

#### 2.3 Edge Cases

Well-tested edge cases include:
- Zero volatility equivalent (very low sigma) in comparative statics
- Single firm in N-firm model (no competitors -> share = 1)
- Lambda near zero (degeneracy to inference-only formula)
- Zero leverage (no default boundary, equity = V - I)
- High alpha parameters where L-regime *does* have an interior trigger
- Impossible trigger values (inversion returns None)
- Zero training fraction (zero quality change)

**Missing edge case:** No test for sigma=0 exactly (only near-zero). This would test the degenerate deterministic case where there is no option value.

#### 2.4 Numerical Stability

**Critical issue:** N-firm equilibrium divergence (see Section 1.3 above).

**Medium issue:** `_particular_solution_coeff()` (`base_model.py`:167) guards Q_L near zero with threshold `1e-15` and returns 0.0. The threshold is too tight for double-precision arithmetic (catastrophic cancellation could occur when mu_L is close to mu_H with small lambda), and returning 0.0 is semantically wrong (C should diverge, not vanish, as Q_L -> 0). At baseline parameters Q_L = -0.178, safely away from zero.

**All other numerical methods are well-guarded.** Division-by-zero protected in default boundary. Quadratic discriminant always positive for negative root. Brentq inversions have proper sign checks and fallbacks.

#### 2.5 Code Organization

**Excellent.** Clean separation of concerns:
- `parameters.py` -> `base_model.py` -> `duopoly.py` -> `nfirm.py` -> `valuation.py` (progressive model hierarchy)
- `symbolic_duopoly.py` (verification/documentation, not in pipeline)
- `figures/paper.py` (all 11 figure computations) vs `paper/generate_figures.py` (thin style wrapper)
- `calibration/data.py` (firm data) vs `calibration/revealed_beliefs.py` (inference algorithm)

No unnecessary abstractions or over-engineering. Module responsibilities are clear. The two-mode pattern (simple vs full/phi-aware) is well-documented in AGENTS.md and consistently applied.

#### 2.6 Reproducibility

- [x] Pipeline orchestration via Hydra (`conf/config.yaml`) with toggleable steps.
- [x] Random seed set for demand simulation (seed 42 in figure generation).
- [x] Deterministic numerical optimization (no stochastic elements outside simulation).
- [ ] **Could not verify** full pipeline (`just run-pipeline`) due to potential data download dependencies, but all model computations are self-contained and reproducible.

---

## Part 2: Paper Review

### 3. Paper Content Review

#### 3a. Structure and Argument

**Motivation:** The introduction is compelling. It clearly articulates the investment dilemma facing AI labs: how to allocate irreversible compute capacity between current inference revenue and future training capability under uncertain AGI timing. The three tensions identified (explore/exploit, compete/wait, survive/believe) provide a unifying narrative.

**Literature positioning:** Adequate. The paper situates itself relative to Dixit & Pindyck (1994), McDonald & Siegel (1986), Grenadier (2002), and Weeds (2002) in real options; Leland (1994) in structural credit risk; and Aghion et al. (2018), Jones (2023) in AI economics. The training-inference allocation connects to R&D race models.

One potential omission: the paper does not discuss the growing literature on *compute governance* (e.g., Sastry et al., 2024) or the *scaling hypothesis* literature (Kaplan et al., 2020, is cited but the broader debate about scaling laws plateauing is not addressed). Given the paper's reliance on unbounded H-regime growth, this deserves at least a sentence in the discussion.

**Model building:** The progression from single-firm (Prop 1) to duopoly with default (Prop 2) to preemption equilibrium (Prop 3) is natural and well-motivated. Each extension adds one layer of complexity with clear economic justification. The training-inference allocation (phi) is introduced alongside the basic model rather than as an afterthought, which is a strength.

**Identification:** The revealed beliefs methodology is clearly presented. The key identifying assumption is that the observable CapEx/Revenue ratio identifies lambda through the model's predicted investment intensity. The assumptions are stated and reasonable, though the stylized calibration (4 firm archetypes rather than a panel) limits the empirical claims. The paper is honest about this limitation.

**Conclusion:** Effective. Summarizes the three propositions and the Dario's dilemma finding without overclaiming. Appropriately forward-looking about empirical extensions.

#### 3b. Writing Quality

**Clarity:** Generally excellent. The mathematical exposition is precise and readable. The economic intuition accompanies each formal result. A few passages could be tightened:

- `_model.qmd`:297-299 — the distinction between "net present value of equity" and "going-concern equity value" could be clearer; this is where the equity formula inconsistency originates (see Critical Issues).
- `_discussion.qmd` — the four testable predictions are well-stated but could benefit from brief discussion of data requirements for each.

**Notation:** Consistent throughout. All symbols defined before use. The paper uses standard real options notation (beta for characteristic roots, sigma for volatility, etc.). The phi/K_i/K_j notation is clear. One minor point: the paper uses both lambda and lambda_tilde (endogenous) but the main text uses only lambda (exogenous) per the simplification in the Feb 2026 revision. This is clean.

**Length and focus:** Appropriate for a top finance journal. The main text is well-scoped (~20 pages of content before appendices). No padding. The appendix structure is efficient (proofs, numerical methods, N-firm extension, calibration details, sensitivity).

**Abstract:** Concise and informative. Covers the methodology (real options, regime switching, duopoly, Tullock contests), key results (analytical triggers, faith-based survival, Dario's dilemma), and calibration. At 6 sentences, it is appropriately brief.

#### 3c. Journal Fit

**Contribution significance:** The paper makes a meaningful contribution by connecting three active areas: real options theory, AI economics, and structural credit risk. The training-inference allocation mechanism is novel and economically interesting. The "faith-based survival" result (training investment lowers default boundary through the option value of future AGI) is a genuine insight. The Dario's dilemma finding (asymmetric costs of belief errors) has clear practical relevance.

**Methodological rigor:** High. Analytical results are clearly stated with proofs. Computational results are honestly labeled as such. The symbolic verification layer (symbolic_duopoly.py) is an impressive addition to the codebase that goes beyond typical paper-appendix standards.

**Formatting and conventions:** Follows Econometrica/JF conventions (numbered propositions, formal proofs in appendix, calibration section, etc.). Quarto formatting is clean.

**Recommended target journal:** **Journal of Finance (JF)** or **Review of Financial Studies (RFS)**. The paper's strength is in the finance application (investment triggers, credit risk, preemption) rather than pure methodology (which would favor Econometrica) or macro (AER). The structural credit risk component and the calibration to AI firms position it well for a top finance journal. JF may be slightly preferred for the novelty of the AI application; RFS for the technical depth of the model.

---

### 4. Figures

#### 4.1 Paper Figures

All 11 figures were reviewed for accuracy, labeling, and quality. Each generates both PDF (paper style) and PNG (talk style).

| # | Figure | Assessment | Notes |
|---|--------|-----------|-------|
| 1 | `fig_sample_paths` | **PASS** | 5 simulated demand paths with regime switch markers. Log-scale y-axis. X_H* dashed line. |
| 2 | `fig_option_value` | **PASS** | F_H(X) vs NPV with "value of waiting" shading. Smooth-pasting verified at X*. |
| 3 | `fig_comparative_statics` | **PASS** | 4-panel (sigma, alpha, gamma, delta) with dual y-axes. Minor cosmetic legend overlap in PNG; fine in PDF. |
| 4 | `fig_lambda_option_value` | **PASS** | F_L and C vs lambda. F_H correctly shown as lambda-independent flat line. |
| 5 | `fig_default_boundaries` | **PASS** | X_F, X_L, X_D vs leverage. Correct ordering: X_D < X_L < X_F at all leverage values. |
| 6 | `fig_credit_risk` | **PASS** | Credit spread and default probability vs leverage. Monotonically increasing. |
| 7 | `fig_competition_effect` | **PASS** with note | Panel (b) capacity ratio is identically 1.0 (K_leader = K_mono by construction). Technically correct but visually redundant. |
| 8 | `fig_firm_comparison` | **PASS** with note | xAI-like CapEx/Revenue ~20x dominates the bar chart, making other bars small. Accurately reflects data. |
| 9 | `fig_lambda_timeline` | **PASS** | Pure analytical (1/lambda and 1-exp(-5*lambda)). No model dependency. |
| 10 | `fig_growth_decomposition` | **PASS** | Uses full phi-aware model. Correct decomposition of value into AIP and growth option. |
| 11 | `fig_investment_dilemma` | **PASS** | Dario's dilemma with unleveraged and leveraged (ell=0.40) curves. Zero loss at matched beliefs verified. |

#### 4.2 Code-Figure Consistency

Three figures were deeply traced from model code through `figures/paper.py` to the final plot:

**Figure 2 (`create_option_value`, `paper.py`:82-133):** Verified. `SingleFirmModel.option_value_H(x)` produces B_H * x^beta_H for x < X*. NPV line is `installed_value(x, K*, "H") - investment_cost(K*)`. Smooth-pasting confirmed: F_H(X*) = V(X*, K*) - I(K*) with gap = 0.

**Figure 5 (`create_default_boundaries`, `paper.py`:256-314):** Verified. Leverage sweep 0.05 to 0.65 with 25 points. Each iteration creates `DuopolyModel(p, leverage=lev)` and calls `solve_preemption_equilibrium("H")`. Correctly extracts `X_follower`, `X_leader`, and `X_default_follower` from the equilibrium dict.

**Figure 11 (`create_investment_dilemma`, `paper.py`:583-650):** Verified. `ValuationAnalysis(p).dario_dilemma(fixed_true=0.10, lambda_invest=lam)` for lambda_invest in [0.02, 0.50]. Self-consistency at lambda_invest=0.10: loss = 0.0% exactly. Asymmetry confirmed: underinvestment (0.02) loses 26.2%, overinvestment (0.50) loses 22.6%.

---

### 5. Calibration and Results

#### 5.1 Parameter Values

- [x] **PASS.** Baseline parameters are well-sourced. r=0.12 as WACC for AI firms is reasonable (tech sector cost of capital range 10-18%). sigma=0.25 is moderate uncertainty. alpha=0.40 reflects diminishing returns to scale consistent with AI scaling laws. gamma=1.50 for convex installation costs is standard.
- [x] **PASS.** Drift rates mu_L=0.01 (near-stagnation) and mu_H=0.06 (moderate growth) capture the regime-switching structure without extreme assumptions.

#### 5.2 Sensitivity

- [x] **PASS.** Figure 3 shows sensitivity to sigma, alpha, gamma, and delta. Appendix E (`tbl-elasticities`) reports parameter elasticities. Sensitivity to lambda is explored in multiple figures (4, 9, 11).
- [ ] **Minor gap.** No systematic sensitivity analysis for the number of firms N (the N-firm extension is presented only for N=3,4 in the appendix, without a sweep).

#### 5.3 Comparative Statics

- [x] **PASS.** All reported comparative statics are consistent with economic intuition:
  - Higher sigma -> higher trigger (option value of waiting increases)
  - Higher lambda -> lower trigger (AGI more likely, invest sooner)
  - Higher lambda -> higher phi (allocate more to training)
  - Higher leverage -> higher default boundary
  - Competition -> lower trigger (preemption accelerates investment)

#### 5.4 Revealed Beliefs Results

- [x] **PASS.** The stylized firm calibration produces plausible results. The 4 archetypes span a realistic range of investment intensities. The inversion methodology is well-identified: CapEx/Revenue ratio maps monotonically to lambda through the model.
- [ ] **Note.** The revealed beliefs are illustrative rather than precise estimates, as the paper acknowledges. The calibration uses 2024-2025 data for firms in a rapidly evolving market.

#### 5.5 Growth Decomposition

- [x] **PASS.** Decomposition into assets-in-place and growth option is correctly computed. Assets + growth fractions sum to 1 (verified in tests). L-regime has positive regime-switch value; H-regime has zero (absorbing state).

---

## Summary of Issues

### Critical Issues

**1. Equity value formula inconsistency (`_model.qmd`:303 vs `duopoly.py`:426)**

The paper's equity formula includes `(1-ell)I(K)` (the sunk equity contribution) inside the default option bracket:
```
E(X) = A_eff*X - delta*K/r - (1-ell)*I(K) - c_D/r
     + [c_D/r + delta*K/r + (1-ell)*I(K) - A_eff*X_D] * (X/X_D)^{beta^-}
```

The code correctly excludes it:
```python
default_claim = c_D / p.r - V_XD  # where V_XD = A_eff*X_D - delta*K/r
equity = V_X - equity_contribution - c_D / p.r + default_claim * (X/X_D)**beta_neg
```

**Why this matters:** The paper's formula satisfies E(X_D)=0 by construction, but if smooth-pasting E'(X_D)=0 is applied to this formula, it yields a *different* X_D that includes `(1-ell)I(K)` in the numerator — inconsistent with eq-default-boundary. The paper's footnote (`_model.qmd`:307) claims `(1-ell)I(K)` "cancels in the smooth-pasting derivative," but this is incorrect for the formula as written (the sunk cost appears inside the default option term, so its derivative with respect to X is nonzero via the `(X/X_D)^{beta^-}` factor).

The **code is correct** (standard Leland approach: solve HJB for ongoing equity, then subtract sunk cost). The **paper formula needs correction**: remove `(1-ell)I(K)` from inside the default option bracket, or redefine E(X) as the going-concern equity value without the sunk cost subtraction and note that E(X_D) = (1-ell)I(K) at default.

**Suggested fix:** Replace the equity formula on `_model.qmd`:303 with:
```
E(X) = A_eff*X - delta*K/r - (1-ell)*I(K) - c_D/r
     + [c_D/r + delta*K/r - A_eff*X_D] * (X/X_D)^{beta^-}
```
and update the text on line 307 to note that E(X_D) = -(1-ell)I(K), which is clamped to zero by limited liability. This matches the code exactly.

### Major Issues

**2. N-firm sequential equilibrium divergence (`nfirm.py`:306-407)**

The iterative best-response algorithm for the N-firm model does not converge. During testing, capacity values explode to 1.17e192 within 20 iterations, generating 141,000+ overflow warnings (`RuntimeWarning: overflow encountered in scalar power/multiply`). The dampening factor (alpha_damp=0.5, line 338) is insufficient because the best-response function is expansionary (optimal K is 28-226x the competitor capacity at each iteration).

**Impact:** The N-firm results (Numerical Finding 1 in Appendix C) should be interpreted cautiously. The paper correctly places these in the appendix as a "numerical extension" rather than a core result, but the current implementation does not reliably compute the equilibrium.

**Suggested fixes:**
- Add divergence detection: break early if `max_change` increases for 3+ consecutive iterations.
- Add explicit bounds to `solve_entrant()`: cap `log_K` at [-15, 15] to prevent overflow.
- Consider reformulating as a simultaneous fixed-point problem using `scipy.optimize.root` on the N-dimensional first-order conditions.
- Use log-space dampening: `log_K_new = alpha*log(K_computed) + (1-alpha)*log(K_old)`, which converts multiplicative divergence into additive updates.

**3. `_extensions.qmd` is orphaned**

The file `paper/_extensions.qmd` (61 lines) defines N-firm contest functions and Numerical Finding 1 but is NOT included in `index.qmd`. Its content is partially duplicated in Appendix C (`_appendix.qmd`:245-256). This file should either be deleted or merged into the appendix to avoid confusion.

### Minor Issues

**4. Test name misleading** (`test_calibration.py`:73, `test_higher_lambda_lower_trigger`): Tests "both values are valid" rather than asserting the expected direction. The H-regime trigger is lambda-independent (correct), but the test name implies a comparative static that isn't being tested.

**5. Q_L near-zero guard** (`base_model.py`:167): Threshold `1e-15` is too tight for double precision; returning 0.0 is semantically incorrect (C should diverge as Q_L -> 0). At baseline this is harmless (Q_L = -0.178). Suggested: widen to `1e-10` and issue a warning instead of silently returning zero.

**6. Coverage gap in `dario_dilemma_leveraged`** (`valuation.py`:348-390): This function is called in Figure 11 but has zero test coverage. Adding a basic test (matched beliefs -> zero loss for leveraged case) would strengthen validation.

**7. Figure 7 panel (b) redundancy:** The capacity ratio K_leader/K_mono is identically 1.0 because the leader uses monopolist-optimal K by construction. The dashed line sits exactly on the reference line. Consider removing it or adding a note.

**8. Figure 8 scale dominance:** xAI-like's CapEx/Revenue ratio (~20x) makes the other three firms' bars nearly invisible. Consider a log-scale y-axis or a broken axis for panel (a).

**9. Missing edge case test:** No test for sigma=0 exactly (the degenerate deterministic case with no option value). While the model requires sigma > 0, a test confirming graceful degradation at very small sigma (e.g., 1e-6) would be valuable.

**10. Scaling hypothesis discussion gap:** The paper assumes unbounded H-regime demand growth. A brief discussion of the possibility that scaling laws may plateau (diminishing returns to compute beyond some frontier) would strengthen the robustness section. This could be a one-sentence caveat in Section 6 (Discussion) noting that alpha < 1 partially captures diminishing returns but does not model a hard ceiling.

---

## Overall Recommendation

**Revise and resubmit (minor revision).** The core model is correct, the paper is well-written, and the contribution is significant. The critical equity formula fix is straightforward (one equation change + footnote edit). The N-firm convergence issue affects only the appendix extension and does not impact the main results.

**Recommended target journal:** Journal of Finance (JF). The paper combines methodological sophistication (real options with regime switching, Tullock contests, Leland credit risk) with a timely and important application (AI lab investment decisions). The "faith-based survival" mechanism and Dario's dilemma are memorable contributions that will resonate with finance audiences. The stylized calibration is appropriate for the JF's empirical expectations (demonstrating magnitudes rather than claiming precise estimates). RFS is a strong alternative if the authors wish to emphasize the structural model's technical depth.
