# Pre-registration — S-VE (VE-PrimeraDivision shots on target)

Frozen: 2026-11-10, before any fitting. Branch `build/ve-primera`.
Design authority: `analysis/MODEL_DESIGN.md` (S-VE); features per
`analysis/FEATURES.md` (X5 adopted; X4/X6 DROPPED — no shotmap);
evidence per `analysis/EDA.md` (SOT traits for/against r=.274/.359
pooled; on-target rate split-half r=−.300 pooled — NOISE, unlike BO).
Reference: production SOT v5 architecture (`model_sot.py`: joint
Poisson ridge regression λ = 100 + Negative Binomial r fitted +
Beta-Binomial on-target ratio), ported as in `league/J1/engine/sot/` /
`league/BO-PrimeraDivision/engine/sot/` — **with no xG input
anywhere** (none exists in this league).

## Data and windows (measured before freezing)

Source: `league/VE-PrimeraDivision/data/ve_matches.csv`.
Target: `y = ShotsOnTarget_home + ShotsOnTarget_away` (stats feed,
present in all 343 stats-era matches). Dev-era (2026 Apertura
regular) mean 8.2527 → **primary line 8.5** (secondary reporting
lines 7.5/9.5 as in the reference harness).

- Seed (training only): 2025 Clausura regular (n = 91).
- Dev eval blocks: 2026 Apertura regular in two expanding blocks,
  rounds 1–7 (n = 49) and rounds 8–13 (n = 42); train on all prior
  stats-era regular matches; n = 91 scored.
- **Virgin: 2026 Clausura regular, TRANSITIONAL (n = 91, complete
  phase; season in progress — Clausura Quadrangular round 6,
  Clausura Final and Super Final pending)** — read ONCE, only for
  arms passing the dev gate, after dev results freeze. The season-end
  confirmatory read is outstanding and noted in the verdict. There is
  no complete stats-era virgin season yet; this is the honest
  consequence of the stats feed starting in 2025 (BO precedent).
  NOTE (known before the read, descriptive only — no line is set
  from it): the virgin mean is 9.23 SOT/match vs 8.25 in dev; the
  calibration leg is therefore expected to be hard, and the gate
  decides — the window is not moved because the outcome is
  inconvenient.
- The harness's dev mode must not read 2026 Clausura rows.

## Arms

1. **Gate Zero** — the unmodified v5 pattern (production ratio prior 200).
2. **RS** — Gate Zero with the on-target ratio prior hardened to
   20,000 (the AU/SA-winning configuration; everything else identical).
   v5-component test: EDA measures the on-target rate as noise here
   (r=−.300 pooled), so hardening the prior toward the league mean is
   the direction the evidence points; RS ships only if it beats Gate
   Zero on dev and virgin.

Baselines: league base rate at 8.5 (pooled stats-era rate strictly
prior to the scored block) and naive trailing-10 (team trailing-10
SOT for/against means, reference-harness definition).

## GATE LEGS (verbatim, frozen)

Dev gate — pooled dev LL@8.5 of an arm must beat BOTH baselines, else the arm is dead. Virgin legs — (i) LL leg: arm's virgin LL@8.5 ≤ Gate Zero's AND ≤ both baselines'; (ii) calibration leg: |mean predicted P(over 8.5) − actual over-rate| ≤ 1.0pp clean PASS; a breach within 1 SE of the boundary is recorded PROVISIONAL PASS, beyond it FAIL (SE = sd(p_i − y_i)/√n); (iii) per-block sign check on dev (arm LL ≤ Gate Zero LL in at least half the dev blocks) for the both-pass rule. Both-pass rule: if Gate Zero and a variant both pass all legs, the lower virgin LL ships; if only one passes, it ships; if none passes, S-VE verdict is FAIL and nothing ships.

Variant arms require leg (iii); Gate Zero is exempt. Ties go to the
simpler arm (Gate Zero before RS). If Gate Zero fails its own dev
gate, variants are moot, verdict FAIL, virgin NOT read.

## Outputs

Engine `league/VE-PrimeraDivision/engine/sot/` (+ README);
`results_dev.json`, `results_virgin.json`, `fitted_params_virgin.json`;
on PASS, virgin predictions
`league/VE-PrimeraDivision/predictions/s_ve_virgin_predictions.csv`
(FT + halves via the frozen SOT constant 0.4651, presentation only).
Verdict: `league/VE-PrimeraDivision/reports/S_VE_VERDICT.md`.
Production code untouched. No push. No merge.
