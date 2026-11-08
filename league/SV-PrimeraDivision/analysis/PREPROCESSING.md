# Step 2 — Preprocessing: El Salvador Primera Division (FotMob 335)

Builder: `league/SV-PrimeraDivision/data/build_data.py` (committed;
regenerates the CSVs from the warehouse in this worktree — the index
at `data_enrichment/fotmob_world_index.csv` and the payloads under
the `data_enrichment/fotmob_world` symlink to the main checkout).
Outputs (gitignored, regenerable): `data/sv_matches.csv` (1,448 rows),
`data/sv_team_matches.csv` (2,896 rows, all eligible matches, both
stages).

## Inclusion rules (frozen)

1. **One row per index row** (1,448). No deduplication was needed: no
   duplicate match ids; every tournament's regular-phase pair counts
   are consistent with a double round robin (132 = 12 teams × 22
   rounds; 110 = 11 × 22; 67 for the shortened 2022/2023 Apertura).
2. **Eligible = all rows.** There are no awarded/forfeit rows in this
   league (DATA_UNDERSTANDING.md §5): the two event-less non-0-0
   matches are isolated played matches with a missing event feed,
   not forfeits, and stay eligible with HT missing. `awarded = 0` on
   every row; `eligible = 1` on every row (1,448). Ghana's awarded
   rule (event-less AND 3-0/0-3) is NOT applied here — it would
   wrongly exclude the played 0-3 in 4397305, and there is no
   team-concentrated forfeit pattern to support it.
3. **Goals and team identity from the payload** (`header.teams`: id,
   name, score per side) — cross-checked against the index on every
   row (payload score == index score 1,448/1,448; asserted in the
   builder). Teams are keyed by **FotMob team id** (19 distinct ids);
   names are carried for readability only.
4. **HT goals from the Half event at time 45** (`homeScore` /
   `awayScore`); `ht_source = "half_event"` where present (1,334
   matches), else null. The duplicate-goal match 4708064 keeps its
   HT values (2-1, verified consistent with the first three goal
   events); it is flagged `event_ft_mismatch=1`, NOT `ht_suspect`
   (`ht_suspect = 0` on every row — no HT value is suspect). No HT
   value is fabricated where the event feed is absent.
5. **Tournament labels as in the warehouse** (`2021/2022 - Apertura`,
   … , `2026/2027 - Apertura`). No re-labelling. Round from
   `general.matchRound` (numeric 1–22, or `1/4` / `1/2` / `final`).
   `sub_tournament` from `infoBox.Tournament.leagueName`
   ("Primera Division - Apertura" / "- Clausura").
6. **Stage: regular vs playoff.** `stage = "regular"` iff the round
   label is numeric (1–22); `"playoff"` iff `1/4`, `1/2`, `final`
   (asserted: no other round value occurs). The fit/score/EDA
   levels use **regular phase only** (1,326 rows); playoff rows
   (122) stay in the CSVs flagged `stage=playoff`. This follows the
   MX-LigaMX precedent for split-season leagues: two-legged
   knockout ties and a single final are different football from the
   double round robin, and the playoffs are a small, unbalanced
   subset (9% of rows) whose inclusion would mix tie dynamics into
   league ratings.
7. **No imputation anywhere.** Stats/shotmap/playerStats/referee/
   lineup columns are all-null (or all-zero) by construction (the
   payloads carry no such content); `lineup_block` is 0 on every row
   (no lineup block exists in any payload). They are recorded as
   coverage columns, not filled.
8. **Team ids are present by construction** (`home_team_id` /
   `away_team_id`): FotMob team ids from `header.teams`.

## Columns

Per match: `match_id, league, season, date, round, sub_tournament, stage,
home_team_id, home_team, away_team_id, away_team, finished, awarded,
home_goals, away_goals, has_events, n_events, n_goal_events, n_card_events,
n_red_events, ht_home_goals, ht_away_goals, ht_source, ht_suspect,
has_stats_all, has_stats_half, has_shotmap, referee, has_lineup,
lineup_block, has_playerstats, eligible, event_ft_mismatch`.

Derived fields and their rules:

- `stage`: `"regular"` if `general.matchRound` is numeric,
  `"playoff"` if in `("1/4", "1/2", "final")`.
- `awarded`: 0 on every row (no forfeit evidence; see rule 2).
- `event_ft_mismatch`: 1 only for match 4708064 (duplicate goal
  event; event FT 4-1 vs official 3-1).
- `ht_suspect`: 0 on every row.
- `has_stats_all` / `has_stats_half` / `has_shotmap`: non-empty
  content (≥1 stat row / ≥1 shot), not key presence — all 0 here,
  verified per payload (asserted in the builder).
- `referee`: `infoBox.Referee.text`, empty string where absent — all
  empty here, asserted per payload.
- `n_red_events`: Card events with `card` ∈ {Red, YellowRed} (all
  593 Card events are dismissals; the builder asserts zero plain
  Yellow Card events).
- `has_lineup`: 1 iff the lineup block carries ≥1 starter — 0 on
  every row. `lineup_block`: 1 iff a lineup block exists at all —
  0 on every row. `has_playerstats`: 1 iff playerStats carries a
  home or away block — 0 on every row.
- `eligible`: 1 on every row. The dev/virgin harness reads this
  column AND `stage == "regular"` for eligibility.
