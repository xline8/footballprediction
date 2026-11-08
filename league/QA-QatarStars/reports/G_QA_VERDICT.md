# Verdict — G-QA (QA-QatarStars goals): **FAIL (dev gate)**

Frozen decision: PREREG_G_QA.md (prereg commit
be4814af3534c69ba912694a4a80cc3fea42f9c1, before any fitting).
Virgin 2025/2026 was NOT read for goals: Gate Zero failed the dev gate,
so under the frozen mechanical reading the variant is moot and the
verdict is FAIL.

Dev (pooled 2022/2023–2024/2025, n = 396, season-blocked expanding fit,
warm-up 2021/2022):

| Arm | 1X2 LL | RPS | OU2.5 LL | Dev gate |
|---|---|---|---|---|
| Gate Zero | 1.0485 | 0.2302 | 0.7275 | FAIL |
| ENTRANT | 1.0431 | 0.2277 | 0.7239 | FAIL (moot) |
| Climatology | 1.0512 | 0.2419 | 0.6469 | — |
| Naive trailing-10 | 1.0106 | 0.2253 | 0.6866 | — |

Per season, Gate Zero 1X2 LL / RPS / OU2.5 LL: 2022/2023 1.0289 / 0.2202 /
0.7637; 2023/2024 1.1101 / 0.2480 / 0.6996; 2024/2025 1.0066 / 0.2224 /
0.7192. ENTRANT: 2022/2023 1.0258 / 0.2186 / 0.7718; 2023/2024 1.0893 /
0.2416 / 0.6976; 2024/2025 1.0142 / 0.2229 / 0.7023.

Gate Zero beats climatology on 1X2 LL and RPS, but loses 1X2 LL and RPS
to naive trailing-10 (1.0485 vs 1.0106; 0.2302 vs 0.2253) and loses
OU2.5 LL to BOTH baselines (0.7275 vs 0.6469 climatology, 0.6866 naive),
so the dev gate (all three metrics vs BOTH baselines) fails. ENTRANT
is better than Gate Zero pooled on all three metrics, but also fails
the dev gate on its own numbers (1X2 LL and RPS lose to naive; OU2.5
LL loses to both baselines); its leg (iii) sign check (ENTRANT 1X2 LL
≤ Gate Zero in 2 of 3 dev seasons: 2022/2023 and 2023/2024) is recorded
but moot. Diagnosis (recorded, not acted on): the DC score matrix
systematically under-predicts total goals in this league — mean
predicted OU2.5 over-rate 0.4996 vs actual 0.6641 pooled (per season
0.486 / 0.497 / 0.517 predicted vs 0.629 / 0.697 / 0.667 actual). The
fitted model carries a single home intercept (the sanctioned reference
pattern, DK dc.py `lambdas`), so the away-goals level has no intercept
of its own; in a league with a near-absent home advantage (pooled dev
scored home 1.707 vs away 1.641 goals/match; 2021/2022 away teams
outscored home teams 1.659 vs 1.553) the fitted away lambdas underfit
(2021/2022 fit: mean fitted away lambda 1.170 vs actual 1.659), and
the OU2.5 probabilities inherit the shortfall. The naive trailing-10
baseline, which uses each team's actual trailing scoring means as its
lambdas, wins 1X2 LL and RPS outright. Nothing ships for G-QA.
