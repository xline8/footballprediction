# Pre-registration — G-PBM (Primera B Metropolitana goals model)

Frozen: 2026-11-10, before any fitting. Branch `build/ar-primera-b-metropolitana`.
Design authority: `league/AR-PrimeraBMetropolitana/analysis/MODEL_DESIGN.md` §1 +
shared validation frame; features per `FEATURES.md` (X1 goals-only,
X2 newcomer priors); evidence per `EDA.md` (F1/F2/F4/F3).
Reference implementation: production Dixon-Coles in `model_v2.py`
(hl = 270), as ported in `league/J1/engine/goals/`.
S-PBM / C-PBM / K-PBM / T-PBM are NOT preregistered (not buildable —
MODEL_DESIGN: no SOT/corners/yellows/total-shots target exists in any
of the 2,236 payloads).

## Reference architecture (all arms share this unless an arm says otherwise)

- Dixon-Coles fit, copied pattern from `league/J1/engine/goals/dc.py`:
  iterative multiplicative updates, 14 sweeps, damping 0.7, +0.25
  smoothing, home advantage fitted (init 0.28), attack/defence per
  team (init 0), score matrix to MAXG = 10 with the production `tau`
  low-score correction.
- Rho: chosen per fit from the grid (0.0, −0.05, −0.10, −0.15) by
  weighted log-likelihood on goals only, exactly as production.
- Observation (X1): goals only. There is NO xG anywhere in this
  corpus (0 shotmap shots, 0 non-empty stats in 2,236 payloads), so
  the blend's xG term never binds; the fit is goals-only throughout.
  Goals from `header.teams` scores in
  `league/AR-PrimeraBMetropolitana/data/pbm_matches.csv`.
- Time decay: w = 0.5 ** ((cutoff − match_date).days / 270), frozen.
- Fit scope for a target block S: all matches with date strictly
  before the first match date of S (expanding window, block-blocked:
  one fit per target block, whole block predicted from that fit).
- Teams unseen in training start at the league mean (a = d = 0).

## Arms

1. **Gate Zero** — the unmodified reference above. Newcomers start at
   the league mean.
2. **Arm X2** — Gate Zero plus newcomer priors (feature X2, EDA F4).
   A club is a *newcomer* for target block S when it plays in S and
   did not play in this league in the immediately preceding block
   S−1 (team id present in the CSV for S, absent for S−1). For a
   newcomer, at prediction time in block S only:
   - attack: `a += log(max(mu + GF_GAP, 0.10) / mu)`
   - defence: `d += log(max(mu + GA_GAP, 0.10) / mu)`
   where mu is the decay-weighted mean goals per team per match in
   the training window, and GF_GAP = −0.0325 / GA_GAP = −0.0410 are
   the pooled F4 magnitudes (GF gap −0.0325, GA gap −0.0410 per match
   over the fourteen 2022–2025 newcomer team-blocks). By-direction
   context (not used): relegated-from-Nacional n=4, GF −0.2125 /
   GA −0.1186; promoted-from-below/cross-competition n=10,
   GF +0.0394 / GA −0.0099. The offset is added to the fitted rating
   (league mean 0 for a first-time club). Clubs with no
   immediately-preceding-block record in either direction start at
   the league mean in every arm.

## Dev protocol

- Dev period: blocks 2021 – 2025. Block 2021 is the initial training
  window; evaluation blocks are 2022, 2023, 2024, 2025 under the
  expanding block-blocked walk-forward (pooled dev n = 1,426;
  scored-dev goals/match 2.0344, OU2.5 over-rate 34.99%, home-win
  rate 39.34%).
- Metrics per arm per block and pooled: mean 1X2 log-loss, mean
  RPS (H, D, A), mean OU2.5 log-loss.
- Baselines: climatology — for target block S, the pooled outcome
  rates and OU2.5 over-rate of all blocks strictly before S; plus a
  naive trailing-10 baseline (per-team trailing-10 goal means, same
  walk-forward) reported alongside.
- The dev harness must not read block "2026" rows at all.

## Virgin protocol

- Virgin window: block "2026" (group phase, single table, 22 teams,
  rounds 1–42, n = 462). Fit = all matches dated before the first
  2026 match. Read ONCE, after dev results are frozen in the results
  file, and ONLY for arms that pass the dev gate.
- **Frozen rule: if Gate Zero fails its dev gate, the variants are
  moot and the virgin is NOT read — even if a variant arm passes
  dev.** (BNAC rule; this rule governs G-PBM.)
- Virgin climatology: pooled 2021 – 2025 outcome rates and OU2.5
  over-rate.
- Calibration per arm: (i) mean predicted home-win probability minus
  actual home-win rate; (ii) mean predicted P(over 2.5) minus actual
  over-rate. SE = sd(pred_i − y_i)/√n, reported with the difference.

## GATE LEGS (verbatim, frozen)

Dev gate — pooled dev 1X2 LL and RPS of an arm must beat climatology, and OU2.5 LL must beat the base-rate baseline, else the arm is dead. Virgin legs — (i) LL leg: arm's virgin 1X2 LL ≤ Gate Zero's AND ≤ climatology's; (ii) calibration leg: |mean predicted − actual| ≤ 1.0pp pooled for home-win rate and for OU2.5 over-rate, SEs reported; a breach within 1 SE of the boundary is recorded PROVISIONAL PASS, beyond it FAIL; (iii) per-block sign check on dev (arm LL ≤ Gate Zero LL in at least half the dev blocks) for the both-pass rule. Both-pass rule: if Gate Zero and a variant both pass all legs, the lower pooled virgin 1X2 LL ships; if only one passes, it ships; if none passes, G-PBM verdict is FAIL and nothing ships.

Reading of the legs, fixed here so the verdict is mechanical:

- An arm *passes* iff it survives the dev gate AND passes virgin
  legs (i)–(ii) (a PROVISIONAL PASS counts as a pass, recorded as
  such) AND, for variant arms only, leg (iii) (≥ 2 of the 4 scored
  dev blocks). Gate Zero is exempt from (iii).
- If several variant arms pass together with Gate Zero, the lower
  pooled virgin 1X2 LL ships; ties go to the simpler arm (Gate Zero
  before X2).
- If Gate Zero fails its dev gate, the virgin is not read (frozen
  rule above) and G-PBM verdict is FAIL.

## Outputs

- Engine: `league/AR-PrimeraBMetropolitana/engine/goals/` (this league's own
  code: fit/predict/harness modules + a CLI runner).
- Dev results: `league/AR-PrimeraBMetropolitana/engine/goals/results_dev.json` (+ CSV).
- Virgin results: `league/AR-PrimeraBMetropolitana/engine/goals/results_virgin.json`.
- Fitted parameters for the virgin fit:
  `league/AR-PrimeraBMetropolitana/engine/goals/fitted_params_virgin.json`.
- Virgin predictions: `league/AR-PrimeraBMetropolitana/predictions/g_pbm_virgin_predictions.csv`
  — the shipped arm's predictions (Gate Zero's if nothing ships,
  labelled in the verdict), one row per 2026 match, with FT
  lambdas, FT 1X2 / OU (1.5, 2.5, 3.5) / BTTS probabilities, and
  1H/2H lines derived by splitting the same lambdas with the frozen
  PBM goals constant 0.439932 (1H λ = 0.439932·FT λ,
  2H λ = 0.560068·FT λ; 1H OU lines 0.5/1.5/2.5, 2H OU lines
  1.5/2.5/3.5, same rho and score-matrix machinery). Halves are
  presentation only.
- Verdict: `league/AR-PrimeraBMetropolitana/reports/G_PBM_VERDICT.md`.

Production code and data are untouched. No push. No merge.
