# Pre-registration — G-KW (KW-PremierLeague goals model)

Frozen: 2026-11-10, before any fitting. Design authority:
`analysis/MODEL_DESIGN.md` (G-KW); features X1 (goals-only fallback —
no xG exists in this feed: no `expected_goals*` key in any of 711
payloads, no shotmap), X2 KEPT (EDA F4); evidence F1/F2/F3/F4/F6.
Reference pattern: programme Dixon-Coles (FI G analogue, BY port).
Documented port: the reference `dc.py` is carried over verbatim
(iterative sweep optimiser, 14 sweeps, damping 0.7, +0.25 smoothing,
home init 0.28, MAXG = 10, production tau, rho grid (0.0, −0.05,
−0.10, −0.15) by goals log-likelihood, decay HL = 270 days); the
harness is adapted from the BY `harness.py` with the naive
trailing-10 baseline (IL precedent). Two documented divergences,
both forced by this league's data: (1) the observation is goals-only
in every match (the X1 blend's documented fallback — no xG in any
season); (2) seasons are split-season labels, not integers, so the
entrant-offset rule and the walk-forward use the frozen canonical
season order (2021 < 2021/2022 < 2022/2023 < 2023/2024 < 2024/2025 <
2025/2026 < 2026/2027) in place of BY's integer-year arithmetic —
the rule itself is unchanged.

Season canonicalisation (frozen, PREPROCESSING decision 1): the
"2021" label (calendar season, Jan–May 2021) and the "2021/2022"
label (split season, Nov 2021–Apr 2022) are DISTINCT seasons —
disjoint match ids and dates. No deduplication. Only played matches
are in the corpus (642 of 711 index rows; 69 unplayed fixtures with
placeholder index scores are excluded, PREPROCESSING decision 2).

Phases: all rows are ordinary rows (phase flags main / championship
/ relegation carried, never filtered) per the frozen phase rule in
`analysis/DATA_UNDERSTANDING.md`. The one awarded match (4067510,
2022/2023) is kept as an ordinary row with awarded=true; the header
score is used.

## Arms
1. **Gate Zero** — the unmodified reference above. A team with no
   fitted rating (absent from the training seasons) is predicted at
   league mean (attack/defence exponents 0.0).
2. **SHRINK** — Gate Zero plus the sanctioned G-J2-lesson change: at
   prediction time a team with n < 6 prior in-league matches has a *=
   n/6, d *= n/6 (counts from the training data only, reference
   `arms.py` mechanics). Expected to be numerically inert under
   season-blocked prediction in this league (any team present in a
   prior season has ≥14 prior matches; teams with no fitted rating
   sit at league mean with exponents 0.0) — same observation as BY.
   It is run and reported anyway; the gate decides.
3. **X2** — SHRINK plus the entrant offset (FI pattern): a club whose
   previous completed season (in the canonical season order) was NOT
   in the Kuwait Premier League (entrant, identified in-corpus by
   absence from the previous season — KW is tier 1, entrants are
   promoted clubs; no tier-2 corpus is built in-system) enters with
   its lambdas tilted — its scoring lambda multiplied by exp(g), its
   conceded lambda by exp(c), where (g, c) are the mean (GF diff, GA
   diff) of all entrant transitions completed BEFORE the predicted
   season, measured in the KW corpus itself (each entrant's
   first-season GF/GA per match minus that season's league team
   mean); if fewer than 3 completed transitions exist, the offset is
   0. Multipliers clamped to [0.8, 1.25]. The tilt applies only in
   the entrant's first Premier League season. EDA F4 (the frozen
   evidence, computed on the full dev era): 8 dev transitions, mean
   GF −0.390 / GA +0.404, GF negative 7/8, GA positive 5/8 — the
   adopt decision of FI (8 transitions) and BY (8 transitions). The
   full-dev realisation of the rule clamps at g_log −0.2231 / c_log
   +0.2231 (log 0.8 / log 1.25); the rule itself, not the realised
   numbers, is what is frozen — the harness recomputes (g, c) from
   completed transitions only, strictly before each predicted season.

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
Training seed (warm-up) 2021; evaluation seasons 2021/2022,
2022/2023, 2023/2024, 2024/2025 (pooled n = 422), season-blocked
(expanding fit strictly before each season's first match). Metrics:
1X2 LL, RPS, OU2.5 LL per season and pooled, for all three arms and
both baselines. The dev harness must not read 2025/2026 or
2026/2027 rows.

## Virgin protocol
Virgin = 2025/2026 (n = 111, complete season), read ONCE, only for
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
in at least half the dev seasons, i.e. ≥ 2 of 4) for the both-pass
rule. Both-pass rule: if Gate Zero and a variant both pass all legs,
the lower pooled virgin 1X2 LL ships; if only one passes, it ships;
if none passes, G-KW verdict is FAIL and nothing ships.
Mechanical reading: an arm passes iff it survives the dev gate AND
passes virgin legs (i)–(ii) (PROVISIONAL counts) AND, for a variant,
leg (iii); Gate Zero is exempt from (iii). Ties → simpler arm (Gate
Zero before SHRINK before X2). If Gate Zero fails its dev gate,
variants are moot, verdict FAIL, virgin NOT read.

## Evaluation lines (frozen, EDA F6)
Primary: 1X2 and OU 2.5 (dev scored over-rates 1.5: 0.8152, 2.5:
0.5877, 3.5: 0.3863; n = 422). Home win rate 0.4265, draw rate
0.2370 in the same window. Dev scored mean team goals 1.5640/match
(1,320 goals / 422 matches / 2). Halves presentation via the
frozen goals constant 0.4411 only (config.yaml; thin base —
2024/2025 event matches only, EDA F3); no halves constant exists
for any count market. Predictions-only: no KW odds/settlement
source in-system.

## Known calibration risk (recorded, not adjusted)
Trait reliability is strong (split-half r 0.786 / 0.922) and
season-to-season team-mean correlations are mostly moderate to
strong, so the expanding fit has real signal to track — but the
scored seasons have uneven played counts (69 / 120 / 122 / 111)
because the early seasons carry many unplayed fixtures, and the
2021/2022→2022/2023 season-to-season GF correlation is weak (0.17).
Virgin-season level is inventory only and is not cited here as a
decision input. No level adjustment is made — the gates are frozen
and the virgin is read once.

## Outputs
Engine `engine/goals/`; `results_dev.json` (+ CSV);
`results_virgin.json`; `fitted_params_virgin.json`; on PASS,
`predictions/g_kw_virgin_predictions.csv` (1H/2H presentation via
frozen goals constant 0.4411). Verdict `reports/G_KW_VERDICT.md`.
