# Phase 1 — Data Understanding: South Korea K League 3

Source for all measured values below: `analysis/eda_summary.json`. Percentages
are the displayed inventory counts divided by that season's index count.
The warehouse uses calendar-year seasons.

| Season | index | regular | playoff | unplayed | stats | splits | events | referee | shotmap | xG |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 2021 | 214 | 202 | 4 | 8 | 0 (0%) | 0 | 141 (65.9%) | 0 (0%) | 0 | 0 |
| 2022 | 240 | 240 | 0 | 0 | 0 (0%) | 0 | 212 (88.3%) | 0 (0%) | 0 | 0 |
| 2023 | 210 | 210 | 0 | 0 | 0 (0%) | 0 | 187 (89.0%) | 0 (0%) | 0 | 0 |
| 2024 | 240 | 240 | 0 | 0 | 0 (0%) | 0 | 218 (90.8%) | 0 (0%) | 0 | 0 |
| 2025 | 210 | 210 | 0 | 0 | 0 (0%) | 0 | 193 (91.9%) | 0 (0%) | 0 | 0 |
| 2026 | 182 | 182 | 0 | 0 | 0 (0%) | 0 | 169 (92.9%) | 0 (0%) | 0 | 0 |

The played corpus is 1,288 matches: 1,284 regular-season matches and four
2021 playoff matches. The index has 1,296 rows. The eight unplayed 2021
fixtures are IDs `3548124`, `3548130`, `3548133`, `3548134`, `3548135`,
`3548139`, `3548147`, and `3548154`; each is `started=False` with a
placeholder 0–0 score. The regular-season counts are 2021: 202, 2022: 240,
2023: 210, 2024: 240, 2025: 210, and 2026: 182. The 2026 season is in
progress; its last match in the verified corpus is 2026-11-07.

The league has 15, 16, 15, 16, 15, and 14 teams in 2021–2026 respectively
(23 team IDs overall). The 2021 playoff format is QF 1/4 single match, SF
1/2 single match, and a two-legged final. No playoffs appear in the feed for
2022–2026.

Identity is keyed by FotMob team ID. Four IDs carry name variants:

| FotMob ID | observed names |
|---|---|
| 187953 | Gimhae; Gimhae FC 2008 |
| 739791 | Pocheon Citizen FC; Pocheon Citizens FC |
| 739800 | Hwaseong; Hwaseong FC |
| 739810 | Yangju Citizen; Yangju Citizens |

The canonical name is the most frequent observed name.

`content.stats` is null in all 1,296 payloads; shotmaps are empty in all
payloads; lineups are absent in all payloads; and no payload identifies a
referee. The index flags for stats, shotmap, lineup, and period splits are
all false. Thus stats, splits, shotmap, xG, referee, and box-touch data are
not available in this corpus.

There are zero K2→K3 incoming movers in any season 2022–2026. Outgoing K3→K2
movers are Gimpo FC (2022), Cheonan City and Cheongju FC (2023), Hwaseong FC
(2025), and Gimhae FC 2008 (2026). Other entrants are from K4, which is not in
the corpus, or reserve teams (Daegu FC Reserves in 2024 and Jeonbuk Hyundai
Motors FC Reserves in 2025–2026). An X2 mover feature is therefore not
estimable.

The event feed contains goal and red-card lists only. Regular-match goal
events reconcile to the final score in 1,229/1,284 matches; all 55 failures
are early March 2021 matches with empty goal-event lists. Across the corpus,
card events are 57 `YellowRed` and 84 `Red`, with zero plain `Yellow` events.

