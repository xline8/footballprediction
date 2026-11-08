# Verdict — T-PE (Peru Liga 1 total shots, unified target) — **PASS (provisional)**, shipped arm **A**

Date: 2026-11-10. Branch `build/pe-liga1`. Prereg:
`league/PE-Liga1/prereg/PREREG_T_PE.md` (frozen in commit 2ca0c6f
before any fitting). Target: the unified shots total of EDA
F-feed-2 (rich = SOT + off-target; sparse = `total_shots` key —
blocked shots excluded; the only homogeneous quantity the feed
carries). Arms: A (v1 pattern), B (v2 level layer, M_BAR frozen
at 19.727), C (E9 trailing-r). Primary line 19.5. Dev: seed 2021
blocks, evaluation 2022 - Apertura … 2024 - Clausura (890 scored
of 982). Virgin: calendar 2025, read ONCE (280 scored of 323).
Built ahead of the top-5 total-shots prospective verdict by the
programme's standing user order; that trial is untouched.

## Dev results (pooled LL@19.5, n = 890)

| arm / baseline | LL@19.5 |
|---|---|
| A | 0.672928 |
| B | **0.671551** |
| C | 0.672915 |
| league base rate | 0.699493 |
| naive trailing-10 | 0.682888 |

Per-block LL@19.5 (A / B / C): 2022-Ap 0.724794 / 0.710961 /
0.723993; 2022-Cl 0.673320 / 0.673989 / 0.673493; 2023-Ap
0.658140 / 0.660247 / 0.658312; 2023-Cl 0.664168 / 0.663277 /
0.664226; 2024-Ap 0.662755 / 0.664414 / 0.662659; 2024-Cl
0.648822 / 0.652345 / 0.649406.

**Dev gate: all three arms beat BOTH baselines — PASS.**

## Virgin results (n = 280, read once)

| arm / baseline | LL@19.5 | calibration (pred − actual) | SE |
|---|---|---|---|
| A | 0.686181 | −2.69 pp | 2.97 pp |
| B | 0.686880 | −2.45 pp | 2.97 pp |
| C | **0.685606** | −2.55 pp | 2.97 pp |
| league base rate | 0.693931 | −1.05 pp | 3.00 pp |
| naive trailing-10 | 0.700709 | −3.17 pp | 3.01 pp |

Gate legs: (i) LL ≤ arm A and ≤ both baselines — A ✓, B ✗
(0.686880 > A), C ✓ (C has the lowest virgin LL of the three).
(ii) Calibration — all three arms breach the 1.0 pp clean
bound but sit within 1 SE of it → **PROVISIONAL PASS** for
every arm. (iii) Dev sign check vs arm A — B: better in 2 of 6
blocks ✗; C: better in 2 of 6 blocks ✗. C is therefore NOT
eligible despite the lowest virgin LL; the frozen sign leg,
not the virgin ranking, decides. A alone survives all legs →
**A ships**.

## Verification performed

- Coordinator re-ran `run_t_pe.py dev`: `results_dev.json`
  bit-identical to the Codex-produced file.
- Shipped arm recomputed from the shipped predictions CSV
  (`predictions/t_pe_virgin_predictions.csv`, 280 rows, all
  2025): LL@19.5 = 0.686181, calibration −0.0269, SE 0.0297 —
  exact match; halves split ratio on the file = 0.4662, the
  frozen constant.
- Coordinator corrections before the virgin run: the ported
  virgin extraction kept only the LAST 2025 block's metrics
  (a dict-comprehension collapse) — a `virgin_pooled`
  accumulator over both blocks (the prereg's n = 280) now
  feeds the legs; the predictions field list carried CO line
  names and would have crashed on the PASS path; arm B's
  `pred_total_ft` is now level-adjusted like its probabilities
  (the gates never read that column).

## What ships

Arm **A** (v1 pattern: ridge ratings + NB + naive ensemble on
the unified target). Virgin predictions:
`league/PE-Liga1/predictions/t_pe_virgin_predictions.csv`
(FT + halves via the frozen total-shots constant 0.4662,
presentation only). Fitted params:
`engine/total_shots/fitted_params_virgin.json`. T-PE verdict:
**PASS (provisional)**.
