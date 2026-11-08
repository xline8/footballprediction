# Verdict — S-PE (Peru Liga 1 shots on target) — **PASS (provisional)**, shipped arm **RS**

Date: 2026-11-10. Branch `build/pe-liga1`. Prereg:
`league/PE-Liga1/prereg/PREREG_S_PE.md` (frozen in commit 2ca0c6f
before any fitting). Arms: Gate Zero (v5 pattern, ratio prior
200), RS (ratio prior 20,000). Primary line 8.5. Dev: seed 2021
blocks, evaluation 2022 - Apertura … 2024 - Clausura (890 scored
of 982 — see the n note below). Virgin: calendar 2025, read ONCE
(280 scored of 323).

## Dev results (pooled LL@8.5, n = 890)

| arm / baseline | LL@8.5 |
|---|---|
| Gate Zero | 0.695761 |
| RS | **0.695426** |
| league base rate (harness) | 0.727443 |
| naive trailing-10 | 0.708491 |

Per-block LL@8.5 (Gate Zero / RS): 2022-Ap 0.715226 / 0.715527;
2022-Cl 0.690860 / 0.689996; 2023-Ap 0.701352 / 0.700712;
2023-Cl 0.693894 / 0.692199; 2024-Ap 0.674807 / 0.677281;
2024-Cl 0.697786 / 0.695888.

**Dev gate: both arms beat BOTH baselines — PASS.** Robustness
check (coordinator): the prereg text also admits a stricter
reading of the league baseline — a constant pooled rate strictly
prior to each scored block — which the coordinator recomputed at
0.696570. Both arms beat that too (Gate Zero by only 0.0008), and
beat the naive baseline under every reading, so the dev gate
outcome does not depend on the baseline definition. (The harness
baseline itself is the reference harness's expanding prior-rate
with a zero cold start on the first dev date; the coordinator
replicated its 0.727443 exactly from the CSV.)

## Virgin results (n = 280, read once)

| arm / baseline | LL@8.5 | calibration (pred − actual) | SE |
|---|---|---|---|
| Gate Zero | 0.685803 | −3.59 pp | 2.96 pp |
| RS | **0.685554** | −3.58 pp | 2.96 pp |
| league base rate | 0.692740 | — | — |
| naive trailing-10 | 0.705508 | — | — |

Gate legs: (i) LL — both arms ≤ Gate Zero and ≤ both baselines ✓.
(ii) Calibration — |breach| 3.6 pp exceeds the 1.0 pp clean bound
but is within 1 SE of it (bound + SE = 3.96 pp) →
**PROVISIONAL PASS** for both arms. (iii) RS dev sign check: RS
LL ≤ Gate Zero in 4 of 6 dev blocks ✓.

Both arms pass all legs → the lower virgin LL ships: **RS**.

## Verification performed

- Coordinator re-ran `run_s_pe.py dev`: `results_dev.json`
  bit-identical to the Codex-produced file.
- Shipped arm recomputed from the shipped predictions CSV
  (`predictions/s_pe_virgin_predictions.csv`, 280 rows, all
  2025): LL@8.5 = 0.685554, calibration −0.0358, SE 0.0296 —
  exact match to `results_virgin.json`.
- Engine diffed against the CO-PrimeraA reference port: line
  shift to 8.5, corpus filter, unified-shots input and block
  keying are the only changes, plus a coordinator-added Gate-Zero
  dev-fail short-circuit in the virgin path (dormant here).

## Notes stated plainly

- The prereg's stated dev scored n (877) was a prose error: the
  loaders score all 890 stats rows in the dev blocks (per-block
  157/137/160/166/153/117, recorded in `results_dev.json`). The
  virgin scored n (280) is exact. No gate depends on the 877
  figure.
- The calibration leg is the weak point: the model under-prices
  the over-8.5 rate by ~3.6 pp on the virgin. It passes only
  provisionally; the 2026 confirmatory read should be watched.

## What ships

Arm **RS** (v5 pattern with the on-target ratio prior hardened
to 20,000 — effectively the league-constant ratio). Virgin
predictions: `league/PE-Liga1/predictions/
s_pe_virgin_predictions.csv` (FT + halves via the frozen SOT
constant 0.4611, presentation only). Fitted params:
`engine/sot/fitted_params_virgin.json`. S-PE verdict:
**PASS (provisional)**.
