# Pre-registration — K-PT (Liga Portugal cards model)

Frozen: 2026-11-09, before any fitting. Branch `build/pt-liga`.
Design authority: `league/PT-LigaPortugal/analysis/MODEL_DESIGN.md`
(K-PT) + FEATURES.md. Reference: production `model_cards.py` pattern (decay-weighted shrunk team yellow rates + NB total; referee not used in production).

Shared engine (season-blocked, decay HL 270): league mean
yellows per team-match mu_L over the training window; per team,
decay-weighted yellows for/against shrunk toward mu_L with prior
K=8 match-equivalents: rate_for = (sum w*y_for + 8*mu_L)/(sum w + 8),
likewise against. mu_home_yellows = mu_L * (for_home/mu_L) *
(against_away/mu_L); total mu = home + away (no home/away split of
the league mean — the cards pattern's league state is venue-free).
NB size r: moment estimate on the training window clamped to
[1.02, 200]. No ensemble (production cards has none).

## Arms

1. **Gate Zero** — the engine above, unmodified.
2. **Arm X8** — total mu multiplied by the appointed referee's
   shrunk yellow rate / league yellow rate: ref_rate =
   (ref_yellows + 8*mu_match)/(ref_matches + 8) over the referee's
   prior in-league matches (strictly before the target season for
   the season fit — the multiplier is a per-season constant per
   referee computed from the training window, because the engine
   is season-blocked; stated here so there is no ambiguity),
   multiplier clamped to [0.75, 1.33]. Referee blank or <8 prior
   matches -> shrunk rate with the matches available (the
   shrinkage formula itself is the fallback; a referee with 0
   prior matches gets exactly mu_match, multiplier 1.0). EDA
   reliability for X8 in this league is weak (r=0.28) — recorded.
   Operational note: warehouse records are post-match snapshots;
   pre-match referee publication cannot be proven from them; the
   no-referee fallback above is the operating rule.

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
Primary line: **4.5**. Metrics per arm/baseline, per season and
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

Engine `league/PT-LigaPortugal/engine/cards/`; results_dev.json
(+CSV), results_virgin.json, fitted_params_virgin.json; virgin
predictions for the shipped arm (Gate Zero's if none ships,
labelled in the verdict) under `league/PT-LigaPortugal/predictions/`
with FT over-probabilities for the ladder around the primary line
and 1H/2H ladders via the frozen PT constant for this market;
verdict `league/PT-LigaPortugal/reports/K_PT_VERDICT.md`.
Production code untouched. No push, no merge.
