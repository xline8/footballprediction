# Pre-registration — S-UA (Ukraine Premier League SOT model)

Frozen: 2026-11-10, before any fitting. Branch `build/ua-premier`.
Design authority: `analysis/MODEL_DESIGN.md` (S-UA); evidence EDA
(SOT for 0.948 / against 0.745, dev block). Reference: production
`model_sot.py` v5; sibling analogue
`league/CN-SuperLeague/prereg/PREREG_S_CN.md` — v5 constants
carried verbatim (ridge lambda = 100, HL = 365, lazy refit 7 days,
total-shots ratings prior K = 8, Beta-Binomial prior P = 200,
ensemble 50/50 with naive trailing-10, NB size r = 79.94 frozen).
Era restriction: fits use **2022/2023+ only** (war-era rule).
Stub rule: all-zero stats rows are stats-missing (PREPROCESSING).
Calibration = actual − predicted.

- Target: total SOT (stats feed). Primary line **6.5** (scored-dev
  over-rate 0.4957, closest to 0.5). Ladder 6.5 / 7.5 / 8.5, gate
  at 6.5. FT-only (no halves source exists in this league).
- Arms: **Gate Zero** (v5 unmodified); **RS** (BB prior 200→20,000).
- Walk-forward: per-match chronological (date, match_id),
  predict-then-update, date-grouped. Warm-up 2022/2023 updates
  state, never scored. Dev scored 2023/2024 + 2024/2025 (valid
  stats n = 462). Dev harness must not read 2025/2026 rows.
- Baselines: league base rate (prior-seasons over-6.5 rate,
  constant within target season); naive trailing-10 through the
  same NB.
- Virgin: 2025/2026 (valid stats n = 223), read ONCE, only for
  dev-passing arms, continuing from the dev end state.

## GATE LEGS (verbatim, frozen)
Dev gate — pooled dev LL@LINE beats BOTH baselines (league base rate; naive trailing-10), else the arm is dead, no virgin read. Virgin legs — (i) LL@LINE ≤ Gate Zero's AND ≤ best baseline's (Gate Zero: ≤ best baseline's); (ii) calibration |actual − mean P(over LINE)| ≤ 1.0pp, SE reported, breach within 1 SE = PROVISIONAL PASS; (iii) dev per-season sign check for both-pass (variant dev LL ≤ Gate Zero's in ≥1 of 2 dev seasons). Both-pass: both → lower pooled virgin LL ships; one → ships; none → FAIL. Ties → simpler arm (Gate Zero first). Gate Zero dev failure ⇒ variants moot, FAIL, virgin NOT read. Calibration = actual − predicted; SE = sd(y_i − p_i)/√n.

## Outputs
Engine `engine/sot/`; `results_dev.json`; `results_virgin.json`;
`fitted_params_virgin.json`; on PASS,
`predictions/s_ua_virgin_predictions.csv` (FT ladder only).
Verdict `reports/S_UA_VERDICT.md`.
