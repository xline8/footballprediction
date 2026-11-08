# K-GR verdict

Preregistration: `prereg/PREREG_K_GR.md` (Gate Zero ONLY — X8 was
dropped at design on referee reliability 0.262). Calibration is
actual − predicted. **Virgin NOT read** (dev gate failed).

## Dev (scored 2022/2023–2024/2025, n=716, LL@4.5)

| arm / baseline | pooled LL@4.5 |
|---|---:|
| Gate Zero | 0.696218 |
| league base rate | 0.691143 |
| naive trailing-10 | 0.705130 |

Gate Zero per-season LL@4.5: 2022/2023 0.703178, 2023/2024
0.721883, 2024/2025 0.663040. Dev mean predicted over-4.5 rate
0.4786 vs actual 0.5461 — the model also materially under-predicts
the card level in dev, but the gate is the LL leg and it is
decisive on its own.

## Gate arithmetic

- Dev gate: Gate Zero beats naive trailing-10 (0.696218 <
  0.705130) but does **NOT** beat the league base rate (0.696218
  is not < 0.691143) → **FAIL**. The arm is dead; there is no
  variant arm in this build by design.

K-GR verdict: **FAIL; nothing ships. Virgin deliberately NOT
read.** Prediction CSV: none. Fitted virgin params: none.
