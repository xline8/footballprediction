# S-IS verdict — PASS (provisional, calibration leg) — Gate Zero ships

Prereg: `prereg/PREREG_S_IS.md`. Dev pooled n=324; virgin 2026 n=162, read once for both dev-passing arms. Primary line 9.5; ladder 8.5/9.5/10.5.

## Dev pooled LL

| Arm / baseline | 8.5 | 9.5 | 10.5 |
|---|---:|---:|---:|
| Gate Zero | 0.592631 | 0.654606 | 0.670223 |
| RS | 0.591662 | 0.654124 | 0.669079 |
| League base rate | 0.684830 | 0.697093 | 0.707211 |
| Naive trailing-10 | 0.595515 | 0.661973 | 0.675125 |

Both arms beat both dev baselines at 9.5. RS dev sign check versus GZ: 2024 pass, 2025 fail; 1/2, so pass.

## Virgin 2026

| Arm / baseline | 8.5 | 9.5 | 10.5 | Calibration at 9.5 |
|---|---:|---:|---:|---:|
| Gate Zero | 0.537842 | 0.631861 | 0.656002 | −1.398pp (SE 3.707pp) |
| RS | 0.538687 | 0.633819 | 0.657771 | −1.308pp (SE 3.715pp) |
| League base rate | 0.575894 | 0.672605 | 0.711505 | — |
| Naive trailing-10 | 0.543126 | 0.640239 | 0.661771 | — |

Gate arithmetic: GZ LL 0.631861 ≤ best baseline 0.640239; calibration breach 1.398pp ≤ 1pp + 3.707pp, provisional pass. RS LL 0.633819 is above GZ, though its calibration is provisional and its dev sign passes; it fails leg (i). GZ is the sole eligible arm and ships.

**Ships:** Gate Zero; fitted parameters and 2026 predictions are in `engine/sot/fitted_params_virgin.json` and `predictions/s_is_virgin_predictions.csv` (FT ladder plus frozen SOT halves constant 0.4644).
