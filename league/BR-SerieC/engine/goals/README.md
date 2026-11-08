# G-BRC goals engine

Reads the BR-SerieC match data and evaluates the preregistered 1X2 and
OU goals arms. Use `python3 run_g_brc.py dev` for the recorded
development evaluation (from this directory). The virgin read is a
separate step (`virgin-metrics` / `virgin-predict --arm ...`), gated
on the per-arm dev gate — see PREREG_G_BRC.md.

## Inputs

- `../data/brc_matches.csv` — one row per finished match. Only
  `in_fit_set == 1` rows are ever fitted or scored (first phase +
  second-stage / Promotion Round groups; the 12 Final legs are
  excluded). xG columns do not exist: every row loads with
  `xgh = xga = None`, so the Dixon-Coles blend is goals-only in
  effect (the reference's own fallback).
- `../../BR-SerieB/data/brb_matches.csv` — read ONLY for Série B
  team-id sets per season, for mover identification.

## Arms (PREREG_G_BRC.md)

- **Gate Zero** — unmodified production Dixon-Coles copy (`dc.py`:
  14 sweeps, damping 0.7, +0.25 smoothing, home advantage fitted
  from 0.28, rho grid (0.0, −0.05, −0.10, −0.15), decay half-life
  270 days, score matrix MAXG = 10, production tau correction).
- **SHRINK** — at prediction time, a team with fewer than 6 prior
  in-league matches in the training window has its fitted attack
  and defence ratings multiplied by n/6 toward the league mean.
- **X2** — cross-tier priors in LAMBDA space (implemented as lambda
  multipliers; the rating-shift equivalent is log(multiplier)).
  With mu = the decay-weighted mean goals per team per match in the
  training window: ex-B movers multiply lambda_for by
  max(mu − 0.0405, 0.10)/mu and lambda_against by
  max(mu − 0.0868, 0.10)/mu; newcomer movers multiply lambda_for by
  max(mu − 0.0627, 0.10)/mu and lambda_against by (mu + 0.0667)/mu.
  The multipliers apply to the mover's own lambdas (as home team:
  its for-lambda and the opponent's against-lambda; mirrored away).
  X2 does not stack on SHRINK. Movers are identified BY TEAM ID:
  ex-B = in C(S) and B(S−1), not in C(S−1); newcomer = in C(S),
  in neither B(S−1) nor C(S−1). The derived sets are asserted
  against the frozen prereg id lists for 2022–2025 (`arms.py`).

## Dev protocol

Season-blocked walk-forward, seed 2021 (fit-set n=147), scored
2022–2025 (pooled fit-set n=856). Per season the fit uses all
fit-set matches strictly before that season's first match date.
Climatology = pooled outcome rates + OU2.5 over-rate of all fit-set
seasons strictly before the target season (expanding). The dev
loader allows seasons 2021–2025 only; `run_dev` asserts no 2026
row is loaded.

## Outputs

- `results_dev.json` + `results_dev.csv` — per arm × season (model
  and climatology) plus pooled rows: mean 1X2 LL, RPS, OU2.5 LL.
- `results_dev_predictions.csv` — per-match predictions for every
  scored match × arm (for independent recomputation of the headline
  numbers).
- `results_virgin.json`, `fitted_params_virgin.json` — only from
  the virgin step. `../predictions/g_brc_virgin_predictions.csv`
  only on PASS, shipped arm only.
- Halves presentation in predictions uses the frozen goals 1H
  share 0.443 (1H lambdas ×0.443, 2H ×0.557), consistently for the
  lambda columns and the 1H/2H probability columns.

## Rerun

```
cd league/BR-SerieC/engine/goals
python3 run_g_brc.py dev
```

The dev run is deterministic (verified: two runs byte-identical).
