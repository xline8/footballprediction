# Step 1 — Data understanding: BO-PrimeraDivision

Source: `data_enrichment/fotmob_world_index.csv`, `league_id=144`, with JSON payloads at each index `path`. The scan and builder both retain only `finished == True`; all 1,603 indexed rows are finished and no never-started placeholders were found.

## Inventory

| season | matches | regular | playoff | teams | goals/match | stats / periods | referee named | shotmap / xG |
|---|---:|---:|---:|---:|---:|---|---:|---|
| 2021 | 240 | 240 | 0 | 16 | 3.0625 | 0 / 0 | 0 | 0 / 0 |
| 2022 | 333 | 320 | 13 | 16 | 2.7988 | 0 / 0 | 0 | 0 / 0 |
| 2023 | 272 | 272 | 0 | 17 | 2.7574 | 0 / 0 | 0 | 0 / 0 |
| 2024 | 319 | 304 | 15 | 16 | 2.9781 | 0 / 0 | 0 | 0 / 0 |
| 2025 | 240 | 240 | 0 | 16 | 3.6208 | 240 / 240 | 40 | 0 / 0 |
| 2026 | 199 | 199 | 0 | 16 | 3.0402 | 199 / 199 | 79 | 0 / 0 |

All scores and event feeds are present. The stats era is exactly 2025–2026 (439 rows), and every one has real `All`, `FirstHalf`, and `SecondHalf` period blocks. The inventory includes keys such as `total_shots`, `ShotsOnTarget`, `ShotsOffTarget`, `blocked_shots`, `touches_opp_box`, `big_chance`, `BallPossesion`, `accurate_passes`, `yellow_cards`, `red_cards`, `fouls`, `corners`, `passes`, and `keeper_saves`.

## Format and quirks

Regular is numeric `roundName`; `1/4`, `1/2`, and `final` are playoff rows (13 in 2022 and 15 in 2024). Round numbers run sequentially within the season: 2022 has 1–16 at 16 matches/round then 17–24 at 8; 2024 has 1–8 at 16 then 9–30 at 8. These blocks and dates support the competition structure, but the payload does not justify inventing an Apertura/Clausura label per match.

The event-unified yellow target is `Yellow + YellowRed`. In 2025, stats-feed yellows total 1,324 versus 1,495 event-unified yellows; exact match totals agree in 151/240 matches. Plain Yellow events total 1,431. Event-feed plain Yellow exists only in 2025–2026; earlier seasons have Red/YellowRed only. Event marker checks found 0 incomplete 2025–2026 rows under the builder's Half+Substitution rule. Referee text is empty in 2021–2024 and named in only 40/240 (2025) and 79/199 (2026).

There is no xG key and no non-empty shotmap in any season. There is no Bolivian second-tier corpus in the warehouse, so no parent-tier mover prior is possible.

The 2025 goal rate is a genuine outlier: 3.6208, versus 2.7574–3.0625 in 2021–2024 and 3.0402 in 2026. EDA breaks it down by month, five-round block, and home/away team; the high round-26–30 block is 4.575 goals/match and 2025 home/away means are 2.2583/1.3625. An independent event-vs-score audit reconciles all ordinary matches; the sole exception is awarded match 3777008 (score 0–3, no Goal events), which is retained for score-based goals (its 3 goals are exactly the 2021 event/score gap of 735 vs 732).
