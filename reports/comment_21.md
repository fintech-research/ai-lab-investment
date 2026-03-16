# Comment 21: Incorrect mathematical explanation for Dario's dilemma asymmetry

**Referee's claim**: The heuristic about A_eff being "more steeply curved on the under-training side" seems wrong — at φ* ≈ 0.70, the local curvature asymmetry of A_eff may go in the opposite direction.

## Assessment

**Relevant**: Yes. The heuristic explanation is imprecise and may be misleading.

**Needs addressing**: Yes, the explanation should be refined.

## Analysis

A_eff(φ) = w_L(1−φ)^α + w_H φ^α

The second derivative: A_eff''(φ) = α(α−1)[w_L(1−φ)^{α−2} + w_H φ^{α−2}] < 0 (concave)

The third derivative (which controls asymmetry):
A_eff'''(φ) = α(α−1)(α−2)[−w_L(1−φ)^{α−3} + w_H φ^{α−3}]

At φ* ≈ 0.70:
- (1−φ*)^{α−3} = 0.30^{−2.6} is very large (small base, large negative exponent)
- φ*^{α−3} = 0.70^{−2.6} is smaller

With α(α−1)(α−2) = 0.40 × (−0.60) × (−1.60) = +0.384 > 0:
A_eff'''(0.70) ∝ +0.384 × [−w_L × 0.30^{−2.6} + w_H × 0.70^{−2.6}]

Since 0.30^{−2.6} ≫ 0.70^{−2.6} and w_L, w_H > 0, the sign depends on relative magnitudes. With w_L < w_H (at baseline) but 0.30^{−2.6} ≫ 0.70^{−2.6}, the first term likely dominates, giving A_eff''' < 0 at φ* ≈ 0.70. This means A_eff is steeper on the OVER-training side (φ > φ*), opposite to the paper's claim.

However, the asymmetry in W(λ_invest) operates through the nonlinear mapping λ → φ*(λ) → A_eff(φ*(λ)), not just through A_eff(φ) directly. The paper conflates two levels of the argument.

## Suggested Fixes

1. **Separate the channels**: "The asymmetry in W(λ_invest) arises from the composition of three channels: (a) the nonlinear mapping λ → φ*(λ), which is concave (since ε_{φ*,λ} < 1 and decreasing in λ); (b) the dominance of the H-regime term in A_eff at baseline (accounting for ~70% of value), which means under-training destroys more value than over-training sacrifices; and (c) the timing channel, where pessimistic firms invest later (higher X*), compressing the option value discount. The local curvature of A_eff(φ) around φ* is insufficient to determine the sign of W''' — the nonlinear mapping from beliefs to policy and the multi-channel value function are the primary drivers."

2. **Drop or weaken the "steeper curvature" claim** and focus on the economic intuition: "Under-training destroys the dominant source of value (H-regime upside), while over-training sacrifices L-regime revenue that is small by comparison."
