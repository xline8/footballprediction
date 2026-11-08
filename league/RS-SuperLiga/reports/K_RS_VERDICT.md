# Verdict — K-RS (RS-SuperLiga cards): **NOT BUILT (feasibility)**

Frozen decision: PREREG_K_RS.md (branch `wip-rs-superliga`, commit
a0b379d, before any fitting).

No model was fitted, no dev gate was run, and the virgin was not read for
cards. Reason, in one paragraph: there is no usable yellows target with
the same meaning in dev and virgin. The dev-era event feed carries Card
events at 0.041–0.120 per match (41–66 cards per season, essentially
YellowRed only; split-half trait reliability r = 0.060) against a real
level of ~4.7, while the stats-feed `yellow_cards` key exists only in the
virgin season (4.230/match) — and where both exist they disagree: in
2025/2026 the stats feed undercounts the event feed by 0.432
yellows/match (events 4.662 vs stats 4.230), exact agreement 72.6%, never
exceeding events. The X8 referee arm is dead independently (referee names
absent in all 1,192 dev matches). This is a feasibility verdict recorded
pre-fitting, not a gate FAIL. K-RS may be pre-registered fresh once a
usable dev-era yellows feed exists; it may not be rescued inside this
prereg.
