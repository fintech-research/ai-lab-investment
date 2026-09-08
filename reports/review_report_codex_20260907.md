# Pre-submission review: Management Science

**Paper:** *Capacity, Training, and Default in the Race to Artificial General Intelligence*
**Review date:** September 7, 2026
**Reviewed checkout:** `048420d`, including the working-tree manuscript and existing submission PDFs
**Recommendation:** Major revision before submission. Management Science is a defensible aspirational target, but the present manuscript is not ready.

## Executive assessment

The paper has a useful economic question: how does allocating a common capital stock between current cash flow and future capability affect investment and survival? Its strongest material is the allocation formula, the distinction between continuation value and liquidation collateral, and the attempt to quantify the cost of mistaken timeline beliefs. The explicit qualifications concerning par debt issuance, leader scale, and reduced-form stopping values are valuable. The code and formal verification are substantial assets.

However, successful algebra checks do not establish that the priced objects solve the stated dynamic investment game. There are remaining inconsistencies at precisely that boundary. The principal issues are:

1. The paper repeatedly treats a derivative with respect to optimism as a derivative with respect to training, producing an incorrect unconditional credit-risk prediction.
2. The purported exact stopping benchmark fixes high-regime capacity even when a regime switch arrives above the high-regime investment trigger. This leaves a feasible, profitable scale deviation unexplored.
3. The levered leader value does not satisfy the default and follower-entry boundary conditions attributed to it.
4. Some comparative statics, robustness interpretations, and source attributions are incorrect, despite the baseline numbers reproducing.
5. The existing anonymous manuscript is 67 pages, before its separate 49-page e-companion. The paper needs substantial consolidation, not just copyediting.

I would preserve the central allocation/default mechanism, repair its mathematical domain, and make the numerical benchmark economically coherent before adding further extensions. More robustness tables built on the same inconsistent value functions would not resolve the main concerns.

## Scope and verification performed

I reviewed the main Quarto sections, Internet Appendix, model and calibration implementation, relevant tests, figure generators, Lean theorem statements, and submission materials. I did not consult the contents of the existing files in `reports/`. Source locations below refer to the reviewed checkout; line numbers will move after edits.

| Check | Result |
|---|---|
| Python test suite | **Pass:** `uv run pytest --cov=ai_lab_investment --cov-report=term-missing -q`: **356 passed**, 129.11 seconds. |
| Combined statement/branch coverage | **88%** overall; base model 91%, duopoly 85%, valuation 88%, piecewise option 80%, revealed beliefs 87%, paper figures 97%, robustness 91%. |
| Full configured analysis | **Pass:** invoked the Hydra pipeline with every configured task enabled and output redirected to a temporary directory; all phases and the robustness sweep completed, approximately 27 seconds. This was the pipeline callable, not a fresh dependency installation or a literal `just run-pipeline` invocation. |
| Lean | **Pass:** `lake build` completed successfully, reporting 8,572 jobs. Existing dependencies were sufficient; no cache download was needed. |
| Formal-proof axioms | **Pass:** scanned project proof sources for `sorry` and custom `axiom` declarations; none found. Printed dependencies of 44 named theorems/lemmas across the six substantive proof files: only `propext`, `Classical.choice`, and `Quot.sound`. |
| Figures | Viewed all 11 PNGs; traced the code for the principal figures; rendered and inspected the comparative-statics PDF as well. PNG and PDF versions use different font styles. |
| Submission PDF | Inspected metadata, extracted text, and rendered the first page of the existing blind manuscript. Main PDF: **67 pages**; separate e-companion: **49 pages**; both dated August 8, 2026. This was not a fresh render or an exhaustive page-by-page typography audit. |
| External verification | Checked current Management Science guidance and selected original research/data sources. This is a targeted source audit, not verification of every bibliography entry or press quotation. |

One additional `uv` invocation encountered the OS sandbox boundary on its cache. Subsequent numerical probes used the existing `.venv/bin/python`, which required no cache access or permission changes. The pipeline completed despite font-cache warnings. No manuscript or model files were edited in this review.

## Critical issues to resolve before submission

### C1. Separate optimism from training in the survival mechanism

**Status: Has issues.** Locations: `paper/_model.qmd:230–254`, `paper/_discussion.qmd` prediction 1, `paper/_conclusion.qmd:9`, `paper/_literature.qmd`, and the abstract.

Proposition 2(ii) correctly concerns **the partial derivative of the default boundary with respect to λ, holding the investment policy fixed**. Its thresholds, φ̲ and φ̃, are not thresholds for the effect of increasing φ. Yet the conclusion uses φ̲ ≈ 0.18 to argue that “at baseline a larger training allocation lowers the default boundary,” and prediction 1 says higher training fractions should imply lower default probabilities conditional on leverage.

In monopoly, with fixed capacity, debt, and λ,

\[
X_D(\phi)=\frac{MN}{A_{\rm eff}(\phi)},\qquad
\frac{\partial X_D}{\partial\phi}
=-\frac{MN}{A_{\rm eff}(\phi)^2}\frac{\partial A_{\rm eff}}{\partial\phi}.
\]

Consequently, X_D decreases below φ*, is stationary at φ*, and increases above φ*. At baseline the optimum is φ* = 0.700856. Direct evaluation at K = 1 and leverage 0.40 gives:

| Training fraction | Default boundary |
|---:|---:|
| 0.50 | 0.030314 |
| Approximately 0.7009 | 0.029698 |
| 0.80 | 0.029889 |
| 0.90 | 0.030693 |

Thus more training does not generally improve survival, even at the baseline primitives. The paper's own aggressive-mismatch example depends on this reversal. Also, the claim at `_model.qmd:252` that the induced increase in optimal φ “further lowers” X_D is not a separate first-order channel at the allocation optimum: A_eff,φ = 0 there, so the envelope term vanishes in the monopoly/common-allocation case.

**Fix:** distinguish three experiments throughout: increasing λ at fixed policy; increasing φ at fixed λ; and comparing re-optimized policies across beliefs. State prediction 1 locally for under-trained firms, with capacity, demand, beliefs, and rival policy controlled, or state a non-monotone prediction. Rewrite the abstract and conclusion accordingly. Put the sign diagram for these experiments in the main text; it is more useful than an unconditional slogan.

**Related proof-domain issue:** `_appendix.qmd:205` imports single-firm strict concavity and the single-firm φ* directly into the unilateral duopoly allocation problem. Rival shares change with own φ; Proposition 1 does not establish that claim. At equal capacities and baseline primitives, directly maximizing A_eff,i gives own optimal φ ≈ 0.8428 when rival φ = 0.10, but ≈ 0.6049 when rival φ = 0.95. The single-firm optimum is not the universal maximizer. Restrict the argument to common equilibrium allocation, or state the iso-boundary result locally wherever A_eff,φ > 0. Equal capacities alone also do not imply equal L- and H-regime shares when allocations differ (`_model.qmd:238`).

### C2. The “exact” stopping benchmark retains a material scale restriction

**Status: Has issues.** Locations: `paper/_appendix.qmd:323–333`; `src/ai_lab_investment/models/piecewise_option.py:110–153`; `base_model.py:346–355`.

The piecewise solver uses the high-regime payoff

\[
P_H(X)=A_H(K_H^*)^\alpha X-\delta K_H^*/r-c(K_H^*)^\gamma
\]

above X_H*, with K_H* fixed at the scale chosen for entry at X_H*. This is correct for a project committed to that scale. It is not the unrestricted exercise payoff of a firm that has not invested and can choose capacity when the regime changes at X > X_H*.

That firm can instead choose the scale maximizing immediate NPV. Its first-order condition is

\[
\alpha A_H X K^{\alpha-1}=\delta/r+c\gamma K^{\gamma-1}.
\]

A direct baseline counterexample at X = 2X_H* = 0.005565924:

| Object | Fixed high-regime policy | Re-optimized immediate scale |
|---|---:|---:|
| K | 0.00672664 | 0.01617164 |
| Exercise NPV | 0.01031265 | 0.01171976 |

The feasible scale adjustment raises the exercise payoff by about **13.6%** at this state. The high-regime derivative with respect to K is therefore not zero at the capacity used by the supposed exact forcing term. Such states are reachable when the switch occurs while the low-regime firm is waiting.

**Fix:** use the optimized high-regime exercise envelope in the forcing term and check the low-regime exercise envelope as well. Solve the associated variational inequality and verify payoff dominance and the continuation/stopping inequalities. Alternatively, explicitly describe the calculation as exact **within a precommitted-scale policy class**, and remove claims that its percentages measure error against the unrestricted optimum. The finite-difference/LCP check verifies the implemented obstacle problem; it does not establish that the obstacle is economically unrestricted. Reassess the 2.6% policy-loss and 40%/0.5% mismatch claims after this correction.

### C3. The levered leader value violates the asserted boundary conditions

**Status: Has issues.** Locations: `src/ai_lab_investment/models/duopoly.py:1047–1094`; `paper/_appendix.qmd:215–233`; `paper/_model.qmd` equity and preemption discussion.

Before follower entry, `_leader_value_at` starts from monopoly equity including its monopoly default option, then subtracts a discounted **revenue** drop at follower entry. It does not solve the default problem for a leader anticipating entry, or match the change in the entire equity claim.

Two direct baseline probes at leverage 0.40 demonstrate the mismatch:

- At the reported leader default boundary, adding back the sunk equity contribution to `_leader_value_at` gives going-concern equity **−0.000120612**, although the paper requires it to equal zero.
- The leader entry NPV immediately below follower entry is approximately **0.046810450**, versus **0.046811012** at follower entry. The small jump is consistent with switching from a monopoly default-option coefficient to a duopoly coefficient without matching the claims.

These are not failures of the standalone Leland smooth-pasting formula; they arise when that formula is combined with the leader's entry-dilution adjustment. In particular, the paper's descriptions of a nonnegative going-concern leader claim and continuity are not satisfied by this implementation. The reported small value jump does not invalidate the zero-leverage concavity proof, but the negative equity at the reported default boundary directly undermines the levered interpretation.

**Fix:** solve the leader's pre-entry equity/default problem with a boundary condition matching post-entry equity at X_F and value matching/smooth pasting at its own default boundary. Recompute levered preemption and distance-to-default results. If retaining the current formula, label the entire leader credit construction an approximation, quantify its error, and stop calling its monopoly boundary the optimal boundary of the anticipating leader. Add tests specifically for the leader's going-concern value and derivative at default and both sides of follower entry.

### C4. Admissibility omits the strictly positive operating cost needed for the interior scale result

**Status: Has issues.** Locations: `paper/_model.qmd:55–57,108–114`; `_appendix.qmd:91–95`; `parameters.py:124–127`; `base_model.py:610–670`.

Assumption 1 allows δ = 0, while Proposition 1 claims an interior positive capacity under A2. At δ = 0 its displayed formula gives K* = 0. More fundamentally, after substitution the reduced objective is proportional to

\[
K^{\alpha\beta_H-\gamma(\beta_H-1)},
\]

whose exponent is negative under A2's lower bound. There is no interior maximum of that reduced objective. Running the existing full solver at δ = 0 returns K ≈ **3.0590 × 10⁻⁷ = exp(−15)**, the numerical guard, as if it were a valid optimum.

**Fix:** require δ > 0 for Proposition 1 and every solver invoking this interior formula; treat δ = 0 separately if it is economically important. Explain the role of the linear operating-cost term in obtaining an interior scale. Add a rejection/boundary test; `TestValidationGuards::test_zero_delta_allowed` only checks parameter construction and misses the optimization failure. Complete the global scale proof by showing the objective tends to zero at both ends for δ > 0 and A2, with its single FOC giving the maximum.

## Major issues and concrete improvements

### M1. The declared primitives, reduced model, and figures need one consistent scope

**Status: Has issues.** The manuscript now honestly labels the A₁ = 0 construction a convention (`_model.qmd:166`; `_appendix.qmd:129–143`), including the mismatch between the forced-ODE coefficient and smooth-fit coefficient. Preserve that disclosure. However, merely defining a pricing convention does not establish a time-consistent stopping game under the original regime-switching GBM. The abstract's analytical-trigger language should explicitly refer to the reduced model, and the unrestricted model should have a clearly separate numerical solution or policy-class restriction.

`create_lambda_option_value()` (`figures/paper.py:213–270`) calls **simple-mode** `option_value_L()` and plots the ODE particular coefficient C. It does not plot the full optimized allocation value used for the central economic results. Its curve is concave throughout the plotted positive-λ range, whereas the discussion describes a low-λ convex region of the full model. The footnote at `_model.qmd:104` identifies the H-regime subproblem but does not adequately distinguish this L-regime figure. Replace the figure with the full-model value and allocation, or label it explicitly as a simple-mode coefficient illustration and remove its use as evidence for full-model valuation curvature.

Remark 3 and the sensitivity prose also describe value as monotonically increasing in λ without a low-λ qualification, despite the appendix acknowledging a low-belief reversal in related derivatives. Derive and state the relevant domain rather than applying the policy-range description globally.

Finally, `_model.qmd:124` says that in the duopoly “the endogenous arrival rate adds a further interaction.” The paper's λ is exogenous and `_discussion.qmd` explicitly leaves endogenization unsolved. The code contains an optional ξ extension, but ξ = 0 in the paper baseline. Remove this leftover statement.

### M2. Correct the Tullock interpretation and rename the alternative contest

**Status: Has issues.** Locations: `_model.qmd:184–196`; `_appendix.qmd:439–451`; `duopoly.py:191–228`.

With capacity ratio z and α = 0.4, the contest share is s(z) = z^α/(1 + z^α). A firm with four times its rival's relevant capacity receives a contest share **0.6352**, below its physical-capacity fraction 0.8. Thus the claim that the larger firm's share exceeds its capacity ratio is false in the maintained α < 1 region. The contest share is concave in own capacity, not convex as stated. Actual revenue shares differ from the contest multiplier because firm revenue also contains its own capacity term; define these distinct objects carefully.

The equal-capacity aggregate-revenue statement should retain the relevant allocation factor: in L it is X[(1−φ)K]^α, not XK^α unless K is redefined as inference capacity. The quadratic-mean expansion calculation in effective capacities is useful and can remain with the benchmark clearly fixed.

Do not infer uniqueness of this dynamic entry/default game or absence of rent over-dissipation from α < 1 in a contest success function. Supply model-specific conditions; the paper itself elsewhere labels uniqueness partly computational.

The “fixed-pie” alternative reduces to π_i = Xy_i/2. Its total pie still changes with capacities, and own post-entry revenue becomes independent of rival capacity. It removes the original asymmetry premium **and** a strategic externality; it is not a clean experiment holding the market prize fixed while retaining the same competitive incentives. Rename it an arithmetic-mean industry-revenue benchmark, report which derivatives disappear, and avoid interpreting every difference as the isolated effect of pie expansion. A genuinely exogenous-prize or Cournot comparison is optional but would provide stronger structural robustness.

### M3. Repair Dario's-dilemma comparisons and state what the robustness actually checks

**Status: Baseline arithmetic passes; interpretation has issues.** Locations: `_valuation.qmd:17–41`; `_appendix.qmd:253–275,333,429–483`; `valuation.py:299–498,713–822`; `piecewise_option.py:645–694`; `robustness.py:157–174`.

The reproduced unlevered losses are **26.1855%** at λ_invest = 0.02, **5.6333%** at 0.20, and **22.5783%** at 0.50. Those support the rounded headline numbers. They do not constitute an equal-distance comparison: 0.02 and 0.20 differ from 0.10 by 0.08 and 0.10. `_appendix.qmd:333` explicitly calls this a mismatch of ±0.10, which is wrong.

Use a matched pair such as **0.02 versus 0.18**. The existing evaluator gives **26.1855% versus 4.1486%**, so this correction strengthens the baseline illustration without changing the model. Report additive-error and log-intensity-error comparisons separately: asymmetry depends on the coordinate in which errors are deemed equally large.

The Taylor sign is correct locally: for a fixed-reference smooth W,

\[
\Delta V(-h)-\Delta V(+h)=\tfrac13 W'''(\lambda_{\rm true})h^3+O(h^5).
\]

A positive third derivative at the optimum does not prove the ranking for every finite mismatch. The implemented ±25% sweep compares selected unequal belief multiples and does **not** calculate W'''; its outputs cannot substantiate the appendix's claim that this derivative was verified at every draw. Add an explicit fixed-X₀ derivative diagnostic with step-size checks and a grid of matched errors, or narrow the claim to the comparisons actually computed.

The reduced evaluator chooses X₀ = 0.5 min(X*_true, X*_invest) separately for each comparison. Percentage losses are unaffected there because the common power cancels, but raw W values across λ do not share one reference state. In the piecewise evaluator that cancellation is unavailable, and `dilemma_bias()` likewise changes X₀ between pairs. Hold one sufficiently low X₀ fixed for an entire loss curve and sensitivity analysis.

The one-sided duopoly experiment is explicitly not the Proposition 3 equilibrium; retain that warning in the main text. Its loss ratio **falls** from 26.19/5.63 ≈ 4.65 to 38.31/17.33 ≈ 2.21. Competition raises both losses but weakens their relative asymmetry. Replace the main text's “quantitatively reinforced” phrasing with that precise description. Also avoid saying the single-firm mismatch “loses first-mover advantage,” or that it “overbuilds”: K is belief-invariant in that exercise.

### M4. Dynamic reallocation does not verify unchanged survival thresholds or mismatch rankings

**Status: Has issues.** Locations: `_discussion.qmd` limitations; `_appendix.qmd:453–469`; `valuation.py:824–998`; `tests/test_valuation.py:585–620`.

The two-period calculation is a useful allocation-value experiment, and its static-nesting identity is meaningful. It does not solve dynamic equity/default or dynamic belief mismatch. Returning the original static φ̲ from this routine does not demonstrate that the economically relevant threshold is unchanged in the dynamic model. The corresponding table test pins the returned constant rather than establishing a dynamic survival result.

At free adjustment the reported initial allocation collapses from about 0.70 to the numerical lower bound 0.01. This is a large change in the very observable used to infer beliefs, even though gross revenue value changes by only 5.1%. In the limit of costless immediate reallocation, pre-switch training need not purchase future capability under this flow-based technology. The mechanism through precommitted training can disappear.

**Fix:** call the static allocation an upper-bound illustration for the solved two-period comparison, not a general bound on arbitrary dynamic models. Separate verified allocation/value effects from conjectures about default and the dilemma. State that κ is measured per unit of demand in the implementation, and justify the κ grid. A small gross-value gain does not establish a small distortion in training fractions or implied beliefs.

### M5. Correct comparative-statical and source-level errors

**Status: Has issues.** These are inexpensive corrections with high credibility value.

| Location | Finding | Concrete correction |
|---|---|---|
| `_model.qmd:106`; `_appendix.qmd:494` | Greater γ is said to reduce capacity, but panel (c) and the model are non-monotone. K_H* is 0.01072 at γ = 1.20, 0.00337 at 1.35, 0.00673 at 1.50, and 0.03523 at 2.00. | Describe both capacity and trigger as non-monotone on this grid. Explain that changing γ with c fixed changes marginal cost differently above and below normalized K = 1. |
| `_model.qmd:310`; `_appendix.qmd:309–311` | The volatility direction is said to survive leader re-optimization. The reported re-optimized discount is 94.3% at σ = 0.20, 86.1% at 0.25, and 87.4% at 0.30. | Retain robustness of earlier entry; withdraw robustness of monotonicity over the whole range. |
| `_appendix.qmd:137` | The standalone no-switch L problem is described using β_L+ defined with discount r + λ; it also concludes no scale is worth building from failure of interior scale. | Use the no-switch characteristic root with discount r. Distinguish failure of an interior threshold/scale parameterization from negative NPV at every feasible state and scale. |
| `_model.qmd:154` | The trigger is called implicit because A_eff depends on the optimal policy. | With explicit K* and φ*, substitution gives an explicit trigger in the reduced model. Present the allocation closed form prominently instead of obscuring it. |
| `_literature.qmd:5` | Décamps, Mariotti, and Villeneuve (2006) is described as an absorbing exogenous regime-switch model. | It studies alternative project scales under a single GBM output price, with an extension allowing a chosen switch between projects. Correct the attribution; do not equate project switching with Poisson demand-regime switching. See the [authors' paper, Section 2](https://idei.fr/sites/default/files/medias/doc/by/mariotti/irreversible_investment.pdf). |
| Abstract and introduction | Curvature is described as calibrated to scaling laws, whereas `_calibration.qmd:15` correctly says α = 0.40 is chosen and not measured by a loss exponent. | Replace “calibrated to” with “motivated by,” consistent with the [Kaplan et al. study](https://arxiv.org/abs/2001.08361) and [Hoffmann et al. study](https://arxiv.org/abs/2203.15556). |
| `_appendix.qmd:299` | States SciPy 1.14. | Reviewed environment is SciPy **1.17.0**, also consistent with the dependency floor. Report the locked replication environment. |

The introduction's executive quotations, aggregate 2026 spending forecast, and all bibliography summaries should receive a final author source audit. I have not independently certified those quotations or the complete $660–690 billion aggregation.

### M6. Strengthen calibration provenance and avoid false identification

**Status: Mixed.** The manuscript appropriately distinguishes chosen inputs, illustrative archetypes, and normalized outputs. The common-baseline and firm-WACC φ inversions are algebraically correct. The explicit standalone/pre-SpaceX xAI caveat in Internet Appendix C is appropriate for the stated historical snapshot; later developments need not invalidate a deliberately dated calibration.

There are still important attribution and interpretation problems:

- The cited [OpenAI CFO disclosure](https://openai.com/index/a-business-that-scales-with-the-value-of-intelligence/) reports **ARR** of $2B, $6B, and $20B+ for 2023–2025. It does not itself substantiate the appendix's attributed recognized-revenue pair of $3.7B/$12.5B. Supply separate sources for those quantities.
- [Epoch AI's compute analysis](https://epoch.ai/data-insights/openai-compute-spend) combines press-reported figures with an assumed two-year amortization schedule to infer approximately $2B of research compute. It explicitly cautions that the underlying figures include projections and are not fully reliable. Describe this as a documented secondary reconstruction, not primary firm disclosure or a directly observed allocation. Cloud operating spend is not owned-infrastructure CapEx.
- `_calibration.qmd:36` singles out two privately held archetypes despite the OpenAI-like reference also being private in the cited snapshot. Use consistent ownership and confidence descriptions. `_calibration.qmd:42` likewise should identify exactly which two columns its all-equity characterization concerns.
- Put the Q4 2025–Q1 2026 cutoff and “assigned allocation” label in the **main table caption**. “Observed training fraction assigned” conflates data with judgment. Conditional inversion of assigned φ values is a scenario map, not evidence that beliefs explain observed firm differences.
- The proposed dollar conversion at `_calibration.qmd:48` needs a complete unit transformation. Altering model parameter c alone changes the optimum; fixed-(X,K) credit metrics are not invariant to arbitrary cost changes. A monetary-unit conversion multiplies all monetary flows and costs consistently. Define that transformation, distinguish it from a structural c comparative static, and avoid promising that every spread is unaffected without those qualifications.

Move most heterogeneous company revenue/CapEx discussion to the appendix. Keep a compact main-text table of assigned φ, its uncertainty band, and the implied λ band. This both improves identification discipline and saves space.

### M7. Tighten numerical acceptance criteria

**Status: Has issues.** The overall engineering is good: deterministic multistart, log-capacity coordinates, A2 checks, Brent refinement, and diagnostics are sensible. There is nevertheless a specific acceptance bug in `base_model.py:38–98`.

`multistart_minimize()` counts successful starts but chooses `best_x` from **all** results, including unsuccessful ones. Callers only require `n_converged > 0`. A two-result probe with a successful objective 1.0 and unsuccessful objective 0.0 returns the unsuccessful point, alongside `n_converged = 1`.

**Fix:** select the incumbent only among finite, successful results, or separately re-run and validate any unsuccessful candidate before accepting it. Test mixed success/failure, not only the existing all-unconverged case.

Also address these narrower gaps:

- Full allocation optimization rejects φ ≤ 0.01 or φ ≥ 0.99 even though the theoretical domain is [0,1]. The optimum reaches those artificial bounds for extreme λ; the dynamic table already reports boundary solutions. Use the analytical allocation solution where available and explicit endpoint handling elsewhere.
- `solve_preemption_equilibrium(strict=True)` rejects missing brackets but can return a root with `single_crossing=False`. It counts sign transitions, not a certified complete root set. Require the claimed diagnostic on paper-producing paths and distinguish a grid check from a uniqueness theorem.
- `debt_value()` uses the continuation expression below X_D (`duopoly.py:753–795`). Define the post-default convention and return the realized recovery consistently rather than extrapolating the continuation solution.
- The capex-based belief inverter brackets only the endpoints despite acknowledging non-monotonicity. It may miss interior roots or multiplicity. This is outside the paper's retained φ-only inversion, but exploratory outputs should not be called identified beliefs.
- Update stale docstrings: simple L mode still describes never exercising as an economic result; the levered-dilemma docstring says leverage amplifies losses although the implemented total-claim metric can reduce them. The tests can pass while those descriptions remain wrong.

## Mathematical and implementation audit by result

| Item | Assessment |
|---|---|
| Proposition 1: installed coefficients, trigger FOC, K separability, allocation FOC | **Pass within the stated reduced objective and δ > 0.** `base_model.py:540–670` matches eq-a-eff and the displayed closed forms; baseline X* = 0.004721756, K* = 0.006726639, φ* = 0.700855709. C2 and C4 limit the optimality claim. |
| Proposition 2(i), (ii), (iv) | **Pass for the single-boundary formula with fixed policies, positive debt/coupon, and exogenous λ.** `duopoly.py:394–443,601–647` matches the markup derivative and both thresholds: φ̲ = 0.180149, φ̃ = 0.321898. Put the denominator-positivity condition for φ̃ in the proposition itself. |
| Proposition 2(iii) | **Has issues in its proof/domain:** see C1. A local iso-boundary slope where A_eff,φ > 0 is straightforward; global single-firm concavity cannot simply be imported with a fixed asymmetric rival. |
| Proposition 3(i) at zero leverage | **Pass conditionally:** the affine-minus-positive-power gap is strictly concave; a negative lower endpoint and positive upper endpoint give the unique crossing in the stated interval. The upper sign remains numerical. |
| Proposition 3(i) with leverage | **Has issues:** root-finding works for the implemented gap, but C3 prevents interpreting its leader boundary as the asserted optimal-default problem. A grid is evidence, not an analytical uniqueness proof. |
| Proposition 3(ii) | **Pass as an allocation FOC at common allocation under the reduced payoff:** f′(u) = αu^(α−1)s(2−s) gives the cancellation. Leader allocation is imposed through its monopoly-policy convention; follower global optimality is numerical as disclosed. Do not generalize to arbitrary rival allocations. |
| Proposition 3(iii)–(v) | **Numerical, with scope issues:** maintain numerical labels, publish exact grids and diagnostics, repair levered leader pricing, and withdraw the re-optimized volatility claim contradicted by reported points. |
| Result taxonomy | **Mostly good:** it openly distinguishes conditional, computational, and numerical results. Update domains for δ > 0, shared allocation, and the extra leader approximation. “Exact statements” should not include unqualified numerical comparative statics. |
| Lean theorem-to-equation mapping | **Pass in spot checks:** `trigger_from_boundary_conditions` derives the trigger from value matching/smooth fit; `K_foc` characterizes K^(γ−1); `alloc_foc_closed_form` solves the allocation FOC; `net_threshold_rearrange` implements the two-channel inequality; `preemption_exists`/`unique_crossing` explicitly assume their model-specific hypotheses. |
| Lean scope | **Manuscript largely passes; cover letter fails.** The formal results are meaningful conditional algebra, not vacuous proofs. They do not establish economic verification, the constrained payoff's correctness, or all numerical claims. The capacity theorem is an equivalence for the FOC, not an existence/global-optimality theorem. |
| Regime simulation | **Pass for the documented discretization:** positive GBM updates, exact one-step switch probability 1−exp(−λdt), absorbing H, and fixed figure seeds. Within-step drift uses the initial regime, so it is not an exact continuous-switch simulation; adequate for the illustrative small time step. |
| Default probability | **Formula passes for constant-drift, constant-barrier GBM.** It omits switching and is an upper bound on pre-switch default, as Appendix H discloses. Main-text 0.64%/5.04% figures should carry that qualification rather than sound like unconditional model probabilities. |
| Risk adjustment | **Requires clarification:** a common discounting convention is legitimate as a reduced-form preference criterion, but WACC plus unspecified drift risk adjustments does not itself prove absence of double-counting. State the discount operator directly; avoid claims of correct market pricing or unqualified physical-probability ordering without a specified premium. |
| Code organization | **Generally passes:** model calculations are centralized; the figure wrapper is thin. The main risk is semantic drift between legacy simple-mode outputs, full-mode paper claims, and newer validation modules. |
| Tests and edge cases | **Good but incomplete:** scalar-vs-Nelder-Mead, finite-difference boundary checks, symbolic equations, metadata parity, and printed-number tests are meaningful. Zero volatility is appropriately rejected. Missing economically important checks include C2–C4 and mixed optimizer success. |
| Reproducibility | **Pipeline passes; submission bundle incomplete for numerical replication.** The build recipe packages Lean and equations, not Python source, dependencies, and figure/table reproduction. The appendix repeatedly says numerical checks are enforced by “the replication package”; either include them or clearly distinguish the proof package from a versioned numerical supplement. |

`TestAppendixERobustness::test_duopoly_dilemma_table` pins the displayed 26/6/38/17 percentages within 0.2 percentage points, which is useful. `test_dynamic_phi_table` checks allocation cells within 0.005 and gains within 0.03 percentage points. These catch material numerical drift, but hardcoded table regressions do not validate economic assumptions. Model coverage gaps concentrate in failure branches, boundary cases, the re-optimized leader, and piecewise reporting/sweeps. Coverage is not evidence that those assumptions are correct.

## Figure review

Eight figures are included: four in the main text and four in the Internet Appendix. The remaining three are not included in the manuscript and are designated slide illustrations. No additional unexplained manuscript figure was found. Visual observations below are based on all PNGs and a PDF spot check, not a fresh full manuscript render.

| Figure | Assessment and improvement |
|---|---|
| `fig_lambda_option_value` | **Substantive issue:** simple-mode L option and coefficient C are not the full allocated option underlying the curvature discussion. Replace or clearly separate; see M1. |
| `fig_default_boundaries` | **Label issue:** X_D is the **follower's** boundary; label it X_D,F and identify both roles in the caption. Shading between X_D,F and X_F is a post-entry continuation/hysteresis band, not the entire operating region: an installed follower also operates above X_F, and a never-entered follower below X_F is still waiting. Show a separate leader boundary or remove the potentially confusing leader comparison. |
| `fig_competition_effect` | **Pass as the zero-leverage convention's output.** Model → equilibrium → X_P/X_mono trace is correct. Make the fixed-leader-scale restriction visible in the graphic/caption and do not attach re-optimized monotonicity claims to it. |
| `fig_investment_dilemma` | **Pass for reduced-form percentage losses.** Uses full-mode policies and the disclosed levered total-claim convention. Add equal-error markers and a legend/caption distinguishing delayed/early entry from capacity overbuilding. |
| `fig_option_value` | **Pass for fixed-scale H illustration.** Tangency and shading are readable. Above-trigger NPV uses the fixed trigger-scale policy; do not interpret it as the optimized capacity envelope at every X. Avoid ratios to NPV where NPV is zero or negative. |
| `fig_comparative_statics` | **Data pass, prose fails:** panel (c) shows non-monotone capacity; correct the text. The PDF is readable; the PNG has crowding near the legend and twin-axis labels. A shared legend and slightly more panel spacing would help. |
| `fig_growth_decomposition` | **Formula and labels broadly pass for its explicitly artificial index.** Stacking gross installed value with a net-project shortfall invites a valuation-decomposition reading despite the caveat. Consider dropping the stack or the whole exhibit; it contributes little to the core mechanism. |
| `fig_credit_risk` | **Pass for fixed X = 0.10, K = 1, φ = 0.5.** Add “no-switch upper bound” to the probability label/caption and “over r” to the spread label. These are normalized stress scenarios, not observed firm credit risk. |
| `fig_sample_paths` | **Pass as an illustration:** readable log-demand paths and H trigger, with seed 42. Legend should explain the switch markers and line-opacity change. Not in the paper. |
| `fig_lambda_timeline` | **Pass:** expected time 1/λ and five-year probability 1−exp(−5λ) are correct. Not in the paper. |
| `fig_firm_comparison` | **Caution:** graphics reproduce assigned inputs, but juxtaposed CapEx/revenue bars invite comparison of non-harmonized quantities. Use explicit “illustrative archetypes” labeling; avoid interpreting the ranking empirically. Not in the paper. |

## Paper quality and Management Science positioning

### Contribution and structure

**Motivation: Pass with tightening.** The capital-allocation question is consequential and accessible. The introduction takes too long to reach the mechanism and repeats the same executive narrative and three-part result summary later in the paper. Lead with the common-capacity allocation and financing tension, then use one short industry example.

**Literature: Broad coverage, but revise precision.** The bibliography engages the requested real-options, strategic-investment, R&D-race, structural-credit, and AI literatures, including genuinely close investment/default work. The marginal contribution should be a result unavailable from those closest models, not the count of ingredients combined. Correct the Décamps attribution and the overly broad contest-theory claims. Explain exactly what the allocation-dependent continuation/collateral distinction adds relative to endogenous investment/default models such as Kumar–Yerramilli and Hackbarth–Mathews–Robinson.

**Model progression: Reasonable, but overextended.** Duopoly is defensible as the smallest model of preemption; it does not need to represent the entire industry. A small early leader and much larger later follower should remain a timing archetype, as the current discussion correctly acknowledges. Define default/recovery, entry, and policy restrictions before asserting equilibrium results, and specify what happens to the survivor's revenue and the follower's opportunity after a rival defaults. The current fixed-rival formulas do not by themselves supply those off-path subgames.

**Assumptions: Material, not peripheral.** Training generates no contemporaneous improvement in inference revenue, post-switch revenue needs no inference capacity, and training is a flow-capacity proxy without an accumulated capability stock. These choices create much of the mechanism. Prioritize one mixed-revenue or capability-stock sensitivity over further unrelated robustness. The existing dynamic-φ exercise is useful but does not validate those technological assumptions.

**Conclusion: Revise.** Keep the distinction between value loss and tail exposure, but correct C1 and the repeated equal-error language. Do not say “capacity is invariant to beliefs” without specifying the reduced single-firm policy class. Do not interpret the result as a general prescription to build more capital: the headline exercise changes timing and allocation, not K.

**Appendix split: Directionally sensible, execution inefficient.** Proofs and source detail belong in the appendix. The operating assumptions, result domains, and essential approximation comparison belong in the main text, preferably in one compact table rather than repeated qualifications across sections. Remove the scale-gap diagnostic and compress textbook H illustrations if space is needed.

### Length, abstract, and language

The existing 67-page main submission file is a serious editorial risk. Current [Management Science submission guidelines](https://pubsonline.informs.org/page/mnsc/submission-guidelines) impose no hard initial-submission page limit, but permit rejection for excessive length; invited revisions are limited to 32 pages at 1.5 spacing or 47 double-spaced, excluding the online appendix. The first submission should already be close to a viable revision length.

A practical target is approximately 30–32 pages including references: 3–4 pages of introduction/positioning, 10–12 of model/results, 5–6 of quantitative evidence, 2–3 of discussion/conclusion, and the remaining space for references. This is a planning target, not a claim that the current 67 pages violate an initial-submission hard cap.

The abstract has suitable keywords and length but needs more restrained claims: chosen curvature, reduced-model trigger formulas, local survival mechanism, illustrative calibration, and numerical belief-cost asymmetry. Put the explicit formula

\[
\phi^*=\frac{[\lambda/(r-\mu_H)]^{1/(1-\alpha)}}{1+[\lambda/(r-\mu_H)]^{1/(1-\alpha)}}
\]

in the main proposition. It communicates the central allocation result more efficiently than several paragraphs describing an implicit condition.

Notation is mostly coherent, but avoid using D for debt value and a discriminant, C for unrelated coefficients, and φ for an option-premium ratio in exploratory outputs. Use E for going-concern equity and a distinct symbol for entry NPV. The paper says the levered dilemma prices E + D − ℓI, but with the paper's E notation its implemented total-project NPV is **E + D − I**: `equity_value()` already subtracts (1−ℓ)I, and the evaluator subtracts the remainder. Make this translation explicit rather than relying on a code convention.

### Journal fit

**Management Science is not inherently over-aimed for the question, but the current execution is below submission standard.** I favor the Finance department if the repaired contribution centers on solvency and liquidation collateral. The [departmental statement](https://pubsonline.informs.org/page/mnsc/editorial-statement) specifically values innovative conceptual frameworks and important emerging financial questions, while expecting theoretical work to change how readers think. Its standards should not be treated as a low bar relative to specialist finance journals. Operations Management becomes more natural if dynamic allocation or operational flexibility becomes the main contribution.

The strongest submission pitch is: *allocating capacity toward future capability can support continuation value while eroding liquidation collateral, and the distinction disciplines how timeline beliefs affect distress.* That is narrower and more defensible than claiming a calibrated explanation of the AI investment race.

I would retain Management Science as the first target **after** the substantive revision. JFQA and Review of Finance are not automatic fallback solutions to mathematical or identification concerns. If the eventual paper remains primarily a stylized computational model with illustrative calibration, JEDC may be a more natural fit than proceeding mechanically through every finance rung; if the financing mechanism becomes sharper, Journal of Corporate Finance is a plausible alternative. These are editorial judgments, not predictions of acceptance.

### Submission materials and AI disclosure

The current [journal guidance](https://pubsonline.informs.org/page/mnsc/submission-guidelines) calls for anonymous manuscript files, an abstract of at most 250 words, three to five keywords, five proposed reviewers, three proposed AEs, ORCID, and the abstract in the cover letter. It requires at least 1.5 spacing, 11-point type, and one-inch margins. Source configuration and the sampled anonymous first page broadly conform; the full PDFs need fresh verification after revision.

Before submission:

- Replace `submission/cover-letter.md:24`'s “no unproven assumptions” and unqualified preemption existence/uniqueness claim with the appendix's accurate conditional-verification description.
- Remove the invitation to upload the manuscript to public AI tools. It is unnecessary and does not settle the journal's review-confidentiality requirements; the journal places responsibility on reviewers for their own conclusions and confidentiality.
- Include the abstract and a short, factual AI-use disclosure in the letter/portal. Preserve the more detailed disclosure separately. “All derivations verified through three independent channels” should not imply that every economic claim is formally proved or that the checks are statistically independent.
- Remove editorial notes/placeholders from the actual letter submitted. Lead with the economics, rather than the speed of the AI-assisted drafting experiment.
- Provide an anonymous, versioned numerical supplement with the Python environment, source, input provenance, and commands for each exhibit, alongside the Lean proof package. A public identified repository is not a substitute for a self-contained review package.

The AI disclosure is unusually transparent and should be retained. The issue is precision of verification claims and author responsibility, not concealment of tool use.

## Prioritized revision plan

1. **Repair the mathematical contract:** distinguish the restricted and unrestricted policy problems; fix the high-regime exercise envelope, levered leader boundary conditions, δ = 0 domain, and equity-NPV notation. Recompute affected results.
2. **Rewrite the central claims:** separate λ and φ effects, qualify prediction 1, correct Tullock interpretation and comparative statics, and use genuinely matched belief errors.
3. **Validate what the revised paper actually claims:** add payoff-dominance and leader-boundary tests, matched-error/derivative diagnostics at fixed X₀, and solver-success checks. Keep the existing algebra, scalar-reduction, and paper-number tests.
4. **Consolidate the manuscript:** one main contribution, one approximation/domain table, one focused calibration illustration; target about 30–32 pages rather than another round of caveats appended to 67 pages.
5. **Complete submission QA:** fresh blind render, all pages and references checked, updated figures and locked numerical package, corrected cover letter/disclosure, then final human mathematical review.

**Overall recommendation:** Do not submit as-is. The project has a plausible Management Science paper inside it, but the next revision should emphasize a smaller set of correctly defined economic results with reproducible numerical evidence. The passing tests and Lean build make that revision easier; they do not replace it.
