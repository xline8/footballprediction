# Shots-on-Target (SOT) Model — v5: Regression Ratings, Negative Binomial, Beta-Binomial Ratio (on SLIM)

Script: `run_sot_v5.py` (re-runnable; reuses `run_sot_v2.py`'s ratings/naive machinery and data loading unchanged). Reference: slim recipe of `run_sot_v3.py` / RESULTS_V3.md, which is what production `model_sot.py` implements. Same walk-forward evaluation (2023/24–2025/26). The three improvements are items R / 2 / 5A of the external proposal `improvement_model_prediksi_shot_on_goal.md`.

Evaluated matches: 21,461

## Slim reproduction check (validity of this run)

Slim recomputed in this pass: pooled line-9.5 log loss **0.6312**, Brier 0.2201, calib err 0.4pp, MAE 2.45 — RESULTS_V3.md: 0.6312 / 0.2201 / 0.4 / 2.45 → **MATCH**.

## Frozen choices (all made on pre-2023/24 data only)

- R ridge lambda (tuned on 2022/23 only, slim+R line-9.5 log loss): lam=1: 0.6079, lam=3: 0.6079, lam=10: 0.6078, lam=30: 0.6078, lam=100: 0.6078 → chosen **lam = 100**. Refits: lazy per division, every 7 days of match dates, data strictly before the prediction date, 365d decay sample weights, warm-started Newton/Fisher IRLS.
- BB prior strength P (tuned on 2022/23 only, slim+BB line-9.5 log loss): P=20: 0.6090, P=50: 0.6088, P=100: 0.6086, P=200: 0.6083 → chosen **P = 200 shots**. (Slim's built-in prior is K*mu_shots ≈ 104 shots home / 88 away.)
- NB size: **r = 79.94** from 28,176 slim walk-forward residuals (2019/20–2022/23; mean predicted total 8.44, residual variance / mean ratio 1.107 — Poisson would be 1.000).

## Headline — pooled, main line 9.5

| Variant | LogLoss | Brier | Calib err (pp) | MAE | ΔLL vs slim |
|---|---|---|---|---|---|
| SLIM (production reference) | 0.6312 | 0.2201 | 0.4 | 2.45 | +0.0000 |
| slim + R (joint regression ratings) | 0.6307 | 0.2199 | 0.4 | 2.44 | -0.0005 |
| slim + NB (negative binomial) | 0.6309 | 0.2200 | 0.2 | 2.45 | -0.0003 |
| slim + BB (Beta-Binomial ratio) | 0.6311 | 0.2201 | 0.4 | 2.45 | -0.0001 |
| slim + R + NB + BB (combined) | 0.6304 | 0.2198 | 0.2 | 2.44 | -0.0007 |

## Every variant at every line (pooled log loss)

| Variant | 7.5 | 8.5 | 9.5 | 10.5 |
|---|---|---|---|---|
| SLIM (production reference) | 0.6533 | 0.6726 | 0.6312 | 0.5456 |
| slim + R (joint regression ratings) | 0.6528 | 0.6719 | 0.6307 | 0.5451 |
| slim + NB (negative binomial) | 0.6531 | 0.6723 | 0.6309 | 0.5453 |
| slim + BB (Beta-Binomial ratio) | 0.6533 | 0.6724 | 0.6311 | 0.5456 |
| slim + R + NB + BB (combined) | 0.6526 | 0.6716 | 0.6304 | 0.5448 |

## By division (top-5) — line 9.5 log loss (slim alongside)

| Div | n | SLIM (production reference) | slim + R + NB + BB (combined) | slim + R (joint regression ratings) | slim + NB (negative binomial) | slim + BB (Beta-Binomial ratio) |
|---|---|---|---|---|---|---|
| E0 | 1,140 | 0.6647 | 0.6648 | 0.6649 | 0.6646 | 0.6645 |
| D1 | 917 | 0.6779 | 0.6780 | 0.6776 | 0.6779 | 0.6782 |
| I1 | 1,140 | 0.6108 | 0.6098 | 0.6097 | 0.6109 | 0.6105 |
| SP1 | 1,140 | 0.6315 | 0.6314 | 0.6316 | 0.6313 | 0.6315 |
| F1 | 918 | 0.6708 | 0.6697 | 0.6695 | 0.6707 | 0.6709 |

## Combined by season — line 9.5 (slim alongside)

| Season | n | Combined LogLoss | Combined Brier | Combined calib (pp) | Slim LogLoss |
|---|---|---|---|---|---|
| 2023/24 | 7,245 | 0.6375 | 0.2233 | 1.5 | 0.6377 |
| 2024/25 | 7,122 | 0.6258 | 0.2178 | 0.6 | 0.6269 |
| 2025/26 | 7,094 | 0.6279 | 0.2183 | 0.3 | 0.6288 |

## Gate verdict

- slim + R (joint regression ratings): ΔLL -0.0005; calib 0.4pp (worsening +0.0pp, limit +1.5pp; stricter absolute ≤1.5pp: ok); worst top-5 division ΔLL +0.0002 (limit +0.003) → **ADOPTABLE**.
- slim + NB (negative binomial): ΔLL -0.0003; calib 0.2pp (worsening -0.2pp, limit +1.5pp; stricter absolute ≤1.5pp: ok); worst top-5 division ΔLL +0.0002 (limit +0.003) → **ADOPTABLE**.
- slim + BB (Beta-Binomial ratio): ΔLL -0.0001; calib 0.4pp (worsening -0.0pp, limit +1.5pp; stricter absolute ≤1.5pp: ok); worst top-5 division ΔLL +0.0003 (limit +0.003) → **ADOPTABLE**.
- slim + R + NB + BB (combined): ΔLL -0.0007; calib 0.2pp (worsening -0.2pp, limit +1.5pp; stricter absolute ≤1.5pp: ok); worst top-5 division ΔLL +0.0002 (limit +0.003) → **ADOPTABLE**.
- **Winner: slim + R + NB + BB (combined)** (LL 0.6304 vs slim 0.6312).

## Method notes and caveats

- R changes only the ratings-based expectation (and the naive tracker's league-mean fallback); the shots system, the naive history and the 50/50 ensemble are slim's. The regression team index spans all of a division's matches (indexing only); a team with no prior matches in the fit set has A = D = 0 by construction of the ridge.
- BB differs from slim's built-in ratio shrinkage only in the prior-strength parametrization: a fixed pseudo-shot count P for both venues (tuned) instead of K * mu_shots (venue-dependent, ~104 home / ~88 away). The shrinkage target rho (decayed league ratio per venue) is unchanged.
- NB is applied to both ensemble members' totals with the single frozen r estimated from slim residuals; the combined variant uses that same frozen r on top of its own (R+BB) expectations — interactions are not re-estimated.
- Tuning (lam, P) used 2022/23 only; the NB size used 2019/20–2022/23 residuals only; test seasons untouched by every choice.
- No odds anywhere: predictive accuracy/calibration only, not betting value (no SOT odds in our data).
- Script runtime (this run, incl. data load): 59s.
