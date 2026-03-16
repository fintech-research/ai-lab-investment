# Comment 16: Mismatch between value decomposition formulas and Figure 8

**Referee's claim**: The value decomposition formulas use A_eff (L-regime with switching), but Figure 8's caption says "Parameters: regime H" and normalizes by K_H*, creating ambiguity about which regime's valuation object is plotted.

## Assessment

**Relevant**: Yes. The figure and text use different regime contexts without making the connection explicit.

**Needs addressing**: Yes, with a brief clarifying note.

## Analysis

The value decomposition in Section 4.1 defines:
- V_AIP = A_eff(φ, K_installed) · X − δK_installed/r
- V_gap = NPV(K*, φ*) − V_AIP

These formulas use A_eff, which is an L-regime object (incorporating the H-regime continuation via λ).

Figure 8 (fig_growth_decomposition) caption says "Parameters: regime H, demand at 1.5 X_H*". This suggests the figure uses H-regime valuation (V_H = A_H · X · (φK)^α − δK/r) rather than the L-regime A_eff formulation.

The figure is apparently an H-regime illustration — it shows how the decomposition works using the simpler H-regime setting as a didactic example. The normalization by K_H* (the H-regime optimal capacity) supports this.

## Suggested Fixes

1. **Clarify in the text**: "Figure [X] illustrates the decomposition using the absorbing H-regime valuation as a simplified example (where A_eff reduces to A_H · (φK)^α). The general decomposition formulas above apply equally to the L-regime with regime switching, substituting A_eff from Eq. [X]."

2. **Update the figure caption** to explicitly state: "The illustration uses H-regime valuation for simplicity; the general decomposition applies to both regimes via A_eff."
