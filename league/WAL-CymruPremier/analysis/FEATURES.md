# Features — Wales Cymru Premier

The J1 X1–X9 template is applied with a strict pre-match causality rule.

- X1 **ADOPTED**, goals-only: no xG anywhere (0/1,103).
- X2 **DROPPED**: no Welsh sibling in the warehouse; no mover prior. SHRINK is the thin-data treatment.
- X3 **DROPPED**: no xG splits (0/1,103).
- X4 **DROPPED**: no shotmap (0/1,103).
- X5 **DROPPED** for SOT/corners/cards: targets absent; the 234 trailing dismissal events are not a yellow target.
- X6 **DROPPED**: no xGOT (0/1,103).
- X7 **DROPPED**: no box touches (stats empty 0/1,103).
- X8 **DROPPED**: referee text empty 1,103/1,103.
- X9 **DROPPED**: no possession/big-chance stats (0/1,103).

## Rejected list

R1 half-shares (F3 noise); R6 lineup/absence (no lineups); R9 standings/h2h (post-match leakage); R12 reds as target (234 rare dismissals and no yellow target). Also reject game-state/first-goal, attendance, formation/coach and momentum as non-pre-match or unsupported. `goals_1h_share=0.4444`; every other market constant is null.
