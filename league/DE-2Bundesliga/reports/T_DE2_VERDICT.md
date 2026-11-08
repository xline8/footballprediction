# T-DE2 verdict — FAIL

Prereg: `prereg/PREREG_T_DE2.md` (frozen 4261ad8, before fitting).
Primary line **27.5** (dev over-rate 0.492). Dev pooled n = 918;
virgin 2025/2026 n = 306, read once, for arm C only — the sole
dev-passing arm.

## Dev results — pooled LL@27.5

| Arm / baseline | LL@27.5 |
|---|---|
| A (v1 pattern) | 0.6936 |
| B (v2 level layer) | 0.6934 |
| C (E9 trailing-r) | 0.6929 |
| League base rate | 0.6931 |
| Naive trailing-10 | 0.7058 |

**A and B FAIL the dev gate** — both lose to the league base rate
(A by 0.0005, B by 0.0003) while beating the naive baseline. Only
**C passes**, beating the base rate by 0.00014 — the narrowest
dev-gate margin in the program so far, recorded as measured.
Per season, all three arms beat the base rate in 2022/2023 and
lose to it in 2024/2025; the pooled verdict is decided by
2023/2024. A and B are dead: no virgin read for them.

## Virgin results (2025/2026, n = 306) — arm C only

| Arm / baseline | LL@27.5 | Calibration (mean P − actual) |
|---|---|---|
| C (E9 trailing-r) | 0.6904 | +0.63pp (SE 2.85pp) |
| League base rate | 0.6877 | — |
| Naive trailing-10 | 0.7028 | — |

## Gate arithmetic

- Leg (i): **C FAILS.** The reference arm under the prereg's
  rule is C itself (A failed dev, so the reference is the
  dev-passing arm with the lowest pooled dev LL); C's virgin LL
  (0.6904) must also beat the best baseline — the league base
  rate's 0.6877 — and does not (0.6904 > 0.6877 by 0.0027).
- Leg (ii): C's calibration is +0.63pp — inside the 1.0pp
  boundary, CLEAN — but moot under leg (i). (The calibration
  cleanliness is worth recording: this is the rare total-shots
  candidate whose virgin failure is a pure LL ranking loss, not
  the program's recurring calibration death.)
- Leg (iii): C's sign check vs arm A is 3/3 — moot under leg (i).

**Verdict: FAIL. Nothing ships.** The E9 trailing-r arm survived
a knife-edge dev gate and then lost the virgin LL to a constant
base rate whose own calibration (+1.24pp) was worse than C's —
the gate's LL leg does not grade on calibration curves, and the
result stands as measured.
