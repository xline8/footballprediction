# Phase 2 — Preprocessing: From Warehouse JSONs to Analysis Tables

Builder: `build_tables.py` (uses `jleague_lib.py`). Regenerate with:

```
.venv/bin/python experiments/jleague_eda/build_tables.py
```

Outputs (in `data/`, gitignored — regenerable in ~25 s; builder + docs
are the committed artifacts):

| File | Rows | Content |
|---|---|---|
| `j1_matches.csv` | 2,091 | one row per J1 match |
| `j2_matches.csv` | 2,318 | one row per J2 match |
| `j3_matches.csv` | 1,819 | one row per J3 match |
| `j1_team_matches.csv` | 4,182 | two rows per match (one per team) |
| `j2_team_matches.csv` | 4,636 | |
| `j3_team_matches.csv` | 3,638 | |

## Reconciliation (no silent loss)

- Warehouse files 6,228 → match rows 6,228 (2,091 + 2,318 + 1,819),
  asserted in the builder; match ids asserted unique across the whole
  corpus (Phase 1 found zero duplicates and exact index agreement, so no
  dedupe was needed — if a future pull adds one, the builder fails loud
  instead of dropping it).
- Team rows = 2 × matches = 12,456 exactly.
- Row order: chronological by kickoff, then match id.

## Derivation rules (numbered; the builder implements exactly these)

1. **FT goals** (`home_goals`, `away_goals`) = `header.status.scoreStr`,
   the official score. Never the event feed, never the shotmap.
2. **HT goals** (`ht_home_goals`, `ht_away_goals`) = count of matchFacts
   Goal events with `time ≤ 45` by credited side (`ht_source='events'`).
   Stoppage-time goals keep `time = 45` with `overloadTime` set in this
   feed, so the ≤45 rule is exact; validated against shotmap period
   counts on 1,711/1,711 J1 matches (Phase 1 §4). Matches without events
   (123, all J3) get NaN + `ht_source='none'`.
3. **Event-goal cross-check** (`ev_goals_*`, `score_events_mismatch`):
   goal-event counts vs rule 1. Flags exactly 2 matches
   (`3520725` awarded, `3520767`), both kept with official scores.
4. **Team stats** (`expected_goals_*`, `total_shots_*`, `ShotsOnTarget_*`,
   `corners_*`, `yellow_cards_*`, `red_cards_*`, `fouls_*`, possession,
   big chances, box touches, offsides, saves, blocked, in/out-of-box,
   xG splits) = stats feed `All` period, home/away as listed. Half stats
   (`fh_*`, `sh_*`) likewise from `FirstHalf`/`SecondHalf` for the seven
   modelling keys (shots, SOT, corners, yellows, reds, xG, fouls).
   Duplicated keys across stat groups never conflict (measured), so the
   flattened value is unambiguous.
5. **Shotmap aggregates** (`sm_*`) are computed over **regulation shots
   only** — `period = 'PenaltyShootout'` attempts are excluded from
   every aggregate and counted separately in `n_shootout_shots`
   (transitional J1 2026; 51 matches, winner in `shootout_winner`).
   Own goals are credited to the opponent (`teamId` is the shooting
   team). `sm_sot_*` uses the stats-aligned definition (on-target AND
   not blocked); `sm_sot_incl_blocked_*` keeps the raw count. `sm_xg_*`
   sums per-shot `expectedGoals`; `sm_xgot_*` sums `expectedGoalsOnTarget`
   over shots where it is populated, with `sm_xgot_n_*` recording how
   many shots contributed (the population rule changes by era — Phase 1
   §2 — so the count is part of the data, not an afterthought).
6. **Cards, unified** (`yellow_*`, `red_*`, `cards_source`): stats feed
   where present (`cards_source='stats'`: all J1, 62 J3 matches);
   otherwise the event feed for J1/J2 (`'events'`: all J2 — its stats
   block has no card keys at all); otherwise NaN (`'none'`: 1,757 J3
   matches). Event yellows count `card='Yellow'`; event reds count
   straight Red + YellowRed, matching the stats feed's own convention
   (99.8% agreement where both exist). J3's event feed omits yellows by
   design of the provider — those matches are missing, **not zero**.
7. **Flags, never silent repairs**: `awarded` (1 match), `has_extra_time`
   (1 match: Machida–Nagoya playoff), `has_shootout` (51),
   `score_events_mismatch` (2), plus presence flags `has_events`,
   `has_lineup`, `has_player_stats`, `has_stats_all`, `has_stats_half`,
   `has_shotmap` — all measured by content.
8. **Team identity**: keyed on FotMob team id everywhere. The display
   name in the match table is the name as listed in that match; the five
   two-spelling ids (Phase 1 §3.5) stay one team. Team-match rows take
   the same ids, so a club moving between tiers keeps one identity —
   this is what makes the cross-tier EDA possible.
9. **Season identity**: `season` is the warehouse folder label
   (`2021`…`2025`, `2026`, `2026-2027`); `season_start` is its first
   year. J1 `2026` (transitional) and `2026-2027` are different
   competitions and are never merged; `2026-2027` is a partial season
   (data through 2026-11-08) and is labelled as such in every analysis.
10. **Team-match long table**: one row per team per match with venue,
    goals for/against, HT goals for/against, result/points from the
    official score (a shootout-decided draw stays a draw in goals —
    `has_shootout`/`shootout_winner` ride along), and for/against pairs
    for xG, shots, SOT, corners, cards, fouls, possession, plus FH/SH
    splits where the feed has them.

## Missingness rules (explicit; no imputation anywhere)

- **Targets are never imputed.** FT goals exist for all 6,228 matches.
  HT goals are NaN for the 123 event-less J3 matches — analyses of
  halves either exclude them (and say so) or do not run on J3.
- **Absent feed ≠ zero.** A missing stats block leaves every stat column
  NaN (e.g. J2 corners after Sep 2024, J3 almost everywhere). Zero is
  only ever a value the feed itself reported.
- **Partial windows are data, with flags.** Windowed coverage (Phase 1
  §3.6) is carried by the `has_*` flags so any downstream filter is an
  explicit, countable choice.
- **Anomalies are flagged, not fixed** (rules 3 and 7). The awarded
  match's played events disagree with its official score on purpose of
  the competition; both facts are preserved.

## Column dictionary (match table; `_home`/`_away` suffixes throughout)

Identity: `match_id, league, season, season_start, date, kickoff_utc,
round, home_team_id, home_team, away_team_id, away_team, coverage_level`.
Scores: `home_goals, away_goals, ht_home_goals, ht_away_goals, ht_source,
ev_goals_home/away, score_events_mismatch`.
Stats FT: `expected_goals_*` (+ `_open_play/_set_play/_non_penalty`),
`total_shots_*`, `ShotsOnTarget_*`, `ShotsOffTarget_*`, `blocked_shots_*`,
`shots_inside_box_*`, `shots_outside_box_*`, `big_chance_*`,
`touches_opp_box_*`, `corners_*`, `yellow_cards_*` (raw stats),
`red_cards_*` (raw stats), `fouls_*`, `Offsides_*`, `keeper_saves_*`,
`BallPossesion_*`.
Stats halves: `fh_`/`sh_` × {`total_shots`, `ShotsOnTarget`, `corners`,
`yellow_cards`, `red_cards`, `expected_goals`, `fouls`} × side.
Shotmap: `sm_shots_*`, `sm_sot_*`, `sm_sot_incl_blocked_*`, `sm_goals_*`,
`sm_xg_*`, `sm_xgot_*`, `sm_xgot_n_*`, `sm_pen_*` (regulation penalties),
`sm_shots_fh_*`, `sm_sot_fh_*`, `sm_xg_fh_*`, `n_shootout_shots`.
Events cards: `ev_yellow_*`, `ev_yellowred_*`, `ev_red_*`.
Unified cards: `yellow_*`, `red_*`, `cards_source`.
Lineup: `formation_home/away`, `coach_home/away`.
Flags: `awarded, has_extra_time, has_shootout, shootout_winner,
has_events, has_lineup, has_player_stats, has_stats_all, has_stats_half,
has_shotmap`.

Team-match table columns are listed in `build_tables.team_rows` and
follow the same naming (`*_for`, `*_against`, `fh_*`, `sh_*`).
