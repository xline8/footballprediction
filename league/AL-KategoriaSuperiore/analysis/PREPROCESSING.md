# Phase 2 — Preprocessing: AL-KategoriaSuperiore

Builder: `league/AL-KategoriaSuperiore/data/build_data.py` (committed).
Output: `league/AL-KategoriaSuperiore/data/al_matches.csv` (969 rows;
gitignored by repo norm — regenerate with the builder).
Index: `data_enrichment/fotmob_world_index.csv`, filter `league_id = 260`.
Payload root: the worktree does not carry the warehouse, so the builder
resolves payloads from this repo when present, else
`FOOTBALLPREDICTION_ROOT`, else `~/workspace/footballprediction`.

## Inclusion rules

- **Played matches only.** Every index row is a finished match
  (`header.status.finished`); no scheduled/unplayed rows exist in
  the index for this league. All 969 rows enter the CSV.
- **One row per match**, keyed by `match_id` (unique across the
  corpus: 969 ids / 969 rows).
- **Score source**: the index `score` (= `header.status.scoreStr`,
  official FT score). Goal events reproduce it in 969/969.
- **Team identity**: FotMob team ids from `general.homeTeam.id` /
  `awayTeam.id`. Names are carried for readability only; four ids
  have two diacritic spellings — never key on names.
- **Season labels**: as in the warehouse (`2021/2022` … `2026/2027`).
- **Round**: `general.leagueRoundName` (plain 1–36 integers for the
  regular season; `1/2`, `bronze`, `final` for the 2023/24–2024/25
  playoffs; the 2025/26 Final Four round-robin is mislabelled
  rounds 1–3 — see playoff rule below).
- **Playoff flag**: `playoff = True` iff the round name is `1/2`,
  `bronze` or `final`, OR the season is 2025/2026 and the round is
  1–3 and the date is ≥ 2026-05-16 (regular season ended
  2026-05-10). 14 matches flagged.

## Derived columns

- `ht_home_goals` / `ht_away_goals`: from the Half event at `time`
  45 (`halfStrShort` HT, `homeScore`/`awayScore`); blank where no
  such event exists (82 matches). Cross-validated: agrees with
  goal-events ≤ 45 on 887/887. Never fabricated for matches
  without the event.
- `playoff`: see above (14 matches).
- `awarded`: `header.status.awarded` (0 matches in this league).
- `n_events`, `n_goal_events`, `n_card_events`, `n_half_events`,
  `events_present`: raw event-feed counts (provenance, not features).

## Exclusion rules (fitting / evaluation — not from the CSV)

- **Playoff matches (14) are excluded from every fit and every
  evaluation** (knockout / top-4 mini-league format, not the
  36-round regular season). They stay in the CSV flagged, so the
  exclusion is auditable.
- Matches without events (82) contribute their FT score normally;
  only the HT columns are blank for them. No imputation anywhere.
- No awarded matches exist, so no awarded exclusion applies.
- No other exclusions. In particular the 2-club churn every season
  is a format fact, not a data defect — no rows are dropped for it.

## Split-source rules

- Period splits exist only as the HT score (Half event). There are
  no per-half team stats, so no per-half SOT/corners/cards/xG
  columns exist and none are constructed.
- The halves constant (goals 1H share 0.4267, see EDA F3) is a
  presentation-only split of FT lambdas, never a fitted quantity.
