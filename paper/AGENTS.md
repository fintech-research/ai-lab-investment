# AGENTS.md — paper/

Rules for working in the `paper/` directory. Global rules are in `@../AGENTS.md`.

## Writing Style

- **No bold paragraph headings in the main body.** In `_introduction.qmd`, `_calibration.qmd`, `_valuation.qmd`, `_discussion.qmd`, and `_conclusion.qmd`, `**Bold text.**` as a pseudo-heading is forbidden — use `###`/`####` for subdivisions, or just start the paragraph. Run-in bold labels *are* the established convention in `_model.qmd`'s preemption-equilibrium derivation and throughout `_appendix.qmd` (proof steps, verification blocks, robustness exercises); match the surrounding file there rather than converting them.
- Concise, formal prose. Top finance/management journal style (current target ladder starts at Management Science; see `../submission/README.md`). No filler.
- Equations: use Quarto cross-references `@eq-name`, figures `@fig-name`, tables `@tbl-name`.

## Paper Structure

Main entry: `index.qmd` (includes all sections, then references, then `_appendix.qmd`). Sections: `_introduction.qmd` (which itself includes `_literature.qmd`), `_model.qmd`, `_calibration.qmd`, `_valuation.qmd`, `_discussion.qmd`, `_conclusion.qmd`, `_appendix.qmd`. Bibliography: `references.bib`; style files `econometrica.bst`, `title.tex`, `keywords.tex`; render config `_quarto.yaml`.

`_appendix.qmd` is the **Internet Appendix** — always refer to it that way in prose ("Internet Appendix A", not "Appendix A"). Its sections: A. Proofs (Propositions 1–3 plus Numerical Finding 1, Dario's dilemma) and the result-taxonomy table; B. Numerical Verification Methods; C. Calibration Details and Data Sources; D. Parameter Sensitivity; E. Robustness (parameter sensitivity, Cournot discussion + quantified fixed-pie contest, dynamic φ reallocation, duopoly Dario's dilemma, alternative regime structure).

Results are labeled by method: Propositions 1–3 for analytical results, **Numerical Finding 1** for Dario's dilemma. Do not promote a numerical finding to a proposition; `@tbl-result-taxonomy` in Internet Appendix A records the analytical status of each result and must stay in sync.

## Proof Verification

The closed-form algebra of Propositions 1–3 is machine-checked in Lean 4/Mathlib (`../lean/`), and Internet Appendix A opens with a paragraph describing exactly what is and is not formalized. If you change a closed form, a first-order condition, or a comparative static, check whether the corresponding Lean theorem and that scope paragraph need updating (`lean/README.md` maps theorems to paper results).

## IMPORTANT: Figures

- All figures are PDFs in `paper/figures/` (one PDF + one PNG per figure, 11 total; 10 are referenced in the paper — `fig_sample_paths` is used in the slides only).
- Figure logic lives in `src/ai_lab_investment/figures/paper.py` — **never** in `generate_figures.py`.
- To update a figure: edit the `create_*` function in `paper.py`, then run `uv run python paper/generate_figures.py`.
- Do not add model code to `generate_figures.py`. It is a thin wrapper only.

## Key Model Facts (for editing proofs/text)

- Baseline: r=0.12, μ_L=0.01, μ_H=0.06, σ=0.25, λ=0.10, α=0.40, γ=1.50, δ=0.03
- β_L⁺ ≈ 3.01, β_H ≈ 1.55 (positive characteristic roots)
- Assumption A3: (1−1/β_L⁺)/α ≈ 1.67 ≥ 1 → simplified F_L = C·X^{β_H} valid at baseline
- φ̲ ≈ 0.18 (faith-based survival threshold, A_eff-channel), R ≈ 0.22; exact net threshold φ̃ ≈ 0.32 (both channels, eq-phi-tilde, λ-dependent); φ*(λ) > φ̃(λ) iff λ ≳ 0.034 at baseline
- Baseline results: X* ≈ 0.0047, K* ≈ 0.0067, φ* ≈ 0.70 (single-firm); X_F ≈ 0.12, K_F ≈ 0.26, X_P ≈ 0.0027, X_L^mono = X* ≈ 0.0047, preemption discount X_P/X_L^mono ≈ 0.57 (duopoly, ℓ=0); φ is role-invariant (φ_L = φ_F = φ*)
- Credit risk: spreads ≈0/12/41/97 bps at ℓ=0.05/0.20/0.40/0.70 (benchmark = r; recovery = inference liquidation value capped at c_D/r); 5-yr default (first-passage, L-regime drift) 0.63%/1.80%/4.85%/12.98% (evaluated at fixed X=0.10, K=1, φ=0.5)
- Option value is increasing but CONCAVE in λ over the policy range [0.1, 0.5] (convex only for λ ≲ 0.08) — the news-asymmetry prediction is that bad timeline news moves valuations more than good news
- All results verified numerically; see `notebooks/model_derivation.ipynb` for SymPy derivations
