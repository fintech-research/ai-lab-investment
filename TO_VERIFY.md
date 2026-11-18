# TO_VERIFY

Items from the prose-review pass (`reports/prose_review_claude.md`, branch
`prose-review-fixes`) that need a human check. Each was raised by an editing
agent that could not resolve it without recomputing a number, opening an
exhibit, or consulting a source. Delete an entry once verified.

## Sources and citations

- [ ] **\$121B 2025 hyperscaler bond issuance** (`_calibration.qmd`, opening
  paragraph). No source exists anywhere in the repo; Internet Appendix C covers
  only the xAI and OpenAI debt. Currently attributed as "Press reports place
  ...". Needs a footnote or removal.
- [ ] **Hassabis timeline range** (`_calibration.qmd`, Demand Process). The
  $\lambda \approx 0.10$–$0.15$ range attributed to Hassabis is still uncited
  while Amodei is cited. Find the source in Zotero or drop the comparison.
- [ ] **Microsoft CFO and Jensen Huang statements** and the ">40% of AI revenue
  is inference by late 2025" figure (`_appendix.qmd`, Internet Appendix C,
  $\hat{\phi}$ evidence block). Now marked as trade-press reports rather than
  filings, but still lack a source, date, and venue. "AI revenue" is also
  undefined (whose, measured how).
- [ ] **xAI CapEx row in `@tbl-sources`**. Labelled "press reports", but the
  body says CapEx is not separately disclosed for that archetype. Reconcile.
- [ ] **Four cite keys dropped from the bibliography.** The literature review's
  catalogue footnotes were cut, so `@bloom2009impact`, `@jovanovic2005general`,
  `@katz1986technology`, and `@farrell1986installed` are no longer cited
  anywhere and have dropped out of the reference list. The entries remain in
  `references.bib`. Confirm you are happy to lose them. (`@bloom2020ideas` is a
  different key and is still cited.)

## Numbers that need an exhibit check

- [ ] **Cooperative/cartel benchmark** (`_discussion.qmd`, Welfare and
  Overinvestment). The claim that industry capacity may exceed the cooperative
  level has no exhibit; grep finds "cartel"/"cooperative" only in that section.
  It is now written as an open question. If a cartel-capacity computation
  exists in the code but is unexhibited, replace the sentence with the actual
  comparison.
- [ ] **`@tbl-duopoly-dilemma` leverage level.** The added note does not state
  $\ell$, because the text never does. If the exercise is the $\ell = 0$ case,
  add it.
- [ ] **26.2% / 5.6% versus 26% / 6%.** Both roundings are now in use:
  `_valuation.qmd` quotes 26.2/5.6 where the 4.7 loss ratio needs that
  precision, and 26/6 elsewhere. Consistent, but confirm both trace to the same
  exhibit.
- [ ] **Rounding of 2.64% to 2.6%** (`_appendix.qmd`, Internet Appendix B) and
  the 97.4%/2.6% pair in the same sentence. Confirm the exported numbers
  support one decimal.
- [ ] **Cost-scale invariance justification** (`_appendix.qmd`, Internet
  Appendix E). The claim that the four sweep objects are invariant to $\delta$
  and $c$ is now attributed to homogeneity of the value functions in the cost
  scale. Confirm this is the mechanism in `robustness.py`.
- [ ] **`@tbl-elasticities` "$\approx 0$" rule.** The new note says those
  entries round to zero at the displayed precision. Confirm that is what the
  generator does.
- [ ] **`fig_growth_decomposition` band order.** The new non-colour cue asserts
  assets-in-place is the lower band and the capacity gap the upper band.
  Confirm against the figure.
- [ ] **Caption procedural numbers in `_model.qmd`** (60-point $\lambda$ grid on
  $[0.01, 0.80]$; 40 leverage levels on $[0.05, 0.65]$; 30 $\sigma$ points).
  Read from `figures/paper.py` and will drift if the generators change.

## Editorial calls to confirm

- [ ] **43% preemption discount in the introduction.** Now qualified as "at
  baseline volatility, and conditional on the convention that the leader
  installs the monopoly-phase optimal scale". The alternative is to drop the
  number from the introduction and keep only the sign. Update (#178): the number no longer describes the model of record. The single firm has no pre-switch trigger at baseline, so there is no discount to quote; against the precommitted-scale single firm the rent-equalization trigger is 7% lower. Left for #187.
- [ ] **`fig-growth-decomposition` label versus prose.** The prose now
  standardizes on "the scale-gap index $g$", and Internet Appendix G insists the
  exhibit is *not* a growth-option decomposition, but the Quarto label and the
  generated file are still `fig_growth_decomposition`. Renaming needs a
  `paper.py` edit plus a figure regeneration.
## Codex review round (2026-09-07), umbrella #135

Author-only checks raised while verifying `reports/review_report_codex_20260907.md`. Each is also referenced from the sub-issue in parentheses.

- [ ] **\$660--690B 2026 spending aggregate** (`_introduction.qmd`, opening paragraph). The footnote cites only Amazon, Alphabet, and Microsoft guidance, which cannot sum to a "laboratories and their compute partners" total. State the aggregation or cite the source that made it. (#144)
- [ ] **Executive quotations in the introduction**: Pichai (Alphabet Q2 2024 call), Huang (GTC 2025, "easily 100x"), Musk (year corrected to 2026 in #172; see the November 2026 section below), LeCun/PYMNTS wording, Amodei/Dwarkesh wording and ellipsis, Stargate figures. Check exact wording and add URLs where missing. (#144)
- [ ] **OpenAI \$3.7B/\$12.5B revenue** (`_appendix.qmd`, Internet Appendix C). The cited openai.com post gives ARR of \$2B/\$6B/\$20B+, not these figures. Supply the press source or switch to the ARR series. (#144)
- [ ] **Management Science reviewer count.** `submission/README.md` says five suggested reviewers; web summaries of the current guidelines say six and three AEs. INFORMS pages returned 403 to automated fetches; confirm on the portal. (#148)
- [ ] **Decision: reframing after the C2 envelope result.** #152 reproduced the finding independently (no finite pre-switch trigger at baseline in the unrestricted problem; 6.9% policy loss) and disclosed it in Internet Appendix B and the conventions paragraph. Still open: whether to reframe the A₁ = 0 discussion and the introduction around the fact that the L-regime trigger is a feature of the convention at baseline, or leave the disclosure as is. (#136, #149)
- [ ] **Decision: cover letter.** The verification paragraph was corrected and the abstract added in #148; the AI-upload invitation and the AI-genesis paragraph were kept per the July decision, though Codex flags both again (the invitation may put reviewers at odds with the journal's rule against uploading manuscripts). Decide whether to keep them. (#148)

## Final prose pass (2026-09-10), #150

- [ ] **Length decision.** After the #149 consolidation and the #150 prose pass the blind manuscript was 47 pages at 1.5 spacing (e-companion 70); removing Internet Appendix I and its references brought it to 45 (e-companion 66). Management Science caps *invited revisions* at 32 pages; an initial submission has no hard cap. Decide whether to submit at 47 or cut a further ~13 pages (candidates, in order: demote the `fig-competition-effect` discussion and the leader-scale asymmetry paragraph to Internet Appendix B; drop Internet Appendix G's scale-gap index from the main-text pointers; compress the preemption-equilibrium derivation to the proposition plus one paragraph). (#150)
- [ ] **A sentence introduced during consolidation** to confirm you are happy with: the limitations list's "Training is a flow allocation of installed capacity rather than an accumulated stock of capability, so there is no learning curve" (`_discussion.qmd`). (#149)
- [ ] **Symbol renames** from the collision cleanup, in case they clash with the slides or the Lean README: discriminant $D 	o \mathcal{R}$ (Proposition 2 statement and proof), piecewise coefficients $D_1, D_2, D_w 	o G_1, G_2, G_w$, debt face value $D_0 	o P$, forced-ODE coefficient $C 	o \Gamma$ (label `eq-particular-C` unchanged). (#150)
- [ ] **Final read of the rendered blind PDF** page by page before upload: `just render-blind`, then `paper/_output/ai_lab_investment_blind.pdf` and the e-companion. The automated checks cover unresolved references, metadata parity, and the house conventions; they do not cover figure placement or page breaks. (#150)

## Review round 2026-11-01, mechanical fixes (#172, umbrella #171)

- [ ] **Musk "AGI in 2026" post** (`_introduction.qmd`, footnote). The status ID `2025124840806514916` decodes (X snowflake timestamp) to 2026-02-21 08:26 UTC, so the footnote year is now 2026. Open <https://x.com/elonmusk/status/2025124840806514916> and confirm the date and that the post says "AGI in 2026". (#172)
- [ ] **Literature citations added without Zotero records.** `@weeds2002strategic` (patent race in a real-options duopoly; "competition can delay rather than hasten investment") and `@sundaresan2015dynamic` (cited among the investment-plus-default papers with homogeneous capital) were already in `references.bib` but are not in the Zotero library, so neither the bib metadata nor the one-line characterization was checked against the paper. Add both to Zotero and confirm. `@mauer2005real` was added from the Zotero record. (#172)
- [ ] **Other suggested references not in Zotero.** The review also suggested Lambrecht (2001) and Grenadier (1996); neither is in the Zotero library, so neither was added (Grenadier 2002, already cited, is the Zotero Grenadier entry). Add them to Zotero if wanted and cite in `_literature.qmd`. (#172)
- [ ] **GPU depreciation source for the `_model.qmd` operating-cost footnote.** `@deepseek2025r1` did not support the hardware-obsolescence pointer and was dropped from that footnote (the entry stays, cited in the conclusion); Zotero has no GPU-depreciation source. The 20--33\% per year / 3--5 year useful-life figures in Internet Appendix C remain unsourced. (#172)

## Capability-stock prototype (issue #174, `capability_stock.py`)

Derivations done by the implementing agent and checked only numerically (two independent LCP solvers, direct integration); none is in the Lean package or the SymPy notebook. Delete an entry once verified.

- [ ] **Smooth-pasting condition with a forcing term.** The module docstring states that the trigger solves $(\beta_L^+ - 1) g^* K^\alpha X - \beta_L^+[\Theta(K) + f] = (2/\sigma^2) X^{\beta_L^-} \int_0^X s^{-\beta_L^- - 1} \lambda\theta F_H(\vartheta s)\,ds$ with $X$ the demand at which $K$ is statically optimal. Confirm the derivation (Green's function of the L-regime operator, then $xS' - \beta_L^+ S = -(2/\sigma^2) x^{\beta_L^-} I^-(x)$).
- [ ] **Head-start factor of the accumulating stock.** $m = [1 - x^{1+\alpha}]/(1 - x)$, $x = (r - \mu_H)/(r - \mu_L + \lambda)$ (`accumulating_stock_premium`), and the normalization of $\zeta$ that keeps the entrant's coefficient at $A_H$. The normalization is a modelling choice, not a result.
- [ ] **Regime classification.** "never" if and only if $\theta\,[\lambda/|Q_L(e)|]\,(\vartheta A_H/g^*)^{e} \ge 1$ at $e = \gamma/(\gamma - \alpha)$; "immediate" from the same ratio at $e = 1/(1-\alpha)$ when the upper bound of (A2) fails. Derived from the growth rates of the two envelopes and confirmed by the LCP at the cases in the tests, not proved.
- [ ] **Illustrative values.** $\theta \in \{0.5, 0.8\}$, $\kappa \in \{0.2, 0.5\}$ and $f = 0.002$ are chosen for illustration (the last to put $K^*$ near the reduced model's $0.0067$). None is calibrated.

## Decision gate for the November 2026 revision (issue #175)

- **Model of record: decided.** Recorded on #175 (comment of 2026-11-17): the exact piecewise primitives, with the preemption game and a re-optimizing leader as the benchmark and the single firm as the monopoly case; baseline unchanged; "over/underinvestment" kept; journal ladder unchanged until #190. Items 2 to 5 were read as accepted defaults; say so on #175 if any should differ. (#175)
- [ ] **Formulation of the exact preemption game** (`preemption_exact.py`, #173). Read critically in #178: the claims, the Green's-function solution and the follower's and leader's problems were re-read line by line, and the levered extension was checked against independent finite-difference solves; no error was found in the valuation. One gap in the equilibrium reasoning was found and is recorded under issue #178 below (the trigger of a firm that knows it will lead lies below X_P). Still not re-derived independently by a person; existence of X_P is established on a finite demand scan with no uniqueness or subgame-perfection argument. (#173, #178)

## Single-firm core under the model of record (issue #176)

- [ ] **What `optimal_trigger_capacity_phi()` returns.** It returns the precommitted-scale (X*, K*, φ*) = (0.00926, 0.01578, 0.7009), the policy of Proposition 1(iii), although with scale chosen at the switch the baseline monopolist does not invest before the switch (`solve().invests_before_switch` is False). This follows item 4 of the #175 decision ("(X*, K*) from the two-region system"). Confirm that the precommitted-scale policy, and not "no trigger", is what Proposition 1 and the baseline table should report. (#176)
- [ ] **The value comparison in the #176 brief does not hold as worded.** "Pure switching weakly dominates the precommitted-scale optimum, about 1.619e-3 against 1.615e-3" compares pure switching (precommitted scale) with the *pure-power policy*, not with the precommitted-scale optimum, which is worth 1.659e-3 and beats it. The monopolist waits only once scale is chosen at the switch (waiting 1.741e-3; following the precommitted-scale policy there 1.703e-3). The paper text and `TestSingleFirmSolution::test_value_ranking_at_baseline` state it this way. (#176)
- [ ] **Step 7 of the Proof of Proposition 1** (`_appendix.qmd`). New derivation: the value below the trigger is S(X) + [P − S] (X/X̄)^{β_L⁺}, the first-order conditions in X̄ and K are smooth pasting and the scale condition `eq-scale-foc`, and A_1 = A_w + [P − S] X̄^{−β_L⁺}, G_1 = [P − S] X̄^{−β_L⁺}, G_2 = G_w. Checked numerically only (boundary conditions, Brennan--Schwartz boundary, two other solvers); not in the Lean package or the notebook (#185, #186). Uniqueness of the capacity maximum is a grid finding. (#176)
- [ ] **Waiting margin as the existence criterion** (`eq-waiting-margin`, main text). Same status as the "Regime classification" entry above: derived from growth rates and confirmed by the LCP, stated in the paper as not proved. The claim that no trigger reappears at high λ is checked up to λ = 20 only (the margin tends to one from above). (#176)
- [ ] **Reviewer's belief table (C20).** K* = 0.0158, 0.0184, 0.0158 at λ = 0.10, 0.20, 0.50 reproduce. The entry K* = 0.0021 at λ = 0.03 reproduces only as the best immediate investment at the evaluation demand X_0 = X*(0.10)/2, which lies above that belief's trigger; the demand-free optimum is K* = 0.00017 at X* = 0.00044, and `tbl-beliefs` reports that. The trigger peaks at λ ≈ 0.127, not 0.15 (0.15 is the grid maximum). Confirm the table as reported. (#176)
- [ ] **Interim notation.** `@sec-conventions` says that X* and K* in the calibration and valuation sections denote the pure-power policy (X^pp, K^pp); since #178 the duopoly section's X_P, K_L, φ_L, X_F*, K_F denote the exact equilibrium. The sentence, the matching `tbl-notation` row and the "Baseline policy" block of Internet Appendix C are temporary and should go as #179 to #183 re-solve those sections; the abstract, introduction and conclusion still describe the pure-power results (#187). (#176, #178)
- [ ] **(A3) implied by (A2).** Stated only "at the baseline values of the other parameters" (α < 0.534 against α ≤ 0.67). It is not a general implication: it requires γ(1 − 1/β_H) ≤ 1 − 1/β_L⁺, which fails for large γ (for example γ = 2 at baseline). (#176)
- [ ] **`fig-lambda-option-value`** now plots the exact value (solid) with the pure-power approximation dashed; the slides pick up the PNG by symlink. Check the legend placement and that the caption's two thresholds (about 0.04 and 0.073) read correctly. (#176)

## Credit primitives (issue #177)

- [ ] **Choice of recovery rule.** The issue offered two definitions (net the operating cost of the inference fraction out of Λ, or (1 − b) times the unlevered inference-only asset value floored at zero). Implemented as one rule with three parts (`DuopolyModel.recovery_value`, `eq-recovery`): Λ net of δ(1 − φ)K/r, floored at zero, capped at the unlevered asset value U(X_D) of the firm, then at C_D/r. Two choices inside it are mine and change the numbers. (a) The cost is capitalized at r, the same perpetual commitment the firm carries, so that V = Λ + training business exactly; a buyer who stops paying at the switch would use r + λ (`recovery_rule="net_until_switch"`), which makes the inference business worth 0.74 of the claim at ℓ = 0.40 before the cap. (b) The cap at U(X_D) is not in the issue; without it the r + λ variant would leave debt default-free below ℓ ≈ 0.3, and with it recovery is 6% of the claim at ℓ = 0.40. Under the default rule recovery is zero at both single-firm policies at every leverage, so the "training raises the loss given default" half of the collateral argument has no bite there. Confirm the rule, or pick the variant. (#177)
- [ ] **Reading of Leland (1994).** The docstring and Internet Appendix A now say that in Leland the bankruptcy payoff is (1 − α) times the unlevered asset value at the boundary and that, with an operating cost, an asset value is net of it. Leland's own model has no operating cost (V is the value of the firm's assets, a primitive), so "net of operating costs" is my inference from his definition, in agreement with the consolidated report (C22), and not a quotation. Check against the paper. (#177)
- [ ] **Uniqueness of X_P.** Settled in #178 as follows; confirm. In the model of record neither existence nor uniqueness of X_P is analytical: existence is the first up-crossing on a demand scan and uniqueness is not claimed (Proposition 3(iii), its proof, `tbl-domains`, `tbl-result-taxonomy`). The strict-concavity argument, and the Lean lemmas `unique_crossing` and the intermediate-value existence lemma, apply only to the nested pure-power game without the shutdown option, and the Lean scope paragraph in Internet Appendix A now says so; `lean/README.md` still needs the same qualification. (#177, #178, #186)
- [ ] **Spread at ℓ = 0.** `credit_spread(0)` now returns the limit as ℓ → 0 (evaluated at ℓ = 1e-6), which is positive (17 bps at the precommitted-scale policy), where it returned zero. The alternative is "undefined without debt". (#177)
- [ ] **Policies ignore the shutdown and default options.** The single-firm policies (both the model of record and the pure-power approximation) and the nested game's follower trigger are computed on the installed value without the shutdown option, and the option enters only when the claims are valued. The single-firm model of record (`SingleFirmModel`, `piecewise_option.py`) was not changed. In the duopoly model of record (#178) this is no longer the case: leader and follower choose their policies on the claim with the option to stop (it lowers X_P by 4.3%, from 0.00896 to 0.00857, and moves the follower's post-switch policy by 0.2%). So the single firm and the duopoly are now solved on slightly different claims; decide in #179 or #180 whether the single-firm policies should be re-solved on the claim with the option. (#177, #178)
- [ ] **Stale numbers left in sections this issue does not own** (listed with old and new values in the PR body and the #177 comment): the unlevered preemption trigger and discount (Section 2.5, Internet Appendix B and E, introduction), the levered dilemma losses and the "recovery cap binds" sentence (Internet Appendix A, Dario's dilemma; Section 5), and `fig-credit-risk`'s evaluation point. The three regenerated figures (`fig_credit_risk`, `fig_competition_effect`, `fig_investment_dilemma`) already show the new values. (#179, #180, #182; the #178 items are done)


## Duopoly under the model of record (issue #178)

- [ ] **Which trigger is the benchmark: X_P or X_L.** The decision on #175 makes the rent-equalization trigger X_P of the game with a re-optimizing leader the benchmark (0.0086 at baseline with the option to stop). Reading the game critically I found that X_P is not established as the date of first investment. The trigger X_L that a firm would choose if it knew its rival would follow maximizes h(X) = [L*(X) − W(X)] X^{−β_L⁺}, W the mutual-waiting value, and it lies below X_P at every arrival rate on the grid: 0.0034 at baseline (0.40 X_P, with K_L = 0.0042), 0.99 X_P at λ = 0.50. Between X_L and X_P the follower is the better-off role (by 10% at X_L at baseline) and yet each firm prefers investing to waiting for X_P, so the payoffs are those of a war of attrition and not of a race to be first. X_L is the first investment when roles are assigned, X_P an upper bound; the symmetric (mixed) equilibrium is not solved. The paper now says this (Proposition 3(iii), `fig-competition-effect`, `tbl-duopoly-beliefs`) and keeps X_P as the trigger at which the leader's scale, the credit objects and the hitting times are evaluated. Decide whether the headline objects should instead be evaluated at X_L, and whether "preemption" is still the right word for the title of the section and for #187: the pull-forward result survives either way, but its mechanism is the race after the switch (waiting leads to a post-switch game in which rents are competed away), not a race before it. The comparison rests on W, which prices the post-switch game by rent equalization, with the scale of the post-switch leader chosen at entry and without the option to stop. I checked that game for the same issue at baseline and it has the standard order (the assigned leader's post-switch trigger is about four times the post-switch rent-equalization trigger, and leading is the better role between them), so the game after the switch is a race; the check was not repeated at other arrival rates. (`preemption_levered.leader_assigned_entry`, `tests/test_duopoly_exact.py::TestOrderOfMoves`) (#178, #187)
- [ ] **Benchmark choices that are mine.** (a) Post-switch scale: the benchmark lets a follower that has not invested when the switch arrives choose its scale then (`scale="envelope"`), consistent with the single-firm model of record in which the firm waits; the precommitted variant gives X_P = 0.0084 instead of 0.0086 and a follower that would also enter before the switch at X ≈ 0.31. (b) Option to stop: the benchmark includes it at ℓ = 0, so that the unlevered game is the limit of the levered one (C21); the diagnostic of #173 did not (X_P = 0.0090). Confirm both. (#178)
- [ ] **Conventions of the game with credit** (`preemption_levered.py` docstring, `tbl-domains`). (a) A firm values its claim as if the rival's capacity stayed in the contest after the rival stops or defaults; the follower's policies therefore do not depend on the leader's coupon. (b) After the switch the inference business has no revenue, so `eq-recovery` gives zero recovery in regime H; this is my extension of the #177 rule, which was stated for regime L. In every cell solved recovery is zero in regime L as well. (c) The coupon is fixed at issuance and the follower's fair coupon is set at the demand at which it enters. (d) The follower's pre-switch entry candidate is located on the claim without the option to stop and polished on the exact claim. None of these uses the unconditional-A_eff convention; (a) is the one with economic content. (#178)
- [ ] **What the game does not establish.** Uniqueness of X_P (with the leader's scale held fixed the gap crosses twice); subgame perfection; the second Huisman--Kort condition (leading at X_P beats simultaneous investment), which is not checked because simultaneous installation is not priced; the value of waiting below X_P, which uses the mutual-waiting value above. Existence is on a 25-point log scan over four decades of demand. (#178)
- [ ] **Proposition 3 as restated.** (i) is analytical only for the follower's post-switch problem without the option to stop (the option moves K_F and X_F* by 0.2%); (ii) keeps the factorization as a critical-point statement at a common allocation and reports the leader's gap from φ* numerically (1.9% at baseline, 19% at λ = 0.03, 0.2% at 0.50); (iii) to (v) are numerical findings. The former clause (iv) on leverage is Remark 4: it holds under par debt and not under fairly priced debt, except for the boundary and the distance to default. The former clause (v) on the spread is restated with the computed U-shape. Confirm the split between proposition, remark and numerical finding, given the rule in `paper/AGENTS.md` against promoting numerical findings. (#178)
- [ ] **Amodei sentence and `fig-default-boundaries`.** The sentence now sits with the leader in the scale-asymmetry paragraph and says that at baseline the shortfall required is large, not modest (the leader enters at 5.9 times its boundary, 5.3 at ℓ = 0.40 under par debt, and reaches it before the switch with probability 7% to 9%). The alternative offered by the issue was to drop it. `fig-default-boundaries` is still drawn in the nested pure-power game and its paragraph says so; redrawing it in the exact game is #179. (#178, #179)
- [ ] **Cached equilibria.** The duopoly numbers in the paper are read from `src/ai_lab_investment/models/duopoly_equilibria.json` (45 cells: one to two minutes each at zero leverage and under par debt, five to eight under fair debt, about half an hour where the follower also enters before the switch, that is λ ≤ 0.05 and the precommitted variant). The two fair-debt cells at λ = 0.05 are solved on a five-point scan between 0.3 and 1.5 X_H* instead of 25 points over four decades, because the full scan would take about five hours each; they bracket the crossing found without debt and do not show that it is the first one over the wider range (`SCAN_OVERRIDES`; every record carries its scan). The default test suite checks every cached cell against rent equalization and local optimality of the leader's policy without re-solving; `just test-slow` re-solves three baseline cells and `just duopoly-grid` rewrites the file. `just test` now deselects tests marked `slow`. Confirm that a cache checked this way is acceptable for the replication package (#184). (#178)
