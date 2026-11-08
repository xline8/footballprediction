# Phase 5 — Features

The feature decisions below are tied to `eda_summary.json`; no feature is
introduced from an in-sample pattern alone.

## 1. Template decisions

- **X1 — goals-only observations: ADOPTED.** Goals exist on all 3,874 group
  rows; xG is absent everywhere, so the xG fallback never binds.
- **X2 — newcomer / cross-tier prior: ADOPTED conditionally.** F4 gives a
  pooled entrant GF gap −0.087 and GA gap +0.036 for 2022–2025, with LP and
  below-tier subsets recorded. It is a pre-registered gated arm.
- **X3 — set-play decomposition: DROPPED.** Zero stats payloads; no xG or
  set-play observations exist.
- **X4 — xG-per-shot quality: DROPPED.** Zero shotmap shots and zero xG.
- **X5 — trailing means: ADOPTED.** Trailing team goal means are available
  for G-BNAC; trailing yellow means are available only in the 2023+ event era
  for K-BNAC.
- **X6 — xGOT / finishing: DROPPED.** Zero shotmap and xG observations.
- **X7 — territorial proxy: DROPPED.** No stats keys, including box touches,
  possession, or big chances.
- **X8 — referee strictness: ADOPTED conditionally.** From 2023+ and ≥8
  referee matches, split-half r=0.525 and range 2.765–6.429. It is a gated
  cards variant; missing assignments use the Gate-Zero fallback.
- **X9 — stats-feed attacking covariates: DROPPED.** No stats block exists.

## 2. Halves

Halves are presentation only. Use frozen ratio-of-sums constants: goals 1H
share 0.435381 and yellows 1H share 0.390091. There is no half-specific model
or team half tendency.

## 3. Rejected list

R1: team half tendencies and half-share modelling (true variance is at or
below the sampling floor). R2: xG and set-play decomposition (absent). R3:
shot-quality and xGOT traits (absent). R4: all shot/corner/possession
covariates (absent). R5: cards before 2023 (target feed absent, NaN not zero).
R9/R10/R11: post-match table snapshots, h2h, form/standings, and leakage from
future observations remain forbidden. No lineup, player, or retrospective
competition-table feature is consumed.
