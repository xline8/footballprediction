# Verdict — K-UY (UY-LigaAUF cards / yellows): **NOT-BUILDABLE**

Frozen decision: PREREG_K_UY.md (prereg commit
7d43257df3460bcfa1bf07c8c94d2ff4466f2074, before any fitting).

No model was fitted, no dev gate was run, and the virgin was not
read for yellows. Reason: there is no consistent yellows target in
dev under either source. The stats feed carries no `yellow_cards` /
`red_cards` key in any of the 1,717 payloads (0 matches with a stats
feed in 2021–2026). The event-feed fallback target is not consistent
across dev: plain Yellow Card events exist ONLY from 2023 onward
(2021–2022: 0 plain Yellows in 504 event matches; only Red 40/63
and YellowRed 44/63). A yellows target defined on the event feed
would have no dev window in 2021–2022 and a two-season window in
2023–2024 — a target-definition break, not a modelling window (the
NO-2Divisjon precedent). Referee data is absent in dev (named in
0/1,717 matches, every season), so no X8 referee arm exists. No
trait reliability is measurable on a consistent dev target, and no
1H share is computable on dev as a frozen constant. This is a
feasibility verdict recorded pre-fitting, not a gate FAIL. The frozen
split was not moved to manufacture a dev window. K-UY may be
pre-registered fresh once a dev cards target exists; it may not be
rescued inside this prereg.
