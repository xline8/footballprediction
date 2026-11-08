# C-AU verdict — PASS (clean calibration) — Gate Zero SHIPS

Prereg: `prereg/PREREG_C_AU.md` (frozen b353f24, before fitting).
Primary line 10.5. Dev pooled n = 508; virgin 2025/2026 n = 163,
read once for both dev-passing arms.

## Dev results — pooled LL@10.5

| Arm / baseline | LL@10.5 |
|---|---|
| Gate Zero (X9) | 0.6962 |
| X7 (box touches) | 0.7030 |
| League base rate | 0.7329 |
| Naive trailing-10 | 0.7255 |

Both arms beat both baselines → both pass the dev gate. X7
per-season sign check vs Gate Zero: 0.7013 ≤ 0.7225 (2022/2023),
0.7112 > 0.6742 (2023/2024), 0.6966 > 0.6930 (2024/2025) → 1/3.

## Virgin results (2025/2026, n = 163)

| Arm / baseline | LL@10.5 | Calibration (mean P − actual) |
|---|---|---|
| Gate Zero | 0.7000 | −0.01pp (SE 3.95pp) |
| X7 | 0.6940 | −0.18pp (SE ~3.9pp) |
| League base rate | 0.7070 | — |
| Naive trailing-10 | 0.7228 | — |

## Gate arithmetic

- Leg (i): Gate Zero 0.7000 ≤ its own LL and ≤ best baseline
  0.7070 — PASS. X7 0.6940 ≤ 0.7000 and ≤ 0.7070 — PASS.
- Leg (ii): Gate Zero |−0.01pp| ≤ 1.0pp — **clean PASS** (the
  tightest calibration recorded in the program: predicted
  over-10.5 rate 45.39% vs actual 45.40%). X7 also clean.
- Leg (iii): X7 sign check 1/3 — **FAIL**. X7 is not eligible
  despite the better virgin LL, applied as written.
- Only Gate Zero passes all legs → **Gate Zero ships**.

**Ships:** Gate Zero (production corners pattern, X9 covariates;
virgin fit γ = 0.15, r = 1.175, β = [−0.0025, 0]), fitted
parameters in `engine/corners/fitted_params_virgin.json`, virgin
predictions in `predictions/c_au_virgin_predictions.csv`
(163 rows; FT ladder 9.5/10.5/11.5 + 1H/2H via the frozen
corners constant 0.452). **AU joins the daily runner with
corners.** Note the X7 pattern differs from J1/DK: there the
box-touch β fitted to exactly 0; here X7 produced genuinely
different (and better-on-virgin) predictions but its dev sign
check (1/3, driven by the 2023/2024 spike season) disqualifies
it under the frozen rule. Coordinator verification: virgin
LL@10.5 recomputed from the shipped predictions CSV = 0.699964,
matching the results JSON to 6dp.
