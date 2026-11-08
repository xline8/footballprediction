# Step 1 — Data Understanding: EC-SerieA (FotMob id 246)

Source: FotMob world warehouse, `data_enrichment/fotmob_world/Ecuador/Serie A/<year>/*.json`,
index filter league_id = 246 (`index_246.csv`, 1,565 rows). One row per played match.
All numbers measured by `analysis/eda.py` (`analysis/eda_summary.json`).

## Inventory

| Season | Matches | Stats rows | Period splits | Events rows | Lineup (11) | Referee named | Goals/match |
|---|---|---|---|---|---|---|---|
| 2021 | 242 | 0 | 0 | 229 | 0 | 0 | 2.719 |
| 2022 | 242 | 0 | 0 | 225 | 0 | 0 | 2.426 |
| 2023 | 242 | 0 | 0 | 220 | 0 | 0 | 2.471 |
| 2024 | 242 | 1 | 0 | 228 | 1 | 0 | 2.628 |
| 2025 | 312 | 311 | 311 | 311 | 311 | 73 | 2.554 |
| 2026 | 285 (in progress) | 285 | 285 | 285 | 285 | 87 | 2.337 |

- **Format**: 16 teams every season; 23 distinct FotMob team ids across the
  corpus. 2021–2024: First Stage 120 + Second Stage 120 + Final Stage 2
  matches per season (two single round robins + a 2-match final) = 242.
  2025–2026: format change — `leagueName` becomes `Ecuador Liga Pro`
  (236 in 2025, 16 in 2026) / `Serie A` (76 in 2025, 269 in 2026), 312
  matches in 2025, 285 played so far in 2026. All phases are ordinary
  rows with a `phase` flag; nothing is dropped. 2026 is in progress and
  stays **untouched** as confirmatory reserve.
- **Stats feed — the era break is at 2025, not in dev.** 0% in
  2021–2023, 1 match in 2024 (All period only, no splits), 311/312 in
  2025, 285/285 in 2026 (38.1% overall, matching the brief's total; the
  brief's "71.2% across the last three seasons" is (1+311+285)/839 and
  is entirely concentrated in 2025–2026). Consequence, decided in EDA:
  **dev ≤ 2024 contains no stats target at all**, so SOT / corners /
  total shots / yellows have no dev scored window and are
  not-buildable under the frozen split (see EDA.md / MODEL_DESIGN.md).
- **Stats feed content (rich era, 2025–2026)**: 36 distinct keys per
  period (All / FirstHalf / SecondHalf), incl. `total_shots`,
  `ShotsOnTarget`, `ShotsOffTarget`, `blocked_shots`,
  `shots_inside_box`, `shots_outside_box`, `big_chance`,
  `touches_opp_box`, `corners`, `yellow_cards`, `red_cards`, `fouls`,
  `Offsides`, `keeper_saves`, `BallPossesion`, passing keys. Splits are
  internally consistent: All = FirstHalf + SecondHalf exactly in
  311/311 2025 matches for total shots, corners, and SOT.
- **No xG anywhere**: zero `expected_goals*` entries in any payload, any
  season. No shotmap anywhere (`has_shotmap` false for 1,565/1,565).
  Goals is a goals-only problem (X1 documented fallback); every
  shotmap/xG arm is impossible by absence and is recorded as such,
  never faked.
- **Event feed — goals yes, cards era-dependent**: goal events reconcile
  with the header score in all but 2 of 1,498 event-carrying matches
  (3528060 in 2021 and 3816510 in 2022, both header 3–0 vs events 2–0;
  header score is authoritative). Card events in 2021–2024 are ONLY
  Red (240) and YellowRed (170) — **zero plain Yellow events in the
  whole dev era** — so event-derived yellows in dev would count second
  yellows only (~0.2/match) and are not a yellow-card total. From 2025
  the event feed carries plain Yellows (1,330 in 2025, 1,280 in 2026).
  Cards target is stats yellows (which exist only from 2025); see
  PREPROCESSING / MODEL_DESIGN.
- **Stats-vs-events yellows (2025, descriptive feed check only)**:
  n=311, exact agreement 80.1%, mean stats − events −0.36/match
  (events count slightly more; the two feeds are not interchangeable,
  and neither has a dev window to validate against).
- **Empty-events matches**: 67 matches have an entirely empty events
  payload (13/17/22/14 in 2021–2024, 1 in 2025). Unlike CH, they are
  NOT all scoreless: 6 goals in total across them (mean 0.09/match),
  and the single 2025 one (1000004645, El Nacional 0–3 Delfin) is also
  the only 2025 match without a stats feed. All events-derived fields
  for these matches are missing (never zero). See PREPROCESSING.
- **Lineups**: a `lineup` object is present in only 16/2/0/1 matches in
  2021–2024 (and never with 11 starters except the single 2024 stats
  match), vs 311/311 in 2025 and 285/285 in 2026. No lineup feature is
  attempted.
- **Referee**: `content.matchFacts.infoBox.Referee.text` is empty in
  every 2021–2024 match (0% coverage in dev). Named referees appear
  only from 2025: 73/312 in 2025 (18 distinct, most frequent Robert
  Cabrera, 9 matches), 87/285 in 2026 (20 distinct). No referee feature
  is attempted in dev (X8 dropped, FEATURES.md).
- **Team-name stability**: 23 FotMob team ids; 4 ids carry two spellings
  (accent variants) — 6609 `CSD Macara` (90) vs `CSD Macará` (76),
  113054 `Tecnico Universitario` (120) vs `Técnico Universitario` (71),
  519457 `Delfin` (120) vs `Delfín` (75), 113053 `Universidad Catolica`
  (120) vs `Universidad Católica` (76). Canonicalised to the most
  frequent (unaccented) spelling in the builder; all logic keyed by
  team id.
