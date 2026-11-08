# Pre-registration — C-EG (EG-PremierLeague corners model)

Frozen: 2026-11-09, before any fitting. Branch `build/eg-premier`.
Design authority: `analysis/MODEL_DESIGN.md` (C-EG); features X5
base, X9 Gate Zero covariates, X7 box touches (FEATURES.md —
adopted: touches-for split-half r = 0.877 career / 0.791 on the
2023/2024–2024/2025 era, touches-against 0.695 / 0.719; coverage
39.2% → 98.7% across the dev era, min-8 trailing rule absorbs the
early era); evidence EDA F1/F2/F5. Reference: production
`model_corners_v3.py`; SA analogue
`league/SA-ProLeague/prereg/PREREG_C_SA.md` and its engine — copy
the architecture and arm constructions, changing only league,
seasons, line and data columns.
Phase rule (frozen, MODEL_DESIGN): all phases are ordinary rows in
every window; no phase feature anywhere.

- Target: total corners = `corners_home + corners_away` (stats
  feed). Primary line **8.5** (scored-dev pooled 2022/2023–2024/2025
  over-rate 0.556, closest to 0.5). Ladder 7.5 / 8.5 / 9.5
  reported, gate at 8.5.
- Arms: **Gate Zero** (corners_v3 unmodified, X9 territorial
  covariates: trailing possession + big chances); **X7** (Gate
  Zero with the territorial multiplier's covariates replaced by
  trailing opp-box touches for/against, exactly as the SA C engine's
  X7 arm; min-8 window matches with the stat, else the arm falls
  back to Gate Zero's multiplier for that match, as in the
  reference).
- Walk-forward: per-match, chronological (date, match_id),
  predict-then-update, date-grouped. Warm-up: 2021/2022 updates
  state, never scored.
- Dev: scored seasons 2022/2023–2024/2025 (rows with the target
  present; n = 826 of 837). The dev harness must not read
  2025/2026 or 2026/2027 rows at all.
- Baselines: league base rate (prior-seasons over-8.5 rate,
  constant within target season); naive trailing-10 through the
  same count distribution as the reference harness.
- Virgin: 2025/2026 (n = 322), read ONCE, only for dev-passing
  arms, continuing from the dev end state. Calibration = actual
  over-8.5 rate − mean P(over 8.5), SE = sd(y_i − p_i)/√n.

## GATE LEGS (verbatim, frozen)

Dev gate — pooled dev LL@8.5 beats BOTH baselines (league base rate; naive trailing-10), else arm dead, no virgin read. Virgin legs — (i) LL@8.5 ≤ Gate Zero's and ≤ best baseline's; (ii) calibration |actual − mean P(over 8.5)| ≤ 1.0pp is clean PASS; beyond 1 SE is FAIL, with SE reported, a breach within 1 SE of the 1.0pp boundary is PROVISIONAL PASS; (iii) dev per-season sign check for both-pass. Both-pass: both → lower pooled virgin LL ships; one → ships; none → FAIL.

Mechanical reading: an arm passes iff it survives the dev gate AND
passes virgin legs (i)–(ii) (PROVISIONAL counts) AND, for variants,
leg (iii) — variant dev LL@8.5 ≤ Gate Zero's in at least 2 of the 3
dev seasons. Ties → simpler arm (Gate Zero before X7). If Gate
Zero fails its dev gate, variants are moot, verdict FAIL, virgin
NOT read.

## Outputs

Engine `engine/corners/`; `results_dev.json` (+ CSV);
`results_virgin.json`; `fitted_params_virgin.json`; on PASS,
`predictions/c_eg_virgin_predictions.csv` (shipped arm; FT ladder
7.5/8.5/9.5; 1H/2H presentation-only via frozen corners constant
0.4604, lines 1H 3.5/4.5/5.5, 2H 4.5/5.5/6.5). Verdict
`reports/C_EG_VERDICT.md`.
