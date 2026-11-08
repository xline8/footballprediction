# Step 1 — Data Understanding: Bulgaria Second Professional League (BG-SecondLeague)

Source: FotMob world warehouse, league_id **9096**, index rows **1,735**.

## Inventory
| Season | Index rows | Finished (CSV) | Teams | Note |
|---|---|---|---|---|
| 2021/2022 | 342 | 329 | 19 | 13 index rows are not finished in their payloads (unplayed/abandoned) — excluded, see PREPROCESSING |
| 2022/2023 | 306 | 306 | 18 | |
| 2023/2024 | 306 | 306 | 19 | |
| 2024/2025 | 380 | 380 | 20 | league expanded |
| 2025/2026 | 272 | 272 | 17 | league contracted — **virgin window (complete)** |
| 2026/2027 | 129 | 129 | 18 | in progress at pull — reserved confirmatory, NOT read |

## Field coverage (all seasons, verified per-file, not index flags alone)
- **FT score: 1,722/1,722 finished matches.** The only real target.
- **Stats feed (`content.stats`): 0 / 1,735 — `None` in every payload.** No SOT, no corners, no cards-from-stats, no total shots, no xG.
- **Shotmap: 0 / 1,735** — the `shots` list is empty in every payload.
- **Period splits: 0%.** No FirstHalf/SecondHalf blocks exist. No halves constant can be measured; goals presentation is **FT-only**.
- **Referee: 0 / 1,722** — `infoBox.Referee.text` is empty everywhere.
- **Events: 1,213 / 1,722 (70%)** carry an event list (goals/cards incidents), but with no stats feed this is not a settlement-grade cards target and the program does not build a market on event lists alone (see MODEL_DESIGN feasibility matrix).
- Coverage level is "lower" throughout.

## Calendar / format
Bulgarian split-year seasons (Jul–May), single round-robin-plus format with
promotion to the First Professional League (id 270, also in the warehouse)
and relegation below. Team count varies 17–20 across seasons (expansion
2024/2025, contraction 2025/2026) — team identity is keyed by FotMob team
id throughout. All matches in the CSV are treated as ordinary league
matches; no playoff phase is separated in the payloads.
