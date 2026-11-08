# K-USL Verdict — USL Championship cards model

Date: 2026-11-09. Prereg: `prereg/PREREG_K_USL.md`. Engine: `engine/cards/`.

## Verdict: FAIL — dev gate; virgin not read

Gate Zero loses to naive trailing-10 at the primary line: 0.732772 > 0.696954. X8 is moot under the frozen gate order, despite also losing to naive (0.721285 > 0.696954). No virgin command was run.

## Dev results (2022–2024, n=1,318; LL@4.5)

| Season | n | GZ | X8 | Base rate | Naive t-10 |
|---|---:|---:|---:|---:|---:|
| 2022 | 472 | 0.753596 | 0.747838 | 0.764612 | 0.695804 |
| 2023 | 423 | 0.736155 | 0.718378 | 0.745097 | 0.707591 |
| 2024 | 423 | 0.706152 | 0.694562 | 0.728270 | 0.687599 |
| **Pooled** | **1318** | **0.732772** | **0.721285** | **0.746685** | **0.696954** |

## Per-leg verdicts

| Leg | GZ | X8 |
|---|---|---|
| Dev gate versus both baselines | FAIL (0.732772 > 0.696954) | FAIL (0.721285 > 0.696954; moot) |
| Virgin | not read | not read |
| **Overall** | **FAIL** | **FAIL (moot)** |

## What ships

Nothing. No virgin predictions file exists.

Verification: no cards virgin command was run.
