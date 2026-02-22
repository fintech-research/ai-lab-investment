### Paper overview

**Working title:** "Investing in Intelligence: Real Options, Default Risk, and Strategic Competition in AI Compute Infrastructure"

**Core contribution:** A unified model of irreversible capacity investment under demand uncertainty with regime switching, oligopoly competition, endogenous default, and diminishing returns calibrated to AI scaling laws. The model delivers three sets of results: (i) analytical characterization of optimal investment triggers and capacity in a duopoly with default risk, (ii) numerical solutions for richer specifications with N firms and dynamic training/inference allocation, and (iii) a "revealed beliefs" methodology for inferring AI labs' private probability assessments of transformative AI arrival from their observable investment decisions.

**Target journals:** JF, RFS, or Econometrica. The paper sits at the intersection of real options (corporate finance), industrial organization (oligopoly investment games), and technology economics. JF or RFS would emphasize the valuation and capital structure angles; Econometrica would emphasize the game-theoretic and inference aspects. I'd lean toward JF given the valuation and corporate finance framing, but the "revealed beliefs" angle could push it toward Econometrica.

---

## Phase 1: The base model (single firm, no competition, no default)

**Goal:** Establish the economic environment and solve the simplest version analytically. This becomes Section 2 of the paper and the benchmark against which all extensions are compared.

### 1.1 — Environment

- **Demand process with regime switching.** The demand shifter $X_t$ follows a GBM whose drift switches between two regimes:
  - Regime L (pre-adoption): $dX_t = \mu_L X_t \, dt + \sigma_L X_t \, dW_t$
  - Regime H (post-adoption): $dX_t = \mu_H X_t \, dt + \sigma_H X_t \, dW_t$
  - Transition L → H at Poisson rate $\lambda$ (arrival of "transformative AI" / mass enterprise adoption). Transition H → L either absent (absorbing) or at some small rate $\lambda'$ (temporary hype followed by disappointment). Start with absorbing for the analytical version.
  - $\mu_H \gg \mu_L$, capturing the 5-10× annual growth Dario describes post-adoption vs. the more uncertain pre-adoption trajectory.

- **Investment technology.** The firm holds an option to invest irreversibly in capacity $K$ at cost $I(K) = c \cdot K^\gamma$ with $\gamma \geq 1$ (convex costs — building larger data centers is proportionally or more than proportionally expensive due to power, cooling, land constraints). Investment has a **time-to-build** lag $\tau$ (1-2 years): capacity ordered at $t$ becomes available at $t + \tau$.

- **Revenue from capacity.** Once capacity is installed, the firm earns flow revenue:
$$\pi(K, X_t) = X_t \cdot K^\alpha, \quad \alpha \in (0,1)$$
  The concavity ($\alpha < 1$) captures diminishing returns to compute — more GPUs yield sublinear improvements in model quality and hence revenue. The parameter $\alpha$ maps to empirical scaling exponents from Kaplan et al. (2020) and Hoffmann et al. (2022). Operating costs are $\delta \cdot K$ per unit time (electricity, maintenance, depreciation).

- **Training vs. inference.** In the base model, abstract away from this distinction — all capacity serves inference. Introduce the split in Phase 3.

### 1.2 — Analytical solution (single firm)

Solve for the optimal investment trigger $X^*$ and optimal capacity $K^*$ as functions of model parameters. The approach follows Guo, Miao & Morellec (2005) for the regime-switching part and Pindyck (1988) for the capacity choice part.

**Method:**
- In each regime $s \in \{L, H\}$, the value of the option to invest satisfies a system of two coupled ODEs (one per regime), linked by the switching intensities.
- The value of installed capacity $V(X, K, s)$ is the expected present value of $(\pi - \delta K)$ under regime switching, which has a known closed-form (a weighted combination of GBM present values in each regime).
- The investment option value $F(X, s)$ satisfies smooth-pasting and value-matching conditions at the optimal trigger $X^*(s)$ in each regime.
- Optimal $K^*$ is found by the first-order condition $\partial V / \partial K = \partial I / \partial K$ at the trigger.

**Deliverables:**
- Closed-form (or semi-closed-form) expressions for $X^*(s)$, $K^*(s)$
- Comparative statics: how do $X^*$ and $K^*$ respond to $\lambda$ (arrival rate of transformative AI), $\sigma$ (demand volatility), $\alpha$ (scaling exponent), $\tau$ (time-to-build)?
- **Key insight to establish:** Higher $\lambda$ (more likely regime switch) lowers the investment trigger — firms invest sooner because waiting risks missing the boom. But the interaction with time-to-build $\tau$ is non-trivial: if $\tau$ is large, firms must invest even earlier, and the penalty for being wrong is larger.

**Tools:** SymPy for deriving and verifying the analytical solutions. Matplotlib for plotting comparative statics.

---

## Phase 2: Duopoly — the analytical core (Section 3 of the paper)

**Goal:** Introduce strategic interaction between two symmetric firms. This is the main analytical contribution. Solve for Markov-perfect equilibrium investment strategies.

### 2.1 — Setup

Two symmetric firms, each holding an option to invest in capacity. Demand is shared:
$$\pi_i(K_i, K_j, X) = X \cdot \frac{K_i^\alpha}{K_i^\alpha + K_j^\alpha}$$
or alternatively a Cournot inverse-demand structure:
$$P = X \cdot (K_i^\alpha + K_j^\alpha)^{-1/\eta}$$
where $\eta$ governs demand elasticity. The first (contest function) is simpler and might be preferable for the analytical version. The Cournot structure is more standard in IO.

**Decision:** I'd suggest using the **contest function** for the analytical duopoly and the **Cournot structure** for the numerical N-firm version.

### 2.2 — Equilibrium concept

Follow Huisman & Kort (2015): firms play a **preemption game** with endogenous timing and capacity. The equilibrium features:
- A **leader** who invests first at trigger $X_L^*$ with capacity $K_L^*$
- A **follower** who invests at trigger $X_F^* > X_L^*$ with capacity $K_F^*$
- The leader's trigger is pinned down by the **preemption condition**: the value of leading equals the value of following at $X_L^*$.

### 2.3 — Adding default risk

This is the novel theoretical contribution. Each firm finances investment with a mix of equity $E$ and debt $D$ with face value $F$ and coupon $c_D$. Default occurs at an endogenous boundary $X_D$ where equity value hits zero.

**Key modeling choice:** Follow Leland (1994) for the default structure. Equity holders choose $X_D$ to maximize equity value; debt is priced rationally. The investment option is held by equity holders, creating the standard risk-shifting incentive: equity is a call option on firm value, so equity holders prefer riskier strategies (larger $K$, earlier investment) than the first-best.

**The three-way interaction (the paper's main mechanism):**
1. **Competition** pushes investment earlier (lower $X^*$) — preemption effect (Grenadier 2002)
2. **Limited liability** pushes investment larger (higher $K^*$) — risk-shifting effect (Brander & Lewis 1986)
3. **Default risk** pushes back — the bankruptcy cost creates a countervailing force against excessive capacity

The equilibrium investment strategy reflects all three forces simultaneously. The central question is: which force dominates for plausible parameter values?

### 2.4 — Analytical approach

For the duopoly with default, full closed-form solutions are unlikely. The approach:

1. **Solve the follower's problem** in closed form (conditional on the leader having invested). This is essentially a single-firm problem with regime switching, diminishing returns, and default risk. It's a system of ODEs with free boundaries ($X_F^*$ for investment, $X_D^F$ for default).

2. **Solve the leader's problem** given the follower's strategy. The leader's payoff depends on the follower's future entry, which changes the leader's cash flows. This introduces a second free boundary (the follower's trigger) into the leader's value function.

3. **Characterize the preemption equilibrium.** The leader's trigger $X_L^*$ is the point where the value of leading equals the value of following. This can be characterized implicitly even if not in full closed form.

4. **Special cases with closed-form solutions:**
   - No default risk, no regime switching → recovers Huisman & Kort (2015)
   - No competition, with default risk → recovers Kumar & Yerramilli (2018) style results
   - No default risk, with regime switching → extends Huisman & Kort to regime switching (new)

   These nested cases build intuition and serve as verification for the numerical solution.

**Deliverables:**
- Propositions characterizing the equilibrium (existence, uniqueness, leader/follower asymmetry)
- Comparative statics propositions (analytically where possible, numerically otherwise):
  - Effect of $\lambda$ on equilibrium investment timing and capacity
  - Effect of leverage on competitive investment distortions
  - Interaction between competition and default risk
- **Key result to target:** A "competition-leverage spiral" — competition forces early investment → early investment requires more leverage (less revenue has been earned before investing) → more leverage amplifies risk-shifting → firms invest even more aggressively → some firms default in bad states. This mechanism could explain why the AI infrastructure race looks like it does.

**Tools:** SymPy for the nested closed-form cases. Pencil-and-paper for the propositions (SymPy is useful for verification but the ODE systems are standard enough that hand derivation is likely cleaner).

---

## Phase 3: The full model — numerical solution (Section 4)

**Goal:** Extend the model to N ≥ 3 firms, dynamic training/inference allocation, richer heterogeneity, and solve numerically.

### 3.1 — Extensions beyond the analytical duopoly

1. **N = 3 or 4 firms** (matching the actual market structure). Follow Bouis, Huisman & Kort (2009) for the N-firm extension. Sequential equilibrium: firms invest one at a time at distinct triggers $X_1^* < X_2^* < \cdots < X_N^*$, or clusters invest simultaneously.

2. **Training vs. inference allocation.** Post-investment, each firm allocates capacity between:
   - **Inference** $K_I$: generates current revenue $X \cdot K_I^\alpha / (\sum_j K_{I,j}^\alpha)$
   - **Training** $K_T$: generates a quality increment $\Delta q = \beta \log(K_T)$ that shifts the firm's demand in the next period (better model → more customers)

   This creates a dynamic trade-off: training sacrifices current revenue for future competitive advantage. The log specification is the scaling law.

3. **Firm heterogeneity.** Firms differ in:
   - Initial cash reserves $W_i$ (Google/Microsoft are cash-rich; Anthropic/OpenAI are not)
   - Existing capacity $K_i^0$ (first-mover advantages in GPU procurement)
   - Model quality $q_i^0$ (some firms start with better models)
   - Cost of capital $r_i$ (reflects market's assessment of default risk)

4. **Stochastic regime switching with learning.** The transition rate $\lambda$ is not known — firms learn about it from signals (e.g., benchmark improvements, internal research results). This sets up the "revealed beliefs" analysis in Phase 4.

### 3.2 — Numerical method

The problem is a system of coupled optimal stopping problems (one per firm) with free boundaries, regime switching, and possibly learning. The most natural approach:

**For the N-firm investment timing game:**
- Backward induction on the number of remaining investors. Solve the last firm's problem first (single-firm with N-1 competitors already in the market), then the second-to-last, etc.
- Each firm's value function solves an ODE in $X$ with regime switching. Use finite difference methods on a log-$X$ grid.
- The free boundaries (investment triggers, default triggers) are found iteratively.

**For the dynamic training/inference allocation:**
- Within each period, the allocation is a static optimization (given $K$, $X$, and competitor allocations, choose $K_T$ to maximize value). This is a fixed-point problem across firms.
- Across periods, the quality dynamics create a state variable. Discretize the quality space and solve by value function iteration.

**Libraries:**
- `numpy` and `scipy` for the core numerics (ODE solving via `scipy.integrate.solve_bvp` or finite differences, optimization via `scipy.optimize`)
- I'd actually suggest considering `numba` for JIT compilation of the value function iteration loops — these can be slow in pure NumPy when the state space is large (X × quality × regime × firm)
- `matplotlib` for figures
- SymPy for verifying analytical special cases against numerical output

### 3.3 — Deliverables

- Numerical solution of the full N-firm game for baseline calibration
- Figures showing equilibrium investment triggers, capacities, and default probabilities as functions of key parameters
- Comparison of the full numerical solution with the analytical duopoly to show which insights survive and which are modified

---

## Phase 4: Calibration and revealed beliefs (Section 5)

**Goal:** Calibrate the model to real-world AI infrastructure investment and develop the "revealed beliefs" methodology.

### 4.1 — Calibration

**Publicly available data points:**
- Revenue trajectories: Anthropic ($0 → $100M → $1B → $9-10B, reported in the interview), OpenAI (~$5-6B in 2025), Google Cloud AI revenue
- Compute costs: ~$10-15B per GW-year (Dario's estimate), GPU pricing (H100 at ~$25-30K, B200 at ~$30-40K)
- Capacity buildout: industry at ~10-15 GW in 2026, growing ~3× per year
- Scaling laws: $\alpha \approx 0.05-0.20$ from Kaplan et al. (2020) and Hoffmann et al. (2022) — the exponent relating compute to loss reduction (needs to be translated to a revenue-relevant metric)
- Capital structure: CoreWeave debt levels, Microsoft/Google/Amazon CapEx from 10-K filings, Anthropic's funding rounds
- Time-to-build: 18-36 months for large data center campuses (from industry reports)

**Parameters to calibrate:**
- $\mu_L, \mu_H, \sigma_L, \sigma_H$: demand process parameters. Can be estimated from the revenue trajectories above.
- $\lambda$: transition rate. This is the **key unobservable** — the whole point of the revealed-beliefs exercise.
- $\alpha$: scaling exponent. From the ML literature.
- $c, \gamma$: investment cost parameters. From GPU pricing and data center construction costs.
- $\delta$: operating cost. From electricity costs and depreciation schedules.
- $r$: discount rate. From WACC estimates for tech firms.
- $\tau$: time-to-build. From industry data.

### 4.2 — Revealed beliefs methodology

This is potentially the most striking part of the paper. The idea:

1. **Given the model**, a firm's observable investment decision $(X^*_{obs}, K^*_{obs})$ — the demand level at which it invested and the capacity it chose — is a deterministic function of all parameters including $\lambda$.

2. **All parameters except $\lambda$ are either observable or can be reasonably calibrated.** Revenue, costs, capital structure, and competitive landscape are public or estimable.

3. **Therefore, we can invert the model** to back out the $\lambda$ implied by each firm's investment behavior. This is the firm's "revealed belief" about the arrival rate of transformative AI.

4. **If firms know more about AI progress than the market** (which is almost certainly true — they see internal benchmarks, scaling curves, emergent capabilities before public release), then the revealed $\lambda$ from their investment decisions contains **private information about AI timelines**.

5. **External observers (investors, policymakers) can use this** to update their own beliefs. If Anthropic is investing as if $\lambda = 0.5$ (50% chance of regime switch per year), that's a strong signal about their internal assessment.

**Implementation:**
- For each major firm (or "stylized firm" representing each), plug observed investment levels and timing into the equilibrium conditions.
- Solve for the $\lambda$ that rationalizes observed behavior.
- Conduct sensitivity analysis: how robust is the inferred $\lambda$ to assumptions about other parameters?
- **Key figure:** A plot of "revealed $\lambda$" over time as firms ramp up investment. If the revealed $\lambda$ is increasing, the market should infer that firms are becoming more confident about near-term transformative AI.

**A subtlety:** Firms may also have strategic incentives to *distort* their investment relative to their true beliefs — e.g., investing aggressively to signal confidence and attract customers/investors, or investing conservatively to avoid alarming regulators. The model could incorporate this via a signaling extension (but this might be a separate paper).

### 4.3 — Deliverables

- Calibrated model with baseline parameter values and sources
- Table of revealed $\lambda$ estimates for stylized versions of major AI labs
- Sensitivity analysis figures
- Discussion of what investment patterns would be consistent with different $\lambda$ values (e.g., "if firms believe AGI is 2 years away, we should see investment of X GW at cost $Y; if 5 years away, Z GW at cost $W")

---

## Phase 5: Valuation (Section 6)

**Goal:** Use the model to value AI infrastructure firms and characterize how valuations depend on beliefs about $\lambda$.

### 5.1 — Firm valuation

The model produces firm value as a function of state variables $(X, s, K, D, q)$ — demand level, regime, installed capacity, debt, and model quality. Total firm value = equity + debt. Equity value is the residual claim after debt service, with an embedded default option.

**Key outputs:**
- **Equity value as a function of $\lambda$.** How much is an AI lab worth if $\lambda = 0.3$ vs. $\lambda = 0.7$? This gives the sensitivity of valuation to AI timeline beliefs.
- **Growth option decomposition.** What fraction of firm value comes from (a) assets-in-place (current inference revenue), (b) the option to expand capacity, (c) the option value of a regime switch? Following Berk, Green & Naik (1999), firms whose value is mostly in growth options have higher systematic risk.
- **Credit risk.** Default probabilities and credit spreads as a function of leverage and $\lambda$. Prediction: firms that are highly levered *and* have low $\lambda$ (slow adoption belief) face much higher credit spreads. Firms with high $\lambda$ can sustain more leverage because the regime switch bails them out.
- **The "Dario dilemma" quantified.** Using the model, compute: if Anthropic believes $\lambda = 0.5$ but buys capacity as if $\lambda = 0.3$ (conservative), what is the expected revenue left on the table? Conversely, if they buy as if $\lambda = 0.7$ (aggressive) but $\lambda = 0.3$, what is the default probability? This directly quantifies the asymmetric risk Dario described.

### 5.2 — Market implications

- **Cross-section of AI firm returns.** The model predicts that firms with more growth options (higher $\lambda$ sensitivity) have higher expected returns if the regime switch is priced risk. This connects to the asset pricing literature (Berk et al. 1999, Carlson et al. 2004).
- **The "inference premium."** Firms with more capacity allocated to inference (current revenue) should trade at lower multiples but with lower risk than firms with more capacity allocated to training (future quality). This is testable with data on GPU allocation.

---

## Phase 6: Paper writing (putting it all together)

### Proposed structure

1. **Introduction** (~5 pages). Motivate with the Dario interview numbers and the general AI infrastructure investment boom. State the three contributions: (i) model, (ii) calibration and revealed beliefs, (iii) valuation implications. Brief literature review.

2. **The Model** (~8 pages).
   - 2.1: Environment (demand, technology, financial structure)
   - 2.2: Single-firm benchmark (analytical)
   - 2.3: Duopoly equilibrium (analytical core)
   - 2.4: Key propositions and comparative statics

3. **Extensions and Numerical Analysis** (~8 pages).
   - 3.1: N-firm game
   - 3.2: Training vs. inference allocation
   - 3.3: Firm heterogeneity
   - 3.4: Numerical method and verification against analytical cases

4. **Calibration** (~6 pages).
   - 4.1: Data and parameter values
   - 4.2: Baseline results
   - 4.3: Sensitivity analysis

5. **Revealed Beliefs and Valuation** (~8 pages).
   - 5.1: Revealed $\lambda$ methodology
   - 5.2: Application to major AI labs
   - 5.3: Firm valuation and the growth option decomposition
   - 5.4: Credit risk and the competition-leverage spiral

6. **Discussion and Policy Implications** (~3 pages).
   - Market efficiency implications (can investors learn about AI timelines from observing lab behavior?)
   - Welfare: is the competitive equilibrium investment level socially optimal?
   - Regulatory implications (should policymakers be concerned about over-investment and systemic default risk?)

7. **Conclusion** (~2 pages).

**Appendices:** Proofs, numerical method details, data sources, robustness checks.

---

## Sequencing and timeline

Here's the order I'd suggest working in, with dependencies:

| Step | Task | Depends on | Estimated effort |
|------|-------|------------|-----------------|
| 1 | Write down the full model environment | — | 1 week |
| 2 | Solve the single-firm benchmark (Phase 1) analytically | 1 | 2 weeks |
| 3 | Implement and verify Phase 1 numerically in Python | 2 | 1 week |
| 4 | Solve the duopoly without default analytically | 2 | 2-3 weeks |
| 5 | Add default risk to the duopoly | 4 | 2-3 weeks |
| 6 | Code the full numerical solution (Phase 3) | 3, 5 | 3-4 weeks |
| 7 | Gather calibration data | — (can run in parallel) | 2 weeks |
| 8 | Calibrate and run revealed-beliefs exercise | 6, 7 | 2-3 weeks |
| 9 | Valuation analysis | 6, 8 | 2 weeks |
| 10 | Write the paper | All above | 4-6 weeks |
| 11 | Revise, polish, circulate | 10 | 2-3 weeks |

**Total:** Roughly 5-7 months of part-time work (assuming this isn't your only project).

---

## Immediate next step

I'd suggest we start with **Step 1-2**: writing down the model environment precisely and solving the single-firm benchmark. This forces all the modeling choices to be made explicit and provides the foundation everything else builds on. Want me to draft the formal model setup — the full set of assumptions, notation, and the single-firm HJB equations to solve?
