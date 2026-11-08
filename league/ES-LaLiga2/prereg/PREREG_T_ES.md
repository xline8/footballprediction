# Pre-registration — T-ES (ES-LaLiga2 total-shots model)

Frozen: 2026-11-09, before any fitting. Branch `build/es-laliga2`.
Design authority: `analysis/MODEL_DESIGN.md` (T-ES); evidence F2.
Reference: the shots family as frozen for T-J1 (v1 pattern /
v2 level layer / E9 trailing-r) — see `league/J1/prereg/PREREG_T_J1.md`
for the three arms' exact constructions and mirror them, changing
only league, seasons and line. (T-J1 ran ahead of the top-5
prospective verdict by user order; T-ES is a separate corpus and
neither trial contaminates the other.) Team state keyed on team_id.

- Target: total shots = `total_shots_home + total_shots_away`
  (stats feed, 100% of matches every season). Primary line **23.5**
  (dev over-rate 0.481, closest to 0.5). Ladder 22.5/23.5/24.5
  reported, gate at 23.5.
- Arms: **A** v1 pattern (ratings + NB + naive ensemble);
  **B** v2 pattern (+ level layer); **C** E9 (NB r from a trailing
  window, league-level analogue).
- Training seed 2021/2022; dev 2022/2023–2024/2025 (n = 1,404);
  dev harness must not read 2025/2026 / 2026/2027 rows.
- Baselines: league base rate; naive trailing-10.
- Virgin: 2025/2026 (n = 468), read ONCE, only for dev-passing arms.
  Calibration at 23.5, SE = sd(p_i − y_i)/√n.

## GATE LEGS (verbatim, frozen)

Dev gate — pooled dev LL@23.5 beats BOTH baselines (league base rate; naive trailing-10), else arm dead, no virgin read. Virgin legs — (i) LL@23.5 ≤ the reference arm's (arm A if it passes dev; otherwise the dev-passing arm with the lowest pooled dev LL) and ≤ best baseline's; (ii) calibration |mean P(over 23.5) − actual| ≤ 1.0pp, SE reported, breach within 1 SE = PROVISIONAL PASS; (iii) dev per-season sign check for both-pass. Both-pass: among passing arms, lower pooled virgin LL ships; one → ships; none → FAIL.

Mechanical reading as in PREREG_S_ES (variant sign check ≥2 of 3
vs the reference arm; ties → simpler arm A before B before C).

## Outputs

Engine `engine/total_shots/`; `results_dev.json` (+ CSV);
`results_virgin.json`; `fitted_params_virgin.json`; on PASS,
`predictions/t_es_virgin_predictions.csv` (FT ladder 22.5/23.5/24.5;
1H/2H presentation-only via frozen shots constant 0.4522, lines
1H 9.5/10.5/11.5, 2H 11.5/12.5/13.5). Verdict
`reports/T_ES_VERDICT.md`.
