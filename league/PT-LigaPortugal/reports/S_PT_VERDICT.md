# S-PT Verdict — Liga Portugal shots-on-target model

Date: 2026-11-09. Branch `build/pt-liga`. Prereg:
`league/PT-LigaPortugal/prereg/PREREG_S_PT.md` (dc457f5, frozen
before fitting). Engine: `league/PT-LigaPortugal/engine/sot/`.

## Verdict: FAIL — nothing ships (by 0.0019 log-loss)

Gate Zero passes the dev gate and its virgin calibration is a
clean pass (−0.98pp), but on the virgin window the naive
trailing-10 baseline edges it on the primary line: LL@8.5 0.6734
vs the model's 0.6753. Virgin leg (i) requires ≤ best baseline.
The gate is mechanical; the margin is tiny and recorded as such.

## Dev results (pooled n=1,224, LL@8.5)

| Arm / baseline | LL@8.5 |
|---|---|
| Gate Zero | 0.6763 |
| X4 (xG/shot tilt) | 0.7040 |
| X6 (xGOT tilt, era) | 0.6826 |
| League base rate | 0.6917 |
| Naive trailing-10 | 0.6809 |

Dev gate (beat BOTH baselines): Gate Zero PASS; X4 FAIL; X6 FAIL
(beats the base rate, loses to naive). X6 was identical to Gate
Zero in the first three dev seasons by construction (its era
guard leaves the tilt inactive until the 2024/2025 era enters the
training window) and actively hurt in 2025/2026 (0.6984 vs Gate
Zero's 0.6734) — the EDA trait (r=0.59) did not survive contact
with the gated arm. Only Gate Zero read the virgin.

## Virgin results (2026/2027, transitional, n=98)

| Arm / baseline | LL@8.5 | Mean P(over) | Actual | Calib |
|---|---|---|---|---|
| Gate Zero | 0.6753 | 41.9% | 42.9% | −0.98pp (SE 4.96) |
| League base rate | 0.6832 | 44.0% | 42.9% | — |
| Naive trailing-10 | 0.6734 | 39.4% | 42.9% | — |

Legs: (i) FAIL (0.6753 > naive 0.6734); (ii) clean PASS;
(iii) n/a. **Overall: FAIL.** Virgin predictions on file are Gate
Zero's, labelled (`predictions/s_pt_virgin_predictions.csv`).

## Verification notes

Codex's first SOT runner was fabricated (league-mean predictions,
hardcoded arm factors, copied baselines) and was rejected; the
repaired engine was then fixed by the coordinator (it never
accumulated shots-against — SOT-for was used as the against rate)
and a Gate Zero mu for the first 2024/2025 match was recomputed by
hand from the CSV: 8.743888 vs the engine's 8.743888.
