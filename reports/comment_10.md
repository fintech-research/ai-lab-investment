# Comment 10: Mismatched segment revenue and corporate CapEx

**Referee's claim**: The Google-like archetype pairs segment revenue (Google Cloud, $43.2B) with consolidated Alphabet CapEx ($91.4B), inflating the CapEx/Revenue ratio.

## Assessment

**Relevant**: Yes. The mismatch is a legitimate calibration concern, though the paper already partially acknowledges it.

**Needs addressing**: Yes, with a brief clarifying note.

## Analysis

The paper states: "For the Google-like archetype, revenue is Google Cloud revenue ($43.2B in 2024)... CapEx is total Alphabet capital expenditure ($91.4B in 2025), approximately 60% to servers and 40% to data centers and networking."

This pairing is intentional — the rationale is that Alphabet's CapEx is overwhelmingly AI-related (serving Search, Gmail, YouTube AI features, Gemini, etc.) even though only Cloud revenue is the explicit AI segment. However, the resulting CapEx/Revenue ratio of 1.52× is inflated relative to a like-for-like comparison.

The paper already notes: "the CapEx concept differs across archetypes" and "For the private labs, it captures cloud compute commitments rather than owned infrastructure, so the ratios are not directly comparable."

## Suggested Fixes

1. **Add an explicit sentence**: "The Google-like archetype intentionally uses consolidated Alphabet CapEx as the numerator because the majority of this spending supports AI workloads across all Google products, not only the Cloud segment. A segment-level ratio using only Cloud-attributed CapEx would be lower (approximately 0.5–0.7×), but would understate the total AI infrastructure investment that the model's capacity K represents. The 1.52× ratio should be interpreted as a firm-wide AI infrastructure intensity measure."

2. **Consider adding a robustness note**: Show that the qualitative cross-sectional ordering (xAI > Google > OpenAI > Anthropic in investment intensity) is preserved under alternative CapEx definitions.
