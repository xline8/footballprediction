# Verdict — K-FR (FR-Ligue2 cards)

**FAIL at the dev gate. Virgin 2025/2026 deliberately NOT read.
Nothing ships.**

Calibration: actual − predicted. Primary line 3.5, target =
event-feed yellows (stats feed undercounts in every season — EDA).
Prereg: `prereg/PREREG_K_FR.md`. Single arm (Gate Zero) by design:
X8 was dropped in FEATURES (referee strictness split-half
r = 0.028 on dev — noise).

## Dev gate (pooled LL@3.5, n = 1,065)

| Arm | LL@3.5 |
|---|---:|
| Gate Zero | 0.6883 |
| League base rate | 0.6921 |
| Naive trailing-10 | **0.6841** |

Gate Zero beats the league base rate (0.6883 < 0.6921) but loses
to naive trailing-10 (0.6883 > 0.6841). The dev gate requires
beating BOTH baselines — **FAIL**. Per-season, the model loses to
the naive in 2022/2023 (0.6845 vs 0.6650) and 2023/2024 (0.6910 vs
0.6888) and beats it only in 2024/2025 (0.6897 vs 0.7019).

The team-yellows trait is real in this league (split-half
r = 0.445), but at the 3.5 line a trailing-10 team-mean through the
same NB prices it better than the reference ratings ensemble.
Recorded in `engine/cards/results_virgin.json` (`virgin_read:
false`). Coordinator verification: dev harness re-run reproduced
`results_dev.json` exactly.
