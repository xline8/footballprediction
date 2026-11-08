# Step 2 — Preprocessing: TH-ThaiLeague2

Builder: `data/build_data.py` (regenerates `th2_matches.csv`, 681 rows, and
`th2_team_matches.csv`, 1,362 rows, from the warehouse index; assert on 681).

## Inclusion rules

- Played matches only, as listed in the world index for league_id 9498
  (all 681 rows are finished matches with a score).
- One row per match; season labels exactly as in the warehouse
  ("2024/2025" … "2026/2027"); rows sorted by (date, match_id).
- `phase = "playoffs"` where the feed's round label contains "Play-off"
  (6 matches in each complete season), else `"regular"`. **Play-off rows
  are excluded from every fit and every scored window** (frozen phase rule).

## Column rules

- Score from `header.status.scoreStr`; HT goals from goal events
  (`time <= 45`, excluding penalty-shootout events), `ht_source = events`
  (2 rows in 2024/2025 have no events at all: `ht_source = none`, HT = 0–0
  as published by the event derivation; they remain ordinary rows).
- Stats columns are carried in the schema exactly as published — which for
  this league means **null in every row** (Step 1: `Periods.All` is a
  null-valued key in all 681 payloads). A stat that is absent stays null —
  never fabricated, never filled from another source.
- Cards: the target columns `yellow_home/away` are the **event-unified**
  counts (`ev_yellow_*` = direct Yellow + YellowRed), `cards_source =
  "events"` (679 rows) or `"none"` (2 rows, target still 0 as counted from
  the absent feed — those rows are excluded from cards scoring by the
  harness's target-presence rule: a row with `cards_source = none` is
  never scored and never updates the cards state). Event counts are also
  kept in their own columns (`ev_yellow_direct_*`, `ev_yellowred_*`,
  `ev_yellow_*`, `ev_red_*`, plus `ev_yellow_1h_*` — unified yellows with
  event time <= 45, for the halves constant).
- Shotmap aggregates are null in every row (no shotmap exists).
- Referee text from `matchFacts.infoBox.Referee.text`, empty string where
  absent (absent in both complete seasons).
- Team identity keyed by FotMob team id; names as published (verified
  stable 1:1 with ids across all seasons).

## Windows (frozen here, before any fitting)

Only two complete seasons exist, so the dev window is a **within-season
walk-forward over the single pre-virgin season**:

- Warm-up: the first **90 regular matches** of 2024/2025 in (date,
  match_id) order (each of the 17 active clubs has 10–12 matches by then;
  Samut Prakan City's single match is inside the warm-up). Warm-up rows
  update state / enter training sets; they are never scored.
- Dev scored: the remaining **183 regular matches** of 2024/2025
  (2024-11-09 – 2025-04-26); the cards candidate scores **182** of them
  (one scored-block row, Trat FC vs Samut Prakan City 2025-01-04, has no
  event feed at all and is excluded by the target-presence rule).
  Goals fits are date-grouped expanding refits
  on all regular matches strictly before each scored date; the cards
  harness is per-match predict-then-update, date-grouped.
- Virgin: **2025/2026 regular, n = 306**, read ONCE, only for arms passing
  the dev gate. Fits use all 2024/2025 regular matches (273).
- 2026/2027 (90 matches, in progress) is confirmatory only and is not
  read by any harness in this build.
- The dev scored n (183) and virgin n (306) are thin by the programme's
  standards. That is reported, not repaired: no window is widened, no
  play-off rows are admitted, and no gate is loosened for pool size.
