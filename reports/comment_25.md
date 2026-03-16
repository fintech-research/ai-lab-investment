# Comment 25: Inaccurate description of monopoly opportunity cost

**Referee's claim**: "The monopoly phase eliminates the opportunity cost of forgone inference revenue" is overstated — increasing φ_L still reduces inference revenue even in monopoly; what monopoly removes is the contest-share-loss component.

## Assessment

**Relevant**: Yes. The statement is materially overstated.

**Needs addressing**: Yes.

## Analysis

The paper says (Introduction): "Duopoly preemption changes both timing and training incentives: the leader allocates more to training than the follower because the monopoly phase eliminates the opportunity cost of forgone inference revenue."

In the monopoly phase, the leader's L-regime revenue is X · [(1−φ_L)K_L]^α with s_L = 1. Increasing φ_L still reduces inference capacity (1−φ_L)K_L and therefore reduces revenue. The direct capacity cost is not eliminated.

What monopoly eliminates is the *contest-share-loss* channel: in monopoly, s_L = 1 regardless of φ_L, so increasing training doesn't erode market share. In duopoly, increasing φ_L reduces both capacity AND contest share — the "double penalty" from Appendix A (though as noted in Comment 19, the net effect is actually smaller in duopoly).

## Suggested Fixes

1. **Correct the statement**: "the leader allocates more to training than the follower because the monopoly phase eliminates the *contest-share component* of the opportunity cost of training: with no rival, the leader's market share is insensitive to its training allocation, so the only cost of training is the direct reduction in inference capacity."

2. **Alternatively**: "because the monopoly phase reduces the marginal cost of training — the leader sacrifices only the direct capacity channel, not the additional contest-share erosion that a duopoly firm would face."
