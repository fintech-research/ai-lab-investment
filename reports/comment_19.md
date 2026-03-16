# Comment 19: Flawed intuition for marginal cost of training in Appendix A

**Referee's claim**: (1) The "double penalty" language is misleading because the absolute marginal revenue loss from raising φ is actually smaller in duopoly than monopoly. (2) Claim (c) that H-regime benefit is "independent of the competitive phase" is too strong since H-regime payoffs are contested post-follower entry.

## Assessment

**Relevant**: Yes. Both points are correct.

**Needs addressing**: Yes — the intuition should be refined.

## Analysis

### "Double penalty"

In the monopoly phase, the marginal revenue loss from increasing φ_L is:
∂π_i^L/∂φ = −X · α · K^α · (1−φ)^{α−1} (direct capacity effect only, since s_L = 1)

In the symmetric duopoly phase:
∂π_i^L/∂φ = −X · α · K^α · (1−φ)^{α−1} · s_i · (2 − s_i)

With s_i = 1/2: the factor is s_i(2−s_i) = 1/2 · 3/2 = 3/4 < 1.

So the TOTAL marginal cost of training is actually **lower** in duopoly (3/4 of the monopoly cost), not higher. The "double penalty" language suggests the opposite.

What the paper means is that the duopoly cost has two *components* (direct capacity + contest share), whereas monopoly has only one (direct capacity). But the total is smaller, not larger.

### H-regime benefit independence

The paper says: "the H-regime benefit of training is independent of the competitive phase." But H-regime revenue involves contest shares s_i^H that depend on whether the leader is in monopoly (s_L^H = 1) or duopoly (s_L^H < 1). So the H-regime benefit is NOT independent of phase.

## Suggested Fixes

1. **Fix the "double penalty" language**: "In the duopoly phase, the marginal cost of increasing φ includes both a direct capacity reduction and a contest-share loss. Although the total marginal cost in duopoly is smaller in absolute terms (because the contest share multiplier s_i(2−s_i) < 1), the *relative* cost of training is higher in duopoly because the marginal benefit from training (H-regime positioning) is also attenuated by competition for the H-regime share."

2. **Fix claim (c)**: "The H-regime benefit of training is higher during the monopoly phase (when s_L^H = 1) than during the duopoly phase (when s_L^H < 1). This asymmetry in marginal benefit, combined with the longer time over which the monopoly-phase advantage compounds, drives the leader's higher training fraction."
