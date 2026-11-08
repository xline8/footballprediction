# Phase A2 — Data Understanding: China Super League

Corpus: 1,442 finished FotMob match rows (league id 120), seasons 2021–2026,
with one long team-match row per club and match. The 2026 season is complete
through 2026-11-08. The source inventory and coverage are frozen in
`inventory_summary.json`.

## Format and scope

| Season | Matches | Teams | Format | Dates |
|---|---:|---:|---|---|
| 2021 | 176 | 16 | two 8-team groups, then championship/relegation playoffs | 2021-04-20–2022-01-04 |
| 2022 | 306 | 18 | double round-robin | 2022-06-03–2022-12-31 |
| 2023 | 240 | 16 | double round-robin | 2023-04-15–2023-11-04 |
| 2024 | 240 | 16 | double round-robin | 2024-03-01–2024-11-02 |
| 2025 | 240 | 16 | double round-robin | 2025-02-22–2025-11-22 |
| 2026 | 240 | 16 | double round-robin | 2026-03-06–2026-11-08 |

The 2021 phase labels are retained in every row. They are descriptive, not a
model feature: from 2023 onward every season is an ordinary 16-team
double round-robin, and the 2021 group/playoff structure is excluded by the
era restriction rather than by a phase filter.

## Payload and coverage

Official scores and events are complete in 2021, 2023–2026; 2022 has 97.39%
event/stats coverage and 8 rows without stats. Total shots, SOT, corners,
raw stats-feed cards, fouls, possession, and half splits are complete from
2023 onward. xG and shotmap are absent everywhere. Referee coverage is
99.43%, 97.39%, 97.08%, 92.08%, 64.58%, and 48.75% by season.

The builder keys teams by stable id. Examples of harmless display-name
changes are Wuhan FC/Wuhan Yangtze River, Cangzhou Mighty Lions F.C./F.C.,
and Henan FC/Henan Songshan Longmen.

## Modelling consequence

The fit era is 2023+. Goals use 2023 as seed, 2024–2025 as scored dev, and
2026 as the virgin season. Stats markets warm up on 2023, score 2024–2025
(480 matches), and read the complete 2026 virgin (240 matches). No model is
fit in this phase.
