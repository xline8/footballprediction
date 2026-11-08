# Pre-registration — T-SE2 (SE-Superettan total-shots model)

Frozen: 2026-11-10, before any fitting. Branch `build/se-superettan`.
Design authority: `analysis/MODEL_DESIGN.md` (T-SE2); evidence F2.
Reference: the shots family as frozen for T-J1 / T-SE (v1 pattern / v2 level
layer / E9 trailing-r) — constructions mirrored, changing only league,
seasons and line.

- Target: total shots = `total_shots_home + total_shots_away` (stats feed).
  Primary line **20.5** (dev over-rate 0.474, closest to 0.5).
  Ladder 19.5 / 20.5 / 21.5 reported, gate at 20.5.
- Arms: **A** v1 pattern (ratings + NB + naive ensemble); **B** v2 pattern
  (+ level layer); **C** E9 (NB r from a trailing window).
- Warm-up 2022; dev scored 2023–2025 (n = 710 stats rows). Dev harness must not read 2026 rows.
- Baselines: league base rate; naive trailing-10.
- Virgin: 2026 (n = 237), read ONCE, only for dev-passing arms.
  Calibration at 20.5, SE = sd(p_i − y_i)/√n.

## GATE LEGS (verbatim, frozen)
Dev gate — pooled dev LL@20.5 beats BOTH baselines (league base rate; naive trailing-10), else arm dead, no virgin read. Virgin legs — (i) LL@20.5 ≤ the reference arm's (arm A if it passes dev; otherwise the dev-passing arm with the lowest pooled dev LL) and ≤ best baseline's; (ii) calibration |mean P(over 20.5) − actual| ≤ 1.0pp, SE reported, breach within 1 SE = PROVISIONAL PASS; (iii) dev per-season sign check for both-pass. Both-pass: among passing arms, lower pooled virgin LL ships; one → ships; none → FAIL.
Mechanical reading as in PREREG_S_SE2 (variant sign check ≥2 of 3 vs the reference arm; ties → simpler arm A before B before C).

## Outputs
Engine `engine/total_shots/`; `results_dev.json` (+ CSV); `results_virgin.json`;
`fitted_params_virgin.json`; on PASS, `predictions/t_se2_virgin_predictions.csv`
(FT ladder only — total shots FT-only, halves share null). Verdict `reports/T_SE2_VERDICT.md`.
