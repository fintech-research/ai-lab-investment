# Comment 20: Conflation of dynamic reallocation with learning about λ

**Referee's claim**: The sentence "no switch after one period is bad news about λ_true" is incorrect under the baseline specification where λ is known and the switch time is memoryless.

## Assessment

**Relevant**: Yes. Under known λ and exponential (memoryless) waiting times, non-arrival carries no information about λ.

**Needs addressing**: Yes.

## Analysis

The paper says (Section 5, "Direction of Bias from Static φ"):

"If the regime switch has not occurred after one period, the firm observes that it remains in regime L, which is (weakly) bad news about λ_true. The optimal response is to decrease φ..."

Under the model's specification:
- λ is a known, fixed parameter (not a random variable)
- The regime switch follows a memoryless exponential distribution
- Non-arrival after one period does NOT update beliefs about λ (there are no beliefs to update — λ is known)
- The remaining waiting time has the same distribution as the original: P(T > t+1 | T > 1) = P(T > t)

The "bad news" framing implicitly assumes a Bayesian learning extension where λ is unknown and the firm updates its posterior from non-arrival. This is not the baseline model.

The intended point — that a dynamic firm would shift toward inference over time if the switch hasn't occurred — could be motivated differently:
- In a finite-horizon model, less remaining time reduces the expected benefit from training
- With learning about λ (an extension), non-arrival would indeed lower the posterior on λ
- With impatience (discounting), the H-regime payoff becomes less valuable the longer the firm waits

## Suggested Fixes

1. **Replace the "bad news" sentence**: "If the regime switch has not occurred after one period and the firm can reallocate, the option value of the remaining H-regime payoff has declined (through discounting alone, even without updating beliefs about λ), shifting the optimal allocation toward inference. Under an extended model with unknown λ (Bayesian learning), non-arrival would additionally lower the posterior arrival rate, further reducing the optimal φ."

2. **Alternatively**, frame the entire argument through the lens of a finite-horizon or discounting effect: "In a dynamic setting, the firm's remaining expected benefit from training decreases over time as the regime switch becomes more discounted, creating a natural time trend toward inference allocation."
