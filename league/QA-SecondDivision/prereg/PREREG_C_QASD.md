# Pre-registration — C-QASD (QA-SecondDivision corners model)

Frozen: 2026-11-10, before any fitting. Branch `build/qa-seconddiv`.
Design authority: `analysis/MODEL_DESIGN.md` (C-QASD); features X5,
X9; evidence F1/F2/F3/F5/F7. Reference: production
`model_corners_v3.py`; SA analogue `PREREG_C_SAFD.md` — its shared
engine is carried over verbatim in form (HL = 270 base rates,
rolling-5 relative factors clamped [0.6, 1.7], core mean `mu_cs`,
NB pmf grid 0..50, gamma grid (0.0, 0.15, 0.3, 0.45, 0.6, 0.8),
r clamped [1.02, 5.0], territorial multiplier clamped [0.70, 1.43],
min-8 of last-10 validity rule, date-grouped predict-then-update
state). Engine port: `league/SCO-Premiership/engine/corners/` (and
`league/SA-ProLeague/engine/corners/`). Phase rule (frozen): single
phase `regular` throughout; only played rows are used. Calibration is
defined as **actual − predicted** everywhere.

- Target: total corners (stats feed). Primary line **9.5** (dev
  over-rate 0.464, closest to 0.5; 8.5 is 0.661 — the pick is
  mechanical). Ladder 8.5 / 9.5 / 10.5 reported, gate at 9.5.
- Arms: **Gate Zero (X9)** — production covariates `BallPossesion`
  + `big_chance`, beta grids exactly as PREREG_C_J1 (poss ∈
  ±{0, .0025, .005, .0075, .010}, bc ∈ ±{0, .025, .05, .075, .10}).
  **No X7 arm**: X7 is dropped — `touches_opp_box` does not exist in
  this feed (FEATURES.md). The `big_chance` covariate is degenerate
  (0/0 in every match) and is carried as a zero column so Gate Zero
  stays the unmodified production pattern; the engine records this
  rather than silently dropping it.
- Walk-forward: per-match, chronological (date, match_id),
  predict-then-update, date-grouped. Warm-up: first 28 matches of
  2025/2026 in (date, match_id) order (rounds 1–7, never scored);
  scored: the remaining **28 matches** (rounds 8–14). Fit history for
  scored matches is all stats matches strictly before each scored
  date — including the 2024/2025 stats-era rounds 6–14 (38 matches).
  The dev harness must not read 2026/2027 rows at all.
- Parameter fitting (adaptation of the port, frozen here because the
  stats era is short): the per-season gamma/beta/r fit uses the
  expanding walk-forward history strictly before each scored date,
  seeded by the warm-up block for the first fits — never any
  stat-less 2024/2025 round 1–5 row and never the virgin.
- Dev: scored block n = 28. Small-n note as in PREREG_S_QASD.
- Baselines: league base rate (NB from the decay-weighted expanding
  history before each scored date, as PREREG_C_J1) and naive
  trailing-10 (X5) through the same per-date NB size.
- Virgin: 2026/2027 partial (n = 29, rounds 1–6, TRANSITIONAL),
  read ONCE, only for dev-passing arms. Calibration at 9.5 with
  SE = sd(y_i − p_i)/√n. Small-n note as in PREREG_S_QASD: at n = 29
  the calibration SE is ≈9pp; the gate is applied mechanically
  regardless, and the verdict records the virgin as TRANSITIONAL
  with a confirmatory read at season end.

## GATE LEGS (verbatim, frozen)

Dev gate — pooled dev LL@9.5 beats BOTH baselines (league base rate; naive trailing-10), else arm dead, no virgin read. Virgin legs — (i) LL@9.5 ≤ Gate Zero's and ≤ best baseline's; (ii) calibration |actual − mean P(over 9.5)| ≤ 1.0pp, SE reported, breach within 1 SE = PROVISIONAL PASS; (iii) dev sign check for both-pass. Both-pass: both → lower pooled virgin LL ships; one → ships; none → FAIL.

Mechanical reading as in PREREG_S_QASD (Gate Zero only, so (iii) is
vacuous; Gate Zero dev failure ⇒ FAIL, virgin NOT read).

## Outputs

Engine `engine/corners/`; `results_dev.json` (+ CSV);
`results_virgin.json`; `fitted_params_virgin.json`; on PASS,
`predictions/c_qasd_virgin_predictions.csv` (FT ladder 8.5/9.5/10.5;
1H/2H presentation-only via frozen corners constant 0.4495). Verdict
`reports/C_QASD_VERDICT.md`.
