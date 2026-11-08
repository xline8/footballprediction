# Verdict — T-VE

**FAIL.** A, B, and C pass DEV and are read on transitional 2026 Clausura (scored n=90), but no arm survives the virgin gates.

Dev LL@24.5 (R1–7 / R8–13 / pooled): A `0.732308 / 0.626898 / 0.683657`, B `0.727227 / 0.631001 / 0.682815`, C `0.732648 / 0.626324 / 0.683576`; base `0.708942`, naive `0.694526`. All pass the dev gate. Sign leg (at least half of 2 dev blocks = ≥1): B 1/2 PASS; C 1/2 PASS; A exempt.

| arm/baseline | virgin LL@24.5 | calibration actual−pred (SE) | legs i/ii/iii |
|---|---:|---:|---|
| A | 0.631348 | +19.812pp (4.504) | FAIL/FAIL/PASS |
| B | 0.602212 | +15.460pp (4.524) | PASS/FAIL/PASS |
| C | 0.633549 | +20.145pp (4.500) | FAIL/FAIL/PASS |
| league base | 0.654962 | — | — |
| naive | 0.616473 | — | — |

All calibration breaches exceed 1pp+SE, so they are FAIL rather than provisional. B has the lowest virgin LL and beats both baselines, but fails calibration; nothing ships. Scored n=90, not 91, because match 1000018666 has `stats: None`. Season-end confirmatory read remains outstanding. Frozen halves: 0.4662/0.5338.
