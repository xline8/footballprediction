# Phase A — Candidate Model Design: SCO Championship

This is a design-only document. No model is fitted and no preregistration file is created. Calibration is reported as predicted minus actual, following the SCO-Premiership convention.

## Validation frame

The dev period uses 2021/2022 as the seed and scores 2022/2023–2024/2025 in season-blocked walk-forward evaluation: goals/cards n=540 and stats markets n=427 target rows. The virgin primary window is 2025/2026: goals/cards n=180 and stats n=177. It is read once only for arms that pass dev. The partial 2026/2027 season is confirmatory and reserved unread.

| candidate | target | allowed arms | primary line |
|---|---|---|---|
| G-SCOCH | DC goals-only, hl=270 | Gate Zero, SHRINK, X2 mover arm | OU 2.5 |
| S-SCOCH v5 | total SOT | Gate Zero, RS | 7.5; ladder 6.5/7.5/8.5 |
| C-SCOCH corners_v3 | total corners | Gate Zero, possession-only | 9.5; ladder 8.5/9.5/10.5 |
| K-SCOCH | event-yellows target | Gate Zero only | 3.5; ladder 2.5/3.5/4.5 |
| T-SCOCH | total shots | arms A/B/C | 15.5; ladder 14.5/15.5/16.5 |

Gate legs are verbatim from the RU-1Division/SCO-Premiership preregistration pattern: dev must beat both baselines; virgin log loss and calibration must pass, with absolute calibration breach ≤1 percentage point clean or ≤1 SE provisional; variants require the sign check. Gate Zero dev fail means FAIL and the virgin is not read.
