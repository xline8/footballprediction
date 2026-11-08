# Pre-registration — T-SCOCH (Scotland Championship total-shots model)

Frozen: 2026-11-10, before any fitting. Branch `build/sco-championship`.
Design authority: `analysis/MODEL_DESIGN.md` (T-SCOCH); evidence EDA
(total-shots trait reliability 0.367 / 0.509). Reference: the shots
family as frozen for T-J1 (v1 pattern / v2 level layer / E9
trailing-r) — see `league/J1/prereg/PREREG_T_J1.md` for the three
arms' exact constructions and mirror them, changing only league,
seasons and line; sibling run: `league/RU-1Division/prereg/PREREG_T_RU1.md`.
(T-J1 ran ahead of the top-5 prospective verdict by user order;
T-SCOCH is a separate corpus and neither trial contaminates the
other.)
Phase rule (frozen): all rows are phase `regular`; no phase feature.
Calibration = **predicted − actual** everywhere in this build.

- Target: total shots = `total_shots_home + total_shots_away`
  (stats feed, taken as-is; this league's feed counts run at
  ≈15/match — a feed-definition property recorded in EDA, not a
  reason to rescale). Primary line **15.5** (dev-period over-rate
  0.4754, closest to 0.5; the 14.5 over-rate is 0.5574, the 16.5
  over-rate is 0.3958). Ladder 14.5/15.5/16.5 reported, gate at 15.5.
- Arms: **A** v1 pattern (ratings + NB + naive ensemble);
  **B** v2 pattern (+ level layer); **C** E9 (NB r from a trailing
  window, league-level analogue).
- Training seed 2021/2022; dev 2022/2023–2024/2025 (stats rows
  n = 427; stats-less rows are never scored and never update
  state); dev harness must not read 2025/2026 / 2026/2027 rows.
- Baselines: league base rate; naive trailing-10.
- Virgin: 2025/2026 (stats rows n = 177), read ONCE, only for
  dev-passing arms. Calibration at 15.5 = mean predicted − actual,
  SE = sd(p_i − y_i)/√n.
- Halves: NONE — no period splits exist for total shots in this
  league; FT presentation only.

## GATE LEGS (verbatim, frozen)

Dev gate — pooled dev LL@15.5 beats BOTH baselines (league base rate; naive trailing-10), else arm dead, no virgin read. Virgin legs — (i) LL@15.5 ≤ the reference arm's (arm A if it passes dev; otherwise the dev-passing arm with the lowest pooled dev LL) and ≤ best baseline's; (ii) calibration |mean P(over 15.5) − actual| ≤ 1.0pp, SE reported, breach within 1 SE = PROVISIONAL PASS; (iii) dev per-season sign check for both-pass. Both-pass: among passing arms, lower pooled virgin LL ships; one → ships; none → FAIL.

Mechanical reading as in PREREG_S_SCOCH (variant sign check ≥2 of 3
vs the reference arm; ties → simpler arm A before B before C).

## Outputs

Engine `engine/total_shots/`; `results_dev.json` (+ CSV);
`results_virgin.json`; `fitted_params_virgin.json`; on PASS,
`predictions/t_scoch_virgin_predictions.csv` (FT ladder
14.5/15.5/16.5; NO halves columns — FT only). Verdict
`reports/T_SCOCH_VERDICT.md`.
