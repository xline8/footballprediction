# Verdict — C-TH (corners): **PASS (clean) — Gate Zero ships**

Prereg: `prereg/PREREG_C_TH.md` (frozen and committed before fitting).
Primary line 9.5. All numbers recomputed by the coordinator from the
per-match CSVs against the league CSV (0 target mismatches, dev and
virgin).

## Dev (seed 2022/2023; scored 2023/2024–2024/2025, n = 480)

| Arm | Pooled LL@9.5 | 2023/2024 | 2024/2025 |
|---|---|---|---|
| Gate Zero (X9) | 0.6950 | 0.6954 | 0.6946 |
| X7 | 0.7058 | 0.7169 | 0.6946 |
| League base rate | 0.7266 | — | — |
| Naive trailing-10 | 0.7251 | — | — |

Both arms beat both baselines → both pass the dev gate and were read on
the virgin. (Audit note: the first dev run fitted betas at the copied RU
line 8.5; corrected to the preregistered primary line 9.5 and re-run
before any virgin read — the numbers above are the corrected run. Gate
Zero's grid selects beta = 0 in both dev seasons even at 9.5; X7 is a
genuinely distinct arm after the fix, active with nonzero beta on
45.4% of dev matches.)

## Virgin (2025/2026, n = 240, read ONCE)

| Arm | LL@9.5 | Mean P(over) | Actual | Calibration (SE) |
|---|---|---|---|---|
| Gate Zero | 0.6994 | 0.4896 | 0.4958 | +0.62pp (3.25pp) |
| X7 | 0.6994 | 0.4896 | 0.4958 | +0.62pp (3.25pp) |
| League base rate | 0.7257 | — | — | — |
| Naive trailing-10 | 0.7280 | — | — | — |

## Gate arithmetic

Gate Zero: leg (i) 0.6994 ≤ best baseline 0.7257 ✓; leg (ii)
|calibration| = 0.62pp ≤ 1.0pp → **clean PASS**. X7: its virgin fit also
selects beta_bt = 0, so its virgin predictions are identical to Gate
Zero's and it passes legs (i)–(iii) as well (dev sign check: ≤ Gate Zero
in 1 of 2 dev seasons). Both-pass tie → the simpler arm ships:
**Gate Zero**.

## What ships

- Arm Gate Zero with virgin fitted params (`engine/corners/
  fitted_params_virgin.json`): gamma 0.15, r 1.1285, beta [0, 0]
  (the X9 territorial multiplier is fitted but selects zero weight in
  this league), fit_n 710.
- `predictions/c_th_virgin_predictions.csv` (240 rows; FT ladder
  8.5/9.5/10.5 + 1H/2H presentation via the frozen corners constant
  0.4622).
