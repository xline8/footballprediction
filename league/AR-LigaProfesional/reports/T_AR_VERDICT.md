# T-AR Verdict — Liga Profesional total shots model

Date: 2026-11-09. Branch `build/ar-liga`. Prereg:
`league/AR-LigaProfesional/prereg/PREREG_T_AR.md` (commit 7169cb5,
frozen before any fitting). Engine:
`league/AR-LigaProfesional/engine/total_shots/`. Implementation
by Codex (gpt-5.6-luna) under the two-agent flow; all numbers
below were reproduced by the coordinator's own reruns, the
pooled dev figures were re-derived from the per-block metrics,
and the shipped-fallback arm's virgin calibration was recomputed
independently from the predictions CSV (see Verification notes).

Provenance (as registered): this candidate's family is under a
frozen prospective trial on the top-5 (v2 + E9 challenger,
verdict not reached). T-AR was built under the program's standing
order on this corpus only; the top-5 trial is untouched.

## Verdict: FAIL — all three arms pass dev and fail both virgin legs

All three arms beat both baselines on the pooled dev gate and are
read on the virgin window. The virgin block ran extremely hot on
shots (mean 26.75 vs dev 24.15; actual over-23.5 rate 69.58%):
the naive trailing-10 baseline adapted fastest and posted the
best virgin LL (0.5982), so every arm fails virgin leg (i); and
every arm under-predicts the level by 7.5–10.5pp, so every arm
fails the calibration leg (ii) far beyond 1 SE. Nothing ships.
The virgin predictions CSV on file is the Arm A fallback product,
labelled `arm = A`.

## Dev results (per-match walk-forward, scored blocks 2022 – 2026 - Apertura, n = 1,854)

LL@23.5, pooled over the six scored blocks (the prereg pool):

| Arm A (v1) | Arm B (v2 level layer) | Arm C (E9 trailing-r) | League base rate | Naive t-10 |
|---|---|---|---|---|
| 0.6698 | 0.6701 | 0.6695 | 0.6953 | 0.6790 |

Dev gate (pooled LL@23.5 beats BOTH baselines): A **PASS**,
B **PASS**, C **PASS**. All three arms were therefore read on
the virgin window. (Frozen tuning, for the record: ridge
λ = 100 selected on the 2022 tuning block at the family's
internal tuning line; Arm A MoM NB r = 104.48; Arm B level cell
(120, 0.5, 50) — all selected on pre-dev-gate data only, exactly
as the family design prescribes.)

## Virgin results (block "2026 - Clausura", n = 240, read once after dev froze)

Actual over-23.5 rate 69.58%; mean total shots 26.75.

| Arm | LL@23.5 | Mean P(over 23.5) | Calib diff | Calib SE |
|---|---|---|---|---|
| A (v1) | 0.6153 | 59.70% | −9.89pp | 2.91pp |
| B (v2 level layer) | 0.6072 | 62.04% | −7.54pp | 2.91pp |
| C (E9 trailing-r) | 0.6187 | 59.10% | −10.48pp | 2.91pp |
| League base rate (baseline) | 0.6568 | — | — | — |
| Naive t-10 (baseline) | **0.5982** | — | — | — |

## Per-leg verdicts

| Leg | A | B | C |
|---|---|---|---|
| Dev gate | PASS | PASS | PASS |
| Virgin (i) LL ≤ Arm A (0.6153) and ≤ best baseline (0.5982) | FAIL (0.6153 > 0.5982) | FAIL (0.6072 > 0.5982) | FAIL (0.6187 > both) |
| Virgin (ii) calibration ≤1.0pp (breach ≤1 SE = provisional) | FAIL (breach 8.89pp > SE 2.91pp) | FAIL (6.54 > 2.91) | FAIL (9.48 > 2.91) |
| Virgin (iii) dev sign check vs Arm A (≥3 of 6 blocks) | n/a | FAIL (1/6 blocks) | PASS (5/6 blocks) |
| **Overall** | **FAIL** | **FAIL** | **FAIL** |

Reading: this is the level-shift failure in its purest form in
this league — a +2.6 shots/match jump in the virgin block that
no decayed-level architecture in the family priced, while the
plain trailing-10 baseline, with its 10-match memory, got most
of the way there. Arm B's level layer helped (+2.3pp of
calibration recovered vs A) and posted the best arm LL, but it
had already failed the dev sign check (1/6) and still misses
calibration by more than 2 SE. Arm C's trailing-r mechanism —
the program's one variant win elsewhere (T-DK) — is worst here:
the virgin block's problem was level, not dispersion.

## Verification notes (coordinator, independent of Codex)

- Full harness rerun (dev + virgin) reproduces every dev and
  virgin number exactly.
- The harness JSON's protocol block carries a stale
  `gate_pool: ["2022","2023","2024"]` label inherited from the
  three-scored-season ports. The gate the code actually computes
  (and the one applied above) pools **all six scored blocks**:
  the coordinator re-derived the pooled LL@23.5 for every arm
  and baseline from the per-block metrics (n-weighted) and
  reproduced the stored pooled values to 4dp (A 0.6698, B
  0.6701, C 0.6695, league 0.6953, naive 0.6790). The label is
  wrong; the arithmetic is the prereg's.
- Independent recompute from the predictions CSV (Arm A
  fallback): LL@23.5 0.6153, calibration −9.89pp, SE 2.91pp,
  actual over-rate 69.58% — identical to the harness.
- Virgin isolation confirmed: the dev loader asserts the virgin
  block is absent from the dev row set (counts asserted per
  block: 325/378/378/378/240/240/240).
- Cosmetic port leftovers recorded, none affecting any number:
  the tuning table is keyed `lambda_logloss_24_5` (the family's
  internal key name) while the AR tuning computation runs at
  23.5, and results_dev.csv's line columns retain the NL
  ll_25_5/26_5/27_5 headers while carrying the 22.5/23.5/24.5
  values. The JSON files govern.
