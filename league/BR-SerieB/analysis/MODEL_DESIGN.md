# Phase 4 — Model Design: BR-SerieB candidates

Dev is 2021–2024: warm-up 2021, scored 2022–2024, n=1,140. The cards dev is
era-restricted: warm-up 2023, scored 2024, n=380. Virgin primary is complete
2025 (n=380), read once only for dev-passers; 2026 has 370 played and is
confirmatory, not read here. Calibration is actual minus predicted; positive
means underprediction.

| candidate | reference | primary line from dev | arms |
|---|---|---|---|
| G-BRB | production DC pattern, goals-only in effect | OU 2.5 (over .356) plus 1X2 LL/RPS | Gate Zero; SHRINK; two-sided X2 ex-A/ex-C |
| S-BRB | model_sot v5 | 7.5 (over .537) | Gate Zero; RS only if dev gate passes |
| C-BRB | corners_v3 | 10.5 (over .454) | Gate Zero; X7 if min-8/gate pass |
| K-BRB | model_cards | 4.5 (over .566; 2024 only) | Gate Zero; X8 if gate pass |
| T-BRB | shots A/B/C family | 26.5 (over .463) | A, B, C trailing-level variants |

Primary lines are the .5 lines closest to 50% in the appropriate scored
distribution. Goals uses the usual two-part gate: beat climatology on 1X2
log loss and RPS, and beat the OU2.5 base rate on log loss. Count candidates
must beat the base rate and naive trailing-10 on primary log loss. A dev pass
is necessary for a virgin read. On virgin, PASS means LL <= best baseline and
absolute calibration <= 1 percentage point; within one standard error is
PROVISIONAL; otherwise FAIL. The rules are frozen before any 2025 candidate
fit. Half outputs use the frozen constants in config, not a half model.

The blend, set-play, and xG/shot findings are explicitly not allowed to turn
virgin-only measurements into dev evidence. X2 is parameterised only from
pre-match mover information available inside each dev fit.
