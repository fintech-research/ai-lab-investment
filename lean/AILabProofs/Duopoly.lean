import AILabProofs.Basic

set_option linter.style.header false

/-!
# Proposition 3 — the duopoly: contest algebra, the follower, values before entry

This file verifies the analytical ingredients of Proposition 3 (`paper/_appendix.qmd`,
"Proof of Proposition 3", and `paper/_model.qmd`, "Entry equilibrium") and two lemmas
about the nested pure-power game of Internet Appendix B.

* `contest_share_scale_invariant`, `share_role_invariant`, `hasDerivAt_tullock` :
  Proposition 3(ii).  At a common allocation the contest shares coincide across
  regimes and the contest derivative factors as `α u^{α-1} s(2-s)`, so the
  allocation condition is the single firm's: a common allocation is a critical
  point iff it is `φ*`.  This is a critical-point statement; the equilibrium
  allocation `φ_L < φ*` is numerical.
* `tullock_elasticity`, `followerFoc_iff`, `followerFocD_strictAntiOn`,
  `followerFoc_unique` : Proposition 3(i).  The follower's capacity condition
  eq-follower-foc has at most one root.  Existence of the root is not formalized.
* `follow_sub_lead`, `follower_condition_of_leader`, `lead_value_ge_payoff` : the
  algebra of eq-values-before-entry used in the no-deviation argument of
  Proposition 3(iii).  The values themselves, the maximization defining `X_L` and
  every number are numerical.
* `A_eff_follower_separable` : the separable reduction of the follower's coefficient
  at a common allocation (nested pure-power game, Internet Appendix B).
* `preemption_exists`, `unique_crossing` : generic intermediate-value and
  strict-concavity lemmas.  They concern only the rent-equalization trigger of the
  nested pure-power game, whose leader scale is fixed (`unique_crossing` only at zero
  leverage and without the option to stop, a case no current paper statement uses).
  Neither applies to `X_L` or `X_P` of Proposition 3(iii), which are numerical findings.
-/

namespace AILab

open Real

/-- **Tullock share is scale-invariant.**  Scaling both firms' capacities by a
common factor `t > 0` leaves the contest share unchanged. -/
theorem contest_share_scale_invariant {t Ki Kj α : ℝ}
    (ht : 0 < t) (hKi : 0 < Ki) (hKj : 0 < Kj) :
    (t * Ki) ^ α / ((t * Ki) ^ α + (t * Kj) ^ α) = Ki ^ α / (Ki ^ α + Kj ^ α) := by
  rw [Real.mul_rpow ht.le hKi.le, Real.mul_rpow ht.le hKj.le, ← mul_add,
      mul_div_mul_left _ _ (ne_of_gt (Real.rpow_pos_of_pos ht α))]

/-- **Role-invariance of the contest share.**  At a common training fraction `φ`,
the inference-regime share (capacities scaled by `1-φ`) equals the training-regime
share (capacities scaled by `φ`); both reduce to `K_i^α/(K_i^α+K_j^α)`. -/
theorem share_role_invariant {φ Ki Kj α : ℝ}
    (hφ0 : 0 < φ) (hφ1 : φ < 1) (hKi : 0 < Ki) (hKj : 0 < Kj) :
    ((1 - φ) * Ki) ^ α / (((1 - φ) * Ki) ^ α + ((1 - φ) * Kj) ^ α)
      = (φ * Ki) ^ α / ((φ * Ki) ^ α + (φ * Kj) ^ α) := by
  rw [contest_share_scale_invariant (by linarith) hKi hKj,
      contest_share_scale_invariant hφ0 hKi hKj]

/-- **Separable reduction of the follower coefficient.**  At a common allocation the
follower's effective revenue coefficient factors into an allocation term
`g(φ) = w_L(1-φ)^α + w_H φ^α` and a capacity term `K_F^{2α}/(K_F^α+K_L^α)`
(nested pure-power game, Internet Appendix B).  Proposition 3(i) is the same algebra
with all capacity in training. -/
theorem A_eff_follower_separable {wL wH φ KF KL α : ℝ}
    (hφ0 : 0 < φ) (hφ1 : φ < 1) (hKF : 0 < KF) (hKL : 0 < KL) :
    wL * ((1 - φ) * KF) ^ α * (((1 - φ) * KF) ^ α / (((1 - φ) * KF) ^ α + ((1 - φ) * KL) ^ α))
      + wH * (φ * KF) ^ α * ((φ * KF) ^ α / ((φ * KF) ^ α + (φ * KL) ^ α))
      = (wL * (1 - φ) ^ α + wH * φ ^ α) * (KF ^ (2 * α) / (KF ^ α + KL ^ α)) := by
  have h1mφ : (0 : ℝ) < 1 - φ := by linarith
  have hi : 0 < KF ^ α := Real.rpow_pos_of_pos hKF _
  have hl : 0 < KL ^ α := Real.rpow_pos_of_pos hKL _
  have hsum : KF ^ α + KL ^ α ≠ 0 := by positivity
  rw [contest_share_scale_invariant h1mφ hKF hKL,
      contest_share_scale_invariant hφ0 hKF hKL,
      Real.mul_rpow h1mφ.le hKF.le, Real.mul_rpow hφ0.le hKF.le,
      show KF ^ (2 * α) = KF ^ α * KF ^ α by rw [two_mul, Real.rpow_add hKF]]
  field_simp

/-- **Rent equalization by the intermediate value theorem** (nested pure-power game,
Internet Appendix B).  Where the leader's value `L` starts below the follower's value
`F` (`L a < F a`) and ends above it (`F b < L b`), with both continuous, `L = F` at
some `X_P ∈ [a, b]`.  In the nested game the fixed leader scale makes `L < F` near
the origin; the upper endpoint sign is computed.  The lemma does not apply to the
exact game of Proposition 3, where both values vanish at the origin. -/
theorem preemption_exists {L F : ℝ → ℝ} {a b : ℝ} (hab : a ≤ b)
    (hL : ContinuousOn L (Set.Icc a b)) (hF : ContinuousOn F (Set.Icc a b))
    (ha : L a < F a) (hb : F b < L b) :
    ∃ X ∈ Set.Icc a b, L X = F X := by
  have hg : ContinuousOn (fun x => L x - F x) (Set.Icc a b) := hL.sub hF
  have h0 : (0 : ℝ) ∈ Set.Icc ((fun x => L x - F x) a) ((fun x => L x - F x) b) := by
    rw [Set.mem_Icc]; refine ⟨?_, ?_⟩ <;> dsimp only <;> linarith
  obtain ⟨X, hX, hXeq⟩ := intermediate_value_Icc hab hg h0
  refine ⟨X, hX, ?_⟩
  have : L X - F X = 0 := hXeq
  linarith

/-- **Single-crossing uniqueness** (generic).  A continuous, *strictly concave*
function with `G a < 0 < G b` has a **unique** zero in `(a, b)`.  It was written for
the nested pure-power game at zero leverage without the option to stop, where the
leader–follower gap is linear minus the convex `X^{β_H}` term; with the option to stop
(the paper's convention since issue #177) and in the exact game the paper does not
supply the concavity hypothesis, and no current paper statement uses the lemma. -/
theorem unique_crossing {G : ℝ → ℝ} {a b : ℝ} (hab : a < b)
    (hcont : ContinuousOn G (Set.Icc a b))
    (hconc : StrictConcaveOn ℝ (Set.Icc a b) G)
    (hGa : G a < 0) (hGb : 0 < G b) :
    ∃! x, x ∈ Set.Ioo a b ∧ G x = 0 := by
  -- Two zeros `p < q < b` are impossible: strict concavity forces `G q > 0`.
  have key : ∀ p q : ℝ, a < p → p < q → q < b → G p = 0 → G q ≠ 0 := by
    intro p q hap hpq hqb hGp hGq
    have hbp : 0 < b - p := by linarith
    have hbpne : b - p ≠ 0 := ne_of_gt hbp
    set w := (b - q) / (b - p) with hwdef
    have hw0 : 0 < w := by rw [hwdef]; exact div_pos (by linarith) hbp
    have hwlt1 : w < 1 := by rw [hwdef, div_lt_one hbp]; linarith
    have hw1 : 0 < 1 - w := by linarith
    have hsum : w + (1 - w) = 1 := by ring
    have hcomb : w * p + (1 - w) * b = q := by rw [hwdef]; field_simp; ring
    have hpmem : p ∈ Set.Icc a b := ⟨hap.le, by linarith⟩
    have hbmem : b ∈ Set.Icc a b := ⟨by linarith, le_refl b⟩
    have hstrict := hconc.2 hpmem hbmem (ne_of_lt (by linarith : p < b)) hw0 hw1 hsum
    simp only [smul_eq_mul] at hstrict
    rw [hcomb, hGp, hGq] at hstrict
    nlinarith [mul_pos hw1 hGb, hstrict]
  -- Existence via the intermediate value theorem.
  have h0 : (0 : ℝ) ∈ Set.Icc (G a) (G b) := ⟨hGa.le, hGb.le⟩
  obtain ⟨x, hxmem, hxeq⟩ := intermediate_value_Icc hab.le hcont h0
  have hxa : a < x := by
    rcases eq_or_lt_of_le hxmem.1 with h | h
    · exfalso; rw [← h] at hxeq; linarith
    · exact h
  have hxb : x < b := by
    rcases eq_or_lt_of_le hxmem.2 with h | h
    · exfalso; rw [h] at hxeq; linarith
    · exact h
  refine ⟨x, ⟨⟨hxa, hxb⟩, hxeq⟩, ?_⟩
  rintro y ⟨⟨hya, hyb⟩, hyeq⟩
  rcases lt_trichotomy y x with h | h | h
  · exact absurd hxeq (key y x hya h hxb hyeq)
  · exact h
  · exact absurd hyeq (key x y hxa h hyb hxeq)

/-- **Tullock contest derivative factorization** (Proposition 3(ii); with
`tullock_elasticity`, the elasticity `α(2-s_F)` of Proposition 3(i)).  For the
contest payoff `f(u) = u^{2α}/(u^α + c)` (rival measure `c = ū^α` fixed), the
marginal revenue factors as `f'(u) = α u^{α-1}·s(2-s)`, the standalone marginal
revenue `α u^{α-1}` times the contest multiplier `s(2-s)`, with `s = u^α/(u^α+c)`.
The multiplier is what cancels in the follower's allocation FOC. -/
theorem hasDerivAt_tullock {u c α : ℝ} (hu : 0 < u) (hc : 0 < c) :
    HasDerivAt (fun x => x ^ (2 * α) / (x ^ α + c))
      (α * u ^ (α - 1) * ((u ^ α / (u ^ α + c)) * (2 - u ^ α / (u ^ α + c)))) u := by
  have hune : u ≠ 0 := ne_of_gt hu
  have hp : HasDerivAt (fun x => x ^ (2 * α)) (1 * (2 * α) * u ^ (2 * α - 1)) u :=
    (hasDerivAt_id u).rpow_const (Or.inl hune)
  have hq : HasDerivAt (fun x => x ^ α + c) (1 * α * u ^ (α - 1)) u :=
    ((hasDerivAt_id u).rpow_const (Or.inl hune)).add_const c
  have hqu : u ^ α + c ≠ 0 := by positivity
  have hEq : α * u ^ (α - 1) * ((u ^ α / (u ^ α + c)) * (2 - u ^ α / (u ^ α + c)))
      = (1 * (2 * α) * u ^ (2 * α - 1) * (u ^ α + c)
          - u ^ (2 * α) * (1 * α * u ^ (α - 1))) / (u ^ α + c) ^ 2 := by
    rw [show u ^ (2 * α - 1) = u ^ α * u ^ (α - 1) by
          rw [← Real.rpow_add hu]; congr 1; ring,
        show u ^ (2 * α) = u ^ α * u ^ α by
          rw [← Real.rpow_add hu]; congr 1; ring]
    field_simp
  rw [hEq]
  exact hp.div hq hqu

/-! ## The follower after the switch (Proposition 3(i), eq-follower-foc)

After the switch the follower trains with all its capacity against a leader with
training capacity `T_L`.  Its revenue coefficient is `A_H K^α s_F(K)` with
`s_F(K) = K^α/(K^α + T_L^α)`, whose elasticity in `K` is `α(2 - s_F)`
(`tullock_elasticity`), and its total cost is `Θ(K) = δK/r + cK^γ` (with `c` the
leverage-adjusted cost coefficient `c[1 - ℓ(1 - r_c/r)]` in the nested game of
Internet Appendix B).  The log-derivative of its option coefficient is
`D(K) = αβ(2 - s_F(K)) - (β-1)·KΘ'(K)/Θ(K)`; `followerFoc_iff` shows that eq-follower-foc
is `D(K) = 0`, and `followerFocD_strictAntiOn` that `D` is strictly decreasing, so the
condition has at most one root (`followerFoc_unique`).  That a root exists (the signs
of `D` at the two ends of `(0, ∞)`, which give the two conditions of the statement)
is not formalized. -/

section Follower

open Set

/-- The follower's contest share `s_F(K) = K^α/(K^α + T^α)`. -/
noncomputable def followerShare (α T K : ℝ) : ℝ := K ^ α / (K ^ α + T ^ α)

/-- The cost elasticity `KΘ'(K)/Θ(K)` for `Θ(K) = δK/r + cK^γ`. -/
noncomputable def costElasticity (c δ r γ K : ℝ) : ℝ :=
  (δ * K / r + γ * (c * K ^ γ)) / (δ * K / r + c * K ^ γ)

/-- The log-derivative of the follower's option coefficient. -/
noncomputable def followerFocD (α β γ c δ r T K : ℝ) : ℝ :=
  α * β * (2 - followerShare α T K) - (β - 1) * costElasticity c δ r γ K

/-- **Elasticity of the contest revenue:** `u f'(u)/f(u) = α(2 - s)` for
`f(u) = u^{2α}/(u^α + c)`, with `f'` from `hasDerivAt_tullock`. -/
theorem tullock_elasticity {u c α : ℝ} (hu : 0 < u) (hc : 0 < c) :
    u * (α * u ^ (α - 1) * ((u ^ α / (u ^ α + c)) * (2 - u ^ α / (u ^ α + c))))
        / (u ^ (2 * α) / (u ^ α + c))
      = α * (2 - u ^ α / (u ^ α + c)) := by
  have hua : 0 < u ^ α := Real.rpow_pos_of_pos hu α
  have e1 : u * u ^ (α - 1) = u ^ α := by
    conv_rhs => rw [show α = 1 + (α - 1) by ring]
    rw [Real.rpow_add hu, Real.rpow_one]
  have e2 : u ^ (2 * α) = u ^ α * u ^ α := by
    rw [← Real.rpow_add hu]; congr 1; ring
  have hs : u ^ α + c ≠ 0 := by positivity
  rw [e2, show u * (α * u ^ (α - 1) * ((u ^ α / (u ^ α + c)) * (2 - u ^ α / (u ^ α + c))))
      = α * (u * u ^ (α - 1)) * ((u ^ α / (u ^ α + c)) * (2 - u ^ α / (u ^ α + c))) by ring,
    e1]
  have := ne_of_gt hua
  field_simp

/-- **eq-follower-foc is `D(K) = 0`.**  For `K > 0` and `Θ(K) > 0`,
`αβ(2 - s_F)Θ = (β-1)KΘ'` iff `D(K) = 0`. -/
theorem followerFoc_iff {α β γ c δ r T K : ℝ} (hK : 0 < K) (hc : 0 < c) (hδ : 0 < δ)
    (hr : 0 < r) :
    α * β * (2 - followerShare α T K) * (δ * K / r + c * K ^ γ)
        = (β - 1) * K * (δ / r + c * γ * K ^ (γ - 1))
      ↔ followerFocD α β γ c δ r T K = 0 := by
  have hΘ : 0 < δ * K / r + c * K ^ γ := by
    have := Real.rpow_pos_of_pos hK γ; positivity
  have e : K * (δ / r + c * γ * K ^ (γ - 1)) = δ * K / r + γ * (c * K ^ γ) := by
    have : K * K ^ (γ - 1) = K ^ γ := by
      conv_rhs => rw [show γ = 1 + (γ - 1) by ring]
      rw [Real.rpow_add hK, Real.rpow_one]
    linear_combination (c * γ) * this
  unfold followerFocD costElasticity
  rw [mul_assoc (β - 1) K, e, sub_eq_zero, ← mul_div_assoc, eq_div_iff (ne_of_gt hΘ)]

/-- The follower's share is strictly increasing in its capacity. -/
theorem followerShare_strictMonoOn {α T : ℝ} (hα : 0 < α) (hT : 0 < T) :
    StrictMonoOn (followerShare α T) (Ioi 0) := by
  intro x hx y hy hxy
  have hTα : 0 < T ^ α := Real.rpow_pos_of_pos hT α
  have hxα : 0 < x ^ α := Real.rpow_pos_of_pos hx α
  have hyα : 0 < y ^ α := Real.rpow_pos_of_pos hy α
  have hlt : x ^ α < y ^ α := Real.rpow_lt_rpow (le_of_lt hx) hxy hα
  unfold followerShare
  rw [div_lt_div_iff₀ (by positivity) (by positivity)]
  nlinarith [mul_pos hTα (sub_pos.mpr hlt)]

/-- The cost elasticity `KΘ'/Θ` is strictly increasing in `K` (for `γ > 1`). -/
theorem costElasticity_strictMonoOn {c δ r γ : ℝ} (hc : 0 < c) (hδ : 0 < δ) (hr : 0 < r)
    (hγ : 1 < γ) :
    StrictMonoOn (costElasticity c δ r γ) (Ioi 0) := by
  intro x hx y hy hxy
  have hx0 : (0:ℝ) < x := hx
  have hy0 : (0:ℝ) < y := hy
  have hxγ : 0 < x ^ γ := Real.rpow_pos_of_pos hx0 γ
  have hyγ : 0 < y ^ γ := Real.rpow_pos_of_pos hy0 γ
  -- `x^γ · y < x · y^γ`, i.e. `x^{γ-1} < y^{γ-1}`
  have hpow : x ^ (γ - 1) < y ^ (γ - 1) := Real.rpow_lt_rpow hx0.le hxy (by linarith)
  have ex : x ^ γ = x ^ (γ - 1) * x := by
    conv_lhs => rw [show γ = (γ - 1) + 1 by ring]
    rw [Real.rpow_add hx0, Real.rpow_one]
  have ey : y ^ γ = y ^ (γ - 1) * y := by
    conv_lhs => rw [show γ = (γ - 1) + 1 by ring]
    rw [Real.rpow_add hy0, Real.rpow_one]
  have hcross : x ^ γ * y < x * y ^ γ := by
    rw [ex, ey]; nlinarith [mul_pos hx0 hy0]
  unfold costElasticity
  rw [div_lt_div_iff₀ (by positivity) (by positivity)]
  have hk : 0 < (γ - 1) * (c * (δ / r)) := by
    have : 0 < δ / r := div_pos hδ hr
    have : 0 < γ - 1 := by linarith
    positivity
  have e : (δ * y / r + γ * (c * y ^ γ)) * (δ * x / r + c * x ^ γ)
      - (δ * x / r + γ * (c * x ^ γ)) * (δ * y / r + c * y ^ γ)
      = (γ - 1) * (c * (δ / r)) * (x * y ^ γ - x ^ γ * y) := by ring
  nlinarith [mul_pos hk (sub_pos.mpr hcross)]

/-- **`D` is strictly decreasing on `(0, ∞)`** (for `α > 0`, `β > 1`, `γ > 1`). -/
theorem followerFocD_strictAntiOn {α β γ c δ r T : ℝ} (hα : 0 < α) (hβ : 1 < β)
    (hγ : 1 < γ) (hc : 0 < c) (hδ : 0 < δ) (hr : 0 < r) (hT : 0 < T) :
    StrictAntiOn (followerFocD α β γ c δ r T) (Ioi 0) := by
  intro x hx y hy hxy
  have hs := followerShare_strictMonoOn hα hT hx hy hxy
  have he := costElasticity_strictMonoOn hc hδ hr hγ hx hy hxy
  have hαβ : 0 < α * β := mul_pos hα (by linarith)
  unfold followerFocD
  nlinarith [mul_lt_mul_of_pos_left hs hαβ,
    mul_lt_mul_of_pos_left he (show (0:ℝ) < β - 1 by linarith)]

/-- **The follower's capacity condition has at most one root** (uniqueness part of
Proposition 3(i)). -/
theorem followerFoc_unique {α β γ c δ r T K₁ K₂ : ℝ} (hα : 0 < α) (hβ : 1 < β)
    (hγ : 1 < γ) (hc : 0 < c) (hδ : 0 < δ) (hr : 0 < r) (hT : 0 < T)
    (hK₁ : 0 < K₁) (hK₂ : 0 < K₂)
    (h₁ : followerFocD α β γ c δ r T K₁ = 0) (h₂ : followerFocD α β γ c δ r T K₂ = 0) :
    K₁ = K₂ :=
  (followerFocD_strictAntiOn hα hβ hγ hc hδ hr hT).injOn hK₁ hK₂ (h₁.trans h₂.symm)

end Follower

/-! ## Values before the first investment (Proof of Proposition 3(iii), eq-values-before-entry)

Below the first investment both values are the mutual-waiting value `W` plus a
multiple of `X^β` (`β = β_L^+`), pinned at `X_L`.  The two facts used in the
no-deviation argument are pure algebra once those forms and the maximizing property
of `X_L` are given; the forms, the maximization and every number are numerical. -/

/-- **`V_follow - V_lead = [F(X_L) - L*(X_L)](X/X_L)^β`.** -/
theorem follow_sub_lead (W X XL β FL LL : ℝ) :
    (W + (FL - W) * (X / XL) ^ β) - (W + (LL - W) * (X / XL) ^ β)
      = (FL - LL) * (X / XL) ^ β := by
  ring

/-- **The follower's condition follows from the leader's when `F(X_L) ≥ L*(X_L)`.**
If `V_lead(X) ≥ L*(X)` and `F(X_L) ≥ L*(X_L)`, then `V_follow(X) ≥ L*(X)`. -/
theorem follower_condition_of_leader {WX WL X XL β FL LL LX : ℝ} (hX : 0 < X) (hXL : 0 < XL)
    (hlead : LX ≤ WX + (LL - WL) * (X / XL) ^ β) (hFL : LL ≤ FL) :
    LX ≤ WX + (FL - WL) * (X / XL) ^ β := by
  have hp : 0 ≤ (X / XL) ^ β := Real.rpow_nonneg (div_pos hX hXL).le _
  nlinarith [mul_le_mul_of_nonneg_right (sub_le_sub_right hFL WL) hp]

/-- **Leading at the maximizer of `h` dominates investing at once.**  If `X_L`
maximizes `h(X) = [L*(X) - W(X)]X^{-β}` over the positive demand levels, then for every
`X > 0`, `V_lead(X) = W(X) + [L*(X_L) - W(X_L)](X/X_L)^β ≥ L*(X)`. -/
theorem lead_value_ge_payoff {L W : ℝ → ℝ} {β XL X : ℝ} (hXL : 0 < XL) (hX : 0 < X)
    (hmax : (L X - W X) * X ^ (-β) ≤ (L XL - W XL) * XL ^ (-β)) :
    L X ≤ W X + (L XL - W XL) * (X / XL) ^ β := by
  have hXβ : 0 < X ^ β := Real.rpow_pos_of_pos hX β
  have e1 : X ^ (-β) = (X ^ β)⁻¹ := Real.rpow_neg hX.le β
  have e2 : (X / XL) ^ β = X ^ β * XL ^ (-β) := by
    rw [Real.div_rpow hX.le hXL.le, Real.rpow_neg hXL.le, div_eq_mul_inv]
  rw [e2]
  rw [e1] at hmax
  have h := mul_le_mul_of_nonneg_left hmax hXβ.le
  have e3 : X ^ β * ((L X - W X) * (X ^ β)⁻¹) = L X - W X := by
    field_simp
  rw [e3] at h
  nlinarith [h]

end AILab
