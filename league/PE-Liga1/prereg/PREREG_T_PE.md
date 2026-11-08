# Pre-registration — T-PE (PE-Liga1 total shots)

Frozen: 2026-11-10, before any fitting. Branch `build/pe-liga1`.
Design authority: `league/PE-Liga1/analysis/MODEL_DESIGN.md` (T-PE);
features per `analysis/FEATURES.md` (X5 adopted); evidence per
`analysis/EDA.md` (F1/F2/F3/F-feed-2). Reference: the shots family
in `experiments/` + `league/J1/engine/total_shots/`, ported as in
`league/CO-PrimeraA/prereg/PREREG_T_COA.md` (v1 / v2 level layer /
E9 trailing-r arms). Built ahead of the top-5 total-shots
prospective verdict by the programme's standing user order; that
trial is untouched.

## Data and windows (measured before freezing)

Source: `league/PE-Liga1/data/pe_liga1_matches.csv`, modelling
corpus (regular, non-awarded). Target: the **unified** shots total
of EDA F-feed-2 — rich matches: `shotsontarget + shotsofftarget`
per side (the feed's rich `total_shots` additionally includes
blocked shots, exactly, in 100% of rich matches); sparse matches:
the `total_shots` key as-is (its block means track rich
SOT + off-target, 19–20 vs 19.6–20.8, not the rich total 25–27).
The unified quantity is "shots excluding blocked shots" and is the
only homogeneous total-shots target this feed carries. Dev-era
unified mean 19.727 → **primary line 19.5** (secondary
17.5/18.5/20.5/21.5 as in the reference harness shifted to this
league's level). The level layer's M_BAR is frozen at **19.727**
(this league's dev pooled unified mean, EDA F-feed-2).

- Seed (training only): 2021 - Fase 1 + 2021 - Fase 2 (n = 234).
- Dev eval blocks: 2022 - Apertura … 2024 - Clausura (6 blocks,
  n = 982; 877 scored — target-missing rows are skipped by the
  loader, as in the reference ports).
- **Virgin: calendar 2025 (n = 323; 280 scored)** — read ONCE, only
  for arms passing the dev gate, after dev results freeze. 2026 is
  NOT read anywhere in this build.
- Hyperparameters (ridge λ grid {3, 10, 30, 100, 300}, r_A by
  moments, level-layer cell grid) are tuned on the dev span exactly
  as in the reference runner (tuning uses scored dev rows only —
  the seed blocks are the tuning span's warmup).

## Arms

1. **A** — v1 pattern (reference total-shots model, unmodified).
2. **B** — v2 level layer on top of A.
3. **C** — E9 trailing-r (dispersion r from the trailing window),
   on top of A.

Baselines: league base rate at 19.5 (reference runner's
`baseline_league`) and naive trailing-10 (`baseline_naive`).

## GATE LEGS (verbatim, frozen)

Dev gate — pooled dev LL@19.5 of an arm must beat BOTH baselines, else the arm is dead. Virgin legs — (i) LL leg: arm's virgin LL@19.5 ≤ arm A's AND ≤ both baselines'; (ii) calibration leg: |mean predicted P(over 19.5) − actual over-rate| ≤ 1.0pp clean PASS; a breach within 1 SE of the boundary is recorded PROVISIONAL PASS, beyond it FAIL (SE = sd(p_i − y_i)/√n); (iii) per-season sign check on dev (arm LL ≤ arm A LL in at least half the dev seasons) for the multi-pass rule. Multi-pass rule: if several arms pass all legs, the lowest virgin LL ships; if only one passes, it ships; if none passes, T-PE verdict is FAIL and nothing ships.

Variant arms B/C require leg (iii); arm A is exempt. Ties go to the
simpler arm (A before B before C). If arm A fails its own dev gate,
variants are moot, verdict FAIL, virgin NOT read. Calibration is
reported as actual − predicted; the gate uses |breach|.

## Outputs

Engine `league/PE-Liga1/engine/total_shots/` (+ README);
`results_dev.json`, `results_virgin.json`, `fitted_params.json`,
`fitted_params_virgin.json`; on PASS, virgin predictions
`league/PE-Liga1/predictions/t_pe_virgin_predictions.csv`
(FT + halves via the frozen total-shots constant 0.4662,
presentation only). Verdict:
`league/PE-Liga1/reports/T_PE_VERDICT.md`.
Production code untouched. No push. No merge.
