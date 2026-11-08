# Verdict — G-CL (Chile Liga de Primera goals)

**FAIL at the dev gate. Virgin NOT read. Nothing ships.**

## Dev (n = 720, walk-forward 2022–2024)

| arm | 1X2 LL | RPS | OU2.5 LL |
|---|---|---|---|
| Gate Zero | 1.079003 | 0.232298 | 0.702573 |
| SHRINK | 1.079003 | 0.232298 | 0.702573 |
| climatology / base | 1.073330 | 0.231059 | 0.695449 |

Per-season 1X2 LL (Gate Zero): 1.055403 / 1.131191 / 1.050414
(2023 is the losing season on every metric).

Dev gate (verbatim): pooled 1X2 LL and RPS must beat climatology
AND OU2.5 LL must beat the base-rate baseline. Gate Zero fails all
three legs (1.079003 > 1.073330; 0.232298 > 0.231059; 0.702573 >
0.695449). SHRINK is numerically identical to Gate Zero on all 720
dev rows — under season-blocked fitting no team sits in the 1–5
prior-match band at prediction time, so the G-J2 season-opener
failure mode does not occur under this protocol here. Variants
moot; virgin (2025) NOT read; G-CL closed as FAIL.

Numbers recomputed by the coordinator from
`engine/goals/predictions_dev.csv`. No fitted params, no
predictions. Production code untouched.
