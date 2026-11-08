# Verdict — C-FI (FI-Veikkausliiga corners): **FAIL (virgin calibration leg)**

Frozen gates: PREREG_C_FI.md (1889033, before any fitting). Primary line 9.5,
ladder 8.5 / 9.5 / 10.5. Single arm (X7 window-infeasible; X9 possession-only
by the frozen feed-forced divergence).

## Dev (warm-up 2021; scored 2022–2025, n = 678 stats rows)
Pooled LL@9.5: Gate Zero **0.690079** vs league base rate 0.742976,
naive trailing-10 0.733379 → dev gate PASS.

## Virgin 2026 (n = 177) — read ONCE
| | LL@9.5 | mean P(over) | actual over-rate |
|---|---|---|---|
| Gate Zero (model) | **0.699364** | 0.5899 | 0.5254 |
| League base rate | 0.724258 | 0.3993 | |
| Naive trailing-10 | 0.742790 | 0.3754 | |

Leg (i) PASS (0.699364 ≤ Gate Zero (= itself) and ≤ best baseline 0.724258).
Leg (ii): calibration diff **+6.45pp**; boundary 1.0pp, 1 SE = 3.76pp →
6.45 > 1.0 + 3.76 = 4.76 → breach beyond 1 SE → **FAIL**.
Leg (iii) vacuous (single arm). → **FAIL. Nothing ships.**

Diagnosis (recorded, not acted on): the model carried the dev era's
corner level (10.36/match, with 2025 at 10.96) into a virgin season that
played at 10.01/match, and its per-match means overshot further
(mean P(over 9.5) 0.590 against a 0.525 outcome). The LL still beat both
baselines — this is a pure calibration-leg failure on a thin virgin
(n = 177), exactly the failure mode the frozen leg exists to catch.
Virgin-fitted parameters (gamma 0.15, r 1.264, beta [0.0], fit_n 796) are
recorded in `results_virgin.json` for the record; they ship nothing.
