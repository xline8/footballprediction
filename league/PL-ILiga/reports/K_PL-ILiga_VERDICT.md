# Verdict — K-PL-ILiga (Poland I Liga cards)

**NOT BUILDABLE. No fitting was performed; the virgin was not read.**

Era evidence (coordinator-verified from the warehouse index and a full
1,671-file payload scan; see analysis/DATA_UNDERSTANDING.md): there is
no yellow-card source anywhere in this league's warehouse data.
`content.stats` is None in all 1,671 payloads (0/1,671), so the stats
`yellow_cards` feed does not exist; and the events feed records NO plain
Yellow cards — its 358 Card events are only Red (202) and YellowRed
(156). The production cards design targets unified yellows, which cannot
be constructed from either source. Dismissals alone (Red + YellowRed)
are a rare-event count (0.21 per match) and are rejected as a target
per the J1 template R12.

A candidate needs a scorable dev window AND a virgin window containing
the target; here the target exists nowhere, so the candidate is recorded
NOT BUILDABLE rather than forced. Halves: no cards halves source exists —
frozen FT-only (no cards constant in config.yaml). Descriptive only: the
Red/YellowRed event counts are retained in the analysis CSV, with the
2025/2026 reclassification quirk noted (YellowRed collapses to 1 while
Red jumps to 49, so even the Red/YellowRed split is not comparable
across the 2025 boundary).

A future preregistration becomes possible only if FotMob starts
publishing stats coverage (with yellow_cards) or Yellow events for this
league and a second complete covered season then exists.
