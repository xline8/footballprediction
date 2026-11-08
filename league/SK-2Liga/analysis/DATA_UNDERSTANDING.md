# Step 1 — Data Understanding (SK-2Liga, Slovakia 2. Liga, FotMob id 8973)

Source: FotMob world warehouse, index
`data_enrichment/fotmob_world_index.csv` filtered to `league_id = 8973`;
payloads at `data_enrichment/fotmob_world/Slovakia/2. Liga/<season>/<id>.json`
in the main repo (the worktree does not carry the warehouse; the builder
reads it by absolute path). Builder: `data/build_data.py` (ported from the
SK-1Liga builder; the payload shape is identical).

## Inventory

- 1,269 index rows: seasons 2021/2022–2026/2027 (240 / 240 / 240 / 182 /
  240 / 127 rows). Finished: 1,143. Unfinished: 126 — all warehouse pull
  gaps (see defect 1).
- Format (verified from the payloads, `general.leagueName` /
  `leagueRoundName`): a single round-robin league, rounds 1–30, no
  split groups, no championship/relegation phase, no play-off ties.
  16 clubs / 30 rounds in every complete season except 2024/2025,
  which has 14 clubs / 26 rounds (182 rows, all finished).
- FotMob id structure (verified from payloads, NOT the index label):
  `parentLeagueId = 8973` in ALL 1,269 payloads; the per-season
  `leagueId` rotates (8973 for nearly all rows in 2021/2022–
  2022/2023, plus 3 rows 874252 and 5 rows 880279; 886311 dominant
  in 2023/2024 with 160 of 231 finished rows still carrying 8973;
  893335 in 2024/2025, 901093 in 2025/2026, 938006 in 2026/2027,
  exclusively). These are FotMob's seasonal competition ids under the
  one parent — the AU-Championship trap (a parent id hiding several
  real competitions) does NOT apply here: every payload is round
  1–30 of the same 2. Liga. No split is needed; the build keeps the
  sub-league id per row for traceability only.

## Field coverage (per season, all rows)

| Season | Rows | Finished | Stats | Period splits | Referee named | xG | Shotmap | Events |
|---|---|---|---|---|---|---|---|---|
| 2021/2022 | 240 | 163 | 0 | 0 | 0 | 0 | 0 | 0 |
| 2022/2023 | 240 | 200 | 0 | 0 | 0 | 0 | 0 | 0 |
| 2023/2024 | 240 | 231 | 0 | 0 | 0 | 0 | 0 | 156 |
| 2024/2025 | 182 | 182 | 0 | 0 | 0 | 0 | 0 | 177 |
| 2025/2026 | 240 | 240 | 0 | 0 | 0 | 0 | 0 | 230 |
| 2026/2027 | 127 | 127 | 0 | 0 | 0 | 0 | 0 | 47 |
| **Total** | **1,269** | **1,143** | **0** | **0** | **0** | **0** | **0** | **610** |

- The index `has_stats` flag is False for all 1,269 rows and this
  time the flag is right: `content.stats` is empty/absent in every
  payload (verified by reading all of them, not by trusting the
  flag). `content.shotmap.shots` is empty in all 1,269. Lineup is
  present in exactly 1 payload.
- Events (goal times, in `header.events` and identically in
  `content.matchFacts.events.events`) exist in 610 finished matches
  and in no others; the two sources are present in exactly the same
  matches and agree with each other. Event goal totals reconcile
  with `header.status.scoreStr` in 608/610 (defects 2–3).
- `coverageLevel` is `lower` in all 1,269 payloads.

## Defects and quirks (all verified against the payloads)

1. **126 unfinished rows are stale pre-match snapshots, not
   cancelled matches.** They carry old dates (e.g. round 1,
   2021-07-24), `started = false`, `finished = false`,
   `cancelled = false`, and a 0–0 placeholder score. They scatter
   across rounds (2021/2022: 77, incl. all 8 of round 29;
   2022/2023: 40; 2023/2024: 9) and vanish entirely from 2024/2025
   onward (0 unfinished in 2024/2025, 2025/2026 and 2026/2027).
   The warehouse pulled these payloads before kickoff and never
   refreshed them. Inclusion rule (Step 2) drops them. The 2021/2022
   seed season is only 163/240 finished — including round 29, which
   is entirely missing (8/8 unfinished) — which thins the training
   seed (see EDA F1).
2. **Two event blocks disagree with the FT score** (header.events /
   matchFacts events; the score itself is consistent everywhere
   else). 4553752 (2024/2025, score 3–0): the event block lists 2
   *away* goals — a stale/wrong block. 4838232 (2025/2026, score
   4–1): Arevalo's 67' goal is listed twice (6 events vs 5 goals).
   Both matches are kept for goals and excluded from the halves
   computation only (608 reconciled events matches remain).
3. **Events coverage is per-match, not a date cutover.** In
   2023/2024 the 75 finished matches without events scatter across
   the whole season (2023-07-28 → 2024-05-04). In the in-progress
   2026/2027 events stop after 2026-08-31 (47 present, 80 absent)
   — a pull-timing artefact of the in-progress season, not a feed
   change. Halves constants use reconciled-events matches only.
4. **No stats-feed anything, ever.** There is no SOT / corners /
   cards / total-shots / possession / xG target in any season, dev
   or virgin. The league is score-only: S-SK2, C-SK2, K-SK2 and
   T-SK2 are not buildable (Step 6 records each as NOT BUILDABLE
   on data absence, not on a failed gate).
5. **No referee names, ever.** `infoBox.Referee.text` is empty in
   all 1,143 finished matches. X8 is untestable (see FEATURES).
6. **Team display names are unstable; ids are stable.** 11 team
   ids carry diacritic variants in the payloads (e.g. 575079
   `Namestovo` / `Námestovo`, 10184 `FC Petrzalka 1898` /
   `FC Petržalka 1898`, 8010 `Tatran Presov` / `Tatran Prešov`).
   All logic keys on FotMob team ids; 16 distinct ids per season
   (14 in 2024/2025). Canonical name = most recent payload string
   per id.
7. **2024/2025 is a short season, not a data gap.** 14 clubs, 26
   rounds, 182 rows, all finished — the competition itself shrank
   that season (and returned to 16 clubs / 30 rounds in 2025/2026).
   No rounds are missing; the season is used whole in dev.
8. **2026/2027 levels are not comparable** (127 matches, rounds
   1–16 of an in-progress season, goals 2.96/match so far). The
   season is inventory only in this build and is never read by any
   harness.
