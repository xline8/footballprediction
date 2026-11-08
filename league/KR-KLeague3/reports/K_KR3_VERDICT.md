# Verdict — K-KR3 (KR-KLeague3 cards / yellows): **NOT-BUILDABLE**

Frozen decision: PREREG_S_C_K_T_KR3.md (prereg commit 6d1a75fb, branch
build/kr-k-league3, before any fitting).

No model was fitted, no dev gate was run, and the virgin was not
read for yellows. Reason: the yellows target exists in NO season
under either source. The stats feed carries no `yellow_cards` /
`red_cards` key in any of the 1,296 payloads (0 matches with a stats
feed in 2021–2026). The event feed is worse than the K2 precedent:
plain Yellow card events exist in NO season at all — **0 plain
Yellows in 1,296 matches** (only YellowRed 57 and Red 84 events in
the whole corpus, 141 red-card events in 1,288 played matches,
~0.11/match — far too rare for a 2.5 line, and a red-card count is
not a yellows market). An event-unified yellow target is therefore
impossible. Nothing ships.
