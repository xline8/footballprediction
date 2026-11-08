# Verdict — C-KW (KW-PremierLeague corners): **NOT-BUILDABLE**

Frozen decision: PREREG_C_KW.md (prereg commit c8988cf, branch
wip-kw-premierleague, before any fitting).

No model was fitted, no dev gate was run, and the virgin was not
read for corners. Reason: no corners target exists in ANY season.
The stats feed is absent in all 711 payloads (0 matches carry a
`Periods` block in 2021–2026/2027) and there is no other corners
source in the corpus; the X7 input (`touches_opp_box`) is likewise
absent everywhere. No trait reliability is measurable on a dev
target and no 1H share is computable (no period splits anywhere).
This is a feasibility verdict recorded pre-fitting, not a gate
FAIL. The frozen split was not moved to manufacture a dev window.
C-KW may be pre-registered fresh once a stats feed exists in dev;
it may not be rescued inside this prereg.
