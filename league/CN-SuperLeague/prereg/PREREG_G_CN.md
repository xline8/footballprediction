# Pre-registration — G-CN (China Super League goals model)

Frozen: 2026-11-10, before any fitting. Branch `build/cn-superleague`.
Design authority: `league/CN-SuperLeague/analysis/MODEL_DESIGN.md` (G-CN);
features per `analysis/FEATURES.md` (X1 adopted in goals-only form — no
xG exists anywhere in this corpus: no `expected_goals` stat key, no
shotmap; X2 dropped, SHRINK is the sanctioned substitute). Reference:
production Dixon-Coles in `model_v2.py` (class `DC`), hl = 270; sibling
analogue: `league/TH-ThaiLeague/prereg/PREREG_G_TH.md`.
Era restriction (frozen, from EDA): fits use **2023+ only** — the 2024
level step (goals 2.78→3.13/match), the 2021 COVID group/playoff
format and the 2022 18-team season with stats-feed anomalies are
excluded eras, documented in `analysis/EDA.md`.
Phase rule (frozen): every row carries a phase flag; all phases are
ordinary rows in every fit (in the 2023+ fit era all seasons are a
plain 16-team double round-robin); no phase feature anywhere.
Calibration is defined as **actual − predicted** everywhere in this build.

## Reference architecture (all arms share unless an arm says otherwise)

- Dixon-Coles fit, copied pattern from production `model_v2.py`:
  iterative multiplicative updates, 14 sweeps, damping 0.7, +0.25
  smoothing, home advantage fitted (init 0.28), attack/defence per
  team (init 0), score matrix MAXG = 10, production `tau` correction.
- Rho per fit from grid (0.0, −0.05, −0.10, −0.15) by weighted
  log-likelihood on goals only, as production.
- Observation: goals only.
- Time decay w = 0.5 ** ((cutoff − match_date).days / 270) — frozen,
  no search.
- Fit scope for target season S: all CN matches (2023+ era) dated
  strictly before the first match date of S (expanding, season-blocked).
- Teams unseen in training start at the league mean (a = d = 0).

## Arms

1. **Gate Zero** — the unmodified reference above.
2. **Arm SHRINK** (sanctioned G-J2-lesson arm) — Gate Zero plus exactly
   one change at prediction time: for a team with fewer than 6 prior
   in-league matches in the training window, its fitted attack and
   defence ratings are shrunk toward the league mean: `a *= n/6`,
   `d *= n/6` where n = its prior in-league match count (n = 0 ⇒
   a = d = 0, identical to Gate Zero's unseen rule). Nothing else
   changes. X2 evidence: 8 team ids first appearing in 2023+ show a
   mean first-season GF gap −0.369 and GA gap +0.089 goals/match
   (analysis/mover_gap.json). No hard-coded tier offset is used.

## Dev protocol

- Training seed = 2023; evaluation seasons 2024, 2025 (pooled scored
  n = 480) under the season-blocked walk-forward.
- Metrics per arm per season and pooled: mean 1X2 LL, mean RPS
  (H, D, A), mean OU2.5 LL. Baselines: climatology — for target
  season S, pooled outcome rates + OU2.5 over-rate of all era seasons
  strictly before S.
- The dev harness must not read 2026 rows at all.

## Virgin protocol

- Virgin = 2026 (n = 240, last complete season, ended 2026-11-08),
  read ONCE, only for arms passing the dev gate, after dev results
  are frozen. Fit = all era matches before the first 2026 match date.
  Climatology = pooled 2023–2025 rates. Calibration: actual − mean
  predicted for home-win rate and OU2.5 over-rate,
  SE = sd(y_i − p_i)/√n.
- No later season exists in the warehouse; there is no confirmatory
  window in this build.

## GATE LEGS (verbatim, frozen)

Dev gate — pooled dev 1X2 LL and RPS must beat climatology, and OU2.5 LL must beat the base-rate baseline, else the arm is dead. Virgin legs — (i) LL leg: arm's virgin 1X2 LL ≤ Gate Zero's AND ≤ climatology's; (ii) calibration leg: |actual − mean predicted| ≤ 1.0pp pooled for home-win rate and for OU2.5 over-rate, SEs reported; a breach within 1 SE of the boundary is recorded PROVISIONAL PASS, beyond it FAIL; (iii) per-season sign check on dev (arm LL ≤ Gate Zero LL in at least half the dev seasons) for the both-pass rule. Both-pass rule: if Gate Zero and a variant both pass all legs, the lower pooled virgin 1X2 LL ships; if only one passes, it ships; if none passes, G-CN verdict is FAIL and nothing ships.

Mechanical reading: an arm passes iff it survives the dev gate AND
passes virgin legs (i)–(ii) (PROVISIONAL counts, recorded as such)
AND, for variant arms, leg (iii); Gate Zero is exempt from (iii).
Ties go to the simpler arm (Gate Zero before SHRINK). If Gate Zero
fails its own dev gate, variants are moot, verdict FAIL, virgin
NOT read.

## Outputs

Engine `league/CN-SuperLeague/engine/goals/`; dev results
`results_dev.json` (+ CSV); virgin `results_virgin.json`; fitted
params `fitted_params_virgin.json`; on PASS, virgin predictions
`league/CN-SuperLeague/predictions/g_cn_virgin_predictions.csv`
(shipped arm; 1H/2H presentation via frozen goals constant 0.4458).
Verdict: `league/CN-SuperLeague/reports/G_CN_VERDICT.md`.
Production code untouched. No push. No merge.
