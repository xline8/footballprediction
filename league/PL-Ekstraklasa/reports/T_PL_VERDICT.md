# T-PL verdict

Preregistration: `prereg/PREREG_T_PL.md`; virgin is 2025/2026, n=306, read once. Calibration is actual − predicted, computed explicitly as actual over-rate minus mean predicted over-rate from the two unambiguous fields.

## Dev primary-line table (LL@25.5)

| arm / baseline | LL@25.5 |
|---|---:|
| A | 0.655074 |
| B | 0.644731 |
| C | 0.653562 |
| league base rate | 0.708698 |
| naive trailing-10 | 0.660246 |

All three arms pass dev. Per-season sign check versus reference A: B 3/3; C 2/3. A is the reference arm.

## Virgin table

| arm / baseline | LL@25.5 | actual over % | mean predicted % | calibration pp ± SE |
|---|---:|---:|---:|---:|
| A | 0.637717 | 64.379 | 58.124 | +6.255 ± 2.771 |
| B | 0.638544 | 64.379 | 59.158 | +5.221 ± 2.752 |
| C | 0.636063 | 64.379 | 58.665 | +5.714 ± 2.755 |
| league base rate | 0.655563 | 64.379 | 59.889 | +4.491 ± 2.786 |
| naive trailing-10 | 0.640537 | 64.379 | 62.489 | +1.890 ± 2.711 |

The virgin shows clear T level drift: the actual over-rate is 64.379%, while the arms predict 58.124% (A), 59.158% (B), and 58.665% (C). The naive baseline is closer at 62.489%.

## Gate arithmetic

- Reference A: leg (i) **PASS** (0.637717 ≤ itself and ≤ best baseline 0.640537); leg (ii) **FAIL** (+6.255 pp > 1.0 + 2.771 pp); leg (iii) exempt.
- B: leg (i) **FAIL** (0.638544 > A 0.637717); leg (ii) **FAIL** (+5.221 pp > 1.0 + 2.752 pp); leg (iii) PASS, 3/3.
- C: leg (i) **PASS** (0.636063 ≤ A 0.637717 and ≤ best baseline); leg (ii) **FAIL** (+5.714 pp > 1.0 + 2.755 pp); leg (iii) PASS, 2/3.

No arm survives both virgin legs. T-PL verdict: **FAIL; nothing ships**. Prediction CSV: none. No virgin fitted params ship (engine/total_shots/fitted_params.json is the dev-stage file only). Verification: coordinator cross-checked results_virgin.json rate fields (actual 64.379%; mean predicted A 58.124 / B 59.158 / C 58.665; LL@25.5 A 0.637717 / B 0.638544 / C 0.636063 vs naive 0.640537) — all three arms beat the baselines on LL and still fail calibration by 4.2–5.3 pp beyond the boundary, beyond 1 SE. Note: the T harness's inherited calibration_pp field carries the BE sign (predicted − actual); every calibration figure in this verdict was computed as actual − predicted from the rate fields, per the PL prereg.
