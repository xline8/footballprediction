# Exploratory data analysis — MK-PrvaLiga

All fitted-window calculations below use model rows only (`is_awarded=0`). Virgin and reserve values are displayed as inventory-level aggregates only.

## F1 — levels

| Season | n | Goals/match | Home | Away | HW | D | AW | OU1.5 | OU2.5 | OU3.5 | BTTS |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 2021/2022 | 198 | 2.3687 | 1.4242 | 0.9444 | .4950 | .2475 | .2576 | .6919 | .4293 | .1970 | .4596 |
| 2022/2023 | 165 | 2.5152 | 1.3939 | 1.1212 | .4303 | .2667 | .3030 | .7091 | .4606 | .2606 | .4364 |
| 2023/2024 | 198 | 2.2525 | 1.3889 | .8636 | .5253 | .2778 | .1970 | .6465 | .3990 | .2020 | .4545 |
| 2024/2025 | 186 | 2.3226 | 1.3226 | 1.0000 | .4355 | .3065 | .2581 | .6398 | .3978 | .2581 | .4624 |
| 2025/2026 virgin | 197 | 3.0863 | 1.6954 | 1.3909 | .4315 | .1929 | .3756 | .7665 | .5736 | .3655 | .4721 |
| 2026/2027 reserve | 65 | 2.6769 | 1.6462 | 1.0308 | .4462 | .2615 | .2923 | .7538 | .4769 | .2769 | .4308 |
| Dev pooled | 549 | 2.3552 | 1.3679 | .9872 | .4663 | .2842 | .2495 | .6630 | .4171 | .2386 | .4517 |

The 2025/2026 level jump to 3.0863 is explicit. It is the virgin calibration level test: it is recorded and not smoothed, acted on, or used to change a gate.

## F2 — team traits

Program-standard chronological split-half reliability is GF r=0.6351 and GA r=0.5482 across the 2021/2022–2024/2025 dev era (47 team-seasons). On the scored 2022/2023–2024/2025 window it is GF r=0.6093 and GA r=0.5135 (35 team-seasons). The 20-seed random-split diagnostic is GF 0.5215 and GA 0.5712. Chronological reliability is therefore a SIGNAL for goals-only team traits. Per-season GF mean dispersion is in `eda_summary.json`.

## F3 — halves

The frozen dev constant is goals 1H share **0.4323**: 559 first-half goals / 1,293 event goals over 492 usable model matches. Observed share variance is 0.119702, binomial noise expectation 0.125050, ratio 0.9572, and implied true SD 0.0000. The halves result is NOISE for a team covariate; the constant is presentation-only.

## F4 — format and turnover

Entrants by first in-league appearance are recorded by ID in `eda_summary.json`: 12 in 2021/2022, 2 in 2022/2023, 3 in 2023/2024, 1 in 2024/2025, 2 in 2025/2026, and 1 in 2026/2027. The index contains only North Macedonia league ID 249, so X2 mover estimation is not available.

For scored target seasons 2022/2023, 2023/2024, and 2024/2025, prior-match counts are mechanically: entrants n=0 are 2, 3, and 1; teams with 1–5 prior matches are 0 in every season; incumbents with at least 30 prior matches are 9, 9, and 11. SHRINK is therefore pre-registered but expected to be identical to Gate Zero on this corpus.

## F5 — absences

Stats, shotmap, xG, referee names, and plain Yellow events are absent in every season and every payload. Lineup is non-null in only 4/1,022 and is not a usable target or feature. SOT, corners, total shots, cards-as-yellows, and referee markets are NOT-BUILDABLE.
