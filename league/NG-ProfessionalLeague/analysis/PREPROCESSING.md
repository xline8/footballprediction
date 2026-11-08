# Step 2 — Preprocessing: Nigeria Professional Football League (FotMob 533)

Builder: `league/NG-ProfessionalLeague/data/build_data.py` (committed;
regenerates the CSVs from the warehouse at
`~/workspace/footballprediction`). Outputs (gitignored, regenerable):
`data/ng_matches.csv` (1,830 rows), `data/ng_team_matches.csv`
(3,626 rows, eligible matches only).

## Inclusion rules (frozen)

1. **One row per index row** (1,830). No deduplication was needed: no
   duplicate match ids; no duplicate `(date, home, away)`.
2. **Eligible = finished AND not awarded AND not Championship Group.**
   `finished`/`awarded` from `header.status`; the Championship Group
   is identified by `general.leagueName` containing "Championship"
   (sub-tournament id 885671, 15 rows, 2023 only). Eligible rows:
   **1,813**. Excluded: 1 phantom fixture (3786217), 1 awarded match
   (4464406), 15 Championship Group matches — 17 rows total. The
   stale-flag match 4765626 is KEPT (score 5-1 reconciles with its 6
   Goal events; see DATA_UNDERSTANDING.md §5).
3. **Goals from `header.status.scoreStr`** (== index score on all
   eligible rows). No other score source is used.
4. **HT goals from the Half event at time 45** (`homeScore` /
   `awayScore`); `ht_source = "half_event"` where present (1,645/1,813
   eligible), else null. No HT value is fabricated where the event
   feed is absent.
5. **Season labels as in the warehouse** (`2021/2022`, `2023`,
   `2023/2024`, `2024/2025`, `2025/2026`, `2026/2027`). No
   re-labelling.
6. **No imputation anywhere.** Stats/shotmap/playerStats/referee
   columns are all-null by construction (the payloads carry no such
   content); `has_lineup` is 1 for exactly one row (4635917). They
   are recorded as coverage columns, not filled.

## Columns

Per match: `match_id, league, season, date, round (matchRound),
sub_tournament (general.leagueName, verbatim), stage (regular /
group_a / group_b / championship_group), home_team_id, home_team,
away_team_id, away_team, finished, awarded, home_goals, away_goals,
has_events, n_events, n_goal_events, n_card_events, n_red_events,
ht_home_goals, ht_away_goals, ht_source, has_stats_all,
has_stats_half, has_shotmap, referee, has_lineup`.

Derived fields and their rules:

- `stage`: "championship_group" iff the sub-tournament name contains
  "Championship"; "group_a"/"group_b" iff it contains "Grp. A"/"Grp.
  B"; else "regular".
- `has_stats_all` / `has_stats_half` / `has_shotmap`: non-empty
  content (≥1 stat row / ≥1 shot), not key presence — all False here,
  verified per payload.
- `referee`: `infoBox.Referee.text`, empty string where absent — all
  empty here, verified per payload.
- `n_red_events`: Card events with `card` ∈ {Red, YellowRed}.
- `eligible`: 1 iff finished AND not awarded AND stage ≠
  championship_group. The dev/virgin harness reads this column and
  nothing else for eligibility.
