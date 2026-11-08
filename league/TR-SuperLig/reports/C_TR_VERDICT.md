# C-TR verdict

Source JSONs: `engine/corners/results_dev.json` and `engine/corners/results_virgin.json`. Dev scored 1,033 rows in 2022/2023–2024/2025; virgin scored 306 rows in 2025/2026. No 2026/2027 rows were read.

| arm | dev pooled LL@9.5 | league base | naive trailing-10 | dev gate | virgin LL | calibration breach / SE |
|---|---:|---:|---:|---|---:|---|
| Gate Zero | 0.694704 | 0.729372 | 0.726099 | PASS | 0.693237 | +1.182pp / 2.862pp |
| X7 | 0.694704 | 0.729372 | 0.726099 | PASS | 0.693237 | +1.182pp / 2.862pp |

Both arms beat both dev baselines. Virgin LL legs and calibration legs pass provisionally: 1.182pp breach is within one SE of the 1.0pp boundary. X7's fitted touches coefficient is beta = [0, 0] (`active_with_nonzero_beta_share` = 0.0 in every season), so X7 is numerically identical to Gate Zero at the primary line in dev and virgin — the same outcome shape as C-BE's dev — and Gate Zero ships by the frozen tie/simplicity rule.

Shipped fitted params: `engine/corners/fitted_params_virgin.json` (Gate Zero; gamma=0.15, r=1.135637, beta=[0,0], fit_n=1403). TR-specific handling: touches-opp-box X7 uses the frozen min-8-of-last-10 fallback; partial early coverage therefore leaves X7 inactive where required.
