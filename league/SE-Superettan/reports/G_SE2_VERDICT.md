# Verdict — G-SE2 (SE-Superettan goals): **FAIL (dev gate)**

Frozen gates: PREREG_G_SE2.md (committed 730a5c1, before any fitting).

## Dev (season-blocked walk-forward, scored 2022–2025, pooled n = 960)

| Arm | 1X2 LL | RPS | OU2.5 LL |
|---|---|---|---|
| Gate Zero / SHRINK / X2 (identical) | 1.081471 | 0.228759 | 0.717879 |
| Climatology (baseline) | 1.073435 | 0.226069 | 0.693800 |

Gate Zero fails ALL THREE dev legs (1X2 LL, RPS, OU LL all worse than
climatology). Per season the model beats climatology on 1X2 only in 2024.
→ Candidate FAILS at the dev gate. **Virgin 2026 NOT read** (results_virgin.json
records `virgin_read: false`). Nothing ships.

## Why the three arms are numerically identical (stated plainly)
- SHRINK is mechanically inert under season-blocked fitting in this league:
  at each season's single fit, every team has either 0 prior in-league matches
  (new entrant — shrink factor 0, identical to Gate Zero's unseen rule) or ≥30
  (a full prior season). No team ever sits in the 1–5 match band the arm targets.
- X2 as implemented by Codex is additionally INVALID as a construction: its
  entrant test looks the team up in the parent (Allsvenskan) corpus for the
  SAME season it plays Superettan — an impossible overlap — so its completed-
  transitions list is always empty and the offset never fires (multipliers {}).
  The correct definition (previous season in the parent corpus) is the one
  measured in EDA F4. Under the frozen gate rule this defect is MOOT: Gate Zero
  failed dev, variants are moot, and no rescue arm may be invented in this
  prereg. A future prereg could test a corrected X2 against a fresh virgin.

Diagnosis (recorded, not acted on): a goals-only DC (no xG exists in this feed)
cannot beat climatology in this league — the same OU/1X2 pattern as most of the
program, here failing even on 1X2 LL and RPS.
