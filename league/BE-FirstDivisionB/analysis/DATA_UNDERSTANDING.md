# Phase A — Data Understanding: BE-FirstDivisionB

The builder reads FotMob league_id 264 from the main warehouse index and writes one row per finished match. All identities are FotMob team IDs.

| Season | Matches | Teams by ID | Stats / half / shotmap / events / referee |
|---|---:|---:|---|
| 2021/2022 | 112 | 8 | 0.0% / 0.0% / 0.0% / 96.4% / 0.0% |
| 2022/2023 | 192 | 12 | 0.0% / 0.0% / 0.0% / 95.3% / 0.0% |
| 2023/2024 | 246 | 16 | 0.0% / 0.0% / 0.0% / 95.9% / 0.0% |
| 2024/2025 | 216 | 15 | 0.0% / 0.0% / 0.0% / 95.8% / 0.0% |
| 2025/2026 | 278 | 17 | 99.6% / 99.6% / 99.6% / 99.6% / 83.8% |
| 2026/2027 | 70 | 15 | 100.0% / 100.0% / 100.0% / 100.0% / 91.4% |

The built CSV has 1,114 unique played matches and 2,228 team-match rows. The 2025/2026 stats era has one stats-less match (277/278). The dev era has no stats feed or shotmap.

## Format and phases

2021/2022 is 8 teams and 112 matches. 2022/2023 is 132 regular + 30 promotion group + 30 relegation group. 2023/2024 is 240 regular + 6 promotion playoff. 2024/2025 is 210 regular + 6 promotion playoff. 2025/2026 has 278 regular matches and FotMob renames 251 rows to “Belgian Challenger Pro League”; 27 remain “First Division B”. 2026/2027 mixes the labels (37/33) and is reserved.

All phases are ordinary rows; the phase flag is descriptive only.

2024/2025 quirk (coordinator-verified): Deinze appears in ZERO
2024/2025 rows. The club's fixtures and results were expunged from
the feed after its December 2024 bankruptcy; the season's 210
regular matches across 15 team IDs are the post-expungement record,
taken as-is.

## Reserve IDs

The frozen ID list is 1173026 Club Brugge NXT; 1378461 Anderlecht Futures; 1378462 SL 16 FC; 1378463 Genk U23; 1379188 Gent U23. Name variants are never used for logic.

Event coverage is approximately 95–96% in the dev era and 100% in the confirmatory season. Cards are sparse in the dev era and dense in the stats era. Referee text exists only in the stats era. The builder fabricates no missing targets.

