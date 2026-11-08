# Verdict — C-ENGL1 (ENG-LeagueOne corners)

**PASS CLEAN — Gate Zero SHIPS.**

Calibration = actual − predicted. Primary line 9.5.

## Dev gate (walk-forward 2022/2023–2024/2025, pooled n=1,671)

| Arm | LL@9.5 | vs league base 0.7410 | vs naive 0.7386 |
|---|---|---|---|
| Gate Zero | 0.6877 | ✓ | ✓ |
| X7 | 0.6877 | ✓ | ✓ |

Both arms pass, with identical numbers: the fitted territorial /
box-touch betas are 0 in every dev fit (the trait is real, F2
r=0.870, but worth zero inside this multiplier structure — the J1
replication).

## Virgin (2025/2026, n=557, read ONCE)

| Arm | LL@9.5 | Calibration (act − pred) | SE |
|---|---|---|---|
| **Gate Zero** | **0.6930** | +0.93pp | 2.12pp |
| X7 | 0.6930 | +0.93pp | 2.12pp |
| league base rate | 0.7390 | — | — |
| naive trailing-10 | 0.7366 | — | — |

- Leg (i): 0.6930 ≤ Gate Zero and ≤ best baseline (0.7366) ✓.
- Leg (ii): |+0.93pp| ≤ 1.0pp → **CLEAN PASS** (the tightest
  calibration of this league's build).
- Leg (iii)/tie: both arms pass with identical virgin predictions
  (virgin fit: Gate Zero betas [0, 0]; X7 beta_bt = 0; gamma 0.15,
  r 1.157) → tie rule ships the simpler arm, **Gate Zero**.

Ships: `engine/corners/fitted_params_virgin.json` (arm gate_zero) +
`predictions/c_engl1_virgin_predictions.csv` (557 rows; FT ladder
8.5/9.5/10.5; 1H/2H presentation-only via frozen corners constant
0.4672). Coordinator's second-path recompute from the shipped CSV:
LL 0.693029, calibration −0.93pp (pred − actual) — exact match.
