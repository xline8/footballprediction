# Pre-registration — G-MY (Malaysia Liga Super goals)

Frozen: 2026-11-10. Branch `build/my-ligasuper`. Design authority: `analysis/MODEL_DESIGN.md`; feature authority: `analysis/FEATURES.md`; measured facts: `analysis/eda_summary.json` and `inventory_summary.json`. This preregistration is frozen before any fitting.

## Frozen EDA facts

The corpus has 793 index rows and 792 model rows after excluding awarded match 4480811. Warm-up 2021 has 132 model matches. The expanding dev seasons are 2022 (132), 2023 (182), and 2024/2025 (155), pooled n=469. Virgin primary is complete 2025/2026 (156); 2026/2027 has 35 partial reserve matches and remains untouched.

Dev pooled levels are goals/match 3.1663, home goals 1.7399, away goals 1.4264, HW .4520, D .2026, AW .3454, OU1.5 .8081, OU2.5 .5885, OU3.5 .3859, and BTTS .5032. Chronological split-half reliability on the scored window is GF r=.8381 and GA r=.7715 over 39 team-seasons; the 2021–2024/2025 era values are .8269 and .7303 over 51 team-seasons. All model seasons through 2025/2026 give GF .8494 and GA .7107 over 64 team-seasons.

The frozen halves constant is `goals_1h_share=0.4534`, from 1125/2481 goals over 759 usable eventful model matches. On 756 matches with goals, observed share variance is .097829 versus binomial noise .105540, ratio .926946, implied true variance 0.000000. It is presentation-only.

SHRINK expectations `(n_0, n_1_to_5, n_6_to_29, n_30_plus)` are `(2,0,10,0)` for 2022, `(4,0,2,8)` for 2023, and `(0,0,3,10)` for 2024/2025. The n=1–5 bucket does not occur in dev.

## Reference architecture and arms

All arms use direct Poisson log-likelihood maximisation, scipy L-BFGS, sum-to-zero attack/defence, ridge 1e-3, rho grid `(0.0, -0.05, -0.10, -0.15)`, MAXG=10, standard Dixon-Coles tau correction, fitted home intercept initialized at 0.25, and frozen 270-day decay. The fit for a target season uses model matches strictly before that season's first match date.

1. Gate Zero: entrants at league mean.
2. SHRINK: at prediction time, a team with fewer than six prior in-league matches has both attack and defence exponents multiplied by `n/6`; n is counted strictly before the predicted season and n=0 uses the league-mean fallback.

There is no X2 mover arm because no sibling Malaysian league exists.

## Baselines and protocol

Climatology is pooled training outcome rates plus the pooled training OU2.5 rate. Naive trailing-10 uses each team's mean goals scored in its last 10 prior in-league matches, fewer when necessary, and the training league mean if none exist; it uses an 11x11 independent Poisson matrix with MAXG=10.

Dev is season-blocked and expanding: warm-up 2021, then score 2022, 2023, and 2024/2025. Report 1X2 log loss, RPS, and OU2.5 log loss per season and pooled for both arms and both baselines. The virgin fit expands through 2024/2025 and reads 2025/2026 once, only for dev-passing arms.

## GATE LEGS

Dev gate: pooled dev 1X2 LL and RPS must beat climatology and naive trailing-10, and OU2.5 LL must beat both; otherwise the arm is dead.

Virgin legs are: (i) LL: arm virgin 1X2 LL <= Gate Zero's AND <= climatology's; (ii) calibration: `|mean predicted - actual| <= 1.0pp` pooled for home-win rate and OU2.5 over-rate, with SE = `sd(p_i - y_i)/sqrt(n)` reported; a breach within 1 SE of the boundary is PROVISIONAL PASS and beyond it FAIL; (iii) per-season sign check on dev: arm LL <= Gate Zero LL in at least half the dev seasons for the both-pass rule, with Gate Zero exempt. Ties go to the simpler arm.

Frozen rule: if Gate Zero fails dev, variants are moot, verdict FAIL, and virgin is NOT read. If both arms pass, ship the lower pooled virgin 1X2 LL; if only one passes, ship it; if none passes, ship nothing. Halves are presentation-only via 0.4534 on PASS.

This preregistration creates no engine, fitted parameters, predictions, results, verdict, or shipping outcome.
