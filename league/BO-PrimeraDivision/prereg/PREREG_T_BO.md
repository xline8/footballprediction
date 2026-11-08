# Pre-registration — T-BO (BO-PrimeraDivision total shots)

Frozen: 2026-11-10, before any fitting. Branch `build/bo-primera`.
Design authority: `analysis/MODEL_DESIGN.md` (T-BO); features per
`analysis/FEATURES.md` (X5 adopted; X4/X6 DROPPED — no shotmap);
evidence per `analysis/EDA.md` (total-shots-for split-half r=.463).
Reference: the shots family (`experiments/` + `league/J1/engine/total_shots/`):
v1 pattern (ratings + NB + naive ensemble), v2 (+ level layer), E9
(NB r from a trailing window) — the T-family pattern as in
`league/PY-DivisionProfesional/prereg/PREREG_T_PY.md`. The top-5
prospective v2-vs-E9 trial is untouched and neither result
contaminates the other (different corpus, different virgin window,
no shared fitting).

## Data and windows (measured before freezing)

Source: `league/BO-PrimeraDivision/data/bo_matches.csv`.
Target: `y = total_shots_home + total_shots_away` (stats feed,
present 2025+ only). Dev-era mean 29.85 → **primary line 29.5**
(secondary reporting lines 28.5/30.5 as in the reference harness).

- Seed (training only): 2025 rounds 1–10 (n = 80).
- Dev eval blocks: 2025 rounds 11–30 in four expanding 5-round blocks
  (train on all prior 2025 rounds; n = 160 scored).
- **Virgin: 2026 regular, TRANSITIONAL (n = 199 played at pull;
  season in progress, rounds 1–25)** — read ONCE, only for arms
  passing the dev gate, after dev results freeze. The season-end
  confirmatory read is outstanding and noted in the verdict.
- The harness's dev mode must not read 2026 rows.

## Arms

1. **A (v1)** — ratings + NB + naive trailing-10 ensemble, the
   v1 pattern.
2. **B (v2)** — A plus the level layer.
3. **C (E9)** — NB dispersion r from a trailing window (single-league
   analogue: league-level trailing r), otherwise the v1 pattern.

Baselines: league base rate at 29.5 (pooled stats-era rate strictly
prior to the scored block) and naive trailing-10 (team trailing-10
total-shots for/against means, reference-harness definition).

## GATE LEGS (verbatim, frozen)

Dev gate — pooled dev LL@29.5 of an arm must beat BOTH baselines, else the arm is dead. Virgin legs — (i) LL leg: arm's virgin LL@29.5 ≤ the best other arm's AND ≤ both baselines' (for arm A, ≤ Gate-Zero-equivalent: the v1 arm is the reference; B/C compare against A); (ii) calibration leg: |mean predicted P(over 29.5) − actual over-rate| ≤ 1.0pp clean PASS; a breach within 1 SE of the boundary is recorded PROVISIONAL PASS, beyond it FAIL (SE = sd(p_i − y_i)/√n); (iii) per-block sign check on dev (arm LL ≤ arm-A LL in at least half the dev blocks) for arms B and C. Both-pass rule: if several arms pass all legs, the lower virgin LL ships; if only one passes, it ships; if none passes, T-BO verdict is FAIL and nothing ships.

Variant arms require leg (iii); arm A is exempt. Ties go to the
simpler arm (A before B before C). If arm A fails its own dev gate,
variants are moot, verdict FAIL, virgin NOT read.

## Outputs

Engine `league/BO-PrimeraDivision/engine/total_shots/` (+ README);
`results_dev.json`, `results_virgin.json`, `fitted_params_virgin.json`;
on PASS, virgin predictions
`league/BO-PrimeraDivision/predictions/t_bo_virgin_predictions.csv`
(FT + halves via the frozen total-shots constant 0.4633, presentation
only). Verdict: `league/BO-PrimeraDivision/reports/T_BO_VERDICT.md`.
Production code untouched. No push. No merge.
