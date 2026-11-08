# Verdict — S-SK (SK-1Liga shots on target, v5 pattern)

**PASS (CLEAN) — Gate Zero ships.**

Dev (pooled, stats-target n = 568, LL@8.5):

| Arm | LL@8.5 | vs base 0.702388 | vs naive 0.695303 | Dev gate |
|---|---|---|---|---|
| Gate Zero | 0.683432 | ✓ | ✓ | PASS |
| RS | 0.683849 | ✓ | ✓ | PASS (but sign check 1/3) |

RS per-season LL@8.5 vs Gate Zero: 0.695051 < 0.695224 ✓;
0.684803 > 0.684097 ✗; 0.671525 > 0.670795 ✗ → sign check 1 of 3
(< 2) → RS was NOT read on the virgin window
(`read_arms: ["GZ"]`).

Virgin (2025/2026, n = 192), Gate Zero only:

| | LL@8.5 | Calibration (pp) |
|---|---|---|
| Gate Zero | **0.687872** | −0.88 (SE 3.60) |
| League base rate | 0.696309 | −5.06 |
| Naive trailing-10 | 0.693703 | −1.30 |

Gate arithmetic (PREREG_S_SK): leg (i) LL ≤ Gate Zero's (same
arm) and ≤ best baseline's (0.693703) → PASS. Leg (ii)
calibration: |−0.88pp| ≤ 1.0pp → **CLEAN PASS** (no SE rescue
needed). Verdict: **PASS (CLEAN)**; Gate Zero ships.

Ships: `predictions/s_sk_virgin_predictions.csv` (192 rows, FT
ladder 7.5/8.5/9.5 only — FT-only market, halves_share null) +
`engine/sot/fitted_params_virgin.json`.

Verification: headline numbers recomputed independently by the
coordinator from the shipped predictions CSV — LL@8.5 0.687872,
calibration −0.88pp, SE 3.60pp, exact match; actual
over-8.5 rate cross-checked against the league CSV (0.53125,
mean predicted 0.52245). The declared total-shots level-break
risk (prereg) did not bite: the walk-forward's in-season state
updates adapted to the rich-era shot counting, and calibration
landed inside the clean band despite the break sitting exactly
at the virgin boundary.
