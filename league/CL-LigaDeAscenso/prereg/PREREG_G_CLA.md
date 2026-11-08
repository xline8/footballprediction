# Pre-registration — G-CLA (Chile Liga de Ascenso goals model)

Frozen: 2026-11-10, before any fitting. Branch `build/cl-ascenso`.
Design authority: `league/CL-LigaDeAscenso/analysis/MODEL_DESIGN.md`
(G-CLA); features per `analysis/FEATURES.md` (X1 DROPPED — no xG
exists in this league at all, so the observation is goals-only; X2
ADOPTED — the parent CL-LigaDePrimera corpus exists and exactly 2
relegated teams arrive per season). Reference: production
Dixon-Coles in `model_v2.py` (class `DC`), hl = 270; sibling
analogues: `league/CL-LigaDePrimera/prereg/PREREG_G_CL.md` (same
country, parent tier) and `league/DK-1Division/prereg/PREREG_G_DK1.md`
(X2 transplant definition, carried over verbatim).
Phase rule (frozen, MODEL_DESIGN): play-off ties are **excluded**
from every fit and every score (the Ascenso feed, unlike the
parent Primera's, contains a promotion play-off every season:
6/8/12/12/12 ties in 2021–2025). Population rule (frozen): only
`finished = 1 AND phase = regular` rows exist for this build —
this also excludes the 62 never-started 2021 placeholder rows
with fake 0-0 scores (DATA_UNDERSTANDING defect). The virgin is
scored on the 240 finished regular rows of 2025.
Calibration is defined as **actual − predicted** everywhere in
this build.

## Reference architecture (all arms share unless an arm says otherwise)

- Dixon-Coles fit, copied pattern from production `model_v2.py`:
  iterative multiplicative updates, 14 sweeps, damping 0.7, +0.25
  smoothing, home advantage fitted (init 0.28), attack/defence per
  team (init 0), score matrix MAXG = 10, production `tau` correction.
- Rho per fit from grid (0.0, −0.05, −0.10, −0.15) by weighted
  log-likelihood on goals only, as production.
- Observation: goals only. (No blend pair can exist here —
  expected_goals is absent from every one of the 1,515 payloads.)
- Time decay w = 0.5 ** ((cutoff − match_date).days / 270) — frozen,
  no search.
- Fit scope for target season S: all CL-LigaDeAscenso modelling-
  population matches dated strictly before the first match date
  of S (expanding, season-blocked).
- Teams unseen in training start at the league mean (a = d = 0).

## Arms

1. **Gate Zero** — the unmodified reference above.
2. **Arm SHRINK** (sanctioned G-J2-lesson arm) — Gate Zero plus
   exactly one change at prediction time: for a team with fewer
   than 6 prior in-league matches in the training window, its
   fitted attack and defence ratings are shrunk toward the league
   mean: `a *= n/6`, `d *= n/6` where n = its prior in-league match
   count (n = 0 ⇒ a = d = 0, identical to Gate Zero's unseen rule;
   the arm bites exactly for teams with 1–5 prior matches — the
   season-opener failure mode; under season-blocked fitting that
   band may not occur, which is itself a recorded finding if so).
   Nothing else changes.
3. **Arm X2** (mover tier offset; DK-1Division definition verbatim,
   tier names adapted) — Gate Zero plus: for a team whose
   CL-LigaDeAscenso training count n is < 12 and which played
   ≥ 10 matches in the parent CL-LigaDePrimera's immediately
   preceding season, its fitted attack and defence ratings are
   blended toward the ratings it earned in a Dixon-Coles fit
   (same reference architecture) on that parent preceding season
   alone (same FotMob team ids):
   `rating = (1 − w) · own + w · parent`, with
   `w = (12 − n)/12 · min(1, n_parent/20)`, where n_parent is the
   team's match count in that parent season. The parent fit is
   causal: it uses only the parent season strictly before the
   target season. Nothing else changes.

## Dev protocol

- Training seed = 2021 (finished regular, n = 178); evaluation
  seasons 2022, 2023, 2024 (pooled scored n = 752) under the
  season-blocked walk-forward.
- Metrics per arm per season and pooled: mean 1X2 LL, mean RPS
  (H, D, A), mean OU2.5 LL. Baselines: climatology — for target
  season S, pooled outcome rates + OU2.5 over-rate of all seasons
  strictly before S (modelling population only).
- The dev harness must not read 2025 or 2026 rows at all.

## Virgin protocol

- Virgin = 2025 (n = 240, last complete season), read ONCE,
  only for arms passing the dev gate, after dev results are frozen.
  Fit = all modelling-population matches before the first 2025
  match date. Climatology = pooled 2021–2024 rates. Calibration:
  actual − mean predicted for home-win rate and OU2.5 over-rate,
  SE = sd(y_i − p_i)/√n.
- 2026 (233 matches, in progress) is the reserved confirmatory
  window — never read in this build.

## GATE LEGS (verbatim, frozen)

Dev gate — pooled dev 1X2 LL and RPS must beat climatology, and OU2.5 LL must beat the base-rate baseline, else the arm is dead. Virgin legs — (i) LL leg: arm's virgin 1X2 LL ≤ Gate Zero's AND ≤ climatology's; (ii) calibration leg: |actual − mean predicted| ≤ 1.0pp pooled for home-win rate and for OU2.5 over-rate, SEs reported; a breach within 1 SE of the boundary is recorded PROVISIONAL PASS, beyond it FAIL; (iii) per-season sign check on dev (arm LL ≤ Gate Zero LL in at least half the dev seasons) for the both-pass rule. Both-pass rule: if Gate Zero and a variant both pass all legs, the lower pooled virgin 1X2 LL ships; if only one passes, it ships; if none passes, G-CLA verdict is FAIL and nothing ships.

Mechanical reading: an arm passes iff it survives the dev gate AND
passes virgin legs (i)–(ii) (PROVISIONAL counts, recorded as such)
AND, for variant arms, leg (iii); Gate Zero is exempt from (iii).
Ties go to the simpler arm (Gate Zero before SHRINK before X2). If Gate Zero
fails its own dev gate, variants are moot, verdict FAIL, virgin
NOT read.

## Outputs

Engine `league/CL-LigaDeAscenso/engine/goals/`; dev results
`results_dev.json` (+ CSV); virgin `results_virgin.json`; fitted
params `fitted_params_virgin.json`; on PASS, virgin predictions
`league/CL-LigaDeAscenso/predictions/g_cla_virgin_predictions.csv`
(shipped arm; 1H/2H presentation via frozen goals constant 0.4273).
Verdict: `league/CL-LigaDeAscenso/reports/G_CLA_VERDICT.md`.
Production code untouched. No push. No merge.
