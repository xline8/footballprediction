# Total Shots Model v2 — Experiment Results

Script: `run_shots_experiment_v2.py`. Design and gate: `PREREG.md` (committed before this run). Candidate = v1's frozen winner (ridge lam=100, NB r=79.82, 50/50 naive ensemble) + a per-division level layer. Verdict window: the virgin 2026/27 season, evaluated once.

Verdict window evaluated matches: 2,032 (of which top-5: 451)

## Level layer — tuning (2022/23 LL@25.5, selection reads this table only)

| HL (days) | s | K | LL@25.5 |
|---|---|---|---|
| 60 | 0.5 | 20 | 0.6116 ← chosen |
| 120 | 0.5 | 20 | 0.6116 |
| 120 | 0.5 | 50 | 0.6117 |
| 60 | 0.5 | 50 | 0.6117 |
| 30 | 0.5 | 20 | 0.6117 |
| 60 | 1 | 50 | 0.6118 |
| 120 | 1 | 50 | 0.6118 |
| 30 | 0.5 | 50 | 0.6118 |
| 30 | 1 | 50 | 0.6119 |
| 120 | 1 | 20 | 0.6120 |
| 60 | 1 | 20 | 0.6120 |
| 30 | 1 | 20 | 0.6123 |

No-layer arm (v1 candidate) on the same tuning pass: 0.6122.

**Frozen layer cell: HL = 60 days, s = 0.5, K = 20** (factor clip [0.9, 1.1], prior mean M̄ = 25.0).

## Harness check — no-layer arm vs v1 published (secondary window 2023/24–2025/26, pooled)

v1 published: LL 0.6263, calib -1.34pp. This pass, no-layer arm: LL 0.6263, calib -1.34pp. Any small deviation is the refit-anchoring difference documented in PREREG.md (predictions computed for every match here; v1's eval pass predicted test seasons only) — both cadences are strictly walk-forward honest, and the v1-vs-v2 comparison below uses arms from THIS pass, which share one trajectory.

## Secondary window — per-season drift @25.5 (NOT the verdict)

| Season | n | v1 published calib | v2 no-layer calib | v2 layered calib | v2 layered LL | v2 no-layer LL |
|---|---|---|---|---|---|---|
| 2023/24 | 7,245 | -2.13pp | -2.13pp | -1.21pp | 0.6268 | 0.6285 |
| 2024/25 | 7,122 | +0.17pp | +0.17pp | +0.03pp | 0.6189 | 0.6187 |
| 2025/26 | 7,094 | -2.06pp | -2.06pp | -1.63pp | 0.6316 | 0.6318 |

Pooled secondary: layered calib -0.94pp (LL 0.6257) vs no-layer -1.34pp (LL 0.6263).

## Verdict window (2026/27) — headline, line 25.5

| Method | LogLoss | Brier | Pred Over% | Actual Over% | Calib (pp, signed) | MAE |
|---|---|---|---|---|---|---|
| Candidate v2 (layered) | 0.6348 | 0.2230 | 48.6 | 54.6 | -6.04 | 4.88 |
| No-layer arm (v1 candidate) | 0.6422 | 0.2266 | 46.0 | 54.6 | -8.60 | 4.92 |
| Baseline (a) division base rate | 0.6694 | 0.2400 | 41.8 | 54.6 | -12.82 | 5.12 |
| Baseline (b) naive trailing-10 | 0.6408 | 0.2250 | 50.6 | 54.6 | -4.01 | 4.90 |

Calibration standard error (pooled, candidate): **1.04pp** at n = 2,032. Top-5 only, for information: calib -6.76pp, SE 2.27pp at n = 451; candidate top-5 LL 0.6653.

## Verdict window — all lines, pooled log loss

| Method | 22.5 | 23.5 | 24.5 | 25.5 | 26.5 | 27.5 | 28.5 |
|---|---|---|---|---|---|---|---|
| Candidate v2 (layered) | 0.5186 | 0.5675 | 0.6060 | 0.6348 | 0.6409 | 0.6366 | 0.6220 |
| No-layer arm (v1 candidate) | 0.5266 | 0.5748 | 0.6139 | 0.6422 | 0.6493 | 0.6459 | 0.6306 |
| Baseline (a) division base rate | 0.5357 | 0.5889 | 0.6339 | 0.6694 | 0.6849 | 0.6903 | 0.6825 |
| Baseline (b) naive trailing-10 | 0.5197 | 0.5705 | 0.6104 | 0.6408 | 0.6461 | 0.6459 | 0.6340 |

## Verdict window — by division (top-5), line 25.5

| Div | n | Candidate LL | Best baseline LL | Δ | Candidate calib (pp) |
|---|---|---|---|---|---|
| E0 | 90 | 0.7155 | 0.6913 | +0.0242 | -3.05 |
| D1 | 72 | 0.6233 | 0.6256 | -0.0023 | -3.49 |
| I1 | 99 | 0.6267 | 0.6057 | +0.0211 | -12.51 |
| SP1 | 109 | 0.6693 | 0.6905 | -0.0212 | -11.55 |
| F1 | 81 | 0.6883 | 0.6878 | +0.0005 | -0.33 |

## Gate verdict (PREREG.md, fixed before the run; 2026/27 window)

1. Pooled LL@25.5 beats best baseline by ≥ 0.001: margin +0.0060 → **PASS**.
2. Calibration @25.5 point estimate within ±1.0pp: -6.04pp → **FAIL** (point estimate). SE = 1.04pp vs the ±1.0pp band: NOT statistically meaningful (SE > 0.5pp) — the honesty clause applies.
3. Worst top-5 division excess over its best baseline ≤ 0.0003: +0.0242 → **FAIL**.

**VERDICT: FAIL — production stays untouched; this market remains unmodelled.**

## Method notes and caveats

- The level layer tracks the base candidate's OWN pre-match predictions (unadjusted), so it estimates the base model's trailing level bias per division; it cannot chase its own corrections.
- The baselines include no NB dispersion (house definition since the SOT base experiment); the candidate's edge partly reflects dispersion, as in v1 — the secondary-window drift table, not the LL margin, is the direct evidence on the layer itself.
- Provider disagreement on total shots is larger than for SOT (O/U flip 1.43–2.04% across the ladder, v1 PREREG.md): the model is trained and graded on the spine's count; bookmaker settlement on another count is a pricing-side risk, not a model error.
- No odds anywhere: predictive accuracy/calibration only, not betting value (no total-shots odds in our data).
- Script runtime (this run, incl. data load): 71s.
