# Phase 2 — Preprocessing: BA-PremierLeague

Builder: `league/BA-PremierLeague/data/build_data.py` (committed).
Output: `league/BA-PremierLeague/data/ba_matches.csv` (1,036 rows;
gitignored by repo norm — regenerate with the builder).
Index: `data_enrichment/fotmob_world_index.csv`, filter `league_id = 267`.

## Inclusion rules

- **Played matches only.** Every index row is a finished match
  (`header.status.finished`); no scheduled/unplayed rows exist in
  the index for this league. All 1,036 rows enter the CSV.
- **One row per match**, keyed by `match_id` (unique across the
  corpus: 1,036 ids / 1,036 rows).
- **Score source**: the index `score` (= `header.status.scoreStr`,
  official FT score). Goal events reproduce it in 1,032/1,036; the
  4 exceptions are the awarded matches (§4 below).
- **Team identity**: FotMob team ids from `general.homeTeam.id` /
  `awayTeam.id`. Names are carried for readability only; four ids
  have two diacritic spellings — never key on names.
- **Season labels**: as in the warehouse (`2021/2022` … `2026/2027`).
- **Round**: `content.matchFacts.infoBox.Tournament.round` (plain
  1–33 / 1–36 integers; no phase labels exist).

## Derived columns

- `ht_home_goals` / `ht_away_goals`: from the Half event at minute
  45 (`homeScore`/`awayScore`); blank where no such event exists
  (75 matches). Cross-validated: agrees with goal-events ≤ 45 on
  961/961. Never fabricated for matches without the event.
- `awarded`: `header.status.awarded` (4 matches).
- `n_events`, `n_goal_events`, `n_card_events`, `n_half_events`,
  `events_present`: raw event-feed counts (provenance, not features).

## Exclusion rules (fitting / evaluation — not from the CSV)

- **Awarded matches (4) are excluded from every fit and every
  evaluation** (their 3-0/0-3 scorelines do not reflect play).
  They stay in the CSV flagged, so the exclusion is auditable.
- Matches without events (75) contribute their FT score normally;
  only the HT columns are blank for them. No imputation anywhere.
- No other exclusions. In particular the 2025/2026 contraction
  (12 → 10 teams) and the missing round-10 fixture in 2026/2027
  are format facts, not data defects — no rows are dropped for them.

## Split-source rules

- Period splits exist only as the HT score (Half event). There are
  no per-half team stats, so no per-half SOT/corners/cards/xG
  columns exist and none are constructed.
- The halves constant (goals 1H share 0.4493, see EDA F3) is a
  presentation-only split of FT lambdas, never a fitted quantity.
