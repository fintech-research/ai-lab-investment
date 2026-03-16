# Comment 18: Inaccurate claim about convexity of leader's value function

**Referee's claim**: The claim that regime switching "adds a convex component to both L(X) and F(X)" is not obvious for the leader, where the post-switch competitive entry could contribute a concave loss term.

## Assessment

**Relevant**: Yes, but minor. The claim is imprecise rather than wrong.

**Needs addressing**: Yes, with a qualification.

## Analysis

For the follower, F(X) ∝ X^{β_H} is indeed strictly convex (power function with β_H > 1). Adding a regime-switching component maintains or enhances convexity.

For the leader, L(X) includes:
- Monopoly-phase revenue (approximately linear in X)
- A default kink at X_D (non-convex)
- H-regime continuation value (option-like, potentially convex)
- Post-follower-entry competition effects (could be concave if the follower's entry erodes the leader's position)

The net effect on L''(X) depends on parameter values. The statement that regime switching "adds a convex component" is technically correct (it adds terms of the form X^{β_H} to the value function), but the overall convexity of L(X) is not guaranteed.

## Suggested Fixes

1. **Qualify the statement**: "(c) the regime-switching option adds power-function terms (proportional to X^{β_H}) to both L(X) and F(X), which contribute positive curvature; for F(X) this reinforces convexity, while for L(X) the net curvature depends on the interaction with the default kink and competitive effects."
