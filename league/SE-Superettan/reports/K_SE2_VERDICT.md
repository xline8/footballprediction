# Verdict — K-SE2 (SE-Superettan cards): **PASS (PROVISIONAL) — Gate Zero ships**

Frozen gates: PREREG_K_SE2.md (730a5c1, before fitting). Primary line 3.5.
Single arm (X8 impossible: referee names empty in 1,440/1,440 payloads).
Target = event-derived unified yellows (the stats feed publishes no card
keys; frozen with the reason in the prereg).

## Dev (warm-up 2021; scored 2022–2025, n = 960)
Gate Zero LL@3.5 **0.672526** vs league base rate 0.690891, naive 0.682459 → dev gate PASS.

## Virgin 2026 (n = 240) — read ONCE
| | LL@3.5 | mean P(over) | actual |
|---|---|---|---|
| Gate Zero (model) | **0.667511** | 0.4377 | 0.4000 |
| League base rate | 0.682322 | | |
| Naive trailing-10 | 0.691608 | | |

Leg (i) PASS (0.667511 ≤ Gate Zero (= itself) and ≤ best baseline 0.682322).
Leg (ii): calibration diff **+3.77pp**; boundary 1.0pp, 1 SE = 3.14pp →
breach within 1 SE of the boundary (3.77 ≤ 4.14) → **PROVISIONAL PASS**.
Leg (iii) vacuous (single arm). → **PASS (PROVISIONAL). Gate Zero ships.**

Independent verification: LL@3.5 and calibration were recomputed from the
shipped per-match predictions CSV against the league CSV — 0.667511 and
+3.77pp / SE 3.14pp, exact to all printed digits.

Ships: `predictions/k_se2_virgin_predictions.csv` (240 rows; FT ladder
2.5/3.5/4.5; 1H/2H expected totals presentation-only via the frozen yellows
constant 0.3344). The virgin NB size for the model was r = 152.09
(results_virgin.json).

## Defect caught pre-ship (presentation only)
The copied SE harness split expected totals with SE-Allsvenskan's yellows
constant 0.370. Corrected to this league's frozen 0.3344 and the predictions
regenerated; virgin metrics reproduced identically (LL 0.667511) and the
shipped CSV's 1H share is exactly 0.3344. FT probabilities and the gate
outcome were never affected.
