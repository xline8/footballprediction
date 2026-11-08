# Verdict — G-QASD (QA-SecondDivision goals): **FAIL (dev gate)**

Frozen decision: PREREG_G_QASD.md (prereg commit
75aac0f17f333edbbb60e46a5fb8dbf3002f7577, before any fitting).
Virgin 2025/2026 was NOT read for goals: Gate Zero failed the dev gate,
so under the frozen mechanical reading the variant is moot and the
verdict is FAIL.

Dev (within-season walk-forward over 2024/2025; warm-up rounds 1–7,
scored rounds 8–14, n = 28, date-grouped expanding fit):

| Arm | 1X2 LL | RPS | OU2.5 LL | Dev gate |
|---|---|---|---|---|
| Gate Zero | 1.1883 | 0.2578 | 0.8978 | FAIL |
| ENTRANT | 1.1883 | 0.2578 | 0.8978 | FAIL (moot) |
| Climatology | 1.1213 | 0.2346 | 0.6945 | — |
| Naive trailing-10 | 1.1153 | 0.2354 | 0.7984 | — |

Gate Zero loses 1X2 LL and RPS to BOTH baselines (1.1883 vs 1.1213 /
1.1153; 0.2578 vs 0.2346 / 0.2354) and loses OU2.5 LL to BOTH baselines
(0.8978 vs 0.6945 / 0.7984), so the dev gate (all three metrics vs BOTH
baselines) fails. ENTRANT is numerically identical to Gate Zero on every
dev match (max |Δp| = 0.0, asserted in the harness): no preceding season
exists in the corpus for dev, so no team is an entrant in the dev season,
and the variant cannot differ there. Its leg (iii) sign check is vacuous
by construction (recorded in the prereg before fitting).

Diagnosis (recorded, not acted on): this is NOT the QA-QatarStars level
failure. The scored block's aggregate rates are close to the model's —
mean predicted H/D/A 41.8% / 28.5% / 29.7% vs actual 46.4% / 28.6% /
25.0%; mean predicted OU2.5 over-rate 44.8% vs actual 39.3% — so there is
no systematic goals-level shortfall (mean fitted lambdas H 1.43 / A 1.10
vs actual 2.43 goals/match). The model loses on per-match sharpness: with
ratings fitted on 28 warm-up matches (7 per team), the per-match
probabilities are overconfident in the wrong direction on individual
matches, and the flat climatology (expanding over-rate ≈ 50% from the
warm-up) beats it on OU2.5 LL by 0.20 nats. At n = 28 the dev gate is a
weak discriminator (F7), but the gate is mechanical and the margin is
large on all three metrics — this is a genuine fail, not a borderline one.

Verification (coordinator, independent of the builder): headline numbers
recomputed from `engine/goals/predictions_dev.csv` by a second path match
`results_dev.json` exactly (all nine numbers, full precision); the 28
scored match ids are exactly 2024/2025 rounds 8–14; ENTRANT == Gate Zero
on all 28; no `results_virgin.json` exists; the run was re-executed and
reproduced `results_dev.json` bit-identically. One latent deviation was
found in the (never-executed) virgin path — climatology used the growing
train instead of the prereg's fixed pooled-2024/2025 rates — and was fixed
before this verdict (dev results unchanged).

Nothing ships for G-QASD. The 2025/2026 virgin stays unread for goals;
the 2026/2027 confirmatory window stays untouched.
