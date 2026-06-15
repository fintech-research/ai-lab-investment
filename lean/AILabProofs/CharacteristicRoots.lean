import AILabProofs.Basic

set_option linter.style.header false

/-!
# Characteristic roots of the regime ODE

The option value `X^β` solves an Euler ODE whose exponent `β` satisfies the
quadratic characteristic equation (`paper/_model.qmd` eq-beta-H,
`paper/_appendix.qmd` notation table):

`Q(β) = ½ σ² β (β-1) + μ β - ρ = 0`,

with `ρ = r` in the H-regime and `ρ = r + λ` in the L-regime.  This file gives the
two roots in closed form and verifies the sign facts the model relies on:

* `charPoly_betaPlus` / `charPoly_betaMinus` : both expressions are genuine roots.
* `betaPlus_gt_one` : the positive root exceeds `1` (used as `β_H > 1`, `β_L⁺ > 1`).
* `betaMinus_neg` : the other root is negative (used as `β_s⁻ < 0`).

`ρ > μ` is the discounting condition (`r > μ_H`, and `r + λ > μ_L`); it is what
forces the positive root above `1`.
-/

namespace AILab

open Real

variable (σ μ ρ : ℝ)

/-- Discriminant of the characteristic quadratic: `(μ - σ²/2)² + 2σ²ρ`. -/
noncomputable def disc : ℝ := (μ - σ ^ 2 / 2) ^ 2 + 2 * σ ^ 2 * ρ

/-- The larger characteristic root (positive root). -/
noncomputable def betaPlus : ℝ := (-(μ - σ ^ 2 / 2) + Real.sqrt (disc σ μ ρ)) / σ ^ 2

/-- The smaller characteristic root (negative root). -/
noncomputable def betaMinus : ℝ := (-(μ - σ ^ 2 / 2) - Real.sqrt (disc σ μ ρ)) / σ ^ 2

/-- The characteristic polynomial `Q(x) = ½σ² x(x-1) + μ x - ρ`. -/
noncomputable def charPoly (x : ℝ) : ℝ := σ ^ 2 / 2 * x * (x - 1) + μ * x - ρ

variable {σ μ ρ}

lemma disc_nonneg (hσ : 0 < σ) (hρ : 0 < ρ) : 0 ≤ disc σ μ ρ := by
  unfold disc; positivity

/-- `√disc² = disc`, expanded against the definition of the discriminant. -/
lemma sq_sqrt_disc (hσ : 0 < σ) (hρ : 0 < ρ) :
    Real.sqrt (disc σ μ ρ) ^ 2 = (μ - σ ^ 2 / 2) ^ 2 + 2 * σ ^ 2 * ρ := by
  rw [Real.sq_sqrt (disc_nonneg hσ hρ)]; rfl

/-- The positive-root expression is a genuine root of the characteristic equation. -/
lemma charPoly_betaPlus (hσ : 0 < σ) (hρ : 0 < ρ) :
    charPoly σ μ ρ (betaPlus σ μ ρ) = 0 := by
  have hσ2 : σ ^ 2 ≠ 0 := pow_ne_zero 2 (ne_of_gt hσ)
  have hs := sq_sqrt_disc hσ hρ (μ := μ)
  unfold charPoly betaPlus
  field_simp
  linear_combination 4 * hs

/-- The negative-root expression is a genuine root of the characteristic equation. -/
lemma charPoly_betaMinus (hσ : 0 < σ) (hρ : 0 < ρ) :
    charPoly σ μ ρ (betaMinus σ μ ρ) = 0 := by
  have hσ2 : σ ^ 2 ≠ 0 := pow_ne_zero 2 (ne_of_gt hσ)
  have hs := sq_sqrt_disc hσ hρ (μ := μ)
  unfold charPoly betaMinus
  field_simp
  linear_combination 4 * hs

/-- `|μ - σ²/2| < √disc` (the discriminant strictly exceeds the square of the
linear coefficient because `2σ²ρ > 0`). -/
lemma abs_lt_sqrt_disc (hσ : 0 < σ) (hρ : 0 < ρ) :
    |μ - σ ^ 2 / 2| < Real.sqrt (disc σ μ ρ) := by
  rw [show |μ - σ ^ 2 / 2| = Real.sqrt ((μ - σ ^ 2 / 2) ^ 2) from
    (Real.sqrt_sq_eq_abs _).symm]
  apply Real.sqrt_lt_sqrt (sq_nonneg _)
  unfold disc
  nlinarith [mul_pos (mul_pos (by norm_num : (0:ℝ) < 2) (pow_pos hσ 2)) hρ]

/-- **The positive root exceeds one.**  This is `β_H > 1` (and `β_L⁺ > 1`); the
discounting condition `μ < ρ` is what pushes it above `1`. -/
theorem betaPlus_gt_one (hσ : 0 < σ) (hρμ : μ < ρ) :
    1 < betaPlus σ μ ρ := by
  have hσ2 : 0 < σ ^ 2 := pow_pos hσ 2
  -- `√disc > μ + σ²/2`
  have hsbig : μ + σ ^ 2 / 2 < Real.sqrt (disc σ μ ρ) := by
    by_cases h : 0 ≤ μ + σ ^ 2 / 2
    · rw [show μ + σ ^ 2 / 2 = Real.sqrt ((μ + σ ^ 2 / 2) ^ 2) from
        (Real.sqrt_sq h).symm]
      apply Real.sqrt_lt_sqrt (sq_nonneg _)
      unfold disc; nlinarith [mul_pos (pow_pos hσ 2) (sub_pos.mpr hρμ)]
    · exact lt_of_lt_of_le (not_le.mp h) (Real.sqrt_nonneg _)
  rw [betaPlus, lt_div_iff₀ hσ2]
  linarith [hsbig]

/-- **The other root is negative.**  This is `β_s⁻ < 0`. -/
theorem betaMinus_neg (hσ : 0 < σ) (hρ : 0 < ρ) : betaMinus σ μ ρ < 0 := by
  have hσ2 : 0 < σ ^ 2 := pow_pos hσ 2
  have habs := abs_lt_sqrt_disc hσ hρ (μ := μ)
  rw [betaMinus, div_neg_iff]
  right
  exact ⟨by linarith [neg_le_abs (μ - σ ^ 2 / 2), habs], hσ2⟩

/-- **Any point where the characteristic polynomial is negative lies below the
positive root.**  For the upward parabola `Q`, `Q(x) < 0` puts `x` strictly between
the two roots, so in particular `x < β₊`.  This is the workhorse for comparing
roots across regimes. -/
theorem lt_betaPlus_of_charPoly_neg (hσ : 0 < σ) (_hρ : 0 < ρ) {x : ℝ}
    (hx : charPoly σ μ ρ x < 0) : x < betaPlus σ μ ρ := by
  have hσ2 : 0 < σ ^ 2 := pow_pos hσ 2
  rw [betaPlus, lt_div_iff₀ hσ2]
  have hkey : x * σ ^ 2 + (μ - σ ^ 2 / 2) < Real.sqrt (disc σ μ ρ) := by
    by_cases h : 0 ≤ x * σ ^ 2 + (μ - σ ^ 2 / 2)
    · rw [show x * σ ^ 2 + (μ - σ ^ 2 / 2)
          = Real.sqrt ((x * σ ^ 2 + (μ - σ ^ 2 / 2)) ^ 2) from (Real.sqrt_sq h).symm]
      apply Real.sqrt_lt_sqrt (sq_nonneg _)
      simp only [disc, charPoly] at hx ⊢
      nlinarith [hx, hσ2]
    · exact lt_of_lt_of_le (not_le.mp h) (Real.sqrt_nonneg _)
  linarith [hkey]

/-- **The L-regime positive root exceeds the H-regime positive root** (`β_L⁺ > β_H`).
The L-regime raises the effective discount rate (`r + λ > r`) and lowers the drift
(`μ_L < μ_H`); both push the positive root higher.  Proof: evaluate the L-regime
polynomial at `β_H` (a root of the H-regime polynomial) — it equals
`(μ_L - μ_H)·β_H - λ < 0`, so `β_H` lies below the L-regime positive root. -/
theorem betaH_lt_betaPlus_L {σ μL μH r lam : ℝ}
    (hσ : 0 < σ) (hr : 0 < r) (hμHr : μH < r) (hlam : 0 < lam) (hμ : μL < μH) :
    betaPlus σ μH r < betaPlus σ μL (r + lam) := by
  have hroot : charPoly σ μH r (betaPlus σ μH r) = 0 := charPoly_betaPlus hσ hr
  have hβHpos : 0 < betaPlus σ μH r := lt_trans one_pos (betaPlus_gt_one hσ hμHr)
  have hrlam : 0 < r + lam := by linarith
  apply lt_betaPlus_of_charPoly_neg hσ hrlam
  have hrel : charPoly σ μL (r + lam) (betaPlus σ μH r)
      = charPoly σ μH r (betaPlus σ μH r) + ((μL - μH) * betaPlus σ μH r - lam) := by
    simp only [charPoly]; ring
  rw [hrel, hroot]
  have : (μL - μH) * betaPlus σ μH r < 0 := mul_neg_of_neg_of_pos (by linarith) hβHpos
  linarith

/-- **The Leland markup factor lies in `(0,1)`.**  For the negative root `β_s⁻ < 0`,
the option-of-waiting factor `β/(β-1) ∈ (0,1)`, so the optimal default boundary lies
strictly below the naive break-even boundary (`paper/_model.qmd`, eq-default-boundary). -/
theorem markup_mem_Ioo {β : ℝ} (hβ : β < 0) : 0 < β / (β - 1) ∧ β / (β - 1) < 1 := by
  have h1 : β - 1 < 0 := by linarith
  refine ⟨div_pos_of_neg_of_neg hβ h1, ?_⟩
  rw [div_lt_iff_of_neg h1]; linarith

/-- **The negative root decreases (becomes more negative) as the discount rate
rises.**  Hence `β_s⁻` falls with `λ` through the effective discount `r + λ`. -/
theorem betaMinus_strictAnti_rho (hσ : 0 < σ) {ρ₁ ρ₂ : ℝ} (hρ₁ : 0 < ρ₁) (hlt : ρ₁ < ρ₂) :
    betaMinus σ μ ρ₂ < betaMinus σ μ ρ₁ := by
  have hσ2 : 0 < σ ^ 2 := pow_pos hσ 2
  have hsqrt : Real.sqrt (disc σ μ ρ₁) < Real.sqrt (disc σ μ ρ₂) := by
    apply Real.sqrt_lt_sqrt (disc_nonneg hσ hρ₁)
    simp only [disc]; nlinarith [mul_pos hσ2 (show (0:ℝ) < ρ₂ - ρ₁ by linarith)]
  rw [betaMinus, betaMinus, div_lt_div_iff₀ hσ2 hσ2]
  nlinarith [hsqrt, hσ2]

/-- **The Leland markup `β/(β-1)` is strictly decreasing in `β`** (for `β < 1`). -/
theorem markup_strictAnti {β₁ β₂ : ℝ} (_h₁ : β₁ < 1) (h₂ : β₂ < 1) (hlt : β₁ < β₂) :
    β₂ / (β₂ - 1) < β₁ / (β₁ - 1) := by
  have d₁ : β₁ - 1 ≠ 0 := by intro h; apply absurd h; linarith
  have d₂ : β₂ - 1 ≠ 0 := by intro h; apply absurd h; linarith
  have key : β₁ / (β₁ - 1) - β₂ / (β₂ - 1) = (β₂ - β₁) / ((β₁ - 1) * (β₂ - 1)) := by
    field_simp; ring
  have hden : 0 < (β₁ - 1) * (β₂ - 1) :=
    mul_pos_of_neg_of_neg (by linarith) (by linarith)
  have : 0 < β₁ / (β₁ - 1) - β₂ / (β₂ - 1) := by
    rw [key]; exact div_pos (by linarith) hden
  linarith

/-- **The markup channel: `β/(β-1)` evaluated at the negative root rises with `λ`.**
Because `β_s⁻` falls with the effective discount `r+λ` and the markup is decreasing
in `β`, the markup `M(β_s⁻)` is increasing in `λ` — the `β`-channel of
Proposition 2(ii) that opposes faith-based survival. -/
theorem markup_betaMinus_increasing_lam {σ μ r lam₁ lam₂ : ℝ}
    (hσ : 0 < σ) (hr : 0 < r) (hlam₁ : 0 < lam₁) (hlt : lam₁ < lam₂) :
    betaMinus σ μ (r + lam₁) / (betaMinus σ μ (r + lam₁) - 1)
      < betaMinus σ μ (r + lam₂) / (betaMinus σ μ (r + lam₂) - 1) := by
  have hr1 : 0 < r + lam₁ := by linarith
  have hβ2lt : betaMinus σ μ (r + lam₂) < betaMinus σ μ (r + lam₁) :=
    betaMinus_strictAnti_rho hσ hr1 (by linarith)
  have hn1 : betaMinus σ μ (r + lam₁) < 0 := betaMinus_neg hσ hr1
  have hn2 : betaMinus σ μ (r + lam₂) < 0 := betaMinus_neg hσ (by linarith)
  exact markup_strictAnti (by linarith) (by linarith) hβ2lt

end AILab
