# Pre-registration — G-SK2 (SK-2Liga goals model)

Frozen: 2026-11-10, before any fitting. Branch `build/sk-2-liga`.
Design authority: `league/SK-2Liga/analysis/MODEL_DESIGN.md` (G-SK2);
features per `analysis/FEATURES.md` (X1 goals-only form, X2);
evidence per `analysis/EDA.md` (F1/F2/F4).
Reference: production Dixon-Coles in `model_v2.py` (class `DC`),
hl = 270; analogues: `PREREG_G_SK.md`, `PREREG_G_J1.md`.

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
- Fit scope for target season S: all finished SK-2Liga matches
  dated strictly before the first match date of S (expanding,
  season-blocked).
- Teams unseen in training start at the league mean (a = d = 0).

## Arms

1. **Gate Zero** — the unmodified reference above.
2. **Arm SHRINK** (sanctioned G-J2-lesson arm; FEATURES/EDA F4
   context) — Gate Zero plus exactly one change at prediction time:
   for a team with fewer than 6 prior in-league matches in the
   training window, its fitted attack and defence ratings are
   shrunk toward the league mean: `a *= n/6`, `d *= n/6` where n =
   its prior in-league match count (n = 0 ⇒ a = d = 0, identical to
   Gate Zero's unseen rule). Nothing else changes. Expected to be
   near-identical to Gate Zero here (every returning club carries a
   full prior season; newcomers sit at n = 0 where both arms
   agree); registered anyway, ties go to Gate Zero.
3. **Arm X2** — Gate Zero plus the mover tier offset (feature X2,
   EDA F4). A club is a *relegated mover* for target season S when
   its most recent prior season is the season immediately preceding
   S, it played that season in 1. Liga (FotMob id 176, team present
   in the 1. Liga finished payloads for that season), and it did
   not play 1. Liga in season S. Movers are keyed by FotMob team
   id (names are unstable in this league — diacritic variants).
   For a relegated mover, at prediction time in season S only:
   - attack: `a += log(max(mu + dGF, 0.10) / mu)`
   - defence: `d += log((mu + dGA) / mu)`
   where mu is the decay-weighted mean goals per team per match in
   the training window, and (dGF, dGA) are the cumulative mean
   first-season deviations of transitions **completed before S**
   (EDA F4, frozen values): S = 2022/2023 → no completed transition
   (arm ≡ Gate Zero that season, by construction); S = 2023/2024 →
   (−0.022593, −0.133704); S = 2024/2025 → (0.109050, −0.029839);
   S = 2025/2026 → (0.150539, −0.236926). Movers by season (team
   id — canonical name): 2022/2023 {291155 FK Pohronie};
   2023/2024 {155166 Liptovsky Mikulas}; 2024/2025 {2255 Zlate
   Moravce}; 2025/2026 {2169 Dukla Banska Bystrica}. A club
   entering from a lower tier (3. Liga) has no prior-season
   warehouse record and starts at the league mean in every arm.
   Clubs with no immediately-preceding-season record in 1. Liga
   or 2. Liga start at the league mean in every arm.

## Dev protocol

- Training seed = 2021/2022; evaluation seasons 2022/2023, 2023/2024,
  2024/2025 (pooled n = 613) under the season-blocked walk-forward.
- Metrics per arm per season and pooled: mean 1X2 LL, mean RPS
  (H, D, A), mean OU2.5 LL. Baselines: climatology — for target
  season S, pooled outcome rates + OU2.5 over-rate of all seasons
  strictly before S. Also report the naive trailing-10 baseline
  (team trailing-10 goal rates) for the 1X2 LL comparison in the
  verdict.
- The dev harness must not read 2025/2026 or 2026/2027 rows at all.

## Virgin protocol

- Virgin = 2025/2026 (n = 240, complete), read ONCE, only for arms
  passing the dev gate, after dev results are frozen. Fit = all
  finished matches before the first 2025/2026 match date.
  Climatology = pooled 2021/2022–2024/2025 rates. Calibration:
  mean predicted − actual for home-win rate and OU2.5 over-rate,
  SE = sd(p_i − y_i)/√n.

## GATE LEGS (verbatim, frozen)

Dev gate — pooled dev 1X2 LL and RPS of an arm must beat climatology, and OU2.5 LL must beat the base-rate baseline, else the arm is dead. Virgin legs — (i) LL leg: arm's virgin 1X2 LL ≤ Gate Zero's AND ≤ climatology's; (ii) calibration leg: |mean predicted − actual| ≤ 1.0pp pooled for home-win rate and for OU2.5 over-rate, SEs reported; a breach within 1 SE of the boundary is recorded PROVISIONAL PASS, beyond it FAIL; (iii) per-season sign check on dev (arm LL ≤ Gate Zero LL in at least half the dev seasons) for the both-pass rule. Both-pass rule: if Gate Zero and a variant both pass all legs, the lower pooled virgin 1X2 LL ships; if only one passes, it ships; if none passes, G-SK2 verdict is FAIL and nothing ships.

Mechanical reading: an arm passes iff it survives the dev gate AND
passes virgin legs (i)–(ii) (PROVISIONAL counts, recorded as such)
AND, for variant arms, leg (iii); Gate Zero is exempt from (iii).
Ties go to the simpler arm (Gate Zero before SHRINK before X2).
If Gate Zero fails its own dev gate, variants are moot, verdict
FAIL, virgin NOT read.

## Outputs

Engine `league/SK-2Liga/engine/goals/`; dev results
`results_dev.json` (+ CSV); virgin `results_virgin.json`; fitted
params `fitted_params_virgin.json`; on PASS, virgin predictions
`league/SK-2Liga/predictions/g_sk2_virgin_predictions.csv`
(shipped arm; 1H/2H presentation via frozen goals constant 0.4940).
Verdict: `league/SK-2Liga/reports/G_SK2_VERDICT.md`.
Production code untouched. No push. No merge.
