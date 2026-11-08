# C-GR verdict

Preregistration: `prereg/PREREG_C_GR.md`; virgin is 2025/2026,
n=236, read once. Calibration below is actual − predicted.

## Dev (scored 2022/2023–2024/2025, n=716, LL@8.5)

| arm / baseline | pooled | 2022/23 | 2023/24 | 2024/25 |
|---|---:|---:|---:|---:|
| Gate Zero | 0.702636 | 0.699208 | 0.708855 | 0.699797 |
| X7 | 0.696186 | 0.699208 | 0.693932 | 0.695404 |
| league base rate | 0.728437 | | | |
| naive trailing-10 | 0.729695 | | | |

Both arms pass the dev gate (beat both baselines).

## Virgin table (LL@8.5)

| arm / baseline | LL | calibration pp ± SE |
|---|---:|---:|
| Gate Zero | 0.693940 | −0.886 ± 3.264 |
| X7 | 0.693940 | −0.886 ± 3.264 |
| league base rate | 0.726897 | |
| naive trailing-10 | 0.734003 | |

X7 ≡ Gate Zero on the virgin: the virgin parameter fit (train
through 2024/2025) selected beta = 0 for both arms and gamma = 0
(r = 1.1014, fit_n = 942) — the territorial multiplier fitted to
zero, so the two arms produce identical virgin predictions. In
dev, per-season fits did select nonzero X7 betas in the later
seasons (hence the dev gap).

## Gate arithmetic

- Gate Zero leg (i): **PASS** — 0.693940 ≤ Gate Zero's own and
  ≤ best baseline 0.726897.
- Gate Zero leg (ii): **clean PASS** — |−0.886| pp ≤ 1.0 pp.
- Gate Zero leg (iii): exempt.
- X7 leg (i): PASS (tie with Gate Zero, ≤ baselines); leg (ii):
  clean PASS (same numbers); leg (iii): PASS (dev LL ≤ Gate
  Zero in 3/3 seasons, one tie).
- Both-pass rule: both arms pass; virgin LLs tie → the simpler
  arm ships: **Gate Zero**.

C-GR verdict: **PASS (clean) — Gate Zero ships.**

Ships: fitted params `engine/corners/fitted_params_virgin.json`
(gamma 0.0, r 1.1014, beta [0.0, 0.0]) and virgin predictions
`predictions/c_gr_virgin_predictions.csv` (n=236; FT ladder
6.5–11.5, 1H/2H presentation via frozen corners constant 0.4862).
Verification: coordinator recomputed the virgin LL and
calibration from the shipped predictions CSV independently —
LL 0.693940, calibration −0.886 pp, exact match.
