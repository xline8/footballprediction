# Verdict — C-IN (India Indian Super League corners)

**PASS (PROVISIONAL, calibration) — Gate Zero SHIPS.**
Primary line 10.5. Virgin predictions:
`predictions/c_in_virgin_predictions.csv` (Gate Zero, n=91).

## Dev (walk-forward, scored 2022/2023–2024/2025, n=419; pooled LL@10.5)

| Arm / baseline | LL@10.5 |
|---|---|
| Gate Zero (X9) | 0.6933 |
| X7 | 0.6973 |
| League base rate | 0.7094 |
| Naive trailing-10 | 0.7023 |

Both arms beat both baselines → both read the virgin.

## Virgin (2025/2026, n=91; read ONCE)

| Arm / baseline | LL@10.5 | Calibration (mean P − actual) | SE |
|---|---|---|---|
| Gate Zero | 0.6835 | −3.00pp | 5.21pp |
| X7 | 0.6859 | −3.10pp | 5.22pp |
| League base rate | 0.7035 | — | — |
| Naive trailing-10 | 0.7037 | — | — |

## Gate arithmetic (frozen legs, applied mechanically)

- **Gate Zero**: leg (i) 0.6835 ≤ best baseline 0.7035 ✓;
  leg (ii) |−3.00pp| > 1pp clean band, breach beyond the band
  (2.00pp) within 1 SE (5.21pp) → **PROVISIONAL PASS**. (The
  virgin was the corpus's hottest corners season, 10.53/match,
  against a model centred on dev levels; the under-prediction
  is the recorded direction.)
- **X7**: leg (i) fails (0.6859 > Gate Zero 0.6835) and leg
  (iii) fails. Its fitted box-touch beta on the virgin fit is
  **0 again** (`active_with_nonzero_beta_share = 0.0`) — the
  F9 trait (r=0.783/0.850) is real, and worth zero inside this
  multiplier structure, replicating J1/DK/AU/AR/BR/SE. Recorded
  plainly; the gate, not the trait table, decides.

Independent verification: LL@10.5 recomputed from the shipped
predictions CSV by a second path — 0.6835, exact.

## What ships

Gate Zero (production corners pattern, X9 covariates;
γ=0.15, r=1.2142, β=[0.0025, −0.025], fit_n=524), fitted params
in `engine/corners/fitted_params_virgin.json`. FT ladder
9.5/10.5/11.5; 1H/2H presentation-only via the frozen corners
constant 0.458.
