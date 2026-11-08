# Step 1 — Data Understanding: CH-ChallengeLeague (FotMob id 163)

Source: FotMob world warehouse, `data_enrichment/fotmob_world/Switzerland/Challenge League/<season>/*.json`,
index filter league_id = 163 (`index_163.csv`, 966 rows). One row per played match.
All numbers measured by `analysis/eda.py` (`analysis/eda_summary.json`).

## Inventory

| Season | Matches | Stats rows | Period splits | Events rows | Goals/match |
|---|---|---|---|---|---|
| 2021/2022 | 180 | 0 | 0 | 170 | 3.250 |
| 2022/2023 | 180 | 0 | 0 | 173 | 3.133 |
| 2023/2024 | 180 | 180 | 180 | 170 | 2.872 |
| 2024/2025 | 180 | 180 | 180 | 170 | 3.000 |
| 2025/2026 | 181 | 181 | 179 | 171 | 3.050 |
| 2026/2027 | 65 (in progress) | 65 | 65 | 65 | 3.108 |

- **Format**: 10 teams, quadruple round robin = 180 matches per full season.
  2025/2026 has 181 — one extra row versus the format (recorded as found;
  it is the virgin season and is used complete, as-is). 2026/2027 is in
  progress (65 played) and stays **untouched** by this build.
- **Teams**: 17 distinct FotMob team ids across the corpus, 10 per season;
  all logic keyed by team id.
- **Stats feed — era break at 2023/2024** (differs from the brief's guess):
  0% in 2021/2022 and 2022/2023, 100% from 2023/2024 onward (62.7% overall,
  matching the brief's total). The rich era is a single consistent feed:
  36 keys incl. period splits (All = FirstHalf + SecondHalf), card keys,
  `big_chance`, `touches_opp_box`, possession. Splits present in 100% of
  stats rows except 2025/2026 (179/181).
- **No xG anywhere**: zero `expected_goals*` entries in any payload, any
  season. No shotmap anywhere (`has_shotmap` false for 966/966). Goals is
  a goals-only problem (X1 documented fallback); every shotmap/xG arm is
  impossible by absence and is recorded as such, never faked.
- **Event feed — goals yes, cards (almost) no**: goal events reconcile
  with the header score in all but 2 of 919 event-carrying matches (both
  2024/2025; header score is authoritative). But card events are
  essentially ABSENT in 2021/2022–2025/2026: 0.16 / 0.16 / 0.12 / 0.05 /
  0.01 event yellows per match versus 4.58 / 5.01 / 4.59 in the stats feed
  where both exist (exact agreement only 10.6%, mean stats − events
  +4.12/match). The event feed only starts carrying cards in 2026/2027
  (4.48/match). Consequence: the cards target is the **stats feed**, and
  cards exist only from 2023/2024 — see PREPROCESSING / MODEL_DESIGN.
- **Empty-events matches**: 47 matches have an entirely empty events
  payload; every one is 0–0, and the 30 of them in the stats era carry a
  mean of 4.4 stats yellows — the payload is missing, not empty of
  incident. All events-derived fields for those matches are missing
  (never zero). See PREPROCESSING.
- **Lineups**: 100% in the index. Referee names were not found in the
  payload structure used by the builder; no referee feature is attempted
  (X8 dropped, FEATURES.md).
