# Verdict — T-BG (total shots): Arm A CLEAN PASS (ships). B and C fail leg (i).

Prereg: `prereg/PREREG_T_BG.md`. Shots family, target total shots
(stats feed as published), primary line 17.5, tuning season
2021/2022, dev scored 2022/2023–2024/2025 (n = 841), virgin
2025/2026 (n = 293) read ONCE for all three dev-passing arms.
FT-only market (no halves source).

## Dev (pooled LL@17.5)

| Arm | Dev LL@17.5 | vs league base 0.6934 | vs naive 0.6789 |
|---|---|---|---|
| A (v1 pattern) | 0.6696 | pass | pass |
| B (+ level layer) | 0.6705 | pass | pass |
| C (E9 trailing-r) | 0.6711 | pass | pass |

## Virgin (n = 293, LL@17.5; calibration = actual − predicted @17.5)

| Arm | Virgin LL@17.5 | Calibration | SE | Legs |
|---|---|---|---|---|
| A | 0.6611 | +0.77pp | 2.83pp | (i) pass (≤ naive 0.6724, ≤ base 0.6939); (ii) CLEAN |
| B | 0.6633 | +0.98pp | 2.84pp | (i) **fail** vs A (0.6633 > 0.6611) |
| C | 0.6647 | +1.89pp | 2.84pp | (i) **fail** vs A; (ii) would be provisional only |

## What ships

**Arm A ships** (v1 pattern: ratings + moment NB + naive ensemble;
fitted lambda = 100.0, r_A = 8186.5 — effectively Poisson at this
league's low shot volume — level cell unused by A). Virgin
predictions in `predictions/t_bg_virgin_predictions.csv` (FT ladder
16.5/17.5/18.5 only, 293 rows); fitted params in
`engine/total_shots/fitted_params_virgin.json`. All numbers
recomputed independently from the per-match prediction CSVs —
exact agreement. (Audit note: the sibling export writer collected
dev-season rows into the virgin predictions file; fixed before the
final export — the file now contains the 293 virgin rows only, and
the recomputed virgin LLs above are from those rows.)
