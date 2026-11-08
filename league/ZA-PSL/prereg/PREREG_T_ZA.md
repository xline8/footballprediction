# Pre-registration — T-ZA (South Africa Premier Soccer League total-shots model)

Frozen: 2026-11-10, before any fitting. Branch `build/za-psl`.
Design authority: `analysis/MODEL_DESIGN.md` (T-ZA); evidence EDA
(total-shots trait reliability 0.751 / 0.630). Reference: the shots
family as frozen for T-J1 (v1 pattern / v2 level layer / E9
trailing-r) — see `league/J1/prereg/PREREG_T_J1.md` for the three
arms' exact constructions and mirror them, changing only league,
seasons and line; sibling run: `league/TH-ThaiLeague/prereg/PREREG_T_TH.md`.
(T-J1 ran ahead of the top-5 prospective verdict by user order; T-ZA
is a separate corpus and neither trial contaminates the other.)
Phase rule (frozen): all modelled rows are phase `regular`; no phase
feature. Team identity is the FotMob team id.
Calibration = **actual − predicted** everywhere in this build.

- Target: total shots = `total_shots_home + total_shots_away`
  (stats feed, taken as-is; pooled stats-era level ≈ 22/match).
  Primary line **21.5** (scored-dev over-rate 0.522, closest to 0.5;
  the 22.5 over-rate is 0.429). Ladder 20.5/21.5/22.5 reported,
  gate at 21.5.
- Arms: **A** v1 pattern (ratings + NB + naive ensemble);
  **B** v2 pattern (+ level layer); **C** E9 (NB r from a trailing
  window, league-level analogue).
- Training seed 2022/2023; dev 2023/2024–2024/2025 (stats rows
  n = 448); dev harness must not read 2025/2026 / 2026/2027 rows.
- Baselines: league base rate; naive trailing-10.
- Virgin: 2025/2026 (stats rows n = 240), read ONCE, only for
  dev-passing arms. Calibration at 21.5 = actual − mean predicted,
  SE = sd(y_i − p_i)/√n.
- Halves: 1H/2H presentation via the frozen total-shots constant
  0.4584.

## GATE LEGS (verbatim, frozen)

Dev gate — pooled dev LL@21.5 beats BOTH baselines (league base rate; naive trailing-10), else arm dead, no virgin read. Virgin legs — (i) LL@21.5 ≤ the reference arm's (arm A if it passes dev; otherwise the dev-passing arm with the lowest pooled dev LL) and ≤ best baseline's; (ii) calibration |actual − mean P(over 21.5)| ≤ 1.0pp, SE reported, breach within 1 SE = PROVISIONAL PASS; (iii) dev per-season sign check for both-pass. Both-pass: among passing arms, lower pooled virgin LL ships; one → ships; none → FAIL.

Mechanical reading: an arm passes iff it survives the dev gate AND
passes virgin legs (i)–(ii) (PROVISIONAL counts) AND, for variant
arms, leg (iii) — variant dev LL@21.5 ≤ the reference arm's in at
least half of the dev seasons (≥1 of 2). Ties → simpler/reference
arm (A before B before C). If arm A fails its dev gate and no other
arm passes dev either, verdict FAIL, virgin NOT read; if A fails dev
but B or C passes dev, the dev-passing arm with the lowest pooled
dev LL becomes the reference for leg (i).

## Outputs

Engine `engine/total_shots/`; `results_dev.json` (+ CSV);
`results_virgin.json`; `fitted_params_virgin.json`; on PASS,
`predictions/t_za_virgin_predictions.csv` (FT ladder 20.5/21.5/22.5
+ 1H/2H presentation via frozen constant 0.4584). Verdict
`reports/T_ZA_VERDICT.md`.
