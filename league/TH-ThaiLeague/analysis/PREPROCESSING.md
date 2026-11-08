# Step 2 — Preprocessing: TH-ThaiLeague

Builder: `data/build_data.py` (regenerates `th_matches.csv`, 1,262 rows, and
`th_team_matches.csv`, 2,524 rows, from the warehouse index; assert on 1,262).

## Inclusion rules

- Played matches only, as listed in the world index for league_id 8984
  (all 1,262 rows are finished matches with a score).
- One row per match; season labels exactly as in the warehouse
  ("2021/2022" … "2026/2027"); rows sorted by (date, match_id).
- `phase = "regular"` for every row (format verified in Step 1; no
  split/play-off phases exist in this era).

## Column rules

- Score from `header.status.scoreStr`; HT goals from goal events
  (`time <= 45`, excluding penalty-shootout events), `ht_source = events`.
- Stats from `content.stats.Periods` flattened per period
  (All / `fh_` FirstHalf / `sh_` SecondHalf) for the key set: BallPossesion,
  expected_goals, expected_goals_set_play, total_shots, ShotsOnTarget,
  big_chance, touches_opp_box, corners, yellow_cards, red_cards, fouls.
  A stat that is absent stays null — never fabricated, never filled from
  another source.
- Period-split columns are populated only where the payload carries
  FirstHalf/SecondHalf periods (49 matches in 2022/2023; all stats matches
  from 2023/2024).
- Cards: `yellow_home/away` = stats-feed `yellow_cards` where stats exist
  (`cards_source = "stats"`, 1,022 rows); in 2021/2022 there is no stats
  feed and the target is null (`cards_source = "none"`, 240 rows) — events
  are NEVER substituted (Step 1 artefact finding: the dev-era event feed
  carries no plain-yellow events). Event counts are kept in their own
  columns (`ev_yellow_direct_*`, `ev_yellowred_*`, `ev_yellow_*`,
  `ev_red_*`) for the artefact audit and the virgin sensitivity.
- Shotmap aggregates (`sm_shots_*`, `sm_sot_*`, `sm_xg_*`, `sm_xgot_*`)
  from non-shootout shots, only where a shotmap exists (2025/2026 onward,
  plus one 2024/2025 match). They are descriptive only in this build —
  the xG era begins inside the virgin, so no feature uses them.
- Referee text from `matchFacts.infoBox.Referee.text`, empty string where
  absent.
- Team identity keyed by FotMob team id; names as published (Latin script,
  verified stable 1:1 with ids across all seasons).

## Windows (frozen here, before any fitting)

- Goals: training seed 2021/2022; dev evaluation 2022/2023–2024/2025
  (720 matches, season-blocked walk-forward); virgin 2025/2026 (240).
- Stats markets (SOT, corners, cards, total shots): warm-up/seed
  2022/2023 (first stats season, updates state, never scored); dev scored
  2023/2024–2024/2025 (480 matches); virgin 2025/2026 (240).
- 2026/2027 (62 matches, in progress) is confirmatory only and is not
  read by any harness in this build.
