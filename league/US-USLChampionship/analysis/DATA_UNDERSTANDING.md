# Stage A — Data Understanding: USA USL Championship

The builder filters `fotmob_world_index.csv` to `league_id=="8972"` and
produces 2,590 unique match rows and 5,180 team-match rows. Seasons are
calendar labels `2021`–`2026`; 2026 is inventory only (in progress at pull,
387 rows, playoffs incomplete).

| season | matches | regular / playoff | stats | shotmap | period splits | referee | xG |
|---|---:|---:|---:|---:|---:|---:|---:|
| 2021 | 510 | 496 / 14 | 100.0% | 0.0% | 0.0% | 0.0% | 0.0% |
| 2022 | 472 | 459 / 13 | 100.0% | 0.0% | 0.0% | 98.7% | 0.0% |
| 2023 | 423 | 408 / 15 | 100.0% | 0.0% | 92.7% | 97.2% | 0.0% |
| 2024 | 423 | 408 / 15 | 100.0% | 0.0% | 100.0% | 91.7% | 0.0% |
| 2025 | 375 | 360 / 15 | 100.0% | 0.0% | 100.0% | 96.3% | 0.0% |
| 2026 | 387 | 375 / 12 | 100.0% | 0.0% | 100.0% | 87.6% | 0.0% |

Regular season runs approximately March–October; playoffs run
October–November. Phase is derived from `general.leagueName`
(`USL Championship` versus `USL Championship Playoff`); it agrees with
the playoff `matchRound` values (`1/8`, `1/4`, `1/2`, `final`) on all
2,590 rows (phase disagreement count 0). Regular matches all carry
`matchRound="1"` in this feed, so round carries no information beyond
phase.

The league runs Eastern/Western conferences with cross-conference play,
but no conference field exists in the warehouse JSONs (same limitation
as US-MLS), so no conference feature is built. There is NO
promotion/relegation: no mover tier exists. Churn is contraction and
expansion: team counts by FotMob team_id are 31 (2021), 27 (2022),
24 (2023), 24 (2024), 24 (2025), 25 (2026). MLS reserve sides
(Atlanta United 2, LA Galaxy II, New York Red Bulls II, Sporting
Kansas City II, Real Monarchs SLC, Tacoma Defiance) left after 2021–22
for MLS Next Pro; genuine new entries after 2021 are Detroit City FC and
Monterey Bay FC (2022), North Carolina FC (returning) and Rhode Island
FC (2024), and Lexington SC (2025, entering the virgin season with zero
prior USL Championship matches in this corpus).

Team identity is FotMob `team_id`: name counts exceed id counts because
of renames on stable ids — id 521005 is `LA Galaxy II` then
`Ventura County FC`; id 915808 appears as both `Monterey Bay FC` and
`Monterey Bay F.C.`. (A naive count of index home/away names gives
32/29/25 teams for 2021–23; the id counts 31/27/24 are correct.)

Two feed artefacts matter. (1) The event feed carries almost no Card
events in 2021–22 (17–24 Card events per 80 sampled matches versus 462
in 2024), while the stats feed is complete in every season — see the
cards audit in PREPROCESSING.md. (2) `touches_opp_box` coverage ramps:
21.4% (2021), 33.7% (2022), 39.0% (2023), 100% (2024–25) — the same
ramp shape as US-MLS, one tier later.

The modelled 2021–25 pooled levels are goals 2.780, SOT 8.433,
corners 9.244, shots 24.162, and yellows 4.325. The 2026 inventory is
387 rows and is not used for any design decision (its row in the cards
audit table inside `eda_summary.json` is descriptive only).
