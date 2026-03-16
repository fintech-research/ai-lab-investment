# Comment 28: Revenue increase from capacity doubling in contest

**Referee's claim**: The 2^{0.4} ≈ 1.32 calculation is correct for monopoly but understates the gain from a unilateral doubling in a symmetric duopoly (where the contest share also rises).

## Assessment

**Relevant**: Yes, but minor. The calculation is correct for the stated context but could be misread.

**Needs addressing**: Yes, with a brief clarification.

## Analysis

The paper says: "Doubling the relevant capacity measure increases revenue by approximately 2^{0.4} ≈ 1.32 times — a 32% increase rather than 100%."

This correctly describes the concavity of K^α (the capacity-only effect, holding contest share fixed or in monopoly). But the sentence directly references "the L-regime inference contest (Equation 14) and the H-regime training contest (Equation 15)," which could imply a duopoly context.

In a symmetric duopoly, unilaterally doubling capacity also increases the contest share from 1/2 to 2^α/(1+2^α) ≈ 0.569, so total revenue gain is:
2^{2α}/(2^α + 1) ÷ 1/2 = 2 × 2^{2α}/(2^α + 1) = 2 × 1.74/2.32 ≈ 1.50

So the total gain is ~50%, not 32%.

## Suggested Fixes

1. **Clarify the comparison**: "In the monopoly case (or holding contest share fixed), doubling capacity increases revenue by 2^α ≈ 1.32 times, reflecting the concavity channel alone. In a symmetric duopoly, unilateral doubling also raises the contest share, so the total revenue gain is larger (~50% at baseline α = 0.40)."
