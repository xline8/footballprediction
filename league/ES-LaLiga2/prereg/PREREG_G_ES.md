# Pre-registration — G-ES (ES-LaLiga2 goals model)

Frozen: 2026-11-09, before any fitting. Branch `build/es-laliga2`.
Design authority: `league/ES-LaLiga2/analysis/MODEL_DESIGN.md`
(G-ES); features per `analysis/FEATURES.md` (X2 mover tier offset;
X1 blend DROPPED era-dead); evidence per `analysis/EDA.md`
(F1/F2/F4). Reference: production Dixon-Coles in `model_v2.py`
(class `DC`), hl = 270; analogues: `league/J2/prereg/PREREG_G_J2.md`
(goals-only construction) and `league/ENG-Championship/prereg/
PREREG_G_ENGCH.md` (SHRINK/X2 formulation).

## Reference architecture (all arms share unless an arm says otherwise)

- Dixon-Coles fit, copied pattern from production `model_v2.py`:
  iterative multiplicative updates, 14 sweeps, damping 0.7, +0.25
  smoothing, home advantage fitted (init 0.28), attack/defence per
  team (init 0), score matrix MAXG = 10, production `tau` correction.
- Rho per fit from grid (0.0, −0.05, −0.10, −0.15) by weighted
  log-likelihood on goals only, as production.
- Observation = **goals only**. The production blend's xG half does
  not exist in this league's dev window (`expected_goals` in 7 of
  1,872 dev matches; the xG era starts in the virgin 2025/2026) —
  goals-only is the reference implementation's own documented
  fallback (G-J2 precedent), frozen here by design, per the task
  brief: no xG arm is built on one era.
- Time decay w = 0.5 ** ((cutoff − match_date).days / 270) — frozen,
  no search.
- Fit scope for target season S: all ES matches dated strictly
  before the first match date of S (expanding, season-blocked).
  Play-off matches are ordinary rows (PREPROCESSING rule 3).
- Teams unseen in training start at the league mean (a = d = 0).
  Team identity is FotMob team_id everywhere (PREPROCESSING rule 9).

## Arms

1. **Gate Zero** — the unmodified reference above.
2. **Arm SHRINK** (sanctioned G-J2-lesson arm; FEATURES F4 context)
   — Gate Zero plus exactly one change at prediction time: for a
   team with fewer than 6 prior in-league matches in the training
   window, its fitted attack and defence ratings are shrunk toward
   the league mean: `a *= n/6`, `d *= n/6` where n = its prior
   in-league match count (n = 0 ⇒ a = d = 0, identical to Gate
   Zero's unseen rule; the arm bites exactly for teams with 1–5
   prior matches — the season-opener failure mode). Nothing else
   changes.
3. **Arm X2** — Gate Zero plus mover tier priors (feature X2, EDA
   F4), in the ENGCH X2 formulation. A club is a *mover* for target
   season S when its most recent prior season is the season
   immediately preceding S, it played that season in LaLiga (team
   present in the warehouse index for league_id 87 in that season)
   or in Primera Federación (league_id 8968), and it did not play
   LaLiga2 in that season. Membership is keyed by accent-normalised
   FotMob team name in the warehouse index (names map 1:1 onto team
   ids with no collisions — Phase 2 rule 9; the mover's ratings are
   the team_id-keyed fitted ratings). For a mover, at prediction
   time in season S only, with mu = the decay-weighted mean goals
   per team per match in the training window:
   - from LaLiga: attack `a += log((mu + 0.080) / mu)`; defence
     `d += log((mu - 0.171) / mu)`
   - from PrimeraFed: attack `a += log(max(mu - 0.025, 0.10) / mu)`;
     defence `d += log((mu + 0.111) / mu)`
   where +0.080 / −0.171 / −0.025 / +0.111 are the frozen F4
   magnitudes (entry-season GF/GA deltas vs league mu 1.191, pooled
   over the corpus's entry seasons). The offset is added to the
   fitted rating (league mean 0 for a first-time club). Nothing
   else changes.

## Dev protocol

- Training seed = 2021/2022; evaluation seasons 2022/2023, 2023/2024,
  2024/2025 (pooled n = 1,404) under the season-blocked walk-forward.
- Metrics per arm per season and pooled: mean 1X2 LL, mean RPS
  (H, D, A), mean OU2.5 LL. Baselines: climatology — for target
  season S, pooled outcome rates + OU2.5 over-rate of all seasons
  strictly before S.
- The dev harness must not read 2025/2026 or 2026/2027 rows at all.

## Virgin protocol

- Virgin = 2025/2026 (n = 468, complete), read ONCE, only for arms
  passing the dev gate, after dev results are frozen. Fit = all
  matches before the first 2025/2026 match date. Climatology =
  pooled 2021/2022–2024/2025 rates. Calibration: mean predicted −
  actual for home-win rate and OU2.5 over-rate, SE = sd(p_i − y_i)/√n.

## GATE LEGS (verbatim, frozen)

Dev gate — pooled dev 1X2 LL and RPS of an arm must beat climatology, and OU2.5 LL must beat the base-rate baseline, else the arm is dead. Virgin legs — (i) LL leg: arm's virgin 1X2 LL ≤ Gate Zero's AND ≤ climatology's; (ii) calibration leg: |mean predicted − actual| ≤ 1.0pp pooled for home-win rate and for OU2.5 over-rate, SEs reported; a breach within 1 SE of the boundary is recorded PROVISIONAL PASS, beyond it FAIL; (iii) per-season sign check on dev (arm LL ≤ Gate Zero LL in at least half the dev seasons) for the both-pass rule. Both-pass rule: if Gate Zero and a variant both pass all legs, the lower pooled virgin 1X2 LL ships; if only one passes, it ships; if none passes, G-ES verdict is FAIL and nothing ships.

Mechanical reading: an arm passes iff it survives the dev gate AND
passes virgin legs (i)–(ii) (PROVISIONAL counts, recorded as such)
AND, for variant arms, leg (iii); Gate Zero is exempt from (iii).
Ties go to the simpler arm (Gate Zero before SHRINK before X2). If
Gate Zero fails its own dev gate, variants are moot, verdict FAIL,
virgin NOT read.

## Outputs

Engine `league/ES-LaLiga2/engine/goals/`; dev results
`results_dev.json` (+ CSV); virgin `results_virgin.json`; fitted
params `fitted_params_virgin.json`; on PASS, virgin predictions
`league/ES-LaLiga2/predictions/g_es_virgin_predictions.csv`
(shipped arm; 1H/2H presentation via frozen goals constant 0.4322).
Verdict: `league/ES-LaLiga2/reports/G_ES_VERDICT.md`.
Production code untouched. No push. No merge.
