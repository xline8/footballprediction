# Pre-registration — G-COA (CO-PrimeraA goals model)

Frozen: 2026-11-09, before any fitting. Branch `build/co-primeraa`.
Design authority: `league/CO-PrimeraA/analysis/MODEL_DESIGN.md`;
features per `league/CO-PrimeraA/analysis/FEATURES.md` (X1 reduced
goals-only; X2 adopted; SHRINK not registered — degenerate here);
evidence per `league/CO-PrimeraA/analysis/EDA.md` (F1/F2/F4).
Reference: production Dixon-Coles in `model_v2.py`, config hl = 270,
as ported in `league/CO-PrimeraB/prereg/PREREG_G_CO.md` and
`league/PY-DivisionProfesional/prereg/PREREG_G_PY.md`.

## Reference architecture (all arms share this unless an arm says otherwise)

- Dixon-Coles fit, production pattern: iterative multiplicative
  updates, 14 sweeps, damping 0.7, +0.25 smoothing, home advantage
  `h` fitted (init 0.28), attack `a`/defence `d` per team (init 0),
  score matrix to MAXG = 10 with the production `tau` correction.
  Lambdas: lam_h = exp(a_home + d_away + h), lam_a = exp(a_away +
  d_home) — `d` is defence weakness (multiplies goals conceded).
- Rho per fit from grid (0.0, −0.05, −0.10, −0.15) by weighted
  log-likelihood on goals only.
- Observation: goals only (stats-feed xG exists only from
  2025 - Clausura — the production blend's documented goals-only
  fallback applies to the dev era; FEATURES X1).
- Time decay: w = 0.5 ** ((cutoff − match_date).days / 270), frozen.
- Fit scope for target tournament S: all CO-PrimeraA matches with
  date strictly before the first match date of S (expanding,
  tournament-blocked: one fit per target tournament, whole
  tournament predicted from that fit). All phases modelled, phase
  flagged, no phase feature (frozen phase rule).
- Teams unseen in training start at the league mean (a = d = 0).
- Team identity = FotMob team_id.

## Arms

1. **Gate Zero** — the unmodified reference above.
2. **Arm X2** — Gate Zero plus exactly one change at prediction
   time: for a team flagged `mover_up` for calendar year Y (absent
   from Primera A in Y−1, present in Primera B — FotMob id 9125 —
   in Y−1; flags frozen in the CSV by the data builder), its fitted
   attack and defence ratings are REPLACED by the frozen cross-tier
   offsets `a = ln(0.81)`, `d = ln(1.18)`, estimated from dev-era
   (2022–2025) promoted arrivals only (EDA F4: ΔGF −0.217/m,
   ΔGA +0.200/m vs the per-team base 1.1235 → attack ×0.81,
   concession ×1.18). Applies to that calendar year's predictions
   (both tournaments). Nothing else changes.

No SHRINK arm: at every dev tournament start the only <6-prior clubs
are the promoted clubs at exactly 0 priors, where shrinkage is
identical to Gate Zero's unseen rule (EDA F4; GE/BG2 precedent).

## Dev protocol

- Dev period: seed 2021 - Apertura + 2021 - Clausura (n = 411,
  training only); evaluation tournaments 2022 - Apertura …
  2025 - Clausura (9 tournaments, pooled n = 1,788) under the
  expanding tournament-blocked walk-forward above.
- Metrics per arm per tournament and pooled: mean 1X2 LL (natural
  log), mean RPS (H, D, A), mean OU2.5 LL (binary, on P(over 2.5)).
- Baselines: climatology — for target tournament S, the pooled
  outcome rates (H/D/A) and OU2.5 over-rate of all CO-A tournaments
  strictly before S. PLUS a naive trailing-10 baseline, REPORTING
  ONLY (never a gate leg): per target match, from matches strictly
  before it, atk10/def10 = team's mean goals scored/conceded over
  its last 10 matches (fallback: the fit window's per-team mean);
  lam_h = mu_h·(atk10_home/mu)·(def10_away/mu), lam_a =
  mu_a·(atk10_away/mu)·(def10_home/mu), with mu, mu_h, mu_a from the
  DC fit window for that target tournament; independent-Poisson
  probabilities (rho = 0).
- The dev harness must not read 2026 - Apertura or 2026 - Clausura
  rows at all.

## Virgin protocol

- Virgin window: **2026 - Apertura (n = 204, complete tournament)**,
  read ONCE, only for arms passing the dev gate, after dev results
  are frozen. Fit = all matches dated before the first
  2026 - Apertura match (2021-Ap…2025-Cl). 2026 - Clausura is NOT
  read (in progress; excluded everywhere in this build).
- Virgin climatology: pooled rates through 2025 - Clausura. Virgin
  naive: as in dev, fit window through 2025 - Clausura.
- Calibration per arm: (i) mean predicted home-win prob − actual
  home-win rate; (ii) mean predicted P(over 2.5) − actual over-rate.
  SE = sd(pred_i − y_i)/√n over the 204 matches. (Verdicts report
  calibration as actual − predicted; the gate uses |breach|.)

## GATE LEGS (verbatim, frozen)

Dev gate — pooled dev 1X2 LL and RPS of an arm must beat climatology, and OU2.5 LL must beat the base-rate baseline, else the arm is dead. Virgin legs — (i) LL leg: arm's virgin 1X2 LL ≤ Gate Zero's AND ≤ climatology's; (ii) calibration leg: |mean predicted − actual| ≤ 1.0pp pooled for home-win rate and for OU2.5 over-rate, SEs reported; a breach within 1 SE of the boundary is recorded PROVISIONAL PASS, beyond it FAIL; (iii) per-season sign check on dev (arm LL ≤ Gate Zero LL in at least half the dev seasons) for the both-pass rule. Both-pass rule: if Gate Zero and a variant both pass all legs, the lower pooled virgin 1X2 LL ships; if only one passes, it ships; if none passes, G-COA verdict is FAIL and nothing ships.

Mechanical reading: an arm passes iff it survives the dev gate AND
passes virgin legs (i)–(ii) (a PROVISIONAL PASS counts as a pass,
recorded as such) AND, for variant arms only, leg (iii). Gate Zero
is exempt from (iii). If Gate Zero fails its own dev gate, variants
are moot, verdict FAIL, virgin NOT read. Ties → simpler arm
(Gate Zero before X2).

## Outputs

- Engine: `league/CO-PrimeraA/engine/goals/` (own code + README).
- Dev results: `league/CO-PrimeraA/engine/goals/results_dev.json` (+ CSV).
- Virgin results: `league/CO-PrimeraA/engine/goals/results_virgin.json`;
  fitted params `fitted_params_virgin.json`.
- On PASS: virgin predictions `league/CO-PrimeraA/predictions/
  g_coa_virgin_predictions.csv` (shipped arm; FT lambdas, FT 1X2 /
  OU 1.5/2.5/3.5 / BTTS, and 1H/2H OU lines derived by splitting the
  lambdas with the frozen constant 0.4706 — presentation only).
- Verdict: `league/CO-PrimeraA/reports/G_COA_VERDICT.md`.

Production code and data untouched. No push. No merge.
