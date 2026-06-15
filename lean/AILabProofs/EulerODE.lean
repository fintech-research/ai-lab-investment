import AILabProofs.CharacteristicRoots

set_option linter.style.header false

/-!
# The Euler ODE and the characteristic equation

The option value in each regime solves the Cauchy–Euler ODE

`L[F](X) = ½σ²X² F''(X) + μ X F'(X) - ρ F(X) = 0`

(`paper/_model.qmd`, eq-hjb-L specialised to the homogeneous part).  Substituting
the trial power solution `F(X) = X^β` reduces the ODE to the *characteristic
equation* `Q(β) = ½σ²β(β-1) + μβ - ρ = 0` (`charPoly`, eq-beta-H).

This file makes that reduction kernel-checked: it computes `F'` and `F''` as
genuine derivatives and shows the differential operator applied to `X^β` factors
as `X^β · Q(β)`.  This is the step the SymPy derivation notebook checks
symbolically (`notebooks/model_derivation.ipynb`); here it is verified by Lean.
It closes the gap between "`β` is a root of the quadratic `Q`" and "`X^β` actually
solves the ODE."
-/

namespace AILab

open Real

/-- First derivative `F'(X) = β X^{β-1}` for `F(X) = X^β`. -/
theorem hasDerivAt_rpow_fst {β X : ℝ} (hX : X ≠ 0) :
    HasDerivAt (fun x => x ^ β) (β * X ^ (β - 1)) X :=
  hasDerivAt_rpow_const (Or.inl hX)

/-- Second derivative `F''(X) = β(β-1) X^{β-2}` (the derivative of `F'`). -/
theorem hasDerivAt_rpow_snd {β X : ℝ} (hX : X ≠ 0) :
    HasDerivAt (fun x => β * x ^ (β - 1)) (β * ((β - 1) * X ^ (β - 2))) X := by
  have h2 : HasDerivAt (fun x => x ^ (β - 1)) ((β - 1) * X ^ (β - 1 - 1)) X :=
    hasDerivAt_rpow_const (Or.inl hX)
  have h3 := h2.const_mul β
  rwa [show (β - 1 - 1 : ℝ) = β - 2 by ring] at h3

/-- **The Euler operator applied to `X^β` factors through the characteristic
polynomial:** `½σ²X²·β(β-1)X^{β-2} + μX·βX^{β-1} - ρX^β = X^β · Q(β)`. -/
theorem euler_operator_rpow {σ μ ρ β X : ℝ} (hX : 0 < X) :
    σ ^ 2 / 2 * X ^ 2 * (β * (β - 1) * X ^ (β - 2)) + μ * X * (β * X ^ (β - 1)) - ρ * X ^ β
      = X ^ β * charPoly σ μ ρ β := by
  have e1 : X * X ^ (β - 1) = X ^ β := by
    conv_rhs => rw [show β = 1 + (β - 1) by ring]
    rw [Real.rpow_add hX, Real.rpow_one]
  have e1' : X * X ^ (β - 2) = X ^ (β - 1) := by
    conv_rhs => rw [show β - 1 = 1 + (β - 2) by ring]
    rw [Real.rpow_add hX, Real.rpow_one]
  have e2 : X ^ 2 * X ^ (β - 2) = X ^ β := by
    rw [pow_two, mul_assoc, e1', e1]
  simp only [charPoly]
  linear_combination (σ ^ 2 / 2 * β * (β - 1)) * e2 + (μ * β) * e1

/-- **`X^β` solves the homogeneous Euler ODE if and only if `β` is a characteristic
root** (`Q(β) = 0`).  This is the precise sense in which the characteristic
equation governs the option value, with the boundary `X > 0`. -/
theorem rpow_solves_euler_iff {σ μ ρ β X : ℝ} (hX : 0 < X) :
    σ ^ 2 / 2 * X ^ 2 * (β * (β - 1) * X ^ (β - 2)) + μ * X * (β * X ^ (β - 1)) - ρ * X ^ β = 0
      ↔ charPoly σ μ ρ β = 0 := by
  rw [euler_operator_rpow hX, mul_eq_zero,
    or_iff_right (ne_of_gt (Real.rpow_pos_of_pos hX β))]

end AILab
