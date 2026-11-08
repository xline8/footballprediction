# Phase 3 — EDA: Russia Premier League

All reported figures are emitted by `analysis/eda_compute.py` into `eda_numbers.json`; this document contains no independently computed numbers.

| season | n | goals | SOT | corners | total shots | stats cards | event cards | referee |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| 2021/2022 | 240 | 2.663 | 8.988 | 9.421 | 25.783 | 3.692 | 4.833 | 40.0% |
| 2022/2023 | 240 | 3.042 | 9.450 | 9.525 | 26.600 | 3.742 | 4.683 | 100.0% |
| 2023/2024 | 240 | 2.654 | 8.833 | 10.067 | 25.408 | 3.875 | 4.229 | 87.1% |
| 2024/2025 | 240 | 2.700 | 8.892 | 9.988 | 26.625 | 4.058 | 4.338 | 97.1% |
| 2025/2026 | 240 | 2.538 | 7.967 | 9.167 | 24.475 | 4.133 | 4.354 | 70.4% |
| 2026/2027 | 112 | 2.696 | 8.741 | 8.741 | 26.857 | 4.562 | 4.705 | 100.0% |

## Findings

Cards are an artefact here: among all 1,312 matches with both sources, exact stats/event agreement is 76.5%, the mean is stats minus events = -0.550, stats are lower in 21.7% and higher in 1.8%, with maximum absolute difference 11. Stats yellows and event yellows are therefore not interchangeable; the artefact is PRESENT (the ninth league in the programme to show it). Coordinator decision, recorded here and frozen in PREREG_K_RU before any fitting: the cards target is the EVENT-UNIFIED yellow count (event Yellow + YellowRed per team, `ev_yellow_home + ev_yellow_away`); the stats-feed count is preserved in the CSV for provenance only and is never the target.

Career-pooled split-half reliability r is: goals for/against 0.842/0.748; SOT 0.849/0.846; corners 0.702/0.582; stats yellows 0.425/0.682; event yellows 0.545/0.645; total shots 0.883/0.862; possession 0.918; big chances for 0.816; box touches for/against 0.876/0.811. xG-for is 0.766 but era-limited.

Referee strictness is 0.178 pooled across 29 eligible referees (53 named total). Coverage is 40.0%, 100.0%, 87.1%, 97.1%, 70.4%, 100.0% by season. Chronological within-season referee split-half r is 0.658, 0.368, -0.398, 0.205, 0.025, null respectively; thin coverage makes X8 conditional.

The first-half complete-split pool is 2023/2024–2025/2026, with 720 matches for the stat shares. Frozen shares are goals 0.4472 (goal count n=665), SOT 0.4612, corners 0.4801, total shots 0.4602, and yellow cards 0.3519. The observed/noise ratios are SOT 0.999, corners 1.035, shots 0.997, and yellows 1.132: SOT and shots are essentially binomial noise; corners are near noise; yellows have modest excess variance. These are presentation constants, not team features.

The invasion-era split of 2021/2022 has 144 matches before 2022-02-24 and 96 after. Goals are 2.667 versus 2.656; SOT 9.194 versus 8.677; corners 9.736 versus 8.948; shots 26.681 versus 24.438; cards 3.542 versus 3.917. This is a real descriptive level shift for shots/SOT/corners, but not a clean goals break; design should score dev on post-break seasons only if prereg later confirms the break, while retaining the full historical seed for descriptive EDA.

There are 12 in-league newcomers. Their first-season GF/GA are 1.109/1.618 versus league team means 1.359/1.359: gaps -0.250/+0.259. This supports shrinkage for thin histories, but not an estimated tier offset without a second-tier corpus.

Primary dev lines selected by nearest 50% over-rate are goals 2.5 (0.525), SOT 8.5 (0.537), corners 9.5 (0.496), cards 3.5 (0.551), and total shots 25.5 (0.518). No fitting, walk-forward, or calibration is performed.

