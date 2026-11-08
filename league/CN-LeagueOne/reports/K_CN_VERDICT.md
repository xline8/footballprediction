# Verdict — K-CN (CN-LeagueOne cards / yellows): **NOT-BUILDABLE**

Frozen decision: PREREG_S_C_K_T_CN.md (prereg commit 05c5870, branch
wip-cn-leagueone, before any fitting).

No model was fitted, no dev gate was run, and the virgin was not
read for yellows. Reason: the yellows target exists in NO season
under either source. The stats feed carries no `yellow_cards` /
`red_cards` key in any of the 1,572 payloads (0 matches with a stats
feed in 2021–2026). The event feed is worse than the NO precedent:
plain Yellow Card events exist in NO season at all — **0 plain
Yellows in 1,572 matches** (only YellowRed 5/21/25/14 and Red
55/51/46/41 in dev). A yellows target defined on the event feed
would be a YellowRed/Red count, not the yellow-cards market, and
the plain-Yellow definition the market uses is absent everywhere —
not a target-definition break across eras, but a target that never
exists. Referee data is absent in dev (named in 0/1,572 matches,
every season), so no X8 referee arm exists. No trait reliability is
measurable on a consistent dev target, and no 1H share is
computable on dev as a frozen constant. This is a feasibility
verdict recorded pre-fitting, not a gate FAIL — and the strongest K
not-buildable case in the program so far. The frozen split was not
moved to manufacture a dev window. K-CN may be pre-registered fresh
once a consistent yellows feed exists in dev; it may not be rescued
inside this prereg.
