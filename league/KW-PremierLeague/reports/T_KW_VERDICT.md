# Verdict — T-KW (KW-PremierLeague total shots): **NOT-BUILDABLE**

Frozen decision: PREREG_T_KW.md (prereg commit c8988cf, branch
wip-kw-premierleague, before any fitting).

No model was fitted, no dev gate was run, and the virgin was not
read for total shots. Reason: no total-shots target exists in ANY
season. The stats feed is absent in all 711 payloads (0 matches
carry a `Periods` block in 2021–2026/2027) and the shotmap is
empty in all 711, so no shotmap-derived total exists either. No
trait reliability is measurable on a dev target and no 1H share
is computable (no period splits, no shotmap periods). This is a
feasibility verdict recorded pre-fitting, not a gate FAIL. The
frozen split was not moved to manufacture a dev window. T-KW may
be pre-registered fresh once a stats feed exists in dev; it may
not be rescued inside this prereg.
