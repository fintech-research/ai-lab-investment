# Comment 7: Misspecification of the leader's H-regime continuation value

**Referee's claim**: The statement that the leader earns monopoly revenue "in both regimes" before follower entry is misleading, because if the economy switches to H while the follower is out, the follower's H-regime entry threshold may differ from the L-regime trigger.

## Assessment

**Relevant**: Yes. The comment identifies a real modeling simplification — the paper uses the unconditional A_eff mapping rather than solving regime-contingent entry policies.

**Needs addressing**: Yes, with a clarifying remark.

## Analysis

In the model, the leader's pre-follower value uses A_eff,i with s_i = 1 (monopoly in both regimes), which implicitly assumes that if regime H arrives before follower entry, the leader retains monopoly indefinitely. In reality, the follower's optimal entry in regime H could differ from its L-regime trigger X_F, and the leader's H-regime monopoly duration would be finite.

The paper handles this through the A_eff framework, which unconditionally averages L and H regime values — a standard approach in regime-switching real options. This is acknowledged in the footnote to the default boundary, but not in the preemption section.

The follower's trigger X_F is computed as a single number, not a regime-pair (X_F^L, X_F^H). This is a simplification inherent in the unconditional approach.

## Suggested Fixes

1. **Add a clarifying remark** after the "monopoly revenue" sentence: "This formulation uses the unconditional effective revenue coefficient A_eff (which averages L- and H-regime values), so the follower's entry trigger X_F is not regime-contingent. A fully state-dependent formulation would feature separate follower triggers (X_F^L, X_F^H) linked by the switching intensity; the unconditional approach is a standard simplification in applied regime-switching models that preserves the key economic forces while maintaining analytical tractability."

2. **Cross-reference** the existing footnote about the unconditional A_eff approximation being conservative.
