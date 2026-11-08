# Pre-registration — G-IN (IN-IndianFootballLeague goals model)

Frozen: 2026-11-10, before any fitting. Design authority:
`analysis/MODEL_DESIGN.md` (G-IN); features X1 (goals-only fallback —
no xG exists in this feed: no `expected_goals*` key in any of 608
payloads, no shotmap), X2 DROPPED (EDA F4); evidence F1/F2/F3/F4/F6.
Reference pattern: programme Dixon-Coles (FI G analogue, IL G port).
Documented port: the FI reference `dc.py` / `arms.py` are carried over
verbatim (iterative sweep optimiser, 14 sweeps, damping 0.7, +0.25
smoothing, home init 0.28, MAXG = 10, production tau, rho grid (0.0,
−0.05, −0.10, −0.15) by goals log-likelihood, decay HL = 270 days);
the harness is adapted from the FI `harness.py` with the naive
trailing-10 baseline added per the IL precedent. The ONLY reference
divergence: the observation is goals-only in every match (the X1
blend's documented fallback), because the Indian Football League feed
carries no xG in any season.

Phases: all rows are ordinary rows (phase flag main / championship /
relegation carried, never filtered) per the frozen phase rule in
`analysis/DATA_UNDERSTANDING.md`. The 4 awarded matches (2 in
2022/2023, 2 in 2024/2025; all disciplinary 0-3/3-0 awards whose
on-pitch scores differed) are kept as ordinary rows with
awarded=true; the header score is used, never the event-derived
score.

## Arms
1. **Gate Zero** — the unmodified reference above. A team with no
   fitted rating (absent from the training seasons) is predicted at
   league mean (attack/defence exponents 0.0).
2. **SHRINK** — Gate Zero plus the sanctioned G-J2-lesson change: at
   prediction time a team with n < 6 prior in-league matches has a *=
   n/6, d *= n/6 (counts from the training data only, FI `arms.py`
   mechanics). Expected to be numerically inert under season-blocked
   prediction in this league (any team present in a prior season has
   ≥22 prior matches; teams with no fitted rating sit at league mean
   with exponents 0.0) — same observation as CH, NO, FR and BY. It is
   run and reported anyway; the gate decides.
3. **X2 — NOT RUN.** The entrant offset was assessed pre-fitting and
   DROPPED on the frozen EDA evidence (F4): 6 dev entrant
   transitions, mean GF diff −0.110 / GA diff +0.025, signs mixed
   (GF negative 3/6, GA positive 3/6) — a ~zero, inconsistent tilt,
   the CH/NO/FR/SE drop pattern, not the FI/BY adopt pattern (8
   transitions with consistent signs). No X2 arm is fitted; this is
   recorded here so the absence is an auditable pre-fitting decision.

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
Training seed 2021/2022; evaluation seasons 2022/2023–2024/2025
(pooled n = 418), season-blocked (expanding fit strictly before each
season's first match). Metrics: 1X2 LL, RPS, OU2.5 LL per season and
pooled, for both arms and both baselines. The dev harness must not
read 2025/2026 or 2026/2027 rows.

## Virgin protocol
Virgin = 2025/2026 (n = 66, COMPLETE season: 45 regular + 15
promotion-group + 6 relegation-group matches; the following season
has already begun, confirming completion), read ONCE, only for
dev-passing arms. Fit expands to all matches ≤ 2024/2025.
Calibration: mean predicted − actual for home-win rate and OU2.5
over-rate, SE = sd(p_i − y_i)/√n. The virgin is small, so the SE
band is wide; the gate is applied as written, not softened.

## GATE LEGS (verbatim, frozen)
Dev gate — pooled dev 1X2 LL, RPS and OU2.5 LL of an arm must beat
BOTH baselines (climatology and naive trailing-10), else the arm is
dead. Virgin legs — (i) LL leg: arm's virgin 1X2 LL ≤ Gate Zero's
AND ≤ each baseline's, and its virgin OU2.5 LL ≤ each baseline's;
(ii) calibration leg: |mean predicted − actual| ≤ 1.0pp pooled for
home-win rate and for OU2.5 over-rate, SEs reported; a breach within
1 SE of the boundary is recorded PROVISIONAL PASS, beyond it FAIL;
(iii) per-season sign check on dev (variant 1X2 LL ≤ Gate Zero 1X2 LL
in at least half the dev seasons, i.e. ≥ 2 of 3) for the both-pass
rule. Both-pass rule: if Gate Zero and a variant both pass all legs,
the lower pooled virgin 1X2 LL ships; if only one passes, it ships;
if none passes, G-IN verdict is FAIL and nothing ships.
Mechanical reading: an arm passes iff it survives the dev gate AND
passes virgin legs (i)–(ii) (PROVISIONAL counts) AND, for a variant,
leg (iii); Gate Zero is exempt from (iii). Ties → simpler arm (Gate
Zero before SHRINK). If Gate Zero fails its dev gate, variants are
moot, verdict FAIL, virgin NOT read.

## Evaluation lines (frozen, EDA F6)
Primary: 1X2 and OU 2.5 (dev scored over-rates 1.5: 0.7871, 2.5:
0.5718, 3.5: 0.3565; n = 418). Home win rate 0.4450, draw rate
0.2392 in the same window. Dev scored mean team goals 1.5467/match
(1,293 goals / 418 matches / 2). Halves presentation via the
frozen goals constant 0.4387 only (config.yaml); no halves constant
exists for any count market. Predictions-only: no IN
odds/settlement source in-system.

## Known calibration risk (recorded, not adjusted)
Trait reliability is only moderate (split-half r 0.608 / 0.462) and
season-to-season team-mean correlations are weak-to-moderate, so
the expanding fit has modest signal to track — and the goals level
ROSE across the dev era (2.579 in the warm-up, then 2.727 / 3.331 /
3.182), so the level moved ~0.75 goals/match between the first and
last dev seasons; the dev gate will judge that as frozen.
Virgin-season goals/match (3.045, inventory only) sits −0.05 below
the dev scored mean (3.093), and the virgin's format (10 teams,
split groups) differs from every dev season. No level adjustment
is made — the gates are frozen and the virgin is read once.

## Outputs
Engine `engine/goals/`; `results_dev.json` (+ CSV);
`results_virgin.json`; `fitted_params_virgin.json`; on PASS,
`predictions/g_in_virgin_predictions.csv` (1H/2H presentation via
frozen goals constant 0.4387). Verdict `reports/G_IN_VERDICT.md`.
