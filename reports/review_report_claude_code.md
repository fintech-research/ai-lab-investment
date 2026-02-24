# Review Report: AI Lab Investment

**Reviewer:** claude_code
**Date:** 2026-02-24

## Executive Summary

This report reviews the research project "Investing in Artificial General Intelligence" by Vincent Gregoire (HEC Montreal), covering both code validation and paper quality. The project develops a real options model of irreversible AI compute capacity investment under regime switching, duopoly competition, endogenous default, and diminishing returns calibrated to AI scaling laws.

The codebase is well-structured and the core model modules (base_model, duopoly, nfirm, valuation) have good test coverage (76--100%). However, two high-severity bugs were identified in the duopoly default boundary computation: (1) the negative characteristic root uses the wrong discount rate (`-r` instead of `-(r + lambda_tilde)`), introducing an ~11% error in the default boundary, and (2) the equity value default option bracket double-counts the operating cost term and omits the equity contribution, causing the smooth-pasting condition $E(X_D) = 0$ to fail analytically. These bugs affect all results involving leverage and default risk (Proposition 2 quantitative magnitudes, Proposition 3 parts iv--v, credit spreads, and the AI investment dilemma with leverage). Additionally, the paper's stated baseline results ($X^* \approx 0.49$, $K^* \approx 0.55$, $\phi^* \approx 0.30$) are stale and do not match current code output ($X^* = 0.027$, $K^* = 0.055$, $\phi^* = 0.701$). Several text-figure discrepancies were also identified.

The paper is ambitious, well-written, and addresses a genuinely important question. The training-inference allocation is a novel addition to the real options literature, and the "faith-based survival" mechanism is an elegant result. With the code bugs fixed, baseline results updated, and figures reconciled with text, the paper would be competitive at RFS, which is the recommended target journal.

---

## Part 1: Code Validation

### 1. Mathematical Correctness

- [x] **Propositions vs. code (regime switching, A_eff, option values)**: The regime-switching demand process, the positive characteristic root $\beta_L^+$, the present-value multipliers $A_L$ and $A_H$, the particular solution coefficient $C$, and the effective revenue coefficient $A_{\text{eff}}$ are all correctly implemented. Specifically:
  - `parameters.py:137` correctly uses `_positive_root(sigma_L, mu_L, r + lam)`, incorporating $r + \lambda$ as the effective discount rate. At baseline, $\beta_L^+ = 3.015$, matching the paper's stated $\approx 3.01$.
  - `parameters.py:139-144` computes $A_L = (r - \mu_H + \lambda) / [(r - \mu_H)(r - \mu_L + \lambda)]$, correctly combining L-regime discounting with H-regime continuation value.
  - `base_model.py:151-168` computes $C = -\lambda B_H / Q_L(\beta_H)$ where $Q_L(\beta_H) = \tfrac{1}{2}\sigma_L^2 \beta_H(\beta_H - 1) + \mu_L \beta_H - (r + \lambda)$. Correctly uses $r + \lambda$. Matches paper Equation 12.
  - `base_model.py:431-454` computes $A_{\text{eff}}$ with the correct denominator $r - \mu_L + \lambda$ and correct H-regime term. Matches paper Equation 7.
  - **PASSES** for all non-default-related formulas.

- [ ] **Propositions vs. code (default boundary — `_negative_root`)**: **HAS ISSUES.**
  - **File:** `src/ai_lab_investment/models/duopoly.py:348-361`
  - **Bug:** The function `_negative_root` computes the negative root of the L-regime characteristic equation using `c = -p.r` (line 359). The paper (`_model.qmd:307`) specifies the discount rate should be $r + \tilde{\lambda}$ (i.e., `c = -(p.r + lam_tilde)`), incorporating the regime-switching term.
  - **Numerical impact:** With baseline parameters, the code computes $\beta^-_{\text{neg}} = -1.649$ while the paper formula gives $\beta^-_{\text{neg}} = -2.335$. The default boundary multiplier $\beta^- / (\beta^- - 1)$ is 0.622 (code) vs. 0.700 (paper) — an **11.1% relative error** in the default boundary.
  - **Affected functions:** `default_boundary()` (line 339), `equity_value()` (line 404), and `debt_value()` (line 442).
  - **Fix:** Change line 359 from `c = -p.r` to `c = -(p.r + lam_tilde)` where `lam_tilde` is obtained from `self._effective_lambda(phi_i, K_i)`.

- [ ] **Propositions vs. code (equity value formula)**: **HAS ISSUES.**
  - **File:** `src/ai_lab_investment/models/duopoly.py:411-415`
  - **Bug:** The code computes `default_claim = c_D / p.r + p.delta * K_i / p.r - V_XD`, where `V_XD = A_eff * X_D - delta * K / r`. Expanding: `default_claim = c_D/r + 2*delta*K/r - A_eff*X_D`.
  - The paper (`_model.qmd:347`) specifies the default option bracket as $[c_D/r + \delta K/r + (1-\ell)I(K) - A_{\text{eff}} X_D]$.
  - **Discrepancy:** The code has `2 * delta*K/r` where the paper has `delta*K/r + (1-ell)*I(K)`. The code double-counts the operating cost term and omits the equity contribution $(1-\ell)I(K)$.
  - **Consequence:** The smooth-pasting condition $E(X_D) = 0$ is not analytically satisfied. With $K = 1.0$ and leverage $= 0.30$, the raw $E(X_D) = -0.45$ (should be 0). The `max(equity, 0.0)` clamp on line 416 masks the error at runtime.
  - **Fix:** Replace the default_claim computation with:
    ```python
    equity_contribution = (1 - p.leverage) * self._investment_cost(K_i)
    default_claim = c_D / p.r + p.delta * K_i / p.r + equity_contribution - a_eff * X_D
    ```

- [ ] **Paper baseline results vs. code output**: **HAS ISSUES.**
  - **Paper** (`_calibration.qmd:131-132`): States $X^* \approx 0.49$, $K^* \approx 0.55$, $\phi^* \approx 0.30$ for the single-firm model, and $X_F \approx 0.66$, $K_F \approx 0.42$, $\phi_F \approx 0.25$ for zero-leverage duopoly.
  - **Code output** (from `SingleFirmModel.optimal_trigger_capacity_phi()`): $X^* = 0.027$, $K^* = 0.055$, $\phi^* = 0.701$.
  - **Discrepancy:** The paper's stated values are completely inconsistent with the code. The project memory confirms $\phi^* \approx 0.701$ at baseline, indicating the paper text is stale from a previous model version. The $\phi^*$ value is particularly off: 0.30 in the paper vs. 0.701 in the code.
  - **Fix:** Update `_calibration.qmd` lines 131-132 with the correct baseline values from the current code.

- [x] **Proofs (Appendix A)**: The proof of Proposition 1 (Appendix A) is logically complete. The Inada conditions argument (Step 5) correctly establishes that $\partial A_{\text{eff}}/\partial\phi \to +\infty$ as $\phi \to 0^+$ and $\partial A_{\text{eff}}/\partial\phi \to -\infty$ as $\phi \to 1^-$, with strict concavity guaranteeing uniqueness. The comparative statics follow from the implicit function theorem. **PASSES.**

- [x] **Numerical methods**: Root-finding in `revealed_beliefs.py` uses `scipy.optimize.brentq` with appropriate brackets and tolerance. The backward induction in `nfirm.py` follows the standard sequential-move construction. The multi-start Nelder-Mead optimization in `base_model.py` and `duopoly.py` explores a grid of starting points. The particular solution coefficient $C$ in `base_model.py:166` guards against near-zero denominators (`abs(Q_L) < 1e-15`). **PASSES**, though the `1e-15` threshold is tight (see Code Quality section).

- [ ] **Parameter consistency**: **MINOR ISSUE.**
  - All primitive parameters match between `models/parameters.py` and Table 3 (`@tbl-param-mapping`) in `_calibration.qmd`: $r = 0.12$, $\mu_L = 0.01$, $\mu_H = 0.06$, $\sigma_L = 0.25$, $\sigma_H = 0.30$, $\lambda_0 = 0.05$, $\xi = 0$, $\eta = 0.07$, $\alpha = 0.40$, $\gamma = 1.50$, $c = 1.0$, $\delta = 0.03$, $c_d = 0.05$, bankruptcy cost $= 0.30$.
  - **Inconsistency:** The paper's Table 3 lists $\lambda_0 = 0.05$ with $\xi = 0$, which by Equation 2 implies $\tilde{\lambda} = \lambda_0 = 0.05$. However, the paper text (`_calibration.qmd:40`) says "the total effective rate $\tilde{\lambda} = 0.10$ per year." The code resolves this via a separate `lam = 0.10` attribute in `parameters.py:54`. The table should either list $\lambda_0 = 0.10$ or explain the additional implicit component.

- [x] **Regime switching implementation**: All components are correctly implemented. The positive root uses $r + \lambda$, the H-regime is absorbing, the demand simulation (`base_model.py:327-372`) uses standard Euler-Maruyama with Poisson switching. **PASSES.**

---

### 2. Code Quality and Testing

- [x] **Test coverage**: 217 tests pass with **52% overall coverage**. Core model modules have strong coverage:

  | Module | Coverage |
  |:-------|:---------|
  | `models/base_model.py` | 89% |
  | `models/duopoly.py` | 86% |
  | `models/nfirm.py` | 90% |
  | `models/parameters.py` | 76% |
  | `models/valuation.py` | 89% |
  | `calibration/revealed_beliefs.py` | 86% |
  | `calibration/data.py` | 100% |
  | `figures/phase*.py` | 0% each |
  | `pipeline.py` | 0% |
  | `utils/` | 0% |

  The 52% headline is depressed by zero-coverage figure generation and pipeline orchestration code, which is acceptable for a research project. The main gap worth closing is `parameters.py` at 76% — several validation branches (lines 87-132) for `r <= 0`, `sigma <= 0`, `lam < 0`, etc. are untested.

- [ ] **Test meaningfulness**: **MOSTLY PASSES**, with some weak tests flagged.

  **Strengths:** The test suite checks economically meaningful properties:
  - Smooth-pasting and value-matching at the trigger (`test_base_model.py:63-78`)
  - Option exceeds NPV before trigger (`test_base_model.py:90-95`)
  - Higher volatility raises investment trigger (`test_base_model.py:142`)
  - Leader invests before follower (`test_duopoly.py:251-254`)
  - Preemption lowers trigger vs. monopolist (`test_duopoly.py:301-304`)
  - More competitors raise trigger (`test_nfirm.py:72-78`)
  - Contest shares sum to one (multiple files)
  - Symbolic verification of analytical expressions (`test_symbolic_duopoly.py`)

  **Weaknesses — potentially vacuous tests:**
  - `test_base_model.py:124-133` (`test_with_high_alpha_has_L_trigger`): Uses `pytest.skip` if the condition under test doesn't hold, so it silently passes if the parameter regime changes. Should hard-assert the precondition.
  - `test_valuation.py:121-142` (`test_matched_beliefs_no_loss` and related): Guards with `if "error" not in result`, meaning tests pass even when computation fails. In the matched-beliefs case, this should be `assert "error" not in result`.
  - `test_calibration.py:72-78` (`test_higher_lambda_lower_trigger`): Docstring says "Higher lambda should lower the trigger" but assertions only check positivity, not the ordering $X_{\text{hi}} < X_{\text{lo}}$. Name is misleading.
  - `test_calibration.py:95-98`: Assertion `recovered is None or recovered >= 0` is extremely weak — any return value passes.

- [ ] **Edge cases**: **HAS GAPS.**
  - No test for `lambda = 0.0` (the `lam = 0` path has special handling at `base_model.py:157` and `parameters.py:139-144` but is untested).
  - No test for `sigma -> 0` (the `_positive_root` function at `parameters.py:253` has `2 * a` in the denominator where `a = 0.5 * sigma^2`; sigma = 0 causes division by zero). Parameter validation guards this at the caller level, but the guard itself is untested.
  - No test for $N = 1$ in `NFirmModel`.
  - No test for very high lambda values ($\lambda > 1.0$).

- [ ] **Numerical stability**: **HAS ISSUES.**
  - **Active overflow warnings** (CONFIRMED): Test output shows 8 `RuntimeWarning`s for overflow in `duopoly.py` during comparative statics over $\sigma \in [0.25, 0.45]$:
    - `duopoly.py:285`: `overflow encountered in scalar power` (`c * K**gamma` for large K)
    - `duopoly.py:740`: `overflow encountered in scalar multiply` (`markup * total_cost / a_eff`)
    - `duopoly.py:511`: Same overflow pattern in `_follower_trigger`
    - `duopoly.py:778`: `invalid value encountered in scalar subtract` (`leader_val - follower_opt`)
    These produce `inf` or `nan` that propagate silently. **Fix:** Add overflow guards:
    ```python
    if total_cost > 1e15 or a_eff < 1e-15:
        return np.inf
    ```
  - **Tight denominator guard**: `base_model.py:166` uses `abs(Q_L) < 1e-15` — a wider threshold like `1e-10` would be safer.
  - **No convergence flag in NFirmModel**: `nfirm.py:234-271` warns on non-convergence but still returns the non-converged result. Callers have no way to detect unreliable output.
  - **Division by zero in `_positive_root`**: `parameters.py:253` divides by `2 * a` where `a = 0.5 * sigma^2`. If called directly with sigma = 0, this fails. The function should have its own guard.

- [x] **Code organization**: The codebase is well-structured. Clean module hierarchy with no circular imports, consistent API patterns across models (`solve_*`, `summary()`, `comparative_statics()`), effective use of caching, and good docstrings with economic interpretation.

  **Minor code smells:**
  - Copy-pasted multi-start optimization loops appear 4 times across `base_model.py` and `duopoly.py`. Could be extracted into a shared helper.
  - Magic number `1e20` used as sentinel in 6 places, with inconsistent threshold `1e19` for checking. Should be a named constant.
  - String-based regime dispatch (`regime == "H"`) with no validation — a typo like `"h"` silently picks the L-regime else branch.

- [x] **Reproducibility**: Core computations are deterministic (analytical solutions + scipy optimizers with fixed starting grids). The `simulate_demand` method accepts an optional `rng` argument; figure code uses `seed=42`. Tests pass explicit seeds. The `conf/config.yaml` has no global seed setting, but this is acceptable since the pipeline's non-simulation outputs are deterministic. **PASSES.**

---

## Part 2: Paper and Presentation Review

### 3. Paper Content Review

#### 3a. Structure and Argument

- [x] **Motivation**: The introduction is compelling and well-motivated. The opening paragraph effectively establishes scale ($200B+ in 2024, $660-690B projected for 2026) and irreversibility. Executive quotes (Pichai, Huang, Amodei, Altman, Musk, LeCun) do real analytical work: they illustrate the dispersion in beliefs the model explains, not merely add color. **PASSES.**

- [ ] **Literature positioning**: The literature review (`_literature.qmd`) is thorough and well-organized around four building blocks. **HAS MINOR GAPS:**
  - **Dixit (1989)** "Entry and Exit Decisions under Uncertainty" (JPE) — the canonical hysteresis paper — is absent despite the paper's emphasis on irreversibility and default boundaries.
  - **Pastor and Veronesi (2009)** on technological revolutions and stock prices — the regime switching to a new technology paradigm is exactly their setting.
  - **Trigeorgis (1996)** on compound options and sequential investment, relevant to the staged investment discussion.
  - **Grenadier and Malenko (2011)** on real options signaling, relevant to the strategic signaling channel in the AI investment dilemma (Section 4).
  - **Lambrecht and Perraudin (2003)** on real options in duopoly with incomplete information — relevant given the paper's heterogeneous beliefs mechanism.

- [x] **Model building**: The progression from single firm (Section 2.3) to duopoly (Section 2.4) is natural and well-executed. The single-firm benchmark establishes key objects ($A_{\text{eff}}$, the training-inference trade-off, the option premium) before introducing strategic interaction. The notation table (Table 1) is a welcome aid. **PASSES**, though Section 2.4 introduces contest structure, capital structure, default, and preemption simultaneously — consider splitting into two subsections.

- [x] **Identification**: The paper is commendably honest about limitations. The introduction calls the revealed beliefs exercise "illustrative," the conclusion explicitly distinguishes it from "structural estimation," and the calibration section flags $\pm 0.10$ uncertainty in training fractions. **PASSES.**

- [x] **Conclusion**: Summarizes findings effectively around three tensions (current cash flow vs. future capability, growth-option upside vs. default risk, waiting value vs. preemption pressure). Avoids overclaiming. Future directions are well-chosen. **PASSES.**

  One suggestion: the $600B revenue gap figure (citing Cahn 2024) may be outdated. Consider updating.

#### 3b. Writing Quality

- [x] **Clarity**: Writing is excellent — concise, formal, and at the standard expected by JF/RFS. Technical passages are clear. Footnotes are informative without being distracting. **PASSES.**

  Minor: The Tullock revenue function (Equation 5) uses $[(1-\phi_i)K_i]^{2\alpha}$ in the numerator — a brief note explaining this equals capacity $\times$ share would prevent reader confusion.

- [ ] **Notation**: **HAS ISSUES.**
  - **$\lambda$ vs. $\tilde{\lambda}$ vs. $\lambda_0$:** Three related symbols. The calibration states $\tilde{\lambda} = 0.10$ but the parameter table has $\lambda_0 = 0.05$ with $\xi = 0$, which by Equation 2 implies $\tilde{\lambda} = 0.05$. The slides use bare $\lambda$ throughout.
  - **$c_D$ vs. $c_d$ vs. $d$:** Section 2.4 defines the coupon as $d = c_d \cdot \ell \cdot I(K)$, but the default boundary uses $c_D$ for the same object. The relationship is in Appendix A but not at first use in the main text.
  - **$\beta_s^-$:** The generic subscript $s$ is confusing when default only occurs in regime L. Just write $\beta_L^-$.

- [x] **Length and focus**: The paper is long but not unreasonable for its scope. **Candidates for trimming:** the nesting remark (Section 2.3, lines 131-134) could be a footnote; the Cournot alternative discussion appears three times; the static-$\phi$ bias subsection could be shortened. A 10-15% reduction would better fit RFS norms.

- [x] **Abstract**: Well-crafted — states question, method, and main results in six sentences. One suggestion: replace "semi-analytical characterization" with "analytical existence and numerical characterization" for precision regarding Proposition 3.

#### 3c. Journal Fit

- [x] **Contribution significance**: The integration of training-inference allocation into a regime-switching real options framework with endogenous default is genuine and novel. The "faith-based survival" and "AI investment dilemma" are original mechanisms. The main weakness is thin empirical content: the calibration is illustrative, and revealed beliefs inverts on four stylized data points. **SUFFICIENT for RFS; challenging for JF or Econometrica.**

- [x] **Methodological rigor**: Meets technical standards, subject to fixing the bugs identified above. The paper is transparent about the analytical vs. numerical status of each result (Table 2). **PASSES.**

- [x] **Which journal fits best**: **RFS is the best target.** RFS publishes theory-with-calibration papers in the Leland tradition (Hackbarth, Mauer, and Robinson 2014; Sundaresan, Wang, and Yang 2015) and structural models with stylized calibrations. The Leland-based default mechanism and growth option decomposition fit the RFS audience well. JF tends to prefer either sharper theoretical results or stronger empirical identification. Econometrica requires methodological novelty (new solution concepts or existence theorems) that this paper does not provide.

---

### 4. Figures

- [ ] **Paper figures**: **HAS ISSUES on several figures.**

  | Figure | Assessment |
  |:-------|:-----------|
  | `fig_sample_paths` | **PASSES.** Clear, log scale appropriate, regime switch dots visible. Publication quality. |
  | `fig_option_value` | **PASSES.** Shaded "value of waiting" region effective. Smooth-pasting tangency visible. Publication quality. |
  | `fig_comparative_statics` | **MINOR ISSUE.** Panel (d) axis label says "Depreciation $\delta$" but the paper carefully calls this "Operating cost rate," not depreciation (Section 2.2, Section 3). The label should read "Operating cost rate $\delta$." |
  | `fig_lambda_option_value` | **PASSES.** Panel (a) shows concave increase in $F_L$, panel (b) shows coefficient $C$. Publication quality. |
  | `fig_default_boundaries` | **PASSES with caveat.** Communicates the "operating region" concept well. The leader trigger $X_P$ is nearly flat and very close to zero, making it hard to see. |
  | `fig_competition_effect` | **POTENTIAL ISSUE.** Verify that the ratio in panel (b) is labeled correctly — if the trigger ratio (duopoly leader / monopolist) exceeds 1.0, the text description ("ratio declines to approximately 0.5") would be inconsistent. The text and figure should be cross-checked after the code bugs are fixed. |
  | `fig_lambda_timeline` | **PASSES.** Clean, simple, effective. Publication quality. |
  | `fig_growth_decomposition` | **MINOR ISSUE.** Panel (a) legend text should be verified against the caption/text label for consistency. |
  | `fig_investment_dilemma` | **PASSES.** The most important figure; the asymmetry is visually striking. The leveraged case dramatically amplifies the right branch. Publication quality. |
  | `fig_firm_comparison` | **PASSES.** Clean two-panel figure. Minor: "Revenue growth (2024-2025x)" — the "x" suffix is non-standard. |
  | `fig_credit_risk` | **POTENTIAL ISSUE.** Verify that credit spread and default probability magnitudes match the text after code bug fixes. The text claims spreads exceed 1,200 bps at $\ell = 0.70$; this should be verified against the actual figure. |

- [ ] **Code-figure consistency**: Spot-checked 3 figures by tracing data flow through `paper/generate_figures.py`:
  - `fig_option_value`: Uses `SingleFirmModel.option_value_H()` and `npv_H()` — correctly computes $F_H(X) = B_H X^{\beta_H}$ and $V_H(X) = A_H X K^\alpha - cK^\gamma$. **PASSES.**
  - `fig_investment_dilemma`: Uses `ValuationAnalysis.dario_dilemma()` — computes value loss from mismatched beliefs. The pipeline is correct. **PASSES.**
  - `fig_default_boundaries`: Uses `DuopolyModel.default_boundary()` — **AFFECTED by the `_negative_root` bug** (Item 1 above). After fixing the bug, the default boundaries will shift and the figure should be regenerated.

- [x] **Slide figures**: Figures in `slides/long-form/figures/` are referenced from the paper's `paper/figures/` directory (shared figures). Consistency is maintained structurally. However, the slide text surrounding the figures is outdated (see Section 6 below).

---

### 5. Calibration and Results

- [x] **Parameter values**: Generally reasonable and appropriately caveated as "stylized." Specific comments:
  - $r = 0.12$ (WACC): Reasonable for a blended AI firm. Range 0.10--0.18 across archetypes is wide but justified.
  - $\mu_L = 0.01$: The L-regime drift of 1% (risk-adjusted) for AI demand seems conservative — cloud revenue grows 20-30% annually — but this is risk-neutral, so 1% is plausible if the AI equity premium is high. Deserves brief discussion.
  - $\alpha = 0.40$: The most critical parameter and the most weakly motivated. The paper argues "GPU utilization rates decline as capacity grows," but this is a utilization argument, not a revenue elasticity argument. The mapping is not explained. Sensitivity analysis shows this is among the highest-elasticity parameters. More disciplining is needed.
  - $\eta = 0.07$: The paper is honest that this is the calibration's weakest link — the mapping from neural scaling law exponents to arrival-rate elasticities has "no well-established empirical basis." Appropriately classified as "inferred" in the current revision.

- [ ] **Sensitivity**: **COULD BE IMPROVED.** Table E1 (Appendix E) provides univariate elasticities, which is adequate but minimal. The paper would benefit from: (a) two-way sensitivity plots for $r$ and $\alpha$ jointly, (b) confidence regions around revealed-belief estimates reflecting $\pm 0.10$ uncertainty in $\hat{\phi}$, and (c) the elasticity of the faith-based survival threshold $\underline{\phi}$ to key parameters.

- [ ] **Comparative statics**: **CANNOT FULLY VERIFY** until the two code bugs (negative root, equity value) are fixed. The qualitative directions (higher $\lambda$ lowers trigger, higher $\sigma$ raises trigger, etc.) are consistent with economic intuition and standard real options theory. The quantitative magnitudes for leveraged cases should be re-verified after bug fixes.

- [ ] **Revealed beliefs results**: The paper does not present explicit $\hat{\lambda}$ estimates per archetype in the main text — it states that "observed investment patterns are consistent with genuinely high-$\tilde{\lambda}$ beliefs." The slides claim "frontier labs invest as if transformative AI is 2-5 years away." Since the inversion results are not presented in detail, this specific claim is not verifiable from the text. **Recommendation:** Either present a table of $\hat{\lambda}$ by archetype or soften the "2-5 years" claim.

- [x] **Growth decomposition**: The decomposition in `models/valuation.py` correctly separates installed capacity value from growth option value. The computation follows the standard real options structure: $V = V_{\text{installed}} + V_{\text{option}}$. The figure (`fig_growth_decomposition`) shows the expected pattern of growth option declining as $X$ approaches the trigger. **PASSES** for the decomposition logic itself, though the $X_D$ component is affected by the bugs.

---

### 6. Slides Review

- [ ] **Completeness**: The slides cover motivation, model, results, calibration, revealed beliefs, and conclusion. Approximately 25 slides, appropriate for a seminar. **PASSES** for coverage.

- [ ] **Consistency with paper**: **MAJOR ISSUES.**
  - **Slide "Training-Inference Allocation"** (`slides/long-form/_results.qmd:23-41`): Presents the revenue function as $\pi(X, K, \phi) = X \cdot A(\phi K)^\eta \cdot ((1-\phi)K)^\alpha$ with $\phi^* = \eta/(\alpha + \eta) \approx 15\%$. This is a **completely different model specification** from the paper, which uses regime-specific revenue (Equations 3-4). The paper's $\phi^* \approx 0.701$ at baseline, not 15%. This slide must be rewritten.
  - **Slide "Duopoly: Default Risk"** (`slides/long-form/_model.qmd:85-89`): Presents a default boundary formula that does not match Equation 18 in the paper — it omits the $\beta_s^- / (\beta_s^- - 1)$ option-value factor.
  - **Slide "Baseline Results"** (`slides/long-form/_calibration.qmd:42-47`): Reports different numerical values from the paper ($X^* \approx 0.016$ in slides vs. $X^* \approx 0.49$ in paper vs. $X^* = 0.027$ in code). All three disagree.
  - **Slide "This Paper"** (`slides/long-form/_introduction.qmd:35-48`): Frames three different contributions than the paper's actual three.
  - The slides use bare $\lambda$ throughout while the paper distinguishes $\lambda_0$, $\tilde{\lambda}$, $\lambda_{\text{true}}$.

- [ ] **Clarity**: The slides are readable and well-formatted as standalone slides. However, presenting them alongside the current paper would create confusion due to the inconsistencies above. **The slides require a complete refresh.**

---

## Summary of Issues

### Critical Issues

1. **`_negative_root` uses wrong discount rate** (`duopoly.py:359`). The negative characteristic root uses $-r$ instead of $-(r + \tilde{\lambda})$, causing an 11% error in the default boundary. All leveraged results (Proposition 2 magnitudes, Proposition 3 parts iv-v, credit spreads, AI investment dilemma with leverage) are numerically incorrect. **Fix:** Change `c = -p.r` to `c = -(p.r + lam_tilde)`.

2. **Equity value default option bracket is wrong** (`duopoly.py:411-415`). Double-counts the operating cost term and omits the equity contribution $(1-\ell)I(K)$. The smooth-pasting condition $E(X_D) = 0$ is not analytically satisfied. **Fix:** Rewrite the default_claim computation to match the paper's Equation for $E(X)$.

3. **Paper baseline results are stale** (`_calibration.qmd:131-132`). States $X^* \approx 0.49$, $K^* \approx 0.55$, $\phi^* \approx 0.30$ but code produces $X^* = 0.027$, $K^* = 0.055$, $\phi^* = 0.701$. All baseline result text must be updated.

### Major Issues

4. **Slides are substantially out of date.** Model specification, numerical results, proposition numbering, and notation differ from the paper. The slides require a complete refresh.

5. **Overflow warnings in duopoly comparative statics** (`duopoly.py:285, 511, 740, 778`). Silent `inf`/`nan` propagation during sigma sensitivity analysis. Add overflow guards.

6. **$\lambda_0 = 0.05$ vs. $\tilde{\lambda} = 0.10$ under $\xi = 0$.** The parameter table and the baseline text description are inconsistent. Clarify.

7. **Text-figure consistency should be verified** for `fig_competition_effect` (ratios) and `fig_credit_risk` (magnitudes) after code bugs are fixed.

8. **Notation inconsistencies** ($\lambda$ vs. $\tilde{\lambda}$, $c_D$ vs. $c_d$ vs. $d$, $\beta_s^-$ vs. $\beta_L^-$) need a consistency pass.

9. **Missing literature**: Dixit (1989), Pastor and Veronesi (2009), Trigeorgis (1996), Grenadier and Malenko (2011), Lambrecht and Perraudin (2003).

### Minor Issues

10. **Vacuous tests** (`test_valuation.py:121-142`, `test_calibration.py:72-78`): Tests that pass even when computations fail. Strengthen assertions.

11. **Missing edge case tests**: $\lambda = 0$, $\sigma \to 0$, $N = 1$ firm, high $\lambda$ values.

12. **Parameter validation untested**: `parameters.py` coverage at 76% — validation branches for invalid inputs are not tested.

13. **fig_comparative_statics panel (d)** axis label says "Depreciation" — should be "Operating cost rate."

14. **Sensitivity analysis** could be expanded: two-way plots for $(r, \alpha)$, confidence regions for revealed beliefs, elasticity of $\underline{\phi}$.

15. **$\alpha = 0.40$ motivation**: The "GPU utilization" argument is not convincing. The mapping from utilization to revenue elasticity should be explained more carefully.

16. **Code: extract multi-start optimization helper** to reduce duplication across 4 near-identical loops.

17. **Code: regime string validation** — no check that `regime in ("L", "H")`, so typos silently select the wrong branch.

18. **Abstract**: "semi-analytical characterization" should be "analytical existence and numerical characterization" for the duopoly result.

19. **Cahn (2024) "$600B gap" figure** in conclusion may be outdated.

---

## Overall Recommendation

**Major revision needed.**

The paper addresses a first-order economic question with a well-constructed and novel theoretical framework. The training-inference allocation is a genuine innovation in the real options literature, and the "faith-based survival" mechanism is both new and economically compelling. The writing quality is excellent. However, two code bugs in the default boundary computation (wrong characteristic root, wrong equity value bracket) affect all leveraged results, the paper's stated baseline numbers are stale, and the slides are substantially out of date with the current paper.

The recommended path forward:
1. Fix the two code bugs and regenerate all leveraged results and figures.
2. Update all stale baseline numbers in the paper text.
3. Verify text-figure consistency throughout.
4. Perform a notation consistency pass.
5. Refresh the slides to match the current paper.
6. Address the literature gaps and expand sensitivity analysis.

**Recommended target journal: RFS**, for the reasons stated in Section 3c above. After addressing the critical and major issues, the paper's combination of timely application, novel mechanisms, and transparent analytical treatment would make it competitive.
