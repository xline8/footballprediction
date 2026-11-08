# Verdict — K-SG (SG-PremierLeague cards): **NOT-BUILDABLE**

Frozen decision: PREREG_K_SG.md (prereg commit 9b5d46b, branch
wip-sg-premierleague, before any fitting).

No model was fitted, no dev gate was run, and the virgin was
not read for cards. Reason: no yellows target exists in ANY
season at all. The stats feed carries no `yellow_cards` /
`red_cards` key in any of the 555 payloads (0 matches with a
stats feed in 2021–2026/2027), and the event feed carries ZERO
plain Yellow events in every season (0 in dev, 0 in the
virgin, 0 in the reserve; only YellowRed + Red events exist —
YellowRed totals 8 / 5 / 13 / 6 / 1 / 3, Red totals 11 / 14 /
35 / 31 / 26 / 10). This is stronger than a definition break
across eras: there is no yellows target to model in the first
place. Referee coverage is 0% in every dev season (and in the
virgin), so no X8 referee arm exists either. No trait
reliability is measurable on dev (split-half r null, n = 0
teams), and no 1H share is computable on dev (the event
yellows that exist are YellowRed only — 32 in the dev era —
and are NOT a frozen constant; no K market), so no line can
be selected and no halves constant frozen. This is a
feasibility verdict recorded pre-fitting, not a gate FAIL.
The frozen split was not moved to manufacture a dev window.
K-SG may be pre-registered fresh once a yellows target exists;
it may not be rescued inside this prereg.
