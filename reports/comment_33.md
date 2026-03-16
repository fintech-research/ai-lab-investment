# Comment 33: Notation overload for variable N

**Referee's claim**: N is used for two different groupings in adjacent paragraphs — first as N = c_D/r + δK_i/r in the ∂X_D/∂λ decomposition, then as N(ℓ) absorbing the markup factor.

## Assessment

**Relevant**: Yes, but minor. The reuse of N in close proximity creates a small risk of confusion.

**Needs addressing**: Yes, with a simple notation change.

## Analysis

In the Proposition 2 proof:
- First use: N = c_D/r + δK_i/r (the cost terms in the default boundary numerator)
- Second use (Part iii): N(ℓ) = [β_s^−/(β_s^−−1)] · (c_d ℓ I(K)/r + δK/r) (which includes the markup factor)

These are different objects: the second includes the markup M(β_s^−) while the first does not.

## Suggested Fixes

1. **Rename one of them**: Use N for the first (cost-only) and N̄(ℓ) or Ñ(ℓ) for the second (which includes the markup). Or use a different letter entirely (e.g., "Write the default boundary as X_D = Ψ(ℓ) / A_eff,i(φ_i)").

2. **Add a clarifying parenthetical**: "where N(ℓ) ≡ M(β_s^−) · (c_d ℓ I(K)/r + δK/r) denotes the full numerator of the default boundary expression (distinct from the cost term N used in the λ-decomposition above)."
