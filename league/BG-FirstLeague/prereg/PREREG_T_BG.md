# Pre-registration — T-BG (Bulgaria First Professional League total-shots model)

Frozen: 2026-11-10, before any fitting. Branch `build/bg-first`.
Design authority: `analysis/MODEL_DESIGN.md` (T-BG); features X5
(FEATURES.md; total-shots reliability for 0.700 / against 0.737).
Reference: the shots family (production total-shots experiments +
J1 construction); sibling analogue `league/ZA-PSL/prereg/
PREREG_T_ZA.md` — the shared engine is carried over in form,
changing only league, seasons, lines and the halves decision below.
The tuning/level-layer fitting objective is at THIS league's
preregistered primary line (17.5) everywhere — a copied harness
fitting at the sibling league's line (21.5) is a named defect class
here; the coordinator will grep for it.
Phase rule (frozen): all phases in every window, flagged; no phase
feature. Team identity is the FotMob team id.
Calibration = **actual − predicted** everywhere in this build.

- Target: total shots (stats feed, as published). Primary line
  **17.5** (scored-dev over-rate 0.473, closest to 0.5). Ladder
  16.5 / 17.5 / 18.5 reported, gate at 17.5.
- Arms: **A** — v1 pattern (joint Poisson regression ratings +
  moment NB size + naive trailing-10 ensemble); **B** — v2 pattern
  (A + level layer fitted on the tuning season); **C** — E9
  (A with NB r from the trailing-200 window). Constructions,
  grids and tie rules exactly as PREREG_T_ZA / PREREG_T_J1.
- Training/tuning season 2021/2022 (stats rows n = 216, never part
  of the gate pool); dev scored 2022/2023–2024/2025 (stats rows
  n = 841) per-match walk-forward. Dev harness must not read
  2025/2026 / 2026/2027 rows.
- Baselines: league base rate; naive trailing-10.
- Virgin: 2025/2026 (stats rows n = 293), read ONCE, only for arms
  passing the dev gate. Calibration at 17.5 = actual − mean
  predicted, SE = sd(y_i − p_i)/√n.
- Halves: **FT-only** (no period splits, no event source for
  shots; frozen, constant null in config).

## GATE LEGS (verbatim, frozen)

Dev gate — pooled dev LL@17.5 beats BOTH baselines (league base rate; naive trailing-10), else the arm is dead, no virgin read. Virgin legs — (i) LL@17.5 ≤ Gate Zero's (arm A's) AND ≤ best baseline's (arm A: ≤ best baseline's); (ii) calibration |actual − mean P(over 17.5)| ≤ 1.0pp, SE reported, breach within 1 SE = PROVISIONAL PASS; (iii) dev per-season sign check for both-pass (variant dev LL@17.5 ≤ arm A's in ≥2 of 3 dev seasons). Both-pass: all passing → lowest pooled virgin LL ships; one → ships; none → FAIL.

Mechanical reading: an arm passes iff it survives the dev gate AND
passes virgin legs (i)–(ii) (PROVISIONAL counts, recorded as such)
AND, for variants, leg (iii). Ties → simpler arm (A before B
before C). Arm A dev failure ⇒ variants moot, FAIL, virgin
NOT read.

## Outputs

Engine `engine/total_shots/`; `results_dev.json` (+ CSV);
`results_virgin.json`; `fitted_params.json` /
`fitted_params_virgin.json`; on PASS,
`predictions/t_bg_virgin_predictions.csv` (FT ladder
16.5/17.5/18.5 only — no halves columns, FT-only market). Verdict
`reports/T_BG_VERDICT.md`.
