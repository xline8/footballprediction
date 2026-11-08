# Verdict — S-RU1 (Russia 1. Division shots on target)

**FAIL at the virgin gate. Nothing ships.**

## Dev (stats n = 855, LL @ 7.5)

| arm | LL @ 7.5 | calibration |
|---|---|---|
| Gate Zero | 0.678264 | +0.60 pp |
| RS | 0.678046 | +0.61 pp |
| league base | 0.709600 | |
| naive trailing-10 | 0.702465 | |

Per-season LL: GZ 0.644903 / 0.685278 / 0.709637; RS 0.645771 /
0.684462 / 0.708806. Dev gate: both arms beat BOTH baselines —
PASS. Both arms were read on the virgin.

## Virgin (2025/2026, stats n = 287, LL @ 7.5)

| arm | LL @ 7.5 | calibration | SE |
|---|---|---|---|
| Gate Zero | 0.704761 | +4.84 pp | 2.98 |
| RS | 0.703490 | +4.93 pp | 2.97 |
| league base | 0.700336 | | |
| naive trailing-10 | 0.724585 | | |

Leg (i): arm LL ≤ Gate Zero's AND ≤ best baseline (0.700336).
Gate Zero 0.704761 > 0.700336 **FAIL**; RS 0.703490 > 0.700336
**FAIL**. Leg (ii): |calibration| ≤ 1.0 pp, breach within 1 SE =
provisional. GZ breach 4.84 pp, excess over the boundary 3.84 pp
> SE 2.98 **FAIL**; RS likewise **FAIL**. Leg (iii) is moot (RS
would have passed it, 2 of 3 dev seasons). No arm passes all
legs: verdict FAIL, nothing ships.

The dev edge did not survive the virgin: both arms land behind
the flat league base rate on LL and over-predict the over-7.5
rate by ~5 pp (the virgin season's SOT level, 7.85/match on stats
rows, came with a lower over-7.5 share than the model expected).

All numbers recomputed by the coordinator from
`engine/sot/predictions_dev.csv` and `predictions_virgin.csv`.
