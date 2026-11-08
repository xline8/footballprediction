# Total Shots Model v2 — Pre-Registration (level-tracking design)

Written 2026-11-08, BEFORE any 2026/27 model number is computed.
Approved by the user 2026-11-08 ("coba jalankan rancangan baru")
after v1 failed its calibration leg. This document fixes the design
and the gate; the gate does not move after results are seen.

## Why v2 exists (v1 verdict, experiments/shots_model/RESULTS.md)

v1's chosen candidate (regression + NB + naive ensemble) beat the
best baseline's pooled log loss @25.5 by +0.0086 (gate: ≥ 0.001) and
passed the division leg, but FAILED calibration: predicted Over
40.5% vs actual 41.8% at line 25.5 (−1.34pp; gate ±1.0pp), with the
error concentrated by season (2023/24 −2.13pp, 2024/25 +0.17pp,
2025/26 −2.06pp). The v1 coordinator's note identified this as a
level/regime-tracking shortfall: shot rates shifted between seasons
and the frozen recipe (weekly refits, 365-day half-life weights)
lagged. Per project discipline, no correction may be fitted to the
v1 test window; the legitimate route is a new design whose level
handling is fixed a priori, tested once on the virgin 2026/27
season. That is this experiment.

## Candidate v2 (frozen design)

Base = the v1 winning candidate, EXACTLY as frozen by v1 tuning
(pre-2023/24 data only): per-division ridge Poisson ratings on total
shots (HS/AS) with lam = 100, negative-binomial line probabilities
with r = 79.82, ensembled 50/50 (probability average) with the naive
trailing-10 member, same regression machinery and data pipeline as
experiments/shots_model/run_shots_experiment.py. Lambda, r, and the
ensemble choice are NOT re-tuned here.

Level layer (the only new component; mechanism class fixed by the
commissioning brief: recency level adaptation, walk-forward honest,
no test-window peeking):

- For each division d, two exponentially decayed sums are kept over
  matches ALREADY PLAYED in that division: A_d = decayed sum of
  actual total shots, P_d = decayed sum of the base candidate's
  ensemble total (0.5·(lt_reg + lt_naive)) as predicted BEFORE the
  match. Decay is in days with half-life HL_L. The tracked
  prediction is the UNADJUSTED base total, so the layer measures the
  base model's current level bias and cannot chase its own output.
  State updates happen only AFTER a match is predicted, carries
  continuously across season boundaries, and starts empty.
- Shrunk ratio: R_d = (A_d + K_L·M̄) / (P_d + K_L·M̄), with the
  fixed constant M̄ = 25.0 (≈ the global mean total shots) and prior
  weight K_L in match-equivalents.
- Factor: f_d = clip(1 + s·(R_d − 1), 0.90, 1.10). Both ensemble
  member totals are multiplied by f_d before their NB probabilities
  are computed; the 50/50 probability ensemble is unchanged.
- Hyperparameter grid (the ONLY quantities tuned in v2):
  HL_L ∈ {30, 60, 120} days × s ∈ {0.5, 1.0} × K_L ∈ {20, 50} = 12
  cells. Selection metric: line-25.5 log loss of the layered
  candidate on the tuning season 2022/23 ONLY (computed in the same
  walk-forward pass; the selection function reads tuning metrics
  only). Ties break toward larger HL_L, then smaller s, then larger
  K_L (the more conservative cell). The no-layer arm (f ≡ 1, i.e.
  v1's candidate) is carried through the same pass for comparison
  but is not a selectable cell: the mechanism class is fixed.

Baselines: the v1 house definitions, unchanged, no layer —
(a) division base rate (decayed league means, Poisson),
(b) naive trailing-10 (Poisson). They receive the identical windows
and the identical walk-forward honesty.

## Harness

- Same loader/scope as v1 (`load_matches` from the SOT experiments:
  spine rows with shot labels). One chronological pass over all
  matches; every state (regression, naive tracker, ratings, layer)
  updates only after the match is predicted.
- Implementation note: predictions are computed for every match, so
  the regression's lazy 7-day refits anchor at the first match of
  the data rather than at the first test match as in v1's eval pass.
  This is a superset refit cadence (both are strictly honest); the
  no-layer arm recomputed in this pass is reported next to v1's
  published numbers as a harness check, and any small deviation from
  refit anchoring is reported, not hidden.
- Tuning: 2022/23 only (plus the layer's own trailing state, which
  by construction uses only earlier matches).

## Windows

- VERDICT (evaluated once, with the frozen design): the virgin
  2026/27 season — every labelled match in the spine as of
  2026-11-08. Counted before any model number is computed:
  **n = 2,032** matches in evaluation scope, of which top-5 = 451;
  dates 2026-07-31 → 2026-11-02. The run recounts and reports the
  actual n.
- SECONDARY (reported, NOT the verdict): 2023/24–2025/26, the same
  seasons as v1's test window. These seasons motivated the design,
  so they cannot judge it; they are reported to answer one specific
  question: does the level layer remove the per-season calibration
  drift v1 showed there (−2.13 / +0.17 / −2.06pp)?

## GATE (mirrors v1; all three on the 2026/27 verdict window)

1. Pooled log loss @25.5 beats the BEST baseline by ≥ 0.001.
2. Calibration @25.5 point estimate within ±1.0pp (signed mean
   predicted Over% minus actual Over%).
3. No top-5 division's LL@25.5 worse than that division's best
   baseline by > 0.0003.

## Honesty clause — calibration sample size (binding)

The standard error of the calibration estimate,
SE = sd(p_i − y_i)/√n at line 25.5 over the verdict window, is
computed and stated in RESULTS.md. (A priori estimate at n = 2,032
with sd(p−y) ≈ 0.49: SE ≈ 1.09pp — the measured value replaces
this.) The calibration leg counts as statistically meaningful only
if SE ≤ 0.5pp, i.e. the ±1.0pp tolerance band is at least ±2 SE
wide. Verdict mapping, fixed now:

- Any leg point-FAILS → **FAIL** (an SE never rescues a point
  failure). No production wiring.
- All legs point-PASS and SE ≤ 0.5pp → **PASS** → production wiring
  exactly as scoped in the v1 brief's Phase 2.
- All legs point-PASS but SE > 0.5pp → **PROVISIONAL PASS**, not a
  full pass. No production wiring, no cron change. A single
  confirmation re-run of this frozen design (same gate, same
  mapping except the SE bar below) is pre-committed for when the
  labelled top-5 2026/27 count reaches ≈ 1,500 (pooled-scope n then
  ≈ 6,700 on the current ratio, expected SE ≈ 0.60pp): at that run,
  all-legs point-PASS with SE ≤ 0.65pp converts to **PASS**; a
  point failure converts to **FAIL**; otherwise it stays
  PROVISIONAL and no further automatic re-run is implied.

Reported regardless of outcome: verdict-window per-line log loss
(pooled), per-division (top-5) LL and calibration @25.5, MAE,
calibration SE (pooled and, for information, top-5 only), the
frozen layer cell, and the secondary-window drift table
(v1 published vs v2 no-layer arm vs v2 layered, per season).

## Halves note (only relevant if PASS → Phase 2)

Unchanged from v1's pre-registration: frozen constant 1H share
S = 0.4582 (measured pre-run on 2022/23 FotMob labels) with per-half
NB sizes from 2022/23 walk-forward split residuals; no fitted share
model (the halves audit forbids more).
