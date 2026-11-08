# Verdict — T-ZA (total shots): **FAIL** (virgin calibration leg)

Prereg: `prereg/PREREG_T_ZA.md` (frozen and committed before fitting).
Primary line 21.5. All numbers recomputed by the coordinator from the
per-match CSVs against the league CSV (0 target mismatches, dev and
virgin).

## Dev (seed 2022/2023; scored 2023/2024–2024/2025, n = 448)

| Arm | Pooled LL@21.5 | 2023/2024 | 2024/2025 |
|---|---|---|---|
| A (v1) | 0.6912 | 0.6914 | 0.6909 |
| B (v2) | 0.6916 | 0.6924 | 0.6907 |
| C (E9) | 0.6909 | 0.6909 | 0.6909 |
| League base rate | 0.6963 | — | — |
| Naive trailing-10 | 0.7014 | — | — |

All three arms beat both baselines → all pass the dev gate and were
read on the virgin.

## Virgin (2025/2026, n = 240, read ONCE)

| Arm | LL@21.5 | Mean P(over) | Actual | Calibration (SE) |
|---|---|---|---|---|
| A | 0.6686 | 0.5140 | 0.5667 | +5.26pp (3.14pp) |
| B | 0.6680 | 0.5208 | 0.5667 | +4.58pp (3.14pp) |
| C | 0.6690 | 0.5126 | 0.5667 | +5.41pp (3.14pp) |
| League base rate | 0.6859 | — | — | — |
| Naive trailing-10 | 0.6692 | — | — | — |

## Gate arithmetic

LL leg: A and B beat the best baseline (0.6692) and C (0.6690) also
edges it, but C fails leg (i) against the reference arm A
(0.6690 > 0.6686). Calibration leg is decisive for all three: the
virgin season ran shot-hot (22.58 total shots/match vs dev 21.79;
over-21.5 rate 0.5667 vs dev 0.522) and every arm under-predicts by
4.6–5.4pp — each breach exceeds the 1.0pp boundary by more than
1 SE (3.14pp), so none qualifies even as provisional. **No arm
passes; nothing ships.**

**T-ZA FAILS.** 2026/2027 remains the untouched confirmatory window.
