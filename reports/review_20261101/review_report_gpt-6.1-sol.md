# Independent referee report: Investing in Artificial General Intelligence

Reviewer: **gpt-6.1-sol**. Date: 2026-11-01. Target: **Management Science**.

## Executive summary

**Recommendation: major revision before submission.** The numerical implementation is unusually well tested, and the central reported numbers reproduce. All 393 tests passed in a scratch copy; all 36 notebook code cells executed; the blind manuscript compiled. This does not establish the paper's unrestricted dynamic optimality. The largest concern is economic rather than an algebraic typo: when the stated regime-switching stopping problem is solved without the post-switch scale restriction, the baseline firm never invests before the switch. Thus a small percentage loss of value from the reduced policy conceals a qualitative change in the decision the paper principally seeks to explain. The manuscript acknowledges this honestly, but acknowledgment does not by itself supply an economic foundation for the replacement valuation rule.

The training/default/liquidation trade-off is interesting and potentially suitable for Management Science. The most promising contribution is the opposition between going-concern capability value and recoverable inference assets. Its institutional foundation needs strengthening: training is contemporaneous compute rather than an accumulated capability stock, the switch is exogenous, and cheap reallocation nearly eliminates initial training. The paper should establish the central mechanism in a coherent dynamic benchmark before emphasizing the numerical preemption and belief-error magnitudes.

There are also concrete repairable defects: the notebook and symbolic verification module still assert mathematical arguments that the manuscript explicitly rejects; the calibration sources table is badly broken in the rendered PDF; and several prose statements have incorrect numbers or domains. I found no Critical issue that invalidates the conditional closed-form algebra itself.

### Derived review brief and scope

The actual include chain is `paper/index.qmd` → introduction (including literature) → model → calibration → valuation → discussion → conclusion → references → Internet Appendix cover → Internet Appendix A–H. The spine is: separability of capacity and allocation under the pure-power convention; role-invariant allocation and accelerated entry under the contest/leader-scale conventions; optimism-supported solvency against nonrecoverable capability; and the expected-value versus tail-risk asymmetry of belief errors. I therefore audited the stopping convention, allocation algebra, credit/default implementation, strategic entry, numerical calibration and robustness, and exhibit production. This is a theory/simulation review, not an empirical identification exercise.

No existing report was read. `reports/` was listed only; no tracked file was modified. All environments, notebook execution logs, builds, and figure rasterizations were placed under `/tmp/agi-review-sol.8pIarH`. This report is the only review artifact I created in the repository. No commit was made.

## Part 1 — Validation

### Execution record and limits

The reviewed HEAD is `4def5f6`; it has zero ahead/behind distance from the locally cached `origin/main`. `git fetch origin` failed because writing the worktree's `FETCH_HEAD` outside the permitted root was denied. Remote freshness is therefore **not verified**. This is an OS sandbox boundary, not evidence of a repository fault. If a fresh fetch is required, the documented options are a one-off restart with `nono run --allow` for the parent Git metadata directory, or a persistent profile draft promoted outside this session; neither was necessary for this local review.

The initially attempted locked `uv run pytest` could not install missing dependencies because DNS/network access was unavailable. I then used the existing project Python environment through `uv run --no-project --python /Users/vincentgregoire/Documents/GitHub/ai-lab-investment/.venv/bin/python`, with `PYTHONPATH` pointing to the scratch source copy and bytecode redirected to `/tmp`. The reported numerical versions were NumPy 2.4.2, SciPy 1.17.0, and SymPy 1.14.0. This is successful execution of the reviewed source, **not** a successful clean installation from the lockfile.

Executed successfully:

- Entire test suite: **393 passed in 115.87 seconds**, without coverage. This includes the 11 figure generators, each saved to a temporary PDF by `tests/test_figures.py:48` (figure rendering tests).
- Sequential execution of all 36 code cells in `notebooks/model_derivation.ipynb`; no cell raised an exception. Mathematical problems in printed assertions are recorded in Issue 2 below.
- Direct baseline single-firm, duopoly, credit-risk, and belief-mismatch calculations.
- `python -m ai_lab_investment.models.piecewise_option`, including the unrestricted baseline comparison.
- The full 18-draw one-at-a-time robustness sweep, plus direct precommitted and unrestricted dilemma comparisons at investment beliefs 0.02, 0.20, and 0.50.
- `quarto render --profile blind --to pdf` in the scratch paper directory. The full PDF has 111 pages: 45 manuscript pages before the Internet Appendix cover, followed by 66 pages including that cover. The final log contained no undefined-reference warning, but did contain material overfull boxes; see Issue 4. I did not run the subsequent PDF-splitting script.

`lake build` was attempted in the scratch Lean directory. It failed while cloning Mathlib because `github.com` could not resolve. **I did not obtain a successful kernel build or independently execute the axiom audit.** I inspected the seven Lean source files and their theorem statements/proofs, plus the top-level imports. The source search found no `sorry` or custom `axiom` declaration; this is a source inspection, not a substitute for kernel checking.

### Stopping problem and capacity/allocation closed forms — has issues

The reduced algebra checks out. Eliminating the option coefficient from value matching and smooth pasting gives `X*=βb/[(β−1)A]`. Substitution leaves the objective proportional to `g(φ)^β K^(αβ)/b(K)^(β−1)`. Its capacity log derivative yields the stated expression for `K^(γ−1)`, and (A2) gives the two endpoint limits needed for global optimality. Strict concavity of the single-firm allocation objective yields the unique allocation `φ*=ρ/(1+ρ)`. The common discount denominator cancels from the allocation FOC, explaining independence from μL. These are conditional results for the chosen objective, rather than a verification of the original switching HJB.

**Issue 1 — Major — The tractable stopping convention changes the principal decision qualitatively; its economic foundation is still missing.**

Locations: `paper/_model.qmd:177` and `paper/_model.qmd:185`, Section “Solution conventions and approximations”; `paper/_appendix.qmd:143`, Internet Appendix A, Proposition 1 Step 5b; `paper/_appendix.qmd:363`, Internet Appendix B, “Piecewise L-regime stopping problem, unrestricted post-switch scale”; `src/ai_lab_investment/models/base_model.py:701`, option-value evaluator.

The paper both displays the original switching HJB and calls the propositions “exact statements about the model these conventions define.” But the smooth-fit coefficient of its pure-power candidate is approximately 16.5 rather than the forcing-implied coefficient Γ≈21.1, as the appendix itself explains. Below the H trigger, inserting that candidate into the displayed HJB leaves a nonzero residual proportional to `Q_L(βH)(C−Γ)X^βH`. This is more than a choice among solutions of that HJB. A reduced payoff criterion can be studied, but its replacement of the dynamic problem needs to be economically defined and motivated.

The independently executed unrestricted comparison is decisive for interpretation: the reduced policy is worth 0.001621454, pure switching 0.001741368, and the numerical unrestricted optimum 0.001741381 at the reference demand. The optimum has **no finite pre-switch trigger**. In the unrestricted belief exercise, losses at optimistic beliefs 0.20 and 0.50 are both zero, versus 5.63% and 22.58% in the reduced model. The reported 6.89% policy value loss therefore cannot be used as evidence that the reduced model preserves investment timing, belief-invariant scale, or the optimistic side of the dilemma. The appendix already discloses these results; the issue is their implication for the contribution, not hidden computation.

Suggested fix: promote a dynamically consistent stopping formulation to the main benchmark, or introduce an economically justified commitment/capability primitive that makes pre-switch training necessary and rules out costless acquisition of the H payoff after arrival. If retaining the reduced criterion, define it as a separate decision model, distinguish its operator from the displayed switching HJB, and frame the closed forms and early investment as conditional benchmark results. Establish strategic-entry robustness in that coherent model before treating the 43% discount as a central quantitative implication.

### Default, recovery, and claim accounting — pass within the stated approximation

The code's `equity_value` returns entry equity NPV, while the manuscript's E denotes going-concern equity. This is handled consistently: subtracting `leverage*I` from the code's equity-plus-debt result is equivalent to the manuscript's `E+D−I`, since the code has already subtracted `(1−leverage)I`. I found no double subtraction in the levered dilemma.

The default boundary, negative root at discount r+λ, recovery cap, and credit-spread benchmark match the stated conventions (`paper/_model.qmd:270`, eq-equity; `paper/_model.qmd:280`, recovery specification; `src/ai_lab_investment/models/duopoly.py:743` and `:795`). Independently differentiating the markup gives `dM/dλ=1/[(β−−1)^2 R]`; combining it with the coefficient derivative gives the paper's net threshold. The distinction between φ-underbar and φ-tilde is economically necessary and correctly made in the current manuscript.

Direct numerical reproduction:

| Leverage | Spread, bps | Five-year no-switch hitting probability |
|---|---:|---:|
| 0.05 | 0.000 | 0.6269% |
| 0.20 | 11.742 | 1.7975% |
| 0.40 | 41.337 | 4.8471% |
| 0.70 | 97.129 | 12.9794% |

These support Section “Credit Risk Analysis” and `fig-credit-risk`; they do not verify actual market spreads or physical default frequencies. The paper labels them appropriately. The coupled-default approximation is covered by passing tests, but I did not independently rederive its complete piecewise free-boundary system.

### Notebook and symbolic support — has issues

**Issue 2 — Major — The supporting derivations still certify two arguments the current paper correctly disavows.**

Locations: `notebooks/model_derivation.ipynb:845` and `:894`, Section 4 “When is A1=0?”; `notebooks/model_derivation.ipynb:1722`, Section 7 “Default Boundary and Faith-Based Survival”; `notebooks/model_derivation.ipynb:2533`, summary; `src/ai_lab_investment/models/symbolic_duopoly.py:23`, module verification description. Comparison: `paper/_appendix.qmd:141`, Internet Appendix A, Step 5b, and `paper/_model.qmd:248`, Proposition 2(ii).

The notebook says (A3) implies A1=0 and validates the simplified stopping solution at baseline. The symbolic module repeats that claim. The paper explicitly explains why it is false and reports a negative A1 in the actual piecewise problem. Moreover, notebook Section 7 writes the λ derivative of XD solely as `(∂XD/∂Aeff)(∂Aeff/∂λ)` and concludes that an increasing Aeff lowers XD, omitting the opposing markup derivative. The manuscript now gives both channels and the stronger net threshold. All cells execute, but these statements are printed or narrated, not established by the successful residual check for the particular solution. Consequently the notebook is not an independent verification of the current stopping argument or complete default comparative static.

Suggested fix: update the notebook and symbolic module to distinguish conditional algebra from switching optimality, remove the A3⇒A1=0 implication, add the complete markup derivative and φ-tilde test, and regenerate stored outputs. Include an executable comparison of the smooth-fit and forcing coefficients and a counterexample where φ lies between the two thresholds. Preserve the useful particular-solution residual check with its correct domain, X below the H trigger.

### Lean statement fidelity — pass on inspected scope; build could not verify

The inspected statements faithfully represent the narrower scope advertised in the manuscript. `lean/AILabProofs/Proposition1.lean:33` takes matching and pasting as hypotheses; `:101` solves the capacity FOC rather than asserting stochastic optimality. `Proposition1Phi.lean:95` identifies the unique interior critical point. `Proposition2.lean:125` rearranges the net inequality; it does not independently derive the markup semi-elasticity. `Duopoly.lean:70` takes continuity and endpoint signs as hypotheses, and `:87` takes strict concavity. These distinctions are also disclosed at `paper/_appendix.qmd:70` (Internet Appendix A, formalization scope). I found no instance in these inspected statements of assuming the claimed algebraic conclusion verbatim as a hypothesis. There is no basis here to claim that Lean verifies equilibrium completeness, the pricing convention, numerical exhibits, or the notebook's stale A3 argument.

### Strategic entry, baseline numbers, and exhibit production — numerical pass with economic limits

The contest derivative `αu^(α−1)s(2−s)` explains the common-allocation critical point. The follower's extra scale elasticity is real, and the code's strict preemption solver checks the bracketing and single-crossing grid rather than silently accepting an endpoint (`src/ai_lab_investment/models/duopoly.py:1340`, Proposition 3 implementation). Global allocation optimality and leveraged uniqueness remain numerical, as labeled. Leader-scale fixing and omitted post-default subgames are explicit restrictions, not a complete unrestricted dynamic game.

Direct reproduction gives:

| Object | Recomputed |
|---|---:|
| βH; βL+ | 1.552859; 3.014995 |
| X*; K*; φ* | 0.004721756; 0.006726639; 0.700855709 |
| XP; XF; KF | 0.002703390; 0.118809288; 0.258819333 |
| XP/X* | approximately 0.5725 |

The single-firm loss percentages are 26.1855 at belief 0.02, 4.1486 at 0.18, 5.6333 at 0.20, and 22.5783 at 0.50. The corresponding levered losses at 0.02/0.20/0.50 are 26.1484/5.3100/21.3926%. Five-year no-switch default at belief 0.50 is 5.0396%, matching the reported 5.04%. These support the rounded headline numbers in the introduction, calibration, valuation, and conclusion, except the sentence in Issue 5.

I traced all eight referenced figure producers. `fig-option-value` and `fig-comparative-statics` use simple H-regime methods; `fig-lambda-option-value` uses `lambda_option_value_curve`; `fig-default-boundaries` and `fig-competition-effect` use the preemption solver; `fig-credit-risk` uses the credit curve; `fig-growth-decomposition` uses the normalized capacity-gap calculation; and `fig-investment-dilemma` uses the unlevered and levered mismatch evaluators. Source locations are `src/ai_lab_investment/figures/paper.py:85`, `:149`, `:213`, `:291`, `:414`, `:368`, `:600`, and `:654`. The wrapper saves these names without duplicating model calculations. The three additional figure files are the documented slides-only outputs, not unexplained paper orphans.

All eight shipped figure PDFs were rasterized and visually inspected, in addition to the PNG contact sheet. Their main curves and captions agree with the inspected producers. Three distinct paths were checked end to end through direct numerical calls: monopoly/preemption, credit-risk claims and hitting probabilities, and belief-mismatch policies/values. I did not perform pixel equality or PDF hash equality against regenerated figures, nor inspect every page of the 111-page manuscript.

### Parameter perturbations — pass for the reported exercise

The full rerun gives 13 admissible and five inadmissible draws. The failed draws and conditions match Internet Appendix E: r down and up, μH down, σ down, and α down. Every reported sign check survives the admissible one-at-a-time draws. Reproduced ranges include dilemma ratio 3.6075–5.9778, matched-error ratio 4.9581–8.0355, trigger ratio 0.5298–0.6283, φ* 0.5919–0.7910, φ-underbar 0.0967–0.2293, and φ-tilde 0.1878–0.3693. This is not a joint-parameter robustness result.

The additional piecewise checks reproduce conservative/aggressive losses of 39.8145%/0.6326% at beliefs 0.02/0.20, and 4.4867% at 0.50. The unrestricted counterparts are 42.6632%, 0%, and 0%. Thus the appendix's sensitivity to the stopping formulation is substantive and reproducible.

## Part 2 — Referee assessment

### Content, contribution, and model

The manuscript clearly distinguishes its contribution from standard real options, strategic capacity choice, and regime-switching credit. The allocation decision linking survival value to collateral destruction is the strongest organizing idea. The literature section acknowledges that fully coupled regime-dependent default boundaries predate this paper; it does not claim novelty merely for adding regime switching to Leland. I did not perform an exhaustive external literature search, so this is an assessment of the articulated contribution, not a certification of priority.

The central institutional problem is that capability is not accumulated. A laboratory can wait, buy compute after AGI arrives, allocate it entirely to training, and obtain the H payoff without the pre-arrival research that the motivation describes. Exogenous λ reinforces this detachment. This explains why removing the scale restriction and allowing reallocation have such large behavioral consequences. The simple model is valuable as an illustration, but for Management Science the paper needs one generalizable managerial insight that survives a credible representation of this capability/commitment margin. Issue 1 addresses the stopping side; Issue 3 addresses the unsupported robustness claim.

**Issue 3 — Major — The appendix asserts that dynamic reallocation preserves the headline asymmetry without solving it; the stated direction does not follow.**

Locations: `paper/_appendix.qmd:535`, Internet Appendix E, “Dynamic training reallocation”; `paper/_discussion.qmd:26`, Section “Limitations”; `src/ai_lab_investment/models/valuation.py:881`, `two_period_dynamic_phi`; exhibit `tbl-dynamic-phi`.

The main text correctly says that the two-period exercise solves allocation and value, not default or belief mismatch, and that implications for the headline mechanisms are conjectures. The appendix nevertheless says the mechanisms would be attenuated “without eliminating them,” and the asymmetry would “narrow but persist.” Its explanation is that allowing over-trainers to recover reduces the aggressive loss. Holding the conservative loss fixed, that change would widen the conservative-minus-aggressive loss gap, not narrow it; allowing under-trainers to acquire training capability later can also reduce the conservative loss. The net ranking is therefore unresolved. The same exercise reports initial training near 0.01 with free reallocation instead of 0.70, so the missing comparison is economically important.

Suggested fix: replace persistence and narrowing assertions with explicitly conditional conjectures, explain both correction channels, and remove directional certainty. Preferably recompute belief losses and default under a revisable allocation with a stock of accumulated capability or an empirically disciplined commitment friction. A small gain in gross value is not a bound on the robustness of the training-based mechanism.

### Calibration and empirical content

The archetypes are appropriately labeled illustrative composites, the assigned training fractions are not represented as measurements, the overlapping uncertainty bands are acknowledged, and inadmissible archetype WACCs are excluded from trigger/capacity optimization. These qualifications deserve credit. Still, the archetypes do not constitute four independently calibrated policy predictions: the main trigger results use common baseline primitives and the inversion rationalizes assigned allocations. The abstract's calibration sentence should be read in that limited scenario sense.

The baseline lies close to the interior-scale boundary, making the extreme leader/follower asymmetry unsurprising but fragile in magnitude. Reporting ratios does not itself remove sensitivity to α and r. The paper now acknowledges this; the exact-model and commitment checks should receive at least as much prominence as the one-at-a-time parameter sweep.

I checked the inversion formula and its numerical logic, but did **not** independently authenticate all company filings, press-report values, executive quotations, or the introductory industry CapEx total. Those source-dependent numbers are not certified by the Python tests. The mixed CapEx/revenue definitions are disclosed and should not be used for cross-sectional inference.

### Writing quality — pass 1: grammar, typographical and rendering defects

**Issue 4 — Major for submission readiness — The calibration sources table is corrupted in the actual blind PDF.**

Location: `paper/_appendix.qmd:422`, Internet Appendix C, `tbl-sources`, with affected following rows at lines 423–426; also the operating-cost row at line 427.

In the successful blind render, Table IA5 on printed appendix page 39 (physical page 85) merges the training, leverage, WACC, growth, and volatility material into math-mode text with literal table separators, and several lines run off the right edge. The final log reports overfull boxes of approximately 327, 133, and 43 points at the generated lines for these rows. I rasterized and inspected the page; this is not merely a warning inferred from the log. The construction `($\sim$50/50)` is parsed incorrectly by Pandoc's dollar-math rules and disrupts following delimiters. The operating-cost `$\approx$30--40\%` construction similarly prints defective delimiters/symbols.

Suggested fix: use `\(\sim 50/50\)` or plain “approximately 50/50,” and use explicit `\(...\)` math or prose in the operating-cost cell. Re-render both profiles and confirm that all eight intended parameter rows are present and fit the page. Do not rely on successful compilation as layout QA.

### Writing quality — pass 2: flow and consistency

The main text is substantially more disciplined than a typical applications-heavy theory draft: numerical results are distinguished from propositions, several policy implications are narrowed, and the role of imposed financing is stated. The price is repeated qualification. Once the economic benchmark is settled, move the most important qualifications into the result statements and shorten the repeated explanations.

**Issue 5 — Minor — The log-error comparison quotes the wrong conservative loss.**

Location: `paper/_valuation.qmd:25`, “Numerical Finding 1,” log-arrival-rate comparison; exhibit `fig-investment-dilemma`.

At λtrue=0.10, beliefs 0.02 and 0.50 are equal and opposite log errors. The computed losses are **26.1855%** and **22.5783%**. The sentence says the aggressive firm loses “the 23% that the conservative firm loses at one fifth of it,” incorrectly giving both losses as 23%. The surrounding text and figure use 26% for the conservative point.

Suggested fix: say that equal multiplicative errors produce losses of approximately 26% versus 23%, much closer than the equal-additive-error comparison. Retain the coordinate-dependence caveat.

### Writing quality — pass 3: notation, units, and domains

**Issue 6 — Minor — The unqualified timing comparative static contradicts the low-λ region already shown in the paper.**

Locations: `paper/_model.qmd:148`, Remark 3, first and final sentences; `paper/_calibration.qmd:42`, “Sensitivity Analysis”; compare `fig-lambda-option-value` and `paper/_model.qmd:150`.

Because K* and the option markup are belief-independent, X* is inversely proportional to optimized Aeff. It therefore rises with λ below the minimum-value turning point and falls above it. Direct evaluation gives X*=0.0052838 at λ=0.005, 0.0054039 at 0.01, and 0.0055153 at 0.02. Remark 3 nevertheless begins by saying higher λ raises Aeff and lowers the trigger without a domain restriction, although its third effect correctly acknowledges the opposite value derivative at low rates.

Suggested fix: state the same φ*>φ-underbar domain on the timing comparative static, and qualify the concluding “shorter timeline invests earlier” statement. Local baseline sensitivity is fine.

**Issue 7 — Minor — The normalization discussion mixes a monetary conversion with changing the optimized cost coefficient, and reverses the value scaling.**

Locations: `paper/_calibration.qmd:38`, “Baseline Results”; `paper/_appendix.qmd:473`, Internet Appendix C, “Normalization.”

Holding the remaining numerical primitives fixed and changing dimensionless c gives κ=c^(1/(γ−1)), K→K/κ, X→X/κ^(1−α), and **V→V/κ**, since both `cK^γ` and `δK/r` scale as 1/κ. The text instead says values scale “by κ.” Moreover, multiplying the old normalized follower cost 0.1317 by $23B gives approximately $3B only as an external monetary conversion; changing c numerically to 23 and re-solving also changes K. In a direct check, c=23 yields follower capacity about 0.0004893, not 0.2588. These are two different operations.

Suggested fix: introduce a monetary unit m, keep normalized c=1, and write dollar investment as `m I_normalized`, with m≈$23B for this illustration. Separately state the homogeneity transformation for an actual change in numerical c, including the inverse scaling of values. Clarify what else changes when physical capacity units are redefined.

### Figures

The eight referenced figures are legible and generally well aligned with their captions. In particular, the default-boundary band is now described as a continuation band rather than an upper operating limit; the credit figure identifies its no-switch probability bound; the growth figure is explicitly a diagnostic rather than a market-value decomposition; and the dilemma caption says capacity is unchanged. These are meaningful safeguards against misinterpretation. The economic limitations in Issues 1 and 3 remain more consequential than cosmetic adjustments. I found no additional figure defect worth a separate numbered finding.

### Tables

The parameter/domain and result-taxonomy tables help distinguish conditional analytical results from numerical claims. The archetype table transparently reports assigned inputs and uncertainty. The principal numerical rows checked against execution agree at their stated precision. Table IA5 is not submission-ready (Issue 4). This was a selective table layout audit, not a visual certification of every table page.

### Robustness

The code appropriately reports inadmissible draws rather than dropping them silently. The exact stopping comparisons are especially informative, and the paper is commendably explicit that optimistic mismatch costs vanish in the unrestricted baseline. Those comparisons establish the limits of the headline mechanism as much as its robustness. The dynamic-φ table and arithmetic-mean contest exercise are useful partial checks, but neither is a solved general alternative equilibrium. In particular the latter removes rival-capacity dependence as well as pie expansion, which the manuscript itself acknowledges.

### Journal fit

Management Science is a defensible target for a rigorous theory paper connecting irreversible compute allocation, strategic entry, and financing. The journal's broad management/finance/operations scope supports that thematic fit; it does not lower the burden of an economically coherent mechanism. The current 45-page main manuscript also leaves substantial work relative to the invited-revision cap: the [official submission guidelines](https://pubsonline.informs.org/page/mnsc/submission-guidelines) specify 32 pages at 1.5 spacing or 47 double-spaced pages for invited revisions. That is **not** an automatic initial-submission rejection rule. This external check was limited to the official guidelines; I did not audit the entire portal checklist.

My referee judgment is that the current paper faces a substantial rejection risk on contribution robustness rather than numerical reproducibility. A Finance framing is plausible if the going-concern/collateral trade-off survives an improved capability model; an operations framing is plausible if capacity and allocation under commitment are the central solved problem. Resolve that choice after the model revision, rather than selecting a department merely from the list of included ingredients. I would not recommend moving down the repository's journal ladder as a substitute for resolving Issue 1.

## Summary of issues

### Critical

None established.

### Major

1. The reduced stopping criterion does not solve the displayed switching problem, and the unrestricted baseline changes pre-switch investment qualitatively.
2. The notebook and symbolic verification documentation retain false A3 and incomplete default-derivative arguments.
3. Dynamic-reallocation persistence/narrowing assertions exceed the solved exercise and do not follow from its explanation.
4. The rendered calibration sources table is corrupted and overflows the page.

### Minor

5. The equal-log-error sentence gives the conservative loss as 23% instead of 26%.
6. The timing comparative static lacks the low-arrival-rate domain qualification.
7. The monetary conversion and cost-coefficient normalization are conflated, and the stated value scaling is reversed.

## Overall recommendation

**Major revision; not ready for Management Science submission.** Preserve the conditional algebra and strong numerical tests. Make a dynamically consistent commitment/capability benchmark the basis of the main contribution, then reassess preemption and belief-error claims against it. Independently repair the notebook, Table IA5, and the three smaller consistency defects. A successful Lean build remains an outstanding validation item for this review, not an observed failure of the proofs.
