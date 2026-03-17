# Referee Comment Address Check

**Reviewer:** codex
**Date:** 2026-03-16
**Scope:** Fresh read of the current manuscript only. I did not use git history.

## Executive Summary

The manuscript has done a strong job on the line-by-line comments. Of the 33 detailed comments, 32 are now addressed satisfactorily in the current text. Most of those fixes are concrete: notation is cleaner, several incorrect comparative statics and elasticity claims are corrected, ambiguous statements have been narrowed, and a number of contested passages now explicitly state when the paper is using a numerical regularity or an unconditional approximation.

The remaining weaknesses are concentrated in the high-level structural comments. The paper now often acknowledges the approximation or limitation, but in several places it still does not provide the stronger derivation or extension the referee asked for. In my judgment, the six “overall feedback” items are not fully resolved, and one detailed comment remains only partially resolved for the same reason.

## Overall Feedback

1. **Solving the real options boundary conditions in Section 2.3.3:** **Not fully addressed.** The current text in `paper/_model.qmd:180-186` removes the internal contradiction by stating clearly that `C` is pinned down by the ODE and that the trigger conditions determine `X*`, not `C`. But it still asserts, rather than proves, that the absence of a standalone L-regime trigger implies `A_1 = 0` exactly. This is clearer than before, but it is not the formal boundary-condition argument the referee requested.

2. **The dimensionality of the default boundary in Proposition 2:** **Not fully addressed.** The manuscript now openly labels the single-boundary formula as an “unconditional `A_eff` approximation” and notes that a fully coupled regime-switching model would have state-dependent boundaries; see `paper/_model.qmd:272-273`. That is an honest clarification, but it is not a derivation showing that the one-boundary expression is exact.

3. **Rigidity in the training-inference allocation margin:** **Not fully addressed.** `paper/_discussion.qmd:44-61` gives a thoughtful discussion of the direction of bias from static `phi`, and `paper/_discussion.qmd:69-70` notes mixed revenue sources as a limitation. But the paper still does not show robustness to reallocation, persistent training stock, or adjustment-cost extensions, which was the core request.

4. **Total industry revenue expansion in the contest specification:** **Not fully addressed.** The current text explains the revenue-expansion property correctly and says the main qualitative results survive under Cournot; see `paper/_model.qmd:229-236` and `paper/_appendix.qmd:313-317`. That is an improvement, but there is still no direct replication of the central quantitative objects under a fixed-pie alternative in the main text.

5. **Scale and normalization across model environments:** **Not fully addressed.** `paper/_calibration.qmd:108-113` now explains why duopoly levels are much larger than single-firm levels inside the model, but the paper still does not map one unit of `K` or `X` to an observable scale in a way that stabilizes interpretation across environments.

6. **The strategic environment for Dario's dilemma:** **Not fully addressed.** `paper/_valuation.qmd:136-139` explicitly acknowledges that the current formalization is single-firm and that a duopoly version is left for future work. That is transparent, but it does not answer the referee’s core concern.

## Detailed Comments

1. **Incorrect determination of the particular solution coefficient `C`:** **Not fully addressed.** `paper/_model.qmd:180-186` fixes the direct inconsistency about `C`, but the claim that `A_1 = 0` is “exact” still rests on assertion rather than a full derivation.

2. **Contradiction regarding the leader's optimal capacity:** **Addressed.** The paper now states that the closed-form separability does **not** carry over exactly to duopoly, that the follower is optimized numerically, and that the leader-monopolist equality is only a computational regularity; see `paper/_model.qmd:144-146` and `paper/_model.qmd:376-379`.

3. **Incorrect elasticities in Table 7:** **Addressed.** The elasticity table is now consistent with Proposition 1: `epsilon_{K*,lambda}` is approximately zero and `epsilon_{phi*,lambda}` is approximately `+0.5`; see `paper/_appendix.qmd:288-304`.

4. **Contradictions in baseline results comparison:** **Addressed.** The baseline paragraph now distinguishes the single-firm trigger from the H-regime monopolist trigger and explains the raw scale jump across environments; see `paper/_calibration.qmd:108-113`.

5. **Contradiction regarding capacity optimization in duopoly:** **Addressed.** The manuscript now says directly that exact separability fails in duopoly and that the follower solves a joint numerical problem in `(K_F, phi_F)`; see `paper/_model.qmd:144-146` and `paper/_model.qmd:345-348`.

6. **Contradictions regarding convexity and capacity independence:** **Addressed.** The equity-value discussion is now explicitly local, not global, in `lambda`, and the text separately clarifies that single-firm `K*` is lambda-independent while duopoly capacity can vary; see `paper/_valuation.qmd:146-149`, `paper/_model.qmd:196-197`, and `paper/_calibration.qmd:122`.

7. **Misspecification of the leader's H-regime continuation value:** **Addressed.** The manuscript now states that the follower trigger is computed with an unconditional `A_eff` and is not regime-contingent, explicitly flagging the approximation the referee asked about; see `paper/_model.qmd:352-355`.

8. **Confusion in the boundary condition for preemption existence:** **Addressed.** Appendix A now aligns the definition of `L(X)` with the endpoint argument and states that `L(X_F*)` is a point evaluation of the invest-now payoff, not a continuation value from earlier entry; see `paper/_appendix.qmd:158-164`.

9. **Misunderstanding of Assumption (A2) and numerical optimization:** **Addressed.** The hyperscaler statement is corrected, and the numerical method discussion now explains bounds, starting points, and the interpretation of cases where `(A2)` fails; see `paper/_appendix.qmd:231-241`.

10. **Mismatched segment revenue and corporate CapEx:** **Addressed.** The Google-like archetype now explicitly explains why consolidated CapEx is paired with Cloud revenue and what the segment-level ratio would look like instead; see `paper/_calibration.qmd:64-66`.

11. **Incorrect elasticity value and backwards logic on uncertainty propagation:** **Addressed.** The calibration now reports the moderate elasticity and states the inverse-mapping logic in the correct direction; see `paper/_calibration.qmd:84-85`.

12. **Asset pricing terminology contradiction:** **Addressed.** The calibration section now restates the reduced-form valuation convention clearly and distinguishes WACC-based valuation from the separate `r_f` used in spread calculations; see `paper/_calibration.qmd:23-25` and `paper/_valuation.qmd:52-69`.

13. **Incorrect comparative static for training fraction:** **Addressed.** The paper now says `phi*` is independent of `mu_L`, both in Proposition 1 and in Appendix A; see `paper/_model.qmd:140` and `paper/_appendix.qmd:103-104`.

14. **Misleading notation and definition for value loss (`Delta V`):** **Addressed.** The valuation section now defines `NPV(lambda_a, lambda_b)` at a common initial demand level and states the normalization for percentage losses; see `paper/_valuation.qmd:95-103`.

15. **Unlevered equity value ignores the abandonment option:** **Addressed.** The text now explicitly states that the unlevered case is treated as a perpetuity with no endogenous abandonment option and explains the omission in a footnote; see `paper/_model.qmd:321`.

16. **Mismatch between value decomposition formulas and Figure 8:** **Addressed.** The valuation section now says that the figure is an H-regime illustration while the more general formulas apply in L with switching; see `paper/_valuation.qmd:35-42`.

17. **Incorrect comparative static for survival threshold:** **Addressed.** The sign on `alpha` is corrected: the text now says `underline(phi)` is increasing in `alpha`; see `paper/_model.qmd:289`.

18. **Inaccurate claim about convexity of leader's value function:** **Addressed.** Appendix A now distinguishes the existence of power-function terms from a blanket claim that `L''(X) > 0`; see `paper/_appendix.qmd:169-171`.

19. **Flawed intuition for marginal cost of training in Appendix A:** **Addressed.** The revised text now describes the duopoly effect as a higher **relative** cost and no longer claims the H-regime benefit is independent of phase; see `paper/_appendix.qmd:180-188`.

20. **Conflation of dynamic reallocation with learning about `lambda`:** **Addressed.** The discussion now notes explicitly that the exponential hazard is memoryless and that the reallocation argument comes from discounting, with Bayesian learning treated as a separate extension; see `paper/_discussion.qmd:46-49`.

21. **Incorrect mathematical explanation for Dario's dilemma asymmetry:** **Addressed.** Appendix A no longer relies on the “steeper curvature on the under-training side” heuristic and instead explains the asymmetry through H-regime dominance plus the nonlinear `lambda -> phi*` mapping; see `paper/_appendix.qmd:200-210`.

22. **Mix-up between cost convexity (`gamma`) and revenue concavity (`alpha`):** **Addressed.** The technology section now separates convex installation costs from scaling-law diminishing returns in revenue; see `paper/_model.qmd:25-27`.

23. **Flawed mathematical justification for asymmetric revenue:** **Addressed.** The paper now uses the correct quadratic-mean versus arithmetic-mean inequality; see `paper/_model.qmd:229-233`.

24. **Contradiction regarding hardware repurposing in Introduction:** **Addressed.** The introduction now says the hardware is physically fungible but reallocation is costly because of configuration, networking, and software frictions; see `paper/_introduction.qmd:9-11`.

25. **Inaccurate description of monopoly opportunity cost:** **Addressed.** The introduction now says monopoly removes the **contest-share component** of the opportunity cost rather than eliminating the opportunity cost entirely; see `paper/_introduction.qmd:22` and `paper/_appendix.qmd:180-182`.

26. **Contradiction regarding fixed market size in Tullock contest:** **Addressed.** The discussion now distinguishes zero-sum share competition from the model’s asymmetry-driven revenue expansion effect; see `paper/_discussion.qmd:78-82` and `paper/_model.qmd:229-236`.

27. **Inconsistent notation for the continuous coupon payment:** **Addressed.** The model section now defines `c_D` as the total coupon payment and states that this notation is used throughout; see `paper/_model.qmd:261-272`.

28. **Revenue increase from capacity doubling in contest:** **Addressed.** The calibration now says the `2^alpha` statement holds when share is fixed and separately states the unilateral symmetric-duopoly effect; see `paper/_calibration.qmd:31-33`.

29. **Mismatch between heading and text in the third tension:** **Addressed.** The current framing now ties Dario’s dilemma directly to preemption-compressed waiting value rather than leaving the label-text connection implicit; see `paper/_conclusion.qmd:16-18`.

30. **Incomplete expression for marginal cost of training:** **Addressed.** The monopoly-phase derivative is now described as proportional to the `phi`-dependent component, with the omitted common factors stated explicitly; see `paper/_appendix.qmd:180`.

31. **Direction of markup factor limit:** **Addressed.** The appendix now says the markup moves toward 1 **from below**, which is the correct direction for `beta_s^- < 0`; see `paper/_appendix.qmd:139-143`.

32. **Notational slip in describing Huisman and Kort (2015):** **Addressed.** The appendix now uses a generic positive root `beta` when discussing the standard HK benchmark; see `paper/_appendix.qmd:166-167`.

33. **Notation overload for variable `N`:** **Addressed.** The leverage-training substitution section now switches to `Psi(ell)` and explicitly notes that this regrouping differs from the earlier `N`; see `paper/_appendix.qmd:141` and `paper/_appendix.qmd:145`.

## Bottom Line

- **Overall feedback items properly addressed:** 0 / 6
- **Detailed comments properly addressed:** 32 / 33
- **Main remaining gap:** the manuscript is much cleaner, but the big unresolved issues are still the structural ones: the exact `A_1 = 0` boundary logic, the one-boundary regime-switching default approximation, the lack of model-based robustness to dynamic `phi`, the limited treatment of the contest-specification issue, the missing unit bridge across environments, and the single-firm formalization of Dario's dilemma.
