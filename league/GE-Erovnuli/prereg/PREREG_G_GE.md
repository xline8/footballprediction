# Pre-registration — G-GE (GE-Erovnuli goals model)

Frozen: 2026-11-09, before any fitting. Branch `build/ge-erovnuli`.
Design authority: `league/GE-Erovnuli/analysis/MODEL_DESIGN.md`;
features per `league/GE-Erovnuli/analysis/FEATURES.md`; evidence per
`league/GE-Erovnuli/analysis/EDA.md` (F1/F2/F4). Reference:
production Dixon-Coles in `model_v2.py`, config hl = 270.

## Reference architecture (all arms share this unless an arm says otherwise)

- Dixon-Coles fit, production pattern: iterative multiplicative
  updates, 14 sweeps, damping 0.7, +0.25 smoothing, home advantage
  `h` fitted (init 0.28), attack `a`/defence `d` per team (init 0),
  score matrix to MAXG = 10 with the production `tau` correction.
- Rho per fit from grid (0.0, −0.05, −0.10, −0.15) by weighted
  log-likelihood on goals only.
- Observation: goals only (no xG exists in this league — the
  production blend's documented fallback).
- Time decay: w = 0.5 ** ((cutoff − match_date).days / 270), frozen.
- Fit scope for target season S: all GE matches with date strictly
  before the first match date of S (expanding, season-blocked: one
  fit per target season, whole season predicted from that fit).
- Teams unseen in training start at the league mean (a = d = 0).
- Team identity = FotMob team_id.

## Arms

1. **Gate Zero** — the unmodified reference above.
2. **Arm SHRINK** — Gate Zero plus exactly one change at prediction
   time: for a team with fewer than 6 prior in-league matches in the
   training window, its fitted attack and defence ratings are shrunk
   toward the league mean: `a *= n/6`, `d *= n/6`, n = prior in-league
   match count (n = 0 ⇒ a = d = 0, identical to Gate Zero's unseen
   rule; the arm bites exactly for teams with 1–5 prior matches —
   the season-opener/new-club failure mode of the G-J2 post-mortem).
   Nothing else changes.

## Dev protocol

- Dev period: seasons 2021–2024. Season 2021 is the initial training
  window; evaluation seasons 2022, 2023, 2024 under the expanding
  season-blocked walk-forward above. Pooled dev = the three
  evaluation seasons combined (n = 540).
- Metrics per arm per season and pooled: mean 1X2 LL (natural log),
  mean RPS (H, D, A), mean OU2.5 LL (binary, on P(over 2.5)).
- Baselines: climatology — for target season S, the pooled outcome
  rates (H/D/A) and OU2.5 over-rate of all GE seasons strictly
  before S, scoring that season.
- The dev harness must not read season 2025 or 2026 rows at all.

## Virgin protocol

- Virgin window: season 2025 (n = 180, complete). Fit = all matches
  dated before the first 2025 match (2021–2024). Read ONCE, only for
  arms passing the dev gate, after dev results are frozen.
- Virgin climatology: pooled 2021–2024 outcome rates + OU2.5 rate.
- Calibration per arm: (i) mean predicted home-win prob − actual
  home-win rate; (ii) mean predicted P(over 2.5) − actual over-rate.
  SE = sd(pred_i − y_i)/√n over the 180 matches.

## GATE LEGS (verbatim, frozen)

Dev gate — pooled dev 1X2 LL and RPS of an arm must beat climatology, and OU2.5 LL must beat the base-rate baseline, else the arm is dead. Virgin legs — (i) LL leg: arm's virgin 1X2 LL ≤ Gate Zero's AND ≤ climatology's; (ii) calibration leg: |mean predicted − actual| ≤ 1.0pp pooled for home-win rate and for OU2.5 over-rate, SEs reported; a breach within 1 SE of the boundary is recorded PROVISIONAL PASS, beyond it FAIL; (iii) per-season sign check on dev (arm LL ≤ Gate Zero LL in at least half the dev seasons) for the both-pass rule. Both-pass rule: if Gate Zero and a variant both pass all legs, the lower pooled virgin 1X2 LL ships; if only one passes, it ships; if none passes, G-GE verdict is FAIL and nothing ships.

Mechanical reading: an arm passes iff it survives the dev gate AND
passes virgin legs (i)–(ii) (a PROVISIONAL PASS counts as a pass,
recorded as such) AND, for variant arms only, leg (iii). Gate Zero
is exempt from (iii). If Gate Zero fails its own dev gate, variants
are moot, verdict FAIL, virgin NOT read. Ties → simpler arm
(Gate Zero before SHRINK).

## Outputs

- Engine: `league/GE-Erovnuli/engine/goals/` (own code + README).
- Dev results: `league/GE-Erovnuli/engine/goals/results_dev.json` (+ CSV).
- Virgin results: `league/GE-Erovnuli/engine/goals/results_virgin.json`;
  fitted params `fitted_params_virgin.json`.
- On PASS: virgin predictions `league/GE-Erovnuli/predictions/
  g_ge_virgin_predictions.csv` (shipped arm; FT lambdas, FT 1X2 /
  OU 1.5/2.5/3.5 / BTTS, and 1H/2H OU lines derived by splitting the
  lambdas with the frozen constant 0.4516 — presentation only).
- Verdict: `league/GE-Erovnuli/reports/G_GE_VERDICT.md`.

Production code and data untouched. No push. No merge.
