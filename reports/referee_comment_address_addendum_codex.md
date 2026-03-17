# Addendum: Re-Check of Previously Unresolved Points

**Reviewer:** codex
**Date:** 2026-03-16
**Scope:** Follow-up check against the current manuscript only.

## Summary

I re-checked the points that remained open in my earlier report. The paper now resolves almost all of them.

- The `A_1 = 0` boundary-condition issue is now addressed with a formal Step 5b in the appendix; see `paper/_appendix.qmd:100`.
- The one-boundary default formulation is now supported by a one-way-coupling argument plus a quantitative baseline error bound; see `paper/_appendix.qmd:128` and `paper/_model.qmd:273`.
- The static-`phi` concern is now supported by a two-period dynamic-reallocation exercise; see `paper/_appendix.qmd:365`.
- The contest-specification concern is now addressed with both Cournot robustness and a fixed-pie comparison; see `paper/_appendix.qmd:345` and `paper/_appendix.qmd:351`.
- The strategic-environment concern for Dario's dilemma is now addressed with a duopoly extension; see `paper/_appendix.qmd:387` and `paper/_valuation.qmd:136`.

## Remaining Point

The only point that still looks only partially addressed is the **normalization / unit interpretation across environments**.

The current revision is much better: it now states clearly that the model is normalized by `c = 1` and that cross-environment interpretation should rely on ratios and percentages rather than raw levels; see `paper/_calibration.qmd:113-117`. That resolves the confusion about how to read the single-firm and duopoly numbers.

What is still missing is an empirical bridge from the model units to observable units. A reader still does not know what one unit of `K` or `X` corresponds to in practice.

## Suggested Fixes

Any one of the following would likely close the point cleanly.

1. Add a short calibration note that maps `K` to a normalized infrastructure unit, for example “one unit of `K` corresponds to one dollar of normalized compute capital” or “one unit of `K` corresponds to one GW-equivalent / GPU-cluster-equivalent of installed capacity after rescaling by `c`.”

2. Add a sentence explaining how `X` should be interpreted observationally, for example as a demand shifter normalized so that only ratios of triggers are meaningful unless one imposes a revenue target.

3. Provide one concrete back-of-the-envelope conversion in the calibration section:
   “If the model is scaled so that the baseline archetype’s 2025 CapEx matches observed CapEx, then `K = ...` corresponds to approximately ... of infrastructure.”

4. Add a brief appendix note stating that the model is intentionally unit-free and that all level comparisons across environments are non-structural, while the economically meaningful objects are invariant ratios such as `X_P / X_H^{mono}`, `phi*`, spreads, and percentage value losses.

## Bottom Line

My updated assessment is:

- Previously unresolved points now fully addressed: `5 / 6`
- Still only partially addressed: `1 / 6`

The only remaining gap is the lack of an explicit observable-unit mapping for `K` and `X`.
