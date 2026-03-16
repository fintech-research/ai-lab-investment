# Overall Feedback Assessment

## OF-1: Solving the real options boundary conditions in Section 2.3.3

**Relevant**: Yes. The referee's concern is well-founded — the paper's wording creates an apparent conflict between C being determined by the ODE forcing term and C being determined by boundary conditions.

**Needs addressing**: Yes. The paper says "the only boundary conditions are the smooth-pasting conditions at the investment trigger driven by A_eff, and these determine C alone." In fact, C is already pinned by the ODE (Eq. 10: C = −λB_H/Q_L(β_H)). What the boundary conditions determine — given A1=0 under (A3) — is the trigger X* (and the optimality conditions for K* and φ*). The sentence conflates two distinct roles: the ODE pins C, while the boundary conditions pin X*.

**Suggested fixes**:
1. Rewrite the passage to clearly separate the two steps: (a) C is determined by the ODE's particular solution, (b) A1=0 follows from the absence of an L-regime exercise boundary under (A3), and (c) value-matching and smooth-pasting then determine X* (with C already known).
2. Add a brief remark that the consistency can be verified: using the ODE-determined C and setting A1=0, the smooth-pasting conditions yield X* and confirm that the solution is self-consistent.

---

## OF-2: The dimensionality of the default boundary in Proposition 2

**Relevant**: Yes. The paper uses an unconditional A_eff mapping to reduce a two-regime default problem to a single-regime Leland framework. In a fully coupled regime-switching credit model, default boundaries would be regime-contingent (X_D^L, X_D^H).

**Needs addressing**: Partially. The paper already acknowledges this in a footnote to Eq. 16 ("A fully coupled regime-switching default model would feature state-dependent boundaries... The unconditional A_eff approximation is standard in applied regime-switching real options models and is conservative"). However, the referee is right that the sign and magnitude of ∂X_D/∂λ and the φ̲ threshold depend on this mapping, so the footnote should be elevated or expanded.

**Suggested fixes**:
1. Expand the footnote into a brief paragraph acknowledging that the single-boundary approach is an approximation and stating the direction of bias (the true L-regime default boundary may be somewhat higher, making the faith-based survival mechanism conservative).
2. Add a sentence explaining why φ̲ is independent of λ: the threshold characterizes when ∂A_eff/∂λ > 0, which depends on the ratio of H-regime to L-regime revenue terms, not on λ itself (since λ appears in both numerator and denominator of A_eff symmetrically at the threshold).

---

## OF-3: Rigidity in the training-inference allocation margin

**Relevant**: Yes. The static φ is the most substantive limitation. The paper already discusses this in Section 5 ("Direction of Bias from Static φ") and notes the bias is conservative (static φ overstates the initial training fraction).

**Needs addressing**: Partially. The existing discussion is adequate for a first paper, but the referee wants evidence that the core mechanisms survive even modest relaxation. The paper should strengthen the bias analysis.

**Suggested fixes**:
1. Add a brief robustness check in Appendix E: compute the faith-based survival threshold and Dario's dilemma asymmetry under a simple two-period φ reallocation, confirming the mechanisms are attenuated but preserved.
2. In Section 5, explicitly note that the calibrated φ* ≈ 0.70 is an upper bound on the static-model optimum; under dynamic reallocation, the equivalent static φ would be lower, implying higher implied λ.

---

## OF-4: Total industry revenue expansion in the contest specification

**Relevant**: Yes. The Tullock specification allows total revenue to vary with asymmetry, which could drive some results mechanically. The paper already discusses Cournot robustness in Appendix E but the referee wants more in the main text.

**Needs addressing**: Yes, but the existing Appendix E treatment is appropriate in scope. The main text should add a brief clarifying statement.

**Suggested fixes**:
1. In the discussion of Tullock properties (Section 2.4.1), add a sentence clarifying that the revenue-expansion property under asymmetry means that the leader's gain from capacity dominance partly reflects pie expansion, not just share theft — and note that Cournot (Appendix E) preserves qualitative results without this feature.
2. Add 1-2 sentences to the main results sections confirming that the preemption gap, faith-based survival, and Dario's dilemma asymmetry are all preserved under Cournot.

---

## OF-5: Scale and normalization across model environments

**Relevant**: Yes. The raw numbers (X* ≈ 0.0047 vs X_F ≈ 0.57; K* ≈ 0.0067 vs K_F ≈ 1.30) are confusing because the single-firm and duopoly models use different effective revenue coefficients under the same normalization c=1.

**Needs addressing**: Yes. The scale jump is a consequence of the model structure (contest shares in duopoly modify A_eff,i, changing the optimal scale), but readers will misread it as an error.

**Suggested fixes**:
1. Add a paragraph in Section 3.4 explaining the scale difference: the single-firm model uses A_eff with no contest (monopoly), while the duopoly follower faces contest shares s_i < 1, reducing effective revenue per unit of K and requiring larger scale to justify investment. The comparison should be between like-for-like objects (e.g., follower vs. H-regime monopolist).
2. Consider reporting relative quantities (e.g., K_F/K_mono, X_P/X_F) alongside raw numbers to make comparisons transparent.

---

## OF-6: The strategic environment for Dario's Dilemma

**Relevant**: Yes. Dario's dilemma is formalized in the single-firm benchmark, but the motivating narrative emphasizes competitive preemption. The referee correctly notes that the dilemma is more compelling in the duopoly setting where overinvestment interacts with the race to lead.

**Needs addressing**: Partially. Extending Dario's dilemma to the full duopoly is a substantial computational exercise that would strengthen the paper but is not strictly necessary for the current contribution.

**Suggested fixes**:
1. Add a paragraph in Section 4.3 acknowledging that the single-firm formalization isolates the belief-mismatch channel, and that the duopoly extension would add the strategic preemption penalty for conservative firms (who lose first-mover advantage) — reinforcing the asymmetry.
2. State explicitly that the duopoly extension is a natural direction for future work and sketch the expected direction (preemption would amplify the underinvestment cost because a conservative firm not only under-trains but also loses the leader position).
