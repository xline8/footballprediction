# Verdict — S-KR3 (KR-KLeague3 shots on target): **NOT-BUILDABLE**

Frozen decision: PREREG_S_C_K_T_KR3.md (prereg commit 6d1a75fb, branch
build/kr-k-league3, before any fitting).

No model was fitted, no dev gate was run, and the virgin was not
read for shots on target. Reason: the SOT target exists in NO season
at all — 0 of 1,296 payloads carry a stats feed (0 in dev, 0 in the
virgin, 0 in the reserve), and the shotmap is empty in all 1,296
payloads. There is no dev season, no warm-up season, and no scored
dev window at all before the virgin season itself, so no trait
reliability is measurable on dev (split-half r null, n = 0 teams),
no 1H share is computable on dev (0 matches with period splits), and
no SOT line can be scored. Nothing ships.
