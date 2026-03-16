# Comment 30: Incomplete expression for marginal cost of training

**Referee's claim**: "The marginal cost is only the direct capacity effect α(1−φ_L)^{α−1}" is hard to reconcile with the full revenue expression, whose derivative includes X and K^α factors.

## Assessment

**Relevant**: Yes, but minor. The expression isolates the φ-dependent part without stating the normalization.

**Needs addressing**: Yes, with a clarification.

## Analysis

The paper says (Appendix A, Proposition 3 proof): "the marginal cost is only the direct capacity effect α(1−φ_L)^{α−1}."

The full derivative of monopoly L-revenue X · [(1−φ_L)K_L]^α with respect to φ_L is:
−X · α · K_L^α · (1−φ_L)^{α−1}

So α(1−φ_L)^{α−1} is the φ-dependent part, omitting X and K_L^α. The intent is to compare monopoly vs. duopoly by isolating the factor that changes across competitive phases, but this isn't stated.

## Suggested Fixes

1. **Add a normalization note**: "the marginal revenue loss from increasing φ_L is proportional to α(1−φ_L)^{α−1} (the φ-dependent component, with the common factors X and K_L^α suppressed for comparison across competitive phases)."
