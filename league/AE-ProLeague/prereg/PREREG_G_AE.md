# Pre-registration — G-AE (AE-ProLeague goals model)

Frozen: 2026-11-10, before any fitting. Branch `build/ae-proleague`.
Design authority: `league/AE-ProLeague/analysis/MODEL_DESIGN.md` (G-AE);
features per `analysis/FEATURES.md` (X1 goals-only). Reference:
production Dixon-Coles in `model_v2.py` (hl=270); engine port pattern:
`league/CY-1Division/engine/goals/` adapted to this league's CSV.

## Reference architecture (all arms share unless an arm says otherwise)

- Dixon-Coles fit, production pattern: iterative multiplicative updates,
  14 sweeps, damping 0.7, +0.25 smoothing, home advantage fitted
  (init 0.28), attack/defence per team (init 0), MAXG=10, production tau.
- Rho per fit from grid (0.0, −0.05, −0.10, −0.15) by weighted
  log-likelihood on goals only.
- Observation: goals-only (X1: no xG exists in this league — the blend's
  documented fallback, not a variant).
- Time decay w = 0.5 ** ((cutoff − match_date).days / 270), frozen.
- Fit scope for target season S: all AE matches dated strictly before
  the first match date of S (expanding, season-blocked). Awarded
  matches excluded everywhere. Teams unseen in training start at the
  league mean (a = d = 0).

## Arms

1. **Gate Zero** — the unmodified reference above.
2. **Arm SHRINK** — Gate Zero plus exactly one change at prediction
   time: for a team with fewer than 6 prior in-league matches in the
   training window, `a *= n/6`, `d *= n/6` (n = prior in-league matches;
   n=0 identical to Gate Zero's unseen rule). The sanctioned G-J2-lesson
   arm for thin-history season openers.

## Dev protocol

- Seed 2021/2022 (fit history, never scored); scored folds 2022/2023,
  2023/2024, 2024/2025 (n=545, awarded excluded). Metrics per arm per
  season and pooled: mean 1X2 LL, RPS, OU2.5 LL. Baseline: climatology
  (pooled outcome + OU2.5 over-rates of seasons strictly before S).
- The dev harness must not read 2025/2026 or 2026/2027 rows at all.

## Virgin protocol

- Virgin = 2025/2026 (n=182, complete), read ONCE, only for arms passing
  the dev gate, after dev results are frozen. Calibration = mean
  predicted − actual for home-win rate and OU2.5 over-rate,
  SE = sd(p_i − y_i)/√n. 2026/2027 NOT read (reserved confirmatory).

## GATE LEGS (verbatim, frozen)

Dev gate — pooled dev 1X2 LL and RPS of an arm must beat climatology, and OU2.5 LL must beat the base-rate baseline, else the arm is dead. Virgin legs — (i) LL leg: arm's virgin 1X2 LL ≤ Gate Zero's AND ≤ climatology's; (ii) calibration leg: |mean predicted − actual| ≤ 1.0pp pooled for home-win rate and for OU2.5 over-rate, SEs reported; a breach within 1 SE of the boundary is recorded PROVISIONAL PASS, beyond it FAIL; (iii) per-season sign check on dev (arm LL ≤ Gate Zero LL in at least half the dev seasons) for the both-pass rule. Both-pass rule: if Gate Zero and a variant both pass all legs, the lower pooled virgin 1X2 LL ships; if only one passes, it ships; if none passes, G-AE verdict is FAIL and nothing ships.

Mechanical reading: an arm passes iff it survives the dev gate AND
passes virgin legs (i)–(ii) (PROVISIONAL counts, recorded as such) AND,
for variant arms, leg (iii); Gate Zero is exempt from (iii). With three
dev seasons, leg (iii) means ≥2 of 3. Ties go to the simpler arm (Gate
Zero before SHRINK). If Gate Zero fails its own dev gate, variants are
moot, verdict FAIL, virgin NOT read.

## Outputs

Engine `league/AE-ProLeague/engine/goals/`; `results_dev.json`;
`results_virgin.json`; `fitted_params_virgin.json`; on PASS, virgin
predictions `league/AE-ProLeague/predictions/g_ae_virgin_predictions.csv`
(1H/2H presentation via frozen goals constant 0.4463). Verdict:
`league/AE-ProLeague/reports/G_AE_VERDICT.md`. Production code
untouched. No push. No merge.
