# Comment 24: Contradiction regarding hardware repurposing in Introduction

**Referee's claim**: "Both activities consume the same scarce hardware" contradicts "purpose-built training clusters cannot be easily repurposed."

## Assessment

**Relevant**: Yes, but minor. The juxtaposition is indeed confusing.

**Needs addressing**: Yes, with a wording adjustment.

## Analysis

The Introduction says:
1. "Both activities consume the same scarce hardware" — implying fungibility
2. "purpose-built training clusters cannot be easily repurposed" — implying rigidity

These statements can coexist (the same type of GPU can be used for either purpose, but facility-level configurations, networking, and software architectures create switching costs), but the current wording doesn't convey this nuance.

Section 5 later notes that "firms can reallocate GPUs between training and inference on timescales of weeks," which makes the Introduction's "cannot be easily repurposed" feel too strong.

## Suggested Fixes

1. **Soften the second sentence**: "These facilities take years to build, and large-scale training clusters involve substantial configuration and networking investments that create adjustment costs when reallocating compute between training and inference, even though the underlying hardware is physically fungible."

2. **Add a cross-reference**: "(see Section 5 for a discussion of the timescales and costs of reallocation, which motivates the static φ assumption)."
