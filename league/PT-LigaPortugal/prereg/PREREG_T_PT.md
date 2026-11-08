# Pre-registration — T-PT (Liga Portugal total_shots model)

Frozen: 2026-11-09, before any fitting. Branch `build/pt-liga`.
Design authority: `league/PT-LigaPortugal/analysis/MODEL_DESIGN.md`
(T-PT) + FEATURES.md. Reference: the shots v1 pattern as in T-J1 arm A (team shots ratings + NB + naive ensemble); the E9 mechanism (trailing-window NB r) as the variant, per MODEL_DESIGN. Built under the same user order as T-J1; the top-5 prospective trial is untouched.

Shared engine (season-blocked, decay HL 270): league per-team
shots mean L; per team decay-weighted shots for/against shrunk
toward L with prior K=8 match-equivalents; expected team shots =
L * (for/L) * (opp_against/L); total mu = sum. Final P(over) =
0.5 * P_model + 0.5 * P_naive (v1 ensemble; naive = baseline 2).
The arms differ ONLY in the NB size r.

## Arms

1. **Gate Zero (arm A)** — r = moment estimate over the whole
   training window, clamped to [1.02, 200].
2. **Arm E9** — r = moment estimate over the trailing 200 league
   matches strictly before the target season, clamped likewise.

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
Primary line: **24.5**. Metrics per arm/baseline, per season and
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

Engine `league/PT-LigaPortugal/engine/total_shots/`; results_dev.json
(+CSV), results_virgin.json, fitted_params_virgin.json; virgin
predictions for the shipped arm (Gate Zero's if none ships,
labelled in the verdict) under `league/PT-LigaPortugal/predictions/`
with FT over-probabilities for the ladder around the primary line
and 1H/2H ladders via the frozen PT constant for this market;
verdict `league/PT-LigaPortugal/reports/T_PT_VERDICT.md`.
Production code untouched. No push, no merge.
