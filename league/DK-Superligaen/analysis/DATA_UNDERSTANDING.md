# Phase 1 — Data Understanding: FotMob Denmark Superligaen Warehouse

Corpus: `data_enrichment/fotmob_world/Denmark/Superligaen/` — 1,049 full
matchDetails JSONs (league_id 46), seasons 2021/2022 → 2026/2027.
Every number below was measured on the files via the index
(`fotmob_world_index.csv`, league_id = 46) and the built CSV.

## 0. Integrity headline

- 1,049 index rows = 1,049 files = 1,049 built match rows; match ids
  unique; every match finished. Index depth flags: stats 100%,
  shotmap 100% — confirmed by content (see §2), not just key presence.

## 1. League format — the Danish split (the honest quirk)

12 teams. Each full season = **193 matches**:
- Rounds 1–22: regular season, all 12 teams, double round-robin (132).
- Rounds 23–32: **split rounds** — top 6 form the championship group,
  bottom 6 the relegation group; each group plays a double round-robin
  (30 + 30) with regular-season points carried over.
- Round "final" (1 match): the European-playoff final between
  relegation-group qualifiers for a UEFA Conference League place.
  The 2025/2026 final went to extra time (its stats Periods include
  ExtraHalf blocks; flagged `has_extra_time`). Its `All` stats therefore
  cover >90 minutes — one match per season at most, kept and flagged,
  never silently repaired.

Preprocessing consequence: split-round matches are ordinary league
matches for every target (same teams, same stakes structure within
group) and are **included**; phase is recorded (`regular`/`split`/
`final`) so any sensitivity check is an explicit filter. There is no
separate "regular-season-only" model — with 193 matches/season the
league cannot afford to discard 61 of them, and the split is part of
the competition every team plays.

Team churn: 2 promoted sides enter most seasons from the 1st Division
(a league outside this corpus), e.g. Fredericia + OB in 2025/2026.
There is no in-corpus feeder tier, so no cross-tier offset can be
estimated (contrast J.League F4); thin-data newcomers are handled by
the goals candidate's pre-registered SHRINK arm instead.

Calendar: autumn–spring season (Jul–May) with a winter break; the
2026/2027 season is partial in the warehouse (84 matches, rounds 1–14,
through 2026-11-08) and is reserved as the confirmatory window.

## 2. Coverage matrix (share of matches with real content)

| Season | n | Stats FT | Stats per half | Shotmap | xG | touches_opp_box | Referee |
|---|---|---|---|---|---|---|---|
| 2021/2022 | 193 | 100% | 9.8% | 100% | 100% | 74.1% | 100% |
| 2022/2023 | 193 | 100% | 33.2% | 100% | 100% | 59.6% | 100% |
| 2023/2024 | 193 | 100% | 100% | 100% | 100% | 72.0% | 100% |
| 2024/2025 | 193 | 100% | 100% | 100% | 100% | 100% | 100% |
| 2025/2026 | 193 | 100% | 100% | 100% | 100% | 100% | 100% |
| 2026/2027 (partial) | 84 | 100% | 100% | 100% | 100% | 100% | 100% |

- This is a **full xG-era corpus from 2021/2022** (unlike J1): stats-feed
  xG with open-play/set-play/non-penalty splits, SOT, corners, cards,
  big chances in every match.
- Per-half stats ramp in during 2021/2022–2022/2023 and are complete
  from 2023/2024. The partial-era splits are artefact-suspect (the
  2022/2023 partial 1H yellow share is 0.167 vs ~0.30–0.36 in every
  complete season) — halves constants are measured on the complete
  era only (EDA F3/F14 analogue).
- `expectedGoalsOnTarget` (xGOT) population break: populated only for
  on-target shots in 2021/2022–2023/2024 (35–36% of shots), ~100% from
  2024/2025. Any xGOT trait is era-guarded to 2024/2025 onward.
- Referee (`matchFacts.infoBox.Referee.text`) present in 100% of matches.

## 3. Definition alignment (measured)

| Concept | Source | Check |
|---|---|---|
| FT score | `header.status.scoreStr` | source of truth |
| HT score | goal events `time ≤ 45` | events present in 100% of matches; HT derivable for all 1,049 |
| SOT | stats feed `ShotsOnTarget` | shotmap aligned definition (on-target AND not blocked) correlates 0.9965 with the stats total; stats feed is source of record |
| Total shots | stats feed `total_shots` | shotmap count exact in 92.7% of matches; stats feed is source of record |
| Cards | stats feed `yellow_cards` | stats == event-feed Yellow counts in 86.2% of matches (event feed also lists YellowRed separately); stats feed is the unified source (`cards_source='stats'` everywhere) |
| Team xG | stats feed `expected_goals` | goals/xG pooled 0.997; per season 0.908–1.076 — calibrated, no systematic bias (2021/2022 runs −9%, noted) |
