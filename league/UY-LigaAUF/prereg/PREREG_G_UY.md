# Pre-registration — G-UY (UY-LigaAUF goals model)

Frozen: 2026-11-10, before any fitting. Design authority:
`analysis/MODEL_DESIGN.md` (G-UY); features X1 (goals-only fallback — no
xG exists in this feed: no `expected_goals*` key in any of 1,717 payloads,
no shotmap), X2 entrant offset ADOPTED, X5; evidence F1/F2/F4/F6.
Reference: production Dixon-Coles in `model_v2.py`; programme analogue
`PREREG_G_QA.md` with the architecture carried over verbatim (ratings
fitted by direct Poisson log-likelihood maximisation, scipy L-BFGS,
sum-to-zero identification, ridge 1e-3; rho grid (0.0, −0.05, −0.10,
−0.15) by training log-likelihood; MAXG = 10; tau = standard
Dixon-Coles low-score correction; home init 0.25). The ONLY reference
divergence: the observation is goals-only in every match (the X1 blend's
documented fallback), because the Uruguay feed carries no xG in any
season.

Phases: all rows are ordinary rows (apertura / clausura / intermedio /
final_stage per the frozen phase rule in
`analysis/DATA_UNDERSTANDING.md`).

## Arms
1. **Gate Zero** — the reference above, unmodified. A team with no
   fitted rating (absent from the training seasons) is predicted at
   league mean (attack/defence exponents 0.0).
2. **ENTRANT** — Gate Zero plus: at prediction time, a team in its
   entrant season has its attack exponent shifted by −0.1178 and its
   defence exponent shifted by −0.1188 (both frozen, from EDA F4).
   The shifts are the log factors of the dev-measured entrant offsets
   against the dev scored mean team goals 1.1520/match
   (2062 goals / 895 matches / 2): attack factor
   (1.1520 − 0.1280)/1.1520 = 0.8889, log −0.1178; defence factor
   (1.1520 + 0.1452)/1.1520 = 1.1261, log +0.1188, applied as a
   reduction of the defence exponent because a worse defence raises
   the opponent's expected goals. Entrant = a team that played no
   match in the immediately preceding season (EDA F4 definition: the
   9 dev transitions are 2022: Danubio, Defensor Sporting, Albion;
   2023: La Luz, Racing, Cerro; 2024: Miramar Misiones, Rampla
   Juniors, Progreso; mean GF −0.128 / GA +0.145, GF negative in 8/9,
   GA positive in 5/9). The offset applies to the team's fitted
   rating if it has one from an earlier season (returning team),
   otherwise to the league-mean fallback (0.0). Note: the GA signal
   is weaker than the QA analogue (5/9 positive vs QA 4/4) and rests
   on 9 transitions — recorded here, not adjusted for.

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
Warm-up 2021; evaluation seasons 2022–2024 (pooled n = 895),
season-blocked (expanding fit strictly before each season's
first match). Metrics: 1X2 LL, RPS, OU2.5 LL per season and pooled, for
both arms and both baselines. The dev harness must not read 2025
or 2026 rows.

## Virgin protocol
Virgin = 2025 (n = 300, complete season), read ONCE, only for
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
passes, G-UY verdict is FAIL and nothing ships.
Mechanical reading: an arm passes iff it survives the dev gate AND
passes virgin legs (i)–(ii) (PROVISIONAL counts) AND, for variants,
leg (iii); Gate Zero is exempt from (iii). Ties → simpler arm (Gate
Zero, ENTRANT). If Gate Zero fails its dev gate, variants are moot,
verdict FAIL, virgin NOT read.

## Outputs
Engine `engine/goals/`; `results_dev.json` (+ CSV); `results_virgin.json`;
`fitted_params_virgin.json`; on PASS, `predictions/g_uy_virgin_predictions.csv`
(1H/2H presentation via frozen goals constant 0.4276). Verdict `reports/G_UY_VERDICT.md`.
