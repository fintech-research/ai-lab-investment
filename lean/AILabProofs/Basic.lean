import Mathlib

set_option linter.style.header false

/-!
# Model primitives

Shared parameter structure for *Investing in Artificial General Intelligence*.

The fields and admissibility hypotheses mirror the calibration in `paper/_appendix.qmd`
(parameter table) and the model setup in `paper/_model.qmd`.  Only the parameters needed
by the formalised closed-form results are included.
-/

namespace AILab

/-- Primitive (exogenous) parameters of the regime-switching investment model.

All quantities are risk-adjusted.  `lam` is the regime-switch arrival rate `λ`,
`α` the revenue elasticity, `σ` the (common) volatility. -/
structure ModelParams where
  r : ℝ        -- discount rate (WACC)
  μL : ℝ       -- L-regime drift
  μH : ℝ       -- H-regime drift
  σ : ℝ        -- volatility
  lam : ℝ      -- regime-switch arrival rate λ
  α : ℝ        -- revenue elasticity
  hσ : 0 < σ
  hlam : 0 < lam
  hα0 : 0 < α
  hα1 : α < 1
  hrμH : μH < r       -- r > μ_H  (finite H-regime present value, 1/(r-μH) > 0)
  hμLH : μL < μH      -- μ_L < μ_H  (H-regime is the optimistic regime)

namespace ModelParams

variable (p : ModelParams)

/-- `r - μ_H > 0`: the H-regime perpetuity is well defined. -/
lemma rμH_pos : 0 < p.r - p.μH := by have := p.hrμH; linarith

/-- `r - μ_L > 0`. -/
lemma rμL_pos : 0 < p.r - p.μL := by
  have := p.hrμH; have := p.hμLH; linarith

/-- `r - μ_L + λ > 0`: the L-regime effective discount rate is positive. -/
lemma rμLlam_pos : 0 < p.r - p.μL + p.lam := by
  have := p.rμL_pos; have := p.hlam; linarith

/-- H-regime present-value multiplier `A_H = 1/(r - μ_H)`. -/
noncomputable def A_H : ℝ := 1 / (p.r - p.μH)

lemma A_H_pos : 0 < p.A_H := div_pos one_pos p.rμH_pos

end ModelParams

end AILab
