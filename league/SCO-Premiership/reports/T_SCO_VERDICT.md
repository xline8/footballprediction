# Verdict — T-SCO (Scotland Premiership total shots) — **PASS** (arm B ships, CLEAN)

Prereg: `prereg/PREREG_T_SCO.md`. Primary line 24.5. Dev n=684,
virgin 2025/2026 n=228.

## Dev (pooled LL@24.5; baselines: league 0.6936, naive 0.6864)
| Arm | Dev LL | Dev gate |
|---|---|---|
| A (v1) | 0.6714 | PASS |
| B (v2 level layer) | 0.6710 | PASS |
| C (E9 trailing-r) | 0.6715 | PASS |

## Virgin 2025/2026 (reference arm = A)
| Arm | LL@24.5 | Calibration (SE) | Legs |
|---|---|---|---|
| A | 0.6694 | −0.22pp (3.23pp) | all pass, clean |
| B | **0.6684** | −0.03pp (3.23pp) | all pass, clean; sign vs A 2/3 ✓ |
| C | 0.6700 | −0.62pp (3.24pp) | leg (i) FAIL vs reference A (0.6700 > 0.6694) |
| Baselines | league 0.6883 / naive 0.6753 | | |

Both-pass rule: among passing arms the lower virgin LL ships →
**arm B (v2 level layer) ships, CLEAN PASS** (calibration −0.03pp,
well inside 1pp). `engine/total_shots/fitted_params_virgin.json`;
`predictions/t_sco_virgin_predictions.csv`; halves via 0.4582.
Independent check: virgin actual over-24.5 rate from raw CSV =
54.82% = harness actual exactly.
