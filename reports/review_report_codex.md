# Review Report: AI Lab Investment

**Reviewer:** codex
**Date:** 2026-07-25

## Executive Summary

The project is unusually well engineered for an analytical paper. In an isolated copy of the repository, all 229 tests passed, the lint/format/type checks passed, the full analysis pipeline completed, all 11 figures regenerated, the Quarto manuscript rendered, the referee replication package built, and the Lean project kernel-checked 8,572 jobs with no `sorry` and only `propext`, `Classical.choice`, and `Quot.sound`. The paper is also topical, has a clear central allocation mechanism, and is plausibly in scope for *Management Science*. The code faithfully reproduces nearly all printed numbers and the algebraic formulas it was designed to implement.

The paper is nevertheless **not ready for submission**. The most serious problem is upstream of the verified algebra: the low-regime optimal-stopping candidate is not a solution of the stated regime-switching problem. At baseline, the claimed low-regime trigger is above the high-regime trigger, so the forcing term in the low-regime HJB is piecewise; the paper instead uses the below-trigger power form for the high-regime option everywhere. Assumption (A3) also does not imply that the homogeneous coefficient is zero: failure of a joint interior scale optimum is not the same as absence of a finite exercise trigger at each fixed scale. The appendix then explicitly substitutes a smooth-fit coefficient for the different coefficient dictated by the forced ODE. Numerically, those coefficients differ by about 22%. This invalidates the claim that Proposition 1 is an exact optimal-stopping solution and propagates into the low-regime triggers, the duopoly timing calculations, and the headline belief-mismatch results. Lean accurately verifies downstream identities conditional on the boundary conditions; it does not verify this missing economic argument.

Several further issues require substantive revision. “Dario's dilemma” is not evaluated as an expected payoff under the true switching process, despite the paper's definition; the code applies an `X^beta_H` timing factor and never integrates over switching before entry. The leveraged version uses an unleveraged policy as the purported optimum, and the text repeatedly says belief changes alter capacity even though Proposition 1 and the code make capacity invariant to lambda. The risk-pricing language conflates a certainty-equivalent WACC framework with risk-neutral valuation, the preemption existence result relies on an endpoint inequality established only numerically, and the dynamic-allocation discussion contradicts both stationarity and its own table. Separately, the submitted PDF fails current *Management Science* mechanics: it is identified, contains acknowledgments, uses 1.25 rather than at least 1.5 spacing, has eight rather than three-to-five keywords, and uses an Econometrica bibliography style. The cover letter also invites reviewers to upload the paper to generative-AI services, cutting against the journal's confidentiality-focused review policy. My recommendation is **major revision; do not submit the present version**.

## Part 1: Code Validation

### 1. Mathematical Correctness

#### Propositions vs. code — **ISSUE**

**Proposition 1.** Conditional on treating the low-regime problem as the reduced-form objective implemented in `base_model.py`, the formulas match. The code constructs
`A_eff = g(phi) K^alpha` at `src/ai_lab_investment/models/base_model.py:439-462`, maximizes
`A_eff^beta_H / b(K)^(beta_H-1)` at lines 482-506, and applies the printed trigger markup at lines 565-568. The numerical optimizer matches the printed closed-form scale and the allocation FOC; baseline values reproduce `X*=0.00472176`, `K*=0.00672664`, and `phi*=0.700856`.

The problem is that this reduced form is not the exact stopping solution claimed in `paper/_model.qmd:158-196`:

1. The low-regime HJB uses `F_H(X)=B_H X^beta_H` at `paper/_model.qmd:163-168`. That expression is valid only for `X<X_H*`. At baseline, however, `X_H*=0.00278296` and the asserted low-regime trigger is `X_L*=0.00472176`. Thus, throughout `(X_H*, X_L*)`, a switch to H leads to immediate exercise, not to the continuation option `B_H X^beta_H`. Even with a fixed exercise scale the H payoff there is linear in X; if scale is chosen on exercise it is an optimized payoff envelope. The correct HJB is therefore piecewise and requires matching at `X_H*`.

2. The argument at `paper/_model.qmd:182-188` and `paper/_appendix.qmd:123-133` conflates failure of a joint interior optimum over K with absence of an exercise boundary. For every fixed `K>0`, a pure-L project with a positive revenue coefficient has a finite trigger. Under (A3), the joint objective degenerates toward `K -> 0`; indeed, the paper correctly describes exactly that behavior for an analogous (A2) failure at `paper/_appendix.qmd:326-328`. It does not imply “wait indefinitely,” and it does not eliminate the homogeneous term.

3. If `A_1=0`, the ODE fixes `C=-lambda B_H/Q_L(beta_H)` (`paper/_model.qmd:173-176`), while value matching and smooth pasting fix the coefficient of `X^beta_H` separately. The appendix acknowledges the substitution at `paper/_appendix.qmd:129-133`: under its “unconditional-A_eff convention,” it prices with the smooth-fit coefficient rather than the forced-ODE coefficient. At baseline the forced coefficient is `21.1405` and the smooth-fit coefficient is `16.5246`, a ratio of `0.7817`. The same candidate therefore cannot satisfy the stated HJB and both boundary conditions.

Concrete fix: either (a) solve the genuine state-contingent, piecewise stopping problem, with the correct H-regime exercise payoff and interface conditions at `X_H*`, then rederive/recompute every downstream result; or (b) explicitly relabel the `A_eff`/`beta_H` construction as a reduced-form approximation, remove the HJB “exactness” and optimal-stopping claims, and substantially narrow the propositions.

**Proposition 2.** The default-boundary algebra is correctly transcribed within the reduced model. `default_boundary`, `faith_threshold`, and `faith_threshold_exact` in `duopoly.py:366-416,570-616` match the paper's closed forms. Tests independently finite-difference both sides of the exact sign threshold (`tests/test_duopoly.py:517-619`), and the coupled-boundary check supports the reported roughly 3% conservative bias. These are meaningful checks. However, `A_eff` is inherited from the invalid low-regime candidate, and calling the output Leland/no-arbitrage credit risk is not justified under the paper's discounting convention.

**Proposition 3.** Several implementation/notation discrepancies remain:

- The main text defines `E(X)` net of the initial equity contribution (`paper/_model.qmd:321-335`) and then defines the leader payoff as `L(X)=E_L(X)-(1-l)I` at line 393. The appendix silently changes `E_L` to going-concern equity at `paper/_appendix.qmd:219`, creating a double-subtraction ambiguity.
- `equity_value()` clamps even unlevered equity at zero (`duopoly.py:668-695`), and `_leader_value_at()` clamps the leader value again (`duopoly.py:1021-1037`). The paper's zero-leverage proof instead requires `L(0)=-I<0` and explicitly says the unlevered project has no abandonment option. The implemented gap and the asserted closed-form gap are therefore not literally the same function near the origin.
- The existence proof's upper endpoint is numerical, not analytical. `paper/_appendix.qmd:223` says `L(X_L^mono)>F(X_L^mono)` was found numerically for every tested parameterization, then invokes the IVT. The main proposition and taxonomy call existence analytical (`paper/_model.qmd:390-395`; `paper/_appendix.qmd:286`). Lean's `preemption_exists` is a generic IVT lemma that assumes the endpoint signs (`lean/AILabProofs/Duopoly.lean:66-80`); it does not prove the model-specific upper sign.

Concrete fix: choose one equity convention and use it throughout; make code and proof agree on abandonment/clamping; and label existence “conditional analytical, with the endpoint inequality verified computationally” unless a model-specific inequality is proved.

#### Proofs — **ISSUE**

- **Separability of K and phi:** The differentiation and cancellation in Proposition 1 are correct for the assumed objective. Lean and `tests/test_base_model.py:336-351` check the same identity. They do not establish that the assumed objective is the original stopping value.
- **Proposition 2 derivative:** The two-channel derivative, markup term, and exact net threshold are algebraically sound under the reduced model. `faith_threshold_exact()` and the finite-difference sign-flip test are especially strong verification.
- **Dario Taylor argument:** `paper/_appendix.qmd:256-274` is a heuristic, not a proof. “By construction” the implemented value need not be maximized at the true lambda because the evaluator is not the true switching payoff, and the leveraged evaluator uses an unleveraged policy. The sign of `W'''` is asserted from numerical scans; no reproducible scan covering the claimed “full parameter space” is present. The example `0.02` versus `0.20` is also not an equal-magnitude comparison around `0.10`, although `tests/test_valuation.py:273-282` separately checks equal deviations of 0.05 and 0.08.
- **Boundary cases:** Lambda zero leads to a boundary allocation `phi=0`, but the numerical problem excludes `phi<=0.01`; phi boundaries are therefore approximated rather than solved. The paper maintains `lambda>0`, so this is not a baseline contradiction, but nesting statements should distinguish a limit from an included case.

#### Result taxonomy — **ISSUE**

The table at `paper/_appendix.qmd:278-292` is mostly admirably explicit, but three labels overstate the evidence:

- Proposition 1 is not an exact closed-form/implicit-function stopping result for the stated HJB, for the reasons above.
- Proposition 3 existence is conditional analytical plus a computational endpoint check, not purely analytical.
- The Dario finding is numerical for the implemented proxy value, not for the expected payoff under the stated true regime-switching process.

The taxonomy correctly labels levered uniqueness and global allocation optimality computational and parts (iii)-(v) numerical.

#### Lean verification — **PASS WITH SCOPE CAVEAT**

`lake exe cache get && lake build` completed successfully (8,572 jobs). A repository-wide search found no `sorry` in Lean source. Spot checks of `trigger_from_boundary_conditions`/`K_foc`, the allocation FOC/closed form, `net_threshold_rearrange`, and `preemption_exists` agree with the equations they cite. `#print axioms` on representative theorems reported only `propext`, `Classical.choice`, and `Quot.sound`.

The scope paragraph at `paper/_appendix.qmd:60` is accurate and unusually careful: it disclaims the HJB derivation, the stopping verification theorem, the (A3) exactness argument, model-specific endpoint hypotheses, coupled ODEs, and numerical findings. The theorems are not vacuous as algebraic statements, but the preemption lemmas are generic and conditional. `lean/README.md:10-15` is somewhat broader (“existence/uniqueness of the preemption trigger”) than the precise table and appendix; `submission/cover-letter.md:17` overstates the package further by saying it checks existence and uniqueness and that “every theorem” has no unproven assumptions. The latter phrase confuses “no Lean placeholders” with “no economic hypotheses.” Align all external claims with the appendix's exact wording.

#### Two model modes — **ISSUE**

The two modes are internally consistent with their own formulas, but only the H-regime simple mode is a standard stopping model. Full mode at `base_model.py:439-594` is the reduced `A_eff` construction described above. The paper also does not use full mode for every quantitative result: `create_lambda_option_value()` calls `option_value_L()` and `particular_solution_coeff()` from simple mode (`src/ai_lab_investment/figures/paper.py:205-227`). The disclosure at `paper/_model.qmd:109` mentions the simple-mode H option and comparative-statics figures but not this low-regime lambda figure. That figure is directly tied to the disputed `A_1=0` construction.

#### Numerical methods — **ISSUE**

The closed-form phi inversion and Brent roots in `revealed_beliefs.py` are implemented sensibly, with sign checks and documented normalization limitations (`revealed_beliefs.py:64-148,154-212`). The scalar follower verification is a valuable independent check.

The optimization routines need stronger failure handling:

- The single-firm, follower, and leader Nelder-Mead loops select the lowest `result.fun` without testing `result.success`, finiteness, gradient/stationarity, or boundary distance (`base_model.py:542-560`; `duopoly.py:892-915,1111-1132`). Phi is clipped after optimization.
- The preemption routine records `single_crossing` but, on a missing bracket or Brent failure, silently substitutes an endpoint and returns it as `X_P`, emitting only a warning (`duopoly.py:1212-1244`). A paper result should fail loudly when equilibrium conditions are not met.
- `K=np.exp(log_K)` is evaluated before the `|log_K|<=15` guard (`base_model.py:489-494`), leaving a theoretical overflow path.

Concrete fix: require successful convergence from multiple starts, verify the analytical FOCs/residuals, expose diagnostics in returned results, and raise on missing/multiple preemption crossings in paper-generation paths.

#### Parameter consistency — **ISSUE**

Defaults in `parameters.py:41-64` match the baseline table and reproduced baseline results. Units are consistently annual. Validation checks `r>mu_s`, sigma, alpha, gamma, cost, lambda, and build lag, but it does not enforce the full stated A1 ordering `mu_H>mu_L>=0`, `delta>=0`, or financial parameter ranges. The Internet Appendix also labels leverage endogenous (`paper/_appendix.qmd:36,40`) while the model fixes it exogenously (`paper/_model.qmd:369-373`).

There is a direct calibration contradiction: `paper/_calibration.qmd:36-37` says the archetype analysis uses full numerical optimization that “does not rely on (A2)” and spans `alpha in [0.20,0.60]`. The solver explicitly refuses to run when A2 fails (`base_model.py:521-536`), and `paper/_appendix.qmd:328` says the high-WACC archetypes enter only the capacity-free phi inversion while triggers/capacities use baseline WACC. The appendix is consistent with the code; the main text is not.

#### Regime switching — **ISSUE**

The simulated demand process has the correct GBM drifts, common volatility, one-way L-to-H transition, and absorbing H state. Its time-step transition uses the first-order Bernoulli approximation `lambda*dt` rather than exact `1-exp(-lambda*dt)`; at the default `dt=0.001` this is negligible but should be exact for robustness to larger steps. The installed-value calculation correctly capitalizes a fixed installed policy. The stopping option fails to handle the piecewise H continuation value, as explained above.

#### Default probability — **PASS FORMULA / ISSUE INTERPRETATION**

The formula in `valuation.py:163-230` matches the standard finite-horizon lower-barrier hitting probability for GBM, and the Monte Carlo test validates it. It deliberately ignores the regime switch; the code and paper call it an upper bound because an H switch is assumed to remove default risk. Thus it is not the model's full default probability. Moreover, with WACC discounting and an unspecified risk-premium adjustment, it cannot be called a “risk-neutral default probability consistent with the spread” (`paper/_valuation.qmd:71-73`; `paper/_discussion.qmd:85-87`). Call it a model-implied risk-adjusted first-passage probability, or specify a genuine pricing measure and risk-free rate.

### 2. Code Quality and Testing

#### Test coverage — **ISSUE**

`pytest --cov` completed with **229 passed in 49.23 seconds** and **52% total statement coverage**. Core-model coverage is much better than the aggregate: `base_model.py` 89%, `duopoly.py` 84%, `valuation.py` 88%, `symbolic_duopoly.py` 83%, `revealed_beliefs.py` 87%, and `parameters.py` 76%. The total is pulled down by 0% coverage of all figure modules, the pipeline, and utility modules. The most consequential missing test is an independent HJB/stopping verification around `X_H*`; existing L-mode tests assert the disputed specification rather than test it. Add tests for optimizer success diagnostics, bracket failure, model-specific preemption endpoint signs, complete figure generation, and an end-to-end pipeline smoke test.

#### Test meaningfulness — **PASS WITH LIMITATION**

Most tests are economically meaningful rather than trivial: H-regime value matching and smooth pasting (`tests/test_base_model.py:63-78`), option domination, K's closed-form independence from phi, role invariance, default boundary ordering, exact faith-threshold sign flips (`tests/test_duopoly.py:517-619`), coupled-boundary bias, scalar-vs-Nelder-Mead follower solutions, first-passage Monte Carlo validation, and paper-number pins. The limitation is circularity at the model's most vulnerable point: `test_option_value_L_from_C_only` (`tests/test_base_model.py:108-115`) and the symbolic L tests confirm that code matches the assumed formula, not that the formula solves the actual stopping problem.

#### Paper-number tests — **PASS WITH TOLERANCE CAVEAT**

Printed baseline values, fixed-pie results, Dario percentages, default probabilities, and dynamic-phi headline values match the tests. Tolerances are adequate for coarse regression but loose for a deterministic paper build: Dario single-firm values allow one percentage point, duopoly values two percentage points (`tests/test_valuation.py:284-289,438-449`), and the dynamic table pins only the free-reallocation phi/gain plus monotonic gains, not all printed cells (`tests/test_valuation.py:453-467`). Tighten deterministic pins after the model is corrected. The docstring at `tests/test_valuation.py:275` still calls Dario “Numerical Finding 2,” while the paper correctly calls it Finding 1.

#### Edge cases — **ISSUE**

Leverage zero, lambda near zero, phi limits for installed value, invalid alpha/gamma/r, default boundaries, and high-alpha two-term branches receive some coverage. Missing or incomplete cases include exact lambda zero in full optimization, very large lambda, financial parameter bounds, negative delta/drifts, optimizer solutions on phi bounds, and explicit failure-path tests for preemption brackets. Zero volatility is correctly rejected because the closed forms divide by sigma; the test suite should assert that validation explicitly.

#### Numerical stability — **ISSUE**

Log objectives and multiple starts are good choices, and most denominators are guarded. The optimizer-success and fallback concerns above are the main risks. The full-model phi bounds `[0.01,0.99]` turn true boundary optima into arbitrary interior approximations. The fixed 500-point preemption grid can miss a narrow crossing; analytical bracketing or adaptive refinement would be safer.

#### Code organization — **PASS**

Responsibilities are generally clean: parameters feed model classes, valuation is separate, paper calculations live in `figures/paper.py`, and `paper/generate_figures.py` is a thin styling/saving wrapper. The explicit simple/full split is documented. Some public method names and docstrings still overstate semantics—for example, `valuation.py:276-277` says X, K, and phi all depend on lambda although K does not—and should be corrected with the model.

#### Reproducibility — **PASS WITH CLAIM GAPS**

In the isolated copy, `just check`, `just run-pipeline`, `uv run python paper/generate_figures.py`, `just render-paper`, `just build-replication-package`, and the Lean build all completed. Figure seeds are fixed where stochastic paths are used. The generated PDF has 81 pages. Initial cache failures were sandbox/environmental; the same commands succeeded with writable caches/outside the sandbox.

Not every robustness claim is reproducible from repository code. I found no implementation or test of the stated full +/-25% “re-compute all results” sweep (`paper/_appendix.qmd:398-402`) and no three-regime model behind “Using a three-regime model ... does not qualitatively change the results” (`paper/_appendix.qmd:463-465`). The fixed-pie and two-period exercises are implemented, but the latter is conceptually flawed (see below). Either add the missing artifacts and tests or recast these as conjectures/qualitative discussion.

## Part 2: Paper Review

### 3. Paper Content Review

#### 3a. Structure and Argument

**Motivation — PASS WITH RESTRAINT NEEDED.** The introduction clearly explains timing, scale, allocation, regime uncertainty, competition, and financial distress. “Training-survival” is memorable and potentially publishable. The paper would be stronger if it led with the general managerial problem—irreversible dual-use capacity under a technology-regime transition—and used frontier AI as the application. “AGI” claims currently dominate and may date the contribution quickly.

**Literature positioning — PASS WITH ISSUES.** The canonical real-options, preemption, R&D-race, and structural-credit literatures are well covered. The closest-neighbor discussion is unusually explicit. The paper should be more cautious about “no close parallel” (`paper/_model.qmd:36`) and “neither result can be obtained” (`paper/_literature.qmd:26`) until the corrected mechanism is established. It should also engage more directly with current economics/operations work on compute capacity, data-center constraints, dynamic experimentation/exploitation, and investment with technology jumps. The current Finance/OM bridge is promising but spreads the contribution across too many literatures.

One verified bibliography error remains: `paper/references.bib:500-505` lists Bledi Taska on “Generative AI and Firm Values,” while the current official [NBER Working Paper 31222 record](https://www.nber.org/papers/w31222) lists Andrea Eisfeldt, Gregor Schubert, and Miao Ben Zhang. Given the project's AI provenance and the prior correction log, perform a fresh manual audit against publishers/working-paper repositories before submission.

**Model building — ISSUE.** The single-firm-to-duopoly progression is natural, and a duopoly is a defensible minimal strategic setting. However, the duopoly is not the stopping game stated at `paper/_model.qmd:355-360`: leader scale/allocation are fixed at the monopoly-phase solution by convention, follower entry is state-unconditional, follower default optionality is omitted from its trigger, and several option terms are discounted with beta_H. These approximations are disclosed only later (`paper/_model.qmd:144-148,375-380`; `paper/_appendix.qmd:304`). They are load-bearing and should be presented before Proposition 3, with the result described as a tractable benchmark rather than the subgame-perfect equilibrium of the full strategy game.

**Key assumptions — CRITICAL ISSUE.** A1-A4 are clearly displayed, but A3's economic and mathematical explanation is not convincing and is, in my assessment, wrong. Repairing or honestly approximating this step is the first-order revision task.

There is also a financing inconsistency. Leverage is treated as debt proceeds equal to `l I`, while debt is then assigned a market value different from `l I`; coupon `c_d l I` is below the model discount rate and debt bears default risk. “Par-issued debt with a below-market coupon” is a financing subsidy, not a self-financing Leland capital structure. The paper acknowledges exogenous leverage but still interprets its scale effects as corporate-finance predictions. Either price debt fairly at issuance, explicitly model a subsidy/guarantee, or present leverage only as a stress-test parameter.

**Conclusion — ISSUE.** The summary is clear, but `paper/_conclusion.qmd:18-19` says aggressive firms have larger capacity and coupon obligations and that observed commitments are too costly to be signaling/agency alone. K is lambda-invariant in the single-firm model, and no identification exercise separates beliefs from signaling or agency. The final claim should be removed or reduced to a model-conditional illustration.

**Internet Appendix split — ISSUE.** Proofs and numerical methods properly belong in the appendix. The unconditional-A_eff pricing convention, omitted follower default option, computational endpoint condition, and A2 failures at archetype WACCs are not peripheral; they qualify the main propositions and should be in the main text. The appendix should be uploaded as a separate anonymous electronic companion rather than embedded after the references in one 81-page PDF.

#### 3b. Writing Quality

**Clarity — ISSUE.** Prose is generally polished and definitions are often excellent, but the manuscript is dense and repetitive. The three mechanisms are restated in the introduction, results, discussion, and conclusion. Long URL footnotes interrupt arguments and produce visually dense pages. Move source details to a data appendix, shorten the repeated intuition, and distinguish consistently among theorem, approximation, numerical regularity, and conjecture.

Confusing or contradictory passages include:

- `paper/_discussion.qmd:46-61` says non-arrival lowers training's continuation value “through discounting alone” despite an exponential clock's memorylessness, predicts phi should fall, and says static phi overstates initial phi. In a stationary infinite-horizon problem with no learning, the conditional problem after non-arrival is unchanged. The table at `paper/_appendix.qmd:429-444` shows `phi_L2=0.70` under free adjustment and `phi_1` equal to or above 0.70, directly contradicting the prose.
- The two-period code uses the perpetual `A_eff` inside a finite first-period term and adds another perpetual continuation term (`valuation.py:797-824`), so it is not a clean Bellman decomposition and can double count continuation value.
- `paper/_discussion.qmd:8-10` asserts that the leader enters earlier than the social optimum and capacity may exceed the cartel level, but neither benchmark is solved.
- `paper/_discussion.qmd:22` predicts equity beta from phi without a systematic-risk process or pricing kernel.

**Notation — ISSUE.** The equity/leader-payoff ambiguity noted above is material. The paper also alternates between beta_H as an option exponent and a generic beta in Dario's timing discussion, labels leverage endogenous in the parameter table but exogenous in the model, and calls an annual revenue multiple “revenue growth.” Define all claim values gross/net of investment once and use separate notation for going-concern equity, net entry NPV, debt face value, and market value.

**Length and focus — ISSUE.** The rendered main body is about 21,156 extracted words over pages 1-51, plus five pages of references and a 24-page appendix. The journal has no first-round page cap, but it warns that excessive length can prompt rejection and later requires 32 pages at 1.5 spacing (or 47 double-spaced), excluding the online appendix. The current 1.25-spaced main text would expand materially. A focused revision should target one core contribution, move calibration mechanics and secondary asset-pricing/policy claims out of the main paper, and reduce repeated narrative.

**Abstract, keywords, JEL codes — PASS/ISSUE.** The 178-word abstract is below the journal's 250-word maximum and states the question, method, and results. It will need revision after the model is corrected. JEL codes G31, G32, G33, L13, and O33 are present in `paper/keywords.tex:9` and are reasonable. Eight keywords are supplied (`paper/index.qmd:26-34`; `paper/keywords.tex:7`), while current *Management Science* instructions request three to five.

#### 3c. Journal Fit

**Contribution significance — CONDITIONAL PASS.** If the corrected model genuinely produces a training-allocation/default interaction and a robust belief-asymmetry result, the topic and mechanism could justify a *Management Science* attempt. In its current form, the main analytical contribution rests on an invalid stopping reduction and the paper is over-aimed for every journal on the ladder, not just the first rung.

**Methodological rigor — ISSUE.** The downstream algebra and software rigor are strong. The economic verification, risk-pricing foundation, equilibrium definitions, and robustness evidence are not yet at a leading-journal standard. Formal verification is a useful supplement, but it cannot substitute for checking that the formalized premises are the right economics.

**Formatting and conventions — CRITICAL ISSUE.** Current [Management Science submission guidelines](https://pubsonline.informs.org/page/mnsc/submission-guidelines) require at least 1.5 spacing, 11-point type, one-inch margins, a double-anonymous manuscript without names, institutions, or acknowledgments, an abstract of at most 250 words, and three-to-five keywords. The PDF uses 11 point and adequate margins, but:

- `paper/_quarto.yaml:41` sets `linestretch: 1.25`.
- `paper/index.qmd:11-18,35` prints the author, institution, e-mail, acknowledgments, and AI disclosure.
- The appendix repeats the author/institution at `paper/_appendix.qmd:6-10`.
- The bibliography uses `econometrica` (`paper/_quarto.yaml:26-27`) rather than INFORMS style.
- The journal says not to upload a title page with the anonymous manuscript; the rendered first page is an identified title page.

The current journal guidance also requires five reviewer suggestions, three AE suggestions, an ORCID for the submitting author, and an abstract in the cover letter. Those portal items could not be verified from the repository.

**AI-use disclosure — ISSUE.** The manuscript thanks note, detailed disclosure, public workflow description, and responsibility statement are transparent. Current Management Science author policy says authors retain full responsibility and does not appear to require the long tool-by-tool disclosure. A brief factual note in the cover letter/portal may be less distracting during anonymous review; follow the editor's instructions on whether any statement belongs in the anonymous manuscript. More importantly, `submission/cover-letter.md:19` grants referees permission to upload the paper to ChatGPT or Claude. The journal's own AI policy warns review-team members against uploading submitted manuscripts where confidentiality or copyright may be compromised; an author-side invitation is unnecessary and risks putting reviewers in conflict with journal procedure even when a preprint is public. Delete it. The cover letter's Lean claims at line 17 also need narrowing.

**Which journal fits best — CONDITIONAL RECOMMENDATION.** Keep *Management Science* as one ambitious first attempt only after the major technical and submission revisions. The [journal-wide statement](https://pubsonline.informs.org/page/mnsc/editorial-statement) values managerial relevance and stochastic modeling grounded in practice; the [Finance statement](https://pubsonline.informs.org/doi/10.1287/mnsc.2018.3075) welcomes important emerging topics and theory that changes how readers think, while the [Operations Management statement](https://pubsonline.informs.org/doi/10.1287/mnsc.2020.3842) explicitly welcomes AI, capacity questions, stochastic processes, and game theory. Finance is defensible if default and valuation remain central; Operations Management may be the more natural department if the paper is reframed around dual-use compute capacity and the credit claims are narrowed.

I would not assume JFQA or *Review of Finance* is an easier second step; both will press even harder on the pricing-measure and capital-structure issues. If the paper remains primarily a regime-switching investment model rather than a corporate-finance model, *Journal of Economic Dynamics and Control* is a more natural early fallback and should move above the pure-finance outlets in the current ladder.

### 4. Figures

#### Paper figures — **PASS WITH SPECIFIC ISSUES**

All 11 stems have both PNG and PDF files. Exactly 10 are cited in the paper; `fig_sample_paths` is cited only in `slides/long-form/_introduction.qmd:52`. No other generated figure is unused. All PNGs are high resolution and all PDFs rendered sharply. Regeneration completed, with one nonfatal `tight_layout` warning.

| Figure | Assessment |
|---|---|
| `fig_option_value` | Visually clean and standard for the simple H problem. It fixes exercise scale above the trigger; clarify that this is an illustration rather than the full state-contingent scale policy. |
| `fig_comparative_statics` | Values match the simple H model. Four dual-axis panels are readable in the PDF but dense; neighboring axis ticks are tight in the standalone PNG. Consider shared legends/more gutter space. |
| `fig_lambda_option_value` | Mechanically matches simple-mode `C X^beta_H`, but inherits the invalid A3/global-HJB claim and is not full mode. Do not retain as evidence of the full model without re-solving. |
| `fig_default_boundaries` | Clean and accurately traces the implemented duopoly outputs; inherits the reduced A_eff and financing assumptions. |
| `fig_credit_risk` | Clean and matches code. Relabel spread/probability as model-implied risk-adjusted objects, not market/risk-neutral quantities. |
| `fig_competition_effect` | Clean and consistent with `solve_preemption_equilibrium`; inherits the equilibrium fallback and endpoint-condition issues. |
| `fig_firm_comparison` | Visually good broken-axis design. The x-axis label “Revenue growth (2024-2025x)” (`figures/paper.py:527`) is malformed and mixes a multiple with a growth rate. Use “Revenue multiple (2025/2024)” or plot percentage growth. Comparability of CapEx concepts is weak. |
| `fig_lambda_timeline` | Correct (`1/lambda` and `1-exp(-5 lambda)`), clean, and self-contained. |
| `fig_growth_decomposition` | Correct for the code's definition, but the “capacity gap” is not a separable growth option: it compares gross installed value with net greenfield NPV. The paper partly concedes this, yet still draws firm-value/beta conclusions. Rename it and narrow interpretation. |
| `fig_investment_dilemma` | Clean and matches the implemented Dario proxy. It should be regenerated only after the true-process payoff is corrected. The “loss >10%” shading should clarify which curve defines the region. |
| `fig_sample_paths` | Clean and correctly used only in slides. The pre/post-switch color change is subtle but adequate. |

#### Code-figure consistency — **PASS MECHANICALLY**

I traced more than three paths: option value from `SingleFirmModel`, default/credit risk from `DuopolyModel` and `ValuationAnalysis`, competition from `solve_preemption_equilibrium`, growth decomposition from `capacity_gap_decomposition`, and Dario from the single/leveraged mismatch evaluators. `paper/generate_figures.py` contains no duplicated economics. The pipeline from implementation to plotted values is correct; the reservations concern the economic object being computed.

### 5. Calibration and Results

#### Parameter values — **ISSUE**

The paper is commendably candid that the exercise is stylized and unit-free. Several “inferred” labels nevertheless overstate the evidence:

- Alpha=0.40 is “anchored” on compute-to-loss scaling exponents (`paper/_calibration.qmd:33-37`), but a loss scaling exponent is not a revenue elasticity or contest exponent. This is a chosen value near the A2 boundary, and the trigger/capacity elasticities to alpha are enormous.
- Sigma=0.25 is said to come from quarterly cloud-revenue volatility, but no series, calculation, window, or uncertainty interval is supplied.
- Delta=0.03 is described as relatively insensitive even though the reported elasticities of roughly 2 imply a 25% perturbation changes K or X by roughly 50% locally.
- Firm inputs mix annual revenue, ARR, cloud commitments, and consolidated CapEx. The paper admits the private-lab and Google ratios are not directly comparable (`paper/_calibration.qmd:98-105`). They should not be used as a common quantitative cross-section without a harmonized measurement definition.
- The source table at `paper/_appendix.qmd:359-372` contains incomplete cells (“xAI,” “OpenAI,” “Google”) without traceable citations. The official [OpenAI disclosure](https://openai.com/index/a-business-that-scales-with-the-value-of-intelligence/) reports ARR, not the annual revenue figures used in the table; [Epoch AI](https://epoch.ai/data-insights/openai-compute-spend) itself warns that its split rests on reported investor documents and estimates. Alphabet's 2025 CapEx is well supported by its [official earnings release](https://abc.xyz/investor/events/event-details/2026/2025-Q4-Earnings-Call-2026-Dr_C033hS6/default.aspx), but assigning consolidated CapEx against Cloud revenue is a modeling choice, not a measured AI-lab ratio.

The Q4 2025-Q1 2026 timing and the xAI pre-SpaceX-acquisition framing are stated consistently at `paper/_calibration.qmd:63-72` and `paper/_appendix.qmd:374-375`.

#### Sensitivity and robustness — **ISSUE**

Local elasticities and admissible windows are useful, but their magnitudes show fragility rather than broad robustness: r and alpha elasticities around 20-29 mean tiny calibration changes produce large policy shifts. Truncating +/-25% perturbations to the admissible A2 region avoids precisely the boundary behavior readers need to understand. Provide complete tables/plots and code for the sweep, including failed/degenerate cases.

The fixed-pie exercise is implemented and tested. The Cournot discussion is explicitly qualitative and acceptable as such if shortened. The three-regime sentence is not acceptable as written without an implementation. The dynamic-phi exercise does not validate the claimed bias because its Bellman accounting and stationarity logic are wrong. The duopoly Dario exercise is correctly described as one-sided rather than a full asymmetric-beliefs equilibrium, but that caveat should move to the main text before the 38%/17% result is cited.

#### Comparative statics — **PASS WITH INTERPRETATION CAVEAT**

The reported directions match the implemented reduced model and tests. Some are counterintuitive only because of the endogenous scale/cost structure (for example, higher delta raises optimal K), and the paper explains that mechanism. Do not generalize these directions outside the narrow A2-admissible region. Statements connecting more optimistic beliefs to “larger capacity” are false in the single-firm model; K is invariant to lambda to numerical precision.

#### Dario's dilemma results — **CRITICAL ISSUE**

The percentages reproduce, but they do not estimate the object defined at `paper/_valuation.qmd:101-107`.

- `valuation.py:322-334` discounts the mismatched trigger with `(X0/X*)^beta_H`. Under the true L-to-H process, payoff depends on whether H arrives before the L trigger and on the policy followed after that event. The implementation neither integrates over the switch nor uses the appropriate killed/coupled first-passage solution.
- `dario_dilemma_leveraged()` obtains both “optimal” policies from the unleveraged `SingleFirmModel` (`valuation.py:367-395`) and only then evaluates levered claims. It does not optimize the levered objective, even though leverage changes the effective cost and preferred scale in the duopoly model.
- K is identical across lambda: for lambda 0.02, 0.10, 0.20, and 0.50 the computed K is 0.006726639 to nine significant figures. Yet `paper/_valuation.qmd:128-130`, `paper/_appendix.qmd:274`, and `paper/_conclusion.qmd:18` attribute default differences to smaller/larger capacity and coupons. Those explanations are false for the code producing the numbers; the variation comes from entry X and phi.
- Appendix line 258 includes an optimal `l*(lambda)` even though leverage is exogenous everywhere.

Concrete fix: define admissible policies after a switch, evaluate each policy under the true joint stopping/switching law (analytically or by validated dynamic programming/Monte Carlo), optimize the leveraged objective when discussing leverage, then retest the asymmetry. If the result survives, the headline will be much stronger.

#### Growth decomposition — **ISSUE**

The code correctly computes the paper's stated arithmetic. Economically, however, `max{NPV(K*)-V_AIP,0}` is neither the value of an incremental expansion nor a real option, and adding it to gross assets-in-place makes total “firm value” equal to the larger of two incommensurate benchmarks. The paper now concedes much of this at `paper/_valuation.qmd:24-42`, but then asserts that typical labs have `K/K*=0.1-0.3` without an empirical mapping and infers high equity beta (`paper/_valuation.qmd:40-44`). Retitle this as a normalized scale-gap diagnostic and remove the asset-pricing conclusion unless a proper enterprise-value decomposition is built.

#### Normalization caveat — **PASS WITH ONE OVERREACH**

`paper/_calibration.qmd:119-124` clearly states that X and K levels are uninterpretable and that the c-to-CapEx mapping is illustrative. Most main results use ratios or percentages. The unsupported claim that observed labs occupy `K/K*=0.1-0.3` effectively reintroduces a level mapping and should be removed or empirically derived. The 44x follower/leader trigger ratio is a state ratio, not a literal duration; avoid prose that invites a time interpretation.

## Summary of Issues

### Critical Issues

1. **Re-solve or honestly downgrade the low-regime stopping problem.** The HJB forcing is piecewise, A3 does not eliminate the homogeneous term, and the forced and smooth-fit coefficients differ. Recompute every low-regime, duopoly, default, and Dario result affected.
2. **Rebuild Dario's dilemma around the stated true-process payoff.** Include switching before entry, policy after switching, and a genuinely optimized leveraged benchmark. Remove false capacity/coupon explanations.
3. **Meet Management Science's anonymous-submission requirements.** Produce separate anonymous main-paper and appendix files; remove author/institution/thanks; use at least 1.5 spacing; reduce keywords to 3-5; adopt INFORMS reference style.
4. **Correct the cover letter.** Remove permission for reviewer AI uploads, narrow the Lean claim, include the exact abstract, and retain transparent disclosure of the SSRN/repository posting.

### Major Issues

1. Recast the WACC/certainty-equivalent framework without calling it risk-neutral, or build a coherent risk-neutral pricing setup with a risk-free discount rate and risk premia.
2. Resolve debt issuance/market-value consistency; do not interpret subsidized, exogenously levered debt as an endogenous capital-structure result.
3. Correct Proposition 3's equity notation/clamping mismatch and label existence conditional on a computational endpoint check.
4. Repair the dynamic-phi argument and code; memorylessness implies no no-switch drift in the stationary optimum without learning, and the current table contradicts the prose.
5. Add code/evidence for the +/-25% and three-regime claims or remove them. Make paper-generation equilibrium failures raise errors.
6. Harmonize and document calibration moments; relabel alpha, sigma, delta, WACC, and private-firm inputs as chosen/proxy values where appropriate.
7. Shorten the main paper substantially and move load-bearing approximation disclosures from the appendix into the model section.
8. Remove unsupported welfare, beta, signaling/agency, and “larger capacity under optimism” claims.

### Minor Issues

1. Fix the firm-comparison x-axis wording and distinguish revenue multiples from percentage growth.
2. Correct the Eisfeldt-Schubert-Zhang bibliography entry and re-audit current working-paper/industry references.
3. Tighten deterministic paper-number tests and pin every dynamic/fixed-pie table cell.
4. Validate all A1/financial parameter ranges, use the exact Poisson step probability, and test solver failure paths.
5. Remove stale “Numerical Finding 2” test wording and update docstrings that say K depends on lambda.
6. Reduce long raw-URL footnotes and repeated descriptions of the same three mechanisms.
7. Prevent `reference_corrections.md` from being rendered as an extra project output during the paper build.

## Overall Recommendation

**Major revision needed. Do not submit as-is.**

The best first target remains **Management Science**, but only conditionally: the capacity-allocation problem, AI application, stochastic timing, and finance/operations bridge fit the journal well, and the repository/Lean package is a genuine strength. The current manuscript would face both an immediate formatting/anonymity return and a high risk of technical rejection once a referee checks the low-regime HJB. After repair, submit to the Finance department if the risk/default contribution remains central, or consider Operations Management if the revision foregrounds dual-use capacity and treats credit risk as an application.

If the corrected paper remains primarily a stylized regime-switching investment model, move **JEDC** ahead of JFQA and *Review of Finance* in the fallback ladder. The pure-finance outlets are unlikely to be more forgiving of the current pricing-measure and debt-issuance issues.
