# Pre-registration — S-PY (PY-DivisionProfesional shots on target)

Frozen: 2026-11-09, before any fitting. Branch `build/py-division`.
Design authority: `analysis/MODEL_DESIGN.md` (S-PY); features per
`analysis/FEATURES.md` (X5 adopted; X4/X6 DROPPED — no shotmap);
evidence per `analysis/EDA.md` (F1/F2/F3). Reference: production SOT
v5 architecture (`model_sot.py`: joint Poisson ridge regression
λ = 100 + Negative Binomial r fitted + Beta-Binomial on-target ratio),
ported as in `league/J1/engine/sot/` / `league/KR-KLeague1/engine/sot/`
— **with no xG input anywhere** (none exists in this league).

## Data and windows (measured before freezing)

Source: `league/PY-DivisionProfesional/data/py_matches.csv`.
Target: `y = shotsontarget_home + shotsontarget_away` (stats feed,
present 2025+ only). Dev-era mean 8.09 → **primary line 7.5**
(secondary reporting lines 6.5/8.5/9.5 as in the reference harness).

- Seed (training only): 2025 - Apertura (n = 132).
- Dev eval blocks: 2025 - Clausura + 2026 - Apertura (n = 264;
  263 scored — the 2026-04-19 clásico has no stats and is never a
  scored row; target-missing rule in PREPROCESSING §9).
- **Virgin: 2026 - Clausura, TRANSITIONAL (n = 112 played at pull;
  tournament in progress)** — read ONCE, only for arms passing the
  dev gate, after dev results freeze. The season-end confirmatory
  read is outstanding and noted in the verdict.
- The harness's dev mode must not read 2026 - Clausura rows.

## Arms

1. **Gate Zero** — the unmodified v5 pattern (production ratio prior 200).
2. **RS** — Gate Zero with the on-target ratio prior hardened to
   20,000 (the AU/SA-winning configuration; everything else identical).

Baselines: league base rate at 7.5 (pooled stats-era rate strictly
prior to the scored block) and naive trailing-10 (team trailing-10
SOT for/against means, reference-harness definition).

## GATE LEGS (verbatim, frozen)

Dev gate — pooled dev LL@7.5 of an arm must beat BOTH baselines, else the arm is dead. Virgin legs — (i) LL leg: arm's virgin LL@7.5 ≤ Gate Zero's AND ≤ both baselines'; (ii) calibration leg: |mean predicted P(over 7.5) − actual over-rate| ≤ 1.0pp clean PASS; a breach within 1 SE of the boundary is recorded PROVISIONAL PASS, beyond it FAIL (SE = sd(p_i − y_i)/√n); (iii) per-season sign check on dev (arm LL ≤ Gate Zero LL in at least half the dev seasons) for the both-pass rule. Both-pass rule: if Gate Zero and a variant both pass all legs, the lower virgin LL ships; if only one passes, it ships; if none passes, S-PY verdict is FAIL and nothing ships.

Variant arms require leg (iii); Gate Zero is exempt. Ties go to the
simpler arm (Gate Zero before RS). If Gate Zero fails its own dev
gate, variants are moot, verdict FAIL, virgin NOT read.

## Outputs

Engine `league/PY-DivisionProfesional/engine/sot/` (+ README);
`results_dev.json`, `results_virgin.json`, `fitted_params_virgin.json`;
on PASS, virgin predictions
`league/PY-DivisionProfesional/predictions/s_py_virgin_predictions.csv`
(FT + halves via the frozen SOT constant 0.442, presentation only).
Verdict: `league/PY-DivisionProfesional/reports/S_PY_VERDICT.md`.
Production code untouched. No push. No merge.
