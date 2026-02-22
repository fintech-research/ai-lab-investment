# Review Report: AI Lab Investment

**Reviewer:** gemini_3_pro_preview
**Date:** 2026-02-22

## Executive Summary

The paper "Investing in Intelligence: A Real Options Framework for AI Compute Infrastructure" presents a timely and ambitious model of AI investment under uncertainty, competition, and technological change. The framework logically progresses from a single-firm benchmark to a complex N-firm equilibrium with endogenous default and training/inference allocation.

However, the review has identified **significant discrepancies between the paper's claims and the code implementation**, particularly in the N-firm model and the default boundary calculation. The N-firm numerical solution implements a Stackelberg leader-follower structure rather than the claimed preemption equilibrium, potentially invalidating the results on competitive dynamics in oligopoly. Additionally, the default boundary calculation in the code omits operating costs, leading to an underestimation of default risk. The "growth decomposition" analysis in Figure 10 is also conceptually inconsistent with the model's irreversible investment assumption.

While the core single-firm model is correctly implemented, the extensions require major revision to match the paper's theoretical claims. I recommend a **Major Revision** to address these critical issues before submission to a top journal.

## Part 1: Code Validation

### 1. Mathematical Correctness

- [x] **Propositions vs. code**:
    - **Proposition 1 (Single Firm)**: **Passes**. The code (`base_model.py`) correctly implements the optimal trigger and capacity formulas.
    - **Proposition 2 (Default Boundary)**: **Has issues**. The code in `duopoly.py` (line 159) calculates the default boundary `X_D` using only the coupon payment `c_D` in the numerator. The paper (Eq 137) correctly includes operating costs: `delta * K + d`. The code ignores `delta * K`, leading to an underestimation of the default boundary and default risk.
    - **Proposition 3 (Preemption)**: **Passes** for Duopoly. The code correctly solves for $X_P$ such that $L(X_P) = F(X_P)$.
    - **Proposition 4 (N-Firm Equilibrium)**: **Has issues**. The paper claims to solve for a "sequential equilibrium" with preemption (citing Bouis et al. 2009). However, `nfirm.py` implements a Stackelberg equilibrium where firms optimize their triggers based on optimal waiting, not preemption. The code does not check for the condition $Value_{leader} = Value_{follower}$ for the first $N-1$ firms. This means the code solves for a "right-to-invest" game rather than a "race-to-invest" game.
    - **Proposition 5 (Training Fraction)**: **Has issues**. The paper derives a static formula $\phi^* = \eta / (\alpha + \eta)$. The code (`nfirm.py`, `optimal_training_fraction`) implements a dynamic optimization that capitalizes future quality gains. While accurate for a dynamic setting, it yields different values ($\phi^* \approx 0.25$ vs $0.15$) and contradicts the proposition's claim of a simple static formula.

- [x] **Proofs**: **Passes**. The proofs in `_appendix.qmd` appear logically sound, although the derivation of Option Value L (Eq 94) in the paper assumes identical parameters across regimes ($\mu_L=\mu_H, \sigma_L=\sigma_H$) to simplify to the form shown. The general case implemented in code is correct.

- [x] **Numerical methods**: **Has issues**.
    - The `solve_sequential_equilibrium` in `nfirm.py` iterates backwards but fails to enforce the preemption constraint (indifference condition) for early entrants. It only solves the "follower" optimization for each firm in the sequence.
    - The `verify_against_duopoly` method in `nfirm.py` is likely to fail or show discrepancies because the analytical duopoly model includes preemption while the N-firm numerical model (for N=2) does not.

- [x] **Parameter consistency**: **Passes**. `models/parameters.py` matches the calibration values in the paper.

- [x] **Regime switching**: **Passes**. The implementation of `_phi` and `_A_L` in `base_model.py` correctly accounts for regime switching, even handling the general case better than the simplified formula in the paper.

### 2. Code Quality and Testing

- [x] **Test coverage**: **Has issues**. Run `uv run pytest --cov` shows ~47% coverage. Core models have good coverage (85-90%), but figure generation and pipeline code are untested.
- [x] **Test meaningfulness**: **Passes**. Tests in `tests/` check economic properties (e.g., `test_comparative_statics` checks if trigger increases with volatility).
- [x] **Edge cases**: **Passes**. Tests cover `lambda=0`, `leverage=0`.
- [x] **Numerical stability**: **Passes**. Code includes guards for division by zero (e.g., `if denom <= 0: return 0.5`).
- [x] **Code organization**: **Passes**. Clean separation of concerns between models, parameters, and figures.
- [x] **Reproducibility**: **Passes**. Random seeds are set in figure generation (`rng = np.random.default_rng(42)`).

## Part 2: Paper and Presentation Review

### 3. Paper Content Review

#### 3a. Structure and Argument
- [x] **Motivation**: **Passes**. The introduction effectively links AI scaling laws to real options theory.
- [x] **Literature positioning**: **Passes**. Appropriately cites Dixit & Pindyck, Grenadier, and recent AI economics papers.
- [x] **Model building**: **Has issues**. The transition from Duopoly (with explicit preemption) to N-firm (described as preemption but implemented as Stackelberg) is inconsistent. The paper claims the N-firm model captures "race" dynamics, but the code does not.
- [x] **Identification**: **Passes**. The "revealed beliefs" methodology is clever, though it relies heavily on the correctness of the underlying structural model.
- [x] **Conclusion**: **Passes**. Summaries are clear.

#### 3b. Writing Quality
- [x] **Clarity**: **Passes**. The paper is well-written and accessible.
- [x] **Notation**: **Has issues**.
    - Eq 38 ($V_L$) omits the regime-switching term $\lambda V_H$, which is confusing given that the option value equation (Eq 89) includes it.
    - Eq 94 ($F_L$) presents a simplified formula that only holds under parameter symmetry, which is not the general case used in the paper.
- [x] **Length and focus**: **Passes**. appropriate.
- [x] **Abstract**: **Passes**. concise.

#### 3c. Journal Fit
- [x] **Contribution significance**: High. The application of real options to AI infrastructure is novel and important.
- [x] **Methodological rigor**: Mixed. The theoretical framework is strong, but the implementation errors (N-firm preemption, default boundary) undermine the rigor.
- [x] **Formatting and conventions**: **Passes**.
- [x] **Which journal fits best**: **RFS** or **Journal of Finance**. The focus on corporate investment, default risk, and revealed beliefs fits finance journals well. Econometrica might require a more rigorous theoretical contribution to the N-firm game (proving existence/uniqueness of the equilibrium).

### 4. Figures

- [x] **Paper figures**: **Has issues**.
    - **Figure 10 (Growth Decomposition)**: Conceptually flawed. It plots "Expansion Option" as the difference between the value of an optimally invested firm ($K^*$) and a firm with suboptimal capacity ($k$). However, the model assumes **irreversible lump-sum investment**. A firm that has already installed $k$ does not hold an option to expand to $K^*$; it has exercised its option. The figure effectively plots "regret" or "foregone value," not a growth option.
    - **Figure 5 (Default Boundaries)**: The default boundary curve is likely too low (underestimating risk) because the underlying code ignores operating costs in the numerator of the default threshold.
- [x] **Code-figure consistency**: **Passes** (mostly). The figures accurately reflect the *code's* output, even if the code itself has errors (e.g., Figure 5 reflects the flawed default boundary formula).
- [x] **Slide figures**: **Passes**. Consistent with paper figures.

### 5. Calibration and Results

- [x] **Parameter values**: **Passes**. Reasonable calibration based on current AI hardware costs.
- [x] **Sensitivity**: **Passes**. Good exploration of $\sigma, \alpha, \lambda$.
- [x] **Comparative statics**: **Passes**.
- [x] **Revealed beliefs results**: **Passes**. The qualitative results (optimistic firms invest earlier/more) hold even with the model issues, though quantitative estimates might be biased by the default boundary error.
- [x] **Growth decomposition**: **Has issues**. See Figure 10 comments. The decomposition is invalid for the specific model structure used.

### 6. Slides Review

- [x] **Completeness**: **Passes**.
- [x] **Clarity**: **Passes**.
- [x] **Consistency with paper**: **Passes**.

## Summary of Issues

### Critical Issues
1.  **N-Firm Equilibrium Logic**: The N-firm model (`nfirm.py`) implements a Stackelberg equilibrium (optimal waiting given entry order) rather than the Preemption equilibrium (race to enter) described in the paper and used in the Duopoly section. This fundamentally changes the strategic dynamics and investment timing for $N > 2$.
2.  **Default Boundary Calculation**: The code for the default boundary (`duopoly.py`) omits operating costs ($\delta K$) from the numerator. This leads to a systematic underestimation of the default threshold $X_D$ and default probabilities.

### Major Issues
1.  **Figure 10 (Growth Decomposition)**: The conceptual basis for this figure is flawed. The "expansion option" it calculates does not exist for a firm that has already committed to a capacity level $k$ under the assumption of irreversible lump-sum investment.
2.  **Proposition 5 vs Code**: The code implements a dynamic optimization for training allocation that differs from the static formula presented in Proposition 5. The paper should either derive the dynamic result or the code should match the static approximation.

### Minor Issues
1.  **Eq 38 Notation**: The value function for installed capacity in regime L should explicitly include the continuation value from regime switching or clarify that it represents the "perpetual regime" value.
2.  **Eq 94 Generality**: The formula for $F_L$ is presented as a general solution but is only valid for symmetric parameters across regimes.
3.  **Test Coverage**: While tests exist, coverage is below 50%. Key numerical methods in `nfirm.py` should be tested against the analytical duopoly results (once fixed).

## Overall Recommendation

**Revise and Resubmit** (Major Revision).

The paper addresses a highly relevant topic with a sophisticated framework. However, the discrepancies between the theoretical model (preemption, default definition) and the numerical implementation (Stackelberg, missing costs) are significant. The N-firm model needs to be rewritten to correctly solve for preemption triggers, and the default boundary calculation must be fixed. Figure 10 should be removed or the model extended to allow for capacity expansion.

**Target Journal**: **Review of Financial Studies (RFS)**. The paper's blend of real options, corporate finance (default risk), and asset pricing (revealed beliefs) aligns well with RFS.
