# Pre-registration — C-PE (PE-Liga1 corners)

Frozen: 2026-11-10, before any fitting. Branch `build/pe-liga1`.
Design authority: `league/PE-Liga1/analysis/MODEL_DESIGN.md` (C-PE);
features per `analysis/FEATURES.md` (X5, X7, X9 adopted); evidence
per `analysis/EDA.md` (F1/F2/F3). Reference: production
`model_corners_v3.py` (decay-weighted base rates + rolling-5 shots
relative factors + Negative Binomial total + territorial multiplier
`exp(beta·z)` clamped to [0.70, 1.43], betas/gamma fitted on a fit
window only), ported as in `league/CO-PrimeraA/prereg/
PREREG_C_COA.md` / `league/J1/engine/corners/`.

## Data and windows (measured before freezing)

Source: `league/PE-Liga1/data/pe_liga1_matches.csv`, modelling
corpus (regular, non-awarded). Target: `y = corners_home +
corners_away` (stats feed). Dev-era mean 9.792 → **primary line
9.5** (secondary 8.5/10.5/11.5 as in the reference harness). The
rolling shots relative factors use this league's **unified** shots
target (EDA F-feed-2), the only homogeneous shots quantity.

- Seed (training only): 2021 - Fase 1 + 2021 - Fase 2 (n = 234).
- Dev eval blocks: 2022 - Apertura … 2024 - Clausura (6 blocks,
  n = 982; 877 scored — target-missing rows are never scored rows).
- **Virgin: calendar 2025 (n = 323; 280 scored)** — read ONCE, only
  for arms passing the dev gate, after dev results freeze. 2026 is
  NOT read anywhere in this build.
- The harness's dev mode must not read 2025 or 2026 rows.

## Arms

1. **Gate Zero** — the unmodified production pattern (X9 covariates:
   possession + big chances inside the territorial multiplier).
2. **X7** — Gate Zero plus the opp-box touches multiplier component
   (X7, FEATURES: touches trait for 0.666 / against 0.614, corr
   with corners 0.571), fitted exactly as the reference X7 arm
   fits its beta (grid on the fit window only; β = 0 collapses X7
   to Gate Zero numerically). Touches coverage is rich-era only
   (zero in every dev Clausura block) — the reference min-presence
   rules decide where the component is active; nothing is imputed.

Shared engine, per-block hyperparameter fitting, walk-forward state
rules and the min-10-prior-matches scoring rule are exactly as in
`league/J1/prereg/PREREG_C_J1.md` / the CO-A port, with PE block
labels substituted. Baselines: league base rate at 9.5 (pooled rate
strictly prior to the scored block) and naive trailing-10
(reference-harness definition).

## GATE LEGS (verbatim, frozen)

Dev gate — pooled dev LL@9.5 of an arm must beat BOTH baselines, else the arm is dead. Virgin legs — (i) LL leg: arm's virgin LL@9.5 ≤ Gate Zero's AND ≤ both baselines'; (ii) calibration leg: |mean predicted P(over 9.5) − actual over-rate| ≤ 1.0pp clean PASS; a breach within 1 SE of the boundary is recorded PROVISIONAL PASS, beyond it FAIL (SE = sd(p_i − y_i)/√n); (iii) per-season sign check on dev (arm LL ≤ Gate Zero LL in at least half the dev seasons) for the both-pass rule. Both-pass rule: if Gate Zero and a variant both pass all legs, the lower virgin LL ships; if only one passes, it ships; if none passes, C-PE verdict is FAIL and nothing ships.

Variant arms require leg (iii); Gate Zero is exempt. Ties go to the
simpler arm (Gate Zero before X7). If Gate Zero fails its own dev
gate, variants are moot, verdict FAIL, virgin NOT read. Calibration
is reported as actual − predicted; the gate uses |breach|.

## Outputs

Engine `league/PE-Liga1/engine/corners/` (+ README);
`results_dev.json`, `results_virgin.json`, `fitted_params_virgin.json`;
on PASS, virgin predictions
`league/PE-Liga1/predictions/c_pe_virgin_predictions.csv`
(FT + halves via the frozen corners constant 0.4817, presentation only).
Verdict: `league/PE-Liga1/reports/C_PE_VERDICT.md`.
Production code untouched. No push. No merge.
