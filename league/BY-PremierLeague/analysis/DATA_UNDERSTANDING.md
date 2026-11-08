# Step 1 — Data Understanding: BY-PremierLeague

Belarus Premier League (tier 1), FotMob league_id 263. Calendar-year
seasons 2021–2026, 1,394 played matches in the bundle index
(`index_263.csv`, 1,394 rows). Warehouse mirror:
`data_enrichment/fotmob_world/Belarus/Premier League/<season>/<match_id>.json`.

## Format

- Single group every season: 16 teams (240 matches) in 2021, 2022,
  2024, 2025; 15 teams (210 matches) in 2023; 16 teams (224 matches
  in the bundle) in 2026, season in progress. No championship /
  relegation split inside a season; every row is an ordinary row
  with phase flag `main`, never filtered.
- 23 distinct FotMob team ids over the corpus; 20 of them appear in
  the dev era (2021–2024).
- Calendar-year seasons (Mar–Nov approx.); promotion/relegation
  churn between seasons is small (8 entrant transitions in the dev
  era — see EDA F4), and the entrants are systematically weaker
  (all 8 score below the league mean).

## Identity / naming

- `general.leagueName` is `"Premier League"` for all 1,394 matches
  and the index carries "Premier League" for all rows. No rebrand,
  no split, no merge. `coverageLevel` is `"lower"` for all 1,394
  matches; `parentLeagueId` is 263 throughout.
- All logic keys by FotMob team id. No id carries two spellings —
  all 23 team ids map to exactly one name each. Team names in the
  CSVs are as published per match; the engine keys by id.

## Feeds (measured, `eda_summary.json` / `inventory_summary.json`)

- **Stats feed: 0/1,394 matches in every season.** `content.stats`
  carries no `Periods` key anywhere. No xG, no SOT, no corners, no
  shots, no yellows from stats. Period splits: 0. This is a
  **scores-only league** — confirmed, not assumed.
- **Shotmap: 0/1,394.** No xG anywhere.
- **Events: 1,280/1,394** (2021: 210/240, 2022: 221/240, 2023:
  199/210, 2024: 216/240, 2025: 227/240, 2026: 207/224). The 114
  matches without events carry 48 goals between them — 45 of them
  are the 15 awarded Sputnik Rechitsa matches of 2021 (3-0 each)
  plus the awarded Gomel–Neman 3-0 of 2022; their events-derived
  fields are missing, never zero.
- **Lineups: 4/1,394** (all 4 in 2021, 0 in every other season).
  Not used by any candidate.
- **Referee: named in 0/1,394 matches, every season.** X8 is
  impossible by data absence.
- Event goals agree with the header score in all but 2 matches:
  4127429 (2023, Naftan–Smorgon, awarded 3-0, played 2-2 — header
  wins) and 3832371 (2022, Shakhtyor–Belshina, header 0-0 vs 5
  event goals 4-1 — the official result is 0-0, the events reflect
  the on-pitch score; header wins). Header `scoreStr` is
  authoritative throughout.

## Scores

- Goals/match by season: 2.713 / 2.542 / 2.738 / 2.346 (dev
  2021–2024), 2.546 in the virgin 2025, 2.603 in the reserve 2026.
  Higher-scoring than FR (2.39–2.55): OU2.5 over-rate 0.40–0.52
  every season; home-win rate 0.35–0.45; draw rate 0.21–0.30.
- Total goals in corpus: 3,593. Dev-era (2021–2024) goals: 2,399
  (n=930). Dev scored window (2022–2024): 1,748 goals, 2.533/match
  (n=690).
- Seventeen awarded matches (kept as ordinary rows with
  `awarded=true`, FT score is the awarded score): 15 in 2021, all
  involving Sputnik Rechitsa, which withdrew mid-season — its
  remaining fixtures were awarded 3-0/0-3 with no event feed at
  all; 3832254 (2022, Gomel–Neman, awarded 3-0, no events);
  4127429 (2023, Naftan–Smorgon, played 2-2, awarded 3-0). Their
  event-derived 1H goals are excluded from dev halves by
  construction (awarded matches excluded).

## Split (frozen)

- Dev: seasons ≤ 2024 (warm-up 2021, scored 2022–2024, n=690).
- Virgin: 2025 (complete, n=240) — read ONCE per dev-passing
  candidate (G only can pass).
- Reserve: 2026 (n=224, in progress) — untouched, confirmatory
  reserve.
