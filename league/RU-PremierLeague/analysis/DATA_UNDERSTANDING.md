# Phase 1 — Data Understanding: Russia Premier League

All counts and coverage below are generated from `eda_compute.py` and `eda_numbers.json`.

## Inventory and format

The build contains 1,312 unique played matches and 2,624 team-perspective rows. Each season has 16 teams. Complete seasons contain 240 matches and 30 matches per team; 2026/2027 has 112 matches and 14 matches per team at this pull. Every row has `phase=regular`; there are no extra phase fields or evidence of a split/play-off phase. Team turnover is measured in `movers` in the JSON: 12 season-entry newcomers total.

| season | matches | teams | stats All | split periods | referee | xG | set-play xG | box touches | shotmap |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 2021/2022 | 240 | 16 | 100.0% | 0.4% | 40.0% | 0.4% | 0.4% | 67.9% | 0.4% |
| 2022/2023 | 240 | 16 | 100.0% | 33.8% | 100.0% | 0.0% | 0.0% | 47.1% | 0.0% |
| 2023/2024 | 240 | 16 | 100.0% | 100.0% | 87.1% | 0.0% | 0.0% | 71.2% | 0.0% |
| 2024/2025 | 240 | 16 | 100.0% | 100.0% | 97.1% | 4.6% | 4.6% | 100.0% | 4.6% |
| 2025/2026 | 240 | 16 | 100.0% | 100.0% | 70.4% | 100.0% | 100.0% | 100.0% | 100.0% |
| 2026/2027 | 112 | 16 | 100.0% | 100.0% | 100.0% | 100.0% | 100.0% | 100.0% | 100.0% |

SOT, corners, total shots, stats yellows, stats reds, possession, and big chances are complete in All in every season. Period-split coverage is partial in 2022/2023 and complete from 2023/2024. Referee text is notably incomplete in 2021/2022 and also varies in later seasons.

The xG inventory confirms the virgin-era rule operationally: the full 2025/2026 and 2026/2027 seasons have coverage; 11 2024/2025 rows carry the stray shotmap/xG payload, plus one older anomalous payload. These rows are retained and explicitly era-limited, not silently reclassified.

## Provenance

Scores come from the finished header. Stats All and period values come from `content.stats.Periods`; first-half corners use key `corners`. Event yellows are `Card/Yellow + Card/YellowRed`, with YellowRed also counted as a red; stats yellows remain separate. Shotmap aggregates exclude shootout attempts. Referee text comes from the info box. Missing values remain null.

