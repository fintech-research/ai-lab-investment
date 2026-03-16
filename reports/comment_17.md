# Comment 17: Incorrect comparative static for survival threshold

**Referee's claim**: The paper says φ̲ is "decreasing in α," but with the base ratio in (0,1), R is increasing in α, so φ̲ should be increasing in α.

## Assessment

**Relevant**: Yes. The sign is wrong — this is a clear analytical error.

**Needs addressing**: Yes, high priority.

## Analysis

The survival threshold is:
$$\underline{\phi} = \frac{R}{1+R}, \quad R = \left(\frac{r - \mu_H}{r - \mu_L}\right)^{1/\alpha}$$

At baseline: (r−μ_H)/(r−μ_L) = 0.06/0.11 ≈ 0.545, which is in (0, 1).

Since the base b = 0.545 < 1 and R = b^{1/α}:
- As α increases, 1/α decreases.
- Since b < 1 and the exponent 1/α decreases, b^{1/α} INCREASES (approaches b^0 = 1).
- Therefore R is increasing in α, and φ̲ = R/(1+R) is also increasing in α.

The paper says "φ̲ is decreasing in α (lower diminishing returns make training more effective)." This has the wrong sign.

**Correct statement**: φ̲ is *increasing* in α. Higher α (less diminishing returns) means the training capacity needs to be a larger fraction of total capacity to generate enough H-regime value to offset L-regime losses. Equivalently, with less concavity in the revenue function, the H-regime term doesn't benefit as much from training concentration, requiring a higher minimum φ.

The intuition "lower diminishing returns make training more effective" is also backwards in this context. Lower α (MORE diminishing returns) means each unit of training compute is worth relatively more in the H-regime PV calculation (the concavity amplifies the benefit of concentration), lowering the threshold.

## Suggested Fixes

1. **Correct the sign**: "Note that φ̲ is *increasing* in α: with higher revenue elasticity (less diminishing returns), the H-regime training term requires a larger allocation φ to dominate the L-regime inference term, because both terms scale similarly with capacity."

2. **Fix the intuition**: "Lower α (stronger diminishing returns) makes training more effective per unit of allocated compute through the concavity channel, reducing the threshold φ̲."
