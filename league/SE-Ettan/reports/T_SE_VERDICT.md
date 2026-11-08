# Verdict — T-SE (SE-Ettan total shots): **NOT-BUILDABLE**

Frozen decision: PREREG_T_SE.md (prereg commit
2fc8d51c13736643f6156b1c71abb11e21b7de08, before any fitting).

No model was fitted, no dev gate was run, and the virgin was not
read for total shots. Reason: the total-shots target exists in NO
season. The stats feed is 0% in 2021–2025 (0 matches with a stats
feed in any season; stats keys per season are empty in
`eda_summary.json`), and the shotmap is 0/2,880 matches. The stats
era never starts. There is no dev season, no warm-up season, and no
scored dev window at all. This is the FI total-shots case in its
strongest form: not a definition break within a dev window, but the
complete absence of a dev window.

Trait reliability is not measurable on dev (split-half r null, n = 0
teams — the target is absent in every dev season), and no 1H share
is computable on dev (0 matches with FirstHalf/SecondHalf splits in
any season), so no line can be selected and no halves constant
frozen. The X6 xGOT-per-shot and X9 keeper-saves / possession
covariates exist nowhere (no shotmap, no stats feed in any season),
so no covariate arm has a dev window either. This is a feasibility
verdict recorded pre-fitting, not a gate FAIL. The frozen split was
not moved to manufacture a dev window. T-SE may be pre-registered
fresh once dev-era stats seasons exist; it may not be rescued inside
this prereg.
