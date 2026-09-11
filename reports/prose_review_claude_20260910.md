# Prose review: final pass before the Management Science submission (2026-09-10)

**Scope.** Prose only, per the `prose-review` skill: argument clarity, claim calibration, wording, terminology, captions and notes, and the house conventions. Nothing was verified against code or the Lean proofs. The review was fanned out to eight readers (abstract/introduction/literature; model; calibration/valuation; discussion/conclusion; Internet Appendix A–B; Internet Appendix C–I; captions and notes; cross-cutting) on the consolidated text of PR #165, and every finding below was then applied on branch `150-final-prose-revision` unless marked "no change". Symbol collisions (D as debt value, face value, discriminant, and ODE coefficients; C as forced-ODE coefficient and coupon) were resolved in the same pass before the fan-out: the discriminant is now $\mathcal{R}$, the piecewise coefficients $G_1, G_2, G_w$, the face value $P$, and the forced-ODE coefficient $\Gamma$.

## Executive summary

The consolidated manuscript reads as one argument; no reviewer found a claim the Internet Appendix qualifies away, and the corrections from the September review round (precommitted versus unrestricted benchmark, beliefs-mediated survival channel, matched belief errors, arithmetic-mean benchmark, assigned allocations) survived the consolidation intact. The issues that mattered most:

1. The abstract stated faith-based survival without the "at the optimal allocation" qualifier the body uses (fixed; abstract now 161 words, no citations).
2. The introduction described the Tullock contest share as the firm's revenue share, which §3 distinguishes (fixed).
3. The conclusion's opening qualifier "in the single-firm reduced model" grammatically covered the duopoly preemption result, and its closing sentence echoed the introduction rather than stating the payoff (both fixed).
4. Three sentences in Internet Appendix A still called the precommitted-scale benchmark "exact" (fixed), and the new derivations block miscounted its own contents (fixed).
5. A duopoly matched-pair ratio quoted in §5 had no exhibit behind it (removed).

Sections ranked by how much rewriting they needed: Internet Appendix E's relocated discussion material (relabelled and split), the model section (fourteen small edits), the valuation section (sentence splits and exhibit pointers), then the rest.

## Findings

## Abstract, introduction, literature (10 findings; 10 applied)
1. [claim-strength] index.qmd:23 abstract faith-based survival unqualified → "at the optimal allocation ... though creditors cannot recover that value". applied (both index files)
2. [claim-strength] _introduction.qmd:15 monotone-in-λ claim without range → "over the arrival rates the calibration considers". applied
3. [claim-strength] _introduction.qmd:17 "forgoes most" → "much". applied
4. [claim-strength] _literature.qmd:13 "cannot deliver" → "do not generate". applied
5. [claim-strength] _introduction.qmd:17 "Capacity is invariant to beliefs" → single-firm reduced-model qualifier. applied
6. [structure] abstract length 171 → 156 words. applied
7. [structure] "worthless to creditors in bankruptcy" repeated in abstract/intro/literature → kept once (literature). applied
8. [wording] _introduction.qmd:3 subject/verb separated by appositive → restructured. applied
9. [wording] _introduction.qmd:3 unsupported superlative → dropped. applied
10. [terminology] _introduction.qmd:11 "revenue share equals its share of industry inference capacity" is the contest share (revenue share differs, §3) → corrected to contest share with the α exponent. applied
## Model section (14 findings; 14 applied)
1. [terminology] _model.qmd:13 "state H" → "regime H". applied
2. [structure] _model.qmd:19 "installed and installed" → "fixed once installed, in a single lump". applied
3. [structure] _model.qmd:209 fragment lacked the mechanism → names the share movements. applied
4. [wording] _model.qmd:179 "not be read as a magnitude" → "as an estimate of the effect's size". applied
5. [structure] _model.qmd:226/230 default-trigger sentence duplicated across subsections → moved into Default boundary. applied
6. [structure] _model.qmd:236 third statement of the single-boundary bias → cut. applied
7. [wording] _model.qmd:205 bare pointer → names the arithmetic-mean benchmark in Internet Appendix E (the reviewer's "B" was corrected: the benchmark lives in E). applied
8. [wording] _model.qmd:43 unnamed appendix section → "Parameters and Notation section". applied
9. [terminology] _model.qmd:177 prose vs tbl-domains labels → "precommitted-scale version" / "unrestricted version". applied
10. [grammar] _model.qmd:205 commas around the conditional. applied
11. [grammar] _model.qmd:140 dangling "at the larger envelope" → two sentences. applied
12. [wording] _model.qmd:258 missing comma. applied
13. [wording] _model.qmd:236 "Crucially" dropped. applied
14. [claim-strength] _model.qmd:238 "the standard result" uncited → rephrased as a description of exogenous-growth-option models (no citation needed). applied
## Calibration and valuation (14 findings; 14 applied)
1. [wording] _calibration.qmd:3 "And ..." caveat → "First ... Second". applied
2. [claim-strength] _calibration.qmd:7 "marginal investor's belief" dropped. applied
3. [structure] _calibration.qmd:7 split. applied
4. [wording] _calibration.qmd:9 "measured for one" → "estimated from one firm's data". applied
5. [structure] _valuation.qmd:3 orphaned five-year-probability sentence → opens Dario's Dilemma. applied
6. [claim-strength] _valuation.qmd:3 "range of disagreement" → "documented in @sec-calibration". applied
7. [structure] _valuation.qmd:7 two channels split. applied
8. [claim-strength] _valuation.qmd:23 shortfall pointer (Internet Appendix A). applied
9. [claim-strength] _valuation.qmd:25 "accounts for most of the firm's value" → "dominates A_eff at baseline (Internet Appendix A)". applied
10. [wording] _valuation.qmd:25 "arises from" → "is driven by". applied
11. [claim-strength] _valuation.qmd:29 1.8%/0.3% pointer (Internet Appendix A). applied
12. [structure] _valuation.qmd:29 split. applied
13. [structure] _valuation.qmd:31 split. applied
14. [terminology] _valuation.qmd:15/37 caveat phrasing unified. applied
## Captions and notes (6 findings; 6 applied)
1. [grammar] fig-credit-risk "neither ... or" → "nor". applied
2. [wording] fig-default-boundaries log-axis sentence. applied
3. [structure] four main-text figure titles → "[object] as a function of [X]". applied
4. [wording] fig-competition-effect colon label dropped. applied
5. [terminology] tbl-duopoly-dilemma "vs." → "versus". applied
6. [structure] tbl-duopoly-dilemma "Parameters: baseline calibration." applied
## Discussion and conclusion (8 findings; all applied)
1. [claim-strength] _discussion.qmd:14 prediction 2 built as assert/retract/reassert → one clause with the imported assumption. applied
2. [structure] _conclusion.qmd:3 "In the single-firm reduced model" governed the duopoly preemption clause → split. applied
3. [wording] _conclusion.qmd:1 "answer to different forces" → "respond to". applied
4. [grammar] _conclusion.qmd:9 ambiguous antecedent of "which may discipline" → restrictive clause. applied
5. [structure] _discussion.qmd:13 prediction 1 sentence chained colon/parenthetical/whereas/since → split. applied
6. [wording] _discussion.qmd:13 "raises it beyond" → "raises it for φ̂ above it". applied
7. [wording] _discussion.qmd:22 "at once" → "simultaneously". applied
8. [structure] _conclusion.qmd:9 closing sentence restated the setup → ties to the two-sided cost of a wrong belief. applied
## Internet Appendix A and B (10 findings; 10 applied)
1. [structure] _appendix.qmd:299 "four derivations" vs six sub-blocks → "six", preemption-game item added. applied
2. [structure] _appendix.qmd:301 wrong pointer to "B's first block" → "documented later in this appendix". applied
3. [wording] _appendix.qmd:135/137/143 bare "exact" continuation value → "precommitted-scale". applied
4. [terminology] "the high regime" → "the H-regime". applied
5. [terminology] block headings → matched pair "Piecewise L-regime stopping problem, precommitted / unrestricted post-switch scale". applied
6. [terminology] overview "parameter elasticities (D)" → "parameter sensitivity (D)". applied
7. [wording] "arithmetic-mean contest"/"benchmark" → canonical label at both sites. applied
8. [grammar] "shortened to a stated result" → "reduced to". applied
9. [wording] value matching / smooth pasting hyphenation unified for bare-noun use. applied
10. [claim-strength] "riskier than it is" → "than the coupled system implies". applied
## Internet Appendix C to I (12 findings; 11 applied, 1 no change)
1. [structure] provenance heading in E → six descriptive run-in labels. applied
2. [structure] three-limitation paragraph split with labels. applied
3. [structure] second Tullock mention cross-references the contest-functions block. applied
4. [structure] δ rescaling derived twice (C and F) → F cross-references C. applied
5. [structure] σ logic explained twice → F cross-references C. applied
6. [structure] archetype rationale and belief inversion → two labelled paragraphs. applied
7. [grammar] "a setting several frontier AI labs" → "a setting that". applied
8. [wording] "coincides ... exactly" reordered. applied
9. [terminology] "redividing a fixed pie" → "redistributing a given level of industry revenue". applied
10. [terminology] "prediction 1" capitalization: lowercase is the paper's convention in every file. no change
11. [claim-strength] discount-rate rationale hedged. applied
12. [wording] follows from 1. applied
## Cross-cutting (10 findings; 8 applied, 2 no change)
1. [structure] conclusion's "central point" echoed the introduction → restated as the payoff. applied
2. [claim-strength] _discussion.qmd:22 unconditional faith-based-survival policy sentence → qualified at the calibrated optimum. applied
3. [terminology] "unconstrained" (X_L^mono) vs "unrestricted" (post-switch scale) → "monopoly-only trigger". applied
4. [wording] _valuation.qmd:39 duopoly matched-pair ratio 3.0 has no exhibit → parenthetical dropped. applied
5. [wording] 4.7 vs 4.6 for the same ratio → 4.6. applied
6. [wording] 26/6 vs 26.2/5.6 → appendix says they are the same numbers at one decimal. applied
7. [structure] D heading and E's opening block both "Parameter sensitivity" → E block "Parameter-perturbation sweep". applied
8. [wording] central mechanism phrased three ways (abstract, intro/conclusion, §3) → abstract and conclusion now differ from §3 by design; left. no change
9. [terminology] Γ vs C: the reviewer read the file before the rename landed; every use is now Γ. no change (verified by grep)
10. [claim-strength] _valuation.qmd non-monotone option value not stated locally → Remark 3 pointer added. applied

## House-conventions check

| Convention | Result |
|---|---|
| Em-dashes (budget 5 per paper, none in the abstract) | pass: 0 in every source file |
| Hard-wrapped prose | pass: one paragraph per line (the only multi-line blocks are lists, tables, and display math) |
| Abstract citations | pass: none |
| Abstract length (≤ 250 words) | pass: 161 |
| Blind-review hygiene | pass: author metadata only in `index.qmd`; `index-blind.qmd` mirrors it without `authors`, `affiliations`, `thanks` (metadata parity test passes) |
| "Internet Appendix" naming | pass |
| No bold pseudo-headings in the main-body files | pass |
| Result labelling (Numerical Finding 1 not promoted) | pass |
| Main-text pointers match Internet Appendix contents (B derivations block, C `tbl-firms-data`, E discussion blocks, I supplementary literature) | pass |
| Terminology (contest vs revenue share; arithmetic-mean industry-revenue benchmark; precommitted-scale vs unrestricted; X_{D,F} vs X_{D,L}; monopoly-only trigger vs unrestricted scale) | pass after the edits above |
