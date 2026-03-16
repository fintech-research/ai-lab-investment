# Comment 11: Incorrect elasticity value and backwards logic on uncertainty propagation

**Referee's claim**: (1) ε_{φ*,λ} = +12.7 is inconsistent with the analytical FOC, which implies ε ≈ 0.50. (2) The propagation logic is reversed — high forward elasticity implies low inverse elasticity.

## Assessment

**Relevant**: Yes. Both points are correct and this is a high-priority issue.

**Needs addressing**: Yes, urgently.

## Analysis

### Elasticity value

As verified in Comment 3, the analytical elasticity of φ* with respect to λ is:

ε_{φ*,λ} = (1 − φ*)/(1 − α) = 0.30/0.60 = 0.50 at baseline

The reported +12.7 is ~25× too high. This error propagates into the calibration discussion in Section 3.3, where it is used to argue that "this uncertainty propagates substantially into implied beliefs."

### Propagation logic

The paper says: "The high elasticity of φ* with respect to λ (ε = +12.7 at baseline) means that this uncertainty propagates substantially into implied beliefs."

This logic is backwards:
- **High forward elasticity** (dφ*/dλ large) means φ* is very sensitive to λ → a small range of λ maps to a wide range of φ* → inverting, a given uncertainty band in φ̂ maps to a NARROW range of implied λ (high precision, low propagation).
- **Low forward elasticity** (dφ*/dλ small) means a wide range of λ maps to a narrow range of φ* → inverting, uncertainty in φ̂ maps to a WIDE range of implied λ (high propagation).

At the correct ε ≈ 0.50 (low forward elasticity), the propagation argument actually works in the direction the paper intends: modest uncertainty in φ̂ ± 0.10 does map to a substantial range of implied λ (roughly a factor of 2), BECAUSE the forward elasticity is low.

### Reconciliation with the inversion examples

The paper reports: φ̂ = 0.75 ± 0.10 → λ ∈ [0.09, 0.17]. This is consistent with ε ≈ 0.50 (low forward elasticity, substantial inverse amplification), not with ε = 12.7.

## Suggested Fixes

1. **Fix the elasticity** (see Comment 3).

2. **Fix the propagation logic**: "The moderate elasticity of φ* with respect to λ (ε ≈ 0.50) means that φ* varies slowly with λ at baseline, so the inverse mapping λ(φ̂) is steep: modest uncertainty in the observed training fraction (±0.10) translates into a wide range of implied arrival rates."

3. **The numerical examples are correct** — the inversion results (λ ∈ [0.09, 0.17] for φ̂ = 0.75 ± 0.10) are internally consistent and should be retained. Only the elasticity value and the verbal logic need correction.
