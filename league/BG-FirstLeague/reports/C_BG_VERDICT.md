# Verdict — C-BG (corners): Gate Zero CLEAN PASS (ships). POSS row-identical.

Prereg: `prereg/PREREG_C_BG.md`. Production v3 pattern, target total
corners, primary line 9.5, seed 2021/2022, dev scored
2022/2023–2024/2025 (n = 841), virgin 2025/2026 (n = 293) read ONCE
for both dev-passing arms. FT-only market (no halves source).

## Dev (pooled LL@9.5)

| Arm | Dev LL@9.5 | vs league base 0.7150 | vs naive 0.7057 |
|---|---|---|---|
| Gate Zero | 0.6935 | pass | pass |
| POSS | 0.6935 | pass | pass |

The two arms are numerically identical in dev and virgin: the
per-season beta fitting chose **beta = 0.0** for POSS (and [0.0, 0.0]
for Gate Zero, whose multiplier is in any case inactive on every row
because `big_chance` does not exist in this league — recorded in the
prereg in advance). Possession, despite its 0.822 trait reliability,
earns a zero coefficient under the preregistered grid; the core
ratings engine carries the result. `active_with_nonzero_beta_share`
= 0.0 in every dev season for both arms.

## Virgin (n = 293, LL@9.5; calibration = actual − predicted @9.5)

| Arm | Virgin LL@9.5 | Calibration | SE | Legs |
|---|---|---|---|---|
| Gate Zero | 0.6838 | +0.38pp | 2.90pp | (i) pass (≤ base 0.7088, ≤ naive 0.7033); (ii) CLEAN |
| POSS | 0.6838 | +0.38pp | 2.90pp | identical; tie → simpler arm |

## What ships

**Gate Zero ships** (tie broken to the simpler arm per prereg):
fitted params gamma = 0.3, r = 1.2858, beta = [0.0, 0.0]
(`engine/corners/fitted_params_virgin.json`); virgin predictions in
`predictions/c_bg_virgin_predictions.csv` (FT ladder 8.5/9.5/10.5
only). All numbers recomputed independently from the per-match
prediction CSVs — exact agreement.
