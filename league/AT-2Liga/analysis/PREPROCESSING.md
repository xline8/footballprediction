# Phase 2 — Preprocessing: From Warehouse JSONs to Analysis Tables

Builder: `league/AT-2Liga/data/build_data.py` (uses the shared
`league/jleague_lib.py` extractors). Regenerate with:

```
python3 league/AT-2Liga/data/build_data.py
```

Outputs (in `league/AT-2Liga/data/`, gitignored — regenerable;
builder + docs are the committed artifacts):

| File | Rows | Content |
|---|---|---|
| `at2_matches.csv` | 1,266 | one row per match |
| `at2_team_matches.csv` | 2,532 | two rows per match (one per team) |

## Reconciliation (no silent loss)

- Index rows for league_id 119: 1,266 → match rows 1,266, asserted
  in the builder; match ids asserted unique. Team rows = 2 × matches.
- Row order: chronological by kickoff, then match id.

## Derivation rules (numbered; the builder implements exactly these)

1. **FT goals** = `header.status.scoreStr` (official). Never events,
   never shotmap (the shotmap is empty anyway).
2. **HT goals** = matchFacts Goal events with `time ≤ 45` by credited
   side (`ht_source='events'`); available for all 1,266 matches.
3. **Event-goal cross-check** (`score_events_mismatch`): flags
   exactly 1 match (4525679 — Phase 1 §0).
4. **Team stats** = stats feed `All` period, home/away as listed.
   Only four keys ever populate (`BallPossesion`, `total_shots`,
   `ShotsOnTarget`, `corners`); the schema keeps the wider key list
   so absence is visible as NaN columns, not as missing columns.
   `fh_*`/`sh_*` columns exist for schema parity and are **null on
   every row** — no payload carries period splits, and none are
   fabricated.
5. **Cards, event-unified** (`yellow_*`, `cards_source='events'` on
   all 1,266 rows): the stats feed carries no `yellow_cards` key in
   any payload, so the stats-vs-events artefact check is **moot** —
   there is no stats target to disagree with the events (the RU-1
   situation, not the TH/ZA era-flipped one). The target is frozen
   here, before any fitting: **event yellows = Yellow + YellowRed
   event counts per team** (`ev_yellow_*`); `yellow_*` copies them.
   Event counts of 1H yellows (`ev_yellow_1h_*`, card events with
   `time ≤ 45`) are kept for the halves constant. Straight reds are
   recorded (`ev_red_*`, YellowRed counted there too) but are never
   a target.
6. **Phase** (`phase`): `regular` on every row — the league has a
   single double-round-robin phase in all six seasons (Phase 1 §1).
7. **Referee** (`referee`): `infoBox.Referee.text` — empty in all
   1,266 payloads, so the column is null everywhere. Never imputed.
8. **Team identity**: keyed on FotMob team id everywhere (27 ids).
   Names are display only (variants recorded in Phase 1 §1).
9. **Season identity**: `season` is the index label (`2021/2022` …
   `2026/2027`); split-year seasons throughout (the Austrian
   calendar, verified from the feed: seasons start in July and end
   the following spring). `2026/2027` is partial and labelled as
   such in every analysis.

## Missingness rules (explicit; no imputation anywhere)

- Targets are never imputed. FT goals exist for all 1,266 matches;
  event yellows for all 1,266; the four stats targets for 1,254
  (the 12 stats-less 2023/2024 matches stay NaN and are not scored
  by the SOT / corners / total-shots harnesses).
- Absent feed ≠ zero: a missing stat is NaN, never 0. (The one
  deliberate exception in the builder's lineage — RU-1's silent
  events-for-stats substitution — does not arise here because the
  substitution is the documented rule 5 for every row, and no row
  lacks events.)
