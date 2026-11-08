# Pre-registration — T-SAFD (SA-FirstDivision total-shots model)

Frozen: 2026-11-10, before any fitting. Branch `build/sa-firstdiv`.
Design authority: `analysis/MODEL_DESIGN.md` (T-SAFD); evidence
F1/F2. Reference: the shots family as frozen for T-J1 (v1 pattern
/ v2 level layer / E9 trailing-r) — see
`league/J1/prereg/PREREG_T_J1.md` for the three arms' exact
constructions and mirror them, changing only league, seasons and
line. SA analogue `PREREG_T_SA.md`. Engine port:
`league/SCO-Premiership/engine/total_shots/` (and
`league/SA-ProLeague/engine/total_shots/`). Phase rule (frozen):
promotion playoffs and awarded matches are **excluded from every
fit and every scored window**; only regular played rows are used.
Calibration is defined as **actual − predicted** everywhere.
(T-SAFD is a separate corpus from the top-5 prospective trial;
neither contaminates the other.)

- Target: total shots = `total_shots_home + total_shots_away`
  (stats feed). Primary line **23.5** (dev over-rate 0.487).
  Ladder 22.5/23.5/24.5 reported, gate at 23.5.
- Arms: **A** v1 pattern (ratings + NB + naive ensemble);
  **B** v2 pattern (+ level layer); **C** E9 (NB r from a trailing
  window, league-level analogue). The port's internal
  tuning-block mechanics use the warm-up block (first 90 regular
  played matches of 2025/2026, never scored) exactly as the SCO
  port used its first scored season; the gate pool is the scored
  block below. (Adaptation frozen here because no prior season with
  the target exists: the 2024/2025 season is score-only.)
- Walk-forward: per-match, chronological (date, match_id),
  predict-then-update, date-grouped. Warm-up: first 90 regular
  played matches of 2025/2026 (never scored); scored: the remaining
  **214 matches**. The 2024/2025 season is not read by this harness
  at all.
- Dev: scored block n = 214. The dev harness must not read
  2026/2027 rows at all.
- Baselines: league base rate (over-23.5 rate of all regular played
  matches strictly before each scored date, expanding); naive
  trailing-10.
- Virgin: 2026/2027 partial (n = 94, rounds 1–11, TRANSITIONAL),
  read ONCE, only for dev-passing arms. Calibration at 23.5,
  SE = sd(p_i − y_i)/√n. Small-n note as in PREREG_S_SAFD: at n = 94
  the calibration SE is ≈5pp; the gate is applied mechanically
  regardless, and the verdict records the virgin as TRANSITIONAL
  with a confirmatory read at season end.

## GATE LEGS (verbatim, frozen)

Dev gate — pooled dev LL@23.5 beats BOTH baselines (league base rate; naive trailing-10), else arm dead, no virgin read. Virgin legs — (i) LL@23.5 ≤ the reference arm's (arm A if it passes dev; otherwise the dev-passing arm with the lowest pooled dev LL) and ≤ best baseline's; (ii) calibration |mean P(over 23.5) − actual| ≤ 1.0pp, SE reported, breach within 1 SE = PROVISIONAL PASS; (iii) dev sign check for both-pass. Both-pass: among passing arms, lower pooled virgin LL ships; one → ships; none → FAIL.

Mechanical reading as in PREREG_S_SAFD (variant sign check: pooled
dev LL@23.5 ≤ reference arm's pooled dev LL@23.5; ties → simpler
arm A before B before C).

## Outputs

Engine `engine/total_shots/`; `results_dev.json` (+ CSV);
`results_virgin.json`; `fitted_params_virgin.json`; on PASS,
`predictions/t_safd_virgin_predictions.csv` (FT ladder
22.5/23.5/24.5; 1H/2H presentation-only via frozen shots constant
0.4557, lines 1H 10.5/11.5/12.5, 2H 12.5/13.5/14.5). Verdict
`reports/T_SAFD_VERDICT.md`.
