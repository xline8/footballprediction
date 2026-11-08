# Step 1 — Data Understanding: QA-SecondDivision (FotMob id 11030)

Source: FotMob world warehouse, `data_enrichment/fotmob_world/Qatar/Second Division/<2024-2025 ...>/*.json`
(index filter league_id = 11030, 141 rows). One row per played match. All numbers measured by `analysis/eda.py`
(`analysis/eda_summary.json`); the builder is `data/build_data.py` (`data/qasd_matches.csv`,
`data/qasd_team_matches.csv`).

## Inventory

| Season | Matches | Stats rows | Period splits | Events rows | Lineup (11) | Referee named | Goals/match |
|---|---|---|---|---|---|---|---|
| 2024/2025 | 56 | 38 | 38 | 56 | 56 | 0 | 2.607 |
| 2025/2026 | 56 | 56 | 56 | 56 | 56 | 0 | 3.018 |
| 2026/2027 | 29 (in progress) | 29 | 29 | 29 | 29 | 1 | 2.759 |

- **Format**: 8 teams in each complete season; every complete season is a double round robin
  (14 rounds × 4 matches = 56). `general.leagueName` is `Qatar Stars League 2` in 123/141 JSONs;
  18 carry `Second Division` instead (10 in 2025/2026 — all Lusail SC, rounds 5–14 — and 8 in
  2026/2027, rounds 5–6). Same 8 teams, same round sequence, no playoff or split phase anywhere:
  this is a naming quirk, not a format change. There is a single phase (`regular`) for every row.
  2026/2027 has **11 teams** (5 matches/round, one bye per round); round 5 has 4 matches instead
  of 5 — presumably one postponed fixture, not in the warehouse as played. Nothing is dropped.
- **Stats feed — the era break is INSIDE 2024/2025, not between seasons.** Rounds 1–5 are
  essentially stat-less (0, 1, 0, 0, 1 matches with stats in rounds 1–5), rounds 6–14 are full
  (38 matches). 2025/2026 is 56/56, 2026/2027 is 29/29. The index's `has_stats` flag agrees
  with the payload audit exactly (123 flagged, 123 with non-null stats) — but that was verified
  from payloads, not assumed: the flag tests key presence, and this league's keys are genuinely
  populated where flagged.
- **Stats feed content (33 keys per period: All / FirstHalf / SecondHalf)**: `total_shots`,
  `ShotsOnTarget`, `ShotsOffTarget`, `blocked_shots`, `corners`, `yellow_cards`, `red_cards`,
  `fouls`, `Offsides`, `keeper_saves`, `BallPossesion`, passing keys, duels, clearances,
  interceptions. Splits are internally consistent: All = FirstHalf + SecondHalf exactly in
  **123/123** stats matches for total shots, corners, SOT, and yellow_cards.
- **No xG anywhere**: zero `expected_goals*` entries in any payload, any season. No shotmap
  anywhere (0 shots in all 141 `shotmap.shots` payloads). No `touches_opp_box` key anywhere.
  Goals is a goals-only problem (X1 documented fallback); every shotmap/xG arm is impossible
  by absence and is recorded as such, never faked.
- **Degenerate keys**: `big_chance`, `shots_inside_box`, `shots_outside_box` exist as keys but
  are 0/0 in every match of every season. They carry no information and are never used.
- **Event feed — goals reconcile perfectly**: goal events match the header score in **141/141**
  matches (0 mismatches). Card events are plentiful, unlike the parent league's dev era:
  Yellow 289 / YellowRed 5 / Red 4 in 2024/2025; 282 / 10 / 3 in 2025/2026; 117 / 4 / 8 in
  2026/2027. No empty-events matches (0/141).
- **Stats-vs-events yellows (the K target decision)**: the stats feed undercounts the event
  feed one-directionally — 2024/2025: 34 exact / 4 low / 0 high, mean −0.21; 2025/2026:
  37 / 19 / 0, mean −0.52; pooled pre-virgin 71 / 23 / 0, mean −0.40. The K target is therefore
  **event-unified (Yellow + YellowRed)**, following the SA-FirstDivision precedent; stats
  yellows are kept alongside as evidence columns only. See PREPROCESSING.
- **Lineups**: a `lineup` object with 11 starters is present in **141/141** matches (both sides).
  No lineup feature is attempted (R6 closed — see FEATURES.md).
- **Referee**: `content.matchFacts.infoBox.Referee.text` is empty in every 2024/2025 and
  2025/2026 match (0% coverage in both dev seasons). One named referee appears in 2026/2027
  (Farhan Al Ruaili, 1 match). No referee feature is attempted in dev (X8 dropped, FEATURES.md).
- **Team-name stability**: 13 FotMob team ids; every id carries exactly one spelling across the
  corpus. All logic is keyed by FotMob team id (from `content.lineup.*Team.id`).
- **Team turnover is high**: 8 teams in 2024/2025; Al-Sailiya out, Al-Khor in for 2025/2026;
  Lusail SC out and four first-season teams in for 2026/2027 (reserve sides Al-Gharafa II,
  Al-Rayyan II, Al-Shamal II, plus Umm Salal). The 2026/2027 entrants are virgin-season facts
  for every candidate — their performance is not recorded in any design document.
- **Home advantage is near-absent, like the parent league**: home vs away goals/match —
  2024/2025: 1.446 vs 1.161; 2025/2026: 1.429 vs **1.589** (away teams outscore home teams);
  2026/2027: 1.310 vs 1.448. Home-win rates 39.3% / 32.1% / 34.5%; draws 30.4% / 23.2% / 20.7%.
