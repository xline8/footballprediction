# Pre-registration — S-BO (BO-PrimeraDivision shots on target)

Frozen: 2026-11-10, before any fitting. Branch `build/bo-primera`.
Design authority: `analysis/MODEL_DESIGN.md` (S-BO); features per
`analysis/FEATURES.md` (X5 adopted; X4/X6 DROPPED — no shotmap);
evidence per `analysis/EDA.md` (SOT traits for/against r=.705/.523;
on-target rate split-half r=.613 — a real trait here, unlike J1).
Reference: production SOT v5 architecture (`model_sot.py`: joint
Poisson ridge regression λ = 100 + Negative Binomial r fitted +
Beta-Binomial on-target ratio), ported as in `league/J1/engine/sot/` /
`league/PY-DivisionProfesional/engine/sot/` — **with no xG input
anywhere** (none exists in this league).

## Data and windows (measured before freezing)

Source: `league/BO-PrimeraDivision/data/bo_matches.csv`.
Target: `y = ShotsOnTarget_home + ShotsOnTarget_away` (stats feed,
present 2025+ only). Dev-era mean 11.2375 → **primary line 11.5**
(secondary reporting lines 10.5/12.5 as in the reference harness).

- Seed (training only): 2025 rounds 1–10 (n = 80).
- Dev eval blocks: 2025 rounds 11–30 in four expanding 5-round blocks
  (train on all prior 2025 rounds; n = 160 scored).
- **Virgin: 2026 regular, TRANSITIONAL (n = 199 played at pull;
  season in progress, rounds 1–25)** — read ONCE, only for arms
  passing the dev gate, after dev results freeze. The season-end
  confirmatory read is outstanding and noted in the verdict. There is
  no complete stats-era virgin season yet; this is the honest
  consequence of the stats feed starting in 2025 (PY precedent).
- The harness's dev mode must not read 2026 rows.

## Arms

1. **Gate Zero** — the unmodified v5 pattern (production ratio prior 200).
2. **RS** — Gate Zero with the on-target ratio prior hardened to
   20,000 (the AU/SA-winning configuration; everything else identical).
   Robustness arm: EDA measures the on-target rate as signal here
   (r=.613), so RS is expected to lose and ships only if it beats
   Gate Zero on dev and virgin.

Baselines: league base rate at 11.5 (pooled stats-era rate strictly
prior to the scored block) and naive trailing-10 (team trailing-10
SOT for/against means, reference-harness definition).

## GATE LEGS (verbatim, frozen)

Dev gate — pooled dev LL@11.5 of an arm must beat BOTH baselines, else the arm is dead. Virgin legs — (i) LL leg: arm's virgin LL@11.5 ≤ Gate Zero's AND ≤ both baselines'; (ii) calibration leg: |mean predicted P(over 11.5) − actual over-rate| ≤ 1.0pp clean PASS; a breach within 1 SE of the boundary is recorded PROVISIONAL PASS, beyond it FAIL (SE = sd(p_i − y_i)/√n); (iii) per-block sign check on dev (arm LL ≤ Gate Zero LL in at least half the dev blocks) for the both-pass rule. Both-pass rule: if Gate Zero and a variant both pass all legs, the lower virgin LL ships; if only one passes, it ships; if none passes, S-BO verdict is FAIL and nothing ships.

Variant arms require leg (iii); Gate Zero is exempt. Ties go to the
simpler arm (Gate Zero before RS). If Gate Zero fails its own dev
gate, variants are moot, verdict FAIL, virgin NOT read.

## Outputs

Engine `league/BO-PrimeraDivision/engine/sot/` (+ README);
`results_dev.json`, `results_virgin.json`, `fitted_params_virgin.json`;
on PASS, virgin predictions
`league/BO-PrimeraDivision/predictions/s_bo_virgin_predictions.csv`
(FT + halves via the frozen SOT constant 0.4555, presentation only).
Verdict: `league/BO-PrimeraDivision/reports/S_BO_VERDICT.md`.
Production code untouched. No push. No merge.
