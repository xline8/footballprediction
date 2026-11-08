# Verdict — G-PBM (Primera B Metropolitana goals model)

**Verdict: FAIL. Nothing ships.** Gate Zero fails all three pooled dev
legs, so under the frozen prereg rule the virgin window (2026, n = 462)
was NOT read: no `results_virgin.json`, no virgin predictions, no
fitted parameters. The X2 arm fails the same legs; its per-block sign
record (3/4) is moot.

Prereg: `league/AR-PrimeraBMetropolitana/prereg/PREREG_G_PBM.md`
(frozen 2026-11-10, before any fitting). Engine:
`league/AR-PrimeraBMetropolitana/engine/goals/`. Dev results:
`engine/goals/results_dev.json` (+ `.csv`).

## Dev tables (walk-forward, scored blocks 2022–2025, n = 1,426)

| Arm | Block | n | 1X2 LL | RPS | OU2.5 LL |
|---|---:|---:|---:|---:|---:|
| Gate Zero | 2022 | 272 | 1.117084 | 0.235446 | 0.680432 |
| Climatology | 2022 | 272 | 1.084665 | 0.223237 | 0.676606 |
| Trailing-10 | 2022 | 272 | 1.113613 | 0.233255 | 0.680712 |
| Gate Zero | 2023 | 272 | 1.138409 | 0.231856 | 0.645446 |
| Climatology | 2023 | 272 | 1.109075 | 0.222274 | 0.643720 |
| Trailing-10 | 2023 | 272 | 1.102012 | 0.221000 | 0.638380 |
| Gate Zero | 2024 | 462 | 1.089286 | 0.219535 | 0.660450 |
| Climatology | 2024 | 462 | 1.084769 | 0.219379 | 0.642689 |
| Trailing-10 | 2024 | 462 | 1.083899 | 0.218703 | 0.660373 |
| Gate Zero | 2025 | 420 | 1.099449 | 0.220094 | 0.669291 |
| Climatology | 2025 | 420 | 1.087739 | 0.217234 | 0.642390 |
| Trailing-10 | 2025 | 420 | 1.111819 | 0.224842 | 0.667640 |
| **Gate Zero pooled** | — | **1,426** | **1.106952** | **0.225085** | **0.664004** |
| **Climatology pooled** | — | **1,426** | **1.090260** | **0.220036** | **0.649267** |
| **Trailing-10 pooled** | — | **1,426** | **1.101245** | **0.223725** | **0.662198** |
| X2 pooled | — | 1,426 | 1.106479 | 0.225004 | 0.662244 |

X2 per block (1X2 LL): 2022: 1.117374; 2023: 1.137944; 2024: 1.088498;
2025: 1.098824.

## Gate arithmetic (mechanical, per the prereg)

Dev gate — pooled model must beat climatology on 1X2 LL, RPS, and
OU2.5 LL (margins = climatology − model; positive passes):

- Gate Zero: LL margin −0.016691 (1.106952 vs 1.090260) **FAIL**;
  RPS margin −0.005049 (0.225085 vs 0.220036) **FAIL**;
  OU2.5 LL margin −0.014737 (0.664004 vs 0.649267) **FAIL**.
- X2: LL margin −0.016219 **FAIL**; RPS margin −0.004968 **FAIL**;
  OU2.5 LL margin −0.012977 **FAIL**.
- Leg (iii) (X2 only): X2 beats Gate Zero on 1X2 LL in 3 of 4 scored
  blocks (2023: −0.000464; 2024: −0.000788; 2025: −0.000625;
  2022: +0.000289) — passes, but moot because the dev gate fails.

Gate Zero fails its dev gate, so the frozen rule applies: the variants
are moot and the virgin is NOT read. No virgin leg is evaluated.

## What this means

The Dixon-Coles reference loses to the pooled base rates on every leg,
in every scored block on 1X2 LL, and even the naive trailing-10
baseline beats it on pooled 1X2 LL (1.101245 vs 1.106952). The X2
newcomer prior helps slightly (pooled LL 1.106479 vs 1.106952) but
nowhere near enough to clear the gate. Consistent with the EDA: team
goal traits are weak in this league (split-half r = 0.347 attack /
0.487 defence), the newcomer gaps are near zero (−0.0325 / −0.0410),
and the 17–22-team split-season format gives each fit a thin,
high-turnover training set. The failure is a property of the league's
signal, not of the implementation: the DC port was verified
independently against the J1 reference (2022 Gate Zero LL reproduced
exactly, 1.117084), climatology baselines were recomputed from the
CSV to 1e-9, and the dev harness is deterministic on re-run.

## What ships

Nothing. No G-PBM market joins the daily pipeline. The engine and dev
results stay on this branch for the record. S-PBM / C-PBM / K-PBM /
T-PBM were not buildable (no target exists in any payload) and were
never fitted.

## Notes for a future rebuild (not a rescue arm)

- The PBM harness folds leg (iii) into X2's `dev_gate_pass` flag;
  the prereg keeps (iii) as a virgin-stage both-pass condition. No
  outcome change here (X2 fails the three legs anyway); a future
  rebuild should separate the two.
- The PBM trailing-10 baseline inherits the fitted DC rho for its
  probabilities; the FEDA twin uses a fresh rho = 0 model. Baseline
  only; the gate compares against climatology.
