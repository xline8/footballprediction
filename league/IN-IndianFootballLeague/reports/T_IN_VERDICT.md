# Verdict — T-IN (IN-IndianFootballLeague total shots): **NOT-BUILDABLE**

Frozen decision: PREREG_T_IN.md (prereg commit 83d1b1f, branch
wip-in-indianfootballleague, before any fitting).

No model was fitted, no dev gate was run, and the virgin was not
read for total shots. Reason: the total-shots target exists in NO
season at all. The stats feed carries no `total_shots` key in any
of the 608 payloads (0 matches with a stats feed in
2021/2022–2026/2027; 0 in dev, 0 in the virgin, 0 in the reserve),
and the shotmap is empty in every season (0 shots in 608 matches),
so no shotmap-derived total-shots target exists either. There is
no dev season, no warm-up season, and no scored dev window at all
before the virgin season (2025/2026) itself. No trait reliability
is measurable on dev (split-half r null, n = 0 teams), and no 1H
share is computable on dev (0 matches with FirstHalf/SecondHalf
splits in dev), so no line can be selected and no halves constant
frozen. This is a feasibility verdict recorded pre-fitting, not a
gate FAIL. The frozen split was not moved to manufacture a dev
window. T-IN may be pre-registered fresh once a stats feed exists
in dev; it may not be rescued inside this prereg.
