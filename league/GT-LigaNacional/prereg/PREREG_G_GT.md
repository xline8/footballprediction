# Pre-registration — G-GT (Guatemala Liga Nacional goals model)

Frozen: 2026-11-10, before any fitting. Branch `build/gt-liga-nacional`.
Design authority: `league/GT-LigaNacional/analysis/MODEL_DESIGN.md`;
features and leakage boundary: `analysis/FEATURES.md`; evidence:
`analysis/DATA_UNDERSTANDING.md`, `analysis/PREPROCESSING.md`, and
`analysis/EDA.md`.

## Reference architecture

All arms share the Dixon–Coles goals-only architecture: 14 multiplicative
sweeps, damping 0.7, +0.25 smoothing, fitted home advantage initialized at
0.28, attack/defence initialized at zero, score matrix `MAXG=10`, production
`tau` correction, and rho selected from `(0, -0.05, -0.10, -0.15)` by weighted
goals log likelihood. Time decay is `0.5 ** (age_days / 270)`. A target-season
fit uses all matches strictly before that season's first kickoff. Unseen teams
start at the league mean.

There are no xG shots in 1,443 finished matches, so the goals-only fallback is
used for 100% of observations. No xG blend is authorized.

## Arms

1. **Gate Zero** — the unmodified reference architecture.
2. **SHRINK** — Gate Zero plus one prediction-time change: teams with fewer
   than six prior in-league matches have fitted attack/defence ratings scaled
   toward league mean by n/6; n=0 remains the unseen-team default.

No X2 mover arm exists. Guatemala has no sibling tier or other warehouse
league, so there is no mover evidence from which to freeze an offset.

No count-market fit is authorized. SOT, corners, and total shots have zero
observations; cards have no yellow-card target and only unstable
Red/YellowRed event coverage.

## Development protocol

Seed season: 2021/2022 (n=292). Evaluate expanding, season-blocked fits on
2022/2023, 2023/2024, and 2024/2025, pooled n=746. The dev harness must not
read 2025/2026 or 2026/2027 rows. Metrics are mean 1X2 log loss, mean RPS
(home/draw/away), and OU2.5 log loss. Baselines are target-season
prior-season pooled climatology for 1X2 and the prior-season OU2.5 rate.

## Virgin protocol

Virgin primary is the complete 2025/2026 season, n=292. It is read once and
only for arms passing the dev gate. The fit uses matches before the first
2025/2026 kickoff; climatology uses pooled 2021/2022–2024/2025 rates.
2026/2027, n=113 at the frozen pull, is reserved confirmatory data and is not
read in this build.

## Frozen gate legs

Dev gate per arm: pooled 1X2 LL and RPS must beat climatology, and OU2.5 LL
must beat the base-rate baseline. If no arm passes, virgin data is not read.

Virgin legs: (i) arm 1X2 LL is <= Gate Zero and <= climatology; (ii)
calibration absolute breach is <=1 percentage point clean, <=1 standard error
provisional, otherwise FAIL, for home-win and OU2.5 rates; (iii) a variant's
dev per-season LL is no worse than Gate Zero in at least half of dev seasons.
Both-pass rule: if Gate Zero and SHRINK pass, ship the lower pooled virgin 1X2
LL; if only one passes, ship it; if neither passes, G-GT is FAIL and nothing
ships. Ties go to Gate Zero. Gate Zero is exempt from the variant sign check.

## Outputs

The later fitting phase may write `engine/goals/`, `results_dev.json` and CSV,
`results_virgin.json`, `fitted_params_virgin.json`, PASS-only predictions under
`league/GT-LigaNacional/predictions/`, and `reports/G_GT_VERDICT.md`.
Predictions are FT-only with no halves columns. Phase A writes none of these
model outputs because fitting is explicitly prohibited.
