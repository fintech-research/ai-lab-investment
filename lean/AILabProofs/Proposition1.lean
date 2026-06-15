import AILabProofs.Basic

set_option linter.style.header false

/-!
# Proposition 1 — optimal investment trigger (closed form)

This file verifies the algebraic heart of Proposition 1 (`paper/_appendix.qmd`,
"Proof of Proposition 1", Steps 1–2, and `paper/_model.qmd` eq-trigger-phi):

* `trigger_from_boundary_conditions` : the value-matching and smooth-pasting
  conditions at the investment trigger imply the closed form
  `X* = β/(β-1) · b / A`, where `A = A_eff` is the effective revenue coefficient
  and `b` is total cost.
* `npv_at_trigger` : at that trigger the net present value equals `b/(β-1)`
  (Step 2: "the NPV at the trigger is `V - I = b(K)/(β_H - 1)`").

Here `A` plays the role of `A_eff`, `b` the role of total cost `δK/r + cK^γ`,
and `β` the role of the positive characteristic root `β_H > 1`.  The result is a
pure-algebra identity, so it is stated for abstract reals with the relevant signs.
-/

namespace AILab

open Real

/-- **Trigger from the boundary conditions.**
At the investment trigger `X`, the firm's option value is `C · X^β` and its
exercised value net of cost is the linear payoff `A · X - b`.  Value-matching
(`vm`) equates the two; smooth-pasting (`sp`) equates their first derivatives in
`X` (the derivative of `C·X^β` being `C·β·X^(β-1)`).  Together they pin down the
trigger in closed form. -/
theorem trigger_from_boundary_conditions
    {β A b X C : ℝ} (hβ : 1 < β) (hA : 0 < A) (hX : 0 < X)
    (vm : A * X - b = C * X ^ β)
    (sp : A = C * β * X ^ (β - 1)) :
    X = β / (β - 1) * b / A := by
  have hβ0 : (0 : ℝ) < β := lt_trans one_pos hβ
  have hβne : β ≠ 0 := ne_of_gt hβ0
  have hβ1 : β - 1 ≠ 0 := by linarith
  have hAne : A ≠ 0 := ne_of_gt hA
  -- `X^β = X^(β-1) · X`
  have hpow : X ^ β = X ^ (β - 1) * X := by
    conv_lhs => rw [show β = (β - 1) + 1 by ring]
    rw [Real.rpow_add hX, Real.rpow_one]
  -- smooth-pasting gives `C · X^(β-1) = A/β`
  have key : C * X ^ (β - 1) = A / β := by
    rw [eq_div_iff hβne]; linear_combination -sp
  -- substitute into value-matching: `A·X - b = (A/β)·X`
  have vm' : A * X - b = A / β * X := by
    rw [vm, hpow, ← mul_assoc, key]
  -- solve the resulting linear equation for `X`
  field_simp at vm' ⊢
  linear_combination vm'

/-- **NPV at the trigger.**  Given the closed-form trigger, the net present value
of investing, `A·X - b`, equals `b/(β-1)` (Proposition 1, Step 2). -/
theorem npv_at_trigger
    {β A b X : ℝ} (hβ : 1 < β) (hA : A ≠ 0)
    (hX : X = β / (β - 1) * b / A) :
    A * X - b = b / (β - 1) := by
  have hβ1 : β - 1 ≠ 0 := ne_of_gt (by linarith : (0:ℝ) < β - 1)
  subst hX
  field_simp
  ring

/-! ## Optimal capacity `K*` (Proposition 1, Step 4)

With `A_eff = g(φ)·K^α`, the capacity first-order condition `∂ln h/∂K = 0` is
`β_H·(∂ln A_eff/∂K) = (β_H-1)·(∂ln b/∂K)`.  Because the `A_eff`-side log-derivative
is `α/K` regardless of `g(φ)`, the optimal `K*` is independent of the training
fraction `φ` — the key claim of Step 4. -/

/-- **The `A_eff`-side log-derivative is `α/K`, independent of `g(φ)`.**
`d/dK [g·K^α] = (α/K)·(g·K^α)`, so the elasticity of `A_eff` in `K` is `α` whatever
`g(φ)` is — which is why `K*` does not depend on `φ`. -/
theorem hasDerivAt_A_eff_K {g α K : ℝ} (hK : 0 < K) :
    HasDerivAt (fun x => g * x ^ α) (α / K * (g * K ^ α)) K := by
  have h : HasDerivAt (fun x => g * x ^ α) (g * (1 * α * K ^ (α - 1))) K :=
    ((hasDerivAt_id K).rpow_const (Or.inl (ne_of_gt hK))).const_mul g
  have hpow : K ^ α = K ^ (α - 1) * K := by
    conv_lhs => rw [show α = (α - 1) + 1 by ring]
    rw [Real.rpow_add hK, Real.rpow_one]
  have hEq : α / K * (g * K ^ α) = g * (1 * α * K ^ (α - 1)) := by
    rw [hpow]; field_simp
  rw [hEq]; exact h

/-- **Reduced capacity FOC, solved in closed form.**  After cancelling the common
`K` factor, the FOC is linear in `u = K^{γ-1}` and solves to an explicit value
depending only on cost/technology parameters `(α, β, γ, δ, r, c)`. -/
theorem K_foc_reduced {c δ r γ β α u : ℝ}
    (_hr : 0 < r) (hc : 0 < c) (hden : α * β - (β - 1) * γ ≠ 0) :
    α * β * (c * u + δ / r) = (β - 1) * (c * γ * u + δ / r) ↔
      u = δ / r * ((β - 1) - α * β) / (c * (α * β - (β - 1) * γ)) := by
  rw [eq_div_iff (mul_ne_zero (ne_of_gt hc) hden)]
  constructor <;> intro h <;> linear_combination h

/-- **Capacity FOC in closed form.**  The full first-order condition
`α β (cK^γ + δK/r) = (β-1) K (cγK^{γ-1} + δ/r)` is equivalent to the closed form
for `K^{γ-1}` — hence `K* = (·)^{1/(γ-1)}`, with no dependence on `φ`. -/
theorem K_foc {c δ r γ β α K : ℝ}
    (hK : 0 < K) (hr : 0 < r) (hc : 0 < c) (hden : α * β - (β - 1) * γ ≠ 0) :
    α * β * (c * K ^ γ + δ * K / r) = (β - 1) * K * (c * γ * K ^ (γ - 1) + δ / r) ↔
      K ^ (γ - 1) = δ / r * ((β - 1) - α * β) / (c * (α * β - (β - 1) * γ)) := by
  have hpow : K ^ γ = K ^ (γ - 1) * K := by
    conv_lhs => rw [show γ = (γ - 1) + 1 by ring]
    rw [Real.rpow_add hK, Real.rpow_one]
  rw [hpow, ← K_foc_reduced hr hc hden]
  constructor <;> intro h
  · apply mul_left_cancel₀ (ne_of_gt hK); linear_combination h
  · linear_combination K * h

end AILab
