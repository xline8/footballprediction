# Pre-registration — C-NLE (Eerste Divisie corners model)

Frozen: 2026-11-09, before any fitting. Branch `build/nl-eerste`.
Design authority: `league/NL-EersteDivisie/analysis/MODEL_DESIGN.md`;
features per `FEATURES.md` (X5 corners naive, X7 opp-box touches,
X9 production territorial covariates); evidence per `EDA.md`
(F2/F9-equivalents). Reference implementation: production
`model_corners_v3.py`, as ported in
`league/NL-Eredivisie/engine/corners/` (decay-weighted base rates +
rolling-5 shots relative factors + Negative Binomial total +
territorial multiplier `exp(beta·z)` clamped to [0.70, 1.43], betas
and gamma fitted on a fit window only, never on the test window).

## Data, target, lines

- Source: `league/NL-EersteDivisie/data/nl_eerste_matches.csv`.
  Target: `y = corners_home + corners_away` (stats feed), present
  for all matches. Dev mean (2021/2022–2024/2025) 10.071.
- Primary line **9.5** (dev over-rate 55.00% at 9.5 vs 41.97% at
  10.5 — 9.5 is the ladder line closest to 50%); ladder 8.5 / 9.5 /
  10.5 reported. All gate legs use binary log-loss at 9.5.
- Coverage of the covariates: X9 (possession + big chance) complete
  in every season. X7 (touches_opp_box) coverage by season:
  72.1%, 77.6%, 85.3%, 100%, 100%, 100%; the FEATURES min-8 trailing
  rule makes the X7 multiplier inactive where a team's window
  cannot be filled — the harness reports the active share per
  season.
- Dev folds: warm-up season 2021/2022 (state building; NOT scored),
  scored seasons **2022/2023, 2023/2024, 2024/2025** (pooled
  n = 1140), chronological (date, then match_id); every state
  quantity uses only matches with date strictly before the target
  match's date. This matches the reference port's contract.

## Shared engine (both arms identical unless an arm says otherwise)

Exactly the `league/NL-Eredivisie/engine/corners/core.py`
machinery, constants frozen at the production/port values: base
rates with HL = 270 days; production moment ratio
`r_base = Σ w·y² / Σ w·y`; rolling-5 shots relative factors clamped
[0.6, 1.7]; core mean
`mu_cs = bh·(fhp·fac)^gamma + ba·(fap·fhc)^gamma`; NB on k = 0..50
normalised, size `k_nb = mu / (r − 1)` for r > 1.02 else the
Poisson limit; territorial multiplier `exp(beta·z)` clamped to
[0.70, 1.43] with z the trailing (min-8 of last-10) for-minus-
against covariate difference, standardised by the fit window's
league SD; gamma and betas selected on the **fit window only**
(the season preceding each scored season, rolling, exactly as the
reference harness does) from the frozen grids in core.py
(GAMMAS, BP, BBC, BBT).

## Arms

1. **Gate Zero (GZ)** — the reference above with the production
   territorial covariates (X9): z from possession and big-chance
   trailing differences.
2. **Arm X7** — identical, except the territorial covariates are
   opp-box touches for/against (X7) instead of X9 (beta grid BBT).

## Baselines (harness, not models)

- **League base rate**: for target season S, P(over 9.5) = the
  over-9.5 rate of all matches in seasons strictly before S,
  **scored as a constant probability**. This constant-rate
  definition is the frozen one; the core's internal NB base-rate
  machinery is part of the model arms, NOT of this baseline (the
  C-NL verdict is the cautionary precedent: prereg text and harness
  must agree, and here they do by construction — the verdict will
  recompute this baseline from the CSV independently).
- **Naive trailing-10**: trailing-10 team corner for/against means
  combined to a match total, scored through an NB whose size is the
  production moment ratio on the trailing window (the core's
  `r_base` machinery) — i.e. the count naive, not a model arm.

## Dev protocol

- Scored dev: seasons 2022/2023–2024/2025 (n = 1140). The dev
  harness must not read "2025/2026" or "2026/2027" rows at all.
- Metric: mean binary log-loss at line 9.5, per season and pooled,
  per arm and per baseline.

## Virgin protocol

- Virgin window: season "2025/2026" (n = 380), read **ONCE**, only
  for arms that pass the dev gate, after dev results are frozen.
  The chronological state continues from the dev run's end.
- Virgin metrics per arm: LL@9.5; calibration = **actual over-9.5
  rate − mean P(over 9.5)**, SE = sd(y_i − p_i)/√n reported.

## GATE LEGS (verbatim, frozen)

Dev gate — pooled dev LL@9.5 beats BOTH baselines (league base rate as defined above; naive trailing-10), else arm dead, no virgin read. Virgin legs — (i) LL@9.5 ≤ Gate Zero's and ≤ best baseline's; (ii) calibration |actual − predicted| ≤ 1.0pp, SE reported, breach within 1 SE = PROVISIONAL PASS; (iii) dev per-season sign check for both-pass. Both-pass: both → lower pooled virgin LL ships; one → ships; none → FAIL.

Reading of the legs, fixed here so the verdict is mechanical:

- The "best baseline" in virgin leg (i) is the lower-LL of the two
  baselines scored on the virgin window.
- Leg (iii): for a variant arm, its dev LL@9.5 ≤ Gate Zero's dev
  LL@9.5 in at least half of the dev seasons (≥ 2 of 3). Gate Zero
  is exempt.
- An arm *passes* iff it survives the dev gate AND passes virgin
  legs (i)–(ii) (PROVISIONAL PASS counts, recorded as such) AND,
  for variant arms, leg (iii).
- Both-pass rule: the lowest pooled virgin LL@9.5 ships; ties go
  to the simpler arm (Gate Zero before X7). If no arm passes,
  C-NLE verdict is FAIL and nothing ships.
- Design NOT-built clause: if Gate Zero fails its own dev gate, the
  variant is moot — verdict FAIL regardless of variant dev numbers,
  and the virgin window is not read.

## Outputs

- Engine: `league/NL-EersteDivisie/engine/corners/`.
- Dev results: `engine/corners/results_dev.json` (+ CSV).
- Virgin results: `engine/corners/results_virgin.json`.
- Fitted parameters: `engine/corners/fitted_params_virgin.json`.
- Virgin predictions (shipped arm only, on PASS):
  `league/NL-EersteDivisie/predictions/c_nle_virgin_predictions.csv`
  — one row per 2025/2026 match with actual total corners, expected
  total, FT ladder P(over 8.5/9.5/10.5), and 1H/2H ladders derived
  presentation-only via the frozen corners constant 0.462 (1H lines
  3.5/4.5/5.5, 2H lines 4.5/5.5/6.5). Halves are never fitted.
- Verdict: `league/NL-EersteDivisie/reports/C_NLE_VERDICT.md`.

Production code and data are untouched. No push. No merge.
