# Verdict — K-KW (KW-PremierLeague cards / yellows): **NOT-BUILDABLE**

Frozen decision: PREREG_K_KW.md (prereg commit c8988cf, branch
wip-kw-premierleague, before any fitting).

No model was fitted, no dev gate was run, and the virgin was not
read for yellows. Reason: no yellows target exists in ANY season at
all, under either source. The stats feed carries no `yellow_cards`
key in any of the 711 payloads (0 matches with a stats feed
anywhere). The event feed carries ZERO plain Yellow events and
ZERO YellowRed events in every season (0 in dev, 0 in the virgin,
0 in the reserve); it records only straight Red cards (53 in the
whole corpus, ≈0.21–0.25 per event match). This is stronger than a
definition break across eras: there is no yellows target to model
in the first place (CN is the only equally strong case in the
programme). Referee data is absent (named in 0/711 matches, every
season), so no X8 referee arm exists. No trait reliability is
measurable on a dev target, and no 1H share is computable on dev
as a frozen constant (no yellows events exist; the event feed
itself exists in dev only in 2024/2025). This is a feasibility
verdict recorded pre-fitting, not a gate FAIL. The frozen split
was not moved to manufacture a dev window. K-KW may be
pre-registered fresh once a yellows target exists in dev; it may
not be rescued inside this prereg.
