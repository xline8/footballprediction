# Phase 1 — Data Understanding: FotMob World Warehouse, Netherlands Eredivisie

Corpus: `data_enrichment/fotmob_world/` (world warehouse), index
`data_enrichment/fotmob_world_index.csv` filtered to `league_id = 57`:
**1,659 matches**. Inventory tool: `league/NL-Eredivisie/analysis/eda.py`
(raw results in `inventory_summary.json`). Every number below was
measured on the files, not taken from the index flags.

## 0. Integrity headline

- 1,659 index rows = 1,659 unique match ids on disk. Of these,
  **1,638 are regular-season Eredivisie** and **21 are ECL-playoff
  matches** (see §3.1) — the analysis corpus is the 1,638.
- Content coverage (measured, not key-presence): team stats FT,
  shotmap, events, lineups, player stats and referee are **100% in
  every season**. The only graded coverage dimension is period
  splits (§2). Score vs goal-events cross-check: **0 mismatches**
  in 1,638 matches.

## 1. Payload anatomy (one matchDetails JSON)

Same layout as the J.League warehouse: `general` (ids, round,
kickoff), `header.status.scoreStr`, `content.matchFacts.events`
(goals/cards/subs with `isHome` = credited side; card events carry
`type='Card'`, `card ∈ {Yellow, YellowRed, Red}`),
`content.stats.Periods` (`All` / `FirstHalf` / `SecondHalf`),
`content.shotmap.shots` (per-shot xG/xGOT, period, situation),
`content.lineup`, `content.playerStats`,
`content.matchFacts.infoBox` (stadium, **Referee.text**,
attendance). `content.table`/`h2h`/`momentum` are post-match
snapshots — never used (leakage).

Stat keys in `Periods.All` include: BallPossesion, expected_goals
(+ open_play / set_play / non_penalty / on_target splits),
total_shots, ShotsOnTarget, ShotsOffTarget, blocked_shots,
shots_inside/outside_box, big_chance, **touches_opp_box (partial —
§3.3)**, corners, yellow_cards, red_cards, fouls, Offsides,
keeper_saves, passing block. Stat values arrive as ints, floats and
numeric strings; the extractor takes the leading number
(`jleague_lib._num`); duplicated keys across stat groups never
disagree in the sampled checks.

## 2. Coverage matrix (regular season, % of matches with real content)

| Season | n | Stats FT | Stats per half | Shotmap | Events | Lineups | Referee | touches_opp_box present |
|---|---|---|---|---|---|---|---|---|
| 2021/2022 | 306 | 100 | 1.6 | 100 | 100 | 100 | 100 | 221/306 |
| 2022/2023 | 306 | 100 | 26.8 | 100 | 100 | 100 | 100 | 210/306 |
| 2023/2024 | 306 | 100 | 100 | 100 | 100 | 100 | 100 | 261/306 |
| 2024/2025 | 306 | 100 | 100 | 100 | 100 | 100 | 100 | 306/306 |
| 2025/2026 | 306 | 100 | 100 | 100 | 100 | 100 | 100 | 306/306 |
| 2026/2027 (partial) | 108 | 100 | 100 | 100 | 100 | 100 | 100 | 108/108 |

- **This is a full xG-era corpus from 2021/2022 on** — unlike J1,
  there is no pre-xG season: team xG and shotmap exist for every
  match in every season.
- Per-half team stats ramp in during 2022/2023 (26.8%) and are
  complete from 2023/2024. Halves constants are therefore measured
  on the 2023/2024+ era (see EDA F3).
- `expectedGoalsOnTarget` (per shot) **changes meaning by era**:
  populated only for on-target shots in 2021/2022–2023/2024
  (all-shots share 0.35–0.36; on-target ≈ 0.57; off-target ≈ 0.01),
  populated for ~100% of shots from **2024/2025** (0.995+). The
  xGOT era guard for this league is therefore 2024/2025 onward —
  the same break pattern as J1, one era earlier.

## 3. Format, calendar, quirks

1. **Playoffs ride inside the same league_id.** Each full season
   folder holds 306 regular-season matches plus ECL-playoff
   matches (6 in 2021/2022 and 2022/2023, 3 per season after;
   21 total). They are identified by `general.leagueName` =
   "Eredivisie ECL Playoff" (vs exactly "Eredivisie") and
   non-numeric `matchRound` ("final", …). They are **excluded**
   from the analysis corpus: the models are regular-season models.
   (Relegation/promotion playoffs are not in this league_id at
   all.) The regular season is a straight 18-team double round
   robin, 34 rounds, Aug–May, no split/relegation rounds in the
   modelled period; the format did not change across 2021–2026.
2. **2026/2027 is a partial season** (108 matches, 2026-08-07 →
   2026-11-08, the warehouse pull date). It is never used for
   fitting or gating; it is the reserved confirmatory window.
3. **touches_opp_box is a part-time key**: present in 69–85% of
   matches 2021/2022–2023/2024, 100% from 2024/2025. The J1
   FEATURES min-8 trailing rule absorbs the gaps (feature X7).
4. **Cards provenance is clean**: the stats feed carries
   yellow_cards/red_cards for 100% of matches, so unified yellows
   are stats-sourced everywhere (`cards_source='stats'`); the
   event feed (type='Card') agrees and is the cross-check, not a
   source. Event-feed yellows on the splits era total 3,130 vs the
   stats feed's 3,294 — the stats feed is the target, per the
   production cards definition.
5. Team identity is keyed on FotMob team id; 18 teams per season,
   3 promoted/relegated each year (newcomer analysis in EDA F4).
6. `general.coverageLevel` = `xG` throughout the corpus.
