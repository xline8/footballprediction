# Verdict — K-IE (Ireland Premier Division cards) — **FAIL** (dev gate; virgin NOT read)

Prereg: `prereg/PREREG_K_IE.md`. Primary line 4.5. Gate Zero only
(X8 referee arm dropped in FEATURES: split-half r = 0.239 on event
yellows; named-referee coverage is 0% in 2021 and 22.2% in 2022
anyway). Target is the event-unified yellow count (Yellow +
YellowRed from match events) — the stats-feed yellows disagree
with events in 18.3% of dev matches, including 0–0 reports against
8 event cards, and are never used as the target.

## Dev (walk-forward, seed 2021, scored 2022–2025, n = 720)

| | LL@4.5 |
|---|---|
| Naive trailing-10 | **0.6647** |
| Gate Zero | 0.6708 |
| League base rate | 0.6877 |

Gate Zero beats the league base rate but **loses to naive
trailing-10 by 0.0061 LL** (and loses to it in all four dev
seasons). The dev gate requires beating BOTH baselines, so the
candidate is dead at dev. Per the frozen rule the virgin window
(2026) was **deliberately NOT read** and stays unburned. Nothing
ships; no predictions CSV.

Context: IE event yellows run high (4.36–5.09/match) with a strong
trailing component; the reference architecture's ratings do not
beat simply carrying each team's recent card rate forward.
