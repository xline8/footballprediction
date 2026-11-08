# Exploratory data analysis — SLO-PrvaLiga

All fitted-window calculations below use model rows only (`is_awarded=0`). Virgin and reserve values are inventory-level aggregates only.

## F1 — levels

| Window | n | Goals/match | Home | Away | HW | D | AW | OU1.5 | OU2.5 | OU3.5 | BTTS |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 2021/2022 | 180 | 2.5389 | 1.3111 | 1.2278 | .3889 | .2667 | .3444 | .7000 | .4389 | .2889 | .4944 |
| 2022/2023 | 180 | 2.5389 | 1.3000 | 1.2389 | .3944 | .2944 | .3111 | .7111 | .4389 | .2444 | .4889 |
| 2023/2024 | 178 | 2.8034 | 1.4494 | 1.3539 | .3820 | .2584 | .3596 | .8034 | .5225 | .3258 | .5899 |
| 2024/2025 | 180 | 2.7667 | 1.5611 | 1.2056 | .4333 | .2611 | .3056 | .7556 | .5000 | .3000 | .5111 |
| 2025/2026 virgin model | 161 | 3.0870 | 1.6894 | 1.3975 | .4969 | .1801 | .3230 | .8509 | .6522 | .3416 | .5901 |
| 2026/2027 reserve | 74 | 2.5405 | 1.3649 | 1.1757 | .3378 | .3514 | .3108 | .7027 | .4730 | .2838 | .5000 |
| Dev pooled | 538 | 2.7026 | 1.4368 | 1.2658 | .4033 | .2714 | .3253 | .7565 | .4870 | .2900 | .5297 |

The all-index official virgin level is 500 goals / 162 matches = 3.0864; the model-only level above excludes the one awarded match and has 497 goals / 161 matches. This is a recorded level test, not a fit input.

## F2 — team traits

Chronological split-half reliability is GF r=.6053 and GA r=.4049 across 40 team-seasons in the 2021/2022–2024/2025 era. On the scored 2022/2023–2024/2025 window it is GF .6302 and GA .4756 across 30 team-seasons. The 20-seed random-split means are GF .6056 and GA .5521.

## F3 — halves

The frozen dev constant is goals 1H share **0.4498**: 654 first-half goals / 1,454 event goals over 506 usable model matches. Observed share variance is 0.108422, binomial noise expectation 0.115791, ratio 0.936361, and implied true SD 0.0000. The halves result is NOISE for a team covariate; the constant is presentation-only.

## F4 — format and turnover

Entrants by first in-league appearance are recorded by ID in `eda_summary.json`: 10 in 2021/2022, 1 in 2022/2023, 1 in 2023/2024, 2 in 2024/2025, 0 in 2025/2026, and 1 in 2026/2027. There is no sibling Slovenia league in the complete index, so X2 mover estimation is not available.

For scored target seasons 2022/2023, 2023/2024, and 2024/2025, SHRINK expectation counts are respectively `(n_0, n_1_to_5, n_6_to_29, n_30_plus) = (1,0,0,9), (1,0,0,9), (2,0,0,8)`. SHRINK is pre-registered but expected to equal Gate Zero on this corpus.

## F5 — absences

Stats, shotmap, referee names, and plain Yellow events are absent in every season and every payload. Lineup is non-null in only 32/956. SOT, corners, total shots, cards-as-yellows, and referee markets are NOT-BUILDABLE.
