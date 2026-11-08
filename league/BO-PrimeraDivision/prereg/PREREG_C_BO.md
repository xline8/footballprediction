# Pre-registration — C-BO (BO-PrimeraDivision corners)

Frozen: 2026-11-10, before any fitting. Branch `build/bo-primera`.
Design authority: `analysis/MODEL_DESIGN.md` (C-BO); features per
`analysis/FEATURES.md` (X5 adopted; X9 adopted for Gate Zero;
X7 adopted as the variant arm — box-touch split-half r=.703 for,
.408 against, 2025, n=16 teams); evidence per `analysis/EDA.md`
(corners traits for/against r=.589/.358; possession r=.775).
Reference: production `model_corners_v3` pattern (team corner ratings
+ Negative Binomial total, territorial multiplier), ported as in
`league/J1/engine/corners/` / `league/PY-DivisionProfesional/engine/corners/`.

## Data and windows (measured before freezing)

Source: `league/BO-PrimeraDivision/data/bo_matches.csv`.
Target: `y = corners_home + corners_away` (stats feed, present 2025+
only). Dev-era mean 9.50625 → **primary line 9.5** (secondary
reporting lines 8.5/10.5 as in the reference harness).

- Seed (training only): 2025 rounds 1–10 (n = 80).
- Dev eval blocks: 2025 rounds 11–30 in four expanding 5-round blocks
  (train on all prior 2025 rounds; n = 160 scored).
- **Virgin: 2026 regular, TRANSITIONAL (n = 199 played at pull;
  season in progress, rounds 1–25)** — read ONCE, only for arms
  passing the dev gate, after dev results freeze. The season-end
  confirmatory read is outstanding and noted in the verdict.
- The harness's dev mode must not read 2026 rows.

## Arms

1. **Gate Zero** — the unmodified corners_v3 pattern (X9 covariates:
   trailing possession + big-chance rates for/against, min-8 rule).
2. **X7** — Gate Zero with the territorial multiplier driven by
   trailing opp-box touches for/against (feature X7, min-6 rule)
   instead of / in addition to the production covariates, exactly as
   the J1 C-arm specifies; everything else identical.

Baselines: league base rate at 9.5 (pooled stats-era rate strictly
prior to the scored block) and naive trailing-10 (team trailing-10
corners for/against means, reference-harness definition).

## GATE LEGS (verbatim, frozen)

Dev gate — pooled dev LL@9.5 of an arm must beat BOTH baselines, else the arm is dead. Virgin legs — (i) LL leg: arm's virgin LL@9.5 ≤ Gate Zero's AND ≤ both baselines'; (ii) calibration leg: |mean predicted P(over 9.5) − actual over-rate| ≤ 1.0pp clean PASS; a breach within 1 SE of the boundary is recorded PROVISIONAL PASS, beyond it FAIL (SE = sd(p_i − y_i)/√n); (iii) per-block sign check on dev (arm LL ≤ Gate Zero LL in at least half the dev blocks) for the both-pass rule. Both-pass rule: if Gate Zero and a variant both pass all legs, the lower virgin LL ships; if only one passes, it ships; if none passes, C-BO verdict is FAIL and nothing ships.

Variant arms require leg (iii); Gate Zero is exempt. Ties go to the
simpler arm (Gate Zero before X7). If Gate Zero fails its own dev
gate, variants are moot, verdict FAIL, virgin NOT read.

## Outputs

Engine `league/BO-PrimeraDivision/engine/corners/` (+ README);
`results_dev.json`, `results_virgin.json`, `fitted_params_virgin.json`;
on PASS, virgin predictions
`league/BO-PrimeraDivision/predictions/c_bo_virgin_predictions.csv`
(FT + halves via the frozen corners constant 0.4866, presentation only).
Verdict: `league/BO-PrimeraDivision/reports/C_BO_VERDICT.md`.
Production code untouched. No push. No merge.
