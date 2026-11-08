# Phase 1 — Data Understanding: FotMob Switzerland Super League Warehouse

Corpus: `data_enrichment/fotmob_world/Switzerland/Super League/` —
1,122 full matchDetails JSONs (league_id 69), seasons 2021/2022 →
2026/2027. Every number below was measured on the files via the index
(`fotmob_world_index.csv`, league_id = 69) and the built CSV.

## 0. Integrity headline

- 1,122 index rows = 1,122 files = 1,122 built match rows; match ids
  unique; every match finished. Index depth flags: stats 100%,
  shotmap 99.9% (1,121/1,122) — confirmed by content (see §2).

## 1. League format — the 2023/2024 format break (the honest quirk)

The competition changed shape mid-corpus; the two eras are NOT the
same league format and are inventoried separately:

| Era | Seasons | Teams | Rounds | Matches/season | Format |
|---|---|---|---|---|---|
| Old | 2021/2022, 2022/2023 | 10 | 1–36 | 180 | Quadruple round-robin, **no split** |
| New | 2023/2024 → | 12 | 1–38 | 228 | Rounds 1–33 triple round-robin (198), then **split**: rounds 34–38, top 6 = championship group, bottom 6 = relegation group, single round-robin inside each group (15 + 15 = 30), regular-season points carried over |

- Phase flag in the CSV: `regular` for every old-era match and for
  rounds 1–33 of the new era; `split` for rounds 34–38 of the new era
  (90 split matches in the corpus: 30 × 3 complete new-era seasons;
  the partial 2026/2027 has not reached the split yet).
- Preprocessing consequence: split-round matches are ordinary league
  matches for every target (same teams, points carried over) and are
  **included**; the flag exists so a phase sensitivity check is an
  explicit filter, never a silent choice. There is no separate
  "regular-season-only" model — at 180–228 matches/season the league
  cannot afford to discard the split, and the split is part of the
  competition every team plays. The format break itself (10 → 12
  teams, more matches, promoted sides arriving into a bigger league)
  is absorbed by the season-blocked walk-forward: fits for a season
  use only earlier seasons, so no fit ever trains on the future
  format to predict the past one.
- Team churn: 17 distinct team ids ever; 1–2 promoted/relegated sides
  swap most seasons (e.g. Thun in 2025/2026, FC Vaduz in 2026/2027 —
  a Liechtenstein club playing in the Swiss system). The feeder tier
  (Challenge League) is not in this corpus, so no cross-tier offset
  is estimable (contrast J.League F4); thin-data newcomers are
  handled by the goals candidate's pre-registered SHRINK arm.
- Calendar: autumn–spring (Jul–May) with a winter break. 2026/2027
  is partial (78 matches, rounds 1–13, through 2026-11-08) and is
  reserved as the confirmatory window. Note it is running extremely
  hot (3.76 goals/match) — a level fact, not a modelling input.

## 2. Coverage matrix (share of matches with real content)

| Season | n | Stats FT | Stats per half | Shotmap | xG (stats) | touches_opp_box | Referee (non-empty) |
|---|---|---|---|---|---|---|---|
| 2021/2022 | 180 | 100% | 0.6% | 100% | 100% | 74.4% | 47.2% |
| 2022/2023 | 180 | 33.9%* | 33.9% | 100% | 100% | 68.3% | 91.7% |
| 2023/2024 | 228 | 99.6% | 99.6% | 100% | 99.6% | 86.0% | 99.1% |
| 2024/2025 | 228 | 100% | 100% | 100% | 100% | 100% | 100% |
| 2025/2026 | 228 | 100% | 99.6% | 100% | 100% | 100% | 98.7% |
| 2026/2027 (partial) | 78 | 100% | 100% | 99%† | 100% | 100% | 100% |

*2022/2023 per-half periods exist in 61/180 matches. Halves constants
are measured on the complete era only (2023/2024–2025/2026), exactly
as DK treated its partial era.

- One match (2023/2024, id 4201311) has corners/SOT/shots and a
  shotmap but **no stats-feed xG/cards/fouls block**: its cards come
  from the event feed (`cards_source='events'`, the only such row)
  and its goals blend falls back to goals-only, per the reference
  rule. Nothing is fabricated.
- `expectedGoalsOnTarget` (xGOT) population break, same shape as DK:
  populated only for on-target shots through 2023/2024 (~33–34% of
  shots), ~97–100% from 2024/2025. Any xGOT trait is era-guarded to
  2024/2025 onward.
- Referee (`matchFacts.infoBox.Referee.text`): empty string in most
  of 2021/2022 (47.2% populated) — the name is genuinely absent, not
  mis-parsed (verified on raw JSONs) — then 91.7% and ~99–100%.
  Overall coverage 1,007/1,122 = 89.8%.

## 3. Definition alignment (measured)

| Concept | Source | Check |
|---|---|---|
| FT score | `header.status.scoreStr` | source of truth |
| HT score | goal events `time ≤ 45` | events present in 100% of matches; HT derivable for all 1,122 |
| SOT | stats feed `ShotsOnTarget` | correlates 0.991 with the shotmap aligned definition (on-target AND not blocked); stats feed is source of record |
| Total shots | stats feed `total_shots` | shotmap present 99.9%; stats feed is source of record |
| Cards | stats feed `yellow_cards`; event fallback for the one stats-less match | stats == event-feed Yellow counts in 85.9% of matches; stats feed is the unified source |
| Team xG | stats feed `expected_goals` | goals/xG pooled ≈ 1.04; per season 1.022–1.075 — goals run consistently ~2–8% above FotMob xG in this league; the blend input is usable in every season, with that level fact noted |

## 4. What this corpus has

- Full stats feed (xG with open-play/set-play/non-penalty splits,
  SOT, corners, cards, big chances, box touches) in essentially every
  match from 2021/2022 — a full xG-era corpus, like DK.
- Per-half team stats from 2023/2024 (the new-format era).
- Event timelines for 100% of matches; shotmaps for 99.9%.
- A genuine format break to handle honestly (§1) — the only Batch-2
  league so far whose competition structure changes inside the
  corpus.
