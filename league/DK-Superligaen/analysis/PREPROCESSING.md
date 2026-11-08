# Phase 2 — Preprocessing: From Warehouse JSONs to the Analysis Table

Builder: `league/DK-Superligaen/data/build_data.py` (adapted from
`league/jleague_lib.py`). Regenerate:
`.venv/bin/python league/DK-Superligaen/data/build_data.py`
(warehouse paths resolve against the main checkout, where the
gitignored world warehouse lives).

Outputs (in `data/`, gitignored — regenerable; builder + docs are the
committed artifacts):

| File | Rows | Content |
|---|---|---|
| `dk_matches.csv` | 1,049 | one row per played match |
| `dk_team_matches.csv` | 2,098 | two rows per match (one per team) |

Reconciliation: index rows for league_id 46 = 1,049 → match rows 1,049
(asserted in the builder); ids asserted unique; team rows = 2 × matches.

## Derivation rules

1. **Inclusion**: played (finished) matches only — all 1,049 qualify.
   Ordered chronologically by date, then match id.
2. **FT goals** = `header.status.scoreStr` (official). Never events.
3. **Phase**: round 1–22 = `regular`, 23–32 = `split`, `final` = the
   European-playoff final. All phases included in every fit; the flag
   exists so exclusions are explicit, countable choices.
4. **HT goals** = matchFacts Goal events with `time ≤ 45` by credited
   side (`isHome`); available for all 1,049 matches.
5. **Team stats** = stats feed `All` period; half stats (`fh_`/`sh_`)
   likewise from `FirstHalf`/`SecondHalf` where present. Duplicated
   keys across stat groups take the flattened value (same convention
   as J.League; the DK feed repeats `expected_goals`/`total_shots`
   across groups).
6. **Shotmap aggregates** (`sm_*`) over regulation shots only
   (`period != 'PenaltyShootout'`; DK has no shootout league — the
   count is 0 in practice, the rule is kept for safety). `sm_sot`
   uses the stats-aligned definition (on-target AND not blocked).
   `sm_xgot_n` records how many shots carried xGOT (the population
   rule changes by era — Phase 1 §2).
7. **Cards, unified** (`yellow_*`, `red_*`) = stats feed, present for
   every match (`cards_source='stats'` for all rows). Event-feed
   yellow counts kept as `ev_yellow_*` cross-check columns.
8. **Referee** = `matchFacts.infoBox.Referee.text` (100% coverage).
9. **Flags, never silent repairs**: `has_stats_all`, `has_stats_half`,
   `has_shotmap`, `has_events`, `has_extra_time` (the 2025/2026
   playoff final), `n_shootout_shots`.
10. **Team identity** keyed on FotMob team id everywhere (16 distinct
    ids appear across the six seasons).

## Missingness rules

- Targets are never imputed. FT goals, SOT, corners, yellows, total
  shots and xG exist for all 1,049 matches.
- Absent feed ≠ zero: partial-era half stats and early `touches_opp_box`
  gaps stay NaN and are absorbed by per-feature minimum-sample rules.
