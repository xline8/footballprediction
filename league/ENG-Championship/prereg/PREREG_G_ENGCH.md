# Pre-registration — G-ENGCH (ENG-Championship goals model)

Frozen: 2026-11-09, before any fitting. Branch `build/eng-championship`.
Design authority: `league/ENG-Championship/analysis/MODEL_DESIGN.md`
(G-ENGCH); features per `analysis/FEATURES.md` (X1 blend pair, X2
mover tier offset); evidence per `analysis/EDA.md` (F1/F2/F4/F11).
Reference: production Dixon-Coles in `model_v2.py` (class `DC`),
hl = 270; J1 analogue: `league/J1/prereg/PREREG_G_J1.md`.

## Reference architecture (all arms share unless an arm says otherwise)

- Dixon-Coles fit, copied pattern from production `model_v2.py`:
  iterative multiplicative updates, 14 sweeps, damping 0.7, +0.25
  smoothing, home advantage fitted (init 0.28), attack/defence per
  team (init 0), score matrix MAXG = 10, production `tau` correction.
- Rho per fit from grid (0.0, −0.05, −0.10, −0.15) by weighted
  log-likelihood on goals only, as production.
- Observation (X1): blend 0.5·goals + 0.5·xG when both xG present,
  goals-only fallback otherwise. ENGCH has xG in every match, so the
  fallback is definitional only. xG = `expected_goals_home/away`.
- Time decay w = 0.5 ** ((cutoff − match_date).days / 270); blend
  weight 0.5 — both frozen, no search.
- Fit scope for target season S: all ENGCH matches dated strictly
  before the first match date of S (expanding, season-blocked).
- Teams unseen in training start at the league mean (a = d = 0).

## Arms

1. **Gate Zero** — the unmodified reference above.
2. **Arm SHRINK** (sanctioned G-J2-lesson arm; FEATURES F4) — Gate
   Zero plus exactly one change at prediction time: for a team with
   fewer than 6 prior in-league matches in the training window, its
   fitted attack and defence ratings are shrunk toward the league
   mean: `a *= n/6`, `d *= n/6` where n = its prior in-league match
   count (n = 0 ⇒ a = d = 0, identical to Gate Zero's unseen rule;
   the arm bites exactly for teams with 1–5 prior matches — the
   season-opener failure mode). Nothing else changes.
3. **Arm X2** — Gate Zero plus mover tier priors (feature X2, EDA
   F4), in the J1 X2 formulation. A club is a *mover* for target
   season S when its most recent prior season is the season
   immediately preceding S, it played that season in the Premier
   League (team name present in the warehouse index for league_id
   47 in that season) or in League One (league_id 108), and it did
   not play the Championship in that season. For a mover, at
   prediction time in season S only, with mu = the decay-weighted
   mean goals per team per match in the training window:
   - from PL: attack `a += log((mu + 0.309) / mu)`; defence
     `d += log((mu - 0.181) / mu)`
   - from L1: attack `a += log(max(mu - 0.031, 0.10) / mu)`; defence
     `d += log((mu + 0.122) / mu)`
   where +0.309 / -0.181 / -0.031 / +0.122 are the frozen F4
   magnitudes (entry-season GF/GA deltas vs league mu, pooled over
   the corpus's entry seasons). The offset is added to the fitted
   rating (league mean 0 for a first-time club). Nothing else
   changes. Mover membership is keyed by FotMob team name in the
   warehouse index (names are consistent across the three tiers).
   X3 (set-play) is a measured signal (F5 r=0.721) but is NOT an
   arm in this build — see FEATURES.md; the arm cap is respected.

## Dev protocol

- Training seed = 2021/2022; evaluation seasons 2022/2023, 2023/2024,
  2024/2025 (pooled n = 1,671) under the season-blocked walk-forward.
- Metrics per arm per season and pooled: mean 1X2 LL, mean RPS
  (H, D, A), mean OU2.5 LL. Baselines: climatology — for target
  season S, pooled outcome rates + OU2.5 over-rate of all seasons
  strictly before S.
- The dev harness must not read 2025/2026 or 2026/2027 rows at all.

## Virgin protocol

- Virgin = 2025/2026 (n = 555, complete), read ONCE, only for arms
  passing the dev gate, after dev results are frozen. Fit = all
  matches before the first 2025/2026 match date. Climatology =
  pooled 2021/2022–2024/2025 rates. Calibration: mean predicted −
  actual for home-win rate and OU2.5 over-rate, SE = sd(p_i − y_i)/√n.

## GATE LEGS (verbatim, frozen)

Dev gate — pooled dev 1X2 LL and RPS of an arm must beat climatology, and OU2.5 LL must beat the base-rate baseline, else the arm is dead. Virgin legs — (i) LL leg: arm's virgin 1X2 LL ≤ Gate Zero's AND ≤ climatology's; (ii) calibration leg: |mean predicted − actual| ≤ 1.0pp pooled for home-win rate and for OU2.5 over-rate, SEs reported; a breach within 1 SE of the boundary is recorded PROVISIONAL PASS, beyond it FAIL; (iii) per-season sign check on dev (arm LL ≤ Gate Zero LL in at least half the dev seasons) for the both-pass rule. Both-pass rule: if Gate Zero and a variant both pass all legs, the lower pooled virgin 1X2 LL ships; if only one passes, it ships; if none passes, G-ENGCH verdict is FAIL and nothing ships.

Mechanical reading: an arm passes iff it survives the dev gate AND
passes virgin legs (i)–(ii) (PROVISIONAL counts, recorded as such)
AND, for variant arms, leg (iii); Gate Zero is exempt from (iii).
Ties go to the simpler arm (Gate Zero before SHRINK before X2). If
Gate Zero fails its own dev gate, variants are moot, verdict FAIL,
virgin NOT read.

## Outputs

Engine `league/ENG-Championship/engine/goals/`; dev results
`results_dev.json` (+ CSV); virgin `results_virgin.json`; fitted
params `fitted_params_virgin.json`; on PASS, virgin predictions
`league/ENG-Championship/predictions/g_engch_virgin_predictions.csv`
(shipped arm; 1H/2H presentation via frozen goals constant 0.4453).
Verdict: `league/ENG-Championship/reports/G_ENGCH_VERDICT.md`.
Production code untouched. No push. No merge.
