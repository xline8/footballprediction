# Stage A — Data Understanding: USA MLS

The builder filters `fotmob_world_index.csv` to `league_id=="130"` and produces 3,054 unique match rows and 6,108 team-match rows. Seasons are calendar labels `2021`–`2026`; 2026 is inventory only because playoffs are absent.

| season | matches | regular / playoff | stats | shotmap | period splits | referee | xG |
|---|---:|---:|---:|---:|---:|---:|---:|
| 2021 | 472 | 459 / 13 | 100.0% | 100.0% | 0.6% | 0.0% | 99.2% |
| 2022 | 489 | 476 / 13 | 100.0% | 100.0% | 1.4% | 97.3% | 99.4% |
| 2023 | 521 | 493 / 28 | 100.0% | 100.0% | 87.3% | 99.0% | 100.0% |
| 2024 | 522 | 493 / 29 | 100.0% | 100.0% | 100.0% | 96.2% | 100.0% |
| 2025 | 540 | 510 / 30 | 100.0% | 100.0% | 100.0% | 96.1% | 100.0% |
| 2026 | 510 | 510 / 0 | 100.0% | 100.0% | 100.0% | 94.3% | 100.0% |

Regular season runs approximately February–October; playoffs run October–December. The playoff field grows from 13 matches in 2021–22 to 28–30 from 2023. Team identity is FotMob `team_id`: names vary (`CF Montreal`/`CF Montréal`, and index `Red Bull New York` versus JSON `New York Red Bulls`). There is no relegation; teams rise from 27 in 2021 to 28 in 2022, 29 in 2023–24, and 30 in 2025. Charlotte FC, St. Louis City, and San Diego FC are the expansion/thin-team cases.

The JSONs have `general.matchRound=None`; phase is derived from `general.leagueName` (`Major League Soccer` versus `Major League Soccer Playoff`). MLS conferences exist operationally, but no conference field exists in this warehouse. Playoff shootout attempts are excluded from shotmap aggregates and counted separately; the corpus contains 7 shootout-shot matches in the 2025 playoffs. Four matches have extra-time periods, all playoffs (2023: Orlando City–Columbus Crew 0–2, FC Cincinnati–Columbus Crew 2–3; 2024: Los Angeles FC–Seattle Sounders FC 1–2; 2025: Vancouver Whitecaps–Los Angeles FC 2–2). For these four, the recorded score and All stats include extra time (the 90-minute score was tied in each case) — a documented 4-match quirk in the goals target.

The modelled 2021–25 pooled levels are goals 2.930, SOT 9.119, corners 9.833, shots 25.610, and yellows 4.047. The 2026 inventory is 510 rows and is not used for any design decision.
