# Pre-registration — G-PE (PE-Liga1 goals model)

Frozen: 2026-11-10, before any fitting. Branch `build/pe-liga1`.
Design authority: `league/PE-Liga1/analysis/MODEL_DESIGN.md` (G-PE);
features per `analysis/FEATURES.md` (X1 reduced goals-only; X2
adopted); evidence per `analysis/EDA.md` (F1/F2/F4). Reference:
production Dixon-Coles in `model_v2.py`, config hl = 270, as ported
in `league/CO-PrimeraA/prereg/PREREG_G_COA.md`.

## Reference architecture (all arms share this unless an arm says otherwise)

- Dixon-Coles fit, production pattern: iterative multiplicative
  updates, 14 sweeps, damping 0.7, +0.25 smoothing, home advantage
  `h` fitted (init 0.28), attack `a`/defence `d` per team (init 0),
  score matrix to MAXG = 10 with the production `tau` correction.
  Lambdas: lam_h = exp(a_home + d_away + h), lam_a = exp(a_away +
  d_home) — `d` is defence weakness (multiplies goals conceded).
- Rho per fit from grid (0.0, −0.05, −0.10, −0.15) by weighted
  log-likelihood on goals only.
- Observation: **goals only** (no xG exists in this corpus — the
  production blend's documented goals-only fallback applies to
  every era; FEATURES X1).
- Time decay: w = 0.5 ** ((cutoff − match_date).days / 270), frozen.
- Fit scope for target block S: all modelling-corpus matches
  (regular phase, non-awarded) with date strictly before the first
  match date of S (expanding, block-blocked: one fit per target
  block, whole block predicted from that fit).
- Teams unseen in training start at the league mean (a = d = 0).
- Team identity = FotMob team_id.

## Arms

1. **Gate Zero** — the unmodified reference above.
2. **Arm X2** — Gate Zero plus exactly one change at prediction
   time: for a team flagged entrant for calendar year Y (absent
   from Liga 1 in Y−1 per the CSV's `absent_prev` flags), its
   fitted attack and defence ratings are REPLACED by the frozen
   offsets `a = ln(0.9375) = −0.0645`, `d = ln(1.1078) = +0.1024`,
   estimated from dev-era (2022–2024) arrivals only (EDA F4:
   ΔGF −0.082/m, ΔGA +0.142/m vs the per-team base 1.317). Applies
   to that calendar year's predictions (both blocks). Nothing
   else changes.

No SHRINK arm: at every dev block start the only <6-prior clubs
are entrants at exactly 0 priors, where shrinkage is identical to
Gate Zero's unseen rule (CO-A precedent). No altitude arm
(FEATURES R-alt: measured, no class premium, collinear with team
identity).

## Dev protocol

- Seed: 2021 - Fase 1 + 2021 - Fase 2 (n = 234, training only).
- Evaluation blocks: 2022 - Apertura … 2024 - Clausura (6 blocks,
  pooled n = 982) under the expanding block-blocked walk-forward.
- Metrics per arm per block and pooled: mean 1X2 LL (natural log),
  mean RPS (H, D, A), mean OU2.5 LL (binary, on P(over 2.5)).
- Baselines: climatology — for target block S, the pooled outcome
  rates (H/D/A) and OU2.5 over-rate of all corpus blocks strictly
  before S. PLUS a naive trailing-10 baseline, REPORTING ONLY
  (never a gate leg), defined exactly as in PREREG_G_COA.
- The dev harness must not read 2025 or 2026 rows at all.

## Virgin protocol

- Virgin window: **calendar 2025 (Apertura + Clausura, n = 323)** —
  the last complete season — read ONCE, only for arms passing the
  dev gate, after dev results are frozen. Fit = all corpus matches
  dated before the first 2025 match. 2026 is NOT read (in
  progress; reserved confirmatory).
- Virgin climatology: pooled rates through 2024 - Clausura.
  Virgin naive: as in dev, fit window through 2024 - Clausura.
- Calibration per arm: (i) mean predicted home-win prob − actual
  home-win rate; (ii) mean predicted P(over 2.5) − actual over-rate.
  SE = sd(pred_i − y_i)/√n over the 323 matches. (Verdicts report
  calibration as actual − predicted; the gate uses |breach|.)

## GATE LEGS (verbatim, frozen)

Dev gate — pooled dev 1X2 LL and RPS of an arm must beat climatology, and OU2.5 LL must beat the base-rate baseline, else the arm is dead. Virgin legs — (i) LL leg: arm's virgin 1X2 LL ≤ Gate Zero's AND ≤ climatology's; (ii) calibration leg: |mean predicted − actual| ≤ 1.0pp pooled for home-win rate and for OU2.5 over-rate, SEs reported; a breach within 1 SE of the boundary is recorded PROVISIONAL PASS, beyond it FAIL; (iii) per-season sign check on dev (arm LL ≤ Gate Zero LL in at least half the dev seasons) for the both-pass rule. Both-pass rule: if Gate Zero and a variant both pass all legs, the lower pooled virgin 1X2 LL ships; if only one passes, it ships; if none passes, G-PE verdict is FAIL and nothing ships.

Mechanical reading: an arm passes iff it survives the dev gate AND
passes virgin legs (i)–(ii) (a PROVISIONAL PASS counts as a pass,
recorded as such) AND, for variant arms only, leg (iii). Gate Zero
is exempt from (iii). If Gate Zero fails its own dev gate, variants
are moot, verdict FAIL, virgin NOT read. Ties → simpler arm
(Gate Zero before X2).

## Outputs

- Engine: `league/PE-Liga1/engine/goals/` (own code + README).
- Dev results: `league/PE-Liga1/engine/goals/results_dev.json` (+ CSV).
- Virgin results: `league/PE-Liga1/engine/goals/results_virgin.json`;
  fitted params `fitted_params_virgin.json`.
- On PASS: virgin predictions `league/PE-Liga1/predictions/
  g_pe_virgin_predictions.csv` (shipped arm; FT lambdas, FT 1X2 /
  OU 1.5/2.5/3.5 / BTTS, and 1H/2H OU lines derived by splitting the
  lambdas with the frozen constant 0.4377 — presentation only).
- Verdict: `league/PE-Liga1/reports/G_PE_VERDICT.md`.

Production code and data untouched. No push. No merge.
