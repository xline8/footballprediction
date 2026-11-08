# K-BE verdict — PASS (clean) — Gate Zero SHIPS

Prereg: `prereg/PREREG_K_BE.md` (frozen f0c214a, before fitting).
Primary line **3.5** (dev over-rate 0.543). Dev pooled n = 955
(score-only match excluded — target absent); virgin 2025/2026
n = 313, read once, for both dev-passing arms.

## Dev results — pooled LL@3.5

| Arm / baseline | LL@3.5 |
|---|---|
| Gate Zero | 0.6861 |
| X8 (referee) | 0.6821 |
| League base rate | 0.6906 |
| Naive trailing-10 | 0.6905 |

Both arms beat both baselines → both pass the dev gate. X8
per-season sign check vs Gate Zero: 2/3 (worse 2022/2023, better
2023/2024 and 2024/2025).

## Virgin results (2025/2026, n = 313)

| Arm / baseline | LL@3.5 | Calibration (mean P − actual) |
|---|---|---|
| Gate Zero | 0.6853 | +0.19pp (SE 2.81pp) |
| X8 | 0.6952 | −0.40pp (SE 2.84pp) |
| League base rate | 0.6941 | — |
| Naive trailing-10 | 0.6989 | — |

## Gate arithmetic

- Leg (i): Gate Zero passes (0.6853 ≤ best baseline 0.6941).
  **X8 FAILS leg (i)** — its virgin LL (0.6952) loses to Gate Zero
  *and* to the league base rate, reversing its dev advantage.
- Leg (ii): Gate Zero's calibration is **+0.19pp — inside the
  1.0pp boundary: CLEAN PASS**, the only clean calibration in this
  league's build. (X8's −0.40pp is also clean but moot.)
- Leg (iii): Gate Zero is exempt; X8's 2/3 is moot under leg (i).

**Ships:** Gate Zero (production cards pattern, referee not used),
fitted parameters in `engine/cards/fitted_params_virgin.json`,
virgin predictions in `predictions/k_be_virgin_predictions.csv`
(313 rows; FT ladder 2.5/3.5/4.5 + 1H/2H via the frozen yellows
constant 0.317). **BE joins the daily runner with cards.**
Coordinator verification: virgin LL@3.5 recomputed from the
shipped predictions CSV (actuals joined from the matches CSV) =
0.6853, matching the results JSON; calibration recomputed +0.19pp.

Recorded plainly: the referee arm genuinely helped in dev
(−0.0040 LL, the largest X8 dev gain in the program) on the
program's weakest adopted referee trait (EDA F9, r = 0.378), and
then gave it all back in the virgin window. The gate, not the dev
story, decides — Gate Zero ships.
