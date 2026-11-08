# Phase 1 — Data Understanding: FotMob Brazil Série A Warehouse

Source: FotMob world warehouse, `league_id = 268` (Série A). Index
rows: 2,239 played matches. Builder: `data/build_data.py`
(parsing reference: `league/jleague_lib.py`, DK builder pattern —
2–3 payloads per era were inspected by hand before adapting).

## 0. Integrity headline

Every index row is a finished match and parses: 2,239 rows in,
2,239 rows out, unique match_ids, FT scores from
`header.status.scoreStr` throughout. No duplicates, no unplayed
fixtures in the index slice.

## 1. League format — calendar-year, no split (the simple case)

- **Calendar-year seasons (Apr–Dec)**, warehouse labels are plain
  years: 2021, 2022, 2023, 2024, 2025 complete; **2026 in progress**
  (339 of 380 played at the pull).
- **20 teams, double round-robin, 380 matches/season.** No playoffs,
  no championship/relegation split, no extra time. The regular
  season *is* the whole competition — no phase modelling is needed
  or honest to add.
- **Relegation/promotion**: bottom 4 drop to Série B, top 4 of
  Série B come up (4 movers per season, one partial exception in
  2022 with 5 new names of which 4 arrived from Série B). Série B
  **is** in the warehouse (`league_id = 8814`, 2,270 matches,
  stats 100%, shotmap 33%) — so the X2 mover bridge is estimable
  in-corpus, unlike DK. Série C (`8971`) also exists but is not
  needed: movers into A come only from B.

## 2. Coverage matrix (share of matches with real content)

| Season | n | Stats (All) | Period splits | Shotmap | Events | Referee | Stats-feed xG | Box touches |
|---|---|---|---|---|---|---|---|---|
| 2021 | 380 | 100% | 9.5% | 8.9% | 100% | **0%** | 9.5% | 48.9% |
| 2022 | 380 | 100% | 4.7% | 7.1% | 100% | 92.6% | 7.4% | 43.9% |
| 2023 | 380 | 100% | 99.7% | 100% | 100% | 96.6% | 99.7% | 46.6% |
| 2024 | 380 | 100% | 100% | 100% | 100% | 97.9% | 100% | 100% |
| 2025 | 380 | 100% | 100% | 100% | 100% | 90.0% | 99.5% | 100% |
| 2026 (partial) | 339 | 100% | 100% | 100% | 100% | 60.2% | 100% | 100% |

The warehouse has **two eras**. 2021–2022 is a thin-feed era: the
basic stats block (score, SOT, corners, cards, shots, possession)
is complete, but the rich feed (xG and its splits, period splits,
shotmap) exists for only ~5–10% of matches, box touches for ~45%,
and referees are entirely absent in 2021. From 2023 the feed is
essentially complete on every axis. Consequences, all handled in
PREPROCESSING/FEATURES rather than papered over:

- xG-based features (X1 blend input, X3) are **2023+ quantities**;
  before that the blend falls back to goals-only, exactly the
  production reference's documented behaviour. The sparse covered
  matches in 2021/2022 are a non-random rich-feed subset (their
  goals/xG is 0.76/0.89 — not the league's calibration) and are
  never used as era evidence.
- Shotmap traits (X4, X6) are measurable only on the 2023+ era.
- Halves constants are measured on the complete-splits era
  2023–2025 only; the 2021/2022 partial splits are never used.
- Referee (X8) has no 2021 at all and 90–98% from 2022 — the
  trailing-window min-sample rule absorbs this.

## 3. Definition alignment (measured)

- **Cards — the stats feed undercounts yellows in 2021–2022.**
  Stats-feed yellows/match: 3.04 (2021), 2.93 (2022) vs the events
  feed's 4.50 / 4.90 for the same matches. From 2023 the two agree
  (5.18 vs 5.43; 5.06 vs 5.28; 4.79 vs 4.89 — stats ~2–5% below
  events, the usual discipline-feed gap). There is no real-world
  story in which Brazilian football gained two yellows a match in
  2023; this is a feed break. The unified-cards rule (J1 pattern)
  is therefore: **events yellows for 2021–2022, stats-feed yellows
  from 2023** (`yellow_unified_*` in the CSV, source flagged per
  match). Unified levels are then smooth: 4.50 / 4.90 / 5.18 /
  5.06 / 4.79.
- **xG calibration (covered matches only)**: goals/xG = 0.984
  (2023), 1.007 (2024), 0.993 (2025) — FotMob xG is calibrated for
  BR in the full-feed era (EDA F11).
- **xGOT population rule breaks twice**: `expectedGoalsOnTarget`
  is populated for 32–37% of shots in 2021–2023, 67% in 2024, and
  ~100% only from 2025. Pre-2025 xGOT is the on-target-only
  population (a different quantity); the era guard for X6 is
  therefore 2025+ — which is the virgin season itself (EDA F7).
- **SOT**: stats-feed `ShotsOnTarget` is the target (production
  definition); shotmap-derived SOT agrees where both exist but is
  never substituted for the feed.
