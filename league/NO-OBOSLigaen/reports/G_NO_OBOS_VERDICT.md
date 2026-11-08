# G-NO-OBOS verdict — goals

**FAIL at the dev gate. The virgin season (2026) was deliberately NOT
read. Nothing ships.**

Reference: production Dixon-Coles pattern (J1 engine), goals-only
observation (no xG exists in this league). Prereg:
`prereg/PREREG_G_NO_OBOS.md`. Gate read on OU 2.5 log-loss.

## Dev (walk-forward, target seasons 2022–2025, n=960)

| Arm | OU 2.5 LL pooled | 2022 | 2023 | 2024 | 2025 | 1X2 LL | RPS |
|---|---|---|---|---|---|---|---|
| Gate Zero | 0.7033 | 0.6863 | 0.6969 | 0.7139 | 0.7162 | 1.0670 | 0.2300 |
| SHR | 0.6924 | 0.6721 | 0.6911 | 0.6975 | 0.7088 | 1.0622 | 0.2288 |
| X2 | 0.6903 | 0.6721 | 0.6930 | 0.6946 | 0.7014 | 1.0771 | 0.2326 |
| Climatology | **0.6660** | — | — | — | — | 1.0744 | 0.2342 |

All numbers recomputed by the coordinator from the per-match
`engine/goals/results_dev.csv` — exact agreement.

## Gate arithmetic

Dev gate — pooled dev LL at the primary line beats BOTH baselines,
else arm dead. Gate Zero (0.7033) **loses to climatology (0.6660)**.
Per the frozen legs, when Gate Zero fails its own dev gate the
candidate verdict is FAIL regardless of variant dev numbers and the
virgin is not read. For the record, the variants also lose to
climatology (SHR 0.6924, X2 0.6903), so no arm passed the dev gate in
any case. The shrinkage and mover arms both help the raw DC pattern
substantially (X2 offsets used per target season: 2023 d_att +0.534 /
d_def −0.633; 2024 +0.405 / −0.289; 2025 +0.421 / −0.200 — the F4
entrant effect is real in-sample) but not enough: a goals-only
Dixon-Coles cannot beat the league's own OU climatology in a league
scoring 3.1 goals a match with a 62% over-rate. Gate Zero's 1X2 LL
(1.0670) does beat climatology's (1.0744) — the gate is read on OU
2.5 as frozen, and there it is not close.

## What ships

Nothing. No virgin predictions exist (the virgin was never read).
The 2026 season remains virgin for a future prereg under a new
registration.
