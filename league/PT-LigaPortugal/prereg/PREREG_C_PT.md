# Pre-registration — C-PT (Liga Portugal corners model)

Frozen: 2026-11-09, before any fitting. Branch `build/pt-liga`.
Design authority: `league/PT-LigaPortugal/analysis/MODEL_DESIGN.md`
(C-PT) + FEATURES.md. Reference: production `model_corners_v3.py` pattern as implemented for C-J1 (decay-weighted base rates + rolling-5 shots relative factors + NB total + territorial multiplier).

Shared engine = the C-J1 engine pattern, copied: matches in
chronological order, all state strictly pre-date; base rates
HL 270 (bh, ba, L = mean total shots per team); relative factors
from each team's last 5 prior matches (shots for/against, clamp
[0.6, 1.7]); core mu_cs = bh*(fhp*fac)**gamma + ba*(fap*fhc)**gamma;
NB pmf on 0..50, size k = mu/(r-1) for r > 1.02 else Poisson limit.
Per target season, gamma (grid 0.0..0.8), r (moment at chosen
gamma, clamp [1.02, 5.0]) and the arm's betas are fitted ONLY on
walk-forward rows from seasons strictly before S (within-season
rows use pre-date state), then frozen for S. Territorial
multiplier: per team over its last 10 prior matches, covariate
active if >=8 of the 10 carry the stat for both teams; match
multiplier applies only if active for both teams;
mult = clamp(exp(beta . dz), 0.70, 1.43); betas chosen by grid
search minimising mean binary LL@9.5 on the training rows (ties:
smallest sum |beta|, then lexicographic).

## Arms

1. **Gate Zero (X9)** — covariates possession (pp) and big
   chances: beta_poss in {-0.010..0.010 step 0.0025}, beta_bc in
   {-0.10..0.10 step 0.025}, joint grid.
2. **Arm X7** — covariates replaced by opp-box touches (feature
   X7, EDA r=0.88/0.74): beta_bt in {-0.04..0.04 step 0.01}.

## Protocols

Dev = expanding season-blocked walk-forward: for target season S,
fit on all matches of seasons strictly before S; evaluation seasons
2022/2023, 2023/2024, 2024/2025, 2025/2026 (pooled n=1,224). The dev
harness must not read 2026/2027 rows at all. Virgin = 2026/2027
(n=98, TRANSITIONAL — season in progress; confirmatory read at
season end reserved), read ONCE after dev results are frozen, and
only for arms that pass the dev gate. Calibration: mean predicted
P(over primary line) - actual over rate; SE = sd(pred_i - y_i)/sqrt(n).
Halves in outputs are presentation only via the frozen PT constants
(goals 0.443, SOT 0.449, corners 0.471, yellows 0.331, shots 0.456).
Primary line: **9.5**. Metrics per arm/baseline, per season and
pooled: n, mean binary LL at the primary line (plus the two
neighbouring half-lines), mean P(over primary), actual over rate.

Baselines: (1) league base rate — one NB per target season, mu =
decay-weighted (HL 270) mean total over matches before the season,
r by the moment ratio over the same window; (2) naive trailing-10 —
per match, mu from the two teams' trailing-10 for/against means
(strictly pre-match, date-grouped; a team with <6 prior matches
contributes the league per-team mean), NB size from the same
per-season r as baseline 1.

## GATE LEGS (verbatim, frozen)

Dev gate — pooled dev LL at the primary line beats BOTH baselines
(league base rate; naive trailing-10), else the arm is dead and does
NOT read the virgin. Virgin legs — (i) LL at the primary line
<= Gate Zero's and <= best baseline's; (ii) calibration
|mean P(over) - actual over rate| <= 1.0pp clean PASS, breach within
1 SE = PROVISIONAL PASS, beyond = FAIL; (iii) dev per-season sign
check (arm LL <= Gate Zero in >= half the dev seasons) for the
both-pass rule. Both-pass: both pass -> lower pooled virgin LL
ships; one -> ships; none -> FAIL. Gate Zero is exempt from (iii).
A tie in virgin LL goes to Gate Zero.

## Outputs

Engine `league/PT-LigaPortugal/engine/corners/`; results_dev.json
(+CSV), results_virgin.json, fitted_params_virgin.json; virgin
predictions for the shipped arm (Gate Zero's if none ships,
labelled in the verdict) under `league/PT-LigaPortugal/predictions/`
with FT over-probabilities for the ladder around the primary line
and 1H/2H ladders via the frozen PT constant for this market;
verdict `league/PT-LigaPortugal/reports/C_PT_VERDICT.md`.
Production code untouched. No push, no merge.
