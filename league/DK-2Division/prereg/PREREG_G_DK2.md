# Pre-registration — G-DK2

Frozen 2026-11-10 before fitting. Target: full-time total goals and 1X2 from `home_goals`/`away_goals`, goals-only. Rounds 1–22 are `regular`; rounds 23–32 are split groups, ordinary rows with a phase flag. Halves use frozen `goals_1h_share: 0.4611` for presentation only.

Reference is production Dixon–Coles goals-only. Arms are Gate Zero, SHRINK for teams with fewer than six prior in-league matches, and X2 mover transplant. X2 uses a parent DK-1Division fit from the preceding season when the team has <12 in-league training matches and ≥10 parent matches, with `w=(12−n)/12 × min(1,n_parent/20)`.

Development is season-blocked: seed 2021/2022, score 2022/2023–2024/2025. Virgin 2025/2026 is read once only after dev gates pass. 2026/2027 is reserved. Primary line is OU 2.5.

Calibration: `|breach| ≤1pp` is clean PASS; within `≤1 SE` is PROVISIONAL; otherwise FAIL. Dev gate: pooled dev 1X2 LL, RPS, and OU2.5 LL for Gate Zero must all beat pooled-prior climatology; otherwise G-DK2 FAIL, variants are moot, and virgin is not read.

Virgin legs: (i) arm virgin 1X2 LL must be ≤ Gate Zero and ≤ climatology; (ii) pooled home-win and OU2.5 over-rate prediction breaches must each be ≤1.0pp, with SEs reported, and within 1 SE of the boundary is PROVISIONAL, beyond it FAIL; (iii) arm LL must be ≤ Gate Zero LL in at least half of dev seasons. If Gate Zero and a variant both pass all legs, ship the lower pooled virgin 1X2 LL; ties go simpler. If only one passes, ship it. If none passes, G-DK2 FAIL and nothing ships.
