# Pre-registration — G-PT3 (Portugal Liga 3 goals model)

Frozen: 2026-11-10, before any fitting. Branch `build/pt-liga3`.
Design authority: `league/PT-Liga3/analysis/MODEL_DESIGN.md`;
features and leakage boundary: `analysis/FEATURES.md`; evidence:
`analysis/DATA_UNDERSTANDING.md`, `analysis/PREPROCESSING.md`, and
`analysis/EDA.md`.

## Reference architecture

All arms share the following Dixon–Coles goals-only architecture: 14
multiplicative sweeps, damping 0.7, +0.25 smoothing, fitted home advantage
initialized at 0.28, attack/defence initialized at zero, score matrix
`MAXG=10`, production `tau` correction, and rho selected from
`(0, -0.05, -0.10, -0.15)` by weighted goals log likelihood. Time decay is
`0.5 ** (age_days / 270)`. A target-season fit uses all matches strictly
before that season's first kickoff. Unseen teams start at the league mean.

The source contains no xG in 1,647 finished matches, so the goals-only
fallback is used for 100% of observations. There is no xG blend in this
preregistration.

## Arms

1. **Gate Zero** — the unmodified reference architecture.
2. **SHRINK** — Gate Zero plus one prediction-time change: a team with fewer
   than six prior in-league matches has its fitted attack and defence ratings
   scaled toward league mean by `n/6`; n=0 remains the unseen-team default.

No X2 mover arm exists. Direct Liga Portugal ↔ Liga 3 movers are 0 in every
transition; Liga 3 ↔ Liga Portugal 2 counts are only 1–3 clubs per direction
per transition (2/2, 2/3, 2/2, 1/2, 2/2) and their descriptive GF/GA changes
are not stable enough to freeze an offset.

Count-market candidates are not preregistered in this phase. SOT, corners,
and total shots have 0 observations in all 1,647 finished matches (stats is
`None` everywhere; shotmap shots total 0); cards have no stats-yellow source
and the event-card feed is unstable (Card events in 95, 118, 79, 119, and 290
matches in 2021/22 through 2025/26; plain Yellow events 0, 0, 2, 303, and
1,207 — the pre-2025/26 feed records dismissals only). No count-market fit is
authorized.

## Development protocol

Seed season: 2021/2022 (n=332 finished). Evaluate expanding, season-blocked
fits on 2022/2023, 2023/2024, and 2024/2025, pooled n=929. The dev harness
must not read 2025/2026 or 2026/2027 rows. Metrics are mean 1X2 log loss,
mean RPS (home/draw/away), and OU2.5 log loss. Baselines are target-season
prior-season pooled climatology for 1X2 and the prior-season OU2.5 rate.

## Virgin protocol

Virgin primary: the complete 2025/2026 season, n=296. It is read once and
only for arms passing the dev gate. The fit uses matches before the first
2025/2026 kickoff; climatology uses pooled 2021/2022–2024/2025 rates.
2026/2027, n=90 at the frozen pull, is reserved confirmatory data and is not
read in this build.

## Frozen gate legs

Dev gate (per arm): pooled 1X2 LL and RPS must beat climatology, and OU2.5 LL
must beat the base-rate baseline. If no arm passes, the virgin is not read.

Virgin legs: (i) the arm's 1X2 LL is <= Gate Zero and <= climatology; (ii)
calibration absolute breach is <=1 percentage point clean, <=1 standard
error provisional, otherwise FAIL, for home-win and OU2.5 rates; (iii) a
variant's dev per-season LL must be no worse than Gate Zero in at least half
of the dev seasons. Both-pass rule: if Gate Zero and a variant pass, ship the
lower pooled virgin 1X2 LL; if only one passes, ship it; if neither passes,
G-PT3 is FAIL and nothing ships. Ties go to Gate Zero. Gate Zero is exempt
from the variant sign check.

## Outputs

Engine: `league/PT-Liga3/engine/goals/`.

Dev results: `engine/goals/results_dev.json` (and CSV). Virgin results:
`engine/goals/results_virgin.json`; fitted virgin parameters:
`engine/goals/fitted_params_virgin.json`; predictions on PASS:
`league/PT-Liga3/predictions/g_pt3_virgin_predictions.csv`.
Verdict: `league/PT-Liga3/reports/G_PT3_VERDICT.md`.
Predictions are FT-only; no halves presentation columns are authorized by
this phase because no halves constant was frozen.
