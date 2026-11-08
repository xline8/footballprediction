# Data understanding — Wales Cymru Premier

## 0 Integrity headline

The inventory rebuild finds 1,103 index rows, 1,103 payload files, 1,103 unique IDs, all finished and none awarded. Goal events reproduce the stored score in 1,103/1,103. There are 1,042 matches with a Half@45 event and 61 eventless matches, all 0–0; HT is therefore derivable for all 1,103. The payload is scores-only: `content.stats` is null 1,103/1,103, shotmap shots are present in 0/1,103, lineups are null in 1,103/1,103, referee text is non-empty in 0/1,103, and coverage is `lower` in 1,103/1,103.

There are 234 card events: Red 154, YellowRed 80, plain Yellow 0. The parent league ID is 116 in 1,103/1,103; `general.leagueId` and tournament IDs are season/phase IDs, not 116.

## 1 Payload anatomy

`general`/`header.status` supplies IDs, names, finish state and `scoreStr`; `content.matchFacts.events.events` supplies goals, cards and Half@45; `infoBox.Tournament` supplies round, phase name and parent ID. No stats, shotmap, lineup or referee feature is available.

## 2 Coverage by season

| season | rows | eligible | events | HT | stats all/half | shotmap | lineup | referee |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| 2021/2022 | 195 | 192 | 183 | 195 | 0/0 | 0 | 0 | 0 |
| 2022/2023 | 195 | 192 | 185 | 195 | 0/0 | 0 | 0 | 0 |
| 2023/2024 | 195 | 192 | 186 | 195 | 0/0 | 0 | 0 | 0 |
| 2024/2025 | 196 | 192 | 184 | 196 | 0/0 | 0 | 0 | 0 |
| 2025/2026 | 195 | 192 | 179 | 195 | 0/0 | 0 | 0 | 0 |
| 2026/2027 | 127 | 127 | 125 | 127 | 0/0 | 0 | 0 | 0 |

## 3 Calendar and format

Rounds 1–22 are the 12-team Premier League (132 matches/season); rounds 23–32 split into Championship and Relegation groups, 30 each. There are 16 playoff rows: nine ECL Playoff rows in 2021/22–2023/24 and seven CL Playoff rows in 2024/25–2025/26. In 2026/27 Wales expanded to 16 clubs: 30 home-and-away matches then a three-way 6/4/6 split, producing 33–35 matches. This expansion and the six promoted/two relegated places are documented by FAW, *The New Structure*.

## 4 Targets absent

SOT, corners, total shots, xG, xGOT, box touches, possession, big chances and usable yellow targets are absent (all stats/shotmap counts are 0/1,103; plain Yellow events are 0).

## 5 Quirks and exceptions

- Playoffs are retained for audit but excluded from fitting/scoring. Match `3873043` (Caernarfon–Flint Town United) is the AET-score anomaly: Half@90 is 0–0 and goals occur at 99, 105 and 120; stored 2–1 is after extra time. Six playoff matches have `Pen` reasons.
- Names are keyed by stable FotMob ID. Rename IDs: 7852 TNS/The New Saints; 321094 Pontypridd Town/Pontypridd United; 560953 Cardiff Met University/Cardiff Met FC.
- Incoming clubs by season are recorded in `eda_numbers.json`; no development/virgin team has 1–5 prior in-league matches, so SHRINK is structurally a no-op.

All measured inventory output is in `inventory_summary.json`.
