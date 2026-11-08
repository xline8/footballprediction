# Verdict — S-BY (BY-PremierLeague shots on target): **NOT-BUILDABLE**

Frozen decision: PREREG_S_BY.md (prereg commit 66cbfe4, branch
wip-by-premierleague, before any fitting).

No model was fitted, no dev gate was run, and the virgin was not
read for SOT. Reason: the SOT target exists in NO season at all. The
stats feed carries no `ShotsOnTarget` key in any of the 1,394
payloads (0 matches with a stats feed in 2021–2026; 0 in dev, 0 in
the virgin, 0 in the reserve), and the shotmap is empty in every
season (0 shots in 1,394 matches), so no shotmap-derived SOT target
exists either. There is no dev season, no warm-up season, and no
scored dev window at all before the virgin season (2025) itself. No
trait reliability is measurable on dev (split-half r null, n = 0
teams), and no 1H share is computable on dev (0 matches with
FirstHalf/SecondHalf splits in dev), so no line can be selected and
no halves constant frozen. This is a feasibility verdict recorded
pre-fitting, not a gate FAIL. The frozen split was not moved to
manufacture a dev window. S-BY may be pre-registered fresh once a
stats feed exists in dev; it may not be rescued inside this prereg.
