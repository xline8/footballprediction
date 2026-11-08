# Phase 2 — Preprocessing: From Warehouse JSONs to the Analysis Table

Builder: `league/DE-2Bundesliga/data/build_data.py` (adapted from
`league/jleague_lib.py` via the BE builder). Regenerate:
`.venv/bin/python league/DE-2Bundesliga/data/build_data.py`
(warehouse paths resolve against the main checkout, where the
gitignored world warehouse lives).

Outputs (in `data/`, gitignored — regenerable; builder + docs are the
committed artifacts):

| File | Rows | Content |
|---|---|---|
| `de2_matches.csv` | 1,629 | one row per played match |
| `de2_team_matches.csv` | 3,258 | two rows per match (one per team) |

Reconciliation: index rows for league_id 146 = 1,629 → match rows
1,629 (asserted in the builder); ids asserted unique; team rows =
2 × matches.

## Derivation rules

1. **Inclusion**: played (finished) matches only — all 1,629 qualify.
   Ordered chronologically by date, then match id.
2. **FT goals** = `header.status.scoreStr` (official). Never events.
3. **Phase**: from the JSON's own `general.leagueName`: contains
   "Qualification" → `qualification`, otherwise `regular`. The raw
   name is kept in `league_name_raw`. Verified: all 1,629 rows are
   `regular` — the relegation play-off is not in this corpus
   (DATA_UNDERSTANDING §1). The frozen rule, should a future pull
   add one, is exclusion from every fit and scored window; the flag
   exists so that choice is explicit and countable. `matchRound` is
   stored as-is.
4. **HT goals** = matchFacts Goal events with `time ≤ 45` by credited
   side (`isHome`); available wherever events exist (100%).
5. **Team stats** = stats feed `All` period; half stats (`fh_`/`sh_`)
   likewise from `FirstHalf`/`SecondHalf` where present. Duplicated
   keys across stat groups take the flattened value (same convention
   as J.League / DK / CH / BE).
6. **Shotmap aggregates** (`sm_*`) over regulation shots only
   (`period != 'PenaltyShootout'`; none in practice, rule kept).
   `sm_sot` uses the stats-aligned definition (on-target AND not
   blocked). `sm_xgot_n` records how many shots carried xGOT (the
   population rule changes by era — Phase 1 §2).
7. **Cards, unified** (`yellow_*`, `red_*`) = stats feed where
   present (`cards_source='stats'`, all 1,629 rows on this corpus);
   a stats-less match with a real event feed would take event-feed
   Yellow counts (`cards_source='events'`). Event-feed counts (incl.
   separate `ev_red_*` / `ev_yellowred_*`) are kept as cross-check
   columns for every row. The stats-vs-events check behind this
   choice is in DATA_UNDERSTANDING §4: stats feed kept (BE/DK
   shape), no amendment.
7b. **Score-only matches** (no events AND no shotmap): every
   stats-derived field is nulled and `cards_source='none'` — targets
   absent, not zero. Rule carried from BE; on this corpus it never
   triggers (events and shotmap are present in 100% of matches).
8. **Referee** = `matchFacts.infoBox.Referee.text`, empty string
   stored as-is (≈90% populated; see Phase 1 §2). Never imputed.
9. **Flags, never silent repairs**: `has_stats_all`, `has_stats_half`,
   `has_shotmap`, `has_events`, `has_extra_time`, `n_shootout_shots`.
10. **Team identity** keyed on FotMob team id everywhere (33 distinct
    ids across the six seasons; display-name variants under one id
    are recorded in DATA_UNDERSTANDING §1).

## Missingness rules

- Targets are never imputed. FT goals, SOT, corners, yellows, total
  shots and xG exist for all 1,629 matches — there are no absent
  targets on this corpus.
- Absent feed ≠ zero: partial-era half stats, early `touches_opp_box`
  gaps and early referee gaps stay NaN/empty and are absorbed by
  per-feature minimum-sample rules.
