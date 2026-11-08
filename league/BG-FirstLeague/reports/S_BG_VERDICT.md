# Verdict — S-BG (SOT): Gate Zero PROVISIONAL PASS (ships). RS fails leg (iii).

Prereg: `prereg/PREREG_S_BG.md`. Production v5 pattern, target total
SOT, primary line 8.5, warm-up 2021/2022, dev scored
2022/2023–2024/2025 (n = 841), virgin 2025/2026 (n = 293) read ONCE
for both dev-passing arms. FT-only market (no halves source).

## Dev (pooled LL@8.5)

| Arm | Dev LL@8.5 | vs league base 0.6924 | vs naive 0.6920 |
|---|---|---|---|
| Gate Zero | 0.6843 | pass | pass |
| RS | 0.6845 | pass | pass |

## Virgin (n = 293, LL@8.5; calibration = actual − predicted @8.5)

| Arm | Virgin LL@8.5 | Calibration | SE | Legs |
|---|---|---|---|---|
| Gate Zero | 0.6487 | −2.74pp | 2.79pp | (i) pass (≤ naive 0.6493, ≤ base 0.6837); (ii) PROVISIONAL |
| RS | 0.6482 | −2.78pp | 2.79pp | (i) pass; (ii) PROVISIONAL; (iii) **fail** |

Leg (iii) for RS: dev LL@8.5 ≤ Gate Zero's in only 1 of 3 dev
seasons (2024/2025: 0.6784 vs 0.6790; 2022/2023: 0.6664 vs 0.6659 and
2023/2024: 0.7084 vs 0.7078 go the other way) — RS is ineligible
regardless of its marginally lower virgin LL.

## Gate arithmetic and what ships

Gate Zero survives dev, passes virgin leg (i), and its calibration
breach (2.74pp) lies within 1 SE (2.79pp) of the 1.0pp boundary ⇒
**PROVISIONAL PASS**. Ships: Gate Zero (v5 unmodified), virgin
predictions in `predictions/s_bg_virgin_predictions.csv` (FT ladder
7.5/8.5/9.5 only), fitted params in
`engine/sot/fitted_params_virgin.json`. The virgin season ran cool
on SOT (actual over-rate at 8.5 below both arms' means); the
provisional status records exactly that. All numbers recomputed
independently from the per-match prediction CSVs — exact agreement.
