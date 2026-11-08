# VE-PrimeraDivision — DEV summary (2026-11-10)

Only preregistered DEV windows were read. No 2025/2026 Clausura virgin rows were loaded. Goal climatology is the required baseline; the other markets use the league base-rate and naive trailing-10 baselines.

| candidate | arm | pooled dev LL | base-rate / climatology | naive | dev gate |
|---|---|---:|---:|---:|---|
| G-VE (1X2) | Gate Zero | 1.072023 | 1.079346 | — | **PASS** |
| G-VE (RPS) | Gate Zero | 0.218352 | 0.220976 | — | **PASS** |
| G-VE (OU2.5) | Gate Zero | 0.675617 | 0.686472 | — | **PASS** |
| G-VE (1X2) | SHRINK | 1.072023 | 1.079346 | — | **PASS** |
| G-VE (RPS) | SHRINK | 0.218352 | 0.220976 | — | **PASS** |
| G-VE (OU2.5) | SHRINK | 0.675617 | 0.686472 | — | **PASS** |
| S-VE (8.5) | GZ | 0.659673 | 0.655479 | 0.669418 | **FAIL** (base-rate leg) |
| S-VE (8.5) | RS | 0.658106 | 0.655479 | 0.669418 | **FAIL** (base-rate leg) |
| C-VE (8.5) | Gate Zero | 0.679629 | 0.729793 | 0.730758 | **PASS** |
| K-VE (6.5) | Gate Zero | 0.687204 | 0.686002 | 0.684814 | **FAIL** (both baseline legs) |
| T-VE (24.5) | A (v1) | 0.683657 | 0.708942 | 0.694526 | **PASS** |
| T-VE (24.5) | B (v2) | 0.682815 | 0.708942 | 0.694526 | **PASS** |
| T-VE (24.5) | C (E9) | 0.683576 | 0.708942 | 0.694526 | **PASS** |

Block sign-check values are retained in each market’s `results_dev.json`: G-VE 1X2 model LL is 1.065747 / 1.079264 for 2023 / 2024; S-VE GZ is 0.662220 / 0.656701 and RS is 0.659961 / 0.655941 for R1–7 / R8–13; T-VE A/B/C are 0.732308/0.626898, 0.727227/0.631001, and 0.732648/0.626324.

## Verification fixes (coordinator review, before commit)

- Corners: the beta grid in `fit_params` was selected by binary LL at
  9.5 (copied from BO/J1, whose primary line is 9.5). Corrected to the
  VE primary 8.5 and the dev re-run: pooled model LL 0.672004 →
  0.679629 (R8–13 0.686663 → 0.703182); the PASS stands against both
  baselines and against the independently recomputed Bernoulli base
  rate (0.6974) and an independent trailing-10 NB naive (0.7055).
- Total shots runner: BO leftovers fixed before any virgin run —
  predictions filename `t_bo_…` → `t_ve_virgin_predictions.csv`,
  prediction field labels 29.5/28.5/30.5/31.5 → 24.5/23.5/25.5,
  HALF .4633 (BO) → .4662 (VE frozen constant), virgin leg (iii)
  `>= 2` → `>= len(DEV)/2` (BO's literal 2 was its half of 4 blocks;
  VE has 2 blocks, so the prereg's "at least half" is 1). Dev numbers
  are unchanged by these fixes (they touch only the virgin path).
- SOT: stale "BO primary line 11.5" comment corrected to VE 8.5.
- Independent recomputation (coordinator, straight from the CSV):
  goals climatology exact (1X2 1.077163/1.081866, RPS
  0.221770/0.220059, OU 0.685820/0.687224); S-VE base rate exact
  (0.655479); SHRINK is vacuous (2023 block: two entrants with 0 prior
  matches, none with 1–5; 2024: none with <6) — recorded, not
  re-designed. T-VE λ tuning on the seed+dev rows and the level-cell
  pick on the first dev block are the inherited BO/J1 pattern, kept
  as ported. Cards NB r hits the 500 cap for all three kinds
  (underdispersed yellows: var 4.4 < mean 6.2 in the seed) — the
  BO-port estimator behaving as designed.

## Virgin eligibility

May be read next, after DEV freeze: G-VE Gate Zero and SHRINK; C-VE Gate Zero; T-VE A, B, and C. Must not be read: S-VE GZ/RS and K-VE Gate Zero, because their DEV gates failed. This build writes no virgin results, fitted virgin parameters, predictions, or verdict files.
