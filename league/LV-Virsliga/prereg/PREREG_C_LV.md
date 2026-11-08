# Pre-registration — C-LV (Latvia Virsliga corners model)

Frozen: 2026-11-10, before any fitting. Branch `build/lv-virsliga`.
Design authority: `league/LV-Virsliga/analysis/MODEL_DESIGN.md`
(C-LV); features per `analysis/FEATURES.md` (X9 partially adopted:
possession only — `big_chance` is identically 0 in all 359
stats-era matches; X7 DROPPED — `touches_opp_box` absent from
every payload). Reference: production `model_corners_v3.py`
pattern as frozen in `league/J1/prereg/PREREG_C_J1.md`, with the
territorial multiplier reduced to its possession term exactly as
in `league/SCO-Championship/prereg/PREREG_C_SCOCH.md`
(possession beta grid ±{0, .0025, .005, .0075, .010}; big-chance
term OMITTED — the key is dead in this league, not merely absent).
Phase rule (frozen): all rows are phase `regular`; no phase
feature anywhere.
Calibration = **actual − predicted** everywhere in this build.

## Virgin-hygiene disclosure

As in PREREG_G_LV: step-1 inventory aggregates (including 2026)
are era facts; no per-match model output and no gate quantity was
computed from 2026 before this freeze. The virgin is NOT burned.

## Era rule (frozen)

Identical to PREREG_S_LV: the corners target exists ONLY in the
stats era (seasons 2025+); pre-era rows are never scored and
never update state.

- Target: total corners = `corners_home + corners_away` (stats
  feed). Primary line **9.5** (2025 dev-era over-rate 0.539,
  closest to 0.5). Ladder 8.5 / 9.5 / 10.5 reported, gate at 9.5.
- Arms: **Gate Zero only** — the production pattern with the
  possession-only territorial covariate (beta grid above). X7 is
  NOT an arm. No variant arm is registered; the dev gate decides
  whether the single arm lives.
- Walk-forward: per-match, chronological (date, match_id),
  predict-then-update, date-grouped. Warm-up, dev, virgin windows
  and state rules exactly as PREREG_S_LV (dev scored n = 133;
  virgin n = 179, continuing from dev end state).
- Baselines: league base rate (per-season NB from decay-weighted
  pre-window rows, as PREREG_C_J1) and naive trailing-10 (X5)
  through the same NB size.
- Virgin: 2026 (n = 179), read ONCE, only if Gate Zero passes
  the dev gate. Calibration at 9.5 = actual − mean predicted,
  SE = sd(y_i − p_i)/√n.
- Halves: FT + 1H/2H via frozen corners constant 0.4816 from 2025
  period splits (presentation only; true per-match share variance
  = 0).

## GATE LEGS (verbatim, frozen)

Dev gate — pooled dev LL@9.5 beats BOTH baselines (league base rate; naive trailing-10), else the candidate is dead, no virgin read. Virgin legs — (i) LL@9.5 ≤ best baseline's; (ii) calibration |actual − mean P(over 9.5)| ≤ 1.0pp, SE reported, breach within 1 SE = PROVISIONAL PASS. If Gate Zero passes all legs it ships; if any leg fails, C-LV verdict is FAIL and nothing ships.

Mechanical reading: Gate Zero passes iff it survives the dev gate
AND passes virgin legs (i)–(ii) (PROVISIONAL counts, recorded as
such). Gate Zero dev failure ⇒ FAIL, virgin NOT read.

## Outputs

Engine `league/LV-Virsliga/engine/corners/`; `results_dev.json`
(+ `predictions_dev.csv`); `results_virgin.json`;
`fitted_params_virgin.json`; on PASS,
`predictions/c_lv_virgin_predictions.csv` (FT ladder 8.5/9.5/10.5;
1H/2H presentation via frozen corners constant 0.4816).
Verdict `reports/C_LV_VERDICT.md`. Production code untouched.
No push. No merge.
