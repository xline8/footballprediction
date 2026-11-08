# Step 6 — Model Design: MD-NationalDivision

Feasibility matrix: **goals — target exists in every season**
(556/556 FT scores). **SOT / corners / total shots / yellows —
no target exists in any season** (stats feed 0/556, shotmap
0/556, period splits 0/556; zero plain-Yellow events corpus-wide;
referee 0/556). **Only G-MD is buildable.** S/C/K/T are
not-buildable on feasibility grounds (see their prereg and verdict
files); the split was not moved to manufacture a window for them.

Windows frozen for the built candidate: warm-up 2021/2022;
dev scored 2022/2023–2024/2025 (n=258), season-blocked expanding
fit; virgin = **2025/2026** (complete, 114 matches — read ONCE,
only for dev-passing arms). 2026/2027 (72, in progress) is
untouched as confirmatory reserve. All rows are ordinary rows
(phase flag `main` / `championship` carried, never filtered), per
the frozen phase rule in DATA_UNDERSTANDING.md.

Implementation: the G-MD engine is a port of the programme
Dixon-Coles reference (`dc.py` / `arms.py` carried over verbatim
from the BY/FI line: iterative sweep optimiser, 14 sweeps,
damping 0.7, +0.25 smoothing, home init 0.28, MAXG = 10, production
tau, rho grid (0.0, −0.05, −0.10, −0.15) by goals log-likelihood,
decay HL = 270 days), with the harness adapted from the same line
plus the naive trailing-10 baseline (IL precedent). The X1 blend's
documented fallback applies throughout: goals-only observation
(no xG exists in this feed).

| Candidate | Gate Zero pattern | Variant arms | Warm-up | Dev scored | Primary line |
|---|---|---|---|---|---|
| G-MD goals | Dixon-Coles Poisson, goals-only (X1 fallback): attack/defence ratings + home advantage, sweep fit, rho grid, score matrix to 10 goals | SHRINK (n<6 shrink) + X2 (entrant offset, rule-based; full-dev realisation g_log −0.223 / c_log +0.223 clamped) | 2021/2022 | 2022/2023–2024/2025 (n=258), season-blocked expanding fit | 1X2 LL/RPS + OU 2.5 |
| S-MD SOT | — not-buildable | — | — | — | — |
| C-MD corners | — not-buildable | — | — | — | — |
| K-MD cards | — not-buildable | — | — | — | — |
| T-MD total shots | — not-buildable | — | — | — | — |

Gate legs (identical program-wide, frozen verbatim in the prereg):
dev gate — pooled dev 1X2 LL, RPS and OU2.5 LL of an arm must beat
BOTH baselines (climatology; naive trailing-10), else the arm is
dead and the virgin is NOT read for it; if Gate Zero fails dev,
variants are moot, verdict FAIL. Virgin legs — (i) LL ≤ Gate
Zero's and ≤ each baseline's (1X2 and OU2.5); (ii) calibration
|mean predicted − actual| ≤ 1.0pp clean PASS, breach within 1 SE
of the boundary = PROVISIONAL PASS, beyond = FAIL; (iii) variant
sign check: variant dev 1X2 LL ≤ Gate Zero's in at least half the
dev seasons (≥2 of 3). Both-pass: lower pooled virgin 1X2 LL
ships; ties → simpler arm. Gates never move after a result is
seen; FAIL is a valid outcome.

Halves presentation via the frozen goals constant 0.4388
(FEATURES.md). Predictions-only: no MD odds/settlement source
in-system.

Known calibration risk (recorded, not adjusted): the dev era
contains a deep level dip — 2022/2023 scored 2.128 goals/match
against 2.953 / 2.965 in the two following dev seasons and 3.063
in the warm-up — so the expanding fit chases a moving level, and
the dev scored pool (n=258) is the smallest in the programme so
far. Trait reliability is strong (0.885 / 0.877), so ratings have
signal; the level swing is the risk. Virgin-season goals/match
(2.947, inventory only) sits near the last two dev seasons. No
level adjustment is made — the gates are frozen and the virgin is
read once.
