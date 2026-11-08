# Step 6 — Model Design: FI-Veikkausliiga

Feasibility matrix: goals — target exists all seasons; SOT / corners —
target exists 2021+ (stats feed) and in the virgin (177/177); cards —
target exists all seasons (event feed) and in the virgin (177/177);
**total shots — target NOT comparable across eras** (thin-era levels
15.2–19.4 vs rich-era 26.3–26.4 per match with SOT flat: a feed definition
change). The only dev seasons carrying the virgin's quantity are 2025
(one season), which cannot support the season-blocked walk-forward dev
protocol — **T-FI is NOT BUILT**. Its absence is a feasibility verdict,
recorded here before any fitting, not a gate FAIL.

Windows frozen for every built candidate: virgin = **2026** (complete,
177 matches, last match 2026-11-08 — read ONCE, only for dev-passing
arms). Dev = season-blocked walk-forward as tabled. The virgin n (177)
is thin; SEs will be wide and PROVISIONAL outcomes are likely — that is
reported, not repaired.

| Candidate | Reference (Gate Zero) | Variant arms (pre-registered) | Warm-up | Dev scored | Primary line |
|---|---|---|---|---|---|
| G-FI goals | Production DC pattern, goals-only (X1 fallback) | SHRINK (thin-data prior, per the G-J2 lesson); X2 entrant offset (in-corpus) | 2021 | 2022–2025 (n=678) | 1X2 LL/RPS + OU 2.5 |
| S-FI SOT | Production v5 pattern unmodified | RS (BB prior 200 → 20,000) | 2021 | 2022–2025 (n=678 stats rows) | 8.5 |
| C-FI corners | Corners_v3 pattern, possession covariate only (X9 partial) | — none (X7 window-infeasible) | 2021 | 2022–2025 (n=678 stats rows) | 9.5 |
| K-FI cards | Production cards pattern on event yellows | — none (X8 data absent in dev era) | 2021 | 2022–2025 (n=678) | 3.5 |
| T-FI total shots | — | — | — | — | NOT BUILT (definition break) |

Gate legs (identical program-wide, frozen in each prereg): dev gate —
pooled dev LL at the primary line (goals: 1X2 LL and OU LL legs) beats
BOTH baselines (league base rate / climatology; naive trailing-10), else
the arm is dead and the virgin is NOT read for it; if Gate Zero fails
dev, variants are moot. Virgin legs — (i) LL ≤ Gate Zero's and ≤ best
baseline's; (ii) calibration |breach| ≤ 1pp clean PASS, ≤ 1 SE
PROVISIONAL PASS, else FAIL; (iii) variant sign check: variant dev LL ≤
Gate Zero's in at least half the dev seasons. Ties → simpler arm.
Halves presentation via the frozen constants in FEATURES.md (goals,
SOT, corners, cards); there is no total-shots product.
