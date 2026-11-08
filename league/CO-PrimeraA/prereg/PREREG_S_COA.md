# Pre-registration — S-COA (CO-PrimeraA shots on target)

Frozen: 2026-11-09, before any fitting. Branch `build/co-primeraa`.
Design authority: `league/CO-PrimeraA/analysis/MODEL_DESIGN.md`
(S-COA); features per `analysis/FEATURES.md` (X5 adopted; X4/X6
DROPPED — shotmap era starts at the virgin boundary); evidence per
`analysis/EDA.md` (F1/F2/F3). Reference: production SOT v5
architecture (`model_sot.py`: joint Poisson ridge regression
λ = 100 + Negative Binomial r = 79.94 + Beta-Binomial on-target
ratio), ported as in `league/PY-DivisionProfesional/prereg/
PREREG_S_PY.md` — with no xG input anywhere (none is dev-available
in this league).

## Data and windows (measured before freezing)

Source: `league/CO-PrimeraA/data/co_primeraa_matches.csv`.
Target: `y = shotsontarget_home + shotsontarget_away` (stats feed,
present ~100% from 2021). Dev-era mean 8.10 → **primary line 7.5**
(secondary reporting lines 6.5/8.5/9.5 as in the reference harness).

- Seed (training only): 2021 - Apertura + 2021 - Clausura (n = 411).
- Dev eval blocks: 2022 - Apertura … 2025 - Clausura (9 tournaments,
  n = 1,788; 1,787 scored — one 2022 - Apertura match has no stats
  feed and is never a scored row; target-missing rows are skipped
  entirely by the loader, as in the PY port).
- **Virgin: 2026 - Apertura (n = 204, complete)** — read ONCE, only
  for arms passing the dev gate, after dev results freeze.
  2026 - Clausura (in progress) is NOT read anywhere in this build.
- The harness's dev mode must not read 2026 rows.

## Arms

1. **Gate Zero** — the unmodified v5 pattern (production ratio prior 200).
2. **RS** — Gate Zero with the on-target ratio prior hardened to
   20,000 (the AU/SA/PY-winning configuration; everything else identical).

Baselines: league base rate at 7.5 (pooled rate strictly prior to
the scored block) and naive trailing-10 (team trailing-10 SOT
for/against means, reference-harness definition).

## GATE LEGS (verbatim, frozen)

Dev gate — pooled dev LL@7.5 of an arm must beat BOTH baselines, else the arm is dead. Virgin legs — (i) LL leg: arm's virgin LL@7.5 ≤ Gate Zero's AND ≤ both baselines'; (ii) calibration leg: |mean predicted P(over 7.5) − actual over-rate| ≤ 1.0pp clean PASS; a breach within 1 SE of the boundary is recorded PROVISIONAL PASS, beyond it FAIL (SE = sd(p_i − y_i)/√n); (iii) per-season sign check on dev (arm LL ≤ Gate Zero LL in at least half the dev seasons) for the both-pass rule. Both-pass rule: if Gate Zero and a variant both pass all legs, the lower virgin LL ships; if only one passes, it ships; if none passes, S-COA verdict is FAIL and nothing ships.

Variant arms require leg (iii); Gate Zero is exempt. Ties go to the
simpler arm (Gate Zero before RS). If Gate Zero fails its own dev
gate, variants are moot, verdict FAIL, virgin NOT read. Calibration
is reported as actual − predicted; the gate uses |breach|.

## Outputs

Engine `league/CO-PrimeraA/engine/sot/` (+ README);
`results_dev.json`, `results_virgin.json`, `fitted_params_virgin.json`;
on PASS, virgin predictions
`league/CO-PrimeraA/predictions/s_coa_virgin_predictions.csv`
(FT + halves via the frozen SOT constant 0.4862, presentation only).
Verdict: `league/CO-PrimeraA/reports/S_COA_VERDICT.md`.
Production code untouched. No push. No merge.
