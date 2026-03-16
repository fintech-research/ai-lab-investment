# Comment 5: Contradiction regarding capacity optimization in duopoly

**Referee's claim**: The paper states "The capacity formula in Proposition 1 carries over to the duopoly ... [and contest] shares ... do not enter the first-order condition for K," but in the duopoly, contest shares depend on own capacity, so A_eff,i is not of the separable form g(φ_i)·K_i^α.

## Assessment

**Relevant**: Yes. This is the same issue as Comment 2 — the analytical claim about capacity carry-over is incorrect for the general duopoly.

**Needs addressing**: Yes. The claim should be corrected or qualified.

## Analysis

In the single-firm model, A_eff = K^α · [w_L(1−φ)^α + w_H φ^α] = g(φ)·K^α. The K^α factor separates cleanly, giving ∂ln(A_eff)/∂K = α/K independent of φ.

In the duopoly, A_eff,i = [(1−φ_i)K_i]^α · s_i^L/(r−μ_L+λ) + λ/(r−μ_L+λ) · (φ_i K_i)^α · s_i^H/(r−μ_H), where s_i^L and s_i^H depend on K_i through the Tullock formula. The derivative ∂/∂K_i of [(1−φ_i)K_i]^α · s_i^L involves a factor (2 − s_i^L), not 1. Therefore ∂ln(A_eff,i)/∂K_i ≠ α/K_i in general.

The paper also says the follower jointly optimizes (K_F, φ_F) — or (K_F, φ_F, ℓ_F) with leverage — which is correct numerically but contradicts the claim that the capacity FOC from Proposition 1 applies.

## Suggested Fixes

1. **Qualify the "carry over" statement**: "In the duopoly, the contest shares s_i^L and s_i^H depend on own capacity K_i, so the exact separability A_eff = g(φ)·K^α that underlies the Proposition 1 closed-form does not hold. The follower's optimal capacity is determined jointly with φ_F by numerical optimization. The leader's capacity is numerically identical to the monopolist's (Proposition 1) across all parameterizations, a regularity attributable to the dominance of the monopoly-phase FOC (where s_L = 1 and separability holds)."

2. Same as Comment 2, Fix 1.
