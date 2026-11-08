# Phase 3.5 — IR Persian Gulf Pro League features

The causality contract is strict: a target match may use only prior
kickoff observations; windows are trailing; ratios are ratios of
sums; missing windows are NaN and deactivate their arm. No feature
is allowed unless it is listed here. The J1 template (X1–X9) is
replicated below with an ADOPTED/DROPPED verdict per feature.

## Accepted features and verdicts

- **X1 blend observation pair — DROPPED.** No xG key or shotmap
  exists in any season (EDA F7). The goals-only fallback is
  documented and is the only admissible goals observation.
- **X2 mover prior — ADOPTED in frozen-offset form (as the X2
  arm, not as a rating input).** Entrants arrive from the
  Azadegan League (FotMob 9372), and the dev transitions support
  a small flat offset: pooled GF gap −0.160, GA gap +0.157 over
  the three dev transitions (EDA F4, n = 6 teams / 180
  team-matches). The arm gives teams with zero training-window
  matches the frozen ratings a0 = −0.18, d0 = +0.15 (the
  log-scale images of those gaps at the pooled dev team-mean
  μ = 0.996; derivation in MODEL_DESIGN.md). The **rating-based
  variant is REJECTED**: it would need each entrant's Azadegan
  rating, and the sibling goals model failed its dev gate and
  shipped no fitted ratings — there is no cross-league scaling
  to freeze from 6 teams on a failed model. Gate Zero and SHRINK
  keep entrants at the league mean.
- **X3 set-play xG — DROPPED.** No xG.
- **X4 xG/shot — DROPPED.** No xG and no shotmap.
- **X5 trailing target means — DROPPED for this league.** The only
  target with coverage is goals, and the goals reference (DC) does
  not consume a trailing-mean feature; there is no SOT/corners/
  cards/total-shots target to trail. The goals-for/against trait
  reliability (F2: GF r = 0.37/0.45, GA r = 0.52/0.40) is carried
  by the DC ratings themselves, not by a trailing-mean covariate.
- **X6 xGOT — DROPPED.** No shotmap.
- **X7 touches_opp_box — DROPPED.** No stats feed.
- **X8 referee — DROPPED.** Referee text is `""` in all 960
  dev-season matches; a name exists in only 43 recent matches
  (14 in the virgin season, 29 in the transitional one). There is
  no referee identity to learn from on dev data, and no cards
  candidate for it to serve.
- **X9 possession/big-chance corners covariates — DROPPED.** No
  stats feed and no corners candidate.

## Frozen halves constant

Goals 1H share **0.427** (ratio of sums over all seasons, EDA F3).
True variance −0.0036 (at/below the binomial noise floor) and team
split-half r = +0.087: a frozen league constant for reporting,
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
| R6 | lineup/absence features | lineups exist only in 2025/2026+ (outside the dev window); no reliability check run |
| R7 | top-shooter concentration | no dedicated reliability check |
| R8 | formation/coach | no reliability check; no lineups in dev seasons |
| R9 | standings, H2H, teamForm snapshots | post-match leakage |
| R10 | attendance | not pre-match in payload |
| R11 | first-goal/game-state traits | in-match facts |
| R12 | red-card target/covariate | rare event (0.10–0.24/match), split-half r = 0.19, early seasons under-captured (F6) |
| R13 | momentum | not pre-match |
| R14 | yellow-card target | yellows exist only in the virgin + transitional seasons (feed break, F6); no dev window |
| R15 | Azadegan-rating mover prior | sibling goals model failed its dev gate, shipped no ratings; no scaling estimable from 6 teams |

## Consumption map

Goals uses Gate Zero goals-only DC, SHRINK, and X2 (frozen offset)
only. No other candidate exists: SOT, corners, and total shots are
NOT buildable (no target data in the corpus, and the virgin window
contains no target for them either); cards is NOT buildable (the
only yellow coverage is the virgin window itself). Nothing else is
consumed.
