# AGENTS.md — src/

Rules for working in `src/ai_lab_investment/`. Global rules are in `@../AGENTS.md`.

## Model Architecture

**Hierarchy:** `models/parameters.py` → `base_model.py` → `duopoly.py` → `valuation.py`

**Two model modes** — do not confuse them:
- *Simple* (no φ): `installed_value()`, `optimal_trigger_and_capacity()` — for H-regime analysis using combined `A_L`/`A_H`.
- *Full* (with φ): `optimal_trigger_capacity_phi()`, `installed_value_with_phi()` — matches paper eq-a-eff; used for all paper results.

**`symbolic_duopoly.py`** — verification/documentation module using SymPy. Not called in the pipeline. Used to verify that `base_model.py` and `duopoly.py` implement the correct ODE solution.

**`piecewise_option.py`** — verification module (not in the pipeline) solving the *exact* piecewise L-regime stopping problem: the HJB forcing term is the H-regime option only below X_H*, and the exercised H payoff above it. Quantifies the bias of the paper's pure-power (unconditional-A_eff) convention against the exact free-boundary solution, with an independent Brennan--Schwartz LCP check. Run `uv run python -m ai_lab_investment.models.piecewise_option [sweep]` for the bias report.

**`calibration/`** — `data.py` holds the four stylized firm archetypes (`get_stylized_firms()`: Anthropic-, OpenAI-, Google-, xAI-like) and the baseline calibration; `revealed_beliefs.py` infers implied λ from observed investment. Revealed beliefs appear in the slides and the paper's conclusion (future work), not as a paper section.

## IMPORTANT: Figure Generation

`figures/paper.py` is the single source of truth for all paper figures (11 `create_*` functions). Never add model computations elsewhere.

The other `figures/` modules produce exploratory output for the Hydra pipeline (`phase1.py`, `phase2.py`, `phase4.py`, `phase5.py`) and write to `RESULTS_DIR`. They do **not** feed the paper — do not edit them when a paper figure needs to change.

## Key Analytical Parameters

At baseline: β_L⁺ ≈ 3.01 (positive root of L-regime ODE with discount r+λ), β_H ≈ 1.55. Assumption A3 holds in the sense the paper uses it, i.e. the pure-power F_L ∝ X^{β_H} convention (see `piecewise_option.py` for its bias). `verify_baseline_simplification()` in `symbolic_duopoly.py` confirms this.

## Testing

Tests are in `tests/` (7 files, one per module; ~250 tests). Run with `just test`. `assert` statements allowed in tests. Several tests pin paper numbers (e.g. `TestAppendixERobustness` in `test_valuation.py` checks the Internet Appendix E tables) — if a model change moves those numbers, update the paper text and the test together.

The closed-form algebra these modules implement is independently machine-checked in Lean (`../lean/`, see `lean/README.md`). Changing a closed form means checking the corresponding Lean theorem too.

## Code Style

- Ruff: line length 88, Python 3.13.
- No docstrings or comments on code you didn't change.
- Pre-commit hooks enforce formatting.
