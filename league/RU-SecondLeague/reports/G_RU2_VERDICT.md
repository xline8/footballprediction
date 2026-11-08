# Verdict — G-RU2 (Russia Second League goals)

**FAIL at the dev gate. Virgin NOT read. Nothing ships.**

## Dev (n = 3,284, walk-forward 2022/2023–2025/2026, date-cutoff)

| arm | fold | 1X2 LL | RPS | OU2.5 LL |
|---|---|---:|---:|---:|
| Gate Zero | 2022/2023 (n=1,115) | 1.091756 | 0.234525 | 0.731117 |
| climatology | 2022/2023 | 1.076036 | 0.235071 | 0.698279 |
| Gate Zero | 2023 (n=512) | 1.087520 | 0.240083 | 0.677598 |
| climatology | 2023 | 1.075109 | 0.238048 | 0.696202 |
| Gate Zero | 2023/2024 (n=362) | 1.188191 | 0.254038 | 0.693677 |
| climatology | 2023/2024 | 1.097497 | 0.222561 | 0.701992 |
| Gate Zero | 2024 (n=904) | 1.029581 | 0.222168 | 0.723263 |
| climatology | 2024 | 1.057464 | 0.235239 | 0.693150 |
| Gate Zero | 2024/2025 (n=235) | 1.094456 | 0.224739 | 0.707039 |
| climatology | 2024/2025 | 1.113906 | 0.227989 | 0.692545 |
| Gate Zero | 2025/2026 (n=156) | 1.094956 | 0.230229 | 0.669044 |
| climatology | 2025/2026 | 1.085822 | 0.227898 | 0.692595 |
| **Gate Zero** | **pooled** | **1.084956** | **0.233237** | **0.711812** |
| **climatology** | **pooled** | **1.076319** | **0.233355** | **0.696273** |

SHRINK is numerically identical to Gate Zero on all 3,284 dev rows
(see below), so its table is the same row for row.

Dev gate (verbatim): pooled 1X2 LL and RPS must beat climatology
AND OU2.5 LL must beat the base-rate baseline. 1X2 leg: 1.084956 >
1.076319 **FAIL** (worse by 0.008637). RPS leg: 0.233237 <
0.233355 PASS (better by 0.000119). OU leg: 0.711812 > 0.696273
**FAIL** (worse by 0.015540). Gate Zero therefore fails its own dev
gate; SHRINK is moot, the virgin is NOT read, and G-RU2 is closed
as FAIL.

Per-fold pattern: the model beats climatology on 1X2 LL in only 2 of
6 folds (2024, 2024/2025) and on RPS in 3 of 6. The worst fold is
2023/2024 (Division A, the low-scoring season: 2.21 goals/match,
30.4% draws), where the model is far worse than climatology on both
1X2 LL (1.188191 vs 1.097497) and RPS (0.254038 vs 0.222561) — the
fit over-predicts away goals there (mean predicted λ_away 1.037 vs
actual 0.928). The OU2.5 leg fails because the model is worse than
the base rate in the three largest folds (2022/2023, 2024,
2024/2025).

SHRINK finding (recorded per the prereg): the arm is numerically
identical to Gate Zero on all 3,284 dev rows (0 differing
predictions). Under date-cutoff fitting no team ever sits in the
1–5 prior in-league match band at prediction time — teams are either
established (≥6 prior matches) or brand new (0 prior matches, e.g.
450 fold rows in 2022/2023 involve a 0-prior team, which starts at
the league mean under both arms). The G-J2 season-opener failure
mode does not occur under this protocol here, the same finding as
G-RU1. X2 note: the 9 relegated entrants from 1. Division showed no
systematic first-season offset (pooled gaps GF −0.079 / GA −0.021),
so no hard-coded tier offset was available either.

## Why it fails (interpretation, not a rescue)

The pooled Dixon-Coles cannot beat climatology in this league. The
structure works against it: teams are rated only within small
disconnected groups (14–25 teams per component per season), seasons
are short (~30 matches per team), the two tracks (A/B) barely share
teams, and the A track's low-scoring seasons break the pooled level.
The sibling parallel is exact: G-RU1 (1. Division) also failed its
dev gate, on the RPS and OU2.5 legs. Goals models fail in both
Russian tiers below the Premier League; only the top tier's goals
model passed. No post-hoc arm is attempted — the prereg forbids it.

## Virgin

**NOT read.** The virgin window (labels 2026 + 2026/2027, 888
finished non-awarded matches) was deliberately left unread per the
frozen Gate Zero rule. No `results_virgin.json`, no fitted params,
no predictions. The halves constant (goals 1H share 0.4393) is
recorded in the config but ships nothing.

All numbers above were recomputed by the builder from
`engine/goals/predictions_dev.csv` through an independent script
(not the harness): pooled and per-fold LL/RPS/OU2.5 reproduce
`results_dev.json` exactly; per-fold n values are exact
(1115/512/362/904/235/156); no 2025-label, awarded, unfinished or
virgin row appears in the dev predictions; a replay refit of the
2022/2023 fold reproduces its lambdas to 0.0. Production code
untouched.
