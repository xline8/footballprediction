# Pre-registration — G-EC (EC-SerieA goals model)

Frozen: 2026-11-10, before any fitting. Design authority:
`analysis/MODEL_DESIGN.md` (G-EC); features X1 (goals-only fallback — no
xG exists in this feed: no `expected_goals*` key in any of 1,565
payloads, no shotmap), X2 entrant offset ADOPTED, X5; evidence
F1/F2/F4/F6. Reference pattern: programme Dixon-Coles (FI G analogue,
CH G port). Documented port divergence: ratings fitted by direct
Poisson log-likelihood maximisation (scipy L-BFGS, sum-to-zero
identification, ridge 1e-3) instead of the production sweep optimiser;
rho selected from the grid (0.0, −0.05, −0.10, −0.15) by training
log-likelihood at the fitted ratings; MAXG = 10; tau = standard
Dixon-Coles low-score correction. All rows are ordinary rows (First
Stage 120 + Second Stage 120 + Final Stage 2 per season 2021–2024;
2025 is a 312-match season after a format change — used complete
as-is for the virgin).

## Arms
1. **Gate Zero** — the reference above, unmodified. A team with no
   fitted rating (absent from the training seasons) is predicted at
   league mean (attack/defence exponents 0.0).
2. **ENTRANT** — Gate Zero plus: at prediction time, a team in its
   entrant season has its attack exponent shifted by −0.1013 and its
   defence exponent shifted by −0.1903 (both frozen, from EDA F4).
   The shifts are the log factors of the dev-measured entrant offsets
   against the dev scored mean team goals 1.2541/match
   (1821 goals / 726 matches / 2): attack factor
   (1.2541 − 0.1208)/1.2541 = 0.9037, log −0.1013; defence factor
   (1.2541 + 0.2625)/1.2541 = 1.2093, log +0.1903, applied as a
   reduction of the defence exponent because a worse defence raises
   the opponent's expected goals. Entrant = a team that played no
   match in the immediately preceding season (EDA F4 definition: the
   6 dev transitions are 2022: 1236950, 618246; 2023: 6612, 1345405;
   2024: 6609 — returning after absence — and 49572; mean GF −0.121 /
   GA +0.263, GA positive in 6/6). The offset applies to the team's
   fitted rating if it has one from an earlier season (returning
   team), otherwise to the league-mean fallback (0.0).

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
Warm-up 2021; scored seasons 2022–2024 (pooled n = 726),
season-blocked (expanding fit strictly before each season's first
match: train on seasons < S to score season S). Metrics: 1X2 LL,
RPS, OU2.5 LL per season and pooled, for both arms and both
baselines. The dev harness must not read 2025/2026 rows.

## Virgin protocol
Virgin = 2025 (n = 312, complete season), read ONCE, only for
dev-passing arms. Fit expands to all matches ≤ 2024. Calibration:
mean predicted − actual for home-win rate and OU2.5 over-rate,
SE = sd(p_i − y_i)/√n.

## GATE LEGS (verbatim, frozen)
Dev gate — pooled dev 1X2 LL, RPS and OU2.5 LL of an arm must beat
BOTH baselines (climatology and naive trailing-10), else the arm is
dead. Virgin legs — (i) LL leg: arm's virgin 1X2 LL ≤ Gate Zero's
AND ≤ each baseline's, and its virgin OU2.5 LL ≤ each baseline's;
(ii) calibration leg: |mean predicted − actual| ≤ 1.0pp pooled for
home-win rate and for OU2.5 over-rate, SEs reported; a breach within
1 SE of the boundary is recorded PROVISIONAL PASS, beyond it FAIL;
(iii) per-season sign check on dev (ENTRANT 1X2 LL ≤ Gate Zero 1X2
LL in at least half the dev seasons, i.e. ≥ 2 of 3) for the
both-pass rule. Both-pass rule: if Gate Zero and ENTRANT both pass
all legs, the lower pooled virgin 1X2 LL ships; if only one passes,
it ships; if none passes, G-EC verdict is FAIL and nothing ships.
Mechanical reading: an arm passes iff it survives the dev gate AND
passes virgin legs (i)–(ii) (PROVISIONAL counts) AND, for the
variant, leg (iii); Gate Zero is exempt from (iii). Ties → simpler
arm (Gate Zero before ENTRANT). If Gate Zero fails its dev gate,
variants are moot, verdict FAIL, virgin NOT read.

## Evaluation lines (frozen, EDA F6)
Primary: 1X2 and OU 2.5 (dev over-rates 1.5: 0.712, 2.5: 0.464,
3.5: 0.251; n = 726). Home win rate 0.4766, draw rate 0.2824 in the
same window. Halves presentation via the frozen goals constant
0.4616 only (config.yaml); no halves constant exists for any count
market. Predictions-only: no EC odds/settlement source in-system.

## Outputs
Engine `engine/goals/`; `results_dev.json` (+ CSV);
`results_virgin.json`; `fitted_params_virgin.json`; on PASS,
`predictions/g_ec_virgin_predictions.csv` (1H/2H presentation via
frozen goals constant 0.4616). Verdict `reports/G_EC_VERDICT.md`.
