# Pre-registration — S-USL (USL Championship shots-on-target model)

Frozen: 2026-11-09, before any fitting. Branch `build/us-usl`.
Design authority: `league/US-USLChampionship/analysis/MODEL_DESIGN.md` §2;
features per `league/US-USLChampionship/analysis/FEATURES.md` (X5 base;
X4/X6 dropped by design — F6); evidence per
`league/US-USLChampionship/analysis/EDA.md` (F2/F6). Reference: production
`model_sot.py` v5 via the J1 engine `league/J1/engine/sot/` (as ported in
`league/US-MLS/engine/sot/`). **Calibration = actual − predicted**
throughout.

## Target and lines

- Target: total SOT = `ShotsOnTarget_home + ShotsOnTarget_away` in
  `league/US-USLChampionship/data/usl_matches.csv` (stats feed, 100%
  coverage). **Primary line 8.5** (dev over-rate 0.483). Ladder 7.5 / 8.5 /
  9.5. All gate legs use binary LL at 8.5.

## Reference architecture — v5, frozen constants (all arms share)

Exactly as PREREG_S_J1/S_US: joint ridge Poisson (lambda_ridge=100,
HL=365d, 7-day lazy refit, eta clip [−6, 4]); venue-split decayed
total-shots ratings shrunk with prior K=8; Beta-Binomial on-target ratio
(P=200); per-team expectation = 0.5·regression + 0.5·implied-shots;
ensemble 0.5·NB(model) + 0.5·NB(naive trailing-10); NB size r = 79.94
frozen. The v5 total-shots component reads the stats feed (`total_shots`),
which is complete in this league; no shotmap input exists or is used.

## Walk-forward protocol

Per-match predict-then-update, chronological (date, match_id). Warm-up
2021 matches update state but are never scored. Scored dev seasons are
2022, 2023, 2024 (n=1,318). The dev harness must not read 2025 rows at
all; 2025 is read ONCE only for dev-passing arms. Season 2026 is reserved
and its rows must not be read at all. Regular and playoff matches remain
in every window, with phase flagged rather than filtered.

## Arms

1. **Gate Zero (GZ)** — v5 pattern unmodified.
2. **Arm RS (ratio-shrink)** — GZ with the BB prior raised P=200 → 20,000
   (the ridge_shrink arm of this build's tasking).

No X4/X6 arms exist in this league: both need shotmap/xG, which are
absent (F6). They are dropped by design in FEATURES.md, not rescued here.

## Baselines

League base rate (prior-seasons over-8.5 rate, constant within a season)
and naive trailing-10 through the same NB (r=79.94).

## Virgin protocol

Season 2025 (n=375), read ONCE, only for dev-passing arms, walk-forward
continuing from the dev end state. Calibration = actual over-rate − mean
P(over 8.5), SE reported.

## GATE LEGS (verbatim, frozen — identical across the program)

Dev gate — pooled dev LL at the primary line beats BOTH baselines (league base rate; naive trailing-10 / climatology), else arm dead, no virgin read. Virgin legs — (i) LL ≤ Gate Zero's and ≤ best baseline's; (ii) calibration |actual − predicted| ≤ 1.0pp, SE reported, breach within 1 SE = PROVISIONAL PASS; (iii) dev per-season sign check for both-pass (variant dev LL ≤ Gate Zero's in at least half the dev seasons; Gate Zero exempt). Both-pass: both → lower pooled virgin LL ships; one → ships; none → FAIL. Ties → simpler arm (Gate Zero first). If Gate Zero fails its own dev gate, the variants are moot — verdict FAIL regardless of variant dev numbers, and the virgin window is not read.

For this candidate the "primary line" in the gate text is 8.5 and LL
means binary log-loss at 8.5.

## Forbidden

Absence features; trailing conversion/finishing/on-target-rate form
features (standalone rate covariate is R4); halves modelling
(presentation via frozen constant 0.456 only); two-stage generative
distributions; snapshots; any shotmap/xG input (none exists).

## Outputs

- Engine: `league/US-USLChampionship/engine/sot/`; `results_dev.json`
  (+ CSV), `results_virgin.json`, `fitted_params_virgin.json`.
- Virgin predictions: `league/US-USLChampionship/predictions/s_usl_virgin_predictions.csv`
  (shipped arm; GZ labelled if nothing ships): match_id, date, teams,
  actual total SOT, exp_sot_home/away/total, FT ladder P(over 7.5/8.5/9.5),
  1H/2H ladders presentation-only via frozen constant 0.456 with NB
  r=79.94 (1H lines 2.5/3.5/4.5; 2H lines 3.5/4.5/5.5).
- Verdict: `league/US-USLChampionship/reports/S_USL_VERDICT.md`.
