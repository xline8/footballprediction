# Pre-registration — T-VE (VE-PrimeraDivision total shots)

Frozen: 2026-11-10, before any fitting. Branch `build/ve-primera`.
Design authority: `analysis/MODEL_DESIGN.md` (T-VE); features per
`analysis/FEATURES.md` (X5 adopted; X4/X6 DROPPED — no shotmap);
evidence per `analysis/EDA.md` (total-shots-for split-half r=.558
pooled).
Reference: the shots family (`experiments/` + `league/J1/engine/total_shots/`):
v1 pattern (ratings + NB + naive ensemble), v2 (+ level layer), E9
(NB r from a trailing window) — the T-family pattern as in
`league/BO-PrimeraDivision/prereg/PREREG_T_BO.md`. The top-5
prospective v2-vs-E9 trial is untouched and neither result
contaminates the other (different corpus, different virgin window,
no shared fitting).

## Data and windows (measured before freezing)

Source: `league/VE-PrimeraDivision/data/ve_matches.csv`.
Target: `y = total_shots_home + total_shots_away` (stats feed,
present in all 343 stats-era matches). Dev-era (2026 Apertura
regular) mean 24.6374 → **primary line 24.5** (secondary reporting
lines 23.5/25.5 as in the reference harness).

- Seed (training only): 2025 Clausura regular (n = 91).
- Dev eval blocks: 2026 Apertura regular in two expanding blocks,
  rounds 1–7 (n = 49) and rounds 8–13 (n = 42); train on all prior
  stats-era regular matches; n = 91 scored.
- **Virgin: 2026 Clausura regular, TRANSITIONAL (n = 91, complete
  phase; season in progress)** — read ONCE, only for arms passing
  the dev gate, after dev results freeze. The season-end confirmatory
  read is outstanding and noted in the verdict.
  NOTE (known before the read, descriptive only): the virgin mean is
  28.40 total shots/match vs 24.64 in dev; the calibration leg is
  therefore expected to be hard, and the gate decides — the window is
  not moved because the outcome is inconvenient.
- The harness's dev mode must not read 2026 Clausura rows.

## Arms

1. **A (v1)** — ratings + NB + naive trailing-10 ensemble, the
   v1 pattern.
2. **B (v2)** — A plus the level layer.
3. **C (E9)** — NB dispersion r from a trailing window (single-league
   analogue: league-level trailing r over up to the 200 most recent
   stats-era matches — all available history when fewer; minimum 50
   trailing matches, else the arm falls back to v1's fitted r for
   that block), otherwise the v1 pattern.

Baselines: league base rate at 24.5 (pooled stats-era rate strictly
prior to the scored block) and naive trailing-10 (team trailing-10
total-shots for/against means, reference-harness definition).

## GATE LEGS (verbatim, frozen)

Dev gate — pooled dev LL@24.5 of an arm must beat BOTH baselines, else the arm is dead. Virgin legs — (i) LL leg: arm's virgin LL@24.5 ≤ the best other arm's AND ≤ both baselines' (for arm A, ≤ Gate-Zero-equivalent: the v1 arm is the reference; B/C compare against A); (ii) calibration leg: |mean predicted P(over 24.5) − actual over-rate| ≤ 1.0pp clean PASS; a breach within 1 SE of the boundary is recorded PROVISIONAL PASS, beyond it FAIL (SE = sd(p_i − y_i)/√n); (iii) per-block sign check on dev (arm LL ≤ arm-A LL in at least half the dev blocks) for arms B and C. Both-pass rule: if several arms pass all legs, the lower virgin LL ships; if only one passes, it ships; if none passes, T-VE verdict is FAIL and nothing ships.

Variant arms require leg (iii); arm A is exempt. Ties go to the
simpler arm (A before B before C). If arm A fails its own dev gate,
variants are moot, verdict FAIL, virgin NOT read.

## Outputs

Engine `league/VE-PrimeraDivision/engine/total_shots/` (+ README);
`results_dev.json`, `results_virgin.json`, `fitted_params_virgin.json`;
on PASS, virgin predictions
`league/VE-PrimeraDivision/predictions/t_ve_virgin_predictions.csv`
(FT + halves via the frozen total-shots constant 0.4662, presentation
only). Verdict: `league/VE-PrimeraDivision/reports/T_VE_VERDICT.md`.
Production code untouched. No push. No merge.
