# Pre-registration — G-CO (CO-PrimeraB goals model)

Frozen: 2026-11-09, before any fitting. Branch `build/co-primerab`.
Design authority: `league/CO-PrimeraB/analysis/MODEL_DESIGN.md`;
features per `league/CO-PrimeraB/analysis/FEATURES.md`; evidence per
`league/CO-PrimeraB/analysis/EDA.md` (F1/F2/F4). Reference:
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
- Fit scope for target season S: all CO-PrimeraB matches with date
  strictly before the first match date of S (expanding,
  season-blocked: one fit per target season, whole season predicted
  from that fit). Season = calendar year (Apertura + Clausura +
  quadrangular + finals, per the frozen phase rule in
  DATA_UNDERSTANDING — all phases modelled, no phase feature).
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
   the season-opener/new-club failure mode of the G-J2 post-mortem;
   in this league two 2022 target clubs sit at 3 and 5 priors because
   the 2021 seed is partial). Nothing else changes.
3. **Arm X2** — Gate Zero plus exactly one change at prediction
   time: for a team flagged `mover_down` for season S (absent from
   Primera B in S−1, present in Primera A — FotMob id 274 — in
   calendar year S−1; flags frozen in the CSV by the data builder),
   its fitted attack and defence ratings are REPLACED by the frozen
   cross-tier offsets `a = ln(1.10)`, `d = ln(0.73)`, estimated from
   dev-era (2023–2024) relegated arrivals only (EDA F4: ΔGF +0.11/m,
   ΔGA −0.30/m vs the B mean). Nothing else changes.

## Dev protocol

- Dev period: seasons 2021–2024. Season 2021 (partial, n = 144
  finished) is the initial training window; evaluation seasons
  2022, 2023, 2024 under the expanding season-blocked walk-forward
  above. Pooled dev = the three evaluation seasons combined
  (n = 909).
- Metrics per arm per season and pooled: mean 1X2 LL (natural log),
  mean RPS (H, D, A), mean OU2.5 LL (binary, on P(over 2.5)).
- Baselines: climatology — for target season S, the pooled outcome
  rates (H/D/A) and OU2.5 over-rate of all CO seasons strictly
  before S, scoring that season. PLUS a naive trailing-10 baseline,
  REPORTING ONLY (never a gate leg): per target match, from matches
  strictly before it, atk10/def10 = team's mean goals scored /
  conceded over its last 10 matches (fallback: the fit window's
  per-team mean mu); lam_h = mu_h·(atk10_home/mu)·(def10_away/mu),
  lam_a = mu_a·(atk10_away/mu)·(def10_home/mu), with mu, mu_h, mu_a
  from the DC fit window for that target season; independent-Poisson
  probabilities (rho = 0).
- The dev harness must not read season 2025 or 2026 rows at all.

## Virgin protocol

- Virgin window: season 2025 (n = 308, last complete calendar
  year). Fit = all matches dated before the first 2025 match
  (2021–2024). Read ONCE, only for arms passing the dev gate, after
  dev results are frozen.
- Virgin climatology: pooled 2021–2024 outcome rates + OU2.5 rate.
  Virgin naive: as in dev, fit window 2021–2024.
- Calibration per arm: (i) mean predicted home-win prob − actual
  home-win rate; (ii) mean predicted P(over 2.5) − actual over-rate.
  SE = sd(pred_i − y_i)/√n over the 308 matches.

## GATE LEGS (verbatim, frozen)

Dev gate — pooled dev 1X2 LL and RPS of an arm must beat climatology, and OU2.5 LL must beat the base-rate baseline, else the arm is dead. Virgin legs — (i) LL leg: arm's virgin 1X2 LL ≤ Gate Zero's AND ≤ climatology's; (ii) calibration leg: |mean predicted − actual| ≤ 1.0pp pooled for home-win rate and for OU2.5 over-rate, SEs reported; a breach within 1 SE of the boundary is recorded PROVISIONAL PASS, beyond it FAIL; (iii) per-season sign check on dev (arm LL ≤ Gate Zero LL in at least half the dev seasons) for the both-pass rule. Both-pass rule: if Gate Zero and a variant both pass all legs, the lower pooled virgin 1X2 LL ships; if only one passes, it ships; if none passes, G-CO verdict is FAIL and nothing ships.

Mechanical reading: an arm passes iff it survives the dev gate AND
passes virgin legs (i)–(ii) (a PROVISIONAL PASS counts as a pass,
recorded as such) AND, for variant arms only, leg (iii). Gate Zero
is exempt from (iii). If Gate Zero fails its own dev gate, variants
are moot, verdict FAIL, virgin NOT read. Ties → simpler arm
(Gate Zero before SHRINK before X2).

## Outputs

- Engine: `league/CO-PrimeraB/engine/goals/` (own code + README).
- Dev results: `league/CO-PrimeraB/engine/goals/results_dev.json` (+ CSV).
- Virgin results: `league/CO-PrimeraB/engine/goals/results_virgin.json`;
  fitted params `fitted_params_virgin.json`.
- On PASS: virgin predictions `league/CO-PrimeraB/predictions/
  g_co_virgin_predictions.csv` (shipped arm; FT lambdas, FT 1X2 /
  OU 1.5/2.5/3.5 / BTTS, and 1H/2H OU lines derived by splitting the
  lambdas with the frozen constant 0.4875 — presentation only).
- Verdict: `league/CO-PrimeraB/reports/G_CO_VERDICT.md`.

Production code and data untouched. No push. No merge.
