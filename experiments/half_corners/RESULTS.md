# Model Corner Babak Pertama (1H) — Backtest

## Ringkasan (Bahasa Indonesia)

Model corner babak pertama diuji walk-forward: tuning HANYA di musim 2023/24 (satu-satunya musim tuning yang jujur — label 1H 2022/23 cakupannya cuma 35,6%, jadi musim itu hanya dipakai sebagai riwayat trailing, bukan untuk tuning), tes di 2024/25 + 2025/26 (n = 3,503). Di garis tengah 4,5: log loss model **0.6885**, baseline base-rate divisi **0.6901**, baseline naif 0,472 × model FT **0.6886**; kalibrasi model -0.36pp (prediksi Over 46.3% vs aktual 46.7%). MAE model 1.80 corner.

**Verdict gerbang (pra-registrasi): LOLOS (PASS)** — syarat log loss mengalahkan KEDUA baseline: terpenuhi; syarat |kalibrasi| ≤ 1pp: terpenuhi. Produksi tidak disentuh apa pun hasilnya.

**Margin sangat tipis — baca ini sebelum mengutip verdict:** keunggulan model atas baseline naif hanya 0.0001 log loss (praktis seri; per musim model kalah dari naif di 2024/25 dan menang di 2025/26, dan per divisi model kalah dari naif di E0, D1, dan F1). Gerbang pra-registrasi C-2 memang tidak mensyaratkan margin minimum, jadi verdict formalnya PASS, tapi bukti keunggulan model 1H khusus atas sekadar menskalakan model FT itu lemah.

**Catatan tetap:** belum ada sumber odds corner babak pertama yang tertangkap sistem (sama seperti corner FT dan SOT) — akurasi terukur di sini, nilai taruhan belum bisa dibuktikan.

---

Script: `run_half_corners.py` (re-runnable; reads the FotMob store + `predictions_corners_shots.csv` read-only, writes only this folder). Design: `experiments/MODEL_AUDIT_2026-11-07.md` §2C item C-2. No production file was modified.

## Label coverage (FotMob store period stats, FirstHalf corners)

| Season | Store matches | With 1H corners | Coverage |
|---|---|---|---|
| 2022/23 | 1,826 | 650 | 35.6% |
| 2023/24 | 1,752 | 1,750 | 99.9% |
| 2024/25 | 1,751 | 1,751 | 100.0% |
| 2025/26 | 1,752 | 1,752 | 100.0% |
| 2026/27 | 451 | 451 | 100.0% |

Cross-check: on matches with both halves labelled, (1H+2H) corners equal the FT corners in `shot_lineup_features.csv` exactly in 6,353/6,353 cases (100.0%). 1H share of FT corners re-measured here: mean 0.468 (n=6,354; audit: 0.472 ± 0.174) — the fixed 0.472 factor of baseline (b) is kept as pre-registered, not re-fit.
Labelled matches in the model window (2022/23 + 2023/24 + 2024/25 + 2025/26): 5,903. `shot_lineup_features.csv` carries no 1H corner split (FT only), so labels were extracted from the store JSONs.

## Frozen choices (2023/24 tuning season ONLY)

- Ratings grid (NB log loss @4.5 on 2023/24, each cell with its own MoM r): chosen **HL = 180d, K = 24** (LL 0.6926, r = 43.03). Full grid:

| HL \ K | K=4 | K=8 | K=16 | K=24 |
|---|---|---|---|---|
| 180d | 0.7079 | 0.6993 | 0.6941 | 0.6926 |
| 270d | 0.7084 | 0.7000 | 0.6944 | 0.6927 |
| 365d | 0.7088 | 0.7004 | 0.6946 | 0.6928 |
| 540d | 0.7092 | 0.7008 | 0.6949 | 0.6929 |

- NB sizes (MoM on 2023/24 walk-forward residuals, frozen): model r = 43.03; base-rate r = 45.13; naive r = 51.17.
- Baseline (b) FT-mu join on the tuning season: 1,750/1,750 matches; on the test set: 3,503/3,503 (any test match without an FT mu would be dropped for ALL predictors — identical set).
- Central line 4.5 = 0.472 × FT central 9.5 = 4.48 ≈ 4.5.

## Headline — pooled test (2024/25 + 2025/26), line 4.5

| Predictor | n | LogLoss@4.5 | Brier | Pred Over% | Act Over% | Calib diff (pp) | MAE |
|---|---|---|---|---|---|---|---|
| 1H ratings model | 3,503 | 0.6885 | 0.2477 | 46.3 | 46.7 | -0.36 | 1.80 |
| (a) division base rate | 3,503 | 0.6901 | 0.2485 | 46.8 | 46.7 | +0.14 | 1.81 |
| (b) naive 0.472×FT model | 3,503 | 0.6886 | 0.2477 | 47.0 | 46.7 | +0.33 | 1.81 |

## All lines — pooled (log loss / calib diff pp)

| Predictor | 3.5 | 4.5 | 5.5 |
|---|---|---|---|
| model | 0.6522 / +0.27pp | 0.6885 / -0.36pp | 0.6050 / +0.44pp |
| base | 0.6521 / +0.85pp | 0.6901 / +0.14pp | 0.6084 / +0.75pp |
| naive | 0.6498 / +1.09pp | 0.6886 / +0.33pp | 0.6072 / +0.86pp |

## By season — line 4.5

| Season | n | Model LL | Base LL | Naive LL | Model calib (pp) | Base calib | Naive calib | Model MAE |
|---|---|---|---|---|---|---|---|---|
| 2024/25 | 1,751 | 0.6881 | 0.6899 | 0.6876 | +0.95 | +1.39 | +1.16 | 1.79 |
| 2025/26 | 1,752 | 0.6889 | 0.6903 | 0.6895 | -1.67 | -1.11 | -0.50 | 1.81 |

## By division — line 4.5 (model, baselines alongside)

| Div | n | Model LL | Base LL | Naive LL | Model calib (pp) | Act Over% |
|---|---|---|---|---|---|---|
| E0 | 760 | 0.6957 | 0.6929 | 0.6923 | +0.91 | 50.9 |
| D1 | 611 | 0.6983 | 0.6940 | 0.6921 | -2.37 | 47.8 |
| I1 | 760 | 0.6820 | 0.6830 | 0.6838 | +1.55 | 42.1 |
| SP1 | 760 | 0.6789 | 0.6899 | 0.6860 | -0.94 | 46.2 |
| F1 | 612 | 0.6897 | 0.6919 | 0.6895 | -1.58 | 46.6 |

## Gate verdict (pre-registered)

- Model LL@4.5 0.6885 vs base 0.6901 (beats) and vs naive 0.6886 (beats).
- Pooled calibration @4.5: -0.36pp (|diff| ≤ 1pp: ok).
- **PASS**

## Method notes and caveats

- Walk-forward everywhere: every state (ratings, league means) updates only AFTER the match is predicted; tuning choices and all three NB sizes are frozen from 2023/24 before any test match is scored.
- 2022/23 honesty: only ~32% of that season carries 1H labels, so ratings entering 2023/24 are built from a partial season — a real cold-start handicap the tuning and test numbers both live with. 2022/23 was used for NOTHING except trailing state updates.
- Baseline (b) construction, exactly: mu_naive = 0.472 × mu_shots_cs from the FT corner model's stored walk-forward artifact (read-only), probability = NegBin(mean=mu_naive, size=r_naive) tail above the line — the same NB family and the same MoM r estimator as the model, with r_naive fit on the naive baseline's own 2023/24 residuals.
- The model's exp is per-team (venue-split attack/defence on 1H corners for/against); the total is the sum. No halftime-state or in-match information is used — this is a pre-match model, like the FT corner model.
- No odds source for 1H corners exists in the system (market_compare carries none, and no other capture is wired) — betting value is unprovable today; this measures accuracy/calibration only.
- Runtime: 249s. Outputs: `labels_1h_corners.csv` (all store matches, reusable asset), `test_predictions.csv`, this file.
