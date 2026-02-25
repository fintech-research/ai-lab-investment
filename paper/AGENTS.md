# AGENTS.md — paper/

Rules for working in the `paper/` directory. Global rules are in `@../AGENTS.md`.

## Writing Style

- **No bold paragraph headings.** `**Bold text.**` as a pseudo-heading is forbidden. Use `###`/`####` for subdivisions, or just start the paragraph.
- Concise, formal prose. Top finance journal style (JF, RFS, Econometrica). No filler.
- Equations: use Quarto cross-references `@eq-name`, figures `@fig-name`, tables `@tbl-name`.

## Paper Structure

Main entry: `index.qmd` (includes all sections). Sections: `_introduction.qmd`, `_model.qmd`, `_calibration.qmd`, `_valuation.qmd`, `_discussion.qmd`, `_conclusion.qmd`, `_appendix.qmd`, `_literature.qmd`. Bibliography: `references.bib`.

## IMPORTANT: Figures

- All figures are PDFs in `paper/figures/` (one PDF + one PNG per figure, 11 total).
- Figure logic lives in `src/ai_lab_investment/figures/paper.py` — **never** in `generate_figures.py`.
- To update a figure: edit the `create_*` function in `paper.py`, then run `uv run python paper/generate_figures.py`.
- Do not add model code to `generate_figures.py`. It is a thin wrapper only.

## Key Model Facts (for editing proofs/text)

- Baseline: r=0.12, μ_L=0.01, μ_H=0.06, σ=0.25, λ=0.10, α=0.40, γ=1.50, δ=0.03
- β_L⁺ ≈ 3.01, β_H ≈ 1.55 (positive characteristic roots)
- Assumption A3: (1−1/β_L⁺)/α ≈ 1.67 ≥ 1 → simplified F_L = C·X^{β_H} valid at baseline
- φ̲ ≈ 0.18 (faith-based survival threshold), R ≈ 0.22
- All results verified numerically; see `notebooks/model_derivation.ipynb` for SymPy derivations
