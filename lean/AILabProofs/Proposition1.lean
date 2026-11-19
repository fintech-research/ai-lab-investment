import AILabProofs.Basic

set_option linter.style.header false

/-!
# Proposition 1(ii) — trigger and capacity for a payoff linear in demand

This file verifies Steps 1--4 of the Proof of Proposition 1 (`paper/_appendix.qmd`),
the stopping problem with exercise payoff `a K^α X - Θ(K)` and continuation value
`B X^β`:

* `trigger_from_boundary_conditions` : value matching and smooth pasting at the
  trigger imply `X = β/(β-1) · b/A` (Step 1; eq-trigger-H with `A = A_H K^α`).
* `npv_at_trigger` : at that trigger the NPV is `b/(β-1)` (Step 2).
* `hasDerivAt_A_eff_K` : the coefficient `a` drops out of the capacity condition,
  because `a K^α` has elasticity `α` in `K` whatever `a` is (Step 4).
* `K_foc_reduced`, `K_foc` : the capacity first-order condition eq-foc-K is
  equivalent to the closed form for `K^{γ-1}` (eq-K-H).  Positivity of the right-hand
  side under (A2) and global optimality are in `Capacity.lean`.

With `a = A_H` (all capacity in training) this is the post-switch policy of
Proposition 1(ii): `X_H*` and `K_H*`.  With `a = g(φ*)` it is the pure-power
approximation (eq-trigger-phi), whose capacity is therefore `K_H*`.  It is *not* the
pre-switch policy `(X*, K*)` of Proposition 1(iii), whose continuation value is not a
single power and whose capacity depends on `λ` (see `PreSwitch.lean`).  Here `A`
plays the role of the revenue coefficient, `b` of total cost `δK/r + cK^γ`, and `β`
of `β_H > 1`; the results are identities for abstract reals with the stated signs.
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

/-! ## Capacity `K_H*` (Proposition 1(ii), Step 4)

With revenue coefficient `a·K^α`, the capacity first-order condition `∂ln h/∂K = 0`
is `β·(∂ln(aK^α)/∂K) = (β-1)·(∂ln Θ/∂K)`.  Because the revenue-side log-derivative
is `α/K` whatever `a` is, the solution does not depend on `a`: the post-switch
capacity `K_H*` and the capacity of the pure-power approximation coincide and do not
depend on the training fraction.  (The pre-switch capacity `K*` of Proposition 1(iii)
solves a different condition, eq-scale-foc, and does depend on beliefs.) -/

/-- **The revenue-side log-derivative is `α/K`, independent of the coefficient.**
`d/dK [g·K^α] = (α/K)·(g·K^α)`, so the elasticity in `K` is `α` whatever `g` is,
which is why `K_H*` (and the pure-power capacity) does not depend on `φ`. -/
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

/-- **Capacity FOC in closed form** (eq-foc-K, eq-K-H).  The first-order condition
`α β (cK^γ + δK/r) = (β-1) K (cγK^{γ-1} + δ/r)` is equivalent to the closed form
for `K^{γ-1}`, hence `K_H* = (·)^{1/(γ-1)}`, with no dependence on `φ`.  The
equivalence does not by itself say that the right-hand side is positive or that
the root is a maximum; see `capRoot_pos` and `capObj_lt_capObj_KHstar`. -/
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
