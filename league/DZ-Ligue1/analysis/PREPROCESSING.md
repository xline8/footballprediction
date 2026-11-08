# Step 2 — Preprocessing: Algeria Ligue 1 (FotMob 516)

Builder: `league/DZ-Ligue1/data/build_data.py` (regenerates the CSVs
from the warehouse in this worktree — the index at
`data_enrichment/fotmob_world_index.csv` and the payloads under the
`data_enrichment/fotmob_world` symlink to the main checkout).
Outputs (gitignored, regenerable): `data/dz_matches.csv` (1,332 rows),
`data/dz_team_matches.csv` (2,664 rows).

## Inclusion rules (frozen)

1. **One row per index row** (1,332). No deduplication was needed: no
   duplicate match ids; every season's round counts are consistent
   with a double round robin (306 = 18 teams × 34 rounds; 240 = 16
   × 30; 66 so far for the in-progress 2026/2027).
2. **Eligible = all rows except the awarded match.** Match 4366461
   (US Souf 0–3 Ben Aknoun, 2023/2024) is `awarded == True` with an
   empty event feed and a first half that never ended — the match
   was not played to completion, so its 0–3 is not a football
   result. Per the GH/NG precedent, awarded matches are excluded:
   `eligible = 0` for 4366461, `eligible = 1` for the other 1,331
   rows (1,331 eligible). The 141 event-less 0-0 draws are played
   matches with a missing event feed, not forfeits, and stay
   eligible with HT missing.
3. **Goals and team identity from the payload** (`header.teams`: id,
   name, score per side) — cross-checked against the index on every
   row (payload score == index score 1,332/1,332; asserted in the
   builder). Teams are keyed by **FotMob team id** (27 distinct ids);
   names are carried for readability only.
4. **HT goals from the Half event at time 45** (`homeScore` /
   `awayScore`); `ht_source = "half_event"` where present (1,190
   matches), else null. Cross-validated: the Half-event HT equals
   the count of Goal events with `time <= 45` in 1,190/1,190
   matches. `ht_suspect = 0` on every row — no HT value is suspect.
   No HT value is fabricated where the event feed is absent (not
   even for the 141 event-less 0-0 draws).
5. **Season labels as in the warehouse** (`2021/2022`, … ,
   `2026/2027`). No re-labelling. Round from `general.matchRound`
   (numeric 1–34). `sub_tournament = ""` for every row (single
   league, no sub-tournaments). `stage = "regular"` for every row
   (no playoffs exist in this league).
6. **No imputation anywhere.** Stats/shotmap/playerStats/referee
   columns are all-null (or all-zero) by construction (the payloads
   carry no such content); `lineup_block` is 1 on 10 rows (a block
   exists) but `has_lineup` is 1 on only 1 row (4040543, the only
   match with real starters). They are recorded as coverage
   columns, not filled.
7. **Team ids are present by construction** (`home_team_id` /
   `away_team_id`): FotMob team ids from `header.teams`.

## Columns

Per match: `match_id, league, season, date, round, sub_tournament, stage,
home_team_id, home_team, away_team_id, away_team, finished, awarded,
home_goals, away_goals, has_events, n_events, n_goal_events, n_card_events,
n_red_events, ht_home_goals, ht_away_goals, ht_source, ht_suspect,
has_stats_all, has_stats_half, has_shotmap, referee, has_lineup,
lineup_block, has_playerstats, eligible, event_ft_mismatch`.

Derived fields and their rules:

- `stage`: `"regular"` on every row. `sub_tournament`: `""` on every
  row.
- `awarded`: 1 only for match 4366461.
- `event_ft_mismatch`: 1 only for match 4366461 (0 goal events vs
  official 0–3; awarded match, empty event feed).
- `ht_suspect`: 0 on every row.
- `has_stats_all` / `has_stats_half` / `has_shotmap`: non-empty
  content (≥1 stat row / ≥1 shot), not key presence — all 0 here,
  verified per payload (asserted in the builder).
- `referee`: `infoBox.Referee.text`, empty string where absent — all
  empty here, asserted per payload.
- `n_red_events`: Card events with `card` ∈ {Red, YellowRed} (all
  244 Card events are dismissals; the builder asserts zero plain
  Yellow Card events).
- `has_lineup`: 1 iff the lineup block carries ≥1 starter — 1 row
  (4040543). `lineup_block`: 1 iff a lineup block exists at all —
  10 rows. `has_playerstats`: 1 iff playerStats carries a home or
  away block — 0 on every row.
- `eligible`: 0 only for match 4366461; 1 on the other 1,331 rows.
  The dev/virgin harness reads this column (AND `stage ==
  "regular"`, which holds everywhere).
