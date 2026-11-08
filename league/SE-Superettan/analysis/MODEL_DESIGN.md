# Step 6 — Model Design: SE-Superettan

Feasibility matrix: goals — target exists all seasons; SOT / corners / total
shots — target exists 2022+ (stats feed) and in the virgin (237/240); cards —
target exists all seasons (event feed) and in the virgin (240/240). All five
candidates are buildable. Windows frozen for every candidate: virgin = **2026**
(complete regular season, 240 matches, last round 2026-11-07 — read ONCE, only
for dev-passing arms). Dev = season-blocked walk-forward as tabled.

| Candidate | Reference (Gate Zero) | Variant arms (pre-registered) | Warm-up | Dev scored | Primary line |
|---|---|---|---|---|---|
| G-SE2 goals | Production DC pattern, goals-only (X1 fallback) | SHRINK (thin-data prior, per the G-J2 lesson); X2 mover offset (parent corpus) | 2021 | 2022–2025 (n=960) | 1X2 LL/RPS + OU 2.5 |
| S-SE2 SOT | Production v5 pattern unmodified | RS (BB prior 200 → 20,000) | 2022 | 2023–2025 (n=710 stats rows) | 9.5 |
| C-SE2 corners | Corners_v3 pattern, possession covariate only (X9 partial) | — none (X7 data absent) | 2022 | 2023–2025 | 10.5 |
| K-SE2 cards | Production cards pattern on event yellows | — none (X8 data absent: no referee names) | 2021 | 2022–2025 (n=960) | 3.5 |
| T-SE2 total shots | Shots family v1 pattern (arm A) | B (v2 level layer); C (E9 trailing-r) | 2022 | 2023–2025 | 20.5 |

Gate legs (identical program-wide, frozen in each prereg): dev gate — pooled
dev LL at the primary line (goals: 1X2 LL and OU LL legs) beats BOTH baselines
(league base rate / climatology; naive trailing-10), else the arm is dead and
the virgin is NOT read for it; if Gate Zero fails dev, variants are moot.
Virgin legs — (i) LL ≤ Gate Zero's and ≤ best baseline's; (ii) calibration
|breach| ≤ 1pp clean PASS, ≤ 1 SE PROVISIONAL PASS, else FAIL; (iii) variant
sign check: variant dev LL ≤ Gate Zero's in at least half the dev seasons.
Ties → simpler arm. Halves presentation (goals, cards only) via the frozen
event-time constants; stats markets ship FT-only.
