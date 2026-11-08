# Phase 1 — Data Understanding: FotMob Poland I Liga

## Inventory

The index contains 1,671 league_id 197 rows. The builder produces 1,671 unique match rows and 3,342 team-match rows. Complete seasons contain 309 rows: 306 regular matches and 3 promotion-playoff matches. 2026/2027 contains 126 regular rows. Team identity is the FotMob team id, not the display name; diacritic variants such as Lechia Gdansk/Lechia Gdańsk and Miedz Legnica/Miedź Legnica are the same club when the id is the same.

The competition is an 18-team, 34-round regular season followed by promotion playoffs: round 1/2 has semi-finals and round final has the final. The warehouse calendar is approximately July–May.

## Coverage

| Season | n | regular | playoff | teams | goals | home | away | events | HT goals |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 2021/2022 | 309 | 306 | 3 | 18 | 2.492 | 1.33 | 1.162 | 92.6% | 92.6% |
| 2022/2023 | 309 | 306 | 3 | 18 | 2.654 | 1.437 | 1.217 | 94.8% | 94.8% |
| 2023/2024 | 309 | 306 | 3 | 18 | 2.663 | 1.482 | 1.181 | 93.5% | 93.5% |
| 2024/2025 | 309 | 306 | 3 | 18 | 2.709 | 1.421 | 1.288 | 93.9% | 93.9% |
| 2025/2026 | 309 | 306 | 3 | 18 | 2.981 | 1.599 | 1.382 | 96.1% | 96.1% |
| 2026/2027 | 126 | 126 | 0 | 18 | 2.698 | 1.5 | 1.198 | 96.8% | 96.8% |

Stats coverage is 0.0%, shotmap coverage is 0.0%, and referee coverage is 0.0%. Events coverage is 94.4% overall. There is no yellow-card source: Card events are only Red and YellowRed; no plain Yellow event exists anywhere in this league warehouse. Feed quirk: YellowRed counts collapse from 2025/2026 (49 Red / 1 YellowRed, vs 44 / 24 in 2024/2025) — second yellows appear reclassified as plain Red from that season, so even the Red/YellowRed split is not comparable across the 2025 boundary; only the Red+YellowRed total is a stable descriptive.

## Provenance

FT scores come from the finished-match header, with the index score as fallback. HT goals come from Goal events at time <= 45 and are null when there is no events block. All stat-derived columns remain null. Team rows are keyed by team id and carry goals only.

