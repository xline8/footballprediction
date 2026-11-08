# Pre-registration — G-ITB (IT-SerieB goals model)

Frozen: 2026-11-09, before any fitting. Branch `build/it-serieb`.
Design authority: `league/IT-SerieB/analysis/MODEL_DESIGN.md`
(G-ITB); features per `analysis/FEATURES.md` (X2 mover tier offset;
X1 blend DROPPED era-dead); evidence per `analysis/EDA.md`
(F1/F2/F4). Reference: production Dixon-Coles in `model_v2.py`
(class `DC`), hl = 270; analogues: `league/ES-LaLiga2/prereg/
PREREG_G_ES.md` (same shape) and `league/IT-SerieC/prereg/
PREREG_G_ITC.md` (same country). **Calibration in this league =
actual − predicted** (stated here and in the verdict; SE =
sd(y_i − p_i)/√n).

## Modeling set (frozen)

- All phases are ordinary rows (regular + promotion play-off +
  relegation play-out; PREPROCESSING rule 3 — 10 of 390 matches
  per season, same-season Serie B clubs only, no phase feature).
- Finished matches: 2021/2022 n=390; 2022/2023 n=390; 2023/2024
  n=390; 2024/2025 n=389; 2025/2026 n=390; 2026/2027 n=110
  (in progress, reserved).
- Team identity is FotMob team_id everywhere (PREPROCESSING
  rule 9, Reggiana alias included).

## Reference architecture (all arms share unless an arm says otherwise)

- Dixon-Coles fit, copied pattern from production `model_v2.py`:
  iterative multiplicative updates, 14 sweeps, damping 0.7, +0.25
  smoothing, home advantage fitted (init 0.28), attack/defence
  per team (init 0), score matrix MAXG = 10, production `tau`
  correction.
- Rho per fit from grid (0.0, −0.05, −0.10, −0.15) by weighted
  log-likelihood on goals only, as production.
- Observation = **goals only**. The production blend's xG half
  does not exist in this league's dev window (`expected_goals`
  in 13 of 1,559 dev matches; the xG era starts in the virgin
  2025/2026) — goals-only is the reference implementation's own
  documented fallback (G-J2 / G-ES precedent), frozen here by
  design: no xG arm is built on one era.
- Time decay w = 0.5 ** ((cutoff − match_date).days / 270) —
  frozen, no search.
- Fit scope for target season S: all matches dated strictly
  before the first match date of S (expanding, season-blocked).
- Teams unseen in training start at the league mean (a = d = 0).

## Arms

1. **Gate Zero** — the unmodified reference above.
2. **Arm SHRINK** (sanctioned G-J2-lesson arm; FEATURES) — Gate
   Zero plus exactly one change at prediction time: for a team
   with fewer than 6 prior in-league matches in the training
   window, its fitted attack and defence ratings are shrunk
   toward the league mean: `a *= n/6`, `d *= n/6` where n = its
   prior in-league match count (n = 0 ⇒ a = d = 0, identical to
   Gate Zero's unseen rule; the arm bites exactly for teams with
   1–5 prior matches — the season-opener failure mode).
3. **Arm X2** — Gate Zero plus mover tier priors (feature X2,
   EDA F4), in the ENGCH/ES formulation. Membership is the
   **frozen mover table** `prereg/movers_itb.json` (team_id ×
   entry season → source tier; derived in EDA from team_id
   churn plus accent-normalised tier name matching with the
   Reggiana spelling alias — the table is data frozen before
   fitting, not re-derived at runtime). A club is a mover for
   target season S when the table lists it under S. For a mover,
   at prediction time in season S only, with mu = the
   decay-weighted mean goals per team per match in the training
   window:
   - from Serie A: attack `a += log((mu + 0.145) / mu)`; defence
     `d += log((mu - 0.143) / mu)`
   - from Serie C: attack `a += log(max(mu - 0.070, 0.10) / mu)`;
     defence `d += log((mu + 0.118) / mu)`
   where +0.145 / −0.143 / −0.070 / +0.118 are the frozen F4
   magnitudes (entry-season GF/GA deltas vs league mu 1.232,
   pooled over entry seasons 2022/2023–2025/2026). The offset is
   added to the fitted rating (league mean 0 for a first-time
   club). Nothing else changes.

## Dev protocol

- Training seed = 2021/2022; evaluation seasons 2022/2023,
  2023/2024, 2024/2025 (pooled n = 1,169) under the
  season-blocked walk-forward.
- Metrics per arm per season and pooled: mean 1X2 LL, mean RPS
  (H, D, A), mean OU2.5 LL. Baselines: climatology — for target
  season S, pooled outcome rates + OU2.5 over-rate of all
  seasons strictly before S.
- The dev harness must not read 2025/2026 or 2026/2027 rows at all.

## Virgin protocol

- Virgin = 2025/2026 (n = 390, complete), read ONCE, only for
  arms passing the dev gate, after dev results are frozen.
  Fit = all matches before the first 2025/2026 match date.
  Climatology = pooled 2021/2022–2024/2025 rates. Calibration:
  **actual − mean predicted** for home-win rate and OU2.5
  over-rate, SE = sd(y_i − p_i)/√n.

## GATE LEGS (verbatim, frozen)

Dev gate — pooled dev 1X2 LL and RPS of an arm must beat climatology, and OU2.5 LL must beat the base-rate baseline, else the arm is dead. Virgin legs — (i) LL leg: arm's virgin 1X2 LL ≤ Gate Zero's AND ≤ climatology's; (ii) calibration leg: |actual − mean predicted| ≤ 1.0pp pooled for home-win rate and for OU2.5 over-rate, SEs reported; a breach within 1 SE of the boundary is recorded PROVISIONAL PASS, beyond it FAIL; (iii) per-season sign check on dev (arm LL ≤ Gate Zero LL in at least half the dev seasons) for the both-pass rule. Both-pass rule: if Gate Zero and a variant both pass all legs, the lower pooled virgin 1X2 LL ships; if only one passes, it ships; if none passes, G-ITB verdict is FAIL and nothing ships.

Mechanical reading: an arm passes iff it survives the dev gate
AND passes virgin legs (i)–(ii) (PROVISIONAL counts, recorded as
such) AND, for variant arms, leg (iii); Gate Zero is exempt from
(iii). Ties go to the simpler arm (Gate Zero before SHRINK
before X2). If Gate Zero fails its own dev gate, variants are
moot, verdict FAIL, virgin NOT read.

## Outputs

Engine `league/IT-SerieB/engine/goals/`; dev results
`results_dev.json` (+ CSV); virgin `results_virgin.json`; fitted
params `fitted_params_virgin.json`; on PASS, virgin predictions
`league/IT-SerieB/predictions/g_itb_virgin_predictions.csv`
(shipped arm; 1H/2H presentation via frozen goals constant
0.4501). Verdict: `league/IT-SerieB/reports/G_ITB_VERDICT.md`.
Production code untouched. No push. No merge.
