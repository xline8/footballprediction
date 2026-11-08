# Pre-registration — T-MX (Liga MX total shots model)

Frozen: 2026-11-09, before any fitting. Branch `build/mx-ligamx`.
Design authority: `league/MX-LigaMX/analysis/MODEL_DESIGN.md` §5; features per `FEATURES.md` X5 and the shots-family components; evidence per `EDA.md` F2. Reference implementation: shots family in `experiments/shots_model/`, as ported in `league/J1/engine/total_shots/`.

**Prospective-trial provenance.** The reference family is under a frozen prospective trial on the top-5 (v2 + E9 challenger), with verdict due at n ≥ 1,200 or season end — not reached. Under the standing J.League §6 override applied program-wide by the conveyor template, T-MX is built now on this corpus only; the top-5 trial is untouched and neither result contaminates the other.

## Target and frozen validation

Target is stats-feed total shots. Blocks, chronological and regular phase only, 153 matches each: `2021/2022 - Apertura`, `2021/2022 - Clausura`, `2022/2023 - Apertura`, `2022/2023 - Clausura`, `2023/2024 - Apertura`, `2023/2024 - Clausura`, `2024/2025 - Apertura`, `2024/2025 - Clausura`, `2025/2026 - Apertura`, `2025/2026 - Clausura`. Blocks 1–9 are dev (n = 1,377), block 1 warm-up and scored dev blocks 2–9 (n = 1,224), via per-match predict-then-update walk-forward. Virgin is block `2025/2026 - Clausura` (n = 153), read once after dev freeze; dev never reads virgin rows.

Primary line **26.5**; ladder **25.5 / 26.5 / 27.5**. Dev mean 26.65 and over-rate 47.9%; all gates use LL@26.5.

## Arms

1. **Arm A / Gate Zero** — v1 pattern: joint ridge Poisson team ratings, NB, and 50/50 model plus naive trailing-10 ensemble.
2. **Arm B** — v2 pattern, Arm A plus the frozen level layer.
3. **Arm C** — E9 mechanism, Arm A with NB size from the league-level trailing-r window.

No constants are re-searched on this corpus; only the per-league fit and the frozen reference mechanisms are used. Where the port takes the corpus mean as an input constant (M_BAR, as the AR T prereg froze it), the value here is this league's dev mean total shots **26.65** — a data input, not a tuned parameter.

## Gates and presentation

Dev gate — pooled dev LL@26.5 must beat both league base rate and naive trailing-10. Virgin legs — (i) LL@26.5 ≤ Arm A's and ≤ best baseline's; (ii) calibration `|mean predicted - actual| <= 1.0pp`, SE = `sd(pred_i - y_i)/sqrt(n)`, within 1 SE PROVISIONAL PASS and beyond it FAIL; (iii) each variant's dev LL must beat Arm A in at least 4 of 8 scored blocks. Both-pass: lower pooled virgin LL ships; ties go to the simpler arm, A before B before C. If no arm passes, T-MX is FAIL and nothing ships.

No half-share shot modelling or arms beyond A/B/C. Predictions carry FT and 1H/2H lines via frozen total-shots constant 0.458, presentation only.

## Outputs

- Engine: `league/MX-LigaMX/engine/total_shots/`.
- Dev results: `league/MX-LigaMX/engine/total_shots/results_dev.json` (+ CSV).
- Virgin results: `league/MX-LigaMX/engine/total_shots/results_virgin.json`.
- Fitted parameters: `league/MX-LigaMX/engine/total_shots/fitted_params_virgin.json`.
- Virgin predictions: `league/MX-LigaMX/predictions/t_mx_virgin_predictions.csv` — shipped-arm predictions, one row per virgin match with match id/date/teams, actual total shots, expected total, FT ladder probabilities over 25.5/26.5/27.5, and 1H/2H ladders derived presentation-only using frozen 0.458.
- Verdict: `league/MX-LigaMX/reports/T_MX_VERDICT.md`.

