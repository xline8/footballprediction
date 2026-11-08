# Step 3 — EDA (RO-LigaII)

EDA uses the modelling inclusion set (`phase != relegation_playoff`), n = 1,505. The levels are descriptive across all seasons; they do not fit or read a virgin model window.

## F1 — Levels by season

| Season | n | Goals/m | Home win | Draw | Away win | OU2.5 over |
|---|---:|---:|---:|---:|---:|---:|
| 2021/2022 | 262 | 2.645 | .431 | .218 | .351 | .477 |
| 2022/2023 | 262 | 2.485 | .443 | .263 | .294 | .473 |
| 2023/2024 | 262 | 2.271 | .435 | .275 | .290 | .378 |
| 2024/2025 | 262 | 2.370 | .424 | .252 | .324 | .450 |
| 2025/2026 | 317 | 2.716 | .476 | .189 | .334 | .498 |
| 2026/2027 | 140 | 2.886 | .479 | .200 | .321 | .550 |

The brief’s checkpoint levels were measured on all matches, including playoff rows: for example 2021/2022 is 2.640 on n=264 and 2022/2023 is 2.473 on n=264. The required EDA is playoff-excluded, so the recomputed inclusion-set numbers above are used here. This is the only headline-level discrepancy: it is a denominator/inclusion convention, not a builder disagreement.

## F2 — Team-trait reliability

Split-half reliability uses team-season match order, odd/even halves, on the inclusion set. There are 124 paired team-season units.

| Trait | split-half r |
|---|---:|
| goals for | 0.411 |
| goals against | 0.593 |

No other traits exist in this league’s payloads. SOT, corners, total shots, possession and yellows reliability cannot be measured; they did not fail a reliability test, because there is no source to test.

## F3 — Halves

The frozen presentation constant is the first-half share of goal events with event time `<=45`, pooled on the inclusion set: 1,751 first-half goals / 3,828 goal events = **0.457419**.

| Season | First-half goals | Goal events | 1H share |
|---|---:|---:|---:|
| 2021/2022 | 307 | 697 | .440 |
| 2022/2023 | 296 | 651 | .455 |
| 2023/2024 | 274 | 595 | .461 |
| 2024/2025 | 309 | 621 | .498 |
| 2025/2026 | 377 | 860 | .438 |
| 2026/2027 | 188 | 404 | .465 |
| **Pooled** | **1,751** | **3,828** | **.457** |

The event/score discrepancy matters: the inclusion set has 3,825 score-derived goals but 3,828 goal events (+3), with +4 in 2021/2022 and −1 in 2025/2026. The constant is presentation only. Per-match half shares are noisy; team-specific half shares are rejected in FEATURES.

## F4 — Movers / tiers

There are 52 distinct team ids. Per-season team counts are 20, 20, 20, 20, 22 and 22. New teams with zero prior in-league matches at each season start are 6, 8, 8, 6 and 4 for 2022/2023 through 2026/2027. No team has 1–5 prior in-league matches at a season start: every team is at 0 or at least 25. This makes the SHRINK arm numerically identical to Gate Zero under season-blocked fitting in the RO-LigaI precedent; the prereg will verify it mechanically here. The 20→22 format change occurs at 2025/2026.

## F5/F6/F7 — xG family

NOT MEASURABLE. There is no xG, xG split, xGOT or shotmap shot in any of 1,513 files. Set-play share/rate, xG per shot and attacking xGOT/shot are dropped on data absence.

## F8 — Referee strictness

NOT MEASURABLE. Referee text is blank in all 1,513 files.

## F9 — Territorial covariates

NOT MEASURABLE. There is no stats feed in any file, so possession, box touches, big chances and related territorial covariates do not exist.

## F10 — Lineup / absence

CLOSED programme-wide. No lineup or absence feature is reopened in this build.

## F11 — xG calibration

Not applicable: no xG source exists.

## F12 — Cards artefact

This is stronger than the RO-LigaI undercount artefact. There is no stats feed, zero straight-Yellow events in all 1,513 payloads, 148 Red events and 106 YellowRed events. A yellow-card target cannot be constructed. Red counts remain audit fields only and are rejected as a target because they are rare events.
