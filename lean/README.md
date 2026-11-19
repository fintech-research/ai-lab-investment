# Lean proof verification (`AILabProofs`)

Machine-checked formalization of closed-form steps in *Investing in Artificial General Intelligence* (issue #100, restated for the model of record in issue #186). Every theorem here is verified by the Lean 4 kernel against [Mathlib](https://github.com/leanprover-community/mathlib4); none relies on `sorry`, and each depends only on Lean's three standard axioms (`propext`, `Classical.choice`, `Quot.sound`).

What the package proves is algebra and single-variable calculus *conditional on* the objects the paper derives from the stopping problems: the HJB equations, the functional forms of the value functions, the exercise payoffs, and value matching and smooth pasting. A theorem stated as an identity under hypotheses proves that identity and nothing more. In particular, no theorem here proves that a candidate policy is optimal in a stopping problem, that an equilibrium exists or is unique, or any number quoted in the paper. Kernel-checked and `sorry`-free means there are no gaps in the formal proofs; it does not mean there are no economic hypotheses, and the hypotheses of each theorem are part of its statement.

## Audit against the current paper (issue #186)

Status key:

- **current**: states algebra the current paper uses, with the paper result named;
- **current, restated**: statement unchanged, but its docstring or the previous README attached it to a result that the model of record changed, and the attribution is corrected;
- **nested approximation**: true algebra about the nested pure-power game or approximation, which the paper keeps as a reported approximation (Internet Appendix B), not about the model of record;
- **no current use**: true, kept for the nested game, but no statement of the current paper uses it;
- **new**: added in issue #186.

No theorem was false; none was deleted. No theorem needed new hypotheses: where the previous statement was weaker than the paper's use (`K_foc` does not show that its right-hand side is positive), the missing step is a new theorem.

### Proposition 1 (single firm)

| File | Theorem | Paper result | Status |
|:-----|:--------|:-------------|:-------|
| `EulerODE.lean` | `hasDerivAt_rpow_fst`, `hasDerivAt_rpow_snd` | `F' = βX^{β-1}`, `F'' = β(β-1)X^{β-2}` | current |
| | `euler_operator_rpow`, `rpow_solves_euler_iff` | `X^β` solves the homogeneous Euler equation iff `Q(β) = 0` (eq-hjb-L, eq-beta-H) | current |
| `CharacteristicRoots.lean` | `charPoly_betaPlus`, `charPoly_betaMinus` | the quadratic-formula roots solve `½σ²β(β-1)+μβ-ρ=0` | current |
| | `betaPlus_gt_one`, `betaMinus_neg` | `β_H > 1`, `β_L⁺ > 1`, `β_L⁻ < 0` | current |
| | `lt_betaPlus_of_charPoly_neg`, `betaH_lt_betaPlus_L` | `β_L⁺ > β_H` (remark on the pure-power form) | current |
| `Proposition1Phi.lean` | `hasDerivAt_alloc`, `alloc_foc_ratio`, `ratio_eq_closed_form`, `alloc_foc_closed_form` | Prop 1(i): the allocation first-order condition has the unique interior root `φ* = ρ/(1+ρ)` (eq-phi-star) | current |
| | `phiStar_lt_phiStar`, `weight_ratio`, `phiStar_increasing_lam`, `phiStar_increasing_muH` | Prop 1(i): `φ*` increasing in `λ` and `μ_H`, independent of `μ_L` | current |
| `Proposition1.lean` | `trigger_from_boundary_conditions` | Prop 1(ii), Step 1: value matching and smooth pasting give `X = β/(β-1)·Θ/(aK^α)` (eq-trigger-H; with `a = g(φ*)`, the pure-power eq-trigger-phi) | current, restated (was "Prop 1"; it is the post-switch trigger and the approximation, not the pre-switch `X*`) |
| | `npv_at_trigger` | Prop 1(ii), Step 2: NPV at the trigger is `Θ/(β-1)` | current, restated |
| | `hasDerivAt_A_eff_K` | Prop 1(ii), Step 4: the revenue coefficient drops out of the capacity condition | current, restated (was "`K*` does not depend on `φ`"; that holds for `K_H*` and the pure-power capacity, not for the pre-switch `K*`) |
| | `K_foc_reduced`, `K_foc` | Prop 1(ii): eq-foc-K is equivalent to the closed form for `K^{γ-1}` (eq-K-H) | current, restated (an equivalence only; positivity and optimality are below) |
| `Capacity.lean` | `capRoot_pos`, `KHstar_pos`, `KHstar_rpow`, `KHstar_foc` | Prop 1(ii): under (A2) the right-hand side of eq-K-H is positive, so `K_H* > 0` is well defined and solves eq-foc-K | new |
| | `foc_numerator_eq`, `foc_numerator_pos_iff`, `foc_numerator_neg_iff`, `hasDerivAt_logCapObj` | Prop 1(ii), Step 4: the log-derivative of the capacity objective is positive below `K_H*` and negative above | new |
| | `logCapObj_lt_KHstar`, `capObj_lt_capObj_KHstar` | Prop 1(ii), Step 4: `K_H*` is the unique global maximiser of the reduced objective `h(K) = (aK^α)^β/Θ(K)^{β-1}` on `(0, ∞)` | new |
| `PreSwitch.lean` | `particular_power_iff` | eq-particular-C: `ΓX^{β_H}` solves the forced L-regime equation iff `Γ = -λB_H/Q_L(β_H)` | new |
| | `charPoly_L_at_H_root`, `charPoly_L_at_H_root_neg`, `particular_coeff_pos` | `Q_L(β_H) = (μ_L-μ_H)β_H - λ < 0`, so `Γ > 0` (remark on the pure-power form) | new |
| | `particular_affine` | eq-option-L-upper: the affine particular solution `λp_H X/(r+λ-μ_L) - λq_H/(r+λ)` | new |
| | `premium_value_matching`, `hasDerivAt_premium_coeff`, `premium_foc_iff` | Prop 1(iii), Step 7, eq-premium: value matching by construction; the first-order condition in the trigger is smooth pasting | new |
| | `hasDerivAt_payoff_K`, `scale_foc_iff` | Prop 1(iii): the first-order condition in capacity is eq-scale-foc | new |

### Proposition 2 and the credit block

| File | Theorem | Paper result | Status |
|:-----|:--------|:-------------|:-------|
| `Proposition2.lean` | `equity_value_matching`, `hasDerivAt_equity`, `default_smooth_pasting_iff` | eq-equity, eq-default-boundary: value matching holds by construction and smooth pasting `E'(X_D) = 0` is equivalent to `X_D = β/(β-1)·N/A` | new |
| | `revenue_at_boundary` | at `X_D` revenue covers `β_L⁻/(β_L⁻-1)` of the fixed claims (section "Equity and debt values") | new |
| | `shutdown_boundary_pos`, `boundary_continuous_coupon` | the zero-coupon boundary is the positive shutdown boundary, and the boundary is continuous in the coupon, hence in leverage at `ℓ = 0` | new |
| | `XD_increasing_leverage` | Prop 2(i): `X_D` increasing in `ℓ` (including from `ℓ = 0`) and, by the same algebra, in `r_c` | current |
| | `share_decreasing_rival`, `XD_decreasing_in_Aeff` | Prop 2(iv): `X_D` increasing in rival capacity | current |
| | `hasDerivAt_A_eff` | Prop 2(ii) and Corollary 1: `∂A_eff/∂λ = (b(r-μ_L)-a)/(r-μ_L+λ)²` | current |
| | `A_eff_deriv_pos` | eq-faith-condition makes the derivative positive | current |
| | `faith_threshold` | eq-phi-underbar: `(φ/(1-φ))^α > q ⟺ φ > φ̲` | current |
| | `phiUnder_strictMono_q`, `phiUnder_strictMono_alpha`, `phiUnder_strictMono_r`, `phiUnder_strictAnti_muH`, `phiUnder_strictMono_muL` | Prop 2(ii): `φ̲` increasing in `α` and `r`, decreasing in `μ_H - μ_L` | new |
| | `oddsPow_strictMonoOn`, `phiUnder_mem`, `oddsPow_phiUnder` | `φ̲ ∈ (0,1)` and `(φ/(1-φ))^α` increasing, equal to `q` at `φ̲` | new |
| | `net_threshold_rearrange`, `net_threshold_phi` | Prop 2(ii), eq-phi-tilde: net-condition rearrangement; `net_threshold_phi` is `faith_threshold` at the cutoff `q̃`, not an independent argument | current |
| `CharacteristicRoots.lean` | `markup_mem_Ioo`, `betaMinus_strictAnti_rho`, `markup_strictAnti`, `markup_betaMinus_increasing_lam` | Prop 2(ii) markup channel: `β_L⁻/(β_L⁻-1) ∈ (0,1)` and increasing in `λ` | current |
| `Credit.lean` | `inference_share_iff_foc` | eq-recovery: the inference business earns the firm's revenue per unit of capacity iff the allocation first-order condition holds (`φ = φ*`) | new |
| | `inference_boundary_eq_shutdown`, `inference_value_eq_frac` | at `φ*`, `X_I` equals the firm's shutdown boundary and `Λ = (1-φ*)U` | new |
| | `gross_inference_at_boundary_pos_iff` | at `φ*`, without the shutdown option the inference business has positive net value at `X_D` iff `C_D > (1-M)/M·δK` (the "0.43 times the operating cost" of the appendix) | new |
| `Corollary1.lean` | `hasDerivAt_A_eff_deriv`, `A_eff_second_deriv_neg`, `hasDerivAt_V_lam`, `hasDerivAt_V_lam_deriv` | eq-installed-lambda: `V' = XG/Δ²`, `V'' = -2XG/Δ³` | new |
| | `V_lam_strictMonoOn`, `V_lam_strictConcaveOn`, `V_lam_strictAntiOn`, `V_lam_strictConvexOn`, `V_lam_const` | Corollary 1(i): the sign of `G` fixes monotonicity and curvature on all of `λ ≥ 0` | new |
| | `faithGap_pos_iff`, `faithGap_neg_iff`, `corollary1_i` | Corollary 1(i): increasing and strictly concave on `λ ≥ 0` iff `φ > φ̲` | new |
| | `news_asymmetry`, `news_asymmetry_pos_iff` | Corollary 1(ii): the news identity `2h²XG/(Δ(Δ-h)(Δ+h))` and its sign | new |
| | `hasDerivAt_faithGap_phi`, `faithGap_deriv_pos`, `faithGap_strictMonoOn`, `semiElasticity_eq`, `semiElasticity_lt`, `ratio_strictMonoOn` | Corollary 1(iii): `∂G/∂φ > 0`, and the semi-elasticity of `A_eff` in `λ` increases in `φ` at a common belief | new |

### Proposition 3 (duopoly)

| File | Theorem | Paper result | Status |
|:-----|:--------|:-------------|:-------|
| `Duopoly.lean` | `contest_share_scale_invariant`, `share_role_invariant`, `hasDerivAt_tullock` | Prop 3(ii): at a common allocation the shares coincide across regimes and the contest derivative factors as `αu^{α-1}s(2-s)`, so a common allocation is a critical point iff it is `φ*` | current, restated (Prop 3(ii) is now a critical-point statement; the equilibrium `φ_L < φ*` is numerical) |
| | `tullock_elasticity`, `followerFoc_iff`, `followerShare_strictMonoOn`, `costElasticity_strictMonoOn`, `followerFocD_strictAntiOn`, `followerFoc_unique` | Prop 3(i), eq-follower-foc: the follower's revenue elasticity is `α(2-s_F)`, the log-derivative of its option coefficient is strictly decreasing, so the condition has at most one root (also the nested game's follower condition, with the leverage-adjusted cost) | new |
| | `follow_sub_lead`, `follower_condition_of_leader`, `lead_value_ge_payoff` | Proof of Prop 3(iii), eq-values-before-entry: `V_follow - V_lead = [F(X_L) - L*(X_L)](X/X_L)^β`; the follower's condition follows from the leader's when `F(X_L) ≥ L*(X_L)`; if `X_L` maximizes `h` then `V_lead ≥ L*` | new |
| | `A_eff_follower_separable` | Internet Appendix B, nested game: separable follower coefficient at a common allocation | nested approximation |
| | `preemption_exists` | Internet Appendix B, nested game: existence of its rent-equalization trigger by the intermediate value theorem, given the endpoint signs (the upper one computed) | nested approximation (does not apply to `X_L` or `X_P` of Prop 3(iii)) |
| | `unique_crossing` | generic: a strictly concave `G` with `G(a) < 0 < G(b)` has a unique zero | no current use (written for the nested game at `ℓ = 0` without the option to stop) |

`Basic.lean` holds the shared `ModelParams` structure and elementary positivity lemmas.

Results are stated for abstract reals with the relevant sign hypotheses, so each theorem holds for every parameter value satisfying them, not only the baseline calibration. The Lean names and the paper's equation labels are cross-referenced in each file's module docstring.

## What is not formalized

- The stochastic-calculus derivation of the HJB equations (eq-hjb-L and the equity and debt equations), and every optimal-stopping verification argument: that smooth pasting characterizes the optimal investment or default rule, and that a candidate value function is the value function. Value matching, smooth pasting and the functional forms of the value functions are inputs.
- Proposition 1(i): that `φ*` is the maximiser of `g` (the Inada limits and strict concavity of Step 5). The package proves that `φ*` is the unique interior critical point.
- Proposition 1(iii) as a whole: ODE uniqueness (that a solution of the homogeneous equation vanishing at the origin is a multiple of `X^{β_L⁺}`), the value and slope matching at `X_H*` that pin `(A_1, G_1, G_2)`, existence or uniqueness of a solution of the two-region system, and the single maximum in capacity. The package proves the particular solutions and that the first-order conditions are smooth pasting and eq-scale-foc.
- The waiting margin eq-waiting-margin and the criterion built on it, which the paper derives from growth rates and confirms numerically.
- Proposition 2: the single-boundary reduction itself and the sign and size of its bias, that eq-equity solves the equity ODE, the leverage-training substitution of part (iii), and the magnitude of `m` and `φ̃`. The comparative statics of `φ̲` and the smooth-pasting algebra of the boundary are formalized.
- The recovery rule eq-recovery beyond the identities at `φ*` (its caps, the bankruptcy cost, every recovery level), the fair coupon, and every credit spread and default probability.
- Proposition 3(i): existence of a root of eq-follower-foc (the signs of the log-derivative at the two ends of `(0, ∞)`), and the version with the option to stop.
- Proposition 3(ii): that the critical point is a maximum, and the allocation against a rival away from `φ*`.
- Proposition 3(iii) to (v) and Remark 4: `X_L`, `X_P`, the no-deviation conditions, the mutual-waiting value `W`, existence and uniqueness of equilibrium, and every number. The lemmas on eq-values-before-entry take the values and the maximization as given.
- Corollary 1 with the option to stop: unlevered value with the shutdown option, levered equity, and the duopoly leader, all numerical in the paper.
- Numerical Finding 1 (Dario's dilemma), the coupled-ODE and piecewise-stopping computations of Internet Appendix B, the pure-power approximation's error, the calibration, and every robustness exercise.

## Building

Requires [`elan`](https://github.com/leanprover/elan) (Lean toolchain manager); the toolchain version is pinned in `lean-toolchain`.

```bash
cd lean
lake exe cache get   # download prebuilt Mathlib oleans (first time only)
lake build           # kernel-checks every proof
```

To confirm soundness (no `sorry`, only standard axioms):

```bash
printf 'import AILabProofs\n#print axioms AILab.capObj_lt_capObj_KHstar\n' | lake env lean --stdin
# 'AILab.capObj_lt_capObj_KHstar' depends on axioms: [propext, Classical.choice, Quot.sound]
```
