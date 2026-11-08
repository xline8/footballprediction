# Pre-registration — T-US (US-MLS total-shots model)

Frozen: 2026-11-09, before any fitting. Branch `build/us-mls`.
Provenance: built ahead of the top-5 total-shots prospective verdict by the
same user order recorded for T-J1; different corpus, different virgin window,
no shared fitting — the top-5 trial is untouched and neither result
contaminates the other. Design authority: `league/US-MLS/analysis/MODEL_DESIGN.md`
§5; features per `league/US-MLS/analysis/FEATURES.md` (X5); evidence per
`league/US-MLS/analysis/EDA.md` (F2; dispersion 1.325). Reference: the shots
family via the J1 engine `league/J1/engine/total_shots/`.

## Target and lines

- Target: total shots = `total_shots_home + total_shots_away`.
  **Primary line 25.5** (dev over-rate 0.492). Ladder 24.5 / 25.5 / 26.5.
  All gate legs use binary LL at 25.5.

## Arms (exactly the J1 engine's methods, retargeted)

1. **Arm A (v1 pattern)** — ratings + NB + naive ensemble, NB r fitted on the
   tuning window by the J1 engine's frozen method.
2. **Arm C (E9 trailing-r)** — Arm A with the NB r taken from a trailing
   window (league-level trailing r), the J1 engine's E9 method unchanged. The
   v2 level-layer arm B is not run here: the two arms bind the comparison to
   the dispersion question this league's EDA raises — shots dispersion 1.325.
The tuning-season / gate-pool split is: tuning season 2022; gate pool = scored
dev seasons 2023 + 2024 pooled (2022 reported, not gated — it is the tuning
season, exactly as T-J1/T-AT).

## Baselines

League base rate (prior-seasons over-25.5 rate) and naive trailing-10 through
the same NB machinery, as the J1 engine computes them.

## Dev protocol

Warm-up 2021; tuning 2022; scored dev 2022, 2023, 2024 (n=1532), with 2022
reported but not gated. Gate pool is 2023 + 2024. The dev harness must not read
2025 rows at all or any 2026 rows. **Dev gate (this candidate's reading of the
shared legs):** pooled gate-pool LL@25.5 beats BOTH baselines. The per-season
sign check (leg iii) is read on the two gate-pool seasons.

## Virgin protocol

Season 2025 (n=540), read ONCE, only for arms passing the dev gate,
walk-forward continuing from the dev end state. Calibration = mean P(over
25.5) − actual over-rate, SE reported.

## GATE LEGS (verbatim, frozen — identical across the program)

Dev gate — pooled dev LL at the primary line beats BOTH baselines (league base rate; naive trailing-10 / climatology), else arm dead, no virgin read. Virgin legs — (i) LL ≤ Gate Zero's and ≤ best baseline's; (ii) calibration |mean P(over) − actual| ≤ 1.0pp, SE reported, breach within 1 SE = PROVISIONAL PASS; (iii) dev per-season sign check for both-pass (variant dev LL ≤ Gate Zero's in at least half the dev seasons; Gate Zero exempt). Both-pass: both → lower pooled virgin LL ships; one → ships; none → FAIL. Ties → simpler arm (Gate Zero first). If Gate Zero fails its own dev gate, the variants are moot — verdict FAIL regardless of variant dev numbers, and the virgin window is not read.

For this candidate the "primary line" in the gate text is 25.5 and LL means binary log-loss at 25.5. The gate pool is 2023 + 2024; the per-season sign check is over those two seasons, so at least one of two is required for a variant.

## Forbidden

Halves modelling (presentation via frozen constant 0.456 only); absence
features; snapshot features; any distribution family outside the shots
family's NB pattern.

## Outputs

- Engine: `league/US-MLS/engine/total_shots/`; `results_dev.json` (+ CSV),
  `results_virgin.json`, `fitted_params_virgin.json`.
- Virgin predictions: `league/US-MLS/predictions/t_us_virgin_predictions.csv`
  (shipped arm; arm A labelled if nothing ships): match_id, date, teams, actual
  total shots, exp_shots_total, FT ladder P(over 24.5/25.5/26.5), 1H/2H
  ladders presentation-only via frozen constant 0.456 with the arm's NB r
  (1H lines 9.5/10.5/11.5; 2H lines 11.5/12.5/13.5).
- Verdict: `league/US-MLS/reports/T_US_VERDICT.md`.
