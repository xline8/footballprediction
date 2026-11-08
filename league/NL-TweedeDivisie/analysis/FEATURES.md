# Phase 3.5 — NL Tweede Divisie features

The causality contract is strict: a target match may use only prior
kickoff observations; windows are trailing; ratios are ratios of
sums; missing windows are NaN and deactivate their arm. No feature
is allowed unless it is listed here.

## Accepted features and verdicts

- **X1 blend observation pair — DROPPED.** No xG key or shotmap
  exists in any season. The goals-only fallback is documented and is
  the only admissible goals observation.
- **X2 mover prior — ADOPTED (below-tier entrant prior, gated).**
  Entrants come from below (Derde Divisie / reserve sides); none
  came from the Eerste Divisie in any observed transition. Pooled
  over the three dev transitions only (n = 256 entrant
  team-matches; the virgin transition is excluded so no virgin
  outcome sets the parameter): GF gap −0.093, GA gap +0.181 vs the
  league team-goal mean. Direction matches the below-tier
  expectation on both sides; magnitudes are small and
  per-transition signs flip (EDA F4). Applied as log-ratio shifts
  frozen in the prereg; gated like every arm.
- **X3 set-play xG — DROPPED.** No xG.
- **X4 xG/shot — DROPPED.** No xG and no shotmap.
- **X5 trailing target means — DROPPED for this league.** The only
  target with coverage is goals, and the goals reference (DC) does
  not consume a trailing-mean feature; there is no SOT/corners/
  cards/total-shots target to trail. The goals-for/against trait
  reliability (F2: r = 0.747/0.714) is carried by the DC ratings
  themselves, not by a trailing-mean covariate.
- **X6 xGOT — DROPPED.** No shotmap.
- **X7 touches_opp_box — DROPPED.** No stats feed.
- **X8 referee — DROPPED.** Referee text is blank in all 1,638
  matches; no referee identity exists.
- **X9 possession/big-chance corners covariates — DROPPED.** No
  stats feed and no corners candidate.

## Frozen halves constant

Goals 1H share **0.436** (ratio of sums over all seasons, EDA F3).
True variance −0.0054 (at/below the binomial noise floor) and team
split-half r = −0.13: a frozen league constant for reporting,
never a team feature. No other market has a halves constant (no
data).

## Rejected list

| # | rejected item | reason |
|---|---|---|
| R1 | team first-half shares (goals) | true variance ≤ 0; constants only (F3) |
| R2 | trailing finishing (goals minus xG) | xG unavailable |
| R3 | trailing conversion | outcome-contaminated and no xG/shot support |
| R4 | standalone SOT/shots | no target, no shotmap |
| R5 | defensive xGOT | no shotmap |
| R6 | lineup/absence features | no lineups in any payload |
| R7 | top-shooter concentration | no dedicated reliability check |
| R8 | formation/coach | no reliability check; no lineups |
| R9 | standings, H2H, teamForm snapshots | post-match leakage |
| R10 | attendance | not pre-match in payload |
| R11 | first-goal/game-state traits | in-match facts |
| R12 | red-card target/covariate | rare event (0.145/match), split-half r = −0.09 (F6) |
| R13 | momentum | not pre-match |
| R14 | yellow-card target | yellows do not exist in this corpus (0 events, F6) |
| R15 | Jong-specific adjustment | no reliability contrast (F5: 0.67/0.60 vs 0.75/0.73); descriptive only |

## Consumption map

Goals uses Gate Zero goals-only DC, SHRINK, and X2 only. No other
candidate exists: SOT, corners, cards, and total shots are NOT
buildable (no target data in the corpus, and the virgin window
contains no target for them either). Nothing else is consumed.
