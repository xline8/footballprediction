# Pre-registration — G-HN (Honduras Liga Nacional goals model)

Frozen: 2026-11-10, before any fitting. Branch `build/hn-liga-nacional`.
Design authority: `league/HN-LigaNacional/analysis/MODEL_DESIGN.md`;
features and leakage boundary: `analysis/FEATURES.md`; evidence:
`analysis/DATA_UNDERSTANDING.md`, `analysis/PREPROCESSING.md`, and
`analysis/EDA.md`.

## Reference architecture

All arms share the Dixon–Coles goals-only architecture: 14
multiplicative sweeps, damping 0.7, +0.25 smoothing, fitted home
advantage initialized at 0.28, attack/defence initialized at zero,
score matrix `MAXG=10`, production `tau` correction, and rho
selected from `(0, -0.05, -0.10, -0.15)` by weighted goals log
likelihood. Time decay is `0.5 ** (age_days / 270)`. A target-
tournament fit uses all eligible regular-phase matches strictly
before that tournament's first kickoff. Unseen teams start at the
league mean.

There is no xG anywhere in 1,132 finished matches, so the
goals-only fallback is used for 100% of observations. No xG blend
is authorized.

## Arms

1. **Gate Zero** — the unmodified reference architecture.
2. **SHRINK** — Gate Zero plus one prediction-time change: teams
   with fewer than six prior in-league matches have fitted
   attack/defence ratings scaled toward league mean by n/6; n=0
   remains the unseen-team default.

No X2 mover arm exists. Honduras has no sibling tier or other
warehouse league, so there is no mover evidence from which to
freeze an offset.

No count-market fit is authorized. SOT, corners, and total shots
have zero observations; cards have no yellow-card target and only
unvalidated Red/YellowRed event coverage.

## Development protocol

Seed tournaments: 2021/2022 - Apertura + Clausura (regular only,
n=180). Evaluate expanding, tournament-blocked fits on 2022/2023 -
Apertura, 2022/2023 - Clausura, 2023/2024 - Apertura, 2023/2024 -
Clausura, 2024/2025 - Apertura, and 2024/2025 - Clausura, pooled
n=540. The dev harness must not read 2025/2026 or 2026/2027 rows.
Metrics are mean 1X2 log loss, mean RPS (home/draw/away), and
OU2.5 log loss. Baselines are target-tournament prior-tournament
pooled climatology for 1X2 and the prior-tournament OU2.5 rate,
plus the naive trailing-10 baseline reported alongside.

## Virgin protocol

Virgin primary is the complete 2025/2026 season (Apertura +
Clausura, regular only, n=220). It is read once and only for arms
passing the dev gate. The fit uses matches before the first
2025/2026 Apertura kickoff; climatology uses pooled 2021/2022 -
Apertura through 2024/2025 - Clausura rates. 2026/2027 - Apertura,
n=84 at the frozen pull and in progress, is reserved confirmatory
data and is not read in this build.

Calibration is defined as **actual − predicted** everywhere in
this build.

## Frozen gate legs

Dev gate per arm: pooled 1X2 LL and RPS must beat climatology,
and OU2.5 LL must beat the base-rate baseline. If no arm passes,
virgin data is not read.

Virgin legs: (i) arm 1X2 LL is <= Gate Zero and <= climatology;
(ii) calibration absolute breach is <=1 percentage point clean,
<=1 standard error provisional, otherwise FAIL, for home-win and
OU2.5 rates; (iii) a variant's dev per-tournament LL is no worse
than Gate Zero in at least half of dev tournaments. Both-pass
rule: if Gate Zero and SHRINK pass, ship the lower pooled virgin
1X2 LL; if only one passes, ship it; if neither passes, G-HN is
FAIL and nothing ships. Ties go to Gate Zero. Gate Zero is exempt
from the variant sign check. If Gate Zero fails its own dev gate,
variants are moot, verdict FAIL, virgin NOT read.

## Halves presentation

On PASS, virgin predictions present FT + 1H/2H via the frozen
goals constant 0.4572 (EDA §3): 1H λ = 0.4572 × FT λ,
2H λ = 0.5428 × FT λ; 1H OU lines 0.5/1.5/2.5, 2H OU lines
1.5/2.5/3.5, same rho and score-matrix machinery. Halves are
presentation only, never fitted.

## Outputs

The later fitting phase may write `engine/goals/`,
`results_dev.json` and CSV, `results_virgin.json`,
`fitted_params_virgin.json`, PASS-only predictions under
`league/HN-LigaNacional/predictions/`, and
`reports/G_HN_VERDICT.md`. Predictions are FT + 1H/2H via the
frozen constant above. Phase A writes none of these model outputs
because fitting is explicitly prohibited.
