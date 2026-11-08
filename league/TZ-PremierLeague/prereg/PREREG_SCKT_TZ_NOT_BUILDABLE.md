# Pre-registration — S/C/K/T-TZ: NOT BUILDABLE

Frozen: 2026-11-10, before any fitting. Branch `build/tz-premier-league`.
Design authority: `league/TZ-PremierLeague/analysis/MODEL_DESIGN.md`
(§1 feasibility matrix); features per `league/TZ-PremierLeague/analysis/FEATURES.md`.
This prereg records the NOT BUILDABLE verdicts with payload-level evidence,
so that no fitting, no virgin read, and no post-hoc arm can follow from it
for any of these four candidates.

**Committed before any fitting. No fitting is done under this prereg.**

## Evidence (payload-verified 2026-11-10, all 1,284 payloads read)

- **S-TZ (shots on target):** `ShotsOnTarget` exists in **0/1,284**
  payloads. `content.stats` is null in 1,284/1,284; `content.shotmap.shots`
  is empty in 1,284/1,284. No SOT target exists in any season.
- **C-TZ (corners):** `corners` exists in **0/1,284** payloads (same empty
  stats feed). No corners target exists in any season.
- **K-TZ (cards):** no yellow-card target exists anywhere.
  `yellow_cards` stats exist in 0/1,284 payloads. Card events number 114
  in total — **all of them dismissals** (Red 99, YellowRed 15; **0 plain
  Yellow events**). The referee field is empty in 1,284/1,284 payloads
  (`infoBox.Referee` text always `''`), so referee strictness (X8) is
  unmeasurable as well. Dismissals are not yellows and are not modelled as
  a substitute target.
- **T-TZ (total shots):** `total_shots` / shot counts exist in **0/1,284**
  payloads (same empty stats feed and shotmap). No total-shots target exists
  in any season.

Note on the index flags: `has_stats` and `has_shotmap` are `False` for all
1,284 rows, and the payloads confirm that by content — the clean case
(opposite of the documented false positives). Coverage was measured by
content regardless. (`general`/`header` are present in TZ payloads, unlike
GH — team identity and scores cross-checked against the index; see
`DATA_UNDERSTANDING.md` §0.)

## Gate arithmetic (why no window exists)

- Dev = season-blocked walk-forward: there is no dev n > 0 for any of the
  four candidates because the targets do not exist. No team trait, rating or
  naive baseline can be computed for any candidate.
- Virgin = season 2025/2026 (239 eligible matches): the targets do not exist
  there either. Calibration SEs are undefined — there is nothing to
  calibrate.
- No pooled or proxy rescue: no season and no stage carries the targets, so
  no subset of the warehouse rescues any candidate.

## Registered decisions

- Arms: **none** (no candidate reaches design).
- Primary lines: **none chosen**.
- Virgin window (2025/2026): **NOT READ** for S/C/K/T — deliberately unread,
  not read-and-failed.
- Halves constants: **none** for SOT/corners/cards/total shots (no splits
  exist for targets that do not exist).

## Verdict

S-TZ, C-TZ, K-TZ, T-TZ are **NOT BUILDABLE**. Report:
`league/TZ-PremierLeague/reports/S_C_K_T_TZ_NOT_BUILDABLE.md`.
Production code untouched. No push. No merge.
