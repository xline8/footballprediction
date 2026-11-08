# Pre-registration — G-BR (BR-SerieA goals model)

Frozen: 2026-11-09, before any fitting. Branch `build/br-seriea`.
Design authority: `league/BR-SerieA/analysis/MODEL_DESIGN.md`
(G-BR); features per `analysis/FEATURES.md` (X1 blend pair, X2
mover offset, X3 set-play, SHRINK prior); evidence per
`analysis/EDA.md` (F1/F2/F4/F5/F11). Reference: production
Dixon-Coles in `model_v2.py` (class `DC`), hl = 270; J1 analogue:
`league/J1/prereg/PREREG_G_J1.md`.

## Reference architecture (all arms share unless an arm says otherwise)

- Dixon-Coles fit, copied pattern from production `model_v2.py`:
  iterative multiplicative updates, 14 sweeps, damping 0.7, +0.25
  smoothing, home advantage fitted (init 0.28), attack/defence per
  team (init 0), score matrix MAXG = 10, production `tau` correction.
- Rho per fit from grid (0.0, −0.05, −0.10, −0.15) by weighted
  log-likelihood on goals only, as production.
- Observation (X1): blend 0.5·goals + 0.5·xG when both xG present,
  goals-only fallback otherwise. BR xG coverage is ~7–10% in
  2021/2022 and ~100% from 2023, so the blend is goals-only in
  effect for early fits and a true blend later — the reference's
  own fallback, not a design change. xG = `expected_goals_home/away`.
- Time decay w = 0.5 ** ((cutoff − match_date).days / 270); blend
  weight 0.5 — both frozen, no search.
- Fit scope for target season S: all BR matches dated strictly
  before the first match date of S (expanding, season-blocked).
- Teams unseen in training start at the league mean (a = d = 0).

## Arms

1. **Gate Zero** — the unmodified reference above.
2. **Arm SHRINK** (sanctioned G-J2-lesson arm; FEATURES) — Gate
   Zero plus exactly one change at prediction time: for a team with
   fewer than 6 prior in-league matches in the training window, its
   fitted attack and defence ratings are shrunk toward the league
   mean: `a *= n/6`, `d *= n/6` where n = its prior in-league match
   count (n = 0 ⇒ a = d = 0, identical to Gate Zero's unseen rule;
   the arm bites exactly for teams with 1–5 prior matches — the
   season-opener failure mode). Nothing else changes.
3. **Arm X2** — Gate Zero plus cross-tier priors (feature X2, EDA
   F4). A club is a *promoted mover* for target season S when its
   most recent prior season is the season immediately preceding S,
   it played that season in Série B (team name present in the
   warehouse index for league_id 8814 that season), and it did not
   play Série A in that season. For a promoted mover, at prediction
   time in season S only:
   - attack: `a += log(max(mu − 0.23, 0.10) / mu)`
   - defence: `d += log((mu + 0.51) / mu)`
   where mu is the decay-weighted mean goals per team per match in
   the training window, and −0.23 / +0.51 are the pooled F4
   magnitudes (promoted sides' own-level change on arrival,
   2022–2025 transitions: GF −0.32/−0.07/−0.23/−0.30, GA
   +0.51/+0.50/+0.59/+0.45). The offset is added to the fitted
   rating (league mean 0 for a first-time club). A club entering
   from a higher tier would receive the mirrored offset; no such
   entry exists into Série A, the top tier, so this case is
   definitional only. Clubs with no immediately-preceding-season
   record in Série A or B start at the league mean in every arm.
   X2 does NOT stack on SHRINK.
4. **Arm X3** — Arm X2 plus the set-play decomposition tilt of
   `PREREG_G_J1.md` arm X3, verbatim in form: decay-weighted
   open-play/set-play xG for/against per team over the training
   window; `att_mult = sqrt((op_for/L_op)·(sp_for/L_sp))`,
   `def_mult` mirrored, clamped [0.5, 2.0]; lambdas tilted by
   `sqrt(att_mult · def_mult_opp)`; teams with <8 xG matches in the
   window get multiplier 1.0. Because BR xG is sparse before 2023,
   X3 ≡ X2 for target season 2022 by construction and activates
   only as xG-covered windows accumulate — recorded, not a defect.

## Dev protocol

- Training seed = 2021; evaluation seasons 2022, 2023, 2024
  (pooled n = 1,140) under the season-blocked walk-forward.
- Metrics per arm per season and pooled: mean 1X2 LL, mean RPS
  (H, D, A), mean OU2.5 LL. Baselines: climatology — for target
  season S, pooled outcome rates + OU2.5 over-rate of all seasons
  strictly before S.
- The dev harness must not read 2025 or 2026 rows at all.

## Virgin protocol

- Virgin = 2025 (n = 380, complete), read ONCE, only for arms
  passing the dev gate, after dev results are frozen. Fit = all
  matches before the first 2025 match date. Climatology = pooled
  2021–2024 rates. Calibration: mean predicted − actual for
  home-win rate and OU2.5 over-rate, SE = sd(p_i − y_i)/√n.
- 2026 (partial) is NOT read in this build; it is the reserved
  confirmatory window.

## GATE LEGS (verbatim, frozen)

Dev gate — pooled dev 1X2 LL and RPS of an arm must beat climatology, and OU2.5 LL must beat the base-rate baseline, else the arm is dead. Virgin legs — (i) LL leg: arm's virgin 1X2 LL ≤ Gate Zero's AND ≤ climatology's; (ii) calibration leg: |mean predicted − actual| ≤ 1.0pp pooled for home-win rate and for OU2.5 over-rate, SEs reported; a breach within 1 SE of the boundary is recorded PROVISIONAL PASS, beyond it FAIL; (iii) per-season sign check on dev (arm LL ≤ Gate Zero LL in at least half the dev seasons) for the both-pass rule. Both-pass rule: if Gate Zero and a variant both pass all legs, the lower pooled virgin 1X2 LL ships; if only one passes, it ships; if none passes, G-BR verdict is FAIL and nothing ships.

Mechanical reading: an arm passes iff it survives the dev gate AND
passes virgin legs (i)–(ii) (PROVISIONAL counts, recorded as such)
AND, for variant arms, leg (iii); Gate Zero is exempt from (iii).
Ties go to the simpler arm (Gate Zero before SHRINK before X2
before X3). If Gate Zero fails its own dev gate, variants are
moot, verdict FAIL, virgin NOT read.

## Outputs

Engine `league/BR-SerieA/engine/goals/`; dev results
`results_dev.json` (+ CSV); virgin `results_virgin.json`; fitted
params `fitted_params_virgin.json`; on PASS, virgin predictions
`league/BR-SerieA/predictions/g_br_virgin_predictions.csv`
(shipped arm; 1H/2H presentation via frozen goals constant 0.455).
Verdict: `league/BR-SerieA/reports/G_BR_VERDICT.md`.
Production code untouched. No push. No merge.
