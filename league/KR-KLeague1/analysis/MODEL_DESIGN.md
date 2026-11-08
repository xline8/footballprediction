# Phase 4 — Model Design: KR-KLeague1 candidates

Design only; no fitting. Dev is 2021–24 (912), virgin is complete 2025
(228), and confirmatory 2026 (210 partial) is reserved. Split rounds are
ordinary matches with a phase flag and no phase feature.

| Candidate | Primary line / DEV over-rate | Arms |
|---|---|---|
| G-KR goals | OU 2.5 / 0.468 | Gate Zero; SHRINK; X2 mover offset |
| S-KR SOT | OU 7.5 / 0.541 | Gate Zero; ratio-shrink; X4 xG/shot |
| C-KR corners | OU 8.5 / 0.438 | Gate Zero/X9; X7 box touches |
| K-KR cards | OU 3.5 / 0.444 | Gate Zero; X8 referee fallback |
| T-KR shots | OU 23.5 / 0.463 | v1 Gate Zero; level layer; trailing-r |

All five targets exist in virgin 2025, so all five receive preregs. Baselines
are league base rate at the line, naive trailing-10 for count markets, and
climatology for goals. The preregs freeze the dev gate, virgin gate, tie rule,
and calibration rule: |breach| <=1pp is clean PASS, <=1 SE is PROVISIONAL,
otherwise FAIL. No fitted or virgin results are included.
