# Verdict — C-ZA (corners): **PROVISIONAL PASS — Gate Zero ships**

Prereg: `prereg/PREREG_C_ZA.md` (frozen and committed before fitting).
Primary line 8.5. All numbers recomputed by the coordinator from the
per-match CSVs against the league CSV (0 target mismatches, dev and
virgin).

## Dev (seed 2022/2023; scored 2023/2024–2024/2025, n = 448)

| Arm | Pooled LL@8.5 | 2023/2024 | 2024/2025 |
|---|---|---|---|
| Gate Zero (X9) | 0.6956 | 0.7027 | 0.6874 |
| X7 | 0.6928 | 0.6975 | 0.6874 |
| League base rate | 0.7443 | — | — |
| Naive trailing-10 | 0.7496 | — | — |

Both arms beat both baselines → both pass the dev gate and were read
on the virgin. (X7's dev edge comes entirely from 2023/2024, where
Gate Zero's X9 multiplier was active with nonzero beta on 93.7% of
matches and hurt it; X7's own beta_bt selected 0 in both dev seasons,
so its 2023/2024 difference is the un-multiplied core with its own
gamma/r fit. In 2024/2025 the two arms are identical.)

## Virgin (2025/2026, n = 240, read ONCE)

| Arm | LL@8.5 | Mean P(over) | Actual | Calibration (SE) |
|---|---|---|---|---|
| Gate Zero | 0.6977 | 0.5002 | 0.4667 | −3.35pp (3.24pp) |
| X7 | 0.6977 | 0.5002 | 0.4667 | −3.35pp (3.24pp) |
| League base rate | 0.7072 | — | — | — |
| Naive trailing-10 | 0.7144 | — | — | — |

## Gate arithmetic

Gate Zero: leg (i) 0.6977 ≤ best baseline 0.7072 ✓; leg (ii)
|calibration| = 3.35pp > 1.0pp clean boundary, but the excess over
the boundary (2.35pp) is within 1 SE (3.24pp) → **PROVISIONAL PASS**.
The virgin season ran corner-poor (8.71/match vs dev 8.83; over-8.5
rate 0.4667 vs dev 0.542) and the model over-predicts accordingly.
X7: its virgin fit also selects beta_bt = 0, so its virgin
predictions are identical to Gate Zero's and it passes legs
(i)–(iii) as well (dev sign check: ≤ Gate Zero in both dev seasons).
Both-pass tie → the simpler arm ships: **Gate Zero**.

## What ships

- Arm Gate Zero with virgin fitted params
  (`engine/corners/fitted_params_virgin.json`): gamma 0.15,
  r 1.1077, beta [0, 0] (the X9 territorial multiplier is fitted but
  selects zero weight in this league), fit_n 676.
- `predictions/c_za_virgin_predictions.csv` (240 rows; FT ladder
  7.5/8.5/9.5 + 1H/2H presentation via the frozen corners constant
  0.4679). Audit note: the first emission of this file lacked the
  preregistered halves-presentation columns (the copied harness's
  writer had lost them); it was re-emitted from the same frozen
  virgin fitted params with the columns restored, and the
  coordinator verified the FT probabilities are identical to the
  first emission on all 240 rows (0 diffs). No gate number changed.
