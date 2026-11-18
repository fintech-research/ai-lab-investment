import AILabProofs.Proposition2

set_option linter.style.header false

/-!
# Recovery at the optimal allocation (eq-recovery)

This file verifies the closed-form facts about the recovery rule that the paper states
at the optimal allocation (`paper/_model.qmd`, "Equity and debt values", and
`paper/_appendix.qmd`, "Recovery, the shutdown boundary, and fairly priced debt").
Write the effective revenue coefficient at monopoly shares as
`A = w_L((1-φ)K)^α + w_H(φK)^α` and the inference business's coefficient and cost as
`a = w_L((1-φ)K)^α`, `c = (1-φ)·δK/r`.

* `inference_share_iff_foc` : the inference business earns the same revenue per unit
  of capacity as the whole firm, `a = (1-φ)A`, **iff** the interior allocation
  first-order condition `w_H φ^{α-1} = w_L (1-φ)^{α-1}` holds, i.e. iff `φ = φ*`
  (by `alloc_foc_closed_form`).
* `inference_boundary_eq_shutdown` : then the inference business's shutdown boundary
  `X_I = β/(β-1)·c/a` equals the firm's shutdown boundary `β/(β-1)·(δK/r)/A`.
* `inference_value_eq_frac` : and its unlevered value `Λ(X)` is exactly the fraction
  `1-φ` of the firm's unlevered asset value `U(X)` at every demand level.
* `gross_inference_at_boundary_pos_iff` : without the shutdown option, the net value of
  the inference business at the levered boundary, `a X_D - c`, is positive iff the
  coupon exceeds `(1-M)/M` times the operating cost `δK`, `M = β/(β-1)`.

The recovery rule itself (the two caps, the bankruptcy cost) and every recovery level
quoted in the paper are numerical and not formalized.
-/

namespace AILab

open Real

/-- **Equal revenue per unit of capacity iff the allocation FOC holds.**  For
`φ ∈ (0,1)` and `K > 0`, `w_L((1-φ)K)^α = (1-φ)·[w_L((1-φ)K)^α + w_H(φK)^α]` exactly
when `w_H φ^{α-1} = w_L (1-φ)^{α-1}`. -/
theorem inference_share_iff_foc {wL wH α φ K : ℝ} (hφ0 : 0 < φ) (hφ1 : φ < 1) (hK : 0 < K) :
    wL * ((1 - φ) * K) ^ α = (1 - φ) * (wL * ((1 - φ) * K) ^ α + wH * (φ * K) ^ α) ↔
      wH * φ ^ (α - 1) = wL * (1 - φ) ^ (α - 1) := by
  have h1φ : 0 < 1 - φ := by linarith
  have hKα : 0 < K ^ α := Real.rpow_pos_of_pos hK α
  have eφ : φ ^ α = φ ^ (α - 1) * φ := by
    conv_lhs => rw [show α = (α - 1) + 1 by ring]
    rw [Real.rpow_add hφ0, Real.rpow_one]
  have e1φ : (1 - φ) ^ α = (1 - φ) ^ (α - 1) * (1 - φ) := by
    conv_lhs => rw [show α = (α - 1) + 1 by ring]
    rw [Real.rpow_add h1φ, Real.rpow_one]
  rw [Real.mul_rpow h1φ.le hK.le, Real.mul_rpow hφ0.le hK.le, eφ, e1φ]
  have hprod : 0 < φ * (1 - φ) * K ^ α := by positivity
  constructor
  · intro h
    have : (φ * (1 - φ) * K ^ α) * (wH * φ ^ (α - 1) - wL * (1 - φ) ^ (α - 1)) = 0 := by
      linear_combination (-1) * h
    rcases mul_eq_zero.mp this with h0 | h0
    · exact absurd h0 (ne_of_gt hprod)
    · linarith
  · intro h
    linear_combination (-(φ * (1 - φ) * K ^ α)) * h

/-- **The inference business's shutdown boundary equals the firm's** when
`a = (1-φ)A` and `c = (1-φ)·δK/r`. -/
theorem inference_boundary_eq_shutdown {M A δKr φ : ℝ} (hφ1 : φ < 1) (hA : 0 < A) :
    M * ((1 - φ) * δKr) / ((1 - φ) * A) = M * δKr / A := by
  have h1φ : (1 - φ) ≠ 0 := by intro h; linarith
  have := ne_of_gt hA
  field_simp

/-- **`Λ = (1-φ)·U` at the optimal allocation.**  With `a = (1-φ)A`, `c = (1-φ)·δK/r`
and the common boundary `X_S`, the inference business's value
`aX - c + (c - aX_S)(X/X_S)^β` is `1-φ` times the firm's unlevered asset value
`AX - δK/r + (δK/r - AX_S)(X/X_S)^β`. -/
theorem inference_value_eq_frac (A δKr φ XS β X : ℝ) :
    (1 - φ) * A * X - (1 - φ) * δKr + ((1 - φ) * δKr - (1 - φ) * A * XS) * (X / XS) ^ β
      = (1 - φ) * (A * X - δKr + (δKr - A * XS) * (X / XS) ^ β) := by
  ring

/-- **Gross inference value at the levered boundary.**  At the optimal allocation
(`a = (1-φ)A`, `c = (1-φ)δK/r`) and the boundary `X_D = M (C_D + δK)/r / A`, the net
inference value without the shutdown option, `a X_D - c`, is positive iff
`C_D > (1-M)/M · δK`.  At baseline `M = β_L⁻/(β_L⁻ - 1) ≈ 0.70`, so the threshold
is about `0.43·δK`. -/
theorem gross_inference_at_boundary_pos_iff {M A CD δK r φ : ℝ} (hM : 0 < M) (hA : 0 < A)
    (hr : 0 < r) (hφ1 : φ < 1) :
    0 < (1 - φ) * A * (M * ((CD + δK) / r) / A) - (1 - φ) * (δK / r) ↔
      (1 - M) / M * δK < CD := by
  have h1φ : 0 < 1 - φ := by linarith
  have e : (1 - φ) * A * (M * ((CD + δK) / r) / A) - (1 - φ) * (δK / r)
      = (1 - φ) / r * (M * CD - (1 - M) * δK) := by
    field_simp
    ring
  rw [e, mul_pos_iff_of_pos_left (div_pos h1φ hr), sub_pos, div_mul_eq_mul_div,
    div_lt_iff₀ hM]
  constructor <;> intro h <;> linarith

end AILab
