# Phase 5 — Features

Feature decisions are based on `eda_summary.json`; 2026 is never used for a
descriptive statistic.

## Template decisions

- **X1 — goals-only observations: ADOPTED.** Header goals exist for all
  2,160 group rows; stats-feed xG is absent, so G-PBM uses the production
  goals-only observation path.
- **X2 — newcomer prior: ADOPTED conditionally.** The pooled 2022–2025
  newcomer blocks have GF gap −0.0325 and GA gap −0.0410 goals/match. The
  Nacional subset is n=4 (GF −0.2125, GA −0.1186); the below/cross-
  competition subset is n=10 (GF +0.0394, GA −0.0099). These are gated
  prior inputs, not hard-coded constants.
- **X3 — set-play decomposition: DROPPED.** No stats or xG payloads.
- **X4 — xG-per-shot quality: DROPPED.** Zero shotmap shots and zero xG.
- **X5 — trailing target means: ADOPTED for goals.** Goals are complete and
  support trailing team goal means. No shot/corner/card target means exist.
- **X6 — xGOT / finishing quality: DROPPED.** Zero shotmap and xG fields.
- **X7 — territorial covariates: DROPPED.** No stats keys, box touches,
  possession, or big chances.
- **X8 — referee strictness: DROPPED.** Referee coverage is 0%.
- **X9 — stats-feed covariates: DROPPED.** No non-empty stats block.

## Halves

Event-time halves are presentation only. The 1H goals share (ratio of
sums) is 0.439932, with observed per-match share variance 0.1288 versus a
binomial noise floor of 0.1354; the estimated true variance is −0.0065 and
team split-half r is −0.117. There is no per-team 1H tendency to model, so
the frozen presentation constant 0.439932 is ADOPTED for goals (FT + 1H/2H
via the constant, as in BNAC/AR/J1). No halves model or team halves feature
is adopted.

## Rejected list

R1 team half tendencies: noise-floor failure. R2 xG/set-play: absent. R3
shot quality and xGOT: absent. R4 shot/corner/card/territorial covariates:
absent. R5 referee identity/rate: 0% coverage. R6 red-card rates: rare event
with no target design. R7 lineup/player/coach features: no reliability test
and not eligible. R8 standings, h2h, form, attendance, and game-state
features: post-match or in-match leakage.
