# Exploratory data analysis

All results are descriptive. No model was fitted and no dev or virgin harness
was run.

| season | n | home goals | away goals | total goals | home/draw/away | OU2.5 | BTTS | card events/match |
|---|---:|---:|---:|---:|---|---:|---:|---:|
| 2021/2022 | 292 | 1.445 | 0.866 | 2.312 | 49.3% / 28.4% / 22.3% | 38.7% | 40.1% | 0.257 |
| 2022/2023 | 292 | 1.551 | 0.918 | 2.469 | 52.4% / 29.1% / 18.5% | 45.2% | 47.9% | 0.370 |
| 2023/2024 | 220 | 1.600 | 0.864 | 2.464 | 56.4% / 24.5% / 19.1% | 46.8% | 43.6% | 0.468 |
| 2024/2025 | 234 | 1.526 | 0.825 | 2.350 | 52.6% / 29.5% / 17.9% | 43.6% | 44.9% | 0.427 |
| 2025/2026 | 292 | 1.599 | 0.818 | 2.418 | 59.6% / 21.9% / 18.5% | 44.5% | 44.5% | 0.438 |
| 2026/2027 | 113 | 1.717 | 0.956 | 2.673 | 61.9% / 20.4% / 17.7% | 52.2% | 52.2% | 0.496 |

Career-pooled chronological split-half, using ratio-of-sums team-match rates,
gives goals-for r=0.410 and goals-against r=0.730 across 21 teams meeting the
six-match-per-half minimum. Event-yellow r is undefined: every event-yellow
value is zero. It is not evidence for a card feature.

Half-time goals are recoverable for 1,332/1,443 matches. The all-match 1H
goal share over recoverable matches is 0.4474. Per-match 1H-share variance
among recoverable matches with at least one goal is 0.1235, which is match
outcome variation rather than a stable frozen constant. No halves constant is
frozen and presentation remains FT-only.

Card coverage is a feed-coverage warning: 570 Card events are all Red or
YellowRed, with no Yellow events. Card totals therefore cannot be treated as
a stable target. Guatemala has no sibling league in the warehouse; no X2
mover count or offset is substituted from another country.

Charts are generated from `eda_summary.json` by `make_charts.py`.
