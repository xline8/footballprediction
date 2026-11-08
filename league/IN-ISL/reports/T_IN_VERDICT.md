# Verdict — T-IN (India Indian Super League total shots)

**FAIL at the virgin gate (legs (i) and (ii), all arms).
Nothing ships.**

## Dev (walk-forward, scored 2022/2023–2024/2025, n=419; pooled LL@26.5)

| Arm / baseline | LL@26.5 |
|---|---|
| A (v1 pattern) | 0.6708 |
| B (v2 level layer) | 0.6681 |
| C (E9 trailing-r) | 0.6709 |
| League base rate | 0.6884 |
| Naive trailing-10 | 0.6754 |

All three arms beat both baselines → all three read the virgin.

## Virgin (2025/2026, n=91; read ONCE)

| Arm / baseline | LL@26.5 | Calibration (mean P − actual) | SE |
|---|---|---|---|
| A | 0.6172 | +9.90pp | 4.73pp |
| B | 0.6068 | +7.36pp | 4.72pp |
| C | 0.6170 | +9.86pp | 4.73pp |
| League base rate | 0.6619 | +13.43pp | — |
| Naive trailing-10 | **0.5945** | — | — |

## Gate arithmetic (frozen legs, applied mechanically)

- Leg (i): every arm loses to the best baseline — naive
  trailing-10 (0.5945) beats B (0.6068), C (0.6170) and A
  (0.6172). FAIL for all arms on this leg alone.
- Leg (ii): calibration breaches are +9.90 / +7.36 / +9.86pp;
  the breaches beyond the 1pp clean band (8.90 / 6.36 / 8.86pp)
  all exceed 1 SE (~4.7pp). FAIL for all arms — not provisional.
- The virgin season ran drastically cold on shot volume
  (24.45/match vs dev 26.48; actual over-26.5 rate 30.8% vs
  ~40% predicted by every arm and 44.2% by the base rate).
  Trailing-10 adapted fastest, which is why naive won the LL
  leg outright. The truncated single-round-robin virgin
  (F1) is the context; the gate is the gate, and no arm is
  rescued post-hoc.

## What ships

Nothing. No virgin predictions file exists for T-IN (correctly).
2026/2027 confirmatory untouched.
