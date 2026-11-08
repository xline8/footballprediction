# Pre-registration — C-SAFD (SA-FirstDivision corners model)

Frozen: 2026-11-10, before any fitting. Branch `build/sa-firstdiv`.
Design authority: `analysis/MODEL_DESIGN.md` (C-SAFD); features X5,
X7, X9; evidence F1/F2/F5. Reference: production
`model_corners_v3.py`; SA analogue `PREREG_C_SA.md` — its shared
engine is carried over verbatim in form (HL = 270 base rates,
rolling-5 relative factors clamped [0.6, 1.7], core mean `mu_cs`,
NB pmf grid 0..50, gamma grid (0.0, 0.15, 0.3, 0.45, 0.6, 0.8),
r clamped [1.02, 5.0], territorial multiplier clamped [0.70, 1.43],
min-8 of last-10 validity rule, date-grouped predict-then-update
state). Engine port: `league/SCO-Premiership/engine/corners/` (and
`league/SA-ProLeague/engine/corners/`). Phase rule (frozen):
promotion playoffs and awarded matches are **excluded from every
fit and every scored window**; only regular played rows are used.
Calibration is defined as **actual − predicted** everywhere.

- Target: total corners (stats feed). Primary line **9.5** (dev
  over-rate 0.434, closest to 0.5; 8.5 is 0.569 — the pick is
  mechanical, |0.434−0.5| = 0.066 < 0.069). Ladder 8.5 / 9.5 / 10.5
  reported, gate at 9.5.
- Arms: **Gate Zero (X9)** — production covariates `BallPossesion`
  + `big_chance`, beta grids exactly as PREREG_C_J1 (poss ∈
  ±{0, .0025, .005, .0075, .010}, bc ∈ ±{0, .025, .05, .075, .10});
  **X7** — covariates replaced by `touches_opp_box` for/against,
  beta_bt ∈ ±{0, .01, .02, .03, .04}.
- Walk-forward: per-match, chronological (date, match_id),
  predict-then-update, date-grouped. Warm-up: first 90 regular
  played matches of 2025/2026 (never scored); scored: the remaining
  **214 matches**. The 2024/2025 season contributes no corners
  history (score-only) and is not read by this harness at all.
- Parameter fitting (adaptation of the port, frozen here because no
  prior season with the target exists): the per-season gamma/beta/r
  fit uses the expanding walk-forward history strictly before each
  scored date, seeded by the warm-up block for the first fits — never
  any 2024/2025 row and never the virgin.
- Dev: scored block n = 214. The dev harness must not read
  2026/2027 rows at all.
- Baselines: league base rate (NB from the decay-weighted expanding
  history before each scored date, as PREREG_C_J1) and naive
  trailing-10 (X5) through the same per-date NB size.
- Virgin: 2026/2027 partial (n = 94, rounds 1–11, TRANSITIONAL),
  read ONCE, only for dev-passing arms. Calibration at 9.5 with
  SE = sd(p_i − y_i)/√n. Small-n note as in PREREG_S_SAFD: at n = 94
  the calibration SE is ≈5pp; the gate is applied mechanically
  regardless, and the verdict records the virgin as TRANSITIONAL
  with a confirmatory read at season end.

## GATE LEGS (verbatim, frozen)

Dev gate — pooled dev LL@9.5 beats BOTH baselines (league base rate; naive trailing-10), else arm dead, no virgin read. Virgin legs — (i) LL@9.5 ≤ Gate Zero's and ≤ best baseline's; (ii) calibration |mean P(over 9.5) − actual| ≤ 1.0pp, SE reported, breach within 1 SE = PROVISIONAL PASS; (iii) dev sign check for both-pass. Both-pass: both → lower pooled virgin LL ships; one → ships; none → FAIL.

Mechanical reading as in PREREG_S_SAFD (variant sign check: pooled
dev LL@9.5 ≤ Gate Zero's pooled dev LL@9.5; ties → Gate Zero;
Gate Zero dev failure ⇒ FAIL, virgin NOT read).

## Outputs

Engine `engine/corners/`; `results_dev.json` (+ CSV);
`results_virgin.json`; `fitted_params_virgin.json`; on PASS,
`predictions/c_safd_virgin_predictions.csv` (FT ladder 8.5/9.5/10.5;
1H/2H presentation-only via frozen corners constant 0.4678 with the
fitted NB r, lines 1H 3.5/4.5/5.5, 2H 4.5/5.5/6.5). Verdict
`reports/C_SAFD_VERDICT.md`.
