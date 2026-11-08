# Pre-registration — S/C/K/T-DZ: NOT BUILDABLE

Frozen: 2026-11-10, before any fitting. Branch `build/dz-ligue1`
(worktree `~/workspace/wt-dz-ligue1`; NOTE — 2026-11-10 15:42 WIB
the coordinator froze all git work repo-wide after a cleanup
command damaged git history, so this prereg is filed on disk
uncommitted; the coordinator will rebuild history and commit the
branch afterwards.)
Design authority: `league/DZ-Ligue1/analysis/MODEL_DESIGN.md`
(§1 feasibility matrix); features per `analysis/FEATURES.md` (§4).
This prereg records the NOT BUILDABLE verdicts with payload-level
evidence, so that no fitting, no virgin read, and no post-hoc arm can
follow from it for any of these four candidates.

**Committed before any fitting. No fitting is done under this prereg.**

## Evidence (payload-verified 2026-11-10, all 1,332 payloads read)

- **S-DZ (shots on target):** `ShotsOnTarget` exists in **0/1,332**
  payloads. `content.stats` is empty in 1,332/1,332; `content.shotmap`
  is empty in 1,332/1,332. No SOT target exists in any season, so no
  dev window and no virgin window exist.
- **C-DZ (corners):** `corners` exists in **0/1,332** payloads
  (same empty stats feed). No corners target exists in any season.
- **K-DZ (cards):** no yellow-card target exists anywhere.
  `yellow_cards` stats exist in 0/1,332 payloads. Card events number
  244 in total across 1,190 event-bearing matches — **all of them
  dismissals** (Red 184, YellowRed 60; **0 plain Yellow events**).
  The referee field is empty in 1,332/1,332 payloads (`infoBox.Referee`
  key present, `text` always `''`), so referee strictness (X8) is
  unmeasurable as well. Dismissals are not yellows and are not
  modelled as a substitute target.
- **T-DZ (total shots):** `total_shots` / shot counts exist in
  **0/1,332** payloads (same empty stats feed and shotmap). No total-
  shots target exists in any season.

Note on the index flags: `has_stats` and `has_shotmap` are `False`
for all 1,332 rows, and the payloads confirm that by content — this
league is the clean case, the opposite of the documented false
positives elsewhere in the program where the flags said True on
empty blocks. Coverage here was measured by content regardless.
(`header.teams` carries ids + scores in every payload; team identity
and scores come from the payload, cross-checked against the index —
see DATA_UNDERSTANDING.md §0.)

## Gate arithmetic (why no window exists)

- Dev = season-blocked walk-forward: the targets do not exist, so no
  team trait, no rating and no naive baseline can be computed for any
  candidate in any season. There is no dev n > 0.
- Virgin = season 2025/2026 (240 eligible matches): the targets do
  not exist there either (stats/shotmap empty in all 240 rows).
  Calibration SEs are undefined — there is nothing to calibrate.
- No pooled or proxy rescue: no season and no stage carries the
  targets, so no subset of the warehouse rescues any candidate.

## Registered decisions

- Arms: **none** (no candidate reaches design).
- Primary lines: **none chosen**.
- Virgin window (2025/2026): **NOT READ** for S/C/K/T —
  deliberately unread, not read-and-failed.
- Halves constants: **none** for SOT/corners/cards/total shots
  (no splits exist for targets that do not exist).

## Verdict

S-DZ, C-DZ, K-DZ and T-DZ are NOT BUILDABLE. The league's only
buildable candidate is G-DZ (goals). See
`league/DZ-Ligue1/reports/S_C_K_T_DZ_NOT_BUILDABLE.md`.
