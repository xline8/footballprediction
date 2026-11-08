# Verdict — C-ES (ES-LaLiga2 corners) — **PROVISIONAL PASS** (X7 ships)

Prereg: `prereg/PREREG_C_ES.md`. Primary line 9.5. Dev n=1,404,
virgin 2025/2026 n=468.

## Dev (pooled LL@9.5; baselines: league 0.7054, naive 0.7068)

| Arm | Dev LL | Per-season sign vs GZ | Dev outcome |
|---|---|---|---|
| Gate Zero (X9) | 0.6938 | — | PASS |
| X7 | **0.6882** | 3/3 | PASS |

## Virgin 2025/2026 (both arms, per the frozen rule)

| Arm | LL@9.5 | Calibration (SE) |
|---|---|---|
| GZ | 0.6962 | −1.89pp (2.32pp) |
| X7 | **0.6923** | −1.80pp (2.31pp) |
| Baselines | naive 0.7153 / league 0.7195 | |

Gate arithmetic: leg (i) both arms ≤ Gate Zero / best baseline
0.7153 ✓ for X7 (0.6923 ≤ 0.6962 ✓); leg (ii) both breach 1.0pp but
the excesses (0.89pp / 0.80pp) are within 1 SE (2.32 / 2.31pp) →
PROVISIONAL for both; leg (iii) X7 3/3 ✓. Both-pass rule: lower
pooled virgin LL ships → **X7 ships, PROVISIONAL PASS**. The virgin
season's corners ran near dev levels (actual over-9.5 0.472) but
both arms under-predicted by ~1.8pp — inside the provisional band.

Construction fact, recorded plainly (the IN-ISL "beta = 0" pattern
again): X7's fitted box-touch beta is **0.0 in the virgin fit** (and
the dev fits report active-with-nonzero-beta share 0.0 throughout).
The arm's edge over Gate Zero is therefore not a box-touch tilt at
work — it is the *absence* of Gate Zero's non-zero big-chance tilt
(virgin beta [0, 0.025]), which transferred slightly worse. The
pre-registered arm as fitted by the verbatim reference procedure is
what ships; the mechanism is named here so nobody reads a
territorial effect into it later.

**Ships: X7** (`engine/corners/fitted_params_virgin.json`;
`predictions/c_es_virgin_predictions.csv`; halves via 0.4692).
Independent checks: virgin LL@9.5 (0.692288) and calibration
(−1.795pp, SE 2.310pp) recomputed by hand from the shipped
predictions CSV; the CSV's probabilities reproduce exactly from its
own (mu, r) via the NB tail on sampled rows.
