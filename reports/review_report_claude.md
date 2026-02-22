# Review Report: AI Lab Investment

**Reviewer:** Claude (Opus 4.6)
**Date:** 2026-02-22

## Executive Summary

This report reviews the research project "Investing in Intelligence: A Real Options Framework for AI Compute Infrastructure" by Vincent Gregoire (HEC Montreal), covering both the codebase and the accompanying paper/slides. The project develops a real options model of irreversible AI compute investment under regime-switching demand, strategic competition, default risk, and diminishing returns, with a "revealed beliefs" methodology for backing out firms' private probability assessments of transformative AI arrival.

**Code assessment:** The codebase is well-organized with clean separation of concerns, 145 passing tests, and reasonable coverage of core model modules (80-93%). However, I identified several significant issues: (1) a potential revenue double-counting bug in the duopoly and N-firm market share computations, (2) the default boundary formula in the code (Leland 1994 optimal boundary) does not match the paper's stated formula (naive zero-equity condition), (3) nearly all stylized firm data values differ between the paper's table and the code, (4) a `mu_L` parameter discrepancy between `CalibrationData` and `ModelParameters`, and (5) no convergence checks in the N-firm backward induction.

**Paper assessment:** The paper addresses a timely and important question with a creative theoretical framework. The progression from single-firm to duopoly to N-firm is well-motivated. However, the paper is not yet ready for submission to a top journal. Critical gaps include: (1) the revealed beliefs methodology -- the paper's most novel contribution -- lacks actual numerical results (no table of implied lambda values), (2) four of six propositions have no formal proofs, (3) there is a mathematical error in the particular solution for $F_L(X)$, (4) the literature review omits several important references (Weeds 2002, Hackbarth & Mauer 2012, Sundaresan et al. 2015), and (5) the N-firm extension describes an algorithm but presents no numerical results for N>2.

**Overall recommendation:** Major revision needed before submission. The most appropriate target journal is **Review of Financial Studies (RFS)**, conditional on completing the revealed beliefs analysis and addressing the issues identified below.

---

## Part 1: Code Validation

### 1. Mathematical Correctness

#### 1a. Propositions vs. Code

**Proposition 1 (Optimal capacity in regime H)** -- PASSES with caveats

- Paper location: `paper/_model.qmd`, lines 67-74
- Code location: `src/ai_lab_investment/models/base_model.py`, lines 83-133

The paper's trigger formula $X_H^* = \frac{\beta_H}{\beta_H - 1} \cdot \frac{(r - \mu_H)(cK^\gamma + \delta K/r)}{K^\alpha}$ matches the code's computation: `markup * b / a` where `markup = beta/(beta-1)`, `b = delta*K/r + c*K^gamma`, `a = A_H * K^alpha`, and `A_H = 1/(r - mu_H)`. The existence condition $1/\gamma < (1 - 1/\beta_H)/\alpha < 1$ is correctly implemented at `base_model.py` lines 52-68. The code uses numerical optimization over log(K) rather than solving the implicit first-order condition analytically, which is a valid alternative approach.

**Proposition 2 (Endogenous default boundary)** -- HAS ISSUES

- Paper: `paper/_model.qmd`, lines 130-141
- Code: `src/ai_lab_investment/models/duopoly.py`, lines 126-161

**Issue 1 (Major):** The paper derives the default boundary from a zero-equity condition, yielding $X_D = \frac{(\delta K + d)(r - \mu_s)}{r} \cdot \frac{K_i^\alpha + K_j^\alpha}{K_i^\alpha}$. The code instead implements the Leland (1994) smooth-pasting optimal default boundary: $X_D = \frac{\beta^-}{\beta^- - 1} \cdot \frac{c_D / r}{\text{revenue\_coeff}}$ (`duopoly.py` line 159). These are fundamentally different formulas -- the Leland boundary includes the factor $\beta^- / (\beta^- - 1)$ and uses only the coupon $c_D$ rather than $(\delta K + d)$.

**Issue 2 (Major):** The `revenue_coeff` at `duopoly.py` line 150 is computed as `A * K_i^alpha * share`, where `share = K_i^alpha / (K_i^alpha + K_j^alpha)`. This yields `A * (K_i^alpha)^2 / (K_i^alpha + K_j^alpha)`. The correct coefficient from the paper should be `A * K_i^alpha / (K_i^alpha + K_j^alpha)` = `A * share`, without the extra `K_i^alpha` factor. This appears to be a revenue double-counting bug that propagates through all duopoly and N-firm computations.

**Suggestion:** Verify the intended formula by checking dimensionality. The revenue PV should be $A \cdot X \cdot \frac{K_i^\alpha}{K_i^\alpha + K_j^\alpha}$. The code computes $A \cdot X \cdot K_i^\alpha \cdot \frac{K_i^\alpha}{K_i^\alpha + K_j^\alpha}$, which has an extra $K_i^\alpha$ factor.

**Proposition 3 (Preemption equilibrium with default risk)** -- HAS ISSUES

- Paper: `paper/_model.qmd`, lines 192-202
- Code: `src/ai_lab_investment/models/duopoly.py`, lines 529-597

The general preemption approach (find $X_P$ where $L(X_P) = F(X_P)$ via Brent's method) is correct. However, the leader's monopoly revenue model in the code (`duopoly.py` line 392, `monopolist_revenue_pv`) computes revenue proportional to $K_L^\alpha$, while the paper (line 179) states the leader earns revenue proportional to $X$ only (monopoly share = 1). Additionally, the revenue double-counting bug from Proposition 2 propagates through the `duopoly_revenue_pv` function used in the leader's value calculation.

**Proposition 4 (N-firm equilibrium properties)** -- HAS ISSUES

- Paper: `paper/_extensions.qmd`, lines 24-36
- Code: `src/ai_lab_investment/models/nfirm.py`, lines 195-266

**Issue 1:** Same revenue double-counting pattern: `nfirm.py` line 100 computes `A * X * exp(q) * K_I^alpha * share`, where `share` already contains `K_I^alpha` in its numerator.

**Issue 2:** The algorithm structure differs from the paper's description. The paper describes backward induction from firm N to firm 1. The code instead solves all firms independently with dummy competitors, then iterates forward (k=0 to N-1) in refinement passes -- a fixed-point iteration rather than true backward induction. While it may converge to the same solution, the approach is not what the paper describes.

**Proposition 5 (Optimal training fraction)** -- PASSES with caveat

- Paper: `paper/_extensions.qmd`, lines 62-69; Proof: `paper/_appendix.qmd`, lines 46-63
- Code: `src/ai_lab_investment/models/nfirm.py`, lines 272-330

The closed-form result $\phi^* = \eta / (\alpha + \eta)$ is analytically correct and the proof is complete. However, the code does NOT use this closed-form solution -- it uses numerical optimization with a more complex objective that includes discrete discounting and competitor effects (lines 296-323), making it more general but not directly comparable to Proposition 5.

**Proposition 6 (Asymmetric Dario dilemma)** -- COULD NOT BE VERIFIED analytically

- Paper: `paper/_valuation.qmd`, lines 132-133
- Code: `src/ai_lab_investment/models/valuation.py`, lines 228-290

Stated without proof. The code implements the value loss calculation correctly as $\Delta V = \text{NPV}(\lambda_{\text{true}}, \lambda_{\text{true}}) - \text{NPV}(\lambda_{\text{true}}, \lambda_{\text{invest}})$. The asymmetry claim would need numerical verification across parameter ranges.

#### 1b. Proofs

**Proof of Proposition 1** (`paper/_appendix.qmd`, lines 5-44) -- HAS ISSUES

- The smooth-pasting derivation (lines 9-13) is stated without intermediate steps.
- Lines 36-43 switch from a formal derivation to a heuristic asymptotic argument ("For delta small, the dominant balance is...") without completing the proof for general $\delta$.
- The expression for $K_H^*$ contains $K$ on both sides of the equation (the $K^{1-\gamma}$ term), making it an implicit rather than explicit formula, which contradicts the presentation as a closed-form solution.
- **Verdict:** Logically incomplete.

**Proof of Proposition 5** (`paper/_appendix.qmd`, lines 46-63) -- PASSES

Complete and correct: FOC, division by common factor, algebraic solution, and SOC verification are all valid.

**Proofs of Propositions 2, 3, 4, 6** -- COULD NOT BE VERIFIED

These propositions have no formal proofs in the appendix. Proposition 2 has only intuitive justification. Proposition 3 defers to Huisman & Kort (2015). Proposition 4 is described as computationally verified. Proposition 6 is stated as an empirical observation.

#### 1c. Numerical Methods

**Root-finding in `revealed_beliefs.py`** -- PASSES

Uses `scipy.optimize.brentq` with `xtol=1e-6` and bounds `[0.001, 2.0]`. Sign checks before calling Brent's method (lines 82-88, 141-148). Handles infinity/NaN gracefully.

**Backward induction in `nfirm.py`** -- HAS ISSUES

- **No convergence check:** The paper claims convergence is verified at tolerance $10^{-4}$. The code hardcodes 5 iterations (`nfirm.py` line 223) with no convergence verification.
- **Optimization bounds mismatch:** Paper says `[0.01, 10]` for K; code uses `[-15, 15]` in log-space ($\approx [3 \times 10^{-7}, 3.3 \times 10^6]$).
- **Initial dummy competitors:** First pass uses `[1.0] * n_competitors` (line 218), an arbitrary initialization not described in the paper.

**Preemption root-finding in `duopoly.py`** -- PASSES

Uses `brentq` with `xtol=1e-10`. Properly checks sign change and handles edge cases with fallback to monopolist trigger.

**Scalar optimization throughout** -- PASSES with note

Uses `scipy.optimize.minimize_scalar` with `method="bounded"` (Brent's for bounded scalar minimization). Optimization over log(K) prevents negative K. However, `result.success` is never checked after any optimization call -- failed convergence would be silently used.

#### 1d. Parameter Consistency

**Finding: HAS ISSUES**

| Parameter | Paper (`_calibration.qmd`) | `ModelParameters` | `CalibrationData` |
|-----------|---------------------------|-------------------|-------------------|
| `mu_L` | 0.01 (line 11) | 0.01 (line 35) | **0.02** (line 54) |
| r | 0.12 | 0.12 | 0.12 |
| mu_H | 0.06 | 0.06 | 0.06 |
| sigma_L | 0.25 | 0.25 | 0.25 |
| sigma_H | 0.30 | 0.30 | 0.30 |
| alpha | 0.40 | 0.40 | 0.40 |
| gamma | 1.50 | 1.50 | 1.50 |
| c | 1.0 | 1.0 | 1.0 |
| delta | 0.03 | 0.03 | 0.03 |
| lambda | 0.10 | 0.10 | 0.10 |

The `mu_L` discrepancy means revealed beliefs analyses using `CalibrationData` defaults operate on a different drift than the paper states.

**Firm data discrepancies** -- Nearly every firm-specific data point differs between the paper's table (`_calibration.qmd` lines 48-57) and `data.py` (lines 106-163):

| Firm | Parameter | Paper | Code |
|------|-----------|-------|------|
| Anthropic-like | Revenue 2025 | $3.0B | $9.0B |
| Anthropic-like | CapEx/Revenue | 2.00 | 0.56 |
| Anthropic-like | Leverage | 0.20 | 0.15 |
| OpenAI-like | Revenue 2024 | $4.0B | $3.5B |
| OpenAI-like | CapEx 2025 | $15.0B | $8.0B |
| OpenAI-like | CapEx/Revenue | 1.25 | 0.67 |
| Google-like | Revenue 2024 | $40.0B | $10.0B |
| Google-like | CapEx/Revenue | 1.09 | 2.50 |
| CoreWeave-like | CapEx 2025 | $10.0B | $15.0B |

The paper claims all four firms have CapEx/Revenue > 1.0 (line 69), but the code data has Anthropic-like at 0.56 and OpenAI-like at 0.67.

#### 1e. Regime Switching

**Finding: PASSES with caveats**

**Transition intensities:** The paper specifies Poisson arrival rate $\lambda > 0$ for $L \to H$ switching, with $H$ absorbing. The code implements this correctly both analytically (`parameters.py` line 103: effective discount $r + \lambda$ for $\beta_L$) and in simulation (`base_model.py` line 348: switch probability $\lambda \cdot dt$ per step, only from regime $L$).

**Characteristic equation:** Paper's $\frac{\sigma_L^2}{2}\beta(\beta-1) + \mu_L \beta - (r + \lambda) = 0$ matches `_positive_root(sigma_L, mu_L, r + lam)` at `parameters.py` line 103.

**Installed value discrepancy:** The paper (Eq. @eq-installed-value) uses $V_L = \frac{X K^\alpha}{r - \mu_L} - \frac{\delta K}{r}$, ignoring regime switching in the installed value. The code correctly uses $A_L = \frac{r - \mu_H + \lambda}{(r - \mu_H)(r - \mu_L + \lambda)}$ which accounts for future switching from $L$ to $H$. The code is more correct than the paper formula.

**Typographical error in paper:** `_model.qmd` line 94 presents $F_L(X) = A_L X^{\beta_L} + \frac{\lambda}{r + \lambda - r} F_H(X)$. The coefficient $\frac{\lambda}{r + \lambda - r} = \frac{\lambda}{\lambda} = 1$ is clearly erroneous. The correct particular solution coefficient is computed in the code via `_particular_solution_coeff()` (`base_model.py` lines 135-152).

---

### 2. Code Quality and Testing

#### 2a. Test Coverage

**Finding: HAS ISSUES**

Overall line coverage: **47%** (969/1852 statements missed). Core model coverage is reasonable:

| Module | Coverage |
|--------|----------|
| `calibration/data.py` | 100% |
| `models/base_model.py` | 93% |
| `models/nfirm.py` | 91% |
| `models/valuation.py` | 89% |
| `calibration/revealed_beliefs.py` | 86% |
| `models/duopoly.py` | 85% |
| `models/parameters.py` | 80% |

Completely untested (0% coverage): all 5 figure modules (718 statements), `pipeline.py` (103 statements), `utils/` (48 statements), `__main__.py`, `exceptions.py`.

Specific gaps: 6 of 9 parameter validation branches untested; the `lam == 0` branch in `_compute_derived` never exercised; `value_function_numerical` in `base_model.py` untested; `solve_no_competition` verification in `duopoly.py` untested.

#### 2b. Test Meaningfulness

**Finding: PASSES with caveats**

**Strong tests (economically meaningful):**

- `test_base_model.py::TestRegimeH::test_smooth_pasting` (line 63) -- verifies the smooth-pasting optimality condition $dF/dX = dV/dX$ at $X^*$
- `test_base_model.py::TestRegimeH::test_value_matching` (line 73) -- verifies $F(X^*) = V(X^*, K^*) - I(K^*)$
- `test_base_model.py::TestRegimeH::test_option_exceeds_npv_before_trigger` (line 90) -- option value exceeds immediate exercise NPV below trigger
- `test_base_model.py::TestComparativeStatics::test_higher_sigma_higher_trigger_H` (line 136) -- canonical real options comparative static
- `test_duopoly.py::TestLeader::test_leader_trigger_below_follower` (line 131) -- defining feature of preemption equilibrium
- `test_duopoly.py::TestPreemptionEquilibrium::test_preemption_lowers_trigger` (line 174) -- competition forces earlier investment
- `test_duopoly.py::TestDefaultRisk::test_default_boundary_below_trigger` (line 196) -- essential economic consistency
- `test_duopoly.py::TestDefaultRisk::test_firm_value_equals_equity_plus_debt` (line 230) -- Modigliani-Miller identity
- `test_valuation.py::TestDarioDilemma::test_matched_beliefs_no_loss` (line 121) -- zero loss when beliefs match

**Weak/tautological tests:**

- `test_duopoly.py::TestDuopolyRevenue::test_symmetric_duopoly_revenue` (line 71) -- calls the same function twice with identical arguments and checks equality; should swap $K_i$ and $K_j$ to test symmetry
- `test_duopoly.py::TestFollower::test_follower_capacity_responds_to_leader` (line 97) -- only checks `K > 0`, does not verify directional response
- `test_calibration.py::TestRevealedBeliefs::test_higher_lambda_lower_trigger` (line 72) -- assertions are just `X > 0`, not directional
- `test_calibration.py::TestRevealedBeliefs::test_infer_lambda_from_trigger` (line 81) -- assertion `recovered is None or recovered >= 0` is vacuous
- `test_nfirm.py::TestSequentialEquilibrium::test_shares_sum_to_one` (line 116) -- uses 10% tolerance for a structural identity
- `test_base_model.py::TestRegimeL::test_with_high_alpha_has_L_trigger` (line 124) -- wrapped in conditional that silently passes without testing

#### 2c. Edge Cases

**Finding: HAS ISSUES**

Missing boundary condition tests:

1. **lambda = 0:** The `lam == 0` branch in `parameters.py` line 105 and `base_model.py` line 141 are never tested (test uses `lam=1e-10`)
2. **Very large lambda:** No test for `lam >= 10.0`; could cause numerical issues in $X^{\beta_L}$
3. **N=1 in N-firm model:** Never tested; `NFirmModel(params, n_firms=1)` with empty competitor set
4. **Very small sigma:** `sigma = 0.001` makes $\beta$ very large, potentially causing overflow in $X^\beta$
5. **Leverage = 1.0:** All-debt financing makes `equity_cost = 0` in `duopoly.py` line 314
6. **X = 0:** Well-defined mathematically but never tested
7. **K_j = 0 in duopoly:** Test uses `1e-10` rather than exact 0
8. **Near-boundary alpha/gamma:** No tests for alpha close to 0 or 1, gamma close to 1

#### 2d. Numerical Stability

**Finding: HAS ISSUES**

1. **No optimization success checks:** After every `minimize_scalar` call (`base_model.py` line 120, `duopoly.py` line 359, `nfirm.py` line 181), `result.x` is extracted without checking `result.success`. Failed convergence is silently used.

2. **Fixed iteration without convergence check:** `nfirm.py` line 223 hardcodes 5 iterations with no convergence verification or diagnostic output.

3. **Silent fallbacks:** `solve_preemption_equilibrium` (`duopoly.py` line 581) silently falls back to the monopolist trigger when Brent's method fails, with no logging.

4. **Particular solution guard too tight:** `base_model.py` line 150 uses `abs(Q_L) < 1e-15` as zero guard. Threshold of `1e-10` would be safer for floating-point arithmetic.

5. **No overflow protection for extreme parameters:** Very small sigma makes beta very large; $X^\beta$ can overflow. No guard present.

#### 2e. Code Organization

**Finding: PASSES**

The code is well-organized:

- Clear module hierarchy mirroring the paper structure (Phase 1-5)
- Centralized parameter management via `ModelParameters` dataclass with validation and `with_param()` for immutable variation
- Effective caching in model classes to avoid recomputation
- Clean Hydra/pipeline configuration

Minor issues: duplicated `plt.rcParams` blocks across all 5 figure modules; magic number `(-15, 15)` optimization bounds appears in 6 places; asymmetric `contest_share` signatures between duopoly and N-firm models.

#### 2f. Reproducibility

**Finding: HAS ISSUES**

- **Deterministic analytical results:** Core model solutions use `scipy.optimize` which is deterministic. This is good.
- **No global random seed in pipeline:** `pipeline.py` and `config.yaml` have no seed parameter. The `plot_sample_paths` function uses `seed=42` by default, but other stochastic components would not be reproducible.
- **Vestigial config parameters:** `config.yaml` has `n_bootstrap_samples: 100000` and `multiprocessing: 10` that are never referenced in any source code.
- **Pinned dependencies:** `uv.lock` exists (good for reproducibility).

---

## Part 2: Paper and Presentation Review

### 3. Paper Content Review

#### 3a. Structure and Argument

**Motivation** -- PASSES with minor issues

The introduction (`paper/_introduction.qmd`, lines 1-57) opens compellingly with the $200 billion figure and irreversibility of AI investments. The three contributions are cleanly enumerated. The "Dario dilemma" framing is memorable. However: (1) the $200B figure (line 4) has no citation, (2) the opening claim "the defining capital allocation event of the 2020s" (line 3) is strong and should be qualified, (3) the introduction should more explicitly state why existing models are inadequate.

**Literature positioning** -- HAS ISSUES

The paper cites the right foundational works (Dixit & Pindyck, McDonald & Siegel, Guo et al., Grenadier, Huisman & Kort, Leland) but the positioning reads as a citation list rather than a nuanced discussion. Significant omissions:

- Weeds (2002) -- "Strategic delay in a real options model of R&D competition" (RES) -- directly relevant to R&D investment races
- Hackbarth & Mauer (2012) -- "Optimal priority structure, capital structure, and investment" (RFS) -- combines real options with capital structure
- Sundaresan, Wang & Yang (2015) -- "Dynamic investment, capital structure, and debt overhang" (RFS) -- debt overhang / limited liability
- Brander & Lewis (1986) -- risk-shifting with leverage; mentioned in `plan.md` but never cited in the paper
- Lambrecht & Perraudin (2003) -- preemption under incomplete information
- Konrad (2009) -- contest function theory for investment contexts

Additionally, Acemoglu & Restrepo (2018) and Korinek (2024) appear in `references.bib` but are never cited in the paper text.

**Model building** -- PASSES

The progression from single-firm to duopoly to N-firm is logical and well-motivated. The convergence verification (N=2 matching analytical duopoly) is good practice. Minor concern: the training-fraction independence result ($\phi^* = \eta/(\alpha + \eta)$, independent of X and K) feels too strong and deserves more discussion of when it breaks down.

**Identification (Revealed beliefs)** -- HAS ISSUES

This is the paper's most novel contribution, but the identification argument needs significant strengthening:

1. The key assumption (line 40 of `_valuation.qmd`) -- that cross-firm variation in investment intensity reflects belief variation rather than unobserved heterogeneity -- is extremely strong and inadequately defended. Sensitivity analysis does not address unobservable differences in strategic objectives, governance, or GPU supply chains.

2. The inversion uses a single scalar moment (CapEx/Revenue). Different calibrations of unobserved parameters (alpha, gamma, sigma) would yield different implied lambdas for the same investment intensity. A formal sensitivity table is needed.

3. **There are no actual revealed belief estimates presented in the paper.** The abstract claims "frontier labs invest as if transformative AI is substantially closer than market consensus," but no table of implied lambda values appears. This is the paper's headline result and its absence is a critical gap.

**Conclusion** -- PASSES

Well-structured, summarizes findings without overclaiming. Appropriate future research directions.

#### 3b. Writing Quality

**Clarity** -- HAS ISSUES

The writing is generally clear and professional. However:

1. **Mathematical error:** `_model.qmd` line 94: $F_L(X) = A_L X^{\beta_L} + \frac{\lambda}{r + \lambda - r} F_H(X)$. The coefficient simplifies to $\lambda/\lambda = 1$, which is clearly a typographical error. The correct coefficient is computed in the code at `base_model.py` lines 135-152.

2. **Implicit formula presented as explicit:** `_model.qmd` lines 67-74: The expression for $K_H^*$ contains $K^{1-\gamma}$ on the RHS, making it an implicit equation. Should be clarified or presented as a fixed-point characterization.

3. **Dimensionality issue:** `_extensions.qmd` line 59: The training-inference revenue function $\pi(X, K, \phi) = X \cdot Q(\phi K) \cdot (1-\phi)^\alpha K^\alpha$ yields zero when $\phi = 0$ (no training), implying a firm that does no training earns zero revenue. This may be intentional but should be explicitly justified.

4. **Notation simplification:** `_model.qmd` line 179: "$X K_L^\alpha / K_L^\alpha = X$" is unnecessarily complex. Simply "monopoly revenue $X$" would be clearer.

**Notation** -- HAS ISSUES

1. Inconsistent use of $\beta$: $\beta_H$ (positive root), $\beta_s^-$ (negative root), $\beta_s$ (without superscript), $\beta$ (without subscript in appendix). Must be standardized.
2. Symbol $c$ is used for both unit investment cost ($I(K) = cK^\gamma$) and is close to coupon rate $c_d$. Consider renaming to $\kappa$.
3. $\delta$ is called "depreciation" but modeled as a perpetual operating cost ($\delta K / r$), not capital stock decline. Should be called "maintenance cost."
4. $d$ (continuous coupon) has no clear connection to $D_0$ (face value) and $D(X)$ (market value of debt). Relationships should be consolidated.

**Length and focus** -- HAS ISSUES

1. The discussion section (`_discussion.qmd`, ~70 lines) is underdeveloped. Either deepen the welfare analysis or cut it.
2. The N-firm section (`_extensions.qmd`) describes the algorithm in detail but presents no numerical results for N>2. No figures or tables show equilibrium outcomes.
3. **Missing headline results:** No table of implied lambda values for each firm.

**Abstract** -- PASSES with minor issues

Conveys the three contributions clearly at ~150 words. However, it claims results ("the model implies that frontier labs invest as if transformative AI is substantially closer than market consensus") not supported by numerical estimates in the paper body.

#### 3c. Journal Fit

**Contribution significance** -- HAS ISSUES

The research question is ambitious and timely. The theoretical combination of real options + regime switching + strategic competition + default risk is novel. However:

1. Each individual component has been studied before; the novelty is in combining them, but no sharp new economic insight emerges uniquely from the combination.
2. The empirical contribution (revealed beliefs) is not delivered -- without actual lambda estimates, the paper reads as a theoretical exercise with a promissory note.
3. For JF/RFS, stronger quantitative/empirical content is needed beyond "stylized" parameterizations.
4. For Econometrica, the identification argument needs formal identification theorems and conditions.

**Methodological rigor** -- HAS ISSUES

1. Proofs provided only for Propositions 1 and 5; Propositions 2, 3, 4, 6 lack formal proofs.
2. Proposition 1's proof is informal with a heuristic asymptotic argument.
3. Existence and uniqueness claims (Propositions 3, 4) are unproven.
4. No numerical convergence results or error bounds are presented.

**Formatting** -- HAS ISSUES

1. Uses Quarto/markdown; needs conversion to journal LaTeX template for submission.
2. "Preliminary draft -- Please do not circulate" subtitle should be removed.
3. Placeholder acknowledgments ("We thank ...") in `index.qmd` line 31.
4. 10 figures is on the high side for a finance journal.

**Best journal fit** -- **Review of Financial Studies (RFS)**

- JF demands a sharper, more focused contribution and increasingly requires empirical validation.
- Econometrica requires much more formal identification analysis and complete proofs.
- RFS publishes corporate finance theory with quantitative applications, is receptive to leverage/default investment models, and values creative methodologies like revealed beliefs.

---

### 4. Figures

#### 4a. Paper Figures

Review of figures generated by `paper/generate_figures.py`:

| # | Figure | Accuracy | Labels | Quality | Issues |
|---|--------|----------|--------|---------|--------|
| 1 | Sample Paths | PASS | PASS | Minor | Regime switch dots are small (markersize=3) |
| 2 | Option Value | PASS | PASS | PASS | None |
| 3 | Comparative Statics | PASS | ISSUES | ISSUES | Y-axis labels missing on some panels; trigger and capacity curves nearly indistinguishable |
| 4 | Lambda Option Value | PASS | PASS | PASS | None |
| 5 | Default Boundaries | ISSUES | PASS | PASS | Default boundary computed with K_j=0 instead of K_leader (`generate_figures.py` line 293) |
| 6 | Credit Risk | PASS | PASS | PASS | None |
| 7 | Competition Effect | PASS | PASS | Minor | Trigger ratio panel needs context |
| 8 | Firm Comparison | ISSUES | PASS | PASS | Uses CODE data, not paper table data -- bar chart contradicts paper's claims |
| 9 | Lambda Timeline | PASS | PASS | PASS | Pure math, trivially correct |
| 10 | Growth Decomposition | ISSUES | PASS | PASS | Expansion option uses full F_H(X) minus installed value, not incremental expansion value |

Publication quality settings (300 DPI, serif fonts, 6.5" width, Econometrica style) are appropriate.

#### 4b. Code-Figure Consistency

**Trace 1 (Figure 2, Option Value):** `ModelParameters()` -> `SingleFirmModel(p)` -> `optimal_trigger_and_capacity("H")` -> `option_value_H(x)` and `installed_value(x, K*, "H") - investment_cost(K*)`. Pipeline is correct.

**Trace 2 (Figure 5, Default Boundaries):** For each leverage, creates `DuopolyModel`, calls `solve_preemption_equilibrium("H")`, then `default_boundary(K_follower, 0, "H")`. Mechanically correct but K_j=0 is economically questionable.

**Trace 3 (Figure 8, Firm Comparison):** `get_baseline_calibration()` -> `get_stylized_firms()` in `data.py`. Pipeline is mechanically correct, but `data.py` values differ from paper table.

#### 4c. Slide Figures

Slide figures are generated by the same `generate_figures.py` script and use PNG copies of the paper figures. They are consistent with each other. However, the slide calibration table (`slides/long-form/_calibration.qmd` lines 14-28) matches the paper table, while Figure 8 shown on the next slide uses the code data -- creating an inconsistency within the slides themselves.

---

### 5. Calibration and Results

#### 5a. Parameter Values

| Parameter | Value | Assessment |
|-----------|-------|------------|
| r = 0.12 | Reasonable tech-sector WACC | PASS |
| mu_L = 0.01, mu_H = 0.06 | Reasonable but mu_L inconsistent across code | ISSUES |
| sigma_L = 0.25, sigma_H = 0.30 | Plausible AI demand volatility | PASS |
| lambda = 0.10 | 10-year expected switch; reasonable moderate prior | PASS |
| alpha = 0.40 | Well-justified via scaling laws; above existence threshold ~0.32 | PASS |
| gamma = 1.50 | Moderate cost convexity | PASS |
| delta = 0.03 | **ISSUES**: Paper claims GPUs depreciate ~20%/year, but uses delta=0.03 (3%) | ISSUES |

The delta calibration justification (`_calibration.qmd` line 42) is internally inconsistent. If physical depreciation is ~20%/year, delta should be much higher, or the paper should clearly explain what delta represents and why it differs from physical depreciation.

#### 5b. Sensitivity

The paper discusses sensitivity to sigma_H, r, lambda, and alpha qualitatively (`_calibration.qmd` lines 89-109). However:
- No quantitative sensitivity tables or ranges are reported
- The `sensitivity_analysis()` method in `revealed_beliefs.py` exists but is never used in the paper
- No confidence intervals or robustness bounds on implied lambda

#### 5c. Comparative Statics

Comparative statics are generally consistent with economic intuition:
- Higher sigma_H raises the trigger (standard real options) -- PASS
- Higher gamma reduces capacity (more convex costs) -- PASS
- Higher delta raises the trigger (higher maintenance hurdle) -- PASS
- Higher lambda encourages earlier investment (opposing channels correctly discussed) -- PASS

#### 5d. Revealed Beliefs Results

**COULD NOT BE FULLY VERIFIED** due to the firm data inconsistency. The methodology is sound (Brent's method inversion in `revealed_beliefs.py`), but:

1. The code would compute implied lambdas from CODE data, not paper table data
2. No numerical lambda estimates are presented in the paper
3. The predicted intensity formula in code (line 135: `I(K)/V`) may differ from the paper's stated CapEx/Revenue ratio

#### 5e. Growth Decomposition

**HAS ISSUES.** The decomposition uses `option_value_H(X)` (value for a firm with ZERO installed capacity) minus `installed_value(X, K, "H")` as the "expansion option." This is not the standard decomposition, which would compute the marginal value of expanding from current K to optimal K. The current approach overstates the expansion option for firms with positive installed capacity.

The paper's claim that growth options account for 60-80% of firm value is qualitatively reasonable for early-stage AI firms.

---

### 6. Slides Review

#### 6a. Completeness

**Finding: PASSES with one gap**

The slides cover: motivation, model environment, single-firm benchmark, duopoly with default, N-firm equilibrium, training-inference allocation, growth decomposition, calibration, baseline results, revealed beliefs methodology, lambda interpretation, credit risk, Dario dilemma, policy implications, and future work.

**Missing:** No slide showing actual implied lambda values for each firm. The methodology is presented but the quantitative punchline is absent.

#### 6b. Clarity

**Finding: PASSES with minor issues**

Slides use a good mix of equations, figures, and bullets. Fragment reveals are well-placed for presentation flow. Column layouts are effective.

Minor issues: No bibliography content despite referencing multiple citations. The N-firm slide is purely verbal with no supporting figure or table.

#### 6c. Consistency with Paper

**Finding: HAS ISSUES**

- Baseline results (X* ~ 0.49, K* ~ 0.55) match the paper -- PASS
- The slide calibration table matches the paper table, but Figure 8 on the next slide uses CODE data -- INCONSISTENT
- Default boundary formula in slides matches paper (naive zero-equity), not code (Leland) -- consistent with paper but not code
- Credit risk claim "~40% default probability at leverage 0.70" slightly overstates the figure (~37%)

---

## Summary of Issues

### Critical Issues

1. **Firm data inconsistency between paper and code** (`paper/_calibration.qmd` lines 48-57 vs. `src/ai_lab_investment/calibration/data.py` lines 106-163). Every firm parameter differs. The paper claims all firms have CapEx/Revenue > 1.0, but the code data has Anthropic-like at 0.56 and OpenAI-like at 0.67. Figure 8 contradicts the paper's own table. **Fix:** Synchronize one source to the other.

2. **Revenue double-counting bug in duopoly and N-firm models** (`duopoly.py` line 95-96, `nfirm.py` line 100). The `contest_share` already contains $K_i^\alpha$ in the numerator, but the revenue computation multiplies by $K_i^\alpha$ again. This affects all downstream duopoly and N-firm results. **Fix:** Remove the extra $K_i^\alpha$ factor, or restructure `contest_share` to return the raw share fraction.

3. **Default boundary formula mismatch** (`paper/_model.qmd` Eq. @eq-XD vs. `duopoly.py` line 159). Paper uses naive zero-equity condition; code implements Leland (1994) optimal boundary. **Fix:** Update the paper to document the Leland formula that is actually implemented.

4. **No revealed beliefs results presented.** The paper's most novel contribution has no numerical results. **Fix:** Add a table of implied lambda values for each stylized firm and discuss the estimates.

5. **Mathematical error in particular solution coefficient** (`paper/_model.qmd` line 94). The fraction $\lambda / (r + \lambda - r) = 1$ is clearly wrong. **Fix:** Replace with the correct coefficient from the code's `_particular_solution_coeff()`.

### Major Issues

6. **mu_L discrepancy:** `CalibrationData.mu_L = 0.02` vs. paper/`ModelParameters` = 0.01 (`data.py` line 54). **Fix:** Align to 0.01.

7. **Four of six proposition proofs missing.** Propositions 2, 3, 4, 6 have no formal proofs. Proposition 1's proof is logically incomplete. **Fix:** Add proofs to the appendix.

8. **N-firm backward induction has no convergence check.** Code hardcodes 5 iterations (`nfirm.py` line 223) with no verification. **Fix:** Add convergence criterion with tolerance $10^{-4}$ as the paper claims.

9. **No optimization success checks anywhere.** After every `minimize_scalar` call, `result.success` is unchecked. **Fix:** Add success checks with appropriate error handling.

10. **Literature omissions.** Missing Weeds (2002), Hackbarth & Mauer (2012), Sundaresan et al. (2015), Brander & Lewis (1986). **Fix:** Add citations and discussion.

11. **Depreciation calibration inconsistency.** Paper claims ~20%/year GPU depreciation but uses delta = 0.03. **Fix:** Explain the discrepancy or recalibrate.

12. **N-firm extension presents no numerical results for N>2.** **Fix:** Add figures/tables showing equilibrium outcomes for N=3, 4, 5.

13. **Identification argument for revealed beliefs is underdeveloped.** **Fix:** Add formal discussion of what is identified, sensitivity table varying each calibration parameter, and explicit caveats about unobserved heterogeneity.

14. **Figure 5 default boundary computed with K_j=0** (`generate_figures.py` line 293). Should use K_j = K_leader in the duopoly setting. **Fix:** Pass the leader's capacity.

### Minor Issues

15. **Notation inconsistencies:** Standardize $\beta$ subscripts/superscripts throughout; consolidate debt notation ($d$, $D_0$, $D(X)$, $c_d$); rename investment cost parameter $c$ to avoid confusion with coupon.

16. **Tautological tests:** Fix `test_symmetric_duopoly_revenue` to swap K_i/K_j; strengthen assertions in `test_follower_capacity_responds_to_leader` and `test_higher_lambda_lower_trigger`; tighten `test_shares_sum_to_one` tolerance from 10% to <1%.

17. **Missing edge case tests:** Add tests for lambda=0, very large lambda, N=1, near-boundary parameters.

18. **Duplicated `plt.rcParams`** across all figure modules. Factor into shared style config.

19. **Vestigial config parameters** (`n_bootstrap_samples`, `multiprocessing`) in `config.yaml` are never used.

20. **Growth decomposition methodology** uses total option value rather than incremental expansion value. Consider revising or documenting the non-standard definition.

21. **Slide credit risk claim** "~40% default probability" should be "~37%" to match the figure.

22. **Placeholder acknowledgments and "preliminary draft" subtitle** should be removed before submission.

23. **Implicit $K$ in Proposition 1** formula. Clarify that the expression is a fixed-point characterization, not a closed-form solution.

24. **Abstract claims** results not numerically presented in the paper body.

---

## Overall Recommendation

**Major revision needed.**

The paper addresses an important and timely question with a creative theoretical framework. The codebase is well-organized and the core economic tests are thoughtful. However, several critical issues must be resolved before the paper is suitable for journal submission:

1. The firm data inconsistency between paper and code undermines the credibility of all quantitative results.
2. The revealed beliefs analysis -- the paper's headline contribution -- lacks actual numerical results.
3. The potential revenue double-counting bug in the duopoly/N-firm models needs to be verified and, if confirmed, all results must be recomputed.
4. The mathematical error in the particular solution and the default boundary formula mismatch between paper and code must be corrected.
5. Missing proofs for four propositions fall below the standards of the target journals.

**Recommended target journal:** Review of Financial Studies (RFS), conditional on completing the revealed beliefs analysis, fixing the identified code issues, and providing all missing proofs. If the empirical analysis is substantially strengthened (actual data-driven calibration, out-of-sample tests), JF becomes feasible. If the theory is deepened (formal identification, complete proofs, existence/uniqueness theorems), Econometrica becomes feasible.
