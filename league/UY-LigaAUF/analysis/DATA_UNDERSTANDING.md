# Step 1 — Data Understanding: UY-LigaAUF

Uruguay Liga AUF Uruguaya, tier 1 (FotMob league_id 161). Warehouse
slice `data_enrichment/fotmob_world/Uruguay/Liga AUF Uruguaya/`,
1,717 played matches, calendar-year seasons 2021–2026. Index
`index_161.csv` (bundle `bundle-uy-liga`); CSV build matches the index
exactly (1,717/1,717 JSONs found, 0 missing, 0 duplicates, 0
unfinished). All numbers below trace to `analysis/eda_summary.json`
and `analysis/inventory_summary.json`.

## Format

- 16 teams per season, every season 2021–2026. 26 distinct team ids
  across the corpus (promotion/relegation churn).
- Season structure (from `general.leagueName`, mapped to a `phase`
  flag; all phases are ordinary rows, never excluded):
  Apertura 120 matches/season + Clausura 120 + Intermedio 57
  (two groups + final) + Final Stage 1–3. Totals: apertura 720,
  clausura 704, intermedio 285, final_stage 8.
- 2021 is short (241 matches): Apertura 120 + Clausura 120 + Final
  Stage 1, **no Intermedio** (57 matches) — the 2021 Intermedio was
  not played / is not in the warehouse. 2022–2025 are complete
  (297–300); 2026 is in progress (281, Apertura 120 + Clausura 104 +
  Intermedio 57, no Final Stage yet).
- Season totals: 2021: 241, 2022: 298, 2023: 300, 2024: 297,
  2025: 300, 2026: 281.

## Levels (goals/match, scoreStr)

2021: 2.531, 2022: 2.191, 2023: 2.287, 2024: 2.434, 2025: 2.333,
2026: 2.377. Total 4,040 goals in 1,717 matches (2.353/match).
Dev scored window 2022–2024 (n=895): home-win 0.381, draw 0.282,
away-win 0.337; OU2.5 over-rate 0.4045 (primary line, closest to 0.5
of 1.5/2.5/3.5 — over-rates 0.6715 / 0.4045 / 0.2045).

## Feed era structure (the finding that decides this league)

- **Stats feed: absent in EVERY season.** 0/1,717 matches with
  `content.stats.Periods`, 0 stats keys in any raw JSON, 0 period
  splits. Index `has_stats=False` for all 1,717 rows (verified in
  raw, not just the index). No `expected_goals*` key anywhere.
- **Shotmap: absent in EVERY season** (0/1,717; index
  `has_shotmap=False` for all rows).
- **Referee: absent in EVERY season** (0/1,717 named; infoBox
  Referee text empty everywhere).
- **Events: present in 1,679/1,717** (97.8%). Missing in 38 matches
  (2021: 15, 2022: 20, 2023: 3) — and all 38 are scoreless 0–0
  draws, i.e. the events payload is missing exactly for scoreless
  draws in 2021–2023. ScoreStr is the modelling score, so this does
  not touch goals; it only limits event-derived halves/card counts
  for those matches (kept missing, never zero-filled).
- **Lineup objects: 0 in 2021–2022, 278/300 in 2023, 297–300/season
  from 2024.** Irrelevant to the goals model (no lineup feature is
  proposed); recorded for completeness.
- **Cards (events):** plain Yellow Card events exist ONLY from 2023
  onward — 2021: Yellow 0, YellowRed 44, Red 40; 2022: Yellow 0,
  YellowRed 63, Red 63; 2023: Yellow 1,659; 2024: 1,597; 2025: 1,586;
  2026: 1,543. The event-derived yellows target therefore has a
  definition break inside dev (no yellows target in 2021–2022) —
  the K not-buildable reason (EDA.md F6).
- **Score vs events:** 2 mismatches in 1,679 event matches (0.12%).
  3834312 (Cerrito–Rentistas, 2022-03-11) is the league's single
  **awarded** match: scoreStr 0–3, events 2–1 (on-field score before
  the award). 4425121 (Defensor Sporting–Cerro, 2024-02-25):
  scoreStr 5–0 vs 6 Goal events (one feed-duplicated goal event).
  scoreStr is authoritative in both cases (PLAYBOOK rule); the two
  matches are excluded from the event-time halves share.
- Team ids carry one canonical name each after canonicalisation of
  three accent variants (Progreso, Peñarol, Central Español);
  see PREPROCESSING.md.

## Split (frozen)

Dev ≤ 2024 (warm-up 2021, scored 2022–2024, n=895); virgin = 2025
(complete, n=300), read once and only for dev-passing arms;
2026 (n=281) untouched confirmatory reserve. The split is the
BRIEF's suggested split, frozen here before any fitting.
