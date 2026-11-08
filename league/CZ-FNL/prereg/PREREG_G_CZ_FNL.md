# Pre-registration — G-CZ-FNL (CZ-FNL goals model)

Frozen: 2026-11-10, before any fitting. Branch `build/cz-fnl`.
Design authority: `league/CZ-FNL/analysis/MODEL_DESIGN.md` (G-CZ-FNL);
features per `analysis/FEATURES.md` (X1 goals-only form, X2);
evidence per `analysis/EDA.md` (F1/F2/F4 equivalents: levels,
reliabilities, movers).
Reference: production Dixon-Coles in `model_v2.py` (class `DC`),
hl = 270; analogues: `PREREG_G_CZ.md`, `PREREG_G_RO.md`,
`PREREG_G_J1.md`.

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
- Fit scope for target season S: all included FNL matches
  (`phase = regular`, all 1,311 rows included) dated strictly before
  the first match date of S (expanding, season-blocked).
- Teams unseen in training start at the league mean (a = d = 0).

## Arms

1. **Gate Zero** — the unmodified reference above.
2. **Arm SHRINK** (sanctioned G-J2-lesson arm) — Gate Zero plus exactly
   one change at prediction time: for a team with fewer than 6 prior
   in-league matches in the training window, its fitted attack and
   defence ratings are shrunk toward the league mean: `a *= n/6`,
   `d *= n/6` where n = its prior in-league match count (n = 0 ⇒
   a = d = 0, identical to Gate Zero's unseen rule). Nothing else
   changes. (Structural expectation, not a freeze: under
   season-blocked fitting a team's prior in-league count at
   prediction time is only ever 0 or ≥ 30, so SHRINK may be
   identical to Gate Zero — the harness decides, and the verdict
   records it either way.)
3. **Arm X2** — Gate Zero plus the mover tier offset (feature X2,
   EDA movers table). A club is a *relegated mover* for target
   season S when its most recent prior season is the season
   immediately preceding S, it played that season in CZ-Liga
   (FotMob id 122 — membership from the CZ-Liga index, placement
   matches excluded from that corpus), and it did not play FNL in
   that season. For a relegated mover, at prediction time in season
   S only:
   - attack: `a += log(max(mu + dGF, 0.10) / mu)`
   - defence: `d += log((mu + dGA) / mu)`
   where mu is the decay-weighted mean goals per team per match in
   the training window, and (dGF, dGA) are the cumulative mean
   first-season deviations of transitions **completed before S**
   (EDA, frozen values): S = 2022/2023 → no completed transition
   (arm ≡ Gate Zero that season, by construction); S = 2023/2024 →
   (+0.545833, −0.154167); S = 2024/2025 → (+0.240625, −0.092708);
   S = 2025/2026 → (+0.240278, −0.326389). The offsets are measured
   directly on relegated entrants (attack up / defence down-GA in
   3 of 4 completed transitions; the Budějovice reversal is inside
   the cumulative means, not excluded). Clubs entering from the
   third tier or as B-teams, and clubs with no
   immediately-preceding-season record in FNL or CZ-Liga, start at
   the league mean in every arm.

## Dev protocol

- Training seed = 2021/2022; evaluation seasons 2022/2023, 2023/2024,
  2024/2025 (pooled n = 720) under the season-blocked walk-forward.
- Metrics per arm per season and pooled: mean 1X2 LL, mean RPS
  (H, D, A), mean OU2.5 LL. Baselines: climatology — for target
  season S, pooled outcome rates + OU2.5 over-rate of all seasons
  strictly before S.
- The dev harness must not read 2025/2026 or 2026/2027 rows at all.

## Virgin protocol

- Virgin = 2025/2026 (n = 240, complete), read ONCE, only for arms
  passing the dev gate, after dev results are frozen. Fit = all
  included matches before the first 2025/2026 match date.
  Climatology = pooled 2021/2022–2024/2025 rates. Calibration:
  mean predicted − actual for home-win rate and OU2.5 over-rate,
  SE = sd(p_i − y_i)/√n.

## GATE LEGS (verbatim, frozen)

Dev gate — pooled dev 1X2 LL and RPS of an arm must beat climatology, and OU2.5 LL must beat the base-rate baseline, else the arm is dead. Virgin legs — (i) LL leg: arm's virgin 1X2 LL ≤ Gate Zero's AND ≤ climatology's; (ii) calibration leg: |mean predicted − actual| ≤ 1.0pp pooled for home-win rate and for OU2.5 over-rate, SEs reported; a breach within 1 SE of the boundary is recorded PROVISIONAL PASS, beyond it FAIL; (iii) per-season sign check on dev (arm LL ≤ Gate Zero LL in at least half the dev seasons) for the both-pass rule. Both-pass rule: if Gate Zero and a variant both pass all legs, the lower pooled virgin 1X2 LL ships; if only one passes, it ships; if none passes, G-CZ-FNL verdict is FAIL and nothing ships.

Mechanical reading: an arm passes iff it survives the dev gate AND
passes virgin legs (i)–(ii) (PROVISIONAL counts, recorded as such)
AND, for variant arms, leg (iii); Gate Zero is exempt from (iii).
Ties go to the simpler arm (Gate Zero before SHRINK before X2).
If Gate Zero fails its own dev gate, variants are moot, verdict
FAIL, virgin NOT read.

## Outputs

Engine `league/CZ-FNL/engine/goals/`; dev results
`results_dev.json` (+ CSV); virgin `results_virgin.json`; fitted
params `fitted_params_virgin.json`; on PASS, virgin predictions
`league/CZ-FNL/predictions/g_cz_fnl_virgin_predictions.csv`
(shipped arm; 1H/2H presentation via frozen goals constant 0.449598).
Verdict: `league/CZ-FNL/reports/G_CZ_FNL_VERDICT.md`.
Production code untouched. No push. No merge.
