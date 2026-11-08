# Pre-registration — K-NO (NO-Eliteserien cards model, yellows)

Frozen: 2026-11-09, before any fitting **on the corrected target**.
Branch `build/no-eliteserien`.
Design authority: `MODEL_DESIGN.md` §4 (as amended); features per
`FEATURES.md` (X5 base; X8 arm, as amended); evidence per `EDA.md`
(F2/F8). Reference: production `model_cards.py` via the J1 engine
`league/J1/engine/cards/` (model.py copied; pattern unchanged), with
ONE documented data difference carried from AT: the NO CSV carries
the referee name directly (`referee` column from Phase 2), so no
separate warehouse referee table is built.

## AMENDMENT (2026-11-09, before any virgin read, before any fitting on the corrected target)

The first frozen version of this prereg (commit 48330b5) specified a
**single Gate Zero arm** and a **stats-feed target**, on two
measurements taken from the stats-feed yellows: dev mean 3.01 and a
referee-trait split-half r = 0.291 (below the program's 0.3 line, so
X8 was dropped — the AU single-arm precedent). A per-match feed audit
run afterwards (Phase 1 §3.5) proved the stats feed **undercounts
yellows in every season of this league** (corpus 4,353 vs 4,625
event-feed yellows; 171/1,407 matches disagree, 156 stats-low, worst
in 2025 at −6.5%). On the corrected event-unified target the
measurements that drove the design change: dev mean 3.14, referee
trait r = **0.316** (canonical EDA stream; 0.348 on an independent
second stream) — above the line, so the template's rule for a passing
trait applies and X8 is restored as an arm. The decision was taken on
the feed-integrity numbers, computed before the discarded run's
results were reviewed. **The one stats-target dev run produced in
the meantime (single-arm Gate Zero) is discarded in full**; nothing
from it is used anywhere, and the virgin window has never been read
by any version of this candidate. This mirrors the BR/AR feed-artefact
corrections, which were likewise made before their virgin reads.
Everything below is the amended, operative prereg.

## Target and lines
- Target: total yellows = `yellow_home + yellow_away`, **event-feed
  unified** (Yellow + YellowRed events per side; Phase 2 rule 7 as
  amended; events present for 100% of matches). **Primary line 2.5**
  (dev over-rate 62.2% on the corrected target — the ladder line
  closest to 50%; the next line, 3.5, sits at 36.8%. J1's primary was
  also 2.5.) Ladder 1.5 / 2.5 / 3.5. All gate legs use binary LL
  at 2.5.

## Reference architecture (all arms share)
Exactly as PREREG_K_J1's harness: per-match online walk-forward
(predict-then-update), team card ratings with the production decay/
shrinkage pattern, NB count distribution with the engine's fitted r,
ensemble with the naive trailing-10 as in the J1 cards engine.

## Arms
1. **Gate Zero (GZ)** — reference pattern, no referee.
2. **Arm X8 (referee covariate)** — GZ plus the referee strictness
   covariate (X8, F8 r=0.316 on the corrected target), constructed
   exactly as K-J1's X8 arm (trailing referee mean of unified yellows
   within this league, shrunk toward the league mean with the J1
   engine's frozen shrinkage; referees with <8 prior in-league
   matches take the shrunk league mean). A fixture whose CSV referee
   is missing falls back to the Gate Zero prediction for that match
   (no imputation). Coverage is reported per season in the results
   (virgin: 100%).

## Baselines
League base rate (prior-seasons over-2.5 rate) and naive trailing-10
through the same NB — as the J1 cards harness computes them, at the
2.5 line.

## Dev protocol
Warm-up 2021 (updates state, never scored); scored dev 2022–2024
(n=720). Dev harness must not read 2025 or 2026 rows.

## Virgin protocol
Season 2025 (complete, n=240), read ONCE, only for dev-passing arms,
online walk-forward continuing from the dev end state. Calibration =
mean P(over 2.5) − actual over-rate, SE reported.

## GATE LEGS (verbatim, frozen — identical across the program)

Dev gate — pooled dev LL at the primary line beats BOTH baselines (league base rate; naive trailing-10 / climatology), else arm dead, no virgin read. Virgin legs — (i) LL ≤ Gate Zero's and ≤ best baseline's; (ii) calibration |mean P(over) − actual| ≤ 1.0pp, SE reported, breach within 1 SE = PROVISIONAL PASS; (iii) dev per-season sign check for both-pass (variant dev LL ≤ Gate Zero's in at least half the dev seasons; Gate Zero exempt). Both-pass: both → lower pooled virgin LL ships; one → ships; none → FAIL. Ties → simpler arm (Gate Zero first). If Gate Zero fails its own dev gate, the variants are moot — verdict FAIL regardless of variant dev numbers, and the virgin window is not read.

## Operational condition (as K-J1)
Referee assignment must be known at prediction time in the live
pipeline; warehouse records are post-match snapshots and cannot prove
pre-match publication. The no-imputation fallback above is the
operating rule regardless of the verdict.

## Forbidden
Red-card target modelling (R12); halves modelling (presentation via
frozen constant 0.317 only — the constant is measured within the
stats feed's period splits, the only half-split source, as a
within-feed ratio; see EDA F3); absence features; snapshot features;
any target other than the event-unified yellows above.

## Outputs
- Engine: `league/NO-Eliteserien/engine/cards/`; `results_dev.json`
  (+ CSV), `results_virgin.json`, `fitted_params_virgin.json`.
- Virgin predictions: `league/NO-Eliteserien/predictions/k_no_virgin_predictions.csv`
  (shipped arm; GZ labelled if nothing ships): match_id, date, teams,
  actual total yellows, exp_yellows_total, referee, FT ladder P(over
  1.5/2.5/3.5), 1H/2H ladders presentation-only via frozen constant
  0.317 with the arm's NB r (1H lines 0.5/1.5/2.5; 2H lines 1.5/2.5/3.5).
- Verdict: `league/NO-Eliteserien/reports/K_NO_VERDICT.md`.
