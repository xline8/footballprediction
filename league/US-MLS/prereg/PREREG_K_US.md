# Pre-registration — K-US (US-MLS cards model, unified yellows)

Frozen: 2026-11-09, before any fitting. Branch `build/us-mls`.
Design authority: `league/US-MLS/analysis/MODEL_DESIGN.md` §4; features per
`league/US-MLS/analysis/FEATURES.md` (X5 base; X8 arm); evidence per
`league/US-MLS/analysis/EDA.md` (F2/F8). Reference: production `model_cards.py`
via the J1 engine `league/J1/engine/cards/`.

## Target and lines

- Target: total unified yellows = `yellow_home + yellow_away` (stats feed,
  100% coverage). **Primary line 4.5** (dev over-rate 0.402). Ladder 3.5 /
  4.5 / 5.5. All gate legs use binary LL at 4.5.

## Reference architecture (all arms share)

Exactly as PREREG_K_J1's harness: per-match online walk-forward
(predict-then-update), team card ratings with the production decay/shrinkage
pattern, NB count distribution with the engine's fitted r, and ensemble with
the naive trailing-10 as in the J1 cards engine.

## Arms

1. **Gate Zero (GZ)** — reference pattern, no referee.
2. **Arm X8 (referee covariate)** — GZ plus the referee strictness covariate
   (X8, F8 r=0.634), constructed exactly as K-J1's X8 arm: trailing referee
   mean of unified yellows within this league, shrunk toward the league mean
   with the engine's frozen shrinkage; referees with <8 prior in-league
   matches take the shrunk league mean. A fixture whose referee is missing
   falls back to Gate Zero, with no imputation. Coverage is 0% in 2021
   (warm-up only), 97.3%/99.0%/96.2% in dev 2022–2024, and 96.1% in virgin
   2025. Target unified yellows have 100% coverage in modelled seasons.

## Baselines

League base rate (prior-seasons over-4.5 rate) and naive trailing-10 through
the same NB, at the 4.5 line.

## Dev protocol

Warm-up 2021 (referee coverage 0%, never scored); scored dev 2022, 2023, 2024
(n=1532). The dev harness must not read 2025 rows at all or any 2026 rows.

## Virgin protocol

Season 2025 (n=540), read ONCE, only for dev-passing arms, online walk-forward
continuing from the dev end state. Calibration = mean P(over 4.5) − actual
over-rate, SE reported.

## GATE LEGS (verbatim, frozen — identical across the program)

Dev gate — pooled dev LL at the primary line beats BOTH baselines (league base rate; naive trailing-10 / climatology), else arm dead, no virgin read. Virgin legs — (i) LL ≤ Gate Zero's and ≤ best baseline's; (ii) calibration |mean P(over) − actual| ≤ 1.0pp, SE reported, breach within 1 SE = PROVISIONAL PASS; (iii) dev per-season sign check for both-pass (variant dev LL ≤ Gate Zero's in at least half the dev seasons; Gate Zero exempt). Both-pass: both → lower pooled virgin LL ships; one → ships; none → FAIL. Ties → simpler arm (Gate Zero first). If Gate Zero fails its own dev gate, the variants are moot — verdict FAIL regardless of variant dev numbers, and the virgin window is not read.

For this candidate the "primary line" in the gate text is 4.5 and LL means binary log-loss at 4.5.

## Operational condition

Referee assignment must be known at prediction time in the live pipeline;
warehouse records are post-match snapshots and cannot prove pre-match
publication. The no-imputation fallback above is the operating rule regardless
of the verdict.

## Forbidden

Red-card target modelling (R12); halves modelling (presentation via frozen
constant 0.341 only); absence features; snapshot features.

## Outputs

- Engine: `league/US-MLS/engine/cards/`; `results_dev.json` (+ CSV),
  `results_virgin.json`, `fitted_params_virgin.json`.
- Virgin predictions: `league/US-MLS/predictions/k_us_virgin_predictions.csv`
  (shipped arm; GZ labelled if nothing ships): match_id, date, teams, actual
  total unified yellows, exp_yellows_total, referee, FT ladder P(over
  3.5/4.5/5.5), 1H/2H ladders presentation-only via frozen constant 0.341
  with the arm's NB r (1H lines 0.5/1.5/2.5; 2H lines 1.5/2.5/3.5).
- Verdict: `league/US-MLS/reports/K_US_VERDICT.md`.
