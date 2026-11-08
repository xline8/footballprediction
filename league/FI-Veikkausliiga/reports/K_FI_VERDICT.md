# Verdict — K-FI (FI-Veikkausliiga cards): **PASS (PROVISIONAL) — Gate Zero ships**

Frozen gates: PREREG_K_FI.md (1889033, before any fitting). Primary line 3.5.
Single arm (X8 impossible: referee names empty in all of 2021–2024 and in
141/177 of 2025). Target = event-derived unified yellows for every season
(stats card keys exist only 2025–2026; the stats-vs-events check in EDA F6
showed exact agreement 81.9%/76.8% and mean Δ −0.040/−0.096 per match —
no era flip; the event target is forced by coverage, frozen in the prereg).

## Dev (warm-up 2021; scored 2022–2025, n = 678)
Gate Zero LL@3.5 **0.673991** vs league base rate 0.674319, naive 0.677092
→ dev gate PASS, by 0.000328 over the base rate — the thinnest dev margin
in this league's build, recorded as such. (Per season the model loses to
the base rate in 2022 and 2023 and wins in 2024 and 2025; the frozen gate
is on the pooled number.)

## Virgin 2026 (n = 177) — read ONCE
| | LL@3.5 | mean P(over) | actual |
|---|---|---|---|
| Gate Zero (model) | **0.679517** | 0.5039 | 0.5254 |
| League base rate | 0.694058 | | |
| Naive trailing-10 | 0.692489 | | |

Leg (i) PASS (0.679517 ≤ Gate Zero (= itself) and ≤ best baseline 0.692489).
Leg (ii): calibration diff **−2.16pp**; boundary 1.0pp, 1 SE = 3.71pp →
breach within 1 SE of the boundary (2.16 ≤ 4.71) → **PROVISIONAL PASS**.
Leg (iii) vacuous (single arm). → **PASS (PROVISIONAL). Gate Zero ships.**

Independent verification: LL@3.5, calibration diff and SE were recomputed
from the shipped per-match predictions CSV against the league CSV —
0.679517 / −2.16pp / 3.71pp, exact to all printed digits. The CSV's 1H
presentation share was also verified to be exactly this league's frozen
yellows constant 0.3109 on every row (the SE2 harness it was adapted from
carried a foreign 0.3344; corrected pre-ship, in the engine commit).

Ships: `predictions/k_fi_virgin_predictions.csv` (177 rows; FT ladder
2.5/3.5/4.5; 1H/2H expected totals presentation-only via the frozen
yellows constant 0.3109). Fitted NB size hit the estimator cap:
r = 500.0 for model/base/naive (`fitted_params_virgin.json`) — the
virgin-era yellows distribution is effectively Poisson at this scale;
recorded, not adjusted.
