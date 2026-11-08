# Pre-registration — G-EG (EG-PremierLeague goals model)

Frozen: 2026-11-09, before any fitting. Branch `build/eg-premier`.
Design authority: `league/EG-PremierLeague/analysis/MODEL_DESIGN.md`
(G-EG); features per `analysis/FEATURES.md` (X1 goals-only — the
xG/shotmap era starts AT the virgin season, so the blend fallback is
goals-only in every dev fold and in the virgin training window);
evidence per `analysis/EDA.md`. Reference: production Dixon-Coles in
`model_v2.py` (class `DC`), hl = 270; engine port pattern:
`league/SA-ProLeague/engine/goals/`.
Phase rule (frozen): all phases are ordinary rows in every window;
no phase feature anywhere (2024/2025 split and 2025/2026 split are
pooled).

## Reference architecture (all arms share unless an arm says otherwise)

- Dixon-Coles fit, copied pattern from production `model_v2.py`:
  iterative multiplicative updates, 14 sweeps, damping 0.7, +0.25
  smoothing, home advantage fitted (init 0.28), attack/defence per
  team (init 0), score matrix MAXG = 10, production `tau` correction.
- Rho per fit from grid (0.0, −0.05, −0.10, −0.15) by weighted
  log-likelihood on goals only, as production.
- Observation (X1): blend 0.5·goals + 0.5·xG when both xG present,
  goals-only fallback otherwise. In this league xG exists only from
  2025/2026, so every training observation in dev AND in the virgin
  fit (trained strictly before 2025/2026) is goals-only by the
  fallback — the reference's documented behaviour, not a variant.
- Time decay w = 0.5 ** ((cutoff − match_date).days / 270); blend
  weight 0.5 — both frozen, no search.
- Fit scope for target season S: all EG matches dated strictly
  before the first match date of S (expanding, season-blocked).
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
   season-opener failure mode; EG has promoted clubs entering from
   outside the warehouse every season). Nothing else changes.
   No X3 arm exists: set-play xG is virgin-era only (FEATURES).

## Dev protocol

- Training seed = 2021/2022 (warm-up only, never scored); evaluation
  seasons **2022/2023, 2023/2024, 2024/2025** (pooled n = 837) under
  the season-blocked walk-forward.
- Metrics per arm per season and pooled: mean 1X2 LL, mean RPS
  (H, D, A), mean OU2.5 LL. Baselines: climatology — for target
  season S, pooled outcome rates + OU2.5 over-rate of all seasons
  strictly before S.
- The dev harness must not read 2025/2026 or 2026/2027 rows at all.

## Virgin protocol

- Virgin = 2025/2026 (n = 322, complete), read ONCE, only for arms
  passing the dev gate, after dev results are frozen. Fit = all
  matches before the first 2025/2026 match date. Climatology =
  pooled 2021/2022–2024/2025 rates. Calibration = actual rate −
  mean predicted probability (home-win rate and OU2.5 over-rate),
  SE = sd(y_i − p_i)/√n.
- 2026/2027 is NOT read in this build (reserved confirmatory).

## GATE LEGS (verbatim, frozen)

Dev gate — pooled dev 1X2 LL and RPS of an arm must beat climatology, and OU2.5 LL must beat the base-rate baseline, else the arm is dead. Virgin legs — (i) LL leg: arm's virgin 1X2 LL ≤ Gate Zero's AND ≤ climatology's; (ii) calibration leg: |actual − predicted| ≤ 1.0pp pooled for home-win rate and for OU2.5 over-rate, SEs reported; a breach within 1 SE of the boundary is recorded PROVISIONAL PASS, beyond it FAIL; (iii) per-season sign check on dev (arm LL ≤ Gate Zero LL in at least half the dev seasons) for the both-pass rule. Both-pass rule: if Gate Zero and a variant both pass all legs, the lower pooled virgin 1X2 LL ships; if only one passes, it ships; if none passes, G-EG verdict is FAIL and nothing ships.

Mechanical reading: an arm passes iff it survives the dev gate AND
passes virgin legs (i)–(ii) (PROVISIONAL counts, recorded as such)
AND, for variant arms, leg (iii); Gate Zero is exempt from (iii).
With three dev seasons, leg (iii) means ≥2 of 3. Ties go to the
simpler arm (Gate Zero before SHRINK). If Gate Zero fails its own
dev gate, variants are moot, verdict FAIL, virgin NOT read.

## Outputs

Engine `league/EG-PremierLeague/engine/goals/`; dev results
`results_dev.json` (+ CSV); virgin `results_virgin.json`; fitted
params `fitted_params_virgin.json`; on PASS, virgin predictions
`league/EG-PremierLeague/predictions/g_eg_virgin_predictions.csv`
(shipped arm; 1H/2H presentation via frozen goals constant 0.4202).
Verdict: `league/EG-PremierLeague/reports/G_EG_VERDICT.md`.
Production code untouched. No push. No merge.
