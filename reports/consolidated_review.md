# Consolidated Review Report

**Date:** 2026-02-25
**Sources:** Three independent AI reviews (Claude Opus, Codex, Gemini)

---

## Verdict

All three reviewers recommend **Revise and Resubmit (minor revision)** and agree on **JF or RFS** as the target journal. The core model (single-firm and duopoly) is mathematically correct, well-tested, and publication-ready. The paper is well-written, the contribution is significant, and the code faithfully implements the theory.

The issues below are organized by priority. The N-firm extension is flagged by all three reviewers as the weakest part of the paper (numerically divergent, methodologically confused); since it has already been decided to remove it, the remaining action items are straightforward.

---

## 1. N-Firm Extension — Remove (already decided)

All three reviewers flag the N-firm extension as the paper's main weakness:
- **Numerical divergence:** The iterative best-response solver in `nfirm.py` does not converge — capacity values explode to ~10^192 with 141,000+ overflow warnings (Opus, Gemini).
- **Methodological contradiction:** `_extensions.qmd` claims both "backward induction" (lines 6, 61) and "iterative best-response" (line 32). The code implements the latter, which is not a sequential equilibrium (Gemini).
- **Docstring mismatch:** `nfirm.py` top-level docstring mentions "finite-difference methods on a log-X grid" but the code uses direct optimization (Codex).

**Action items:**
1. Remove `_extensions.qmd` from the paper (it is already orphaned — not included in `index.qmd`). Either delete the file or archive it.
2. Remove or demote the N-firm content in `_appendix.qmd` (Numerical Finding 1 around lines 245-256).
3. Optionally retain a brief remark in the Discussion noting that the duopoly extends naturally to N firms as a direction for future work.
4. The code modules (`nfirm.py`, `test_nfirm.py`) can remain in the codebase for future development but should not be referenced from the paper.

---

## 2. Equity Value Formula — Fix (Critical)

**Identified by:** Opus (confirmed by code inspection)
**Location:** `_model.qmd` around line 303

The paper's equity formula includes `(1-ℓ)I(K)` (the sunk equity contribution) *inside* the default option bracket:

```
E(X) = A_eff·X − δK/r − (1−ℓ)I(K) − c_D/r
     + [c_D/r + δK/r + (1−ℓ)I(K) − A_eff·X_D] · (X/X_D)^{β⁻}
```

The code (`duopoly.py:426`) correctly *excludes* it from the bracket. The issue: if smooth-pasting E'(X_D)=0 is applied to the paper formula, the `(1-ℓ)I(K)` term inside the bracket has a nonzero derivative via the `(X/X_D)^{β⁻}` factor, yielding a different X_D than eq-default-boundary. The paper's footnote claiming this "cancels in the derivative" is incorrect for the formula as written.

**Action items:**
1. Remove `(1−ℓ)I(K)` from inside the default option bracket in the equity formula.
2. The corrected formula should be:
   ```
   E(X) = A_eff·X − δK/r − (1−ℓ)I(K) − c_D/r
        + [c_D/r + δK/r − A_eff·X_D] · (X/X_D)^{β⁻}
   ```
3. Update the footnote to note that E(X_D) = −(1−ℓ)I(K), which is clamped to zero by limited liability. This matches the code and standard Leland (1994) approach.

---

## 3. Growth Decomposition Figure — Clarify (Major)

**Identified by:** Gemini

Figure 10 (Growth Decomposition) calculates a "counterfactual" value that Gemini flags as non-standard — it compares optimal vs. sub-optimal capacity rather than using the standard "growth option = PV of future investment opportunities" definition.

**Action items:**
1. Review the `create_growth_decomposition` function in `paper.py` and the accompanying text in `_valuation.qmd`.
2. Either (a) clarify the definition in the paper text so the decomposition methodology is unambiguous, or (b) align the computation with the standard growth-option definition.

---

## 4. Overflow Warnings in Duopoly — Investigate (Major)

**Identified by:** Gemini

Beyond the N-firm module, `RuntimeWarning: overflow encountered in scalar power` also occurs in `duopoly.py` for some parameter combinations. This suggests intermediate values of K^γ can blow up during optimization.

**Action items:**
1. Review the optimization bounds in the duopoly solver and ensure log-K search bounds prevent overflow.
2. Consider adding explicit bounds or log-space transformations where K^γ is computed.

---

## 5. Figure Improvements — Consider (Minor)

**Identified by:** Opus

Two figures have minor visual issues:

- **Figure 7 panel (b)** (Competition Effect): The capacity ratio K_leader/K_mono is identically 1.0 by construction, making the panel visually redundant — the dashed line sits on the reference line.
- **Figure 8 panel (a)** (Firm Comparison): xAI-like's CapEx/Revenue ratio (~20x) dominates the bar chart, making other firms' bars nearly invisible.

**Action items:**
1. Figure 7(b): Either remove the panel, replace it with a more informative metric (e.g., capacity difference or welfare), or add a note explaining why the ratio is 1.0.
2. Figure 8(a): Consider a log-scale y-axis, a broken axis, or an inset for the smaller bars.

---

## 6. Paper Text Improvements — Consider (Minor)

### 6a. Scaling hypothesis caveat
**Identified by:** Opus

The paper assumes unbounded H-regime demand growth. A brief sentence in the Discussion noting that α < 1 partially captures diminishing returns but does not model a hard ceiling on scaling laws would strengthen robustness. The broader debate about scaling laws plateauing (beyond Kaplan et al.) is not addressed.

### 6b. Compute governance literature
**Identified by:** Opus

The growing literature on compute governance (e.g., Sastry et al., 2024) is not mentioned. A sentence in the literature review or discussion could acknowledge this related strand.

### 6c. Testable predictions and data requirements
**Identified by:** Opus

The four testable predictions in `_discussion.qmd` are well-stated but could benefit from brief discussion of what data would be needed to test each one.

### 6d. Dynamic φ robustness
**Identified by:** Codex

The limitation of static φ (training fraction chosen at investment, not adjusted over time) is acknowledged in the Discussion. Codex suggests a short sensitivity experiment or qualitative discussion of how results would change with dynamic reallocation.

---

## 7. Code Housekeeping — Low Priority (Minor)

These are code-level issues that do not affect the paper but should be fixed for maintainability:

| Issue | Source | Location | Fix |
|-------|--------|----------|-----|
| Download cache directory naming: `download-cache` (justfile) vs `download_cache` (code) | Codex | `justfile:20-27` vs `directories.py` | Standardize naming |
| Q_L near-zero guard threshold too tight (1e-15) and returns 0.0 instead of diverging | Opus | `base_model.py:167` | Widen to 1e-10, add warning |
| Test `test_higher_lambda_lower_trigger` name is misleading (tests validity, not direction) | Opus | `test_calibration.py:73` | Rename or strengthen assertion |
| No test for `dario_dilemma_leveraged` function | Opus | `valuation.py:348-390` | Add basic test |
| `nfirm.py` docstring mentions "finite-difference methods" but code uses optimization | Codex | `nfirm.py` top-level docstring | Update docstring |
| Two model modes (simple vs full) not documented in code docstrings | Gemini | `base_model.py` | Add brief docstring notes |

---

## Summary of Priorities

| Priority | Item | Effort | Impact |
|----------|------|--------|--------|
| **Done** | Remove N-firm extension from paper | Low | Eliminates main weakness |
| **High** | Fix equity value formula (§2) | Low | Corrects mathematical inconsistency |
| **Medium** | Clarify growth decomposition (§3) | Low-Med | Prevents referee confusion |
| **Medium** | Fix duopoly overflow warnings (§4) | Medium | Improves robustness |
| **Low** | Figure visual improvements (§5) | Low | Polish |
| **Low** | Paper text additions (§6) | Low | Strengthens discussion |
| **Low** | Code housekeeping (§7) | Low | Maintainability |

The high-priority fix (equity formula) is a one-line equation change plus a footnote edit. With the N-firm removal already decided, the remaining revision is genuinely minor.
