# Verdict — S-CZ (CZ-Liga shots on target, v5 pattern)

**PASS (PROVISIONAL) — Gate Zero ships.**

Dev (pooled, stats-target n = 802, LL@8.5):

| Arm | LL@8.5 | vs base 0.696543 | vs naive 0.684394 | Dev gate |
|---|---|---|---|---|
| Gate Zero | 0.678020 | ✓ | ✓ | PASS |
| RS | 0.678059 | ✓ | ✓ | PASS (but sign check 1/3) |

RS per-season LL@8.5 vs Gate Zero: 0.675275 < 0.676468 ✓;
0.690650 > 0.689904 ✗; 0.668542 > 0.667959 ✗ → sign check 1 of 3
(< 2) → RS was NOT read on the virgin window
(`read_arms: ["GZ"]`).

Virgin (2025/2026, n = 270), Gate Zero only:

| | LL@8.5 | Calibration (pp) |
|---|---|---|
| Gate Zero | **0.666555** | −1.09 (SE 2.97) |
| League base rate | 0.693006 | +2.45 |
| Naive trailing-10 | 0.688820 | −1.20 |

Gate arithmetic (PREREG_S_CZ): leg (i) LL ≤ Gate Zero's (same arm)
and ≤ best baseline's (0.688820) → PASS. Leg (ii) calibration:
|−1.09pp| breaches the 1.0pp boundary by 0.09pp, well within 1 SE
(2.97pp) → PROVISIONAL PASS. Verdict: **PASS (PROVISIONAL)**;
Gate Zero ships.

Ships: `predictions/s_cz_virgin_predictions.csv` (270 rows, FT
ladder 7.5/8.5/9.5 only — FT-only market, halves_share null) +
`engine/sot/fitted_params_virgin.json`.

Verification: headline numbers recomputed independently by the
coordinator from the shipped predictions CSV — LL@8.5 0.666555,
calibration −1.09pp, SE 2.97pp, exact match; actuals cross-checked
against the league CSV for all 270 matches. The declared
total-shots level-break risk (prereg) did not bite hard enough to
fail the gate: the walk-forward's in-season state updates adapted,
and the LL margin over the naive baseline is comfortable
(−0.0223). The provisional tag is calibration-only.
