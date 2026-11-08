# Report — S/C/K/T-NG: NOT BUILDABLE

Prereg `league/NG-ProfessionalLeague/prereg/PREREG_SCKT_NG_NOT_BUILDABLE.md`
(commit `f45177d7`, before any fitting). Branch
`build/ng-professional-league`.

## Evidence (payload-verified 2026-11-10, all 1,830 payloads read by content)

- **S-NG (shots on target):** `ShotsOnTarget` exists in **0/1,830**
  payloads. `content.stats` is empty in 1,830/1,830; `content.shotmap`
  is empty in 1,830/1,830. No SOT target exists in any season.
- **C-NG (corners):** `corners` exists in **0/1,830** payloads
  (same empty stats feed). No corners target exists in any season.
- **K-NG (cards):** no yellow-card target exists anywhere.
  `yellow_cards` stats exist in 0/1,830 payloads. Card events number
  155 in total across 1,659 event-bearing matches — **all of them
  dismissals** (YellowRed 50, Red 105; **0 plain Yellow events**).
  The referee field is empty in 1,830/1,830 payloads
  (`infoBox.Referee` key present, `text` always `''`), so referee
  strictness (X8) is unmeasurable as well. Dismissals are not
  yellows and are not modelled as a substitute target.
- **T-NG (total shots):** `total_shots` / shot counts exist in
  **0/1,830** payloads (same empty stats feed and shotmap). No total-
  shots target exists in any season.

Note on the index flags: `has_stats` and `has_shotmap` are `False`
for all 1,830 rows, and the payloads confirm that by content — this
league is the clean case, the opposite of the documented false
positives (TH2/DK-1/ID/BRC/EE/FNL/FI-YK) where the flags said True on
empty blocks. Coverage here was measured by content regardless, and
the data builder's coverage columns agree (all zero; the single
`has_lineup=1` row, 4635917, is a simple starters block, not a target).

## Consequence

No dev window and no virgin window exist for any of S/C/K/T. No
fitting was done, no virgin read was made for these candidates, and
no halves constant exists for them. The 2025/2026 virgin window is
unread for S/C/K/T — deliberately unread, not read-and-failed.

## Verdict

S-NG, C-NG, K-NG, T-NG are **NOT BUILDABLE**. League completion state:
**complete** — G-NG failed its dev gate (see `G_NG_VERDICT.md`) and
S/C/K/T are not buildable; 0 of 5 candidates pass, 1 fail, 4 not
buildable. Nothing ships.
