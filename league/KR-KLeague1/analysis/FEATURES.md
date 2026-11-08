# Phase 3.5 — Features: KR-KLeague1

All adopted features use strict pre-match cutoffs and trailing/decayed
windows. X1 blend is guarded to matches with expected_goals (2022 onward,
with 2024/2026 small gaps); 2021 is goals-only. X2 mover offset is ADOPTED
as an arm: prior K2 rows exist and every identified mover is found by ID.
X3 set-play share is DROPPED (r=0.283). X4 xG/shot is ADOPTED as an arm
(r=0.701; shotmap era from 2022). X5 trailing target rates are ADOPTED.

X6 xGOT/shot is DROPPED: population share is only about 0.33–0.35 of
regulation shots in every shotmap era and 2025+ r=0.137. X7 box touches is
ADOPTED with the min-8 guard (for/against r=0.846/0.660; coverage 0%,
54.4%, 75.0%, then ~100%). X8 referee strictness is ADOPTED with fallback
(r=0.362 on named-referee matches; unknown or under-8 histories use base).
X9 possession/big chance is ADOPTED in the corners Gate Zero (r=0.923 for
possession and 0.634/0.264 for big chance for/against).

Half constants are presentation-only. Lineups, absence, standings, h2h,
attendance, momentum, and red cards are rejected for leakage, no evidence,
or rare-event reasons. No phase feature is adopted.
