# Referee report: "Investing in Artificial General Intelligence"

Reviewer: claude-opus-5.5 · Date: 2026-11-01 · Branch `t3/parallel-paper-review-reports` at `4def5f6` (0 ahead / 0 behind `origin/main` after `git fetch`). Target journal: Management Science.

## Derived review brief

The paper's spine, read from the abstract, introduction and conclusion, has four blocks: (S1) closed forms for the single-firm trigger, capacity and training fraction (Proposition 1, `@eq-trigger-phi`, `@eq-phi-star`), resting on the "unconditional-A_eff" pricing convention (`A_1 = 0`, L-regime options priced with `β_H`); (S2) faith-based survival: the default boundary falls in λ above the thresholds `φ̲` and `φ̃` (Proposition 2, `@eq-phi-underbar`, `@eq-phi-tilde`), resting on the single-boundary Leland reduction; (S3) the preemption equilibrium with role-invariant φ and a 43% preemption discount (Proposition 3, `@fig-competition-effect`), resting on the leader-scale convention; (S4) Dario's dilemma, an asymmetric loss from belief errors (26% against 4–6%) plus an eight-fold tail-default asymmetry (Numerical Finding 1, `@fig-investment-dilemma`). The load-bearing choices are the pricing convention, training as a flow that earns nothing before the switch, par debt at `r_c < r`, the Tullock contest, and the stylized calibration. So Part 1 has one heading for each spine block, plus the Lean package, the SymPy notebook, and figure and code hygiene. Part 2 follows the skill skeleton. There is no `REVIEW_INSTRUCTIONS.md`, and I did not read anything in `reports/`.

What I actually ran (all scratch work under `/tmp/review_opus55`):

- `lake build` of a copy of `lean/`, which succeeded (8572 jobs), and `#print axioms` on five key theorems (standard axioms only).
- `uv run pytest` (393 passed).
- Direct re-computation of every headline number listed in Part 1 through the package API.
- Execution of `notebooks/model_derivation.ipynb` (it runs).
- A `quarto render` of the identified PDF: 98 pages with references starting on p. 37, and no `??` or `(?)` in the extracted text.
- Visual inspection of four figure PDFs.

I did not re-run the robustness sweep, the piecewise or LCP solver, the dynamic-φ table, or Proposition 3(v). Statements about those rest on reading the code and the text.

---

## Executive summary

**Correctness.** The algebra is right. I re-derived independently `K*`, `φ*`, `X*`, `∂A_eff/∂λ`, `φ̲`, `m`, `φ̃` and the `λ ≈ 0.025/0.034` crossings by hand. The code reproduces every headline number I checked, to the reported precision. The Lean package builds and its statements faithfully formalise the algebra they claim to cover.

**Submission readiness.** Not yet, for a reason the paper itself documents but does not let reach the abstract or the introduction:

> **Single biggest concern (Issue 1).** At the baseline calibration, the paper's own Internet Appendix B shows that the policy it studies (investing before AGI arrives at `X*`) is beaten by *never investing before the switch*. This holds in the unrestricted problem (no pre-switch trigger exists; the paper's policy delivers 93.1% of the optimum) and even within the precommitted-scale class (pure switching is worth 1.619e-3 against 1.615e-3 for the paper's policy; `_appendix.qmd:363`). In other words, the analytical triggers, the preemption game in regime L, the entry-time default risk and the optimistic branch of Dario's dilemma all describe a policy that the exact version of the model does not choose.

A Management Science referee will read Step 5b and IA-B and ask why the paper's main object is a convention-defined trigger rather than the closed-form precommitted-scale solution the authors already have.

The second-tier concerns are these:

- The four lab archetypes feed no reported investment result, despite the abstract's claim (Issue 2).
- The archetypes' implied λ contradicts the executive timelines used to motivate the λ range by a factor of 3 to 10 (Issue 3).
- The SymPy notebook that AGENTS.md presents as backing the propositions asserts the very claim (`A_1 = 0` follows from (A3)) that the paper now explicitly rejects (Issue 4).

---

## Part 1: Validation

### 1.1 Spine S1: Proposition 1 closed forms (pass, with the convention caveat in Issue 1)

- `K*` (`_model.qmd:100`): the FOC of `ln h = αβ ln K − (β−1) ln(δK/r + cK^γ)` gives `K^{γ−1} = δ(αβ−β+1)/(rc(γ(β−1)−αβ))`, and the (A2) bounds are exactly the positivity of numerator and denominator. **Pass.** The global-max argument at `_appendix.qmd:99` is correct.
- `φ*` (`_model.qmd:104`): the ratio `w_H/w_L = λ/(r−μ_H)`, and at baseline `ρ = (0.1/0.06)^{1/0.6} = 2.343`, so `φ* = 0.7009`. The code gives 0.700856 numerically against 0.700856 in closed form. **Pass.**
- `β_H = 1.5529`, `β_L⁺ = 3.015`, `(1−1/β_L⁺)/α = 1.67`, and the option premium is `2.82`. **Pass.**
- `X* = 0.004722` and `K* = 0.006727` (code). **Pass.**
- An observation the paper could use: at the optimum, the H-regime share of `A_eff` equals `φ*` *exactly*, because the FOC gives `w_Hφ^α / A = φ`. `_appendix.qmd:273` says "approximately 70%"; that should be stated as an identity (Minor, Issue 27).

### 1.2 Spine S2: Proposition 2 and the faith thresholds (pass)

- `∂A_eff/∂λ = [Π_H(r−μ_L) − Π_L]/Δ²` and `Ω = (0.06/0.11)^{2.5} = 0.2198`, so `φ̲ = 0.180`. The code gives 0.180149. **Pass.**
- Markup channel: `dβ⁻/dλ = −1/𝓡`, so `dM/dλ = 1/((β−1)²𝓡)` and `m = 1/(β(β−1)𝓡) = 0.768`. With that, `Ω̃ = [0.06·1.161/(0.11−0.0161)]^{2.5} = 0.475`, giving `φ̃ = 0.322`. The code gives 0.32190. **Pass.**
- At `λ = 0.034` I get `φ* = 0.280` and `φ̃ = 0.280` by hand, confirming `λ̄ ≈ 0.034`. At `λ = 0.02`, `φ* = 0.138`. **Pass.**
- The single-boundary `X_D` (`@eq-default-boundary`) follows from the L-regime equity ODE with the perpetuity `E_H`. I re-derived it, including the constant `−(C_D+δK)/r`. **Pass.**
- Not re-run: the 3% coupled-boundary bias.

### 1.3 Spine S3: Proposition 3 and the preemption numbers (pass)

The code output (`solve_preemption_equilibrium`, `ℓ = 0`) gives:

- `X_P = 0.002703`, `X_L^mono = 0.004722`, ratio 0.5725 (43% discount);
- `X_F = 0.1188`, `K_F = 0.2588`, `φ_F = 0.70086`, with a single crossing;
- ratio 0.644 at `σ = 0.20` and 0.536 at `σ = 0.30`.

With leverage:

- `X_F` is 0.123 at `ℓ = 0.05` and 0.211 at `ℓ = 0.65`;
- `X_F/X_{D,F}` is 11.7 at `ℓ = 0.05` and 6.4 at `ℓ = 0.65`;
- at `ℓ = 0.40`, `X_{D,L} = 0.001401` and `X_P = 0.003573`, matching `_appendix.qmd:329`.

The re-optimized leader gives a discount of 86.1%, with `K_L^re = 0.00038` and `X_F^re = 0.0312`, matching `_appendix.qmd:337`. **Pass.**

The zero-leverage uniqueness proof (`_appendix.qmd:229–233`) is correct: the gap is linear minus `𝓔X^{β_H}`. Proposition 3(v) (`X_P/X_D` from 2.6 to 2.4) was **not re-run**.

### 1.4 Spine S4: Dario's dilemma and the credit numbers (pass)

The code output (`dario_dilemma`, `λ_true = 0.10`):

| `λ_invest` | Loss | Policy at that belief |
|---|---|---|
| 0.02 | 26.19% | `φ = 0.138`, `X = 0.00552` |
| 0.08 | 0.65% | |
| 0.12 | 0.43% | |
| 0.18 | 4.15% | |
| 0.20 | 5.63% | |
| 0.50 | 22.58% | `φ = 0.972`, `X = 0.00334` |

- Levered (`ℓ = 0.4`): losses of 26.15% and 21.39%, and five-year default probabilities of 0.64%, 0.79% and 5.04%.
- Spreads at `(X, K, φ) = (0.1, 1, 0.5)`: 0.0, 11.7, 41.3 and 97.1 bps; default probabilities of 0.63%, 1.80%, 4.85% and 12.98%.
- Spreads rise in φ (38.9 → 46.3 bps for φ 0.3 → 0.7 at `ℓ = 0.4`) while default probabilities fall (6.26% → 4.45%), confirming `_valuation.qmd:7`.
- Duopoly dilemma: 38.3% and 17.3%.
- The option value in λ has its minimum at `λ ≈ 0.025`, and its convexity changes sign near 0.075–0.085 on the 80-point grid.

**Pass.** Every prose number above traces to code. However, one sentence misquotes these numbers (Issue 14).

### 1.5 Lean package (pass: builds, faithful, but thin)

`lake build` succeeds. `#print axioms` on `alloc_foc_closed_form`, `unique_crossing`, `K_foc`, `net_threshold_rearrange` and `rpow_solves_euler_iff` returns `[propext, Classical.choice, Quot.sound]`. I read every theorem statement against the paper. They are faithful: no green build of the wrong statement. They are also mostly shape lemmas on abstract reals: for example, `XD_increasing_leverage` proves monotonicity of `M(coef·ℓ+base)/A`, not that this is the smooth-pasting boundary.

Three gaps should be stated where the paper advertises the formalisation (`_appendix.qmd:70`):

- the default-boundary closed form `@eq-default-boundary` is not derived from smooth pasting in Lean (only the investment trigger is);
- the comparative statics of `φ̲` in `α`, `μ_H − μ_L` and `r` (`_model.qmd:252`) are not formalised;
- the "m" formula is not formalised as a derivative (the README states this, but the appendix paragraph does not).

These are honest omissions. The fix is one sentence (Minor, Issue 24).

### 1.6 SymPy notebook (has issues: stale and contradicts the paper; Issue 4)

The notebook runs without errors (the only noise is a jupyter ZMQ teardown message). However:

- `notebooks/model_derivation.ipynb` line 845 (markdown, §4 "When is A_1 = 0?") states: "The homogeneous term A_1 = 0 when no interior trigger exists in regime L. This happens when Φ_L ≥ 1. Economically: the option to wait is so valuable that the firm never exercises in L."
- Line 884 prints "The simplified F_L = C·X^{β_H} IS valid at baseline."
- The completeness audit also cites a stale "α ∈ [0.20, 0.60]" admissible range, against the (A2) window (0.356, 0.534).

The paper (`_model.qmd:140`, `_appendix.qmd:141`) explicitly says the opposite: `A_1 = 0` is a convention, not implied by (A3), and the exact `A_1 ≈ −1.01×10⁴`. See Issue 4.

### 1.7 Code and figure hygiene (minor issues)

- `figures/paper.py:238, 311, 434` catch `ValueError`/`RuntimeError` and `continue`/`pass`. A grid point at which the strict single-crossing check fails would therefore silently become a gap in `@fig-default-boundaries` and `@fig-competition-effect`, rather than stopping the build. That sits uneasily with the claim at `_appendix.qmd:327` that the check "is enforced on every path that produces a reported number". The curves I inspected are complete, so this is latent (Issue 25).
- `valuation.py:846–851`, the duopoly-dilemma benchmark: see Issue 9.
- Tests: 393 pass; paper numbers are pinned in tests (`TestPaperNumbers`, `TestAppendixERobustness`). Good practice.

---

## Part 2: Paper review

### Content

**Contribution.** The core idea is genuinely new and well suited to Management Science: a single allocation decision, φ, moves continuation value (and hence the default boundary) and liquidation collateral in opposite directions. The role-invariance result (Proposition 3(ii)), with its exact factorization `f'(u) = αu^{α−1}s(2−s)`, is clean.

**The model's central economic object is fragile.** Specifically:

1. **Issue 1 (pre-switch investment is not optimal in the exact model).** See the summary above.
2. **Training is a flow, so "training" is really idle capacity pre-positioned for the post-AGI market** (`_model.qmd:33–39`; `@tbl-domains` row "Training as a flow"). Under free one-period reallocation, the pre-switch φ collapses to the 0.01 bound (`@tbl-dynamic-phi`, `_appendix.qmd:523`). The φ* = 0.70 that drives faith-based survival, the belief inversion and Dario's dilemma therefore exists only because compute cannot be re-purposed at the switch. The paper does concede (`_discussion.qmd:26`) that its φ* is an upper bound. However, the label "training", and the reading of φ̂ as revealing beliefs, needs the accumulation story that the model lacks.

**Calibration content is thinner than the abstract implies** (Issues 2 and 3).

**Descriptive versus causal discipline is generally excellent.** The paper carefully labels conventions, numerical findings and stress-test parameters. At times the caveats are so dense that the reader loses the argument (see Writing, pass 2).

### Writing quality: pass 1 (grammar, typos, LaTeX)

The PDF builds with no unresolved references or citations. Specific defects:

- `_valuation.qmd:25`: "to lose the 23% that the conservative firm loses at one fifth of it" is wrong; the conservative firm loses 26% at one fifth (Issue 14).
- `_introduction.qmd:7`: the Musk footnote says "post on X, 2025", but status id 2025124840806514916 decodes to 2026-02-21 (Issue 19).
- `_calibration.qmd:7`: "the range implied by Hassabis's public statements (λ ≈ 0.10–0.15)" has no citation (Issue 18).
- `@fig-investment-dilemma` (generated by `paper.py:734`): the red "Overinvestment (aggressive)" annotation is drawn over the solid ℓ = 0 curve near λ ≈ 0.27–0.30 (Issue 26).

### Writing quality: pass 2 (flow and consistency)

- The headline numbers agree across the abstract, introduction, body and conclusion: 43%, 26% versus 6%, eight times, 0.70, 0.18, 0.32.
- `_discussion.qmd:22` cites `@sec-calibration` for preemption cutting the leader's trigger; it should cite `@sec-duopoly` (Issue 20).
- `_appendix.qmd:441` ("what drives the heterogeneous investment behavior analyzed in @sec-valuation"), `_calibration.qmd:7` ("cross-sectional variation analyzed in @sec-valuation") and `_appendix.qmd:564` ("illustrative inversions in @sec-calibration and @sec-valuation") all point to analysis that `@sec-valuation` does not contain (part of Issue 2).
- The policy discussion appears twice, in `_discussion.qmd:22` and `_appendix.qmd:554`, in overlapping terms (Issue 23).
- `_appendix.qmd:379` says "For α > 0.67, the full two-term solution must be used". This implies that the one-term form is *valid* below 0.67, contradicting Step 5b (Issue 5).

### Writing quality: pass 3 (notation)

- **Leverage.** The model defines `ℓ = P/I(K)` (`_model.qmd:226`; figure axes "D/I"), whereas `@tbl-firms` (`_calibration.qmd:27`) and `@tbl-parameters` (`_appendix.qmd:36`) define it as "debt / total capital" (Issue 17).
- **Symbol reuse.**
  - `b` is both bankruptcy cost (`_model.qmd:282`) and total cost `b(K)` (`_calibration.qmd:15`, `_appendix.qmd:437`).
  - `g` is both the allocation function `g(φ)` and the scale-gap index (`@tbl-notation`).
  - `ρ` is `φ*`'s ratio (`@eq-phi-star`) and also the hazard-adjusted rate in IA-E (`_appendix.qmd:519`).
  - `Δ` is the hazard-adjusted rate and also `Δ_F` (the dilution drop).
  - `L(·)` is the leader value while L is also the regime.
  - `F` is the follower option value and also the single-firm option value.

  Rename where cheap: for example `κ_b` for bankruptcy cost, `G` for the scale-gap index, and `ρ_φ` for the allocation ratio (Issue 22).
- `@tbl-domains` uses "β_H dilution" before it is defined in the text.

### Figures

I traced `@fig-lambda-option-value`, `@fig-investment-dilemma`, `@fig-default-boundaries` and `@fig-competition-effect` end to end (caption → `paper.py` → model → my re-computation).

- The captions match the producers: grids (80 points on [0.005, 0.8], 40 leverage points, 30 σ points), the "X = 0.002 below every trigger" statement (the minimum trigger on the grid is 0.00314 at λ = 0.8), the parameter values, and the line styles.
- The prose descriptions match what the figures show.
- No orphan figure files: three slide-only figures are documented in `paper/AGENTS.md`.
- `@fig-lambda-option-value` underpins prediction 3, but it plots the *pre-investment option* value, while the prediction concerns the equity value of *installed* labs (Issue 16).

### Tables

- `@tbl-firms`: I recomputed all four implied-λ bands at `r = 0.12` and they match. However, the leverage and WACC rows feed no reported number (Issue 2).
- `@tbl-domains`, `@tbl-elasticities`, `@tbl-dynamic-phi`, `@tbl-fixedpie` and `@tbl-duopoly-dilemma`: the in-text numbers match their cells. I verified the `@tbl-duopoly-dilemma` cells.
- `@tbl-duopoly-dilemma` is not an equilibrium object (Issue 9).

### Robustness

- The ±25% one-at-a-time sweep (`_appendix.qmd:499–503`) is honest about inadmissible draws (5 of 18).
- Most sweeps are bounded by the narrow (A2) window: `r ∈ (0.097, 0.135)` and `α ∈ (0.356, 0.534)`. Three of the four archetype WACCs, and one of the paper's own sweep directions on four parameters, fall outside it. The model is therefore well-posed only in a narrow sliver of parameter space near a degeneracy (`dlnK*/dlnα ≈ 24`). The paper says so, but should treat it as a limitation of the design rather than of the calibration (Issue 10).
- The unrestricted and precommitted re-checks of Numerical Finding 1 are a real strength. They show that the *ranking* (pessimism is costlier) survives every version, which is stronger than the reduced model alone.

### Journal fit

- **Management Science (Finance department) is appropriate.** The cross-disciplinary operations-and-finance framing (capacity, flexibility, Van Mieghem and Chod–Rudi) fits, and the transparency on approximations fits the journal's culture.
- **The bar is rigor plus economic insight.** A referee there will focus on Issue 1, and on whether the closed forms are worth having once they are known to describe a dominated policy.
- **Length.** The blind manuscript is 45 pages at 1.5 spacing (per `submission/README.md`), against a 32-page cap for invited revisions. The main text is dense with caveats that belong in `@tbl-domains` or in the IA.
- **Fallback.** If the Issue 1 restructuring is not done, JEDC (on the authors' ladder) is the most natural home for a paper whose contribution is a carefully documented solution convention.

---

## Summary of issues

### Critical

1. **The paper's pre-AGI investment policy is dominated by waiting, in the model's own exact versions, at baseline.**
   - Where: `_appendix.qmd:363` (pure switching 1.741e-3 against 1.621e-3 unrestricted; 1.619e-3 against 1.615e-3 even within the precommitted class); `_appendix.qmd:147`; `_model.qmd:140, 169, 177`; abstract `index.qmd:22` ("analytical investment triggers").
   - What happens: the L-regime trigger `X*`, the L-regime preemption game, the entry-time distance to default, and the optimistic branch of Numerical Finding 1 (zero cost in the unrestricted problem) are objects of a pricing convention, `A_1 = 0` with `β_H` exponents, that is not the solution of the stated HJB (the coefficient is 16.5 against Γ = 21.1).
   - What the main text discloses: only "value loss 2.6% / 6.9%" (`@tbl-domains`). It never says that the policy is beaten by the trivial strategy of never investing pre-switch.
   - Fix, preferred: make the precommitted-scale piecewise problem, which IA-B says has a closed form, the primary single-firm model; keep φ* (unchanged) and report triggers from it. A time-to-build or capacity-lag story justifies precommitment.
   - Fix, minimum: state in the introduction and in `@sec-conventions` that at baseline waiting for the switch dominates the convention's policy. Explain economically why labs nonetheless invest pre-AGI (inference revenue needed for survival or financing, time-to-build, learning-by-doing), and identify the parameter region (e.g. λ ≈ 0.05, γ ≥ 1.9) where pre-switch investment is optimal in the exact problem, ideally calibrating there.

### Major

2. **The archetypes feed no reported investment result.**
   - Where: abstract `index.qmd:24` ("Calibration to four AI lab archetypes shows how heterogeneous beliefs … can generate cross-sectional differences in investment"); `_calibration.qmd:7`; `_appendix.qmd:441, 564`.
   - What happens: every trigger and capacity result is at the baseline WACC (`_calibration.qmd:9`). The `@tbl-firms` leverage and WACC rows enter no computation. The only archetype output is the φ̂→λ inversion, which is a closed-form identity applied to judgmentally assigned φ̂.
   - Fix: either compute archetype-level outputs (triggers, distance to default, Dario losses at each archetype's implied λ and leverage, holding r at baseline) or rewrite the abstract and the cross-references to say "maps assigned allocations into implied beliefs". Delete the stale `@sec-valuation` pointers.
3. **The implied beliefs contradict the stated beliefs the paper uses to motivate λ.**
   - Where: `_calibration.qmd:7` against `@tbl-firms` (`_calibration.qmd:26`).
   - What happens: the paper says Amodei implies λ ≈ 0.30–0.50 (and `amodei2026dwarkesh` reports 90% within 10 years, i.e. λ ≈ 0.23), and Hassabis 0.10–0.15. Yet the Anthropic-like φ̂ implies λ ∈ [0.05, 0.09] and the Google-like φ̂ implies [0.03, 0.05], 3 to 10 times lower. The paper never confronts this, though it is informative: either the static-φ model overstates training (consistent with IA-E's upper-bound result, where the dynamic model would raise implied λ), or φ̂ is mis-assigned.
   - Fix: add a paragraph comparing implied and stated λ and discussing what the gap says about the model (static φ bias) versus stated beliefs (cheap talk or signaling).
4. **The SymPy notebook contradicts the paper on the central convention.**
   - Where: `notebooks/model_derivation.ipynb` lines 845 and 884, plus the audit's α range.
   - What happens: the notebook asserts that (A3) implies `A_1 = 0`, "IS valid at baseline", and that the firm "never exercises in L". AGENTS.md presents the notebook as backing the propositions, and it would plausibly be read by referees via the public repository.
   - Fix: rewrite §4 to match Step 5b (a convention; `A_1 ≈ −1.01e4` exactly in the precommitted problem), update the audit, and re-execute.
5. **(A3) is still presented as a validity condition in places.**
   - Where: `_model.qmd:55` ("this is the condition under which the paper adopts the simplified option value"); `_appendix.qmd:76` ("It applies in the parameter region where the paper adopts…"); `_appendix.qmd:379` ("For α > 0.67, the full two-term solution must be used"); `@tbl-baseline-results` "(A3) check (≥ 1: satisfied)".
   - What happens: all of these suggest that (A3) licenses the convention. Step 5b says it does not.
   - Fix: either drop (A3) from Assumption 1, or restate it as an economic description ("L-regime revenue alone cannot justify a standalone scale") with no role in the solution, and delete the α > 0.67 sentence.
6. **Proposition 3(iv) is an artifact of the acknowledged financing subsidy.**
   - Where: `_model.qmd:304`, `_model.qmd:262`.
   - What happens: the leverage effects on `K_F`, `X_F*` and `X_P` arise because par debt at `r_c < r` transfers 23% of `I` to equity at ℓ = 0.4 (`_appendix.qmd:321`). Putting a convention-driven comparative static inside a numbered proposition invites the objection that the paper proves properties of mispriced debt.
   - Fix: move (iv) out of the proposition, or recompute with fairly priced debt (coupon set so that `D = ℓI` at issuance) and report what survives.
7. **The credit-risk numbers are evaluated at an arbitrary point far from the model's policy.**
   - Where: `_valuation.qmd:7`, `_appendix.qmd:630`, `@fig-credit-risk`.
   - What happens: `(X, K, φ) = (0.10, 1, 0.5)` has K about 150 × K* and X about 21 × X*. Under the paper's own normalization argument (`_calibration.qmd:38`), the spreads at such a point carry no unit-free meaning, yet 0/12/41/97 bps appear in the main text.
   - Fix: evaluate at entry `(X*, K*, φ*)` (or the leader's `(X_P, K_L)`) for each ℓ, as is already done for the Dario's dilemma default probabilities, or drop the bps levels from the main text.
8. **The "training" label and belief inversion rely on the flow assumption.**
   - Where: `_model.qmd:33–39`, `@tbl-dynamic-phi` (`_appendix.qmd:523`).
   - What happens: with costless one-period reallocation, pre-switch φ falls to the bound. φ is therefore "capacity reserved for the post-AGI market", not training that builds a capability stock.
   - Fix: either add a minimal stock version (H revenue depends on cumulative φK, which `_appendix.qmd:533` argues restores φ*) as a solved robustness exercise, or reframe φ in the introduction as pre-positioned post-AGI capacity, with the training interpretation as motivation.
9. **The duopoly Dario's dilemma (38% and 17%) is not computed in the paper's equilibrium.**
   - Where: `_valuation.qmd:39`, `@tbl-duopoly-dilemma`, `valuation.py:846–851`.
   - What happens: the correct-belief benchmark is *simultaneous* symmetric entry at the single-firm `X*` with `K*`. Proposition 3 says this is not the equilibrium (the equilibrium has preemption at `X_P`, and the follower at `X_F ≈ 0.12` with `K_F ≈ 0.26`). The follower also enters at its single-firm trigger without solving its follower problem. "Competition raises both losses" is therefore a statement about an ad hoc benchmark.
   - Fix: compute the mismatch inside the preemption equilibrium (both roles solved, the mismatched firm best-responding under its belief), or demote the result to IA-E with an explicit "non-equilibrium benchmark" label and delete the main-text sentence.
10. **Admissibility narrowness is a design limitation, not just a calibration fact.**
    - Where: `_calibration.qmd:9, 13`; `_appendix.qmd:381–385, 501`.
    - What happens: (A2) holds only for r ∈ (0.097, 0.135) and α ∈ (0.356, 0.534). Three of the four archetype WACCs violate it, and the baseline sits near the boundary where `K*` explodes (elasticities of about 20–29).
    - Fix: say plainly in `@sec-conventions` or `@tbl-domains` that the capacity problem is well-posed only in this sliver, and why (pure power revenue against linear-plus-power cost). Consider a revenue or cost specification with a wider interior region (e.g. `δK` replaced by `δK^η`).

### Minor

11. **Coordinate dependence of the dilemma headline.** `_introduction.qmd:17` and `_valuation.qmd:37` juxtapose 26% at λ = 0.02 (5× below) with 6% at λ = 0.20 (2× above). That is neither the additive match (0.18: 4.15%) nor the log match (0.50: 22.6%). Use one stated metric in the introduction, preferably giving both the additive (26 vs 4) and log (26 vs 23) pairs.
12. **The generality of Numerical Finding 1 is overstated.** "for the same magnitude of mismatch" (`_valuation.qmd:25`) is verified across draws only at `λ_true(1 ± 0.8)` (`_appendix.qmd:265, 503`). Rephrase it to "at the matched pair ±0.8 λ_true and locally (W''' > 0)".
13. **"Fully analytical" is overstated.** "Propositions 1 and 2 are fully analytical" (`_model.qmd:316`) sits awkwardly with Proposition 2(iii) relying on numerical single-peakedness against an asymmetric rival (`_appendix.qmd:209`), and with Proposition 2 resting on the single-boundary approximation. Qualify it.
14. **A sentence misquotes the losses.** `_valuation.qmd:25` says "to lose the 23% that the conservative firm loses at one fifth of it". The conservative loss at one fifth is 26.2% (verified). Fix to "to lose 23%, still below the 26% the conservative firm loses at one fifth of it".
15. **Proposition 2's maintained assumption contradicts its statement.** `_appendix.qmd:151` says "Capacity … fixed at their optimal values", whereas the proposition (`_model.qmd:240`) holds at *any* fixed `(K, φ)` and part (ii) is explicitly about non-optimal φ. Align the two.
16. **Prediction 3 cites the wrong object.** `_discussion.qmd:15` concerns the equity value of installed labs but cites the pre-investment option value (`@fig-lambda-option-value`). For an installed firm at fixed φ, `A_eff = Π_H + (Π_L − Π_H(r−μ_L))/Δ` is increasing and concave in λ whenever φ > φ̲, for *all* λ. That is a cleaner and stronger basis than the option-value curve, and it removes the λ ≲ 0.085 caveat.
17. **Leverage is defined two ways.** It is "debt / total capital" in `@tbl-firms` (`_calibration.qmd:27`) and `@tbl-parameters` (`_appendix.qmd:36`), but `P/I(K)` in the model (`_model.qmd:226`). Harmonize.
18. **The Hassabis-implied λ range is uncited** (`_calibration.qmd:7`), and the timeline-to-λ mapping (for example Amodei to 0.30–0.50) is not explained. Add the citation and the mapping rule (e.g. `λ = −ln(1−p)/T`).
19. **The Musk footnote year is wrong** (`_introduction.qmd:7`): the post is dated 2026 (Feb 21), not 2025.
20. **Wrong cross-reference:** `_discussion.qmd:22` should cite `@sec-duopoly`, not `@sec-calibration`.
21. **Missing literature and unused bibliography entries.**
    - `weeds2002strategic` (real-options R&D race with strategic delay, directly relevant) and `sundaresan2015dynamic` (investment and capital structure with debt overhang) are in `references.bib` but never cited.
    - The authors should also consider Lambrecht (2001, RFS) on debt financing and duopoly entry and exit, the closest antecedent for preemption plus default. Other candidates are Grenadier (1996, JF) on strategic overbuilding, Mauer and Sarkar (2005) on investment and financing, and Korinek and Vipra on scaling and market structure in AI.
    - Verify these against Zotero before adding them; I did not check metadata.
22. **Symbol reuse** (`b`, `g`, `ρ`, `Δ`, `L`, `F`; see notation pass 3). Rename where cheap.
23. **Duplicated policy discussion** (`_discussion.qmd:22` and `_appendix.qmd:554`). Keep one.
24. **The Lean scope paragraph should say what is not formalised.** `_appendix.qmd:70` should add that the default-boundary smooth-pasting derivation and the `φ̲` comparative statics in (α, r, μ_H − μ_L) are not formalised.
25. **Silent exception handling in figure generators** (`paper.py:238, 311, 434`). Log, count and fail on dropped grid points so that a failed single-crossing check cannot silently thin a figure.
26. **Annotation overlap** in `@fig-investment-dilemma` (`paper.py:734`). Move the "Overinvestment" label off the curve.
27. **H-regime value share.** `_appendix.qmd:273` ("approximately 70% of A_eff") should be stated as the exact identity: H-share = φ* at the optimum. This also sharpens the economic reading of Numerical Finding 1.

---

## Overall recommendation

**Major revision before submission.** The mathematics, the code and the Lean proofs are sound, and the transparency is exemplary. But Issue 1 goes to the economics: at baseline, the paper's own exact benchmarks say a firm should wait for AGI rather than invest beforehand, and the main text does not say so. Rebuilding the single-firm block on the precommitted-scale closed form (or calibrating where pre-switch investment is optimal), together with Issues 2–4 and 9, would make the paper competitive at Management Science. Without them, a referee will find Issue 1 in IA-B and treat it as decisive.
