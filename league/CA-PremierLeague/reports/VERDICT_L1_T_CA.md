# Verdict — L1-T-CA (CA-PremierLeague total shots, Lane 1)

**FAIL (dev) — the corrected arm C still fails the dev gate
against naive trailing-10; sealed window NOT read.**

Lane 1 re-entry of T-CA under `prereg/PREREG_L1_T_CA.md`
(prereg commit `d7f3cbff`, committed before any sealed access).
Cohort B (AUDIT.md §5.9): the shipped engine ran arms B/C with a
copied `M_BAR = 24.15`; this candidate re-ran the dev evaluation
with M_BAR derived from the league's own dev data via
`league/gate_lib` (`derive_level_prior` over all loaded dev-era
rows, n = 448): **M_BAR = 22.8326** (22.832589285714285 — the value
the shipped harness computed into its protocol block but never
used). Arm of record: arm C. Arms A/B and both baselines retained
as comparators.

## Dev legs — shipped (M_BAR = 24.15) vs corrected (M_BAR = 22.8326)

Pooled dev LL@22.5, n = 336 (seasons 2022–2024):

| Entity | Shipped | Corrected | vs base 0.696515 | vs naive 0.686318 |
|---|---|---|---|---|
| A (Gate Zero ref; no M_BAR) | 0.687676 | 0.687676 | ✓ | ✗ |
| B (level layer) | 0.687951 | 0.687963 | ✓ | ✗ |
| **C (arm of record, trailing-r)** | **0.687220** | **0.687304** | **✓** | **✗ by 0.0010** |

Dev gate (identical to `PREREG_T_CA`): pooled LL@22.5 must beat
BOTH baselines. Corrected arm C beats the league base rate
(0.687304 < 0.696515) and loses to naive trailing-10
(0.687304 vs 0.686318, margin 0.000986 — the shipped margin was
0.000902). The correction moved arm C by only +0.000084 LL, and in
the wrong direction: the copied constant did not decide the
original dev FAIL. Corrected arm B likewise fails (0.687963).
**Dev gate: FAIL. The candidate dies at dev, per the Lane 1
protocol; the sealed window (season 2025, n = 112) was NOT read.**

Fidelity of the corrected run: arm A and both baselines reproduce
the shipped `results_dev.json` to ≤ 8e-16 (they do not read M_BAR),
confirming the corrected harness is the shipped walk-forward with
only the M_BAR wiring changed. The dev-pass registry
(`engine/total_shots/dev_pass_registry_l1.json`) records
`L1-T-CA: dev_pass = false`; the gate_lib sealed loader therefore
refuses any sealed load for this candidate. P2 seal check on
`results_dev_l1.json`: CLEAN (no sealed-season references).

Sign check (leg iii, information at a dev death): corrected arm C
vs arm A per season — 2022 ✓ (0.679655 ≤ 0.681152), 2023 ✗
(0.693818 > 0.693462), 2024 ✗ (0.688439 > 0.688414) → 1 of 3; it
would also have failed leg (iii) had the window been read. Moot.

## P6 worst-fold block (information only, no gate change)

Worst dev season by the reference arm (A) at LL@22.5: **2023**.

| Entity | Pooled LL@22.5 (corrected) | Worst-season 2023 LL@22.5 (n = 112) |
|---|---|---|
| A | 0.6877 | 0.6935 |
| B | 0.6880 | 0.6936 |
| C | 0.6873 | 0.6938 |
| baseline_league | 0.6965 | 0.7007 |
| baseline_naive | 0.6863 | 0.6813 |

On the worst fold the naive baseline improves (0.6813) while every
arm degrades — the pooled near-miss is not one easy season's doing.

## Disposition

- Verdict: **FAIL (dev)** — final for this Lane 1 candidate.
- Sealed read: NO (deliberately unread; window stays sealed).
- Ships: nothing. No runner-join preparation.
- Artefacts: `engine/total_shots/model_l1.py`,
  `engine/total_shots/harness_l1.py`,
  `engine/total_shots/results_dev_l1.json`,
  `engine/total_shots/predictions_dev_l1.csv` (on disk),
  `engine/total_shots/dev_pass_registry_l1.json`.
- Prereg commit: `d7f3cbff` (branch `build/lane1-tca`, first
  commit, precedes any sealed access). No push, no merge.
