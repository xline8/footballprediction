# K-DK1 verdict — PASS (Gate Zero ships)

Primary line 3.5. Target (frozen in prereg): stats-feed yellow+red
cards (stats-vs-events match-level agreement 88.0–92.2% in the dev
seasons; stats chosen as the structured, complete source). Dev (seed
2022/2023, scored 2023/2024–2024/2025, n=384): Gate Zero LL 0.6723,
X5 0.6678; base-rate 0.6882, naive trailing-10 0.6749. Gate Zero beats
both ⇒ dev gate PASS; virgin read once.

Virgin 2025/2026 (n=192), read once:

| Arm | LL | Calibration (pp) | SE (pp) |
|---|---:|---:|---:|
| Gate Zero | 0.6780 | +0.03 | 3.56 |
| X5 | 0.6861 | −0.42 | 3.59 |
| Base rate | 0.6883 | — | — |

Gate arithmetic: LL leg — Gate Zero 0.6780 ≤ base 0.6883 ✓ and is the
lowest arm LL; X5 fails the LL leg vs Gate Zero. Calibration leg —
|+0.03|pp ≤ 1.0pp ⇒ clean PASS. Ships: Gate Zero, predictions in
predictions/k_dk1_virgin_predictions.csv (1H/2H via frozen share
0.314). Numbers independently recomputed by the coordinator — exact
match.
