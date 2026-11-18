import AILabProofs.Proposition1

set_option linter.style.header false

/-!
# Post-switch capacity `K_H*`: positivity and global optimality (Proposition 1(ii))

`Proposition1.lean` shows that the capacity first-order condition (`eq-foc-K`) is
equivalent to the closed form for `K^{γ-1}` (`K_foc`).  This file adds what that
equivalence leaves open (`paper/_appendix.qmd`, Proof of Proposition 1, Step 4, and
`paper/_model.qmd`, eq-K-H):

* `capRoot_pos` : under the two bounds of (A2), `β-1 < αβ < γ(β-1)`, the right-hand
  side of the closed form is strictly positive, so `K_H* = capRoot^{1/(γ-1)}` is a
  well-defined positive capacity (`KHstar_pos`, `KHstar_rpow`, `KHstar_foc`).
* `foc_numerator_eq`, `foc_numerator_pos_iff`, `foc_numerator_neg_iff` : the
  numerator of the logarithmic derivative of the reduced capacity objective,
  `αβΘ(K) - (β-1)KΘ'(K)`, is positive below `K_H*` and negative above it.
* `hasDerivAt_logCapObj` : the logarithmic derivative itself.
* `capObj_lt_capObj_KHstar` : the reduced capacity objective of Step 3,
  `h(K) = (aK^α)^β / Θ(K)^{β-1}` with `Θ(K) = cK^γ + δK/r`, is strictly smaller at
  every other positive capacity than at `K_H*`.  So `K_H*` is the unique global
  maximiser of `h` on `(0, ∞)`, not only a critical point.

The objective `h` is taken as given (it is Steps 1--3, which rest on value
matching and smooth pasting for a payoff linear in demand); the file says nothing
about the optimality of the stopping rule itself.  Here `β` plays the role of
`β_H > 1` and `a > 0` that of `A_H` (Proposition 1(ii)) or `g(φ)` (the pure-power
approximation).
-/

namespace AILab

open Real Set

/-- Total cost `Θ(K) = c K^γ + δ K / r` (investment outlay plus the present value
of the operating-cost flow). -/
noncomputable def capCost (c δ r γ K : ℝ) : ℝ := c * K ^ γ + δ * K / r

/-- The closed-form value of `K^{γ-1}` at the capacity optimum (`K_foc`). -/
noncomputable def capRoot (c δ r γ β α : ℝ) : ℝ :=
  δ / r * ((β - 1) - α * β) / (c * (α * β - (β - 1) * γ))

/-- The post-switch capacity `K_H* = capRoot^{1/(γ-1)}` (eq-K-H). -/
noncomputable def KHstar (c δ r γ β α : ℝ) : ℝ := capRoot c δ r γ β α ^ (1 / (γ - 1))

/-- The reduced capacity objective `h(K) = (a K^α)^β / Θ(K)^{β-1}` of Step 3. -/
noncomputable def capObj (a c δ r γ β α K : ℝ) : ℝ :=
  (a * K ^ α) ^ β / capCost c δ r γ K ^ (β - 1)

/-- Its logarithm up to the constant `β log a`. -/
noncomputable def logCapObj (c δ r γ β α K : ℝ) : ℝ :=
  α * β * Real.log K - (β - 1) * Real.log (capCost c δ r γ K)

variable {a c δ r γ β α : ℝ}

lemma capCost_pos {K : ℝ} (hc : 0 < c) (hδ : 0 < δ) (hr : 0 < r) (hK : 0 < K) :
    0 < capCost c δ r γ K := by
  unfold capCost
  have := Real.rpow_pos_of_pos hK γ
  positivity

/-- **Positivity of the closed-form right-hand side under (A2).**  With
`β - 1 < αβ` (upper bound of (A2)) and `αβ < γ(β - 1)` (lower bound), both the
numerator and the denominator of `capRoot` are negative. -/
theorem capRoot_pos (hc : 0 < c) (hδ : 0 < δ) (hr : 0 < r)
    (hA2u : β - 1 < α * β) (hA2l : α * β < γ * (β - 1)) :
    0 < capRoot c δ r γ β α := by
  unfold capRoot
  apply div_pos_of_neg_of_neg
  · exact mul_neg_of_pos_of_neg (div_pos hδ hr) (by linarith)
  · exact mul_neg_of_pos_of_neg hc (by linarith)

/-- `K_H* > 0`. -/
theorem KHstar_pos (hc : 0 < c) (hδ : 0 < δ) (hr : 0 < r)
    (hA2u : β - 1 < α * β) (hA2l : α * β < γ * (β - 1)) :
    0 < KHstar c δ r γ β α :=
  Real.rpow_pos_of_pos (capRoot_pos hc hδ hr hA2u hA2l) _

/-- `(K_H*)^{γ-1} = capRoot`. -/
theorem KHstar_rpow (hc : 0 < c) (hδ : 0 < δ) (hr : 0 < r) (hγ : 1 < γ)
    (hA2u : β - 1 < α * β) (hA2l : α * β < γ * (β - 1)) :
    KHstar c δ r γ β α ^ (γ - 1) = capRoot c δ r γ β α := by
  have hu := capRoot_pos hc hδ hr hA2u hA2l
  have hγ1 : γ - 1 ≠ 0 := by linarith
  rw [KHstar, ← Real.rpow_mul hu.le, one_div, inv_mul_cancel₀ hγ1, Real.rpow_one]

/-- **`K_H*` satisfies the capacity first-order condition** (eq-foc-K). -/
theorem KHstar_foc (hc : 0 < c) (hδ : 0 < δ) (hr : 0 < r) (hγ : 1 < γ)
    (hA2u : β - 1 < α * β) (hA2l : α * β < γ * (β - 1)) :
    let K := KHstar c δ r γ β α
    α * β * (c * K ^ γ + δ * K / r) = (β - 1) * K * (c * γ * K ^ (γ - 1) + δ / r) := by
  intro K
  have hden : α * β - (β - 1) * γ ≠ 0 := by intro h; linarith
  exact (K_foc (KHstar_pos hc hδ hr hA2u hA2l) hr hc hden).mpr
    (KHstar_rpow hc hδ hr hγ hA2u hA2l)

/-- **Factorization of the first-order-condition numerator.**
`αβΘ(K) - (β-1)K Θ'(K) = K · c (αβ - (β-1)γ) · (K^{γ-1} - capRoot)`. -/
theorem foc_numerator_eq {K : ℝ} (hK : 0 < K) (hc : 0 < c) (hr : 0 < r)
    (hden : α * β - (β - 1) * γ ≠ 0) :
    α * β * capCost c δ r γ K - (β - 1) * K * (c * γ * K ^ (γ - 1) + δ / r)
      = K * (c * (α * β - (β - 1) * γ)) * (K ^ (γ - 1) - capRoot c δ r γ β α) := by
  have hpow : K ^ γ = K ^ (γ - 1) * K := by
    conv_lhs => rw [show γ = (γ - 1) + 1 by ring]
    rw [Real.rpow_add hK, Real.rpow_one]
  have hcd : c * (α * β - (β - 1) * γ) ≠ 0 := mul_ne_zero (ne_of_gt hc) hden
  have hroot : c * (α * β - (β - 1) * γ) * capRoot c δ r γ β α
      = δ / r * ((β - 1) - α * β) := by
    unfold capRoot; field_simp
  unfold capCost
  rw [hpow]
  linear_combination K * hroot

/-- `K^{γ-1} < (K_H*)^{γ-1}` exactly when `K < K_H*`. -/
lemma rpow_lt_root_iff {K : ℝ} (hK : 0 < K) (hc : 0 < c) (hδ : 0 < δ) (hr : 0 < r)
    (hγ : 1 < γ) (hA2u : β - 1 < α * β) (hA2l : α * β < γ * (β - 1)) :
    K ^ (γ - 1) < capRoot c δ r γ β α ↔ K < KHstar c δ r γ β α := by
  rw [← KHstar_rpow hc hδ hr hγ hA2u hA2l]
  exact Real.rpow_lt_rpow_iff hK.le (KHstar_pos hc hδ hr hA2u hA2l).le (by linarith)

/-- **The first-order-condition numerator is positive below `K_H*`.** -/
theorem foc_numerator_pos_iff {K : ℝ} (hK : 0 < K) (hc : 0 < c) (hδ : 0 < δ) (hr : 0 < r)
    (hγ : 1 < γ) (hA2u : β - 1 < α * β) (hA2l : α * β < γ * (β - 1)) :
    0 < α * β * capCost c δ r γ K - (β - 1) * K * (c * γ * K ^ (γ - 1) + δ / r)
      ↔ K < KHstar c δ r γ β α := by
  have hden : α * β - (β - 1) * γ ≠ 0 := by intro h; linarith
  have hneg : K * (c * (α * β - (β - 1) * γ)) < 0 :=
    mul_neg_of_pos_of_neg hK (mul_neg_of_pos_of_neg hc (by linarith))
  rw [foc_numerator_eq hK hc hr hden, ← rpow_lt_root_iff hK hc hδ hr hγ hA2u hA2l]
  constructor
  · intro h
    by_contra hc'
    have : 0 ≤ K ^ (γ - 1) - capRoot c δ r γ β α := by linarith [not_lt.mp hc']
    nlinarith
  · intro h
    exact mul_pos_of_neg_of_neg hneg (by linarith)

/-- **The first-order-condition numerator is negative above `K_H*`.** -/
theorem foc_numerator_neg_iff {K : ℝ} (hK : 0 < K) (hc : 0 < c) (hδ : 0 < δ) (hr : 0 < r)
    (hγ : 1 < γ) (hA2u : β - 1 < α * β) (hA2l : α * β < γ * (β - 1)) :
    α * β * capCost c δ r γ K - (β - 1) * K * (c * γ * K ^ (γ - 1) + δ / r) < 0
      ↔ KHstar c δ r γ β α < K := by
  have hden : α * β - (β - 1) * γ ≠ 0 := by intro h; linarith
  have hneg : K * (c * (α * β - (β - 1) * γ)) < 0 :=
    mul_neg_of_pos_of_neg hK (mul_neg_of_pos_of_neg hc (by linarith))
  have hKs := KHstar_pos hc hδ hr hA2u hA2l
  have hiff : capRoot c δ r γ β α < K ^ (γ - 1) ↔ KHstar c δ r γ β α < K := by
    rw [← KHstar_rpow hc hδ hr hγ hA2u hA2l]
    exact Real.rpow_lt_rpow_iff hKs.le hK.le (by linarith)
  rw [foc_numerator_eq hK hc hr hden, ← hiff]
  constructor
  · intro h
    by_contra hc'
    have : K ^ (γ - 1) - capRoot c δ r γ β α ≤ 0 := by linarith [not_lt.mp hc']
    nlinarith
  · intro h
    exact mul_neg_of_neg_of_pos hneg (by linarith)

/-- **Logarithmic derivative of the capacity objective.**
`d/dK [αβ log K - (β-1) log Θ(K)] = (αβΘ(K) - (β-1)KΘ'(K)) / (KΘ(K))`. -/
theorem hasDerivAt_logCapObj {K : ℝ} (hK : 0 < K) (hc : 0 < c) (hδ : 0 < δ) (hr : 0 < r) :
    HasDerivAt (logCapObj c δ r γ β α)
      ((α * β * capCost c δ r γ K - (β - 1) * K * (c * γ * K ^ (γ - 1) + δ / r))
        / (K * capCost c δ r γ K)) K := by
  have hΘ := capCost_pos (γ := γ) hc hδ hr hK
  have hΘd : HasDerivAt (capCost c δ r γ) (c * γ * K ^ (γ - 1) + δ / r) K := by
    have h1 : HasDerivAt (fun x => c * x ^ γ) (c * (1 * γ * K ^ (γ - 1))) K :=
      ((hasDerivAt_id K).rpow_const (Or.inl (ne_of_gt hK))).const_mul c
    have h2 : HasDerivAt (fun x => δ * x / r) (δ * 1 / r) K :=
      ((hasDerivAt_id K).const_mul δ).div_const r
    exact (h1.add h2).congr_deriv (by ring)
  have hlogK : HasDerivAt Real.log K⁻¹ K := Real.hasDerivAt_log (ne_of_gt hK)
  have hlogΘ := hΘd.log (ne_of_gt hΘ)
  have h := (hlogK.const_mul (α * β)).sub (hlogΘ.const_mul (β - 1))
  refine h.congr_deriv ?_
  field_simp

/-- **`K_H*` is the unique global maximiser of the logarithmic capacity objective.** -/
theorem logCapObj_lt_KHstar {K : ℝ} (hK : 0 < K) (hc : 0 < c) (hδ : 0 < δ) (hr : 0 < r)
    (hγ : 1 < γ) (hA2u : β - 1 < α * β) (hA2l : α * β < γ * (β - 1))
    (hne : K ≠ KHstar c δ r γ β α) :
    logCapObj c δ r γ β α K < logCapObj c δ r γ β α (KHstar c δ r γ β α) := by
  set Ks := KHstar c δ r γ β α with hKsdef
  have hKs : 0 < Ks := KHstar_pos hc hδ hr hA2u hA2l
  have hder : ∀ x, 0 < x → HasDerivAt (logCapObj c δ r γ β α)
      ((α * β * capCost c δ r γ x - (β - 1) * x * (c * γ * x ^ (γ - 1) + δ / r))
        / (x * capCost c δ r γ x)) x :=
    fun x hx => hasDerivAt_logCapObj hx hc hδ hr
  have hden : ∀ x, 0 < x → 0 < x * capCost c δ r γ x :=
    fun x hx => mul_pos hx (capCost_pos hc hδ hr hx)
  have hcont : ∀ D : Set ℝ, D ⊆ Ioi 0 → ContinuousOn (logCapObj c δ r γ β α) D :=
    fun D hD x hx => (hder x (hD hx)).continuousAt.continuousWithinAt
  rcases lt_or_gt_of_ne hne with hlt | hgt
  · -- increasing on `(0, K_H*]`
    have hmono : StrictMonoOn (logCapObj c δ r γ β α) (Ioc 0 Ks) := by
      apply strictMonoOn_of_deriv_pos (convex_Ioc 0 Ks)
        (hcont _ (fun x hx => hx.1))
      intro x hx
      rw [interior_Ioc] at hx
      rw [(hder x hx.1).deriv]
      exact div_pos ((foc_numerator_pos_iff hx.1 hc hδ hr hγ hA2u hA2l).mpr hx.2)
        (hden x hx.1)
    exact hmono ⟨hK, hlt.le⟩ ⟨hKs, le_refl _⟩ hlt
  · -- decreasing on `[K_H*, ∞)`
    have hanti : StrictAntiOn (logCapObj c δ r γ β α) (Ici Ks) := by
      apply strictAntiOn_of_deriv_neg (convex_Ici Ks)
        (hcont _ (fun x hx => lt_of_lt_of_le hKs hx))
      intro x hx
      rw [interior_Ici] at hx
      have hx0 : 0 < x := lt_trans hKs hx
      rw [(hder x hx0).deriv]
      exact div_neg_of_neg_of_pos
        ((foc_numerator_neg_iff hx0 hc hδ hr hγ hA2u hA2l).mpr hx) (hden x hx0)
    exact hanti (le_refl Ks) (le_of_lt hgt) hgt

/-- `h(K) = a^β · exp(αβ log K - (β-1) log Θ(K))`. -/
lemma capObj_eq_exp {K : ℝ} (ha : 0 < a) (hK : 0 < K) (hc : 0 < c) (hδ : 0 < δ)
    (hr : 0 < r) :
    capObj a c δ r γ β α K = a ^ β * Real.exp (logCapObj c δ r γ β α K) := by
  have hΘ := capCost_pos (γ := γ) hc hδ hr hK
  unfold capObj logCapObj
  rw [Real.mul_rpow ha.le (Real.rpow_nonneg hK.le _), ← Real.rpow_mul hK.le,
    Real.rpow_def_of_pos hK, Real.rpow_def_of_pos hΘ, Real.exp_sub, mul_div_assoc]
  congr 2 <;> ring_nf

/-- **`K_H*` is the unique global maximiser of the reduced capacity objective**
(Proposition 1(ii), Step 4).  Under (A1)--(A2) (`c, δ, r > 0`, `γ > 1`,
`β-1 < αβ < γ(β-1)`), every other positive capacity gives a strictly smaller
value of `h(K) = (aK^α)^β/Θ(K)^{β-1}`. -/
theorem capObj_lt_capObj_KHstar {K : ℝ} (ha : 0 < a) (hK : 0 < K) (hc : 0 < c)
    (hδ : 0 < δ) (hr : 0 < r) (hγ : 1 < γ)
    (hA2u : β - 1 < α * β) (hA2l : α * β < γ * (β - 1))
    (hne : K ≠ KHstar c δ r γ β α) :
    capObj a c δ r γ β α K < capObj a c δ r γ β α (KHstar c δ r γ β α) := by
  have hKs := KHstar_pos hc hδ hr hA2u hA2l
  rw [capObj_eq_exp ha hK hc hδ hr, capObj_eq_exp ha hKs hc hδ hr]
  exact mul_lt_mul_of_pos_left
    (Real.exp_lt_exp.mpr (logCapObj_lt_KHstar hK hc hδ hr hγ hA2u hA2l hne))
    (Real.rpow_pos_of_pos ha β)

end AILab
