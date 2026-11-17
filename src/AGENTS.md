# AGENTS.md — src/

Rules for working in `src/ai_lab_investment/`. Global rules are in `@../AGENTS.md`.

## Model Architecture

**Hierarchy:** `models/parameters.py` → `base_model.py` → `duopoly.py` → `valuation.py`

**Two model modes** — do not confuse them:
- *Simple* (no φ): `installed_value()`, `optimal_trigger_and_capacity()` — for H-regime analysis using combined `A_L`/`A_H`.
- *Full* (with φ): `installed_value_with_phi()` matches paper eq-a-eff. The single-firm entry points return the **model of record**, the exact piecewise problem (issue #176): `solve()` gives a `SingleFirmSolution` (whether a finite pre-switch trigger exists, the precommitted-scale policy, the value of waiting, the post-switch policy, the pure-power error), `optimal_trigger_capacity_phi()` the precommitted-scale (X*, K*, φ*), `option_value_with_phi()` the exact value.
- *Pure-power approximation*: `pure_power_trigger_capacity_phi()`, `pure_power_option_value()`. The former full-model solution, kept so its error can be reported and the earlier draft's numbers reproduced. `duopoly.py`, `valuation.py`, `robustness.py`, `calibration/` and the other paper figures are still pinned to it (comments name the issue, #177 to #184, that re-solves each); do not switch one of them without re-pinning its tests and paper numbers.

**`symbolic_duopoly.py`** — verification/documentation module using SymPy. Not called in the pipeline. Used to verify that `base_model.py` and `duopoly.py` implement the correct ODE solution.

**`piecewise_option.py`**: core solver of the single-firm model of record, the *exact* piecewise L-regime stopping problem (the HJB forcing term is the H-regime option only below X_H*, and the exercised H payoff above it). First half: `PiecewiseOptionModel` (two-region closed form at fixed (K, φ), `precommitted_optimum()` for the demand-free optimal policy, pure switching, the exercise envelope, the Brennan--Schwartz LCP), `solve_single_firm()` / `SingleFirmSolution`, and the belief comparative statics (`belief_comparative_statics`, `belief_trigger_ranges`, grid `BELIEF_GRID`). Second half (from `reduced_form_reference` on): verification, the error of the pure-power approximation against the exact solution (`piecewise_bias`, `envelope_bias`, the sweeps and dilemma re-checks behind Internet Appendix B). `optimal_policy(X_0)` states the policy at an evaluation demand and returns the best *immediate* investment when X_0 is above the trigger (low λ); use `precommitted_optimum()` unless reproducing those reports. Run `uv run python -m ai_lab_investment.models.piecewise_option [sweep]` for the solution, belief table and error report.

**`capability_stock.py`**: research prototype for issue #174 (not in the pipeline). Its default specification is the unrestricted single-firm problem, and `solve_single_firm()` uses it for the unrestricted policy and the value of waiting; the added primitives feed no paper number. Solves the exact pre-switch stopping problem under four added primitives: a late-entry discount `theta`, a late-training effectiveness for entrants and for incumbents' redeployed compute (`late_training`, `redeploy`), a fixed installation cost, and an accumulating capability stock. The defaults are the paper's exact problem, so `CapabilityStockModel(params)` reproduces the unrestricted `PiecewiseOptionModel` numbers, and `pure_power_policy(params, beta=params.beta_H)` reproduces the reduced model. The solution is one scalar root (algebraic below the entrant's trigger, one quadrature above it), checked by the Brennan--Schwartz solver of `piecewise_option.py` through `model.lcp` and by a policy-iteration LCP on the exercise envelope (`joint_lcp`). Run `uv run python -m ai_lab_investment.models.capability_stock` for the tables behind the issue comment; the numbers are pinned in `tests/test_capability_stock.py`.

**`preemption_exact.py`**: diagnostic module (not in the pipeline; issue #173) for the L-regime preemption game in the exact primitives at zero leverage: the leader's and follower's values solve the L-regime ODE with the follower's exact post-switch option as forcing (Green's function, `ForcedClaim`), under both post-switch scale assumptions of Internet Appendix B, with an independent finite-difference/LCP check (`finite_difference_subgame`). `ExactPreemptionGame.rent_equalization` holds the leader at the reduced-form (K*, φ*); `rent_equalization_reoptimized` lets the leader choose scale at entry. Run `uv run python -m ai_lab_investment.models.preemption_exact` for the λ × γ table (about ten minutes). Pinned in `tests/test_preemption_exact.py`. It reproduces no paper number and feeds none.

**`robustness.py`** — the ±25% one-at-a-time parameter-perturbation sweep behind Internet Appendix E. Re-computes the dilemma asymmetry, capacity-gap fraction, faith thresholds, and preemption discount at each draw, and *reports* (A1)/(A2) failures instead of truncating them. Run `just run-sweep`, or via the `tasks.robustness_sweep` pipeline flag. Its paper-pinned numbers live in `tests/test_robustness.py::TestPaperNumbers` — update the appendix text and the test together.

**`calibration/`** — `data.py` holds the four stylized firm archetypes (`get_stylized_firms()`: Anthropic-, OpenAI-, Google-, xAI-like) and the baseline calibration; `revealed_beliefs.py` infers implied λ from observed investment. Revealed beliefs appear in the slides and the paper's conclusion (future work), not as a paper section.

## IMPORTANT: Figure Generation

`figures/paper.py` is the single source of truth for all paper figures (11 `create_*` functions). Never add model computations elsewhere.

The other `figures/` modules produce exploratory output for the Hydra pipeline (`phase1.py`, `phase2.py`, `phase4.py`, `phase5.py`) and write to `RESULTS_DIR`. They do **not** feed the paper — do not edit them when a paper figure needs to change.

## Key Analytical Parameters

At baseline: β_L⁺ ≈ 3.01 (positive root of L-regime ODE with discount r+λ), β_H ≈ 1.55. Single firm, model of record: φ* ≈ 0.7009, X_H* ≈ 0.00278, K_H* ≈ 0.00673; precommitted-scale X* ≈ 0.00926, K* ≈ 0.01578; with scale chosen at the switch the firm waits (waiting margin 1.077; finite trigger only for λ < 0.0729). Pure-power approximation: X ≈ 0.00472, K ≈ 0.00673 (= K_H*). The L-regime insufficiency condition (the former A3, ratio 1.67) is descriptive only; `verify_baseline_simplification()` in `symbolic_duopoly.py` reports that the pure-power form is *not* exact (A_1 ≈ −8.5e3).

## Testing

Tests are in `tests/` (one file per module; about 630 tests). `tests/test_base_model.py` pins the single-firm model of record (`TestSingleFirmSolution`, `TestBeliefComparativeStatics`, `TestProposition1ClosedForm`) and keeps everything about the pure-power approximation in `TestPurePowerApproximation`. Run with `just test`. `assert` statements allowed in tests. Several tests pin paper numbers (e.g. `TestAppendixERobustness` in `test_valuation.py` checks the Internet Appendix E tables) — if a model change moves those numbers, update the paper text and the test together.

The closed-form algebra these modules implement is independently machine-checked in Lean (`../lean/`, see `lean/README.md`). Changing a closed form means checking the corresponding Lean theorem too.

## Code Style

- Ruff: line length 88, Python 3.13.
- No docstrings or comments on code you didn't change.
- Pre-commit hooks enforce formatting.
