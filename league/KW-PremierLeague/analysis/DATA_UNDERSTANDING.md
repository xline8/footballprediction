# KW-PremierLeague — Data Understanding (Step 1)

League: Kuwait Premier League (tier 1), FotMob league_id 529.
Warehouse: `data_enrichment/fotmob_world/Kuwait/Premier League/`
(release `bundle-kw-premier`; tar extracted to
`data_enrichment/Kuwait/Premier League/` in this workspace).
Index: `index_529.csv` (711 rows for league 529).

## What the data is

One JSON per index row (711 files, 0 missing vs the index), one row
per match in FotMob's world warehouse, seasons labelled 2021 …
2026/2027. `coverageLevel` is `lower` for all 711. The feed is
**scores-only in the strongest sense**:

- stats feed (`content.stats.Periods`): present in **0/711** matches,
  every season (2021: 0/90 … 2026/2027: 0/45).
- shotmap: **0/711**. lineup: **0/711**. referee named: **0/711**.
- No `expected_goals*` key exists anywhere (xg_rows = 0 per season).
- Event feed (`matchFacts.events`): exists only from 2024/2025 —
  0 event matches in 2021, 2021/2022, 2022/2023, 2023/2024;
  87/111 in 2024/2025; 105/111 in 2025/2026; 45/45 in 2026/2027.
  Where events exist they are exact: **0 score mismatches** in 237
  event matches; but card events exist only as **Red** (53 in the
  whole corpus) — plain Yellow and YellowRed events are **zero in
  every season**.

## The dual 2021 / 2021/2022 labels (BRIEF caution — resolved)

The 90 rows labelled "2021" and the 90 labelled "2021/2022" are
**not the same matches twice**: match ids are fully disjoint
(0 overlap), date ranges are disjoint (2021: 2021-01-21 → 2021-05-17;
2021/2022: 2021-11-19 → 2022-04-25), and the team sets differ by the
usual 2 promoted/relegated clubs. Kuwait played a calendar-year
season in early 2021, then switched to a split season starting
November 2021. Both labels are real, distinct seasons; the canonical
order is 2021 < 2021/2022 < 2022/2023 < 2023/2024 < 2024/2025 <
2025/2026 < 2026/2027. Full decision record in PREPROCESSING.md.

## Played vs indexed

Only **642 of the 711 index rows were actually played**
(`header.status.finished=true`). 69 rows are fixtures that never
started (`started=false`, no header score, index score is the
placeholder "0-0"): 26 in 2021, 21 in 2021/2022, 12 in 2022/2023,
10 in 2023/2024, 0 from 2024/2025 on. The BRIEF's "711 played" is the
index row count. Played per season: 64 / 69 / 120 / 122 / 111 / 111 /
45 (= 642). Only played matches enter the corpus.

## Format facts

- 10 teams per season in every dev season and the virgin; 12 in the
  reserve 2026/2027 (in progress, 45 played). 14 distinct FotMob
  team ids over the corpus, each with exactly one name spelling.
- Phases from `general.leagueName` (ordinary rows, phase flag only):
  `main` (Premier League), `championship` (Championship Group),
  `relegation` (Relegation Group). Championship/relegation groups
  exist in 2022/2023 (25/9 played), 2023/2024 (30/12), 2024/2025
  (15/6) and the virgin (15/6); none in 2021 or 2021/2022.
- One awarded match: 4067510 (2022/2023, Al-Jahra 0–3 Al-Tadhamon),
  kept as an ordinary row with `awarded=true`; header score used.
- Scoring level is high and fairly stable in dev: goals/match 3.06 /
  2.93 / 3.27 / 3.03 / 3.21 (2021 → 2024/2025). OU2.5 over-rate
  0.52–0.63 per dev season.

## Split (per BRIEF, frozen in the prereg)

- Warm-up: 2021 (n=64 played).
- Dev scored: 2021/2022–2024/2025 (n=422 played).
- Virgin: 2025/2026 (n=111 played, complete season) — read once,
  only for dev-passing arms.
- Reserve: 2026/2027 (n=45, in progress) — untouched.
