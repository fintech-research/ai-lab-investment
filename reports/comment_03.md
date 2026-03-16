# Comment 3: Incorrect elasticities in Table 7

**Referee's claim**: Table 7's reported sensitivities appear inconsistent with the analytical characterization. In particular, K* should not depend on λ (yet ε_{K*,λ} = +4.8), and ε_{φ*,λ} = +12.7 is too high (analytical value is ~0.50).

## Assessment

**Relevant**: Yes. This is a high-priority issue — multiple elasticities in Table 7 appear to be numerically incorrect.

**Needs addressing**: Yes, urgently. The elasticity table is cited throughout the paper and the calibration section.

## Analysis

### ε_{K*,λ} = +4.8 is wrong (should be 0)

By Proposition 1, K* depends only on (α, β_H, γ, δ, r, c). The characteristic root β_H solves σ²β(β−1)/2 + μ_H β − r = 0, which does not involve λ. Therefore K* is analytically independent of λ, and ε_{K*,λ} should be exactly 0.

### ε_{φ*,λ} = +12.7 is wrong (should be ~0.50)

From the FOC (Appendix A, Step 5), φ* satisfies: w_H/w_L = ((1−φ)/φ)^{α−1}, where w_H/w_L = λA_H = λ/(r−μ_H).

Differentiating implicitly:
dφ*/dλ = φ*(1−φ*) / (λ(1−α))

Elasticity: ε = (dφ*/dλ)(λ/φ*) = (1−φ*)/(1−α) = 0.30/0.60 = 0.50 at baseline.

A direct numerical check confirms: at λ = 0.101 (1% increase from 0.10), φ* ≈ 0.7044, giving ε ≈ 0.53.

The reported ε = +12.7 is about 25× too high. This likely indicates a bug in the elasticity computation (e.g., computing arc elasticities over a very different range, using log-transforms incorrectly, or a code error in the sensitivity routine).

### ε_{φ*,α} = −5.1 appears to have the wrong sign

From the implicit differentiation of the FOC:
dφ*/dα = φ*(1−φ*) · ln(φ*/(1−φ*)) / (1−α)

At baseline (φ* ≈ 0.70): ln(0.70/0.30) = ln(2.33) ≈ 0.85 > 0, so dφ*/dα > 0.
The elasticity should be positive (~0.17), not −5.1.

### Root cause

The elasticity computation code needs to be audited. Possible issues:
- The finite difference step size may be too large, causing non-local effects
- The code may be computing elasticities for a different model variant (duopoly vs single-firm)
- There may be a bug in the parameter perturbation routine (e.g., perturbing the wrong parameter)

## Suggested Fixes

1. **Audit and fix the elasticity computation code**. Verify each entry against analytical formulas: K* has a closed form, so all K* elasticities can be checked analytically. For φ*, the implicit function theorem gives exact local elasticities.

2. **Add analytical elasticity formulas** in Appendix D alongside the numerical values, at least for the parameters where closed-form expressions exist (λ, α for φ*; all parameters for K* via the explicit formula).

3. **Rewrite the calibration discussion** that references these elasticities (Section 3.3 on implied beliefs, the claim about "high elasticity of φ* with respect to λ").
