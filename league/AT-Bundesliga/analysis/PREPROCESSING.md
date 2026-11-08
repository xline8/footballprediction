# Phase 2 — Preprocessing: From Warehouse JSONs to Analysis Tables

Builder: `league/AT-Bundesliga/data/build_data.py` (uses the shared
`league/jleague_lib.py` extractors). Regenerate with:

```
.venv/bin/python league/AT-Bundesliga/data/build_data.py
```

Outputs (in `league/AT-Bundesliga/data/`, gitignored — regenerable;
builder + docs are the committed artifacts):

| File | Rows | Content |
|---|---|---|
| `at_matches.csv` | 1,047 | one row per match |
| `at_team_matches.csv` | 2,094 | two rows per match (one per team) |

## Reconciliation (no silent loss)

- Index rows for league_id 38: 1,047 → match rows 1,047, asserted in
  the builder; match ids asserted unique. Team rows = 2 × matches.
- Row order: chronological by kickoff, then match id.

## Derivation rules (numbered; the builder implements exactly these)

1. **FT goals** = `header.status.scoreStr` (official). Never events,
   never shotmap.
2. **HT goals** = matchFacts Goal events with `time ≤ 45` by credited
   side (`ht_source='events'`); available for all 1,047 matches.
3. **Event-goal cross-check** (`score_events_mismatch`): flags 0
   matches in this corpus.
4. **Team stats** = stats feed `All` period, home/away as listed; half
   stats (`fh_*`/`sh_*`) from `FirstHalf`/`SecondHalf` for the seven
   modelling keys. Period splits exist only where the feed carries
   them (complete from 2023/2024) — **never fabricated** for earlier
   matches; those cells stay NaN.
5. **Shotmap aggregates** (`sm_*`) over regulation shots only
   (`period = 'PenaltyShootout'` excluded — none occur in this corpus,
   the rule is carried for safety). Own goals credited to the opponent.
   `sm_sot_*` uses the stats-aligned definition (on-target AND not
   blocked); `sm_xgot_*` sums `expectedGoalsOnTarget` over shots where
   populated, with `sm_xgot_n_*` recording the count (the population
   rule changes by era — Phase 1 §2).
6. **Cards, unified** (`yellow_*`, `red_*`, `cards_source='stats'`):
   the stats feed carries yellows/reds for 100% of matches, so it is
   the source of record for every match; event counts are kept as
   cross-check columns (`ev_yellow_*` etc.). No J1-2021-style exception
   is needed.
7. **Phase** (`phase`): from `general.matchRound` — rounds 1–22
   `regular`, 23–32 `split`, '1/2'/'final' `playoff` (Phase 1 §1).
   Split and playoff matches are included in all windows; the column
   exists so the choice is explicit and stratifiable.
8. **Referee** (`referee`): `infoBox.Referee.text`, empty string →
   missing (NaN). Never imputed.
9. **Team identity**: keyed on FotMob team id everywhere (15 ids).
10. **Season identity**: `season` is the index label (`2021/2022` …
    `2026/2027`); `2026/2027` is partial and labelled as such in every
    analysis.

## Missingness rules (explicit; no imputation anywhere)

- Targets are never imputed. FT goals and every FT team stat exist for
  all 1,047 matches.
- Absent feed ≠ zero: missing period splits / box touches / referee
  leave NaN, carried by `has_stats_half` and the columns themselves.
