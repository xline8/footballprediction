# Phase 1 — model design (no fitting)

The design is a pre-registration boundary, not implementation. All candidates use strictly pre-kickoff, season-blocked expanding data and the target's team ids/venue only. There are no playoffs or phase effects. The 2025/2026 season is virgin primary (complete, n=306) and is read once only after a dev gate; 2026/2027 is reserved confirmatory data and is not read.

Goals use the production Dixon–Coles reference with X1: 0.5 goals + 0.5 xG when xG exists, goals-only in 2021/2022 and for any missing xG. The G-TR candidate arms are Gate Zero, the promoted/thin-data SHRINK arm, and X3 set-play decomposition. X2 cannot exist in this single-tier corpus.

SOT uses the v5 reference and X5, with RS ratio-shrink and X4 xG/shot as candidate variants. X6 is not admitted because its population/reliability check failed. Corners use the production X9 Gate Zero, X5, and X7 box-touch multiplier. Cards use unified stats-feed yellows (frozen broken-stats event fallback), X5, and the X8 referee arm with a no-referee fallback. Total shots preregisters A v1, B v2 level layer, and C E9 trailing-r.

Halves are presentation-only frozen constants from the two complete-split DEV seasons. No feature is computed from a target match, and no model fitting is performed in phase 1. The exact gate legs, tie rules, calibration rule, and virgin discipline are frozen in the five preregistrations.
