# Step 1 — Data Understanding: SG-PremierLeague

Singapore Premier League (tier 1), FotMob league_id 461. 555 played
matches in the bundle index (`index_461.csv`, 555 rows). Warehouse
mirror:
`data_enrichment/fotmob_world/Singapore/Premier League/<season>/<match_id>.json`.

## Format

- Single group every season: 8 teams in 2021 (84 matches), 2022
  (112) and 2025/2026 (84); 9 teams in 2023 (108) and 2024/2025
  (144); 8 teams in 2026/2027 (23 in the bundle, season in
  progress). No championship / relegation split inside a season;
  every row is an ordinary row with phase flag `main`, never
  filtered.
- Season structure changes mid-corpus: 2021–2023 are calendar-year
  seasons; from 2024/2025 the league runs split seasons
  (2024/2025, 2025/2026, 2026/2027). Season labels are carried as
  published; `_yr()` (start year) is used only for era bookkeeping.
- 9 distinct FotMob team ids over the corpus, all 9 appear in the
  dev era. Membership is very stable: the only dev-era entrant is
  Brunei DPMM returning in 2023 after two seasons out (see EDA F4).

## Identity / naming

- `general.leagueName` is `"S.League"` in 2021–2022 (196 matches)
  and `"Premier League"` from 2023 on (359 matches) — a rename of
  the same competition, not a different league; the index carries
  "Premier League" for all rows. `coverageLevel` is `"lower"` for
  all 555 matches; `parentLeagueId` is 461 throughout.
- All logic keys by FotMob team id. One id carries two names:
  67377 appears as "FC Jurong" and "Albirex Niigata FC" (the
  renamed satellite club) — 10 published names over 9 ids. Team
  names in the CSVs are as published per match; the engine keys
  by id.

## Feeds (measured, `eda_summary.json` / `inventory_summary.json`)

- **Stats feed: 0/555 matches in every season.** `content.stats`
  carries no non-empty `Periods` anywhere. No xG, no SOT, no
  corners, no shots, no yellows from stats. Period splits: 0.
  This is a **scores-only league** — confirmed, not assumed
  (BRIEF said the same; step 1 verified it from the raw JSONs).
- **Shotmap: 0/555.** No xG anywhere.
- **Events: 543/555** (2021: 82/84, 2022: 110/112, 2023: 108/108,
  2024/2025: 140/144, 2025/2026: 82/84, 2026/2027: 21/23). The 12
  matches without events are ALL scoreless (0 goals between them,
  every one a 0-0) — so event goals are complete for the dev era:
  event-derived goal counts agree with the header score in all
  555 matches (0 score/events mismatches).
- **Lineups: 0 in every dev season** (0/448); 84/84 in the virgin
  and 23/23 in the reserve. Not used by any candidate.
- **Referee: named in 0 matches in every dev season and in the
  virgin** (0/532); 13/23 only in the untouched reserve. X8 is
  impossible in the dev era by data absence.
- Event feed carries **zero plain Yellow card events in all 555
  matches** (only YellowRed and Red) — see EDA F5.

## Scores

- Goals/match by season: 3.976 / 4.518 / 4.185 / 4.257 (dev
  2021–2024/2025), 3.607 in the virgin 2025/2026, 3.478 in the
  reserve 2026/2027. This is the highest-scoring league in the
  program so far: OU2.5 over-rate 0.74–0.79 every season; home-win
  rate 0.39–0.45; draw rate low, 0.11–0.24.
- Total goals in corpus: 2,271. Dev-era goals: 1,905 (n=448).
  Dev scored window (2022 + 2023 + 2024/2025): 1,571 goals,
  4.316/match (n=364).
- No awarded matches (0/555). All 555 index rows are finished, so
  CSV count == index count.

## Split (frozen)

- Dev: seasons ≤ 2024/2025 (warm-up 2021, scored 2022, 2023,
  2024/2025, n=364).
- Virgin: 2025/2026 (complete, n=84 — small; the gate applies as
  written, per BRIEF) — read ONCE per dev-passing candidate
  (G only can pass).
- Reserve: 2026/2027 (n=23, in progress) — untouched, confirmatory
  reserve.
