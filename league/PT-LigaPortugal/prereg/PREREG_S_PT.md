# Pre-registration — S-PT (Liga Portugal sot model)

Frozen: 2026-11-09, before any fitting. Branch `build/pt-liga`.
Design authority: `league/PT-LigaPortugal/analysis/MODEL_DESIGN.md`
(S-PT) + FEATURES.md. Reference: production `model_sot.py` v5 (joint shots ratings + Beta-Binomial on-target ratio + NB, ensembled 50/50 with naive trailing-10).

Shared engine (season-blocked: state fitted on all matches of
seasons strictly before the target season, decay HL 365 days,
0.5**((cutoff-date).days/365)): per team, decay-weighted shots
for/against means shrunk toward the league per-team mean with
prior K=8 match-equivalents; expected team shots
Venue splits are not used: for/against are overall (this
venue-free simplification of the v5 ratings is part of the frozen
design). Expected shots for home =
L * (F_home/L) * (A_away/L) and symmetrically for away, where L =
league per-team shots mean, F = shrunk shots-for, A = shrunk
shots-against-conceded. On-target ratio per team: shrunk with the
v5 Beta-Binomial prior — ratio = (SOT + 200*league_ratio) /
(shots + 200). Team SOT mu = expected shots * ratio. Total mu =
sum of team mus. NB size r: moment estimate on the training
window, r = mu_bar/(var/mu_bar - 1) clamped to [1.02, 200].
Final P(over line) = 0.5 * P_model + 0.5 * P_naive, where the
naive component is baseline 2 below (the v5 ensemble).

## Arms

1. **Gate Zero** — the engine above, unmodified.
2. **Arm X4** — each team's ratio is multiplied by
   (team xG-per-shot / league xG-per-shot)**0.5, clamped to
   [0.80, 1.25], where xG-per-shot is a ratio of sums over the
   training window (feature X4, EDA r=0.63).
3. **Arm X6** — same tilt with attacking xGOT-per-shot (stats-feed
   expected_goals_on_target sums / shots), computed ONLY from
   2024/2025+ matches (era guard); a team with <8 era matches gets
   tilt 1.0. For target seasons whose training window contains no
   era matches the arm is identical to Gate Zero by construction
   and is reported as such.

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
Primary line: **8.5**. Metrics per arm/baseline, per season and
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

Engine `league/PT-LigaPortugal/engine/sot/`; results_dev.json
(+CSV), results_virgin.json, fitted_params_virgin.json; virgin
predictions for the shipped arm (Gate Zero's if none ships,
labelled in the verdict) under `league/PT-LigaPortugal/predictions/`
with FT over-probabilities for the ladder around the primary line
and 1H/2H ladders via the frozen PT constant for this market;
verdict `league/PT-LigaPortugal/reports/S_PT_VERDICT.md`.
Production code untouched. No push, no merge.
