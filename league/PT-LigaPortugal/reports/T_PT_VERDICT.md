# T-PT Verdict — Liga Portugal total-shots model

Date: 2026-11-09. Branch `build/pt-liga`. Prereg:
`league/PT-LigaPortugal/prereg/PREREG_T_PT.md` (dc457f5, frozen
before fitting). Engine: `league/PT-LigaPortugal/engine/total_shots/`.

## Verdict: FAIL — nothing ships

Both arms pass the dev gate, then both fail the virgin LL leg
(naive trailing-10 is best on the transitional window) and the
virgin calibration leg (the partial 2026/2027 season is running
shot-hot relative to its predictions: actual over-24.5 rate
52.0% vs ~45% predicted). E9 additionally fails the frozen
per-season sign check (1/4).

## Dev results (pooled n=1,224, LL@24.5)

| Arm / baseline | LL@24.5 |
|---|---|
| Gate Zero (arm A) | 0.6733 |
| E9 (trailing-200 r) | 0.6733 |
| League base rate | 0.6947 |
| Naive trailing-10 | 0.6763 |

Dev gate: both arms PASS (beat both baselines). Sign check for
E9 (iii): LL ≤ Gate Zero in 1 of 4 dev seasons (only 2025/2026,
0.67869 vs 0.67884) → FAIL, recorded before the virgin read as
the prereg requires. Both arms read the virgin because both
passed the dev gate; leg (iii) is applied in the verdict below.

## Virgin results (2026/2027, transitional, n=98)

| Arm / baseline | LL@24.5 | Mean P(over) | Actual | Calib |
|---|---|---|---|---|
| Gate Zero | 0.6886 | 45.0% | 52.0% | −7.00pp (SE 4.98) |
| E9 | 0.6884 | 45.0% | 52.0% | −7.09pp (SE 4.98) |
| League base rate | 0.6991 | 46.2% | 52.0% | — |
| Naive trailing-10 | 0.6799 | 45.6% | 52.0% | — |

Legs: Gate Zero — (i) FAIL (0.6886 > naive 0.6799), (ii) FAIL
(7.00 > 4.98). E9 — (i) FAIL, (ii) FAIL, (iii) FAIL (1/4).
**Overall: FAIL.** Virgin predictions on file are Gate Zero's,
labelled (`predictions/t_pt_virgin_predictions.csv`).

## Verification notes

Baselines are scored with their own r_base (a coordinator fix —
Codex's repair scored them with each arm's r, which made the e9
baseline rows differ spuriously from the gate_zero ones). The
naive baseline is asserted equal to a brute-force recomputation
inside the runner on every run.
