# Verdict — G-EC (EC-SerieA goals): **FAIL (dev gate)**

Frozen decision: PREREG_G_EC.md (prereg commit
1a2eb966f78fe43570c2f4a1177bf27b14ba2a6e, before any fitting).
Virgin 2025 was NOT read for goals: Gate Zero failed the dev gate,
so under the frozen mechanical reading the variant is moot and the
verdict is FAIL.

Dev (pooled 2022–2024, n = 726, season-blocked expanding fit,
warm-up 2021):

| Arm | 1X2 LL | RPS | OU2.5 LL | Dev gate |
|---|---|---|---|---|
| Gate Zero | 1.0142 | 0.2034 | 0.7036 | FAIL |
| ENTRANT | 1.0159 | 0.2038 | 0.7050 | FAIL (moot) |
| Climatology | 1.0575 | 0.2176 | 0.6941 | — |
| Naive trailing-10 | 1.1965 | 0.2268 | 0.7388 | — |

Per season, Gate Zero 1X2 LL / RPS / OU2.5 LL: 2022 1.0429 / 0.2109 /
0.6999; 2023 0.9990 / 0.1956 / 0.7120; 2024 1.0007 / 0.2037 / 0.6988.
ENTRANT: 2022 1.0384 / 0.2097 / 0.7055; 2023 1.0093 / 0.1984 /
0.7113; 2024 0.9998 / 0.2033 / 0.6982.

Gate Zero beats both baselines on 1X2 LL and RPS, and beats naive
trailing-10 on OU2.5 LL — but loses OU2.5 LL to climatology (0.7036
vs 0.6941), so the dev gate (all three metrics vs BOTH baselines)
fails. ENTRANT is slightly worse than Gate Zero pooled on all three
metrics, so it fails the dev gate on its own numbers as well; its
leg (iii) sign check (ENTRANT 1X2 LL ≤ Gate Zero in 2 of 3 dev
seasons: 2022 and 2024) is recorded but moot. Diagnosis (recorded,
not acted on): the DC ratings carry across seasons here — unlike
CH, the 1X2/RPS legs win clearly — but the score matrix's OU2.5
probabilities do not beat the constant base rate on log-loss, even
though the mean predicted over-rate (0.4555) is close to the actual
(0.4642). Nothing ships for G-EC.
