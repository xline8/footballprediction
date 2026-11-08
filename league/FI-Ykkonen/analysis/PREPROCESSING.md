# Step 2 — Preprocessing: FI-Ykkonen

Script: `data/build_data.py` (adapted from the NO-2Divisjon scores-only
build + the FI reference build). Input: bundle `index_8969.csv`
(1,730 rows, league_id 8969) + the extracted JSON warehouse. Output:
`data/fi_matches.csv` (1,730 rows) + `data/fi_team_matches.csv`
(3,460 rows).

## Derivation rules (program standard, none negotiable)

- FT score from `header.status.scoreStr`; verified 0 mismatches
  against the index `score` column.
- Rows: only `status.finished` matches are kept — all 1,730 index
  rows are finished, so CSV count == index count (asserted in the
  script). No rows dropped.
- Phase from `general.leagueName`: "Kakkonen - Lohko A/B/C" →
  `kakkonen_a/b/c`; promotion groups → `kakkonen_promo_a/b/c`;
  "Kakkonen - Promotion Playoff" → `kakkonen_promo_playoff`;
  "Kakkonen - Playoff" → `kakkonen_playoff`; "Ykkönen" →
  `ykkonen`; championship / relegation → `ykkonen_championship` /
  `ykkonen_relegation`. Unknown names would map to `unknown`
  (none occur — 0 unknown phases).
- Team stats from `content.stats.Periods` (All / FirstHalf /
  SecondHalf) — the feed is absent, so all stat keys × 3 periods
  stay empty (NaN + `has_stats_all=0`, `has_stats_half=0` on every
  row). Missing stays missing; an absent feed is never read as zero.
- 1H goals / 1H yellows counted from event times (time ≤ 45, incl.
  45+ stoppage). Matches without events get `ht_source="none"` and
  null 1H fields.
- Cards: BOTH sources recorded — stats yellows/reds (always null
  here) and event-derived counts (`ev_yellow_*` = Card events with
  card in {Yellow, YellowRed}; `ev_yellowred_*`, `ev_red_*`). The
  modelling target `yellow_*` is the event-derived unified yellows,
  recorded for EDA completeness; the K candidate is not-buildable
  (see EDA F5), so no cards target is ever fitted. Note: plain
  Yellow events occur **0 times in the whole corpus** — the event
  yellows are YellowRed events only (EDA F5).
- Shotmap aggregates over regulation shots only — the shotmap is
  absent, so `has_shotmap=0` and all `sm_*` are 0/null on every row.
- Referee recorded as published (`referee`, `has_referee`) — null on
  every row (0% coverage).
- `awarded` flag from `header.status.awarded`; `score_events_mismatch`
  flags the 7 matches where event goals ≠ header score (all 7 are
  the awarded matches; header wins).
- Team table: one row per team-match (home + away), with goals for /
  against and the (empty) stat columns mirrored.

## Spot checks (3 raw JSONs, by hand — Fase 1)

- 4422555 (2024, ykkonen): JSON `scoreStr` "2 - 0", HT 1-0, 0 kartu
  — matches index and CSV.
- 4422585 (2024, FC Vaajakoski–OLS): awarded, header "0 - 3",
  event goals 1-3 — matches CSV (`awarded=true`, mismatch flagged).
- 3537968 (2021, kakkonen): no events, "0 - 0", `ht_source="none"`
  — matches CSV.
