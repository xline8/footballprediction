# Verdict — C-COA (Colombia Primera A corners) — **PASS** (clean, Gate Zero ships)

Date: 2026-11-09. Branch `build/co-primeraa`. Prereg:
`league/CO-PrimeraA/prereg/PREREG_C_COA.md` (frozen in commit
3f57f1c before any fitting). Arms: Gate Zero (production corners
v3 pattern, X9 covariates inside), X7 (opp-box touches
multiplier). Primary line 8.5. Dev: tournament-blocked
walk-forward, seed 2021-Ap+Cl, evaluation 2022-Ap…2025-Cl
(n = 1,787 scored). Virgin: 2026 - Apertura (n = 204, complete),
read ONCE for both dev-passing arms.

## Dev results (coordinator-run; see Verification)

Pooled dev LL @8.5 (n = 1,787):

| arm / baseline | LL@8.5 |
|---|---|
| Gate Zero | 0.6891 |
| X7 | **0.6879** |
| league base rate | 0.7413 |
| naive trailing-10 | 0.7366 |

Both arms beat both baselines by wide margins → both pass the dev
gate. X7's edge over Gate Zero is small and concentrated: the two
arms are identical in 6 of 9 dev blocks (the touches component is
inactive or fits β = 0 where its coverage is partial — the
2021–2023 Clausura feed quirk), and X7 is better in 2022-Ap,
2025-Ap and 2025-Cl.

## Virgin results (n = 204)

| arm | LL@8.5 | calibration (actual − predicted) | SE | legs |
|---|---|---|---|---|
| Gate Zero | **0.6923** | **−0.96pp** | 3.51pp | (i) ✓ (ii) CLEAN (iii) exempt |
| X7 | **0.6923** | −0.96pp | 3.51pp | (i) ✓ (ii) CLEAN (iii) ✓ (≤ GZ in ≥5/9 dev blocks) |
| league base rate | 0.7316 | — | — | — |
| naive trailing-10 | 0.7333 | — | — | — |

The arms are bit-identical on the virgin because the X7 arm's
virgin-fit touches beta is **β = 0.0** (fitted on the full train,
fit_n = 2,188; active share 96.1% but the grid chose zero — the
reference design's stated collapse: β = 0 ⇒ X7 = Gate Zero
numerically). Gate Zero's own virgin-fit beta is also [0.0, 0.0]
(γ = 0.15, r = 1.177): the shipped model is the base corners
model with the territorial multiplier fitted to zero on the full
train. Both arms pass all legs; the both-pass rule ties on virgin
LL (0.692294 both) → the simpler arm ships: **Gate Zero, verdict
PASS (clean)** — calibration |−0.96pp| ≤ 1.0pp.

## Verification performed

- `core.py` diffed against the PY reference port: identical except
  the docstring. All dev numbers in this verdict come from the
  coordinator's own run of the committed code (Codex's session
  died on a sandbox I/O panic mid-fit — an isolated Codex failure;
  its written code was inspected line-by-line and then run by the
  coordinator; no Codex-reported number is used anywhere).
- Virgin run reproduced after the fix below: identical LLs.
- Spot check: first virgin prediction (mu = 8.810, r = 1.177)
  hand-verified against the NB tail (P(over 8.5) = 0.510 ✓).
- **Defect found and fixed (coordinator):** `write_predictions`'
  field list named `p_over_7.5` while the writer produces the
  8.5/9.5/10.5 ladder — the first virgin run crashed on the first
  prediction row (results_virgin.json was already written and is
  unaffected; the predictions CSV was header-only). The field list
  now matches the produced ladder; the rerun wrote all 204 rows
  and `fitted_params_virgin.json`. The same latent mismatch exists
  in the PY reference (never exercised there — its corners virgin
  ship path did not run); recorded here as this port's only
  divergence beyond labels/constants.
- One stale season label in the virgin metrics calls ("2026 -
  Clausura" left over from the PY port) was corrected to the
  virgin season before the virgin run; it affected only a label
  string in the output, no number.

## What ships

Gate Zero: `engine/corners/fitted_params_virgin.json` +
`predictions/c_coa_virgin_predictions.csv` (force-added,
204 rows; halves via the frozen constant 0.4956, presentation
only). The market joins the daily runner as a clean PASS.
