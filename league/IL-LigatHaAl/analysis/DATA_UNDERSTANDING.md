# Step 1 — Data Understanding: IL-LigatHaAl (FotMob id 127)

Source: FotMob world warehouse, `data_enrichment/fotmob_world/Israel/Ligat ha'Al/<season dir like 2021-2022>/*.json`,
index filter league_id = 127 (`index_127.csv`, 1,270 rows). One row per played match.
All numbers measured by `analysis/eda.py` (`analysis/eda_summary.json`).

## Inventory

| Season | Matches | Stats rows | Period splits | Events rows | Lineup (11) | Referee named | Goals/match |
|---|---|---|---|---|---|---|---|
| 2021/2022 | 240 | 0 | 0 | 224 | 0 | 0 | 2.471 |
| 2022/2023 | 240 | 0 | 0 | 228 | 0 | 0 | 2.642 |
| 2023/2024 | 240 | 0 | 0 | 230 | 0 | 0 | 2.542 |
| 2024/2025 | 240 | 0 | 0 | 223 | 0 | 0 | 2.783 |
| 2025/2026 | 240 | 239 | 239 | 239 | 239 | 64 | 2.967 |
| 2026/2027 | 70 (in progress) | 69 | 69 | 69 | 70 | 70 | 3.000 |

- **Format**: 14 teams every season; 19 distinct FotMob team ids across the
  corpus. Every full season: regular 182 + championship group 30 +
  relegation group 28 = 240 (26 regular rounds x 7 matches, then 10
  championship rounds x 3 and 7 relegation rounds x 4). All phases are
  ordinary rows with a `phase` flag; nothing is dropped. 2026/2027 is in
  progress (70 regular-round matches so far) and stays **untouched** as
  confirmatory reserve.
- **Stats feed — the era break is at 2025/2026, not in dev.** 0% in
  2021/2022–2024/2025, 239/240 in 2025/2026, 69/70 in 2026/2027
  (24.3% overall, 56.0% across the last three seasons, matching the
  brief). Consequence, decided in EDA: **dev ≤ 2024/2025 contains no
  stats target at all**, so SOT / corners / total shots / yellows have
  no dev scored window and are not-buildable under the frozen split
  (see EDA.md / MODEL_DESIGN.md).
- **Stats feed content (rich era, 2025/2026–2026/2027)**: 36 distinct keys
  per period (All / FirstHalf / SecondHalf), incl. `total_shots`,
  `ShotsOnTarget`, `ShotsOffTarget`, `blocked_shots`,
  `shots_inside_box`, `shots_outside_box`, `big_chance`,
  `touches_opp_box`, `corners`, `yellow_cards`, `red_cards`, `fouls`,
  `Offsides`, `keeper_saves`, `BallPossesion`, passing keys. Splits are
  internally consistent: All = FirstHalf + SecondHalf exactly in
  239/239 2025/2026 matches for total shots, corners, and SOT.
- **No xG anywhere**: zero `expected_goals*` entries in any payload, any
  season. No shotmap anywhere (`has_shotmap` false for 1,270/1,270).
  Goals is a goals-only problem (X1 documented fallback); every
  shotmap/xG arm is impossible by absence and is recorded as such,
  never faked.
- **Event feed — goals yes, cards era-dependent**: goal events reconcile
  with the header score in all but 3 of 1,213 event-carrying matches —
  and all 3 are awarded wins (3606698 in 2021/2022, 4516796 and 4516800
  in 2024/2025; header 3–0 / 0–3 vs on-pitch events 1–1; header score
  is authoritative). 7 awarded matches in total. Card events in
  2021/2022–2024/2025 are ONLY Red (185) and YellowRed (98) —
  **zero plain Yellow events in the whole dev era** — so event-derived
  yellows in dev would count second yellows only (~0.1/match) and are
  not a yellow-card total. From 2025/2026 the event feed carries plain
  Yellows (1,230 in 2025/2026, 342 in 2026/2027). Cards target is stats
  yellows (which exist only from 2025/2026); see PREPROCESSING /
  MODEL_DESIGN.
- **Stats-vs-events yellows (2025/2026, descriptive feed check only)**:
  n=239, exact agreement 68.6%, mean stats − events −0.53/match
  (events count more; the two feeds are not interchangeable, and
  neither has a dev window to validate against). The gap is largely
  mechanical: the event count adds YellowRed (second yellows) on top
  of plain Yellows, while the stats feed books a second yellow as a
  red.
- **Empty-events matches**: 57 matches have an entirely empty events
  payload (16/12/10/17 in 2021/2022–2024/2025, 1 in 2025/2026, 1 in
  2026/2027). They are NOT all scoreless: 9 goals in total across them
  (mean 0.16/match). The single 2025/2026 one (4864314, Hapoel Tel Aviv
  0–3 Maccabi Tel Aviv, 2025-10-19) is an awarded derby and is also
  the only 2025/2026 match without a stats feed. All events-derived
  fields for these matches are missing (never zero). See PREPROCESSING.
- **Lineups**: a `lineup` object is present in 0 matches in
  2021/2022–2023/2024, in 6 matches in 2024/2025 — but as an empty
  shell (0 starters, no formation) — vs 239/239 in 2025/2026 and 70/70
  in 2026/2027. No lineup feature is attempted.
- **Referee**: `content.matchFacts.infoBox.Referee.text` is empty in
  every 2021/2022–2024/2025 match (0% coverage in dev). Named referees
  appear only from 2025/2026: 64/240 in 2025/2026 (21 distinct, most
  frequent Gal Laibuvitz, 7 matches), 70/70 in 2026/2027 (15 distinct).
  No referee feature is attempted in dev (X8 dropped, FEATURES.md).
- **Team-name stability**: 19 FotMob team ids, each carrying exactly one
  spelling across the whole corpus — no canonicalisation needed. All
  logic is keyed by FotMob team id.
- **Scoring level is rising**: goals/match 2.471 / 2.642 / 2.542 / 2.783
  across the four dev seasons (scored window 2022/2023–2024/2025 mean
  2.656), then 2.967 in the virgin season 2025/2026 and 3.000 so far in
  2026/2027. The virgin level sits +0.31 goals/match above the dev
  scored mean — a flagged calibration risk for the goals gates
  (recorded here, NOT used to adjust anything: the gates are frozen
  and the virgin is read once).
