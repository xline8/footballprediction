# Verdict — G-UY (UY-LigaAUF goals): **FAIL (dev gate)**

Frozen decision: PREREG_G_UY.md (prereg commit
7d43257df3460bcfa1bf07c8c94d2ff4466f2074, branch wip-uy-ligaauf,
before any fitting). Virgin 2025 was NOT read for goals: Gate Zero
failed the dev gate, so under the frozen mechanical reading the
variant is moot and the verdict is FAIL.

Dev (pooled 2022–2024, n = 895, season-blocked expanding fit,
warm-up 2021):

| Arm | 1X2 LL | RPS | OU2.5 LL | Dev gate |
|---|---|---|---|---|
| Gate Zero | 1.0705 | 0.2228 | 0.6869 | FAIL |
| ENTRANT | 1.0753 | 0.2244 | 0.6858 | FAIL (moot) |
| Climatology | 1.0939 | 0.2305 | 0.6806 | — |
| Naive trailing-10 | 1.1465 | 0.2280 | 0.7296 | — |

Per season, Gate Zero 1X2 LL / RPS / OU2.5 LL: 2022 1.1226 / 0.2438 /
0.6832; 2023 1.0586 / 0.2134 / 0.6772; 2024 1.0302 / 0.2112 / 0.7004.
ENTRANT: 2022 1.1325 / 0.2471 / 0.6863; 2023 1.0619 / 0.2145 / 0.6758;
2024 1.0314 / 0.2115 / 0.6954.

Gate Zero beats BOTH baselines on 1X2 LL (1.0705 vs 1.0939
climatology, 1.1465 naive) and on RPS (0.2228 vs 0.2305 / 0.2280),
but loses OU2.5 LL to climatology (0.6869 vs 0.6806) while beating
naive (0.7296), so the dev gate (all three metrics vs BOTH
baselines) fails on the OU leg alone. ENTRANT is worse than Gate
Zero pooled on 1X2 LL and RPS (1.0753 / 0.2244) and also fails the
OU leg vs climatology (0.6858 vs 0.6806); its leg (iii) sign check
(ENTRANT 1X2 LL ≤ Gate Zero in 0 of 3 dev seasons) is recorded but
moot. Diagnosis (recorded, not acted on): the failure is narrow and
OU-specific — 0.0063 nats vs climatology pooled. The model's OU2.5
probabilities are slightly worse than a constant: mean predicted
over-rate 0.378 vs actual 0.4045 pooled (per season 0.438 vs 0.383
in 2022, 0.361 vs 0.400 in 2023, 0.336 vs 0.431 in 2024 — the model
over-predicts overs in the low-scoring 2022 season and
under-predicts them in the higher-scoring 2024 season, i.e. its
season-level totals do not track the year-to-year level shift:
goals/match 2.191 in 2022 vs 2.434 in 2024). The 1X2/RPS legs pass,
so the ratings carry real signal; the OU2.5 line is where the
constant wins. Nothing ships for G-UY.
