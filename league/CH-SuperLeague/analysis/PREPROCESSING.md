# Phase 2 — Preprocessing: From Warehouse JSONs to the Analysis Table

Builder: `league/CH-SuperLeague/data/build_data.py` (adapted from
`league/jleague_lib.py` via the DK builder). Regenerate:
`.venv/bin/python league/CH-SuperLeague/data/build_data.py`
(warehouse paths resolve against the main checkout, where the
gitignored world warehouse lives).

Outputs (in `data/`, gitignored — regenerable; builder + docs are the
committed artifacts):

| File | Rows | Content |
|---|---|---|
| `ch_matches.csv` | 1,122 | one row per played match |
| `ch_team_matches.csv` | 2,244 | two rows per match (one per team) |

Reconciliation: index rows for league_id 69 = 1,122 → match rows
1,122 (asserted in the builder); ids asserted unique; team rows =
2 × matches.

## Derivation rules

1. **Inclusion**: played (finished) matches only — all 1,122 qualify.
   Ordered chronologically by date, then match id.
2. **FT goals** = `header.status.scoreStr` (official). Never events.
3. **Phase**: old era (2021/2022, 2022/2023) = `regular` for all
   rounds 1–36 (no split existed); new era (2023/2024 onward):
   rounds 1–33 = `regular`, rounds 34–38 = `split`. All phases
   included in every fit; the flag exists so exclusions are
   explicit, countable choices.
4. **HT goals** = matchFacts Goal events with `time ≤ 45` by credited
   side (`isHome`); available for all 1,122 matches.
5. **Team stats** = stats feed `All` period; half stats (`fh_`/`sh_`)
   likewise from `FirstHalf`/`SecondHalf` where present. Duplicated
   keys across stat groups take the flattened value (same convention
   as J.League / DK).
6. **Shotmap aggregates** (`sm_*`) over regulation shots only
   (`period != 'PenaltyShootout'`; none in practice, rule kept).
   `sm_sot` uses the stats-aligned definition (on-target AND not
   blocked). `sm_xgot_n` records how many shots carried xGOT (the
   population rule changes by era — Phase 1 §2).
7. **Cards, unified** (`yellow_*`, `red_*`) = stats feed where
   present (`cards_source='stats'`, 1,121 rows); the single
   stats-less match (4201311) takes event-feed Yellow counts
   (`cards_source='events'`). Event-feed counts kept as `ev_yellow_*`
   cross-check columns for every row.
8. **Referee** = `matchFacts.infoBox.Referee.text`, empty string
   stored as-is (89.8% populated; see Phase 1 §2). Never imputed.
9. **Flags, never silent repairs**: `has_stats_all`, `has_stats_half`,
   `has_shotmap`, `has_events`, `has_extra_time`, `n_shootout_shots`.
10. **Team identity** keyed on FotMob team id everywhere (17 distinct
    ids across the six seasons).

## Missingness rules

- Targets are never imputed. FT goals exist for all 1,122; SOT,
  corners, yellows, total shots exist for all 1,122 (yellows via the
  one event fallback); xG missing for exactly one match (4201311),
  where the goals blend uses its goals-only fallback.
- Absent feed ≠ zero: partial-era half stats, early `touches_opp_box`
  gaps and early referee gaps stay NaN/empty and are absorbed by
  per-feature minimum-sample rules.
