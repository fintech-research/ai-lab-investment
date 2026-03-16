# Comment 23: Flawed mathematical justification for asymmetric revenue

**Referee's claim**: The explanation that "the sum of 2α-terms in the numerator exceeds the squared sum of α-terms" is an incorrect inequality.

## Assessment

**Relevant**: Yes. The stated inequality is mathematically wrong.

**Needs addressing**: Yes, high priority — the math needs correction.

## Analysis

The paper states: "Total industry revenue ∑_i π_i = X · ∑_i [(1−φ_i)K_i]^{2α} / ∑_j [(1−φ_j)K_j]^α can exceed the symmetric benchmark because the sum of 2α-terms in the numerator exceeds the squared sum of α-terms."

With y_i = [(1−φ_i)K_i]^α, total revenue is:
X · (y_1² + y_2²) / (y_1 + y_2)

The claim "y_1² + y_2² exceeds (y_1 + y_2)²" is false: by the expansion (y_1 + y_2)² = y_1² + 2y_1y_2 + y_2² > y_1² + y_2² always.

The correct comparison is against the symmetric benchmark X · (y_1 + y_2)/2 (total revenue when each firm gets share 1/2):

(y_1² + y_2²)/(y_1 + y_2) ≥ (y_1 + y_2)/2

This holds by the QM-AM inequality (or equivalently, y_1² + y_2² ≥ (y_1 + y_2)²/2, which is just the variance being non-negative). Equality holds when y_1 = y_2.

## Suggested Fixes

1. **Correct the inequality**: "Total industry revenue X · (y_1² + y_2²)/(y_1 + y_2) exceeds the symmetric benchmark X · (y_1 + y_2)/2 under asymmetry, because the quadratic-mean of (y_1, y_2) exceeds their arithmetic mean whenever y_1 ≠ y_2. Equivalently, the Tullock share function allocates more revenue to the larger firm, and the resulting share-weighted sum exceeds the equal-weighted sum."

2. **Alternatively, simplify**: "Under asymmetry (y_1 ≠ y_2), the Tullock specification produces total industry revenue that exceeds the symmetric benchmark by a dispersion premium proportional to (y_1 − y_2)²."
