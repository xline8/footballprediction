# Verdict — C-HR (HR-HNL corners): **PASS (PROVISIONAL) — X7 ships**

Frozen gates: PREREG_C_HR.md (e9872c4, before any fitting). Primary line 8.5,
ladder 7.5 / 8.5 / 9.5.

## Dev (warm-up 2021/2022; scored 2022/2023–2024/2025, n = 540 stats rows)
Pooled LL@8.5: Gate Zero **0.695758**, X7 **0.693357** vs league base rate
0.725167, naive trailing-10 0.725569 → **both arms pass the dev gate**.
Per season (model LL@8.5): 2022/2023 GZ 0.692870 / X7 0.699212;
2023/2024 GZ 0.691735 / X7 0.685724; 2024/2025 GZ 0.702669 / X7 0.695135
→ X7 sign check: ≤ GZ in 2 of 3 dev seasons ✓.

**What X7 actually is here, stated plainly:** the fitted touches beta
is **0.0 in every dev season and in the virgin fit** (dev
active-with-nonzero-beta share = 0.0 despite a 63.9% both-teams-active
share). The X7 arm therefore never applies a touches multiplier — it
is the corners_v3 core *without* the territorial multiplier, and it
beat Gate Zero (whose virgin-fitted betas are [poss 0.0, bc +0.025])
because the territorial multiplier itself was the worse component in
this league. The ship is honest under the frozen arm definition, but
no box-touch signal ships: the fitted coefficient is zero.

## Virgin 2025/2026 (n = 180) — read ONCE, for both dev-passing arms
| | LL@8.5 | mean P(over) | actual over-rate | calibration diff | SE |
|---|---|---|---|---|---|
| Gate Zero | 0.693697 | 0.5462 | 0.5778 | −3.16pp | 3.73pp |
| X7 | **0.685221** | 0.5481 | 0.5778 | −2.97pp | 3.70pp |
| League base rate | 0.758846 | 0.3824 | | | |
| Naive trailing-10 | 0.749282 | 0.3954 | | | |

Leg (i) PASS for both (X7 0.685221 ≤ GZ 0.693697 and ≤ best baseline
0.749282). Leg (ii): breaches 3.16pp / 2.97pp vs the 1.0pp boundary,
both within 1 SE (3.16 ≤ 1.0 + 3.73; 2.97 ≤ 1.0 + 3.70) →
**PROVISIONAL PASS** for both. Leg (iii) X7 ✓ (above). Both-pass rule:
lower pooled virgin LL ships → **X7 ships, PASS (PROVISIONAL)**.

Independent verification: LL@8.5, calibration diff and SE were
recomputed from the shipped per-match predictions CSV against the
league CSV — 0.685221 / −2.97pp / 3.70pp, exact to all printed digits.
The CSV's 1H presentation share was verified to be exactly this
league's frozen corners constant 0.4793 on every row (the J1 seed
carried a foreign 0.447; corrected pre-ship, in the engine adaptation).

Ships: `predictions/c_hr_virgin_predictions.csv` (180 rows; FT ladder
7.5/8.5/9.5; 1H/2H expected totals presentation-only via the frozen
corners constant 0.4793). Virgin-fitted params: gamma 0.15,
r = 1.158, X7 beta [0.0] (fit_n 710) in
`engine/corners/fitted_params_virgin.json`.
