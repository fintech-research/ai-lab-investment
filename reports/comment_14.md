# Comment 14: Misleading notation and definition for value loss (ΔV)

**Referee's claim**: NPV(λ_a, λ_b) is not clearly defined as a time-0 value. Also, ΔV is introduced in levels but discussed as a percentage, and the normalization isn't stated.

## Assessment

**Relevant**: Yes. The definition could be clearer, and the normalization should be explicit.

**Needs addressing**: Yes, with clarifications to the definition.

## Analysis

The paper defines:
$$\Delta V = \text{NPV}(\lambda_{\text{true}}, \lambda_{\text{true}}) - \text{NPV}(\lambda_{\text{true}}, \lambda_{\text{invest}})$$

The subsequent text says "loses 26% of value" and the figure shows normalized loss. But the normalization is not stated at the point of definition.

Looking at the code, the computation evaluates option values at a common reference demand level X_0, applying timing discounts (X_0/X*)^{β_H}. So NPV(λ_a, λ_b) is the expected present value at X_0 of following the policy optimal for λ_b when the true parameter is λ_a.

The percentage loss is ΔV / NPV(λ_true, λ_true).

## Suggested Fixes

1. **Clarify the definition**: "NPV(λ_a, λ_b) denotes the expected present value, evaluated at a common initial demand level X_0, of following the investment policy (X*, K*, φ*) that is optimal under belief λ_b, when demand outcomes are realized under the true parameter λ_a. The timing discount (X_0/X*)^{β_H} accounts for different waiting times before investment triggers at the respective thresholds."

2. **State the normalization**: "The percentage value loss is ΔV/NPV(λ_true, λ_true), reported throughout as a fraction of the first-best value."
