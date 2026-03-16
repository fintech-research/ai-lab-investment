# Comment 26: Contradiction regarding fixed market size in Tullock contest

**Referee's claim**: "The Tullock form assumes a fixed total market size" is imprecise — aggregate industry revenue depends on capacities and scales up with proportional increases.

## Assessment

**Relevant**: Yes. The statement is imprecise.

**Needs addressing**: Yes, with a correction.

## Analysis

The paper says (Section 5, Limitations): "Revenue depends on relative capacity, which fits a zero-sum share game but not a growing market; in particular, the Tullock form assumes a fixed total market size."

This is incorrect. With the Tullock payoff π_i = X · y_i^{2α}/(y_i^α + y_j^α):
- If both firms scale capacity proportionally (y_1, y_2) → (ty_1, ty_2), total revenue scales as t^α — the market size grows.
- The "fixed" aspect is that the contest share is zero-sum: one firm's gain in share is the other's loss. But total revenue is NOT fixed.

The intended limitation is that the Tullock form involves pure business stealing — symmetric entry doesn't expand aggregate revenue (it just splits it), unlike a Cournot specification where additional capacity lowers prices but expands quantity.

## Suggested Fixes

1. **Correct the statement**: "Revenue depends on relative capacity through a zero-sum share function: symmetric entry by a second firm splits the pie rather than expanding it, unlike a Cournot specification where additional industry capacity would serve new demand. Under asymmetry, the Tullock form generates a revenue-expansion effect (Comment 23/OF-4), but it does not capture the market-growing effect of AI adoption where investment expands total addressable demand."
