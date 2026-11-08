# Pre-registration — G-MK (North Macedonia Prva Liga goals)

Frozen: 2026-11-10. Branch `build/mk-prva-liga`. Design authority: `analysis/MODEL_DESIGN.md`; feature authority: `analysis/FEATURES.md`; measured facts: `analysis/eda_summary.json` and `inventory_summary.json`. This preregistration is frozen before any fitting.

## Frozen EDA facts

The dev scored window is 2022/2023–2024/2025, n=549 model matches. Warm-up 2021/2022 has 198 model matches. Virgin 2025/2026 has 197 model matches after one awarded match. The 2026/2027 partial reserve has 65 model matches and is untouched.

Dev pooled levels are goals/match 2.3552, home goals 1.3679, away goals 0.9872, HW .4663, D .2842, AW .2495, OU1.5 .6630, OU2.5 .4171, OU3.5 .2386, and BTTS .4517. Chronological split-half reliability on the scored window is GF r=.6093 and GA r=.5135 over 35 team-seasons; the dev-era values are GF .6351 and GA .5482 over 47 team-seasons. The frozen halves constant is goals_1h_share=.4323, from 559/1,293 goals over 492 matches; observed variance .119702 versus binomial noise .125050, ratio .9572, implied true SD 0.0000.

The virgin goals level is 3.0863 per match, versus 2.3226 in 2024/2025. This is a recorded virgin level test. It does not smooth the data or change a gate.

## Reference architecture and arms

All arms use direct Poisson log-likelihood maximisation, scipy L-BFGS, sum-to-zero attack/defence, ridge 1e-3, rho grid (0.0, -0.05, -0.10, -0.15), MAXG=10, standard Dixon-Coles tau correction, fitted home intercept initialized at 0.25, and frozen 270-day decay. Fit observations are goals only. The fit for a target season uses matches strictly before that season’s first match date.

1. Gate Zero: entrants start at league mean.
2. SHRINK: at prediction time a team with n < 6 prior in-league matches has a *= n/6, d *= n/6, where n is matches played in the training data strictly before the predicted season; n >= 6 means no change; n = 0 means exponents 0.0. This applies home and away.
3. NO ENTRANT: no X2 mover offset, because the North Macedonia index contains only FotMob league id 249. It is a design exclusion, not a post-fit rescue arm.

The SHRINK expectation is mechanically n_1_to_5=0 in every scored target season. The n=0 entrant counts are 2, 3, and 1 for 2022/2023, 2023/2024, and 2024/2025; all incumbents have at least 30 prior matches (9, 9, and 11 respectively). SHRINK is therefore expected to equal Gate Zero here.

## Baselines and protocol

Climatology is the pooled training outcome rate and OU2.5 rate. Naive trailing-10 uses each team’s mean goals scored in its last 10 prior league matches, fewer when necessary, and the training league mean if none exist; it uses an 11x11 independent Poisson matrix with MAXG=10.

Dev is season-blocked and expanding: warm-up 2021/2022, then score 2022/2023, 2023/2024, and 2024/2025. Report 1X2 log loss, RPS, and OU2.5 log loss per season and pooled for each arm and both baselines. The virgin fit expands through 2024/2025 and reads 2025/2026 once, only for arms that pass dev. Report virgin 1X2 LL and calibration errors for home-win and OU2.5 rates with SE = sd(p_i-y_i)/sqrt(n).

## GATE LEGS

Dev gate — pooled dev 1X2 LL and RPS of an arm must beat climatology AND naive trailing-10, and OU2.5 LL must beat both baselines, else the arm is dead. Virgin legs — (i) LL leg: arm's virgin 1X2 LL <= Gate Zero's AND <= climatology's; (ii) calibration leg: |mean predicted − actual| <= 1.0pp pooled for home-win rate and for OU2.5 over-rate, SEs reported; a breach within 1 SE of the boundary is recorded PROVISIONAL PASS, beyond it FAIL; (iii) per-season sign check on dev (arm LL <= Gate Zero LL in at least half the dev seasons) for the both-pass rule.

Mechanical reading: an arm passes iff it survives the dev gate AND passes virgin legs (i)–(ii) (PROVISIONAL counts) AND, for variants, leg (iii); Gate Zero is exempt from (iii). Ties go to the simpler arm. If Gate Zero fails dev, variants are moot, verdict FAIL, and virgin is NOT read. If both pass, ship lower pooled virgin 1X2 LL; if only one passes, ship it; if none passes, ship nothing. Halves are presentation-only via .4323 on PASS.

## Outputs

The later fitting phase, if authorized, writes the G-MK engine/results and a verdict. This Phase A preregistration does not create engine code, fitted parameters, predictions, or a shipping outcome.
