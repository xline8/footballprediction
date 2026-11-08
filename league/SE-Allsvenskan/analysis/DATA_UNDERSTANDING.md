# Phase 1 — Data Understanding: FotMob World Warehouse, Sweden Allsvenskan

Corpus: `data_enrichment/fotmob_world/` (world warehouse), index
`data_enrichment/fotmob_world_index.csv` filtered to `league_id = 67`:
**1,424 matches**. Inventory tool: `league/SE-Allsvenskan/analysis/eda.py`
(raw results in `inventory_summary.json` / `eda_summary.json`). Every
number below was measured on the files, not taken from the index flags.

## 0. Integrity headline

- 1,424 index rows = 1,424 unique match ids on disk, all finished,
  all regular-season Allsvenskan (no playoff rows ride inside this
  league_id — checked via `general.leagueName` / round structure).
- Content coverage (measured): team stats FT and events are **100%
  in every season**; shotmap is 100% except 2024 (238/240, 99.2%) —
  99.9% overall, matching the task brief. The graded dimensions are
  period splits, referee names and `touches_opp_box` (§2).

## 1. Payload anatomy (one matchDetails JSON)

Same layout as the J.League warehouse: `general` (ids, round,
kickoff), `header.status.scoreStr`, `content.matchFacts.events`
(goals/cards/subs, `isHome` = credited side; card events carry
`type='Card'`, `card ∈ {Yellow, YellowRed, Red}`),
`content.stats.Periods` (`All` / `FirstHalf` / `SecondHalf`),
`content.shotmap.shots` (per-shot xG/xGOT, period, situation),
`content.lineup`, `content.playerStats`,
`content.matchFacts.infoBox` (stadium, **Referee.text**, attendance).
`content.table`/`h2h`/`momentum` are post-match snapshots — never
used (leakage).

Stat keys in `Periods.All` include: BallPossesion, expected_goals
(+ open_play / set_play / non_penalty / on_target splits),
total_shots, ShotsOnTarget, ShotsOffTarget, blocked_shots,
shots_inside/outside_box, big_chance, touches_opp_box, corners,
yellow_cards, red_cards, fouls, Offsides, keeper_saves.

## 2. Coverage matrix (% of matches with real content)

| Season | n | Stats FT | Stats per half | Shotmap | Events | Referee named | xG | touches_opp_box |
|---|---|---|---|---|---|---|---|---|
| 2021 | 240 | 100 | 11.7 | 100 | 100 | 0.0 | 100 | 50.8 |
| 2022 | 240 | 100 | 0.0 | 100 | 100 | 87.5 | 100 | 51.3 |
| 2023 | 240 | 100 | 100 | 100 | 100 | 85.0 | 100 | 38.8 |
| 2024 | 240 | 100 | 100 | 99.2 | 100 | 70.8 | 100 | 100 |
| 2025 | 240 | 100 | 100 | 100 | 100 | 84.6 | 100 | 100 |
| 2026 (partial) | 224 | 100 | 100 | 100 | 100 | 88.4 | 100 | 100 |

- **Full xG-era corpus from 2021 on** — team xG and shotmap exist
  for (essentially) every match in every season.
- Per-half team stats are absent in 2022, sparse in 2021 (11.7%),
  and complete from 2023. Halves constants are therefore measured
  on the 2023+ era (see EDA F3), with one exception below.
- **2023 first-half yellow splits are artefact-suspect**: the 2023
  FH yellow share is 0.283 vs 0.387 (2024) and 0.355 (2025) on the
  same complete-coverage basis — the yellows halves constant is
  measured on 2024–2025 only.
- Referee names are **empty for the whole of 2021** and 71–88%
  populated from 2022 on. The cards referee arm must fall back to
  its base form wherever the identity is unknown.
- `expectedGoalsOnTarget` (per shot) **changes meaning by era**:
  populated for only ~0.32–0.33 of shots in 2021–2023 (the
  on-target subset), 0.65 in transitional 2024, and ~1.00 from
  2025. The xGOT era guard for this league would be 2025 onward.
- `touches_opp_box` is a part-time key 2021–2023 (39–51%), 100%
  from 2024. The J1 FEATURES min-8 trailing rule absorbs the gaps.

## 3. Format, calendar, quirks

1. **Calendar-year season, no split.** 16 teams, straight double
   round robin, 30 rounds, 240 matches per season, roughly
   late-March/April to early/mid-November. No championship or
   relegation rounds, no playoffs in the modelled period; the
   format did not change across 2021–2026. Relegation/promotion is
   direct with Superettan (plus a playoff for 14th place played
   outside this league_id): 2–3 new sides per season (2022: GIF
   Sundsvall, Helsingborg, IFK Värnamo; 2023: Brommapojkarna,
   Halmstads BK; 2024: GAIS, Västerås SK; 2025: Degerfors,
   Östers IF) — movers exist, but Superettan is not in this
   corpus, so no cross-tier offset is estimable (EDA F4).
2. **2025 is the most recent complete season** (240/240, 2025-03-29
   → 2025-11-09). It is the virgin window.
3. **2026 is a partial season** (224/240 played at the warehouse
   pull, 2026-04-04 → 2026-11-08; two rounds remain). It is never
   used for fitting or gating; it is the reserved confirmatory
   window, to be read once when complete.
4. **Cards provenance is clean**: the stats feed carries
   yellow_cards/red_cards for 100% of matches, so unified yellows
   are stats-sourced everywhere (`cards_source='stats'`); the event
   feed agrees and is the cross-check, not a source.
5. Team identity is keyed on FotMob team id; 16 teams per season,
   21 distinct teams across 2021–2026.
6. `general.coverageLevel` = `xG` throughout the corpus.
