# Phase 1 — Data Understanding: FotMob World Warehouse, Argentina Liga Profesional

Corpus: `data_enrichment/fotmob_world/` (world warehouse), index
`data_enrichment/fotmob_world_index.csv` filtered to `league_id = 112`:
**2,464 matches**. Inventory tool: `league/AR-LigaProfesional/analysis/eda.py`
(raw results in `inventory_summary.json`). Every number below was
measured on the files, not taken from the index flags.

## 0. Integrity headline

- 2,464 index rows = 2,464 unique match ids on disk. Of these,
  **2,419 are group-phase (regular-phase) matches** and **45 are
  playoff-bracket matches** of the 2025–2026 split tournaments
  (15 per completed tournament) — the analysis corpus is the 2,419.
- Content coverage (measured, not key-presence): team stats FT,
  events, lineups and player stats are **100% in every block**. The
  graded dimensions are shotmap/xG (absent before 2023), period
  splits (complete only from 2024) and referee (absent in 2021) —
  see §2. Score vs goal-events cross-check: **1 mismatch** in
  2,419 matches (one 2025 Apertura match; the header score is the
  target by rule, the flag is carried in the data).

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
(+ open_play / set_play / non_penalty / on_target splits — **2023
onward only**), total_shots, ShotsOnTarget, ShotsOffTarget,
blocked_shots, shots_inside/outside_box, big_chance,
touches_opp_box (part-time before 2024 — §3.4), corners,
yellow_cards, red_cards, fouls, Offsides, keeper_saves, passing
block. Stat values arrive as ints, floats and numeric strings; the
extractor takes the leading number (`jleague_lib._num`).

## 2. Coverage matrix (group phase, % of matches with real content)

| Block | n | Teams | Stats FT | Stats per half | Shotmap / xG | Events | Referee named | touches_opp_box present |
|---|---|---|---|---|---|---|---|---|
| 2021 | 325 | 26 | 100 | 2.8 | 3.1 | 100 | **0** | 188/325 |
| 2022 | 378 | 28 | 100 | 1.9 | 4.8 | 100 | 100 | 168/378 |
| 2023 | 378 | 28 | 100 | 72.8 | 100 | 100 | 99.5 | 239/378 |
| 2024 | 378 | 28 | 100 | 100 | 100 | 100 | 100 | 378/378 |
| 2025 - Apertura | 240 | 30 | 100 | 100 | 100 | 100 | 99.2 | 240/240 |
| 2025 - Clausura | 240 | 30 | 100 | 100 | 100 | 100 | 100 | 240/240 |
| 2026 - Apertura | 240 | 30 | 100 | 100 | 100 | 100 | 90.8 | 240/240 |
| 2026 - Clausura | 240 | 30 | 100 | 100 | 100 | 100 | 100 | 240/240 |

- **The xG era starts in 2023.** Before that, the stats feed has no
  expected_goals keys and the shotmap is populated for only
  10/325 (2021) and 18/378 (2022) matches. The goals model's blend
  therefore runs goals-only for 2021–2022 training data (the
  production fallback), exactly as J1's 2021 did.
- Per-half team stats are essentially absent in 2021–2022, partial
  in 2023 (72.8%) and complete from 2024. Halves constants are
  measured on the splits-present matches (EDA F3).
- Referee: the infoBox field exists in 2021 but its text is empty
  for all 325 matches; named from 2022 on. The virgin block
  (2026 - Clausura) has 100% referee coverage.
- `expectedGoalsOnTarget` (per shot) **changes meaning by era**:
  populated only for (some) on-target shots in 2023 (on-target
  share 0.56, off-target 0.003), transitional in 2024 (all-shots
  0.85; on 0.90 / off 0.79), populated for ~100% of shots only
  from **2025** (0.996+ on and off target). The xGOT era guard for
  this league is therefore 2025-01-01 onward.

## 3. Format, calendar, quirks

1. **The format changes across the window — three eras.**
   - *2021*: one league tournament, 26 teams, single round-robin
     (25 rounds × 13), 2021-07-16 → 2021-12-13.
   - *2022–2024*: one league tournament per year, 28 teams, single
     round-robin (27 rounds × 14). Calendars shift (2022:
     Jun–Oct, World-Cup-compressed; 2023: Jan–Jul; 2024: May–Dec).
     Each season folder holds exactly this one tournament (counts
     prove it); the Copa de la Liga played in the same years is a
     separate FotMob competition and is not in these folders.
   - *2025–2026*: two tournaments per year — Apertura (Jan–May)
     and Clausura (Jul–Nov/Dec) — 30 teams in two zones of 15,
     16 group rounds (240 matches) followed by a 15-match playoff
     bracket (round of 16 → final) per tournament.
   Only the round-robin / group phase is modelled; the 45 playoff
   matches (identified by leagueName containing "Playoff" or a
   bracket round label: `1/8`, `1/4`, `1/2`, `final`,
   `*Finals*`/`Quarter-finals`/`Semi-finals`) are **excluded**,
   as in NL-Eredivisie. Playoff matches are single-leg knockout
   ties, several settled on penalties — a different competition
   object from the league phase the models price.
2. **The virgin block is complete.** 2026 - Clausura: all 16 group
   rounds played (240/240 matches, 2026-07-23 → 2026-11-08, the
   warehouse pull window); its playoff bracket had not been played
   at pull time and is excluded by design anyway. It is the most
   recent complete competition block and is this build's virgin
   window (see MODEL_DESIGN). 2025 - Clausura is likewise complete
   (group 2025-07-11 → 2025-11-17, playoffs to 2025-12-14 in the
   index dates) and sits in the dev period.
3. **Cards: the stats feed's `yellow_cards` key is NOT one
   consistent quantity in this league** (the build's headline data
   finding). Sampled per block (n≈40/block), stats-feed yellows
   per match vs event-feed Yellow cards per match: 2021: 3.67 vs
   4.42; 2022: 4.12 vs 4.90; 2023: 4.38 vs 4.50; 2024: 4.72 vs
   4.85; 2025-A: 4.77 vs 4.85; 2025-C: 4.86 vs 4.94; 2026-A: 3.06
   vs 4.75; 2026-C: 3.83 vs 4.70. The stats key undercounts
   throughout and breaks sharply in 2026, while the event feed is
   stable (4.4–4.9 in every block). The unified yellow target is
   therefore **event-derived** (`card='Yellow'` only — the
   program's unified convention) for every match; the raw stats
   value stays in the `yellow_cards_*` columns for reference.
   (Had the stats key been used, the 2026 "cards collapse" would
   have been a feed artefact, and the cards dispersion would read
   1.54 instead of the event target's ~0.95.)
4. **touches_opp_box is a part-time key before 2024**: present in
   44–63% of matches 2021–2023, 100% from 2024. The J1 FEATURES
   min-8 trailing rule absorbs the gaps (feature X7).
5. **Team identity**: keyed on FotMob team id (35 distinct ids
   across the window). Seven ids carry accent-variant spellings
   (e.g. Vélez Sarsfield / Velez Sarsfield) — the same id in every
   case; the builder canonicalises each id to its most recent
   spelling. Team counts per block: 26 / 28 / 28 / 28 / 30 / 30 /
   30 / 30.
6. **Movers**: relegation in this era is by promedios (multi-season
   points averages) plus the annual-table last place; measured
   movement between consecutive blocks is exactly **2 newcomers at
   each year boundary** (2022: Barracas Central, Tigre; 2023:
   Belgrano, Instituto; 2024: Deportivo Riestra, Independiente
   Rivadavia; 2025-A: Aldosivi, San Martín San Juan — with no
   departures, expanding the league 28 → 30; 2026-A: Estudiantes
   de Río Cuarto, Gimnasia Mendoza) and **zero** between Apertura
   and Clausura of the same year. Newcomer gaps are measured in
   EDA F4.
7. `general.coverageLevel` is `ratings` in 2021 and `xG` from 2023
   (2022 mixed) — consistent with the xG-era boundary above.
   2026 - Clausura leagueName is split between "Liga Profesional"
   (206) and "Liga Profesional Argentina" (34) in the feed — a
   naming inconsistency in FotMob's own labels; selection is by
   league_id + round pattern, never by that string.
