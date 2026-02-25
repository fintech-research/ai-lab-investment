# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Research Project

"Investing in Artificial General Intelligence"

A unified model of irreversible capacity investment under demand uncertainty with regime switching, oligopoly competition, endogenous default, and diminishing returns calibrated to AI scaling laws. The model delivers: (i) analytical characterization of optimal investment triggers and capacity in a duopoly with default risk, (ii) numerical solutions for N firms with dynamic training/inference allocation, and (iii) an asymmetric "Dario's dilemma" showing that overinvestment carries greater downside risk than underinvestment. Target: JF, RFS, or Econometrica.

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

- **Research paper**: `paper/` directory, Quarto → PDF/HTML
- **Slides**: `slides/long-form/`, Quarto → RevealJS HTML
- **API docs**: MkDocs with mkdocstrings, served from `docs/`

## Paper Writing Style

- **No bold paragraph headings.** Never use `**Bold text.**` as a pseudo-heading to start a paragraph in the paper. If a section needs subdivision, use proper Quarto/markdown headings (`###`, `####`). Otherwise, just start the paragraph with its content — no label.
- Target style: top finance journals (JF, RFS, Econometrica). Concise, formal, no filler.

## Figure Generation

**Single source of truth.** All figure logic lives in `src/ai_lab_investment/figures/` (phase1–5 modules + phi_allocation). The paper script `paper/generate_figures.py` must import and call these functions — never duplicate model logic or plotting code. When updating a figure, edit only the pipeline module; `generate_figures.py` is a thin wrapper that applies paper styling and saves to `paper/figures/`.

- Never copy-paste model computations (triggers, valuations, spreads) into `generate_figures.py`
- If a figure needs a new computation, add it to the appropriate module in `src/ai_lab_investment/figures/` and import it
- After modifying any figure function, always regenerate via `uv run python paper/generate_figures.py` and visually inspect the output

## Code Style

- Ruff for linting and formatting (line length 88, target Python 3.13)
- `assert` statements allowed in tests (`S101` ignored for `tests/*`)
- Pre-commit hooks run ruff check (with autofix) and ruff format on commit
