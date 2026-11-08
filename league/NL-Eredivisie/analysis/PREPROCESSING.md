# Phase 2 — Preprocessing: From Warehouse JSONs to Analysis Tables

Builder: `league/NL-Eredivisie/data/build_data.py` (uses
`league/jleague_lib.py`). Regenerate with:

```
~/workspace/footballprediction/.venv/bin/python league/NL-Eredivisie/data/build_data.py
```

Outputs (in `league/NL-Eredivisie/data/`, gitignored — regenerable;
builder + docs are the committed artifacts):

| File | Rows | Content |
|---|---|---|
| `nl_matches.csv` | 1,638 | one row per regular-season Eredivisie match |
| `team_matches.csv` | 3,276 | two rows per match (one per team) |

## Reconciliation (no silent loss)

- Index rows with league_id 57: 1,659 → regular-season rows 1,638
  + excluded ECL-playoff matches 21 (counted and printed by the
  builder, identified by `general.leagueName != "Eredivisie"`).
- Match ids asserted unique; team rows = 2 × matches exactly.
- Row order: chronological by date, then match id.

## Derivation rules (numbered; the builder implements exactly these)

1. **FT goals** (`home_goals`, `away_goals`) = `header.status.scoreStr`
   (fallback: `header.teams` scores). Never the event feed, never
   the shotmap. Cross-checked against goal events in
   `ev_goals_*` / `score_events_mismatch` (0 mismatches measured).
2. **HT goals** = count of matchFacts Goal events with `time ≤ 45`
   by credited side (`ht_source='events'`); events exist for all
   1,638 matches, so no NaN HT in this corpus.
3. **Team stats** = stats feed `Periods.All`, home/away as listed,
   for the xG family (+ open-play/set-play/non-penalty splits),
   total shots, SOT, off target, blocked, in/out of box, big
   chances, box touches, corners, yellows, reds, fouls, offsides,
   saves, possession. Half stats (`fh_*`/`sh_*`) likewise from
   `FirstHalf`/`SecondHalf` for shots, SOT, corners, yellows, reds,
   xG, fouls — present only where the feed carries splits (Phase 1
   §2); never fabricated.
4. **Shotmap aggregates** (`sm_*`) over **regulation shots only**
   (`period='PenaltyShootout'` excluded and counted in
   `n_shootout_shots`; no shootouts exist in this corpus's regular
   season). `sm_sot_*` = on-target AND not blocked (stats-aligned);
   `sm_xgot_*` sums `expectedGoalsOnTarget` over shots where it is
   populated, with `sm_xgot_n_*` (and on/off splits) recording how
   many shots contributed — the population rule changes by era
   (Phase 1 §2), so the count is part of the data.
5. **Cards, unified** (`yellow_*`, `red_*`, `cards_source`): stats
   feed (`cards_source='stats'` — all 1,638 matches here). The
   event feed is the documented fallback only (card events:
   `type='Card'`, yellows count `card='Yellow'`; YellowRed/Red are
   reds), unused in this corpus because stats coverage is 100%.
6. **Flags, never silent repairs**: presence flags `has_events`,
   `has_lineup`, `has_player_stats`, `has_stats_all`,
   `has_stats_half`, `has_shotmap` — all measured by content
   (non-empty), plus `score_events_mismatch`.
7. **Team identity**: FotMob team id everywhere; display name as
   listed in the match.
8. **Season identity**: `season` is the warehouse label
   (`2021/2022` … `2026/2027`); `season_start` is its first year.
   `2026/2027` is a partial season (through 2026-11-08) and is
   labelled as such in every analysis.

## Missingness rules (explicit; no imputation anywhere)

- **Targets are never imputed.** FT goals, and every stats-feed
  target, exist for all 1,638 matches.
- **Absent feed ≠ zero.** Missing period splits leave `fh_*`/`sh_*`
  NaN (2021/2022: 98.4% of matches; 2022/2023: 73.2%); a missing
  `touches_opp_box` leaves it NaN. Zero is only ever a value the
  feed itself reported.
- **Partial windows are data, with flags** (`has_stats_half`,
  per-column NaN), so any downstream filter is an explicit,
  countable choice.
