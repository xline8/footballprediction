# Pre-registration — G-MX (Liga MX goals model)

Frozen: 2026-11-09, before any fitting. Branch `build/mx-ligamx`.
Design authority: `league/MX-LigaMX/analysis/MODEL_DESIGN.md` §1 and shared validation frame; features per `FEATURES.md` (X1 blend, X3 set-play; X2 dropped); evidence per `EDA.md` (F1/F2/F4/F5/F13). Reference implementation: production Dixon-Coles, as ported in `league/AR-LigaProfesional/engine/goals/` and `league/J1/engine/goals/`.

## Data, target, and frozen blocks

- Blocks, chronological and regular phase only, 153 matches each: `2021/2022 - Apertura`, `2021/2022 - Clausura`, `2022/2023 - Apertura`, `2022/2023 - Clausura`, `2023/2024 - Apertura`, `2023/2024 - Clausura`, `2024/2025 - Apertura`, `2024/2025 - Clausura`, `2025/2026 - Apertura`, `2025/2026 - Clausura`.
- Dev blocks 1–9 contain n = 1,377. Block 1 is warm-up/training only; scored dev is blocks 2–9, n = 1,224, under expanding block-blocked fits.
- Virgin block: `2025/2026 - Clausura`, n = 153. Fit/state uses only matches strictly before its first match; read ONCE after dev results freeze. The dev harness must not read virgin rows.
- Target is the goals model's match outcome set: 1X2, OU, BTTS, with Dixon-Coles score probabilities.

## Reference architecture

All arms use the production pattern: Dixon-Coles fit with per-division rho selected from the frozen grid, 14 sweeps, damping 0.7, +0.25 smoothing, home advantage and attack/defence ratings, score matrix `MAXG = 10`, exponential decay half-life 270 days, and observation blend 0.5 goals + 0.5 xG. xG is 100% available in every block, so the goals-only fallback never binds. Fits are expanding and block-blocked, using only matches dated strictly before the target block.

## Arms

1. **Gate Zero** — the unmodified reference architecture.
2. **Arm X3** — Gate Zero plus the set-play tilt exactly as the AR X3 arm: trailing ratio-of-sums open-play/set-play xG, minimum 8 xG matches, multipliers clamped to [0.5, 2.0], shrinkage exponent 0.5.

There is no X2 arm: no movers exist; X2 was dropped in `FEATURES.md` and EDA F4.

## Dev and virgin gates

Dev metrics per arm per block and pooled are mean 1X2 log-loss, RPS (H/D/A), and OU2.5 log-loss. The dev gate requires pooled 1X2 LL and RPS to beat climatology, and OU2.5 LL to beat the climatology/base-rate baseline. The dev harness must not read the virgin block.

Virgin legs — (i) 1X2 log-loss ≤ Gate Zero's and ≤ climatology's; (ii) calibration for home-win probability and OU2.5 over-rate satisfies `|mean predicted - actual| <= 1.0pp`; SE = `sd(pred_i - y_i)/sqrt(n)`, and a breach within 1 SE of the boundary is PROVISIONAL PASS, beyond it FAIL; (iii) variant dev per-block sign check: LL ≤ Gate Zero in at least half of the eight scored dev blocks (≥ 4 of 8). Both-pass rule: if both pass all legs, lower pooled virgin 1X2 log-loss ships; ties go to Gate Zero. An arm passes only if it survives dev and virgin legs; if none passes, G-MX is FAIL and nothing ships.

## Forbidden and presentation

No X2, half-share, finishing/conversion, absence, altitude, standings, H2H, or post-match snapshot features. Predictions carry FT plus 1H/2H lines using the frozen goals constant 0.456; halves are presentation only and are derived from the same FT lambdas.

## Outputs

- Engine: `league/MX-LigaMX/engine/goals/` (this league's own fit/predict/harness modules and CLI runner).
- Dev results: `league/MX-LigaMX/engine/goals/results_dev.json` (+ CSV).
- Virgin results: `league/MX-LigaMX/engine/goals/results_virgin.json`.
- Fitted parameters: `league/MX-LigaMX/engine/goals/fitted_params_virgin.json`.
- Virgin predictions: `league/MX-LigaMX/predictions/g_mx_virgin_predictions.csv` — shipped-arm predictions, one row per virgin match with match id/date/teams, actual goals, FT lambdas, FT 1X2/OU/BTTS probabilities, and 1H/2H ladders derived presentation-only from the same lambdas and frozen 0.456 split.
- Verdict: `league/MX-LigaMX/reports/G_MX_VERDICT.md`.

