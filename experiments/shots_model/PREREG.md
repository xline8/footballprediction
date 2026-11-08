# Total Shots Model — Pre-Registration

Written 2026-11-08, BEFORE the test window (2023/24–2025/26) is run.
Approved by the user 2026-11-08 ("gas") after the 1xBet market mapping
work established that the bookmaker's "Shots Towards The Goal" market
is total shot attempts (on target + off target + blocked). This
document fixes the design and the gate; the gate does not move after
results are seen (project discipline, same as every prior model).

## Target and data

- Target: total shots per match (HS + AS) from `all_matches_clean.csv`
  (football-data spine; the same source family the production graders
  use — NOT API-Football, never a results source here).
- Coverage (verified 2026-11-08): HS/AS present in ~100% of matches in
  every division-season 2017/18–2026/27; top-5 test seasons complete
  (E0/D1/I1/SP1/F1: 380/306/380/380/306 per season, no gaps).
- Top-5 mean total shots: 2022/23 25.00, 2023/24 26.04, 2024/25 24.80,
  2025/26 25.16. Headline line 25.5 sits at the pooled mean.
- Evaluation scope mirrors the SOT experiments: every division in the
  spine with shot stats, walk-forward; the gate's division clause
  applies to the top-5 (production only predicts top-5 fixtures).

## Provider agreement (spine vs FotMob warehouse, measured pre-run)

Join of `data_enrichment/shot_lineup_features.csv` (FotMob totals,
7,531 usable of 7,532 top-5 matches ≥ 2022/23) to the spine on
(div, date, cleaned team names): 7,531 matched, 0 unmatched.

- Identical totals: 81.3% · |diff| ≤ 1: 95.3% · |diff| ≤ 2: 98.2% ·
  |diff| > 2: 1.8%. Mean diff (FotMob − spine) = +0.15 shots.
- O/U settlement flip purely from provider disagreement, by line:
  22.5: 1.66% · 23.5: 1.43% · 24.5: 1.69% · 25.5: 2.04% · 26.5: 1.71% ·
  27.5: 1.75% · 28.5: 1.73%.
- Reading: total-shots counting disagrees between providers MORE than
  SOT counting did (SOT flips were 0.78–1.17%). Roughly 1.4–2.0% of
  bets at these lines would settle differently depending on whose
  count the bookmaker uses. This is settlement risk on the personal
  assessment side (the standing 1-point shave logic applies), not a
  modelling error: the model trains and will be graded on one
  consistent definition (the spine's).

## Candidates (architecture mirrors SOT v5, applied to shots)

- Regression core: per-division jointly fitted log-linear Poisson
  ratings on total shots — log(mu_home) = beta_home + A[home] +
  D[away], log(mu_away) = beta_away + A[away] + D[home] — ridge
  (lam/2)·sum(A² + D²), lazy refits every 7 days of match dates on
  matches strictly before the prediction date, 365-day exponential
  sample weights, warm-started Newton/Fisher IRLS (the v5
  RegressionStore machinery, target HS/AS).
- Candidate (a): regression + Negative Binomial line probabilities,
  NB size r by method of moments from the regression model's
  walk-forward residuals over 2019/20–2022/23 (pre-test only),
  r = sum(lam²) / (sum((t − lam)²) − sum(lam)), clipped to [1, 1e6].
- Candidate (b): candidate (a) ensembled 50/50 with the naive
  trailing-10 shot means (both members' totals via the same NB).
- Ridge grid {3, 10, 30, 100, 300} — the v5 grid {1, 3, 10, 30, 100}
  scaled ~3× because per-team shot counts (~13) are ~3× SOT counts
  (~4.4), so the likelihood scale — and therefore the penalty scale
  that bites equally — is ~3× larger. Lambda tuned ONLY on 2022/23
  (line-25.5 log loss of regression+Poisson); ties toward larger lam.
- Candidate selection, on 2022/23 ONLY (line-25.5 log loss at the
  tuned lambda): candidate (b) is chosen only if it beats candidate
  (a) by ≥ 0.0005; otherwise candidate (a). The Poisson-only variant
  is scored on the tuning season for context but is not a candidate.

## Baselines (house definitions, as in the SOT base experiment)

- (a) Division base rate: decayed (HL 365d) league mean home/away shot
  rates, expectation = mu_h + mu_a, Poisson probabilities.
- (b) Naive trailing-10: each team's plain mean shots for/against over
  its last 10 matches, combined (for + opponent-against)/2 per side,
  league-mean fallback, Poisson probabilities.

## Harness

- Walk-forward, strictly chronological; every state updates only
  AFTER the match is predicted. Test seasons 2023/24, 2024/25,
  2025/26. All tuning (lambda, NB r, candidate choice) on pre-2023/24
  data only, frozen before the test pass.
- Lines: ladder 22.5–28.5; headline line 25.5.
- Reported regardless of outcome: pooled per-line log loss for
  candidate and both baselines; per-season and per-division (top-5)
  tables at 25.5; MAE; calibration at 25.5 (mean predicted Over% −
  actual Over%, in pp).

## GATE (fixed; all three must hold for the chosen candidate)

1. Pooled log loss @25.5 beats the BEST baseline by ≥ 0.001.
2. Calibration error @25.5 within ±1.0pp pooled (signed mean predicted
   Over% minus actual Over%).
3. No top-5 division's LL@25.5 worse than that division's best
   baseline by > 0.0003.

PASS → production build (Phase 2: model_shots.py + constant-share
halves + shadow wiring + new-market grading + report section).
FAIL → production stays untouched; the experiment is committed with
its honest verdict and the market remains unmodelled.

## Halves note (for Phase 2, measured pre-run)

1H share of total shots from the FotMob features file, 2022/23 only
(the pre-test season with labels; n = 1,826): **S = 0.4582**. Other
seasons for context: 2023/24 0.4606, 2024/25 0.4554, 2025/26 0.4511 —
the constant is stable. If Phase 2 runs, the halves split uses this
frozen constant (no fitted share model — the halves audit forbids
more) with per-half NB sizes estimated by method of moments from
2022/23 walk-forward split residuals.
