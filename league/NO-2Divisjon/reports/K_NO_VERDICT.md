# Verdict — K-NO (NO-2Divisjon cards / yellows): **NOT-BUILDABLE**

Frozen decision: PREREG_K_NO.md (prereg commit 2901fa0, branch
wip-no-2divisjon, before any fitting).

No model was fitted, no dev gate was run, and the virgin was not
read for yellows. Reason: the yellows target exists in NO season
under either source across the dev era. The stats feed carries no
`yellow_cards` / `red_cards` key in any of the 2,158 payloads (0
matches with a stats feed in 2021–2026). The event-feed fallback
target is not consistent across dev: plain Yellow Card events exist
ONLY from 2024 onward (2021–2023: 0 plain Yellows in 1,034 event
matches; only Red 35/25/22 and YellowRed 24/15/13). A yellows target
defined on the event feed would have no dev window in 2021–2023 and
a one-season target in 2024 — a target-definition break, not a
modelling window. Referee data is absent in dev (named in 0/2,158
matches, every season), so no X8 referee arm exists. No trait
reliability is measurable on a consistent dev target, and no 1H
share is computable on dev as a frozen constant. This is a
feasibility verdict recorded pre-fitting, not a gate FAIL. The frozen
split was not moved to manufacture a dev window. K-NO may be
pre-registered fresh once a consistent yellows feed exists in dev;
it may not be rescued inside this prereg.
