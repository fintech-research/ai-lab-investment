# Review Report: AI Lab Investment

**Reviewer:** Claude Opus 4.6
**Date:** 2026-02-22

## Executive Summary

This report reviews the research project "Investing in Intelligence: A Real Options Framework for AI Compute Infrastructure" by Vincent Gregoire (HEC Montreal), covering both the codebase implementation and the research paper. The project builds a unified real options model for irreversible AI compute investment under demand uncertainty with regime switching, oligopoly competition, endogenous default, and diminishing returns calibrated to AI scaling laws.

**Code assessment:** The implementation is generally correct and well-engineered. All 146 tests pass. A systematic mathematical audit confirms that core formulas in the code faithfully implement the paper's propositions, with exact matches for 20 of 22 verified formulas (characteristic equations, present-value multipliers, option values, installed values, default boundaries, contest functions, revealed beliefs inversion, etc.). Two formula discrepancies were found: (1) the debt recovery value in bankruptcy uses gross asset value rather than net installed value as stated in the paper (`duopoly.py:270`), and (2) the Dario dilemma NPV computation omits a timing discount factor present in the paper's appendix (`valuation.py:228-290`). Additionally, the growth option decomposition double-counts the regime-switch value for regime L. The code exhibits good numerical stability practices (log-space optimization, division-by-zero guards, convergence bounds). Overall test coverage is 46% (core model modules 80-100%, but figure generation, pipeline orchestration, and utilities are untested). A data-figure mismatch was detected in Figure 8, and multiple slide numerical claims do not match current model outputs.

**Paper assessment:** The paper presents a genuinely novel contribution -- the "revealed beliefs" methodology for inferring AI labs' private probability assessments of transformative AI from observable investment decisions -- within a technically rigorous real options framework. The writing is consistently clear and precise. However, several proofs are incomplete (Propositions 1, 4(iii), and 6), notation is overloaded in places ($D$ used for three distinct meanings), 10 bibliography entries are orphaned (never cited), and the identification strategy deserves deeper investigation (implied $\hat{\lambda}$ may be primarily driven by CapEx/Revenue ratio alone). The paper is best suited for the **Review of Financial Studies** and requires moderate revision before submission.

---

## Part 1: Code Validation

### 1. Mathematical Correctness

#### 1.1 Propositions vs. Code

- [x] **PASS: Proposition 1 (Optimal trigger and capacity in regime H).** The trigger formula in `base_model.py:70-81` (`_trigger_for_K`) computes $X^*(K) = [\beta/(\beta-1)] \cdot [\delta K/r + cK^\gamma] / [A \cdot K^\alpha]$, which exactly matches the Appendix A derivation (`_appendix.qmd` lines 9-13). The capacity optimization in `base_model.py:83-96` (`_objective_K`) maximizes $\beta \ln(a) - (\beta-1) \ln(b)$ where $a = A K^\alpha$ and $b = \delta K/r + c K^\gamma$, which is the correct log-transformation of the option value at the trigger. The existence condition $1/\gamma < (1-1/\beta)/\alpha < 1$ is implemented at `base_model.py:51-68` (`_phi`, `has_interior_trigger`). **Exact match.**

- [x] **PASS: Proposition 2 (Endogenous default boundary).** The default boundary formula in `duopoly.py:126-161` (`default_boundary`) computes $X_D = [\beta^-/(\beta^- - 1)] \cdot (c_D/r) / [A \cdot K_i^\alpha \cdot s_i]$, matching `_model.qmd` Eq. 9 (`@eq-default-boundary`, line 141). The negative root computation at `duopoly.py:163-176` uses the same characteristic equation as the positive root but selects $(-b - \sqrt{\Delta})/(2a)$. **Exact match.**

- [x] **PASS: Proposition 3 (Preemption equilibrium with default risk).** The preemption equilibrium is solved via Brent's method on `_preemption_gap` (`duopoly.py:519-587`), finding the demand level where leader value equals follower option value. The follower optimization (`duopoly.py:343-372`) and leader monopolist solution (`duopoly.py:466-493`) correctly implement the sequential game. The Brent tolerance is `xtol=1e-10` (`duopoly.py:583`). **Match (numerical solution).**

- [x] **PASS: Proposition 4 (N-firm equilibrium properties).** The sequential equilibrium solver in `nfirm.py:200-289` (`solve_sequential_equilibrium`) uses backward induction with iterative refinement. The contest share function (`nfirm.py:73-84`) correctly generalizes the Tullock function to N firms. Convergence criterion is `tol=1e-6` with `max_iterations=20` (`nfirm.py:209`). **Match (numerical solution).**

- [x] **PASS: Proposition 5 (Optimal training fraction).** The formula $\phi^* = \eta/(\alpha + \eta)$ is implemented at `nfirm.py:300-310` (`optimal_training_fraction`). The quality dynamics $Q = A \cdot (\phi K \cdot t)^\eta$ is at `nfirm.py:320-340`. **Exact match.**

- [x] **PASS: Proposition 6 (Asymmetric Dario dilemma).** Implemented via `valuation.py` `dario_dilemma_loss` function and the `dario_dilemma_surface` function, which computes value losses for grid combinations of $\lambda_{\text{invest}}$ vs $\lambda_{\text{true}}$. **Match.**

#### 1.2 Key Equation Verification

| Equation | Paper Location | Code Location | Verdict |
|----------|---------------|---------------|---------|
| GBM demand (Eq. 1) | `_model.qmd` line 8 | `base_model.py:346-357` | EXACT MATCH |
| Installed value (Eq. 2) | `_model.qmd` line 38 | `base_model.py:38-45` | EXACT MATCH |
| Option value H (Eq. 3) | `_model.qmd` line 53 | `base_model.py:229-238` | EXACT MATCH |
| Characteristic eq. H (Eq. 5) | `_model.qmd` line 57 | `parameters.py:151-160` | EXACT MATCH |
| ODE for regime L (Eq. 6) | `_model.qmd` line 95 | `base_model.py:138-155` | EXACT MATCH |
| Characteristic eq. L (Eq. 8) | `_model.qmd` line 101 | `parameters.py:103` | EXACT MATCH |
| Contest function (Eq. 4) | `_model.qmd` line 121 | `duopoly.py:64-74` | EXACT MATCH |
| Default boundary (Eq. 9) | `_model.qmd` line 141 | `duopoly.py:126-161` | EXACT MATCH |
| N-firm contest (Eq. 10) | `_extensions.qmd` line 12 | `nfirm.py:73-84` | EXACT MATCH |
| Scaling law (Eq. 11) | `_extensions.qmd` line 47 | `nfirm.py:320-340` | EXACT MATCH |
| Debt value recovery | `_model.qmd` line 171 | `duopoly.py:239-273` | **DISCREPANCY** (see below) |
| Inversion condition (Eq. 12) | `_valuation.qmd` line 18 | `revealed_beliefs.py:40-65` | MATCH |
| PV multiplier A_H | `_model.qmd` line 42 | `parameters.py:104` | EXACT MATCH |
| PV multiplier A_L | `_model.qmd` line 45 | `parameters.py:106-110` | EXACT MATCH |
| Smooth-pasting B_H | Appendix A | `base_model.py:133` | EXACT MATCH |
| Particular solution C | `_model.qmd` line 103 | `base_model.py:138-155` | EXACT MATCH |

#### 1.3 Proofs

- [x] **Proposition 1 proof (`_appendix.qmd` lines 5-44):** **HAS ISSUES.** Step 1 (smooth-pasting derivation) is correct and standard. Step 2 (optimal capacity) is incomplete: the transition from the $\delta=0$ leading-order solution (line 33) to the general first-order condition (line 38) is abrupt. The phrase "dominant balance between the $\alpha$ and $\gamma$ exponents" (line 36) is a physicist's asymptotic argument, not a rigorous proof. The existence condition is asserted (lines 43-44) without proving that the upper bound holds generically.

- [x] **Proposition 5 proof (`_appendix.qmd` lines 46-63):** **PASS.** Complete and correct standard FOC/SOC argument.

- [x] **Proposition 2 proof (`_appendix.qmd` lines 65-73):** **PASS.** Straightforward comparative statics on the explicit formula.

- [x] **Proposition 3 proof (`_appendix.qmd` lines 75-85):** **HAS ISSUES.** The uniqueness argument (line 85) claims "leader value grows linearly in X" but the leader value includes terms proportional to $X^{\beta_s}$ ($\beta_s > 1$), which is superlinear. This is imprecise.

- [x] **Proposition 4 proof (`_appendix.qmd` lines 87-95):** **HAS ISSUES.** Part (iii) -- that total capacity increases with N -- is asserted ("the number of contributors grows faster than individual capacity shrinks for $\alpha < 1$") without a formal bound. The required condition $f^\alpha > 1 - 1/N$ (where $f$ is the capacity reduction factor) is not verified.

- [x] **Proposition 6 proof (`_appendix.qmd` lines 97-110):** **HAS ISSUES.** Entirely qualitative. Identifies three channels for aggressive loss vs. one for conservative loss, but provides no formal magnitude comparison. A Taylor expansion or formal bound is needed for a top journal.

#### 1.4 Numerical Methods

- [x] **Root-finding (`duopoly.py:576-587`):** Uses `scipy.optimize.brentq` with `xtol=1e-10`. Appropriate for the preemption gap problem. Search interval is `[0.001*X_L_mono, X_L_mono]`. **PASS.**

- [x] **Capacity optimization (`base_model.py:115-128`):** Uses `scipy.optimize.minimize_scalar` with Brent's method over log-space bounds `(-15, 15)`, corresponding to $K \in [3 \times 10^{-7}, 3.3 \times 10^6]$. Reasonable range. Failure detection via sentinel `1e19`. **PASS.**

- [x] **Backward induction (`nfirm.py:200-289`):** Iterative refinement with `max_iterations=20`, `tol=1e-6`. Initializes with dummy competitors `[1.0] * n_competitors`. Non-convergence handled with warning. **PASS with caveat:** The dummy initialization of 1.0 is arbitrary and could affect convergence speed. No formal convergence guarantee is provided.

- [x] **Revealed beliefs inversion (`revealed_beliefs.py:40-65`):** Uses `scipy.optimize.brentq` to find $\lambda$ matching observed investment intensity. Bounds $\lambda \in [0.001, 2.0]$ with `xtol=1e-8`. Returns `None` for impossible targets. **PASS.**

#### 1.5 Parameter Consistency

- [x] **PASS.** Default parameter values in `parameters.py` match the calibration values stated in `_calibration.qmd`:

| Parameter | `parameters.py` | `_calibration.qmd` | Match? |
|-----------|-----------------|---------------------|--------|
| $r$ | 0.12 | 0.12 | Yes |
| $\mu_L$ | 0.01 | 0.01 | Yes |
| $\mu_H$ | 0.06 | 0.06 | Yes |
| $\sigma_L$ | 0.25 | 0.25 | Yes |
| $\sigma_H$ | 0.30 | 0.30 | Yes |
| $\lambda$ | 0.10 | 0.10 | Yes |
| $\alpha$ | 0.40 | 0.40 | Yes |
| $\gamma$ | 1.50 | 1.50 | Yes |
| $c$ | 1.00 | 1.00 | Yes |
| $\delta$ | 0.03 | 0.03 | Yes |

Firm-specific parameters in `CalibrationData` (`data.py`) are consistent with `@tbl-firms` in `_calibration.qmd`. Leverage defaults (0.0), coupon rate (0.05), and bankruptcy cost (0.30) are consistent across `duopoly.py`, `nfirm.py`, and `valuation.py`.

#### 1.6 Regime Switching

- [x] **PASS.** The regime-switching demand process in `base_model.py:314-390` (`simulate_demand`) correctly implements:
  - Regime-dependent drift and volatility selection (lines 346-349)
  - Log-normal GBM discretization: $X_{t+1} = X_t \exp((\mu - \sigma^2/2)\Delta t + \sigma\sqrt{\Delta t}\,Z)$ (line 357)
  - Poisson switching as Bernoulli approximation: $P(\text{switch}) = \lambda \Delta t$ (line 354)
  - Absorbing regime H: only checks switch when $s = 0$ (line 353)

  **Minor caveat:** The Bernoulli approximation $P = \lambda\Delta t$ is only accurate when $\lambda\Delta t \ll 1$. With default `dt=0.001` and max $\lambda = 2.0$ (revealed beliefs bound), $\lambda\Delta t = 0.002$ -- still acceptable but no validation is present.

---

### 2. Code Quality and Testing

#### 2.1 Test Coverage

```
Overall:   46% (1852 statements, 978 missed)

Well-covered modules:
  calibration/data.py           100%
  models/base_model.py           90%
  models/nfirm.py                90%
  models/valuation.py            89%
  calibration/revealed_beliefs.py 86%
  models/duopoly.py              84%
  models/parameters.py           80%

Uncovered modules (0%):
  figures/phase1-5.py            0%   (visualization code)
  pipeline.py                    0%   (orchestration)
  utils/directories.py           0%   (directory resolution)
  utils/files.py                 0%   (timestamped file naming)
  __main__.py                    0%   (entry point)
  exceptions.py                  0%   (custom exceptions)
```

**Assessment:** Core model logic is well-covered (80-100%). The 0% coverage on figure generation, pipeline, and utilities is acceptable for a research project (these are infrastructure rather than analytical code), though it means the end-to-end pipeline is not integration-tested.

#### 2.2 Test Meaningfulness

The test suite is **generally excellent** in testing economically meaningful properties rather than trivial assertions. Highlights:

**Exemplary tests:**
- `test_smooth_pasting` (`test_base_model.py:63`): Verifies $F'(X^*) = V'(X^*, K^*)$ -- the core optimality condition
- `test_value_matching` (`test_base_model.py:73`): Verifies $F(X^*) = V(X^*, K^*) - I(K^*)$
- `test_option_exceeds_npv_before_trigger` (`test_base_model.py:90`): Tests $F(X) \geq \text{NPV}(X)$ for $X < X^*$
- `test_higher_sigma_higher_trigger_H` (`test_base_model.py:136`): Key comparative static from real options theory
- `test_leader_trigger_below_follower` (`test_duopoly.py:131`): Core preemption result $X_L < X_F$
- `test_default_boundary_below_trigger` (`test_duopoly.py:196`): Economic necessity $X_D < X_F$
- `test_firm_value_equals_equity_plus_debt` (`test_duopoly.py:230`): Modigliani-Miller identity $FV = E + D$
- `test_optimal_training_closed_form` (`test_nfirm.py:147`): Verifies Proposition 5
- `test_preemption_lowers_trigger` (`test_duopoly.py:174`): Preemption accelerates investment

**Issues found:**
- **Soft assertions mask failures.** Several tests use conditional assertions that silently pass when preconditions aren't met:
  - `test_with_high_alpha_has_L_trigger` (`test_base_model.py:129`): Wraps assertion in `if m.has_interior_trigger("L"):` -- if False, test passes vacuously
  - `test_higher_sigma_higher_trigger_H` (`test_base_model.py:141`): Wraps in `if valid.sum() == 2:` -- no test if no valid solutions
  - `test_default_boundary_below_trigger` (`test_duopoly.py:199`): Wraps in `if eq["X_default_follower"] > 0:` -- unnecessary given leverage=0.5
  - `test_leader_always_before_follower_in_statics` (`test_duopoly.py:287`): Wraps in `if valid.sum() > 0:`

- **Tautological test.** `test_symmetric_duopoly_revenue` (`test_duopoly.py:71`): Calls `duopoly_revenue_pv(X, K, K, "H")` twice with identical arguments and asserts they're equal. This always passes trivially. Should swap argument order to test true symmetry ($\pi_i(K_i, K_j) = \pi_j(K_j, K_i)$).

- **Vague assertion.** `test_follower_capacity_responds_to_leader` (`test_duopoly.py:97`): Tests `K_F1 > 0 and K_F2 > 0` but the name implies directional response. Should assert an inequality between `K_F1` and `K_F2`.

- **Loose tolerance.** `test_shares_sum_to_one` (`test_nfirm.py:116`): Uses tolerance of 0.1 (10%). Should be tighter (e.g., `1e-6`).

#### 2.3 Edge Cases

**Covered:**
- All-equity firm (leverage=0) vs levered firm (leverage=0.5)
- Regime H and regime L separately
- N=2, N=3, N=4 firms
- Lambda = 0 (no regime switching, `test_parameters.py:63`)
- Parameters that create an L-regime interior trigger (`test_base_model.py:124`)

**Missing edge cases:**
- Zero or near-zero volatility ($\sigma \to 0$)
- Lambda very large ($\lambda \gg 1$), testing convergence of regime L to regime H behavior
- N=1 (monopoly degeneration in N-firm model)
- N large (e.g., N=10) to test convergence of sequential equilibrium solver
- X at exactly the trigger ($X = X^*$), testing the branch boundary
- Leverage = 1.0 (fully debt-financed, extreme default risk)
- $\alpha = \gamma$ (the exponent $1/(\gamma - \alpha)$ in Proposition 1 is undefined)
- Training fraction = 1.0 (all training, no inference: $K_I = 0$)
- $\eta = 0$ (quality always zero regardless of training)
- Negative installed value (very low X where operating costs exceed revenue)
- Coupon rate = 0 with leverage > 0 (testing `c_D <= 0` path in `duopoly.py:145`)

#### 2.4 Numerical Stability

**Good practices observed:**
- Log-space optimization for capacity ($K = e^{z}$), preventing negative K: `base_model.py:85`, `duopoly.py:360`, `nfirm.py:135`
- Sentinel values for degenerate optimization results: `1e20` return for infeasible points, `1e19` threshold for failure detection
- Division-by-zero guards: `contest_share` returns 0.5 when `denom <= 0` (`duopoly.py:73`, `nfirm.py:83`)
- Near-zero guard for $Q_L$: `abs(Q_L) < 1e-15` check in `base_model.py:153`
- Default boundary guards: multiple early returns for degenerate inputs (`duopoly.py:134-148`)
- Parameter validation in `__post_init__` enforcing $r > \mu_H$, $\sigma > 0$, $0 < \alpha < 1$, $\gamma > 1$ (`parameters.py:60-98`)

**Potential issues:**
- **No overflow guard for `X**(1 - beta_H)` when `X_star` is very close to 0** (`base_model.py:133`): Since $\beta_H > 1$, the exponent is negative, creating a potential overflow. In practice, the optimizer constrains `X_star > 0`, but no explicit guard exists.
- **Poisson approximation validity not checked** (`base_model.py:354`): The Bernoulli approximation `P = lambda * dt` assumes `lambda * dt << 1`. No validation.
- **`np.exp(quality)` in `nfirm.py:102`** could overflow for extreme quality values, though current parameter ranges keep this safe.
- **Hardcoded optimization bounds `(-15, 15)`** in `base_model.py:121,177` and `duopoly.py:360,481`: While reasonable for current parameters ($K \in [3 \times 10^{-7}, 3.3 \times 10^6]$), these are undocumented and could become binding for extreme parameter choices.

#### 2.5 Code Organization

**Strengths:**
- Clean separation: parameters (`parameters.py`) -> single-firm (`base_model.py`) -> duopoly (`duopoly.py`) -> N-firm (`nfirm.py`) -> valuation/beliefs (`valuation.py`, `revealed_beliefs.py`)
- Consistent API: all models expose `summary()`, `solve_*()`, `comparative_statics_*()` methods
- Proper caching of expensive computations via `self._cache` dictionaries
- Well-documented functions with economic context in docstrings

**Minor issues:**
- `parameters.py:132-148` (`with_param`): Manually enumerates all fields. Could use `dataclasses.asdict()` for robustness.
- `duopoly.py:182-237` (`equity_value`): 55-line function with nested conditionals for leverage/no-leverage and K_j/no-K_j cases. Would benefit from decomposition.
- The `nfirm.py:238-248` competitor indexing logic is somewhat confusing and could use clearer variable naming.

#### 2.6 Reproducibility

- **Deterministic by default:** All model computations (triggers, capacities, option values, equilibria) are deterministic. No random seeds needed for the core analytical/numerical results.
- **Simulation non-deterministic by default:** `simulate_demand` (`base_model.py:314`) creates `np.random.default_rng()` without a seed if none is provided. However, tests correctly pass seeded generators (`test_base_model.py:159`: `seed=42`).
- **Pipeline not integration-tested:** `pipeline.py` has 0% coverage. Cannot verify end-to-end reproducibility from the test suite alone.

---

## Part 2: Paper and Presentation Review

### 3. Paper Content Review

#### 3a. Structure and Argument

- [x] **Motivation: PASS.** The introduction (`_introduction.qmd`) is compelling and clearly articulates the gap: existing real options literature does not address the AI compute investment problem with its unique combination of scaling laws, regime-switching demand, and extreme uncertainty about transformative AI. The motivating figures (CapEx statistics, Dario Amodei's "invest even if you'll go bankrupt" quote) effectively establish stakes.

- [ ] **Literature positioning: HAS ISSUES.** The paper adequately cites core references (Dixit & Pindyck 1994, McDonald & Siegel 1986, Grenadier 2002, Huisman & Kort 2015, Leland 1994). However, **10 of 31 bibliography entries are orphaned** (in `references.bib` but never cited in the text): `novymarx2007operating`, `pawlina2006real`, `epoch2024trends`, `sevilla2022compute`, `hayashi1982tobin`, `fazzari1988financing`, `korinek2024scenarios`, `tirole1988theory`, `leland1996optimal`, `blackcox1976`. Several of these are directly relevant:
  - Pawlina & Kort (2006) on asymmetric duopolies applies to the heterogeneous firms extension
  - Epoch AI (2024) and Sevilla et al. (2022) on AI compute trends support the calibration
  - Korinek (2024) on AGI scenarios connects to the revealed beliefs methodology
  - These should be either cited or removed from the bibliography.

- [x] **Model building: PASS.** The progression from single-firm benchmark (Section 2) to duopoly with default risk (Section 2.3) to N-firm equilibrium (Section 3) is natural and well-motivated. Each extension is clearly justified before being developed.

- [ ] **Identification: HAS ISSUES.** The revealed beliefs methodology (`_valuation.qmd` lines 9-25) is clearly described. However, the identification assumption (line 40) -- that "cross-firm variation in investment intensity reflects variation in beliefs about $\lambda$ rather than unobserved heterogeneity in costs or technology" -- is strong and deserves deeper investigation. Critically, Anthropic-like and CoreWeave-like produce identical $\hat{\lambda} = 0.95$ despite very different business models, leverage levels, and WACCs. Both have CapEx/Revenue = 2.00, suggesting the inversion may be primarily driven by a single sufficient statistic. If implied $\lambda$ is essentially a monotone function of CapEx/Revenue alone, the claimed contribution of accounting for heterogeneous firm characteristics is overstated. **The paper should report the sensitivity of $\hat{\lambda}$ to each firm-specific parameter (WACC, leverage, coupon rate) individually to demonstrate that they matter for the cross-section.**

- [x] **Conclusion: PASS.** Concise (`_conclusion.qmd`, 19 lines) and effective. Restates three main findings without overclaiming. Future research directions (dynamic learning, financial frictions, other sectors) are sensible.

#### 3b. Writing Quality

- [x] **Clarity: PASS.** The writing is consistently clear and precise, at the level expected of a top finance journal. Sentence lengths are varied. Technical terms are introduced naturally with appropriate economic motivation.

- [ ] **Notation: HAS ISSUES.** Three notation problems identified:
  1. **$D$ overloading (`_model.qmd`):** $D_L$ is a constant in the option value solution (line 100), $D_0$ is face value of debt (line 131), and $D(X)$ is the debt value function (line 170). Three distinct meanings for the same letter.
  2. **Coupon notation (`_model.qmd` lines 131-162):** The coupon rate is $c_d$ (line 132), the coupon payment is $d = c_d \cdot \ell \cdot I(K)$ (line 132), but the default boundary formula uses $c_D$ (capital D subscript, line 141) for the coupon payment. The distinction between $c_d$ (rate) and $c_D$ (payment) is not made clearly.
  3. **$A_s$ vs. inline:** The multiplier $A_H = 1/(r-\mu_H)$ is introduced (line 42) but the installed value equation (Eq. 2, line 38) writes the multiplier inline as $1/(r-\mu_s)$ rather than as $A_s$.
  - **Suggestion:** Add a notation table or glossary. Rename the option value constant from $D_L$ to $G_L$ or $\tilde{C}_L$ to avoid collision with debt notation.

- [ ] **Length and focus: HAS ISSUES.** The training-inference allocation (Section 3.2 of `_extensions.qmd`) produces the elegant Proposition 5 but is not used in the calibration or revealed beliefs inversion. The quality dynamics subsection (lines 76-82) is underdeveloped and never revisited. This creates a disconnected thread. Either integrate the training allocation into the revealed beliefs analysis or reduce its prominence.

- [x] **Abstract: PASS.** The abstract (`index.qmd`) concisely conveys the contribution, methodology, and key results. The "Dario dilemma" is memorably named.

- [ ] **Author voice: MINOR ISSUE.** "We" is used throughout the paper (e.g., "We develop", "We calibrate") but only one author is listed (Vincent Gregoire). This should be either changed to "I" or a co-author added.

#### 3c. Journal Fit

- [ ] **Contribution significance: PASS.** The "revealed beliefs" methodology is a genuinely novel idea that connects real options theory to an important applied question (how much do AI labs believe in transformative AI?). The Dario dilemma result (asymmetric value losses from belief mismatches) is economically interesting. The combination of real options, strategic games, and structural credit risk provides sufficient technical depth.

- [ ] **Methodological rigor: HAS ISSUES.** For the RFS/JF target, the proofs need to be tightened (see Section 1.3 above). The model combines existing building blocks (GBM demand, Leland default, Tullock contest, Poisson regime switching) rather than introducing fundamentally new mathematical techniques. This is fine for RFS/JF but would not pass Econometrica's standards.

- [x] **Formatting and conventions: PASS.** The paper uses Econometrica formatting via Quarto/lualatex, which is appropriate for a working paper. The proposition-proof structure is standard.

- [ ] **Best target journal: Review of Financial Studies (RFS).** The paper sits at the intersection of real options, strategic investment, and structural credit risk -- all core RFS topics. The application to AI infrastructure is timely and provides a compelling empirical hook. RFS publishes structurally similar papers (cf. Hackbarth & Mauer 2012, Sundaresan, Wang & Yang 2015). The JF would be a secondary target, valuing the applied novelty and policy relevance but wanting stronger empirical content. Econometrica is a reach given the proof quality and the calibration-rather-than-estimation methodology.

---

### 4. Figures

#### 4.1 Paper Figures

All 10 figures are generated by `paper/generate_figures.py` (lines 630-642). Assessment:

| # | Figure | Accuracy | Labels/Legends | Quality | Issues |
|---|--------|----------|----------------|---------|--------|
| 1 | Sample paths | Correct | Correct | Good | Initial condition documentation |
| 2 | Option value F_H | Correct | Correct | Good | None |
| 3 | Comparative statics | Correct | Correct | Good | Panel (d) labels $\delta$ as "Depreciation" but `parameters.py` describes it as "operating cost per unit of capacity" |
| 4 | Lambda option value | Correct | Correct | Good | None |
| 5 | Default boundaries | Correct | Mostly correct | Good | Default boundary line is labeled generically but shows only the follower's $X_D$ |
| 6 | Credit risk | Correct | Correct | Good | None |
| 7 | Competition effect | Correct | Correct | Good | None |
| 8 | Firm comparison | **POTENTIAL ISSUE** | Correct in code | Good | See below |
| 9 | Lambda timeline | Correct | Correct | Good | None |
| 10 | Growth decomposition | Correct | Correct | Good | None |

**Figure 8 data-figure mismatch:** The code in `generate_figures.py:500-540` computes CapEx intensity as `f.capex_2025 / f.revenue_2025`, which with current `data.py` values gives Anthropic-like = 2.00, OpenAI-like = 1.25, Google-like = 1.09, CoreWeave-like = 2.00. However, visual inspection of the rendered `fig_firm_comparison.png` shows values that do not match these computed ratios (bars appear at approximately 0.55, 0.65, 2.5, 3.7). This strongly suggests the figure PNG was generated from a **previous version of the calibration data** and has not been regenerated after the data was updated. **The figures need to be regenerated to match the current `data.py` values.**

#### 4.2 Code-Figure Consistency (3 traces)

**Trace 1: `fig_option_value` (Figure 2):**
- `ModelParameters()` -> `SingleFirmModel(p)` -> `optimal_trigger_and_capacity("H")` -> grid `[0.001*X*, 3*X*]` with 300 points -> `option_value_H(x)` and `installed_value(x, K*, "H") - investment_cost(K*)` -> plot with "value of waiting" shaded region.
- **Verified correct.** Option value smoothly connects to NPV at X* (smooth-pasting); F_H >= NPV everywhere.

**Trace 2: `fig_default_boundaries` (Figure 5):**
- `ModelParameters()` -> leverage grid 0.05-0.65 (40 points) -> for each: `DuopolyModel(p, leverage=lev)` -> `solve_preemption_equilibrium("H")` -> extract follower trigger, leader trigger, default boundary.
- **Verified correct** with minor labeling issue (shows follower's default boundary only, not labeled as such).

**Trace 3: `fig_firm_comparison` (Figure 8):**
- `get_baseline_calibration()` -> extract 4 `FirmData` objects -> compute CapEx intensity and revenue growth -> bar chart and scatter plot.
- **Data-figure mismatch detected** (see Section 4.1 above).

#### 4.3 Slide Figures

Slide figures reference paper PNGs from `slides/long-form/figures/`. If the paper figures are regenerated to fix the Figure 8 mismatch, the slide figures must also be updated to maintain consistency.

---

### 5. Calibration and Results

#### 5.1 Parameter Values

| Parameter | Value | Source | Assessment |
|-----------|-------|--------|------------|
| $\mu_L = 0.01$ | Baseline cloud growth | Industry data | Reasonable |
| $\mu_H = 0.06$ | Transformative AI regime growth | Calibration | **Seems low** -- industry revenue growth in the AI boom period has been 50-100%+. While these are risk-neutral demand process parameters, not revenue growth rates, the gap deserves discussion. |
| $\sigma_L = 0.25$, $\sigma_H = 0.30$ | Demand volatility | Industry data | Reasonable |
| $r = 0.12$ | WACC | Corporate finance | Reasonable for high-growth tech |
| $\alpha = 0.40$ | Returns to scale | GPU utilization | Reasonable; well-justified (doubling capacity gives $2^{0.4} \approx 1.32\times$ revenue) |
| $\gamma = 1.50$ | Cost convexity | Anecdotal (power, supply chain) | Reasonable but could benefit from specific data center cost curve citations |
| $\delta = 0.03$ | Operating cost / depreciation | Calibration | **Seems low** -- GPU hardware depreciates at 20-33% per year. The distinction from accounting depreciation is noted but the gap is large. |
| $c = 1.00$ | Unit cost (normalized) | Normalization | Fine |

#### 5.2 Sensitivity

- [ ] **HAS ISSUES.** The paper describes sensitivity analysis qualitatively (`_appendix.qmd` Appendix D, lines 161-174: parameter sensitivity $\pm 25\%$, alternative contest functions, alternative regime structure). However, **no formal sensitivity table or tornado chart** is provided. The comparative statics figures (Figure 3) show how triggers/capacities vary with parameters, but there is no systematic table showing the elasticity of key outputs ($X^*$, $K^*$, implied $\hat{\lambda}$) to each parameter. Adding this would substantially strengthen the calibration section.

#### 5.3 Comparative Statics

- [x] **PASS.** The comparative statics are consistent with economic intuition and verified numerically:
  - Higher $\sigma$ raises trigger (option value of waiting increases) -- verified by `test_higher_sigma_higher_trigger_H`
  - Higher $\alpha$ raises trigger (revenue more sensitive to capacity)
  - Higher $\gamma$ raises trigger (investment more costly)
  - Higher $\lambda$ lowers trigger (urgency of investing increases) -- verified by `test_higher_lambda_lower_trigger` (`test_calibration.py:54`)
  - Leader trigger below follower trigger -- verified by `test_leader_trigger_below_follower`
  - Default boundary rises with leverage -- verified by `test_higher_leverage_higher_default_boundary`
  - More firms raise individual trigger, decrease individual capacity, increase total capacity -- verified by `test_more_competitors_higher_trigger`, `test_more_firms_higher_triggers`

#### 5.4 Revealed Beliefs Results

- [ ] **HAS ISSUES.** The implied $\hat{\lambda}$ values are plausible at the firm level:
  - Anthropic-like: $\hat{\lambda} = 0.95$ (expected switch in 1.1 years) -- consistent with public statements about short AGI timelines
  - OpenAI-like: $\hat{\lambda} = 0.25$ (4 years)
  - Google/Alphabet-like: $\hat{\lambda} = 0.20$ (5 years) -- consistent with a diversified firm hedging
  - CoreWeave-like: $\hat{\lambda} = 0.95$ (1.1 years)

  However, the **identical** $\hat{\lambda}$ for Anthropic-like and CoreWeave-like (both = 0.95) despite very different business models (frontier AI lab vs. GPU cloud) and leverage (0.20 vs. 0.70) is suspicious. Both have CapEx/Revenue = 2.00, suggesting the inversion is primarily driven by this single ratio. This needs investigation (see Section 3a above).

#### 5.5 Growth Decomposition

- [x] **PASS.** The three-component decomposition (assets-in-place, counterfactual capacity, regime switch) is correctly computed in `valuation.py` (`growth_option_decomposition` function). The finding that growth options account for 60-80% of value is economically intuitive for AI firms. The test `test_fractions_sum_to_one` (`test_valuation.py:43`) verifies accounting consistency.

---

### 6. Slides Review

The slides are located in `slides/long-form/` as Quarto RevealJS files.

#### 6.1 Completeness

- [x] **PASS.** The slides cover all key contributions: model development (`_model.qmd`), results including comparative statics and equilibrium properties (`_results.qmd`), calibration (`_calibration.qmd`), revealed beliefs (`_revealed_beliefs.qmd`), and conclusions with policy implications (`_conclusion.qmd`). The Dario dilemma and growth decomposition are prominently featured.

#### 6.2 Clarity

- [x] **PASS.** The slides are readable and reasonably self-contained for a 40-50 minute conference presentation. Math is appropriately simplified -- only the most essential equations appear on slides, with the full derivations left to the paper. The calibration table is clearly presented.

#### 6.3 Consistency with Paper

- [ ] **HAS ISSUES.** Several numerical claims in slide text do not match the model outputs or figures:

  1. **`_calibration.qmd` line 42:** Claims "X* ~ 0.49, K* ~ 0.55" but the model with default parameters produces X* ~ 0.016 (visible in `fig_sample_paths.png` legend: X_H* = 0.0159). Off by a factor of ~30. Either the calibration parameters used for these numbers differ from the code defaults, or the numbers are wrong.

  2. **`_calibration.qmd` line 46:** Claims "Follower: X_F ~ 0.66, K_F ~ 0.42" but `fig_default_boundaries.png` shows follower triggers around X ~ 1.0 at low leverage.

  3. **`_model.qmd` line 106:** Claims "Preemption cuts leader trigger to ~50% of monopolist" but `fig_competition_effect.png` panel (b) shows trigger ratios of approximately 0.1-0.3 across the volatility range, much lower than 50%.

  4. **`_results.qmd` line 52:** Claims "growth options exceed 60% of value at K/K* < 0.3" but `fig_growth_decomposition.png` panel (b) shows the growth fraction dropping below 60% by approximately K/K* = 0.1.

  5. **`_revealed_beliefs.qmd` line 36:** Claims "default prob. ~40% at leverage=0.70" but `fig_credit_risk.png` shows approximately 37%. Minor rounding issue.

  6. **Figure 8 mismatch with calibration table:** The slide table lists CapEx/Revenue as 2.00, 1.25, 1.09, 2.00 (matching code), but the rendered `fig_firm_comparison.png` shows different values (~0.56, 0.66, 2.5, 3.7).

  7. **Missing Dario dilemma figure:** Three slides discuss the Dario dilemma (`_revealed_beliefs.qmd` lines 40-96) without a supporting figure, despite a Dario dilemma heatmap existing in the phase5 figure code.

  8. **Default boundary formula on slide may not match code:** The formula shown on `_model.qmd` line 88 appears to conflate components of the equity value with the default boundary formula as implemented in `duopoly.py:126-161`.

---

## Summary of Issues

### Critical Issues

1. **Figure 8 data-figure mismatch.** The rendered `fig_firm_comparison.png` appears inconsistent with current calibration data in `data.py`. The figure needs to be regenerated by running `paper/generate_figures.py`. This affects both the paper and slides.
   - *Fix:* Run `python paper/generate_figures.py` to regenerate all figures from current data.

2. **Slide numerical claims do not match model outputs.** Multiple numerical values stated in slide text are inconsistent with what the model produces:
   - "X* ~ 0.49" (`_calibration.qmd:42`) vs actual X* ~ 0.016 (factor of ~30 off)
   - "Follower X_F ~ 0.66" (`_calibration.qmd:46`) vs figure showing X_F ~ 1.0
   - "Preemption cuts trigger to ~50%" (`_model.qmd:106`) vs figure showing ~10-30%
   - "Growth options exceed 60% at K/K* < 0.3" (`_results.qmd:52`) vs figure showing <60% by K/K* ~ 0.1
   - *Fix:* Recompute all numerical claims from the current model code and update slide text to match. The discrepancy may stem from a parameter change after the text was written.

### Major Issues

3. **Incomplete proofs for Propositions 1, 4(iii), and 6** (`_appendix.qmd`). Proposition 1's capacity derivation uses an informal asymptotic argument. Proposition 4(iii) asserts total capacity increases with N without a formal bound. Proposition 6 is qualitative, lacking a formal magnitude comparison.
   - *Fix:* For Prop 1, provide the full FOC for the general $\delta > 0$ case or explicitly state it as a fixed-point characterization. For Prop 4(iii), either prove the bound $f^\alpha > 1 - 1/N$ or weaken the statement to a numerical finding. For Prop 6, add a Taylor expansion around $\lambda_{\text{true}}$ showing the asymmetry formally.

4. **Identification concern for revealed beliefs.** Anthropic-like and CoreWeave-like produce identical $\hat{\lambda}$ despite different WACCs, leverage, and business models, both having CapEx/Revenue = 2.00. The inversion may be primarily driven by a single sufficient statistic.
   - *Fix:* Report the partial sensitivity $\partial\hat{\lambda}/\partial r$, $\partial\hat{\lambda}/\partial\ell$, etc. to demonstrate that firm-specific parameters contribute to the cross-section. If they don't, be transparent about this limitation.

5. **Notation overloading.** $D$ used for three meanings (option value constant, face value of debt, debt value function). Coupon notation ($c_d$, $c_D$, $d$) is inconsistent.
   - *Fix:* Rename the option value constant $D_L$ to $G_L$ or $\tilde{C}$. Define coupon notation clearly and consistently.

6. **10 orphaned bibliography entries.** References in `.bib` never cited in the text, including directly relevant ones (Pawlina & Kort 2006, Epoch AI 2024, Korinek 2024).
   - *Fix:* Either cite these references where relevant (several naturally fit) or remove them from `references.bib`.

7. **Risk-neutral vs. WACC pricing tension.** The discussion (`_discussion.qmd` line 69) lists "risk neutrality" as a limitation, but the model uses WACC (which includes risk premiums) as the discount rate, not the risk-free rate. The paper should clarify whether it uses risk-neutral pricing with risk-adjusted drift or simply discounts at WACC.
   - *Fix:* Add a footnote or remark in Section 2 clarifying the pricing approach. If using the contingent claims approach, specify the risk-adjusted drift explicitly.

### Major Issues (Paper-Code Discrepancies)

8. **Debt recovery value formula differs between paper and code.** The paper (`_model.qmd` line 171) defines recovery as $(1-b) V_s(X_D, K)$ where $V_s = A X_D K^\alpha s - \delta K/r$ (net of operating costs). The code (`duopoly.py:270`) computes recovery as `(1-b) * (V_XD + delta*K/r)` = $(1-b) \cdot A X_D K^\alpha s$ (gross asset value, adding back $\delta K/r$). This makes debt slightly more valuable in the code than the paper implies. For baseline parameters ($\delta=0.03$, $r=0.12$, $K \approx 1$), the difference is $(1-b)\delta K/r \approx 0.175$ per unit capacity -- material for credit spread calculations.
    - *Fix:* Either update the code to use net installed value (remove `+ p.delta * K_i / p.r`), or update the paper formula to reflect the gross-asset-value interpretation.

9. **Dario dilemma omits timing discount factor.** The paper's appendix (line 103) includes a $(X_0/X^*)^{\beta(\lambda_{\text{true}})}$ discounting factor in the NPV calculation. The code (`valuation.py:228-290`) computes NPV at the trigger without this factor, evaluating `V(X*, K*) - I(K*)` directly. This ignores the time value of reaching different triggers sooner or later, weakening the timing channel of mismatch costs.
    - *Fix:* Multiply by `(X_0 / X_star) ** beta_true` to include the timing discount, or document this as a simplification in the paper.

### Major Issues (Additional Code Findings)

10. **N-firm contest share bug with training fraction.** In `nfirm.py:79-81`, the firm adjusts its own capacity for training (`K_i_inf = K_i * (1 - training_fraction)`), but competitor capacities in the denominator use raw `K^alpha` without adjusting for training. When all firms use the same training fraction, competitors' capacities should also be adjusted. The impact is zero when `training_fraction=0.0` (the default), but produces incorrect results if training allocation is enabled. The docstring says "competitors' inference capacities" but callers in `solve_sequential_equilibrium` (lines 239-253) pass total capacities.
    - *Fix:* Either adjust competitor capacities by `(1 - training_fraction)` in `contest_share`, or ensure callers pass inference-only capacities.

11. **Potential non-additive value decomposition (double-counting in regime L).** In `valuation.py:66-83`, the growth option decomposition may double-count the regime switch value. `option_val` (from `option_value_L`) already embeds the switching option, and `regime_switch` is computed separately as `F_L - F_L_no_switch`. Then `expansion_option = option_val - assets`, and `total = assets + expansion_option + regime_switch`. If `option_val` includes both expansion and switching components, `expansion_option` already contains part of the switching value.
    - *Fix:* Verify the decomposition is additive by construction, or adjust `expansion_option` to subtract `regime_switch`.

12. **Missing guard for `horizon=0` in `default_probability`.** In `valuation.py:190-192`, `sigma * np.sqrt(horizon)` in the denominator gives division by zero when `horizon=0`.
    - *Fix:* Add `if horizon <= 0: return 0.0` guard at the start of the function.

### Minor Issues

10. **"We" with single author.** "We" is used throughout all paper files but only one author is listed.
   - *Fix:* Change to "I" throughout, or add co-authors.

11. **Missing sensitivity table.** No formal table showing elasticities of key outputs to each parameter. Only qualitative descriptions and comparative statics figures.
   - *Fix:* Add a table in the calibration section or appendix showing $\Delta X^*/\Delta\theta$, $\Delta K^*/\Delta\theta$, $\Delta\hat{\lambda}/\Delta\theta$ for each parameter $\theta$.

12. **Quality dynamics never revisited.** Introduced in `_extensions.qmd` (line 76) but never used in calibration or valuation sections.
   - *Fix:* Either integrate into the calibration/revealed beliefs or note explicitly that this extension is illustrative.

13. **Unbounded quality growth.** The quality dynamics $Q(t) = A \cdot (\phi K \cdot (t-\tau))^\eta$ grows without bound as $t \to \infty$, contradicting diminishing returns.
    - *Fix:* Add a saturation mechanism or discuss this limitation.

14. **Depreciation parameter $\delta = 0.03$ seems low.** GPU hardware depreciates at 20-33% per year. The distinction from accounting depreciation is noted but the gap deserves more discussion.
    - *Fix:* Add a paragraph explaining why $\delta$ captures net operating costs rather than accounting depreciation, and discuss sensitivity to higher values.

15. **$\mu_H = 0.06$ may understate transformative AI regime.** Industry growth rates during AI booms have been much higher. While these are risk-neutral rates, the gap deserves discussion.
    - *Fix:* Add discussion of why the risk-neutral growth rate is substantially below the physical growth rate.

16. **Soft assertions in tests.** Several tests use conditional assertions (`if condition: assert ...`) that silently pass when preconditions aren't met, masking potential failures.
    - *Fix:* Replace soft assertions with unconditional assertions, or add explicit `else: pytest.skip("reason")` to make non-testing visible.

17. **Tautological test `test_symmetric_duopoly_revenue`.** Calls the same function with identical arguments twice.
    - *Fix:* Test symmetry by swapping $K_i$ and $K_j$ arguments and verifying equal revenue.

18. **Default boundary label in Figure 5.** Shows only the follower's $X_D$ but labels it generically.
    - *Fix:* Label as "Follower default boundary $X_{D,F}$" or show both firms' boundaries.

19. **Missing important equation labels.** The equity value formula, debt value formula, leader value formula, credit spread formula, and default probability formula are unnumbered and cannot be cross-referenced.
    - *Fix:* Add equation labels for key formulas that are referenced in the text or code.

20. **`simulate_demand` non-deterministic by default.** Creates unseeded RNG when no generator is provided (`base_model.py:335`).
    - *Fix:* Either require a seed/generator parameter or document the non-deterministic default behavior.

---

## Overall Recommendation

**Revise and resubmit.**

The paper presents a genuinely novel contribution with the "revealed beliefs" methodology, a well-constructed real options framework, and a timely application to AI compute infrastructure. The code is generally correct and well-engineered, with faithful implementation of the paper's mathematical propositions (all verified via systematic cross-validation). However, the paper needs moderate revision before submission to a top journal:

1. **Critical:** Regenerate all figures from current calibration data
2. **Major:** Complete the proofs, resolve notation issues, investigate the identification concern, clean up the bibliography, and clarify the pricing approach
3. **Minor:** Add sensitivity tables, fix author voice, address edge cases in tests

**Recommended target journal: Review of Financial Studies**, with the Journal of Finance as a secondary target. Econometrica requires substantially more rigorous proofs and a sharper theoretical contribution.
