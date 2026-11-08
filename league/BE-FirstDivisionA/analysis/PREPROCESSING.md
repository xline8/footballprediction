# Phase 2 — Preprocessing: From Warehouse JSONs to the Analysis Table

Builder: `league/BE-FirstDivisionA/data/build_data.py` (adapted from
`league/jleague_lib.py` via the CH builder). Regenerate:
`.venv/bin/python league/BE-FirstDivisionA/data/build_data.py`
(warehouse paths resolve against the main checkout, where the
gitignored world warehouse lives).

Outputs (in `data/`, gitignored — regenerable; builder + docs are the
committed artifacts):

| File | Rows | Content |
|---|---|---|
| `be_matches.csv` | 1,698 | one row per played match |
| `be_team_matches.csv` | 3,396 | two rows per match (one per team) |

Reconciliation: index rows for league_id 40 = 1,698 → match rows
1,698 (asserted in the builder); ids asserted unique; team rows =
2 × matches.

## Derivation rules

1. **Inclusion**: played (finished) matches only — all 1,698 qualify.
   Ordered chronologically by date, then match id.
2. **FT goals** = `header.status.scoreStr` (official). Never events.
3. **Phase**: from the JSON's own `general.leagueName` (the
   tournament FotMob assigns the match to): contains "Championship"
   → `playoff_championship`; contains "Relegation" →
   `playoff_relegation`; ends with "ECL Playoff" → `playoff_final`
   (the single end-of-season European-ticket final, 2023/2024
   onward); contains "ECL" or "Conference League" →
   `playoff_europe` (named "Playoff ECL Group" through 2023/2024,
   "Playoff Conference League Group" from 2024/2025); otherwise
   `regular`. The raw name is kept in `league_name_raw`. Verified:
   phase counts reproduce the known format of every season exactly
   (306+12+12 in the 18-team era; 240+30+30+12+1 in the 16-team
   era). **All phases are included in every fit** (the frozen
   phase decision, DATA_UNDERSTANDING §1); the flag exists so any
   future exclusion is explicit and countable. `matchRound` is
   stored as-is but is NOT used for phase: its play-off numbering
   is inconsistent across seasons.
4. **HT goals** = matchFacts Goal events with `time ≤ 45` by credited
   side (`isHome`); available wherever events exist (99.9%).
5. **Team stats** = stats feed `All` period; half stats (`fh_`/`sh_`)
   likewise from `FirstHalf`/`SecondHalf` where present. Duplicated
   keys across stat groups take the flattened value (same convention
   as J.League / DK / CH).
6. **Shotmap aggregates** (`sm_*`) over regulation shots only
   (`period != 'PenaltyShootout'`; none in practice, rule kept).
   `sm_sot` uses the stats-aligned definition (on-target AND not
   blocked). `sm_xgot_n` records how many shots carried xGOT (the
   population rule changes by era — Phase 1 §2).
7. **Cards, unified** (`yellow_*`, `red_*`) = stats feed where
   present (`cards_source='stats'`, 1,695 rows); the one
   stats-less match with a real event feed (4206400) takes
   event-feed Yellow counts (`cards_source='events'`, 1 row).
   Event-feed counts (incl. separate `ev_red_*` / `ev_yellowred_*`)
   are kept as cross-check columns for every row. The
   stats-vs-events check behind this choice is in
   DATA_UNDERSTANDING §4.
7b. **Score-only matches** (no events AND no shotmap: 3604331 with a
   stub stats feed, 4449361 with a null stats feed): every
   stats-derived field is nulled and `cards_source='none'` — the
   targets are absent, not zero. Count-market loaders exclude such
   rows entirely (they neither score nor enter that market's
   trailing state); the goals engine keeps them on its goals-only
   fallback. See DATA_UNDERSTANDING §2.
8. **Referee** = `matchFacts.infoBox.Referee.text`, empty string
   stored as-is (≈86% populated; see Phase 1 §2). Never imputed.
9. **Flags, never silent repairs**: `has_stats_all`, `has_stats_half`,
   `has_shotmap`, `has_events`, `has_extra_time`, `n_shootout_shots`.
10. **Team identity** keyed on FotMob team id everywhere (24 distinct
    ids across the six seasons; display-name variants under one id
    are recorded in DATA_UNDERSTANDING §1).

## Missingness rules

- Targets are never imputed. FT goals exist for all 1,698; SOT,
  corners, yellows, total shots exist for 1,696 (absent — not zero —
  for the two score-only matches, rule 7b; yellows additionally via
  the one event fallback); xG missing for exactly three matches,
  where the goals blend uses its goals-only fallback.
- Absent feed ≠ zero: partial-era half stats, early `touches_opp_box`
  gaps and early referee gaps stay NaN/empty and are absorbed by
  per-feature minimum-sample rules.
