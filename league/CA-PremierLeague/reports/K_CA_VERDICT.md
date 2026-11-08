# Verdict — K-CA (CA-PremierLeague cards model)

**FAIL — Gate Zero fails the dev gate; virgin NOT read.**

Target (frozen in PREREG_K_CA from this league's artefact audit):
stats-feed yellows, era-restricted — the stats yellow series is a
feed artefact in 2021/22 (means 1.15/0.94 with 71–76% zero-total
matches) and the event feed carries no Yellow events before 2025,
so no earlier dev season is legitimate. Warm-up 2023, dev 2024
only (n = 112, reported as the thin window it is).

Dev (2024, n = 112, LL@4.5):

| | LL@4.5 |
|---|---|
| Gate Zero | 0.688993 |
| League base rate | 0.695527 |
| Naive trailing-10 | **0.687491** |

Gate arithmetic (PREREG_K_CA): the dev gate requires beating
BOTH baselines. Gate Zero beats the base rate but loses to naive
trailing-10 (0.688993 > 0.687491) → candidate dead, verdict
FAIL, virgin NOT read. Team yellow traits in this league are
weak (split-half r ≈ 0.20 for / 0.46 against on the credible era,
EDA), and at one 112-match dev season the ratings add nothing
over the trailing mean.

Ships: nothing. Virgin read: NO (deliberately unread).
