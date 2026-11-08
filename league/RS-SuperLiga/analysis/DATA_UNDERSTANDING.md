# Step 1 — Data Understanding: RS-SuperLiga (FotMob id 182)

Source: FotMob world warehouse, `data_enrichment/fotmob_world/Serbia/Super Liga/<season>/<id>.json`,
index filter league_id = 182. One row per played match; 1,592 matches in the warehouse,
1,488 of which are in scope for this EDA (dev + virgin — see the reserve rule below).
Built CSVs: `data/rs_matches.csv` (1,592 rows = index count, verified in Phase 1)
+ `data/rs_team_matches.csv` (3,184 rows).

## Split rule (frozen, from BRIEF.md)

- **Dev = 2021/2022 – 2024/2025** (1,192 matches). **Virgin = 2025/2026** (296 matches,
  complete season, last match 2026-05-24 — `eda_summary.json: calendar`).
- **Reserve = 2026/2027 is excluded from every computation in `analysis/eda.py`**
  (`eda_summary.json: reserve_season_excluded`): its 104 CSV rows are filtered out first
  and its raw-JSON directory was never read. Nothing in this document uses a 2026/2027 number.
- Virgin rows are used in this EDA **only** for inventory purposes (feed coverage, levels)
  and for the two rich-era target-definition checks the Phase-2 task explicitly authorises
  (stats-vs-events cards; splits consistency). No virgin row chooses a feature, threshold,
  arm, or halves constant anywhere in steps 1–6.

## Inventory (measured, `analysis/inventory_summary.json`, `analysis/eda.py`)

| Season | Matches | Dates | Stats rows | Stats keys (All) | Period splits | Referee named (distinct) | Shotmap | Lineup full XI |
|---|---|---|---|---|---|---|---|---|
| 2021/2022 | 300 | 2021-07-16 – 2022-05-29 | 0 | 0 | no | 0 (0) | 0 | 0 |
| 2022/2023 | 300 | 2022-07-08 – 2023-06-04 | 0 | 0 | no | 0 (0) | 0 | 0 |
| 2023/2024 | 296 | 2023-07-29 – 2024-05-25 | 0 | 0 | no | 0 (0) | 0 | 0 |
| 2024/2025 | 296 | 2024-07-19 – 2025-05-25 | 0 | 0 | no | 0 (0) | 0 | 0 |
| 2025/2026 (virgin) | 296 | 2025-07-19 – 2026-05-24 | 296 | 36 | yes | 197 (23) | 0 | 296 |

- **Calendar / format**: split season (July/August – May/June), 18 teams in 2021/2022–2022/2023,
  16 teams from 2023/2024 (`eda_summary.json: teams_per_season`). Format per full season
  (`eda_summary.json: phase_counts`): regular 240 (double round robin, 30 rounds) +
  championship 28 + relegation 28. **Qualification 4 matches in 2021/2022 and 2022/2023 only** —
  two 2-legged relegation/promotion play-off ties (see below).
- **Phase rule (frozen)**: phases are taken from `general.leagueName` + `general.matchRound`
  (the 2025/2026 rename `Super Liga` → `Serbian Super Liga` moved the phase label into
  `matchRound`; `data/build_data.py` handles both). Regular / championship / relegation rows
  are ordinary rows with a `phase` flag. **Qualification rows are cross-tier and are excluded
  from fitting** (design justification in MODEL_DESIGN.md): each tie pits a Super Liga club
  against a Prva Liga (tier 2) club — FK Graficar and Indjija appear in the corpus ONLY as
  2022/2023 qualification opponents (`eda_summary.json: qualification_cross_tier_clubs`),
  2 matches each. The 8 qualification rows stay in `rs_matches.csv` with `phase=qualification`
  and in the levels table; they are out of the halves constant, the X2 measurement, and every fit.
- **Stats feed — a hard era break, not a gradient**:
  - 2021/2022–2024/2025: NO stats feed at all. `content.stats.Periods` is empty in 1,192/1,192
    dev payloads (`inventory_summary.json: by_season[].stats_matches` = 0). There is no thin era
    here, unlike FI (which had 4 keys in 2021–2024). SOT, corners, total shots, possession,
    touches, fouls, keeper saves — none of it exists before 2025/2026.
  - 2025/2026 (virgin): RICH, 36 keys in `All` with `FirstHalf`/`SecondHalf` splits on all
    296 matches (`inventory_summary.json: by_season.2025/2026.stats_keys_all`), internally
    consistent: All = FirstHalf + SecondHalf verified on 296 matches, 0 mismatches
    (`eda_summary.json: splits_consistency_corners_home_virgin_inventory`). The 36 keys are
    listed verbatim in `inventory_summary.json`.
  - **No xG in ANY season**: no `expected_goals*` key in any season's stats keys
    (`inventory_summary.json: has_expected_goals_key` = false everywhere), and `has_shotmap`
    is false for 1,488/1,488 in-scope matches. Goals are a goals-only problem (X1 falls back
    to goals-only, its documented fallback).
  - Coverage level tracks the break exactly: `lower` for all 1,192 dev matches, `ratings`
    for all 296 virgin matches (`eda_summary.json: coverage_level_by_season`).
- **Events**: present in 278 / 277 / 280 / 275 dev matches and 296/296 virgin matches
  (`inventory_summary.json: by_season[].events_matches`); **82 dev matches have NO events at all**
  (22 / 23 / 16 / 21 per season, `eda_summary.json: no_events_matches_dev`) — those matches
  have no HT goals and no event cards (missing, never zero-filled). Dev event types are ONLY
  Goal / Card / Half (`inventory_summary.json: by_season[].event_types`); the virgin adds
  AddedTime, Substitution, VAR, Comment, MissedPenalty.
- **Cards — the dev event feed is broken, not thin**: dev Card events carry NO plain `Yellow`
  at all. Card detail per season (`inventory_summary.json: by_season[].card_detail`):
  2021/2022 YellowRed 30 / Red 20 / Yellow 0; 2022/2023 YellowRed 36 / Red 30 / Yellow 0;
  2023/2024 YellowRed 27 / Red 24 / Yellow 0; 2024/2025 YellowRed 12 / Red 29 / Yellow 0.
  Event-derived yellows in dev are therefore YellowRed-only: 0.100 / 0.120 / 0.091 / 0.041 per
  match (`eda_summary.json: levels[].yellows_event`), against 4.662 in the virgin
  (Yellow 1,347 + YellowRed 33). The dev cards feed is unusable as a target, a feature,
  or a halves source — see EDA.md F6 and FEATURES.md X8/X5.
- **Cards stats-vs-events (rich era only, authorised check)**:
  virgin n = 296, exact agreement 72.6%, mean events 4.662 vs mean stats 4.230 per match,
  mean stats − events = −0.432 (`eda_summary.json: cards_stats_vs_events`). The stats feed
  NEVER exceeds events (81 matches ev > stats, 0 stats > ev): it systematically undercounts
  yellows against the event feed. This is the FI precedent for an event-unified target — but
  here it cannot rescue K-RS, because the event target itself is broken in dev (see above).
  The check is recorded for the record, not used to build anything.
- **Total-shots definition**: `total_shots` exists ONLY in the virgin season (25.084/match,
  `eda_summary.json: levels.2025/2026.shots`). There is no dev-era series to compare it
  against, so no dev definition check is possible at all — and no dev gate can validate an
  arm against the virgin's quantity. T-RS is not buildable on window grounds alone
  (MODEL_DESIGN.md), before any definition question even arises.
- **Lineups**: effectively absent before the virgin. Full XI on both sides in 0 dev matches
  (`inventory_summary.json: by_season[].lineup_full_xi_both_sides`): 2021/2022 has no lineup
  block at all (0/300); 2022/2023–2024/2025 have empty lineup shells (11 / 4 / 32 blocks with
  0 starters). The virgin has full XIs in 296/296. No lineup-based feature can be measured
  on dev.
- **Referee**: `infoBox.Referee.text` is empty in all 1,192 dev payloads; named in 197/296
  virgin matches across 23 distinct referees (`inventory_summary.json`). The referee trait
  cannot be measured on the dev era — X8 is dead on window grounds (FEATURES.md).
- **Team identity**: 25 distinct FotMob team ids across dev+virgin
  (`eda_summary.json: team_ids_total`; the pre-findings figure of 27 counts the full CSV
  including the excluded reserve season — see `eda_summary.json: team_ids_note`). **7 ids
  carry 2 name spellings** — all diacritic variants
  (`eda_summary.json: team_ids_multi_name`: e.g. 8687 `FK Crvena Zvezda` / `Red Star Belgrade`,
  6374 `Cukaricki` / `Čukarički`, 676140 `TSC Backa Topola` / `TSC Bačka Topola`,
  1739 `Mladost Lucani` / `Mladost Lučani`, 1675 `FK Radnicki 1923` / `FK Radnički 1923`,
  6410 `Radnicki Nis` / `Radnički Niš`, 676141 `Zeleznicar Pancevo` / `Železničar Pančevo`).
  All logic keys on team id, as in FI.
- **Levels** (per match, EDA.md F1): goals 2.563 / 2.430 / 2.770 / 2.882 in dev,
  2.662 in the virgin; home goals exceed away goals every season (1.357–1.544 vs 1.073–1.355).
  Virgin-only stats levels (inventory only): SOT 8.831, corners 9.003, total shots 25.084.
- **Data-quality notes** (measured in `eda.py`, recorded pre-fitting):
  - One awarded match: 4271663 (2023/2024, FK Radnicki 1923 vs FK Crvena Zvezda), awarded 0–3,
    but 7 Goal events (5 in 1H) are in the feed. FT score is authoritative; the match is
    excluded from the halves-goals computation (`eda_summary.json: halves_note_awarded_match`).
    Goal-events vs FT goals mismatch in exactly 1 match per affected season
    (`inventory_summary.json: goal_event_vs_ft_mismatch_matches`): 2021/2022 (match 3621462,
    Proleter vs Radnički Niš — 2 Goal events vs FT 3, one goal has no event although events
    exist) and 2023/2024 (the awarded match); 0 elsewhere.
  - No extra time, no shootout shots in any in-scope match (`rs_matches.csv`: `has_extra_time`
    = 0, `n_shootout_shots` = 0 everywhere). The qualification ties were decided over two legs
    on aggregate, not on penalties in this feed.
