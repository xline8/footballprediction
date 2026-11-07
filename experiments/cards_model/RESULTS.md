# Model Kartu Pertama (Total Kartu Kuning) — Hasil Backtest

## Ringkasan (Bahasa Indonesia)

Model rating tim untuk total kartu kuning per laga (HY+AY, lima liga top Eropa) diuji walk-forward pada musim 2023/24–2025/26 (n=5,255). Half-life terpilih dari jendela tuning (musim 2020/21–2022/23, tanpa menyentuh musim uji): **270 hari**, dengan ukuran Negative Binomial r = 112.39 untuk model. Di garis utama 4.5, log loss pooled model **0.6555** vs baseline laju dasar divisi **0.6634** dan baseline naif trailing-10 **0.6623**; kalibrasi model +0.90pp (prediksi − aktual Over); selisih divisi terburuk vs baseline (a) +0.0001 (E0).

**Putusan gerbang (pre-registered, audit §3C): LOLOS (PASS)** — mengalahkan baseline (a): ya; mengalahkan baseline (b): ya; |kalibrasi| ≤ 1pp: ya; tidak ada divisi lebih buruk dari (a) > 0.003: ya.

Model lolos gerbang akurasi offline. Nilai taruhannya tetap belum terbukti: tidak ada odds kartu yang tertangkap sistem (sama seperti SOT/corner) — akurasi dulu, pasar kemudian.

Script: `run_cards_experiment.py` (rerunnable; stdlib only; reads only `all_matches_clean.csv`, writes only this file and `cards_test_predictions.csv` in this folder). Design: `experiments/MODEL_AUDIT_2026-11-07.md` §3C.

## Method

- Target: total yellows per match = HY + AY (clean file is the single label source; FotMob yellows differ definitionally on ~10% of matches per the audit, so it is not mixed in).
- Model: venue-split decayed team ratings for yellows for/against (prior K = 8 match-equivalents), division base rates (decayed mu_home/mu_away), Negative Binomial probabilities. No referee term (audit: excess between-referee variance ~= 0).
- Tuning window: seasons 2020/21, 2021/22, 2022/23 scored walk-forward (warm-up from 2017/18); half-life grid [180, 270, 365]; test seasons 2023/24, 2024/25, 2025/26 scored once with frozen HL and r.
- Rows skipped (HY/AY missing): 1: D1 2024/25 2024-12-14 Union Berlin vs Bochum.

## Tuning (window ≤2022/23 only)

| Half-life | Tuning n | r (model) | Tuning LL@4.5 model | Tuning LL@4.5 base (a) | Tuning LL@4.5 naive (b) |
|---|---|---|---|---|---|
| 180 | 5478 | 108.77 | 0.6367 | 0.6442 | 0.6425 |
| 270 ← chosen | 5478 | 112.39 | 0.6366 | 0.6449 | 0.6425 |
| 365 | 5478 | 110.87 | 0.6369 | 0.6453 | 0.6425 |

Frozen NB sizes at chosen HL 270: model r = 112.39, baseline (a) r = 70.04, baseline (b) r = 66.57 (audit prior expectation for the model: r ≈ 31).

Note on r: the audit's r ≈ 31 is the MARGINAL moment estimate (one pooled mean for all matches; on this test set the same marginal formula gives r ≈ 38). The frozen r above is estimated from walk-forward RESIDUALS around match-specific means: team and division ratings absorb much of the marginal overdispersion, so the conditional r is larger (the same estimation route the SOT v5 model used for its r = 79.94). Applied to the test residuals after the fact, the model's implied r is ≈ 84 — the same order, so the frozen 112 is not an artefact of the tuning window.

## Pooled test results (2023/24–2025/26)

### All top-5, n=5,255

| Method | Line | n | Brier | LogLoss | Pred Over% | Actual Over% | Calib (pp) | MAE total |
|---|---|---|---|---|---|---|---|---|
| Cards ratings model | 3.5 | 5255 | 0.2387 | 0.6705 | 57.94 | 58.31 | -0.37 | 1.651 |
| Cards ratings model | 4.5 | 5255 | 0.2315 | 0.6555 | 39.50 | 38.59 | +0.90 | 1.651 |
| Cards ratings model | 5.5 | 5255 | 0.1707 | 0.5225 | 24.32 | 22.40 | +1.93 | 1.651 |
| Baseline (a) division base-rate | 3.5 | 5255 | 0.2433 | 0.6796 | 58.04 | 58.31 | -0.26 | 1.665 |
| Baseline (a) division base-rate | 4.5 | 5255 | 0.2353 | 0.6634 | 39.38 | 38.59 | +0.78 | 1.665 |
| Baseline (a) division base-rate | 5.5 | 5255 | 0.1719 | 0.5268 | 24.04 | 22.40 | +1.64 | 1.665 |
| Baseline (b) naive trailing-10 | 3.5 | 5255 | 0.2416 | 0.6765 | 56.56 | 58.31 | -1.75 | 1.663 |
| Baseline (b) naive trailing-10 | 4.5 | 5255 | 0.2344 | 0.6623 | 38.43 | 38.59 | -0.16 | 1.663 |
| Baseline (b) naive trailing-10 | 5.5 | 5255 | 0.1715 | 0.5256 | 23.71 | 22.40 | +1.31 | 1.663 |

## Per season

### Season 2023/24, n=1,752

| Method | Line | n | Brier | LogLoss | Pred Over% | Actual Over% | Calib (pp) | MAE total |
|---|---|---|---|---|---|---|---|---|
| Cards ratings model | 3.5 | 1752 | 0.2367 | 0.6665 | 59.40 | 62.10 | -2.70 | 1.684 |
| Cards ratings model | 4.5 | 1752 | 0.2428 | 0.6803 | 41.16 | 42.98 | -1.82 | 1.684 |
| Cards ratings model | 5.5 | 1752 | 0.1883 | 0.5644 | 25.85 | 25.74 | +0.11 | 1.684 |
| Baseline (a) division base-rate | 3.5 | 1752 | 0.2386 | 0.6701 | 59.15 | 62.10 | -2.95 | 1.694 |
| Baseline (a) division base-rate | 4.5 | 1752 | 0.2451 | 0.6839 | 40.71 | 42.98 | -2.27 | 1.694 |
| Baseline (a) division base-rate | 5.5 | 1752 | 0.1891 | 0.5655 | 25.33 | 25.74 | -0.42 | 1.694 |
| Baseline (b) naive trailing-10 | 3.5 | 1752 | 0.2353 | 0.6634 | 60.40 | 62.10 | -1.70 | 1.689 |
| Baseline (b) naive trailing-10 | 4.5 | 1752 | 0.2425 | 0.6793 | 42.34 | 42.98 | -0.63 | 1.689 |
| Baseline (b) naive trailing-10 | 5.5 | 1752 | 0.1890 | 0.5655 | 27.00 | 25.74 | +1.26 | 1.689 |

### Season 2024/25, n=1,751

| Method | Line | n | Brier | LogLoss | Pred Over% | Actual Over% | Calib (pp) | MAE total |
|---|---|---|---|---|---|---|---|---|
| Cards ratings model | 3.5 | 1751 | 0.2394 | 0.6717 | 59.06 | 57.57 | +1.49 | 1.694 |
| Cards ratings model | 4.5 | 1751 | 0.2306 | 0.6533 | 40.56 | 37.75 | +2.81 | 1.694 |
| Cards ratings model | 5.5 | 1751 | 0.1702 | 0.5212 | 25.15 | 22.04 | +3.10 | 1.694 |
| Baseline (a) division base-rate | 3.5 | 1751 | 0.2442 | 0.6815 | 59.13 | 57.57 | +1.56 | 1.705 |
| Baseline (a) division base-rate | 4.5 | 1751 | 0.2347 | 0.6621 | 40.41 | 37.75 | +2.66 | 1.705 |
| Baseline (a) division base-rate | 5.5 | 1751 | 0.1718 | 0.5271 | 24.84 | 22.04 | +2.79 | 1.705 |
| Baseline (b) naive trailing-10 | 3.5 | 1751 | 0.2424 | 0.6784 | 56.18 | 57.57 | -1.38 | 1.695 |
| Baseline (b) naive trailing-10 | 4.5 | 1751 | 0.2328 | 0.6587 | 38.13 | 37.75 | +0.38 | 1.695 |
| Baseline (b) naive trailing-10 | 5.5 | 1751 | 0.1688 | 0.5182 | 23.53 | 22.04 | +1.49 | 1.695 |

### Season 2025/26, n=1,752

| Method | Line | n | Brier | LogLoss | Pred Over% | Actual Over% | Calib (pp) | MAE total |
|---|---|---|---|---|---|---|---|---|
| Cards ratings model | 3.5 | 1752 | 0.2402 | 0.6733 | 55.37 | 55.25 | +0.12 | 1.574 |
| Cards ratings model | 4.5 | 1752 | 0.2213 | 0.6327 | 36.78 | 35.05 | +1.73 | 1.574 |
| Cards ratings model | 5.5 | 1752 | 0.1537 | 0.4819 | 21.98 | 19.41 | +2.57 | 1.574 |
| Baseline (a) division base-rate | 3.5 | 1752 | 0.2470 | 0.6871 | 55.85 | 55.25 | +0.60 | 1.595 |
| Baseline (a) division base-rate | 4.5 | 1752 | 0.2260 | 0.6443 | 37.01 | 35.05 | +1.96 | 1.595 |
| Baseline (a) division base-rate | 5.5 | 1752 | 0.1549 | 0.4876 | 21.96 | 19.41 | +2.56 | 1.595 |
| Baseline (b) naive trailing-10 | 3.5 | 1752 | 0.2472 | 0.6877 | 53.09 | 55.25 | -2.16 | 1.604 |
| Baseline (b) naive trailing-10 | 4.5 | 1752 | 0.2280 | 0.6490 | 34.81 | 35.05 | -0.24 | 1.604 |
| Baseline (b) naive trailing-10 | 5.5 | 1752 | 0.1567 | 0.4929 | 20.60 | 19.41 | +1.19 | 1.604 |

## Per division (pooled test seasons)

### Division E0, n=1,140 (ΔLL@4.5 model − base (a): +0.0001)

| Method | Line | n | Brier | LogLoss | Pred Over% | Actual Over% | Calib (pp) | MAE total |
|---|---|---|---|---|---|---|---|---|
| Cards ratings model | 3.5 | 1140 | 0.2457 | 0.6847 | 53.90 | 58.51 | -4.61 | 1.670 |
| Cards ratings model | 4.5 | 1140 | 0.2391 | 0.6731 | 35.23 | 38.33 | -3.11 | 1.670 |
| Cards ratings model | 5.5 | 1140 | 0.1741 | 0.5347 | 20.64 | 22.02 | -1.38 | 1.670 |
| Baseline (a) division base-rate | 3.5 | 1140 | 0.2473 | 0.6876 | 53.53 | 58.51 | -4.98 | 1.660 |
| Baseline (a) division base-rate | 4.5 | 1140 | 0.2396 | 0.6730 | 34.62 | 38.33 | -3.72 | 1.660 |
| Baseline (a) division base-rate | 5.5 | 1140 | 0.1728 | 0.5311 | 19.95 | 22.02 | -2.06 | 1.660 |
| Baseline (b) naive trailing-10 | 3.5 | 1140 | 0.2447 | 0.6823 | 54.78 | 58.51 | -3.73 | 1.675 |
| Baseline (b) naive trailing-10 | 4.5 | 1140 | 0.2395 | 0.6741 | 36.59 | 38.33 | -1.74 | 1.675 |
| Baseline (b) naive trailing-10 | 5.5 | 1140 | 0.1722 | 0.5290 | 22.16 | 22.02 | +0.14 | 1.675 |

### Division D1, n=917 (ΔLL@4.5 model − base (a): -0.0070)

| Method | Line | n | Brier | LogLoss | Pred Over% | Actual Over% | Calib (pp) | MAE total |
|---|---|---|---|---|---|---|---|---|
| Cards ratings model | 3.5 | 917 | 0.2436 | 0.6806 | 56.12 | 55.18 | +0.94 | 1.682 |
| Cards ratings model | 4.5 | 917 | 0.2284 | 0.6480 | 37.41 | 36.31 | +1.09 | 1.682 |
| Cards ratings model | 5.5 | 917 | 0.1660 | 0.5117 | 22.37 | 21.16 | +1.22 | 1.682 |
| Baseline (a) division base-rate | 3.5 | 917 | 0.2471 | 0.6873 | 55.94 | 55.18 | +0.76 | 1.683 |
| Baseline (a) division base-rate | 4.5 | 917 | 0.2312 | 0.6550 | 36.96 | 36.31 | +0.64 | 1.683 |
| Baseline (a) division base-rate | 5.5 | 917 | 0.1665 | 0.5152 | 21.80 | 21.16 | +0.64 | 1.683 |
| Baseline (b) naive trailing-10 | 3.5 | 917 | 0.2473 | 0.6885 | 55.34 | 55.18 | +0.16 | 1.699 |
| Baseline (b) naive trailing-10 | 4.5 | 917 | 0.2323 | 0.6586 | 37.04 | 36.31 | +0.73 | 1.699 |
| Baseline (b) naive trailing-10 | 5.5 | 917 | 0.1646 | 0.5116 | 22.42 | 21.16 | +1.26 | 1.699 |

### Division I1, n=1,140 (ΔLL@4.5 model − base (a): -0.0241)

| Method | Line | n | Brier | LogLoss | Pred Over% | Actual Over% | Calib (pp) | MAE total |
|---|---|---|---|---|---|---|---|---|
| Cards ratings model | 3.5 | 1140 | 0.2315 | 0.6549 | 59.55 | 57.02 | +2.53 | 1.519 |
| Cards ratings model | 4.5 | 1140 | 0.2198 | 0.6300 | 41.05 | 36.58 | +4.47 | 1.519 |
| Cards ratings model | 5.5 | 1140 | 0.1570 | 0.4906 | 25.54 | 20.00 | +5.54 | 1.519 |
| Baseline (a) division base-rate | 3.5 | 1140 | 0.2432 | 0.6794 | 59.82 | 57.02 | +2.80 | 1.570 |
| Baseline (a) division base-rate | 4.5 | 1140 | 0.2308 | 0.6541 | 41.03 | 36.58 | +4.45 | 1.570 |
| Baseline (a) division base-rate | 5.5 | 1140 | 0.1614 | 0.5039 | 25.27 | 20.00 | +5.27 | 1.570 |
| Baseline (b) naive trailing-10 | 3.5 | 1140 | 0.2374 | 0.6674 | 55.03 | 57.02 | -1.99 | 1.523 |
| Baseline (b) naive trailing-10 | 4.5 | 1140 | 0.2214 | 0.6347 | 36.85 | 36.58 | +0.27 | 1.523 |
| Baseline (b) naive trailing-10 | 5.5 | 1140 | 0.1580 | 0.4930 | 22.35 | 20.00 | +2.35 | 1.523 |

### Division SP1, n=1,140 (ΔLL@4.5 model − base (a): -0.0060)

| Method | Line | n | Brier | LogLoss | Pred Over% | Actual Over% | Calib (pp) | MAE total |
|---|---|---|---|---|---|---|---|---|
| Cards ratings model | 3.5 | 1140 | 0.2268 | 0.6468 | 67.79 | 64.30 | +3.49 | 1.855 |
| Cards ratings model | 4.5 | 1140 | 0.2462 | 0.6856 | 49.99 | 47.11 | +2.88 | 1.855 |
| Cards ratings model | 5.5 | 1140 | 0.2125 | 0.6151 | 33.48 | 30.96 | +2.51 | 1.855 |
| Baseline (a) division base-rate | 3.5 | 1140 | 0.2306 | 0.6541 | 68.44 | 64.30 | +4.14 | 1.872 |
| Baseline (a) division base-rate | 4.5 | 1140 | 0.2492 | 0.6916 | 50.50 | 47.11 | +3.40 | 1.872 |
| Baseline (a) division base-rate | 5.5 | 1140 | 0.2135 | 0.6182 | 33.74 | 30.96 | +2.77 | 1.872 |
| Baseline (b) naive trailing-10 | 3.5 | 1140 | 0.2305 | 0.6547 | 65.09 | 64.30 | +0.79 | 1.871 |
| Baseline (b) naive trailing-10 | 4.5 | 1140 | 0.2526 | 0.6995 | 47.34 | 47.11 | +0.24 | 1.871 |
| Baseline (b) naive trailing-10 | 5.5 | 1140 | 0.2147 | 0.6232 | 31.40 | 30.96 | +0.43 | 1.871 |

### Division F1, n=918 (ΔLL@4.5 model − base (a): -0.0011)

| Method | Line | n | Brier | LogLoss | Pred Over% | Actual Over% | Calib (pp) | MAE total |
|---|---|---|---|---|---|---|---|---|
| Cards ratings model | 3.5 | 918 | 0.2492 | 0.6916 | 50.55 | 55.34 | -4.78 | 1.505 |
| Cards ratings model | 4.5 | 918 | 0.2217 | 0.6352 | 31.93 | 33.12 | -1.19 | 1.505 |
| Cards ratings model | 5.5 | 918 | 0.1364 | 0.4427 | 17.98 | 16.45 | +1.53 | 1.505 |
| Baseline (a) division base-rate | 3.5 | 918 | 0.2503 | 0.6937 | 50.64 | 55.34 | -4.70 | 1.514 |
| Baseline (a) division base-rate | 4.5 | 918 | 0.2221 | 0.6363 | 31.84 | 33.12 | -1.28 | 1.514 |
| Baseline (a) division base-rate | 5.5 | 918 | 0.1377 | 0.4478 | 17.79 | 16.45 | +1.34 | 1.514 |
| Baseline (b) naive trailing-10 | 3.5 | 918 | 0.2512 | 0.6958 | 51.29 | 55.34 | -4.05 | 1.527 |
| Baseline (b) naive trailing-10 | 4.5 | 918 | 0.2238 | 0.6396 | 32.98 | 33.12 | -0.13 | 1.527 |
| Baseline (b) naive trailing-10 | 5.5 | 918 | 0.1406 | 0.4545 | 19.07 | 16.45 | +2.62 | 1.527 |

## Gate verdict (detail)

- Pooled LL@4.5: model **0.6555** vs (a) 0.6634 (Δ -0.0079) vs (b) 0.6623 (Δ -0.0069) → beats both: yes
- Pooled calibration @4.5: +0.90pp (limit |1.00|pp) → ok
- Worst division ΔLL@4.5 vs (a): E0 +0.0001 (limit +0.003) → ok
- LL@3.5 / @5.5 (context): model 0.6705 / 0.5225; (a) 0.6796 / 0.5268; (b) 0.6765 / 0.5256
- **VERDICT: PASS**

## Caveats

- No cards odds exist anywhere in the system, so this measures predictive accuracy and calibration only — betting value is unproven even on a PASS (identical blocker to SOT/corners).
- The two teams' card counts are not independent in reality (match temperature, scoreline, referee on the day couple them); the NB size absorbs average overdispersion only.
- 2025/26 in the clean file is a complete stored season here (1,752 top-5 rows, same as 2023/24 and 2024/25).
- A production model_cards.py, if built, needs only the clean spine (HY/AY history) plus upcoming fixtures — no FotMob warehouse features are used anywhere in this recipe.
