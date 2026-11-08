# Pre-registration — G-J1 (J1 goals model)

Frozen: 2026-11-09, before any fitting. Branch `build/g-j1`.
Design authority: `league/J1/analysis/MODEL_DESIGN.md` §1 (candidate
G-J1) + shared validation frame + §7b; features per
`league/J1/analysis/FEATURES.md` (X1 blend pair, X2 cross-tier, X3
set-play); evidence per `league/J1/analysis/EDA.md` (F1/F2/F4/F5).
Reference implementation: production Dixon-Coles in `model_v2.py`
(class `DC`, `probs`), production config `v2_config.json` (hl = 270).

## Reference architecture (all arms share this unless an arm says otherwise)

- Dixon-Coles fit, copied pattern from production `model_v2.py`:
  iterative multiplicative updates, 14 sweeps, damping 0.7, +0.25
  smoothing, home advantage `h` fitted (init 0.28), attack `a` and
  defence `d` per team (init 0), score matrix to MAXG = 10 with the
  production `tau` low-score correction.
- Rho: chosen per fit from the grid (0.0, −0.05, −0.10, −0.15) by
  weighted log-likelihood on goals only, exactly as production.
- Observation (X1): blend 0.5·goals + 0.5·xG when both xG values are
  present, goals-only fallback otherwise. J1 2021 has no xG and
  therefore enters goals-only. xG = `expected_goals_home/away` in
  `league/J1/data/j1_matches.csv`.
- Time decay: weight w = 0.5 ** ((cutoff − match_date).days / 270).
  Half-life 270 days is the production value, frozen — no search.
  Blend weight 0.5 is frozen — no search.
- Fit scope for a target season S: all J1 matches with date strictly
  before the first match date of S (expanding window, season-blocked:
  one fit per target season, whole season predicted from that fit).
- Teams unseen in training start at the league mean (a = d = 0).

## Arms

1. **Gate Zero** — the unmodified reference above. Movers start at
   the league mean.
2. **Arm X2** — Gate Zero plus cross-tier priors (feature X2, EDA F4).
   A club is a *promoted mover* for target season S when its most
   recent prior season is the season immediately preceding S, it
   played that season in J2 (team id present in
   `league/J2/data/j2_matches.csv` for that season), and it did not
   play J1 in that season. For a promoted mover, at prediction time
   in season S only:
   - attack: `a += log(max(mu − 0.56, 0.10) / mu)`
   - defence: `d += log((mu + 0.51) / mu)`
   where mu is the decay-weighted mean goals per team per match in
   the training window, and −0.56 / +0.51 are the F4 magnitudes
   (GF −0.56, GA +0.51 per match on J2→J1 arrival). The offset is
   added to the fitted rating (league mean 0 for a first-time club).
   A club entering from a higher tier would receive the mirrored
   offset (+0.56 attack, −0.51 defence); no such entry exists into
   J1, the top tier, so this case is definitional only. Clubs with
   no immediately-preceding-season record in J1 or J2 start at the
   league mean in every arm.
3. **Arm X3** — Arm X2 plus an open-play/set-play decomposition tilt
   of the xG observation (feature X3, EDA F5). For each team, over
   its training-window J1 matches with xG present (decay-weighted,
   same half-life and cutoff), compute per-match open-play xG for
   (`op_for`) and against (`op_against`) and set-play xG for
   (`sp_for`) and against (`sp_against`), from
   `expected_goals_open_play_*` / `expected_goals_set_play_*`.
   League means `L_op`, `L_sp` are the decay-weighted league
   per-team-match means of the same quantities (for and against
   coincide league-wide). Multipliers:
   - `att_mult(t) = sqrt( (op_for/L_op) · (sp_for/L_sp) )`
   - `def_mult(t) = sqrt( (op_against/L_op) · (sp_against/L_sp) )`
   each clamped to [0.5, 2.0]. Predicted lambdas:
   - `lam_h(X3) = lam_h(X2) · sqrt( att_mult(home) · def_mult(away) )`
   - `lam_a(X3) = lam_a(X2) · sqrt( att_mult(away) · def_mult(home) )`
   The outer square root is a frozen shrinkage exponent (0.5) against
   double-counting the xG half of the blend. A team with fewer than
   8 xG matches in the training window gets multiplier 1.0 (arm
   inactive for that team). With a 2021-only training window (target
   2022) no xG exists, so X3 ≡ X2 for that season by construction.

## Dev protocol

- Dev period: seasons 2021–2025. Season 2021 is the initial training
  window; evaluation seasons are 2022, 2023, 2024, 2025 under the
  expanding season-blocked walk-forward above. Pooled dev = the four
  evaluation seasons combined.
- Metrics per arm per season and pooled: mean 1X2 log-loss (natural
  log), mean RPS (outcomes ordered H, D, A;
  RPS = 0.5 · Σ_k (Σ_{j≤k} p_j − Σ_{j≤k} y_j)²), mean OU2.5 log-loss
  (binary, on P(over 2.5)).
- Baselines: climatology — for target season S, the pooled outcome
  rates (home win / draw / away win) and OU2.5 over-rate of all J1
  seasons strictly before S. The same climatology probabilities score
  LL, RPS and OU LL for that season.
- The dev harness must not read season "2026" or "2026/2027" rows at
  all. Virgin data is touched only by the separate virgin step, once,
  after dev results are frozen in the results file.

## Virgin protocol

- Virgin window: season "2026" (n = 200, complete). Shootout draws
  count as draws (the stored score is the regulation score; result
  markets use it as-is). Fit = all J1 matches dated before the first
  2026 match (seasons 2021–2025). Read ONCE, after dev freezes.
- Virgin climatology: pooled 2021–2025 outcome rates and OU2.5
  over-rate.
- Calibration per arm: (i) mean predicted home-win probability minus
  actual home-win rate; (ii) mean predicted P(over 2.5) minus actual
  over-rate. Standard error of each difference:
  SE = sd(pred_i − y_i) / √n over the 200 matches, reported with the
  difference.

## GATE LEGS (verbatim, frozen)

Dev gate — pooled dev 1X2 LL and RPS of an arm must beat climatology, and OU2.5 LL must beat the base-rate baseline, else the arm is dead. Virgin legs — (i) LL leg: arm's virgin 1X2 LL ≤ Gate Zero's AND ≤ climatology's; (ii) calibration leg: |mean predicted − actual| ≤ 1.0pp pooled for home-win rate and for OU2.5 over-rate, SEs reported; a breach within 1 SE of the boundary is recorded PROVISIONAL PASS, beyond it FAIL; (iii) per-season sign check on dev (arm LL ≤ Gate Zero LL in at least half the dev seasons) for the both-pass rule. Both-pass rule: if Gate Zero and a variant both pass all legs, the lower pooled virgin 1X2 LL ships; if only one passes, it ships; if none passes, G-J1 verdict is FAIL and nothing ships.

Reading of the legs, fixed here so the verdict is mechanical:

- An arm *passes* iff it survives the dev gate AND passes virgin
  legs (i)–(ii) (a PROVISIONAL PASS counts as a pass, recorded as
  such) AND, for variant arms only, leg (iii). Gate Zero is exempt
  from (iii) (it is the comparator).
- If several variant arms pass together with Gate Zero, the
  both-pass rule's "lower pooled virgin 1X2 LL ships" applies across
  all passing arms; ties go to the simpler arm (Gate Zero before X2
  before X3).

## Outputs

- Engine: `league/J1/engine/goals/` (this league's own code:
  fit/predict/harness modules + a CLI runner).
- Dev results: `league/J1/engine/goals/results_dev.json` (+ CSV).
- Fitted parameters for the virgin fit:
  `league/J1/engine/goals/fitted_params_virgin.json`.
- Virgin predictions: `league/J1/predictions/g_j1_virgin_predictions.csv`
  — the shipped arm's predictions (Gate Zero's if nothing ships,
  labelled in the verdict), one row per 2026 match, with FT lambdas,
  FT 1X2 / OU (1.5, 2.5, 3.5) / BTTS probabilities, and 1H/2H lines
  derived by splitting the same lambdas with the frozen J1 goals
  constant 0.412 (1H λ = 0.412·FT λ, 2H λ = 0.588·FT λ; 1H OU lines
  0.5/1.5/2.5, 2H OU lines 1.5/2.5/3.5, same rho and score-matrix
  machinery). Halves are presentation only, never fitted (design §7b).
- Verdict: `league/J1/reports/G_J1_VERDICT.md`.

Production code and data are untouched. No push. No merge.
