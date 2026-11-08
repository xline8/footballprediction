# Data understanding — SLO-PrvaLiga

The source is the FotMob world warehouse, filtered by index `league_id=173` and checked against each payload. The corpus has 956 finished matches from 2021/2022 through partial 2026/2027. Every payload has `general.leagueName=Prva Liga`, `parentLeagueId=173`, a parseable `scoreStr`, and `finished=true`.

## Format and coverage

This is one regular single table. There are 36 rounds and 5 matches per round in complete seasons; no split group or playoff is present. Every season has 10 teams. Match counts are 180, 180, 180, 180, 162, and 74.

`content.stats` is null, `content.shotmap.shots` is empty, and `playerStats` is absent in 956/956 payloads. Referee text is empty in 956/956. Lineup is non-null in 32 payloads. Events are present in 893/956 matches. The event feed contains Goal, Half, and Card types: 2,599 goals, 1,784 halves, 125 Red, 51 YellowRed, and 0 plain Yellow events. There are 63 eventless matches.

| Season | Matches | Model rows | Teams | Dates | Events | Lineup non-null |
|---|---:|---:|---:|---|---:|---:|
| 2021/2022 | 180 | 180 | 10 | 2021-07-16..2022-05-22 | 166 | 0 |
| 2022/2023 | 180 | 180 | 10 | 2022-07-15..2023-05-20 | 165 | 0 |
| 2023/2024 | 180 | 178 | 10 | 2023-07-22..2024-05-19 | 171 | 5 |
| 2024/2025 | 180 | 180 | 10 | 2024-07-19..2025-05-25 | 171 | 0 |
| 2025/2026 | 162 | 161 | 10 | 2025-07-18..2026-05-23 | 155 | 21 |
| 2026/2027 | 74 | 74 | 10 | 2026-07-17..2026-11-08 | 65 | 6 |

## Quirk register

- 2025/2026 has 162 matches: Domzale played 18 matches, every other team 34; rounds 19–36 have 4 matches. The payloads do not state a reason.
- Three awarded matches are retained with `is_awarded=1` and excluded from every fit and score: 4206754, 4206847, and 4834588.
- Goal-event counts reproduce official scores for all non-awarded matches. The time `<=45` first-half rule agrees with the HT marker in 893/893 eventful payloads; 51 goals sit at minute 45 with overload time.
- The complete Slovenia index contains only league ID 173, so no sibling league is available for an X2 mover prior. Team name and ID mapping has no variants across 15 distinct team IDs.
