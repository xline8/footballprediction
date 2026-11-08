# Phase 2 — Preprocessing: From Warehouse JSONs to the Analysis Table

Builder: `data/build_data.py` (regenerates both CSVs from the index;
warehouse JSONs are read from the main checkout, where the
gitignored warehouse lives). Outputs (gitignored, repo norm):
`data/br_matches.csv` (2,239 rows) and `data/br_team_matches.csv`
(4,478 rows). Column spirit identical to the J1/DK tables.

## Inclusion rules

1. **Played matches only** — index rows for `league_id = 268` with
   `header.status.finished`; all 2,239 index rows qualify.
2. **All rounds are ordinary league matches** — 20-team double
   round-robin, no split/playoff phase exists to flag.
3. Season label = warehouse label (calendar year as string).

## Derivation rules

- FT score from `header.status.scoreStr`; HT goals counted from
  goal events with `time ≤ 45` (source `events`; events exist for
  100% of matches).
- Team stats from `content.stats.Periods` blocks `All` /
  `FirstHalf` / `SecondHalf`, keys as listed in the builder's
  `STAT_KEYS`. Period-split columns exist only where the feed
  carries them — **never fabricated**; absence stays NaN.
- Shotmap aggregates over **regulation shots only**
  (`period != PenaltyShootout`); `sm_xg`, `sm_sot` (on-target and
  not blocked), `sm_xgot` (+ its population count `sm_xgot_n`).
- **Unified yellows** (`yellow_unified_home/away`, source flagged):
  events count for 2021–2022 (stats feed undercounts there —
  DATA_UNDERSTANDING §3), stats feed from 2023. One 2023 match has
  no cards in either feed: its unified yellows are NaN and it is
  excluded from cards scoring only (targets are per-market).
- Referee from `content.matchFacts.infoBox.Referee.text`
  (absent 2021 entirely; kept as-is, no imputation).

## Missingness rules

- A missing stat stays missing in the CSV. Every downstream
  consumer applies its own min-sample rule (FEATURES contract);
  nothing is filled with league means at this phase.
- Matches whose *target* for a market is missing do not score in
  that market's harness; they still update other markets' state
  where their inputs exist.
