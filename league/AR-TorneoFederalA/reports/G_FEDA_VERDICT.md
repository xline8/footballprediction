# Verdict — G-FEDA (Torneo Federal A goals model)

**Verdict: FAIL. Nothing ships.** Gate Zero beats climatology on pooled
1X2 LL and RPS but loses the OU2.5 LL leg, so the dev gate fails; under
the frozen prereg rule the virgin window (2026, n = 459) was NOT read:
no `results_virgin.json`, no virgin predictions, no fitted parameters.
The X2 arm fails the same leg; its per-block sign record (2/4) is moot.

Prereg: `league/AR-TorneoFederalA/prereg/PREREG_G_FEDA.md` (frozen
2026-11-10, before any fitting). Engine:
`league/AR-TorneoFederalA/engine/goals/`. Dev results:
`engine/goals/results_dev.json` (+ `.csv`).

## Dev tables (walk-forward, scored blocks 2022–2025, n = 2,083)

| Arm | Block | n | 1X2 LL | RPS | OU2.5 LL |
|---|---:|---:|---:|---:|---:|
| Gate Zero | 2022 | 544 | 1.036952 | 0.209797 | 0.679623 |
| X2 | 2022 | 544 | 1.038184 | 0.210191 | 0.679661 |
| Climatology | 2022 | 544 | 1.034935 | 0.208603 | 0.667228 |
| Trailing-10 | 2022 | 544 | 1.094211 | 0.229046 | 0.663192 |
| Gate Zero | 2023 | 576 | 0.978377 | 0.196220 | 0.682473 |
| X2 | 2023 | 576 | 0.978764 | 0.196265 | 0.684876 |
| Climatology | 2023 | 576 | 1.007810 | 0.204963 | 0.659060 |
| Trailing-10 | 2023 | 576 | 1.089120 | 0.233465 | 0.676860 |
| Gate Zero | 2024 | 477 | 1.009527 | 0.196375 | 0.630307 |
| X2 | 2024 | 477 | 1.007615 | 0.195639 | 0.633516 |
| Climatology | 2024 | 477 | 1.035608 | 0.204915 | 0.617756 |
| Trailing-10 | 2024 | 477 | 1.088907 | 0.223321 | 0.621355 |
| Gate Zero | 2025 | 486 | 1.040429 | 0.210647 | 0.673337 |
| X2 | 2025 | 486 | 1.039034 | 0.210144 | 0.675726 |
| Climatology | 2025 | 486 | 1.040589 | 0.212206 | 0.646339 |
| Trailing-10 | 2025 | 486 | 1.099276 | 0.230852 | 0.667337 |
| **Gate Zero pooled** | — | **2,083** | **1.015285** | **0.203167** | **0.667651** |
| **X2 pooled** | — | **2,083** | **1.014951** | **0.202997** | **0.669618** |
| **Climatology pooled** | — | **2,083** | **1.028908** | **0.207592** | **0.648767** |
| **Trailing-10 pooled** | — | **2,083** | **1.092770** | **0.229378** | **0.658358** |

## Gate arithmetic (mechanical, per the prereg)

Dev gate — pooled model must beat climatology on 1X2 LL, RPS, and
OU2.5 LL (margins = climatology − model; positive passes):

- Gate Zero: LL margin +0.013622 (1.015285 vs 1.028908) pass;
  RPS margin +0.004425 (0.203167 vs 0.207592) pass;
  OU2.5 LL margin **−0.018885** (0.667651 vs 0.648767) **FAIL**.
- X2: LL margin +0.013957 pass; RPS margin +0.004596 pass;
  OU2.5 LL margin **−0.020851 FAIL**.
- Leg (iii) (X2 only): X2 beats Gate Zero on 1X2 LL in 2 of 4 scored
  blocks (2024: −0.001912; 2025: −0.001395; 2022: +0.001232;
  2023: +0.000387) — passes, but moot because the dev gate fails.

Gate Zero fails its dev gate, so the frozen rule applies: the variants
are moot and the virgin is NOT read. No virgin leg is evaluated.

## What this means

A split verdict inside the gate: the DC model is a real improvement
over base rates for match outcomes (1X2 LL better by 0.0136 pooled,
winning 3 of 4 blocks) but its totals are systematically worse than
the base rate — Gate Zero loses the OU2.5 LL leg in ALL FOUR scored
blocks (2022: 0.679623 vs 0.667228; 2023: 0.682473 vs 0.659060;
2024: 0.630307 vs 0.617756; 2025: 0.673337 vs 0.646339). The model's
over-2.5 probabilities are miscalibrated against a league whose
over-rate swings 28–39% by season and whose second-phase format
re-sorts teams mid-season. The X2 newcomer prior is a near-no-op here
(pooled gaps +0.05535 / +0.00444; pooled LL moves by 0.0003). The
failure is specific and mechanical — the OU leg — not a coding error:
the DC port was verified independently against the J1 reference
(2022 and 2025 Gate Zero LLs reproduced exactly), climatology
baselines were recomputed from the CSV to 1e-9, and the dev harness
is deterministic on re-run.

## What ships

Nothing. No G-FEDA market joins the daily pipeline. The engine and
dev results stay on this branch for the record. S-FEDA / C-FEDA /
K-FEDA / T-FEDA were not buildable (no target exists in any payload)
and were never fitted.

## Notes for a future rebuild (not a rescue arm)

- The FEDA `dc.py` has no `over()` method and its `matrix`/`probs`
  take no rho override (unlike the J1 reference). Irrelevant to the
  dev verdict; a future virgin-capable rebuild would need the
  method restored for halves predictions.
