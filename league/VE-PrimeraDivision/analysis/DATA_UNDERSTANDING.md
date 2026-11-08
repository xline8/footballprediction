# Step 1 — Data understanding: VE-PrimeraDivision

Source: `data_enrichment/fotmob_world_index.csv`, `league_id=339`, with JSON payloads at each indexed path. The builder retains the 1,497 finished matches in seasons 2021–2026.

## Inventory

| season | matches | regular / playoff | teams | stats | period splits | referee named | shotmap / xG |
|---|---:|---:|---:|---:|---:|---:|---:|
| 2021 | 303 | 252 / 51 | 21 | 0 | 0 | 0 | 0 / 0 |
| 2022 | 277 | 240 / 37 | 16 | 0 | 0 | 0 | 0 / 0 |
| 2023 | 223 | 210 / 13 | 15 | 0 | 0 | 0 | 0 / 0 |
| 2024 | 234 | 182 / 52 | 14 | 0 | 0 | 0 | 0 / 0 |
| 2025 | 233 | 182 / 51 | 14 | 117 | 62 | 87 | 0 / 0 |
| 2026 | 227 | 182 / 45 | 14 | 226 | 226 | 145 | 0 / 0 |

Stats exist only from Clausura 2025 onward. Period splits are partial in the 2025 Clausura first stage and complete except the awarded 2026 match. The 2025 stats feed has two tiers: 62 matches carry the full feed (all stat groups + period splits) while 55 carry only `Periods.All` / 'Top stats' (possession, total shots, SOT, corners) — so yellows, fouls, reds, passes and keeper saves exist in only 288 of the 343 stats-era matches. 2021 contains COVID-era regional groups; Apertura/Clausura naming begins in 2024. 2026 has two disjoint league-name spellings (`Primera División` and `Venezuela Primera División`) for the same league id and is in progress.

The shotmap is empty for every match and no `expected_goals` stat key occurs. Stat keys observed in the stats era include total shots, SOT, shots off target, blocked shots, big chances, possession, accurate passes, yellow/red cards, fouls, corners, passes, keeper saves, and inside/outside-box shots. Two awarded matches are retained by final score: 3575291 and 1000018666.

The event card feed is broken before 2026 and overcounts stats yellows in 2026. Referee coverage is not adequate for a multi-season reliability check; the payload scan finds 87 named referees in 2025 and 145 in 2026.
