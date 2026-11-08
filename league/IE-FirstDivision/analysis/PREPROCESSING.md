# Phase 2 — Preprocessing: From Warehouse JSONs to Analysis Tables

Builder: `data/build_data.py` (adapted from the sibling
`league/IE-PremierDivision/data/build_data.py` — same warehouse format,
same flat-stats extractor; the First Division payloads simply carry no
stats, so every stat column is None by measurement, not by omission).
Regenerate with:

```
python3 league/IE-FirstDivision/data/build_data.py
```

Outputs (in `data/`, gitignored — regenerable in ~5 s; builder + docs
are the committed artifacts):

| File | Rows | Content |
|---|---|---|
| `ie_first_division_matches.csv` | 1,028 | one row per match (998 regular + 30 playoff) |
| `ie_first_division_team_matches.csv` | 2,056 | two rows per match (one per team) |

## Reconciliation (no silent loss)

- Warehouse index rows 1,028 → match rows 1,028, asserted in the
  builder; match ids asserted unique; regular 998 + playoff 30
  asserted.
- Team rows = 2 × matches = 2,056 exactly.
- Row order: chronological by kickoff, then match id.

## Derivation rules (numbered; the builder implements exactly these)

1. **FT goals** (`home_goals`, `away_goals`) = `header.status.scoreStr`,
   the official score. Never the event feed, never the shotmap.
2. **Phase** (`phase`): `regular` when `general.matchRound` is numeric
   (`1`–`36`, 2021: `1`–`27`); `playoff` for `1/2` and `final`.
   Playoffs are built but excluded from every EDA/design number and
   from all fitting/evaluation (Phase 1 §1).
3. **HT goals** (`ht_home_goals`, `ht_away_goals`) = count of matchFacts
   Goal events with `time ≤ 45` by credited side (`ht_source='events'`).
   Exceptions, flagged not repaired: event-less 0–0 matches get HT
   0–0 (`ht_source='inferred-0-0'` — implied by the FT score itself,
   54 matches); the event-less 0–3 Cabinteely–Galway match gets NaN
   (`ht_source='none'`); the side-flipped UCD–Wexford feed gets NaN
   (`ht_source='mismatch'`). HT is derivable for 1,026/1,028 matches.
4. **Event-goal cross-check** (`ev_goals_*`, `score_events_mismatch`):
   goal-event counts vs rule 1. Flags exactly 1 match with events
   (UCD–Wexford 2025-02-14); the Cabinteely match has no events and
   is flagged via `ht_source='none'`.
5. **Team stats** (`expected_goals_*`, `total_shots_*`,
   `ShotsOnTarget_*`, `corners_*`, `yellow_cards_*`, `red_cards_*`,
   `fouls_*`, possession, big chances, box touches, …) = stats feed
   `All` period — which is `None` in every payload, so every one of
   these columns is None in every row. Half stats (`fh_*`, `sh_*`)
   likewise None. The columns are kept (same shape as the sibling
   builder) so the absence is visible in the data, not assumed.
6. **Shotmap aggregates** (`sm_*`): the shot list is empty in every
   payload, so all counts are 0 and all xG sums 0.0. Kept for shape
   parity; no shotmap-derived feature can be built from them.
7. **Cards, unified** (`yellow_*`, `red_*`, `cards_source`): **no
   yellow target exists** (Phase 1 §4.1 — zero plain `Yellow` events
   in 1,028 matches), so `yellow_*` is None and `cards_source='none'`
   for every row. Event audit columns are kept: `ev_yellow_*`
   (Yellow + YellowRed events — in practice YellowRed second yellows
   only, 68 total), `ev_yellow_strict_*` (plain Yellow — 0 total),
   `ev_red_*` (Red + YellowRed — 210 total, 0.20/match).
   Event yellows are NOT promoted to a target: a count that is zero
   by feed omission is missing, not zero.
8. **Referee** (`referee`): `infoBox.Referee.text`, empty string in
   every row. Kept as a column; no referee feature can be built.
9. **Flags**: `has_extra_time` (non-empty extra-half timestamp in
   `status.halfs` — 3 matches, the 2023/2024/2025 playoff finals),
   `has_shootout` (`status.reason.short == 'Pen'` — 1 match, the 2024
   final; regulation score is the target), `score_events_mismatch`,
   plus presence flags `has_events`, `has_stats_all`,
   `has_stats_half`, `has_shotmap` — all measured by content, all
   stats/shotmap flags 0.
10. **Team identity**: keyed on FotMob team id everywhere. 15 ids,
    no name maps to two ids.
11. **Season identity**: `season` is the warehouse folder label
    (`2021`…`2026`); calendar-year seasons, Feb–Oct/Nov. No split
    seasons, no double labels.
12. **Team-match long table**: one row per team per match with venue,
    goals for/against, HT goals for/against. No stat for/against
    pairs exist to carry (see rule 5).

## Missingness rules (explicit; no imputation anywhere)

- **Targets are never imputed.** FT goals exist for all 1,028 matches.
  HT goals are NaN for the 2 flagged matches only.
- **Absent feed ≠ zero.** A missing stats block leaves every stat
  column None. Zero is only ever a value the feed itself reported
  (e.g. `sm_shots_* = 0` is a counted empty shot list, not a missing
  feed — and it is still unusable as a target, since the feed is
  empty by provider coverage, not by match content).
- **The 2025 warehouse gap is not repaired.** One regular match
  (Finn Harps vs Kerry FC, round 1) is absent from the warehouse;
  2025 regular n = 179, not 180. Nothing is filled in.
- **Anomalies are flagged, not fixed** (rules 3, 4, 9).

## Column dictionary (match table; `_home`/`_away` suffixes throughout)

Identity: `match_id, league, season, date, round, phase, home_team_id,
home_team, away_team_id, away_team, coverage_level`.
Scores: `home_goals, away_goals, ht_home_goals, ht_away_goals, ht_source,
ev_goals_home/away, score_events_mismatch`.
Stats FT/halves: `expected_goals_*` (+ `_open_play/_set_play/_non_penalty`),
`total_shots_*`, `ShotsOnTarget_*`, `ShotsOffTarget_*`, `blocked_shots_*`,
`shots_inside_box_*`, `shots_outside_box_*`, `big_chance_*`,
`touches_opp_box_*`, `corners_*`, `yellow_cards_*` (raw stats),
`red_cards_*` (raw stats), `fouls_*`, `Offsides_*`, `keeper_saves_*`,
`BallPossesion_*`, `fh_*`/`sh_*` × the seven modelling keys — **all None
in this league** (kept for shape parity with the sibling builder).
Shotmap: `sm_shots_*`, `sm_sot_*`, `sm_xg_*`, `sm_xgot_*`, `sm_xgot_n_*`,
`sm_shots_fh_*`, `n_shootout_shots` — **all 0 / 0.0**.
Events cards: `ev_yellow_*`, `ev_yellow_strict_*`, `ev_red_*`,
`ev_yellow_fh_*`.
Unified cards: `yellow_*` (None), `red_*` (= `ev_red_*`), `cards_source`
(`'none'`).
Referee: `referee` (empty string).
Flags: `has_extra_time, has_shootout, shootout_winner, has_events,
has_stats_all, has_stats_half, has_shotmap`.

Team-match table columns: `match_id, season, date, phase, team_id, team,
venue, goals_for, goals_against, ht_goals_for, ht_goals_against`.
