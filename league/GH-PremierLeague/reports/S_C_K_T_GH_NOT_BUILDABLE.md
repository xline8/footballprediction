# Verdict — S/C/K/T-GH: NOT BUILDABLE

Prereg `league/GH-PremierLeague/prereg/PREREG_SCKT_GH_NOT_BUILDABLE.md`
(commit `577fae30`) precedes any fitting. Branch
`build/gh-premier-league`. No engine, no results, no predictions
exist for any of these four candidates — there is nothing to fit.

## Evidence (payload-verified 2026-11-10, all 1,619 payloads read)

- **S-GH (shots on target):** `ShotsOnTarget` exists in **0/1,619**
  payloads. `content.stats` is empty in 1,619/1,619;
  `content.shotmap` is empty in 1,619/1,619. No SOT target exists
  in any season.
- **C-GH (corners):** `corners` exists in **0/1,619** payloads
  (same empty stats feed). No corners target exists in any season.
- **K-GH (cards):** no yellow-card target exists anywhere.
  `yellow_cards` stats exist in 0/1,619 payloads. Card events
  number 177 in total across 1,412 event-bearing matches — **all of
  them dismissals** (YellowRed 68, Red 109; **0 plain Yellow
  events**). The referee field is empty in 1,619/1,619 payloads
  (`infoBox.Referee` key present, `text` always `''`), so referee
  strictness (X8) is unmeasurable as well. Dismissals are not
  yellows and are not modelled as a substitute target.
- **T-GH (total shots):** `total_shots` / shot counts exist in
  **0/1,619** payloads (same empty stats feed and shotmap). No
  total-shots target exists in any season.

Note on the index flags: `has_stats` and `has_shotmap` are `False`
for all 1,619 rows, and the payloads confirm that by content — this
league is the clean case, the opposite of the documented false
positives (TH2/DK-1/ID/BRC/EE/FNL/FI-YK) where the flags said True
on empty blocks. Coverage here was measured by content regardless.
(`general`/`header` are null in every payload; team identity and
scores come from the index.)

## Gate arithmetic (why no window exists)

- Dev = season-blocked walk-forward: the targets do not exist, so no
  team trait, no rating and no naive baseline can be computed for any
  candidate in any season. There is no dev n > 0.
- Virgin = season 2025/2026 (299 eligible matches): the targets do
  not exist there either (stats/shotmap empty in all 306 rows).
  Calibration SEs are undefined — there is nothing to calibrate.
- No pooled or proxy rescue: no season and no stage carries the
  targets, so no subset of the warehouse rescues any candidate.

## Verdict

S-GH, C-GH, K-GH, T-GH are **NOT BUILDABLE**. The virgin window
(2025/2026) was **NOT READ** for S/C/K/T — deliberately unread, not
read-and-failed. No halves constants exist for these markets.
Production code untouched. No push. No merge.
