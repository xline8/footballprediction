# T-GR verdict

Preregistration: `prereg/PREREG_T_GR.md` (including the frozen
2021/2022 seed-season exclusion for the shots feed artefact);
virgin is 2025/2026, n=236, read once. Calibration below is
actual − predicted (the engine JSON stores the reverse sign,
predicted − actual; converted here — magnitudes identical).

## Dev (scored 2022/2023–2024/2025, n=716, LL@22.5)

| arm / baseline | pooled | 2022/23 | 2023/24 | 2024/25 |
|---|---:|---:|---:|---:|
| A (v1) | 0.684461 | 0.702401 | 0.684256 | 0.666424 |
| B (v2) | 0.683169 | 0.701575 | 0.681168 | 0.666487 |
| C (E9) | 0.684115 | 0.702215 | 0.683596 | 0.666234 |
| league base rate | 0.690642 | | | |
| naive trailing-10 | 0.698043 | | | |

All three arms pass the dev gate (beat both baselines).

## Virgin table (LL@22.5)

| arm / baseline | LL | calibration pp ± SE |
|---|---:|---:|
| A (reference) | 0.682956 | +0.123 ± 3.223 |
| B | 0.685539 | +0.511 ± 3.231 |
| C (E9) | 0.682529 | +0.638 ± 3.222 |
| league base rate | 0.684963 | |
| naive trailing-10 | 0.693670 | |

## Gate arithmetic

- A leg (i): **PASS** — 0.682956 ≤ best baseline 0.684963.
  Leg (ii): **clean PASS** (|+0.123| ≤ 1.0 pp). Leg (iii):
  reference arm, exempt-equivalent.
- B leg (i): **FAIL** — 0.685539 is not ≤ reference A's 0.682956
  (nor ≤ best baseline 0.684963). B is dead despite the best
  pooled dev LL.
- C leg (i): **PASS** — 0.682529 ≤ A's 0.682956 and ≤ 0.684963.
  Leg (ii): **clean PASS** (|+0.638| ≤ 1.0 pp). Leg (iii):
  **PASS** — dev LL ≤ A's in 3/3 seasons.
- Both-pass rule: A and C pass; the lower pooled virgin LL
  ships → **C (E9)**, 0.682529 < 0.682956.

T-GR verdict: **PASS (clean) — arm C (E9) ships.**

Ships: fitted params `engine/total_shots/fitted_params_virgin.json`
(arm C; dev-fitted lambda 300.0, r_A 139.57, level cell
[30.0, 1.0, 50.0], half split 0.4611/0.5389) and virgin predictions
`predictions/t_gr_virgin_predictions.csv` (n=236; FT ladder
21.5/22.5/23.5, 1H/2H presentation via frozen shots constant
0.4611). Verification: coordinator recomputed the virgin LL and
calibration for arm C from the shipped predictions CSV
independently — LL 0.682529, calibration +0.638 pp, exact match.
