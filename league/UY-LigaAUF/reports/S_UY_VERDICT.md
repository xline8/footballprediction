# Verdict — S-UY (UY-LigaAUF shots on target): **NOT-BUILDABLE**

Frozen decision: PREREG_S_UY.md (prereg commit
7d43257df3460bcfa1bf07c8c94d2ff4466f2074, before any fitting).

No model was fitted, no dev gate was run, and the virgin was not
read for shots on target. Reason: the SOT target exists in NO season
under any source. The stats feed is absent in every season (0/1,717
matches with `content.stats.Periods`, 0 stats keys in any raw JSON,
0 period splits in 2021–2026). There is no `ShotsOnTarget` key
anywhere, no shotmap anywhere, and no event-derived SOT substitute.
No trait reliability is measurable on dev (split-half r null,
n = 0 teams), no 1H share is computable on dev, and no line can be
selected. This is a feasibility verdict recorded pre-fitting, not a
gate FAIL. The frozen split was not moved to manufacture a dev window.
S-UY may be pre-registered fresh once a dev SOT target exists; it may
not be rescued inside this prereg.
