# YouTube descriptions

Descriptions for the seven videos accompanying *Investing in Artificial General Intelligence* (Vincent Grégoire, HEC Montréal). Chapter timestamps are computed from the rendered scene durations.

Video links:

| Video | Link |
|---|---|
| Explainer | https://youtu.be/k-KJjKV449U |
| Part 1 — The Environment | https://youtu.be/ICHPUIG7yl4 |
| Part 2 — The Single-Firm Benchmark | https://youtu.be/2e08FFt7oC0 |
| Part 3 — The Pre-AGI Option | https://youtu.be/2GWxoMXoQGE |
| Part 4 — Duopoly, Debt & Default | https://youtu.be/u2NzcfgE1gs |
| Part 5 — The Preemption Equilibrium | https://youtu.be/zlJEPksGxhU |
| Part 6 — Calibration & Credit Risk | https://youtu.be/T56Mxp6GVpg |

---

## Explainer (https://youtu.be/k-KJjKV449U)

The leading AI labs are committing hundreds of billions of dollars to compute that becomes worthless if their bet on artificial general intelligence is wrong. How should a frontier lab decide *when* to invest, *how much* capacity to build, and how to split that capacity between training tomorrow's models and serving today's customers?

This is a 3Blue1Brown-style explainer of my paper "Investing in Artificial General Intelligence." In about ten minutes it walks through a real-options model with regime-switching demand, duopoly competition, and endogenous default — and the headline results: training intensity is pinned down by beliefs about AI timelines rather than by competition, optimism backed by training literally extends a firm's solvency ("faith-based survival"), and Dario's dilemma — why underinvesting destroys more expected value, while overinvesting concentrates the tail risk of bankruptcy.

Want the full derivations and proofs? This explainer is the summary; the six-part walkthrough series goes through the model section by section, with every appendix proof worked out on screen:

- Part 1 — The Environment: https://youtu.be/ICHPUIG7yl4
- Part 2 — The Single-Firm Benchmark: https://youtu.be/2e08FFt7oC0
- Part 3 — The Pre-AGI Option: https://youtu.be/2GWxoMXoQGE
- Part 4 — Duopoly, Debt & Default: https://youtu.be/u2NzcfgE1gs
- Part 5 — The Preemption Equilibrium: https://youtu.be/zlJEPksGxhU
- Part 6 — Calibration & Credit Risk: https://youtu.be/T56Mxp6GVpg

🔗 Useful Links:

- The paper: https://papers.ssrn.com/sol3/papers.cfm?abstract_id=6305300
- Companion blog post: https://vincent.codes.finance/posts/vibe-research-fable/

🐍 More Vincent Codes Finance:

- ✍🏻 Blog: https://vincent.codes.finance
- 🐦 X: https://twitter.com/CodesFinance
- 😺 GitHub: https://github.com/Vincent-Codes-Finance
- 👨‍💼 LinkedIn: https://www.linkedin.com/company/vincent-codes-finance/
- 🎓 Academic website: https://www.vincentgregoire.com/

🔖 Chapters:

0:00 The $660 billion bet
0:42 Three decisions, one bet
1:23 Regime-switching demand
2:29 One stock of GPUs, two uses
3:31 Waiting has value
4:47 Beliefs pin the split
5:39 Competition compresses timing
6:52 Faith-based survival
8:00 Who believes what
8:50 Dario's dilemma
10:01 What to remember

---

## Part 1 — The Environment (https://youtu.be/ICHPUIG7yl4)

This is Part 1 of the full derivation-and-proof walkthrough of "Investing in Artificial General Intelligence" — the companion series to the short explainer (https://youtu.be/k-KJjKV449U), where we go through the model section by section and work out every derivation, including the appendix proofs, on screen.

Part 1 builds the foundation. We set up the demand environment — a geometric Brownian motion whose drift switches at a Poisson "AGI arrival" — explain what the risk-adjusted discount rate and drifts actually mean, introduce the convex investment cost and the training/inference allocation, and then assemble the mathematical toolkit used in every later part: the growing perpetuity, the characteristic equation and its roots, and the regime-switching Hamilton-Jacobi-Bellman equation. We close with Assumption 1 and the baseline calibration.

Series:

- Part 2 — The Single-Firm Benchmark: https://youtu.be/2e08FFt7oC0
- Part 3 — The Pre-AGI Option: https://youtu.be/2GWxoMXoQGE
- Part 4 — Duopoly, Debt & Default: https://youtu.be/u2NzcfgE1gs
- Part 5 — The Preemption Equilibrium: https://youtu.be/zlJEPksGxhU
- Part 6 — Calibration & Credit Risk: https://youtu.be/T56Mxp6GVpg

🔗 Useful Links:

- The paper: https://papers.ssrn.com/sol3/papers.cfm?abstract_id=6305300
- Companion blog post: https://vincent.codes.finance/posts/vibe-research-fable/

🐍 More Vincent Codes Finance:

- ✍🏻 Blog: https://vincent.codes.finance
- 🐦 X: https://twitter.com/CodesFinance
- 😺 GitHub: https://github.com/Vincent-Codes-Finance
- 👨‍💼 LinkedIn: https://www.linkedin.com/company/vincent-codes-finance/
- 🎓 Academic website: https://www.vincentgregoire.com/

🔖 Chapters:

0:00 Introduction & series overview
0:40 Regime-switching demand
2:13 What r, mu, and sigma really are
3:41 Technology and the cost of capacity
5:18 Training versus inference
7:07 Toolkit 1: the growing perpetuity
8:39 Toolkit 2: the characteristic equation
10:54 Toolkit 3: the regime-switch HJB
12:57 Assumption 1: admissibility
14:54 Baseline calibration

---

## Part 2 — The Single-Firm Benchmark (https://youtu.be/2e08FFt7oC0)

Part 2 of the full walkthrough of "Investing in Artificial General Intelligence." (Start with the explainer for the big picture: https://youtu.be/k-KJjKV449U; Part 1 builds the toolkit this video relies on: https://youtu.be/ICHPUIG7yl4.)

Here we solve the single firm's problem from the ground up. We derive the installed value in both regimes, then build the effective revenue coefficient A_eff — the object that combines today's inference revenue with the expected post-AGI training prize — step by step, including the expectation over the random AGI arrival time. We solve the H-regime option, derive the investment trigger with its option premium, reproduce the option-value figure live from the model code, and then prove Proposition 1, Steps 1–4: the closed-form optimal capacity and why it is independent of both the training fraction and the arrival rate.

Series:

- Part 1 — The Environment: https://youtu.be/ICHPUIG7yl4
- Part 3 — The Pre-AGI Option: https://youtu.be/2GWxoMXoQGE
- Part 4 — Duopoly, Debt & Default: https://youtu.be/u2NzcfgE1gs
- Part 5 — The Preemption Equilibrium: https://youtu.be/zlJEPksGxhU
- Part 6 — Calibration & Credit Risk: https://youtu.be/T56Mxp6GVpg

🔗 Useful Links:

- The paper: https://papers.ssrn.com/sol3/papers.cfm?abstract_id=6305300
- Companion blog post: https://vincent.codes.finance/posts/vibe-research-fable/

🐍 More Vincent Codes Finance:

- ✍🏻 Blog: https://vincent.codes.finance
- 🐦 X: https://twitter.com/CodesFinance
- 😺 GitHub: https://github.com/Vincent-Codes-Finance
- 👨‍💼 LinkedIn: https://www.linkedin.com/company/vincent-codes-finance/
- 🎓 Academic website: https://www.vincentgregoire.com/

🔖 Chapters:

0:00 Introduction
0:30 The toolkit from Part 1
1:17 Installed value in regime H
2:40 Installed value in regime L
4:12 Deriving A effective
6:22 Sanity checks: nested special cases
7:03 Option value in regime H
8:23 Deriving the H-regime trigger
9:43 The option-value figure, live
10:49 Proposition 1: trigger and NPV at the trigger
12:21 Proposition 1: substituting back
13:21 Proposition 1: the closed-form capacity
15:32 Comparative statics in regime H
16:35 Where we are, and what's next

---

## Part 3 — The Pre-AGI Option (https://youtu.be/2GWxoMXoQGE)

Part 3 of the full walkthrough of "Investing in Artificial General Intelligence." (Explainer: https://youtu.be/k-KJjKV449U. This part picks up directly from Part 2: https://youtu.be/2e08FFt7oC0.)

This is the analytically subtlest part. We write the low-regime HJB as a forced Euler ODE, solve for its homogeneous and particular pieces, and then give the full proof that the homogeneous coefficient is exactly zero under Assumption A3 — ruling out both signs — so that the pre-AGI option value collapses to a single power term. We then prove the interior optimal training fraction exists and is unique (Inada conditions, intermediate value theorem, strict concavity), derive its closed form, and work through the comparative statics: more optimistic firms train more, and the split is independent of the low-regime growth rate.

Series:

- Part 1 — The Environment: https://youtu.be/ICHPUIG7yl4
- Part 2 — The Single-Firm Benchmark: https://youtu.be/2e08FFt7oC0
- Part 4 — Duopoly, Debt & Default: https://youtu.be/u2NzcfgE1gs
- Part 5 — The Preemption Equilibrium: https://youtu.be/zlJEPksGxhU
- Part 6 — Calibration & Credit Risk: https://youtu.be/T56Mxp6GVpg

🔗 Useful Links:

- The paper: https://papers.ssrn.com/sol3/papers.cfm?abstract_id=6305300
- Companion blog post: https://vincent.codes.finance/posts/vibe-research-fable/

🐍 More Vincent Codes Finance:

- ✍🏻 Blog: https://vincent.codes.finance
- 🐦 X: https://twitter.com/CodesFinance
- 😺 GitHub: https://github.com/Vincent-Codes-Finance
- 👨‍💼 LinkedIn: https://www.linkedin.com/company/vincent-codes-finance/
- 🎓 Academic website: https://www.vincentgregoire.com/

🔖 Chapters:

0:00 Introduction
0:18 Where we left off
1:15 The L-regime HJB equation
3:18 A non-homogeneous Euler ODE
4:17 Homogeneous solution
5:48 Particular solution
8:22 When does the simple form apply?
9:39 Step 5b: ruling out A1 > 0
11:50 Step 5b: ruling out A1 < 0
13:39 Two conditions, one unknown
15:23 The interior training fraction
18:15 Comparative statics of the training fraction
19:46 The role of lambda
21:19 What we proved today

---

## Part 4 — Duopoly, Debt & Default (https://youtu.be/u2NzcfgE1gs)

Part 4 of the full walkthrough of "Investing in Artificial General Intelligence." (Explainer: https://youtu.be/k-KJjKV449U. Parts 1–3 build the single-firm model this part extends: starting at https://youtu.be/ICHPUIG7yl4.)

Now there are two firms and there is debt. We set up the regime-specific Tullock contests and prove their key properties, build the duopoly effective revenue coefficient, and work through the par-issuance financing concession. Then the centerpiece: a full Leland-style derivation of the endogenous default boundary, the one-way coupling that makes the single-boundary formula exact (with its conservative ~3% bias), and the complete proof of Proposition 2 — faith-based survival. We derive both thresholds in closed form (the A_eff-channel threshold and the exact net threshold including the markup channel) and show when optimism actually lowers the default boundary.

Series:

- Part 1 — The Environment: https://youtu.be/ICHPUIG7yl4
- Part 2 — The Single-Firm Benchmark: https://youtu.be/2e08FFt7oC0
- Part 3 — The Pre-AGI Option: https://youtu.be/2GWxoMXoQGE
- Part 5 — The Preemption Equilibrium: https://youtu.be/zlJEPksGxhU
- Part 6 — Calibration & Credit Risk: https://youtu.be/T56Mxp6GVpg

🔗 Useful Links:

- The paper: https://papers.ssrn.com/sol3/papers.cfm?abstract_id=6305300
- Companion blog post: https://vincent.codes.finance/posts/vibe-research-fable/

🐍 More Vincent Codes Finance:

- ✍🏻 Blog: https://vincent.codes.finance
- 🐦 X: https://twitter.com/CodesFinance
- 😺 GitHub: https://github.com/Vincent-Codes-Finance
- 👨‍💼 LinkedIn: https://www.linkedin.com/company/vincent-codes-finance/
- 🎓 Academic website: https://www.vincentgregoire.com/

🔖 Chapters:

0:00 Introduction
0:21 Where we are
1:17 Regime-specific Tullock contests
2:54 Three properties, with proofs
4:44 The duopoly A effective
5:36 Capital structure
7:13 The default boundary: Leland derivation
10:37 The one-way coupling, made exact
13:51 Proposition 2(i): leverage and the coupon
14:27 Proposition 2(ii): the faith condition
16:34 The opposing markup channel
17:56 The exact net threshold
20:11 Sign at the optimum
21:25 Parts (iii) and (iv): substitution and rivals
22:46 Equity and debt values
25:17 Leverage and the margin of safety
26:44 What we proved

---

## Part 5 — The Preemption Equilibrium (https://youtu.be/zlJEPksGxhU)

Part 5 of the full walkthrough of "Investing in Artificial General Intelligence." (Explainer: https://youtu.be/k-KJjKV449U. This part builds on the duopoly setup in Part 4: https://youtu.be/u2NzcfgE1gs.)

How do two firms time their entry when each fears being preempted? We set up the timing game, solve the follower's problem with its separable reduction and the elasticity wedge that makes the follower build at far larger scale, and handle the leader's two-phase value. Then we prove Proposition 3: existence of the preemption trigger by the intermediate value theorem, uniqueness via strict concavity of the value gap (analytic at zero leverage, computational with debt), and — the slickest argument in the paper — the role invariance of the training fraction, where the contest terms cancel exactly so leader, follower, and monopolist all choose the same split.

Series:

- Part 1 — The Environment: https://youtu.be/ICHPUIG7yl4
- Part 2 — The Single-Firm Benchmark: https://youtu.be/2e08FFt7oC0
- Part 3 — The Pre-AGI Option: https://youtu.be/2GWxoMXoQGE
- Part 4 — Duopoly, Debt & Default: https://youtu.be/u2NzcfgE1gs
- Part 6 — Calibration & Credit Risk: https://youtu.be/T56Mxp6GVpg

🔗 Useful Links:

- The paper: https://papers.ssrn.com/sol3/papers.cfm?abstract_id=6305300
- Companion blog post: https://vincent.codes.finance/posts/vibe-research-fable/

🐍 More Vincent Codes Finance:

- ✍🏻 Blog: https://vincent.codes.finance
- 🐦 X: https://twitter.com/CodesFinance
- 😺 GitHub: https://github.com/Vincent-Codes-Finance
- 👨‍💼 LinkedIn: https://www.linkedin.com/company/vincent-codes-finance/
- 🎓 Academic website: https://www.vincentgregoire.com/

🔖 Chapters:

0:00 Introduction
0:31 The timing game
1:49 The follower's problem
3:12 Separable reduction of the follower
4:55 Follower capacity: the elasticity wedge
7:45 The leader's problem
9:21 Discounting conventions
10:52 Rent equalization
12:02 Proposition 3(i): existence
13:53 Proposition 3(i): uniqueness
16:35 Proposition 3(ii): role invariance
19:45 Parts (iii)-(v): numerical findings
20:56 The competition effect
22:18 Summary and what's next

---

## Part 6 — Calibration & Credit Risk (https://youtu.be/T56Mxp6GVpg)

Part 6, the finale of the full walkthrough of "Investing in Artificial General Intelligence." (Explainer: https://youtu.be/k-KJjKV449U. The full series starts at Part 1: https://youtu.be/ICHPUIG7yl4.)

We take the solved model to numbers. We walk through the stylized calibration and the four AI-lab archetypes, invert the model to read each lab's implied beliefs about AI timelines from its training intensity, and then develop the quantitative implications: the value decomposition, credit spreads and first-passage default probabilities, and Dario's dilemma — why conservative underinvestment costs more expected value while aggressive overinvestment carries roughly eight times the tail default risk. We close with the equity-value concavity, the robustness checks, the testable predictions, and a recap of what is proved analytically versus computed.

Series:

- Part 1 — The Environment: https://youtu.be/ICHPUIG7yl4
- Part 2 — The Single-Firm Benchmark: https://youtu.be/2e08FFt7oC0
- Part 3 — The Pre-AGI Option: https://youtu.be/2GWxoMXoQGE
- Part 4 — Duopoly, Debt & Default: https://youtu.be/u2NzcfgE1gs
- Part 5 — The Preemption Equilibrium: https://youtu.be/zlJEPksGxhU

🔗 Useful Links:

- The paper: https://papers.ssrn.com/sol3/papers.cfm?abstract_id=6305300
- Companion blog post: https://vincent.codes.finance/posts/vibe-research-fable/

🐍 More Vincent Codes Finance:

- ✍🏻 Blog: https://vincent.codes.finance
- 🐦 X: https://twitter.com/CodesFinance
- 😺 GitHub: https://github.com/Vincent-Codes-Finance
- 👨‍💼 LinkedIn: https://www.linkedin.com/company/vincent-codes-finance/
- 🎓 Academic website: https://www.vincentgregoire.com/

🔖 Chapters:

0:00 Introduction
0:16 From theory to numbers
1:02 A stylized calibration
4:01 Four stylized archetypes
6:05 Reading beliefs from allocations
8:35 Baseline magnitudes
10:05 What a lambda means
10:49 Where the value sits
12:21 Credit spreads
14:03 Default probability
15:52 The cost of wrong beliefs
17:46 The dilemma, quantified
19:35 Equity value and timeline news
20:39 Robustness, rapid fire
22:07 What the data could say
23:15 What is proved vs computed
