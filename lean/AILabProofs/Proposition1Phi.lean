import AILabProofs.Basic

set_option linter.style.header false

/-!
# Proposition 1 — optimal training fraction `φ*`

This file verifies Proposition 1's allocation result (`paper/_appendix.qmd`,
"Proof of Proposition 1", Step 5, and `paper/_model.qmd`).  Factoring `K^α` out of
the effective revenue coefficient, the firm chooses `φ` to maximise

`g(φ) = w_L (1-φ)^α + w_H φ^α`,   `w_L, w_H > 0`,  `α ∈ (0,1)`,

where `w_L = 1/(r-μ_L+λ)` and `w_H = λ A_H/(r-μ_L+λ)`.

* `hasDerivAt_alloc` : `g'(φ) = α (w_H φ^{α-1} - w_L (1-φ)^{α-1})`, the first
  derivative used to derive the first-order condition.
* `alloc_foc_ratio` : the interior FOC `g'(φ) = 0` is equivalent to the ratio
  condition `(φ/(1-φ))^{1-α} = w_H/w_L`.
* `ratio_eq_closed_form` : that ratio condition pins `φ` to the explicit value
  `ρ/(1+ρ)` with `ρ = (w_H/w_L)^{1/(1-α)}` — establishing the unique interior
  critical point `φ*`.
* `alloc_foc_closed_form` : the two combined — the closed form for `φ*`.
-/

namespace AILab

open Real

/-- **First derivative of the allocation objective.**
`d/dφ [w_L (1-φ)^α + w_H φ^α] = α (w_H φ^{α-1} - w_L (1-φ)^{α-1})`. -/
theorem hasDerivAt_alloc {wL wH α φ : ℝ} (hφ0 : 0 < φ) (hφ1 : φ < 1) :
    HasDerivAt (fun x => wL * (1 - x) ^ α + wH * x ^ α)
      (α * (wH * φ ^ (α - 1) - wL * (1 - φ) ^ (α - 1))) φ := by
  have h1mφ : (0 : ℝ) < 1 - φ := by linarith
  have hd1 : HasDerivAt (fun x => 1 - x) (-1 : ℝ) φ :=
    (hasDerivAt_id φ).const_sub 1
  have ht1 : HasDerivAt (fun x => wL * (1 - x) ^ α)
      (wL * (-1 * α * (1 - φ) ^ (α - 1))) φ :=
    (hd1.rpow_const (Or.inl (ne_of_gt h1mφ))).const_mul wL
  have ht2 : HasDerivAt (fun x => wH * x ^ α)
      (wH * (1 * α * φ ^ (α - 1))) φ :=
    ((hasDerivAt_id φ).rpow_const (Or.inl (ne_of_gt hφ0))).const_mul wH
  have hD : α * (wH * φ ^ (α - 1) - wL * (1 - φ) ^ (α - 1))
      = wL * (-1 * α * (1 - φ) ^ (α - 1)) + wH * (1 * α * φ ^ (α - 1)) := by ring
  rw [hD]
  exact ht1.add ht2

/-- **Interior first-order condition in ratio form.**  `g'(φ) = 0` holds exactly
when `(φ/(1-φ))^{1-α} = w_H/w_L`. -/
theorem alloc_foc_ratio {wL wH α φ : ℝ}
    (hφ0 : 0 < φ) (hφ1 : φ < 1) (hα0 : 0 < α) (hwL : 0 < wL) (_hwH : 0 < wH) :
    α * (wH * φ ^ (α - 1) - wL * (1 - φ) ^ (α - 1)) = 0 ↔
      (φ / (1 - φ)) ^ (1 - α) = wH / wL := by
  have h1mφ : (0 : ℝ) < 1 - φ := by linarith
  have hA0 : 0 < φ ^ (1 - α) := Real.rpow_pos_of_pos hφ0 _
  have hB0 : 0 < (1 - φ) ^ (1 - α) := Real.rpow_pos_of_pos h1mφ _
  have hPe : φ ^ (α - 1) = (φ ^ (1 - α))⁻¹ := by
    rw [← Real.rpow_neg hφ0.le]; congr 1; ring
  have hQe : (1 - φ) ^ (α - 1) = ((1 - φ) ^ (1 - α))⁻¹ := by
    rw [← Real.rpow_neg h1mφ.le]; congr 1; ring
  rw [hPe, hQe, Real.div_rpow hφ0.le h1mφ.le, mul_eq_zero,
      or_iff_right (ne_of_gt hα0), sub_eq_zero]
  simp only [← div_eq_mul_inv]
  rw [div_eq_div_iff (ne_of_gt hA0) (ne_of_gt hB0),
      div_eq_div_iff (ne_of_gt hB0) (ne_of_gt hwL)]
  constructor <;> intro h <;> linear_combination -h

/-- **Ratio condition pins the unique interior allocation.**  For `β = 1-α > 0`
and `t = w_H/w_L > 0`, the condition `(φ/(1-φ))^β = t` holds exactly at
`φ = ρ/(1+ρ)`, `ρ = t^{1/β}`.  Monotonicity makes this the *unique* solution. -/
theorem ratio_eq_closed_form {φ β t : ℝ}
    (hφ0 : 0 < φ) (hφ1 : φ < 1) (hβ : 0 < β) (ht : 0 < t) :
    (φ / (1 - φ)) ^ β = t ↔ φ = t ^ (1 / β) / (1 + t ^ (1 / β)) := by
  set R := t ^ (1 / β) with hRdef
  have hR : 0 < R := Real.rpow_pos_of_pos ht _
  have h1mφ : 0 < 1 - φ := by linarith
  have hg : 0 < φ / (1 - φ) := div_pos hφ0 h1mφ
  have hRβ : R ^ β = t := by
    rw [hRdef, ← Real.rpow_mul ht.le, one_div, inv_mul_cancel₀ (ne_of_gt hβ), Real.rpow_one]
  have step1 : (φ / (1 - φ)) ^ β = t ↔ φ / (1 - φ) = R := by
    rw [← hRβ]
    constructor
    · intro h
      rcases lt_trichotomy (φ / (1 - φ)) R with hlt | heq | hgt
      · exact absurd h (ne_of_lt (Real.rpow_lt_rpow hg.le hlt hβ))
      · exact heq
      · exact absurd h (ne_of_gt (Real.rpow_lt_rpow hR.le hgt hβ))
    · intro h; rw [h]
  rw [step1, div_eq_iff (ne_of_gt h1mφ), eq_div_iff (by linarith : (1 + R) ≠ 0)]
  constructor <;> intro h <;> nlinarith [h]

/-- **Closed form for the optimal training fraction `φ*`.**  The interior FOC
holds exactly at `φ* = ρ/(1+ρ)` with `ρ = (w_H/w_L)^{1/(1-α)}`. -/
theorem alloc_foc_closed_form {wL wH α φ : ℝ}
    (hφ0 : 0 < φ) (hφ1 : φ < 1) (hα0 : 0 < α) (hα1 : α < 1)
    (hwL : 0 < wL) (hwH : 0 < wH) :
    α * (wH * φ ^ (α - 1) - wL * (1 - φ) ^ (α - 1)) = 0 ↔
      φ = (wH / wL) ^ (1 / (1 - α)) / (1 + (wH / wL) ^ (1 / (1 - α))) :=
  (alloc_foc_ratio hφ0 hφ1 hα0 hwL hwH).trans
    (ratio_eq_closed_form hφ0 hφ1 (by linarith) (div_pos hwH hwL))

/-! ## Comparative statics of `φ*` (Proposition 1, Step 6)

`φ*` is the closed form `t^{1/β}/(1 + t^{1/β})` with `β = 1-α > 0` and revenue
ratio `t = w_H/w_L`.  The map is strictly increasing in `t`, and `t = λ/(r-μ_H)`
(independent of `μ_L`).  Hence `φ*` rises with optimism `λ` and with the H-regime
growth rate `μ_H`, and is independent of `μ_L`. -/

/-- The optimal training fraction as a function of the revenue ratio `t`. -/
noncomputable def phiStar (β t : ℝ) : ℝ := t ^ (1 / β) / (1 + t ^ (1 / β))

/-- `φ*` is strictly increasing in the revenue ratio `t = w_H/w_L`. -/
theorem phiStar_lt_phiStar {β t₁ t₂ : ℝ} (hβ : 0 < β) (ht₁ : 0 < t₁) (ht : t₁ < t₂) :
    phiStar β t₁ < phiStar β t₂ := by
  have hR₁ : 0 < t₁ ^ (1 / β) := Real.rpow_pos_of_pos ht₁ _
  have hR₂ : 0 < t₂ ^ (1 / β) := Real.rpow_pos_of_pos (lt_trans ht₁ ht) _
  have hRlt : t₁ ^ (1 / β) < t₂ ^ (1 / β) :=
    Real.rpow_lt_rpow ht₁.le ht (div_pos one_pos hβ)
  rw [phiStar, phiStar, div_lt_div_iff₀ (by linarith) (by linarith)]
  nlinarith [hRlt, hR₁, hR₂]

/-- **The revenue ratio is `λ/(r-μ_H)`, independent of `μ_L`.**  Writing
`w_L = 1/(r-μ_L+λ)` and `w_H = λ/((r-μ_H)(r-μ_L+λ))`, the common factor cancels.
This is why `φ*` does not depend on `μ_L` (Proposition 1(ii)). -/
theorem weight_ratio {r μL μH lam : ℝ}
    (hd : r - μL + lam ≠ 0) (hH : r - μH ≠ 0) :
    lam / ((r - μH) * (r - μL + lam)) / (1 / (r - μL + lam)) = lam / (r - μH) := by
  field_simp

/-- **`φ*` is increasing in optimism `λ`** (Proposition 1(i)). -/
theorem phiStar_increasing_lam {r μH β lam₁ lam₂ : ℝ}
    (hβ : 0 < β) (hH : 0 < r - μH) (hlam₁ : 0 < lam₁) (hlt : lam₁ < lam₂) :
    phiStar β (lam₁ / (r - μH)) < phiStar β (lam₂ / (r - μH)) :=
  phiStar_lt_phiStar hβ (div_pos hlam₁ hH) (by gcongr)

/-- **`φ*` is increasing in the H-regime growth rate `μ_H`** (Proposition 1(ii)). -/
theorem phiStar_increasing_muH {r β lam μH₁ μH₂ : ℝ}
    (hβ : 0 < β) (hlam : 0 < lam) (hH₂ : 0 < r - μH₂) (hlt : μH₁ < μH₂) :
    phiStar β (lam / (r - μH₁)) < phiStar β (lam / (r - μH₂)) :=
  phiStar_lt_phiStar hβ (div_pos hlam (by linarith))
    (by gcongr)

end AILab
