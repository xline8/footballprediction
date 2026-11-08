# Step 5 — Features (SK-1Liga; J1 X1–X9 template)

Consumption rule and causality contract as in J1 FEATURES §1–§2
(trailing/expanding windows strictly pre-match; ratio features are
ratios of sums; NaN ⇒ arm inactive for that match, never filled).

## Adopted / dropped per template feature

| # | Feature | Verdict | Reason (this league's evidence) |
|---|---|---|---|
| X1 | xG blend pair (goals) | **DROPPED** | No xG in any of 1,053 payloads; goals model is goals-only (the reference blend's documented fallback form). |
| X2 | Mover tier offset (promoted clubs) | **ADOPTED** | 2. Liga (id 8973) is in-warehouse; EDA F4: 6 completed transitions — attack below league mean in 5/6 (cumulative ΔGF −0.008 → −0.135 → −0.162 by target season), defence mixed (cumulative ΔGA +0.055 → +0.138 → +0.132). Weaker/less symmetric than CZ/J1; adopted as a preregistered arm with the frozen cumulative offsets, gate decides. Consumed by G-SK's X2 arm only. |
| X3 | Set-play xG share | **DROPPED** | No xG splits (no xG at all). |
| X4 | xG per shot | **DROPPED** | Shotmap empty in all 1,053 matches. |
| X5 | Trailing target-rate means (naive/ensemble base) | **ADOPTED** | F2: SOT r 0.549/0.552, corners 0.395/0.435, yellows 0.194/0.474 — all real traits (yellows-for the weakest). Base component of the S/C/K reference architectures + harness naive baseline. |
| X6 | xGOT per shot | **DROPPED** | No shotmap. |
| X7 | Opp-box touches (corners arm) | **DROPPED** | `touches_opp_box` exists only in the rich era (virgin season onward) — zero dev-era data; an arm on it could never be dev-tested. |
| X8 | Referee yellow rate (cards arm) | **DROPPED** | Referee `text` is EMPTY in all 768 dev-era included matches (names only from 2025/2026). Reliability not estimable (F5); the arm is untestable in dev. Data absence, recorded plainly — not a failed reliability test. K-SK therefore registers Gate Zero only. |
| X9 | Corners Gate Zero covariates | **ADOPTED, reduced form** | Possession only: `BallPossesion` exists in every stats-era match and its trait reliability is the league's highest (F2, r = 0.784). `big_chance` (the other production covariate) has no dev-era data (rich era only) → excluded, as in CZ/RO. |

## Architectural components (not features, as J1 §2)

Ratings/home advantage/DC rho/NB sizes are fitted parameters of
the reference architectures. League half-share constants —
**goals 0.4448, yellows 0.3357** (EDA F3, dev era, event times) —
are frozen presentation constants for the goals and cards markets
only. SOT/corners/total-shots halves: **null (FT-only)** — no
dev-era source exists (period splits begin with the virgin season
itself; RU-1Division precedent).

## Rejected (J1 R-list, adapted)

- R1 per-team/per-match half shares: NOISE (F3: true variance ≈ 0,
  split-half r 0.035/0.103 for goals/yellows).
- R2/R3 finishing & conversion traits: no xG → not computable.
- R4 standalone trailing on-target rate: NOISE per J1 F6; also its
  denominator (total shots) breaks definition at 2025/2026 here.
- R6 lineup/absence features: CLOSED programme-wide (V10 result).
- R9 standings/h2h snapshots, R10 attendance, R11 game-state,
  R13 momentum: leakage / not pre-match.
- R12 red cards as target/covariate: rare-event count, excluded by
  the production cards design; YellowRed/Red stored separately only.
