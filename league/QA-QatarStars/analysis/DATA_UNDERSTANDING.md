# Step 1 — Data Understanding: QA-QatarStars (FotMob id 535)

Source: FotMob world warehouse, `data_enrichment/Qatar/Qatar Stars League/<2021-2022 ...>/*.json`
(release `bundle-qa-qsl`), index filter league_id = 535 (`index_535.csv`, 714 rows).
One row per played match. All numbers measured by `analysis/eda.py`
(`analysis/eda_summary.json`).

## Inventory

| Season | Matches | Stats rows | Period splits | Events rows | Lineup (11) | Referee named | Goals/match |
|---|---|---|---|---|---|---|---|
| 2021/2022 | 132 | 0 | 0 | 123 | 0 | 0 | 3.212 |
| 2022/2023 | 132 | 0 | 0 | 128 | 0 | 0 | 3.045 |
| 2023/2024 | 132 | 0 | 0 | 127 | 0 | 0 | 3.652 |
| 2024/2025 | 132 | 1 | 0 | 128 | 1 | 0 | 3.348 |
| 2025/2026 | 132 | 132 | 132 | 127 | 132 | 9 | 3.318 |
| 2026/2027 | 54 (in progress) | 54 | 54 | 54 | 54 | 53 | 3.630 |

- **Format**: 12 teams every season; 16 distinct FotMob team ids across the
  corpus. Every season is a double round robin (22 rounds × 6 matches =
  132). `general.leagueName` is `Qatar Stars League` in all 714 JSONs, so
  there is a single phase (`regular`) for every row — no championship /
  relegation split, no final stage. All rows are ordinary rows; nothing
  is dropped. 2026/2027 is in progress and stays **untouched** as
  confirmatory reserve.
- **Stats feed — the era break is at 2025/2026, not in dev.** 0% in
  2021/2022–2023/2024, 1 match in 2024/2025 (All period only, no
  splits), 132/132 in 2025/2026, 54/54 in 2026/2027 (26.2% overall,
  58.8% across the last three seasons, matching the brief; the share is
  entirely concentrated in 2025/2026–2026/2027). Consequence, decided
  in EDA: **dev ≤ 2024/2025 contains no stats target at all**, so SOT /
  corners / total shots / yellows have no dev scored window and are
  not-buildable under the frozen split (see EDA.md / MODEL_DESIGN.md).
- **Stats feed content (rich era, 2025/2026–2026/2027)**: 36 distinct
  keys per period (All / FirstHalf / SecondHalf), incl. `total_shots`,
  `ShotsOnTarget`, `ShotsOffTarget`, `blocked_shots`,
  `shots_inside_box`, `shots_outside_box`, `big_chance`,
  `touches_opp_box`, `corners`, `yellow_cards`, `red_cards`, `fouls`,
  `Offsides`, `keeper_saves`, `BallPossesion`, passing keys. Splits are
  internally consistent: All = FirstHalf + SecondHalf exactly in
  132/132 2025/2026 matches for total shots, corners, and SOT, and in
  130/132 for yellow_cards (2 matches off by one — descriptive only).
- **No xG anywhere**: zero `expected_goals*` entries in any payload, any
  season. No shotmap anywhere (`has_shotmap` false for 714/714).
  Goals is a goals-only problem (X1 documented fallback); every
  shotmap/xG arm is impossible by absence and is recorded as such,
  never faked.
- **Event feed — goals yes, cards era-dependent**: goal events reconcile
  with the header score in all but 3 of 687 event-carrying matches
  (4543706 in 2024/2025 — a duplicated Goal event at 7', header 0–1;
  5099043 and 5099029 in 2025/2026 — corrupt/flipped goal events vs
  header 3–0; header score is authoritative). Card events in
  2021/2022–2025/2026 are ONLY Red (83 in dev, 38 in 2025/2026) and
  YellowRed (50 in dev, 0 in 2025/2026) — **zero plain Yellow events
  in the whole dev era and in the virgin season** — so event-derived
  yellows in dev would count second yellows only (~0.2/match) and are
  not a yellow-card total. Plain Yellow events appear only in
  2026/2027 (230). Cards target is stats yellows (which exist only
  from 2025/2026); see PREPROCESSING / MODEL_DESIGN.
- **Stats-vs-events yellows (2025/2026, descriptive feed check only)**:
  n=182, exact agreement 25.8%, mean stats − events +3.22/match
  (the event feed counts only reds/second yellows there, so the gap is
  structural, not noise; neither feed has a dev window to validate
  against).
- **Empty-events matches**: 27 matches have an entirely empty events
  payload (9/4/5/4/5 in 2021/2022–2025/2026). They are ALL scoreless
  (0–0, 0 goals total), so no goal information is lost, but every
  events-derived field for these matches is missing (never zero). The
  5 empty-events matches in 2025/2026 do carry stats yellows
  (mean 4.2/match). See PREPROCESSING.
- **Lineups**: a `lineup` object is present in only 6/0/0/1 matches in
  2021/2022–2024/2025 (and never with 11 starters except the single
  2024/2025 stats match), vs 132/132 in 2025/2026 and 54/54 in
  2026/2027. No lineup feature is attempted.
- **Referee**: `content.matchFacts.infoBox.Referee.text` is empty in
  every 2021/2022–2024/2025 match (0% coverage in dev). Named referees
  appear only from 2025/2026: 9/132 in 2025/2026 (7 distinct, most
  frequent Abdulla Ali Al Athba Al Marri and Abdulhadi Al Asmar Al
  Ruaile, 2 matches each), 53/54 in 2026/2027 (13 distinct). No
  referee feature is attempted in dev (X8 dropped, FEATURES.md).
- **Team-name stability**: 16 FotMob team ids; every id carries exactly
  one spelling across the corpus. All logic is keyed by FotMob team id.
