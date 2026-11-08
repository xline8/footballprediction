# Phase 3.5 — Features

Team identity is always the FotMob id. Features are pre-match only; match
snapshots, game-state facts, and post-match information are excluded.

## X1–X9 decision table

| feature | decision | reason / reliability |
|---|---|---|
| X1 goals-only observation | ADOPTED | Goals exist in all seasons. xG is DROPPED: no usable stats or shotmap in 810/810. |
| X2 mover tier offset | DROPPED | No 1. deild feeder tier exists in the warehouse; no mover prior source. |
| X3 set-play xG | DROPPED | No xG. |
| X4 xG per shot | DROPPED | No shotmap. |
| X5 trailing target-rate means | ADOPTED | Trailing-10 unified yellows from events; naive baseline and harness component. Goals retain naive/climatology context. Trait reliability: yellows-for r=0.869, against r=0.851. |
| X6 xGOT | DROPPED | No shotmap. |
| X7 box touches | DROPPED | No stats. |
| X8 referee | DROPPED | Referee text is empty in 810/810. |
| X9 corners covariates | DROPPED | No stats. |

## Halves constants

Half-specific team features are not adopted. Presentation-only constants are
frozen at goals first-half share **0.441** and unified-yellows first-half
share **0.348**. They are league constants, not fitted team tendencies.

## Rejected list

| id | rejected item | reason |
|---|---|---|
| R1 | per-team first-half shares | NOISE: observed variance 0.1005, binomial expectation 0.0994, true variance about 0.0011. |
| R2/R3 | finishing / conversion | No xG; not measurable. |
| R4 | on-target rate | No shots data. |
| R5 | defensive xGOT | No shotmap. |
| R6 | lineup / absence | CLOSED by program rule and V10; lineups present but not used. |
| R9 | standings / h2h | LEAKAGE: post-match snapshots. |
| R10 | attendance | NOT PRE-MATCH. |
| R11 | game-state traits | NOT PRE-MATCH. |
| R12 | reds as target | Rare event: 74 straight reds, 0.09 per match; excluded by program rule. |
| R13 | momentum | NOT PRE-MATCH. |

