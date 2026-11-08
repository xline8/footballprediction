# Verdict — K-FI (FI-Ykkonen cards): **NOT-BUILDABLE**

Frozen decision: PREREG_S_C_K_T_FI.md (prereg commit
e5874b8d62f005abf9a79e8ee2b5641069cf1f2a, branch wip-fi-ykkonen,
before any fitting).

No model was fitted, no dev gate was run, and the virgin was not
read for cards. Reason: no stats yellows in any season (stats feed
0/1,730), and the referee is named in 0/1,730 matches (no X8
referee arm). The event feed carries cards, but the plain-Yellow
target does not exist: 0 plain Yellow events in the whole corpus
(only YellowRed + Red events; event yellows per match 0.073–0.159
in dev). A cards target built on event yellows would be a
YellowRed/Red count, not the yellow-cards market, and the
plain-Yellow definition the market uses is absent everywhere. This
is a feasibility verdict recorded pre-fitting, not a gate FAIL. The
frozen split was not moved to manufacture a dev window. K-FI may be
pre-registered fresh once a consistent yellows target exists; it may
not be rescued inside this prereg.
