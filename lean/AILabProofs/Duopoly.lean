import AILabProofs.Basic

set_option linter.style.header false

/-!
# Proposition 3 — duopoly preemption and role-invariance

This file verifies the algebraic and existence ingredients of Proposition 3
(`paper/_appendix.qmd`, "Proof of Proposition 3", and `paper/_model.qmd`,
@sec-duopoly).

* `contest_share_scale_invariant` : the Tullock contest share
  `(tK_i)^α/((tK_i)^α+(tK_j)^α)` is independent of the common scale `t` — the
  cancellation behind the role-invariance of the training fraction (Proposition
  3(ii)) and the separable reduction of the follower problem (Appendix B).
* `share_role_invariant` : consequently the L-regime share (`t = 1-φ`) and the
  H-regime share (`t = φ`) coincide at a common allocation `φ`.
* `A_eff_follower_separable` : the follower's effective revenue coefficient
  factors as `g(φ)·K_F^{2α}/(K_F^α+K_L^α)` (Appendix B, "Separable reduction").
* `preemption_exists` : the rent-equalization point `X_P` exists — an
  intermediate-value argument from the leader/follower value crossing
  (Proposition 3(i)).
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

/-- **Separable reduction of the follower coefficient.**  With the role-invariant
shares, the follower's effective revenue coefficient factors into an allocation
term `g(φ) = w_L(1-φ)^α + w_H φ^α` and a capacity term `K_F^{2α}/(K_F^α+K_L^α)`
(Appendix B). -/
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

/-- **Existence of the preemption trigger `X_P`** (Proposition 3(i)).  Where the
leader's value `L` starts below the follower's option value `F` (`L a < F a`) and
ends above it (`F b < L b`), with both continuous, rent equalization `L = F` occurs
at some interior `X_P` — an intermediate-value argument. -/
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

/-- **Single-crossing uniqueness** (Proposition 3(i), zero-leverage case).  A
continuous, *strictly concave* function with `G a < 0 < G b` has a **unique** zero
in `(a, b)`.  At `ℓ = 0` the leader–follower gap `L(X) - F(X)` is linear minus the
convex `X^{β_H}` term, hence strictly concave; with `G(0) < 0` this gives the
unique up-crossing that pins the preemption trigger `X_P`. -/
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

/-- **Tullock contest derivative factorization** (Proposition 3(ii)).  For the
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

end AILab
