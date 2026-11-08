# Step 2 — Preprocessing: ZA-PSL

Builder: `data/build_data.py` (regenerates `za_matches.csv`, 1,243 rows,
and `za_team_matches.csv`, 2,486 rows, from the warehouse index; asserts
on both counts and prints the play-off exclusion count).

## Inclusion rules

- Played matches only, as listed in the world index for league_id 537
  (all 1,255 rows are finished matches with a score).
- **Play-off exclusion (frozen):** rows whose payload `general.leagueName`
  contains "Qualification" (the Premier Soccer League Qualification
  Group) are excluded — 12 rows (6 in 2021/2022, 6 in 2022/2023). They are
  a separate promotion/relegation mini-league including second-tier
  clubs, not regular-season matches. Kept rows: 1,243.
- One row per match; season labels exactly as in the warehouse
  ("2021/2022" … "2026/2027"); rows sorted by (date, match_id).
- `phase = "regular"` for every kept row (format verified in Step 1).

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
  FirstHalf/SecondHalf periods (60 matches in 2022/2023; near-complete
  from 2023/2024).
- Cards: `yellow_home/away` = stats-feed `yellow_cards` where stats exist
  (`cards_source = "stats"`, 999 rows); where there is no stats feed the
  target is null (`cards_source = "none"`, 244 rows: all of 2021/2022
  plus 4 stats-era rows missing the key) — events are NEVER substituted
  (Step 1 artefact finding: the dev- and virgin-era event feeds carry no
  plain-yellow events). Event counts are kept in their own columns
  (`ev_yellow_direct_*`, `ev_yellowred_*`, `ev_yellow_*`, `ev_red_*`) for
  the artefact audit.
- Shotmap aggregates (`sm_shots_*`, `sm_sot_*`, `sm_xg_*`, `sm_xgot_*`)
  from non-shootout shots, only where a shotmap exists (2025/2026
  onward). They are descriptive only in this build — the xG era begins
  inside the virgin, so no feature uses them.
- Referee text from `matchFacts.infoBox.Referee.text`, empty string where
  absent.
- Team identity keyed by FotMob team id; names as published per row
  (three ids carry two names across the corpus — Step 1; display only).

## Windows (frozen here, before any fitting)

- Goals: training seed 2021/2022; dev evaluation 2022/2023–2024/2025
  (690 matches, season-blocked walk-forward); virgin 2025/2026 (240).
- Stats markets (SOT, corners, cards, total shots): warm-up/seed
  2022/2023 (first stats season, updates state, never scored); dev scored
  2023/2024–2024/2025 (450 matches; 448 with the target — 2 stats-missing
  rows in 2023/2024, 447 for cards); virgin 2025/2026 (240).
- 2026/2027 (73 matches, in progress) is confirmatory only and is not
  read by any harness in this build.
