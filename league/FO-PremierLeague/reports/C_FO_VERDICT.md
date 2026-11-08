# C-FO Verdict — Faroe Islands Premier League corners model

Date: 2026-11-10. Branch `build/fo-premier-league`. Prereg:
`league/FO-PremierLeague/prereg/PREREG_C_FO.md` (commit 4c162d84,
frozen before any fitting).

## Verdict: NOT BUILDABLE

No corners data exists anywhere in the corpus: `content.stats`
present in 0/810 payloads, shotmap shots 0/810, no corner events
in the event feed, and no stats-feed proxy (possession, box
touches, big chances are all absent with the stats block). There is
no training target, no naive baseline, and no calibration object.
No engine was built, no fitting was done, the virgin window (2026)
was NOT read, and nothing ships.
