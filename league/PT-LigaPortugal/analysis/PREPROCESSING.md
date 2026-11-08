# Phase 2 — Preprocessing: PT-LigaPortugal

Builder: `league/PT-LigaPortugal/data/build_data.py` (committed;
regenerates the CSV). Output: `league/PT-LigaPortugal/data/
pt_matches.csv` — 1,628 rows, one per played match, gitignored per
repo norm. Row counts per season: 306 × 5 + 98 (2026/2027) = 1,628,
matching the warehouse index exactly.

Warehouse root resolution (the JSONs are gitignored and held in the
main checkout): (1) `$FOOTMOB_WORLD_ROOT`, (2) `<repo>/data_enrichment`
if it contains `fotmob_world/`, (3) the main checkout path. The index
CSV itself is tracked and read from the repo.

## Inclusion rules

- Played matches only (`header.status.finished`); all 1,628 index
  rows for league 61 qualify.
- Season labels exactly as in the warehouse (`2021/2022` style).
- Identity by FotMob team id (`home_id`/`away_id`); display names are
  stored per match as found (accent variants exist — see
  DATA_UNDERSTANDING quirk 6).

## Column rules

- FT score from `header.teams` scores (cross-checked against the
  index `score` string at build time by construction of the pull).
- HT score: from goal events with `time <= 45` (the payload carries
  no FirstHalf goals stat key). Available for all 1,628 matches;
  verified against shotmap FirstHalf goals, 44/44 on a stride sample.
- Team stats for periods `All` and `FirstHalf` from
  `content.stats.Periods`, via the `jleague_lib.flat_stats` pattern.
  **Period splits are stored only where the payload carries them**
  (35 matches in 2021/2022, 107 in 2022/2023, all from 2023/2024);
  absent splits stay blank — never fabricated, never derived by
  subtraction.
- Shotmap aggregates over regulation shots only (no shootouts exist
  in this league's payloads): per side, shot counts, ΣxG, ΣxGOT and
  the xGOT-populated count, split by `teamId` (own goals stay with
  the shooting team in these aggregates; they are volume/quality
  aggregates, not score accounting).
- Referee: `content.matchFacts.infoBox.Referee.text`, blank where
  FotMob carries an empty referee block (about half of 2021/2022).
- Cards target = stats-feed `yellow_cards` (home + away). Red cards
  are stored but are never a target (program rule).
