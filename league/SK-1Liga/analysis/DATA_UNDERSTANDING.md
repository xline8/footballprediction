# Step 1 — Data Understanding (SK-1Liga, Slovakia 1. liga, FotMob id 176)

Source: FotMob world warehouse, index
`data_enrichment/fotmob_world_index.csv` filtered to `league_id = 176`;
payloads at `data_enrichment/fotmob_world/Slovakia/1. liga/<season>/<id>.json`
in the main repo. Builder: `data/build_data.py` (ported from the
CZ-Liga builder; the payload shape is identical).

## Inventory

- 1,053 matches: seasons 2021/2022–2025/2026 complete
  (195 / 195 / 192 / 195 / 192 rows) plus 2026/2027 in progress
  (84 rows, regular phase only, up to 2026-11-08).
- Format (verified from the payloads, `general.leagueName`): 12 clubs;
  regular phase 22 rounds (132 matches), then a split — Championship
  Group (top 6, 30 matches) and Relegation Group (bottom 6,
  30 matches) — 192 league matches per complete season. Split groups
  are separate FotMob sub-leagues (own `leagueId` per season) with
  round numbering restarting inside the group.
- European play-off: `Super Liga / 1. Liga ECL Playoff` sub-league —
  3 one-off ties (2 semifinals + 1 final) present in the feed in
  2021/2022, 2022/2023 and 2024/2025; **absent from the feed in
  2023/2024 and 2025/2026** (those seasons total exactly 192 rows).
  The build cannot distinguish "not held" from "not in feed"; the
  feed fact is what is recorded.
- The competition was renamed mid-2024/2025: payload league names
  change from `Super Liga …` to `1. Liga …` inside that season
  (4 regular + split rows carry each name). Same competition,
  same FotMob parent id 176.

## Field coverage (per season, all rows)

| Season | Rows | Stats | Period splits | Referee named | xG | Shotmap |
|---|---|---|---|---|---|---|
| 2021/2022 | 195 | 134 | 0 | 0 | 0 | 0 |
| 2022/2023 | 195 | 195 | 0 | 0 | 0 | 0 |
| 2023/2024 | 192 | 187 | 0 | 0 | 0 | 0 |
| 2024/2025 | 195 | 192 | 0 | 0 | 0 | 0 |
| 2025/2026 | 192 | 192 | 192 | 174 | 0 | 0 |
| 2026/2027 | 84 | 84 | 84 | 84 | 0 | 0 |

- Dev-era stats (`Periods.All`) carry only four keys:
  `BallPossesion`, `total_shots`, `ShotsOnTarget`, `corners`.
  The rich feed (yellow/red cards, `big_chance`, `touches_opp_box`,
  off-target/blocked shots, fouls, …) and the FirstHalf/SecondHalf
  period splits begin exactly with the virgin season 2025/2026.
- Events (goals, cards, substitutions, with minutes) are present in
  every match except one (defect 4). Event goal totals reconcile
  with `header.status.scoreStr` in 1,052 of 1,053 matches.

## Defects and quirks (all verified against the payloads)

1. **Total-shots definition break at the rich-feed boundary.**
   Dev-era `total_shots` means ≈ 19.8 / 20.2 / 17.8 / 19.2 per match
   jump to 27.1 in 2025/2026 (+~40%) while SOT, corners and goals
   are continuous across the same boundary. The dev-era key plainly
   counts a narrower quantity than the rich-era key. Consequence:
   T-SK is not buildable (Step 6), and the S-SK engine's shots input
   carries a declared risk (CZ/RO precedent).
2. **Stats feed starts mid-2021/2022.** The first 61 matches of
   2021/2022 (2021-07-23 → 2021-10-17) have no stats block at all;
   included-row stats coverage is 131/192 that season. One full
   round in 2023/2024 (2023-11-11/12, 5 matches) is also missing
   stats. All other included rows have stats (192 / 187 / 189 / 192
   for 2022/2023–2025/2026).
3. **No referee names in the dev era.** `infoBox.Referee.text` is
   empty in all 777 dev-era matches; names appear only from
   2025/2026 (174/192) and 2026/2027 (84/84). X8 is untestable.
4. **One match with an empty events list**: 2021-10-17, Spartak
   Trnava 0–3 Slovan Bratislava (id 3606259). Its event-derived
   fields (HT goals, event yellows) are zero in the feed — not a
   real 0 — while the score is present. It is 1 of 768 dev cards
   rows; the halves/card aggregates move by <0.2% if it is dropped,
   so it is kept and flagged, not silently repaired.
5. **No stats-feed cards key in the dev era.** `yellow_cards`
   exists in exactly 1 of 768 dev-era included matches. The cards
   target is therefore event yellows **by construction** (see
   PREPROCESSING and EDA F6 for the virgin-era artefact audit:
   where both exist they agree closely — no era artefact).
6. **Team display names are unstable; ids are stable.** The index
   carries diacritic variants of the same clubs in 2026/2027
   (`Ruzomberok` / `Ružomberok`, `Zilina` / `Žilina`, …). All logic
   keys on FotMob team ids from the payloads; 18 distinct ids appear
   across the six seasons (12 per season).
7. **No xG, no shotmap, ever.** `expected_goals` appears in zero
   payloads and `content.shotmap.shots` is empty in all 1,053.
   The goals model is goals-only; X3/X4/X6 have no data.
8. **2026/2027 levels are not comparable** (84 regular-phase matches
   of an in-progress season, goals 3.27/match so far). The season is
   inventory only in this build and is never read by any harness.
