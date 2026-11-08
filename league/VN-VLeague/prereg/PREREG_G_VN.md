# Pre-registration — G-VN (Vietnam V-League goals model)

Frozen: 2026-11-10, before any fitting. Branch `build/vn-vleague`.
Design authority: `league/VN-VLeague/analysis/MODEL_DESIGN.md` (G-VN);
features per `analysis/FEATURES.md` (X1 goals-only form, fitted home
advantage; X2 dropped — no Vietnamese sibling); evidence per
`analysis/EDA.md` (F1/F2/F3/F11/F13) and `analysis/eda_summary.json`.
Reference: production Dixon-Coles in `model_v2.py` (class `DC`),
hl = 270; analogue: `PREREG_G_KZ.md` (sibling scores-only league,
same data pattern).

## Reference architecture (all arms share unless an arm says otherwise)

- Dixon-Coles fit, copied pattern from production `model_v2.py`:
  iterative multiplicative updates, 14 sweeps, damping 0.7, +0.25
  smoothing, home advantage fitted (init 0.28), attack/defence per
  team (init 0), score matrix MAXG = 10, production `tau` correction.
- Rho per fit from grid (0.0, −0.05, −0.10, −0.15) by weighted
  log-likelihood on goals only, as production.
- Observation: **goals only** (X1 fallback form — xG is absent in
  every payload of this league; there is no blend).
- Time decay w = 0.5 ** ((cutoff − match_date).days / 270) — frozen.
- Fit scope for target season S: all finished VN-VLeague matches
  dated strictly before the first match date of S (expanding,
  season-blocked).
- Teams unseen in training start at the league mean (a = d = 0).

## Arms

1. **Gate Zero** — the unmodified reference above.
2. **Arm SHRINK** (sanctioned G-J2-lesson arm; FEATURES/EDA F13
   context) — Gate Zero plus exactly one change at prediction time:
   for a team with fewer than 6 prior in-league matches in the
   training window, its fitted attack and defence ratings are
   shrunk toward the league mean: `a *= n/6`, `d *= n/6` where n =
   its prior in-league match count (n = 0 ⇒ a = d = 0, identical to
   Gate Zero's unseen rule). Nothing else changes. EDA F13 measured
   zero teams in the 1–5 prior-match band at any target-season start
   (every team has 0, 6–23, or 24+ prior matches), so SHRINK is
   expected to be identical to Gate Zero — the verdict must verify
   that from the results file rather than assume it. Ties go to Gate
   Zero.

No X2 arm is registered: no Vietnamese sibling league exists in the
warehouse, so no mover prior can be estimated (brief; EDA F4 records
the entrant pattern — mean GF diff +0.18, GA diff −0.02, n=3 real
entrants — descriptively only).

## Dev protocol

- Training seed = 2021 (84 finished matches); evaluation seasons
  2022, 2023, 2023/2024, 2024/2025 (pooled n = 654) under the
  season-blocked walk-forward.
- Metrics per arm per season and pooled: mean 1X2 LL, mean RPS
  (H, D, A), mean OU2.5 LL. Primary line OU2.5 (dev pooled
  over-rate 0.445, closest to 50% among 1.5/2.5/3.5 — EDA F11).
  Baselines: climatology — for target season S, pooled outcome
  rates + OU2.5 over-rate of all seasons strictly before S. Also
  report the naive trailing-10 baseline (team trailing-10 goal
  rates) for the 1X2 LL comparison in the verdict.
- The dev harness must not read 2025/2026 rows at all.

## Virgin protocol

- Virgin = 2025/2026 (n = 182, COMPLETE season, 2025-08-15 –
  2026-06-07, 14 teams, 26 rounds), read ONCE, only for arms
  passing the dev gate, after dev results are frozen. Fit = all
  finished matches before the first 2025/2026 match date.
  Climatology = pooled 2021–2024/2025 rates. Calibration: mean
  predicted − actual for home-win rate and OU2.5 over-rate,
  SE = sd(p_i − y_i)/√n.
- 2026/2027 (in progress) is NOT a virgin window; season-end
  confirmatory read only, no gate depends on it.

## GATE LEGS (verbatim, frozen)

Dev gate — pooled dev 1X2 LL and RPS of an arm must beat climatology, and OU2.5 LL must beat the base-rate baseline, else the arm is dead. Virgin legs — (i) LL leg: arm's virgin 1X2 LL ≤ Gate Zero's AND ≤ climatology's; (ii) calibration leg: |mean predicted − actual| ≤ 1.0pp pooled for home-win rate and for OU2.5 over-rate, SEs reported; a breach within 1 SE of the boundary is recorded PROVISIONAL PASS, beyond it FAIL; (iii) per-season sign check on dev (arm LL ≤ Gate Zero LL in at least half the dev seasons) for the both-pass rule. Both-pass rule: if Gate Zero and a variant both pass all legs, the lower pooled virgin 1X2 LL ships; if only one passes, it ships; if none passes, G-VN verdict is FAIL and nothing ships.

Mechanical reading: an arm passes iff it survives the dev gate AND
passes virgin legs (i)–(ii) (PROVISIONAL counts, recorded as such)
AND, for variant arms, leg (iii); Gate Zero is exempt from (iii).
Ties go to the simpler arm (Gate Zero before SHRINK). If Gate Zero
fails its own dev gate, variants are moot, verdict FAIL, virgin NOT
read.

## Outputs

Engine `league/VN-VLeague/engine/goals/`; dev results
`results_dev.json` (+ CSV, force-added); virgin `results_virgin.json`;
fitted params `fitted_params_virgin.json`; on PASS, virgin predictions
`league/VN-VLeague/predictions/g_vn_virgin_predictions.csv`
(shipped arm; 1H/2H presentation via frozen goals constant 0.4468).
Verdict: `league/VN-VLeague/reports/G_VN_VERDICT.md`.
Production code untouched. No push. No merge.
