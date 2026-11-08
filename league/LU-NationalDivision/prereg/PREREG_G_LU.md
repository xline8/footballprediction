# Pre-registration — G-LU (LU-NationalDivision goals model)

Frozen: 2026-11-10 WIB, before any fitting. Branch
`build/lu-national-division`. Design authority:
`league/LU-NationalDivision/analysis/MODEL_DESIGN.md` (candidate
G-LU); features per `league/LU-NationalDivision/analysis/FEATURES.md`
(X1 goals-only, X5 baseline-only; X2–X9 dropped); evidence per
`league/LU-NationalDivision/analysis/EDA.md` (F1/F2/F3/F4).
Reference implementation: production Dixon-Coles in `model_v2.py`
(class `DC`, `probs`), production config `v2_config.json` (hl = 270),
as carried by the programme analogues `PREREG_G_SE.md` /
`PREREG_G_QA.md` (ratings fitted by direct Poisson log-likelihood
maximisation, scipy L-BFGS, sum-to-zero identification, ridge 1e-3;
rho grid (0.0, −0.05, −0.10, −0.15) by training log-likelihood;
MAXG = 10; tau = standard Dixon-Coles low-score correction; home
intercept fitted, init 0.25).

## Frozen EDA facts (all from `analysis/eda_summary.json` / EDA.md)

Dev scored window 2022/23–2024/25, n = 720; warm-up 2021/22 complete,
n = 240; virgin 2025/26 complete, n = 240; 2026/27 partial (n = 96)
is the untouched confirmatory reserve. Dev scored: OU2.5 over-rate
0.6028 (1.5: 0.8167, 3.5: 0.3889), home win rate 0.4431, draw rate
0.2014, home goals 1.6833 / away goals 1.4681 per match (3.151
goals/match). Goals trait reliable: split-half r goals-for 0.730
(dev era 2021–2025, n = 64 team-seasons) / 0.742 (scored window,
n = 48), goals-against 0.673 / 0.627. Frozen halves constant:
goals_1h_share = 0.4294 (event times, 973/2,266 goals, 720 matches,
dev scored window; match 4520839 contributes 0 goals to numerator
and denominator). Format: single table, 16 teams, 30 rounds, no
playoffs, no split (EDA F1 / DATA_UNDERSTANDING.md). Goals level
drifts down across complete seasons (3.21 → 3.34 → 3.13 → 2.99 →
2.85); the 270-day decay is the only drift defence in this design.

## Reference architecture (all arms share this unless an arm says otherwise)

- Dixon-Coles fit, production pattern: iterative / direct Poisson
  log-likelihood maximisation as in the analogues above, home
  advantage `h` fitted, attack `a` and defence `d` per team,
  score matrix to MAXG = 10 with the production `tau` low-score
  correction.
- Rho: chosen per fit from the grid (0.0, −0.05, −0.10, −0.15) by
  training log-likelihood on goals only, exactly as production.
- Observation (X1): goals only in every match — no xG exists in any
  of the 1,296 payloads, so the blend's documented goals-only
  fallback applies throughout (no season has xG).
- Time decay: weight w = 0.5 ** ((cutoff − match_date).days / 270).
  Half-life 270 days is the production value, frozen — no search.
- Fit scope for a target season S: all LU matches with date strictly
  before the first match date of S (expanding window, season-blocked:
  one fit per target season, whole season predicted from that fit).
- Teams unseen in training start at the league mean (a = d = 0).

## Arms

1. **Gate Zero** — the unmodified reference above. Movers start at
   the league mean.
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
   sibling Luxembourg league exists in the warehouse (only FotMob
   id 229 for Luxembourg), so no mover tilt can be estimated from
   in-warehouse prior-tier data. Entrants (2 in 2022/23, 2 in
   2023/24, 3 in 2024/25, 4 in 2025/26) arrive from the Division of
   Honour, which is not in the warehouse. This is the LU divergence
   from QA, which adopted ENTRANT on 4 transitions.

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

Warm-up 2021/22 (240 played matches); evaluation seasons 2022/23–
2024/25 (pooled n = 720), season-blocked (expanding fit strictly
before each season's first match). Metrics: 1X2 LL, RPS, OU2.5 LL
per season and pooled, for both arms and both baselines. The dev
harness must not read 2025/26 or 2026/27 rows at all. Virgin data
is touched only by the separate virgin step, once, after dev
results are frozen in the results file.

## Virgin protocol

Virgin = 2025/26 (n = 240, complete season), read ONCE, only for
dev-passing arms. Fit expands to all matches ≤ 2024/25.
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
passes, G-LU verdict is FAIL and nothing ships.

Mechanical reading: an arm passes iff it survives the dev gate AND
passes virgin legs (i)–(ii) (PROVISIONAL counts) AND, for variants,
leg (iii); Gate Zero is exempt from (iii). Ties → simpler arm (Gate
Zero, SHRINK). If Gate Zero fails its dev gate, variants are moot,
verdict FAIL, virgin NOT read.

## Outputs

Engine `engine/goals/`; `results_dev.json` (+ CSV);
`results_virgin.json`; `fitted_params_virgin.json`; on PASS,
`predictions/g_lu_virgin_predictions.csv` (1H/2H presentation via
frozen goals constant 0.4294). Verdict `reports/G_LU_VERDICT.md`.
