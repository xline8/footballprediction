# Phase 2 — Preprocessing: From Warehouse JSONs to Analysis Tables

Builder: `league/MX-LigaMX/data/build_data.py` (uses
`league/jleague_lib.py`). Regenerate with:

```
~/workspace/footballprediction/.venv/bin/python league/MX-LigaMX/data/build_data.py
```

Outputs (in `league/MX-LigaMX/data/`, gitignored — regenerable;
builder + docs are the committed artifacts):

| File | Rows | Content |
|---|---|---|
| `mx_matches.csv` | 1,530 | one row per regular-phase Liga MX match |
| `team_matches.csv` | 3,060 | two rows per match (one per team) |

## Reconciliation (no silent loss)

- Index rows with league_id 230: 1,829 → regular-phase rows 1,530
  (10 complete tournaments × 153) + excluded playoff matches 156
  (18 × 4 tournaments in 2021/2022–2022/2023, 14 × 6 from
  2023/2024) + excluded in-progress tournament rows 143
  (2026/2027 - Apertura, regular phase only at pull time, excluded
  wholesale as an incomplete block). Counts are printed by the
  builder and per-tournament regular counts are asserted (≥153
  floors, the AR pattern).
- Match ids asserted unique; team rows = 2 × matches exactly.
- Row order: chronological by date, then match id.
- Reads are two-pass, one match at a time, straight from the
  symlinked warehouse; the warehouse is never copied.

## Derivation rules (numbered; the builder implements exactly these)

1. **Phase rule (frozen)**: a match is REGULAR phase iff
   `general.matchRound` is a digit string "1".."17". Every other
   non-empty round label is a Liguilla / play-in / reclassification
   label and the match is excluded; an empty or unclassifiable
   label raises. `season` is the warehouse label; `block_idx` is
   its chronological position (0–9); `phase='regular'` for every
   retained row.
2. **FT goals** (`home_goals`, `away_goals`) =
   `header.status.scoreStr` (fallback: `header.teams` scores).
   Never the event feed, never the shotmap. Cross-checked against
   goal events in `ev_goals_*` / `score_events_mismatch`
   (2 mismatches measured; header score stands).
3. **HT goals** = count of matchFacts Goal events with `time ≤ 45`
   by credited side (`ht_source='events'`); events exist for all
   1,530 matches, so no NaN HT in this corpus.
4. **Team stats** = stats feed `Periods.All`, home/away as listed,
   for the xG family (+ open-play/set-play/non-penalty/on-target
   splits — present in all tournaments here), total shots, SOT, off
   target, blocked, in/out of box, big chances, box touches,
   corners, yellows (stats copy, reference only — rule 5), reds,
   fouls, offsides, saves, possession. Half stats (`fh_*`/`sh_*`)
   likewise from `FirstHalf`/`SecondHalf` — present only where the
   feed carries splits (Phase 1 coverage matrix); never fabricated.
5. **Cards, unified** (`yellow_*`, `cards_source='events'`):
   **event-derived for every match in this league** — yellows count
   matchFacts card events with `card='Yellow'` by credited side;
   YellowRed/Red are reds, not yellows. This departs from the
   NL/J1 stats-first rule for a measured reason: the stats feed's
   `yellow_cards` key undercounts the event feed in every dev
   tournament and agrees per-match in only 120–135 of 153 matches
   per tournament (DATA_UNDERSTANDING F10, decided on dev-era
   evidence only, before any fitting). The raw stats value is kept
   in `yellow_cards_*`. Reds (`red_*`) remain stats-feed; reds are
   not a modelling target. First-half event yellows are also stored
   (`fh_yellow_events_*`, `time ≤ 45`) so the yellows halves
   constant uses the same event definition as the FT target.
6. **Shotmap aggregates** (`sm_*`) over **regulation shots only**
   (`period='PenaltyShootout'` excluded and counted in
   `n_shootout_shots`; measured shootout shots in the regular
   corpus: 0). `sm_sot_*` = on-target AND not blocked
   (stats-aligned); `sm_xgot_*` sums `expectedGoalsOnTarget` over
   shots where it is populated, with `sm_xgot_n_*` (and on/off
   splits) recording how many shots contributed — the population
   rule changes by era (Phase 1), so the count is part of the data.
7. **Flags, never silent repairs**: `has_events`, `has_lineup`,
   `has_player_stats`, `has_stats_all`, `has_stats_half`,
   `has_shotmap` — all measured by content (non-empty), plus
   `score_events_mismatch`, `referee` (None where the infoBox text
   is empty) and `stadium_city` (from the payload's Stadium block;
   EDA-only, F12).
8. **Team identity**: FotMob team id everywhere; display name
   canonicalised per id to the spelling in that id's most recent
   match.

## Missingness rules (explicit; no imputation anywhere)

- **Targets are never imputed.** FT goals, SOT, corners, total
  shots and event yellows exist for all 1,530 matches.
- **Absent feed ≠ zero.** Missing period splits leave `fh_*`/`sh_*`
  NaN (95.4% of matches in 2021/2022 Apertura; complete from
  2023/2024 Apertura); a missing `touches_opp_box` leaves it NaN
  (early tournaments).
- **Referee** is None where the infoBox text is empty (all of the
  warm-up tournament; 75.2% of 2025/2026 Apertura; 41.8% of the
  virgin block). No referee is ever imputed; the cards design's X8
  arm treats a missing referee as the shrunk league mean by its
  preregistered fallback.
