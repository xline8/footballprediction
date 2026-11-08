# Pre-registration — S-PE (PE-Liga1 shots on target)

Frozen: 2026-11-10, before any fitting. Branch `build/pe-liga1`.
Design authority: `league/PE-Liga1/analysis/MODEL_DESIGN.md` (S-PE);
features per `analysis/FEATURES.md` (X5 adopted; X4/X6 DROPPED — no
shotmap exists in this corpus); evidence per `analysis/EDA.md`
(F1/F2/F3). Reference: production SOT v5 architecture
(`model_sot.py`: joint Poisson ridge regression λ = 100 + Negative
Binomial r = 79.94 + Beta-Binomial on-target ratio), ported as in
`league/CO-PrimeraA/prereg/PREREG_S_COA.md`. The v5 total-shots
input signal uses this league's **unified** shots target (EDA
F-feed-2: rich = SOT + off-target; sparse = `total_shots` key).

## Data and windows (measured before freezing)

Source: `league/PE-Liga1/data/pe_liga1_matches.csv`, modelling
corpus (regular, non-awarded). Target: `y = shotsontarget_home +
shotsontarget_away` (stats feed). Dev-era mean 8.557 → **primary
line 8.5** (secondary reporting lines 6.5/7.5/9.5/10.5 as in the
reference harness).

- Seed (training only): 2021 - Fase 1 + 2021 - Fase 2 (n = 234).
- Dev eval blocks: 2022 - Apertura … 2024 - Clausura (6 blocks,
  n = 982; 877 scored — target-missing rows are never scored rows
  and are skipped entirely by the loader, as in the reference
  ports).
- **Virgin: calendar 2025 (n = 323; 280 scored)** — read ONCE, only
  for arms passing the dev gate, after dev results freeze. 2026 is
  NOT read anywhere in this build (in progress; reserved).
- The harness's dev mode must not read 2025 or 2026 rows.

## Arms

1. **Gate Zero** — the unmodified v5 pattern (production ratio prior 200).
2. **RS** — Gate Zero with the on-target ratio prior hardened to
   20,000 (the programme's RS configuration; everything else identical).

Baselines: league base rate at 8.5 (pooled rate strictly prior to
the scored block) and naive trailing-10 (reference-harness
definition).

## GATE LEGS (verbatim, frozen)

Dev gate — pooled dev LL@8.5 of an arm must beat BOTH baselines, else the arm is dead. Virgin legs — (i) LL leg: arm's virgin LL@8.5 ≤ Gate Zero's AND ≤ both baselines'; (ii) calibration leg: |mean predicted P(over 8.5) − actual over-rate| ≤ 1.0pp clean PASS; a breach within 1 SE of the boundary is recorded PROVISIONAL PASS, beyond it FAIL (SE = sd(p_i − y_i)/√n); (iii) per-season sign check on dev (arm LL ≤ Gate Zero LL in at least half the dev seasons) for the both-pass rule. Both-pass rule: if Gate Zero and a variant both pass all legs, the lower virgin LL ships; if only one passes, it ships; if none passes, S-PE verdict is FAIL and nothing ships.

Variant arms require leg (iii); Gate Zero is exempt. Ties go to the
simpler arm (Gate Zero before RS). If Gate Zero fails its own dev
gate, variants are moot, verdict FAIL, virgin NOT read. Calibration
is reported as actual − predicted; the gate uses |breach|.

## Outputs

Engine `league/PE-Liga1/engine/sot/` (+ README);
`results_dev.json`, `results_virgin.json`, `fitted_params_virgin.json`;
on PASS, virgin predictions
`league/PE-Liga1/predictions/s_pe_virgin_predictions.csv`
(FT + halves via the frozen SOT constant 0.4611, presentation only).
Verdict: `league/PE-Liga1/reports/S_PE_VERDICT.md`.
Production code untouched. No push. No merge.
