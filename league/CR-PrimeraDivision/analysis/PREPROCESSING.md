# Phase 2 — Preprocessing: Costa Rica Primera Division

Builder: `league/CR-PrimeraDivision/data/build_data.py` → `cr_matches.csv` (1,350 rows, one per played
match) + `team_aliases.json` (17 team ids). The CSV is gitignored by repo norm; the builder script is the
committed artifact and regenerates it deterministically (verified: re-run is byte-identical in row count
and content; cross-checked against the warehouse index — all 1,350 match_ids present exactly once).

## Inclusion rules

- **Played matches only.** All 1,350 warehouse rows are finished matches (`general.finished` true);
  nothing is excluded. No unplayed/future rows exist in the warehouse slice.
- **Regular season is the fitting scope** (`stage == regular`, 1,290 matches). Playoffs
  (`final_stage` 48 + `championship_final` 12 = 60 matches) are kept in the CSV but excluded from
  fitting (different format: two-legged ties; card events also missing for 2021–2024 playoffs).
- **Season labels as in the warehouse** (`2021/2022` … `2026/2027`); directory names use dashes
  (`2021-2022`, …) — the mapping is in the builder.

## Parse rules (frozen)

- **FT goals** from `header.teams[].score` (authoritative). Never from goal-event counts
  (7 matches mismatch — see DATA_UNDERSTANDING §Gaps).
- **HT goals** from the `Half` event's `homeScore`/`awayScore`; null when no Half event (26 matches).
  `goals_1h_total` / `goals_2h_total` derive from HT and FT totals; null when HT is null.
- **Tournament**: `Clausura` if `infoBox.Tournament.leagueName` contains `Clausura`, else `Apertura`
  (absorbs the `Costa Rica Primera Division Apertura` naming variant).
- **Stage**: `championship_final` if the league name contains `Championship Final`;
  `final_stage` if it contains `Final Stage`; else `regular`. `round` = `Tournament.roundName` as-is.
- **Yellows** = count of Card events with `card == Yellow` + `card == YellowRed`, split by `isHome`.
  `YellowRed` is always paired with an earlier `Yellow` event for the same player (verified 31/31 in
  2023/24), so each `YellowRed` adds exactly one yellow and the first yellow is already counted.
- **Reds** = count of Card events with `card == Red` only (straight reds; `YellowRed` excluded).
- **Cards halves**: each Yellow/YellowRed event goes to 1H if it appears BEFORE the Half event in the
  events-list order, else 2H. Per-team 1H/2H yellows are stored as separate columns. Null when no Half
  event. (Minute thresholds are not used — stoppage-time minutes are ambiguous.)
- **Referee**: `infoBox.Referee.text`, stripped; empty → null.
- **Teams keyed by FotMob team id** (`header.teams[].id`); canonical name = most frequent variant per
  id (see `team_aliases.json` for the alias lists).
- **Flags**: `events_present` (events list non-empty), `goal_event_mismatch` (goal-event count ≠ FT total).

## Split-source rules

- Period splits (HT goals, cards halves) exist only where a Half event exists; **never fabricated**.
  Matches without a Half event contribute FT totals only and are excluded from halves estimation.
- Card-derived columns before 2023/2024 are present in the CSV but must not be used for fitting:
  the feed is broken (2021/22: no Yellow events at all; Apertura 2022/23: means 0.11–0.35;
  Clausura 2022/23: patchy, 10.6% false-zero rate). The reliable cards era starts 2023/2024
  (see EDA.md F4).
- No imputation anywhere: no stats, shotmap or xG columns exist to impute from.
