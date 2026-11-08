# Features and decisions

J1 feature decisions are frozen as follows:

- X1 xG blend — DROPPED: no xG.
- X2 cross-tier prior — SHRINK arm only: there is no parent-league prior; Cyprus 2nd division is not in the programme.
- X3 set-play — DROPPED: no set-play xG.
- X4 xG/shot — DROPPED: no xG or shotmap.
- X5 naive trailing-10 — ADOPTED as the registered baseline arm.
- X6 xGOT — DROPPED: absent.
- X7 box touches — DROPPED: absent.
- X8 referee — DROPPED: empty in all 1,271 payloads.
- X9 territorial — ADOPTED for the corners Gate Zero as possession-only; `big_chance` is absent.

All phases are modelled as ordinary matches, phase is retained as a flag, and no phase feature is used.
