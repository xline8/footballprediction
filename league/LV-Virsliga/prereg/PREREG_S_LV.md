# Pre-registration — S-LV (Latvia Virsliga SOT model)

Frozen: 2026-11-10, before any fitting. Branch `build/lv-virsliga`.
Design authority: `league/LV-Virsliga/analysis/MODEL_DESIGN.md`
(S-LV); features per `analysis/FEATURES.md` (X5 adopted; X4/X6
DROPPED — no shotmap exists in this league). Reference: production
SOT v5 in `model_sot.py`; sibling analogue:
`league/RU-1Division/prereg/PREREG_S_RU1.md` — mirror its frozen
constants (joint Poisson ridge lambda = 100, HL = 365, lazy refit
7 days, total-shots ratings prior K = 8, Beta-Binomial prior
P = 200, ensemble 50/50 with naive trailing-10, NB size r = 79.94),
changing only league, windows, line and the era rule below.
Phase rule (frozen): all rows are phase `regular`; no phase
feature anywhere.
Calibration = **actual − predicted** everywhere in this build.

## Virgin-hygiene disclosure

As in PREREG_G_LV: step-1 inventory aggregates (including 2026)
are era facts; no per-match model output and no gate quantity was
computed from 2026 before this freeze. The virgin is NOT burned.

## Era rule (frozen, from the payload-verified era map)

The SOT target exists ONLY in the stats era (seasons 2025+).
Rows before 2025 do not exist for this market: never scored,
never update target state. Every stats-era row carries a stats
block (180/180 in 2025; 179/179 in 2026).

- Target: total SOT = `ShotsOnTarget_home + ShotsOnTarget_away`
  (stats feed). Primary line **9.5** (2025 dev-era over-rate
  0.444, closest to 0.5; 8.5 is 0.572). Ladder 8.5 / 9.5 / 10.5
  reported, gate at 9.5.
- Arms: **Gate Zero** (v5 unmodified); **RS** (Gate Zero with the
  BB prior raised P = 200 → 20,000).
- Walk-forward: per-match, chronological (date, match_id),
  predict-then-update, date-grouped (same-date matches never see
  each other). Warm-up: stats-era matches 2025-03-05 – 2025-04-30
  update state, never scored (47 matches).
- Dev: scored stats-era matches 2025-05-01 – 2025-11-09 (n = 133).
  The dev harness must not read 2026 rows at all.
- Baselines: league base rate (warm-up-era over-9.5 rate, constant
  within the scored window); naive trailing-10 through the same NB.
- Virgin: 2026 (n = 179), read ONCE, only for dev-passing arms,
  continuing from the dev end state (per-match walk-forward
  through the virgin, stats-era rows only).
  Calibration = actual rate − mean P(over 9.5), SE =
  sd(y_i − p_i)/√n.
- Halves: FT + 1H/2H via frozen SOT constant 0.4637 from 2025
  period splits (presentation only; true per-match share variance
  = 0).

## GATE LEGS (verbatim, frozen)

Dev gate — pooled dev LL@9.5 beats BOTH baselines (league base rate; naive trailing-10), else arm dead, no virgin read. Virgin legs — (i) LL@9.5 ≤ Gate Zero's and ≤ best baseline's; (ii) calibration |actual − mean P(over 9.5)| ≤ 1.0pp, SE reported, breach within 1 SE = PROVISIONAL PASS; (iii) dev sign check for both-pass: with a single scored dev window in this league, the variant's pooled dev LL@9.5 must be ≤ Gate Zero's. Both-pass: both → lower pooled virgin LL ships; one → ships; none → FAIL.

Mechanical reading: an arm passes iff it survives the dev gate AND
passes virgin legs (i)–(ii) (PROVISIONAL counts) AND, for variant
arms, leg (iii). Ties → simpler arm (Gate Zero before RS). If Gate
Zero fails its dev gate, variants are moot, verdict FAIL, virgin
NOT read.

## Outputs

Engine `league/LV-Virsliga/engine/sot/`; `results_dev.json`
(+ `predictions_dev.csv`); `results_virgin.json`;
`fitted_params_virgin.json`; on PASS,
`predictions/s_lv_virgin_predictions.csv` (shipped arm; FT ladder
8.5/9.5/10.5 ensemble probabilities; 1H/2H presentation via frozen
SOT constant 0.4637). Verdict `reports/S_LV_VERDICT.md`.
Production code untouched. No push. No merge.
