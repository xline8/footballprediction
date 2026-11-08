# Pre-registration — G-AU (AU A-League goals model)

Frozen: 2026-11-09, before any fitting. Branch `build/au-aleague`.
Design authority: `league/AU-ALeague/analysis/MODEL_DESIGN.md`
(G-AU); features per `analysis/FEATURES.md` (X1 blend pair, X3
set-play); evidence per `analysis/EDA.md` (F1/F2/F4/F5/F11).
Reference: production Dixon-Coles in `model_v2.py` (class `DC`),
hl = 270; J1 analogue: `league/J1/prereg/PREREG_G_J1.md`; DK
analogue: `PREREG_G_DK.md` (same construction, AU windows/lines).

## Reference architecture (all arms share unless an arm says otherwise)

- Dixon-Coles fit, copied pattern from production `model_v2.py`:
  iterative multiplicative updates, 14 sweeps, damping 0.7, +0.25
  smoothing, home advantage fitted (init 0.28), attack/defence per
  team (init 0), score matrix MAXG = 10, production `tau` correction.
- Rho per fit from grid (0.0, −0.05, −0.10, −0.15) by weighted
  log-likelihood on goals only, as production.
- Observation (X1): blend 0.5·goals + 0.5·xG when both xG present,
  goals-only fallback otherwise. AU has xG in every match, so the
  fallback is definitional only. xG = `expected_goals_home/away`.
- Time decay w = 0.5 ** ((cutoff − match_date).days / 270); blend
  weight 0.5 — both frozen, no search.
- Fit scope for target season S: all AU matches dated strictly
  before the first match date of S (expanding, season-blocked).
  Finals Series matches are ordinary rows (PREPROCESSING rule 3).
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
   season-opener failure mode; Auckland FC's 2024/2025 entry is
   the AU case). Nothing else changes. (Recorded in advance, from
   the DK build: under season-blocked fitting this arm may prove
   degenerate — if so that is reported as a construction fact,
   not repaired mid-flight.)
3. **Arm X3** — Arm SHRINK plus the set-play decomposition tilt of
   `PREREG_G_J1.md` arm X3, verbatim in form: decay-weighted
   open-play/set-play xG for/against per team over the training
   window; `att_mult = sqrt((op_for/L_op)·(sp_for/L_sp))`,
   `def_mult` mirrored, clamped [0.5, 2.0]; lambdas tilted by
   `sqrt(att_mult · def_mult_opp)`; teams with <8 xG matches in the
   window get multiplier 1.0. (AU has no mover offset — X2 was
   DROPPED in FEATURES — so X3 builds on SHRINK, not on an X2 arm.)

## Dev protocol

- Training seed = 2021/2022; evaluation seasons 2022/2023,
  2023/2024, 2024/2025 (pooled n = 508) under the season-blocked
  walk-forward.
- Metrics per arm per season and pooled: mean 1X2 LL, mean RPS
  (H, D, A), mean OU2.5 LL. Baselines: climatology — for target
  season S, pooled outcome rates + OU2.5 over-rate of all seasons
  strictly before S.
- The dev harness must not read 2025/2026 or 2026/2027 rows at all.

## Virgin protocol

- Virgin = 2025/2026 (n = 163, complete), read ONCE, only for arms
  passing the dev gate, after dev results are frozen. Fit = all
  matches before the first 2025/2026 match date. Climatology =
  pooled 2021/2022–2024/2025 rates. Calibration: mean predicted −
  actual for home-win rate and OU2.5 over-rate, SE = sd(p_i − y_i)/√n.

## GATE LEGS (verbatim, frozen)

Dev gate — pooled dev 1X2 LL and RPS of an arm must beat climatology, and OU2.5 LL must beat the base-rate baseline, else the arm is dead. Virgin legs — (i) LL leg: arm's virgin 1X2 LL ≤ Gate Zero's AND ≤ climatology's; (ii) calibration leg: |mean predicted − actual| ≤ 1.0pp pooled for home-win rate and for OU2.5 over-rate, SEs reported; a breach within 1 SE of the boundary is recorded PROVISIONAL PASS, beyond it FAIL; (iii) per-season sign check on dev (arm LL ≤ Gate Zero LL in at least half the dev seasons) for the both-pass rule. Both-pass rule: if Gate Zero and a variant both pass all legs, the lower pooled virgin 1X2 LL ships; if only one passes, it ships; if none passes, G-AU verdict is FAIL and nothing ships.

Mechanical reading: an arm passes iff it survives the dev gate AND
passes virgin legs (i)–(ii) (PROVISIONAL counts, recorded as such)
AND, for variant arms, leg (iii); Gate Zero is exempt from (iii).
Ties go to the simpler arm (Gate Zero before SHRINK before X3). If
Gate Zero fails its own dev gate, variants are moot, verdict FAIL,
virgin NOT read.

## Outputs

Engine `league/AU-ALeague/engine/goals/`; dev results
`results_dev.json` (+ CSV); virgin `results_virgin.json`; fitted
params `fitted_params_virgin.json`; on PASS, virgin predictions
`league/AU-ALeague/predictions/g_au_virgin_predictions.csv`
(shipped arm; 1H/2H presentation via frozen goals constant 0.432).
Verdict: `league/AU-ALeague/reports/G_AU_VERDICT.md`.
Production code untouched. No push. No merge.
