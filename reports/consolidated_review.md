# Consolidated Review Report

**Based on:** Three independent reviews (Codex, Claude Opus 4.6, Gemini 3 Pro Preview)
**Date:** 2026-02-22

## Executive Summary

Three independent reviewers examined both the codebase and the accompanying paper/slides. All three agree the project addresses a timely, important question with a creative theoretical framework and a well-organized codebase (145 passing tests). All three recommend **major revision** before journal submission, with **Review of Financial Studies (RFS)** as the best target journal (JF possible with stronger empirical content; Econometrica requires expanded proofs and formal identification).

The reviewers converge on several high-priority issues. The findings below are organized by how many reviewers independently flagged each issue, giving greater weight to cross-reviewer consensus.

---

## Issues Flagged by All Three Reviewers

These are the highest-confidence findings -- each was independently identified by all three agents.

### 1. Proposition 5 (Training Fraction): Paper vs. Code Mismatch

**Severity: Critical** | Codex: Critical, Claude: Caveat, Gemini: Has Issues

The paper derives a closed-form optimal training share $\phi^* = \eta/(\alpha + \eta)$ from a static power-law quality model (Proposition 5). The code (`nfirm.py:280-326`) implements a dynamic optimization with log-based incremental quality and finite-horizon PV, yielding numerical solutions that differ from the stated formula ($\phi^* \approx 0.25$ vs $0.15$ per Gemini).

**Fix options (per Codex):**
- *Option A (faster):* Align text to code -- replace Proposition 5 with a description of the implemented dynamic model and state $\phi^*$ is obtained numerically.
- *Option B (cleaner):* Align code to text -- implement the power-law quality model multiplicatively in revenue so the analytic formula holds.

### 2. Mathematical Error in $F_L(X)$ Particular Solution (Eq. 94)

**Severity: Critical** | Codex: Major, Claude: Critical, Gemini: Minor

Paper (`_model.qmd:94`) states $F_L(X) = A_L X^{\beta_L} + \frac{\lambda}{r + \lambda - r} F_H(X)$. The coefficient simplifies to $\lambda/\lambda = 1$, which is clearly a typographical error. The correct particular solution (as implemented in `base_model.py:135-152`) is:

$$F_L(X) = D_L X^{\beta_L} + C X^{\beta_H}, \quad C = -\lambda B_H / Q_L(\beta_H)$$

where $Q_L(\beta) = \tfrac{1}{2}\sigma_L^2 \beta(\beta-1) + \mu_L \beta - (r + \lambda)$.

### 3. Default Boundary Formula Mismatch

**Severity: Critical** | Codex: Major, Claude: Critical, Gemini: Critical

The paper presents a naive zero-equity default condition. The code implements the Leland (1994) smooth-pasting optimal default boundary with the negative characteristic root:

$$X_D = \frac{\beta_s^-}{\beta_s^- - 1} \cdot \frac{c_D/r}{A_s \cdot K^\alpha \cdot \text{share}}$$

Additionally, Gemini notes the code omits operating costs ($\delta K$) from the default boundary numerator, potentially underestimating default risk. The paper formula, the code formula, and economic correctness need to be reconciled.

### 4. N-Firm Model Implementation Issues

**Severity: Critical** | Codex: Noted, Claude: Major, Gemini: Critical

- **Gemini (critical):** The N-firm model implements a Stackelberg equilibrium (optimal waiting given entry order) rather than the preemption equilibrium (race to enter) described in the paper. This fundamentally changes strategic dynamics for $N > 2$.
- **Claude (major):** No convergence check -- code hardcodes 5 iterations (`nfirm.py:223`) with no verification, despite the paper claiming convergence at tolerance $10^{-4}$.
- **Codex:** Algorithm structure (fixed-point iteration) differs from the paper's description (backward induction).

### 5. Journal Fit Consensus: RFS

All three reviewers recommend **Review of Financial Studies** as the primary target. JF is possible with stronger empirical content. Econometrica requires complete proofs, formal identification theorems, and existence/uniqueness results.

---

## Issues Flagged by Two Reviewers

### 6. Missing or Incomplete Proofs

**Severity: Major** | Claude: Major, Codex: Minor

- Propositions 2, 3, 4, and 6 lack formal proofs (Claude).
- Proposition 1's proof uses a heuristic asymptotic argument that is logically incomplete (Claude).
- Appendix proofs are sketch-level (Codex) -- acceptable for JF/RFS but insufficient for Econometrica.

### 7. Notation Inconsistencies

**Severity: Moderate** | Codex: Minor, Claude: Minor

- $\beta$ is used inconsistently ($\beta_H$, $\beta_s^-$, $\beta_s$, $\beta$ without subscript).
- Symbol $c$ (investment cost) conflicts with coupon rate $c_d$.
- $\delta$ is called "depreciation" but modeled as perpetual operating cost.
- Debt notation ($d$, $D_0$, $D(X)$, $c_d$) is fragmented.

Codex recommends: prefer $D_L$ (free constant) and $C$ (particular coefficient) over $A_L$ for regime-L option constants to avoid confusion with $A_s = 1/(r - \mu_s)$.

### 8. Literature Gaps

**Severity: Moderate** | Claude: Major, Codex: Minor

Missing references flagged by Claude: Weeds (2002, RES), Hackbarth & Mauer (2012, RFS), Sundaresan et al. (2015, RFS), Brander & Lewis (1986), Lambrecht & Perraudin (2003). Codex suggests adding recent empirical/finance literature on AI capex and credit conditions.

### 9. Growth Decomposition Issues

**Severity: Moderate** | Claude: Minor, Gemini: Major

Gemini flags Figure 10 as conceptually flawed: the "expansion option" plotted does not exist for a firm that has already committed to capacity $k$ under irreversible lump-sum investment. Claude notes the decomposition uses total option value rather than incremental expansion value (non-standard methodology).

### 10. Test Coverage Gaps

**Severity: Moderate** | Claude: Major, Gemini: Moderate

Overall coverage is ~47%. Core models are well-covered (80-93%), but figure modules (718 statements), `pipeline.py`, and `utils/` are completely untested. Claude identifies several weak/tautological tests and missing edge cases (lambda=0, very large lambda, N=1, near-boundary parameters).

### 11. No Optimization Success Checks

**Severity: Moderate** | Claude: Major, Codex: Noted

After every `minimize_scalar` call, `result.success` is never checked. Failed convergence would be silently used. Affects `base_model.py`, `duopoly.py`, and `nfirm.py`.

### 12. Abstract Overclaiming

**Severity: Minor** | Codex: Minor, Claude: Minor

Both suggest softening "analytical characterization" of duopoly triggers to reflect mixed analytic/numeric solution. Claude notes the abstract claims results ("frontier labs invest as if transformative AI is substantially closer than market consensus") not numerically presented in the paper body.

---

## Issues Flagged by One Reviewer

These warrant investigation but carry less cross-reviewer weight.

### 13. Firm Data Inconsistency (Claude only)

**Severity flagged: Critical** | **VERIFIED**

Only 6 of 24 firm data points match between the paper table and the code. The paper claims all firms have CapEx/Revenue > 1.0, but the code data has Anthropic-like at 0.556 and OpenAI-like at 0.667. Revenue figures differ by up to 4x (Google: $40B in paper vs $10B in code). Figure 8 contradicts the paper's own table.

### 14. Revenue Double-Counting Bug (Claude only)

**Severity flagged: Critical** | **VERIFIED**

`contest_share` returns $K_i^\alpha / (K_i^\alpha + K_j^\alpha)$, a fraction between 0 and 1. Revenue then computes `A * X * K_i^alpha * share`, yielding $K_i^{2\alpha}$ in the numerator instead of $K_i^\alpha$. For typical $K_i = 10, \alpha = 0.4$, this overstates revenue by ~2.5x. The bug propagates through `duopoly.py` (lines 95, 150, 337) and `nfirm.py` (lines 100, 162), affecting all duopoly/N-firm results including triggers, capacities, and default boundaries.

### 15. No Revealed Beliefs Numerical Results (Claude only)

**Severity flagged: Critical** | **VERIFIED**

The paper describes the inversion methodology and calibrates firms with observable data, but never executes the inversion to produce results. No table of implied $\lambda$ values appears anywhere in the paper or slides. The code infrastructure exists (`revealed_beliefs.py:compute_all_revealed_beliefs()`) but its output is never presented. The abstract's claim that "frontier labs invest as if transformative AI is substantially closer than market consensus" is unsupported by any numerical evidence in the paper.

### 16. $\mu_L$ Parameter Discrepancy (Claude only)

**Severity flagged: Major** | Needs verification

`CalibrationData.mu_L = 0.02` vs. paper/`ModelParameters.mu_L = 0.01`. This would affect revealed beliefs analyses using `CalibrationData` defaults.

### 17. Depreciation Calibration Inconsistency (Claude only)

**Severity flagged: Major** | Needs verification

Paper claims GPUs depreciate ~20%/year but uses $\delta = 0.03$ (3%). Either the discrepancy needs explanation or the parameter needs recalibration.

### 18. Figure 5 Default Boundary with $K_j = 0$ (Claude only)

**Severity flagged: Major** | Needs verification

`generate_figures.py:293` computes default boundary with `K_j = 0` instead of `K_j = K_\text{leader}` in the duopoly setting.

### 19. N-Firm Extension Lacks Numerical Results for N > 2 (Claude only)

**Severity flagged: Major**

The N-firm section describes the algorithm but presents no figures or tables showing equilibrium outcomes for $N = 3, 4, 5$.

### 20. Installed Value Formula Missing Regime Switching (Claude, Gemini)

**Severity: Minor**

Paper's $V_L$ formula omits the continuation value from regime switching. Code correctly accounts for it via $A_L = \frac{r - \mu_H + \lambda}{(r - \mu_H)(r - \mu_L + \lambda)}$. Paper should match the code.

---

## Reviewer Agreement Matrix

| Issue | Codex | Claude | Gemini | Consensus |
|-------|:-----:|:------:|:------:|:---------:|
| Prop 5 mismatch | X | X | X | **3/3** |
| $F_L$ typo (Eq 94) | X | X | X | **3/3** |
| Default boundary mismatch | X | X | X | **3/3** |
| N-firm implementation issues | X | X | X | **3/3** |
| RFS as target journal | X | X | X | **3/3** |
| Major revision needed | X | X | X | **3/3** |
| Missing/incomplete proofs | - | X | X | 2/3 |
| Notation inconsistencies | X | X | - | 2/3 |
| Literature gaps | X | X | - | 2/3 |
| Growth decomposition flawed | - | X | X | 2/3 |
| Test coverage gaps | - | X | X | 2/3 |
| No optimization success checks | X | X | - | 2/3 |
| Abstract overclaiming | X | X | - | 2/3 |
| Firm data inconsistency | - | X | - | 1/3 |
| Revenue double-counting | - | X | - | 1/3 |
| No revealed beliefs results | - | X | - | 1/3 |

---

## Priority-Ordered Action Items

### P0 -- Must Fix Before Submission

1. **Fix revenue double-counting bug** in `duopoly.py` and `nfirm.py` (VERIFIED -- K_i^{2\alpha} instead of K_i^\alpha; affects all duopoly/N-firm results)
2. **Synchronize firm data** between paper table and `data.py` (VERIFIED -- 75% of values mismatch)
3. **Fix $F_L$ particular solution typo** in `paper/_model.qmd:94` (3/3 consensus)
4. **Reconcile default boundary formula** between paper and code (3/3 consensus)
5. **Align Proposition 5** with code (or vice versa) for training fraction (3/3 consensus)
6. **Fix N-firm model** -- add preemption logic and convergence checks (3/3 consensus)
7. **Add revealed beliefs numerical results** -- table of implied $\lambda$ values (VERIFIED missing -- the paper's headline result)
8. **Fix abstract** to match actual content

### P1 -- Should Fix

9. **Add missing proofs** for Propositions 2, 3, 4, 6
10. **Standardize notation** ($\beta$, cost/coupon symbols, debt notation)
11. **Add optimization success checks** throughout codebase
12. **Fix or remove growth decomposition** (Figure 10)
13. **Expand literature review** with missing references
14. **Fix installed value formula** in paper to include regime switching

### P2 -- Nice to Have

15. Fix $\mu_L$ parameter discrepancy
16. Explain or recalibrate $\delta$ depreciation value
17. Fix Figure 5 default boundary ($K_j = 0$ issue)
18. Add N > 2 numerical results
19. Improve test coverage and fix weak tests
20. Remove vestigial config parameters and "preliminary draft" subtitle
