# Pre-registration — S-MX (Liga MX shots-on-target model)

Frozen: 2026-11-09, before any fitting. Branch `build/mx-ligamx`.
Design authority: `league/MX-LigaMX/analysis/MODEL_DESIGN.md` §2; features per `FEATURES.md` (X5 base, X4 quality; X6 dropped); evidence per `EDA.md` (F6/F7). Reference implementation: `model_sot.py` v5 as ported in `league/J1/engine/sot/` and AR.

## Target, blocks, and lines

- Target: stats-feed total SOT, blocked shots excluded.
- Blocks, chronological and regular phase only, 153 matches each: `2021/2022 - Apertura`, `2021/2022 - Clausura`, `2022/2023 - Apertura`, `2022/2023 - Clausura`, `2023/2024 - Apertura`, `2023/2024 - Clausura`, `2024/2025 - Apertura`, `2024/2025 - Clausura`, `2025/2026 - Apertura`, `2025/2026 - Clausura`. Blocks 1–9 are dev (n = 1,377); block 1 is warm-up, and scored dev is blocks 2–9 (n = 1,224), with per-match predict-then-update walk-forward. Virgin is block 10, n = 153, read once after dev freeze; dev never reads it.
- Primary line **8.5**; ladder **7.5 / 8.5 / 9.5**. Dev mean 8.92 and over-rate 51.2%. Gate legs use binary log-loss at 8.5.

## Reference architecture and arms

Gate Zero is v5: joint ridge Poisson team ratings, ridge lambda 100, HL 365, NB `r = 79.94`, Beta-Binomial on-target ratio with prior P = 200, 50/50 model/naive trailing-10 ensemble, and total-shots signal.

1. **GZ** — v5 unchanged.
2. **RS** — GZ with BB prior P = 20,000 pseudo-shots.
3. **X4** — Gate Zero with exactly one change, *in addition to* the raw total-shots signal (the AR X4 definition verbatim): the BB on-target ratio is replaced, per team and venue, by `ratio_X4 = rho_venue · (q_team / q_league)`, clamped to [0.15, 0.50], where `q_team` = Σ sm_xg / Σ sm_shots over the team's trailing 25 matches (any venue, strictly pre-match) with shotmap aggregates (regulation shots only); minimum 8 such matches, else the Gate Zero BB ratio for that team-venue; `q_league` = the same ratio of sums over all matches strictly before the predicted match; `rho_venue` = the decayed league SOT/shots ratio at that venue. Active in all blocks because shotmap coverage is 100%.

There is no X6 arm: EDA F7 found era-restricted xGOT reliability r = 0.073, which is NOISE in this league; `FEATURES.md` R5 drops it.

## Gates

Dev gate — pooled dev LL@8.5 must beat both league base rate and naive trailing-10, else the arm is dead and the virgin is not read. Virgin legs — (i) LL@8.5 ≤ Gate Zero's and ≤ best baseline's; (ii) `|mean predicted - actual| <= 1.0pp`, SE = `sd(pred_i - y_i)/sqrt(n)`, with a breach within 1 SE PROVISIONAL PASS and beyond it FAIL; (iii) variant dev LL@8.5 ≤ Gate Zero in at least half of the eight scored dev blocks (≥ 4 of 8). Both-pass: lower pooled virgin LL ships; ties go to the simpler arm, GZ before RS before X4. If no arm passes, S-MX is FAIL and nothing ships.

## Forbidden and presentation

No X6/xGOT, lineup/absence, finishing/conversion, standalone on-target-rate, half-share, two-stage generative, or post-match snapshot features. Predictions carry FT and 1H/2H lines via frozen SOT constant 0.455, presentation only.

## Outputs

- Engine: `league/MX-LigaMX/engine/sot/`.
- Dev results: `league/MX-LigaMX/engine/sot/results_dev.json` (+ CSV).
- Virgin results: `league/MX-LigaMX/engine/sot/results_virgin.json`.
- Fitted parameters: `league/MX-LigaMX/engine/sot/fitted_params_virgin.json`.
- Virgin predictions: `league/MX-LigaMX/predictions/s_mx_virgin_predictions.csv` — shipped-arm predictions, one row per virgin match with match id/date/teams, actual total SOT, expected home/away/total SOT, FT ladder probabilities over 7.5/8.5/9.5, and 1H/2H ladders derived presentation-only from the same total using frozen 0.455 and NB `r = 79.94`.
- Verdict: `league/MX-LigaMX/reports/S_MX_VERDICT.md`.

