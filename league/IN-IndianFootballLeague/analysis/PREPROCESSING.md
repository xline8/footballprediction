# Step 2 — Preprocessing: IN-IndianFootballLeague

Script: `data/build_data.py` (adapted from the BY-PremierLeague
scores-only build). Input: bundle `index_8982.csv` (608 rows,
league_id 8982) + the extracted JSON warehouse. Output:
`data/in_matches.csv` (608 rows) + `data/in_team_matches.csv`
(1,216 rows).

## Derivation rules (program standard, none negotiable)

- FT score from `header.status.scoreStr`; verified 0 mismatches
  against the index `score` column.
- Rows: only `status.finished` matches are kept — all 608 index
  rows are finished, so CSV count == index count (asserted in the
  script). No rows dropped.
- Phase from `general.leagueName`: "I-League" / "Indian Football
  League" / "I League" → `main`; "I-League Championship Group" /
  "Indian Football League Promotion Group" → `championship`;
  "I-League Relegation Group" / "Indian Football League Relegation
  Group" → `relegation`. Unknown names would map to `unknown`
  (none occur: main 551, championship 36, relegation 21).
- Team stats from `content.stats.Periods` (All / FirstHalf /
  SecondHalf) — the feed is absent, so all 19 stat keys × 3 periods
  stay empty (NaN + `has_stats_all=0`, `has_stats_half=0` on every
  row). Missing stays missing; an absent feed is never read as zero.
- 1H goals / 1H yellows counted from event times (time ≤ 45, incl.
  45+ stoppage). Matches without events get `ht_source="none"` and
  null 1H fields. All 34 no-event matches are 0-0 per the header.
- Cards: BOTH sources recorded — stats yellows/reds (always null
  here) and event-derived counts (`ev_yellow_*` = Card events with
  card in {Yellow, YellowRed}; `ev_yellowred_*`, `ev_red_*`). The
  modelling target `yellow_*` is the event-derived unified yellows,
  recorded for EDA completeness; the K candidate is not-buildable
  (see EDA F5), so no cards target is ever fitted. Note: plain
  Yellow events are 0 in every dev season AND in the virgin —
  `ev_yellow_*` counts YellowRed only in the modelled eras (plain
  Yellows appear only in the 2026/2027 reserve, 27 events).
- Shotmap aggregates over regulation shots only — the shotmap is
  absent, so `has_shotmap=0` and all `sm_*` are 0/null on every row.
- Referee recorded as published (`referee`, `has_referee`): named
  in 467/608 (dev era 453/496; virgin only 4/66).
- `awarded` flag from `header.status.awarded`;
  `score_events_mismatch` flags the 4 awarded matches where event
  goals ≠ header score (4058291, 4058277, 4664604, 4664639 — header
  wins in all four).
- Team table: one row per team-match (home + away), with goals for /
  against and the (empty) stat columns mirrored.

## Spot checks (3 raw JSONs, by hand)

- 3778932 (2021/2022, Gokulam FC–Churchill Brothers): JSON
  `scoreStr` "1 - 0", leagueName "I-League", HT 1-0 from events,
  stats Periods empty, shotmap 0 — matches index and CSV.
- 5187191 (2025/2026, Namdhari FC–Aizawl FC): JSON "1 - 1",
  leagueName "Indian Football League", phase main, HT 0-1 —
  matches index and CSV.
- 1000022426 (2026/2027, Gokulam FC–Samaleswari SC): JSON "3 - 2",
  HT 2-0 from events — matches index and CSV.
