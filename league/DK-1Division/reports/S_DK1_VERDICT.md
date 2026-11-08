# S-DK1 verdict — PROVISIONAL PASS (Gate Zero ships)

Primary line 9.5. Dev (seed 2022/2023, scored 2023/2024–2024/2025, n=384):
Gate Zero LL 0.6772, X5 0.6772; base-rate 0.6946, naive trailing-10
0.6895. Gate Zero beats both baselines ⇒ dev gate PASS; virgin read once.

Virgin 2025/2026 (n=192), read once:

| Arm | LL | Calibration (pp) | SE (pp) |
|---|---:|---:|---:|
| Gate Zero | 0.6902 | −1.48 | 3.60 |
| X5 | 0.6904 | −1.47 | 3.61 |
| Base rate | 0.6909 | — | — |

Gate arithmetic: LL leg — Gate Zero 0.6902 ≤ climatology 0.6909 ✓
(X5 fails the LL leg vs Gate Zero, 0.6904 > 0.6902). Calibration leg —
|−1.48|pp exceeds the 1.0pp clean boundary but lies within 1 SE of it
(1.0 + 3.60 = 4.60) ⇒ PROVISIONAL. Ships: Gate Zero, predictions in
predictions/s_dk1_virgin_predictions.csv (1H/2H via frozen share
0.455). Virgin LL and calibration independently recomputed by the
coordinator from the shipped predictions CSV — exact match.
