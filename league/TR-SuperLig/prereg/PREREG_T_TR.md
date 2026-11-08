# Pre-registration — T-TR (TR-SuperLig total-shots model)

Frozen: 2026-11-09, before any fitting. Branch `build/tr-superlig`.
Design authority: `analysis/MODEL_DESIGN.md` (T-TR); evidence F2.
Reference: the shots family as frozen for T-J1 (v1 pattern /
v2 level layer / E9 trailing-r) — see `league/J1/prereg/PREREG_T_J1.md`
for the three arms' exact constructions and mirror them, changing
only league, seasons and line. (T-J1 ran ahead of the top-5
prospective verdict by user order; T-TR is a separate corpus and
neither trial contaminates the other.)
Phase rule (frozen, MODEL_DESIGN): all phases are ordinary rows in
every window; no phase feature anywhere.

- Target: total shots = `total_shots_home + total_shots_away`
  (stats feed). Primary line **25.5** (dev over-rate 0.476;
  the 26.5 over-rate is 0.415).
  Ladder 24.5/25.5/26.5 reported, gate at 25.5.
- Arms: **A** v1 pattern (ratings + NB + naive ensemble);
  **B** v2 pattern (+ level layer); **C** E9 (NB r from a trailing
  window, league-level analogue).
- Training seed 2021/2022; dev 2021/2022–2024/2025 (n = 1033);
  dev harness must not read 2025/2026 / 2026/2027 rows.
- Baselines: league base rate; naive trailing-10.
- Virgin: 2025/2026 (n = 306), read ONCE, only for dev-passing arms.
  Calibration at 25.5, SE = sd(p_i − y_i)/√n.

## GATE LEGS (verbatim, frozen)

Dev gate — pooled dev LL@25.5 beats BOTH baselines (league base rate; naive trailing-10), else arm dead, no virgin read. Virgin legs — (i) LL@25.5 ≤ the reference arm's (arm A if it passes dev; otherwise the dev-passing arm with the lowest pooled dev LL) and ≤ best baseline's; (ii) calibration |mean P(over 25.5) − actual| ≤ 1.0pp is clean PASS; beyond 1 SE is FAIL, with SE reported, a breach within 1 SE of the 1.0pp boundary is PROVISIONAL PASS; (iii) dev per-season sign check for both-pass. Both-pass: among passing arms, lower pooled virgin LL ships; one → ships; none → FAIL.

Mechanical reading as in PREREG_S_TR (variant sign check ≥2 of 3
vs the reference arm; ties → simpler arm A before B before C).

## Outputs

Engine `engine/total_shots/`; `results_dev.json` (+ CSV);
`results_virgin.json`; `fitted_params_virgin.json`; on PASS,
`predictions/t_tr_virgin_predictions.csv` (FT ladder 24.5/25.5/26.5;
1H/2H presentation-only via frozen shots constant 0.4544, lines
1H 11.5/12.5/13.5, 2H 13.5/14.5/15.5). Verdict
`reports/T_TR_VERDICT.md`.
