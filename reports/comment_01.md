# Comment 1: Incorrect determination of the particular solution coefficient C

**Referee's claim**: There is an inconsistency — C is first derived from the ODE forcing term as C = −λB_H/Q_L(β_H), then the paper says boundary conditions "determine C alone," implying C is re-identified from trigger conditions.

## Assessment

**Relevant**: Yes. The wording in the paper is genuinely confusing and creates an apparent contradiction.

**Needs addressing**: Yes — the wording needs clarification, though the underlying mathematics is correct.

## Analysis

The paper's derivation is actually sound, but the exposition conflates two distinct steps:

1. **C is determined by the ODE**: The particular solution coefficient C = −λB_H/Q_L(β_H) is pinned by the structure of the HJB equation (Eq. 10). This is not a choice — it is forced by the non-homogeneous term.

2. **A1 = 0 under (A3)**: When L-regime revenue alone cannot justify investment (the option premium ratio ≥ 1), there is no standalone L-regime exercise boundary. The homogeneous term A1·X^{β_L^+} has no boundary condition to determine A1, so A1 = 0.

3. **Boundary conditions determine X***: Given F_L = C·X^{β_H} (with C already known), the value-matching and smooth-pasting conditions at the investment trigger determine X* (and jointly with K* and φ* through the FOC system).

The problematic sentence is: "the only boundary conditions are the smooth-pasting conditions at the investment trigger driven by A_eff, and these determine C alone." This should say "these determine X* alone" (since C is already known from the ODE).

## Suggested Fixes

1. **Rewrite the passage** to separate the three steps explicitly: (a) C comes from the ODE, (b) A1 = 0 from the absence of an L-regime boundary, (c) smooth-pasting determines X*.

2. **Add a consistency check sentence**: "The particular-solution coefficient C is fully determined by the ODE's forcing structure (Eq. 10); the smooth-pasting conditions at X* then determine the trigger, and the system is self-consistent because the two boundary conditions (value-matching and smooth-pasting) determine two unknowns (X* and the option value scaling) rather than re-determining C."
