# Verdict — G-RU1 (Russia 1. Division goals)

**FAIL at the dev gate. Virgin NOT read. Nothing ships.**

## Dev (n = 918, walk-forward 2022/2023–2024/2025)

| arm | 1X2 LL | RPS | OU2.5 LL |
|---|---|---|---|
| Gate Zero | 1.085944 | 0.222749 | 0.679603 |
| SHRINK | 1.085944 | 0.222749 | 0.679603 |
| climatology / base | 1.086566 | 0.222411 | 0.675299 |

Per-season 1X2 LL (Gate Zero): 1.080035 / 1.100559 / 1.077236.

Dev gate (verbatim): pooled 1X2 LL and RPS must beat climatology
AND OU2.5 LL must beat the base-rate baseline. 1X2 leg: 1.085944 <
1.086566 PASS (by 0.0006). RPS leg: 0.222749 > 0.222411 **FAIL**.
OU leg: 0.679603 > 0.675299 **FAIL**. Gate Zero therefore fails
its own dev gate; SHRINK is moot, the virgin is NOT read, and
G-RU1 is closed as FAIL.

SHRINK finding (recorded per the prereg): the arm is numerically
identical to Gate Zero on all 918 dev rows. Under season-blocked
fitting no team ever sits in the 1–5 prior in-league match band at
prediction time, so the shrinkage never bites — the G-J2 season-
opener failure mode does not occur under this protocol here, even
though entrants are measurably off league mean (X2: relegated
n = 9, GF gap +0.233 / GA gap −0.126; promoted/other n = 11,
−0.136 / +0.059).

All numbers above were recomputed by the coordinator from
`engine/goals/predictions_dev.csv`. No fitted params, no
predictions. Production code untouched.
