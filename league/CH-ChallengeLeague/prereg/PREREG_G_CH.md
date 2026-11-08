# Pre-registration — G-CH (CH-ChallengeLeague goals model)

Frozen: 2026-11-10, before any fitting. Design authority:
`analysis/MODEL_DESIGN.md` (G-CH); features X1 (goals-only fallback — no
xG exists in this feed), X5; evidence F1/F2/F4. X2 entrant offset
DROPPED pre-fitting on EDA F4 (7 transitions, GF −0.079 / GA −0.035,
no systematic tilt).
Reference pattern: programme Dixon-Coles (FI G analogue). Documented
port divergence: ratings fitted by direct Poisson log-likelihood
maximisation (scipy L-BFGS, sum-to-zero identification, ridge 1e-3)
instead of the production sweep optimiser; rho selected from the grid
(0.0, −0.05, −0.10, −0.15) by training log-likelihood at the fitted
ratings; MAXG = 10; tau = standard Dixon-Coles low-score correction.
All rows are ordinary rows (single quadruple-round-robin phase).

## Arms
1. **Gate Zero** — the reference above, unmodified.
2. **SHRINK** — Gate Zero plus: at prediction time a team with n < 6
   prior in-league matches has its attack/defence exponents scaled by
   n/6 (toward league mean).

## Dev protocol
Training seed 2021/2022; evaluation seasons 2022/2023–2024/2025
(pooled n = 540), season-blocked (expanding fit strictly before each
season's first match). Metrics: 1X2 LL, RPS, OU2.5 LL per season and
pooled. Baseline: climatology (prior-seasons pooled outcome rates +
OU2.5 over-rate). The dev harness must not read 2025/2026 rows.

## Virgin protocol
Virgin = 2025/2026 (n = 181, complete season), read ONCE, only for
dev-passing arms. Fit expands to all matches ≤ 2024/2025.
Calibration: mean predicted − actual for home-win rate and OU2.5
over-rate, SE = sd(p_i − y_i)/√n.

## GATE LEGS (verbatim, frozen)
Dev gate — pooled dev 1X2 LL and RPS of an arm must beat climatology, and OU2.5 LL must beat the base-rate baseline, else the arm is dead. Virgin legs — (i) LL leg: arm's virgin 1X2 LL ≤ Gate Zero's AND ≤ climatology's; (ii) calibration leg: |mean predicted − actual| ≤ 1.0pp pooled for home-win rate and for OU2.5 over-rate, SEs reported; a breach within 1 SE of the boundary is recorded PROVISIONAL PASS, beyond it FAIL; (iii) per-season sign check on dev (arm LL ≤ Gate Zero LL in at least half the dev seasons) for the both-pass rule. Both-pass rule: if Gate Zero and a variant both pass all legs, the lower pooled virgin 1X2 LL ships; if only one passes, it ships; if none passes, G-CH verdict is FAIL and nothing ships.
Mechanical reading: an arm passes iff it survives the dev gate AND passes virgin legs (i)–(ii) (PROVISIONAL counts) AND, for variants, leg (iii); Gate Zero is exempt from (iii). Ties → simpler arm (Gate Zero before SHRINK). If Gate Zero fails its dev gate, variants are moot, verdict FAIL, virgin NOT read.

## Outputs
Engine `engine/goals/`; `results_dev.json` (+ CSV); `results_virgin.json`;
`fitted_params_virgin.json`; on PASS, `predictions/g_ch_virgin_predictions.csv`
(1H/2H presentation via frozen goals constant 0.4409). Verdict `reports/G_CH_VERDICT.md`.
