# Verdict — G-AT2 (Austria 2. Liga goals)

**FAIL — at the dev gate. Virgin window NOT read.**

## Dev (season-blocked expanding fits; scored 2022/2023–2024/2025, n = 720)

| arm | 1X2 LL | RPS | OU2.5 LL |
|---|---|---|---|
| Gate Zero | 1.073657 | 0.236741 | 0.693380 |
| SHRINK | 1.073657 | 0.236741 | 0.693380 |
| climatology | 1.060892 | 0.237144 | 0.683684 |

Gate (frozen, PREREG_G_AT2): pooled dev 1X2 LL **and** RPS must
beat climatology, and OU2.5 LL must beat the base-rate baseline.
Gate Zero beats climatology on RPS only (0.236741 < 0.237144) and
loses both LL legs (1.073657 > 1.060892; 0.693380 > 0.683684) →
**dev gate FAIL**. SHRINK is numerically identical to Gate Zero in
every season: under season-blocked fitting no team ever sits in the
1–5 prior-match band at prediction time (every scored-season team
carries either 0 or ≥30 prior in-league matches), so the arm never
bites — the recorded finding the prereg anticipated. With Gate
Zero dead, the variant is moot, the verdict is FAIL, and season
2025/2026 was **not read** by this candidate. Nothing ships; no
virgin predictions file exists for G-AT2, deliberately.

Reading: the DC ratings carry a small real result signal (RPS
edge) but not enough to beat the league's own outcome rates on
log-loss in a 16-team league scoring 2.9 goals a match with a
57% over-2.5 rate — the same failure shape as G-AT in the parent
tier (there on the OU leg; here on both LL legs).

Coordinator notes: all numbers recomputed independently from
`engine/goals/predictions_dev.csv` (720 rows per arm); they match
the harness output to 6dp. Dev harness loads only
2021/2022–2024/2025 rows (verified in the port diff).
