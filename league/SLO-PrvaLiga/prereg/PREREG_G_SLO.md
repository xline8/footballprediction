# Pre-registration — G-SLO (Slovenia Prva Liga goals)

Frozen: 2026-11-10. Branch `build/slo-prva-liga`. Design authority: `analysis/MODEL_DESIGN.md`; feature authority: `analysis/FEATURES.md`; measured facts: `analysis/eda_summary.json` and `inventory_summary.json`. This preregistration is frozen before any fitting.

## Frozen EDA facts

The dev scored window is 2022/2023–2024/2025, n=538 model matches. Warm-up 2021/2022 has 180 model matches. Virgin 2025/2026 has 161 model matches after one awarded match. The 2026/2027 partial reserve has 74 model matches and is untouched.

Dev pooled levels are goals/match 2.7026, home goals 1.4368, away goals 1.2658, HW .4033, D .2714, AW .3253, OU1.5 .7565, OU2.5 .4870, OU3.5 .2900, and BTTS .5297. Chronological split-half reliability on the scored window is GF r=.6302 and GA r=.4756 over 30 team-seasons; the dev-era values are GF .6053 and GA .4049 over 40 team-seasons. The 20-seed random-split means are GF .6056 and GA .5521.

The frozen halves constant is goals_1h_share=.4498, from 654/1,454 goals over 506 usable model matches; observed variance .108422 versus binomial noise .115791, ratio .936361, implied true SD 0.0000. The official virgin level test is 500/162=3.0864; the model-only level is 497/161=3.0870. Neither changes a gate or fit.

## Reference architecture and arms

All arms use direct Poisson log-likelihood maximisation, scipy L-BFGS, sum-to-zero attack/defence, ridge 1e-3, rho grid (0.0, -0.05, -0.10, -0.15), MAXG=10, standard Dixon-Coles tau correction, fitted home intercept initialized at 0.25, and frozen 270-day decay. Fit observations are goals only. The fit for a target season uses matches strictly before that season’s first match date.

1. Gate Zero: entrants start at league mean.
2. SHRINK: at prediction time a team with n < 6 prior in-league matches has a *= n/6 and d *= n/6; n is counted strictly before the predicted season; n=0 means exponents 0.0.
3. NO ENTRANT: no X2 mover offset, because the complete Slovenia index contains only league id 173.

SHRINK expectations `(n_0, n_1_to_5, n_6_to_29, n_30_plus)` are `(1,0,0,9)`, `(1,0,0,9)`, and `(2,0,0,8)` for the three dev target seasons.

## Baselines and protocol

Climatology is pooled training outcome rates and OU2.5 rate. Naive trailing-10 uses each team’s mean goals scored in its last 10 prior league matches, fewer when necessary, and the training league mean if none exist; it uses an 11x11 independent Poisson matrix with MAXG=10.

Dev is season-blocked and expanding: warm-up 2021/2022, then score 2022/2023, 2023/2024, and 2024/2025. Report 1X2 LL, RPS, and OU2.5 LL per season and pooled for each arm and baseline. The virgin fit expands through 2024/2025 and reads 2025/2026 once, only for dev-passing arms.

## GATE LEGS

Dev gate: pooled dev 1X2 LL and RPS must beat climatology and naive trailing-10, and OU2.5 LL must beat both; otherwise the arm is dead. Virgin legs are (i) LL leg: the arm's virgin 1X2 LL <= Gate Zero's AND <= climatology's; (ii) calibration `|mean predicted − actual| <= 1.0pp` pooled for the home-win rate and for the OU2.5 over-rate, SEs reported with SE = sd(p_i − y_i)/sqrt(n); a breach within 1 SE of the boundary is recorded PROVISIONAL PASS, beyond it FAIL; and (iii) per-season sign check on dev (arm LL <= Gate Zero LL in at least half the dev seasons) for the both-pass rule. Gate Zero is exempt from (iii). Ties go to the simpler arm.

If Gate Zero fails dev, variants are moot, verdict FAIL, and virgin is NOT read. If both arms pass, ship lower pooled virgin 1X2 LL; if only one passes, ship it; if none passes, ship nothing. Halves are presentation-only via .4498 on PASS.

This preregistration creates no engine, fitted parameters, predictions, results, verdict, or shipping outcome.
