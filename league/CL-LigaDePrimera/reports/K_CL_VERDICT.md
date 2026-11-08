# Verdict — K-CL (Chile Liga de Primera cards)

**FAIL at the dev gate. Virgin NOT read. Nothing ships.**

Target: event-unified yellows (frozen in the prereg after the
stats-vs-events artefact check: the stats feed undercounts the
event feed in every season, −1.20 to −0.16 cards/match).

## Dev (n = 720, walk-forward 2022–2024, primary line 5.5)

| arm | LL@5.5 |
|---|---|
| Gate Zero | 0.710444 |
| league base rate | 0.700199 |
| naive trailing-10 | 0.711144 |

Dev gate (verbatim): pooled dev LL@5.5 beats BOTH baselines.
Gate Zero beats the naive (0.710444 < 0.711144) but **fails
against the league base rate** (0.710444 > 0.700199). The single
registered arm is dead; virgin (2025) NOT read; K-CL closed
as FAIL. No fitted params, no predictions.
