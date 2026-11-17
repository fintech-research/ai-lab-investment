---
title: "Consolidated review: Investing in Artificial General Intelligence"
subtitle: "Round of 2026-11-01 (four independent reports; Fable 5.2 added 2026-11-17)"
date: "2026-11-17"
geometry: margin=1in
fontsize: 11pt
colorlinks: true
---

# Inputs and verification

This report consolidates four independent referee reports of the paper at commit `4def5f6` (still identical to `origin/main` on 2026-11-17), target journal Management Science:

- **Opus** = `review_report_claude-opus-5.5.md` (Claude Opus 5.5; 1 Critical, 9 Major, 17 Minor)
- **Sol** = `review_report_gpt-6.1-sol.md` (GPT-6.1-Sol; 4 Major, 3 Minor)
- **Astra** = `review_report_gpt-6-astra.md` (GPT-6-Astra; 3 Major, 3 Minor; selective static audit, ran nothing)
- **Fable** = `review_report_claude-fable-5.2.md` (Claude Fable 5.2, run later; 1 Critical, 11 Major, 18 Minor)

What the reviewers executed: Opus, Sol and Fable each ran the full test suite (393 passed), executed the SymPy notebook, rendered the paper (Opus identified, 98 pp.; Sol and Fable blind, 111 pp.), and recomputed the headline numbers through the package API. Their recomputations agree with each other and with the prose (43% preemption discount, 26.2/4.1/5.6/22.6% dilemma losses, 0/12/41/97 bps spreads, 5.04% five-year default, duopoly losses of 38% and 17%). Sol re-ran the 18-draw sweep and the piecewise/LCP solver and reproduced Internet Appendix B and E. Fable reproduced every Internet Appendix B bias figure, regenerated all eight paper figures pixel-identically from `figures/paper.py`, and ran extra experiments of its own (C20 to C24). Opus and Fable both obtained a successful `lake build` (8572 jobs, standard axioms only); Sol and Astra were blocked by network access, which is not evidence against the proofs.

I checked every comment below against the source myself (file and line given), and for Fable's new numerical claims I re-ran the key computations (C20, C21, C24); where I could not verify, I say so. **Recommendation shared by all four: do not submit before a major revision.** None found an error in the conditional closed-form algebra. The disagreement is about severity, not substance: the shared top concern (C1) is the economic foundation of the solution convention. Fable adds a second cluster the first three missed: the credit block is largely inoperative at the model's own policy (C21, C22).

Comment numbers C1 to C19 are unchanged from the first version of this report; Fable's new comments are C20 to C26. Because the numbering is kept stable, the sections below are no longer strictly ordered by agreement; the table gives the current count.

| Comment | Reports | Comment | Reports |
|:--|:--|:--|:--|
| C1 dominated pre-switch policy | all 4 | C14 credit evaluation point | Opus, Fable |
| C2 training as a flow | all 4 | C16 narrow (A2) window | Opus, Fable (Sol) |
| C3 stale notebook | Opus, Sol, Fable | C18 length | Opus, Sol, Fable |
| C7 Prediction 3 object | Astra, Opus, Fable | C19f error metric | Opus, Fable |
| C8 archetypes unused | Opus, Fable (Sol) | C4, C5, C6 | 2 each |
| C9 implied vs stated λ | Opus, Fable | C20 to C26 | Fable only |
| C10 (A3) framing | Opus, Fable | others | 1 each |

# Comments raised by every report

## C1. At baseline, the exact model never invests before the switch, and the main text does not say so

**Raised by:** Opus (Critical, Issue 1), Sol (Major, Issue 1), Astra (Major, Issue 1), Fable (Critical, Finding 1).

**What.** `paper/_appendix.qmd:363` (Internet Appendix B) reports that with unrestricted post-switch scale the LCP returns an empty exercise region at every capacity searched: waiting for the switch is worth 1.741e-3 against 1.621e-3 for the paper's policy, so the policy delivers 93.1% of the optimum. Even within the precommitted-scale class, pure switching (1.619e-3) beats the reduced-form policy (1.615e-3). In the unrestricted belief-mismatch exercise the optimistic losses vanish (Sol reproduced 0% at beliefs 0.20 and 0.50, against 5.6% and 22.6% in the reduced model). Sol adds that the pure-power candidate does not solve the displayed switching HJB (smooth-fit coefficient about 16.5 against the forcing coefficient of about 21.1). The main text only discloses "value loss 2.6% ... 6.9% ... no pre-switch trigger in the unrestricted problem" in a table cell (`paper/_model.qmd:169`, `@tbl-domains`); the introduction, abstract and conclusion do not mention it.

**Assessment.** Correct and the most important comment in the round. I verified the numbers in `_appendix.qmd:363` and that no main-text prose outside `@tbl-domains` mentions it. The paper is honest in the appendix, and it gives two real qualifications (the sign flips at λ = 0.05 and at γ ≥ 1.9; the single irreversible lump drives the result). But a referee who reads IA-B will conclude that the trigger X\*, the L-regime preemption game, entry-time default risk and the optimistic branch of Numerical Finding 1 describe a policy the exact model does not choose. A small value loss does not defend a reversed action. I side with Opus and Fable on severity: this is critical for the *framing*, though not an algebraic error. The pessimistic branch of the dilemma (the loss ranking) survives every version, which is worth saying. Fable sharpens the point in two ways. First, the pure-power candidate pairs an H-regime ODE solution with an L-regime exercise payoff, so no consistently specified stopping problem has it as its value function; "exact statements about the model these conventions define" (`_model.qmd:185`) is true of the algebra only. Second, it shows that results the paper presents as structural (belief-invariant capacity, "optimists invest earlier") also fail in the exact benchmark (now C20).

**Suggested actions.**

1. Minimum: state in the introduction and `@sec-conventions` that at baseline the exact model prefers waiting, give the economic reason the convention is still informative (time-to-build, need for inference revenue to finance or survive, inability to scale instantly at the switch), and report the region where a finite pre-switch trigger survives.
2. Better: introduce an explicit commitment or time-to-build primitive under which pre-switch investment is optimal in the exact problem, and either calibrate there (e.g. λ near 0.05) or make the precommitted-scale piecewise solution the main single-firm benchmark.
3. Re-check the timing, preemption and default-at-entry conclusions under whichever benchmark is chosen, and describe the convention as a decision rule, not as the solution of the displayed HJB.
4. (Fable) Check whether preemption restores pre-switch investment in the exact problem. Pure waiting is not available to both duopolists, so the threat of being preempted may rescue the paper's object; if it does, the duopoly rather than the single firm is the natural benchmark, and that is itself a publishable observation. This is the cheapest test of whether action 2 is needed. Fable points out that the precommitted-scale problem already has a closed form up to one scalar root in `piecewise_option.py`, so option 2 is less work than it sounds.

## C2. "Training" is a flow, and the dynamic-reallocation discussion overstates robustness

**Raised by:** Opus (Major, Issue 8), Sol (Major, Issue 3 plus the institutional discussion in Part 2), Astra (robustness section; not numbered), Fable (Major, Finding 8).

**What.** With free one-period reallocation the pre-switch training fraction collapses to the 0.01 search bound (`@tbl-dynamic-phi`, `paper/_appendix.qmd:523`). So φ* = 0.70 exists because compute cannot be repurposed at the switch, not because training builds a capability stock. Sol notes that `paper/_appendix.qmd:535` nevertheless asserts the dilemma asymmetry "would narrow but persist", and that the stated reasoning does not support the direction: cheaper recovery for over-trainers lowers the aggressive loss and *widens* the gap, while letting under-trainers catch up lowers the conservative loss, so the net is unresolved.

**Assessment.** Correct. I verified the wording at `_appendix.qmd:535`; Sol's logic on the direction is right. The main text (`_discussion.qmd:26`) is already appropriately conditional, so the inconsistency is with the appendix paragraph. This comment and C1 share a root cause: capability is not accumulated, so waiting and buying compute after AGI is cheap. Fable adds that the paper itself says firms reallocate GPUs "on timescales of weeks" (`_appendix.qmd:469`), so the trade-off rests on a rigidity the paper concedes is counterfactual. It also notes that the motivating Amodei quotation is about buying too much compute, a margin the reduced model holds fixed (see C25).

**Suggested actions.**

1. Rewrite `_appendix.qmd:535` as a conditional conjecture that names both correction channels and drops "narrow but persist".
2. Either solve a minimal stock version (H revenue depending on cumulative φK, which the appendix already argues would restore φ*) as a robustness exercise, or reframe φ in the introduction as capacity pre-positioned for the post-AGI market, with training as the motivating interpretation. A stock version would also help C1. Fable's simplest version: H-regime revenue proportional to (φ̄K)^α, where φ̄ is the pre-switch allocation and the remainder is re-optimized after the switch. Fable expects this to make early investment optimal and to make capacity respond to beliefs.

# Comments raised by two or three of the first three reports

## C3. The SymPy notebook and symbolic module contradict the paper on (A3) ⇒ A₁ = 0

**Raised by:** Opus (Major, Issue 4), Sol (Major, Issue 2), Fable (Major for the repo, Finding 11).

**What.** `notebooks/model_derivation.ipynb:845` states that A₁ = 0 when Φ_L ≥ 1 and that the firm "never exercises in L"; line 884 prints "The simplified F_L = C * X^{beta_H} IS valid at baseline." `src/ai_lab_investment/models/symbolic_duopoly.py:23` repeats the claim. The paper (`_appendix.qmd:141`, Step 5b) explicitly says the opposite and reports A₁ ≈ −1.01e4. Sol adds that notebook §7 (`:1722`) differentiates X_D in λ through A_eff only and omits the markup channel the paper now includes (`_model.qmd:248`). Opus notes a stale admissible α range in the completeness audit. Fable lists the affected cells (18, 19, 35, 42, 53) and adds that the notebook identifies the option coefficient with Γ = 21.14, while the paper uses the smooth-fit 16.5; the notebook covers nothing in Proposition 3, φ̃ or the piecewise problem.

**Assessment.** Correct; I verified lines 845 and 884. AGENTS.md presents the notebook as backing the propositions and it ships in the public repo, so a referee may read it. Easy to fix.

**Suggested actions.**

1. Rewrite notebook §4 to match Step 5b (A₁ = 0 is a convention), add the markup derivative and the φ̃ test to §7, update the audit's α range, re-execute and commit outputs.
2. Fix the docstring in `symbolic_duopoly.py:23`.

## C4. Numerical Finding 1 misquotes the conservative loss as 23%

**Raised by:** Opus (Minor, Issue 14), Sol (Minor, Issue 5).

**What.** `paper/_valuation.qmd:25`: "the aggressive firm must believe λ = 0.50 ... to lose the 23% that the conservative firm loses at one fifth of it." The conservative loss at λ = 0.02 is 26.2%; the aggressive loss at 0.50 is 22.6%.

**Assessment.** Correct, verified in the source; both reviewers reproduced the numbers.

**Suggested action.** "... to lose 23%, still below the 26% that the conservative firm loses at one fifth of it."

## C5. Remark 3's timing statement lacks the low-λ qualification

**Raised by:** Astra (Minor, Issue 5), Sol (Minor, Issue 6).

**What.** `paper/_model.qmd:148` says higher λ raises A_eff and lowers the trigger without qualification, while the third effect in the same remark says ∂A_eff/∂λ < 0 below φ̲ (λ ≲ 0.025). Since K\* and the markup do not depend on λ, X\* ∝ 1/A_eff, so the trigger *rises* in λ there. Sol computed X\* = 0.00528, 0.00540, 0.00552 at λ = 0.005, 0.01, 0.02. The final sentence ("a firm holding a shorter AGI timeline invests earlier") inherits the problem.

**Assessment.** Correct, an internal inconsistency within one remark, and the plotted λ grid covers that region. Fable's C20 is a deeper version of the same problem: in the exact precommitted problem the trigger *rises* with λ up to about 0.15, so the timing prediction also depends on the convention.

**Suggested action.** Put the same φ*(λ) > φ̲ condition on the first effect and on the closing sentence. If C20 is accepted, also label the timing prediction a property of the convention.

## C6. The unit-normalization paragraph reverses the value scaling and mixes two operations

**Raised by:** Astra (Minor, Issue 3), Sol (Minor, Issue 7).

**What.** `paper/_calibration.qmd:38` says that with κ = c^{1/(γ−1)}, K → K/κ, X → X/κ^{1−α}, "values scale by κ". Substituting gives X K^α, δK/r and cK^γ all scaling by 1/κ. Sol adds that the "$23B" conversion is a monetary reporting unit applied to normalized values, which is a different operation from re-solving with c = 23 (which changes K).

**Assessment.** Correct; I redid the substitution and get 1/κ. It does not affect any ratio or percentage.

**Suggested actions.**

1. Change "by κ" to "by 1/κ".
2. Introduce a monetary unit m (≈ $23B here) for the dollar illustration, and keep the homogeneity transformation separate. The same edit may be needed at `_appendix.qmd:473`.

## C7. Testable Prediction 3 rests on the pre-investment option, not on installed equity

**Raised by:** Astra (Major, Issue 2), Opus (Minor, Issue 16), Fable (Minor, item 21).

**What.** `paper/_discussion.qmd:15` predicts that lab *equity* value is concave in λ, citing `@fig-lambda-option-value`, which plots a re-optimized, unexercised investment option (`figures/paper.py:213`). Installed labs cannot re-optimize K and φ after news, and levered equity includes the default option.

**Assessment.** Correct. The reports disagree on severity; I would call it Major-lite because it is a prose-to-exhibit mismatch with an easy fix. Opus's fix is the better one: for an installed firm at fixed φ, A_eff = Π_H + (Π_L − Π_H(r − μ_L))/Δ is increasing and concave in λ whenever φ > φ̲, which gives a cleaner basis and removes the λ ≲ 0.085 caveat. Fable independently reaches the same conclusion: at fixed φ > φ̲, A_eff(λ) = (a + λb)/(d + λ) is increasing and concave for every λ, with no convex range. Two reviewers agree, but I have not re-derived it myself; check it before using it.

**Suggested actions.**

1. Base the prediction on installed value at fixed (K, φ), derived in the appendix, and keep `@fig-lambda-option-value` for the option.
2. Address the levered-equity version, or limit the prediction to unlevered value.
3. Derive the "high-φ̂ firms carry the larger exposure" clause separately.

# Comments raised by one of the first three reports (some now also by Fable)

## C8. The archetypes feed no reported investment result

**Raised by:** Opus (Major, Issue 2), Fable (Major, Finding 9(i)–(ii)). Sol makes a related, milder point in Part 2.

**What.** The abstract (`paper/index.qmd:24`) says the calibration "shows how heterogeneous beliefs ... can generate cross-sectional differences in investment", and `_calibration.qmd:7` points to "cross-sectional variation analyzed in @sec-valuation". All trigger and capacity results use the baseline WACC; the leverage and WACC rows of `@tbl-firms` enter no computation; the only archetype output is the φ̂ → λ inversion. Further stale pointers are at `_appendix.qmd:441` and `:564`.

**Assessment.** Correct; I verified the abstract sentence and the `_calibration.qmd:7` pointer. This is a claim/evidence mismatch in the abstract, which referees read first. Fable adds two points: the one figure that did compare archetypes (`fig_firm_comparison`) is now slides-only, and the conclusion's "more optimistic firms train more, consistent with the archetypes" (`_conclusion.qmd:5`) is circular, because the φ̂ are assigned by the author (`_calibration.qmd:32` says as much). Fable suggests moving `@tbl-firms` to the Internet Appendix, which also helps C18.

**Suggested actions.**

1. Either compute archetype-level outputs (trigger, distance to default, dilemma loss at each implied λ and leverage, holding r at baseline), or
2. Rewrite the abstract to "maps assigned training allocations into implied beliefs" and delete the stale `@sec-valuation` pointers.
3. Delete "consistent with the archetypes" from the conclusion.

## C9. Implied λ from the archetypes is 3 to 10 times below the executive timelines used to motivate λ

**Raised by:** Opus (Major, Issue 3), Fable (Major, Finding 9(iii)).

**What.** `_calibration.qmd:7` motivates λ with Amodei (0.30 to 0.50) and Hassabis (0.10 to 0.15), but the Anthropic-like φ̂ implies λ in [0.05, 0.09] and the Google-like one [0.03, 0.05] (`@tbl-firms`). The gap is not discussed. Fable states it from the other side: at the stated executive beliefs the allocation rule gives φ\* ≈ 0.90 (λ ≈ 0.23, the 90%-in-ten-years reading of `amodei2026dwarkesh`) to 0.94 to 0.97 (λ = 0.30 to 0.50), against the "roughly 50/50" allocation reported in the same source.

**Assessment.** Plausible and interesting, and now two reviewers reproduce the bands independently by hand; I did not recompute them. Fable's framing is the stronger one: this is the most direct external evidence on the paper's central closed form, and it points the same way as the dynamic-reallocation result (C2). The gap is informative either way: it fits the static-φ upper-bound point in C2, or φ̂ is mis-assigned, or stated timelines are cheap talk.

**Suggested action.** Add a short paragraph comparing implied and stated λ and what each explanation implies.

## C10. (A3) is still presented as the condition that licenses the convention

**Raised by:** Opus (Major, Issue 5), Fable (Minor, item 23). It is a sibling of C3.

**What.** `_model.qmd:55` ("this is the condition under which the paper adopts the simplified option value"), `_appendix.qmd:76`, and `_appendix.qmd:379` ("For α > 0.67, the full two-term solution must be used"), plus the "(A3) check" row in `@tbl-baseline-results`. Step 5b says (A3) does not imply A₁ = 0.

**Assessment.** Correct; I verified all three lines. The α > 0.67 sentence in particular implies the one-term form is valid below 0.67. It also contradicts the mirror-image role (A3) plays in the IA-B explanation of C1.

**Suggested action.** Restate (A3) as an economic description (L-regime revenue alone cannot justify a standalone investment) with no role in the solution, and delete the α > 0.67 sentence. Fable notes that (A3) is implied by (A2) on the whole admissible range (α < 0.534 against α ≤ 0.67), so it could become a remark, and that (A4) is a property of the functional form rather than an assumption.

## C11. The calibration sources table renders with literal dollar signs

**Raised by:** Sol (Major for submission readiness, Issue 4).

**What.** `paper/_appendix.qmd:422` (`($\sim$50/50)`) and `:427` (`$\approx$30--40\%`), `@tbl-sources`. Pandoc does not treat a `$` followed by a digit as a closing math delimiter. Sol inspected the blind render and reports merged rows and overfull boxes of about 327, 133 and 43 pt.

**Assessment.** Correct. I confirmed the parsing with pandoc 3.13: both cells come out as literal `\$\sim\$50` and `\$\approx\$30`. I did not re-render the full PDF to confirm the extent of the row merging Sol describes. Fable reports "no table running off the page that I could detect in the text layer"; that check could not see a layout defect, and Sol looked at the rasterized page, so Sol's finding stands.

**Suggested action.** Use `\(\sim\)50/50` or "about 50/50", and `\(\approx\)30--40\%`; re-render both profiles and inspect the page.

## C12. The literature paragraph attributes the dilemma asymmetry to the recovery mechanism

**Raised by:** Astra (Major, Issue 4).

**What.** `paper/_literature.qmd:13` says the opposition between survival value and liquidation collateral "is what makes belief errors asymmetric". But the headline unlevered dilemma has no default or recovery, and Numerical Finding 1 itself (`_valuation.qmd:25`) attributes the asymmetry to the training-allocation channel, with leverage contributing tail risk.

**Assessment.** Correct: the sentence contradicts the paper's own finding. It is a one-sentence fix, so I would grade it Minor despite Astra's Major, but it matters because it sits in the contribution statement.

**Suggested action.** Say the expected-value asymmetry comes from the allocation channel, and the default/recovery opposition shapes where the *tail* risk falls.

## C13. The duopoly dilemma benchmark is not the paper's equilibrium

**Raised by:** Opus (Major, Issue 9).

**What.** `src/ai_lab_investment/models/valuation.py:846-851` computes the correct-belief duopoly benchmark as symmetric simultaneous entry at the single-firm (X\*, K\*) ("Symmetric: both invest at the same trigger, immediate duopoly"), whereas Proposition 3 has preemption at X_P and a follower at X_F ≈ 0.12. The 38% and 17% figures (`_valuation.qmd:39`, `@tbl-duopoly-dilemma`) are therefore relative to an ad hoc benchmark.

**Assessment.** Correct; I verified the code comment and logic.

**Suggested actions.** Compute the mismatch inside the preemption equilibrium, or move the result to the Internet Appendix with an explicit "non-equilibrium benchmark" label and drop the main-text sentence.

## C14. Credit spreads are quoted at an evaluation point far from the model's policy

**Raised by:** Opus (Major, Issue 7), Fable (Major, part of Finding 4; the recovery-rule part is C22).

**What.** `_appendix.qmd:630` evaluates `@fig-credit-risk` at (X, K, φ) = (0.10, 1, 0.5), about 21 × X\* and 150 × K\*. The paper's own normalization paragraph (`_calibration.qmd:38`) says such fixed-point levels carry no unit-free meaning, yet 0/12/41/97 bps appear in the main text.

**Assessment.** Correct (verified the evaluation point). Taken alone it is internally inconsistent rather than wrong, and the fix is cheap. But Fable shows why the paper may have chosen this point: at the model's own policy the spread is identically zero (C22), so moving the evaluation point will likely remove the bps numbers altogether. Do C22 first.

**Suggested action.** Evaluate at entry (X\*, K\*, φ*), or at the leader's (X_P, K_L), for each ℓ, as is already done for the dilemma default probabilities; or drop the bps levels from the main text.

## C15. Proposition 3(iv) is driven by the below-market debt subsidy

**Raised by:** Opus (Major, Issue 6).

**What.** `_model.qmd:304`: the leverage effects on K_F, X_F and X_P come from par debt at r_c < r, which `_appendix.qmd:321` quantifies as a 23% transfer of I(K) at ℓ = 0.40.

**Assessment.** Fair but partly addressed: the proposition already labels (iv) a numerical finding under a modelling convention. The residual risk is that a numbered proposition proves properties of mispriced debt. Medium priority.

**Suggested action.** Move (iv) out of the proposition into a remark, or recompute with fairly priced debt (coupon set so that D = ℓI at issuance) and report what survives.

## C16. (A2) admits only a narrow parameter window

**Raised by:** Opus (Major, Issue 10), Fable (Major, mostly disclosed, Finding 10); Sol notes the baseline's proximity to the interior-scale boundary.

**What.** Interior capacity requires r in (0.097, 0.135) and α in (0.356, 0.534); three of the four archetype WACCs and five of 18 sweep draws fall outside; capacity elasticities near the baseline are about 20 to 29.

**Assessment.** Correct as a description, and the paper does disclose the window. Whether to treat it as a design limitation is a judgment call. Fable's point moves me partway: ratios as well as levels inherit the near-degeneracy (the preemption discount is 43% at baseline, 86% under leader re-optimization, 94% at σ = 0.20), so "we report ratios, not levels" does not fully protect the trigger results. The φ results are the ones that are robust to the window.

**Suggested actions.**

1. State plainly that the capacity problem is well-posed only in this window and why (pure-power revenue against linear-plus-power cost).
2. (Fable) Organize the quantitative section around the objects that do not depend on the window or the convention (φ\*, φ̲, φ̃, the loss function in φ), and present trigger and capacity magnitudes as illustrations.
3. (Fable) Replace or supplement the one-at-a-time sweep with a joint sweep over the admissible region; a few thousand draws is cheap for the single-firm objects.

## C17. Physical default probabilities "would be lower" needs an assumption

**Raised by:** Astra (Minor, Issue 6).

**What.** `_discussion.qmd:34` ends "a certainty-equivalent convention rather than a pricing measure, so physical default probabilities would be lower."

**Assessment.** Partly right. The ordering is standard *if* the risk premium on X is positive, so physical drift exceeds the certainty-equivalent drift, with the boundary and switch intensity held fixed. The sentence needs that condition, not deletion.

**Suggested action.** "... so, with a positive risk premium on demand and the boundary held fixed, physical default probabilities would be lower."

## C18. Length relative to Management Science limits

**Raised by:** Sol (journal fit), Opus (journal fit), Fable (Major, known to the author, item 30).

**What.** The 45-page main manuscript exceeds the 32-page (1.5-spaced) cap that applies to invited revisions. Neither reviewer says it bars an initial submission.

**Assessment.** Correct and worth planning for, but secondary to C1. The caveat density the reviewers mention is the natural place to cut, once C1 settles the benchmark. Fable names candidates: `@tbl-firms` (see C8), most of Section 2.4 if the model of record changes, and Remark 2. Fable also expects a reject or reject-and-resubmit at Management Science, JFQA and Review of Finance in the current form, because the first objection is about the model, not the venue. Its fallback is the same as Opus's: JEDC, if the current structure is kept. Check `submission/README.md` for the current policy.

## C19. Minor items (all verified unless noted)

- **C19a. Musk footnote year.** `_introduction.qmd:7` says "post on X, 2025"; status id 2025124840806514916 decodes to 2026-02-21 (I verified). Fix the year. (Opus, Fable)
- **C19b. Leverage defined two ways.** "debt / total capital" in `@tbl-firms` (`_calibration.qmd:27`) and `@tbl-parameters` (`_appendix.qmd:36`), but ℓ = P/I(K) in the model (`_model.qmd:226`). Harmonize on debt over the investment outlay, which is what the model uses. (Opus, Fable)
- **C19c. Wrong cross-references.** `_discussion.qmd:22` cites `@sec-calibration` for preemption; it should be `@sec-duopoly` (I verified). Fable adds that "the solution convention discussed after Proposition 1" (`_calibration.qmd:38`, `_appendix.qmd:219`, `:471`) should point to `@sec-conventions`. (Opus, Fable)
- **C19d. Uncited Hassabis λ range** at `_calibration.qmd:7`, and no stated mapping from timelines to λ (e.g. λ = −ln(1 − p)/T). Add both. (Opus)
- **C19e. Unused bibliography entries.** `weeds2002strategic` and `sundaresan2015dynamic` are in `references.bib` but uncited (I verified no `.qmd` cites them); both are relevant. Opus also suggests Lambrecht (2001), Grenadier (1996) and Mauer and Sarkar (2005). Check metadata against Zotero before adding.
- **C19f. Headline metric mixing; the asymmetry is mostly an additive-metric result.** The introduction juxtaposes 26% at λ = 0.02 with 6% at λ = 0.20, which matches neither the additive (4%) nor the log (23%) comparison. (Opus, Minor, Issue 11.) Fable rates this Major (Finding 7). For proportional errors the losses are 26.2% against 22.6%, a ratio of 1.16, and in horizon terms (1/λ) the additive pair is a 40-year error against a 4.4-year error around a 10-year truth. Numerical Finding 1 states the caveat, but the abstract, introduction, Section 4.3 and conclusion all lead with the additive version. **My assessment: Fable is right that this deserves more than a wording fix**, because "costs far more" and "consistent with value maximization" (`_valuation.qmd:37`) rest on the metric choice. Fable also checked the mechanism: the loss is almost exactly 1 − [g(φ_b)/g(φ\*)]^β_H (26.15% against 26.19%), so "the allocation channel dominates" is right. But `_appendix.qmd:271` understates timing on the aggressive side, where timing accounts for about 1.7 of the 5.6 points. Actions: state the finding as "steep on the pessimistic side in levels of λ, nearly symmetric in logs"; put 26% against 23% next to every 26% against 6%; and soften `_valuation.qmd:37`.
- **C19g. "Fully analytical" and "for the same magnitude of mismatch" overstate** what is verified (`_model.qmd:316`; `_valuation.qmd:25`, checked across draws only at λ_true(1 ± 0.8)). Hedge. (Opus, Issues 12 and 13)
- **C19h. Proposition 2's maintained assumption** (`_appendix.qmd:151`, capacity "fixed at optimal values") is narrower than the statement, which holds at any fixed (K, φ). Align. (Opus, Issue 15; not verified by me)
- **C19i. Lean scope paragraph** (`_appendix.qmd:70`) should say that the default-boundary smooth pasting and the comparative statics of φ̲ are not formalized. (Opus, Issue 24.) Fable judges the appendix wording accurate as it stands, but notes that the Lean files formalize identities (e.g. `K_foc` does not show the right-hand side is positive under (A2)). Its warning is that "machine-checked" must never appear next to a claim the Lean files do not cover, in the cover letter or in talks. Both views are compatible: add Opus's sentence and keep Fable's rule for the cover letter.
- **C19j. Silent exception handling** in `figures/paper.py:238, 311, 434` could silently thin a figure if the single-crossing check fails, contrary to `_appendix.qmd:327`. Log and fail instead. Latent; the current curves are complete. (Opus)
- **C19k. Symbol reuse:** b, g, ρ, Δ, L, F each carry two meanings; Fable adds s_L (leader's share) next to s^L (L-regime share), and Θ(K) against b(K) for total cost. Rename where cheap. (Opus, Fable)
- **C19l. Cosmetic and expository:** the "Overinvestment" annotation overlaps the curves in `@fig-investment-dilemma` (Opus, Fable); the policy discussion is duplicated at `_discussion.qmd:22` and `_appendix.qmd:554`; the "approximately 70%" H-share at `_appendix.qmd:273` is an exact identity (H-share = φ* at the optimum). (Opus)

# New comments from Fable 5.2

## C20. Belief-invariant capacity and "optimists invest earlier" are properties of the convention

**Raised by:** Fable (Major, Finding 2; new evidence).

**What.** Proposition 1's separation ("cost and the option premium govern scale, beliefs govern allocation", `_model.qmd:116`), Remark 3's timing prediction (`_model.qmd:148`), the opening of the conclusion (`_conclusion.qmd:3`: "That separation is what makes belief errors asymmetric: a firm with the wrong timeline installs the same capacity ...") and the `@fig-investment-dilemma` caption all rest on K\* being independent of λ. Fable solved the exact precommitted-scale problem (`PiecewiseOptionModel.optimal_policy` at X_0 = X\*(0.10)/2) across beliefs. Capacity varies about ninefold and is hump-shaped (0.0021 at λ = 0.03, 0.0158 at 0.10, 0.0184 at 0.20, 0.0158 at 0.50, against 0.0067 throughout in the reduced model). The trigger *rises* with λ from 0.03 to about 0.15 (0.0021, 0.0093, 0.0094) before falling.

**Assessment.** Correct. I re-ran the piecewise solver at λ = 0.03, 0.10 and 0.20 and got exactly Fable's K, X\* and φ. The paper reports that *levels* move under the exact problem (+96%, +135%), but not that the invariance and the sign of ∂X\*/∂λ also depend on the convention. This is new relative to the other three reports and is the strongest concrete illustration of C1. Note that φ\* is identical in both problems (0.7009 at λ = 0.10), which supports Fable's broader point: the allocation results are the convention-free core.

**Suggested actions.**

1. Add both properties to `@tbl-domains` as convention-dependent, and label them so wherever they are used.
2. Drop "That separation is what makes belief errors asymmetric" from the conclusion; in the exact problem a wrong belief changes scale and coupon too.
3. Restate or drop Remark 3's timing prediction (it holds for λ ≳ 0.15 in the piecewise problem), and lead with φ\* and its comparative statics.

## C21. The tail-risk asymmetry is an operating-cost effect, not a leverage effect

**Raised by:** Fable (Major, Finding 3).

**What.** The paper attributes the tail-risk side of Dario's dilemma to leverage (`_valuation.qmd:25` "leverage's distinctive contribution is to the tail risk of overinvestment"; `_valuation.qmd:29-31, 37`; `_introduction.qmd:17`; `_literature.qmd:13`). But the aggressive-to-correct ratio of five-year default probabilities is 8.4 at ℓ = 0.01 and 7.8 at ℓ = 0.40. X_D is about 95% operating cost (δK/r is 18 times C_D/r at K\*, `_appendix.qmd:281`). The code sets X_D = 0 at exactly ℓ = 0 (`duopoly.py:424`, `if lev <= 0: return 0.0`), and the `_model.qmd:272` footnote calls the omitted unlevered abandonment option negligible. Yet the whole levered/unlevered wedge in the dilemma appears at ℓ = 0.01 (loss 21.6% against 22.6% unlevered and 21.4% at ℓ = 0.40).

**Assessment.** Correct. I re-ran `dario_dilemma_leveraged` and got Fable's numbers: default probabilities 0.48%/4.06% at ℓ = 0.01 and 0.64%/5.04% at ℓ = 0.40, and a loss of 21.58% at ℓ = 0.01. So "nearly eight times" is a statement about distance to an operating-cost shutdown boundary, and leverage is a second-order shifter. It also explains a puzzle in the text ("leverage therefore raises its measured value slightly", `_valuation.qmd:29`): that is the discontinuity at ℓ = 0. This also bears on C12: neither leverage nor recovery drives the asymmetries the contribution paragraph attributes to them.

**Suggested actions.**

1. Give the unlevered firm the same abandonment option (C_D = 0 in `@eq-default-boundary`; remove the early return) and report default probabilities across ℓ, including ℓ = 0.01.
2. Rewrite the tail-risk claims in terms of distance to an operating-cost shutdown boundary, with leverage as a shifter. Fable argues this is arguably the more interesting statement for labs whose fixed operating commitments dwarf their debt.
3. Quote tail-risk numbers at the archetypes' leverage (0.05 to 0.15) or say why 0.40 is used.

## C22. Debt is riskless at the firm's own policy because recovery is gross of operating costs

**Raised by:** Fable (Major, Finding 4).

**What.** The liquidation value Λ capitalizes inference revenue *gross* of the operating cost that triggers default (`duopoly.py:809-834`: "Gross of operating costs, following Leland (1994)"; recovery at `_model.qmd:278-282`). At (X\*, K\*, φ\*), Fable finds that the recovery cap binds at every leverage up to 0.95 ((1 − b)Λ(X_D) is 2.8 times the coupon claim at ℓ = 0.40), so D = C_D/r and the spread is identically zero. The paper notes in passing that "at this calibration the recovery cap binds" (`_appendix.qmd:281`) but does not draw the consequence. So the 12/41/97 bps spreads exist only at the off-policy point in C14. And "training raises the loss given default", the collateral half of the contribution (`_literature.qmd:13`) and of Prediction 1 (`_discussion.qmd:13`), affects no priced object at the calibrated optimum.

**Assessment.** The mechanism is right: I verified the docstring and the `_appendix.qmd:281` sentence. I did not re-run Fable's spread-at-optimum calculation, but it follows directly from the binding cap the paper itself reports. Fable's reading of Leland is also right: Leland's liquidation value is an unlevered asset value, net of operating costs. This is the most consequential new comment after C20, because it undercuts half of the "single decision variable moves the boundary and the collateral in opposite directions" contribution.

**Suggested actions.**

1. Net the operating cost of the inference fraction out of Λ (or define recovery as a fraction of the unlevered inference-only asset value), and fix the docstring's attribution to Leland.
2. Recompute spreads at the model's own policies (leader at X_P, follower at X_F\*) and report them, even if they are near zero; then resolve C14.
3. If the collateral channel still does not bind where the model operates, present Section 4.1 as an explicit off-equilibrium stress test and narrow the contribution paragraph accordingly.

## C23. The credit-spread half of Proposition 3(v) may be false on the stated range

**Raised by:** Fable (Major, Finding 5).

**What.** `_model.qmd:306` says "the credit spread at entry is correspondingly weakly increasing in λ", and `_appendix.qmd:255` says this is "verified computationally across all parameterizations tested". But `tests/test_duopoly.py:1195-1209` pins only X_P/X_D, and Fable found no code that computes the leader's spread at entry. Building it from the paper's D(X) formula, Fable finds the spread is zero up to λ ≈ 0.15 at ℓ = 0.40 and then hump-shaped, peaking near λ = 0.40 (about 33 bps). The spread is not a function of X_P/X_D alone, because β_L⁻ moves with λ (from −2.0 to −4.1) and recovery moves with φ\*(λ).

**Assessment.** Plausible, not verified. The reasoning is sound: the spread depends on β_L⁻ and recovery as well as the distance ratio, so monotonicity in X_P/X_D does not carry over. The absence of any spread-at-entry code backing "verified computationally" is itself a finding, and I confirmed it at the level of the test Fable cites. Fable flags the numbers as its own construction and asks for them to be re-derived before the text changes; I agree. The result also interacts with C22: once recovery is netted, the shape may change again.

**Suggested actions.** Add a leader-debt-at-entry function and a test. Then either drop the spread clause from Proposition 3(v) or restate it with the shape and mechanism the computation shows. Update the Proposition 3 row of `@tbl-result-taxonomy`.

## C24. In the baseline duopoly the follower essentially never enters

**Raised by:** Fable (Major, Finding 6).

**What.** With X_F\*/X_P ≈ 44 and a negative L-regime log drift (μ_L − σ²/2 = −0.021), the probability of ever reaching X_F\* is about 7.6%, about 0.03% before the switch, and the expected time after the switch is about 130 years. Yet `_model.qmd:262` attaches the Amodei scenario ("a firm committed to trillion-dollar compute purchases faces bankruptcy") to the follower's X_F\*/X_{D,F}, and `@fig-default-boundaries` is about the follower.

**Assessment.** Correct. I checked the 7.6% analytically: (1/44)^(2 × 0.021/0.0625) ≈ 0.076. In calendar time the equilibrium is a monopoly disciplined by a threat that is almost never executed. The paper already calls the scale asymmetry "not a robust prediction" (`_model.qmd:314`); converting it into time makes the point plainly.

**Suggested actions.** Report the hitting-time implication next to the scale ratio; move the Amodei sentence to the leader or drop it; consider redrawing `@fig-default-boundaries` for the leader, whose boundary is the one reached on the equilibrium path.

## C25. "Over/underinvestment" describes a belief error that leaves capacity unchanged

**Raised by:** Fable (Major as part of Finding 8(ii); Minor item 28).

**What.** In the reduced model a wrong belief changes the timing and the training allocation, not capacity, which the `@fig-investment-dilemma` caption has to say explicitly ("no point on either curve involves over- or under-building"). Still, "overinvestment" and "underinvestment" are used throughout, and the motivating Amodei quotation is about buying too much compute.

**Assessment.** Correct as terminology. It is cheap to fix and removes a mismatch a referee will notice on page one. If C20 leads to a model in which capacity responds to beliefs, the original terms become accurate again, so decide after C1.

**Suggested action.** Use "over/under-training" or "aggressive/conservative policy" in the reduced model, or say in the introduction that the commitment assumption, not capacity, carries the trade-off.

## C26. Further minor items from Fable (all verified)

- **C26a.** `_appendix.qmd:323`: "Two properties ... are used elsewhere" is followed by First, Second, Third.
- **C26b.** `_appendix.qmd:215`: the conventions are said to be "immediately before the statement of Proposition 3"; they are in Section 2.4. Stale pointer.
- **C26c.** `_appendix.qmd:133-135`: "Step 5b" follows Step 6 and the proof's end, with a sentence explaining its own placement. Rename it (e.g. "Remark on the pure-power form").
- **C26d.** Revision-history language a referee should not see: "demoted from the main text" and "the 2026 consolidation" (`_appendix.qmd:303`), "the limitation of the model most often raised" (`_appendix.qmd:519`).
- **C26e.** `_model.qmd:41`: `@deepseek2025r1` (a Nature paper on reinforcement learning for reasoning) is cited for hardware obsolescence. It does not support that; cite a source on GPU depreciation or drop it.
- **C26f.** "about 4.6 to about 2.2" (`_valuation.qmd:39`) against "about 4× ... to about 2×" (`_appendix.qmd:546`). Use one.
- **C26g.** `_discussion.qmd:11` announces "four cross-sectional predictions", one of which (prediction 2) is then called a conjecture. Say three predictions and one conjecture.
- **C26h.** φ̂ is "not an observed quantity" in the calibration (`_calibration.qmd:30`) but "a firm's observed training fraction" in the predictions (`_discussion.qmd:11`). Use "assigned" for the calibration and different wording for the empirical object.
- **C26i.** `@tbl-parameters` labels r and r_c "Inferred = backed out from observable proxies", while `_calibration.qmd:9` says r is chosen. Use "Chosen".

# Contradictions between reports

- **Severity of C1.** Opus and Fable call it Critical; Sol and Astra call it Major and say no Critical issue exists. All four describe the same facts. I side with Critical because it governs how every L-regime result is framed, and C20 shows the effect reaches the paper's headline structural claims.
- **Lean.** Opus and Fable report a successful build; Sol and Astra could not build (network) and correctly do not count that as a failure. The successful builds stand.
- **Robustness of the dilemma.** Opus reads the unrestricted re-checks as a strength (the pessimism ranking survives); Sol, Astra and Fable read them as exposing fragility (the optimistic branch disappears, and in logs the asymmetry nearly vanishes, C19f). Both readings are right about different things; the paper should say both (C1, action 1).
- **Severity of the error-metric point (C19f).** Opus: Minor; Fable: Major. I side with Fable (see C19f).
- **Table IA5 rendering (C11).** Sol saw a corrupted table on the rendered page; Fable detected nothing in the text layer. Sol's visual check and my pandoc test win.
- **What leverage does.** The original three reports (and the paper) accept that leverage concentrates tail risk on the aggressive side; Fable shows the effect is present at ℓ = 0.01 (C21). I verified Fable's numbers, so on this point Fable is right and the others missed it.

# Suggested priority

1. **Before anything else:** C1, with C2 and C20 (same root cause). Decide the model of record. Fable's two options are the precommitted-scale piecewise problem (fastest route to a defensible paper) or a capability stock (the better paper). The duopoly check in C1 action 4 is the cheapest first step.
2. **Repair the credit block:** C22 then C14, C21, C23. Roughly a few weeks of work on the existing code, independent of the choice in step 1.
3. **Quick, mechanical fixes:** C3, C4, C5, C6, C10, C11, C12, C17, C19a to C19e, C26.
4. **Moderate work:** C7, C8, C9, C13, C15, C19f, C24, C25.
5. **After C1 settles:** C16, C18, the remaining C19 items.
