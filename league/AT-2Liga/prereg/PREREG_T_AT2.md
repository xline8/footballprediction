# Pre-registration — T-AT2 (Austria 2. Liga total-shots model)

Frozen: 2026-11-10, before any fitting. Branch `build/at-2liga`.
Design authority: `analysis/MODEL_DESIGN.md` (T-AT2); evidence EDA
(total-shots trait reliability 0.816 / 0.814). Reference: the shots
family as frozen for T-J1 (v1 pattern / v2 level layer / E9
trailing-r) — see `league/J1/prereg/PREREG_T_J1.md` for the three
arms' exact constructions and mirror them, changing only league,
seasons and line; sibling run: `league/RU-1Division/prereg/PREREG_T_RU1.md`.
Phase rule (frozen, MODEL_DESIGN): all rows are phase `regular`;
no phase feature anywhere.
Calibration = **actual − predicted** everywhere in this build.
Carried caveat (EDA F12, frozen here): the target series itself is
the one whose feed definition breaks in 2024/2025 (dev season 3 of
3) and reverts in the virgin season. The line below is the frozen
dev-distribution line; no era adjustment is registered; the gates
decide this candidate as registered.

- Target: total shots = `total_shots_home + total_shots_away`
  (stats feed, taken as-is). Primary line **18.5** (dev-period
  over-rate 0.473, closest to 0.5; the 17.5 over-rate is 0.556,
  the 19.5 over-rate is 0.415). Ladder 17.5/18.5/19.5 reported,
  gate at 18.5.
- Arms: **A** v1 pattern (ratings + NB + naive ensemble);
  **B** v2 pattern (+ level layer); **C** E9 (NB r from a trailing
  window, league-level analogue).
- Training seed 2021/2022; dev 2022/2023–2024/2025 (stats rows
  n = 708); dev harness must not read 2025/2026 / 2026/2027 rows.
- Baselines: league base rate; naive trailing-10.
- Virgin: 2025/2026 (stats rows n = 210), read ONCE, only for
  dev-passing arms. Calibration at 18.5 = actual − mean predicted,
  SE = sd(y_i − p_i)/√n.
- Halves: NONE — no period splits exist in this league and shots
  leave no event trace; FT presentation only.

## GATE LEGS (verbatim, frozen)

Dev gate — pooled dev LL@18.5 beats BOTH baselines (league base rate; naive trailing-10), else arm dead, no virgin read. Virgin legs — (i) LL@18.5 ≤ the reference arm's (arm A if it passes dev; otherwise the dev-passing arm with the lowest pooled dev LL) and ≤ best baseline's; (ii) calibration |actual − mean P(over 18.5)| ≤ 1.0pp, SE reported, breach within 1 SE = PROVISIONAL PASS; (iii) dev per-season sign check for both-pass. Both-pass: among passing arms, lower pooled virgin LL ships; one → ships; none → FAIL.

Mechanical reading as in PREREG_S_AT2 (variant sign check ≥2 of 3
vs the reference arm; ties → simpler arm A before B before C).

## Outputs

Engine `engine/total_shots/`; `results_dev.json` (+ CSV);
`results_virgin.json`; `fitted_params_virgin.json`; on PASS,
`predictions/t_at2_virgin_predictions.csv` (FT only — NO halves
presentation, no total-shots halves constant exists in this
league). Verdict `reports/T_AT2_VERDICT.md`.
