# Phase 2 — Preprocessing: From Warehouse JSONs to Analysis Tables

Builder: `league/AR-LigaProfesional/data/build_data.py` (uses
`league/jleague_lib.py`). Regenerate with:

```
~/workspace/footballprediction/.venv/bin/python league/AR-LigaProfesional/data/build_data.py
```

Outputs (in `league/AR-LigaProfesional/data/`, gitignored —
regenerable; builder + docs are the committed artifacts):

| File | Rows | Content |
|---|---|---|
| `ar_matches.csv` | 2,419 | one row per group-phase Liga Profesional match |
| `team_matches.csv` | 4,838 | two rows per match (one per team) |

## Reconciliation (no silent loss)

- Index rows with league_id 112: 2,464 → group-phase rows 2,419
  + excluded playoff matches 45 (counted and printed by the
  builder; identified by leagueName containing "Playoff" or a
  bracket round label — see DATA_UNDERSTANDING §3.1). Per-block
  group counts are asserted in the builder: 325 / 378 / 378 / 378 /
  240 / 240 / 240 / 240.
- Match ids asserted unique; team rows = 2 × matches exactly.
- Row order: chronological by date, then match id.

## Derivation rules (numbered; the builder implements exactly these)

1. **FT goals** (`home_goals`, `away_goals`) = `header.status.scoreStr`
   (fallback: `header.teams` scores). Never the event feed, never
   the shotmap. Cross-checked against goal events in
   `ev_goals_*` / `score_events_mismatch` (1 mismatch measured, in
   2025 - Apertura; header score stands).
2. **HT goals** = count of matchFacts Goal events with `time ≤ 45`
   by credited side (`ht_source='events'`); events exist for all
   2,419 matches, so no NaN HT in this corpus.
3. **Team stats** = stats feed `Periods.All`, home/away as listed,
   for the xG family (+ open-play/set-play/non-penalty/on-target
   splits, 2023 onward), total shots, SOT, off target, blocked,
   in/out of box, big chances, box touches, corners, yellows
   (stats copy, reference only — rule 5), reds, fouls, offsides,
   saves, possession. Half stats (`fh_*`/`sh_*`) likewise from
   `FirstHalf`/`SecondHalf` for shots, SOT, corners, yellows, reds,
   xG, fouls — present only where the feed carries splits (Phase 1
   §2); never fabricated.
4. **Shotmap aggregates** (`sm_*`) over **regulation shots only**
   (`period='PenaltyShootout'` excluded and counted in
   `n_shootout_shots`). `sm_sot_*` = on-target AND not blocked
   (stats-aligned); `sm_xgot_*` sums `expectedGoalsOnTarget` over
   shots where it is populated, with `sm_xgot_n_*` (and on/off
   splits) recording how many shots contributed — the population
   rule changes by era (Phase 1 §2), so the count is part of the
   data. Shotmap aggregates exist only where the shotmap exists
   (2023 onward, plus 28 matches in 2021–2022).
5. **Cards, unified** (`yellow_*`, `cards_source='events'`):
   **event-derived for every match in this league** — yellows
   count matchFacts card events with `card='Yellow'` by credited
   side; YellowRed/Red are reds, not yellows. This departs from
   the NL/J1 stats-first rule for a measured reason: the stats
   feed's `yellow_cards` key undercounts the event feed in every
   block and breaks in 2026 (DATA_UNDERSTANDING §3.3), so it is
   not one consistent quantity here. The raw stats value is kept
   in `yellow_cards_*`. Reds (`red_*`) remain stats-feed
   (`red_cards`), as in the reference leagues; reds are not a
   modelling target. First-half event yellows are also stored
   (`fh_yellow_events_*`, card events with `time ≤ 45`) so the
   yellows halves constant uses the same event definition as the
   FT target.
6. **Flags, never silent repairs**: presence flags `has_events`,
   `has_lineup`, `has_player_stats`, `has_stats_all`,
   `has_stats_half`, `has_shotmap` — all measured by content
   (non-empty), plus `score_events_mismatch`.
7. **Team identity**: FotMob team id everywhere; display name
   canonicalised per id to the spelling in that id's most recent
   match (accent variants share one id — DATA_UNDERSTANDING §3.5).
8. **Block identity**: `season` is the warehouse label (`2021` …
   `2026 - Clausura`); `block_idx` is its chronological position
   (0–7); `season_start` is its first year. `phase='group'` for
   every row (playoffs are excluded, not flagged in).

## Missingness rules (explicit; no imputation anywhere)

- **Targets are never imputed.** FT goals, SOT, corners, total
  shots and event yellows exist for all 2,419 matches.
- **Absent feed ≠ zero.** Missing period splits leave `fh_*`/`sh_*`
  NaN (2021: 97.2% of matches; 2022: 98.1%; 2023: 27.2%); a missing
  `touches_opp_box` leaves it NaN; missing xG (all of 2021–2022
  bar 28 matches) leaves the xG family NaN — the goals model's
  blend falls back to goals-only there by its own frozen rule,
  which is a model rule, not an imputation.
- **Referee** is None where the infoBox text is empty (all of
  2021; scattered matches later). No referee is ever imputed; the
  cards design's X8 arm treats a missing referee as the shrunk
  league mean by its preregistered fallback.
- **Partial windows are data, with flags** (`has_stats_half`,
  per-column NaN), so any downstream filter is an explicit,
  countable choice.
