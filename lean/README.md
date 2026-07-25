# Lean proof verification (`AILabProofs`)

Machine-checked formalization of the closed-form results in *Investing in
Artificial General Intelligence* (issue #100: "Try out Lean for proof
verification"). Every theorem here is verified by the Lean 4 kernel against
[Mathlib](https://github.com/leanprover-community/mathlib4); none rely on
`sorry`, and each depends only on Lean's three standard axioms (`propext`,
`Classical.choice`, `Quot.sound`).

It covers the reduction of the Euler ODE to the characteristic equation and the
algebraic / single-variable-calculus content of the propositions — the closed
forms, first-order conditions, comparative statics, and the existence/uniqueness
of the preemption trigger — i.e. the steps a referee checks by hand. It does *not*
attempt the optimal-stopping verification theorem or the numerical results, which
are out of scope for an algebraic proof assistant.

## What is verified

| File | Theorem | Paper result |
|:-----|:--------|:-------------|
| `EulerODE.lean` | `hasDerivAt_rpow_fst`, `hasDerivAt_rpow_snd` | the option value's first and second derivatives `F'=βX^{β-1}`, `F''=β(β-1)X^{β-2}` |
| | `euler_operator_rpow`, `rpow_solves_euler_iff` | `X^β` solves the homogeneous Euler ODE (eq-hjb-L) **iff** `Q(β)=0` (eq-beta-H) — ties the roots to the actual ODE |
| `Proposition1.lean` | `trigger_from_boundary_conditions` | Prop 1, Step 1 — value-matching + smooth-pasting give `X* = β/(β-1)·b/A` (eq-trigger-phi) |
| | `npv_at_trigger` | Prop 1, Step 2 — NPV at the trigger equals `b/(β-1)` |
| | `hasDerivAt_A_eff_K` | Prop 1, Step 4 — `A_eff = g(φ)K^α` has log-derivative `α/K`, independent of `φ` (so `K*` does not depend on `φ`) |
| | `K_foc_reduced`, `K_foc` | Prop 1, Step 4 — capacity FOC in closed form for `K^{γ-1}` |
| `CharacteristicRoots.lean` | `charPoly_betaPlus`, `charPoly_betaMinus` | the quadratic-formula roots solve `½σ²β(β-1)+μβ-ρ=0` (eq-beta-H) |
| | `betaPlus_gt_one` | positive root `> 1` (used as `β_H>1`, `β_L⁺>1`); needs `ρ>μ` |
| | `betaMinus_neg` | negative root `< 0` (used as `β_s⁻<0`) |
| | `lt_betaPlus_of_charPoly_neg` | `Q(x)<0 ⟹ x<β₊` (workhorse for comparing roots) |
| | `betaH_lt_betaPlus_L` | root ordering `β_L⁺ > β_H` |
| | `markup_mem_Ioo` | Leland markup `β/(β-1) ∈ (0,1)` for `β<0` |
| | `betaMinus_strictAnti_rho`, `markup_strictAnti`, `markup_betaMinus_increasing_lam` | Prop 2(ii) markup channel — `M(β_s⁻)` increasing in `λ` |
| `Proposition2.lean` | `hasDerivAt_A_eff` | Prop 2(ii) — `∂A_eff/∂λ = (b(r-μ_L)-a)/(r-μ_L+λ)²` (quotient rule) |
| | `A_eff_deriv_pos` | faith-based survival condition `a < b·d ⟹ ∂A_eff/∂λ > 0` |
| | `faith_threshold` | the threshold `(φ/(1-φ))^α > q ⟺ φ > R/(1+R)`, `R=q^{1/α}` (eq-phi-underbar) |
| | `XD_increasing_leverage` | Prop 2(i) — default boundary increasing in leverage `ℓ` |
| | `share_decreasing_rival`, `XD_decreasing_in_Aeff` | Prop 2(iv) — contest share falls in rival capacity, so `X_D` rises |
| | `net_threshold_rearrange`, `net_threshold_phi` | Prop 2(ii) — net-threshold rearrangement and the `φ̃` ratio inversion (eq-phi-tilde) |
| `Proposition1Phi.lean` | `hasDerivAt_alloc` | Prop 1, Step 5 — `g'(φ) = α(w_H φ^{α-1} - w_L(1-φ)^{α-1})` |
| | `alloc_foc_ratio` | interior FOC `⟺ (φ/(1-φ))^{1-α} = w_H/w_L` |
| | `ratio_eq_closed_form` | ratio condition pins the **unique** interior `φ* = ρ/(1+ρ)`, `ρ=(w_H/w_L)^{1/(1-α)}` |
| | `alloc_foc_closed_form` | the two combined: closed form for `φ*` |
| | `phiStar_lt_phiStar`, `phiStar_increasing_lam`, `phiStar_increasing_muH`, `weight_ratio` | Prop 1, Step 6 — `φ*` increasing in `λ` and `μ_H`, independent of `μ_L` |
| `Duopoly.lean` | `contest_share_scale_invariant`, `share_role_invariant` | Prop 3(ii) — Tullock share is scale-invariant, so the allocation cancels |
| | `A_eff_follower_separable` | Appendix B — follower coefficient factors as `g(φ)·K_F^{2α}/(K_F^α+K_L^α)` |
| | `preemption_exists` | Prop 3(i) — existence of the rent-equalization trigger `X_P` (IVT) |
| | `unique_crossing` | Prop 3(i) — a continuous strictly concave `G` with `G(a)<0<G(b)` has a **unique** zero in `(a,b)` (the `ℓ=0` single-crossing) |
| | `hasDerivAt_tullock` | Prop 3(ii) — `f'(u) = α u^{α-1} s(2-s)` for `f(u)=u^{2α}/(u^α+c)` |

`Basic.lean` holds the shared `ModelParams` structure (primitives + admissibility
hypotheses mirroring the calibration table) and elementary positivity lemmas.

Results are stated for abstract reals with the relevant sign hypotheses, so a
theorem proves the identity for *every* admissible parameter value, not just the
baseline calibration. The Lean names and the paper equation labels are
cross-referenced in each file's module docstring.

## Building

Requires [`elan`](https://github.com/leanprover/elan) (Lean toolchain manager);
the toolchain version is pinned in `lean-toolchain`.

```bash
cd lean
lake exe cache get   # download prebuilt Mathlib oleans (first time only)
lake build           # kernel-checks every proof
```

To confirm soundness (no `sorry`, only standard axioms):

```bash
printf 'import AILabProofs\n#print axioms AILab.alloc_foc_closed_form\n' | lake env lean --stdin
# 'AILab.alloc_foc_closed_form' depends on axioms: [propext, Classical.choice, Quot.sound]
```

## Scope and limitations

- **In scope (done):** the reduction of the homogeneous Euler ODE to the
  characteristic equation, and the closed-form algebra, first-order conditions, and
  comparative statics of Propositions 1–3 — the trigger and NPV, the capacity
  `K*` and training fraction `φ*` (with comparative statics), the characteristic
  roots and their ordering, the faith-based-survival derivative/threshold and the
  default-boundary monotonicities, the duopoly role-invariance and separable
  reduction, and the existence **and** zero-leverage single-crossing uniqueness of
  the preemption trigger.
- **Not formalized:** the single-crossing uniqueness of `X_P` for `ℓ>0`
  (numerical in the paper), the explicit markup semi-elasticity `m` as a derivative
  and the numerical magnitude of `φ̃` (the markup-channel *monotonicity* and the
  net-threshold rearrangement are verified), strict-concavity of `A_eff` in `φ` as
  an abstract statement (the explicit FOC closed form here already gives existence
  *and* uniqueness of the interior critical point), the pure-power (`A₁=0`) form of
  the L-regime option value — a solution convention rather than a theorem, see
  Step 5b of the Proof of Proposition 1 — and all numerical / coupled-ODE results
  (Appendix B), including the piecewise-stopping bias check and Numerical
  Finding 1.
- The reduction of the ODE to the characteristic equation is verified
  (`rpow_solves_euler_iff`), but the *derivation of the HJB equation itself* from
  stochastic-calculus primitives, and the optimal-stopping verification theorem
  (that smooth-fit holds and the candidate is the value function), are not — these
  are taken as the starting point, as a referee reading the appendix would.
