# Pre-registration — T-USL (USL Championship total-shots model)

Frozen: 2026-11-09, before any fitting. Branch `build/us-usl`.
Provenance: built ahead of the top-5 total-shots prospective verdict by
the same user order recorded for T-J1; different corpus, different virgin
window, no shared fitting — the top-5 trial is untouched and neither
result contaminates the other. Design authority:
`league/US-USLChampionship/analysis/MODEL_DESIGN.md` §5; features per
`league/US-USLChampionship/analysis/FEATURES.md` (X5); evidence per
`league/US-USLChampionship/analysis/EDA.md` (F2/F9/F10; dispersion
1.464). Reference: the shots family as frozen for T-J1 (v1 pattern / v2
level layer / E9 trailing-r) — see `league/J1/prereg/PREREG_T_J1.md` and
`league/IT-SerieB/prereg/PREREG_T_ITB.md` for the arms' exact
constructions; mirror them, changing only league, seasons, line and the
tuning/gate-pool split below. Team state keyed on team_id.
**Calibration = actual − predicted** throughout.

- Target: total shots = `total_shots_home + total_shots_away`
  (stats feed, 100% of matches every season). Primary line **24.5**
  (dev pooled over-rate 0.476, closest to 0.5; measured: 23.5 → 0.552,
  24.5 → 0.476, 25.5 → 0.407). Ladder 23.5/24.5/25.5 reported, gate at
  24.5.
- Arms: **A** v1 pattern (ratings + NB + naive ensemble);
  **B** v2 pattern (+ level layer, M̄ = 24.4 frozen ≈ the USL dev mean
  24.354); **C** E9 (NB r from a trailing 200-match window, league-level
  analogue, prior mean 24.4 and this build's r_A in the E9 formula
  positions where J1 used 24.9/r_A).
- Tuning (frozen procedure, J1 discipline): ridge lambda, r_A and arm
  B's level-layer cell are chosen on the **tuning season 2022 only**;
  that season is reported for transparency but is NOT part of the dev
  gate pool.
- Dev gate pool: **2023–2024 (n = 846)**, walk-forward with 2021 as
  warm-up and state carrying continuously. Dev harness must not read
  2025 / 2026 rows.
- Baselines: league base rate; naive trailing-10 (house definitions as
  in T-J1: base rate Poisson on decayed league means; naive Poisson).
- Virgin: 2025 (n = 375), read ONCE, only for arms passing the dev
  gate. Calibration at 24.5 = actual over-rate − mean P(over 24.5),
  SE = sd(y_i − p_i)/√n.

## GATE LEGS (verbatim, frozen)

Dev gate — pooled dev LL@24.5 beats BOTH baselines (league base rate; naive trailing-10), else arm dead, no virgin read. Virgin legs — (i) LL@24.5 ≤ the reference arm's (arm A if it passes dev; otherwise the dev-passing arm with the lowest pooled dev LL) and ≤ best baseline's; (ii) calibration |actual − mean P(over 24.5)| ≤ 1.0pp, SE reported, breach within 1 SE = PROVISIONAL PASS; (iii) dev per-season sign check for both-pass. Both-pass: among passing arms, lower pooled virgin LL ships; one → ships; none → FAIL.

Mechanical reading as in PREREG_T_ITB (variant sign check ≥1 of 2
gate-pool seasons vs the reference arm; ties → simpler arm A before B
before C). Reference-arm dev failure does NOT moot the other arms for
this candidate (the verbatim T-family leg (i) defines the fallback
reference explicitly).

## Forbidden

Halves modelling (presentation via frozen constant 0.453 only); absence
features; snapshot features; any distribution family outside the shots
family's NB pattern.

## Outputs

Engine `engine/total_shots/`; `results_dev.json` (+ CSV), including the
frozen tuning outcomes; `fitted_params.json` /
`fitted_params_virgin.json`; on PASS,
`predictions/t_usl_virgin_predictions.csv` (FT ladder 23.5/24.5/25.5;
1H/2H presentation-only via frozen shots constant 0.453, lines 1H
10.5/11.5/12.5, 2H 12.5/13.5/14.5). Verdict
`reports/T_USL_VERDICT.md`.
