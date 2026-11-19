import AILabProofs.EulerODE

set_option linter.style.header false

/-!
# Proposition 1(iii) — the pre-switch policy: ODE pieces and first-order conditions

This file verifies the closed-form ingredients of the pre-switch problem with the
post-switch scale precommitted (`paper/_model.qmd`, eq-particular-C,
eq-option-L-upper, eq-scale-foc; `paper/_appendix.qmd`, Proof of Proposition 1,
Step 7, eq-premium, and the remark on the pure-power form).

* `particular_power_iff` : `Γ X^{β_H}` solves the forced L-regime equation
  `½σ²X²F'' + μ_L X F' - (r+λ)F + λ B_H X^{β_H} = 0` iff `Γ = -λB_H/Q_L(β_H)`
  (eq-particular-C).
* `charPoly_L_at_H_root`, `charPoly_L_at_H_root_neg`, `particular_coeff_pos` :
  `Q_L(β_H) = (μ_L-μ_H)β_H - λ < 0`, so `Γ > 0` when `B_H > 0`.
* `particular_affine` : with the affine forcing `λ(p_H X - q_H)` above `X_H*`, the
  particular solution is `λp_H/(r+λ-μ_L)·X - λq_H/(r+λ)` (eq-option-L-upper).
* `premium_value_matching`, `hasDerivAt_premium_coeff`, `premium_foc_iff` : for the
  policy "invest at `X̄`", eq-premium matches value at `X̄` by construction, and the
  first-order condition of the coefficient `[P(X̄) - S(X̄)]X̄^{-β}` in `X̄` is the
  smooth-pasting condition `X̄(P' - S') = β(P - S)`.
* `hasDerivAt_payoff_K`, `scale_foc_iff` : the first-order condition of the exercise
  payoff `g K^α X - (cK^γ + δK/r)` in `K` is the scale condition eq-scale-foc.

Not formalized: that the solution of the homogeneous equation vanishing at the origin
is a multiple of `X^{β_L^+}` (ODE uniqueness), the value and slope matching at `X_H*`
that pin down `(A_1, G_1, G_2)`, the existence or uniqueness of a solution of the
two-region system, and the optimality of the policy it describes.
-/

namespace AILab

open Real

/-- **The power particular solution** (eq-particular-C).  For `X > 0`, `Γ X^β`
satisfies the L-regime equation with forcing `λ B X^β` exactly when
`Γ Q_L(β) + λ B = 0`, `Q_L = charPoly σ μ_L (r+λ)`. -/
theorem particular_power_iff {σ μL r lam β B Γ X : ℝ} (hX : 0 < X) :
    σ ^ 2 / 2 * X ^ 2 * (Γ * (β * (β - 1) * X ^ (β - 2))) + μL * X * (Γ * (β * X ^ (β - 1)))
        - (r + lam) * (Γ * X ^ β) + lam * B * X ^ β = 0
      ↔ Γ * charPoly σ μL (r + lam) β + lam * B = 0 := by
  have h := euler_operator_rpow (σ := σ) (μ := μL) (ρ := r + lam) (β := β) hX
  have e : σ ^ 2 / 2 * X ^ 2 * (Γ * (β * (β - 1) * X ^ (β - 2)))
        + μL * X * (Γ * (β * X ^ (β - 1))) - (r + lam) * (Γ * X ^ β) + lam * B * X ^ β
      = X ^ β * (Γ * charPoly σ μL (r + lam) β + lam * B) := by
    linear_combination Γ * h
  rw [e, mul_eq_zero, or_iff_right (ne_of_gt (Real.rpow_pos_of_pos hX β))]

/-- **`Q_L` at an H-regime root.**  If `Q_H(β) = 0` then
`Q_L(β) = (μ_L - μ_H)β - λ`. -/
theorem charPoly_L_at_H_root {σ μL μH r lam β : ℝ} (hβ : charPoly σ μH r β = 0) :
    charPoly σ μL (r + lam) β = (μL - μH) * β - lam := by
  have : charPoly σ μL (r + lam) β = charPoly σ μH r β + ((μL - μH) * β - lam) := by
    simp only [charPoly]; ring
  rw [this, hβ, zero_add]

/-- **`Q_L(β_H) < 0`** for `β_H > 0`, `μ_L < μ_H`, `λ > 0`. -/
theorem charPoly_L_at_H_root_neg {σ μL μH r lam β : ℝ} (hβ : charPoly σ μH r β = 0)
    (hβpos : 0 < β) (hμ : μL < μH) (hlam : 0 < lam) :
    charPoly σ μL (r + lam) β < 0 := by
  rw [charPoly_L_at_H_root hβ]
  nlinarith

/-- **`Γ = -λB_H/Q_L(β_H) > 0`** when `B_H > 0`. -/
theorem particular_coeff_pos {σ μL μH r lam β B : ℝ} (hβ : charPoly σ μH r β = 0)
    (hβpos : 0 < β) (hμ : μL < μH) (hlam : 0 < lam) (hB : 0 < B) :
    0 < -lam * B / charPoly σ μL (r + lam) β :=
  div_pos_of_neg_of_neg (by nlinarith) (charPoly_L_at_H_root_neg hβ hβpos hμ hlam)

/-- **The affine particular solution above `X_H*`** (eq-option-L-upper).  With
`k = λp/(r+λ-μ_L)` and `m = λq/(r+λ)`, `F(X) = kX - m` (for which `F'' = 0`) satisfies
`μ_L X F' - (r+λ)F + λ(pX - q) = 0` at every `X`. -/
theorem particular_affine {μL r lam p q X : ℝ} (h1 : r + lam - μL ≠ 0) (h2 : r + lam ≠ 0) :
    μL * X * (lam * p / (r + lam - μL))
        - (r + lam) * (lam * p / (r + lam - μL) * X - lam * q / (r + lam))
        + lam * (p * X - q) = 0 := by
  field_simp
  ring

/-- **Value matching of eq-premium at the trigger:** `S(X̄) + [P - S](X̄/X̄)^β = P`. -/
theorem premium_value_matching {P S Xb β : ℝ} (hXb : 0 < Xb) :
    S + (P - S) * (Xb / Xb) ^ β = P := by
  rw [div_self (ne_of_gt hXb), Real.one_rpow]; ring

/-- **Derivative of the premium coefficient in the trigger.**  If `P` and `S` have
derivatives `P'`, `S'` at `x > 0`, then `x ↦ [P(x) - S(x)] x^{-β}` has derivative
`x^{-β-1}·(x(P' - S') - β(P(x) - S(x)))`. -/
theorem hasDerivAt_premium_coeff {P S : ℝ → ℝ} {P' S' β x : ℝ} (hx : 0 < x)
    (hP : HasDerivAt P P' x) (hS : HasDerivAt S S' x) :
    HasDerivAt (fun y => (P y - S y) * y ^ (-β))
      (x ^ (-β - 1) * (x * (P' - S') - β * (P x - S x))) x := by
  have hpow : HasDerivAt (fun y => y ^ (-β)) (-β * x ^ (-β - 1)) x :=
    hasDerivAt_rpow_const (Or.inl (ne_of_gt hx))
  have h := (hP.sub hS).mul hpow
  refine h.congr_deriv ?_
  have e : x ^ (-β) = x ^ (-β - 1) * x := by
    conv_lhs => rw [show -β = (-β - 1) + 1 by ring]
    rw [Real.rpow_add hx, Real.rpow_one]
  rw [e]
  simp only [Pi.sub_apply]
  ring

/-- **The trigger first-order condition is smooth pasting.**  The derivative of the
premium coefficient vanishes at `x > 0` iff `x(P' - S') = β(P(x) - S(x))`. -/
theorem premium_foc_iff {P' S' β x Px Sx : ℝ} (hx : 0 < x) :
    x ^ (-β - 1) * (x * (P' - S') - β * (Px - Sx)) = 0 ↔ x * (P' - S') = β * (Px - Sx) := by
  rw [mul_eq_zero, or_iff_right (ne_of_gt (Real.rpow_pos_of_pos hx _)), sub_eq_zero]

/-- **Derivative of the exercise payoff in capacity:**
`∂/∂K [gK^αX - (cK^γ + δK/r)] = αgK^{α-1}X - (cγK^{γ-1} + δ/r)`. -/
theorem hasDerivAt_payoff_K {g α X c γ δ r K : ℝ} (hK : 0 < K) :
    HasDerivAt (fun k => g * k ^ α * X - (c * k ^ γ + δ * k / r))
      (α * g * K ^ (α - 1) * X - (c * γ * K ^ (γ - 1) + δ / r)) K := by
  have h1 : HasDerivAt (fun k => k ^ α) (α * K ^ (α - 1)) K :=
    hasDerivAt_rpow_const (Or.inl (ne_of_gt hK))
  have h2 : HasDerivAt (fun k => k ^ γ) (γ * K ^ (γ - 1)) K :=
    hasDerivAt_rpow_const (Or.inl (ne_of_gt hK))
  have h3 : HasDerivAt (fun k => δ * k / r) (δ * 1 / r) K :=
    ((hasDerivAt_id K).const_mul δ).div_const r
  have h := ((h1.const_mul g).mul_const X).sub ((h2.const_mul c).add h3)
  refine h.congr_deriv ?_
  ring

/-- **The scale condition** (eq-scale-foc).  For `K > 0`, the capacity first-order
condition of the exercise payoff holds iff `α (gK^α) X = K(δ/r + cγK^{γ-1})`. -/
theorem scale_foc_iff {g α X c γ δ r K : ℝ} (hK : 0 < K) :
    α * g * K ^ (α - 1) * X - (c * γ * K ^ (γ - 1) + δ / r) = 0 ↔
      α * (g * K ^ α) * X = K * (δ / r + c * γ * K ^ (γ - 1)) := by
  have e : K ^ α = K ^ (α - 1) * K := by
    conv_lhs => rw [show α = (α - 1) + 1 by ring]
    rw [Real.rpow_add hK, Real.rpow_one]
  rw [e]
  constructor
  · intro h; linear_combination K * h
  · intro h
    have : K * (α * g * K ^ (α - 1) * X - (c * γ * K ^ (γ - 1) + δ / r)) = 0 := by
      linear_combination h
    rcases mul_eq_zero.mp this with h0 | h0
    · exact absurd h0 (ne_of_gt hK)
    · exact h0

end AILab
