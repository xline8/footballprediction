# Pre-registration — S/C/K/T-NG: NOT BUILDABLE

Frozen: 2026-11-10, before any fitting. Branch `build/ng-professional-league`.
Design authority: `league/NG-ProfessionalLeague/analysis/MODEL_DESIGN.md`
(§1 feasibility matrix); features per `analysis/FEATURES.md` (§4).
This prereg records the NOT BUILDABLE verdicts with payload-level
evidence, so that no fitting, no virgin read, and no post-hoc arm can
follow from it for any of these four candidates.

**Committed before any fitting. No fitting is done under this prereg.**

## Evidence (payload-verified 2026-11-10, all 1,830 payloads read)

- **S-NG (shots on target):** `ShotsOnTarget` exists in **0/1,830**
  payloads. `content.stats` is empty in 1,830/1,830; `content.shotmap`
  is empty in 1,830/1,830. No SOT target exists in any season, so no
  dev window and no virgin window exist.
- **C-NG (corners):** `corners` exists in **0/1,830** payloads
  (same empty stats feed). No corners target exists in any season.
- **K-NG (cards):** no yellow-card target exists anywhere.
  `yellow_cards` stats exist in 0/1,830 payloads. Card events number
  155 in total across 1,659 event-bearing matches — **all of them
  dismissals** (YellowRed 50, Red 105; **0 plain Yellow events**).
  The referee field is empty in 1,830/1,830 payloads (`infoBox.Referee`
  key present, `text` always `''`), so referee strictness (X8) is
  unmeasurable as well. Dismissals are not yellows and are not
  modelled as a substitute target.
- **T-NG (total shots):** `total_shots` / shot counts exist in
  **0/1,830** payloads (same empty stats feed and shotmap). No total-
  shots target exists in any season.

Note on the index flags: `has_stats` and `has_shotmap` are `False`
for all 1,830 rows, and the payloads confirm that by content — this
league is the clean case, the opposite of the documented false
positives (TH2/DK-1/ID/BRC/EE/FNL/FI-YK) where the flags said True on
empty blocks. Coverage here was measured by content regardless.

## Gate arithmetic (why no window exists)

- Dev = season-blocked walk-forward: the targets do not exist, so no
  team trait, no rating and no naive baseline can be computed for any
  candidate in any season. There is no dev n > 0.
- Virgin = season 2025/2026 (379 eligible matches): the targets do
  not exist there either (stats/shotmap empty in all 379). Calibration
  SEs are undefined — there is nothing to calibrate.
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

S-NG, C-NG, K-NG, T-NG are **NOT BUILDABLE**. Report:
`league/NG-ProfessionalLeague/reports/S_C_K_T_NG_NOT_BUILDABLE.md`.
Production code untouched. No push. No merge.
