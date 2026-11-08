# Pre-registration — T-UA (Ukraine Premier League total-shots model)

Frozen: 2026-11-10, before any fitting. Branch `build/ua-premier`.
Design authority: `analysis/MODEL_DESIGN.md` (T-UA); evidence EDA
(shots for 0.880 / against 0.727, dev block). Reference: the shots
family as frozen for T-J1 (v1 / v2 level layer / E9 trailing-r) —
see `league/J1/prereg/PREREG_T_J1.md`, mirrored changing only
league, seasons and line; sibling run
`league/CN-SuperLeague/prereg/PREREG_T_CN.md`. (T-J1 ran ahead of
the top-5 prospective verdict by user order; T-UA is a separate
corpus.) Era restriction: 2022/2023+ only. Stub rule applies.
Calibration = actual − predicted.

- Target: total shots (stats feed, as-is; scored-dev level
  ~13.8/match in THIS feed). Primary line **14.5** (scored-dev
  over-rate 0.4827). Ladder 13.5 / 14.5 / 15.5, gate at 14.5.
  FT-only (no halves source).
- Arms: **A** v1 pattern (ratings + NB + naive ensemble);
  **B** v2 pattern (+ level layer); **C** E9 (NB r from trailing
  window, league-level analogue).
- Seed 2022/2023; dev 2023/2024 + 2024/2025 (valid stats n = 462).
  Dev harness must not read 2025/2026 rows.
- Baselines: league base rate; naive trailing-10.
- Virgin: 2025/2026 (valid stats n = 223), read ONCE, only for
  dev-passing arms.

## GATE LEGS (verbatim, frozen)
Dev gate — pooled dev LL@14.5 beats BOTH baselines, else the arm
is dead, no virgin read. Virgin legs — (i) LL@14.5 ≤ the reference
arm's (arm A if it passes dev; otherwise the dev-passing arm with
the lowest pooled dev LL) AND ≤ best baseline's; (ii) calibration
|actual − mean P(over 14.5)| ≤ 1.0pp, SE reported, breach within
1 SE = PROVISIONAL PASS; (iii) dev per-season sign check for
both-pass (variant dev LL ≤ reference arm's in ≥1 of 2 dev
seasons). Both-pass: among passing arms, lower pooled virgin LL
ships; one → ships; none → FAIL. Ties → A before B before C. If
arm A fails dev and no other arm passes dev, FAIL, virgin NOT
read.

## Outputs
Engine `engine/total_shots/`; `results_dev.json`;
`results_virgin.json`; `fitted_params_virgin.json`; on PASS,
`predictions/t_ua_virgin_predictions.csv` (FT ladder only).
Verdict `reports/T_UA_VERDICT.md`.
