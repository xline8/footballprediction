# Verdict — S/C/K/T-TZ: NOT BUILDABLE

Prereg `league/TZ-PremierLeague/prereg/PREREG_SCKT_TZ_NOT_BUILDABLE.md`
(commit `de16ef20`) precedes any fitting. Branch
`build/tz-premier-league`. No engine, no results, no predictions
exist for any of these four candidates — there is nothing to fit.

## Evidence (payload-verified 2026-11-10, all 1,284 payloads read)

- **S-TZ (shots on target):** `ShotsOnTarget` exists in **0/1,284**
  payloads. `content.stats` is null in 1,284/1,284;
  `content.shotmap.shots` is an empty list in 1,284/1,284. No SOT
  target exists in any season.
- **C-TZ (corners):** `corners` exists in **0/1,284** payloads
  (same empty stats feed). No corners target exists in any season.
- **K-TZ (cards):** no yellow-card target exists anywhere.
  `yellow_cards` stats exist in 0/1,284 payloads. Card events
  number 114 in total across 1,147 event-bearing matches — **all of
  them dismissals** (Red 99, YellowRed 15; **0 plain Yellow
  events**). The referee field is empty in 1,284/1,284 payloads
  (`infoBox.Referee` text always `''`), so referee strictness (X8)
  is unmeasurable as well. Dismissals are not yellows and are not
  modelled as a substitute target.
- **T-TZ (total shots):** `total_shots` / shot counts exist in
  **0/1,284** payloads (same empty stats feed and shotmap). No
  total-shots target exists in any season.

Note on the index flags: `has_stats` and `has_shotmap` are `False`
for all 1,284 rows, and the payloads confirm that by content — this
league is the clean case, the opposite of the documented false
positives (TH2/DK-1/ID/BRC/EE/FNL/FI-YK) where the flags said True
on empty blocks. Coverage here was measured by content regardless.
(`general`/`header` are present in TZ payloads, unlike GH; team
identity and scores were cross-checked against the index — see
DATA_UNDERSTANDING.md §0. The 10 lineup blocks that exist carry zero
starters, so no lineup data exists in usable form either.)

## Gate arithmetic (why no window exists)

- Dev = season-blocked walk-forward: the targets do not exist, so no
  team trait, no rating and no naive baseline can be computed for any
  candidate in any season. There is no dev n > 0.
- Virgin = season 2025/2026 (239 eligible matches): the targets do
  not exist there either (stats/shotmap empty in all 240 rows).
  Calibration SEs are undefined — there is nothing to calibrate.
- No pooled or proxy rescue: no season and no stage carries the
  targets, so no subset of the warehouse rescues any candidate.

## Verdict

S-TZ, C-TZ, K-TZ, T-TZ are **NOT BUILDABLE**. The virgin window
(2025/2026) was **NOT READ** for S/C/K/T — deliberately unread, not
read-and-failed. No halves constants exist for these markets.
Production code untouched. No push. No merge.
