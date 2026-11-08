# Verdict — T-HR (HR-HNL total shots): **FAIL (virgin leg i)**

Frozen gates: PREREG_T_HR.md (e9872c4, before any fitting). Primary line 23.5,
ladder 22.5 / 23.5 / 24.5. Arms A (v1), B (v2 level layer, M_BAR = 24.10),
C (E9 trailing-200 r).

## Dev (warm-up 2021/2022; scored 2022/2023–2024/2025, n = 540)
Pooled LL@23.5: A **0.675982**, B **0.674827**, C **0.675685** vs league
base rate 0.702309, naive trailing-10 0.685905 → **all three arms pass
the dev gate**. (Tuned on the warm-up season: ridge lambda 300,
r_A = 159.74, level cell (30d, 0.5, 50).)

## Virgin 2025/2026 (n = 180) — read ONCE, for all dev-passing arms
| | LL@23.5 | calibration diff | SE |
|---|---|---|---|
| A | 0.705541 | +2.19pp | 3.77pp |
| B | 0.705873 | +2.36pp | 3.77pp |
| C | 0.704204 | +1.65pp | 3.76pp |
| League base rate | **0.693392** | +1.22pp | 3.73pp |
| Naive trailing-10 | 0.713549 | +4.11pp | 3.78pp |

Leg (i): an arm's LL must be ≤ arm A's AND ≤ the best baseline's.
**All three arms lose to the league base-rate baseline (0.693392)** →
leg (i) FAILS for every arm. Leg (ii) would have been PROVISIONAL for
all three (breaches 1.65–2.36pp, each within 1 SE of the boundary) —
moot under the mechanical reading. → **FAIL. Nothing ships.**

Independent verification: every virgin LL in the table (arms and both
baselines) was recomputed from the engine's per-match virgin
predictions file (`engine/total_shots/predictions_virgin.csv`, 540
arm-rows) against the league CSV — exact to all printed digits.

Diagnosis (recorded, not acted on): the virgin played at a higher
shots level than the dev era carried (actual over-23.5 rate 0.539;
virgin mean 24.53/match vs dev 24.10) and all three model arms
over-predicted the over-rate by ≈2pp while a constant base rate sat
closer — the ratings/level machinery added variance without adding
level accuracy on this window. The dev edge (0.675 vs naive 0.686)
did not survive contact with the virgin.
