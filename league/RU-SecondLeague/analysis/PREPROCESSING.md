# Step 2 — Preprocessing: Russia Second League (FotMob 9123)

Builder: `league/RU-SecondLeague/data/build_data.py` (committed; regenerates
the CSVs from the warehouse at `~/workspace/footballprediction`).
Outputs (gitignored, regenerable): `data/ru2_matches.csv` (6,558 rows),
`data/ru2_team_matches.csv` (10,754 rows, finished matches only).

## Inclusion rules (frozen)

1. **One row per index row** (6,558). No deduplication was needed:
   no duplicate `(date, home, away)`; the 359 duplicate
   `(season, home, away)` pairs are home/away legs of double
   round-robins.
2. **Finished only for analysis/fitting.** `finished` is taken from
   `header.status.finished`. Unfinished rows (1,181) enter the CSV with
   null goals; they are never scored and never train.
3. **Awarded matches excluded from every fit, score and EDA level.**
   `awarded` from `header.status.awarded`; 50 rows. They stay in the
   CSV with `awarded=1` (AE-ProLeague precedent).
4. **Season label 2025 excluded from every fit and score** (training
   history included). 42 finished rows, 5% harvest coverage, distorted
   scorelines (DATA_UNDERSTANDING.md §3). They stay in the CSV.
5. **Goals from `header.status.scoreStr`** (== index score on all
   finished rows). No other score source is used.

## Columns

Per match: `match_id, league, season, date, round (matchRound),
sub_tournament (general.leagueName, verbatim), track (A/B/pre-2023),
phase (first_stage / second_stage / promotion_group / relegation_group /
promotion_playoff / relegation_playoff / final_four / group_stage),
home_team_id, home_team, away_team_id, away_team, finished, awarded,
home_goals, away_goals, has_events, n_events, n_card_events,
n_red_events, ht_home_goals, ht_away_goals, ht_source,
has_stats_all, has_stats_half, has_shotmap, referee, has_lineup`.

Derived fields and their rules:

- `track`: "Division A" in the sub-tournament name → A; "Division B"
  → B; otherwise (FNL 2 / Second League Grp.) → pre-2023.
- `phase`: from the sub-tournament name — "First Stage" /
  "Second Stage" / "Promotion Playoff" / "Relegation Playoff" /
  "Promotion Group" / "Relegation Group" / "Final Four"; anything else
  (groups, subgroups) → `group_stage`. The phase is a **record** of
  the format, not a model feature: no phase feature is used anywhere
  (the goals fit is pooled; see MODEL_DESIGN.md).
- `ht_home_goals` / `ht_away_goals`: Goal events with `time <= 45`,
  **only** where the payload has events AND the event goal counts
  reconcile exactly with the score (3,758 matches). Otherwise null
  with `ht_source="none"`. No half split is ever fabricated: there are
  no period-split stats in this league.
- `has_stats_all`, `has_stats_half`, `has_shotmap`: 0 on every row
  (payload-verified). Kept for schema parity with sibling leagues.
- `referee`: empty on every row. Kept for schema parity.
- `has_lineup`: 1 on 25 rows whose lineup shell exists (id/name only);
  no player data is extracted (lineup features are closed, FEATURES.md
  R6).

## Split-source rules

- Period splits: **do not exist** for any market in this league.
  The goals halves presentation uses the frozen constant from EDA
  (§4), computed from event-derived HT goals — never a per-match
  split, never imputed.
- Stats/shotmap: absent; nothing is imputed in their place.
- Cards: no stats yellows and no yellow events exist; no card target
  is constructed (dismissals are not yellows and are not modelled).

## Season labels as in the warehouse

Labels are kept verbatim (`2021/2022`, `2023`, `2023/2024`, …).
The two tracks interleave in calendar time (B runs Mar–Nov, A runs
Jul–Jun); the walk-forward protocol in the prereg orders folds by
season label and applies a strict **date cutoff** for training
(matches dated strictly before the test fold's first match date),
so the A/B calendar overlap cannot leak across tracks.

## Reconciliation checks (run by the builder / audits)

- Rows: 6,558 == index rows for league 9123. Finished 5,377.
  Awarded 50. Phantom 1,181.
- `scoreStr` vs index score: 0 mismatches among finished rows.
- Goal events vs score: 15 mismatches, all awarded matches.
- Team ids: stable across leagues/seasons; joins by id, never by name.
