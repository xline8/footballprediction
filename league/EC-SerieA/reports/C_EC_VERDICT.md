# Verdict — C-EC (EC-SerieA corners): **NOT-BUILDABLE**

Frozen decision: PREREG_C_EC.md (prereg commit
1a2eb966f78fe43570c2f4a1177bf27b14ba2a6e, before any fitting).

No model was fitted, no dev gate was run, and the virgin was not
read for corners. Reason: the corners target exists ONLY in the
stats era (2025+): 0 matches with a stats feed in 2021–2023, 1 match
in 2024, 311/312 in 2025. There is no dev season, no warm-up season,
and no scored dev window at all before the virgin season itself, so
no trait reliability is measurable on dev (split-half r null, n = 0
teams), no 1H share is computable on dev (0 matches with period
splits in dev), and no line can be selected. The X7 opp-box-touches
covariate likewise exists only in the stats era, so a touches
variant has no dev window either. This is a feasibility verdict
recorded pre-fitting, not a gate FAIL. The frozen split was not
moved to manufacture a dev window. C-EC may be pre-registered fresh
once dev-era stats seasons exist; it may not be rescued inside this
prereg.
