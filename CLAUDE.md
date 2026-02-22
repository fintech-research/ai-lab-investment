# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Research Project

"Investing in Intelligence: Real Options, Default Risk, and Strategic Competition in AI Compute Infrastructure"

A unified model of irreversible capacity investment under demand uncertainty with regime switching, oligopoly competition, endogenous default, and diminishing returns calibrated to AI scaling laws. The model delivers: (i) analytical characterization of optimal investment triggers and capacity in a duopoly with default risk, (ii) numerical solutions for N firms with dynamic training/inference allocation, and (iii) a "revealed beliefs" methodology for inferring AI labs' private probability assessments of transformative AI arrival from observable investment decisions. Target: JF, RFS, or Econometrica.

The research plan is detailed in `plan.md`.

## Documentation Lookup

Use the Context7 MCP tool to fetch up-to-date documentation for libraries and software used in this project before writing code. This ensures compatibility with current APIs.

## Common Commands

All commands use `just` (task runner) and `uv` (Python package manager). Run `just help` to list all available recipes. Key commands:

- `just check` — linting, formatting, type checking (pre-commit + ty)
- `just test` — pytest with coverage
- `just run-pipeline` — run the analysis pipeline (`uv run python -m ai_lab_investment`)
- Single test: `uv run pytest tests/test_file.py::test_name`

## Architecture

### Pipeline (`src/ai_lab_investment/`)

- **Entry point**: `__main__.py` calls `pipeline()` from `pipeline.py`
- **Pipeline orchestration**: `pipeline.py` uses `@hydra.main` decorator, loading config from `conf/config.yaml`
- Pipeline steps are toggled via config flags (`cfg.data.download`, `cfg.tasks.simulations`, etc.)
- Hydra supports CLI config overrides (e.g., `uv run python -m ai_lab_investment data.download=true`)

### Configuration

- **Hydra config**: `conf/config.yaml` controls pipeline behavior (which steps run, parameters)
- **Environment variables**: `.env` file (copied from `.env-sample`) sets `DATA_DIR`, `RESULTS_DIR`, `RESOURCES_DIR`
- Directory paths are resolved via `utils/directories.py` using `DataDirectories` and `ResultsDirectories` named tuples

### File Conventions

- `utils/files.py`: Timestamped file naming pattern `{name}_UTC{YYYYMMDD_HHMMSS}.ext` and `get_latest_file()` for retrieving the most recent version

### Outputs

- **Research paper**: `paper/` directory, Quarto → PDF (lualatex, Econometrica style)
- **Slides**: `slides/long-form/`, Quarto → RevealJS HTML
- **API docs**: MkDocs with mkdocstrings, served from `docs/`

## Code Style

- Ruff for linting and formatting (line length 88, target Python 3.13)
- `assert` statements allowed in tests (`S101` ignored for `tests/*`)
- Pre-commit hooks run ruff check (with autofix) and ruff format on commit
