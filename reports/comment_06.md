# Comment 6: Contradictions regarding convexity and capacity independence

**Referee's claim**: Section 4.4 says equity value is "increasing and convex in λ," but Section 2.3.3 says F_L "increases concavely in λ" and approaches the λ-independent F_H. Also, "larger investment" is confusing since K* is independent of λ.

## Assessment

**Relevant**: Yes. The global convexity claim cannot hold if F_L is bounded above by F_H as λ → ∞.

**Needs addressing**: Yes — both the curvature claim and the "larger" wording need correction.

## Analysis

### Convexity vs. concavity

- **Section 2.3.3**: F_L(X) "increases concavely in λ" — this is about the L-regime option value, which is bounded above by F_H as λ → ∞ (the option value in a world that is already in regime H). The approach to the upper bound is necessarily concave.

- **Section 4.4**: Claims equity value is "increasing and convex in λ" — this is about the computed option values across a range of λ. If the relevant range is λ ∈ [0.1, 0.5], the function could be locally convex there (e.g., accelerating gains from combined effects of lower trigger, higher φ*, and compounding through the option value formula).

The reconciliation is that F_L can be locally convex over some range while being globally concave. But the blanket statement "convex in λ" without qualification is misleading.

### "Larger investment"

The phrase "higher λ implies earlier and larger investment with more training" is indeed confusing. K* is independent of λ by Proposition 1 (single-firm). If this refers to the duopoly, it should say so. If "larger" refers to timing (investing at a lower trigger), it should say "earlier" not "larger."

## Suggested Fixes

1. **Qualify the convexity claim**: "Over the economically relevant range λ ∈ [0.1, 0.5], the option value is locally convex in λ... As λ → ∞, the option value converges to F_H from below (Section 2.3.3), so global convexity does not hold, but the policy-relevant range exhibits accelerating returns to higher λ."

2. **Fix the "larger" wording**: "Higher λ implies earlier investment with a higher training fraction, generating more value from the growth option" — dropping "larger" which falsely suggests higher K*.
