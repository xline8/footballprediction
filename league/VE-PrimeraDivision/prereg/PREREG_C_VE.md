# Pre-registration — C-VE (VE-PrimeraDivision corners)

Frozen: 2026-11-10, before any fitting. Branch `build/ve-primera`.
Design authority: `analysis/MODEL_DESIGN.md` (C-VE); features per
`analysis/FEATURES.md` (X5 adopted; X9 adopted for Gate Zero —
possession live, big-chance void at 0/288; X7 DROPPED — no box-touch
key); evidence per `analysis/EDA.md` (corners traits for/against
r=.615/.264 pooled; possession r=.655 pooled).
Reference: production `model_corners_v3` pattern (team corner ratings
+ Negative Binomial total, territorial multiplier), ported as in
`league/J1/engine/corners/` / `league/BO-PrimeraDivision/engine/corners/`.

## Data and windows (measured before freezing)

Source: `league/VE-PrimeraDivision/data/ve_matches.csv`.
Target: `y = corners_home + corners_away` (stats feed, present in
all 343 stats-era matches). Dev-era (2026 Apertura regular) mean
8.7363 → **primary line 8.5** (secondary reporting lines 7.5/9.5 as
in the reference harness).

- Seed (training only): 2025 Clausura regular (n = 91).
- Dev eval blocks: 2026 Apertura regular in two expanding blocks,
  rounds 1–7 (n = 49) and rounds 8–13 (n = 42); train on all prior
  stats-era regular matches; n = 91 scored.
- **Virgin: 2026 Clausura regular, TRANSITIONAL (n = 91, complete
  phase; season in progress)** — read ONCE, only if the (single) arm
  passes the dev gate, after dev results freeze. The season-end
  confirmatory read is outstanding and noted in the verdict.
  NOTE (known before the read, descriptive only): the virgin mean is
  9.37 corners/match vs 8.74 in dev; the calibration leg is expected
  to be hard, and the gate decides.
- The harness's dev mode must not read 2026 Clausura rows.

## Arms

1. **Gate Zero** — the unmodified corners_v3 pattern (X9 covariates:
   trailing possession for/against, min-8 rule; trailing big-chance
   rates carried as in production but constant 0 in this league, so
   they contribute nothing). Single arm by design: no variant exists
   for this candidate (X7 impossible).

Baselines: league base rate at 8.5 (pooled stats-era rate strictly
prior to the scored block) and naive trailing-10 (team trailing-10
corners for/against means, reference-harness definition).

## GATE LEGS (verbatim, frozen)

Dev gate — pooled dev LL@8.5 of Gate Zero must beat BOTH baselines, else the candidate is dead and the virgin is NOT read. Virgin legs — (i) LL leg: Gate Zero's virgin LL@8.5 ≤ both baselines'; (ii) calibration leg: |mean predicted P(over 8.5) − actual over-rate| ≤ 1.0pp clean PASS; a breach within 1 SE of the boundary is recorded PROVISIONAL PASS, beyond it FAIL (SE = sd(p_i − y_i)/√n). If both virgin legs pass, C-VE verdict is PASS (PROVISIONAL if leg (ii) is provisional, or by the transitional-virgin note) and Gate Zero ships; otherwise FAIL and nothing ships.

## Outputs

Engine `league/VE-PrimeraDivision/engine/corners/` (+ README);
`results_dev.json`, `results_virgin.json`, `fitted_params_virgin.json`;
on PASS, virgin predictions
`league/VE-PrimeraDivision/predictions/c_ve_virgin_predictions.csv`
(FT + halves via the frozen corners constant 0.4669, presentation only).
Verdict: `league/VE-PrimeraDivision/reports/C_VE_VERDICT.md`.
Production code untouched. No push. No merge.
