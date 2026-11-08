# Pre-registration — C-MA (Morocco Botola Pro corners model)

Frozen: 2026-11-10, before any fitting. Branch `build/ma-botola`.
Design authority: `league/MA-BotolaPro/analysis/MODEL_DESIGN.md`
(C-MA); features per `analysis/FEATURES.md` (X9 partially adopted:
possession only; X7 DROPPED — `touches_opp_box` absent from the
feed; `big_chance` likewise absent). Reference: production
`model_corners_v3.py` pattern as frozen in
`league/J1/prereg/PREREG_C_J1.md`, with the territorial multiplier
reduced to its possession term exactly as in
`league/SCO-Championship/prereg/PREREG_C_SCOCH.md` (possession beta
grid ±{0, .0025, .005, .0075, .010}; big-chance term OMITTED).
Phase rule (frozen): all rows are phase `regular`; no phase
feature anywhere.
Calibration = **actual − predicted** everywhere in this build.

## Era rule (frozen)

Identical to PREREG_S_MA: the corners target exists ONLY in the
rich era (date >= 2024-11-01); pre-era rows and rich-era rows
without a stats block are never scored and never update state.

- Target: total corners = `corners_home + corners_away` (stats
  feed). Primary line **8.5** (rich dev-era over-rate 0.476,
  closest to 0.5). Ladder 7.5 / 8.5 / 9.5 reported, gate at 8.5.
- Arms: **Gate Zero only** — the production pattern with the
  possession-only territorial covariate (beta grid above). X7 is
  NOT an arm. No variant arm is registered; the dev gate decides
  whether the single arm lives.
- Walk-forward: per-match, chronological (date, match_id),
  predict-then-update, date-grouped. Warm-up, dev, virgin windows
  and state rules exactly as PREREG_S_MA (dev scored stats
  n = 109; virgin stats n = 226, continuing from dev end state).
- Baselines: league base rate (per-season NB from decay-weighted
  pre-window rows, as PREREG_C_J1) and naive trailing-10 (X5)
  through the same NB size.
- Virgin: 2025/2026 (n = 226), read ONCE, only if Gate Zero passes
  the dev gate. Calibration at 8.5 = actual − mean predicted,
  SE = sd(y_i − p_i)/√n.
- Halves: NONE — no period splits exist in this league and corners
  have no event source; FT presentation only.

## GATE LEGS (verbatim, frozen)

Dev gate — pooled dev LL@8.5 beats BOTH baselines (league base rate; naive trailing-10), else the candidate is dead, no virgin read. Virgin legs — (i) LL@8.5 ≤ best baseline's; (ii) calibration |actual − mean P(over 8.5)| ≤ 1.0pp, SE reported, breach within 1 SE = PROVISIONAL PASS. If Gate Zero passes all legs it ships; if any leg fails, C-MA verdict is FAIL and nothing ships.

Mechanical reading: Gate Zero passes iff it survives the dev gate
AND passes virgin legs (i)–(ii) (PROVISIONAL counts, recorded as
such). Gate Zero dev failure ⇒ FAIL, virgin NOT read.

## Outputs

Engine `league/MA-BotolaPro/engine/corners/`; `results_dev.json`
(+ `predictions_dev.csv`); `results_virgin.json`;
`fitted_params_virgin.json`; on PASS,
`predictions/c_ma_virgin_predictions.csv` (FT ladder 7.5/8.5/9.5;
NO halves columns — FT only). Verdict `reports/C_MA_VERDICT.md`.
Production code untouched. No push. No merge.
