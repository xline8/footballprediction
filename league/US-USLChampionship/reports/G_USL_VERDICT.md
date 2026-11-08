# G-USL Verdict — USL Championship goals model

Date: 2026-11-09. Prereg: `prereg/PREREG_G_USL.md`. Engine: `engine/goals/`.

## Verdict: FAIL — dev gate; virgin not read

Gate Zero fails OU 2.5: 0.694456 > climatology 0.692857. SHR is moot. The frozen rule therefore forbids a goals virgin read and nothing ships.

## Dev results (2022–2024, n=1,318)

| Season | n | GZ OU2.5 | SHR OU2.5 | Climatology OU2.5 |
|---|---:|---:|---:|---:|
| 2022 | 472 | 0.689133 | 0.689606 | 0.685735 |
| 2023 | 423 | 0.693257 | 0.693257 | 0.693627 |
| 2024 | 423 | 0.701596 | 0.700051 | 0.700035 |
| **Pooled** | **1318** | **0.694456** | **0.694130** | **0.692857** |

Frozen extra legs, pooled: GZ 1X2 LL 1.058520 versus climatology 1.063659 (PASS); RPS 0.230017 versus 0.232189 (PASS). These do not rescue the failed OU gate.

## Per-leg verdicts

| Leg | GZ | SHR |
|---|---|---|
| OU2.5 LL beats climatology | FAIL (0.694456 > 0.692857) | FAIL (0.694130 > 0.692857; moot) |
| 1X2 LL versus climatology | PASS (1.058520 < 1.063659) | PASS (1.059102 < 1.063659; moot) |
| RPS versus climatology | PASS (0.230017 < 0.232189) | PASS (0.230183 < 0.232189; moot) |
| Virgin | not read | not read |
| **Overall** | **FAIL** | **FAIL (moot)** |

## What ships

Nothing. No virgin predictions file exists.

Verification: no goals virgin command was run.
