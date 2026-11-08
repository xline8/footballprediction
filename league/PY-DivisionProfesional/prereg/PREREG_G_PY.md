# Pre-registration — G-PY (PY-DivisionProfesional goals model)

Frozen: 2026-11-09, before any fitting. Branch `build/py-division`.
Design authority: `league/PY-DivisionProfesional/analysis/MODEL_DESIGN.md`
(G-PY); features per `analysis/FEATURES.md` (X1 degraded goals-only,
SHRINK adopted, X2 DROPPED); evidence per `analysis/EDA.md` (F1/F2).
Reference: production Dixon-Coles in `model_v2.py` (class `DC`),
hl = 270; closest analogues: `league/BG-SecondLeague/prereg/PREREG_G_BG2.md`
(also goals-only, no xG), `league/J1/prereg/PREREG_G_J1.md`.

## Reference architecture (all arms share unless an arm says otherwise)

- Dixon-Coles fit, copied pattern from production `model_v2.py`:
  iterative multiplicative updates, 14 sweeps, damping 0.7, +0.25
  smoothing, home advantage fitted (init 0.28), attack/defence per
  team (init 0), score matrix MAXG = 10, production `tau` correction.
- Rho per fit from grid (0.0, −0.05, −0.10, −0.15) by weighted
  log-likelihood on goals only, as production.
- Observation: **goals only for every match.** This league has no xG
  (shotmap 0% in all seasons), so the production blend's documented
  goals-only fallback applies to 100% of observations.
- Time decay w = 0.5 ** ((cutoff − match_date).days / 270), frozen.
- Fit scope for target block S: all PY matches dated strictly before
  the first match date of S (expanding, tournament-blocked).
- Teams unseen in training start at the league mean (a = d = 0).
- Team identity: canonicalised CSV names (= team_id identity).

## Arms

1. **Gate Zero** — the unmodified reference above.
2. **Arm SHRINK** (sanctioned G-J2-lesson arm) — Gate Zero plus exactly
   one change at prediction time: for a team with fewer than 6 prior
   in-league matches in the training window, fitted attack/defence are
   shrunk toward the league mean: `a *= n/6`, `d *= n/6`, n = prior
   in-league match count (n = 0 ⇒ identical to Gate Zero's unseen rule;
   the arm bites exactly for teams with 1–5 prior matches — promoted
   clubs entering an Apertura, the season-opener failure mode).

## Dev protocol

- Training seed = 2021 - Apertura + 2021 - Clausura (n = 180);
  evaluation blocks 2022 - Apertura … 2025 - Clausura (8 tournaments,
  pooled n = 1,056), tournament-blocked walk-forward.
- Metrics per arm per block and pooled: mean 1X2 LL, mean RPS, mean
  OU2.5 LL. Baseline: climatology — for target block S, pooled outcome
  rates + OU2.5 over-rate of all blocks strictly before S.
- The dev harness must not read 2026 - Apertura or 2026 - Clausura rows.

## Virgin protocol

- Virgin = **2026 - Apertura, a complete tournament (n = 132)**, read
  ONCE, only for arms passing the dev gate, after dev results freeze.
  2026 - Clausura (in progress) is NOT read for goals; it is the
  reserved confirmatory window.
- Fit = all matches before the first 2026 - Apertura match date.
  Climatology = pooled rates through 2025 - Clausura. Calibration:
  mean predicted − actual for home-win rate and OU2.5 over-rate,
  SE = sd(p_i − y_i)/√n.

## GATE LEGS (verbatim, frozen)

Dev gate — pooled dev 1X2 LL and RPS of an arm must beat climatology, and OU2.5 LL must beat the base-rate baseline, else the arm is dead. Virgin legs — (i) LL leg: arm's virgin 1X2 LL ≤ Gate Zero's AND ≤ climatology's; (ii) calibration leg: |mean predicted − actual| ≤ 1.0pp pooled for home-win rate and for OU2.5 over-rate, SEs reported; a breach within 1 SE of the boundary is recorded PROVISIONAL PASS, beyond it FAIL; (iii) per-season sign check on dev (arm LL ≤ Gate Zero LL in at least half the dev seasons) for the both-pass rule. Both-pass rule: if Gate Zero and a variant both pass all legs, the lower pooled virgin 1X2 LL ships; if only one passes, it ships; if none passes, G-PY verdict is FAIL and nothing ships.

Mechanical reading: an arm passes iff it survives the dev gate AND
passes virgin legs (i)–(ii) (PROVISIONAL counts, recorded as such)
AND, for variant arms, leg (iii); Gate Zero is exempt from (iii).
Ties go to the simpler arm (Gate Zero before SHRINK). If Gate Zero
fails its own dev gate, variants are moot, verdict FAIL, virgin
NOT read.

## Outputs

Engine `league/PY-DivisionProfesional/engine/goals/`; dev results
`results_dev.json`; virgin `results_virgin.json`; fitted params
`fitted_params_virgin.json`; on PASS, virgin predictions
`league/PY-DivisionProfesional/predictions/g_py_virgin_predictions.csv`
(shipped arm; FT columns + halves via the frozen goals constant
0.418, presentation only). Verdict:
`league/PY-DivisionProfesional/reports/G_PY_VERDICT.md`.
Production code untouched. No push. No merge.
