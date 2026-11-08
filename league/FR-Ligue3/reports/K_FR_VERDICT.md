# Verdict — K-FR (FR-Ligue3 cards / yellows): **NOT-BUILDABLE**

Frozen decision: PREREG_K_FR.md (prereg commit ef482d7, branch
wip-fr-ligue3, before any fitting).

No model was fitted, no dev gate was run, and the virgin was not
read for yellows. Reason: the yellows target exists in NO season
under either source across the dev era. The stats feed carries no
`yellow_cards` / `red_cards` key in any of the 1,570 payloads (0
matches with a stats feed in 2021/2022–2026/2027). The event-feed fallback
target is not consistent across dev: plain Yellow Card events exist
ONLY from 2023/2024 onward (2021/2022–2022/2023: 0 plain Yellows in 574 event
matches; only plain Red 74/62 and YellowRed 22/31). A yellows target
defined on the event feed would have no dev window in 2021/2022–2022/2023 and
a two-season target from 2023/2024 — a target-definition break, not a
modelling window. Referee data is absent in dev (named in 0/1,570
matches, every season), so no X8 referee arm exists. No trait
reliability is measurable on a consistent dev target, and no 1H
share is computable on dev as a frozen constant. This is a
feasibility verdict recorded pre-fitting, not a gate FAIL. The frozen
split was not moved to manufacture a dev window. K-FR may be
pre-registered fresh once a consistent yellows feed exists in dev;
it may not be rescued inside this prereg.
