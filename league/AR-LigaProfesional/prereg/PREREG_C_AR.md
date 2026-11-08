# Pre-registration — C-AR (Liga Profesional corners model)

Frozen: 2026-11-09, before any fitting. Branch `build/ar-liga`.
Design authority: `league/AR-LigaProfesional/analysis/MODEL_DESIGN.md` §3;
features per `FEATURES.md` (X5 corners naive, X7 opp-box touches,
X9 production territorial covariates); evidence per `EDA.md`
(F2/F9/F12). Reference implementation: production
`model_corners_v3.py`, as ported in `league/J1/engine/corners/`
(decay-weighted base rates + rolling-5 shots relative factors +
Negative Binomial total + territorial multiplier `exp(beta·z)`
clamped to [0.70, 1.43], betas and gamma fitted on a fit window
only, never on the test window).

## Data, target, lines

- Source: `league/AR-LigaProfesional/data/ar_matches.csv`. Target:
  `y = corners_home + corners_away` (stats feed), present for all
  matches. Dev mean (blocks 2021 – 2026 - Apertura) 9.20.
- Primary line **9.5** (dev over-rate 43.9%; ladder 8.5 / 9.5 /
  10.5 reported). All gate legs use binary log-loss at 9.5.
- Coverage of the covariates: X9 (possession + big chance) complete
  in every block. X7 (touches_opp_box) present in 188/325,
  168/378, 239/378 matches in 2021–2023 and 100% from
  2024; the FEATURES min-8 trailing rule makes the X7
  multiplier inactive where a team's window cannot be filled — the
  harness reports the active share per season.
- Dev folds: warm-up block 2021 (state building; the core is
  date-based, so early 2021 matches are predicted from little
  state and are NOT scored), scored blocks **2022, 2023, 2024,
  2025 - Apertura, 2025 - Clausura, 2026 - Apertura** (pooled
  n = 1,854), chronological (date, then match_id);
  every state quantity uses only matches with date strictly before
  the target match's date. This matches the J1 port's processing
  contract.

## Shared engine (both arms identical unless an arm says otherwise)

Exactly the `league/J1/engine/corners/core.py` machinery, constants
frozen at the production/J1-port values: base rates with
HL = 270 days; production moment ratio `r_base = Σ w·y² / Σ w·y`;
rolling-5 shots relative factors clamped [0.6, 1.7]; core mean
`mu_cs = bh·(fhp·fac)^gamma + ba·(fap·fhc)^gamma`; NB on
k = 0..50 normalised, size `k_nb = mu / (r − 1)` for r > 1.02 else
the Poisson limit; territorial multiplier `exp(beta·z)` clamped to
[0.70, 1.43] with z the trailing (min-8 of last-10) for-minus-
against covariate difference, standardised by the fit window's
league SD; gamma and betas selected on the **fit window only**
(the block preceding each scored block, rolling, exactly as the
J1 port's harness does) from the frozen grids in core.py
(GAMMAS, BP, BBC, BBT).

## Arms

1. **Gate Zero (GZ)** — the reference above with the production
   territorial covariates (X9): z from possession and big-chance
   trailing differences.
2. **Arm X7** — identical, except the territorial covariates are
   opp-box touches for/against (X7) instead of X9 (beta grid BBT).

## Baselines (harness, not models)

- **League base rate**: for target block S, P(over 9.5) = the
  over-9.5 rate of all matches in blocks strictly before S,
  scored as a constant probability.
- **Naive trailing-10**: trailing-10 team corner for/against means
  combined to a match total, scored through an NB whose size is the
  production moment ratio on the trailing window (the core's
  `r_base` machinery) — i.e. the count naive, not a model arm.

## Dev protocol

- Scored dev: blocks 2022 – 2026 - Apertura (n = 1,854). The dev
  harness must not read block "2026 - Clausura" rows at all.
- Metric: mean binary log-loss at line 9.5, per block and pooled,
  per arm and per baseline.

## Virgin protocol

- Virgin window: block "2026 - Clausura" (n = 240), read **ONCE**, only
  for arms that pass the dev gate, after dev results are frozen.
  The chronological state continues from the dev run's end.
- Virgin metrics per arm: LL@9.5; calibration = mean P(over 9.5)
  − actual over-9.5 rate, SE = sd(p_i − y_i)/√n reported.

## GATE LEGS (verbatim, frozen)

Dev gate — pooled dev LL@9.5 beats BOTH baselines (league base rate; naive trailing-10), else arm dead, no virgin read. Virgin legs — (i) LL@9.5 ≤ Gate Zero's and ≤ best baseline's; (ii) calibration |mean P(over 9.5) − actual| ≤ 1.0pp, SE reported, breach within 1 SE = PROVISIONAL PASS; (iii) dev per-block sign check for both-pass. Both-pass: both → lower pooled virgin LL ships; one → ships; none → FAIL.

Reading: leg (iii) = variant's dev LL@9.5 ≤ Gate Zero's in at least
half the dev blocks (≥ 3 of 6); Gate Zero exempt. An arm passes iff
it survives the dev gate AND passes virgin (i)–(ii) (PROVISIONAL
counts, recorded as such) AND, for the variant, (iii). Both-pass
across passing arms: lowest pooled virgin LL@9.5 ships; ties go to
Gate Zero. If no arm passes, C-AR verdict is FAIL, nothing ships.

## Forbidden

Half-share corner modelling (F3 — halves via the frozen constant
0.480 in presentation only); any covariate outside X7/X9 for the
multiplier; fitting gamma/betas on any scored or virgin window.

## Outputs

- Engine: `league/AR-LigaProfesional/engine/corners/`.
- Dev results: `league/AR-LigaProfesional/engine/corners/results_dev.json` (+ CSV).
- Virgin results: `league/AR-LigaProfesional/engine/corners/results_virgin.json`.
- Fitted parameters: `league/AR-LigaProfesional/engine/corners/fitted_params_virgin.json`.
- Virgin predictions:
  `league/AR-LigaProfesional/predictions/c_ar_virgin_predictions.csv` —
  the shipped arm's predictions (Gate Zero's if nothing ships,
  labelled in the verdict): match_id, date, teams, actual total
  corners, exp_corners_total, FT ladder P(over 8.5/9.5/10.5), and
  1H/2H ladders derived presentation-only via the frozen corners
  constant 0.480 from the same expected total and NB machinery.
- Verdict: `league/AR-LigaProfesional/reports/C_AR_VERDICT.md`.

Production code and data are untouched. No push. No merge.
