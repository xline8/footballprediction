# Pre-registration — G-RL2 (RO-LigaII goals model)

Frozen: 2026-11-10, before any fitting. Branch `build/ro-liga2`.
Design authority: `league/RO-LigaII/analysis/MODEL_DESIGN.md` (G-RL2);
features per `analysis/FEATURES.md` (X1 goals-only form, X5 goals-only
form); evidence per `analysis/EDA.md` (F1/F2/F4).
Reference: production Dixon-Coles in `model_v2.py` (class `DC`),
hl = 270; RO-LigaI analogue: `league/RO-LigaI/prereg/PREREG_G_RO.md`.

## Reference architecture (all arms share unless an arm says otherwise)

- Dixon-Coles fit, copied pattern from production `model_v2.py`:
  iterative multiplicative updates, 14 sweeps, damping 0.7, +0.25
  smoothing, home advantage fitted (init 0.28), attack/defence per
  team (init 0), score matrix MAXG = 10, production `tau` correction.
- Rho per fit from grid (0.0, −0.05, −0.10, −0.15) by weighted
  log-likelihood on goals only, as production.
- Observation: **goals only** (X1 fallback form — no xG, stats or
  shotmap exist for this league in any of the 1,513 payloads; there
  is no blend).
- Time decay w = 0.5 ** ((cutoff − match_date).days / 270) — frozen.
- Fit scope for target season S: all included RO-LigaII matches
  (phase != relegation_playoff) dated strictly before the first
  match date of S (expanding, season-blocked).
- Teams unseen in training start at the league mean (a = d = 0).

## Arms

1. **Gate Zero** — the unmodified reference above.
2. **Arm SHRINK** (sanctioned G-J2-lesson arm; FEATURES F4) — Gate
   Zero plus exactly one change at prediction time: for a team with
   fewer than 6 prior in-league matches in the training window, its
   fitted attack and defence ratings are shrunk toward the league
   mean: `a *= n/6`, `d *= n/6` where n = its prior in-league match
   count (n = 0 ⇒ a = d = 0, identical to Gate Zero's unseen rule).
   Nothing else changes.
- Note: at season starts in this league, team prior counts are 0 or
  ≥25 (no team ever has 1–5 prior matches) — SHRINK may therefore be
  numerically identical to Gate Zero under season-blocked fitting.
  This must be verified mechanically (compare per-match predictions);
  if identical, the both-pass rule below ties to the simpler arm.

## Dev protocol

- Training seed = 2021/2022; evaluation seasons 2022/2023, 2023/2024,
  2024/2025 (pooled n = 786) under the season-blocked walk-forward.
- Metrics per arm per season and pooled: mean 1X2 LL, mean RPS
  (H, D, A), mean OU2.5 LL. Baselines: climatology — for target
  season S, pooled outcome rates + OU2.5 over-rate of all seasons
  strictly before S.
- The dev harness must not read 2025/2026 or 2026/2027 rows at all.

## Virgin protocol

- Virgin = 2025/2026 (n = 317, complete), read ONCE, only for arms
  passing the dev gate, after dev results are frozen. Fit = all
  matches before the first 2025/2026 match date. Climatology =
  pooled 2021/2022–2024/2025 rates. Calibration: mean predicted −
  actual for home-win rate and OU2.5 over-rate, SE = sd(p_i − y_i)/√n.
- 2026/2027 (n = 140, in progress) is reserved confirmatory and is
  NOT read in this build.

## GATE LEGS (verbatim, frozen)

Dev gate — pooled dev 1X2 LL and RPS of an arm must beat climatology, and OU2.5 LL must beat the base-rate baseline, else the arm is dead. Virgin legs — (i) LL leg: arm's virgin 1X2 LL ≤ Gate Zero's AND ≤ climatology's; (ii) calibration leg: |mean predicted − actual| ≤ 1.0pp pooled for home-win rate and for OU2.5 over-rate, SEs reported; a breach within 1 SE of the boundary is recorded PROVISIONAL PASS, beyond it FAIL; (iii) per-season sign check on dev (arm LL ≤ Gate Zero LL in at least half the dev seasons) for the both-pass rule. Both-pass rule: if Gate Zero and a variant both pass all legs, the lower pooled virgin 1X2 LL ships; if only one passes, it ships; if none passes, G-RL2 verdict is FAIL and nothing ships.

Mechanical reading: an arm passes iff it survives the dev gate AND
passes virgin legs (i)–(ii) (PROVISIONAL counts, recorded as such)
AND, for variant arms, leg (iii); Gate Zero is exempt from (iii).
Ties go to the simpler arm (Gate Zero before SHRINK). If Gate Zero
fails its own dev gate, variants are moot, verdict FAIL, virgin
NOT read.

## Outputs

Engine `league/RO-LigaII/engine/goals/`; dev results
`results_dev.json` (+ CSV); virgin `results_virgin.json`; fitted
params `fitted_params_virgin.json`; on PASS, virgin predictions
`league/RO-LigaII/predictions/g_rl2_virgin_predictions.csv`
(shipped arm; 1H/2H presentation via frozen goals constant 0.457419).
Verdict: `league/RO-LigaII/reports/G_RL2_VERDICT.md`.
Production code untouched. No push. No merge.
