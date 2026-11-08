# Phase A — Candidate Model Design: SCO League One

This is design-only. No model is fitted here, and 2025/2026 and 2026/2027 are not used for fitting. Dev is season-blocked walk-forward: seed 2021/2022, score 2022/2023–2024/2025. Virgin primary is 2025/2026 (complete, n=180), read once only for dev-passing arms. 2026/2027 (partial, n=69) is confirmatory and reserved, not read. Calibration is actual − predicted.

| candidate | target / architecture | allowed arms | primary line |
|---|---|---|---|
| G-SCO-L1 | goals, Dixon-Coles hl=270 | Gate Zero + SHRINK + X2-if-adopted | OU 2.5 |
| K-SCO-L1 | event Yellow target | Gate Zero only | 3.5 |
| S-SCO-L1 | SOT | **NOT buildable**: no target in any of 969 payloads | — |
| C-SCO-L1 | corners | **NOT buildable**: no target in any of 969 payloads | — |
| T-SCO-L1 | total shots | **NOT buildable**: no target in any of 969 payloads | — |

The exact gate text for preregistration is:

G-SCO-L1 (goals) — Dev gate: pooled dev 1X2 LL and RPS must beat
climatology, and OU2.5 LL must beat the base-rate baseline, else the
arm is dead and there is no virgin read. Virgin legs — (i) LL leg:
the arm's virgin 1X2 LL ≤ Gate Zero's AND ≤ climatology's; (ii)
calibration leg: |actual − predicted| ≤ 1.0pp pooled for the home-win
rate and for the OU2.5 over-rate, SEs reported; a breach within 1 SE
of the boundary is PROVISIONAL PASS, beyond it FAIL; (iii) variant
sign check: a variant's dev 1X2 LL ≤ Gate Zero's in at least half of
the dev seasons. Both-pass rule: if Gate Zero and a variant both
pass all legs, the lower pooled virgin 1X2 LL ships; if only one
passes, it ships; if none passes, G-SCO-L1 is FAIL. Gate Zero dev
fail ⇒ variants moot, verdict FAIL, virgin NOT read.

K-SCO-L1 (cards) — Dev gate: pooled dev LL@3.5 must beat BOTH
baselines (league base rate; naive trailing-10), else the candidate
is dead and there is no virgin read. Virgin legs — (i) LL@3.5 ≤ best
baseline's; (ii) calibration |actual − predicted| ≤ 1.0pp at 3.5, SE
reported, breach within 1 SE = PROVISIONAL PASS, beyond it FAIL. If
Gate Zero passes all legs it ships; if any leg fails, K-SCO-L1 is
FAIL and nothing ships.

Calibration is actual − predicted everywhere in this build.

There is no referee arm and no stats-market candidate because a valid virgin window cannot contain an absent target.
