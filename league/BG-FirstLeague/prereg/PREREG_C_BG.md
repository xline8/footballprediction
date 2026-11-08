# Pre-registration — C-BG (Bulgaria First Professional League corners model)

Frozen: 2026-11-10, before any fitting. Branch `build/bg-first`.
Design authority: `analysis/MODEL_DESIGN.md` (C-BG); features X5,
X9-partial (FEATURES.md); evidence EDA (corners for 0.659 / against
0.583; possession 0.822 / 0.822; `touches_opp_box` and `big_chance`
absent from the feed). Reference: production `model_corners_v3.py`;
sibling analogue `league/ZA-PSL/prereg/PREREG_C_ZA.md` — the shared
engine is carried over verbatim in form (HL = 270 base rates,
rolling-5 relative factors clamped [0.6, 1.7], core mean `mu_cs`,
NB pmf grid 0..50, per-season gamma/beta/r fitting on prior-season
walk-forward rows only, gamma grid (0.0, 0.15, 0.3, 0.45, 0.6, 0.8),
r clamped [1.02, 5.0], territorial multiplier clamped [0.70, 1.43],
min-8 of last-10 validity rule, date-grouped predict-then-update
state). One documented divergence, named here in advance: the
engine's `multiplier()` gains a third arm branch `poss` (below);
Gate Zero's branch is byte-identical to the sibling's.
The beta/gamma/r fitting objective is at THIS league's preregistered
primary line (9.5) everywhere — the TH build's audit caught a copied
harness fitting betas at the sibling league's line; that defect
class is named here in advance and the coordinator will grep for it.
Phase rule (frozen): all phases in every window, flagged; no phase
feature. Team identity is the FotMob team id.
Calibration = **actual − predicted** everywhere in this build.

- Target: total corners (stats feed). Primary line **9.5**
  (scored-dev over-rate 0.467, closest to 0.5). Ladder 8.5 / 9.5 /
  10.5 reported, gate at 9.5.
- Arms: **Gate Zero (X9)** — production covariates `BallPossesion` +
  `big_chance`, beta grids exactly as PREREG_C_J1 (poss ∈ ±{0, .01,
  .02, .03, .04}; bc ∈ ±{0, .025, .05, .075, .10}; joint 9×9 grid,
  multiplier `exp(beta·z)` clamped [0.70, 1.43]). Recorded in
  advance: `big_chance` does not exist in this league, so z_bc is
  None on every row and this multiplier is inactive everywhere —
  Gate Zero here is the core engine; that is reported, not patched.
  **Arm POSS** — identical engine; territorial multiplier =
  `exp(beta_poss · z_poss)` with beta_poss ∈ ±{0, .01, .02, .03,
  .04} (the J1 possession grid), clamped [0.70, 1.43], inactive
  where a team's trailing possession is missing (min-8 rule).
  X7 (box touches) is NOT an arm: the key does not exist here.
- Training seed 2021/2022; dev evaluation 2022/2023–2024/2025
  (stats rows n = 841). Dev harness must not read 2025/2026 /
  2026/2027 rows.
- Baselines: league base rate (per-season NB from decay-weighted
  pre-season window, as PREREG_C_J1) and naive trailing-10 (X5)
  through the same per-season NB size.
- Virgin: 2025/2026 (stats rows n = 293), read ONCE, only for arms
  passing the dev gate. Calibration at 9.5 = actual − mean
  predicted, SE = sd(y_i − p_i)/√n.
- Halves: **FT-only** (no period splits, no event source for
  corners; frozen, constant null in config).

## GATE LEGS (verbatim, frozen)

Dev gate — pooled dev LL@9.5 beats BOTH baselines (league base rate; naive trailing-10), else the arm is dead, no virgin read. Virgin legs — (i) LL@9.5 ≤ Gate Zero's AND ≤ best baseline's (Gate Zero: ≤ best baseline's); (ii) calibration |actual − mean P(over 9.5)| ≤ 1.0pp, SE reported, breach within 1 SE = PROVISIONAL PASS; (iii) dev per-season sign check for both-pass (variant dev LL@9.5 ≤ Gate Zero's in ≥2 of 3 dev seasons). Both-pass: both → lower pooled virgin LL ships; one → ships; none → FAIL.

Mechanical reading: an arm passes iff it survives the dev gate AND
passes virgin legs (i)–(ii) (PROVISIONAL counts, recorded as such)
AND, for the variant, leg (iii). Ties → simpler arm (Gate Zero
before POSS). Gate Zero dev failure ⇒ variants moot, FAIL, virgin
NOT read.

## Outputs

Engine `engine/corners/`; `results_dev.json` (+ CSV);
`results_virgin.json`; `fitted_params_virgin.json`; on PASS,
`predictions/c_bg_virgin_predictions.csv` (FT ladder 8.5/9.5/10.5
only — no halves columns, FT-only market). Verdict
`reports/C_BG_VERDICT.md`.
