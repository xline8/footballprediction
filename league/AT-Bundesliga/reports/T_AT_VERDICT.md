# T-AT Verdict — AT-Bundesliga total-shots model

Date: 2026-11-09. Branch `build/at-bundesliga`. Prereg:
`league/AT-Bundesliga/prereg/PREREG_T_AT.md` (commit c6f6cc1),
including its provenance note (built ahead of the top-5 prospective
verdict by user order, as T-J1 was; that trial is untouched).
Engine: `league/AT-Bundesliga/engine/total_shots/` (J1 seed, arms
A and C only). Numbers from the coordinator's own runs.

## Verdict: FAIL — both arms fail both virgin legs. Nothing ships.

Both arms pass the dev gate (gate pool 2023/2024 + 2024/2025). On
the virgin window, naive trailing-10 beats both arms on LL and both
over-predict the over-24.5 rate by ~6pp — the same cold-season level
miss as S-AT and C-AT. The predictions CSV on file is arm A,
labelled, per the prereg fallback.

## Dev results (tuning season 2022/2023; gate pool 2023/2024 + 2024/2025, n=390)

LL@24.5:

| Scope | n | Arm A (v1) | Arm C (E9) | League base | Naive t-10 |
|---|---|---|---|---|---|
| 2023/2024 | 195 | 0.6826 | 0.6823 | 0.6912 | 0.6907 |
| 2024/2025 | 195 | 0.6934 | 0.6927 | 0.6933 | 0.7083 |
| **Gate pool** | 390 | **0.6880** | **0.6875** | 0.6922 | 0.6995 |

Dev gate (gate-pool LL beats BOTH baselines): A PASS, C PASS.
Sign check (leg iii, gate-pool seasons): C ≤ A in 2/2 — PASS.

## Virgin results (season 2025/2026, n=195, read once after dev froze)

Actual over-24.5 rate 42.56%; mean total shots 24.36.

| Arm | LL@24.5 | Mean P(over 24.5) | Calib diff | Calib SE |
|---|---|---|---|---|
| A (v1) | 0.6317 | 48.57% | +6.01pp | 3.33pp |
| C (E9) | 0.6334 | 48.29% | +5.72pp | 3.34pp |
| League base | 0.6902 | 48.58% | +6.01pp | — |
| Naive t-10 | 0.6225 | 48.46% | +5.89pp | — |

## Per-leg verdicts

| Leg | Arm A | Arm C |
|---|---|---|
| Dev gate (gate pool) | PASS | PASS |
| Virgin (i) LL ≤ arm A (0.6317) and ≤ best baseline (0.6225) | FAIL (0.6317 > 0.6225) | FAIL (0.6334) |
| Virgin (ii) calibration ≤1.0pp (breach ≤1 SE = provisional) | FAIL (breach 5.01pp > SE 3.33pp) | FAIL (breach 4.72pp > SE 3.34pp) |
| Virgin (iii) sign check | n/a | PASS (2/2) |
| **Overall** | **FAIL** | **FAIL** |

The E9 trailing-r mechanism (C) was the better dev arm by a hair
and the worse virgin arm by a hair — noise-level differences both
ways; the decisive fact is the level miss both arms share with
every other count market in this league's virgin season.

## Verification notes
- Coordinator verified the adapted runner's protocol block (dev
  seasons n=195 each, gate pool n=390, arms A/C only, no B in
  results) and ran the virgin step. Virgin isolation: the dev
  loader asserts it never sees 2025/2026 or 2026/2027.
