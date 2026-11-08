# Pre-registration — G-TN (Tunisia Ligue I goals model)

Frozen: 2026-11-10 WIB, before any fitting. Branch
`build/tn-ligue1`. Design authority:
`league/TN-LigueI/analysis/MODEL_DESIGN.md` (candidate G-TN);
features per `league/TN-LigueI/analysis/FEATURES.md`
(X1 goals-only, X5 baseline-only; X2–X9 dropped); evidence per
`league/TN-LigueI/analysis/EDA.md` (F1/F2/F3/F4/F5).
Reference implementation: production Dixon-Coles in `model_v2.py`
(class `DC`, `probs`), production config `v2_config.json` (hl = 270),
as carried by the programme analogues `PREREG_G_SE.md` /
`PREREG_G_QA.md` / `PREREG_G_LU.md` / `PREREG_G_NI.md` (ratings fitted
by direct Poisson log-likelihood maximisation, scipy L-BFGS,
sum-to-zero identification, ridge 1e-3; rho grid (0.0, −0.05, −0.10,
−0.15) by training log-likelihood; MAXG = 10; tau = standard
Dixon-Coles low-score correction; home intercept fitted, init 0.25).

## Frozen EDA facts (all from `analysis/eda_summary.json` / EDA.md)

Dev scored window 2022/23–2024/25, n = 602 model matches (all
phases, awarded excluded); warm-up 2021/22 complete, n = 156;
virgin 2025/26 complete, n = 237 model rows (3 awarded excluded);
2026/27 partial (n = 56) is the untouched confirmatory reserve.
Dev scored: OU2.5 over-rate 0.3389 (1.5: 0.5748, 3.5: 0.1512), home
win rate 0.4635, draw rate 0.2824, home goals 1.1960 / away goals
0.8056 per match (2.0017 goals/match). Goals trait weak by the
program-standard chronological split-half (dev era 2021–2025,
n = 62 team-seasons: GF 0.235, GA 0.251; scored window n = 46:
GF 0.168, GA 0.302) but phase-attenuated: random split-half mean
over 20 seeds GF 0.389 / GA 0.463, regular-phase-only chronological
GF 0.497 / GA 0.622. Frozen halves constant: goals_1h_share =
0.4539 (goal-event times, 547/1,205 goals, 602 matches used, dev
scored window; awarded matches contribute nothing). Format: group
era 2021/22–2023/24 (2 groups + championship/relegation groups,
double round robin within each phase) then single 16-team table
from 2024/25; all phases enter model data (90-minute scores, no
extra time anywhere). Nine awarded matches are excluded from every
fit and score (4096477, 4145842, 4145834, 4608322, 4608325, 4612011,
4919136, 4919206, 5178447). Goals level has no trend across complete
seasons (1.70 → 2.05 → 1.90 → 2.03 → 1.72); the 270-day decay is the
only drift defence in this design. Teams are keyed by FotMob team
id, never by name (accent variants: 8153 Esperance/Espérance,
102104 Olympique de Beja/Béja, 405958 Etoile Metlaoui/Métlaoui).

## Reference architecture (all arms share this unless an arm says otherwise)

- Dixon-Coles fit, production pattern: direct Poisson
  log-likelihood maximisation as in the analogues above, home
  advantage `h` fitted, attack `a` and defence `d` per team,
  score matrix to MAXG = 10 with the production `tau` low-score
  correction.
- Rho: chosen per fit from the grid (0.0, −0.05, −0.10, −0.15) by
  training log-likelihood on goals only, exactly as production.
- Observation (X1): goals only in every match — no xG exists in any
  of the 1,060 payloads, so the blend's documented goals-only
  fallback applies throughout (no season has xG).
- Time decay: weight w = 0.5 ** ((cutoff − match_date).days / 270).
  Half-life 270 days is the production value, frozen — no search.
- Fit scope for a target season S: all TN model matches (all
  phases, awarded excluded) with date strictly before the first
  match date of S (expanding window, season-blocked: one fit per
  target season, whole season predicted from that fit).
- Teams unseen in training start at the league mean (a = d = 0).

## Arms

1. **Gate Zero** — the unmodified reference above. Entrants start
   at the league mean.
2. **SHRINK** — Gate Zero plus the sanctioned G-J2-lesson change,
   defined verbatim from `PREREG_G_FI.md` (via `PREREG_G_SE.md`):
   at prediction time a team with n < 6 prior in-league matches has
   a *= n/6, d *= n/6, where n is the number of matches the team
   played in the training data strictly before the predicted season
   (all matches in that season's expanding fit); n ≥ 6 → no change;
   n = 0 → exponents 0.0 (identical to the league-mean fallback).
   The scaling applies to both the attack and the defence exponent,
   for home and away teams alike.
3. **NO ENTRANT arm** — X2 is dropped (FEATURES.md / EDA F4): no
   sibling Tunisian league exists in the warehouse (only FotMob id
   544 for Tunisia), so no mover tilt can be estimated from
   in-warehouse prior-tier data. Entrants (1–2 in each of 2022/23,
   2023/24, 2024/25, 2025/26) arrive from Ligue II, which is not in
   the warehouse. This is the TN divergence from QA, which adopted
   ENTRANT on 4 transitions.

## Baselines (both, frozen)

- **Climatology / league base rate**: pooled outcome rates (H/D/A)
  and OU2.5 over-rate over the training seasons only (prior seasons
  pooled), as constant probabilities for every scored match.
- **Naive trailing-10**: for each match, independent Poissons with
  means equal to each team's mean goals scored in its last 10 league
  matches strictly before the match (fewer if fewer exist; if none,
  the training league mean team goals/match). 1X2 and OU2.5
  probabilities from the resulting 11×11 score matrix (MAXG = 10).
  No home advantage, no ratings, no fitted parameter beyond the
  training league mean fallback.

## Dev protocol

Warm-up 2021/22 (156 played model matches); evaluation seasons
2022/23–2024/25 (pooled n = 602), season-blocked (expanding fit
strictly before each season's first match). Metrics: 1X2 LL, RPS,
OU2.5 LL per season and pooled, for both arms and both baselines.
The dev harness must not read 2025/26 or 2026/27 rows at all. Virgin
data is touched only by the separate virgin step, once, after dev
results are frozen in the results file.

## Virgin protocol

Virgin = 2025/26 (n = 237 model rows, complete season), read ONCE,
only for dev-passing arms. Fit expands to all matches ≤ 2024/25.
Calibration: mean predicted − actual for home-win rate and OU2.5
over-rate, SE = sd(p_i − y_i)/√n.

## GATE LEGS (verbatim, frozen)

Dev gate — pooled dev 1X2 LL and RPS of an arm must beat climatology
AND naive trailing-10, and OU2.5 LL must beat both baselines, else the
arm is dead. Virgin legs — (i) LL leg: arm's virgin 1X2 LL ≤ Gate
Zero's AND ≤ climatology's; (ii) calibration leg: |mean predicted −
actual| ≤ 1.0pp pooled for home-win rate and for OU2.5 over-rate, SEs
reported; a breach within 1 SE of the boundary is recorded PROVISIONAL
PASS, beyond it FAIL; (iii) per-season sign check on dev (arm LL ≤
Gate Zero LL in at least half the dev seasons) for the both-pass rule.
Both-pass rule: if Gate Zero and a variant both pass all legs, the lower
pooled virgin 1X2 LL ships; if only one passes, it ships; if none
passes, G-TN verdict is FAIL and nothing ships.

Mechanical reading: an arm passes iff it survives the dev gate AND
passes virgin legs (i)–(ii) (PROVISIONAL counts) AND, for variants,
leg (iii); Gate Zero is exempt from (iii). Ties → simpler arm (Gate
Zero, SHRINK). If Gate Zero fails its dev gate, variants are moot,
verdict FAIL, virgin NOT read.

## Outputs

Engine `engine/goals/`; `results_dev.json` (+ CSV);
`results_virgin.json`; `fitted_params_virgin.json`; on PASS,
`predictions/g_tn_virgin_predictions.csv` (1H/2H presentation via
frozen goals constant 0.4539). Verdict `reports/G_TN_VERDICT.md`.
