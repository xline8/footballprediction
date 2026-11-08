# Pre-registration — K-NO-OBOS (NO-OBOSLigaen cards model, yellows)

Frozen: 2026-11-10, before any fitting. Branch `build/no-obos`.
Design authority: `MODEL_DESIGN.md` §4; features per `FEATURES.md`
(X5 base; X8 arm); evidence per `EDA.md` (F2/F8). Reference:
production `model_cards.py` via the NO-Eliteserien engine
`league/NO-Eliteserien/engine/cards/` (model.py copied; pattern
unchanged). The OBOS CSV carries the referee name directly
(`referee` column from Phase 2), as in NO-Eliteserien.

## Target — frozen with its reason
- Target: total yellows = `yellow_home + yellow_away`, **event-feed
  unified** (Yellow + YellowRed events per side; PREPROCESSING
  rule 7; events present for 100% of matches).
- **Why event-unified, decided from THIS league's data before
  fitting**: the stats feed carries **no yellow_cards key at all** in
  any season of this league — there is no stats target, so the
  stats-vs-events artefact comparison that other leagues ran is
  impossible here (nothing to compare). The event feed is complete
  (240/240 matches every season; 4,522 Yellow + 73 YellowRed events
  corpus-wide) and supports the unified target directly. This is not
  the TH/ZA era-flipped artefact situation and not the NO-Eliteserien
  undercount situation; it is a single-source target, frozen as such.
- **Primary line 3.5** (dev over-rate 38.65% — closer to 50% than
  2.5's 63.02%; dev mean 3.19). Ladder 2.5 / 3.5 / 4.5. All gate legs
  use binary LL at 3.5.

## Reference architecture (all arms share)
Exactly as PREREG_K_NO's harness: per-match online walk-forward
(predict-then-update), team card ratings with the production decay/
shrinkage pattern, NB count distribution with the engine's fitted r,
ensemble with the naive trailing-10 as in the J1 cards engine.

## Arms
1. **Gate Zero (GZ)** — reference pattern, no referee.
2. **Arm X8 (referee covariate)** — GZ plus the referee strictness
   covariate (X8, F8 r=0.715, second seed stream 0.723 — the
   program's strongest referee reading), constructed exactly as
   K-J1's X8 arm (trailing referee mean of unified yellows within
   this league, shrunk toward the league mean with the J1 engine's
   frozen shrinkage; referees with <8 prior in-league matches take
   the shrunk league mean). A fixture whose CSV referee is missing
   falls back to the Gate Zero prediction for that match (no
   imputation). Coverage is reported per season in the results
   (virgin: 229/240 = 95.4%; 2021 has no named referees at all and
   is warm-up only).

## Baselines
League base rate (prior-seasons over-3.5 rate) and naive trailing-10
through the same NB — as the J1 cards harness computes them, at the
3.5 line.

## Dev protocol
Warm-up 2021 (updates state, never scored); scored dev 2022–2025
(n=960). Dev harness must not read 2026 rows.

## Virgin protocol
Season 2026 (complete regular season, n=240), read ONCE, only for
dev-passing arms, online walk-forward continuing from the dev end
state. Calibration = mean P(over 3.5) − actual over-rate, SE
reported.

## GATE LEGS (verbatim, frozen — identical across the program)

Dev gate — pooled dev LL at the primary line beats BOTH baselines (league base rate; naive trailing-10 / climatology), else arm dead, no virgin read. Virgin legs — (i) LL ≤ Gate Zero's and ≤ best baseline's; (ii) calibration |mean P(over) − actual| ≤ 1.0pp, SE reported, breach within 1 SE = PROVISIONAL PASS; (iii) dev per-season sign check for both-pass (variant dev LL ≤ Gate Zero's in at least half the dev seasons; Gate Zero exempt). Both-pass: both → lower pooled virgin LL ships; one → ships; none → FAIL. Ties → simpler arm (Gate Zero first). If Gate Zero fails its own dev gate, the variants are moot — verdict FAIL regardless of variant dev numbers, and the virgin window is not read.

## Operational condition (as K-J1)
Referee assignment must be known at prediction time in the live
pipeline; warehouse records are post-match snapshots and cannot prove
pre-match publication. The no-imputation fallback above is the
operating rule regardless of the verdict.

## Forbidden
Red-card target modelling (R12); halves modelling (presentation via
frozen constant 0.306 only — measured from event times, the only
half-split source in this league; see EDA F3); absence features;
snapshot features; any target other than the event-unified yellows
above.

## Outputs
- Engine: `league/NO-OBOSLigaen/engine/cards/`; `results_dev.json`
  (+ CSV), `results_virgin.json`, `fitted_params_virgin.json`.
- Virgin predictions: `league/NO-OBOSLigaen/predictions/k_no_obos_virgin_predictions.csv`
  (shipped arm; GZ labelled if nothing ships): match_id, date, teams,
  actual total yellows, exp_yellows_total, referee, FT ladder P(over
  2.5/3.5/4.5), 1H/2H ladders presentation-only via frozen constant
  0.306 with the arm's NB r (1H lines 0.5/1.5/2.5; 2H lines
  1.5/2.5/3.5).
- Verdict: `league/NO-OBOSLigaen/reports/K_NO_OBOS_VERDICT.md`.
