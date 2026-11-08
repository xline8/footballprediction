# Pre-registration — T-GR (GR-SuperLeague total-shots model)

Frozen: 2026-11-09, before any fitting. Branch `build/gr-super`.
Design authority: `analysis/MODEL_DESIGN.md` (T-GR); evidence EDA
(total-shots trait reliability 0.907 / 0.880 — the strongest count
trait in this league). Reference: the shots family as frozen for
T-J1 (v1 pattern / v2 level layer / E9 trailing-r) — see
`league/J1/prereg/PREREG_T_J1.md` for the three arms' exact
constructions and mirror them, changing only league, seasons and
line. (T-J1 ran ahead of the top-5 prospective verdict by user
order; T-GR is a separate corpus and neither trial contaminates
the other.)
Phase rule (frozen, MODEL_DESIGN): all phases are ordinary rows;
no phase feature anywhere.
Calibration = **actual − predicted** everywhere in this build.

- Target: total shots = `total_shots_home + total_shots_away`
  (stats feed). Primary line **22.5** (scored-dev over-rate 0.534,
  closest to 0.5; the 23.5 over-rate is 0.447). Ladder
  21.5/22.5/23.5 reported, gate at 22.5.
- **Seed-season exclusion (frozen, design-stage):** the 2021/2022
  total_shots feed is a different measurement (mean 16.89 and
  on-target rate 0.510 vs 21.96–24.16 / 0.315–0.362 in every later
  season; DATA_UNDERSTANDING §2). For T-GR only, 2021/2022 rows
  never enter any trailing window, rating fit, level layer, r
  estimate, or baseline. The T-GR walk-forward seeds on 2022/2023
  itself (predict-then-update within the scored seasons, exactly
  as the reference handles a feed window — the J2 X5 rule). All
  arms and both baselines run under this same exclusion.
- Arms: **A** v1 pattern (ratings + NB + naive ensemble);
  **B** v2 pattern (+ level layer); **C** E9 (NB r from a trailing
  window, league-level analogue).
- Dev: scored seasons 2022/2023–2024/2025 (n = 716); dev harness
  must not read 2025/2026 / 2026/2027 rows.
- Baselines: league base rate; naive trailing-10 (under the same
  seed-season exclusion).
- Virgin: 2025/2026 (n = 236), read ONCE, only for dev-passing arms.
  Calibration at 22.5 = actual − mean predicted, SE = sd(y_i − p_i)/√n.

## GATE LEGS (verbatim, frozen)

Dev gate — pooled dev LL@22.5 beats BOTH baselines (league base rate; naive trailing-10), else arm dead, no virgin read. Virgin legs — (i) LL@22.5 ≤ the reference arm's (arm A if it passes dev; otherwise the dev-passing arm with the lowest pooled dev LL) and ≤ best baseline's; (ii) calibration |actual − mean P(over 22.5)| ≤ 1.0pp, SE reported, breach within 1 SE = PROVISIONAL PASS; (iii) dev per-season sign check for both-pass. Both-pass: among passing arms, lower pooled virgin LL ships; one → ships; none → FAIL.

Mechanical reading as in PREREG_S_GR (variant sign check ≥2 of 3
vs the reference arm; ties → simpler arm A before B before C).

## Outputs

Engine `engine/total_shots/`; `results_dev.json` (+ CSV);
`results_virgin.json`; `fitted_params_virgin.json`; on PASS,
`predictions/t_gr_virgin_predictions.csv` (FT ladder 21.5/22.5/23.5;
1H/2H presentation-only via frozen shots constant 0.4611, lines
1H 10.5/11.5/12.5, 2H 11.5/12.5/13.5). Verdict
`reports/T_GR_VERDICT.md`.
