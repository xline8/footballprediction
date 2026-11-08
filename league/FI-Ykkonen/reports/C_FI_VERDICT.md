# Verdict — C-FI (FI-Ykkonen corners): **NOT-BUILDABLE**

Frozen decision: PREREG_S_C_K_T_FI.md (prereg commit
e5874b8d62f005abf9a79e8ee2b5641069cf1f2a, branch wip-fi-ykkonen,
before any fitting).

No model was fitted, no dev gate was run, and the virgin was not
read for corners. Reason: the corners target exists in NO season at
all — 0 matches with a stats feed in 2021–2026 (0 in dev, 0 in the
virgin, 0 in the reserve). There is no dev season, no warm-up
season, and no scored dev window at all, so no trait reliability is
measurable on dev (split-half r null, n = 0 teams), no 1H share is
computable on dev (0 matches with period splits in dev), and no line
can be selected. The X7 opp-box-touches covariate is likewise absent
in dev, so no touches variant has a dev window either. This is a
feasibility verdict recorded pre-fitting, not a gate FAIL. The frozen
split was not moved to manufacture a dev window. C-FI may be
pre-registered fresh once dev-era stats seasons exist; it may not be
rescued inside this prereg.
