# Verdict — K-IN (IN-IndianFootballLeague cards / yellows): **NOT-BUILDABLE**

Frozen decision: PREREG_K_IN.md (prereg commit 83d1b1f, branch
wip-in-indianfootballleague, before any fitting).

No model was fitted, no dev gate was run, and the virgin was not
read for yellows. Reason: no consistent yellows target exists in
dev under either source. The stats feed carries no `yellow_cards`
key in any of the 608 payloads (0 matches with a stats feed in
2021/2022–2026/2027). The event feed carries ZERO plain Yellow
events in every dev season AND in the virgin (2021/2022–2025/2026:
YellowRed + Red only — YellowRed totals 12 / 13 / 16 / 7 / 0, Red
totals 24 / 24 / 27 / 31 / 15); plain Yellow events exist ONLY in
the untouched reserve (27 in 2026/2027), a target-definition break
entirely outside the modelled eras. Event-derived "yellows" in
dev are YellowRed counts averaging 0.06–0.11 per match — not a
cards target. Referee data, unusually, IS present in dev (named
in 453/496 matches, 91.3%), so the X8 input exists — but referee
coverage collapses in the virgin (4/66, 6.1%), so no referee arm
could be virgin-evaluated or shipped, and with no yellows target
there is nothing for it to predict in any case. No trait
reliability is measurable on a dev target, and no 1H share is
computable on dev as a frozen constant (the event yellows that
exist are YellowRed only and are NOT a frozen constant; no K
market). This is a feasibility verdict recorded pre-fitting, not
a gate FAIL. The frozen split was not moved to manufacture a dev
window. K-IN may be pre-registered fresh once a consistent
yellows target exists in dev; it may not be rescued inside this
prereg.
