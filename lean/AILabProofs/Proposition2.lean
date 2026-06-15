import AILabProofs.Basic

set_option linter.style.header false

/-!
# Proposition 2 — faith-based survival

This file verifies the two closed-form ingredients of Proposition 2
(`paper/_appendix.qmd`, "Proof of Proposition 2", part (ii), and
`paper/_model.qmd` eq-phi-underbar).

The effective revenue coefficient, as a function of the regime-switch arrival rate
`λ`, is

`A_eff(λ) = (a + λ b) / (d + λ)`,    `d = r - μ_L`,

where `a = [(1-φ)K]^α s^L` is the L-regime revenue flow and
`b = (φK)^α s^H / (r - μ_H)` the H-regime revenue present value.

* `hasDerivAt_A_eff` : `∂A_eff/∂λ = (b·d - a)/(d+λ)²`, matching the paper's
  quotient-rule derivative `(b(r-μ_L) - a)/(r-μ_L+λ)²`.
* `A_eff_deriv_pos` : the faith-based survival condition `a < b·d` makes the
  derivative positive (optimism *lowers* the default boundary).
* `faith_threshold` : in the symmetric duopoly the condition
  `(φ/(1-φ))^α > (r-μ_H)/(r-μ_L)` is equivalent to `φ > φ̲ = R/(1+R)` with
  `R = ((r-μ_H)/(r-μ_L))^(1/α)`.
-/

namespace AILab

open Real

/-- **Quotient-rule derivative of `A_eff` in `λ`.**  With `A_eff(l) = (a+l b)/(d+l)`,
the derivative at `λ` is `(b·d - a)/(d+λ)²`. -/
theorem hasDerivAt_A_eff (a b d lam : ℝ) (hdlam : 0 < d + lam) :
    HasDerivAt (fun l => (a + l * b) / (d + l)) ((b * d - a) / (d + lam) ^ 2) lam := by
  have hn : HasDerivAt (fun l => a + l * b) b lam := by
    simpa using ((hasDerivAt_id lam).mul_const b).const_add a
  have hm : HasDerivAt (fun l => d + l) 1 lam := by
    simpa using (hasDerivAt_id lam).const_add d
  have hmne : d + lam ≠ 0 := ne_of_gt hdlam
  have key : (b * d - a) / (d + lam) ^ 2
      = (b * (d + lam) - (a + lam * b) * 1) / (d + lam) ^ 2 := by
    have : (d + lam) ^ 2 ≠ 0 := pow_ne_zero 2 hmne
    field_simp; ring
  rw [key]
  exact hn.div hm hmne

/-- **Faith-based survival condition.**  When the H-regime revenue present value
scaled by the L-regime discount rate exceeds the L-regime flow (`a < b·d`), the
effective revenue coefficient rises with optimism `λ`. -/
theorem A_eff_deriv_pos {a b d lam : ℝ} (hdlam : 0 < d + lam) (hfaith : a < b * d) :
    0 < (b * d - a) / (d + lam) ^ 2 :=
  div_pos (by linarith) (pow_pos hdlam 2)

/-- **Faith-based survival threshold (symmetric duopoly).**  The faith condition
`(φ/(1-φ))^α > q` (with `q = (r-μ_H)/(r-μ_L)`) holds exactly when `φ` exceeds the
threshold `R/(1+R)`, `R = q^(1/α)`.  This is `eq-phi-underbar`. -/
theorem faith_threshold {φ α q : ℝ}
    (hφ0 : 0 < φ) (hφ1 : φ < 1) (hα : 0 < α) (hq : 0 < q) :
    q < (φ / (1 - φ)) ^ α ↔ q ^ (1 / α) / (1 + q ^ (1 / α)) < φ := by
  set R := q ^ (1 / α) with hRdef
  have hR : 0 < R := Real.rpow_pos_of_pos hq _
  have h1mφ : 0 < 1 - φ := by linarith
  have hg : 0 < φ / (1 - φ) := div_pos hφ0 h1mφ
  -- `R^α = q`
  have hRq : R ^ α = q := by
    rw [hRdef, ← Real.rpow_mul hq.le, one_div, inv_mul_cancel₀ (ne_of_gt hα), Real.rpow_one]
  -- Step 1: `q < g^α ↔ R < g` (strict monotonicity of `x ↦ x^α`, `α > 0`).
  have step1 : q < (φ / (1 - φ)) ^ α ↔ R < φ / (1 - φ) := by
    rw [← hRq]
    constructor
    · intro h
      by_contra hc
      replace hc := not_lt.1 hc
      exact absurd (Real.rpow_le_rpow hg.le hc hα.le) (not_le.mpr h)
    · intro h
      exact Real.rpow_lt_rpow hR.le h hα
  -- Step 2: `R < φ/(1-φ) ↔ R/(1+R) < φ` (clearing the increasing map `φ ↦ φ/(1-φ)`).
  have step2 : R < φ / (1 - φ) ↔ R / (1 + R) < φ := by
    rw [lt_div_iff₀ h1mφ, div_lt_iff₀ (by linarith : (0:ℝ) < 1 + R)]
    constructor <;> intro h <;> nlinarith [h]
  rw [step1, step2]

/-! ## Default-boundary monotonicities (Proposition 2(i),(iv)) -/

/-- **The default boundary is increasing in leverage** (Proposition 2(i)).
`X_D = M·(coef·ℓ + base)/A` with markup `M>0`, coefficient `coef = c_d·I(K)/r > 0`,
and `A = A_eff > 0`; only the coupon numerator depends on `ℓ`. -/
theorem XD_increasing_leverage {M A coef base ℓ₁ ℓ₂ : ℝ}
    (hM : 0 < M) (hA : 0 < A) (hcoef : 0 < coef) (hℓ : ℓ₁ < ℓ₂) :
    M * (coef * ℓ₁ + base) / A < M * (coef * ℓ₂ + base) / A := by
  rw [div_lt_div_iff₀ hA hA]
  nlinarith [mul_pos (mul_pos hM hA) hcoef, hℓ]

/-- **The Tullock contest share is decreasing in rival capacity** (Proposition 2(iv)).
`s_i = K_i^α/(K_i^α + K_j^α)` falls as `K_j` rises; since `A_eff` is increasing in the
shares and `X_D = N/A_eff`, stronger rivals raise the default boundary. -/
theorem share_decreasing_rival {Ki α Kj₁ Kj₂ : ℝ}
    (hKi : 0 < Ki) (hα : 0 < α) (hKj₁ : 0 < Kj₁) (hlt : Kj₁ < Kj₂) :
    Ki ^ α / (Ki ^ α + Kj₂ ^ α) < Ki ^ α / (Ki ^ α + Kj₁ ^ α) := by
  have hi : 0 < Ki ^ α := Real.rpow_pos_of_pos hKi _
  have hj₁ : 0 < Kj₁ ^ α := Real.rpow_pos_of_pos hKj₁ _
  have hj₂ : 0 < Kj₂ ^ α := Real.rpow_pos_of_pos (lt_trans hKj₁ hlt) _
  have hjlt : Kj₁ ^ α < Kj₂ ^ α := Real.rpow_lt_rpow hKj₁.le hlt hα
  rw [div_lt_div_iff₀ (by linarith) (by linarith)]
  nlinarith [mul_pos hi (sub_pos.mpr hjlt)]

/-- **The default boundary `N/A_eff` rises as `A_eff` falls** — combined with
`share_decreasing_rival`, this is the rival-capacity comparative static. -/
theorem XD_decreasing_in_Aeff {N A₁ A₂ : ℝ} (hN : 0 < N) (hA₂ : 0 < A₂) (hlt : A₂ < A₁) :
    N / A₁ < N / A₂ := by
  rw [div_lt_div_iff₀ (by linarith) hA₂]
  nlinarith [hN, hlt]

/-! ## Exact net threshold `φ̃` (Proposition 2(ii), eq-phi-tilde)

The sign of `∂X_D/∂λ` nets the `A_eff`-channel (faith-based survival) against the
markup channel (`markup_betaMinus_increasing_lam` in `CharacteristicRoots`).  The
condition `∂X_D/∂λ < 0` is `b(r-μ_L) - a > m(a+λb)Δ` with `Δ = r-μ_L+λ` and `m` the
markup semi-elasticity; it rearranges to a clean ratio threshold on `b/a`. -/

/-- **Net-threshold rearrangement.**  `b·rm - a > m(a+λb)Δ ⟺ b/a > (1+mΔ)/(rm - mλΔ)`,
under the regularity condition `rm > mλΔ`.  (This is linear in `(a,b)`; `rm = r-μ_L`.) -/
theorem net_threshold_rearrange {a b rm Δ m lam : ℝ}
    (ha : 0 < a) (hreg : 0 < rm - m * lam * Δ) :
    b * rm - a > m * (a + lam * b) * Δ ↔ b / a > (1 + m * Δ) / (rm - m * lam * Δ) := by
  rw [gt_iff_lt, gt_iff_lt, div_lt_div_iff₀ hreg ha]
  constructor <;> intro h <;> nlinarith [h]

/-- **Net threshold `φ̃` in symmetric duopoly.**  Substituting the symmetric ratio
`b/a = (φ/(1-φ))^α/(r-μ_H)`, the net condition becomes a faith-style threshold on
`φ`: combine `net_threshold_rearrange` with `faith_threshold` at the larger cutoff
`q̃ = (1+mΔ)/(rm-mλΔ)·(r-μ_H)`.  Because `q̃ > q`, the net threshold `φ̃` exceeds the
`A_eff`-channel threshold `φ̲`. -/
theorem net_threshold_phi {φ α qtilde : ℝ}
    (hφ0 : 0 < φ) (hφ1 : φ < 1) (hα : 0 < α) (hq : 0 < qtilde) :
    qtilde < (φ / (1 - φ)) ^ α ↔ qtilde ^ (1 / α) / (1 + qtilde ^ (1 / α)) < φ :=
  faith_threshold hφ0 hφ1 hα hq

end AILab
