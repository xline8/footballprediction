# Pre-registration — G-LV (Latvia Virsliga goals model)

Frozen: 2026-11-10, before any fitting. Branch `build/lv-virsliga`.
Design authority: `league/LV-Virsliga/analysis/MODEL_DESIGN.md`
(G-LV); features per `analysis/FEATURES.md` (X1/X2 DROPPED — no xG
exists in this league and Latvia has exactly one league in the
warehouse); evidence per `analysis/EDA.md`. Reference: production
Dixon-Coles in `model_v2.py` (class `DC`), hl = 270; sibling
analogue: `league/RU-1Division/prereg/PREREG_G_RU1.md`
(goals-only).
Phase rule (frozen): every kept row is phase `regular` — calendar-
year seasons, straight round-robin, no play-off rows in the feed
(the 6 relegation finals were excluded in PREPROCESSING and are
not league rows). No phase feature anywhere.
Calibration = **actual − predicted** everywhere in this build.

## Virgin-hygiene disclosure

Step-1 inventory computed aggregate per-season counts (including
2026) from the payloads. Those are era facts, as in every prior
league's DATA_UNDERSTANDING; no per-match model output and no gate
quantity was computed from 2026 before this freeze. The virgin is
NOT burned.

## Reference architecture (all arms share unless an arm says otherwise)

- Dixon-Coles fit, copied pattern from production `model_v2.py`:
  iterative multiplicative updates, 14 sweeps, damping 0.7, +0.25
  smoothing, home advantage fitted (init 0.28), attack/defence per
  team (init 0), score matrix MAXG = 10, production `tau` correction.
- Rho per fit from grid (0.0, −0.05, −0.10, −0.15) by weighted
  log-likelihood on goals only, as production.
- Observation: goals only (no xG in any of the 1,017 payloads; the
  X1 blend cannot exist here).
- Time decay w = 0.5 ** ((cutoff − match_date).days / 270) — frozen.
- Fit scope for target season S: all LV-Virsliga matches dated
  strictly before the first match date of S (expanding,
  season-blocked). Teams keyed on team ids (two ids carry two name
  spellings; names are never keys).
- Teams unseen in training start at the league mean (a = d = 0).

## Arms

1. **Gate Zero** — the unmodified reference above.
2. **Arm SHRINK** (sanctioned G-J2-lesson arm) — Gate Zero plus
   exactly one change at prediction time: for a team with fewer
   than 6 prior in-league matches in the training window, its
   fitted attack and defence ratings are shrunk toward the league
   mean: `a *= n/6`, `d *= n/6`, n = prior in-league match count.
   Nothing else changes. (Motivation: EDA entrant gaps ΔGF −0.453 /
   ΔGA +0.255, n=6 entrants — the largest entrant gap in the
   program so far.)

## Dev protocol

- Training seed = 2021; evaluation seasons 2022, 2023, 2024, 2025
  (pooled n = 720 league matches; the 6 relegation finals are
  excluded) under the season-blocked walk-forward.
- Metrics per arm per season and pooled: mean 1X2 LL, mean RPS,
  mean OU2.5 LL. Baselines: climatology — for target season S,
  pooled outcome rates + OU2.5 over-rate of all seasons strictly
  before S.
- The dev harness must not read 2026 rows at all.

## Virgin protocol

- Virgin = 2026 (n = 179 played matches; the RFS–Riga FC round-36
  fixture is absent from the warehouse), read ONCE, only for arms
  passing the dev gate, after dev results are frozen. Fit = all
  matches before the first 2026 match date. Climatology =
  pooled 2021–2025 rates. Calibration: mean actual −
  predicted for home-win rate and OU2.5 over-rate, SE =
  sd(y_i − p_i)/√n.

## GATE LEGS (verbatim, frozen)

Dev gate — pooled dev 1X2 LL and RPS of an arm must beat climatology, and OU2.5 LL must beat the base-rate baseline, else the arm is dead. Virgin legs — (i) LL leg: arm's virgin 1X2 LL ≤ Gate Zero's AND ≤ climatology's; (ii) calibration leg: |mean actual − predicted| ≤ 1.0pp pooled for home-win rate and for OU2.5 over-rate, SEs reported; a breach within 1 SE of the boundary is recorded PROVISIONAL PASS, beyond it FAIL; (iii) per-season sign check on dev (arm LL ≤ Gate Zero LL in at least half the dev seasons) for the both-pass rule. Both-pass rule: if Gate Zero and a variant both pass all legs, the lower pooled virgin 1X2 LL ships; if only one passes, it ships; if none passes, G-LV verdict is FAIL and nothing ships.

Mechanical reading: an arm passes iff it survives the dev gate AND
passes virgin legs (i)–(ii) (PROVISIONAL counts, recorded as such)
AND, for variant arms, leg (iii); Gate Zero is exempt from (iii).
Ties go to the simpler arm (Gate Zero before SHRINK). If Gate Zero
fails its own dev gate, variants are moot, verdict FAIL, virgin
NOT read.

## Outputs

Engine `league/LV-Virsliga/engine/goals/`; dev results
`results_dev.json` (+ per-match `predictions_dev.csv`); virgin
`results_virgin.json`; fitted params `fitted_params_virgin.json`;
on PASS, virgin predictions
`league/LV-Virsliga/predictions/g_lv_virgin_predictions.csv`
(shipped arm; 1H/2H presentation via frozen goals constant 0.4569).
Verdict: `league/LV-Virsliga/reports/G_LV_VERDICT.md`.
Production code untouched. No push. No merge.
