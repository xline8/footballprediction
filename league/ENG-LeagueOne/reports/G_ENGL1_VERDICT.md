# Verdict — G-ENGL1 (ENG-LeagueOne goals)

**FAIL at the dev gate. Virgin 2025/2026 deliberately NOT read.
Nothing ships.**

Calibration convention (where applicable): actual − predicted.

## Dev gate (walk-forward 2022/2023–2024/2025, pooled n=1,671)

| Arm | 1X2 LL | RPS | OU2.5 LL | vs climatology |
|---|---|---|---|---|
| Gate Zero | 1.0578 | 0.2249 | 0.7048 | LL ✓ / RPS ✓ / OU ✗ |
| SHRINK | 1.0578 | 0.2249 | 0.7048 | identical to Gate Zero |
| X2 | 1.0557 | 0.2240 | 0.7044 | LL ✓ / RPS ✓ / OU ✗ |
| climatology | 1.0746 | 0.2323 | 0.6931 | — |

Gate (frozen): pooled dev 1X2 LL AND RPS must beat climatology AND
OU2.5 LL must beat the base-rate baseline. Every arm wins the two
1X2 legs and loses the OU leg by ~+0.011 LL — the DC's goal-total
distribution is too dispersed for this league's OU market even
though its outcome probabilities are the best on the table. X2 is
the best arm on all three metrics and still fails. FAIL is
mechanical; no rescue arm exists in the prereg.

Notes:
- SHRINK is degenerate under the season-blocked design (as in DK):
  a team's prior in-league match count at a season fit is 0 or a
  full season's worth, never 1–5, so the arm is bit-identical to
  Gate Zero. Recorded, not a defect.
- The coordinator recomputed the pooled climatology from the CSV
  by a second path: 1.074618 / 0.232339 / 0.693108 — exact match
  with the harness.
- Virgin NOT read (`engine/goals/results_virgin.json` carries the
  `virgin_read: false` stub written by the run script's own gate
  check). 2025/2026 remains available only under a new prereg;
  2026/2027 confirmatory untouched.
