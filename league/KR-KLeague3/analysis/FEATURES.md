# Phase 5 — Features: KR-KLeague3

The X1–X9 template is judged against this league's verified corpus. Every
number below is from `eda_summary.json`.

- **X1 goals-only blend — ADOPTED as goals-only.** Goals exist for the
  played population. xG is DROPPED: 0/1,296 payloads carry xG, and all
  shotmaps are empty.
- **X2 mover offset — DROPPED.** There are zero K2→K3 incoming movers in
  2022–2026; K4 entrants have no corpus, so no prior-tier rate can be
  estimated.
- **X3 set-play xG share/rate — DROPPED.** No xG exists in 0/1,296 payloads.
- **X4 xG per shot — DROPPED.** Shotmap is absent/empty in all 1,296
  payloads, so the denominator and xG are unavailable.
- **X5 trailing target-rate means — DROPPED** for SOT, corners, and yellows:
  those targets are absent. Trailing goals means are subsumed by the
  Dixon–Coles fit and are not a separate arm.
- **X6 xGOT per shot — DROPPED.** No shotmap exists.
- **X7 box touches/territory — DROPPED.** Stats are absent in 0/1,296
  payloads, including territorial stats.
- **X8 referee strictness — DROPPED.** Zero referees are identified.
- **X9 on-target ratio/finishing — DROPPED.** No shots or SOT data exist.

The goals first-half share 0.4273 is ADOPTED for FT/1H/2H presentation only.
It is supported by observed variance 0.1198 versus noise floor 0.1230, with
true variance -0.0031 approximately zero. SOT, corners, cards, and total-shot
halves constants DO NOT EXIST.

