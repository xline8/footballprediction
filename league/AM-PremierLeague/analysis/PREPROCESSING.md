# Phase 2 — Preprocessing: AM-PremierLeague

Builder: `league/AM-PremierLeague/data/build_data.py` (committed).
Output: `league/AM-PremierLeague/data/am_matches.csv` (881 rows;
gitignored by repo norm — regenerate with the builder).
Index: `data_enrichment/fotmob_world_index.csv`, filter `league_id = 118`.
Payload root: the worktree does not carry the warehouse, so the builder
resolves payloads from this repo when present, else
`FOOTBALLPREDICTION_ROOT`, else `~/workspace/footballprediction`.

## Inclusion rules

- **Played matches only, as indexed.** Every index row is a finished
  match (`header.status.finished`); no scheduled/unplayed rows exist
  in the index for this league. All 881 rows enter the CSV, including
  the 7 awarded matches (flagged, see below — they are excluded from
  fits/evaluations, not from the CSV).
- **One row per match**, keyed by `match_id` (unique across the
  corpus: 881 ids / 881 rows).
- **Score source**: the index `score` (= `header.status.scoreStr`,
  official FT score). Goal events reproduce it in 874/881; the 7
  exceptions are exactly the awarded matches.
- **Team identity**: FotMob team ids from `general.homeTeam.id` /
  `awayTeam.id`. Names are carried for readability only; each of the
  15 ids carries exactly one name spelling.
- **Season labels**: as in the warehouse (`2021/2022` … `2026/2027`).
- **Round**: `general.leagueRoundName` (plain integers 1–36 in every
  season; no playoff/split round names exist).
- **Playoff flag**: `playoff = False` for all 881 rows — no playoff,
  split-group, championship, or relegation phase exists in any season
  (DATA_UNDERSTANDING §3). The column is kept for schema parity with
  sibling leagues.

## Derived columns

- `ht_home_goals` / `ht_away_goals`: from the Half event at `time`
  45 (`halfStrShort` HT, `homeScore`/`awayScore`); blank where no
  such event exists (53 matches). Cross-validated: agrees with
  goal-events ≤ 45 on 828/828. Never fabricated for matches
  without the event.
- `awarded`: `header.status.awarded` (7 matches, all 2024/2025,
  all involving West Armenia — see DATA_UNDERSTANDING §4.1).
- `n_events`, `n_goal_events`, `n_card_events`, `n_half_events`,
  `events_present`: raw event-feed counts (provenance, not features).

## Exclusion rules (fitting / evaluation — not from the CSV)

- **Awarded matches (7) are excluded from every fit and every
  evaluation** (administrative 3-0/0-3 scorelines, six of them
  never played — the BA/AE precedent). They stay in the CSV flagged,
  so the exclusion is auditable. Dev scored n is therefore 653, not
  660 (2022/23: 180, 2023/24: 180, 2024/25: 158, 2025/26: 135).
- Matches without events (53) contribute their FT score normally;
  only the HT columns are blank for them. No imputation anywhere.
- No other exclusions. In particular the changing team count
  (9 → 10 → 10 → 11 → 10 → 12) and the changing games-per-team
  (32/36/36/30/27) are format facts, not data defects — no rows are
  dropped for them. The 2026/2027 round-15 fixture played early
  (Van–Syunik, 2026-08-20) and the one unplayed round-13 fixture
  are both ordinary virgin-window rows / absences, not exclusions.

## Split-source rules

- Period splits exist only as the HT score (Half event). There are
  no per-half team stats, so no per-half SOT/corners/cards/xG
  columns exist and none are constructed.
- The halves constant (goals 1H share 0.4335, see EDA F3) is a
  presentation-only split of FT lambdas, never a fitted quantity.
