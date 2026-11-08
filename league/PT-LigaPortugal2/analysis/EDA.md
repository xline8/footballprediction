# Exploratory data analysis

All results are descriptive and were computed without model fitting. The
levels and coverage are in `eda_summary.json`; charts are in `charts/`.

## Match levels

| season | goals | home goals | away goals | SOT | corners | total shots | event yellows |
|---|---:|---:|---:|---:|---:|---:|---:|
| 2021/2022 | 2.484 | 1.346 | 1.137 | — | — | — | 1.003 |
| 2022/2023 | 2.637 | 1.422 | 1.216 | — | — | — | 0.000 |
| 2023/2024 | 2.448 | 1.297 | 1.150 | — | — | — | 0.010 |
| 2024/2025 | 2.513 | 1.333 | 1.180 | 8.933 | 8.967 | 18.656 | 1.412 |
| 2025/2026 | 2.444 | 1.281 | 1.163 | 8.605 | 9.428 | 19.026 | 5.503 |
| 2026/2027 | 2.494 | 1.292 | 1.202 | — | — | — | 0.000 |

Stats levels are available for only 90 partial-season matches in 2024/2025
and the full 2025/2026 season. Event-yellow levels are not interchangeable
with stats yellows; the event feed changes materially across seasons.

## Trait reliability

Career-pooled chronological split-half, ratio-of-sums/mean-of-counts for
team-match rates, gives: goals-for r=0.578 and goals-against r=0.520 across
35 teams; SOT-for r=0.282, corners-for r=0.376, and total-shots-for
r=-0.210 across 18 teams and 792 valid team-match values each. The SOT,
corner, and total-shot results use only the 396 stats matches from the tiny
2024/2025 partial plus 2025/2026 full era. Event-yellow-for is a
supplementary event-source check, r=0.005 across 35 teams; it is not a
stats-yellow reliability result.

## Movers between tiers

Descriptive season-to-season counts are 3/3 in each direction in 2022/2023,
2023/2024, and 2024/2025; 1 up and 2 down in 2025/2026; and 2/2 in the
in-progress 2026/2027 transition. Mean GF/GA changes (destination minus
source, per match) are:

| season | Liga Portugal → PT2 n | GF Δ | GA Δ | PT2 → Liga Portugal n | GF Δ | GA Δ |
|---|---:|---:|---:|---:|---:|---:|
| 2022/2023 | 3 | +0.549 | -0.402 | 3 | -0.529 | +0.343 |
| 2023/2024 | 3 | +0.569 | -0.980 | 3 | -0.725 | +0.314 |
| 2024/2025 | 3 | +0.216 | -0.902 | 3 | -0.696 | +0.529 |
| 2025/2026 | 1 | +0.176 | -0.265 | 2 | -0.794 | +0.559 |
| 2026/2027 | 2 | +0.506 | -0.644 | 2 | -0.456 | +0.729 |

The evidence is only 1–3 clubs per direction per transition and is not
consistent enough to justify a fixed mover offset.

## Referees and halves

Named-referee coverage is 0/1,619 (0%); the referee trait is skipped. No
payload has FirstHalf/SecondHalf stats. Half-time goals are recoverable for
1,540 matches and the descriptive all-match 1H goal share is 0.4503, but no
halves constant is frozen. Count-market presentation is FT-only.
