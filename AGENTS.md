# AGENTS.md — Investing in Artificial General Intelligence

A unified model of irreversible capacity investment with regime-switching demand, duopoly competition, endogenous default, and AI scaling laws. Delivers analytical triggers and Dario's dilemma (overinvestment asymmetry). Target: JF, RFS, or Econometrica.

## Commands

All commands use `just` (task runner) and `uv` (Python package manager).

- `just check` — lint, format, typecheck (pre-commit + ty)
- `just test` — pytest with coverage
- `just run-pipeline` — full analysis pipeline (`uv run python -m ai_lab_investment`)
- `uv run pytest tests/test_file.py::test_name` — single test

Use the Context7 MCP tool to look up library documentation before writing code.

## Architecture

**Pipeline entry point:** `src/ai_lab_investment/__main__.py` → `pipeline.py` (Hydra, `conf/config.yaml`). Toggle steps via config flags; override via CLI (e.g., `data.download=true`).

**Core model hierarchy:**
`models/parameters.py` → `base_model.py` (single firm) → `duopoly.py` (2 firms) → `valuation.py` (credit risk, dilemma)

**Two model modes** — important distinction:
- *Simple mode* (no training fraction): `SingleFirmModel.installed_value()`, `optimal_trigger_and_capacity()` — uses combined `A_L`/`A_H` from `parameters.py`. Used for basic H-regime analysis and comparative statics.
- *Full model* (training-inference allocation): `optimal_trigger_capacity_phi()`, `installed_value_with_phi()` — uses `_effective_revenue_coeff_single()`, matching paper eq-a-eff. Used for all paper figures and the duopoly.

Paper figures use the full model.

## IMPORTANT: Figure Generation

All figure logic lives in `src/ai_lab_investment/figures/paper.py` (11 `create_*` functions). `paper/generate_figures.py` is a thin wrapper — it only applies styles and saves output.

- **Never duplicate model computations in `generate_figures.py`**
- If a figure needs new computation, add it to `paper.py` or a model module
- After any change, regenerate: `uv run python paper/generate_figures.py`

## Configuration

- Hydra config: `conf/config.yaml`
- Environment: `.env` (copy from `.env-sample`) — sets `DATA_DIR`, `RESULTS_DIR`, `RESOURCES_DIR`
- File naming: `{name}_UTC{YYYYMMDD_HHMMSS}.ext`; use `get_latest_file()` to retrieve most recent

## Code Style

- Ruff: line length 88, Python 3.13. `assert` allowed in `tests/` (S101 ignored).
- Pre-commit: ruff check (autofix) + ruff format on commit.

## Subdirectory instructions

- Paper writing and figures: `@paper/AGENTS.md`
- Slides: `@slides/AGENTS.md`
- Source code: `@src/AGENTS.md`
