# Phase A — Data Understanding: SCO Championship

All counts below are taken from `inventory_summary.json` and the generated EDA artefacts. The build contains 969 matches: 180 in each of 2021/2022 through 2025/2026 and 69 in 2026/2027. Each complete season has 10 teams, quadruple round-robin scheduling, and 36 rounds.

| season | matches | stats All | events | referee |
|---|---:|---:|---:|---:|
| 2021/2022 | 180 | 180 | 180 | 84 |
| 2022/2023 | 180 | 173 | 180 | 180 |
| 2023/2024 | 180 | 172 | 180 | 180 |
| 2024/2025 | 180 | 82 | 180 | 180 |
| 2025/2026 | 180 | 177 | 180 | 180 |
| 2026/2027 | 69 | 29 | 69 | 69 |

There are no play-off rows (`playoff_rows=0`). Seasons end between 29 April and 5 May; play-offs fall outside this feed. Therefore `phase=regular` for every row and the phase definition is frozen.

Stats-target coverage (`All` plus corners) is 180/173/172/82/177/29 by season. The exact missing pattern is: 2022/2023 rounds 1, 4 and 9 (7 matches); 2023/2024 has 8 matches in rounds 28–34 on 9–19 April 2024, with the All period present but the corners key absent; 2024/2025 has a contiguous 98-match outage across rounds 9–28 from 12 October 2024 to 11 March 2025; 2025/2026 has 3 missing matches; and 2026/2027 is missing from round 7 onward (39 matches). The full match-level lists remain in `inventory_summary.json`.

The available stats keys are `BallPossesion`, `ShotsOnTarget`, `corners`, and `total_shots`; only 19 matches in 2021/2022 have the richer key set and period splits. There is no xG and no shotmap (`0/969`). Events are present in all 969 matches. Referee coverage is 84/180 in 2021/2022 and 100% thereafter.

There are 20 team IDs. Team ID 8066 appears under both “Inverness CT” and “Inverness Caledonian Thistle”; analyses key on IDs, never display names. The feed's `total_shots` sums to about 15 per match in this league. That feed definition is retained consistently across eras and is the target scale.
