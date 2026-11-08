# Verdict — S-COA (Colombia Primera A shots on target) — **PROVISIONAL PASS** (Gate Zero ships)

Date: 2026-11-09. Branch `build/co-primeraa`. Prereg:
`league/CO-PrimeraA/prereg/PREREG_S_COA.md` (frozen in commit
3f57f1c before any fitting). Arms: Gate Zero (v5 pattern, ratio
prior 200), RS (ratio prior 20,000). Primary line 7.5. Dev:
chronological walk-forward, seed 2021-Ap+Cl, evaluation
2022-Ap…2025-Cl (n = 1,787 scored). Virgin: 2026 - Apertura
(n = 204, complete), read ONCE for both dev-passing arms.

## Dev results (coordinator-verified)

Pooled dev LL @7.5 (n = 1,787):

| arm / baseline | LL@7.5 |
|---|---|
| Gate Zero | **0.6851** |
| RS | 0.6855 |
| league base rate | 0.7194 |
| naive trailing-10 | 0.6962 |

Both arms beat both baselines → both pass the dev gate. RS is
slightly WORSE than Gate Zero on dev in this league (the harder
ratio shrinkage that won in AU/SA/PY does not pay here — the
on-target-rate trait is strong, r = 0.774, so the production prior
is already near-right).

## Virgin results (n = 204)

| arm | LL@7.5 | calibration (actual − predicted) | SE | legs |
|---|---|---|---|---|
| Gate Zero | **0.6527** | **+2.66pp** | 3.36pp | (i) ✓ (ii) PROVISIONAL (iii) exempt |
| RS | 0.6542 | +2.69pp | 3.37pp | (i) ✗ (ii) PROVISIONAL (iii) ✗ |
| league base rate | 0.6778 | — | — | — |
| naive trailing-10 | 0.6599 | — | — | — |

- Leg (i): Gate Zero 0.6527 ≤ Gate Zero (itself), ≤ league
  0.6778, ≤ naive 0.6599 ✓. RS 0.6542 > Gate Zero ✗.
- Leg (ii): Gate Zero's breach is +2.66pp (the virgin runs hot:
  actual over-rate 60.3% vs mean predicted 57.6% — the virgin's SOT
  level, 8.49/match, is the highest of any tournament). Breach
  > 1.0pp but within 1 SE of the boundary (2.66 ≤ 1.0 + 3.36) →
  **PROVISIONAL PASS**. RS likewise provisional on (ii) but already
  out on (i) and (iii) (RS ≤ GZ in only a minority of dev blocks).
- Both-pass rule does not trigger (only Gate Zero passes);
  **Gate Zero ships, verdict PROVISIONAL PASS**.

## Verification performed

- `model.py` diffed against the PY reference port: identical.
- Coordinator reproduced the virgin GZ LL (0.652689) and the
  calibration (+2.66pp, SE 3.36pp) through an independent driver
  script — exact match.
- **Defect found and fixed (coordinator):** the PY reference
  harness computed its virgin "naive" baseline from the MODEL's
  probabilities (a mislabel inherited by the port — the file's
  naive entry was bit-identical to Gate Zero). The harness now
  scores the naive baseline from `naive_probs`. True naive virgin
  LL = 0.6599, independently recomputed to 6 dp before the fix;
  leg (i) holds against the true baseline and the verdict is
  unchanged (the mislabelled comparison was the stricter one).
  The fix is the engine's only divergence from the PY port and is
  recorded here per the design's divergence rule.
- Virgin predictions CSV: 204 rows, shipped arm GZ, halves via the
  frozen constant 0.4862 (presentation only).

## What ships

Gate Zero: `engine/sot/fitted_params_virgin.json` +
`predictions/s_coa_virgin_predictions.csv` (force-added). The
market joins the daily runner as a PROVISIONAL pass.
