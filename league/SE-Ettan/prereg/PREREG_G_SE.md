# Pre-registration — G-SE (SE-Ettan goals model)

Frozen: 2026-11-10 WIB, before any fitting. Design authority:
`analysis/MODEL_DESIGN.md` (G-SE); features X1 (goals-only fallback — no
xG exists in this feed: no `expected_goals*` key in any of 2,880 payloads,
no shotmap), X2 REJECTED, X5; evidence EDA F1/F2/F3/F4/F6.
Reference: production Dixon-Coles in `model_v2.py`; programme analogue
`PREREG_G_QA.md` with the architecture carried over verbatim (ratings
fitted by direct Poisson log-likelihood maximisation, scipy L-BFGS,
sum-to-zero identification, ridge 1e-3; rho grid (0.0, −0.05, −0.10,
−0.15) by training log-likelihood; MAXG = 10; tau = standard
Dixon-Coles low-score correction; home init 0.25). The ONLY reference
divergences: the observation is goals-only in every match (the X1 blend's
documented fallback), because the Ettan feed carries no xG in any season;
there is NO ENTRANT arm (X2 rejected, EDA F4 — see Arms); and the variant
arm is SHRINK, defined verbatim from `PREREG_G_FI.md` (see Arms).

Frozen EDA facts (all from `analysis/eda_summary.json` / EDA.md):
dev scored window 2022–2024, n = 1,440; warm-up 2021 partial, 262 played
matches of 480 fixtures, no events; virgin 2025 complete, n = 480;
2026 untouched confirmatory reserve. Dev scored: OU 2.5 over-rate
0.5833 (1.5: 0.791, 3.5: 0.340), home win rate 0.4313, draw rate
0.2097, home goals 1.6104 / away goals 1.3771 per match. Goals trait
reliable: split-half r goals-for 0.562 (dev 2021–2024, n = 57 teams) /
0.703 (scored window, n = 49), goals-against 0.742 / 0.604.
Frozen halves constant: goals_1h_share = 0.4385 (event times, 4,299
goals, 1,439 matches, 2022–2024; awarded match 4398485 excluded).
Format: two independent groups (Ettan Norra / Ettan Södra, 16 teams
each), no cross-group matches in the feed, no group term fitted (EDA
F1: Norra outscores Södra by ~0.3–0.5 goals/match in every season —
recorded as a format fact, not acted on).

Phases: all rows are ordinary rows (phase `norra` / `sodra` flags
carried, never filtered; no playoffs, no championship/relegation split
in this feed) per the frozen phase rule in
`analysis/DATA_UNDERSTANDING.md`.

## Arms
1. **Gate Zero** — the reference above, unmodified. A team with no
   fitted rating (absent from the training seasons) is predicted at
   league mean (attack/defence exponents 0.0).
2. **SHRINK** — Gate Zero plus the sanctioned G-J2-lesson change,
   defined verbatim from `PREREG_G_FI.md`: at prediction time a team
   with n < 6 prior in-league matches has a *= n/6, d *= n/6, where n
   is the number of matches the team played in the training data
   strictly before the predicted season (all matches in that season's
   expanding fit); n ≥ 6 → no change; n = 0 → exponents 0.0 (identical
   to the league-mean fallback). The scaling applies to both the attack
   and the defence exponent, for home and away teams alike. Source
   note: QA's `arms.py` / `dc.py` do NOT define SHRINK (QA's arms are
   Gate Zero + ENTRANT only), so no SHRINK definition is invented
   here — the FI definition above is the one carried over, unchanged.
   SHRINK matters in SE because warm-up 2021 is partial (262 of 480
   fixtures played), so several teams enter scored 2022 with few prior
   in-league matches.
3. **NO ENTRANT arm** — X2 is rejected (EDA F4): 27 dev entrant
   transitions (10 in 2022, 8 in 2023, 9 in 2024), mean GF diff
   −0.013, GA diff +0.081 vs league team mean; GF negative in 13/27,
   GA positive in 15/27; per-season means flip sign (2022 +0.064 /
   −0.082, 2023 +0.013 / +0.067, 2024 −0.120 / +0.276). No systematic
   entrant tilt — entrants mix strong relegated Superettan sides with
   weak promoted Division 2 sides, and the two cancel. This is the SE
   divergence from QA, which adopted ENTRANT on 4 transitions
   (GF −0.356 / GA +0.360, signs 4/4).

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
Warm-up 2021 (partial, 262 played matches, no events); evaluation
seasons 2022–2024 (pooled n = 1,440), season-blocked (expanding fit
strictly before each season's first match). Metrics: 1X2 LL, RPS,
OU2.5 LL per season and pooled, for both arms and both baselines.
The dev harness must not read 2025/2026 rows.

## Virgin protocol
Virgin = 2025 (n = 480, complete season), read ONCE, only for
dev-passing arms. Fit expands to all matches ≤ 2024.
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
passes, G-SE verdict is FAIL and nothing ships.
Mechanical reading: an arm passes iff it survives the dev gate AND
passes virgin legs (i)–(ii) (PROVISIONAL counts) AND, for variants,
leg (iii); Gate Zero is exempt from (iii). Ties → simpler arm (Gate
Zero, SHRINK). If Gate Zero fails its dev gate, variants are moot,
verdict FAIL, virgin NOT read.

## Outputs
Engine `engine/goals/`; `results_dev.json` (+ CSV); `results_virgin.json`;
`fitted_params_virgin.json`; on PASS, `predictions/g_se_virgin_predictions.csv`
(1H/2H presentation via frozen goals constant 0.4385). Verdict `reports/G_SE_VERDICT.md`.
