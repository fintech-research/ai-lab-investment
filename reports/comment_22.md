# Comment 22: Mix-up between cost convexity (γ) and revenue concavity (α)

**Referee's claim**: The paper uses scaling laws ("doubling compute does not double capability") to motivate the convex cost I(K) = cK^γ, but scaling laws map more naturally to the revenue concavity α ∈ (0,1).

## Assessment

**Relevant**: Yes. The paragraph conflates two distinct economic mechanisms.

**Needs addressing**: Yes — the motivations for γ and α should be separated.

## Analysis

The paper says: "A firm invests an irreversible lump sum I(K) = cK^γ to install capacity K > 0, where γ > 1 captures diminishing returns (equivalently, convex investment costs). This specification... reflects the empirical regularity that AI scaling laws exhibit diminishing returns to compute: doubling compute does not double capability."

The issue:
- **Scaling laws** (Kaplan et al., Hoffmann et al.) describe the relationship between compute/data and model performance/capability. This is a **revenue-side** phenomenon: more compute yields better models, but with diminishing returns. This is captured by α ∈ (0,1) in the revenue function π = X · (φK)^α.

- **γ > 1** captures **cost-side** convexity: the marginal cost of building additional capacity is increasing. This reflects supply-chain bottlenecks (GPU procurement), power constraints, site preparation costs, and construction complexity — not diminishing returns to compute in model training.

The two mechanisms are conceptually distinct: α governs how much capability (and hence revenue) an additional unit of compute delivers, while γ governs how much it costs to procure that additional unit.

## Suggested Fixes

1. **Separate the motivations**: "A firm invests I(K) = cK^γ with γ > 1, reflecting increasing marginal costs of capacity procurement: power constraints, GPU supply bottlenecks, data center site preparation, and construction complexity all contribute to super-linear scaling of investment costs. The revenue elasticity α ∈ (0,1) in the contest function separately captures diminishing returns to compute in capability and revenue generation, consistent with the empirical AI scaling laws of Kaplan et al. (2020) and Hoffmann et al. (2022)."

2. **Remove the scaling laws citation** from the γ paragraph and move it to the α discussion (Section 3.2 or where α is first introduced).
