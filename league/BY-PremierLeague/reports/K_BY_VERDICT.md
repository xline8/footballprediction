# Verdict — K-BY (BY-PremierLeague cards / yellows): **NOT-BUILDABLE**

Frozen decision: PREREG_K_BY.md (prereg commit 66cbfe4, branch
wip-by-premierleague, before any fitting).

No model was fitted, no dev gate was run, and the virgin was not
read for yellows. Reason: no yellows target exists in ANY season at
all, under either source. The stats feed carries no `yellow_cards` /
`red_cards` key in any of the 1,394 payloads (0 matches with a stats
feed in 2021–2026). The event feed carries ZERO plain Yellow events
in every season (0 in dev, 0 in the virgin, 0 in the reserve; only
YellowRed + Red events exist — 92 YellowRed and 144 Red in dev).
This is stronger than a definition break across eras: there is no
yellows target to model in the first place. Referee data is absent
in dev (named in 0/1,394 matches, every season), so no X8 referee
arm exists. No trait reliability is measurable on a dev target, and
no 1H share is computable on dev as a frozen constant (the event
yellows that exist are YellowRed only and are NOT a frozen constant;
no K market). This is a feasibility verdict recorded pre-fitting,
not a gate FAIL. The frozen split was not moved to manufacture a dev
window. K-BY may be pre-registered fresh once a yellows target
exists in dev; it may not be rescued inside this prereg.
