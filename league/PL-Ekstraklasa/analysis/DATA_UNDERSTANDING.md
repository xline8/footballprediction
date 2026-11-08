# Phase 1 — Data Understanding: FotMob Poland Ekstraklasa Warehouse

## 0. Integrity headline

The index contains 1,654 league_id 196 rows and the builder produces 1,654 unique match rows plus 3,308 team-match rows. The season counts are 306, 306, 306, 306, 306, and 124. Every season has 18 teams and 34 rounds in the complete seasons. `general.leagueName` is always `Ekstraklasa` and `parentLeagueId` is always 196.

There is no split or play-off phase in this warehouse era. The phase is frozen as `regular` for every row and no phase feature is permitted. This corrects the programme's initial assumption about an 8+8 split; it is recorded here rather than silently normalised.

## 1. Coverage measured from content

| Season | n | stats All | period splits | referee | box touches | stats xG | shotmap | shotmap xG |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| 2021/2022 | 306 | 100.0% | 0.0% | 72.9% | 0.0% | 0.0% | 0.0% | 0.0% |
| 2022/2023 | 306 | 100.0% | 27.1% | 100.0% | 61.1% | 0.0% | 0.7% | 0.7% |
| 2023/2024 | 306 | 100.0% | 99.7% | 100.0% | 76.8% | 1.3% | 1.3% | 1.3% |
| 2024/2025 | 306 | 100.0% | 100.0% | 100.0% | 100.0% | 2.0% | 2.0% | 2.0% |
| 2025/2026 | 306 | 100.0% | 100.0% | 86.6% | 100.0% | 100.0% | 100.0% | 100.0% |
| 2026/2027 | 124 | 100.0% | 100.0% | 100.0% | 100.0% | 100.0% | 100.0% | 100.0% |

The period-split constants therefore use the complete-splits era 2023/2024–2025/2026, not the partial current season. Stats-feed xG is not equivalent to shotmap availability: shotmap xG is virtually absent until 2025/2026, whereas stats xG has a sparse early tail from 2023/2024. The xG era is consequently labelled in every reliability result.

Poland's I Liga (197, 1,671 rows) and II Liga (8935, 1,679 rows) are present in the warehouse. This build intentionally creates no second-league corpus. Newcomers are identified in-corpus the NL way: teams present in season S and absent in S−1 (three per transition). Their measured first-season gaps are recorded under X2 in FEATURES, but X2 is not consumed by any arm in this build — the goals candidate's pre-registered thin-data mechanism is SHRINK (the BE precedent), and no true tier offset is estimated because no I Liga corpus is built.

## 2. Definition and provenance rules

- FT score: `header.status.scoreStr`.
- HT goals: goal events at `time <= 45`.
- SOT, shots, corners, cards, xG, set-play xG, box touches, possession, and big chances: `content.stats.Periods.All`.
- Shotmap xG and xGOT: regulation shots only; shootout attempts are excluded.
- Referee: `content.matchFacts.infoBox.Referee.text`.
- Unified yellows: stats-feed `yellow_cards` when present, event-feed Yellow fallback when the stats card is absent. Event counts remain in the table for the early cross-check.

The builder nulls score-only payloads rather than converting missing stats to zero. The count targets therefore distinguish absent data from a genuine zero.

## 3. Cards check

Among 1,348 matches carrying both a stats card and an event feed, stats and events agree exactly on total yellows in 83.8%; stats are lower in 12.9%, higher in 3.3%, and the mean difference is −0.158 yellows per match. The maximum absolute difference is 8.0. Including YellowRed events changes exact agreement to 83.2%.

The unified target is the same coherent choice used by the reference leagues: stats-feed yellows, with an events fallback only where the stats card is absent. The sources are not mixed within a match's target definition.
