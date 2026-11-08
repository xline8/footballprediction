# T-NO Verdict — NO-Eliteserien total-shots model

Date: 2026-11-09. Branch `build/no-eliteserien`. Prereg:
`league/NO-Eliteserien/prereg/PREREG_T_NO.md` (commit 48330b5).
Provenance as in the prereg: built ahead of the top-5 prospective
verdict under the T-J1 user order; that trial is untouched.
Engine: `league/NO-Eliteserien/engine/total_shots/` (J1 shots engine
seed via AT). Numbers from the coordinator's own runs.
Predictions-only scope.

## Verdict: PASS (calibration PROVISIONAL) — arm A (v1 pattern) SHIPS.

Arm A passes the dev gate — narrowly, by 0.00015 LL against the
naive baseline — while arm C (E9 trailing-r) fails it against the
same baseline and is not read on the virgin. On the virgin window
arm A beats both baselines clearly (0.6198 vs naive 0.6484) and its
calibration breach (−2.54pp) is within 1 SE (3.00pp): PROVISIONAL
PASS. The shipped predictions CSV is arm A's. Norway's shots
dispersion (1.54, the program's highest league reading) did *not*
make the trailing-r mechanism the winner here — C never got to the
virgin, on a dev gate it lost outright.

## Dev results (tuning 2022; gate pool 2023+2024, n=480)

LL@26.5, gate pool pooled:

| Method | LL@26.5 |
|---|---|
| Arm A (v1 pattern) | **0.6306** |
| Arm C (E9 trailing-r) | 0.6314 |
| League base rate | 0.6926 |
| Naive trailing-10 | 0.6308 |

Dev gate (gate-pool LL beats BOTH baselines): A PASS
(0.63062 < 0.63077 naive, by 0.00015 — the thinnest dev pass in this
league's build), C FAIL (0.63137 > 0.63077). Fitted: lambda 100,
r_A 75.66, level cell (hl 30, s 1.0, k 20).

## Virgin results (season 2025, n=240, read once, arm A only)

Actual over-26.5 rate 45.42%; mean total shots 26.10.

| Method | LL@26.5 | Mean P(over 26.5) | Calib diff | Calib SE |
|---|---|---|---|---|
| Arm A | 0.6198 | 42.88% | −2.54pp | 3.00pp |
| League base rate | 0.6905 | 44.89% | −0.53pp | 3.22pp |
| Naive t-10 | 0.6484 | 42.29% | −3.13pp | 3.08pp |

## Per-leg verdicts

| Leg | Arm A | Arm C |
|---|---|---|
| Dev gate (gate pool) | PASS | FAIL (0.6314 > naive 0.6308) |
| Virgin (i) LL ≤ best baseline (0.6484) | PASS (0.6198) | not read |
| Virgin (ii) calibration ≤1.0pp (breach ≤1 SE = provisional) | PROVISIONAL PASS (breach 1.54pp ≤ SE 3.00pp) | not read |
| Virgin (iii) sign check | n/a (reference arm) | moot (dev-dead) |
| **Overall** | **PASS (PROVISIONAL) — SHIPS** | **FAIL** |

## Verification notes
- Coordinator fix in this engine: the implementer's port had moved
  the cell-selection score line inside the match loop, so the dev
  run died with a ZeroDivisionError on the first non-tuning row —
  caught on diff audit against AT, fixed by restoring the reference
  indentation, and the dev run then completed in the coordinator's
  hands (numbers above are from that run and the subsequent virgin
  run, both coordinator-executed).
- Predictions CSV halves recomputed for a sample row: 1H P(over
  11.5) matches NB(0.465·exp_total, r_A=75.66) to 6 decimals.
