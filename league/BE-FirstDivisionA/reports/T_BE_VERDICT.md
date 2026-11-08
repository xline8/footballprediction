# T-BE verdict — FAIL

Prereg: `prereg/PREREG_T_BE.md` (frozen f0c214a, before fitting).
Primary line **25.5** (dev over-rate 0.473). Dev pooled n = 955
(score-only match excluded — target absent); virgin 2025/2026
n = 313, read once, for all three dev-passing arms.

## Dev results — pooled LL@25.5

| Arm / baseline | LL@25.5 |
|---|---|
| A (v1 pattern) | 0.6598 |
| B (v2 level layer) | 0.6569 |
| C (E9 trailing-r) | 0.6598 |
| League base rate | 0.6888 |
| Naive trailing-10 | 0.6705 |

All three arms beat both baselines → all pass the dev gate.
Sign checks vs arm A: B 2/3; C 1/3 (worse 2022/2023 and 2024/2025
by 0.0002 / 0.0001 — recorded as measured).

## Virgin results (2025/2026, n = 313)

| Arm / baseline | LL@25.5 | Calibration (mean P − actual) |
|---|---|---|
| A | 0.6557 | −4.93pp (SE 2.71pp) |
| B | 0.6544 | −4.03pp (SE 2.71pp) |
| C | 0.6562 | −5.11pp (SE 2.71pp) |
| League base rate | 0.6891 | — |
| Naive trailing-10 | 0.6568 | — |

## Gate arithmetic

- Leg (i) (vs reference arm A and best baseline 0.6568): A passes
  (0.6557 — by 0.0011 over the naive baseline); B passes (0.6544 ≤
  A); **C fails** (0.6562 > A's 0.6557).
- Leg (ii): **A and B both FAIL.** Breaches beyond the 1.0pp
  boundary are 3.93pp (A) and 3.03pp (B), each beyond 1 SE
  (2.71pp) — B misses the provisional band by 0.32pp of breach.
  Every arm under-predicted the virgin over-25.5 rate by 4–5pp:
  the virgin season's shot *distribution* shifted over the line
  (mean 26.33 vs dev 25.9 tells only part of it).
- Leg (iii): B's 2/3 sign check is moot under leg (ii); C's 1/3
  would have failed it independently.

**Verdict: FAIL. Nothing ships.** All three arms ranked the
virgin season well (LLs at or below the naive baseline) and all
three die on the same calibration leg — the program's recurring
total-shots failure shape, here in its narrowest B-arm form.
