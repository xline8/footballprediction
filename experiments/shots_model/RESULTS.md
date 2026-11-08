# Total Shots Model — Experiment Results

Script: `run_shots_experiment.py`. Design and gate: `PREREG.md` (committed before this run). Target: total shots per match (HS + AS), walk-forward test seasons 2023/24–2025/26, headline line 25.5.

Evaluated matches: 21,461

## Frozen choices (pre-2023/24 data only)

- Ridge lambda (2022/23 line-25.5 log loss, regression+Poisson): lam=3: 0.6268, lam=10: 0.6252, lam=30: 0.6232, lam=100: 0.6213, lam=300: 0.6219 → chosen **lam = 100**.
- NB size: **r = 79.82** from 28,176 regression walk-forward residuals (2019/20–2022/23; mean predicted total 23.28, residual variance / mean ratio 1.296 — Poisson would be 1.000).
- Candidate selection on 2022/23 (LL@25.5): A reg+Poisson 0.6213 · B reg+NB 0.6180 · C B+ensemble 0.6122 → chosen **(b) regression + NB + naive ensemble** (ensemble requires a ≥ 0.0005 win on tuning).

## Headline — pooled, line 25.5

| Method | LogLoss | Brier | Pred Over% | Actual Over% | Calib (pp, signed) | MAE |
|---|---|---|---|---|---|---|
| Candidate (chosen on tuning) | 0.6263 | 0.2195 | 40.5 | 41.8 | -1.34 | 4.49 |
| Baseline (a) division base rate | 0.6511 | 0.2306 | 38.9 | 41.8 | -2.96 | 4.63 |
| Baseline (b) naive trailing-10 | 0.6350 | 0.2230 | 41.3 | 41.8 | -0.51 | 4.51 |

## All lines — pooled log loss

| Method | 22.5 | 23.5 | 24.5 | 25.5 | 26.5 | 27.5 | 28.5 |
|---|---|---|---|---|---|---|---|
| Candidate (chosen on tuning) | 0.6108 | 0.6323 | 0.6360 | 0.6263 | 0.6005 | 0.5626 | 0.5157 |
| Baseline (a) division base rate | 0.6326 | 0.6555 | 0.6612 | 0.6511 | 0.6272 | 0.5885 | 0.5414 |
| Baseline (b) naive trailing-10 | 0.6192 | 0.6409 | 0.6448 | 0.6350 | 0.6095 | 0.5723 | 0.5256 |

## By season — line 25.5 log loss

| Season | n | Candidate | Base (a) | Base (b) | Candidate calib (pp) | Candidate MAE |
|---|---|---|---|---|---|---|
| 2023/24 | 7,245 | 0.6285 | 0.6582 | 0.6369 | -2.13 | 4.50 |
| 2024/25 | 7,122 | 0.6187 | 0.6382 | 0.6291 | +0.17 | 4.52 |
| 2025/26 | 7,094 | 0.6318 | 0.6569 | 0.6390 | -2.06 | 4.44 |

## By division (top-5) — line 25.5 log loss

| Div | n | Candidate | Best baseline | Δ (cand − best base) |
|---|---|---|---|---|
| E0 | 1,140 | 0.6691 | 0.6776 | -0.0084 |
| D1 | 917 | 0.6809 | 0.6916 | -0.0107 |
| I1 | 1,140 | 0.6665 | 0.6792 | -0.0127 |
| SP1 | 1,140 | 0.6368 | 0.6501 | -0.0133 |
| F1 | 918 | 0.6666 | 0.6760 | -0.0094 |

## Gate verdict (PREREG.md, fixed before the run)

1. Pooled LL@25.5 beats best baseline by ≥ 0.001: margin +0.0086 → **PASS**.
2. Calibration @25.5 within ±1.0pp: -1.34pp → **FAIL**.
3. Worst top-5 division excess over its best baseline ≤ 0.0003: -0.0084 → **PASS**.

**VERDICT: FAIL — production stays untouched; this market remains unmodelled.**

## Method notes and caveats

- The candidate's edge over the baselines includes the NB dispersion (the baselines are Poisson, the house definition since the SOT base experiment); the tuning table above separates the regression's own contribution (variant A vs baselines would show it) — variant A/B/C are tuning-season numbers, not test numbers.
- Provider disagreement on total shots is larger than for SOT (O/U flip 1.43–2.04% across the ladder, PREREG.md): the model is trained and graded on the spine's count; bookmaker settlement on another count is a pricing-side risk, not a model error.
- No odds anywhere: predictive accuracy/calibration only, not betting value (no total-shots odds in our data).
- Script runtime (this run, incl. data load): 121s.

## Coordinator's note (added after the run; no numbers changed)

The failure is narrow and specific: the candidate is the sharpest
predictor in the room — it beats both baselines at every ladder line,
in every season and every top-5 division — but at the headline line
its Over probability runs about 1.3 points low on average, driven by
two of the three test seasons (−2.13pp in 2023/24, −2.06pp in
2025/26, +0.17pp in 2024/25). That is a level/regime-tracking
shortfall in the predicted totals (shot rates shifted in those
seasons and the frozen recipe lagged), not a discrimination failure.

What may NOT happen next, by the project's own discipline: no
correction fitted to this test window, no gate edit, no re-run of
2023/24–2025/26 with a tweaked design — choosing the fix from the
test window would void the gate (the same refusal as the goals-halves
V3 tuning-elimination case). The legitimate route, if the user wants
one, is a NEW pre-registration: a design fixed in advance (e.g. one
whose level tracking is addressed a priori, not fitted here) tested
once on the virgin 2026/27 season once enough of it has been played.
Until then this market stays unmodelled and production is untouched.
