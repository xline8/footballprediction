# Pre-registration — G-MD (MD-NationalDivision goals model)

Frozen: 2026-11-10, before any fitting. Design authority:
`analysis/MODEL_DESIGN.md` (G-MD); features X1 (goals-only fallback —
no xG exists in this feed: no `expected_goals*` key in any of 556
payloads, no shotmap), X2 KEPT (EDA F4); evidence F1/F2/F3/F4/F6.
Reference pattern: programme Dixon-Coles (FI G analogue, BY G port).
Documented port: the FI/BY reference `dc.py` / `arms.py` are carried
over verbatim (iterative sweep optimiser, 14 sweeps, damping 0.7,
+0.25 smoothing, home init 0.28, MAXG = 10, production tau, rho grid
(0.0, −0.05, −0.10, −0.15) by goals log-likelihood, decay HL = 270
days); the harness is adapted from the same line with the naive
trailing-10 baseline added per the IL precedent. The ONLY reference
divergence: the observation is goals-only in every match (the X1
blend's documented fallback), because the Moldova feed carries no
xG in any season.

Phases: all rows are ordinary rows (phase flag `main` /
`championship` carried, never filtered) per the frozen phase rule in
`analysis/DATA_UNDERSTANDING.md`. The 10 awarded matches (9 in
2021/2022, 1 in 2024/2025) are kept as ordinary rows with
awarded=true; the header score is used, never the event-derived
score (there are 0 score-vs-event mismatches in the corpus anyway).

## Arms
1. **Gate Zero** — the unmodified reference above. A team with no
   fitted rating (absent from the training seasons) is predicted at
   league mean (attack/defence exponents 0.0).
2. **SHRINK** — Gate Zero plus the sanctioned G-J2-lesson change: at
   prediction time a team with n < 6 prior in-league matches has a *=
   n/6, d *= n/6 (counts from the training data only). Expected to be
   numerically inert under season-blocked prediction in this league
   (any team present in a prior season has ≥14 prior matches; teams
   with no fitted rating sit at league mean with exponents 0.0) —
   same observation as CH, NO, FR and BY. It is run and reported
   anyway; the gate decides.
3. **X2** — SHRINK plus the entrant offset (FI pattern): a club whose
   previous completed season was NOT in this league (entrant,
   identified in-corpus by absence from the previous season — MD is
   tier 1, entrants are promoted clubs; no tier-2 corpus is built
   in-system) enters with its lambdas tilted — its scoring lambda
   multiplied by exp(g), its conceded lambda by exp(c), where (g, c)
   are the mean (GF diff, GA diff) of all entrant transitions
   completed BEFORE the predicted season, measured in the MD corpus
   itself (each entrant's first-season GF/GA per match minus that
   season's league team mean); if fewer than 3 completed transitions
   exist, the offset is 0. Multipliers clamped to [0.8, 1.25]. The
   tilt applies only in the entrant's first season in the league.
   EDA F4 (the frozen evidence, computed on the full dev era): only
   3 dev transitions, mean GF −0.363 / GA +0.780, GF negative 3/3,
   GA positive 2/3 — the direction matches the programme pattern
   and both raw means exceed the clamp, so the full-dev realisation
   is g_log −0.223 / c_log +0.223 (log 0.8 / log 1.25); the rule
   itself, not the realised numbers, is what is frozen — the harness
   recomputes (g, c) from completed transitions only, strictly
   before each predicted season. Recorded expectation: on the dev
   scored window X2 is numerically identical to SHRINK (2022/2023
   entrant: 0 prior transitions; 2023/2024 entrants: 1 prior
   transition < 3 → offset 0; 2024/2025: no entrants). It can only
   differ on the virgin season, if the virgin is ever read.

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
(pooled n = 258), season-blocked (expanding fit strictly before each
season's first match). Metrics: 1X2 LL, RPS, OU2.5 LL per season and
pooled, for all three arms and both baselines. The dev harness must
not read 2025/2026 or 2026/2027 rows.

## Virgin protocol
Virgin = 2025/2026 (n = 114, complete season), read ONCE, only for
dev-passing arms. Fit expands to all matches ≤ 2024/2025.
Calibration: mean predicted − actual for home-win rate and OU2.5
over-rate, SE = sd(p_i − y_i)/√n.

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
if none passes, G-MD verdict is FAIL and nothing ships.
Mechanical reading: an arm passes iff it survives the dev gate AND
passes virgin legs (i)–(ii) (PROVISIONAL counts) AND, for a variant,
leg (iii); Gate Zero is exempt from (iii). Ties → simpler arm (Gate
Zero before SHRINK before X2). If Gate Zero fails its dev gate,
variants are moot, verdict FAIL, virgin NOT read.

## Evaluation lines (frozen, EDA F6)
Primary: 1X2 and OU 2.5 (dev scored over-rates 1.5: 0.7481, 2.5:
0.4884, 3.5: 0.2829; n = 258). Home win rate 0.4574, draw rate
0.2403 in the same window. Dev scored mean team goals 1.3411/match
(692 goals / 258 matches / 2). Halves presentation via the
frozen goals constant 0.4388 only (config.yaml); no halves constant
exists for any count market. Predictions-only: no MD
odds/settlement source in-system.

## Known calibration risk (recorded, not adjusted)
Trait reliability is strong (split-half r 0.885 / 0.877) and
season-to-season team-mean correlations are positive, so the
expanding fit has real signal to track — but the dev era contains a
deep level dip: 2022/2023 scored 2.128 goals/match against 2.953 /
2.965 in the two following dev seasons and 3.063 in the warm-up,
and the dev scored pool (n=258) is small, so pooled metrics carry
wide season-level variance. Virgin-season goals/match (2.947,
inventory only) sits near the last two dev seasons. No level
adjustment is made — the gates are frozen and the virgin is read
once.

## Outputs
Engine `engine/goals/`; `results_dev.json` (+ CSV);
`results_virgin.json`; `fitted_params_virgin.json`; on PASS,
`predictions/g_md_virgin_predictions.csv` (1H/2H presentation via
frozen goals constant 0.4388). Verdict `reports/G_MD_VERDICT.md`.
