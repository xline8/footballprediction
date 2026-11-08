# Verdict — G-CH (CH-ChallengeLeague goals): **FAIL (dev gate)**

Frozen decision: PREREG_G_CH.md (prereg commit 157f991, before any fitting).
Virgin 2025/2026 was NOT read for goals: Gate Zero failed the dev gate,
so under the frozen mechanical reading the variants are moot and the
verdict is FAIL.

Dev (pooled 2022/2023–2024/2025, n=540, season-blocked expanding fit):

| Arm | 1X2 LL | RPS | OU2.5 LL | Dev gate |
|---|---|---|---|---|
| Gate Zero | 1.1225 | 0.2391 | 0.7169 | FAIL |
| SHRINK | 1.1225 | 0.2391 | 0.7169 | moot |
| Climatology | 1.0926 | 0.2312 | 0.6856 | — |

Gate Zero loses to climatology on all three legs. Diagnosis (recorded,
not acted on): the DC fit is strong in-sample (2021/2022 fit scores
1X2 LL 0.9365 on its own training rows vs climatology 1.0346) but the
ratings do not carry across seasons in this 10-team tier-2 league —
squad churn between seasons is large and the expanding fit lags it.
SHRINK is numerically identical to Gate Zero: under season-blocked
prediction every scored team either already has ≥6 prior in-league
matches or has no fitted rating at all, so the n<6 scaling never binds.
Nothing ships for G-CH.
