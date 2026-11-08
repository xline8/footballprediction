# Pre-registration — T-COA (CO-PrimeraA total shots)

Frozen: 2026-11-09, before any fitting. Branch `build/co-primeraa`.
Design authority: `league/CO-PrimeraA/analysis/MODEL_DESIGN.md`
(T-COA); features per `analysis/FEATURES.md` (X5 adopted; no xG is
dev-available to consume); evidence per `analysis/EDA.md`
(F1/F2/F3). Reference: the shots family in `experiments/` +
`league/J1/engine/total_shots/` / `league/PY-DivisionProfesional/
prereg/PREREG_T_PY.md` (v1 / v2 level layer / E9 trailing-r arms,
exactly as frozen for T-J1 and T-PY). Built ahead of the top-5
total-shots prospective verdict by the program's standing user
order; that trial is untouched.

## Data and windows (measured before freezing)

Source: `league/CO-PrimeraA/data/co_primeraa_matches.csv`.
Target: `y = total_shots_home + total_shots_away` (stats feed,
~100% from 2021). Dev-era mean 25.06 → **primary line 24.5**
(secondary 23.5/25.5/26.5 as in the reference harness). The level
layer's M_BAR is frozen at **25.06** (this league's dev pooled
mean, EDA F1 — the PY port's M_BAR = 24.9 plays the same role).

- Seed (training only): 2021 - Apertura + 2021 - Clausura (n = 411).
- Dev eval blocks: 2022 - Apertura … 2025 - Clausura (9 tournaments,
  n = 1,788; 1,787 scored — one 2022 - Apertura match has no stats
  feed and is never a scored row; target-missing rows are skipped
  by the loader, as in the PY port).
- **Virgin: 2026 - Apertura (n = 204, complete)** — read ONCE, only
  for arms passing the dev gate, after dev results freeze.
  2026 - Clausura (in progress) is NOT read anywhere in this build.
- Hyperparameters (ridge λ grid {3, 10, 30, 100, 300}, r_A by
  moments, level-layer cell grid) are tuned on the dev span exactly
  as in the reference runner (tuning uses scored dev rows only —
  the seed blocks are the tuning span's warmup, as in T-PY).

## Arms

1. **A** — v1 pattern (reference total-shots model, unmodified).
2. **B** — v2 level layer on top of A.
3. **C** — E9 trailing-r (dispersion r from the trailing window),
   on top of A.

Baselines: league base rate at 24.5 (reference runner's
`baseline_league`) and naive trailing-10 (`baseline_naive`).

## GATE LEGS (verbatim, frozen)

Dev gate — pooled dev LL@24.5 of an arm must beat BOTH baselines, else the arm is dead. Virgin legs — (i) LL leg: arm's virgin LL@24.5 ≤ arm A's AND ≤ both baselines'; (ii) calibration leg: |mean predicted P(over 24.5) − actual over-rate| ≤ 1.0pp clean PASS; a breach within 1 SE of the boundary is recorded PROVISIONAL PASS, beyond it FAIL (SE = sd(p_i − y_i)/√n); (iii) per-season sign check on dev (arm LL ≤ arm A LL in at least half the dev seasons) for the multi-pass rule. Multi-pass rule: if several arms pass all legs, the lowest virgin LL ships; if only one passes, it ships; if none passes, T-COA verdict is FAIL and nothing ships.

Variant arms B/C require leg (iii); arm A is exempt. Ties go to the
simpler arm (A before B before C). If arm A fails its own dev gate,
variants are moot, verdict FAIL, virgin NOT read. Calibration is
reported as actual − predicted; the gate uses |breach|.

## Outputs

Engine `league/CO-PrimeraA/engine/total_shots/` (+ README);
`results_dev.json`, `results_virgin.json`, `fitted_params.json`,
`fitted_params_virgin.json`; on PASS, virgin predictions
`league/CO-PrimeraA/predictions/t_coa_virgin_predictions.csv`
(FT + halves via the frozen total-shots constant 0.4850,
presentation only). Verdict:
`league/CO-PrimeraA/reports/T_COA_VERDICT.md`.
Production code untouched. No push. No merge.
