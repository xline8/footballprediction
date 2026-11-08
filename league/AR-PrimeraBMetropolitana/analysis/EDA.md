# Phase 3 — Exploratory data analysis

All descriptive statistics below use seasons 2021–2025 only (1,698 group
matches). The 2026 window is reserved as virgin and contributes no levels,
rates, traits, constants, or chart data.

## Levels

| season | matches | goals/match | home goals | away goals | home/draw/away % | OU 1.5 | OU 2.5 | OU 3.5 |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| 2021 | 272 | 2.3713 | 1.2904 | 1.0809 | 39.71 / 30.15 / 30.15 | 68.38 | 39.34 | 21.32 |
| 2022 | 272 | 2.2022 | 1.2426 | 0.9596 | 41.54 / 30.15 / 28.31 | 66.18 | 40.81 | 19.12 |
| 2023 | 272 | 1.9375 | 1.0074 | 0.9301 | 33.46 / 34.93 / 31.62 | 57.35 | 32.72 | 12.50 |
| 2024 | 462 | 1.9675 | 1.1320 | 0.8355 | 41.56 / 32.25 / 26.19 | 59.09 | 33.77 | 13.42 |
| 2025 | 420 | 2.0619 | 1.1738 | 0.8881 | 39.29 / 34.05 / 26.67 | 62.62 | 34.05 | 15.48 |

Pooled goals are 2.0883 per match, with home 1.1655 and away 0.9229;
home advantage is 0.2426 goals. The pooled primary line is OU 2.5 over at
35.6890% (OU 1.5 62.3086%; OU 3.5 15.9600%). Goal variance/mean is 1.0143.

## Reliability and halves

The split-half team-trait checks use 60 random within-team splits and a
24-match minimum. Goals-for reliability is r = 0.3470 and goals-against
reliability is r = 0.4869 (the exact values, including odd/even checks, are
in `eda_summary.json`). These support goal ratings and trailing goal means.

For goals, event-time 1H share is 0.4399 across 1,463 non-zero-goal matches.
Observed share variance is 0.1288 versus a binomial noise floor of 0.1354;
the estimated true variance is −0.0065 and the team split-half r is −0.1167.
The team half-tendency test therefore fails: there is no per-team 1H
tendency to model. The frozen presentation constant is adopted instead,
exactly as in BNAC/AR/J1 — goals 1H share 0.439932, presentation only.

## Movers and absent targets

The 2022–2025 newcomer pool has 14 team-blocks. The pooled GF/GA gaps are
−0.0325/−0.0410 goals per match. Four blocks are from Nacional, with gaps
−0.2125/−0.1186; ten are from below or cross-competition, with gaps
+0.0394/−0.0099. These are the conditional X2 arm inputs.

Stats blocks, shotmap shots, SOT, corners, total shots, xG, referee text,
and Yellow card events are absent across the 2,236 PBM payloads. They are
recorded as absent rather than estimated. The full machine-readable output
is in `eda_summary.json` and `inventory_summary.json`.
