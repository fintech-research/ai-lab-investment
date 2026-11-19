# Prose review, 2026-11-18 (issue #189)

Prose-only review of `paper/` at `5768902` (umbrella branch `171-review-2026-11-revision`, after the framing rewrite #187 and the length cut #188). Eight reviewers ran in parallel: three on the main-text sections, three on the Internet Appendix, one on captions and notes, one cross-cutting. Nothing was recomputed and no exhibit was traced to code; where the truth of a claim is in doubt the finding says "check". Line numbers are source lines at that commit. Grades: **S** substantive (claim too strong, contradiction, structure), **W** wording or terminology, **M** minor (grammar, mechanics).

## Executive summary

The prose is in good shape mechanically: no em-dashes, no hard-wrapped paragraphs, no bold pseudo-headings in the restricted files, no bare "Appendix X", no use of "preemption" for the paper's own equilibrium, no calibration described as an estimation. What needs work is what two successive rewrites left behind.

1. **Unscoped invariance of the training fraction to leverage** (Proposition 2(iii) and the paragraph after it, findings 21 and 22). Exact for the single firm; the leader's allocation is a numerical object that moves slightly with leverage.
2. **Sentences that now contradict another passage**: (A1) and (A2) "hold at all parameter values used in the paper" against the admissible window and the sweeps (19); "All results here are numerical" against "Three objects are available in closed form" (52); waiting worth "about 2% more" beside losses of 2.6% and 6.9% that are measured in two different problems (24); "the ranking reverses" in Numerical Finding 1 against "about the same" in the abstract, introduction and conclusion (55); the credit exhibits said both to use and not to use the single-boundary formula (104); "I have not run the exercise over the parameter sweep" against Internet Appendix E (88).
3. **Revision-history language a first-round referee should not see**: "the earlier draft", "an earlier version of the computation", "a reviewer reported", "updated through", in about fifteen places, one of them in the main text (30, 89 to 91, 106 to 109, 125).
4. **Terminology that drifts**: five labels for "scale chosen at the switch", "monopolist" against "single firm", "timing game" against "entry game", "default" for a firm without debt, "training-survival channel" and "solvency floor" against "faith-based survival", "cautious/bold/conservative" against "pessimistic/optimistic" (7, 9, 14, 31, 35, 50, 76, 86).
5. **Stale pointers after the length cut**: blocks moved to Internet Appendix B still say "(Internet Appendix B)" of themselves, a block opener counts six derivations where there are eight, and one main-text pointer names the wrong section letter (42, 103, 105, 110).

Sections ranked by how much rewriting they need: Internet Appendix B (moved blocks, seams, history), Section 2.5 and Proposition 2 in `_model.qmd`, the conclusion, Internet Appendix E and C, Section 4, the introduction, Internet Appendix A, the calibration, the literature review.

## Findings

### Abstract (`index.qmd`, `index-blind.qmd`)

1. **S** `index.qmd:20-28`. 250 words, above the style guide's ceiling of 200 (the journal's cap is 250). Candidates to cut: the uniqueness clause, the expected-years clause, the tail of the calibration sentence.
2. **W** `:23` "a monopolist". The paper's term is "single firm".
3. **W** `:27` "the two errors cost about the same". Three errors were just named, and the equal-years pair is a different pair (0.069, 0.18). Rewrite: "Errors matched in expected years to the switch cost about the same".
4. **W** `:24`, `:27` "a boundary at which a firm stops operating" then "its shutdown boundary": two names for one object in one abstract; "far optimist" undefined.

### Introduction (`_introduction.qmd`)

5. **M** `:3` "whether and when ... , the uncertainty that drives them, remains unresolved": misplaced appositive. Rewrite: "and the uncertainty that drives them, whether and when AI capabilities reach a transformative threshold, is unresolved."
6. **W** `:5` "if the switch comes": "the switch" used before it is defined.
7. **W** `:7` "priors", "The prize is": the paper's word is "beliefs"; "prize" is decorative. `:9` "duopoly timing game": the defined term is "entry game". `:11` "post-switch contest" collides with the Tullock contest; elsewhere "post-switch race".
8. **S** `:7` "not with current architectures." in quotation marks, sourced to a headline with other wording. Check the source or drop the quotation marks.
9. **W** `:9` "I solve its problem in these primitives": jargon. Rewrite: "The allocation and the post-switch policy are in closed form; the pre-switch policy and the duopoly equilibrium are numerical."
10. **W** `:11` "I find that in the calibrated model competition, and not the single firm's own option, is what brings": wordy, and "calibrated model" against "stylized calibration". Rewrite: "First, at the baseline calibration competition, not the single firm's own option, brings investment forward of the switch."
11. **S** `:11` the closed-form sentence on φ* interrupts a paragraph about timing; move it next to the sentence on competitive position.
12. **S** `:11` "Competitive position moves the allocation only modestly ... while a follower ... trains with all its capacity": self-contradictory, and true of the leader at baseline only (14% at λ = 0.03). Rewrite with the leader's levels.
13. **S** `:11` caveats: uniqueness and the mixed equilibrium are stated, the selection of roles is not.
14. **W** `:13` "the threshold on the training fraction" does not say which of the two thresholds; `:13`, `:15` the boundary is unnamed until Section 2 and "default probability" is used for firms without debt elsewhere.
15. **S** `:13` "so training beyond the optimum raises it": holds only if the boundary's minimum is at or below φ*. Safer: "training past its minimum raises it". Check.
16. **W** `:13` "The continuation value is lost in default, yet recovery is at most 5% ... whatever the allocation": "yet" marks no contrast; "whatever the allocation" clashes with "at the model's policies".
17. **S** `:15` "Tail risk comes from operating costs more than from debt": the evidence shows the risk exists without debt; leverage of 0.40 more than doubles it. Rewrite: "Tail risk arises without debt, and leverage adds to it."
18. **W** `:15` "and not late" trails; `:15` and `_conclusion.qmd:7` "(no-switch upper bounds)" is cryptic.

### Model (`_model.qmd`)

19. **S** `:43` "Both conditions hold at the baseline calibration and at all parameter values used in the paper": contradicted by the (A2) window in `tbl-conventions`, by the archetype WACCs and by the sweeps.
20. **S** `:116` "across the admissible ranges of the other parameters, only at the top of the γ range": reads as a statement over the admissible set; it comes from the one-at-a-time sweep. Check and scope.
21. **S** `:214` Proposition 2(iii), "in the solved model the optimal training fraction is invariant to leverage": unscoped inside a proposition labelled "duopoly"; exact for the single firm only. (Known item.)
22. **S** `:218` "Because the optimal training fraction is invariant to leverage, observed comovement ... would reflect joint determination rather than a causal link": same scope problem, and "would reflect" is stronger than the model supports.
23. **S** `:218` "Parts (i)--(iv) hold at fixed (K, φ, ℓ)" although (i) and (iii) vary ℓ; "part (i) is a stress-test comparative static ... as are Remark 4 and @sec-valuation" (a section is not a comparative static; Section 4.1 is a numerical result with leverage as an exogenous parameter).
24. **S** `:116` against `:126` and `tbl-conventions`: waiting "about 2% more" beside "97.4% ... 93.1%". The 2.6% is measured inside the precommitted-scale problem and the 6.9% and the 2% with scale chosen at the switch; say so. The pure-power error is also given twice (text and table) in two framings.
25. **S** `:194` "The shift is small at baseline" against Remark 4 (boundary up 46% under par debt and 11% under fair debt at ℓ = 0.40).
26. **S** `:196`, `:218` "falling up to φ*", "if and only if φ_i < φ*": with contest shares the peak is the maximizer of A_eff,i, which is φ* only for the single firm or at a common allocation; Proposition 2(iii) words it correctly.
27. **S** `:220` "so faith-based survival holds at the optimum": at the single firm's optimum. "Because φ̃ depends on λ, the ranking reverses": φ* moves too. `:218` "A more optimistic firm therefore trains more and sits further from default": drops the λ ≳ 0.034 limit of the previous sentence.
28. **S** `:128` "holds in every version of the problem": of the single-firm problem.
29. **S** `:176` "is therefore specific to a contest in which capacity takes revenue from the rival": one alternative benchmark shows dependence, not specificity. Also "the leader's gain from capacity dominance partly reflects pie expansion, not just share theft" (the leader is the small firm; colloquial), and "the arms-race logic executives describe" (unsourced).
30. **W** `:156` "the reduced-form game of the earlier draft": revision history in the main text.
31. **W** five labels for the unrestricted single-firm problem (`:84`, `:112`, `:116`, `:258`, `:270`): use "scale chosen at the switch".
32. **S** `:256` "Role invariance of the training fraction is thus approximate for the leader": `paper/AGENTS.md` rules out role invariance (14% gap at λ = 0.03).
33. **S** `:268` "The force at work is the race that follows the switch": rests on the selected continuation; also repeats the introduction word for word. `:244` "Above it each firm would rather lead than follow": the crossing is not shown to be unique ("Just above").
34. **S** `:230` "Recovery is therefore weakly increasing in φ": a computed pattern presented as derived. `:228` "Only the inference business survives liquidation ... because the post-AGI payoff requires the going concern": an assumption written as a fact. `:230` "Faith is worthless to creditors in default, but that does not make ...": double negative.
35. **W** `:196`, `:204`, `:220` "training-survival channel", "the A_eff channel", "faith-based survival": three names for one mechanism. `:192`, `:208` the factor β⁻/(β⁻ − 1) is called an option value, then a "markup channel", and M is used undefined.
36. **S** `:272` "This is the exposure Amodei describes ... large, not modest": too strong an identification, and redundant. "not the dominant incumbent of the AI-rivalry narrative": journalistic. "the elasticity wedge of part (i)": no antecedent outside the proposition.
37. **S** `:162` "both firms' policies are obtained numerically" against Proposition 3(i) (analytical for the follower after the switch). `:45` "plays no role in the solution" against `:116` "The reason for waiting is the one that the L-regime insufficiency condition describes".
38. **S** `:27` "@sec-discussion bounds the resulting bias": the discussion measures the gain from reallocation; check and soften.
39. **S** `:134` "every exhibit of @sec-calibration and @sec-valuation": the calibration section has no main-text exhibit after #188. The two credit approximations are stated four times (`:134`, two table rows, `:158`, `:246`).
40. **W** repetition available to cut: "committed at installation" twice (`:19`, `:27`); "common volatility" and "μ_H > μ_L" twice (`:5` to `:13`); U defined three times (`:224`, `:228`); "(A1) and (A2), and in particular for δ > 0" (`:88`); "duopoly" three times in the heading of Proposition 3 (`:248`); stray "(Proposition 3(ii))" pointer at `:178`.
41. **W** `:68-76` φ_H* introduced and never used; starred trigger with generic (K, φ) on the right. `:41`, `:76` "option premium condition" and "option premium factor" name two objects. `:258` "=" for rounded values, "≈" elsewhere. `:256` "by 3.1%" ambiguous between percent and points. `:130` does not say which version of the exact problem the value curve is for. `:110` "does so later" for a comparison in demand levels. `:94` "regime-switching discount" undefined. `:64` "standard L-regime present value" with λ in the discount rate. `:147` table cell "against faith-based survival" is an interpretation.
42. **W** pointers: `:230` "(@sec-valuation, Internet Appendix A)" for the recovery bound, which is in Internet Appendix H; `:31` "in the Internet Appendix" without a location; `:148`, `:158`, `:266` "par debt at r_c < r" with the value of r_c never given in the section.
43. **M** `:226-228` display ends with a comma before a new sentence; `:143` "and" for a contrast; `:162` "each hold options"; `:128`, `:262` "near λ ≈"; `:45` "At the baseline the"; `:200` "fixed capacity (K_i, φ_i)"; `:218` "(i)--(iv)" against "(iii) to (v)"; `:204` italics break and "or monopoly"; `:240` "Both firms share the same λ"; caption at `:270` uses "Both" twice with different antecedents and the text at `:268` describes a different shaded band than the caption.

### Related literature (`_literature.qmd`, included by the introduction; listed here to keep the numbering continuous)

44. **M** `:3` "Neither includes" after four papers; move before the clause about this paper and write "None of these".
45. **S** `:5` "heterogeneous beliefs about the AGI arrival rate": the paper has a belief that differs from the truth, not equilibrium disagreement. `:7` "a discouragement effect ... that echoes the follower's delayed entry": the follower here waits because following is the better role.
46. **W** `:7`, `:13` and `_introduction.qmd:11`: the second-mover advantage is stated three times in two pages.
47. **M** `:7` "the dual role of capacity, which generates ... while training determines": subject shift. `:9` "Proposition 2 is therefore not the first default boundary": a proposition is not a boundary.
48. **W** `:9` "consistent with @gornall2020squaring": unclear what is consistent with what. `:11` "@akcigit2018growth on exploitation versus exploration R&D": check against the source (their distinction is internal against external innovation).
49. **W** `:13` "The investment-financing framework follows @hackbarth2012corporate": orphan sentence that weakens the end of the contribution statement.

### Calibration (`_calibration.qmd`)

50. **W** `:7` "a moderate prior, more conservative than": the model has no prior, and "conservative" is outside the vocabulary. `:7` three independent clauses joined by commas.
51. **S** `:3` "discipline the model's quantitative magnitudes" beside "chosen rather than estimated"; `:15` "triangulated"; `:15` "differ in ... discount rate" then "the baseline WACC" for every result; `:21` "The implied beliefs lie well below stated ones" on one executive against one archetype; `:25` "the Anthropic-like archetype's 2025 compute spending"; `:19` "costs 17% of value" without the version or the reference demand; `:19` "pessimistic end" for a belief with no truth attached.
(Wording items at `:9`, `:11`, `:17`, `:19`: "the trigger ratio" undefined, "the Dario's dilemma losses", "in both contests", dangling "and to r", years given for two of four bands, "carries ... through the single firm of the model of record", "fall only in". Pointers "in the Internet Appendix" without the section letter.)

### Quantitative implications (`_valuation.qmd`)

52. **S** `:3` "All results here are numerical" against `:7` "Three objects are available in closed form". `:3` "scale-gap index" against the appendix title "scale-gap diagnostic".
53. **S** `:7` "do not require (A2)" yet ranges reported on "draws that are solved": say which set. "rest the quantitative claims below on shares, ratios and rankings" although the credit subsection reports basis points.
54. **W** `:11` Dario's dilemma defined twice in one sentence, the second definition covering the optimistic error only.
55. **S** `:21` "the ranking reverses: 1.0% ... against 1.3%" against "about the same" in the abstract, introduction and conclusion. `:21` "do not hold at both" is ambiguous; the finding's grid (eleven beliefs) differs from the figure's (121) without a word.
56. **S** `:23` "its error is one of scale and allocation and of investing too early" against a decomposition that gives capacity no part of the pessimist's loss; "The reason ... is an identity" (the conclusion is an implication); mixed rounding (8, 4, 1.5).
57. **S** `:27` "The tail exposure is therefore set mainly by the belief and not by leverage": true of the far optimist only (leverage of 0.40 triples the informed firm's probability). "equally close to the boundary" on evidence that is probabilities. `:25` "does not move these curves": check against the ℓ = 0 row.
58. **S** `:31` "The aggressive investment reported for frontier AI labs is therefore compatible with a moderately optimistic belief at small cost": an inference about real firms from a point-mismatch exercise, close to the "consistent with value maximization" that `paper/AGENTS.md` rules out; duplicated in the conclusion.
59. **S** `:33` "and the optimistic side grows more": true of the far optimist only. "bears the leader's loss": check.
60. **W** `:37` an eighty-word first sentence with a list inside a list; "Three findings follow" beside the labelled Numerical Finding 1; "five-year default probabilities ... without debt"; "the firm exposed to default is the leader" (the single firm is too); "debt carries 4 basis points without leverage"; "for both firms" after three firms.
61. **M** `:29` caption: two different objects called "dotted"; `:27` "the optimist at 0.50 at 4.1 times, because it".

### Discussion (`_discussion.qmd`)

62. **M** `:5` "Whether competition dissipates rents on net requires a cooperative benchmark"; "brings investment forward" (only the first investment moves); "monopolist".
63. **S** `:9` "The model generates three cross-sectional predictions and one conjecture": the conjecture is not generated by the model and prediction 3 is not cross-sectional.
64. **S** `:11` "Training-heavy labs should carry less credit risk": unconditional headline against `_model.qmd:218` ("it is the belief, not the training fraction") and the U-shape; "falls with optimism"; "recover less" repeated.
65. **S** `:13` the news asymmetry is stated without its metric (equal changes in λ); "they do not" covers sensitivity and asymmetry on evidence about the first only.
66. **W** `:12` "Firms" against "labs"; `:14` "rise with beliefs" has no direction; "slightly below φ* except at long timelines" can be misread.
67. **S** `:18` the competition-policy item draws no competition-policy implication.
68. **S** `:22` "signs and bounds the resulting bias" beside "the direction ... is open"; "biases the pre-switch allocation downward, so the static φ* is an upper bound" (the static model is the one biased); "re-purpose", "redeployment", "reallocation"; "solvency floor of Proposition 2".
69. **S** `:26` "the demand level at which the firm can no longer sustain operations": the owners choose to stop.
70. **W** italics for emphasis in the three files ("stylized", "risk-adjusted", "illustrative composites", "upper bound").

### Conclusion (`_conclusion.qmd`)

71. **S** `:5` faith-based survival restated as a statement about firms that train more (a different comparative static from the introduction's); "calibrated optimum"; "from default" for a boundary that exists without debt; "(Proposition 2)" attached to a baseline numerical statement.
72. **W** `:5` "Creditors gain little on either side of the split": obscure.
73. **S** `:5-7` "Three tensions drive the results": a device the introduction never sets up, and the third is not a tension; "mismatches" against "errors".
74. **S** `:7` "Tail exposure runs the other way for proportional errors" on numbers that compare the optimist with the informed firm; "The belief sets most of this exposure" (check; leverage more than doubles it).
75. **W** `:7` "Moderate optimism is cheap ... Aggressive commitments are therefore compatible ..." says the same thing twice and duplicates `_valuation.qmd:31`; "neither beliefs from signaling nor either from agency motives".
76. **W** `:9` "too cautious ... far too bold" against pessimistic and optimistic; "abstracts from ... a \$600 billion gap" (not parallel; a 2024 figure beside 2026 spending); "natural extensions" is generic and dynamic reallocation is already treated in Internet Appendix E; the last clause repeats `_introduction.qmd:5`.

### Internet Appendix, notation and A (`_appendix.qmd:1-410`)

77. **S** `:18` "Internet Appendix A proves Propositions 1--3": most of Proposition 3 is numerical; Corollary 1 and Numerical Finding 1 are omitted.
78. **W** `:24-38` three "Target / Source" cells restate the parameter name; b is labelled "Standard" without a citation. `:42-70` symbols used throughout have no row (K*, φ*, φ̲, φ̃, X_0, λ_invest, λ_true); `:56` "Endogenous default boundary".
79. **S** `:78` "which makes K_H* its unique global maximizer" beside "none proves that a policy is optimal": reads as a contradiction. The paragraph is about 600 words. `:80` a sentence with no main verb; "is in the public repository" in a file that feeds the double-anonymous build; module and test names in prose (`:262`, `:272`).
80. **W** `:106` "so that root is it"; `:136-138` dangling "Because ...:" clause, labels (i) and (ii) that collide with the proposition's parts, a sentence repeated twice, "Note that".
81. **W** `:166` "so this interval is non-empty" with no interval named; "solves ... in closed form" against "system solved numerically" in the taxonomy. `:168` a 600-word paragraph carrying three arguments, with X_L^pure used once, "fictitious problem", and two undefined labels. `:160` an unnumbered "Remark on the pure-power form" beside numbered Remarks 1 to 4.
82. **S** `:188` "The approximation therefore errs against the faith-based survival mechanism ... and is conservative for the credit-risk conclusions": the evidence is a 3% bias in the level of X_D at baseline; faith-based survival is about its slope in λ.
83. **W** `:204` "Parts (ii) to (iv) therefore hold for ℓ ≥ 0, and so does part (i) in ℓ"; `:220` "contributes meaningfully"; `:242` "throughout the calibration ranges" unnamed; `:244` "the full range used in Proposition 3(v)" (the grid starts below λ̄), "falls with optimism".
84. **S** `:246` "The economically relevant range lies below the maximizer": unsupported (`tbl-dilemma` has firms at φ from 0.82 to 0.97); closing sentence repeats the opening; "monopoly".
85. **W** `:258` redundant parenthesis; `:262` repeats the Lean scope sentence of `:78`; `:268` "It fails"; `:296` "by 3.1%".
86. **W** drift in the range: h with three meanings (`:98`, `:258`, `:306`); "monopoly"; "pure power form"; "value-matching"; "the entry game of the absorbing regime" for the post-switch race; "1--3" against "1 to 3"; "the Proof of" against "the proof of".
87. **S** `:310` "Four further things are not established" followed by six, with five in the taxonomy row; the strongest limitation (the strategies are not an equilibrium of subgames starting above X_P) is in neither list. `:319` restates `:304` and `:308` after a double blank line.
88. **S** `:366` "I have not run the exercise over the parameter sweep of Internet Appendix E": Internet Appendix E reports the loss ratios across both sweeps. Check, and align the Domain cell at `:407`.
89. **W** `:321` "The earlier statement that the spread at entry is weakly increasing in λ was not backed by a computation": revision history.
90. **W** `:382` "The earlier draft computed this exercise with pure-power policies"; `:331` "Nothing is priced with the exponent β_H": revision history.
91. **W** `:306` "An earlier scan of 26 demand levels": revision history.
92. **S** `:358` "absent or reversed in expected time" (the table gives one number, 0.8); `:380` "the two exposures are about equal; at a factor of five ... five times" is true of the ℓ = 0 row only; "do not move with fairly priced leverage" (31.7 against 31.8); "the subsidy" undefined.
93. **W** `:362` "the reason is exact"; `:174` "And the value delivered by" and a redundant clause.
94. **S** `:409` the taxonomy note defines a label no row uses and leaves four used labels undefined; rows cite Assumption 1 where the proof maintains (A1); `:392` "all parameterizations tested".

### Internet Appendix B (`_appendix.qmd:411-703`)

95. **S** `:413` "which the main text reports as verified computationally" against `:433` "The first is not checked in the exact game"; "six derivations" where there are eight.
96. **M** `:415` "using the expectation ... to integrate out"; `:421-425` the same identity twice at the seam of a moved display, with φ_H* undefined.
97. **W** `:431` "the first ... the second" read in the wrong order; "four primitives" with three named.
98. **W** `:437` Θ_ℓ "used throughout the duopoly's capacity first-order condition" (nested game only), with a self-pointer; "appear to receive" below-market financing unsourced.
99. **W** `:439`, `:445` "Revenue is concave in capacity and the cost is linear" twice; the moved liquidation-value paragraph interrupts First, Second, Third; a 600-word paragraph; "tending to zero with leverage" for figures that rise with it; "at most a fifth" beside "at most 5%".
100. **W** `:447` "where they were previously set to zero, the perpetuity and zero": revision history, unintelligible without the earlier draft.
101. **W** `:461`, `:671` (A2) window quoted as (0.356, 0.534), γ > 1.124 and as (0.36, 0.53), γ > 1.13; `:667` "(A2) holds comfortably"; `:669` "the capacity-free closed-form training-allocation inversion".
102. **W** `:484` the nested game is defined after being used and "appears only as the approximation against which @tbl-domains measures the exact equilibrium" (false in this appendix, and reversed).
103. **W** `:484-490` "(Internet Appendix B)" three times and "(Internet Appendix A)" once inside Internet Appendix B, left from the main text; `:486` duplicates the block at `:554`.
104. **S** `:488` "The entry equilibrium and the credit exhibits ... do not" against `:608` "which Proposition 2 and the credit exhibits use".
105. **W** `:492` invokes Girsanov's theorem and then says "this is not a pricing measure"; last sentence repeats the third. `:494` solver paragraph without a label; a parenthesis on (A2) attached to a list that includes λ, ℓ and γ ≤ 2; dangling participle; `:496` module names `preemption_exact.py`, `preemption_levered.py` show the referee the word "preemption" for the paper's own game.
106. **W** `:512` "An earlier version of the computation left the option to stop ... out of W": revision history. `:508` "Two assumptions ... are solved"; `:516` "above" for a block that is below.
107. **W** `:571` "the earlier draft's statement", "the gross recovery rule of the earlier draft", "the pattern a reviewer reported": revision history and review-process language. "Four features" followed by six claims; "about four to four and a half times" against a table range of 3.66 to 4.55 (check).
108. **W** `:587`, `:591` "Under par debt every line rises with leverage" twice with the same numbers; "every object rises" although X_L/X_D falls; the table's discussion is separated from the table by the figure paragraph.
109. **W** `:596` "the reduced-form preemption game of the earlier version of the paper"; "Under the pure-power convention adopted in the Proof of Proposition 1"; "at baseline leverage ℓ = 0.40" against a zero-leverage baseline; "This block and the next two" (the third is at `:649`).
110. **W** `:494`, `:602`, `:604` X_L^mono, a fourth name for X^pp that collides with X_L.
111. **M** `:618` "cross-checked in three ways ... That check verifies"; `:622` "delays too long (the trigger is 32% lower at its capacity)".
112. **S** `:626` "and φ* is invariant throughout": unscoped; "which is optimal at every scale" attached to the wrong noun; a 700-word paragraph.
113. **W** `:628` against `:643`: the crossing of φ* and φ̲ is λ ≈ 0.024 in one and 0.025 in the other (check). `:643` italic "concavely", "policy-relevant range". `:647` "the reference demand of the earlier re-check".
114. **S** `:657`, `:659` the elasticity wedge is derived for the nested game's follower and called "the analytical source of the large follower scale" of the main text, which is the exact game's post-switch follower; scope. "Nelder-Mead" against "Nelder--Mead".
115. **W** `:665` "at the baseline" twice at the seam of a moved display.

### Internet Appendix C to H (`_appendix.qmd:704-1105`)

116. **W** `:714`, `:723` betas "for private labs" and "for comparable listed firms"; `:717`, `:727` power cost \$0.03--0.06/kWh and \$0.05--0.10/kWh (check the source); `:725` "close to the lower bound" and `:831` "close to the upper bound" for the same edge; `:721`, `:813` "disciplined".
117. **S** `:723`, `:772` "The inversion at the archetype's own WACC ... gives the bands of the previous paragraph": the bands are at the common r = 0.12. `:770` "the ordering claim" without antecedent; "reflecting ε".
118. **S** `:731` "only the training fraction enters ... and leverage enters them only through the credit objects"; several market facts without a source (issuance estimate, Oracle downgrade, CoreWeave CDS, Meta vehicle spreads, the two equity rounds); "The model's Leland channel applies most directly to these leveraged partners"; `@tbl-sources` cited for leverage values that are in `@tbl-firms`.
119. **W** `:729-756` the discussion quotes the tables before they are introduced; `:744` "(Internet Appendix C)" inside Internet Appendix C; `:756` "which is why @sec-calibration reads the columns of @tbl-firms ... one at a time".
120. **W** `:744`, `:754` "updated through Q3 2026"; `:756` "these replace earlier run-rate-based press estimates"; `:764` "unchanged from the earlier evidence": revision history.
121. **W** `:762`, `:768`, `:807` assigned values described as choices ("allocates the most to training", "the model's φ̂"); no rationale for 0.55 and 0.60.
122. **M** `:772` "five arrival rates" followed by four; "(1.2 at the Anthropic-like φ̂)" reads as a ratio.
123. **S** `:807` "firms dynamically reallocate GPUs ... on timescales of weeks": unsourced, later cited as established (`:936`) and contradicted in emphasis (`:932`).
124. **S** `:813` "their robustness to joint perturbation; the signs, not the levels, are the model's disciplined prediction" beside a paragraph saying the effect of λ on timing is not monotone; `:809` misplaced modifier ("64% below" after φ_L).
125. **W** `:847` "The diagnostic that preceded the choice of the model of record"; `:897` "where the earlier draft solved it"; `:916` "the earlier draft's reduced-form game ... reported for continuity"; `:991` "Non-equilibrium comparison of the earlier draft"; `:1049` "The pure-power policy of the earlier draft".
126. **W** `:835` "Six exercises assess robustness" omits the seven unsolved-extension blocks at the end of the section; "calibrated parameters".
127. **S** `:873` "The allocation and the thresholds are stable" (φ̲ ranges from 0.02 to 0.35 in the joint sweep; the ordering is what is stable).
128. **W** `:845`, `:893` "at most 0.98 of mutual waiting" twice in a sentence; "therefore all hold in 47 of the 59" (the count does not follow from the list); "in every such draw"; a circular sentence on the five draws without a first investment.
129. **S** `:895` "The main qualitative mechanisms do not depend on the contest functional form": categorical with no alternative contest solved for the duopoly; "the two paragraphs that follow are qualitative". `:914` "turn out to rest on the dependence of a firm's revenue on its rival's capacity" against the paragraph's own last sentence.
130. **W** κ carries three meanings (`:811`, `:918`, `:936`), the reuse note mentions two.
131. **M** `:930` "Three findings emerge" with a scope statement as the third; "Note also that"; `:932` broken syntax.
132. **S** `:993` "binary uncertainty over whether AI becomes transformative": the switch arrives with probability one; properties of an unsolved three-regime model stated in the indicative.
133. **S** `:999` "higher training investment lowers the distress threshold": unconditional. `:1001` direction of a bias asserted; `:997` "disclosed in some filings".
134. **S** `:1015` "The option value lies everywhere above the NPV curve" against two other sentences of the paragraph; "the value of waiting is the whole of the option value where the NPV is negative".
135. **S** `:1029`, `:1049` "its level at any particular point on the horizontal axis is not [identified]", then levels at two points reported as findings; "so the band survives both" although the joint ranges leave the band, without the draw count or box.
136. **S** `:1071` "upper bounds on the pre-switch default probability" from a one-clause argument; "(see the footnote in @sec-model)"; `:1101` ambiguous "it".

### Captions and notes

All notes are inside the captions. The main text has two exhibits with captions (`fig-competition-effect`, `fig-investment-dilemma`) and one table; the Internet Appendix has 34.

137. **W** `tbl-beliefs` (`:641`), `tbl-capability` (`:955`): X*, K* used for the scale-chosen-at-the-switch objects, with identical header pairs told apart by column position; `tbl-archetypes` already writes X^u.
138. **W** `fig-competition-effect` (`_model.qmd:270`), `tbl-duopoly-order` (`:550`), `fig-lambda-option-value` (`:645`), `tbl-capability`: "scale chosen freely", "whenever it invests".
139. **S** interpretive notes: `tbl-spread-entry` (`:569`) "so that the debt is worth less than half of its proceeds"; `fig-growth-decomposition` (`:1051`); `fig-lambda-option-value` (`:645`); `tbl-dynamic-phi` (`:928`) parenthesis; `fig-competition-effect` threshold.
140. **W** "in the full model" (`:645`, `:1051`): code vocabulary. "Generated by `calibration/archetypes.py`" (`:793`, `:805`). "model of record" in six captions, a term the model section never defines.
141. **W** standalone: `tbl-baseline-results` (`:700`) "described above" twice and a sentence about rounding; `tbl-duopoly-leverage` (`:585`) leaves most columns undefined.
142. **W** parallelism: the leader's boundary is X_D in two tables and X_{D,L} in the figure of the same solves; "none" against "waits"; "no debt" against "zero leverage"; "Equilibrium of the exact game", "entry game", "entry equilibrium"; "Value loss", "loss of value", "Losses"; "regime switch omitted" against "the switch omitted"; "at the model's own policies".
143. **W** titles that name the exercise and not the object: `tbl-fixedpie` (`:912`, where "benchmark" also carries two meanings), `tbl-archetypes` (`:793`, "outputs"; and "All other parameters ..., r included"), `tbl-dynamic-phi` (`:928`; percent signs in the cells).
144. **M** `tbl-dilemma-tail` (`:378`) "with the option to stop operating and debt, issued at entry" misparses, headers "True (%)", "0.02 (%)"; `tbl-duopoly-dilemma` (`:983`); `tbl-duopoly-sweep` (`:891`) "its count"; `fig-option-value` (`:1017`) "trigger-optimal", scare quotes; `tbl-dilemma` (`:333`) headers do not say they are losses.

### Cross-cutting

145. **S** The uniqueness and mixed-equilibrium caveat is stated four times in the model section (table, `:234`, `:258`, `:264`); "X, not Y" constructions appear 27 times there. Keep the caveats in Proposition 3(iii) and once after it.
146. **W** Repetition across abstract, introduction, conclusion and Section 4: the closed-form sentence (three times), "the rent from leading is competed away" (four), the allocation "sets what the firm is worth ..." (two), the full number block with its measurement conventions (four). The Leland and VC-backed caveat appears in the literature review, the calibration and the discussion.
147. **W** Eight enumerations of three ("Three experiments", "Three things", "three layers", "three ways", "Three findings", "three predictions", "Three tensions", three contributions).
148. **W** "default" for firms without debt: `_valuation.qmd:37`, `_model.qmd:272`, `_calibration.qmd:25`, `_conclusion.qmd:5`. The pair shutdown boundary and default boundary is defined at `_model.qmd:194` and then not kept.

## House-conventions check

| Convention | Result |
|:--|:--|
| Em-dash budget | Pass: none in any file |
| Hard-wrapped paragraphs | Pass (the abstract is one sentence per YAML line and renders as one paragraph) |
| Bold pseudo-headings in the main body | Pass: none in the five restricted files; the run-in labels of `_model.qmd` are in the entry-equilibrium derivation, where they are allowed |
| Citations in the abstract | Pass: none |
| Abstract length | 250 words: at the journal's cap, above the style guide's 200 |
| Blind-review hygiene | Pass, with a note: no name, affiliation or URL, but `_appendix.qmd:80` says the code "is in the public repository" |
| "Internet Appendix" naming | Pass: no bare "Appendix X" |
| Result labelling | Pass: Propositions 1 to 3, Corollary 1, Numerical Finding 1 used consistently |
| "preemption" | Pass: every hit names another paper's model, the post-switch race or the nested pure-power game; two module names in `_appendix.qmd:496` carry the word |
| Pessimistic and optimistic errors | Fail in three places (`_conclusion.qmd:9`, `_calibration.qmd:7`, and "aggressive" for observed spending) |
| Calibration not an estimation | Pass |
| Attribution | Pass |
| Revision-history language | Fail: about fifteen places (findings 30, 89 to 91, 100, 106, 107, 109, 113, 120, 125) |
