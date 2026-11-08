# Pre-registration — T-IE (Ireland Premier Division total-shots model)

Frozen: 2026-11-10, before any fitting. Branch `build/ie-premier`.
Design authority: `analysis/MODEL_DESIGN.md` (T-IE); evidence F2
(shots-for r = 0.961, against r = 0.938). Reference: the shots
family as frozen for T-J1 / T-SCO (v1 pattern / v2 level layer /
E9 trailing-r) — see `league/SCO-Premiership/prereg/PREREG_T_SCO.md`
and mirror its arms' exact constructions, changing only league,
seasons and line. (The top-5 prospective trial is a separate corpus;
neither trial contaminates the other.)

- Target: total shots = `total_shots_home + total_shots_away`
  (stats feed; 35 matches in 2021, complete from 2022). Primary
  line **24.5** (dev over-rate 0.487). Ladder 23.5/24.5/25.5
  reported, gate at 24.5.
- Arms: **A** v1 pattern (ratings + NB + naive ensemble);
  **B** v2 pattern (+ level layer); **C** E9 (NB r from a trailing
  window, league-level analogue).
- Training seed / warm-up 2022 (never scored); dev 2023–2025
  (n = 540); dev harness must not read 2026 rows.
- Baselines: league base rate; naive trailing-10.
- Virgin: 2026 (n = 180, complete), read ONCE, only for dev-passing
  arms. Calibration at 24.5, SE = sd(p_i − y_i)/√n.

## GATE LEGS (verbatim, frozen)

Dev gate — pooled dev LL@24.5 beats BOTH baselines (league base rate; naive trailing-10), else arm dead, no virgin read. Virgin legs — (i) LL@24.5 ≤ the reference arm's (arm A if it passes dev; otherwise the dev-passing arm with the lowest pooled dev LL) and ≤ best baseline's; (ii) calibration |mean P(over 24.5) − actual| ≤ 1.0pp, SE reported, breach within 1 SE = PROVISIONAL PASS; (iii) dev per-season sign check for both-pass. Both-pass: among passing arms, lower pooled virgin LL ships; one → ships; none → FAIL.

Mechanical reading as in PREREG_S_IE (variant sign check ≥2 of 3 vs
the reference arm; ties → simpler arm A before B before C).

## Outputs

Engine `engine/total_shots/`; `results_dev.json` (+ per-match CSV);
`results_virgin.json`; `fitted_params_virgin.json`; on PASS,
`predictions/t_ie_virgin_predictions.csv` (FT ladder 23.5/24.5/25.5;
1H/2H presentation-only via frozen shots constant 0.4600, lines
1H 10.5/11.5/12.5, 2H 12.5/13.5/14.5). Verdict
`reports/T_IE_VERDICT.md`.
