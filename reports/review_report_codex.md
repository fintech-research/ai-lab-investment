# Review Report: AI Lab Investment

**Reviewer:** codex
**Date:** 2026-02-25

## Executive Summary
The codebase is well structured, mathematically consistent with the paper’s derivations, and thoroughly tested (227 tests across 7 files). The two model modes are implemented cleanly: the simple single‑firm trigger/capacity mode and the full phi‑aware mode used for paper figures and all multi‑firm settings. Symbolic verification (sympy) mirrors the analytical solution and matches the numerical code, providing strong internal validation. Figure generation follows the “single source of truth” rule via `src/ai_lab_investment/figures/paper.py`, and the thin wrapper `paper/generate_figures.py` correctly delegates all computation.

I could not execute `just install/check/test` due to restricted network access in this environment; conclusions below are based on static inspection of the code, tests, and paper sources. The test suite appears comprehensive and directly exercises the key results (roots, smooth pasting, C coefficient, default boundary, preemption, phi optimization, calibration/revealed beliefs).

The paper is well written and technically sound. The model’s extensions (training–inference allocation, regime‑specific contests, endogenous default) are justified and mapped to the implemented equations. Figures are consistent with the code and publication-ready. A few minor consistency issues (notably a directory naming mismatch and a small docstring claim about numerical method) should be fixed. Overall, I recommend “Revise and resubmit” with minor code/documentation fixes and an explicit note about dynamic phi as a limitation; best journal fit is JF or RFS.

## Part 1: Code Validation

### 1. Mathematical Correctness
- Characteristic roots and ODEs
  - Positive root implementation: `src/ai_lab_investment/models/parameters.py:238` computes the quadratic root for `(σ^2/2)β(β−1)+μβ−discount=0` and is used to set `beta_H` and `beta_L` with the correct effective discount in L (`r+λ`), see `parameters.py:131-139`. Tests: `tests/test_parameters.py::TestPositiveRoot::*` and `test_L_regime_uses_r_plus_lambda` in `tests/test_symbolic_duopoly.py` verify the mapping and sign.
  - L‑regime coupled ODE: `src/ai_lab_investment/models/symbolic_duopoly.py:200-257` derives the general solution and particular coefficient `C = -λ·B_H / Q_L(β_H)`. The code computes the same in `src/ai_lab_investment/models/base_model.py:151-169`. Tests: `tests/test_symbolic_duopoly.py::TestLRegimeODE::test_C_matches_code` passes this identity.

- Option value structure and smooth pasting
  - H‑regime option: value‑matching/smooth‑pasting is implemented in `base_model.py:111-149` and used in `option_value_H` (`base_model.py:242-251`). Tests: `tests/test_base_model.py::TestRegimeH::test_smooth_pasting` and `test_value_matching` confirm both conditions.
  - L‑regime option: code switches between two‑term `D_L X^{β_L}+C X^{β_H}` below the trigger and installed value above (`base_model.py:253-270`). The symbolic verification module confirms: `tests/test_symbolic_duopoly.py::TestOptionValueStructure::*` and `::TestSmoothPasting` (when an interior L‑trigger exists).
  - Baseline simplification (Assumption A3): `verify_baseline_simplification()` in `src/ai_lab_investment/models/symbolic_duopoly.py:626-656` aligns with code’s `has_interior_trigger('L')` (`base_model.py:73-81`) and tests (`tests/test_base_model.py::TestPhiAndExistence::test_no_interior_trigger_L_default`).

- Effective revenue coefficient with training–inference allocation
  - Single firm (phi‑aware): `A_eff(φ,K)` in `base_model.py:431-454` matches the paper’s eq‑a‑eff (L term plus H continuation via λ and `A_H`). Tests: `tests/test_base_model.py::TestEffectiveRevenueCoeff` cover positivity, no‑switch limit, and monotonicity.
  - Duopoly: `src/ai_lab_investment/models/duopoly.py:147-194` correctly multiplies by regime‑specific contest shares `s_L`/`s_H` and uses `λ̃` when endogenous (`duopoly.py:76-88`). Tests: `tests/test_duopoly.py::TestRegimeContestFunctions::*` and `::TestEndogenousLambda::*` confirm behavior.
  - N‑firm: `src/ai_lab_investment/models/nfirm.py:127-160` mirrors the duopoly definition with N‑firm shares.

- Default boundary and credit risk
  - Default boundary formula: `X_D = [β_-/(β_-−1)]·[c_D/r + δK/r]/A_eff` implemented in `src/ai_lab_investment/models/duopoly.py:303-327`, with the negative root built from `(r+λ̃)` (`duopoly.py:353-365`). Symbolic signs and smooth pasting are verified in `tests/test_symbolic_duopoly.py::TestDefaultBoundary::*`. Debt valuation uses standard Leland recovery structure (`duopoly.py:432-467`).

- Preemption and follower/leader structure
  - Follower 3D optimization over `(K,φ,lev)` in `duopoly.py:528-618` with trigger using `β_H` and `A_eff` (consistent with the paper’s methodology). Leader value incorporates monopoly period, follower entry, and H‑regime value (`duopoly.py:624-742`). Preemption solved by bisection (`duopoly.py:810-832`). Tests: `tests/test_duopoly.py::TestLeader::*`, `::TestPreemptionEquilibrium::*` check leader before follower, required keys, and positivity.

- N‑firm sequential equilibrium
  - Entrant 2D optimization (`nfirm.py:116-160`, `solve_entrant`) and iterative backward refinement (`nfirm.py:197-239`) match the described sequential structure. Tests: `tests/test_nfirm.py::TestSequentialEquilibrium::*` cover ordering, positivity, and share summation; `::TestVerification` compares N=2 against duopoly.

Overall, the code and symbolic derivations are consistent and exercise the expected real‑options identities through tests.

### 2. Code Quality and Testing
- Structure and clarity
  - Clear module boundaries: parameters → base_model → duopoly → nfirm → valuation. Public API surfaced via `src/ai_lab_investment/models/__init__.py`.
  - Two model modes are cleanly separated and documented in `src/AGENTS.md`.

- Tests coverage and intent
  - Tests target key invariants and economics: roots, smooth‑pasting, option value structure (including two‑term vs one‑term), regime‑specific contests, default boundary signs, preemption ordering, phi comparative statics, and revealed‑beliefs inversion. File examples: `tests/test_symbolic_duopoly.py::TestOptionValueStructure`, `tests/test_duopoly.py::TestDefaultRisk::test_negative_root_is_negative`, `tests/test_valuation.py::TestDarioDilemma::*`.

- Pipeline and configuration
  - Entry point and Hydra toggles: `src/ai_lab_investment/__main__.py`, `pipeline.py` use `conf/config.yaml` flags. Figure generation is centralized in `src/ai_lab_investment/figures/paper.py` and invoked only by `paper/generate_figures.py` as required by AGENTS.md.

- Reproducibility and env
  - Uses `uv` workflows (`just install/check/test`) and `.env-sample`. Data/results directories are resolved via `utils/directories.py`. Naming mismatch noted below.

- Style/tooling
  - Ruff configured for py313 with autofix; pre‑commit and ty hooks in `pyproject.toml` and `.pre-commit-config.yaml`. Docstrings and inline comments are concise and mostly used where derivations are non‑obvious.

Issues and suggestions:
- Inconsistent download cache directory naming
  - `just init-data-dir` creates `raw/download-cache` (hyphen), while `get_data_directories()` returns `raw/download_cache/` (underscore). See `justfile:20-27` vs `src/ai_lab_investment/utils/directories.py:...` (download path constructed at `directories.py:28-36` and specifically `download_dir = data_dir / "raw" / "download_cache/"`). Fix by standardizing on `download-cache` in `directories.py` and tests/docs.
- Minor docstring mismatch
  - `src/ai_lab_investment/models/nfirm.py` top‑level docstring mentions “finite‑difference methods on a log‑X grid,” but the implementation uses direct 2D optimization and backward induction. Update the docstring to avoid confusion.
- Optional: create figures directories under `RESULTS_DIR` if used by pipeline
  - `get_results_directories()` does not `mkdir` subdirectories; ensure figure writers create paths or `mkdir` when toggling pipeline tasks to true.

## Part 2: Paper Review

### 3. Paper Content Review

#### 3a. Content and Results
- Model building
  - The progression—single‑firm (analytical) → duopoly (semi‑analytical with preemption/default) → N‑firm (numerical)—is natural and well motivated. The training–inference split provides a genuine trade‑off across regimes and is tightly integrated with the real‑options machinery.
- Identification (revealed beliefs)
  - The inversion uses investment intensity `F_L(X_ref)/I(K*_H)` and, in the phi‑aware variant, joint moments `(intensity, φ*)`. Assumptions are explicit in `_calibration.qmd` and `src/ai_lab_investment/calibration/revealed_beliefs.py`. The paper appropriately frames results as illustrative rather than structural estimation; this is reasonable given data scarcity and model scope.
- Default risk and faith‑based survival (Proposition 2)
  - The code implements `X_D` exactly as in eq‑default‑boundary and uses `β_-` with effective discount `(r+λ̃)`. Monotone signs `∂X_D/∂A_eff<0`, `∂X_D/∂c_D>0` are checked symbolically and in tests.
- Dario’s dilemma
  - Unlevered and levered versions in `valuation.py:160+` match the description; timing and convex cost channels generate the asymmetry. Numerical, not closed form, as stated.

#### 3b. Writing Quality
- Clarity and notation
  - Clear exposition. Notation is consistent; symbols are defined in Appendix tables (e.g., Table of parameters and notation in `paper/_appendix.qmd`). Equation labels are present (e.g., eq‑a‑eff‑duopoly) and used consistently. Risk‑adjusted valuation assumptions are clearly stated in `paper/_model.qmd`.
- Length and focus
  - Appropriate for a top journal submission; technical details are mostly contained in the appendix and symbolic module. The “dynamic φ” limitation is acknowledged in `paper/_discussion.qmd` with a two‑period intuition—this is good, but adding a short sensitivity experiment (e.g., ex‑post φ adjustment thought experiment) would strengthen it.
- Abstract and conclusion
  - Accurate and not over‑claiming; conveys contributions, methods, and findings effectively.

#### 3c. Journal Fit
- Contribution significance and rigor
  - The unified real‑options + regime‑switching + strategic competition + default framework with training/inference allocation is a meaningful theoretical contribution for corporate finance/IO. The symbolic verification and extensive testing increase credibility.
- Best fit recommendation
  - JF or RFS. The paper’s focus on investment timing, capital structure, and competition under uncertainty aligns more closely with finance journals. Econometrica would require either sharper theoretical novelty or an empirical component beyond calibration.

### 4. Figures
- Single source of truth
  - All 11 figures are defined in `src/ai_lab_investment/figures/paper.py` and saved by `paper/generate_figures.py`, which only applies styles—compliant with project rules.
- Spot checks of code→figure pipeline (3 examples)
  - Figure 1 (Sample paths): `create_sample_paths()` simulates regime‑switching GBM using `SingleFirmModel.simulate_demand` and overlays `X_H^*` (`figures/paper.py:13-62`), consistent with the model.
  - Figure 4 (λ vs option value): `create_lambda_option_value()` sweeps λ, computes `F_L(X_ref)`, `F_H(X_ref)`, and `C` from `base_model` (`figures/paper.py:94-138`), matching the economics (H curve independent of λ, L curve increasing in λ through C).
  - Figure 5 (Default boundaries): `create_default_boundaries()` sweeps leverage and extracts `X_F^*`, `X_P`, and `X_D` from the duopoly equilibrium (`figures/paper.py:158-209`). The shaded operating region matches definitions.
- Publication quality
  - Styles configured for PDF/PNG; axes labels use math notation; legends are clear. No duplicated computations in `paper/generate_figures.py`.

### 5. Calibration and Results
- Parameter values and sources
  - Baseline parameters and firm archetypes are documented in `src/ai_lab_investment/calibration/data.py` and cited in `_calibration.qmd`. Values are plausible given public reports; interpretations (e.g., `α=0.40`, `η=0.07`) are consistent with scaling‑law literature.
- Sensitivity and comparative statics
  - Comparative statics functions exist in single‑firm, duopoly, and N‑firm modules; tests exercise shapes and monotonic directions where applicable.
- Revealed beliefs plausibility
  - The inversion returns positive lambdas for most firms; the phi‑aware variant reports `(λ̂, φ_model, φ_observed)`—sensible for diagnostics. The paper appropriately caveats identification.
- Growth decomposition
  - Decomposition with and without φ is implemented (`valuation.py:23-86`, `:262-321`) and matches the paper’s narrative (growth options dominate at low installed K).

## Summary of Issues

### Critical Issues
- None blocking correctness identified in static review.

### Major Issues
- None.

### Minor Issues
- Directory naming mismatch for download cache
  - Hyphen vs underscore (`justfile` vs `utils/directories.py`). Standardize to `download-cache` in code to match initialization and documentation.
- Docstring claim in N‑firm module
  - Remove/adjust “finite‑difference methods on a log‑X grid” in `src/ai_lab_investment/models/nfirm.py` to reflect the implemented optimization/backward induction approach.
- Optional robustness note
  - Consider adding a short appendix sensitivity on dynamic φ (even qualitative), since the discussion highlights this limitation.

## Overall Recommendation
- Recommendation: Revise and resubmit (minor revision).
- Target journal: Journal of Finance or Review of Financial Studies. The contribution and methodology align with corporate finance and IO under uncertainty; Econometrica may be a stretch without an empirical component or further theoretical novelty.

Notes on execution: I did not run `just install/check/test` due to restricted network access in this environment. If desired, I can run `just install && just check && just test` to confirm the test suite passes and regenerate figures (`uv run python paper/generate_figures.py`) once network permissions are granted.
