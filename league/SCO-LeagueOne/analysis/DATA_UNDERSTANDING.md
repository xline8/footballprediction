# Phase A — Data Understanding: SCO League One

All counts in this document are from `inventory_summary.json`; descriptive levels are from `eda_summary.json`. The warehouse contains 969 regular-season matches: 180 in each of 2021/2022–2025/2026 and 69 in 2026/2027 (rounds 1–14 in progress). There are 10 teams, 36 rounds, and five matches per round in each complete season. There are no play-off rows.

| season | matches | stats content | events | usable referee | lineups |
|---|---:|---:|---:|---:|---:|
| 2021/2022 | 180 | 0 | 180 | 0 | 180 |
| 2022/2023 | 180 | 0 | 180 | 0 | 176 |
| 2023/2024 | 180 | 0 | 180 | 0 | 180 |
| 2024/2025 | 180 | 0 | 180 | 0 | 180 |
| 2025/2026 | 180 | 0 | 180 | 0 | 180 |
| 2026/2027 | 69 | 0 | 69 | 0 | 69 |

All 969 scores reconcile with event goal totals. Events are present in all 969 rows. Shotmap shots are 0/969. Stats `Periods` content is 0/969, so SOT, corners, total shots, possession, big chances, touches, and xG do not exist for this corpus. The referee field is present but empty in all 969 payloads.

There are 22 team IDs. ID 4130 has the display-name alias “Edinburgh City” / “FC Edinburgh”; all analysis keys on team ID, never display name.
