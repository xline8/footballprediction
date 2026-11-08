# Phase 3.5 — NL Eerste Divisie features

The causality contract is strict: a target match may use only prior kickoff observations; windows are trailing; ratios are ratios of sums; missing windows are NaN and deactivate their arm. No feature is allowed unless it is listed here.

## Accepted features and verdicts

- **X1 blend observation pair — DROPPED.** No xG key or shotmap exists. The goals-only fallback is documented and is the only admissible goals observation.
- **X2 mover prior — ADOPTED (relegated-club prior).** Coordinator-verified against the Eredivisie corpus (id 57): every entrant in every observed transition is a club relegated from the Eredivisie; no Tweede Divisie club entered. Pooled match-weighted first-season gaps over the four complete transitions (n=456 entrant team-matches): GF +0.419, GA -0.199 vs the league team-goal mean. Relegated clubs enter stronger — the mirror image of NL-Eredivisie's X2. Applied as log-ratio shifts frozen in the prereg; gated like every arm.
- **X3 set-play xG — DROPPED.** No xG.
- **X4 xG/shot — DROPPED.** No xG and essentially no shotmap.
- **X5 trailing target means — ADOPTED.** SOT, corners, event-unified yellows, and total shots have usable target coverage. Use strict trailing-10 means with the minimum prior-observation rule.
- **X6 xGOT — DROPPED.** No shotmap.
- **X7 touches_opp_box — ADOPTED as a gated corners covariate.** Coverage is 72.1%, 77.6%, 85.3%, 100%, 100%, 100% by season; pooled split-half r is 0.875 for and 0.918 against. Earlier sparse coverage still requires the inactive-arm rule.
- **X8 referee — ADOPTED as a gated cards arm (coordinator correction).** Coverage 87.35% overall and 95.8-100% in the scored dev seasons (47.4% only in the 2021/2022 warm-up); strictness split-half r=0.420 over 32 referees with >=20 matches. Program precedent adopts X8 at weaker readings (BE r=0.378, USL r=0.378, KR r=0.362) under exactly this coverage shape. The appointment-availability caveat is handled the standard way: a fixture with no named referee in the warehouse falls back to Gate Zero — no imputation, ever.
- **X9 possession/big-chance corners covariates — ADOPTED for Gate Zero.** Possession reliability is r=0.910 for/against and big-chance reliability is r=0.669/0.750. These are the reference territorial covariates; X7 is the gated extension.

## Frozen halves constants

Measured shares are goals from events across all seasons and the other markets from the 2023/2024+ period-split era. Goals/SOT/corners/total shots/yellows 1H shares are **0.451 / 0.451 / 0.462 / 0.451 / 0.326**. The JSON records observed variance, binomial noise floor, true variance, and team split-half r. Coordinator-recomputed true variances (per-match binomial noise) are at/below zero for goals/SOT/corners/shots and small-positive (+0.014) for yellows only, with team split-half r low throughout; these are frozen league constants, never team features.

## Rejected list

| # | rejected item | reason |
|---|---|---|
| R1 | team first-half shares | low team split-half reliability; constants only |
| R2 | trailing finishing (goals minus xG) | xG unavailable |
| R3 | trailing conversion | outcome-contaminated and no xG/shot support |
| R4 | standalone SOT/shots | not needed beyond target architecture; no shotmap quality support |
| R5 | defensive xGOT | no shotmap |
| R6 | lineup/absence features | no Phase-1 reliability check; not eligible |
| R7 | top-shooter concentration | no dedicated reliability check |
| R8 | formation/coach | no reliability check |
| R9 | standings, H2H, teamForm snapshots | post-match leakage |
| R10 | attendance | not pre-match in payload |
| R11 | first-goal/game-state traits | in-match facts |
| R12 | red-card target/covariate | rare event and no reliability evidence |
| R13 | momentum | not pre-match |

## Consumption map

Goals use Gate Zero goals-only DC, SHRINK, and X2 only because X2 is adopted. SOT uses Gate Zero plus RS ratio-shrink; corners uses Gate Zero X9 plus X7; cards uses Gate Zero plus the X8 referee arm; total shots uses the three specified reference arms. No xG-derived arm exists.
