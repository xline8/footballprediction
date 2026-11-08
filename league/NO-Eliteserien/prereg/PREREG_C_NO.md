# Pre-registration — C-NO (NO-Eliteserien corners model)

Frozen: 2026-11-09, before any fitting. Branch `build/no-eliteserien`.
Design authority: `MODEL_DESIGN.md` §3; features per `FEATURES.md`
(X5, X9 base; X7 arm); evidence per `EDA.md` (F2/F9). Reference:
production `model_corners_v3.py` via the J1 engine
`league/J1/engine/corners/` (core.py copied; pattern unchanged except
the primary-line retarget below — the AU-ALeague precedent, whose
corners primary was also 10.5).

## Target and lines
- Target: total corners = `corners_home + corners_away`.
  **Primary line 10.5** (dev over-rate 48.3% — the ladder line
  closest to 50%; dev mean 10.55). Ladder 9.5 / 10.5 / 11.5.
  All gate legs use binary LL at 10.5. The reference's internal
  fit-loss line is retargeted 9.5 → 10.5, as in AU; nothing else in
  the pattern changes.

## Reference architecture (all arms share)
Exactly as PREREG_C_J1: season-blocked walk-forward — for target
season S, features and ratings are built from all matches in seasons
strictly before S (expanding), with the production territorial
multiplier fitted on the training window; per-match predictions for
S use trailing team features computed strictly pre-match within the
harness's feature builder (as the J1 engine does). NB total with the
reference size fitted per the J1 engine's frozen method.

## Arms
1. **Gate Zero (GZ)** — production multiplier covariates (X9:
   possession + big-chance trailing rates), unchanged.
2. **Arm X7 (box-touch multiplier)** — GZ with the multiplier's
   covariates replaced by opp-box touches for/against (X7, F9),
   constructed exactly as C-J1's X7 arm (trailing means, min 8 window
   matches with the stat else that team's covariate falls back to
   the Gate Zero value — the pre-2024 coverage ramp is absorbed
   by this rule, never by imputation).

## Baselines
League base rate (prior-seasons over-10.5 rate) and naive trailing-10
through the same NB — as the J1 corners harness computes them.

## Dev protocol
Evaluation seasons 2022, 2023, 2024 (n=720); 2021 is training only.
Dev harness must not read 2025 or 2026 rows.

## Virgin protocol
Season 2025 (complete, n=240), read ONCE, only for dev-passing arms,
after dev freezes. Training = all matches before 2025.
Calibration = mean P(over 10.5) − actual over-rate, SE reported.

## GATE LEGS (verbatim, frozen — identical across the program)

Dev gate — pooled dev LL at the primary line beats BOTH baselines (league base rate; naive trailing-10 / climatology), else arm dead, no virgin read. Virgin legs — (i) LL ≤ Gate Zero's and ≤ best baseline's; (ii) calibration |mean P(over) − actual| ≤ 1.0pp, SE reported, breach within 1 SE = PROVISIONAL PASS; (iii) dev per-season sign check for both-pass (variant dev LL ≤ Gate Zero's in at least half the dev seasons; Gate Zero exempt). Both-pass: both → lower pooled virgin LL ships; one → ships; none → FAIL. Ties → simpler arm (Gate Zero first). If Gate Zero fails its own dev gate, the variants are moot — verdict FAIL regardless of variant dev numbers, and the virgin window is not read.

For this candidate the "primary line" in the gate text is 10.5 and
LL means the binary log-loss at 10.5 (the AT/AU reading with their
league's line substituted).

## Forbidden
Half-share corner modelling (F3; presentation via frozen constant
0.473 only); absence features; snapshot features; any covariate
outside FEATURES.md §1.

## Outputs
- Engine: `league/NO-Eliteserien/engine/corners/`; `results_dev.json`
  (+ CSV), `results_virgin.json`, `fitted_params_virgin.json`.
- Virgin predictions: `league/NO-Eliteserien/predictions/c_no_virgin_predictions.csv`
  (shipped arm; GZ labelled if nothing ships): match_id, date, teams,
  actual total corners, exp_corners_total, FT ladder P(over
  9.5/10.5/11.5), 1H/2H ladders presentation-only via frozen constant
  0.473 with the arm's NB r (1H lines 3.5/4.5/5.5; 2H lines 4.5/5.5/6.5).
- Verdict: `league/NO-Eliteserien/reports/C_NO_VERDICT.md`.
