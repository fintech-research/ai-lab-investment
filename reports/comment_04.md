# Comment 4: Contradictions in baseline results comparison

**Referee's claim**: The baseline results paragraph mixes several trigger/capacity objects without clearly distinguishing which regime/problem each comes from.

## Assessment

**Relevant**: Yes. The paragraph is genuinely confusing — it presents X* ≈ 0.0047 (single-firm with regime switching), X_P ≈ 0.0082 (duopoly leader preemption), X_H^{mono} ≈ 0.0163 (H-regime monopolist), and K* ≈ 0.0067 vs K_F ≈ 1.30 without clear disambiguation.

**Needs addressing**: Yes. The passage needs clearer labeling and explicit acknowledgment of the scale differences.

## Analysis

The confusion arises from three sources:

1. **Which "monopolist trigger"?** The paper says "the preemption trigger X_P ≈ 0.0082 < X_H^* ≈ 0.0163" for the acceleration comparison. X_H^* = X_H^{mono} ≈ 0.0163 is the H-regime monopolist trigger (the optimal trigger for a single firm in regime H only, without regime switching). Meanwhile X* ≈ 0.0047 is the single-firm trigger under the full model with regime switching and φ optimization. A reader could mistake X* for the monopolist benchmark, in which case X_P > X* looks like deceleration.

2. **Capacity comparison**: K* ≈ 0.0067 (single-firm with φ optimization) vs K_F ≈ 1.30 (duopoly follower) differ by ~200×. This is because the single-firm model uses A_eff (which includes the full H-regime contribution), while the duopoly follower faces contest shares s_i < 1 that dramatically reduce effective revenue per unit K, requiring much larger scale. The statement "reduces capacity per firm relative to the monopolist benchmark" is opaque without specifying which monopolist benchmark.

3. **Unit scale**: All quantities use the same normalization (c = 1), but the effective "size" of the economy differs across model environments because of contest shares.

## Suggested Fixes

1. **Label each object explicitly**: "The single-firm model with regime switching produces X* ≈ 0.0047... The H-regime monopolist trigger (without regime switching) is X_H^{mono} ≈ 0.0163... The duopoly leader's preemption trigger is X_P ≈ 0.0082, representing a ~50% reduction relative to X_H^{mono}."

2. **Explain the scale difference**: Add a sentence: "The large difference in raw scale between single-firm (K* ≈ 0.0067) and duopoly (K_F ≈ 1.30) quantities arises because the duopoly contest shares reduce firm i's effective revenue coefficient, requiring larger capacity to generate the same effective revenue. All comparisons of competitive effects should be made within the same model environment (e.g., K_F vs. K_mono in the duopoly, not K_F vs. K* from the single-firm model)."
