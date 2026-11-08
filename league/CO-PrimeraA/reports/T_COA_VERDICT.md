# Verdict — T-COA (Colombia Primera A total shots) — **PASS** (clean, arm A ships)

Date: 2026-11-09. Branch `build/co-primeraa`. Prereg:
`league/CO-PrimeraA/prereg/PREREG_T_COA.md` (frozen in commit
3f57f1c before any fitting). Arms: A (v1 pattern), B (v2 level
layer), C (E9 trailing-r). Primary line 24.5, M_BAR = 25.06.
Tuned on dev: λ = 300, r_A = 101.89, level cell (30, 0.5, 20).
Dev: seed 2021-Ap+Cl, evaluation 2022-Ap…2025-Cl (n = 1,787
scored). Virgin: 2026 - Apertura (n = 204, complete), read ONCE
for all three dev-passing arms.

## Dev results (coordinator-verified)

Pooled dev LL @24.5 (n = 1,787):

| arm / baseline | LL@24.5 |
|---|---|
| A | 0.6770 |
| B | **0.6764** |
| C | 0.6772 |
| league base rate | 0.6908 |
| naive trailing-10 | 0.6806 |

All three arms beat both baselines → all pass the dev gate.

## Virgin results (n = 204)

| arm | LL@24.5 | calibration (actual − predicted) | SE | legs |
|---|---|---|---|---|
| A | 0.6593 | **+1.00pp** (+0.998) | 3.39pp | (i) ✓ (ii) CLEAN (iii) exempt |
| B | 0.6597 | +0.92pp | 3.39pp | (i) ✗ (LL > A) (ii) CLEAN (iii) ✓ |
| C | **0.6592** | +0.90pp | 3.39pp | (i) ✓ (ii) CLEAN (iii) ✗ |
| league base rate | 0.6911 | — | — | — |
| naive trailing-10 | 0.6645 | — | — | — |

- Arm A passes everything. Its calibration is clean by the
  narrowest margin in this build: actual over-rate 53.431% vs
  mean predicted 52.433% = +0.998pp against the 1.0pp boundary.
- Arm C has the lowest virgin LL (0.65915 vs A's 0.65932) but
  fails leg (iii): it beats arm A in only **3 of the 8 dev
  blocks** (needs ≥5 as registered; it also fails a ≥4 "at least
  half" reading — see the erratum below, which does not change
  this verdict).
- Arm B fails leg (i) (virgin LL above arm A's).
- Only arm A is eligible → **arm A ships, verdict PASS (clean)**.

## Erratum — dev block count in the frozen documents

The preregs and MODEL_DESIGN say "9 tournaments" for the
2022-Ap…2025-Cl dev span. The true count is **8** (four years ×
Apertura/Clausura); the pooled n = 1,788 (1,787 scored) stated
everywhere is correct. Consequences, checked arm by arm: every
leg-(iii) threshold was implemented as "≥5 blocks" (goals, SOT,
corners, total shots) or "≥3 of 5" (cards — its span genuinely
has 5 scored blocks). Under the corrected count, "≥5 of 8" is
stricter than "at least half", and no verdict in this build
changes under either reading: goals/cards virgins were never
read; SOT's RS also failed leg (i); corners' X7 satisfies ≤ in
8 of 8 blocks; total shots' C satisfies ≤ in only 3 of 8 (fails
≥4 as well as ≥5) and B in 5 of 8 (passes both, but failed leg
(i)). The frozen documents are left unedited, per prereg
discipline; this note is the correction of record.

## Verification performed

- Coordinator re-ran the full `virgin` step (dev + virgin) from
  the committed code: `results_dev.json` and `results_virgin.json`
  bit-identical (md5) to Codex's run. (A first rerun attempt was
  SIGTERM'd by VM contention before writing anything; the files
  on disk were confirmed untouched by it.)
- `model.py` diffed against the PY reference port: the ONLY
  difference is M_BAR = 25.06 (this league's frozen value).
- Per-block sign counts recomputed from `results_dev.json` by the
  coordinator (C ≤ A: 3 blocks; B ≤ A: 5 blocks) — matches the
  recorded legs.
- Calibration recomputed from the virgin file's own fields
  (actual 53.431% − mean predicted 52.433% = +0.998pp) ✓.
- Virgin predictions CSV: 204 rows, arm A, halves via the frozen
  constant 0.4850 (presentation only).

## What ships

Arm A: `engine/total_shots/fitted_params.json` +
`fitted_params_virgin.json` +
`predictions/t_coa_virgin_predictions.csv` (force-added). The
market joins the daily runner as a clean PASS.
