# Total Shots v2 — Prospective Test Pre-Registration (Branch A)

Written and committed 2026-11-08, BEFORE any match in the scored
window has been played or scored. Matches accumulate daily, which
is why this freeze happens now. The gate does not move after
results are seen.

## Basis

v2 (PREREG.md / RESULTS.md, commit 92fe654) failed its virgin
2026/27 window on calibration (−6.04pp pooled; top-5 −6.76pp) and
the division leg. The history-only diagnostic
(`DIAGNOSTIC_PHASE.md`, commit 38f4cf9) established:

1. There is **no consistent early-season phase elevation** in
   total shots (first-90-days ratios ≈ 1.005 / 1.001 / 0.997 over
   2017/18–2025/26) — a phase pattern cannot explain, and must not
   be fitted to, 2026/27. (This is why Branch B of the
   commissioning brief — v2 + a season-phase curve — is NOT
   frozen: its premise is absent from the data.)
2. 2026/27's start is a **record level shift**: early top-5 mean
   27.98 vs a historical norm of 24.63 (**+3.35**; phase-adjusted
   +3.09 vs a historical range of [−2.28, +0.96]), broad across
   all five divisions, corroborated independently by FotMob
   counts (agreement profile unchanged vs prior seasons —
   artefact ruled out).
3. Early level deviations **historically persist** within the
   season (OLS slope 0.78, r = 0.82 over 9 seasons; hot starts
   retain ~76% of their deviation in the rest of the season).

The v2 design's level layer was tuned on ≤2022/23 and had only the
first ~11 rounds of the shift to chase, with a ±10% clip. The open
question this test answers — and the only one it answers — is
whether the **identical frozen design**, given a full run of
post-shift football with its layer state carried on the shift
itself, calibrates acceptably on matches played after this
freeze. It does not re-litigate the virgin window, and it does
not judge whether 2026/27 is a multi-season regime change.

## Candidate (frozen, byte-identical)

The v2 candidate EXACTLY as committed in **92fe654**:
`run_shots_experiment_v2.py`'s prediction machinery — base = v1's
frozen winner (per-division ridge Poisson ratings on total shots,
lam = 100; NB r = 79.82; 50/50 probability ensemble with the naive
trailing-10 member) plus the level layer at its frozen cell
(HL = 60 days, s = 0.5, K = 20, M̄ = 25.0, factor clip
[0.90, 1.10]).

- **No parameter may change.** No re-tuning of anything, on any
  data, at any point before the verdict.
- The prediction code path must remain byte-identical to 92fe654.
  Evaluation-window filtering (below) is applied outside the
  model code. Any change to the prediction code after this commit
  voids the test; a voided test may only be replaced by a new
  pre-registration, never by a quiet edit.
- Baselines: the v1 house definitions, unchanged, no layer —
  (a) division base rate (decayed league means, Poisson),
  (b) naive trailing-10 (Poisson) — identical window and
  walk-forward honesty.

## Harness / state honesty

One chronological pass over all labelled spine matches from the
same data start as v2's pass. Every state (regression, naive
trackers, ratings, level layer) updates only after a match is
predicted, on **every** played match — including non-top-5 matches
and matches played before 2026-11-09 — exactly as in v2's harness.
Matches played 2026-11-03 → 2026-11-08 (after the virgin window
closed, before this scored window opens) are state-only: they
inform the layer and ratings but are **not scored**. Only scoring
is restricted to the prospective window.

## Scored window (evaluated ONCE, at the verdict point)

- Divisions: top-5 only (E0, D1, I1, SP1, F1).
- Matches: spine rows with Date ≥ **2026-11-09** and HS/AS
  present, as labelled in `all_matches_clean.csv` at the verdict
  run.
- **No interim peeking:** gate metrics must not be computed on
  this window before the verdict point. (Descriptive data-quality
  checks that do not touch model outputs are not peeking.)

## Verdict point

The single evaluation runs when the scored-window count reaches
**n ≥ 1,200** top-5 matches **or** the 2026/27 season ends (last
top-5 matchday), whichever comes first. On the remaining fixture
volume (≈ 1,300 top-5 matches after 2026-11-08) the two triggers
nearly coincide, around late April / May 2027.

## GATE (identical to v2's three legs, on the scored window)

1. Pooled log loss @25.5 beats the BEST baseline by ≥ 0.001.
2. Calibration @25.5 point estimate within ±1.0pp (signed mean
   predicted Over% minus actual Over%).
3. No top-5 division's LL@25.5 worse than that division's best
   baseline by > 0.0003.

## Honesty clause — calibration sample size (binding; mirrors v2)

SE = sd(p_i − y_i)/√n at line 25.5 over the scored window is
computed and stated at the verdict. A priori, at n ≈ 1,200 with
sd(p−y) ≈ 0.49, SE ≈ 1.4pp — so the calibration leg will not be
"statistically meaningful" (SE ≤ 0.5pp) inside 2026/27, and a
strict-mapping full PASS is unlikely this season even if every
leg point-passes. The mapping is kept unchanged regardless:

- Any leg point-FAILS → **FAIL**. No production wiring, no cron
  change; this market remains unmodelled, and the v2 design is
  not re-tested again on later data without a new user decision.
- All legs point-PASS and SE ≤ 0.5pp → **PASS** → production
  wiring exactly as scoped in the v1 brief's Phase 2
  (model_shots.py + frozen-constant halves split + non-critical
  shadow step + run-status registry + archive files +
  grade_new_markets shots_total extension with the main ledger
  byte-identical + unit tests + full suite/test_core + shadow run
  + cron "Total Tembakan :" block section, verified by read-back).
- All legs point-PASS but SE > 0.5pp → **PROVISIONAL PASS**. No
  production wiring, no cron change. A single confirmation is
  pre-committed: the identical frozen design keeps accumulating
  (2027/28 top-5 matches join the same scored scope) and is
  re-judged ONCE when the cumulative prospective top-5 SE
  ≤ 0.65pp (a priori n ≈ 5,700 at sd ≈ 0.49) or at the end of
  2027/28, whichever comes first. At that run: all-legs
  point-PASS with SE ≤ 0.65pp → **PASS**; a point failure →
  **FAIL**; otherwise it stays PROVISIONAL and no further
  automatic re-run is implied.

Reported regardless of outcome: scored-window n and date range,
per-line pooled log loss, per-division (top-5) LL and calibration
@25.5, MAE, calibration SE, the frozen layer cell, and the verdict
under the mapping above.

## Status at freeze

- The prospective test is **NOT run now** — its window has not
  accumulated. This document only freezes it.
- Production code and the daily-report cron are untouched by
  this pre-registration.
