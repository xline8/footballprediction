# Verdict — S-SA (Saudi Pro League shots on target) — **PROVISIONAL PASS** (RS ships)

Prereg: `prereg/PREREG_S_SA.md` (frozen aa3a34d, before fitting).
Dev = walk-forward scored 2023/2024 + 2024/2025 (n=612); virgin =
2025/2026 (n=306), read once for dev-passing arms (all three).

## Dev (pooled LL@8.5)

| Arm | Pooled | 2023/2024 | 2024/2025 | vs baselines (league 0.7007 / naive 0.6710) |
|---|---|---|---|---|
| Gate Zero | 0.6664 | 0.6735 | 0.6594 | beats both — PASS |
| RS | 0.6671 | 0.6731 | 0.6611 | beats both — PASS |
| X4 | 0.6661 | 0.6754 | 0.6569 | beats both — PASS |

## Virgin 2025/2026 (n=306)

| Arm | LL@8.5 | Calibration (SE) |
|---|---|---|
| Gate Zero | 0.6855 | +1.95pp (2.84pp) |
| **RS** | **0.6843** | +1.92pp (2.84pp) |
| X4 | 0.6868 | +2.13pp (2.84pp) |
| League base rate | 0.6931 | — |
| Naive trailing-10 | 0.6894 | — |

Gate arithmetic: leg (i) — RS 0.6843 ≤ GZ 0.6855 ✓ and ≤ best
baseline 0.6894 ✓; X4 0.6868 > GZ → leg (i) FAIL. Leg (ii) — GZ
and RS both breach the 1pp boundary (1.95 / 1.92pp) but lie within
1 SE (2.84pp) → PROVISIONAL for both. Leg (iii) — RS dev LL ≤ GZ
in 1 of 2 dev seasons (2023/2024 ✓, 2024/2025 ✗), meeting the
frozen ≥1-of-2 threshold. Both-pass rule: GZ and RS both pass →
lower pooled virgin LL ships → **RS**.

**Ships: RS** (Gate Zero with the Beta-Binomial prior raised
P = 200 → 20,000; fitted params
`engine/sot/fitted_params_virgin.json`; predictions
`predictions/s_sa_virgin_predictions.csv`, halves via frozen
0.4469). The whole field over-predicts SOT in the virgin season
by ~2pp — the virgin SOT level (8.91/match) came in below the dev
level (9.04) — hence provisional, not clean, for every arm.
