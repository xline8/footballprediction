# Verdict — C-UY (UY-LigaAUF corners): **NOT-BUILDABLE**

Frozen decision: PREREG_C_UY.md (prereg commit
7d43257df3460bcfa1bf07c8c94d2ff4466f2074, before any fitting).

No model was fitted, no dev gate was run, and the virgin was not
read for corners. Reason: the corners target exists in NO season
under any source. The stats feed is absent in every season (0/1,717
matches with `content.stats.Periods`, 0 stats keys in any raw JSON,
0 period splits in 2021–2026). There is no `corners` key anywhere
and no event-derived corners substitute (no corner events in the
event feed). No trait reliability is measurable on dev (split-half r
null, n = 0 teams), no 1H share is computable on dev, and no line
can be selected. The X7 box-touches/territory multiplier has no
input either (`touches_opp_box` absent in every season). This is a
feasibility verdict recorded pre-fitting, not a gate FAIL. The frozen
split was not moved to manufacture a dev window. C-UY may be
pre-registered fresh once a dev corners target exists; it may not be
rescued inside this prereg.
