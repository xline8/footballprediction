# Phase 1 — Data Understanding: FotMob Scotland Premiership Warehouse

Corpus: `data_enrichment/fotmob_world/Scotland/Premiership/` — 1,215 full
matchDetails JSONs (league_id 64), seasons 2021/2022 → 2026/2027.
Every number below was measured on the files via the index
(`fotmob_world_index.csv`, league_id = 64) and the built CSV
(`analysis/eda_compute.py` → `eda_numbers.json`).

## 0. Integrity headline

- 1,215 index rows = 1,215 files = 1,215 built match rows; match ids
  unique; every match finished. Index depth flags: stats 100%,
  shotmap 100% — confirmed by content, not just key presence.

## 1. League format — the Scottish split (the honest quirk)

12 teams. Each complete season = **228 matches**:
- Rounds 1–33: regular season, all 12 teams, triple round-robin (198).
- Rounds 34–38: **split rounds** — top 6 and bottom 6 each play a
  single round-robin (15 + 15) with regular-season points carried
  over. No playoff final (contrast DK); no extra-time rows.

Preprocessing consequence: split-round matches are ordinary league
matches for every target and are **included**; phase is recorded
(`regular`/`split`, split = round ≥ 34) so any sensitivity check is
an explicit filter. There is no separate "regular-season-only" model.

Team churn: 1 club is relegated and 1 promoted most seasons (14
distinct clubs across the corpus). The feeder tier (Championship) is
not in this corpus, so no cross-tier offset can be estimated
(contrast J.League F4); thin-data newcomers are handled by the goals
candidate's pre-registered SHRINK arm instead.

**Old Firm dominance (measured, extreme):** career goal-difference
per match — Celtic +1.729, Rangers +1.208, next best Hearts +0.347,
worst Livingston −0.691; SD of team GD means = 0.714. The trait
spread is far wider than J1/DK; ratings must be allowed to be
extreme, and no arm may clamp them toward parity.

Calendar: autumn–spring season (Jul–May); 2026/2027 is partial in
the warehouse (75 matches, rounds 1–13, through 2026-11-08) and is
reserved as the confirmatory window.

## 2. Coverage matrix (share of matches with real content)

| Season | n | Stats FT | Stats per half | Shotmap | xG | touches_opp_box | Referee |
|---|---|---|---|---|---|---|---|
| 2021/2022 | 228 | 100% | 0% | 100% | 100% | 82.0% | 47.4% |
| 2022/2023 | 228 | 100% | 30.7% | 100% | 100% | 73.7% | 100% |
| 2023/2024 | 228 | 100% | 100% | 100% | 100% | 88.6% | 100% |
| 2024/2025 | 228 | 100% | 100% | 100% | 100% | 100% | 100% |
| 2025/2026 | 228 | 100% | 100% | 100% | 100% | 100% | 98.7% |
| 2026/2027 (partial) | 75 | 100% | 100% | 100% | 100% | 100% | 100% |

- This is a **full xG-era corpus from 2021/2022**: stats-feed xG with
  open-play/set-play/non-penalty splits, SOT, corners, cards, big
  chances in every match.
- Per-half stats are absent in 2021/2022, partial (30.7%) in
  2022/2023, complete from 2023/2024. Halves constants are measured
  on the complete era only (2023/2024–2025/2026, EDA F3).
- `expectedGoalsOnTarget` (xGOT) population break: populated for
  <1% of shots in 2021/2022–2023/2024, ~94–95% from 2024/2025. Any
  xGOT trait is era-guarded to 2024/2025 onward.
- Referee (`matchFacts.infoBox.Referee.text`) missing in 52.6% of
  2021/2022, ~100% thereafter.

## 3. Definition alignment (measured)

| Concept | Source | Check |
|---|---|---|
| FT score | `header.status.scoreStr` | source of truth |
| HT score | goal events `time ≤ 45` | events present in every match |
| SOT | stats feed `ShotsOnTarget` | source of record (shotmap kept as aggregates) |
| Total shots | stats feed `total_shots` | source of record |
| Cards | stats feed `yellow_cards` | stats total == event Yellow total in 90.6% of matches; stats feed is the unified source (`cards_source='stats'` everywhere) |
| Team xG | stats feed `expected_goals` | goals/xG per season 0.989–1.106 (partial 2026/2027: 0.867, small-n) — calibrated, no systematic bias |
