# Comment 8: Confusion in the boundary condition for preemption existence

**Referee's claim**: The endpoint inequality L(X_F*) > F(X_F*) is justified by "accumulated monopoly rents," which suggests L is a continuation value, not the "NPV of entering at state X" as defined in Proposition 3(i).

## Assessment

**Relevant**: Yes. The definition of L(X) and the boundary argument are not fully aligned as written.

**Needs addressing**: Yes — the definitions need tightening.

## Analysis

Proposition 3(i) defines: "L(X) = E_L(X) − (1−ℓ)I(K_L) is the leader's NPV of entering at state X."

The Appendix A proof says: "At X = X_F*: the leader has accumulated monopoly rents over the interval since entry while the follower has just triggered, so L(X_F*) > F(X_F*)."

These are inconsistent. If L(X) is the NPV of entering NOW at state X, then L(X_F*) is the value of a leader that enters at X_F* (not one that entered earlier). But the "accumulated monopoly rents" argument requires the leader to have entered at X_P < X_F*, having already operated during [X_P, X_F*].

The correct interpretation is: L(X) is the leader's *invest-now* payoff — the NPV of entering at state X, which includes the discounted stream of monopoly rents from X until follower entry at X_F*, followed by duopoly rents. At X = X_F*, the monopoly phase is zero (leader and follower enter simultaneously), but the leader still earns duopoly rents with a leader-sized capacity that was optimized for the leader role. The boundary condition L(X_F*) > F(X_F*) holds because the leader's installed project value at X_F* exceeds the follower's option value (which is zero net of investment cost at the exercise boundary).

Actually, at X_F*, the follower is indifferent between investing and waiting, so F(X_F*) equals the follower's NPV of investing at X_F*. The leader's NPV of entering at X_F* includes a weakly better capacity/training choice (optimized for the leader role) and possibly accumulated value from the specific K_L, φ_L choices.

The proof's wording is misleading — it should be rewritten.

## Suggested Fixes

1. **Clarify the definition**: "L(X) is the leader's NPV of investing at demand state X, defined as the equity value of the installed project at X minus the equity contribution: L(X) = E_L(X) − (1−ℓ)I(K_L). This is a function of X evaluated at a single point, not a continuation value from prior entry."

2. **Fix the boundary argument**: "At X = X_F*, the follower is indifferent between investing and waiting (by construction of X_F*), so F(X_F*) equals the follower's NPV of investing now. The leader's NPV of investing at X_F* exceeds the follower's because the leader (a) enters as the first mover with monopoly contest share during [X_F*, X_F*] = {X_F*} (instantaneous) plus the continuation from being the installed leader, and (b) has optimized (K_L, φ_L) for the leader role. Formally, L(X_F*) > 0 ≥ F(X_F*) − (value of option component)."
