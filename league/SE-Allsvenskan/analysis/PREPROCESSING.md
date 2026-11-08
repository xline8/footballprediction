# Phase 2 — Preprocessing: SE-Allsvenskan

Builder: `league/SE-Allsvenskan/data/build_data.py` (regenerates
both CSVs from the warehouse index; CSVs themselves are gitignored
by repo norm). Adapted from the DK-Superligaen builder, which follows
the J.League rules in `league/build_league_data.py`.

## Inclusion rules

1. **Played matches only**: index rows for `league_id = 67` whose
   payload has `header.status.finished` true. All 1,424 index rows
   qualify; the output CSV has exactly 1,424 rows, one per match id
   (asserted in the builder).
2. **Regular season only**: every row in this league_id is a
   regular-season match (DATA_UNDERSTANDING §3.1) — no exclusion
   was needed; `phase` is `regular` for all rows.
3. Season labels are the warehouse labels verbatim: calendar years
   `"2021"` … `"2026"`.

## Column rules

- FT score from `header.status.scoreStr`; HT goals counted from
  goal events (`time ≤ 45`, `isHome` = credited side) where the
  event feed exists, else missing — never fabricated.
- Team stats from `content.stats.Periods`: `All` → bare key names,
  `FirstHalf` → `fh_` prefix, `SecondHalf` → `sh_` prefix. Period
  splits are recorded **only where present**; 2022 has none and its
  `fh_*`/`sh_*` columns are empty — no filling, no borrowing.
- Shotmap aggregates over **regulation shots only**
  (`period != PenaltyShootout`; none occur in this league):
  `sm_shots`, `sm_sot` (on-target and not blocked), `sm_xg`,
  `sm_xgot` / `sm_xgot_n` (sum and count of non-null
  `expectedGoalsOnTarget`), `sm_shots_fh`.
- Unified yellows = stats-feed `yellow_cards`
  (`yellow_home/away`, `cards_source='stats'` for 100% of rows);
  event-feed yellows are kept separately as `ev_yellow_*` for
  cross-checking only. Reds likewise from the stats feed.
- Referee = `content.matchFacts.infoBox.Referee.text`, empty string
  where the payload carries none (all of 2021; 12–29% elsewhere) —
  recorded as missing, never imputed.
- The team-match table (`se_team_matches.csv`, 2,848 rows) is the
  long form: one row per team per match with for/against columns
  for goals, xG, total shots, SOT, corners, yellows, box touches,
  big chances and possession, plus shotmap xG/shots for.

## Windows frozen here

- Dev period: seasons 2021–2024 (n = 960).
- Virgin window: season 2025 (n = 240, complete), read once per
  candidate and only for arms passing the dev gate.
- Confirmatory window: season 2026 (224/240 at pull) — reserved,
  not read in this build.
