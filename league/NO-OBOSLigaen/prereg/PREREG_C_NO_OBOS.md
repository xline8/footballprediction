# Pre-registration — C-NO-OBOS (NO-OBOSLigaen corners model)

Frozen: 2026-11-10, before any fitting. Branch `build/no-obos`.
Design authority: `MODEL_DESIGN.md` §3; features per `FEATURES.md`
(X5, X9-possession base); evidence per `EDA.md` (F2). Reference:
production `model_corners_v3.py` via the NO-Eliteserien engine
`league/NO-Eliteserien/engine/corners/` (core.py copied; pattern
unchanged except the covariate reduction and the primary line below).

## Target and lines
- Target: total corners = `corners_home + corners_away`.
  **Primary line 10.5** (dev over-rate 48.59% — the ladder line
  closest to 50%; dev mean 10.71). Ladder 9.5 / 10.5 / 11.5.
  All gate legs use binary LL at 10.5. The reference's internal
  fit-loss line is set to 10.5, as in the AU/NO retargets.
- Rows without the stats keys (1 in dev, 3 in the virgin season) are
  skipped by scoring, never imputed (PREPROCESSING rule 5).

## Reference architecture (all arms share)
Exactly as PREREG_C_NO: season-blocked walk-forward — for target
season S, features and ratings are built from all matches in seasons
strictly before S (expanding), with the production territorial
multiplier fitted on the training window; per-match predictions for
S use trailing team features computed strictly pre-match within the
harness's feature builder (as the J1 engine does). NB total with the
reference size fitted per the J1 engine's frozen method.
**One recorded reduction**: the multiplier's covariates are
possession for/against ONLY (X9-possession) — `big_chance` does not
exist in this league's feed (FEATURES §1, RU-1Division precedent).
This reduction applies to Gate Zero itself; it is the production
pattern reduced to the covariates this league has, not a variant.

## Arms
1. **Gate Zero (GZ)** — possession-only territorial multiplier (X9),
   unchanged otherwise.
2. **Arm PLAIN (no-multiplier ablation)** — GZ with the territorial
   multiplier removed entirely (multiplier ≡ 1.0 for every match);
   ratings, NB and harness identical. The arm tests whether the
   possession multiplier earns its place in a league where it is the
   only covariate.

## Baselines
League base rate (prior-seasons over-10.5 rate) and naive trailing-10
through the same NB — as the J1 corners harness computes them.

## Dev protocol
Evaluation seasons 2022, 2023, 2024, 2025 (n=959 with target); 2021
is training only. Dev harness must not read 2026 rows.

## Virgin protocol
Season 2026 (complete regular season, n=240; 237 with target), read
ONCE, only for dev-passing arms, after dev freezes. Training = all
matches before 2026. Calibration = mean P(over 10.5) − actual
over-rate, SE reported.

## GATE LEGS (verbatim, frozen — identical across the program)

Dev gate — pooled dev LL at the primary line beats BOTH baselines (league base rate; naive trailing-10 / climatology), else arm dead, no virgin read. Virgin legs — (i) LL ≤ Gate Zero's and ≤ best baseline's; (ii) calibration |mean P(over) − actual| ≤ 1.0pp, SE reported, breach within 1 SE = PROVISIONAL PASS; (iii) dev per-season sign check for both-pass (variant dev LL ≤ Gate Zero's in at least half the dev seasons; Gate Zero exempt). Both-pass: both → lower pooled virgin LL ships; one → ships; none → FAIL. Ties → simpler arm (Gate Zero first). If Gate Zero fails its own dev gate, the variants are moot — verdict FAIL regardless of variant dev numbers, and the virgin window is not read.

For this candidate the "primary line" in the gate text is 10.5 and
LL means the binary log-loss at 10.5.

## Forbidden
Half-share corner modelling — **this market is FT-only** (no halves
source exists, F3; no halves ladders are produced); absence features;
snapshot features; any covariate outside FEATURES.md §1 (in
particular big_chance and touches_opp_box, which do not exist here).

## Outputs
- Engine: `league/NO-OBOSLigaen/engine/corners/`; `results_dev.json`
  (+ CSV), `results_virgin.json`, `fitted_params_virgin.json`.
- Virgin predictions: `league/NO-OBOSLigaen/predictions/c_no_obos_virgin_predictions.csv`
  (shipped arm; GZ labelled if nothing ships): match_id, date, teams,
  actual total corners, exp_corners_total, FT ladder P(over
  9.5/10.5/11.5). FT only — no halves ladders.
- Verdict: `league/NO-OBOSLigaen/reports/C_NO_OBOS_VERDICT.md`.
