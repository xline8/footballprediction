# Pre-registration — S/C/K/T-SV: NOT BUILDABLE

Frozen: 2026-11-10, before any fitting. Branch `build/sv-primera-division`.
Design authority: `league/SV-PrimeraDivision/analysis/MODEL_DESIGN.md`
(§1 feasibility matrix); features per `analysis/FEATURES.md` (§4).
This prereg records the NOT BUILDABLE verdicts with payload-level
evidence, so that no fitting, no virgin read, and no post-hoc arm can
follow from it for any of these four candidates.

**Committed before any fitting. No fitting is done under this prereg.**

## Evidence (payload-verified 2026-11-10, all 1,448 payloads read)

- **S-SV (shots on target):** `ShotsOnTarget` exists in **0/1,448**
  payloads. `content.stats` is empty in 1,448/1,448; `content.shotmap`
  is empty in 1,448/1,448. No SOT target exists in any tournament, so no
  dev window and no virgin window exist.
- **C-SV (corners):** `corners` exists in **0/1,448** payloads
  (same empty stats feed). No corners target exists in any tournament.
- **K-SV (cards):** no yellow-card target exists anywhere.
  `yellow_cards` stats exist in 0/1,448 payloads. Card events number
  593 in total across 1,334 event-bearing matches — **all of them
  dismissals** (Red 449, YellowRed 144; **0 plain Yellow events**).
  The referee field is empty in 1,448/1,448 payloads (`infoBox.Referee`
  key present, `text` always `''`), so referee strictness (X8) is
  unmeasurable as well. Dismissals are not yellows and are not
  modelled as a substitute target.
- **T-SV (total shots):** `total_shots` / shot counts exist in
  **0/1,448** payloads (same empty stats feed and shotmap). No total-
  shots target exists in any tournament.

Note on the index flags: `has_stats` and `has_shotmap` are `False`
for all 1,448 rows, and the payloads confirm that by content — this
league is the clean case, the opposite of the documented false
positives (TH2/DK-1/ID/BRC/EE/FNL/FI-YK) where the flags said True on
empty blocks. Coverage here was measured by content regardless.
(`header.teams` carries ids + scores in every payload; team identity
and scores come from the payload, cross-checked against the index —
see DATA_UNDERSTANDING.md §0.)

## Gate arithmetic (why no window exists)

- Dev = tournament-blocked walk-forward: the targets do not exist, so no
  team trait, no rating and no naive baseline can be computed for any
  candidate in any tournament. There is no dev n > 0.
- Virgin = tournaments 2025/2026 - Apertura and 2025/2026 - Clausura
  (264 eligible regular-phase matches): the targets do not exist there
  either (stats/shotmap empty in all 290 rows). Calibration
  SEs are undefined — there is nothing to calibrate.
- No pooled or proxy rescue: no tournament and no stage carries the
  targets, so no subset of the warehouse rescues any candidate.

## Registered decisions

- Arms: **none** (no candidate reaches design).
- Primary lines: **none chosen**.
- Virgin window (2025/2026 Apertura + Clausura): **NOT READ** for S/C/K/T —
  deliberately unread, not read-and-failed.
- Halves constants: **none** for SOT/corners/cards/total shots
  (no splits exist for targets that do not exist).

## Verdict

S-SV, C-SV, K-SV and T-SV are NOT BUILDABLE. The league's only
buildable candidate is G-SV (goals). See
`league/SV-PrimeraDivision/reports/S_C_K_T_SV_NOT_BUILDABLE.md`.
