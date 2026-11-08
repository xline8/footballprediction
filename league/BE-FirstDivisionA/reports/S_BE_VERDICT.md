# S-BE verdict — PASS (calibration PROVISIONAL) — RS SHIPS

Prereg: `prereg/PREREG_S_BE.md` (frozen f0c214a, before fitting).
Primary line **8.5** (dev over-rate 0.548). Dev pooled n = 955
(count-market scoring excludes the one score-only dev match,
4449361 — target absent, never imputed); virgin 2025/2026 n = 313,
read once, for all three dev-passing arms. Arms: Gate Zero + RS +
X4 (X4 adopted on BE reliability, EDA F7 r = 0.435; X6 dropped,
F8 r = 0.075).

## Dev results — pooled LL@8.5

| Arm / baseline | LL@8.5 |
|---|---|
| Gate Zero | 0.6797 |
| RS (BB prior 20,000) | 0.6791 |
| X4 (xG/shot quality) | 0.6789 |
| League base rate | 0.6887 |
| Naive trailing-10 | 0.6866 |

All three arms beat both baselines → all pass the dev gate.
Per-season sign checks vs Gate Zero: RS 3/3; X4 2/3 (better
2022/2023 and 2023/2024, worse 2024/2025).

## Virgin results (2025/2026, n = 313)

| Arm / baseline | LL@8.5 | Calibration (mean P − actual) |
|---|---|---|
| Gate Zero | 0.6888 | +2.40pp (SE 2.82pp) |
| RS | 0.6882 | +2.32pp (SE 2.81pp) |
| X4 | 0.6897 | +1.94pp (SE 2.82pp) |
| League base rate | 0.6962 | — |
| Naive trailing-10 | 0.6983 | — |

## Gate arithmetic

- Leg (i): RS passes (0.6882 ≤ Gate Zero 0.6888 and ≤ best baseline
  0.6962). Gate Zero also ≤ both baselines. **X4 FAILS leg (i)** —
  the best dev arm loses the virgin LL to Gate Zero (0.6897 >
  0.6888); its calibration was the best of the three and it still
  cannot ship.
- Leg (ii): Gate Zero and RS breach the 1.0pp boundary by 1.40pp /
  1.32pp, each within 1 SE (~2.8pp) → **PROVISIONAL PASS** for
  both. The virgin season ran slightly hot on SOT relative to the
  model (actual over-8.5 rate above prediction for every arm).
- Leg (iii): RS sign check 3/3 (above).
- Both Gate Zero and RS pass; the both-pass rule ships the lower
  pooled virgin LL: **RS** (0.6882 < 0.6888 — a 0.0006 margin,
  recorded as such; the same RS-wins-by-a-hair shape as S-CH).

**Ships:** RS (v5 pattern with the ratio-shrink prior P = 20,000),
fitted parameters in `engine/sot/fitted_params_virgin.json`, virgin
predictions in `predictions/s_be_virgin_predictions.csv` (313 rows;
FT ladder + 1H/2H via the frozen SOT constant 0.452). **BE joins
the daily runner with SOT.** Coordinator verification: virgin
LL@8.5 recomputed from the shipped predictions CSV = 0.6882,
matching the results JSON; calibration recomputed +2.32pp.
