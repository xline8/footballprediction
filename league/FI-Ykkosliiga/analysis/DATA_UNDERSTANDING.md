# Step 1 — Data Understanding: FI-Ykkosliiga (FotMob id 251)

Fresh builder inventory: 895 finished rows and 895 unique match ids.

| Season | Matches | Dates | Teams | Stats non-null | Index stats flag | Events | Referee named | Card-event matches | Shotmap |
|---|---:|---|---:|---:|---:|---:|---:|---:|---:|
| 2021 | 162 | 2021-05-05–2021-10-23 | 12 | 0 | 0 | 153 | 0 | 27 | 0 |
| 2022 | 164 | 2022-04-18–2022-10-17 | 12 | 0 | 0 | 161 | 0 | 23 | 0 |
| 2023 | 164 | 2023-04-14–2023-10-21 | 12 | 0 | 0 | 154 | 0 | 19 | 0 |
| 2024 | 135 | 2024-04-13–2024-10-19 | 10 | 0 | 0 | 129 | 0 | 26 | 0 |
| 2025 | 135 | 2025-04-21–2025-10-18 | 10 | 0 | 0 | 131 | 0 | 22 | 0 |
| 2026 | 135 | 2026-04-03–2026-10-17 | 10 | 0 | 135 | 135 | 32 | 134 | 0 |

The index `has_stats=True` flag occurs in 135/895 rows, all in 2026, but those
payloads contain `{"Periods": {"All": null}}`; builder `has_stats_all=0` is
asserted for all 895. This is a false positive, not usable stats. Shotmap shots
are empty in 895/895 and no xG key occurs. A `Half` event at time 45 is the HT
source in every match that has events.

## Format and phase rule

2021–2023 have 12 teams: 132 regular rows, 15 Championship Group rows, 15
Relegation Group rows, and two same-tier Promotion Playoff rows in 2022 and
2023. 2024–2026 have 10 teams, one table, and 27 rounds × 5 = 135. The feed
renames Ykkonen to Ykkosliiga in 2024 and uses Ykkösliiga in 2026. All phases
are ordinary rows with a `phase` flag. No cross-tier playoff rows are in this
league feed.

Card coverage breaks sharply: 27/162, 23/164, 19/164, 26/135, and 22/135 in
2021–2025 (16.7%, 14.0%, 11.6%, 19.3%, 16.3%) versus 134/135 (99.3%) in 2026,
with 494 Card events. Referee text is empty in 2021–2025 and named in 32/135
2026 matches. These gaps rule out cards and referee features for the dev design.

There are 23 distinct FotMob team ids and no id carries multiple names. Logic
keys by team id. 2026 is complete, ending 2026-10-17, and is virgin-only for
modelling.

## Fresh levels

| Season | Goals/match | Home win | Over 2.5 |
|---|---:|---:|---:|
| 2021 | 2.809 | 0.426 | 0.525 |
| 2022 | 3.165 | 0.482 | 0.634 |
| 2023 | 2.915 | 0.463 | 0.537 |
| 2024 | 3.111 | 0.415 | 0.593 |
| 2025 | 3.281 | 0.430 | 0.637 |
| 2026 | 2.667 | 0.430 | 0.489 |

These are inventory and level counts only; no model fitting or virgin model read
was performed.
