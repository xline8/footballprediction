# Verdict — K-ITB (Italy Serie B cards) — **FAIL** (dev gate, naive leg; virgin NOT read)

Prereg: `prereg/PREREG_K_ITB.md` (frozen 369a3a7, before
fitting). Primary line 4.5, target = event-feed yellows (Phase 1
§cards: the stats feed undercounts in every dev season).
Gate Zero only (X8 dropped in FEATURES, referee r = 0.061).
Dev n=1,169, virgin 2025/2026 n=390 **not read**.

## Dev (LL@4.5)

| Season | Gate Zero | League base rate | Naive trailing-10 |
|---|---|---|---|
| 2022/2023 | 0.6816 | 0.6780 | 0.6844 |
| 2023/2024 | 0.6666 | 0.6751 | 0.6507 |
| 2024/2025 | 0.6725 | 0.6825 | 0.6760 |
| **Pooled** | **0.6736** | **0.6785** | **0.6704** |

## Gate arithmetic

The dev gate requires the pooled LL@4.5 to beat **both**
baselines. Gate Zero beats the league base rate (0.6736 <
0.6785) but **loses to the naive trailing-10** (0.6736 >
0.6704), driven by 2023/2024 (naive 0.6507 vs model 0.6666 —
in the league's most stable cards season the plain trailing
means were enough and the decayed ratings added noise). The
team yellows trait is real here (EDA F2, events r = 0.475);
the reference architecture does not convert it into an edge
over its own naive component in this league. The ES cards
candidate failed the same way (lost to both baselines by a
hair); ITB loses to one.

One mechanical note: the NB size r hit the frozen clip value
500 for all three methods (the production method-of-moments
denominator on warm-up residuals was ≤ 0) — the counts are
near-Poisson at these means; this is the frozen formula's
output, not a tuning choice, and it applied identically to
the baselines.

**Verdict: FAIL. Nothing ships.**
`engine/cards/results_virgin.json` records
`{"virgin_read": false, ...}` — the virgin window (which ran
cold on cards, 4.36/match) stays untouched.
