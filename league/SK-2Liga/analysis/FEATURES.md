# Step 5 — Features (SK-2Liga; J1 X1–X9 template)

Consumption rule and causality contract as in J1 FEATURES §1–§2
(trailing/expanding windows strictly pre-match; ratio features are
ratios of sums; NaN ⇒ arm inactive for that match, never filled).

## Adopted / dropped per template feature

| # | Feature | Verdict | Reason (this league's evidence) |
|---|---|---|---|
| X1 | xG blend pair (goals) | **DROPPED** | No xG in any of 1,269 payloads; goals model is goals-only (the reference blend's documented fallback form). |
| X2 | Mover tier offset (relegated clubs) | **ADOPTED** | 1. Liga (id 176) is in-warehouse; EDA F4: 4 completed transitions, one per season — attack above the league mean in 3/4, defence below it in 3/4, cumulative offsets (−0.023, −0.134) → (+0.109, −0.030) → (+0.151, −0.237). The mirror image of the SK-1Liga promoted-mover signal, direction-consistent. Thin (n = 1 per season) — adopted as a preregistered arm with the frozen cumulative offsets, gate decides. Consumed by G-SK2's X2 arm only. |
| X3 | Set-play xG share | **DROPPED** | No xG splits (no xG at all). |
| X4 | xG per shot | **DROPPED** | Shotmap empty in all 1,269 matches. |
| X5 | Trailing target-rate means (naive/ensemble base) | **ADOPTED, goals-only form** | F2: goals-for r 0.528, goals-against r 0.514 — real traits. The DC ratings themselves are the trailing means in the goals architecture; the harness naive baseline (trailing-10 team goal rates) is the X5 consumer here. No SOT/corners/cards trailing means exist (no data). |
| X6 | xGOT per shot | **DROPPED** | No shotmap. |
| X7 | Opp-box touches (corners arm) | **DROPPED** | No stats feed at all; no corners market. |
| X8 | Referee yellow rate (cards arm) | **DROPPED** | Referee `text` is EMPTY in all 1,143 finished matches. Reliability not estimable (F5); untestable on data absence. |
| X9 | Corners Gate Zero covariates | **DROPPED** | No stats feed (no possession, no big_chance); no corners market. |

## Architectural components (not features, as J1 §2)

Ratings/home advantage/DC rho are fitted parameters of the
reference architecture. League half-share constant — **goals
0.4940** (EDA F3, dev era, event times) — is a frozen
presentation constant for the goals market only. SOT/corners/
total-shots/cards halves: **null (FT-only)** — no data source
exists for any of them.

## Rejected (J1 R-list, adapted)

- R1 per-team/per-match half shares: NOISE (F3: true variance ≈
  −0.0059, split-half r −0.165 for goals).
- R2/R3 finishing & conversion traits: no xG → not computable.
- R4 standalone trailing on-target rate: no shots data.
- R6 lineup/absence features: CLOSED programme-wide (V10 result).
- R9 standings/h2h snapshots, R10 attendance, R11 game-state,
  R13 momentum: leakage / not pre-match.
- R12 red cards as target/covariate: no card data at all (event
  red-card counts exist in a few header.events blocks but there
  is no yellow-card feed and no cards market).
