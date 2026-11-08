# Pre-registration — C-MX (Liga MX corners model)

Frozen: 2026-11-09, before any fitting. Branch `build/mx-ligamx`.
Design authority: `league/MX-LigaMX/analysis/MODEL_DESIGN.md` §3; features per `FEATURES.md` (X5, X7, X9); evidence per `EDA.md` (F2/F9). Reference implementation: `model_corners_v3` as ported in `league/J1/engine/corners/` and AR.

## Target and frozen validation

Target is stats-feed total corners. Blocks, chronological and regular phase only, 153 matches each: `2021/2022 - Apertura`, `2021/2022 - Clausura`, `2022/2023 - Apertura`, `2022/2023 - Clausura`, `2023/2024 - Apertura`, `2023/2024 - Clausura`, `2024/2025 - Apertura`, `2024/2025 - Clausura`, `2025/2026 - Apertura`, `2025/2026 - Clausura`. Blocks 1–9 are dev (n = 1,377), with block 1 warm-up and scored dev blocks 2–9 (n = 1,224), via per-match predict-then-update walk-forward. Virgin is block `2025/2026 - Clausura` (n = 153), read once after dev freeze; dev does not read virgin rows.

Primary line **9.5**; ladder **8.5 / 9.5 / 10.5**. Dev mean 9.79 and over-rate 50.8%; all gates use LL@9.5.

## Architecture and arms

Reference `model_corners_v3`: decay-weighted base rates, rolling-5 shots relative factors, NB total, and territorial multiplier `exp(beta·z)` clamped to [0.70, 1.43], with parameters fitted on fit data only.

1. **Gate Zero** — production possession + big-chance multiplier (X9).
2. **Arm X7** — identical except the territorial multiplier uses trailing opp-box touches for/against, with the minimum-8 rule.

## Gates and presentation

Dev gate — pooled dev LL@9.5 must beat both the league base rate and naive trailing-10. Virgin legs — (i) LL@9.5 ≤ Gate Zero's and ≤ best baseline's; (ii) calibration `|mean predicted - actual| <= 1.0pp`, SE = `sd(pred_i - y_i)/sqrt(n)`, within 1 SE PROVISIONAL PASS and beyond it FAIL; (iii) X7's dev LL must beat Gate Zero in at least 4 of 8 scored blocks. Both-pass: lower pooled virgin LL ships; ties go to Gate Zero. If no arm passes, C-MX is FAIL and nothing ships.

No half-share corner modelling or covariates outside X7/X9. Predictions carry FT and 1H/2H lines via frozen corners constant 0.465, presentation only.

## Outputs

- Engine: `league/MX-LigaMX/engine/corners/`.
- Dev results: `league/MX-LigaMX/engine/corners/results_dev.json` (+ CSV).
- Virgin results: `league/MX-LigaMX/engine/corners/results_virgin.json`.
- Fitted parameters: `league/MX-LigaMX/engine/corners/fitted_params_virgin.json`.
- Virgin predictions: `league/MX-LigaMX/predictions/c_mx_virgin_predictions.csv` — shipped-arm predictions, one row per virgin match with match id/date/teams, actual total corners, expected total, FT ladder probabilities over 8.5/9.5/10.5, and 1H/2H ladders derived presentation-only using frozen 0.465.
- Verdict: `league/MX-LigaMX/reports/C_MX_VERDICT.md`.

