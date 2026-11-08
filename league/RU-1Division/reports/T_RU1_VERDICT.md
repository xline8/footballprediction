# Verdict — T-RU1 (Russia 1. Division total shots)

**FAIL at the virgin gate (calibration leg, all arms). Nothing ships.**

## Dev (stats n = 855, LL @ 15.5)

| arm | LL @ 15.5 | calibration |
|---|---|---|
| A (v1 pattern) | 0.691481 | +4.09 pp |
| B (v2 level layer) | 0.692467 | +4.79 pp |
| C (E9 trailing-r) | 0.692409 | +3.90 pp |
| league base | 0.701883 | |
| naive trailing-10 | 0.737267 | |

Per-season LL: A 0.696615 / 0.682307 / 0.695584; B 0.699377 /
0.680963 / 0.697059; C 0.699161 / 0.681545 / 0.696480. Dev gate:
all three arms beat BOTH baselines — PASS. All three were read
on the virgin.

## Virgin (2025/2026, stats n = 287, LL @ 15.5)

| arm | LL @ 15.5 | calibration | SE |
|---|---|---|---|
| A | 0.693726 | +6.83 pp | 2.93 |
| B | 0.694095 | +6.56 pp | 2.93 |
| C | 0.693837 | +6.80 pp | 2.92 |
| league base | 0.704708 | | |
| naive trailing-10 | 0.712787 | | |

Leg (i): arm LL ≤ reference arm A's (0.693726) AND ≤ best
baseline (0.704708). A passes (itself, and under both baselines);
B (0.694095) and C (0.693837) both sit above A's LL, so both
**FAIL** leg (i) against the reference despite beating the
baselines. Leg (ii): |calibration| ≤ 1.0 pp, breach within 1 SE
= provisional. Breaches are 6.6–6.8 pp with SE ≈ 2.9; excess
over the boundary ≈ 5.6–5.8 pp > 1 SE — **FAIL for every arm**,
including A. Leg (iii): B and C each beat A in only 1 of 3 dev
seasons — FAIL. No arm passes all legs: verdict FAIL, nothing
ships.

The virgin season ran hot on shots: actual over-15.5 rate
47.39% against ~40.5% mean predicted. The arms rank totals well
(LL beats both baselines) but sit ~7 pp under the realised level,
outside every calibration allowance the prereg permits.

Arm LLs and calibrations recomputed by the coordinator from
`engine/total_shots/predictions_virgin.csv`; baselines from
`engine/total_shots/results_virgin.json` (the T engine emits no
per-match baseline columns).
