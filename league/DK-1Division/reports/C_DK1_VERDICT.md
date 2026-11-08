# C-DK1 verdict — PROVISIONAL PASS (X5 ships)

Primary line 9.5. Dev (seed 2022/2023, scored 2023/2024–2024/2025, n=384):
Gate Zero LL 0.7016, X5 0.6965, X7 0.6977; base baseline (ported core's
decayed league-mu construction) 0.7285, naive trailing-10 0.7233.
Gate Zero beats both ⇒ dev gate PASS; virgin read once.

Virgin 2025/2026 (n=192), read once:

| Arm | LL | Calibration (pp) | SE (pp) |
|---|---:|---:|---:|
| Gate Zero | 0.7051 | −5.16 | 3.64 |
| X5 | 0.7035 | −3.71 | 3.64 |
| X7 | 0.7065 | −5.29 | 3.65 |
| Base rate | 0.7497 | — | — |

Gate arithmetic: Gate Zero's calibration breach |−5.16|pp exceeds
1.0 + 1 SE = 4.64pp ⇒ Gate Zero FAILS the calibration leg. X7 fails
likewise (−5.29pp). X5: LL leg 0.7035 ≤ Gate Zero 0.7051 and ≤ base
0.7497 ✓; sign leg ✓ (dev LL ≤ Gate Zero in both scored seasons);
calibration |−3.71|pp ≤ 4.64 ⇒ PROVISIONAL. Ships: X5, predictions in
predictions/c_dk1_virgin_predictions.csv (1H/2H via frozen share
0.469). 2025/2026 was a high-corner season (actual over-rate 53.6% vs
48–49% dev) — all arms under-predicted; X5's trailing blend adapted
best. Numbers independently recomputed by the coordinator — exact
match.
