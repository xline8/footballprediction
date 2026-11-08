# Pre-registration — G-BY (BY-PremierLeague goals model)

Frozen: 2026-11-10, before any fitting. Design authority:
`analysis/MODEL_DESIGN.md` (G-BY); features X1 (goals-only fallback —
no xG exists in this feed: no `expected_goals*` key in any of 1,394
payloads, no shotmap), X2 KEPT (EDA F4); evidence F1/F2/F3/F4/F6.
Reference pattern: programme Dixon-Coles (FI G analogue, IL G port).
Documented port: the FI reference `dc.py` / `arms.py` are carried over
verbatim (iterative sweep optimiser, 14 sweeps, damping 0.7, +0.25
smoothing, home init 0.28, MAXG = 10, production tau, rho grid (0.0,
−0.05, −0.10, −0.15) by goals log-likelihood, decay HL = 270 days);
the harness is adapted from the FI `harness.py` with the naive
trailing-10 baseline added per the IL precedent. The ONLY reference
divergence: the observation is goals-only in every match (the X1
blend's documented fallback), because the Belarus Premier League feed
carries no xG in any season.

Phases: all rows are ordinary rows (phase flag `main` carried, never
filtered) per the frozen phase rule in
`analysis/DATA_UNDERSTANDING.md`. The 17 awarded matches (15 in 2021,
all involving Sputnik Rechitsa's mid-season withdrawal; 1 in 2022;
1 in 2023) are kept as ordinary rows with awarded=true; the header
score is used, never the event-derived score.

## Arms
1. **Gate Zero** — the unmodified reference above. A team with no
   fitted rating (absent from the training seasons) is predicted at
   league mean (attack/defence exponents 0.0).
2. **SHRINK** — Gate Zero plus the sanctioned G-J2-lesson change: at
   prediction time a team with n < 6 prior in-league matches has a *=
   n/6, d *= n/6 (counts from the training data only, FI `arms.py`
   mechanics). Expected to be numerically inert under season-blocked
   prediction in this league (any team present in a prior season has
   ≥28 prior matches; teams with no fitted rating sit at league mean
   with exponents 0.0) — same observation as CH, NO and FR. It is run
   and reported anyway; the gate decides.
3. **X2** — SHRINK plus the entrant offset (FI pattern): a club whose
   previous completed season was NOT in the Belarus Premier League
   (entrant, identified in-corpus by absence from the previous season
   — BY is tier 1, entrants are promoted clubs; no tier-2 corpus is
   built in-system) enters with its lambdas tilted — its scoring
   lambda multiplied by exp(g), its conceded lambda by exp(c), where
   (g, c) are the mean (GF diff, GA diff) of all entrant transitions
   completed BEFORE the predicted season, measured in the BY corpus
   itself (each entrant's first-season GF/GA per match minus that
   season's league team mean); if fewer than 3 completed transitions
   exist, the offset is 0. Multipliers clamped to [0.8, 1.25]. The
   tilt applies only in the entrant's first Premier League season.
   EDA F4 (the frozen evidence, computed on the full dev era): 8 dev
   transitions, mean GF −0.325 / GA +0.426, signs consistent (GF
   negative 8/8, GA positive 7/8) — the largest entrant tilt in the
   programme so far, and the same adopt decision as FI (8 transitions,
   −0.210 / +0.159). The full-dev realisation of the rule clamps at
   g_log −0.223 / c_log +0.223 (log 0.8 / log 1.25); the rule itself,
   not the realised numbers, is what is frozen — the harness recomputes
   (g, c) from completed transitions only, strictly before each
   predicted season.

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
Training seed 2021; evaluation seasons 2022–2024 (pooled n = 690),
season-blocked (expanding fit strictly before each season's first
match). Metrics: 1X2 LL, RPS, OU2.5 LL per season and pooled, for all
three arms and both baselines. The dev harness must not read 2025
or 2026 rows.

## Virgin protocol
Virgin = 2025 (n = 240, complete season), read ONCE, only for
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
(iii) per-season sign check on dev (variant 1X2 LL ≤ Gate Zero 1X2 LL
in at least half the dev seasons, i.e. ≥ 2 of 3) for the both-pass
rule. Both-pass rule: if Gate Zero and a variant both pass all legs,
the lower pooled virgin 1X2 LL ships; if only one passes, it ships;
if none passes, G-BY verdict is FAIL and nothing ships.
Mechanical reading: an arm passes iff it survives the dev gate AND
passes virgin legs (i)–(ii) (PROVISIONAL counts) AND, for a variant,
leg (iii); Gate Zero is exempt from (iii). Ties → simpler arm (Gate
Zero before SHRINK before X2). If Gate Zero fails its dev gate,
variants are moot, verdict FAIL, virgin NOT read.

## Evaluation lines (frozen, EDA F6)
Primary: 1X2 and OU 2.5 (dev scored over-rates 1.5: 0.700, 2.5:
0.4551, 3.5: 0.2638; n = 690). Home win rate 0.3971, draw rate
0.2638 in the same window. Dev scored mean team goals 1.2667/match
(1,748 goals / 690 matches / 2). Halves presentation via the
frozen goals constant 0.4314 only (config.yaml); no halves constant
exists for any count market. Predictions-only: no BY
odds/settlement source in-system.

## Known calibration risk (recorded, not adjusted)
Trait reliability is strong (split-half r 0.855 / 0.947) and
season-to-season team-mean correlations are moderate and positive,
so the expanding fit has real signal to track — but 2024 was the
lowest-scoring dev season (2.346/match) while 2023 was the highest
(2.738/match), so the level can swing ~0.4 goals/match between
seasons; the dev gate will judge that as frozen. Virgin-season
goals/match (2.546, inventory only) sits +0.01 above the dev scored
mean (2.533). No level adjustment is made — the gates are frozen
and the virgin is read once.

## Outputs
Engine `engine/goals/`; `results_dev.json` (+ CSV);
`results_virgin.json`; `fitted_params_virgin.json`; on PASS,
`predictions/g_by_virgin_predictions.csv` (1H/2H presentation via
frozen goals constant 0.4314). Verdict `reports/G_BY_VERDICT.md`.
