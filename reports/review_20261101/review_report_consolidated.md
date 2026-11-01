---
title: "Consolidated review: Investing in Artificial General Intelligence"
subtitle: "Round of 2026-11-01 (three independent reports)"
date: "2026-11-01"
geometry: margin=1in
fontsize: 11pt
colorlinks: true
---

# Inputs and verification

This report consolidates three independent referee reports written in parallel on commit `4def5f6` (0 ahead, 0 behind `origin/main`), target journal Management Science:

- **Opus** = `review_report_claude-opus-5.5.md` (Claude Opus 5.5; 1 Critical, 9 Major, 17 Minor)
- **Sol** = `review_report_gpt-6.1-sol.md` (GPT-6.1-Sol; 4 Major, 3 Minor)
- **Astra** = `review_report_gpt-6-astra.md` (GPT-6-Astra; 3 Major, 3 Minor; selective static audit, ran nothing)

What the reviewers executed: Opus and Sol both ran the full test suite (393 passed), executed the SymPy notebook, rendered the paper (Opus identified, 98 pp.; Sol blind, 111 pp.), and recomputed the headline numbers through the package API. Their recomputations agree with each other and with the prose (43% preemption discount, 26.2/4.1/5.6/22.6% dilemma losses, 0/12/41/97 bps spreads, 5.04% five-year default, duopoly losses of 38% and 17%). Sol also re-ran the 18-draw sweep and the piecewise/LCP solver and reproduced Internet Appendix B and E. Only Opus obtained a successful `lake build` (standard axioms only); Sol and Astra were blocked by network access, which is not evidence against the proofs.

I checked every comment below against the source myself (file and line given); where I could not, I say so. **Recommendation shared by all three: major revision before submission.** None found an error in the conditional closed-form algebra. The disagreement is about severity, not substance: the shared top concern (C1) is the economic foundation of the solution convention.

# Comments raised by all three reports

## C1. At baseline, the exact model never invests before the switch, and the main text does not say so

**Raised by:** Opus (Critical, Issue 1), Sol (Major, Issue 1), Astra (Major, Issue 1).

**What.** `paper/_appendix.qmd:363` (Internet Appendix B) reports that with unrestricted post-switch scale the LCP returns an empty exercise region at every capacity searched: waiting for the switch is worth 1.741e-3 against 1.621e-3 for the paper's policy, so the policy delivers 93.1% of the optimum. Even within the precommitted-scale class, pure switching (1.619e-3) beats the reduced-form policy (1.615e-3). In the unrestricted belief-mismatch exercise the optimistic losses vanish (Sol reproduced 0% at beliefs 0.20 and 0.50, against 5.6% and 22.6% in the reduced model). Sol adds that the pure-power candidate does not solve the displayed switching HJB (smooth-fit coefficient about 16.5 against the forcing coefficient of about 21.1). The main text only discloses "value loss 2.6% ... 6.9% ... no pre-switch trigger in the unrestricted problem" in a table cell (`paper/_model.qmd:169`, `@tbl-domains`); the introduction, abstract and conclusion do not mention it.

**Assessment.** Correct and the most important comment in the round. I verified the numbers in `_appendix.qmd:363` and that no main-text prose outside `@tbl-domains` mentions it. The paper is honest in the appendix, and it gives two real qualifications (the sign flips at λ = 0.05 and at γ ≥ 1.9; the single irreversible lump drives the result). But a referee who reads IA-B will conclude that the trigger X\*, the L-regime preemption game, entry-time default risk and the optimistic branch of Numerical Finding 1 describe a policy the exact model does not choose. A small value loss does not defend a reversed action. I side with Opus on severity: this is critical for the *framing*, though not an algebraic error. The pessimistic branch of the dilemma (the loss ranking) survives every version, which is worth saying.

**Suggested actions.**

1. Minimum: state in the introduction and `@sec-conventions` that at baseline the exact model prefers waiting, give the economic reason the convention is still informative (time-to-build, need for inference revenue to finance or survive, inability to scale instantly at the switch), and report the region where a finite pre-switch trigger survives.
2. Better: introduce an explicit commitment or time-to-build primitive under which pre-switch investment is optimal in the exact problem, and either calibrate there (e.g. λ near 0.05) or make the precommitted-scale piecewise solution the main single-firm benchmark.
3. Re-check the timing, preemption and default-at-entry conclusions under whichever benchmark is chosen, and describe the convention as a decision rule, not as the solution of the displayed HJB.

## C2. "Training" is a flow, and the dynamic-reallocation discussion overstates robustness

**Raised by:** Opus (Major, Issue 8), Sol (Major, Issue 3 plus the institutional discussion in Part 2), Astra (robustness section; not numbered).

**What.** With free one-period reallocation the pre-switch training fraction collapses to the 0.01 search bound (`@tbl-dynamic-phi`, `paper/_appendix.qmd:523`). So φ* = 0.70 exists because compute cannot be repurposed at the switch, not because training builds a capability stock. Sol notes that `paper/_appendix.qmd:535` nevertheless asserts the dilemma asymmetry "would narrow but persist", and that the stated reasoning does not support the direction: cheaper recovery for over-trainers lowers the aggressive loss and *widens* the gap, while letting under-trainers catch up lowers the conservative loss, so the net is unresolved.

**Assessment.** Correct. I verified the wording at `_appendix.qmd:535`; Sol's logic on the direction is right. The main text (`_discussion.qmd:26`) is already appropriately conditional, so the inconsistency is with the appendix paragraph. This comment and C1 share a root cause: capability is not accumulated, so waiting and buying compute after AGI is cheap.

**Suggested actions.**

1. Rewrite `_appendix.qmd:535` as a conditional conjecture that names both correction channels and drops "narrow but persist".
2. Either solve a minimal stock version (H revenue depending on cumulative φK, which the appendix already argues would restore φ*) as a robustness exercise, or reframe φ in the introduction as capacity pre-positioned for the post-AGI market, with training as the motivating interpretation. A stock version would also help C1.

# Comments raised by two reports

## C3. The SymPy notebook and symbolic module contradict the paper on (A3) ⇒ A₁ = 0

**Raised by:** Opus (Major, Issue 4), Sol (Major, Issue 2).

**What.** `notebooks/model_derivation.ipynb:845` states that A₁ = 0 when Φ_L ≥ 1 and that the firm "never exercises in L"; line 884 prints "The simplified F_L = C * X^{beta_H} IS valid at baseline." `src/ai_lab_investment/models/symbolic_duopoly.py:23` repeats the claim. The paper (`_appendix.qmd:141`, Step 5b) explicitly says the opposite and reports A₁ ≈ −1.01e4. Sol adds that notebook §7 (`:1722`) differentiates X_D in λ through A_eff only and omits the markup channel the paper now includes (`_model.qmd:248`). Opus notes a stale admissible α range in the completeness audit.

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

**Assessment.** Correct, an internal inconsistency within one remark, and the plotted λ grid covers that region.

**Suggested action.** Put the same φ*(λ) > φ̲ condition on the first effect and on the closing sentence.

## C6. The unit-normalization paragraph reverses the value scaling and mixes two operations

**Raised by:** Astra (Minor, Issue 3), Sol (Minor, Issue 7).

**What.** `paper/_calibration.qmd:38` says that with κ = c^{1/(γ−1)}, K → K/κ, X → X/κ^{1−α}, "values scale by κ". Substituting gives X K^α, δK/r and cK^γ all scaling by 1/κ. Sol adds that the "$23B" conversion is a monetary reporting unit applied to normalized values, which is a different operation from re-solving with c = 23 (which changes K).

**Assessment.** Correct; I redid the substitution and get 1/κ. It does not affect any ratio or percentage.

**Suggested actions.**

1. Change "by κ" to "by 1/κ".
2. Introduce a monetary unit m (≈ $23B here) for the dollar illustration, and keep the homogeneity transformation separate. The same edit may be needed at `_appendix.qmd:473`.

## C7. Testable Prediction 3 rests on the pre-investment option, not on installed equity

**Raised by:** Astra (Major, Issue 2), Opus (Minor, Issue 16).

**What.** `paper/_discussion.qmd:15` predicts that lab *equity* value is concave in λ, citing `@fig-lambda-option-value`, which plots a re-optimized, unexercised investment option (`figures/paper.py:213`). Installed labs cannot re-optimize K and φ after news, and levered equity includes the default option.

**Assessment.** Correct. The reports disagree on severity; I would call it Major-lite because it is a prose-to-exhibit mismatch with an easy fix. Opus's fix is the better one: for an installed firm at fixed φ, A_eff = Π_H + (Π_L − Π_H(r − μ_L))/Δ is increasing and concave in λ whenever φ > φ̲, which gives a cleaner basis and removes the λ ≲ 0.085 caveat. I have not re-derived the concavity claim myself; check it before using it.

**Suggested actions.**

1. Base the prediction on installed value at fixed (K, φ), derived in the appendix, and keep `@fig-lambda-option-value` for the option.
2. Address the levered-equity version, or limit the prediction to unlevered value.
3. Derive the "high-φ̂ firms carry the larger exposure" clause separately.

# Comments raised by one report

## C8. The archetypes feed no reported investment result

**Raised by:** Opus (Major, Issue 2). Sol makes a related, milder point in Part 2.

**What.** The abstract (`paper/index.qmd:24`) says the calibration "shows how heterogeneous beliefs ... can generate cross-sectional differences in investment", and `_calibration.qmd:7` points to "cross-sectional variation analyzed in @sec-valuation". All trigger and capacity results use the baseline WACC; the leverage and WACC rows of `@tbl-firms` enter no computation; the only archetype output is the φ̂ → λ inversion. Further stale pointers are at `_appendix.qmd:441` and `:564`.

**Assessment.** Correct; I verified the abstract sentence and the `_calibration.qmd:7` pointer. This is a claim/evidence mismatch in the abstract, which referees read first.

**Suggested actions.**

1. Either compute archetype-level outputs (trigger, distance to default, dilemma loss at each implied λ and leverage, holding r at baseline), or
2. Rewrite the abstract to "maps assigned training allocations into implied beliefs" and delete the stale `@sec-valuation` pointers.

## C9. Implied λ from the archetypes is 3 to 10 times below the executive timelines used to motivate λ

**Raised by:** Opus (Major, Issue 3).

**What.** `_calibration.qmd:7` motivates λ with Amodei (0.30 to 0.50) and Hassabis (0.10 to 0.15), but the Anthropic-like φ̂ implies λ in [0.05, 0.09] and the Google-like one [0.03, 0.05] (`@tbl-firms`). The gap is not discussed.

**Assessment.** Plausible and interesting. I did not recompute the bands; Opus says it did and that they match the table. The gap is informative either way: it fits the static-φ upper-bound point in C2, or φ̂ is mis-assigned, or stated timelines are cheap talk.

**Suggested action.** Add a short paragraph comparing implied and stated λ and what each explanation implies.

## C10. (A3) is still presented as the condition that licenses the convention

**Raised by:** Opus (Major, Issue 5). It is a sibling of C3.

**What.** `_model.qmd:55` ("this is the condition under which the paper adopts the simplified option value"), `_appendix.qmd:76`, and `_appendix.qmd:379` ("For α > 0.67, the full two-term solution must be used"), plus the "(A3) check" row in `@tbl-baseline-results`. Step 5b says (A3) does not imply A₁ = 0.

**Assessment.** Correct; I verified all three lines. The α > 0.67 sentence in particular implies the one-term form is valid below 0.67. It also contradicts the mirror-image role (A3) plays in the IA-B explanation of C1.

**Suggested action.** Restate (A3) as an economic description (L-regime revenue alone cannot justify a standalone investment) with no role in the solution, and delete the α > 0.67 sentence.

## C11. The calibration sources table renders with literal dollar signs

**Raised by:** Sol (Major for submission readiness, Issue 4).

**What.** `paper/_appendix.qmd:422` (`($\sim$50/50)`) and `:427` (`$\approx$30--40\%`), `@tbl-sources`. Pandoc does not treat a `$` followed by a digit as a closing math delimiter. Sol inspected the blind render and reports merged rows and overfull boxes of about 327, 133 and 43 pt.

**Assessment.** Correct. I confirmed the parsing with pandoc 3.13: both cells come out as literal `\$\sim\$50` and `\$\approx\$30`. I did not re-render the full PDF to confirm the extent of the row merging Sol describes.

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

**Raised by:** Opus (Major, Issue 7).

**What.** `_appendix.qmd:630` evaluates `@fig-credit-risk` at (X, K, φ) = (0.10, 1, 0.5), about 21 × X\* and 150 × K\*. The paper's own normalization paragraph (`_calibration.qmd:38`) says such fixed-point levels carry no unit-free meaning, yet 0/12/41/97 bps appear in the main text.

**Assessment.** Correct (verified the evaluation point). It is internally inconsistent rather than wrong, and the fix is cheap.

**Suggested action.** Evaluate at entry (X\*, K\*, φ*), or at the leader's (X_P, K_L), for each ℓ, as is already done for the dilemma default probabilities; or drop the bps levels from the main text.

## C15. Proposition 3(iv) is driven by the below-market debt subsidy

**Raised by:** Opus (Major, Issue 6).

**What.** `_model.qmd:304`: the leverage effects on K_F, X_F and X_P come from par debt at r_c < r, which `_appendix.qmd:321` quantifies as a 23% transfer of I(K) at ℓ = 0.40.

**Assessment.** Fair but partly addressed: the proposition already labels (iv) a numerical finding under a modelling convention. The residual risk is that a numbered proposition proves properties of mispriced debt. Medium priority.

**Suggested action.** Move (iv) out of the proposition into a remark, or recompute with fairly priced debt (coupon set so that D = ℓI at issuance) and report what survives.

## C16. (A2) admits only a narrow parameter window

**Raised by:** Opus (Major, Issue 10); Sol notes the baseline's proximity to the interior-scale boundary.

**What.** Interior capacity requires r in (0.097, 0.135) and α in (0.356, 0.534); three of the four archetype WACCs and five of 18 sweep draws fall outside; capacity elasticities near the baseline are about 20 to 29.

**Assessment.** Correct as a description, and the paper does disclose the window. Whether to treat it as a design limitation is a judgment call. I would add one sentence to `@sec-conventions`, not change the specification.

**Suggested action.** State plainly that the capacity problem is well-posed only in this window and why (pure-power revenue against linear-plus-power cost).

## C17. Physical default probabilities "would be lower" needs an assumption

**Raised by:** Astra (Minor, Issue 6).

**What.** `_discussion.qmd:34` ends "a certainty-equivalent convention rather than a pricing measure, so physical default probabilities would be lower."

**Assessment.** Partly right. The ordering is standard *if* the risk premium on X is positive, so physical drift exceeds the certainty-equivalent drift, with the boundary and switch intensity held fixed. The sentence needs that condition, not deletion.

**Suggested action.** "... so, with a positive risk premium on demand and the boundary held fixed, physical default probabilities would be lower."

## C18. Length relative to Management Science limits

**Raised by:** Sol (journal fit), Opus (journal fit).

**What.** The 45-page main manuscript exceeds the 32-page (1.5-spaced) cap that applies to invited revisions. Neither reviewer says it bars an initial submission.

**Assessment.** Correct and worth planning for, but secondary to C1. The caveat density both reviewers mention is the natural place to cut, once C1 settles the benchmark. Check `submission/README.md` for the current policy.

## C19. Minor items (single report, all verified unless noted)

- **C19a. Musk footnote year.** `_introduction.qmd:7` says "post on X, 2025"; status id 2025124840806514916 decodes to 2026-02-21 (I verified). Fix the year. (Opus)
- **C19b. Leverage defined two ways.** "debt / total capital" in `@tbl-firms` (`_calibration.qmd:27`) and `@tbl-parameters` (`_appendix.qmd:36`), but ℓ = P/I(K) in the model (`_model.qmd:226`). Harmonize. (Opus)
- **C19c. Wrong cross-reference.** `_discussion.qmd:22` cites `@sec-calibration` for preemption; it should be `@sec-duopoly` (I verified). (Opus)
- **C19d. Uncited Hassabis λ range** at `_calibration.qmd:7`, and no stated mapping from timelines to λ (e.g. λ = −ln(1 − p)/T). Add both. (Opus)
- **C19e. Unused bibliography entries.** `weeds2002strategic` and `sundaresan2015dynamic` are in `references.bib` but uncited (I verified no `.qmd` cites them); both are relevant. Opus also suggests Lambrecht (2001), Grenadier (1996) and Mauer and Sarkar (2005). Check metadata against Zotero before adding.
- **C19f. Headline metric mixing.** The introduction juxtaposes 26% at λ = 0.02 with 6% at λ = 0.20, which matches neither the additive (4%) nor the log (23%) comparison. Use one stated metric, or give both pairs. (Opus, Issue 11)
- **C19g. "Fully analytical" and "for the same magnitude of mismatch" overstate** what is verified (`_model.qmd:316`; `_valuation.qmd:25`, checked across draws only at λ_true(1 ± 0.8)). Hedge. (Opus, Issues 12 and 13)
- **C19h. Proposition 2's maintained assumption** (`_appendix.qmd:151`, capacity "fixed at optimal values") is narrower than the statement, which holds at any fixed (K, φ). Align. (Opus, Issue 15; not verified by me)
- **C19i. Lean scope paragraph** (`_appendix.qmd:70`) should say that the default-boundary smooth pasting and the comparative statics of φ̲ are not formalized. (Opus, Issue 24)
- **C19j. Silent exception handling** in `figures/paper.py:238, 311, 434` could silently thin a figure if the single-crossing check fails, contrary to `_appendix.qmd:327`. Log and fail instead. Latent; the current curves are complete. (Opus)
- **C19k. Symbol reuse:** b, g, ρ, Δ, L, F each carry two meanings. Rename where cheap. (Opus)
- **C19l. Cosmetic and expository:** the "Overinvestment" annotation overlaps the ℓ = 0 curve in `@fig-investment-dilemma`; the policy discussion is duplicated at `_discussion.qmd:22` and `_appendix.qmd:554`; the "approximately 70%" H-share at `_appendix.qmd:273` is an exact identity (H-share = φ* at the optimum). (Opus)

# Contradictions between reports

- **Severity of C1.** Opus calls it Critical; Sol and Astra call it Major and say no Critical issue exists. All three describe the same facts. I side with Opus because it governs how every L-regime result is framed.
- **Lean.** Opus reports a successful build; Sol and Astra could not build (network) and correctly do not count that as a failure. Opus's result stands.
- **Robustness of the dilemma.** Opus reads the unrestricted re-checks as a strength (the pessimism ranking survives); Sol and Astra read them as exposing fragility (the optimistic branch disappears). Both are right about different branches; the paper should say both (C1, action 1).

# Suggested priority

1. **Before anything else:** C1 (and C2, which shares the root cause). This decides how much of the main text changes.
2. **Quick, mechanical fixes:** C3, C4, C5, C6, C10, C11, C12, C17, C19a to C19e.
3. **Moderate work:** C7, C8, C9, C13, C14, C15.
4. **After C1 settles:** C16, C18, the remaining C19 items.
