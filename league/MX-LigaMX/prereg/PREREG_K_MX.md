# Pre-registration — K-MX (Liga MX cards model)

Frozen: 2026-11-09, before any fitting. Branch `build/mx-ligamx`.
Design authority: `league/MX-LigaMX/analysis/MODEL_DESIGN.md` §4; feature per `FEATURES.md` X8; evidence per `EDA.md` F8/F10. Reference implementation: `model_cards.py` as ported in `league/J1/engine/cards/` and AR.

## Target and frozen validation

Target is event-derived unified yellows (`card='Yellow'`). Dev-era evidence is stats 6,090 versus events 6,235 across scored plus warm-up dev blocks, with per-match agreement only 120–135/153. Blocks, chronological and regular phase only, are `2021/2022 - Apertura`, `2021/2022 - Clausura`, `2022/2023 - Apertura`, `2022/2023 - Clausura`, `2023/2024 - Apertura`, `2023/2024 - Clausura`, `2024/2025 - Apertura`, `2024/2025 - Clausura`, `2025/2026 - Apertura`, `2025/2026 - Clausura`, 153 matches each. Blocks 1–9 are dev (n = 1,377), block 1 warm-up and scored dev blocks 2–9 (n = 1,224), via per-match predict-then-update walk-forward. Virgin is block 10 (n = 153), read once after dev freeze; dev does not read it.

Primary line **4.5**; ladder **3.5 / 4.5 / 5.5**. Dev mean 4.53 and over-rate 47.5%; gates use LL@4.5.

## Architecture and arms

Gate Zero is the production cards pattern: venue-split decayed team ratings, HL = 270, shrinkage K = 8, NB size `r = 112.39`, and no referee covariate.

1. **Gate Zero** — reference unchanged.
2. **Arm X8** — referee covariate exactly as the AR referee arm: the expected total is multiplied by a referee factor built from the appointed referee's trailing in-league record — decayed (HL = 270) mean yellows per match over matches strictly before kickoff, shrunk toward the decayed league mean with prior K = 8 match-equivalents; factor = shrunk_ref_mean / league_mean, clamped to [0.8, 1.25]. Referees with no prior in-league matches get factor 1.0, and a match with no named referee likewise gets factor 1.0 (Gate Zero for that match; no referee is ever imputed). If the appointment is not published pre-match in the live pipeline, operationally fall back to Gate Zero. Coverage is 0% in warm-up, 24.8% in `2025/2026 - Apertura`, and 58.2% in the virgin block.

## Gates and presentation

Dev gate — pooled dev LL@4.5 must beat both league base rate and naive trailing-10. Virgin legs — (i) LL@4.5 ≤ Gate Zero's and ≤ best baseline's; (ii) calibration `|mean predicted - actual| <= 1.0pp`, SE = `sd(pred_i - y_i)/sqrt(n)`, within 1 SE PROVISIONAL PASS and beyond it FAIL; (iii) X8's dev LL must beat Gate Zero in at least 4 of 8 scored blocks. Both-pass: lower pooled virgin LL ships; ties go to Gate Zero. If no arm passes, K-MX is FAIL and nothing ships.

No red-card target or half-share card modelling. Predictions carry FT and 1H/2H lines via frozen yellows constant 0.385, presentation only.

## Outputs

- Engine: `league/MX-LigaMX/engine/cards/`.
- Dev results: `league/MX-LigaMX/engine/cards/results_dev.json` (+ CSV).
- Virgin results: `league/MX-LigaMX/engine/cards/results_virgin.json`.
- Fitted parameters: `league/MX-LigaMX/engine/cards/fitted_params_virgin.json`.
- Virgin predictions: `league/MX-LigaMX/predictions/k_mx_virgin_predictions.csv` — shipped-arm predictions, one row per virgin match with match id/date/teams/referee, actual unified yellows, expected total, FT ladder probabilities over 3.5/4.5/5.5, and 1H/2H ladders derived presentation-only using frozen 0.385 and NB `r = 112.39`.
- Verdict: `league/MX-LigaMX/reports/K_MX_VERDICT.md`.

