import AILabProofs.Basic

set_option linter.style.header false

/-!
# Proposition 2 — the default boundary and faith-based survival

This file verifies the closed-form ingredients of Proposition 2
(`paper/_appendix.qmd`, "Proof of Proposition 2", and `paper/_model.qmd`,
eq-default-boundary, eq-equity, eq-phi-underbar, eq-phi-tilde).  Proposition 2 is a
statement about the single-boundary reduction at fixed `(K, φ, ℓ)`, with `ℓ ≥ 0`: at
`ℓ = 0` the boundary is the unlevered firm's shutdown boundary.

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
* `XD_increasing_leverage`, `share_decreasing_rival`, `XD_decreasing_in_Aeff` :
  parts (i) and (iv).
* `net_threshold_rearrange`, `net_threshold_phi` : the net threshold `φ̃` of part (ii)
  (with the markup channel in `CharacteristicRoots.lean`).
* `phiUnder_strictMono_alpha`, `phiUnder_strictMono_r`, `phiUnder_strictAnti_muH`,
  `phiUnder_strictMono_muL` : the comparative statics of `φ̲` in part (ii).
* `equity_value_matching`, `hasDerivAt_equity`, `default_smooth_pasting_iff` : value
  matching holds by construction for eq-equity and smooth pasting is equivalent to
  eq-default-boundary.  `revenue_at_boundary`, `shutdown_boundary_pos` and
  `boundary_continuous_coupon` : revenue at the boundary covers `β/(β-1)` of the fixed
  claims, the zero-coupon boundary is positive, and the boundary is continuous in the
  coupon.

The equity function of eq-equity is taken as given: that it solves the equity ODE
under the single-boundary reduction, and that smooth pasting is the optimal default
rule, are not formalized.
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
`X_D = M·(coef·ℓ + base)/A` with markup `M>0`, coefficient `coef = r_c·I(K)/r > 0`,
`base = δK/r` and `A = A_eff > 0`; only the coupon numerator depends on `ℓ`.  No sign
is imposed on `ℓ`, so the statement covers `ℓ₁ = 0`, the shutdown boundary.  With
`coef = ℓ·I(K)/r` and the variable `r_c` it is the monotonicity in the coupon rate. -/
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

/-! ## The threshold `φ̲` and its comparative statics (Proposition 2(ii))

`φ̲ = Ω/(1+Ω)` with `Ω = q^{1/α}` and `q = (r-μ_H)/(r-μ_L) ∈ (0,1)`.  The paper states
that `φ̲` is increasing in `α`, decreasing in the growth premium `μ_H - μ_L` (whether
`μ_H` rises or `μ_L` falls) and increasing in `r`.  Each follows from the monotonicity
of `q ↦ q^{1/α}/(1+q^{1/α})` in `q` and, for `q < 1`, in `α`. -/

section Threshold

open Set

/-- The threshold `φ̲ = Ω/(1+Ω)`, `Ω = q^{1/α}` (eq-phi-underbar). -/
noncomputable def phiUnder (q α : ℝ) : ℝ := q ^ (1 / α) / (1 + q ^ (1 / α))

/-- The odds power `(φ/(1-φ))^α` is strictly increasing on `(0,1)`. -/
theorem oddsPow_strictMonoOn {α : ℝ} (hα : 0 < α) :
    StrictMonoOn (fun φ : ℝ => (φ / (1 - φ)) ^ α) (Ioo 0 1) := by
  intro x hx y hy hxy
  have h1x : 0 < 1 - x := by linarith [hx.2]
  have h1y : 0 < 1 - y := by linarith [hy.2]
  have hlt : x / (1 - x) < y / (1 - y) := by
    rw [div_lt_div_iff₀ h1x h1y]; nlinarith
  exact Real.rpow_lt_rpow (div_pos hx.1 h1x).le hlt hα

lemma phiUnder_mem {q α : ℝ} (hq : 0 < q) : phiUnder q α ∈ Ioo 0 1 := by
  have hR : 0 < q ^ (1 / α) := Real.rpow_pos_of_pos hq _
  refine ⟨div_pos hR (by linarith), ?_⟩
  rw [phiUnder, div_lt_one (by linarith)]; linarith

/-- At the threshold the odds power equals `q`. -/
lemma oddsPow_phiUnder {q α : ℝ} (hq : 0 < q) (hα : 0 < α) :
    (phiUnder q α / (1 - phiUnder q α)) ^ α = q := by
  have hR : 0 < q ^ (1 / α) := Real.rpow_pos_of_pos hq _
  have hodds : phiUnder q α / (1 - phiUnder q α) = q ^ (1 / α) := by
    unfold phiUnder
    have : (1 + q ^ (1 / α)) ≠ 0 := by linarith
    field_simp
    ring
  rw [hodds, ← Real.rpow_mul hq.le, one_div, inv_mul_cancel₀ (ne_of_gt hα), Real.rpow_one]


/-- `φ̲` is strictly increasing in `q` (for `α > 0`). -/
theorem phiUnder_strictMono_q {α q₁ q₂ : ℝ} (hα : 0 < α) (hq₁ : 0 < q₁) (hlt : q₁ < q₂) :
    phiUnder q₁ α < phiUnder q₂ α := by
  have hR₁ : 0 < q₁ ^ (1 / α) := Real.rpow_pos_of_pos hq₁ _
  have hR₂ : 0 < q₂ ^ (1 / α) := Real.rpow_pos_of_pos (lt_trans hq₁ hlt) _
  have hRlt : q₁ ^ (1 / α) < q₂ ^ (1 / α) :=
    Real.rpow_lt_rpow hq₁.le hlt (div_pos one_pos hα)
  rw [phiUnder, phiUnder, div_lt_div_iff₀ (by linarith) (by linarith)]
  nlinarith

/-- **`φ̲` is strictly increasing in `α`** when `q < 1` (i.e. `μ_L < μ_H`). -/
theorem phiUnder_strictMono_alpha {q α₁ α₂ : ℝ} (hq0 : 0 < q) (hq1 : q < 1)
    (hα₁ : 0 < α₁) (hlt : α₁ < α₂) :
    phiUnder q α₁ < phiUnder q α₂ := by
  have hα₂ : 0 < α₂ := lt_trans hα₁ hlt
  have hexp : 1 / α₂ < 1 / α₁ := one_div_lt_one_div_of_lt hα₁ hlt
  have hRlt : q ^ (1 / α₁) < q ^ (1 / α₂) := Real.rpow_lt_rpow_of_exponent_gt hq0 hq1 hexp
  have hR₁ : 0 < q ^ (1 / α₁) := Real.rpow_pos_of_pos hq0 _
  have hR₂ : 0 < q ^ (1 / α₂) := Real.rpow_pos_of_pos hq0 _
  rw [phiUnder, phiUnder, div_lt_div_iff₀ (by linarith) (by linarith)]
  nlinarith

/-- `q = (r-μ_H)/(r-μ_L)` is strictly increasing in `r` when `μ_L < μ_H < r`. -/
lemma q_strictMono_r {μL μH r₁ r₂ : ℝ} (hμ : μL < μH) (hr₁ : μH < r₁) (hlt : r₁ < r₂) :
    (r₁ - μH) / (r₁ - μL) < (r₂ - μH) / (r₂ - μL) := by
  rw [div_lt_div_iff₀ (by linarith) (by linarith)]
  nlinarith [mul_pos (sub_pos.mpr hlt) (sub_pos.mpr hμ)]

/-- **`φ̲` is strictly increasing in `r`.** -/
theorem phiUnder_strictMono_r {μL μH α r₁ r₂ : ℝ} (hα : 0 < α) (hμ : μL < μH)
    (hr₁ : μH < r₁) (hlt : r₁ < r₂) :
    phiUnder ((r₁ - μH) / (r₁ - μL)) α < phiUnder ((r₂ - μH) / (r₂ - μL)) α :=
  phiUnder_strictMono_q hα (div_pos (by linarith) (by linarith)) (q_strictMono_r hμ hr₁ hlt)

/-- **`φ̲` is strictly decreasing in `μ_H`** (a larger growth premium, `μ_L` fixed). -/
theorem phiUnder_strictAnti_muH {μL α r μH₁ μH₂ : ℝ} (hα : 0 < α) (hL : μL < r)
    (hr : μH₂ < r) (hlt : μH₁ < μH₂) :
    phiUnder ((r - μH₂) / (r - μL)) α < phiUnder ((r - μH₁) / (r - μL)) α :=
  phiUnder_strictMono_q hα (div_pos (by linarith) (by linarith))
    (div_lt_div_of_pos_right (by linarith) (by linarith))

/-- **`φ̲` is strictly increasing in `μ_L`** (so decreasing in `μ_H - μ_L` when `μ_L`
falls, `μ_H` fixed). -/
theorem phiUnder_strictMono_muL {μH α r μL₁ μL₂ : ℝ} (hα : 0 < α) (hH : μH < r)
    (hL₂ : μL₂ < r) (hlt : μL₁ < μL₂) :
    phiUnder ((r - μH) / (r - μL₁)) α < phiUnder ((r - μH) / (r - μL₂)) α :=
  phiUnder_strictMono_q hα (div_pos (by linarith) (by linarith))
    (div_lt_div_of_pos_left (by linarith) (by linarith) (by linarith))

end Threshold

/-! ## Default and shutdown boundary from smooth pasting (eq-default-boundary, eq-equity)

Above the boundary the single-boundary going-concern equity is
`E(X) = A X - N + (N - A X_D)(X/X_D)^β`, with `A = A_eff`, `N = (C_D + δK)/r` the
fixed claims and `β = β_L^- < 0` (eq-equity; that this is the solution of the
equity ODE under the single-boundary reduction is taken as given).  Value matching
`E(X_D) = 0` holds by construction, and smooth pasting `E'(X_D) = 0` is equivalent to
the closed form `X_D = β/(β-1) · N/A`.  At `C_D = 0` the same formula is the shutdown
boundary of the unlevered firm, and the boundary is continuous in the coupon, hence in
leverage, at zero. -/

/-- The single-boundary equity value `E(X) = AX - N + (N - A X_D)(X/X_D)^β`. -/
noncomputable def equityValue (A N XD β X : ℝ) : ℝ :=
  A * X - N + (N - A * XD) * (X / XD) ^ β

/-- **Value matching at the boundary:** `E(X_D) = 0`. -/
theorem equity_value_matching {A N XD β : ℝ} (hXD : 0 < XD) :
    equityValue A N XD β XD = 0 := by
  unfold equityValue
  rw [div_self (ne_of_gt hXD), Real.one_rpow]
  ring

/-- **Derivative of equity in demand:**
`E'(X) = A + (N - A X_D)·β·(X/X_D)^{β-1}/X_D`. -/
theorem hasDerivAt_equity {A N XD β X : ℝ} (hXD : 0 < XD) (hX : 0 < X) :
    HasDerivAt (equityValue A N XD β)
      (A + (N - A * XD) * (β * (X / XD) ^ (β - 1) * (1 / XD))) X := by
  have hq : HasDerivAt (fun x => x / XD) (1 / XD) X := by
    simpa [one_div] using (hasDerivAt_id X).div_const XD
  have hp := hq.rpow_const (p := β) (Or.inl (ne_of_gt (div_pos hX hXD)))
  have h := (((hasDerivAt_id X).const_mul A).sub_const N).add (hp.const_mul (N - A * XD))
  refine h.congr_deriv ?_
  ring

/-- **Smooth pasting at the default boundary pins it down in closed form**
(eq-default-boundary).  For `β ≠ 1` (in the model `β = β_L^- < 0`), `A > 0` and
`X_D > 0`, the condition `E'(X_D) = 0` holds exactly when
`X_D = β/(β-1) · N/A`. -/
theorem default_smooth_pasting_iff {A N XD β : ℝ} (hβ : β < 0) (hA : 0 < A) (hXD : 0 < XD) :
    A + (N - A * XD) * (β * (XD / XD) ^ (β - 1) * (1 / XD)) = 0 ↔
      XD = β / (β - 1) * N / A := by
  have hβ1 : β - 1 ≠ 0 := by intro h; linarith
  rw [div_self (ne_of_gt hXD), Real.one_rpow]
  have hXDne : XD ≠ 0 := ne_of_gt hXD
  have hAne : A ≠ 0 := ne_of_gt hA
  constructor
  · intro h
    field_simp at h ⊢
    linear_combination (-1) * h
  · intro h
    have hk : A * XD * (β - 1) = β * N := by rw [h]; field_simp
    rw [show A + (N - A * XD) * (β * 1 * (1 / XD)) = (A * XD + (N - A * XD) * β) / XD by
      field_simp]
    rw [div_eq_zero_iff]
    left
    linear_combination (-1) * hk

/-- **Revenue at the boundary covers the fraction `β/(β-1)` of the fixed claims:**
`A·X_D = β/(β-1)·N`. -/
theorem revenue_at_boundary {A N β : ℝ} (hA : 0 < A) :
    A * (β / (β - 1) * N / A) = β / (β - 1) * N := by
  field_simp

/-- **Shutdown boundary.**  At a zero coupon the boundary is
`β/(β-1)·(δK/r)/A`, strictly positive for `β < 0`, `δK/r > 0` and `A > 0`. -/
theorem shutdown_boundary_pos {A β δK r : ℝ} (hβ : β < 0) (hA : 0 < A) (hδK : 0 < δK)
    (hr : 0 < r) :
    0 < β / (β - 1) * ((0 + δK) / r) / A := by
  have hM : 0 < β / (β - 1) := div_pos_of_neg_of_neg hβ (by linarith)
  rw [zero_add]
  positivity

/-- **The boundary is continuous in the coupon**, so it is continuous in leverage at
`ℓ = 0`, where it equals the shutdown boundary. -/
theorem boundary_continuous_coupon (A β δK r : ℝ) :
    Continuous (fun CD : ℝ => β / (β - 1) * ((CD + δK) / r) / A) := by
  fun_prop

end AILab
