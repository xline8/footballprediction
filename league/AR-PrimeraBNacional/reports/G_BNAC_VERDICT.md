# G-BNAC Verdict — FAIL

Date: 2026-11-10. The frozen preregistration requires Gate Zero to beat climatology on pooled 1X2 LL and RPS and the OU2.5 baseline on LL before any virgin read.

## Dev results

| Block | n | Gate Zero LL | Gate Zero RPS | Gate Zero OU2.5 LL | X2 LL | X2 RPS | X2 OU2.5 LL | Climatology LL | Climatology RPS | Climatology OU2.5 LL |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 2022 | 666 | 1.074492 | 0.209362 | 0.647847 | 1.071824 | 0.208600 | 0.647283 | 1.063825 | 0.205964 | 0.635911 |
| 2023 | 648 | 1.047592 | 0.211772 | 0.666203 | 1.045590 | 0.211087 | 0.665471 | 1.054056 | 0.213275 | 0.653815 |
| 2024 | 722 | 1.067570 | 0.211564 | 0.626976 | 1.067723 | 0.211712 | 0.623809 | 1.067085 | 0.211810 | 0.610402 |
| 2025 | 612 | 1.055586 | 0.206617 | 0.611014 | 1.054502 | 0.206260 | 0.609813 | 1.053753 | 0.206849 | 0.593228 |
| **Pooled** | **2,648** | **1.061652** | **0.209918** | **0.638135** | **1.060282** | **0.209516** | **0.636674** | **1.059995** | **0.209551** | **0.623472** |

## Gate arithmetic

Gate Zero fails all three pooled legs: 1X2 LL `1.061652087849 > 1.059995276782`; RPS `0.209917937736 > 0.209551432636`; and OU2.5 LL `0.638135310669 > 0.623472345044`. X2 also fails the LL leg (`1.060282465347 > 1.059995276782`) and the OU leg (`0.636673584771 > 0.623472345044`), although its RPS is lower than climatology (`0.209516429415 < 0.209551432636`).

Per-block sign record for X2 versus Gate Zero: 2022 PASS, 2023 PASS, 2024 FAIL, 2025 PASS (3/4). This cannot revive an arm that fails the dev gate.

Calibration context: coordinator-verified from the engine, in 2024 the model mean P(over 2.5) was `0.3714` versus actual `0.2909`, an over-prediction of `8.06pp`.

The frozen preregistration rule is invoked: because Gate Zero failed its dev gate, the G-BNAC virgin is **NOT read**. No 2026 goals data was read, fitted on, or used for any statistic. Nothing ships.
