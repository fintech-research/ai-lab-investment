# Comment 9: Misunderstanding of Assumption (A2) and numerical optimization

**Referee's claim**: (1) The hyperscaler (r=0.10) is unlikely to violate the lower bound of (A2). (2) "Full numerical optimization does not require (A2)" is misleading if (A2) ensures interior capacity.

## Assessment

**Relevant**: Yes. The specific A2 violation claim for the hyperscaler appears to be a numerical error. The point about optimization behavior without (A2) is also valid.

**Needs addressing**: Yes.

## Analysis

### A2 at the hyperscaler WACC

Assumption (A2): 1/γ < (β_H − 1)/(αβ_H) < 1.

At r = 0.10 (hyperscaler WACC), with baseline μ_H = 0.06, σ = 0.25:
- β_H solves 0.03125β² + 0.02875β − 0.10 = 0 → β_H ≈ 1.387
- (β_H − 1)/(αβ_H) = 0.387/(0.40 × 1.387) = 0.387/0.555 ≈ 0.697
- Lower bound: 1/γ = 1/1.50 = 0.667
- Check: 0.697 > 0.667 → lower bound IS satisfied

The paper says the hyperscaler "violates the lower bound," but this appears incorrect with baseline parameters. The violation might occur if the hyperscaler also uses different α or γ, but the paper doesn't indicate this.

At r = 0.18 (compute racer):
- β_H ≈ 1.985
- (β_H − 1)/(αβ_H) = 0.985/0.794 ≈ 1.240
- Upper bound: 1.240 > 1 → upper bound IS violated ✓

### "Does not require (A2)"

(A2) ensures an interior capacity solution. If (A2) fails, the capacity optimization may have a corner solution (K → 0 or K → ∞) or may not be well-defined without explicit bounds. The numerical optimizer uses bounded search, so it will find "something," but the result may not correspond to a well-behaved interior optimum. The paper should be explicit about how the optimizer handles this.

## Suggested Fixes

1. **Verify the A2 check numerically** for the hyperscaler archetype. If the violation claim is wrong, correct it. If it relies on archetype-specific parameters beyond WACC, state those parameters.

2. **Clarify the numerical treatment**: "When (A2) fails, the closed-form capacity expression may not yield a positive real solution. The numerical optimizer searches over (log K, φ) with explicit bounds and multiple starting points, ensuring convergence to a local optimum. In all archetype-specific cases where (A2) is violated, the optimizer converges to an interior solution, suggesting that (A2) is sufficient but not necessary for interior capacity."
