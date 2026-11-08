# Phase 1 — Data Understanding: FotMob Germany 2. Bundesliga Warehouse

Corpus: `data_enrichment/fotmob_world/Germany/2. Bundesliga/` —
1,629 full matchDetails JSONs (league_id 146), seasons 2021/2022 →
2026/2027. Every number below was measured on the files via the index
(`fotmob_world_index.csv`, league_id = 146) and the built CSV
(`analysis/eda_compute.py` → `eda_numbers.json`;
`analysis/movers.py` → `movers.json`).

## 0. Integrity headline

- 1,629 index rows = 1,629 files = 1,629 built match rows; match ids
  unique; every match finished. Index depth flags: stats 100%,
  shotmap 100% in every season — confirmed by content (see §2).
  This is the cleanest corpus in the program so far: no score-only
  matches, no stats gaps, no event gaps.
- **Virgin-window note (correcting the commissioning brief):** the
  brief described 2025/2026 as "in progress (transitional)". The
  warehouse says otherwise: 2025/2026 holds the full 306 matches
  (2025-08-01 → 2026-05-17) — it is a COMPLETE season and is frozen
  as the virgin window. 2026/2027 (99 matches, 11 rounds, through
  2026-11-08) is the partial season and is reserved as the
  confirmatory window, un-read in this build.

## 1. League format — the simplest in the program

- 18 teams, single double round-robin, 34 rounds, **306 matches per
  season, no split, no play-off groups, no points halving** — in
  every season of the corpus. Measured: exactly 18 team ids and 306
  matches in each of 2021/2022–2025/2026; 99 (11 rounds) in the
  partial 2026/2027.
- **The relegation play-off is NOT in this corpus.** FotMob files
  the 2. Bundesliga relegation play-off (16th vs 3rd of 3. Liga)
  under a separate tournament name; a full-corpus scan (run twice,
  independently) found all 1,629 files carrying
  `general.leagueName = '2. Bundesliga'` and zero carrying
  '2. Bundesliga Qualification'. The builder keeps a
  `qualification` phase flag as a guard: if a future pull ever adds
  such a match, the frozen rule is exclusion from every fit and
  scored window (its opponent is not a member of this league).
  On this corpus the flag never triggers: every row is `regular`.
- Team churn is heavy, as commissioned to check: 33 distinct team
  ids ever; **4–5 entrants every season** (2022/2023: 5,
  2023/2024: 5, 2024/2025: 5, 2025/2026: 4), arriving from BOTH
  neighbours — relegated from the Bundesliga (ids 54: e.g. Schalke
  04, Hertha BSC, 1. FC Köln) and promoted from 3. Liga (id 208:
  e.g. Kaiserslautern, Elversberg, Dynamo Dresden). Both neighbour
  leagues are in the warehouse, so entrant direction is known for
  every mover (name-matched against the neighbours' previous-season
  membership in the index; every entrant resolves to exactly one
  neighbour — `analysis/movers.py`). Direction-specific entrant
  performance is measured in EDA (F5): the two directions are NOT
  symmetric here.
- Big-club yo-yo traffic is real (Schalke 04, Hamburger SV, Hertha
  BSC, 1. FC Köln, VfL Bochum all appear) and trait spreads are
  wide: per-season team GF means run from 0.68 to 2.29, with the
  SD of team GF means at 0.34–0.39 per season (EDA).
- Calendar: autumn–spring (Aug–May) with a winter break.
  2026/2027 partial is running hot (10.23 SOT, 30.3 shots/match) —
  a level fact about the reserved window, not a modelling input.
- Team identity is keyed on FotMob team id everywhere (33 ids);
  several clubs appear under two display names under one id in the
  index (e.g. Kaiserslautern / 1.FC Kaiserslautern, Magdeburg /
  1.FC Magdeburg) — another reason ids, never names, key the data.

## 2. Coverage matrix (share of matches with real content)

| Season | n | Stats FT | Stats per half | Shotmap | xG (stats) | touches_opp_box | Referee (non-empty) |
|---|---|---|---|---|---|---|---|
| 2021/2022 | 306 | 100% | 0% | 100% | 100% | 68.0% | 46.4% |
| 2022/2023 | 306 | 100% | 26.8% | 100% | 100% | 60.8% | 98.4% |
| 2023/2024 | 306 | 100% | 100% | 100% | 100% | 80.1% | 99.7% |
| 2024/2025 | 306 | 100% | 100% | 100% | 100% | 100% | 99.0% |
| 2025/2026 | 306 | 100% | 100% | 100% | 100% | 100% | 88.2% |
| 2026/2027 (partial) | 99 | 100% | 100% | 100% | 100% | 100% | 100% |

- Per-half periods are absent in 2021/2022 and partial in
  2022/2023 (26.8%). Halves constants are measured on the complete
  era only (2023/2024–2025/2026), exactly as BE/CH/DK treated their
  partial eras.
- `expectedGoalsOnTarget` (xGOT) population break, same shape as
  BE/DK/CH: populated only for on-target shots through 2023/2024
  (~33% of shots), ~99.7% from 2024/2025. Any xGOT trait is
  era-guarded to 2024/2025 onward (and fails its check anyway, F8).
- Referee (`matchFacts.infoBox.Referee.text`): only 46.4%
  populated in 2021/2022 (verified on raw JSONs — the name is
  genuinely absent), then 88–100%. Overall coverage ≈ 90%.
- touches_opp_box: 61–80% before 2024/2025, 100% from 2024/2025 —
  the min-8 window rule absorbs the early gaps for the X7 arm.

## 3. Definition alignment (measured)

| Concept | Source | Check |
|---|---|---|
| FT score | `header.status.scoreStr` | source of truth |
| HT score | goal events `time ≤ 45` | events present in 100% of matches |
| SOT | stats feed `ShotsOnTarget` | correlates 0.996 with the shotmap aligned definition (on-target AND not blocked); stats feed is source of record |
| Total shots | stats feed `total_shots` | shotmap present 100%; stats feed is source of record |
| Cards | stats feed `yellow_cards` | **explicit feed check (§4)**; stats feed is the unified source |
| Team xG | stats feed `expected_goals` | goals/xG pooled ≈ 1.03; per season 0.96–1.06 — FotMob xG runs slightly LOW for DE-2 in the dev era; the blend input is usable in every season |

## 4. Cards feed check (run early, per the program's standing warning)

Three conveyor leagues found stats-feed card undercounts (one, NO,
needed an event-unified target via a documented prereg amendment),
so the check was run before any design decision, on all 1,629
matches (every match carries a stats-feed cards block):

- Exact total-yellows agreement stats vs events: **87.5%** of
  matches (identical 87.5% when second-yellow `YellowRed` events
  are added to the event count — the gap is not a second-yellow
  artefact; adding them makes the mean difference WORSE, −0.217).
- Direction: stats feed is **lower** than events in 12.0% of
  matches, higher in 0.5%; mean difference −0.126 yellows/match;
  max absolute difference 3.
- Verdict: this is the **same shape BE and DK measured** (86–88%
  exact, stats feed kept as the unified source) and far from the
  broken-feed shape that forced NO's amendment: one consistent
  source, consistently applied, with the event counts kept as
  cross-check columns (`ev_yellow_*`) for every row. The unified
  target is the stats feed; the −0.126/match tendency is a recorded
  level fact that the per-league fit absorbs. The sources are never
  mixed within the target. **No prereg amendment is needed.**

## 5. What this corpus has

- Full stats feed (xG with open-play/set-play/non-penalty splits,
  SOT, corners, cards, big chances, box touches) in every match
  from 2021/2022 — a full xG-era corpus, like BE/DK/CH, but with
  100% stats/shotmap coverage in ALL seasons.
- Per-half team stats from 2023/2024 (partial 2022/2023).
- Event timelines and shotmaps for 100% of matches.
- The program's simplest format (§1) paired with its heaviest
  two-direction churn — the mover question is this league's
  defining design problem, and both feeder tiers are in the
  warehouse to answer it with.
