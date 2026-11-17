# Review report: "Investing in Artificial General Intelligence"

**Reviewer:** claude-fable-5.2 (independent; I did not read any other file under `reports/`)
**Round:** review_20261101
**Paper content reviewed:** commit `4def5f6` (branch `t3/parallel-paper-review-reports` is one commit ahead of `origin/main`; that commit touches only `reports/`, so the paper, code, Lean and notebook are identical to `origin/main`)
**Target journal assumed:** Management Science (`submission/README.md`)

## Review brief (derived from the paper and repo on this run)

The paper's spine, as the abstract, introduction and conclusion state it, is four results: (1) Proposition 1, closed-form capacity $K^*$ and training fraction $\phi^*$, with capacity invariant to beliefs and allocation pinned by $\lambda/(r-\mu_H)$; (2) Proposition 2, "faith-based survival", a default boundary that falls in $\lambda$ above a closed-form threshold while creditors cannot recover the continuation value; (3) Proposition 3, a preemption equilibrium in which competition compresses timing but leaves $\phi^*$ unchanged; (4) Numerical Finding 1, "Dario's dilemma", pessimism costlier in expected value and optimism costlier in tail default risk. The load-bearing choices are the pure-power ($A_1 = 0$, "unconditional-$A_{\text{eff}}$") pricing convention, the leader-scale convention, the single-boundary default reduction with the inference-only recovery rule, par debt at $r_c < r$, the regime-exclusive revenue technology with $\phi$ committed at installation, and a calibration that sits near the edge of the (A2) window. I audited each of these against the code (`src/ai_lab_investment/models/`), the Lean package (`lean/`), the SymPy notebook, and the rendered paper, then read the paper as a referee.

## What I executed

| Check | Result |
|:--|:--|
| `uv run pytest` (393 tests collected) | all pass |
| Headline numbers recomputed through the package API (scratch scripts, no repo writes) | all reproduce (Section 1.1) |
| `lake exe cache get` + `lake build` on a scratch copy of `lean/` | builds, 8572 jobs, no warnings; no `sorry`/`axiom` in sources; `#print axioms` on ten theorems returns only `propext`, `Classical.choice`, `Quot.sound` |
| `notebooks/model_derivation.ipynb` executed with `nbconvert` on a scratch copy | runs without error |
| `QUARTO_PROFILE=blind quarto render` on a scratch copy of `paper/` | 111 pages (45 manuscript + 66 e-companion); no `??`, no undefined citation; all 44 cite keys resolve in `references.bib` |
| Eight paper figures regenerated from `figures/paper.py` to scratch and compared with the shipped PDFs | pixel-identical at 60 dpi for all eight; I then looked at each one |
| Extra experiments of my own (credit spread and default probability at the firm's own policy, leader spread at entry across $\lambda$, capacity and trigger across beliefs in the precommitted piecewise problem, follower hitting times) | findings 2 to 6 below |

Not run: `just run-pipeline` and `just run-sweep` as such (the sweep's paper-pinned numbers are covered by `tests/test_robustness.py`, which passes); the replication-package zip build; the slides. I did not verify any external source (no web access used), so sourcing claims in the calibration are unverified.

---

## Executive summary

**Correctness.** The implementation is faithful to the paper. Every closed form I re-derived by hand is right ($K^*$, $\phi^*$, $A_{\text{eff}}$, $X^*$, $X_D$, $\underline{\phi}$, $\tilde{\phi}$, the markup semi-elasticity $m$, the first-passage formula), every quoted number I recomputed matches, the shipped figures are exactly what the code produces, and the Lean package builds and states what the paper says it states. The repo is in unusually good shape for a theory paper. I found one stated result that is false on the paper's own range (the credit-spread half of Proposition 3(v), finding 5) and one repo artifact that contradicts the paper (the notebook, finding 11).

**Submission readiness.** Not ready for Management Science, and the reason is not polish. The paper is now so candid about its conventions that it documents its own central weakness: in the model's actual primitives, the policy the paper characterizes is dominated at baseline by never investing before the switch (Internet Appendix B), so the triggers, the preemption game, the entry-time default distances and the "investing too early or too late" reading of Dario's dilemma all describe behaviour the properly solved model does not produce. Disclosure does not fix that for a referee; it hands them the rejection paragraph.

**Single biggest concern (finding 1).** The reduced model is not an approximation to the stated problem and is not itself a well-posed stopping problem; several results presented as structural (belief-invariant capacity, "optimists invest earlier") reverse or disappear in the paper's own exact benchmark (finding 2, new evidence from this review). My recommendation is to make the precommitted-scale piecewise problem, for which a closed form already exists in `piecewise_option.py`, the model of record, or to change one primitive (a capability stock) so that pre-switch training is optimal for an economic reason rather than by convention.

A second cluster concerns the credit-risk half of the paper: at the firm's own optimal policy, debt is riskless in value at every leverage, the "default" boundary is 95% an operating-cost abandonment boundary, and the tail-risk asymmetry attributed to leverage is essentially independent of leverage (findings 3 and 4).

---

## Part 1: Validation

### 1.1 Reproduction of quoted numbers: pass

Recomputed through `SingleFirmModel`, `DuopolyModel`, `ValuationAnalysis` and `piecewise_option`:

| Quantity (location) | Paper | Recomputed |
|:--|:--|:--|
| $\beta_H$, $K^*$, $\phi^*$, $X^*$ (`_calibration.qmd:38`, `tbl-baseline-results`) | 1.55, 0.0067, 0.70, 0.0047 | 1.5529, 0.006727, 0.7009, 0.004722; closed-form $K^*$ agrees with the solver to 8 digits |
| $\underline{\phi}$, $\tilde{\phi}$, $m$ (`_model.qmd:260`, `_appendix.qmd:205`) | 0.18, 0.32, 0.77 | 0.1801, 0.3219, 0.768 (hand) |
| Duopoly, $\ell=0$: $X_P$, $X_F^*$, $K_F$, ratio (`_model.qmd:314`) | 0.0027, 0.119, 0.259, 0.57 | 0.002703, 0.11881, 0.25882, 0.5725 |
| Dilemma losses at $\lambda_{\text{invest}}$ = 0.02 / 0.18 / 0.20 / 0.50 (`_valuation.qmd:25-29`) | 26% / 4% / 6% / 23% | 26.19% / 4.15% / 5.63% / 22.58% |
| Levered losses, $\ell=0.40$ (`_appendix.qmd:279`) | 26.1% / 21.4% | 26.15% / 21.39% |
| Five-year default probabilities at own policy (`_valuation.qmd:31`) | 0.64% / 0.79% / 5.04% | 0.643% / 0.794% / 5.040% |
| Credit grid at $X=0.10$, $K=1$, $\phi=0.5$ (`_valuation.qmd:7`) | 0 / 12 / 41 / 97 bps; 0.63 / 1.80 / 4.85 / 12.98% | 0.0 / 11.7 / 41.3 / 97.1 bps; 0.627 / 1.798 / 4.847 / 12.979% |
| Fig. 1: minimum of value in $\lambda$, inflection (`_model.qmd:150`) | 0.025, 0.085 | 0.0249, 0.083 (400-point grid) |
| Pure-power bias (`tbl-domains`, `_appendix.qmd:357-365`) | +52.9%, +19.1%, +96.1%, +134.6%, 2.6%, 6.9%, 39.8%, 0.6%, 4.5%, 42.7%, 1.0% | all reproduce to the displayed digit |
| $\Gamma$ and smooth-fit coefficient (`_appendix.qmd:147`) | 21.1, 16.5 | 21.14, 16.52 |
| Implied $\lambda$ bands (`tbl-firms`) | [0.05,0.09], [0.06,0.10], [0.03,0.05], [0.09,0.17] | reproduced by hand from the inversion |
| Elasticities of $\phi^*$ and $\varepsilon_{X^*,\lambda}$ (`tbl-elasticities`) | $-1.0$, $+0.5$, $+0.5$, $+0.2$; $-0.2$ | reproduced by hand |

No prose number without a producer was found in the spine.

### 1.2 Independent re-derivation of the closed forms: pass

I re-derived by hand: the $K$ first-order condition and its solution (`_model.qmd:100`, `_appendix.qmd:95-99`); $\phi^* = \rho/(1+\rho)$ (`_model.qmd:104`); $A_{\text{eff}}$ by splitting the integral at the exponential switch time (`_model.qmd:73`); the particular solution of the equity ODE, which gives coefficient $A_{\text{eff}}$ and constant $-(C_D+\delta K)/r$ exactly (`_appendix.qmd:157-165`); $dM/d\lambda = 1/[(\beta_L^- - 1)^2\mathcal{R}]$ and $m = 1/[\beta_L^-(\beta_L^- - 1)\mathcal{R}]$ (`_appendix.qmd:195-197`); the rearrangement to $\tilde{\phi}$ (`_model.qmd:250`); the debt ODE under the perpetuity approximation (it does give the $X^{\beta_L^-}$ form with a riskless post-switch claim); and the first-passage probability (`_appendix.qmd:626`). All correct. The global-maximum argument for $K^*$ in Step 4 is sound.

### 1.3 Lean package: builds, and is a faithful formalization of what the paper says it covers

The theorems I read against the paper (`Proposition1.lean`, `Proposition2.lean`, `Duopoly.lean`) state the paper's algebra, with the right signs, for abstract reals. The scope paragraph at `_appendix.qmd:70-72` is accurate and does not overclaim. Two observations, neither a defect:

- The formalization is of identities and single-variable facts, not of the propositions as stated. For example `K_foc` proves the equivalence of the first-order condition with the closed form under `hden : αβ - (β-1)γ ≠ 0`, but nothing in Lean shows that the right-hand side is positive under (A2) or that the first-order condition is the derivative of $\ln h$; `net_threshold_phi` is, as the README says, an alias of `faith_threshold`. A reader of the sentence "machine-checked in Lean" will assume more. The appendix wording is careful; the cover letter and any talk should be equally careful.
- The Lean package verifies the reduced model's algebra. It is silent on the question a referee will care about most (finding 1), and the paper should not let "machine-checked" stand near the conventions without that caveat. It currently does not, which is right.

### 1.4 The pure-power convention (the load-bearing choice)

**Finding 1 (Critical for submission; structural, not an arithmetic error). The object the paper characterizes is a dominated policy in the paper's own primitives, and the "reduced model" is not a well-posed stopping problem.**
Location: `_model.qmd:140`, `_model.qmd:177`, `tbl-domains` (`_model.qmd:169`), `_appendix.qmd:141-147`, `_appendix.qmd:357-363`.

Three facts, all in the paper or reproduced by me:

1. A function $B X^{\beta_H}$ solves the H-regime ODE (drift $\mu_H$, discount $r$), not the L-regime HJB. Pairing it with the exercise payoff $A_{\text{eff}}X - \Theta(K)$, which is an L-regime installed value, defines the value of an option whose underlying grows at $\mu_H$ before exercise and whose payoff assumes regime $L$ at exercise. No stochastic control problem with consistent dynamics has this as its value function. The sentence "Propositions 1--3 are exact statements about the model these conventions define" (`_model.qmd:185`) is therefore true only in the sense that the algebra is right; there is no model in the usual sense behind it.
2. The forced-ODE coefficient $\Gamma \approx 21.1$ exceeds the smooth-fit coefficient $16.5$, and the pure switching strategy (never invest in $L$, exercise after the switch) is worth more than the paper's policy at every demand level, in both the precommitted and the unrestricted problem (`_appendix.qmd:363`: $1.619$ vs $1.615$, and $1.741$ vs $1.621$, all $\times 10^{-3}$; I reproduce these). In the unrestricted problem no finite pre-switch trigger exists at baseline or anywhere on the $\sigma$, $\alpha$, $r$ ranges.
3. Consequently, at baseline, every quantity defined at a pre-switch entry date (the trigger $X^*$, the preemption trigger $X_P$ and the 43% discount, the distance to default at entry, the five-year default probabilities "at each firm's own policy", the timing half of Dario's dilemma) describes an action the correctly solved single-firm problem does not take.

Assessment. The paper is admirably transparent, and the appendix analysis is good work. But transparency converts a hidden weakness into a stated one; it does not make the reduced model the right object. A Management Science referee in finance or operations will read `tbl-domains` row "Pure power: no pre-switch trigger in the unrestricted problem" and stop.

Suggested fix, in order of preference:
(a) Promote the precommitted-scale piecewise problem to the model of record. It has a closed form up to one scalar root (`piecewise_option.py`), $\phi^*$ carries over exactly, and Dario's dilemma sharpens there. Proposition 1 becomes "closed-form $\phi^*$; $(X^*, K^*)$ from a two-region system", which is still a clean result, and the pure-power form becomes the stated approximation with a measured error.
(b) Change one primitive so that pre-switch investment is optimal: let post-switch revenue depend on capability accumulated before the switch (a stock), not on contemporaneous training compute. This also repairs finding 8 and is the economically natural reading of "training builds future capability".
(c) At minimum, check whether preemption restores pre-switch investment in the exact problem. In a duopoly the pure switching strategy is not available to both firms, so the threat of being preempted may rescue the paper's object. If it does, the duopoly rather than the single firm should be the benchmark, and that is a publishable observation. As written, the paper does not say.

**Finding 2 (Major; new evidence). Belief-invariant capacity and "optimists invest earlier" do not survive the paper's own exact benchmark.**
Location: Proposition 1 and `_model.qmd:116` ("cost and the option premium govern scale, beliefs govern allocation"); Remark 3 (`_model.qmd:148`, "a firm holding a shorter AGI timeline invests earlier"); `_conclusion.qmd:3` ("optimal capacity ... is invariant to beliefs ... That separation is what makes belief errors asymmetric"); caption of `fig-investment-dilemma` ("no point on either curve involves over- or under-building").

I solved `PiecewiseOptionModel(...).optimal_policy(X_0)` at $X_0 = X^*(0.10)/2$ across beliefs:

| $\lambda$ | $K$ piecewise | $K^*$ reduced | $X^*$ piecewise | $X^*$ reduced | $\phi$ |
|:--|:--|:--|:--|:--|:--|
| 0.03 | 0.0021 | 0.0067 | 0.0021 | 0.0055 | 0.24 |
| 0.05 | 0.0070 | 0.0067 | 0.0055 | 0.0053 | 0.42 |
| 0.075 | 0.0127 | 0.0067 | 0.0083 | 0.0050 | 0.59 |
| 0.10 | 0.0158 | 0.0067 | 0.0093 | 0.0047 | 0.70 |
| 0.15 | 0.0181 | 0.0067 | 0.0094 | 0.0043 | 0.82 |
| 0.20 | 0.0184 | 0.0067 | 0.0089 | 0.0040 | 0.88 |
| 0.50 | 0.0158 | 0.0067 | 0.0066 | 0.0033 | 0.97 |

Capacity varies by a factor of nine across beliefs and is hump-shaped; the trigger rises with $\lambda$ from 0.03 to 0.15 (a more optimistic firm invests later, because waiting for the switch is worth more) and only then falls. The paper reports that the levels move (+96%, +135% at baseline) and says levels are "objects of the reduced model", but it does not report that the invariance of $K^*$ and the sign of $\partial X^*/\partial\lambda$ are also properties of the convention. Both are presented as economic results, and the conclusion opens with the first.

Suggested fix: state both as properties of the pure-power convention in `tbl-domains` and wherever they are used; drop "That separation is what makes belief errors asymmetric" (in the exact problem a wrong belief does change scale and coupon); restate Remark 3's timing prediction as holding for $\lambda \gtrsim 0.15$ in the piecewise problem, or drop it. Only $\phi^*$ and its comparative statics are convention-free, and the paper should lead with that.

### 1.5 Credit risk, recovery and default probabilities

**Finding 3 (Major). The tail-risk asymmetry is not a leverage effect; the "default boundary" at the optimal policy is almost entirely an operating-cost abandonment boundary that the unlevered firm is denied by convention.**
Location: `_valuation.qmd:25` ("leverage's distinctive contribution is to the tail risk of overinvestment"), `_valuation.qmd:29-31`, `_valuation.qmd:37` ("especially with leverage"), `_introduction.qmd:17`, `_literature.qmd:13` ("leverage concentrates tail risk on the aggressive side"), `_appendix.qmd:279-281`, `_appendix.qmd:556`; code `duopoly.py:424` (`if lev <= 0: return 0.0`).

Five-year default probabilities at each firm's own policy, recomputed with `dario_dilemma_leveraged`:

| $\ell$ | correct beliefs | $\lambda_{\text{invest}}=0.02$ | $\lambda_{\text{invest}}=0.50$ | ratio aggressive / correct |
|:--|:--|:--|:--|:--|
| 0.01 | 0.48% | 0.60% | 4.06% | 8.4 |
| 0.05 | 0.50% | 0.62% | 4.15% | 8.3 |
| 0.20 | 0.56% | 0.69% | 4.52% | 8.1 |
| 0.40 | 0.64% | 0.79% | 5.04% | 7.8 |
| 0.70 | 0.79% | 0.97% | 5.88% | 7.5 |

The "nearly eight times" figure is 8.4 times at one percent leverage and falls slightly as leverage rises. The reason is in `_appendix.qmd:281`: $\delta K/r$ is eighteen times $C_D/r$ at $K^*$, so $X_D = M(C_D/r + \delta K/r)/A_{\text{eff}}$ is 95% operating cost. $X^*/X_D$ is 5.3 at $\ell = 0.05$ and 4.7 at $\ell = 0.95$. The model then sets $X_D = 0$ and the default probability to zero at exactly $\ell = 0$ (`duopoly.py:424`, `valuation.py:226`), and the paper says the unlevered firm has "no abandonment option" and that omitting it is "negligible" (`_model.qmd:272` footnote). It is not negligible relative to the levered wedge: the wedge between the levered and unlevered loss curves (1.2 points at $\lambda_{\text{invest}}=0.50$) appears in full at $\ell = 0.01$ (loss 21.6% against 22.6% at $\ell=0$, 21.4% at $\ell = 0.40$). The wedge is the abandonment option being switched on, not leverage.

Consequences: (i) the claim that leverage concentrates tail risk is unsupported at the calibrated policy; what the model shows is that over-training plus early entry brings the firm closer to an operating-cost shutdown boundary; (ii) "leverage therefore raises its measured value slightly" (`_valuation.qmd:29`) is an artifact of the discontinuity at $\ell = 0$; (iii) the headline tail-risk numbers are quoted at $\ell = 0.40$ while the archetypes carry 0.05 to 0.15 (`tbl-firms`), which invites the reader to think the leverage level matters.

Suggested fix: give the unlevered firm the same abandonment option (set $C_D = 0$ in `eq-default-boundary`, no code change beyond removing the early return), report the default-probability table above, and rewrite the claims as "distance to an operating-cost shutdown boundary", with leverage a second-order shifter at the model's scale. This is a more honest and arguably more interesting statement for labs whose fixed operating commitments dwarf their debt.

**Finding 4 (Major). At the firm's own optimal policy, debt is riskless in value at every leverage, so the spread is zero and the loss-given-default channel is inoperative; the credit exhibit is evaluated far from any policy the model produces.**
Location: `_model.qmd:278-282` (recovery), `_valuation.qmd:7`, `fig-credit-risk` and `_appendix.qmd:630`, prediction 1 in `_discussion.qmd:13`; code `duopoly.py:809-834` ("Gross of operating costs"), `valuation.py:137-191`.

At $(X^*, K^*, \phi^*)$ the recovery cap binds for every leverage I tried, including $\ell = 0.95$: $(1-b)\Lambda(X_D)$ is 2.8 times the coupon claim at $\ell = 0.40$ and still 1.2 times at $\phi = 0.97$. So $D = C_D/r$, the spread is identically zero, and "training raises the loss given default" has no effect on any priced object at the calibrated optimum. The paper says in passing that "at this calibration the recovery cap binds" (`_appendix.qmd:281`) but does not draw the consequence.

Why: $\Lambda$ capitalizes the inference revenue gross of the operating cost that drives the firm into default in the first place. At $X_D$ the inference business cannot cover $\delta K$; a buyer who had to pay the operating cost on the inference fraction would bid less than zero. Leland's liquidation value is an unlevered asset value, which nets operating costs; "gross of operating costs, following Leland (1994)" in the docstring is not what Leland does.

The spreads in the paper (12, 41, 97 bps) come from $X = 0.10$, $K = 1$, $\phi = 0.5$: a capacity 150 times $K^*$ and a demand level 21 times $X^*$, where the convex investment cost makes the coupon comparable to the operating cost. The text calls this "a representative interior allocation" but does not say that no firm in the model is ever at that point.

Suggested fix: net the operating cost of the inference fraction out of $\Lambda$ (or model recovery as a fraction of the unlevered inference-only asset value), then report spreads at the model's own policies (leader at $X_P$, follower at $X_F^*$). If spreads at the optimal policy stay near zero, say so, and present Section 4.1 as a stress test at an explicitly off-equilibrium scale. Prediction 1's "recover less when they do" needs the recovery rule to bind somewhere the model operates.

**Finding 5 (Major). The credit-spread half of Proposition 3(v) is false on the paper's stated range, and the reason given for it is wrong.**
Location: `_model.qmd:306` ("the credit spread at entry is correspondingly weakly increasing in $\lambda$"), `_appendix.qmd:255` ("the Leland credit spread at entry, which is monotonically decreasing in $X_P/X_D$, is weakly increasing in $\lambda$. This is verified computationally across all parameterizations tested"); `tests/test_duopoly.py:1195-1209` pins only the ratio $X_P/X_D$ at three values of $\lambda$; I found no code or test that computes the leader's spread at entry.

I computed it with the paper's own $D(X)$ formula at the solved equilibrium, with the anticipating leader's boundary:

| $\lambda$ | $X_P/X_D$ | spread at entry, $\ell=0.40$ (bps) | spread at entry, $\ell=0.65$ (bps) |
|:--|:--|:--|:--|
| 0.05 | 2.63 | 0.0 | 0.0 |
| 0.10 | 2.55 | 0.0 | 0.0 |
| 0.15 | 2.49 | 0.0 | 30.7 |
| 0.20 | 2.44 | 0.6 | 56.1 |
| 0.25 | 2.41 | 21.7 | 63.2 |
| 0.30 | 2.37 | 30.3 | 63.1 |
| 0.40 | 2.32 | 33.2 | 56.0 |
| 0.50 | 2.29 | 30.1 | 47.6 |

The distance-to-default half of 3(v) holds on the whole range. The spread is zero up to $\lambda \approx 0.15$ at $\ell = 0.40$ (finding 4), then hump-shaped: it peaks near $\lambda = 0.40$ at $\ell = 0.40$ and near $\lambda = 0.25$ to $0.30$ at $\ell = 0.65$, and falls thereafter. The spread is not a function of $X_P/X_D$ alone: the discount exponent $\beta_L^-$ becomes more negative as $\lambda$ rises (from $-2.0$ to $-4.1$), because a faster switch makes the debt riskless sooner, and the recovery rate moves with $\phi^*(\lambda)$. The same pattern appears with the monopoly boundary in place of the anticipating one. Caveat: this is my construction from the paper's formulas, since the repo has no leader-debt-at-entry function; it should be re-derived by the author before the text is changed.

Suggested fix: drop the spread clause from Proposition 3(v) or restate it as hump-shaped with the mechanism; add the computation and a test.

**Finding 6 (Major). In the baseline duopoly the follower essentially never enters, and the main-text exhibit and the Amodei mapping are about that follower.**
Location: `_model.qmd:262` and `fig-default-boundaries`; `_model.qmd:314`.

With $X_F^*/X_P = 44$: under the L-regime dynamics the log-drift is negative ($\mu_L - \sigma^2/2 = -0.021$), the probability of ever reaching $X_F^*$ is 7.6%, and the probability of reaching it before the switch is about 0.03%; after the switch the expected time to reach it is about 130 years. The paper flags the scale asymmetry as "not a robust prediction" (`_model.qmd:314`), but does not translate it into time, and `_model.qmd:262` attaches the Amodei scenario ("a firm committed to trillion-dollar compute purchases faces bankruptcy") to the follower's $X_F^*/X_{D,F}$. The equilibrium is, in calendar time, a monopoly disciplined by a threat that is never executed, with a 0.0067-capacity leader that would hold a 19% contest share if the threat were executed.

Suggested fix: report the hitting-time implication next to the scale ratio; move the Amodei sentence to the leader or drop it; consider making `fig-default-boundaries` about the leader, whose boundary is the one reached on the equilibrium path.

### 1.6 Dario's dilemma

**Finding 7 (Major, overstated claim). The expected-value asymmetry is largely a statement about the coordinate in which belief errors are measured.**
Location: abstract (`index.qmd:25`), `_introduction.qmd:17`, Numerical Finding 1 (`_valuation.qmd:25`), `_valuation.qmd:37`, `_conclusion.qmd:7`.

The 26% versus 4 to 6% comparison sets a belief of one fifth of the truth against a belief of 1.8 to 2 times the truth. For proportional errors the paper's own numbers are 26.2% (one fifth) against 22.6% (five times), a ratio of 1.16, and that is what the sweep's "asymmetry ratio 3.6 to 6.0" and the matched pair $\lambda_{\text{true}}(1 \pm 0.8)$ do not test. Since $\lambda$ is a positive rate with a lower bound at zero, and the paper itself maps beliefs to expected horizons $1/\lambda$, the additive metric is the less natural one: in horizon terms, 0.02 is a 40-year error and 0.18 is a 4.4-year error around a 10-year truth. Numerical Finding 1 states the caveat, which is to its credit, but the abstract, introduction, Section 4.3 and conclusion all lead with the additive comparison.

Suggested fix: state the finding as "the loss function is steep on the pessimistic side in levels of $\lambda$ and nearly symmetric in logs"; put the 26% against 23% comparison beside the 26% against 6% one wherever the latter appears; soften "costs far more" at `_valuation.qmd:37` and the inference that "aggressive investment ... is consistent with value maximization". I checked the mechanism: the loss is almost exactly $1 - [g(\phi_b)/g(\phi^*)]^{\beta_H}$ evaluated under the true $\lambda$ (26.15% against 26.19%), so the "allocation channel dominates" claim is right, and for the conservative firm the timing error is slightly helpful rather than harmful given its allocation. The sentence at `_appendix.qmd:271` ("the timing factor is approximately symmetric, contributing only weakly") understates timing on the aggressive side, where it accounts for about 1.7 of the 5.6 points at $\lambda_{\text{invest}} = 0.20$.

### 1.7 Calibration tracing

**Finding 9 (Major). The archetypes have no downstream use, the abstract and several cross-references say otherwise, and the one mapping that is used contradicts the stated beliefs the introduction is built on.**
Location: abstract (`index.qmd:24`); `_calibration.qmd:7` ("That dispersion of beliefs is what generates the cross-sectional variation analyzed in @sec-valuation"); `_model.qmd:292`; `_appendix.qmd:441`; `_conclusion.qmd:5` ("more optimistic firms train more, consistent with the archetypes in @sec-calibration").

(i) Of the six rows of `tbl-firms`, only $\hat{\phi}$ feeds a computed number, through the one-line inversion $\lambda = (\hat\phi/(1-\hat\phi))^{1-\alpha}(r-\mu_H)$. Archetype leverage (0.05 to 0.15) is never used; every levered result is at 0.20 to 0.70. Archetype WACCs are outside the (A2) window for three of four and enter only a robustness remark. Section 4 contains no cross-sectional or archetype-level analysis (the figure that had one, `fig_firm_comparison`, is slides-only), so the three cross-references above point at nothing. "Calibration to four AI lab archetypes shows how heterogeneous beliefs ... can generate cross-sectional differences in investment" in the abstract describes an exercise the paper does not contain, particularly since $K^*$ is belief-invariant in the reduced model.
(ii) The conclusion's "consistent with the archetypes" is circular: the $\hat\phi$ are assigned by the author, and the calibration section itself says the inversion "is not evidence that beliefs explain observed differences" (`_calibration.qmd:32`).
(iii) The model's allocation rule is strongly at odds with the stated beliefs it cites. The bibliography note for @amodei2026dwarkesh records a 90% probability of transformative AI within ten years, i.e. $\lambda \approx 0.23$, at which $\phi^* = 0.90$; the same source gives "roughly 50/50" as the allocation. At the range the paper attributes to @amodei2024machines ($\lambda \approx 0.30$ to $0.50$, `_calibration.qmd:7`) $\phi^*$ is 0.94 to 0.97. Conversely the Anthropic-like $\hat\phi = 0.55$ implies a 15-year expected horizon. The paper mentions that baseline $\lambda$ is "more conservative" than these statements but never confronts the size of the gap, which is the most direct piece of external evidence on the model's central closed form. The dynamic-reallocation exercise (`tbl-dynamic-phi`) points the same way, since any ability to re-purpose compute pushes the optimal pre-switch $\phi$ down.

Suggested fix: cut the abstract sentence or replace it with what is done ("an inversion of the allocation rule maps assumed training shares to implied arrival rates"); delete the three dangling cross-references; delete "consistent with the archetypes"; add a short paragraph that reports $\phi^*$ at the stated executive beliefs and discusses the discrepancy as evidence on the commitment assumption (finding 8). Consider moving `tbl-firms` to the Internet Appendix, which also saves main-text space.

**Finding 10 (Major, mostly disclosed). The interior solution exists only in a narrow window and the baseline sits near its edge.**
Location: `_calibration.qmd:9`, `_calibration.qmd:13`, `tbl-elasticities`, `_appendix.qmd:501`.
(A2) admits $r \in (0.097, 0.135)$, $\alpha \in (0.356, 0.534)$, $\sigma \in (0.19, 0.39)$; both $\pm 25\%$ perturbations of $r$ leave the window; trigger and capacity elasticities are 20 to 29; the follower-to-leader capacity ratio of 38 comes from a 19% change in an effective elasticity. The paper says all of this. My assessment is that it is more damaging than the framing "we report ratios, not levels" allows: ratios such as the 43% preemption discount, $X_F^*/X_P$, and the entry-time default distances inherit the same near-degeneracy (the discount becomes 86% under leader re-optimization and 94% at $\sigma = 0.20$). The parts of the paper that are robust to the window are exactly the $\phi$ results. Suggested fix: reorganize the quantitative section around the convention-free and window-free objects ($\phi^*$, $\underline\phi$, $\tilde\phi$, the loss function in $\phi$), and present trigger and capacity magnitudes as illustrations. A cost function with a fixed component, or decreasing-returns revenue with a capacity-independent markup, might widen the window; worth one paragraph on why the window is this narrow.

### 1.8 SymPy notebook

**Finding 11 (Major for the repo, Minor for the manuscript). `notebooks/model_derivation.ipynb` runs, but it asserts the claim the paper now explicitly disclaims, and it omits the markup channel.**
Location: notebook cell 18 ("The homogeneous term $A_1 = 0$ when no interior trigger exists in regime $L$ ... when $\Phi_L \geq 1$"), cell 19 output ("$\Phi_L > 1 \Rightarrow A_1 = 0$. The simplified $F_L = C X^{\beta_H}$ IS valid at baseline"), cell 42 ("=> Simplified ... is VALID"), cell 53 item 3 ("At baseline parameters, $A_1 = 0$ ..., validating the simplified form"); cell 35 and cell 53 item 7 (sign of $dX_D/d\lambda$ from the $A_{\text{eff}}$ channel alone).
The paper says (A3) does not imply $A_1 = 0$, that the piecewise solution has $A_1 \approx -1.0\times10^4$, and that the net sign needs $\tilde\phi$, not $\underline\phi$. The notebook also identifies the option coefficient with $\Gamma = 21.14$, whereas the paper's is the smooth-fit 16.5. It covers nothing in Proposition 3, $\tilde\phi$, or the piecewise problem. `AGENTS.md` and `paper/AGENTS.md` describe it as the SymPy derivations "backing the propositions", and the paper's acknowledgments footnote points readers to the repository. Suggested fix: update cells 18, 19, 35, 42 and 53 to the paper's current position (and to the smooth-fit coefficient), or mark the notebook as historical; a referee who opens it will find the repo arguing against the manuscript on its most delicate point.

### 1.9 Code quality: pass

Deterministic multistart, no random seeds on any paper path, solvers raise on (A2) failure and on a failed single-crossing check instead of truncating, 393 tests with paper numbers pinned. One gap: no test for the spread clause of Proposition 3(v) (finding 5). One convention worth a comment in code and paper: `default_boundary` and `default_probability` return zero at `leverage <= 0`, which creates the discontinuity in finding 3.

---

## Part 2: Paper review

### 2.1 Content and contribution

**Finding 8 (Major). The central trade-off exists only because of the commitment assumption, and the motivating quotation is about a margin the model shuts down.**
Location: `_introduction.qmd:5`, `_introduction.qmd:17`, `_model.qmd:39`, `tbl-domains` rows "Training as a flow" and "Single lump", `_discussion.qmd:26-28`, `tbl-dynamic-phi`.

(i) Training is a flow proxy: post-switch revenue depends on the training compute in place after the switch, with no accumulated capability. Then nothing is gained by training before the switch except through the assumption that $\phi$ is frozen at installation. The paper's own two-period exercise confirms it: with free reallocation the pre-switch training fraction goes to the lower bound (0.01). The introduction's economics ("a firm that bets on the future by allocating capacity to training weakens its ability to survive to that future") is the economics of a capability stock; the model delivers it through a rigidity that the paper concedes is counterfactual ("firms dynamically reallocate GPUs between training and inference on timescales of weeks", `_appendix.qmd:469`). This is the same root as finding 1: because nothing accumulates, waiting for the switch dominates.
(ii) Amodei's quotation is about buying too much compute. In the reduced model capacity does not respond to beliefs, a point the figure caption has to make explicitly. The dilemma the paper prices is a timing and allocation dilemma, and the term "overinvestment" is used throughout for a firm that installs exactly the same capacity.

Suggested fix: a capability stock (even the simplest version: H-regime revenue proportional to $(\bar\phi K)^\alpha$ where $\bar\phi$ is the pre-switch allocation, with post-switch re-optimization of the remainder) would make pre-switch training valuable for the stated reason, would make early investment optimal, and would likely make capacity respond to beliefs. That is a different and better paper, and much of the existing machinery carries over. Short of that, rename "over/underinvestment" to "over/under-training" and say plainly in the introduction that the commitment assumption carries the trade-off.

**Contribution against the literature.** The positioning paragraph (`_literature.qmd:13`) is well argued: a single decision variable that moves the default boundary and the liquidation collateral in opposite directions is new relative to homogeneous-capital investment and default models. Given finding 4, though, the "collateral" half is not operative at the calibrated optimum, so the claimed marginal contribution currently rests on a recovery rule that never binds where the model operates. The role-invariance result (Proposition 3(ii)) is the cleanest genuinely new analytical result and deserves more prominence; it survives every convention and the leader re-optimization.

**Narrative.** The paper has been revised into a defensive crouch. `tbl-domains`, the four conventions, and the repeated "this is not a result" qualifiers are honest, but the reader finishes Section 2 unsure what the paper claims. A top-journal theory paper states a model, solves it, and discusses extensions; this one states a model, replaces it with conventions, and reports how far the conventions are from the model. The fix is finding 1(a) or (b), not more qualifiers.

**Abstract.** Stands alone and is accurate except for the archetype sentence (finding 9) and the unqualified asymmetry (finding 7).

### 2.2 Writing quality

#### Pass 1: grammar, typos, typesetting

- **12 (Minor).** `_appendix.qmd:323`: "Two properties ... are used elsewhere" is followed by First, Second, Third. Fix the count.
- **13 (Minor).** `_appendix.qmd:215`: the conventions are said to be "collected immediately before the statement of Proposition 3". They are in Section 2.4; the paragraph before Proposition 3 is about default and entry. Stale pointer.
- **14 (Minor).** `_appendix.qmd:133-135`: "Step 5b" follows Step 6 and the proof's $\square$, with a sentence explaining its own placement. Rename it (for example "Remark on the pure-power form") and drop the explanation.
- **15 (Minor).** Revision-history language in the e-companion: "Derivations demoted from the main text", "the 2026 consolidation of the main text" (`_appendix.qmd:303`); "the limitation of the model most often raised" (`_appendix.qmd:519`); "which the main text says are 'verified computationally' without stating them" (`_appendix.qmd:303`). A referee should not see the paper's editing history.
- **16 (Minor).** `_introduction.qmd:7`, footnote: the post is dated "2025", but the status ID `2025124840806514916` decodes (snowflake timestamp) to 21 February 2026. I could not open the link; the date in the footnote should be checked.
- **17 (Minor).** `_model.qmd:41` footnote cites @deepseek2025r1 (a Nature paper on reinforcement learning for reasoning) for "hardware obsolescence". The source does not support that; cite something on GPU depreciation or drop it.
- **18 (Minor).** `fig-investment-dilemma`: the red annotation "Overinvestment (aggressive)" is overprinted by both loss curves and the shading edge near $\lambda_{\text{invest}} \approx 0.3$. Move it below the curves (`paper.py:733-739`).
- No LaTeX defects in the scratch build: no unresolved references or citations, no table running off the page that I could detect in the text layer.

#### Pass 2: flow and consistency

- **19 (Minor).** Asymmetry ratio: "from about 4.6 to about 2.2" (`_valuation.qmd:39`) against "from about $4\times$ ... to about $2\times$" (`_appendix.qmd:546`). Use one.
- **20 (Minor).** `_discussion.qmd:11` says "The model generates four cross-sectional predictions", and prediction 2 then says it is "a conjecture ... rather than a model implication". Say three predictions and one conjecture.
- **21 (Minor).** Prediction 3 (`_discussion.qmd:15`) is about the equity value of AI labs but is derived from the pre-investment option value at $X = 0.002$ (`fig-lambda-option-value`). For an installed firm at fixed $\phi > \underline\phi$, $A_{\text{eff}}(\lambda) = (a + \lambda b)/(d + \lambda)$ is increasing and concave for every $\lambda$, with no convex range. The prediction is cleaner and applies to the firms in question if stated on installed value.
- **22 (Minor).** `_discussion.qmd:22` cites @sec-calibration for "preemption cuts the leader's trigger well below the monopolist's"; the result is in @sec-duopoly. Similarly "the solution convention discussed after Proposition 1" (`_calibration.qmd:38`, `_appendix.qmd:219`, `_appendix.qmd:471`) should point to @sec-conventions.
- **23 (Minor).** Assumption 1: (A3) is implied by (A2) on the whole admissible range at baseline ((A3) needs $\alpha \le 0.67$, (A2) needs $\alpha < 0.534$) and, by the paper's own account, does not deliver the pure-power form; (A4) is a property of the functional form, not an assumption. Both can go, or (A3) can become a remark. As written (A3) reads as if it licensed the convention ("this is the condition under which the paper adopts the simplified option value", `_model.qmd:55`), and the next page says it does not.
- **24 (Minor).** Caveats mostly travel with their claims. Exceptions: the abstract and conclusion state belief-invariant capacity and the asymmetry without the convention and metric caveats (findings 2 and 7); the introduction's "roughly 43%" carries its caveat, good.
- The headline numbers agree across abstract, introduction, body, captions and conclusion.

#### Pass 3: notation

- **25 (Minor).** $\hat\phi$ is "not an observed quantity" (`tbl-firms` caption, `_calibration.qmd:30`) and "a firm's observed training fraction" (`_discussion.qmd:11`; also `_appendix.qmd:467`, `:533`). Pick "assigned" for the calibration and a different symbol or wording for the empirical object in the predictions.
- **26 (Minor).** Overloaded symbols: $\rho$ is the allocation ratio in `eq-phi-star` and the hazard-adjusted discount rate in `_appendix.qmd:519` (which is $\Delta$ in Proposition 2); the total cost is $\Theta(K)$ in the proofs and $b(K)$ in `_calibration.qmd:15` and `_appendix.qmd:437`, while $b$ is the bankruptcy cost; $g$ is the allocation factor $g(\phi)$ and the scale-gap index; $s_L$ (leader's share, `_model.qmd:191`, `:290`) sits next to $s^L$ (L-regime share); $F$ is the single-firm option and the follower value (acknowledged at `_appendix.qmd:215`); $\Delta$, $\Delta_F$, $\Delta V$.
- **27 (Minor).** "Leverage ratio (debt / total capital)" in `tbl-parameters` and `tbl-firms` against $\ell = P/I(K)$ (`_model.qmd:226`) and the "Leverage (D/I)" axis labels. Debt over investment outlay is what the model uses.
- **28 (Minor).** "Over/underinvestment" for a belief error that leaves capacity unchanged (finding 8(ii)).

### 2.3 Figures

All eight figures referenced in the paper are regenerated exactly by `figures/paper.py`; three more PDFs in `paper/figures/` are slides-only and documented as such (not orphans). I traced `fig-lambda-option-value`, `fig-investment-dilemma` and `fig-credit-risk` end to end and viewed all eight.

- `fig-lambda-option-value`: caption matches the producer (80 points on $[0.005, 0.80]$, $X = 0.002$); minimum and inflection confirmed on a finer grid.
- `fig-default-boundaries`: matches caption (40 leverage levels, log axis). Substantive issue is finding 6.
- `fig-competition-effect`: matches; ratio from 0.64 to 0.54.
- `fig-investment-dilemma`: matches (40 points; the grid does not include $\lambda = 0.10$ exactly, so the plotted minimum is 0.05% rather than zero, invisible at the plotted scale). Issues 7 and 18. Given finding 3, an added line at $\ell = 0.01$ would show the reader that the levered and unlevered curves differ by a discontinuity, not by leverage.
- `fig-credit-risk`: matches the producer, and the caption states the evaluation point. Issue is finding 4: the evaluation point is far off any model policy.
- `fig-option-value`, `fig-comparative-statics`, `fig-growth-decomposition`: captions match what is drawn; the non-monotone $\gamma$ panel is described correctly.

### 2.4 Tables

- `tbl-domains`: every "measured size" traces to code and reproduces. It should gain rows for finding 2 (capacity invariance and the sign of $\partial X^*/\partial\lambda$ are convention-dependent) and finding 4 (recovery cap binds at the optimal policy).
- `tbl-firms`, `tbl-firms-data`: internally consistent (ratios 0.67, 0.96, 1.52, 20.0 follow from the rows; bands reproduce). Sourcing unverified. See finding 9 on use.
- `tbl-elasticities`, `tbl-baseline-results`, `tbl-fixedpie`, `tbl-dynamic-phi`, `tbl-duopoly-dilemma`: pinned by passing tests; the $\phi$ elasticities reproduce by hand.
- `tbl-result-taxonomy`: accurate, apart from the Proposition 3(iii)-(v) row, which should exclude the spread clause (finding 5).
- **29 (Minor).** `tbl-parameters` labels $r$ and $r_c$ "Inferred = backed out from observable proxies", while `_calibration.qmd:9` says $r$ is "chosen ... rather than estimated". Use "Chosen" for both.

### 2.5 Robustness

The qualitative $\phi$ results survive everything shipped: the $\pm 25\%$ sweep, the arithmetic-mean benchmark, leader re-optimization, both piecewise problems. What does not survive the shipped alternatives, or has not been tested against them:

- trigger and capacity levels, the invariance of capacity, and the sign of the timing response (finding 2);
- the size of the optimistic-side loss (22.6% in the reduced model, 4.5% precommitted, zero unrestricted; disclosed);
- the leverage attribution (finding 3) and the spread monotonicity (finding 5);
- faith-based survival and the dilemma under a revisable allocation (not solved; disclosed as conjecture).

The sweep is one-at-a-time around a baseline at the edge of the admissible window, and five of eighteen draws are inadmissible. A joint sweep over the admissible region (a few thousand draws is cheap for the single-firm objects) would turn "no sign reversal in thirteen draws" into a real statement.

### 2.6 Journal fit

- **30 (Major, known to the author).** Length: 45 pages at 1.5 spacing in my build, against Management Science's 32-page cap for invited revisions, plus a 66-page e-companion. The main text can lose `tbl-firms`, most of Section 2.4 if finding 1(a) is adopted, and Remark 2.
- Fit. The question (capacity, allocation and default under regime uncertainty) suits the Finance or Operations department. The obstacles are substantive: a reduced model that is not the solution of the stated problem (finding 1), a credit block that is inoperative at the model's own scale (findings 3 and 4), and a calibration that does no work (finding 9). In its current form I would expect a reject or a reject-and-resubmit at Management Science, and similar reactions at JFQA and Review of Finance, because the first objection is about the model and not about the venue. With the model of record changed to the piecewise problem (or a capability stock) and the credit block repaired, the $\phi$ results (closed-form allocation, role invariance, the two thresholds, the steep pessimistic side of the loss function) make a coherent and novel paper for Management Science. If the author prefers to submit the current structure, JEDC is the realistic home: its readers accept convention-based tractability with measured errors, and the appendix B analysis would be read as a strength there.
- The AI-use disclosure and the Lean package are assets, provided "machine-checked" is never left near a claim the Lean files do not cover (Section 1.3).

---

## Summary of issues

### Critical

1. The characterized policy is dominated in the paper's own primitives and the reduced model is not a well-posed stopping problem; disclosure does not resolve it (Section 1.4).

### Major

2. Capacity invariance to beliefs and the sign of $\partial X^*/\partial\lambda$ fail in the precommitted piecewise problem, yet are presented as results and lead the conclusion (Section 1.4; new evidence).
3. The tail-risk asymmetry is independent of leverage (8.4 times at $\ell = 0.01$, 7.8 times at $\ell = 0.40$); $X_D$ is 95% operating cost; the levered wedge is an abandonment option switched on at $\ell > 0$ (Section 1.5).
4. Debt is riskless in value at the optimal policy for every leverage; the recovery rule is gross of the operating cost that causes default; spreads in the paper come from a point 150 times $K^*$ (Section 1.5).
5. The spread clause of Proposition 3(v) is false on the stated range (hump-shaped in $\lambda$), is untested, and its stated justification is wrong (Section 1.5).
6. The baseline follower essentially never enters (0.03% before the switch, about 130 years after); the main-text exhibit and the Amodei mapping concern that follower (Section 1.5).
7. The expected-value asymmetry is mostly a property of the additive error metric (26% against 23% for proportional errors); abstract, introduction and conclusion lead with the additive version (Section 1.6).
8. The training-versus-inference trade-off is carried by the commitment assumption, not by capability accumulation; the motivating quotation concerns capacity, which the model holds fixed (Section 2.1).
9. The archetypes have no downstream use; three cross-references and the abstract promise a cross-sectional analysis that is absent; "consistent with the archetypes" is circular; the allocation rule implies $\phi^* \approx 0.90$ to $0.97$ at the stated executive beliefs against a stated 50/50 (Section 1.7).
10. Narrow (A2) window and extreme elasticities contaminate ratios as well as levels (Section 1.7; mostly disclosed).
11. The SymPy notebook asserts $A_1 = 0$ from (A3) and omits the markup channel, contradicting the paper (Section 1.8).
30. Main text is 45 pages against a 32-page revision cap (Section 2.6; known).

### Minor

12. "Two properties" followed by three (`_appendix.qmd:323`).
13. Stale pointer to conventions "immediately before" Proposition 3 (`_appendix.qmd:215`).
14. "Step 5b" after Step 6 (`_appendix.qmd:133`).
15. Revision-history language in the e-companion (`_appendix.qmd:303`, `:519`).
16. Footnote date "2025" for a post whose ID decodes to February 2026 (`_introduction.qmd:7`).
17. @deepseek2025r1 cited for hardware obsolescence (`_model.qmd:41`).
18. Annotation overprinted in `fig-investment-dilemma`.
19. "4.6 to 2.2" against "$4\times$ to $2\times$".
20. "Four predictions", one of which is declared a conjecture.
21. Prediction 3 derived from the pre-investment option, better stated on installed value.
22. Cross-references to the wrong section for the preemption result and the leader-scale convention.
23. (A3) redundant and misleadingly worded; (A4) not an assumption.
24. Convention and metric caveats missing from abstract and conclusion.
25. $\hat\phi$ "assigned, not observed" against "observed".
26. Overloaded symbols ($\rho$, $b$, $g$, $s_L$, $F$, $\Delta$; $\Theta(K)$ against $b(K)$).
27. "Debt / total capital" against $\ell = P/I(K)$.
28. "Over/underinvestment" at unchanged capacity.
29. $r$ and $r_c$ labelled "Inferred" in `tbl-parameters`.

---

## Overall recommendation

Do not submit to Management Science in the current form. The code, proofs, numbers and figures are right, and the allocation results are novel and robust; the paper around them is built on a pricing convention that the paper itself shows is neither the solution nor a close approximation of the stated problem, and on a credit block that does not bind at the model's own scale.

Priority order for revision:

1. Decide the model of record (finding 1): the precommitted-scale piecewise problem, or a capability stock. Re-derive which of the timing and capacity statements survive (finding 2) and rebuild the propositions around what does.
2. Repair the credit block: give the unlevered firm the abandonment option, net operating costs out of recovery, evaluate at model policies, and restate the tail-risk result as operating leverage (findings 3, 4, 5).
3. Restate Dario's dilemma with both error metrics and without the capacity language (findings 7, 8).
4. Cut or demote the archetypes and confront the stated-belief discrepancy (finding 9).
5. Update the notebook (finding 11), then the minor items.

Items 2 to 5 are a few weeks of work on the existing code base. Item 1 is the real decision, and it is the author's: I would take option (a) if the goal is the fastest route to a defensible paper, and option (b) if the goal is the best paper.
