# Phase 3.5 — Features: Tanzania Premier League

The causality contract is the J1 template: only matches strictly before a target may contribute; trailing windows are fixed; missing values remain missing; no target-match payload content is used as a covariate.

## 1 X1–X9

- **X1 ADOPTED — goals-only observation.** Goals are present for all 1,284 rows and the payload contains no xG. The Dixon–Coles fit therefore uses official score goals only.
- **X2 DROPPED.** No built Tanzanian sibling/parent league supplies a mover prior. The documented name turnover is descriptive only; the SHRINK arm in MODEL_DESIGN is the thin-data treatment. Rename footnote: Fountain Gate FC and Singida Black Stars are not merged with their former names.
- **X3 DROPPED.** Set-play xG is absent in 0/1,284 payloads.
- **X4 DROPPED.** Shotmap shots and xG are absent in 0/1,284.
- **X5 DROPPED.** SOT, corners and yellow-card targets are absent; stats are non-empty in 0/1,284 and plain Yellow events are 0.
- **X6 DROPPED.** xGOT/per-shot data are absent in 0/1,284.
- **X7 DROPPED.** Opponent-box touches are absent with stats empty in 0/1,284.
- **X8 DROPPED.** Referee text is non-empty in 0/1,284; there is also no yellow target.
- **X9 DROPPED.** Corners are not buildable and territorial stats are absent in 0/1,284.

## 2 Architectural components

Ratings, home advantage, Dixon–Coles rho, time decay, score-matrix probabilities and the half-share constant are architectural or presentation components, not covariates. SHRINK is a pre-registered thin-data arm. The frozen pooled 1H goals share is 0.4867818118.

## 3 Rejected list

R1 team first-half shares: rejected as a feature; excess variance is −.001605 and split-half r=.168. R2 trailing finishing, R3 conversion, R4 on-target rate and R5 xGOT: no xG/shot target exists. R6 lineup/absence: only 10 blocks, zero starters. R7 top-shooter concentration and R8 formation/coach: no usable player/lineup data. R9 standings/h2h/form: post-match snapshots and leakage. R10 attendance: not a pre-match feature. R11 first-goal/game-state: in-match. R12 reds: 114 dismissals (Red 99, YellowRed 15, plain Yellow 0), rare and rejected as target/covariate. R13 momentum: in-match. R14 AW/withdrawal indicator: excluded rows cannot contribute to a feature.

## 4 Consumption map

G-TZ consumes X1. Gate Zero and SHRINK consume no extra covariates. S/C/K/T have no candidate because their targets are absent.
