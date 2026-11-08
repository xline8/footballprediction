# Phase 3.5 — IR Azadegan League features

The causality contract is strict: a target match may use only prior
kickoff observations; windows are trailing; ratios are ratios of
sums; missing windows are NaN and deactivate their arm. No feature
is allowed unless it is listed here. The J1 template (X1–X9) is
replicated below with an ADOPTED/DROPPED verdict per feature.

## Accepted features and verdicts

- **X1 blend observation pair — DROPPED.** No xG key or shotmap
  exists in any season (EDA F7). The goals-only fallback is
  documented and is the only admissible goals observation.
- **X2 mover prior — DROPPED.** Two independent reasons, either of
  which suffices. (a) Scope: the build brief states no
  parent/sibling tier exists for an X2 newcomer prior and forbids
  inventing one. (b) Evidence: pooled over the three dev
  transitions, entrants perform at the league mean (EDA F4: GF gap
  +0.002, GA gap −0.034, n = 18 teams / 600 team-matches) — there
  is no prior to fit even from within-league data. Flag recorded
  in DATA_UNDERSTANDING.md §4: the warehouse index does contain
  the Persian Gulf Pro League (id 523, 1,245 rows); it was not
  used, and any future X2 amendment would need a fresh prereg and
  a coordinator decision.
- **X3 set-play xG — DROPPED.** No xG.
- **X4 xG/shot — DROPPED.** No xG and no shotmap.
- **X5 trailing target means — DROPPED for this league.** The only
  target with coverage is goals, and the goals reference (DC) does
  not consume a trailing-mean feature; there is no SOT/corners/
  cards/total-shots target to trail. The goals-for/against trait
  reliability (F2: GF r = 0.27/0.38, GA r = 0.51/0.53) is carried
  by the DC ratings themselves, not by a trailing-mean covariate.
- **X6 xGOT — DROPPED.** No shotmap.
- **X7 touches_opp_box — DROPPED.** No stats feed.
- **X8 referee — DROPPED.** Referee text is blank in all 1,564
  matches; no referee identity exists.
- **X9 possession/big-chance corners covariates — DROPPED.** No
  stats feed and no corners candidate.

## Frozen halves constant

Goals 1H share **0.415** (ratio of sums over all seasons, EDA F3).
True variance −0.00411 (at/below the binomial noise floor) and team
split-half r = −0.083: a frozen league constant for reporting,
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
| R12 | red-card target/covariate | rare event (0.085/match), split-half r = 0.07 (F6) |
| R13 | momentum | not pre-match |
| R14 | yellow-card target | yellows do not exist in this corpus (0 events, F6) |
| R15 | reserve-side (B-team) adjustment | Foolad Khuzestan B is the only B side (2026/2027, 4 matches so far); no reliability evidence |

## Consumption map

Goals uses Gate Zero goals-only DC and SHRINK only. No other
candidate exists: SOT, corners, cards, and total shots are NOT
buildable (no target data in the corpus, and the virgin window
contains no target for them either). Nothing else is consumed.
