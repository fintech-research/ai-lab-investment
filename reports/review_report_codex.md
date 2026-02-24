# Review Report: AI Lab Investment

**Reviewer:** codex
**Date:** 2026-02-24

## Executive Summary
This repository implements a multi‑phase real‑options framework for AI compute investment with regime switching, competition, and default risk, alongside a Quarto paper and slides. Based on static code review and targeted reading of the paper sections, the core mathematical structure in the models is consistent with the stated theory: characteristic roots, value matching, and smooth pasting are implemented correctly in the single‑firm model; contest‑share logic and default boundary with a negative characteristic root are implemented in the duopoly; and the valuation layer composes these pieces coherently.

I could not run the test suite or compute coverage due to sandbox/network restrictions preventing dependency resolution via `uv` (details below). However, the repository contains an extensive test suite across the base model, duopoly, N‑firm, valuation, calibration, and symbolic checks, with tests that verify smooth‑pasting/value‑matching, option structure in L, comparative statics, follower/leader problems, default risk, and valuation. Figure generation code clearly connects to model outputs and applies publication‑quality styles.

Paper quality is strong overall and matches the implemented code. I recommend clarifying the mapping from compute scaling exponents to the arrival‑rate elasticity parameter `eta`, adding more precise sourcing for training allocations and CapEx intensities, and tightening terminology around “phi” since the code uses “phi” both for training share and (legacy) the option‑premium ratio in one location. Overall recommendation: Revise and resubmit, target Journal of Finance, contingent on the documentation clarifications and a coverage report.

## Part 1: Code Validation
### 1. Mathematical Correctness
- Characteristic roots: Implemented in `src/ai_lab_investment/models/parameters.py:244` as `_positive_root`, matching the Euler ODE characteristic equation `0.5 sigma^2 beta(beta−1) + mu beta − discount = 0`. Tests cover correct behavior and positivity under valid parameter ranges (tests/test_parameters.py:8, tests/test_parameters.py:25).
- H‑regime option and trigger: Single‑firm regime‑H solution computes `(X_H*, K_H*, B_H)` via interior K optimization and closed‑form smooth‑pasting/value‑matching (see SingleFirmModel._solve_regime_H in `src/ai_lab_investment/models/base_model.py`). Tests verify smooth‑pasting and value‑matching identities at the optimum (tests/test_base_model.py:64–88, 90–98).
- L‑regime option structure: Particular solution coefficient C is implemented per the paper’s Eq. for `C = -lambda * B_H / Q_L(beta_H)` in `src/ai_lab_investment/models/base_model.py` and used in `option_value_L`. Tests check positivity of C and the “no interior trigger” formula `F_L(X) = C X^{beta_H}` (tests/test_base_model.py:116–132) and monotonicity (tests/test_base_model.py:133–136).
- Existence of interior triggers: The condition `1/gamma < Phi < 1` with `Phi = (1 − 1/beta)/alpha` is implemented and used to gate solutions (has_interior_trigger in `base_model.py`); tests cover both existence in H and absence in baseline L (tests/test_base_model.py:43–56, 98–105). Edge case with higher `alpha` restoring L‑trigger is tested (tests/test_base_model.py:136–155).
- Training–inference allocation (phi): The phi‑aware single‑firm objective maximizes `A_eff^beta_H / cost^(beta_H−1)` over `(K, phi)` with constraints and multiple starts, consistent with the text’s joint optimization (see `_effective_revenue_coeff_single`, `_objective_K_phi`, and `optimal_trigger_capacity_phi` in `src/ai_lab_investment/models/base_model.py`; tests/test_base_model.py:206–310).
- Duopoly contest functions: Regime‑specific shares implemented as functions of inference capacity in L and training compute in H (contest_share_L/H in `src/ai_lab_investment/models/duopoly.py:94`, `:111`), with legacy total‑capacity share preserved. Tests cover contest functions, revenue PV, and endogenous lambda pass‑through (tests/test_duopoly.py:46–176).
- Default boundary (Leland): Uses the negative characteristic root of L and an effective revenue coefficient that includes L‑inference and H‑continuation value (default_boundary in `src/ai_lab_investment/models/duopoly.py:283` ff.). Equity/debt value and recovery logic are consistent with standard Leland structure (debt_value in `src/ai_lab_investment/models/duopoly.py:372` ff.). Tests cover default boundary behavior and credit decomposition (tests/test_duopoly.py:318–406).
- Valuation layer: Growth option decomposition splits assets‑in‑place, expansion option, and regime‑switch value by evaluating L with and without switching (`src/ai_lab_investment/models/valuation.py:1–120`). Credit metrics are derived via duopoly objects (e.g., `valuation.py:185–235`), and the “Dario dilemma” computes value loss from belief mismatch at the NPV level (`valuation.py:235–325`). Tests cover these components (tests/test_valuation.py:24–216).

Overall, the implementations match the paper’s derivations, including the role of `beta_H` in the trigger markup and the structure of L’s option with a particular solution term.

### 2. Code Quality and Testing
- Structure and typing: Clear module boundaries (`models/`, `calibration/`, `figures/`, `utils/`) with type hints and docstrings throughout. Pipeline orchestration is Hydra‑based with phase toggles (`src/ai_lab_investment/pipeline.py:1–220`).
- Numerical stability: Objective functions guard invalid regions by returning large sentinels; multiple starting points are used for non‑convex searches; caching avoids redundant work in `SingleFirmModel` and `DuopolyModel`.
- Tests: The suite is broad and specific, including symbolic checks (tests/test_symbolic_duopoly.py:53–234), comparative statics, and scenario coverage across single‑firm, duopoly, N‑firm, valuation, and calibration. Reproducibility is explicitly tested for simulated paths (tests/test_base_model.py:161–170).
- Coverage: Unable to run `just test`/`uv run pytest --cov` due to sandbox/network limits. Attempted `just test` failed when `uv` could not initialize cache/write to `~/.cache` and later due to network for dependency resolution. Qualitatively, models are well covered; figures and pipeline entrypoints appear untested, which is typical and acceptable, but worth documenting.
- Reproducibility: Figure generator sets deterministic seeds where relevant and applies a publication‑quality style (paper/generate_figures.py:1–120). Paths are relative; outputs to `paper/figures/` are consistent.

## Part 2: Paper and Presentation Review
### 3. Paper Content Review
#### 3a. Theoretical Validity
- Demand and regimes: The GBM environment with regime switching is precisely stated (paper/_model.qmd: “eq-gbm”), with H absorbing and risk‑adjusted valuation assumptions clearly spelled out.
- Endogenous arrival: The arrival‐rate function `tilde{lambda}` in Eq. (endogenous‑lambda) matches implementation (`ModelParameters.lambda_tilde` in `src/ai_lab_investment/models/parameters.py:166` ff.). The paper correctly distinguishes exogenous (`xi=0`) and endogenous cases and treats the latter numerically.
- H‑regime option: The H‑regime option value is used as the non‑homogeneous term when solving the L‑regime HJB (paper/_model.qmd around eq‑hjb‑L and eq‑particular‑C), matching `_particular_solution_coeff` and `option_value_L` in code.
- Trigger markup and A_eff: The use of `beta_H/(beta_H−1)` markup and an effective revenue coefficient combining L‑inference and H‑continuation is documented in the paper and implemented in the phi‑aware single‑firm and duopoly models.
- Default risk: The default boundary leverages the negative root and includes coupon, bankruptcy cost, and continuation value; this aligns with the narrative “faith‑based survival” mechanism in the abstract and model section.

Minor notes:
- Time‑to‑build `tau` exists in parameters but is not integrated in the analytical routines; the paper could flag this as future work or note where `tau>0` would be handled numerically.
- The term “phi” is overloaded: in `base_model.py` there is a legacy alias `_phi` for the option‑premium ratio Phi (not training share). Consider renaming to avoid confusion.

#### 3b. Writing Quality
- Clarity: Generally clear and precise; equations and boundary conditions are labeled and referenced. The H vs. L roles for inference/training are well motivated.
- Notation: Consistent with a few potential confusions around phi vs Phi (see above). Suggest explicitly reserving Phi for the option‑premium ratio and using only `phi` for training share.
- Length/focus: Appropriate for a top‑journal single‑paper with extensions. The endogenous‑lambda results are wisely presented as numerical analogues of closed‑form exogenous results.
- Abstract: Accurately summarizes contributions, emphasizes “faith‑based survival,” and previews comparative statics and valuation.

#### 3c. Journal Fit
- Contribution significance: Strong theoretical contribution with clear finance relevance (irreversible investment, default, preemption). The revealed‑beliefs angle provides empirical traction.
- Methodological rigor: Solid analytical core plus careful numerical verification; extensive unit tests in the repo add credibility.
- Formatting/conventions: Paper and figures follow economics style. Quarto project is organized and reproducible.
- Best target: Journal of Finance — topical fit (real options, corporate investment, default), clear empirical hooks; RFS also a fit. Econometrica is plausible but would likely require deeper theoretical generality beyond the applied focus here.

### 4. Figures
- Generation: `paper/generate_figures.py` produces 10+ figures using model outputs. Each plot sets labels, titles, and legends with a consistent style (Econometrica/JF friendly).
- Spot‑checks for code‑figure consistency:
  - fig_option_value: Uses `option_value_H` and NPV at fixed K* with the area between shaded appropriately (paper/generate_figures.py:120–190) — consistent with theory.
  - fig_comparative_statics: Calls `SingleFirmModel.comparative_statics` and overlays K* and X* with twin axes (paper/generate_figures.py:192–240).
  - fig_default_boundaries: Solves duopoly equilibrium across leverage to plot follower trigger and default boundary (paper/generate_figures.py:280–345) — coherent with default logic.
  - fig_growth_decomposition: Decomposition matches `ValuationAnalysis.growth_option_decomposition` logic (paper/generate_figures.py:880–960).
- Publication quality: Fonts, DPI, axis formatting, and legend placement are set globally. Minor suggestion: ensure all math text uses consistent LaTeX formatting; currently set `text.usetex=False` which is fine given fonts.

### 5. Calibration and Results
- Parameters: Baseline values in `src/ai_lab_investment/calibration/data.py` look reasonable (e.g., `alpha=0.40`, `gamma=1.5`, `r=0.12`, `lam≈0.10`). The mapping to `ModelParameters` is straightforward via `CalibrationData.to_model_params`.
- Sources: `CalibrationData.sources` provides categories, but several key inputs would benefit from more specific citations (e.g., training fractions, GPU counts, WACC estimates). Consider adding exact report/filing links or footnote references in the paper.
- Sensitivity: Comparative statics are implemented for key parameters; revealed‑beliefs sensitivity helpers exist (see `RevealedBeliefs.sensitivity_analysis`). Suggest adding a small figure/table in the paper for sensitivity of implied lambda to `alpha`/`r`/`sigma_H`.
- Revealed beliefs: Inversion uses `F_L(X_ref)/I(K*_H)` monotonicity in lambda (see `RevealedBeliefs._model_intensity_at_lambda`). This is sound, but the paper should discuss identification assumptions explicitly (e.g., holding cost parameters fixed and treating phi if observed).
- Growth decomposition: Implementation matches narrative; the “no‑switch” comparison in L uses `lam→~0` to isolate switch value (valuation.py:80–108).

### 6. Slides Review
- Structure: Long‑form slides include intro, model, results, calibration, revealed beliefs, and conclusion (slides/long-form/index.qmd). Content mirrors the paper.
- Clarity: Quarto RevealJS with modular sections; equations are simplified appropriately for presentation. Ensure slide figures match paper versions exactly (same seeds/parameters).

## Summary of Issues
### Critical Issues
- Clarify the mapping between compute scaling exponents and the arrival‑rate elasticity parameter `eta`. The paper currently references Kaplan/Hoffmann; it should explain how loss‑vs‑compute translates to arrival‑rate responsiveness, note assumptions, and label `eta` as “calibrated/inferred” rather than “directly observed” if applicable. Provide citations and, if possible, a sensitivity range in calibration.

### Major Issues
- Terminology collision on “phi”: In `src/ai_lab_investment/models/base_model.py`, `_phi` is a legacy alias for the option‑premium ratio Phi. This can be confused with the training share `phi`. Suggest renaming `_phi` to `_Phi_ratio` or similar and updating callers (base_model.py) and any tests that reference it.
- Test coverage report: Could not be computed in this environment. Please run `just test` locally and attach coverage. Consider adding minimal smoke tests for figure generation functions and `pipeline.py` task routing (non‑graphical), if feasible.
- Data sourcing: Add precise citations for training fraction estimates and CapEx intensities used in `CalibrationData` and reflect these in paper footnotes.

### Minor Issues
- Time‑to‑build `tau`: Present in parameters but unused in analytic routines; add a brief note in the paper indicating how `tau>0` would be handled (e.g., numerical delay in the trigger condition) or mark as future work.
- Numerical docs: Briefly note in an appendix the multi‑start strategy and sentinel‑value rejection used in non‑convex optimizations to assure readers about global‑optimum robustness.
- Default boundary documentation: In the paper, include a short derivation linking the negative root and recovery term to the implemented formulas (duopoly.py:340–420) for completeness.

## Overall Recommendation
- Recommendation: Revise and resubmit.
- Target journal: Journal of Finance. Rationale: strong corporate‑finance fit (irreversible investment under uncertainty, credit risk, competition) with a clean empirical pathway via revealed beliefs. RFS is also a good alternative. For Econometrica, deeper theoretical generality or empirical estimation may be needed.

## Notes on Test Execution in This Environment
- Attempted `just test` → `uv run pytest --cov` failed due to sandboxed cache writes to `~/.cache/uv` and later due to network‑blocked dependency resolution. A local run should succeed with `uv sync && just test`. If constrained, set `UV_CACHE_DIR` to a workspace subdirectory and ensure dependencies are pre‑synced.
