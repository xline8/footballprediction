# Verdict — T-TH (total shots): **PROVISIONAL PASS — arm B ships**

Prereg: `prereg/PREREG_T_TH.md` (frozen and committed before fitting).
Primary line 26.5. All numbers recomputed by the coordinator from the
per-match CSVs against the league CSV (0 target mismatches, dev and
virgin); the recomputation matches the harness's virgin metrics exactly.

## Dev (seed 2022/2023; scored 2023/2024–2024/2025, n = 480)

| Arm | Pooled LL@26.5 | 2023/2024 | 2024/2025 |
|---|---|---|---|
| A (v1) | 0.6688 | 0.6807 | 0.6569 |
| B (v2 + level layer) | 0.6672 | 0.6785 | 0.6559 |
| C (E9 trailing-r) | 0.6689 | 0.6811 | 0.6568 |
| League base rate | 0.7047 | — | — |
| Naive trailing-10 | 0.6717 | — | — |

All three arms beat both baselines → all pass the dev gate and were read
on the virgin.

## Virgin (2025/2026, n = 240, read ONCE)

| Arm | LL@26.5 | Calibration (SE) |
|---|---|---|
| A | 0.6938 | −1.34pp (3.23pp) |
| B | 0.6908 | −1.03pp (3.23pp) |
| C | 0.6937 | −1.31pp (3.23pp) |
| League base rate | 0.6912 | −1.67pp |
| Naive trailing-10 | 0.7037 | −2.30pp |

## Gate arithmetic

Reference arm = A (it passed dev). Leg (i): LL ≤ A's AND ≤ best
baseline's (0.6912).
- A: 0.6938 > 0.6912 → **fails leg (i)**.
- C: 0.6937 > 0.6912 → **fails leg (i)**.
- B: 0.6908 ≤ 0.6938 ✓ and ≤ 0.6912 ✓ (margin 0.0004 — thin, recorded
  as-is; gates are mechanical). Leg (ii): |−1.03pp| breaches 1.0pp by
  0.03pp, within 1 SE (3.23pp) → **PROVISIONAL PASS**. Leg (iii): B's
  dev LL ≤ A's in both dev seasons ✓.

**T-TH: arm B ships as a PROVISIONAL PASS.**

## What ships

- Arm B with fitted params (`engine/total_shots/
  fitted_params_virgin.json`): lambda 100, r_A 107.848, level cell
  (HL 30, scale 0.5, K 50), trailing-r window 200.
- `predictions/t_th_virgin_predictions.csv` (240 virgin rows only;
  FT ladder 25.5/26.5/27.5 + 1H/2H presentation via the frozen
  total-shots constant 0.4522).
