# Comment 2: Contradiction regarding the leader's optimal capacity

**Referee's claim**: The claim that "the leader's optimal capacity is identical to the monopolist's across all volatility levels" seems inconsistent with the duopoly payoff structure, where contest shares depend on own capacity.

## Assessment

**Relevant**: Yes. The referee identifies a genuine issue with the analytical claim.

**Needs addressing**: Yes — both the analytical claim and the numerical finding need clarification.

## Analysis

The paper makes two related claims:

1. **Analytical claim** (after Proposition 1): "The capacity formula in Proposition 1 carries over to the duopoly, where the contest shares modify A_eff,i but do not enter the first-order condition for K."

2. **Numerical finding** (Section 2.4.5): "Competition primarily affects timing rather than scale: the leader's optimal capacity is identical to the monopolist's across all volatility levels."

**The analytical claim is incorrect for the general duopoly.** In the duopoly, A_eff,i involves contest shares s_i^L and s_i^H that depend on K_i through the Tullock formula. Specifically:

- Revenue term: [(1−φ_i)K_i]^α · s_i^L, where s_i^L = [(1−φ_i)K_i]^α / {[(1−φ_i)K_i]^α + [(1−φ_j)K_j]^α}
- The product [(1−φ_i)K_i]^α · s_i^L = [(1−φ_i)K_i]^{2α} / {[(1−φ_i)K_i]^α + [(1−φ_j)K_j]^α}
- ∂/∂K_i of this = (α/K_i) · [(1−φ_i)K_i]^α · s_i^L · (2 − s_i^L)

The factor (2 − s_i^L) means the elasticity of A_eff,i w.r.t. K_i is NOT simply α/K_i — it depends on the contest share. The Proposition 1 argument (which relies on ∂ln(A_eff)/∂K = α/K) does not hold.

**However**, for the leader during the monopoly phase, s_L = 1 and (2 − s_L) = 1, so the single-firm FOC does hold for that phase. The leader's value also includes a duopoly phase (after follower entry), but if the monopoly phase dominates, the effective K* may be close to the monopolist's. This would explain why it is a robust numerical regularity.

**For the follower**, s_i^L = s_i^H = 1/2 in the symmetric case, giving (2 − 1/2) = 3/2, so the effective revenue elasticity is 3α/2 rather than α. This changes the follower's capacity FOC, and the numerical results confirm K_F ≠ K_mono.

## Suggested Fixes

1. **Correct the analytical claim**: Replace "The capacity formula in Proposition 1 carries over to the duopoly" with: "In the duopoly, the contest shares s_i^L and s_i^H depend on K_i, so the separability that yields the closed-form K* in Proposition 1 does not hold exactly. However, the leader's capacity is numerically identical to the monopolist's across all calibration parameterizations, because the monopoly-phase FOC (where s_L = 1) dominates the joint optimization."

2. **Reframe the numerical finding**: Explicitly label "leader's capacity equals monopolist's capacity" as a computational regularity (not an analytical result), and explain that it arises because the monopoly phase heavily weights the leader's value function.
