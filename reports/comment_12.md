# Comment 12: Asset pricing terminology contradiction

**Referee's claim**: The use of "risk-adjusted (certainty-equivalent) growth rate" μ_s alongside a WACC discount rate r is confusing, because "certainty-equivalent" language is usually associated with discounting at r_f.

## Assessment

**Relevant**: Yes, but minor. The paper already addresses this in Footnote 12, which explains the reduced-form convention clearly.

**Needs addressing**: Yes, with a brief reinforcing sentence in Section 3.1.

## Analysis

The paper's approach is standard and correct: μ_s is the risk-adjusted growth rate (physical growth rate minus risk premium), and r is the WACC. Discounting expected cash flows (under the risk-adjusted measure) at r gives the correct present value. Footnote 12 in Section 2 explains this clearly.

However, Section 3.1 says "r is the WACC and μ_s is the risk-adjusted (certainty-equivalent) growth rate" without fully restating the convention. The phrase "certainty-equivalent" is indeed more commonly associated with discounting at r_f, which could confuse readers who missed the footnote.

The later credit-spread calculation introduces a separate r_f, which adds to the potential confusion.

## Suggested Fixes

1. **In Section 3.1**, replace "risk-adjusted (certainty-equivalent) growth rate" with "risk-adjusted growth rate" and add a parenthetical: "(see Footnote 12 in Section 2 for the detailed framework; the key convention is that μ_s already incorporates a risk adjustment so that discounting at WACC r yields the correct present value)."

2. **When r_f first appears** (credit spread section), add: "The risk-free rate r_f enters only in the credit spread calculation; all present-value computations use the WACC r as described in Section 2."
