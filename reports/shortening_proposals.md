# Shortening Proposals — Main Manuscript (Management Science blind submission)

**Date:** 2026-07-26
**Analyst:** claude (Claude Fable 5, Claude Code) — analysis only, no paper edits made
**Baseline artifact:** `paper/_output/ai_lab_investment_blind.pdf` (75 pp, built 2026-07-25 23:07, `linestretch: 1.5`)
**Companion artifact:** `paper/_output/ai_lab_investment_blind_ecompanion.pdf` (36 pp)
**Branch state at measurement:** `fix/presubmission-review-110`, HEAD `bbfdad2` (all review-fix PRs #111–#128 merged)

**Method.** Page positions were extracted with `pdftotext -bbox` and reconstructed into per-page line
boxes. The text block runs from y ≈ 82 pt to y ≈ 710 pt (page numbers sit at 726–742 pt), so
fractional page positions are `(y0 − 82)/628`. All lengths below are in *pages of the blind PDF at
1.5 spacing*, quoted to 0.01 pp but reliable to about ±0.1 pp; float (figure/table) footprints are
measured from the first line of the graphic to the last line of the caption, and each float is
**attributed to the section that owns it**, not to the page LaTeX floated it onto (four floats drift
across a subsection boundary: Fig. 2, Fig. 5, Fig. 7, Fig. 9).

---

## 1. Page map of the blind manuscript

Note the blind manuscript's numbering: the literature review is **§1.1**, a subsection of the
Introduction, so the top-level sections are 1 Introduction, 2 The Model, 3 Quantitative Calibration,
4 Quantitative Implications, 5 Discussion, 6 Conclusion, References.

### 1.1 Top-level structure

| Block | Starts (pg) | Ends (pg) | Length (pp) | Share of main text |
|---|---|---|---|---|
| Title + abstract + keywords | 1.00 | 1.75 | 0.75 | 1.1% |
| **1 Introduction** (excl. 1.1) | 1.75 | 5.41 | **3.66** | 5.3% |
| **1.1 Related literature** | 5.41 | 10.23 | **4.82** | 7.0% |
| **2 The Model** | 10.23 | 38.29 | **28.06** | 40.7% |
| **3 Quantitative Calibration** | 38.29 | 49.16 | **10.87** | 15.8% |
| **4 Quantitative Implications** | 49.16 | 61.23 | **12.07** | 17.5% |
| **5 Discussion** | 61.23 | 67.45 | **6.22** | 9.0% |
| **6 Conclusion** | 67.45 | 70.00 | **2.55** | 3.7% |
| *Main text subtotal (pp. 1–69)* | | | **69.00** | 100% |
| References | 70.00 | 75.45 | 5.45 | — |
| *Total blind manuscript* | | | **74.45** (75 physical pp) | — |

### 1.2 Subsection detail

Column "Own floats" gives the footprint of figures/tables the subsection owns; "Text" is length net
of owned floats placed inside the span. "Owned total" is what would actually leave the main text if
the subsection were demoted wholesale.

| § | Title | Span (pp) | Own floats | Text | Owned total |
|---|---|---|---|---|---|
| 1 | Introduction | 3.66 | — | 3.66 | 3.66 |
| 1.1 | Related literature | 4.82 | — | 4.82 | 4.82 |
| 2 | The Model — preamble | 0.17 | — | 0.17 | 0.17 |
| 2.1 | Environment | 0.82 | — | 0.82 | 0.82 |
| 2.2 | Technology (preamble) | 0.46 | — | 0.46 | 0.46 |
| 2.2.1 | Training-inference allocation | 1.32 | — | 1.32 | 1.32 |
| 2.3 | Single-Firm Benchmark (preamble) | 0.17 | — | 0.17 | 0.17 |
| 2.3.1 | Installed value | 0.83 | — | 0.83 | 0.83 |
| 2.3.2 | Option value in regime *H* | 3.61 | Fig 1 (0.52), Fig 2 (0.61)† | 3.09 | 4.22 |
| 2.3.3 | Option value in regime *L* | 4.11 | Fig 3 (0.51) | 2.99 | 3.50 |
| 2.4 | Duopoly with Default Risk (preamble) | 0.14 | — | 0.14 | 0.14 |
| 2.4.1 | Regime-specific competition | 1.62 | — | 1.62 | 1.62 |
| 2.4.2 | Installed value in the duopoly | 0.61 | — | 0.61 | 0.61 |
| 2.4.3 | Capital structure | 0.72 | — | 0.72 | 0.72 |
| 2.4.4 | Default boundary (incl. Prop 2) | 4.08 | Fig 4 (0.65) | 3.43 | 4.08 |
| 2.4.5 | Equity and debt values | 1.59 | — | 1.59 | 1.59 |
| 2.4.6 | Preemption equilibrium (incl. Prop 3) | 5.93 | Fig 5 (0.52) | 5.41 | 5.93 |
| 2.5 | Solution conventions and approximations | 1.88 | — | 1.88 | 1.88 |
| 3 | Quantitative Calibration — preamble | 0.53 | — | 0.53 | 0.53 |
| 3.1 | Demand Process | 1.66 | — | 1.66 | 1.66 |
| 3.2 | Technology Parameters | 1.61 | — | 1.61 | 1.61 |
| 3.3 | Stylized Firm Archetypes | 4.97 | Tbl 1 (0.45), Fig 6 (0.52) | 4.00 | 4.97 |
| 3.4 | Baseline Results | 1.13 | — | 1.13 | 1.13 |
| 3.5 | Sensitivity Analysis | 0.97 | — | 0.97 | 0.97 |
| 4 | Quantitative Implications — preamble | 0.50 | Fig 7 (0.45)‡ | 0.50 | 0.95 |
| 4.1 | A Normalized Scale-Gap Diagnostic | 2.94 | Fig 8 (0.57) | 1.92 | 2.49 |
| 4.2 | Credit Risk Analysis | 2.24 | Fig 9 (0.60)‡ | 2.24 | 2.84 |
| 4.2.1 | — Credit spreads | 0.77 | — | 0.77 | 0.77 |
| 4.2.2 | — Default probability | 0.69 | — | 0.69 | 0.69 |
| 4.2 | — Fig 9 discussion | 0.64 | Fig 9 (0.60) | 0.64 | 1.24 |
| 4.3 | Dario's Dilemma | 5.67 | Fig 10 (0.66) | 4.41 | 5.07 |
| 4.3.1 | — Setup | 0.37 | — | 0.37 | 0.37 |
| 4.3.2 | — Value loss | 3.69 | Fig 10 (0.66) | 3.03 | 3.69 |
| 4.3.3 | — Implications | 0.82 | — | 0.82 | 0.82 |
| 4.4 | Equity Valuation Sensitivity | 0.72 | — | 0.72 | 0.72 |
| 5 | Discussion — preamble | 0.21 | — | 0.21 | 0.21 |
| 5.1 | Welfare and Overinvestment | 0.45 | — | 0.45 | 0.45 |
| 5.2 | Testable Predictions | 1.56 | — | 1.56 | 1.56 |
| 5.3 | Policy Implications | 0.55 | — | 0.55 | 0.55 |
| 5.4 | Direction of Bias from Static φ | 1.67 | — | 1.67 | 1.67 |
| 5.5 | Limitations | 1.78 | — | 1.78 | 1.78 |
| 6 | Conclusion | 2.55 | — | 2.55 | 2.55 |

† Fig 2 (`fig-comparative-statics`) is *owned* by §2.3.2 but typeset on p. 18, inside §2.3.3's span.
‡ Fig 7 (`fig-lambda-timeline`) is owned by the §4 preamble but typeset on p. 50 inside §4.1;
Fig 9 (`fig-credit-risk`) is owned by §4.2 but typeset on p. 55 inside §4.3.

### 1.3 Floats: count and footprint

11 floats (10 figures + 1 table) occupy **6.06 pp = 8.8% of the main text**.

| Float | Label | Placed pg | Owner § | Graphic | Caption | Footprint |
|---|---|---|---|---|---|---|
| Figure 1 | `fig-option-value` | 15 | 2.3.2 | 0.39 | 0.13 | **0.52** |
| Figure 2 | `fig-comparative-statics` | 18 | 2.3.2 | 0.50 | 0.11 | **0.61** |
| Figure 3 | `fig-lambda-option-value` | 21 | 2.3.3 | 0.40 | 0.11 | **0.51** |
| Figure 4 | `fig-default-boundaries` | 28 | 2.4.4 | 0.47 | 0.18 | **0.65** |
| Figure 5 | `fig-competition-effect` | 35 | 2.4.6 | 0.37 | 0.15 | **0.52** |
| Table 1 | `tbl-firms` | 42 | 3.3 | 0.34 | 0.11 | **0.45** |
| Figure 6 | `fig-firm-comparison` | 46 | 3.3 | 0.37 | 0.15 | **0.52** |
| Figure 7 | `fig-lambda-timeline` | 50 | 4 (pre) | 0.36 | 0.09 | **0.45** |
| Figure 8 | `fig-growth-decomposition` | 52 | 4.1 | 0.35 | 0.22 | **0.57** |
| Figure 9 | `fig-credit-risk` | 55 | 4.2 | 0.36 | 0.24 | **0.60** |
| Figure 10 | `fig-investment-dilemma` | 59 | 4.3.2 | 0.42 | 0.24 | **0.66** |

Figures per section: §2 five (2.81 pp), §3 one figure + one table (0.97 pp), §4 four (2.28 pp),
§§1, 5, 6 none. Captions are heavy: Figures 8–10 spend 0.22–0.24 pp each on caption text alone, a
consequence of the review-driven scope caveats now living in captions.

---

## 2. Target

| Basis | Current | −10% | −15% | −20% |
|---|---|---|---|---|
| Main text, excl. references (69.00 pp) | 69.00 | −6.90 → 62.1 | **−10.35 → 58.7** | **−13.80 → 55.2** |
| Whole blind manuscript (74.45 pp) | 74.45 | −7.45 | −11.17 | −14.89 |

**Working target: remove 10.4–13.8 pages of main text.** References are effectively fixed (5.45 pp,
~120 entries; the only lever is dropping citations, which cuts against review fix #122). Sections 2
and 4 together are 58% of the main text and are where the pages are.

A caveat on precision: LaTeX reflow means a measured *x*-page removal typically yields between
0.9*x* and 1.2*x* actual pages, because removing a float also removes page-breaking slack. Treat the
package totals as ±1 page.

---

## 3. Constraints (do not undo)

Carried forward from `reports/review_report_consolidated.md` and PRs #111–#128, these must remain in
the **main paper** in some form:

1. **(A2) admissibility disclosure in §3** — admissible windows for *r*, α, σ, and the statement
   that three of four archetype WACCs violate (A2) (§3.1 lines 30–35, §3.2 lines 42–44). Fix A7/M4.
2. **`@sec-conventions` (§2.5) and the forward-reference block before Proposition 3** (§2.4.6,
   "Conventions maintained in the equilibrium"). Fix C1/M8.
3. **Piecewise-bias scoping statements** — the "what is exact and what is convention" block in
   §2.3.3 and the 53%/96%/2.6% bias numbers in §2.5. Fix C1/C2.
4. **Honest robustness/sweep statements** — the ±25% band language in §4.1, the "verified
   computationally" labels in Prop 3, the §3.5 pointer to `@tbl-elasticities`. Fix M6.
5. **Corrected dilemma attributions** — the asymmetry runs through the entry trigger and φ, *not*
   capacity/coupon (§4.3.2 line 145; §6). Fix C3/A2.
6. **Regime-switching-credit positioning in §1.1** — Hackbarth–Miao–Morellec, Chen, Bhamra et al.,
   plus the Aguerrevere and Van Mieghem/Chod–Rudi anchors. Fix M7/#122.

Everything proposed below is compatible with all six. Where a proposal touches one of these blocks,
it is compression-in-place, not demotion.

---

## 4. Candidate cuts

Ordered by pages-per-unit-of-risk. "Net" = measured owned footprint minus the summary paragraph left
behind (a 2–4 sentence stub + pointer costs ≈ 0.12–0.20 pp at 1.5 spacing).

---

### C1. §4.1 "A Normalized Scale-Gap Diagnostic" → Internet Appendix

**Moves:** the whole subsection (§4.1, pp. 49.66–52.60) including `@fig-growth-decomposition`, the
`V_AIP` / `V_gap` / `g` definitions, the crossover-at-0.77 discussion, and the ±25%-band sentence.
**Stays:** 3 sentences in §4 — the Berk–Green–Naik motivation, the statement that the index falls
monotonically to zero at *K/K\** ≈ 0.77, the "not a growth-option decomposition, levels not
identified" caveat, and a pointer.

**Measured:** owned total 2.49 pp − 0.16 stub = **net 2.33 pp (3.4% of main text)**.

**Message impact:** low. This is the one §4 result that, after PR #124's reframing, explicitly
disclaims being a decomposition, disclaims an asset-pricing implication (§4.1 last paragraph:
"carries no direct asset-pricing implication… no pricing kernel"), and disclaims level
identification. It supports none of the three headline mechanisms (φ\*, faith-based survival,
Dario's dilemma) nor the duopoly preemption results. On a linear read a referee loses a
comparative-statics exhibit about installed capacity — genuinely interesting, but the section itself
now says its content is "entirely the monotone decline and the location of the crossover."
**Referee-asks-it-back risk: low.** The one live thread is testable prediction 2 (training–beta),
which cites `@aguerrevere2009real` and is already framed in §5.2 as a conjecture imported from
outside the model; it needs the *idea* of a composition shift, not the figure.

**Verdict: Recommended.** Largest single saving with the weakest link to any headline claim.

---

### C2. §4.2 credit-risk exposition → Internet Appendix, keep headline numbers

**Moves:** the spread definition display, the first-passage default-probability display and its four
sentences of measure/drift qualification, the panel-by-panel walk-through, and
`@fig-credit-risk`.
**Stays (≈0.55 pp):** one paragraph giving (i) the two opposing φ-channels — faith-based survival
lowers PD, recovery specification raises LGD, "novel to my knowledge"; (ii) the headline leverage
gradient (spreads ≈0/12/41/97 bps and 5-yr PD 0.63%/1.80%/4.85%/12.98% at ℓ = 0.05/0.20/0.40/0.70);
(iii) the one-sentence "high-probability, modest-severity for creditors, catastrophic for
shareholders" contrast; (iv) the model-implied-risk-adjusted relabeling (review fix M2) and the
fixed-(*X*, *K*, φ) evaluation-point caveat (fix #9).

**Measured:** owned total 2.84 pp − 0.55 stub = **net 2.29 pp (3.3%)**.

**Message impact:** moderate. §4.2 is the quantitative face of Proposition 2 (faith-based survival),
which *is* a headline mechanism — but the mechanism itself is proved and discussed in §2.4.4, and
the "two faces" decomposition is restated as testable prediction 1 in §5.2. What a referee loses on
a linear read is the visual leverage gradient. **Referee-asks-it-back risk: moderate** — an MS-Finance
referee may want to see the spread curve. Mitigation: the retained paragraph carries every number
the abstract and conclusion rely on, and the figure is one click away in the e-companion.

**Lighter variant (C2-lite):** move only `@fig-credit-risk` (0.60) and the two equation displays
with their measure caveats (≈0.55) → **net ≈ 1.05 pp**, keeping both prose subsections. Use this if
C2 feels too aggressive.

**Verdict: Recommended** (C2 full if the ~15% target is binding; C2-lite otherwise).

---

### C3. §5.4 "Direction of Bias from Static φ" → Internet Appendix

**Moves:** the two-period setup, the memorylessness argument and its footnote, the "why the option
biases φ₁ downward" paragraph, the numerical illustration sentence (φ₁ = 0.60, φ_H → 0.99, option
worth 5.1%/0.2%), and the closing "dynamic reallocation would attenuate but not eliminate" paragraph
(0.51 pp of it).
**Stays (4 sentences):** static φ is the most-flagged limitation; a two-period extension signs the
bias — the revision option biases the *pre-switch* allocation downward, so φ\* ≈ 0.70 is an upper
bound; because of that, the λ implied by an observed φ̂ is *higher* under the dynamic model; and both
headline mechanisms (Prop 2 solvency floor, NF1 asymmetry) attenuate but survive, because each runs
through the *level* of training investment rather than its adjustability. Pointer to Internet
Appendix E / `@tbl-dynamic-phi`.

**Measured:** 1.67 pp − 0.22 stub = **net 1.45 pp (2.1%)**.

**Message impact:** low-to-moderate, *provided the four sentences are written carefully*. This
subsection is the repaired version of review fix B3/M3 — the earlier text contradicted its own
table. The repair is a *claim* (bias is signed downward; mechanisms survive), and the claim can
travel in four sentences; the two-period arithmetic that supports it cannot, and belongs in the
appendix anyway. **Referee-asks-it-back risk: low**, because every referee who cares will read the
Internet Appendix table. Risk if done badly: dropping the "upper bound" sign statement would reopen
exactly the objection PR #120 closed. Flag this as the one candidate where the stub must be drafted
before the cut is committed.

**Verdict: Recommended.**

---

### C4. H-regime illustration figures in §2.3 → Internet Appendix

Three standard real-options exhibits, measured individually:

| Item | Figure | Text | Total | Net after stub |
|---|---|---|---|---|
| C4a `fig-option-value` (Fig 1) + its 0.26 pp discussion | 0.52 | 0.26 | 0.78 | **0.65** |
| C4b `fig-comparative-statics` (Fig 2) + its 0.38 pp discussion | 0.61 | 0.38 | 0.99 | **0.85** |
| C4c `fig-lambda-option-value` (Fig 3) + its ≈0.30 pp discussion | 0.51 | 0.30 | 0.81 | **0.68** |

**C4a — option value vs NPV, the "value of waiting" shaded region.** This is the textbook
McDonald–Siegel picture. It illustrates smooth pasting, which Proposition 1 states analytically. A
Management Science referee does not need to be shown that option value exceeds NPV.
**Verdict: Recommended.** Keep one sentence ("the option premium factor β_H/(β_H − 1) ≈ 2.8 at
baseline") and point to the appendix.

**C4b — four-panel comparative statics in σ, α, γ, δ.** Fully duplicated by §3.5 plus
`@tbl-elasticities` in the Internet Appendix, which reports the same objects as numbers. Note also
that the δ panel is, per §3.2, a *rescaling* rather than an economic sensitivity — a referee who
reads carefully will see the panel is not what it looks like. **Verdict: Recommended.** Retain the
non-obvious signs in one sentence (γ non-monotone in the trigger; δ raises both trigger and
capacity) with a pointer to `@tbl-elasticities`.

**C4c — F_L(X) and the coefficient *C* against λ.** Weaker candidate: this figure is cited again in
§4.4 as the basis for the concavity-of-value-in-λ claim, which is testable prediction 3 (asymmetric
response to AI news) — a genuine contribution. It is also, per review fix A9, the figure produced in
*simple mode* and directly illustrating the disputed A₁ = 0 construction, so demoting it could read
as burying the construction the reviewers pressed on. **Verdict: Worth considering** — demote only
if the ~20% target is binding, and if so, say explicitly in §2.3.3 where it went.

**Combined C4a+C4b: net 1.50 pp (2.2%). All three: net 2.18 pp (3.2%).**

---

### C5. §3.3 archetype narrative detail → Internet Appendix C

**Moves:** (i) the four archetype-by-archetype sourcing paragraphs (Anthropic ARR vs collected
revenue, OpenAI CFO disclosure and the Epoch decomposition, Google Cloud vs Alphabet-wide revenue
and the 1.52× numerator choice, xAI/SpaceX standalone attribution) — 1.01 pp; (ii) the three
"types of evidence" blocks for φ̂ (*Executive statements*, *Firm-specific data*, *Industry
trajectory*) — 0.87 pp. `@tbl-sources` in Internet Appendix C already exists as the destination.
**Stays:** `@tbl-firms`; the "illustrative composites, not structural estimates" framing; the
non-harmonized-concepts caveat ("read one column at a time, not as cross-sectional moments"); the
±0.10 uncertainty on φ̂; the λ-inversion result with its two qualifications (this is a substantive
result and feeds §6); the inference-time-scaling caveat; the three "patterns emerge" observations.

**Measured:** 1.88 pp gross − 0.30 stub = **net 1.58 pp (2.3%)**.

**Message impact:** low. This is provenance, not economics, and it is the material a referee checks
in an appendix rather than reads linearly. **The (A2) disclosure is in §3.1–§3.2 and is untouched by
this cut.** **Referee-asks-it-back risk: low** — indeed, MS referees often prefer sourcing tables in
the e-companion. One caution: keep enough sourcing in the main text that the abstract's "calibration
to four AI lab archetypes" is not left unsupported; the retained table + caveats do that.

**Verdict: Recommended.**

---

### C6. `fig-lambda-timeline` (Figure 7) → delete or demote

**Moves:** Figure 7 and its 0.33 pp discussion. **Stays:** one clause in the §4 preamble ("at the
baseline λ = 0.10 there is a 39% chance of a switch within five years; the steep range
λ ∈ [0.05, 0.50] is precisely the range of market disagreement").

**Measured:** 0.78 pp − 0.10 = **net 0.68 pp (1.0%)**.

**Message impact:** none. Both panels are deterministic transforms of λ — *E*[*T*] = 1/λ and
1 − e^(−5λ). They contain no model output. This is the lowest information-density float in the
paper. **Referee-asks-it-back risk: nil.** A skeptical referee is more likely to note that a figure
was spent on plotting the exponential distribution.

**Verdict: Recommended** — and this one is a candidate for outright deletion rather than demotion.

---

### C7. `fig-firm-comparison` (Figure 6) → delete or demote

**Moves:** Figure 6 and its 0.26 pp discussion. **Stays:** the dispersion observation in one sentence
(it is already restated in the "Several patterns emerge" paragraph immediately below).

**Measured:** 0.78 pp − 0.10 = **net 0.68 pp (1.0%)**.

**Message impact:** none. Panel (a) plots the CapEx/Revenue row of `@tbl-firms` as bars — with a
broken axis, because xAI is at 20× — and the surrounding text then warns that the ratios "are not
directly comparable." Panel (b) plots two more `@tbl-firms` rows against each other. A figure whose
own caption and adjacent prose disclaim its comparability is a liability, not an exhibit.
**Referee-asks-it-back risk: nil.**

**Verdict: Recommended** — delete rather than demote; the table already carries the content.

---

### C8. §2.4.6 leader–follower asymmetry + Tullock properties → compress in place

Two blocks in the duopoly presentation that can be halved without demotion:

**C8a — "The leader–follower scale asymmetry" (1.03 pp of text, pp. 34.68–36.23).** The elasticity-wedge
arithmetic (α(2 − s_F) ≈ 0.475, d ln K\*/d ln α ≈ 24, the "reproduces K_F exactly" verification, the
170× ratio under re-optimization) is already in Internet Appendix B. **Keep in main text:** the bare
numbers (38× capacity, 44× trigger), the one-sentence mechanism, the statement that the magnitude is
a joint property of the Tullock form and the (A2) boundary rather than a robust prediction, and the
substantive reading ("the model's leader is a small, early, preemptive commitment, not the dominant
incumbent; claims about leadership concern the *timing* margin only"). That last paragraph is
review fix M8 and must stay. Compress to ~0.45 pp → **net 0.58 pp**.

**C8b — "Three properties of the Tullock specification" + the Cournot/fixed-pie paragraph (0.92 pp).**
The consolidated review flagged Cournot as appearing four times (§2.4.1, §5.5, Internet Appendix E,
plus the conventions block). Keep the revenue-inflation-under-asymmetry point (it is the honest
caveat on preemption magnitudes) and the pointer to the quantified fixed-pie variant; move the
quadratic-mean algebra and the Skaperdas regularity discussion. Compress to ~0.37 pp →
**net 0.55 pp**.

**Combined: net 1.13 pp (1.6%).**

**Message impact:** low. Nothing demoted; two dense passages become two tight ones. **Referee risk:
low**, provided the M8 substantive reading and the fixed-pie pointer survive verbatim.

**Verdict: Recommended.**

---

### C9. §1.1 Related literature → selective compression

Current 4.82 pp across five thematic blocks. PR #122 added the regime-switching-credit positioning
(Hackbarth–Miao–Morellec / Chen / Bhamra et al.) plus the Aguerrevere and OM anchors; that block and
the "Marginal contribution" paragraph are the two that do real work and must not shrink.

**Compressible:** the "R&D races and arms race dynamics" block (Loury, Reinganum, Harris–Vickers,
Grossman–Shapiro, ≈0.65 pp) reduces to two sentences plus a citation string without losing the
departure claim ("in standard races, pre-breakthrough spend is pure cost; here it earns inference
revenue"). The strategic-investment block carries three tangential threads —
Lambrecht–Perraudin private signals, Harrison–Kreps/Scheinkman–Xiong disagreement,
Grenadier–Malenko signaling, Bouis et al. *N*-firm — that can be compressed to a single sentence
each or moved to footnotes (≈0.4 pp). Realistic **net ≈ 0.95 pp (1.4%)**.

**Message impact:** low if the compression is confined as above. **Not recommended:** moving §1.1
wholesale to the e-companion. MS referees read positioning linearly and the review explicitly
required the credit-literature positioning be *visible*; burying it would look like the paper is
hiding from the priority question.

**Verdict: Worth considering** — real pages, but this is the slowest 1 page in the list to write and
the easiest to get wrong. Do it last.

---

### C10. §5.2 testable predictions — demote the "how to test" paragraph only

**Moves:** the second half of §5.2 (lines 26–31: default-probability and recovery regressions, event
studies around capability announcements, cross-sectional investment regressions, "data currently
scarce but becoming available") — ≈0.50 pp.
**Stays:** all four numbered predictions in full, and the closing "directional, small sample"
sentence.

**Measured:** **net ≈ 0.45 pp (0.7%).**

**Message impact:** low. The four predictions are the contribution; the research-design sketch is
not. **Referee risk: low-to-moderate** — some referees like an empirical roadmap, but the predictions
themselves already name the proxies (pre-training compute share; order of entry; timeline news).
**Not recommended:** demoting the numbered predictions themselves. Prediction 1 is the empirical face
of the two-faces credit result and prediction 4 the empirical face of Proposition 3(ii); both are
headline.

**Verdict: Worth considering.**

---

### C11. §4.3.2 — demote the default-option wedge algebra

**Moves:** the paragraph deriving why the levered curve lies *below* the unlevered one on the
aggressive side (the [R(X_D) + δK/r − A_eff X_D](X\*/X_D)^{β_L^-} bracket, the "eighteen times the
coupon claim" arithmetic, the belief-invariance-of-the-bracket argument, the 1.8%-vs-0.3%
capitalization) — 0.71 pp.
**Stays:** two sentences — the crossing exists, it is the shareholders' default option, it is worth
most to the firm entering closest to its boundary, and therefore "leverage's distinctive effect is
on tail risk, not on the mean." That conclusion is the review-fix-corrected statement (#114, #113)
and must stay.

**Measured:** 0.71 − 0.15 = **net 0.56 pp (0.8%).**

**Message impact:** low. This is a defensive derivation explaining a second-order feature of one
figure. **Referee risk: low** — but keep the *conclusion* in the main text verbatim, because the
honest restatement of the leveraged evaluator was a specific review fix.

**Verdict: Worth considering.**

---

### C12. §2.5 "Solution conventions and approximations" — **do not demote**

**Assessment.** 1.88 pp. This block is the direct product of review fix C1 and is arguably the
paper's best defense against the single most serious referee objection (the A₁ = 0 / piecewise
stopping problem). Demoting it would be self-harming: it is what converts "the paper overclaims
exactness" into "the paper defines a reduced-form model and quantifies its distance from the exact
one."

**However,** there is genuine duplication *between* §2.5 and its two upstream statements: the
"simplified form F_L ∝ X^{β_H}: what is exact and what is convention" block in §2.3.3 (1.11 pp) and
the "Conventions maintained in the equilibrium" block before Proposition 3 (0.64 pp). All three say
the unconditional-A_eff convention, the leader-scale convention, and the single-boundary
approximation. A disciplined de-duplication — §2.3.3 states the convention and forward-references;
the pre-Prop-3 block stays as the required forward reference but drops to a compact four-item list;
§2.5 remains the single full statement — is worth **≈0.60 pp** with no loss of content.

**Verdict: Not recommended** (as a demotion). **Recommended** as a ≈0.6 pp de-duplication that keeps
all three locations and all six load-bearing statements.

---

### C13. Minor de-duplications (aggregate ≈0.8 pp)

Not individually worth a package slot, but they add up and carry essentially zero risk:

- §2.4.3 "Capital structure" (0.72) restates the par-issuance/implicit-subsidy arithmetic that §2.5
  "Par debt issuance at an exogenous coupon" restates again — the 42%/23% numbers appear twice.
  ≈0.30 pp.
- §3.4's cost-normalization paragraph (0.44) restates §3.2's δ-rescaling argument. ≈0.20 pp.
- §6 Conclusion's future-research paragraph (≈0.9 pp on p. 69) lists five directions at
  paragraph length each; two sentences would do. ≈0.35 pp.
- §4.4 "Equity Valuation Sensitivity" (0.72) and §5.2 prediction 3 state the same concavity/news
  asymmetry claim. Merging §4.4 into prediction 3 saves ≈0.35 pp. *(Worth considering; slight cost
  in that §4.4 is where the concavity is established numerically.)*

**Verdict: Recommended** for the first three; the §4.4 merge is Worth considering.

---

## 5. Summary table

| # | Candidate | Net pp | % of main | Verdict |
|---|---|---:|---:|---|
| C1 | §4.1 scale-gap diagnostic → IA | **2.33** | 3.4% | Recommended |
| C2 | §4.2 credit-risk exposition → IA (keep numbers) | **2.29** | 3.3% | Recommended |
| C2-lite | — figure + displays only | 1.05 | 1.5% | (alternative) |
| C3 | §5.4 static-φ bias → IA (4-sentence stub) | **1.45** | 2.1% | Recommended |
| C4a | `fig-option-value` → IA | **0.65** | 0.9% | Recommended |
| C4b | `fig-comparative-statics` → IA | **0.85** | 1.2% | Recommended |
| C4c | `fig-lambda-option-value` → IA | 0.68 | 1.0% | Worth considering |
| C5 | §3.3 archetype sourcing + φ̂ evidence → IA C | **1.58** | 2.3% | Recommended |
| C6 | `fig-lambda-timeline` → delete | **0.68** | 1.0% | Recommended |
| C7 | `fig-firm-comparison` → delete | **0.68** | 1.0% | Recommended |
| C8 | Duopoly: asymmetry + Tullock compression | **1.13** | 1.6% | Recommended |
| C9 | §1.1 literature selective compression | 0.95 | 1.4% | Worth considering |
| C10 | §5.2 "how to test" paragraph → IA | 0.45 | 0.7% | Worth considering |
| C11 | §4.3.2 default-option wedge algebra → IA | 0.56 | 0.8% | Worth considering |
| C12 | §2.5 conventions → demote | — | — | **Not recommended** |
| C12′ | §2.5/§2.3.3/pre-Prop-3 de-duplication | 0.60 | 0.9% | Recommended |
| C13 | Minor de-duplications (3 items) | 0.85 | 1.2% | Recommended |
| — | §1.1 → e-companion wholesale | (4.8) | 7.0% | **Not recommended** (#122) |
| — | §5.2 numbered predictions → IA | (1.1) | 1.6% | **Not recommended** (headline) |

---

## 6. Packages

### Package A — "Free pages" (≈10%): 7.05 pp → main text 61.9 pp

C1 + C3 + C4a + C4b + C6 + C7 + C12′ + C13
= 2.33 + 1.45 + 0.65 + 0.85 + 0.68 + 0.68 + 0.60 + 0.85 = **8.09 pp (11.7%)**
*(drop C13 to land at 7.24 pp = 10.5% if a tighter 10% is wanted)*

**Risk assessment.** Essentially none. Every item is either a figure with no model content
(C6, C7), a textbook illustration duplicated by an appendix table (C4a, C4b), a subsection that
disclaims its own interpretive reach (C1), a repaired-but-appendix-supported argument that travels
in four sentences (C3), or pure de-duplication (C12′, C13). No headline mechanism loses main-text
support: φ\* stays fully in §2.2.1/§2.3/Prop 1/Prop 3(ii); faith-based survival stays fully in
§2.4.4/Prop 2 and §4.2; Dario's dilemma stays fully in §4.3; duopoly preemption stays fully in
§2.4.6 with Figure 5. The only item requiring drafting care is C3's four-sentence stub, which must
retain the *sign* of the bias and the "mechanisms attenuate but survive" claim. Three figures drop
from the main text (10 → 7), which if anything improves the exhibit-to-content ratio. This package
is the one I would run regardless of the length target.

---

### Package B — Recommended target (≈16%): main text 58.0 pp

Package A + C2 + C5
= 8.09 + 2.29 + 1.58 = **11.96 pp (17.3%)** → **main text ≈ 57.0 pp, blind manuscript ≈ 63 pp**

*(Using C2-lite instead of C2 gives 10.72 pp = 15.5% → main text ≈ 58.3 pp.)*

**Risk assessment.** Low-to-moderate, concentrated in one place: C2 removes the credit-spread and
default-probability figure and formulas from the main text, and Proposition 2 is a headline result.
The mitigation is that the mechanism, the threshold φ̲ ≈ 0.18 / φ̃ ≈ 0.32 characterization, and the
faith-based survival argument all live in §2.4.4 and are untouched; what moves is the *numerical
illustration*, and the retained paragraph keeps every published number (0/12/41/97 bps;
0.63%/1.80%/4.85%/12.98%) plus the two-faces PD/LGD contrast that the paper claims as novel and that
§5.2 prediction 1 tests. A finance referee may ask for the figure back; that is a one-line response
("Figure IA-x") rather than a re-derivation. C5 is low-risk — sourcing detail migrating to
`@tbl-sources`, where it arguably belonged — but check on the redraft that the abstract's
"calibration to four AI lab archetypes" still reads as supported by what remains, and that the §3.1
and §3.2 (A2) disclosures are untouched (they are in different subsections, so this is a
verification step, not a design risk). **This is the package I would recommend.** It hits the
author's stated 15–20% band, leaves the e-companion at ≈49 pp (from 36), and does not require
compressing the literature review or the propositions.

---

### Package C — Maximum defensible (≈21%): main text 54.5 pp

Package B + C4c + C8 + C9 + C10 + C11
= 11.96 + 0.68 + 1.13 + 0.95 + 0.45 + 0.56 = **15.73 pp (22.8%)** → main text ≈ 53.3 pp

*(Drop C9 — the literature compression — to land at 14.78 pp = 21.4%, main text ≈ 54.2 pp, which I
would prefer.)*

**Risk assessment.** Moderate, and the marginal pages are the expensive ones. Three specific
exposures. First, C9 touches §1.1, which grew deliberately in PR #122 to answer a priority question
about regime-switching credit models; compressing the *adjacent* blocks is safe, but the edit is
delicate and a careless pass could re-open A-issue M7 — this is why I would drop C9 first. Second,
C4c demotes the figure that visualizes the disputed A₁ = 0 construction; after two reviewers pressed
on exactly that construction, removing its only picture from the main text is a bad look unless
§2.3.3 says plainly where it went, and unless §4.4 (or §5.2 prediction 3) still states the concavity
result it supports. Third, C8's compressions run through the paragraph that PR #123/M8 required —
the "the model's leader is not the dominant incumbent" reading — which must survive verbatim even as
the elasticity arithmetic around it goes. C10 and C11 are safe. Net: this package is achievable, but
it converts the shortening exercise from mechanical demotion into judgment-heavy rewriting of blocks
that were themselves written to satisfy referees. If the target is a hard 20%, run Package B plus
C8 + C10 + C11 + C4c (= 14.78 pp, 21.4%) and leave the literature review alone.

---

## 7. Practical notes

- **Where things land.** Internet Appendix sections already exist for every destination: C1 → a new
  short section (or E, Robustness); C2 → B or a new credit-risk section; C3 → E (`@tbl-dynamic-phi`
  is already there); C4a/C4b/C4c → B; C5 → C (`@tbl-sources` already there); C8/C11 → B. The
  e-companion grows from 36 pp to roughly 49 pp under Package B. INFORMS does not page-limit the
  e-companion.
- **Cross-references.** `index.qmd` and `index-blind.qmd` must both be updated if any include is
  added or removed (`paper/AGENTS.md`), and `split_blind_pdf.py` cuts at the `_appendix-cover.qmd`
  page, so moved content must land *after* that cover for the split to work.
- **Figure code.** Demoting a figure changes nothing in `src/ai_lab_investment/figures/paper.py`;
  only the `![...](...)` block moves. Deleting `fig-lambda-timeline` / `fig-firm-comparison`
  outright would make their `create_*` functions dead — check `tests/` and
  `paper/generate_figures.py` before removing the generators (the AGENTS file records 11 figure PDFs
  with 10 referenced, so `fig_sample_paths` is already precedent for keeping an unreferenced
  generator for the slides).
- **Slides.** `slides/` reuses several of these figures; demotion in the paper has no effect there.
- **Re-measure after cutting.** Reflow can move the total by ±1 page in either direction; re-run the
  bbox measurement on the rebuilt blind PDF rather than trusting the arithmetic.
