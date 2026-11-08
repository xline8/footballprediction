# Pre-registration — T-ITB (IT-SerieB total-shots model)

Frozen: 2026-11-09, before any fitting. Branch `build/it-serieb`.
Design authority: `analysis/MODEL_DESIGN.md` (T-ITB); evidence
F2. Reference: the shots family as frozen for T-J1 (v1 pattern /
v2 level layer / E9 trailing-r) — see
`league/J1/prereg/PREREG_T_J1.md` for the three arms' exact
constructions and mirror them, changing only league, seasons,
line and the tuning/gate-pool split below. (T-J1 ran ahead of
the top-5 prospective verdict by user order; T-ITB is a
separate corpus and neither trial contaminates the other.)
Team state keyed on team_id. **Calibration = actual −
predicted** throughout.

- Target: total shots = `total_shots_home + total_shots_away`
  (stats feed, 100% of matches every season). Primary line
  **25.5** (dev-eval over-rate 0.475, closest to 0.5; measured:
  24.5 → 0.540, 25.5 → 0.475). Ladder 24.5/25.5/26.5 reported,
  gate at 25.5.
- Arms: **A** v1 pattern (ratings + NB + naive ensemble);
  **B** v2 pattern (+ level layer, M̄ = 25.6 frozen ≈ the
  ITB dev mean 25.59); **C** E9 (NB r from a trailing
  200-match window, league-level analogue, prior mean 25.6
  and this build's r_A in the E9 formula positions where J1
  used 24.9/r_A).
- Tuning (frozen procedure, J1 discipline): ridge lambda,
  r_A and arm B's level-layer cell are chosen on the **tuning
  season 2022/2023 only**; that season is reported for
  transparency but is NOT part of the dev gate pool.
- Dev gate pool: **2023/2024–2024/2025 (n = 779)**,
  walk-forward with 2021/2022 as warm-up and state carrying
  continuously. Dev harness must not read 2025/2026 /
  2026/2027 rows.
- Baselines: league base rate; naive trailing-10 (house
  definitions as in T-J1: base rate Poisson on decayed league
  means; naive Poisson).
- Virgin: 2025/2026 (n = 390), read ONCE, only for arms
  passing the dev gate. Calibration at 25.5 = actual over
  rate − mean P(over 25.5), SE = sd(y_i − p_i)/√n.

## GATE LEGS (verbatim, frozen)

Dev gate — pooled dev LL@25.5 beats BOTH baselines (league base rate; naive trailing-10), else arm dead, no virgin read. Virgin legs — (i) LL@25.5 ≤ the reference arm's (arm A if it passes dev; otherwise the dev-passing arm with the lowest pooled dev LL) and ≤ best baseline's; (ii) calibration |actual − mean P(over 25.5)| ≤ 1.0pp, SE reported, breach within 1 SE = PROVISIONAL PASS; (iii) dev per-season sign check for both-pass. Both-pass: among passing arms, lower pooled virgin LL ships; one → ships; none → FAIL.

Mechanical reading as in PREREG_S_ITB (variant sign check ≥1
of 2 gate-pool seasons vs the reference arm; ties → simpler
arm A before B before C). Reference-arm dev failure does NOT
moot the other arms for this candidate (the verbatim T-family
leg (i) defines the fallback reference explicitly).

## Outputs

Engine `engine/total_shots/`; `results_dev.json` (+ CSV),
including the frozen tuning outcomes; `fitted_params.json` /
`fitted_params_virgin.json`; on PASS,
`predictions/t_itb_virgin_predictions.csv` (FT ladder
24.5/25.5/26.5; 1H/2H presentation-only via frozen shots
constant 0.4650, lines 1H 11.5/12.5/13.5, 2H 13.5/14.5/15.5).
Verdict `reports/T_ITB_VERDICT.md`.
