# Comment 27: Inconsistent notation for the continuous coupon payment

**Referee's claim**: The coupon is introduced as d = c_d · ℓ · I(K), then formulas use c_D as the coupon payment, then debt value uses d again. The visual proximity of c_D and c_d adds confusion.

## Assessment

**Relevant**: Yes, but minor. The notation is inconsistent across sections.

**Needs addressing**: Yes, with a notation cleanup.

## Analysis

The paper defines:
- d = c_d · ℓ · I(K) — the continuous coupon flow (Section 2.4.3)
- c_D = c_d · ℓ · I(K) — the coupon payment in default boundary formulas (Section 2.4.4)
- d — reappears in the debt value equation (Section 2.4.5)

Since d ≡ c_D, this is just a notational inconsistency, not a mathematical error. But c_D looks confusingly similar to c_d (the coupon rate), and the switch between d and c_D is jarring.

## Suggested Fixes

1. **Unify notation**: Use c_D ≡ c_d · ℓ · I(K) consistently throughout, defined once in Section 2.4.3 and used in all subsequent formulas. Drop the d notation entirely.

2. **Alternatively**, use d consistently and never introduce c_D. The subscript D could be confused with "default."
