# Verdict — K-EC (EC-SerieA cards): **NOT-BUILDABLE**

Frozen decision: PREREG_K_EC.md (prereg commit
1a2eb966f78fe43570c2f4a1177bf27b14ba2a6e, before any fitting).

No model was fitted, no dev gate was run, and the virgin was not
read for cards. Reason: there is no cards target in any dev season
under either source. Stats-feed yellows exist only from 2025
(0 matches with a stats feed in 2021–2023, 1 match in 2024,
311/312 in 2025), and the event feed in dev carries zero plain
Yellow events (2021–2024: Red 240, YellowRed 170, Yellow 0) — the
only dev card events are second yellows, the wrong target, so there
is no event-feed fallback. No trait reliability is measurable on
dev, no 1H share is computable on dev, the X8 referee covariate
cannot be measured on dev (no referee field populated in any dev
match), and no line can be selected. This is a feasibility verdict
recorded pre-fitting, not a gate FAIL. The frozen split was not
moved to manufacture a dev window. K-EC may be pre-registered fresh
once a dev cards target exists; it may not be rescued inside this
prereg.
