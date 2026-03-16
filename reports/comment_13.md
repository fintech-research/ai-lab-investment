# Comment 13: Incorrect comparative static for training fraction

**Referee's claim**: Step 6(ii) says ∂φ*/∂(r−μ_L)^{−1} < 0, but w_H/w_L = λA_H = λ/(r−μ_H) is independent of μ_L, so φ* should not vary with (r−μ_L)^{−1}.

## Assessment

**Relevant**: Yes. This is a genuine analytical error — the stated comparative static is wrong.

**Needs addressing**: Yes, this is high priority since it appears in Proposition 1.

## Analysis

From Appendix A, Step 5:
- w_L = 1/(r − μ_L + λ)
- w_H = λA_H/(r − μ_L + λ), where A_H = 1/(r − μ_H)
- w_H/w_L = λA_H = λ/(r − μ_H)

The ratio w_H/w_L is **independent of μ_L**. Since the FOC for φ* depends only on w_H/w_L (and α), the optimal training fraction φ* does not depend on μ_L.

The paper's claim that "a higher L-regime revenue premium 1/(r−μ_L) raises w_L relative to w_H, decreasing w_H/w_L" is algebraically incorrect. A change in (r−μ_L) affects both w_L and w_H proportionally (through the common denominator r−μ_L+λ), leaving their ratio unchanged.

**Intuition for why φ* is independent of μ_L**: A higher μ_L raises the present value of ALL cash flows in regime L proportionally — both inference revenue (through w_L) and the expected value of the regime switch (through the λ/(r−μ_L+λ) weighting). Since both terms scale equally, the optimal split between training and inference is unaffected. The training fraction responds only to the *relative* value of H-regime vs L-regime positioning, which is governed by λ/(r−μ_H).

## Suggested Fixes

1. **Remove or correct Part (ii) of Proposition 1**: Either delete it entirely (since the comparative static is zero) or replace it with a correct comparative static. Possible alternatives:
   - ∂φ*/∂μ_H > 0: higher H-regime growth raises w_H/w_L = λ/(r−μ_H), shifting allocation toward training.
   - ∂φ*/∂r < 0: higher discount rate raises (r−μ_H), reducing w_H/w_L, shifting allocation toward inference.

2. **Update Appendix A, Step 6(ii)** accordingly, with the correct algebra showing w_H/w_L = λ/(r−μ_H) is independent of μ_L.

3. **Check whether any downstream text** relies on the incorrect comparative static (e.g., discussions of how L-regime conditions affect training allocation).
