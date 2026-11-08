# Pre-registration — C-US (US-MLS corners model)

Frozen: 2026-11-09, before any fitting. Branch `build/us-mls`.
Design authority: `league/US-MLS/analysis/MODEL_DESIGN.md` §3; features per
`league/US-MLS/analysis/FEATURES.md` (X5, X9 base; X7 arm); evidence per
`league/US-MLS/analysis/EDA.md` (F2/F9). Reference: production
`model_corners_v3.py` via the J1 engine `league/J1/engine/corners/`.

## Target and lines

- Target: total corners = `corners_home + corners_away`.
  **Primary line 9.5** (dev over-rate 0.514). Ladder 8.5 / 9.5 / 10.5. All
  gate legs use binary LL at 9.5.

## Reference architecture (all arms share)

Exactly as PREREG_C_J1: season-blocked walk-forward; for target season S,
features and ratings are built from all matches in seasons strictly before S,
with the production territorial multiplier fitted on the training window;
per-match predictions use trailing team features strictly pre-match. NB total
with the reference size fitted per the J1 engine's frozen method.

## Arms

1. **Gate Zero (GZ)** — production multiplier covariates (X9: possession +
   big-chance trailing rates), unchanged.
2. **Arm X7 (box-touch multiplier)** — GZ with the multiplier's covariates
   replaced by opp-box touches for/against (X7, F9), constructed exactly as
   C-J1's X7 arm. Coverage is approximately 39–45% in 2021–2023 and 100% in
   2024–2025; the minimum-8 trailing rule makes the arm fall back to Gate Zero
   during the ramp.

## Baselines

League base rate (prior-seasons over-9.5 rate) and naive trailing-10 through
the same NB, at the 9.5 line.

## Dev protocol

Evaluation seasons 2022, 2023, 2024 (n=1532); 2021 is warm-up only. The dev
harness must not read 2025 rows at all or any 2026 rows. Regular and playoff
matches are in every window; phase is not a filter.

## Virgin protocol

Season 2025 (n=540), read ONCE, only for dev-passing arms, after dev freezes.
Training is all matches before 2025. Calibration = mean P(over 9.5) − actual
over-rate, SE reported.

## GATE LEGS (verbatim, frozen — identical across the program)

Dev gate — pooled dev LL at the primary line beats BOTH baselines (league base rate; naive trailing-10 / climatology), else arm dead, no virgin read. Virgin legs — (i) LL ≤ Gate Zero's and ≤ best baseline's; (ii) calibration |mean P(over) − actual| ≤ 1.0pp, SE reported, breach within 1 SE = PROVISIONAL PASS; (iii) dev per-season sign check for both-pass (variant dev LL ≤ Gate Zero's in at least half the dev seasons; Gate Zero exempt). Both-pass: both → lower pooled virgin LL ships; one → ships; none → FAIL. Ties → simpler arm (Gate Zero first). If Gate Zero fails its own dev gate, the variants are moot — verdict FAIL regardless of variant dev numbers, and the virgin window is not read.

For this candidate the "primary line" in the gate text is 9.5 and LL means binary log-loss at 9.5.

## Forbidden

Half-share corner modelling (F3; presentation via frozen constant 0.464 only);
absence features; snapshot features; any covariate outside `FEATURES.md` §1.

## Outputs

- Engine: `league/US-MLS/engine/corners/`; `results_dev.json` (+ CSV),
  `results_virgin.json`, `fitted_params_virgin.json`.
- Virgin predictions: `league/US-MLS/predictions/c_us_virgin_predictions.csv`
  (shipped arm; GZ labelled if nothing ships): match_id, date, teams, actual
  total corners, exp_corners_total, FT ladder P(over 8.5/9.5/10.5), 1H/2H
  ladders presentation-only via frozen constant 0.464 with the arm's NB r
  (1H lines 3.5/4.5/5.5; 2H lines 4.5/5.5/6.5).
- Verdict: `league/US-MLS/reports/C_US_VERDICT.md`.
