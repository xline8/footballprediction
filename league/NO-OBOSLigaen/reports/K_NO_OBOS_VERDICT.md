# K-NO-OBOS verdict — cards (event-unified yellows)

**FAIL at the dev gate. The virgin season (2026) was deliberately NOT
read. Nothing ships.**

Reference: production `model_cards.py` pattern (NO-Eliteserien
engine). Target: event-unified yellows (Yellow + YellowRed events) —
the only target that exists in this league: the stats feed carries no
yellow_cards key in any season, so no stats target and no
stats-vs-events artefact comparison are possible (prereg, frozen with
that reason before fitting). Primary line 3.5. Prereg:
`prereg/PREREG_K_NO_OBOS.md`.

## Dev (walk-forward, warm-up 2021, scored 2022–2025, n=960)

| Arm | LL@3.5 pooled |
|---|---|
| Gate Zero | 0.6693 |
| X8 (referee) | 0.6553 |
| League base rate | **0.6683** |
| Naive trailing-10 | 0.6729 |

Recomputed by the coordinator as n-weighted means of the per-season
rows in `engine/cards/results_dev.json` — exact agreement. X8 active
coverage: fallbacks (unknown referee + thin referee history) decline
from 148/240 matches in 2022 to 20–33/240 by 2024–2025 as referee
histories accumulate; the trait itself is the program's strongest
(F8, r=0.715).

## Gate arithmetic

Dev gate — pooled dev LL beats BOTH baselines, else arm dead. Gate
Zero (0.6693) beats naive trailing-10 (0.6729) but **loses to the
league base rate (0.6683) by 0.0010**. Per the frozen legs, when Gate
Zero fails its own dev gate the candidate verdict is FAIL regardless
of variant dev numbers and the virgin is not read. X8's dev number
(0.6553, beating both baselines by a clear margin) is therefore
**moot by rule** — recorded here in full because it is the honest
picture: the referee covariate demonstrably carries signal in this
league, and a future prereg that promotes the referee arm to the
reference position (a new registration, not a rescue of this one)
would be the legitimate way to test it on the still-virgin 2026
season.

## What ships

Nothing. No virgin predictions exist (the virgin was never read).
The 2026 season remains virgin for a future prereg.
