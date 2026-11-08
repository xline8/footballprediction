# K-PT Verdict — Liga Portugal cards model

Date: 2026-11-09. Branch `build/pt-liga`. Prereg:
`league/PT-LigaPortugal/prereg/PREREG_K_PT.md` (dc457f5, frozen
before fitting). Engine: `league/PT-LigaPortugal/engine/cards/`.

## Verdict: FAIL — nothing ships

The referee arm X8 did something real on dev — it is the only arm
that passed the dev gate, beating Gate Zero in 3 of 4 seasons —
and it also posts the best virgin LL. It dies on virgin
calibration: the transitional season's card levels fell off a
cliff (actual over-4.5 rate 41.8% vs 51.4% predicted, breach
+9.57pp vs SE 4.90pp). Even the league base rate over-predicts by
9.3pp; only the fast-adapting naive baseline stayed calibrated.
The gate is mechanical and applied as written.

## Dev results (pooled n=1,224, LL@4.5)

| Arm / baseline | LL@4.5 |
|---|---|
| Gate Zero | 0.6991 |
| X8 (referee) | 0.6940 |
| League base rate | 0.6947 |
| Naive trailing-10 | 0.6991 |

Dev gate (beat BOTH baselines): Gate Zero FAIL (loses to the base
rate 0.6947; its edge over naive is 0.000025, not enough — the
rule is both). X8 PASS. Sign check (iii) for X8: LL ≤ Gate Zero
in 2022/2023, 2024/2025, 2025/2026 = 3/4 PASS. Only X8 read the
virgin. (Referee coverage: 53% in 2021/2022, ~100% from
2023/2024; the X8 multiplier was non-1.0 on 36.7% of virgin
matches.)

## Virgin results (2026/2027, transitional, n=98)

| Arm / baseline | LL@4.5 | Mean P(over) | Actual | Calib |
|---|---|---|---|---|
| X8 | 0.6813 | 51.4% | 41.8% | +9.57pp (SE 4.90) |
| League base rate | 0.6971 | 51.1% | 41.8% | +9.30pp |
| Naive trailing-10 | 0.6915 | 43.1% | 41.8% | +1.26pp |

Legs (X8): (i) LL ≤ best baseline (0.6915) PASS (Gate Zero has no
virgin read — it was dev-dead — so the leg is read against the
baselines, as the prereg's both-pass structure intends);
(ii) calibration FAIL (9.57 > SE 4.90); (iii) PASS (3/4).
**Overall: FAIL.** Virgin predictions on file are X8's, labelled
(`predictions/k_pt_virgin_predictions.csv`).

## Verification notes

Coordinator fixes before dev froze: Codex's model used the
per-match mean as the per-team base, double-counting mu
(~11 yellows/match); the X8 multiplier's denominator had the same
factor-of-two error. A Gate Zero mu was recomputed by hand from
the CSV after the fix: 5.125158 vs the engine's 5.125158, with
matching P(over 4.5). Operational note per prereg: pre-match
referee publication cannot be proven from post-match snapshots;
the shrunk-rate/no-referee fallback is the operating rule.
