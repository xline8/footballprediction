# Step 1 — Data Understanding: FI-Veikkausliiga (FotMob id 51)

Source: FotMob world warehouse, `data_enrichment/fotmob_world/Finland/Veikkausliiga/<season>/<id>.json`,
index filter league_id = 51. One row per played match; 1,017 matches.

## Inventory (measured, `analysis/inventory_summary.json`, `analysis/eda.py`)

| Season | Matches | Dates | Stats rows | Period splits | Referee named |
|---|---|---|---|---|---|
| 2021 | 162 | 2021-04-24 – 2021-10-31 | 130 | no | 0 |
| 2022 | 167 | 2022-04-02 – 2022-10-30 | 167 | no | 0 |
| 2023 | 167 | 2023-04-05 – 2023-11-05 | 167 | no | 0 |
| 2024 | 167 | 2024-04-06 – 2024-11-02 | 167 | no | 0 |
| 2025 | 177 | 2025-04-05 – 2025-11-09 | 177 | **yes** | 36 |
| 2026 | 177 | 2026-04-04 – 2026-11-08 | 177 | **yes** | 96 |

- **Calendar / format**: calendar-year season (April – early November), 12 teams.
  The feed's own `general.leagueName` names the phase of every match:
  - Regular phase: 132 matches (double round robin, 22 rounds) every season.
  - Championship Group: 15 matches (single round robin) 2021–2024, **30 matches
    (double round robin) from 2025** — a real format change in the feed.
  - Relegation Group: 15 matches (single round robin) every season.
  - **ECL Playoff: 5 matches in 2022, 2023, 2024 only** — a same-tier internal
    play-off for the last European place (two of those ties carry
    PenaltyShootout events; the recorded score is the 90/120-minute score).
    Absent 2021, dropped from 2025 when the championship group doubled.
  - Season totals follow exactly: 162 / 167 / 167 / 167 / 177 / 177.
- **Phase rule (frozen)**: split phases (championship / relegation) are modelled
  as ordinary rows with a `phase` flag (the SCO/CY program precedent). The ECL
  Playoff is same-tier (all 12 clubs are Veikkausliiga clubs), so its rows are
  also ordinary rows with phase = `ecl_playoff`. There are NO cross-tier
  play-off ties in this feed (the relegation play-off vs Ykkönen clubs is not
  in league_id 51), so nothing is excluded on that ground.
- **2026 is COMPLETE**: 177/177 matches with scores, structure identical to
  2025 (132 + 30 + 15), last match 2026-11-08. The Finnish season ends in
  autumn; nothing is outstanding. 2026 is frozen as the virgin window
  (n = 177 — thin because the league has 12 teams; reported honestly, never
  widened after the fact).
- **Stats feed — two eras**:
  - 2021–2024 THIN: a single `All` period with exactly four keys —
    `BallPossesion`, `total_shots`, `ShotsOnTarget`, `corners`. No period
    splits (`has_period_splits` False for all 663 rows), no card keys.
  - 2025–2026 RICH: 32 keys (incl. `yellow_cards`, `red_cards`, `fouls`,
    `touches_opp_box`, `big_chance`, shots inside/outside box) WITH
    FirstHalf/SecondHalf period splits. Splits are internally consistent:
    All = FirstHalf + SecondHalf verified on 354 matches (corners_home,
    0 mismatches).
  - **No xG in ANY season**: no `expected_goals*` key appears even in the rich
    era, and `has_shotmap` is False for 1,017/1,017. Goals are a goals-only
    problem here (X1 blend falls back to goals-only, its documented fallback).
  - Missing stats, exactly: 2021 — 32 matches, ALL in the regular phase
    (championship/relegation groups have stats for all 30); 2022–2026 — none.
- **Total-shots definition break (fatal for T-FI)**: total shots per match by
  season: 19.38 / 16.90 / 15.94 / 15.16 in the thin era vs **26.40 / 26.31**
  in the rich era, while SOT stays in its normal band (8.20–9.46) across the
  break. The thin-era `total_shots` therefore does not measure the same
  quantity as the rich-era one (implied on-target share 0.52 vs 0.35). See
  MODEL_DESIGN: T-FI is not buildable — only one rich-era dev season (2025)
  exists, which cannot support the program's season-blocked walk-forward.
- **Events**: present in all matches. Goal and Card events carry minute
  (`time`; 45 = first half incl. stoppage). Events are the halves source for
  goals and cards in the dev era, and the only cards source before 2025.
- **Cards stats-vs-events artefact check (done before target freeze)**:
  stats `yellow_cards` exists only 2025–2026. Against event-derived unified
  yellows on the same matches: exact agreement 81.9% (2025) / 76.8% (2026);
  mean stats − events = −0.040 / −0.096 per match — small, no era flip, no
  systematic blow-out of the TH/ZA kind. BUT a single target must cover dev
  (2022–2025) and virgin, and stats keys do not exist before 2025, so the
  frozen target is **event-derived unified yellows** (Yellow + YellowRed) for
  every season, validated against the stats feed where both exist
  (see PREREG_K_FI).
- **Referee**: `infoBox.Referee.text` is empty in all of 2021–2024
  (663/663), named in only 36/177 (2025) and 96/177 (2026). Coverage in the
  dev era is far too low to measure the trait, let alone use it — X8 dead.
- **Team identity**: 17 distinct FotMob team ids across six seasons, every id
  carries exactly ONE name (no renames). All logic keys on team id anyway.
- **Levels** (per match, EDA): goals 2.52 / 2.96 / 2.56 / 2.95 / **3.29** /
  2.61 (2025 is a high-scoring outlier; virgin 2026 is back at the low end);
  SOT 8.49–9.46; corners 9.93–10.96; event yellows 4.17–4.43 in 2021–2024,
  dropping to 3.50 / 3.65 in 2025–2026 (the stats feed corroborates the 2025
  level, 3.46 vs events 3.50, so the drop is in the football or in both feeds
  together — recorded pre-fitting; the gates decide).
