# Pre-registration — T-PY (PY-DivisionProfesional total shots)

Frozen: 2026-11-09, before any fitting. Branch `build/py-division`.
Design authority: `analysis/MODEL_DESIGN.md` (T-PY); features per
`analysis/FEATURES.md` (X5 adopted; no xG exists to consume);
evidence per `analysis/EDA.md` (F1/F2/F3). Reference: the shots
family in `experiments/` + `league/J1/engine/total_shots/` /
`league/KR-KLeague1/engine/total_shots/` (v1 / v2 level layer / E9
trailing-r arms, exactly as frozen for T-J1). Built ahead of the
top-5 total-shots prospective verdict by the program's standing
user order; that trial is untouched.

## Data and windows (measured before freezing)

Source: `league/PY-DivisionProfesional/data/py_matches.csv`.
Target: `y = total_shots_home + total_shots_away` (stats feed,
2025+ only). Dev-era mean 24.83 → **primary line 24.5** (secondary
23.5/25.5/26.5 as in the reference harness).

- Seed (training only): 2025 - Apertura (n = 132).
- Dev eval blocks: 2025 - Clausura + 2026 - Apertura (n = 264;
  263 scored — target-missing clásico rule, PREPROCESSING §9).
- **Virgin: 2026 - Clausura, TRANSITIONAL (n = 112 played at pull)**
  — read ONCE, only for arms passing the dev gate, after dev results
  freeze. Season-end confirmatory read outstanding (verdict notes it).
- The harness's dev mode must not read 2026 - Clausura rows.

## Arms

1. **A** — v1 pattern (reference total-shots model, unmodified).
2. **B** — v2 level layer on top of A.
3. **C** — E9 trailing-r (dispersion r from the trailing window),
   on top of A.

Baselines: league base rate at 24.5 (pooled stats-era rate strictly
prior to the scored block) and naive trailing-10.

## GATE LEGS (verbatim, frozen)

Dev gate — pooled dev LL@24.5 of an arm must beat BOTH baselines, else the arm is dead. Virgin legs — (i) LL leg: arm's virgin LL@24.5 ≤ arm A's AND ≤ both baselines'; (ii) calibration leg: |mean predicted P(over 24.5) − actual over-rate| ≤ 1.0pp clean PASS; a breach within 1 SE of the boundary is recorded PROVISIONAL PASS, beyond it FAIL (SE = sd(p_i − y_i)/√n); (iii) per-season sign check on dev (arm LL ≤ arm A LL in at least half the dev seasons) for the multi-pass rule. Multi-pass rule: if several arms pass all legs, the lowest virgin LL ships; if only one passes, it ships; if none passes, T-PY verdict is FAIL and nothing ships.

Variant arms B/C require leg (iii); arm A is exempt. Ties go to the
simpler arm (A before B before C). If arm A fails its own dev gate,
variants are moot, verdict FAIL, virgin NOT read.

## Outputs

Engine `league/PY-DivisionProfesional/engine/total_shots/` (+ README);
`results_dev.json`, `results_virgin.json`, `fitted_params_virgin.json`;
on PASS, virgin predictions
`league/PY-DivisionProfesional/predictions/t_py_virgin_predictions.csv`
(FT + halves via the frozen total-shots constant 0.465, presentation only).
Verdict: `league/PY-DivisionProfesional/reports/T_PY_VERDICT.md`.
Production code untouched. No push. No merge.
