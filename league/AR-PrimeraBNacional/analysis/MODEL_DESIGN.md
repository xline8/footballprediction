# Phase 6 — Model design (Phase A, not fitted)

## 1. Shared gate

Each candidate uses the production reference architecture as Gate Zero and a
walk-forward, season-blocked dev evaluation. The dev gate compares against
climatology/base-rate and naive trailing-10 baselines. The virgin read is
one-time and only for arms that pass dev: (i) log loss no worse than Gate Zero
and the best baseline, (ii) calibration breach ≤1.0 percentage point is a
clean pass, ≤1 standard error is provisional, otherwise fail, and (iii) a
variant must have the correct dev sign in at least half of scored blocks.
No rescue arm may be added after results.

## 2. G-BNAC — goals (BUILDABLE)

Reference: production `model_v2.py` Dixon–Coles, as ported in
`league/J1/engine/goals/`, with goals-only observations and the same Gate-Zero
architecture. X1 is the sole observation source; there is no xG fallback to
bind. X2 is the only justified variant: newcomer priors use F4's pooled
offsets (GF −0.087, GA +0.036) in season-block initialization. Warm-up is
2021; scored dev blocks are 2022–2025, n=2,648. Virgin is the 2026 window,
n=648. Primary line: OU2.5 goals (dev over-rate 32.1%).

## 3. K-BNAC — yellow cards (BUILDABLE from 2023)

Reference: production `model_cards.py`, as ported in `league/J1/engine/cards/`;
target is event `card='Yellow'` total. X8 is the only variant: referee
strictness with the documented ≥8-match rule and fallback when referee is
missing. Warm-up is 2023; scored dev blocks are 2024–2025, n=1,334. Virgin
is 2026, n=648. Primary line: OU4.5 (dev rate 52.4%). The 2021–2022
exclusion is structural: there is no Yellow target, so those columns are NaN.

## 4. S-BNAC / C-BNAC / T-BNAC — NOT BUILDABLE

SOT, corners, and total shots are unavailable in 0/3,966 payloads: stats are
empty and shotmap `shots` is empty. No virgin window contains any target.
These candidates are not fit or preregistered.

## 5. Not built in Phase A

No engines, fitted parameters, preregistration files, predictions, or verdicts
are created here. The coordinator writes preregs after reviewing this design.
