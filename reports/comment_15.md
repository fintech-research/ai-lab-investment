# Comment 15: Unlevered equity value ignores the abandonment option

**Referee's claim**: When ℓ = 0 and δ > 0, the unlevered firm should have an abandonment option (shut down to avoid δK operating costs), but the paper treats E(X) as a pure perpetuity.

## Assessment

**Relevant**: Yes. The comment correctly identifies that the ℓ = 0 case implicitly rules out abandonment.

**Needs addressing**: Yes, with a brief clarifying remark.

## Analysis

The paper says: "Without debt (ℓ = 0), the expression simplifies to the NPV of the unlevered investment: E(X) = A_eff,i · X − δK/r − I(K)."

This is a perpetuity: the firm operates forever, paying δK in perpetuity. With δ > 0 and X potentially declining, there exists a demand level below which the firm would prefer to shut down (abandon) rather than continue paying operating costs. An abandonment boundary X_A would satisfy A_eff · X_A = δK/r (roughly), with an option-value correction.

The model does not include this abandonment option for the unlevered case. The levered case has an endogenous default boundary X_D that serves a similar function (the firm stops when equity value hits zero), but this is driven by debt obligations, not operating costs alone.

This is a modeling choice, not an error: many real options models treat post-investment cash flows as perpetuities. Since the firm invests at a high X* (well above any potential abandonment threshold), the abandonment option has negligible value at the time of investment.

## Suggested Fixes

1. **Add a clarifying sentence**: "The unlevered case treats the firm as a perpetuity with no endogenous abandonment option: once invested, the firm operates indefinitely. An abandonment option (shutting down to avoid operating costs δK when demand falls sufficiently) would add a floor to equity value; its omission is conservative in the sense that it slightly understates unlevered equity value. The effect is quantitatively negligible because the firm invests at X* well above any potential abandonment threshold."

2. No structural model change is needed — this is a standard simplification.
