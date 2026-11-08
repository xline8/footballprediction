# T-CH verdict — PASS (calibration PROVISIONAL) — arm A SHIPS

Prereg: `prereg/PREREG_T_CH.md` (frozen ccf74a9, before fitting).
Primary line **26.5** (dev over-rate 0.518). Dev pooled n = 636;
virgin 2025/2026 n = 228, read once, for all three dev-passing arms.

## Dev results — pooled LL@26.5

| Arm / baseline | LL@26.5 |
|---|---|
| A (v1 pattern) | 0.6691 |
| B (v2 level layer) | 0.6694 |
| C (E9 trailing-r) | 0.6687 |
| League base rate | 0.7026 |
| Naive trailing-10 | 0.6830 |

All three arms beat both baselines → all pass the dev gate.

## Virgin results (2025/2026, n = 228)

| Arm / baseline | LL@26.5 | Calibration (mean P − actual) |
|---|---|---|
| A | 0.6114 | −3.53pp (SE 3.04pp) |
| B | 0.6109 | −3.30pp (SE 3.04pp) |
| C | 0.6122 | −3.87pp (SE 3.04pp) |
| League base rate | 0.6655 | — |
| Naive trailing-10 | 0.6231 | — |

## Gate arithmetic

- Leg (i) (vs reference arm A and best baseline 0.6231): A PASS
  (0.6114); B PASS (0.6109 ≤ 0.6114); **C FAIL** (0.6122 > A's
  0.6114) — the E9 trailing-r arm does not replicate its DK/BR/US
  wins here.
- Leg (ii): A and B breach the 1.0pp boundary by 2.53pp / 2.30pp,
  within 1 SE (3.04pp) → **PROVISIONAL PASS** for both. (C's breach,
  2.87pp, would also be provisional — moot under leg (i).) The
  virgin season ran hot on shots (28.51/match vs dev 27.44).
- Leg (iii): B's dev sign check vs A is **1/3** (B better only in
  2022/2023: 0.6639 ≤ 0.6644; worse 2023/2024 and 2024/2025) →
  **B FAILS leg (iii)** despite the best virgin LL.
- Only **arm A** passes all legs → A ships.

**Ships:** arm A (v1 pattern), fitted parameters in
`engine/total_shots/fitted_params_virgin.json`, virgin predictions
in `predictions/t_ch_virgin_predictions.csv` (228 rows; FT ladder
25.5/26.5/27.5 + 1H/2H via the frozen shots constant 0.456).
**CH joins the daily runner with total shots.** Coordinator
verification: virgin LL@26.5 recomputed from the shipped
predictions CSV = 0.6114, matching the results JSON.
