# AGENTS.md — slides/

Rules for working in the `slides/` directory. Global rules are in `@../AGENTS.md`.

## Structure

Slides live in `slides/long-form/`. Entry point: `index.qmd`. Output: RevealJS HTML (`_output/ai_lab_investment.html`).

Sections: `_introduction.qmd`, `_model.qmd`, `_calibration.qmd`, `_results.qmd`, `_revealed_beliefs.qmd`, `_conclusion.qmd`. Config: `_quarto.yml`. Styling: `custom.scss`.

## Figures

- Slides use **PNG** figures (not PDF), symlinked from `paper/figures/`.
- To update a figure: edit in `src/ai_lab_investment/figures/paper.py`, regenerate with `uv run python paper/generate_figures.py` (creates both PDF and PNG), then the symlink picks up the new PNG automatically.
- Do not copy figure files; the symlink is intentional.

## Slide Writing Style

- Concise bullet points for presentation. Each slide conveys one idea.
- Math notation must match the paper exactly (same variable names, equation labels).
- Use `@fig-name` for figure references; figure IDs must match `paper/figures/fig_*.png`.
