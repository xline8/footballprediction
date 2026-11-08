# Step 2 — Preprocessing: Ghana Premier League (FotMob 522)

Builder: `league/GH-PremierLeague/data/build_data.py` (committed;
regenerates the CSVs from the warehouse at
`~/workspace/footballprediction`). Outputs (gitignored, regenerable):
`data/gh_matches.csv` (1,619 rows), `data/gh_team_matches.csv`
(3,192 rows, eligible matches only).

## Inclusion rules (frozen)

1. **One row per index row** (1,619). No deduplication was needed: no
   duplicate match ids; no duplicate `(date, home, away)`; every
   unordered pair meets exactly twice per full season.
2. **Eligible = not awarded.** `awarded = 1` iff the payload carries
   no events AND the index score is 3-0 or 0-3 (DATA_UNDERSTANDING.md
   §5 — a played match with ≥1 goal always carries a goal-event
   feed in this corpus). Eligible rows: **1,596**. Excluded: 23
   awarded/forfeit rows (1 in 2023/2024, 15 in 2024/2025, 7 in
   2025/2026). Event-less 0-0 draws (184) are played matches and
   stay eligible. There is no `finished`/`awarded` flag in these
   payloads (`header` is null); the rule above is the eligibility
   test, and it is computed from the payload + index score, not
   hard-coded per match.
3. **Goals and team identity from the index** (`score`, `home`,
   `away` columns) — `general`/`header` are null in every payload,
   so no payload score source exists. Index date == payload `Match
   Date` on 1,619/1,619; goal-event counts reproduce the index score
   on 1,592/1,619 matches (exceptions: the 23 awarded rows, the 184
   event-less 0-0 draws, and the 4 `ht_suspect` event-feed errors).
4. **HT goals from the Half event at time 45** (`homeScore` /
   `awayScore`); `ht_source = "half_event"` where present (1,412
   matches), else null. The 4 `ht_suspect` matches keep their HT
   values in the CSV but flagged (`ht_suspect=1`); HT-share work
   excludes them (1,408 trusted HT rows). No HT value is fabricated
   where the event feed is absent.
5. **Season labels as in the warehouse** (`2021/2022`, `2022/2023`,
   `2023/2024`, `2024/2025`, `2025/2026`, `2026/2027`). No
   re-labelling. Round from `infoBox.Tournament.round` (1–34;
   2026/2027 rounds 1–10 so far).
6. **No imputation anywhere.** Stats/shotmap/playerStats/referee
   columns are all-null by construction (the payloads carry no such
   content); `has_lineup` is 0 for every row (10 lineup blocks
   exist but contain zero starters); `lineup_block` records block
   presence (10 rows). They are recorded as coverage columns, not
   filled.
7. **Team ids are null by construction** (`home_team_id` /
   `away_team_id`): no team ids exist in this corpus. Teams are
   keyed by name (32 distinct names, stable across seasons).

## Columns

Per match: `match_id, league, season, date, round,
sub_tournament ("Premier League"), stage ("regular"),
home_team_id (null), home_team, away_team_id (null), away_team,
finished (1), awarded, home_goals, away_goals,
has_events, n_events, n_goal_events, n_card_events, n_red_events,
ht_home_goals, ht_away_goals, ht_source, ht_suspect,
has_stats_all, has_stats_half, has_shotmap, referee (empty),
has_lineup, lineup_block, eligible`.

Derived fields and their rules:

- `stage`: always `"regular"` (single table; no sub-tournaments —
  `Tournament.leagueName` is "Premier League" on every row,
  `parentLeagueId` = 522 = the league id itself, not a parent id).
- `awarded`: 1 iff no events AND index score ∈ {3-0, 0-3}.
- `ht_suspect`: 1 for the 4 event-feed-error matches (4015488,
  4015491, 4015543, 4584614).
- `has_stats_all` / `has_stats_half` / `has_shotmap`: non-empty
  content (≥1 stat row / ≥1 shot), not key presence — all False
  here, verified per payload.
- `referee`: `infoBox.Referee.text`, empty string where absent — all
  empty here, verified per payload.
- `n_red_events`: Card events with `card` ∈ {Red, YellowRed} (all
  177 Card events are dismissals).
- `has_lineup`: 1 iff the lineup block carries ≥1 starter — 0 on
  every row. `lineup_block`: 1 iff a lineup block exists at all —
  10 rows.
- `eligible`: 1 iff not awarded. The dev/virgin harness reads this
  column and nothing else for eligibility.
