# Phase 1 — Data Understanding: South Korea K League 1

Corpus: FotMob World Warehouse, index filtered to `league_id=9080`.
Measured corpus: 1,350 finished matches: 228 in each of 2021–2025 and 210
in partial 2026. The builder uses FotMob team IDs and does not fit models.

| Season | n | stats block | period splits | events | referee | shotmap | xG in stats | box touches |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| 2021 | 228 | 167 (73.2%) | 0 | 228 (100%) | 118 (51.8%) | 0 | 0 | 0 |
| 2022 | 228 | 228 (100%) | 0 | 228 (100%) | 41 (18.0%) | 228 (100%) | 228 (100%) | 124 (54.4%) |
| 2023 | 228 | 228 (100%) | 205 (89.9%) | 228 (100%) | 118 (51.8%) | 228 (100%) | 228 (100%) | 171 (75.0%) |
| 2024 | 228 | 228 (100%) | 227 (99.6%) | 228 (100%) | 104 (45.6%) | 218 (95.6%) | 227 (99.6%) | 227 (99.6%) |
| 2025 | 228 | 228 (100%) | 228 (100%) | 228 (100%) | 64 (28.1%) | 228 (100%) | 228 (100%) | 228 (100%) |
| 2026 | 210 | 210 (100%) | 206 (98.1%) | 210 (100%) | 79 (37.6%) | 206 (98.1%) | 206 (98.1%) | 206 (98.1%) |

Stats-block coverage counts the warehouse `Periods.All` placeholder in 2021;
individual measures remain missing when that block is null. xG begins in
2022. The apparent 13–14 team names in 2021–2023 are ID aliases: 133896 is
Ulsan Hyundai/Ulsan HD FC and 133898 is Jeju United/Jeju SK.

Scores use `header.status.scoreStr`; events contain goals/cards; stats contain
full and available half measures; shotmaps contain regulation shots and xG.
Rounds >=34 are `phase=split`, but remain ordinary matches for modelling.

Frozen windows: dev 2021–2024 (912), virgin complete 2025 (228), and
confirmatory partial 2026 (210), reserved and not read in this build.
K League 2 (`league_id=9116`) has index rows 182, 222, 236, 236, 275, and
256 in 2021–2026. Every identified 2022–2026 mover has a matching ID in the
prior K2 payloads, making an in-corpus X2 offset feasible.
