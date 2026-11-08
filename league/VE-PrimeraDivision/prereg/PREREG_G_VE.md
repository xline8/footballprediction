# Pre-registration — G-VE (VE-PrimeraDivision goals model)

Frozen: 2026-11-10, before any fitting. Branch `build/ve-primera`.
Design authority: `league/VE-PrimeraDivision/analysis/MODEL_DESIGN.md`
(G-VE); features per `analysis/FEATURES.md` (X1 degraded goals-only,
SHRINK adopted, X2 DROPPED — no parent-tier corpus); evidence per
`analysis/EDA.md` (levels, split-half traits, 2026 count drift).
Reference: production Dixon-Coles in `model_v2.py` (class `DC`),
hl = 270; closest analogues: `league/BO-PrimeraDivision/prereg/PREREG_G_BO.md`
(also goals-only, no xG), `league/J1/prereg/PREREG_G_J1.md`.

## Reference architecture (all arms share unless an arm says otherwise)

- Dixon-Coles fit, copied pattern from production `model_v2.py`:
  iterative multiplicative updates, 14 sweeps, damping 0.7, +0.25
  smoothing, home advantage fitted (init 0.28), attack/defence per
  team (init 0), score matrix MAXG = 10, production `tau` correction.
- Rho per fit from grid (0.0, −0.05, −0.10, −0.15) by weighted
  log-likelihood on goals only, as production.
- Observation: **goals only for every match.** This league has no xG
  (shotmap 0% in all seasons, 0 expected_goals keys), so the
  production blend's documented goals-only fallback applies to 100%
  of observations.
- Time decay w = 0.5 ** ((cutoff − match_date).days / 270), frozen.
- Fit scope for target block S: all VE regular matches dated strictly
  before the first match date of S (expanding, season-blocked).
  Play-off rows (phase=playoff) never enter any fit or scored window.
- Teams unseen in training start at the league mean (a = d = 0).
- Team identity: canonicalised CSV names (= team_id identity).
- Awarded matches 3575291 (2021-06-27, Zamora FC 0–3 Zulia) and
  1000018666 (2026-07-31, Anzoategui FC 0–3 Deportivo Tachira)
  enter as score-based goals observations (no Goal events).

## Arms

1. **Gate Zero** — the unmodified reference above.
2. **Arm SHRINK** (sanctioned G-J2-lesson arm) — Gate Zero plus exactly
   one change at prediction time: for a team with fewer than 6 prior
   in-league matches in the training window, fitted attack/defence are
   shrunk toward the league mean: `a *= n/6`, `d *= n/6`, n = prior
   in-league match count (n = 0 ⇒ identical to Gate Zero's unseen rule;
   the arm bites exactly for teams with 1–5 prior matches — promoted
   clubs entering a season, the season-opener failure mode).

## Dev protocol

- Training seed = 2021+2022 regular (n = 492); evaluation blocks
  2023, 2024 regular (pooled n = 392), season-blocked walk-forward.
- Metrics per arm per block and pooled: mean 1X2 LL, mean RPS, mean
  OU2.5 LL. Baseline: climatology — for target block S, pooled outcome
  rates + OU2.5 over-rate of all blocks strictly before S.
- The dev harness must not read 2025 or 2026 rows.

## Virgin protocol

- Virgin = **2025 regular, a complete season (n = 182)**, read ONCE,
  only for arms passing the dev gate, after dev results freeze.
  2026 (in progress) is NOT read for goals; it is the reserved
  confirmatory window. NOTE (known before the read): 2025 is NOT a
  scoring outlier (2.335 goals/match vs 2.403 in the dev window).
- Fit = all regular matches before the first 2025 match date.
  Climatology = pooled rates through 2024. Calibration:
  mean predicted − actual for home-win rate and OU2.5 over-rate,
  SE = sd(p_i − y_i)/√n. Calibration is reported as actual − predicted
  in the verdict (sign flipped consistently); the gate uses |.|.

## GATE LEGS (verbatim, frozen)

Dev gate — pooled dev 1X2 LL and RPS of an arm must beat climatology, and OU2.5 LL must beat the base-rate baseline, else the arm is dead. Virgin legs — (i) LL leg: arm's virgin 1X2 LL ≤ Gate Zero's AND ≤ climatology's; (ii) calibration leg: |mean predicted − actual| ≤ 1.0pp pooled for home-win rate and for OU2.5 over-rate, SEs reported; a breach within 1 SE of the boundary is recorded PROVISIONAL PASS, beyond it FAIL; (iii) per-season sign check on dev (arm LL ≤ Gate Zero LL in at least half the dev seasons) for the both-pass rule. Both-pass rule: if Gate Zero and a variant both pass all legs, the lower pooled virgin 1X2 LL ships; if only one passes, it ships; if none passes, G-VE verdict is FAIL and nothing ships.

Mechanical reading: an arm passes iff it survives the dev gate AND
passes virgin legs (i)–(ii) (PROVISIONAL counts, recorded as such)
AND, for variant arms, leg (iii); Gate Zero is exempt from (iii).
Ties go to the simpler arm (Gate Zero before SHRINK). If Gate Zero
fails its own dev gate, variants are moot, verdict FAIL, virgin
NOT read.

## Outputs

Engine `league/VE-PrimeraDivision/engine/goals/`; dev results
`results_dev.json`; virgin `results_virgin.json`; fitted params
`fitted_params_virgin.json`; on PASS, virgin predictions
`league/VE-PrimeraDivision/predictions/g_ve_virgin_predictions.csv`
(shipped arm; FT columns + halves via the frozen goals constant
0.4478, presentation only). Verdict:
`league/VE-PrimeraDivision/reports/G_VE_VERDICT.md`.
Production code untouched. No push. No merge.
