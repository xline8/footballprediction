# Step 1 — Data Understanding: SE-Superettan (FotMob id 168)

Source: FotMob world warehouse, `data_enrichment/fotmob_world/Sweden/Superettan/<season>/<id>.json`,
index filter league_id = 168. One row per played match; 1,440 matches.

## Inventory (measured, `analysis/inventory_summary.json`, `analysis/eda.py`)

| Season | Matches | Dates | Stats keys present | Shotmap | Referee named |
|---|---|---|---|---|---|
| 2021 | 240 | 2021-04-10 – 2021-11-27 | **0 usable** (32 payloads carry an empty stats block) | 0 | 0 |
| 2022 | 240 | 2022-04-02 – 2022-11-05 | 240 | 0 | 0 |
| 2023 | 240 | 2023-04-01 – 2023-11-11 | 231 | 0 | 0 |
| 2024 | 240 | 2024-03-30 – 2024-11-09 | 240 | 0 | 0 |
| 2025 | 240 | 2025-03-29 – 2025-11-08 | 239 | 0 | 0 |
| 2026 | 240 | 2026-04-03 – 2026-11-07 | 237 | 0 | 0 |

- **Calendar**: calendar-year season, late March/April to early November. 16 teams,
  straight double round robin: exactly 30 rounds / 240 matches per season, and every
  team plays exactly 30 matches in every season (verified per season). No split,
  no championship/relegation rounds inside this league_id.
- **2026 is COMPLETE**: 240/240 matches with scores, final round all played
  2026-11-07, 16 teams x 30. It is the most recent complete season and is frozen
  as the virgin window (see MODEL_DESIGN). The Swedish season ends in November;
  unlike the parent Allsvenskan pull (224/240 at its build), nothing is outstanding here.
- **Play-offs (phase rule, frozen)**: Superettan has a promotion play-off (vs the
  Allsvenskan 14th club, two legs) and a relegation play-off (vs Division 1 clubs).
  The feed for league_id 168 contains NO play-off rows: every payload carries
  Tournament id 168 / parentLeagueId 168 and a round name in 1..30 (two 2021
  payloads lack a round name but are ordinary league fixtures by date/opponents —
  the corpus totals are exactly 240 = regular season in all six seasons, so there
  is no room for extra ties). Cross-tier play-off ties are therefore absent by
  construction, not excluded after the fact. Frozen rule: **corpus = the regular
  season only**, which is what the feed contains.
- **Stats feed is thin**: a single `top_stats` section in a single `All` period,
  with exactly four keys — `BallPossesion`, `total_shots`, `ShotsOnTarget`,
  `corners`. There are NO period splits (`FirstHalf`/`SecondHalf`) in any of the
  1,440 payloads, NO `expected_goals`, NO `big_chance`, NO `touches_opp_box`,
  NO card keys, in any season. `has_period_splits` is False for all 1,440 rows.
- **Missing stats, exactly**: 2021 — the whole season (208 payloads have no stats
  object; 32 have a stats object with zero usable keys; the 32 are scattered
  2021-05-17 – 2021-10-14, not a contiguous block). 2023 — 9 matches: 2023-04-24
  plus 7 of the 8 final-round matches on 2023-11-11 and one more that day.
  2025 — 1 match (2025-10-06). 2026 — 3 matches per the index (2026-04-06,
  2026-04-20 with no stats object, plus one empty stats block).
  Stats markets are therefore buildable only from 2022 onward, and their virgin
  (2026) contains the target in 237/240 matches.
- **Events**: present in 1,440/1,440 matches. Goal and Card events carry minute
  (`time`; 45 = first half incl. stoppage). This is the ONLY halves source in the
  league (goals, cards) and the ONLY cards source at all.
- **Cards stats-vs-events artefact check**: the usual artefact cannot occur here —
  the stats feed publishes no card keys, so there is no stats target to disagree
  with. The event feed carries plain Yellow events in every season (yellows/match
  3.67 / 4.24 / 4.04 / 3.92 / 3.53 / 3.17 by season — plausible, monotone-ish decline,
  no era flip of the TH/ZA kind). Frozen target: **event-derived unified yellows**
  (Yellow + YellowRed), for dev and virgin alike (see PREREG_K_SE2).
- **Referee**: `infoBox.Referee.text` is empty in 1,440/1,440 payloads. There is no
  referee identity anywhere in this league's feed.
- **xG / shotmap**: absent everywhere (`has_shotmap` False 1,440/1,440; no
  `expected_goals*` keys). Goals are a goals-only problem here.
- **Team identity**: 33 distinct FotMob team ids across six seasons. Names are NOT
  fully stable: id 8482 appears as both "AFC United" and "AFC Eskilstuna" (a club
  rename). All logic keys on team id.
- **Levels** (per match, EDA): goals 2.55–2.90; SOT 9.50–9.79 (2022–24), **12.33 in
  2025**, 8.57 in 2026; corners 9.67–10.59; total shots 19.5–21.6; yellows 3.17–4.24.
  The 2025 SOT spike is a regime anomaly: SOT per shot 0.571 in 2025 vs
  0.439–0.484 in all other stats seasons. Recorded before any fitting.
