# Phase 2 — Preprocessing: From Warehouse JSONs to the Analysis Table

Builder: `league/AU-ALeague/data/build_data.py` (adapted from the
DK builder, itself adapted from `league/jleague_lib.py`).
Regenerate:
`.venv/bin/python league/AU-ALeague/data/build_data.py`
(warehouse paths resolve against the main checkout, where the
gitignored world warehouse lives).

Outputs (in `data/`, gitignored — regenerable; builder + docs are
the committed artifacts):

| File | Rows | Content |
|---|---|---|
| `au_matches.csv` | 857 | one row per played match |
| `au_team_matches.csv` | 1,714 | two rows per match (one per team) |

Reconciliation: index rows for league_id 113 = 857 → match rows
857 (asserted in the builder); ids asserted unique; team rows =
2 × matches.

## Derivation rules

1. **Inclusion**: played (finished) matches only — all 857 qualify.
   Ordered chronologically by date, then match id.
2. **FT goals** = `header.status.scoreStr` (official; after extra
   time for the 5 flagged finals). Never events.
3. **Phase**: numeric round = `regular`; `1/4` / `1/2` / `final` =
   `finals`. All phases included in every fit; the flag exists so
   exclusions are explicit, countable choices.
4. **HT goals** = matchFacts Goal events with `time ≤ 45` by
   credited side (`isHome`); available for all 857 matches.
5. **Team stats** = stats feed `All` period; half stats (`fh_`/`sh_`)
   likewise from `FirstHalf`/`SecondHalf` where present. Duplicated
   keys across stat groups take the flattened value (same
   convention as J.League/DK; the AU feed repeats
   `expected_goals`/`total_shots` across groups).
6. **Shotmap aggregates** (`sm_*`) over regulation shots only
   (`period != 'PenaltyShootout'`; 32 shootout shots excluded).
   `sm_sot` uses the stats-aligned definition (on-target AND not
   blocked). `sm_xgot_n` records how many shots carried xGOT (the
   population rule changes by era — Phase 1 §2).
7. **Cards, unified** (`yellow_*`, `red_*`) = stats feed, present
   for every match (`cards_source='stats'` for all rows).
   Event-feed yellow counts kept as `ev_yellow_*` cross-checks.
8. **Referee** = `matchFacts.infoBox.Referee.text` (89.8% overall;
   per-season coverage in Phase 1 §2 — gaps stay missing).
9. **Flags, never silent repairs**: `has_stats_all`,
   `has_stats_half`, `has_shotmap`, `has_events`,
   `has_extra_time` (5 finals), `n_shootout_shots`.
10. **Team identity** keyed on FotMob team id everywhere (13
    distinct ids appear across the six seasons).

## Missingness rules

- Targets are never imputed. FT goals, SOT, corners, yellows, total
  shots and xG exist for all 857 matches.
- Absent feed ≠ zero: partial-era half stats, early
  `touches_opp_box` gaps and missing referees stay NaN and are
  absorbed by per-feature minimum-sample rules.
