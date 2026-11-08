# Pre-registration — C-PY (PY-DivisionProfesional corners)

Frozen: 2026-11-09, before any fitting. Branch `build/py-division`.
Design authority: `analysis/MODEL_DESIGN.md` (C-PY); features per
`analysis/FEATURES.md` (X5, X7, X9 adopted); evidence per
`analysis/EDA.md` (F1/F2/F3). Reference: production
`model_corners_v3.py` (decay-weighted base rates + rolling-5 shots
relative factors + Negative Binomial total + territorial multiplier
`exp(beta·z)` clamped to [0.70, 1.43], betas/gamma fitted on a fit
window only), ported as in `league/J1/engine/corners/` /
`league/KR-KLeague1/engine/corners/`.

## Data and windows (measured before freezing)

Source: `league/PY-DivisionProfesional/data/py_matches.csv`.
Target: `y = corners_home + corners_away` (stats feed, 2025+ only).
Dev-era mean 8.75 → **primary line 8.5** (secondary 9.5/10.5 as in
the reference harness).

- Seed (training only): 2025 - Apertura (n = 132).
- Dev eval blocks: 2025 - Clausura + 2026 - Apertura (n = 264;
  263 scored — target-missing clásico rule, PREPROCESSING §9).
- **Virgin: 2026 - Clausura, TRANSITIONAL (n = 112 played at pull)**
  — read ONCE, only for arms passing the dev gate, after dev results
  freeze. Season-end confirmatory read outstanding (verdict notes it).
- The harness's dev mode must not read 2026 - Clausura rows.

## Arms

1. **Gate Zero** — the unmodified production pattern (X9 covariates:
   possession + big chances inside the territorial multiplier).
2. **X7** — Gate Zero plus the opp-box touches multiplier component
   (X7, FEATURES: touches trait r = 0.70, corr with corners 0.389),
   fitted exactly as the reference X7 arm fits its beta (grid on the
   fit window only; β = 0 collapses X7 to Gate Zero numerically).

Shared engine, per-season hyperparameter fitting, walk-forward state
rules and the min-10-prior-matches scoring rule are exactly as in
`league/J1/prereg/PREREG_C_J1.md` / the KR port, with PY block labels
substituted. Baselines: league base rate at 8.5 (pooled stats-era
rate strictly prior to the scored block) and naive trailing-10.

## GATE LEGS (verbatim, frozen)

Dev gate — pooled dev LL@8.5 of an arm must beat BOTH baselines, else the arm is dead. Virgin legs — (i) LL leg: arm's virgin LL@8.5 ≤ Gate Zero's AND ≤ both baselines'; (ii) calibration leg: |mean predicted P(over 8.5) − actual over-rate| ≤ 1.0pp clean PASS; a breach within 1 SE of the boundary is recorded PROVISIONAL PASS, beyond it FAIL (SE = sd(p_i − y_i)/√n); (iii) per-season sign check on dev (arm LL ≤ Gate Zero LL in at least half the dev seasons) for the both-pass rule. Both-pass rule: if Gate Zero and a variant both pass all legs, the lower virgin LL ships; if only one passes, it ships; if none passes, C-PY verdict is FAIL and nothing ships.

Variant arms require leg (iii); Gate Zero is exempt. Ties go to the
simpler arm (Gate Zero before X7). If Gate Zero fails its own dev
gate, variants are moot, verdict FAIL, virgin NOT read.

## Outputs

Engine `league/PY-DivisionProfesional/engine/corners/` (+ README);
`results_dev.json`, `results_virgin.json`, `fitted_params_virgin.json`;
on PASS, virgin predictions
`league/PY-DivisionProfesional/predictions/c_py_virgin_predictions.csv`
(FT + halves via the frozen corners constant 0.492, presentation only).
Verdict: `league/PY-DivisionProfesional/reports/C_PY_VERDICT.md`.
Production code untouched. No push. No merge.
