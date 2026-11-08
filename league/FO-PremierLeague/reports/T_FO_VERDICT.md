# T-FO Verdict — Faroe Islands Premier League total-shots model

Date: 2026-11-10. Branch `build/fo-premier-league`. Prereg:
`league/FO-PremierLeague/prereg/PREREG_T_FO.md` (commit 4c162d84,
frozen before any fitting).

## Verdict: NOT BUILDABLE

No total-shots data exists anywhere in the corpus: `content.stats`
present in 0/810 payloads, shotmap shots 0/810, no shot events in
the event feed. The shots family (v1/v2, challenger E9) has no
training target, no naive baseline, and no calibration object
here; goals are not substituted as a proxy. No engine was built, no
fitting was done, the virgin window (2026) was NOT read, and
nothing ships.
