# Phase 2 — Preprocessing: From Warehouse JSONs to the Analysis Table

Builder: `league/IN-ISL/data/build_data.py` (adapted from the
AU-ALeague builder, itself adapted from `league/jleague_lib.py`).
Regenerate:
`.venv/bin/python league/IN-ISL/data/build_data.py`
(warehouse paths resolve against the main checkout, where the
gitignored world warehouse lives).

Outputs (in `data/`, gitignored — regenerable; builder + docs are
the committed artifacts):

| File | Rows | Content |
|---|---|---|
| `in_matches.csv` | 653 | one row per played match |
| `in_team_matches.csv` | 1,306 | two rows per match (one per team) |

Reconciliation: index rows for league_id 9478 = 653 → match rows
653 (asserted in the builder as a floor for daily rebuilds); ids
asserted unique; team rows = 2 × matches.

## Derivation rules

1. **Inclusion**: played (finished) matches only — all 653 qualify.
   Ordered chronologically by date, then match id.
2. **FT goals** = `header.status.scoreStr` (official; after extra
   time for the 3 flagged play-off matches). Never events.
3. **Phase** (FREEZE, from Phase 1 §1): round in
   (`1/4`, `1/2`, `final`) = `playoffs`; everything else =
   `regular`. All phases included in every fit; the flag exists so
   exclusions are explicit, countable choices. Counts: regular
   110/110/132/156/91/28, play-offs 5/7/7/7/0/0 by season.
4. **HT goals** = matchFacts Goal events with `time ≤ 45` by
   credited side (`isHome`); available for all 653 matches.
5. **Team stats** = stats feed `All` period; half stats
   (`fh_`/`sh_`) likewise from `FirstHalf`/`SecondHalf` where
   present (never fabricated where absent).
6. **Shotmap aggregates** (`sm_*`) over regulation shots only
   (`period != 'PenaltyShootout'`). `sm_sot` uses the stats-aligned
   definition (on-target AND not blocked). `sm_xgot_n` records how
   many shots carried xGOT (the population rule changes by era —
   Phase 1 §2).
7. **Cards, unified** (`yellow_*`, `red_*`): the target columns
   `yellow_home/away` are the **event-unified** counts
   (`ev_yellow_*`: events with `type == 'Card'` and
   `card == 'Yellow'`, `YellowRed` excluded) — the Phase 1 §3
   decision, taken on dev-era evidence before any fitting.
   `cards_source='events_unified'` for all rows. Stats-feed
   yellows remain available as `yellow_cards_*`; event first-half
   yellow counts are kept as `ev_yellow_1h_*` for the halves
   constant.
8. **Referee** = `matchFacts.infoBox.Referee.text`, empty string
   normalised to missing (88/653 named; per-season coverage in
   Phase 1 §2 — gaps stay missing).
9. **Flags, never silent repairs**: `has_stats_all`,
   `has_stats_half`, `has_shotmap`, `has_events`,
   `has_extra_time` (3 play-off matches), `n_shootout_shots`.
10. **Team identity** keyed on FotMob team id everywhere (17
    distinct ids appear across the six seasons).

## Missingness rules

- Targets are never imputed. FT goals, SOT, corners, event
  yellows, total shots and xG exist for all 653 matches.
- Absent feed ≠ zero: partial-era half stats and missing referees
  stay NaN and are absorbed by per-feature minimum-sample rules.
