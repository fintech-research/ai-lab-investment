import AILabProofs.Proposition2

set_option linter.style.header false

/-!
# Corollary 1 — installed value in the arrival rate

This file verifies Corollary 1 (`paper/_appendix.qmd`, "Installed value in the arrival
rate (Corollary 1)", eq-installed-lambda).  A single installed firm holds capacity
`K`, allocation `φ`, coupon `C_D` and demand `X` fixed while `λ` varies.  Its
going-concern value is

`V(λ) = A_eff(λ)·X - κ`,   `A_eff(λ) = (a + λ b)/(d + λ)`,   `κ = (δK + C_D)/r`,

with `a = Π_L = [(1-φ)K]^α`, `b = Π_H = (φK)^α/(r-μ_H)` and `d = r - μ_L > 0`.  The
faith gap is `G = b·d - a`.

* `hasDerivAt_V_lam`, `hasDerivAt_V_lam_deriv` : `V' = XG/Δ²` and `V'' = -2XG/Δ³`
  with `Δ = d + λ` (eq-installed-lambda); `hasDerivAt_A_eff_deriv` is the same for
  `A_eff`.
* `V_lam_strictMonoOn`, `V_lam_strictConcaveOn` (and the mirror images
  `V_lam_strictAntiOn`, `V_lam_strictConvexOn`, `V_lam_const`) : the sign of `G`
  fixes monotonicity and curvature on all of `λ ≥ 0`.
* `faithGap_pos_iff`, `faithGap_neg_iff` : at monopoly shares, `G > 0 ⟺ φ > φ̲` and
  `G < 0 ⟺ φ < φ̲`, with `φ̲` of eq-phi-underbar.
* `corollary1_i` : part (i), `V` strictly increasing and strictly concave on
  `λ ≥ 0` **iff** `φ > φ̲`.
* `news_asymmetry`, `news_asymmetry_pos_iff` : part (ii), the identity
  `[V(λ)-V(λ-h)] - [V(λ+h)-V(λ)] = 2h²XG/(Δ(Δ-h)(Δ+h))` and its sign.
* `hasDerivAt_faithGap_phi`, `faithGap_strictMonoOn`, `semiElasticity_eq`,
  `semiElasticity_lt` : part (iii), `∂G/∂φ > 0`, so `V'`, `|V''|` and the news
  difference increase in `φ`; and the semi-elasticity of `A_eff` in `λ` is
  increasing in `ρ = Π_H/Π_L`, which is increasing in `φ` (`ratio_strictMonoOn`).

The corollary is about the going-concern value without the option to stop; the
versions with the shutdown or default option, and for the duopoly leader, are
numerical and not formalized.
-/

namespace AILab

open Real Set

/-! ## Derivatives (eq-installed-lambda) -/

/-- **Second derivative of `A_eff` in `λ`.**  The derivative `(bd - a)/(d+l)²` of
`hasDerivAt_A_eff` has derivative `-2(bd - a)/(d+λ)³`. -/
theorem hasDerivAt_A_eff_deriv (a b d lam : ℝ) (hdlam : 0 < d + lam) :
    HasDerivAt (fun l => (b * d - a) / (d + l) ^ 2)
      (-2 * (b * d - a) / (d + lam) ^ 3) lam := by
  have hm : HasDerivAt (fun l => d + l) 1 lam := by
    simpa using (hasDerivAt_id lam).const_add d
  have hsq := hm.pow 2
  have hne : (d + lam) ^ 2 ≠ 0 := pow_ne_zero 2 (ne_of_gt hdlam)
  have h := (hasDerivAt_const lam (b * d - a)).div hsq hne
  refine h.congr_deriv ?_
  have : d + lam ≠ 0 := ne_of_gt hdlam
  simp only [Pi.pow_apply]
  field_simp
  ring

/-- **`A_eff'' < 0` under the faith condition** `a < bd`. -/
theorem A_eff_second_deriv_neg {a b d lam : ℝ} (hdlam : 0 < d + lam) (hfaith : a < b * d) :
    -2 * (b * d - a) / (d + lam) ^ 3 < 0 :=
  div_neg_of_neg_of_pos (by linarith) (pow_pos hdlam 3)

/-- Going-concern value of the installed firm as a function of `λ`. -/
noncomputable def Vlam (a b d X κ l : ℝ) : ℝ := (a + l * b) / (d + l) * X - κ

/-- **`V'(λ) = X(bd - a)/(d+λ)²`** (eq-installed-lambda, first identity). -/
theorem hasDerivAt_V_lam (a b d X κ lam : ℝ) (hdlam : 0 < d + lam) :
    HasDerivAt (Vlam a b d X κ) (X * (b * d - a) / (d + lam) ^ 2) lam := by
  have h := ((hasDerivAt_A_eff a b d lam hdlam).mul_const X).sub_const κ
  refine h.congr_deriv ?_
  ring

/-- **`V''(λ) = -2X(bd - a)/(d+λ)³`** (eq-installed-lambda, second identity). -/
theorem hasDerivAt_V_lam_deriv (a b d X lam : ℝ) (hdlam : 0 < d + lam) :
    HasDerivAt (fun l => X * (b * d - a) / (d + l) ^ 2)
      (-2 * X * (b * d - a) / (d + lam) ^ 3) lam := by
  have h := (hasDerivAt_A_eff_deriv a b d lam hdlam).const_mul X
  refine (h.congr_deriv ?_).congr_of_eventuallyEq ?_
  · ring
  · exact Filter.Eventually.of_forall (fun l => by ring)

/-! ## Shape on `λ ≥ 0` -/

/-- `A_eff(l) - A_eff(l') = G (l - l')/((d+l)(d+l'))`. -/
lemma A_eff_sub {a b d l l' : ℝ} (h : 0 < d + l) (h' : 0 < d + l') :
    (a + l * b) / (d + l) - (a + l' * b) / (d + l')
      = (b * d - a) * (l - l') / ((d + l) * (d + l')) := by
  have := ne_of_gt h; have := ne_of_gt h'
  field_simp
  ring

/-- `1/t` is strictly convex: `1/(wp + vq) < w/p + v/q` for `p ≠ q`. -/
lemma inv_strict_convex {p q w v : ℝ} (hp : 0 < p) (hq : 0 < q) (hpq : p ≠ q)
    (hw : 0 < w) (hv : 0 < v) (hwv : w + v = 1) :
    1 / (w * p + v * q) < w / p + v / q := by
  have hv' : v = 1 - w := by linarith
  subst hv'
  have hs : 0 < w * p + (1 - w) * q := by nlinarith
  rw [div_add_div _ _ (ne_of_gt hp) (ne_of_gt hq), div_lt_div_iff₀ hs (mul_pos hp hq)]
  have hsq : 0 < (p - q) ^ 2 := by
    have : p - q ≠ 0 := sub_ne_zero.mpr hpq
    positivity
  nlinarith [mul_pos (mul_pos hw hv) hsq]

/-- `A_eff(l) = b - G/(d+l)`. -/
lemma A_eff_eq_sub {a b d l : ℝ} (h : 0 < d + l) :
    (a + l * b) / (d + l) = b - (b * d - a) / (d + l) := by
  have := ne_of_gt h
  field_simp
  ring

/-- Convex-combination inequality for `A_eff` in `λ`: strict concavity when `G > 0`,
written as `G · (w f(x) + v f(y) - f(wx + vy)) < 0` through `1/t` convexity. -/
lemma A_eff_combo {a b d x y w v : ℝ} (hx : 0 < d + x) (hy : 0 < d + y)
    (hw : 0 < w) (hv : 0 < v) (hwv : w + v = 1) :
    w * ((a + x * b) / (d + x)) + v * ((a + y * b) / (d + y))
        - (a + (w * x + v * y) * b) / (d + (w * x + v * y))
      = (b * d - a) * (1 / (w * (d + x) + v * (d + y)) - (w / (d + x) + v / (d + y))) := by
  have hv' : v = 1 - w := by linarith
  subst hv'
  have hc : d + (w * x + (1 - w) * y) = w * (d + x) + (1 - w) * (d + y) := by ring
  have hcpos : 0 < w * (d + x) + (1 - w) * (d + y) := by positivity
  rw [A_eff_eq_sub hx, A_eff_eq_sub hy, A_eff_eq_sub (by rw [hc]; exact hcpos), hc]
  have := ne_of_gt hx; have := ne_of_gt hy; have := ne_of_gt hcpos
  field_simp
  ring

variable {a b d X κ : ℝ}

/-- **Strictly increasing on `λ ≥ 0` when `G > 0`.** -/
theorem V_lam_strictMonoOn (hd : 0 < d) (hX : 0 < X) (hG : a < b * d) :
    StrictMonoOn (Vlam a b d X κ) (Ici 0) := by
  intro x hx y hy hxy
  have hx' : 0 < d + x := by have : (0:ℝ) ≤ x := hx; linarith
  have hy' : 0 < d + y := by have : (0:ℝ) ≤ y := hy; linarith
  have key := A_eff_sub (a := a) (b := b) hy' hx'
  have hpos : 0 < (b * d - a) * (y - x) / ((d + y) * (d + x)) :=
    div_pos (mul_pos (by linarith) (by linarith)) (mul_pos hy' hx')
  unfold Vlam
  nlinarith [mul_pos hX hpos]

/-- **Strictly decreasing on `λ ≥ 0` when `G < 0`.** -/
theorem V_lam_strictAntiOn (hd : 0 < d) (hX : 0 < X) (hG : b * d < a) :
    StrictAntiOn (Vlam a b d X κ) (Ici 0) := by
  intro x hx y hy hxy
  have hx' : 0 < d + x := by have : (0:ℝ) ≤ x := hx; linarith
  have hy' : 0 < d + y := by have : (0:ℝ) ≤ y := hy; linarith
  have key := A_eff_sub (a := a) (b := b) hy' hx'
  have hneg : (b * d - a) * (y - x) / ((d + y) * (d + x)) < 0 :=
    div_neg_of_neg_of_pos (mul_neg_of_neg_of_pos (by linarith) (by linarith))
      (mul_pos hy' hx')
  unfold Vlam
  nlinarith [mul_neg_of_pos_of_neg hX hneg]

/-- **Constant when `G = 0`.** -/
theorem V_lam_const (hd : 0 < d) (hG : a = b * d) {l : ℝ} (hl : 0 ≤ l) :
    Vlam a b d X κ l = b * X - κ := by
  have : d + l ≠ 0 := by linarith
  unfold Vlam
  rw [hG]
  field_simp

/-- **Strictly concave on `λ ≥ 0` when `G > 0`.** -/
theorem V_lam_strictConcaveOn (hd : 0 < d) (hX : 0 < X) (hG : a < b * d) :
    StrictConcaveOn ℝ (Ici 0) (Vlam a b d X κ) := by
  refine ⟨convex_Ici 0, ?_⟩
  intro x hx y hy hxy w v hw hv hwv
  have hx' : 0 < d + x := by have : (0:ℝ) ≤ x := hx; linarith
  have hy' : 0 < d + y := by have : (0:ℝ) ≤ y := hy; linarith
  have hpq : d + x ≠ d + y := fun h => hxy (by linarith)
  have hconv := inv_strict_convex hx' hy' hpq hw hv hwv
  have hcombo := A_eff_combo (a := a) (b := b) hx' hy' hw hv hwv
  have hneg : w * ((a + x * b) / (d + x)) + v * ((a + y * b) / (d + y))
      - (a + (w * x + v * y) * b) / (d + (w * x + v * y)) < 0 := by
    rw [hcombo]; exact mul_neg_of_pos_of_neg (by linarith) (by linarith)
  simp only [smul_eq_mul, Vlam]
  have key : w * ((a + x * b) / (d + x) * X - κ) + v * ((a + y * b) / (d + y) * X - κ)
      - ((a + (w * x + v * y) * b) / (d + (w * x + v * y)) * X - κ)
      = X * (w * ((a + x * b) / (d + x)) + v * ((a + y * b) / (d + y))
          - (a + (w * x + v * y) * b) / (d + (w * x + v * y))) := by
    linear_combination (-κ) * hwv
  linarith [mul_neg_of_pos_of_neg hX hneg]

/-- **Strictly convex on `λ ≥ 0` when `G < 0`.** -/
theorem V_lam_strictConvexOn (hd : 0 < d) (hX : 0 < X) (hG : b * d < a) :
    StrictConvexOn ℝ (Ici 0) (Vlam a b d X κ) := by
  refine ⟨convex_Ici 0, ?_⟩
  intro x hx y hy hxy w v hw hv hwv
  have hx' : 0 < d + x := by have : (0:ℝ) ≤ x := hx; linarith
  have hy' : 0 < d + y := by have : (0:ℝ) ≤ y := hy; linarith
  have hpq : d + x ≠ d + y := fun h => hxy (by linarith)
  have hconv := inv_strict_convex hx' hy' hpq hw hv hwv
  have hcombo := A_eff_combo (a := a) (b := b) hx' hy' hw hv hwv
  have hpos : 0 < w * ((a + x * b) / (d + x)) + v * ((a + y * b) / (d + y))
      - (a + (w * x + v * y) * b) / (d + (w * x + v * y)) := by
    rw [hcombo]; exact mul_pos_of_neg_of_neg (by linarith) (by linarith)
  simp only [smul_eq_mul, Vlam]
  have key : w * ((a + x * b) / (d + x) * X - κ) + v * ((a + y * b) / (d + y) * X - κ)
      - ((a + (w * x + v * y) * b) / (d + (w * x + v * y)) * X - κ)
      = X * (w * ((a + x * b) / (d + x)) + v * ((a + y * b) / (d + y))
          - (a + (w * x + v * y) * b) / (d + (w * x + v * y))) := by
    linear_combination (-κ) * hwv
  linarith [mul_pos hX hpos]

/-! ## The faith gap at monopoly shares and the threshold `φ̲` -/

/-- The faith gap `G = Π_H(r-μ_L) - Π_L` at monopoly shares. -/
noncomputable def faithGap (r μL μH α K φ : ℝ) : ℝ :=
  (φ * K) ^ α / (r - μH) * (r - μL) - ((1 - φ) * K) ^ α

/-- `G` has the sign of `(φ/(1-φ))^α - q`, `q = (r-μ_H)/(r-μ_L)`. -/
lemma faithGap_eq {r μL μH α K φ : ℝ} (hK : 0 < K) (hφ0 : 0 < φ) (hφ1 : φ < 1)
    (hH : 0 < r - μH) (hL : 0 < r - μL) :
    faithGap r μL μH α K φ
      = ((1 - φ) * K) ^ α * (r - μL) / (r - μH)
          * ((φ / (1 - φ)) ^ α - (r - μH) / (r - μL)) := by
  have h1φ : 0 < 1 - φ := by linarith
  have hp : 0 < (1 - φ) ^ α := Real.rpow_pos_of_pos h1φ _
  unfold faithGap
  rw [Real.mul_rpow hφ0.le hK.le, Real.mul_rpow h1φ.le hK.le,
    Real.div_rpow hφ0.le h1φ.le]
  have := ne_of_gt hp; have := ne_of_gt hH; have := ne_of_gt hL
  field_simp

/-- **`G > 0 ⟺ φ > φ̲`** (faith condition at monopoly shares). -/
theorem faithGap_pos_iff {r μL μH α K φ : ℝ} (hK : 0 < K) (hφ0 : 0 < φ) (hφ1 : φ < 1)
    (hα : 0 < α) (hH : 0 < r - μH) (hL : 0 < r - μL) :
    0 < faithGap r μL μH α K φ ↔ phiUnder ((r - μH) / (r - μL)) α < φ := by
  have hq : 0 < (r - μH) / (r - μL) := div_pos hH hL
  have h1φ : 0 < 1 - φ := by linarith
  have hc : 0 < ((1 - φ) * K) ^ α * (r - μL) / (r - μH) :=
    div_pos (mul_pos (Real.rpow_pos_of_pos (mul_pos h1φ hK) _) hL) hH
  rw [faithGap_eq hK hφ0 hφ1 hH hL]
  have hmono := oddsPow_strictMonoOn hα
  have hmem := phiUnder_mem (α := α) hq
  have hthr := oddsPow_phiUnder hq hα
  constructor
  · intro h
    have h' : (r - μH) / (r - μL) < (φ / (1 - φ)) ^ α := by
      by_contra hc'; nlinarith [not_lt.mp hc']
    rw [← hthr] at h'
    exact (hmono.lt_iff_lt hmem ⟨hφ0, hφ1⟩).mp h'
  · intro h
    have h' := hmono hmem ⟨hφ0, hφ1⟩ h
    simp only at h'
    rw [hthr] at h'
    exact mul_pos hc (by linarith)

/-- **`G < 0 ⟺ φ < φ̲`.** -/
theorem faithGap_neg_iff {r μL μH α K φ : ℝ} (hK : 0 < K) (hφ0 : 0 < φ) (hφ1 : φ < 1)
    (hα : 0 < α) (hH : 0 < r - μH) (hL : 0 < r - μL) :
    faithGap r μL μH α K φ < 0 ↔ φ < phiUnder ((r - μH) / (r - μL)) α := by
  have hq : 0 < (r - μH) / (r - μL) := div_pos hH hL
  have h1φ : 0 < 1 - φ := by linarith
  have hc : 0 < ((1 - φ) * K) ^ α * (r - μL) / (r - μH) :=
    div_pos (mul_pos (Real.rpow_pos_of_pos (mul_pos h1φ hK) _) hL) hH
  rw [faithGap_eq hK hφ0 hφ1 hH hL]
  have hmono := oddsPow_strictMonoOn hα
  have hmem := phiUnder_mem (α := α) hq
  have hthr := oddsPow_phiUnder hq hα
  constructor
  · intro h
    have h' : (φ / (1 - φ)) ^ α < (r - μH) / (r - μL) := by
      by_contra hc'; nlinarith [not_lt.mp hc']
    rw [← hthr] at h'
    exact (hmono.lt_iff_lt ⟨hφ0, hφ1⟩ hmem).mp h'
  · intro h
    have h' := hmono ⟨hφ0, hφ1⟩ hmem h
    simp only at h'
    rw [hthr] at h'
    exact mul_neg_of_pos_of_neg hc (by linarith)

/-- **Corollary 1(i).**  At monopoly shares, with `a = [(1-φ)K]^α`,
`b = (φK)^α/(r-μ_H)`, `d = r-μ_L`, `X > 0`: the going-concern value is strictly
increasing and strictly concave in `λ` on `λ ≥ 0` if and only if `φ > φ̲`. -/
theorem corollary1_i {r μL μH α K φ X κ : ℝ} (hK : 0 < K) (hφ0 : 0 < φ) (hφ1 : φ < 1)
    (hα : 0 < α) (hH : 0 < r - μH) (hL : 0 < r - μL) (hX : 0 < X) :
    (StrictMonoOn (Vlam (((1 - φ) * K) ^ α) ((φ * K) ^ α / (r - μH)) (r - μL) X κ) (Ici 0)
      ∧ StrictConcaveOn ℝ (Ici 0)
          (Vlam (((1 - φ) * K) ^ α) ((φ * K) ^ α / (r - μH)) (r - μL) X κ))
      ↔ phiUnder ((r - μH) / (r - μL)) α < φ := by
  rw [← faithGap_pos_iff hK hφ0 hφ1 hα hH hL]
  unfold faithGap
  constructor
  · rintro ⟨hmono, -⟩
    by_contra hG
    have hG' := not_lt.mp hG
    have h0 : (0:ℝ) ∈ Ici (0:ℝ) := Set.self_mem_Ici
    have h1 : (1:ℝ) ∈ Ici (0:ℝ) := Set.mem_Ici.mpr zero_le_one
    have hlt := hmono h0 h1 zero_lt_one
    rcases hG'.lt_or_eq with hneg | heq
    · have := V_lam_strictAntiOn (a := ((1 - φ) * K) ^ α) (b := (φ * K) ^ α / (r - μH))
        (κ := κ) hL hX (by linarith) h0 h1 zero_lt_one
      linarith
    · have e0 := V_lam_const (a := ((1 - φ) * K) ^ α) (b := (φ * K) ^ α / (r - μH))
        (X := X) (κ := κ) hL (by linarith) (le_refl (0:ℝ))
      have e1 := V_lam_const (a := ((1 - φ) * K) ^ α) (b := (φ * K) ^ α / (r - μH))
        (X := X) (κ := κ) hL (by linarith) (zero_le_one' ℝ)
      linarith
  · intro hG
    exact ⟨V_lam_strictMonoOn hL hX (by linarith), V_lam_strictConcaveOn hL hX (by linarith)⟩

/-! ## Part (ii): the news asymmetry -/

/-- **News identity.**  For `0 < h < Δ = d+λ`, the loss from bad news exceeds the
gain from good news of the same size by `2h²XG/(Δ(Δ-h)(Δ+h))`. -/
theorem news_asymmetry {lam h : ℝ} (hh : 0 < h) (hhΔ : h < d + lam) :
    (Vlam a b d X κ lam - Vlam a b d X κ (lam - h))
        - (Vlam a b d X κ (lam + h) - Vlam a b d X κ lam)
      = 2 * h ^ 2 * X * (b * d - a)
          / ((d + lam) * (d + lam - h) * (d + lam + h)) := by
  have h1 : d + lam ≠ 0 := by linarith
  have h2 : d + (lam - h) ≠ 0 := by linarith
  have h3 : d + (lam + h) ≠ 0 := by linarith
  have h2' : d + lam - h ≠ 0 := by linarith
  have h3' : d + lam + h ≠ 0 := by linarith
  unfold Vlam
  field_simp
  ring

/-- **The asymmetry is positive iff `G > 0`** (for `X > 0`). -/
theorem news_asymmetry_pos_iff {lam h : ℝ} (hX : 0 < X) (hh : 0 < h) (hhΔ : h < d + lam) :
    0 < (Vlam a b d X κ lam - Vlam a b d X κ (lam - h))
        - (Vlam a b d X κ (lam + h) - Vlam a b d X κ lam) ↔ a < b * d := by
  rw [news_asymmetry hh hhΔ]
  have hden : 0 < (d + lam) * (d + lam - h) * (d + lam + h) := by
    have : 0 < d + lam - h := by linarith
    have : 0 < d + lam + h := by linarith
    have : 0 < d + lam := by linarith
    positivity
  rw [div_pos_iff_of_pos_right hden]
  have hc : 0 < 2 * h ^ 2 * X := by positivity
  constructor
  · intro hpos
    by_contra hc'
    nlinarith [not_lt.mp hc']
  · intro hG
    exact mul_pos hc (by linarith)

/-! ## Part (iii): monotonicity in `φ` -/

/-- **`∂G/∂φ = α[Π_H(r-μ_L)/φ + Π_L/(1-φ)]`** at monopoly shares. -/
theorem hasDerivAt_faithGap_phi {r μL μH α K φ : ℝ} (hK : 0 < K) (hφ0 : 0 < φ)
    (hφ1 : φ < 1) :
    HasDerivAt (faithGap r μL μH α K)
      (α * ((φ * K) ^ α / (r - μH) * (r - μL) / φ + ((1 - φ) * K) ^ α / (1 - φ))) φ := by
  have h1φ : 0 < 1 - φ := by linarith
  have hu : HasDerivAt (fun x => x * K) K φ := by
    simpa using (hasDerivAt_id φ).mul_const K
  have hw : HasDerivAt (fun x => (1 - x) * K) (-K) φ := by
    simpa using ((hasDerivAt_id φ).const_sub 1).mul_const K
  have hφK := hu.rpow_const (p := α) (Or.inl (ne_of_gt (mul_pos hφ0 hK)))
  have hH := (hφK.div_const (r - μH)).mul_const (r - μL)
  have hLd := hw.rpow_const (p := α) (Or.inl (ne_of_gt (mul_pos h1φ hK)))
  have h := hH.sub hLd
  refine h.congr_deriv ?_
  have e1 : (φ * K) ^ (α - 1) = (φ * K) ^ α / (φ * K) :=
    Real.rpow_sub_one (ne_of_gt (mul_pos hφ0 hK)) α
  have e2 : ((1 - φ) * K) ^ (α - 1) = ((1 - φ) * K) ^ α / ((1 - φ) * K) :=
    Real.rpow_sub_one (ne_of_gt (mul_pos h1φ hK)) α
  rw [e1, e2]
  have := ne_of_gt hK; have := ne_of_gt hφ0; have := ne_of_gt h1φ
  field_simp
  ring

/-- **`∂G/∂φ > 0`.** -/
theorem faithGap_deriv_pos {r μL μH α K φ : ℝ} (hK : 0 < K) (hφ0 : 0 < φ) (hφ1 : φ < 1)
    (hα : 0 < α) (hH : 0 < r - μH) (hL : 0 < r - μL) :
    0 < α * ((φ * K) ^ α / (r - μH) * (r - μL) / φ + ((1 - φ) * K) ^ α / (1 - φ)) := by
  have h1φ : 0 < 1 - φ := by linarith
  have := Real.rpow_pos_of_pos (mul_pos hφ0 hK) α
  have := Real.rpow_pos_of_pos (mul_pos h1φ hK) α
  positivity

/-- **`G` is strictly increasing in `φ` on `(0,1)`**, so `V' = XG/Δ²`,
`|V''| = 2XG/Δ³` (where `G > 0`) and the news difference of part (ii) all rise with
`φ` at given `(λ, K, X)`. -/
theorem faithGap_strictMonoOn {r μL μH α K : ℝ} (hK : 0 < K) (hα : 0 < α)
    (hH : 0 < r - μH) (hL : 0 < r - μL) :
    StrictMonoOn (faithGap r μL μH α K) (Ioo 0 1) := by
  apply strictMonoOn_of_deriv_pos (convex_Ioo 0 1)
  · intro x hx
    exact (hasDerivAt_faithGap_phi hK hx.1 hx.2).continuousAt.continuousWithinAt
  · intro x hx
    rw [interior_Ioo] at hx
    rw [(hasDerivAt_faithGap_phi hK hx.1 hx.2).deriv]
    exact faithGap_deriv_pos hK hx.1 hx.2 hα hH hL

/-- **Semi-elasticity of `A_eff` in `λ` in terms of `ρ = b/a`:**
`(bd - a)/((a+λb)(d+λ)) = (ρd - 1)/((1+λρ)(d+λ))`. -/
theorem semiElasticity_eq {lam : ℝ} (ha : 0 < a) (hden : 0 < a + lam * b)
    (hdl : 0 < d + lam) :
    (b * d - a) / ((a + lam * b) * (d + lam))
      = (b / a * d - 1) / ((1 + lam * (b / a)) * (d + lam)) := by
  have h1 : 1 + lam * (b / a) = (a + lam * b) / a := by field_simp
  rw [h1]
  have := ne_of_gt ha; have := ne_of_gt hden; have := ne_of_gt hdl
  field_simp

/-- **The semi-elasticity is strictly increasing in `ρ`** (for `λ ≥ 0`, `ρ ≥ 0`). -/
theorem semiElasticity_lt {lam ρ₁ ρ₂ : ℝ} (hd : 0 < d) (hlam : 0 ≤ lam) (hρ₁ : 0 ≤ ρ₁)
    (hlt : ρ₁ < ρ₂) :
    (ρ₁ * d - 1) / ((1 + lam * ρ₁) * (d + lam)) < (ρ₂ * d - 1) / ((1 + lam * ρ₂) * (d + lam)) := by
  have hdl : 0 < d + lam := by linarith
  have h1 : 0 < 1 + lam * ρ₁ := by nlinarith
  have h2 : 0 < 1 + lam * ρ₂ := by nlinarith
  rw [div_lt_div_iff₀ (mul_pos h1 hdl) (mul_pos h2 hdl)]
  nlinarith [mul_pos (sub_pos.mpr hlt) hdl, mul_pos (mul_pos (sub_pos.mpr hlt) hdl) hdl]

/-- **`ρ = Π_H/Π_L` is strictly increasing in `φ`** at monopoly shares. -/
theorem ratio_strictMonoOn {r μH α K : ℝ} (hK : 0 < K) (hα : 0 < α) (hH : 0 < r - μH) :
    StrictMonoOn (fun φ : ℝ => (φ * K) ^ α / (r - μH) / ((1 - φ) * K) ^ α) (Ioo 0 1) := by
  intro x hx y hy hxy
  have e : ∀ φ : ℝ, 0 < φ → φ < 1 →
      (φ * K) ^ α / (r - μH) / ((1 - φ) * K) ^ α = (φ / (1 - φ)) ^ α / (r - μH) := by
    intro φ h0 h1
    have h1φ : 0 < 1 - φ := by linarith
    rw [Real.mul_rpow h0.le hK.le, Real.mul_rpow h1φ.le hK.le, Real.div_rpow h0.le h1φ.le]
    have := ne_of_gt (Real.rpow_pos_of_pos hK α)
    have := ne_of_gt (Real.rpow_pos_of_pos h1φ α)
    have := ne_of_gt hH
    field_simp
  simp only
  rw [e x hx.1 hx.2, e y hy.1 hy.2]
  exact div_lt_div_of_pos_right (oddsPow_strictMonoOn hα hx hy hxy) hH

end AILab
