# Prose review — *Investing in Artificial General Intelligence*

Reviewer: Claude (prose-review skill). Read-only pass over `paper/index.qmd`, `index-blind.qmd`, `_introduction.qmd`, `_literature.qmd`, `_model.qmd`, `_calibration.qmd`, `_valuation.qmd`, `_discussion.qmd`, `_conclusion.qmd`, `_appendix-cover.qmd`, `_appendix.qmd`, plus every figure and table caption. Eleven parallel sub-agents (one per section slice, one for captions, one cross-cutting) checked against `.claude/skills/finance-writing/reference.md` and the house rules in `paper/AGENTS.md`. No numbers were traced to code, no exhibits recomputed, no Lean checked; where the truth of a claim was in doubt the finding says so.

Findings are numbered continuously, ordered by position in the paper, and graded **substantive** / **wording** / **minor**.

---

## Executive summary

The paper is well written at the sentence level in the sections that matter most: the model derivation is orderly, the Internet Appendix is unusually honest about what is proved versus computed, and the terminology is broadly stable. The problems are concentrated in five places.

**1. The em-dash budget is not overrun, it is abandoned.** A single rendered manuscript contains **249 prose em-dashes** against a house budget of five, including one in the abstract, where the rule is zero. The construction has become the paper's default connector: it does apposition, parenthesis, contrast, and consequence interchangeably, so it no longer signals anything. This is the single largest mechanical change the paper needs, and it touches every section file. Density is worst in `_model.qmd` (78) and `_appendix.qmd` (72), but the ones to fix first are the 60-odd lines carrying *two or more* in one sentence.

**2. Claim strength drifts upward whenever the paper summarizes itself.** Individual sections hedge carefully, then the abstract, introduction, and conclusion state the same results flatly. "Drives cross-sectional variation" (abstract), "no subset of existing models can generate" (intro), "reveals that this cost is asymmetric" (conclusion), "the observed aggressive investment patterns of frontier AI labs are *rational*" (valuation), "would improve market efficiency" (discussion). The pattern is consistent enough to be worth a single dedicated pass: every summary sentence should be checked against the hedge attached to the result where it is derived.

**3. The calibration section reads, in places, as estimation.** "Estimated from", "point estimate", "these estimates carry substantial uncertainty", "market betas of 1.5–2.5" for private firms, and a `@tbl-firms` header row naming Anthropic, OpenAI, Google, and xAI outright, against body prose that is careful to say "Anthropic-like archetype". A referee reading the table before the text will conclude the paper claims to calibrate four named companies. The fix is small and mostly lexical.

**4. Two headline numbers are quoted inconsistently, and one stub misstates its Internet Appendix section.** The **preemption discount** means $X_P/X_L^{\text{mono}}$ (0.57) in `_calibration.qmd` and $1-X_P/X_L^{\text{mono}}$ (43%) in `_model.qmd`, so the same phrase rises when preemption weakens and rises when it strengthens, twenty lines apart. Two different five-year default probabilities at $\ell=0.40$ (4.85% and 5.04%) are quoted four paragraphs apart against baselines of 0.63% and 0.64%, with the different evaluation points stated for only one of them. And the Internet Appendix G stub in `_valuation.qmd:6` says the 25–50% band "survives ±25% perturbations" when Internet Appendix G itself reports 19–59% under those perturbations. These are prose-level inconsistencies, not necessarily arithmetic errors; each needs one check against the exhibit.

**5. Redundancy across abstract / introduction / conclusion.** The faith-based-survival mechanism is stated near-verbatim three times, the model-ingredient list three times, "pinned down by beliefs, not competitive position" five times, and the "three core tensions" frame twice. The conclusion currently opens by re-listing the model's ingredients rather than by stating what the paper found.

**Sections ranked by how much rewriting they need**

| Rank | Section | Why |
|---|---|---|
| 1 | `_calibration.qmd` | Estimation vocabulary throughout; `@tbl-firms` names real firms; two internal contradictions (harmonized vs not harmonized concepts; "read columns one at a time" vs a cross-column "patterns emerge" paragraph) |
| 2 | `_discussion.qmd` | Welfare claims against an uncharacterized social optimum; conjectures stated in the indicative; a policy claim (disclosure improves market efficiency) the model cannot support |
| 3 | `_conclusion.qmd` | Opens by restating the abstract; five em-dashes in 26 lines; quotes reduced-model percentages without the qualification §5 attaches to them |
| 4 | `_valuation.qmd` | Novelty claim; several results restated three times; the figure caption reproduces four paragraphs of body text |
| 5 | `_model.qmd` | Structurally sound; needs the em-dash pass, Assumption 1 moved ahead of the results that use it, and one economic (not algebraic) explanation of role-invariance |
| 6 | `_introduction.qmd` / `_literature.qmd` | Question arrives on page 3; one overclaim that its own literature review contradicts; six bold run-in labels |
| 7 | `_appendix.qmd` | Strongest writing in the paper; needs the Lean scope sentence narrowed, the QED box removed from Numerical Finding 1, and its own em-dash pass |

---

## Findings

### Title and abstract

**1. [substantive] `index.qmd:2`, `index-blind.qmd:18`** — "Investing in Artificial General Intelligence". The title names a topic, not the object of study, and read cold suggests investing *in AGI as an asset*. The paper models AI labs' irreversible capacity choice and its split between training and inference under uncertain AGI timing. Consider "Capacity, Training, and Default in the Race to AGI" or "Investing under AGI Uncertainty: Irreversible Capacity and the Training-Inference Split".

**2. [substantive] `index.qmd:24`, `index-blind.qmd:32`** — "lowering the default boundary---the hope of AGI keeps the firm alive". The one em-dash in the abstract, where the house rule is zero. Replace with a colon.

**3. [substantive] `index.qmd:26`, `index-blind.qmd:34`** — "heterogeneity in beliefs about AI timelines **drives** cross-sectional variation in investment behavior". Asserts an empirical causal relation a four-archetype stylized calibration cannot establish. Rewrite: "shows how heterogeneity in beliefs about AI timelines *can generate* cross-sectional differences in investment behavior."

**4. [substantive] `index.qmd:25`** — "conservative underinvestment is costlier in expected value, but aggressive overinvestment carries substantially higher tail default risk". Stated as a general model property; it is Numerical Finding 1 at baseline parameters. Add "In the calibrated model," and drop the unquantified "substantially".

**5. [wording] `index.qmd:22`** — "diminishing returns calibrated to AI scaling laws". Returns are not calibrated; a curvature parameter is. Rewrite: "diminishing returns to capacity, with the curvature parameter calibrated to AI scaling laws."

**6. [wording] `index.qmd:24-25`** — "A 'faith-based survival' mechanism **emerges**" / "An asymmetric dilemma **arises**". Consecutive sentences with the same construction, both presenting results as self-occurring rather than as model implications. Recast with the model as the actor.

**7. [minor] `index.qmd:20-26`** — abstract runs 169 words against the guide's 100–150 target, and the first sentence states the setting rather than the question. Merge the two openers so the decision problem leads; findings 44 and 47 identify sentences that can go.

### Introduction

**8. [substantive] `_introduction.qmd:12`** — "structural credit models [@leland1994corporate] handle leverage and default but not regime-switching growth options with endogenous capacity allocation". Contradicted by the paper's own literature review at `_literature.qmd:23`, which concedes that "a well-developed branch of this literature already embeds regime switching in the Leland framework" and that "Proposition 2 is therefore not the first default boundary derived in a regime-switching environment". Rewrite to name the actual gap: those models take the size of the growth option as exogenous rather than as a capacity-allocation choice.

**9. [substantive] `_introduction.qmd:14`** — "producing mechanisms ... that **no subset of existing models can generate**". An absolute non-existence claim over the literature; unsupportable and unnecessary, since `_literature.qmd:29` already does the comparison properly. Rewrite: "that the component models do not generate individually."

**10. [substantive] `_introduction.qmd:29`** — "aggressive overinvestment carries higher downside risk than conservative underinvestment". Inverts the headline relative to the abstract, §5, and §7, all of which lead with the expected-value asymmetry running the other way. The paper's most-quoted pair (26% vs 6%) never appears in the introduction at all. Rewrite: "Conservative underinvestment costs roughly 26% of value against 6% for a symmetric overinvestment, but overinvestment raises the five-year default probability nearly eightfold; the dilemma is two-sided."

**11. [substantive] `_introduction.qmd:21`** — "the leader invests at a trigger roughly 43\% below the monopoly benchmark". Unhedged here; `_model.qmd:404-405` says the number is "conditional on the leader-scale convention, and strongly so", rising to 86% when the leader's scale is re-optimized, and that "the magnitude is not" robust. Either attach the convention or keep only the sign in the introduction.

**12. [substantive] `_introduction.qmd:26-29`** — Dario's dilemma is presented with no indication of its evidentiary status, while the first result is explicitly flagged as analytical at line 20. Per `paper/AGENTS.md` this is Numerical Finding 1. Add the label, and soften "illustrates that the asymmetry is substantial" to "suggests the asymmetry can be substantial at the calibrated parameters".

**13. [substantive] `_introduction.qmd:24`** — the faith-based-survival paragraph mentions only the default-boundary side, omitting the loss-given-default side that the abstract carries ("that hope is worthless to creditors in bankruptcy") and that `_valuation.qmd:12` calls novel. Add the clause so the claim is set up before it is asserted.

**14. [substantive] `_introduction.qmd:3-12`** — the research question does not arrive until line 12, after roughly 470 words of industry context, technology description, and executive quotation. State it in one sentence at the end of the first paragraph, then let paragraphs 2 and 3 supply only what the question needs.

**15. [wording] `_introduction.qmd:3`** — "the defining capital allocation event of the 2020s". Unsupported superlative opening. Rewrite: "one of the largest concentrated capital commitments of the 2020s." Also hyphenate "capital-allocation event".

**16. [wording] `_introduction.qmd:21, 29`** — "but, **strikingly**, not on the allocation margin"; "a **sharp**, testable implication". The paper grading its own results; the reader decides what is striking. Delete both.

**17. [substantive] `_introduction.qmd:4-5`** — "committed over \$200 billion in 2024 alone". The attached footnote cites Amazon FY2026 guidance, the Alphabet Q4 2025 release, and Microsoft FY2026 Q2, none of which covers a 2024 aggregate. Source it or lead with the sourced 2026 projection.

**18. [substantive] `_introduction.qmd:32`** — "as of 2025, the vast majority of the world's largest training runs are conducted by a handful of laboratories". A quantitative concentration claim with no citation, in a paper dated 2026. Cite a compute-tracking source or hedge.

**19. [wording] `_introduction.qmd:26`** — "The asymmetry of this trade-off is captured by ... Amodei's observation". The 67-word quotation describes only the overbuilding side; the underinvestment side is absent, so it does not illustrate an asymmetry. Trim the quotation and reframe it as the overinvestment case.

**20. [structure] `_introduction.qmd:10`** — one 205-word paragraph carries time-to-build, reallocation adjustment costs, two executive quotations, the definition of AGI, and the dispersion of timeline forecasts. It opens on "These facilities take years to build", which the paragraph never uses again. Split into a technology paragraph and a belief-dispersion paragraph.

**21. [structure] `_introduction.qmd:17-20`** — the "First" result opens with three sentences of setup before the result arrives in one clause. Lead with the result.

**22. [wording] `_introduction.qmd:41`** — a 58-word sentence carrying the preemption result, a contrast, a mechanism, and a three-part conclusion, with an em-dash pair inside. Split at "but".

**23. [terminology] `_introduction.qmd:18-19`** — "the current (low) regime" / "the post-AGI (high) regime" / "the **transformative AI regime**". The last appears only here. Introduce the L and H labels once at line 18 and use "post-AGI" thereafter (see finding 68).

**24. [terminology] `_introduction.qmd:18`** — "a Tullock contest" used with no gloss. Add: "in which a firm's revenue share equals its share of industry inference capacity."

**25. [terminology] `_introduction.qmd:26-27`** — line 26 defines Dario's dilemma as investing on a belief that "differs from reality"; line 27 describes investing "as though AGI is less likely than it truly believes", a different comparison (distorted policy under correct beliefs). Fix on one framing: belief versus the true arrival intensity $\lambda$. Also "dilemma is *the cost*" is a category mismatch; prefer "I quantify the cost of *Dario's dilemma*".

**26. [minor] `_introduction.qmd:38-43`** — the roadmap never mentions the Internet Appendix, although `_literature.qmd:26` already forward-references Internet Appendix G. Add a closing sentence.

**27. [minor] `_introduction.qmd:10`** — "range from X [cite], Y [cite], **and** Z ... **to** W". The interior "and" breaks the from/to pair. Recast as "run from X and Y, through Z, to W."

**28. [minor] `_introduction.qmd:10`** — three intensifiers in one paragraph ("starkly", "precisely", "profoundly") plus "so acute". Cut.

### Literature (`_literature.qmd`, included by the introduction)

**29. [wording] `_literature.qmd:5, 11, 14, 22, 25, 28`** — six `**Bold label.**` run-in pseudo-headings. `paper/AGENTS.md` forbids these in `_introduction.qmd` and does not list `_literature.qmd`, but the file is *included by* the introduction and renders as part of it, so the intent of the rule reaches it. Judgment call: either promote to `####` subheadings or delete the labels and let each paragraph's first sentence carry the topic.

**30. [substantive] `_literature.qmd:26`** — "the Baumol mechanism in @aghion2019artificial ... **is the aggregate counterpart of** the diminishing returns $\alpha<1$ imposed at the firm level here". Asserts an equivalence between a general-equilibrium task-composition result and an imposed firm-level curvature parameter. Hedge to "plays a role loosely analogous to".

**31. [substantive] `_literature.qmd:17`** — "the frontrunner invests more aggressively---**analogous to** the leader's earlier entry in ... Proposition 3". Reinganum's frontrunner is defined by technological position, this paper's leader by endogenous investment timing. Hedge, and say the leader's position is itself the outcome of the timing game.

**32. [structure] `_literature.qmd:12, 23, 26, 29`** — four single paragraphs of 295, 340, 251, and 247 words. Line 23 alone covers Merton/Leland, the regime-switching credit branch, the positioning of Proposition 2, what those models lack, the $\phi$ mechanism, investment-with-default papers, and the VC reinterpretation of "default". Split each at its natural seam.

**33. [structure] `_literature.qmd:3`** — "I organize the review around **the four building blocks**", followed by five bold blocks. Make the count match, or fold R&D races into strategic investment.

**34. [wording] `_literature.qmd:9`** — a 54-word sentence chaining an em-dash aside, a relative clause on payoff timing, and a second independent claim about joint pricing with default. Split into three.

**35. [wording] `_literature.qmd:23`** — "Put differently, the regime-switching credit literature makes the default boundary depend on the state; the present model makes it depend on how the firm has positioned itself for the state it is waiting for." This is the sharper formulation; delete the preceding "What they do not contain..." sentence rather than keeping both.

**36. [wording] `_literature.qmd:26`, `_introduction.qmd:5`** — "a **comprehensive** framework", "a **comprehensive** treatment". On the guide's remove list. Say what the cited work does instead.

**37. [minor] `_literature.qmd:12`** — "@huisman2015strategic **is** the closest strategic investment paper: **they** study..." Singular verb, plural pronoun, same referent. Recast: "The closest strategic-investment paper is @huisman2015strategic, who study..."

**38. [terminology] `_literature.qmd:12`** — "the antecedent of the **training-beta** prediction in @sec-discussion". First and only use in these files, undefined. Gloss or drop.

**39. [terminology] `_literature.qmd:6, 23`** — the L and H labels are used throughout the literature review but introduced nowhere before it. See finding 23.

**40. [structure] `_literature.qmd:6, 23, 26` and `_introduction.qmd:5`** — footnotes that list papers without connecting them to a claim (@bloom2009impact, @jovanovic2005general, @sundaresan2015dynamic, @bolton2019investment, @katz1986technology, @farrell1986installed, @babina2024artificial, @eisfeldt2023generative). Keep the citations that bear on an adjacent argument; delete the catalogue.

### Model (`_model.qmd`)

**41. [substantive] `_model.qmd:108-119`** — Assumption 1 is stated *after* the results that use it: the H-regime option value (91–98), the trigger (100–104), and a numerical claim at baseline (106) all precede the admissibility conditions they require, and (A2) is then quoted verbatim again inside Proposition 1 at line 126. Move Assumption 1 to the head of the Single-Firm Benchmark and replace the repetition with "under (A2)".

**42. [substantive] `_model.qmd:426`** — `Solution conventions and approximations` sits *after* the propositions that rely on it, and line 347 already refers to "the solution conventions collected before Proposition 3" when they have not yet appeared. Move the section ahead of the duopoly, and let 347 and 384 cite rather than restate it.

**43. [substantive] `_model.qmd:345-381`** — the Preemption equilibrium subsection never states plainly that the duopoly equilibrium has **no closed form** and is solved numerically. The reader arrives from three displayed closed forms; the hedging is scattered across "verified numerically" (354), "smooth pasting at each evaluation" (363), and the taxonomy sentence at 424. Add one explicit sentence after line 347 naming the fixed-point and root-finding procedure and stating that the reported triggers, capacities, and preemption discount are numerical solutions.

**44. [substantive] `_model.qmd:392, 406`** — Proposition 3(ii) carries the entire explanation of role-invariance inside the italicized statement, and it is algebraic ("the common multiplier $s_i(2-s_i)$ cancels exactly") rather than economic; the body never explains it in words. Add a body paragraph: because both regimes' contests run over the *same* capacity scaled by $\phi$ and $1-\phi$, a change in $\phi$ moves the L- and H-regime shares by the same proportional factor, so competitive position enters the marginal value of training and of inference identically and drops out of their ratio. Rivalry changes how much a firm builds and when, not how it splits what it builds.

**45. [substantive] `_model.qmd:406`** — "In this solution, competition affects **timing** rather than **scale**." The very next paragraph is titled "The leader-follower scale asymmetry" and reports a factor-38 capacity gap. The claim holds only for the leader, and only by convention. Restrict it.

**46. [substantive] `_model.qmd:354`** — "Both conditions are verified numerically **for all parameterizations**". Proposition 3(i) at line 390 says the honest thing ("at every parameterization tested"). Match it.

**47. [substantive] `_model.qmd:373`** — "the unconditional approach preserves the key economic forces while maintaining tractability". Unsupported self-endorsement, and it sits against @sec-conventions, which reports the convention displaces trigger levels by 53–96%. Rewrite to state both.

**48. [substantive] `_model.qmd:401`** — "The leader invests strictly earlier than the monopolist **for all volatility levels**". A numerical result on the grid $\sigma\in[0.20,0.30]$. Rewrite: "Over the admissible volatility grid".

**49. [substantive] `_model.qmd:412` vs `:418`** — "The asymmetry is **not a numerical accident**" followed six lines later by "is not a robust prediction ... reflects the baseline's proximity to the (A2) boundary". The *direction* follows from the contest structure; the *magnitude* does not. Say so, and drop the ceremonial "it is worth stating plainly".

**50. [substantive] `_model.qmd:51`** — "This regime-dependent revenue structure captures a **fundamental** asymmetry in AI infrastructure: today, inference capacity determines revenue (**you** must serve demand)". Promotional adjective, second person, and a modelling assumption asserted as a fact about the world. Recast as an imposed assumption.

**51. [substantive] `_model.qmd:18`** — "This asymmetric regime structure captures the *irreversibility of AI progress*: capabilities, once demonstrated, do not disappear." An absorbing-state assumption presented as established fact. Rewrite: "The absorbing high regime *assumes* irreversible AI progress: the model rules out a reversal of demonstrated capabilities."

**52. [substantive] `_model.qmd:188`, `:192-193`** — "consistent with **the observation that** AI labs with more optimistic timeline beliefs invest more aggressively"; "below the range of **market disagreement**"; "**confirming** that the mechanism operates through the continuation value channel". Nothing in the paper measures lab-level beliefs or compute allocation; the $\lambda$ range comes from three executive statements, not market prices; and a plot of the model's own coefficient illustrates rather than confirms. Fix all three.

**53. [substantive] `_model.qmd:205, 222, 421`** — "The Tullock specification captures **the essential feature** of AI compute competition"; "consistent with AI markets where the leading model captures a disproportionate share of API revenue"; "a **defensible reading** of an industry in which early movers have committed comparatively small amounts of compute". Three uncited institutional claims doing interpretive work. Cite or hedge each. *Check against `references/` for citable sources.*

**54. [substantive] `_model.qmd:228`** — "The training fraction $\phi$ introduces a new **strategic dimension**". Proposition 3(ii) then finds the opposite: the optimum is role-invariant, i.e. not strategic. Recast so the setup does not contradict the result.

**55. [substantive] `_model.qmd:428`** — "The closed forms above rest on **four** solution conventions, collected here so that a reader can track which objects are exact and which are not." At least two further approximations sit outside the four: the omitted default-option term in the follower's entry payoff (452) and the omitted abandonment option (footnote at 327). Either extend the inventory or say explicitly that two smaller approximations are recorded elsewhere.

**56. [substantive] `_model.qmd:130, 188, 191`** — $\lambda$ slides between an exogenous arrival intensity (its definition at line 15) and a subjective firm belief ("more optimistic beliefs", "firms with higher arrival-rate beliefs"). Introduce the reading once, explicitly, then use "higher $\lambda$" consistently.

**57. [structure] `_model.qmd:136-143`** — the duopoly-convention paragraph and the H-regime comparative statics interrupt the single-firm derivation, and 136–140 uses $s_i^L$, $s_i^H$, leader, and follower before any is defined. Move 136–140 to the head of @sec-duopoly and 142–143 to just after line 106.

**58. [structure] `_model.qmd:302-307`** — the `fig-default-boundaries` discussion uses *leader*, *follower*, $X_F^*$, and $X_P$ 45 to 78 lines before they are defined. Move the figure paragraph after the Preemption equilibrium subsection, or add a forward-defining clause.

**59. [structure] `_model.qmd:383-385` vs `:426-458`** — the four solution conventions are stated twice at near-equal length. Reduce 384 to a one-sentence pointer, keeping only the locally relevant sentence at 385.

**60. [structure] `_model.qmd:250-256, 299, 366, 454-458`** — "leverage is a stress-test parameter, not a capital-structure result" is made five times, with the implicit-subsidy arithmetic given twice. State it once in Capital structure with a pointer, keep the short qualification on Propositions 2(i)/3(iv), delete the rest.

**61. [structure] `_model.qmd:121-132`** — interpretation and appendix navigation embedded inside the formal statement of Proposition 1 ("Note that $K^*$ is independent of $\phi$: ... (see Internet Appendix A, Step 4)"). Move the mechanism, the pointer, and the economic reading into the paragraph after the proposition.

**62. [structure] `_model.qmd:293, 295`** — Propositions 2(ii) and 2(iii) carry calibration output ($\Omega\approx0.22$, $\underline{\phi}\approx0.18$, $\tilde{\phi}\approx0.32$, $\phi^*\approx0.70$, the $\lambda\gtrsim0.034$ crossing) and an empirical-interpretation sentence inside the italicized statements. Move both out.

**63. [structure] `_model.qmd:220-227`** — "Three properties of the Tullock specification **under asymmetry**" whose first property is the *symmetric* benchmark; and the Cournot detour at 226 separates the concern raised at 225 from its resolution at 227. Retitle and reorder. Line 227 (567 characters, one sentence) should also split.

**64. [structure] `_model.qmd:174, 176, 267`** — three sentences carrying four or more independent claims each; the 267 footnote is 1,049 characters and duplicates a result stated in the body at 272 and again at 451. Split each; cut the footnote to the coupled-ODE argument.

**65. [terminology] `_model.qmd:269-293`** — the section that derives the paper's headline mechanism never uses the paper's own name for it: it is "the continuation-value channel" (278, 293) and "the $A_{\text{eff}}$-channel" (285, 293), while the introduction calls it the *training-survival channel*. Name it once at line 270 and use one label.

**66. [terminology] `_model.qmd:358`** — $X_L$ is introduced as the leader's trigger and never used again; the leader's trigger is $X_P$ everywhere afterward, while subscript $L$ simultaneously carries $X_L^{\text{mono}}$ and the low regime. Delete the $X_L$ sentence. Relatedly the follower's trigger appears as both $X_F$ and $X_F^*$; settle on one.

**67. [terminology] `_model.qmd:45, 51, 65` vs `:70`** — "training quality" and "training compute $\phi K$" for the same object. Only $\phi K$ is a model object. Use it throughout, and if "training quality" is the intended economic interpretation, say so once.

**68. [terminology] `_model.qmd:192`, `_conclusion.qmd:9`** — "the **post-adoption** option value", "a **post-adoption** world". A fourth name for regime H, alongside "high regime", "post-AGI", and "transformative AI regime". Standardize on post-AGI.

**69. [terminology] `_model.qmd:35` vs `:70, 85-87, 106`** — the stated domain $\phi\in(0,1)$ excludes the boundary cases the text then evaluates ($\phi=0$ at 70, both endpoints at 85–87, $\phi=1$ at 106). Define $\phi\in[0,1]$ and keep $(0,1)$ only where differentiability is invoked.

**70. [terminology] `_model.qmd:27` vs `:43`** — $\alpha$ glossed as "the revenue elasticity ... in the contest functions below" and as "diminishing returns to inference capacity", and in @eq-revenue-H applied to *training* capacity with no gloss. Use one gloss and fix the forward reference.

**71. [terminology] `_model.qmd:152`** — $B_H$ appears for the first time and is never defined. Define it where the H-regime option value is introduced.

**72. [terminology] `_model.qmd:115`** — Assumption (A3) uses $\beta_L^+$ and "the L-regime characteristic equation", neither defined until line 159, forty lines later.

**73. [terminology] `_model.qmd:172`** — "the **extended region**", used once and never defined; the reader must infer it means $X>X_H^*$.

**74. [terminology] `_model.qmd:354` vs `:390, 392`** — "verified numerically" vs "verified computationally" for the same status, in a paper whose result taxonomy turns on that distinction. Pick the taxonomy table's term.

**75. [terminology] `_model.qmd:84` vs `:187`** — "**Remark** (Nesting)" unnumbered, "**Remark 1** (Role of $\lambda$)" numbered. Number both or neither.

**76. [structure] `_model.qmd:188`** — Remark 1 announces "two effects", gives "First..." and "Second...", then adds a third (higher $\lambda$ raises the option value monotonically). Fold it in or announce three.

**77. [wording] `_model.qmd:28`** — "Two simplifying assumptions **should be flagged** at the outset". Passive in a first-person section. "I make two simplifying assumptions."

**78. [wording] `_model.qmd:82`** — "weighted by the **probability-rate** ... **before the discount factor drives the value to zero**". Coined hybrid plus a loose gloss. "weighted by $\lambda/(r-\mu_L+\lambda)$, the discounted probability that the regime switch arrives."

**79. [wording] `_model.qmd:357`** — "By symmetry, both firms are identical ex ante." Circular. "The two firms are identical ex ante."

**80. [wording] `_model.qmd:369-374`** — the same point ("the leader must account for the follower's entry") made three times, once with "account for the fact that". Fold into one sentence.

**81. [wording] `_model.qmd:436, 447, 405`** — "The displacement of levels is large and the displacement of value is small"; "The convention ... is not to be read as a magnitude" (a convention is not a magnitude; the preemption discount is); "the direction of the sign" (redundant). Recast each.

**82. [minor] `_model.qmd:142`** — "raises *both* the trigger and the optimal capacity---**which** is a rescaling of the capacity unit". Ambiguous referent, and the sentence already carries two findings plus a semicolon. Split. "Sharply" a line earlier is vague; give the elasticity or cite @tbl-elasticities.

**83. [minor] `_model.qmd:70`** — past-tense relative clauses ("allocated", "invested") against present-tense main verbs ("generates", "captures"). Put both in the present.

**84. [minor] `_model.qmd:217`** — "the capability of **your** *models*". Second person in formal manuscript text.

**85. [minor] `_model.qmd:261-262`** — dangling participle ("Following @leland1994corporate, the optimal default boundary is obtained...") and a non-parallel three-item list.

**86. [minor] `_model.qmd:7, 181`** — $X$ is never given an interpretation or a unit, yet the paper quotes levels such as $X^*\approx0.0047$. Add one sentence saying what $X$ measures, or point to the normalization in @sec-calibration.

**87. [minor] `_model.qmd:173, 14, 25, 91`** — "with wide margin" (needs "a"); "the current state **where**" (→ "in which"); noun strings "data center site preparation", "capacity procurement"; "real options form" (hyphenate as a modifier).

### Calibration (`_calibration.qmd`)

**88. [substantive] `_calibration.qmd:65`** — `@tbl-firms` header row reads `| Archetype | Anthropic | OpenAI | Google | xAI |`, so the revenue, CapEx, leverage, and WACC rows below read as those firms' actual figures, while the body is careful to say "the Anthropic-like archetype". Relabel the row entries `Anthropic-like`, `OpenAI-like`, `Google-like`, `xAI-like`.

**89. [substantive] `_calibration.qmd:74, 82, 87, 91`** — "Training fractions **estimated from** executive statements"; "The training fraction $\hat\phi$ **estimates**"; "These **estimates** carry substantial uncertainty"; "the **point-estimate** ordering". Estimation vocabulary for assigned inputs, contradicting line 4 ("not to structurally estimate") and line 7 ("inferred from incomplete data"). Replace throughout with "set from", "values", "baseline ordering".

**90. [substantive] `_calibration.qmd:77` vs `:79`** — "The same sector-specific revenue concept applies to all archetypes" followed two lines later by "the revenue and CapEx concepts **are not harmonized** across the four archetypes". Direct contradiction. Keep 79 and rewrite 77.

**91. [substantive] `_calibration.qmd:79` vs `:98-101`** — "the columns of @tbl-firms should be read one at a time ..., **not compared with each other** as measured cross-sectional moments", followed by a paragraph opening "Several **patterns emerge** from @tbl-firms" that does exactly that comparison. Reframe the second paragraph as design choices: "The archetypes are constructed to differ along three dimensions."

**92. [substantive] `_calibration.qmd:28`** — "CAPM-based **estimates** for **private** AI labs with **market betas** of 1.5--2.5". Private labs have no market beta to estimate. "Assuming betas of 1.5 to 2.5 for comparable listed firms, the CAPM implies a cost of equity of roughly 10.5% to 15.0%."

**93. [substantive] `_calibration.qmd:26`** — "$r = 0.12$, **the** risk-adjusted WACC **for a representative frontier AI lab**". The appositive states $r$ *is* a measured quantity; @tbl-parameters records its status as "Chosen". Rewrite to match the table.

**94. [substantive] `_calibration.qmd:122-124`** — "for frontier AI labs, this means that higher uncertainty ... justifies more cautious investment timing, **even as firms rush to build**"; "the wide variation in WACC **across AI firms** ... **implies** substantially different investment policies"; "consistent with **the observation that** more optimistic firms invest more aggressively". Three model comparative statics converted into claims about real firms, one of them ("the observation") implying a documented empirical regularity that the paper never establishes. Hedge all three to the model.

**95. [substantive] `_calibration.qmd:123`** — presents the archetype WACCs as *observed* cross-firm variation, which sits badly with lines 30–35 stating that three of four archetype WACCs violate (A2) and that every trigger and capacity result is computed at the baseline WACC. Say which sub-range is actually used.

**96. [substantive] `_calibration.qmd:80` and `:92`** — the same blanket robustness claim ("The qualitative results are robust to moderate perturbation of these inputs") twice in three paragraphs, against line 44's report of elasticities of +19.7 and +24.2 in $\alpha$. Keep one instance and name which results are robust: the ratios and percentage differences, not the levels of $X^*$ and $K^*$.

**97. [substantive] `_calibration.qmd:16, 85, 100, 101`** — four uses of "reflects"/"reflecting" asserting that an assumed input is *caused by* a real-world fact ("reflects the venture-backed nature of AI labs", "reflecting fundamentally different business models and beliefs"). Per the house rule, "is meant to capture" or "is consistent with".

**98. [substantive] `_calibration.qmd:6`** — "hyperscalers issued \$121B in bonds in 2025 **alone**" and the xAI "\$5B+" figure, both unsourced here (the footnote on the line covers only the OpenAI credit facility). Add footnotes or point to Internet Appendix C. *Check against Internet Appendix C.*

**99. [substantive] `_calibration.qmd:83`** — "**the one** firm-level compute decomposition with primary documentation". A uniqueness claim. "the only ... that I could locate".

**100. [substantive] `_calibration.qmd:100`** — "as these firms mature and take on traditional debt ..., leverage ratios **will** rise toward the Leland framework's domain". A forecast in the indicative. Recast conditionally.

**101. [structure] `_calibration.qmd:30, 51`** — "for a reason that belongs in the main text rather than the Internet Appendix"; "Nothing substantive turns on the choice, **for a reason worth making precise**". Meta-commentary addressed to the referee, not the reader. Delete both trailing clauses.

**102. [structure] `_calibration.qmd:5, 42, 89, 94`** — "Two caveats should be noted at the outset." / "Two limitations of this choice should be disclosed." / "Two qualifications apply." / "An important caveat:". The same formula four times, three of them impersonal. Vary and activate.

**103. [structure] `_calibration.qmd:8`** — the three-step roadmap ("demand process, technology and cost, financial") does not match the section's subheadings (Demand Process, Technology Parameters, Stylized Firm Archetypes, Baseline Results, Sensitivity Analysis); there is no financial-parameters subsection. Rewrite to match.

**104. [structure] `_calibration.qmd:39, 123, 6`** — three sentences each carrying four independent claims across two or more semicolons (line 39 on $\alpha$; line 123 chaining a mechanism, a net result, and a cross-sectional implication; line 6 packing a caveat, its rebuttal, a footnote, and three unsourced facts). Split each.

**105. [structure] `_calibration.qmd:10`** — a one-sentence orphan paragraph pointing at @tbl-parameters. Fold into the preceding paragraph.

**106. [wording] `_calibration.qmd:99, 127, 16, 20`** — "an **extraordinary** investment intensity"; "This parameter is also **crucial**"; "generate **massive** new demand"; "sits **comfortably** inside that window". Intensifiers the guide rules out.

**107. [wording] `_calibration.qmd:121`** — "The investment trigger, capacity, and training fraction are sensitive to several key parameters." Empty topic sentence duplicating the subsection title. Name the parameters or delete.

**108. [wording] `_calibration.qmd:48`** — "Accounting depreciation ... typically **implies** a 3--5 year useful life (20--33\% per year)". The logic runs backwards: a useful life implies a depreciation rate. Reverse.

**109. [wording] `_calibration.qmd:24, 27`** — "the dispersion ... is **precisely** what generates"; "all valuation uses this reduced-form framework **throughout**" ("all" + "throughout" is redundant).

**110. [terminology] `_calibration.qmd:123`** — "10\%--18\% in **our** calibration". First-person plural in a single-author paper that uses "I" at lines 3, 8, 15, 45, and 60.

**111. [terminology] `_calibration.qmd:78`** — "For privately held firms (the Anthropic-like and xAI-like archetypes), figures are based on press reports". Conflates archetypes with the firms they are modelled on. "For the two archetypes modelled on privately held firms".

**112. [terminology] `_calibration.qmd:55`** — "The **calibrated** $\delta$ is therefore part of the cost normalization rather than a separately identified quantity". "Calibrated" is the wrong label for a parameter the same sentence says is not identified; @tbl-parameters records its status as "Chosen".

**113. [terminology] `_calibration.qmd:24`** — Hassabis is named with no citation or footnote while Amodei is cited. Also, the baseline $\lambda=0.10$ equals the lower endpoint of the quoted Hassabis range, so "more conservative than" is only marginally true.

**114. [minor] `_calibration.qmd:19, 113, 125`** — three ambiguous pronouns: "so **it** disciplines the order of magnitude" (three candidate referents); "annual CapEx---**which** affects no ratio" (intended referent is the choice of $c$); "**it** lowers the trigger as well" (reads as the installation, not lower $\alpha$).

**115. [minor] `_calibration.qmd:69`** — the CapEx/Revenue row mixes precision (0.67, 0.96, 1.52, 20.0) and does not match the "20$\times$" form at line 99.

### Valuation (`_valuation.qmd`)

**116. [substantive] `_valuation.qmd:12`** — "this two-sided interaction ... is, **to my knowledge, novel**". A bare novelty claim with no precise comparison, in a paper whose literature review does this properly elsewhere. Rewrite to name what the adjacent models lack.

**117. [substantive] `_valuation.qmd:78`** — "Within the model, the **observed** aggressive investment patterns of frontier AI labs are ***rational***". Attributes rationality to observed behavior the model does not evaluate. "aggressive investment is value-maximizing under uncertainty about $\lambda$, so the observed behavior is *consistent with* value maximization rather than requiring extreme optimism."

**118. [substantive] `_valuation.qmd:78`** — "so a firm maximizing risk-adjusted value **should err on the side of** higher training allocation even when uncertain about $\lambda$". "Err on the side of" requires minimizing expected loss over a belief distribution; the exercise compares two point mismatches and never averages over a prior. Hedge or supply the step.

**119. [substantive] `_valuation.qmd:80`** — "a conservative firm ... **must** hold genuinely pessimistic beliefs about $\lambda$". Contradicts lines 27–29, where agency problems, signaling, and bounded rationality all generate low $\phi$ without pessimism, and contradicts line 79's own revealed-beliefs disclaimer. Add the proviso.

**120. [substantive] `_valuation.qmd:81`** — "The asymmetric loss function **implies** that firms should hedge against conservative under-training ..., **rationalizing the observation** that frontier AI labs consistently push the boundary of training compute investment." Explanatory power a stylized calibration does not deliver, plus an unsourced empirical claim. Downgrade to "gives a value-maximizing firm more reason to guard against ..., which is consistent with".

**121. [substantive] `_valuation.qmd:6`** — the Internet Appendix G stub says the 25–50% band "**survives** ±25\% one-at-a-time parameter perturbations", but `_appendix.qmd:597` reports 48–59% and 19–30% at those two points, i.e. a perturbed range of 19–59% that is not contained in 25–50%. Restate both ranges. *Check against exhibit.*

**122. [substantive] `_valuation.qmd:13` vs `:68-69`** — two five-year default probabilities at $\ell=0.40$, 4.85% and 5.04%, quoted 55 lines apart against baselines of 0.63% and 0.64%. The evaluation points differ (fixed $X=0.10$, $K=1$, $\phi=0.5$ for the first; the optimal policy for the second), but that is stated only for the first set. State it at line 68 too. *Check against exhibit.*

**123. [substantive] `_valuation.qmd:53`** — "the ratio of the two losses widens from **4.7** to roughly 80". 26/6 gives 4.3, so the reader cannot reconstruct 4.7 from the numbers quoted nearby (it needs the 26.2/5.6 rounding used at `_calibration.qmd:54`). Quote consistent precision or drop the ratio. *Check against exhibit.*

**124. [substantive] `_valuation.qmd:46`** — "For **$\ell > 0$**, the expected-value asymmetry is essentially unchanged". Stated for all positive leverage; only $\ell=0.40$ is reported.

**125. [substantive] `_valuation.qmd:59`** — "a firm investing as if $\lambda=0.50$ ... loses approximately 23\%---a **substantial asymmetry**". A 26% vs 23% gap is not a substantial asymmetry, and the two mismatches differ by a factor of five in magnitude, so the pair does not illustrate the same-magnitude comparison Numerical Finding 1 states. Make the actual point: the aggressive firm needs a five-times-larger belief error to incur a comparable loss.

**126. [substantive] `_valuation.qmd:15`** — "the credit risk of an AI lab in this model is a **high-probability**, modest-severity event". 0.63% to 12.98% over five years is not high-probability in absolute terms; the claim is relative to the spread. Rewrite.

**127. [substantive] `_valuation.qmd:3`** — the roadmap promises two implications, then line 6 inserts a third (the scale-gap index) before either, and it attributes Dario's dilemma to the duopoly model when line 84 concedes it is a single-firm exercise. Rewrite to three items and note the duopoly counterpart is in Internet Appendix E.

**128. [structure] `_valuation.qmd:26-29`** — three bold list-item labels (`**Agency problems**:`, `**Strategic signaling**:`, `**Bounded rationality**:`). These are list labels rather than the forbidden paragraph pseudo-heading, so this is a judgment call, but the list is also the author's own taxonomy presented unattributed and none of the three mechanisms is modelled. Recast as prose and attribute.

**129. [structure] `_valuation.qmd:73` (caption)** — the `fig-investment-dilemma` caption interprets the figure across four clauses and duplicates lines 58–64 nearly in full. Trim to the title phrase, what is plotted, the definition of the shaded region, and the parameters. See finding 168.

**130. [structure] `_valuation.qmd:46, 48-51`** — the same mechanism stated three times (in Numerical Finding 1, again at 49–50, a third time at 51). Collapse to one statement and delete the "The intuition is that" opener.

**131. [structure] `_valuation.qmd:55` and `:82`** — "absolute losses from overinvestment can be existential" appears twice, nearly verbatim. Keep the one under Implications.

**132. [structure] `_valuation.qmd:61, 14, 43`** — three sentences each carrying four or five qualifications (the default-option wedge at 61; the measure qualifications at 14; the levered-maximizer caveat at 43). Split each.

**133. [structure] `_valuation.qmd:6`** — the Internet Appendix G stub reproduces essentially all of Internet Appendix G (definition, monotonicity, the 0.77 crossing, the band, the robustness, three disclaimers) in two dense sentences, defeating the demotion. Compress to one sentence plus the pointer.

**134. [wording] `_valuation.qmd:51`** — "the cost of **timidity** exceeds the cost of **boldness**" introduces a decorative second vocabulary for the established conservative/aggressive pair, and "**foregoes**" is the wrong word (forgo = do without; forego = precede); line 46 uses "forgoing" correctly.

**135. [wording] `_valuation.qmd:67, 64, 46`** — "tells only **half the story**" (cliché); "Leverage **flatters** the overinvesting firm" (decorative verb); "**drastically** under-allocates", "most of the firm's **worth**" (intensifier; informal noun).

**136. [wording] `_valuation.qmd:19`** — "I now **formalize** the cost of belief mismatches ... the **fundamental** tension". "Formalize" reads as analytical treatment; the result is Numerical Finding 1. Use "quantify", and drop "fundamental".

**137. [wording] `_valuation.qmd:77`** — "Dario's dilemma has several implications." Content-free opener; begin with the first implication.

**138. [wording] `_valuation.qmd:84`** — "isolates the belief-mismatch channel **in its cleanest form**" (promotional); "a key **forcing function**" (jargon).

**139. [terminology] `_valuation.qmd:65` vs `:73`** — the body calls the shaded region the "**danger zone**" (informal, scare-quoted) and describes it as where overinvestment losses exceed 10%; the caption says it is bounded by the unlevered curve and marks where *that curve* exceeds 10%, a range not restricted to overinvestment. Fix on the caption's definition and move the sentence to first mention of the figure.

**140. [terminology] `_valuation.qmd:42, 43, 61` vs `:60, 73`** — levered/unlevered alternates with leveraged/unleveraged for the same objects, including inside one caption.

**141. [terminology] `_valuation.qmd:61, 63, 73`** — "the shareholders' default option" becomes "this shutdown option" two lines later.

**142. [terminology] `_valuation.qmd:54`** — "the headline percentages reported here are those of **the reduced model**", a new label for what line 52 calls "the pure-power discounting convention".

**143. [terminology] `_valuation.qmd:62, 70`** — "**the three firms**" used before the set is introduced. Name them at first use.

**144. [minor] `_valuation.qmd:63`** — "so it **capitalizes the most of** this shutdown option". Ungrammatical. "so this shutdown option is worth most to it".

**145. [minor] `_valuation.qmd:31`** — "#### Value loss" in sentence case against Title Case everywhere else in both files.

### Discussion (`_discussion.qmd`)

**146. [substantive] `_discussion.qmd:8-10`** — "generates potential overinvestment relative to **the social optimum**"; "the leader invests earlier than **the socially optimal timing**". The paper does not solve a planner's problem, so both benchmarks are undefined. Either characterize the benchmark or hedge to the cooperative benchmark actually computed. "Total industry capacity may exceed the cooperative (cartel) level" also needs an exhibit. *Check against exhibit/code.*

**147. [substantive] `_discussion.qmd:12-15`** — "Such an extension **would generate** a positive externality ... firms **would underweight** this externality". Indicative statements about a model that is not solved. Mark as conjecture.

**148. [substantive] `_discussion.qmd:41`** — "requiring AI labs to disclose compute expenditure *and training allocation* ... **would improve market efficiency and enable better risk assessment**". The model has no information asymmetry, no belief-updating investors, and no price-formation mechanism. State what the model does support (that $\phi$ jointly determines solvency and the composition of value) and put the efficiency claim outside the model.

**149. [substantive] `_discussion.qmd:36`** — "if multiple highly levered AI labs default simultaneously ..., fire sales could depress asset values and trigger contagion". The model has two firms, no asset-market feedback, no fire-sale mechanism. Mark the step as outside the model.

**150. [substantive] `_discussion.qmd:37`** — "faith-based survival ... suggests that optimism about AI timelines **may be propping up equity values, masking underlying credit risk**". Inside the model nothing is masked: the H-regime option value genuinely raises equity value and lowers the default boundary. Separate the model result from the outside-the-model fragility worry, and drop "propping up".

**151. [substantive] `_discussion.qmd:42`** — "The training fraction $\hat\phi$ is particularly informative because it **reveals** the firm's intertemporal trade-off". "Reveals" is too strong; `_valuation.qmd:79` concedes the mapping from $\hat\phi$ to beliefs is not identified. "summarizes".

**152. [substantive] `_discussion.qmd:23`** — "with the sensitivity greatest for firms priced under relatively pessimistic beliefs, where the value function is steepest". Concavity holds over the policy range; at low $\lambda$ the option value is convex, so the prediction's sign at the pessimistic end is unclear. Restrict the claim to the concave range. *Check against `@fig-lambda-option-value`.*

**153. [substantive] `_discussion.qmd:61-62`** — "the broader financial distress risk that **all** AI labs face"; "The qualitative predictions ... **apply across** financing structures". The model has one financing structure and does not verify portability. Hedge both.

**154. [substantive] `_discussion.qmd:60`** — "Several frontier AI labs (Anthropic, OpenAI) **have** complex capital structures involving SAFE notes, convertible debt, and multi-class equity". Unsourced factual claims about named private firms. Cite Internet Appendix C or hedge to "reportedly".

**155. [substantive] `_discussion.qmd:74`** — "In practice, an 'AI winter' scenario **is a material risk**". An unsourced risk assessment about the world. "is possible; the model abstracts from it."

**156. [substantive] `_discussion.qmd:59`** — "The Leland (1994) structural default framework" written as plain text while `@leland1994corporate` exists and is used in `_model.qmd:256, 261`. This will not render as a citation or enter the bibliography.

**157. [structure] `_discussion.qmd:21-24`** — four `**Bold sentence.**` run-in labels on numbered list items. These sit closest to the construction `paper/AGENTS.md` forbids in this file; judgment call, but folding each label into the item's first clause costs nothing.

**158. [structure] `_discussion.qmd:44-53`** — a single limitation ("Direction of Bias from Static $\phi$") gets its own `###` subsection immediately before the Limitations subsection, forcing line 53 to reach back to it. Fold it in as the first paragraph of Limitations or demote to `####`.

**159. [structure] `_discussion.qmd:4`** — the roadmap ("implications, testable predictions, and limitations") does not match the subsection order (Welfare and Overinvestment, Testable Predictions, Policy Implications, Direction of Bias from Static $\phi$, Limitations).

**160. [structure] `_discussion.qmd:39`** — a one-sentence paragraph under a competition-policy heading that restates the mechanism and states no policy implication.

**161. [structure] `_discussion.qmd:47`** — one sentence carrying a negation, its justification, the positive claim, a bound, and an identification implication. Split into three.

**162. [wording] `_discussion.qmd:27`** — "the model provides a framework for interpreting empirical patterns in the emerging AI sector **through the lens of** existing corporate finance and industrial organization methods". Empty and metaphorical; the three sentences that follow do the work. Delete.

**163. [wording] `_discussion.qmd:46, 52`** — "is the **most-flagged** limitation" (flagged by whom? reads as a referee-response artifact); "Several limitations **should be noted**." (empty passive opener).

**164. [wording] `_discussion.qmd:67, 59`** — "relative to a setting **where** investment expands **the pie**" (informal metaphor; "in which" for a non-spatial antecedent).

**165. [terminology] `_discussion.qmd:21-24, 42, 47`** — $\hat\phi$ used six times in the main text but is not among the paper's defined terms. Confirm it is defined at first use in the main text as the observed training fraction; if it is defined only in Internet Appendix C, define it here. Same for $\phi_1$ at line 48.

**166. [terminology] `_discussion.qmd:15`** — "*over-investment*" and "*under-investment*" hyphenated here, unhyphenated in all seventeen other occurrences, including line 8 of the same file.

**167. [minor] `_discussion.qmd:30, 31`** — sentence opening with "And"; "data that **is** currently scarce" (data take the plural in formal finance prose).

**168. [structure] `_discussion.qmd`, voice** — `_valuation.qmd` is first-person singular throughout; `_discussion.qmd` avoids the first person entirely and falls back on empty passives and abstract subjects. Align on the first person where the authorial choice is the subject.

### Conclusion (`_conclusion.qmd`)

**169. [substantive] `_conclusion.qmd:3-5`** — reproduces abstract sentences 3 and 4 almost word for word (the model-ingredient list, "analytical investment triggers for the single firm and semi-analytical characterization of the duopoly preemption equilibrium"). Open with the *answer* instead: capacity is set by technology and prices, timing by competition, the training-inference split by beliefs about AGI timing, and that separation is what makes belief errors asymmetric.

**170. [substantive] `_conclusion.qmd:19`** — quotes the reduced-model loss percentages (6% and 23%) without the qualification `_valuation.qmd:53-54` attaches: these are the reduced model's numbers, and the exact piecewise problem gives 40% conservative and 0.5% aggressive. The conclusion's "moderate overinvestment is cheap" argument is precisely the one most sensitive to that correction.

**171. [substantive] `_conclusion.qmd:10`** — "a prediction that **aligns with the cross-sectional variation in observed training intensity** across AI labs". The paper has no estimation and no panel of training intensity. "is qualitatively consistent with the differences in reported training intensity across the archetypes in @sec-calibration."

**172. [substantive] `_conclusion.qmd:16`** — "Dario's dilemma **reveals** that this cost is asymmetric." Grants discovery status to a numerical result and personifies the named finding. "Numerical Finding 1 shows that in the calibration this cost is asymmetric."

**173. [substantive] `_conclusion.qmd:25`** — "a *formal* revealed-beliefs methodology that inverts **the structural model**". Implies structural estimation; the same sentence then concedes the inversions "fall short of estimation". Drop "structural".

**174. [substantive] `_conclusion.qmd:3`** — "captures **the distinctive features** of AI infrastructure competition". A stylized model captures some features; "distinctive" is promotional.

**175. [terminology] `_conclusion.qmd:5`** — "supplemented by **numerical findings** on Dario's dilemma". The paper labels exactly one, Numerical Finding 1, and the result-taxonomy table depends on that label. Use it.

**176. [terminology] `_conclusion.qmd:14`** — "This creates a **knife-edge** for levered firms". In economics a knife-edge is a non-robust boundary case; what is described is a two-sided trade-off with an interior optimum. Also "capture market share" imports a quantity-competition object the duopoly result does not carry.

**177. [terminology] `_conclusion.qmd:17`** — "forfeits the H-regime option value that dominates **firm worth**". "Firm worth" is used nowhere else; the paper's term is firm value.

**178. [structure] `_conclusion.qmd:18` and `:19`** — "nearly eight times the baseline" appears twice within four sentences, the first time without the horizon or leverage that make it interpretable. Drop the first.

**179. [structure] `_conclusion.qmd:19`** — one 550-character sentence carrying five numbers, two em-dashes, a contrast, and an interpretation; it reads as a results paragraph rather than a conclusion. Split, keep one magnitude pair, point to the exhibit.

**180. [wording] `_conclusion.qmd:22, 23, 24`** — "The model **necessarily** abstracts from ... dimensions of the full decision space that executives navigate" (defensive hedging plus abstraction); "These omissions define **the frontier** for extending the framework developed here" (empty flourish naming no question); "Several directions for future research are **promising**". Cut all three.

**181. [wording] `_conclusion.qmd:22`** — "geopolitical competition from **actors like** DeepSeek". DeepSeek is a lab, not a geopolitical actor.

**182. [minor] `_conclusion.qmd:22`** — three consecutive sentences opening with "It", the third beginning "And".

### Internet Appendix A (Proofs)

**183. [substantive] `_appendix.qmd:53`** — "**The closed-form results** in this Internet Appendix have been **independently** verified with the Lean 4 proof assistant". The opening sentence claims verification of the closed-form results without qualification; the next 20 lines walk it back to the algebra and calculus downstream of an HJB equation and boundary conditions "taken as given". A reader who stops after sentence one takes away more than is true. "Independently" is also unearned: the same author formalized the same derivations. Narrow to: "The algebraic and single-variable-calculus content of Propositions 1--3 is machine-checked in Lean 4 and Mathlib."

**184. [substantive] `_appendix.qmd:273`** — Numerical Finding 1 closes with a **`$\square$` QED box**, inside a section headed "A. Proofs". The paper is careful everywhere else to keep this result numerical; the container and the symbol both assert proof status. Delete the box and retitle the section "A. Proofs and Supporting Derivations".

**185. [substantive] `_appendix.qmd:209`** — "Parts (ii)--(v) combine **analytical motivation** with numerical verification as indicated in the proposition statement." The proposition labels (iii), (iv), and (v) simply "(Numerical finding)", and @tbl-result-taxonomy classifies them as "Numerical". This upgrades three results.

**186. [substantive] `_appendix.qmd:207-249`** — the proof of Proposition 3 skips parts (iii) and (iv) entirely, yet part (v) opens "Higher $\lambda$ lowers the preemption trigger $X_P$ **(from part iii)**", citing a part with no entry. Add stub entries pointing to Internet Appendix B, or state explicitly that (iii) and (iv) are purely numerical.

**187. [substantive] `_appendix.qmd:267-269`** — line 259 correctly frames the block as "The following **heuristic** argument", then two sentences state $W'''>0$ as derived, and state it twice. Keep one, framed as the numerical result it is.

**188. [substantive] `_appendix.qmd:229`** — "so the up-crossing on $(0, X_L^{\text{mono}})$---**which exists by the boundary conditions above**---is unique". The zero-leverage result the taxonomy calls "Analytical" is *at most one* up-crossing; existence still rests on the computationally verified upper-endpoint sign, which this clause quietly absorbs. Make the conditionality explicit.

**189. [substantive] `_appendix.qmd:249`** — "This is verified numerically across **the full parameter space**." Elsewhere the paper says "all parameterizations tested" or "the calibration ranges". Match.

**190. [substantive] `_appendix.qmd:267`** — "a source of asymmetry **novel relative to standard real options models**". Promotional and unsupported by a stated comparison. Name the specific absent feature or delete.

**191. [substantive] `_appendix.qmd:212` vs `:218`** — "I verify that continuity and the required boundary conditions hold" followed six lines later by the concession that one boundary condition "is *not* established analytically". Put the qualification in the opening sentence.

**192. [structure] `_appendix.qmd:53`** — the Lean scope paragraph is a single ~250-word sentence with four semicolon-separated inventories. It is the one paragraph a referee will read closely and the least readable in the section. One sentence per proposition.

**193. [structure] `_appendix.qmd:116-130`** — Step 5b (justifying a convention used back in Step 1) interrupts the $\phi^*$ argument between Step 5 and Step 6. Move it after Step 6 as a closing discussion block. The orphan sentence at 130 belongs with the paragraph defining $\Phi_L$ at 122.

**194. [structure] `_appendix.qmd:87-136`** — three `$\square$` boxes inside the proof of Proposition 1 (ends of Step 5, Step 5b, Step 6), so the reader cannot tell which closes the proposition. Reserve it for 136. Also drop the bare "(Lemma)" tag at 87, used nowhere else.

**195. [structure] `_appendix.qmd:12-47`** — the Internet Appendix opens with no prose: no sentence saying what it contains, and the parameter and notation tables float above Section A with no lettered heading of their own. Add a two-sentence opener and give the tables a heading.

**196. [structure] `_appendix.qmd:178-187`** — the block opens on the symmetric threshold $\underline\phi$ then pivots mid-block to the markup channel. Start a new run-in block at "To complete the proof".

**197. [structure] `_appendix.qmd:214-218`** — bold run-in labels here against italic labels everywhere else in Section A. Match.

**198. [terminology] `_appendix.qmd:172, 183, 187, 191`** — "**effective discount rate**" names three different quantities within thirty lines ($r-\mu_L$, $r+\lambda$, and $\Delta \equiv r-\mu_L+\lambda$). Give each its own name.

**199. [terminology] `_appendix.qmd:187` vs `:253`, and `:153` vs `:227`** — $D$ is both the characteristic-root discriminant and the debt value; $E$ is both the equity value and a positive constant coefficient. Rename the discriminant and the coefficient.

**200. [terminology] `_appendix.qmd:122, 145, 151`** — $\beta_H^-$, $p_H$, $q_H$, and $B_H$ appear without definition and none is in @tbl-notation.

**201. [terminology] `_appendix.qmd:214-227`** — $F$ is the single firm's option value in Proposition 1 and the follower's value here, with no disambiguation; and the follower's trigger appears as $X_F^*$ at 218 and 247 and as $X_F$ at 225 and 227.

**202. [terminology] `_appendix.qmd:235, 281, 287` vs `_model.qmd:392`** — Proposition 3(ii) is labelled "Analytical **critical point**" in the Internet Appendix and taxonomy table, and "Analytical **fixed point**" in `_model.qmd`, whose own body then says "critical point". Standardize.

**203. [terminology] `_appendix.qmd:253, 257, 261, 271`** — levered/unlevered and leveraged/unleveraged both used within twenty lines.

**204. [terminology] `_appendix.qmd:253`** — "Define the **value function** $W(\lambda_{\text{invest}})$". "Value function" already names $V$, $F_L$, $F_H$; $W$ is the evaluation of a fixed policy under a possibly wrong belief.

**205. [terminology] `_appendix.qmd:281`** — the taxonomy row states the Proposition 1 comparative static in "$(r-\mu_H)^{-1}$" where the proposition states it in $\mu_H$; and the same row names one convention two ways ("pure-power" in Method, "unconditional-$A_{\text{eff}}$" in Domain).

**206. [wording] `_appendix.qmd:133`** — "From the **implicit function theorem** applied to the FOC". Neither (i) nor (ii) uses it; both argue from Step 5's monotonicity in $w_H/w_L$. Restate accordingly.

**207. [wording] `_appendix.qmd:143`** — "**Two features of the present model** permit a tractable single-boundary reduction." The first is a model feature; the second is an approximation the text itself calls "the perpetuity approximation" eight lines later.

**208. [wording] `_appendix.qmd:145`** — a displayed "closed-form solution" whose leading term is the placeholder "[perpetuity]" is not a closed form. Write the term out or describe it in prose.

**209. [wording] `_appendix.qmd:68`** — "**The revenue** at the trigger is $A_{\text{eff}}\cdot X^*$". $A_{\text{eff}}X$ is a present value, not a revenue flow; and $\Theta$, called "the total cost", bundles the outlay with the operating-cost perpetuity.

**210. [wording] `_appendix.qmd:100`** — "(Inada condition: the **last** unit of inference has infinite marginal value.)" As $\phi\to1^-$ inference capacity goes to zero, so it is the *first* unit. Also breaks parallel with line 99.

**211. [wording] `_appendix.qmd:247`** — "The **duration** of the monopoly phase is substantial---$X_F^*/X_P \approx 44$--$46$". A ratio of demand triggers is not a length of time.

**212. [wording] `_appendix.qmd:197`** — "verified by finite differences **as a regression test**". Software jargon that in a finance paper reads as an econometric regression.

**213. [wording] `_appendix.qmd:202, 233, 108, 90, 41`** — five redundant restatements: "the two channels are distinct" (already displayed); "No case of multiple up-crossings was found" (restates the preceding sentence); "both bracketed terms $>0$ **are positive**"; "equivalent to ... **or equivalently**"; "proved in full, **with no unproved placeholders**". Also "**moot**" at 233 reads differently in US and UK usage; use "does not bind".

**214. [minor] `_appendix.qmd:53, 84-85, 140, 267`** — a dangling modifier ("its closed-form solution $K^*$, independent of the training fraction"); a comma-terminated display followed by a capitalized "Since"; a hand-typed "Leland (1994)" where a cite key exists; an unescaped `70%`.

**215. [minor] `_appendix.qmd:271`** — "whereas **under underinvestment**" stutters.

### Internet Appendix B–D

**216. [substantive] `_appendix.qmd:303`** — "**Equilibrium uniqueness** for the duopoly is **assessed** by running the optimization from the same 16 deterministic starting points; all converge to the same solution." Multistart agreement is evidence about local optima in the optimizer, not about uniqueness of the equilibrium. Say which is which.

**217. [substantive] `_appendix.qmd:325`** — "so the direction of the bias ... follows **analytically, not only numerically**". The same sentence states that the argument is a first-order expansion and that the sign of $C_2$ is evaluated "at calibration values". Rewrite to claim only a closed-form explanation of the sign.

**218. [substantive] `_appendix.qmd:349`** — "The wedge accounts for the gap **exactly**." Overstates a match reported "to five significant figures" in the next sentence.

**219. [substantive] `_appendix.qmd:351`** — "For $\alpha > 0.67$, the full two-term solution must be used; **qualitative patterns are preserved**." A bare assertion with no stated support, in the section whose job is to say what was checked. Report the check or say the region was not explored.

**220. [substantive] `_appendix.qmd:412`** — "The values of $\hat\phi$ in @tbl-firms are **triangulated** from three types of evidence." No combining procedure is described, and the block never states the resulting values. This is the natural place to say plainly that $\hat\phi$ is assigned judgmentally and that no moment is matched.

**221. [substantive] `_appendix.qmd:408` vs `:400`** — "the archetype **is calibrated to xAI**" against "they do not represent exact calibrations to any specific company" eight lines earlier. Also "**exact** calibrations" implies they are approximate calibrations to specific companies, which the blocks then confirm by naming four firms. State the honest version positively.

**222. [substantive] `_appendix.qmd:436-437`** — Section D reports $\varepsilon_{K^*,r}=-28.8$ and $\varepsilon_{K^*,\alpha}=+24.2$ with no warning that these are **local** elasticities at a baseline Section B says sits close to the (A2) upper bound, where Section B itself concludes the scale results are "not a robust quantitative prediction". Add the caveat.

**223. [substantive] `_appendix.qmd:437`** — "its FOC depends **only** on the ratio $w_H/w_L$" is contradicted by the table two lines above, which gives $\varepsilon_{\phi^*,\alpha}=+0.2$; and "negligible sensitivity to $\sigma$, $\gamma$, $\delta$, **which do not enter** the training allocation FOC" implies the reported $\approx 0$ entries are finite-difference noise. Say so.

**224. [substantive] `_appendix.qmd:407`** — "because **the majority of** Alphabet's infrastructure spending supports AI workloads across all products". An unsourced quantitative assertion about a named firm, used to justify a modelling choice.

**225. [substantive] `_appendix.qmd:414`** — three quoted statements, only one attributed: the Microsoft CFO quote, the Huang quote, and the "40% of AI revenue" figure carry no source, date, or venue, and "AI revenue" is undefined.

**226. [substantive] `_appendix.qmd:388-391`** — `@tbl-sources` rows list bare firm names ("xAI", "OpenAI", "Google") where a document belongs, in a table whose stated job is documenting sources. The $\delta$ row at 395 shows the standard.

**227. [substantive] `_appendix.qmd:337`** — "The optimal training fractions coincide in the two problems **at every belief**" where the exercise covers three $\lambda_{\text{invest}}$ values. "at every belief considered".

**228. [structure] `_appendix.qmd:404-408`** — the four archetype blocks are not parallel: Anthropic reports 2025 revenue only, OpenAI and Google report two years, xAI reports a single quarter and never states CapEx; Google gets an extra paragraph; verbs vary without cause. Impose one template.

**229. [structure] `_appendix.qmd:405` and `:416`** — the Epoch AI decomposition is stated twice with identical figures, and 405 mixes a 2025 CapEx figure with a 2024 decomposition without reconciling them.

**230. [structure] `_appendix.qmd:353`** — one 2,081-character paragraph carrying five distinct claims (where (A2) holds, the $K\to0$ degeneracy, what the solvers do, how archetype WACCs enter, the admissible windows). Split twice.

**231. [structure] `_appendix.qmd:298, 302`** — (A2) is *used* at 298 and *stated* at 353, with the same vague forward pointer "(see the (A2) discussion below)" twice.

**232. [terminology] `_appendix.qmd:353` vs `:404-408`** — two incompatible naming schemes for the four archetypes ("the hyperscaler / the platform / the frontier lab / the compute racer" in Section B; "the Anthropic-like / OpenAI-like / Google-like / xAI-like archetype" in Section C), with no mapping between them. Worse, `_appendix.qmd:408` uses "frontier lab" generically for the xAI archetype, colliding with the defined archetype name.

**233. [terminology] `_appendix.qmd:298` vs `:353`** — (A2) is "the interior-capacity condition" and "the option premium condition".

**234. [terminology] `_appendix.qmd:392`** — bare $\beta$ for the equity beta collides with the characteristic roots $\beta_L^\pm$, $\beta_H$ used heavily thirty lines earlier. Write it in words.

**235. [terminology] `_appendix.qmd:400`** — "stylized firms", "composites", "firm category" in two sentences, against the defined term "four AI lab archetypes".

**236. [wording] `_appendix.qmd:295`** — "**All** parameters ($r$, $\mu_s$, $\sigma$) are risk-adjusted" contradicts the preceding sentence, which says $\sigma$ is common to both measures.

**237. [wording] `_appendix.qmd:349, 437`** — "**extremely** elastic", "**remarkably** insensitive". The numbers do the work.

**238. [wording] `_appendix.qmd:333`** — "delivers $97.4\%$ of the exact optimum: the value loss ... is $2.64\%$". One quantity at two precisions in one sentence. *Check against exhibit/code for the supported precision.*

**239. [wording] `_appendix.qmd:416, 335, 313`** — "The **key finding** is that..." (promotional, and the finding is Epoch AI's); "**near-dismissal** of transformative AI" (coinage); "shrinks and enters earlier **in step**" (colloquial, and in step with what?).

**240. [minor] `_appendix.qmd:298, 303, 311`** — "16 deterministic starting points" against "a six-point deterministic multistart" and "the sixteen-start follower solver"; "Nelder-Mead" against "Nelder--Mead".

**241. [minor] `_appendix.qmd:399, 409, 331`** — "All firm-level data **reflects**" (take the plural) and two as-of dates for one dataset; "**These concepts**" with an antecedent that lives in `_calibration.qmd`, so the e-companion does not read standalone; "to a relative $10^{-4}$" (missing "error of").

### Internet Appendix E–H

**242. [substantive] `_appendix.qmd:597`** — "so the band is **a property of the model** rather than of the baseline draw". A ±25% one-at-a-time sweep over nine parameters shows the band survives local univariate perturbation, not a property of the model. See also finding 121.

**243. [substantive] `_appendix.qmd:534`** — "the underinvestment cost remains roughly 2$\times$ the overinvestment cost, **confirming** the single-firm finding". The duopoly ratio (38/17) is roughly half the single-firm ratio (26/6), so competition compresses the asymmetry substantially; "confirming" reads as if the magnitude carried over. Say it survives but narrows. *Check against exhibit.* This is the same issue as `_valuation.qmd:86`'s "quantitatively **reinforced**" (finding 125's neighbour), which is at best ambiguous and arguably backwards.

**244. [substantive] `_appendix.qmd:454`** — "All four objects are ratios or value shares, **and are therefore** exactly invariant to the cost-scale parameters $\delta$ and $c$." Being a ratio does not by itself imply invariance. If the invariance comes from homogeneity of the value functions in the cost scale, say so. *Check against exhibit/code.*

**245. [substantive] `_appendix.qmd:511`** — "The bias is therefore **entirely** the value of the re-purposing option." Holds only within the two-period, fixed-$K$, exponential-arrival exercise, and partly undoes the honest hedge at 504.

**246. [substantive] `_appendix.qmd:509`** — "Firms in practice reallocate GPUs between training and inference on timescales of weeks". An uncited empirical claim about industry practice inside a model paragraph.

**247. [substantive] `_appendix.qmd:546`** — "which is **without loss of generality** within the absorbing H-regime". The justification was left behind in the main text (`_model.qmd:106` carries it). Since F must stand alone after demotion, restore the clause.

**248. [substantive] `_appendix.qmd:638`** — "the credit risk of an AI lab in this model is a **high-probability, modest-severity** event ... while the **catastrophic** component ... is borne by shareholders". A 12.98% five-year probability at $\ell=0.70$ is moderate, not high, and "catastrophic" is rhetorical. Same sentence as finding 126; the two copies should be fixed together.

**249. [substantive] `_appendix.qmd:459-461`** — "The main qualitative mechanisms **would be expected to survive** a Cournot specification ... **would likely be somewhat** weaker". Stacked hedges plus a hidden actor, and "I do not solve the Cournot model" arrives only after two paragraphs of conjecture. Move the disclaimer to the head of the block and use one precise hedge.

**250. [structure] `_appendix.qmd:441`** — "I assess robustness along several dimensions:". The exact pattern the guide names as the thing to avoid: no count, no concern. Name the five exercises and, for each, the concern and whether it is quantified.

**251. [structure] `_appendix.qmd:443, 457, 477, 519, 536`** — the five robustness blocks are not parallel in what their first sentence does (method / concern / limitation / recap / extension), and two of them end by disclaiming that nothing was solved while the others never say up front what was computed.

**252. [structure] `_appendix.qmd:500` and `:510`** — the exponential-stationarity argument appears twice, near-verbatim, ten lines apart, the second time opening with "The stationarity of the problem **is worth stating explicitly**".

**253. [structure] `_appendix.qmd:513-516`** — the Internet Appendix cites the main text as the authority for its own claim ("as @sec-discussion states"), then restates qualitatively what 496–511 just established numerically.

**254. [structure] `_appendix.qmd:571-576`** — four consecutive negative definitions ("This is deliberately *not* a growth-option decomposition. It does not measure... are benchmarks rather than... not a valuation identity...") before the reader is told what the index *is*, and the numbered list at 576 arrives with no lead-in.

**255. [structure] `_appendix.qmd:598-601`** — the same disclaimer ("the model is silent on where any actual lab sits on the horizontal axis") three times: twice in consecutive body sentences and once in the caption. Keep one in each place.

**256. [structure] `_appendix.qmd:453, 459, 538, 629`** — four sentences carrying three to five results each across multiple semicolons. Split.

**257. [structure] `_appendix.qmd:610`** — "This section gives **the formulas** and the leverage curves", then uses $D(X)$ and $X_D$ without giving or cross-referencing either. Add @eq pointers so Internet Appendix H reads standalone.

**258. [structure] `_appendix.qmd:633`** — a robustness result (using $\phi^*\approx0.70$ instead of $\phi=0.5$ shifts levels but not shape) buried inside a parenthesis inside a sentence establishing the evaluation point. Promote it to its own sentence.

**259. [terminology] `_appendix.qmd:455`** — "the statements elsewhere in **this appendix**". The one bare-"appendix" reference I found in the whole paper; house rule is "Internet Appendix".

**260. [terminology] `_appendix.qmd:453` vs `:590`** — "the capacity gap fraction" and "the scale-gap index $g$" for the same object in two Internet Appendix sections, while the figure label remains `fig-growth-decomposition` in a section insisting the exhibit is *not* a growth-option decomposition. Standardize the name, and consider renaming the label and generated file to `fig-scale-gap`.

**261. [terminology] `_appendix.qmd:613, 617, 640`** — three notations for the coupon within one section: a word inside the display, $C_D$ in the footnote, $r_c$ in the caption. The paper's defined term is $C_D$. Also line 613 announces "training fraction $\phi$" for a display in which $\phi$ never appears.

**262. [terminology] `_appendix.qmd:557`** — "@tbl-elasticities reports **the same objects** as elasticities at the baseline". Not the same objects: `tbl-elasticities` reports $X^*$, $K^*$, $\phi^*$ from the full model; `fig-comparative-statics` reports $X_H^*$ and $K_H^*$ from the H-regime sub-problem that line 546 has just distinguished.

**263. [terminology] `_appendix.qmd:445` vs `:450`** — "truncation" used for the reporting practice being rejected and, ten lines later, for the binding of the admissibility boundary.

**264. [claim-strength] `_appendix.qmd:558`** — "when the firm does invest, it builds more **to compensate for the higher risk**". Not the mechanism under risk-adjusted discounting: higher volatility raises the trigger, so investment occurs at a higher demand level, where optimal scale is larger.

**265. [structure] `_appendix.qmd:561-562`** — the economic reading of the $\delta$ panel is offered and withdrawn one sentence later. Put the normalization first.

**266. [wording] `_appendix.qmd:458, 478, 508, 632`** — "so it is **natural to ask**"; "the **most-flagged** limitation"; "The **honest** reading of @tbl-dynamic-phi" (implies competing readings are dishonest); "@fig-credit-risk presents the credit risk **implications**" (names no object).

**267. [wording] `_appendix.qmd:474`** — "The preemption discount is modestly **less aggressive** under the fixed-pie specification (0.63 vs.\ 0.57)". A discount is not aggressive, and the number order reverses the table's column order. See also finding 273.

**268. [wording] `_appendix.qmd:463`** — "$y_i$ **the regime-relevant capacity measure** raised to $\alpha$" in a passage whose whole point is a precise alternative specification. Write it out. *Check against exhibit/code.*

**269. [wording] `_appendix.qmd:448, 500, 628, 636`** — "fail through its upper bound, **whose failure** sends"; "**Nothing in this is** a drift"; "upper bounds on the default **hazard**" (a hazard is a rate; the object bounded is a probability); "0.63\%/1.80\%/4.85\%/12.98\%" (two decimals imply precision the calibration does not support; round to one).

**270. [minor] `_appendix.qmd:552, 632, 638`** — "real options result", "credit risk discussion" unhyphenated as modifiers where 546 and 610 hyphenate. Also `:612, 621, 631` — "**The** leverage gradient." takes an article the two neighbouring run-in labels do not.

**271. [minor] `_appendix.qmd:558-561`** — "shows / illustrates / shows / demonstrates" varied for stylistic variety only; "demonstrates" is on the guide's discouraged list.

### Captions and notes

**272. [substantive] — captions state conclusions rather than naming the object.** Six of the eight figure captions carry a result and its mechanism, in every case duplicating body text that is a few lines away:
- `_model.qmd:195` (`fig-lambda-option-value`): "Higher $\lambda$ raises $F_L$ toward $F_H$ **by increasing the expected value of the switching opportunity**" — duplicates lines 191–193.
- `_model.qmd:309` (`fig-default-boundaries`): "Higher leverage raises both boundaries---debt-financed scale delays entry while coupon obligations raise the default point---and compresses..." — duplicates 302–305.
- `_model.qmd:408` (`fig-competition-effect`): "The leader **always** invests at a lower trigger than the monopolist **due to preemption**" — duplicates 401, and "always" overstates the plotted grid $\sigma\in[0.20,0.30]$.
- `_valuation.qmd:73` (`fig-investment-dilemma`): a four-clause interpretation duplicating 61–64.
- `_appendix.qmd:601` (`fig-growth-decomposition`): two sentences of argument duplicating 573 and 598–599.
- `_appendix.qmd:640` (`fig-credit-risk`): two results with mechanisms duplicating 634–637.
In each case, cut the interpretive sentence and put the procedural content there instead (parameters, ranges, evaluation point, what is held fixed).

**273. [substantive] `_model.qmd:309`** — "Higher leverage raises **both** boundaries" when three are plotted ($X_F^*$, $X_D$, $X_P$) and Proposition 3(iv) states leverage raises all three.

**274. [substantive] — four exhibits have no note at all and are not readable standalone.**
- `@tbl-baseline-results` (`_appendix.qmd:378`): no solver, no tolerance, no rounding, no rate convention, no units for $K^*\!=\!0.0067$ and $X^*\!=\!0.0047$.
- `@tbl-fixedpie` (`_appendix.qmd:471`): never defines the fixed-pie contest, $\underline\phi$, or that this is the zero-leverage duopoly at baseline.
- `@tbl-duopoly-dilemma` (`_appendix.qmd:529`): never defines $\Delta V$, never states $\lambda_{\text{true}}=0.10$, and never states the design restriction from line 522 (the rival follows its single-firm optimal policy and does not re-optimize).
- `@tbl-sources` (`_appendix.qmd:397`): the as-of date sits in the body at 399 rather than in the note.

**275. [substantive] `_appendix.qmd:30`** — `@tbl-parameters` note: "**All** parameters are risk-adjusted". Read literally this covers $\alpha$, $\gamma$, $c$, $b$, and $\ell$, for which risk adjustment is not meaningful. The body states the narrower claim correctly at 295. Also "dashes indicate no baseline value" is contradicted by the $c$ row (baseline 1.00, dash in *Status*), and "'Chosen' = **chosen** for discipline" defines the term with itself.

**276. [substantive] `_appendix.qmd:291`** — `@tbl-result-taxonomy` note defines four method categories ("Closed-form", "implicit function", "computational verification", "numerical"), but the Method column actually uses "Analytical (mechanical)", "Conditional analytical (IVT; ...)", and "Analytical critical point (exact factorization)", while "computational verification" never appears. Align the glossary with the entries.

**277. [structure] `_appendix.qmd:47`** — `@tbl-notation` types $X_D$ and $X^*$ as a bare "Derived", a category the note never defines (it defines "Derived (primitives)" and "Derived (choices)"); and the table promises "additional notation not listed in @tbl-parameters" while omitting $X_P$, $X_F^*$, $X_L^{\text{mono}}$, $\Delta V$, and $g$, all of which appear in captions and body text.

**278. [structure] — units belong in the exhibit, not the caption.** `@tbl-parameters` and `@tbl-baseline-results` report rates as bare decimals (0.12, 0.06, 0.25, 0.03) with no unit anywhere; `@tbl-firms` labels revenue and CapEx "(\$B)" but leaves Leverage and WACC bare. Add "(per year)" and "(debt / total capital)" to the column headers.

**279. [structure] `_appendix.qmd:493`** — `@tbl-dynamic-phi` constrains $\phi_1$ and $\phi_H$ in its note but never defines $\kappa$ or $\phi_{L2}$, both of which are column headers.

**280. [structure] `_appendix.qmd:434`** — `@tbl-elasticities`: "Elasticities ... **to** model parameters" (→ "with respect to", as at 422); only $\varepsilon_{X^*}$ is defined; the "$\approx 0$" entries are never explained.

**281. [terminology] `_calibration.qmd:74`** — `@tbl-firms` caption says "Stylized **firm parameters**" while the section heading, the body, and Internet Appendix C all say "archetypes"; the first column is headed "Parameter" but its first entry is "Archetype"; and the row "Training fraction $\hat\phi$" is never distinguished from the model's endogenous $\phi$. Also "All **figures** are order-of-magnitude composites" is ambiguous in a paper with eight figures.

**282. [terminology] `_model.qmd:195`** — "**pre-adoption** option value", a fifth regime vocabulary appearing only in this caption and at `_model.qmd:192`, against the Internet Appendix's "pre-switch"/"post-switch" (10 occurrences).

**283. [structure] `_appendix.qmd:601`** — `fig-growth-decomposition` is the only caption identifying series by colour ("assets-in-place (blue) and capacity gap (orange)"); every other uses solid/dashed/dotted/gray. Add a non-colour cue for grayscale printing.

**284. [structure] `_appendix.qmd:564`** — `fig-comparative-statics` is the only figure caption not closing with the "Parameters: baseline calibration" formula its six siblings use; it says "holding others at baseline values" mid-sentence instead.

**285. [minor] — five-year vs 5-year.** "five-year default probability" at `_valuation.qmd:13` and `_conclusion.qmd:19`; "5-year" at `_valuation.qmd:67`, `_appendix.qmd:273, 636`, and the `fig-credit-risk` caption. Standardize on "five-year".

### Cross-cutting

**286. [substantive] — "preemption discount" denotes two reciprocal quantities.** `_calibration.qmd:112, 127` and the `fig-competition-effect` caption use it for the ratio $X_P/X_L^{\text{mono}}\approx0.57$; `_model.qmd:404, 445` and `_appendix.qmd:313` use it for the complement $1-X_P/X_L^{\text{mono}}\approx43\%$. The same phrase therefore *rises* when preemption weakens (ratio sense) and *rises* when it strengthens (complement sense), within twenty lines of each other in `_model.qmd`. Reserve "preemption discount" for the complement and call the ratio "the trigger ratio $X_P/X_L^{\text{mono}}$".

**287. [substantive] — the faith-based survival mechanism is stated near-verbatim three times.** `index.qmd:24`, `_introduction.qmd:24`, `_conclusion.qmd:13`; the last two differ by two words. The conclusion should state the *consequence* the body established ($\underline\phi\approx0.18$ against $\phi^*\approx0.70$, and the reversal below $\lambda\approx0.034$), not restate the mechanism.

**288. [substantive] — "pinned down by beliefs, not competitive position" appears five times.** `index.qmd:23`, `_introduction.qmd:22`, `_model.qmd:392` (Proposition 3(ii)), `_calibration.qmd:116`, `_discussion.qmd:24`. Keep the abstract, the proposition, and the discussion's testable-prediction form; cut the other two.

**289. [substantive] — the model-ingredient list appears three times** (`index.qmd:22`, `_introduction.qmd:14`, `_conclusion.qmd:3`), and the dilemma's two-sidedness three times (`index.qmd:25`, `_valuation.qmd:71`, `_conclusion.qmd:17-18`). Cut the conclusion's ingredient recital (finding 169) and the `_valuation.qmd:71` summary sentence, whose numbers are given in the two preceding sentences.

**290. [substantive] — the "three core tensions" frame is duplicated between §6 and §7.** `_discussion.qmd:3` states it and then never uses it; `_conclusion.qmd:7-16` states and expands it. Delete the discussion's version.

**291. [substantive] — the §5 credit-risk paragraph is duplicated in Internet Appendix H**, numbers and closing sentence included: `_valuation.qmd:13` / `_appendix.qmd:635-636` give the same bps and probability series, and `_valuation.qmd:15` / `_appendix.qmd:638` are the same sentence with one word changed ("the two gradients" / "the two panels"). Keep the interpretive sentence in the main text; Internet Appendix H should carry the formulas, the measure qualifications, and the figure.

**292. [substantive] — the introduction claims three result categories, the literature review two.** `_introduction.qmd:15` says "The results fall into three categories"; `_literature.qmd:29`, included three pages later, says "This mechanism produces two results". Reconcile.

**293. [substantive] — Internet Appendix exhibits are referenced bare in the main text.** `@tbl-elasticities` is qualified at `_model.qmd:143` and `_calibration.qmd:120` but bare at `_calibration.qmd:44, 53, 80, 92, 125`; likewise `@tbl-parameters` (`_calibration.qmd:18, 19, 39`), `@tbl-sources` (`:17, 55`), `@tbl-result-taxonomy` (`_model.qmd:424`), `@tbl-duopoly-dilemma` (`_valuation.qmd:86`). Because `split_blind_pdf.py` cuts the manuscript from the e-companion, a bare "Table 9" in the submitted manuscript points at nothing the referee holds. Add "in the Internet Appendix" at each.

**294. [terminology] — the high regime carries four names**: "high regime $H$", "post-AGI", "the transformative AI regime" (`_introduction.qmd:19`), "post-adoption" (`_model.qmd:192`, `_conclusion.qmd:9`), plus "pre-adoption"/"pre-switch" for its complement. `_introduction.qmd:10` explicitly notes the prize is "variously called" transformative AI or AGI and then never picks one. Define once, use "post-AGI" thereafter.

**295. [terminology] — four labels for the choice variable $\phi$**: "training fraction" (63 uses), "training allocation" (30), "training share" (`_discussion.qmd:47`, `_appendix.qmd` ×3), "training intensity" (`_literature.qmd:23`, `_model.qmd`, `_conclusion.qmd:10`). Keep "training fraction" for the variable and "training allocation" for the decision; drop the other two.

**296. [terminology] — the safety-margin ratio has three names**: "proportional margin of safety $X_F^*/X_D$" (`_model.qmd:305, 309, 396`), "the distance-to-default ratio $X_P/X_D$" (`_model.qmd:398`), "its distance to default at entry, $X^*/X_D$" (`_valuation.qmd:69`).

**297. [terminology] — the archetypes are named two ways, sometimes in one sentence.** `_calibration.qmd:32` runs the firm-anchored form and the bare-role form together: "The Google-like hyperscaler ($r=0.10$) and the baseline ($r=0.12$) lie inside this window; **the platform** ($r=0.14$), **the frontier lab** ($r=0.15$), and **the compute racer** ($r=0.18$) violate its upper bound." Use the firm-anchored form uniformly, since @tbl-firms defines the mapping. See also finding 232.

**298. [minor] — hyphenation and numeral drift.** "real-options model" (abstract) vs "Real options models" (`_introduction.qmd:12`) vs "the standard real options form" (`_model.qmd:91`); "over-investment"/"under-investment" once against seventeen unhyphenated uses; "five-year"/"5-year"; "Nelder-Mead"/"Nelder--Mead"; "16"/"sixteen"/"six-point".

**299. [minor] — sentence-opening scaffold.** No instances of "Moreover", "Furthermore", "Importantly", "Notably", "Indeed", or "It is worth noting" (clean). But "This section..." opens four of the seven main sections plus two Internet Appendix sections; "is therefore" appears 18 times; and the "Two/Three X should be noted/flagged/disclosed/apply." + "First, ... Second, ..." scaffold recurs nine times (`_calibration.qmd:5, 42, 89`; `_model.qmd:28, 170, 220, 338, 417`; `_discussion.qmd:52`). Worth thinning.

---

## House-conventions check

| Convention | Verdict | Detail |
|---|---|---|
| **Em-dash budget (≤5 per paper)** | **FAIL** | 255 `---` constructions in source; 5 are literal placeholders in Internet Appendix table cells and one is double-counted across `index.qmd`/`index-blind.qmd`, so **249 in a single rendered manuscript**. By file: `_model.qmd` 78, `_appendix.qmd` 72 (67 prose), `_calibration.qmd` 30, `_valuation.qmd` 28, `_discussion.qmd` 22, `_literature.qmd` 13, `_introduction.qmd` 5, `_conclusion.qmd` 5, abstract 1. Roughly 60 lines carry two or more in one sentence. Zero literal `—`/`–` characters; every one is the LaTeX `---` form. |
| **No em-dash in the abstract** | **FAIL** | `index.qmd:24` and `index-blind.qmd:32`, identically: "lowering the default boundary---the hope of AGI keeps the firm alive". Finding 2. |
| **≤1 em-dash per page** | **FAIL** | Follows from the above; `_appendix.qmd:122` alone carries six. |
| **No hard-wrapped prose** | **PASS (with a caveat)** | I checked every adjacent line pair across all section files: **zero mid-sentence line breaks**, and no column wrapping (lines run to 1,500–3,100 characters). The paper uses semantic line breaks (one sentence per line) in some paragraphs and one-line paragraphs in others, so diffs stay readable, which is what the rule protects. The real issue is **internal inconsistency**: `_literature.qmd` has L23, L26, L29 as single-line paragraphs while L5–9 and L14–20 are split; `_conclusion.qmd:22` is a single 910-character line while every other paragraph in the file is split; `_appendix.qmd` is split throughout while `_model.qmd` mixes both. Pick one convention per file. |
| **No citations in the abstract** | **PASS** | None. |
| **Blind-review hygiene** | **PASS** | `index-blind.qmd` carries no author name, affiliation, acknowledgement, or repository URL; a repo-wide grep over every included `.qmd` finds the author name, institution, and GitHub URL only at `index.qmd:12, 18, 33`. |
| **`index.qmd` / `index-blind.qmd` metadata parity** | **PASS** | `title`, `abstract`, and `keywords` are byte-identical; the only differences are the intended `authors`/`affiliations`/`thanks` removal, the `html` format, and `linestretch`. |
| **Attribution honesty** | **MIXED** | Several unattributed author taxonomies and uncited institutional claims: `_valuation.qmd:26-29` (the agency/signaling/bounded-rationality list), `_model.qmd:15` footnote (the executive-statement → $\lambda$ mapping, "maps directly"), `_model.qmd:205, 222, 421`, `_calibration.qmd:6, 124`, `_appendix.qmd:407, 414, 509`, `_discussion.qmd:60`. Findings 53, 98, 154, 225, 246. |
| **"Internet Appendix", never "Appendix"** | **PASS (one exception)** | One bare reference: `_appendix.qmd:455`, "the statements elsewhere in this appendix". Finding 259. |
| **No `**Bold text.**` pseudo-headings in the main body** | **PASS (two judgment calls)** | Zero paragraph-level pseudo-headings in `_introduction.qmd`, `_calibration.qmd`, `_valuation.qmd`, `_discussion.qmd`, `_conclusion.qmd`. Two borderline constructions: six bold run-in labels in `_literature.qmd` (not named in `paper/AGENTS.md`, but the file is included by the introduction and renders as part of it — finding 29), and bold *list-item* labels at `_valuation.qmd:26-29` and `_discussion.qmd:21-24`, which are list labels rather than pseudo-headings but sit close to the line (findings 128, 157). Run-in labels in `_model.qmd` and `_appendix.qmd` are the sanctioned convention and were not flagged. |
| **Result labelling (Propositions 1–3, Numerical Finding 1)** | **MIXED** | The label is used correctly at `_valuation.qmd:45`, and Dario's dilemma is nowhere called a proposition. Three lapses: the `$\square$` QED box closing Numerical Finding 1 inside a section headed "A. Proofs" (finding 184); `_appendix.qmd:209` upgrading parts (iii)–(v) to "analytical motivation" against the taxonomy table's "Numerical" (finding 185); and `_conclusion.qmd:5` pluralizing to "numerical findings" (finding 175). Proposition 3(ii)'s method label also differs between `_model.qmd` ("fixed point") and the Internet Appendix and taxonomy table ("critical point") (finding 202). |
| **Numbers trace to an exhibit** | **NOT CHECKED (out of scope)** | Seven places where the prose is internally inconsistent and needs one check against the exhibit are flagged: findings 121, 122, 123, 238, 243, 244, 273. |

---

## Suggested order of work

1. **One mechanical pass for em-dashes**, file by file, starting with the abstract and the ~60 double-dash lines. This is the largest single change and touches nothing else.
2. **One claim-strength pass over the four summary locations** — abstract, introduction results paragraphs, `_valuation.qmd` Implications, conclusion — checking each summary sentence against the hedge attached to the result where it is derived (findings 3, 4, 9, 10, 12, 117–120, 169–174).
3. **Calibration vocabulary**: replace estimation language, relabel `@tbl-firms`, resolve the two internal contradictions (findings 88–97).
4. **The seven number-consistency checks** against exhibits (findings 121, 122, 123, 238, 243, 244, 273), plus the preemption-discount definition (286).
5. **Redundancy cuts** across abstract / introduction / conclusion and the §5 ↔ Internet Appendix H duplication (findings 287–291).
6. Everything else, section by section.

Fixes were not applied. If you want them made, the finance-writing skill's parallel per-section edit pattern works from this report.
