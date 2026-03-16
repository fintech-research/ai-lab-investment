# Comment 31: Direction of markup factor limit

**Referee's claim**: The paper says increasing λ pushes the markup M = β_s^−/(β_s^−−1) "toward 1 from above," but for β_s^− < 0, M ∈ (0,1), so the limit is from below.

## Assessment

**Relevant**: Yes. The direction is wrong — this is a clear error.

**Needs addressing**: Yes.

## Analysis

For the default boundary, β_s^− < 0 (negative characteristic root).

M = β_s^−/(β_s^−−1)

With β_s^− < 0:
- β_s^−−1 < −1 (more negative than −1)
- M = (negative)/(more negative) = positive, and |β_s^−| < |β_s^−−1|, so M ∈ (0, 1)

As λ increases, β_s^− becomes more negative (larger in absolute value), so:
- |β_s^−| → ∞
- M = β_s^−/(β_s^−−1) → 1 **from below** (since M < 1 for all finite β_s^−)

The paper says "from above," which is incorrect. The confusion likely arises from the standard investment trigger markup β^+/(β^+−1) > 1, which approaches 1 from above as β^+ → ∞. But the default boundary uses the negative root, where the markup is in (0,1).

dM/dλ > 0 is correct (the sign statement is fine), just the "from above" direction is wrong.

## Suggested Fixes

1. **Change "from above" to "from below"**: "...making β_s^− more negative and pushing the markup M toward 1 from below."
