# Pre-registration — T-EG (EG-PremierLeague total-shots model)

Frozen: 2026-11-09, before any fitting. Branch `build/eg-premier`.
Design authority: `analysis/MODEL_DESIGN.md` (T-EG); evidence
EDA F1/F2/F5. Reference: the shots family as frozen for T-J1
(v1 pattern / v2 level layer / E9 trailing-r) — see
`league/J1/prereg/PREREG_T_J1.md` and the SA engine
`league/SA-ProLeague/engine/total_shots/` for the three arms' exact
constructions; mirror them, changing only league, seasons and line.
(T-J1 ran ahead of the top-5 prospective verdict by user order;
T-EG is a separate corpus and neither trial contaminates the other.)
Phase rule (frozen, MODEL_DESIGN): all phases are ordinary rows in
every window; no phase feature anywhere.

- Target: total shots = `total_shots_home + total_shots_away`
  (stats feed). Primary line **22.5** (scored-dev pooled
  2022/2023–2024/2025 over-rate 0.473, closest to 0.5). Ladder
  21.5 / 22.5 / 23.5 reported, gate at 22.5.
- Arms: **A** v1 pattern (ratings + NB + naive ensemble);
  **B** v2 pattern (+ level layer); **C** E9 (NB r from a trailing
  window, league-level analogue).
- Walk-forward: per-match, chronological (date, match_id),
  predict-then-update, date-grouped. Warm-up: 2021/2022 updates
  state, never scored.
- Dev: scored seasons 2022/2023–2024/2025 (rows with the target
  present; n = 826 of 837). The dev harness must not read
  2025/2026 or 2026/2027 rows at all.
- Baselines: league base rate (prior-seasons over-22.5 rate,
  constant within target season); naive trailing-10 through the
  same count distribution as the reference harness.
- Virgin: 2025/2026 (n = 322), read ONCE, only for dev-passing
  arms, continuing from the dev end state. Calibration = actual
  over-22.5 rate − mean P(over 22.5), SE = sd(y_i − p_i)/√n.

## GATE LEGS (verbatim, frozen)

Dev gate — pooled dev LL@22.5 beats BOTH baselines (league base rate; naive trailing-10), else arm dead, no virgin read. Virgin legs — (i) LL@22.5 ≤ the reference arm's (arm A if it passes dev; otherwise the dev-passing arm with the lowest pooled dev LL) and ≤ best baseline's; (ii) calibration |actual − mean P(over 22.5)| ≤ 1.0pp is clean PASS; beyond 1 SE is FAIL, with SE reported, a breach within 1 SE of the 1.0pp boundary is PROVISIONAL PASS; (iii) dev per-season sign check for both-pass. Both-pass: among passing arms, lower pooled virgin LL ships; one → ships; none → FAIL.

Mechanical reading: an arm passes iff it survives the dev gate AND
passes virgin legs (i)–(ii) (PROVISIONAL counts) AND, for variants
(B, C), leg (iii) — variant dev LL@22.5 ≤ the reference arm's in at
least 2 of the 3 dev seasons. Ties → simpler arm (A before B
before C). If NO arm passes the dev gate, verdict FAIL, virgin
NOT read. (For this candidate the reference arm is A; if A fails
dev but B or C passes, the surviving arm still faces legs (i)–(ii)
against the baselines and the lowest-dev-LL dev-passer as the
leg-(i) comparator, per the frozen leg text.)

## Outputs

Engine `engine/total_shots/`; `results_dev.json` (+ CSV);
`results_virgin.json`; `fitted_params_virgin.json`; on PASS,
`predictions/t_eg_virgin_predictions.csv` (shipped arm; FT ladder
21.5/22.5/23.5; 1H/2H presentation-only via frozen shots constant
0.4459, lines 1H 9.5/10.5/11.5, 2H 11.5/12.5/13.5). Verdict
`reports/T_EG_VERDICT.md`.
