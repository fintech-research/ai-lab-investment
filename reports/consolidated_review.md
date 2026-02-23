# Consolidated Referee Report and Revision Plan

## Summary of Reports

Two independent referee reports were received. Referee A (Claude) recommends **Major Revision**; Referee B (ChatGPT) recommends **Reject (encourage resubmission after substantial revision)**. Both referees agree that:

- The training-inference allocation mechanism is genuinely novel and interesting
- The "faith-based survival" idea is economically compelling
- The revealed beliefs methodology is creative
- The paper is ambitious, timely, and clearly written

However, both reports converge on a **shared set of critical concerns** that must be addressed before the paper can be considered for a top journal.

---

## Merged Major Concerns

### 1. L-Regime Option Value Derivation Is Incorrect (Critical Priority)

**Both referees independently flag this as the most serious issue.**

The paper claims the L-regime option value takes the form $F_L(X) = B \cdot X^{\beta_H}$, using the H-regime characteristic exponent, justified by the statement that "the investment option value is driven by H-regime expectations." Both referees argue this is incorrect.

In a regime-switching stopping problem, the L-regime option value satisfies the coupled HJB equation:

$$\frac{1}{2}\sigma_L^2 X^2 F_L'' + \mu_L X F_L' + \tilde{\lambda}[F_H(X) - F_L(X)] - r F_L = 0$$

The correct general solution is:

$$F_L(X) = A_1 X^{\beta_L^+} + C X^{\beta_H}$$

where:
- $A_1 X^{\beta_L^+}$ is the **homogeneous solution** with exponents determined by L-regime parameters and $(r + \tilde{\lambda})$
- $C X^{\beta_H}$ is a **particular solution** from the regime-switching term

The paper's claimed form $F_L = B X^{\beta_H}$ sets $A_1 = 0$, which requires either $\beta_L^+ = \beta_H$ (identical roots) or a specific limiting argument (e.g., $\tilde{\lambda} \to \infty$). Neither is established.

**This error propagates to:**
- The investment trigger (Eq. 11)
- The smooth-pasting conditions
- Proposition 1 comparative statics
- The duopoly equilibrium
- The revealed beliefs inversion

**Interestingly, the code (`base_model.py`) already computes both the particular solution coefficient $C$ and a homogeneous term $D_L X^{\beta_L}$ (lines 170-213), and Figure 4's discussion references $C$. The paper's text simply doesn't reflect the actual solution structure the code implements.**

**Action:** Rederive the L-regime option value using the correct coupled ODE system. Verify all downstream results. This is the single highest-priority task.

### 2. Proofs Are Proof Sketches, Not Proofs (High Priority)

Both referees note that the appendix proofs do not meet top-journal standards:

| Proposition | Status per Referees |
|:---|:---|
| **Prop 1** (Interior $\phi^*$) | Boundary arguments are "too informal" (B). Correct but imprecise (A). |
| **Prop 2** (Default boundary) | Loose wording; confusing leverage-training substitution (B). Sign conditions need precision (A). |
| **Prop 3** (Preemption equilibrium) | Existence delegated to Huisman & Kort; part (ii) only "verified numerically" (both). Proof of part (ii) contains an error: claims leader earns $X \cdot K_L^\alpha$ "regardless of $\phi$" during monopoly, inconsistent with L-regime revenue depending on $(1-\phi)K$ (B). |
| **Prop 4** (N-firm equilibrium) | Mostly numerical observations stated as propositions (both). |
| **Prop 5** (Asymmetric dilemma) | Taylor expansion + "verified numerically" is not a proof (both). Third derivative arguments are not computed or bounded (A). |

**Action:** Either prove propositions rigorously or downgrade them to numerical findings. For the duopoly model (Props 1-3), we should aim for rigorous proofs verified via sympy. For Props 4-5, reframe as numerical findings.

### 3. Overclaiming of "Closed-Form" Results

Both referees note that the paper's "closed-form" claim is overstated. The triggers are closed-form *conditional on* $K^*$ and $\phi^*$, which themselves require numerical optimization in the general (L-regime with regime switching) case.

**Referee A:** "The claim of closed-form investment triggers is somewhat overstated."
**Referee B:** "The paper repeatedly emphasizes 'closed-form' solutions and formal propositions, but many of the key results are [only partially derived, dependent on unproven assertions, established numerically, or internally inconsistent]."

**Action:** Be precise about what is analytically derived vs. what is numerical. The H-regime single-firm trigger and capacity have genuine closed-form expressions. The L-regime trigger with regime switching, the duopoly equilibrium, and the N-firm game are all numerical. Qualify the abstract and introduction accordingly.

### 4. Revealed Beliefs Identification Is Weak (High Priority)

Both referees identify serious problems with the revealed beliefs exercise:

**a) Extreme sensitivity (both):** $\sigma_H \pm 25\%$ shifts Anthropic-like $\hat{\lambda}$ from 0.003 to 0.90---spanning the entire parameter space.

**b) Heterogeneous demand parameters (A):** The inversion assumes all firms face identical demand-side parameters. This is implausible given different business models (Google = diversified cloud, CoreWeave = GPU lessor, Anthropic = API access, OpenAI = consumer product).

**c) Training fraction is diagnostic, not identifying moment (A):** The paper claims two moments but only uses CapEx/Revenue for the inversion; $\hat{\phi}$ is a post-hoc diagnostic.

**d) Many parameters are jointly influential (B):** Cost convexity, operating cost, discount rate, revenue elasticities, contest structure, leverage---all unobserved and jointly influential. The exercise is "better viewed as a structural thought experiment."

**e) Timing lag (A):** 2025 CapEx reflects 2023-2024 commitments.

**Action:** Reframe the entire revealed beliefs section as an "illustrative calibration exercise" (the paper partially does this already but inconsistently). Report ordinal rankings as the robust finding. Consider implementing a proper two-moment minimum-distance estimator, or explicitly frame as partial identification.

### 5. Scope Is Too Broad / Paper Tries to Do Too Much

**Referee B** is especially emphatic: "The paper is trying to do too much at once: new theory model, closed-form results, duopoly preemption game, N-firm extension, endogenous default, calibration, revealed-beliefs inversion, policy implications."

**Referee A** makes a similar point through specific concerns about each component.

**Both referees suggest narrowing scope.** Referee B offers two paths:
- **Option A (theory-first):** Focus on core model + 1-2 robust propositions + rigorous proofs. Keep calibration minimal.
- **Option B (quantitative/modeling):** Be explicit that results are numerical. Recast propositions as numerical findings. Build transparent sensitivity analysis.

**Action:** We pursue a hybrid: tighten the duopoly model as the rigorous analytical core, be explicit that the N-firm extension and revealed beliefs are numerical/illustrative, and downplay their importance relative to the core duopoly theory.

### 6. Tullock Contest Specification (Moderate Priority)

**Referee A** questions the Tullock contest choice:
- Revenue depends on *relative* capacity, which fits a zero-sum share game but not a growing market
- The transition from single-firm to duopoly revenue is discontinuous as $K_j \to 0$
- A Cournot specification may be more appropriate

**Action:** Provide economic justification for Tullock. Mention Cournot as robustness check (Appendix F claims it preserves results but provides no details). At minimum, discuss whether qualitative results survive.

### 7. Static Training Fraction (Moderate Priority)

**Referee A** notes that $\phi$ fixed at investment time is a significant limitation, especially given inference-time scaling (o1/o3, DeepSeek R1). The static $\phi$ drives key results: faith-based survival requires ex-ante commitment, and revealed beliefs requires comparing observed $\hat{\phi}$ to static $\phi^*$.

**Action:** Provide a time-scale argument for why static $\phi$ is a reasonable first approximation (large training runs take weeks/months). Discuss inference-time scaling as a limitation. Consider a brief dynamic extension in the appendix, even if solved numerically.

### 8. Literature Gaps

Both referees identify missing literatures:
- **Technology adoption / R&D races** (both): Katz & Shapiro 1986, Farrell & Saloner 1986, patent race models
- **R&D vs. production capacity** in real options (A): Dixit & Pindyck Ch. 11
- **Empirical AI investment** (A): Babina et al. 2024, Eisfeldt et al. 2024
- **VC/startup finance** (A): Gompers & Lerner 2004 (relevant since Anthropic/OpenAI are VC-backed)
- **Overstatement of novelty** (B): Less "this paper combines X+Y+Z," more focus on the one genuinely new mechanism

### 9. Specific Technical Issues

- **Eq. 7:** $\tilde{\lambda}$ in $A_{\text{eff}}$ creates an implicit fixed-point equation. Clarify whether it's evaluated at the firm's own $(K, \phi)$ or equilibrium values. (A)
- **Prop 3 proof, Part (ii):** Leader's monopoly-phase revenue is claimed to be independent of $\phi$, but L-regime revenue depends on $(1-\phi)K$. (B)
- **Default boundary derivation:** Uses L-regime characteristic root but the regime-switching term should modify this. (A)
- **Notation:** Distinguish exogenous $\lambda_0$ vs. endogenous $\tilde{\lambda}$; partial vs. equilibrium comparative statics. (B)
- **WACC heterogeneity:** Paper uses common $r=0.12$ but Table 1 shows firm-specific WACCs ranging 0.10-0.18. (A)

---

## Revision Plan

### Phase 1: Fix the Mathematical Core (Highest Priority)

**Goal:** Rigorously derive the coupled regime-switching option value and verify all closed-form results.

#### 1.1 Derive the correct L-regime option value using sympy

Create a sympy module that:
1. Defines the coupled ODE system for $F_L(X)$ and $F_H(X)$ in the regime-switching stopping problem
2. Solves the homogeneous and particular solutions symbolically
3. Applies boundary conditions (value-matching, smooth-pasting) symbolically
4. Derives the investment trigger, optimal capacity, and training fraction conditions
5. Verifies the H-regime results (which should be correct as they're standard)
6. Shows explicitly under what conditions (if any) the paper's simplified $F_L = B X^{\beta_H}$ is valid

**Deliverables:**
- `src/ai_lab_investment/models/symbolic_duopoly.py` --- sympy derivation
- Updated `_appendix.qmd` with rigorous derivations
- Corrected `_model.qmd` Section 2.3.3

#### 1.2 Update the numerical code to match the correct solution

The code in `base_model.py` already computes both the particular solution coefficient $C$ and a homogeneous term $D_L X^{\beta_L}$, which is more correct than the paper text. Verify this implementation against the sympy derivation and ensure consistency.

**Deliverables:**
- Verified `base_model.py` and `duopoly.py`
- Numerical tests comparing analytical vs. numerical solutions

#### 1.3 Restate Propositions 1-2 with correct expressions

Update the propositions and their proofs to use the correct option value structure. Determine which comparative statics survive and which are modified.

### Phase 2: Tighten the Duopoly Proofs

**Goal:** Make Propositions 1-3 rigorous or honestly qualified.

#### 2.1 Proposition 1 (Interior $\phi^*$)
- Write a formal lemma with explicit derivatives and limits at $\phi \to 0$ and $\phi \to 1$
- State the Inada condition mechanism precisely
- Verify comparative statics via implicit differentiation (sympy)

#### 2.2 Proposition 2 (Default boundary)
- Tighten sign conditions for $\partial A_{\text{eff}} / \partial \tilde{\lambda}$
- Clarify what is held fixed in each comparative static
- Fix the leverage-training substitution wording (leverage affects numerator, not $A_{\text{eff}}$)

#### 2.3 Proposition 3 (Preemption equilibrium)
- Fix Part (ii) proof: the claim that monopoly-phase revenue is independent of $\phi$ is wrong (L-regime revenue depends on $(1-\phi)K$)
- If Part (ii) cannot be proved analytically, downgrade to "Numerical Finding" with appropriate caveats
- Verify existence/uniqueness conditions for the enriched payoff functions (not just cite Huisman & Kort)

### Phase 3: Downgrade Non-Duopoly Results (Moderate Priority)

**Goal:** Be honest about what is analytical vs. numerical.

#### 3.1 Proposition 4 (N-firm equilibrium)
- Reframe as "Numerical Finding 1" or "Computational Result"
- State clearly that existence and properties are established computationally
- Remove "Proposition" label

#### 3.2 Proposition 5 (Asymmetric dilemma)
- Reframe as "Numerical Finding 2"
- The Taylor expansion argument is a useful heuristic but not a proof
- Keep the economic intuition but be explicit about the scope of verification

#### 3.3 Revealed beliefs section
- Frame consistently as "illustrative calibration"
- Remove language suggesting "identification" or "estimation"
- Report ordinal rankings as the robust result
- Be upfront about extreme sensitivity to $\sigma_H$

### Phase 4: Adjust Claims and Framing

#### 4.1 Abstract and introduction
- Remove or qualify "closed-form" claims
- State clearly: H-regime single-firm trigger is closed-form; duopoly trigger involves numerical optimization over $(K, \phi)$; N-firm game is fully numerical
- Emphasize the training-inference allocation as the key novel mechanism
- De-emphasize "feature stacking" (combining real options + regime switching + Tullock + default + scaling laws)

#### 4.2 Literature review
- Add technology adoption / R&D race / patent race literature
- Add Dixit & Pindyck Ch. 11 connection
- Reduce "this is the first paper to combine X+Y+Z" rhetoric
- More cleanly separate: formal theory contribution, institutional motivation, sector application

#### 4.3 Model section
- Justify Tullock contest economically (or present Cournot as an alternative)
- Discuss static $\phi$ limitation more carefully; provide time-scale argument
- Unify notation: state Eq. 2 for general N-firm case from the start
- Clarify the fixed-point nature of $\tilde{\lambda}$ in $A_{\text{eff}}$

#### 4.4 Discussion / Limitations
- Add discussion of inference-time scaling (o1/o3, DeepSeek R1)
- Note that the Leland default framework fits poorly for VC-backed firms
- Discuss the absorbing H-regime assumption and its implications

### Phase 5: Sympy Verification Module

**Goal:** Build a symbolic verification module that serves as both a research tool and a reproducibility guarantee.

The module should:
1. Derive the characteristic equations symbolically
2. Verify value-matching and smooth-pasting conditions
3. Compute comparative statics via symbolic differentiation
4. Generate LaTeX expressions that can be directly pasted into the paper
5. Numerically verify the sympy solutions against `base_model.py` and `duopoly.py`

This addresses the core concern of both referees: that the mathematical claims need to be verified rigorously. Having a sympy module that derives everything from first principles provides both verification and a permanent record of the correct derivations.

---

## Priority Order

| Priority | Task | Effort | Impact |
|:---------|:-----|:-------|:-------|
| 1 | Fix L-regime option value derivation (1.1) | High | Critical --- everything else depends on this |
| 2 | Sympy verification of duopoly model (1.2, 5) | High | Provides rigorous foundation |
| 3 | Tighten Props 1-3 proofs (2.1-2.3) | Medium | Required for theory contribution |
| 4 | Downgrade Props 4-5, reframe revealed beliefs (3.1-3.3) | Low | Framing changes, mostly editorial |
| 5 | Adjust claims in abstract/intro (4.1) | Low | Important signaling to referees |
| 6 | Literature additions (4.2) | Low | Straightforward |
| 7 | Model justification and limitations (4.3-4.4) | Medium | Addresses secondary concerns |

## What the Correct Solution Likely Looks Like

After fixing the L-regime derivation, the option value will have the form:

$$F_L(X) = A_1 X^{\beta_L^+} + C X^{\beta_H}, \quad X < X_L^*$$

where $\beta_L^+$ solves $\frac{1}{2}\sigma_L^2 \beta(\beta-1) + \mu_L \beta - (r + \tilde{\lambda}) = 0$ (the positive root), and $C = -\tilde{\lambda} B_H / Q_L(\beta_H)$ is the particular solution coefficient (already computed in the code).

The investment trigger will be determined by two conditions:
- **Value-matching:** $A_1 (X^*)^{\beta_L^+} + C(X^*)^{\beta_H} = V_L(X^*, K^*, \phi^*) - I(K^*)$
- **Smooth-pasting:** $A_1 \beta_L^+ (X^*)^{\beta_L^+ - 1} + C \beta_H (X^*)^{\beta_H - 1} = A_{\text{eff}} $

This is a system of two equations in two unknowns ($A_1$, $X^*$), which can be solved analytically (the trigger formula will be more complex but still semi-closed-form, involving both $\beta_L^+$ and $\beta_H$).

The key question is whether the paper's main *qualitative* results survive:
- The faith-based survival mechanism likely survives (it operates through $A_{\text{eff}}$, which is unchanged)
- The comparative statics on $\tilde{\lambda}$ likely survive in direction (though magnitudes change)
- The preemption equilibrium structure likely survives (it depends on leader/follower payoff ordering, not the specific option value formula)

The sympy verification will settle all of these questions definitively.
