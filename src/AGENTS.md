# AGENTS.md — src/

Rules for working in `src/ai_lab_investment/`. Global rules are in `@../AGENTS.md`.

## Model Architecture

**Hierarchy:** `models/parameters.py` → `base_model.py` → `duopoly.py` → `valuation.py`

**Two model modes** — do not confuse them:
- *Simple* (no φ): `installed_value()`, `optimal_trigger_and_capacity()` — for H-regime analysis using combined `A_L`/`A_H`.
- *Full* (with φ): `optimal_trigger_capacity_phi()`, `installed_value_with_phi()` — matches paper eq-a-eff; used for all paper results.

**`symbolic_duopoly.py`** — verification/documentation module using SymPy. Not called in the pipeline. Used to verify that `base_model.py` and `duopoly.py` implement the correct ODE solution.

## IMPORTANT: Figure Generation

`figures/paper.py` is the single source of truth for all paper figures (11 `create_*` functions). Never add model computations elsewhere.

## Key Analytical Parameters

At baseline: β_L⁺ ≈ 3.01 (positive root of L-regime ODE with discount r+λ), β_H ≈ 1.55. Assumption A3 holds: simplified F_L = C·X^{β_H} is valid. `verify_baseline_simplification()` in `symbolic_duopoly.py` confirms this.

## Testing

Tests are in `tests/` (7 files, one per module). Run with `just test`. `assert` statements allowed in tests.

## Code Style

- Ruff: line length 88, Python 3.13.
- No docstrings or comments on code you didn't change.
- Pre-commit hooks enforce formatting.
